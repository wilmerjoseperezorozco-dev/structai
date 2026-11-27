# SECOP II — procesos de obra por UNSPSC (#212)

Generado por `procesos_obra_unspsc.py` (reglas-0.1.0) el 2026-11-15 desde la copia del 12-nov-2026.

## Limpieza

| Paso | Filas |
|---|---|
| leidas | 151,359 |
| duplicado_id | 18,970 |
| excluidas_por_segmento | 17,277 |
| conservadas | 115,112 |

Segmentos excluidos: {'80': 2952, '70': 2192, '30': 2002, '77': 1161, '39': 900, '93': 732, '73': 574, '40': 564, '46': 555, '76': 521, '31': 378, '44': 341, '49': 304, '26': 279, '56': 263, '47': 247, '71': 220, '22': 199, '85': 191, '43': 179, '10': 179, '11': 172, '24': 169, '78': 167, '60': 166, '55': 150, '90': 131, '27': 128, '82': 125, '20': 117, '86': 110, '41': 106, '25': 97, '92': 91, '23': 82, '84': 73, '32': 66, '94': 56, '45': 52, '52': 50, '21': 44, '42': 41, '12': 36, '15': 24, '48': 20, '50': 20, '14': 17, '91': 14, '53': 10, '13': 8, '51': 1, '54': 1}

Control de cordura de la API: no verificado (usa --verificar-api)

## Segmento UNSPSC

| Valor | Procesos | % |
|---|---|---|
| 72 | 81,654 | 70.9% |
| sin_codigo | 15,397 | 13.4% |
| 81 | 10,136 | 8.8% |
| 95 | 5,159 | 4.5% |
| 83 | 2,766 | 2.4% |

## Tipo de obra (etiqueta principal)

| Valor | Procesos | % |
|---|---|---|
| mantenimiento | 36,844 | 32.0% |
| vias | 13,409 | 11.6% |
| edificacion_institucional | 8,749 | 7.6% |
| acueducto_alcantarillado | 7,816 | 6.8% |
| edificacion_educativa | 7,531 | 6.5% |
| sin_clasificar | 7,158 | 6.2% |
| espacio_publico_deportivo | 6,562 | 5.7% |
| obra_civil_pesada | 5,424 | 4.7% |
| estudios_y_disenos | 4,143 | 3.6% |
| obra_especializada | 3,325 | 2.9% |
| electrico_alumbrado | 3,078 | 2.7% |
| placa_huella_via_terciaria | 2,995 | 2.6% |
| vivienda | 2,449 | 2.1% |
| puentes | 1,756 | 1.5% |
| edificacion_salud | 1,362 | 1.2% |
| servicios_publicos | 1,147 | 1.0% |
| contencion_estabilizacion | 957 | 0.8% |
| interventoria | 407 | 0.4% |

## Prioridad StructAI

| Valor | Procesos | % |
|---|---|---|
| media | 62,458 | 54.3% |
| alta | 42,418 | 36.8% |
| baja | 10,236 | 8.9% |

## Origen de la etiqueta

| Valor | Procesos | % |
|---|---|---|
| texto | 82,812 | 71.9% |
| unspsc | 25,142 | 21.8% |
| ninguna | 7,158 | 6.2% |

## Modalidad

| Valor | Procesos | % |
|---|---|---|
| Selección Abreviada de Menor Cuantía | 46,272 | 40.2% |
| Contratación régimen especial | 27,549 | 23.9% |
| Licitación pública Obra Publica | 16,041 | 13.9% |
| Mínima cuantía | 10,610 | 9.2% |
| Contratación directa | 9,257 | 8.0% |
| Contratación régimen especial (con ofertas) | 2,517 | 2.2% |
| Contratación Directa (con ofertas) | 1,477 | 1.3% |
| Licitación pública | 843 | 0.7% |
| Seleccion Abreviada Menor Cuantia Sin Manifestacion Interes | 546 | 0.5% |

## Alertas de calidad (no se borran, se marcan)

| Alerta | Procesos |
|---|---|
| precio_base_invalido | 1,037 |
| precio_base_menor_1M | 268 |
| adjudicado_mayor_150pct_base | 64 |
| precio_base_mayor_10_billones | 4 |

Las etiquetas son **reglas de texto + familia UNSPSC**: base para el clasificador TF-IDF (#196) y se miden contra la muestra humana de 300 (`muestra_etiquetar_300.csv`). Criterio prerregistrado en #212: F1 macro ≥ 0,85.
