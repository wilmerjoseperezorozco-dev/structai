# Resultados H1: lluvia media anual de CHIRPS frente a las normales del IDEAM 1991-2020 (2026-11-08)

Protocolo, fijado y publicado antes de comparar: [`PROTOCOLO_NORMALES_CHIRPS.md`](PROTOCOLO_NORMALES_CHIRPS.md). Código: `normales_vs_chirps.py`. Salidas: `normales_chirps_resultados.json`, `normales_chirps_estaciones.csv`. Datos: IDEAM, conjunto `nsz2-kzcq` de datos.gov.co (licencia CC BY-SA 4.0).

## Datos
1.445 estaciones de las normales de precipitación en los 21 departamentos del proyecto, en 58 bloques de 1° (Andina 809, Caribe 347, Pacífica 243, Orinoquía 46). Ninguna quedó sin dato de CHIRPS.

## Acuerdo antes de corregir
CHIRPS está **un 5 % por encima** de las normales en la mediana (IC95 % [1,05; 1,06]), con un error típico de **7 %** (factor 1,07); el 92 % de las estaciones queda dentro de ±20 %. El patrón es parecido en todas partes:
| Corte | Sesgo (CHIRPS/normal) | Error típico |
|---|---:|---:|
| Andina / Caribe / Pacífica / Orinoquía | 1,06 / 1,04 / 1,08 / 1,04 | 1,06 / 1,06 / 1,09 / 1,05 |
| Altitud < 500 / 500-1.500 / 1.500-2.500 / ≥ 2.500 m | 1,05 / 1,06 / 1,06 / 1,07 | 1,06 / 1,07 / 1,07 / 1,09 |
| Lluvia < 1.000 / 1.000-2.000 / 2.000-3.500 / ≥ 3.500 mm | 1,11 / 1,06 / 1,04 / 1,03 | 1,12 / 1,07 / 1,05 / 1,05 |

CHIRPS sobrestima más donde llueve poco. Con la media de 3 × 3 pixeles el error sube a 1,09, y con solo las estaciones de `ao` ≤ 5 (632) es 1,06: el resultado no depende de esas elecciones.

## **Precaución central: esto no es una validación independiente de CHIRPS**
El acuerdo es **demasiado bueno para ser independiente** (correlación de los logaritmos 0,98). Una prueba con lugar cambiado lo confirma: al comparar cada normal con el pixel desplazado, el error típico sube de 1,07 (en la estación) a 1,09 (5 km), 1,15 (14 km), 1,25 (35 km) y 1,44 (155 km). El acuerdo existe solo en el punto de la estación, por lo que **no es un error de mi código**, sino que el mapa de lluvia media de CHIRPS está construido a partir de estaciones climatológicas, y probablemente de las mismas normales. Eso es lo que anticipé en el protocolo y ahora parece cierto, aunque no lo verifiqué en la documentación de CHIRPS. Conclusión: este resultado dice que **CHIRPS reproduce las normales donde hay estaciones**, no que sea exacto donde no las hay (montaña alta, selva, la mayor parte de las cuencas de interés).

## Corrección (validación con zona de exclusión de 50 km)
| Modelo | Error típico | Sesgo |
|---|---:|---:|
| C0 sin corregir | 1,065 | 1,054 |
| C1 factor regional | 1,041 | 1,000 |
| C2 regresión con altitud y región | 1,042 | 0,999 |

**Criterio primario: se cumple.** C1 reduce la mediana de |error ln| en 0,043 (IC95 % [−0,044; −0,041]), es decir, de ~6,5 % a ~4,1 %. Es estadísticamente claro pero **prácticamente pequeño**. C2 no mejora a C1 (+0,0001 [−0,001; +0,002]). La mejora aparece en las cuatro regiones.

## Efecto en la Etapa A (T = 10): ninguno
Al sustituir el predictor de lluvia de cada cuenca por su versión corregida (cambio mediano del predictor −5,2 %), el factor de error típico de M2 pasa de 1,746 a 1,734 con C1 (diferencia pareada −0,0004 [−0,0016; +0,0007]) y a 1,764 con C2 (+0,0002 [−0,0021; +0,0033]). **La corrección no cambia el resultado de la regionalización.** El factor de error de ~1,75 no viene del sesgo de la lluvia media (que es de 5 %), sino del propio modelo y de los datos de caudal, como ya se había visto con el análisis de incertidumbre.

## Lectura
1. La lluvia media anual de CHIRPS, en los puntos con estación del IDEAM, está unos 5 % alta y es muy consistente con las normales. La corrección regional lo lleva a cerca de 0 %.
2. **No usar este resultado como evidencia de exactitud de CHIRPS en cuencas sin estaciones**: la comparación no es independiente.
3. La Etapa A **no necesita** esta corrección. Se deja la decisión documentada: el predictor sin corregir sigue siendo válido.
4. Queda pendiente la Etapa B diaria (lluvia 2022-2024 de pluviómetros automáticos, fuente más independiente porque CHIRPS diario no se calibra con esas series), que sigue extrayéndose.

## Límites
Ciclo estacional (secundario del protocolo) **no ejecutado**: requiere leer CHIRPS mensual y el servidor está limitando las consultas. Estaciones concentradas en zonas pobladas; el significado de la columna `ao` no está verificado; no hay validación en zonas sin estaciones; mediana de 58 bloques, de modo que los IC reflejan solo la variación entre bloques. **No sustituye una calibración hidrológica con ingeniero responsable.**
