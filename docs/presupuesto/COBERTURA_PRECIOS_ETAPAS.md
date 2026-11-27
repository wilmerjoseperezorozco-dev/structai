# Cobertura de precios de StructAI por etapa y capítulo

Generado por `scripts/presupuesto/cobertura_etapas.py` (solo lectura) contra `apu_precios_referencia`, con la taxonomía `packages/motor-apu/data/taxonomia_etapas_presupuesto.json`. Clasificación por palabras clave (línea base): sirve para ver huecos, no como etiqueta definitiva.

- Filas totales: **4566**. Insumos sueltos de ferretería (IAD): **1754**, fuera del conteo.
- Actividades con APU o precio de obra: **2812**; clasificadas: **1846** (66%); sin clasificar: **966**; con más de un capítulo posible: **374**.

| Etapa | Capítulo | Actividades | Con desglose MO/materiales | Regiones (top 3) | Motores | Normas que faltan | Issues |
|---|---|---|---|---|---|---|---|
| 0. Costos indirectos y transversales | 0.1 AIU (administración, imprevistos y utilidad) | 0 | 0 | — | motor-apu (AIU con valor por defecto, sin calibrar por tipo de proyecto) | Decreto 1625 de 2016, art. 1.3.1.7.9 (IVA en construcción); IDU GU-DP-017 (guía, no norma) | — |
| 0. Costos indirectos y transversales | 0.2 Gastos generales, PMA, SST, PMT y gestión social | 11 | 0 | Barranquilla 11 | **ninguno** | Resolución 0312 de 2019 (estándares mínimos SG-SST); Resolución 1257 de 2021 (RCD) | — |
| 0. Costos indirectos y transversales | 0.3 Supervisión técnica, interventoría y trámites | 3 | 0 | Barranquilla 3 | motor-geotecnia, motor-topovia | Ley 1796 de 2016 (vivienda segura, revisión independiente) | — |
| 0. Costos indirectos y transversales | 0.4 Equipos y herramienta (alquiler y compra) | 11 | 0 | Barranquilla 9, Puerto Colombia 2 | **ninguno** | Resolución 4272 de 2021 (trabajo en alturas) | — |
| 1. Fase inicial y obra negra | 1.1 Preliminares | 59 | 2 | Barranquilla 43, Puerto Colombia 15, Atlántico 1 | motor-topovia (replanteo) | Resolución 1257 de 2021 (gestión de RCD de demoliciones) | — |
| 1. Fase inicial y obra negra | 1.2 Excavación y movimiento de tierras | 97 | 4 | Atlántico 37, Barranquilla 32, Puerto Colombia 28 | motor-geotecnia, motor-geopot (proctor, CBR, USCS), motor-licuacion | Resolución 1257 de 2021 (RCD) | — |
| 1. Fase inicial y obra negra | 1.3 Cimentación | 32 | 3 | Barranquilla 21, Puerto Colombia 11 | motor-geotecnia (capacidad portante), motor-concreto (cantidades), motor-apu.cantidades | — | #149, #136 |
| 1. Fase inicial y obra negra | 1.4 Estructura en concreto | 79 | 14 | Barranquilla 55, Puerto Colombia 16, Atlántico 8 | motor-concreto, motor-estructural, motor-analisis, motor-apu.cantidades | — | #122, #142, #149 |
| 1. Fase inicial y obra negra | 1.5 Estructura metálica | 6 | 0 | Barranquilla 4, Puerto Colombia 2 | motor-acero-frio (F.4) | — | #141, #121 |
| 1. Fase inicial y obra negra | 1.6 Mampostería | 66 | 6 | Barranquilla 45, Puerto Colombia 19, — 2 | motor-vulnerabilidad-vivienda | — | #141, #184 |
| 1. Fase inicial y obra negra | 1.7 Cubierta e impermeabilización | 102 | 20 | Barranquilla 85, Puerto Colombia 10, Atlántico 6 | **ninguno** | — | #121, #146 |
| 2. Obra gris (instalaciones) | 2.1 Instalaciones hidrosanitarias | 560 | 32 | Barranquilla 421, Puerto Colombia 88, Atlántico 42 | motor-aquai (redes externas, bombeo, ariete), motor-redes | Resolución 0194 de 2025 (ahorro de agua en edificaciones nuevas) | #138, #139 |
| 2. Obra gris (instalaciones) | 2.2 Red contra incendio | 11 | 2 | Atlántico 9, Barranquilla 2 | **ninguno** | NTC 1669 / NFPA 13 y 14 | — |
| 2. Obra gris (instalaciones) | 2.3 Instalaciones de gas | 2 | 0 | Barranquilla 2 | **ninguno** | Resolución 90902 de 2013 (instalaciones internas de gas); NTC 2505 | — |
| 2. Obra gris (instalaciones) | 2.4 Instalaciones eléctricas | 71 | 6 | Barranquilla 64, — 7 | **ninguno** | RETIE (Res. 40117 de 2024 y modificaciones); NTC 2050 (código eléctrico); RETILAP (iluminación); NTC 4552 (protección contra rayos) | #143 |
| 2. Obra gris (instalaciones) | 2.5 Comunicaciones y redes de datos | 1 | 1 | Barranquilla 1 | **ninguno** | RITEL (Res. CRC 5050 de 2016, Anexo 8.1, act. Res. 7930 de 2025) | — |
| 2. Obra gris (instalaciones) | 2.6 Equipos especiales | 0 | 0 | — | **ninguno** | NTC 5926 (ascensores) | — |
| 3. Obra blanca (acabados) | 3.1 Pañetes, estucos y pinturas | 65 | 6 | Barranquilla 49, Puerto Colombia 11, — 5 | **ninguno** | NTC 1335 (pinturas tipo emulsión) | — |
| 3. Obra blanca (acabados) | 3.2 Pisos y enchapes | 103 | 14 | Barranquilla 94, — 5, Puerto Colombia 4 | **ninguno** | NTC 919 / ISO 13006 (baldosas cerámicas) | — |
| 3. Obra blanca (acabados) | 3.3 Carpintería, ventanería y cerrajería | 112 | 20 | Barranquilla 103, — 5, Atlántico 4 | **ninguno** | — | — |
| 3. Obra blanca (acabados) | 3.4 Cielorrasos | 37 | 6 | Barranquilla 32, Puerto Colombia 4, — 1 | **ninguno** | — | — |
| 3. Obra blanca (acabados) | 3.5 Aparatos sanitarios, griferías y accesorios | 25 | 2 | Barranquilla 18, — 7 | **ninguno** | Resolución 0194 de 2025 (aparatos ahorradores) | — |
| 3. Obra blanca (acabados) | 3.6 Aseo y entrega | 1 | 0 | Barranquilla 1 | **ninguno** | — | — |
| 4. Fase final: urbanismo y obras exteriores | 4.1 Urbanismo y espacio público | 138 | 2 | Puerto Colombia 86, Barranquilla 52 | motor-vias | NTC 4143 y Ley 361 de 1997 (accesibilidad); IDU ET-IC-01 (espacio público, Bogotá) | — |
| 4. Fase final: urbanismo y obras exteriores | 4.2 Vías internas y parqueaderos | 160 | 1 | Barranquilla 126, Puerto Colombia 34 | motor-vias, motor-topovia | — | #185 |
| 4. Fase final: urbanismo y obras exteriores | 4.3 Redes externas y drenaje | 73 | 2 | Barranquilla 47, Puerto Colombia 22, Atlántico 4 | motor-aquai, motor-redes | — | #138, #139 |
| 4. Fase final: urbanismo y obras exteriores | 4.4 Cerramiento definitivo, portería y alumbrado exterior | 21 | 0 | Barranquilla 21 | **ninguno** | RETILAP (alumbrado exterior) | — |

Palabras más frecuentes en las actividades sin clasificar (para ampliar las claves):

suministro (73), instalación (62), concreto (57), puntos (36), cobre (35), geotextil (29), equipo (27), galvanizado (25), tejido (25), aplicación (23), acero (22), resistencia (21), diámetro (20), punto (18), generales (14), cemento (14), mortero (14), reducida (14), selareneg (13), agregado (13), sobre (13), tapón (13), camisa (13), malla (12), adaptador (12), esquema (12), empalme (12), construcción (12), sodallated (11), fachada (11), lamina (11), salida (11), válvula (11), inspección (11), aditivos (11), mecánico (11), grava (10), limpieza (10), material (10), entre (10)
