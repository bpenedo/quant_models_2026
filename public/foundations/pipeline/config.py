# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Configuração central do projeto — lida de `projeto.toml` (fonte única de verdade).

Toda leitura/escrita de texto do projeto usa `ENCODING` daqui, explicitamente (R11).
`Path.read_text()` sem `encoding=` usa o locale da máquina e destrói acentuação —
falha que só aparece na máquina do outro, e sempre em produção.
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path


def _raiz() -> Path:
    p = Path(__file__).resolve()
    for pai in [p, *p.parents]:
        if (pai / "projeto.toml").exists():
            return pai
    raise SystemExit("❌ projeto.toml não encontrado.")


RAIZ = _raiz()
CFG = tomllib.loads((RAIZ / "projeto.toml").read_text(encoding="utf-8"))

NOME = CFG["projeto"]["nome"]
SLUG = CFG["projeto"]["slug"]
TITULO = CFG["projeto"]["titulo"]
PREFIXO_ENV = "QUANT_MODELS"


def _env(sufixo: str, padrao):
    return os.environ.get(f"{PREFIXO_ENV}_{sufixo}", padrao)


# ── R11 — encoding explícito, sempre ─────────────────────────────────────────
ENCODING = _env("ENCODING", CFG["execucao"]["encoding"])
IDIOMA_SAIDA = CFG["execucao"]["idioma_saida"]            # R1 — pt-BR

# ── R2 — paralelismo ─────────────────────────────────────────────────────────
WORKERS = int(_env("WORKERS", "0")) or (os.cpu_count() or 4)
LIMIAR_TRABALHO = int(_env("LIMIAR_TRABALHO", "1500000"))
BLOCOS_LOGICOS = int(_env("BLOCOS", "64"))    # FIXO: partição não depende do nº de processos

# ── R7 / R6 — JIT e Cython ───────────────────────────────────────────────────
USAR_NUMBA = _env("NUMBA", "1") != "0"
USAR_CYTHON = _env("CYTHON", "1") != "0"

# ── Reprodutibilidade ────────────────────────────────────────────────────────
SEED = int(_env("SEED", "42"))

# ── R14 — acervo local (DataFusion + Parquet) ────────────────────────────────
ACERVO = Path(_env("ACERVO", RAIZ / "_private/kb"))
PARQUET = Path(_env("PARQUET", RAIZ / "dados/parquet"))
OCR_MODO = _env("OCR", "auto")               # auto | sempre | nunca
ZSTD_NIVEL = int(_env("ZSTD_NIVEL", "3"))

# ── R15 — PostgreSQL (só via .env; NUNCA no fonte) ───────────────────────────
PG_DSN = os.environ.get("PG_DSN", "")

# ── D14 — orçamento de performance ───────────────────────────────────────────
ORCAMENTO_S = float(CFG["performance"]["orcamento_segundos"])
TOLERANCIA = float(CFG["performance"]["tolerancia_regressao"])

# ── Caminhos ─────────────────────────────────────────────────────────────────
PRIVADO = RAIZ / "_private"
FOUNDATIONS = PRIVADO / "foundations"
BENCH = FOUNDATIONS / "bench"
TELAS_PRIVADAS = FOUNDATIONS / "telas"
DOCS = RAIZ / "docs"
TELAS_PUBLICAS = DOCS / "telas"
LOGS = RAIZ / "logs"


def ler(caminho: Path) -> str:
    """Leitura SEMPRE com encoding explícito (R11)."""
    return Path(caminho).read_text(encoding=ENCODING)


def escrever(caminho: Path, texto: str) -> None:
    """Escrita ATÔMICA e com encoding explícito: arquivo meio escrito é pior que ausente."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(texto, encoding=ENCODING)
    tmp.replace(caminho)


def njit(*args, **kwargs):
    """`@njit` com degradação graciosa (R7): sem numba, roda NumPy puro.

    Mesma resposta, mais devagar — e com AVISO. Degradação silenciosa é falha
    silenciosa.
    """
    def decorador(fn):
        if not USAR_NUMBA:
            return fn
        try:
            from numba import njit as _njit
        except ImportError:
            if not getattr(njit, "_avisou", False):
                print("  ⚠️  numba ausente — kernels rodando em NumPy puro "
                      "(mesmo resultado, mais lento).")
                njit._avisou = True
            return fn
        return _njit(*args, **kwargs)(fn)
    if args and callable(args[0]) and not kwargs:
        fn, args = args[0], ()
        return decorador(fn)
    return decorador


# ─────────────────────────────────────────────────────────────────────────────
# R2 / D8 — paralelismo com ProcessPoolExecutor
# ─────────────────────────────────────────────────────────────────────────────
def paralelizar(tarefas, funcao, *, initializer=None, initargs=(), trabalho=None):
    """Executa `funcao` sobre `tarefas` com ProcessPoolExecutor (R2/D8).

    Nunca `threading` para CPU-bound: o GIL serializa e a complexidade é paga
    sem ganho nenhum.

    Três regras que vieram de defeitos reais:

    1. `funcao` tem de ser **pura** — recebe e devolve arrays e primitivos.
       Conexão de banco e closure não são serializáveis, e o erro só aparece
       sob carga.
    2. **Só paralelize quando o trabalho justifica.** `trabalho` é a estimativa
       de custo total; abaixo de `LIMIAR_TRABALHO` roda serial, porque 10.000
       tarefas triviais custam mais em serialização do que em CPU.
    3. A **partição é fixa** (`BLOCOS_LOGICOS`), independente do número de
       processos — senão o resultado muda com a máquina e a reprodutibilidade
       vira loteria.
    """
    from concurrent.futures import ProcessPoolExecutor

    tarefas = list(tarefas)
    if trabalho is not None and trabalho < LIMIAR_TRABALHO:
        return [funcao(t) for t in tarefas]          # regra 2
    if len(tarefas) <= 1 or WORKERS <= 1:
        return [funcao(t) for t in tarefas]
    with ProcessPoolExecutor(max_workers=WORKERS,
                             initializer=initializer,
                             initargs=initargs) as executor:
        return list(executor.map(funcao, tarefas))


def particionar(itens, blocos: int = BLOCOS_LOGICOS):
    """Divide em nº FIXO de blocos lógicos — nunca em função de `max_workers`.

    Se a partição acompanha o número de processos, o resultado passa a depender
    da máquina: mesma semente, respostas diferentes em 4 e em 8 núcleos.
    """
    itens = list(itens)
    n = min(blocos, len(itens)) or 1
    tamanho = -(-len(itens) // n)
    return [itens[i:i + tamanho] for i in range(0, len(itens), tamanho)]
