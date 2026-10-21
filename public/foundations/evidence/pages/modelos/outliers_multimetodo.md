---
title: "13 · Outliers multimétodo (IQR, z-robusto, LOF)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Isolation Forest — retornos e volumes anormais](/modelos/isolation_forest) · [Catálogo](/catalogo) · [Cadeia de Markov de regimes (alta, baixa, lateral) →](/modelos/markov_regimes)

**Tipo:** Estatístico · **Categoria:** Detecção de anomalias · **Fonte na base de conhecimento:** Quant Q67, Q68, Q70, Q73, Q75, Q77, Q79, Q81, Q85; Modelos [130], [140]

Compara critérios de discrepância: boxplot (1,5·IQR), escore-z robusto pela mediana e MAD, e densidade local (LOF). Não existe detector ideal para todo conjunto de dados, então a decisão sai do consenso entre métodos. Mostra quanto um único outlier desloca uma regressão e separa erro de coleta (remover) de evento raro real (manter e estudar). Inclui as nove anomalias sintéticas usadas para testar detectores.

> **Leitura dos dados:** No S&P 500, o boxplot marca 264 dias como outlier (6,7% da amostra); o consenso de três métodos fica com 101. Um único ponto discrepante muda a inclinação da reta de 0,76 para 0,53.

```sql outliers_multimetodo__resumo
select * from quant.outliers_multimetodo__resumo
```
```sql outliers_multimetodo__efeito_regressao
select * from quant.outliers_multimetodo__efeito_regressao
```

<BarChart data={outliers_multimetodo__resumo} x=metodo y=outliers swapXY=true title="Dias marcados como outlier"/>
<DataTable data={outliers_multimetodo__efeito_regressao}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so outliers_multimetodo     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Isolation Forest — retornos e volumes anormais](/modelos/isolation_forest) · [Catálogo](/catalogo) · [Cadeia de Markov de regimes (alta, baixa, lateral) →](/modelos/markov_regimes)
