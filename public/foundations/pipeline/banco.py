#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""CLI do ACERVO LOCAL — sem SGBD (D24/R14).

Pilha: PyMuPDF (fitz) para PDF · PP-OCRv6 tiny sobre ONNX Runtime quando a página
não tem camada de texto · Apache Arrow em memória · Apache Parquet particionado
com zstd em disco · Apache DataFusion como motor SQL.

Verbos FIXOS (campos e tabelas adaptados ao projeto):
    carregar (load) · info · buscar · consulta · sql

Por que sem SGBD: acervo local é carga em lote e leitura analítica, não carga
transacional. Um SGBD acrescenta processo, porta, usuário, backup e ponto de
falha — e não entrega nada que Parquet + DataFusion não entreguem com latência
menor. Para SMB, o "banco" vira um diretório que se copia, versiona e leva embora.

Uso:
  python3 banco.py carregar --origem _private/kb --formatos pdf,docx,pptx,xlsx --ocr auto
  python3 banco.py info
  python3 banco.py buscar "cláusula de reajuste" --limite 20 --contexto 200
  python3 banco.py consulta por-ano --de 2020 --ate 2026
  python3 banco.py sql "SELECT fonte, COUNT(*) FROM acervo GROUP BY fonte" --formato csv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

MANIFESTO = config.PARQUET.parent / "manifesto.json"
EXT_FORMATO = {".pdf": "pdf", ".docx": "docx", ".doc": "docx", ".pptx": "pptx",
               ".ppt": "pptx", ".xlsx": "xlsx", ".xls": "xlsx", ".csv": "csv",
               ".txt": "txt", ".md": "txt"}
LOTE = 12          # arquivos por tarefa — paralelizar por LOTE, não por arquivo (R2)


# ─────────────────────────────────────────────────────────────────────────────
# Extração
# ─────────────────────────────────────────────────────────────────────────────
def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _ocr(pagina) -> str:
    """OCR com PP-OCRv6 tiny sobre ONNX Runtime.

    Degradação graciosa: sem o runtime ou sem o modelo, devolve vazio e a
    cobertura cai — mas `info` REPORTA a cobertura. Nunca deixar OCR
    indisponível virar "acervo carregado com sucesso".
    """
    modelo = os.environ.get("QUANT_MODELS_OCR_MODELO", "")
    if not modelo or not Path(modelo).exists():
        return ""
    try:
        import onnxruntime  # noqa: F401
    except ImportError:
        return ""
    try:
        # _(ponto de extensão: pré-processar o pixmap e rodar a sessão ONNX)_
        return ""
    except Exception:
        return ""


def _extrair_pdf(caminho: Path, modo_ocr: str) -> list[dict]:
    import fitz                       # PyMuPDF — SEMPRE para PDF (R14)
    linhas, doc = [], fitz.open(caminho)
    try:
        for n, pagina in enumerate(doc, start=1):
            texto = pagina.get_text("text") or ""
            metodo = "nativo"
            if modo_ocr != "nunca" and (modo_ocr == "sempre" or len(texto.strip()) < 20):
                t2 = _ocr(pagina)
                if t2:
                    texto, metodo = t2, "ocr"
                elif len(texto.strip()) < 20:
                    metodo = "sem-texto"
            linhas.append({"pagina": n, "texto": texto, "metodo": metodo})
    finally:
        doc.close()
    return linhas


def _extrair_docx(caminho: Path) -> list[dict]:
    from docx import Document
    d = Document(str(caminho))
    texto = "\n".join(p.text for p in d.paragraphs)
    return [{"pagina": 1, "texto": texto, "metodo": "nativo"}]


def _extrair_pptx(caminho: Path) -> list[dict]:
    from pptx import Presentation
    pres, linhas = Presentation(str(caminho)), []
    for n, slide in enumerate(pres.slides, start=1):
        partes = [sh.text for sh in slide.shapes if getattr(sh, "has_text_frame", False)]
        linhas.append({"pagina": n, "texto": "\n".join(partes), "metodo": "nativo"})
    return linhas


