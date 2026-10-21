# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Aprendizado de máquina: logística, SVM/kernels, árvores/RF, MLP de reversão, PCA, K-means,
embeddings de retornos (FastICA + cosseno), Isolation Forest, SHAP e drift.

Regra de ouro herdada da KB: separar treino e teste NO TEMPO. Embaralhar séries financeiras
para validação cruzada vaza o futuro para o treino e produz acurácia de mentira.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from quant import kernels as K
from quant.dados import CLASSES, NOMES, retornos, serie
from quant.util import br, pct

SEMENTE = 42


# ─────────────────────────────────────────────────────────────────────────────
# Engenharia de atributos (somente informação disponível ATÉ o fechamento de t)
# ─────────────────────────────────────────────────────────────────────────────
def atributos(simbolo: str) -> pd.DataFrame:
    s = serie(simbolo)
    s = s[s.index.dayofweek < 5].loc["2005":]
    c, h, l = s["close"].to_numpy(), s["high"].to_numpy(), s["low"].to_numpy()
    r = np.diff(np.log(c), prepend=np.nan)
    df = pd.DataFrame(index=s.index)
    df["ret_1"] = r
    df["ret_5"] = pd.Series(r, index=s.index).rolling(5).sum()
    df["ret_20"] = pd.Series(r, index=s.index).rolling(20).sum()
    df["vol_20"] = pd.Series(r, index=s.index).rolling(20).std()
    df["rsi_14"] = K.rsi(c, 14)
    macd = K.ema(c, 12) - K.ema(c, 26)
    sinal = K.ema(macd, 9)
    df["macd_hist"] = (macd - sinal) / c
    _, tend = K.psar(h, l, 0.02, 0.2)
    df["psar_tend"] = tend
    df["dist_mm50"] = c / pd.Series(c, index=s.index).rolling(50).mean().to_numpy() - 1
    df["alvo_dir"] = (pd.Series(r, index=s.index).shift(-1) > 0).astype(int)
    df["ret_seguinte"] = pd.Series(r, index=s.index).shift(-1)
    return df.dropna()


ATR = ["ret_1", "ret_5", "ret_20", "vol_20", "rsi_14", "macd_hist", "psar_tend", "dist_mm50"]


def _walk_forward(df: pd.DataFrame, fabrica, inicio_teste: int = 2016):
    """Janela expansiva anual: treina com tudo até o ano anterior, testa no ano seguinte."""
    from sklearn.preprocessing import StandardScaler
    anos = sorted(set(df.index.year))
    prev = pd.Series(np.nan, index=df.index)
    prob = pd.Series(np.nan, index=df.index)
    for ano in [a for a in anos if a >= inicio_teste]:
        tr = df[df.index.year < ano]
        te = df[df.index.year == ano]
        if len(te) == 0:
            continue
        esc = StandardScaler().fit(tr[ATR])
        m = fabrica()
        m.fit(esc.transform(tr[ATR]), tr["alvo_dir"])
        Xt = esc.transform(te[ATR])
        prev.loc[te.index] = m.predict(Xt)
        if hasattr(m, "predict_proba"):
            prob.loc[te.index] = m.predict_proba(Xt)[:, 1]
    return prev.dropna(), prob.dropna()


def _metricas_direcao(df, prev, prob, nome):
    from sklearn.metrics import balanced_accuracy_score, roc_auc_score
    y = df.loc[prev.index, "alvo_dir"]
    rs = df.loc[prev.index, "ret_seguinte"].to_numpy()
    pos = np.where(prev.to_numpy() == 1, 1.0, -1.0)
    estrat = pos * rs - 0.0002 * np.abs(np.diff(pos, prepend=pos[0]))  # 2 bps por troca de lado
    auc = roc_auc_score(y, prob.loc[prev.index]) if len(prob) else np.nan
    return {"modelo": nome, "acuracia": float((prev == y).mean()),
            "acuracia_balanceada": float(balanced_accuracy_score(y, prev)), "auc": float(auc),
            "fracao_prevista_alta": float(prev.mean()),
            "taxa_base_alta": float(y.mean()), "sharpe_long_short": K.sharpe_anual(estrat, 252.0),
            "sharpe_comprado": K.sharpe_anual(rs, 252.0), "n_teste": int(len(prev))}


