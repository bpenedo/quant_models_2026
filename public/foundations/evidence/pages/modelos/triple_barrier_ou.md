---
title: "30 · Regras ótimas de trading (Ornstein-Uhlenbeck)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Backtest walk-forward com custos](/modelos/backtest_walkforward) · [Catálogo](/catalogo) · [Lei de Newcomb-Benford — integridade de dados →](/modelos/benford)

**Tipo:** Probabilístico · **Categoria:** Regras de trading · **Fonte na base de conhecimento:** Modelos [161]

Ajusta um processo de Ornstein-Uhlenbeck (reversão à média) à série e, por Monte Carlo, simula milhares de trajetórias para cada par de alvo de lucro e stop-loss, com período máximo de manutenção. O resultado é uma malha de índices de Sharpe que mostra a combinação ótima de saída. Substitui o 'stop de 2%' arbitrário por uma regra derivada da dinâmica estimada do próprio ativo.

> **Leitura dos dados:** O spread Brent − WTI reverte à média com meia-vida de 22 pregões. Simulando 4.000 trajetórias por célula, a melhor regra é alvo de 1,5σ com stop de 10,0σ (Sharpe por operação 0,63) — um stop percentual fixo ignora a dinâmica do ativo.

```sql triple_barrier_ou__parametros
select * from quant.triple_barrier_ou__parametros
```
```sql triple_barrier_ou__malha
select * from quant.triple_barrier_ou__malha where previsao_sigmas = 0
```

<Heatmap data={triple_barrier_ou__malha} x=stop_sigmas y=alvo_lucro_sigmas value=sharpe valueFmt=num2 title="Sharpe por operação — alvo × stop (σ)"/>
<DataTable data={triple_barrier_ou__parametros}/>

> Recalcule esta malha no navegador, com seus próprios parâmetros, no [Laboratório](/laboratorio).


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so triple_barrier_ou     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Backtest walk-forward com custos](/modelos/backtest_walkforward) · [Catálogo](/catalogo) · [Lei de Newcomb-Benford — integridade de dados →](/modelos/benford)
