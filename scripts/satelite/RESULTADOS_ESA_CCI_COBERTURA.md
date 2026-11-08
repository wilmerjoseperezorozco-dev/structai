# Cobertura de la humedad del suelo ESA CCI v09.2 (COMBINED) sobre Colombia, año 2022 (2026-11-08)

Fuente: CEDA, `COMBINED/v09.2`, diario, 0,25° (~25 km). Descargador: `bajar_esa_cci_humedad.py`. Este es un chequeo de **cobertura**, no un análisis de hipótesis. Solo 2022; los otros años se descargaron después y no se han revisado.

## Verificación de la georreferenciación
Barranquilla: 99 % de los días con dato, humedad media 0,31 m³/m³. Cali: 96 %, 0,33. Son valores plausibles. No tengo una referencia externa para confirmar la cuadrícula; la comprobación es de plausibilidad.

## Dónde hay dato (por celda de 0,25°, 2022)
1.003 de 4.464 celdas del recuadro (22 %) tienen algún dato; 925 lo tienen ≥ 90 % de los días. El recuadro incluye mar y países vecinos. **Sin dato en todo el año:** Bogotá, Quibdó, Leticia, Riohacha y Villavicencio (celda de su punto). El mapa de cobertura muestra dato en el Caribe interior, los Llanos y parte de los valles; **vacío** en los Andes altos, el Chocó y la Amazonía.

La causa no está verificada. La explicación habitual es que el producto enmascara selva densa, relieve complejo y agua, pero no lo confirmé en la documentación del producto.

## Cobertura por municipio (celda del punto representativo del polígono; 995 municipios del panel)
| Región | Municipios | % con dato ≥ 50 % de los días | Eventos de mov. en masa UNGRD 2019-2024 |
|---|---:|---:|---:|
| Caribe | 192 | **80 %** | 120 |
| Orinoquía | 29 | 41 % | 75 |
| Andina | 627 | **17 %** | 5.531 |
| Pacífica | 147 | **15 %** | 1.365 |
| **Total** | 995 | 30 % | 7.091 |

Solo el **17 %** de los eventos de movimiento en masa (1.216 de 7.091) cae en municipios con dato ≥ 50 % de los días; con ≥ 90 %, el 6 %.

## Qué implica
- **La hipótesis #3 (humedad antecedente antes de movimientos en masa) no es viable con este producto**: los eventos están justo donde no hay dato (Andes y Pacífico).
- **Sí es utilizable en el Caribe** (80 % de los municipios): por ejemplo para inundaciones y para la hipótesis fluvial, donde está la mayor parte de la cobertura.
- Limitaciones de este chequeo: un solo punto por municipio (un municipio grande abarca varias celdas, y un punto sin dato no implica que no haya dato en otra parte de su territorio); solo el año 2022; no comparé con humedad medida en campo.
