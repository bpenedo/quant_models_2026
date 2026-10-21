---
title: "08 · Rede neural MLP — indicador de reversão"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Árvores de decisão e Random Forest](/modelos/arvores_random_forest) · [Catálogo](/catalogo) · [PCA — fatores de risco e índices →](/modelos/pca_fatores)

**Tipo:** Aprendizado profundo · **Categoria:** Previsão de direção · **Fonte na base de conhecimento:** Quant Q136–143, Q205–207, Q213–223

Perceptron multicamadas (duas camadas ocultas de 10 neurônios, regularização L2) treinado para prever reversões: alvo +1 quando o preço sobe 5% em 10 dias após quedas, −1 no inverso e 0 na lateralização. As entradas são eventos de Parabolic SAR, cruzamentos do RSI em 30/70 e trocas de sinal do histograma do MACD. Treino em anos passados e validação em ano nunca visto pelo modelo.

> **Leitura dos dados:** Na prata, em 2023–2026 (nunca vistos no treino), a MLP emitiu 607 sinais de reversão de alta com precisão de 17,3%, contra taxa base de 13,6% (1,27× a frequência natural): é essa razão, e não a acurácia geral, que diz se o indicador agrega informação.

```sql mlp_reversao__classes
select * from quant.mlp_reversao__classes
```
```sql mlp_reversao__sinal
select * from quant.mlp_reversao__sinal
```

<DataTable data={mlp_reversao__classes}>
  <Column id=classe/><Column id=sinais_emitidos title="Sinais"/><Column id=eventos_reais title="Eventos reais"/>
  <Column id=precisao title="Precisão" fmt=pct1/><Column id=taxa_base title="Taxa-base" fmt=pct1/>
</DataTable>

<LineChart data={mlp_reversao__sinal} x=data y=fechamento title="Prata 2023–2026 (nunca vista no treino)"/>
<BarChart data={mlp_reversao__sinal} x=data y=indicador_mlp title="Indicador da MLP (+1 alta, −1 queda)"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so mlp_reversao     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Árvores de decisão e Random Forest](/modelos/arvores_random_forest) · [Catálogo](/catalogo) · [PCA — fatores de risco e índices →](/modelos/pca_fatores)
