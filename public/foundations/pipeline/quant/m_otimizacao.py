# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Otimização: fronteira de Markowitz, algoritmo genético (carteira e indicadores) e
programação genética (regressão simbólica).

Paralelismo (D8): as RODADAS independentes (sementes diferentes) vão para o
ProcessPoolExecutor — avaliar a população dentro de uma geração já é numba e custaria
mais em serialização do que em CPU. A dispersão entre sementes é reportada: um ótimo
que muda a cada semente não é ótimo, é ruído.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from config import paralelizar
from quant import kernels as K
from quant.dados import NOMES, retornos, serie
from quant.util import br, pct

UNIVERSO = ["US500", "US100", "XAUUSD", "XAGUSD", "WTI", "COPPER", "EURUSD", "USDJPY", "USTBOND", "SOYBEAN"]
CORTE = "2020-01-01"   # treino < CORTE ≤ teste


def _treino_teste():
    r = retornos(simbolos=UNIVERSO)
    return r[r.index < CORTE], r[r.index >= CORTE]


# ─────────────────────────────────────────────────────────────────────────────
def markowitz_fronteira(n_aleatorias: int = 20000) -> dict:
    from scipy.optimize import minimize
    tr, te = _treino_teste()
    mu = tr.mean().to_numpy() * 252
    S = tr.cov().to_numpy() * 252
    n = mu.size
    rng = np.random.default_rng(42)
    W = rng.dirichlet(np.ones(n) * 0.6, n_aleatorias)
    ret = W @ mu
    vol = np.sqrt(np.einsum("ij,jk,ik->i", W, S, W))
    nuvem = pd.DataFrame({"retorno_anual_pct": ret * 100, "vol_anual_pct": vol * 100, "sharpe": ret / vol})
    nuvem = nuvem.iloc[::4]
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    b = [(0, 1)] * n
    w0 = np.full(n, 1 / n)
    minvar = minimize(lambda w: w @ S @ w, w0, bounds=b, constraints=cons).x
    maxsh = minimize(lambda w: -(w @ mu) / math.sqrt(w @ S @ w), w0, bounds=b, constraints=cons).x
    fronteira = []
    for alvo in np.linspace(minvar @ mu, mu.max() * 0.98, 30):
        c2 = cons + [{"type": "eq", "fun": lambda w, a=alvo: w @ mu - a}]
        w = minimize(lambda w: w @ S @ w, w0, bounds=b, constraints=c2).x
        fronteira.append({"retorno_anual_pct": w @ mu * 100, "vol_anual_pct": math.sqrt(w @ S @ w) * 100})
    carteiras = {"Mínima variância": minvar, "Máximo Sharpe (tangência)": maxsh, "Pesos iguais": w0}
    pesos = pd.DataFrame([{"carteira": k, "simbolo": s, "nome": NOMES[s], "peso": v[i]}
                          for k, v in carteiras.items() for i, s in enumerate(tr.columns)])
    fora = []
    for k, w in carteiras.items():
        m_tr = K.metricas_carteiras(tr.to_numpy(), w[None, :], 252.0, 0.0)[0]
        m_te = K.metricas_carteiras(te.to_numpy(), w[None, :], 252.0, 0.0)[0]
        fora.append({"carteira": k, "sharpe_treino": m_tr[2], "sharpe_teste": m_te[2], "vol_teste_pct": m_te[1] * 100,
                     "drawdown_teste_pct": m_te[3] * 100, "retorno_teste_pct": m_te[0] * 100})
    f = pd.DataFrame(fora)
    ms = f.set_index("carteira").loc["Máximo Sharpe (tangência)"]
    ig = f.set_index("carteira").loc["Pesos iguais"]
    return {"tabelas": {"nuvem": nuvem, "fronteira": pd.DataFrame(fronteira), "pesos": pesos, "fora_amostra": f},
            "destaque": (f"A carteira de máximo Sharpe tinha Sharpe {br(ms.sharpe_treino)} em 2010–2019 e entregou "
                         f"{br(ms.sharpe_teste)} em 2020–2026; os pesos iguais foram de {br(ig.sharpe_treino)} para "
                         f"{br(ig.sharpe_teste)}. A fronteira é exata sobre o passado — o erro está na estimativa "
                         f"de médias que o futuro não repete.")}


