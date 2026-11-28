# Resultados: generalización de la susceptibilidad a movimientos en masa entre departamentos (#349), 2026-11-28

Se ejecutó según [`PROTOCOLO_GENERALIZACION_DEPARTAMENTOS.md`](PROTOCOLO_GENERALIZACION_DEPARTAMENTOS.md), fijado en el
commit `a3579a8` antes de regenerar las muestras. Script: `generalizacion_departamentos.py`; cifras completas en
`generalizacion_departamentos.json`.

## Respuesta corta

- **El modelo generaliza a medias.** Siempre es mejor que el azar: los 23 departamentos tienen el límite inferior del
  IC por encima de 0,5. Pero solo **13 de 23 (57 %)** llegan a un AUC de 0,7, por debajo del 75 % fijado para decir
  que "generaliza en la mayoría".
- **El AUC agrupado (0,827) sobreestima el desempeño de un departamento típico (mediana 0,735) en 0,09 puntos.** Es la
  hipótesis A1 y **se confirma**.
- **La validación aleatoria infla el AUC en 0,06** (0,889 frente a 0,827). Es la B1 y **se confirma**.
- **El área de aplicabilidad no separa bien** los puntos en que el modelo acierta de aquellos en que falla. Es la C1 y
  **no se confirma**: Δ = +0,03 con un IC que cruza 0.
- **La Región Andina es la que peor generaliza** (mediana 0,657), y es la que más movimientos en masa tiene.

## Control de reproducibilidad

Las muestras se regeneraron con los mismos scripts y la misma semilla que H6:

| | Ahora | H6 |
|---|---:|---:|
| Muestras | 54 717 | 54 723 |
| Presencias | 9 129 | — |

| Modelo | AUC agrupado ahora | H6 | ¿Dentro de ±0,01? |
|---|---:|---:|---|
| B0 (logística) | 0,771 | 0,775 | Sí |
| G1 (boosting) | 0,827 | 0,830 | Sí |

**Se reproduce,** así que las comparaciones con H6 son válidas.

Hubo un detalle técnico en la descarga: el servicio del SIMMA no respondía al pedir todos los campos, así que se bajaron
solo `OBJECTID` y `TIPO`, que son los únicos que usa el muestreo. Llegaron los 9 177 puntos.

## A. Tabla por departamento

En cada fila, el modelo se entrena **sin** ese departamento. G1 es el modelo principal. Los IC95 % salen de un
bootstrap de puntos dentro del departamento y son optimistas por la autocorrelación.

| Depto. | Región | Presencias | AUC B0 | AUC G1 | IC95 % G1 | G1 con zona de 25 km | Fuera del área de aplicabilidad |
|---|---|---:|---:|---:|---|---:|---:|
| 25 Cundinamarca | Andina | 1 121 | 0,559 | **0,561** | 0,536–0,585 | 0,583 | 4,2 % |
| 41 Huila | Andina | 273 | 0,597 | 0,588 | 0,550–0,625 | 0,587 | 4,0 % |
| 63 Quindío | Andina | 85 | 0,563 | 0,593 | 0,504–0,683 | 0,535 | 0,6 % |
| 15 Boyacá | Andina | 1 059 | 0,627 | 0,607 | 0,583–0,631 | 0,593 | 6,0 % |
| 17 Caldas | Andina | 449 | 0,572 | 0,614 | 0,573–0,655 | 0,587 | 4,8 % |
| 27 Chocó | Pacífica | 70 | 0,707 | 0,643 | 0,582–0,706 | 0,632 | 9,8 % |
| 11 Bogotá | Andina | 25 | 0,424 | 0,657 | 0,534–0,770 | 0,701 | 7,3 % |
| 05 Antioquia | Andina | 727 | 0,603 | 0,669 | 0,646–0,691 | 0,668 | 5,3 % |
| 66 Risaralda | Andina | 117 | 0,455 | 0,674 | 0,606–0,739 | 0,623 | 2,8 % |
| 73 Tolima | Andina | 440 | 0,661 | 0,675 | 0,646–0,705 | 0,675 | 4,7 % |
| 68 Santander | Andina | 468 | 0,626 | 0,717 | 0,692–0,744 | 0,720 | 3,8 % |
| 76 Valle | Pacífica | 579 | 0,658 | 0,735 | 0,710–0,760 | 0,723 | 3,5 % |
| 19 Cauca | Pacífica | 1 007 | 0,576 | 0,751 | 0,731–0,770 | 0,752 | 3,4 % |
| 13 Bolívar | Caribe | 100 | 0,586 | 0,760 | 0,719–0,796 | 0,744 | 4,1 % |
| 54 Norte de Santander | Andina | 1 176 | 0,702 | 0,766 | 0,746–0,788 | 0,753 | 12,2 % |
| 20 Cesar | Caribe | 101 | 0,725 | 0,775 | 0,736–0,809 | 0,781 | 3,7 % |
| 86 Putumayo | Amazonia | 146 | 0,830 | 0,830 | 0,794–0,866 | 0,834 | 3,3 % |
| 08 Atlántico | Caribe | 68 | 0,585 | 0,834 | 0,777–0,881 | 0,837 | 5,0 % |
| 52 Nariño | Pacífica | 559 | 0,752 | 0,841 | 0,823–0,858 | 0,844 | 9,9 % |
| 18 Caquetá | Amazonia | 111 | 0,923 | 0,915 | 0,892–0,935 | 0,913 | 4,6 % |
| 50 Meta | Orinoquia | 128 | 0,964 | 0,923 | 0,908–0,936 | 0,913 | 2,6 % |
| 85 Casanare | Orinoquia | 241 | 0,930 | 0,927 | 0,909–0,943 | 0,925 | 1,2 % |
| 81 Arauca | Orinoquia | 41 | 0,915 | **0,937** | 0,917–0,955 | 0,938 | 2,2 % |

