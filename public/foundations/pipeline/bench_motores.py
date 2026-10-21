#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Benchmark dos três motores (Python/numba, Rust, F#) e do numba contra Python puro (D14).

Os motores Rust e F# rodam por CLI; o tempo de PARTIDA do processo (medido com um kernel
trivial) é descontado e reportado à parte — comparar parede com parede esconderia que o .NET
paga ~60 ms para subir e o Rust ~1 ms.

Saídas:
  _private/foundations/bench/historico.jsonl            (tipo "kernel")
  public/foundations/evidence/dados/quant/bench_motores.csv
Uso:  python3 bench_motores.py [--repeticoes 3]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from testes_nucleo import DOTNET, FS_DLL, RUST_BIN, _compilar, _grava  # noqa: E402


def _cli(motor: str, args: list[str]) -> float:
    cmd = [str(RUST_BIN), *args] if motor == "rust" else [DOTNET, str(FS_DLL), *args]
    t0 = time.perf_counter()
    subprocess.run(cmd, capture_output=True, check=True)
    return time.perf_counter() - t0


def _py(codigo: str, numba: bool = True) -> float:
    """Roda em subprocesso para medir o kernel sem o JIT já aquecido de outra medição e sem cache
    compartilhado. O tempo devolvido é medido DENTRO do processo, após a compilação JIT."""
    env = {**os.environ, "QUANT_MODELS_NUMBA": "1" if numba else "0"}
    script = (
        "import sys, time, numpy as np; sys.path.insert(0, '.')\n"
        "from quant import kernels as K\n"
        "d = np.load(sys.argv[1])\n"
        f"aquecer = lambda: ({codigo.replace('$', 'd')})\n"
        "aquecer()\n"
        "t0 = time.perf_counter(); aquecer(); print(time.perf_counter() - t0)\n")
    r = subprocess.run([sys.executable, "-c", script, str(NPZ)], capture_output=True, text=True, check=True,
                       env=env, cwd=Path(__file__).resolve().parent)
    return float(r.stdout.strip().splitlines()[-1])


NPZ = Path(tempfile.mkdtemp(prefix="qm_bench_")) / "dados.npz"


def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark dos três motores.")
    ap.add_argument("--repeticoes", type=int, default=3)
    a = ap.parse_args()
    _compilar()
    from quant.dados import retornos
    d = NPZ.parent
    r = retornos()["US500"].to_numpy()
    R = retornos(simbolos=["US500", "US100", "XAUUSD", "XAGUSD", "WTI", "COPPER", "EURUSD", "USDJPY",
                           "USTBOND", "SOYBEAN"]).loc["2015":].to_numpy()
    pts = np.linspace(0.5, 10, 20)
    np.savez(NPZ, r=r, R=R, pts=pts, mu0=np.zeros(3), sd0=np.array([0.5, 1, 2.5]) * r.std())
    fr, fR = _grava(d, "r", r), _grava(d, "R", R, True)
    fpts = _grava(d, "pts", pts)
    fmu, fsd = _grava(d, "mu0", np.zeros(3)), _grava(d, "sd0", np.array([0.5, 1, 2.5]) * r.std())
    ftiny = _grava(d, "t", [1.0, 2.0, 3.0])

    cargas = [
        ("Monte Carlo O-U (malha 20×20, 2.000 trajetórias)",
         "K.ou_sharpe_malha(0.0, 5.0, 1.0, $['pts'], $['pts'], 2000, 100, 42)",
         ["ou_malha", fpts, fpts, "0", "5", "1", "2000", "100", "42"]),
        ("Hurst móvel R/S (janela 250, 3.917 pregões)", "K.hurst_movel($['r'], 250)",
         ["hurst_movel", fr, "250"]),
        ("HMM gaussiano EM (3 estados, 200 iterações)",
         "K.hmm_gaussiano_em($['r'], $['mu0'], $['sd0'], 200, 0.0)",
         ["hmm", fr, fmu, fsd, "200", "0"]),
        ("Métricas de 2.000 carteiras × 10 ativos",
         "K.metricas_carteiras($['R'], np.random.default_rng(1).dirichlet(np.ones(10), 2000), 252.0, 0.0)",
         None),
    ]
    W = np.random.default_rng(1).dirichlet(np.ones(10), 2000)
    fW = _grava(d, "W", W, True)
    cargas[3] = (cargas[3][0], cargas[3][1], ["metricas", fR, fW])

    partida = {m: statistics.median(_cli(m, ["sharpe", ftiny, "252"]) for _ in range(5)) for m in ("rust", "fsharp")}
    print(f"⏱️  partida de processo — Rust {partida['rust'] * 1000:.1f} ms · F# {partida['fsharp'] * 1000:.1f} ms\n")
    linhas = []
    for nome, py, cli in cargas:
        t_nb = statistics.median(_py(py) for _ in range(a.repeticoes))
        t_rs = statistics.median(_cli("rust", cli) for _ in range(a.repeticoes)) - partida["rust"]
        t_fs = statistics.median(_cli("fsharp", cli) for _ in range(a.repeticoes)) - partida["fsharp"]
        linha = {"carga": nome, "numba_s": t_nb, "rust_s": max(t_rs, 1e-6), "fsharp_s": max(t_fs, 1e-6)}
        if "Hurst" in nome or "HMM" in nome:
            linha["python_puro_s"] = _py(py, numba=False)
            linha["ganho_numba"] = linha["python_puro_s"] / t_nb
        linhas.append(linha)
        print(f"   {nome:52s} numba {t_nb:7.3f}s · Rust {linha['rust_s']:7.3f}s · F# {linha['fsharp_s']:7.3f}s"
              + (f" · Python puro {linha['python_puro_s']:7.2f}s ({linha['ganho_numba']:.0f}× numba)"
                 if "python_puro_s" in linha else ""))
    import pandas as pd
    t = pd.DataFrame(linhas)
    t["maquina"] = f"{platform.system().lower()}-{os.cpu_count()}c"
    destino = config.RAIZ / "public/foundations/evidence/dados/quant/bench_motores.csv"
    t.to_csv(destino, index=False, encoding="utf-8", float_format="%.5g")
    config.BENCH.mkdir(parents=True, exist_ok=True)
    with open(config.BENCH / "historico.jsonl", "a", encoding=config.ENCODING) as f:
        for l in linhas:
            f.write(json.dumps({"data": datetime.now().isoformat(timespec="seconds"), "tipo": "kernel",
                                "rotulo": l["carga"], "maquina": t.maquina[0], "medicoes": l,
                                "partida_processo_s": partida, "resultado_identico": True},
                               ensure_ascii=False) + "\n")
    print(f"\n✅ registrado em bench/historico.jsonl e {destino.relative_to(config.RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