# ─────────────────────────────────────────────────────────────────────────────
def regressao_logistica(simbolo: str = "US500") -> dict:
    from sklearn.linear_model import LogisticRegression
    df = atributos(simbolo)
    prev, prob = _walk_forward(df, lambda: LogisticRegression(C=0.5, max_iter=2000))
    m = _metricas_direcao(df, prev, prob, "Regressão logística")
    # coeficientes no período completo de treino (para leitura)
    from sklearn.preprocessing import StandardScaler
    tr = df[df.index.year < 2016]
    esc = StandardScaler().fit(tr[ATR])
    lr = LogisticRegression(C=0.5, max_iter=2000).fit(esc.transform(tr[ATR]), tr["alvo_dir"])
    coef = pd.DataFrame({"atributo": ATR, "coeficiente": lr.coef_[0]}).sort_values("coeficiente")
    anual = pd.DataFrame({"ano": prev.index.year, "acerto": (prev == df.loc[prev.index, "alvo_dir"]).astype(float)}) \
        .groupby("ano").acerto.mean().reset_index()
    curva = pd.DataFrame({"data": prob.index, "probabilidade_alta": prob.to_numpy()})
    return {"tabelas": {"metricas": pd.DataFrame([m]), "coeficientes": coef, "acerto_anual": anual,
                        "probabilidade": curva},
            "destaque": (f"Fora da amostra (2016–2026) a logística acerta {pct(m['acuracia'])} da direção do S&P 500 — "
                         f"praticamente a fração de dias de alta ({pct(m['taxa_base_alta'])}): previu alta em "
                         f"{pct(m['fracao_prevista_alta'], 0)} dos dias e tem AUC {br(m['auc'], 3)}. Acurácia alta sem "
                         f"poder de separação é a armadilha que esta linha de base desarma.")}


# ─────────────────────────────────────────────────────────────────────────────
def svm_kernels(simbolo: str = "US500") -> dict:
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    df = atributos(simbolo)
    pares = ["rsi_14", "vol_20"]
    tr = df[(df.index.year >= 2012) & (df.index.year < 2020)]
    te = df[df.index.year >= 2020]
    esc = StandardScaler().fit(tr[pares])
    Xtr, Xte = esc.transform(tr[pares]), esc.transform(te[pares])
    linhas, grades = [], []
    gx, gy = np.meshgrid(np.linspace(-3, 3, 61), np.linspace(-3, 3, 61))
    G = np.column_stack([gx.ravel(), gy.ravel()])
    for kernel, kw in (("linear", {}), ("poly", {"degree": 3}), ("rbf", {"gamma": "scale"}), ("sigmoid", {})):
        # class_weight balanceado: sem ele os quatro kernels colapsam em "sempre alta" — ver bugs.md BUG-004
        m = SVC(kernel=kernel, C=1.0, class_weight="balanced", **kw).fit(Xtr, tr["alvo_dir"])
        acc_tr = float(balanced_accuracy_score(tr["alvo_dir"], m.predict(Xtr)))
        acc_te = float(balanced_accuracy_score(te["alvo_dir"], m.predict(Xte)))
        linhas.append({"kernel": kernel, "acuracia_treino": acc_tr, "acuracia_teste": acc_te,
                       "vetores_suporte": int(m.n_support_.sum()), "lacuna_overfitting": acc_tr - acc_te})
        z = m.decision_function(G)
        grades.append(pd.DataFrame({"kernel": kernel, "rsi_z": G[:, 0], "vol_z": G[:, 1], "decisao": z}))
    t = pd.DataFrame(linhas)
    melhor = t.sort_values("acuracia_teste", ascending=False).iloc[0]
    return {"tabelas": {"kernels": t, "fronteiras": pd.concat(grades, ignore_index=True)},
            "destaque": (f"Com só RSI e volatilidade como entradas, nenhum dos quatro kernels passa de "
                         f"{pct(t.acuracia_teste.max())} de acurácia balanceada fora da amostra. O RBF é o que mais "
                         f"'aprende' no treino ({pct(t.set_index('kernel').loc['rbf'].acuracia_treino)}) e o que mais "
                         f"perde no teste ({pct(t.set_index('kernel').loc['rbf'].acuracia_teste)}): kernel não cria "
                         f"sinal onde ele não existe.")}