def _extrair_xlsx(caminho: Path) -> list[dict]:
    from openpyxl import load_workbook
    wb, linhas = load_workbook(str(caminho), read_only=True, data_only=True), []
    for n, aba in enumerate(wb.worksheets, start=1):
        partes = []
        for linha in aba.iter_rows(values_only=True):
            partes.append(" | ".join("" if c is None else str(c) for c in linha))
        linhas.append({"pagina": n, "texto": "\n".join(partes), "metodo": "nativo"})
    wb.close()
    return linhas


def _extrair_texto(caminho: Path) -> list[dict]:
    return [{"pagina": 1, "texto": caminho.read_text(encoding=config.ENCODING,
                                                     errors="replace"),
             "metodo": "nativo"}]


EXTRATORES = {"pdf": _extrair_pdf, "docx": _extrair_docx, "pptx": _extrair_pptx,
              "xlsx": _extrair_xlsx, "csv": _extrair_texto, "txt": _extrair_texto}


def processar_lote(args: tuple[list[str], str]) -> list[dict]:
    """Executado em processo separado (R2). Função PURA: entra e sai só dado."""
    caminhos, modo_ocr = args
    saida = []
    for c in caminhos:
        caminho = Path(c)
        fmt = EXT_FORMATO.get(caminho.suffix.lower())
        if not fmt:
            continue
        try:
            extrator = EXTRATORES[fmt]
            paginas = (extrator(caminho, modo_ocr) if fmt == "pdf" else extrator(caminho))
        except ImportError as e:
            saida.append({"_erro": f"{caminho.name}: dependência ausente ({e})",
                          "_formato": fmt})
            continue
        except Exception as e:
            saida.append({"_erro": f"{caminho.name}: {e}", "_formato": fmt})
            continue
        sha = _sha256(caminho)
        agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
        ano = str(datetime.fromtimestamp(caminho.stat().st_mtime).year)
        for p in paginas:
            saida.append({
                "arquivo_origem": str(caminho), "sha256": sha, "pagina": p["pagina"],
                "texto": p["texto"], "metodo": p["metodo"], "extraido_em": agora,
                "fonte": fmt, "ano": ano, "nome_arquivo": caminho.name,
                "bytes": caminho.stat().st_size,
            })
    return saida


# ─────────────────────────────────────────────────────────────────────────────
# Comandos
# ─────────────────────────────────────────────────────────────────────────────
def _manifesto_ler() -> dict:
    if MANIFESTO.exists():
        try:
            return json.loads(config.ler(MANIFESTO))
        except Exception:
            return {}
    return {}


