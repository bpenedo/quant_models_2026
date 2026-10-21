#!/usr/bin/env python3
# quant_models_2026
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Fonte única da tradução dos READMEs (D4/D20) — padrão Translation Memory (SDL Trados).

    translation/blocos/pt.json      ← GERADO aqui (catálogo + leituras dos modelos + copy PT)
    translation/blocos/<xx>.json    ← traduções (uma por idioma, chave → segmento)
            │  montar_i18n.py
            ├─► translation/readme.template.md      (estrutura, nunca traduzida)
            ├─► translation/readme.blocos.json      (chave → {pt, en, …})
            ├─► translation/tuids.json              (chave → tuid estável, só incremental)
            └─► translation/translation.memory.md   (§3 glossário · §5 TUs · §5b targets)

Desatualização (fuzzy): cada tradução guarda o hash do segmento PT de origem em
`blocos/_origem.json`. Se o PT mudar (ex.: nova execução muda um número de uma leitura),
os alvos daquele segmento viram PENDENTES e `--verificar` reprova.

Uso:
    python3 montar_i18n.py --pt            # (re)gera blocos/pt.json e o template
    python3 montar_i18n.py --verificar     # cobertura e desatualização
    python3 montar_i18n.py                 # consolida blocos + TM
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo_modelos import MODELOS  # noqa: E402
from config import FOUNDATIONS, RAIZ, escrever, ler  # noqa: E402

TRAD = FOUNDATIONS / "translation"
BLOCOS_DIR = TRAD / "blocos"
IDIOMAS = ["pt", "en", "es", "fr", "de", "zh", "ko", "hi", "he", "ru", "sv", "fi"]
LOCALE = {"pt": "pt-BR", "en": "en-US", "es": "es-ES", "fr": "fr-FR", "de": "de-DE", "zh": "zh-CN",
          "ko": "ko-KR", "hi": "hi-IN", "he": "he-IL", "ru": "ru-RU", "sv": "sv-SE", "fi": "fi-FI"}
NOME_LOCALE = {"pt-BR": "Português (Brasil)", "en-US": "Inglês", "es-ES": "Espanhol", "fr-FR": "Francês",
               "de-DE": "Alemão", "zh-CN": "Chinês simplificado", "ko-KR": "Coreano", "hi-IN": "Híndi",
               "he-IL": "Hebraico", "ru-RU": "Russo", "sv-SE": "Sueco", "fi-FI": "Finlandês"}
