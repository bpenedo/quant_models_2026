---
title: "07 · Árvores de decisão e Random Forest"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← SVM e métodos de kernel](/modelos/svm_kernels) · [Catálogo](/catalogo) · [Rede neural MLP — indicador de reversão →](/modelos/mlp_reversao)

**Tipo:** Aprendizado supervisionado · **Categoria:** Previsão de direção · **Fonte na base de conhecimento:** Quant Q145–154; Modelos [133], [160]–[172]

Regras condicionais em forma de árvore (ex.: RSI ≤ 39 e %K ≤ 4,6) que separam o espaço em degraus não lineares. A floresta aleatória combina centenas de árvores treinadas em subamostras e vota, reduzindo o overfitting de uma árvore isolada. Entrega a importância de cada indicador, o que torna a decisão explicável. Em dados tabulares, modelos de árvore seguem competitivos com redes profundas.

> **Leitura dos dados:** Árvore com profundidade 20 acerta 83,7% no treino e 49,8% no teste: decorou o passado. A floresta rasa fica em 53,5% — modesta, mas honesta; o atributo mais usado é 'ret_1'.

```sql arvores_random_forest__profundidade
select * from quant.arvores_random_forest__profundidade
```
```sql arvores_random_forest__importancia
select * from quant.arvores_random_forest__importancia
```
```sql arvores_random_forest__metricas
select * from quant.arvores_random_forest__metricas
```

<LineChart data={arvores_random_forest__profundidade} x=profundidade y={["acuracia_treino","acuracia_teste"]} yFmt=pct1 markers=true title="Overfitting por profundidade"/>

<BarChart data={arvores_random_forest__importancia} x=atributo y=importancia swapXY=true title="Importância dos indicadores"/>

<DataTable data={arvores_random_forest__metricas}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so arvores_random_forest     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← SVM e métodos de kernel](/modelos/svm_kernels) · [Catálogo](/catalogo) · [Rede neural MLP — indicador de reversão →](/modelos/mlp_reversao)
