# Presupuesto por etapas en StructAI: qué podemos ofrecer y qué falta

Fecha: 2026-11-12. Datos: [`COBERTURA_PRECIOS_ETAPAS.md`](COBERTURA_PRECIOS_ETAPAS.md), generado por
`scripts/presupuesto/cobertura_etapas.py` (solo lectura). Taxonomía:
[`packages/motor-apu/data/taxonomia_etapas_presupuesto.json`](../../packages/motor-apu/data/taxonomia_etapas_presupuesto.json).

## 1. La estructura de un presupuesto en Colombia

El presupuesto se ordena en cuatro etapas constructivas, más los costos transversales:

| Etapa | Capítulos | Equivalente ICOCED (DANE) |
|---|---|---|
| 0. Transversales | AIU; gastos generales, PMA, SST, PMT y gestión social; supervisión técnica y trámites; equipos | — |
| 1. Fase inicial y obra negra | preliminares; excavación y movimiento de tierras; cimentación; estructura en concreto; estructura metálica; mampostería; cubierta e impermeabilización | preliminares; excavación y cimentación; estructura y cubierta; mampostería y pañetes |
| 2. Obra gris | hidrosanitarias; contra incendio; gas; eléctricas; comunicaciones; equipos especiales | acabados tipo 1 |
| 3. Obra blanca | pañetes, estucos y pinturas; pisos y enchapes; carpintería y ventanería; cielorrasos; aparatos sanitarios; aseo y entrega | mampostería y pañetes; acabados tipo 2 y 3 |
| 4. Fase final | urbanismo y espacio público; vías internas y parqueaderos; redes externas y drenaje; cerramiento y alumbrado exterior | — |

