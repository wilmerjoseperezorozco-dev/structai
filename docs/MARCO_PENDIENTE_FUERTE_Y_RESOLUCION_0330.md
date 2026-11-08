# Marco de trabajo: caudales de diseño en pendiente fuerte y su cruce con la Resolución 0330 de 2017

Estado: documento de diseño y de brechas, 2026-11-08. No contiene resultados nuevos de modelos; cada estudio que propone se preregistra aparte antes de calcularse. Lo que aquí se afirma sobre la norma se verificó en el texto del repositorio (`packages/construdata/normativa_raw/res0330/res0330.txt`) y sobre nuestros datos, en los archivos citados.

Nota de nomenclatura: la norma es la **Resolución 0330 de 2017** del Ministerio de Vivienda (Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico, RAS), no un decreto.

## 1. Por qué existe esta brecha
El piloto de literatura (`scripts/hidro/RESULTADOS_LITERATURA_CAUDALES.md`) mostró que las ecuaciones regionales publicadas piden dos insumos que no tenemos: **lluvia de diseño** (con duración atada al tiempo de concentración) y **pendiente del cauce principal**. Nuestro modelo regional (M2) usa la pendiente **media de la cuenca**, no la del cauce, y una lluvia **media anual**, no una lluvia de diseño.

## 2. Qué exige la Resolución 0330 (artículos verificados)
| Artículo | Exigencia (resumen) | Relación con pendiente fuerte |
|---|---|---|
| 135 | Caudal de aguas lluvias con modelos lluvia-escorrentía; **método racional solo si el área de drenaje es menor de 80 ha**; períodos de retorno mínimos en la Tabla 16 (la tabla solo está en el PDF original, no en nuestro texto); curvas IDF de la localidad, verificadas y con datos recientes, incluyendo variabilidad y cambio climático; análisis de cobertura al inicio y al final del período de diseño; **simulación con tiempos de concentración mínimos entre 3 y 10 minutos** y evaluar su incidencia | El tiempo de concentración en ladera empinada es corto, y la IDF a esa duración es justo lo que menos se mide |
| 142 | Velocidad máxima real en colector por gravedad: 5,0 m/s; **se permiten velocidades mayores en topografías con pendientes superiores al 30 %**, diámetros ≥ 600 mm o caudales > 500 L/s, con protecciones y disipación de energía | Es la excepción de pendiente fuerte; exige criterio, no una fórmula |
| 151 | Nuevos desarrollos: sistemas urbanos de drenaje sostenible que reduzcan **al menos 25 %** el caudal pico del hidrograma de creciente de diseño | Necesita un caudal pico de referencia bien estimado |
| 153 | Cámara de caída si la diferencia entre cotas batea supera 0,75 m; **estructuras de disipación si el desnivel supera 7,0 m** | Aparece sistemáticamente en ladera |
| 157 | Estructura de descarga y disipación que lleve el flujo a régimen subcrítico | Idem |

## 3. Hallazgos verificables al cruzar la norma con nuestro código (`packages/motor-aquai`)
Son discrepancias entre lo que el módulo declara y lo que dice el artículo; no he evaluado su efecto numérico.
1. **Límite del método racional.** `hidrologia.py` lo da por válido hasta ~1.000 ha y solo advierte por encima de ese valor; el Artículo 135 lo limita a **menos de 80 ha** (12,5 veces menos). El encabezado del módulo cita la Resolución 0330 como referencia.
2. **Tiempo de concentración mínimo.** El módulo fija un mínimo práctico de 5 min; el artículo pide simular entre 3 y 10 min y evaluar la incidencia. No hay análisis de sensibilidad.
3. **Curvas IDF.** Los coeficientes a/b/n están marcados en el propio código como de referencia, sin cita verificable. El artículo exige curvas de la localidad con datos recientes.
4. **Pendiente fuerte en colectores.** `manning.py` limita la velocidad a 5 m/s (concreto) y 3 m/s (PVC/HDPE) sin la excepción del Artículo 142 para pendientes > 30 %, y no contiene lógica de cámaras de caída (0,75 m) ni de disipación (7 m) de los Artículos 153 y 157. Para ladera empinada el módulo solo puede responder «no cumple».
5. **Falta la Tabla 16** (períodos de retorno mínimos) en el texto que indexamos; cualquier verificación automática de períodos de retorno exige primero transcribirla del PDF original.

