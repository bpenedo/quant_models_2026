---
title: "06 · SVM e métodos de kernel"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Regressão logística de direção](/modelos/regressao_logistica) · [Catálogo](/catalogo) · [Árvores de decisão e Random Forest →](/modelos/arvores_random_forest)

**Tipo:** Aprendizado supervisionado · **Categoria:** Previsão de direção · **Fonte na base de conhecimento:** Quant Q20, Q39, Q46, Q50, Q55, Q56, Q196–224

Máquina de vetores de suporte que busca o hiperplano de margem máxima entre classes. Os kernels linear, polinomial, RBF e sigmoide projetam os dados em espaços de maior dimensão onde problemas não lineares ficam separáveis, sem criar as colunas em memória (kernel trick). Compara as quatro fronteiras de decisão sobre os mesmos dados de mercado e mostra o custo do kernel mais flexível: overfitting.

> **Leitura dos dados:** Com só RSI e volatilidade como entradas, nenhum dos quatro kernels passa de 50,7% de acurácia balanceada fora da amostra. O RBF é o que mais 'aprende' no treino (53,2%) e o que mais perde no teste (48,4%): kernel não cria sinal onde ele não existe.

```sql svm_kernels__kernels
select * from quant.svm_kernels__kernels
```

<BarChart data={svm_kernels__kernels} x=kernel y={["acuracia_treino","acuracia_teste"]} type=grouped yFmt=pct1 title="Acurácia balanceada: treino × teste"/>

<DataTable data={svm_kernels__kernels}/>

![Fronteiras de decisão](/telas/svm_kernels.png)


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so svm_kernels     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Regressão logística de direção](/modelos/regressao_logistica) · [Catálogo](/catalogo) · [Árvores de decisão e Random Forest →](/modelos/arvores_random_forest)
