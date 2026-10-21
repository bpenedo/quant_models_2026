#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Telas do README (D21): uma figura por modelo, a partir dos CSVs de executar_modelos.py.

Gera em _private/foundations/telas/<id>.png e COPIA para docs/telas/ (imagem em _private/
quebra no GitHub). Paleta: instância de referência validada (CVD) — séries 1–3 em
dispersão, sequencial azul, divergente azul↔vermelho com meio cinza.

Uso:  python3 gerar_telas.py [--so id1,id2]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAIZ, TELAS_PRIVADAS, TELAS_PUBLICAS, WORKERS  # noqa: E402

DADOS = RAIZ / "public/foundations/evidence/dados/quant"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
TXT, TXT2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
NEUTRO = "#b9b8b2"
DIV = ["#184f95", "#5598e7", "#cde2fb", "#f0efec", "#f6c9c8", "#e66767", "#a32c2c"]


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
        "axes.edgecolor": GRADE, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
        "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8, "axes.spines.top": False,
        "axes.spines.right": False, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.titlecolor": TXT, "legend.frameon": False, "lines.linewidth": 2.0,
    })
    return plt


def _ler(nome):
    import pandas as pd
    return pd.read_csv(DADOS / f"{nome}.csv")


def _salvar(fig, mid: str, titulo: str, subtitulo: str):
    # posições em POLEGADAS a partir do topo: fração da altura fazia título e subtítulo se
    # sobreporem em figuras baixas — ver bugs.md (FRONTEND, telas)
    h = fig.get_figheight()
    fig.text(0.01, 1 - 0.30 / h, titulo, ha="left", va="center", fontsize=14, fontweight="bold", color=TXT)
    fig.text(0.01, 1 - 0.58 / h, subtitulo, ha="left", va="top" if "\n" in subtitulo else "center",
             fontsize=9.5, color=TXT2)
    fig.text(0.99, 0.01, "quant_models_2026 · ProfBru © 2026 · dados: DataFeed (D1)", ha="right",
             fontsize=7.5, color=TXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 1 - 0.85 / h))
    destino = TELAS_PRIVADAS / f"{mid}.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=110)
    import matplotlib.pyplot as plt
    plt.close(fig)
    TELAS_PUBLICAS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destino, TELAS_PUBLICAS / destino.name)
    return destino.name


# ─────────────────────────────────────────────────────────────────────────────
def t_estatistica_descritiva():
    plt = _plt()
    d = _ler("estatistica_descritiva__resumo").sort_values("vol_anual_pct")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    y = range(len(d))
    ax.barh(y, d.vol_anual_pct, color=S1, height=0.38, label="desvio-padrão anual")
    ax.barh([i + 0.4 for i in y], d.sigma_robusta_anual_pct, color=S2, height=0.38, label="σ robusta (MAD)")
    ax.set_yticks([i + 0.2 for i in y], d.nome, fontsize=8)
    ax.set_xlabel("volatilidade anual (%)")
    ax.legend(loc="lower right")
    return _salvar(fig, "estatistica_descritiva", "Quanto da volatilidade é feita de poucos dias extremos?",
                   "Desvio-padrão × σ robusta por ativo — a distância entre as barras é a cauda pesada")


def t_suporte_resistencia():
    plt = _plt()
    p, f = _ler("suporte_resistencia__preco"), _ler("suporte_resistencia__faixas")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(p.data.astype("datetime64[ns]"), p.fechamento, color=S1, lw=1.6)
    for _, r in f.iterrows():
        ax.axhspan(r.minimo, r.maximo, color=S2 if r.tipo == "resistência" else S3,
                   alpha=0.10 + 0.5 * r.intensidade_pct / 100, lw=0)
        ax.text(1.01, r.centro, f"{r.tipo} · {r.intensidade_pct:.0f}%", transform=ax.get_yaxis_transform(),
                fontsize=8, color=TXT2, va="center", ha="left")
    ax.set_ylabel("ouro (US$/oz)")
    return _salvar(fig, "suporte_resistencia", "Suporte e resistência sem régua na tela",
                   "Ouro, 2 anos: faixas = moda dos preços arredondados agrupada por K-means; opacidade = nº de visitas")


