# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Catálogo de modelos quantitativos — FONTE ÚNICA DE VERDADE.

Derivado da base de conhecimento (_private/kb/, 540 imagens únicas analisadas).
Alimenta: modelos_quant.md (raiz), o site evidence.dev (CSV) e os READMEs.

Uso:
    python3 catalogo_modelos.py            # gera modelos_quant.md + CSV do site
    python3 catalogo_modelos.py --verificar  # só valida (≤ 600 caracteres, campos, números)
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAIZ, escrever  # noqa: E402

LIMITE_DESCRICAO = 600

# Tipos (a "família" matemática) e categorias (o problema de negócio que resolve)
TIPOS = ["Estatístico", "Probabilístico", "Processamento de sinais", "Otimização",
         "Aprendizado supervisionado", "Aprendizado não supervisionado", "Aprendizado profundo",
         "Aprendizado por reforço", "PLN", "Sistemas complexos", "Governança de modelos"]
CATEGORIAS = ["Descrição de dados", "Previsão de retorno", "Previsão de direção", "Regime de mercado",
              "Risco e volatilidade", "Alocação de carteira", "Detecção de anomalias",
              "Similaridade e estrutura", "Ciclos e tendência", "Sinal alternativo",
              "Validação e monitoramento", "Regras de trading"]

