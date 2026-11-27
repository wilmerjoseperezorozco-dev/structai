# Prerregistro #292: ¿un margen de utilización bajo gravedad u_máx = 0,90 en zona sísmica baja sube la confiabilidad a un costo aceptable?

Fijado el 2026-11-20, **antes** de diseñar ningún edificio con u_máx < 1 y de calcular su β.

## Lo que ya se sabe (declarado)

- **De la F3b:** la zona baja es la menos confiable.
  - Central: mediana β 5,19, percentil 10 3,66 y 13 % con β < 3,8.
  - Alta: 71 % con β < 3,8.
- **Elemento crítico:** la viga de cubierta.
- **Variable dominante:** θS.
- **Con el código nuevo de #292** (deflexiones C.9.5 y carga viva alternada C.8.11.2), los 1.348 diseños siguen cumpliendo y 17 cambian de refuerzo.
- **Expectativa a priori** (orden de magnitud, no criterio): Δβ ≈ ln(1/0,9)/σ_ln ≈ 0,7 donde la gravedad gobierna y el refuerzo no está en la cuantía mínima.

## Diseño del experimento

- **Población:** los 358 edificios de zona baja (Aa = Av ≤ 0,10) con solución del corpus F1, todos.
- **Brazos pareados, con el mismo código de este PR:**
  - **Control:** u_máx = 1,0.
  - **Tratamiento:** u_máx = 0,90.
  - Las secciones son las del corpus en ambos; solo cambia el refuerzo.
- **Confiabilidad:** el método F3b sin cambios (FORM + muestreo por importancia, tres variantes, semilla 2753), con su puerta Q2 (≤ 1 % de elementos imprecisos).
- **Lo que el modelo de β no incluye:** la carga viva alternada (usa L completa, igual que la F3b). Se declara.
- **Costo:** `costo_cop` de las cantidades de vigas y columnas (motor-concreto.Economia).

## Hipótesis y regla de decisión

IC95 bootstrap **pareado** por edificio, con semilla 2753 y 2.000 réplicas.

| Id | Hipótesis | Criterio de «CONFIRMADA» |
|---|---|---|
| **H-292a** | El margen sube la cola baja de β (variante central) | percentil 10 (tratamiento) − percentil 10 (control) ≥ 0,3, con IC95 > 0 |
| **H-292b** | El margen reduce la fracción bajo la referencia en la variante desfavorable | fracción con β < 3,8 en «alta»: control − tratamiento ≥ 0,10, con IC95 > 0 |
| **C-292** (costo) | El sobrecosto es aceptable | mediana del sobrecosto ≤ 3 % y percentil 90 ≤ 6 % |

**Regla de decisión, fijada aquí:**
- **Adoptar** `u_max_recomendado` como valor por defecto en zona baja si H-292a está CONFIRMADA, C-292 cumple y **ningún** diseño deja de cumplir con u_máx = 0,90.
- **Si un diseño deja de cumplir,** se reporta cuántos y por qué (necesitarían sección mayor). La adopción queda **condicionada** a que el optimizador F1 pueda resolverlos.
- **H-292b** es secundaria: se reporta, pero no decide.

## Descriptivo
- Δβ por elemento crítico (cubierta frente a otros), por N y por perfil de suelo.
- Fracción de edificios en los que el margen no cambió el refuerzo (la cuantía mínima o el sismo gobiernan).

## Limitaciones
- **El corpus es sintético** (rejilla F1). El β es del elemento, no del sistema. Las distribuciones no están calibradas; θS domina y es un supuesto.
- **Las secciones no se reoptimizan:** se mide el efecto del margen con las secciones F1 fijas. Con reoptimización, el costo podría ser menor.
- **Alcance:** nada de esto aprueba un diseño. El margen es un criterio de StructAI, **no un requisito de la NSR-10**, y todo diseño pasa por la F4 y por la firma de un ingeniero (#18).
