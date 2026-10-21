---
title: Quant Models 2026
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 **Português** · [English](/en) · [Español](/es) · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

# Pare de decidir por planilha. Comece a decidir por modelo.

> Uma planilha ordena, filtra e soma — e em nenhum momento pergunta **quanto do que você vê é ruído**.
> Aqui, 32 modelos quantitativos rodam sobre 27 ativos reais (2010–2026) e cada um mostra, com o dado,
> **onde a intuição engana**: a acurácia que é só a taxa-base, o ótimo que não sobrevive ao futuro, a memória
> longa que é viés do estimador, a "diversificação" que é rótulo.

```sql totais
select (select count(*) from quant.catalogo_modelos) as catalogo, (select count(*) from quant.resumo_modelos) as implementados, (select max(linhas) from quant.resumo_modelos) as maior_tabela
```

<BigValue data={totais} value=catalogo title="Modelos no catálogo"/>
<BigValue data={totais} value=implementados title="Rodando sobre dados reais"/>

## As leituras — uma frase por modelo

| Nº | Modelo | Categoria | O que o dado mostrou |
|---:|---|---|---|
| 01 | [Estatística descritiva robusta](/modelos/estatistica_descritiva) | Descrição de dados | Prata tem desvio-padrão 1,6× maior que a σ robusta: poucos dias extremos inflam a volatilidade 'média' — curtose em excesso de 26,9. |
| 02 | [Suporte e resistência por moda + clusterização](/modelos/suporte_resistencia) | Regras de trading | Ouro: a moda dos preços arredondados é 3.330,00; a faixa mais visitada (2.350,00–2.730,00) concentra 24% dos pregões e hoje atua como suporte. |
| 03 | [Estacionariedade (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | Validação e monitoramento | 1 de 8 séries de preço são estacionárias a 5%; em log-retorno, 8 de 8. Treinar com preço é treinar com uma distribuição que não volta. |
| 04 | [Regressão linear (MQO) entre ativos](/modelos/regressao_linear) | Previsão de retorno | Dow Jones ~ S&P 500: β = 0,91 com R² = 0,91. Já Treasury americano ~ S&P 500 tem R² de 0,04: a relação 'óbvia' explica quase nada do dia a dia. |
| 05 | [Regressão logística de direção](/modelos/regressao_logistica) | Previsão de direção | Fora da amostra (2016–2026) a logística acerta 54,2% da direção do S&P 500 — praticamente a fração de dias de alta (54,2%): previu alta em 98% dos dias e tem AUC 0,492. Acurácia alta sem poder de separação é a armadilha que esta linha de base desarma. |
| 06 | [SVM e métodos de kernel](/modelos/svm_kernels) | Previsão de direção | Com só RSI e volatilidade como entradas, nenhum dos quatro kernels passa de 50,7% de acurácia balanceada fora da amostra. O RBF é o que mais 'aprende' no treino (53,2%) e o que mais perde no teste (48,4%): kernel não cria sinal onde ele não existe. |
| 07 | [Árvores de decisão e Random Forest](/modelos/arvores_random_forest) | Previsão de direção | Árvore com profundidade 20 acerta 83,7% no treino e 49,8% no teste: decorou o passado. A floresta rasa fica em 53,5% — modesta, mas honesta; o atributo mais usado é 'ret_1'. |
| 08 | [Rede neural MLP — indicador de reversão](/modelos/mlp_reversao) | Previsão de direção | Na prata, em 2023–2026 (nunca vistos no treino), a MLP emitiu 607 sinais de reversão de alta com precisão de 17,3%, contra taxa base de 13,6% (1,27× a frequência natural): é essa razão, e não a acurácia geral, que diz se o indicador agrega informação. |
| 09 | [PCA — fatores de risco e índices](/modelos/pca_fatores) | Risco e volatilidade | O 1º fator sozinho explica 24,5% da variação diária de 27 ativos; são precisos 12 fatores para chegar a 80%. Os 27 ativos não são 27 apostas independentes. |
| 10 | [Clusterização de ativos (K-means)](/modelos/kmeans_clusters) | Similaridade e estrutura | A silhueta escolhe K = 4 grupos sem intervenção manual; há grupo que mistura 3 classes de ativo diferentes — o rótulo 'commodity' ou 'câmbio' não diz como o ativo se comporta. |
| 11 | [Embeddings de retornos (FastICA) + cosseno](/modelos/embedding_retornos) | Similaridade e estrutura | Nos últimos 60 pregões, o par mais parecido é Petróleo Brent × Petróleo WTI (cosseno 0,96) e o mais oposto é Índice do dólar × Euro/Dólar (-0,89): um mapa de proximidade que se atualiza a cada janela. |
| 12 | [Isolation Forest — retornos e volumes anormais](/modelos/isolation_forest) | Detecção de anomalias | Sem nenhum rótulo, a floresta de isolamento marca 77 pregões do S&P 500 como anômalos — 21 só em 2020 — e 57% deles são quedas: a anomalia é sinal de mudança de dinâmica, não ruído a descartar. |
| 13 | [Outliers multimétodo (IQR, z-robusto, LOF)](/modelos/outliers_multimetodo) | Detecção de anomalias | No S&P 500, o boxplot marca 264 dias como outlier (6,7% da amostra); o consenso de três métodos fica com 101. Um único ponto discrepante muda a inclinação da reta de 0,76 para 0,53. |
| 14 | [Cadeia de Markov de regimes (alta, baixa, lateral)](/modelos/markov_regimes) | Regime de mercado | No S&P 500, estando em baixa em um bloco de 20 pregões, a chance de o próximo bloco ser de alta é 59,0% — maior que a de continuar em baixa (30,8%). Em equilíbrio, o mercado passa 41,3% do tempo em regime de alta. |
| 15 | [Modelo oculto de Markov (HMM gaussiano)](/modelos/hmm_regimes) | Regime de mercado | Sem regra de corte arbitrária, o HMM encontra três regimes no S&P 500: o turbulento tem volatilidade de 43% ao ano contra 7% no calmo e dura em média 18 pregões. Hoje o regime mais provável é 'calmo'. |
| 16 | [Atualização bayesiana de retorno e volatilidade](/modelos/bayes_conjugado) | Risco e volatilidade | Ouro desde 2019: o retorno médio anual a posteriori é 15,3%, mas o intervalo de credibilidade de 95% vai de 2,3% a 28,4%. A probabilidade de a média ser positiva é 98,9% — a média amostral (15,7%) sozinha não diz isso. |
| 17 | [Transformada de Fourier — ciclos dominantes](/modelos/fourier_ciclos) | Ciclos e tendência | Dos 12 maiores picos de ciclo nos quatro ativos, só 2 superam o limiar de ruído de 95% obtido embaralhando os próprios retornos. Todo periodograma tem picos; o teste diz quais são ciclo e quais são acaso. |
| 18 | [Wavelets — decomposição tempo-frequência](/modelos/wavelet_haar) | Ciclos e tendência | O nível 1 (oscilações de 2 pregões) concentra 55,0% da energia do S&P 500. Quando a energia de alta frequência explode (z {">"} 2), a dispersão do retorno dos 20 pregões seguintes é 1,3× a normal: a wavelet localiza no tempo o que Fourier só vê na média. |
| 19 | [Fronteira eficiente de Markowitz](/modelos/markowitz_fronteira) | Alocação de carteira | A carteira de máximo Sharpe tinha Sharpe 1,19 em 2010–2019 e entregou 0,76 em 2020–2026; os pesos iguais foram de 0,35 para 0,94. A fronteira é exata sobre o passado — o erro está na estimativa de médias que o futuro não repete. |
| 20 | [Algoritmo genético — otimização de carteira](/modelos/ag_carteira) | Alocação de carteira | Quatro rodadas paralelas do AG, com sementes diferentes, convergem para a mesma carteira (desvio médio de peso de 0,1 p.p.) com Sharpe de 1,19 em 2010–2019. Em 2020–2026 ela entrega 0,86, abaixo dos pesos iguais (0,94): convergência prova que o ótimo é estável, não que o futuro vai repeti-lo. |
| 21 | [Algoritmo genético — seleção de indicadores e parâmetros](/modelos/ag_indicadores) | Regras de trading | O AG testou 1826 regras distintas no S&P 500 e a melhor de cada rodada teve Sharpe de treino até 0,78; em 2019–2026 elas ficaram entre 0,41 e 0,54, contra 0,77 de simplesmente ficar comprado. Quanto mais regras se testa, maior o Sharpe de treino por puro acaso. |
| 22 | [Programação genética — regressão simbólica](/modelos/programacao_genetica) | Previsão de retorno | A programação genética descobriu fórmulas legíveis como ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 nós), com correlação de postos de -0,080 com o próximo retorno no treino e -0,028 no teste. A evolução sempre encontra 'algo' no passado; só o período nunca visto separa indicador de coincidência. |
| 23 | [Expoente de Hurst e indicador Hurst móvel](/modelos/hurst_movel) | Ciclos e tendência | O H bruto de R/S fica entre 0,54 e 0,59 e pareceria 'persistente'; contra séries embaralhadas, nenhum dos 6 ativos mostra memória real. O cruzamento MH100 − MH150 supera o de médias móveis em 3 de 6 ativos pelo índice de Sharpe. |
| 24 | [Dinâmica não linear e caudas pesadas](/modelos/sistemas_nao_lineares) | Risco e volatilidade | Movimentos de 4 desvios acontecem, em mediana, 64× mais do que a curva normal prevê; o retorno quase não tem memória (autocorrelação -0,02), mas o tamanho do movimento tem (0,15). |
| 25 | [Volatilidade condicional (EWMA e GARCH(1,1))](/modelos/garch_volatilidade) | Risco e volatilidade | S&P 500: persistência α+β = 0,963 — um choque de volatilidade leva 18 pregões para perder metade da força. VaR 99% de 1 dia: 1,75%. |
| 26 | [Rede de correlação e centralidade](/modelos/rede_correlacao) | Similaridade e estrutura | Escolhidos pela rede de 2010–2019, os 8 periféricos seguiram quase independentes em 2020–2026 (correlação média 0,00 contra 0,15 dos centrais) e renderam mais (11,0% contra 7,4% a.a.), porém com mais volatilidade. Quem venceu as duas cestas foi a carteira com os 27 (Sharpe 0,95): número de apostas independentes pesa mais que a posição na rede. |
| 27 | [Causalidade de Granger e contágio](/modelos/causalidade_granger) | Similaridade e estrutura | Dos 72 pares testados, 7 sobrevivem à correção de Bonferroni. O mais forte, Euro/Dólar → Índice do dólar, é artefato de horário de fechamento entre fontes diferentes: precedência estatística não é causa — e o teste mostra exatamente onde a intuição seria enganada. |
| 28 | [Detecção de drift de modelo e de conceito](/modelos/drift_modelo) | Validação e monitoramento | O modelo treinado em 2010–2016 pede retreino em 8 dos 10 anos seguintes: o regime de entrada daquele período não voltou. 2022 teve a pior acurácia (43,8%) e 2017 o maior deslocamento (KS 0,77) — monitorar a entrada mostra o problema sem esperar a perda. |
| 29 | [Backtest walk-forward com custos](/modelos/backtest_walkforward) | Validação e monitoramento | Com custos de 5 bps por giro, 2 de 4 estratégias passam pelos três portões STOP (Pesos iguais, Paridade de risco). A janela do momentum, escolhida a cada mês só com o passado, mudou 45 vezes — o 'parâmetro ótimo' não é constante. |
| 30 | [Regras ótimas de trading (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | Regras de trading | O spread Brent − WTI reverte à média com meia-vida de 22 pregões. Simulando 4.000 trajetórias por célula, a melhor regra é alvo de 1,5σ com stop de 10,0σ (Sharpe por operação 0,63) — um stop percentual fixo ignora a dinâmica do ativo. |
| 31 | [Lei de Newcomb-Benford — integridade de dados](/modelos/benford) | Detecção de anomalias | Só 21 das 29 séries de volume cobrem amplitude suficiente para o teste; aplicar Benford às demais seria falso alarme. Agregados, os volumes cobrem 6,4 ordens de grandeza e dão MAD de 0,0099 (conformidade aceitável). |
| 32 | [Explicabilidade com valores de Shapley (SHAP)](/modelos/shap_explicabilidade) | Validação e monitoramento | Na última previsão, a probabilidade de alta sai de 54,0% (média do modelo) para 55,4%; o atributo que mais pesou foi 'ret_1' (+1,0 p.p.). A caixa-preta passa a responder 'por quê'. |

## Explore

- [Catálogo completo (40 modelos)](/catalogo)
- [Laboratório no navegador (WebAssembly)](/laboratorio)
- [Três motores, um resultado (Python/numba · Rust · F#)](/motores)

---

_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 — TODOS OS DIREITOS RESERVADOS · profbruanbima@gmail.com_
