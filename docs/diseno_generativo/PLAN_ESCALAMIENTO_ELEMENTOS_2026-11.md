# Escalamiento del diseño generativo a otros elementos estructurales

Fecha: 2026-11-08. Estado: plan, sin código de los elementos nuevos. Todo lo marcado HIPÓTESIS es un supuesto de investigación sin verificar contra la norma ni contra ensayos; los porcentajes de ahorro citados en los enunciados originales (reducción del alma, del peso de la escalera, de la utilización de barras) son **objetivos a medir**, no resultados.

## 1. Inventario verificado (2026-11-08)

Motores existentes en `packages/motor-concreto/src`: viga, columna, zapata (prismática y troncopiramidal), pedestal, optimizador conjunto zapata + pedestal, encofrado DXF. **No existe** ningún motor de muros, pilotes, escaleras, cerchas, nudos ni ménsulas. `motor-estructural` es de visión/carga (InfraCortex), no de diseño.

Cobertura del corpus `nsr10_chunks` (conteo real por prefijo de `id`):

| Tema | Chunks | Estado para ingeniería verbatim |
|---|---|---|
| C.21.9 muros estructurales sísmicos | 45 | Revisar completitud con rag-audit-kit antes de codificar |
| C.14 muros | 51 | idem |
| C.11.8 ménsulas / C.11.9 vigas pared | 17 / 19 | idem |
| C.21.7 y C.21.5-6 (nudos, vigas, columnas sísmicas) | 25 / 33 | idem |
| C.9.5, C.13 (deflexiones, losas) | 46 / 212 | disponible |
| Apéndice C-A (puntales y tensores) | 40 (18 numerales; ingestado 2026-11-08) | Verbatim del Reglamento, sin Comentario; ver `docs/fuentes-normativas.md` |
| H (geotecnia: contención, pilotes H.4.4) | 552 (40 de pilotes) | disponible, auditar |
| F (acero estructural) | 2.728 | disponible |

## 2. Arquitectura común (se construye una vez)

El pipeline de zapata + pedestal es la plantilla: **optimizador exacto → muestreo LHS → etiquetas → sustituto → validador determinista**. Se extrae a un kit compartido y cada elemento solo aporta cuatro piezas:

1. `Espacio`: variables, rangos y escala (LHS con `scipy.stats.qmc`).
2. `evaluar_geometria(caso, x) -> Resultado | None`: verificación normativa completa, determinista. Es la única fuente de verdad de seguridad.
3. `exacto(caso)`: búsqueda de referencia (rejilla, evolución diferencial o NSGA-II según dimensionalidad).
4. `criterio`: costo APU + λ·CO₂ (reusa `economia_concreto`).

Compartido: etiquetado paralelo con checkpoint, entrenamiento LightGBM (regresión + clasificación para variables discretas como diámetros y perfiles), validador con tres orígenes (`directo` / `reparado` / `exacto`), re-verificación independiente y benchmark con brecha de criterio. Dos reglas nuevas frente a zapata:

- **Detección fuera de distribución**: si el caso queda fuera del casco convexo del entrenamiento o la incertidumbre (varianza de un ensamble) es alta, se salta directo al `exacto`.
- **Variables discretas por catálogo** (perfiles tubulares, diámetros de barra, espesores de 10 mm): el modelo propone y se redondea al catálogo antes de validar.

La garantía "0 % de diseños inseguros" es **por construcción de la capa de validación**, no una propiedad del modelo, y vale solo respecto de las verificaciones implementadas (ver "NO verifica" de cada motor).

## 3. Elementos, en el orden recomendado

Orden por valor y por riesgo: primero lo que ya tiene corpus y mecánica cerrada.

