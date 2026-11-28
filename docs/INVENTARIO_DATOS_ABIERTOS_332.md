# Inventario verificado de datos abiertos para ingeniería civil (#332, fase 1), 2026-11-28

**Qué es y qué no es.**
- Es la fase 1 de #332: qué contiene cada fuente, su licencia (texto exacto), formato, cobertura, frecuencia, tamaño
  aproximado y para qué issue sirve.
- Es solo lectura: se leyeron **metadatos y términos de uso**, no se descargó ningún conjunto de datos.
- Amplía [INVENTARIO_DATOS_COLOMBIA.md](INVENTARIO_DATOS_COLOMBIA.md) (2026-11-08), que dejó la licencia de cada
  conjunto como «por verificar».
- No es un concepto jurídico. Donde la licencia impide o condiciona el uso comercial, se marca y la decisión queda para
  Wilmer.

**Cómo se verificó.**
- **datos.gov.co:** `scripts/inventario/metadatos_fuentes_332.py` lee, por conjunto, `/api/views/<id>.json` (licencia,
  entidad, cobertura, frecuencia, fecha, columnas) y `count(*)` (filas). Revisó 62 conjuntos: 13 que ya usa o nombra el
  proyecto y los que salieron al buscar por tema. Salida completa: `scripts/inventario/metadatos_fuentes_332.json`.
- **Portales propios** (SGC, Aerocivil, Copernicus, USGS/NASA, IGAC, IDEAM, UNGRD, DANE): lectura de sus páginas de
  términos. Los PDF de licencia se pasaron a texto localmente con `python -I`.
- Las páginas que no cargaron están en el §6. Ninguna fila se llenó con un valor supuesto.

## 1. Hallazgos que cambian decisiones

1. **El SGC no tiene licencia abierta para sus datos geocientíficos.**
   - Sus *Términos generales y condiciones para el uso de productos/información/datos/servicios que se acceden del SGC*
     dicen que el SGC «concede licencia de uso para un fin específico y determinado».
   - Que «el LICENCIADO no está autorizado a hacer copias de la información suministrada» (2.3).
   - Y que «no comercializará o intercambiará los productos, información, datos y servicio alguno derivado o resultado de
     la incorporación de los datos sin autorización expresa por escrito» (5.1).
   - Sus *Condiciones sobre la propiedad intelectual* agregan que la información geocientífica «no podrá reproducirse
     total o parcialmente sin el permiso expreso [...] aún si no se está reproduciendo con propósitos comerciales».
   - El *Aviso de derechos de autor 2024*, que menciona CC BY 4.0, rige las **publicaciones de sus autores**
     (revistas, libros), no los datos de los servicios ArcGIS.
   - **Qué afecta en StructAI hoy:**
     - `packages/construdata/sgc_amenaza_sismica.py`, con la copia en la tabla `sgc_amenaza_sismica_municipios`;
     - `sgc_movimientos_masa.py` (SIMMA);
     - `sitio_territorial.py` y los scripts de `scripts/satelite/` que bajan el mapa de amenaza por movimientos en masa
       1:100.000. Ese mapa es justo el producto que nombra la plantilla de licencia del SGC.
   - **Ruta propuesta:**
     - (a) Aa, Av, Ae y Ad por municipio salen del **Apéndice A-4 de la NSR-10**. Es un decreto, un texto oficial, y el
       proyecto ya lo audita contra el SGC (`scripts/ingesta/nsr10/auditoria_a4_vs_sgc.py`). Se puede tomar de ahí y no
       del servicio del SGC.
     - (b) Para el SIMMA y el mapa de movimientos en masa, pedir **autorización escrita al SGC** para uso en un producto
       comercial. La carta la envía Wilmer.
     - (c) Hasta entonces, no ampliar el uso de capas del SGC en producción.
