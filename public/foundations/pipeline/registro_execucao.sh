#!/usr/bin/env bash
# quant_models_2026 — 4 logs de execução (D28 · I17)
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
#   <ambiente>_DDMM_HHMMSS.stdout.log     saída padrão, passo a passo, [DD/MM/AAAA HH:MM:SS]
#   <ambiente>_DDMM_HHMMSS.stderr.log     saída de erro, passo a passo, [DD/MM/AAAA HH:MM:SS]
#   <ambiente>_DDMM_HHMMSS.janela.log     variação temporal: subida · healthcheck · TOTAL
#   tokenizacao_<ambiente>_DDMM_HHMMSS.md tokens reais gastos na criação do ambiente
#
# Uso:
#   eval "$(bash registro_execucao.sh iniciar --ambiente stack05 --dir logs/infra)"   # exporta REGISTRO_DIR
#   bash registro_execucao.sh passo --fase subida      --nome "subir compose"  -- docker compose up -d
#   bash registro_execucao.sh passo --fase healthcheck --nome "healthcheck"    -- bash verificar.sh
#   bash registro_execucao.sh finalizar
#   bash registro_execucao.sh executar --ambiente venv --verificar "test -x .venv/bin/python" -- bash venv_setup.sh   # tudo em 1
#
# RCA: a coluna de código de saída (janela) e a linha "❌ código de saída N" (stderr) são os
# marcadores de falha. Ferramentas como `docker compose` escrevem PROGRESSO em stderr — o
# stderr.log reflete o stderr real, então linha em stderr não significa, sozinha, erro.
set -uo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
agora() { date '+%d/%m/%Y %H:%M:%S'; }
seg() { date +%s.%N; }
dur() { python3 -c "import sys;s=float(sys.argv[1]);print(f'{int(s//3600):02d}h{int(s%3600//60):02d}m{s%60:06.3f}s'.replace('.',','))" "$1"; }

