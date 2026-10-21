#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Gera o site evidence.dev a partir do catálogo e dos CSVs dos modelos.

Escreve:
  evidence/sources/quant/<tabela>.sql      uma consulta por CSV (DuckDB em memória)
  evidence/pages/index.md                  vitrine (PT-BR)
  evidence/pages/modelos/<id>.md           uma página por modelo da fase 1
  evidence/pages/catalogo.md               os 40 modelos, incluindo a fase 2
  evidence/pages/motores.md                três motores + benchmark medido
  evidence/static/qm_core.wasm             motor Rust compilado para wasm32
  evidence/static/laboratorio.json         retornos diários usados no laboratório
  evidence/static/img/logo_capa.png

Uso:  python3 gerar_site.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_modelos import MODELOS  # noqa: E402
from config import RAIZ, escrever  # noqa: E402

EV = RAIZ / "public/foundations/evidence"
DADOS = EV / "dados/quant"
RUST = RAIZ / "public/foundations/rust/quant_models_2026_core"
CAB = ("<!--\nquant_models_2026\nAutor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS\n"
       "E-mail: profbruanbima@gmail.com\n-->\n")
SELETOR = ("🌐 **Português** · [English](/en) · [Español](/es) · [Français](/fr) · [Deutsch](/de) · [中文](/zh) · "
           "[한국어](/ko) · [हिन्दी](/hi) · [עברית](/he) · [Русский](/ru) · [Svenska](/sv) · [Suomi](/fi)")


def esc(t: str) -> str:
    """Texto livre em página evidence vira Svelte DEPOIS do Markdown — e o Markdown decodifica
    entidades (&lt; volta a ser '<'). A forma segura é a expressão Svelte {"<"} — ver bugs.md."""
    m = {"{": '{"{"}', "}": '{"}"}', "<": '{"<"}', ">": '{">"}'}
    return "".join(m.get(c, c) for c in str(t))


def q(nome: str, sql: str | None = None) -> str:
    return f"```sql {nome}\n{sql or f'select * from quant.{nome}'}\n```\n"


