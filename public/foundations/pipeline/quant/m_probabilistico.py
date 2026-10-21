# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Modelos probabilísticos: cadeia de Markov de regimes, HMM gaussiano, atualização bayesiana
e regras ótimas de trading por Monte Carlo de Ornstein-Uhlenbeck."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from config import particionar, paralelizar
from quant import kernels as K
from quant.dados import NOMES, retornos, serie
from quant.util import br, pct

REGIMES = ["baixa", "lateral", "alta"]


# ─────────────────────────────────────────────────────────────────────────────
def markov_regimes(simbolo: str = "US500", janela: int = 20) -> dict:
    """Regime por retorno acumulado de `janela` pregões contra ±0,5 desvio desse acumulado."""
    r = retornos()[simbolo]
    acum = r.rolling(janela).sum().dropna()
    lim = 0.5 * acum.std()
    est = np.where(acum < -lim, 0, np.where(acum > lim, 2, 1)).astype(np.int64)
    # transição de BLOCO a bloco (não sobreposto) para não contar a mesma janela várias vezes
    blocos = est[::janela]
    P = K.matriz_transicao(blocos, 3)
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    pi = pi / pi.sum()
    duracao = 1 / (1 - np.diag(P))
    mat = pd.DataFrame(P, index=REGIMES, columns=REGIMES).reset_index().rename(columns={"index": "de"}) \
        .melt(id_vars="de", var_name="para", value_name="probabilidade")
    resumo = pd.DataFrame({"regime": REGIMES, "estacionaria": pi, "duracao_esperada_blocos": duracao,
                           "duracao_esperada_pregoes": duracao * janela,
                           "frequencia_observada": [float((blocos == k).mean()) for k in range(3)]})
    horiz = []
    Pn = np.eye(3)
    for n in range(1, 13):
        Pn = Pn @ P
        for i, de in enumerate(REGIMES):
            horiz.append({"blocos": n, "pregoes": n * janela, "de": de, "p_alta": Pn[i, 2], "p_baixa": Pn[i, 0]})
    hist = pd.DataFrame({"data": acum.index[::janela], "regime": [REGIMES[k] for k in blocos]})
    pbx_alta = P[0, 2]
    return {"tabelas": {"transicao": mat, "resumo": resumo, "horizonte": pd.DataFrame(horiz), "historico": hist},
            "destaque": (f"No S&P 500, estando em baixa em um bloco de {janela} pregões, a chance de o próximo bloco ser "
                         f"de alta é {pct(pbx_alta)} — maior que a de continuar em baixa ({pct(P[0, 0])}). "
                         f"Em equilíbrio, o mercado passa {pct(pi[2])} do tempo em regime de alta.")}


# ─────────────────────────────────────────────────────────────────────────────
def hmm_regimes(simbolo: str = "US500") -> dict:
    r = retornos()[simbolo]
    x = r.to_numpy()
    sd = x.std()
    # inicialização por VOLATILIDADE (não por média): regimes de mercado se distinguem mais pela
    # variância do que pela média — inicializar pela média leva a ótimo local ruim.
    mu0 = np.array([0.0, 0.0, 0.0])
    sd0 = np.array([0.5 * sd, 1.0 * sd, 2.5 * sd])
    pi, A, mu, sdv, gamma, ll = K.hmm_gaussiano_em(x, mu0, sd0, 500, 1e-7)
    ordem = np.argsort(sdv)  # 0 = calmo … 2 = turbulento
    nomes = ["calmo", "normal", "turbulento"]
    A = A[np.ix_(ordem, ordem)]
    mu, sdv, gamma = mu[ordem], sdv[ordem], gamma[:, ordem]
    estados = pd.DataFrame({"estado": nomes, "media_diaria_pct": mu * 100, "vol_anual_pct": sdv * math.sqrt(252) * 100,
                            "persistencia": np.diag(A), "duracao_media_pregoes": 1 / (1 - np.diag(A)),
                            "fracao_tempo": gamma.mean(0)})
    prob = pd.DataFrame({"data": r.index, **{f"p_{n}": gamma[:, i] for i, n in enumerate(nomes)},
                         "retorno_pct": x * 100})
    atual = nomes[int(np.argmax(gamma[-1]))]
    t = estados.set_index("estado")
    return {"tabelas": {"estados": estados, "probabilidades": prob,
                        "transicao": pd.DataFrame(A, index=nomes, columns=nomes).reset_index().rename(
                            columns={"index": "de"})},
            "destaque": (f"Sem regra de corte arbitrária, o HMM encontra três regimes no S&P 500: o turbulento tem "
                         f"volatilidade de {br(t.loc['turbulento'].vol_anual_pct, 0)}% ao ano contra "
                         f"{br(t.loc['calmo'].vol_anual_pct, 0)}% no calmo e dura em média "
                         f"{br(t.loc['turbulento'].duracao_media_pregoes, 0)} pregões. Hoje o regime mais provável é "
                         f"'{atual}'.")}


