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

## Fases siguientes (no construidas)

1. Cascada sísmica/geoespacial: capas de amenaza → Aa/Av del Apéndice A-4 (por municipio, no la tabla departamental de `sismica.py`) → fuerzas → motores de mampostería/acero → cuantías finales.
2. Vigas continuas, columnas, losas; Capítulo C.21.
3. Aplicar el contrato de contexto compartido a los motores existentes.
4. Recuperar φ y Tabla C.9.5(a) del PDF fuente y cerrar los dos puntos no verificados.
