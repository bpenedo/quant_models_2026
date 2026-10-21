// quant_models_2026
// Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
// E-mail: profbruanbima@gmail.com
//
// Kernels numéricos — gêmeos de `pipeline/quant/kernels.py` (mesmos nomes, mesma matemática).
// `testes_nucleo.py` exige concordância entre Python/numba, Rust e F# (D9).
// O módulo `wasm` expõe a mesma API ao navegador (memória linear, ponteiros f64).

pub mod wasm;

use std::f64::consts::PI;

// ─────────────────────────────────────────────────────────────────────────────
// Retornos, médias e risco
// ─────────────────────────────────────────────────────────────────────────────

pub fn log_retornos(p: &[f64]) -> Vec<f64> {
    p.windows(2).map(|w| (w[1] / w[0]).ln()).collect()
}

pub fn ema(x: &[f64], n: f64) -> Vec<f64> {
    let a = 2.0 / (n + 1.0);
    let mut out = Vec::with_capacity(x.len());
    if x.is_empty() {
        return out;
    }
    out.push(x[0]);
    for i in 1..x.len() {
        let v = a * x[i] + (1.0 - a) * out[i - 1];
        out.push(v);
    }
    out
}

pub fn ewma_vol(r: &[f64], lam: f64) -> Vec<f64> {
    let n = r.len();
    let mut s2 = vec![0.0; n];
    if n == 0 {
        return s2;
    }
    s2[0] = r.iter().map(|v| v * v).sum::<f64>() / n as f64;
    for i in 1..n {
        s2[i] = lam * s2[i - 1] + (1.0 - lam) * r[i - 1] * r[i - 1];
    }
    s2.iter().map(|v| v.sqrt()).collect()
}

/// Variância condicional GARCH(1,1) e log-verossimilhança gaussiana negativa.
pub fn garch11_filtro(r: &[f64], omega: f64, alpha: f64, beta: f64) -> (Vec<f64>, f64) {
    let n = r.len();
    let mut s2 = vec![0.0; n];
    s2[0] = r.iter().map(|v| v * v).sum::<f64>() / n as f64;
    let mut nll = 0.0;
    for i in 0..n {
        if i > 0 {
            s2[i] = omega + alpha * r[i - 1] * r[i - 1] + beta * s2[i - 1];
        }
        nll += 0.5 * ((2.0 * PI).ln() + s2[i].ln() + r[i] * r[i] / s2[i]);
    }
    (s2, nll)
}

pub fn drawdown_maximo(curva: &[f64]) -> f64 {
    let mut pico = curva[0];
    let mut mdd = 0.0;
    for &v in curva {
        if v > pico {
            pico = v;
        }
        let dd = v / pico - 1.0;
        if dd < mdd {
            mdd = dd;
        }
    }
    mdd
}

pub fn sharpe_anual(r: &[f64], periodos: f64) -> f64 {
    let n = r.len();
    if n < 2 {
        return 0.0;
    }
    let m = r.iter().sum::<f64>() / n as f64;
    let v = r.iter().map(|x| (x - m) * (x - m)).sum::<f64>() / (n as f64 - 1.0);
    if v <= 0.0 {
        return 0.0;
    }
    m / v.sqrt() * periodos.sqrt()
}

/// R: T×N (linha a linha), W: P×N. Saída P×4: retorno, vol, Sharpe, drawdown.
pub fn metricas_carteiras(r: &[f64], t: usize, n: usize, w: &[f64], p: usize, periodos: f64) -> Vec<f64> {
    let mut out = vec![0.0; p * 4];
    for k in 0..p {
        let (mut curva, mut pico, mut mdd, mut s, mut s2) = (1.0f64, 1.0f64, 0.0f64, 0.0f64, 0.0f64);
        for ti in 0..t {
            let mut rp = 0.0;
            for j in 0..n {
                rp += w[k * n + j] * (r[ti * n + j].exp() - 1.0);
            }
            s += rp;
            s2 += rp * rp;
            curva *= 1.0 + rp;
            if curva > pico {
                pico = curva;
            }
            let dd = curva / pico - 1.0;
            if dd < mdd {
                mdd = dd;
            }
        }
        let m = s / t as f64;
        let v = s2 / t as f64 - m * m;
        let vol = v.max(1e-18).sqrt() * periodos.sqrt();
        let ret = m * periodos;
        out[k * 4] = ret;
        out[k * 4 + 1] = vol;
        out[k * 4 + 2] = ret / vol;
        out[k * 4 + 3] = mdd;
    }
    out
}

