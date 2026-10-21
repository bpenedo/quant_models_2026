---
title: "18 · Wavelets — decomposição tempo-frequência"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Transformada de Fourier — ciclos dominantes](/modelos/fourier_ciclos) · [Catálogo](/catalogo) · [Fronteira eficiente de Markowitz →](/modelos/markowitz_fronteira)

**Tipo:** Processamento de sinais · **Categoria:** Ciclos e tendência · **Fonte na base de conhecimento:** Fourier [32], [33]; Modelos [152], [153], [155]

A transformada wavelet discreta separa o log-retorno em aproximação (baixa frequência, tendência) e detalhes (alta frequência) em vários níveis, mantendo a localização no tempo, o que Fourier não faz. Aumentos de energia nos coeficientes de detalhe antecedem mudanças de tendência, base de estudos de reversão na bolsa brasileira e de previsão de direção do S&P 500 com SVM.

> **Leitura dos dados:** O nível 1 (oscilações de 2 pregões) concentra 55,0% da energia do S&P 500. Quando a energia de alta frequência explode (z {">"} 2), a dispersão do retorno dos 20 pregões seguintes é 1,3× a normal: a wavelet localiza no tempo o que Fourier só vê na média.

```sql wavelet_haar__energia_niveis
select * from quant.wavelet_haar__energia_niveis
```
```sql wavelet_haar__sinal
select * from quant.wavelet_haar__sinal
```

<BarChart data={wavelet_haar__energia_niveis} x=escala_pregoes y=fracao_energia yFmt=pct0 title="Energia por escala (pregões)"/>
<LineChart data={wavelet_haar__sinal} x=data y=energia_detalhe_z title="Energia de alta frequência (z)">
  <ReferenceLine y=2 label="z = 2"/>
</LineChart>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so wavelet_haar     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Transformada de Fourier — ciclos dominantes](/modelos/fourier_ciclos) · [Catálogo](/catalogo) · [Fronteira eficiente de Markowitz →](/modelos/markowitz_fronteira)
