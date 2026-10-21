#!/usr/bin/env bash
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# Sobe o site evidence em segundo plano, SEMPRE via screen (D11): dá para reatar e ver ao vivo.
#   bash subir_servidor.sh            (re)inicia na porta 3020
#   bash subir_servidor.sh --parar
# Encerra pelo NOME da sessão screen: `pkill -f "evidence dev"` casaria com a própria linha
# de comando de quem chama (lição herdada do portfólio).
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSAO="qm_evidence"
PORTA="${QUANT_MODELS_PORTA:-3020}"
LOG="$AQUI/../../../logs/qm_evidence.log"
mkdir -p "$(dirname "$LOG")"

screen -S "$SESSAO" -X quit >/dev/null 2>&1 || true
[[ "${1:-}" == "--parar" ]] && { echo "servidor parado"; exit 0; }
sleep 1
screen -dmS "$SESSAO" bash -c "cd '$AQUI' && npx evidence sources > '$LOG' 2>&1 && npx evidence dev --port $PORTA --host 0.0.0.0 >> '$LOG' 2>&1"

for _ in $(seq 1 90); do
  if curl -s -o /dev/null --max-time 5 "http://localhost:$PORTA/"; then
    echo "✅ servidor no ar: http://localhost:$PORTA  (log: $LOG)"; exit 0
  fi
  screen -ls | grep -q "$SESSAO" || { echo "❌ a sessão screen morreu — veja $LOG"; tail -20 "$LOG"; exit 1; }
  sleep 5
done
echo "❌ sem resposta em 450 s — veja $LOG"; tail -20 "$LOG"; exit 1
