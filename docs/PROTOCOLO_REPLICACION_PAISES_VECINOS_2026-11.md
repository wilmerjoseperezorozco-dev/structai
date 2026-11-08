# Protocolo de replicación en países vecinos (issue #110)

Preregistrado el 2026-11-08, **antes de descargar o calcular nada** para ningún país distinto de Colombia. Colombia sigue siendo el país primario: sus resultados son la línea base y ningún dato extranjero los reemplaza (ver `referencia_internacional.py` y la columna `pais` de `normas_registro`).

**Qué es este documento:** un contrato de método. Fija qué se replica, con qué control de sesgo, qué cuenta como evidencia y qué se prohíbe concluir. **Qué no es:** un resultado, ni una propuesta de norma continental.

Todas las cifras de la sección 1 salen de los informes del repositorio que se citan; no se recalcularon para este documento.

## 1. Lo que ya hicimos en Colombia (inventario consolidado)

### 1.1 Qué significan los órdenes
El repositorio define explícitamente el segundo y el tercer orden (`docs/investigacion/relaciones_no_lineales_con_rezago.md`, `scripts/hidro/PROTOCOLO_COHERENCIA.md`). El primer orden **no está definido en ningún documento**; lo fijo aquí para este protocolo y queda sujeto a corrección.

| Orden | Definición operativa | Ejemplos ya ejecutados |
|---|---|---|
| **1.º** (definición mía, nueva) | Descripción y asociación marginal: distribuciones, cobertura, una variable frente a otra sin dinámica | Cobertura ESA CCI; distribución del área SIMMA; sesgo de CHIRPS frente a normales IDEAM y pluviómetros; asociación vía-evento (V1 en el Caribe) |
| **2.º** | Regresión estática con controles: la relación se mantiene al descontar tamaño, reporte u otras variables | Barrido del Caribe (correlación parcial de Spearman); V1 en 21 departamentos; SGC frente a UNGRD (K3, K4); regionalización de caudales; pendiente de cauce; régimen térmico |
| **3.º** | Dinámica: rezagos, interacciones, dependencia espacio-temporal | Rezagos no lineales ONI×TNA→lluvia; coherencia espacio-temporal de anomalías de caudal y su modulación por ENSO (C2); umbrales lluvia-duración; GEV con ENSO (H4) |

### 1.2 Resultados por línea (positivos y negativos con el mismo peso)

