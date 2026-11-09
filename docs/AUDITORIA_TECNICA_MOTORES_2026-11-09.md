# Auditoría técnica de los motores de cálculo de StructAI/Construdata

**Fecha:** 9 de noviembre de 2026. **Alcance:** 19 paquetes de `packages/`, API y scripts asociados.

## 1. Método y límites de la evidencia

- Escaneo estático de 19 paquetes (líneas, funciones, presencia de álgebra lineal, logaritmos, optimización, ML, geoespacial, llamadas externas, constantes y citas normativas). Un escaneo por texto indica presencia, no corrección.
- Ejecución de las suites de prueba de los 12 motores y del orquestador: 762 pruebas, 0 fallas (motor-acero-frio 7, motor-analisis 10, motor-apu 31, motor-aquai 83, motor-concreto 287, motor-deformacion 55, motor-estructural 18, motor-geopot 65, motor-gerencia 38, motor-topovia 18 antes de esta auditoría, motor-vias 62, motor-vulnerabilidad-vivienda 17, orquestador 71). No se ejecutaron las pruebas de construdata, eval-stats, rag-audit-kit, bim-intelligence, yolo ni ai-gateway. Pruebas que pasan demuestran consistencia con lo que el autor esperaba, no corrección física.
- Verificación independiente de un motor (AASHTO-93 en motor-topovia) contra la raíz exacta de la ecuación (Brent). Resultado en la sección 3.
- Lectura dirigida de los módulos citados. Lo no leído se marca como tal en la tabla.

## 2. Inventario

19 paquetes con código (≈ 26.000 líneas): 12 motores de dominio, 1 integrador y 6 paquetes de soporte. Solo 6 motores están expuestos por la API (aquai, estructural, geopot, gerencia, vias, vulnerabilidad_vivienda). Los motores estructuralmente más rigurosos (motor-concreto, orquestador, motor-analisis, motor-acero-frio, motor-topovia, eval-stats) no tienen router en apps/api. Los modelos de aprendizaje supervisado (sustitutos LightGBM de zapata y muro) y todo el procesamiento geoespacial (HAND, CHIRPS, fluvial, SECOP) viven en scripts/, no en paquetes con pruebas.

| Paquete | Rol | Líneas | Funciones | Pruebas | Dominio |
|---|---|---|---|---|---|
| motor-concreto | Motor | 4.025 | 258 | 287 | Concreto reforzado NSR-10 Título C, zapatas, pórticos vectorizados, flota de construcción, excavación (Bishop, pantallas, balance de tierras) |
| motor-vias | Motor | 3.774 | 156 | 62 | Diseño geométrico, pavimentos por tablas, mantenimiento, materiales NTC |
| motor-aquai | Motor | 3.001 | 73 | 83 | Acueducto: demanda, Hazen-Williams por tramo, PTAP, memoria PDF, IDF |
| motor-apu | Motor | 1.475 | 65 | 31 | Catálogo de precios INVIAS/APU y recomendador de insumos (TF-IDF + vecinos) |
| motor-geopot | Motor | 1.327 | 81 | 65 | Zonificación sísmica (por departamento), laboratorios: concreto, suelos USCS/AASHTO, Proctor, CBR, agregados, diseño de mezcla ACI |
| motor-deformacion | Motor | 1.241 | 89 | 55 | Deflexiones: teoría de vigas, BVP, elementos finitos de barra, modos |
| motor-topovia | Motor | 755 | 20 | 22 | Poligonales, volúmenes, curvas horizontales, pavimento flexible AASHTO-93 |
| motor-gerencia | Motor | 546 | 38 | 38 | KPIs de obra, regresión lineal, anomalías, pronóstico |
| motor-estructural | Motor | 465 | 15 | 18 | Nudos desde IFC → fuerzas (load_engine); red neuronal PINN eliminada por ser código muerto |
| motor-vulnerabilidad-vivienda | Motor | 387 | 7 | 17 | Índice de vulnerabilidad de vivienda |
| motor-analisis | Motor | 178 | 13 | 10 | Pórtico plano (rigidez directa) |
| motor-acero-frio | Motor | 93 | 6 | 7 | Acero conformado en frío (MVP) |
| orquestador | Integrador | 1.579 | 64 | 71 | Diseño integral de edificio: pórticos, MILP por pisos, acoplamiento entre motores |
| construdata | Datos/plugins | 4.723 | 176 | no ejecutadas | Clientes de datos abiertos (IDEAM, IGAC, DIVIPOLA, INVIAS), plugins del chat, noticias |
| bim-intelligence | Soporte | 2.498 | 115 | sin pruebas | Lectura/análisis BIM |
| rag-audit-kit | Soporte | 276 | 10 | no ejecutadas | Auditoría de calidad del RAG |
| ai-gateway | Soporte | 237 | 13 | sin pruebas | Enrutamiento de modelos de lenguaje |
| eval-stats | Soporte | 214 | 11 | no ejecutadas | Bootstrap y estadística pareada para evaluación |
| yolo | Soporte | 210 | 6 | sin pruebas | Detección YOLOv11n (InfraCortex, desactivada) |