def t_estacionariedade_adf():
    plt = _plt()
    d = _ler("estacionariedade_adf__adf")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    nomes = d.nome.unique()
    for i, forma in enumerate(["log-preço", "log-retorno"]):
        s = d[d.forma == forma]
        ax.bar([j + i * 0.4 for j in range(len(nomes))], s.estatistica_adf, width=0.38,
               color=[S1, S2][i], label=forma)
    ax.axhline(d.critico_5pct.iloc[0], color=TXT, lw=1, ls="--")
    ax.text(len(nomes) - 0.5, d.critico_5pct.iloc[0] + 1, "valor crítico 5%", fontsize=8, color=TXT, ha="right")
    ax.set_xticks([j + 0.2 for j in range(len(nomes))], nomes, rotation=20, fontsize=8)
    ax.set_ylabel("estatística ADF (abaixo da linha = estacionária)")
    ax.legend()
    return _salvar(fig, "estacionariedade_adf", "Preço não é estacionário; retorno é",
                   "Teste ADF com constante — implementação própria conferida com o statsmodels")


def t_regressao_linear():
    plt = _plt()
    d = _ler("regressao_linear__dispersao")
    c = _ler("regressao_linear__coeficientes")
    pares = [c.iloc[0].rotulo, c.sort_values("r2").iloc[0].rotulo]
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 5))
    for ax, par, cor in zip(axs, pares, (S1, S2)):
        s = d[d.par == par]
        k = c[c.rotulo == par].iloc[0]
        ax.scatter(s.x_pct, s.y_pct, s=9, color=cor, alpha=0.5, lw=0)
        xs = [s.x_pct.min(), s.x_pct.max()]
        ax.plot(xs, [k.alfa_diario_pct + k.beta * x for x in xs], color=TXT, lw=1.5)
        ax.set_title(f"{par}\nβ = {k.beta:.2f} · R² = {k.r2:.2f}".replace(".", ","), fontsize=10)
        ax.set_xlabel("retorno diário x (%)"); ax.set_ylabel("retorno diário y (%)")
    return _salvar(fig, "regressao_linear", "A relação 'óbvia' explica quanto do dia a dia?",
                   "Mínimos quadrados entre log-retornos diários, 2010–2026")


def t_regressao_logistica():
    plt = _plt()
    a = _ler("regressao_logistica__acerto_anual")
    m = _ler("regressao_logistica__metricas").iloc[0]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(a.ano.astype(str), a.acerto * 100, color=S1, width=0.6)
    ax.axhline(m.taxa_base_alta * 100, color=S2, lw=2, ls="--")
    ax.text(0, m.taxa_base_alta * 100 + 0.6, f"fração de dias de alta: {m.taxa_base_alta * 100:.1f}%".replace(".", ","),
            color=TXT, fontsize=9)
    ax.set_ylim(40, 65); ax.set_ylabel("acerto fora da amostra (%)")
    return _salvar(fig, "regressao_logistica", "Acurácia que é só a taxa-base disfarçada",
                   f"S&P 500, walk-forward anual — AUC {m.auc:.3f}: a linha de base que desarma o autoengano".replace(".", ","))


def t_svm_kernels():
    plt = _plt()
    import numpy as np
    g = _ler("svm_kernels__fronteiras")
    k = _ler("svm_kernels__kernels").set_index("kernel")
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.8), sharey=True)
    for ax, ker in zip(axs, ["linear", "poly", "rbf", "sigmoid"]):
        s = g[g.kernel == ker]
        n = int(np.sqrt(len(s)))
        Z = s.decisao.to_numpy().reshape(n, n)
        ax.contourf(s.rsi_z.to_numpy().reshape(n, n), s.vol_z.to_numpy().reshape(n, n), Z,
                    levels=[-1e12, 0, 1e12], colors=["#f6c9c8", "#cde2fb"])
        ax.contour(s.rsi_z.to_numpy().reshape(n, n), s.vol_z.to_numpy().reshape(n, n), Z, levels=[0],
                   colors=TXT, linewidths=1.5)
        ax.set_title(f"{ker}\nteste {k.loc[ker].acuracia_teste * 100:.1f}%".replace(".", ","), fontsize=10)
        ax.set_xlabel("RSI (z)")
    axs[0].set_ylabel("volatilidade 20d (z)")
    return _salvar(fig, "svm_kernels", "Quatro kernels, quatro fronteiras — e nenhum sinal novo",
                   "SVM com classes balanceadas; azul = prevê alta, vermelho = prevê queda; acurácia balanceada fora da amostra")


