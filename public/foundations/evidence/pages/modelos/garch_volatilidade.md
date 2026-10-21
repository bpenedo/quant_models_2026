---
title: "25 · Volatilidade condicional (EWMA e GARCH(1,1))"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Dinâmica não linear e caudas pesadas](/modelos/sistemas_nao_lineares) · [Catálogo](/catalogo) · [Rede de correlação e centralidade →](/modelos/rede_correlacao)

**Tipo:** Estatístico · **Categoria:** Risco e volatilidade · **Fonte na base de conhecimento:** Modelos [69], [78], [185]

Modela o agrupamento de volatilidade: dias agitados seguem dias agitados. O EWMA (RiskMetrics) e o GARCH(1,1), estimado por máxima verossimilhança, projetam a volatilidade do próximo pregão e o VaR/Expected Shortfall a 99%. Serve para dimensionar posição, ajustar stops e monitorar se a volatilidade dos retornos do modelo permanece estacionária ou começa a mudar de patamar.

> **Leitura dos dados:** S&P 500: persistência α+β = 0,963 — um choque de volatilidade leva 18 pregões para perder metade da força. VaR 99% de 1 dia: 1,75%.

```sql garch_volatilidade__parametros
select * from quant.garch_volatilidade__parametros
```
```sql garch_volatilidade__serie
select * from quant.garch_volatilidade__serie
```

<BigValue data={garch_volatilidade__parametros} value=persistencia title="Persistência α+β" fmt=num3/>
<BigValue data={garch_volatilidade__parametros} value=meia_vida_dias title="Meia-vida do choque (pregões)" fmt=num0/>
<BigValue data={garch_volatilidade__parametros} value=var99_pct title="VaR 99% 1 dia (%)" fmt=num2/>
<LineChart data={garch_volatilidade__serie} x=data y={["vol_garch_anual_pct","vol_ewma_anual_pct"]} title="Volatilidade condicional (% a.a.)"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so garch_volatilidade     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Dinâmica não linear e caudas pesadas](/modelos/sistemas_nao_lineares) · [Catálogo](/catalogo) · [Rede de correlação e centralidade →](/modelos/rede_correlacao)
