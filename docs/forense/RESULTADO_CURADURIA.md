# Resultado: ¿cuántas etiquetas hacen falta? (issue #213, 2026-11-15)

**Montaje:**
- **Datos:** SDNET2018 (CC BY 4.0). 15.025 imágenes, con un tope de 2.600 por estrato (superficie × fisura/sana).
- **Prueba:** fija, el 25 % estratificado, separada antes de seleccionar.
- **Pool:** 10.793 imágenes, después de quitar casi duplicados (coseno ≥ 0,97).
- **Modelo:** DINOv2-small congelado (token CLS) más sonda lineal (regresión logística balanceada), en CPU.
- **Repeticiones:** 5 semillas por punto.
- **Script:** `scripts/forense/curar_subconjunto.py`.

**Techo:** etiquetando las 10.793 imágenes del pool, el **F1 de fisura es 0,803**.

## F1 de fisura (media ± desviación estándar, 5 semillas), cuota 70 % fisuras y 30 % sanas

| Etiquetas | Típicos (k-means + medoide) | Azar | k-center (core-set) |
|---|---|---|---|
| 25 | 0,712 | 0,723 | 0,657 |
| 100 | **0,735 ± 0,003** | 0,728 ± 0,023 | 0,659 |
| 400 | **0,767 ± 0,002** | 0,753 ± 0,004 | 0,689 |
| 800 | **0,774 ± 0,002** | 0,767 ± 0,007 | 0,705 |

Con cuota 50/50 el resultado es parecido: con 400 etiquetas, típicos llega a 0,767 ± 0,004 y azar a 0,747 ± 0,010.

## Lectura

1. **La tesis se sostiene para clasificación.**
   - Con **400 etiquetas**, el 3,7 % del pool, se llega a **0,767**: el 96 % del techo, a 3,6 pp.
   - Pasar de 400 a 800 etiquetas solo suma 0,7 pp. Lo que sigue limitando es el extractor congelado y el ruido de etiquetas de SDNET, no la cantidad de fotos.
2. **Cómo se elige importa, y no de la forma esperada.**
   - **k-center (máxima diversidad) es peor que el azar.** Escoge las imágenes atípicas, y el clasificador termina llamando "fisura" a casi todo: F1 macro de 0,40 con 25–100 etiquetas.
   - Elegir los **típicos** de cada grupo le gana al azar con 100 etiquetas o más, por 0,7 a 2 pp, y con **5 a 10 veces menos varianza**: es reproducible.
   - Coincide con lo reportado para presupuesto bajo (Hacohen et al., ICML 2022, "Active learning on a budget"): con pocas etiquetas sirve lo representativo, y con muchas, lo diverso.
3. **Decisión:**
   - La primera tanda de etiquetado se elige con **típicos**: `--metodo-final tipicos`, 400 fotos, archivo `seleccion_para_etiquetar.csv`.
   - Las rondas siguientes de aprendizaje activo mezclan incertidumbre y diversidad sobre los casos dudosos.

## Límites

- Es clasificación fisura/sana, no segmentación. Para máscaras el siguiente paso es Özgenel (CC BY 4.0, 458 fotos con máscara).
- SDNET tiene ruido de etiquetas conocido (fisuras finas, sombras), así que el techo de 0,80 es el de este extractor y esta sonda, no un límite del problema.
- **Siguiente comparación:** afinar DINOv2 o un CNN pequeño con 400 etiquetas, frente a la sonda congelada. Requiere GPU.
