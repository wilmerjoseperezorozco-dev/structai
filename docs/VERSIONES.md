# Política de versiones, tags y trazabilidad

Objetivo: que cualquier estado importante del proyecto sea **identificable, reproducible y citable**, y que cada cambio se pueda seguir desde el commit hasta la versión que lo publicó.

```
commit pequeño  →  issue (qué y por qué)  →  milestone (fase)  →  tag / release (estado estable)
```

## Ramas

`master` es siempre la versión estable: compila, pasa la CI y es lo que alimenta producción. El trabajo largo se hace en ramas cortas (`feat/…`, `fix/…`) y entra por pull request. No se etiqueta nada sobre un árbol con cambios sin revisar.

## Versionado semántico (`vX.Y.Z`)

| Cambio | Incrementa | Ejemplo |
|---|---|---|
| Funcionalidad nueva compatible (motor, corpus, endpoint, análisis publicado) | `Y` | `v1.16.0` |
| Corrección sin cambiar el comportamiento esperado | `Z` | `v1.16.1` |
| Cambio incompatible de API pública, esquema de base de datos o comportamiento | `X` | `v2.0.0` |

`v2.0.0` se reserva para una ruptura real, no para un hito de marketing.

**Los tags de versión son planos** (`v1.15.0`). El nombre descriptivo va en el título del release (`v1.15.0 — Programa de investigación del Caribe…`). Los releases `v1.1.0`–`v1.9.0` se crearon con un sufijo en el tag; como SemVer interpreta un sufijo como pre-release (y lo ordena *antes* de la versión plana), existe además un tag plano en el mismo commit. Ambos se conservan para no romper enlaces.

## Tags de investigación (`research/…`)

Marcan un **estado cerrado y reproducible** de una línea de investigación: el commit donde ya están el protocolo, el código y los resultados. Se usan solo para eso.

| Tag | Qué fija |
|---|---|
| `research/protocolo-NN` | Resultados del protocolo NN (o, si se indica, el estado preregistrado antes de ejecutar) |
| `research/hN` | Resultados de una hipótesis concreta |
| `research/<tema>` | Una línea cerrada que no corresponde a un protocolo numerado (por ejemplo `precios-p1-p3`) |

Regla: un protocolo se **preregistra antes de ejecutar** y el tag va en el commit de resultados. Si hay estado preregistrado que importa conservar (como el protocolo 23), tiene su propio tag y la descripción lo dice. Los resultados nulos o negativos se etiquetan igual que los positivos.

## Milestones

Un milestone agrupa los issues de una fase y suele coincidir con un release. Los issues de visión (“no construir sin pedido”) viven en `Backlog: visión` para no mezclarse con el trabajo activo. Un milestone se cierra cuando se publica su release.

## Cómo publicar una versión

1. `master` limpio y la CI en verde.
2. Mover lo de `[Sin publicar]` en [`CHANGELOG.md`](../CHANGELOG.md) a la nueva versión, con fecha y periodo.
3. Alinear la versión de los `package.json`.
4. Tag anotado: `git tag -a vX.Y.Z -m "…"` y `git push origin vX.Y.Z`.
5. Release en GitHub con el título `vX.Y.Z — <nombre>` y las notas tomadas del CHANGELOG.
6. Cerrar el milestone de la fase y abrir el siguiente.

## Cómo citar

Para citar un resultado, usa el tag `research/…` correspondiente o la versión; el DOI de Zenodo de la portada identifica el proyecto. Todas las cifras públicas indican fecha y cómo reproducirlas.
