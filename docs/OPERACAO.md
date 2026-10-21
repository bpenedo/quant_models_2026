<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
-->

# 🛠️ Operação — uma página

> Se algum item desta página exigir o autor, o item **não está pronto**: está na cabeça dele.

## Subir
```bash
cd quant_models_2026/public/foundations/pipeline
./run_all.sh --demo          # demonstração completa em ≤ 60 s
```

## Rodar em background (D11 + D12)
```bash
screen -dmS quant_models_2026 bash -c './run_all.sh 2>&1 | tee ../../../logs/pipeline.log'
bash watchdog.sh --sessao quant_models_2026 --log ../../../logs/pipeline.log --intervalo 20
screen -r quant_models_2026           # ver ao vivo   ·   Ctrl-A D para soltar
```

## Parar
```bash
screen -S quant_models_2026 -X quit
```

## Backup
```bash
# _(preencher: o que precisa ser copiado — dados, Parquet, banco)_
```

## Restaurar — **executar ao menos uma vez**
```bash
# _(preencher e TESTAR: restauração não testada não é restauração)_
```

## Exportar todos os dados do cliente (plano de saída)
```bash
# _(preencher: CSV / SQL / Parquet — formato aberto, sem depender deste sistema)_
```

## Voltar à versão anterior
```bash
git log --oneline -5
git checkout <commit-anterior>
```

---
_Quant Models 2026 · ProfBru - Bruno Penedo © 2026 — TODOS OS DIREITOS RESERVADOS · profbruanbima@gmail.com_