# Corpo de cada página: consultas + componentes. Texto explicativo vem do catálogo e da leitura.
PAGINAS: dict[str, str] = {
    "estatistica_descritiva": q("estatistica_descritiva__resumo") + """
<BarChart data={estatistica_descritiva__resumo} x=nome y={["vol_anual_pct","sigma_robusta_anual_pct"]} type=grouped swapXY=true title="Desvio-padrão × σ robusta (% a.a.)" yFmt=num1/>

<DataTable data={estatistica_descritiva__resumo} rows=30 search=true>
  <Column id=nome title="Ativo"/><Column id=classe title="Classe"/>
  <Column id=media_anual_pct title="Retorno médio % a.a." fmt=num1/><Column id=vol_anual_pct title="Vol % a.a." fmt=num1/>
  <Column id=sigma_robusta_anual_pct title="σ robusta % a.a." fmt=num1/><Column id=curtose_excesso title="Curtose" fmt=num1/>
  <Column id=pior_dia_pct title="Pior dia %" fmt=num1/><Column id=melhor_dia_pct title="Melhor dia %" fmt=num1/>
</DataTable>
""",
    "suporte_resistencia": q("suporte_resistencia__preco") + q("suporte_resistencia__faixas") + """
<LineChart data={suporte_resistencia__preco} x=data y=fechamento title="Ouro — 2 anos" yFmt=num0>
{#each suporte_resistencia__faixas as f}
  <ReferenceArea yMin={f.minimo} yMax={f.maximo} color={f.tipo === 'suporte' ? 'positive' : 'negative'} label="{f.tipo} · {Math.round(f.intensidade_pct)}%"/>
{/each}
</LineChart>

<DataTable data={suporte_resistencia__faixas}/>
""",
    "estacionariedade_adf": q("estacionariedade_adf__adf") + """
<BarChart data={estacionariedade_adf__adf} x=nome y=estatistica_adf series=forma type=grouped title="Estatística ADF (abaixo de −2,86 = estacionária a 5%)">
  <ReferenceLine y=-2.86 label="crítico 5%"/>
</BarChart>

<DataTable data={estacionariedade_adf__adf}/>
""",
    "regressao_linear": q("regressao_linear__coeficientes") + q("regressao_linear__dispersao") + """
<DataTable data={regressao_linear__coeficientes}>
  <Column id=rotulo title="Relação"/><Column id=beta fmt=num2/><Column id=ic95_inf title="IC 95% inf." fmt=num2/>
  <Column id=ic95_sup title="IC 95% sup." fmt=num2/><Column id=r2 title="R²" fmt=num2/><Column id=correlacao fmt=num2/>
</DataTable>

<Dropdown data={regressao_linear__coeficientes} name=par value=rotulo defaultValue="Dow Jones ~ S&P 500" title="Relação"/>

```sql par_sel
select * from quant.regressao_linear__dispersao where par = '${inputs.par.value}'
```

<ScatterPlot data={par_sel} x=x_pct y=y_pct title="Retornos diários (%)"/>
""",
    "regressao_logistica": q("regressao_logistica__metricas") + q("regressao_logistica__acerto_anual") + q("regressao_logistica__coeficientes") + """
<BigValue data={regressao_logistica__metricas} value=acuracia title="Acurácia fora da amostra" fmt=pct1/>
<BigValue data={regressao_logistica__metricas} value=taxa_base_alta title="Dias de alta (taxa-base)" fmt=pct1/>
<BigValue data={regressao_logistica__metricas} value=auc title="AUC" fmt=num3/>

<BarChart data={regressao_logistica__acerto_anual} x=ano y=acerto yFmt=pct1 title="Acerto por ano (walk-forward)">
  <ReferenceLine y={regressao_logistica__metricas[0]?.taxa_base_alta} label="taxa-base"/>
</BarChart>

<BarChart data={regressao_logistica__coeficientes} x=atributo y=coeficiente swapXY=true title="Coeficientes padronizados"/>
""",
    "svm_kernels": q("svm_kernels__kernels") + """
<BarChart data={svm_kernels__kernels} x=kernel y={["acuracia_treino","acuracia_teste"]} type=grouped yFmt=pct1 title="Acurácia balanceada: treino × teste"/>

<DataTable data={svm_kernels__kernels}/>

![Fronteiras de decisão](/telas/svm_kernels.png)
""",
    "arvores_random_forest": q("arvores_random_forest__profundidade") + q("arvores_random_forest__importancia") + q("arvores_random_forest__metricas") + """
<LineChart data={arvores_random_forest__profundidade} x=profundidade y={["acuracia_treino","acuracia_teste"]} yFmt=pct1 markers=true title="Overfitting por profundidade"/>

<BarChart data={arvores_random_forest__importancia} x=atributo y=importancia swapXY=true title="Importância dos indicadores"/>

<DataTable data={arvores_random_forest__metricas}/>
""",
    "mlp_reversao": q("mlp_reversao__classes") + q("mlp_reversao__sinal") + """
<DataTable data={mlp_reversao__classes}>
  <Column id=classe/><Column id=sinais_emitidos title="Sinais"/><Column id=eventos_reais title="Eventos reais"/>
  <Column id=precisao title="Precisão" fmt=pct1/><Column id=taxa_base title="Taxa-base" fmt=pct1/>
</DataTable>

<LineChart data={mlp_reversao__sinal} x=data y=fechamento title="Prata 2023–2026 (nunca vista no treino)"/>
<BarChart data={mlp_reversao__sinal} x=data y=indicador_mlp title="Indicador da MLP (+1 alta, −1 queda)"/>
""",
    "pca_fatores": q("pca_fatores__variancia") + q("pca_fatores__cargas") + q("pca_fatores__representantes") + """
<BarChart data={pca_fatores__variancia} x=componente y=variancia_explicada yFmt=pct1 title="Variância explicada por componente"/>
<LineChart data={pca_fatores__variancia} x=componente y=acumulada yFmt=pct0 markers=true title="Acumulada">
  <ReferenceLine y=0.8 label="80%"/>
</LineChart>

<ScatterPlot data={pca_fatores__cargas} x=PC1 y=PC2 series=classe tooltipTitle=nome title="Ativos no plano dos 2 primeiros fatores"/>

<DataTable data={pca_fatores__representantes}/>
""",
    "kmeans_clusters": q("kmeans_clusters__ativos") + q("kmeans_clusters__escolha_k") + """
<LineChart data={kmeans_clusters__escolha_k} x=k y=silhueta markers=true title="Silhueta por K"/>
<ScatterPlot data={kmeans_clusters__ativos} x=x y=y series=grupo tooltipTitle=nome title="Grupos (projeção PCA)"/>
<DataTable data={kmeans_clusters__ativos} rows=30>
  <Column id=nome/><Column id=classe/><Column id=grupo/><Column id=retorno_anual fmt=pct1/><Column id=vol_anual fmt=pct1/>
  <Column id=drawdown_max fmt=pct1/><Column id=corr_sp500 fmt=num2/>
</DataTable>
""",
    "embedding_retornos": q("embedding_retornos__embedding") + q("embedding_retornos__similaridade",
        "select * from quant.embedding_retornos__similaridade order by cosseno desc") + """
<ScatterPlot data={embedding_retornos__embedding} x=dim1 y=dim2 series=classe tooltipTitle=nome title="Embedding 2D (FastICA)"/>
<DataTable data={embedding_retornos__similaridade} rows=15 search=true>
  <Column id=nome_a title="Ativo A"/><Column id=nome_b title="Ativo B"/><Column id=cosseno fmt=num2/><Column id=pearson fmt=num2/>
</DataTable>
""",
    "isolation_forest": q("isolation_forest__resumo") + """
<Dropdown data={isolation_forest__resumo} name=ativo value=simbolo label=nome defaultValue="US500" title="Ativo"/>

```sql pontos_sel
select * from quant.isolation_forest__pontos where simbolo = '${inputs.ativo.value}'
```

<ScatterPlot data={pontos_sel} x=data y=retorno_pct series=anomalia title="Retornos diários — anomalias destacadas"/>
<DataTable data={isolation_forest__resumo}/>
""",
    "outliers_multimetodo": q("outliers_multimetodo__resumo") + q("outliers_multimetodo__efeito_regressao") + """
<BarChart data={outliers_multimetodo__resumo} x=metodo y=outliers swapXY=true title="Dias marcados como outlier"/>
<DataTable data={outliers_multimetodo__efeito_regressao}/>
""",
    "markov_regimes": q("markov_regimes__transicao") + q("markov_regimes__resumo") + q("markov_regimes__horizonte",
        "select * from quant.markov_regimes__horizonte where de = 'baixa'") + """
<Heatmap data={markov_regimes__transicao} x=para y=de value=probabilidade valueFmt=pct0 title="Matriz de transição (blocos de 20 pregões)"/>
<LineChart data={markov_regimes__horizonte} x=pregoes y={["p_alta","p_baixa"]} yFmt=pct0 title="Partindo de 'baixa': probabilidade ao longo do horizonte"/>
<DataTable data={markov_regimes__resumo}/>
""",
    "hmm_regimes": q("hmm_regimes__estados") + q("hmm_regimes__probabilidades") + """
<AreaChart data={hmm_regimes__probabilidades} x=data y={["p_calmo","p_normal","p_turbulento"]} yFmt=pct0 title="Probabilidade de cada regime — S&P 500"/>
<DataTable data={hmm_regimes__estados}>
  <Column id=estado/><Column id=media_diaria_pct title="Média diária %" fmt=num3/><Column id=vol_anual_pct title="Vol % a.a." fmt=num1/>
  <Column id=duracao_media_pregoes title="Duração (pregões)" fmt=num0/><Column id=fracao_tempo title="Fração do tempo" fmt=pct1/>
</DataTable>
""",
    "bayes_conjugado": q("bayes_conjugado__posterior") + """
<LineChart data={bayes_conjugado__posterior} x=data y={["ic95_inf_anual_pct","media_post_anual_pct","ic95_sup_anual_pct"]} title="Ouro — retorno médio anual a posteriori e credibilidade 95% (%)" yMin=-60 yMax=80/>
<LineChart data={bayes_conjugado__posterior} x=data y=p_media_positiva yFmt=pct0 title="Probabilidade de a média ser positiva"/>
""",
    "fourier_ciclos": q("fourier_ciclos__picos") + q("fourier_ciclos__espectro") + """
<DataTable data={fourier_ciclos__picos}>
  <Column id=nome/><Column id=periodo_semanas title="Período (semanas)" fmt=num1/><Column id=potencia fmt=num5/>
  <Column id=limiar_ruido_95 title="Limiar de ruído 95%" fmt=num5/><Column id=significativo/>
</DataTable>
<LineChart data={fourier_ciclos__espectro} x=periodo_semanas y=potencia series=nome xLog=true title="Periodograma (retornos semanais)"/>
""",
    "wavelet_haar": q("wavelet_haar__energia_niveis") + q("wavelet_haar__sinal") + """
<BarChart data={wavelet_haar__energia_niveis} x=escala_pregoes y=fracao_energia yFmt=pct0 title="Energia por escala (pregões)"/>
<LineChart data={wavelet_haar__sinal} x=data y=energia_detalhe_z title="Energia de alta frequência (z)">
  <ReferenceLine y=2 label="z = 2"/>
</LineChart>
""",
    "markowitz_fronteira": q("markowitz_fronteira__nuvem") + q("markowitz_fronteira__fronteira") + q("markowitz_fronteira__fora_amostra") + q("markowitz_fronteira__pesos") + """
<ScatterPlot data={markowitz_fronteira__nuvem} x=vol_anual_pct y=retorno_anual_pct title="5 mil carteiras aleatórias (treino 2010–2019)" pointSize=3/>
<LineChart data={markowitz_fronteira__fronteira} x=vol_anual_pct y=retorno_anual_pct title="Fronteira eficiente"/>
<BarChart data={markowitz_fronteira__fora_amostra} x=carteira y={["sharpe_treino","sharpe_teste"]} type=grouped title="Sharpe: treino × 2020–2026"/>
<BarChart data={markowitz_fronteira__pesos} x=nome y=peso series=carteira type=grouped yFmt=pct0 swapXY=true title="Pesos"/>
""",
    "ag_carteira": q("ag_carteira__evolucao") + q("ag_carteira__rodadas") + q("ag_carteira__pesos") + """
<LineChart data={ag_carteira__evolucao} x=geracao y=melhor_aptidao series=semente title="Evolução da melhor aptidão (4 sementes em paralelo)"/>
<DataTable data={ag_carteira__rodadas}/>
<BarChart data={ag_carteira__pesos} x=nome y=peso series=semente type=grouped swapXY=true yFmt=pct0 title="Pesos por semente"/>

> Rode o mesmo algoritmo genético no seu navegador, em WebAssembly, no [Laboratório](/laboratorio).
""",
    "ag_indicadores": q("ag_indicadores__rodadas") + """
<BarChart data={ag_indicadores__rodadas} x=semente y={["sharpe_treino","sharpe_teste"]} type=grouped title="Sharpe: treino (até 2018) × teste (2019–2026)"/>
<DataTable data={ag_indicadores__rodadas}/>
""",
    "programacao_genetica": q("programacao_genetica__formulas") + q("programacao_genetica__evolucao") + """
<DataTable data={programacao_genetica__formulas} wrapTitles=true>
  <Column id=semente/><Column id=formula title="Fórmula descoberta" wrap=true/><Column id=nos title="Nós"/>
  <Column id=ic_treino title="IC treino" fmt=num3/><Column id=ic_teste title="IC teste" fmt=num3/>
</DataTable>
<LineChart data={programacao_genetica__evolucao} x=geracao y=melhor_aptidao series=semente title="Evolução da aptidão"/>
""",
    "hurst_movel": q("hurst_movel__resumo") + q("hurst_movel__series") + """
<BarChart data={hurst_movel__resumo} x=nome y={["hurst_rs","hurst_nulo"]} type=grouped yMin=0.4 title="H medido × H da série embaralhada"/>
<DataTable data={hurst_movel__resumo}/>
<LineChart data={hurst_movel__series} x=data y=diferenca series=simbolo title="MH100 − MH150"/>
""",
    "sistemas_nao_lineares": q("sistemas_nao_lineares__caudas") + q("sistemas_nao_lineares__histograma_us500",
        # escala log não aceita zero: faixas sem nenhuma observação ficam fora do gráfico
        "select * from quant.sistemas_nao_lineares__histograma_us500 "
        "where densidade_real > 0 and densidade_normal > 1e-12") + """
<LineChart data={sistemas_nao_lineares__histograma_us500} x=z y={["densidade_real","densidade_normal"]} yLog=true title="S&P 500 × normal (escala log)"/>
<BarChart data={sistemas_nao_lineares__caudas} x=nome y=razao_caudas swapXY=true title="Quantas vezes mais eventos de 4σ do que a normal prevê"/>
""",
    "garch_volatilidade": q("garch_volatilidade__parametros") + q("garch_volatilidade__serie") + """
<BigValue data={garch_volatilidade__parametros} value=persistencia title="Persistência α+β" fmt=num3/>
<BigValue data={garch_volatilidade__parametros} value=meia_vida_dias title="Meia-vida do choque (pregões)" fmt=num0/>
<BigValue data={garch_volatilidade__parametros} value=var99_pct title="VaR 99% 1 dia (%)" fmt=num2/>
<LineChart data={garch_volatilidade__serie} x=data y={["vol_garch_anual_pct","vol_ewma_anual_pct"]} title="Volatilidade condicional (% a.a.)"/>
""",
    "rede_correlacao": q("rede_correlacao__nos") + q("rede_correlacao__carteiras") + """
<DataTable data={rede_correlacao__carteiras}/>
<ScatterPlot data={rede_correlacao__nos} x=x y=y series=classe tooltipTitle=nome title="Posição na árvore geradora mínima"/>
<DataTable data={rede_correlacao__nos} rows=30>
  <Column id=nome/><Column id=forca fmt=num2/><Column id=autovetor fmt=num3/><Column id=proximidade fmt=num3/>
  <Column id=intermediacao fmt=num3/><Column id=centralidade_composta title="Centralidade (posto médio)" fmt=num1/>
</DataTable>

![Rede](/telas/rede_correlacao.png)
""",
    "causalidade_granger": q("causalidade_granger__granger") + """
<Heatmap data={causalidade_granger__granger} x=rotulo_efeito y=rotulo_causa value=estatistica_f title="Estatística F (causa → efeito)"/>
<DataTable data={causalidade_granger__granger} rows=15 search=true>
  <Column id=rotulo_causa title="Causa"/><Column id=rotulo_efeito title="Efeito"/><Column id=estatistica_f fmt=num1/>
  <Column id=p_valor fmt=0.0e+0/><Column id=significativo_bonferroni title="Sobrevive a Bonferroni"/>
</DataTable>
""",
    "drift_modelo": q("drift_modelo__anual") + """
<LineChart data={drift_modelo__anual} x=ano y=acuracia yFmt=pct1 markers=true title="Acurácia por ano"/>
<BarChart data={drift_modelo__anual} x=ano y=ks_max series=alerta title="Deslocamento da entrada (KS máx.)">
  <ReferenceLine y=0.25 label="limite de retreino"/>
</BarChart>
<DataTable data={drift_modelo__anual}/>
""",
    "backtest_walkforward": q("backtest_walkforward__metricas") + q("backtest_walkforward__curvas") + """
<LineChart data={backtest_walkforward__curvas} x=data y=patrimonio series=estrategia yLog=true title="Patrimônio (escala log)"/>
<DataTable data={backtest_walkforward__metricas}>
  <Column id=estrategia/><Column id=cagr_pct title="CAGR %" fmt=num1/><Column id=vol_anual_pct title="Vol %" fmt=num1/>
  <Column id=sharpe fmt=num2/><Column id=drawdown_max_pct title="Drawdown %" fmt=num1/><Column id=giro_anual title="Giro a.a." fmt=num2/>
  <Column id=veredito title="Portões STOP"/>
</DataTable>
""",
    "triple_barrier_ou": q("triple_barrier_ou__parametros") + q("triple_barrier_ou__malha",
        "select * from quant.triple_barrier_ou__malha where previsao_sigmas = 0") + """
<Heatmap data={triple_barrier_ou__malha} x=stop_sigmas y=alvo_lucro_sigmas value=sharpe valueFmt=num2 title="Sharpe por operação — alvo × stop (σ)"/>
<DataTable data={triple_barrier_ou__parametros}/>

> Recalcule esta malha no navegador, com seus próprios parâmetros, no [Laboratório](/laboratorio).
""",
    "benford": q("benford__conformidade") + q("benford__distribuicao",
        "select * from quant.benford__distribuicao where conjunto = 'TODOS'") + """
<BarChart data={benford__distribuicao} x=digito y={["observada","benford"]} type=grouped yFmt=pct0 title="Primeiro dígito — volumes agregados × Benford"/>
<DataTable data={benford__conformidade} rows=30>
  <Column id=nome/><Column id=ordens_grandeza title="Ordens de grandeza" fmt=num1/><Column id=mad_nigrini title="MAD" fmt=num4/><Column id=veredito/>
</DataTable>
""",
    "shap_explicabilidade": q("shap_explicabilidade__importancia") + q("shap_explicabilidade__ultima_previsao") + """
<BarChart data={shap_explicabilidade__ultima_previsao} x=atributo y=contribuicao swapXY=true title="Contribuição de cada atributo na última previsão"/>
<BarChart data={shap_explicabilidade__importancia} x=atributo y=shap_medio_abs swapXY=true title="Importância média |SHAP|"/>
""",
}


