# Normas colombianas candidatas a ingesta: priorización (sin verificar)

Estado: 2026-11-08. **Ninguna de estas normas está verificada en texto vigente.** La lista sale de conocimiento general y sirve solo para decidir qué verificar primero. Antes de ingestar cualquiera se aplica la regla del proyecto: buscar la versión consolidada y las modificaciones posteriores, y revisar los issues abiertos del milestone (ver `CLAUDE.md`). Los números de norma y su alcance deben confirmarse en la fuente oficial; si no coinciden, esta tabla se corrige.

Criterio de puntuación (1–5 cada uno, total máx. 20): **A** relación directa con los frentes F1–F4 y con `motor-aquai`; **B** probabilidad de que el usuario de StructAI la consulte; **C** facilidad de obtener texto consolidado verificable; **D** riesgo de que el RAG sirva una versión desactualizada si no se ingesta (sesgo de vigencia).

| Norma candidata (por verificar) | Tema | A | B | C | D | Total | Frente |
|---|---|---|---|---|---|---|---|
| Decreto 1076 de 2015 (Decreto Único del Sector Ambiente), partes sobre licencias, concesiones y caudal ambiental | Licenciamiento y uso del agua; pequeñas centrales | 5 | 4 | 4 | 4 | 17 | F1, F4 |
| Decreto 1077 de 2015 (Decreto Único del Sector Vivienda), partes sobre gestión del riesgo en ordenamiento territorial | Amenaza por avenida torrencial en POT | 5 | 4 | 4 | 4 | 17 | F2 |
| Ley 1523 de 2012 | Sistema Nacional de Gestión del Riesgo | 4 | 4 | 5 | 2 | 15 | F2 |
| Ley 1715 de 2014 y Ley 2099 de 2021 | Fuentes no convencionales de energía y pequeñas centrales | 5 | 3 | 5 | 3 | 16 | F1 |
| Resoluciones de la CREG sobre pequeña generación y autogeneración | Condiciones de conexión y venta | 3 | 3 | 3 | 4 | 13 | F1 |
| Normas sobre acotamiento de rondas hídricas (decreto y guía técnica del Ministerio de Ambiente) | Delimitación de franjas de cauce | 4 | 3 | 3 | 3 | 13 | F2, F4 |
| Resoluciones de la CRA modificatorias de la 0330 de 2017 posteriores a 2021 | Vigencia del verificador | 5 | 4 | 3 | 5 | 17 | Verificador |
| Normas técnicas de IDEAM sobre caudal ambiental y estudio nacional del agua (metodologías) | Caudal ecológico | 4 | 2 | 3 | 2 | 11 | F1, F4 |

## Lectura

1. **Primero lo que ya usamos:** las modificaciones posteriores a 2021 de la Resolución 0330 (puntaje 17, riesgo D = 5). Es la verificación pendiente del verificador y no requiere decidir nada nuevo.
2. **Después los dos decretos únicos (1076 y 1077):** alta relevancia y alto riesgo de desactualización porque se modifican con frecuencia; su ingesta debe traer solo las partes pertinentes, no el decreto completo.
3. **La Ley 1715/2099** habilita el contexto de F1; no es urgente hasta que F1 produzca resultados.
4. **No ingestar nada por inercia:** si F1–F4 dan resultados negativos o no concluyentes, el contexto normativo asociado pierde prioridad.

## Hallazgo ya confirmado que justifica la prioridad

El texto de la Resolución 0330 indexado en el RAG (255 artículos) es anterior a las Resoluciones 799 y 908 de 2021 y difiere del texto consolidado (265 artículos) en numeración y en al menos un valor (SUDS 25 % vs. 30 %). Esto ya ocurrió dos veces antes en el proyecto con otras normas; por eso la verificación de vigencia va antes de ingestar.

## Pendiente de decisión del usuario

- Re-ingestar el texto consolidado de la Resolución 0330 en producción (cambio en base de datos; requiere confirmar vigencia y aprobación).
