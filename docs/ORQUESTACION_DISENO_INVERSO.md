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
las fuerzas sísmicas laterales pueden llegar como dato o derivarse del espectro (ver la sección siguiente); refuerzo continuo
en toda la luz, mismo diámetro arriba y abajo.

## Cortante basal desde el espectro y núcleo vectorizado (2026-11-08)

**Cadena nueva** (`ProyectoPortico(perfil_suelo="D", grupo_uso="I")`; el usuario ya no entrega las fuerzas sísmicas):
municipio → Aa, Av (A-4) + perfil de suelo → Fa, Fv (Tablas A.2.4-3/-4, interpolación lineal) → Ta = Ct·hⁿ^α (A.4.2-3) → Sa
(A.2.6, meseta hasta Tc) → Vs = Sa·W (A.4.3-1) → Fx = Cvx·Vs (A.4.3-2/-3) → E = Fx/R con R = R0 de la Tabla A.3-3
(DES 7,0 · DMO 5,0 · DMI 2,5, pórticos de concreto) → análisis → envolventes → diseño por nivel → costo APU.
Módulo: `packages/motor-geopot/src/cortante_basal.py`. Todas las tablas y ecuaciones se verificaron en `nsr10_chunks`
(ids citados en el docstring del módulo), incluido el límite de deriva de la Tabla A.6.4-1 (1,0 % de hp para concreto).

**Deriva como restricción:** además de resistencia, cada sección candidata debe cumplir Δ/hp ≤ 1,0 % con las fuerzas elásticas
(sin dividir por R, I = 1 permitido por A.6.2.1.2). En el ejemplo de Pereira (DES, perfil D) la deriva descarta 62 de las 104
secciones de la rejilla y cambia el óptimo: 250×750 mm. El permiso de A.6.4.1.1 (multiplicar por 0,7 con secciones fisuradas)
está disponible con `factor_deriva_fisurada=0.7` pero **no** se aplica por defecto.

**Núcleo vectorizado** (`grilla_vectorizada.py`): la rigidez es lineal en (A, I) de las vigas, así que K(b,h) = K₀ + A·K_a + I·K_i
se arma para N secciones por broadcasting; los casos D, L y E se resuelven juntos como columnas de una sola matriz de cargas
(una factorización por sección) y las combinaciones de B.2.4 salen por superposición (einsum), no resolviendo cada una.
Medido en esta máquina: 104 secciones en ~0,02 s (antes ~0,3 s en el análisis escalar); 50.000 secciones en ~4,5 s.
Con `preseleccion=K` el diseño exacto + costo APU solo se hace sobre las secciones que un proxy (área + acero requerido,
con la razón de precios medida en el propio APU) ordena primero, hasta reunir K diseños factibles. **Es una heurística, no una
garantía de óptimo global**: en una rejilla de 1.239 secciones coincidió con el barrido exacto con K = 10, 25 y 60 (una sola
rejilla, un solo proyecto); con `preseleccion=None` el barrido es exacto sobre toda la rejilla.

**Paridad:** el óptimo se reanaliza siempre con la ruta escalar de referencia (la del motor anterior) y la ejecución se
interrumpe si las demandas difieren más de 1e-6; en las pruebas la diferencia es ~1e-15.

**Lo que se descartó, y por qué** (decidido con datos, no por omisión):
- *Matrices dispersas:* el pórtico típico tiene 27–60 grados de libertad libres; una factorización dispersa es más lenta que la
  densa por lotes a ese tamaño. Cambiaría con edificios de cientos de nudos.
- *24 combinaciones como columnas de F:* la superposición necesita resolver solo 3 casos (D, L, E); resolver 24 columnas
  habría sido más trabajo para el mismo resultado.
- *JIT (Numba):* ya está instalado, pero el cuello de botella dejó de ser el análisis (4,5 s para 50.000 secciones, dominado por
  el LAPACK de NumPy); no se justifica añadir una dependencia de compilación.
- *MILP y teoría de grafos:* no se construyeron. Dónde sí aportarían: MILP cuando haya varias secciones por pórtico (asignar
  una sección por piso con restricciones de constructibilidad y continuidad con columnas, minimizando costo); grafos al importar
  topologías irregulares (BIM/IFC) para generar el modelo, en vez de la malla paramétrica actual. Hoy la malla es regular.

**Supuestos y límites nuevos:** peso sísmico = carga muerta + peso propio (sin viva); estructura regular y redundante
(φa = φp = φr = 1,0); sin torsión, P-Delta, cortante basal mínimo ni interacción suelo-estructura; el pórtico plano representa su
ancho tributario; T = Ta (el período de Rayleigh se reporta y se indica si cambiaría las fuerzas; en el ejemplo supera Cu·Ta
pero ambos están en la meseta del espectro, por lo que las fuerzas no cambian); perfil F rechazado (exige estudio geotécnico).

## Columnas, columna fuerte–viga débil y diseño integral (2026-11-08)

`motor-concreto/src/columna.py` (diagrama de interacción por compatibilidad de deformaciones, φ 0,65→0,90, Pn,max, ρ 1–4 %,
esbeltez con magnificación, Ve por Mpr, confinamiento DMI/DMO/DES) y `orquestador/src/diseno_integral.py` (rejilla lado de
columna × sección de viga, costo total APU vigas + columnas).

