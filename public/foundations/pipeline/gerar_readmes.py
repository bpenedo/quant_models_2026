#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Template + blocos → 12 READMEs (D19/D20).

NUNCA traduza 12 arquivos à mão: alguém corrige um exemplo no português e os
outros 11 ficam desatualizados EM SILÊNCIO.

REGRA DE SEGURANÇA: bloco sem tradução é ERRO DE GERAÇÃO. O gerador se RECUSA a
escrever um README incompleto e informa quais blocos faltam — é isso que torna
impossível publicar arquivo meio traduzido sem perceber.

Uso:
  python3 gerar_readmes.py --verificar     cobertura, sem escrever
  python3 gerar_readmes.py                 gera os 12
  python3 gerar_readmes.py --idioma en     gera um
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

TRAD = config.FOUNDATIONS / "translation"
TEMPLATE = TRAD / "readme.template.md"
BLOCOS = TRAD / "readme.blocos.json"

IDIOMAS = [("pt", "pt-BR", "Português", "README.md"),
           ("en", "en-US", "English", "README.en.md"),
           ("es", "es-ES", "Español", "README.es.md"),
           ("fr", "fr-FR", "Français", "README.fr.md"),
           ("de", "de-DE", "Deutsch", "README.de.md"),
           ("zh", "zh-CN", "中文", "README.zh.md"),
           ("ko", "ko-KR", "한국어", "README.ko.md"),
           ("hi", "hi-IN", "हिन्दी", "README.hi.md"),
           ("he", "he-IL", "עברית", "README.he.md"),
           ("ru", "ru-RU", "Русский", "README.ru.md"),
           ("sv", "sv-SE", "Svenska", "README.sv.md"),
           ("fi", "fi-FI", "Suomi", "README.fi.md")]

RX_BLOCO = re.compile(r"\{\{b:([a-z0-9_]+)\}\}")


def seletor(atual: str) -> str:
    partes = []
    for cod, _, nome, arq in IDIOMAS:
        partes.append(f"🌐 **{nome}**" if cod == atual and not partes
                      else (f"**{nome}**" if cod == atual else f"[{nome}]({arq})"))
    return " · ".join(partes)


def direitos(locale: str) -> str:
    arq = TRAD / f"strings.{locale.split('-')[0]}.json"
    if arq.exists():
        try:
            return json.loads(config.ler(arq)).get("_direitos", "") or "TODOS OS DIREITOS RESERVADOS"
        except Exception:
            pass
    return "TODOS OS DIREITOS RESERVADOS"


def tabela_bench(cod: str) -> str:
    """Linhas da tabela de desempenho a partir do MEDIDO (bench_motores.csv) — número no README
    só se foi medido (D14). Nome da carga traduzido pelos blocos bench_<n>."""
    import csv
    arq = config.RAIZ / "public/foundations/evidence/dados/quant/bench_motores.csv"
    if not arq.exists():
        return "| — | — | — | — | — |"
    blocos = json.loads(config.ler(BLOCOS))
    sep = "," if cod in ("pt", "es", "fr", "de", "ru", "sv", "fi") else "."

    def f(x, c):
        if x in ("", None):
            return "—"
        return f"{float(x):.{c}f}".replace(".", sep) + " s"
    linhas = []
    for i, r in enumerate(csv.DictReader(arq.open(encoding="utf-8")), start=1):
        nome = blocos.get(f"bench_{i}", {}).get(cod) or r["carga"]
        linhas.append(f"| {nome} | {f(r['numba_s'], 3)} | {f(r['rust_s'], 3)} | {f(r['fsharp_s'], 3)} | "
                      f"{f(r.get('python_puro_s'), 2)} |")
    return "\n".join(linhas)


def verificar(template: str, blocos: dict) -> dict[str, list[str]]:
    usados = set(RX_BLOCO.findall(template))
    faltando: dict[str, list[str]] = {}
    for cod, _, _, _ in IDIOMAS:
        ausentes = [b for b in sorted(usados)
                    if not (blocos.get(b, {}).get(cod) or "").strip()]
        if ausentes:
            faltando[cod] = ausentes
    orfaos = sorted(usados - set(blocos))
    if orfaos:
        faltando["_sem_chave"] = orfaos
    return faltando


def gerar(template: str, blocos: dict, cod: str, locale: str, arquivo: str) -> None:
    texto = RX_BLOCO.sub(lambda m: blocos.get(m.group(1), {}).get(cod, ""), template)
    texto = texto.replace("{{lang:seletor}}", seletor(cod))
    texto = texto.replace("{{lang:direitos}}", direitos(locale))
    texto = texto.replace("{{lang:tabela_bench}}", tabela_bench(cod))
    destino = config.RAIZ / arquivo
    config.escrever(destino, texto)
    print(f"  💾 {arquivo}")


def main():
    ap = argparse.ArgumentParser(description="Gera os 12 READMEs a partir do template e dos blocos.")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--idioma", default=None)
    a = ap.parse_args()

    if not TEMPLATE.exists() or not BLOCOS.exists():
        sys.exit(f"❌ Template ou blocos ausentes em {TRAD}")
    template = config.ler(TEMPLATE)
    blocos = json.loads(config.ler(BLOCOS))
    usados = set(RX_BLOCO.findall(template))
    print(f"📄 Template: {len(usados)} blocos · {len(IDIOMAS)} idiomas "
          f"= {len(usados)*len(IDIOMAS)} traduções esperadas")

    faltando = verificar(template, blocos)
    if faltando:
        total = sum(len(v) for v in faltando.values())
        print(f"❌ {total} bloco(s) sem tradução:")
        for cod, lista in list(faltando.items())[:12]:
            print(f"   • [{cod}] {len(lista)}: {', '.join(lista[:8])}"
                  + (" …" if len(lista) > 8 else ""))
        print("\n⛔ O gerador NÃO escreve README incompleto (D4/D19).")
        print("   Preencha _private/foundations/translation/readme.blocos.json e repita.")
        sys.exit(1)
    print("✅ Cobertura completa.")
    if a.verificar:
        return

    for cod, locale, _, arquivo in IDIOMAS:
        if a.idioma and cod != a.idioma:
            continue
        gerar(template, blocos, cod, locale, arquivo)
    print("✅ READMEs gerados.")


if __name__ == "__main__":
    main()
