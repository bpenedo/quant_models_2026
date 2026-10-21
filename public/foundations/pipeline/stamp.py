#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Carimbo de autoria em 20+ linguagens — FONTE ÚNICA DE VERDADE (D18).

Os valores vêm de `projeto.toml`. Corrigir a autoria é editar UM arquivo; todo o
resto consome daqui. Sem isso, uma correção de e-mail vira varredura manual em
dezenas de arquivos — e o que passa despercebido fica errado para sempre.

Uso:
  python3 stamp.py python|bash|rust|fsharp|sql|md|...     imprime o carimbo
  python3 stamp.py --todos                                 todas as variantes
  python3 stamp.py --aplicar <arquivo>                     insere se faltar
  python3 stamp.py --verificar <diretório>                 lista arquivos SEM carimbo
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ENCODING = "utf-8"


def raiz_projeto(inicio: Path | None = None) -> Path:
    p = (inicio or Path(__file__)).resolve()
    for pai in [p, *p.parents]:
        if (pai / "projeto.toml").exists():
            return pai
    raise SystemExit("❌ projeto.toml não encontrado — este script exige o manifesto do projeto.")


def campos() -> dict[str, str]:
    cfg = tomllib.loads((raiz_projeto() / "projeto.toml").read_text(encoding=ENCODING))
    a = cfg["autoria"]
    return {"projeto": cfg["projeto"]["nome"], "autor": a["autor"], "ano": a["ano"],
            "direitos": a["direitos"], "email": a["email"],
            "assinatura": a["assinatura_curta"]}


def linhas() -> list[str]:
    c = campos()
    return [c["projeto"],
            f"Autor: {c['autor']} © {c['ano']} - {c['direitos']}",
            f"E-mail: {c['email']}"]


PREFIXO = {
    "#": ("bash", "sh", "python", "py", "ruby", "rb", "yaml", "yml", "r", "julia",
          "toml", "perl", "make", "conf", "dockerfile"),
    "//": ("rust", "rs", "zig", "go", "javascript", "js", "typescript", "ts",
           "c", "cpp", "java", "swift", "kotlin", "scala", "dart", "csharp", "cs"),
    "--": ("sql", "haskell", "hs", "lua", "ada", "elm"),
    "%": ("tex", "latex", "matlab", "octave", "erlang"),
    ";": ("lisp", "clojure", "asm", "ini"),
}
BLOCO = {
    "fsharp": ("(*", "*)"), "fs": ("(*", "*)"), "ocaml": ("(*", "*)"), "ml": ("(*", "*)"),
    "md": ("<!--", "-->"), "markdown": ("<!--", "-->"),
    "html": ("<!--", "-->"), "xml": ("<!--", "-->"), "svelte": ("<!--", "-->"),
    "css": ("/*", "*/"), "scss": ("/*", "*/"),
}
EXT_LINGUAGEM = {
    ".py": "python", ".sh": "bash", ".bash": "bash", ".rs": "rust", ".fs": "fsharp",
    ".fsx": "fsharp", ".ml": "ocaml", ".sql": "sql", ".md": "md", ".html": "html",
    ".js": "javascript", ".ts": "typescript", ".svelte": "svelte", ".css": "css",
    ".toml": "toml", ".yaml": "yaml", ".yml": "yaml", ".rb": "ruby", ".go": "go",
    ".java": "java", ".c": "c", ".cpp": "cpp", ".zig": "zig", ".lua": "lua",
    ".jl": "julia", ".tex": "tex", ".r": "r", ".R": "r",
}


def carimbo(linguagem: str, bloco: bool = False) -> str:
    ling = linguagem.lower().lstrip(".")
    ls = linhas()
    if ling in BLOCO or (bloco and ling in BLOCO):
        ab, fe = BLOCO[ling]
        return "\n".join([ab, *ls, fe])
    for pref, langs in PREFIXO.items():
        if ling in langs:
            return "\n".join(f"{pref} {l}" for l in ls)
    if ling in ("json",):
        c = campos()
        return (f'"author": "{c["autor"]} <{c["email"]}>",\n'
                f'"license": "UNLICENSED",\n"private": true')
    raise SystemExit(f"❌ Linguagem desconhecida: {linguagem}. "
                     f"Use --todos para ver as suportadas.")


def _tem_carimbo(texto: str) -> bool:
    return campos()["autor"] in texto


def aplicar(arquivo: Path) -> bool:
    ling = EXT_LINGUAGEM.get(arquivo.suffix.lower())
    if not ling:
        print(f"  ⏭️  extensão não suportada: {arquivo.name}")
        return False
    texto = arquivo.read_text(encoding=ENCODING)
    if _tem_carimbo(texto):
        return False
    marca = carimbo(ling)
    linhas_arq = texto.splitlines(keepends=True)
    pos = 0
    if linhas_arq and linhas_arq[0].startswith("#!"):     # shebang fica em primeiro
        pos = 1
    novo = "".join(linhas_arq[:pos]) + marca + "\n" + "".join(linhas_arq[pos:])
    arquivo.write_text(novo, encoding=ENCODING)
    print(f"  ✅ carimbado: {arquivo}")
    return True


def verificar(diretorio: Path) -> int:
    faltando = []
    # .evidence/ e .svelte-kit/ são GERADOS pelo build do site; bin/obj pelo .NET; logs/dados são saída.
    # Exigir carimbo em arquivo gerado reprova o que não se edita (falso positivo do gate).
    ignorar = {"node_modules", ".git", ".venv", "venv", "target", "__pycache__",
               "build", "dist", "_private", ".evidence", ".svelte-kit", "bin", "obj", "logs", "dados"}
    for arq in sorted(diretorio.rglob("*")):
        if not arq.is_file() or set(arq.parts) & ignorar:
            continue
        if arq.suffix.lower() not in EXT_LINGUAGEM:
            continue
        try:
            if not _tem_carimbo(arq.read_text(encoding=ENCODING, errors="replace")):
                faltando.append(arq)
        except Exception:
            continue
    if faltando:
        print(f"❌ {len(faltando)} arquivo(s) SEM carimbo de autoria:")
        for f in faltando[:40]:
            print(f"   • {f}")
        if len(faltando) > 40:
            print(f"   … e mais {len(faltando)-40}")
        return 1
    print("✅ Todos os arquivos-fonte estão carimbados.")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    arg = sys.argv[1]
    if arg == "--todos":
        vistos = set()
        for grupo in (*PREFIXO.values(), tuple(BLOCO)):
            ling = grupo[0]
            if ling in vistos:
                continue
            vistos.add(ling)
            print(f"\n### {ling}\n{carimbo(ling)}")
        return
    if arg == "--aplicar":
        alvo = Path(sys.argv[2])
        alvos = [alvo] if alvo.is_file() else [
            a for a in alvo.rglob("*") if a.suffix.lower() in EXT_LINGUAGEM]
        n = sum(aplicar(a) for a in alvos)
        print(f"✅ {n} arquivo(s) carimbado(s).")
        return
    if arg == "--verificar":
        raise SystemExit(verificar(Path(sys.argv[2] if len(sys.argv) > 2 else ".")))
    print(carimbo(arg, bloco="--bloco" in sys.argv))


if __name__ == "__main__":
    main()
