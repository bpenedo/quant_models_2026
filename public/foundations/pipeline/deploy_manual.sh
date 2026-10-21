#!/usr/bin/env bash
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# DEPLOY MANUAL (D23) — este script IMPRIME o passo a passo. NÃO EXECUTA NADA.
#
# ⛔ JAMAIS SUBIR AUTOMATICAMENTE.
# Publicar é ato irreversível e externo: o que sai indexa, cacheia e permanece
# mesmo se apagado depois. A decisão é do autor, sempre.
set -uo pipefail
cd "$(dirname "$0")"
RAIZ="$(cd ../../.. && pwd)"
cd "$RAIZ"

echo "═══════════════════════════════════════════════════════════════"
echo "  DEPLOY MANUAL — Quant Models 2026"
echo "  Este script NÃO executa git push, gh repo create nem publica nada."
echo "═══════════════════════════════════════════════════════════════"

echo
echo "▶️  CONFERÊNCIAS DE SEGURANÇA (executadas agora, somente leitura)"
echo "───────────────────────────────────────────────────────────────"
falha=0
ck() { if [[ -z "$2" ]]; then echo "   ✅ $1"; else echo "   ❌ $1"; echo "$2" | head -5 | sed 's/^/        /'; falha=1; fi }

if [[ -d .git ]]; then
  ck "_private/ ignorado pelo git" "$(git check-ignore -q _private/ && echo '' || echo 'NÃO ignorado')"
  ck "Nenhum arquivo privado rastreado" "$(git ls-files | grep -i '_private' || true)"
else
  echo "   ⚠️  Ainda não é um repositório git (o passo 2 abaixo resolve)."
fi
ck "Nenhum segredo aparente" "$(grep -rniE --include=*.py --include=*.js --include=*.json --include=*.toml --include=*.sh \
   --exclude-dir=github --exclude-dir=repos --exclude-dir=logs \
   'api[_-]?key *= *["'"'"'][^"'"'"']{12,}|BEGIN (RSA|PRIVATE) KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}' . 2>/dev/null | grep -v node_modules | head -5 || true)"
# --exclude: os próprios verificadores citam o padrão que detectam.
ck "Nenhum carimbo de ferramenta de IA" "$(grep -rniE --include=*.py --include=*.md --include=*.sh --include=*.toml \
   --exclude=verificar_publicacao.sh --exclude=deploy_manual.sh --exclude=testes_imunidade.py \
   --exclude=triplecheck.md --exclude=stamp.md --exclude=README.TEMPLATE.md --exclude=foundations.md \
   --exclude-dir=github --exclude-dir=repos --exclude-dir=logs \
   'co-authored-by|generated with .*claude|claude code|anthropic' . 2>/dev/null | grep -v node_modules | head -5 || true)"
ck "Nenhuma imagem de README em _private/" "$(grep -n '_private' README.md README.*.md 2>/dev/null | head -5 || true)"

echo
if [[ "$falha" -eq 1 ]]; then
  echo "   ⛔ Há conferências reprovadas acima. NÃO publique antes de corrigir."
else
  echo "   ✅ Conferências de segurança aprovadas."
fi

echo
echo "▶️  PASSO A PASSO — copie e execute VOCÊ MESMO, no seu terminal"
echo "───────────────────────────────────────────────────────────────"
cat <<FIM

  # ── 1 · gate de publicação (obrigatório) ─────────────────────────
  bash public/foundations/pipeline/verificar_publicacao.sh

  # ── 2 · inicializar o repositório ────────────────────────────────
  cd $RAIZ
  git init
  git branch -M main

  # ── 3 · CONFERIR o .gitignore ANTES de qualquer add ──────────────
  head -20 .gitignore
  git check-ignore -v _private/          # precisa casar com a regra "_private/"

  # ── 4 · adicionar e CONFERIR o que entrou ────────────────────────
  git add -A
  git status
  git ls-files | grep -i "_private"      # PRECISA devolver vazio

  # ── 5 · commit (sem carimbo de ferramenta de IA — D15) ───────────
  git commit -m "Fundação do projeto quant_models_2026

Estrutura, motor, i18n em 12 idiomas, telas e documentação.
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS"

  # ── 6 · criar o repositório PRIVADO no GitHub ────────────────────
  #   Opção A — interface web:
  #     https://github.com/new → nome → marcar "Private" → NÃO criar README
  #   Opção B — gh CLI (você executa; a skill não):
  gh auth status
  gh repo create quant_models_2026 --private --source=. --remote=origin

  # ── 7 · vincular o remoto (se usou a opção A) ────────────────────
  git remote add origin git@github.com:<SEU_USUARIO>/quant_models_2026.git
  git remote -v

  # ── 8 · CONFIRMAR que o repositório é privado ────────────────────
  gh repo view <SEU_USUARIO>/quant_models_2026 --json isPrivate

  # ── 9 · enviar ───────────────────────────────────────────────────
  git push -u origin main

  # ── 10 · conferir no GitHub ──────────────────────────────────────
  #   • o repositório aparece com o cadeado "Private"
  #   • a pasta _private/ NÃO existe no repositório
  #   • a logo aparece abaixo do H1 do README
  #   • as telas de docs/telas/ carregam
  #   • o seletor dos 12 idiomas funciona

FIM

echo "▶️  ATUALIZAÇÕES POSTERIORES"
echo "───────────────────────────────────────────────────────────────"
cat <<'FIM'

  bash public/foundations/pipeline/verificar_publicacao.sh   # gate SEMPRE
  git status && git add -A
  git ls-files | grep -i "_private"     # continua tendo de ser vazio
  git commit -m "<o que mudou, em português>"
  git push

FIM

echo "▶️  SE _private/ FOI RASTREADO POR ENGANO"
echo "───────────────────────────────────────────────────────────────"
cat <<'FIM'

  git rm -r --cached _private/
  echo "_private/" >> .gitignore
  git commit -m "Remove diretório privado do rastreamento"
  git push

  ⚠️  Isso remove do HEAD, não do HISTÓRICO. Se já houve push, o conteúdo
      continua acessível nos commits anteriores: trate como VAZAMENTO —
      rotacione qualquer segredo exposto e considere recriar o repositório.

FIM

echo "═══════════════════════════════════════════════════════════════"
echo "  Nenhum destes comandos foi executado por este script."
echo "  O deploy é seu (D23)."
echo "═══════════════════════════════════════════════════════════════"