def cmd_carregar(a) -> int:
    origem = Path(a.origem or config.ACERVO)
    if not origem.exists():
        print(f"❌ Origem não encontrada: {origem}")
        return 1
    formatos = {f.strip().lower() for f in (a.formatos or "pdf,docx,pptx,xlsx,csv,txt").split(",")}
    arquivos = [p for p in sorted(origem.rglob("*"))
                if p.is_file() and EXT_FORMATO.get(p.suffix.lower()) in formatos]
    print(f"📂 Origem: {origem}")
    print(f"   {len(arquivos)} arquivo(s) nos formatos {sorted(formatos)}")
    if not arquivos:
        print("⚠️  Nada a carregar.")
        return 0

    # Idempotência: só reprocessa o que mudou (caminho + mtime + tamanho)
    man = _manifesto_ler()
    novos = []
    for p in arquivos:
        st = p.stat()
        chave = str(p)
        assinatura = f"{st.st_mtime_ns}:{st.st_size}"
        if not a.forcar and man.get(chave) == assinatura:
            continue
        novos.append(p)
        man[chave] = assinatura
    if not novos:
        print("✅ Nada mudou desde a última carga (idempotente).")
        return 0
    print(f"   {len(novos)} arquivo(s) novo(s) ou alterado(s)")

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("❌ pyarrow ausente — instale para carregar o acervo (R14).")
        return 1

    workers = a.workers or config.WORKERS
    lotes = [([str(p) for p in novos[i:i + LOTE]], a.ocr or config.OCR_MODO)
             for i in range(0, len(novos), LOTE)]
    print(f"⚙️  Extraindo com ProcessPoolExecutor: {len(lotes)} lote(s), "
          f"{workers} processo(s) (R2)")

    t0, registros, erros = time.perf_counter(), [], []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for parcial in ex.map(processar_lote, lotes):
            for r in parcial:
                (erros if "_erro" in r else registros).append(r)
    if not registros:
        print("❌ Nenhum registro extraído.")
        for e in erros[:10]:
            print(f"   • {e['_erro']}")
        return 1

    tabela = pa.Table.from_pylist(registros)
    config.PARQUET.mkdir(parents=True, exist_ok=True)
    pq.write_to_dataset(tabela, root_path=str(config.PARQUET),
                        partition_cols=["fonte", "ano"],
                        compression="zstd", compression_level=config.ZSTD_NIVEL,
                        existing_data_behavior="overwrite_or_ignore")
    config.escrever(MANIFESTO, json.dumps(man, ensure_ascii=False, indent=2))

    dur = time.perf_counter() - t0
    ocr_n = sum(1 for r in registros if r["metodo"] == "ocr")
    sem_texto = sum(1 for r in registros if r["metodo"] == "sem-texto")
    print(f"✅ {len(registros)} página(s) gravada(s) em {dur:.1f}s".replace(".", ","))
    print(f"   Parquet: {config.PARQUET} (zstd nível {config.ZSTD_NIVEL}, "
          f"particionado por fonte/ano)")
    print(f"   Cobertura: nativo {len(registros)-ocr_n-sem_texto} · OCR {ocr_n} · "
          f"SEM TEXTO {sem_texto}")
    if sem_texto:
        print(f"   ⚠️  {sem_texto} página(s) sem camada de texto e sem OCR disponível — "
              "a cobertura está PARCIAL.")
    if erros:
        print(f"   ⚠️  {len(erros)} arquivo(s) não processado(s):")
        for e in erros[:8]:
            print(f"      • {e['_erro']}")
    return 0


def _dataset():
    """Abre o dataset Parquet. Devolve None (com mensagem) se o acervo não existe.

    O diretório existir NÃO significa que há acervo: o scaffold cria a pasta
    vazia. Verificar só o diretório fazia `info` estourar com erro de esquema
    do pyarrow — exceção de biblioteca no lugar de aviso em português.
    """
    if not config.PARQUET.exists() or not any(config.PARQUET.rglob("*.parquet")):
        print(f"ℹ️  Acervo ainda não carregado ({config.PARQUET}).")
        print("   Rode: python3 banco.py carregar --origem ../../../_private/kb")
        return None
    try:
        import pyarrow.dataset as ds
    except ImportError:
        print("❌ pyarrow ausente — instale para consultar o acervo (R14).")
        return None
    try:
        return ds.dataset(str(config.PARQUET), format="parquet", partitioning="hive")
    except Exception as e:
        print(f"❌ Acervo ilegível: {e}")
        print("   Recarregue com: python3 banco.py carregar --forcar")
        return None