// ─────────────────────────────────────────────────────────────────────────────
// Indicadores técnicos
// ─────────────────────────────────────────────────────────────────────────────

pub fn rsi(p: &[f64], n: usize) -> Vec<f64> {
    let m = p.len();
    let mut out = vec![f64::NAN; m];
    if m <= n {
        return out;
    }
    let (mut g, mut q) = (0.0, 0.0);
    for i in 1..=n {
        let d = p[i] - p[i - 1];
        if d > 0.0 {
            g += d;
        } else {
            q -= d;
        }
    }
    g /= n as f64;
    q /= n as f64;
    out[n] = if q == 0.0 { 100.0 } else { 100.0 - 100.0 / (1.0 + g / q) };
    for i in n + 1..m {
        let d = p[i] - p[i - 1];
        let up = if d > 0.0 { d } else { 0.0 };
        let dn = if d < 0.0 { -d } else { 0.0 };
        g = (g * (n as f64 - 1.0) + up) / n as f64;
        q = (q * (n as f64 - 1.0) + dn) / n as f64;
        out[i] = if q == 0.0 { 100.0 } else { 100.0 - 100.0 / (1.0 + g / q) };
    }
    out
}

pub fn psar(h: &[f64], l: &[f64], passo: f64, maximo: f64) -> (Vec<f64>, Vec<f64>) {
    let n = h.len();
    let mut sar = vec![0.0; n];
    let mut tend = vec![0.0; n];
    let mut alta = true;
    let mut af = passo;
    let mut ep = h[0];
    sar[0] = l[0];
    tend[0] = 1.0;
    for i in 1..n {
        let mut s = sar[i - 1] + af * (ep - sar[i - 1]);
        if alta {
            let l2 = if i >= 2 { l[i - 2] } else { l[i - 1] };
            s = s.min(l[i - 1]).min(l2);
            if l[i] < s {
                alta = false;
                s = ep;
                ep = l[i];
                af = passo;
            } else if h[i] > ep {
                ep = h[i];
                af = (af + passo).min(maximo);
            }
        } else {
            let h2 = if i >= 2 { h[i - 2] } else { h[i - 1] };
            s = s.max(h[i - 1]).max(h2);
            if h[i] > s {
                alta = true;
                s = ep;
                ep = h[i];
                af = passo;
            } else if l[i] < ep {
                ep = l[i];
                af = (af + passo).min(maximo);
            }
        }
        sar[i] = s;
        tend[i] = if alta { 1.0 } else { -1.0 };
    }
    (sar, tend)
}

// ─────────────────────────────────────────────────────────────────────────────
// Memória longa e sinais
// ─────────────────────────────────────────────────────────────────────────────

pub fn hurst_rs(x: &[f64]) -> f64 {
    let big_n = x.len();
    let mut ns = Vec::new();
    let mut n = 8usize;
    while n <= big_n / 2 {
        ns.push(n);
        n *= 2;
    }
    if ns.len() < 2 {
        return f64::NAN;
    }
    let mut lx = Vec::with_capacity(ns.len());
    let mut ly = Vec::with_capacity(ns.len());
    for &n in &ns {
        let blocos = big_n / n;
        let (mut acc, mut cnt) = (0.0, 0usize);
        for b in 0..blocos {
            let seg = &x[b * n..(b + 1) * n];
            let m = seg.iter().sum::<f64>() / n as f64;
            let (mut z, mut zmax, mut zmin, mut s2) = (0.0f64, -1e300f64, 1e300f64, 0.0f64);
            for &v in seg {
                z += v - m;
                if z > zmax {
                    zmax = z;
                }
                if z < zmin {
                    zmin = z;
                }
                s2 += (v - m) * (v - m);
            }
            let s = (s2 / n as f64).sqrt();
            if s > 0.0 {
                acc += (zmax - zmin) / s;
                cnt += 1;
            }
        }
        lx.push((n as f64).ln());
        ly.push(if cnt > 0 { (acc / cnt as f64).ln() } else { f64::NAN });
    }
    let k = lx.len() as f64;
    let mx = lx.iter().sum::<f64>() / k;
    let my = ly.iter().sum::<f64>() / k;
    let (mut num, mut den) = (0.0, 0.0);
    for i in 0..lx.len() {
        num += (lx[i] - mx) * (ly[i] - my);
        den += (lx[i] - mx) * (lx[i] - mx);
    }
    num / den
}

