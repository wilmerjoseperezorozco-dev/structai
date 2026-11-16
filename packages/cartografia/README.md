# cartografia: georreferenciación IGAC con origen local (issue #211)

**Sistema oficial:** MAGNA-SIRGAS 2018 / Origen-Nacional, **EPSG:9377**, también llamado CTM12 (Res. IGAC 471 y 529 de 2020; Res. 370 de 2021).

**El problema:** cerca de E = 5.000.000 m, un `float32` solo distingue saltos de **0,5 m**. Si un visor CAD, IFC o WebGL guarda los vértices en `float32`, la geometría "salta".

**La solución:** dibujar en coordenadas locales `(E − E0, N − N0, H − H0)` y guardar el punto base real en el archivo. La prueba `test_float32_pierde_decimetros_en_oficial_y_no_en_local` muestra la diferencia: en coordenadas oficiales el error llega a decímetros; en locales queda por debajo de 0,03 mm.

| Módulo | Qué hace |
|---|---|
| `georef.py` | Proyecta a EPSG:9377 desde WGS84, MAGNA geográfico o las zonas MAGNA antiguas (3114–3118). También: `PuntoBase` (rotación y escala con la convención de IfcMapConversion), `punto_base_desde` (centro del envolvente redondeado) y `proyectar_a_local`. |
| `dxf_georef.py` | Escribe el punto base en tres sitios: XRECORD `STRUCTAI_GEOREF` (fuente de verdad), variables `$CUSTOMPROPERTY` `STRUCTAI_*` y, opcionalmente, GEODATA. Fija `$INSUNITS` en metros. Lo lee de vuelta con `leer_georef`. |
| `ifc_georef.py` | IFC4: `IfcMapConversion` + `IfcProjectedCRS` (`EPSG:9377`). IFC2X3: `ePSet_MapConversion` / `ePSet_ProjectedCRS` en IfcSite. Incluye la lectura de vuelta. |
| `capas.py` + `data/catalogo_capas.json` | Catálogo versionado `DISCIPLINA-ELEMENTO[-ESTADO]` y `aplicar_catalogo(doc)`. `validar_dxf(doc)` reporta capas estándar, mapeables (con su propuesta) y sin mapear. El mapeo es una propuesta: no renombra capas sin confirmación. |

## Verificación (58 pruebas)

- **Referencia independiente.** La serie de Krüger para Transversa de Mercator (orden n⁶) está escrita en la prueba a partir de los parámetros de EPSG, sin pyproj. Coincide con pyproj en menos de 1 mm en Bogotá, Barranquilla, Leticia, San Andrés, Puerto Carreño y Pasto.
- **El origen de la proyección es exacto:** (−73°, 4°) da (5.000.000, 2.000.000).
- **Ida y vuelta** oficial → local → oficial en menos de 1 mm, con rotación y escala, y también a través de DXF y de IFC guardados en disco.
- **El IFC georreferenciado (IFC4 e IFC2X3) pasa el validador de esquema** de ifcopenshell.

## Pendiente (criterio de hecho del issue)

- Abrir un DXF con GEODATA en Civil 3D o QGIS y confirmar que se ubica bien. Por eso GEODATA viene desactivado por defecto: su definición de sistema de coordenadas usa el WKT de EPSG, no el XML de Autodesk.
- Comparar con los **puntos de control publicados por el IGAC**: coordenadas oficiales de vértices de la red MAGNA-ECO.
- **Validar la convención de capas** con colegas y alinearla con el catálogo de objetos de la Res. IGAC 471 de 2020.
- **Migración `infra/supabase/migrations/20261115120000_proyecto_georreferencia.sql`:** está escrita, **sin aplicar**, y espera aprobación.