### 3.1 Muros de contención (prioridad 1)
- **Geometría**: pantalla de espesor lineal o parabólico, contrafuertes posteriores/anteriores, bandeja de alivio embebida.
- **Variables**: espesor en corona t_c y en base t_b, longitud de puntera y talón, cota y ancho de la bandeja, espaciamiento de contrafuertes, ángulo del relleno, γ, φ, c, q_adm, sobrecarga, sismo.
- **Mecánica (HIPÓTESIS de partida)**: empuje activo de Rankine o Coulomb por tramos con la bandeja como plataforma que descarga el relleno superior; sismo por Mononobe-Okabe. La afirmación de que la bandeja reduce "drásticamente" el volcamiento se **mide** en el dataset comparando contra el mismo muro sin bandeja.
- **Verificaciones**: volcamiento, deslizamiento, capacidad de soporte, excentricidad en el tercio medio, flexión y cortante de pantalla y talón (C.10/C.11), acero mínimo, juntas y drenaje (no se diseña drenaje: se declara supuesto).
- **Norma**: Título H del corpus + C.10, C.11, C.14. Factores de seguridad mínimos se leen de H, no se asumen.

### 3.2 Pilotes y cimentaciones profundas (prioridad 2)
- **Geometría**: fuste recto, acampanado (under-reamed), escalonado. Helicoidal/con aletas **fuera de alcance de NSR-10**: se modela solo como capacidad por fórmula publicada y se marca no normativo.
- **Variables**: D_s, D_b, ángulo de transición, longitud, profundidad de empotramiento, perfil SPT por estrato.
- **Qué aprende**: cuándo conviene alargar un fuste recto frente a ensanchar la base, con costo de excavación APU.
- **Verificaciones**: capacidad por punta y fricción desde SPT (método a fijar leyendo H.4.4 del corpus: no se elige uno de memoria), asentamiento, estructural del fuste, estabilidad de la campana, nivel freático. HIPÓTESIS: relación D_b/D_s máxima constructiva (valor práctico, sin fuente normativa verificada).
- **Dato necesario**: perfiles SPT reales de Barranquilla/Atlántico para no entrenar solo con perfiles sintéticos. Sin ellos el sustituto cubre el espacio, no la realidad.

### 3.3 Muros de corte de edificios (prioridad 3)
- **Geometría**: sección con elementos de borde engrosados (barbell, I) y alma delgada; muros con aberturas escalonadas.
- **Variables**: espesor del alma, ancho y longitud de cabezales, cuantía concentrada en bordes, altura, h_w/l_w.
- **Qué aprende**: maximizar I dentro y fuera del plano retirando concreto del alma donde la flexión es baja. El porcentaje de ahorro de alma es el **resultado a reportar**.
- **Verificaciones (C.21.9)**: flexocompresión con curva de interacción de sección compuesta, cortante, necesidad y dimensiones de elementos de borde (C.21.9.6), cuantías mínimas, espesor mínimo, pandeo fuera del plano del alma delgada.
- **Límite honesto**: muros con aberturas escalonadas son muros acoplados con vigas de acople (C.21.9.7) y su análisis fiable exige modelo de pórtico equivalente o elementos finitos. Fase 1 cubre solo muro sin aberturas; aberturas quedan para Fase 2, después de C-A.

### 3.4 Cerchas y cubiertas de grandes luces (prioridad 4)
- **Geometría**: cordón parabólico (bowstring), Pratt/Warren de altura variable. Gridshell queda fuera (análisis no lineal de forma).
- **Variables**: f/L, número de paneles N, perfil por grupo (cordón superior, inferior, diagonales, montantes) tomado de un catálogo.
- **Solver**: método matricial de rigidez 2D con numpy (se escribe y se valida contra casos de libro antes de usarlo). Cargas de Título B (viva de cubierta, viento, granizo/ceniza no aplican), combinaciones B.2.
- **Verificaciones (Título F)**: tracción, compresión con pandeo, esbeltez, flecha. Conexiones **no** se diseñan (se reporta fuerza de diseño por nudo y se declara).
- **Qué aprende**: forma que iguala fuerzas axiales en el cordón. La meta "85–95 % de utilización" se reporta como distribución observada.

