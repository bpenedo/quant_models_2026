---
title: "32 · Explicabilidade com valores de Shapley (SHAP)"
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

[← Lei de Newcomb-Benford — integridade de dados](/modelos/benford) · [Catálogo](/catalogo)

**Tipo:** Governança de modelos · **Categoria:** Validação e monitoramento · **Fonte na base de conhecimento:** Modelos [74], [100], [101], [113], [120], [129]

Abre a caixa-preta: para cada previsão, distribui a contribuição de cada variável de entrada segundo os valores de Shapley da teoria dos jogos, com sinal (empurra para cima ou para baixo) e magnitude. Mostra o compromisso entre poder preditivo e interpretabilidade e permite responder 'por que o modelo mandou comprar hoje?' com indicadores e patamares concretos, requisito para auditoria e para confiança do decisor.

> **Leitura dos dados:** Na última previsão, a probabilidade de alta sai de 54,0% (média do modelo) para 55,4%; o atributo que mais pesou foi 'ret_1' (+1,0 p.p.). A caixa-preta passa a responder 'por quê'.

```sql shap_explicabilidade__importancia
select * from quant.shap_explicabilidade__importancia
```
```sql shap_explicabilidade__ultima_previsao
select * from quant.shap_explicabilidade__ultima_previsao
```

<BarChart data={shap_explicabilidade__ultima_previsao} x=atributo y=contribuicao swapXY=true title="Contribuição de cada atributo na última previsão"/>
<BarChart data={shap_explicabilidade__importancia} x=atributo y=shap_medio_abs swapXY=true title="Importância média |SHAP|"/>


## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so shap_explicabilidade     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

[← Lei de Newcomb-Benford — integridade de dados](/modelos/benford) · [Catálogo](/catalogo)
