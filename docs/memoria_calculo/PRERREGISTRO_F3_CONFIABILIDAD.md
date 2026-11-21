# Prerregistro F3 (#275, #276): confiabilidad de los pórticos diseñados con la NSR-10

Fijado el 2026-11-20, **antes** de calcular ningún índice β sobre el corpus.

- **Lo visto hasta ahora:** el corpus F1 (2.048 edificios: 1.348 con solución y 700 sin solución) y los resultados F2. Ninguna corrida de confiabilidad.
- **Script:** `scripts/memorias_sinteticas/confiabilidad_f3.py`. Se probó solo con `--piloto 3` (3 edificios, para verificar que corre); esos números no se miran para fijar criterios.

## Pregunta

¿Las vigas y columnas de pórticos de concreto diseñados con la NSR-10 (el óptimo de la rejilla F1) alcanzan una confiabilidad adecuada bajo cargas de gravedad? ¿Esa confiabilidad es **pareja** entre zonas de amenaza sísmica, alturas y suelos, o el diseño sísmico deja reservas desiguales?

## Alcance (y lo que se excluye a propósito)

- **Estado límite principal: resistencia bajo gravedad**, D + L con el máximo de L en 50 años.
  - **Vigas:** flexión en las secciones críticas de cada nivel (momento negativo en la cara del apoyo y positivo en el vano), con el refuerzo que diseñó la F4.
  - **Columnas:** flexo-compresión con el contorno lineal biaxial y la curva de interacción **nominal** (sin φ).
- **Excluido: la confiabilidad sísmica de resistencia.** Con R > 1 los elementos están diseñados para fluir ante el sismo de diseño, así que una probabilidad de «falla por resistencia» bajo ese sismo no tiene sentido sin análisis no lineal y curva de amenaza. Queda para un trabajo futuro con el SGC (curvas de amenaza) y análisis no lineal.
- **Excluido: cortante, nudos, anclajes y deflexiones** (la F4 no los verifica completos; ver `NO_VERIFICA`).
- **Índice reportado:** β a 50 años del **elemento crítico** de cada edificio (el mínimo sobre vigas y columnas). Es una cota superior del β del sistema en serie, y se declara así.

## Datos

- **Edificios:** los 1.348 edificios con solución del corpus F1, todos, sin muestreo.
- **Reconstrucción:**
  - Cada diseño se rehace con `disenar_edificio` a partir de las entradas y las secciones óptimas de `corpus.csv`.
  - Se exige que la F4 reproduzca `cumple`. Si no lo hace, el caso se reporta y se excluye (criterio de calidad, no de resultado).
- **Fuerzas:** los casos D y L del análisis lineal 3D (`_resolver_casos`), por elemento y sección.

## Modelo probabilístico (fijado aquí)

Todas las variables son **independientes** y multiplican al valor nominal. Los valores son SUPUESTOS del orden reportado en la literatura de calibración de códigos (Nowak y Szerszen 2003, ACI Structural Journal; JCSS Probabilistic Model Code 2001). **No se citan como valores exactos de esas fuentes.** Por eso la conclusión se exige en **tres variantes**:

| Variable | Distribución | Central (λ, V) | Baja | Alta |
|---|---|---|---|---|
| f'c en obra | lognormal | 1,20; 0,15 | 1,30; 0,10 | 1,10; 0,20 |
| fy (Grado 420) | lognormal | 1,13; 0,05 | 1,15; 0,03 | 1,10; 0,08 |
| Carga muerta D | normal | 1,05; 0,10 | 1,03; 0,08 | 1,08; 0,12 |
| Carga viva, máximo en 50 años | Gumbel (máx.) | 1,00; 0,18 | 0,95; 0,15 | 1,05; 0,25 |
| Modelo de resistencia, flexión (θR) | lognormal | 1,02; 0,06 | 1,05; 0,05 | 1,00; 0,10 |
| Modelo de resistencia, flexo-compresión (θR) | lognormal | 1,00; 0,08 | 1,02; 0,06 | 0,98; 0,12 |
| Modelo del efecto de carga (θS) | lognormal | 1,00; 0,10 | 1,00; 0,08 | 1,00; 0,15 |

«Baja» y «alta» se refieren a la **incertidumbre**: en la columna «baja» todo es más favorable y en la «alta», más desfavorable.

**Función de estado límite:**

