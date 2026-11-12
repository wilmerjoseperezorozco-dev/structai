# Validación de K6 con el held-out escrito por Wilmer (#171)

Criterio prerregistrado (fijado antes de ver el held-out): (a) diferencia K6 − V1 en *aceptable* > 0 con IC95 que no cruce 0; (b) K6 no tiene más callejones sin salida que V1; (c) sin regresiones de enrutamiento en `test_rag_motores_regresion.py`.

Held-out: 60 preguntas escritas y etiquetadas a mano por Wilmer, congeladas en el commit fabdf2c antes de evaluar. Chequeo de fuga: 0 casi-duplicados de los ejemplos de entrenamiento y 0 iguales al dev.

| | V1 producción | K6 |
|---|---|---|
| Aceptable | 58.3% (35/60) | 78.3% (47/60) |
| Callejones sin salida | 3 | 1 |
| Enrutamiento correcto en la regresión de motores (13) | 13/13 | 13/13 |

Diferencia K6 − V1: **+20.0%**, IC95 bootstrap pareado **+10.0% a +30.0%**. McNemar exacto: K6 gana en 12 preguntas, V1 en 0, p = 0.0005.

- (a) CUMPLE
- (b) CUMPLE
- (c) CUMPLE

**Veredicto: K6 se recomienda para integrar (#192).**

Por tipo de pregunta (aceptable):

| Estrato | n | V1 | K6 |
|---|---|---|---|
| H_compuesta | 50 | 60% | 80% |
| H_negacion | 10 | 50% | 70% |

Por dominio esperado (aceptable):

| Dominio | n | V1 | K6 |
|---|---|---|---|
| geopot | 18 | 39% | 83% |
| normativa_general | 11 | 45% | 73% |
| apu_precios | 8 | 62% | 62% |
| gerencia | 6 | 100% | 100% |
| vias | 5 | 80% | 80% |
| vulnerabilidad_vivienda | 5 | 40% | 40% |
| aquai | 4 | 75% | 100% |
| peru_e030 | 3 | 100% | 100% |

Fallos de K6:

- #3 (H_compuesta) esperado `geopot` → K6 `normativa_general`: ¿Qué son las ondas sismicas y que diferencias existen entre las ondas primarias y las ondas secundarias?
- #18 (H_compuesta) esperado `apu_precios` → K6 `geopot`: ¿Qué variables tiene en cuenta un APU?
- #21 (H_compuesta) esperado `apu_precios` → K6 `gerencia`: ¿Cómo se hace un presupuesto solo mano de obra?
- #24 (H_negacion) esperado `apu_precios` → K6 `geopot`: ¿como se hacen las conversiones de m2/m3 y que caso no se pueden aplicar?
- #27 (H_compuesta) esperado `geopot` → K6 `normativa_general`: ¿Por qué el cemento pega?
- #32 (H_compuesta) esperado `vias` → K6 `geopot`: ¿Qué es trazabilidad vial?
- #35 (H_compuesta) esperado `normativa_general` → K6 `vias`: ¿Por qué es critico el nivel freatico y el drenaje superficial en el diseño de carretera y en excavaciones pro
- #38 (H_negacion) esperado `normativa_general` → K6 `geopot`: ¿Dame la formula general para diseñar una Viga 30cm X 50cm y a su vez dime cual no usar?
- #39 (H_compuesta) esperado `normativa_general` → K6 `geopot`: ¿Cómo se diseña una columna en zona sismica alta para una vivienda de 3 pisos?
- #47 (H_compuesta) esperado `vulnerabilidad_vivienda` → K6 `vias`: ¿Se observan grietas diagonales, fisuras profundas o desprendimiento de material en las paredes de carga?
- #48 (H_compuesta) esperado `vulnerabilidad_vivienda` → K6 `geopot`: ¿De qué material está construido el techo (y el entrepiso, si es de dos niveles) y cómo está fijado?
- #51 (H_compuesta) esperado `vulnerabilidad_vivienda` → K6 `geopot`: Presenta la vivienda problemas de asentamientos (hundimientos en pisos) o humedad ascendente severa en la base
- #43 (H_negacion) esperado `geopot` → K6 `aquai`: ¿Por qué no se debe utilizar agua salada en la mezcla de concreto armado?
