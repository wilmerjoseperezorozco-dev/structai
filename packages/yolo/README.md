# motor-yolo — Detección de elementos estructurales en obra

Retoma la idea original de StructAI: tomar una foto en obra y que el sistema
identifique elementos automáticamente. `apps/api/main.py` ya tiene la inferencia
real (`_load_onnx_model`, `_detect_onnx`), con el pre y posproceso en
`src/decodificar.py` (RF-DETR desde #217; YOLO heredado aún se lee). Lo único que falta es el modelo entrenado. Esta carpeta es el
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
con `dataset/data.yaml` y con `CLASES` en `train_rfdetr.py` (no tocar el orden).

Tiempo estimado para las 41 fotos restantes: 30–50 minutos.

## Licencia: por qué RF-DETR y no Ultralytics (issue #217)

Hasta #217 el entrenamiento usaba `ultralytics` (YOLOv11), que es **AGPL-3.0**: el código y también los modelos
entrenados con él quedan bajo AGPL, incompatible con un SaaS de código cerrado salvo licencia Enterprise. Se migró a
**RF-DETR** (Roboflow, **Apache-2.0** en los tamaños Nano, Small y Medium; XL/2XL tienen otra licencia y no se usan).
`train.py` se eliminó y los pesos `yolo11n.pt` (nunca estuvieron en git) ya no se usan. `scripts/inventario/verificar_licencias.py` corre en el CI y
falla si `ultralytics` (u otro paquete AGPL vetado) vuelve a aparecer en un `requirements*.txt` o `pyproject.toml`.

## Cómo entrenar (después de etiquetar)

El dataset etiquetado **no está en git** (las fotos son de obra real). Se copia a `packages/yolo/dataset/` con la
estructura YOLO de siempre (`images/{train,val}` + `labels/{train,val}`, la que escribe `etiquetar.py`).

```bash
cd packages/yolo
pip install "rfdetr[onnx]==1.12.1"
python train_rfdetr.py --solo-convertir      # revisa dataset_coco/ antes de gastar GPU
python train_rfdetr.py --tamano nano --epocas 60
```

`train_rfdetr.py`:
1. convierte las etiquetas YOLO a COCO (`dataset_coco/{train,valid}/_annotations.coco.json`, categorías contiguas
   0..6 en el orden de `CLASES_MODELO`; una prueba verifica que ese orden coincide con `apps/api/main.py`);
2. hace fine-tuning desde pesos COCO preentrenados;
3. exporta `model.onnx` y escribe `model.json` (arquitectura, clases, fecha, tamaño del dataset), del que `/detect`
   toma el campo `modelo_version`.

RF-DETR es un transformer: en CPU el fine-tuning es lento. Lo práctico es **Colab o Kaggle con GPU** (Nano cabe en
una T4). **Nunca se entrena en el servidor de producción**: producción solo carga el `.onnx` con `onnxruntime`.

Antes de desplegar: correr el `.onnx` con `onnxruntime` en local y confirmar que expone las salidas `dets` [1, Q, 4]
y `labels` [1, Q, C]. El decodificador (`src/decodificar.py`, solo numpy, con pruebas en `tests/`) replica el
posproceso oficial de RF-DETR: sigmoide por clase, top-k sobre (consulta, clase), umbral y sin NMS. Descarta la
última ranura ("sin objeto"). Un `model.onnx` YOLO viejo (una sola salida `[1, 4+nc, N]`) se sigue leyendo con NMS
por compatibilidad, pero no se entrenan modelos nuevos con Ultralytics.

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
