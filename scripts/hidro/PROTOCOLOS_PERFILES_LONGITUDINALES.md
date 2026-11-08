# Protocolos preregistrados: usos del perfil longitudinal de cauce (F1–F4)

Estado: **preregistrados el 2026-11-08, sin ejecutar.** Ninguna cifra de este documento es un resultado; todo lo que sigue define qué se va a medir y con qué criterio se juzgará antes de calcular. Cualquier cambio posterior se publica como enmienda fechada, antes de calcular.

## 0. Insumos comunes y su límite real

- **Perfiles:** los 256–257 perfiles longitudinales de E1 (`scripts/hidro/pendiente_cauce.csv`, DEM Copernicus GLO-30 agregado a ~90 m, ruta de flujo más larga hasta cada estación de aforo).
- **Limitación estructural, conocida de E1:** en el 44 % de los tramos la pendiente cae al piso de 0,0005 m/m por la resolución de 90 m. Los perfiles son solo la ruta más larga hasta cada estación, **no** la red completa de drenaje; los caudales existen solo en las estaciones.
- **Regla común:** ningún análisis usa tramos cuya pendiente esté en el piso; se reporta qué fracción de tramos queda fuera. Si menos del 50 % de los perfiles conserva tramos utilizables, el resultado se declara no concluyente y no se interpreta.
- **No se usan datos sintéticos para decidir.** Toda validación exige datos observados verificables; si no existen o no se pueden obtener, el frente queda en «solo descriptivo».
- **Descargas:** cualquier archivo nuevo (DEM de 30 m, inventarios) se descarga solo con permiso explícito del usuario, indicando nombre, fuente y tamaño.

---

## F1. Potencial hidroeléctrico a filo de agua (pequeñas centrales)

**Pregunta.** ¿En qué tramos de los perfiles coinciden alta caída concentrada y caudal firme suficiente para una pequeña central sin embalse?

**Fundamento.** Las pequeñas centrales a filo de agua no requieren embalse ni navegabilidad; buscan tramos de alta caída en cuencas andinas. Potencia: P = ρ·g·Q·H·η.

**Diseño.**
1. Segmentar cada perfil en tramos de longitud fija L ∈ {1, 2, 5} km (tres tamaños, se reportan los tres).
2. Caída bruta del tramo H = z_inicio − z_fin; pendiente por tramo S = H/L, solo con tramos sobre el piso.
3. Caudales de cálculo en la estación: Q_medio (media de la serie histórica) y Q_mín (percentil 10 de la curva de duración de caudales medios diarios), de `scripts/hidro/_cache/caudal_historico.pkl`. Para tramos aguas arriba de la estación: Q(x) = Q_estación · (A(x)/A_estación)^k, con **k = 1 como caso base** y k ∈ {0,8; 1,0} como sensibilidad; el supuesto de proporcionalidad al área se declara como principal fuente de incertidumbre.
4. Potencia teórica bruta P_bruta = 9,81·Q·H (kW, Q en m³/s, H en m, η = 1) y potencia con η = 0,7; la capacidad instalada realista usa Q de diseño ≈ percentil 30–50 de la curva de duración, reportado, nunca Q_medio solo.
5. Clasificación referencial por potencia (pico-, micro- y pequeña central) usando los umbrales vigentes de la norma colombiana, **que se verifican en texto antes de usarse** (ver `NORMAS_CANDIDATAS_INGESTA.md`); hasta verificar, solo se reporta potencia en kW.

**Medidas.** Número y porcentaje de tramos utilizables; distribución de P (mediana, p90, máximo) por región natural; los 10 tramos de mayor potencia con su caída, Q_mín, Q_medio y fracción de tramo utilizable.

**Criterios.**
- *Descriptivo:* se reporta la distribución con IC bootstrap por bloques de 1° (como en E1).
- *Robustez:* un tramo solo se declara «candidato» si mantiene P_bruta ≥ 100 kW tanto con Q_mín como con k = 0,8, y su pendiente no está en el piso.
- *Validación externa:* comparar los candidatos con proyectos o inventarios públicos de pequeñas centrales; **no existe aún** una fuente verificada en este proyecto. Mientras no se obtenga, los resultados se presentan como cribado de prefactibilidad, no como potencial.

**Qué no se afirma.** Que un tramo sea aprovechable: faltan caudal ecológico, derechos de agua, geología, accesos, red eléctrica y licenciamiento.

---

## F2. Susceptibilidad a avenidas torrenciales (quiebre de pendiente en el abanico)

**Pregunta.** ¿El contraste entre la pendiente de cabecera y el cambio de pendiente aguas abajo identifica los sitios donde el río pierde capacidad de transporte y deposita sedimentos?

