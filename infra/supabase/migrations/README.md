# Migraciones de Supabase

**Actualizado 2026-08-20**: esta carpeta ya NO está vacía. Contiene las
**65 migraciones reales** aplicadas contra la base de datos de producción
(`zuiwdtwkahkrrnnatniy`, proyecto "StructAI"), reconstruidas **byte a byte**
desde `supabase_migrations.schema_migrations.statements` (Supabase guarda el
SQL exacto ejecutado por cada migración, no solo el nombre) — no son un
"baseline" aproximado, son el historial real.

## Por qué esto es seguro (no re-ejecuta nada en producción)

Cada archivo se llama `<version>_<nombre>.sql`, con `<version>` idéntica al
`version` ya registrado en `supabase_migrations.schema_migrations` de la
base de datos real. El mecanismo de migraciones de Supabase (tanto el CLI
`db push` como la integración GitHub) compara versiones contra esa tabla y
**solo aplica las que no están presentes todavía** — como las 65 versiones
de aquí YA existen en producción, empujar estos archivos no re-ejecuta nada,
es puramente declarativo/documental. Esto es el mismo principio que ya usan
Rails/Django/Alembic/Flyway: la tabla de control de migraciones es la fuente
de verdad de "qué ya se aplicó", nunca el contenido del archivo.

## Ver también

- `../SCHEMA.md` — resumen legible del schema actual (tablas, RLS, índices,
  funciones), generado por introspección el mismo día.
- Para el estado real y en vivo (no snapshot): `GET /data-status` en
  `apps/api`.

## Cómo mantener esto actualizado hacia adelante

Cualquier cambio de schema nuevo debe:
1. Aplicarse vía el MCP de Supabase (`apply_migration`) contra la base de
   datos real, como hasta ahora.
2. **Guardarse también aquí** como archivo nuevo `<version>_<nombre>.sql`
   con el mismo `version` que quedó registrado en
   `supabase_migrations.schema_migrations` — así el repo deja de acumular
   drift otra vez.

**No existe un script standalone para esto** (`supabase-py`/PostgREST no
exponen el esquema interno `supabase_migrations`, solo acceso directo a
Postgres lo permite — en esta sesión eso solo estuvo disponible vía el MCP
de Supabase, no vía una credencial reutilizable en un script del repo).
Para reconstruir/actualizar este historial en el futuro, correr esta
consulta contra el proyecto vía el MCP de Supabase (`execute_sql`) y
volcar cada fila a un archivo `<version>_<nombre>.sql` — es exactamente lo
que se hizo el 2026-08-20 para generar las 65 migraciones ya presentes:

```sql
select version, name, array_to_string(statements, E'\n') as sql_text
from supabase_migrations.schema_migrations
order by version;
```

Es idempotente por diseño: sobreescribir un archivo existente con el mismo
`<version>_<nombre>.sql` no duplica nada, y las migraciones ya presentes
aquí no cambian su SQL histórico (solo aparecerían filas nuevas al final).

## Por qué se archivó `001_auth_freemium.sql`

Ese archivo (en `../_archivo/001_auth_freemium.OBSOLETO.sql.txt`) describe
un diseño de esquema **abandonado y obsoleto**: crea tablas `user_profiles`,
`proyectos`, `trazabilidad_apu`, `trazabilidad_consultas` que **no existen**
en la base de datos real (que usa `profiles`, `apu_calculations`,
`consultas`/`consultas_history`, `plan_analyses`, etc.). Además redefine la
función `handle_new_user()`, que **sí existe y funciona** en producción
hoy — si ese archivo se hubiera aplicado vía la integración GitHub-Supabase,
habría sobrescrito el trigger real de registro de usuarios con una versión
que inserta en una tabla muerta, rompiendo el alta de usuarios nuevos
silenciosamente. No aparece en `schema_migrations`, así que nunca se
ejecutó contra la base de datos real — queda archivado, no borrado, por si
hace falta consultar el diseño original.
