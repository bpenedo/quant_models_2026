---
title: "11 · Embeddings de retornos (FastICA) + cosseno"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Clusterização de ativos (K-means)](/modelos/kmeans_clusters) · [Catálogo](/catalogo) · [Isolation Forest — retornos e volumes anormais →](/modelos/isolation_forest)

**Tipo:** Aprendizado não supervisionado · **Categoria:** Similaridade e estrutura · **Fonte na base de conhecimento:** Quant Q120–129; Embeddings; Modelos [84]

Transforma a janela recente de retornos de cada ativo em um vetor denso de 2 dimensões por Análise de Componentes Independentes. Ativos que oscilaram de forma parecida ficam próximos no plano. A similaridade por cosseno entre vetores de retornos é uma medida alternativa de correlação, menos sensível a nível e escala, e o embedding reduz ruído antes de comparar. Atualizado a cada janela, mostra pares que se aproximam ou se afastam.

> **Leitura dos dados:** Nos últimos 60 pregões, o par mais parecido é Petróleo Brent × Petróleo WTI (cosseno 0,96) e o mais oposto é Índice do dólar × Euro/Dólar (-0,89): um mapa de proximidade que se atualiza a cada janela.

```sql embedding_retornos__embedding
select * from quant.embedding_retornos__embedding
```
```sql embedding_retornos__similaridade
select * from quant.embedding_retornos__similaridade order by cosseno desc
```

<ScatterPlot data={embedding_retornos__embedding} x=dim1 y=dim2 series=classe tooltipTitle=nome title="Embedding 2D (FastICA)"/>
<DataTable data={embedding_retornos__similaridade} rows=15 search=true>
  <Column id=nome_a title="Ativo A"/><Column id=nome_b title="Ativo B"/><Column id=cosseno fmt=num2/><Column id=pearson fmt=num2/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so embedding_retornos     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Clusterização de ativos (K-means)](/modelos/kmeans_clusters) · [Catálogo](/catalogo) · [Isolation Forest — retornos e volumes anormais →](/modelos/isolation_forest)
