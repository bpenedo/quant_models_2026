# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Formatação numérica PT-BR (vírgula decimal, ponto de milhar) — um só lugar.

Trocar '.' por ',' com `str.replace` na frase inteira corrompe a pontuação do texto
(o ponto final vira vírgula) — ver bugs.md BUG-009.
"""
from __future__ import annotations


def br(x: float, casas: int = 2) -> str:
    s = f"{x:,.{casas}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, casas: int = 1) -> str:
    """x já em fração (0,123 → '12,3%')."""
    return br(x * 100, casas) + "%"
