# Resultados del barrido exploratorio de relaciones municipales del Caribe (2026-11-08)

Protocolo fijado antes de calcular: [`PROTOCOLO_BARRIDO_CARIBE.md`](PROTOCOLO_BARRIDO_CARIBE.md). Código: `barrido_caribe.py`. Panel: `panel_caribe.csv` (195 municipios, 17 variables). Todos los pares: `barrido_caribe_resultados.json`.

**Esto genera hipótesis; no confirma nada.** Se evaluaron 120 pares de variables de familias distintas (correlación parcial de Spearman controlando log de población y de área, corrección de Benjamini-Hochberg, estabilidad del signo al omitir cada departamento). **39 pares cumplieron el criterio de candidato.** Es un número alto y la mayor parte no aporta información nueva, como se explica a continuación.

## 1. Candidatos que son mecánicos o definicionales (se descartan como hallazgos)
La mayoría de los candidatos con |ρ| más alto son redundantes porque miden lo mismo con otro nombre:
- Terreno frente al mapa de inundación del IGAC y frente a HAND (elevación media y pendiente frente a la fracción inundable, ρ = −0,75; HAND frente a fracción inundable, ρ = +0,75). El terreno bajo y plano es, por definición, el que se inunda.
- Exposición vial frente a HAND del municipio (ρ = +0,64): la exposición vial se calcula con el propio HAND.
- Elevación y pendiente frente a amenaza de movimientos en masa (ρ ≈ +0,5): relieve y amenaza por relieve.
- Dentro de la misma familia (control de consistencia): pendiente frente a HAND ρ = −0,90, elevación frente a pendiente ρ = +0,89, lluvia anual frente a p95 mensual ρ = +0,80.

## 2. Candidatos que confirman lo esperado
- Lluvia extrema frente a reportes de inundación por 100 mil habitantes: ρ = +0,28 (+0,30 controlando HAND, IC por departamentos [+0,07; +0,37]).
- Terreno bajo (HAND) frente a reportes de inundación y viviendas dañadas: ρ = +0,21 y +0,26.

Son coherentes con la física y con resultados anteriores del proyecto; sirven como control de sentido del panel, no como novedad.

## 3. Candidatos que valen una hipótesis preregistrada
Marcados como **posteriores al barrido** (las verificaciones adicionales de esta sección se hicieron después de ver el barrido y no están preregistradas).

**V1. La exposición de la vía principal a terreno bajo se asocia con más reportes por habitante, más allá del HAND del municipio.**
Controlando población, área y la fracción del municipio en HAND < 10 m: reportes de inundación ρ = +0,27 (IC por departamentos [+0,17; +0,34]), viviendas dañadas ρ = +0,34 [+0,19; +0,45], personas afectadas ρ = +0,26 [+0,08; +0,40], con n = 159.
*Por qué importa:* en el análisis C1 la exposición vial apenas superó al territorio, pero aquí parece capturar algo que el territorio no: dónde está la población.
*Explicaciones alternativas que hay que descartar:* que la población y los asentamientos se concentren a lo largo de la vía en terreno bajo; que los municipios con más vía reporten más (sesgo de reporte); que el OpenStreetMap esté mejor mapeado donde hay más actividad.
*Cómo confirmar:* calcular la misma exposición en departamentos que no entraron al barrido (por ejemplo Antioquia, Santander, Tolima o Meta, con la tubería HAND y OpenStreetMap ya escrita) y probar V1 con el mismo control, fijando el criterio antes.

**V2. Los municipios con más terreno bajo (< 10 m) tienen menos vivienda de material vulnerable en el Sisbén.**
ρ = −0,35 en el barrido y −0,39 controlando el porcentaje de población en cabecera (IC por departamentos [−0,47; −0,20]).
*Explicaciones a descartar:* efecto del área metropolitana de Barranquilla y de las capitales costeras (más cemento y ladrillo), la composición de las muestras del Sisbén (es una muestra, no un censo) y el efecto de la ruralidad.
*Cómo confirmar:* repetir con municipios del interior que tengan zonas bajas (valle del Magdalena, Bajo Cauca), o dentro de cada departamento por separado.

**V3. Coeficiente de variación mensual de la lluvia frente a vivienda vulnerable (ρ = −0,30).** Más irregular la lluvia, menos vivienda vulnerable. Sin mecanismo evidente; puede ser una variable que representa la región (La Guajira frente al resto). Se anota, no se persigue.

## 4. Qué no se puede concluir
- Con 7 departamentos y 195 municipios, un patrón regional (por ejemplo, que La Guajira difiera del resto en varias variables a la vez) puede producir muchos candidatos falsos. La estabilidad del signo al omitir un departamento ayuda, pero no elimina esa posibilidad.
- 120 pares con q < 0,10 admiten por construcción alrededor de un 10 % de falsos descubrimientos entre los candidatos.
- Ninguna asociación es causal.
- La UNGRD no registra daños a infraestructura vial; las variables de eventos son de personas y viviendas.

## 5. Siguiente paso propuesto
Preregistrar V1 y confirmarla fuera del Caribe antes de afirmar nada. Si se confirma, la exposición vial a terreno bajo sería un indicador útil para priorizar inspección de infraestructura; si no, queda como un artefacto del Caribe.
