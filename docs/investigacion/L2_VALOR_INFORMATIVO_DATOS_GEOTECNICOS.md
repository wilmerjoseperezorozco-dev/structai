# L2. Valor informativo de los datos geotécnicos y de microzonificación frente a la complejidad del modelo

Estado: **Fase 0, protocolo (9 de noviembre de 2026).** No se ha ejecutado ningún análisis ni se ha escrito código para esta línea. Los valores marcados «a fijar» se congelan **antes** de la primera corrida y se registran con fecha; después solo cambian por una enmienda escrita.

Issue: [#168](https://github.com/wilmerjoseperezorozco-dev/structai/issues/168). Relacionada: [#76](https://github.com/wilmerjoseperezorozco-dev/structai/issues/76) (microzonificación local), [#61](https://github.com/wilmerjoseperezorozco-dev/structai/issues/61) (amenazas geoespaciales), L1 ([#167](https://github.com/wilmerjoseperezorozco-dev/structai/issues/167)).

## 1. Pregunta e hipótesis

**Pregunta.** Al elegir la sección de un pórtico de concreto, ¿cuánto vale cada fuente de información sísmica y de suelo, y ese valor supera lo que se gana haciendo más complejo el modelo de aprendizaje automático?

**H2.** Para pórticos de concreto reforzado en Bogotá, Cali y Pereira, pasar de la información regional (Aa/Av del Apéndice A-4) a la información local (perfil de suelo y microzonificación) reduce la pérdida de decisión más que pasar de un modelo simple a uno complejo con la misma información. La pérdida combina el error en deriva, cortante basal, sección requerida y costo, y la tasa de diseños que incumplen bajo el espectro local.

**Resultado científico principal.** No es solo aceptar o rechazar H2: es **cuantificar cuánto vale cada fuente** (en error de deriva, de cortante basal, de sección y de costo, y en tasa de subdiseño), por ciudad y por zona.

**Advertencia de partida.** Con un motor determinista suave, es probable que un modelo flexible aproxime bien la salida si dispone de las entradas correctas, y que un modelo sin la entrada local no pueda recuperarla por mucho que se complique. Por eso H2 tiene buena probabilidad de cumplirse casi por construcción; lo que el estudio aporta de nuevo es la **magnitud** del valor de cada fuente y dónde (qué zonas) el dato regional falla hacia el lado inseguro. Se reporta aunque H2 se cumpla de forma trivial.

## 2. Motores elegidos y datos

| Pieza | Papel | Estado hoy |
|---|---|---|
| `motor-geopot` (`a4.py`) | Aa/Av regionales por municipio (Apéndice A-4) | Existe |
| `motor-geopot` (`cortante_basal.py`) | Fa, Fv, periodos del espectro, Sa, cortante basal Vs y fuerzas por nivel | Existe, **pero Fa y Fv salen solo de las tablas NSR-10**: no admite un espectro local |
| `orquestador` (`diseno_integral`) | Selección de sección de viga y columna con deriva A.6.4, estabilidad, columna fuerte–viga débil y costo APU; internamente usa `motor-analisis`, `motor-concreto` y `motor-apu` | Existe, mismas limitaciones del L1 |
| Tabla `microzonificacion_sismica_local` | Fa, Fv, Tc, Tl y A0 (diseño y seguridad limitada) por zona | Existe: **36 zonas**, verificadas el 9-nov-2026: Bogotá 16 (Decreto 523/2010), Pereira 7 (2011), Cali 13 filas (2014) |
| Espectro local en el cortante basal | Evaluar Vs con los coeficientes de cada zona | **Falta** (Fase 1) |
| Sustituto de aprendizaje automático de sección y costo | Escalera de complejidad | **Falta** (Fase 4); hoy solo hay sustitutos de zapata y muro |

No se usan `motor-geotecnia` ni `motor-licuacion`: ampliarían el alcance a cimentaciones y licuación, que no son parte de esta pregunta.

## 3. Diseño del estudio

**Niveles de información (anidados).**
- **I0, regional:** Aa/Av del A-4 del municipio y un perfil de suelo por defecto (**a fijar y documentar con su fuente en NSR-10 A.2.4**; el resultado se reporta también con otro perfil por defecto como sensibilidad).
- **I1, + perfil de suelo:** el perfil NSR-10 (A–E) de la zona. El perfil «verdadero» de cada zona no está en el repositorio; se define como el **perfil equivalente**, el que mejor aproxima el espectro local de la zona. Esto es una cota optimista del valor del perfil (en la práctica se estima con error); se añade una sensibilidad con una clase de error.
- **I2, + microzonificación:** los coeficientes de la zona (Fa, Fv, Tc, Tl, A0). Es la **referencia**, porque la microzonificación prevalece legalmente donde existe (NSR-10 A.2.9.1).

**Niveles de modelo.** Motor determinista con el nivel de información dado (sin aprendizaje: mide solo el sesgo de información) y tres modelos de aprendizaje de complejidad creciente M0, M1, M2 (lineal regularizado, árboles potenciados, red o conjunto; **elección exacta a fijar**) entrenados con las salidas del motor. El «modelo completo» es I2 con el modelo más complejo.

**Diseño factorial.** Error de cada celda (nivel de información × modelo) frente a la referencia. La pérdida total se descompone en un componente de información (lo que el modelo no puede saber) y uno de aproximación (lo que el modelo aprende mal).

**La zona es un escenario, no una ubicación.** La tabla no tiene polígonos: no se puede asignar una zona a un predio. Cada una de las 36 zonas se evalúa como escenario posible de la ciudad. El valor de conocer la zona se mide como lo que se pierde al no conocerla.

**Estructuras.** Matriz de pórticos (número de pisos, luces, grupo de uso, DMO/DES) **a fijar antes de correr**; número de casos limitado por el tiempo de evaluación por pórtico, que se mide en la Fase 1.

## 4. Medidas

Por pórtico y zona, frente a la referencia I2:

| Medida | Cómo |
|---|---|
| Error en deriva | Δ/hp, absoluto y relativo |
| Error en cortante basal | Vs en kN y relativo |
| Error en sección requerida | Salto en la rejilla (columna, base, altura) y si la sección elegida coincide |
| Error en costo | Relativo (%), porque los precios APU son de Barranquilla 2026 y se aplican a otras ciudades: el costo absoluto no es válido, la diferencia relativa sí |
| Tasa de subdiseño | Fracción de diseños elegidos con información de nivel menor que **no cumplen** la verificación bajo el espectro local |
| Sobrecosto | Costo adicional cuando la sección elegida cumple pero es mayor que la de referencia |

El error inseguro (subdiseño) y el costoso (sobrecosto) son asimétricos; se reportan por separado y la pérdida combinada usa ponderaciones **a fijar antes de correr**.

## 5. Análisis

- Valor incremental de cada fuente: I0→I1 (perfil) e I1→I2 (microzonificación), y total I0→I2. Como las fuentes están anidadas (la microzonificación incluye el efecto del suelo), no se usa una descomposición tipo Shapley entre ellas: se reportan los incrementos en orden y la sensibilidad al orden.
- Valor de la complejidad: M0→M2 con la información fija.
- **Criterio de H2:** cociente entre la ganancia por información y la ganancia por complejidad ≥ ρ (**a fijar**), con intervalo bootstrap por conglomerados (por zona) que excluya 1.
- Validación del aprendizaje con zonas completas retenidas (dejar una zona fuera) y con familias de pórticos retenidas, para medir extrapolación y no memoria.
- Se reportan por ciudad y por zona, incluidos los casos sin efecto.

## 6. Límites declarados desde el inicio

- **Solo Bogotá, Cali y Pereira.** No hay microzonificación ingestada del Caribe ni de Barranquilla; la hipótesis no se extiende al Atlántico.
- La «verdad» es el resultado del código bajo el espectro del decreto local, no la respuesta medida de estructuras reales.
- Pórtico plano por fuerza horizontal equivalente, una sección de viga y una de columna, sin torsión ni P-Delta en la deriva (supuestos del motor).
- El perfil equivalente es optimista; el costo absoluto no es transferible entre ciudades.
- Los espectros de Cali incluyen filas de dos tramos y cada decreto tiene su forma: reproducirlos exige validar contra las tablas de cada decreto (Fase 1), no suponer la forma del NSR-10.
- Resultado dentro del modelo; salida como propuesta para revisión del ingeniero responsable, con el aviso de responsabilidad profesional ([#18](https://github.com/wilmerjoseperezorozco-dev/structai/issues/18)).

## 7. Fases

| Fase | Contenido | Condición para pasar |
|---|---|---|
| 0 | Este protocolo | Congelar perfil por defecto, matriz de pórticos, ponderaciones de la pérdida, ρ y la escalera de modelos |
| 1 | Cortante basal con espectro local por ciudad; verificar las 36 zonas contra los decretos; medir tiempo por pórtico | Pruebas contra cálculo a mano de cada decreto |
| 2 | El orquestador acepta un espectro local sin alterar el comportamiento actual | Regresión: sin espectro local, resultados idénticos |
| 3 | Errores de información sin aprendizaje (primer resultado: valor de cada fuente) | Dataset generado y reproducible |
| 4 | Escalera de modelos de aprendizaje y validación con zonas retenidas | Hiperparámetros fijados por la regla preregistrada |
| 5 | Análisis preregistrado e informe con nulos | |

## 8. ¿Llegará a ser un motor?

Como en L1, el resultado se publica como hallazgo. Lo reutilizable de la Fase 1 (cortante basal con espectro local) sí iría como extensión de `motor-geopot` con contrato `ResultadoMotor`.
