---
title: "22 · Programação genética — regressão simbólica"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Algoritmo genético — seleção de indicadores e parâmetros](/modelos/ag_indicadores) · [Catálogo](/catalogo) · [Expoente de Hurst e indicador Hurst móvel →](/modelos/hurst_movel)

**Tipo:** Otimização · **Categoria:** Previsão de retorno · **Fonte na base de conhecimento:** Quant Q107–109, Q111–113, Q115, Q116, Q118; Genético [40], [42]

Os indivíduos são árvores de operações (+, −, ×, ÷, seno, cosseno, máximo) sobre os últimos retornos. A evolução por seleção, crossover de subárvores e mutação procura a fórmula que melhor estima o próximo retorno, com penalidade por tamanho da árvore (parcimônia) para evitar fórmulas gigantes. Cria indicadores novos e legíveis, em vez de combinar os que todo o mercado já usa.

> **Leitura dos dados:** A programação genética descobriu fórmulas legíveis como ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 nós), com correlação de postos de -0,080 com o próximo retorno no treino e -0,028 no teste. A evolução sempre encontra 'algo' no passado; só o período nunca visto separa indicador de coincidência.

```sql programacao_genetica__formulas
select * from quant.programacao_genetica__formulas
```
```sql programacao_genetica__evolucao
select * from quant.programacao_genetica__evolucao
```

<DataTable data={programacao_genetica__formulas} wrapTitles=true>
  <Column id=semente/><Column id=formula title="Fórmula descoberta" wrap=true/><Column id=nos title="Nós"/>
  <Column id=ic_treino title="IC treino" fmt=num3/><Column id=ic_teste title="IC teste" fmt=num3/>
</DataTable>
<LineChart data={programacao_genetica__evolucao} x=geracao y=melhor_aptidao series=semente title="Evolução da aptidão"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so programacao_genetica     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Algoritmo genético — seleção de indicadores e parâmetros](/modelos/ag_indicadores) · [Catálogo](/catalogo) · [Expoente de Hurst e indicador Hurst móvel →](/modelos/hurst_movel)
