---
title: "quant_models_2026 — 40 quantitative Modelle für Entscheidungen unter Unsicherheit"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · [English](/en) · [Español](/es) · [Français](/fr) · **Deutsch** · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Hören Sie auf, per Tabellenkalkulation zu wählen. Entscheiden Sie per Modell.

**32 Modelle auf 16 Jahren echter Daten, drei Engines (Python, Rust und F#), die Bit für Bit übereinstimmen, und ein Labor, das in Ihrem Browser läuft — jedes zeigt mit den Daten, wo die Intuition täuscht.**

> Sie haben das schon getan. Sie haben eine Tabelle mit den Alternativen angelegt — Lieferanten, Smartphones für das Team, Elektroautos für den Fuhrpark, Anlagen für das Portfolio, Flugzeuge für eine Staffel —, jedes Kriterium bewertet, gewichtet, absteigend sortiert und den Ersten in die Besprechung gebracht. Die Tabelle stimmte. Die Entscheidung nicht.
>
> **Die Tabellenkalkulation verrechnet sich nicht. Sie stellt die falsche Frage.**

Tabellenkalkulationen, Bewertungsmatrizen und Rangfilter behandeln jede Zahl als sicher. Keines davon fragt, wie viel von dem, was Sie sehen, Rauschen ist, ob die Vergangenheit die Zukunft noch repräsentiert oder ob Ihre „beste Option“ einen Zeitraum überstehen würde, den sie nie gesehen hat.

## Die 32 Modelle, eines nach dem anderen

| # | Modell | Was die Daten zeigten: |
|---:|---|---|
| 01 | [Robuste deskriptive Statistik](/modelos/estatistica_descritiva) | Silber hat eine 1,6× größere Standardabweichung als sein robustes σ: Wenige extreme Tage blähen die „durchschnittliche“ Volatilität auf — Überschusskurtosis von 26,9. |
| 02 | [Unterstützung und Widerstand per Modus + Clustering](/modelos/suporte_resistencia) | Gold: Der Modus der gerundeten Preise ist 3.330,00; das meistbesuchte Band (2.350,00–2.730,00) umfasst 24 % der Handelstage und wirkt heute als Unterstützung. |
| 03 | [Stationarität (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | 1 von 8 Preisreihen ist auf 5-%-Niveau stationär; als Log-Rendite 8 von 8. Mit Preisen zu trainieren heißt, mit einer Verteilung zu trainieren, die nicht wiederkehrt. |
| 04 | [Lineare Regression (KQ) zwischen Anlagen](/modelos/regressao_linear) | Dow Jones ~ S&P 500: β = 0,91 bei R² = 0,91. US-Staatsanleihe ~ S&P 500 hat dagegen ein R² von 0,04: Die „offensichtliche“ Beziehung erklärt im Alltag fast nichts. |
| 05 | [Logistische Regression der Richtung](/modelos/regressao_logistica) | Außerhalb der Stichprobe (2016–2026) trifft die Logistik 54,2 % der Richtung des S&P 500 — praktisch den Anteil der Aufwärtstage (54,2 %): Sie sagte an 98 % der Tage einen Anstieg voraus und hat eine AUC von 0,492. Hohe Genauigkeit ohne Trennschärfe ist die Falle, die diese Basislinie entschärft. |
| 06 | [SVM und Kernel-Methoden](/modelos/svm_kernels) | Mit nur RSI und Volatilität als Eingaben überschreitet keiner der vier Kernel 50,7 % balancierte Genauigkeit außerhalb der Stichprobe. Der RBF-Kernel „lernt“ im Training am meisten (53,2 %) und verliert im Test am meisten (48,4 %): Ein Kernel erzeugt kein Signal, wo keines ist. |
| 07 | [Entscheidungsbäume und Random Forest](/modelos/arvores_random_forest) | Ein Baum der Tiefe 20 trifft im Training 83,7 % und im Test 49,8 %: Er hat die Vergangenheit auswendig gelernt. Der flache Wald bleibt bei 53,5 % — bescheiden, aber ehrlich; das meistgenutzte Merkmal ist „ret_1“. |
| 08 | [MLP-Neuronales Netz — Umkehrindikator](/modelos/mlp_reversao) | Bei Silber gab das MLP 2023–2026 (im Training nie gesehen) 607 Signale für eine Aufwärtsumkehr mit 17,3 % Präzision ab, gegenüber einer Basisrate von 13,6 % (1,27× die natürliche Häufigkeit): Dieses Verhältnis, nicht die Gesamtgenauigkeit, zeigt, ob der Indikator Information liefert. |
| 09 | [PCA — Risikofaktoren und Indizes](/modelos/pca_fatores) | Der 1. Faktor allein erklärt 24,5 % der täglichen Schwankung von 27 Anlagen; 12 Faktoren sind nötig, um 80 % zu erreichen. Die 27 Anlagen sind nicht 27 unabhängige Wetten. |
| 10 | [Clustering von Anlagen (K-Means)](/modelos/kmeans_clusters) | Die Silhouette wählt K = 4 Gruppen ohne manuellen Eingriff; eine Gruppe mischt 3 verschiedene Anlageklassen — das Etikett „Rohstoff“ oder „Währung“ sagt nicht, wie sich die Anlage verhält. |
| 11 | [Rendite-Embeddings (FastICA) + Kosinus](/modelos/embedding_retornos) | In den letzten 60 Handelstagen ist das ähnlichste Paar Brent-Öl × WTI-Öl (Kosinus 0,96) und das gegensätzlichste Dollar-Index × Euro/Dollar (-0,89): eine Nähekarte, die sich in jedem Fenster aktualisiert. |
| 12 | [Isolation Forest — anomale Renditen und Volumina](/modelos/isolation_forest) | Ohne ein einziges Label markiert der Isolationswald 77 Handelstage des S&P 500 als anomal — 21 davon allein 2020 — und 57 % davon sind Rückgänge: Die Anomalie ist ein Signal für veränderte Dynamik, kein Rauschen zum Aussortieren. |
| 13 | [Ausreißer mit mehreren Methoden (IQR, robustes z, LOF)](/modelos/outliers_multimetodo) | Beim S&P 500 markiert der Boxplot 264 Tage als Ausreißer (6,7 % der Stichprobe); der Konsens dreier Methoden behält 101. Ein einziger abweichender Punkt ändert die Steigung der Geraden von 0,76 auf 0,53. |
| 14 | [Markow-Kette der Regime (steigend, fallend, seitwärts)](/modelos/markov_regimes) | Beim S&P 500 liegt nach einem fallenden 20-Tage-Block die Wahrscheinlichkeit für einen steigenden nächsten Block bei 59,0 % — höher als für ein Weiterfallen (30,8 %). Im Gleichgewicht verbringt der Markt 41,3 % der Zeit im Aufwärtsregime. |
| 15 | [Verborgenes Markow-Modell (gaußsches HMM)](/modelos/hmm_regimes) | Ohne willkürliche Schwellenregel findet das HMM drei Regime im S&P 500: Das turbulente hat 43 % Volatilität pro Jahr gegenüber 7 % im ruhigen und dauert im Mittel 18 Handelstage. Heute ist das wahrscheinlichste Regime „ruhig“. |
| 16 | [Bayes'sche Aktualisierung von Rendite und Volatilität](/modelos/bayes_conjugado) | Gold seit 2019: Die durchschnittliche Jahresrendite a posteriori beträgt 15,3 %, doch das 95-%-Glaubwürdigkeitsintervall reicht von 2,3 % bis 28,4 %. Die Wahrscheinlichkeit, dass der Mittelwert positiv ist, liegt bei 98,9 % — der Stichprobenmittelwert (15,7 %) allein sagt das nicht. |
| 17 | [Fourier-Transformation — dominante Zyklen](/modelos/fourier_ciclos) | Von den 12 größten Zyklusspitzen der vier Anlagen überschreiten nur 2 die 95-%-Rauschschwelle, die durch Mischen der eigenen Renditen gewonnen wurde. Jedes Periodogramm hat Spitzen; der Test sagt, welche Zyklen und welche Zufall sind. |
| 18 | [Wavelets — Zeit-Frequenz-Zerlegung](/modelos/wavelet_haar) | Stufe 1 (Schwingungen über 2 Handelstage) enthält 55,0 % der Energie des S&P 500. Wenn die Hochfrequenzenergie explodiert (z {">"} 2), ist die Streuung der Rendite der folgenden 20 Handelstage 1,3× so hoch wie normal: Das Wavelet verortet zeitlich, was Fourier nur im Durchschnitt sieht. |
| 19 | [Effizienzgrenze nach Markowitz](/modelos/markowitz_fronteira) | Das Portfolio mit maximalem Sharpe hatte 2010–2019 eine Sharpe-Ratio von 1,19 und lieferte 2020–2026 0,76; die Gleichgewichtung stieg von 0,35 auf 0,94. Die Grenze ist für die Vergangenheit exakt — der Fehler liegt in der Schätzung von Mittelwerten, die die Zukunft nicht wiederholt. |
| 20 | [Genetischer Algorithmus — Portfoliooptimierung](/modelos/ag_carteira) | Vier parallele GA-Läufe mit verschiedenen Startwerten konvergieren zum selben Portfolio (mittlere Gewichtsabweichung 0,1 Pp.) mit einer Sharpe-Ratio von 1,19 in 2010–2019. 2020–2026 liefert es 0,86, unter der Gleichgewichtung (0,94): Konvergenz beweist, dass das Optimum stabil ist, nicht, dass die Zukunft es wiederholt. |
| 21 | [Genetischer Algorithmus — Auswahl von Indikatoren und Parametern](/modelos/ag_indicadores) | Der GA testete 1826 verschiedene Regeln auf dem S&P 500, und die beste jedes Laufs hatte eine Trainings-Sharpe-Ratio von bis zu 0,78; 2019–2026 lagen sie zwischen 0,41 und 0,54, gegenüber 0,77 beim bloßen Halten. Je mehr Regeln man testet, desto höher die Trainings-Sharpe-Ratio aus purem Zufall. |
| 22 | [Genetische Programmierung — symbolische Regression](/modelos/programacao_genetica) | Die genetische Programmierung entdeckte lesbare Formeln wie ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 Knoten), mit einer Rangkorrelation von -0,080 zur nächsten Rendite im Training und -0,028 im Test. Die Evolution findet in der Vergangenheit immer „etwas“; nur der nie gesehene Zeitraum trennt Indikator von Zufall. |
| 23 | [Hurst-Exponent und gleitender Hurst-Indikator](/modelos/hurst_movel) | Das rohe R/S-H liegt zwischen 0,54 und 0,59 und wirkte „persistent“; gegenüber gemischten Reihen zeigt keine der 6 Anlagen echtes Gedächtnis. Der Kreuzungspunkt MH100 − MH150 schlägt den der gleitenden Durchschnitte bei 3 von 6 Anlagen nach Sharpe-Ratio. |
| 24 | [Nichtlineare Dynamik und schwere Verteilungsenden](/modelos/sistemas_nao_lineares) | Bewegungen von 4 Standardabweichungen treten im Median 64× häufiger auf, als die Normalverteilung vorhersagt; die Rendite hat kaum Gedächtnis (Autokorrelation -0,02), die Größe der Bewegung schon (0,15). |
| 25 | [Bedingte Volatilität (EWMA und GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500: Persistenz α+β = 0,963 — ein Volatilitätsschock braucht 18 Handelstage, um die Hälfte seiner Kraft zu verlieren. 1-Tages-VaR 99 %: 1,75 %. |
| 26 | [Korrelationsnetzwerk und Zentralität](/modelos/rede_correlacao) | Vom Netzwerk 2010–2019 ausgewählt, blieben die 8 peripheren Anlagen 2020–2026 nahezu unabhängig (mittlere Korrelation 0,00 gegenüber 0,15 bei den zentralen) und erzielten mehr (11,0 % gegenüber 7,4 % p. a.), allerdings mit höherer Volatilität. Sieger über beide Körbe war das Portfolio mit allen 27 (Sharpe 0,95): Die Zahl unabhängiger Wetten wiegt mehr als die Position im Netzwerk. |
| 27 | [Granger-Kausalität und Ansteckung](/modelos/causalidade_granger) | Von 72 getesteten Paaren überstehen 7 die Bonferroni-Korrektur. Das stärkste, Euro/Dollar → Dollar-Index, ist ein Artefakt der Schlusszeiten unterschiedlicher Quellen: Statistische Vorzeitigkeit ist keine Ursache — und der Test zeigt genau, wo die Intuition getäuscht würde. |
| 28 | [Erkennung von Modell- und Konzeptdrift](/modelos/drift_modelo) | Das auf 2010–2016 trainierte Modell verlangt in 8 der folgenden 10 Jahre ein Neutraining: Das Eingaberegime jenes Zeitraums kehrte nicht zurück. 2022 hatte die schlechteste Genauigkeit (43,8 %) und 2017 die größte Verschiebung (KS 0,77) — die Überwachung der Eingaben zeigt das Problem, ohne auf den Verlust zu warten. |
| 29 | [Walk-forward-Backtest mit Kosten](/modelos/backtest_walkforward) | Bei Kosten von 5 Bp. pro Umschlag bestehen 2 von 4 Strategien die drei STOP-Schwellen (Gleichgewichtung, Risikoparität). Das Momentum-Fenster, jeden Monat allein aus der Vergangenheit gewählt, änderte sich 45-mal — der „optimale Parameter“ ist nicht konstant. |
| 30 | [Optimale Handelsregeln (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | Der Brent − WTI-Spread kehrt mit einer Halbwertszeit von 22 Handelstagen zum Mittelwert zurück. Bei 4.000 simulierten Pfaden pro Zelle ist die beste Regel ein Ziel von 1,5σ mit einem Stopp bei 10,0σ (Sharpe pro Trade 0,63) — ein fester prozentualer Stopp ignoriert die Dynamik der Anlage. |
| 31 | [Newcomb-Benford-Gesetz — Datenintegrität](/modelos/benford) | Nur 21 der 29 Volumenreihen decken eine für den Test ausreichende Spannweite ab; Benford auf die übrigen anzuwenden, wäre Fehlalarm. Zusammengefasst decken die Volumina 6,4 Größenordnungen ab und ergeben eine MAD von 0,0099 (akzeptable Konformität). |
| 32 | [Erklärbarkeit mit Shapley-Werten (SHAP)](/modelos/shap_explicabilidade) | In der letzten Prognose steigt die Wahrscheinlichkeit eines Anstiegs von 54,0 % (Modelldurchschnitt) auf 55,4 %; am stärksten wog das Merkmal „ret_1“ (+1,0 Pp.). Die Blackbox beginnt, das „Warum“ zu beantworten. |

## Website und Labor

Die Website wird mit evidence.dev erzeugt: SQL über die Ergebnisse, eine interaktive Seite pro Modell und ein Labor, in dem die Rust-Engine, nach WebAssembly kompiliert, in Ihrem Browser läuft — ohne Server und ohne Kosten pro Nutzer.

- [Labor im Browser (WebAssembly)](/laboratorio)
- [Drei Engines, ein Ergebnis](/motores)
- [Vollständiger Katalog](/catalogo)

> Die Modelle sagen die Zukunft nicht mit Sicherheit voraus — und sagen das auch: Mehrere Ergebnisse hier zeigen, dass eine populäre Methode kein Signal hat. Das ist der Wert: zu wissen, wo man nicht vertrauen darf, bevor man Geld ausgibt.

</div>

---

_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