- **Conectado a la cascada**: municipio → A-4 → espectro → Vs → Fx → análisis vectorizado → deriva y Q → vigas → ΣMnb real de cada
  viga diseñada → columna (flexo-compresión con TODAS las combinaciones y columnas, C.21.6.2.2 con la Pu más desfavorable de cada
  nudo) → costo APU. Nada se reingresa.
- **Algoritmos**: la rigidez es lineal en (A, I) → N secciones por broadcasting; las fuerzas de las columnas salen de `k·T·U` en el
  mismo lote; el diagrama de interacción es una curva cacheada y toda la verificación es `np.interp` sobre el vector de demandas.
- **Verificación**: paridad vectorizado/escalar de vigas y de columnas (5e-15) abortando sobre 1e-6; equilibrio vertical, cortante
  basal y equilibrio de momentos del nudo; Po y punto balanceado en forma cerrada; la razón SCWB del óptimo se recalcula con
  indexación independiente.
- **Ejemplo** (Pereira, perfil D, DES, 3 vanos de 6 m × 3 pisos): óptimo columna 550 mm, viga 250×750 mm, costo total $31,9 M
  (vigas $14,0 M + columnas $17,9 M), deriva 0,83 %, Q = 0,011, ΣMnc/1,2ΣMnb = 1,02. 1.040 combinaciones en 4,6 s.
- **No verificado en el corpus** (marcado en cada verificación): Pn,max (corpus 0,75, ACI 0,80; se usa 0,75), Ash en DES
  (C.21-7/-8), so en DMO (C.21.3.5.6), Mpr = 1,25 fy, k de Jackson–Moreland y magnificación (C.10.10.5–7). φ de cortante 0,75
  (C.9.3.2.3) quedó verificado y se actualizó la marca.
- **Límites**: una sección de columna y una de viga en todo el pórtico (óptimo sobre la rejilla); flexión uniaxial; esfuerzos en el
  eje del nudo; ΣMnb sin aporte de losa; sin nudos (C.21.7), cimentación ni empalmes; Q > 1/3 se rechaza (sin segundo orden completo).

## Secciones distintas por piso: MILP + verificación exacta (2026-11-08)

`orquestador/src/diseno_por_pisos.py`. Cada piso elige su columna cuadrada y su viga de una biblioteca; el costo APU total se minimiza
con deriva (A.6.4), Q, diseño completo por piso, columna fuerte–viga débil entre pisos, columna que no crece hacia arriba y topes
de secciones distintas (columna / viga).

- **Por qué no es un MILP puro**: la rigidez de un piso depende de los vecinos, así que la deriva no es separable. Se usa un MILP
  maestro (scipy/HiGHS, binarias x[j,s], un candidato por piso, columna no creciente por umbrales, topes de secciones distintas)
  y un juez exacto: análisis matricial del pórtico real con secciones por piso y diseño de arriba hacia abajo.
- **Bucle**: biblioteca (pórticos uniformes → costo y razón deriva/cortante por piso) → MILP → verificación exacta → si falla se
  añade un corte exacto y de dominancia (todos los demás pisos iguales o más blandos), si mejora se re-linealiza la deriva
  alrededor del nuevo mejor y se adopta el costo exacto observado. Se detiene con una cota calibrada con los errores observados
  (mínimo 3 %) o a los 60 s (se avisa en `diagnostico["busqueda_completa"]`).
- **Resultado medido**: Pereira, perfil D, DES, 3 vanos × 4 pisos, biblioteca de 48 secciones: columnas 700/700/500/500 mm y vigas
  250×500, 350×800, 300×800, 250×500; costo $45,65 M frente a $47,67 M del mejor pórtico uniforme de la misma biblioteca
  (−4,2 %), en 15 s. El ahorro se mide solo contra un uniforme que cumple todo.
- **Contra fuerza bruta** (3 pisos, 12 secciones, 8.000 asignaciones analizadas una a una): el MILP devuelve un costo 1,0 % por
  encima del mínimo verdadero y nunca por debajo. Es una heurística con verificación exacta: no se afirma optimalidad global.
- **Hallazgo durante la construcción**: la razón deriva/cortante medida en pórticos uniformes es muy pesimista para el piso
  superior (un pórtico uniforme de vigas débiles amplifica la rotación de los nudos de abajo) y descartaba el óptimo real; por eso
  la deriva del MILP se linealiza alrededor del mejor verificado y no se usa el pórtico uniforme como cota.
- **Límites**: el costo del MILP viene de pórticos uniformes (la cota lleva tolerancia); la monotonía de la deriva respecto de c, b,
  h se supone en el corte de dominancia; nudo de la base sin verificar; mismos límites normativos del diseño integral.

## Fases siguientes (no construidas)

1. Extender la cascada sísmica ya construida (concreto) a los motores de mampostería y acero → cuantías finales; irregularidades φa/φp, torsión y P-Delta.
2. Vigas continuas, columnas, losas; Capítulo C.21.
3. Aplicar el contrato de contexto compartido a los motores existentes.
4. Recuperar φ y Tabla C.9.5(a) del PDF fuente y cerrar los dos puntos no verificados.
