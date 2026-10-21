#!/usr/bin/env bash
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# GATE DE PUBLICAÇÃO — tripla-checagem executável (D5).
# Nenhuma publicação acontece sem as três passadas. Código de saída != 0 reprova.
#
#   bash verificar_publicacao.sh                 as três passadas
#   bash verificar_publicacao.sh --passada 3     só uma
#   bash verificar_publicacao.sh --auto-teste    prova que o gate REPROVA (DC3)
set -uo pipefail
cd "$(dirname "$0")"
RAIZ="$(cd ../../.. && pwd)"

PASSADA_ALVO=0
AUTO_TESTE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --passada) PASSADA_ALVO="$2"; shift 2;;
    --auto-teste) AUTO_TESTE=1; shift;;
    -h|--ajuda) sed -n '5,12p' "$0"; exit 0;;
    *) echo "❌ Opção desconhecida: $1"; exit 2;;
  esac
done

OK=0; FALHAS=0; AVISOS=0
LOG="$RAIZ/_private/foundations/bench/triplecheck.log"
mkdir -p "$(dirname "$LOG")"

verde()   { echo "   ✅ $1"; OK=$((OK+1)); }
vermelho(){ echo "   ❌ $1"; FALHAS=$((FALHAS+1)); }
amarelo() { echo "   ⚠️  $1"; AVISOS=$((AVISOS+1)); }
titulo()  { echo; echo "$1"; echo "$(printf '─%.0s' {1..63})"; }

# checa: descrição | comando (vazio = passa) | modo(vazio_passa|vazio_falha)
checar_vazio() {  # o comando NÃO pode devolver saída
  local desc="$1"; shift
  local saida; saida="$("$@" 2>/dev/null)"
  if [[ -z "$saida" ]]; then verde "$desc"; else
    vermelho "$desc"
    echo "$saida" | head -6 | sed 's/^/        /'
  fi
}

