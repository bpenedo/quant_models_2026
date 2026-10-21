#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Executa os modelos da fase 1 do catálogo em paralelo e exporta as tabelas para o site.

Cada modelo é uma tarefa PURA (id → resultado) enviada ao ProcessPoolExecutor (D8).
A ordem das tarefas é fixa (a do catálogo) e cada modelo usa semente própria: o resultado
não depende do número de processos.

Uso:
    python3 executar_modelos.py                  # todos
    python3 executar_modelos.py --so hmm_regimes,ag_carteira
    python3 executar_modelos.py --sem-registro   # sem os 4 logs (testes)
Saída:
    public/foundations/evidence/dados/quant/<id>__<tabela>.csv
    public/foundations/evidence/dados/quant/resumo_modelos.csv
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_modelos import MODELOS  # noqa: E402
from config import RAIZ, WORKERS  # noqa: E402

SAIDA = RAIZ / "public/foundations/evidence/dados/quant"
MODULOS = ["quant.m_estatistica", "quant.m_ml", "quant.m_probabilistico", "quant.m_sinais",
           "quant.m_otimizacao", "quant.m_governanca"]


def _localizar(mid: str):
    for nome in MODULOS:
        m = importlib.import_module(nome)
        if hasattr(m, mid):
            return getattr(m, mid)
    raise KeyError(f"modelo '{mid}' do catálogo não tem implementação")


def _rodar(mid: str) -> dict:
    """Função pura enviada ao pool: roda um modelo e grava os CSVs dele."""
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    t0 = time.perf_counter()
    out = _localizar(mid)()
    arquivos = []
    for tabela, df in out["tabelas"].items():
        destino = SAIDA / f"{mid}__{tabela}.csv"
        df.to_csv(destino, index=False, encoding="utf-8", float_format="%.6g")
        arquivos.append(destino.name)
    return {"id": mid, "segundos": time.perf_counter() - t0, "destaque": out["destaque"], "arquivos": arquivos,
            "linhas": int(sum(len(df) for df in out["tabelas"].values()))}


def _aquecer_jit() -> None:
    """Compila os kernels numba UMA vez antes do pool: sem isto, 4 processos compilam o mesmo
    código ao mesmo tempo e disputam o cache em disco."""
    import numpy as np
    from quant import kernels as K
    x = np.random.default_rng(0).normal(0, 0.01, 512)
    p = np.exp(np.cumsum(x))
    K.log_retornos(p); K.ema(p, 5); K.ewma_vol(x, 0.94); K.garch11_filtro(x, 1e-6, 0.05, 0.9)
    K.drawdown_maximo(p); K.sharpe_anual(x, 252.0); K.rsi(p, 14); K.psar(p * 1.01, p * 0.99, 0.02, 0.2)
    K.hurst_rs(x); K.hurst_movel(x[:200], 100); K.haar_dwt(x, 3); K.matriz_transicao(np.zeros(5, np.int64), 3)
    K.hmm_gaussiano_em(x, np.zeros(3), np.array([.005, .01, .02]), 2, 1e-6)
    K.ou_sharpe_malha(0.0, 5.0, 1.0, np.array([1.0]), np.array([1.0]), 10, 10, 1)
    K.avaliar_posfixa(np.array([0, 0, 200], np.int64), np.zeros(3), x.reshape(-1, 1))
    K.primeiros_digitos(p); K.kmeans_1d(x, 2, 5); K.metricas_carteiras(x.reshape(-1, 2), np.ones((1, 2)) / 2, 252.0, 0.0)


def main() -> int:
    ap = argparse.ArgumentParser(description="Executa os modelos quantitativos e exporta para o site.")
    ap.add_argument("--so", default="", help="ids separados por vírgula")
    ap.add_argument("--sem-registro", action="store_true")
    a = ap.parse_args()
    ids = [m["id"] for m in MODELOS if m["fase"] == 1]
    if a.so:
        pedidos = [x.strip() for x in a.so.split(",") if x.strip()]
        desconhecidos = set(pedidos) - set(ids)
        if desconhecidos:
            print(f"❌ ids desconhecidos ou de fase 2: {', '.join(sorted(desconhecidos))}")
            return 1
        ids = pedidos
    SAIDA.mkdir(parents=True, exist_ok=True)
    print(f"▶️  {len(ids)} modelos · {WORKERS} processos · saída em {SAIDA.relative_to(RAIZ)}")
    t0 = time.perf_counter()
    _aquecer_jit()
    print(f"   kernels numba prontos em {time.perf_counter() - t0:.1f}s")
    resultados, falhas = {}, {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futuros = {ex.submit(_rodar, mid): mid for mid in ids}
        for f in as_completed(futuros):
            mid = futuros[f]
            try:
                r = f.result()
                resultados[mid] = r
                print(f"   ✅ {mid:24s} {r['segundos']:6.1f}s  {r['linhas']:>7,} linhas".replace(",", "."))
            except Exception as e:  # noqa: BLE001 — falha de um modelo não derruba os outros, mas reprova no fim
                falhas[mid] = f"{type(e).__name__}: {e}"
                print(f"   ❌ {mid}: {falhas[mid]}")
    import pandas as pd
    nomes = {m["id"]: m for m in MODELOS}
    resumo = pd.DataFrame([{"numero": [m["id"] for m in MODELOS].index(mid) + 1, "id": mid,
                            "nome": nomes[mid]["nome"], "tipo": nomes[mid]["tipo"],
                            "categoria": nomes[mid]["categoria"], "segundos": r["segundos"],
                            "linhas": r["linhas"], "destaque": r["destaque"]}
                           for mid, r in resultados.items()]).sort_values("numero")
    if not a.so:
        resumo.to_csv(SAIDA / "resumo_modelos.csv", index=False, encoding="utf-8", float_format="%.4g")
        (SAIDA.parent.parent / "static").mkdir(parents=True, exist_ok=True)
    total = time.perf_counter() - t0
    soma = float(resumo.segundos.sum()) if len(resumo) else 0.0
    print(f"\n⏱️  parede {total:.1f}s · soma dos modelos {soma:.1f}s · aceleração {soma / max(total, 1e-9):.2f}×")
    (RAIZ / "logs").mkdir(exist_ok=True)
    (RAIZ / "logs" / "ultima_execucao_modelos.json").write_text(
        json.dumps({"parede_s": total, "soma_s": soma, "workers": WORKERS, "ok": list(resultados), "falhas": falhas},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    if falhas:
        print(f"❌ {len(falhas)} modelo(s) falharam: {', '.join(falhas)}")
        return 1
    print(f"✅ {len(resultados)} modelos concluídos")
    return 0


if __name__ == "__main__":
    if "--sem-registro" not in sys.argv:
        from registro4logs import sob_registro
        sob_registro("modelos-quant", RAIZ / "logs" / "criacao", fase="pipeline", nome="executar modelos")
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    sys.exit(main())
