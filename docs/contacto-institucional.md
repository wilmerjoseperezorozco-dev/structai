# Colaboración institucional

StructAI nació como una herramienta para ingenieros civiles y maestros de
obra del Atlántico. La base normativa y de precios que hemos construido ya
no tiene ese límite técnico, y quiero que tampoco lo tenga a nivel
institucional. Este documento es el punto de entrada para tres tipos de
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
