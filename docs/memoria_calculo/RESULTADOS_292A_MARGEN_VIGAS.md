# Resultados #292-A: margen u_máx = 0,90 solo en vigas, zona sísmica baja

Corrida del 2026-11-21 contra el [prerregistro](PRERREGISTRO_292A_MARGEN_VIGAS.md). Datos: `data/memorias_sinteticas/f3b_292a/` (`resultados_292a.json`, `brazos.csv`). Script: `scripts/memorias_sinteticas/reserva_292.py --experimento A`.

**Recordatorio del sesgo declarado:** la variante se eligió después de ver #292 con el mismo corpus. No es una confirmación ciega.

## Calidad

- 358 de 358 pares evaluados sin falla.
- Control reutilizado de #292: los 5 controles rehechos reproducen β **idéntico**.
- Q2 (elementos imprecisos): 0,68 % (≤ 1 %).

## Hipótesis

| Id | Resultado | IC95 | Criterio | Veredicto |
|---|---|---|---|---|
| **H-292A-1** (primaria) | mediana Δβ = **+0,65** en los 39 edificios con β_control < 3,8 | [0,50; 1,14] | ≥ 0,3 con IC > 0 | **CUMPLE** |
| **H-292A-2** | p10 pasa de 3,76 a 4,06 (Δ = +0,30) | [0,12; 0,42] | IC > 0 | **CUMPLE** |
| **C-292A** | sobrecosto mediano 0 %, p90 0,2 %, máximo 3,3 % | — | mediana ≤ 3 %, p90 ≤ 6 % | **CUMPLE** |
| **R-292A** | 0 de 358 dejan de cumplir | — | 0 | **CUMPLE** |

**Descriptivo:**
- El 87 % de los edificios conserva β igual: el margen no actúa donde la viga ya tiene reserva.
- El 92 % de los edificios débiles sí cambia.
- La fracción de la variante «alta» con β < 3,8 apenas baja (70,7 % → 69,8 %). Esa variante sigue limitada por las columnas, que este brazo no toca a propósito.

## Comparación con #292 (margen en vigas y columnas)

| | Vigas y columnas (#292) | Solo vigas (A) |
|---|---|---|
| Δβ débiles | +0,62 | +0,65 |
| Diseños que dejan de cumplir | 15 (columnas del piso 1, N 8–12) | 0 |
| Decisión | NO ADOPTAR | **ADOPTAR** |

## Decisión (regla prerregistrada)

**Se adopta por defecto en zona baja (Aa y Av ≤ 0,10): margen 0,90 bajo gravedad solo en vigas.**

- `ProyectoEdificio3D.u_max_gravedad` es `None` por defecto y se resuelve con `u_max_recomendado` (0,90 en zona baja, 1,0 en el resto). `margen_en` es `"vigas"` por defecto.
- Pasar `u_max_gravedad=1.0` restituye el diseño al límite estricto de la NSR-10.
- **Es un criterio StructAI, no un requisito de la NSR-10.** Lo dice la memoria de cálculo.
- **Los resultados históricos (F1, F3, F3b, #292) se corrieron con el valor anterior (sin margen)** y no se recalculan. Los scripts de #292 fijan `u_max` y `margen_en` explícitos.
- Un margen no aprueba un diseño ni reemplaza la firma del ingeniero (#18).

## Lo que no cubre

- **Succión de viento en la cubierta (B.6, 0,9D + 1,0W):** invierte el momento y exige refuerzo en la otra cara y anclajes. Sigue en `NO_VERIFICA` y es un ítem propio de #292.
- **Columnas de la variante alta en zona baja** (β mínimo 2,44 en F3b): requieren un estudio propio, no un margen uniforme.
- **Validación física:** la sensibilidad real se mide con vibración ambiental (#276 P1), prioridad del usuario.
