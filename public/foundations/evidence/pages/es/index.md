---
title: "quant_models_2026 — 40 modelos cuantitativos para decidir bajo incertidumbre"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

<div style="text-align:center;">

🌐 [Português](/) · [English](/en) · **Español** · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · [한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div>

# Deje de elegir con hojas de cálculo. Empiece a decidir con modelos.

**32 modelos ejecutándose sobre 16 años de datos reales, tres motores (Python, Rust y F#) que coinciden bit a bit y un laboratorio que corre en su navegador — cada uno mostrando, con el dato, dónde engaña la intuición.**

> Usted ya lo hizo. Armó una hoja de cálculo con las alternativas — proveedores, celulares para el equipo, autos eléctricos para la flota, activos para la cartera, aeronaves para un escuadrón —, puso nota a cada criterio, ponderó, ordenó de mayor a menor y llevó al primero a la reunión. La hoja estaba bien. La decisión, no.
>
> **La hoja de cálculo no se equivoca en la cuenta. Se equivoca en la pregunta.**

Las hojas de cálculo, las matrices de puntuación y los filtros de clasificación tratan cada número como cierto. Ninguno pregunta cuánto de lo que usted ve es ruido, si el pasado todavía representa el futuro o si su 'mejor opción' sobreviviría a un período que nunca vio.

## Los 32 modelos, uno por uno

| # | Modelo | Lo que mostró el dato: |
|---:|---|---|
| 01 | [Estadística descriptiva robusta](/modelos/estatistica_descritiva) | La plata tiene una desviación estándar 1,6× mayor que su σ robusta: unos pocos días extremos inflan la volatilidad 'promedio' — curtosis en exceso de 26,9. |
| 02 | [Soporte y resistencia por moda + agrupamiento](/modelos/suporte_resistencia) | Oro: la moda de los precios redondeados es 3.330,00; la franja más visitada (2.350,00–2.730,00) concentra el 24% de las sesiones y hoy actúa como soporte. |
| 03 | [Estacionariedad (Augmented Dickey-Fuller)](/modelos/estacionariedade_adf) | 1 de 8 series de precio es estacionaria al 5%; en log-retorno, 8 de 8. Entrenar con precios es entrenar con una distribución que no vuelve. |
| 04 | [Regresión lineal (MCO) entre activos](/modelos/regressao_linear) | Dow Jones ~ S&P 500: β = 0,91 con R² = 0,91. En cambio, Bono del Tesoro de EE. UU. ~ S&P 500 tiene un R² de 0,04: la relación 'obvia' casi no explica el día a día. |
| 05 | [Regresión logística de dirección](/modelos/regressao_logistica) | Fuera de muestra (2016–2026) la logística acierta el 54,2% de la dirección del S&P 500 — prácticamente la fracción de días al alza (54,2%): predijo alza en el 98% de los días y tiene un AUC de 0,492. La exactitud alta sin poder de separación es la trampa que esta línea base desactiva. |
| 06 | [SVM y métodos de kernel](/modelos/svm_kernels) | Con solo RSI y volatilidad como entradas, ninguno de los cuatro kernels supera el 50,7% de exactitud balanceada fuera de muestra. El RBF es el que más 'aprende' en el entrenamiento (53,2%) y el que más pierde en la prueba (48,4%): un kernel no crea señal donde no la hay. |
| 07 | [Árboles de decisión y Random Forest](/modelos/arvores_random_forest) | Un árbol de profundidad 20 acierta el 83,7% en el entrenamiento y el 49,8% en la prueba: memorizó el pasado. El bosque poco profundo queda en el 53,5% — modesto, pero honesto; el atributo más usado es 'ret_1'. |
| 08 | [Red neuronal MLP — indicador de reversión](/modelos/mlp_reversao) | En la plata, en 2023–2026 (nunca vistos en el entrenamiento), la MLP emitió 607 señales de reversión al alza con una precisión del 17,3%, frente a una tasa base del 13,6% (1,27× la frecuencia natural): es esa razón, y no la exactitud general, la que dice si el indicador aporta información. |
| 09 | [PCA — factores de riesgo e índices](/modelos/pca_fatores) | El 1.er factor por sí solo explica el 24,5% de la variación diaria de 27 activos; se necesitan 12 factores para llegar al 80%. Los 27 activos no son 27 apuestas independientes. |
| 10 | [Agrupamiento de activos (K-means)](/modelos/kmeans_clusters) | La silueta elige K = 4 grupos sin intervención manual; hay un grupo que mezcla 3 clases de activo diferentes — la etiqueta 'materia prima' o 'divisa' no dice cómo se comporta el activo. |
| 11 | [Embeddings de retornos (FastICA) + coseno](/modelos/embedding_retornos) | En las últimas 60 sesiones, el par más parecido es Petróleo Brent × Petróleo WTI (coseno 0,96) y el más opuesto es Índice del dólar × Euro/Dólar (-0,89): un mapa de proximidad que se actualiza en cada ventana. |
| 12 | [Isolation Forest — retornos y volúmenes anormales](/modelos/isolation_forest) | Sin ninguna etiqueta, el bosque de aislamiento marca 77 sesiones del S&P 500 como anómalas — 21 solo en 2020 — y el 57% de ellas son caídas: la anomalía es señal de cambio de dinámica, no ruido que descartar. |
| 13 | [Valores atípicos multimétodo (IQR, z robusto, LOF)](/modelos/outliers_multimetodo) | En el S&P 500, el diagrama de caja marca 264 días como atípicos (6,7% de la muestra); el consenso de tres métodos se queda con 101. Un único punto discrepante cambia la pendiente de la recta de 0,76 a 0,53. |
| 14 | [Cadena de Markov de regímenes (alza, baja, lateral)](/modelos/markov_regimes) | En el S&P 500, estando a la baja en un bloque de 20 sesiones, la probabilidad de que el bloque siguiente sea al alza es del 59,0% — mayor que la de seguir a la baja (30,8%). En equilibrio, el mercado pasa el 41,3% del tiempo en régimen alcista. |
| 15 | [Modelo oculto de Markov (HMM gaussiano)](/modelos/hmm_regimes) | Sin regla de corte arbitraria, el HMM encuentra tres regímenes en el S&P 500: el turbulento tiene una volatilidad del 43% anual frente al 7% del calmo y dura en promedio 18 sesiones. Hoy el régimen más probable es 'calmo'. |
| 16 | [Actualización bayesiana de retorno y volatilidad](/modelos/bayes_conjugado) | Oro desde 2019: el retorno medio anual a posteriori es del 15,3%, pero el intervalo de credibilidad del 95% va del 2,3% al 28,4%. La probabilidad de que la media sea positiva es del 98,9% — la media muestral (15,7%) por sí sola no lo dice. |
| 17 | [Transformada de Fourier — ciclos dominantes](/modelos/fourier_ciclos) | De los 12 mayores picos de ciclo en los cuatro activos, solo 2 superan el umbral de ruido del 95% obtenido mezclando los propios retornos. Todo periodograma tiene picos; la prueba dice cuáles son ciclo y cuáles son azar. |
| 18 | [Wavelets — descomposición tiempo-frecuencia](/modelos/wavelet_haar) | El nivel 1 (oscilaciones de 2 sesiones) concentra el 55,0% de la energía del S&P 500. Cuando la energía de alta frecuencia explota (z {">"} 2), la dispersión del retorno de las 20 sesiones siguientes es 1,3× la normal: la wavelet localiza en el tiempo lo que Fourier solo ve en promedio. |
| 19 | [Frontera eficiente de Markowitz](/modelos/markowitz_fronteira) | La cartera de máximo Sharpe tenía un Sharpe de 1,19 en 2010–2019 y entregó 0,76 en 2020–2026; los pesos iguales pasaron de 0,35 a 0,94. La frontera es exacta sobre el pasado — el error está en estimar medias que el futuro no repite. |
| 20 | [Algoritmo genético — optimización de cartera](/modelos/ag_carteira) | Cuatro corridas paralelas del AG, con semillas distintas, convergen a la misma cartera (desviación media de peso de 0,1 p.p.) con un Sharpe de 1,19 en 2010–2019. En 2020–2026 entrega 0,86, por debajo de los pesos iguales (0,94): la convergencia prueba que el óptimo es estable, no que el futuro vaya a repetirlo. |
| 21 | [Algoritmo genético — selección de indicadores y parámetros](/modelos/ag_indicadores) | El AG probó 1826 reglas distintas sobre el S&P 500 y la mejor de cada corrida tuvo un Sharpe de entrenamiento de hasta 0,78; en 2019–2026 quedaron entre 0,41 y 0,54, frente a 0,77 de simplemente mantenerse comprado. Cuantas más reglas se prueban, mayor el Sharpe de entrenamiento por puro azar. |
| 22 | [Programación genética — regresión simbólica](/modelos/programacao_genetica) | La programación genética descubrió fórmulas legibles como ((sen(cos(r3)) + r1) + sen(sen(cos(r2)))) (10 nodos), con una correlación de rangos de -0,080 con el próximo retorno en el entrenamiento y -0,028 en la prueba. La evolución siempre encuentra 'algo' en el pasado; solo el período nunca visto separa indicador de coincidencia. |
| 23 | [Exponente de Hurst e indicador Hurst móvil](/modelos/hurst_movel) | El H bruto de R/S queda entre 0,54 y 0,59 y parecería 'persistente'; frente a series mezcladas, ninguno de los 6 activos muestra memoria real. El cruce MH100 − MH150 supera al de medias móviles en 3 de 6 activos por ratio de Sharpe. |
| 24 | [Dinámica no lineal y colas pesadas](/modelos/sistemas_nao_lineares) | Los movimientos de 4 desviaciones ocurren, en mediana, 64× más de lo que prevé la curva normal; el retorno casi no tiene memoria (autocorrelación -0,02), pero el tamaño del movimiento sí (0,15). |
| 25 | [Volatilidad condicional (EWMA y GARCH(1,1))](/modelos/garch_volatilidade) | S&P 500: persistencia α+β = 0,963 — un choque de volatilidad tarda 18 sesiones en perder la mitad de su fuerza. VaR 99% a 1 día: 1,75%. |
| 26 | [Red de correlación y centralidad](/modelos/rede_correlacao) | Elegidos por la red de 2010–2019, los 8 periféricos siguieron casi independientes en 2020–2026 (correlación media 0,00 frente a 0,15 de los centrales) y rindieron más (11,0% frente a 7,4% anual), aunque con más volatilidad. Quien venció a ambas canastas fue la cartera con los 27 (Sharpe 0,95): el número de apuestas independientes pesa más que la posición en la red. |
| 27 | [Causalidad de Granger y contagio](/modelos/causalidade_granger) | De los 72 pares probados, 7 sobreviven a la corrección de Bonferroni. El más fuerte, Euro/Dólar → Índice del dólar, es un artefacto del horario de cierre entre fuentes distintas: la precedencia estadística no es causa — y la prueba muestra exactamente dónde se engañaría la intuición. |
| 28 | [Detección de deriva de modelo y de concepto](/modelos/drift_modelo) | El modelo entrenado en 2010–2016 pide reentrenamiento en 8 de los 10 años siguientes: el régimen de entrada de aquel período no volvió. 2022 tuvo la peor exactitud (43,8%) y 2017 el mayor desplazamiento (KS 0,77) — monitorear la entrada muestra el problema sin esperar la pérdida. |
| 29 | [Backtest walk-forward con costos](/modelos/backtest_walkforward) | Con costos de 5 pb por rotación, 2 de 4 estrategias pasan las tres compuertas STOP (Pesos iguales, Paridad de riesgo). La ventana del momentum, elegida cada mes solo con el pasado, cambió 45 veces — el 'parámetro óptimo' no es constante. |
| 30 | [Reglas óptimas de trading (Ornstein-Uhlenbeck)](/modelos/triple_barrier_ou) | El spread Brent − WTI revierte a la media con una vida media de 22 sesiones. Simulando 4.000 trayectorias por celda, la mejor regla es un objetivo de 1,5σ con un stop de 10,0σ (Sharpe por operación 0,63) — un stop porcentual fijo ignora la dinámica del activo. |
| 31 | [Ley de Newcomb-Benford — integridad de datos](/modelos/benford) | Solo 21 de las 29 series de volumen cubren amplitud suficiente para la prueba; aplicar Benford a las demás sería una falsa alarma. Agregados, los volúmenes cubren 6,4 órdenes de magnitud y dan un MAD de 0,0099 (conformidad aceptable). |
| 32 | [Explicabilidad con valores de Shapley (SHAP)](/modelos/shap_explicabilidade) | En la última predicción, la probabilidad de alza pasa del 54,0% (promedio del modelo) al 55,4%; el atributo que más pesó fue 'ret_1' (+1,0 p.p.). La caja negra empieza a responder 'por qué'. |

## El sitio y el laboratorio

El sitio se genera con evidence.dev: SQL sobre los resultados, una página interactiva por modelo y un laboratorio en el que el motor Rust, compilado a WebAssembly, corre en su navegador — sin servidor y sin costo por usuario.

- [Laboratorio en el navegador (WebAssembly)](/laboratorio)
- [Tres motores, un resultado](/motores)
- [Catálogo completo](/catalogo)

> Los modelos no predicen el futuro con certeza — y lo dicen: varios resultados aquí muestran que un método popular no tiene señal. Ese es el valor: saber dónde no confiar antes de gastar.

</div>

---

_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
