---
title: "quant_models_2026 — 40 quantitative models for deciding under uncertainty"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · **English** · [Español](/es) · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Stop choosing by spreadsheet. Start deciding by model.

**32 models running on 16 years of real data, three engines (Python, Rust and F#) that agree bit for bit, and a lab that runs in your browser — each one showing, with the data, where intuition misleads.**

> You have done this. You built a spreadsheet of alternatives — suppliers, phones for the team, electric cars for the fleet, assets for the portfolio, aircraft for a squadron —, scored each criterion, weighted them, sorted from highest to lowest and took the winner to the meeting. The spreadsheet was right. The decision was not.
>
> **The spreadsheet does not get the arithmetic wrong. It gets the question wrong.**

Spreadsheets, scoring matrices and ranking filters treat every number as certain. None of them asks how much of what you see is noise, whether the past still represents the future, or whether your 'best option' would survive a period it has never seen.

## The 32 models, one by one

| # | Model | What the data showed: |
|---:|---|---|
| 01 | [Robust descriptive statistics](/modelos/estatistica_descritiva) | Silver has a standard deviation 1.6× larger than its robust σ: a few extreme days inflate the 'average' volatility — excess kurtosis of 26.9. |
| 02 | [Support and resistance by mode + clustering](/modelos/suporte_resistencia) | Gold: the mode of rounded prices is 3,330.00; the most visited band (2,350.00–2,730.00) holds 24% of the sessions and now acts as support. |
| 03 | [Stationarity (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | 1 of 8 price series is stationary at 5%; in log returns, 8 of 8. Training on prices is training on a distribution that does not come back. |
| 04 | [Linear regression (OLS) between assets](/modelos/regressao_linear) | Dow Jones ~ S&P 500: β = 0.91 with R² = 0.91. US Treasury ~ S&P 500, however, has an R² of 0.04: the 'obvious' relationship explains almost nothing day to day. |
| 05 | [Directional logistic regression](/modelos/regressao_logistica) | Out of sample (2016–2026) the logistic model gets 54.2% of the S&P 500 direction right — practically the share of up days (54.2%): it predicted up on 98% of days and has an AUC of 0.492. High accuracy without separating power is the trap this baseline defuses. |
| 06 | [SVM and kernel methods](/modelos/svm_kernels) | With only RSI and volatility as inputs, none of the four kernels exceeds 50.7% balanced accuracy out of sample. RBF is the one that 'learns' most in training (53.2%) and loses most in testing (48.4%): a kernel does not create signal where there is none. |
| 07 | [Decision trees and Random Forest](/modelos/arvores_random_forest) | A depth-20 tree gets 83.7% right in training and 49.8% in testing: it memorized the past. The shallow forest stays at 53.5% — modest but honest; the most used attribute is 'ret_1'. |
| 08 | [MLP neural network — reversal indicator](/modelos/mlp_reversao) | On silver, in 2023–2026 (never seen in training), the MLP issued 607 upward-reversal signals with 17.3% precision, against a base rate of 13.6% (1.27× the natural frequency): that ratio, not overall accuracy, says whether the indicator adds information. |
| 09 | [PCA — risk factors and indices](/modelos/pca_fatores) | The 1st factor alone explains 24.5% of the daily variation of 27 assets; 12 factors are needed to reach 80%. The 27 assets are not 27 independent bets. |
| 10 | [Asset clustering (K-means)](/modelos/kmeans_clusters) | The silhouette picks K = 4 groups without manual intervention; one group mixes 3 different asset classes — the 'commodity' or 'currency' label does not say how the asset behaves. |
| 11 | [Return embeddings (FastICA) + cosine](/modelos/embedding_retornos) | Over the last 60 sessions, the most similar pair is Brent crude × WTI crude (cosine 0.96) and the most opposite is the Dollar Index × Euro/Dollar (-0.89): a proximity map that updates every window. |
| 12 | [Isolation Forest — abnormal returns and volumes](/modelos/isolation_forest) | Without a single label, the isolation forest flags 77 S&P 500 sessions as anomalous — 21 in 2020 alone — and 57% of them are drops: the anomaly is a signal of changing dynamics, not noise to discard. |
| 13 | [Multi-method outliers (IQR, robust z, LOF)](/modelos/outliers_multimetodo) | On the S&P 500, the boxplot flags 264 days as outliers (6.7% of the sample); the three-method consensus keeps 101. A single discrepant point changes the slope of the line from 0.76 to 0.53. |
| 14 | [Markov chain of regimes (up, down, sideways)](/modelos/markov_regimes) | On the S&P 500, being in a down 20-session block, the chance that the next block is up is 59.0% — higher than staying down (30.8%). In equilibrium, the market spends 41.3% of the time in an up regime. |
| 15 | [Hidden Markov model (Gaussian HMM)](/modelos/hmm_regimes) | With no arbitrary cut-off rule, the HMM finds three regimes in the S&P 500: the turbulent one has 43% annual volatility against 7% in the calm one and lasts 18 sessions on average. Today the most likely regime is 'calm'. |
| 16 | [Bayesian update of return and volatility](/modelos/bayes_conjugado) | Gold since 2019: the posterior average annual return is 15.3%, but the 95% credible interval runs from 2.3% to 28.4%. The probability that the mean is positive is 98.9% — the sample mean (15.7%) alone does not say that. |
| 17 | [Fourier transform — dominant cycles](/modelos/fourier_ciclos) | Of the 12 largest cycle peaks across the four assets, only 2 exceed the 95% noise threshold obtained by shuffling the returns themselves. Every periodogram has peaks; the test says which are cycles and which are chance. |
| 18 | [Wavelets — time-frequency decomposition](/modelos/wavelet_haar) | Level 1 (2-session oscillations) holds 55.0% of the S&P 500's energy. When high-frequency energy explodes (z {">"} 2), the dispersion of the next 20 sessions' return is 1.3× normal: the wavelet locates in time what Fourier only sees on average. |
| 19 | [Markowitz efficient frontier](/modelos/markowitz_fronteira) | The maximum-Sharpe portfolio had a Sharpe of 1.19 in 2010–2019 and delivered 0.76 in 2020–2026; equal weights went from 0.35 to 0.94. The frontier is exact about the past — the error lies in estimating means the future does not repeat. |
| 20 | [Genetic algorithm — portfolio optimization](/modelos/ag_carteira) | Four parallel GA runs, with different seeds, converge to the same portfolio (average weight deviation of 0.1 p.p.) with a Sharpe of 1.19 in 2010–2019. In 2020–2026 it delivers 0.86, below equal weights (0.94): convergence proves the optimum is stable, not that the future will repeat it. |
| 21 | [Genetic algorithm — selection of indicators and parameters](/modelos/ag_indicadores) | The GA tested 1826 distinct rules on the S&P 500 and the best of each run had a training Sharpe of up to 0.78; in 2019–2026 they stayed between 0.41 and 0.54, against 0.77 for simply staying long. The more rules you test, the higher the training Sharpe by pure chance. |
| 22 | [Genetic programming — symbolic regression](/modelos/programacao_genetica) | Genetic programming discovered readable formulas such as ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 nodes), with a rank correlation of -0.080 with the next return in training and -0.028 in testing. Evolution always finds 'something' in the past; only the unseen period separates indicator from coincidence. |
| 23 | [Hurst exponent and rolling Hurst indicator](/modelos/hurst_movel) | The raw R/S H lies between 0.54 and 0.59 and would look 'persistent'; against shuffled series, none of the 6 assets shows real memory. The MH100 − MH150 crossover beats the moving-average crossover in 3 of 6 assets by Sharpe ratio. |
| 24 | [Non-linear dynamics and heavy tails](/modelos/sistemas_nao_lineares) | 4-standard-deviation moves happen, in median, 64× more often than the normal curve predicts; the return has almost no memory (autocorrelation -0.02), but the size of the move does (0.15). |
| 25 | [Conditional volatility (EWMA and GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500: persistence α+β = 0.963 — a volatility shock takes 18 sessions to lose half its strength. 1-day 99% VaR: 1.75%. |
| 26 | [Correlation network and centrality](/modelos/rede_correlacao) | Chosen by the 2010–2019 network, the 8 peripheral assets stayed almost independent in 2020–2026 (average correlation 0.00 against 0.15 for the central ones) and returned more (11.0% against 7.4% p.a.), but with more volatility. The winner over both baskets was the portfolio with all 27 (Sharpe 0.95): the number of independent bets weighs more than position in the network. |
| 27 | [Granger causality and contagion](/modelos/causalidade_granger) | Of the 72 pairs tested, 7 survive the Bonferroni correction. The strongest, Euro/Dollar → Dollar Index, is an artifact of closing times between different sources: statistical precedence is not cause — and the test shows exactly where intuition would be fooled. |
| 28 | [Model and concept drift detection](/modelos/drift_modelo) | The model trained on 2010–2016 calls for retraining in 8 of the following 10 years: the input regime of that period did not return. 2022 had the worst accuracy (43.8%) and 2017 the largest shift (KS 0.77) — monitoring the input reveals the problem without waiting for the loss. |
| 29 | [Walk-forward backtest with costs](/modelos/backtest_walkforward) | With costs of 5 bps per turnover, 2 of 4 strategies pass the three STOP gates (Equal weights, Risk parity). The momentum window, chosen each month using only the past, changed 45 times — the 'optimal parameter' is not constant. |
| 30 | [Optimal trading rules (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | The Brent − WTI spread reverts to the mean with a half-life of 22 sessions. Simulating 4,000 paths per cell, the best rule is a 1.5σ target with a 10.0σ stop (Sharpe per trade 0.63) — a fixed percentage stop ignores the asset's dynamics. |
| 31 | [Newcomb-Benford law — data integrity](/modelos/benford) | Only 21 of the 29 volume series span enough range for the test; applying Benford to the others would be a false alarm. Aggregated, the volumes span 6.4 orders of magnitude and give a MAD of 0.0099 (acceptable conformity). |
| 32 | [Explainability with Shapley values (SHAP)](/modelos/shap_explicabilidade) | In the latest forecast, the probability of a rise goes from 54.0% (model average) to 55.4%; the attribute that weighed most was 'ret_1' (+1.0 p.p.). The black box starts answering 'why'. |

## The site and the lab

The site is built with evidence.dev: SQL over the results, one interactive page per model and a lab where the Rust engine, compiled to WebAssembly, runs in your browser — no server and no per-user cost.

- [In-browser lab (WebAssembly)](/laboratorio)
- [Three engines, one result](/motores)
- [Full catalog](/catalogo)

> The models do not predict the future with certainty — and they say so: several results here show that a popular method carries no signal. That is the value: knowing where not to trust before spending.

</div>

---

_quant_models_2026 · Author: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
