# Preregistro: ¿generalizan los modelos de susceptibilidad a movimientos en masa entre departamentos? (2026-11-28)

Este documento se fija **antes** de regenerar las muestras y antes de ver cualquier cifra por departamento. Si algo
cambia, se agrega como enmienda fechada al final, sin borrar lo de arriba.

## Lo que ya se sabe (no se puede "des-ver")

Del experimento H6 (§24 de `PROTOCOLO_ANALISIS.md`, `resultados_corrida/h6_satelite_ml.txt`), con validación dejando
un departamento fuera:

| Medida | B0 | G1 |
|---|---:|---:|
| AUC agrupado | 0,775 | 0,830 |
| AUC Andina | 0,628 | 0,679 |
| AUC Orinoquía | 0,942 | 0,928 |

- **B0:** regresión logística con pendiente, curvatura, log de la distancia a falla y edad geológica.
- **G1:** gradiente boosting con las variables de B0, más la cobertura WorldCover 2021 y el log de la lluvia anual.

Hasta hoy no se ha visto **ninguna** cifra por departamento, ni la validación aleatoria, ni el área de aplicabilidad.

## Pregunta

¿Un modelo entrenado en unos departamentos discrimina bien dónde hay movimientos en masa en un departamento que no
vio? ¿Cuánto cambia la respuesta según cómo se parten los datos? ¿Se puede saber de antemano dónde el modelo no
debería opinar?

## Datos

Son los mismos de H6, regenerados con los mismos scripts y semillas: `muestrear_susceptibilidad.py` seguido de
`agregar_cobertura_worldcover.py`. Las muestras no se versionaron, así que hay que regenerarlas.

| Elemento | Detalle |
|---|---|
| Presencias | puntos SIMMA (SGC) dentro de municipios continentales |
| Fondo | 5 puntos al azar por presencia (semilla 20261107) |
| Problema | solo presencia: el AUC mide discriminación frente al fondo, no probabilidad de ocurrencia |
| Departamentos evaluables | los que tienen ≥ 20 presencias (en H6 fueron 23) |

**Control de reproducibilidad, antes de cualquier análisis nuevo:** el AUC agrupado dejando un departamento fuera
debe quedar a ±0,01 de H6 en B0 y en G1.
- Si no se cumple, los datos regenerados no son los de H6. Se informa y se sigue, pero las comparaciones con H6 se
  marcan como no comparables.
- Los servicios del IGAC/ANH y del SGC pueden haber cambiado desde el 2026-11-07.

## Modelos

Se usan B0 y G1 exactamente como en `hipotesis_h6_satelite_ml.py`, con los mismos hiperparámetros. No se ajusta nada
después de ver resultados.

## A. Tabla por departamento

- **Cálculo:** en cada departamento evaluable se mide el AUC del modelo entrenado sin ese departamento. Se hace para
  B0 y para G1.
- **IC95 %:** bootstrap estratificado de puntos dentro del departamento (2 000 réplicas).
  - Es optimista, porque los puntos vecinos están autocorrelacionados. Se declara y no se corrige.
- **Qué se informa por departamento:**
  - región natural;
  - número de presencias;
  - AUC B0 y AUC G1, con sus IC;
  - fracción de puntos fuera del área de aplicabilidad (ver C).
- **A1 (confirmatoria):** el AUC agrupado sobreestima el desempeño típico de un departamento.
  - Estadístico: D_A = AUC agrupado − mediana de los AUC por departamento, para G1.
  - IC95 % por bootstrap de departamentos (2 000 réplicas; en cada réplica se recalculan las dos cantidades).
  - Hipótesis: D_A > 0.
- **A2 (descriptiva, con umbral fijado):** cuántos departamentos tienen un límite inferior del IC de G1 por encima de
  0,5 (mejor que el azar) y cuántos por encima de 0,7 ("discriminación aceptable", la convención usual).
  - **Lectura fijada de antemano:** se dice que el modelo "generaliza en la mayoría" solo si al menos el 75 % de los
    departamentos supera 0,7 en el punto estimado.