| Línea | Resultado verificable | Fuente |
|---|---|---|
| Amenaza oficial frente a eventos | El índice del SGC ordena municipios: AUC 0,76; ρ parcial +0,39 tras descontar población y reporte; +0,18 tras descontar pendiente. **La pendiente sola ordena igual (AUC 0,78).** Por región: Pacífica 0,73, Andina 0,65, Caribe 0,59 | `RESULTADOS_SGC_VS_UNGRD.md` |
| Exposición vial (V1) | Candidato del barrido del Caribe (ρ +0,34). **No se confirmó fuera de él:** confirmación ρ 0,00 [−0,10; +0,11], n = 570. No mejora la focalización | `RESULTADOS_BARRIDO_CARIBE.md`, `RESULTADOS_V1.md` |
| Sesgo de reporte UNGRD | Medido: el indicador usado atenúa el efecto un 6 % (criterio: 50 %); **prueba débil** porque el indicador casi no varía en el Caribe | `RESULTADOS_SESGO_REPORTE.md` |
| Índice vial solo con DEM | Ningún criterio se cumple; el resultado casi constante (93–96 % de municipios con evento) deja sin potencia | `RESULTADOS_INDICE_VIAL.md` |
| Susceptibilidad con ML | Gradient boosting: AUC global 0,903 pero concordancia con el mapa SGC ρ +0,54 global y **+0,10 Andina, −0,26 Pacífica**; el plugin omite el índice donde ρ < 0,30 | `RESULTADOS_SUSCEPTIBILIDAD_MUNICIPAL.md` |
| Umbrales y extremos | Lluvia acumulada a 5 días: AUC 0,775; la curva E–D **no** supera a la regla simple; H3 (logaritmos) confirmada; H2, H4b peores que la base | `RESULTADOS_UMBRALES_Y_FORMULAS.md` |
| Rezagos no lineales | **Ningún modelo no lineal supera al lineal estacional** (p Holm = 1,0); la habilidad lineal no sobrevive a la corrección | `scripts/clima/RESULTADOS_REZAGOS_NO_LINEALES.md` |
| Coherencia de caudales | Anomalías sincronizadas en todas las regiones; La Niña multiplica por 2–2,7 la fracción de estaciones en anomalía alta (Andina, Pacífica, Caribe), **sin efecto en Orinoquía y signo opuesto en Amazonía**; ≈ 2,5–3,3 estaciones independientes por promedio regional | `scripts/hidro/RESULTADOS_COHERENCIA.md` |
| Regionalización de caudales | Mejora pequeña frente al área sola (factor de error 1,88 → 1,75); modelos por región, temperatura y pendiente de cauce **no mejoran** la validación ciega | `RESULTADOS_REGIONALIZACION_CAUDALES.md`, `RESULTADOS_NO_ESTACIONARIEDAD.md`, `RESULTADOS_REGIMEN_TERMICO.md`, `RESULTADOS_PENDIENTE_CAUCE.md` |
| Insumos | CHIRPS sobrestima 5 % frente a normales, pero la concordancia **no es independiente** (usa las mismas estaciones); humedad ESA CCI sin dato en Andes y Pacífico; HAND de 90 m no ve diques | `RESULTADOS_NORMALES_CHIRPS.md`, `RESULTADOS_SESGO_CHIRPS.md`, `RESULTADOS_ESA_CCI_COBERTURA.md` |
| Literatura | El piloto de ecuaciones de la literatura no produjo ninguna evaluable (bloqueos de acceso y rangos de validez); la verificación de referencias usa `verificar_referencias.py` y `referencias_verificadas.json` (46 entradas) | `RESULTADOS_LITERATURA_CAUDALES.md` |
| Normas | NSR-10 por títulos, Perú E.030 (corpus mixto 2019/2026), Ecuador NEC-SE-DS; referencias extranjeras con etiqueta `INT/<PAIS>/<AÑO>` | `docs/fuentes-normativas.md`, migración `20261108140000` |

### 1.3 Lecciones que este protocolo convierte en reglas
1. **Un candidato del barrido no es un hallazgo.** V1 se vio en 7 departamentos y se desvaneció al salir. Regla: nada se afirma en un país sin confirmación en datos que no entraron a su descubrimiento.
2. **El efecto puede ser regional.** Caribe +0,34; Andina +0,02; Pacífica −0,05. Regla: cada resultado se reporta por región natural y por país antes de cualquier modelo conjunto.
3. **Lo simple suele ganar.** Pendiente sola ≈ mapa SGC; regla de un umbral ≥ curva E–D; lineal ≥ no lineal; área sola ≈ modelo con covariables. Regla: **toda comparación de un modelo complejo incluye la línea base simple**, y el complejo solo gana si el IC de la diferencia excluye 0 fuera de muestra.
4. **Un AUC alto engaña con tasa base alta o por fuga.** Regla: reportar tasa base, usar validación que deja bloques completos fuera (departamento/país) y declarar los insumos que comparten origen con el objetivo.
5. **Herramientas que invierten el veredicto.** `consolidar_corrida.py` marcaba «significativo» lo que era significativamente peor. Regla: todo consolidador muestra la dirección del efecto.
6. **Las unidades no son réplicas independientes** (≈ 3 estaciones efectivas por región). Regla: bootstrap o permutación por bloques espaciales; nunca errores estándar por municipio o estación.
7. **El sesgo de reporte es la explicación alternativa más fuerte** y la UNGRD es el único registro de eventos que verificamos. Regla: sin un registro de eventos comparable verificado en el país, **no se hace análisis evento-exposición** allí (solo lo que no depende de eventos).

## 2. Alcance de países y orden

| Nivel | Países | Motivo | Estado de normas |
|---|---|---|---|
| A | Perú, Ecuador | Ya hay corpus normativo y de zonificación (204 y 395 fragmentos; 1.884 y 512 filas de zonificación); comparten Andes y Pacífico con Colombia | Registrados; Perú corpus mixto, Ecuador vigencia no verificada |
| B | Chile, Bolivia | Chile tiene fuentes geológicas identificadas (SERNAGEOMIN); Bolivia no se ha inventariado | Sin corpus |
| C | Venezuela, Panamá, Brasil | Frontera/cuenca compartida; Venezuela con el doblete sísmico de 2026 ya registrado en memoria como sensible | Sin corpus; Venezuela no se publica sin revisión |

