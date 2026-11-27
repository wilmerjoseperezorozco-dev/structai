# Prerregistro #292-A: margen u_máx = 0,90 bajo gravedad **solo en vigas**, zona sísmica baja

Fijado el 2026-11-21, **antes** de diseñar con esta variante.

## Sesgo declarado

- **Esta variante y su métrica primaria se eligieron después de ver el resultado de #292** ([`RESULTADOS_292_RESERVA_ZONA_BAJA.md`](RESULTADOS_292_RESERVA_ZONA_BAJA.md)), con el mismo corpus.
  - En ese experimento, el margen en vigas y columnas actuó en 33 de los 36 edificios más débiles (Δβ mediano +0,62).
  - También rompió 15 edificios altos en las columnas del piso 1.
- **Una confirmación aquí no es ciega** y pesa menos que una réplica independiente.
- **Justificación física** (Wilmer, 2026-11-21): la viga de cubierta no tiene demanda sísmica que la sobredimensione y es el elemento crítico en el 76 % de los edificios de zona baja.

## Diseño

- **Población:** los mismos 358 edificios de zona baja.
- **Brazos:**
  - **Control:** u_máx = 1,0. Se **reutiliza** el brazo control de #292 (mismo código, la opción nueva no cambia el valor por defecto). Control de calidad: se rehacen 5 controles y su β debe coincidir exactamente.
  - **Tratamiento A:** u_máx = 0,90 aplicado **solo** a las combinaciones de gravedad de las vigas. Las columnas se diseñan sin margen, pero sí con la capacidad de las vigas nuevas en columna fuerte–viga débil.
- **Confiabilidad:** el método F3b sin cambios, con la puerta Q2 (≤ 1 % de elementos imprecisos).

## Hipótesis y regla de decisión

IC95 bootstrap pareado, semilla 2753, 2.000 réplicas.

| Id | Hipótesis | Criterio |
|---|---|---|
| **H-292A-1** (primaria) | En los edificios con β_control < 3,8 (central), el margen en vigas sube β | mediana(Δβ) ≥ 0,3 con IC95 > 0 |
| **H-292A-2** | Cola de la población | percentil 10 (A) − percentil 10 (control) > 0 con IC95 > 0 (sin umbral de magnitud) |
| **C-292A** | Costo | mediana del sobrecosto ≤ 3 % y p90 ≤ 6 % |
| **R-292A** | Ningún diseño deja de cumplir | 0 de 358 |

**Decisión:** el valor por defecto en zona baja pasa a ser «margen 0,90 solo en vigas» si H-292A-1, C-292A y R-292A se cumplen. En cualquier otro caso queda como opción y no se activa por defecto.

## Fuera de alcance (declarado)

**La succión de viento en la cubierta** (Título B.6) hoy no se modela; está en `NO_VERIFICA`.
- El margen de gravedad **no** cubre el levantamiento: la succión invierte el momento y exige refuerzo en la otra cara, con la combinación 0,9D + 1,0W.
- Queda como ítem propio de #292, motivado por las ráfagas de más de 80 km/h que Wilmer reporta en el Caribe el 2024-09-16 (dato por confirmar con el IDEAM).