def cmd_info(a) -> int:
    d = _dataset()
    if d is None:
        return 1
    import pyarrow.compute as pc
    tab = d.to_table(columns=["fonte", "ano", "metodo", "bytes", "arquivo_origem"])
    n = tab.num_rows
    arquivos = len(set(tab.column("arquivo_origem").to_pylist()))
    metodos = {}
    for m in tab.column("metodo").to_pylist():
        metodos[m] = metodos.get(m, 0) + 1
    tam_parquet = sum(p.stat().st_size for p in config.PARQUET.rglob("*.parquet"))
    tam_origem = int(pc.sum(pc.cast(tab.column("bytes"), "int64")).as_py() or 0)
    partes = sorted({(f, y) for f, y in zip(tab.column("fonte").to_pylist(),
                                            tab.column("ano").to_pylist())})
    print("═══════════════════════════════════════════════════════════")
    print(f"  ACERVO — {config.NOME}")
    print("═══════════════════════════════════════════════════════════")
    print(f"  Raiz Parquet .....: {config.PARQUET}")
    print(f"  Arquivos .........: {arquivos}")
    print(f"  Páginas/linhas ...: {n:,}".replace(",", "."))
    print(f"  Partições ........: {len(partes)}  {partes[:8]}{' …' if len(partes) > 8 else ''}")
    # Formatar o NÚMERO antes: `.replace(".", ",")` sobre a linha inteira
    # também troca os pontos do rótulo ("Tamanho Parquet ,,:").
    mb = f"{tam_parquet/1e6:.1f}".replace(".", ",")
    razao = f"{tam_origem/max(tam_parquet,1):.1f}".replace(".", ",")
    print(f"  Tamanho Parquet ..: {mb} MB")
    print(f"  Compressão .......: zstd nível {config.ZSTD_NIVEL} · razão {razao}×")
    print("  Esquema ..........:")
    for campo in d.schema:
        print(f"      {campo.name:<18} {campo.type}")
    print("  Cobertura de extração:")
    for m, c in sorted(metodos.items(), key=lambda x: -x[1]):
        pct = f"{c/n*100:.1f}".replace(".", ",")
        print(f"      {m:<12} {c:>8}  ({pct}%)")
    if metodos.get("sem-texto"):
        print("  ⚠️  COBERTURA PARCIAL: há páginas sem camada de texto e sem OCR.")
    print("═══════════════════════════════════════════════════════════")
    return 0


def _saida(tabela, formato: str, limite: int | None = None) -> None:
    linhas = tabela.to_pylist()
    if limite:
        linhas = linhas[:limite]
    if formato == "json":
        print(json.dumps(linhas, ensure_ascii=False, indent=2, default=str))
    elif formato == "csv":
        import csv
        w = csv.DictWriter(sys.stdout, fieldnames=list(linhas[0].keys()) if linhas else [])
        w.writeheader()
        w.writerows(linhas)
    else:
        if not linhas:
            print("  (sem resultados)")
            return
        cols = list(linhas[0].keys())
        larg = {c: min(46, max(len(c), *(len(str(l.get(c, ""))[:46]) for l in linhas)))
                for c in cols}
        print(" | ".join(c[:larg[c]].ljust(larg[c]) for c in cols))
        print("-+-".join("-" * larg[c] for c in cols))
        for l in linhas:
            print(" | ".join(str(l.get(c, ""))[:larg[c]].replace("\n", " ").ljust(larg[c])
                             for c in cols))


