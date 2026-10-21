// quant_models_2026
// Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
// E-mail: profbruanbima@gmail.com
//
// Kernels numéricos em F# — gêmeos de quant/kernels.py e de rust/.../src/lib.rs.
// Estilo deliberadamente imperativo nos laços quentes: a mesma ordem de operações de ponto
// flutuante dos outros dois motores é o que permite comparar resultados com tolerância de 1e-9.
module QuantModels2026.Kernels

open System

// ─────────────────────────────────────────────────────────────────────────────
// Retornos, médias e risco
// ─────────────────────────────────────────────────────────────────────────────

let logRetornos (p: float[]) = Array.init (max (p.Length - 1) 0) (fun i -> log (p.[i + 1] / p.[i]))

let ema (x: float[]) (n: float) =
    let a = 2.0 / (n + 1.0)
    let out = Array.zeroCreate x.Length
    if x.Length > 0 then
        out.[0] <- x.[0]
        for i in 1 .. x.Length - 1 do
            out.[i] <- a * x.[i] + (1.0 - a) * out.[i - 1]
    out

let ewmaVol (r: float[]) (lam: float) =
    let n = r.Length
    let s2 = Array.zeroCreate n
    let mutable v = 0.0
    for x in r do v <- v + x * x
    s2.[0] <- v / float n
    for i in 1 .. n - 1 do
        s2.[i] <- lam * s2.[i - 1] + (1.0 - lam) * r.[i - 1] * r.[i - 1]
    Array.map sqrt s2

let garch11Filtro (r: float[]) omega alpha beta =
    let n = r.Length
    let s2 = Array.zeroCreate n
    let mutable v = 0.0
    for x in r do v <- v + x * x
    s2.[0] <- v / float n
    let mutable nll = 0.0
    for i in 0 .. n - 1 do
        if i > 0 then s2.[i] <- omega + alpha * r.[i - 1] * r.[i - 1] + beta * s2.[i - 1]
        nll <- nll + 0.5 * (log (2.0 * Math.PI) + log s2.[i] + r.[i] * r.[i] / s2.[i])
    s2, nll

let drawdownMaximo (curva: float[]) =
    let mutable pico = curva.[0]
    let mutable mdd = 0.0
    for v in curva do
        if v > pico then pico <- v
        let dd = v / pico - 1.0
        if dd < mdd then mdd <- dd
    mdd

let sharpeAnual (r: float[]) (periodos: float) =
    let n = r.Length
    if n < 2 then 0.0
    else
        let mutable m = 0.0
        for x in r do m <- m + x
        m <- m / float n
        let mutable v = 0.0
        for x in r do v <- v + (x - m) * (x - m)
        v <- v / float (n - 1)
        if v <= 0.0 then 0.0 else m / sqrt v * sqrt periodos

/// r: T×N (linha a linha), w: P×N. Saída P×4: retorno, vol, Sharpe, drawdown.
let metricasCarteiras (r: float[]) (t: int) (n: int) (w: float[]) (p: int) (periodos: float) =
    let out = Array.zeroCreate (p * 4)
    for k in 0 .. p - 1 do
        let mutable curva = 1.0
        let mutable pico = 1.0
        let mutable mdd = 0.0
        let mutable s = 0.0
        let mutable s2 = 0.0
        for ti in 0 .. t - 1 do
            let mutable rp = 0.0
            for j in 0 .. n - 1 do
                rp <- rp + w.[k * n + j] * (exp r.[ti * n + j] - 1.0)
            s <- s + rp
            s2 <- s2 + rp * rp
            curva <- curva * (1.0 + rp)
            if curva > pico then pico <- curva
            let dd = curva / pico - 1.0
            if dd < mdd then mdd <- dd
        let m = s / float t
        let v = s2 / float t - m * m
        let vol = sqrt (max v 1e-18) * sqrt periodos
        let ret = m * periodos
        out.[k * 4] <- ret
        out.[k * 4 + 1] <- vol
        out.[k * 4 + 2] <- ret / vol
        out.[k * 4 + 3] <- mdd
    out

// ─────────────────────────────────────────────────────────────────────────────
// Indicadores técnicos
// ─────────────────────────────────────────────────────────────────────────────

