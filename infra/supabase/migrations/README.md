# Migraciones de Supabase

Esta carpeta está vacía intencionalmente por ahora.

## Estado real

El esquema de la base de datos de producción (`zuiwdtwkahkrrnnatniy`, proyecto
"StructAI") se ha construido aplicando migraciones **directamente contra la
base de datos real** vía el MCP de Supabase (`apply_migration`), no a través
de archivos versionados en este repo. Esas 20 migraciones reales sí quedan
registradas en la tabla `supabase_migrations.schema_migrations` de la base de
datos (verificable con `list_migrations`), pero **no existen como archivos
`.sql` aquí**.

Migraciones reales aplicadas (nombre, no contenido — ver la base de datos
real para el detalle exacto):

`construdata_auth_rls`, `construdata_plan_analyses`, `structai_sgsst_chunks`,
`structai_agent_results`, `security_fixes_structai`,
`security_fixes_views_and_agent_results`,
`fix_remaining_update_policy_checks`, `search_knowledge_over_real_schema`,
`search_knowledge_fix_column_ambiguity`, `search_knowledge_fix_score_type`,
`aquai_proyectos`, `fix_search_knowledge_search_path`,
`rag_embeddings_switch_to_local_384dim`, `geopot_proyectos`,
`vias_proyectos`, `gerencia_proyectos`, `motor_chunks_rag_dominio`,
`create_normas_registro_vigencia`, `search_knowledge_surface_vigencia`,
`search_knowledge_include_general_normativa_in_motor_filter`.

## Por qué se archivó `001_auth_freemium.sql`

Ese archivo (ahora en `../_archivo/001_auth_freemium.OBSOLETO.sql.txt`)
describe un diseño de esquema **abandonado y obsoleto**: crea tablas
`user_profiles`, `proyectos`, `trazabilidad_apu`, `trazabilidad_consultas`
que **no existen** en la base de datos real actual (que usa `profiles`,
`apu_calculations`, `consultas`/`consultas_history`, `plan_analyses`, etc.).
Además redefine la función `handle_new_user()`, que **sí existe y funciona**
en producción hoy — si ese archivo se hubiera aplicado vía la integración
GitHub-Supabase, habría sobrescrito el trigger real de registro de usuarios
con una versión que inserta en una tabla muerta, rompiendo el alta de
usuarios nuevos silenciosamente. No aparece en `schema_migrations`, así que
nunca se ejecutó contra la base de datos real — es seguro que quede
archivado, no borrado, por si hace falta consultar el diseño original.

## Pendiente (no urgente)

Para que la integración GitHub-Supabase (Project Settings → Integrations →
GitHub, con "Working directory" apuntando a `infra/supabase`) tenga utilidad
real hacia adelante, cualquier cambio de esquema nuevo debería añadirse aquí
como archivo de migración además de aplicarse vía MCP, para que el repo deje
de tener drift con la base de datos real. Generar un archivo de "baseline"
que capture el esquema completo actual sigue pendiente si se quiere
reproducibilidad completa desde cero — no es necesario para que la
integración funcione de forma segura desde ahora (con esta carpeta vacía,
un push no hace nada, porque no hay migraciones pendientes que aplicar).
