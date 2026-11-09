# Análisis de motores, ingesta y roadmap por etapas (2026-11-08)

Estado: **análisis, sin código nuevo.** Lo que está marcado «verificado» salió de una consulta o lectura de archivo de esta sesión; lo marcado «hipótesis» no se ha comprobado.

## 1. Motores: qué hay y qué le suma valor

| Motor | Estado verificado | Mejora de mayor valor |
|---|---|---|
| `motor-deformacion` | Casos cerrados de viga + pandeo Euler/Johnson. No hay solver discretizado ni adimensionalización. | Solver FD/FEM de `EI w'''' = q` y `EI w'''' + P w'' = 0` → `K·u = F`, con `x/L ∈ [0,1]`. Valida contra los casos cerrados (error < 1e-6 en mallas finas) y abre secciones variables, apoyos elásticos y viga sobre suelo (Winkler). |
| `motor-vulnerabilidad-vivienda` | Checklist AIS de 15 criterios; sin tabla Mo ni Lo automático. | Tres capas (sección 3). |
| `motor-concreto` / `orquestador` | Vigas, columnas rectangulares, SCWB, MILP por piso (commits `b20e326`, `11928bd`). | Columnas circulares, losas, cimentaciones (sección 4). |
| `motor-topovia` | **Sin código fuente** en el árbol; solo `.pytest_cache` con 18 tests (`tests/test_engine.py`: curva horizontal, pavimentos CBR→MR, poligonal cerrada, azimut/rumbo, diagrama de masas). Está en el historial git (commits `8e0fca9`, `b75fd0c`). | Recuperar con `git show` desde el historial y reescribir con los tests como especificación. Primero confirmar que el commit de limpieza lo borró a propósito. |
| `bim-intelligence` (2556 líneas), `ai-gateway` | Sin tests. | Tests de caracterización antes de tocar nada. |

## 2. Ingesta: inventario real y sesgos

Conteos verificados hoy: `nsr10_chunks` 10639, `motor_chunks` 4060, `ntc_chunks` 294, `normas_registro` 69 (53 vigente CO, 9 derogada_total, 4 desconocido, 1 derogada_parcial, 1 PE modificada, 1 EC desconocido).

Sesgos medibles:
- `motor_chunks`: vías 2816 (69 %), gerencia 818, aquai 320, geopot 106. **Geopot y estructural están subrepresentados** frente a lo que el producto promete.
- `ntc_chunks`: ACI 318-05 son 17 chunks de una «ficha curada», no texto verbatim; AISC 360-10, 6 chunks de ficha. Ambas figuran `vigente` en el registro aunque la edición ACI es 2005.
- Un solo país por norma sísmica extranjera (PE E.030 `modificada`, EC NEC-SE-DS `desconocido`).
- 4 normas con vigencia `desconocido` (RES-001049-2013, RES-000803-2009, RES-20213040041135-2021, RES-2743-2026) y NEC-SE-DS: el RAG las sirve sin saber si rigen.

Huecos (hipótesis hasta verificar en fuente primaria, regla del proyecto):
- **Cimentaciones profundas/pilotes:** Título H está, pero no hay norma específica de pilotes (p. ej. AASHTO LRFD, FHWA). Corpus insuficiente para un motor de pilotes que no invente.
- **Losas:** cubiertas solo por Título C (capítulos de losas en una y dos direcciones); falta verificar cobertura verbatim con el baseline de `rag-audit-kit`.
- **Marco legal:** no aparecen en el registro Ley 400/1997 ni el decreto de adopción de la NSR-10 (confirmar el número en fuente primaria antes de ingestar).
- **Evaluación/rehabilitación:** AIS 410-23 y AIS-2004 están; no hay FEMA P-154 ni ASCE 41 (y el proyecto ya decidió no mezclarlos con el método AIS).
- **Arquitectura/habitabilidad:** sin norma de accesibilidad ni de evacuación ingestada (hipótesis; verificar).

## 3. Vulnerabilidad: arquitectura de 3 capas (propuesta)

