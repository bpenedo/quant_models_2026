# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Processamento de sinais e memória longa: Fourier, wavelets de Haar e Hurst móvel."""
from __future__ import annotations

import numpy as np
import pandas as pd

from quant import kernels as K
from quant.dados import NOMES, retornos, serie
from quant.util import br, pct


# ─────────────────────────────────────────────────────────────────────────────
def fourier_ciclos(simbolos=("NATGAS", "SOYBEAN", "US500", "XAUUSD"), n_embaralhamentos: int = 200) -> dict:
    """Periodograma dos retornos. Significância contra o máximo de periodogramas de retornos
    EMBARALHADOS (mesma distribuição, sem estrutura temporal) — ruído também tem picos."""
    rng = np.random.default_rng(42)
    linhas, picos = [], []
    for s in simbolos:
        d = serie(s)
        d = d[d.index.dayofweek < 5].loc["2005":]
        # retorno semanal reduz o ruído diário e evidencia ciclos de semanas/meses/safra
        w = np.log(d["close"]).resample("W-FRI").last().diff().dropna().to_numpy()
        w = w - w.mean()
        n = w.size
        P = np.abs(np.fft.rfft(w)) ** 2 / n
        f = np.fft.rfftfreq(n, d=1.0)
        lim = np.quantile([np.max(np.abs(np.fft.rfft(rng.permutation(w)))[1:] ** 2 / n)
                           for _ in range(n_embaralhamentos)], 0.95)
        validos = (f > 0) & (1 / np.where(f > 0, f, 1) <= 104) & (1 / np.where(f > 0, f, 1) >= 3)
        for fi, pi in zip(f[validos], P[validos]):
            linhas.append({"simbolo": s, "nome": NOMES[s], "periodo_semanas": 1 / fi, "potencia": pi,
                           "limiar_ruido_95": lim})
        ordem = np.argsort(P[validos])[::-1][:3]
        for o in ordem:
            per = 1 / f[validos][o]
            picos.append({"simbolo": s, "nome": NOMES[s], "periodo_semanas": per,
                          "potencia": P[validos][o], "limiar_ruido_95": lim,
                          "significativo": bool(P[validos][o] > lim)})
    t = pd.DataFrame(linhas)
    pk = pd.DataFrame(picos)
    sig = pk[pk.significativo]
    return {"tabelas": {"espectro": t, "picos": pk},
            "destaque": (f"Dos {len(pk)} maiores picos de ciclo nos quatro ativos, só {len(sig)} superam o limiar de "
                         f"ruído de 95% obtido embaralhando os próprios retornos. Todo periodograma tem picos; o teste "
                         f"diz quais são ciclo e quais são acaso.")}


# ─────────────────────────────────────────────────────────────────────────────
def wavelet_haar(simbolo: str = "US500", niveis: int = 6) -> dict:
    d = serie(simbolo)
    d = d[d.index.dayofweek < 5].loc["2006":]
    r = np.log(d["close"]).diff().dropna()
    x = r.to_numpy()
    n2 = 2 ** int(np.floor(np.log2(x.size)))
    x2 = x[-n2:]
    idx = r.index[-n2:]
    _, energia, d1 = K.haar_dwt(x2, niveis)
    total = float((x2 ** 2).sum())
    e = pd.DataFrame({"nivel": np.arange(1, niveis + 1), "escala_pregoes": 2 ** np.arange(1, niveis + 1),
                      "energia": energia, "fracao_energia": energia / total})
    # energia local dos detalhes de nível 1 (janela 20) como indicador de mudança de regime
    loc = pd.Series(d1 ** 2, index=idx).rolling(20).mean()
    z = (loc - loc.rolling(250).mean()) / loc.rolling(250).std()
    preco = d["close"].reindex(idx)
    fut = np.log(preco.shift(-20) / preco)
    sinal = pd.DataFrame({"data": idx, "fechamento": preco.to_numpy(), "energia_detalhe_z": z.to_numpy(),
                          "retorno_futuro_20d_pct": fut.to_numpy() * 100})
    alto = sinal[sinal.energia_detalhe_z > 2].retorno_futuro_20d_pct.dropna()
    base = sinal.retorno_futuro_20d_pct.dropna()
    return {"tabelas": {"energia_niveis": e, "sinal": sinal.dropna(subset=["energia_detalhe_z"])},
            "destaque": (f"O nível 1 (oscilações de 2 pregões) concentra {pct(e.fracao_energia[0])} da energia do "
                         f"S&P 500. Quando a energia de alta frequência explode (z > 2), a dispersão do retorno dos "
                         f"20 pregões seguintes é {br(alto.std() / base.std(), 1)}× a normal: a wavelet localiza no "
                         f"tempo o que Fourier só vê na média.")}


