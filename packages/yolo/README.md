# motor-yolo — Detección de elementos estructurales en obra

Retoma la idea original de StructAI: tomar una foto en obra y que el sistema
identifique elementos automáticamente. `apps/api/main.py` ya tiene el código
de inferencia real (`_load_onnx_model`, `_detect_onnx`) escrito y correcto —
formato de salida YOLOv8/v11 ONNX, decodificación de cajas, NMS, umbral de
confianza. Lo único que falta es el modelo entrenado. Esta carpeta es el
pipeline completo para producirlo.

## Estado (2026-07-31)

- **Dataset real**: 59 fotos de un sitio de obra hidrosanitaria real
  (`dataset/imagenes_originales/`), copiadas desde `C:\Users\HP\Pictures\AAA`
  (no movidas — el original sigue intacto ahí).
- **Etiquetado**: **18 de 59 fotos ya etiquetadas** (`dataset/images/train` +
  `dataset/labels/train`, formato YOLO válido, verificado). Vienen de un
  trabajo previo en `tubara/yolov11-vision` (carpeta hermana fuera de este
  repo) que se consolidó acá. **Faltan 41 fotos por etiquetar** (29 en
  train, 12 en val — la carpeta `labels/val` está vacía).
- **Modelo entrenado**: **no existe todavía**, a pesar de que
  `tubara/yolov11-vision/resultados/` parecía sugerir lo contrario. Se
  verificó línea por línea: ese `reporte_detecciones.csv` es de correr
  `yolo11n.pt` **sin ajustar** (pesos base COCO) sobre las 59 fotos — por
  eso detecta clases genéricas de COCO (`person`, `car`, `orange`, `toilet`,
  `surfboard`...) y ninguna clase de obra civil. No hay ningún `runs/`,
  `weights/` ni `best.pt` en ningún lado — el entrenamiento nunca se
  completó.

## Alcance: 7 clases estructurales (no solo seguridad)

Sesión anterior había reducido el alcance a 3 clases de seguridad
industrial (`trabajador_con_epp`, `excavacion_profunda`, `acero_expuesto`)
por ser lo más honesto con un dataset de 59 fotos sin etiquetar. Al
descubrir que ya existían 18 fotos etiquetadas con un esquema más amplio de
**7 clases estructurales**, se decidió con el usuario aprovechar ese avance
real en vez de descartarlo:

| Clase (índice) | Qué detecta | Conecta con |
|---|---|---|
| `acero_refuerzo` (0) | Barras/malla de refuerzo | APU `C.ACE.G60` + recordatorio de seguridad (Res. 0312 — riesgo de empalamiento) |
| `viga` (1) | Viga estructural | APU `C.VIG.30X40` |
| `columna` (2) | Columna estructural | APU `C.COL.40X30` |
| `muro` (3) | Muro (material ambiguo desde foto) | Sin APU directo — ver nota abajo |
| `formaleta` (4) | Formaleta / encofrado | Sin APU directo (es un material dentro de otros APU, no una actividad propia) |
| `tuberia` (5) | Tubería | Sin APU directo (no se puede saber diámetro/uso exacto desde una foto) |
| `trabajador` (6) | Persona en obra | Recordatorio de seguridad (Res. 0312 — verificar EPP visible) |

**Por qué `muro`/`formaleta`/`tuberia` no sugieren un APU específico**: el
catálogo de costos distingue `muro_bloque_15` vs `muro_bloque_10` vs
`muro_concreto`, pero eso no se puede inferir de una sola foto sin saber el
material real — forzar un match específico sería un error de costo
silencioso. Se prefirió dejarlo sin sugerencia de precio antes que sugerir
uno adivinado. Ver `CLASE_APU_MAP` / `CLASE_DESCRIPCION_SIN_APU` en
`apps/api/main.py`.

**Sobre los recordatorios de seguridad**: `trabajador` y `acero_refuerzo`
disparan una nota con referencia normativa, pero deliberadamente formulada
como "verificar" — el modelo detecta que el elemento está presente, no si
cumple la norma (p.ej. no puede saber si el trabajador trae puesto el
casco). Ver `NOTAS_SEGURIDAD` en `apps/api/main.py`.

## Cómo etiquetar lo que falta (siguiente paso — requiere al usuario)

Ya existe una herramienta local de etiquetado en `etiquetar.py` (no hace
falta Roboflow ni cuenta externa):

```bash
cd packages/yolo
pip install opencv-python
python etiquetar.py                 # etiqueta dataset/images/train (pendientes)
python etiquetar.py dataset val      # etiqueta dataset/images/val (las 12, todas pendientes)
```

Controles: click+arrastrar dibuja una caja, `1`-`7` cambia de clase, `S`
guarda y pasa a la siguiente, `Z` deshace la última caja, `Q` sale (guarda
el progreso hecho hasta ahí — se puede retomar después, la herramienta salta
automáticamente las imágenes ya etiquetadas).

Clases y teclas: `1` acero_refuerzo · `2` viga · `3` columna · `4` muro ·
`5` formaleta · `6` tuberia · `7` trabajador — deben coincidir exactamente
con `dataset/data.yaml` (ya vienen correctas, no tocar el orden).

Tiempo estimado para las 41 fotos restantes: 30–50 minutos.

## Cómo entrenar (después de etiquetar)

```bash
cd packages/yolo
pip install ultralytics  # ya está en apps/api/requirements.txt, aquí es para entrenar local
python train.py
```

`train.py` hace fine-tuning desde pesos COCO preentrenados (`yolo11n.pt`,
ya está en esta carpeta) — no entrena desde cero, así que converge rápido
incluso con dataset pequeño y sin GPU (más lento en CPU, pero viable: minutos,
no horas). Al terminar exporta automáticamente a ONNX en
`packages/yolo/model.onnx`.

**Este entrenamiento se corre en tu máquina local, nunca en el servidor de producción (Google Cloud Run desde 2026-09-01, antes DigitalOcean)** —
`ultralytics`/`torch` para entrenar es pesado; el servidor de producción
solo necesita el archivo `.onnx` final (unos 6-12 MB), que se hornea en la
imagen Docker igual que el modelo de embeddings.

Antes de desplegar: verificar con `onnxruntime` localmente que la forma del
tensor de salida de YOLOv11 exportado sigue siendo `[1, 4+nc, N]` (misma
convención que YOLOv8, pero se debe comprobar con el modelo real exportado,
no asumir).

## Cómo se conecta al backend

`apps/api/main.py` ya busca el modelo en `packages/yolo/model.onnx` al
arrancar (`_load_onnx_model()`) — en cuanto el archivo exista ahí, `/detect`
deja de usar el stub automáticamente, sin cambiar código. El campo `modo` en
la respuesta ya distingue `"onnx"` (real) de `"stub"` (simulado), así que el
frontend nunca miente sobre qué está mostrando.

`CLASES_MODELO`, `CLASE_APU_MAP`, `CLASE_DESCRIPCION_SIN_APU` y
`NOTAS_SEGURIDAD` en `main.py` hacen el mapeo completo de cada clase
detectada a: nombre legible, APU sugerido (si aplica) y recordatorio de
seguridad (si aplica).
