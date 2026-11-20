"""
Entrena el detector de elementos de obra (7 clases) con RF-DETR (Roboflow, Apache-2.0) y lo exporta a ONNX
(issue #217). Reemplaza a train.py (Ultralytics YOLO, AGPL-3.0: el modelo entrenado también quedaría bajo AGPL).

Corre en local o en Colab/Kaggle con GPU, NUNCA en el servidor de producción; producción solo carga el .onnx con
onnxruntime (ver apps/api/main.py → _detect_onnx y src/decodificar.py).

Pasos:
  1. Convierte dataset/ (formato YOLO: images/{train,val} + labels/{train,val}) a COCO, el formato que lee RF-DETR:
     dataset_coco/{train,valid}/_annotations.coco.json con categorías CONTIGUAS 0..6 en el orden de CLASES.
     Con ids contiguos, la última ranura de salida del modelo es "sin objeto" y el decodificador la descarta
     (clase_fondo=-1).
  2. Fine-tuning desde pesos COCO preentrenados (RF-DETR Nano/Small: Apache-2.0; XL/2XL tienen otra licencia y NO
     se usan).
  3. Exporta a ONNX → packages/yolo/model.onnx + model.json (clases, resolución, versión).

Uso:
  pip install "rfdetr[onnx]==1.12.1"
  python train_rfdetr.py --tamano nano --epocas 60
  python train_rfdetr.py --solo-convertir         # solo genera dataset_coco/ (para revisar)
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET_YOLO = ROOT / "dataset"
DATASET_COCO = ROOT / "dataset_coco"
MODEL_OUT = ROOT / "model.onnx"

# Mismo orden que CLASES_MODELO en apps/api/main.py: un desajuste etiqueta mal cada detección.
CLASES = ["acero_refuerzo", "viga", "columna", "muro", "formaleta", "tuberia", "trabajador"]
TAMANOS = {"nano": "RFDETRNano", "small": "RFDETRSmall", "medium": "RFDETRMedium"}   # Apache-2.0
EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def _tam_imagen(ruta: Path) -> tuple[int, int]:
    from PIL import Image
    with Image.open(ruta) as im:
        return im.size   # (ancho, alto)


def yolo_a_coco(origen: Path = DATASET_YOLO, destino: Path = DATASET_COCO, clases=CLASES) -> dict:
    """Convierte etiquetas YOLO (clase cx cy w h normalizados) a COCO (x, y, w, h en píxeles).
    Solo incluye imágenes con archivo de etiquetas (las no etiquetadas se omiten y se cuentan)."""
    resumen = {}
    for sub_yolo, sub_coco in (("train", "train"), ("val", "valid")):
        imgs_dir, lbl_dir = origen / "images" / sub_yolo, origen / "labels" / sub_yolo
        out = destino / sub_coco
        out.mkdir(parents=True, exist_ok=True)
        coco = {"images": [], "annotations": [], "info": {"description": "StructAI obra (#217)"},
                "categories": [{"id": i, "name": n, "supercategory": "obra"} for i, n in enumerate(clases)]}
        omitidas = 0
        for img in sorted(p for p in imgs_dir.glob("*") if p.suffix.lower() in EXTS):
            lbl = lbl_dir / f"{img.stem}.txt"
            if not lbl.exists():
                omitidas += 1
                continue
            w, h = _tam_imagen(img)
            iid = len(coco["images"])
            coco["images"].append({"id": iid, "file_name": img.name, "width": w, "height": h})
            shutil.copy2(img, out / img.name)
            for linea in lbl.read_text(encoding="utf-8").splitlines():
                partes = linea.split()
                if len(partes) != 5:
                    continue
                c, cx, cy, bw, bh = int(partes[0]), *map(float, partes[1:])
                if not 0 <= c < len(clases):
                    raise ValueError(f"{lbl}: clase {c} fuera de rango 0..{len(clases) - 1}")
                coco["annotations"].append({
                    "id": len(coco["annotations"]), "image_id": iid, "category_id": c,
                    "bbox": [round((cx - bw / 2) * w, 2), round((cy - bh / 2) * h, 2), round(bw * w, 2), round(bh * h, 2)],
                    "area": round(bw * w * bh * h, 2), "iscrowd": 0})
        (out / "_annotations.coco.json").write_text(json.dumps(coco, ensure_ascii=False), encoding="utf-8")
        resumen[sub_coco] = {"imagenes": len(coco["images"]), "cajas": len(coco["annotations"]), "sin_etiqueta": omitidas}
    return resumen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tamano", choices=sorted(TAMANOS), default="nano")
    ap.add_argument("--epocas", type=int, default=60)
    ap.add_argument("--lote", type=int, default=4)
    ap.add_argument("--acumular", type=int, default=4, help="pasos de acumulación de gradiente (lote efectivo = lote×acumular)")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--solo-convertir", action="store_true")
    a = ap.parse_args()

    if not (DATASET_YOLO / "images" / "train").exists():
        raise SystemExit(f"No existe {DATASET_YOLO}/images/train. Ver README.md: el dataset etiquetado no está en git.")
    resumen = yolo_a_coco()
    print("dataset COCO:", json.dumps(resumen, ensure_ascii=False))
    if a.solo_convertir:
        return
    if resumen["valid"]["imagenes"] == 0:
        raise SystemExit("valid/ quedó vacío: etiqueta las fotos de validación antes de entrenar (etiquetar.py dataset val).")

    import rfdetr
    clase_modelo = getattr(rfdetr, TAMANOS[a.tamano])
    modelo = clase_modelo()                       # pesos COCO preentrenados (Apache-2.0)
    salida = ROOT / "runs_rfdetr" / a.tamano
    modelo.train(dataset_dir=str(DATASET_COCO), epochs=a.epocas, batch_size=a.lote, grad_accum_steps=a.acumular,
                 lr=a.lr, output_dir=str(salida))
    ruta_onnx = Path(modelo.export(output_dir=str(salida / "onnx")) or next((salida / "onnx").glob("*.onnx")))
    shutil.copy(ruta_onnx, MODEL_OUT)
    (ROOT / "model.json").write_text(json.dumps({
        "formato": "detr", "arquitectura": f"RF-DETR {a.tamano}", "licencia": "Apache-2.0",
        "rfdetr_version": getattr(rfdetr, "__version__", "?"), "clases": CLASES, "clase_fondo": -1,
        "epocas": a.epocas, "fecha": date.today().isoformat(), "dataset": resumen}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"✓ {MODEL_OUT} + model.json. Verificar con onnxruntime antes de desplegar (salidas 'dets' y 'labels').")


if __name__ == "__main__":
    main()