2. **datos.gov.co publica casi todo con CC BY-SA 4.0, no con CC BY:** 60 de 62 conjuntos.
   - El texto de los metadatos es «Creative Commons Attribution | Share Alike 4.0 International».
   - Las excepciones:
     - `2343-nuqp` (Emergencias UNGRD V2) tiene CC BY 4.0;
     - `psyr-i7bp` (Licencias urbanísticas, SNR) tiene CC BY-ND 4.0. Esta **prohíbe obras derivadas**, así que no sirve
       para combinarla.
   - El «compartir igual» obliga a publicar con la misma licencia el **material adaptado que se comparta**, por ejemplo
     una capa de techo aeronáutico construida con esos datos.
   - Usarlos internamente para calcular no obliga a nada, pero la atribución sí es obligatoria.
   - Es el mismo caso que ODbL (#332): **se marca y se decide caso por caso**. Propuesta de regla:
     - las capas derivadas que StructAI publique llevan CC BY-SA 4.0 y la atribución;
     - las respuestas a usuarios citan la fuente.
3. **Copernicus DEM sí permite el uso comercial**, con avisos obligatorios.
   - La licencia (Art. 4) concede reproducción, distribución, comunicación al público y «adaptation, modification and
     combination with other data», sin costo (Art. 5).
   - El Art. 6 obliga a un aviso de fuente, a un aviso distinto si el dato se modificó y a una frase de exención de
     responsabilidad. Los textos están en el §3.
   - Es un **modelo de superficie**: incluye edificios y árboles, no es terreno desnudo. Para Kzt y pendientes urbanas
     hay que tenerlo en cuenta.
4. **Aerocivil:** el RAC 14 vigente tiene fecha de entrada en vigencia **30/07/2026** según el listado oficial de RAC.
   - Su PDF no se pudo leer (HTTP 403).
   - Los enlaces conocidos del AIP (AMDT 67 y el índice) devuelven 404: la Aerocivil cambió su sitio.
   - El trámite de altura existe: «Permiso para levantar construcciones o plantaciones» (Código de Comercio, arts.
     1823–1826).
   - La fase 2 (piloto de Barranquilla) **no puede arrancar** hasta tener el RAC 14 vigente y el AD 2 SKBQ vigente. Hay
     que pedirle a Wilmer que los descargue desde el navegador.
5. **POT municipales:** no se confirmó ningún servicio público de alturas o tratamientos para Barranquilla, Bogotá,
   Medellín ni Cartagena.
   - Respuestas de los portales:
     - Barranquilla: `barranquilla.gov.co/planeacion` devolvió 403;
     - Bogotá: `datosabiertos.bogota.gov.co` devolvió 500;
     - Medellín: GeoMedellín devolvió 404.
   - IDECA (Bogotá) carga, pero solo muestra «Todos los derechos reservados».
   - En datos.gov.co, Barranquilla tiene «Barrios según POT» y «Perfiles viales», pero no alturas.
   - La restricción urbanística de #325 sigue sin fuente abierta verificada.

## 2. Tabla por fuente

**Tamaño:** «MB» es una estimación gruesa del CSV (filas × columnas × 15 bytes), solo un orden de magnitud. «Licencia» es
el texto exacto que publica la fuente. **Apto comercial:**
- **Sí:** licencia abierta que permite uso comercial.
- **SA:** permite el uso comercial, con «compartir igual».
- **No:** no lo permite sin autorización.
- **?:** sin licencia verificable.

### 2.1 Aerocivil (techo aeronáutico, #325)
| Conjunto | URL oficial | Licencia | Formato | Cobertura / frecuencia | Tamaño | Apto | Issue |
|---|---|---|---|---|---|---|---|
| RAC 14 Aeródromos, Aeropuertos y Helipuertos | [listado RAC](https://www.aerocivil.gov.co/autoridad_aeronautica/normatividad/13-reglamentos-aeronauticos-de-colombia-rac) | Norma (texto oficial) | PDF | Nacional; vigencia 30/07/2026 | — (PDF con 403) | Sí (norma) | #325 |
| AIP Colombia, AD 2 SKBQ (Ernesto Cortissoz) | índice AIP de aerocivil.gov.co (enlaces con 404) | Sin verificar; hay «Política de derechos de autor» (PDF del 21/07/2025, no leído) | PDF por sección, ciclo AIRAC | Nacional; cada 28 días | — | ? | #325 |
| Permiso para levantar construcciones o plantaciones | [trámite](https://www.aerocivil.gov.co/autoridad_aeronautica/publicaciones/3783/permiso-para-levantar-construcciones-o-plantaciones/) | Trámite (no es dato) | Web / SUIT | — | — | — | #325 (validación) |
| Operaciones aéreas acumuladas (`jh8x-n6h6`) | [datos.gov.co](https://www.datos.gov.co/d/jh8x-n6h6) | CC BY-SA 4.0 | Tabla | Nacional; trimestral; 2026-11-24 | 639.976 × 11; ~106 MB | SA | (no aplica a alturas) |

### 2.2 SGC (sismo, suelos, movimientos en masa: #327, #43, taludes)
| Conjunto | URL oficial | Licencia | Formato | Cobertura | Tamaño | Apto | Issue |
|---|---|---|---|---|---|---|---|
| Servicios ArcGIS (53 carpetas: `Zonas_amenaza_Sismica_NR10`, `catalogo_sismos`, `SIMMA`, `Mapa_Nacional_Amenaza_Mov_Masa_100K`, `Geomecanica_Por_Regiones`, `Mapa_Geologico_Colombia_2015`…) | `srvags.sgc.gov.co/arcgis/rest/services` | «licencia de uso para un fin específico y determinado»; prohíbe copiar y comercializar derivados sin autorización escrita (ver §1.1) | ArcGIS REST (JSON, sin descarga masiva) | Nacional | 3.020 capas (inventario del 2026-11-08) | **No** | #327, #43, taludes |
| Red Nacional de Acelerógrafos (RNAC) | por solicitud al SGC | Misma política | — | — | — | **No** (sin autorización) | #327 |
| Registros administrativos del SGC en datos.gov.co (activos de información, museo) | [b3vx-5vd2](https://www.datos.gov.co/d/b3vx-5vd2) y otros | CC BY-SA 4.0 | Tabla | — | 10.868 filas | SA | (no son datos geocientíficos) |
| **Alternativa:** Aa, Av, Ae, Ad por municipio | NSR-10, Apéndice A-4 (decreto) | Norma | PDF oficial (ya en local) | 1.122 municipios | — | Sí | #327 |

### 2.3 IDEAM (hidrología, viento: #320)
| Conjunto | Id | Licencia | Cobertura / frecuencia / actualizado | Tamaño | Apto | Issue |
|---|---|---|---|---|---|---|
| Precipitación (telemetría) | [s54a-sgyg](https://www.datos.gov.co/d/s54a-sgyg) | CC BY-SA 4.0 | Nacional; diaria; 2026-11-27 | 297 M filas × 12; ~53 GB | SA | #320, hidrología |
| Velocidad del viento | [sgfv-3yp8](https://www.datos.gov.co/d/sgfv-3yp8) | CC BY-SA 4.0 | Nacional; diaria; 2026-11-27 | 179 M filas × 12; ~32 GB | SA | **#320** |
| Dirección del viento | [kiw7-v9ta](https://www.datos.gov.co/d/kiw7-v9ta) | CC BY-SA 4.0 | Nacional; diaria; 2026-11-27 | `count(*)` sin respuesta (muy grande) | SA | #320 |
| Nivel instantáneo del río | [bdmn-sqnh](https://www.datos.gov.co/d/bdmn-sqnh) | CC BY-SA 4.0 | Nacional; diaria | 21,9 M × 12; ~3,9 GB | SA | hidrología |
| Normales climatológicas | [nsz2-kzcq](https://www.datos.gov.co/d/nsz2-kzcq) | CC BY-SA 4.0 | Nacional; anual; 2026-10-13 | 16.761 × 24; ~6 MB | SA | #320 |
| Catálogo nacional de estaciones | [hp9r-jxuu](https://www.datos.gov.co/d/hp9r-jxuu) | CC BY-SA 4.0 | Nacional; diaria | 29.320 × 19; ~8 MB | SA | #320 |
| Datos de estaciones IDEAM y terceros | [57sv-p2fu](https://www.datos.gov.co/d/57sv-p2fu) | CC BY-SA 4.0 | Nacional; diaria | 160.878 × 13; ~31 MB | SA | #320 |
| DHIME (series convencionales desde 1929) | dhime.ideam.gov.co | **Sin licencia publicada** (los «términos» del sitio son la política de datos personales) | Descarga web por estación | Nacional | — | ? | hidrología, H-F |

Las series de telemetría son crudas, sin validar (inventario del 2026-11-08). Para viento de diseño (#320), primero hay
que filtrar por estación y periodo. La consulta se hace por API filtrada, nunca bajando los 32 GB.

### 2.4 DANE, IGAC, datos.gov.co (municipios, predios, precios)
| Conjunto | Id / URL | Licencia | Cobertura / frecuencia | Tamaño | Apto | Issue |
|---|---|---|---|---|---|---|
| DIVIPOLA, códigos de municipios (DANE) | [gdxc-w37w](https://www.datos.gov.co/d/gdxc-w37w) | CC BY-SA 4.0 | Nacional; semestral; 2025-01-24 | 1.122 × 7 | SA | todos (clave territorial) |
| Transacciones inmobiliarias (IGAC) | [7y2j-43cv](https://www.datos.gov.co/d/7y2j-43cv) | CC BY-SA 4.0 | Nacional; anual; 2025-04-04 | 30,9 M × 26; ~12 GB | SA; **solo agregados** | #196–#200 |
| Gestores catastrales (IGAC) | [bhcx-bx97](https://www.datos.gov.co/d/bhcx-bx97) | CC BY-SA 4.0 | Nacional; anual | 1.122 × 28 | SA | predios |
| Registro uno alfanumérico Galapa, Juan de Acosta, Puerto Colombia y Piojó (AMB) | [qdbg-jqav](https://www.datos.gov.co/d/qdbg-jqav) | CC BY-SA 4.0 | Área metropolitana; trimestral | 201.239 × 14 | SA; **revisar campos de propietarios antes de usar** | #325 (Atlántico) |
| Colombia en Mapas / cartografía básica (IGAC) | [colombiaenmapas.gov.co](https://www.colombiaenmapas.gov.co/) | «Cada dato dispuesto en la plataforma tiene su licencia de uso»; las imágenes de uso gubernamental «no puede ser compartida ni comercializada con empresas privadas» | Visor / descarga por capa | Nacional | — | Por capa; imágenes **No** | topografía |
| Licencias urbanísticas (SNR) | [psyr-i7bp](https://www.datos.gov.co/d/psyr-i7bp) | CC BY-ND 4.0 | Nacional; cuatrimestral | 10.418 × 13 | **No para derivados** | #325 |
| Licencias de construcción municipales (Fusagasugá, Chía, San Pedro, Belalcázar) | `7fsy-xzzb`, `n686-d6yb`, `8ijs-g3kz`, `bsqe-umzr` | CC BY-SA 4.0 | Municipal | < 5.000 filas cada uno | SA | #325 |
| ICOCED / ICOCIV (DANE) | página del DANE | Términos del DANE: 404, sin verificar | Boletín y anexos | Nacional; mensual | — | ? | #196–#200 |
| SECOP II contratos / adiciones | [jbjy-vk9h](https://www.datos.gov.co/d/jbjy-vk9h), [cb9c-h8sn](https://www.datos.gov.co/d/cb9c-h8sn) | CC BY-SA 4.0 | Nacional; diaria | 5,7 M × 95 (~8 GB); 8,6 M × 5 | SA; seudonimizar entidades (regla vigente) | #196–#200 |

### 2.5 UNGRD, INVIAS y ANI
| Conjunto | Id | Licencia | Cobertura / frecuencia | Tamaño | Apto | Issue |
|---|---|---|---|---|---|---|
| **Emergencias UNGRD V2** | [2343-nuqp](https://www.datos.gov.co/d/2343-nuqp) | **CC BY 4.0** | Nacional; anual; 2026-11-06 | 6.506 × 61; ~6 MB | **Sí** | dónde fallan las obras |
| Emergencias UNGRD 2023–2024 | [rgre-6ak4](https://www.datos.gov.co/d/rgre-6ak4) | CC BY-SA 4.0 | Nacional; anual | 16.036 × 69 | SA | ídem |
| Emergencias UNGRD (histórico) | [wwkg-r6te](https://www.datos.gov.co/d/wwkg-r6te) | CC BY-SA 4.0 | Nacional; anual; 2023-09-07 | 25.857 × 71 | SA | ídem |
| Consolidado anual de emergencias 1998–2025 | [portal UNGRD](https://portal.gestiondelriesgo.gov.co/Paginas/Consolidado-Atencion-de-Emergencias.aspx) | Sin licencia abierta: «información [...] pública en los términos señalados en la Ley 1712 de 2014»; la UNGRD «se reserva todos los derechos de autor» | .xls por año | Nacional | — | ? | ídem |
| Red vial INVIAS | [ie7y-asdn](https://www.datos.gov.co/d/ie7y-asdn) | CC BY-SA 4.0 | Nacional; anual; 2026-11-19 | 715 × 18 | SA | #106 |
| Peajes INVIAS | [68qj-5xux](https://www.datos.gov.co/d/68qj-5xux) | CC BY-SA 4.0 | Nacional; anual | 179 × 44 | SA | #106 |
| Tráfico vehicular ANI | [8yi9-t44c](https://www.datos.gov.co/d/8yi9-t44c) | CC BY-SA 4.0 | Nacional; semestral; 2026-09-02 | 149.944 × 9; ~20 MB | SA | #106 |

### 2.6 POT e IDE municipales (restricción urbanística, #325)
| Ciudad | Qué se encontró | Licencia | Apto |
|---|---|---|---|
| Barranquilla | En datos.gov.co: «Barrios de Barranquilla según POT» (`qui6-qeux`, 189 filas) y «Perfiles viales» (`aj6f-wwpi`, 258), CC BY-SA 4.0. **Sin capa de alturas ni tratamientos.** El portal de Planeación respondió 403 y `geoportal.barranquilla.gov.co` no existe en el DNS. | SA (lo encontrado) | Sin fuente de alturas |
| Bogotá | IDECA carga (visor, metadatos, catálogo de servicios dinámico), pero solo muestra «Todos los derechos reservados». Datos Abiertos Bogotá dio 500. | ? | Sin verificar |
| Medellín | GeoMedellín y la página de geografía dieron 404. | ? | Sin verificar |
| Cartagena | No se encontró una URL oficial que se pudiera verificar. | ? | Sin verificar |

### 2.7 Modelos de elevación (Kzt, pendientes)
| Conjunto | URL | Licencia | Formato / tamaño | Apto |
|---|---|---|---|---|
| Copernicus DEM GLO-30 | [registro AWS](https://registry.opendata.aws/copernicus-dem/), bucket `s3://copernicus-dem-30m` | Licencia Copernicus WorldDEM-30 (2020-10-29): reproducción, distribución, adaptación y combinación sin costo, con los avisos del Art. 6 | GeoTIFF optimizado para la nube, teselas de 1°; **modelo de superficie**; algunas teselas no son públicas (Armenia, Azerbaiyán) | **Sí** (con avisos) |
| SRTM 1 arc-seg (USGS EROS) | [USGS](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1), DOI 10.5066/F7PR7TFT | «Sources/Usage: Public Domain» (USGS); NASA: CC0 para misiones lideradas por NASA | GeoTIFF por tesela | **Sí** (se pide citar) |

## 3. Avisos obligatorios que StructAI debe mostrar si usa estos datos

- **Copernicus DEM, dato modificado** (pendientes, Kzt):
  > "produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided
  > under COPERNICUS by the European Union and ESA; all rights reserved"
- **Copernicus DEM, exención de responsabilidad** (Art. 6c):
  > "The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any
  > use of the Copernicus WorldDEM-30"
- **Copernicus DEM, sin aparentar respaldo oficial** (Art. 6d): no dar a entender que el programa Copernicus respalda a
  StructAI.
- **CC BY-SA 4.0 y CC BY 4.0 (datos.gov.co):** dar el nombre de la entidad, el título del conjunto, el enlace a la
  licencia e indicar si hubo cambios. Con BY-SA, lo adaptado que se comparta va con la misma licencia.
- **SRTM:** cita recomendada con el DOI.

## 4. Qué sirve para cada issue

| Issue | Fuente verificada y apta | Bloqueo |
|---|---|---|
| #325 techo aeronáutico | RAC 14 (norma) + AIP SKBQ | Los dos PDF hay que bajarlos a mano (403/404) |
| #325 restricción POT | — | No hay fuente abierta verificada de alturas para ninguna de las 4 ciudades |
| #325 altura por sistema estructural | NSR-10 A.3 (norma, ya en local) | — |
| #320 viento | IDEAM `sgfv-3yp8` / `kiw7-v9ta` (SA), por API filtrada | Telemetría cruda; definir filtro de calidad |
| #327 suelo y sismo | NSR-10 A-4 (Aa/Av) | Capas del SGC: **autorización escrita** |
| #196–#200 precios | SECOP II (SA, seudonimizado), transacciones IGAC (SA, agregados) | ICOCIV: términos del DANE sin verificar |
| #106 vías | INVIAS red vial y peajes, tráfico ANI (SA) | — |
| Kzt / pendientes | Copernicus DEM (avisos) o SRTM (dominio público) | El DEM es de superficie: en ciudad sobreestima la cota del terreno |
| Fallas de obra | UNGRD V2 `2343-nuqp` (CC BY 4.0) | — |

## 5. Decisiones que quedan para Wilmer

1. **SGC:**
   - ¿Pasamos Aa/Av al Apéndice A-4 de la NSR-10 y dejamos de leer `srvags` en producción?
   - ¿Le escribimos al SGC pidiendo autorización para el SIMMA y el mapa de movimientos en masa? Yo redacto la carta y
     la envías tú.
2. **CC BY-SA:** ¿se acepta la regla «capas derivadas publicadas con CC BY-SA 4.0 + atribución»?
3. **Aerocivil:** bajar desde el navegador el PDF del RAC 14 vigente y el AD 2 SKBQ vigente. Van a
   `C:\Users\wilme\dev\descargas\aerocivil\`.
4. **POT:** ¿pedimos por derecho de petición (Ley 1712) la capa de alturas y tratamientos del POT de Barranquilla
   (Decreto 0212 de 2014)?

## 6. No verificado (páginas que no cargaron)

| URL | Respuesta |
|---|---|
| Índice AIP y AD 2 SKBQ (AMDT 67) en aerocivil.gov.co | 404 |
| Visor PDF del RAC 14 (`id=16891`) | 403 |
| barranquilla.gov.co/planeacion | 403 |
| geoportal.barranquilla.gov.co | DNS inexistente |
| datosabiertos.bogota.gov.co | 500 |
| GeoMedellín y medellin.gov.co/geografia | 404 |
| Términos y condiciones del DANE | 404 |
| Destino de la redirección de DHIME | No se siguió |
| Política editorial de la UNGRD (PDF) | No leída |