## 3. Hallazgos verificados y pendientes

| Id | Severidad | Ubicación | Hallazgo | Estado |
|---|---|---|---|---|
| H1 | CRÍTICO | motor-topovia · calcular_sn_flexible | El solver AASHTO-93 sumaba +0,05 / restaba 0,01 hasta que log10(W18) caía a 0,001, usaba un 4,2 fijo en lugar de (po − 1,5) y tomaba ZR = −1,037 (R = 0,85) para cualquier confiabilidad no tabulada. Con po = 4,5 y pt = 2,5 daba SN = 4,46 frente a 4,56 de la raíz exacta (2,2 % por debajo, lado inseguro). Con R = 0,80 devolvía lo mismo que con 0,85. Con W18 = 10¹² devolvía 11,0 sin avisar que no convergió. | CORREGIDO hoy: raíz exacta (Brent), ZR por inversa de la normal para cualquier R en (0,5; 1), validación de dominio, ValueError si no hay solución. 4 pruebas nuevas rojas→verdes; 22 pasan. |
| H2 | ALTO | motor-aquai · hidraulica.py:46 | COEF_HAZEN_WILLIAMS.get(material, 130): un material desconocido o mal escrito recibe C = 130 sin aviso. Un C sobreestimado subdimensiona diámetros. | PENDIENTE (Fase 1): lanzar error o exigir C explícito. |
| H3 | ALTO | motor-geopot · lab_concreto.py:185 | FC_MIN_NSR10.get(zona_sismica, 21.0): una zona no reconocida recibe 21 MPa como mínimo normativo. | PENDIENTE (Fase 1): error explícito para zona desconocida. |
| H4 | ALTO | motor-vias · pavimentos.py:277-282, 498-503 | resultado.get('espesor_*', 0): si el cálculo no devuelve una capa, el informe muestra espesor 0 en vez de fallar. | PENDIENTE (Fase 1). |
| H5 | ALTO | motor-aquai · ras2000_tablas.py | Las curvas IDF están declaradas 'de referencia/ilustrativas' en todas las regiones, sin cita verificable. Cualquier caudal de diseño pluvial que dependa de ellas no es dimensionable. | PENDIENTE (Fase 1): bloquear su uso en resultados de diseño hasta cargar IDF oficiales del IDEAM. |
| H6 | MEDIO | motor-geopot · sismica.py | Zonificación a nivel de departamento: el Apéndice A-4 de NSR-10 define Aa/Av por municipio y la microzonificación local exige resolución de sitio. | PENDIENTE (Fase 2): usar la tabla municipal ya ingestada. |
| H7 | MEDIO | motor-gerencia · ml_engine.py | Se presenta como 'ML' una regresión lineal de mínimos cuadrados escrita a mano, sin validación fuera de muestra ni intervalos. | PENDIENTE (Fase 4): intervalos de predicción y validación cruzada temporal. |
| H8 | MEDIO | Arquitectura | Los motores con mayor rigor (concreto, orquestador, análisis, acero frío, topovía, eval-stats) no están expuestos en la API; los usuarios acceden a motores de menor rigor. | PENDIENTE (Fase 3). |
| H9 | MEDIO | bim-intelligence, ai-gateway, yolo | Sin pruebas (2.945 líneas). | PENDIENTE (Fase 6). |

