# Prerregistro F3b (#275, #276): confiabilidad sin censura (FORM + muestreo por importancia)

Fijado el 2026-11-20, **después** de ver los resultados F3 ([`RESULTADOS_F3_CONFIABILIDAD.md`](RESULTADOS_F3_CONFIABILIDAD.md)) y **antes** de calcular ningún β sin censura.

## Lo que ya se vio (declarado)

**La F3b no es ciega.** De la F3 ya se conocen:
- los β por debajo de 4,5, que se estimaron bien con Monte Carlo;
- la fracción censurada por zona: 69 %, 82 % y 94 % en baja, intermedia y alta;
- los resultados de la variante alta, en los que H-F3b sale en la dirección prevista y H-F3c al revés.

Las hipótesis de abajo que se apoyan en esas observaciones se marcan **[informada por F3]**. Una confirmación de ese tipo pesa menos que una ciega. La réplica independiente (un corpus nuevo, aleatorio y no de rejilla) queda como trabajo futuro.

## Qué cambia frente a la F3 (y qué no)

**No cambia:**
- el corpus (los 1.348 edificios con solución);
- la reconstrucción con `disenar_edificio`;
- las fuerzas D y L;
- las funciones de estado límite;
- las secciones críticas;
- las tres variantes del modelo probabilístico.

Todo se importa de `confiabilidad_f3.py`, sin copiarlo.

**Cambia la estimación de Pf por elemento:**
1. **Espacio normal estándar:** las 7 variables se escriben como transformaciones de u ~ N(0, I₇) (lognormal: exp(μ + s·u); normal; Gumbel por su CDF inversa de Φ(u)).
2. **FORM:** se busca el punto de diseño u\* con HL-RF y gradiente por diferencias finitas (máximo 60 iteraciones, tolerancia ‖Δu‖ < 10⁻³).
3. **Muestreo por importancia** centrado en u\*: N_IS = 2·10⁵ muestras z ~ N(0, I) con u = u\* + z y peso w = exp(−u\*·z − ‖u\*‖²/2), semilla 2753.
   - Pf = media(1[g < 0]·w) y β = −Φ⁻¹(Pf).
   - El muestreo corrige el error de FORM, así que el estimador es insesgado aunque u\* no sea exacto.
4. **Precisión:** se reporta el CoV de Pf por elemento.
   - Si el CoV es > 0,10, se repite con 10⁶ muestras.
   - Si sigue > 0,10, el elemento se marca «impreciso» y se cuenta.
5. **Techo numérico:** si FORM da ‖u\*‖ > 8, el elemento se reporta con β > 8 (Pf < 6·10⁻¹⁶). Ese techo es irrelevante para cualquier comparación de diseño.
6. **Columnas:** la tabla de interpolación de Mn(P) se construye **una vez por diseño de columna** y se guarda en caché. Es la misma rejilla de la F3.

## Puerta de calidad (se verifica antes de mirar las hipótesis)

- **Q1, concordancia con Monte Carlo:** se toman los elementos críticos de la F3 con 100 o más fallas en 10⁶ (β_MC ≤ ~3,7). En ellos, |β_IS − β_MC| debe ser ≤ 0,10 en el 95 % de los casos y la mediana de |Δβ| debe ser ≤ 0,03.
- **Q2, precisión:** los elementos «imprecisos» deben ser ≤ 1 %.
- **Si Q1 o Q2 fallan,** las hipótesis **no se evalúan**. Se reporta el fallo del método y se corrige con otro prerregistro.

## Hipótesis (una sola evaluación; regla de variantes igual que en la F3)

β = β₅₀ del elemento crítico (el mínimo sobre vigas y columnas). IC95 bootstrap con semilla 2753 y 2.000 réplicas.

| Id | Hipótesis | Criterio de «CONFIRMADA» |
|---|---|---|
| **H-F3b-1** (zona) [informada por F3] | En zona de amenaza alta el diseño sísmico deja más reserva bajo gravedad que en zona baja | mediana(β, alta) − mediana(β, baja) ≥ 0,5, con IC95 > 0 |
| **H-F3b-2** (no uniformidad) | La confiabilidad del corpus **no** es pareja: la dispersión entre edificios supera la que buscan las calibraciones de código | rango intercuartílico de β ≥ 0,75, con límite inferior del IC95 ≥ 0,5 |
| **H-F3b-3** (altura) [informada por F3] | En zona baja, los edificios altos (N ≥ 9) tienen **más** β que los bajos (N ≤ 5), al revés de H-F3c | mediana(altos) − mediana(bajos) > 0, con IC95 > 0 |

**Lectura de las variantes:**
- **CONFIRMADA** si cumple en las tres variantes (central, baja y alta).
- **DEPENDE DEL SUPUESTO** si cumple en la central y falla en alguna otra.
- **REFUTADA** si no cumple en la central.

## Descriptivo (sin criterio)

- **β sin censura por zona, perfil, f'c, grupo de uso y altura:** mediana, percentil 10 y fracción con β < 3,8.
- **Sensibilidad** (pendiente en la F3 y entregada aquí): los factores de importancia α² de FORM en el elemento crítico, con la variable dominante por edificio y su frecuencia en el corpus.
- **Reserva frente a la referencia:** distribución de β − 3,8. Se compara con los β objetivo de la calibración ACI/ASCE (≈ 3,0–3,5 para flexión en vigas, a 50 años), solo como orden de magnitud y **sin citarlos como valores exactos**.

## Limitaciones

- **Hereda todas las de la F3:** el β es del elemento y no del sistema, las distribuciones no están calibradas, el corpus es sintético y no hay corrosión.
- **No es ciega** respecto a la F3; ver arriba.
- **Puntos de diseño múltiples:** FORM supone uno por elemento. El muestreo centrado en un solo u\* puede subestimar Pf si hay modos de falla separados (por ejemplo, P > P₀ frente a flexión en una columna). Q1 lo detecta solo donde hay datos de Monte Carlo; se declara.
- **Alcance:** nada de esto aprueba ni desaprueba un diseño. Todo diseño pasa por la F4 y por la firma de un ingeniero (#18).
