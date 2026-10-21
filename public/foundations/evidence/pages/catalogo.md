---
title: Catálogo de modelos
---
<!--
quant_models_2026
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

Os 40 modelos extraídos da base de conhecimento. A fase 1 roda sobre os dados do DataFeed; a fase 2 exige corpus textual, book de ofertas ou GPU.

```sql catalogo_modelos
select numero, nome, tipo, categoria, fase, case when fase = 1 then '/modelos/' || id else null end as pagina, descricao from quant.catalogo_modelos order by numero
```

<DataTable data={catalogo_modelos} rows=40 search=true link=pagina>
  <Column id=numero title="Nº"/><Column id=nome title="Modelo"/><Column id=tipo/><Column id=categoria/>
  <Column id=fase/><Column id=descricao title="Descrição" wrap=true/>
</DataTable>
