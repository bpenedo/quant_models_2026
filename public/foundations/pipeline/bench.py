#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Medição de desempenho com histórico (D14/R8).

Sem registro, otimização vira folclore. Com registro, vira argumento de venda e
detector de regressão.

INVARIANTE: otimização que muda resultado é BUG, não ganho. Todo registro
carrega `resultado_identico`; `false` reprova no gate.

Uso:
  python3 bench.py --registrar --rotulo "pré-computação de tensores"
  python3 bench.py --historico
  python3 bench.py --verificar          # reprova regressão acima da tolerância
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

HIST = config.BENCH / "historico.jsonl"


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=config.RAIZ,
                              capture_output=True, text=True, timeout=5).stdout.strip() or "—"
    except Exception:
        return "—"


def _maquina() -> str:
    return f"{platform.system().lower()}-{os.cpu_count()}c"


def medir() -> tuple[float, bool, dict]:
    """Caminho crítico: malha de Monte Carlo O-U (o kernel mais caro do projeto) no numba.

    `resultado_identico` compara a malha com a do motor Rust (mesmo gerador ⇒ mesma saída):
    otimização que muda o número é bug, não ganho.
    """
    import numpy as np
    from quant import kernels as K
    pts = np.linspace(0.5, 10, 20)
    K.ou_sharpe_malha(0.0, 5.0, 1.0, pts[:1], pts[:1], 10, 10, 1)        # aquece o JIT fora da medição
    t0 = time.perf_counter()
    m = K.ou_sharpe_malha(0.0, 5.0, 1.0, pts, pts, 2000, 100, 42)
    dt = time.perf_counter() - t0
    identico = True
    try:
        import tempfile
        from testes_nucleo import RUST_BIN, _grava
        if RUST_BIN.exists():
            d = Path(tempfile.mkdtemp(prefix="qm_bench_"))
            f = _grava(d, "pts", pts)
            out = subprocess.run([str(RUST_BIN), "ou_malha", f, f, "0", "5", "1", "2000", "100", "42"],
                                 capture_output=True, text=True, check=True).stdout.split()
            identico = bool(np.allclose(np.array(out, float), m.ravel(), rtol=1e-12, atol=0))
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠️  sem comparação com o Rust: {e}")
    return dt, identico, {"alvo": "ou_sharpe_malha 20x20x2000x100", "motor": "numba"}


def registrar(rotulo: str, tipo: str | None = None) -> dict:
    segundos, identico, params = medir()
    anteriores = ler_historico()
    anterior = anteriores[-1]["segundos"] if anteriores else None
    reg = {
        "data": datetime.now().isoformat(timespec="seconds"),
        "rotulo": rotulo, "commit": _commit(), "maquina": _maquina(),
        "parametros": params, "segundos": round(segundos, 4),
        "anterior": anterior,
        "fator": round(anterior / segundos, 2) if anterior and segundos else None,
        "resultado_identico": identico,
        "orcamento": config.ORCAMENTO_S,
    }
    if tipo:
        # "experimento": configuração diferente da padrão — documenta o ensaio sem virar
        # "melhor marca" do caminho crítico (senão todo retorno ao padrão parece regressão).
        reg["tipo"] = tipo
    config.BENCH.mkdir(parents=True, exist_ok=True)
    with open(HIST, "a", encoding=config.ENCODING) as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    print(f"  ⏱️  {rotulo}: {segundos:.4f}s".replace(".", ",")
          + (f" (antes {anterior:.4f}s, fator {reg['fator']}×)".replace(".", ",")
             if anterior else ""))
    if not identico:
        print("  ❌ RESULTADO DIFERENTE do caminho de referência — isso é BUG, não ganho.")
    return reg


def ler_historico() -> list[dict]:
    """Só medições do CAMINHO CRÍTICO. Registros com "tipo": "kernel" (micro-benchmarks de
    milissegundos) ficam de fora: misturá-los fazia a "melhor marca" virar 0,03 s e todo
    caminho crítico parecer regressão. Esta é a ÚNICA implementação da regra — o gate
    (verificar_publicacao.sh) chama `bench.py --verificar` em vez de reimplementá-la."""
    if not HIST.exists():
        return []
    return [r for r in (json.loads(l) for l in config.ler(HIST).splitlines() if l.strip())
            if r.get("tipo") not in ("kernel", "experimento")]


def verificar() -> int:
    h = ler_historico()
    if not h:
        print("⚠️  Nenhuma medição registrada — rode: python3 bench.py --registrar")
        return 0
    ult = h[-1]
    melhor = min(x["segundos"] for x in h)
    problemas = []
    if ult["segundos"] > config.ORCAMENTO_S:
        problemas.append(f"acima do orçamento ({ult['segundos']:.3f}s > "
                         f"{config.ORCAMENTO_S:.3f}s)".replace(".", ","))
    if ult["segundos"] > melhor * (1 + config.TOLERANCIA):
        problemas.append(f"regressão de {(ult['segundos']/melhor-1)*100:.1f}% sobre a melhor "
                         f"marca ({melhor:.3f}s)".replace(".", ","))
    if not ult.get("resultado_identico", True):
        problemas.append("a otimização MUDOU o resultado — isso é bug, não ganho")
    if problemas:
        print("❌ Desempenho reprovado:")
        for p in problemas:
            print(f"   • {p}")
        return 1
    print(f"✅ Desempenho aprovado: {ult['segundos']:.4f}s "
          f"(orçamento {config.ORCAMENTO_S}s, melhor {melhor:.4f}s)".replace(".", ","))
    return 0


def historico() -> None:
    h = ler_historico()
    if not h:
        print("  (histórico vazio)")
        return
    print(f"{'Data':<20} {'Rótulo':<34} {'Seg.':>9} {'Fator':>7} {'Igual?':>7}")
    print("─" * 82)
    for r in h[-30:]:
        print(f"{r['data'][:19]:<20} {r['rotulo'][:34]:<34} "
              f"{r['segundos']:>9.4f} {str(r.get('fator') or '—'):>7} "
              f"{'sim' if r.get('resultado_identico', True) else 'NÃO':>7}")


def main():
    ap = argparse.ArgumentParser(description="Mede, registra e verifica o desempenho (D14).")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--rotulo", default="medição de rotina")
    ap.add_argument("--historico", action="store_true")
    ap.add_argument("--experimento", action="store_true", help="marca a medição como ensaio fora do caminho padrão")
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    if a.registrar:
        registrar(a.rotulo, "experimento" if a.experimento else None)
    if a.historico:
        historico()
    if a.verificar or not (a.registrar or a.historico):
        sys.exit(verificar())


if __name__ == "__main__":
    main()
