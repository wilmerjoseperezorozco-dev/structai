# Matriz general de elementos estructurales y estándar común de los motores de diseño generativo

Fecha: 2026-11-09. Estado: inventario y plan; solo lo marcado «hecho» tiene código y pruebas. Los valores de precio son costo directo INVIAS APU 2026-1, Atlántico Norte (catálogo `data/precios_elementos/catalogo_precios_2026-1.csv`), con incertidumbre en `distribuciones_precios.json`.

## 1. Contrato común de un motor (lo que cada elemento debe aportar)

| # | Pieza | Qué es | Dónde vive hoy |
|---|---|---|---|
| 1 | `Espacio` | Variables, rangos y escala; muestreo Sobol/LHS | Repetido en zapata y muro; falta extraer |
| 2 | `evaluar_geometria(caso, x)` | Verificación normativa determinista; única fuente de verdad de seguridad | Cada motor |
| 3 | `exacto(caso)` | Optimizador de referencia (búsqueda local, rejilla, DE o NSGA-II) | `muro_optimizador.py`, `zapata*.py` |
| 4 | `criterio` | Costo APU + λ·CO₂ con `Economia` | `economia_concreto.py` |
| 5 | Escenario de precios | `muestrear(Economia, rng)` con sigma calibrado | `precios_distribucion.py` (hecho) |
| 6 | Indexación | Llevar un precio a la fecha del proyecto con ICOCED | `Economia.indexar_a` + `indices_icoced.py` (hecho) |
| 7 | Sustituto | LightGBM entrenado sobre etiquetas del `exacto`; clasificación para variables discretas | `scripts/surrogate_muro/` |
| 8 | Guardia | Re-verificación independiente + intervalo conforme + detección fuera de distribución | Zapata y muro |
| 9 | Exportación | JSON, memoria de cálculo, DXF | `muro_exportar.py`, `encofrado_dxf.py` |
| 10 | Supuestos y «NO verifica» | Lista explícita en el docstring y en la memoria | Cada motor |
| 11 | Pruebas | Esperados calculados a mano, no solo regresión | `tests/` |

Brechas de integración detectadas: (a) las piezas 1, 7 y 8 no están en un kit compartido; (b) `Economia` usa constantes de código y no lee el catálogo; (c) el sustituto del muro no se ha reentrenado con las cinco tipologías ni con variables de precio; (d) los motores no están expuestos en `apps/api` ni enrutados por el chat (verificar antes de afirmarlo).

## 2. Matriz de elementos

Estado: **hecho** (código + pruebas), **parcial**, **plan**, **sin plan**. «Precio» indica si el catálogo INVIAS tiene ítems para costearlo.

| Elemento | Estado | Norma en el corpus | Precio disponible | Dato público para validar | Pendiente principal |
|---|---|---|---|---|---|
| Viga | hecho | C.9–C.11, C.21 | concreto, acero, formaleta | — | Entrar al kit común |
| Columna | hecho; costo y CO₂ desde 2026-11-09 | C.10, C.21 | idem | UW-PEER (columnas) | Validar contra ensayos |
| Zapata, pedestal | hecho | C.15, H | idem | — | Sustituto ya validado (0 inseguros) |
| Muro de contención en voladizo / contrafuertes / anclaje | hecho | H.6, C.14 | idem + 623,1 | — | Contraste con ejemplo publicado; momento vertical con contrafuertes sin calibrar |
| Pilote prefabricado / in situ | plan | H.4.4 (40 chunks) | 620,1 / 621,1 / 621,2 | SPT Atlántico: **no hay fuente pública verificada** | Perfiles SPT reales; motor de capacidad |
| Tablestaca | plan | H | 622,1–622,4 por m² | — | Motor de empuje y empotramiento |
| Muro de corte | plan | C.21.9 (45 chunks) | concreto, acero, formaleta | UW-PEER / SERIES RC Walls | Auditar completitud con rag-audit-kit |
| Viga de acople | plan | C.21.9.7 | idem | idem | Requiere modelo de pórtico equivalente |
| Ménsula, nudo, viga pared | plan | C.11.8, C.11.9, C.21.7, Apéndice C-A | idem | PEER (nudos parcial) | Falta el Comentario de C-A (figuras) |
| Cercha / cubierta | plan | F (2.728 chunks), B | **acero estructural fabricado: sin fuente** | — | Precio de acero estructural y montaje |
| Escalera (plegada, helicoidal) | plan | C.9.5, B | idem concreto | — | Calibrar contra elementos finitos |
| Losa maciza / aligerada (viguetas y casetón) | sin plan | C.13 (212 chunks), C.9.5 | concreto, acero, formaleta, malla 640,2 | — | **Elemento más común en vivienda colombiana; falta plan** |
| Viga de cimentación / riostra, losa de fundación | sin plan | C.15, H | idem | — | Falta plan |
| Muro de gaviones | sin plan | H | 681,1–681,5 por m³ | — | Motor de estabilidad externa (reusa muro) |
| Muro de suelo reforzado con geosintético | sin plan | H | geomalla biaxial 20 kN/m: 9.834 COP/m²; geotextil | — | Motor de estabilidad interna y externa |
| Mampostería estructural / confinada | sin plan | Título D | bloques (ICOCED) | — | Precios de mampostería no están en el catálogo |
| Pórtico de acero con conexiones | sin plan | F | platina, soldadura, pintura | — | Conexiones |
| Acero formado en frío | parcial | `motor-acero-frio` solo ancho efectivo | platina galvanizada | — | Verificaciones de miembro |
| Alcantarilla / cajón de concreto, losa de puente corta | sin plan | — | 630, 633 | — | Cargas viales fuera de NSR-10 |
| Pavimento rígido | sin plan | — | 500,1 por m³ | — | Fuera del alcance estructural de edificios |