def t_arvores_random_forest():
    plt = _plt()
    p, i = _ler("arvores_random_forest__profundidade"), _ler("arvores_random_forest__importancia")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.8))
    a1.plot(p.profundidade, p.acuracia_treino * 100, color=S1, marker="o", ms=5, label="treino")
    a1.plot(p.profundidade, p.acuracia_teste * 100, color=S2, marker="o", ms=5, label="teste")
    a1.set_xlabel("profundidade da árvore"); a1.set_ylabel("acurácia (%)"); a1.legend()
    a1.set_title("Decorar o passado não prevê o futuro", fontsize=10)
    a2.barh(i.atributo, i.importancia, color=S1, height=0.6)
    a2.set_title("Importância dos indicadores (Random Forest)", fontsize=10)
    return _salvar(fig, "arvores_random_forest", "Árvores: onde o overfitting começa",
                   "S&P 500, treino até 2017, teste 2018–2026")


def t_mlp_reversao():
    plt = _plt()
    s = _ler("mlp_reversao__sinal")
    c = _ler("mlp_reversao__classes")
    fig, ax = plt.subplots(figsize=(10.5, 5))
    dt = s.data.astype("datetime64[ns]")
    ax.plot(dt, s.fechamento, color=NEUTRO, lw=1.4)
    alta, queda = s[s.indicador_mlp == 1], s[s.indicador_mlp == -1]
    ax.scatter(alta.data.astype("datetime64[ns]"), alta.fechamento, s=12, color=S3, label="MLP: reversão de alta")
    ax.scatter(queda.data.astype("datetime64[ns]"), queda.fechamento, s=12, color=S2, label="MLP: reversão de queda")
    ax.legend(loc="upper left"); ax.set_ylabel("prata (US$/oz)")
    a = c.iloc[0]
    return _salvar(fig, "mlp_reversao", "Indicador de reversão com rede neural, em período nunca visto",
                   f"Prata 2023–2026 · precisão das reversões de alta {a.precisao * 100:.1f}% contra "
                   f"{a.taxa_base * 100:.1f}% de frequência natural".replace(".", ","))


def t_pca_fatores():
    plt = _plt()
    v, c = _ler("pca_fatores__variancia"), _ler("pca_fatores__cargas")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5))
    a1.bar(v.componente, v.variancia_explicada * 100, color=S1, width=0.7)
    a1.plot(v.componente, v.acumulada * 100, color=S2, marker="o", ms=4)
    a1.axhline(80, color=TXT2, lw=1, ls=":"); a1.set_xlabel("componente"); a1.set_ylabel("variância explicada (%)")
    a1.set_title("Variância por fator e acumulada", fontsize=10)
    a2.scatter(c.PC1, c.PC2, s=28, color=S1)
    for _, r in c.iterrows():
        a2.annotate(r.simbolo, (r.PC1, r.PC2), fontsize=7, color=TXT2, xytext=(3, 2), textcoords="offset points")
    a2.set_xlabel("carga PC1"); a2.set_ylabel("carga PC2"); a2.set_title("Ativos no plano dos 2 primeiros fatores", fontsize=10)
    return _salvar(fig, "pca_fatores", "27 ativos não são 27 apostas independentes",
                   "PCA dos retornos padronizados, 2010–2026")


