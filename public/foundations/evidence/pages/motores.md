---
title: Três motores, um resultado
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

Cada kernel numérico existe em **três linguagens** — Python/numba, Rust e F# — e o teste de concordância
exige que os três devolvam o mesmo número, inclusive no Monte Carlo (o gerador xorshift64* é idêntico nos três).
Dois motores independentes que concordam provam que a **matemática** está certa, não só o código.

```sql bench_motores
select * from quant.bench_motores
```

<DataTable data={bench_motores}>
  <Column id=carga title="Carga"/><Column id=numba_s title="numba (s)" fmt=num3/><Column id=rust_s title="Rust (s)" fmt=num3/>
  <Column id=fsharp_s title="F# (s)" fmt=num3/><Column id=python_puro_s title="Python puro (s)" fmt=num2/>
  <Column id=ganho_numba title="Ganho do numba" fmt=num0/>
</DataTable>

<BarChart data={bench_motores} x=carga y={["numba_s","rust_s","fsharp_s"]} type=grouped swapXY=true title="Tempo por motor (s)"/>

Tempos de Rust e F# **descontam a partida do processo** (medida à parte). No F#, o tempo inclui a compilação JIT do .NET.
Medido com `bench_motores.py`; histórico em `bench/historico.jsonl`.
