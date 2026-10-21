#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""PostgreSQL — migrações versionadas e conferência de esquema (D26/R15).

DataGrip (https://www.jetbrains.com/pt-br/datagrip/) é a ferramenta de INSPEÇÃO
e MANUTENÇÃO. Não é canal de deploy: toda mudança de esquema entra aqui, como
migração versionada. Alteração feita só na grade do DataGrip e não versionada é
dívida invisível — e some na primeira restauração de backup.

Credenciais SÓ em `.env` / variável de ambiente `PG_DSN`. Nunca no fonte, nunca
no README.

Uso:
  python3 db_postgres.py migrar        aplica as migrações pendentes, em ordem
  python3 db_postgres.py estado        lista aplicadas e pendentes
  python3 db_postgres.py verificar     esquema esperado × esquema real
  python3 db_postgres.py nova "titulo" cria o próximo arquivo de migração
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

MIGRACOES = Path(__file__).resolve().parent / "migracoes"
TABELA_CONTROLE = "_migracoes"


def _conectar():
    if not config.PG_DSN:
        sys.exit("❌ PG_DSN não definido. Defina-o no .env (nunca no código — D26).")
    try:
        import psycopg
    except ImportError:
        sys.exit("❌ psycopg ausente. Instale: pip install 'psycopg[binary]'")
    return psycopg.connect(config.PG_DSN)


def _arquivos() -> list[Path]:
    return sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql"))


def _aplicadas(cur) -> set[str]:
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABELA_CONTROLE} (
            nome        text PRIMARY KEY,
            aplicada_em timestamptz NOT NULL DEFAULT now()
        )""")
    cur.execute(f"SELECT nome FROM {TABELA_CONTROLE}")
    return {r[0] for r in cur.fetchall()}


def cmd_estado(_a) -> int:
    arqs = _arquivos()
    if not arqs:
        print(f"⚠️  Nenhuma migração em {MIGRACOES}")
        return 0
    with _conectar() as con, con.cursor() as cur:
        ap = _aplicadas(cur)
    print(f"📋 {len(arqs)} migração(ões) · {len(ap)} aplicada(s)")
    for a in arqs:
        print(f"   {'✅' if a.name in ap else '⏳'} {a.name}")
    return 0


def cmd_migrar(_a) -> int:
    arqs = _arquivos()
    with _conectar() as con, con.cursor() as cur:
        ap = _aplicadas(cur)
        pendentes = [a for a in arqs if a.name not in ap]
        if not pendentes:
            print("✅ Nenhuma migração pendente.")
            return 0
        print(f"▶️  Aplicando {len(pendentes)} migração(ões), em ordem:")
        for arq in pendentes:
            sql = arq.read_text(encoding=config.ENCODING)
            print(f"   • {arq.name}")
            # Cada migração é uma TRANSAÇÃO: ou entra inteira, ou não entra.
            cur.execute(sql)
            cur.execute(f"INSERT INTO {TABELA_CONTROLE} (nome) VALUES (%s)", (arq.name,))
            con.commit()
    print("✅ Migrações aplicadas.")
    return 0


def cmd_nova(a) -> int:
    MIGRACOES.mkdir(parents=True, exist_ok=True)
    n = len(_arquivos()) + 1
    slug = re.sub(r"[^a-z0-9]+", "_", a.titulo.lower()).strip("_")[:48]
    arq = MIGRACOES / f"{n:03d}_{slug}.sql"
    arq.write_text(f"""-- {config.NOME}
-- Migração {n:03d} — {a.titulo}
-- Criada em {datetime.now():%d/%m/%Y}
--
-- Regras (D26/R15):
--   • dinheiro em NUMERIC, jamais em float
--   • histórico em livro-razão (INSERT de lançamentos), nunca contador mutável
--   • timestamptz em UTC; apresentação converte para America/Sao_Paulo
--   • índice só depois de EXPLAIN ANALYZE — índice presumido é custo sem ganho

BEGIN;

-- <<< sua DDL aqui >>>

COMMIT;
""", encoding=config.ENCODING)
    print(f"✅ {arq}")
    return 0


def cmd_verificar(_a) -> int:
    """Confere invariantes de esquema que já custaram caro em outros projetos."""
    problemas = []
    with _conectar() as con, con.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name, data_type
              FROM information_schema.columns
             WHERE table_schema = 'public'""")
        colunas = cur.fetchall()
        for tab, col, tipo in colunas:
            if re.search(r"(valor|preco|preço|total|saldo|custo|desconto)", col, re.I) \
               and tipo in ("double precision", "real"):
                problemas.append(f"{tab}.{col}: dinheiro em {tipo} — use NUMERIC")
            if re.search(r"(_em|_at|data|quando)$", col, re.I) \
               and tipo == "timestamp without time zone":
                problemas.append(f"{tab}.{col}: use timestamptz, não timestamp")
        cur.execute("SELECT current_setting('server_encoding')")
        enc = cur.fetchone()[0]
        if enc.upper() != "UTF8":
            problemas.append(f"encoding do servidor é {enc} — deveria ser UTF8")
    if problemas:
        print("❌ Esquema com problemas:")
        for p in problemas:
            print(f"   • {p}")
        return 1
    print("✅ Esquema conforme (dinheiro em NUMERIC, timestamptz, UTF8).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="PostgreSQL — migrações e conferência (D26).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrar").set_defaults(fn=cmd_migrar)
    sub.add_parser("estado").set_defaults(fn=cmd_estado)
    sub.add_parser("verificar").set_defaults(fn=cmd_verificar)
    n = sub.add_parser("nova")
    n.add_argument("titulo")
    n.set_defaults(fn=cmd_nova)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