def gerar_sql() -> int:
    """Fonte CSV nativa do evidence: os arquivos vivem em sources/quant/ e cada um vira a tabela
    quant.<nome>. Sem caminho em SQL — read_csv_auto com caminho relativo quebrava quando o servidor
    de desenvolvimento reexecutava as fontes a partir de .evidence/template — ver bugs.md."""
    destino = EV / "sources/quant"
    for f in list(destino.glob("*.sql")) + list(destino.glob("*.csv")):
        f.unlink()
    (destino / "connection.yaml").write_text(
        "# quant_models_2026 · ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS\n"
        "# CSVs gerados por pipeline/executar_modelos.py (cópia de evidence/dados/quant)\n"
        "name: quant\ntype: csv\noptions: {}\n", encoding="utf-8")
    n = 0
    for csv in sorted(DADOS.glob("*.csv")):
        shutil.copy2(csv, destino / csv.name)
        n += 1
    return n


def _resumo() -> dict:
    import pandas as pd
    r = pd.read_csv(DADOS / "resumo_modelos.csv")
    return {row.id: row.destaque for row in r.itertuples()}


def gerar_paginas() -> int:
    destaques = _resumo()
    pasta = EV / "pages/modelos"
    pasta.mkdir(parents=True, exist_ok=True)
    n = 0
    fase1 = [m for m in MODELOS if m["fase"] == 1]
    for i, m in enumerate(MODELOS, start=1):
        if m["fase"] != 1:
            continue
        corpo = PAGINAS[m["id"]]
        idx = fase1.index(m)
        ant = fase1[idx - 1] if idx > 0 else None
        prox = fase1[idx + 1] if idx + 1 < len(fase1) else None
        nav = " · ".join(x for x in [f"[← {ant['nome']}](/modelos/{ant['id']})" if ant else "",
                                     "[Catálogo](/catalogo)",
                                     f"[{prox['nome']} →](/modelos/{prox['id']})" if prox else ""] if x)
        texto = f"""---
title: "{i:02d} · {m['nome']}"
---
{CAB}
{nav}

**Tipo:** {m['tipo']} · **Categoria:** {m['categoria']} · **Fonte na base de conhecimento:** {m['kb']}

{esc(m['descricao'])}

> **Leitura dos dados:** {esc(destaques.get(m['id'], ''))}

{corpo}

## Como reproduzir

```bash
cd public/foundations/pipeline
python3 executar_modelos.py --so {m['id']}     # Python + numba, ProcessPoolExecutor
python3 testes_nucleo.py                        # confere numba × Rust × F#
```

{nav}
"""
        escrever(pasta / f"{m['id']}.md", texto)
        n += 1
    return n


