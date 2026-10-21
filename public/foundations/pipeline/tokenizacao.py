#!/usr/bin/env python3
# quant_models_2026 — 4 logs de execução (D28 · I17)
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Soma o uso de tokens registrado pelo agente de IA no transcript da sessão (~/.claude/projects), dentro da
janela [início, fim] da criação do ambiente, e grava tokenizacao_<ambiente>_DDMM_HHMMSS.md.

Não é estimativa: o transcript (~/.claude/projects/<projeto>/<sessão>.jsonl) guarda, por
mensagem do assistente, input_tokens, cache_creation_input_tokens, cache_read_input_tokens
e output_tokens (com thinking_tokens).

⚠️ DEDUPLICAÇÃO OBRIGATÓRIA. A mesma mensagem aparece em várias linhas do transcript
(medido: 502 linhas, 224 mensagens distintas, usage idêntico nas repetições). Somar linhas
inflaria a conta ~2,2×. Conta-se uma vez por message.id.

Uso:
  python3 tokenizacao.py --ambiente stack05 --inicio 2026-09-14T18:00:00Z --fim 2026-09-14T18:30:00Z --saida DIR
  python3 tokenizacao.py ... --transcript ~/.claude/projects/X/Y.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ENCODING = "utf-8"
milhar = lambda v: f"{v:,}".replace(",", ".")


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def mensagens(transcript: Path, ini: datetime, fim: datetime) -> dict[str, dict]:
    """Mensagens distintas na janela, MAIS a última imediatamente anterior ao início.

    A mensagem que dispara `registro_execucao.sh iniciar` é gerada ANTES de o script rodar
    (medido: 4 s antes do carimbo de início). Sem incluí-la, a conta perde justamente o
    raciocínio que decidiu criar o ambiente.
    """
    vistas: dict[str, dict] = {}
    anterior: tuple[str, dict] | None = None
    with open(transcript, encoding=ENCODING) as f:
        for linha in f:
            try:
                o = json.loads(linha)
            except json.JSONDecodeError:
                continue
            m = o.get("message") or {}
            if o.get("type") != "assistant" or not m.get("usage") or not o.get("timestamp"):
                continue
            quando = ts(o["timestamp"])
            registro = {"quando": quando, "modelo": m.get("model", "?"), "usage": m["usage"]}
            chave = m.get("id") or o.get("uuid")
            if quando < ini:
                anterior = (chave, registro)
            elif quando <= fim:
                vistas[chave] = registro
    if anterior and (ini - anterior[1]["quando"]).total_seconds() <= 300:
        vistas.setdefault(anterior[0], anterior[1])
    return vistas


def localizar_transcript(ini: datetime, fim: datetime) -> Path | None:
    """O transcript com MAIS mensagens dentro da janela (a sessão que criou o ambiente)."""
    melhor, maior = None, 0
    base = Path.home() / ".claude" / "projects"
    for arq in base.glob("*/*.jsonl"):
        try:
            # Mesma tolerância de 300 s da mensagem disparadora: quando TODA a criação cabe numa
            # única chamada de ferramenta, o transcript só é escrito de novo DEPOIS do fim — o
            # mtime fica antes do início e o filtro antigo descartava a sessão certa.
            if (ini - datetime.fromtimestamp(arq.stat().st_mtime, timezone.utc)).total_seconds() > 300:
                continue
            n = len(mensagens(arq, ini, fim))
        except OSError:
            continue
        if n > maior:
            melhor, maior = arq, n
    return melhor


def main() -> int:
    ap = argparse.ArgumentParser(description="Tokens reais gastos na criação de um ambiente.")
    ap.add_argument("--ambiente", required=True)
    ap.add_argument("--inicio", required=True, help="ISO-8601 UTC")
    ap.add_argument("--fim", default=None, help="ISO-8601 UTC (padrão: agora)")
    ap.add_argument("--saida", default=".")
    ap.add_argument("--transcript", default=None)
    ap.add_argument("--carimbo", default=None, help="DDMM_HHMMSS do arquivo (padrão: o do início)")
    a = ap.parse_args()

    ini = ts(a.inicio)
    fim = ts(a.fim) if a.fim else datetime.now(timezone.utc)
    tr = Path(a.transcript).expanduser() if a.transcript else localizar_transcript(ini, fim)
    carimbo = a.carimbo or ini.astimezone().strftime("%d%m_%H%M%S")
    destino = Path(a.saida) / f"tokenizacao_{a.ambiente}_{carimbo}.md"

    msgs = mensagens(tr, ini, fim) if tr and tr.exists() else {}
    soma = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
            "output_tokens": 0, "thinking_tokens": 0}
    modelos: dict[str, int] = {}
    for m in msgs.values():
        u = m["usage"]
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
            soma[k] += int(u.get(k) or 0)
        soma["thinking_tokens"] += int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)
        modelos[m["modelo"]] = modelos.get(m["modelo"], 0) + 1
    entrada_total = soma["input_tokens"] + soma["cache_creation_input_tokens"] + soma["cache_read_input_tokens"]

    L = ["<!--", "Infraestrutura de Ambientes Locais — tokenização da criação de ambiente",
         "Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS", "-->", "",
         f"# 🔢 Tokenização — ambiente `{a.ambiente}`", "",
         "| Campo | Valor |", "|---|---|",
         f"| Ambiente | `{a.ambiente}` |",
         f"| Janela | {ini.astimezone():%d/%m/%Y %H:%M:%S} → {fim.astimezone():%d/%m/%Y %H:%M:%S} |",
         f"| Duração | {int((fim - ini).total_seconds() // 60)} min {int((fim - ini).total_seconds() % 60)} s |",
         f"| Transcript | `{tr if tr else 'NÃO ENCONTRADO'}` |",
         f"| Mensagens do assistente (distintas) | {milhar(len(msgs))} |",
         f"| Modelo(s) | {', '.join(f'{k} ({v})' for k, v in modelos.items()) or '—'} |", "",
         "## Tokens gastos", "",
         "| Tipo | Tokens | O que é |", "|---|---:|---|",
         f"| Entrada nova | {milhar(soma['input_tokens'])} | texto novo enviado ao modelo |",
         f"| Entrada gravada em cache | {milhar(soma['cache_creation_input_tokens'])} | contexto escrito no cache de prompt |",
         f"| Entrada lida do cache | {milhar(soma['cache_read_input_tokens'])} | contexto reaproveitado (custo menor por token) |",
         f"| **Entrada total** | **{milhar(entrada_total)}** | soma das três |",
         f"| **Saída** | **{milhar(soma['output_tokens'])}** | resposta gerada (inclui raciocínio) |",
         f"| └ raciocínio (thinking) | {milhar(soma['thinking_tokens'])} | parte da saída |",
         f"| **Total geral** | **{milhar(entrada_total + soma['output_tokens'])}** | entrada total + saída |", "",
         "> **Fonte:** uso real registrado pelo agente no transcript, uma vez por `message.id` — o transcript repete a",
         "> mesma mensagem em várias linhas, e somar linhas inflaria a conta.",
         "> **Limite:** conta o que o **assistente** consumiu nesta sessão dentro da janela; subagentes e",
         "> outras sessões paralelas têm transcripts próprios e não entram.", ""]
    if not msgs:
        L += ["> ⚠️ Nenhuma mensagem com uso de tokens na janela — execução fora de sessão do agente, ou",
              "> transcript não localizado. Informe `--transcript`.", ""]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(L) + "\n", encoding=ENCODING)
    print(f"🔢 {destino} · {milhar(len(msgs))} mensagens · entrada {milhar(entrada_total)} · saída {milhar(soma['output_tokens'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
