---
title: "23 · Expoente de Hurst e indicador Hurst móvel"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Programação genética — regressão simbólica](/modelos/programacao_genetica) · [Catálogo](/catalogo) · [Dinâmica não linear e caudas pesadas →](/modelos/sistemas_nao_lineares)

**Tipo:** Sistemas complexos · **Categoria:** Ciclos e tendência · **Fonte na base de conhecimento:** Modelos [247], [249]

O expoente de Hurst (análise R/S) mede memória da série: H {">"} 0,5 indica persistência (tendência), H {"<"} 0,5 reversão à média e H ≈ 0,5 passeio aleatório. Calculado em janelas móveis de 100 e 150 pregões, a diferença MH100 − MH150 vira um sinal de compra e venda alternativo ao cruzamento de médias móveis, informando qual tipo de estratégia faz sentido no regime atual.

> **Leitura dos dados:** O H bruto de R/S fica entre 0,54 e 0,59 e pareceria 'persistente'; contra séries embaralhadas, nenhum dos 6 ativos mostra memória real. O cruzamento MH100 − MH150 supera o de médias móveis em 3 de 6 ativos pelo índice de Sharpe.

```sql hurst_movel__resumo
select * from quant.hurst_movel__resumo
```
```sql hurst_movel__series
select * from quant.hurst_movel__series
```

<BarChart data={hurst_movel__resumo} x=nome y={["hurst_rs","hurst_nulo"]} type=grouped yMin=0.4 title="H medido × H da série embaralhada"/>
<DataTable data={hurst_movel__resumo}/>
<LineChart data={hurst_movel__series} x=data y=diferenca series=simbolo title="MH100 − MH150"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so hurst_movel     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Programação genética — regressão simbólica](/modelos/programacao_genetica) · [Catálogo](/catalogo) · [Dinâmica não linear e caudas pesadas →](/modelos/sistemas_nao_lineares)
