# Línea base costo + CO₂ — zapata prismática vs troncopiramidal (2026-11-08)

Reproducir: `python scripts/experimentos/linea_base_costo_co2_zapata.py` (datos en `linea_base_costo_co2_zapata_2026-11.json`).
Geometrías: las del experimento de desperdicio (optimizadas por volumen + acero, 30 casos). **No** están optimizadas por costo ni CO₂: es la referencia del diseño inverso.

| Resultado (mediana; rango) | Valor |
|---|---|
| Ahorro de costo directo | 19 % (0–33 %), casi igual con encofrado a 20.000 o 27.000 COP/m² |
| Ahorro de CO₂ (A1–A3) | 20 % (0–34 %), igual con cemento 0,892 o 1,010 |
| Por carga (P_serv 300/600/1000/1500/2500 kN), costo | 0 / 14 / 19 / 26 / 31 % |

Concreto estimado: 321–362 kgCO₂e/m³ (21 MPa) y 383–433 (28 MPa); el promedio de cartera de Argos publicado (353–364) cae en ese rango.

## Límites (leer antes de citar)
- Precios APU Barranquilla: concreto zapata 21 MPa 688.796 COP/m³; acero fy 420 4.151 COP/kg; encofrado solo material (insumo "enconfrado en madera"), sin mano de obra. El precio de 28 MPa es un **sustituto** (concreto de vigas 28 MPa, 822.510): no hay precio de zapata a 28.
- Dosificación (350/420 kg cemento por m³) es **supuesto** sin fuente; el CO₂ del concreto depende casi todo de ese número.
- Factores: cemento EPD 857 Argos (primaria) y Pardo 2022 (secundaria); acero 1,322 kgCO₂/kg es secundario y 0,850 de Paz del Río no verificado. Sin CO₂ de encofrado, transporte ni bombeo.
- El ahorro de costo y CO₂ casi coincide con el de volumen porque el concreto domina ambos; el acero aumenta (−10 % de ahorro) y no cambia el orden.