cmd="${1:-}"; shift || true
case "$cmd" in
  iniciar)
    AMB=""; DIR="logs/infra"
    while [[ $# -gt 0 ]]; do case "$1" in --ambiente) AMB="$2"; shift 2;; --dir) DIR="$2"; shift 2;; *) shift;; esac; done
    [[ -n "$AMB" ]] || { echo "❌ --ambiente obrigatório" >&2; exit 2; }
    AMB="$(echo "$AMB" | tr -c 'A-Za-z0-9_-' '_' | sed 's/_*$//')"
    C="$(date +%d%m_%H%M%S)"
    R="$(mkdir -p "$DIR/${AMB}_$C" && cd "$DIR/${AMB}_$C" && pwd)"
    base="$R/${AMB}_$C"
    : > "$base.stdout.log"; : > "$base.stderr.log"
    {
      echo "# JANELA DE EXECUÇÃO — ambiente $AMB"
      echo "# início: $(agora)  ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
      echo "# colunas: data_hora_fim | fase | passo | duração | código_saída"
    } > "$base.janela.log"
    # .estado é relido com `source`: é CÓDIGO. Todo valor passa por printf %q, senão um
    # caminho com espaço ("Viral Media Analyzer") vira comando e BASE fica indefinida.
    {
      printf 'AMB=%q\n' "$AMB"
      printf 'CARIMBO=%q\n' "$C"
      printf 'BASE=%q\n' "$base"
      printf 'INICIO_S=%q\n' "$(seg)"
      printf 'INICIO_ISO=%q\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf 'N=0\n'
    } > "$R/.estado"
    echo "[$(agora)] [início] ambiente $AMB · registro em $R" >> "$base.stdout.log"
    # Contrato de saída: export REGISTRO_DIR='<caminho>' (lido por eval, registro4logs.py e
    # rodar_prova.sh). Apóstrofo no caminho é escapado à moda shell ('\'') — o eval continua
    # válido e o formato NÃO muda para quem já consome.
    printf "export REGISTRO_DIR='%s'\n" "${R//\'/\'\\\'\'}"
    ;;

  passo)
    R="${REGISTRO_DIR:-}"; FASE="subida"; NOME="passo"
    while [[ $# -gt 0 ]]; do
      case "$1" in --dir) R="$2"; shift 2;; --fase) FASE="$2"; shift 2;; --nome) NOME="$2"; shift 2;; --) shift; break;; *) break;; esac
    done
    [[ -f "$R/.estado" ]] || { echo "❌ registro não iniciado (REGISTRO_DIR)" >&2; exit 2; }
    # shellcheck disable=SC1091
    source "$R/.estado"; N=$((N + 1)); sed -i "s/^N=.*/N=$N/" "$R/.estado"
    P="passo $N · $FASE · $NOME"
    echo "[$(agora)] [$P] ▶ $*" | tee -a "$BASE.stdout.log"
    t0=$(seg)
    # stdout e stderr SEPARADOS, cada linha com data e hora, e também no terminal.
    { "$@" 2> >(while IFS= read -r l; do printf '[%s] [%s] %s\n' "$(agora)" "$P" "$l"; done | tee -a "$BASE.stderr.log" >&2) \
        | while IFS= read -r l; do printf '[%s] [%s] %s\n' "$(agora)" "$P" "$l"; done | tee -a "$BASE.stdout.log"; } 
    rc=${PIPESTATUS[0]}
    sleep 0.2   # deixa o leitor de stderr drenar antes de fechar o passo
    t1=$(seg); d=$(python3 -c "print($t1-$t0)")
    estado=$([[ $rc -eq 0 ]] && echo "✅" || echo "❌")
    echo "[$(agora)] [$P] $estado fim · código $rc · $(dur "$d")" | tee -a "$BASE.stdout.log"
    [[ $rc -ne 0 ]] && echo "[$(agora)] [$P] ❌ código de saída $rc" >> "$BASE.stderr.log"
    echo "$(agora) | $FASE | $NOME | $(python3 -c "print(f'{$d:.3f}'.replace('.',','))") s | $rc" >> "$BASE.janela.log"
    exit $rc
    ;;

  finalizar)
    R="${REGISTRO_DIR:-}"
    while [[ $# -gt 0 ]]; do case "$1" in --dir) R="$2"; shift 2;; *) shift;; esac; done
    [[ -f "$R/.estado" ]] || { echo "❌ registro não iniciado (REGISTRO_DIR)" >&2; exit 2; }
    # shellcheck disable=SC1091
    source "$R/.estado"
    FIM_S=$(seg); FIM_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    python3 - "$BASE.janela.log" "$INICIO_S" "$FIM_S" <<'PY'
import sys
arq, ini, fim = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
fases, falhas = {}, 0
for l in open(arq, encoding="utf-8"):
    if l.startswith("#") or "|" not in l:
        continue
    _, fase, _, d, rc = [c.strip() for c in l.split("|")]
    fases[fase] = fases.get(fase, 0.0) + float(d.split()[0].replace(",", "."))
    falhas += rc != "0"
fmt = lambda s: f"{int(s//3600):02d}h{int(s%3600//60):02d}m{s%60:06.3f}s".replace(".", ",")
sub, hc = fases.get("subida", 0.0), fases.get("healthcheck", 0.0)
outras = sum(v for k, v in fases.items() if k not in ("subida", "healthcheck"))
with open(arq, "a", encoding="utf-8") as f:
    f.write("#\n# ─────────────── RESUMO DA JANELA ───────────────\n")
    f.write(f"# subida do ambiente ........: {fmt(sub)}\n")
    f.write(f"# healthcheck ...............: {fmt(hc)}\n")
    if outras:
        f.write(f"# outras fases ..............: {fmt(outras)}\n")
    f.write(f"# TOTAL (subida+healthcheck) : {fmt(sub + hc)}\n")
    f.write(f"# relógio de parede ..........: {fmt(fim - ini)}  (inclui intervalos entre passos)\n")
    f.write(f"# passos com erro ...........: {falhas}\n")
print(f"⏱️  subida {fmt(sub)} · healthcheck {fmt(hc)} · TOTAL {fmt(sub+hc)} · parede {fmt(fim-ini)} · erros {falhas}")
PY
    echo "# fim: $(date '+%d/%m/%Y %H:%M:%S')  ($FIM_ISO)" >> "$BASE.janela.log"
    python3 "$AQUI/tokenizacao.py" --ambiente "$AMB" --inicio "$INICIO_ISO" --fim "$FIM_ISO" \
      --saida "$R" --carimbo "$CARIMBO" 2>>"$BASE.stderr.log" || echo "⚠️  tokenização não gerada (ver stderr)"
    echo "[$(agora)] [fim] registro concluído" >> "$BASE.stdout.log"
    echo "📁 $R"; ls -1 "$R" | sed 's/^/   /'
    ;;
  executar)
    # atalho de 1 comando: iniciar → subida → (healthcheck) → finalizar, devolvendo o 1º código de erro.
    # Usado pelos scripts de preparo que se auto-registram (asdf_setup.sh, venv_setup.sh…).
    AMB=""; DIR="logs/infra"; NOME="preparo"; VER=""
    while [[ $# -gt 0 ]]; do
      case "$1" in --ambiente) AMB="$2"; shift 2;; --dir) DIR="$2"; shift 2;; --nome) NOME="$2"; shift 2;;
        --verificar) VER="$2"; shift 2;; --) shift; break;; *) break;; esac
    done
    [[ $# -gt 0 ]] || { echo "❌ executar: comando ausente após --" >&2; exit 2; }
    ini="$(bash "$0" iniciar --ambiente "$AMB" --dir "$DIR")" || exit 2
    eval "$ini"; export REGISTRO_DIR
    bash "$0" passo --fase subida --nome "$NOME" -- "$@"; rc=$?
    if [[ $rc -eq 0 && -n "$VER" ]]; then
      bash "$0" passo --fase healthcheck --nome "verificação" -- bash -c "$VER"; rc=$?
    fi
    bash "$0" finalizar
    exit $rc
    ;;
  *)
    sed -n '5,17p' "$0"; exit 2;;
esac