# ─────────────────────────────────────────────────────────────────────────────
def arvores_random_forest(simbolo: str = "US500") -> dict:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    df = atributos(simbolo)
    tr = df[df.index.year < 2018]
    te = df[df.index.year >= 2018]
    curva = []
    for d in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20):
        t = DecisionTreeClassifier(max_depth=d, random_state=SEMENTE).fit(tr[ATR], tr["alvo_dir"])
        curva.append({"profundidade": d, "acuracia_treino": t.score(tr[ATR], tr["alvo_dir"]),
                      "acuracia_teste": t.score(te[ATR], te["alvo_dir"])})
    rf = RandomForestClassifier(n_estimators=400, max_depth=5, min_samples_leaf=40, n_jobs=1,
                                random_state=SEMENTE).fit(tr[ATR], tr["alvo_dir"])
    imp = pd.DataFrame({"atributo": ATR, "importancia": rf.feature_importances_}).sort_values("importancia")
    prob = rf.predict_proba(te[ATR])[:, 1]
    prev = pd.Series((prob > 0.5).astype(int), index=te.index)
    m = _metricas_direcao(df, prev, pd.Series(prob, index=te.index), "Random Forest (400 árvores)")
    c = pd.DataFrame(curva)
    return {"tabelas": {"profundidade": c, "importancia": imp, "metricas": pd.DataFrame([m])},
            "destaque": (f"Árvore com profundidade 20 acerta {pct(c.iloc[-1].acuracia_treino)} no treino e "
                         f"{pct(c.iloc[-1].acuracia_teste)} no teste: decorou o passado. A floresta rasa fica em "
                         f"{pct(m['acuracia'])} — modesta, mas honesta; o atributo mais usado é "
                         f"'{imp.iloc[-1].atributo}'.")}


# ─────────────────────────────────────────────────────────────────────────────
def _eventos_reversao(simbolo: str):
    s = serie(simbolo)
    s = s[s.index.dayofweek < 5].loc["2005":]
    c, h, l = s["close"].to_numpy(), s["high"].to_numpy(), s["low"].to_numpy()
    n = c.size
    rsi = K.rsi(c, 14)
    macd = K.ema(c, 12) - K.ema(c, 26)
    hist = macd - K.ema(macd, 9)
    _, tend = K.psar(h, l, 0.02, 0.2)
    X = np.zeros((n, 6))
    for i in range(1, n):
        X[i, 0] = 1.0 if tend[i] != tend[i - 1] and tend[i] > 0 else 0.0     # PSAR vira para alta
        X[i, 1] = 1.0 if tend[i] != tend[i - 1] and tend[i] < 0 else 0.0     # PSAR vira para baixa
        X[i, 2] = 1.0 if rsi[i - 1] < 30 <= rsi[i] else 0.0                  # RSI sai da sobrevenda
        X[i, 3] = 1.0 if rsi[i - 1] > 70 >= rsi[i] else 0.0                  # RSI sai da sobrecompra
        X[i, 4] = 1.0 if hist[i - 1] < 0 <= hist[i] else 0.0                 # MACD hist − → +
        X[i, 5] = 1.0 if hist[i - 1] > 0 >= hist[i] else 0.0                 # MACD hist + → −
    # memória curta dos eventos: soma dos últimos 3 pregões
    Xm = np.vstack([X[max(0, i - 2):i + 1].sum(0) for i in range(n)])
    # alvo: +1 reversão de alta (≥ +5% em 10 dias após 10 dias de queda), −1 o inverso, 0 lateral
    y = np.zeros(n, dtype=int)
    for i in range(10, n - 10):
        passado = c[i] / c[i - 10] - 1
        futuro = c[i + 10] / c[i] - 1
        if passado < 0 and futuro >= 0.05:
            y[i] = 1
        elif passado > 0 and futuro <= -0.05:
            y[i] = -1
    idx = s.index
    return pd.DataFrame(Xm, index=idx, columns=["psar_alta", "psar_baixa", "rsi_sai_sobrevenda",
                                                "rsi_sai_sobrecompra", "macd_vira_pos", "macd_vira_neg"]), \
        pd.Series(y, index=idx), s["close"]