## 4. Verificación matemática por categoría

| Capacidad | Evidencia | Nivel |
|---|---|---|
| Fórmulas dinámicas (parametrización) | Presentes en todos los motores de cálculo; los coeficientes normativos están embebidos en tablas y constantes (motor-vias: 542 citas, motor-geopot: 104, motor-aquai: 163). Un cambio de norma exige editar código, no datos. | Parcial |
| Cálculo matricial | Rigidez directa y MEF: motor-analisis, motor-deformacion, orquestador (21 usos). Ausente: redes hidráulicas (Hardy-Cross/gradiente), análisis modal 3D de edificio, tensores de esfuerzo en suelos. | Parcial |
| Logaritmos y escalas | AASHTO-93 (topovia), concreto (7 usos), idf del TF-IDF (apu). Ausentes: ESAL por factor de equivalencia logarítmico en motor-vias (usa tablas), curvas granulométricas semilog, consolidación (Cc·log), intensidad sísmica (Gutenberg-Richter), decaimiento exponencial de calidad de agua. | Parcial |
| Machine learning | Un recomendador de vecinos más cercanos (apu), sustitutos LightGBM (scripts), YOLO desactivado, regresión lineal a mano (gerencia). No hay validación de dominio ni intervalos de predicción en producción. | Débil |
| Optimización | MILP/LP (concreto, orquestador), brentq, Nelder-Mead. Correcto y bien probado en excavación y orquestador. | Fuerte |
| Incertidumbre | FOSM log-normal en taludes y bootstrap en eval-stats. No hay propagación de incertidumbre transversal entre motores. | Débil |

## 5. Alcance por disciplina

| Disciplina | Cobertura | Detalle y vacíos |
|---|---|---|
| Estructuras (concreto, pórticos, nudos) | Alta | Rigidez directa, MILP, deflexiones, nudos IFC. Falta: acero estructural general, mampostería, madera, análisis dinámico modal 3D, fundaciones profundas. |
| Geotecnia | Media | Zapatas, taludes Bishop, pantallas, laboratorios. Falta: pilotes, licuación, consolidación/asentamientos, capacidad portante general, estabilidad sísmica de laderas. |
| Hidráulica y sanitaria | Media-baja | Hazen-Williams por tramo y PTAP. Falta: solver de redes malladas, transitorios (golpe de ariete), alcantarillado, hidrología con IDF oficiales. |
| Vías y transporte | Media | Geometría, pavimento AASHTO-93 (topovia), tablas (vias). Falta: pavimento rígido mecanístico, tránsito/ESAL dinámico, puentes, ruteo logístico. |
| Ambiental | Baja | Datos de clima y deforestación como entradas; sin motores de calidad de agua, aire, huella ambiental de obra más allá del combustible de excavación. |
| Geoespacial | Baja en producto, alta en investigación | HAND, CHIRPS, fluvial y susceptibilidad en scripts y plugins; sin paquete con pruebas ni API. |
| Industrial / minería | Nula | Sin motores. |
| Eléctrica | Nula | Una mención aislada de conductores; sin motor. |
| Logística e infraestructura de obra | Baja | Balance de tierras (LP) y flota; sin ruteo (VRP) ni programación de recursos. |
| Costos y gerencia | Media | APU, precios reales INVIAS/ICOCED, KPIs, pronóstico lineal. Falta: EVM completo, riesgo Monte Carlo de cronograma. |

## 6. Tabla de auditoría por motor

