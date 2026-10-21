// quant_models_2026
// Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
// E-mail: profbruanbima@gmail.com
//
// Interface C/WASM sem wasm-bindgen: o JavaScript reserva buffers com `qm_alocar`, escreve
// os f64 na memória linear, chama o kernel e lê o resultado. Zero dependências, zero servidor:
// o cálculo roda no navegador do usuário (D10/D27).

use std::alloc::{alloc, dealloc, Layout};
use std::slice;

#[no_mangle]
pub extern "C" fn qm_alocar(n_f64: usize) -> *mut f64 {
    let layout = Layout::array::<f64>(n_f64.max(1)).unwrap();
    unsafe { alloc(layout) as *mut f64 }
}

/// # Safety
/// `ptr` precisa ter vindo de `qm_alocar(n_f64)` com o mesmo `n_f64`.
#[no_mangle]
pub unsafe extern "C" fn qm_liberar(ptr: *mut f64, n_f64: usize) {
    let layout = Layout::array::<f64>(n_f64.max(1)).unwrap();
    dealloc(ptr as *mut u8, layout);
}

unsafe fn ler<'a>(p: *const f64, n: usize) -> &'a [f64] {
    slice::from_raw_parts(p, n)
}

unsafe fn escrever(p: *mut f64, v: &[f64]) {
    slice::from_raw_parts_mut(p, v.len()).copy_from_slice(v);
}

/// # Safety
/// Ponteiros válidos para `n` f64.
#[no_mangle]
pub unsafe extern "C" fn qm_hurst_rs(x: *const f64, n: usize) -> f64 {
    crate::hurst_rs(ler(x, n))
}

/// # Safety
/// `saida` com espaço para `n` f64.
#[no_mangle]
pub unsafe extern "C" fn qm_hurst_movel(r: *const f64, n: usize, janela: usize, saida: *mut f64) {
    escrever(saida, &crate::hurst_movel(ler(r, n), janela));
}

/// # Safety
/// `saida` com espaço para `n` f64.
#[no_mangle]
pub unsafe extern "C" fn qm_ewma_vol(r: *const f64, n: usize, lam: f64, saida: *mut f64) {
    escrever(saida, &crate::ewma_vol(ler(r, n), lam));
}

/// # Safety
/// `saida` com espaço para `npts × nsls` f64. A semente chega como f64 (inteiro exato ≤ 2^53).
#[no_mangle]
pub unsafe extern "C" fn qm_ou_sharpe_malha(
    previsao: f64, meia_vida: f64, sigma: f64, pts: *const f64, npts: usize, sls: *const f64, nsls: usize,
    n_iter: usize, max_hp: usize, semente: f64, saida: *mut f64,
) {
    let m = crate::ou_sharpe_malha(previsao, meia_vida, sigma, ler(pts, npts), ler(sls, nsls), n_iter, max_hp,
                                   semente as u64);
    escrever(saida, &m);
}

/// # Safety
/// `r` T×N, `w` P×N, `saida` P×4.
#[no_mangle]
pub unsafe extern "C" fn qm_metricas_carteiras(
    r: *const f64, t: usize, n: usize, w: *const f64, p: usize, saida: *mut f64,
) {
    escrever(saida, &crate::metricas_carteiras(ler(r, t * n), t, n, ler(w, p * n), p, 252.0));
}

/// # Safety
/// `pesos` com `n` f64; `hist` com `geracoes` f64.
#[no_mangle]
pub unsafe extern "C" fn qm_ag_carteira(
    r: *const f64, t: usize, n: usize, pop: usize, geracoes: usize, penal_dd: f64, semente: f64,
    pesos: *mut f64, hist: *mut f64,
) {
    let (w, h) = crate::ag_carteira(ler(r, t * n), t, n, pop, geracoes, 4, 0.3, penal_dd, semente as u64);
    escrever(pesos, &w);
    escrever(hist, &h);
}

/// # Safety
/// `saida` com `niveis` f64 (energia por nível).
#[no_mangle]
pub unsafe extern "C" fn qm_haar_energia(x: *const f64, n: usize, niveis: usize, saida: *mut f64) {
    let (_, e, _) = crate::haar_dwt(ler(x, n), niveis);
    escrever(saida, &e);
}
