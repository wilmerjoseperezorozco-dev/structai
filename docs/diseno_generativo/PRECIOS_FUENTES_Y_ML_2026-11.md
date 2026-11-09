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

| Precio de perforación y cabeza | Casos con solución previa donde gana una tipología nueva | Gana anclaje | Gana contrafuerte |
|---|---|---|---|
| Supuesto original (×1) | 73,7 % | 73,2 % | 0,4 % |
| ×3 (≈ INVIAS real) | 23,2 % | 16,7 % | 6,6 % |
| ×6 | 10,1 % | 0 % | 10,1 % |

La recuperación mecánica de casos sin solución (50 %) no depende del precio. El ranking económico sí: con el precio real el anclaje deja de dominar y pasa a ser una solución de rescate donde el voladizo no cumple. Conclusión de diseño: los precios del anclaje deben entrar como distribución, no como constante.

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

- Verificar la inversión de columnas en `invias_actividad_insumos`.
- Integrar ICCV/ICOCED del DANE.
- Reemplazar los defaults de `Economia` por distribuciones y repetir `region_sin_solucion.py` con muestreo de precios.
- Acero estructural fabricado y montado para cerchas y nudos (sin fuente INVIAS).