Solo el nivel A entra en la primera ronda. Los demás exigen inventario de fuentes (como el de `INVENTARIO_FUENTES_DOMINIOS_2026-11.md`) antes de cualquier descarga.

## 3. Qué se replica y qué no

**Insumos independientes del país (se pueden replicar sin registro nacional):** DEM Copernicus 30 m, HAND derivado, ESA WorldCover, CHIRPS, red vial de OpenStreetMap, humedad ESA CCI, índices ONI/TNA, población gridded. Todos con los límites ya documentados (HAND de 90 m, OSM voluntario, humedad sin dato en relieve complejo, CHIRPS no independiente de las normales).

**Insumos que dependen de cada país y hoy NO están verificados para Perú ni Ecuador:** registro de eventos/emergencias (equivalente a la UNGRD), caudales (equivalente a IDEAM), inventario de movimientos en masa (equivalente a SIMMA), mapa oficial de amenaza (equivalente a SGC), censo/índice de necesidades. Para Perú hay candidatos sin verificar (INGEMMET GEOCATMIN, CENEPRED/SIGRID, ANA, SENAMHI, INDECI/SINPAD no encontrado); para Ecuador no se ha buscado nada.

### 3.1 Familias de pruebas, por orden, y qué país las puede correr

| Id | Prueba (réplica de) | Orden | Insumos nacionales requeridos | Se puede correr con solo insumos globales |
|---|---|---|---|---|
| P1 | Terreno: distribuciones de pendiente, HAND, cobertura por región natural, comparadas con Colombia | 1.º | Ninguno | **Sí** |
| P2 | Sesgo de CHIRPS frente a pluviómetros del país | 1.º/2.º | Pluviómetros (SENAMHI, INAMHI) | No |
| P3 | Amenaza oficial frente a eventos (réplica de SGC–UNGRD, K1–K4) | 2.º | Mapa oficial + registro de eventos | No |
| P4 | Exposición vial a terreno bajo (réplica de V1) | 2.º | Registro de eventos | Parcial: la exposición sí, la validación no |
| P5 | Susceptibilidad por ML con validación dejando país/región fuera | 2.º | Inventario de movimientos en masa | No |
| P6 | Regionalización de caudales con modelo entrenado en Colombia y probado en el país vecino (transferibilidad) | 2.º | Caudales máximos con cuenca delineable | No |
| P7 | Rezagos ONI/TNA → lluvia (CHIRPS), lineal estacional frente a no lineal | 3.º | Ninguno | **Sí** |
| P8 | Coherencia espacio-temporal de anomalías de caudal y modulación por ENSO | 3.º | Caudales mensuales | No |
| P9 | Umbrales lluvia-duración (regla simple frente a curva E–D) | 3.º | Eventos con fecha | No |
| P10 | Comparación normativa sísmica: parámetros de zona, espectro, suelo, en NSR-10, E.030 y NEC-SE-DS | — | Texto verificado y vigencia fechada | Sí, con el corpus actual **solo en la parte 2026 de la E.030** |

**Primera ronda propuesta (sin registros nacionales):** P1 y P7, más P10 en su parte verificable. Es lo único que se puede hacer sin resolver la verificación de fuentes nacionales.

## 4. Control del sesgo (obligatorio en toda prueba)

