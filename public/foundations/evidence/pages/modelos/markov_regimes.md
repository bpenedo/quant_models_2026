---
title: "14 · Cadeia de Markov de regimes (alta, baixa, lateral)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Outliers multimétodo (IQR, z-robusto, LOF)](/modelos/outliers_multimetodo) · [Catálogo](/catalogo) · [Modelo oculto de Markov (HMM gaussiano) →](/modelos/hmm_regimes)

**Tipo:** Probabilístico · **Categoria:** Regime de mercado · **Fonte na base de conhecimento:** Quant Q0–3, Q12, Q21, Q23

Classifica cada período em alta, baixa ou lateral pelo retorno acumulado e estima a matriz de transição P[i,j]: a probabilidade de ir do regime i para o j. Responde perguntas do tipo 'estando em baixa hoje, qual a chance de estar em alta em 20 pregões?' por potências da matriz, e calcula a distribuição estacionária e a duração esperada de cada regime. Serve de filtro para ligar ou desligar estratégias.

> **Leitura dos dados:** No S&P 500, estando em baixa em um bloco de 20 pregões, a chance de o próximo bloco ser de alta é 59,0% — maior que a de continuar em baixa (30,8%). Em equilíbrio, o mercado passa 41,3% do tempo em regime de alta.

```sql markov_regimes__transicao
select * from quant.markov_regimes__transicao
```
```sql markov_regimes__resumo
select * from quant.markov_regimes__resumo
```
```sql markov_regimes__horizonte
select * from quant.markov_regimes__horizonte where de = 'baixa'
```

<Heatmap data={markov_regimes__transicao} x=para y=de value=probabilidade valueFmt=pct0 title="Matriz de transição (blocos de 20 pregões)"/>
<LineChart data={markov_regimes__horizonte} x=pregoes y={["p_alta","p_baixa"]} yFmt=pct0 title="Partindo de 'baixa': probabilidade ao longo do horizonte"/>
<DataTable data={markov_regimes__resumo}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so markov_regimes     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Outliers multimétodo (IQR, z-robusto, LOF)](/modelos/outliers_multimetodo) · [Catálogo](/catalogo) · [Modelo oculto de Markov (HMM gaussiano) →](/modelos/hmm_regimes)
