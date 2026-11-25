# Resultados #328, fase 1: motor-licuacion frente a 210 casos SPT reales (Cetin et al. 2018)

- **Prerregistro:** [`PRERREGISTRO_328_LICUACION_CETIN2018.md`](PRERREGISTRO_328_LICUACION_CETIN2018.md), publicado en [#328](https://github.com/wilmerjoseperezorozco-dev/structai/issues/328#issuecomment-7149588714) antes de correr.
- **Corrida:** sin cambios en el script.
- **Muestra:** 206 casos principales (A y B, Sí/No), de 20 grupos de sismo.
- **Excluidos, como estaba declarado:** 27 y 29 (clase C), 12 y 28 (marginales).
- **Datos:** Cetin, Seed, Kayen et al. (2018), *Data in Brief* 20, DOI 10.1016/j.dib.2018.08.043, CC BY.
- **Recordatorio:** esto mide **coherencia**, no es validación independiente. Los casos se superponen con las bases de calibración de los métodos.

## Decisión: L1 NO se cumple → se abre una v2 del motor, a validar con datos distintos

| Id | Resultado | Predicción | Veredicto |
|---|---|---|---|
| **L1** (seguridad) | Sensibilidad de M0 = **0,847** (94/111), IC95 [0,73; 0,92]. No detectados: 15,3 %, IC95 superior **27 %** | ≥ 0,85 e IC sup. de no detectados ≤ 20 % | **NO CUMPLE** |
| L2 | Especificidad de M0 = 0,830 (78/94), IC95 [0,75; 0,89], menor que la sensibilidad | menor que la sensibilidad | se cumple, pero por muy poco y sin significancia |
| **L3** | M1 − M0 en exactitud balanceada = −0,012, IC95 [−0,034; +0,024] | ±0,05 e IC que incluye 0 | **CONFIRMADA**: B&I 2014 no le gana al motor |
| **L5** | log-loss M3 − M1p = −0,117, IC95 [−0,270; +0,003] | IC que incluye 0 | **CONFIRMADA por la regla**, pero al límite (ver calibración) |

**Error de datos detectado:** el caso 165 tiene σv < σ'v en el archivo. El motor lo rechaza, como debe.

## Dónde falla el motor (L6, descriptivo)

| Estrato | n | M0 sens. / esp. | M1 sens. / esp. | Lectura |
|---|---|---|---|---|
| **FC ≥ 35 %** | 25 | **0,56** / 0,89 | 0,69 / 0,67 | **El punto débil:** M0 no detectó 7 de 16 licuaciones. El motor ya marca estos suelos como "en borde" de su dominio, y ahora está medido cuánto falla ahí |
| 5 < FC < 35 | 88 | 0,89 / 0,86 | 0,95 / 0,77 | bien |
| FC ≤ 5 | 93 | 0,90 / 0,78 | 0,85 / 0,83 | bien |
| 15 ≤ (N1)60cs < 30 | 77 | **0,73** / 0,74 | 0,82 / 0,72 | zona de transición: 10 no detectados |
| **Mw < 7** | 128 | **0,77** / 0,87 | 0,86 / 0,79 | el MSF de Idriss (NCEER) del motor parece generoso con sismos moderados |
| clase A (mejor calidad) | 50 | 0,82 / 0,88 | 0,82 / 0,76 | |
| σ'v > 150 kPa / z > 12 m | 3 / 2 | — | — | **No se puede evaluar**: la falta de Kσ en M0 no se prueba con esta base |

## Calibración de la versión probabilística de B&I (M1p)

| Probabilidad predicha | n | Media predicha | Fracción que licuó |
|---|---|---|---|
| 0–0,1 | 86 | 0,01 | **0,14** |
| 0,1–0,3 | 12 | 0,22 | **0,75** |
| 0,3–0,5 | 15 | 0,39 | 0,33 |
| 0,9–1,0 | 71 | 0,99 | 0,94 |

En esta base, **M1p subestima la probabilidad en el tramo bajo**: 12 de los 86 casos a los que asigna menos del 1 % sí licuaron. Ese es el lado peligroso. La logística aprendida (M3, dejando un sismo fuera) quedó mejor calibrada, pero su ventaja no es significativa (el IC toca 0). Además se entrenó con casos de la misma compilación, así que no se adopta.

## Consecuencias

1. **v2 del motor (nuevo trabajo):**
   - revisar el MSF para Mw < 7;
   - tratar los suelos con FC ≥ 35 %: hoy solo los marca "en borde". Habría que advertir explícitamente que la tasa medida de no detección es del 44 %, o exigir una evaluación de susceptibilidad aparte (criterios de plasticidad);
   - incorporar Kσ.
   - **Se valida con datos distintos:** NGL (cuando DesignSafe sea accesible) o el inventario colombiano (#329). Nunca con estos 210 casos.
2. **Mientras tanto,** la memoria del motor debe declarar los límites medidos: sensibilidad de 0,85 en general y de 0,56 con FC ≥ 35 %, en la compilación de Cetin 2018.
3. **Cambiar a B&I 2014 no es la solución** por sí sola (L3): mejora un poco la sensibilidad y empeora la especificidad.

## Limitaciones

- No es una validación independiente: hay superposición de casos con las bases de calibración.
- 20 grupos de sismo, con Kobe como el 27 % de los casos.
- El (N1)60 es común a todos los brazos (procesamiento de Cetin). No se evaluó el procesamiento del SPT del motor.
- Casi sin casos profundos o con confinamiento alto.
- Las fórmulas de B&I solo se verificaron a mano.