| Fuente de sesgo | Qué puede pasar | Control fijado de antemano |
|---|---|---|
| **Sesgo de reporte** | Más reportes ≠ más riesgo | Indicador de capacidad de reporte por país; análisis de sensibilidad; una prueba que depende de eventos sin ese control se marca «no concluyente». Reconocido: en Colombia el indicador es débil (§1.2) |
| **Fuga por origen común** | CHIRPS se construye con estaciones; SGC usa pendiente; SIMMA sin fecha y cobertura 2021 | Cada prueba declara qué insumos comparten origen con el objetivo; no se llama «validación» a una comparación con un insumo derivado de los mismos datos |
| **Autocorrelación espacial** | Pocas unidades efectivas | Remuestreo por bloques (departamento/provincia o bloques de 1°); IC95 % por bloques; reportar el número de bloques; con menos de 5 bloques el resultado es «indicativo» (lección del índice vial andino con 3 bloques) |
| **Heterogeneidad regional** | Un efecto del Caribe no es del continente | Resultado por región natural **antes** del modelo conjunto; el conjunto solo se reporta si la heterogeneidad se examinó |
| **Comparaciones múltiples** | 120 pares → ~10 % de falsos candidatos | Benjamini-Hochberg q < 0,10 para exploración; Holm para confirmatorias; un barrido solo genera hipótesis |
| **Tasa base** | Resultado casi constante (93–96 % con evento) | Reportar tasa base y potencia antes de interpretar; si la tasa base > 90 %, la prueba se declara sin potencia |
| **Escala (MAUP)** | Municipio ≠ lote; las unidades administrativas difieren por país | Reportar la unidad y su tamaño mediano por país; comparar solo estandarizado por rango (percentil intra-país) y nunca valores absolutos de «terreno bajo» entre llanura y montaña |
| **Cobertura de OpenStreetMap** | Mapeo voluntario desigual | Reportar km de vía por 100 km²; controlar o excluir unidades por debajo de un mínimo fijado antes (≥ 5 km, como en V1) |
| **Desplazamiento de dominio** | Un modelo entrenado en Colombia no vale en otro clima/geología | Prueba de transferibilidad explícita antes de usar un modelo colombiano en otro país: error del modelo transferido frente a la línea base simple y frente a un modelo del propio país; si el transferido no iguala a la línea base, no se usa |
| **Sesgo de selección de literatura** | Citar solo lo que apoya | Búsqueda con las consultas fijadas antes (como en `PROTOCOLO_LITERATURA_CAUDALES.md`), lista completa guardada antes de cribar, criterios de inclusión previos |
| **Sesgo del evaluador (yo)** | Interpretar a favor | Criterios y umbrales de efecto fijados antes; un veredicto «no se confirma» se publica igual; los análisis post hoc se rotulan «posteriores, no preregistrados» |
| **Sesgo de supervivencia** | Países/regiones con datos son las más organizadas | Reportar cobertura de datos por región y excluir del resumen las regiones sin dato, nombrándolas |

## 5. Machine learning: reglas

1. **Siempre con línea base simple** (pendiente sola, área sola, climatología, regla de un umbral) evaluada con la misma partición.
2. **Validación que deja un bloque completo fuera:** departamento dentro de un país y, para transferibilidad, **país completo** (entrenar en Colombia, probar en Perú, y al revés), con purga espacial cuando sea posible.
3. **Reporte de calibración**, no solo AUC: tasa base, curva de calibración y desempeño por región. El caso Andina/Pacífica (AUC alto con concordancia nula o negativa con el mapa oficial) es la advertencia.
4. **Salida de ranking, no de probabilidad**, mientras los puntos de fondo sean aleatorios (como el índice municipal actual).
5. **Complejidad creciente solo si hay datos:** con ~500 meses de lluvia o ≈ 250 de temperatura no se usan redes profundas (conclusión ya documentada).
6. **Importancia de variables** se interpreta como asociación, nunca causal; si dos variables comparten origen (p. ej. pendiente y mapa), se reporta explícitamente.
7. **Prohibido ajustar umbrales de decisión mirando el conjunto de prueba.**
8. **Quien modele el segundo país no reentrena con datos del país de prueba** sin declarar un nuevo protocolo.

## 6. Criterios de decisión (fijados ahora)

| Pregunta | Criterio de «se replica» | Criterio de «no se replica» | En otro caso |
|---|---|---|---|
| Asociación (2.º orden) | |ρ parcial| ≥ 0,15, mismo signo que Colombia, IC por bloques excluye 0 | IC incluye 0 **y** el IC es más estrecho que ±0,15 (se puede afirmar ausencia práctica) | «No concluyente» (potencia insuficiente) |
| Mejora de un modelo | ΔError con IC95 % que excluye 0 a favor del complejo, fuera de muestra | IC incluye 0 → se conserva la línea base | — |
| Transferibilidad | El modelo colombiano iguala o mejora al modelo simple del país | Peor que el simple | — |
| Dinámica (3.º) | Mejora fuera de muestra con corrección de Holm sobre las familias | Sin mejora → lineal estacional | — |

