# Precios reales para el diseño generativo: fuentes, método y coherencia del aprendizaje automático

Fecha: 2026-11-09. Alcance: extender el flujo (muestreo Sobol → optimizador → sustituto LightGBM → guardia determinista → Pareto costo/CO₂) de los muros a pilotes, tablestacas, anclajes, cerchas, escaleras y nudos.

## 1. Fuentes evaluadas

| Fuente | Cobertura | Fortaleza | Límite |
|---|---|---|---|
| INVIAS APU 2026-1 (Supabase, 5 tablas) | 526 actividades, 686 insumos, 140 provincias, una sola fecha | Estructurada, con receta (rendimientos) y costo directo por provincia | Orientada a obra vial; sin AIU; descripciones de tipo/diámetro incompletas |
| Contratos locales Barranquilla/Puerto Colombia | Acero, concreto 21/28 MPa | Precio de mercado real | Heterogéneo en especificación; la fecha de captura no es la del precio |
| Catálogo IAD nacional (`apu_precios_nacional_detalle`) | Amplio | Cobertura | Entradas con especificación dudosa (concreto ≈220 mil COP/m³) |
| DANE ICCV / ICOCED | Índices mensuales | Para indexar entre fechas | Pendiente de descargar e integrar |

Catálogo reproducible: `scripts/precios/descargar_invias.py` → `scripts/precios/construir_catalogo.py` → `data/precios_elementos/catalogo_precios_2026-1.{csv,json}` (44 ítems con valor en Atlántico Norte, mediana nacional, cuartiles y n).

## 2. Hallazgos medidos

- La matriz de costos INVIAS es casi aditiva en logaritmo (ítem + provincia): R² = 0,9966; error mediano de validación cruzada 4,3 %, p90 19,5 %.
- El efecto provincia es pequeño (≈ ±5 %, salvo islas). La incertidumbre dominante es de especificación, fuente y fecha, no de localización.
- Acero de refuerzo: INVIAS 6.826 COP/kg instalado (insumo 4.585) frente a 4.979–7.388 en contratos locales: consistentes.
- Concreto 28 MPa: INVIAS insumo 657 mil COP/m³; contratos locales 772–947 mil colocado: consistentes.
- **Anclaje (623,1): 549.776 COP por metro perforado**, unas 3 veces el supuesto anterior. Torón: 10.790 COP/kg. Preesfuerzo instalado: 11.607 COP/kg.
- Posible inversión de columnas `cantidad_o_rendimiento` y `valor_unitario_linea` en algunas filas de `invias_actividad_insumos` (p. ej. torón: 10.790 en cantidad, 59.670 en valor; la cantidad real es 5,53 kg/m). Sin corregir; hay que verificar en la ingesta antes de usar rendimientos.
- 623,1 está descrito para roca. En suelo el rendimiento de perforación y la longitud fija cambian: el precio real es una cota de referencia, no un valor para suelo blando.

## 3. Efecto en la tipología ganadora del muro (512 casos, mismo conjunto)

| Precio de perforación y cabeza | Casos con solución previa donde gana una tipología nueva | Gana anclaje | Gana contrafuerte | Ahorro mediano si gana |
|---|---|---|---|---|
| Supuesto original (180 mil COP/m, cabeza 450 mil) | 73,7 % | 73,2 % | 0,4 % | 18,6 % |
| ×3 sobre el supuesto (sensibilidad) | 23,2 % | 16,7 % | 6,6 % | 11,3 % |
| ×6 sobre el supuesto (sensibilidad) | 10,1 % | 0 % | 10,1 % | 7,5 % |
| **INVIAS 2026-1 (490.100 COP/m sin torón, cabezal 114.571, torón 10.790 COP/kg) con un escenario lognormal de precios por caso** | **36,0 %** | **29,4 %** | **6,6 %** | **15,3 %** |

Con precios reales, el 50 % de los casos sin solución sigue recuperándose con anclaje (es mecánico: no depende del precio) y la recuperación es mayor en muros bajos (66 % a 1,5–3 m; 74 % a 3–5 m; 49 % a 5–6,5 m; 24 % a 6,5–8 m). La fracción sin solución tras las dos tipologías nuevas se mantiene en 27,7 %. Conclusión de diseño: el anclaje es una solución de rescate competitiva, no dominante, y su ranking económico depende de la distribución de precios, que ahora entra por `precios_distribucion.muestrear`. Archivo: `data/surrogate_muro/region_sin_solucion_invias_muestreo.json`.

La corrida usa un escenario por caso (marginaliza la incertidumbre sobre el conjunto); no estima la probabilidad de ganar de un caso individual, que requeriría varios escenarios por caso.

## 3.1 Indices del DANE