# ─────────────────────────────────────────────────────────────────────────────
def _ag_rodada(args):
    """Uma rodada completa do AG (função pura). Devolve (melhor peso, histórico de aptidão)."""
    R, semente, pop, geracoes, elite, taxa_mut, penal_dd = args
    rng = np.random.default_rng(semente)
    n = R.shape[1]
    P = rng.dirichlet(np.ones(n), pop)
    hist = []
    for g in range(geracoes):
        m = K.metricas_carteiras(R, P, 252.0, 0.0)
        apt = m[:, 2] + penal_dd * m[:, 3]           # Sharpe + penalidade (drawdown é negativo)
        ordem = np.argsort(apt)[::-1]
        hist.append((g, float(apt[ordem[0]]), float(np.median(apt))))
        nova = [P[i] for i in ordem[:elite]]          # elitismo
        prob = apt - apt.min() + 1e-9
        prob = prob / prob.sum()                      # roleta
        while len(nova) < pop:
            a, b = P[rng.choice(pop, p=prob)], P[rng.choice(pop, p=prob)]
            corte = rng.integers(1, n)
            filho = np.concatenate([a[:corte], b[corte:]])
            if rng.random() < taxa_mut:
                j = rng.integers(n)
                filho[j] = max(0.0, filho[j] + rng.normal(0, 0.15))
            s = filho.sum()
            filho = filho / s if s > 0 else np.full(n, 1 / n)
            nova.append(filho)
        P = np.array(nova)
    m = K.metricas_carteiras(R, P, 252.0, 0.0)
    apt = m[:, 2] + penal_dd * m[:, 3]
    return P[int(np.argmax(apt))], hist


def ag_carteira(sementes=(1, 2, 3, 4), pop: int = 120, geracoes: int = 60) -> dict:
    tr, te = _treino_teste()
    Rtr = tr.to_numpy()
    tarefas = [(Rtr, s, pop, geracoes, 6, 0.3, 0.5) for s in sementes]
    res = paralelizar(tarefas, _ag_rodada, trabalho=pop * geracoes * Rtr.size * len(sementes))
    linhas, pesos, evol = [], [], []
    for s, (w, hist) in zip(sementes, res):
        m_tr = K.metricas_carteiras(Rtr, w[None, :], 252.0, 0.0)[0]
        m_te = K.metricas_carteiras(te.to_numpy(), w[None, :], 252.0, 0.0)[0]
        linhas.append({"semente": s, "sharpe_treino": m_tr[2], "drawdown_treino_pct": m_tr[3] * 100,
                       "sharpe_teste": m_te[2], "drawdown_teste_pct": m_te[3] * 100})
        for i, c in enumerate(tr.columns):
            pesos.append({"semente": s, "simbolo": c, "nome": NOMES[c], "peso": w[i]})
        for g, melhor, mediana in hist:
            evol.append({"semente": s, "geracao": g, "melhor_aptidao": melhor, "aptidao_mediana": mediana})
    t = pd.DataFrame(linhas)
    pw = pd.DataFrame(pesos)
    disp = pw.groupby("simbolo").peso.std().mean()
    eq = K.metricas_carteiras(te.to_numpy(), np.full((1, tr.shape[1]), 1 / tr.shape[1]), 252.0, 0.0)[0]
    return {"tabelas": {"rodadas": t, "pesos": pw, "evolucao": pd.DataFrame(evol)},
            "destaque": (f"Quatro rodadas paralelas do AG, com sementes diferentes, convergem para a mesma carteira "
                         f"(desvio médio de peso de {br(disp * 100, 1)} p.p.) com Sharpe de {br(t.sharpe_treino.mean())} "
                         f"em 2010–2019. Em 2020–2026 ela entrega {br(t.sharpe_teste.mean())}, abaixo dos pesos iguais "
                         f"({br(eq[2])}): convergência prova que o ótimo é estável, não que o futuro vai repeti-lo.")}


