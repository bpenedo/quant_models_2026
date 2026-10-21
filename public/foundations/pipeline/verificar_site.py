#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Passada 2 (frontend) automatizada: abre TODAS as páginas do site num Chromium headless,
coleta erros de console, erros de componente do evidence e consultas vazias, testa o
laboratório WebAssembly e captura as telas do site para o README.

Uso:  python3 verificar_site.py [--url http://localhost:3020] [--sem-capturas]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_modelos import MODELOS  # noqa: E402
from config import RAIZ, TELAS_PRIVADAS, TELAS_PUBLICAS  # noqa: E402

CAPTURAS = {"index": "/", "catalogo": "/catalogo", "laboratorio": "/laboratorio", "motores": "/motores",
            "modelo_triple_barrier": "/modelos/triple_barrier_ou", "modelo_hmm": "/modelos/hmm_regimes"}
SINAIS_ERRO = ["Error in", "error in query", "Cannot read", "is not defined", "No data", "Error:"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:3020")
    ap.add_argument("--sem-capturas", action="store_true")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    rotas = ["/", "/catalogo", "/motores", "/laboratorio"] + [f"/modelos/{m['id']}" for m in MODELOS if m["fase"] == 1]
    falhas: list[str] = []
    destino = TELAS_PRIVADAS / "site"
    destino.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1280, "height": 900}, color_scheme="light")
        erros_console: list[str] = []
        pag.on("console", lambda m: erros_console.append(m.text) if m.type == "error" else None)
        pag.on("pageerror", lambda e: erros_console.append(str(e)))
        for rota in rotas:
            erros_console.clear()
            carregou = False
            for _tentativa in range(2):   # o servidor de desenvolvimento pode estar reprocessando as fontes
                try:
                    pag.goto(a.url + rota, wait_until="networkidle", timeout=120_000)
                    carregou = True
                    break
                except Exception:  # noqa: BLE001
                    pag.wait_for_timeout(10_000)
            if not carregou:
                falhas.append(f"{rota}: não carregou em 2 tentativas")
                print(f"   ❌ {rota:40s} não carregou em 2 tentativas")
                continue
            try:   # captura só depois que as consultas carregaram (tela com "loading…" não prova nada)
                # o botão de status do evidence mostra "loading..." mesmo com classe `success`:
                # o critério é o ESTADO (nenhum .status-bar sem success), não o texto
                pag.wait_for_function(
                    "document.querySelectorAll('button.status-bar:not(.success)').length === 0", timeout=90_000)
                # e os componentes de fato desenhados: nenhum esqueleto de carregamento restante
                pag.wait_for_function(
                    "document.querySelectorAll('[class*=skeleton],[class*=animate-pulse]').length === 0",
                    timeout=90_000)
            except Exception:  # noqa: BLE001
                pass
            pag.wait_for_timeout(2500)
            corpo = pag.inner_text("body")
            pendentes = pag.eval_on_selector_all(
                "button.status-bar:not(.success), [class*=skeleton], [class*=animate-pulse]", "els => els.length")
            achados = ([f"{pendentes} consulta(s)/componente(s) sem renderizar"] if pendentes else []) + \
                [s for s in SINAIS_ERRO if s in corpo]
            ruins = [e for e in erros_console if "favicon" not in e and "DevTools" not in e]
            if rota == "/laboratorio":
                try:
                    pag.wait_for_selector("text=no seu navegador", timeout=60_000)
                    pag.wait_for_selector("text=Evoluído em", timeout=60_000)
                except Exception:  # noqa: BLE001
                    achados.append("laboratório WASM não calculou")
            if achados or ruins:
                falhas.append(f"{rota}: {achados} {ruins[:2]}")
                print(f"   ❌ {rota:40s} {achados} {ruins[:2]}")
            else:
                print(f"   ✅ {rota}")
            nome = next((k for k, v in CAPTURAS.items() if v == rota), None)
            if nome and not a.sem_capturas:
                pag.set_viewport_size({"width": 1280, "height": 1500})
                pag.wait_for_timeout(1500)
                pag.screenshot(path=str(destino / f"{nome}.png"), full_page=False)
                pag.set_viewport_size({"width": 1280, "height": 900})
        nav.close()
    if not a.sem_capturas:
        (TELAS_PUBLICAS / "site").mkdir(parents=True, exist_ok=True)
        for f in destino.glob("*.png"):
            shutil.copy2(f, TELAS_PUBLICAS / "site" / f.name)
    print()
    if falhas:
        print(f"❌ {len(falhas)} página(s) com problema")
        return 1
    print(f"✅ {len(rotas)} páginas sem erro de console nem de componente; laboratório WASM calculando")
    return 0


if __name__ == "__main__":
    sys.exit(main())
