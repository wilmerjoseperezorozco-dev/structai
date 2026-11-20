# Prerregistro HE4 (#274): periodo medido frente al periodo del motor en pórticos colombianos

Fijado el 2026-11-19, **antes** de tener datos medidos de pórticos. Código: `he4_t_motor.py`.

## Pregunta

En pórticos de concreto colombianos, ¿el periodo medido con vibración ambiental es claramente menor que el del modelo de pórtico desnudo, incluso con inercias brutas?

Si la respuesta es sí, la diferencia la explican los elementos no estructurales (sobre todo la mampostería) y no la fisuración.

## Datos que entran

- **Edificios:** de Colombia, de pórticos de concreto, con periodo fundamental medido por vibración ambiental o por instrumentación sísmica de amplitud baja, y con la altura total publicada.
- **Fuente:** tesis, artículo o informe que se pueda citar. Solo se transcriben números.
- **Dirección:** una por edificio, la del periodo más largo que reporte la fuente.
- **Control de calidad:** si la fuente da dos métodos de identificación, el edificio se excluye cuando difieren más del 10 %. Si concuerdan, se usa su promedio.
- **Excluidos:** edificios de fuera de Colombia, estudios que solo tienen modelos, edificios combinados o de muros (esos esperan a la F3, cuando el motor modele muros) y los 15 edificios de Bucaramanga de Torres Ayala (2022), porque ya los vi (ver `LITERATURA_HE4.md`).

## Modelo equivalente (T_motor), fijado

- **Geometría:** planta de 3×3 vanos de 6 m y N = máx(1, round(h/3)) pisos.
- **Secciones:** columnas por carga axial y vigas h = máx(L/12; 0,30), con el mismo prediseño de HE6.
- **Inercias:** **brutas**, para igualar la amplitud mínima de la medición.
- **Masa:** D = 7,0 kN/m².
- **Periodo:** el mayor del análisis modal 3D (F2).

No uso la planta real de cada edificio porque no tenemos los planos. Esa es la principal limitación, y la declaro.

## Medida y criterio

**Medida:** mediana de T_medido/T_motor, con IC95 por bootstrap (10 000 remuestreos, semilla 274).

| Veredicto | Condición |
|---|---|
| **CONFIRMADA** | límite superior < 0,80 |
| **REFUTADA** | límite inferior ≥ 0,80 |
| **NO CONCLUYENTE** | en otro caso |

- **Por qué 0,80:** con inercias brutas la fisuración no puede explicar la diferencia. Exigir una razón por debajo de 0,8 deja margen para lo que el modelo simplificado no capta (losas, escaleras, la planta real).
- **Mínimo de datos:** n ≥ 10 pórticos válidos. Con menos, HE4 **no se corre**.

**Descriptivo:** T_medido/Ta, reportado por número de pisos.

## Referencia sin datos medidos (calculada al fijar el protocolo)

Con `--tabla`, el modelo equivalente con inercias brutas da T_motor ≈ 1,4–1,5·Ta en edificios de 4 a 20 pisos, y ≈ 2,2–2,4·Ta en edificios de 1 y 2 pisos.

Esto no es evidencia a favor de HE4, por dos razones:
- Ta (A.4.2-3) se ajustó con periodos medidos en edificios de EE. UU. y está deliberadamente sesgado hacia abajo.
- El prediseño por gravedad, sin iterar la deriva, da pórticos más flexibles que los reales.

## Estado al 2026-11-19

**n = 0 pórticos válidos.** Datos que faltan:
- **Univalle (Coral Vargas 2014):** son edificios de muros, así que no entran en la prueba principal. Su repositorio no responde.
- **Instrumentación de edificios de Bogotá (NSR-10 A.11):** habría que pedirle los datos a IDIGER.
- **Mediciones propias:** un edificio de pórticos medido con un acelerómetro, siguiendo el protocolo de 60 min a 200 Hz o equivalente.
