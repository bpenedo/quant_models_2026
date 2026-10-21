---
title: "quant_models_2026 — 40 kvantitatiivista mallia päätöksiin epävarmuudessa"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · [English](/en) · [Español](/es) · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · **Suomi**

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Lopeta valitseminen taulukkolaskennalla. Ala päättää mallilla.

**32 mallia 16 vuoden todellisella datalla, kolme moottoria (Python, Rust ja F#), jotka täsmäävät bitilleen, ja selaimessasi toimiva laboratorio — jokainen näyttää datalla, missä intuitio johtaa harhaan.**

> Olet tehnyt tämän. Teit taulukon vaihtoehdoista — toimittajat, puhelimet tiimille, sähköautot kalustoon, sijoitukset salkkuun, lentokoneet laivueelle —, pisteytit jokaisen kriteerin, painotit, lajittelit suurimmasta pienimpään ja veit ykkösen kokoukseen. Taulukko oli oikeassa. Päätös ei.
>
> **Taulukkolaskenta ei laske väärin. Se kysyy väärin.**

Taulukot, pisteytysmatriisit ja järjestyssuodattimet pitävät jokaista lukua varmana. Mikään niistä ei kysy, kuinka paljon näkemästäsi on kohinaa, edustaako menneisyys yhä tulevaa tai kestäisikö ”paras vaihtoehtosi” jakson, jota se ei ole koskaan nähnyt.

## 32 mallia yksi kerrallaan

| # | Malli | Mitä data näytti: |
|---:|---|---|
| 01 | [Robusti kuvaileva tilastotiede](/modelos/estatistica_descritiva) | Hopean keskihajonta on 1,6-kertainen robustiin σ:aan nähden: muutamat äärimmäiset päivät paisuttavat ”keskimääräistä” volatiliteettia — huipukkuuden ylite 26,9. |
| 02 | [Tuki ja vastus moodilla + klusteroinnilla](/modelos/suporte_resistencia) | Kulta: pyöristettyjen hintojen moodi on 3 330,00; useimmin käyty vyöhyke (2 350,00–2 730,00) kattaa 24 % kaupankäyntipäivistä ja toimii nyt tukena. |
| 03 | [Stationaarisuus (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | Vain 1 hintasarja 8:sta on stationaarinen 5 %:n tasolla; logaritmisina tuottoina 8/8. Hinnoilla opettaminen on opettamista jakaumalla, joka ei palaa. |
| 04 | [Lineaarinen regressio (PNS) kohteiden välillä](/modelos/regressao_linear) | Dow Jones ~ S&P 500: β = 0,91 ja R² = 0,91. Sen sijaan Yhdysvaltain valtionlaina ~ S&P 500 antaa R²:ksi 0,04: ”ilmeinen” yhteys ei selitä päivittäistä liikettä juuri lainkaan. |
| 05 | [Suunnan logistinen regressio](/modelos/regressao_logistica) | Otoksen ulkopuolella (2016–2026) logistinen malli osuu S&P 500:n suuntaan 54,2 %:ssa — käytännössä nousupäivien osuus (54,2 %): se ennusti nousua 98 %:na päivistä, ja AUC on 0,492. Korkea tarkkuus ilman erottelukykyä on ansa, jonka tämä vertailukohta purkaa. |
| 06 | [SVM ja ydinmenetelmät](/modelos/svm_kernels) | Kun syötteinä ovat vain RSI ja volatiliteetti, yksikään neljästä ytimestä ei ylitä 50,7 %:n tasapainotettua tarkkuutta otoksen ulkopuolella. RBF ”oppii” eniten opetuksessa (53,2 %) ja häviää eniten testissä (48,4 %): ydin ei luo signaalia sinne, missä sitä ei ole. |
| 07 | [Päätöspuut ja Random Forest](/modelos/arvores_random_forest) | Syvyyden 20 puu osuu oikeaan 83,7 %:ssa opetuksessa ja 49,8 %:ssa testissä: se opetteli menneen ulkoa. Matala metsä jää 53,5 %:iin — vaatimatonta mutta rehellistä; eniten käytetty piirre on ”ret_1”. |
| 08 | [MLP-neuroverkko — käänneindikaattori](/modelos/mlp_reversao) | Hopealla vuosina 2023–2026 (joita opetus ei nähnyt) MLP antoi 607 nousukäänteen signaalia 17,3 %:n tarkkuudella, kun perustaso oli 13,6 % (1,27-kertainen luonnolliseen yleisyyteen): juuri tämä suhde, ei kokonaistarkkuus, kertoo, tuoko indikaattori tietoa. |
| 09 | [PCA — riskitekijät ja indeksit](/modelos/pca_fatores) | Ensimmäinen tekijä yksinään selittää 24,5 % 27 kohteen päivittäisestä vaihtelusta; 80 %:iin tarvitaan 12 tekijää. 27 kohdetta eivät ole 27 riippumatonta panosta. |
| 10 | [Kohteiden klusterointi (K-means)](/modelos/kmeans_clusters) | Siluetti valitsee K = 4 ryhmää ilman manuaalista puuttumista; yksi ryhmä sekoittaa 3 eri omaisuusluokkaa — tunniste ”raaka-aine” tai ”valuutta” ei kerro, miten kohde käyttäytyy. |
| 11 | [Tuottojen upotukset (FastICA) + kosini](/modelos/embedding_retornos) | Viimeisten 60 kaupankäyntipäivän aikana samankaltaisin pari on Brent-öljy × WTI-öljy (kosini 0,96) ja vastakkaisin dollari-indeksi × euro/dollari (-0,89): läheisyyskartta, joka päivittyy joka ikkunassa. |
| 12 | [Isolation Forest — poikkeavat tuotot ja volyymit](/modelos/isolation_forest) | Ilman ainuttakaan merkintää eristysmetsä merkitsee 77 S&P 500:n kaupankäyntipäivää poikkeaviksi — 21 pelkästään vuonna 2020 — ja niistä 57 % on laskuja: poikkeama on signaali muuttuneesta dynamiikasta, ei pois heitettävää kohinaa. |
| 13 | [Poikkeavat havainnot monella menetelmällä (IQR, robusti z, LOF)](/modelos/outliers_multimetodo) | S&P 500:ssa laatikkokuvio merkitsee 264 päivää poikkeaviksi (6,7 % otoksesta); kolmen menetelmän konsensus jättää 101. Yksi poikkeava piste muuttaa suoran kulmakertoimen 0,76:sta 0,53:een. |
| 14 | [Markovin ketju markkinatiloille (nousu, lasku, sivuttais)](/modelos/markov_regimes) | S&P 500:ssa laskevan 20 kaupankäyntipäivän jakson jälkeen todennäköisyys seuraavan jakson nousulle on 59,0 % — suurempi kuin laskun jatkuminen (30,8 %). Tasapainossa markkina viettää 41,3 % ajasta noususuhdanteessa. |
| 15 | [Piilo-Markov-malli (gaussinen HMM)](/modelos/hmm_regimes) | Ilman mielivaltaista katkaisusääntöä HMM löytää S&P 500:sta kolme tilaa: myrskyisän tilan vuotuinen volatiliteetti on 43 %, rauhallisen 7 %, ja myrskyisä kestää keskimäärin 18 kaupankäyntipäivää. Tänään todennäköisin tila on ”rauhallinen”. |
| 16 | [Tuoton ja volatiliteetin bayesilainen päivitys](/modelos/bayes_conjugado) | Kulta vuodesta 2019: posteriorinen keskimääräinen vuosituotto on 15,3 %, mutta 95 %:n uskottavuusväli on 2,3 %:sta 28,4 %:iin. Todennäköisyys, että keskiarvo on positiivinen, on 98,9 % — otoskeskiarvo (15,7 %) ei yksin kerro sitä. |
| 17 | [Fourier-muunnos — hallitsevat syklit](/modelos/fourier_ciclos) | Neljän kohteen 12 suurimmasta syklihuipusta vain 2 ylittää 95 %:n kohinarajan, joka saadaan sekoittamalla itse tuotot. Jokaisessa periodogrammissa on huippuja; testi kertoo, mitkä ovat syklejä ja mitkä sattumaa. |
| 18 | [Aallokkeet — aika-taajuushajotelma](/modelos/wavelet_haar) | Taso 1 (2 kaupankäyntipäivän värähtelyt) sisältää 55,0 % S&P 500:n energiasta. Kun korkean taajuuden energia räjähtää (z {">"} 2), seuraavien 20 päivän tuoton hajonta on 1,3-kertainen normaaliin: aalloke paikantaa ajassa sen, minkä Fourier näkee vain keskimäärin. |
| 19 | [Markowitzin tehokas rintama](/modelos/markowitz_fronteira) | Suurimman Sharpen salkun Sharpen luku oli 1,19 vuosina 2010–2019 ja 0,76 vuosina 2020–2026; tasapainotus nousi 0,35:stä 0,94:ään. Rintama on tarkka menneestä — virhe on sellaisten keskiarvojen estimoinnissa, joita tulevaisuus ei toista. |
| 20 | [Geneettinen algoritmi — salkun optimointi](/modelos/ag_carteira) | Neljä rinnakkaista GA-ajoa eri siemenillä suppenee samaan salkkuun (keskimääräinen painopoikkeama 0,1 prosenttiyksikköä), Sharpen luku 1,19 vuosina 2010–2019. Vuosina 2020–2026 se tuottaa 0,86, alle tasapainotuksen (0,94): suppeneminen todistaa optimin vakauden, ei sitä, että tulevaisuus toistaa sen. |
| 21 | [Geneettinen algoritmi — indikaattorien ja parametrien valinta](/modelos/ag_indicadores) | GA testasi S&P 500:lla 1826 eri sääntöä, ja kunkin ajon parhaan opetusjakson Sharpen luku oli enintään 0,78; vuosina 2019–2026 ne asettuivat välille 0,41–0,54, kun pelkkä ostettuna pysyminen antoi 0,77. Mitä enemmän sääntöjä testataan, sitä korkeammaksi opetusjakson Sharpen luku nousee puhtaasta sattumasta. |
| 22 | [Geneettinen ohjelmointi — symbolinen regressio](/modelos/programacao_genetica) | Geneettinen ohjelmointi löysi luettavia kaavoja, kuten ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 solmua), joiden järjestyskorrelaatio seuraavaan tuottoon oli opetuksessa -0,080 ja testissä -0,028. Evoluutio löytää menneestä aina ”jotakin”; vain näkemätön jakso erottaa indikaattorin sattumasta. |
| 23 | [Hurstin eksponentti ja liukuva Hurst-indikaattori](/modelos/hurst_movel) | Raaka R/S-H on välillä 0,54–0,59 ja näyttäisi ”pysyvältä”; sekoitettuihin sarjoihin verrattuna yksikään 6 kohteesta ei osoita todellista muistia. MH100 − MH150 -risteys voittaa liukuvien keskiarvojen risteyksen 3 kohteessa 6:sta Sharpen luvulla mitattuna. |
| 24 | [Epälineaarinen dynamiikka ja paksut hännät](/modelos/sistemas_nao_lineares) | Neljän keskihajonnan liikkeitä esiintyy mediaanina 64 kertaa useammin kuin normaalikäyrä ennustaa; tuotolla ei ole juuri muistia (autokorrelaatio -0,02), mutta liikkeen suuruudella on (0,15). |
| 25 | [Ehdollinen volatiliteetti (EWMA ja GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500: pysyvyys α+β = 0,963 — volatiliteettisokki tarvitsee 18 kaupankäyntipäivää menettääkseen puolet voimastaan. Yhden päivän 99 %:n VaR: 1,75 %. |
| 26 | [Korrelaatioverkko ja keskeisyys](/modelos/rede_correlacao) | Vuosien 2010–2019 verkon valitsemat 8 reunakohdetta pysyivät vuosina 2020–2026 lähes riippumattomina (keskikorrelaatio 0,00, keskeisillä 0,15) ja tuottivat enemmän (11,0 % vs. 7,4 % vuodessa), mutta suuremmalla volatiliteetilla. Molemmat korit voitti kaikkien 27:n salkku (Sharpe 0,95): riippumattomien panosten määrä painaa enemmän kuin asema verkossa. |
| 27 | [Grangerin kausaliteetti ja tartunta](/modelos/causalidade_granger) | Testatuista 72 parista 7 kestää Bonferronin korjauksen. Vahvin, euro/dollari → dollari-indeksi, on eri lähteiden sulkemisaikojen artefakti: tilastollinen edeltävyys ei ole syy — ja testi näyttää tarkasti, missä intuitio menisi harhaan. |
| 28 | [Mallin ja käsitteen ajautumisen tunnistus](/modelos/drift_modelo) | Vuosilla 2010–2016 opetettu malli vaatii uudelleenopetusta 8:na seuraavista 10 vuodesta: sen jakson syötetila ei palannut. Vuonna 2022 tarkkuus oli heikoin (43,8 %) ja vuonna 2017 siirtymä suurin (KS 0,77) — syötteen seuranta paljastaa ongelman odottamatta tappiota. |
| 29 | [Walk-forward-jälkitestaus kustannuksineen](/modelos/backtest_walkforward) | Kun kustannus on 5 peruspistettä vaihtoa kohden, 2 strategiaa 4:stä läpäisee kolme STOP-porttia (tasapainotus, riskipariteetti). Joka kuukausi pelkän menneen perusteella valittu momentum-ikkuna vaihtui 45 kertaa — ”optimaalinen parametri” ei ole vakio. |
| 30 | [Optimaaliset kaupankäyntisäännöt (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | Brent − WTI -erotus palautuu keskiarvoon 22 kaupankäyntipäivän puoliintumisajalla. Simuloimalla 4 000 polkua ruutua kohden paras sääntö on 1,5σ:n tavoite ja 10,0σ:n stop (Sharpe per kauppa 0,63) — kiinteä prosentuaalinen stop ohittaa kohteen dynamiikan. |
| 31 | [Newcomb-Benfordin laki — datan eheys](/modelos/benford) | Vain 21 volyymisarjasta 29:stä kattaa testiin riittävän vaihteluvälin; Benfordin soveltaminen muihin olisi väärä hälytys. Yhdistettyinä volyymit kattavat 6,4 suuruusluokkaa ja antavat MAD-arvon 0,0099 (hyväksyttävä yhdenmukaisuus). |
| 32 | [Selitettävyys Shapley-arvoilla (SHAP)](/modelos/shap_explicabilidade) | Viimeisimmässä ennusteessa nousun todennäköisyys kasvaa 54,0 %:sta (mallin keskiarvo) 55,4 %:iin; eniten painoi piirre ”ret_1” (+1,0 prosenttiyksikköä). Musta laatikko alkaa vastata kysymykseen ”miksi”. |

## Sivusto ja laboratorio

Sivusto tehdään evidence.dev:llä: SQL tulosten päällä, interaktiivinen sivu jokaiselle mallille ja laboratorio, jossa WebAssemblyksi käännetty Rust-moottori toimii selaimessasi — ilman palvelinta ja ilman käyttäjäkohtaisia kustannuksia.

- [Laboratorio selaimessa (WebAssembly)](/laboratorio)
- [Kolme moottoria, yksi tulos](/motores)
- [Täydellinen luettelo](/catalogo)

> Mallit eivät ennusta tulevaa varmasti — ja sanovat sen: useat tulokset tässä osoittavat, ettei suositussa menetelmässä ole signaalia. Se on arvo: tietää, mihin ei pidä luottaa ennen kuin rahaa käytetään.

</div>

---

_quant_models_2026 · Tekijä: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
