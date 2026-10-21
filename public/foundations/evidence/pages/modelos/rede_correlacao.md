---
title: "26 · Rede de correlação e centralidade"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Volatilidade condicional (EWMA e GARCH(1,1))](/modelos/garch_volatilidade) · [Catálogo](/catalogo) · [Causalidade de Granger e contágio →](/modelos/causalidade_granger)

**Tipo:** Sistemas complexos · **Categoria:** Similaridade e estrutura · **Fonte na base de conhecimento:** Curso Laboratório da Bolsa [1]–[5]; Quant Q76

Inspirado na Lazy Network (rede temporal construída por similaridade de documentos 10-K), constrói uma rede em que os ativos são nós e as arestas são correlações fortes, filtrada pela árvore geradora mínima. Calcula as centralidades de força, autovetor, proximidade e intermediação. Ativos periféricos tendem a carregar risco mais idiossincrático; a carteira dos periféricos é comparada com a carteira igualmente ponderada.

> **Leitura dos dados:** Escolhidos pela rede de 2010–2019, os 8 periféricos seguiram quase independentes em 2020–2026 (correlação média 0,00 contra 0,15 dos centrais) e renderam mais (11,0% contra 7,4% a.a.), porém com mais volatilidade. Quem venceu as duas cestas foi a carteira com os 27 (Sharpe 0,95): número de apostas independentes pesa mais que a posição na rede.

```sql rede_correlacao__nos
select * from quant.rede_correlacao__nos
```
```sql rede_correlacao__carteiras
select * from quant.rede_correlacao__carteiras
```

<DataTable data={rede_correlacao__carteiras}/>
<ScatterPlot data={rede_correlacao__nos} x=x y=y series=classe tooltipTitle=nome title="Posição na árvore geradora mínima"/>
<DataTable data={rede_correlacao__nos} rows=30>
  <Column id=nome/><Column id=forca fmt=num2/><Column id=autovetor fmt=num3/><Column id=proximidade fmt=num3/>
  <Column id=intermediacao fmt=num3/><Column id=centralidade_composta title="Centralidade (posto médio)" fmt=num1/>
</DataTable>

![Rede](/telas/rede_correlacao.png)


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so rede_correlacao     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Volatilidade condicional (EWMA e GARCH(1,1))](/modelos/garch_volatilidade) · [Catálogo](/catalogo) · [Causalidade de Granger e contágio →](/modelos/causalidade_granger)
