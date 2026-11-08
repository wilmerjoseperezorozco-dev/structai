# Protocolo: no estacionariedad espacial y transferibilidad del modelo de caudales máximos (preregistrado 2026-11-08, antes de ajustar ningún modelo regional)

**Pregunta.** ¿Los coeficientes de la regionalización de caudales (elasticidad frente a área, lluvia y pendiente) cambian entre dominios hidro-climáticos de Colombia, de modo que un modelo único nacional rinde peor que modelos por dominio al predecir cuencas no vistas? Y, aparte: ¿cuánto se degrada un modelo cuando se aplica en un dominio que no estuvo en su entrenamiento?

**Postura.** La hipótesis puede salir a favor o en contra. La Etapa A ya dio una señal en contra: añadir solo una constante por región (M3) no mejoró frente al modelo nacional M2 (−0,012, IC95 % [−0,030; +0,007]). Este protocolo prueba algo más fuerte (que **cambien los coeficientes**, no solo el nivel) y declara de antemano que un resultado nulo es plausible y se publica igual. «Demostrar que el modelo nacional falla» no es el objetivo: es una de las dos salidas posibles.

## 1. Datos
Los mismos de la Etapa A (`cuencas_estaciones.csv` con la variante elegida r1500; `frecuencia_crecientes_ideam.json`): **257 estaciones**, objetivo ln Q_T con GEV, T = 2, 5, 10, 25, 50. Predictores A, S, P (+ elevación media H solo para dominios). Código reutilizado de `regionalizacion_validacion.py`. Ningún dato nuevo.

## 2. Dominios
- **D1 (primario, fijado de antemano): regiones naturales** de la Etapa A (Caribe 59, Andina 152, Pacífica 35, Orinoquía 11). **Regla de tamaño:** un dominio con menos de 30 estaciones de entrenamiento en el pliegue usa el modelo nacional (así Orinoquía, con 11, no tiene modelo propio y no se concluye nada sobre ella).
- **D2 (secundario): dominios por agrupamiento** (k-means, **k = 3**, fijado ahora; k = 4 como sensibilidad) sobre ln P, ln S y ln H estandarizados. **Solo predictores, sin caudales ni coordenadas.** El agrupamiento se recalcula **dentro de cada pliegue** con las estaciones de entrenamiento, y la estación de prueba entra al centroide más cercano. Por tanto no usa información de la estación de prueba.

## 3. Modelos
- **M2** (nacional, de la Etapa A): ln Q = a + b ln A + c ln P + d ln S.
- **M5** (por dominio): el mismo M2 ajustado **solo** con las estaciones de entrenamiento del dominio de la estación de prueba (todos los coeficientes varían). Con D1 es M5a; con D2 es M5b.
- **R** (comparador de aprendizaje automático): bosque aleatorio (scikit-learn, 300 árboles, profundidad máxima 6, semilla fija) sobre ln A, ln P, ln S y ln H, **sin coordenadas** (con coordenadas explotaría la vecindad espacial). Nacional.

Todos con la validación ciega de la Etapa A: se excluyen las estaciones a menos de 50 km y las de la misma corriente.

## 4. Criterios
- **Confirmatorio único (C1):** a T = 10, la mediana de |ε| de **M5a** es **menor** que la de **M2**; IC95 % de la diferencia por bloques espaciales de 1° × 1° (la misma rutina pareada de la Etapa A) que excluya 0.
- **Secundarios (exploratorios, todos reportados):** M5b frente a M2 (k = 3 y 4); R frente a M2; los demás T; cada región.
- **Heterogeneidad de coeficientes (descriptivo):** coeficientes de M2 ajustados por dominio D1 con IC95 % por bloques, comparados con los nacionales; y la prueba F clásica de interacción dominio × predictores, **marcada como no válida como prueba formal** porque las estaciones están autocorrelacionadas en el espacio (el p-valor se reporta como orientación).
- **Sesgo regional del modelo nacional (C2, descriptivo):** mediana de ε de M2 por región con IC95 % por bloques. Se dice que el modelo nacional «falla» en una región solo si el IC95 % excluye 0 **y** el factor de sesgo queda fuera de [0,67; 1,5].
- **Transferibilidad entre dominios (T1):** validación «dejar fuera una región entera»: M2 se ajusta con todas las regiones menos una y se aplica a la región excluida. Se reporta la penalización respecto a la validación ciega normal (factor típico por región). Orinoquía se reporta pero no se concluye (n = 11).

## 5. Sensibilidad
Zona de exclusión de 0 y de 100 km; T = 2 a 50; objetivo Log-Pearson III en lugar de GEV; excluir cuencas > 2.000 km²; k = 4 para D2.

## 6. Qué NO se concluye
Que haya o no no estacionariedad *temporal* (cambio climático en el tiempo): aquí solo hay variación **espacial**; la estacionariedad temporal se supone, como en la Etapa A. Ninguna interpretación física de los signos (la pendiente ya salió con signo negativo). Nada sobre embalses ni cuencas reguladas.

## 7. Limitaciones de antemano
Orinoquía (11) no se puede modelar aparte. Las regiones naturales se definen por departamento, no por cuenca, así que las estaciones de un departamento «de otra región» (por ejemplo, ríos que nacen en los Andes y pasan al Caribe) se asignan por el departamento de la estación. Con 257 estaciones, ajustar tres coeficientes por dominio con ~35 estaciones (Pacífica) tiene poca potencia y mucha varianza: un M5a peor que M2 puede deberse a eso y no a la ausencia de no estacionariedad. El caudal observado sigue siendo el máximo horario. **No sustituye el estudio hidrológico de un proyecto con ingeniero responsable.**

## 8. Qué se publica pase lo que pase
C1, C2, T1 y la tabla de coeficientes por dominio, con los intervalos, aunque C1 salga negativo.