let rsi (p: float[]) (n: int) =
    let m = p.Length
    let out = Array.create m nan
    if m > n then
        let mutable g = 0.0
        let mutable q = 0.0
        for i in 1 .. n do
            let d = p.[i] - p.[i - 1]
            if d > 0.0 then g <- g + d else q <- q - d
        g <- g / float n
        q <- q / float n
        out.[n] <- if q = 0.0 then 100.0 else 100.0 - 100.0 / (1.0 + g / q)
        for i in n + 1 .. m - 1 do
            let d = p.[i] - p.[i - 1]
            let up = if d > 0.0 then d else 0.0
            let dn = if d < 0.0 then -d else 0.0
            g <- (g * float (n - 1) + up) / float n
            q <- (q * float (n - 1) + dn) / float n
            out.[i] <- if q = 0.0 then 100.0 else 100.0 - 100.0 / (1.0 + g / q)
    out

let psar (h: float[]) (l: float[]) passo maximo =
    let n = h.Length
    let sar = Array.zeroCreate n
    let tend = Array.zeroCreate n
    let mutable alta = true
    let mutable af = passo
    let mutable ep = h.[0]
    sar.[0] <- l.[0]
    tend.[0] <- 1.0
    for i in 1 .. n - 1 do
        let mutable s = sar.[i - 1] + af * (ep - sar.[i - 1])
        if alta then
            let l2 = if i >= 2 then l.[i - 2] else l.[i - 1]
            s <- min (min s l.[i - 1]) l2
            if l.[i] < s then
                alta <- false; s <- ep; ep <- l.[i]; af <- passo
            elif h.[i] > ep then
                ep <- h.[i]; af <- min (af + passo) maximo
        else
            let h2 = if i >= 2 then h.[i - 2] else h.[i - 1]
            s <- max (max s h.[i - 1]) h2
            if h.[i] > s then
                alta <- true; s <- ep; ep <- h.[i]; af <- passo
            elif l.[i] < ep then
                ep <- l.[i]; af <- min (af + passo) maximo
        sar.[i] <- s
        tend.[i] <- if alta then 1.0 else -1.0
    sar, tend

// ─────────────────────────────────────────────────────────────────────────────
// Memória longa e sinais
// ─────────────────────────────────────────────────────────────────────────────

let hurstRs (x: float[]) =
    let bigN = x.Length
    let ns = ResizeArray<int>()
    let mutable n = 8
    while n <= bigN / 2 do
        ns.Add n
        n <- n * 2
    if ns.Count < 2 then nan
    else
        let lx = Array.zeroCreate ns.Count
        let ly = Array.zeroCreate ns.Count
        for k in 0 .. ns.Count - 1 do
            let n = ns.[k]
            let blocos = bigN / n
            let mutable acc = 0.0
            let mutable cnt = 0
            for b in 0 .. blocos - 1 do
                let mutable m = 0.0
                for i in b * n .. (b + 1) * n - 1 do m <- m + x.[i]
                m <- m / float n
                let mutable z = 0.0
                let mutable zmax = -1e300
                let mutable zmin = 1e300
                let mutable s2 = 0.0
                for i in b * n .. (b + 1) * n - 1 do
                    let v = x.[i]
                    z <- z + (v - m)
                    if z > zmax then zmax <- z
                    if z < zmin then zmin <- z
                    s2 <- s2 + (v - m) * (v - m)
                let s = sqrt (s2 / float n)
                if s > 0.0 then
                    acc <- acc + (zmax - zmin) / s
                    cnt <- cnt + 1
            lx.[k] <- log (float n)
            ly.[k] <- if cnt > 0 then log (acc / float cnt) else nan
        let mx = Array.average lx
        let my = Array.average ly
        let mutable num = 0.0
        let mutable den = 0.0
        for i in 0 .. lx.Length - 1 do
            num <- num + (lx.[i] - mx) * (ly.[i] - my)
            den <- den + (lx.[i] - mx) * (lx.[i] - mx)
        num / den

let hurstMovel (r: float[]) (janela: int) =
    let n = r.Length
    let out = Array.create n nan
    for i in janela .. n do
        out.[i - 1] <- hurstRs r.[i - janela .. i - 1]
    out

let haarDwt (x: float[]) (niveis: int) =
    let mutable a = Array.copy x
    let energia = Array.zeroCreate niveis
    let d1 = Array.zeroCreate x.Length
    let r2 = sqrt 2.0
    let mutable lv = 0
    let mutable continuar = true
    while continuar && lv < niveis do
        let m = a.Length / 2
        if m < 1 then continuar <- false
        else
            let na = Array.init m (fun i -> (a.[2 * i] + a.[2 * i + 1]) / r2)
            let nd = Array.init m (fun i -> (a.[2 * i] - a.[2 * i + 1]) / r2)
            let mutable e = 0.0
            for v in nd do e <- e + v * v
            energia.[lv] <- e
            if lv = 0 then
                for i in 0 .. m - 1 do
                    d1.[2 * i] <- nd.[i]
                    d1.[2 * i + 1] <- nd.[i]
            a <- na
            lv <- lv + 1
    a, energia, d1