Para afirmar **ausencia** de efecto se usa una prueba de equivalencia (TOST) con margen ±0,15, no la falta de significancia (lección: «el IC incluye 0» ≠ «no hay efecto»).

## 7. Comparación normativa y uso de artículos científicos

**Comparación de normas (P10).** Solo entre textos con vigencia fechada y verificada. Hoy: NSR-10 (Colombia, vigente con la cadena registrada), Perú E.030 solo en los capítulos 2–4 de la RM 183-2026 (resto 2019, no usar como vigente), Ecuador NEC-SE-DS (vigencia no verificada). La comparación se hace sobre parámetros, no sobre cumplimiento: zona/aceleración, tipo de suelo, forma espectral, factores de reducción. Cada celda lleva fuente, artículo, edición y fecha. Una diferencia numérica no se interpreta como mayor o menor seguridad sin analizar el método de cada norma.

**Admisión de artículos científicos.** Un artículo entra al análisis solo si:
1. Está verificado por `verificar_referencias.py` (busca el título en OpenAlex y guarda el registro real con su similitud de título y si el autor coincide; el script no fija un umbral, así que **aquí se fija: similitud ≥ 0,95 y autor coincidente**) o leído por una persona;
2. Se pudo leer el texto (o el resumen se marca como tal; no se extraen ecuaciones de un resumen automático);
3. Declara su rango de validez (área, región, clima) y el caso del país objetivo cae dentro (el caso peruano de la Amazonía quedó fuera: cero estaciones dentro del rango);
4. Declara datos y método de forma que se pueda contrastar.

Los resultados de un artículo se usan como hipótesis o referencia comparada; nunca como parámetro de una respuesta sin la etiqueta de referencia internacional.

## 8. Fases con puertas de salida

| Fase | Contenido | Puerta de salida | Permiso requerido |
|---|---|---|---|
| F0 | Este protocolo | Revisado y fijado (commit anterior a cualquier cálculo) | — |
| F1 | Verificar fuentes nacionales de Perú y Ecuador: eventos, caudales, inventario de movimientos, mapa de amenaza, licencia y formato | Tabla verificada con enlace y fecha; decisión por prueba P2–P9 | Ninguno (lectura). Antes de bajar un archivo: **nombre, fuente y tamaño** |
| F2 | P1 y P7 con insumos globales, Colombia vs. Perú vs. Ecuador | Informe de resultados con IC por bloques y heterogeneidad | Permiso de descarga de DEM/CHIRPS (tamaño a declarar) |
| F3 | P10 con texto verificado | Tabla comparativa con vigencia | Verificar RM 183-2026 completa y vigencia NEC-SE-DS |
| F4 | P3–P6, P8, P9 en los países donde F1 dio fuente verificada | Un informe por prueba; las no ejecutables se registran como «bloqueadas por fuente» | Permiso de descarga por fuente |
| F5 | Síntesis: qué se replica, qué no, qué queda abierto | Documento y issue; ninguna propuesta normativa | — |

## 9. Lo que NO se hará
- Declarar una «norma continental» o recomendarla: no es un entregable técnico de este proyecto y exigiría revisión de especialistas y entidades.
- Interpretar un resultado extranjero con el significado colombiano, o viceversa.
- Descargar archivos sin declarar nombre, fuente y tamaño.
- Mezclar datos de países en un modelo único sin haber examinado antes la heterogeneidad por país.
- Presentar un análisis post hoc como confirmatorio.
- Usar un registro de eventos no verificado para medir sesgo de reporte.
- Publicar contenido del doblete sísmico de Venezuela sin revisión previa.

## 10. Riesgos y límites declarados
- Perú y Ecuador pueden carecer de un registro de eventos comparable; entonces las pruebas P3, P4, P9 quedarán bloqueadas y no se sustituirán por un indicador inventado.
- Los insumos globales heredan los límites ya medidos (HAND de 90 m, OSM voluntario, CHIRPS no independiente de estaciones, humedad sin dato en relieve complejo).
- La definición de «primer orden» de la sección 1.1 es provisional.
- La potencia estadística puede ser baja con pocos bloques; en ese caso el resultado será «indicativo».
- Los informes de Colombia fueron redactados por el mismo proceso que ahora fija este protocolo; una revisión externa independiente sigue siendo recomendable antes de cualquier publicación.