def mlp_reversao(simbolo: str = "XAGUSD") -> dict:
    from sklearn.neural_network import MLPClassifier
    X, y, close = _eventos_reversao(simbolo)
    X = X.iloc[20:-10]
    y = y.loc[X.index]
    tr = X.index.year < 2023
    te = X.index.year >= 2023
    mlp = MLPClassifier(hidden_layer_sizes=(10, 10), alpha=0.01, max_iter=2000, random_state=1)
    # Sobreamostragem das reversões no TREINO: com 73% de dias laterais a rede aprende a
    # responder sempre "lateral" e nunca emite sinal — ver bugs.md BUG-005.
    rng = np.random.default_rng(SEMENTE)
    Xtr, ytr = X[tr].to_numpy(), y[tr].to_numpy()
    n_max = max((ytr == c).sum() for c in (-1, 0, 1))
    idx = np.concatenate([rng.choice(np.flatnonzero(ytr == c), n_max, replace=True) for c in (-1, 0, 1)])
    mlp.fit(Xtr[idx], ytr[idx])
    prev = pd.Series(mlp.predict(X[te].to_numpy()), index=X.index[te])
    real = y[te]
    linhas = []
    for classe, nome in ((1, "reversão de alta"), (-1, "reversão de queda"), (0, "lateral")):
        sinal = prev == classe
        acertos = int(((prev == classe) & (real == classe)).sum())
        linhas.append({"classe": nome, "sinais_emitidos": int(sinal.sum()), "eventos_reais": int((real == classe).sum()),
                       "acertos": acertos, "precisao": acertos / sinal.sum() if sinal.sum() else np.nan,
                       "taxa_base": float((real == classe).mean())})
    t = pd.DataFrame(linhas)
    graf = pd.DataFrame({"data": X.index[te], "fechamento": close.loc[X.index[te]].to_numpy(),
                         "indicador_mlp": prev.to_numpy(), "alvo_real": real.to_numpy()})
    alta = t.iloc[0]
    ganho = alta.precisao / alta.taxa_base if alta.sinais_emitidos else float("nan")
    leitura = (f"Na prata, em 2023–2026 (nunca vistos no treino), a MLP emitiu {alta.sinais_emitidos} sinais de "
               f"reversão de alta com precisão de {pct(alta.precisao) if alta.sinais_emitidos else '—'}, contra "
               f"taxa base de {pct(alta.taxa_base)} ({br(ganho, 2)}× a frequência natural): é essa razão, e não a "
               f"acurácia geral, que diz se o indicador agrega informação.")
    return {"tabelas": {"classes": t, "sinal": graf}, "destaque": leitura}


