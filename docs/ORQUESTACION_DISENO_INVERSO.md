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
- Sin Capítulo C.21 (detallado sísmico), sin torsión, deflexión solo por altura mínima l/16.
- **No verificados contra el corpus**: φ de cortante 0,75 (C.9.3.2.3) y l/16 de la Tabla C.9.5(a). Revisar antes de uso real.
- La sección óptima de 250 mm de base puede violar requisitos de detallado sísmico o constructivos; el óptimo es sobre la rejilla (b 250–500, h 300–800, paso 50; barras #4–#8, 2–8; estribos #3).
- Costo = costo directo APU determinista del catálogo (Barranquilla 2026) por elemento; no incluye AIU ni Monte Carlo.
- Herramienta de apoyo: requiere revisión y firma de un ingeniero (issue #18).

## Fases siguientes (no construidas)

1. Cascada sísmica/geoespacial: capas de amenaza → Aa/Av del Apéndice A-4 (por municipio, no la tabla departamental de `sismica.py`) → fuerzas → motores de mampostería/acero → cuantías finales.
2. Vigas continuas, columnas, losas; Capítulo C.21.
3. Aplicar el contrato de contexto compartido a los motores existentes.
4. Recuperar φ y Tabla C.9.5(a) del PDF fuente y cerrar los dos puntos no verificados.
