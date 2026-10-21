#!/usr/bin/env python3
# quant_models_2026 — 4 logs de execução (D28 · I17)
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Os 4 logs de criação (I17 · D28) para QUALQUER script Python do portfólio, em duas linhas.

Formato único: este módulo não reimplementa nada — delega a `registro_execucao.sh` (mesmo
diretório), então STDOUT, STDERR, janela e tokenização saem idênticos aos da infra.

    from registro4logs import sob_registro
    def main(): ...
    if __name__ == "__main__":
        sob_registro("fundar-meu_projeto", "logs/criacao", fase="preparo", nome="fundar projeto")
        sys.exit(main())

`sob_registro` reexecuta o próprio script como UM passo do registro (iniciar → passo →
finalizar) e encerra com o código dele. Dentro da reexecução (variável REGISTRO_4LOGS_ATIVO)
não faz nada — o script roda normalmente. Para vários passos, use a classe `Registro`.
Desligar (ex.: testes): REGISTRO_4LOGS=0.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPT = AQUI / "registro_execucao.sh"
MARCA = "REGISTRO_4LOGS_ATIVO"


class Registro:
    def __init__(self, ambiente: str, dir_logs: str | Path):
        r = subprocess.run(["bash", str(SCRIPT), "iniciar", "--ambiente", ambiente, "--dir", str(dir_logs)],
                           capture_output=True, text=True, check=True)
        # shlex entende as aspas e o escape '\'' exatamente como o bash — split("'") quebrava
        # com apóstrofo no caminho (o passo não rodava e nada avisava).
        linha = next(l for l in r.stdout.splitlines() if l.startswith("export REGISTRO_DIR="))
        self.dir = shlex.split(linha)[1].split("=", 1)[1]

    def passo(self, fase: str, nome: str, cmd: list[str], env: dict | None = None) -> int:
        return subprocess.run(["bash", str(SCRIPT), "passo", "--dir", self.dir, "--fase", fase, "--nome", nome, "--"]
                              + cmd, env=env).returncode

    def finalizar(self) -> None:
        subprocess.run(["bash", str(SCRIPT), "finalizar", "--dir", self.dir])


def sob_registro(ambiente: str, dir_logs: str | Path, fase: str = "preparo", nome: str | None = None) -> None:
    if os.environ.get(MARCA) == "1" or os.environ.get("REGISTRO_4LOGS") == "0":
        return
    if not SCRIPT.is_file():
        print(f"⚠️  registro_execucao.sh ausente em {AQUI} — seguindo SEM os 4 logs", file=sys.stderr)
        return
    reg = Registro(ambiente, dir_logs)
    rc = reg.passo(fase, nome or ambiente, [sys.executable, str(Path(sys.argv[0]).resolve()), *sys.argv[1:]],
                   env={**os.environ, MARCA: "1"})
    reg.finalizar()
    sys.exit(rc)