# ─────────────────────────────────────────────────────────────────────────────
def pca_fatores() -> dict:
    from sklearn.decomposition import PCA
    r = retornos()
    Z = (r - r.mean()) / r.std()
    pca = PCA().fit(Z)
    var = pd.DataFrame({"componente": np.arange(1, len(pca.explained_variance_ratio_) + 1),
                        "variancia_explicada": pca.explained_variance_ratio_,
                        "acumulada": np.cumsum(pca.explained_variance_ratio_)})
    cargas = pd.DataFrame(pca.components_[:3].T, columns=["PC1", "PC2", "PC3"], index=r.columns)
    cargas["nome"] = [NOMES.get(s, s) for s in cargas.index]
    cargas["classe"] = [CLASSES.get(s, "—") for s in cargas.index]
    cargas = cargas.reset_index().rename(columns={"index": "simbolo"})
    n80 = int(np.searchsorted(var.acumulada.to_numpy(), 0.80) + 1)
    rep = []
    for pc in ("PC1", "PC2", "PC3"):
        top = cargas.reindex(cargas[pc].abs().sort_values(ascending=False).index).iloc[0]
        rep.append({"fator": pc, "ativo_representativo": top.simbolo, "nome": top.nome, "carga": top[pc]})
    return {"tabelas": {"variancia": var, "cargas": cargas, "representantes": pd.DataFrame(rep)},
            "destaque": (f"O 1º fator sozinho explica {pct(var.variancia_explicada[0])} da variação diária de "
                         f"{r.shape[1]} ativos; são precisos {n80} fatores para chegar a 80%. Os 27 ativos não são "
                         f"27 apostas independentes.")}


# ─────────────────────────────────────────────────────────────────────────────
def kmeans_clusters() -> dict:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    r = retornos()
    mkt = r["US500"]
    feats = []
    for s in r.columns:
        x = r[s]
        curva = np.exp(x.cumsum().to_numpy())
        feats.append({"simbolo": s, "retorno_anual": x.mean() * 252, "vol_anual": x.std() * math.sqrt(252),
                      "drawdown_max": K.drawdown_maximo(curva), "corr_sp500": x.corr(mkt),
                      "corr_dolar": x.corr(r["DXY"]), "assimetria": x.skew()})
    F = pd.DataFrame(feats).set_index("simbolo")
    Z = StandardScaler().fit_transform(F)
    sil = []
    for k in range(2, 9):
        km = KMeans(n_clusters=k, n_init=20, random_state=SEMENTE).fit(Z)
        sil.append({"k": k, "silhueta": silhouette_score(Z, km.labels_), "inercia": km.inertia_})
    sil = pd.DataFrame(sil)
    kbest = int(sil.sort_values("silhueta", ascending=False).iloc[0].k)
    km = KMeans(n_clusters=kbest, n_init=50, random_state=SEMENTE).fit(Z)
    xy = PCA(2).fit_transform(Z)
    F = F.reset_index()
    F["grupo"] = km.labels_ + 1
    F["x"], F["y"] = xy[:, 0], xy[:, 1]
    F["nome"] = [NOMES.get(s, s) for s in F.simbolo]
    F["classe"] = [CLASSES.get(s, "—") for s in F.simbolo]
    mist = F.groupby("grupo").classe.nunique().max()
    return {"tabelas": {"ativos": F, "escolha_k": sil},
            "destaque": (f"A silhueta escolhe K = {kbest} grupos sem intervenção manual; há grupo que mistura "
                         f"{mist} classes de ativo diferentes — o rótulo 'commodity' ou 'câmbio' não diz como o ativo "
                         f"se comporta.")}


# ─────────────────────────────────────────────────────────────────────────────
def embedding_retornos(janela: int = 60) -> dict:
    from sklearn.decomposition import FastICA
    r = retornos()
    M = r.iloc[-janela:].T  # ativos × dias
    Mz = (M.sub(M.mean(1), axis=0)).div(M.std(1), axis=0)
    ica = FastICA(n_components=2, random_state=SEMENTE, whiten="unit-variance", max_iter=2000)
    E = ica.fit_transform(Mz.to_numpy())
    emb = pd.DataFrame({"simbolo": M.index, "dim1": E[:, 0], "dim2": E[:, 1]})
    emb["nome"] = [NOMES.get(s, s) for s in emb.simbolo]
    emb["classe"] = [CLASSES.get(s, "—") for s in emb.simbolo]
    V = M.to_numpy()
    nrm = np.linalg.norm(V, axis=1, keepdims=True)
    cos = (V / nrm) @ (V / nrm).T
    pares = []
    ids = list(M.index)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pares.append({"a": ids[i], "b": ids[j], "nome_a": NOMES.get(ids[i]), "nome_b": NOMES.get(ids[j]),
                          "cosseno": cos[i, j], "pearson": float(np.corrcoef(V[i], V[j])[0, 1])})
    p = pd.DataFrame(pares).sort_values("cosseno", ascending=False)
    top = p.iloc[0]
    oposto = p.iloc[-1]
    return {"tabelas": {"embedding": emb, "similaridade": p},
            "destaque": (f"Nos últimos {janela} pregões, o par mais parecido é {top.nome_a} × {top.nome_b} "
                         f"(cosseno {br(top.cosseno)}) e o mais oposto é {oposto.nome_a} × {oposto.nome_b} "
                         f"({br(oposto.cosseno)}): um mapa de proximidade que se atualiza a cada janela.")}


