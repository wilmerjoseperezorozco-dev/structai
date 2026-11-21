# Análisis de vacíos en la investigación de ingeniería civil que usa StructAI

Fecha: 2026-11-11. Objetivo: encontrar fallas o vacíos en estudios y métodos anteriores que **justifiquen propuestas nuevas** de StructAI. Es un análisis de escritorio para priorizar, no una revisión sistemática publicable. Antes de citar cualquier punto en una propuesta (MAPFRE, artículo, convocatoria) hay que leer la fuente primaria.

**Nivel de evidencia de cada afirmación:**
- **[V]** verificado hoy en una fuente consultada (enlazada al final);
- **[R]** medido o documentado en este repositorio;
- **[P]** por verificar en la fuente primaria. No citar todavía.

## 1. Rúbrica (aplicable a cualquier estudio)

| Criterio | Pregunta de control | Señal de vacío |
|---|---|---|
| **1. Sesgo de la muestra** | ¿Cuántos casos, de dónde y de qué periodo? ¿Se parecen al contexto colombiano de StructAI (tropical, andino, sísmico, informal, con pocos datos)? | n chico; una sola región, clima o evento; casos de otros países trasladados sin recalibrar |
| **2. Obsolescencia tecnológica o teórica** | ¿El estudio tiene más de 15 años? ¿Sus instrumentos, series o supuestos siguen vigentes? ¿Hay un método sucesor? | Series que terminan antes de 2010; métodos empíricos superados por métodos mecanicistas o probabilísticos; supuesto de estacionariedad |
| **3. Variables ignoradas** | ¿Considera cambio climático, cambios normativos, datos digitales o satelitales, urbanización e informalidad, carbono? | La variable existe y se mide hoy, pero el modelo no la incluye |

Un vacío es **fuerte** cuando se cumple más de un criterio **y** StructAI ya tiene datos para medirlo. Eso convierte la crítica en una propuesta ejecutable.

## 2. Matriz de vacíos por problema

### 2.1 Diseño de pavimentos: AASHTO 93 y la AASHO Road Test (1958–1960)

- **Base:** la guía AASHTO 1993 es empírica y se calibró con la AASHO Road Test, cerca de Ottawa, Illinois, entre 1958 y 1960 **[V]**. El motor de vías de StructAI usa "AASHTO 93 adaptado" del Manual INVIAS **[R]** (`motor_chunks`: "Método mecánico-empírico AASHTO 93 adaptado").
- **1. Muestra:** un solo clima y un solo tipo de subrasante; unos dos años de seguimiento; como máximo ~10 millones de ejes equivalentes; sin datos de rehabilitación ni subdrenaje **[V]**. Nada de clima tropical, suelos residuales ni topografía andina.
- **2. Obsolescencia:** el método tiene más de 60 años de base. La propia AASHTO lo reemplazó por la MEPDG, mecanicista-empírica y calibrada con datos de desempeño **[V]**.
- **3. Ignoradas:** variación de humedad y temperatura en las capas **[V]**, que es justo lo que incluye la MEPDG; sobrecarga real de camiones en Colombia; cambio climático **[P]**.
- **Propuesta:** calibración local mecanicista-empírica con datos de desempeño de vías colombianas, y medición de cuánto difiere el SN de AASHTO 93 en climas y subrasantes típicos del país. **Vacío fuerte.**

### 2.2 Amenaza sísmica de diseño: Aa y Av de la NSR-10

- **Base:** los coeficientes Aa y Av de la NSR-10 vienen del estudio general de amenaza sísmica que acompañó su actualización (Salgado et al., 2010) **[V]**.
- **2. Obsolescencia:** el mapa de diseño tiene ~16 años. El SGC, con la Fundación GEM, publicó después un **Modelo Nacional de Amenaza Sísmica** **[V]**: citado como volumen 43 del SGC (2020), con mapas en superficie basados en Vs30 y consulta en línea para varios periodos de retorno **[V]**. Hay una memoria justificativa de un proyecto de resolución sobre su adopción **[V]**. El estado de esa adopción está por confirmar **[P]**.
- **3. Ignoradas:** efectos de sitio a escala nacional (Vs30), sismos registrados después del catálogo de 2009, otros periodos de retorno y de vibración **[V]**. La microzonificación existe solo para pocas ciudades: StructAI tiene 36 filas en `microzonificacion_sismica_local` **[R]**.
- **Propuesta:** comparar municipio por municipio el Aa y Av de la NSR-10 (StructAI ya tiene el Apéndice A-4, 1.117 municipios, y el SGC en vivo, 1.121 **[R]**) contra el modelo nacional del SGC, y cuantificar dónde cambia la demanda sísmica. Es una de las propuestas más ejecutables, porque los datos ya están cargados. **Vacío fuerte.**

### 2.3 Lluvias de diseño: curvas IDF sintéticas regionalizadas (1998)

