---
title: "28 · Detecção de drift de modelo e de conceito"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Causalidade de Granger e contágio](/modelos/causalidade_granger) · [Catálogo](/catalogo) · [Backtest walk-forward com custos →](/modelos/backtest_walkforward)

**Tipo:** Governança de modelos · **Categoria:** Validação e monitoramento · **Fonte na base de conhecimento:** Modelos [51], [52], [185], [188], [189], [226], [227]

Monitora o modelo em produção: compara a distribuição recente das entradas e dos erros com a do treino (teste de Kolmogorov-Smirnov e índice de estabilidade populacional) e acompanha a acurácia em janela móvel. Classifica o drift em súbito, gradual, incremental ou recorrente. A degradação costuma aparecer antes das perdas financeiras, por isso o alerta é o gatilho para retreinar ou desligar a estratégia.

> **Leitura dos dados:** O modelo treinado em 2010–2016 pede retreino em 8 dos 10 anos seguintes: o regime de entrada daquele período não voltou. 2022 teve a pior acurácia (43,8%) e 2017 o maior deslocamento (KS 0,77) — monitorar a entrada mostra o problema sem esperar a perda.

```sql drift_modelo__anual
select * from quant.drift_modelo__anual
```

<LineChart data={drift_modelo__anual} x=ano y=acuracia yFmt=pct1 markers=true title="Acurácia por ano"/>
<BarChart data={drift_modelo__anual} x=ano y=ks_max series=alerta title="Deslocamento da entrada (KS máx.)">
  <ReferenceLine y=0.25 label="limite de retreino"/>
</BarChart>
<DataTable data={drift_modelo__anual}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so drift_modelo     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Causalidade de Granger e contágio](/modelos/causalidade_granger) · [Catálogo](/catalogo) · [Backtest walk-forward com custos →](/modelos/backtest_walkforward)
