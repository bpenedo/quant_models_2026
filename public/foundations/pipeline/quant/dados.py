# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Acesso aos dados consolidados (dados/parquet/ohlcv_d1) — uma leitura por processo."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from config import PARQUET

# Classes de ativo do DataFeed (rótulos em PT-BR para as telas)
CLASSES = {
    "EURUSD": "Câmbio", "GBPUSD": "Câmbio", "USDJPY": "Câmbio", "USDCHF": "Câmbio",
    "AUDUSD": "Câmbio", "USDCAD": "Câmbio", "NZDUSD": "Câmbio", "DXY": "Câmbio",
    "XAUUSD": "Metais", "XAGUSD": "Metais", "PLATINUM": "Metais", "PALLADIUM": "Metais", "COPPER": "Metais",
    "WTI": "Energia", "BRENT": "Energia", "NATGAS": "Energia", "DIESEL": "Energia",
    "COCOA": "Agrícolas", "COFFEE": "Agrícolas", "COTTON": "Agrícolas", "OJUICE": "Agrícolas",
    "SOYBEAN": "Agrícolas", "SUGAR": "Agrícolas",
    "US500": "Índices", "US100": "Índices", "US30": "Índices", "US2000": "Índices",
    "BUND": "Juros", "UKGILT": "Juros", "USTBOND": "Juros",
}
NOMES = {
    "EURUSD": "Euro/Dólar", "GBPUSD": "Libra/Dólar", "USDJPY": "Dólar/Iene", "USDCHF": "Dólar/Franco",
    "AUDUSD": "Dólar australiano", "USDCAD": "Dólar/Dólar canadense", "NZDUSD": "Dólar neozelandês",
    "DXY": "Índice do dólar", "XAUUSD": "Ouro", "XAGUSD": "Prata", "PLATINUM": "Platina",
    "PALLADIUM": "Paládio", "COPPER": "Cobre", "WTI": "Petróleo WTI", "BRENT": "Petróleo Brent",
    "NATGAS": "Gás natural", "DIESEL": "Diesel", "COCOA": "Cacau", "COFFEE": "Café", "COTTON": "Algodão",
    "OJUICE": "Suco de laranja", "SOYBEAN": "Soja", "SUGAR": "Açúcar", "US500": "S&P 500",
    "US100": "Nasdaq 100", "US30": "Dow Jones", "US2000": "Russell 2000", "BUND": "Bund alemão",
    "UKGILT": "Gilt britânico", "USTBOND": "Treasury americano",
}


@lru_cache(maxsize=1)
def ohlcv() -> pd.DataFrame:
    """Tabela longa (timestamp, simbolo, open, high, low, close, volume) — já validada pelo DSP."""
    df = pd.read_parquet(PARQUET / "ohlcv_d1")
    df["simbolo"] = df["simbolo"].astype(str)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_localize(None).dt.normalize()
    df = df[df["close"] > 0].sort_values(["simbolo", "timestamp"])
    return df.drop_duplicates(["simbolo", "timestamp"], keep="last")


def serie(simbolo: str) -> pd.DataFrame:
    d = ohlcv()
    return d[d["simbolo"] == simbolo].set_index("timestamp")[["open", "high", "low", "close", "volume"]]


@lru_cache(maxsize=4)
def fechamentos(desde: str = "2010-01-01") -> pd.DataFrame:
    """Matriz data × símbolo, SÓ dias úteis. O câmbio (Dukascopy) tem barra de domingo e
    os demais (Yahoo) não: sem este filtro a cobertura dos não-câmbio cai para ~83% e eles
    somem do universo — ver bugs.md BUG-002."""
    d = ohlcv()
    d = d[d["timestamp"].dt.dayofweek < 5]
    w = d.pivot(index="timestamp", columns="simbolo", values="close").sort_index()
    return w.loc[desde:]


def retornos(desde: str = "2010-01-01", min_cobertura: float = 0.9,
             simbolos: list[str] | None = None) -> pd.DataFrame:
    """Log-retornos diários alinhados.

    Cada ativo tem o retorno calculado no PRÓPRIO calendário (sobre os preços existentes)
    e só depois as séries são alinhadas. Sem forward-fill de preço: ele fabricaria retorno
    zero em feriado e subestimaria a volatilidade."""
    p = fechamentos(desde)
    if simbolos:
        p = p[[s for s in simbolos if s in p.columns]]
    cobertura = p.notna().mean()
    p = p.loc[:, cobertura >= min_cobertura]
    r = pd.concat({c: np.log(p[c].dropna()).diff() for c in p.columns}, axis=1)
    return r.dropna(how="any")


def amostra_ativos() -> list[str]:
    """Universo de demonstração com cobertura longa e classes variadas."""
    return ["US500", "US100", "US30", "XAUUSD", "XAGUSD", "WTI", "BRENT", "COPPER",
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "DXY", "SOYBEAN", "SUGAR", "USTBOND"]
