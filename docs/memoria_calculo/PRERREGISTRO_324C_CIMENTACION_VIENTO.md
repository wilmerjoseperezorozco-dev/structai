# Prerregistro #324-C: cimentación de los edificios que se redimensionan por viento

Fijado el 2026-11-26, **antes** de correr. Solo hubo una prueba de humo sobre el edificio 544, que está fuera de la población.

- **Hipótesis:** H1–H4 son de Wilmer y se registran como las propuso, con su formulación operativa. Al lado van mis contrapredicciones, para que ambas puedan fallar.
- **Código:** `packages/orquestador/src/cimentacion_edificio_3d.py`, con 4 pruebas a mano, y `scripts/memorias_sinteticas/viento_324c.py`.

## Variables que #324 no medía

1. **La cimentación.** El sobrecosto de #324 era solo de vigas y columnas.
2. **El suelo.** El corpus no tiene estudio de suelos, así que q_adm se recorre como **estrato declarado**:

| Estrato | q_adm |
|---|---|
| blando | 100 kPa |
| medio (**primario**) | 200 kPa |
| firme | 400 kPa |

## Método (herramienta de medición, no de diseño de cimentaciones)

- **Población:** los 11 edificios que fallaban con W36D en #324 (grupo falla).
- **Dos diseños por edificio:**
  - con las secciones óptimas sin viento, y cimentación sin W;
  - con las secciones óptimas con W36D (casos 1–4), y cimentación con W.
- **Zapata aislada cuadrada** por columna (motor-concreto, troncopiramidal), diseñada para todas las combinaciones:
  - servicio (B.2.3): D+L, D, D+W, D+0,75L+0,75W, 0,6D+W, D+0,7E, D+0,75L+0,525E, 0,6D+0,7E;
  - últimas (B.2.4), emparejadas con la misma acción lateral;
  - E con 100 % + 30 % (A.3.6.3).
- **Criterios del motor:**
  - q_máx ≤ q_adm;
  - **sin despegue en servicio** (q_mín ≥ 0, resultante dentro del núcleo central);
  - flexión, cortante y punzonamiento.
- **Qué gobierna cada zapata:**
  - *excentricidad*, si la L mínima sin despegue supera a la L mínima por capacidad portante y define el tamaño;
  - *portante*, si la define q_adm;
  - *estructural*, en otro caso.
  - Además se registra la *tracción neta*: alguna combinación de servicio con P < 0.
- **Costo** de la cimentación: concreto, acero y encofrado de las zapatas, con los mismos precios que la superestructura. Sin excavación.
- **Se marca y no se diseña:**
  - la zapata que no cabe entre columnas vecinas (L > luz − 0,30 m), que pediría zapata combinada, losa o pilotes;
  - el pedestal;
  - Ω0.

## Hipótesis, predicciones y contrapredicciones

| Id | Hipótesis de Wilmer | Operativa | Predicción de Wilmer | Contrapredicción de Claude |
|---|---|---|---|---|
| **H1** | El sobrecosto mediano sube al incluir la cimentación | Δpp = sobrecosto(superestructura + cimentación) − sobrecosto(superestructura), en puntos porcentuales, mediana de los 11 | **Δpp entre +3 y +7** (q = 200) | Δpp ≤ +1 (la zapata la define la carga de gravedad; el costo de la cimentación diluye el sobrecosto) |
| **H2** | Con viento, la cimentación la gobierna la excentricidad o el levantamiento, no la capacidad portante | Edificio "gobernado" si ≥ 50 % de sus zapatas las gobierna la excentricidad o si hay tracción neta | **≥ 7/11** (q = 200) | ≤ 3/11 con q = 100 y 200; puede subir con q = 400, porque zapatas más pequeñas hacen más relevante la excentricidad |
| **H3** | Los resueltos con viga peraltada (1290, 1729, 1762) tienen mayores luces o más esbeltez global | Mediana de la luz máxima y de H/B_mín de los 3 frente a los otros 8 | **mayor en las dos** | sin predicción. Exploratoria: n = 3, sin IC |
| **H4** | La reducción de sección arriba compensa parte del concreto que se agrega abajo | Compensación = −ΔV_sup/ΔV_inf de las columnas, en edificios con ΔV_inf > 0 | **mediana entre 15 y 30 %** | sin predicción |

## Notas críticas, escritas antes de ver los resultados

- **H1:** "3–7 % adicional" se lee como **puntos porcentuales** sobre el +8,6 % de #324. La lectura alternativa, un sobrecosto relativo de la cimentación, se reporta pero no decide.
- **H2:** el criterio del motor, sin despegue en servicio, es **estricto**. Otros criterios permiten despegue parcial con área efectiva, así que este favorece a H2. Se declara como límite.
- **H3:** el mecanismo propuesto ("rigidizar el nudo controla la deriva") **se pone a prueba**. En #324 la falla era flexocompresión biaxial de columnas, no deriva, y la deriva por viento no tiene límite en la NSR-10. Se reporta el uso de la deriva sísmica de cada diseño: si la deriva fuera el mecanismo, los 3 de viga deberían estar cerca de 1.
- **H4:** el optimizador divide en **mitades**, no en tercios. Se mide por mitades. Las secciones ya son públicas (RESULTADOS_324), así que **H4 es descriptiva**, no una prueba a ciegas.

## Reglas

- Los criterios no cambian después de ver los resultados.
- Los errores y las zapatas sin solución se reportan por id.
- Una zapata que no cabe se cuenta igual en el costo, como aproximación de zapata aislada. Su número se reporta por estrato.
- Nada de esto diseña cimentaciones reales: el estudio de suelos y la firma del ingeniero son insustituibles.