def t_kmeans_clusters():
    plt = _plt()
    a, k = _ler("kmeans_clusters__ativos"), _ler("kmeans_clusters__escolha_k")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5), gridspec_kw={"width_ratios": [1, 2]})
    a1.plot(k.k, k.silhueta, color=S1, marker="o", ms=6); a1.set_xlabel("K"); a1.set_ylabel("silhueta")
    a1.set_title("Escolha automática de K", fontsize=10)
    cores = [S1, S2, S3, S4, "#e34948", "#eda100"]
    for g in sorted(a.grupo.unique()):
        s = a[a.grupo == g]
        a2.scatter(s.x, s.y, s=40, color=cores[(g - 1) % 6], label=f"grupo {g}")
        for _, r in s.iterrows():
            a2.annotate(r.simbolo, (r.x, r.y), fontsize=7, color=TXT2, xytext=(3, 2), textcoords="offset points")
    a2.legend(fontsize=8); a2.set_title("Grupos de comportamento (projeção PCA)", fontsize=10)
    return _salvar(fig, "kmeans_clusters", "Comportamento, não rótulo: grupos que misturam classes",
                   "K-means sobre retorno, volatilidade, drawdown, correlações e assimetria")


def t_embedding_retornos():
    plt = _plt()
    e = _ler("embedding_retornos__embedding")
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.scatter(e.dim1, e.dim2, s=40, color=S1)
    for _, r in e.iterrows():
        ax.annotate(r.nome, (r.dim1, r.dim2), fontsize=7.5, color=TXT2, xytext=(4, 2), textcoords="offset points")
    ax.set_xlabel("dimensão 1"); ax.set_ylabel("dimensão 2")
    return _salvar(fig, "embedding_retornos", "Mapa de proximidade dos últimos 60 pregões",
                   "Embedding 2D por FastICA dos vetores de retorno — vizinhos se moveram parecido")


def t_isolation_forest():
    plt = _plt()
    p = _ler("isolation_forest__pontos")
    s = p[p.simbolo == "US500"]
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    dt = s.data.astype("datetime64[ns]")
    ax.plot(dt, s.retorno_pct, color=NEUTRO, lw=0.8)
    an = s[s.anomalia]
    ax.scatter(an.data.astype("datetime64[ns]"), an.retorno_pct, s=18, color=S2, label="anomalia (Isolation Forest)", zorder=3)
    ax.legend(loc="lower left"); ax.set_ylabel("retorno diário S&P 500 (%)")
    return _salvar(fig, "isolation_forest", "Anomalia como sinal, sem um único rótulo",
                   "Isolation Forest sobre retorno e volume padronizado, 2010–2026")


def t_outliers_multimetodo():
    plt = _plt()
    r, e = _ler("outliers_multimetodo__resumo"), _ler("outliers_multimetodo__efeito_regressao")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
    a1.barh(r.metodo, r.outliers, color=[S1, S1, S1, S2], height=0.6)
    a1.set_title("Quantos dias cada critério chama de outlier", fontsize=10)
    import numpy as np
    xs = np.linspace(0, 10, 2)
    for (_, k), cor in zip(e.iterrows(), (S1, S2)):
        a2.plot(xs, k.intercepto + k.inclinacao * xs, color=cor, label=f"{k.cenario}: inclinação {k.inclinacao:.2f}".replace(".", ","))
    a2.legend(); a2.set_title("Um ponto discrepante desloca a reta", fontsize=10)
    return _salvar(fig, "outliers_multimetodo", "Não existe detector ideal — existe consenso",
                   "S&P 500: boxplot, z-robusto e LOF; à direita, o efeito de um único outlier")


def t_markov_regimes():
    plt = _plt()
    t = _ler("markov_regimes__transicao")
    import numpy as np
    ordem = ["baixa", "lateral", "alta"]
    M = np.array([[t[(t.de == a) & (t.para == b)].probabilidade.iloc[0] for b in ordem] for a in ordem])
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    ax.imshow(M, cmap="Blues", vmin=0, vmax=1)
    ax.grid(False)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{M[i, j] * 100:.0f}%", ha="center", va="center", color="white" if M[i, j] > 0.5 else TXT)
    ax.set_xticks(range(3), ordem); ax.set_yticks(range(3), ordem)
    ax.set_xlabel("para (próximo bloco de 20 pregões)"); ax.set_ylabel("de")
    return _salvar(fig, "markov_regimes", "Depois de uma baixa, o que vem?",
                   "Matriz de transição de regimes do S&P 500 (blocos de 20 pregões)")


