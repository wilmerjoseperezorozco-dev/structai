# Protocolo E1: ¿la pendiente del cauce principal mejora la estimación regional de caudales máximos? (preregistrado 2026-11-08, antes de calcular ninguna pendiente de cauce)

Contexto: [`docs/MARCO_PENDIENTE_FUERTE_Y_RESOLUCION_0330.md`](../../docs/MARCO_PENDIENTE_FUERTE_Y_RESOLUCION_0330.md). Parte de la Etapa A (`RESULTADOS_REGIONALIZACION_CAUDALES.md`), cuyo modelo M2 usa la pendiente **media de la cuenca**.

## Pregunta
Con las mismas 257 cuencas y el mismo caudal objetivo de la Etapa A, ¿sustituir o complementar la pendiente media de cuenca por la **pendiente del cauce principal** reduce el error de predicción en estaciones no vistas, y en particular en cuencas de pendiente fuerte?

## Insumos (sin descargas nuevas)
- Las 257 cuencas de `cuencas_estaciones.csv`, variante `r1500`, con el DEM de ~90 m ya en `scripts/satelite/_cache/dem90_<depto>.tif` y la misma delineación que la Etapa A (pysheds, D8).
- Caudal objetivo: los mismos Q_T (GEV sobre máximos anuales del IDEAM) de la Etapa A, T = 2, 5, 10, 25, 50; **T = 10 es el resultado primario**, fijado como en la Etapa A.

## Variables nuevas (definidas ahora)
- **L**: longitud (km) de la ruta de flujo más larga aguas arriba del punto de aforo.
- **S_cauce**: pendiente equivalente de Taylor-Schwarz del cauce principal, `S = (Σ L_i / Σ (L_i / √S_i))²` con tramos de la ruta (m/m).
- **S_10-85**: (cota al 85 % − cota al 10 % de L) / (0,75 L).
- Se descartan los valores con S ≤ 0 y se aplica un piso de 0,0005 m/m, declarado y contado. Con DEM de 90 m el relieve fino de cauce no se resuelve; **las pendientes de cauce serán sesgadas a la baja en tramos cortos y empinados**. Es una limitación del insumo, no se corrige.

## Modelos (los de la Etapa A más dos nuevos; mismas reglas de validación)
- **M2**: ln Q = a + b ln A + c ln P + d ln S_cuenca (referencia).
- **M2c**: ln Q = a + b ln A + c ln P + d ln S_cauce (sustituye).
- **M2b**: ln Q = a + b ln A + c ln P + d ln S_cuenca + e ln S_cauce (añade).
- Mismos P y A que en la Etapa A. La variante de pendiente de cauce primaria es **S_cauce de Taylor-Schwarz**; S_10-85 se reporta solo como sensibilidad.

## Validación (idéntica a la Etapa A)
Validación espacial a ciegas con zona de exclusión de 50 km y mismo cauce; error = |ln(Q̂/Q)|; diferencias pareadas con IC95 % por bootstrap de bloques de 1° (reutilizando `regionalizacion_validacion.py` sin modificar su lógica).

## Criterios de decisión (fijados ahora)
- **Primario (T = 10, 257 cuencas):** M2b mejora a M2 si el IC95 % de la diferencia pareada media de |ln(Q̂/Q)| (M2b − M2) está **íntegramente por debajo de 0**. Se hacen dos comparaciones (M2b y M2c frente a M2), así que el nivel se corrige con Bonferroni: IC al 97,5 %.
- **Secundarios (descriptivos, no cambian la decisión primaria):** (a) mismo contraste en cuencas con pendiente media de cuenca > 30 % (112) y ≤ 30 % (145); (b) región Caribe; (c) T = 2, 5, 25, 50; (d) signo y valor del coeficiente de ln S_cauce, y su correlación con ln S_cuenca; (e) factor de error típico exp(mediana |ln(Q̂/Q)|) de cada modelo.
- **Si el IC incluye 0**, se publica «sin evidencia de mejora con esta muestra y este DEM», sin declarar equivalencia.
- **Alerta de calidad:** si más del 10 % de las cuencas no producen una ruta de flujo coherente (longitud menor que 0,5 √A, o área acumulada que difiera más de 15 % de la de la Etapa A), se reporta y el análisis primario se hace con las que sí, indicando el cambio de muestra.

## Qué NO se concluye
Nada sobre cuencas de menos de 5 km² (no hay en la muestra), ni sobre el dominio de la Resolución 0330 (< 80 ha); ni que una pendiente de cauce de 90 m sea la «verdadera»; ni causalidad. Un resultado positivo no sustituye la lluvia de diseño: solo dice si la geometría del cauce aporta información.

## Limitaciones declaradas de antemano
Muestra de una sola red (IDEAM) con posible autocorrelación espacial remanente; DEM de 90 m; el Q objetivo es un cuantil ajustado, no un valor observado; 112 de 257 cuencas con pendiente media > 30 % es una muestra, no una cobertura del país.

## Se publica pase lo que pase
Tabla de variables de cauce por cuenca, coeficientes, errores de los tres modelos y todos los contrastes, incluido el caso en que no mejoren.
