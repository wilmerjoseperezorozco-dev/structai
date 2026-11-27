# Resultados H2c (#273): definición objetiva de llanura (Hammond) como compuerta de la alarma de relieve (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §34, publicado en #273 antes de correr el análisis.
- **Código:** `h2c_llanura_objetiva.py`.
- **Salida:** `h2c_llanura_resultados.json`.
- **Definición:** se tomó de Hammond (1964) sin ajustarla. Un punto es llanura si, en un radio de 5 km, más del 80 % del terreno tiene pendiente < 8 % y el relieve es < 90 m.

## Veredictos

| Medida | Valor | IC95 % | Veredicto |
|---|---|---|---|
| **C1**: AUC de la alarma dentro de la llanura objetiva (n 669, 43 bloques, prevalencia 0,63) | **0,77** | [0,67; 0,85] | **VÁLIDA** |
| AUC fuera de la llanura (n 342, 23 bloques, prevalencia 0,20) | 0,68 | [0,50; 0,84] | |
| **C2**: ΔAUC dentro − fuera | +0,09 | [−0,10; +0,30] | **NO CONCLUYENTE** |

Alarma dentro de la llanura: sensibilidad 0,76, especificidad 0,64, VPP 0,78. Se activa en el 61 % de los puntos.

## Clasificación de los puntos

- **La compuerta separa bien las regiones:** clasifica como llanura entre el 74 % y el 100 % de los puntos de la Orinoquía y el **0 %** de Quindío.
- **Por capa, dentro de la llanura:**

  | Capa | n | AUC | IC95 % |
  |---|---|---|---|
  | Meta | 190 | 0,85 | [0,69; 0,92] |
  | Guaviare | 56 | 0,76 | [0,60; 1,00] |
  | Inírida | 75 | 0,83 | no interpretable* |
  | Casanare | 348 | 0,66 | [0,60; 0,74] |

  \* En Inírida el IC [0,0; 0,88] sale de un bootstrap degenerado, porque hay muy pocos bloques.
- **Fuera de la llanura:**

  | Zona | n | AUC | IC95 % |
  |---|---|---|---|
  | Casanare (piedemonte) | 63 | 0,73 | [0,63; 0,84] |
  | Quindío | 258 | 0,52 | [0,34; 0,74] |

## Cómo leerlo

- **Dentro de la llanura de Hammond la alarma funciona.** Es la condición necesaria para usarla en `/sitio`.
- **Fuera de la llanura el problema es que la alarma calla, no que se equivoque.**
  - Se activa en solo el 3 % de los puntos, con sensibilidad 0,15. Su silencio no significa "nivel profundo".
  - Cuando sí se activa, casi siempre acierta (VPP 0,91, pero con pocos casos).
  - Por eso C2 no sale concluyente: la diferencia de AUC entre dentro y fuera no es la pregunta relevante.
- **El piedemonte de Casanare no se comporta como Quindío** (AUC 0,73). La compuerta es conservadora: deja fuera terreno donde la regla quizá también sirve. Esto es exploratorio y no cambia la regla.

## Decisión (según la lectura fijada)

En `/sitio`, la alarma de nivel freático por relieve:
1. requiere el punto del lote (opt-in, redondeado a 0,01°). Así lo exige H8: con solo el municipio no se muestra.
2. solo se muestra si el lote es **llanura de Hammond**.
3. **Fuera de la llanura** el mensaje es "la alarma de relieve no aplica en este terreno; mida el nivel freático".
4. **Dentro de la llanura sin alarma** el mensaje es "relieve no indica nivel somero", nunca "nivel profundo". La especificidad es de solo 0,64.

En cualquier caso se recomienda medir antes de diseñar pilotes excavados (H7).

## Limitaciones

- Solo hay niveles medidos de la Orinoquía y de Quindío. Las llanuras del Caribe, del Magdalena y del Pacífico pasarían la compuerta **sin validación**: hay que declararlo en `/sitio` como "validado en la Orinoquía".
- Se excluyeron 194 puntos porque la vecindad de 5 km quedaba cortada por el borde de la tesela DEM (sobre todo en Meta).
- El DSM incluye el dosel del bosque.
- El umbral S = 6,5 m se fijó con Meta, Guaviare e Inírida, que aquí vuelven a entrar. La validación independiente sigue siendo la de Casanare (H2b), y dentro de la llanura da 0,66 [0,60; 0,74].