# ─────────────────────────────────────────────────────────────────────────────
def _regra(c: np.ndarray, cromo: np.ndarray) -> np.ndarray:
    """Cromossomo: [usa_mm, rapida, lenta, usa_rsi, rsi_baixo, usa_rompimento, janela_rompimento]."""
    votos = np.zeros(c.size)
    ativos = 0
    if cromo[0] > 0.5:
        r, l = int(cromo[1]), int(cromo[2])
        mr = pd.Series(c).rolling(r).mean().to_numpy()
        ml = pd.Series(c).rolling(l).mean().to_numpy()
        votos += np.where(mr > ml, 1.0, 0.0)
        ativos += 1
    if cromo[3] > 0.5:
        rs = K.rsi(c, 14)
        votos += np.where(rs > cromo[4], 1.0, 0.0)
        ativos += 1
    if cromo[5] > 0.5:
        n = int(cromo[6])
        mx = pd.Series(c).rolling(n).max().shift(1).to_numpy()
        mn = pd.Series(c).rolling(n).min().shift(1).to_numpy()
        votos += np.where(c > (mx + mn) / 2, 1.0, 0.0)
        ativos += 1
    if ativos == 0:
        return np.ones(c.size)
    return np.where(votos / ativos > 0.5, 1.0, 0.0)


LIM = np.array([[0, 1], [5, 60], [40, 250], [0, 1], [30, 60], [0, 1], [10, 120]], float)


