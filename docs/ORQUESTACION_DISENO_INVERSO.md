# Orquestación en cascada y diseño inverso (prototipo, 2026-11-08)

## Qué hace

El usuario ingresa **una sola vez** luz, cargas y calidad del concreto. De ahí la cascada es automática:

```
datos del proyecto ──► motor-concreto (verifica NSR-10 Título C) ──► motor-apu (costo directo) ──► comparación
        ▲                         │ si falla                                  │
        └──── orquestador: itera b, h, barras, estribos (peso propio recalculado en cada candidato)
```

En lugar de «cumple / no cumple», devuelve la sección **más económica que cumple**, con la razón demanda/capacidad
de cada verificación y su numeral. Paquetes: `packages/motor-concreto`, `packages/orquestador`
(+ `run_montecarlo` opcional en `motor-apu`, retrocompatible).

## Cómo se reporta el ahorro (regla de honestidad)

- El `% de reducción` **solo** se calcula contra un diseño base que **cumple**.
- Si el base no cumple, se reporta el costo mínimo para cumplir y la **corrección mínima que conserva b y h**; no se inventa un porcentaje.
- Ejemplo real (luz 6 m, D=18 kN/m sin peso propio, L=10 kN/m, f'c 21 MPa): un base sobredimensionado 400×700 con 6#8 cumple y cuesta $2.470.636; el óptimo 250×550 con 3#7 y estribos #3 c/225 cuesta $1.294.903 (−47,6 %). Ese porcentaje es relativo a **ese** base, no una promesa general. Un base 300×450 con 3#5 falla por flexión y estribos; conservando 300×450 se corrige con 3#8 y E c/175 ($1.379.105), mientras que cambiar la sección cuesta $1.294.903.

## Límites declarados

- Viga simplemente apoyada, carga gravitacional, sección rectangular, una capa de barras, estribos uniformes, λ = 1.
- Modo gravitacional (sin municipio): sin Capítulo C.21. Modo sísmico: ver la sección siguiente. En ambos: sin torsión, deflexión solo por altura mínima l/16.
- **No verificados contra el corpus**: φ de cortante 0,75 (C.9.3.2.3) y l/16 de la Tabla C.9.5(a). Revisar antes de uso real.
- La sección óptima de 250 mm de base puede violar requisitos constructivos y, en modo gravitacional, de detallado sísmico; el óptimo es sobre la rejilla (b 250–500, h 300–800, paso 50; barras #4–#8, 2–8; estribos #3).
- Costo = costo directo APU determinista del catálogo (Barranquilla 2026) por elemento; no incluye AIU ni Monte Carlo.
- Herramienta de apoyo: requiere revisión y firma de un ingeniero (issue #18).

## Cascada geoespacial → sísmica (2026-11-08)

`ProyectoViga(municipio=...)` dispara: Apéndice A-4 (Aa, Av del municipio, `motor-geopot/src/a4.py`) → zona (A.2.3: Baja si Aa y
Av ≤ 0,10; Alta si alguno > 0,20) → capacidad mínima de disipación (Baja DMI, Intermedia DMO, Alta DES) → requisitos de
C.21.5 aplicados a la viga → costo APU. Mismas cargas, otra amenaza: Tubará (Baja, DMI) 250×550 3#7 $1.294.903; Pereira (Alta, DES)
250×700 3#6 + 3#6 superiores, estribos c/150 $1.661.995 (+28 %).

- Datos locales: `motor-geopot/data/nsr10_a4_municipios.json` (1.117 municipios, 29 con Decreto 092/2011), generado por
  `scripts/ingesta/nsr10/generar_snapshot_a4.py`; idéntico a la tabla de Supabase (suma de control y conteo iguales). La zona
  calculada con A.2.3 coincide con la columna `zona` de la tabla en los 1.117 municipios.
- Verificado en el corpus: C.21.5.1.2, C.21.5.1.3, C.21.5.2.1, C.21.5.2.2, C.21.5.3.1/.2, C.21.5.4.1/.2, B.2.4-5 y -7, A.2.3.1-3.
- No verificado: Mpr = 1,25·fy con φ = 1,0; φ de cortante; el mapeo zona→capacidad para concreto se tomó del esquema de F.3.2.1.1 (acero).
- DMO se trata con los requisitos de DES (cota conservadora, C.21.3.4 no implementado). Refuerzo simétrico arriba/abajo, estribos de
  confinamiento en toda la luz, sin empalmes, nudos ni efecto de sitio (Fa, Fv).
- La demanda sísmica de flexión no se calcula aquí: entra como `momento_apoyo_kn_m` desde el análisis del pórtico (siguiente paso:
  conectar `motor-estructural`). Sin ella solo se verifican detallado y cortante por capacidad.
- `capacidad` solo puede subir la mínima de la zona; bajarla lanza error. Nombre de municipio ambiguo exige departamento o código DANE.

### Hallazgo: tabla departamental de `sismica.py` incorrecta

`packages/motor-geopot/src/sismica.py::DEPARTAMENTOS` (usada por `zona_sismica` y el endpoint de geopot) no coincide con el
Apéndice A-4 en ninguna de las 27 capitales comparables (ej. Barranquilla 0,15/0,20 frente a 0,10/0,10; Bogotá la clasifica Alta
cuando A-4 da Intermedia; Yopal 0,15/0,20 frente a 0,30/0,20, es decir, subestima). El orquestador ya no la usa. Corrección pendiente en tarea aparte.

## Motor de diseño restringido: análisis matricial + envolventes (2026-11-08)

Se pasó de «evaluar fórmulas sobre una viga simple» a un motor que analiza el pórtico y diseña contra restricciones.

- `packages/motor-analisis`: rigidez directa 2D (3 gdl por nodo, elementos viga-columna Euler-Bernoulli), casos D, L, E,
  combinaciones NSR-10 (1.4D; 1.2D+1.6L; 1.2D+1.0L±E; 0.9D±E) y envolvente de M⁺, M⁻, V a lo largo de cada elemento, con la
  combinación gobernante en cada punto. Verificado contra solución cerrada: viga simple (reacciones, M, flecha 5wL⁴/384EI),
  biempotrada (−wL²/12, +wL²/24), continua de dos vanos (−wL²/8, 3wL/8, 10wL/8), voladizo (PL³/3EI), pórtico con viga rígida
  (Ph/4) y equilibrio global; rechaza modelos inestables.
- `packages/motor-concreto/src/diseno_viga.py`: dado el nivel DMI/DMO/DES y las demandas de la envolvente, diseña refuerzo
  superior e inferior independientes y estribos en dos zonas (2h de confinamiento y centro). Restricciones duras:
  DMO b ≥ 200 mm (C.21.3.4.1); DES b ≥ mín(0,3h; 250 mm) (C.21.5.1.3) y b ≤ c2 + 2·mín(c2; 0,75·c1) (C.21.5.1.4); ln ≥ 4d;
  ρmín (C.10.5.1) y ρ ≤ 0,025; ≥ 2 barras continuas arriba y abajo; Mn⁺ ≥ ½ Mn⁻ (DES) o ⅓ (DMO) en la cara y ≥ ¼ (DES) o ⅕ (DMO)
  del máximo en cualquier sección; confinamiento s ≤ mín(d/4; 8db; 24dest; 300); cortante por capacidad Ve = (Mpr⁻+Mpr⁺)/ln + wu·ln/2
  (DES, Mpr con 1,25·fy) y con Mn en DMO; Vc = 0 en confinamiento cuando el cortante sísmico es ≥ la mitad de Ve (DES).
- `packages/orquestador/src/diseno_portico.py`: municipio → A-4 → capacidad; por cada sección candidata se vuelve a analizar el
  pórtico (la viga cambia la rigidez y por tanto el reparto sísmico), se toma la peor demanda y se elige la de menor costo APU.

### Sobre el ancho de 250 mm

El óptimo anterior daba b = 250 mm porque la rejilla empezaba ahí, no por una restricción olvidada. La norma verificada en el corpus
dice «no menor que el más pequeño de 0,3h y 250 mm» (C.21.5.1.3): el mínimo es **mín**(0,3h; 250), no el mayor. Con h = 600 el piso
normativo es 180 mm, y con h ≥ 833 mm es 250 mm. La rejilla ahora empieza en 200 mm y el ancho queda acotado por las columnas.

### Huecos del corpus encontrados al verificar

`C.21.3.3 (a)/(b)` (cortante de diseño DMO) y la lista de inercias agrietadas de `C.10.10.4.1` aparecen truncadas en `nsr10_chunks`
(solo el encabezado). Se usaron los valores del ACI 318-08 (Mn para DMO; 0,35·Ig viga y 0,70·Ig columna) y se marcaron como no
verificados. Pendiente: re-ingestar esos numerales desde el PDF fuente. También se corrigió una cifra propia: Ec = 4700·√f'c
(C.8.5.1), no 3900.

### Límites (además de los anteriores)

Una sola sección para todas las vigas; columnas dadas y no diseñadas (sin columna fuerte-viga débil C.21.6.2 ni nudos C.21.7);
las fuerzas sísmicas laterales llegan como dato (el cortante basal desde Sa, Fa, Fv, T, R todavía no está encadenado: requiere
verificar las tablas A.2.4-3/-4 y A.4.2 en el corpus); refuerzo continuo en toda la luz, mismo diámetro arriba y abajo.

## Fases siguientes (no construidas)

1. Cascada sísmica/geoespacial: capas de amenaza → Aa/Av del Apéndice A-4 (por municipio, no la tabla departamental de `sismica.py`) → fuerzas → motores de mampostería/acero → cuantías finales.
2. Vigas continuas, columnas, losas; Capítulo C.21.
3. Aplicar el contrato de contexto compartido a los motores existentes.
4. Recuperar φ y Tabla C.9.5(a) del PDF fuente y cerrar los dos puntos no verificados.
