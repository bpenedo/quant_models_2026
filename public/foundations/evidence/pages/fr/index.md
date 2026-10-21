---
title: "quant_models_2026 — 40 modèles quantitatifs pour décider dans l'incertitude"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · [English](/en) · [Español](/es) · **Français** · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Arrêtez de choisir au tableur. Commencez à décider par modèle.

**32 modèles exécutés sur 16 ans de données réelles, trois moteurs (Python, Rust et F#) qui concordent bit à bit et un laboratoire qui tourne dans votre navigateur — chacun montrant, par la donnée, où l'intuition trompe.**

> Vous l'avez déjà fait. Vous avez monté un tableur avec les alternatives — fournisseurs, téléphones pour l'équipe, voitures électriques pour la flotte, actifs pour le portefeuille, avions pour un escadron —, noté chaque critère, pondéré, trié du plus grand au plus petit et apporté le premier à la réunion. Le tableur avait raison. La décision, non.
>
> **Le tableur ne se trompe pas dans le calcul. Il se trompe de question.**

Tableurs, matrices de notation et filtres de classement traitent chaque nombre comme certain. Aucun ne demande quelle part de ce que vous voyez est du bruit, si le passé représente encore l'avenir ou si votre « meilleure option » survivrait à une période qu'elle n'a jamais vue.

## Les 32 modèles, un par un

| # | Modèle | Ce que la donnée a montré : |
|---:|---|---|
| 01 | [Statistique descriptive robuste](/modelos/estatistica_descritiva) | L'argent a un écart-type 1,6× supérieur à son σ robuste : quelques jours extrêmes gonflent la volatilité « moyenne » — kurtosis en excès de 26,9. |
| 02 | [Support et résistance par mode + clustering](/modelos/suporte_resistencia) | Or : le mode des prix arrondis est 3 330,00 ; la bande la plus visitée (2 350,00–2 730,00) concentre 24 % des séances et sert aujourd'hui de support. |
| 03 | [Stationnarité (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | 1 série de prix sur 8 est stationnaire à 5 % ; en log-rendement, 8 sur 8. S'entraîner sur les prix, c'est s'entraîner sur une distribution qui ne revient pas. |
| 04 | [Régression linéaire (MCO) entre actifs](/modelos/regressao_linear) | Dow Jones ~ S&P 500 : β = 0,91 avec R² = 0,91. En revanche, Bon du Trésor américain ~ S&P 500 a un R² de 0,04 : la relation « évidente » n'explique presque rien au quotidien. |
| 05 | [Régression logistique de direction](/modelos/regressao_logistica) | Hors échantillon (2016–2026), la logistique prédit correctement 54,2 % de la direction du S&P 500 — pratiquement la part des jours de hausse (54,2 %) : elle a prédit la hausse 98 % des jours et a un AUC de 0,492. Une précision élevée sans pouvoir de séparation est le piège que cette référence désamorce. |
| 06 | [SVM et méthodes à noyau](/modelos/svm_kernels) | Avec seulement le RSI et la volatilité en entrée, aucun des quatre noyaux ne dépasse 50,7 % de précision équilibrée hors échantillon. Le RBF est celui qui « apprend » le plus à l'entraînement (53,2 %) et perd le plus au test (48,4 %) : un noyau ne crée pas de signal là où il n'y en a pas. |
| 07 | [Arbres de décision et Random Forest](/modelos/arvores_random_forest) | Un arbre de profondeur 20 réussit 83,7 % à l'entraînement et 49,8 % au test : il a mémorisé le passé. La forêt peu profonde reste à 53,5 % — modeste mais honnête ; l'attribut le plus utilisé est « ret_1 ». |
| 08 | [Réseau de neurones MLP — indicateur de retournement](/modelos/mlp_reversao) | Sur l'argent, en 2023–2026 (jamais vus à l'entraînement), le MLP a émis 607 signaux de retournement haussier avec une précision de 17,3 %, contre un taux de base de 13,6 % (1,27× la fréquence naturelle) : c'est ce rapport, et non la précision globale, qui dit si l'indicateur apporte de l'information. |
| 09 | [ACP — facteurs de risque et indices](/modelos/pca_fatores) | Le 1er facteur explique à lui seul 24,5 % de la variation quotidienne de 27 actifs ; il faut 12 facteurs pour atteindre 80 %. Les 27 actifs ne sont pas 27 paris indépendants. |
| 10 | [Clustering d'actifs (K-means)](/modelos/kmeans_clusters) | La silhouette choisit K = 4 groupes sans intervention manuelle ; un groupe mélange 3 classes d'actifs différentes — l'étiquette « matière première » ou « devise » ne dit pas comment l'actif se comporte. |
| 11 | [Embeddings de rendements (FastICA) + cosinus](/modelos/embedding_retornos) | Sur les 60 dernières séances, la paire la plus semblable est Pétrole Brent × Pétrole WTI (cosinus 0,96) et la plus opposée Indice du dollar × Euro/Dollar (-0,89) : une carte de proximité mise à jour à chaque fenêtre. |
| 12 | [Isolation Forest — rendements et volumes anormaux](/modelos/isolation_forest) | Sans aucune étiquette, la forêt d'isolement marque 77 séances du S&P 500 comme anormales — 21 rien qu'en 2020 — et 57 % d'entre elles sont des baisses : l'anomalie est un signal de changement de dynamique, pas un bruit à écarter. |
| 13 | [Valeurs aberrantes multiméthode (IQR, z robuste, LOF)](/modelos/outliers_multimetodo) | Sur le S&P 500, la boîte à moustaches marque 264 jours comme aberrants (6,7 % de l'échantillon) ; le consensus des trois méthodes en retient 101. Un seul point discordant fait passer la pente de la droite de 0,76 à 0,53. |
| 14 | [Chaîne de Markov de régimes (hausse, baisse, latéral)](/modelos/markov_regimes) | Sur le S&P 500, en baisse sur un bloc de 20 séances, la probabilité que le bloc suivant soit haussier est de 59,0 % — plus élevée que celle de rester en baisse (30,8 %). À l'équilibre, le marché passe 41,3 % du temps en régime haussier. |
| 15 | [Modèle de Markov caché (HMM gaussien)](/modelos/hmm_regimes) | Sans règle de coupure arbitraire, le HMM trouve trois régimes dans le S&P 500 : le turbulent a une volatilité de 43 % par an contre 7 % pour le calme et dure en moyenne 18 séances. Aujourd'hui, le régime le plus probable est « calme ». |
| 16 | [Mise à jour bayésienne du rendement et de la volatilité](/modelos/bayes_conjugado) | Or depuis 2019 : le rendement annuel moyen a posteriori est de 15,3 %, mais l'intervalle de crédibilité à 95 % va de 2,3 % à 28,4 %. La probabilité que la moyenne soit positive est de 98,9 % — la moyenne empirique (15,7 %) ne le dit pas à elle seule. |
| 17 | [Transformée de Fourier — cycles dominants](/modelos/fourier_ciclos) | Sur les 12 plus grands pics de cycle des quatre actifs, seuls 2 dépassent le seuil de bruit à 95 % obtenu en mélangeant les rendements eux-mêmes. Tout périodogramme a des pics ; le test dit lesquels sont des cycles et lesquels relèvent du hasard. |
| 18 | [Ondelettes — décomposition temps-fréquence](/modelos/wavelet_haar) | Le niveau 1 (oscillations de 2 séances) concentre 55,0 % de l'énergie du S&P 500. Quand l'énergie haute fréquence explose (z {">"} 2), la dispersion du rendement des 20 séances suivantes est 1,3× la normale : l'ondelette localise dans le temps ce que Fourier ne voit qu'en moyenne. |
| 19 | [Frontière efficiente de Markowitz](/modelos/markowitz_fronteira) | Le portefeuille de Sharpe maximal avait un Sharpe de 1,19 en 2010–2019 et a livré 0,76 en 2020–2026 ; les poids égaux sont passés de 0,35 à 0,94. La frontière est exacte sur le passé — l'erreur réside dans l'estimation de moyennes que l'avenir ne répète pas. |
| 20 | [Algorithme génétique — optimisation de portefeuille](/modelos/ag_carteira) | Quatre exécutions parallèles de l'AG, avec des graines différentes, convergent vers le même portefeuille (écart moyen de poids de 0,1 p.p.) avec un Sharpe de 1,19 en 2010–2019. En 2020–2026, il livre 0,86, en dessous des poids égaux (0,94) : la convergence prouve que l'optimum est stable, pas que l'avenir le répétera. |
| 21 | [Algorithme génétique — sélection d'indicateurs et de paramètres](/modelos/ag_indicadores) | L'AG a testé 1826 règles distinctes sur le S&P 500 et la meilleure de chaque exécution a eu un Sharpe d'entraînement allant jusqu'à 0,78 ; en 2019–2026, elles sont restées entre 0,41 et 0,54, contre 0,77 en restant simplement acheteur. Plus on teste de règles, plus le Sharpe d'entraînement monte par pur hasard. |
| 22 | [Programmation génétique — régression symbolique](/modelos/programacao_genetica) | La programmation génétique a découvert des formules lisibles comme ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 nœuds), avec une corrélation de rangs de -0,080 avec le rendement suivant à l'entraînement et de -0,028 au test. L'évolution trouve toujours « quelque chose » dans le passé ; seule la période jamais vue sépare l'indicateur de la coïncidence. |
| 23 | [Exposant de Hurst et indicateur de Hurst glissant](/modelos/hurst_movel) | Le H brut de R/S se situe entre 0,54 et 0,59 et paraîtrait « persistant » ; face à des séries mélangées, aucun des 6 actifs ne montre de mémoire réelle. Le croisement MH100 − MH150 bat celui des moyennes mobiles sur 3 actifs sur 6 selon le ratio de Sharpe. |
| 24 | [Dynamique non linéaire et queues épaisses](/modelos/sistemas_nao_lineares) | Les mouvements de 4 écarts-types se produisent, en médiane, 64× plus souvent que ne le prévoit la courbe normale ; le rendement n'a presque pas de mémoire (autocorrélation -0,02), mais l'amplitude du mouvement, si (0,15). |
| 25 | [Volatilité conditionnelle (EWMA et GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500 : persistance α+β = 0,963 — un choc de volatilité met 18 séances à perdre la moitié de sa force. VaR 99 % à 1 jour : 1,75 %. |
| 26 | [Réseau de corrélation et centralité](/modelos/rede_correlacao) | Choisis par le réseau de 2010–2019, les 8 actifs périphériques sont restés presque indépendants en 2020–2026 (corrélation moyenne 0,00 contre 0,15 pour les centraux) et ont rapporté davantage (11,0 % contre 7,4 % par an), mais avec plus de volatilité. Le vainqueur des deux paniers a été le portefeuille des 27 (Sharpe 0,95) : le nombre de paris indépendants pèse plus que la position dans le réseau. |
| 27 | [Causalité de Granger et contagion](/modelos/causalidade_granger) | Sur les 72 paires testées, 7 survivent à la correction de Bonferroni. La plus forte, Euro/Dollar → Indice du dollar, est un artefact d'horaire de clôture entre sources différentes : la précédence statistique n'est pas une cause — et le test montre exactement où l'intuition serait trompée. |
| 28 | [Détection de dérive du modèle et du concept](/modelos/drift_modelo) | Le modèle entraîné sur 2010–2016 demande un réentraînement pour 8 des 10 années suivantes : le régime d'entrée de cette période n'est pas revenu. 2022 a eu la pire précision (43,8 %) et 2017 le plus grand déplacement (KS 0,77) — surveiller l'entrée révèle le problème sans attendre la perte. |
| 29 | [Backtest walk-forward avec coûts](/modelos/backtest_walkforward) | Avec des coûts de 5 pb par rotation, 2 stratégies sur 4 franchissent les trois barrières STOP (Poids égaux, Parité de risque). La fenêtre du momentum, choisie chaque mois avec le seul passé, a changé 45 fois — le « paramètre optimal » n'est pas constant. |
| 30 | [Règles de trading optimales (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | Le spread Brent − WTI revient à la moyenne avec une demi-vie de 22 séances. En simulant 4 000 trajectoires par cellule, la meilleure règle est un objectif de 1,5σ avec un stop de 10,0σ (Sharpe par opération 0,63) — un stop en pourcentage fixe ignore la dynamique de l'actif. |
| 31 | [Loi de Newcomb-Benford — intégrité des données](/modelos/benford) | Seules 21 des 29 séries de volume couvrent une amplitude suffisante pour le test ; appliquer Benford aux autres serait une fausse alerte. Agrégés, les volumes couvrent 6,4 ordres de grandeur et donnent un MAD de 0,0099 (conformité acceptable). |
| 32 | [Explicabilité par valeurs de Shapley (SHAP)](/modelos/shap_explicabilidade) | Dans la dernière prévision, la probabilité de hausse passe de 54,0 % (moyenne du modèle) à 55,4 % ; l'attribut qui a le plus pesé est « ret_1 » (+1,0 p.p.). La boîte noire commence à répondre « pourquoi ». |

## Le site et le laboratoire

Le site est généré avec evidence.dev : du SQL sur les résultats, une page interactive par modèle et un laboratoire où le moteur Rust, compilé en WebAssembly, tourne dans votre navigateur — sans serveur et sans coût par utilisateur.

- [Laboratoire dans le navigateur (WebAssembly)](/laboratorio)
- [Trois moteurs, un résultat](/motores)
- [Catalogue complet](/catalogo)

> Les modèles ne prédisent pas l'avenir avec certitude — et ils le disent : plusieurs résultats ici montrent qu'une méthode populaire n'a pas de signal. C'est là leur valeur : savoir où ne pas faire confiance avant de dépenser.

</div>

---

_quant_models_2026 · Auteur: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