# fase 1 = implementado com os dados do DataFeed (Python + Rust/WASM)
# fase 2 = catalogado; exige corpus textual, book de ofertas ou GPU (declarado como lacuna)
MODELOS: list[dict] = [
    {"id": "estatistica_descritiva", "nome": "Estatística descritiva robusta", "tipo": "Estatístico",
     "categoria": "Descrição de dados", "fase": 1, "kb": "Quant Q278–289",
     "descricao": "Resume cada série por média, mediana, moda, desvio-padrão, assimetria, curtose, quantis e σ robusta (MAD). Mostra por que a média engana: o Quarteto de Anscombe tem a mesma média e a mesma reta com dados completamente diferentes. A moda dos preços arredondados revela regiões de preço frequentes, ponto de partida para suporte e resistência. É o primeiro filtro antes de qualquer modelo: quem não descreve o dado não sabe o que está modelando."},
    {"id": "suporte_resistencia", "nome": "Suporte e resistência por moda + clusterização", "tipo": "Estatístico",
     "categoria": "Regras de trading", "fase": 1, "kb": "Quant Q284, Q288",
     "descricao": "Arredonda os preços para um passo proporcional à volatilidade, conta a frequência de cada nível (moda) e agrupa os níveis vizinhos com K-means 1D. Cada grupo vira uma faixa de suporte ou resistência com intensidade igual ao número de visitas. Substitui a linha traçada à mão no gráfico por um critério objetivo, reprodutível e auditável, que pode ser recalculado a cada pregão."},
    {"id": "estacionariedade_adf", "nome": "Estacionariedade (Augmented Dickey-Fuller)", "tipo": "Estatístico",
     "categoria": "Validação e monitoramento", "fase": 1, "kb": "Quant Q57–62, Q72, Q78, Q80",
     "descricao": "Testa se média e variância da série são constantes no tempo pelo teste ADF (regressão da diferença sobre o nível defasado e defasagens da diferença). Preços quase nunca são estacionários; retornos costumam ser. Treinar um modelo com preços é treinar com uma distribuição que não volta mais: o teste impede esse erro antes que ele vire prejuízo, e decide se a série entra no modelo em nível, em diferença ou em log-retorno."},
    {"id": "regressao_linear", "nome": "Regressão linear (MQO) entre ativos", "tipo": "Estatístico",
     "categoria": "Previsão de retorno", "fase": 1, "kb": "Quant Q15–19, Q24, Q26, Q34, Q187–195",
     "descricao": "Estima a relação y = b0 + b1·x por mínimos quadrados entre log-retornos de ativos (ex.: S&P 500 × Nasdaq, ouro × dólar). Reporta coeficientes, R², resíduos e intervalo de confiança. Mostra a transformação logarítmica que torna lineares relações exponenciais e o alerta de que correlação não implica causalidade: uma terceira variável oculta pode mover as duas. Base de beta, hedge ratio e fatores."},
    {"id": "regressao_logistica", "nome": "Regressão logística de direção", "tipo": "Aprendizado supervisionado",
     "categoria": "Previsão de direção", "fase": 1, "kb": "Quant Q16, Q44, Q45, Q52, Q54, Q63",
     "descricao": "Classifica se o próximo retorno será positivo ou negativo a partir de indicadores técnicos defasados (RSI, MACD, momentum, volatilidade), com saída em probabilidade pela função sigmoide. Treino e teste separados no tempo (walk-forward), sem vazamento de informação do futuro. É a linha de base honesta: qualquer modelo mais complexo precisa vencê-la fora da amostra para justificar sua complexidade."},
    {"id": "svm_kernels", "nome": "SVM e métodos de kernel", "tipo": "Aprendizado supervisionado",
     "categoria": "Previsão de direção", "fase": 1, "kb": "Quant Q20, Q39, Q46, Q50, Q55, Q56, Q196–224",
     "descricao": "Máquina de vetores de suporte que busca o hiperplano de margem máxima entre classes. Os kernels linear, polinomial, RBF e sigmoide projetam os dados em espaços de maior dimensão onde problemas não lineares ficam separáveis, sem criar as colunas em memória (kernel trick). Compara as quatro fronteiras de decisão sobre os mesmos dados de mercado e mostra o custo do kernel mais flexível: overfitting."},
    {"id": "arvores_random_forest", "nome": "Árvores de decisão e Random Forest", "tipo": "Aprendizado supervisionado",
     "categoria": "Previsão de direção", "fase": 1, "kb": "Quant Q145–154; Modelos [133], [160]–[172]",
     "descricao": "Regras condicionais em forma de árvore (ex.: RSI ≤ 39 e %K ≤ 4,6) que separam o espaço em degraus não lineares. A floresta aleatória combina centenas de árvores treinadas em subamostras e vota, reduzindo o overfitting de uma árvore isolada. Entrega a importância de cada indicador, o que torna a decisão explicável. Em dados tabulares, modelos de árvore seguem competitivos com redes profundas."},
    {"id": "mlp_reversao", "nome": "Rede neural MLP — indicador de reversão", "tipo": "Aprendizado profundo",
     "categoria": "Previsão de direção", "fase": 1, "kb": "Quant Q136–143, Q205–207, Q213–223",
     "descricao": "Perceptron multicamadas (duas camadas ocultas de 10 neurônios, regularização L2) treinado para prever reversões: alvo +1 quando o preço sobe 5% em 10 dias após quedas, −1 no inverso e 0 na lateralização. As entradas são eventos de Parabolic SAR, cruzamentos do RSI em 30/70 e trocas de sinal do histograma do MACD. Treino em anos passados e validação em ano nunca visto pelo modelo."},
    {"id": "pca_fatores", "nome": "PCA — fatores de risco e índices", "tipo": "Aprendizado não supervisionado",
     "categoria": "Risco e volatilidade", "fase": 1, "kb": "Quant Q22, Q25, Q27, Q31, Q38, Q245–263",
     "descricao": "Análise de componentes principais da matriz de retornos: encontra direções ortogonais de maior variância, que funcionam como fatores de risco comuns (o primeiro costuma ser o 'mercado'). Mostra a variância explicada acumulada para escolher quantos fatores manter, projeta os ativos em 2D/3D para visualizar semelhanças e permite construir índices otimizados com os ativos mais representativos de cada fator."},
    {"id": "kmeans_clusters", "nome": "Clusterização de ativos (K-means)", "tipo": "Aprendizado não supervisionado",
     "categoria": "Similaridade e estrutura", "fase": 1, "kb": "Quant Q48, Q49, Q53, Q64, Q65, Q69, Q71, Q74, Q76",
     "descricao": "Agrupa ativos com comportamento semelhante (retorno médio, volatilidade, correlação, drawdown) posicionando K centroides e atualizando-os até convergir. Escolhe K pelo método do cotovelo e pela silhueta, em vez de fixá-lo à mão. O resultado mostra que 'diversificar' entre ativos do mesmo grupo é diversificação aparente, e orienta a seleção de um representante por grupo."},
    {"id": "embedding_retornos", "nome": "Embeddings de retornos (FastICA) + cosseno", "tipo": "Aprendizado não supervisionado",
     "categoria": "Similaridade e estrutura", "fase": 1, "kb": "Quant Q120–129; Embeddings; Modelos [84]",
     "descricao": "Transforma a janela recente de retornos de cada ativo em um vetor denso de 2 dimensões por Análise de Componentes Independentes. Ativos que oscilaram de forma parecida ficam próximos no plano. A similaridade por cosseno entre vetores de retornos é uma medida alternativa de correlação, menos sensível a nível e escala, e o embedding reduz ruído antes de comparar. Atualizado a cada janela, mostra pares que se aproximam ou se afastam."},
    {"id": "isolation_forest", "nome": "Isolation Forest — retornos e volumes anormais", "tipo": "Aprendizado não supervisionado",
     "categoria": "Detecção de anomalias", "fase": 1, "kb": "Quant Q155–164; Modelos [235]",
     "descricao": "Floresta de árvores totalmente aleatórias que isola cada observação; pontos anômalos ficam em ramos curtos porque têm pouco em comum com os demais. Aplicado a retornos e volumes, marca choques de volatilidade e picos de negociação sem precisar de exemplos rotulados. No mercado, a anomalia costuma ser sinal e não ruído: indica mudança de dinâmica e é gatilho para revisar posição ou estratégia."},
    {"id": "outliers_multimetodo", "nome": "Outliers multimétodo (IQR, z-robusto, LOF)", "tipo": "Estatístico",
     "categoria": "Detecção de anomalias", "fase": 1, "kb": "Quant Q67, Q68, Q70, Q73, Q75, Q77, Q79, Q81, Q85; Modelos [130], [140]",
     "descricao": "Compara critérios de discrepância: boxplot (1,5·IQR), escore-z robusto pela mediana e MAD, e densidade local (LOF). Não existe detector ideal para todo conjunto de dados, então a decisão sai do consenso entre métodos. Mostra quanto um único outlier desloca uma regressão e separa erro de coleta (remover) de evento raro real (manter e estudar). Inclui as nove anomalias sintéticas usadas para testar detectores."},
    {"id": "markov_regimes", "nome": "Cadeia de Markov de regimes (alta, baixa, lateral)", "tipo": "Probabilístico",
     "categoria": "Regime de mercado", "fase": 1, "kb": "Quant Q0–3, Q12, Q21, Q23",
     "descricao": "Classifica cada período em alta, baixa ou lateral pelo retorno acumulado e estima a matriz de transição P[i,j]: a probabilidade de ir do regime i para o j. Responde perguntas do tipo 'estando em baixa hoje, qual a chance de estar em alta em 20 pregões?' por potências da matriz, e calcula a distribuição estacionária e a duração esperada de cada regime. Serve de filtro para ligar ou desligar estratégias."},
    {"id": "hmm_regimes", "nome": "Modelo oculto de Markov (HMM gaussiano)", "tipo": "Probabilístico",
     "categoria": "Regime de mercado", "fase": 1, "kb": "Modelos [209], [211], [212]",
     "descricao": "Os regimes não são observados: são inferidos dos retornos por um HMM gaussiano estimado pelo algoritmo EM (Baum-Welch) e decodificado por Viterbi. Cada estado tem sua própria média e volatilidade, e a literatura mostra que três estados (alta, neutro, baixa) descrevem bem ativos voláteis. Ao contrário da regra fixa de corte, o modelo aprende onde estão as fronteiras e entrega a probabilidade de cada regime a cada dia."},
    {"id": "bayes_conjugado", "nome": "Atualização bayesiana de retorno e volatilidade", "tipo": "Probabilístico",
     "categoria": "Risco e volatilidade", "fase": 1, "kb": "Quant Q4, Q6, Q9, Q18, Q30",
     "descricao": "Combina uma crença prévia (prior) com os dados novos para obter a distribuição posterior do retorno esperado e da volatilidade, pelo modelo conjugado Normal-Gama-Inversa. A cada pregão a crença é atualizada e o intervalo de credibilidade encolhe ou alarga conforme a evidência. É útil quando os dados são escassos ou mudam: responde 'quanto eu deveria confiar nesta média?' em vez de entregar um número sem incerteza."},
    {"id": "fourier_ciclos", "nome": "Transformada de Fourier — ciclos dominantes", "tipo": "Processamento de sinais",
     "categoria": "Ciclos e tendência", "fase": 1, "kb": "Quant Q7, Q10, Q11, Q13, Q14; Fourier",
     "descricao": "Decompõe a série de retornos (sem tendência) em senoides e mede a energia de cada frequência pelo periodograma da FFT. Os picos indicam ciclos dominantes em pregões, como sazonalidades semanais, mensais ou de safra. Compara o espectro com o de ruído aleatório para separar ciclo real de coincidência e reconstrói a série só com as frequências relevantes, como um filtro passa-baixa."},
    {"id": "wavelet_haar", "nome": "Wavelets — decomposição tempo-frequência", "tipo": "Processamento de sinais",
     "categoria": "Ciclos e tendência", "fase": 1, "kb": "Fourier [32], [33]; Modelos [152], [153], [155]",
     "descricao": "A transformada wavelet discreta separa o log-retorno em aproximação (baixa frequência, tendência) e detalhes (alta frequência) em vários níveis, mantendo a localização no tempo, o que Fourier não faz. Aumentos de energia nos coeficientes de detalhe antecedem mudanças de tendência, base de estudos de reversão na bolsa brasileira e de previsão de direção do S&P 500 com SVM."},
    {"id": "markowitz_fronteira", "nome": "Fronteira eficiente de Markowitz", "tipo": "Otimização",
     "categoria": "Alocação de carteira", "fase": 1, "kb": "Quant Q37, Q40, Q42, Q43, Q47, Q51; Modelos [91], [97]",
     "descricao": "Simula milhares de carteiras aleatórias e resolve a otimização média-variância para traçar a fronteira eficiente: o maior retorno esperado para cada nível de risco. Marca a carteira de mínima variância e a de máximo índice de Sharpe (tangência). Mostra visualmente que a diversificação elimina risco não sistemático, mas não o sistemático, e que escolher ativos isoladamente ignora as correlações entre eles."},
    {"id": "ag_carteira", "nome": "Algoritmo genético — otimização de carteira", "tipo": "Otimização",
     "categoria": "Alocação de carteira", "fase": 1, "kb": "Quant Q99–106, Q117; Genético",
     "descricao": "Cada indivíduo é um vetor de pesos da carteira. A aptidão é o resultado do backtest (Sharpe com penalidade de drawdown). Seleção por roleta, elitismo, crossover em ponto de corte e mutação geram novas populações até a convergência. Diferente da fórmula fechada, aceita objetivos e restrições arbitrárias (custos, limites por ativo, cardinalidade). Avalia o melhor indivíduo fora da amostra para não premiar sobreajuste."},
    {"id": "ag_indicadores", "nome": "Algoritmo genético — seleção de indicadores e parâmetros", "tipo": "Otimização",
     "categoria": "Regras de trading", "fase": 1, "kb": "Genético [41]",
     "descricao": "Busca a combinação de indicadores técnicos e seus parâmetros (períodos de médias, limiares de RSI, janelas de rompimento) que maximiza o desempenho de uma regra de trading no período de treino. O cromossomo codifica liga/desliga de cada indicador e seus parâmetros. O resultado é validado em período posterior, e o número de regras testadas é registrado para dimensionar o risco de mineração de dados."},
    {"id": "programacao_genetica", "nome": "Programação genética — regressão simbólica", "tipo": "Otimização",
     "categoria": "Previsão de retorno", "fase": 1, "kb": "Quant Q107–109, Q111–113, Q115, Q116, Q118; Genético [40], [42]",
     "descricao": "Os indivíduos são árvores de operações (+, −, ×, ÷, seno, cosseno, máximo) sobre os últimos retornos. A evolução por seleção, crossover de subárvores e mutação procura a fórmula que melhor estima o próximo retorno, com penalidade por tamanho da árvore (parcimônia) para evitar fórmulas gigantes. Cria indicadores novos e legíveis, em vez de combinar os que todo o mercado já usa."},
    {"id": "hurst_movel", "nome": "Expoente de Hurst e indicador Hurst móvel", "tipo": "Sistemas complexos",
     "categoria": "Ciclos e tendência", "fase": 1, "kb": "Modelos [247], [249]",
     "descricao": "O expoente de Hurst (análise R/S) mede memória da série: H > 0,5 indica persistência (tendência), H < 0,5 reversão à média e H ≈ 0,5 passeio aleatório. Calculado em janelas móveis de 100 e 150 pregões, a diferença MH100 − MH150 vira um sinal de compra e venda alternativo ao cruzamento de médias móveis, informando qual tipo de estratégia faz sentido no regime atual."},
    {"id": "sistemas_nao_lineares", "nome": "Dinâmica não linear e caudas pesadas", "tipo": "Sistemas complexos",
     "categoria": "Risco e volatilidade", "fase": 1, "kb": "Quant Q28, Q29, Q32, Q33, Q35, Q41; Modelos [66], [67]",
     "descricao": "Compara a distribuição real dos retornos com a normal: caudas pesadas, assimetria e agrupamento de volatilidade mostram que o mercado é um sistema dinâmico não linear, em que pequenas mudanças produzem grandes efeitos. Mede curtose, quantis extremos e a autocorrelação dos retornos absolutos, e explica por que modelos que assumem normalidade subestimam cisnes negros e quebras de estratégia."},
    {"id": "garch_volatilidade", "nome": "Volatilidade condicional (EWMA e GARCH(1,1))", "tipo": "Estatístico",
     "categoria": "Risco e volatilidade", "fase": 1, "kb": "Modelos [69], [78], [185]",
     "descricao": "Modela o agrupamento de volatilidade: dias agitados seguem dias agitados. O EWMA (RiskMetrics) e o GARCH(1,1), estimado por máxima verossimilhança, projetam a volatilidade do próximo pregão e o VaR/Expected Shortfall a 99%. Serve para dimensionar posição, ajustar stops e monitorar se a volatilidade dos retornos do modelo permanece estacionária ou começa a mudar de patamar."},
    {"id": "rede_correlacao", "nome": "Rede de correlação e centralidade", "tipo": "Sistemas complexos",
     "categoria": "Similaridade e estrutura", "fase": 1, "kb": "Curso Laboratório da Bolsa [1]–[5]; Quant Q76",
     "descricao": "Inspirado na Lazy Network (rede temporal construída por similaridade de documentos 10-K), constrói uma rede em que os ativos são nós e as arestas são correlações fortes, filtrada pela árvore geradora mínima. Calcula as centralidades de força, autovetor, proximidade e intermediação. Ativos periféricos tendem a carregar risco mais idiossincrático; a carteira dos periféricos é comparada com a carteira igualmente ponderada."},
    {"id": "causalidade_granger", "nome": "Causalidade de Granger e contágio", "tipo": "Estatístico",
     "categoria": "Similaridade e estrutura", "fase": 1, "kb": "Modelos [148], [150], [157]",
     "descricao": "Testa se o passado de um ativo melhora a previsão de outro além do próprio passado deste (teste F em regressões com defasagens). Constrói o grafo direcionado de 'quem antecede quem' entre dólar, juros, metais, energia e bolsas. Distingue correlação de precedência temporal, como no caso da quebra do SVB: os ativos caíram juntos, mas só um teste causal indica se um evento propagou para o outro."},
    {"id": "drift_modelo", "nome": "Detecção de drift de modelo e de conceito", "tipo": "Governança de modelos",
     "categoria": "Validação e monitoramento", "fase": 1, "kb": "Modelos [51], [52], [185], [188], [189], [226], [227]",
     "descricao": "Monitora o modelo em produção: compara a distribuição recente das entradas e dos erros com a do treino (teste de Kolmogorov-Smirnov e índice de estabilidade populacional) e acompanha a acurácia em janela móvel. Classifica o drift em súbito, gradual, incremental ou recorrente. A degradação costuma aparecer antes das perdas financeiras, por isso o alerta é o gatilho para retreinar ou desligar a estratégia."},
    {"id": "backtest_walkforward", "nome": "Backtest walk-forward com custos", "tipo": "Governança de modelos",
     "categoria": "Validação e monitoramento", "fase": 1, "kb": "Modelos [80], [85], [154], [158], [186], [230]–[233]",
     "descricao": "Motor de backtest vetorizado com janelas de treino e teste que avançam no tempo, custos de transação e slippage, e métricas de desempenho (CAGR, volatilidade, Sharpe, Sortino, drawdown máximo, taxa de acerto). Inclui os portões de parada do pipeline quant: estratégia que falha em robustez ou em período fora da amostra é descartada. Combate vazamento de dados, overfitting e cherrypicking de resultados."},
    {"id": "triple_barrier_ou", "nome": "Regras ótimas de trading (Ornstein-Uhlenbeck)", "tipo": "Probabilístico",
     "categoria": "Regras de trading", "fase": 1, "kb": "Modelos [161]",
     "descricao": "Ajusta um processo de Ornstein-Uhlenbeck (reversão à média) à série e, por Monte Carlo, simula milhares de trajetórias para cada par de alvo de lucro e stop-loss, com período máximo de manutenção. O resultado é uma malha de índices de Sharpe que mostra a combinação ótima de saída. Substitui o 'stop de 2%' arbitrário por uma regra derivada da dinâmica estimada do próprio ativo."},
    {"id": "benford", "nome": "Lei de Newcomb-Benford — integridade de dados", "tipo": "Estatístico",
     "categoria": "Detecção de anomalias", "fase": 1, "kb": "Modelos [98]",
     "descricao": "Em muitos conjuntos de números reais, o primeiro dígito segue a lei de Benford (o dígito 1 aparece em cerca de 30% dos casos). Compara a distribuição observada dos primeiros dígitos de volumes e valores com a teórica pelo qui-quadrado e pela MAD de Nigrini. Desvios fortes sinalizam dados fabricados, arredondados ou corrompidos: um teste barato de auditoria antes de confiar na base de dados."},
    {"id": "shap_explicabilidade", "nome": "Explicabilidade com valores de Shapley (SHAP)", "tipo": "Governança de modelos",
     "categoria": "Validação e monitoramento", "fase": 1, "kb": "Modelos [74], [100], [101], [113], [120], [129]",
     "descricao": "Abre a caixa-preta: para cada previsão, distribui a contribuição de cada variável de entrada segundo os valores de Shapley da teoria dos jogos, com sinal (empurra para cima ou para baixo) e magnitude. Mostra o compromisso entre poder preditivo e interpretabilidade e permite responder 'por que o modelo mandou comprar hoje?' com indicadores e patamares concretos, requisito para auditoria e para confiança do decisor."},
    {"id": "lstm_sequencias", "nome": "LSTM para sequências de candles", "tipo": "Aprendizado profundo",
     "categoria": "Previsão de retorno", "fase": 2, "kb": "Quant Q144; Modelos [132], [138], [141], [145]",
     "descricao": "Rede recorrente com portões de entrada, esquecimento e saída que preserva dependências longas em sequências de retornos, volumes e indicadores. Catalogada com arquitetura e protocolo de validação; a implementação completa fica na fase 2 porque o ganho sobre árvores e modelos lineares em dados tabulares diários é pequeno e o custo de treino exige GPU para varrer hiperparâmetros com honestidade."},
    {"id": "sentimento", "nome": "Análise de sentimento (léxico, ML, BERT, LLM)", "tipo": "PLN",
     "categoria": "Sinal alternativo", "fase": 2, "kb": "Quant Q5, Q58, Q66, Q82–89; Modelos [110], [116]",
     "descricao": "Classifica notícias e postagens em positivo, neutro ou negativo por quatro caminhos de complexidade crescente: léxico de polaridade, classificador supervisionado sobre TF-IDF, BERT ajustado ao domínio financeiro e LLM com instrução zero/few-shot. O saldo diário de sentimento vira sinal alternativo, descorrelacionado dos indicadores de preço que todo o mercado já usa. Exige corpus de notícias (fase 2)."},
    {"id": "topicos_lda_nmf", "nome": "Modelagem de tópicos (LDA e NMF)", "tipo": "PLN",
     "categoria": "Sinal alternativo", "fase": 2, "kb": "Quant Q90–97; Modelos [44], [47], [55], [58]",
     "descricao": "Descobre automaticamente os assuntos de um conjunto de textos: o LDA modela documentos como misturas de tópicos e tópicos como distribuições de palavras; a NMF fatora a matriz texto × palavra em texto × tópico e tópico × palavra. Acompanha a evolução dos tópicos no tempo e gera nuvens de palavras, permitindo saber o que move o mercado sem ler centenas de notícias. Exige corpus textual (fase 2)."},
    {"id": "word_embeddings_copom", "nome": "Word embeddings e atas do COPOM", "tipo": "PLN",
     "categoria": "Sinal alternativo", "fase": 2, "kb": "Quant Q98, Q110, Q114, Q119, Q130–134, Q167, Q170, Q179–186",
     "descricao": "Treina vetores de palavras (word2vec skip-gram/CBOW, FastText) com textos do mercado e atas do COPOM. Palavras de sentido próximo ficam próximas no espaço e permitem analogias vetoriais (Brasil − país + Ásia ≈ China). Mede a similaridade entre atas sucessivas para detectar mudança de tom da política monetária e encontrar termos associados a inflação e juros. Exige o corpus das atas (fase 2)."},
    {"id": "tfidf_pca_textos", "nome": "Embeddings textuais com TF-IDF + PCA", "tipo": "PLN",
     "categoria": "Similaridade e estrutura", "fase": 2, "kb": "Quant Q264–277",
     "descricao": "Vetoriza parágrafos com TF-IDF de n-gramas (milhares de colunas esparsas) e projeta em 250 componentes por PCA, obtendo vetores densos que preservam o significado. Dois textos sobre o mesmo assunto com palavras diferentes passam a ter alta similaridade por cosseno, o que o TF-IDF puro não capta. Alternativa local, rápida e sem custo por chamada aos LLMs para buscar, comparar e agrupar notícias."},
    {"id": "lazy_network_10k", "nome": "Lazy Network — rede de documentos 10-K", "tipo": "PLN",
     "categoria": "Sinal alternativo", "fase": 2, "kb": "Curso Laboratório da Bolsa [1]–[5]",
     "descricao": "Gera embeddings Doc2Vec dos relatórios anuais 10-K, mede a mudança de cada empresa entre anos pela similaridade por cosseno e monta uma rede temporal entre empresas. Centralidades de força, autovetor, proximidade e intermediação selecionam as 50 empresas mais periféricas, cuja carteira gerou alfa sobre CAPM e modelos de 3 e 5 fatores no estudo original. Exige o corpus SEC/CVM (fase 2)."},
    {"id": "rl_trading", "nome": "Aprendizado por reforço profundo para trading", "tipo": "Aprendizado por reforço",
     "categoria": "Alocação de carteira", "fase": 2, "kb": "Modelos [74], [222], [242], [243]",
     "descricao": "Modela o trading como processo de decisão de Markov: estado = preços, posições e caixa; ação = comprar, vender ou manter k unidades; recompensa = variação do valor da carteira. Agentes de política e de valor aprendem por tentativa e erro em simulador com custos, e a distilação de vários professores estabiliza o treino em ambiente ruidoso. Catalogado com o ambiente; o treino robusto fica na fase 2."},
    {"id": "simulacao_multiagente", "nome": "Simulação multiagente de flash crash", "tipo": "Sistemas complexos",
     "categoria": "Risco e volatilidade", "fase": 2, "kb": "Modelos [54], [57], [59], [89], [107]",
     "descricao": "Simula um livro de ofertas com agentes heterogêneos (formadores de mercado, seguidores de tendência, investidores fundamentalistas e robôs de alta frequência) para reproduzir quedas abruptas em milissegundos causadas pela reação recursiva de algoritmos uns aos outros. Permite testar regras de mercado, como circuit breakers, e entender efeitos emergentes que nenhum modelo de um único ativo captura."},
]


