#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""IMUNIDADE HERDADA — testes de regressão vindos do catálogo GLOBAL de bugs.

GERADO por imunidade.py em 20/10/2026. Não editar à mão:
acrescente a classe em `imunidade.py` e ressemeie, para que TODOS os projetos
ganhem a mesma proteção.

Base: 982 defeitos catalogados em projetos anteriores.
Cada classe abaixo já custou caro pelo menos uma vez — e não vai custar de novo.

Uso:
  python3 testes_imunidade.py              roda tudo (entra na Passada 1)
  python3 testes_imunidade.py --detalhe    mostra a lição de cada classe
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
IGNORAR = {"node_modules", ".git", ".venv", "venv", "target", "__pycache__",
           "build", "dist", "_private", "dados"}

CLASSES = [
    {
        "id": "IMU-001",
        "titulo": "Ausência de dado virando valor neutro",
        "licao": "Nunca faça `if valor_ausente: usar_neutro()` num mecanismo de verificação. O mecanismo que existe para reprovar passa a aprovar tudo, em silêncio.",
        "categorias": [
            "FALHA-SILENCIOSA",
            "CORRETUDE"
        ],
        "rx": "\\.get\\([^)]*\\)\\s+or\\s+[0-9.]|if\\s+not\\s+\\w+\\s*:\\s*\\w+\\s*=\\s*0\\b|or\\s+0\\.0\\b",
        "arquivos": "*.py",
        "excecoes": [
            "config.py",
            "testes_imunidade.py",
            "tokenizacao.py"
        ]
    },
    {
        "id": "IMU-002",
        "titulo": "Encoding implícito em leitura/escrita de texto",
        "licao": "`read_text()` sem `encoding=` usa o locale da máquina (cp1252 no Windows pt-BR) e destrói acentuação. A falha só aparece na máquina do outro.",
        "categorias": [
            "CHARSET"
        ],
        "rx": "(?<!\\.)\\b(open\\((?![^)]*encoding=)[^)]*['\\\"][rwa]['\\\"]|read_text\\(\\s*\\)|write_text\\([^)]*\\)(?![^)]*encoding))",
        "arquivos": "*.py",
        "excecoes": [
            "config.py",
            "testes_imunidade.py"
        ]
    },
    {
        "id": "IMU-003",
        "titulo": "Background com nohup em vez de screen",
        "licao": "`nohup` despeja em arquivo e perde o terminal; `screen` permite reatar, ver ao vivo e interagir. Numa pipeline que pode pedir decisão, isso decide.",
        "categorias": [
            "BUILD/DEPLOY"
        ],
        "rx": "\\bnohup\\b",
        "arquivos": "*.sh",
        "excecoes": [
            "testes_imunidade.py",
            "verificar_publicacao.sh",
            "deploy_manual.sh",
            "run_all.sh"
        ]
    },
    {
        "id": "IMU-004",
        "titulo": "Carimbo de ferramenta de IA em artefato do projeto",
        "licao": "A autoria do projeto é exclusivamente do autor humano. Carimbo encontrado deve ser removido — não comentado, não desativado: removido.",
        "categorias": [
            "PRIVACIDADE/LGPD"
        ],
        "rx": "co-authored-by|generated with .*claude|claude code|anthropic",
        "arquivos": "*.py,*.md,*.sh,*.toml,*.json,*.rs,*.fs",
        "excecoes": [
            "testes_imunidade.py",
            "verificar_publicacao.sh",
            "deploy_manual.sh",
            "global_main_bugs.md",
            "stamp.md"
        ]
    },
    {
        "id": "IMU-005",
        "titulo": "Imagem de README apontando para _private/",
        "licao": "`_private/` não é publicado. A imagem existe na máquina do autor e quebra para todo o resto do mundo — defeito que a pré-visualização local esconde.",
        "categorias": [
            "LAYOUT"
        ],
        "rx": "!\\[[^\\]]*\\]\\([^)]*_private|<img[^>]*src=\\\"[^\\\"]*_private",
        "arquivos": "README.md,README.*.md",
        "excecoes": []
    },
    {
        "id": "IMU-006",
        "titulo": "Bug ou limitação documentado no README",
        "licao": "README vende a solução; bugs.md mantém a engenharia honesta. Públicos diferentes, documentos diferentes — misturar destrói os dois.",
        "categorias": [
            "CORRETUDE"
        ],
        "rx": "(nosso|neste|deste) (bug|defeito|erro)|bug conhecido|limitação conhecida|BUG-[0-9]{3}|(?-i:\\bFIXME\\b|\\bTODO:)",
        "arquivos": "README.md,README.*.md",
        "excecoes": []
    },
    {
        "id": "IMU-007",
        "titulo": "Ordem de resultado emergente de iteração de dicionário",
        "licao": "Ordem é dado, nunca emergente. Serializar um `set` ou iterar um dict sem ordenar produz saída que muda entre execuções — e o diff mente.",
        "categorias": [
            "DETERMINISMO"
        ],
        "rx": "for\\s+\\w+\\s+in\\s+set\\(|json\\.dump[s]?\\([^)]*set\\(",
        "arquivos": "*.py",
        "excecoes": [
            "testes_imunidade.py"
        ]
    },
    {
        "id": "IMU-008",
        "titulo": "Paralelismo com threading em trabalho CPU-bound",
        "licao": "O GIL serializa: `threading` em CPU-bound gasta complexidade sem ganho. Para CPU-bound é `ProcessPoolExecutor` (R2).",
        "categorias": [
            "PERFORMANCE"
        ],
        "rx": "ThreadPoolExecutor|threading\\.Thread",
        "arquivos": "*.py",
        "excecoes": [
            "testes_imunidade.py"
        ]
    },
    {
        "id": "IMU-009",
        "titulo": "Segredo ou credencial no código-fonte",
        "licao": "Segredo commitado é o vazamento mais comum em SMB — e o histórico do git não esquece: remover do HEAD não remove dos commits anteriores.",
        "categorias": [
            "SEGURANÇA",
            "PRIVACIDADE/LGPD"
        ],
        "rx": "api[_-]?key\\s*=\\s*[\\\"'][^\\\"']{12,}|BEGIN (RSA|PRIVATE) KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|postgres(ql)?://[^\\s\\\"']*:[^\\s\\\"']*@",
        "arquivos": "*.py,*.js,*.json,*.toml,*.sh,*.md",
        "excecoes": [
            "testes_imunidade.py",
            "verificar_publicacao.sh",
            "deploy_manual.sh"
        ]
    },
    {
        "id": "IMU-010",
        "titulo": "SGBD introduzido para acervo local",
        "licao": "Acervo local é carga em lote e leitura analítica. Postgres/MySQL acrescenta processo, porta, backup e ponto de falha sem entregar nada que Parquet + DataFusion não entreguem com latência menor (D24).",
        "categorias": [
            "BUILD/DEPLOY"
        ],
        "rx": "\\b(psycopg2|pymysql|MySQLdb)\\b",
        "arquivos": "*.py",
        "excecoes": [
            "testes_imunidade.py",
            "db_postgres.py"
        ]
    },
    {
        "id": "IMU-011",
        "titulo": "Marcador de template remanescente em arquivo publicado",
        "licao": "Marcador que sobrou é template publicado como se fosse produto — e o leitor descobre antes de você.",
        "categorias": [
            "CORRETUDE"
        ],
        "rx": "\\{\\{[A-Z_]{3,}\\}\\}",
        "arquivos": "README.md,README.*.md",
        "excecoes": []
    },
    {
        "id": "IMU-012",
        "titulo": "Saída de terminal em inglês",
        "licao": "O destinatário do software SMB é brasileiro. Mensagem de erro em inglês num sistema de oficina é defeito de produto, não detalhe (R1).",
        "categorias": [
            "UX"
        ],
        "rx": "print\\(\\s*[\\\"'](Error|Warning|Done|Success|Failed|Loading)\\b",
        "arquivos": "*.py",
        "excecoes": [
            "testes_imunidade.py"
        ]
    },
    {
        "id": "IMU-013",
        "titulo": "Separador decimal PT-BR aplicado à linha inteira",
        "licao": "`f\"...\".replace('.', ',')` sobre a linha inteira também troca os pontos do rótulo e do caminho: 'Memória .........:' vira 'Memória ,,,,,,,,,:'. Formate o NÚMERO antes de compor a linha.",
        "categorias": [
            "UX",
            "LAYOUT"
        ],
        "rx": "print\\(f?\\\"[^\\\"]*\\.{3,}[^\\\"]*\\\"[^)]*\\)\\.replace\\(\\\"\\.\\\", ?\\\",\\\"\\)",
        "arquivos": "*.py",
        "excecoes": [
            "testes_imunidade.py"
        ]
    }
]