def _quantos(k: int, n: int) -> str:
    return f"nenhum dos {n} ativos" if k == 0 else f"só {k} de {n} ativos"


# ─────────────────────────────────────────────────────────────────────────────
def hurst_movel(simbolos=("US500", "XAUUSD", "EURUSD", "WTI", "USTBOND", "SOYBEAN")) -> dict:
    r = retornos()
    linhas, series_ = [], []
    for s in simbolos:
        x = r[s].to_numpy()
        h_total = K.hurst_rs(x)
        # referência nula: H de R/S tem viés para cima em amostra finita; compara-se contra a mesma
        # série embaralhada (mesma distribuição, sem memória) — ver bugs.md BUG-006
        rng = np.random.default_rng(7)
        h_nulo = np.array([K.hurst_rs(rng.permutation(x)) for _ in range(30)])
        excesso = h_total - h_nulo.mean()
        z_h = excesso / h_nulo.std()
        mh100 = K.hurst_movel(x, 100)
        mh150 = K.hurst_movel(x, 150)
        diff = mh100 - mh150
        # sinal: posição comprada quando MH100 > MH150 (persistência crescente) — comparado à MM100/150
        pos_mh = np.where(diff > 0, 1.0, 0.0)
        p = np.exp(np.cumsum(x))
        mm100 = pd.Series(p).rolling(100).mean().to_numpy()
        mm150 = pd.Series(p).rolling(150).mean().to_numpy()
        pos_mm = np.where(mm100 > mm150, 1.0, 0.0)
        ret_mh = pos_mh[:-1] * x[1:]
        ret_mm = pos_mm[:-1] * x[1:]
        val = ~np.isnan(diff[:-1]) & ~np.isnan(mm150[:-1])
        linhas.append({"simbolo": s, "nome": NOMES[s], "hurst_rs": h_total, "hurst_nulo": float(h_nulo.mean()),
                       "excesso": excesso, "z": z_h,
                       "leitura": "persistente" if z_h > 2 else ("antipersistente" if z_h < -2
                                                                 else "indistinguível de passeio aleatório"),
                       "sharpe_hurst_movel": K.sharpe_anual(ret_mh[val], 252.0),
                       "sharpe_medias_moveis": K.sharpe_anual(ret_mm[val], 252.0),
                       "sharpe_comprado": K.sharpe_anual(x[1:][val], 252.0)})
        series_.append(pd.DataFrame({"simbolo": s, "data": r.index, "mh100": mh100, "mh150": mh150,
                                     "diferenca": diff}).iloc[150::5])
    t = pd.DataFrame(linhas)
    vence = int((t.sharpe_hurst_movel > t.sharpe_medias_moveis).sum())
    return {"tabelas": {"resumo": t, "series": pd.concat(series_, ignore_index=True)},
            "destaque": (f"O H bruto de R/S fica entre {br(t.hurst_rs.min())} e {br(t.hurst_rs.max())} e pareceria "
                         f"'persistente'; contra séries embaralhadas, {_quantos(int((t.leitura == 'persistente').sum()), len(t))} "
                         f"mostra memória real. O cruzamento MH100 − MH150 supera o de médias móveis em "
                         f"{vence} de {len(t)} ativos pelo índice de Sharpe.")}