pub fn hurst_movel(r: &[f64], janela: usize) -> Vec<f64> {
    let n = r.len();
    let mut out = vec![f64::NAN; n];
    for i in janela..=n {
        out[i - 1] = hurst_rs(&r[i - janela..i]);
    }
    out
}

/// DWT de Haar: (aproximação final, energia por nível, detalhe nível 1 reamostrado).
pub fn haar_dwt(x: &[f64], niveis: usize) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let mut a = x.to_vec();
    let mut energia = vec![0.0; niveis];
    let n0 = x.len();
    let mut d1 = vec![0.0; n0];
    let r2 = 2.0f64.sqrt();
    for lv in 0..niveis {
        let m = a.len() / 2;
        if m < 1 {
            break;
        }
        let mut na = vec![0.0; m];
        let mut nd = vec![0.0; m];
        for i in 0..m {
            na[i] = (a[2 * i] + a[2 * i + 1]) / r2;
            nd[i] = (a[2 * i] - a[2 * i + 1]) / r2;
        }
        energia[lv] = nd.iter().map(|v| v * v).sum();
        if lv == 0 {
            for i in 0..m {
                d1[2 * i] = nd[i];
                d1[2 * i + 1] = nd[i];
            }
        }
        a = na;
    }
    (a, energia, d1)
}

// ─────────────────────────────────────────────────────────────────────────────
// Markov / HMM
// ─────────────────────────────────────────────────────────────────────────────

pub fn matriz_transicao(estados: &[usize], k: usize) -> Vec<f64> {
    let mut p = vec![0.0; k * k];
    for i in 1..estados.len() {
        p[estados[i - 1] * k + estados[i]] += 1.0;
    }
    for i in 0..k {
        let s: f64 = p[i * k..(i + 1) * k].iter().sum();
        if s > 0.0 {
            for j in 0..k {
                p[i * k + j] /= s;
            }
        }
    }
    p
}

fn gauss(x: f64, m: f64, s: f64) -> f64 {
    (-0.5 * ((x - m) / s).powi(2)).exp() / (s * (2.0 * PI).sqrt())
}

pub struct Hmm {
    pub pi: Vec<f64>,
    pub a: Vec<f64>,
    pub mu: Vec<f64>,
    pub sd: Vec<f64>,
    pub gamma: Vec<f64>,
    pub ll: f64,
}