FASE1 = [m for m in MODELOS if m["fase"] == 1]
GRUPOS = [
    ("g_estatistica", ["estatistica_descritiva", "suporte_resistencia", "estacionariedade_adf", "regressao_linear",
                       "outliers_multimetodo", "benford", "garch_volatilidade", "sistemas_nao_lineares",
                       "causalidade_granger"]),
    ("g_ml", ["regressao_logistica", "svm_kernels", "arvores_random_forest", "mlp_reversao", "pca_fatores",
              "kmeans_clusters", "embedding_retornos", "isolation_forest", "shap_explicabilidade"]),
    ("g_prob", ["markov_regimes", "hmm_regimes", "bayes_conjugado", "triple_barrier_ou", "fourier_ciclos",
                "wavelet_haar", "hurst_movel"]),
    ("g_otim", ["markowitz_fronteira", "ag_carteira", "ag_indicadores", "programacao_genetica", "rede_correlacao",
                "drift_modelo", "backtest_walkforward"]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Justificativa de escolha de cada modelo (PT): a pergunta de decisão que ele responde
PORQUE = {
    "estatistica_descritiva": "Escolha quando precisar saber se a média representa o caso típico ou se poucos extremos distorcem a conta.",
    "suporte_resistencia": "Escolha quando o limite de preço ou de orçamento precisar sair de um critério reprodutível, e não de uma linha traçada a olho.",
    "estacionariedade_adf": "Escolha antes de qualquer previsão: ele diz se o passado ainda é uma amostra válida do futuro.",
    "regressao_linear": "Escolha para medir quanto uma variável realmente explica outra — e descobrir que a relação 'óbvia' às vezes explica quase nada.",
    "outliers_multimetodo": "Escolha quando um dado estranho puder ser erro de coleta ou o evento mais importante da série: o consenso decide.",
    "benford": "Escolha para auditar uma base de valores antes de confiar nela, sabendo quando o teste se aplica e quando seria falso alarme.",
    "garch_volatilidade": "Escolha para dimensionar risco, estoque de segurança ou limite de exposição pelo risco de amanhã, não pela média do ano.",
    "sistemas_nao_lineares": "Escolha quando o pior cenário importar mais que o cenário médio: ele mede quanto as caudas reais excedem a curva normal.",
    "causalidade_granger": "Escolha para separar 'andam juntos' de 'um antecede o outro' antes de tomar um indicador como gatilho.",
    "regressao_logistica": "Escolha como linha de base honesta de toda classificação sim/não: se um modelo complexo não a vence, ele não paga o próprio custo.",
    "svm_kernels": "Escolha quando a fronteira entre 'bom' e 'ruim' for curva — e para provar se existe sinal antes de gastar com modelos maiores.",
    "arvores_random_forest": "Escolha quando a decisão precisar ser explicável em regras e robusta em dados tabulares.",
    "mlp_reversao": "Escolha para eventos raros de virada, medindo o acerto contra a frequência natural do evento, não contra a acurácia geral.",
    "pca_fatores": "Escolha para descobrir quantas apostas independentes existem de fato dentro de uma lista longa de opções.",
    "kmeans_clusters": "Escolha para agrupar alternativas pelo comportamento medido, e não pelo rótulo de catálogo.",
    "embedding_retornos": "Escolha para ver, num mapa único, quem se move junto agora — atualizado a cada janela.",
    "isolation_forest": "Escolha para achar o anormal sem exemplos rotulados: o primeiro alarme de que a dinâmica mudou.",
    "shap_explicabilidade": "Escolha quando alguém perguntar 'por que o modelo decidiu isso?' e a resposta precisar de números, não de fé.",
    "markov_regimes": "Escolha para responder 'estando nesta fase, qual a chance de passar para aquela?' com uma matriz auditável.",
    "hmm_regimes": "Escolha quando os regimes não forem observáveis e precisarem ser aprendidos dos dados, com probabilidade diária.",
    "bayes_conjugado": "Escolha quando houver poucos dados e muita pressão para decidir: ele diz quanto confiar na média, não só qual é a média.",
    "triple_barrier_ou": "Escolha para definir alvo e limite de perda a partir da dinâmica medida, em vez de percentuais fixos herdados.",
    "fourier_ciclos": "Escolha para provar se um ciclo sazonal existe ou se é acaso — todo espectro tem picos.",
    "wavelet_haar": "Escolha para localizar no tempo quando a turbulência começa, o que a média anual esconde.",
    "hurst_movel": "Escolha para decidir entre estratégia de tendência e de reversão — comparando com a referência sem memória.",
    "markowitz_fronteira": "Escolha para ver o melhor retorno possível para cada nível de risco — e o quanto esse ótimo depende de estimativas frágeis.",
    "ag_carteira": "Escolha quando o objetivo tiver restrições reais (custos, limites, perdas máximas) que nenhuma fórmula fechada aceita.",
    "ag_indicadores": "Escolha para buscar a melhor combinação de regras — registrando quantas foram testadas para não se enganar com o acaso.",
    "programacao_genetica": "Escolha para inventar fórmulas legíveis e auditáveis, e submetê-las a um período nunca visto.",
    "rede_correlacao": "Escolha para enxergar quem está no centro e quem está na periferia de um sistema de dependências.",
    "drift_modelo": "Escolha para saber que um modelo envelheceu antes que o prejuízo apareça.",
    "backtest_walkforward": "Escolha para testar qualquer regra de decisão contra o tempo, com custos e portões de reprovação declarados antes.",
}

# Copy PT (seções fixas). Números citados vêm de medições registradas (bench/historico.jsonl,
# testes_nucleo.py, executar_modelos.py, verificar_site.py).
COPY_PT = {
    "subtitulo": "40 modelos quantitativos para decidir sob incerteza",
    "slogan": "Pare de escolher por planilha. Comece a decidir por modelo.",
    "promessa": "32 modelos rodando sobre 16 anos de dados reais, três motores (Python, Rust e F#) que concordam bit a bit e um laboratório que roda no seu navegador — cada um mostrando, com o dado, onde a intuição engana.",
    "badge1_label": "32 modelos sobre dados reais", "badge1_txt": "32%20modelos-dados%20reais",
    "badge2_label": "3 motores bit a bit", "badge2_txt": "3%20motores-bit%20a%20bit",
    "badge3_label": "numba 273x mais rápido", "badge3_txt": "numba-273x%20mais%20r%C3%A1pido",
    "badge4_label": "36 páginas verificadas", "badge4_txt": "site-36%20p%C3%A1ginas%20verificadas",
    "badge_licenca": "licen%C3%A7a-todos%20os%20direitos%20reservados",
    "badge_licenca_label": "Licença: todos os direitos reservados",
    "aviso_oficial": "Use apenas este repositório como fonte. Os resultados dependem dos dados validados do DataFeed; nenhuma tela é recomendação de investimento.",
    "h_dor": "A dor: decidir por planilha", "h_solucao": "A solução", "h_aplicacao": "Para que serve — além do mercado",
    "h_telas": "Veja funcionando", "h_site": "O site e o laboratório", "h_modelos": "Os 32 modelos, um por um",
    "h_instalacao": "Instalação", "h_profundidade": "Arquitetura e decisões", "h_performance": "Desempenho medido",
    "h_faq": "Perguntas difíceis", "h_licenca": "Licença e autoria", "h_catalogo": "Catálogo completo",
    "g_estatistica": "Estatística — o que o dado é, antes do que ele prevê",
    "g_ml": "Aprendizado de máquina — com a régua da taxa-base",
    "g_prob": "Probabilidade e sinais — regimes, incerteza e ciclos",
    "g_otim": "Otimização e governança — o ótimo, o acaso e o tempo",
    "label_porque": "Por que escolher:", "label_leitura": "O que o dado mostrou:", "label_pagina": "página interativa",
    "dor_cena": "Você já fez isto. Montou uma planilha com as alternativas — fornecedores, celulares para a equipe, carros elétricos para a frota, ativos para a carteira, aeronaves para um esquadrão —, deu nota a cada critério, ponderou, ordenou do maior para o menor e levou o primeiro colocado para a reunião. A planilha estava certa. A decisão, não.",
    "dor_acao": "A planilha não erra a conta. Ela erra a pergunta.",
    "th_o_que_fez": "O que você fez", "th_o_que_aconteceu": "O que a ferramenta escondeu",
    "erro1": "Ordenou pela média do passado", "erro1_consequencia": "A média de 2010–2019 elegeu a melhor carteira; em 2020–2026 ela perdeu para os pesos iguais. O passado tinha ruído que a coluna não mostra.",
    "erro2": "Filtrou pelo rótulo", "erro2_consequencia": "'Diversificou' entre opções da mesma categoria que se movem juntas — e entre categorias diferentes que, no dado, formam o mesmo grupo.",
    "erro3": "Confiou na taxa de acerto", "erro3_consequencia": "Um modelo que 'acerta 54%' só repetia a fração de dias de alta. Acurácia alta sem poder de separação é um sorteio caro.",
    "diagnostico": "O defeito não é seu. É da ferramenta.",
    "diagnostico_explicacao": "Planilhas, matrizes de pontuação e filtros de classificação tratam cada número como certo. Nenhum deles pergunta quanto do que você vê é ruído, se o passado ainda representa o futuro ou se a sua 'melhor opção' sobreviveria a um período que ela nunca viu.",
    "problema_invisivel": "E há um erro que você comete sem saber: quanto mais alternativas e combinações você testa, melhor fica o resultado do passado — por puro acaso. O algoritmo genético deste projeto testou 1.826 regras para um índice de ações; a melhor brilhou no treino e perdeu, no período seguinte, para simplesmente manter a posição.",
    "h_colapso": "Onde a decisão desaba", "cena_do_fracasso": "Na reunião, a pergunta que derruba a recomendação nunca é 'qual a nota?'. É outra:",
    "pergunta_que_mata": "E se o cenário mudar — quanto disso continua de pé?",
    "porque_nao_tem_resposta": "A planilha não tem como responder, porque nunca separou sinal de ruído, nunca testou fora da amostra e nunca mediu a própria incerteza.",
    "como_funciona": "Cada um dos 32 modelos roda sobre 27 ativos reais de 2010 a 2026, com treino e teste separados no tempo, e termina com uma frase escrita a partir do número — inclusive quando o número desmente a intuição.",
    "diferencial_destaque": "Três motores independentes — Python/numba, Rust e F# — calculam a mesma matemática e precisam concordar bit a bit. Dois motores que concordam provam que a conta está certa, não só o código.",
    "antes": "Planilha", "depois": "Modelo",
    "antes_ex1": "A opção com a maior nota média", "depois_ex1": "A opção que sobrevive fora da amostra, com custo e risco declarados",
    "antes_ex2": "'Diversificado' porque são categorias diferentes", "depois_ex2": "Diversificado porque o dado mostra correlação baixa entre as escolhas",
    "honestidade": "Os modelos não preveem o futuro com certeza — e dizem isso: vários resultados aqui mostram que um método popular não tem sinal. Esse é o valor: saber onde não confiar antes de gastar.",
    "aplicacao_intro": "Os exemplos usam séries de mercado porque elas são longas, públicas e implacáveis. As técnicas são as mesmas para qualquer decisão sob incerteza — a própria base de conhecimento do projeto mostra o modelo de direção de mercado prevendo evasão escolar e o detector de anomalia apontando fraude.",
    "th_dominio": "Decisão", "th_modelos": "Modelos que respondem", "th_dor_especifica": "A pergunta que a planilha não responde",
    "dom1": "Carteira de investimentos", "dom1_modelos": "regimes (HMM), GARCH, Markowitz, backtest walk-forward",
    "dom1_dor": "A alocação ótima do passado vale para o próximo regime?",
    "dom2": "Compras corporativas — equipamentos e celulares", "dom2_modelos": "Benford, outliers, K-means, drift",
    "dom2_dor": "O preço deste fornecedor é anomalia, erro de digitação ou fraude? O fornecedor de ontem ainda entrega o mesmo?",
    "dom3": "Frota de carros elétricos", "dom3_modelos": "Bayes, GARCH, Monte Carlo O-U, sistemas não lineares",
    "dom3_dor": "Com poucos meses de dados de autonomia e de preço de energia, quanto confiar na economia projetada?",
    "dom4": "Defesa — aquisição de tanques e aeronaves", "dom4_modelos": "cadeias de Markov, caudas pesadas, AG com restrições, PCA",
    "dom4_dor": "Qual a disponibilidade esperada da frota entre operação e manutenção, e qual o custo no pior cenário, não no médio?",
    "dom5": "Startups e decisões executivas", "dom5_modelos": "Bayes, drift, SHAP, backtest walk-forward",
    "dom5_dor": "A hipótese validada no piloto continua válida no mercado — e consigo explicar a decisão ao conselho com números?",
    "ressalva_dados": "As telas e números deste repositório vêm de dados de mercado. Aplicar a outro domínio exige os dados daquele domínio; os métodos, os testes de validação e os três motores são os mesmos.",
    "site_intro": "O site é gerado com evidence.dev: SQL sobre os resultados, uma página interativa por modelo e um laboratório em que o motor Rust, compilado para WebAssembly, roda no seu navegador — sem servidor e sem custo por usuário.",
    "site1_titulo": "Vitrine: uma frase por modelo", "site1_leitura": "Cada linha é a leitura que o próprio dado produziu — inclusive as que desmentem a técnica popular.",
    "site2_titulo": "Laboratório no navegador (WebAssembly)", "site2_leitura": "216 mil trajetórias de Monte Carlo em cerca de 3 segundos, no navegador, com o mesmo motor que passa nos testes de concordância.",
    "site3_titulo": "Página de modelo: ficha, leitura e gráficos", "site3_leitura": "A regra ótima de saída sai da dinâmica medida do spread Brent − WTI, não de um percentual fixo.",
    "site4_titulo": "Três motores, um resultado", "site4_leitura": "Tempos medidos do mesmo kernel em numba, Rust e F#, com a partida de processo descontada.",
    "modelos_intro": "Cada tela abaixo tem a pergunta de decisão que o modelo responde e a leitura que o dado produziu. Os 8 modelos restantes do catálogo (texto, aprendizado por reforço e simulação multiagente) estão descritos em modelos_quant.md.",
    "instalacao_intro": "Pré-requisitos: Python 3.13, Rust 1.96 (com o alvo wasm32-unknown-unknown), .NET 9 para o motor F# e Node 20+ para o site. Os dados vêm do DataFeed Service Provider (variável QUANT_MODELS_DATAFEED).",
    "inst_passo1": "Dados e modelos", "inst_passo2": "Os três motores e a concordância", "inst_passo3": "Telas e site",
    "inst_passo4": "Execução longa em segundo plano (screen + watchdog de 20 minutos)",
    "profundidade_intro": "Decisões de arquitetura, cada uma com a razão que a sustenta:",
    "dec1": "Três motores com o mesmo gerador pseudoaleatório (xorshift64*)", "dec1_porque": "até o Monte Carlo coincide bit a bit; um erro de matemática não passa despercebido em três linguagens ao mesmo tempo.",
    "dec2": "WebAssembly sem dependências (63 KB)", "dec2_porque": "o cálculo pesado roda no navegador do usuário: custo de servidor zero e nenhum dado sai da máquina.",
    "dec3": "Treino e teste separados no tempo, sempre", "dec3_porque": "embaralhar séries temporais vaza o futuro para o treino e fabrica acurácia.",
    "dec4": "Estimadores comparados com o próprio nulo", "dec4_porque": "Hurst e Fourier têm vieses conhecidos; só a comparação com dados embaralhados separa sinal de artefato.",
    "dec5": "Leitura escrita a partir do número", "dec5_porque": "a frase de cada tela é gerada do resultado; quando o resultado muda, a frase muda junto.",
    "dec6": "Paralelismo com ProcessPoolExecutor e partição fixa", "dec6_porque": "o resultado não depende de quantos núcleos a máquina tem.",
    "performance_intro": "Números medidos com bench_motores.py e registrados no histórico do projeto. Rust e F# têm a partida de processo descontada.",
    "th_carga": "Carga", "th_python_puro": "Python puro",
    "perf_nota": "O caminho crítico (malha de Monte Carlo 20×20 em numba) roda em 3,4 s, com orçamento de 10 s e prova de resultado idêntico ao do motor Rust.",
    "faq1_p": "Já uso planilha com pesos e filtros. Não é a mesma coisa?", "faq1_r": "Não. A planilha soma notas que considera certas. Os modelos medem quanto da nota é ruído, testam a escolha num período que ela nunca viu e mostram quando a melhor opção do passado deixa de ser a melhor.",
    "faq2_p": "Algum desses modelos 'acerta o mercado'?", "faq2_r": "Vários resultados deste repositório mostram justamente o contrário para técnicas populares: indicadores e kernels sem sinal de direção diária, memória longa que é viés de estimador. Saber disso antes de investir tempo e dinheiro é o objetivo.",
    "faq3_p": "Por que três linguagens para a mesma conta?", "faq3_r": "Porque um segundo motor independente que concorda com o primeiro prova a matemática, e o terceiro desempata. Em 38 verificações, os três concordam bit a bit.",
    "faq4_p": "Preciso de servidor ou nuvem?", "faq4_r": "Não. Os modelos rodam na sua máquina e o site é estático: o laboratório executa o motor Rust em WebAssembly dentro do navegador.",
    "faq5_p": "Serve para decisões fora do mercado financeiro?", "faq5_r": "Os métodos sim; os dados precisam ser os do seu domínio. A tabela 'Para que serve' mostra quais modelos respondem a cada tipo de decisão.",
    "licenca_texto": "Código, modelos, textos e telas: uso restrito ao autor. Bibliotecas de terceiros mantêm suas próprias licenças (NumPy, numba, scikit-learn, SciPy, pandas, networkx, matplotlib, evidence.dev).",
    "catalogo_texto": "Os 40 modelos — número, tipo, categoria e descrição — estão em modelos_quant.md, gerado a partir da mesma fonte que alimenta o site.",
    "label_autor": "Autor",
    "bench_1": "Monte Carlo O-U (malha 20×20, 2.000 trajetórias)",
    "bench_2": "Hurst móvel R/S (janela 250, 3.917 pregões)",
    "bench_3": "HMM gaussiano EM (3 estados, 200 iterações)",
    "bench_4": "Métricas de 2.000 carteiras × 10 ativos",
}


def _hash(t: str) -> str:
    return hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]


def blocos_pt() -> dict:
    import pandas as pd
    resumo = pd.read_csv(RAIZ / "public/foundations/evidence/dados/quant/resumo_modelos.csv").set_index("id")
    b = dict(COPY_PT)
    for m in FASE1:
        n = MODELOS.index(m) + 1
        b[f"m{n:02d}_nome"] = m["nome"]
        b[f"m{n:02d}_porque"] = PORQUE[m["id"]]
        b[f"m{n:02d}_leitura"] = resumo.loc[m["id"], "destaque"]
    return b


def template() -> str:
    """Estrutura do README (padrão ECC adaptado). Prosa = {{b:chave}}; nunca traduzir aqui."""
    num = {m["id"]: MODELOS.index(m) + 1 for m in FASE1}
    secoes = []
    for g, ids in GRUPOS:
        partes = [f"### {{{{b:{g}}}}}\n"]
        for mid in ids:
            n = num[mid]
            partes.append(f"""#### {n:02d} · {{{{b:m{n:02d}_nome}}}}

<div align="center"><img src="docs/telas/{mid}.png" alt="{{{{b:m{n:02d}_nome}}}}" width="860"/></div>

**{{{{b:label_porque}}}}** {{{{b:m{n:02d}_porque}}}}

> **{{{{b:label_leitura}}}}** {{{{b:m{n:02d}_leitura}}}}
""")
        secoes.append("\n".join(partes))
    modelos = "\n".join(secoes)
    return f"""<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com

README GERADO — não editar à mão. Estrutura: montar_i18n.py · prosa: translation/blocos/<idioma>.json
Gerar: python3 public/foundations/pipeline/montar_i18n.py && python3 public/foundations/pipeline/gerar_readmes.py
-->

<div align="center">

# 📈 quant_models_2026 — {{{{b:subtitulo}}}}

<img src="docs/logo_capa.png" alt="ProfBru © 2026" width="320"/>

**ProfBru © 2026**

### {{{{b:slogan}}}}

**{{{{b:promessa}}}}**

[![{{{{b:badge1_label}}}}](https://img.shields.io/badge/{{{{b:badge1_txt}}}}-2a78d6?style=for-the-badge)](#modelos)
[![{{{{b:badge2_label}}}}](https://img.shields.io/badge/{{{{b:badge2_txt}}}}-eb6834?style=for-the-badge)](#arquitetura)
[![{{{{b:badge3_label}}}}](https://img.shields.io/badge/{{{{b:badge3_txt}}}}-1baf7a?style=for-the-badge)](#desempenho)
[![{{{{b:badge4_label}}}}](https://img.shields.io/badge/{{{{b:badge4_txt}}}}-6250d6?style=for-the-badge)](#site)

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![numba](https://img.shields.io/badge/numba-0.65-00A3E0)](https://numba.pydata.org)
[![Rust](https://img.shields.io/badge/Rust-1.96%20%2B%20WASM-000000?logo=rust)](https://www.rust-lang.org)
[![F#](https://img.shields.io/badge/F%23-.NET%209-378BBA?logo=fsharp&logoColor=white)](https://fsharp.org)
[![evidence.dev](https://img.shields.io/badge/evidence.dev-40-111827)](https://evidence.dev)
[![{{{{b:badge_licenca_label}}}}](https://img.shields.io/badge/{{{{b:badge_licenca}}}}-d03b3b)](#licenca)

{{{{lang:seletor}}}}

</div>

> [!WARNING]
> {{{{b:aviso_oficial}}}}

---

## 💀 {{{{b:h_dor}}}}

{{{{b:dor_cena}}}}

**{{{{b:dor_acao}}}}**

| {{{{b:th_o_que_fez}}}} | {{{{b:th_o_que_aconteceu}}}} |
|---|---|
| 🔻 **{{{{b:erro1}}}}** | {{{{b:erro1_consequencia}}}} |
| 🏷️ **{{{{b:erro2}}}}** | {{{{b:erro2_consequencia}}}} |
| 🎯 **{{{{b:erro3}}}}** | {{{{b:erro3_consequencia}}}} |

> [!IMPORTANT]
> **{{{{b:diagnostico}}}}**
> {{{{b:diagnostico_explicacao}}}}

{{{{b:problema_invisivel}}}}

### {{{{b:h_colapso}}}}

{{{{b:cena_do_fracasso}}}}

> *{{{{b:pergunta_que_mata}}}}*

{{{{b:porque_nao_tem_resposta}}}}

---

## 💊 {{{{b:h_solucao}}}}

{{{{b:como_funciona}}}}

> ### {{{{b:diferencial_destaque}}}}

<div align="center">

| ❌ {{{{b:antes}}}} | ✅ {{{{b:depois}}}} |
|---|---|
| {{{{b:antes_ex1}}}} | **{{{{b:depois_ex1}}}}** |
| *{{{{b:antes_ex2}}}}* | **{{{{b:depois_ex2}}}}** |

</div>

**{{{{b:honestidade}}}}**

---

## 🎯 {{{{b:h_aplicacao}}}}

{{{{b:aplicacao_intro}}}}

| {{{{b:th_dominio}}}} | {{{{b:th_modelos}}}} | {{{{b:th_dor_especifica}}}} |
|---|---|---|
| 📊 **{{{{b:dom1}}}}** | {{{{b:dom1_modelos}}}} | {{{{b:dom1_dor}}}} |
| 📱 **{{{{b:dom2}}}}** | {{{{b:dom2_modelos}}}} | {{{{b:dom2_dor}}}} |
| 🔋 **{{{{b:dom3}}}}** | {{{{b:dom3_modelos}}}} | {{{{b:dom3_dor}}}} |
| 🛡️ **{{{{b:dom4}}}}** | {{{{b:dom4_modelos}}}} | {{{{b:dom4_dor}}}} |
| 🚀 **{{{{b:dom5}}}}** | {{{{b:dom5_modelos}}}} | {{{{b:dom5_dor}}}} |

> [!NOTE]
> {{{{b:ressalva_dados}}}}

---

## 🖼️ {{{{b:h_telas}}}}

<a id="site"></a>

### 🌐 {{{{b:h_site}}}}

{{{{b:site_intro}}}}

| | |
|---|---|
| <img src="docs/telas/site/index.png" alt="{{{{b:site1_titulo}}}}" width="420"/><br/>**{{{{b:site1_titulo}}}}**<br/>{{{{b:site1_leitura}}}} | <img src="docs/telas/site/laboratorio.png" alt="{{{{b:site2_titulo}}}}" width="420"/><br/>**{{{{b:site2_titulo}}}}**<br/>{{{{b:site2_leitura}}}} |
| <img src="docs/telas/site/modelo_triple_barrier.png" alt="{{{{b:site3_titulo}}}}" width="420"/><br/>**{{{{b:site3_titulo}}}}**<br/>{{{{b:site3_leitura}}}} | <img src="docs/telas/site/motores.png" alt="{{{{b:site4_titulo}}}}" width="420"/><br/>**{{{{b:site4_titulo}}}}**<br/>{{{{b:site4_leitura}}}} |

<a id="modelos"></a>

### 🧪 {{{{b:h_modelos}}}}

{{{{b:modelos_intro}}}}

{modelos}

---

## ⚡ {{{{b:h_instalacao}}}}

{{{{b:instalacao_intro}}}}

**1 · {{{{b:inst_passo1}}}}**

```bash
git clone <url-do-repositorio-privado> quant_models_2026
cd quant_models_2026/public/foundations/pipeline
pip install -r requisitos.txt
export QUANT_MODELS_DATAFEED=/mnt/d/DataFeedServiceProvider
python3 dados_feed.py consolidar --tf D1
python3 executar_modelos.py
```

**2 · {{{{b:inst_passo2}}}}**

```bash
(cd ../rust/quant_models_2026_core && cargo build --release && cargo build --release --lib --target wasm32-unknown-unknown)
(cd ../fsharp/QuantModels2026.Core && dotnet build -c Release)
python3 testes_nucleo.py        # 38 verificações: numba × Rust × F#
```

**3 · {{{{b:inst_passo3}}}}**

```bash
python3 gerar_telas.py && python3 gerar_site.py
cd ../evidence && npm ci && bash subir_servidor.sh     # http://localhost:3020
```

**4 · {{{{b:inst_passo4}}}}**

```bash
./run_all.sh --background
screen -r quant_models_2026
```

---

<a id="arquitetura"></a>

## 🧠 {{{{b:h_profundidade}}}}

```mermaid
flowchart LR
  DSP[(DataFeed D1)] --> PQ[Parquet + zstd]
  PQ --> M[32 modelos · Python + numba]
  K[kernels] --> M
  K --- RS[Rust]
  K --- FS[F#]
  RS --> W[WASM 63 KB]
  M --> CSV[CSVs] --> EV[evidence.dev]
  W --> EV
  M --> T[telas] --> R[READMEs x12]
```

{{{{b:profundidade_intro}}}}

| | |
|---|---|
| **{{{{b:dec1}}}}** | {{{{b:dec1_porque}}}} |
| **{{{{b:dec2}}}}** | {{{{b:dec2_porque}}}} |
| **{{{{b:dec3}}}}** | {{{{b:dec3_porque}}}} |
| **{{{{b:dec4}}}}** | {{{{b:dec4_porque}}}} |
| **{{{{b:dec5}}}}** | {{{{b:dec5_porque}}}} |
| **{{{{b:dec6}}}}** | {{{{b:dec6_porque}}}} |

---

<a id="desempenho"></a>

## 🚀 {{{{b:h_performance}}}}

{{{{b:performance_intro}}}}

| {{{{b:th_carga}}}} | numba | Rust | F# | {{{{b:th_python_puro}}}} |
|---|---:|---:|---:|---:|
{{{{lang:tabela_bench}}}}

{{{{b:perf_nota}}}}

---

## 📚 {{{{b:h_catalogo}}}}

{{{{b:catalogo_texto}}}} → [modelos_quant.md](modelos_quant.md)

---

## ❓ {{{{b:h_faq}}}}

<details><summary><b>{{{{b:faq1_p}}}}</b></summary>

{{{{b:faq1_r}}}}
</details>

<details><summary><b>{{{{b:faq2_p}}}}</b></summary>

{{{{b:faq2_r}}}}
</details>

<details><summary><b>{{{{b:faq3_p}}}}</b></summary>

{{{{b:faq3_r}}}}
</details>

<details><summary><b>{{{{b:faq4_p}}}}</b></summary>

{{{{b:faq4_r}}}}
</details>

<details><summary><b>{{{{b:faq5_p}}}}</b></summary>

{{{{b:faq5_r}}}}
</details>

---

<a id="licenca"></a>

## 📜 {{{{b:h_licenca}}}}

{{{{b:licenca_texto}}}}

**{{{{b:label_autor}}}}:** ProfBru - Bruno Penedo © 2026 — {{{{lang:direitos}}}} · profbruanbima@gmail.com

<div align="center">

<img src="docs/logo_capa.png" alt="ProfBru © 2026" width="120"/>

**ProfBru © 2026**

</div>
"""


def gerar_pt() -> None:
    BLOCOS_DIR.mkdir(parents=True, exist_ok=True)
    pt = blocos_pt()
    escrever(BLOCOS_DIR / "pt.json", json.dumps(pt, ensure_ascii=False, indent=1) + "\n")
    escrever(TRAD / "readme.template.md", template())
    print(f"✅ blocos/pt.json ({len(pt)} segmentos) e readme.template.md")


def _carregar() -> dict[str, dict]:
    return {c: json.loads(ler(BLOCOS_DIR / f"{c}.json")) for c in IDIOMAS if (BLOCOS_DIR / f"{c}.json").exists()}


def verificar() -> list[str]:
    todos = _carregar()
    pt = todos.get("pt", {})
    origem_arq = BLOCOS_DIR / "_origem.json"
    origem = json.loads(ler(origem_arq)) if origem_arq.exists() else {}
    problemas = []
    for c in IDIOMAS[1:]:
        alvo = todos.get(c)
        if alvo is None:
            problemas.append(f"[{c}] arquivo de blocos ausente")
            continue
        faltam = [k for k in pt if not str(alvo.get(k, "")).strip()]
        if faltam:
            problemas.append(f"[{c}] {len(faltam)} segmento(s) sem tradução: {', '.join(faltam[:6])}")
        desat = [k for k in pt if k in alvo and origem.get(c, {}).get(k) not in (None, _hash(pt[k]))]
        if desat:
            problemas.append(f"[{c}] {len(desat)} tradução(ões) DESATUALIZADA(S) — o PT mudou: {', '.join(desat[:6])}")
        sobra = [k for k in alvo if k not in pt]
        if sobra:
            problemas.append(f"[{c}] {len(sobra)} chave(s) órfã(s): {', '.join(sobra[:6])}")
    return problemas


def consolidar() -> None:
    todos = _carregar()
    pt = todos["pt"]
    origem_arq = BLOCOS_DIR / "_origem.json"
    origem = json.loads(ler(origem_arq)) if origem_arq.exists() else {}
    # registra a origem das traduções que ainda não tinham hash (primeira consolidação)
    for c in IDIOMAS[1:]:
        o = origem.setdefault(c, {})
        for k in todos.get(c, {}):
            o.setdefault(k, _hash(pt.get(k, "")))
    escrever(origem_arq, json.dumps(origem, ensure_ascii=False, indent=1) + "\n")
    blocos = {k: {c: todos[c].get(k, "") for c in IDIOMAS if c in todos} for k in pt}
    escrever(TRAD / "readme.blocos.json", json.dumps(blocos, ensure_ascii=False, indent=1) + "\n")
    # tuids estáveis: só acrescenta, nunca renumera
    tu_arq = TRAD / "tuids.json"
    tuids = json.loads(ler(tu_arq)) if tu_arq.exists() else {}
    prox = max([int(v[1:]) for v in tuids.values()] + [100]) + 1
    for k in pt:
        if k not in tuids:
            tuids[k] = f"S{prox:03d}"
            prox += 1
    escrever(tu_arq, json.dumps(tuids, ensure_ascii=False, indent=1) + "\n")
    escrever_tm(pt, todos, tuids)
    print(f"✅ readme.blocos.json ({len(blocos)} segmentos × {len(todos)} idiomas) · TM atualizada")


def _cel(t: str) -> str:
    return str(t).replace("|", "\\|").replace("\n", " ")


GLOSSARIO = [
    ("pt-BR", "en-US", "es-ES", "fr-FR", "de-DE", "zh-CN", "ko-KR", "hi-IN", "he-IL", "ru-RU", "sv-SE", "fi-FI"),
    ("retorno", "return", "rentabilidad", "rendement", "Rendite", "收益率", "수익률", "प्रतिफल", "תשואה", "доходность", "avkastning", "tuotto"),
    ("volatilidade", "volatility", "volatilidad", "volatilité", "Volatilität", "波动率", "변동성", "अस्थिरता", "תנודתיות", "волатильность", "volatilitet", "volatiliteetti"),
    ("carteira", "portfolio", "cartera", "portefeuille", "Portfolio", "投资组合", "포트폴리오", "पोर्टफोलियो", "תיק השקעות", "портфель", "portfölj", "salkku"),
    ("regime de mercado", "market regime", "régimen de mercado", "régime de marché", "Marktregime", "市场状态", "시장 국면", "बाज़ार व्यवस्था", "משטר שוק", "рыночный режим", "marknadsregim", "markkinatila"),
    ("fora da amostra", "out of sample", "fuera de muestra", "hors échantillon", "außerhalb der Stichprobe", "样本外", "표본 외", "नमूने के बाहर", "מחוץ למדגם", "вне выборки", "utanför urvalet", "otoksen ulkopuolella"),
    ("taxa-base", "base rate", "tasa base", "taux de base", "Basisrate", "基准率", "기저율", "आधार दर", "שיעור בסיס", "базовая частота", "basfrekvens", "perustaso"),
    ("índice de Sharpe", "Sharpe ratio", "ratio de Sharpe", "ratio de Sharpe", "Sharpe-Ratio", "夏普比率", "샤프 지수", "शार्प अनुपात", "מדד שארפ", "коэффициент Шарпа", "Sharpekvot", "Sharpen luku"),
    ("drawdown", "drawdown", "drawdown", "drawdown", "Drawdown", "最大回撤", "최대 낙폭", "ड्रॉडाउन", "ירידה מהשיא", "просадка", "drawdown", "pudotus"),
    ("motor", "engine", "motor", "moteur", "Engine", "引擎", "엔진", "इंजन", "מנוע", "движок", "motor", "moottori"),
    ("leitura", "reading", "lectura", "lecture", "Befund", "解读", "해석", "निष्कर्ष", "קריאה", "вывод", "tolkning", "tulkinta"),
    ("algoritmo genético", "genetic algorithm", "algoritmo genético", "algorithme génétique", "genetischer Algorithmus", "遗传算法", "유전 알고리즘", "आनुवंशिक एल्गोरिदम", "אלגוריתם גנטי", "генетический алгоритм", "genetisk algoritm", "geneettinen algoritmi"),
    ("planilha", "spreadsheet", "hoja de cálculo", "tableur", "Tabellenkalkulation", "电子表格", "스프레드시트", "स्प्रेडशीट", "גיליון אלקטרוני", "электронная таблица", "kalkylblad", "taulukkolaskenta"),
]


def escrever_tm(pt: dict, todos: dict, tuids: dict) -> None:
    """Reescreve §3 (glossário), §5 (TUs) e §5b (targets) da TM; preserva §0–§2 e §4."""
    tm_arq = TRAD / "translation.memory.md"
    texto = ler(tm_arq)
    ini3 = texto.index("## 3. Glossário")
    ini4 = texto.index("## 4. Frase de direitos")
    ini5 = texto.index("## 5. Unidades de tradução")
    gl = ["## 3. Glossário (MultiTerm) — termos do domínio quantitativo", "",
          "> Termo que aparece mais de uma vez entra aqui ANTES de ser traduzido em qualquer lugar.", ""]
    for faixa in ((0, 5), (5, 9), (9, 12)):
        cab = [GLOSSARIO[0][0]] + list(GLOSSARIO[0][faixa[0] + 1 if faixa[0] == 0 else faixa[0]:faixa[1]])
        if faixa[0] == 0:
            cab = list(GLOSSARIO[0][0:5])
        gl.append("| " + " | ".join(cab) + " |")
        gl.append("|" + "---|" * len(cab))
        for termo in GLOSSARIO[1:]:
            cel = [termo[0]] + list(termo[faixa[0] + (1 if faixa[0] == 0 else 0):faixa[1]]) if faixa[0] else list(termo[0:5])
            gl.append("| " + " | ".join(cel) + " |")
        gl.append("")
    gl += ["---", "", ""]
    secao5 = ["## 5. Unidades de tradução (TU) — segmentos dos READMEs e do site", "",
              "Cada TU tem `tuid` **estável** (`translation/tuids.json`, só incremental). Segmento que muda de sentido "
              "ganha `tuid` novo; o antigo é aposentado. A interface do site usa os segmentos `S001`–`S016` (legado da "
              "fundação, preservados).", "",
              "| tuid | pt-BR (origem) | Chave |", "|---|---|---|"]
    legado_fonte = []
    legado_alvos: dict[str, list[str]] = {}
    # preserva S001–S016 da fundação
    import re
    bloco5 = texto[ini5:]
    for l in bloco5.splitlines():
        m = re.match(r"^\|\s*`(S0[01]\d)`\s*\|", l)
        if m and int(m.group(1)[1:]) <= 16:
            legado_fonte.append(l) if l.count("|") == 4 else None
    loc_atual = None
    for l in bloco5.splitlines():
        mm = re.match(r"^###\s+([a-z]{2}-[A-Z]{2})\b", l)
        if mm:
            loc_atual = mm.group(1)
            continue
        m = re.match(r"^\|\s*`(S0[01]\d)`\s*\|", l)
        if loc_atual and m and int(m.group(1)[1:]) <= 16 and l.count("|") == 3:
            legado_alvos.setdefault(loc_atual, []).append(l)
    secao5 += [l for l in bloco5.splitlines() if re.match(r"^\|\s*`S0(0\d|1[0-6])`\s*\|", l) and l.count("|") == 4]
    for k, v in pt.items():
        secao5.append(f"| `{tuids[k]}` | {_cel(v)} | `{k}` |")
    secao5 += ["", "---", "", "## 5b. Traduções de segmento (target segments por locale)", ""]
    for c in IDIOMAS[1:]:
        loc = LOCALE[c]
        secao5 += [f"### {loc} — {NOME_LOCALE[loc]}", "| tuid | target |", "|---|---|"]
        secao5 += legado_alvos.get(loc, [])
        for k in pt:
            secao5.append(f"| `{tuids[k]}` | {_cel(todos.get(c, {}).get(k, ''))} |")
        secao5.append("")
    secao5 += ["---", "", "_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 — TODOS OS DIREITOS "
               "RESERVADOS · profbruanbima@gmail.com_", ""]
    novo = texto[:ini3] + "\n".join(gl) + texto[ini4:ini5] + "\n".join(secao5)
    escrever(tm_arq, novo)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fonte única da tradução (TM SDL Trados).")
    ap.add_argument("--pt", action="store_true")
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()
    if a.pt:
        gerar_pt()
        return 0
    if a.verificar:
        p = verificar()
        if p:
            print("❌ Tradução incompleta ou desatualizada:")
            for x in p:
                print("   •", x)
            return 1
        print("✅ 12 idiomas completos e em dia com o PT")
        return 0
    consolidar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