**Mediana de G1 por región:**

| Región | Mediana | Departamentos |
|---|---:|---:|
| Andina | 0,657 | 11 |
| Pacífica | 0,743 | 4 |
| Caribe | 0,775 | 3 |
| Amazonia | 0,873 | 2 |
| Orinoquia | 0,927 | 3 |

**Cómo leerlo:**

1. **El buen número sale de las llanuras.** En la Orinoquía y en el piedemonte amazónico el modelo solo tiene que
   separar "loma" de "llanura", y por eso llega a 0,92–0,94.
2. **En los Andes, donde está el problema, el modelo apenas supera al azar.**
   - Cundinamarca (0,56), Huila (0,59), Quindío (0,59), Boyacá (0,61) y Caldas (0,61) son los peores.
   - Cundinamarca y Boyacá tienen más de 1 000 presencias cada uno: no es falta de datos.
   - Dentro de una cordillera, casi todo el terreno es pendiente y geología "susceptible". Variables a 90 m y
     1:1 000 000 no alcanzan a distinguir qué ladera falla.
3. **La logística (B0) es aún más frágil.**
   - Solo 9 de 23 departamentos superan 0,7.
   - En Bogotá (0,42) y Risaralda (0,46) queda por debajo del azar: ordena al revés.
   - El boosting con cobertura y lluvia (G1) corrige parte. Recuerda la posible fuga causal de la cobertura de 2021
     (limitación 2).

**A1 (confirmatoria).**
- D_A = AUC agrupado − mediana de departamentos = 0,827 − 0,735 = **+0,092**.
- IC95 % [+0,027; +0,172]; p = 0,007, p Holm = 0,014.
- **Se cumple.**

**A2.**

| Umbral | Departamentos |
|---|---:|
| Límite inferior del IC > 0,5 | 23 de 23 |
| Límite inferior del IC > 0,7 | 12 de 23 |
| Punto estimado > 0,7 | 13 de 23 (57 %) |

Como 57 % < 75 %, **no** se puede decir que "generaliza en la mayoría".

## B. ¿Cuánto infla la validación aleatoria?

| Esquema | AUC B0 | AUC G1 |
|---|---:|---:|
| R: 5 pliegues aleatorios | 0,791 | **0,889** |
| D: un departamento fuera | 0,771 | **0,827** |
| D+zona: además, sin puntos a menos de 25 km | — | 0,824 |

