#!/usr/bin/env bash
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# WATCHDOG (D12/R12) — status a cada 20 minutos até a task concluir.
#
# Processo longo sem sinal de vida é indistinguível de processo travado. Este
# watchdog elimina a pior decisão da operação: "espero mais ou mato?".
#
# 20 minutos e não 5: intervalo curto vira ruído e ensina a ignorar; 20 min é
# curto o bastante para detectar travamento e longo o bastante para cada status
# SIGNIFICAR alguma coisa.
set -uo pipefail

SESSAO=""; LOG=""; INTERVALO=20; PID_ALVO=""; TOTAL=""; ROTULO="task"

uso() {
  cat <<'FIM'
Uso: watchdog.sh --sessao <nome-screen> [--log <arquivo>] [--intervalo <min>]
                 [--pid <pid>] [--total <n>] [--rotulo <nome>]

  --sessao     nome da sessão screen a monitorar (D11)
  --log        arquivo de log acompanhado (última linha útil entra no status)
  --intervalo  minutos entre status (padrão: 20 — D12)
  --pid        monitorar um PID em vez de uma sessão screen
  --total      total de itens, para calcular progresso e ETA
  --rotulo     nome da task no relatório
FIM
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sessao) SESSAO="$2"; shift 2;;
    --log) LOG="$2"; shift 2;;
    --intervalo) INTERVALO="$2"; shift 2;;
    --pid) PID_ALVO="$2"; shift 2;;
    --total) TOTAL="$2"; shift 2;;
    --rotulo) ROTULO="$2"; shift 2;;
    -h|--ajuda|--help) uso; exit 0;;
    *) echo "❌ Opção desconhecida: $1"; uso; exit 2;;
  esac
done

[[ -z "$SESSAO" && -z "$PID_ALVO" ]] && { echo "❌ Informe --sessao ou --pid."; uso; exit 2; }

INICIO=$(date +%s)
INTERVALO_S=$(( INTERVALO * 60 ))
SAIDA_LOG="logs/watchdog_${ROTULO}.log"
mkdir -p "$(dirname "$SAIDA_LOG")"

vivo() {
  if [[ -n "$PID_ALVO" ]]; then kill -0 "$PID_ALVO" 2>/dev/null; return $?; fi
  screen -ls 2>/dev/null | grep -q "[.]${SESSAO}[[:space:]]"
}

# ⚠️ NUNCA usar `pkill -f <termo>` com um termo que aparece na própria linha de
# comando do watchdog: ele mataria a si mesmo. Sempre pelo PID registrado.
pid_da_sessao() {
  [[ -n "$PID_ALVO" ]] && { echo "$PID_ALVO"; return; }
  screen -ls 2>/dev/null | sed -n "s/^[[:space:]]*\([0-9]\+\)\.${SESSAO}[[:space:]].*/\1/p" | head -1
}

fmt_dur() {
  local s=$1
  printf "%02dh%02dm%02ds" $((s/3600)) $(((s%3600)/60)) $((s%60))
}

status() {
  local agora decorrido pid cpu mem ultima progresso eta
  agora=$(date +%s); decorrido=$(( agora - INICIO ))
  pid=$(pid_da_sessao)
  cpu="—"; mem="—"
  if [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1; then
    read -r cpu mem < <(ps -o %cpu=,%mem= -p "$pid" 2>/dev/null | awk '{print $1, $2}')
  fi
  ultima="(sem log)"
  if [[ -n "$LOG" && -f "$LOG" ]]; then
    ultima=$(grep -vE '^\s*$' "$LOG" 2>/dev/null | tail -1 | cut -c1-140)
    [[ -z "$ultima" ]] && ultima="(log vazio)"
  fi
  progresso=""; eta=""
  if [[ -n "$TOTAL" && -n "$LOG" && -f "$LOG" ]]; then
    local feitos
    feitos=$(grep -cE '\[(OK|FEITO|CONCLU)' "$LOG" 2>/dev/null || echo 0)
    if [[ "$feitos" -gt 0 ]]; then
      progresso="   Progresso ...: ${feitos}/${TOTAL} ($(( feitos * 100 / TOTAL ))%)"
      local restante
      restante=$(( decorrido * (TOTAL - feitos) / feitos ))
      eta="   ETA .........: $(fmt_dur $restante) restantes"
    fi
  fi
  {
    echo "─────────────────────────────────────────────────────────────"
    echo "🐕 WATCHDOG · ${ROTULO} · $(date '+%d/%m/%Y %H:%M:%S')"
    echo "   Sessão ......: ${SESSAO:-pid $PID_ALVO}"
    echo "   Estado ......: $(vivo && echo 'EM EXECUÇÃO ✅' || echo 'ENCERRADA ⛔')"
    echo "   Decorrido ...: $(fmt_dur $decorrido)"
    echo "   PID .........: ${pid:-—}   CPU: ${cpu}%   MEM: ${mem}%"
    [[ -n "$progresso" ]] && echo "$progresso"
    [[ -n "$eta" ]] && echo "$eta"
    echo "   Última linha : ${ultima}"
    echo "   Reatar ......: screen -r ${SESSAO}"
    echo "─────────────────────────────────────────────────────────────"
  } | tee -a "$SAIDA_LOG"
}

echo "🐕 Watchdog iniciado — status a cada ${INTERVALO} min (D12). Log: ${SAIDA_LOG}"
status
while vivo; do
  sleep "$INTERVALO_S"
  vivo || break
  status
done

FIM=$(date +%s)
{
  echo "═════════════════════════════════════════════════════════════"
  echo "✅ TASK CONCLUÍDA · ${ROTULO}"
  echo "   Início ......: $(date -d "@$INICIO" '+%d/%m/%Y %H:%M:%S')"
  echo "   Término .....: $(date -d "@$FIM" '+%d/%m/%Y %H:%M:%S')"
  echo "   Duração total: $(fmt_dur $(( FIM - INICIO )))"
  [[ -n "$LOG" && -f "$LOG" ]] && {
    echo "   Últimas linhas do log:"
    tail -5 "$LOG" | sed 's/^/      /'
  }
  echo "═════════════════════════════════════════════════════════════"
} | tee -a "$SAIDA_LOG"
