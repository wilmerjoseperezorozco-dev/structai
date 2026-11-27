# Resultados H7 (#273): cuánto vale conocer el nivel freático antes de diseñar pilotes (2026-11-18)

- **Prerregistro:** `PRERREGISTRO_H7_NIVEL_FREATICO.md`, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6995544064) antes de cruzar niveles con el motor.
- **Código:** `h7_valor_nivel_freatico.py`, sin cambios. **Salida:** `h7_resultados.json`.
- **Muestra:** 947 niveles medidos en llanura (51 bloques), perfiles arena y mixto, proyecto de 30 pilotes.

## C1 (seguridad): suponer "seco" es **materialmente inseguro**

| Muestra | P(capacidad real < 0,9·Q), política optimista | IC95 % | P(< 0,8·Q) |
|---|---|---|---|
| Todos | **46 %** | [42 %; 50 %] | 35 % |
| Con alarma de relieve | 53 % | [52 %; 54 %] | 42 % |
| Sin alarma | 37 % | [30 %; 43 %] | 24 % |

- **Todo el déficit está en pilotes excavados (método β).** Ahí, entre el 51 % y el 94 % de los sitios queda por debajo de 0,9·Q, según la carga.
  - **Ejemplo:** arena, Ø0,5 m, 1.000 kN. Diseñado "seco" sale de 11,25 m; con el nivel real haría falta, en promedio, 13,9 m.
- **En hincados (Meyerhof), suponer seco no produce déficit**, por el efecto de CN declarado en el prerregistro.
  - En cambio, suponer el nivel freático en la superficie deja entre el 7 % y el 18 % de los sitios por debajo de 0,9·Q. En hincados, la suposición "conservadora" **no es conservadora**.

## C2 (valor de la información): medir se paga

| Muestra | VOI frente a suponer NF = 0 | IC95 % | Referencia de exploración |
|---|---|---|---|
| Todos | **26 M$** por proyecto | [22; 30] M$ | 9,7 M$ (10 m de perforación INVIAS 621.3.1) |
| Con alarma | 19 M$ | [17; 20] M$ | |
| Sin alarma | 37 M$ | [30; 43] M$ | |

- En promedio, el piezómetro o apique **vale entre 2 y 4 veces más que una referencia de exploración alta**. Además, deja el diseño sin déficit en todos los escenarios.
- **Por tipo de pilote:**
  - En excavados de diámetro grande, el VOI llega a 83-170 M$ (mixto, Ø1,0 m).
  - En hincados el VOI frente a "NF = 0" es negativo: medir alarga el pilote, pero corrige el déficit de hasta el 18 %.

## La alarma de relieve ayuda, pero no reemplaza medir

| Política | P(< 0,9·Q), todos | Con alarma | Sin alarma |
|---|---|---|---|
| Optimista (seco) | 46 % | 53 % | 37 % |
| **Alarma H2b** (NF = 0 si hay alarma) | **16 %** [12 %; 20 %] | **0,8 %** | 37 % |
| Piezómetro | 0 % | 0 % | 0 % |

- **Con alarma:** usar NF = 0 elimina prácticamente el déficit, y cuesta casi lo mismo que medir (el VOI frente a la alarma no es significativo: −1,2 M$ [−6,6; +3,5]).
- **Sin alarma**, el 37 % de los sitios sigue con déficit. La alarma no detecta todos los niveles someros (sensibilidad ≈ 0,74-0,77 en H2/H2b).

## Lectura (fijada de antemano)

- **Para StructAI (`/sitio` y motor de pilotes):** en llanura, antes de diseñar **pilotes excavados**, pedir la medición del nivel freático. No suponerlo nunca "seco".
  - Si no se mide, el motor debería usar NF = 0 por defecto en excavados y advertirlo. En hincados debería advertir que la suposición superficial no es conservadora por el efecto de CN.
  - La alarma de relieve sirve para **priorizar** la medición, no para sustituirla.
- **Qué no mide:** licuación, hinca, succión sobre el nivel freático, variación estacional ni el perfil de suelo real de cada pozo.

## Limitaciones

- Los perfiles de suelo son idealizados; el N60 es fijo e independiente del nivel.
- Los niveles son de llanura, de fechas distintas.
- La referencia de costo de exploración no es el precio real de un piezómetro: el INVIAS no tiene ese ítem.
- El bootstrap tiene solo 200 réplicas.

## Antecedentes en la literatura

- **HAND** (*Height Above the Nearest Drainage*): Rennó et al. (2008) y Nobre et al. (2011) lo propusieron como descriptor del terreno ligado a la profundidad del agua subterránea en la Amazonía. Es el antecedente directo del "relieve local" de H2. Aquí se usó una versión simplificada (cota menos la mínima a ≤ 1 km), no el HAND con red de drenaje.
- **Fan, Li y Miguez-Macho (2013, *Science*):** mapa global de profundidad del nivel freático, a partir de más de un millón de pozos y un modelo forzado por clima, terreno y nivel del mar. La profundidad sigue el relieve y el clima, y en llanuras húmedas el nivel es somero.
- **Aprendizaje automático con DEM y pozos:**
  - Ma et al. (2023, *Groundwater*): bosques aleatorios en EE. UU.;
  - Li et al. (2023, *Water*): 75 perforaciones en Etiopía con *gradient boosting*.
  - Ambos advierten el **sesgo de muestreo**: los pozos están donde es fácil acceder y hay agua.
- **Valor de la información en geotecnia:**
  - Freeze et al. (1990, 1992): "valor de los datos" en hidrogeología;
  - Ching y Phoon: el diseño por confiabilidad es el que más responde a la información disponible;
  - Schweckendiek y Vrouwenvelder: análisis bayesiano preposterior con piezómetros en diques.
  - No encontré un estudio que combine nivel freático inferido por DEM con el VOI para pilotes. H7 sería una contribución en esa intersección; habría que confirmarlo con una búsqueda bibliográfica formal.