- **Base:** Vargas y Díaz-Granados (1998), "Curvas sintéticas regionalizadas de intensidad-duración-frecuencia para Colombia" **[V]**: unas 150 curvas IDF filtradas por confiabilidad, con un modelo que usa la precipitación máxima diaria media, los días con lluvia al año y la región **[V]**.
- **1. Muestra:** regionalización con estaciones disponibles antes de 1998. Hay estudios que recomiendan no usar la ecuación regionalizada en sitios concretos, y uno reporta intensidades bastante mayores que las de registros pluviográficos locales **[V]**.
- **2. Obsolescencia:** 28 años, sin las series de 1998 a 2026 **[P]** (comprobar qué series siguen en uso).
- **3. Ignoradas:** **no estacionariedad** por cambio climático; urbanización; la variabilidad ENSO **[P]**, que StructAI ya cruzó con caudales (`fase4c_enso_caudal.py`) **[R]**.
- **En StructAI:** los coeficientes IDF de `motor-aquai` están marcados como ilustrativos y no verificados; el issue #134 pide reemplazarlos por las IDF oficiales del IDEAM **[R]**.
- **Propuesta:** IDF actualizadas por estación con series IDEAM recientes, con prueba explícita de tendencia o no estacionariedad, comparadas contra la regionalización de 1998. **Vacío fuerte.**

### 2.4 Licuación de suelos: procedimiento simplificado (Seed e Idriss, 1971 → Boulanger e Idriss, 2014)

- **Base:** el procedimiento simplificado y su actualización de 2014 (informe UCD/CGM-14/01), con una base de casos actualizada **[V]**. Un trabajo posterior dice que el modelo probabilístico CPT de 2014 se entrenó con prácticamente todos los casos publicados, unos 255 puntos **[V]**.
- **1. Muestra:** unos 255 casos para todo el mundo, dominados por los sismos que alimentan las bases internacionales; el proyecto NGL se expandió sobre todo con Japón y Nueva Zelanda (2011) **[V]**. La representación de casos colombianos y de suelos tropicales o volcánicos está por verificar **[P]**. Si es mínima, como se espera, es un sesgo directo para StructAI.
- **2. Obsolescencia:** el marco de 1971 sigue en uso con correcciones. El campo avanza hacia métodos probabilísticos y bases de datos abiertas (NGL) **[V]**.
- **3. Ignoradas:** duración de sismos de subducción largos; suelos residuales y volcánicos; envejecimiento del depósito **[P]**.
- **En StructAI:** existe `motor-licuacion` (84 pruebas) y el issue #137 **[R]**.
- **Propuesta:** inventario de casos históricos de licuación en Colombia y evaluación del procedimiento simplificado sobre ellos. **Vacío fuerte si se confirma la subrepresentación.**

### 2.5 Vulnerabilidad sísmica de vivienda: checklist AIS (2004) y FEMA P-154

