<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com

Laboratório no navegador: o MESMO motor Rust dos testes de concordância, compilado para
wasm32, roda aqui sobre retornos reais. Sem servidor, sem custo por usuário (D10/D27).
-->
<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';   // respeita o basePath do GitHub Pages / Cloudflare

  let w = null, dados = null, erro = '';
  let ativo = 0, janela = 250, lambda = 0.94;
  let previsao = 0, meiaVida = 5, trajetorias = 1500;
  let pop = 80, geracoes = 40, penal = 0.5, semente = 7;
  let hurst = null, ou = null, ag = null, tHurst = 0, tOu = 0, tAg = 0;

  const fmt = (x, c = 2) => Number.isFinite(x)
    ? x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c }) : '—';

  onMount(async () => {
    try {
      const [wasm, json] = await Promise.all([
        fetch(`${base}/qm_core.wasm`).then((r) => r.arrayBuffer()),
        fetch(`${base}/laboratorio.json`).then((r) => r.json()),
      ]);
      const { instance } = await WebAssembly.instantiate(wasm, {});
      w = instance.exports;
      dados = json;
    } catch (e) {
      erro = 'Não foi possível carregar o motor WebAssembly: ' + e;
    }
  });

  // A memória do WASM pode crescer a cada alocação; a view Float64Array tem de ser recriada
  // DEPOIS de alocar, nunca guardada entre chamadas (buffer destacado = zeros silenciosos).
  function enviar(arr) {
    const p = w.qm_alocar(arr.length);
    new Float64Array(w.memory.buffer, p, arr.length).set(arr);
    return p;
  }
  function receber(p, n) {
    return Array.from(new Float64Array(w.memory.buffer, p, n));
  }

  function calcHurst(w, dados, ativo, janela, lambda) {
    if (!w || !dados) return null;
    const t0 = performance.now();
    const r = dados.retornos[ativo], n = r.length;
    const pr = enviar(r), ps = w.qm_alocar(n), pv = w.qm_alocar(n);
    w.qm_hurst_movel(pr, n, janela, ps);
    w.qm_ewma_vol(pr, n, lambda, pv);
    const h = receber(ps, n), v = receber(pv, n).map((x) => x * Math.sqrt(252) * 100);
    const hg = w.qm_hurst_rs(pr, n);
    [pr, ps, pv].forEach((p) => w.qm_liberar(p, n));
    tHurst = performance.now() - t0;
    return { h, v, hg };
  }

  function calcOu(w, previsao, meiaVida, trajetorias) {
    if (!w) return null;
    const t0 = performance.now();
    const grade = Array.from({ length: 12 }, (_, i) => 0.5 + i * (9.5 / 11));
    const pp = enviar(grade), ps = enviar(grade), po = w.qm_alocar(144);
    w.qm_ou_sharpe_malha(previsao, meiaVida, 1.0, pp, 12, ps, 12, trajetorias, 100, 42, po);
    const m = receber(po, 144);
    w.qm_liberar(pp, 12); w.qm_liberar(ps, 12); w.qm_liberar(po, 144);
    let best = 0;
    m.forEach((v, i) => { if (v > m[best]) best = i; });
    tOu = performance.now() - t0;
    return { m, grade, best, max: Math.max(...m.map(Math.abs)) };
  }

  function calcAg(w, dados, pop, geracoes, penal, semente) {
    if (!w || !dados) return null;
    const t0 = performance.now();
    const n = dados.ativos.length, T = dados.datas.length;
    const flat = new Array(T * n);
    for (let t = 0; t < T; t++) for (let j = 0; j < n; j++) flat[t * n + j] = dados.retornos[j][t];
    const pr = enviar(flat), pw = w.qm_alocar(n), ph = w.qm_alocar(geracoes), pm = w.qm_alocar(8);
    w.qm_ag_carteira(pr, T, n, pop, geracoes, penal, semente, pw, ph);
    const pesos = receber(pw, n), hist = receber(ph, geracoes);
    // compara com pesos iguais (mesmo kernel de métricas)
    const pe = enviar([...pesos, ...new Array(n).fill(1 / n)]);
    w.qm_metricas_carteiras(pr, T, n, pe, 2, pm);
    const met = receber(pm, 8);
    [[pr, T * n], [pw, n], [ph, geracoes], [pm, 8], [pe, 2 * n]].forEach(([p, k]) => w.qm_liberar(p, k));
    tAg = performance.now() - t0;
    return { pesos, hist, ag: met.slice(0, 4), igual: met.slice(4, 8) };
  }

  $: hurst = calcHurst(w, dados, ativo, janela, lambda);
  $: ou = calcOu(w, previsao, meiaVida, trajetorias);
  let rodarAg = 0;
  $: ag = rodarAg >= 0 ? calcAg(w, dados, pop, geracoes, penal, semente) : null;

  // desenho SVG simples (linhas com 2px, grade recessiva)
  function caminho(v, larg, alt, min, max) {
    const ok = v.map((y, i) => [i, y]).filter(([, y]) => Number.isFinite(y));
    if (!ok.length) return '';
    const n = v.length;
    return ok.map(([i, y], k) => `${k ? 'L' : 'M'}${(i / (n - 1)) * larg},${alt - ((y - min) / (max - min || 1)) * alt}`).join('');
  }
  const cor = (v, m) => {
    const a = Math.min(Math.abs(v) / (m || 1), 1);
    return v >= 0 ? `rgba(42,120,214,${0.12 + 0.88 * a})` : `rgba(227,73,72,${0.12 + 0.88 * a})`;
  };
