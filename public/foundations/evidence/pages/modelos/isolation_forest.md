---
title: "12 · Isolation Forest — retornos e volumes anormais"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Embeddings de retornos (FastICA) + cosseno](/modelos/embedding_retornos) · [Catálogo](/catalogo) · [Outliers multimétodo (IQR, z-robusto, LOF) →](/modelos/outliers_multimetodo)

**Tipo:** Aprendizado não supervisionado · **Categoria:** Detecção de anomalias · **Fonte na base de conhecimento:** Quant Q155–164; Modelos [235]

Floresta de árvores totalmente aleatórias que isola cada observação; pontos anômalos ficam em ramos curtos porque têm pouco em comum com os demais. Aplicado a retornos e volumes, marca choques de volatilidade e picos de negociação sem precisar de exemplos rotulados. No mercado, a anomalia costuma ser sinal e não ruído: indica mudança de dinâmica e é gatilho para revisar posição ou estratégia.

> **Leitura dos dados:** Sem nenhum rótulo, a floresta de isolamento marca 77 pregões do S&P 500 como anômalos — 21 só em 2020 — e 57% deles são quedas: a anomalia é sinal de mudança de dinâmica, não ruído a descartar.

```sql isolation_forest__resumo
select * from quant.isolation_forest__resumo
```

<Dropdown data={isolation_forest__resumo} name=ativo value=simbolo label=nome defaultValue="US500" title="Ativo"/>

```sql pontos_sel
select * from quant.isolation_forest__pontos where simbolo = '${inputs.ativo.value}'
```

<ScatterPlot data={pontos_sel} x=data y=retorno_pct series=anomalia title="Retornos diários — anomalias destacadas"/>
<DataTable data={isolation_forest__resumo}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so isolation_forest     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Embeddings de retornos (FastICA) + cosseno](/modelos/embedding_retornos) · [Catálogo](/catalogo) · [Outliers multimétodo (IQR, z-robusto, LOF) →](/modelos/outliers_multimetodo)
