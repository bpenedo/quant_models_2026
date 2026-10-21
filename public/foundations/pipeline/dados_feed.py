# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Camada de dados — séries financeiras do DataFeed Service Provider (DSP).

Fontes, em ordem de preferência (a primeira que existir vence):
  1. $QUANT_MODELS_DATAFEED
  2. /mnt/d/DataFeedServiceProvider          (D:\\DataFeedServiceProvider no Windows)
  3. ~/devparetoprojects/marty-schwartz/datafeedserviceprovider

Formatos lidos:
  · Parquet  `parquet/hf_package_d1/<SIMBOLO>.parquet`  (D1, já validado pelo GATE ZERO)
  · MT4 .hst `<TF>/<SIMBOLO>_<TF>.hst` (build 400: cabeçalho 148 B + registros 60 B)

Política herdada do DSP: UMA fonte por símbolo, NUNCA emendar séries.

Uso:
    python3 dados_feed.py info
    python3 dados_feed.py consolidar [--tf D1|H4|H1]   # grava dados/parquet/ohlcv_<tf>/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PARQUET, ZSTD_NIVEL, paralelizar  # noqa: E402

CANDIDATAS = [
    os.environ.get("QUANT_MODELS_DATAFEED", ""),
    "/mnt/d/DataFeedServiceProvider",
    str(Path.home() / "devparetoprojects/marty-schwartz/datafeedserviceprovider"),
]

# MT4 build 400: time(int64) open high low close (float64) volume(int64) spread(int32) real_volume(int64)
HST_DTYPE = np.dtype([("t", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"), ("c", "<f8"),
                      ("v", "<i8"), ("spread", "<i4"), ("rv", "<i8")])
HST_CABECALHO = 148


def raiz_feed() -> Path:
    for c in CANDIDATAS:
        if c and Path(c).is_dir() and any(Path(c).glob("D1/*.hst")):
            return Path(c)
    raise SystemExit("❌ DataFeed não encontrado. Defina QUANT_MODELS_DATAFEED com o caminho do DSP.")


def simbolos(tf: str = "D1") -> list[str]:
    return sorted(p.name.rsplit("_", 1)[0] for p in (raiz_feed() / tf).glob(f"*_{tf}.hst"))


def ler_hst(caminho: Path) -> dict[str, np.ndarray]:
    """Lê um .hst MT4 build 400 sem dependências além do NumPy (memória contígua)."""
    bruto = np.fromfile(caminho, dtype=np.uint8)
    reg = bruto[HST_CABECALHO:]
    reg = reg[: len(reg) - len(reg) % HST_DTYPE.itemsize].view(HST_DTYPE)
    ordem = np.argsort(reg["t"], kind="stable")
    reg = reg[ordem]
    return {"t": reg["t"].copy(), "open": reg["o"].copy(), "high": reg["h"].copy(),
            "low": reg["l"].copy(), "close": reg["c"].copy(), "volume": reg["v"].astype(np.float64)}


def ler_serie(simbolo: str, tf: str = "D1"):
    """Devolve um pandas.DataFrame indexado por data (UTC) com OHLCV."""
    import pandas as pd
    raiz = raiz_feed()
    pq = raiz / "parquet" / "hf_package_d1" / f"{simbolo}.parquet"
    if tf == "D1" and pq.exists():
        df = pd.read_parquet(pq)
        df = df.set_index("timestamp").sort_index()
        return df[["open", "high", "low", "close", "volume"]]
    d = ler_hst(raiz / tf / f"{simbolo}_{tf}.hst")
    idx = pd.to_datetime(d.pop("t"), unit="s", utc=True)
    return pd.DataFrame(d, index=idx).rename_axis("timestamp")


def painel_fechamento(tf: str = "D1", simbolos_: list[str] | None = None):
    """Matriz data × símbolo de fechamentos (sem preenchimento: NaN onde não houve pregão)."""
    import pandas as pd
    simbolos_ = simbolos_ or simbolos(tf)
    return pd.DataFrame({s: ler_serie(s, tf)["close"] for s in simbolos_}).sort_index()


def _consolidar_um(args: tuple[str, str, str]) -> tuple[str, int]:
    simbolo, tf, destino = args
    import pyarrow as pa
    import pyarrow.parquet as papq
    # O símbolo vive SÓ no caminho da partição (simbolo=X/). Gravá-lo também dentro do
    # arquivo cria duas definições do mesmo campo (string × dictionary) e a leitura do
    # dataset falha ao mesclar esquemas — ver bugs.md BUG-001.
    df = ler_serie(simbolo, tf).reset_index()
    tabela = pa.Table.from_pandas(df, preserve_index=False)
    saida = Path(destino) / f"simbolo={simbolo}"
    saida.mkdir(parents=True, exist_ok=True)
    papq.write_table(tabela, saida / "parte-0.parquet", compression="zstd",
                     compression_level=ZSTD_NIVEL)
    return simbolo, len(df)


def consolidar(tf: str = "D1") -> dict[str, int]:
    destino = PARQUET / f"ohlcv_{tf.lower()}"
    tarefas = [(s, tf, str(destino)) for s in simbolos(tf)
               if tf == "D1" or (raiz_feed() / tf / f"{s}_{tf}.hst").exists()]
    res = dict(paralelizar(tarefas, _consolidar_um))
    (destino / "_manifesto.json").write_text(
        json.dumps({"tf": tf, "fonte": str(raiz_feed()), "barras": res}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"✅ {len(res)} séries {tf} consolidadas em {destino} ({sum(res.values()):,} barras)".replace(",", "."))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Camada de dados do DataFeed Service Provider.")
    ap.add_argument("comando", choices=["info", "consolidar"])
    ap.add_argument("--tf", default="D1")
    a = ap.parse_args()
    if a.comando == "info":
        r = raiz_feed()
        print(f"📂 DataFeed: {r}")
        for tf in ("D1", "H4", "H1", "M30", "M15", "M5"):
            print(f"   {tf:>4}: {len(simbolos(tf)) if (r / tf).exists() else 0} símbolos")
        man = r / "manifesto.json"
        if man.exists():
            m = json.loads(man.read_text(encoding="utf-8"))
            print(f"   manifesto: {len(m.get('series', {}))} séries · política: {m.get('politica')}")
    else:
        consolidar(a.tf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
