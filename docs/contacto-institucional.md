# Colaboración institucional

StructAI nació como una herramienta para ingenieros civiles y maestros de
obra del Atlántico. La base normativa y de precios que hemos construido ya
no tiene ese límite técnico, y quiero que tampoco lo tenga a nivel
institucional. Este documento es el punto de entrada para cuatro tipos de
colaboración concreta — no una lista de intenciones genéricas.

## Para universidades y programas de ingeniería civil

Ofrezco acceso educativo gratuito a StructAI para estudiantes y docentes de
programas de ingeniería civil, como material de apoyo para cursos de
estructuras, hidráulica, geotecnia, vías o gerencia de proyectos — las
áreas que cubren los motores del sistema. La idea es simple: un estudiante
que consulta la NSR-10 o el RAS 2000 a través de StructAI ve la norma
citada exacta (sección, artículo), no una síntesis genérica, y puede
verificarla contra el texto oficial en el mismo momento.

Si diriges o participas en un programa académico (UNAL, Universidad de los
Andes, Javeriana, o cualquier otra universidad colombiana con programa de
ingeniería civil) y quieres explorar esto para tu curso o semillero de
investigación, abre una conversación por cualquiera de los canales de la
sección [Cómo contactar](#cómo-contactar).

Dos casos concretos que quiero destacar en vez de dejar la invitación
genérica:

- **ACOFI** (Asociación Colombiana de Facultades de Ingeniería) agrupa a
  decenas de facultades del país (Andes, Nacional, Javeriana, EAFIT,
  Escuela Colombiana de Ingeniería Julio Garavito, La Salle, Militar
  Nueva Granada, Universidad de Antioquia, EIA, Bolivariana, y sigue
  creciendo). Es el punto de entrada más eficiente si representas a la
  academia de ingeniería colombiana en general, no una universidad
  puntual.
- **Universidad del Norte** (Barranquilla) es el caso más natural de
  todos: tiene Doctorado en Ingeniería Civil, acreditación ABET, y un
  grupo de investigación real (**GIEG**, Grupo de Investigación en
  Estructuras y Geotecnia) que cubre estructuras, geotecnia, sísmica y
  materiales — exactamente los motores GeoPot y Estructural de StructAI,
  en la misma ciudad donde nació el proyecto.

## Para gremios y entidades de referencia normativa

La Asociación Colombiana de Ingeniería Sísmica (AIS) es la entidad de
referencia detrás de buena parte de la NSR-10 y de la línea de
rehabilitación sísmica de vivienda existente (AIS 2004, AIS 410-23) que
StructAI ya cita con atribución explícita. Si representas a AIS, al
Ministerio de Vivienda, a INVIAS, o a cualquier entidad con interés directo
en cómo se está usando y citando su normativa, quiero que veas exactamente
cómo lo hacemos — el código de las reglas de citación es público
(`packages/construdata/rag_multi_norma.py`), y la cobertura real (no
proyectada) es verificable en vivo en [`GET
/data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

En esta misma línea, hay tres instituciones más con las que quiero
hablar específicamente:

- **Sociedad Colombiana de Ingenieros (SCI)** — fundada en 1887 y
  declarada por la Ley 46 de 1904 Cuerpo Consultivo del Gobierno
  Nacional. Es, hasta donde investigué, el mayor peso institucional
  posible en ingeniería en Colombia.
- **Sociedad Colombiana de Geotecnia (SCG)** — fundada en 1971,
  afiliada a las sociedades internacionales de mecánica de suelos
  (ISSMGE), mecánica de rocas (ISRM) y geología para la ingeniería
  (IAEG). Directamente relevante al motor GeoPot.
- **CAMACOL** (Cámara Colombiana de la Construcción) — el gremio
  nacional específico del sector, no una cámara de comercio genérica.
  Publica el ICOCED (índice de costos de construcción de edificaciones)
  y el índice de precios de vivienda nueva — una fuente independiente
  real contra la cual contrastar los precios que ya tenemos. **CAMACOL
  Atlántico** existe en Barranquilla y publica informes regionales
  ("Atlántico Construcción en Cifras", informe de actividad edificadora)
  — mismo terreno donde nació StructAI.

## Para Cámaras de Comercio

Esta no es una relación hipotética — ya existe una de hecho, solo que
todavía no está formalizada. Los 78 proveedores mipyme nacionales que
StructAI cita con precio real (catálogo IAD MIPYMES / Colombia Compra
Eficiente) se enriquecen hoy con ciudad y departamento cruzando el
registro público consolidado de Cámaras de Comercio de Colombia (RUES) —
70 de esos 78 (90%) ya tienen ubicación real verificada así, sin que
ninguna Cámara haya sido contactada todavía. Formalizar esa relación
abriría varias cosas que hoy hacemos "desde afuera", con más fricción y
menos frescura de la necesaria:

- **Verificación en vivo de matrícula activa.** Hoy consulto el dato
  público de RUES en lote, con la latencia y los huecos de un dataset
  abierto (los 8 restantes son casos genuinamente ambiguos — homónimos
  reales, uniones temporales que no se registran como empresa regular —
  no un límite de esfuerzo). Con una relación directa, StructAI podría
  verificar "matriculado y activo hoy" con la misma frescura que ya
  ofrezco para matrícula profesional de ingenieros vía COPNIA.
- **Proveedores reales, con su consentimiento.** El catálogo nacional
  actual es un cruce de datos públicos, no una relación con las empresas
  mismas. Una Cámara tiene contacto directo con sus afiliados del sector
  construcción — podría invitarlos a aparecer en StructAI con marca,
  especificación técnica y ficha de producto real, el mismo nivel de
  detalle que hoy solo tienen los 24 proveedores del Atlántico.
- **Contraste con el observatorio económico regional**, si la Cámara
  publica uno (varias lo hacen para el sector construcción) — una
  segunda fuente independiente para verificar los precios que ya
  tenemos, en cualquier dirección.
- **Canal de distribución hacia quien ya construye.** Una Cámara agrupa
  exactamente al usuario objetivo de StructAI — constructores,
  ferreterías, contratistas — en un espacio de confianza institucional
  ya establecido, no una red social fría.

Si representas a una Cámara de Comercio (empezando naturalmente por la de
Barranquilla, de donde nació este proyecto) y quieres ver el cruce real
que ya hacemos con tu dato público antes de hablar de nada más, el código
es público: `scripts/ingesta/apu_barranquilla/enriquecer_ubicacion_proveedores_rues.py`.

Las que ya sé que publican un observatorio económico propio, en caso de
que esto interese verlo desde ese ángulo: la **Cámara de Comercio de
Bogotá** (el más completo que encontré), la **Cámara de Comercio de
Medellín**, la **Cámara de Comercio de Cali**, y hasta la **Cámara de
Comercio de Casanare** — si una cámara regional más chica lo hace, es
señal de que esto es una práctica extendida, no una excepción. Y en vez
de escribirle a cada una por separado, **Confecámaras** (la confederación
nacional de las 57 cámaras de Colombia) es el punto de entrada que las
agrupa a todas.

## Visión de largo plazo — interoperabilidad estatal (X-Road)

Esto es explícitamente **aspiracional, no un próximo paso técnico de esta
semana** — lo dejo escrito para que quede el mapa, no para prometer una
fecha. Colombia está construyendo la interoperabilidad real del Estado
sobre **X-Road** (la misma plataforma open-source que usa Estonia),
coordinada por la Agencia Nacional Digital y MinTIC. De las entidades ya
conectadas, estas son las que reforzarían StructAI de verdad si algún
día hay un convenio formal (conectarse a X-Road requiere eso, no es una
API que se activa sola):

**Refuerzo directo de motores:**
- **IGAC** — ya integrado hoy vía datos abiertos (suelos, motor GeoPot);
  X-Road sería la vía técnicamente correcta a futuro, y además IGAC
  maneja catastro nacional multipropósito — terreno sin tocar todavía,
  podría abrir un motor nuevo de predios/avalúo catastral.
- **Ministerio de Vivienda** — política de vivienda VIS/VIP, normativa
  de construcción — refuerza APU, GeoPot y Estructural a la vez.
- **Ministerio de Transporte** — INVIAS depende de este ministerio;
  dato nacional de infraestructura vial más allá de los APU
  regionalizados que ya tenemos (motor Vías).
- **Superintendencia de Notariado y Registro** — folios de matrícula
  inmobiliaria; relevante si StructAI conecta un cálculo a un predio
  real, no solo a un municipio (motor APU/proyectos).
- **Contraloría General de la República** — auditoría real de obra
  pública (sobrecostos, atrasos, hallazgos fiscales) — casos reales
  para el motor Gerencia (EVM/PMBOK), no solo teoría.

**Investigación/semilleros:**
- **Contraloría General** (doble uso) — los hallazgos de auditoría son
  material de investigación aplicada real: ¿por qué se sobrecostean los
  proyectos en Colombia?
- **Superintendencia de Notariado y Registro** (doble uso) —
  informalidad de tenencia de tierra, mercado inmobiliario real.
- **Ministerio de Educación** — canal institucional para reconocimiento
  formal de StructAI como herramienta educativa/de investigación (vía
  SNIES o similar), en la misma línea que ACOFI y Uninorte arriba.

**Nota honesta y corrección**: ninguna de las entidades conectadas a
X-Road hoy es **MinCiencias** (Ministerio de Ciencia, Tecnología e
Innovación) — no está en esa lista específica, así que no aparece
forzado ahí. Pero investigando más a fondo (2026-08-24) encontré algo
que sí vale la pena tener presente: por el **CONPES 4144** (Política
Nacional de Inteligencia Artificial, aprobada 2025), **MinCiencias es
hoy la Autoridad Nacional en IA de Colombia** — no es solo el ministerio
de ciencia genérico, es literalmente quien gobierna la política pública
de IA del país, con seis ejes (ética y gobernanza, datos e
infraestructura, investigación e innovación, entre otros) y una
inversión proyectada de $479.273 millones COP hasta 2030. Es, de lejos,
el contacto de mayor peso institucional si el objetivo es visibilidad
de IA aplicada en Colombia, no solo ingeniería civil — y además sigue
siendo la entidad real de fondeo/reconocimiento de semilleros de
investigación. MinCiencias corre convocatorias de fondeo para proyectos
de IA con regularidad (ver minciencias.gov.co/convocatorias) — vale la
pena vigilarlas, aunque ninguna convocatoria activa encontrada hasta
ahora encaja limpio con construcción/ingeniería civil todavía.

Las demás entidades conectadas a X-Road (ICA, ICBF, Cancillería,
Ministerio del Interior, DAFP, Unidad para las Víctimas, entre otras) no
tienen una conexión real con ingeniería civil/construcción — se dejan
fuera deliberadamente en vez de estirar la relevancia.

## Prioridad de ejecución

Para quien lea esto y se pregunte "¿por dónde empiezo yo, el autor,
a tocar puertas?" — este es el orden real, de más a menos accionable
ahora mismo:

1. **CAMACOL Atlántico** y **Universidad del Norte (GIEG)** — mismo
   terreno donde nació StructAI, menor fricción, mayor probabilidad de
   respuesta rápida. Empezar aquí.
2. **ACOFI** y **Confecámaras** — un solo contacto abre decenas de
   facultades o las 57 cámaras del país a la vez. Alto apalancamiento.
3. **SCI**, **SCG**, y las Cámaras de Comercio con observatorio propio
   (Bogotá, Medellín, Cali) — peso institucional nacional real, pero
   ciclos de respuesta más lentos. Vale la pena, sin prisa.
4. **MinCiencias** (Autoridad Nacional en IA de Colombia) — a diferencia
   de X-Road, esto sí es vigilable de forma concreta: corre
   convocatorias públicas de fondeo para IA con fechas reales
   (minciencias.gov.co/convocatorias). Ninguna convocatoria actual
   encaja limpio con construcción/ingeniería civil todavía, pero es el
   contacto de mayor peso si el objetivo es visibilidad de IA aplicada
   en Colombia a nivel país, no solo el sector construcción.
5. **X-Road / entidades estatales** (IGAC, Min Vivienda, Min Transporte,
   Notariado y Registro, Contraloría) — visión de largo plazo, requiere
   convenio formal, no es ejecutable como los niveles anteriores.
   Tenerlo en el radar, no perseguirlo todavía.

## Para quien tenga datos técnicos, normativos o de precios reales

Si tienes datos que puedan sumar a esta base — precios de materiales
verificados en tu región, normativa técnica que no esté cubierta todavía,
o series climáticas/hidrológicas locales — el repositorio está abierto
para revisión y toda incorporación queda documentada con su fuente
(`normas_registro`, `apu_precios_referencia.fuente`), nunca sin
atribución.

## Cómo contactar

- **GitHub Issues o Discussions** en el
  [repositorio](https://github.com/wilmerjoseperezorozco-dev/structai) —
  el canal preferido, queda público y trazable.
- **Perfil del autor**, enlazado desde el repositorio y desde
  [`CITATION.cff`](../CITATION.cff), si prefieres un canal directo.

## Cómo citar StructAI

Si usas StructAI en un trabajo académico o técnico, el archivo
[`CITATION.cff`](../CITATION.cff) tiene los metadatos completos, y el DOI
concepto (siempre apunta a la última versión publicada) es:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21851529.svg)](https://doi.org/10.5281/zenodo.21851529)

## Estado honesto, para quien evalúa colaborar

StructAI es un piloto en producción, no una cobertura nacional completa
todavía — el detalle exacto de qué está cargado y qué falta está en
[`docs/comparacion.md`](comparacion.md) y en el `README`. Prefiero que
cualquier conversación institucional empiece con esa claridad, no con una
promesa sin fecha.