Las celdas con 'n/d' indican que este informe no verificó ese aspecto, no que no exista.

| Motor | Dominio / tema | Fórmulas dinámicas | Cálculo matricial | Logaritmos | ML | Datos | Estado / brechas | Investigación | Resultados | Discusiones | Discretización | Variables | Protocolos | Enmiendas | Descubrimientos | Frameworks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| motor-concreto | Concreto reforzado, zapatas, excavación | Sí: parámetros de entrada; coeficientes NSR en tablas | Parcial: solo vía orquestador | Sí (7 usos) | No en paquete (sustituto LightGBM en scripts) | Sintéticos + catálogos (flota ANDI/FECOC) | Fuerte; sin API; Rankine sin agua; Bishop con dominio acotado | Docs diseno_generativo | Rankings sintéticos rotulados | Sí, con limitaciones declaradas | Dovelas Bishop, malla de círculos | Geometría, suelo, c/φ/γ, kh | NSR-10 C, H.2.4-1 | Errores corregidos en 2 revisiones | FS depende de la cota de profundidad si φ=0 y sismo | numpy, scipy (HiGHS, brentq), shapely |
| orquestador | Diseño integral edificio | Sí | Sí (21 usos) | No | No | Sintéticos | Sólido; no expuesto | Docs matriz de motores | Ranking de alternativas | Parcial | Pórtico por pisos | Secciones, cargas | NSR-10 | n/d | n/d | numpy, scipy (MILP) |
| motor-analisis | Pórtico plano | Sí | Sí (rigidez directa) | No | No | n/d | Sin API; 2D solamente | n/d | 10 pruebas | No | Elementos de barra | Geometría, cargas | n/d | n/d | n/d | numpy |
| motor-deformacion | Deflexiones, BVP, MEF, modos | Sí | Sí (solve, eigh) | No | No | n/d | Bien cubierto; sin validación contra soluciones cerradas en este informe | n/d | 55 pruebas | No | BVP adaptativo (tol 1e-9), MEF | Apoyos, EI, cargas | n/d | n/d | n/d | scipy (solve_bvp, eigh) |
| motor-estructural | Nudos IFC → fuerzas | Sí (fórmulas clásicas) | Sí (rotaciones R3) | No | No (PINN eliminada) | IFC | Depende de ifcopenshell; 18 pruebas | Registrado en docstring | n/d | No | n/d | Topología del nudo | n/d | Eliminación de código muerto 2026-08-26 | El veredicto nunca usó la red neuronal | ifcopenshell, numpy |
| motor-aquai | Acueducto, PTAP, IDF | Parcial: C de Hazen-Williams por material con valor por defecto 130 | No | Poco (2) | No | Tablas RAS 2000; IDF 'de referencia/ilustrativos' | Sin solver de redes; IDF sin fuente verificable | n/d | 83 pruebas | No | Por tramo | Q, D, L, C | RAS 2000 | n/d | IDF marcados explícitamente como ilustrativos | python puro |
| motor-vias | Geometría vial, pavimentos, mantenimiento | Parcial: tablas, 11 defaults numéricos | No | No | No | NTC/INVIAS en código (542 citas; 59 marcas 'referencia/sin verificar') | Pavimentos por tablas; resultado.get(...,0) puede reportar espesor 0 | n/d | 62 pruebas | No | Tablas | CBR, ESAL, tránsito | INVIAS, NTC | n/d | n/d | python puro |
| motor-topovia | Poligonales, volúmenes, curvas, AASHTO-93 | Sí (tras corrección) | No | Sí (AASHTO-93) | No | n/d | Corregido hoy: solver burdo, fallback silencioso de ZR, 4,2 fijo en término de serviciabilidad | Auditoría 2026-11-09 | Ver sección 3 | Sí | Iteración → raíz exacta | W18, MR, R, So, po, pt | AASHTO-93 | 4 pruebas nuevas | Con po=4,5 el SN salía 2 % bajo | scipy.optimize.brentq |
| motor-geopot | Sísmica (depto.) y laboratorios | Parcial: tablas; fc mínimo por zona con 21 MPa por defecto | No | No | No | Tabla por departamento (resolución gruesa) | Sísmica a nivel departamento, no municipio ni sitio; default 21 MPa en zona desconocida | n/d | 65 pruebas | No | n/d | Ensayos de laboratorio | NTC, ASTM, NSR-10 | n/d | n/d | python puro |
| motor-apu | Precios y recomendador de insumos | Sí | Sí (vectores TF-IDF) | Sí (idf) | Vecinos más cercanos con numpy; acierto@10 de 0,78–0,84 | INVIAS 2026-1 (324 actividades con composición) | Catálogo grande embebido; vigencia manual | scripts/precios | Evaluación offline | Sí | n/d | Insumos, rendimientos | INVIAS | n/d | n/d | numpy |
| motor-gerencia | KPIs, pronóstico, anomalías | Sí | No | No | Regresión lineal escrita a mano; z-score | Instantáneas de proyecto | 'ML' = regresión simple; sin validación fuera de muestra | n/d | 38 pruebas | No | Series temporales | KPIs | n/d | n/d | n/d | python puro |
| motor-vulnerabilidad-vivienda | Vulnerabilidad de vivienda | Parcial | No | No | No | n/d | Índice sin calibración contra daños observados (no verificado) | n/d | 17 pruebas | No | n/d | Atributos de vivienda | n/d | n/d | n/d | python puro |
| motor-acero-frio | Acero conformado en frío | Parcial | No | No | No | n/d | MVP de 93 líneas | Issue #81 | 7 pruebas | No | n/d | Perfil, espesor | AISI/NSR-10 F (no verificado) | n/d | n/d | python puro |
| eval-stats | Estadística de evaluación | Sí | No | No | Bootstrap, pareadas | Salidas de evaluación | Sin API | Plan maestro eval | n/d | n/d | n/d | n/d | n/d | n/d | n/d | numpy |
| construdata (datos) | Clientes de datos abiertos y plugins | No aplica | No | No | No | IDEAM, IGAC, DIVIPOLA, INVIAS, NOAA ONI, noticias (113 referencias a servicios externos) | 30 bloques 'except Exception'; URLs fijas en código | n/d | n/d | n/d | n/d | n/d | n/d | n/d | n/d | httpx/urllib |
| Sustitutos (scripts/) | Zapata y muro (LightGBM) | No | No | No | Sí (0 inseguros en 5.000 casos; brecha mediana 1,3 %) | Sintéticos | Fuera de paquetes; sin guardia de dominio documentada en producción | Docs escalamiento | Resumen en docs | Sí | n/d | Geometría, cargas | n/d | n/d | n/d | LightGBM |