def t_hmm_regimes():
    plt = _plt()
    p = _ler("hmm_regimes__probabilidades")
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    dt = p.data.astype("datetime64[ns]")
    ax.stackplot(dt, p.p_calmo, p.p_normal, p.p_turbulento, colors=[S1, S3, S2],
                 labels=["calmo", "normal", "turbulento"], alpha=0.9)
    ax.set_ylim(0, 1); ax.set_ylabel("probabilidade do regime"); ax.legend(loc="lower left", ncol=3)
    return _salvar(fig, "hmm_regimes", "Regimes aprendidos dos dados, não de uma regra de corte",
                   "HMM gaussiano de 3 estados (Baum-Welch) sobre o S&P 500")


def t_bayes_conjugado():
    plt = _plt()
    b = _ler("bayes_conjugado__posterior")
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    dt = b.data.astype("datetime64[ns]")
    ax.fill_between(dt, b.ic95_inf_anual_pct, b.ic95_sup_anual_pct, color="#cde2fb", lw=0, label="credibilidade 95%")
    ax.plot(dt, b.media_post_anual_pct, color=S1, label="média a posteriori")
    ax.axhline(0, color=TXT2, lw=1)
    ax.set_ylim(-60, 80); ax.set_ylabel("retorno médio anual (%)"); ax.legend(loc="upper left")
    return _salvar(fig, "bayes_conjugado", "Quanto confiar numa média de retorno?",
                   "Ouro desde 2019 — atualização bayesiana pregão a pregão (Normal-Gama)")


def t_triple_barrier_ou():
    plt = _plt()
    m = _ler("triple_barrier_ou__malha")
    s = m[m.previsao_sigmas == 0.0].pivot(index="alvo_lucro_sigmas", columns="stop_sigmas", values="sharpe")
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    im = ax.imshow(s.to_numpy(), origin="lower", cmap="RdBu", aspect="auto",
                   extent=[s.columns.min(), s.columns.max(), s.index.min(), s.index.max()],
                   vmin=-abs(s.to_numpy()).max(), vmax=abs(s.to_numpy()).max())
    ax.grid(False); fig.colorbar(im, ax=ax, label="Sharpe por operação")
    ax.set_xlabel("stop-loss (σ)"); ax.set_ylabel("alvo de lucro (σ)")
    return _salvar(fig, "triple_barrier_ou", "O stop ótimo vem da dinâmica do ativo",
                   "Spread Brent − WTI · 4.000 trajetórias O-U por célula\nmesmo resultado, bit a bit, em numba, Rust e F#")


def t_fourier_ciclos():
    plt = _plt()
    e = _ler("fourier_ciclos__espectro")
    fig, axs = plt.subplots(2, 2, figsize=(11, 6), sharex=True)
    for ax, (s, g) in zip(axs.ravel(), e.groupby("nome")):
        ax.plot(g.periodo_semanas, g.potencia, color=S1, lw=1.2)
        ax.axhline(g.limiar_ruido_95.iloc[0], color=S2, lw=1.5, ls="--")
        ax.set_title(s, fontsize=10); ax.set_xscale("log")
    axs[1, 0].set_xlabel("período (semanas)"); axs[1, 1].set_xlabel("período (semanas)")
    return _salvar(fig, "fourier_ciclos", "Todo espectro tem picos — quais são ciclo?",
                   "Periodograma dos retornos semanais; tracejado = limiar de ruído 95% por embaralhamento")


def t_wavelet_haar():
    plt = _plt()
    s = _ler("wavelet_haar__sinal")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10.5, 5.6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    dt = s.data.astype("datetime64[ns]")
    a1.plot(dt, s.fechamento, color=S1, lw=1.4); a1.set_ylabel("S&P 500")
    a2.plot(dt, s.energia_detalhe_z, color=S2, lw=1.0); a2.axhline(2, color=TXT2, ls="--", lw=1)
    a2.set_ylabel("energia alta freq. (z)")
    return _salvar(fig, "wavelet_haar", "Onde a turbulência começa, no tempo",
                   "Energia dos coeficientes de detalhe da DWT de Haar (nível 1, janela de 20 pregões)")


