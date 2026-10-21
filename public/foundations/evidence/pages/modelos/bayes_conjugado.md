---
title: "16 · Atualização bayesiana de retorno e volatilidade"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Modelo oculto de Markov (HMM gaussiano)](/modelos/hmm_regimes) · [Catálogo](/catalogo) · [Transformada de Fourier — ciclos dominantes →](/modelos/fourier_ciclos)

**Tipo:** Probabilístico · **Categoria:** Risco e volatilidade · **Fonte na base de conhecimento:** Quant Q4, Q6, Q9, Q18, Q30

Combina uma crença prévia (prior) com os dados novos para obter a distribuição posterior do retorno esperado e da volatilidade, pelo modelo conjugado Normal-Gama-Inversa. A cada pregão a crença é atualizada e o intervalo de credibilidade encolhe ou alarga conforme a evidência. É útil quando os dados são escassos ou mudam: responde 'quanto eu deveria confiar nesta média?' em vez de entregar um número sem incerteza.

> **Leitura dos dados:** Ouro desde 2019: o retorno médio anual a posteriori é 15,3%, mas o intervalo de credibilidade de 95% vai de 2,3% a 28,4%. A probabilidade de a média ser positiva é 98,9% — a média amostral (15,7%) sozinha não diz isso.

```sql bayes_conjugado__posterior
select * from quant.bayes_conjugado__posterior
```

<LineChart data={bayes_conjugado__posterior} x=data y={["ic95_inf_anual_pct","media_post_anual_pct","ic95_sup_anual_pct"]} title="Ouro — retorno médio anual a posteriori e credibilidade 95% (%)" yMin=-60 yMax=80/>
<LineChart data={bayes_conjugado__posterior} x=data y=p_media_positiva yFmt=pct0 title="Probabilidade de a média ser positiva"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so bayes_conjugado     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Modelo oculto de Markov (HMM gaussiano)](/modelos/hmm_regimes) · [Catálogo](/catalogo) · [Transformada de Fourier — ciclos dominantes →](/modelos/fourier_ciclos)