**Diseño.**
1. Por perfil, pendiente de cabecera S_c = pendiente del primer tercio de la longitud, sobre el piso; pendiente de salida a abanico S_a = pendiente del tramo donde ocurre el mayor descenso de pendiente entre tramos consecutivos de 2 km.
2. Índice de quiebre: R = S_c / S_a y ΔS = S_c − S_a; punto de quiebre = posición del máximo descenso.
3. Se reportan R y ΔS por región (Andina y Caribe por separado), con IC bootstrap por bloques.
4. Cruce espacial con centros poblados del DANE solo agregado por municipio (sin datos personales).

**Validación (condición para interpretar).** Inventario de eventos de avenida torrencial verificable (Servicio Geológico Colombiano, UNGRD u otro); **aún no verificado que exista descargable ni su cobertura**. Si se obtiene: AUC del índice R para discriminar cuencas con evento registrado de cuencas sin él, con IC 95 % por bloques; **criterio:** el límite inferior del IC de AUC > 0,60. Si no se obtiene o hay menos de 20 cuencas con evento, el frente queda en descriptivo.

**Limitación explícita.** Los perfiles son rutas hasta estaciones de aforo, que están en cauces ya relativamente estables; los abanicos reales suelen estar en cabeceras de valles que estas rutas no cubren. Un resultado negativo aquí no refuta la hipótesis física; solo refuta su detectabilidad con estos datos.

---

## F3. Transporte de sedimentos y erosión (producto pendiente × caudal)

**Pregunta.** ¿La potencia de corriente específica identifica las subcuencas que aportan mayor carga de sedimentos a embalses o acueductos?

**Diseño.**
1. Potencia de corriente por tramo: Ω = ρ·g·Q·S (W/m); potencia específica ω = Ω/ancho, con ancho w = a·Q^0,5 (a = 5 como caso base, a ∈ {3, 7} sensibilidad; supuesto declarado).
2. Q: Q_medio y Q_bankfull aproximado (percentil 95 de caudales diarios, reportado como proxy, no como caudal formativo).
3. Agregación por cuenca: máximo y percentil 90 de ω a lo largo del perfil; contraste cabecera vs. tramo bajo (donde ω cae indica depósito probable).

**Validación (condición para interpretar).** Concentración o carga de sólidos suspendidos medida (IDEAM) en estaciones coincidentes: correlación de Spearman entre ω_p90 y el rendimiento específico de sedimentos (t/km²/año) con **mínimo 30 estaciones** emparejadas; criterio: ρ de Spearman con IC inferior > 0,3. **Disponibilidad no verificada**; si hay menos de 30 pares, solo descriptivo.

**Limitación.** El transporte real depende de oferta de sedimento (litología, cobertura, deslizamientos) que este producto no contiene: mide capacidad de transporte, no aporte. No se comparará con embalses concretos sin datos de batimetría.

---

## F4. Ecología fluvial y conectividad (escalones del perfil)

**Pregunta.** ¿Los escalones de pendiente del perfil longitudinal permiten delimitar tramos homogéneos y detectar barreras naturales (rápidos, cascadas)?

**Diseño.**
1. Regresión segmentada del perfil z(x) con 1 a 6 puntos de ruptura; número de rupturas por BIC.
2. Un «escalón» candidato: ruptura con aumento de pendiente ≥ 3× respecto al tramo vecino y caída ≥ 10 m en ≤ 2 km, sobre el piso de pendiente.
3. Tramos homogéneos = segmentos entre rupturas con pendiente dentro de ±30 % de la mediana del segmento; se reporta su longitud.
4. Estabilidad: repetir con las rutas de flujo calculadas desde dos umbrales de acumulación distintos; criterio de estabilidad: ≥ 70 % de coincidencia de rupturas a ±1 km.

**Validación.** No existe en este proyecto un inventario verificado de cascadas o barreras naturales. Si se obtiene uno público (p. ej. de autoridades ambientales), se reporta la proporción de escalones candidatos a ≤ 2 km de un accidente conocido; **sin inventario, solo estabilidad interna.**

**Limitación crítica.** Un DEM de 90 m no resuelve cascadas pequeñas; es el frente más sensible a la resolución. Se prevé repetir con DEM de 30 m solo con permiso de descarga.

---

## Orden y costo sugeridos

| Frente | Datos nuevos | Esfuerzo | Riesgo principal |
|---|---|---|---|
| F1 | Ninguno | Bajo | Q en tramos por proporcionalidad al área |
| F3 | Posible: sólidos suspendidos IDEAM | Medio | Falta validación observada |
| F2 | Inventario de eventos (no verificado) | Medio | Rutas no cubren abanicos reales |
| F4 | DEM 30 m recomendado | Alto | Resolución del DEM |

Recomendación: ejecutar F1 primero (sin descargas), y solo después pedir permiso para los datos de F2–F4.