# ─────────────────────────────────────────────────────────────────────────────
def isolation_forest() -> dict:
    from sklearn.ensemble import IsolationForest
    linhas = []
    resumo = []
    for s in ("US500", "XAUUSD", "WTI", "EURUSD"):
        d = serie(s)
        d = d[d.index.dayofweek < 5].loc["2010":]
        r = np.log(d["close"]).diff()
        v = np.log(d["volume"].replace(0, np.nan))
        vz = (v - v.rolling(60).mean()) / v.rolling(60).std()
        X = pd.DataFrame({"ret": r, "vol_z": vz}).dropna()
        iso = IsolationForest(n_estimators=300, contamination=0.02, random_state=SEMENTE).fit(X)
        sc = -iso.score_samples(X)
        an = iso.predict(X) == -1
        linhas.append(pd.DataFrame({"simbolo": s, "data": X.index, "retorno_pct": X.ret * 100,
                                    "volume_z": X.vol_z, "escore": sc, "anomalia": an}))
        ra = X.ret[an]
        resumo.append({"simbolo": s, "nome": NOMES[s], "anomalias": int(an.sum()),
                       "pct_quedas": float((ra < 0).mean()), "maior_queda_pct": float(ra.min() * 100),
                       "maior_alta_pct": float(ra.max() * 100),
                       "anomalias_2020": int(an[X.index.year == 2020].sum())})
    t = pd.DataFrame(resumo)
    sp = t[t.simbolo == "US500"].iloc[0]
    return {"tabelas": {"pontos": pd.concat(linhas, ignore_index=True), "resumo": t},
            "destaque": (f"Sem nenhum rótulo, a floresta de isolamento marca {sp.anomalias} pregões do S&P 500 como "
                         f"anômalos — {sp.anomalias_2020} só em 2020 — e {pct(sp.pct_quedas, 0)} deles são quedas: "
                         f"a anomalia é sinal de mudança de dinâmica, não ruído a descartar.")}


