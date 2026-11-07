# Resultados: umbrales de lluvia (§19), distribución del área de movimientos en masa (§20) y hipótesis H1-H5 (§23)

Ejecutado el 2026-11-07 y 2026-11-08 según `PROTOCOLO_ANALISIS.md` (cada protocolo se fijó antes de correr). Los resultados se leen **contra su criterio preregistrado**, no contra su significancia a secas. Señales estadísticas, no alertas oficiales.

## §19 Umbrales de lluvia acumulada–duración (E–D), resultado global
UNGRD 2019-2024 (4.442 eventos municipio-día con CHIRPS diario; 3.189 de calibración y 1.253 de prueba reservada 2023-2024; 1.537.467 días negativos).

| Contraste | Resultado | Criterio | Veredicto |
|---|---|---|---|
| T1: AUC de la lluvia acumulada (D\* = 5 días) | **0,775** (IC95 % 0,752-0,790) | límite inferior > 0,5 | **Cumple** |
| T2: curva E–D (E = 0,03·D^1,66, en % de la lluvia anual) | TSS **+0,090** (IC +0,079; +0,104) con sensibilidad 0,99 y **falsas alarmas 0,90** | TSS > 0 | Cumple en la letra, **pero la regla alerta casi todos los días** |
| T3: ¿la curva supera a la regla de un solo D\*? | La regla simple: TSS **+0,253** (sensibilidad 0,93, falsas alarmas 0,68) | La curva debe superar a la regla simple | **No**: la curva E–D no aporta; la regla simple es mejor |

**Lectura.** La lluvia acumulada de 5 días discrimina los días con movimiento reportado (AUC 0,775), pero la curva E–D del protocolo no mejora a un umbral simple y, tal como se calibra (percentil 5 de los positivos), dispara casi siempre. Límites declarados: la fecha de la UNGRD es la del reporte; 2022 aporta 4.176 de 7.451 eventos; CHIRPS a 5 km subestima la intensidad convectiva; sin humedad antecedente del suelo; **no es un sistema de alerta temprana**.
**Por región:** el Caribe no se ajusta (63 eventos de calibración, menos de 100). La corrida por región de las demás se interrumpió y se relanzó (resultados pendientes de registrar); este informe se actualizará.

## §20 Distribución del área de los movimientos en masa (SIMMA, 184 polígonos)

| Criterio | Resultado | Veredicto |
|---|---|---|
| M1: log-normal o inversa gamma con KS p > 0,05 | Log-normal: mediana 7.418 m², σ = 1,66, **KS p = 0,040**; inversa gamma peor por AIC (4.160 frente a 3.992) | **No cumple** (la log-normal se rechaza al 5 %) |
| M2: cola con ley de potencia, α entre 1,5 y 3,5 y KS p > 0,05 | xmin = 18.988 m², **α = 2,31**, KS p = 0,32 (60 polígonos en la cola) | **Cumple** |

La muestra de 209 polígonos (184 con área válida) no es probabilística y el inventario no tiene volumen ni fecha: **no sirve para dimensionar obras de contención**.

## §23 Hipótesis H1-H5, con corrección de Holm (α = 0,05) sobre H1, H2, H3, H4a y H4b

| Hipótesis | Resultado | p ajustado | Veredicto |
|---|---|---:|---|
| **H3** susceptibilidad con variables en logaritmo | ΔAUC +0,0153 (IC +0,0055; +0,0288) | 0,004 | **Confirmada** (con la salvedad de que la candidata cambia dos cosas a la vez; el control lineal sin curvatura da AUC 0,774 frente a 0,775 de la base, así que la ganancia viene de los logaritmos) |
| **H4a** GEV con ONI, significancia de campo | 29,2 % de las estaciones con efecto frente al 5 % esperado | 0,003 | **Confirmada** |
| **H4b** GEV con ONI, predictiva | La candidata gana en el 43,1 % de las estaciones | 0,004 | **No confirmada**: significativo, pero en contra (peor que el azar) |
| **H2** umbral E–D con pendiente y ONI | ΔTSS −0,031 (IC −0,036; −0,026) | 0,005 | **No confirmada**: significativamente **peor** que la curva global |
| **H1** umbral normalizado por la lluvia anual | ΔTSS −0,008 (IC −0,027; +0,012) | 0,50 | No significativo |
| **H5** forma ξ fija regional | Razón de ancho del IC 0,57; Δ log-verosimilitud no definido | — (regla) | No mejora |

**Una corrección de herramienta.** `consolidar_corrida.py` marcaba H2 y H4b como «significativo» porque los p-valores son bilaterales y la diferencia es significativa **en contra**. Un lector rápido habría concluido que se confirmaron. Ahora el consolidador muestra la dirección: «significativo y la candidata MEJORA» o «significativo pero la candidata es PEOR».

## Qué se concluye
- Se confirma que el logaritmo mejora la susceptibilidad (H3) y que hay efecto de ENSO dentro de la muestra de crecientes (H4a).
- **No** se confirma que ENSO o el terreno mejoren la predicción (H2, H4b), ni la normalización por lluvia anual (H1), ni la forma regional fija (H5). Es coherente con los demás resultados negativos del proyecto: lo simple alcanza.