def verificar() -> list[str]:
    erros = []
    ids = set()
    for i, m in enumerate(MODELOS, start=1):
        for campo in ("id", "nome", "tipo", "categoria", "fase", "kb", "descricao"):
            if not m.get(campo):
                erros.append(f"modelo {i}: campo '{campo}' ausente")
        if m["id"] in ids:
            erros.append(f"modelo {i}: id duplicado {m['id']}")
        ids.add(m["id"])
        if len(m["descricao"]) > LIMITE_DESCRICAO:
            erros.append(f"modelo {i} ({m['id']}): descrição com {len(m['descricao'])} > {LIMITE_DESCRICAO} caracteres")
        if m["tipo"] not in TIPOS:
            erros.append(f"modelo {i}: tipo desconhecido '{m['tipo']}'")
        if m["categoria"] not in CATEGORIAS:
            erros.append(f"modelo {i}: categoria desconhecida '{m['categoria']}'")
    return erros


def gerar_markdown() -> str:
    f1 = sum(1 for m in MODELOS if m["fase"] == 1)
    linhas = [
        "<!--\nquant_models_2026\nAutor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS\n"
        "E-mail: profbruanbima@gmail.com\n-->",
        "",
        "# 📚 Catálogo de Modelos Quantitativos — `modelos_quant.md`",
        "",
        f"> **{len(MODELOS)} modelos** extraídos da base de conhecimento do projeto. "
        f"**{f1} implementados** em Python (numba + `ProcessPoolExecutor`) com segundo motor em Rust/WASM, "
        f"aplicados aos dados do DataFeed; **{len(MODELOS) - f1} catalogados** para a fase 2.",
        ">",
        "> Arquivo **gerado** por `public/foundations/pipeline/catalogo_modelos.py` — edite lá, nunca aqui.",
        "",
        "## Resumo",
        "",
        "| Nº | Modelo | Tipo | Categoria | Fase |",
        "|---:|---|---|---|:---:|",
    ]
    for i, m in enumerate(MODELOS, start=1):
        linhas.append(f"| {i:02d} | [{m['nome']}](#m{i:02d}) | {m['tipo']} | {m['categoria']} | "
                      f"{'✅ 1' if m['fase'] == 1 else '🗂️ 2'} |")
    linhas += ["", "## Fichas", ""]
    for i, m in enumerate(MODELOS, start=1):
        linhas += [
            f'<a id="m{i:02d}"></a>',
            f"### {i:02d} · {m['nome']}",
            "",
            f"**Tipo:** {m['tipo']} · **Categoria:** {m['categoria']} · "
            f"**Fase:** {'1 — implementado' if m['fase'] == 1 else '2 — catalogado'} · "
            f"**Fonte na KB:** {m['kb']} · **ID:** `{m['id']}`",
            "",
            m["descricao"],
            "",
        ]
    linhas += ["---", "",
               "_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 — TODOS OS DIREITOS RESERVADOS · "
               "profbruanbima@gmail.com_", ""]
    return "\n".join(linhas)


def gerar_csv(destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["numero", "id", "nome", "tipo", "categoria", "fase", "fonte_kb", "descricao"])
        for i, m in enumerate(MODELOS, start=1):
            w.writerow([i, m["id"], m["nome"], m["tipo"], m["categoria"], m["fase"], m["kb"], m["descricao"]])


def main() -> int:
    ap = argparse.ArgumentParser(description="Catálogo de modelos quantitativos.")
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    erros = verificar()
    if erros:
        print("❌ Catálogo inválido:")
        for e in erros:
            print("   •", e)
        return 1
    maior = max(len(m["descricao"]) for m in MODELOS)
    print(f"✅ {len(MODELOS)} modelos válidos · maior descrição: {maior} caracteres (limite {LIMITE_DESCRICAO})")
    if a.verificar:
        return 0
    escrever(RAIZ / "modelos_quant.md", gerar_markdown())
    gerar_csv(RAIZ / "public/foundations/evidence/dados/quant/catalogo_modelos.csv")
    print(f"📄 {RAIZ / 'modelos_quant.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
