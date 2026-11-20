# HE4 (#274): periodos medidos en edificios colombianos (recopilación)

Hipótesis HE4: los periodos medidos en edificios colombianos son menores que los del modelo de pórtico desnudo, por la rigidez de la mampostería no estructural. Medidas: T_medido/T_modelo y T_medido/Ta.

Este documento recopila la literatura y hace un análisis **descriptivo**. Todavía **no** es la prueba de HE4, que se prerregistrará aparte (ver "Siguiente paso").

Recopilado el 2026-11-19. Datos: `periodos_medidos_colombia.csv`. Solo se transcriben números, citando la fuente; no se copia texto de las fuentes.

## Fuentes

| Fuente | Ciudad | Edificios | Sistema | Modelo comparado | Estado |
|---|---|---|---|---|---|
| Torres Ayala, I. K. (2022). *Ecuación simplificada para la estimación del periodo fundamental de vibración aproximado para las edificaciones con sistemas de resistencia sísmica combinado*. Tesis de maestría, Universidad Militar Nueva Granada, Bogotá. | Bucaramanga | 15, de 21 a 108 m | Combinado, DES | ETABS 16.2.1 a partir de planos y memorias, **sin elementos no estructurales** (según la autora) | **Incluida** |
| Coral Vargas, C. M. (2014). *Caracterización del período fundamental de vibración de edificios de muros estructurales de concreto reforzado para uso residencial*. Pregrado, Universidad del Valle. hdl:10893/16234 | Cali (y torres de Bogotá medidas con la U. de los Andes) | 12 en Cali | Muros de concreto | NSR-10 A.4.2-3 y elementos finitos | **Pendiente**: el repositorio de Univalle respondió 500/503 el 2026-11-19 |
| Córdoba Arango, I. D. (2022). *Estimación del período fundamental de edificaciones conformadas por pórticos de concreto considerando secciones fisuradas*. Maestría, Universidad Nacional, Bogotá. | (amenaza de Medellín) | — | Pórticos | Solo modelos numéricos | **Excluida de la medida**: no tiene mediciones, solo "experimentos" numéricos. Sirve como referencia de modelos |
| Carrillo, J. (2009). *Ciencia e Ingeniería Neogranadina* 19(1), 39-54 | México | Viviendas de 1–2 pisos | Muros de concreto | Elementos finitos y columna ancha | **Excluida**: las viviendas son de México |
| Estudios de Quito (152 edificios), Ciudad de México y Cuba | Fuera de Colombia | — | — | — | **Excluidos**: solo como análogos regionales |

Valores de Cali y Bogotá que aparecieron en fragmentos de búsqueda del documento de Univalle (por ejemplo Mirador de Terrazas ≈ 0,61–0,63 s): **no están verificados** y no entran en el CSV hasta leer el PDF.

## Transcripción (Torres Ayala 2022)

Fuentes dentro de la tesis:
- Alturas: Tabla 8.
- Periodos medidos: Tabla 9 (EFDD y SSI, acelerómetro triaxial y registros de 60 min a 200 Hz).
- Periodo del modelo: Tabla 10 (ETABS).

Al extraer el texto del PDF, la columna de alturas quedó corrida una fila. El orden correcto lo verifiqué reproduciendo los Ta de la Tabla 11: 0,047·h^0,9 y 0,049·h^0,75 coinciden en las 15 filas con al menos 3 cifras.

## Resultado descriptivo (n = 15, una dirección por edificio)

T_medido es el promedio de EFDD y SSI. Ta se calcula para pórticos de concreto (0,047·h^0,9) y para muros (0,049·h^0,75).

| Razón | Todos (15): mediana [mín; máx] | EFDD y SSI concuerdan ≤ 10 % (12) | Casos > 1 |
|---|---|---|---|
| T_medido / T_modelo ETABS | **0,53** [0,30; 0,62] | **0,53** [0,39; 0,62] | **0 de 15** |
| T_medido / Ta pórticos | 0,53 [0,34; 0,74] | 0,52 [0,34; 0,74] | 0 de 15 |
| T_medido / Ta muros | 0,93 [0,52; 1,26] | 0,92 [0,52; 1,26] | 6 de 15 |

Hay tres edificios donde EFDD y SSI no concuerdan (Torre Gaudí 40 %, Zeratto 16 %, Aqua Tower 288 %). El filtro de concordancia **lo definí después de ver los datos**, así que es solo sensibilidad: no cambia la conclusión.

**Lectura:** en los 15 edificios, el periodo medido es aproximadamente la mitad del periodo del modelo ETABS sin elementos no estructurales, y ninguno lo supera. Va en la dirección de HE4. Ta de pórticos también sobrestima el periodo real de estos edificios combinados. Ta de muros queda cerca, con dispersión en ambos sentidos.

## Por qué esto todavía no confirma HE4

1. **Amplitud y fisuración (confusión principal).** La vibración ambiental mide con amplitudes muy pequeñas, con el concreto sin fisurar y la mampostería intacta. No se sabe si el modelo ETABS usó inercias fisuradas (0,70/0,35·Ig). Si las usó, eso solo ya explica una razón de aproximadamente 0,7–0,8. La razón 0,53 mezcla fisuración, mampostería, escaleras, losas y la interacción con el suelo.
2. **Sistema.** Son edificios combinados, no pórticos. HE4 está formulada para pórticos.
3. **Muestra.** Es una sola ciudad y una sola tesis, con edificios altos (de 21 a 108 m). No hay edificios bajos de pórticos con mampostería, que son la mayoría del inventario colombiano.
4. **El modelo no es el nuestro.** Lo construyó la autora en ETABS. Nosotros no tenemos los planos.
5. **Comparación con Ta.** Ta de la NSR-10 es deliberadamente conservador en la dirección que importa para el diseño, así que T_medido < Ta es lo esperado y no prueba nada sobre la mampostería.

## Siguiente paso propuesto

Prerregistrar HE4 en una versión que sí se puede probar:
- **Medida principal:** T_medido / T_motor, donde T_motor sale de `motor-analisis` para el edificio paramétrico equivalente (misma altura y sistema, con inercias **brutas** para igualar la amplitud de la medición).
- **Criterio:** la mediana con su IC < 1, y además < 0,8, que es la parte que la fisuración no explica.
- **Sensibilidad:** separar los edificios por sistema y por altura.

Para eso faltan más datos, en especial pórticos bajos y de mediana altura:
- el PDF de Univalle cuando el servidor responda;
- datos de la red de instrumentación de edificios de Bogotá (exigida por la NSR-10, A.11) si se piden formalmente a IDIGER;
- mediciones propias con un acelerómetro de celular, si se decide hacerlas.