## B. ¿Cuánto infla la validación aleatoria?

Sobre los mismos puntos de los departamentos evaluables, tres esquemas:

| Esquema | Cómo se parte |
|---|---|
| **R** | 5 pliegues aleatorios, estratificados por presencia (semilla fija) |
| **D** | un departamento fuera (el de A) |
| **D+zona** | un departamento fuera, y además se quitan del entrenamiento los puntos a menos de 25 km de algún punto del departamento reservado (distancias en EPSG:9377) |

- **B1 (confirmatoria):** Δ_B = AUC(R) − AUC(D) > 0, para G1.
  - IC95 % por bootstrap de departamentos sobre las predicciones fuera de pliegue (pareado: mismos puntos).
- **B2 (descriptiva):** AUC(D) − AUC(D+zona), para medir cuánto ayuda la vecindad con departamentos contiguos.

## C. Área de aplicabilidad (Meyer y Pebesma, 2021)

- **Espacio de variables:**
  - las numéricas se estandarizan con la media y la DE del entrenamiento;
  - las categóricas (edad y cobertura) van en one-hot, escaladas para que no coincidir sume 1 a la distancia al
    cuadrado;
  - cada variable se pondera por su importancia por permutación en G1. Esa importancia se calcula **dentro** del
    pliegue de entrenamiento, con un departamento interno reservado: el de más presencias entre los de entrenamiento.
- **Índice de disimilitud (DI):** distancia del punto al punto de entrenamiento más cercano, dividida por la distancia
  media entre puntos de entrenamiento (estimada con 2 000 pares al azar).
- **Umbral:**
  - para los puntos de entrenamiento, el DI se calcula frente a los puntos de entrenamiento de **otros**
    departamentos;
  - el umbral es el percentil 95 de ese DI;
  - un punto de prueba está **fuera** del área si su DI supera el umbral.
- **C1 (confirmatoria):** Δ_C = AUC de G1 dentro del área − AUC de G1 fuera del área > 0, juntando los departamentos
  reservados.
  - IC95 % por bootstrap de departamentos.
  - Solo se evalúa si fuera del área hay ≥ 200 puntos y ≥ 30 presencias. Si no, se informa "no evaluable".
- **C2 (descriptiva):** correlación de Spearman, entre departamentos, entre la fracción fuera del área y el AUC de G1.

## Corrección y criterios

- Holm con α = 0,05 sobre las tres confirmatorias: A1, B1 y C1.
- El valor p bootstrap es el mismo de H6 (`p_boot`).
- Se cumple una hipótesis si su p ajustado es < 0,05 y el signo es el previsto.

## Limitaciones declaradas

1. **Sesgo del inventario.** El SIMMA tiene sesgo de acceso y de reporte (`RESULTADOS_SESGO_REPORTE.md`). El modelo
   puede aprender "dónde se reporta".
2. **Posible fuga causal.** La cobertura es de 2021: un suelo desnudo puede ser efecto del movimiento. Por eso A se
   informa también con B0, que no tiene cobertura.
3. **Escala nacional.** La geología es 1:1 000 000, agrupada por edad. El DEM es de superficie a unos 90 m.
4. **No es un mapa de amenaza.** No tiene detonantes ni probabilidad temporal, y no sustituye estudios de campo.
5. **Validación aún optimista.** Dejar un departamento fuera sigue siendo optimista si los departamentos vecinos se
   parecen. D+zona lo mide en parte.
6. **Uso de datos del SGC.** Es el uso ya integrado, bajo la excepción decidida por Wilmer (#332): análisis local, con
   cita al SGC y sin redistribuir capas crudas. Las muestras regeneradas **no se versionan**.

## Salidas

- `generalizacion_departamentos.py`: el análisis completo.
- `generalizacion_departamentos.json`: todas las cifras.
- `RESULTADOS_GENERALIZACION_DEPARTAMENTOS.md`: el informe.
