"""Conversión de etiquetas YOLO a COCO para RF-DETR (issue #217)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

Image = pytest.importorskip("PIL.Image")
import train_rfdetr as t  # noqa: E402


def _img(ruta, w=200, h=100):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h)).save(ruta)


def test_conversion_cajas_y_categorias(tmp_path):
    o = tmp_path / "dataset"
    _img(o / "images/train/a.jpg")
    (o / "labels/train").mkdir(parents=True)
    (o / "labels/train/a.txt").write_text("2 0.5 0.5 0.2 0.4\n6 0.1 0.1 0.1 0.1\n")
    _img(o / "images/train/sin_etiqueta.jpg")
    _img(o / "images/val/b.jpg")
    (o / "labels/val").mkdir(parents=True)
    (o / "labels/val/b.txt").write_text("0 0.25 0.75 0.5 0.5\n")

    r = t.yolo_a_coco(o, tmp_path / "coco")
    assert r == {"train": {"imagenes": 1, "cajas": 2, "sin_etiqueta": 1},
                 "valid": {"imagenes": 1, "cajas": 1, "sin_etiqueta": 0}}
    coco = json.loads((tmp_path / "coco/train/_annotations.coco.json").read_text())
    assert [c["id"] for c in coco["categories"]] == list(range(7))           # contiguas 0..6
    assert [c["name"] for c in coco["categories"]] == t.CLASES
    a = coco["annotations"][0]
    assert a["category_id"] == 2 and a["bbox"] == [80.0, 30.0, 40.0, 40.0]   # 200×100 px
    assert (tmp_path / "coco/train/a.jpg").exists() and not (tmp_path / "coco/train/sin_etiqueta.jpg").exists()


def test_clase_fuera_de_rango_falla(tmp_path):
    o = tmp_path / "dataset"
    _img(o / "images/train/a.jpg")
    (o / "labels/train").mkdir(parents=True)
    (o / "labels/train/a.txt").write_text("9 0.5 0.5 0.1 0.1\n")
    (o / "images/val").mkdir(parents=True)
    with pytest.raises(ValueError, match="fuera de rango"):
        t.yolo_a_coco(o, tmp_path / "coco")


def test_clases_coinciden_con_el_backend():
    main = open(os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps", "api", "main.py"), encoding="utf-8").read()
    bloque = main[main.index("CLASES_MODELO = ["):]
    bloque = bloque[:bloque.index("]")]
    assert [s.strip().strip('",') for s in bloque.splitlines()[1:] if s.strip()] == t.CLASES
