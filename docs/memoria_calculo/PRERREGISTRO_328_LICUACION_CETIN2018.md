# Prerregistro #328, fase 1: motor-licuacion frente a 210 casos SPT reales (Cetin et al. 2018)

Fijado el 2026-11-24, **antes** de correr. Código: `packages/motor-licuacion/validacion/medir_cetin2018.py` (rama `feat/licuacion-medicion-328`). Las fórmulas de Boulanger e Idriss están verificadas a mano en `tests/test_validacion_bi2014.py`.

## Datos

- **Fuente:** Cetin, Seed, Kayen et al. (2018), *Dataset on SPT-based seismic soil liquefaction*, Data in Brief 20, DOI 10.1016/j.dib.2018.08.043, licencia **CC BY**.
  - Archivo `mmc2.xls` de la editorial, sha256 `31b8a1fc…aa431000`, en `C:\Users\wilme\dev\descargas\cetin2018\`. No se versiona.
- **Lo que ya vi (estructura, no resultados):**
  - 210 casos: 113 con licuación, 95 sin licuación y 2 marginales ("No/Yes");
  - calidad de datos: A = 50, B = 158, C = 2;
  - 28 rótulos de sismo, de los cuales 56 casos son de Kobe 1995;
  - columnas: profundidad crítica, σv, σ'v, amax, Mw, (N1)60, FC, con sus desviaciones.
  - **No he calculado ningún factor de seguridad ni ninguna probabilidad.**
- **Análisis principal:** casos A y B con observación Sí/No (se excluyen los 2 marginales y los de clase C). La corrida con todos los casos es de sensibilidad.
- **Agrupación por sismo:** año + nombre, sin magnitud. Esto une variantes de escritura y también eventos distintos del mismo año y nombre (Miyagiken-Oki 1978 M6,7 y M7,4; Nihonkai-Chubu 1983 y su réplica). Es conservador: deja menos grupos.

## Sesgo declarado (importante)

**Esto NO es una validación independiente.** Estos casos son la base con la que Cetin et al. ajustaron su modelo. Además se superponen en parte con las bases de Youd et al. (2001) y de Boulanger e Idriss (2014). Lo que se mide es **coherencia**:
- si el motor reproduce lo observado en la compilación de referencia;
- dónde se aparta de ella.

El modelo de Cetin (2018) **no** es un brazo, porque estaría evaluado con sus propios datos de ajuste. La validación independiente queda para NGL (cuando DesignSafe sea accesible) y para el inventario colombiano (#329).

**Entradas comunes:** todos los brazos usan el (N1)60 del archivo (correcciones de Cetin). Así se compara la relación de disparo, no el procesamiento del SPT.

## Brazos

| Brazo | Qué es |
|---|---|
| **M0** | `motor-licuacion` **tal cual**: Youd et al. 2001 **sin Kσ**, CRR de Rauch, MSF de Idriss, finos de Idriss y Seed. FS < 1 → predice licuación. Si (N1)60cs ≥ 30, FS = ∞. Si el motor rechaza la entrada (por ejemplo z > 30 m), se reporta como error |
| **M1** | Boulanger e Idriss (2014) determinista: rd(z, M), MSF(N), Kσ, ΔN por finos, CRR7.5,1 |
| **M1p** | Boulanger e Idriss (2014) probabilístico: σ_lnR = 0,13 |
| **M3** | Logística sobre ((N1)60cs, ln CSR7.5,1) de M1, dejando un sismo fuera. Penalización L2 = 10⁻³ |

## Métricas y predicciones

IC95 con bootstrap **por sismo** (2.000 remuestreos, semilla 3280).

| Id | Métrica | Predicción |
|---|---|---|
| **L1** (primaria, seguridad) | Sensibilidad de M0 (licuados con FS < 1) | ≥ 0,85, y la tasa de no detectados con IC95 superior ≤ 0,20 |
| L2 | Especificidad de M0 | Menor que su sensibilidad (curva conservadora, PL ≈ 15 %) |
| **L3** | M1 − M0 en exactitud balanceada | Dentro de ±0,05, con IC95 que **incluye** 0 (sin ganador claro) |
| L4 | Calibración de M1p (observado frente a predicho por tramos; Brier, log-loss) | Descriptiva |
| **L5** | log-loss de M3 − M1p | IC95 que **incluye** 0. Con 22 sismos, un modelo aprendido no le gana al publicado |
| L6 | Estratos: FC (≤ 5, 5–35, ≥ 35); (N1)60cs (< 15, 15–30, ≥ 30); z > 12 m; σ'v > 150 kPa; Mw < 7; clase A | Descriptiva. Espero que M0 se aparte más donde Kσ importa (σ'v > 150 kPa) y en FC ≥ 35 |

## Regla de decisión sobre el motor

- **El motor queda como está**, con sus límites documentados en la memoria, si se cumplen las dos:
  - L1 se cumple;
  - M1 no domina a M0. "Dominar" es: sensibilidad y especificidad no peores, y al menos una mejor con IC95 que no cruza 0.
- **En otro caso se abre una v2 del motor** (Kσ, B&I 2014 o la corrección que indique el diagnóstico). Esa v2 se valida con **datos distintos**: NGL o #329, nunca con estos 210 casos.
- Ningún brazo aprendido reemplaza el FS determinista.

## Calidad

- Los errores de M0 se reportan por id y no se reemplazan.
- Las fórmulas de M1/M1p se transcribieron de la publicación y se verificaron a mano en 4 pruebas. No hay un ejemplo independiente resuelto: es **verificación**.