def t_markowitz_fronteira():
    plt = _plt()
    n, f, o = _ler("markowitz_fronteira__nuvem"), _ler("markowitz_fronteira__fronteira"), _ler("markowitz_fronteira__fora_amostra")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5))
    a1.scatter(n.vol_anual_pct, n.retorno_anual_pct, s=3, c=n.sharpe, cmap="Blues", alpha=0.6)
    a1.plot(f.vol_anual_pct, f.retorno_anual_pct, color=S2, lw=2.2, label="fronteira eficiente")
    a1.set_xlabel("volatilidade anual (%)"); a1.set_ylabel("retorno anual (%)"); a1.legend(loc="lower right")
    a1.set_title("2010–2019 (treino)", fontsize=10)
    x = range(len(o))
    a2.bar([i - 0.2 for i in x], o.sharpe_treino, width=0.4, color=S1, label="treino")
    a2.bar([i + 0.2 for i in x], o.sharpe_teste, width=0.4, color=S2, label="2020–2026")
    a2.set_xticks(list(x), o.carteira, fontsize=8); a2.set_ylabel("índice de Sharpe"); a2.legend()
    a2.set_title("O ótimo do passado no futuro", fontsize=10)
    return _salvar(fig, "markowitz_fronteira", "A fronteira é exata — o futuro não",
                   "Markowitz com 10 ativos: 20 mil carteiras, mínima variância, tangência e pesos iguais")


def t_ag_carteira():
    plt = _plt()
    e, w = _ler("ag_carteira__evolucao"), _ler("ag_carteira__pesos")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    for i, (s, g) in enumerate(e.groupby("semente")):
        a1.plot(g.geracao, g.melhor_aptidao, color=[S1, S2, S3, S4][i], lw=1.6, label=f"semente {s}")
    a1.set_xlabel("geração"); a1.set_ylabel("melhor aptidão"); a1.legend(fontsize=8)
    a1.set_title("Quatro rodadas paralelas convergem", fontsize=10)
    m = w.groupby("nome").peso.mean().sort_values()
    a2.barh(m.index, m.to_numpy() * 100, color=S1, height=0.6); a2.set_xlabel("peso médio (%)")
    a2.set_title("Carteira encontrada", fontsize=10)
    return _salvar(fig, "ag_carteira", "Algoritmo genético: seleção, crossover, mutação — e honestidade",
                   "Aptidão = Sharpe + 0,5 × drawdown no backtest 2010–2019")


def t_ag_indicadores():
    plt = _plt()
    r = _ler("ag_indicadores__rodadas")
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = range(len(r))
    ax.bar([i - 0.2 for i in x], r.sharpe_treino, width=0.4, color=S1, label="treino (até 2018)")
    ax.bar([i + 0.2 for i in x], r.sharpe_teste, width=0.4, color=S2, label="teste (2019–2026)")
    ax.set_xticks(list(x), [f"semente {s}\nMM {a}/{b}" for s, a, b in zip(r.semente, r.media_rapida, r.media_lenta)], fontsize=8)
    ax.set_ylabel("índice de Sharpe"); ax.legend()
    return _salvar(fig, "ag_indicadores", "Quanto mais regras se testa, mais o treino mente",
                   f"AG sobre médias, RSI e rompimento no S&P 500 — {int(r.regras_avaliadas.sum())} regras avaliadas")


def t_programacao_genetica():
    plt = _plt()
    f = _ler("programacao_genetica__formulas")
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = range(len(f))
    ax.bar([i - 0.2 for i in x], f.ic_treino.abs(), width=0.4, color=S1, label="|IC| treino")
    ax.bar([i + 0.2 for i in x], f.ic_teste.abs(), width=0.4, color=S2, label="|IC| teste")
    ax.set_xticks(list(x), [f"semente {s}\n{n} nós" for s, n in zip(f.semente, f.nos)], fontsize=8)
    ax.set_ylabel("correlação de postos com o próximo retorno"); ax.legend()
    return _salvar(fig, "programacao_genetica", "Fórmulas que a evolução inventa — e o teste que as desmente",
                   "Regressão simbólica sobre os 3 últimos retornos do S&P 500")