def gerar_catalogo() -> None:
    linhas = ["---", "title: Catálogo de modelos", "---", CAB,
              "Os 40 modelos extraídos da base de conhecimento. A fase 1 roda sobre os dados do DataFeed; a fase 2 "
              "exige corpus textual, book de ofertas ou GPU.", "",
              q("catalogo_modelos", "select numero, nome, tipo, categoria, fase, "
                "case when fase = 1 then '/modelos/' || id else null end as pagina, descricao "
                "from quant.catalogo_modelos order by numero"),
              """<DataTable data={catalogo_modelos} rows=40 search=true link=pagina>
  <Column id=numero title="Nº"/><Column id=nome title="Modelo"/><Column id=tipo/><Column id=categoria/>
  <Column id=fase/><Column id=descricao title="Descrição" wrap=true/>
</DataTable>
"""]
    escrever(EV / "pages/catalogo.md", "\n".join(linhas))


def gerar_motores() -> None:
    escrever(EV / "pages/motores.md", f"""---
title: Três motores, um resultado
---
{CAB}
Cada kernel numérico existe em **três linguagens** — Python/numba, Rust e F# — e o teste de concordância
exige que os três devolvam o mesmo número, inclusive no Monte Carlo (o gerador xorshift64* é idêntico nos três).
Dois motores independentes que concordam provam que a **matemática** está certa, não só o código.

{q("bench_motores")}
<DataTable data={{bench_motores}}>
  <Column id=carga title="Carga"/><Column id=numba_s title="numba (s)" fmt=num3/><Column id=rust_s title="Rust (s)" fmt=num3/>
  <Column id=fsharp_s title="F# (s)" fmt=num3/><Column id=python_puro_s title="Python puro (s)" fmt=num2/>
  <Column id=ganho_numba title="Ganho do numba" fmt=num0/>
</DataTable>

<BarChart data={{bench_motores}} x=carga y={{["numba_s","rust_s","fsharp_s"]}} type=grouped swapXY=true title="Tempo por motor (s)"/>

Tempos de Rust e F# **descontam a partida do processo** (medida à parte). No F#, o tempo inclui a compilação JIT do .NET.
Medido com `bench_motores.py`; histórico em `bench/historico.jsonl`.
""")


