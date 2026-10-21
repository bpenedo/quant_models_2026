---
title: "01 · Estatística descritiva robusta"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[Catálogo](/catalogo) · [Suporte e resistência por moda + clusterização →](/modelos/suporte_resistencia)

**Tipo:** Estatístico · **Categoria:** Descrição de dados · **Fonte na base de conhecimento:** Quant Q278–289

Resume cada série por média, mediana, moda, desvio-padrão, assimetria, curtose, quantis e σ robusta (MAD). Mostra por que a média engana: o Quarteto de Anscombe tem a mesma média e a mesma reta com dados completamente diferentes. A moda dos preços arredondados revela regiões de preço frequentes, ponto de partida para suporte e resistência. É o primeiro filtro antes de qualquer modelo: quem não descreve o dado não sabe o que está modelando.

> **Leitura dos dados:** Prata tem desvio-padrão 1,6× maior que a σ robusta: poucos dias extremos inflam a volatilidade 'média' — curtose em excesso de 26,9.

```sql estatistica_descritiva__resumo
select * from quant.estatistica_descritiva__resumo
```

<BarChart data={estatistica_descritiva__resumo} x=nome y={["vol_anual_pct","sigma_robusta_anual_pct"]} type=grouped swapXY=true title="Desvio-padrão × σ robusta (% a.a.)" yFmt=num1/>

<DataTable data={estatistica_descritiva__resumo} rows=30 search=true>
  <Column id=nome title="Ativo"/><Column id=classe title="Classe"/>
  <Column id=media_anual_pct title="Retorno médio % a.a." fmt=num1/><Column id=vol_anual_pct title="Vol % a.a." fmt=num1/>
  <Column id=sigma_robusta_anual_pct title="σ robusta % a.a." fmt=num1/><Column id=curtose_excesso title="Curtose" fmt=num1/>
  <Column id=pior_dia_pct title="Pior dia %" fmt=num1/><Column id=melhor_dia_pct title="Melhor dia %" fmt=num1/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so estatistica_descritiva     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[Catálogo](/catalogo) · [Suporte e resistência por moda + clusterização →](/modelos/suporte_resistencia)