**B1 (confirmatoria).**
- Δ_B = R − D = **+0,061**, con IC95 % [+0,042; +0,089]; p = 0,001, p Holm = 0,003.
- **Se cumple.** Validar con puntos al azar hace ver el modelo bastante mejor de lo que es fuera de lo que ya conoce.
  En la literatura, un 0,89 pasaría por "muy bueno". La cifra honesta es 0,83, y 0,74 para un departamento típico.

**B2 (descriptiva).**
- Quitar los puntos de entrenamiento a menos de 25 km del departamento reservado baja el AUC solo 0,003, con IC95 %
  [+0,000; +0,006].
- La vecindad con departamentos contiguos casi no infla el resultado. **La validación por departamento ya es casi tan
  estricta como puede ser con este diseño.**

## C. Área de aplicabilidad

- El 5,0 % de los puntos (1 784, con 599 presencias) quedó fuera del área.

**C1 (confirmatoria).**

| | AUC |
|---|---:|
| Dentro del área | 0,829 |
| Fuera del área | 0,798 |

- Δ_C = **+0,030**, con IC95 % [−0,032; +0,078]; p = 0,30.
- **No se cumple.**

**C2.**
- La correlación entre la fracción fuera del área y el AUC del departamento es ρ = −0,25 (p = 0,24): no hay relación
  clara.

**Lectura:**
- Los departamentos donde el modelo falla (Cundinamarca, Huila, Quindío) **no** se ven "raros" en el espacio de las
  variables: entre 0,6 % y 4 % fuera del área.
- El modelo no falla porque esas zonas sean distintas a lo que vio. Falla porque **con estas variables, una ladera que
  se desliza y una que no se ven iguales**.
- El área de aplicabilidad detecta extrapolación, pero no esta otra falta de información. Por eso no sirve como
  semáforo de confianza para este modelo.

## Holm (α = 0,05)

| Hipótesis | p | p Holm | Cumple |
|---|---:|---:|---|
| B1: la validación aleatoria infla el AUC | 0,001 | 0,003 | **Sí** |
| A1: el AUC agrupado sobreestima al departamento típico | 0,007 | 0,014 | **Sí** |
| C1: el área de aplicabilidad separa aciertos de fallas | 0,300 | 0,300 | No |

## Respuesta a la pregunta

Un modelo entrenado en unos departamentos **sí** predice en otros mejor que el azar. Pero **su desempeño depende
mucho de las características locales y de cómo se parten los datos**:

1. **Según cómo se valide, el mismo modelo da 0,89, 0,83 o 0,74.**
   - 0,89 con puntos al azar;
   - 0,83 dejando departamentos fuera y juntando todo;
   - 0,74 para el departamento típico.
2. **El desempeño cambia por región.** Va de 0,56 en Cundinamarca a 0,94 en Arauca. Lo bueno se concentra en las
   llanuras, donde el problema es fácil. En los Andes, donde ocurre la mayoría de los movimientos, queda entre 0,56 y
   0,77.
3. **Que una zona se parezca a los datos de entrenamiento no basta** para confiar en el modelo ahí. El límite no es la
   extrapolación: es la información que traen las variables.

**Para StructAI:**
- La susceptibilidad nacional sirve para **priorizar a escala regional**. No sirve para comparar laderas dentro de un
  departamento andino.
- Cualquier cifra de desempeño que se publique debe ser la de **departamento fuera, por región**, no la agrupada ni la
  aleatoria.
- Para mejorar en los Andes harían falta variables más finas: un DEM de 30 m, que es el #350; geología a 1:100 000; y
  lluvia detonante con fecha. Más filas no van a ayudar.

## Limitaciones

Son las mismas del preregistro:
- sesgo de acceso y de reporte del SIMMA;
- posible fuga causal de la cobertura de 2021;
- variables a escala nacional;
- no es un mapa de amenaza;
- IC por departamento optimistas por la autocorrelación.

## Fuentes y avisos

- **Inventario SIMMA y Mapa Geológico de Colombia V2023:** © Servicio Geológico Colombiano. Uso local de
  investigación, sin redistribuir capas (excepción decidida en #332). Las muestras no se versionan.
- **Copernicus DEM:** Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH
  2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
- **ESA WorldCover 2021:** © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed
  by ESA WorldCover consortium (CC BY 4.0).
- **Lluvia:** CHIRPS (Climate Hazards Center, UCSB).
- **Polígonos municipales:** ANH.