/// HMM gaussiano 1D por Baum-Welch escalonado — mesma ordem de operações do numba.
pub fn hmm_gaussiano_em(x: &[f64], mu0: &[f64], sd0: &[f64], iters: usize, tol: f64) -> Hmm {
    let t_n = x.len();
    let k = mu0.len();
    let mut mu = mu0.to_vec();
    let mut sd = sd0.to_vec();
    let mut a = vec![0.02 / (k as f64 - 1.0); k * k];
    for i in 0..k {
        a[i * k + i] = 0.98;
    }
    let mut pi = vec![1.0 / k as f64; k];
    let mut alpha = vec![0.0; t_n * k];
    let mut beta = vec![0.0; t_n * k];
    let mut c = vec![0.0; t_n];
    let mut b = vec![0.0; t_n * k];
    let mut gamma = vec![0.0; t_n * k];
    let mut ll_ant = -1e300;
    let mut ll = 0.0;
    for _ in 0..iters {
        for t in 0..t_n {
            for j in 0..k {
                b[t * k + j] = gauss(x[t], mu[j], sd[j]).max(1e-300);
            }
        }
        let mut s = 0.0;
        for j in 0..k {
            alpha[j] = pi[j] * b[j];
            s += alpha[j];
        }
        c[0] = s;
        for j in 0..k {
            alpha[j] /= s;
        }
        for t in 1..t_n {
            let mut s = 0.0;
            for j in 0..k {
                let mut acc = 0.0;
                for i in 0..k {
                    acc += alpha[(t - 1) * k + i] * a[i * k + j];
                }
                alpha[t * k + j] = acc * b[t * k + j];
                s += alpha[t * k + j];
            }
            c[t] = s;
            for j in 0..k {
                alpha[t * k + j] /= s;
            }
        }
        for j in 0..k {
            beta[(t_n - 1) * k + j] = 1.0;
        }
        for t in (0..t_n - 1).rev() {
            for i in 0..k {
                let mut acc = 0.0;
                for j in 0..k {
                    acc += a[i * k + j] * b[(t + 1) * k + j] * beta[(t + 1) * k + j];
                }
                beta[t * k + i] = acc / c[t + 1];
            }
        }
        ll = c.iter().map(|v| v.ln()).sum();
        for t in 0..t_n {
            let mut s = 0.0;
            for j in 0..k {
                gamma[t * k + j] = alpha[t * k + j] * beta[t * k + j];
                s += gamma[t * k + j];
            }
            for j in 0..k {
                gamma[t * k + j] /= s;
            }
        }
        let mut xi = vec![0.0; k * k];
        for t in 0..t_n - 1 {
            for i in 0..k {
                for j in 0..k {
                    xi[i * k + j] +=
                        alpha[t * k + i] * a[i * k + j] * b[(t + 1) * k + j] * beta[(t + 1) * k + j] / c[t + 1];
                }
            }
        }
        for j in 0..k {
            pi[j] = gamma[j];
        }
        for i in 0..k {
            let s: f64 = xi[i * k..(i + 1) * k].iter().sum();
            for j in 0..k {
                a[i * k + j] = if s > 0.0 { xi[i * k + j] / s } else { 1.0 / k as f64 };
            }
        }
        for j in 0..k {
            let (mut w, mut m) = (0.0, 0.0);
            for t in 0..t_n {
                w += gamma[t * k + j];
                m += gamma[t * k + j] * x[t];
            }
            m /= w;
            let mut v = 0.0;
            for t in 0..t_n {
                v += gamma[t * k + j] * (x[t] - m).powi(2);
            }
            mu[j] = m;
            sd[j] = (v / w).sqrt().max(1e-6);
        }
        if (ll - ll_ant).abs() < tol {
            break;
        }
        ll_ant = ll;
    }
    Hmm { pi, a, mu, sd, gamma, ll }
}

// ─────────────────────────────────────────────────────────────────────────────
// Monte Carlo O-U — mesmo gerador xorshift64* do numba ⇒ mesmas trajetórias
// ─────────────────────────────────────────────────────────────────────────────

#[inline]
fn xorshift(estado: &mut u64) -> u64 {
    *estado ^= *estado >> 12;
    *estado ^= *estado << 25;
    *estado ^= *estado >> 27;
    estado.wrapping_mul(2685821657736338717)
}

#[inline]
fn normal(estado: &mut u64) -> f64 {
    let a = xorshift(estado);
    let b = xorshift(estado);
    let u1 = ((a >> 11) + 1) as f64 * (1.0 / 9007199254740993.0);
    let u2 = (b >> 11) as f64 * (1.0 / 9007199254740992.0);
    (-2.0 * u1.ln()).sqrt() * (2.0 * PI * u2).cos()
}

