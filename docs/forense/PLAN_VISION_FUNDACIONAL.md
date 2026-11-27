# Visión forense con modelos fundacionales y 300–500 fotos (issue #213)

**Tesis (de Wilmer):** no hacen falta 100.000 fotos. Con un modelo fundacional congelado, una selección diversa y aprendizaje activo, unos cientos de etiquetas bien escogidas bastan. Este documento fija cómo se prueba y con qué datos y modelos se puede hacer **legalmente en un producto comercial**.

## 1. Licencias: qué datos y qué modelos se pueden usar

StructAI cobra planes (#210). Por eso solo entra al entrenamiento lo que permite uso comercial. Revisión del 2026-11-15:

| Recurso | Licencia | ¿Entrenar el modelo comercial? | Uso permitido |
|---|---|---|---|
| **SDNET2018**: 56.092 fotos de tablero de puente, muro y pavimento, fisura/sana. Clasificación, sin máscaras | CC BY 4.0 ([USU](https://digitalcommons.usu.edu/all_datasets/48), DOI 10.15142/T3TD19) | **Sí**, citando | Ya descargado y extraído en `C:\Users\wilme\dev\datasets\sdnet2018` |
| **Özgenel, Concrete Crack Segmentation**: 458 fotos de alta resolución **con máscaras** | CC BY 4.0 ([Mendeley](https://data.mendeley.com/datasets/jwsn7tfbrp/1)) | **Sí**, citando | Núcleo de la segmentación. Encaja justo con "300–500 fotos". Pendiente descargarlo |
| **RDD2022**: daño vial multinacional, cajas | Probablemente CC BY-SA 4.0 (no confirmado en la fuente oficial) | Sí, si se confirma; el modelo derivado queda bajo share-alike | Verificar en CRDDC2022 antes de descargar |
| **CODEBRIM**: 6 defectos de puentes, multietiqueta | Propia, **solo no comercial**. La cláusula 3 prohíbe obtener ganancia con modelos derivados | **No** | Solo como benchmark académico del proyecto de grado, sin entrar al modelo de producción. **No se descargó** |
| **DeepCrack**: 537 fotos con máscaras | "Restringido a investigación no comercial" | **No** | Igual que CODEBRIM |
| **Crack500**: 500 fotos con máscaras | Sin licencia explícita | **No**, hasta pedir permiso a los autores (Temple University) | — |
| Código **CT-crackseg** (ICIP 2023, ConvTransformer con bordes) | MIT | Sí (es código) | Clonado en `C:\Users\wilme\dev\terceros\CT-crackseg`. Requiere CUDA (torch 1.10 cu111): se entrena en Colab o Kaggle |
| Código **meta-learning-CODEBRIM** | Igual que CODEBRIM | No | No se clonó |
| **DINOv2** (Meta) | Apache-2.0 | Sí | Extractor congelado, pesos `facebook/dinov2-small` (88 MB) descargados |
| **SAM 2** (Meta) | Apache-2.0 | Sí | Acelera las máscaras: un clic o una caja da una máscara que el humano corrige |
| SAM 3 y DINOv3 | Licencias propias de Meta | Revisar antes de usar | — |
| **Ultralytics YOLO** (v8/11) | **AGPL-3.0**. Los modelos entrenados también quedan en AGPL | **No** sin licencia Enterprise | ⚠️ `packages/yolo/train.py` usa `ultralytics`: hay que migrar |
| **RF-DETR** (Roboflow), tamaños N–L | Apache-2.0 (XL y 2XL tienen otra licencia) | Sí | Reemplazo de YOLO para la detección (acero, vías, elementos) |

## 2. Experimento 1: ¿cuántas etiquetas hacen falta? (`scripts/forense/curar_subconjunto.py`)

1. **Datos:** 15.025 imágenes de SDNET2018, con un tope de 2.600 por estrato (superficie × fisura/sana).
2. **Prueba fija:** el 25 % estratificado se separa **antes** de seleccionar nada.
3. **Embeddings:** DINOv2-small congelado, token CLS normalizado, en CPU.
4. **Limpieza:** se quitan los casi duplicados del pool (coseno ≥ 0,97).
5. **Selección:** k-center greedy por estrato (core-set), con 70 % fisuras y 30 % sanas.
6. **Comparación:** contra **muestreo al azar** con la misma cuota. Una sonda lineal (regresión logística) se entrena con n = 25, 50, 100, 200, 400 y 800 etiquetas, con 5 semillas.
7. **Techo:** la misma sonda entrenada con **todo** el pool etiquetado.

**Lectura:**
- Si con 400 etiquetas se queda a ≤ 2 pp del techo, la tesis se sostiene para clasificación.
- Si k-center le gana al azar con n pequeño, la curaduría ahorra etiquetas.

Resultados en `RESULTADO_CURADURIA.md`.

## 3. Ruta para segmentación y detección

1. **Curar** 300–500 fotos por tarea con el mismo k-center sobre embeddings DINOv2, a partir de un pool que mezcle fotos propias de obra, Özgenel y SDNET.
   - Tareas: patologías del concreto, elementos estructurales, auditoría de acero y daño vial.
2. **Etiquetado acelerado con SAM 2:** puntos o caja producen la máscara, que el humano corrige.
   - Las fisuras finas son el punto débil de SAM. Ahí la máscara de partida la da el modelo de fisuras de la ronda anterior.
3. **Modelos:**
   - clasificación: sonda lineal sobre DINOv2;
   - segmentación de fisuras: CT-crackseg (MIT) o un decodificador liviano sobre parches DINOv2 congelados, entrenado con Özgenel más las propias;
   - detección: RF-DETR-S/M.
4. **Aprendizaje activo por rondas de 50:** se elige por incertidumbre (entropía o margen) combinada con diversidad (k-center sobre los dudosos).
   - Se para cuando la curva de validación se aplana: ganancia menor a 1 pp en dos rondas.
5. **Sintéticos:** fisuras procedurales sobre texturas sanas de SDNET y renders de elementos desde IFC (#211).
   - Solo se aceptan si mejoran sobre la prueba **real** fija.
6. **Criterio preregistrado por tarea, antes de entrenar:**
   - IoU de fisura ≥ 0,60 en la prueba real;
   - mAP50 ≥ 0,70 en detección;
   - IC bootstrap por imagen;
   - nada pasa a producción sin pasar por #169.

## 4. Pendientes que dependen de Wilmer

- Aprobar la descarga de Özgenel (CC BY 4.0) y confirmar la licencia de RDD2022.
- Decidir la migración de `packages/yolo` de Ultralytics (AGPL) a RF-DETR (Apache-2.0).
- Decidir si se escribe a los autores de Crack500 para pedir permiso de uso.
- Decidir el GPU de entrenamiento (Colab o Kaggle): este PC no tiene GPU.