## 7. Plan por fases (orden de importancia)

### Fase 1 — Seguridad de resultados (inmediata)

Eliminar fallbacks silenciosos y entradas fuera de dominio: H1 (hecho), H2, H3, H4, H5. Barrido automático de `.get(x, número)`, `except Exception` y valores por defecto en los 12 motores. Criterio de salida: ningún motor devuelve un número de diseño con una entrada no reconocida; todo error es explícito.

Estimación: 1–2 días.

### Fase 2 — Verificación independiente

Pruebas de referencia con solución cerrada o fuente externa para concreto, deformación, aquai, vias y geopot; pruebas de propiedad (monotonicidad, homogeneidad dimensional); unidades con pint en las interfaces. Criterio: cada motor tiene ≥ 3 casos con respuesta independiente.

Estimación: 1–2 semanas.

### Fase 3 — Exposición y contratos

Routers para motor-concreto, orquestador, motor-analisis, motor-topovia, motor-acero-frio; esquema de respuesta con banderas de dominio, supuestos y fuente normativa; regresión dorada en CI.

Estimación: 1–2 semanas.

### Fase 4 — Modelos predictivos gobernados

Guardia de dominio (detección fuera de distribución) y intervalos conformales para sustitutos LightGBM; reemplazar la regresión manual de gerencia; ficha de modelo por cada sustituto; nunca reemplazar la verificación de ingeniería.