pub fn ou_sharpe_malha(
    previsao: f64, meia_vida: f64, sigma: f64, pts: &[f64], sls: &[f64], n_iter: usize, max_hp: usize,
    semente: u64,
) -> Vec<f64> {
    let phi = 2.0f64.powf(-1.0 / meia_vida);
    let mut out = vec![0.0; pts.len() * sls.len()];
    let mut estado = semente;
    for (a, &pt) in pts.iter().enumerate() {
        for (b, &sl) in sls.iter().enumerate() {
            let (mut s, mut s2) = (0.0, 0.0);
            for _ in 0..n_iter {
                let mut p = 0.0;
                for _ in 0..max_hp {
                    let z = normal(&mut estado);
                    p = (1.0 - phi) * previsao + phi * p + sigma * z;
                    if p > pt || p < -sl {
                        break;
                    }
                }
                s += p;
                s2 += p * p;
            }
            let m = s / n_iter as f64;
            let v = s2 / n_iter as f64 - m * m;
            out[a * sls.len() + b] = if v > 0.0 { m / v.sqrt() } else { 0.0 };
        }
    }
    out
}

// ─────────────────────────────────────────────────────────────────────────────
// Programação genética — máquina de pilha pós-fixa
// ─────────────────────────────────────────────────────────────────────────────

/// X: T×nvars (linha a linha). Códigos: <100 variável · 100 constante · 200+op.
pub fn avaliar_posfixa(codigo: &[i64], consts: &[f64], x: &[f64], t_n: usize, nvars: usize) -> Vec<f64> {
    let mut pilha: Vec<Vec<f64>> = Vec::with_capacity(codigo.len());
    for (i, &c) in codigo.iter().enumerate() {
        if c < 100 {
            pilha.push((0..t_n).map(|t| x[t * nvars + c as usize]).collect());
        } else if c == 100 {
            pilha.push(vec![consts[i]; t_n]);
        } else {
            let op = c - 200;
            if op >= 4 && op != 6 {
                let a = pilha.last_mut().unwrap();
                for v in a.iter_mut() {
                    *v = match op {
                        4 => v.sin(),
                        5 => v.cos(),
                        _ => -*v,
                    };
                }
            } else {
                let b = pilha.pop().unwrap();
                let a = pilha.last_mut().unwrap();
                for t in 0..t_n {
                    a[t] = match op {
                        0 => a[t] + b[t],
                        1 => a[t] - b[t],
                        2 => a[t] * b[t],
                        3 => {
                            if b[t].abs() > 1e-12 {
                                a[t] / b[t]
                            } else {
                                1.0
                            }
                        }
                        _ => a[t].max(b[t]),
                    };
                }
            }
        }
    }
    pilha.swap_remove(0)
}

// ─────────────────────────────────────────────────────────────────────────────
// Diversos
// ─────────────────────────────────────────────────────────────────────────────

pub fn primeiros_digitos(x: &[f64]) -> [f64; 9] {
    let mut cont = [0.0; 9];
    for &v0 in x {
        let mut v = v0.abs();
        if v <= 0.0 || !v.is_finite() {
            continue;
        }
        while v >= 10.0 {
            v /= 10.0;
        }
        while v < 1.0 {
            v *= 10.0;
        }
        let d = v as usize;
        if (1..=9).contains(&d) {
            cont[d - 1] += 1.0;
        }
    }
    cont
}

pub fn kmeans_1d(x: &[f64], k: usize, iters: usize) -> (Vec<f64>, Vec<usize>) {
    let mut xs = x.to_vec();
    xs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let n = xs.len();
    let mut c: Vec<f64> = (0..k).map(|i| xs[((i as f64 + 0.5) * n as f64 / k as f64) as usize]).collect();
    let mut rot = vec![0usize; x.len()];
    for _ in 0..iters {
        for (i, &v) in x.iter().enumerate() {
            let mut best = 0;
            let mut bd = 1e300;
            for (j, &cj) in c.iter().enumerate() {
                let d = (v - cj).abs();
                if d < bd {
                    bd = d;
                    best = j;
                }
            }
            rot[i] = best;
        }
        let mut mudou = false;
        for j in 0..k {
            let (mut s, mut cnt) = (0.0, 0usize);
            for (i, &v) in x.iter().enumerate() {
                if rot[i] == j {
                    s += v;
                    cnt += 1;
                }
            }
            if cnt > 0 {
                let nv = s / cnt as f64;
                if (nv - c[j]).abs() > 1e-12 {
                    mudou = true;
                }
                c[j] = nv;
            }
        }
        if !mudou {
            break;
        }
    }
    (c, rot)
}