## 3. Precios que alimentan la matriz (Atlántico Norte, 2026-1, costo directo)

| Familia | Ítem INVIAS | Valor | Unidad | Sigma lognormal |
|---|---|---|---|---|
| Acero de refuerzo instalado | 640,1 | 6.826 | COP/kg | 0,120 |
| Concreto estructural premezclado | 630,1,1 | 852.673 | COP/m³ | 0,090 |
| Anclaje postensado (roca) | 623,1 | 549.776 | COP/m | 0,283 (incluye 0,25 de especificación supuesta) |
| Pilote prefabricado | 620,1,1 / 620,1,2 | 388.900 / 544.439 | COP/m | pendiente |
| Pilote in situ | 621,1,1 / 621,1,2 | 2.359.302 / 2.680.252 | COP/m | pendiente |
| Tablestacado metálico | 622,2 | 218.308 | COP/m² | pendiente |
| Gavión | 681,1 | 294.531 | COP/m³ | pendiente |
| Acero de preesfuerzo instalado | 641,2 | 11.607 | COP/kg | pendiente |

Dispersión medida: el efecto de provincia es pequeño (rango intercuartil relativo ≤ 0,24 en las 23 actividades del catálogo; hasta 0,42 en insumos como la formaleta de madera); domina la incertidumbre de especificación y de fecha. El ICOCED de Barranquilla AM a septiembre de 2026 muestra variación anual de +9,1 % en acero corrugado y −0,9 % en concreto común.

## 4. Fuentes de datos públicos para validar (estado de verificación)

| Fuente | Contenido | Verificado | Uso |
|---|---|---|---|
| DANE ICOCED (anexos mensuales) | 19 dominios, 93 insumos, base dic-2021, 2022-01 a 2026-09 | **Descargado y procesado** (100.719 filas) | Indexación de precios |
| UCI Concrete Compressive Strength (Yeh, 1998; CC BY 4.0) | 1.030 mezclas, edad, resistencia | **Descargado y analizado** | Calibración de la relación a/c–resistencia |
| Mendeley: Multi-source Modified Concrete (≈2.578 mezclas), SCM-blended (1.456 mezclas, con módulo), recycled aggregate (1.736 registros) | Mezclas y propiedades | Solo por descripción de búsqueda; licencias sin revisar | Ampliar calibración |
| UW-PEER Structural Performance Database | Ensayos cíclicos de columnas (cientos a más de mil) | Solo por descripción; el recuento difiere entre fuentes | Validar columnas y muros |
| SERIES RC Walls Database (DOI 10.7277/2FY5-BK22, 2013) | Ensayos de muros de concreto | Solo por descripción | Validar muros de corte |
| SPT / sondeos de Barranquilla | — | **No se encontró fuente pública** | Pendiente: Alcaldía, CRA, curaduría, estudios de suelos locales |
| Ensayos de laboratorio locales (NTC 673) | Compresión de cilindros | **No hay conjunto abierto**; hay tesis y reportes en PDF | Requiere convenio con laboratorio |

## 5. Hallazgo sobre el modelo de resistencia del concreto

`economia_concreto.mezcla()` usa Abrams `f_cm = 90 / 9^(a/c)`. Contra los 80 ensayos de UCI a 28 días sin escoria ni ceniza (a/c entre 0,27 y 0,90):

- el modelo subestima la resistencia media en ≈ 20 % (sesgo logarítmico medio +0,183, desviación 0,157; error porcentual absoluto medio 0,18);
- el ajuste libre da `f = 134·exp(−2,60·a/c)` (equivale a B = 13,5), con R² logarítmico 0,878.

Esto **no** prueba que el modelo falle para cemento colombiano: UCI reúne datos de varias fuentes (17 según la descripción del conjunto), tiene superplastificante y cementos de otros países. Sí indica que las constantes 90 y 9 son una elección conservadora sin calibración local, y que el costo del concreto del optimizador (que depende del contenido de cemento necesario) puede estar sesgado hacia mezclas más caras. La calibración debe hacerse con ensayos locales.

## 6. Laboratorio digital con aprendizaje automático (plan)

Objetivo: medir cuánto de lo que se hace en laboratorio puede anticiparse con simulación sintética calibrada, y dónde la simulación falla.

1. Generador sintético con relaciones conocidas: Abrams/Bolomey para resistencia a 28 días; evolución con la edad (ACI 209 o CEB-FIP); módulo de elasticidad (`E ≈ f(√f'c)` del Título C); módulo de rotura; contracción y fluencia; efecto del contenido de pasta y de aditivos.
2. Ruido y sesgo de laboratorio calibrados con datos reales (dispersión entre cilindros, entre lotes y entre laboratorios).
3. Modelos candidatos: regresión simbólica o paramétrica sobre las relaciones físicas, procesos gaussianos y LightGBM; comparar por validación en datos reales no vistos (UCI y Mendeley), no en los sintéticos.
4. Métrica central: brecha simulación–realidad por variable (resistencia, módulo, revenimiento) y cobertura de intervalos.
5. Cierre: constantes locales (A y B de Abrams, módulo) con ensayos de laboratorios del Atlántico, y reentrenamiento del costo del concreto del optimizador.

## 7. Orden de ejecución propuesto

1. Corregir la ingesta INVIAS (columnas de materiales) y completar sigmas de las familias que faltan.
2. Integrar indexación ICOCED y lectura del catálogo en `Economia`.
3. Extraer el kit común (`Espacio`, etiquetado, sustituto, guardia).
4. Reentrenar el sustituto del muro con cinco tipologías y variables de precio.
5. Laboratorio digital y calibración local del concreto.
6. Elementos nuevos en el orden del plan de escalamiento, añadiendo losas aligeradas y gaviones.
