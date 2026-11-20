# Prerregistro HE1, HE2 y HE3 (#274)

Fijado el 2026-11-19, **antes** de correr `he1_he2_periodo_ajuste.py` y `he3_torsion_accidental.py`.

## Lo que ya sabía al fijarlo (declarado para no ocultar sesgos)

- **Datos de HE6.** `he6_resultados.json` ya trae `T_modelo_s` y `CuTa_s` de cada diseño, pero no los analicé para HE1. Este script los recalcula desde las secciones de diseño.
- **Expectativa de HE4.** Con inercias brutas y prediseño por carga axial, T_motor ≈ 1,4–1,5·Ta entre 4 y 20 pisos, y Cu está entre 1,2 y 1,75. Con inercias fisuradas, mi expectativa es que T > Cu·Ta casi siempre. HE1 con inercias fisuradas es casi una confirmación esperada; lo informativo es el margen y la sensibilidad con inercias brutas.
- **Población de HE3.** Para HE3 solo conté la población (Ω), sin medir derivas: 400 plantas, 72 con Ω < 1. Con la primera malla salían 22, menos que el mínimo de 30, y por eso la amplié a 5 luces y 5 valores de k. Cronometré un edificio, sin mirar su resultado.

## HE1: el periodo del pórtico desnudo supera Cu·Ta

- **Población:** los 500 diseños espectrales de HE6. Son pórticos de 3×3 vanos, de 3 a 12 pisos, L de 4 a 8 m, Aa de 0,10 a 0,30 y perfiles C y D, ya ajustados para cumplir la deriva.
- **Medida:** T_modelo = mayor periodo modal del modelo de pórtico desnudo, comparado con Cu·Ta (A.4.2.1; Ta de A.4.2-3 para pórticos de concreto).
- **Principal:** inercias fisuradas (columnas 0,70·Ig, vigas 0,35·Ig), las que usa el motor. **Sensibilidad:** inercias brutas.
- **Criterio:** proporción con T_modelo > Cu·Ta, con IC95 de Wilson.

| Veredicto | Condición |
|---|---|
| **CONFIRMADA** ("la mayoría") | límite inferior > 0,5 |
| **REFUTADA** | límite superior < 0,5 |
| **NO CONCLUYENTE** | en otro caso |

- **Descriptivo:** mediana de T/Cu·Ta, por pisos, por Aa y por perfil.

## HE2: gobierna el ajuste A.5.4.5

- **Población:** la misma de HE1, con inercias fisuradas y sin torsión accidental.
- **Medida:** razón Vt/Vs. Vt es el cortante basal dinámico sin escalar (CQC; A.5.4-3); Vs es el de la FHE con T = mín(T_modelo, Cu·Ta). Se toma la menor de las dos direcciones.
- **Criterio:** proporción con Vt/Vs < 0,80 (edificio regular), con IC95 de Wilson. Usa los mismos umbrales que HE1 (límite inferior > 0,5 → CONFIRMADA; límite superior < 0,5 → REFUTADA).
- **Descriptivo:** mediana de Vt/Vs y del factor de ajuste.

## HE3: omitir la torsión accidental en el análisis dinámico

- **Familia paramétrica nueva:**

| Parámetro | Valores |
|---|---|
| Planta | 3×3 vanos de luz L ∈ {4, 5, 6, 7, 8} m |
| Pisos (de 3 m) | N ∈ {3, 6, 9, 12} |
| Núcleo | las 4 columnas interiores valen k ∈ {1; 1,5; 2; 2,5; 3} veces las de borde (núcleo rígido aproximado con columnas) |
| Voladizo perimetral | v ∈ {0, 1, 2, 3} m; agrega masa e inercia rotacional sin rigidez |
| Espectro | Aa = Av ∈ {0,10; 0,25}, perfil D |

  - Las columnas de borde salen de la carga axial de HE6.
  - Inercias fisuradas, sin iterar la deriva. La razón que se mide no depende de la escala de las fuerzas.

- **Flexibilidad torsional:** Ω = T_traslación / T_torsión de los modos fundamentales. La planta es **flexible** si Ω < 1. En plantas simétricas esto equivale a r < ls (EC8 4.2.3.2); la NSR-10 no define el término.
- **Medida:** deriva de borde = máxima deriva de punto (ejes de columna, combinada modo a modo) entre pisos y direcciones.
  - **Sin torsión:** modelo con el centro de masa en su lugar.
  - **Con torsión:** el mismo, más los 4 modelos con el centro de masa corrido ±5 % (A.3.6.7).
  - Ambos con el mismo factor de ajuste A.5.4.5.
  - Subestimación = 1 − deriva_sin / deriva_con.
- **Población principal:** plantas flexibles con Aa = 0,25 (n = 72).
- **Criterio:** proporción con subestimación > 10 %, con IC95 de Wilson. Mismos umbrales (límite inferior > 0,5 → CONFIRMADA; límite superior < 0,5 → REFUTADA). Si n < 30, INSUFICIENTE.
- **Además:**
  - mediana de la subestimación con IC95 bootstrap (semilla 274);
  - sensibilidad con Aa = 0,10;
  - contraste con las plantas rígidas (Ω ≥ 1);
  - resultados por k y por v.

## Limitaciones declaradas

- **Mallas sin peso de inventario.** Las proporciones describen la malla, no los edificios de Colombia.
- **HE1–HE2 heredan la geometría de HE6:** planta cuadrada simétrica, sin muros ni mampostería.
- **HE3 representa el núcleo con columnas grandes, no con muros** (los muros quedan para la F3). La planta es simétrica, así que la única excentricidad es la accidental; no se estudian plantas con excentricidad propia.
- **Ω es una razón de periodos,** una medida global y no por piso.
