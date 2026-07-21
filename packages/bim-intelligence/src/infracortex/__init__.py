"""
InfraCortex — motor científico multidisciplinario sobre modelos BIM (IFC).

Prototipo original desarrollado con asistencia de Gemini (sesión externa,
2026-07-20), portado a este monorepo. En el port se corrigieron 2 bugs
reales (ver core.py y train_pinn.py para el detalle de cada uno) y se
eliminó una clase `InfracortexVisionSensor` duplicada y sin uso que había
quedado en el archivo original de core (versión antigua superada por la
de vision.py, nadie la importaba).

Componentes:
  - core.py       → InfracortexEngine: lectura IFC, topología del nudo
                     viga-columna, ensamblaje de matrices de transformación.
  - loads.py       → Demanda sísmica y de gravedad real NSR-10 Títulos A/B
                     (espectro de diseño, período fundamental, cortante
                     basal, combinaciones de carga).
  - train_pinn.py   → Capacidad por cortante del nudo NSR-10 Título C
                     (C.21.7.4.1 / C.11.4.7.2 / C.11.3.1.1) + red neuronal
                     de regresión (MultidisciplinaryPINN — ver nota de
                     alcance en core.py, no es una PINN físicamente
                     informada en el sentido técnico estricto todavía).
  - vision.py       → InfracortexVisionSensor: detección de estribos vía
                     YOLO. Estado actual: usa detecciones sintéticas
                     (posiciones conocidas), no inferencia real — requiere
                     fine-tuning con dataset civil anotado para producción.

Estado: experimental, no conectado al producto (mismo criterio que el
resto de packages/bim-intelligence/). No expone router en apps/api todavía.
"""