# ═══════════════════════ PASSADA 1 — CORREÇÃO ═══════════════════════
passada1() {
  titulo "🔵 PASSADA 1 — CORREÇÃO (backend, dados, performance)"
  if python3 -m py_compile ./*.py 2>/dev/null; then
    verde "Todos os .py compilam"
  else vermelho "Erro de sintaxe em algum .py"; fi

  if [[ -f testes_nucleo.py ]]; then
    if python3 testes_nucleo.py >/dev/null 2>&1; then verde "testes_nucleo.py — verde"
    else vermelho "testes_nucleo.py — FALHOU"; fi
  else amarelo "testes_nucleo.py ainda não existe"; fi

  if [[ -f testes_imunidade.py ]]; then
    if python3 testes_imunidade.py >/dev/null 2>&1; then verde "Imunidade herdada — verde (DC1)"
    else vermelho "testes_imunidade.py — FALHOU"; fi
  else amarelo "Imunidade não semeada — rode imunidade.py --semear"; fi

  # R11 — encoding explícito em toda leitura/escrita de TEXTO.
  # Verificação por AST, não por grep: grep de linha não enxerga chamada
  # multi-linha (falso positivo) nem distingue `fitz.open` de `open` (idem).
  # Verificador que reprova o certo treina quem o usa a ignorá-lo.
  local sem_enc
  sem_enc=$(python3 - <<'PYENC'
import ast, pathlib, sys
IGNORAR = {"__pycache__", ".venv", "venv", "node_modules", "_private"}
ALVOS = {"read_text", "write_text", "open"}
achados = []
for arq in sorted(pathlib.Path(".").rglob("*.py")):
    if set(arq.parts) & IGNORAR:
        continue
    try:
        arvore = ast.parse(arq.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        f = no.func
        # `open(...)` builtin OU `<path>.read_text/write_text(...)`.
        # `fitz.open`, `zipfile.ZipFile.open` etc. NÃO contam: não são E/S de texto.
        if isinstance(f, ast.Name) and f.id == "open":
            nome = "open"
        elif isinstance(f, ast.Attribute) and f.attr in ("read_text", "write_text"):
            nome = f.attr
        else:
            continue
        chaves = {k.arg for k in no.keywords if k.arg}
        if "encoding" in chaves:
            continue
        # Path.read_text/write_text só aceitam encoding/errors/newline. Outro argumento
        # nomeado (ex.: fitz.TextWriter.write_text(page, render_mode=3)) NÃO é E/S de
        # arquivo — reprová-lo era falso positivo.
        if nome != "open" and chaves - {"encoding", "errors", "newline"}:
            continue
        if nome == "open":
            modos = [a.value for a in no.args[1:2] if isinstance(a, ast.Constant)]
            modos += [k.value.value for k in no.keywords
                      if k.arg == "mode" and isinstance(k.value, ast.Constant)]
            if any("b" in str(m) for m in modos):     # binário não tem encoding
                continue
        achados.append(f"{arq}:{no.lineno}: {nome}() sem encoding=")
for a in achados[:6]:
    print(a)
PYENC
)
  [[ -z "$sem_enc" ]] && verde "Encoding explícito em toda E/S de texto (R11)" \
    || { vermelho "E/S de texto sem encoding= (R11)"; echo "$sem_enc" | sed 's/^/        /'; }

  # D14 — orçamento de performance. Delega ao bench.py: UMA implementação da regra
  # (reimplementá-la aqui fez o gate acusar regressão falsa ao misturar kernels com o
  # caminho crítico — ver catálogo global, "gate × bench").
  local hist="$RAIZ/_private/foundations/bench/historico.jsonl"
  if [[ -s "$hist" ]]; then
    local saida_bench
    if saida_bench=$(cd "$RAIZ/public/foundations/pipeline" && python3 bench.py --verificar 2>&1); then
      verde "Desempenho dentro do orçamento (D14)"
    else
      vermelho "Regressão de desempenho acima da tolerância (D14)"
      echo "$saida_bench" | sed 's/^/        /' | tail -4
    fi
  else amarelo "Nenhuma medição registrada — rode bench.py --registrar (D14)"; fi

  # D24 — acervo local, quando houver
  if [[ -f banco.py ]]; then
    if python3 banco.py info >/dev/null 2>&1; then verde "Acervo local responde (banco.py info — D24)"
    else amarelo "banco.py presente mas sem acervo carregado"; fi
    checar_vazio "Nenhum SGBD introduzido para acervo local (D24)" \
      grep -rn "psycopg2\|pymysql\|sqlalchemy" --include="*.py" \
        --exclude=testes_imunidade.py --exclude=db_postgres.py .
  fi
}

# ═══════════════════════ PASSADA 2 — EXPERIÊNCIA ═══════════════════════
passada2() {
  titulo "🟢 PASSADA 2 — EXPERIÊNCIA (frontend, telas, tradução, UX)"
  echo "   ⚠️  Esta passada é HUMANA. O script confere o que é conferível;"
  echo "       ABRIR E OLHAR cada tela continua sendo obrigação de quem publica."

  local telas
  telas=$(find "$RAIZ/docs/telas" -name "*.png" 2>/dev/null | wc -l)
  [[ "$telas" -gt 0 ]] && verde "$telas tela(s) em docs/telas/ (D21)" \
    || amarelo "Nenhuma tela em docs/telas/ — o README precisa de prova visual (D21)"

  if [[ -f gerar_i18n.py ]]; then
    python3 gerar_i18n.py --verificar >/dev/null 2>&1 \
      && verde "QA de i18n — verde (D4)" || vermelho "QA de i18n — FALHOU (D4)"
  else amarelo "gerar_i18n.py ainda não existe"; fi

  if [[ -f gerar_readmes.py ]]; then
    python3 gerar_readmes.py --verificar >/dev/null 2>&1 \
      && verde "Cobertura de blocos dos READMEs — completa" \
      || vermelho "Blocos de README sem tradução — o gerador se recusa a escrever (D4)"
  fi

  # R1 — saída em pt-BR
  local ingles
  ingles=$(grep -rn "print(\"Error\|print('Error\|print(\"Done\|print(\"Warning" \
           --include="*.py" . 2>/dev/null | head -5)
  [[ -z "$ingles" ]] && verde "Saída de terminal em português-Brasil (R1)" \
    || { vermelho "Saída em inglês encontrada (R1)"; echo "$ingles" | sed 's/^/        /'; }

  # DC9 — demo de 60 s
  grep -q -- "--demo" run_all.sh 2>/dev/null && verde "Demonstração de 60 s disponível (DC9)" \
    || amarelo "run_all.sh sem --demo (DC9)"
}

# ═══════════════════════ PASSADA 3 — INTEGRIDADE ═══════════════════════
passada3() {
  titulo "🟣 PASSADA 3 — INTEGRIDADE (privacidade, autoria, repositório)"
  cd "$RAIZ"

  # D3 — bug NUNCA no README. Padrão ESTREITO: um grep largo por "bug|defeito"
  # gera falso positivo em "debug", em "o mesmo defeito" (da ferramenta
  # concorrente) e em "é um bug, não um ganho". Verificador que reprova o certo
  # treina quem o usa a ignorá-lo.
  checar_vazio "Nenhum bug/limitação deste projeto nos READMEs (D3)" \
    bash -c 'grep -niE "(nosso|neste|deste) (bug|defeito|erro)|bug conhecido|limitação conhecida|known (bug|issue)|BUG-[0-9]{3}" README.md README.*.md; grep -nwE "FIXME|TODO" README.md README.*.md | grep -E "FIXME|TODO:" || true'
  # FIXME/TODO em caixa exata e palavra inteira: com -i, "TODO:" casava "método:".

  # D15 — nenhum carimbo de ferramenta de IA
  # --exclude: os próprios verificadores citam o padrão que detectam (self-reference).
  checar_vazio "Nenhum carimbo de ferramenta de IA (D15)" \
    grep -rniE --include=*.py --include=*.rs --include=*.fs --include=*.md --include=*.sh --include=*.toml --include=*.json --include=*.js \
    --exclude=verificar_publicacao.sh --exclude=deploy_manual.sh --exclude=testes_imunidade.py \
    --exclude=triplecheck.md --exclude=stamp.md --exclude=global_main_bugs.md \
    --exclude=README.TEMPLATE.md --exclude=foundations.md --exclude-dir=logs --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=build --exclude-dir=.evidence --exclude-dir=target \
    --exclude-dir=github --exclude-dir=repos \
    "co-authored-by|generated with .*claude|claude code|anthropic" .
  # --exclude-dir=github/repos: corpus de TERCEIROS em _private/kb/github e dados/repos (clonado
  # para estudo, nunca publicado — D23). Varrê-lo reprovava o projeto por código alheio.

  # D23 — _private/ nunca rastreado
  if [[ -d .git ]]; then
    checar_vazio "Nenhum arquivo de _private/ rastreado pelo git (D23)" \
      bash -c 'git ls-files | grep -i "_private" || true'
    git check-ignore -q _private/ && verde ".gitignore cobre _private/ (D23)" \
      || vermelho ".gitignore NÃO cobre _private/ (D23)"
  else amarelo "Ainda não é repositório git — conferir antes do primeiro commit"; fi

  # Segredos
  checar_vazio "Nenhum segredo aparente no código" \
    grep -rniE --include=*.py --include=*.js --include=*.json --include=*.toml --include=*.sh --include=*.md \
    --exclude-dir=github --exclude-dir=repos --exclude-dir=logs --exclude-dir=node_modules \
    --exclude-dir=.evidence --exclude-dir=build --exclude-dir=target --exclude-dir=bin --exclude-dir=obj \
    "api[_-]?key *= *[\"'][^\"']{12,}|BEGIN (RSA|PRIVATE) KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}" .

  # D19 — marcadores remanescentes
  checar_vazio "Nenhum marcador {{...}} remanescente nos READMEs (D19)" \
    bash -c 'grep -o "{{[^}]*}}" README.md README.*.md 2>/dev/null || true'

  # D21 — imagem em caminho público
  checar_vazio "Nenhuma imagem de README apontando para _private/ (D21)" \
    bash -c 'grep -n "_private" README.md README.*.md 2>/dev/null || true'

  # D20 — 12 idiomas
  local n; n=$(ls README.md README.*.md 2>/dev/null | wc -l)
  [[ "$n" -eq 12 ]] && verde "12 READMEs presentes (D20)" \
    || amarelo "$n README(s) — o padrão são 12 idiomas (D20)"

  # D22 — logo e assinatura
  if [[ -f README.md ]]; then
    grep -q "docs/logo_capa.png" README.md && verde "Logo abaixo do H1 (D22)" \
      || vermelho "README.md sem a logo de docs/logo_capa.png (D22)"
    grep -q "ProfBru © 2026" README.md && verde "Assinatura ProfBru © 2026 presente (D22)" \
      || vermelho "README.md sem a assinatura ProfBru © 2026 (D22)"
  else amarelo "README.md ainda não gerado"; fi

  # D11 — nunca nohup
  checar_vazio "Nenhum uso de nohup (D11 — background é sempre screen)" \
    bash -c 'grep -rnE "^[^#]*\bnohup\b" --include="*.sh" --include="*.py" \
      --exclude=verificar_publicacao.sh --exclude=testes_imunidade.py \
      --exclude=run_all.sh --exclude-dir=github --exclude-dir=repos --exclude-dir=node_modules \
      --exclude-dir=.evidence . 2>/dev/null || true'

  # D12 — watchdog de 20 min
  if [[ -f public/foundations/pipeline/watchdog.sh ]]; then
    grep -q "INTERVALO=20" public/foundations/pipeline/watchdog.sh \
      && verde "Watchdog com intervalo de 20 min (D12)" \
      || vermelho "Watchdog sem o intervalo de 20 min (D12)"
  else vermelho "watchdog.sh ausente (D12)"; fi

  # D18 — carimbo em todo arquivo-fonte
  if python3 public/foundations/pipeline/stamp.py --verificar . >/dev/null 2>&1; then
    verde "Todo arquivo-fonte carimbado (D18)"
  else vermelho "Arquivos sem carimbo de autoria (D18) — rode stamp.py --verificar ."; fi

  # D16 — CHECKPOINT em dia
  local cont="_private/foundations/.checkpoint_contador.json"
  if [[ -f "$cont" ]]; then
    python3 -c "
import json,sys
d=json.load(open('$cont',encoding='utf-8'))
sys.exit(1 if d.get('desde_ultimo_bloco',0)>=3 else 0)" \
      && verde "CHECKPOINT em dia (D16)" \
      || vermelho "3 grandes solicitações sem bloco de CHECKPOINT (D16)"
  else amarelo "Contador de CHECKPOINT ainda não iniciado (D16)"; fi

  # D17 — knowledgebase
  [[ -s _private/kb/knowledgebase.md ]] && verde "knowledgebase.md presente (D17)" \
    || vermelho "knowledgebase.md ausente ou vazio (D17)"

  cd - >/dev/null
}

# ═══════════════════════ AUTO-TESTE DO GATE (DC3) ═══════════════════════
auto_teste() {
  titulo "🧪 AUTO-TESTE — o gate precisa REPROVAR o que é errado"
  echo "   Testar só o caso bom deixa passar o verificador que aprova tudo —"
  echo "   o defeito mais caro do catálogo global."
  local tmp="$RAIZ/README.__autoteste__.md"
  printf '# t\n\nEste é um bug conhecido do projeto.\nCo-Authored-By: alguém\n' > "$tmp"
  local saida
  saida=$(cd "$RAIZ" && grep -niE "(nosso|neste|deste) (bug|defeito|erro)|bug conhecido|limitação conhecida|BUG-[0-9]{3}" README.__autoteste__.md 2>/dev/null)
  [[ -n "$saida" ]] && verde "O verificador de bugs-em-README REPROVA quando deve" \
    || vermelho "O verificador de bugs-em-README NÃO reprovou — ele está cego"
  saida=$(cd "$RAIZ" && grep -niE "co-authored-by" README.__autoteste__.md 2>/dev/null)
  [[ -n "$saida" ]] && verde "O verificador de carimbo de IA REPROVA quando deve" \
    || vermelho "O verificador de carimbo de IA NÃO reprovou — ele está cego"
  # E o inverso: não pode reprovar construção legítima
  printf '# t\n\nUse a variável DEBUG=1. A ferramenta concorrente tem o mesmo defeito.\n' > "$tmp"
  saida=$(cd "$RAIZ" && grep -niE "(nosso|neste|deste) (bug|defeito|erro)|bug conhecido|limitação conhecida|BUG-[0-9]{3}" README.__autoteste__.md 2>/dev/null)
  [[ -z "$saida" ]] && verde "O verificador NÃO reprova construção legítima (debug / defeito do concorrente)" \
    || vermelho "Falso positivo: o verificador reprovou texto legítimo"
  rm -f "$tmp"
}

# ═══════════════════════ EXECUÇÃO ═══════════════════════
echo "═══════════════════════════════════════════════════════════════"
echo "  GATE DE PUBLICAÇÃO — Quant Models 2026"
echo "  $(date '+%d/%m/%Y %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════"

[[ "$AUTO_TESTE" == "1" ]] && { auto_teste; }
if [[ "$AUTO_TESTE" != "1" ]]; then
  [[ "$PASSADA_ALVO" == "0" || "$PASSADA_ALVO" == "1" ]] && passada1
  [[ "$PASSADA_ALVO" == "0" || "$PASSADA_ALVO" == "2" ]] && passada2
  [[ "$PASSADA_ALVO" == "0" || "$PASSADA_ALVO" == "3" ]] && passada3
fi

titulo "RESULTADO"
echo "   ✅ Aprovados: $OK    ⚠️  Avisos: $AVISOS    ❌ Falhas: $FALHAS"
echo "$(date -Iseconds)  passadas=${PASSADA_ALVO:-todas}  ok=$OK  avisos=$AVISOS  falhas=$FALHAS" >> "$LOG"

if [[ "$FALHAS" -gt 0 ]]; then
  echo
  echo "   ⛔ PUBLICAÇÃO INTERROMPIDA. Corrija as falhas acima."
  echo "      Não existe 'passar assim mesmo' (D5)."
  exit 1
fi
echo
echo "   ✅ Gate aprovado. Próximo passo: bash deploy_manual.sh"
echo "      Lembre: o deploy é MANUAL. Nada sobe automaticamente (D23)."