def t_hurst_movel():
    plt = _plt()
    r = _ler("hurst_movel__resumo")
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = range(len(r))
    ax.bar([i - 0.2 for i in x], r.hurst_rs, width=0.4, color=S1, label="H medido (R/S)")
    ax.bar([i + 0.2 for i in x], r.hurst_nulo, width=0.4, color=NEUTRO, label="H da série embaralhada")
    ax.axhline(0.5, color=TXT2, lw=1, ls=":")
    ax.set_ylim(0.4, 0.65); ax.set_xticks(list(x), r.nome, fontsize=8); ax.legend()
    return _salvar(fig, "hurst_movel", "Memória longa ou viés do estimador?",
                   "Expoente de Hurst contra a própria série sem memória — a diferença é o que importa")


def t_sistemas_nao_lineares():
    plt = _plt()
    h = _ler("sistemas_nao_lineares__histograma_us500")
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.semilogy(h.z, h.densidade_real.where(h.densidade_real > 0), color=S1, marker="o", ms=3, label="S&P 500 real")
    ax.semilogy(h.z, h.densidade_normal, color=S2, label="curva normal")
    ax.set_ylim(1e-6, 1); ax.set_xlabel("retorno padronizado (desvios)"); ax.set_ylabel("densidade (log)"); ax.legend()
    return _salvar(fig, "sistemas_nao_lineares", "Cisnes negros não são raros o bastante",
                   "Distribuição dos retornos diários × normal, em escala log: as caudas reais são muito mais grossas")


def t_garch_volatilidade():
    plt = _plt()
    s = _ler("garch_volatilidade__serie")
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    dt = s.data.astype("datetime64[ns]")
    ax.plot(dt, s.vol_garch_anual_pct, color=S1, lw=1.3, label="GARCH(1,1)")
    ax.plot(dt, s.vol_ewma_anual_pct, color=S2, lw=1.0, label="EWMA λ=0,94")
    ax.set_ylabel("volatilidade anualizada (%)"); ax.legend()
    return _salvar(fig, "garch_volatilidade", "Dias agitados seguem dias agitados",
                   "Volatilidade condicional do S&P 500 — base de VaR, stop e tamanho de posição")


def t_rede_correlacao():
    plt = _plt()
    n, a = _ler("rede_correlacao__nos"), _ler("rede_correlacao__arestas")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    for _, e in a.iterrows():
        ax.plot([e.xa, e.xb], [e.ya, e.yb], color=NEUTRO, lw=1 + 2 * abs(e.correlacao), zorder=1)
    per = n.simbolo.iloc[:8].tolist()
    for _, r in n.iterrows():
        ax.scatter(r.x, r.y, s=60, color=S2 if r.simbolo in per else S1, zorder=2)
        ax.annotate(r.simbolo, (r.x, r.y), fontsize=7.5, color=TXT, xytext=(4, 3), textcoords="offset points")
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.scatter([], [], color=S2, label="periféricos"); ax.scatter([], [], color=S1, label="demais"); ax.legend()
    return _salvar(fig, "rede_correlacao", "Quem está no centro da rede de mercado",
                   "Árvore geradora mínima das correlações 2010–2019; laranja = 8 ativos mais periféricos")


def t_causalidade_granger():
    plt = _plt()
    import numpy as np
    g = _ler("causalidade_granger__granger")
    ativos = sorted(set(g.rotulo_causa))
    M = np.full((len(ativos), len(ativos)), np.nan)
    for _, r in g.iterrows():
        M[ativos.index(r.rotulo_causa), ativos.index(r.rotulo_efeito)] = -np.log10(max(r.p_valor, 1e-20))
    fig, ax = plt.subplots(figsize=(8.5, 6.6))
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=8); ax.grid(False)
    ax.set_xticks(range(len(ativos)), ativos, rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(len(ativos)), ativos, fontsize=8)
    ax.set_xlabel("efeito"); ax.set_ylabel("causa (antecede)")
    fig.colorbar(im, ax=ax, label="−log10(p) — mais escuro = mais significativo")
    return _salvar(fig, "causalidade_granger", "Quem antecede quem — e onde a intuição engana",
                   "Teste de Granger com 5 defasagens; correção de Bonferroni na tabela")