El ICCV se descontinuó en dic-2021 y lo reemplaza el ICOCED (base dic-2021 = 100). `scripts/precios/indices_dane.py` lee el anexo mensual (hoja 7.2) y produce `data/precios_elementos/indices_icoced.csv`: 100.719 filas, 19 dominios geográficos, 93 grupos de insumos, 2022-01 a 2026-09. Para Barranquilla AM la variación anual a sep-2026 es +9,1 % en acero corrugado y −0,9 % en concreto común. `factor(df, dominio, insumo, desde, hasta)` lleva un precio de una fecha a otra.

## 3.2 Incertidumbres calibradas

`scripts/precios/calibrar_distribuciones.py` compone el sigma de cada familia (localización entre 140 provincias + fuente entre contratos locales + deriva temporal del ICOCED + especificación declarada): acero 0,120; concreto 0,090; perforación de anclaje 0,283 (de los cuales 0,25 es un supuesto de especificación, porque la receta INVIAS es en roca).

## 3.3 Defecto de ingesta INVIAS (issue #112, corregido 2026-11-09)

En el Excel FR-APU-1 las columnas cambian según la sección: en materiales idx10 = cantidad e idx11 = precio unitario; en equipo y mano de obra idx11 = rendimiento. El cargador leía idx11 para todo, de modo que en las 185.780 filas de material `cantidad_o_rendimiento` guardaba el precio (100 % de las filas, comprobado contra `invias_insumos_precios`). Ejemplo en 623,1: torón con 10.790 donde debía haber 5,53 kg/m.

Corrección: el cargador (`scripts/ingesta/invias_apu/cargar_invias_apu.py`) lee la columna correcta por sección y guarda `precio_unitario`; la migración `20261109120000_corregir_invias_cantidad_material.sql` conserva el valor leído en `precio_unitario` y reconstruye la cantidad como `valor_unitario_linea / precio_unitario` (4 decimales). Contra el Excel de Atlántico Norte (1.328 filas de material) el error relativo mediano es 0 y 14 filas con cantidades menores de 0,01 difieren más de 0,1 % por el redondeo del valor de línea; tras la migración quedan 140 filas (de 185.780) con `cantidad × precio` a más de 2 % del valor de línea, atribuibles al mismo redondeo. Equipo, transporte y mano de obra no se tocaron. El costo directo por actividad nunca estuvo afectado.

## 4. Método propuesto y coherencia del aprendizaje automático

1. **El modelo aprendido sigue siendo un sustituto del optimizador**, nunca un predictor de precios. Los precios son entradas con incertidumbre, no etiquetas.
2. **Muestreo de precios empírico**: por ítem, distribución lognormal con mediana del catálogo y dispersión tomada de (a) el rango intercuartil entre provincias, (b) la discrepancia INVIAS–contratos locales. Cada caso Sobol incluye un escalar de precio por familia (acero, concreto, perforación, hincado).
3. **Imputación de ítems faltantes**: modelo log-aditivo ítem + provincia (jerárquico), ya validado con R² 0,9966; no regresión de caja negra.
4. **Indexación por fecha**: llevar cada observación a la fecha base con ICCV/ICOCED (pendiente).
5. **Guardia intacta**: toda predicción del sustituto pasa por el verificador determinista con intervalo conforme; el sustituto no puede aprobar un diseño inseguro.
6. **Reentrenar con características de precio** cuando se sumen elementos, para que el sustituto devuelva el diseño óptimo condicionado al escenario de precios.

## 5. Plan por elemento

| Elemento | Ítems de precio disponibles | Estado |
|---|---|---|
| Pilotes | 620,1 / 621,1 (precio por m), base acampanada, descabece, pruebas | Precios listos; falta motor de capacidad (NSR-10 H) |
| Tablestacas | 622,1–622,4 por m² | Precios listos |
| Anclajes | 623,1; torón; cabezal | Integrado en muros; actualizar defaults con la distribución |
| Cerchas y nudos | Acero estructural, platinas, soldadura, pintura | Falta precio de acero estructural fabricado (INVIAS 5xx/6xx no lo cubre); buscar en contratos |
| Escaleras | Concreto, acero, formaleta | Precios listos |
| Gaviones | 681,1–681,5 | Precios listos |

## 6. Pendiente

- Integrar el factor ICOCED y la lectura del catálogo en `Economia`.
- Sigmas para pilotes, tablestacas, gaviones y preesfuerzo.
- Acero estructural fabricado y montado para cerchas y nudos (sin fuente INVIAS).
- Varios escenarios de precio por caso para estimar la probabilidad de que una tipología gane.
- Matriz de elementos y laboratorio digital: ver `MATRIZ_ESTANDARIZACION_MOTORES_2026-11.md`.
