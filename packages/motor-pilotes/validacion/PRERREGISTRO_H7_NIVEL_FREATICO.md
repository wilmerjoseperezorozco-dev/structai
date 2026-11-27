# Prerregistro H7 (#273): cuánto vale conocer el nivel freático antes de diseñar pilotes

Fijado el 2026-11-18, **antes** de cruzar los niveles medidos con el motor. Código: `h7_valor_nivel_freatico.py`.

## Pregunta

En suelo granular (arena y perfil mixto), si se diseña sin conocer el nivel freático, ¿cuánto se equivoca la capacidad y cuánto cuesta cubrirse? ¿Cuánto vale medirlo (piezómetro o apique) frente a suponerlo, o frente a la alarma de relieve validada en H2b?

## Datos

- **Nivel real:** 947 niveles estáticos medidos en llanura (SGC, CC BY 4.0: Meta, Guaviare, Inírida y Casanare; 558 con alarma de relieve). Están en `niveles_freaticos_llanura_sgc.json`, sin coordenadas y con el bloque de 0,1° anonimizado.
- **Motor de pilotes de StructAI:**
  - perfiles "arena" y "mixto" de H1;
  - pilotes in situ Ø0,5 y Ø1,0 y prefabricado Ø0,5, con las cargas de H1;
  - N60 medido fijo.
  - El nivel freático entra en σ'v: por fricción β·σ'v y por la normalización CN de N60 en la punta de Meyerhof.
- **Precios:** INVIAS 2026-1, mediana. Proyecto de N = 30 pilotes.

## Conteo previo (`--conteo`: respuesta del motor al NF, sin niveles reales)

| Tipo de pilote | Si el NF se supone más somero… | Ejemplo (arena, 1.000 kN) |
|---|---|---|
| **In situ (método β)** | el pilote sale **más largo**: baja σ'v y baja la fricción | 11,25 m (seco) → 15,75 m (NF = 0) |
| **Prefabricado hincado (Meyerhof)** | el pilote sale **más corto**: al bajar σ'v, sube CN y sube N1_60 en la punta | 31 m (seco) → 25 m (NF = 0) |

Por lo tanto, **el sentido del error depende del método**:
- en pilotes excavados, suponer "seco" es **inseguro**;
- en hincados, suponer "seco" es **conservador**.

Esto sale de las ecuaciones del CCP-14 tal como están en el motor y no se ajusta.

## Políticas

| Política | NF que se supone |
|---|---|
| Optimista | perfil seco |
| Conservadora | NF = 0 |
| Alarma (H2b) | NF = 0 si hay alarma; si no, seco |
| Piezómetro | NF real, con la longitud óptima |

Para cada punto medido y cada escenario: L de diseño con el NF supuesto, capacidad real con el NF medido y costo. Los niveles por debajo de 20 m se tratan como seco.

## Medidas

- **C1 (seguridad):** P(Q_adm real < 0,9·Q) con la política optimista. Se calcula para todos los puntos y para los que tienen alarma.
  - Si el IC95 queda por encima del 10 %, **suponer "seco" es materialmente inseguro**.
- **C2 (valor de la información):** VOI = costo esperado con la política conservadora − costo con piezómetro, en pesos, para un proyecto de 30 pilotes.
  - Se compara con una **referencia alta** de exploración: 10 m de "perforación de prueba para pilote" del INVIAS (621.3.1, unos 9,7 M$).
  - Un piezómetro real cuesta menos que esa perforación, que es de diámetro de pilote. Si el VOI la supera, medir se paga.
  - El VOI se reporta también frente a la política de alarma.
- **IC95 %:** bootstrap por bloque espacial (200 réplicas, semilla 7273).
- **Descriptivo:**
  - P(Q real < 0,8·Q);
  - sobrecosto relativo de la política conservadora;
  - resultados por escenario, pilote y carga;
  - con alarma frente a sin alarma.

## Lectura fijada de antemano

- Si C1 da material en pilotes excavados, `/sitio` debe pedir **medir el nivel freático** antes de diseñar pilotes excavados en llanura. La alarma de relieve sirve para priorizar, no para reemplazar la medición.
- El resultado de pilotes hincados (suponer seco es conservador) **no** es una razón para no medir. Depende de la normalización CN con un N60 fijo. En la realidad, el N60 medido ya refleja el estado del agua. Además, el nivel importa para la licuación y para la hinca, que este análisis no evalúa.

## Limitaciones declaradas

- Los niveles medidos son de llanura, de fechas y estaciones distintas, y se trata un nivel por sitio.
- Los perfiles de suelo son idealizados (no corresponden al perfil real de cada pozo).
- Se supone N60 fijo e independiente del nivel.
- No se considera la succión sobre el nivel freático ni la variación estacional.
- La referencia de costo de exploración no es el precio de un piezómetro.
