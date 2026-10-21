---
title: "10 · Clusterização de ativos (K-means)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← PCA — fatores de risco e índices](/modelos/pca_fatores) · [Catálogo](/catalogo) · [Embeddings de retornos (FastICA) + cosseno →](/modelos/embedding_retornos)

**Tipo:** Aprendizado não supervisionado · **Categoria:** Similaridade e estrutura · **Fonte na base de conhecimento:** Quant Q48, Q49, Q53, Q64, Q65, Q69, Q71, Q74, Q76

Agrupa ativos com comportamento semelhante (retorno médio, volatilidade, correlação, drawdown) posicionando K centroides e atualizando-os até convergir. Escolhe K pelo método do cotovelo e pela silhueta, em vez de fixá-lo à mão. O resultado mostra que 'diversificar' entre ativos do mesmo grupo é diversificação aparente, e orienta a seleção de um representante por grupo.

> **Leitura dos dados:** A silhueta escolhe K = 4 grupos sem intervenção manual; há grupo que mistura 3 classes de ativo diferentes — o rótulo 'commodity' ou 'câmbio' não diz como o ativo se comporta.

```sql kmeans_clusters__ativos
select * from quant.kmeans_clusters__ativos
```
```sql kmeans_clusters__escolha_k
select * from quant.kmeans_clusters__escolha_k
```

<LineChart data={kmeans_clusters__escolha_k} x=k y=silhueta markers=true title="Silhueta por K"/>
<ScatterPlot data={kmeans_clusters__ativos} x=x y=y series=grupo tooltipTitle=nome title="Grupos (projeção PCA)"/>
<DataTable data={kmeans_clusters__ativos} rows=30>
  <Column id=nome/><Column id=classe/><Column id=grupo/><Column id=retorno_anual fmt=pct1/><Column id=vol_anual fmt=pct1/>
  <Column id=drawdown_max fmt=pct1/><Column id=corr_sp500 fmt=num2/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so kmeans_clusters     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← PCA — fatores de risco e índices](/modelos/pca_fatores) · [Catálogo](/catalogo) · [Embeddings de retornos (FastICA) + cosseno →](/modelos/embedding_retornos)
