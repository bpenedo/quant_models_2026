---
title: "24 · Dinâmica não linear e caudas pesadas"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Expoente de Hurst e indicador Hurst móvel](/modelos/hurst_movel) · [Catálogo](/catalogo) · [Volatilidade condicional (EWMA e GARCH(1,1)) →](/modelos/garch_volatilidade)

**Tipo:** Sistemas complexos · **Categoria:** Risco e volatilidade · **Fonte na base de conhecimento:** Quant Q28, Q29, Q32, Q33, Q35, Q41; Modelos [66], [67]

Compara a distribuição real dos retornos com a normal: caudas pesadas, assimetria e agrupamento de volatilidade mostram que o mercado é um sistema dinâmico não linear, em que pequenas mudanças produzem grandes efeitos. Mede curtose, quantis extremos e a autocorrelação dos retornos absolutos, e explica por que modelos que assumem normalidade subestimam cisnes negros e quebras de estratégia.

> **Leitura dos dados:** Movimentos de 4 desvios acontecem, em mediana, 64× mais do que a curva normal prevê; o retorno quase não tem memória (autocorrelação -0,02), mas o tamanho do movimento tem (0,15).

```sql sistemas_nao_lineares__caudas
select * from quant.sistemas_nao_lineares__caudas
```
```sql sistemas_nao_lineares__histograma_us500
select * from quant.sistemas_nao_lineares__histograma_us500 where densidade_real > 0 and densidade_normal > 1e-12
```

<LineChart data={sistemas_nao_lineares__histograma_us500} x=z y={["densidade_real","densidade_normal"]} yLog=true title="S&P 500 × normal (escala log)"/>
<BarChart data={sistemas_nao_lineares__caudas} x=nome y=razao_caudas swapXY=true title="Quantas vezes mais eventos de 4σ do que a normal prevê"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so sistemas_nao_lineares     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Expoente de Hurst e indicador Hurst móvel](/modelos/hurst_movel) · [Catálogo](/catalogo) · [Volatilidade condicional (EWMA e GARCH(1,1)) →](/modelos/garch_volatilidade)
