# Prerregistro #292-W: ¿el viento B.6 cambia el diseño de los pórticos de concreto de zona sísmica baja?

Fijado el 2026-11-24, **antes** de correr el corpus. Código: `scripts/memorias_sinteticas/viento_292.py` y el motor de la rama `feat/viento-cubierta-292` (PR #319).

## Sesgo declarado

- **Exploración previa.** Ya hice una exploración informativa con un edificio de 2 pisos de 5 × 5 m, en zona baja, con cubierta liviana. Resultado: el refuerzo no cambió, pero 1,6W en la base (43,6 kN) superó a E (26,6 kN). Las predicciones de abajo salen de esa exploración.
- **Conteo de elegibles.** Sé cuántos edificios entran, porque sale de la geometría y no de resultados: de los 358 edificios de zona baja (todos DMI), 86 son "edificios bajos" según B.6 (h ≤ 18 m y h ≤ menor dimensión en planta).
- **Lo que no se ha corrido:** ningún diseño del corpus con viento.

## Diseño

- **Población:** los 86 edificios bajos de zona baja del corpus F1 (`corpus.csv`, estado ok). Los otros 272 quedan para #242 y no se evalúan.
- **Brazos pareados por edificio:** las mismas secciones, cargas y margen u_máx por defecto (0,90 en vigas, #292-A).
  - **control:** sin viento;
  - **W28C:** V = 28 m/s, exposición C. Es la velocidad de las regiones especiales y de la región 3.
  - **W36D:** V = 36 m/s, exposición D. Es la envolvente superior: región 5 en costa abierta.
- **Lo que se mantiene igual en todos los brazos:**
  - la cubierta es la losa del corpus, con la D de entrepiso; la cubierta liviana **no** se evalúa;
  - el factor de importancia es I = 1,00 para el grupo I (hipótesis de #319).

## Métricas e hipótesis

IC95 de Wilson para proporciones.

| Id | Métrica (por brazo de viento frente al control) | Predicción |
|---|---|---|
| **H-W1** (primaria) | Fracción de edificios cuyo refuerzo cambia en alguna viga o columna (firma completa del armado) | W36D: IC95 superior ≤ 10 % |
| **H-W2** | Fracción de edificios donde 1,6·W en la base (máximo entre ±X y ±Y) supera a E = ΣFs/R (máximo entre X e Y) | W36D: > 50 % (descriptiva, sin regla de decisión) |
| **C-W** | Sobrecosto relativo (vigas y columnas, costo directo) | W36D: p90 ≤ 1 % |
| **R-W** | Edificios que cumplían y dejan de cumplir | 0 |

## Regla de decisión

**Si se cumplen las tres condiciones en W36D:**
- H-W1 tiene IC95 superior ≤ 10 %;
- R-W = 0;
- C-W tiene p90 ≤ 1 %;

entonces **el viento no gobierna el pórtico de concreto con losa en zona baja**. Queda opcional y la memoria lo declara.

**Si no se cumplen**, el viento sí cambia los diseños y debe evaluarse por defecto en zona baja. Eso exige V por municipio, que va en un issue aparte. W28C se informa sin regla de decisión.

## Calidad

- Errores de ejecución: se reportan por id y no se reemplazan.
- La firma de refuerzo incluye todos los niveles y pisos: barras, diámetros, estribos y separaciones.

## Fuera de alcance (declarado)

- Cubierta liviana, anclajes (SIN VALIDAR en #319) y confiabilidad β con viento: F3b no modela W.
- Edificios con h > 18 m.
- Casos torsionales de viento.

## Piloto (declarado)

Se corrió un piloto de 2 edificios para comprobar el script (`--piloto 2`). En los dos, ningún refuerzo cambió y 1,6W no superó a E. Los dos están incluidos en los 86 y no se excluyen. Los criterios no se cambiaron después del piloto.
