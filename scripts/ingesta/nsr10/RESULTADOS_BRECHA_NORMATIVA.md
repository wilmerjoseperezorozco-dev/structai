# Resultados: brecha entre el Apéndice A-4 y la capa del SGC, y población bajo ella (2026-11-08)

Protocolo fijado y publicado antes de calcular (commit `82d4812`): [`PROTOCOLO_BRECHA_NORMATIVA.md`](PROTOCOLO_BRECHA_NORMATIVA.md). Código: `brecha_normativa.py`. Salida: `brecha_normativa.json`.

## Tamaño de la brecha (29 municipios; Aa en 10, Av en 19; 7 cambian de zona)
| Medida | n | mínimo | mediana | máximo |
|---|---:|---:|---:|---:|
| Brecha relativa de Aa, (máx−mín)/mín | 10 | 14 % | 33 % | 60 % |
| Brecha relativa de Av | 19 | 20 % | 25 % | 200 % |

El máximo de Av (200 %) es Cartagena del Chairá (A-4 0,15; SGC 0,05), que además baja de zona Intermedia a Baja. Los valores de Aa y Av se mueven en saltos de 0,05, por lo que una brecha de 20-33 % suele ser un solo escalón de la tabla.

## Población según qué fuente sea la vigente (22 de 29 municipios con población en el panel)
| Escenario | Municipios (de 29) | Población |
|---|---:|---:|
| La capa del SGC pide **más** que el A-4 (en Aa o Av) | 16 | 1.522.489 |
| El A-4 pide **más** que la capa del SGC | 13 | 621.663 |
| Solo Aa: SGC mayor | | 569.824 |
| Solo Aa: A-4 mayor | | 57.865 |

La población total de los 22 con dato es de 2.144.152. Villavicencio pesa en el escenario «SGC mayor» (554.012 hab., Aa 0,25 frente a 0,35); Cúcuta (765.533) y Montería (517.476) también pesan, pero solo en Av (Cúcuta SGC mayor; Montería A-4 mayor). **No sé cuál fuente es la vigente**, así que las dos cifras son los extremos del intervalo, no una estimación.

## B1: ¿los 29 son más vulnerables que los demás? **No se cumple**
Mediana de viviendas con material vulnerable: 39,7 % (22 municipios) frente a 39,1 % (976 restantes). Diferencia +0,7 puntos, IC95 % bootstrap por departamento [−9,6; +9,5], Mann-Whitney p = 0,80. Con 22 municipios la potencia es baja: esto no demuestra que no haya relación, solo que no se detecta ninguna.

## Casos para revisión por un ingeniero (población × brecha, no es un ranking de riesgo)
Villavicencio, Montería, Cúcuta, Caldas (Antioquia), La Calera, Ábrego, Santafé de Antioquia, Guachetá, Garagoa y San Luis. De ellos, Caldas, La Calera, Santafé de Antioquia y San Luis cambian de zona de amenaza.

## Límites
- 7 de los 29 no están en el panel (Cartagena del Chairá; Nunchía, Pore, Sácama y Támara en Casanare; Lloró y Río Quito en Chocó), así que su población no se cuenta: las cifras de población son un **mínimo**.
- No verifiqué el año de la población del panel.
- La «deuda» es una cota de exposición a una discrepancia normativa, no una probabilidad de daño. Es nivel municipal, sin separar cabecera y rural.
- Se excluyó el Sisbén (acceso no verificado, datos personales).

## Qué cambia en StructAI
Nada se implementó. Sigue pendiente la recomendación de que el chat cite la fuente del Aa y avise en los 29 municipios; esta lista da el orden de prioridad (primero los 7 que cambian de zona y las ciudades grandes).
