# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Indexa a base de conhecimento (_private/kb/): deduplica imagens por hash, faz OCR
(tesseract eng+por) em paralelo com ProcessPoolExecutor e gera folhas de contato.

Uso:
    python3 kb_indexar.py ocr      [--kb DIR] [--saida DIR] [--processos N]
    python3 kb_indexar.py folhas   [--kb DIR] [--saida DIR] [--por-folha 6]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
KB_PADRAO = RAIZ / "_private" / "kb"
SAIDA_PADRAO = RAIZ / "_private" / "kb" / "_indice"
EXTENSOES = {".webp", ".jpg", ".jpeg", ".png"}


def _hash(caminho: Path) -> str:
    return hashlib.md5(caminho.read_bytes()).hexdigest()


def inventario(kb: Path) -> dict[str, list[str]]:
    """hash -> lista de caminhos relativos (um conteúdo pode estar em várias pastas)."""
    arquivos = sorted(p for p in kb.rglob("*")
                      if p.suffix.lower() in EXTENSOES and "_indice" not in p.parts)
    with ProcessPoolExecutor() as ex:
        hashes = list(ex.map(_hash, arquivos, chunksize=16))
    mapa: dict[str, list[str]] = {}
    for h, p in zip(hashes, arquivos):
        mapa.setdefault(h, []).append(str(p.relative_to(kb)))
    return mapa


def _ocr_um(args: tuple[str, str]) -> tuple[str, str]:
    """Função pura enviada ao pool: (hash, caminho) -> (hash, texto)."""
    from PIL import Image
    h, caminho = args
    img = Image.open(caminho).convert("L")
    if max(img.size) < 1600:  # amplia imagens pequenas: o OCR erra menos
        f = 1600 / max(img.size)
        img = img.resize((int(img.width * f), int(img.height * f)), Image.LANCZOS)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        try:
            r = subprocess.run(["tesseract", tmp.name, "-", "-l", "eng+por", "--psm", "3"],
                               capture_output=True, text=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
            texto = r.stdout
        finally:
            os.unlink(tmp.name)
    return h, texto


def cmd_ocr(kb: Path, saida: Path, processos: int | None) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    mapa = inventario(kb)
    print(f"[kb] {sum(map(len, mapa.values()))} arquivos · {len(mapa)} conteúdos únicos")
    tarefas = [(h, str(kb / ps[0])) for h, ps in mapa.items()
               if not (saida / "ocr" / f"{h}.txt").exists()]
    (saida / "ocr").mkdir(exist_ok=True)
    feitos = 0
    with ProcessPoolExecutor(max_workers=processos) as ex:
        for h, texto in ex.map(_ocr_um, tarefas, chunksize=4):
            (saida / "ocr" / f"{h}.txt").write_text(texto, encoding="utf-8")
            feitos += 1
            if feitos % 50 == 0:
                print(f"[ocr] {feitos}/{len(tarefas)}", flush=True)
    indice = {h: {"arquivos": ps,
                  "pastas": sorted({Path(p).parts[0] for p in ps}),
                  "caracteres": len((saida / "ocr" / f"{h}.txt").read_text(encoding="utf-8"))}
              for h, ps in mapa.items()}
    (saida / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[ocr] concluído · índice em {saida / 'indice.json'}")


def _folha(args: tuple[int, list[str], str, int]) -> str:
    from PIL import Image, ImageDraw
    n, caminhos, destino, lado = args
    cols = 2
    linhas = (len(caminhos) + cols - 1) // cols
    folha = Image.new("RGB", (cols * lado, linhas * lado), "white")
    d = ImageDraw.Draw(folha)
    for i, c in enumerate(caminhos):
        img = Image.open(c).convert("RGB")
        img.thumbnail((lado, lado - 18))
        x, y = (i % cols) * lado, (i // cols) * lado
        folha.paste(img, (x, y + 18))
        d.text((x + 4, y + 2), f"[{i}] {Path(c).parent.name}/{Path(c).name[:28]}", fill="red")
    folha.save(destino, quality=85)
    return destino


def cmd_folhas(kb: Path, saida: Path, por_folha: int, lado: int) -> None:
    indice = json.loads((saida / "indice.json").read_text(encoding="utf-8"))
    (saida / "folhas").mkdir(parents=True, exist_ok=True)
    itens = sorted(indice.items(), key=lambda kv: (kv[1]["pastas"][0], kv[1]["arquivos"][0]))
    grupos = [itens[i:i + por_folha] for i in range(0, len(itens), por_folha)]
    tarefas = [(n, [str(kb / v["arquivos"][0]) for _, v in g],
                str(saida / "folhas" / f"folha_{n:03d}.jpg"), lado) for n, g in enumerate(grupos)]
    with ProcessPoolExecutor() as ex:
        list(ex.map(_folha, tarefas))
    mapa = {f"folha_{n:03d}.jpg": [h for h, _ in g] for n, g in enumerate(grupos)}
    (saida / "folhas" / "mapa.json").write_text(json.dumps(mapa, indent=1), encoding="utf-8")
    print(f"[folhas] {len(grupos)} folhas em {saida / 'folhas'}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Indexador da base de conhecimento (OCR + folhas de contato).")
    ap.add_argument("comando", choices=["ocr", "folhas"])
    ap.add_argument("--kb", type=Path, default=KB_PADRAO)
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    ap.add_argument("--processos", type=int, default=None)
    ap.add_argument("--por-folha", type=int, default=4)
    ap.add_argument("--lado", type=int, default=900)
    a = ap.parse_args()
    if a.comando == "ocr":
        cmd_ocr(a.kb, a.saida, a.processos)
    else:
        cmd_folhas(a.kb, a.saida, a.por_folha, a.lado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
