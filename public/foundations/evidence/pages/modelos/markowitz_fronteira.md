---
title: "19 · Fronteira eficiente de Markowitz"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Wavelets — decomposição tempo-frequência](/modelos/wavelet_haar) · [Catálogo](/catalogo) · [Algoritmo genético — otimização de carteira →](/modelos/ag_carteira)

**Tipo:** Otimização · **Categoria:** Alocação de carteira · **Fonte na base de conhecimento:** Quant Q37, Q40, Q42, Q43, Q47, Q51; Modelos [91], [97]

Simula milhares de carteiras aleatórias e resolve a otimização média-variância para traçar a fronteira eficiente: o maior retorno esperado para cada nível de risco. Marca a carteira de mínima variância e a de máximo índice de Sharpe (tangência). Mostra visualmente que a diversificação elimina risco não sistemático, mas não o sistemático, e que escolher ativos isoladamente ignora as correlações entre eles.

> **Leitura dos dados:** A carteira de máximo Sharpe tinha Sharpe 1,19 em 2010–2019 e entregou 0,76 em 2020–2026; os pesos iguais foram de 0,35 para 0,94. A fronteira é exata sobre o passado — o erro está na estimativa de médias que o futuro não repete.

```sql markowitz_fronteira__nuvem
select * from quant.markowitz_fronteira__nuvem
```
```sql markowitz_fronteira__fronteira
select * from quant.markowitz_fronteira__fronteira
```
```sql markowitz_fronteira__fora_amostra
select * from quant.markowitz_fronteira__fora_amostra
```
```sql markowitz_fronteira__pesos
select * from quant.markowitz_fronteira__pesos
```

<ScatterPlot data={markowitz_fronteira__nuvem} x=vol_anual_pct y=retorno_anual_pct title="5 mil carteiras aleatórias (treino 2010–2019)" pointSize=3/>
<LineChart data={markowitz_fronteira__fronteira} x=vol_anual_pct y=retorno_anual_pct title="Fronteira eficiente"/>
<BarChart data={markowitz_fronteira__fora_amostra} x=carteira y={["sharpe_treino","sharpe_teste"]} type=grouped title="Sharpe: treino × 2020–2026"/>
<BarChart data={markowitz_fronteira__pesos} x=nome y=peso series=carteira type=grouped yFmt=pct0 swapXY=true title="Pesos"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so markowitz_fronteira     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Wavelets — decomposição tempo-frequência](/modelos/wavelet_haar) · [Catálogo](/catalogo) · [Algoritmo genético — otimização de carteira →](/modelos/ag_carteira)
