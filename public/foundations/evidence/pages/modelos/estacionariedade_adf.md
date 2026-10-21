---
title: "03 · Estacionariedade (Augmented Dickey-Fuller)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Suporte e resistência por moda + clusterização](/modelos/suporte_resistencia) · [Catálogo](/catalogo) · [Regressão linear (MQO) entre ativos →](/modelos/regressao_linear)

**Tipo:** Estatístico · **Categoria:** Validação e monitoramento · **Fonte na base de conhecimento:** Quant Q57–62, Q72, Q78, Q80

Testa se média e variância da série são constantes no tempo pelo teste ADF (regressão da diferença sobre o nível defasado e defasagens da diferença). Preços quase nunca são estacionários; retornos costumam ser. Treinar um modelo com preços é treinar com uma distribuição que não volta mais: o teste impede esse erro antes que ele vire prejuízo, e decide se a série entra no modelo em nível, em diferença ou em log-retorno.

> **Leitura dos dados:** 1 de 8 séries de preço são estacionárias a 5%; em log-retorno, 8 de 8. Treinar com preço é treinar com uma distribuição que não volta.

```sql estacionariedade_adf__adf
select * from quant.estacionariedade_adf__adf
```

<BarChart data={estacionariedade_adf__adf} x=nome y=estatistica_adf series=forma type=grouped title="Estatística ADF (abaixo de −2,86 = estacionária a 5%)">
  <ReferenceLine y=-2.86 label="crítico 5%"/>
</BarChart>

<DataTable data={estacionariedade_adf__adf}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so estacionariedade_adf     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Suporte e resistência por moda + clusterização](/modelos/suporte_resistencia) · [Catálogo](/catalogo) · [Regressão linear (MQO) entre ativos →](/modelos/regressao_linear)
