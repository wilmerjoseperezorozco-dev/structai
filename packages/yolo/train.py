"""
Entrena el detector de elementos estructurales (7 clases) desde pesos
YOLOv11n preentrenados en COCO. Corre en local, NUNCA en el servidor de
producción — ver README.md para el porqué.

Requiere que dataset/ tenga formato YOLO (data.yaml + images/{train,val} +
labels/{train,val}). El dataset ya trae 18/59 fotos etiquetadas — ver
README.md para completar el resto con etiquetar.py antes de entrenar.

Uso: python train.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET_YAML = ROOT / "dataset" / "data.yaml"
BASE_WEIGHTS = ROOT / "yolo11n.pt"
MODEL_OUT = ROOT / "model.onnx"

# Deben coincidir EXACTAMENTE en nombre y orden con datasets/obra_civil/data.yaml
# (índices 0-6) y con CLASES_MODELO en apps/api/main.py — un desajuste de
# orden hace que el modelo "acierte" internamente pero el backend etiquete
# mal la clase.
CLASES_ESTRUCTURA = [
    "acero_refuerzo",
    "viga",
    "columna",
    "muro",
    "formaleta",
    "tuberia",
    "trabajador",
]


def main() -> None:
    if not DATASET_YAML.exists():
        raise FileNotFoundError(
            f"No se encontró {DATASET_YAML}. Ver README.md, sección "
            "'Cómo etiquetar' — faltan fotos por etiquetar con etiquetar.py."
        )

    from ultralytics import YOLO

    # Fine-tuning desde pesos COCO preentrenados (yolo11n.pt) — no se entrena
    # desde cero. Con un dataset pequeño esto converge en minutos en CPU,
    # no horas, porque el modelo ya sabe "ver" formas/bordes/texturas
    # generales y solo tiene que aprender las 7 clases nuevas.
    modelo_base = str(BASE_WEIGHTS) if BASE_WEIGHTS.exists() else "yolo11n.pt"
    modelo = YOLO(modelo_base)

    resultados = modelo.train(
        data=str(DATASET_YAML),
        epochs=100,
        imgsz=640,
        patience=20,       # early stopping si no mejora en 20 épocas
        batch=8,            # dataset pequeño, batch chico evita batches vacíos
        project=str(ROOT / "runs"),
        name="estructura_civil",
        exist_ok=True,
    )

    print(f"\nEntrenamiento terminado. Métricas en: {resultados.save_dir}")

    # Exportar a ONNX — formato que _detect_onnx() en apps/api/main.py espera
    # (salida [1, 4+nc, N_predicciones]; YOLOv11 usa la misma cabeza
    # anchor-free que YOLOv8, así que la convención de salida es la misma,
    # pero verificar la forma real del tensor con onnxruntime después de
    # exportar antes de desplegar — no asumir sin comprobar).
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
