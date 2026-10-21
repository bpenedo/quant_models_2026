---
title: "09 · PCA — fatores de risco e índices"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Rede neural MLP — indicador de reversão](/modelos/mlp_reversao) · [Catálogo](/catalogo) · [Clusterização de ativos (K-means) →](/modelos/kmeans_clusters)

**Tipo:** Aprendizado não supervisionado · **Categoria:** Risco e volatilidade · **Fonte na base de conhecimento:** Quant Q22, Q25, Q27, Q31, Q38, Q245–263

Análise de componentes principais da matriz de retornos: encontra direções ortogonais de maior variância, que funcionam como fatores de risco comuns (o primeiro costuma ser o 'mercado'). Mostra a variância explicada acumulada para escolher quantos fatores manter, projeta os ativos em 2D/3D para visualizar semelhanças e permite construir índices otimizados com os ativos mais representativos de cada fator.

> **Leitura dos dados:** O 1º fator sozinho explica 24,5% da variação diária de 27 ativos; são precisos 12 fatores para chegar a 80%. Os 27 ativos não são 27 apostas independentes.

```sql pca_fatores__variancia
select * from quant.pca_fatores__variancia
```
```sql pca_fatores__cargas
select * from quant.pca_fatores__cargas
```
```sql pca_fatores__representantes
select * from quant.pca_fatores__representantes
```

<BarChart data={pca_fatores__variancia} x=componente y=variancia_explicada yFmt=pct1 title="Variância explicada por componente"/>
<LineChart data={pca_fatores__variancia} x=componente y=acumulada yFmt=pct0 markers=true title="Acumulada">
  <ReferenceLine y=0.8 label="80%"/>
</LineChart>

<ScatterPlot data={pca_fatores__cargas} x=PC1 y=PC2 series=classe tooltipTitle=nome title="Ativos no plano dos 2 primeiros fatores"/>

<DataTable data={pca_fatores__representantes}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so pca_fatores     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Rede neural MLP — indicador de reversão](/modelos/mlp_reversao) · [Catálogo](/catalogo) · [Clusterização de ativos (K-means) →](/modelos/kmeans_clusters)