</script>

<div class="lab">
  {#if erro}
    <p class="erro">{erro}</p>
  {:else if !w || !dados}
    <p>Carregando o motor WebAssembly e os dados…</p>
  {:else}
    <section>
      <h3>1 · Memória longa e volatilidade de um ativo</h3>
      <div class="controles">
        <label>Ativo
          <select bind:value={ativo}>
            {#each dados.nomes as n, i}<option value={i}>{n}</option>{/each}
          </select>
        </label>
        <label>Janela do Hurst: {janela} pregões
          <input type="range" min="100" max="500" step="10" bind:value={janela} /></label>
        <label>λ do EWMA: {fmt(lambda, 2)}
          <input type="range" min="0.80" max="0.99" step="0.01" bind:value={lambda} /></label>
      </div>
      {#if hurst}
        <p class="nota">H de R/S na série inteira: <b>{fmt(hurst.hg, 3)}</b> · calculado em {fmt(tHurst, 1)} ms no seu navegador.
          Lembre: em amostra finita, uma série sem memória já dá H ≈ 0,55.</p>
        <svg viewBox="0 0 800 160" class="graf" role="img" aria-label="Hurst móvel">
          <line x1="0" x2="800" y1="80" y2="80" class="grade" />
          <path d={caminho(hurst.h, 800, 160, 0.3, 0.8)} class="s1" />
        </svg>
        <p class="eixo">Hurst móvel (faixa 0,30–0,80; linha = 0,55)</p>
        <svg viewBox="0 0 800 140" class="graf" role="img" aria-label="Volatilidade EWMA">
          <path d={caminho(hurst.v, 800, 140, 0, Math.max(...hurst.v.filter(Number.isFinite)))} class="s2" />
        </svg>
        <p class="eixo">Volatilidade EWMA anualizada (%) · {dados.datas[0]} a {dados.datas[dados.datas.length - 1]}</p>
      {/if}
    </section>

    <section>
      <h3>2 · Regra ótima de saída (Monte Carlo Ornstein-Uhlenbeck)</h3>
      <div class="controles">
        <label>Previsão (σ): {fmt(previsao, 1)}
          <input type="range" min="-5" max="5" step="0.5" bind:value={previsao} /></label>
        <label>Meia-vida: {meiaVida} pregões
          <input type="range" min="1" max="50" step="1" bind:value={meiaVida} /></label>
        <label>Trajetórias por célula: {trajetorias}
          <input type="range" min="200" max="4000" step="100" bind:value={trajetorias} /></label>
      </div>
      {#if ou}
        <p class="nota">{(144 * trajetorias).toLocaleString('pt-BR')} trajetórias em {fmt(tOu, 0)} ms. Melhor regra:
          alvo <b>{fmt(ou.grade[Math.floor(ou.best / 12)], 1)}σ</b>, stop <b>{fmt(ou.grade[ou.best % 12], 1)}σ</b>
          (Sharpe {fmt(ou.m[ou.best], 2)}).</p>
        <svg viewBox="0 0 480 480" class="mapa" role="img" aria-label="Malha de Sharpe">
          {#each ou.m as v, i}
            <rect x={(i % 12) * 40} y={440 - Math.floor(i / 12) * 40} width="38" height="38" rx="3" fill={cor(v, ou.max)}>
              <title>alvo {fmt(ou.grade[Math.floor(i / 12)], 1)}σ · stop {fmt(ou.grade[i % 12], 1)}σ · Sharpe {fmt(v, 2)}</title>
            </rect>
          {/each}
        </svg>
        <p class="eixo">linhas: alvo de lucro 0,5σ (baixo) → 10σ (alto) · colunas: stop 0,5σ → 10σ · azul = Sharpe positivo</p>
      {/if}
    </section>

    <section>
      <h3>3 · Algoritmo genético de carteira (10 ativos, 2015–2026)</h3>
      <div class="controles">
        <label>População: {pop}<input type="range" min="20" max="200" step="10" bind:value={pop} /></label>
        <label>Gerações: {geracoes}<input type="range" min="5" max="120" step="5" bind:value={geracoes} /></label>
        <label>Penalidade de drawdown: {fmt(penal, 1)}<input type="range" min="0" max="3" step="0.1" bind:value={penal} /></label>
        <label>Semente<input type="number" min="1" max="99999" bind:value={semente} /></label>
      </div>
      {#if ag}
        <p class="nota">Evoluído em {fmt(tAg, 0)} ms. Sharpe <b>{fmt(ag.ag[2])}</b> e drawdown {fmt(ag.ag[3] * 100, 1)}%
          contra pesos iguais: Sharpe {fmt(ag.igual[2])} e drawdown {fmt(ag.igual[3] * 100, 1)}% —
          <i>dentro da amostra</i>; troque a semente e veja quanto do "ótimo" muda.</p>
        <div class="pesos">
          {#each ag.pesos as p, i}
            <div class="linha"><span>{dados.nomes[i]}</span>
              <div class="barra" style="width:{p * 100 * 3}px"></div><span class="v">{fmt(p * 100, 1)}%</span></div>
          {/each}
        </div>
        <svg viewBox="0 0 800 120" class="graf" role="img" aria-label="Evolução da aptidão">
          <path d={caminho(ag.hist, 800, 120, Math.min(...ag.hist), Math.max(...ag.hist))} class="s1" />
        </svg>
        <p class="eixo">melhor aptidão por geração</p>
      {/if}
    </section>
  {/if}
</div>

<style>
  .lab { --s1: #2a78d6; --s2: #eb6834; --grade: #e6e5e1; --txt2: #52514e; }
  @media (prefers-color-scheme: dark) {
    :global(:root:where(:not([data-theme="light"]))) .lab { --s1: #3987e5; --s2: #d95926; --grade: #383835; --txt2: #c3c2b7; }
  }
  :global(:root[data-theme="dark"]) .lab { --s1: #3987e5; --s2: #d95926; --grade: #383835; --txt2: #c3c2b7; }
  section { margin: 1.5rem 0 2.5rem; }
  .controles { display: flex; flex-wrap: wrap; gap: 1rem 2rem; margin: 0.5rem 0 1rem; }
  label { display: flex; flex-direction: column; font-size: 0.9rem; min-width: 200px; }
  .graf { width: 100%; height: auto; overflow: visible; }
  .mapa { width: min(100%, 420px); height: auto; }
  path.s1 { fill: none; stroke: var(--s1); stroke-width: 2; }
  path.s2 { fill: none; stroke: var(--s2); stroke-width: 2; }
  line.grade { stroke: var(--grade); stroke-dasharray: 4 4; }
  .nota { font-size: 0.95rem; }
  .eixo { font-size: 0.8rem; color: var(--txt2); margin-top: 0.2rem; }
  .pesos { display: grid; gap: 4px; margin: 0.5rem 0 1rem; }
  .linha { display: grid; grid-template-columns: 180px auto 1fr; align-items: center; gap: 8px; font-size: 0.85rem; }
  .barra { height: 12px; background: var(--s1); border-radius: 0 4px 4px 0; max-width: 100%; }
  .v { color: var(--txt2); }
  .erro { color: #d03b3b; }
  @media (max-width: 640px) { .linha { grid-template-columns: 120px auto 1fr; } }
</style>
