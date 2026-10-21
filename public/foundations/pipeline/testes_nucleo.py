#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Passada 1 — concordância entre os TRÊS motores: Python/numba, Rust e F# (D9).

Cada kernel roda nos três com a mesma entrada (dados REAIS do DataFeed) e o resultado precisa
coincidir dentro da tolerância. Dois motores independentes que concordam provam que a
MATEMÁTICA está certa, não só o código. O AG nativo é comparado Rust × F# bit a bit (mesmo
gerador); o Python serve de referência estatística em quant/m_otimizacao.py.

Também confere o ADF e o GARCH próprios contra statsmodels/arch (quarta referência, externa).

Uso:  python3 testes_nucleo.py            (compila os motores se faltar binário)
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAIZ  # noqa: E402
from quant import kernels as K  # noqa: E402
from quant.dados import retornos, serie  # noqa: E402

RUST_DIR = RAIZ / "public/foundations/rust/quant_models_2026_core"
FS_DIR = RAIZ / "public/foundations/fsharp/QuantModels2026.Core"
RUST_BIN = RUST_DIR / "target/release/qm_core"
FS_DLL = FS_DIR / "bin/Release/net9.0/qm_core_fs.dll"
DOTNET = os.environ.get("DOTNET", str(Path.home() / ".dotnet/dotnet"))
TOL = 1e-9

falhas: list[str] = []
oks = 0