- **Vigas:**
  - g = θR·Mn(f'c, fy) − θS·(xD·M_D + xL·M_L).
  - Mn se evalúa con `_mn_nominal` y las barras diseñadas, en la sección con mayor cociente nominal de cada signo.
- **Columnas:**
  - g = 1 − θS·(Mx + My) / (θR·Mn(P)), con P = θS·(xD·P_D + xL·P_L).
  - Mn(P) sale de la curva nominal interpolada en una rejilla de (f'c, fy); si P > P₀, hay falla.
  - Se evalúan la columna más cargada y la de mayor momento de gravedad de cada piso.

**Simulación:**
- Monte Carlo con 10⁶ muestras por elemento y semilla 2753.
- β = −Φ⁻¹(Pf).
- Con 0 fallas, β se censura en «> 4,5», porque Pf < 3·10⁻⁶ con 95 % de confianza. Las medianas se calculan con los censurados al valor del límite, y se reporta cuántos hay.

## Hipótesis y criterios (una sola evaluación, variante central y las dos de sensibilidad)

| Id | Hipótesis | Criterio de «CONFIRMADA» |
|---|---|---|
| **H-F3a** (adecuación) | El elemento crítico de los pórticos diseñados con la NSR-10 alcanza la referencia β₅₀ = 3,8 (EN 1990, clase de consecuencias RC2; referencia internacional, no requisito de la NSR-10) | mediana de β₅₀,mín ≥ 3,8, con IC95 bootstrap (semilla 2753, 2.000 réplicas) cuyo límite inferior sea ≥ 3,5 |
| **H-F3b** (no uniformidad) | En zona de amenaza alta el diseño sísmico deja más reserva bajo gravedad que en zona baja | mediana(β, alta) − mediana(β, baja) ≥ 0,5, con IC95 bootstrap > 0 |
| **H-F3c** (altura) | En zona baja, los edificios altos (N ≥ 9) tienen β menor que los bajos (N ≤ 5), porque la gravedad domina el diseño de las columnas inferiores | diferencia de medianas (bajos − altos) > 0, con IC95 > 0 |

**Lectura de las variantes:**
- Una hipótesis es **CONFIRMADA** si cumple en las tres variantes.
- Es **DEPENDE DEL SUPUESTO** si cumple en la central pero no en alguna de las otras dos.
- Es **REFUTADA** si no cumple en la central.

## Descriptivo (sin criterio)

- **Composición de las fallas:** fracción de edificios cuyo elemento crítico es viga o columna, y en qué piso.
- **Sensibilidad:** variable dominante por la correlación de rangos entre g y cada variable en las muestras con g < cuantil del 1 %.
- **β por perfil de suelo, por f'c y por uso** (grupo I frente a III).
- **Deriva ante el sismo de diseño:** P(uso real de la deriva > 1).
  - **Supuestos:** rigidez efectiva κ ~ U[0,7; 1,3] veces la del modelo fisurado (incluye el rango bruto–fisurado de la HE1) y error epistémico del espectro lognormal con σ_ln = 0,3.
  - **Escalamiento:** uso_real = uso_diseño · Sa(T/√κ)/Sa(T_diseño) / κ, con T el periodo modal. Desprecia el cambio del exponente k de la distribución de fuerzas y lo declara.
  - **Conexión con la HE1:** cuando Cu·Ta gobierna, el diseño usa un Sa mayor que el del periodo real. Se reporta esa reserva.

## Limitaciones declaradas

- **El β es del elemento crítico, no del sistema.** No hay redistribución, y la correlación entre elementos del mismo edificio no se modela.
- **Distribuciones sin calibrar.** No se ajustaron a datos colombianos: la carga viva de vivienda en Colombia, la resistencia del concreto de obra pequeña y la calidad de la mano de obra quedan como SUPUESTOS. Las variantes miden cuánto pesan.
- **Corpus.** Diseños óptimos de una rejilla (F1), no de ingenieros. Es una malla sin ponderar por inventario y con plantas regulares solo de pórticos.
- **Sin efectos dependientes del tiempo:** ni corrosión ni flujo plástico. La corrosión en la costa es parte de #276 P4.
- **Alcance del resultado:** nada de esto aprueba ni desaprueba un diseño. Es un estudio de calibración, y cualquier diseño pasa por el verificador F4.
