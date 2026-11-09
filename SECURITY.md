# Política de seguridad

## Versiones con soporte

Solo la rama `master` y lo que sirve producción (`structai.online` y la API en Cloud Run). No se mantienen versiones anteriores.

## Cómo reportar una vulnerabilidad

**No abra un issue público.** Use el reporte privado de GitHub: pestaña **Security → Report a vulnerability** de este repositorio. Incluya:

- qué componente afecta (API, web, base de datos, un motor) y cómo reproducirlo;
- el impacto que observó (acceso a datos, ejecución de código, denegación de servicio);
- si el hallazgo toca datos de usuarios, no los copie ni los conserve: describa lo mínimo para reproducir.

El proyecto lo mantiene una sola persona: la respuesta es de mejor esfuerzo, sin plazo garantizado. Se acusa recibo, se evalúa la gravedad y se corrige antes de publicar los detalles.

## Qué cuenta como vulnerabilidad y qué no

| Sí es un reporte de seguridad | No lo es (use un issue normal) |
|---|---|
| Saltarse la autenticación o los límites de tasa | Una cita o un numeral de norma incorrecto |
| Inyección, ejecución de código, lectura de archivos | Un resultado de cálculo que no coincide con una referencia |
| Exposición de secretos o de datos de usuarios | Un precio desactualizado |
| Dependencia con una vulnerabilidad explotable en este uso | Sugerencias de funcionalidad |

Los errores de contenido técnico (normas, cálculos, precios) se reportan con la plantilla de issue correspondiente: son importantes, pero no son un problema de seguridad del sistema.

## Alcance y límites

- Las alertas de dependencias se siguen con Dependabot y se listan en la [matriz de madurez](docs/MATRIZ_MADUREZ.md). Hay alertas abiertas: el estado real es el que muestra la pestaña Security del repositorio.
- No hay programa de recompensas.
- No pruebe contra datos de otras personas ni degrade el servicio de producción (sin pruebas de carga ni de denegación de servicio).

Ninguna salida de StructAI sustituye el criterio de un ingeniero responsable; esto no es un tema de seguridad del sistema pero se recuerda en cada respuesta.
