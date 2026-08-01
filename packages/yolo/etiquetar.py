"""
Herramienta de etiquetado para dataset YOLOv11 - Obra Civil.

Controles:
  Click izquierdo + arrastrar  = dibujar caja
  1-7                          = cambiar clase activa
  Z                            = deshacer ultima caja
  S                            = guardar y siguiente imagen
  ESPACIO                      = siguiente sin guardar
  Q                            = salir

Clases:
  1: acero_refuerzo  2: viga       3: columna
  4: muro            5: formaleta  6: tuberia
  7: trabajador
"""

import cv2
import os
import sys
from pathlib import Path

CLASES = [
    "acero_refuerzo",
    "viga",
    "columna",
    "muro",
    "formaleta",
    "tuberia",
    "trabajador",
]

COLORES = [
    (0, 0, 255),
    (0, 165, 255),
    (0, 255, 255),
    (0, 255, 0),
    (255, 165, 0),
    (255, 0, 0),
    (255, 0, 255),
]

drawing = False
ix, iy = 0, 0
boxes = []
clase_activa = 0
img_original = None
img_display = None


def mouse_callback(event, x, y, flags, param):
    global drawing, ix, iy, boxes, img_display

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp = img_display.copy()
        dibujar_cajas(temp)
        cv2.rectangle(temp, (ix, iy), (x, y), COLORES[clase_activa], 2)
        cv2.imshow("Etiquetar", temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = min(ix, x), min(iy, y)
        x2, y2 = max(ix, x), max(iy, y)
        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            boxes.append((clase_activa, x1, y1, x2, y2))
            redraw()


def dibujar_cajas(img):
    for cls_id, x1, y1, x2, y2 in boxes:
        color = COLORES[cls_id]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{cls_id}: {CLASES[cls_id]}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(img, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def redraw():
    global img_display
    img_display = img_original.copy()
    dibujar_cajas(img_display)
    info = f"Clase: {clase_activa + 1}-{CLASES[clase_activa]} | Cajas: {len(boxes)} | S=guardar Z=deshacer Q=salir"
    cv2.putText(img_display, info, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
    cv2.imshow("Etiquetar", img_display)


def guardar_labels(img_path, label_dir, img_h, img_w):
    label_path = os.path.join(label_dir, Path(img_path).stem + ".txt")
    with open(label_path, "w") as f:
        for cls_id, x1, y1, x2, y2 in boxes:
            cx = ((x1 + x2) / 2) / img_w
            cy = ((y1 + y2) / 2) / img_h
            bw = (x2 - x1) / img_w
            bh = (y2 - y1) / img_h
            f.write(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
    return label_path


def main():
    global clase_activa, boxes, img_original, img_display

    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "dataset"
    )
    split = sys.argv[2] if len(sys.argv) > 2 else "train"

    img_dir = os.path.join(dataset_dir, "images", split)
    label_dir = os.path.join(dataset_dir, "labels", split)
    os.makedirs(label_dir, exist_ok=True)

    extensiones = {".jpg", ".jpeg", ".png", ".bmp"}
    imagenes = sorted([f for f in Path(img_dir).iterdir() if f.suffix.lower() in extensiones])

    ya_etiquetadas = {f.stem for f in Path(label_dir).iterdir() if f.suffix == ".txt"}
    pendientes = [f for f in imagenes if f.stem not in ya_etiquetadas]

    print(f"=== Etiquetador YOLOv11 - Obra Civil ===")
    print(f"Carpeta: {img_dir}")
    print(f"Total imagenes: {len(imagenes)}")
    print(f"Ya etiquetadas: {len(ya_etiquetadas)}")
    print(f"Pendientes: {len(pendientes)}")
    print()
    print("Clases:")
    for i, c in enumerate(CLASES):
        print(f"  {i + 1}: {c}")
    print()
    print("Controles: click+arrastrar=caja | 1-7=clase | S=guardar | Z=deshacer | Q=salir")
    print()

    if not pendientes:
        print("Todas las imagenes ya estan etiquetadas!")
        return

    cv2.namedWindow("Etiquetar", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Etiquetar", mouse_callback)

    for idx, img_path in enumerate(pendientes):
        boxes = []
        print(f"[{idx + 1}/{len(pendientes)}] {img_path.name}")

        img_original = cv2.imread(str(img_path))
        if img_original is None:
            print("  Error leyendo imagen, saltando...")
            continue

        h, w = img_original.shape[:2]
        scale = min(1200 / w, 800 / h, 1.0)
        if scale < 1.0:
            img_original = cv2.resize(img_original, (int(w * scale), int(h * scale)))
            h, w = img_original.shape[:2]

        redraw()

        while True:
            key = cv2.waitKey(0) & 0xFF

            if key == ord("q"):
                cv2.destroyAllWindows()
                print(f"\nSesion terminada. Etiquetadas en esta sesion: {idx}")
                return

            elif ord("1") <= key <= ord("7"):
                clase_activa = key - ord("1")
                print(f"  Clase: {CLASES[clase_activa]}")
                redraw()

            elif key == ord("z") and boxes:
                removed = boxes.pop()
                print(f"  Deshecho: {CLASES[removed[0]]}")
                redraw()

            elif key == ord("s"):
                if boxes:
                    label_path = guardar_labels(img_path, label_dir, h, w)
                    print(f"  Guardado: {len(boxes)} cajas -> {Path(label_path).name}")
                else:
                    print("  Sin cajas, no se guardo")
                break

            elif key == ord(" "):
                print("  Saltada")
                break

    cv2.destroyAllWindows()
    total_labels = len(list(Path(label_dir).glob("*.txt")))
    print(f"\nEtiquetado completo! Total labels: {total_labels}/{len(imagenes)}")


if __name__ == "__main__":
    main()
