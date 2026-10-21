---
title: "20 · Algoritmo genético — otimização de carteira"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Fronteira eficiente de Markowitz](/modelos/markowitz_fronteira) · [Catálogo](/catalogo) · [Algoritmo genético — seleção de indicadores e parâmetros →](/modelos/ag_indicadores)

**Tipo:** Otimização · **Categoria:** Alocação de carteira · **Fonte na base de conhecimento:** Quant Q99–106, Q117; Genético

Cada indivíduo é um vetor de pesos da carteira. A aptidão é o resultado do backtest (Sharpe com penalidade de drawdown). Seleção por roleta, elitismo, crossover em ponto de corte e mutação geram novas populações até a convergência. Diferente da fórmula fechada, aceita objetivos e restrições arbitrárias (custos, limites por ativo, cardinalidade). Avalia o melhor indivíduo fora da amostra para não premiar sobreajuste.

> **Leitura dos dados:** Quatro rodadas paralelas do AG, com sementes diferentes, convergem para a mesma carteira (desvio médio de peso de 0,1 p.p.) com Sharpe de 1,19 em 2010–2019. Em 2020–2026 ela entrega 0,86, abaixo dos pesos iguais (0,94): convergência prova que o ótimo é estável, não que o futuro vai repeti-lo.

```sql ag_carteira__evolucao
select * from quant.ag_carteira__evolucao
```
```sql ag_carteira__rodadas
select * from quant.ag_carteira__rodadas
```
```sql ag_carteira__pesos
select * from quant.ag_carteira__pesos
```

<LineChart data={ag_carteira__evolucao} x=geracao y=melhor_aptidao series=semente title="Evolução da melhor aptidão (4 sementes em paralelo)"/>
<DataTable data={ag_carteira__rodadas}/>
<BarChart data={ag_carteira__pesos} x=nome y=peso series=semente type=grouped swapXY=true yFmt=pct0 title="Pesos por semente"/>

> Rode o mesmo algoritmo genético no seu navegador, em WebAssembly, no [Laboratório](/laboratorio).


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so ag_carteira     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Fronteira eficiente de Markowitz](/modelos/markowitz_fronteira) · [Catálogo](/catalogo) · [Algoritmo genético — seleção de indicadores e parâmetros →](/modelos/ag_indicadores)
