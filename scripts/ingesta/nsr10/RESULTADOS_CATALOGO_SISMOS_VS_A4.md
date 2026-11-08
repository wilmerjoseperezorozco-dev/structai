# Resultados: catálogo de sismos del SGC frente al Aa del Apéndice A-4 (2026-11-08)

Protocolo fijado y publicado antes de descargar los eventos (commit `8312209`): [`PROTOCOLO_CATALOGO_SISMOS_VS_A4.md`](PROTOCOLO_CATALOGO_SISMOS_VS_A4.md). Código: `auditoria_catalogo_sismos_vs_a4.py`. Salida: `auditoria_catalogo_sismos_vs_a4.json`.

## Qué es el catálogo (verificado al descargarlo)
16.290 eventos de la capa de «solución preferida» (`f25_capa_sols_pref`): 31 anteriores a 1900, 4.434 de 1900-1992 y 11.825 de 1993-2020 (unos 300-600 por año; el último evento es de diciembre de 2020). Cubre un recuadro (latitud −6 a 16, longitud −84 a −66) que incluye mar y países vecinos: solo **5.761** de los eventos de 1993-2020 caen dentro de un polígono municipal continental. Magnitud mínima 3,5, así que la magnitud de completitud por máxima curvatura sale en 3,5 (el borde del catálogo): **no puedo estimar la completitud**. No verifiqué si es el catálogo completo de la Red Sismológica Nacional o una selección.

## Resultados (1.113 municipios del A-4 con polígono; M ≥ 4,0; 2.256 eventos)
| Criterio | Resultado | ¿Se cumple? |
|---|---|---|
| **C1** ρ(Aa, tasa de eventos por área) > 0, IC excluye 0 | **+0,21** [+0,11; +0,34] | Sí |
| **C2** la tasa **mediana** crece de Baja a Intermedia a Alta | Mediana 0 en las tres zonas | **No, tal como lo escribí** |

C2 no se cumple de forma trivial: el 67 % de los municipios no tiene **ningún** evento M ≥ 4,0 en 28 años, así que la mediana es 0 en todas las zonas. Esa definición era mala (no la anticipé). Como descripción adicional, **fijada después de ver los datos y por tanto no confirmatoria**: la fracción de municipios con al menos un evento sí crece con la zona, **23 % (Baja), 28 % (Intermedia), 39 % (Alta)**. La razón entre la tasa media de las zonas Alta y Baja es 23 con un IC95 % de [2,5; 103], demasiado ancho para decir cuánto.

## Sensibilidad
| Variante | Eventos | ρ (Aa, tasa) [IC95 %] |
|---|---:|---|
| M ≥ 3,5 | 5.738 | +0,24 [+0,12; +0,37] |
| **M ≥ 4,0 (primaria)** | 2.256 | **+0,21 [+0,11; +0,34]** |
| M ≥ 4,5 | 774 | +0,25 [+0,15; +0,35] |
| M ≥ 4,0 y profundidad ≤ 70 km | 663 | +0,13 [+0,03; +0,24] |

La asociación es positiva y débil en todas las variantes; con solo sismos someros baja a +0,13.

## Descriptivo
- **332 de 543 municipios en zona Alta (61 %) no tienen ningún evento M ≥ 4,0** en 1993-2020. El catálogo no puede «confirmar» el Aa en la mayoría de los municipios de zona Alta; esto es lo esperable porque el Aa se basa en sismos grandes y raros.
- **Zona Baja con sismicidad en el decil más alto:** 3 municipios (Barranquilla, Candelaria y Manaure del Cesar), cada uno con **un solo evento**. Con un evento, la tasa depende del área del municipio; no es una señal.

## Qué concluyo y qué no
El catálogo apunta en el mismo sentido que el Aa (más sismicidad registrada donde el Aa es mayor), pero débilmente. **No valida ni cuestiona el Aa**: 28 años de sismos pequeños y medianos no son la base de un valor de diseño a 475 años, y el 49 % de los eventos cae fuera de los municipios (mar, vecinos).

## Límites
No se declusteriza (réplicas y enjambres inflan conteos). La detección depende de la densidad de estaciones. No verifiqué la completitud del catálogo. Los municipios costeros pierden la sismicidad costa afuera. El C2 original fue una mala definición y se reporta como no cumplido.