Estimación: 2–3 semanas.

### Fase 5 — Motores faltantes

En orden de impacto en seguridad: asentamientos/consolidación, pilotes, licuación, redes hidráulicas (gradiente matricial), puentes, sísmica municipal (A-4), luego eléctrica, minería y logística.

Estimación: meses.

### Fase 6 — Plataforma

Pruebas para bim-intelligence, ai-gateway, yolo; paquete geoespacial con pruebas; resiliencia de APIs externas (reintentos con tope, caché con vigencia, validación de esquema, circuito abierto); rendimiento y escalabilidad de las consultas.

Estimación: continuo.

## 8. Elementos no mencionados que conviene cubrir

- Consistencia dimensional y de unidades (kN vs. N, mm vs. m, MPa vs. kPa) en las fronteras entre motores.
- Vigencia normativa: versionado de tablas con fecha, decreto y alcance; alerta cuando una norma cambia (ya falló dos veces con Perú E.030).
- Trazabilidad de cada número a su fuente (norma, artículo, edición) en la salida del motor.
- Propagación de incertidumbre de extremo a extremo (parámetros del suelo → capacidad → costo).
- Reproducibilidad: semillas, versiones de bibliotecas fijadas y resultados deterministas.
- Ficha de modelo y guardia de dominio para todo sustituto de aprendizaje.
- Aviso de responsabilidad profesional en toda salida de diseño (ya existe en el chat; extender a la API).
- Condicionamiento numérico de matrices (número de condición, singularidad por apoyos insuficientes).
- Idempotencia y concurrencia en la API; límites de tiempo por cálculo.
- Licenciamiento y privacidad de los datos de terceros (SECOP, SIRNA, SISBEN).

## 9. Banco de preguntas para el auditor

### 1. Integridad física y matemática (cero alucinaciones)

1. ¿Cada fórmula reproduce un caso resuelto en la norma o en un texto de referencia con tolerancia declarada? ¿Cuál es la fuente de cada caso?
2. ¿La salida cumple homogeneidad dimensional? ¿Qué ocurre si se mezclan kN y N, o MPa y kPa, en una entrada?
3. ¿Existe algún valor por defecto que sustituya una entrada no reconocida (`.get(x, número)`)? ¿Alguno es un valor normativo?
4. ¿El motor falla ruidosamente cuando un solver no converge, o devuelve el último valor iterado?
5. ¿Cada coeficiente embebido tiene fuente, edición y artículo? ¿Cuántos están marcados 'referencia' o 'no verificado'?
6. ¿Las conservaciones (equilibrio de fuerzas y momentos, balance de masa) se verifican como invariantes en las pruebas?
7. ¿Los modelos de aprendizaje alguna vez producen el valor final de diseño, o solo una estimación sujeta a verificación determinista?

### 2. Casos límite

1. ¿Qué devuelve el motor con cero, negativo, NaN, infinito o un valor 10⁶ veces mayor al esperado?
2. ¿Qué pasa en el borde del dominio (φ = 0, pendiente 90°, relación luz/altura extrema, caudal nulo)?
3. ¿Hay discontinuidades en las tablas por tramos que produzcan saltos de diseño por un cambio mínimo de entrada?
4. ¿El resultado es monótono donde la física lo exige (más carga ⇒ más armadura)?
5. ¿Qué ocurre con la sensibilidad a la malla o a la tolerancia (Bishop, BVP, MEF)? ¿Se reporta?
6. ¿Se degrada con gracia cuando el dominio de búsqueda condiciona el resultado (como `en_borde_dominio`)?

### 3. Lógica oculta y código trampa

