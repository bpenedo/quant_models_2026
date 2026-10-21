#!/usr/bin/env bash
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
#
# Esteira completa do projeto.
#   ./run_all.sh              esteira inteira
#   ./run_all.sh --demo       demonstração de 60 s com dados de exemplo (DC9)
#   ./run_all.sh --rapido     pula as etapas caras
#   ./run_all.sh --background executa em screen + watchdog de 20 min (D11/D12)
set -uo pipefail
cd "$(dirname "$0")"

RAIZ="$(cd ../../.. && pwd)"
SESSAO="quant_models_2026"
MODO="completo"
for a in "$@"; do
  case "$a" in
    --demo) MODO="demo";;
    --rapido) MODO="rapido";;
    --background) MODO="background";;
    -h|--ajuda) sed -n '5,12p' "$0"; exit 0;;
  esac
done

mkdir -p "$RAIZ/logs"

if [[ "$MODO" == "background" ]]; then
  # D11 — SEMPRE screen, NUNCA nohup: screen permite reatar, ver ao vivo e interagir.
  if ! command -v screen >/dev/null; then
    echo "⚠️  'screen' não encontrado. Rodando em primeiro plano."
    echo "    (nunca caímos para nohup: nohup perde o terminal e não reata.)"
    exec "$0"
  fi
  screen -dmS "$SESSAO" bash -c "'$0' 2>&1 | tee '$RAIZ/logs/pipeline.log'"
  echo "🚀 Esteira iniciada em background — sessão screen: $SESSAO"
  echo "   Reatar: screen -r $SESSAO    ·    Encerrar: screen -S $SESSAO -X quit"
  # D12 — watchdog obrigatório, status de 20 em 20 minutos até concluir
  bash watchdog.sh --sessao "$SESSAO" --log "$RAIZ/logs/pipeline.log" \
       --intervalo 20 --rotulo esteira &
  echo "🐕 Watchdog ativo (status a cada 20 min)."
  exit 0
fi

passo() { echo; echo "▶️  $*"; }
falhou() { echo "❌ FALHOU: $*"; exit 1; }

echo "═══════════════════════════════════════════════════════════"
echo "  Quant Models 2026 — esteira ($MODO)"
echo "  Início: $(date '+%d/%m/%Y %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════"

passo "Verificando o ambiente"
python3 --version || falhou "Python 3 ausente"

passo "Compilando os módulos Python (higiene — Passada 1)"
python3 -m py_compile ./*.py || falhou "erro de sintaxe"

if [[ "$MODO" == "demo" ]]; then
  passo "DEMONSTRAÇÃO — 3 modelos e a concordância dos três motores (DC9)"
  python3 executar_modelos.py --sem-registro --so markov_regimes,garch_volatilidade,estatistica_descritiva \
    || falhou "modelos da demonstração"
  python3 -c "import csv; [print('  ▸', r['destaque']) for r in csv.DictReader(open('../evidence/dados/quant/resumo_modelos.csv', encoding='utf-8')) if r['id'] in ('markov_regimes','garch_volatilidade','estatistica_descritiva')]"
  echo; echo "✅ Demo concluída em $SECONDS s."
  exit 0
fi

passo "Dados do DataFeed (D1 consolidado em Parquet + zstd)"
python3 dados_feed.py info || falhou "DataFeed não encontrado (defina QUANT_MODELS_DATAFEED)"
[[ -d ../../../dados/parquet/ohlcv_d1 ]] || python3 dados_feed.py consolidar --tf D1 || falhou "consolidação"

passo "Catálogo de modelos (modelos_quant.md)"
python3 catalogo_modelos.py || falhou "catálogo"

passo "Concordância dos três motores — numba × Rust × F# (Passada 1, D9)"
python3 testes_nucleo.py || falhou "motores divergem"

passo "Imunidade herdada (Passada 1 — DC1)"
[[ -f testes_imunidade.py ]] && { python3 testes_imunidade.py || falhou "imunidade"; } || echo "  ⏭️  rode imunidade.py --semear"

passo "Os 32 modelos em paralelo (ProcessPoolExecutor)"
python3 executar_modelos.py --sem-registro || falhou "modelos"

if [[ "$MODO" != "rapido" ]]; then
  passo "Medição de desempenho (D14)"
  python3 bench.py --registrar --rotulo "esteira completa" || falhou "bench"
  python3 bench.py --verificar || falhou "regressão de desempenho"

  passo "Telas do README (D21)"
  python3 gerar_telas.py || falhou "telas"

  passo "Site evidence.dev + WASM"
  python3 gerar_site.py || falhou "site"

  passo "Internacionalização — TM SDL Trados + 12 READMEs (D4/D20)"
  python3 montar_i18n.py --pt && python3 montar_i18n.py --verificar || falhou "traduções desatualizadas — atualize translation/blocos/<idioma>.json"
  python3 montar_i18n.py && python3 gerar_i18n.py --tudo && python3 gerar_readmes.py || falhou "i18n"
fi

echo
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Esteira concluída em ${SECONDS}s"
echo "  Próximo passo: bash verificar_publicacao.sh"
echo "═══════════════════════════════════════════════════════════"