// ─────────────────────────────────────────────────────────────────────────────
// Markov / HMM
// ─────────────────────────────────────────────────────────────────────────────

let matrizTransicao (estados: int[]) (k: int) =
    let p = Array.zeroCreate (k * k)
    for i in 1 .. estados.Length - 1 do
        p.[estados.[i - 1] * k + estados.[i]] <- p.[estados.[i - 1] * k + estados.[i]] + 1.0
    for i in 0 .. k - 1 do
        let mutable s = 0.0
        for j in 0 .. k - 1 do s <- s + p.[i * k + j]
        if s > 0.0 then
            for j in 0 .. k - 1 do p.[i * k + j] <- p.[i * k + j] / s
    p

let private gauss x m s = exp (-0.5 * ((x - m) / s) ** 2.0) / (s * sqrt (2.0 * Math.PI))

type Hmm = { Pi: float[]; A: float[]; Mu: float[]; Sd: float[]; Gamma: float[]; Ll: float }

let hmmGaussianoEm (x: float[]) (mu0: float[]) (sd0: float[]) (iters: int) (tol: float) =
    let tN = x.Length
    let k = mu0.Length
    let mu = Array.copy mu0
    let sd = Array.copy sd0
    let a = Array.create (k * k) (0.02 / float (k - 1))
    for i in 0 .. k - 1 do a.[i * k + i] <- 0.98
    let pi = Array.create k (1.0 / float k)
    let alpha = Array.zeroCreate (tN * k)
    let beta = Array.zeroCreate (tN * k)
    let c = Array.zeroCreate tN
    let b = Array.zeroCreate (tN * k)
    let gamma = Array.zeroCreate (tN * k)
    let mutable llAnt = -1e300
    let mutable ll = 0.0
    let mutable it = 0
    let mutable parar = false
    while not parar && it < iters do
        for t in 0 .. tN - 1 do
            for j in 0 .. k - 1 do
                b.[t * k + j] <- max (gauss x.[t] mu.[j] sd.[j]) 1e-300
        let mutable s = 0.0
        for j in 0 .. k - 1 do
            alpha.[j] <- pi.[j] * b.[j]
            s <- s + alpha.[j]
        c.[0] <- s
        for j in 0 .. k - 1 do alpha.[j] <- alpha.[j] / s
        for t in 1 .. tN - 1 do
            let mutable s = 0.0
            for j in 0 .. k - 1 do
                let mutable acc = 0.0
                for i in 0 .. k - 1 do acc <- acc + alpha.[(t - 1) * k + i] * a.[i * k + j]
                alpha.[t * k + j] <- acc * b.[t * k + j]
                s <- s + alpha.[t * k + j]
            c.[t] <- s
            for j in 0 .. k - 1 do alpha.[t * k + j] <- alpha.[t * k + j] / s
        for j in 0 .. k - 1 do beta.[(tN - 1) * k + j] <- 1.0
        for t in tN - 2 .. -1 .. 0 do
            for i in 0 .. k - 1 do
                let mutable acc = 0.0
                for j in 0 .. k - 1 do acc <- acc + a.[i * k + j] * b.[(t + 1) * k + j] * beta.[(t + 1) * k + j]
                beta.[t * k + i] <- acc / c.[t + 1]
        ll <- 0.0
        for t in 0 .. tN - 1 do ll <- ll + log c.[t]
        for t in 0 .. tN - 1 do
            let mutable s = 0.0
            for j in 0 .. k - 1 do
                gamma.[t * k + j] <- alpha.[t * k + j] * beta.[t * k + j]
                s <- s + gamma.[t * k + j]
            for j in 0 .. k - 1 do gamma.[t * k + j] <- gamma.[t * k + j] / s
        let xi = Array.zeroCreate (k * k)
        for t in 0 .. tN - 2 do
            for i in 0 .. k - 1 do
                for j in 0 .. k - 1 do
                    xi.[i * k + j] <- xi.[i * k + j]
                                      + alpha.[t * k + i] * a.[i * k + j] * b.[(t + 1) * k + j]
                                        * beta.[(t + 1) * k + j] / c.[t + 1]
        for j in 0 .. k - 1 do pi.[j] <- gamma.[j]
        for i in 0 .. k - 1 do
            let mutable s = 0.0
            for j in 0 .. k - 1 do s <- s + xi.[i * k + j]
            for j in 0 .. k - 1 do a.[i * k + j] <- if s > 0.0 then xi.[i * k + j] / s else 1.0 / float k
        for j in 0 .. k - 1 do
            let mutable w = 0.0
            let mutable m = 0.0
            for t in 0 .. tN - 1 do
                w <- w + gamma.[t * k + j]
                m <- m + gamma.[t * k + j] * x.[t]
            m <- m / w
            let mutable v = 0.0
            for t in 0 .. tN - 1 do v <- v + gamma.[t * k + j] * (x.[t] - m) ** 2.0
            mu.[j] <- m
            sd.[j] <- max (sqrt (v / w)) 1e-6
        if abs (ll - llAnt) < tol then parar <- true
        else llAnt <- ll
        it <- it + 1
    { Pi = pi; A = a; Mu = mu; Sd = sd; Gamma = gamma; Ll = ll }