1. ¿Existen ramas que nunca se ejecutan (código muerto, como la PINN eliminada) que aparenten capacidad?
2. ¿Hay constantes disfrazadas en funciones (factores de seguridad, topes, mínimos) que no aparezcan en la interfaz?
3. ¿Algún `try/except` amplio oculta un fallo y deja un resultado parcial?
4. ¿Hay semillas aleatorias fijas o valores calibrados con los mismos datos con que se evalúan?
5. ¿Las pruebas comprueban el valor correcto o el valor que el código ya producía?
6. ¿Existen ramas que se comportan distinto en CI y en producción (variables de entorno, claves)?

### 4. Coherencia entre disciplinas (acoplamiento)

1. ¿Las cargas que la estructura entrega a la cimentación son las mismas que usa el motor de zapata (combinaciones, signos, unidades)?
2. ¿La amenaza sísmica usada en vulnerabilidad, estructura y geotecnia viene de una sola fuente y un solo nivel de resolución?
3. ¿El costo del APU responde al mismo diseño (cantidades) que produjo el motor estructural?
4. ¿Un cambio de un parámetro se propaga a todos los motores que lo consumen, o hay copias?
5. ¿El hidráulico y el vial comparten la misma hidrología (IDF) o tienen constantes separadas?

### 5. Rendimiento y escalabilidad

1. ¿Cuál es el tiempo y la memoria por llamada en el peor caso (motor-concreto: 287 pruebas tardan 185 s)?
2. ¿Hay límites de tiempo por cálculo y cancelación segura?
3. ¿Los solvers escalan con el número de pisos, vanos o dovelas? ¿Se midió la curva?
4. ¿Los cálculos son idempotentes y cacheables por hash de entrada?
5. ¿Qué ocurre con 100 usuarios simultáneos sobre el mismo recurso compartido?

### 6. Fallas de datos geoespaciales

1. ¿Se verifica el sistema de referencia (EPSG) de cada capa y se transforma explícitamente?
2. ¿Cómo se tratan los nulos, los valores centinela (−9999) y las celdas fuera de cobertura?
3. ¿La resolución del dato cubre la escala del fenómeno (departamento vs. municipio vs. predio)?
4. ¿Hay sesgo de muestreo (estaciones concentradas en zonas pobladas)?
5. ¿La geometría se valida (polígonos inválidos, autointersecciones, orden de coordenadas lat/lon)?
6. ¿Existe una lista de huecos de cobertura (qué municipios o cuencas no tienen dato) que acompañe cada resultado?

### 7. Fallas de datos web y APIs externas (excluye OpenAI y Groq)

1. ¿Cada cliente (IDEAM, IGAC, DIVIPOLA, INVIAS, NOAA) tiene tiempo de espera, reintentos con tope y retroceso exponencial?
2. ¿Se valida el esquema de la respuesta antes de usarla, o un cambio de columnas rompe en silencio?
3. ¿Los datos externos se versionan con fecha de descarga y huella (hash) para reproducir un resultado?
4. ¿Qué ocurre ante respuesta parcial, paginación truncada (el bug de 1.000 filas) o cambio de formato?
5. ¿Hay caché con vigencia y modo degradado explícito en la salida cuando la fuente no responde?
6. ¿Se respetan los límites de uso y los términos de cada portal de datos abiertos?
7. ¿Las URL y los nombres de conjuntos de datos están fuera del código (configuración) y hay alerta si desaparecen?

### 8. Fallas en el cruce de datos y los cálculos

1. ¿La llave de cruce (código DIVIPOLA, NIT, nombre) es única y estable? ¿Cuántos registros se pierden o duplican en cada unión?
2. ¿La unión cambia el denominador de una tasa (por ejemplo, per cápita) sin avisar?
3. ¿Los datos cruzados tienen la misma ventana temporal?
4. ¿Se corrigen las comparaciones múltiples cuando se prueban muchos cruces?
5. ¿Se distingue asociación de causalidad en lo que el producto afirma?
6. ¿Se prueba el cruce con un caso sintético con respuesta conocida?