# ─────────────────────────────────────────────────────────────────────────────
def bayes_conjugado(simbolo: str = "XAUUSD") -> dict:
    """Normal com média e variância desconhecidas — prior Normal-Gama (μ0, κ0, α0, β0).

    Atualização sequencial por pregão; intervalo de credibilidade de 95% da média via t de Student.
    """
    r = retornos()[simbolo].loc["2019":]
    x = r.to_numpy()
    mu0, k0, a0 = 0.0, 50.0, 3.0                  # prior cético: média ≈ 0 com peso de 50 dias
    b0 = (x[:250].var() if x.size > 250 else x.var()) * (a0 - 1)
    mu, k, a, b = mu0, k0, a0, b0
    linhas = []
    for i, xi in enumerate(x):
        mu_n = (k * mu + xi) / (k + 1)
        b = b + k * (xi - mu) ** 2 / (2 * (k + 1))
        k, a, mu = k + 1, a + 0.5, mu_n
        escala = math.sqrt(b / (a * k))
        tq = stats.t.ppf(0.975, 2 * a)
        vol = math.sqrt(b / (a - 1)) if a > 1 else np.nan
        if i % 5 == 0 or i == x.size - 1:
            linhas.append({"data": r.index[i], "media_post_anual_pct": mu * 252 * 100,
                           "ic95_inf_anual_pct": (mu - tq * escala) * 252 * 100,
                           "ic95_sup_anual_pct": (mu + tq * escala) * 252 * 100,
                           "vol_post_anual_pct": vol * math.sqrt(252) * 100,
                           "p_media_positiva": float(stats.t.sf(-mu / escala, 2 * a))})
    t = pd.DataFrame(linhas)
    ult = t.iloc[-1]
    freq = x.mean() * 252 * 100
    return {"tabelas": {"posterior": t},
            "destaque": (f"Ouro desde 2019: o retorno médio anual a posteriori é {br(ult.media_post_anual_pct, 1)}%, mas "
                         f"o intervalo de credibilidade de 95% vai de {br(ult.ic95_inf_anual_pct, 1)}% a "
                         f"{br(ult.ic95_sup_anual_pct, 1)}%. A probabilidade de a média ser positiva é "
                         f"{pct(ult.p_media_positiva)} — a média amostral ({br(freq, 1)}%) sozinha não diz isso.")}


# ─────────────────────────────────────────────────────────────────────────────
def _ou_bloco(args):
    """Função PURA para o ProcessPoolExecutor: um bloco de linhas (alvos) da malha."""
    previsao, meia_vida, pts, sls, n_iter, max_hp, semente = args
    return K.ou_sharpe_malha(previsao, meia_vida, 1.0, np.asarray(pts), np.asarray(sls), n_iter, max_hp, semente)


def ajustar_ou(x: np.ndarray) -> tuple[float, float, float]:
    """AR(1) em tempo discreto: x_t = c + φ·x_{t-1} + ε. Devolve (φ, meia-vida, σ)."""
    y, z = x[1:], x[:-1]
    Z = np.column_stack([np.ones_like(z), z])
    (c, phi), *_ = np.linalg.lstsq(Z, y, rcond=None)
    res = y - (c + phi * z)
    phi = min(max(phi, 1e-6), 0.999999)
    return float(phi), float(-math.log(2) / math.log(phi)), float(res.std())


def triple_barrier_ou(n_iter: int = 4000, max_hp: int = 100) -> dict:
    """Regras ótimas de lucro/stop (López de Prado, cap. 13) para o spread Brent − WTI."""
    p = np.log(serie("BRENT")["close"]).to_frame("b").join(np.log(serie("WTI")["close"]).to_frame("w"), how="inner")
    p = p[p.index.dayofweek < 5].loc["2015":]
    spread = (p.b - p.w).to_numpy()
    phi, meia, sig = ajustar_ou(spread)
    grade = np.linspace(0.5, 10.0, 20)  # em unidades de σ do ruído
    blocos = particionar(range(grade.size), 4)  # partição FIXA, independente do nº de processos (D8)
    previsoes = [0.0, 2.5]
    linhas = []
    for prev in previsoes:
        tarefas = [(prev, meia, grade[b].tolist(), grade.tolist(), n_iter, max_hp, 1234 + 97 * i)
                   for i, b in enumerate(blocos)]
        partes = paralelizar(tarefas, _ou_bloco, trabalho=n_iter * max_hp * grade.size ** 2)
        malha = np.vstack(partes)
        for i, pt in enumerate(grade):
            for j, sl in enumerate(grade):
                linhas.append({"previsao_sigmas": prev, "alvo_lucro_sigmas": pt, "stop_sigmas": sl,
                               "sharpe": malha[i, j]})
    t = pd.DataFrame(linhas)
    ot = t[t.previsao_sigmas == 0.0].sort_values("sharpe", ascending=False).iloc[0]
    params = pd.DataFrame([{"serie": "Spread log Brent − WTI", "phi": phi, "meia_vida_pregoes": meia,
                            "sigma": sig, "n_iter": n_iter, "max_hp": max_hp}])
    return {"tabelas": {"malha": t, "parametros": params},
            "destaque": (f"O spread Brent − WTI reverte à média com meia-vida de {br(meia, 0)} pregões. Simulando "
                         f"{br(n_iter, 0)} trajetórias por célula, a melhor regra é alvo de {br(ot.alvo_lucro_sigmas, 1)}σ "
                         f"com stop de {br(ot.stop_sigmas, 1)}σ (Sharpe por operação {br(ot.sharpe)}) — um stop "
                         f"percentual fixo ignora a dinâmica do ativo.")}
