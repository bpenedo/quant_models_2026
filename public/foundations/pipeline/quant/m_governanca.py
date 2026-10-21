# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Estrutura e governança: rede de correlação (árvore geradora mínima + centralidades) e
backtest walk-forward com custos e portões STOP do pipeline quant."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from quant import kernels as K
from quant.dados import CLASSES, NOMES, retornos
from quant.util import br, pct


# ─────────────────────────────────────────────────────────────────────────────
def rede_correlacao(periferia: int = 8) -> dict:
    import networkx as nx
    r = retornos()
    tr = r[r.index < "2020-01-01"]
    te = r[r.index >= "2020-01-01"]
    C = tr.corr()
    ativos = list(C.columns)
    G = nx.Graph()
    for i, a in enumerate(ativos):
        for b in ativos[i + 1:]:
            rho = C.loc[a, b]
            G.add_edge(a, b, peso=abs(rho), distancia=math.sqrt(2 * (1 - rho)))
    T = nx.minimum_spanning_tree(G, weight="distancia")
    forca = {a: sum(abs(C.loc[a, b]) for b in ativos if b != a) for a in ativos}
    autovetor = nx.eigenvector_centrality_numpy(G, weight="peso")
    proximidade = nx.closeness_centrality(T, distance="distancia")
    intermediacao = nx.betweenness_centrality(T, weight="distancia")
    nos = pd.DataFrame({"simbolo": ativos, "nome": [NOMES.get(a) for a in ativos],
                        "classe": [CLASSES.get(a) for a in ativos], "forca": [forca[a] for a in ativos],
                        "autovetor": [autovetor[a] for a in ativos], "proximidade": [proximidade[a] for a in ativos],
                        "intermediacao": [intermediacao[a] for a in ativos],
                        "grau_arvore": [T.degree(a) for a in ativos]})
    # centralidade composta = média dos postos das quatro medidas
    for c in ("forca", "autovetor", "proximidade", "intermediacao"):
        nos[f"posto_{c}"] = nos[c].rank()
    nos["centralidade_composta"] = nos[[c for c in nos if c.startswith("posto_")]].mean(1)
    nos = nos.sort_values("centralidade_composta")
    pos = nx.spring_layout(T, weight="peso", seed=7)
    nos["x"] = [pos[a][0] for a in nos.simbolo]
    nos["y"] = [pos[a][1] for a in nos.simbolo]
    arestas = pd.DataFrame([{"a": a, "b": b, "correlacao": C.loc[a, b],
                             "xa": pos[a][0], "ya": pos[a][1], "xb": pos[b][0], "yb": pos[b][1]}
                            for a, b in T.edges()])
    perif = nos.simbolo.iloc[:periferia].tolist()
    centro = nos.simbolo.iloc[-periferia:].tolist()
    res = []
    for nome, cesta in (("Periféricos", perif), ("Centrais", centro), ("Todos (pesos iguais)", ativos)):
        w = np.array([[1 / len(cesta) if a in cesta else 0.0 for a in ativos]])
        m = K.metricas_carteiras(te[ativos].to_numpy(), w, 252.0, 0.0)[0]
        cte = te[cesta].corr().to_numpy()
        corr_media = float(cte[np.triu_indices(len(cesta), 1)].mean())
        res.append({"carteira": nome, "ativos": ", ".join(cesta) if nome != "Todos (pesos iguais)" else "27 ativos",
                    "correlacao_media_entre_si": corr_media,
                    "retorno_anual_pct": m[0] * 100, "vol_anual_pct": m[1] * 100, "sharpe": m[2],
                    "drawdown_pct": m[3] * 100})
    t = pd.DataFrame(res)
    p_, c_, todos = t.iloc[0], t.iloc[1], t.iloc[2]
    return {"tabelas": {"nos": nos, "arestas": arestas, "carteiras": t},
            "destaque": (f"Escolhidos pela rede de 2010–2019, os {periferia} periféricos seguiram quase independentes em "
                         f"2020–2026 (correlação média {br(p_.correlacao_media_entre_si)} contra "
                         f"{br(c_.correlacao_media_entre_si)} dos centrais) e renderam mais ({br(p_.retorno_anual_pct, 1)}% "
                         f"contra {br(c_.retorno_anual_pct, 1)}% a.a.), porém com mais volatilidade. Quem venceu as duas "
                         f"cestas foi a carteira com os 27 (Sharpe {br(todos.sharpe)}): número de apostas independentes "
                         f"pesa mais que a posição na rede.")}


# ─────────────────────────────────────────────────────────────────────────────
def _metricas(ret: np.ndarray) -> dict:
    curva = np.exp(np.cumsum(np.log1p(ret)))
    anos = ret.size / 252
    cagr = curva[-1] ** (1 / anos) - 1
    neg = ret[ret < 0]
    sortino = ret.mean() / neg.std() * math.sqrt(252) if neg.size > 1 else np.nan
    return {"cagr_pct": cagr * 100, "vol_anual_pct": ret.std() * math.sqrt(252) * 100,
            "sharpe": K.sharpe_anual(ret, 252.0), "sortino": sortino,
            "drawdown_max_pct": K.drawdown_maximo(curva) * 100, "dias_positivos_pct": float((ret > 0).mean() * 100)}