EVIDENCIA = {
    "IMU-001": 483,
    "IMU-002": 13,
    "IMU-003": 56,
    "IMU-004": 0,
    "IMU-005": 61,
    "IMU-006": 355,
    "IMU-007": 21,
    "IMU-008": 37,
    "IMU-009": 35,
    "IMU-010": 56,
    "IMU-011": 355,
    "IMU-012": 31,
    "IMU-013": 92
}


def _arquivos(padroes: str):
    for padrao in padroes.split(","):
        for arq in RAIZ.rglob(padrao.strip()):
            if set(arq.parts) & IGNORAR or not arq.is_file():
                continue
            yield arq


def rodar(detalhe: bool = False) -> int:
    print("=" * 66)
    print("  IMUNIDADE HERDADA — regressões do catálogo GLOBAL de bugs")
    print("=" * 66)
    falhas = 0
    for c in CLASSES:
        rx = re.compile(c["rx"], re.I)
        achados = []
        for arq in _arquivos(c["arquivos"]):
            if arq.name in c["excecoes"]:
                continue
            try:
                texto = arq.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for n, linha in enumerate(texto.splitlines(), 1):
                if rx.search(linha):
                    achados.append((arq.relative_to(RAIZ), n, linha.strip()[:100]))
        ev = EVIDENCIA.get(c["id"], 0)
        if achados:
            falhas += 1
            print(f"  X {c['id']} · {c['titulo']}  ({len(achados)} ocorrencia(s))")
            for a, n, l in achados[:5]:
                print(f"       {a}:{n}  {l}")
            print(f"       LICAO: {c['licao']}")
        else:
            print(f"  OK {c['id']} · {c['titulo']}"
                  + (f"  [{ev} bug(s) no catalogo global]" if ev else ""))
            if detalhe:
                print(f"       {c['licao']}")
    print("=" * 66)
    if falhas:
        print(f"  REPROVADO: {falhas} classe(s) de defeito reintroduzida(s).")
        print("  Cada uma delas ja custou caro em outro projeto.")
        return 1
    print(f"  APROVADO: {len(CLASSES)} classes de defeito barradas.")
    return 0


if __name__ == "__main__":
    sys.exit(rodar("--detalhe" in sys.argv))
