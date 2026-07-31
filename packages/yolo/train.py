"""
Entrena el detector de precauciones de seguridad (prueba de concepto,
3 clases) desde pesos YOLOv8n preentrenados en COCO. Corre en local, NUNCA
en el servidor de producción — ver README.md para el porqué.

Requiere que dataset/ ya tenga el formato exportado por Roboflow
(data.yaml + train/images, train/labels, valid/images, valid/labels)
después de etiquetar las imágenes de dataset/imagenes_originales/.

Uso: python train.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET_YAML = ROOT / "dataset" / "data.yaml"
MODEL_OUT = ROOT / "model.onnx"

# Deben coincidir exactamente con los nombres de clase usados al etiquetar
# en Roboflow (ver README.md) y con SEGURIDAD_MAP en apps/api/main.py.
CLASES_SEGURIDAD = ["trabajador_con_epp", "excavacion_profunda", "acero_expuesto"]


def main() -> None:
    if not DATASET_YAML.exists():
        raise FileNotFoundError(
            f"No se encontró {DATASET_YAML}. Falta etiquetar y exportar el dataset "
            "desde Roboflow primero — ver README.md, sección 'Cómo etiquetar'."
        )

    from ultralytics import YOLO

    # Fine-tuning desde pesos COCO preentrenados (yolov8n.pt) — no se entrena
    # desde cero. Con un dataset de ~59 imágenes esto converge en minutos en
    # CPU, no horas, porque el modelo ya sabe "ver" formas/bordes/texturas
    # generales y solo tiene que aprender las 3 clases nuevas.
    modelo = YOLO("yolov8n.pt")

    resultados = modelo.train(
        data=str(DATASET_YAML),
        epochs=100,
        imgsz=640,
        patience=20,       # early stopping si no mejora en 20 épocas
        batch=8,            # dataset pequeño, batch chico evita batches vacíos
        project=str(ROOT / "runs"),
        name="seguridad_epp",
        exist_ok=True,
    )

    print(f"\nEntrenamiento terminado. Métricas en: {resultados.save_dir}")

    # Exportar a ONNX — formato que _detect_onnx() en apps/api/main.py espera
    # (salida [1, 4+nc, 8400], opset por defecto de ultralytics es compatible
    # con onnxruntime==1.19.2 ya instalado en requirements.txt).
    mejor_peso = Path(resultados.save_dir) / "weights" / "best.pt"
    modelo_entrenado = YOLO(str(mejor_peso))
    ruta_onnx = modelo_entrenado.export(format="onnx", imgsz=640, simplify=True)

    import shutil
    shutil.copy(ruta_onnx, MODEL_OUT)
    print(f"\n✓ Modelo exportado a {MODEL_OUT}")
    print("Siguiente paso: probar localmente con apps/api antes de desplegar")
    print("  (packages/yolo/model.onnx ya es la ruta que main.py busca al arrancar).")


if __name__ == "__main__":
    main()
