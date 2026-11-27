# Resultados H5 (#273): amenaza sísmica normativa frente a daño estructural empírico (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §28, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6977741066) antes de calcular el índice de daño.
- **Código:** `h5_asimetria_normativa.py`, sin cambios después del prerregistro.
- **Salida:** `h5_asimetria_resultados.json`.
- **Muestra:** 994 municipios de 21 departamentos.
- **Intervalos:** IC95 % por bootstrap por departamento, 2.000 réplicas.

## Veredicto principal (A1): **ASIMETRÍA**

| Medida | Valor | IC95 % |
|---|---|---|
| A0: ρ bruto (Aa, daño D) | +0,14 | [−0,03; +0,34] |
| **A1: ρ parcial (Aa, D \| población, capacidad de reporte, pendiente)** | **−0,04** | **[−0,18; +0,15]** |

El IC del ρ parcial queda dentro de (−0,20; 0,20), el umbral prerregistrado. Una vez descontados el relieve, la población y el reporte, **el Aa de la NSR-10 no ordena a los municipios según el daño estructural reportado en 2019-2024**. La pequeña asociación bruta (+0,14) desaparece al controlar la pendiente, con la que el Aa se correlaciona 0,53.

## A2: ¿qué mecanismo produce el daño? (viviendas + vías + puentes)

| Mecanismo | Fracción del daño | IC95 % |
|---|---|---|
| **Hídrico** (inundación, creciente súbita, avenida torrencial) | **73 %** | [64 %; 80 %] |
| Otros (vendaval, colapso, incendio, etc.) | 19 % | [14 %; 26 %] |
| Remoción en masa | 7 % | [4 %; 13 %] |
| **Sísmico** | **0,4 %** | [0,1 %; 0,9 %] |

## Descriptivo

**A3, zona NSR-10 contra tercil de daño:**

| Zona | Daño bajo | Daño medio | Daño alto |
|---|---|---|---|
| Alta | 155 | 145 | 195 |
| Intermedia | 148 | 135 | 118 |
| Baja | 29 | 51 | 18 |

- Hay **155 municipios en zona sísmica Alta con daño bajo** y **18 en zona Baja con daño alto**.

**Correlación bruta de cada componente con Aa:**
- vías: +0,30;
- puentes: +0,15;
- **viviendas por habitante: −0,14.** El daño en vivienda es mayor donde el Aa es menor, por ejemplo en el Caribe inundable.

**ρ parcial por región** (estimaciones puntuales sin IC):

| Región | ρ parcial |
|---|---|
| Andina | −0,05 |
| Caribe | +0,09 |
| Pacífica | −0,21 |

## Lectura (fijada de antemano)

- **Qué muestra:** la zonificación sísmica oficial no captura el riesgo dominante contemporáneo. En estos seis años, ese riesgo fue **hídrico (73 % del daño)** y el sismo produjo menos del 1 %.
- **Qué no muestra:** que la zonificación sísmica esté equivocada o deba cambiarse.
  - La NSR-10 zonifica una amenaza de baja frecuencia y alta consecuencia, con período de retorno de 475 años.
  - En 2019-2024 no hubo un sismo destructivo mayor en el panel, así que la fracción sísmica es pequeña casi por construcción.
- **Para StructAI:** una ficha de sitio que solo muestra Aa/Av informa sobre la amenaza que menos daño ha causado en el período reciente. Por eso `/sitio` cruza también UNGRD, IGAC, IDEAM y SIMMA. Con H3, esto justifica mostrar **un indicador hídrico al lado del sísmico**, no en lugar de él.

## Limitaciones

- La UNGRD registra reportes y no inventaría lo expuesto.
- Las viviendas se normalizan por población, no por número de viviendas.
- Es un análisis municipal (falacia ecológica).
- El panel cubre 21 departamentos.
- El Aa toma pocos valores distintos.
- El umbral de equivalencia de ±0,20 es arbitrario.