- **Base:** el checklist de 15 criterios de la AIS (2004) nace de la experiencia del sismo del Eje Cafetero de 1999. Se descartó FEMA P-154 porque está calibrado para tipologías de EE. UU. **[R]** (docstring del motor y issue #51).
- **1. Muestra:** un evento y una región; mampostería de 1-2 pisos **[R]**.
- **2. Obsolescencia:** 22 años. Existe un documento más riguroso y reciente, la AIS 410-23, ya cargado en el corpus **[R]**.
- **3. Ignoradas:** densificación informal posterior a 2004; datos masivos de material de vivienda (Sisbén, 1.099 municipios en StructAI **[R]**); detección remota de tipologías **[P]**.
- **Propuesta:** contrastar la clasificación del checklist con daños observados en sismos posteriores y con los datos de Sisbén por municipio. Conecta con la línea L2 (#168).

### 2.6 Caudales máximos en sitios sin aforo: regionalización

- **1. Muestra:** red de estaciones escasa en Orinoquía, Amazonía, Pacífica y Caribe; el issue #156 pide más estaciones antes de afirmar algo sobre esas regiones **[R]**.
- **2. Obsolescencia:** pendientes de cauce calculadas con DEM de 90 m; se propone repetir con 30 m (#155) **[R]**.
- **3. Ignoradas:** ENSO y deforestación, que StructAI ya explora (`fase4c`, `fase67`) **[R]**.
- **Propuesta:** #151, con intervalo de predicción y validación por región.

### 2.7 Movimientos en masa disparados por lluvia

- **1–3:** umbrales de lluvia acumulada tomados de otras regiones o de pocos eventos; la deforestación como variable moderna ignorada **[P]**. StructAI tiene la señal de 5 días propuesta en #153 y los cruces con deforestación (`fase67`) **[R]**.
- **Propuesta:** umbral local con su tasa de falsas alarmas (TSS), por región.

### 2.8 La evaluación de IA aplicada a ingeniería (incluido StructAI)

Los mismos tres criterios aplican a la literatura reciente, y a nosotros:
- **1. Muestra:** las baterías de StructAI son 63 % NSR-10 y casi sin vías, agua ni gerencia (#109); entrenar el enrutador con ellas lo empeora (E1e) **[R]**. Muchos benchmarks publicados de LLM en construcción usan preguntas generadas por el mismo LLM **[P]**.
- **2. Obsolescencia:** jueces LLM sin calibrar contra expertos; métricas con hasta 51 % de faltantes (#109) **[R]**.
- **3. Ignoradas:** el desplazamiento de distribución entre el benchmark y el uso real, y la vigencia normativa (la E.030 de 2019 vs la de 2026, y la Res. 0330 antes de 2021 en el corpus) **[R]**.
- **Propuesta:** el benchmark con sabotaje controlado y el held-out escrito por personas (#169, #171) son en sí una contribución metodológica publicable.

### 2.9 Otros, para una segunda pasada

- **Gerencia:** el valor ganado clásico frente a métodos de cronograma más recientes y BIM 4D/5D; la Ley 80 de 1993 y sus reformas, con 785 chunks en el corpus **[R]**; impacto digital no medido **[P]**.
- **Concreto:** dosificación ACI 211 sin carbono incorporado, ni materiales cementantes suplementarios ni cementos actuales **[P]**; conecta con L1 costo-seguridad-carbono (#167) **[R]**.

## 3. Priorización

| Vacío | Criterios | ¿StructAI ya tiene los datos? | Costo | Prioridad |
|---|---|---|---|---|
| Aa/Av NSR-10 vs modelo nacional del SGC | 2 + 3 | **Sí** (A-4, SGC) | Bajo | **1** |
| IDF 1998 vs series IDEAM con no estacionariedad | 1 + 2 + 3 | Parcial (IDEAM caudal; falta lluvia horaria) | Medio | **2** |
| Pavimentos: AASHTO 93 en clima y subrasante colombianos | 1 + 2 + 3 | Parcial (motor-vías; falta desempeño real) | Alto | 3 |
| Licuación: casos colombianos | 1 + 3 | No (hay que construir el inventario) | Alto | 4 |
| Vivienda: AIS 2004 vs daños recientes y Sisbén | 1 + 2 + 3 | Parcial (Sisbén; faltan daños) | Medio | 5 |
| Evaluación de IA en ingeniería | 1 + 2 + 3 | **Sí** (#169) | Bajo | en curso |

## 4. Cómo usar esto en una propuesta

1. Elegir un vacío con prioridad alta.
2. Pasar sus afirmaciones **[P]** a **[V]** leyendo la fuente primaria. Para las **[V]**, citar la fuente primaria, no el resumen secundario.
3. Redactar el problema con los tres criterios: *"El método X, calibrado con [muestra], tiene [N] años y no considera [variable]; en Colombia esto implica [consecuencia medible]."*
4. Proponer la medición con los datos de StructAI y su criterio de éxito preregistrado, con el mismo estándar del benchmark.

## Fuentes consultadas

- FHWA, LTPP: limitaciones de la AASHO Road Test. https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/ltpp/10071/004.cfm
- NCAT (Auburn), informe 14-04. https://eng.auburn.edu/research/centers/ncat/files/reports/2014/rep14-04.pdf
- North Dakota DOT (ROSA P). https://rosap.ntl.bts.gov/view/dot/28527/dot_28527_DS1.pdf
- SGC, amenaza sísmica. https://www2.sgc.gov.co/Direcciones-Tecnicas/Geoamenazas/amenaza-sismica/Paginas/default.aspx
- SGC, memoria justificativa del modelo de amenaza. https://www2.sgc.gov.co:443/Archivos/MEMORIA%20JUSTIFICATIVA%20Modelo%20de%20Amenaza.pdf
- Salgado et al. (2010), referenciado en Redalyc. https://www.redalyc.org/pdf/1210/121018987004.pdf
- Referencias a Vargas y Díaz-Granados (1998) y sus limitaciones: https://core.ac.uk/download/71895009.pdf · https://repository.usta.edu.co/bitstreams/3001a49b-4db0-49c1-bef8-2be2ec5fb759/download · https://revistaingenieria.univalle.edu.co/index.php/ingenieria_y_competitividad/article/view/2362
- Boulanger e Idriss (2014), UCD/CGM-14/01. https://faculty.engineering.ucdavis.edu/boulanger/wp-content/uploads/sites/71/2014/09/Boulanger_Idriss_CPT_and_SPT_Liq_triggering_CGM-14-01_20141.pdf
- Estudio posterior sobre la base de 2014 (255 casos). https://par.nsf.gov/servlets/purl/10281037
- PEER, Next-Generation Liquefaction. https://peer.berkeley.edu/ngl
