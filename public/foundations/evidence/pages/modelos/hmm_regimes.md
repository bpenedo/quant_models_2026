---
title: "15 · Modelo oculto de Markov (HMM gaussiano)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Cadeia de Markov de regimes (alta, baixa, lateral)](/modelos/markov_regimes) · [Catálogo](/catalogo) · [Atualização bayesiana de retorno e volatilidade →](/modelos/bayes_conjugado)

**Tipo:** Probabilístico · **Categoria:** Regime de mercado · **Fonte na base de conhecimento:** Modelos [209], [211], [212]

Os regimes não são observados: são inferidos dos retornos por um HMM gaussiano estimado pelo algoritmo EM (Baum-Welch) e decodificado por Viterbi. Cada estado tem sua própria média e volatilidade, e a literatura mostra que três estados (alta, neutro, baixa) descrevem bem ativos voláteis. Ao contrário da regra fixa de corte, o modelo aprende onde estão as fronteiras e entrega a probabilidade de cada regime a cada dia.

> **Leitura dos dados:** Sem regra de corte arbitrária, o HMM encontra três regimes no S&P 500: o turbulento tem volatilidade de 43% ao ano contra 7% no calmo e dura em média 18 pregões. Hoje o regime mais provável é 'calmo'.

```sql hmm_regimes__estados
select * from quant.hmm_regimes__estados
```
```sql hmm_regimes__probabilidades
select * from quant.hmm_regimes__probabilidades
```

<AreaChart data={hmm_regimes__probabilidades} x=data y={["p_calmo","p_normal","p_turbulento"]} yFmt=pct0 title="Probabilidade de cada regime — S&P 500"/>
<DataTable data={hmm_regimes__estados}>
  <Column id=estado/><Column id=media_diaria_pct title="Média diária %" fmt=num3/><Column id=vol_anual_pct title="Vol % a.a." fmt=num1/>
  <Column id=duracao_media_pregoes title="Duração (pregões)" fmt=num0/><Column id=fracao_tempo title="Fração do tempo" fmt=pct1/>
</DataTable>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so hmm_regimes     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Cadeia de Markov de regimes (alta, baixa, lateral)](/modelos/markov_regimes) · [Catálogo](/catalogo) · [Atualização bayesiana de retorno e volatilidade →](/modelos/bayes_conjugado)