// ─────────────────────────────────────────────────────────────────────────────
// Monte Carlo O-U — xorshift64* idêntico ao numba e ao Rust
// ─────────────────────────────────────────────────────────────────────────────

/// Gerador xorshift64* — estado encapsulado (closures F# não podem capturar byref).
type Gerador(semente: uint64) =
    let mutable estado = semente
    member _.Proximo() =
        estado <- estado ^^^ (estado >>> 12)
        estado <- estado ^^^ (estado <<< 25)
        estado <- estado ^^^ (estado >>> 27)
        estado * 2685821657736338717UL
    member g.Uniforme() = float (g.Proximo() >>> 11) * (1.0 / 9007199254740992.0)
    member g.Normal() =
        let a = g.Proximo()
        let b = g.Proximo()
        let u1 = float ((a >>> 11) + 1UL) * (1.0 / 9007199254740993.0)
        let u2 = float (b >>> 11) * (1.0 / 9007199254740992.0)
        sqrt (-2.0 * log u1) * cos (2.0 * Math.PI * u2)

let ouSharpeMalha previsao meiaVida sigma (pts: float[]) (sls: float[]) (nIter: int) (maxHp: int) (semente: uint64) =
    let phi = Math.Pow(2.0, -1.0 / meiaVida)
    let out = Array.zeroCreate (pts.Length * sls.Length)
    let g = Gerador(semente)
    for a in 0 .. pts.Length - 1 do
        for b in 0 .. sls.Length - 1 do
            let mutable s = 0.0
            let mutable s2 = 0.0
            for _ in 1 .. nIter do
                let mutable p = 0.0
                let mutable h = 0
                let mutable sair = false
                while not sair && h < maxHp do
                    let z = g.Normal()
                    p <- (1.0 - phi) * previsao + phi * p + sigma * z
                    if p > pts.[a] || p < -sls.[b] then sair <- true
                    h <- h + 1
                s <- s + p
                s2 <- s2 + p * p
            let m = s / float nIter
            let v = s2 / float nIter - m * m
            out.[a * sls.Length + b] <- if v > 0.0 then m / sqrt v else 0.0
    out

// ─────────────────────────────────────────────────────────────────────────────
// Programação genética — máquina de pilha pós-fixa
// ─────────────────────────────────────────────────────────────────────────────

let avaliarPosfixa (codigo: int64[]) (consts: float[]) (x: float[]) (tN: int) (nvars: int) =
    let pilha = Collections.Generic.List<float[]>()
    for i in 0 .. codigo.Length - 1 do
        let c = codigo.[i]
        if c < 100L then pilha.Add(Array.init tN (fun t -> x.[t * nvars + int c]))
        elif c = 100L then pilha.Add(Array.create tN consts.[i])
        else
            let op = c - 200L
            if op >= 4L && op <> 6L then
                let a = pilha.[pilha.Count - 1]
                for t in 0 .. tN - 1 do
                    a.[t] <- (match op with
                              | 4L -> sin a.[t]
                              | 5L -> cos a.[t]
                              | _ -> -a.[t])
            else
                let b = pilha.[pilha.Count - 1]
                pilha.RemoveAt(pilha.Count - 1)
                let a = pilha.[pilha.Count - 1]
                for t in 0 .. tN - 1 do
                    a.[t] <- (match op with
                              | 0L -> a.[t] + b.[t]
                              | 1L -> a.[t] - b.[t]
                              | 2L -> a.[t] * b.[t]
                              | 3L -> if abs b.[t] > 1e-12 then a.[t] / b.[t] else 1.0
                              | _ -> max a.[t] b.[t])
    pilha.[0]

// ─────────────────────────────────────────────────────────────────────────────
// Diversos
// ─────────────────────────────────────────────────────────────────────────────

