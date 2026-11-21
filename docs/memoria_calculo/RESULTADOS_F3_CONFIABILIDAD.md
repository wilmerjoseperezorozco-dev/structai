# Resultados F3 (#275, #276): confiabilidad bajo gravedad de los pórticos diseñados con la NSR-10

Corrida única según [`PRERREGISTRO_F3_CONFIABILIDAD.md`](PRERREGISTRO_F3_CONFIABILIDAD.md), 2026-11-20.

- **Edificios:** los 1.348 con solución del corpus F1. La F4 reprodujo `cumple` en los 1.348 (0 excluidos).
- **Simulación:** Monte Carlo con 10⁶ muestras por elemento y semilla 2753, censura en β = 4,5. Tomó 3.199 s con 6 procesos.
- **Datos:** [`beta_por_edificio.csv`](../../data/memorias_sinteticas/f3/beta_por_edificio.csv) y [`resultados_f3.json`](../../data/memorias_sinteticas/f3/resultados_f3.json).

## Veredictos (regla prerregistrada)

| Hipótesis | Central | Baja | Alta | Veredicto |
|---|---|---|---|---|
| **H-F3a** adecuación: mediana β₅₀,mín ≥ 3,8 y límite inferior del IC ≥ 3,5 | 4,5 (censurada), IC [4,5; 4,5] ✔ | 4,5, IC [4,5; 4,5] ✔ | **3,81**, IC [3,71; 3,91] ✔ | **CONFIRMADA** |
| **H-F3b** zona alta − zona baja ≥ 0,5 | 0,0, IC [0; 0] ✘ | 0,0 ✘ | **1,31**, IC [1,19; 1,45] ✔ | **REFUTADA** (por regla) |
| **H-F3c** bajos (N ≤ 5) − altos (N ≥ 9) en zona baja > 0 | 0,0, IC [−0,08; 0] ✘ | 0,0 ✘ | **−0,62**, IC [−0,92; −0,34] ✘ | **REFUTADA** |

## Lectura honesta

### 1. H-F3a se confirma, pero con poco margen en la variante desfavorable

- **Variante central:** 1.134 de 1.348 edificios (84 %) quedan censurados en β > 4,5. Solo el 6,5 % baja de 3,8 y el 0,07 % baja de 3,0.
- **Variante alta** (incertidumbre desfavorable):
  - la mediana es 3,81, apenas sobre la referencia;
  - **el 25 % de los edificios queda con β < 3,0** y el 50 % con β < 3,8;
  - **en zona sísmica baja la mediana es 3,19**, por debajo de la referencia EN 1990 RC2.
- **Conclusión:** el diseño NSR-10 del corpus es adecuado bajo gravedad con los supuestos centrales. Si la resistencia del concreto en obra y la carga viva real son más inciertas (lo plausible en obra pequeña en Colombia), los edificios de zona baja son los que quedan cortos. Esto refuerza la línea de calibración con datos colombianos de #276.

### 2. H-F3b y H-F3c se refutan por regla, pero la prueba no podía discriminar en la central

- **El prerregistro tenía un defecto de diseño, y se declara.** Con 84 % de censura en la central y 99,8 % en la baja, la mediana es 4,5 en todos los grupos, así que la diferencia de medianas es 0 por construcción. «REFUTADA» aquí significa **«el criterio fijado no la sostiene»**, no «se demostró lo contrario».
- **H-F3b en la variante alta:** cuando la censura deja de dominar, la dirección prevista aparece con fuerza (+1,31, IC [1,19; 1,45]).
- **Exploratorio, sin criterio, posterior a ver los datos.** En la central, la fracción censurada sube con la amenaza sísmica:

  | Zona | Censurados | β del percentil 10 |
  |---|---|---|
  | Baja | 69 % | 3,65 |
  | Intermedia | 82 % | 4,08 |
  | Alta | 94 % | ≥ 4,5 |

  Es consistente con H-F3b, pero **no cuenta como confirmación**.
- **H-F3c** sale al revés de lo previsto en la variante alta: los edificios altos tienen **más** β que los bajos (−0,62). Una explicación probable, sin verificar: en los edificios altos de zona baja el viento o las combinaciones mínimas y la rigidez exigida por la deriva sobredimensionan las columnas inferiores. En los edificios bajos, en cambio, la viga del primer nivel gobierna con poca reserva.

### 3. Composición del elemento crítico (descriptivo)

- **Las vigas gobiernan casi siempre:** el 99,3 % en la central y el 96,9 % en la alta.
  - ~~En la central, la viga del nivel 1 es la crítica en el 85 % de los edificios.~~ **Corrección (2026-11-20):** era un artefacto de desempate. Con 84 % de censura, todos los elementos valen 4,5 y `min()` devuelve el primero (nivel 1). Sin empates (F3b), la crítica es la **viga del último nivel** en el 63–76 % de los edificios. Ver `RESULTADOS_F3B_SIN_CENSURA.md` §2.
- **Las columnas casi nunca son el elemento crítico bajo gravedad** (0,7 % y 3,1 %). Su diseño lo controla el sismo, que deja reserva frente a la gravedad.

### 4. Deriva ante el sismo de diseño (descriptivo)

- **Probabilidad de exceder el límite:** con κ ~ U[0,7; 1,3] y σ_ln Sa = 0,3, la mediana de P(uso real de la deriva > 1) es **0,42**, y el **81 %** de los edificios tiene P > 10 %.
  - El optimizador lleva la deriva cerca del límite, así que la incertidumbre de rigidez y espectro la cruza a menudo.
  - Es una **probabilidad de exceder el límite de código**, no de colapso.
- **Reserva por Cu·Ta:** el periodo límite Cu·Ta gobierna en el **86 %** de los edificios. En esos casos, el Sa en el periodo del modelo es en mediana el **92 %** del Sa de diseño, una reserva de ~8 % que la NSR-10 introduce a propósito (conecta con la HE1).

## Qué se corrige para una F3b (nuevo prerregistro, no retroactivo)

1. **Quitar la censura:** muestreo por importancia o FORM/SORM, para estimar β > 4,5 sin 10⁸ muestras. Así las comparaciones entre grupos pasan a ser posibles en la variante central.
2. **Comparar con una estadística que use la cola:** el percentil 10 de β, o la fracción por debajo de 3,8, en vez de la mediana.
3. **Calibrar f'c y la carga viva con datos colombianos** (#276), porque la variante alta cambia la conclusión en zona baja.

## Limitaciones (del prerregistro, vigentes)

- El β es del elemento crítico, no del sistema: no hay redistribución ni correlación entre elementos.
- Las distribuciones son supuestos del orden de la literatura y no están calibradas.
- El corpus es sintético: diseños óptimos de una rejilla, no edificios reales.
- No hay corrosión ni flujo plástico, y no se evalúan cortante ni nudos.
- **Nada de esto aprueba ni desaprueba un diseño.** Todo diseño pasa por el verificador F4 y por la firma de un ingeniero (#18).
