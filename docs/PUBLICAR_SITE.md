<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

# 🌐 Publicar o site — GitHub Pages ou Cloudflare Pages

> O site é **estático**: o build gera HTML, Parquet dos resultados e o motor `qm_core.wasm` (63 KB).
> Não há servidor nem banco a manter — o laboratório calcula no navegador de quem visita.
> **Nenhum passo abaixo é executado automaticamente.** Você roda cada comando no seu terminal.

## 1. Gerar o build

```bash
cd public/foundations/pipeline
python3 executar_modelos.py && python3 gerar_telas.py && python3 gerar_site.py
cd ../evidence
npm ci
npm run build              # saída em public/foundations/evidence/build/
npx serve build            # conferência local antes de publicar
python3 ../pipeline/verificar_site.py --url http://localhost:3000   # 36/36 páginas
```

## 2a. Cloudflare Pages (recomendado: domínio raiz, sem basePath)

```bash
npx wrangler login
npx wrangler pages project create quant-models-2026 --production-branch main
npx wrangler pages deploy public/foundations/evidence/build --project-name quant-models-2026
```

Para restringir o acesso, ative **Cloudflare Access** no projeto (Zero Trust → Access → Applications).

## 2b. GitHub Pages (repositório privado exige plano que permita Pages privado)

O site fica em `https://<usuario>.github.io/quant_models_2026/`, então o evidence precisa do *basePath*.
Acrescente a `public/foundations/evidence/evidence.config.yaml`:

```yaml
deployment:
  basePath: /quant_models_2026
```

O laboratório já usa `base` de `$app/paths` para achar `qm_core.wasm` e `laboratorio.json`
nesse subcaminho. Depois:

```bash
npm run build
# publique a pasta build/ no branch gh-pages (por exemplo com: npx gh-pages -d build)
```

## 3. O que vai para o site — e o que não vai

| Publicado | Não publicado |
|---|---|
| CSVs agregados dos 32 modelos (`evidence/dados/quant`) | séries brutas do DataFeed (`dados/parquet/` — no `.gitignore`) |
| retornos diários derivados de 10 ativos (`static/laboratorio.json`) | base de conhecimento (`_private/kb/`) |
| telas PNG e o motor WASM | governança, bugs e TM (`_private/`) |

---

_quant_models_2026 · Autor: **ProfBru - Bruno Penedo** © 2026 — TODOS OS DIREITOS RESERVADOS · profbruanbima@gmail.com_