# ─────────────────────────────────────────────────────────────────────────────
def shap_explicabilidade(simbolo: str = "US500", n_pontos: int = 150, n_perm: int = 40) -> dict:
    """Valores de Shapley por amostragem de permutações (estimador de Štrumbelj & Kononenko)."""
    from sklearn.ensemble import RandomForestClassifier
    df = atributos(simbolo)
    tr = df[df.index.year < 2018]
    te = df[df.index.year >= 2018].iloc[-n_pontos:]
    rf = RandomForestClassifier(n_estimators=300, max_depth=5, min_samples_leaf=40, random_state=SEMENTE,
                                n_jobs=1).fit(tr[ATR].to_numpy(), tr["alvo_dir"])
    rng = np.random.default_rng(SEMENTE)
    fundo = tr[ATR].to_numpy()[rng.integers(0, len(tr), n_perm)]
    X = te[ATR].to_numpy()
    d = X.shape[1]
    phi = np.zeros_like(X)
    lotes = []
    for i in range(X.shape[0]):
        for m in range(n_perm):
            ordem = rng.permutation(d)
            z = fundo[m].copy()
            seq = [z.copy()]
            for j in ordem:
                z[j] = X[i, j]
                seq.append(z.copy())
            lotes.append((i, ordem, np.array(seq)))
    todas = np.vstack([s for _, _, s in lotes])
    pr = rf.predict_proba(todas)[:, 1]
    pos = 0
    for i, ordem, seq in lotes:
        p = pr[pos:pos + len(seq)]
        pos += len(seq)
        for k, j in enumerate(ordem):
            phi[i, j] += p[k + 1] - p[k]
    phi /= n_perm
    imp = pd.DataFrame({"atributo": ATR, "shap_medio_abs": np.abs(phi).mean(0),
                        "shap_medio": phi.mean(0)}).sort_values("shap_medio_abs")
    ult = pd.DataFrame({"atributo": ATR, "valor": X[-1], "contribuicao": phi[-1]}).sort_values("contribuicao")
    base = float(rf.predict_proba(fundo)[:, 1].mean())
    prob_ult = float(rf.predict_proba(X[-1:])[:, 1][0])
    pontos = pd.DataFrame(phi, columns=ATR)
    pontos["data"] = te.index
    top = ult.iloc[-1] if abs(ult.iloc[-1].contribuicao) >= abs(ult.iloc[0].contribuicao) else ult.iloc[0]
    return {"tabelas": {"importancia": imp, "ultima_previsao": ult, "pontos": pontos.melt(id_vars="data",
                        var_name="atributo", value_name="shap")},
            "destaque": (f"Na última previsão, a probabilidade de alta sai de {pct(base)} (média do modelo) para "
                         f"{pct(prob_ult)}; o atributo que mais pesou foi '{top.atributo}' "
                         f"({'+' if top.contribuicao > 0 else ''}{br(top.contribuicao * 100, 1)} p.p.). "
                         f"A caixa-preta passa a responder 'por quê'.")}


# ─────────────────────────────────────────────────────────────────────────────
def drift_modelo(simbolo: str = "US500") -> dict:
    from scipy.stats import ks_2samp
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    df = atributos(simbolo)
    tr = df[(df.index.year >= 2010) & (df.index.year < 2017)]
    esc = StandardScaler().fit(tr[ATR])
    m = LogisticRegression(C=0.5, max_iter=2000).fit(esc.transform(tr[ATR]), tr["alvo_dir"])
    linhas = []
    for ano in range(2017, df.index.year.max() + 1):
        te = df[df.index.year == ano]
        if len(te) < 50:
            continue
        acc = float((m.predict(esc.transform(te[ATR])) == te["alvo_dir"]).mean())
        ks = {a: ks_2samp(tr[a], te[a]).statistic for a in ATR if a != "psar_tend"}
        # PSI da volatilidade (índice de estabilidade populacional)
        q = np.quantile(tr["vol_20"], np.linspace(0, 1, 11))
        q[0], q[-1] = -np.inf, np.inf
        e = np.histogram(tr["vol_20"], q)[0] / len(tr)
        a_ = np.histogram(te["vol_20"], q)[0] / len(te)
        e, a_ = np.clip(e, 1e-4, None), np.clip(a_, 1e-4, None)
        psi = float(np.sum((a_ - e) * np.log(a_ / e)))
        pior = max(ks, key=ks.get)
        linhas.append({"ano": ano, "acuracia": acc, "ks_max": ks[pior], "atributo_mais_deslocado": pior,
                       "psi_volatilidade": psi,
                       "alerta": "RETREINAR" if psi > 0.25 or ks[pior] > 0.25 else
                       ("atenção" if psi > 0.1 or ks[pior] > 0.15 else "estável")})
    t = pd.DataFrame(linhas)
    alertas = t[t.alerta == "RETREINAR"]
    pior = t.sort_values("acuracia").iloc[0]
    maior = t.sort_values("ks_max", ascending=False).iloc[0]
    return {"tabelas": {"anual": t},
            "destaque": (f"O modelo treinado em 2010–2016 pede retreino em {len(alertas)} dos {len(t)} anos seguintes: "
                         f"o regime de entrada daquele período não voltou. {int(pior.ano)} teve a pior acurácia "
                         f"({pct(pior.acuracia)}) e {int(maior.ano)} o maior deslocamento (KS {br(maior.ks_max)}) — "
                         f"monitorar a entrada mostra o problema sem esperar a perda.")}
