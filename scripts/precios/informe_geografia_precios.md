# Geografia de los precios de construccion (INVIAS 2026-1)

Precios de REFERENCIA (analisis de precios unitarios regionalizados de INVIAS), periodo 2026-1; no son cotizaciones de mercado. Unidad de analisis: provincia. Ver el docstring del script para las preguntas y limites.

## Datos
- Provincias: 140; insumos con precio: 663; filas de precio: 92820 (periodo ['2026-1']).
- Precios nulos o no positivos: 240.

## P1. Prima por region natural (indice provincial; 1,00 = mediana nacional del mismo insumo)
| region (n provincias) | cementantes_bituminosos (49 insumos) | acero (46 insumos) | agregados (70 insumos) |
|---|---|---|---|
| Amazonía (4) | 0.97 [0.88, 0.98] | 0.93 [0.91, 0.94] | 1.03 [0.97, 1.03] |
| Andina (73) | 0.98 [0.96, 1.01] | 0.97 [0.97, 0.98] | 1.00 [0.99, 1.01] |
| Caribe (34) | 0.99 [0.98, 1.00] | 0.96 [0.95, 0.97] | 0.99 [0.97, 1.00] |
| Orinoquía (9) | 0.92 [0.90, 0.94] | 0.94 [0.90, 0.96] | 0.92 [0.85, 0.96] |
| Pacífico (20) | 0.99 [0.95, 1.02] | 0.98 [0.94, 1.02] | 1.00 [0.99, 1.05] |

Mediana de los indices provinciales de la region con IC95 % (remuestreo de provincias). >1 = mas caro que la mediana nacional.

## P2. Inestabilidad entre provincias (coeficiente de variacion por insumo; insumos con precio en >= 120 provincias)
| categoria | insumos | CV mediano | CV p90 |
|---|---|---|---|
| AGREGADOS | 70 | 0.54 | 0.71 |
| MADERA | 10 | 0.26 | 0.35 |
| (transporte) | 41 | 0.25 | 0.48 |
| (equipo) | 146 | 0.20 | 0.42 |
| CEMENTANTES Y BITUMINOSOS | 49 | 0.19 | 0.29 |
| ARBOLES, VEGETACION, Y FERTILIZANTES. | 24 | 0.17 | 0.31 |
| ACERO, ALAMBRES, SOLDADURA Y MALLAS METALICA | 46 | 0.16 | 0.33 |
| CAUCHOS Y ELASTOMEROS | 7 | 0.13 | 0.24 |
| SENALIZACION Y SEGURIDAD VIAL | 67 | 0.10 | 0.30 |
| ANCLAJES | 20 | 0.10 | 0.33 |
| MORTEROS, CONCRETO ESTRUCTURAL Y PAVIMENTO H | 18 | 0.09 | 0.19 |
| ADITIVOS Y ADHESIVOS | 47 | 0.08 | 0.30 |

## Participacion del transporte en el costo directo (media sobre ~526 actividades)
| region | provincias | transporte / costo directo (mediana, IC95 %) |
|---|---|---|
| Amazonía | 4 | 1.0 % [1.0, 1.3] |
| Andina | 73 | 1.0 % [1.0, 1.1] |
| Caribe | 34 | 0.9 % [0.8, 1.0] |
| Orinoquía | 9 | 1.0 % [0.7, 1.5] |
| Pacífico | 20 | 1.0 % [0.9, 1.1] |

## P3. Consistencia interna: ¿la prima de materiales pesados se asocia con el peso del transporte?
rho de Spearman (n=140 provincias) = **-0.05**, IC95 % por regiones [-0.22, 0.25]. El IC incluye 0: el indice de prima y el peso del transporte no se asocian de forma robusta.

## P4 (exploratorio). Prima vs distancia (ubicacion = capital del departamento; aproximacion gruesa)
- distancia al puerto mas cercano (Cartagena, Barranquilla, Santa Marta, Buenaventura): rho = 0.05, IC95 % por regiones [-0.61, 0.33] (n=140)
- distancia a Bogota: rho = -0.03, IC95 % por regiones [-0.34, 0.29] (n=140)

Las distancias usan la capital departamental, no la provincia; los puertos elegidos son una decision del analista; una correlacion no establece que la distancia cause la prima (hay confusion con relieve, vias y volumen).

## Puntos fragiles (descriptivo)
| provincia | departamento | region | prima materiales pesados | transporte / costo directo |
|---|---|---|---|---|
| ARCHIPIELAGO DE SAN ANDRES | SAN ANDRES | Caribe | 1.84 | 1.8 % |
| DARIEN | CHOCO | Pacífico | 1.06 | 1.2 % |
| VALLE DE ABURRA | ANTIOQUIA | Andina | 1.06 | 0.8 % |
| GUALIVA | CUNDINAMARCA | Andina | 1.05 | 1.0 % |
| VELEZ | SANTANDER | Andina | 1.04 | 0.9 % |
| ORIENTE | CAUCA | Pacífico | 1.03 | 0.8 % |
| GUANENTA | SANTANDER | Andina | 1.03 | 0.9 % |
| PACIFICO SUR | CHOCO | Pacífico | 1.03 | 1.3 % |

Limites: precios de referencia, no de mercado; un solo periodo (2026-1), por eso no hay volatilidad temporal; provincias ≠ mercados; el indice depende de los insumos que tienen precio en >= 120 provincias.