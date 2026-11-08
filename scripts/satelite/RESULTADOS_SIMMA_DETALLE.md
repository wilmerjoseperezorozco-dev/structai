# SIMMA: amenaza por movimientos en masa a mayor detalle que el mapa nacional (2026-11-08)

**Pregunta:** ¿ordena mejor los eventos de la UNGRD el mapa de amenaza de SIMMA a 1:25.000 que el índice nacional a 1:100.000 (§26)?

**Respuesta: no se puede probar con estos datos.** No se ejecutó ninguna comparación; esto es lo verificado.

- **1:25.000** (`SIMMA/ZonificacionAmenazaCache`, capa 9): 5.501 polígonos de amenaza relativa (muy baja a muy alta). Los descargué simplificados (10 MB) y calculé su cobertura sobre los 1.120 polígonos municipales del IGAC, **sin mirar eventos**. Solo **59 municipios** tienen algún polígono, **12 tienen ≥ 10 % de su área cubierta** y **11 ≥ 50 %**, en su mayoría de Norte de Santander (códigos 54xxx), con Popayán y Soacha. Con n = 12 un contraste con ρ e IC por departamento no tiene potencia. La amenaza es **relativa a cada estudio**, no comparable entre zonas.
- **1:100.000** (capa 11): 890 polígonos. Es el mismo mapa nacional ya contrastado en la §26 (el índice por municipio de `Municipios_100K`), solo que en forma de polígonos. Su descarga pesó **733 MB** con una simplificación de ~600 m, no cabe cargarla en memoria en este equipo (0,8 GB libres), y no aporta información nueva, así que **la borré** (caché no versionado).

**Conclusión:** la capa de detalle de SIMMA existe, pero cubre unos pocos municipios y no permite repetir la comparación nacional. Solo serviría para estudios locales (por ejemplo Cúcuta y su área). Scripts: `bajar_simma_amenaza.py`, `simma_cobertura.py`; cobertura en `simma_25k_cobertura_municipal.json`.
