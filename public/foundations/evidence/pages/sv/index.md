---
title: "quant_models_2026 — 40 kvantitativa modeller för beslut under osäkerhet"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · [English](/en) · [Español](/es) · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · **Svenska** · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Sluta välja med kalkylblad. Börja besluta med modeller.

**32 modeller som körs på 16 år av verkliga data, tre motorer (Python, Rust och F#) som stämmer överens bit för bit och ett labb som körs i din webbläsare — var och en visar med data var intuitionen vilseleder.**

> Du har gjort det här. Du byggde ett kalkylblad med alternativen — leverantörer, mobiler till teamet, elbilar till fordonsparken, tillgångar till portföljen, flygplan till en division —, gav poäng per kriterium, viktade, sorterade från högst till lägst och tog med vinnaren till mötet. Kalkylbladet hade rätt. Beslutet hade fel.
>
> **Kalkylbladet räknar inte fel. Det ställer fel fråga.**

Kalkylblad, poängmatriser och rangordningsfilter behandlar varje tal som säkert. Inget av dem frågar hur mycket av det du ser som är brus, om det förflutna fortfarande representerar framtiden eller om ditt ”bästa alternativ” skulle klara en period det aldrig har sett.

## De 32 modellerna, en i taget

| # | Modell | Vad data visade: |
|---:|---|---|
| 01 | [Robust deskriptiv statistik](/modelos/estatistica_descritiva) | Silver har en standardavvikelse 1,6× större än sin robusta σ: några få extrema dagar blåser upp den ”genomsnittliga” volatiliteten — överskottskurtosis på 26,9. |
| 02 | [Stöd och motstånd via typvärde + klustring](/modelos/suporte_resistencia) | Guld: typvärdet för avrundade priser är 3 330,00; det mest besökta bandet (2 350,00–2 730,00) rymmer 24 % av handelsdagarna och fungerar i dag som stöd. |
| 03 | [Stationaritet (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | 1 av 8 prisserier är stationär på 5 %-nivån; i logavkastning 8 av 8. Att träna på priser är att träna på en fördelning som inte kommer tillbaka. |
| 04 | [Linjär regression (MKV) mellan tillgångar](/modelos/regressao_linear) | Dow Jones ~ S&P 500: β = 0,91 med R² = 0,91. Amerikansk statsobligation ~ S&P 500 har däremot R² 0,04: det ”uppenbara” sambandet förklarar nästan ingenting från dag till dag. |
| 05 | [Logistisk regression för riktning](/modelos/regressao_logistica) | Utanför urvalet (2016–2026) träffar den logistiska modellen 54,2 % av S&P 500:s riktning — i praktiken andelen uppgångsdagar (54,2 %): den förutsade uppgång 98 % av dagarna och har AUC 0,492. Hög träffsäkerhet utan särskiljande förmåga är fällan som den här baslinjen desarmerar. |
| 06 | [SVM och kärnmetoder](/modelos/svm_kernels) | Med bara RSI och volatilitet som indata når ingen av de fyra kärnorna över 50,7 % balanserad träffsäkerhet utanför urvalet. RBF ”lär sig” mest i träningen (53,2 %) och förlorar mest i testet (48,4 %): en kärna skapar ingen signal där ingen finns. |
| 07 | [Beslutsträd och Random Forest](/modelos/arvores_random_forest) | Ett träd med djup 20 träffar 83,7 % i träningen och 49,8 % i testet: det lärde sig det förflutna utantill. Den grunda skogen stannar på 53,5 % — blygsamt men ärligt; det mest använda attributet är ”ret_1”. |
| 08 | [MLP-neuralnät — vändningsindikator](/modelos/mlp_reversao) | För silver gav MLP:n 2023–2026 (aldrig sedda i träningen) 607 signaler om uppåtvändning med 17,3 % precision, mot en basfrekvens på 13,6 % (1,27× den naturliga frekvensen): det är den kvoten, inte den totala träffsäkerheten, som avgör om indikatorn tillför information. |
| 09 | [PCA — riskfaktorer och index](/modelos/pca_fatores) | Den 1:a faktorn ensam förklarar 24,5 % av den dagliga variationen hos 27 tillgångar; det krävs 12 faktorer för att nå 80 %. De 27 tillgångarna är inte 27 oberoende satsningar. |
| 10 | [Klustring av tillgångar (K-means)](/modelos/kmeans_clusters) | Siluetten väljer K = 4 grupper utan manuellt ingrepp; en grupp blandar 3 olika tillgångsklasser — etiketten ”råvara” eller ”valuta” säger inte hur tillgången beter sig. |
| 11 | [Avkastningsinbäddningar (FastICA) + cosinus](/modelos/embedding_retornos) | Under de senaste 60 handelsdagarna är det mest lika paret Brentolja × WTI-olja (cosinus 0,96) och det mest motsatta dollarindex × euro/dollar (-0,89): en närhetskarta som uppdateras i varje fönster. |
| 12 | [Isolation Forest — avvikande avkastning och volym](/modelos/isolation_forest) | Utan en enda etikett markerar isoleringsskogen 77 handelsdagar i S&P 500 som avvikande — 21 bara under 2020 — och 57 % av dem är nedgångar: avvikelsen är en signal om förändrad dynamik, inte brus att kasta bort. |
| 13 | [Avvikare med flera metoder (IQR, robust z, LOF)](/modelos/outliers_multimetodo) | För S&P 500 markerar lådagrammet 264 dagar som avvikare (6,7 % av urvalet); konsensus mellan tre metoder behåller 101. En enda avvikande punkt ändrar linjens lutning från 0,76 till 0,53. |
| 14 | [Markovkedja för regimer (upp, ner, sidled)](/modelos/markov_regimes) | För S&P 500 är sannolikheten, efter ett fallande block om 20 handelsdagar, 59,0 % att nästa block blir uppåt — högre än att fortsätta falla (30,8 %). I jämvikt tillbringar marknaden 41,3 % av tiden i en uppåtregim. |
| 15 | [Dold Markovmodell (gaussisk HMM)](/modelos/hmm_regimes) | Utan godtycklig gränsregel hittar HMM tre regimer i S&P 500: den turbulenta har 43 % årlig volatilitet mot 7 % i den lugna och varar i genomsnitt 18 handelsdagar. I dag är den mest sannolika regimen ”lugn”. |
| 16 | [Bayesiansk uppdatering av avkastning och volatilitet](/modelos/bayes_conjugado) | Guld sedan 2019: den genomsnittliga årsavkastningen a posteriori är 15,3 %, men 95 %-trovärdighetsintervallet går från 2,3 % till 28,4 %. Sannolikheten att medelvärdet är positivt är 98,9 % — stickprovsmedelvärdet (15,7 %) ensamt säger inte det. |
| 17 | [Fouriertransform — dominerande cykler](/modelos/fourier_ciclos) | Av de 12 största cykeltopparna i de fyra tillgångarna överstiger bara 2 brusgränsen på 95 % som erhålls genom att blanda själva avkastningarna. Varje periodogram har toppar; testet visar vilka som är cykler och vilka som är slump. |
| 18 | [Wavelets — tid-frekvensuppdelning](/modelos/wavelet_haar) | Nivå 1 (svängningar över 2 handelsdagar) rymmer 55,0 % av S&P 500:s energi. När högfrekvensenergin exploderar (z {">"} 2) är spridningen i avkastningen för de följande 20 handelsdagarna 1,3× den normala: waveleten placerar i tiden det Fourier bara ser i genomsnitt. |
| 19 | [Markowitz effektiva front](/modelos/markowitz_fronteira) | Portföljen med högst Sharpekvot hade 1,19 under 2010–2019 och levererade 0,76 under 2020–2026; lika vikter gick från 0,35 till 0,94. Fronten är exakt om det förflutna — felet ligger i att skatta medelvärden som framtiden inte upprepar. |
| 20 | [Genetisk algoritm — portföljoptimering](/modelos/ag_carteira) | Fyra parallella GA-körningar med olika frön konvergerar till samma portfölj (genomsnittlig viktavvikelse 0,1 procentenhet) med Sharpekvot 1,19 under 2010–2019. Under 2020–2026 levererar den 0,86, under lika vikter (0,94): konvergens bevisar att optimumet är stabilt, inte att framtiden upprepar det. |
| 21 | [Genetisk algoritm — val av indikatorer och parametrar](/modelos/ag_indicadores) | GA:n testade 1826 olika regler på S&P 500 och den bästa i varje körning hade en träningssharpekvot på upp till 0,78; under 2019–2026 låg de mellan 0,41 och 0,54, mot 0,77 för att bara ligga kvar köpt. Ju fler regler man testar, desto högre träningssharpekvot av ren slump. |
| 22 | [Genetisk programmering — symbolisk regression](/modelos/programacao_genetica) | Genetisk programmering upptäckte läsbara formler som ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 noder), med en rangkorrelation mot nästa avkastning på -0,080 i träningen och -0,028 i testet. Evolutionen hittar alltid ”något” i det förflutna; bara den osedda perioden skiljer indikator från tillfällighet. |
| 23 | [Hurstexponent och rullande Hurstindikator](/modelos/hurst_movel) | Det råa R/S-H ligger mellan 0,54 och 0,59 och skulle se ”ihållande” ut; mot blandade serier visar ingen av de 6 tillgångarna verkligt minne. Korsningen MH100 − MH150 slår glidande medelvärden i 3 av 6 tillgångar enligt Sharpekvot. |
| 24 | [Icke-linjär dynamik och tjocka svansar](/modelos/sistemas_nao_lineares) | Rörelser på 4 standardavvikelser inträffar, i median, 64× oftare än normalkurvan förutsäger; avkastningen har nästan inget minne (autokorrelation -0,02), men rörelsens storlek har det (0,15). |
| 25 | [Betingad volatilitet (EWMA och GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500: persistens α+β = 0,963 — en volatilitetschock behöver 18 handelsdagar för att förlora halva sin kraft. VaR 99 % för 1 dag: 1,75 %. |
| 26 | [Korrelationsnätverk och centralitet](/modelos/rede_correlacao) | Valda av nätverket 2010–2019 förblev de 8 perifera tillgångarna nästan oberoende 2020–2026 (genomsnittlig korrelation 0,00 mot 0,15 för de centrala) och gav mer (11,0 % mot 7,4 % per år), men med högre volatilitet. Den som slog båda korgarna var portföljen med alla 27 (Sharpe 0,95): antalet oberoende satsningar väger tyngre än positionen i nätverket. |
| 27 | [Grangerkausalitet och smitta](/modelos/causalidade_granger) | Av 72 testade par klarar 7 Bonferronikorrigeringen. Det starkaste, euro/dollar → dollarindex, är en artefakt av olika stängningstider mellan källorna: statistisk föregångare är inte orsak — och testet visar exakt var intuitionen skulle luras. |
| 28 | [Upptäckt av modell- och konceptdrift](/modelos/drift_modelo) | Modellen som tränats på 2010–2016 kräver omträning i 8 av de följande 10 åren: den periodens indataregim kom inte tillbaka. 2022 hade sämst träffsäkerhet (43,8 %) och 2017 störst förskjutning (KS 0,77) — att övervaka indata visar problemet utan att vänta på förlusten. |
| 29 | [Walk-forward-backtest med kostnader](/modelos/backtest_walkforward) | Med kostnader på 5 baspunkter per omsättning klarar 2 av 4 strategier de tre STOP-gränserna (lika vikter, riskparitet). Momentumfönstret, valt varje månad enbart utifrån det förflutna, ändrades 45 gånger — den ”optimala parametern” är inte konstant. |
| 30 | [Optimala handelsregler (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | Brent − WTI-spreaden återgår till medelvärdet med en halveringstid på 22 handelsdagar. Med 4 000 simulerade banor per cell är bästa regeln ett mål på 1,5σ med stopp vid 10,0σ (Sharpe per affär 0,63) — ett fast procentuellt stopp ignorerar tillgångens dynamik. |
| 31 | [Newcomb-Benfords lag — dataintegritet](/modelos/benford) | Endast 21 av de 29 volymserierna spänner över ett tillräckligt intervall för testet; att tillämpa Benford på de övriga vore falsklarm. Sammantaget spänner volymerna över 6,4 storleksordningar och ger MAD 0,0099 (godtagbar överensstämmelse). |
| 32 | [Förklarbarhet med Shapleyvärden (SHAP)](/modelos/shap_explicabilidade) | I den senaste prognosen stiger sannolikheten för uppgång från 54,0 % (modellens genomsnitt) till 55,4 %; attributet som vägde tyngst var ”ret_1” (+1,0 procentenhet). Den svarta lådan börjar svara på ”varför”. |

## Webbplatsen och labbet

Webbplatsen byggs med evidence.dev: SQL över resultaten, en interaktiv sida per modell och ett labb där Rust-motorn, kompilerad till WebAssembly, körs i din webbläsare — utan server och utan kostnad per användare.

- [Labb i webbläsaren (WebAssembly)](/laboratorio)
- [Tre motorer, ett resultat](/motores)
- [Fullständig katalog](/catalogo)

> Modellerna förutsäger inte framtiden med säkerhet — och säger det: flera resultat här visar att en populär metod saknar signal. Det är värdet: att veta var man inte ska lita innan man spenderar.

</div>

---

_quant_models_2026 · Upphovsperson: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
