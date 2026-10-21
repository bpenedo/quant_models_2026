---
title: "04 · Regressão linear (MQO) entre ativos"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Estacionariedade (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) · [Catálogo](/catalogo) · [Regressão logística de direção →](/modelos/regressao_logistica)

**Tipo:** Estatístico · **Categoria:** Previsão de retorno · **Fonte na base de conhecimento:** Quant Q15–19, Q24, Q26, Q34, Q187–195

Estima a relação y = b0 + b1·x por mínimos quadrados entre log-retornos de ativos (ex.: S&P 500 × Nasdaq, ouro × dólar). Reporta coeficientes, R², resíduos e intervalo de confiança. Mostra a transformação logarítmica que torna lineares relações exponenciais e o alerta de que correlação não implica causalidade: uma terceira variável oculta pode mover as duas. Base de beta, hedge ratio e fatores.

> **Leitura dos dados:** Dow Jones ~ S&P 500: β = 0,91 com R² = 0,91. Já Treasury americano ~ S&P 500 tem R² de 0,04: a relação 'óbvia' explica quase nada do dia a dia.

```sql regressao_linear__coeficientes
select * from quant.regressao_linear__coeficientes
```
```sql regressao_linear__dispersao
select * from quant.regressao_linear__dispersao
```

<DataTable data={regressao_linear__coeficientes}>
  <Column id=rotulo title="Relação"/><Column id=beta fmt=num2/><Column id=ic95_inf title="IC 95% inf." fmt=num2/>
  <Column id=ic95_sup title="IC 95% sup." fmt=num2/><Column id=r2 title="R²" fmt=num2/><Column id=correlacao fmt=num2/>
</DataTable>

<Dropdown data={regressao_linear__coeficientes} name=par value=rotulo defaultValue="Dow Jones ~ S&P 500" title="Relação"/>

```sql par_sel
select * from quant.regressao_linear__dispersao where par = '${inputs.par.value}'
```

<ScatterPlot data={par_sel} x=x_pct y=y_pct title="Retornos diários (%)"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so regressao_linear     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Estacionariedade (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) · [Catálogo](/catalogo) · [Regressão logística de direção →](/modelos/regressao_logistica)
