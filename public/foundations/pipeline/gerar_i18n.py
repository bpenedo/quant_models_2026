#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""TM (SDL Trados) → strings.<locale>.json + TMX 1.4b (D4).

A TM em Markdown é a FONTE CANÔNICA. Nenhuma string traduzida existe fora dela.
Corrigir uma tradução é editar UM lugar e regerar.

Uso:
  python3 gerar_i18n.py --tudo         gera strings + TMX
  python3 gerar_i18n.py --verificar    QA (o Verify do Trados) — não escreve
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

TM = config.FOUNDATIONS / "translation/translation.memory.md"
SAIDA = config.FOUNDATIONS / "translation"
LOCALES = ["pt-BR", "en-US", "es-ES", "fr-FR", "de-DE", "zh-CN",
           "ko-KR", "hi-IN", "he-IL", "ru-RU", "sv-SE", "fi-FI"]
CURTO = {l: l.split("-")[0] for l in LOCALES}
RTL = {"he-IL"}


def _tabelas(texto: str, titulo_rx: str) -> list[list[str]]:
    """Extrai as linhas de tabela da seção cujo título casa com o padrão."""
    linhas, dentro, saida = texto.splitlines(), False, []
    for l in linhas:
        if l.startswith("#"):
            dentro = bool(re.search(titulo_rx, l, re.I))
            continue
        if dentro and l.lstrip().startswith("|"):
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            if set("".join(cel)) <= set("-: "):
                continue
            saida.append(cel)
    return saida


def carregar_tm() -> dict:
    if not TM.exists():
        sys.exit(f"❌ TM não encontrada: {TM}")
    texto = config.ler(TM)

    fonte: dict[str, str] = {}
    for cel in _tabelas(texto, r"^##\s*5\.\s*Unidades de tradução"):
        if len(cel) >= 2 and re.fullmatch(r"`?S\d{3}`?", cel[0]):
            fonte[cel[0].strip("`")] = cel[1]

    alvos: dict[str, dict[str, str]] = {l: {} for l in LOCALES if l != "pt-BR"}
    locale_atual = None
    for l in texto.splitlines():
        m = re.match(r"^###\s+([a-z]{2}-[A-Z]{2})\b", l)
        if m:
            locale_atual = m.group(1)
            continue
        if l.startswith("##") and not l.startswith("###"):
            if not re.search(r"5b\.", l):
                locale_atual = None
        if locale_atual and l.lstrip().startswith("|"):
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cel) >= 2 and re.fullmatch(r"`?S\d{3}`?", cel[0]):
                alvos.setdefault(locale_atual, {})[cel[0].strip("`")] = cel[1]

    direitos = {}
    for cel in _tabelas(texto, r"^##\s*4\.\s*Frase de direitos"):
        if len(cel) >= 2 and re.fullmatch(r"`?[a-z]{2}-[A-Z]{2}`?", cel[0]):
            direitos[cel[0].strip("`")] = cel[1]

    glossario: list[list[str]] = _tabelas(texto, r"^##\s*3\.\s*Glossário")
    return {"fonte": fonte, "alvos": alvos, "direitos": direitos, "glossario": glossario}


def qa(tm: dict) -> list[str]:
    """As seis verificações do Verify do Trados."""
    problemas = []
    fonte = tm["fonte"]
    if not fonte:
        problemas.append("Nenhuma unidade de tradução (TU) encontrada na §5 da TM.")
    for locale in LOCALES:
        if locale == "pt-BR":
            continue
        alvo = tm["alvos"].get(locale, {})
        # 5. cobertura de segmento — a verificação que pega o defeito real
        faltando = [t for t in fonte if t not in alvo]
        if faltando:
            problemas.append(f"[{locale}] cobertura incompleta: faltam "
                             f"{len(faltando)} segmento(s): {', '.join(faltando[:6])}")
        # 6. segmentos vazios
        vazios = [t for t, v in alvo.items() if not v.strip()]
        if vazios:
            problemas.append(f"[{locale}] segmento(s) vazio(s): {', '.join(vazios[:6])}")
        # 3. placeables preservados
        for t, src in fonte.items():
            tgt = alvo.get(t, "")
            if not tgt:
                continue
            for marca in ("`", "{", "}"):
                if src.count(marca) != tgt.count(marca):
                    problemas.append(f"[{locale}] {t}: placeable '{marca}' não preservado")
        # 4. encoding estrito
        for t, v in alvo.items():
            if unicodedata.normalize("NFC", v) != v:
                problemas.append(f"[{locale}] {t}: texto não está em NFC")
        if locale not in tm["direitos"]:
            problemas.append(f"[{locale}] frase de direitos ausente na §4 da TM")
    return problemas


def gerar_strings(tm: dict) -> None:
    for locale in LOCALES:
        dados = dict(tm["fonte"]) if locale == "pt-BR" else dict(tm["alvos"].get(locale, {}))
        dados["_direitos"] = tm["direitos"].get(locale, "")
        dados["_locale"] = locale
        dados["_dir"] = "rtl" if locale in RTL else "ltr"
        arq = SAIDA / f"strings.{CURTO[locale]}.json"
        config.escrever(arq, json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
        print(f"  💾 {arq.name} ({len(dados)-3} segmentos)")


def gerar_tmx(tm: dict) -> None:
    tmx = ET.Element("tmx", version="1.4b")
    cab = ET.SubElement(tmx, "header", {
        "creationtool": f"{config.NOME} i18n Pipeline", "creationtoolversion": "1.0.0",
        "segtype": "sentence", "o-tmf": f"{config.SLUG}-TM", "adminlang": "pt-BR",
        "srclang": "pt-BR", "datatype": "plaintext"})
    ET.SubElement(cab, "prop", type="x-project").text = config.NOME
    corpo = ET.SubElement(tmx, "body")
    n = 0
    for tuid, src in tm["fonte"].items():
        tu = ET.SubElement(corpo, "tu", tuid=tuid)
        for locale in LOCALES:
            texto = src if locale == "pt-BR" else tm["alvos"].get(locale, {}).get(tuid, "")
            if not texto:
                continue
            tuv = ET.SubElement(tu, "tuv", {"xml:lang": locale})
            ET.SubElement(tuv, "seg").text = texto
            n += 1
    arq = SAIDA / "translation.memory.tmx"
    ET.indent(tmx, space="  ")
    config.escrever(arq, ET.tostring(tmx, encoding="unicode", xml_declaration=True) + "\n")
    print(f"  💾 {arq.name} ({n} segmentos)")


def main():
    ap = argparse.ArgumentParser(description="Gera i18n a partir da TM (SDL Trados).")
    ap.add_argument("--tudo", action="store_true")
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()

    tm = carregar_tm()
    print(f"📚 TM carregada: {len(tm['fonte'])} TU · {len(LOCALES)} locales")

    problemas = qa(tm)
    if problemas:
        print(f"❌ QA reprovou — {len(problemas)} problema(s):")
        for p in problemas[:25]:
            print(f"   • {p}")
        if a.verificar:
            sys.exit(1)
        sys.exit("⛔ Geração interrompida: não se escreve i18n incompleto (D4).")
    print("✅ QA aprovado nas seis verificações.")
    if a.verificar:
        return
    if a.tudo or True:
        gerar_strings(tm)
        gerar_tmx(tm)
    print("✅ i18n gerado.")


if __name__ == "__main__":
    main()