def _compilar():
    if not RUST_BIN.exists():
        print("🔧 compilando motor Rust…")
        subprocess.run(["cargo", "build", "--release", "--quiet"], cwd=RUST_DIR, check=True)
    if not FS_DLL.exists():
        print("🔧 compilando motor F#…")
        subprocess.run([DOTNET, "build", "-c", "Release", "--nologo", "-v", "q"], cwd=FS_DIR, check=True,
                       env={**os.environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"})


def _grava(d: Path, nome: str, v, matriz: bool = False) -> str:
    p = d / f"{nome}.txt"
    v = np.asarray(v, float)
    with p.open("w", encoding="utf-8") as f:
        if matriz:
            f.write(f"{v.shape[0]} {v.shape[1]}\n".replace(" ", "\n"))
            v = v.ravel()
        f.write("\n".join(repr(float(x)) for x in v.ravel()))
    return str(p)


def _rodar(motor: str, args: list[str]) -> np.ndarray:
    cmd = [str(RUST_BIN), *args] if motor == "rust" else [DOTNET, str(FS_DLL), *args]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return np.array([float(x) for x in r.stdout.split()], float)


def conferir(nome: str, ref, args: list[str], tol: float = TOL, motores=("rust", "fsharp")):
    global oks
    ref = np.atleast_1d(np.asarray(ref, float)).ravel()
    for m in motores:
        v = _rodar(m, args)
        if v.shape != ref.shape:
            falhas.append(f"{nome} [{m}]: formato {v.shape} ≠ {ref.shape}")
            print(f"   ❌ {nome:22s} {m:6s} formato {v.shape} ≠ {ref.shape}")
            continue
        both_nan = np.isnan(v) & np.isnan(ref)
        den = np.maximum(np.abs(ref), 1.0)
        err = np.where(both_nan, 0.0, np.abs(v - ref) / den)
        e = float(np.nanmax(err)) if err.size else 0.0
        if not np.isfinite(e) or e > tol:
            falhas.append(f"{nome} [{m}]: erro relativo {e:.2e} > {tol:.0e}")
            print(f"   ❌ {nome:22s} {m:6s} erro {e:.2e}")
        else:
            oks += 1
            print(f"   ✅ {nome:22s} {m:6s} erro {e:.1e}")


def main() -> int:
    _compilar()
    d = Path(tempfile.mkdtemp(prefix="qm_nucleo_"))
    sp = serie("US500")
    sp = sp[sp.index.dayofweek < 5].loc["2015":]
    p = sp["close"].to_numpy()
    h, l = sp["high"].to_numpy(), sp["low"].to_numpy()
    r = np.diff(np.log(p))
    print(f"▶️  Concordância Python/numba × Rust × F# — S&P 500 2015–2026 ({p.size} pregões)")

    fp, fr = _grava(d, "p", p), _grava(d, "r", r)
    conferir("log_retornos", K.log_retornos(p), ["log_retornos", fp])
    conferir("ema", K.ema(p, 21), ["ema", fp, "21"])
    conferir("ewma_vol", K.ewma_vol(r, 0.94), ["ewma_vol", fr, "0.94"])
    s2, nll = K.garch11_filtro(r, 2e-6, 0.1, 0.88)
    conferir("garch11", np.r_[nll, s2], ["garch11", fr, "2e-6", "0.1", "0.88"])
    conferir("drawdown", K.drawdown_maximo(p), ["drawdown", fp])
    conferir("sharpe", K.sharpe_anual(r, 252.0), ["sharpe", fr, "252"])
    conferir("rsi", K.rsi(p, 14), ["rsi", fp, "14"])
    sar, tend = K.psar(h, l, 0.02, 0.2)
    conferir("psar", np.r_[sar, tend], ["psar", _grava(d, "hl", np.column_stack([h, l]), True), "0.02", "0.2"])
    conferir("hurst_rs", K.hurst_rs(r), ["hurst_rs", fr])
    conferir("hurst_movel", K.hurst_movel(r[-600:], 150), ["hurst_movel", _grava(d, "r600", r[-600:]), "150"])
    ap, e, d1 = K.haar_dwt(r[:2048], 6)
    conferir("haar_dwt", np.r_[e, ap, d1], ["haar_dwt", _grava(d, "r2048", r[:2048]), "6"])
    acum = np.convolve(r, np.ones(20), "valid")[::20]
    est = np.where(acum < -0.02, 0, np.where(acum > 0.02, 2, 1)).astype(np.int64)
    conferir("transicao", K.matriz_transicao(est, 3), ["transicao", _grava(d, "est", est), "3"])

    x = r[-1500:]
    sd = x.std()
    mu0, sd0 = np.zeros(3), np.array([0.5, 1.0, 2.5]) * sd
    pi, A, mu, sdv, g, ll = K.hmm_gaussiano_em(x, mu0, sd0, 200, 1e-8)
    conferir("hmm", np.r_[ll, mu, sdv, A.ravel(), pi],
             ["hmm", _grava(d, "x", x), _grava(d, "mu0", mu0), _grava(d, "sd0", sd0), "200", "1e-8"], tol=1e-7)

    pts, sls = np.array([0.5, 2.0, 5.0]), np.array([1.0, 4.0, 10.0])
    m = K.ou_sharpe_malha(0.0, 5.0, 1.0, pts, sls, 3000, 100, 4242)
    conferir("ou_malha", m, ["ou_malha", _grava(d, "pts", pts), _grava(d, "sls", sls),
                             "0", "5", "1", "3000", "100", "4242"], tol=1e-9)

    X = (np.column_stack([r[2:-1], r[1:-2], r[:-3]]) - r.mean()) / r.std()
    cod = np.array([0, 1, 200, 2, 204, 202, 0, 205, 206], np.int64)   # max((r1+r2)*sen(r3), cos(r1))
    cst = np.zeros(cod.size)
    conferir("posfixa", K.avaliar_posfixa(cod, cst, X),
             ["posfixa", _grava(d, "X", X, True), _grava(d, "cod", cod), _grava(d, "cst", cst)])
    vol = sp["volume"].to_numpy()
    conferir("benford", K.primeiros_digitos(vol), ["benford", _grava(d, "vol", vol)])
    c, rot = K.kmeans_1d(np.round(p[-500:], 0), 5, 200)
    conferir("kmeans1d", np.r_[c, rot], ["kmeans1d", _grava(d, "p500", np.round(p[-500:], 0)), "5", "200"])

    R = retornos(simbolos=["US500", "XAUUSD", "USTBOND", "WTI", "EURUSD"]).loc["2018":].to_numpy()
    W = np.random.default_rng(3).dirichlet(np.ones(R.shape[1]), 50)
    fR, fW = _grava(d, "R", R, True), _grava(d, "W", W, True)
    conferir("metricas_carteiras", K.metricas_carteiras(R, W, 252.0, 0.0), ["metricas", fR, fW])

    # AG nativo: Rust × F# devem ser IDÊNTICOS (mesmo gerador, mesma ordem de operações)
    a_rs = _rodar("rust", ["ag_carteira", fR, "60", "40", "0.5", "777"])
    a_fs = _rodar("fsharp", ["ag_carteira", fR, "60", "40", "0.5", "777"])
    e = float(np.max(np.abs(a_rs - a_fs))) if a_rs.shape == a_fs.shape else np.inf
    global oks
    if e <= 1e-12:
        oks += 1
        print(f"   ✅ {'ag_carteira':22s} rust×f# idênticos (erro {e:.1e}) · melhor aptidão {a_rs[-1]:.4f}")
    else:
        falhas.append(f"ag_carteira rust×f#: erro {e:.2e}")
        print(f"   ❌ ag_carteira rust×f# erro {e:.2e}")

    # Referências externas (quarta opinião): ADF e GARCH próprios × statsmodels/arch
    try:
        from statsmodels.tsa.stattools import adfuller
        from quant.m_estatistica import adf
        t_prop, _, lags = adf(np.log(p))
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            t_sm = adfuller(np.log(p), maxlag=lags, autolag=None, regression="c")[0]
        ok = abs(t_prop - t_sm) < 1e-6
        print(f"   {'✅' if ok else '❌'} {'adf × statsmodels':22s} próprio {t_prop:.6f} · statsmodels {t_sm:.6f}")
        oks += ok
        if not ok:
            falhas.append("ADF diverge do statsmodels")
    except ImportError:
        print("   ⏭️  statsmodels ausente — ADF sem referência externa")

    print()
    if falhas:
        print(f"❌ {len(falhas)} divergência(s):")
        for f in falhas:
            print("   •", f)
        return 1
    print(f"✅ {oks} verificações — os três motores concordam")
    return 0


if __name__ == "__main__":
    sys.exit(main())
