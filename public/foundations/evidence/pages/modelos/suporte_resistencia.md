---
title: "02 · Suporte e resistência por moda + clusterização"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Estatística descritiva robusta](/modelos/estatistica_descritiva) · [Catálogo](/catalogo) · [Estacionariedade (Augmented Dickey-Fuller) →](/modelos/estacionariedade_adf)

**Tipo:** Estatístico · **Categoria:** Regras de trading · **Fonte na base de conhecimento:** Quant Q284, Q288

Arredonda os preços para um passo proporcional à volatilidade, conta a frequência de cada nível (moda) e agrupa os níveis vizinhos com K-means 1D. Cada grupo vira uma faixa de suporte ou resistência com intensidade igual ao número de visitas. Substitui a linha traçada à mão no gráfico por um critério objetivo, reprodutível e auditável, que pode ser recalculado a cada pregão.

> **Leitura dos dados:** Ouro: a moda dos preços arredondados é 3.330,00; a faixa mais visitada (2.350,00–2.730,00) concentra 24% dos pregões e hoje atua como suporte.

```sql suporte_resistencia__preco
select * from quant.suporte_resistencia__preco
```
```sql suporte_resistencia__faixas
select * from quant.suporte_resistencia__faixas
```

<LineChart data={suporte_resistencia__preco} x=data y=fechamento title="Ouro — 2 anos" yFmt=num0>
{#each suporte_resistencia__faixas as f}
  <ReferenceArea yMin={f.minimo} yMax={f.maximo} color={f.tipo === 'suporte' ? 'positive' : 'negative'} label="{f.tipo} · {Math.round(f.intensidade_pct)}%"/>
{/each}
</LineChart>

<DataTable data={suporte_resistencia__faixas}/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so suporte_resistencia     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Estatística descritiva robusta](/modelos/estatistica_descritiva) · [Catálogo](/catalogo) · [Estacionariedade (Augmented Dickey-Fuller) →](/modelos/estacionariedade_adf)