// ─────────────────────────────────────────────────────────────────────────────
// Algoritmo genético de carteira (nativo) — mesmo gerador xorshift64* do F#:
// Rust e F# produzem a MESMA evolução, bit a bit; o Python (numpy) serve de referência de qualidade.
// ─────────────────────────────────────────────────────────────────────────────

#[inline]
fn uniforme(estado: &mut u64) -> f64 {
    (xorshift(estado) >> 11) as f64 * (1.0 / 9007199254740992.0)
}

/// Pesos aleatórios no simplex via exponenciais normalizadas (Dirichlet(1)).
fn dirichlet(estado: &mut u64, n: usize) -> Vec<f64> {
    let mut w: Vec<f64> = (0..n).map(|_| -(1.0 - uniforme(estado)).ln()).collect();
    let s: f64 = w.iter().sum();
    w.iter_mut().for_each(|v| *v /= s);
    w
}

/// Devolve (melhores pesos, histórico da melhor aptidão por geração).
/// Aptidão = Sharpe + penal_dd × drawdown (drawdown negativo).
pub fn ag_carteira(
    r: &[f64], t: usize, n: usize, pop: usize, geracoes: usize, elite: usize, taxa_mut: f64, penal_dd: f64,
    semente: u64,
) -> (Vec<f64>, Vec<f64>) {
    let mut estado = semente.max(1);
    let mut p: Vec<f64> = (0..pop).flat_map(|_| dirichlet(&mut estado, n)).collect();
    let mut hist = Vec::with_capacity(geracoes);
    let aptidao = |p: &[f64]| -> Vec<f64> {
        let m = metricas_carteiras(r, t, n, p, pop, 252.0);
        (0..pop).map(|k| m[k * 4 + 2] + penal_dd * m[k * 4 + 3]).collect()
    };
    for _ in 0..geracoes {
        let apt = aptidao(&p);
        let mut ordem: Vec<usize> = (0..pop).collect();
        ordem.sort_by(|&a, &b| apt[b].partial_cmp(&apt[a]).unwrap().then(a.cmp(&b)));
        hist.push(apt[ordem[0]]);
        let minimo = apt.iter().cloned().fold(f64::INFINITY, f64::min);
        let pesos: Vec<f64> = apt.iter().map(|a| a - minimo + 1e-9).collect();
        let total: f64 = pesos.iter().sum();
        let roleta = |estado: &mut u64| -> usize {
            let alvo = uniforme(estado) * total;
            let mut acc = 0.0;
            for (i, w) in pesos.iter().enumerate() {
                acc += w;
                if acc >= alvo {
                    return i;
                }
            }
            pop - 1
        };
        let mut nova = Vec::with_capacity(pop * n);
        for &i in ordem.iter().take(elite) {
            nova.extend_from_slice(&p[i * n..(i + 1) * n]);
        }
        while nova.len() < pop * n {
            let a = roleta(&mut estado);
            let b = roleta(&mut estado);
            let corte = 1 + (uniforme(&mut estado) * (n as f64 - 1.0)) as usize;
            let mut filho: Vec<f64> =
                (0..n).map(|j| if j < corte { p[a * n + j] } else { p[b * n + j] }).collect();
            if uniforme(&mut estado) < taxa_mut {
                let j = (uniforme(&mut estado) * n as f64) as usize % n;
                filho[j] = (filho[j] + 0.15 * normal(&mut estado)).max(0.0);
            }
            let s: f64 = filho.iter().sum();
            if s > 0.0 {
                filho.iter_mut().for_each(|v| *v /= s);
            } else {
                filho.iter_mut().for_each(|v| *v = 1.0 / n as f64);
            }
            nova.extend_from_slice(&filho);
        }
        p = nova;
    }
    let apt = aptidao(&p);
    let mut melhor = 0;
    for k in 1..pop {
        if apt[k] > apt[melhor] {
            melhor = k;
        }
    }
    (p[melhor * n..(melhor + 1) * n].to_vec(), hist)
}