1. **Filtro rápido (determinista):** árbol sobre el checklist AIS ya existente; modelos Pydantic; alerta explícita «No conformidad crítica» cuando un criterio crítico falla. No requiere datos nuevos.
2. **Índice Benedetti‑Petrini adaptado:** 11 parámetros ponderados, vectorizado (N viviendas). **Bloqueo:** los pesos y escalas deben tomarse de una fuente citable; no se escriben de memoria. Primero localizar y verificar la tabla; si no se puede, la capa se entrega vacía y marcada «no verificada».
3. **Amenaza local:** Aa/Av del Apéndice A‑4 (ya ingestado), perfil de suelo A–F, y susceptibilidad por inundación/remoción en masa reutilizando HAND/CHIRPS y la microzonificación (#76) ya construidos. No duplicar esas fuentes.

## 4. Motores nuevos (orden por valor/riesgo)

| Etapa | Entrega | Dependencia de corpus |
|---|---|---|
| 1 | `motor-deformacion` FD/FEM + adimensionalización + validación cerrada | Ninguna (mecánica) |
| 2 | Recuperar `motor-topovia` desde git | Ninguna |
| 3 | Columna circular (P‑M por compatibilidad, zunchos/estribos) | Título C, mismos huecos de numerales ya listados |
| 4 | Losas en una dirección y placa (coeficientes verificables + FD sobre la ecuación de placa) | Título C capítulo de losas: auditar cobertura |
| 5 | Vulnerabilidad capas 1 y 3 | Capa 2 solo con fuente verificada |
| 6 | Zapatas aisladas/combinadas (capacidad portante) | Título H: auditar cobertura |
| 7 | Pilotes | **No empezar** hasta ingestar norma citable |
| 8 | Modelado plano genérico (pórticos 2D con cargas/apoyos arbitrarios, exportar al solver ya vectorizado) | Ninguna |

## 5. Ingesta por etapas

- **I‑1** (barato, alto valor): resolver `desconocido` de las 4 resoluciones y de NEC‑SE‑DS en fuente primaria; actualizar `normas_registro`.
- **I‑2:** reingesta de los numerales truncados ya listados (C.21.3.3, C.10.10.4.1, C.21‑7/‑8, C.21.3.5.6, C.10.3.6.2, Tabla C.9.5(a)); desbloquea parámetros hoy «no verificados» del motor de concreto.
- **I‑3:** ACI 318 y AISC 360 verbatim o dejarlos marcados explícitamente como fichas (hoy figuran `vigente` sin esa aclaración).
- **I‑4:** balancear `motor_chunks` (geopot/estructural) con tests de retrieval reales.
- **I‑5:** normas de pilotes/cimentaciones profundas, solo tras búsqueda de vigencia.

Cada etapa cierra con: consulta de retrieval real contra `match_<tabla>_chunks`, conteo `count(*)` (no `list_tables`) y actualización de `docs/fuentes-normativas.md`.

## 6. Límites de este análisis

No se leyó el código de `bim-intelligence` ni `ai-gateway` más allá de tamaño y existencia de tests. La lista de huecos normativos es hipótesis de cobertura, no auditoría contra fuente primaria. Los pesos Benedetti‑Petrini no se tienen verificados.

## 7. NSR-10: corpus completo vs. motor existente (2026-11-08)

Corpus según `docs/fuentes-normativas.md` (estado al 2026-09-24; no re-contado hoy). Motores según los módulos que existen hoy en `packages/`.

| Título | Corpus verbatim | Motor hoy | Siguiente módulo programable sin huecos |
|---|---|---|---|
| A | Incompleto: A.1, A.7, A.8, A.11, A.12, A.13 sin chunks (auditoría 2026-09-07; la memoria dice 45.6 % tras cierres posteriores) | `motor-geopot` (espectro, cortante basal, A‑4) | Irregularidades φa/φp (A.3.3.4/5 ya verbatim) |
| B | Parcial: B.4.3, B.4.6–B.4.8 sin chunks; B.3.4 resumido | `motor-analisis` (combinaciones) | Cargas vivas/muertas de B.3.4 tras ingesta verbatim |
| C | Verbatim completo | `motor-concreto`: viga, columna rectangular, SCWB | Columna circular, losas (C.13), zapatas (C.15), muros (C.14), nudos (C.21.7) |
| D | Verbatim completo | Ninguno | Muro de mampostería: resistencia a cortante y flexocompresión |
| E | Verbatim completo | `motor-vulnerabilidad-vivienda` (checklist) | Verificación de casas de 1–2 pisos |
| F | F.1–F.5.7.6 completo; F.5.7.7 en adelante pendiente | `motor-acero-frio` (ancho efectivo) | Miembros de acero laminado (F.2) |
| G | Verbatim completo | Ninguno | Vigas y columnas de madera/guadua |
| H | Verbatim completo | Ninguno | Capacidad portante y asentamientos (H.4) → zapatas |
| I | Verbatim completo | n/a (procedimental) | Lista de verificación de supervisión |
| J | Incompleto: casi todo resumido | Ninguno | Re-ingesta verbatim antes de programar |
| K | Verbatim completo | Ninguno | Pocos cálculos; baja prioridad |

Lectura: «sin huecos» hoy equivale a C, D, E, G, H, I, K y la parte de F ya ingestada. A, B y J se programan después de cerrar su ingesta; programar sobre ellos antes repetiría el error de usar texto resumido como si fuera la norma. Orden propuesto por valor: **H.4 + C.15 (zapatas)** → **C.13 (losas)** → **columna circular** → **D (muros)** → **G (madera)** → **F.2 (acero laminado)**.
