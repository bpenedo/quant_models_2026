---
title: "17 · Transformada de Fourier — ciclos dominantes"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Atualização bayesiana de retorno e volatilidade](/modelos/bayes_conjugado) · [Catálogo](/catalogo) · [Wavelets — decomposição tempo-frequência →](/modelos/wavelet_haar)

**Tipo:** Processamento de sinais · **Categoria:** Ciclos e tendência · **Fonte na base de conhecimento:** Quant Q7, Q10, Q11, Q13, Q14; Fourier

Decompõe a série de retornos (sem tendência) em senoides e mede a energia de cada frequência pelo periodograma da FFT. Os picos indicam ciclos dominantes em pregões, como sazonalidades semanais, mensais ou de safra. Compara o espectro com o de ruído aleatório para separar ciclo real de coincidência e reconstrói a série só com as frequências relevantes, como um filtro passa-baixa.

> **Leitura dos dados:** Dos 12 maiores picos de ciclo nos quatro ativos, só 2 superam o limiar de ruído de 95% obtido embaralhando os próprios retornos. Todo periodograma tem picos; o teste diz quais são ciclo e quais são acaso.

```sql fourier_ciclos__picos
select * from quant.fourier_ciclos__picos
```
```sql fourier_ciclos__espectro
select * from quant.fourier_ciclos__espectro
```

<DataTable data={fourier_ciclos__picos}>
  <Column id=nome/><Column id=periodo_semanas title="Período (semanas)" fmt=num1/><Column id=potencia fmt=num5/>
  <Column id=limiar_ruido_95 title="Limiar de ruído 95%" fmt=num5/><Column id=significativo/>
</DataTable>
<LineChart data={fourier_ciclos__espectro} x=periodo_semanas y=potencia series=nome xLog=true title="Periodograma (retornos semanais)"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so fourier_ciclos     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Atualização bayesiana de retorno e volatilidade](/modelos/bayes_conjugado) · [Catálogo](/catalogo) · [Wavelets — decomposição tempo-frequência →](/modelos/wavelet_haar)
