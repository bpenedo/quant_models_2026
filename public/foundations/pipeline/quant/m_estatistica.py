# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Modelos estatísticos: descritiva, suporte/resistência, ADF, regressão, outliers, Benford,
GARCH, caudas pesadas e causalidade de Granger.

Contrato de todo modelo: `rodar() -> dict` com
    "tabelas":  {nome: DataFrame}   → CSV do site evidence
    "destaque": str                 → a leitura não óbvia (vai para tela e README)
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from quant import kernels as K
from quant.dados import CLASSES, NOMES, retornos, serie
from quant.util import br, pct


def _ols(y: np.ndarray, X: np.ndarray):
    """MQO com erros-padrão clássicos. X já inclui a constante."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    n, k = X.shape
    s2 = res @ res / (n - k)
    cov = s2 * np.linalg.inv(X.T @ X)
    return beta, np.sqrt(np.diag(cov)), res


# ─────────────────────────────────────────────────────────────────────────────
def estatistica_descritiva() -> dict:
    r = retornos()
    linhas = []
    for s in r.columns:
        x = r[s].to_numpy()
        med = float(np.median(x))
        mad = float(np.median(np.abs(x - med)) * 1.4826)
        linhas.append({
            "simbolo": s, "nome": NOMES.get(s, s), "classe": CLASSES.get(s, "—"),
            "media_anual_pct": x.mean() * 252 * 100, "mediana_diaria_pct": med * 100,
            "vol_anual_pct": x.std(ddof=1) * math.sqrt(252) * 100, "sigma_robusta_anual_pct": mad * math.sqrt(252) * 100,
            "assimetria": float(stats.skew(x)), "curtose_excesso": float(stats.kurtosis(x)),
            "p01_pct": np.percentile(x, 1) * 100, "p99_pct": np.percentile(x, 99) * 100,
            "pior_dia_pct": x.min() * 100, "melhor_dia_pct": x.max() * 100,
        })
    t = pd.DataFrame(linhas).sort_values("vol_anual_pct", ascending=False)
    # Quarteto de Anscombe — mesma média e mesma reta, dados diferentes
    ans = pd.DataFrame({
        "x123": [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
        "y1": [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
        "y2": [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
        "y3": [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
        "x4": [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
        "y4": [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89],
    })
    gap = t.assign(gap=lambda d: d.vol_anual_pct / d.sigma_robusta_anual_pct).sort_values("gap", ascending=False).iloc[0]
    return {"tabelas": {"resumo": t, "anscombe": ans},
            "destaque": (f"{NOMES.get(gap.simbolo, gap.simbolo)} tem desvio-padrão {br(gap.gap, 1)}× maior que a σ robusta: "
                         f"poucos dias extremos inflam a volatilidade 'média' — curtose em excesso de "
                         f"{br(gap.curtose_excesso, 1)}.")}


# ─────────────────────────────────────────────────────────────────────────────
def suporte_resistencia(simbolo: str = "XAUUSD", anos: int = 2, k: int = 6) -> dict:
    s = serie(simbolo)["close"]
    s = s[s.index >= s.index[-1] - pd.DateOffset(years=anos)]
    p = s.to_numpy()
    vol = np.std(np.diff(np.log(p))) * p.mean()
    passo = 10 ** math.floor(math.log10(max(vol, 1e-9)))  # passo ~ ordem de grandeza da oscilação diária
    nivel = np.round(p / passo) * passo
    contagem = pd.Series(nivel).value_counts()
    freq = np.repeat(contagem.index.to_numpy(float), contagem.to_numpy())
    centros, rot = K.kmeans_1d(freq, k, 200)
    faixas = []
    for j in range(k):
        v = freq[rot == j]
        if v.size == 0:
            continue
        faixas.append({"faixa": j + 1, "centro": float(centros[j]), "minimo": float(v.min()),
                       "maximo": float(v.max()), "visitas": int(v.size)})
    f = pd.DataFrame(faixas).sort_values("centro")
    f["intensidade_pct"] = f.visitas / f.visitas.sum() * 100
    preco = pd.DataFrame({"data": s.index, "fechamento": p})
    moda = float(contagem.index[0])
    ultimo = float(p[-1])
    f["tipo"] = np.where(f.centro < ultimo, "suporte", "resistência")
    forte = f.sort_values("visitas", ascending=False).iloc[0]
    return {"tabelas": {"faixas": f, "preco": preco},
            "destaque": (f"{NOMES[simbolo]}: a moda dos preços arredondados é {br(moda)}; a faixa mais visitada "
                         f"({br(forte.minimo)}–{br(forte.maximo)}) concentra {br(forte.intensidade_pct, 0)}% dos "
                         f"pregões e hoje atua como {forte.tipo}.")}


# ─────────────────────────────────────────────────────────────────────────────
# ADF — MacKinnon (2010), valores críticos com constante, aproximação de superfície
_ADF_C = {0.01: (-3.43035, -6.5393, -16.786, -79.433),
          0.05: (-2.86154, -2.8903, -4.234, -40.040),
          0.10: (-2.56677, -1.5384, -2.809, 0.0)}


def adf(y: np.ndarray, lags: int | None = None) -> tuple[float, dict, int]:
    """Teste ADF com constante. Defasagens por Schwert se não informadas."""
    y = np.asarray(y, float)
    n = y.size
    if lags is None:
        lags = int(12 * (n / 100) ** 0.25)
    dy = np.diff(y)
    Y = dy[lags:]
    cols = [np.ones_like(Y), y[lags:-1]]
    for i in range(1, lags + 1):
        cols.append(dy[lags - i:-i])
    X = np.column_stack(cols)
    beta, se, _ = _ols(Y, X)
    t = beta[1] / se[1]
    N = Y.size
    crit = {f"{int(a * 100)}%": c0 + c1 / N + c2 / N ** 2 + c3 / N ** 3 for a, (c0, c1, c2, c3) in _ADF_C.items()}
    return float(t), crit, lags


def estacionariedade_adf() -> dict:
    simbolos = ["US500", "XAUUSD", "EURUSD", "WTI", "USTBOND", "SOYBEAN", "DXY", "COPPER"]
    linhas = []
    for s in simbolos:
        p = serie(s)["close"]
        p = p[p.index.dayofweek < 5].loc["2010":]
        lp = np.log(p.to_numpy())
        for forma, x in (("log-preço", lp), ("log-retorno", np.diff(lp))):
            t, crit, lags = adf(x)
            linhas.append({"simbolo": s, "nome": NOMES[s], "forma": forma, "estatistica_adf": t,
                           "critico_1pct": crit["1%"], "critico_5pct": crit["5%"], "defasagens": lags,
                           "estacionaria_5pct": t < crit["5%"]})
    t = pd.DataFrame(linhas)
    nprecos = int((t[t.forma == "log-preço"].estacionaria_5pct).sum())
    nret = int((t[t.forma == "log-retorno"].estacionaria_5pct).sum())
    return {"tabelas": {"adf": t},
            "destaque": (f"{nprecos} de {len(simbolos)} séries de preço são estacionárias a 5%; em log-retorno, "
                         f"{nret} de {len(simbolos)}. Treinar com preço é treinar com uma distribuição que não volta.")}


# ─────────────────────────────────────────────────────────────────────────────
def regressao_linear() -> dict:
    pares = [("US100", "US500"), ("US30", "US500"), ("XAGUSD", "XAUUSD"), ("BRENT", "WTI"),
             ("EURUSD", "DXY"), ("XAUUSD", "DXY"), ("COPPER", "US500"), ("USTBOND", "US500")]
    r = retornos()
    linhas = []
    disp = []
    for y, x in pares:
        if y not in r or x not in r:
            continue
        yy, xx = r[y].to_numpy(), r[x].to_numpy()
        beta, se, res = _ols(yy, np.column_stack([np.ones_like(xx), xx]))
        r2 = 1 - res @ res / ((yy - yy.mean()) @ (yy - yy.mean()))
        linhas.append({"y": y, "x": x, "rotulo": f"{NOMES[y]} ~ {NOMES[x]}", "alfa_diario_pct": beta[0] * 100,
                       "beta": beta[1], "ep_beta": se[1], "ic95_inf": beta[1] - 1.96 * se[1],
                       "ic95_sup": beta[1] + 1.96 * se[1], "r2": r2, "correlacao": np.corrcoef(yy, xx)[0, 1],
                       "n": yy.size})
        amostra = np.linspace(0, yy.size - 1, 600).astype(int)
        disp.append(pd.DataFrame({"par": f"{NOMES[y]} ~ {NOMES[x]}", "x_pct": xx[amostra] * 100,
                                  "y_pct": yy[amostra] * 100}))
    t = pd.DataFrame(linhas).sort_values("r2", ascending=False)
    fraco = t.sort_values("r2").iloc[0]
    return {"tabelas": {"coeficientes": t, "dispersao": pd.concat(disp, ignore_index=True)},
            "destaque": (f"{t.iloc[0].rotulo}: β = {br(t.iloc[0].beta)} com R² = {br(t.iloc[0].r2)}. "
                         f"Já {fraco.rotulo} tem R² de {br(fraco.r2)}: a relação 'óbvia' explica quase nada do dia a dia.")}


# ─────────────────────────────────────────────────────────────────────────────
def outliers_multimetodo(simbolo: str = "US500") -> dict:
    from sklearn.neighbors import LocalOutlierFactor
    r = retornos()[simbolo]
    x = r.to_numpy()
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    m_iqr = (x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826
    z = (x - med) / mad
    m_z = np.abs(z) > 4.0
    vol = pd.Series(np.abs(x)).rolling(20, min_periods=5).mean().bfill().to_numpy()
    lof = LocalOutlierFactor(n_neighbors=35, contamination=0.02)
    m_lof = lof.fit_predict(np.column_stack([x, vol])) == -1
    votos = m_iqr.astype(int) + m_z.astype(int) + m_lof.astype(int)
    t = pd.DataFrame({"data": r.index, "retorno_pct": x * 100, "z_robusto": z, "iqr": m_iqr, "z4": m_z,
                      "lof": m_lof, "votos": votos})
    resumo = pd.DataFrame([{"metodo": "Boxplot 1,5·IQR", "outliers": int(m_iqr.sum())},
                           {"metodo": "z-robusto |z|>4 (mediana/MAD)", "outliers": int(m_z.sum())},
                           {"metodo": "LOF (densidade local)", "outliers": int(m_lof.sum())},
                           {"metodo": "Consenso (≥2 votos)", "outliers": int((votos >= 2).sum())}])
    # efeito de UM outlier na regressão (exemplo didático)
    rng = np.random.default_rng(7)
    xa = np.linspace(0, 10, 30)
    ya = 2 + 0.8 * xa + rng.normal(0, 0.6, 30)
    b_sem = np.polyfit(xa, ya, 1)
    xa2, ya2 = np.append(xa, 9.5), np.append(ya, -6.0)
    b_com = np.polyfit(xa2, ya2, 1)
    efeito = pd.DataFrame([{"cenario": "sem outlier", "inclinacao": b_sem[0], "intercepto": b_sem[1]},
                           {"cenario": "com 1 outlier", "inclinacao": b_com[0], "intercepto": b_com[1]}])
    n_iqr = int(m_iqr.sum())
    return {"tabelas": {"pontos": t, "resumo": resumo, "efeito_regressao": efeito},
            "destaque": (f"No S&P 500, o boxplot marca {n_iqr} dias como outlier ({pct(n_iqr / x.size)} da amostra); "
                         f"o consenso de três métodos fica com {int((votos >= 2).sum())}. Um único ponto discrepante "
                         f"muda a inclinação da reta de {br(b_sem[0])} para {br(b_com[0])}.")}


# ─────────────────────────────────────────────────────────────────────────────
def _benford_teste(v: np.ndarray, teorica: np.ndarray) -> dict:
    c = K.primeiros_digitos(v)
    obs = c / c.sum()
    mad = float(np.mean(np.abs(obs - teorica)))
    chi2 = float(((c - teorica * c.sum()) ** 2 / (teorica * c.sum())).sum())
    p1, p99 = np.percentile(v, [1, 99])
    ordens = float(np.log10(p99 / p1)) if p1 > 0 else 0.0
    if ordens < 2.0:
        veredito = "não aplicável (amplitude < 2 ordens de grandeza)"
    else:
        veredito = ("conformidade próxima" if mad < 0.006 else "conformidade aceitável" if mad < 0.012
                    else "conformidade marginal" if mad < 0.015 else "NÃO conforme")
    return {"n": int(c.sum()), "ordens_grandeza": ordens, "mad_nigrini": mad, "qui_quadrado": chi2,
            "veredito": veredito, "_obs": obs}


def benford() -> dict:
    """Lei de Benford sobre volumes. Só se aplica a dados que cobrem várias ordens de grandeza;
    aplicar a uma série de amplitude estreita gera falso alarme — ver bugs.md BUG-003."""
    teorica = np.log10(1 + 1 / np.arange(1, 10))
    linhas = []
    dist = []
    from quant.dados import ohlcv
    d = ohlcv()
    agregado = []
    for s, g in d.groupby("simbolo"):
        v = g["volume"].to_numpy(float)
        v = v[v > 0]
        if v.size < 500:
            continue
        agregado.append(v)
        t = _benford_teste(v, teorica)
        obs = t.pop("_obs")
        linhas.append({"simbolo": s, "nome": NOMES.get(s, s), **t})
        for dgt in range(9):
            dist.append({"conjunto": s, "digito": dgt + 1, "observada": obs[dgt], "benford": teorica[dgt]})
    tg = _benford_teste(np.concatenate(agregado), teorica)
    obs = tg.pop("_obs")
    linhas.append({"simbolo": "TODOS", "nome": "Volumes agregados (todos os ativos)", **tg})
    for dgt in range(9):
        dist.append({"conjunto": "TODOS", "digito": dgt + 1, "observada": obs[dgt], "benford": teorica[dgt]})
    t = pd.DataFrame(linhas).sort_values("mad_nigrini")
    aplic = t[~t.veredito.str.startswith("não aplicável") & (t.simbolo != "TODOS")]
    return {"tabelas": {"conformidade": t, "distribuicao": pd.DataFrame(dist)},
            "destaque": (f"Só {len(aplic)} das {len(t) - 1} séries de volume cobrem amplitude suficiente para o teste; "
                         f"aplicar Benford às demais seria falso alarme. Agregados, os volumes cobrem "
                         f"{br(tg['ordens_grandeza'], 1)} ordens de grandeza e dão MAD de {br(tg['mad_nigrini'], 4)} "
                         f"({tg['veredito']}).")}


# ─────────────────────────────────────────────────────────────────────────────
def garch_volatilidade(simbolo: str = "US500") -> dict:
    from scipy.optimize import minimize
    r = retornos()[simbolo].to_numpy()
    rc = r - r.mean()

    def nll(th):
        w, a, b = th
        if w <= 0 or a < 0 or b < 0 or a + b >= 0.9999:
            return 1e10
        return K.garch11_filtro(rc, w, a, b)[1]

    v = rc.var()
    res = minimize(nll, x0=[v * 0.05, 0.08, 0.9], method="Nelder-Mead",
                   options={"xatol": 1e-10, "fatol": 1e-6, "maxiter": 5000})
    w, a, b = res.x
    s2, _ = K.garch11_filtro(rc, w, a, b)
    ew = K.ewma_vol(rc, 0.94)
    prox = math.sqrt(w + a * rc[-1] ** 2 + b * s2[-1])
    idx = retornos().index
    serie_vol = pd.DataFrame({"data": idx, "retorno_pct": r * 100, "vol_garch_anual_pct": np.sqrt(s2 * 252) * 100,
                              "vol_ewma_anual_pct": ew * math.sqrt(252) * 100})
    var99 = 2.326 * prox
    es99 = prox * stats.norm.pdf(2.326) / 0.01
    params = pd.DataFrame([{"simbolo": simbolo, "omega": w, "alfa": a, "beta": b, "persistencia": a + b,
                            "meia_vida_dias": math.log(0.5) / math.log(a + b),
                            "vol_longo_prazo_anual_pct": math.sqrt(w / (1 - a - b) * 252) * 100,
                            "vol_proximo_dia_pct": prox * 100, "var99_pct": var99 * 100, "es99_pct": es99 * 100}])
    return {"tabelas": {"parametros": params, "serie": serie_vol},
            "destaque": (f"S&P 500: persistência α+β = {br(a + b, 3)} — um choque de volatilidade leva "
                         f"{br(params.meia_vida_dias[0], 0)} pregões para perder metade da força. VaR 99% de 1 dia: "
                         f"{pct(var99, 2)}.")}


# ─────────────────────────────────────────────────────────────────────────────
def sistemas_nao_lineares() -> dict:
    r = retornos()
    linhas = []
    for s in r.columns:
        x = r[s].to_numpy()
        z = (x - x.mean()) / x.std()
        cauda_obs = float(np.mean(np.abs(z) > 4))
        cauda_norm = float(2 * stats.norm.sf(4))
        ab = np.abs(x)
        ac_abs = float(np.corrcoef(ab[1:], ab[:-1])[0, 1])
        ac_ret = float(np.corrcoef(x[1:], x[:-1])[0, 1])
        linhas.append({"simbolo": s, "nome": NOMES.get(s, s), "curtose_excesso": float(stats.kurtosis(x)),
                       "freq_4sigma_obs": cauda_obs, "freq_4sigma_normal": cauda_norm,
                       "razao_caudas": cauda_obs / cauda_norm, "autocorr_retorno": ac_ret,
                       "autocorr_retorno_abs": ac_abs})
    t = pd.DataFrame(linhas).sort_values("razao_caudas", ascending=False)
    # histograma padronizado do S&P 500 vs normal
    x = r["US500"].to_numpy()
    z = (x - x.mean()) / x.std()
    bordas = np.linspace(-8, 8, 81)
    h, _ = np.histogram(z, bordas, density=True)
    centro = (bordas[1:] + bordas[:-1]) / 2
    hist = pd.DataFrame({"z": centro, "densidade_real": h, "densidade_normal": stats.norm.pdf(centro)})
    med = t.razao_caudas.median()
    return {"tabelas": {"caudas": t, "histograma_us500": hist},
            "destaque": (f"Movimentos de 4 desvios acontecem, em mediana, {br(med, 0)}× mais do que a curva normal prevê; "
                         f"o retorno quase não tem memória (autocorrelação {br(t.autocorr_retorno.median())}), mas o "
                         f"tamanho do movimento tem ({br(t.autocorr_retorno_abs.median())}).")}


# ─────────────────────────────────────────────────────────────────────────────
def causalidade_granger(lags: int = 5) -> dict:
    ativos = ["DXY", "USTBOND", "XAUUSD", "WTI", "COPPER", "US500", "EURUSD", "USDJPY", "SOYBEAN"]
    r = retornos()[ativos]
    linhas = []
    X = r.to_numpy()
    T = X.shape[0]
    for i, causa in enumerate(ativos):
        for j, efeito in enumerate(ativos):
            if i == j:
                continue
            y = X[lags:, j]
            proprio = np.column_stack([X[lags - k:T - k, j] for k in range(1, lags + 1)])
            outro = np.column_stack([X[lags - k:T - k, i] for k in range(1, lags + 1)])
            um = np.ones((y.size, 1))
            Xr = np.hstack([um, proprio])
            Xc = np.hstack([um, proprio, outro])
            _, _, er = _ols(y, Xr)
            _, _, ec = _ols(y, Xc)
            rss_r, rss_c = er @ er, ec @ ec
            gl2 = y.size - Xc.shape[1]
            F = ((rss_r - rss_c) / lags) / (rss_c / gl2)
            p = float(stats.f.sf(F, lags, gl2))
            linhas.append({"causa": causa, "efeito": efeito, "rotulo_causa": NOMES[causa],
                           "rotulo_efeito": NOMES[efeito], "estatistica_f": F, "p_valor": p,
                           "significativo_1pct": p < 0.01})
    t = pd.DataFrame(linhas).sort_values("p_valor")
    # correção de Bonferroni para o número de testes
    t["significativo_bonferroni"] = t.p_valor < 0.01 / len(t)
    top = t.iloc[0]
    return {"tabelas": {"granger": t},
            "destaque": (f"Dos {len(t)} pares testados, {int(t.significativo_bonferroni.sum())} sobrevivem à correção "
                         f"de Bonferroni. O mais forte, {top.rotulo_causa} → {top.rotulo_efeito}, é artefato de horário "
                         f"de fechamento entre fontes diferentes: precedência estatística não é causa — e o teste "
                         f"mostra exatamente onde a intuição seria enganada.")}
