# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Kernels numéricos quentes — NumPy SEMPRE com numba (D13).

Cada kernel tem um gêmeo em Rust (rust/quant_models_2026_core/src/lib.rs) com o MESMO
nome; `testes_nucleo.py` exige que os dois motores concordem (D9). Mudar a matemática
de um lado sem o outro reprova a Passada 1.
"""
from __future__ import annotations

import math

import numpy as np

from config import njit

# ─────────────────────────────────────────────────────────────────────────────
# Retornos, médias e risco
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def log_retornos(p):
    n = p.shape[0]
    r = np.empty(max(n - 1, 0))
    for i in range(1, n):
        r[i - 1] = math.log(p[i] / p[i - 1])
    return r


@njit(cache=True)
def ema(x, n):
    """Média móvel exponencial com alfa = 2/(n+1), semente = primeiro valor."""
    out = np.empty_like(x)
    a = 2.0 / (n + 1.0)
    out[0] = x[0]
    for i in range(1, x.shape[0]):
        out[i] = a * x[i] + (1.0 - a) * out[i - 1]
    return out


@njit(cache=True)
def ewma_vol(r, lam):
    """Volatilidade EWMA (RiskMetrics): σ²_t = λσ²_{t-1} + (1-λ) r²_{t-1}. Semente = variância amostral."""
    n = r.shape[0]
    s2 = np.empty(n)
    v = 0.0
    for i in range(n):
        v += r[i] * r[i]
    s2[0] = v / n
    for i in range(1, n):
        s2[i] = lam * s2[i - 1] + (1.0 - lam) * r[i - 1] * r[i - 1]
    return np.sqrt(s2)


@njit(cache=True)
def garch11_filtro(r, omega, alpha, beta):
    """Variância condicional GARCH(1,1) e log-verossimilhança gaussiana (negativa)."""
    n = r.shape[0]
    s2 = np.empty(n)
    v = 0.0
    for i in range(n):
        v += r[i] * r[i]
    s2[0] = v / n
    nll = 0.0
    for i in range(n):
        if i > 0:
            s2[i] = omega + alpha * r[i - 1] * r[i - 1] + beta * s2[i - 1]
        nll += 0.5 * (math.log(2.0 * math.pi) + math.log(s2[i]) + r[i] * r[i] / s2[i])
    return s2, nll


@njit(cache=True)
def drawdown_maximo(curva):
    pico = curva[0]
    mdd = 0.0
    for v in curva:
        if v > pico:
            pico = v
        dd = v / pico - 1.0
        if dd < mdd:
            mdd = dd
    return mdd


@njit(cache=True)
def sharpe_anual(r, periodos):
    n = r.shape[0]
    if n < 2:
        return 0.0
    m = 0.0
    for x in r:
        m += x
    m /= n
    v = 0.0
    for x in r:
        v += (x - m) * (x - m)
    v /= n - 1
    if v <= 0.0:
        return 0.0
    return m / math.sqrt(v) * math.sqrt(periodos)


@njit(cache=True)
def metricas_carteiras(R, W, periodos, penal_dd):
    """Para cada linha de W (pesos), retorno/vol/Sharpe/drawdown da carteira sobre R (T×N log-retornos).

    Aptidão = Sharpe + penal_dd · drawdown (drawdown é negativo). Rebalanceamento diário.
    """
    P = W.shape[0]
    T = R.shape[0]
    out = np.empty((P, 4))
    for k in range(P):
        curva = 1.0
        pico = 1.0
        mdd = 0.0
        s = 0.0
        s2 = 0.0
        for t in range(T):
            rp = 0.0
            for j in range(R.shape[1]):
                rp += W[k, j] * (math.exp(R[t, j]) - 1.0)
            s += rp
            s2 += rp * rp
            curva *= 1.0 + rp
            if curva > pico:
                pico = curva
            dd = curva / pico - 1.0
            if dd < mdd:
                mdd = dd
        m = s / T
        v = s2 / T - m * m
        vol = math.sqrt(max(v, 1e-18)) * math.sqrt(periodos)
        ret = m * periodos
        sh = ret / vol
        out[k, 0] = ret
        out[k, 1] = vol
        out[k, 2] = sh
        out[k, 3] = mdd
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Indicadores técnicos
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def rsi(p, n):
    """RSI de Wilder."""
    m = p.shape[0]
    out = np.full(m, np.nan)
    if m <= n:
        return out
    g = 0.0
    q = 0.0
    for i in range(1, n + 1):
        d = p[i] - p[i - 1]
        if d > 0:
            g += d
        else:
            q -= d
    g /= n
    q /= n
    out[n] = 100.0 if q == 0 else 100.0 - 100.0 / (1.0 + g / q)
    for i in range(n + 1, m):
        d = p[i] - p[i - 1]
        up = d if d > 0 else 0.0
        dn = -d if d < 0 else 0.0
        g = (g * (n - 1) + up) / n
        q = (q * (n - 1) + dn) / n
        out[i] = 100.0 if q == 0 else 100.0 - 100.0 / (1.0 + g / q)
    return out


@njit(cache=True)
def psar(h, l, passo, maximo):
    """Parabolic SAR de Wilder. Devolve (sar, tendencia ±1)."""
    n = h.shape[0]
    sar = np.empty(n)
    tend = np.empty(n)
    alta = True
    af = passo
    ep = h[0]
    sar[0] = l[0]
    tend[0] = 1.0
    for i in range(1, n):
        s = sar[i - 1] + af * (ep - sar[i - 1])
        if alta:
            s = min(s, l[i - 1], l[i - 2] if i >= 2 else l[i - 1])
            if l[i] < s:
                alta = False
                s = ep
                ep = l[i]
                af = passo
            else:
                if h[i] > ep:
                    ep = h[i]
                    af = min(af + passo, maximo)
        else:
            s = max(s, h[i - 1], h[i - 2] if i >= 2 else h[i - 1])
            if h[i] > s:
                alta = True
                s = ep
                ep = h[i]
                af = passo
            else:
                if l[i] < ep:
                    ep = l[i]
                    af = min(af + passo, maximo)
        sar[i] = s
        tend[i] = 1.0 if alta else -1.0
    return sar, tend


# ─────────────────────────────────────────────────────────────────────────────
# Memória longa e sinais
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def hurst_rs(x):
    """Expoente de Hurst por R/S clássico: regressão de log(R/S) em log(n) para n = 8, 16, 32, …"""
    N = x.shape[0]
    ns = []
    n = 8
    while n <= N // 2:
        ns.append(n)
        n *= 2
    if len(ns) < 2:
        return np.nan
    lx = np.empty(len(ns))
    ly = np.empty(len(ns))
    for k in range(len(ns)):
        n = ns[k]
        blocos = N // n
        acc = 0.0
        cnt = 0
        for b in range(blocos):
            seg = x[b * n:(b + 1) * n]
            m = seg.mean()
            z = 0.0
            zmax = -1e300
            zmin = 1e300
            s2 = 0.0
            for v in seg:
                z += v - m
                if z > zmax:
                    zmax = z
                if z < zmin:
                    zmin = z
                s2 += (v - m) * (v - m)
            s = math.sqrt(s2 / n)
            if s > 0:
                acc += (zmax - zmin) / s
                cnt += 1
        lx[k] = math.log(n)
        ly[k] = math.log(acc / cnt) if cnt > 0 else np.nan
    mx = lx.mean()
    my = ly.mean()
    num = 0.0
    den = 0.0
    for k in range(lx.shape[0]):
        num += (lx[k] - mx) * (ly[k] - my)
        den += (lx[k] - mx) * (lx[k] - mx)
    return num / den


@njit(cache=True)
def hurst_movel(r, janela):
    n = r.shape[0]
    out = np.full(n, np.nan)
    for i in range(janela, n + 1):
        out[i - 1] = hurst_rs(r[i - janela:i])
    return out


@njit(cache=True)
def haar_dwt(x, niveis):
    """DWT de Haar multinível. Devolve (aproximação final, energia dos detalhes por nível,
    detalhe de nível 1 reamostrado para o tamanho original)."""
    a = x.copy()
    energia = np.zeros(niveis)
    n0 = x.shape[0]
    d1 = np.zeros(n0)
    for lv in range(niveis):
        m = a.shape[0] // 2
        if m < 1:
            break
        na = np.empty(m)
        nd = np.empty(m)
        for i in range(m):
            na[i] = (a[2 * i] + a[2 * i + 1]) / math.sqrt(2.0)
            nd[i] = (a[2 * i] - a[2 * i + 1]) / math.sqrt(2.0)
        e = 0.0
        for v in nd:
            e += v * v
        energia[lv] = e
        if lv == 0:
            for i in range(m):
                d1[2 * i] = nd[i]
                d1[2 * i + 1] = nd[i]
        a = na
    return a, energia, d1


# ─────────────────────────────────────────────────────────────────────────────
# Markov / HMM
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def matriz_transicao(estados, k):
    P = np.zeros((k, k))
    for i in range(1, estados.shape[0]):
        P[estados[i - 1], estados[i]] += 1.0
    for i in range(k):
        s = P[i].sum()
        if s > 0:
            P[i] /= s
    return P


@njit(cache=True)
def _gauss(x, m, s):
    return math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2.0 * math.pi))


@njit(cache=True)
def hmm_gaussiano_em(x, mu0, sd0, iters, tol):
    """HMM gaussiano 1D por Baum-Welch (forward-backward escalonado).

    Devolve (pi, A, mu, sd, gamma, loglik). Estados ordenados por média crescente na saída.
    """
    T = x.shape[0]
    K = mu0.shape[0]
    mu = mu0.copy()
    sd = sd0.copy()
    A = np.full((K, K), 0.02 / (K - 1))
    for i in range(K):
        A[i, i] = 0.98
    pi = np.full(K, 1.0 / K)
    alpha = np.empty((T, K))
    beta = np.empty((T, K))
    c = np.empty(T)
    B = np.empty((T, K))
    gamma = np.empty((T, K))
    ll_ant = -1e300
    ll = 0.0
    for _ in range(iters):
        for t in range(T):
            for k in range(K):
                B[t, k] = max(_gauss(x[t], mu[k], sd[k]), 1e-300)
        # forward
        s = 0.0
        for k in range(K):
            alpha[0, k] = pi[k] * B[0, k]
            s += alpha[0, k]
        c[0] = s
        for k in range(K):
            alpha[0, k] /= s
        for t in range(1, T):
            s = 0.0
            for j in range(K):
                acc = 0.0
                for i in range(K):
                    acc += alpha[t - 1, i] * A[i, j]
                alpha[t, j] = acc * B[t, j]
                s += alpha[t, j]
            c[t] = s
            for j in range(K):
                alpha[t, j] /= s
        # backward
        for k in range(K):
            beta[T - 1, k] = 1.0
        for t in range(T - 2, -1, -1):
            for i in range(K):
                acc = 0.0
                for j in range(K):
                    acc += A[i, j] * B[t + 1, j] * beta[t + 1, j]
                beta[t, i] = acc / c[t + 1]
        ll = 0.0
        for t in range(T):
            ll += math.log(c[t])
        # E
        for t in range(T):
            s = 0.0
            for k in range(K):
                gamma[t, k] = alpha[t, k] * beta[t, k]
                s += gamma[t, k]
            for k in range(K):
                gamma[t, k] /= s
        xi = np.zeros((K, K))
        for t in range(T - 1):
            for i in range(K):
                for j in range(K):
                    xi[i, j] += alpha[t, i] * A[i, j] * B[t + 1, j] * beta[t + 1, j] / c[t + 1]
        # M
        for k in range(K):
            pi[k] = gamma[0, k]
        for i in range(K):
            s = xi[i].sum()
            for j in range(K):
                A[i, j] = xi[i, j] / s if s > 0 else 1.0 / K
        for k in range(K):
            w = 0.0
            m = 0.0
            for t in range(T):
                w += gamma[t, k]
                m += gamma[t, k] * x[t]
            m /= w
            v = 0.0
            for t in range(T):
                v += gamma[t, k] * (x[t] - m) ** 2
            mu[k] = m
            sd[k] = max(math.sqrt(v / w), 1e-6)
        if abs(ll - ll_ant) < tol:
            break
        ll_ant = ll
    return pi, A, mu, sd, gamma, ll


# ─────────────────────────────────────────────────────────────────────────────
# Monte Carlo — regras ótimas de trading (López de Prado, cap. 13)
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def _lcg(estado):
    # gerador determinístico (mesma sequência no Rust): xorshift64*
    estado ^= estado >> np.uint64(12)
    estado ^= estado << np.uint64(25)
    estado ^= estado >> np.uint64(27)
    return estado, (estado * np.uint64(2685821657736338717))


@njit(cache=True)
def _normal(estado):
    estado, a = _lcg(estado)
    estado, b = _lcg(estado)
    u1 = ((a >> np.uint64(11)) + np.uint64(1)) * (1.0 / 9007199254740993.0)
    u2 = (b >> np.uint64(11)) * (1.0 / 9007199254740992.0)
    return estado, math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


@njit(cache=True)
def ou_sharpe_malha(previsao, meia_vida, sigma, pts, sls, n_iter, max_hp, semente):
    """Para cada (alvo de lucro, stop) simula trajetórias O-U e devolve a malha de Sharpe.

    P_t = (1-φ)·E[P] + φ·P_{t-1} + σ·ε,  φ = 2^(-1/meia_vida),  P_0 = 0.
    Saída na primeira barreira tocada (lucro, stop ou max_hp).
    """
    phi = 2.0 ** (-1.0 / meia_vida)
    out = np.empty((pts.shape[0], sls.shape[0]))
    estado = np.uint64(semente)
    for a in range(pts.shape[0]):
        for b in range(sls.shape[0]):
            s = 0.0
            s2 = 0.0
            for _ in range(n_iter):
                p = 0.0
                for _h in range(max_hp):
                    estado, z = _normal(estado)
                    p = (1.0 - phi) * previsao + phi * p + sigma * z
                    if p > pts[a] or p < -sls[b]:
                        break
                s += p
                s2 += p * p
            m = s / n_iter
            v = s2 / n_iter - m * m
            out[a, b] = m / math.sqrt(v) if v > 0 else 0.0
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Programação genética — avaliação de árvores em notação pós-fixa (máquina de pilha)
# ─────────────────────────────────────────────────────────────────────────────
# códigos: 0..(nvars-1) variáveis; 100 constante (valor em consts); 200 + op
OP_SOMA, OP_SUB, OP_MUL, OP_DIV, OP_SEN, OP_COS, OP_MAX, OP_NEG = range(8)


@njit(cache=True)
def avaliar_posfixa(codigo, consts, X):
    """Avalia um programa pós-fixo sobre todas as linhas de X (T × nvars)."""
    T = X.shape[0]
    pilha = np.empty((codigo.shape[0], T))
    topo = 0
    for i in range(codigo.shape[0]):
        c = codigo[i]
        if c < 100:
            pilha[topo, :] = X[:, c]
            topo += 1
        elif c == 100:
            pilha[topo, :] = consts[i]
            topo += 1
        else:
            op = c - 200
            if op >= OP_SEN and op != OP_MAX:
                a = pilha[topo - 1]
                if op == OP_SEN:
                    pilha[topo - 1, :] = np.sin(a)
                elif op == OP_COS:
                    pilha[topo - 1, :] = np.cos(a)
                else:
                    pilha[topo - 1, :] = -a
            else:
                b = pilha[topo - 1].copy()
                a = pilha[topo - 2]
                topo -= 1
                if op == OP_SOMA:
                    pilha[topo - 1, :] = a + b
                elif op == OP_SUB:
                    pilha[topo - 1, :] = a - b
                elif op == OP_MUL:
                    pilha[topo - 1, :] = a * b
                elif op == OP_DIV:
                    for t in range(T):
                        pilha[topo - 1, t] = a[t] / b[t] if abs(b[t]) > 1e-12 else 1.0
                else:
                    pilha[topo - 1, :] = np.maximum(a, b)
    return pilha[0].copy()


# ─────────────────────────────────────────────────────────────────────────────
# Diversos
# ─────────────────────────────────────────────────────────────────────────────


@njit(cache=True)
def primeiros_digitos(x):
    cont = np.zeros(9)
    for v in x:
        v = abs(v)
        if v <= 0 or not math.isfinite(v):
            continue
        while v >= 10.0:
            v /= 10.0
        while v < 1.0:
            v *= 10.0
        d = int(v)
        if 1 <= d <= 9:
            cont[d - 1] += 1.0
    return cont


@njit(cache=True)
def kmeans_1d(x, k, iters):
    xs = np.sort(x)
    c = np.empty(k)
    for i in range(k):
        c[i] = xs[int((i + 0.5) * xs.shape[0] / k)]
    rot = np.zeros(x.shape[0], dtype=np.int64)
    for _ in range(iters):
        for i in range(x.shape[0]):
            best = 0
            bd = 1e300
            for j in range(k):
                d = abs(x[i] - c[j])
                if d < bd:
                    bd = d
                    best = j
            rot[i] = best
        mudou = False
        for j in range(k):
            s = 0.0
            n = 0
            for i in range(x.shape[0]):
                if rot[i] == j:
                    s += x[i]
                    n += 1
            if n > 0:
                nv = s / n
                if abs(nv - c[j]) > 1e-12:
                    mudou = True
                c[j] = nv
        if not mudou:
            break
    return c, rot