def _ag_regras_rodada(args):
    c, r, corte, semente, pop, geracoes = args
    rng = np.random.default_rng(semente)
    P = LIM[:, 0] + rng.random((pop, LIM.shape[0])) * (LIM[:, 1] - LIM[:, 0])
    avaliadas = 0
    cache = {}

    def apt(cr):
        nonlocal avaliadas
        chave = tuple(np.round(cr, 0))
        if chave not in cache:
            pos = _regra(c, np.round(cr, 0))
            ret = pos[:-1] * r[1:] - 0.0005 * np.abs(np.diff(pos))
            cache[chave] = K.sharpe_anual(ret[:corte], 252.0)
            avaliadas += 1
        return cache[chave]

    for _ in range(geracoes):
        f = np.array([apt(x) for x in P])
        ordem = np.argsort(f)[::-1]
        nova = [P[i].copy() for i in ordem[:4]]
        while len(nova) < pop:
            i, j = rng.choice(ordem[:pop // 2], 2)
            m = rng.random(LIM.shape[0]) < 0.5
            filho = np.where(m, P[i], P[j])
            if rng.random() < 0.4:
                g = rng.integers(LIM.shape[0])
                filho[g] = LIM[g, 0] + rng.random() * (LIM[g, 1] - LIM[g, 0])
            nova.append(filho)
        P = np.array(nova)
    f = np.array([apt(x) for x in P])
    melhor = np.round(P[int(np.argmax(f))], 0)
    pos = _regra(c, melhor)
    ret = pos[:-1] * r[1:] - 0.0005 * np.abs(np.diff(pos))
    return melhor, K.sharpe_anual(ret[:corte], 252.0), K.sharpe_anual(ret[corte:], 252.0), avaliadas


def ag_indicadores(simbolo: str = "US500", sementes=(11, 12, 13, 14)) -> dict:
    d = serie(simbolo)
    d = d[d.index.dayofweek < 5].loc["2008":]
    c = d["close"].to_numpy()
    r = np.diff(np.log(c), prepend=np.nan)
    r[0] = 0.0
    corte = int(np.searchsorted(d.index.values, np.datetime64("2019-01-01")))
    tarefas = [(c, r, corte, s, 40, 25) for s in sementes]
    res = paralelizar(tarefas, _ag_regras_rodada, trabalho=10**7)
    linhas = []
    for s, (cr, sh_tr, sh_te, aval) in zip(sementes, res):
        linhas.append({"semente": s, "usa_medias": bool(cr[0]), "media_rapida": int(cr[1]), "media_lenta": int(cr[2]),
                       "usa_rsi": bool(cr[3]), "rsi_limiar": int(cr[4]), "usa_rompimento": bool(cr[5]),
                       "janela_rompimento": int(cr[6]), "sharpe_treino": sh_tr, "sharpe_teste": sh_te,
                       "regras_avaliadas": aval})
    t = pd.DataFrame(linhas)
    bh_te = K.sharpe_anual(r[corte + 1:], 252.0)
    total = int(t.regras_avaliadas.sum())
    return {"tabelas": {"rodadas": t},
            "destaque": (f"O AG testou {total} regras distintas no S&P 500 e a melhor de cada rodada teve Sharpe de treino "
                         f"até {br(t.sharpe_treino.max())}; em 2019–2026 elas ficaram entre {br(t.sharpe_teste.min())} e "
                         f"{br(t.sharpe_teste.max())}, contra {br(bh_te)} de simplesmente ficar comprado. Quanto mais "
                         f"regras se testa, maior o Sharpe de treino por puro acaso.")}


# ─────────────────────────────────────────────────────────────────────────────
# Programação genética — árvores como tuplas: ("op", filho, filho) | ("x", i) | ("c", valor)
_BIN = {"+": 0, "-": 1, "*": 2, "/": 3, "max": 6}
_UN = {"sen": 4, "cos": 5, "neg": 7}


def _arvore_aleatoria(rng, prof, nvars):
    if prof == 0 or (prof < 3 and rng.random() < 0.3):
        return ("x", int(rng.integers(nvars))) if rng.random() < 0.75 else ("c", float(np.round(rng.normal(0, 1), 2)))
    if rng.random() < 0.2:
        return (rng.choice(list(_UN)), _arvore_aleatoria(rng, prof - 1, nvars))
    return (rng.choice(list(_BIN)), _arvore_aleatoria(rng, prof - 1, nvars), _arvore_aleatoria(rng, prof - 1, nvars))


def _posfixa(a, cod, cst):
    if a[0] == "x":
        cod.append(a[1]); cst.append(0.0)
    elif a[0] == "c":
        cod.append(100); cst.append(a[1])
    elif a[0] in _UN:
        _posfixa(a[1], cod, cst); cod.append(200 + _UN[a[0]]); cst.append(0.0)
    else:
        _posfixa(a[1], cod, cst); _posfixa(a[2], cod, cst); cod.append(200 + _BIN[a[0]]); cst.append(0.0)


def _tamanho(a):
    return 1 if a[0] in ("x", "c") else 1 + sum(_tamanho(f) for f in a[1:])


def _texto(a):
    nomes = ["r1", "r2", "r3"]
    if a[0] == "x":
        return nomes[a[1]]
    if a[0] == "c":
        return f"{a[1]:g}"
    if a[0] in _UN:
        return f"{a[0]}({_texto(a[1])})"
    if a[0] == "max":
        return f"max({_texto(a[1])}, {_texto(a[2])})"
    return f"({_texto(a[1])} {a[0]} {_texto(a[2])})"


def _subarvores(a, caminho=()):
    yield caminho, a
    if a[0] not in ("x", "c"):
        for i, f in enumerate(a[1:], start=1):
            yield from _subarvores(f, caminho + (i,))


def _substituir(a, caminho, nova):
    if not caminho:
        return nova
    i = caminho[0]
    lst = list(a)
    lst[i] = _substituir(a[i], caminho[1:], nova)
    return tuple(lst)


def _avaliar(a, X):
    cod, cst = [], []
    _posfixa(a, cod, cst)
    return K.avaliar_posfixa(np.array(cod, np.int64), np.array(cst), X)


def _postos(v):
    o = np.argsort(v, kind="stable")
    p = np.empty(v.size)
    p[o] = np.arange(v.size)
    return p


def _ic(pred, y):
    """IC de POSTOS (Spearman). Pearson é dominado por poucos dias extremos quando a fórmula
    eleva retornos ao quadrado — dava IC de 0,37 'no treino' — ver bugs.md BUG-007."""
    if not np.all(np.isfinite(pred)) or pred.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(_postos(pred), _postos(y))[0, 1])


def _pg_rodada(args):
    X, y, corte, semente, pop, geracoes, parcimonia = args
    rng = np.random.default_rng(semente)
    P = [_arvore_aleatoria(rng, 4, X.shape[1]) for _ in range(pop)]

    def apt(a):
        return abs(_ic(_avaliar(a, X[:corte]), y[:corte])) - parcimonia * _tamanho(a)

    hist = []
    for g in range(geracoes):
        f = np.array([apt(a) for a in P])
        ordem = np.argsort(f)[::-1]
        hist.append((g, float(f[ordem[0]])))
        nova = [P[i] for i in ordem[:5]]
        while len(nova) < pop:
            torneio = rng.choice(pop, 7)
            pai = P[torneio[np.argmax(f[torneio])]]
            torneio = rng.choice(pop, 7)
            mae = P[torneio[np.argmax(f[torneio])]]
            if rng.random() < 0.7:   # crossover de subárvores
                cp, _ = list(_subarvores(pai))[rng.integers(_tamanho(pai))]
                _, sub = list(_subarvores(mae))[rng.integers(_tamanho(mae))]
                filho = _substituir(pai, cp, sub)
            else:                     # mutação: troca uma subárvore por uma nova
                cp, _ = list(_subarvores(pai))[rng.integers(_tamanho(pai))]
                filho = _substituir(pai, cp, _arvore_aleatoria(rng, 2, X.shape[1]))
            if _tamanho(filho) <= 25:
                nova.append(filho)
        P = nova
    f = np.array([apt(a) for a in P])
    melhor = P[int(np.argmax(f))]
    pred = _avaliar(melhor, X)
    return _texto(melhor), _tamanho(melhor), _ic(pred[:corte], y[:corte]), _ic(pred[corte:], y[corte:]), hist


def programacao_genetica(simbolo: str = "US500", sementes=(21, 22, 23, 24)) -> dict:
    r = retornos()[simbolo].to_numpy()
    z = (r - r.mean()) / r.std()
    X = np.column_stack([z[2:-1], z[1:-2], z[:-3]])     # r1 = último, r2 = penúltimo, r3 = antepenúltimo
    y = z[3:]                                             # próximo retorno
    corte = int(0.6 * y.size)
    tarefas = [(X, y, corte, s, 200, 30, 0.0005) for s in sementes]
    res = paralelizar(tarefas, _pg_rodada, trabalho=10**8)
    linhas, evol = [], []
    for s, (txt, tam, ic_tr, ic_te, hist) in zip(sementes, res):
        linhas.append({"semente": s, "formula": txt, "nos": tam, "ic_treino": ic_tr, "ic_teste": ic_te})
        evol += [{"semente": s, "geracao": g, "melhor_aptidao": a} for g, a in hist]
    t = pd.DataFrame(linhas)
    melhor = t.sort_values("nos").iloc[0]   # a mais parcimoniosa é a que se consegue ler e auditar
    return {"tabelas": {"formulas": t, "evolucao": pd.DataFrame(evol)},
            "destaque": (f"A programação genética descobriu fórmulas legíveis como {melhor.formula} ({melhor.nos} nós), com correlação de "
                         f"postos de {br(melhor.ic_treino, 3)} com o próximo retorno no treino e "
                         f"{br(melhor.ic_teste, 3)} no teste. "
                         f"A evolução sempre encontra 'algo' no passado; só o período nunca visto separa indicador de "
                         f"coincidência.")}
