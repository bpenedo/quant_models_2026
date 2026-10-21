---
title: "27 · Causalidade de Granger e contágio"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Rede de correlação e centralidade](/modelos/rede_correlacao) · [Catálogo](/catalogo) · [Detecção de drift de modelo e de conceito →](/modelos/drift_modelo)

**Tipo:** Estatístico · **Categoria:** Similaridade e estrutura · **Fonte na base de conhecimento:** Modelos [148], [150], [157]

Testa se o passado de um ativo melhora a previsão de outro além do próprio passado deste (teste F em regressões com defasagens). Constrói o grafo direcionado de 'quem antecede quem' entre dólar, juros, metais, energia e bolsas. Distingue correlação de precedência temporal, como no caso da quebra do SVB: os ativos caíram juntos, mas só um teste causal indica se um evento propagou para o outro.

> **Leitura dos dados:** Dos 72 pares testados, 7 sobrevivem à correção de Bonferroni. O mais forte, Euro/Dólar → Índice do dólar, é artefato de horário de fechamento entre fontes diferentes: precedência estatística não é causa — e o teste mostra exatamente onde a intuição seria enganada.

```sql causalidade_granger__granger
select * from quant.causalidade_granger__granger
```

<Heatmap data={causalidade_granger__granger} x=rotulo_efeito y=rotulo_causa value=estatistica_f title="Estatística F (causa → efeito)"/>
<DataTable data={causalidade_granger__granger} rows=15 search=true>
  <Column id=rotulo_causa title="Causa"/><Column id=rotulo_efeito title="Efeito"/><Column id=estatistica_f fmt=num1/>
  <Column id=p_valor fmt=0.0e+0/><Column id=significativo_bonferroni title="Sobrevive a Bonferroni"/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so causalidade_granger     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Rede de correlação e centralidade](/modelos/rede_correlacao) · [Catálogo](/catalogo) · [Detecção de drift de modelo e de conceito →](/modelos/drift_modelo)
