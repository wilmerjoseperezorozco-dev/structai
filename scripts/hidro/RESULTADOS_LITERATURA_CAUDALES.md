# Resultados: ecuaciones de caudal máximo de la literatura (protocolo PROTOCOLO_LITERATURA_CAUDALES.md, 2026-11-08)

**Resumen: el piloto no produjo ninguna ecuación evaluable.** No se calculó ninguna métrica contra las 257 estaciones, porque ninguna ecuación pasó los criterios de inclusión fijados de antemano. Es un resultado negativo sobre la **viabilidad del método**, no sobre las ecuaciones ni sobre la hidrología.

## Qué se hizo
- Búsqueda con las 6 consultas del protocolo (OpenAlex, desde 1990, 25 por consulta): **141 trabajos únicos**, lista completa en `literatura_caudales_busqueda.json` (guardada antes de cribar). OpenAlex marca 140 de 141 como acceso abierto; esa marca es del indexador y no garantiza que yo pueda leer el texto.
- Cribado por título y resumen, por una sola persona: la gran mayoría trata de otros temas (glaciares, calidad de agua, política, clima, caudales mínimos, modelos lluvia-escorrentía). Quedaron **8 candidatos** con posibilidad de traer una ecuación explícita de caudal máximo; los otros 133 se descartan por no cumplir I1 (sin ecuación explícita de Q máximo) a la vista del título y el resumen. Ese descarte es el paso menos verificado: no leí el texto de esos 133.

## Los 8 candidatos y por qué ninguno se evaluó
| # | Trabajo (DOI) | Decisión | Motivo |
|---|---|---|---|
| 0 | Cauca, Colombia, controles del caudal pico (10.1016/j.ejrh.2026.103763) | No evaluable | Es abierto según el indexador, pero la página de ScienceDirect devuelve 403 y un captcha a mis herramientas; no lo salté. No pude leer las ecuaciones (I3). **Es el candidato más cercano y debería leerlo una persona.** |
| 122 | Calibración del modelo MG para caudales máximos en Colombia, 277 estaciones (hdl 11190/166) | No evaluable | El repositorio devuelve error 500; texto no leído (I3). Además, por usar estaciones del IDEAM, tendría el riesgo de fuga declarado en el protocolo. |
| 38 | Amazonía peruana, análisis regional (10.1590/0102-77863440052) | Leído; **fuera de rango** | Ecuación Q̄ = 6987,6393 + 0,0554·A, válida solo para 99.779–877.479 km². Nuestra cuenca más grande tiene 18.624 km²: **cero estaciones dentro del rango declarado**. La extracción vino de un resumen automático de la página (que avisó que las ecuaciones salen desordenadas); no la verifiqué contra la imagen de la página. |
| 33 | Arroyo Feliciano, Entre Ríos, Argentina (10.33414/rtyc.44.1-25.2022) | Leído en el PDF; **excluido por I2** | Las ecuaciones (14, 16, 18, 20) dependen de la lluvia media areal de un evento de 2 años con duración por región y de la pendiente del cauce principal (m/m); no son variables que tengamos. Además se ajustaron a caudales de un **modelo hidrológico**, no a caudales observados. |
| 5 | Calibración del índice de torrencialidad, Andes noroccidental (10.18273/revuin.v24n1-2025006) | Excluido por I2 (por resumen) | Método racional modificado de Témez: necesita coeficiente de escorrentía e intensidad, no solo A, P, S. |
| 16 | Caudales extremos no instantáneos, Andes nororiental (10.18273/revuin.v23n2-2024008) | Excluido por I1 (por resumen) | Aplica ecuaciones de amplificación (Fuller, Tonini, Tucci) para pasar de caudal medio diario a pico; no publica una ecuación regional de Q_T. |
| 49 | L-momentos para eventos máximos en Colombia, tesis (Javeriana, 10554/17079) | Excluido por I1 (por resumen) | Curvas de frecuencia regional adimensionales; el resumen no anuncia una ecuación del caudal índice. No leí el texto. |
| 112 | Regionalización de distribuciones de caudales máximos instantáneos en Colombia (repositorio UTB) | Excluido por I1 (por resumen) | Idem: distribuciones y curvas, no una ecuación en función de predictores. No leí el texto. |

## Qué se concluye y qué no
- **Se concluye:** con las consultas y los criterios fijados, no obtuve una sola ecuación regional de Q máximo, abierta y legible, que use predictores que podemos calcular **y** cuyo rango incluya nuestras cuencas. El cuello de botella son el acceso al texto (captchas y repositorios caídos) y que lo publicado en Colombia suele ser distribuciones y curvas de frecuencia, no ecuaciones del caudal.
- **No se concluye** nada sobre si la literatura mejora a M2 (factor 1,75): nunca se comparó. Tampoco que el Cauca o el modelo MG fallen o acierten.
- La extracción automática por resumen de página (Peru) tiene el riesgo de transcripción declarado; solo se usó para constatar el rango de validez.

## Lo que quedó abierto (necesita una persona o una decisión)
1. Leer a mano el artículo del Cauca (#0): si trae ecuaciones de Q_T con área y lluvia, se evalúa con este mismo protocolo sin cambiarlo. Sus 38 cuencas están en el Cauca, que no es el Caribe, así que aportaría poco al caso Caribe.
2. Conseguir el texto del modelo MG (#122) por otra vía (biblioteca universitaria). Si se evalúa, anotar la fuga posible.
3. Ampliar la búsqueda (más consultas, otros índices, literatura gris del IDEAM/INVÍAS/CAR) exigiría un protocolo nuevo; no lo hice por mi cuenta.

Descarga: para leer #33 bajé un PDF de 3,6 MB de la revista Tecnología y Ciencia (CC BY-NC 4.0) a una carpeta temporal fuera del repositorio; no se versiona.
