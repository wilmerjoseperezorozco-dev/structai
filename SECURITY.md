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

## Alertas conocidas sin corrección aplicada (9 de noviembre de 2026)

Corregidas ese día: `js-yaml` (3 alertas altas) en `packages/shared-types`, actualizando su lockfile desactualizado a 4.3.2; `tsc --noEmit` pasa.

Quedan abiertas, con la razón:

| Paquete | Dónde | Por qué no se corrigió | Exposición |
|---|---|---|---|
| `decode-uri-component` ≤ 0.5.0 | `apps/native`, vía `expo-router` → `query-string` 7 | La versión corregida (0.5.1) es solo ESM y `query-string` 7 la llama como función con `require`; forzarla rompería el análisis de URL de la app. La corrección real depende de que `expo-router` actualice `query-string` | Denegación de servicio al decodificar una URL maliciosa en la propia app móvil, que está en Fase 0 y no se distribuye |
| `image-size` 1.2.1 | `apps/native`, vía `metro` (herramienta de empaquetado) | Un `overrides` a 2.0.3 no se aplicó en npm 11 con workspaces; no se forzó el lockfile a mano | Solo en desarrollo: lee imágenes del propio proyecto al empaquetar, no corre en producción |

Estas dos alertas no afectan a la API ni a la web en producción. Siguen abiertas en la pestaña Security hasta que se actualice `expo-router`/`metro` o se pruebe una vía de corrección.

## Alcance y límites

- Las alertas de dependencias se siguen con Dependabot y se listan en la [matriz de madurez](docs/MATRIZ_MADUREZ.md). Hay alertas abiertas: el estado real es el que muestra la pestaña Security del repositorio.
- No hay programa de recompensas.
- No pruebe contra datos de otras personas ni degrade el servicio de producción (sin pruebas de carga ni de denegación de servicio).

Ninguna salida de StructAI sustituye el criterio de un ingeniero responsable; esto no es un tema de seguridad del sistema pero se recuerda en cada respuesta.
