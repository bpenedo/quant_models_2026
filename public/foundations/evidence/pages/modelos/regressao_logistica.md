---
title: "05 · Regressão logística de direção"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Regressão linear (MQO) entre ativos](/modelos/regressao_linear) · [Catálogo](/catalogo) · [SVM e métodos de kernel →](/modelos/svm_kernels)

**Tipo:** Aprendizado supervisionado · **Categoria:** Previsão de direção · **Fonte na base de conhecimento:** Quant Q16, Q44, Q45, Q52, Q54, Q63

Classifica se o próximo retorno será positivo ou negativo a partir de indicadores técnicos defasados (RSI, MACD, momentum, volatilidade), com saída em probabilidade pela função sigmoide. Treino e teste separados no tempo (walk-forward), sem vazamento de informação do futuro. É a linha de base honesta: qualquer modelo mais complexo precisa vencê-la fora da amostra para justificar sua complexidade.

> **Leitura dos dados:** Fora da amostra (2016–2026) a logística acerta 54,2% da direção do S&P 500 — praticamente a fração de dias de alta (54,2%): previu alta em 98% dos dias e tem AUC 0,492. Acurácia alta sem poder de separação é a armadilha que esta linha de base desarma.

```sql regressao_logistica__metricas
select * from quant.regressao_logistica__metricas
```
```sql regressao_logistica__acerto_anual
select * from quant.regressao_logistica__acerto_anual
```
```sql regressao_logistica__coeficientes
select * from quant.regressao_logistica__coeficientes
```

<BigValue data={regressao_logistica__metricas} value=acuracia title="Acurácia fora da amostra" fmt=pct1/>
<BigValue data={regressao_logistica__metricas} value=taxa_base_alta title="Dias de alta (taxa-base)" fmt=pct1/>
<BigValue data={regressao_logistica__metricas} value=auc title="AUC" fmt=num3/>

<BarChart data={regressao_logistica__acerto_anual} x=ano y=acerto yFmt=pct1 title="Acerto por ano (walk-forward)">
  <ReferenceLine y={regressao_logistica__metricas[0]?.taxa_base_alta} label="taxa-base"/>
</BarChart>

<BarChart data={regressao_logistica__coeficientes} x=atributo y=coeficiente swapXY=true title="Coeficientes padronizados"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so regressao_logistica     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Regressão linear (MQO) entre ativos](/modelos/regressao_linear) · [Catálogo](/catalogo) · [SVM e métodos de kernel →](/modelos/svm_kernels)