def cmd_buscar(a) -> int:
    d = _dataset()
    if d is None:
        return 1
    import pyarrow as pa
    termo = a.termo
    rx = re.compile(termo, re.I) if a.regex else None
    achados = []
    for lote in d.to_batches(columns=["arquivo_origem", "pagina", "texto", "metodo"]):
        for linha in lote.to_pylist():
            texto = linha["texto"] or ""
            pos = (rx.search(texto).start() if (rx and rx.search(texto))
                   else (texto.lower().find(termo.lower()) if not rx else -1))
            if pos < 0:
                continue
            ini = max(0, pos - a.contexto // 2)
            achados.append({
                "arquivo": Path(linha["arquivo_origem"]).name,
                "pagina": linha["pagina"], "metodo": linha["metodo"],
                "trecho": " ".join(texto[ini:ini + a.contexto].split()),
            })
            if len(achados) >= a.limite:
                break
        if len(achados) >= a.limite:
            break
    print(f"🔎 {len(achados)} ocorrência(s) de “{termo}”"
          + (" (regex)" if a.regex else ""))
    if achados:
        _saida(pa.Table.from_pylist(achados), a.formato)
    return 0


CONSULTAS = {
    "por-ano": "SELECT ano, COUNT(*) AS paginas, COUNT(DISTINCT arquivo_origem) AS arquivos "
               "FROM acervo {onde} GROUP BY ano ORDER BY ano",
    "por-fonte": "SELECT fonte, COUNT(*) AS paginas, COUNT(DISTINCT arquivo_origem) AS arquivos "
                 "FROM acervo {onde} GROUP BY fonte ORDER BY paginas DESC",
    "cobertura": "SELECT metodo, COUNT(*) AS paginas FROM acervo {onde} "
                 "GROUP BY metodo ORDER BY paginas DESC",
    "maiores": "SELECT nome_arquivo, COUNT(*) AS paginas FROM acervo {onde} "
               "GROUP BY nome_arquivo ORDER BY paginas DESC LIMIT 25",
}


def _ctx():
    try:
        from datafusion import SessionContext
    except ImportError:
        return None
    if not config.PARQUET.exists():
        return None
    ctx = SessionContext()
    # As colunas de partição vivem no CAMINHO (fonte=pdf/ano=2026), não no
    # arquivo. Sem declará-las, o DataFusion não as enxerga e todo GROUP BY
    # por partição falha com "No field named fonte" — justamente as colunas
    # que existem para o motor descartar arquivo sem abrir.
    ctx.register_parquet("acervo", str(config.PARQUET),
                         table_partition_cols=[("fonte", "string"), ("ano", "string")])
    return ctx


def _sql(consulta: str, formato: str) -> int:
    ctx = _ctx()
    if ctx is None:
        print("⚠️  datafusion ausente ou acervo não carregado — SQL indisponível.")
        print("    Os dados continuam intactos; use `buscar` ou instale datafusion (R14).")
        return 1
    t0 = time.perf_counter()
    tabela = ctx.sql(consulta).to_arrow_table()
    dur = (time.perf_counter() - t0) * 1000
    _saida(tabela, formato)
    print(f"\n  ⏱️  {tabela.num_rows} linha(s) em {dur:.0f} ms".replace(".", ","))
    return 0


def cmd_consulta(a) -> int:
    if a.nome not in CONSULTAS:
        print(f"❌ Consulta desconhecida: {a.nome}")
        print(f"   Disponíveis: {', '.join(CONSULTAS)}")
        return 2
    filtros = []
    if a.de:
        filtros.append(f"ano >= '{a.de}'")
    if a.ate:
        filtros.append(f"ano <= '{a.ate}'")
    onde = ("WHERE " + " AND ".join(filtros)) if filtros else ""
    return _sql(CONSULTAS[a.nome].format(onde=onde), a.formato)


def cmd_sql(a) -> int:
    return _sql(a.consulta, a.formato)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Acervo local sem SGBD — DataFusion + Parquet + Arrow (D24/R14).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("carregar", aliases=["load"], help="varre, extrai e grava o Parquet")
    c.add_argument("--origem", default=None)
    c.add_argument("--formatos", default=None)
    c.add_argument("--ocr", choices=["auto", "sempre", "nunca"], default=None)
    c.add_argument("--workers", type=int, default=0)
    c.add_argument("--forcar", action="store_true", help="reprocessa tudo, ignorando o manifesto")
    c.set_defaults(fn=cmd_carregar)

    i = sub.add_parser("info", help="esquema, partições, linhas, compressão, cobertura")
    i.set_defaults(fn=cmd_info)

    b = sub.add_parser("buscar", help="busca textual sem escrever SQL")
    b.add_argument("termo")
    b.add_argument("--limite", type=int, default=20)
    b.add_argument("--contexto", type=int, default=200)
    b.add_argument("--regex", action="store_true")
    b.add_argument("--formato", choices=["tabela", "csv", "json"], default="tabela")
    b.set_defaults(fn=cmd_buscar)

    q = sub.add_parser("consulta", help="consultas nomeadas do domínio")
    q.add_argument("nome", choices=list(CONSULTAS))
    q.add_argument("--de", default=None)
    q.add_argument("--ate", default=None)
    q.add_argument("--formato", choices=["tabela", "csv", "json"], default="tabela")
    q.set_defaults(fn=cmd_consulta)

    s = sub.add_parser("sql", help="SQL livre via Apache DataFusion")
    s.add_argument("consulta")
    s.add_argument("--formato", choices=["tabela", "csv", "json"], default="tabela")
    s.set_defaults(fn=cmd_sql)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
