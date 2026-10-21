---
title: Laboratório no navegador (WebAssembly)
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

Os controles abaixo chamam o **mesmo motor Rust** que passa nos testes de concordância contra Python/numba e F#,
compilado para WebAssembly (63 KB). Nada é enviado a servidor: o cálculo roda na sua máquina, em milissegundos.

<!-- Toda página precisa de ao menos uma consulta: sem ela o build não gera all-queries.json e o
     navegador registra um 404 — ver bugs.md. -->
<LaboratorioWasm/>

```sql bench_lab
select carga, rust_s, numba_s, fsharp_s from quant.bench_motores
```

O mesmo motor, medido fora do navegador (segundos, com a partida do processo descontada):

<DataTable data={bench_lab}>
  <Column id=carga title="Carga"/><Column id=rust_s title="Rust (s)" fmt=num3/>
  <Column id=numba_s title="numba (s)" fmt=num3/><Column id=fsharp_s title="F# (s)" fmt=num3/>
</DataTable>

[← Voltar à vitrine](/)
