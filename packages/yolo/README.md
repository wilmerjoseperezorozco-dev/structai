# motor-yolo — Detección de precauciones de seguridad en obra

Retoma la idea original de StructAI: tomar una foto en obra y que el sistema
identifique elementos y riesgos automáticamente. `apps/api/main.py` ya tiene
el código de inferencia real (`_load_onnx_model`, `_detect_onnx`) escrito y
correcto — formato de salida YOLOv8 ONNX, decodificación de cajas, umbral de
confianza. Lo único que faltaba era el modelo entrenado. Esta carpeta es el
pipeline completo para producirlo.

## Estado (2026-08-01)

- **Dataset real**: 59 fotos de obra reales (`dataset/imagenes_originales/`),
  de un sitio de infraestructura hidrosanitaria — trabajadores con casco y
  arnés, excavaciones profundas, acero de refuerzo expuesto, escaleras de
  acceso. Copiadas desde `C:\Users\HP\Pictures\AAA` (no movidas — el original
  sigue intacto ahí).
- **Etiquetado**: pendiente (siguiente paso, ver abajo).
- **Modelo entrenado**: no existe todavía.

## Alcance deliberado: prueba de concepto de seguridad, no detector estructural

El código de `main.py` ya tenía un mapa de 9 clases estructurales (columna,
viga, muro, zapata...) pensado para cuando hubiera un dataset grande de
múltiples sitios. Con 59 fotos de un solo sitio, entrenar esas 9 clases
produciría un modelo sobreajustado a este sitio específico (mismo fondo,
misma luz, mismo color de concreto) — no generalizaría a fotos de otras
obras. Decisión tomada con el usuario: enfocar este primer modelo real en
**seguridad industrial (SGSST)**, que es honesto con lo que el dataset
realmente permite y conecta directo con el foco actual del piloto
(NSR-10/NTC/SGSST).

### Las 3 clases

| Clase | Qué detecta | Por qué importa (norma) |
|---|---|---|
| `trabajador_con_epp` | Persona con casco y arnés visibles | Resolución 0312 de 2019 — EPP mínimo obligatorio |
| `excavacion_profunda` | Zanja/excavación sin entibado visible | NSR-10 Título H / Resolución 0312 — riesgo de colapso en excavaciones |
| `acero_expuesto` | Malla o barras de refuerzo expuestas | Resolución 0312 — riesgo de empalamiento/punción, requiere protección (capuchones) |

Un jurado puede preguntar "¿por qué no detecta columnas y vigas también?" —
la respuesta honesta es esta tabla: con el dataset actual, 3 clases bien
entrenadas valen más que 9 clases mal entrenadas.

## Cómo etiquetar (siguiente paso — requiere al usuario)

1. Crear cuenta gratuita en [Roboflow](https://roboflow.com) (o CVAT/LabelImg
   si se prefiere una herramienta local).
2. Nuevo proyecto → tipo "Object Detection" → subir las 59 imágenes de
   `dataset/imagenes_originales/`.
3. Crear las 3 clases exactamente con estos nombres (deben coincidir con
   `CLASES_SEGURIDAD` en `train.py`):
   `trabajador_con_epp`, `excavacion_profunda`, `acero_expuesto`.
4. Dibujar las cajas en cada imagen donde aparezca cada clase (una imagen
   puede tener varias cajas de clases distintas).
5. Generar un dataset version → aplicar split 80/20 train/val (Roboflow lo
   hace automático) → export en formato **YOLOv8** (Roboflow genera
   `data.yaml` + carpetas `train/`, `valid/` ya en el formato que
   `ultralytics` espera).
6. Descargar el .zip exportado y descomprimirlo dentro de
   `packages/yolo/dataset/` (reemplaza el `data.yaml` de ejemplo de este
   repo por el que genera Roboflow).

Tiempo estimado para 59 imágenes × 3 clases: 30–60 minutos.

## Cómo entrenar (después de etiquetar)

```bash
cd packages/yolo
pip install ultralytics  # ya está en apps/api/requirements.txt, aquí es para entrenar local
python train.py
```

`train.py` hace fine-tuning desde pesos COCO preentrenados (`yolov8n.pt`) —
no entrena desde cero, así que converge rápido incluso con dataset pequeño
y sin GPU (más lento en CPU, pero viable para 59 imágenes: minutos, no
horas). Al terminar exporta automáticamente a ONNX en
`packages/yolo/model.onnx`.

**Este entrenamiento se corre en tu máquina local, nunca en DigitalOcean** —
`ultralytics`/`torch` para entrenar es pesado; el servidor de producción
solo necesita el archivo `.onnx` final (unos 6-12 MB), que se hornea en la
imagen Docker igual que el modelo de embeddings.

## Cómo se conecta al backend

`apps/api/main.py` ya busca el modelo en `packages/yolo/model.onnx` al
arrancar (`_load_onnx_model()`) — en cuanto el archivo exista ahí, `/detect`
deja de usar el stub automáticamente, sin cambiar código. El campo `modo` en
la respuesta ya distingue `"onnx"` (real) de `"stub"` (simulado), así que el
frontend nunca miente sobre qué está mostrando.

`SEGURIDAD_MAP` en `main.py` mapea cada clase de seguridad a un mensaje de
alerta con referencia normativa (ver sección siguiente del código) — a
diferencia de `CLASE_APU_MAP`, estas clases no sugieren un costo, sugieren
un riesgo.
