# Resultados C1: exposición de la red vial principal a terreno bajo (HAND), Caribe (2026-11-08)

Protocolo fijado antes de calcular: [`PROTOCOLO_VIAS_HAND.md`](PROTOCOLO_VIAS_HAND.md). Código: `vias_hand_caribe.py`. Salida por municipio: `vias_hand_caribe.json`. OpenStreetMap consultado el 2026-11-07 (marca de tiempo de la base 23:18 a 23:27 UTC). 159 municipios con al menos 5 km de vía principal, en los 7 departamentos del Caribe continental.

## C1a (confirmatoria): **no se cumple, por poco**
Mediana de (exposición vial − exposición del territorio) = **+0,029** (2,9 puntos porcentuales), IC95 % por departamentos **[−0,001; +0,074]**. El criterio exigía que el límite inferior superara 0; queda en −0,0005. Por regla, el resultado es **«no se confirma»**.
Sensibilidad C1a′ (sin los 18 municipios con más del 90 % del territorio en HAND < 10 m): +0,050, IC [−0,003; +0,123]. Tampoco cumple el criterio, aunque el efecto estimado sube.

**Lectura.** La estimación puntual apunta a que la red vial principal está algo más en terreno bajo que el territorio (unos 3 a 5 puntos), pero con solo 7 departamentos como bloques el intervalo es ancho y roza el cero. Los datos son compatibles con «no hay diferencia» y con «hay una diferencia pequeña». No se debe presentar como hallazgo.

## C1b (descriptiva): puentes sobre vías troncales, primarias y secundarias, según OpenStreetMap
| Departamento | Vía principal (km) | Puentes | Por 100 km | Sobre cauces con ≥ 25 km² aguas arriba |
|---|---:|---:|---:|---:|
| Atlántico | 784 | 198 | 25,3 | 18 |
| Bolívar | 967 | 154 | 15,9 | 32 |
| Cesar | 1.418 | 162 | 11,4 | 42 |
| Córdoba | 1.061 | 80 | 7,5 | 24 |
| La Guajira | 626 | 59 | 9,4 | 16 |
| Magdalena | 985 | 155 | 15,7 | 37 |
| Sucre | 713 | 75 | 10,5 | 12 |

**Cómo leerla.** En Atlántico solo 18 de 198 elementos etiquetados como puente caen sobre una red de 25 km² o más de área aguas arriba; no se determinó qué son los demás (podrían ser pasos sobre arroyos menores, canales o intersecciones a desnivel: no se verificó). La columna final es la más cercana a «puentes sobre ríos», y aun así depende de la resolución del modelo de terreno. Un tramo de puente puede estar partido en varios elementos de OSM, de modo que el conteo es de elementos, no de estructuras.

## Límites que condicionan todo lo anterior
1. HAND de 90 m no resuelve diques ni terraplenes: una vía elevada puede estar protegida aunque su celda sea baja.
2. HAND < 10 m es una condición del terreno, no una probabilidad de inundación ni de falla.
3. La cobertura de OSM es voluntaria: las diferencias entre departamentos (por ejemplo 967 km en Bolívar frente a 1.418 km en Cesar) pueden reflejar el mapeo y no la red real.
4. No hay validación contra daños: la tabla de la UNGRD no registra daños a vías ni puentes.
5. Exposición no es vulnerabilidad: no se evaluó el estado de ninguna estructura ni se nombra ninguna.
