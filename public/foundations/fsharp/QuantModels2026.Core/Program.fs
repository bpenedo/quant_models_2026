// quant_models_2026
// Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
// E-mail: profbruanbima@gmail.com
//
// CLI de verificação cruzada — MESMO protocolo do motor Rust (src/bin/qm_core.rs):
//   qm_core_fs <kernel> <entrada.txt> [parâmetros...]
module QuantModels2026.Program

open System
open System.Globalization
open System.IO
open System.Text
open QuantModels2026.Kernels

let inv = CultureInfo.InvariantCulture

let lerVetor (caminho: string) =
    File.ReadAllLines caminho
    |> Array.filter (fun l -> l.Trim() <> "")
    |> Array.map (fun l -> Double.Parse(l.Trim(), inv))

let lerMatriz caminho =
    let v = lerVetor caminho
    v.[2..], int v.[0], int v.[1]

let imprimir (v: float seq) =
    let sb = StringBuilder()
    for x in v do
        if Double.IsNaN x then sb.Append("nan\n") |> ignore
        else sb.Append(x.ToString("E16", inv)).Append('\n') |> ignore
    Console.Out.Write(sb.ToString())

let num (a: string[]) i = Double.Parse(a.[i], inv)

[<EntryPoint>]
let main argv =
    if argv.Length < 2 then
        eprintfn "uso: qm_core_fs <kernel> <entrada.txt> [parâmetros...]"
        2
    else
        let k, f = argv.[0], argv.[1]
        match k with
        | "log_retornos" -> imprimir (logRetornos (lerVetor f)); 0
        | "ema" -> imprimir (ema (lerVetor f) (num argv 2)); 0
        | "ewma_vol" -> imprimir (ewmaVol (lerVetor f) (num argv 2)); 0
        | "garch11" ->
            let s2, nll = garch11Filtro (lerVetor f) (num argv 2) (num argv 3) (num argv 4)
            imprimir (Seq.append [ nll ] s2); 0
        | "drawdown" -> imprimir [ drawdownMaximo (lerVetor f) ]; 0
        | "sharpe" -> imprimir [ sharpeAnual (lerVetor f) (num argv 2) ]; 0
        | "metricas" ->
            let r, t, n = lerMatriz f
            let w, p, _ = lerMatriz argv.[2]
            imprimir (metricasCarteiras r t n w p 252.0); 0
        | "rsi" -> imprimir (rsi (lerVetor f) (int (num argv 2))); 0
        | "psar" ->
            let m, n, _ = lerMatriz f
            let h = Array.init n (fun i -> m.[i * 2])
            let l = Array.init n (fun i -> m.[i * 2 + 1])
            let s, t = psar h l (num argv 2) (num argv 3)
            imprimir (Seq.append s t); 0
        | "hurst_rs" -> imprimir [ hurstRs (lerVetor f) ]; 0
        | "hurst_movel" -> imprimir (hurstMovel (lerVetor f) (int (num argv 2))); 0
        | "haar_dwt" ->
            let ap, e, d1 = haarDwt (lerVetor f) (int (num argv 2))
            imprimir (Seq.concat [ e; ap; d1 ]); 0
        | "transicao" ->
            let e = lerVetor f |> Array.map int
            imprimir (matrizTransicao e (int (num argv 2))); 0
        | "hmm" ->
            let h = hmmGaussianoEm (lerVetor f) (lerVetor argv.[2]) (lerVetor argv.[3]) (int (num argv 4)) (num argv 5)
            imprimir (Seq.concat [ [| h.Ll |]; h.Mu; h.Sd; h.A; h.Pi ]); 0
        | "ou_malha" ->
            imprimir (ouSharpeMalha (num argv 3) (num argv 4) (num argv 5) (lerVetor f) (lerVetor argv.[2])
                          (int (num argv 6)) (int (num argv 7)) (uint64 (num argv 8))); 0
        | "posfixa" ->
            let x, t, nv = lerMatriz f
            let cod = lerVetor argv.[2] |> Array.map int64
            imprimir (avaliarPosfixa cod (lerVetor argv.[3]) x t nv); 0
        | "benford" -> imprimir (primeirosDigitos (lerVetor f)); 0
        | "kmeans1d" ->
            let c, rot = kmeans1d (lerVetor f) (int (num argv 2)) (int (num argv 3))
            imprimir (Seq.append c (rot |> Seq.map float)); 0
        | "ag_carteira" ->
            let r, t, n = lerMatriz f
            let w, h = agCarteira r t n (int (num argv 2)) (int (num argv 3)) 4 0.3 (num argv 4) (uint64 (num argv 5))
            imprimir (Seq.append w h); 0
        | _ ->
            eprintfn "❌ kernel desconhecido: %s" k
            2