El ICOCED del DANE distingue siete capítulos constructivos y estos sistemas constructivos: aporticado, mampostería confinada, mampostería estructural, industrializado y metálico. El índice se publica cada mes por capítulo y destino. Es la referencia oficial para alinear la taxonomía y para **indexar precios viejos por capítulo** en vez de usar el IPC (#113).

Lo que dicen las fuentes y hay que llevar al producto:

- **APU** (IDU GU-DP-017 v3, 2024): cuatro grupos de costo (materiales, mano de obra, transporte, equipo y herramienta). Cada insumo nuevo necesita al menos tres cotizaciones comparables, con fecha, unidad, IVA, transporte y descuentos. PMA, SST, PGS y PMT se pagan a valor global. Hay un fondo aparte para mayores cantidades e ítems no previstos.
- **AIU** (misma guía):
  - **A:** personal profesional, técnico y administrativo; oficina y campamento con servicios; vehículos; papelería; impuestos; pólizas.
  - **I:** la guía lista 14 imprevistos típicos (clima, ausencias de personal, proveedores exclusivos, fallas geotécnicas no previsibles, orden público, permisos, vecinos, SST...). El mínimo usual está entre 3 % y 5 % (Betancur, citado por el IDU). Los imprevistos **no** son mayores cantidades ni ítems no previstos.
  - **U:** la ganancia del contratista.
- **IVA** (Decreto 1625 de 2016, art. 1.3.1.7.9; Oficio DIAN 4761 de 2019): en construcción de inmueble se liquida el 19 % **sobre la utilidad** (o sobre los honorarios). La base AIU del art. 462-1 del E.T. es para aseo y vigilancia, no para construcción.
- **Dónde se equivocan los presupuestos** (U. Distrital, 2024, vivienda multifamiliar industrializada):
  - En el caso de estudio, estructura y cimentación pesan el 44 % del costo; luego vienen eléctricas y comunicaciones (11 %), hidrosanitarias y gas (8 %), mampostería (8 %) y obras exteriores (7 %).
  - Las mayores diferencias de cantidades están en movimiento de tierras y en cimentación y estructura.
  - Los rendimientos presupuestados suelen ser optimistas.
  - Causas típicas de desviación: omisión de actividades, errores de rendimiento, diseños incompletos y mala actualización anual de precios.

## 2. Lo que tiene StructAI, por capítulo

Precios (`apu_precios_referencia`): 4.566 filas. De ellas, 1.754 son insumos sueltos de ferretería del catálogo IAD (no son actividades), así que quedan **2.812 actividades de obra**. El 66 % se clasifica con la línea base de palabras clave y 374 son ambiguas.

| Capítulo | Actividades | Con desglose | Motor | Normas en el corpus | Lo que falta |
|---|---|---|---|---|---|
| Preliminares | 59 | 2 | topovía (replanteo) | — | RCD (Res. 1257 de 2021) |
| Excavación y movimiento de tierras | 97 | 4 | geotecnia, GeoPot, licuación | NSR-10 H, ensayos INVIAS | RCD |
| Cimentación | 32 | 3 | geotecnia, concreto, cantidades APU | NSR-10 H, C, A-4/SGC | motores de #149 y #136 |
| Estructura en concreto | 79 | 14 | concreto, estructural, análisis | NSR-10 A, C | #122, #142 |
| Estructura metálica | 6 | 0 | acero en frío (F.4) | NSR-10 F, AISC 360 | precios; #141, #121 |
| Mampostería | 66 | 6 | vulnerabilidad de vivienda | NSR-10 D, E, A.9, AIS | #141 |
| Cubierta e impermeabilización | 102 | 20 | **ninguno** | NSR-10 B, G | #121, #146; B.6 (viento) sin cargar |
| Hidrosanitarias | 560 | 32 | AquAI y redes (**solo redes externas**) | NTC 1500, RAS | motor interior; Res. 0194 de 2025 |
| Contra incendio | 11 | 2 | **ninguno** | NSR-10 J y K | motor; NTC 1669 / NFPA |
| Gas | 2 | 0 | **ninguno** | — | Res. 90902 de 2013, NTC 2505 |
| Eléctricas | 71 | 6 | **ninguno** | — | RETIE, NTC 2050, RETILAP; #143 |
| Comunicaciones | 1 | 1 | **ninguno** | — | RITEL (Res. CRC 7930 de 2025) |
| Equipos especiales | 0 | 0 | **ninguno** | — | NTC 5926 |
| Pañetes, estucos, pinturas | 65 | 6 | **ninguno** | — | APU y rendimientos (#19) |
| Pisos y enchapes | 103 | 14 | **ninguno** | — | APU y rendimientos |
| Carpintería y ventanería | 112 | 20 | **ninguno** | NSR-10 K (vidrios), B.4 (barandas) | APU |
| Cielorrasos | 37 | 6 | **ninguno** | NSR-10 A.9 | — |
| Aparatos sanitarios | 25 | 2 | **ninguno** | — | Res. 0194 de 2025 |
| Urbanismo y espacio público | 138 | 2 | vías | POT | accesibilidad (NTC 4143, Ley 361), IDU ET-IC-01 |
| Vías internas | 160 | 1 | vías, topovía | manuales INVIAS | — |
| Redes externas y drenaje | 73 | 2 | AquAI, redes | RAS | #138, #139 |
| Cerramiento y alumbrado exterior | 21 | 0 | **ninguno** | — | RETILAP |
| Transversales (AIU, SST, PMA, equipos) | 25 | 0 | motor-apu (AIU por defecto) | Dec. 1072 (SST), Ley 80/1150 | IVA (Dec. 1625), Res. 0312 de 2019, Res. 4272 de 2021 |

## 3. Qué podemos ofrecer

### A. Ya, con lo que hay

1. **Consulta de precios por actividad** con fuente, región y fecha. Son 2.812 actividades, más 114.616 precios de 102 proveedores.
2. **APU con rango de confianza** (Monte Carlo, IC90) y AIU para las 29 actividades del catálogo del motor, además de las cantidades de los elementos de concreto.
3. **Presupuesto por lote** en `.xlsx` y **detección de precios atípicos**.
4. **Cada capítulo de obra negra con su norma:** NSR-10 A a K, amenaza sísmica del municipio, NTC 1500 para hidrosanitarias, RAS para redes y manuales INVIAS para vías.
5. **Contratación y SST:** Ley 80, 1150 y 1474; Decreto 1072 (SG-SST); manual de interventoría.

### B. Con trabajo corto (los datos están, falta código)

1. **Clasificador de actividades por etapa y capítulo.** Toma la taxonomía de este documento y la combina con MiniLM, umbral de confianza y aprendizaje activo, el mismo método del enrutador de #169. Es la base de todo lo demás.
2. **Revisor de presupuestos:**
   - estructura el `.xlsx` de un contratista en las etapas;
   - marca **faltantes por dependencia**: pintura sin pañete, pañete sin mampostería, enchape sin alistado, ventanería sin dinteles ni alfajías, cubierta sin canales ni bajantes, cimentación sin excavación ni retiro de sobrantes, estructura sin acero ni formaleta, instalaciones sin regatas ni resanes;
   - marca **precios atípicos** frente a la referencia;
   - revisa el **AIU** por componente: imprevistos por debajo del 3 %, administración sin pólizas ni personal, utilidad sin IVA;
   - revisa el **IVA del 19 % sobre la utilidad**;
   - compara el **peso de cada capítulo** con la referencia del tipo de proyecto, para alertar cuando la estructura pese 10 % en un multifamiliar.
3. **Plantillas de presupuesto por tipo de proyecto:** casa de 1 o 2 pisos en mampostería confinada, VIS, multifamiliar industrializado, red de acueducto y vía urbana, con los capítulos e ítems de la taxonomía.
4. **Indexación por capítulo con el ICOCED** para los contratos de 2016 a 2019, que hoy se ajustan por IPC (#113).
5. **Curva S y flujo de caja por etapa**, combinando `dag-proyecto` y Gerencia.

### C. Requiere datos o normas nuevas (los huecos)

| Hueco | Qué habilita | Nota |
|---|---|---|
| RETIE, RETILAP, NTC 2050 | motor eléctrico (#143) y el 11 % del presupuesto multifamiliar | RETIE y RETILAP son públicos; **NTC 2050 es de ICONTEC (derechos de autor)**: solo referencia y metadatos, salvo licencia |
| RITEL (Res. CRC 7930 de 2025) | comunicaciones en propiedad horizontal | público |
| Gas (Res. 90902 de 2013; NTC 2505) | instalaciones de gas | la resolución es pública; la NTC es de ICONTEC |
| Motor hidrosanitario **interior** (NTC 1500, que ya está) | el capítulo con más precios (560) no tiene motor de diseño interior | solo código |
| Motor contra incendio (NSR-10 J, que ya está) | redes y gabinetes; NFPA y NTC 1669 tienen derechos | solo código y referencias |
| APU y rendimientos de obra blanca | presupuesto de acabados con desglose | el catálogo tiene 0 APU de acabados; bloqueado por falta de fuente de recetas (#19) |
| Construcción sostenible (Res. 0194 de 2025) | cumplimiento de ahorro de agua y energía en edificaciones nuevas | pública, obligatoria |
| RCD (Res. 1257 de 2021), SST (Res. 0312 de 2019), alturas (Res. 4272 de 2021), accesibilidad (Ley 361 de 1997) | costos transversales que el revisor debe exigir | públicas; NTC 4143 es de ICONTEC |
| Precios de edificación fuera del Atlántico | presupuestos para el resto del país | hoy todo es Barranquilla, Puerto Colombia y Atlántico. Fuentes: visor del IDU (Bogotá), SECOP II (ya cruzado con RUES), listas de gobernaciones (no publicadas en línea; pedirlas por derecho de petición) |
| Desglose de materiales y mano de obra | ajuste por región y por salario | solo 255 de 2.812 actividades lo tienen |
| Calidad de datos | — | 22 filas de Construdata con el encabezado "DETALLADOS GENERALES" pegado e invertido (`SODALLATED SELARENEG`); una es solo el encabezado |

## 4. Orden recomendado

1. Clasificador de actividades (B1): sin él no hay revisor ni plantillas.
2. Revisor de presupuestos (B2): es lo de más valor visible y usa lo que ya existe.
3. Ingesta de reglamentos públicos de obra gris (RETIE, RETILAP, RITEL, gas, 0194) y motor hidrosanitario interior: cubren el 20 % del costo que hoy no tiene motor.
4. Obra blanca: conseguir una fuente de recetas y rendimientos (#19). Los presupuestos y contratos reales del usuario son la mejor.
5. Cobertura regional de precios.

## 5. Issues

| Issue | Qué |
|---|---|
| #196 | clasificador de actividades por etapa y capítulo, revisor de presupuestos (faltantes, AIU, IVA, atípicos, peso por capítulo) y plantillas por tipo de proyecto |
| #197 | ingesta de reglamentos que faltan: RETIE, RETILAP, RITEL, gas, 0194 de 2025, RCD, SST, accesibilidad, IVA, Ley 1796, IDU ET-IC-01 |
| #198 | motores hidrosanitario interior (NTC 1500), gas (Res. 90902) y contra incendio (NSR-10 J) |
| #199 | motor de cantidades y APU de obra blanca, con recetas con fuente (destraba #19) |
| #200 | precios: cobertura regional, desglose MO/materiales, 22 filas con texto invertido |
| #143, #113, #121 | existentes, actualizados con estos datos (eléctrico y RITEL, ICOCED por capítulo, cubiertas) |

Ninguno de estos pasos toca producción hasta que el usuario lo apruebe. La taxonomía y la cobertura son archivos del repositorio; la carga a la base queda para cuando se decida.
