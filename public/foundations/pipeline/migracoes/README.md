<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
-->

# Migrações de esquema (D26/R15)

Numeradas, versionadas e aplicadas **em ordem**. O **DataGrip** é ferramenta de
**inspeção e manutenção** — não é canal de deploy. Alteração feita só na grade e não
versionada aqui é dívida invisível, e some na primeira restauração de backup.

```bash
python3 ../db_postgres.py nova "criar tabela de ordens"
python3 ../db_postgres.py estado
python3 ../db_postgres.py migrar
python3 ../db_postgres.py verificar
```