## 4. Lo que no hemos medido (inventario verificado)
| Magnitud | Estado real | Evidencia |
|---|---|---|
| Pendiente y longitud del **cauce principal** de las cuencas aforadas | No calculadas; solo pendiente media de la cuenca | `scripts/hidro/cuencas_estaciones.csv` (columna `pend_media_pct`) |
| **Cuencas pequeñas**, el dominio del método racional | De 257 cuencas, la menor tiene 5,1 km² (510 ha, 6,4 veces el límite de 80 ha); solo 4 tienen menos de 10 km² y 16 menos de 50 km². **Ninguna cae dentro del dominio de la Resolución 0330** | `cuencas_estaciones.csv`, variante `r1500` |
| Cuencas de **pendiente fuerte** | Sí hay muestra: 112 de 257 (44 %) con pendiente media de cuenca > 30 %; mediana 27,3 % (DEM ~90 m, suaviza pendientes locales) | idem |
| **Lluvia de diseño por duración** | Solo CHIRPS diario y lluvia media anual; los pluviógrafos automáticos del IDEAM (10 min) cubren 2022-2024 en una muestra de 42 estaciones: sirven para razones entre duraciones, no para períodos de retorno largos | `RESULTADOS_SESGO_CHIRPS.md` |
| Sesgo de CHIRPS en extremos | Piloto: razón del percentil 99 de 0,90 [0,78; 1,05] sobre 35 estaciones; **Caribe** con un IC muy amplio [0,58; 4,50] | idem |
| **Tiempo de concentración observado** | No existe; no tenemos hidrogramas, solo máximos anuales | — |
| Coeficiente de escorrentía / número de curva por cobertura en ladera | No medido | — |
| Efecto de **flujos torrenciales y sedimento** en el caudal de diseño | No medido; es hipótesis | — |
| Colectores reales en ladera (velocidades, caídas) | No tenemos base de redes | — |

## 5. Marco propuesto (cinco módulos)
Cada módulo es independiente, con entradas y salidas definidas y una validación propia; ninguno se da por bueno sin su protocolo.
- **M1. Geomorfometría de cauce.** A partir del DEM ya en caché: longitud del cauce principal (ruta de flujo más larga), pendiente equivalente (Taylor-Schwarz) y pendiente entre el 10 % y el 85 % de la longitud, para las 257 cuencas. Salida: tabla de variables.
- **M2. Lluvia por duración.** Razones entre duraciones (por ejemplo 1 h / 24 h) estimadas con los pluviógrafos de 10 min, por región, con su incertidumbre; aplicables solo para trasladar máximos diarios largos a duraciones menores, con las advertencias del período corto.
- **M3. Incertidumbre del tiempo de concentración.** Dispersión entre fórmulas (Kirpich, Témez, Bransby-Williams, ya en el módulo) según pendiente, para cuantificar cuánto cambia el caudal de diseño con la fórmula elegida. Sin hidrogramas no se puede decir cuál fórmula es correcta; solo cuánto importa elegir.
- **M4. Ajuste del pico por pendiente.** Modelo que corrige el estimador regional con la pendiente del cauce, con validación espacial a ciegas, reportando intervalo y no solo valor puntual, y por estratos de pendiente.
- **M5. Verificador de la Resolución 0330.** Reglas deterministas (área < 80 ha para método racional; sensibilidad del Tc entre 3 y 10 min; velocidad 5 m/s con excepción documentada para pendiente > 30 %; cámaras de caída > 0,75 m; disipación > 7 m; reducción de pico ≥ 25 % con SUDS) que `motor-aquai` evalúe y reporte como «cumple / no cumple / requiere criterio del diseñador». Es lo más inmediato y el que más valor da a los usuarios, porque no necesita datos nuevos.

## 6. Estudios propuestos, en orden
| # | Estudio | Datos nuevos | Estado |
|---|---|---|---|
| E1 | Pendiente del cauce para 257 cuencas y si mejora M2 | Ninguno: DEM90 ya en caché | **Protocolo publicado** (`scripts/hidro/PROTOCOLO_PENDIENTE_CAUCE.md`); sin ejecutar |
| E2 | Auditoría de `motor-aquai` frente a la Resolución 0330 (puntos 1-4 de la sección 3) y su corrección con pruebas | Transcribir la Tabla 16 del PDF original | Propuesto; requiere decisión sobre qué cambiar en producción |
| E3 | Razones entre duraciones con pluviógrafos de 10 min | Re-descarga de series de 10 min (el caché guarda diarios) | Propuesto; descarga requiere tu permiso con tamaño |
| E4 | Dispersión del Tc entre fórmulas por pendiente | Depende de E1 | Propuesto |
| E5 | Datos de cuencas pequeñas para el dominio del método racional | Fuentes por verificar: la red de cuencas de cabecera de los Andes tropicales (Sci. Data, 10.1038/sdata.2018.80) y CAMELS-CL (10.5194/hess-22-5817-2018), ambas con texto abierto; **aún no leídas**, no sé si su clima y escala sirven para Colombia | Propuesto |

## 7. Qué no se afirma
- No se afirma que el módulo actual dé caudales incorrectos: se afirma que difiere del artículo en los puntos señalados; el efecto está por medir.
- No se afirma que la pendiente del cauce mejore la estimación; es lo que E1 prueba, con criterio fijado antes.
- La pendiente media de cuenca de 90 m no es la pendiente de ladera ni la del terreno del Artículo 142.
