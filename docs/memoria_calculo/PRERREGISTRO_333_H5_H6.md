# Prerregistro #333 (H5 y H6): costo real de la transición de cimentación

Fijado el 2026-11-26, **antes** de correr. Solo hubo pruebas de humo sobre el edificio 544, que está fuera de la población.

- **Hipótesis:** H5 y H6 son de Wilmer (#333). Al lado van mis contrapredicciones.
- **Código:**
  - `packages/orquestador/src/transicion_cimentacion_3d.py` (nuevo), con 6 pruebas a mano;
  - `scripts/memorias_sinteticas/viento_333h56.py`.
- **Población y diseños:** los 11 del grupo falla de #324, con sus secciones `sin_viento` y `W36D` (casos 1–4 de viento).

## Cambio de alcance respecto al cuerpo de #333, declarado antes de correr

1. **Escalera de transición:** zapata aislada cuadrada (#324-C) → **zapata rectangular** prismática (motor-concreto `zapata.verificar`) → **losa maciza rígida** bajo todo el edificio.
   - La rectangular entra por el hallazgo post hoc de H8: las zapatas que no caben son las de bahías alargadas.
   - La transición elegida es la **más barata que cumple y cabe**: rectangulares solo en las zapatas que no caben, o la losa completa.
2. **Pilotes y losa aligerada quedan fuera de esta versión.**
   - `motor-pilotes` calcula punta y fuste, pero necesita un perfil de estratos con SPT que el corpus no tiene, e inventarlo haría del costo una hipótesis pura.
   - Consecuencia: si ni la rectangular ni la losa cumplen, el edificio se marca *sin_solucion (requiere pilotes o losa compensada)* y **no entra en la mediana**. Se reporta.
   - El costo medido es entonces el de la transición más barata **sin pilotes**.
3. **Zapata combinada:** no se modela. Se declara.

## Método de la losa (herramienta de medición, no de diseño)

- **Presión de contacto:** losa rígida, con q = ΣP/A ± |M_y|/S_y ± |M_x|/S_x más el peso de la losa y del relleno.
  - M_y = ΣP·x′ − ΣMy y M_x = ΣP·y′ + ΣMx. Los signos se comprobaron con los casos sísmicos simétricos del 544.
  - Criterios en servicio: q_máx ≤ q_adm (**bruta**, sin compensación por excavación) y q_mín ≥ 0.
- **Voladizo** más allá de la cara de las columnas de borde: 0; 0,5 o 1,0 m (HIPÓTESIS: lo limitan los linderos).
- **Espesor:** de 300 a 2.500 mm. Se revisan:
  - punzonamiento C.11.11.2.1 en cada columna, con su P_u máxima, perímetro de 4, 3 o 2 lados según el voladizo y la presión media mínima (sin C.11.11.7);
  - cortante como viga por metro de ancho;
  - flexión por franja con m_u = q_u,máx·L²/10 (luz máxima de cada dirección), refuerzo uniforme en las dos caras y las dos direcciones, y ρ_mín en cada cara. Es una **cota superior del acero**.
- **Costo:** el primer h que cumple y los 4 siguientes; se toma el más barato, con los mismos precios de #324-C.

## Hipótesis, predicciones y contrapredicciones

| Id | Operativa | Predicción de Wilmer | Contrapredicción de Claude |
|---|---|---|---|
| **H5** | Con 200 kPa, en los edificios del diseño W36D con alguna zapata cuadrada que no cabe, la mediana de C_cim,transición / C_super. Sensibilidad: sin_viento | **entre 25 % y 35 %** (en el límite, se cumple) | **< 25 %**: la rectangular resuelve casi todos los casos y la razón queda cerca del 16 % de #324-C |
| **H6** | Con 100 kPa y losa rígida en los dos diseños: Δ = 100·(C_losa,W − C_losa,sv) / (C_super,sv + C_losa,sv), mediana de los edificios donde la losa es factible en ambos | **Δ < +0,5 pp** | La losa **no es factible por capacidad portante en la mayoría** (≥ 8/11): con 9–12 pisos la presión bruta supera 100 kPa sin compensación. Donde sí lo es, Δ < +0,5 pp se cumple |

## Reglas de veredicto

- **H5:** *se cumple* si la mediana está en [25 %, 35 %]; si no, *refutada*. Si ningún edificio tiene solución sin pilotes, *inconclusa*.
- **H6:** *se cumple* si la mediana de Δ es < 0,5 pp; si no, *refutada*. Si ninguna losa es factible, *inconclusa*. Con n < 3 factibles se reporta como exploratoria.
- Los criterios no cambian después de ver los resultados.
- Errores y casos sin solución se reportan por id.
- Nada de esto diseña cimentaciones reales. El estudio de suelos (Título H), la interacción suelo-estructura y la firma del ingeniero son insustituibles.