def t_drift_modelo():
    plt = _plt()
    d = _ler("drift_modelo__anual")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
    a1.plot(d.ano, d.acuracia * 100, color=S1, marker="o", ms=5); a1.axhline(50, color=TXT2, lw=1, ls=":")
    a1.set_title("Acurácia por ano", fontsize=10); a1.set_ylabel("%")
    a2.bar(d.ano, d.ks_max, color=[S2 if x == "RETREINAR" else S1 for x in d.alerta], width=0.6)
    a2.axhline(0.25, color=TXT2, lw=1, ls="--"); a2.set_title("Deslocamento da entrada (KS máx.)", fontsize=10)
    return _salvar(fig, "drift_modelo", "O modelo envelhece — o monitor avisa",
                   "Logística treinada em 2010–2016; laranja = alerta de retreino (KS > 0,25 ou PSI > 0,25)")


def t_backtest_walkforward():
    plt = _plt()
    c, m = _ler("backtest_walkforward__curvas"), _ler("backtest_walkforward__metricas")
    fig, ax = plt.subplots(figsize=(10.5, 5))
    cores = {"Pesos iguais": S1, "Paridade de risco": S3, "Momentum (janela walk-forward)": S4, "S&P 500 comprado": S2}
    for e, g in c.groupby("estrategia"):
        v = m[m.estrategia == e].veredito.iloc[0]
        ax.plot(g.data.astype("datetime64[ns]"), g.patrimonio, color=cores[e], label=f"{e} — {v}")
    ax.set_yscale("log"); ax.set_ylabel("patrimônio (log, início = 1)"); ax.legend(fontsize=8)
    return _salvar(fig, "backtest_walkforward", "Backtest com custos e portões STOP",
                   "27 ativos, rebalanceamento mensal, 5 bps por giro; STOP = Sharpe < 0,5, drawdown < −30% ou custo ≥ 1% a.a.")


def t_benford():
    plt = _plt()
    d = _ler("benford__distribuicao")
    s = d[d.conjunto == "TODOS"]
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.bar(s.digito - 0.2, s.observada * 100, width=0.4, color=S1, label="volumes agregados")
    ax.bar(s.digito + 0.2, s.benford * 100, width=0.4, color=NEUTRO, label="lei de Benford")
    ax.set_xticks(range(1, 10)); ax.set_xlabel("primeiro dígito"); ax.set_ylabel("%"); ax.legend()
    return _salvar(fig, "benford", "Auditoria de dados em uma linha de código",
                   "Primeiro dígito dos volumes de 29 ativos (6,4 ordens de grandeza) × Benford")


def t_shap_explicabilidade():
    plt = _plt()
    u = _ler("shap_explicabilidade__ultima_previsao")
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.barh(u.atributo, u.contribuicao * 100, color=[S1 if v > 0 else S2 for v in u.contribuicao], height=0.6)
    ax.axvline(0, color=TXT2, lw=1); ax.set_xlabel("contribuição para a probabilidade de alta (p.p.)")
    return _salvar(fig, "shap_explicabilidade", "Por que o modelo disse 'compra' hoje?",
                   "Valores de Shapley da última previsão do Random Forest (azul empurra para alta, laranja para queda)")


TELAS = {n[2:]: f for n, f in list(globals().items()) if n.startswith("t_") and callable(f)}


def _uma(mid):
    return TELAS[mid]()


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera as telas do README.")
    ap.add_argument("--so", default="")
    a = ap.parse_args()
    ids = [x for x in a.so.split(",") if x] or list(TELAS)
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        feitos = list(ex.map(_uma, ids))
    print(f"✅ {len(feitos)} telas em {TELAS_PRIVADAS.relative_to(RAIZ)} → copiadas para {TELAS_PUBLICAS.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