def gerar_index() -> None:
    import pandas as pd
    r = pd.read_csv(DADOS / "resumo_modelos.csv")
    cartoes = "\n".join(f"| {row.numero:02d} | [{row.nome}](/modelos/{row.id}) | {row.categoria} | {esc(row.destaque)} |"
                        for row in r.itertuples())
    escrever(EV / "pages/index.md", f"""---
title: Quant Models 2026
---
{CAB}
<div style="text-align:center;">

{SELETOR}

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

# Pare de decidir por planilha. Comece a decidir por modelo.

> Uma planilha ordena, filtra e soma — e em nenhum momento pergunta **quanto do que você vê é ruído**.
> Aqui, 32 modelos quantitativos rodam sobre 27 ativos reais (2010–2026) e cada um mostra, com o dado,
> **onde a intuição engana**: a acurácia que é só a taxa-base, o ótimo que não sobrevive ao futuro, a memória
> longa que é viés do estimador, a "diversificação" que é rótulo.

{q("totais", "select (select count(*) from quant.catalogo_modelos) as catalogo, "
   "(select count(*) from quant.resumo_modelos) as implementados, "
   "(select max(linhas) from quant.resumo_modelos) as maior_tabela")}
<BigValue data={{totais}} value=catalogo title="Modelos no catálogo"/>
<BigValue data={{totais}} value=implementados title="Rodando sobre dados reais"/>

## As leituras — uma frase por modelo

| Nº | Modelo | Categoria | O que o dado mostrou |
|---:|---|---|---|
{cartoes}

## Explore

- [Catálogo completo (40 modelos)](/catalogo)
- [Laboratório no navegador (WebAssembly)](/laboratorio)
- [Três motores, um resultado (Python/numba · Rust · F#)](/motores)

---

_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 — TODOS OS DIREITOS RESERVADOS · profbruanbima@gmail.com_
""")


