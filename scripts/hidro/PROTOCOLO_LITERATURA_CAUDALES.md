# Protocolo: ecuaciones de caudal máximo de la literatura, evaluadas a ciegas contra las estaciones del IDEAM (preregistrado 2026-11-08, antes de buscar o leer ningún artículo)

**Pregunta.** ¿Alguna ecuación publicada de caudal máximo o de crecida regional estima los caudales de nuestras 257 cuencas del IDEAM mejor que nuestro modelo de la Etapa A (M2: factor de error típico 1,75 a T = 10), o al menos lo bastante bien como para ser aplicable en Colombia?

**Por qué es una prueba limpia.** Una ecuación publicada no se ajusta a nuestros datos, así que no necesita validación cruzada: se evalúa sobre las 257 estaciones tal cual, con los predictores ya calculados (área A, pendiente S, lluvia media anual P, elevación media H).

## 1. Búsqueda (consultas fijadas ahora, OpenAlex, sin filtrar por resultado)
1. `regional flood frequency analysis Colombia`
2. `regionalization peak discharge Andes catchment area`
3. `regional flood estimation tropical catchments ungauged regression drainage area`
4. `ecuaciones regionales caudal máximo Colombia`
5. `regionalización de caudales máximos cuencas Latinoamérica`
6. `flood quantile regression ungauged basins South America`
Se conservan los 25 primeros resultados de cada consulta por relevancia de OpenAlex (publicaciones desde 1990), se unen y se eliminan duplicados. La lista completa, con DOI, se guarda **antes** de cribar.

## 2. Criterios de inclusión (fijados ahora; los aplico leyendo título y resumen, y registro la decisión de cada trabajo con su motivo)
Un trabajo entra a la evaluación solo si cumple **todo**:
- **I1.** Publica una **ecuación explícita** (o una tabla de coeficientes) de caudal máximo/crecida (Q_T o Q_máx) para una o más cuencas.
- **I2.** La ecuación usa como predictores variables que podemos calcular: área de cuenca, y opcionalmente lluvia, pendiente o elevación.
- **I3.** El texto completo es de **acceso abierto** y puedo leer los coeficientes y sus unidades; si no, se registra como «no evaluable» y no se usa.
- **I4.** Declara el periodo de retorno (o el tipo de caudal) para el que vale.
- **I5.** Su región de calibración es tropical, andina o latinoamericana. Las ecuaciones globales o de otros climas se **registran pero se evalúan por separado**, marcadas como «no regionales».

## 3. Extracción
Cada coeficiente se lee del texto completo (Docling donde haya tablas, lectura directa en el resto) y se **verifica contra la página** antes de usarse. Se guarda: DOI, ecuación como se escribe, unidades, región, periodo de retorno, rango de validez declarado (áreas, lluvias), y el número de la página.

## 4. Evaluación (idéntica para todas las ecuaciones incluidas)
Para cada ecuación se calcula Q̂ en las estaciones **dentro de su rango de validez declarado** (si no lo declara, en todas) para el T que más se aproxime entre 2, 5, 10, 25 y 50 años. Se usa como referencia el mismo Q_T de la Etapa A (GEV sobre máximos anuales del IDEAM; Log-Pearson III como sensibilidad).
- **Métrica de escala (absoluta):** factor de error típico exp(mediana |ln(Q̂/Q)|) y sesgo mediano.
- **Métrica sin escala:** ρ de Spearman entre ln Q̂ y ln Q. Separa si la ecuación **ordena** bien las cuencas (forma) de si tiene la **escala** correcta (por ejemplo, por ser de pico instantáneo y no de máximo horario).
- **Comparación:** diferencia pareada de |ln(Q̂/Q)| frente a M2 con las mismas estaciones, IC95 % por bloques espaciales de 1° (la rutina de la Etapa A).

## 5. Criterios de decisión (fijados ahora)
- **Aporta** si, para alguna ecuación incluida con al menos 30 estaciones dentro de su rango, la diferencia pareada con M2 tiene IC95 % que excluye 0 **a favor de la ecuación**. Como se prueban varias ecuaciones, el umbral se corrige por el número de ecuaciones evaluadas (Bonferroni sobre la cantidad incluida).
- **Es aplicable** si su factor de error típico es ≤ 2,0 en el total y ≤ 2,5 en el Caribe. Umbrales arbitrarios míos; se declaran como tales.
- **Falla** si su error es mayor que el del caudal específico constante B0 (1,81).
Se reportan **todas** las ecuaciones evaluadas, incluidas las que fallan.

## 6. Qué NO se concluye
Que una ecuación sea «mala» en su cuenca de origen: aquí se prueba si se **traslada** a las nuestras. Tampoco se concluye nada de ecuaciones que no pude leer en abierto.

## 7. Limitaciones de antemano
- **Fuga de información posible:** varias ecuaciones colombianas se calibraron con estaciones del IDEAM, quizá las mismas. Si una ecuación sale muy bien, no puedo descartar que se haya calibrado con las mismas estaciones; se anota.
- **Tipo de caudal:** muchas ecuaciones son de pico instantáneo y nuestro objetivo es el máximo horario, que lo subestima. La métrica sin escala (ρ) existe por esto.
- **Sesgo de publicación y de idioma;** se buscó en inglés y español.
- **Cribado por una sola persona** (yo), sin segundo revisor.
- La lluvia de nuestros predictores es CHIRPS 1991-2020, no la que usó el artículo.

## 8. Qué se publica pase lo que pase
La lista completa de trabajos encontrados, la decisión de inclusión con motivo, todas las ecuaciones extraídas y los resultados de todas ellas.