def backtest_walkforward(custo_bps: float = 5.0) -> dict:
    r = retornos()
    R = np.expm1(r.to_numpy())               # retornos simples para composição da carteira
    T, N = R.shape
    datas = r.index
    custo = custo_bps / 1e4
    fim_mes = np.r_[datas[1:].month != datas[:-1].month, True]

    def simular(pesos_fn):
        w = np.full(N, 1 / N)
        out = np.zeros(T)
        giro = 0.0
        for t in range(T):
            out[t] = w @ R[t]
            w = w * (1 + R[t])
            w = w / w.sum() if w.sum() > 0 else w
            if fim_mes[t] and t >= 252:
                nw = pesos_fn(t)
                g = np.abs(nw - w).sum()
                giro += g
                out[t] -= g * custo
                w = nw
        return out, giro / (T / 252)

    vol60 = pd.DataFrame(R).rolling(60).std().to_numpy()
    janelas = (63, 126, 252)

    def pesos_iguais(t):
        return np.full(N, 1 / N)

    def paridade_risco(t):
        iv = 1 / np.maximum(vol60[t], 1e-6)
        return iv / iv.sum()

    escolha_hist = []

    def momentum_wf(t):
        # walk-forward: escolhe a janela de momentum pelo Sharpe dos ÚLTIMOS 3 anos, sem olhar o futuro
        inicio = max(252, t - 756)
        melhor, msh = janelas[-1], -1e9
        for L in janelas:
            sinais = []
            for s in range(inicio, t, 21):
                if s < L:
                    continue
                m = R[s - L:s].sum(0) > 0
                w = m / m.sum() if m.sum() > 0 else np.zeros(N)
                sinais.append(R[s:min(s + 21, t)] @ w)
            if sinais:
                v = np.concatenate(sinais)
                sh = v.mean() / v.std() if v.std() > 0 else -1e9
                if sh > msh:
                    melhor, msh = L, sh
        escolha_hist.append({"data": datas[t], "janela_escolhida": melhor})
        m = R[t - melhor:t].sum(0) > 0
        return m / m.sum() if m.sum() > 0 else np.zeros(N)

    estrategias = {"Pesos iguais": pesos_iguais, "Paridade de risco": paridade_risco,
                   "Momentum (janela walk-forward)": momentum_wf}
    curvas, linhas = [], []
    sp = R[:, list(r.columns).index("US500")]
    for nome, fn in estrategias.items():
        ret, giro = simular(fn)
        ret = ret[252:]
        m = _metricas(ret)
        m.update({"estrategia": nome, "giro_anual": giro})
        linhas.append(m)
        curvas.append(pd.DataFrame({"estrategia": nome, "data": datas[252:],
                                    "patrimonio": np.cumprod(1 + ret)}).iloc[::5])
    m = _metricas(sp[252:])
    m.update({"estrategia": "S&P 500 comprado", "giro_anual": 0.0})
    linhas.append(m)
    curvas.append(pd.DataFrame({"estrategia": "S&P 500 comprado", "data": datas[252:],
                                "patrimonio": np.cumprod(1 + sp[252:])}).iloc[::5])
    t = pd.DataFrame(linhas)
    # portões STOP do pipeline (Kostovcik): reprovou um, a estratégia não segue para produção
    # critérios DECLARADOS antes de rodar (portão que aprova tudo não filtra nada — bugs.md BUG-008)
    t["portao_sharpe"] = t.sharpe >= 0.5
    t["portao_drawdown"] = t.drawdown_max_pct >= -30
    t["portao_custos"] = t.giro_anual * custo_bps / 100 < 1.0     # custo anual < 1% a.a.
    t["veredito"] = np.where(t.portao_sharpe & t.portao_drawdown & t.portao_custos, "APROVADA", "STOP")
    cols = ["estrategia", "cagr_pct", "vol_anual_pct", "sharpe", "sortino", "drawdown_max_pct", "dias_positivos_pct",
            "giro_anual", "portao_sharpe", "portao_drawdown", "portao_custos", "veredito"]
    t = t[cols]
    jan = pd.DataFrame(escolha_hist)
    jan = jan.drop_duplicates("data")
    aprov = t[t.veredito == "APROVADA"].estrategia.tolist()
    return {"tabelas": {"metricas": t, "curvas": pd.concat(curvas, ignore_index=True), "janelas_momentum": jan},
            "destaque": (f"Com custos de {br(custo_bps, 0)} bps por giro, {len(aprov)} de {len(t)} estratégias passam pelos "
                         f"três portões STOP ({', '.join(aprov) or 'nenhuma'}). A janela do momentum, escolhida a cada mês "
                         f"só com o passado, mudou {int((jan.janela_escolhida.diff() != 0).sum() - 1)} vezes — "
                         f"o 'parâmetro ótimo' não é constante.")}