NOMES_IDIOMA = [("pt", "Português", "/"), ("en", "English", "/en"), ("es", "Español", "/es"), ("fr", "Français", "/fr"),
                ("de", "Deutsch", "/de"), ("zh", "中文", "/zh"), ("ko", "한국어", "/ko"), ("hi", "हिन्दी", "/hi"),
                ("he", "עברית", "/he"), ("ru", "Русский", "/ru"), ("sv", "Svenska", "/sv"), ("fi", "Suomi", "/fi")]


def gerar_idiomas() -> int:
    """Uma página inicial por idioma, a partir dos MESMOS blocos traduzidos dos READMEs (TM).
    As páginas de modelo seguem em PT-BR; a vitrine localizada traduz a ficha e a leitura."""
    from config import FOUNDATIONS, ler
    blocos = json.loads(ler(FOUNDATIONS / "translation/readme.blocos.json"))
    fase1 = [m for m in MODELOS if m["fase"] == 1]
    n = 0
    for cod, _nome, rota in NOMES_IDIOMA[1:]:
        b = {k: v[cod] for k, v in blocos.items()}
        sel = " · ".join(f"**{nm}**" if c == cod else f"[{nm}]({r})" for c, nm, r in NOMES_IDIOMA)
        linhas = []
        for m in fase1:
            i = MODELOS.index(m) + 1
            linhas.append(f"| {i:02d} | [{esc(b[f'm{i:02d}_nome'])}](/modelos/{m['id']}) | "
                          f"{esc(b[f'm{i:02d}_leitura'])} |")
        direcao = ' dir="rtl"' if cod == "he" else ""
        texto = f"""---
title: "quant_models_2026 — {esc(b['subtitulo'])}"
---
{CAB}
<div style="text-align:center;">

🌐 {sel}

<img src="/img/logo_capa.png" alt="ProfBru" width="220" style="display:inline-block;margin-top:1rem;"/>

**ProfBru © 2026**

</div>

<div{direcao}>

# {esc(b['slogan'])}

**{esc(b['promessa'])}**

> {esc(b['dor_cena'])}
>
> **{esc(b['dor_acao'])}**

{esc(b['diagnostico_explicacao'])}

## {esc(b['h_modelos'])}

| # | {esc(b['depois'])} | {esc(b['label_leitura'])} |
|---:|---|---|
{chr(10).join(linhas)}

## {esc(b['h_site'])}

{esc(b['site_intro'])}

- [{esc(b['site2_titulo'])}](/laboratorio)
- [{esc(b['site4_titulo'])}](/motores)
- [{esc(b['h_catalogo'])}](/catalogo)

> {esc(b['honestidade'])}

</div>

---

_quant_models_2026 · {esc(b['label_autor'])}: **ProfBru - Bruno Penedo** © 2026 · profbruanbima@gmail.com_
"""
        escrever(EV / f"pages/{cod}/index.md", texto)
        n += 1
    return n