### 3.5 Escaleras autoportantes (prioridad 5)
- **Geometría**: losa plegada (sawtooth), helicoidal de espesor variable.
- **Variables**: espesor de lámina t, huella/contrahuella, rigidez torsional de apoyos, luz.
- **Verificaciones**: flexión/cortante del pliegue, deflexión (C.9.5), vibración de piso, cargas vivas de Título B, límites de huella y contrahuella de la normativa de accesibilidad vigente (verificar vigencia antes de fijarlos).
- **Límite**: la losa plegada requiere modelo de placa plegada o elementos finitos para ser fiable; un modelo de viga equivalente subestima. Se calibra contra un modelo de elementos finitos de referencia antes de generar datos. El "30 % menos peso" se mide.

### 3.6 Nudos viga-columna y ménsulas (prioridad 6)
- **Desbloqueado el 2026-11-08**: el Apéndice C-A (puntales y tensores) ya está en el corpus (18 numerales verbatim). Falta el Comentario (figuras de nodos y puntales), que la ingesta no incluye.
- **Variables**: ángulo del puntal θ, ancho de nodos CCC/CCT/CTT, chaflán o ménsula trapezoidal.
- **Verificaciones**: resistencia de puntales, tensores, zonas nodales y anclaje (C-A), más C.11.8 y C.21.7 en el corpus.
- **Objetivo**: geometría mínima de ensanche que reduce congestión de acero. La congestión se mide con proxy (separación libre entre barras, cuantía local); constructibilidad real requiere criterio de obra.

## 4. Los que no se nombraron (propuestas a resolver)

Elementos y transversales que el enfoque necesita y aún no están en la lista:

| Propuesta | Por qué importa en Colombia | Dependencia |
|---|---|---|
| Losas aligeradas y nervadas (C.8.13, C.13) | Es el sistema de entrepiso dominante; mayor ahorro de concreto por m² | Corpus C.8/C.13 (212 chunks) |
| Vigas de cimentación y placas de fundación (C.15) | Cierra el ciclo con el motor de zapata; suelos blandos del Caribe | `zapata.py`, balasto ya modelado |
| Vigas de transferencia y vigas peraltadas de gran luz | Aparecen con muros y cerchas | `diseno_viga.py` existente |
| Columnas de sección variable o con cabezal | Reutiliza `columna.py` | curva de interacción existente |
| Tanques y muros de contención de agua (RAS 2000) | Mismo mecanismo que 3.1 con fisuración y estanqueidad | Normativa RAS en Drive |
| Mampostería estructural (Título D) | Vivienda de 1-2 pisos del Atlántico | Título D del corpus |
| Efecto sísmico real por elemento (Título A) | Hoy los motores reciben cargas ya calculadas | `cortante_basal.py` |

Transversales: **acciones y combinaciones de Título B** como módulo único reutilizable; **durabilidad C.4** y **mezcla variable** (ya en `diseno_zapata_pedestal`) para todo elemento de concreto; **exportación DXF/BIM** por elemento; **factores de CO₂ verificados** (siguen siendo el eslabón débil: ver `data/factores_emision`).

## 5. Riesgos y cómo se controlan

1. **Sustituto sin cobertura real**: el espacio LHS es una hipótesis. Mitigación: OOD + exacto y publicar la tasa de caída al exacto por elemento.
2. **Confundir "cumple el motor" con "cumple la norma"**: cada motor lista lo que NO verifica; se publica junto al resultado.
3. **Numerales inventados o de otra edición**: cada verificación cita el numeral leído del corpus en la fecha; cuando el corpus no lo tiene se ingesta primero (caso C-A).
4. **CPU**: el dataset de zapata ocupa los 4 núcleos ~4,4 h. Los datasets nuevos se generan en serie, no en paralelo con éste.
5. **Responsabilidad profesional**: ninguna salida reemplaza a un ingeniero que firme memorias; el aviso del issue #18 aplica a todos los motores nuevos.

## 6. Secuencia propuesta

1. Terminar zapata + pedestal (dataset, sustituto, benchmark) y extraer el kit común.
2. Muros de contención (motor, tests, dataset, sustituto).
3. Apéndice C-A: ingestado el 2026-11-08. Quedan sin ingestar los apéndices C-B y C-D.
4. Pilotes, luego muros de corte sin aberturas, luego cerchas, escaleras y nudos/ménsulas.
5. Por elemento: motor exacto con tests → dataset LHS → sustituto → benchmark → documento con supuestos.