let primeirosDigitos (x: float[]) =
    let cont = Array.zeroCreate 9
    for v0 in x do
        let mutable v = abs v0
        if v > 0.0 && Double.IsFinite v then
            while v >= 10.0 do v <- v / 10.0
            while v < 1.0 do v <- v * 10.0
            let d = int v
            if d >= 1 && d <= 9 then cont.[d - 1] <- cont.[d - 1] + 1.0
    cont

let kmeans1d (x: float[]) (k: int) (iters: int) =
    let xs = Array.sort x
    let n = xs.Length
    let c = Array.init k (fun i -> xs.[int ((float i + 0.5) * float n / float k)])
    let rot = Array.zeroCreate x.Length
    let mutable it = 0
    let mutable parar = false
    while not parar && it < iters do
        for i in 0 .. x.Length - 1 do
            let mutable best = 0
            let mutable bd = 1e300
            for j in 0 .. k - 1 do
                let d = abs (x.[i] - c.[j])
                if d < bd then
                    bd <- d
                    best <- j
            rot.[i] <- best
        let mutable mudou = false
        for j in 0 .. k - 1 do
            let mutable s = 0.0
            let mutable cnt = 0
            for i in 0 .. x.Length - 1 do
                if rot.[i] = j then
                    s <- s + x.[i]
                    cnt <- cnt + 1
            if cnt > 0 then
                let nv = s / float cnt
                if abs (nv - c.[j]) > 1e-12 then mudou <- true
                c.[j] <- nv
        if not mudou then parar <- true
        it <- it + 1
    c, rot

// ─────────────────────────────────────────────────────────────────────────────
// Algoritmo genético de carteira — mesma sequência pseudoaleatória do Rust
// ─────────────────────────────────────────────────────────────────────────────

let agCarteira (r: float[]) (t: int) (n: int) (pop: int) (geracoes: int) (elite: int) (taxaMut: float)
               (penalDd: float) (semente: uint64) =
    let g = Gerador(max semente 1UL)
    let dirichlet () =
        let w = Array.zeroCreate n
        for j in 0 .. n - 1 do w.[j] <- -(log (1.0 - g.Uniforme()))
        let s = Array.sum w
        Array.map (fun v -> v / s) w
    let mutable p = Array.zeroCreate (pop * n)
    for k in 0 .. pop - 1 do
        let w = dirichlet ()
        Array.blit w 0 p (k * n) n
    let hist = ResizeArray<float>()
    let aptidao (p: float[]) =
        let m = metricasCarteiras r t n p pop 252.0
        Array.init pop (fun k -> m.[k * 4 + 2] + penalDd * m.[k * 4 + 3])
    for _ in 1 .. geracoes do
        let apt = aptidao p
        let ordem = Array.init pop id
                    |> Array.sortWith (fun a b -> let c = compare apt.[b] apt.[a] in if c <> 0 then c else compare a b)
        hist.Add apt.[ordem.[0]]
        let minimo = Array.min apt
        let pesos = apt |> Array.map (fun a -> a - minimo + 1e-9)
        let total = Array.sum pesos
        let roleta () =
            let alvo = g.Uniforme() * total
            let mutable acc = 0.0
            let mutable i = 0
            let mutable achou = -1
            while achou < 0 && i < pop do
                acc <- acc + pesos.[i]
                if acc >= alvo then achou <- i
                i <- i + 1
            if achou < 0 then pop - 1 else achou
        let nova = ResizeArray<float>(pop * n)
        for e in 0 .. elite - 1 do
            let i = ordem.[e]
            for j in 0 .. n - 1 do nova.Add p.[i * n + j]
        while nova.Count < pop * n do
            let a = roleta ()
            let b = roleta ()
            let corte = 1 + int (g.Uniforme() * (float n - 1.0))
            let filho = Array.init n (fun j -> if j < corte then p.[a * n + j] else p.[b * n + j])
            if g.Uniforme() < taxaMut then
                let j = int (g.Uniforme() * float n) % n
                filho.[j] <- max (filho.[j] + 0.15 * g.Normal()) 0.0
            let s = Array.sum filho
            if s > 0.0 then
                for j in 0 .. n - 1 do filho.[j] <- filho.[j] / s
            else
                for j in 0 .. n - 1 do filho.[j] <- 1.0 / float n
            nova.AddRange filho
        p <- nova.ToArray()
    let apt = aptidao p
    let mutable melhor = 0
    for k in 1 .. pop - 1 do
        if apt.[k] > apt.[melhor] then melhor <- k
    p.[melhor * n .. (melhor + 1) * n - 1], hist.ToArray()