def copiar_estaticos() -> None:
    est = EV / "static"
    (est / "img").mkdir(parents=True, exist_ok=True)
    shutil.copy2(RAIZ / "docs/logo_capa.png", est / "img/logo_capa.png")
    (est / "telas").mkdir(exist_ok=True)
    for png in (RAIZ / "docs/telas").glob("*.png"):
        shutil.copy2(png, est / "telas" / png.name)
    subprocess.run(["cargo", "build", "--release", "--lib", "--target", "wasm32-unknown-unknown", "--quiet"],
                   cwd=RUST, check=True)
    shutil.copy2(RUST / "target/wasm32-unknown-unknown/release/quant_models_2026_core.wasm", est / "qm_core.wasm")
    # retornos para o laboratório (derivados; arredondados a 6 casas para caber leve no navegador)
    from quant.dados import NOMES, retornos
    ativos = ["US500", "US100", "XAUUSD", "XAGUSD", "WTI", "COPPER", "EURUSD", "USDJPY", "USTBOND", "SOYBEAN"]
    r = retornos(simbolos=ativos).loc["2015":]
    lab = {"datas": [d.strftime("%Y-%m-%d") for d in r.index], "ativos": list(r.columns),
           "nomes": [NOMES[a] for a in r.columns],
           "retornos": [[round(float(v), 6) for v in r[c]] for c in r.columns]}
    (est / "laboratorio.json").write_text(json.dumps(lab, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> int:
    n_sql = gerar_sql()
    n_pag = gerar_paginas()
    gerar_catalogo()
    gerar_motores()
    gerar_index()
    n_idi = gerar_idiomas()
    copiar_estaticos()
    print(f"✅ site: {n_sql} fontes CSV · {n_pag} páginas de modelo · {n_idi} vitrines localizadas · catálogo, motores · "
          "WASM e dados do laboratório")
    return 0


if __name__ == "__main__":
    sys.exit(main())
