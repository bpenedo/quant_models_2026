---
title: "29 · Backtest walk-forward com custos"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Detecção de drift de modelo e de conceito](/modelos/drift_modelo) · [Catálogo](/catalogo) · [Regras ótimas de trading (Ornstein-Uhlenbeck) →](/modelos/triple_barrier_ou)

**Tipo:** Governança de modelos · **Categoria:** Validação e monitoramento · **Fonte na base de conhecimento:** Modelos [80], [85], [154], [158], [186], [230]–[233]

Motor de backtest vetorizado com janelas de treino e teste que avançam no tempo, custos de transação e slippage, e métricas de desempenho (CAGR, volatilidade, Sharpe, Sortino, drawdown máximo, taxa de acerto). Inclui os portões de parada do pipeline quant: estratégia que falha em robustez ou em período fora da amostra é descartada. Combate vazamento de dados, overfitting e cherrypicking de resultados.

> **Leitura dos dados:** Com custos de 5 bps por giro, 2 de 4 estratégias passam pelos três portões STOP (Pesos iguais, Paridade de risco). A janela do momentum, escolhida a cada mês só com o passado, mudou 45 vezes — o 'parâmetro ótimo' não é constante.

```sql backtest_walkforward__metricas
select * from quant.backtest_walkforward__metricas
```
```sql backtest_walkforward__curvas
select * from quant.backtest_walkforward__curvas
```

<LineChart data={backtest_walkforward__curvas} x=data y=patrimonio series=estrategia yLog=true title="Patrimônio (escala log)"/>
<DataTable data={backtest_walkforward__metricas}>
  <Column id=estrategia/><Column id=cagr_pct title="CAGR %" fmt=num1/><Column id=vol_anual_pct title="Vol %" fmt=num1/>
  <Column id=sharpe fmt=num2/><Column id=drawdown_max_pct title="Drawdown %" fmt=num1/><Column id=giro_anual title="Giro a.a." fmt=num2/>
  <Column id=veredito title="Portões STOP"/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so backtest_walkforward     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Detecção de drift de modelo e de conceito](/modelos/drift_modelo) · [Catálogo](/catalogo) · [Regras ótimas de trading (Ornstein-Uhlenbeck) →](/modelos/triple_barrier_ou)
