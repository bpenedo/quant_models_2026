---
title: "31 · Lei de Newcomb-Benford — integridade de dados"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Regras ótimas de trading (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) · [Catálogo](/catalogo) · [Explicabilidade com valores de Shapley (SHAP) →](/modelos/shap_explicabilidade)

**Tipo:** Estatístico · **Categoria:** Detecção de anomalias · **Fonte na base de conhecimento:** Modelos [98]

Em muitos conjuntos de números reais, o primeiro dígito segue a lei de Benford (o dígito 1 aparece em cerca de 30% dos casos). Compara a distribuição observada dos primeiros dígitos de volumes e valores com a teórica pelo qui-quadrado e pela MAD de Nigrini. Desvios fortes sinalizam dados fabricados, arredondados ou corrompidos: um teste barato de auditoria antes de confiar na base de dados.

> **Leitura dos dados:** Só 21 das 29 séries de volume cobrem amplitude suficiente para o teste; aplicar Benford às demais seria falso alarme. Agregados, os volumes cobrem 6,4 ordens de grandeza e dão MAD de 0,0099 (conformidade aceitável).

```sql benford__conformidade
select * from quant.benford__conformidade
```
```sql benford__distribuicao
select * from quant.benford__distribuicao where conjunto = 'TODOS'
```

<BarChart data={benford__distribuicao} x=digito y={["observada","benford"]} type=grouped yFmt=pct0 title="Primeiro dígito — volumes agregados × Benford"/>
<DataTable data={benford__conformidade} rows=30>
  <Column id=nome/><Column id=ordens_grandeza title="Ordens de grandeza" fmt=num1/><Column id=mad_nigrini title="MAD" fmt=num4/><Column id=veredito/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so benford     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Regras ótimas de trading (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) · [Catálogo](/catalogo) · [Explicabilidade com valores de Shapley (SHAP) →](/modelos/shap_explicabilidade)
