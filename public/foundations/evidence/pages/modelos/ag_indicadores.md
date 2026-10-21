---
title: "21 · Algoritmo genético — seleção de indicadores e parâmetros"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Algoritmo genético — otimização de carteira](/modelos/ag_carteira) · [Catálogo](/catalogo) · [Programação genética — regressão simbólica →](/modelos/programacao_genetica)

**Tipo:** Otimização · **Categoria:** Regras de trading · **Fonte na base de conhecimento:** Genético [41]

Busca a combinação de indicadores técnicos e seus parâmetros (períodos de médias, limiares de RSI, janelas de rompimento) que maximiza o desempenho de uma regra de trading no período de treino. O cromossomo codifica liga/desliga de cada indicador e seus parâmetros. O resultado é validado em período posterior, e o número de regras testadas é registrado para dimensionar o risco de mineração de dados.

> **Leitura dos dados:** O AG testou 1826 regras distintas no S&P 500 e a melhor de cada rodada teve Sharpe de treino até 0,78; em 2019–2026 elas ficaram entre 0,41 e 0,54, contra 0,77 de simplesmente ficar comprado. Quanto mais regras se testa, maior o Sharpe de treino por puro acaso.

```sql ag_indicadores__rodadas
select * from quant.ag_indicadores__rodadas
```

<BarChart data={ag_indicadores__rodadas} x=semente y={["sharpe_treino","sharpe_teste"]} type=grouped title="Sharpe: treino (até 2018) × teste (2019–2026)"/>
<DataTable data={ag_indicadores__rodadas}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so ag_indicadores     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Algoritmo genético — otimização de carteira](/modelos/ag_carteira) · [Catálogo](/catalogo) · [Programação genética — regressão simbólica →](/modelos/programacao_genetica)
