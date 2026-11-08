# Protocolo: ¿se reproduce el mapa municipal de intensidad máxima observada del SGC desde sus puntos de intensidad histórica? (fijado el 2026-11-08, antes de descargar los puntos)

**Contexto.** El SGC publica el catálogo de sismicidad histórica (`sismicidad_historica_2`): 89 sismos con epicentro y magnitud, 3.405 puntos de intensidad por sitio (`f15_capa_intensidad`) y 1.430 puntos de intensidad máxima (`f15_capa_intensidad_max`). El «mapa de intensidad máxima observada» municipal (ya usado en `RESULTADOS_INTENSIDAD_VS_A4.md`) casi con seguridad **proviene de esos mismos datos**; por eso cruzar la sismicidad histórica con el A-4 no es independiente de ese resultado.

**Pregunta (control de consistencia del producto):** si tomo el máximo de `VALOR_INTENSIDAD` de los puntos que caen en cada municipio (polígonos IGAC), ¿recupero el `GRIDCODE` del mapa municipal del SGC?

**Medidas fijas:** (a) % de municipios con coincidencia exacta tras redondear el valor al entero más cercano; (b) % con diferencia ≤ 1; (c) ρ de Spearman. Solo municipios con al menos un punto y categoría `M` en el mapa. Se usa `f15_capa_intensidad_max` como primaria y la unión de las dos capas como sensibilidad.

**Criterio fijado:** el mapa «se reproduce» si la coincidencia con diferencia ≤ 1 es ≥ 90 % y ρ ≥ 0,9. Si no, se describen los patrones de discrepancia sin atribuir una causa.

**Qué NO se concluye:** nada sobre la calidad de las intensidades históricas, solo sobre si el mapa municipal se deriva de estos puntos. El SGC puede haber interpolado o suavizado el mapa; en ese caso no se reproducirá aunque ambos sean correctos.

**Limitaciones:** la escala de intensidad (campo `ESCALA`) no está documentada en el servicio; puntos con sitio mal ubicado caen en el municipio equivocado; municipios sin puntos quedan fuera.
