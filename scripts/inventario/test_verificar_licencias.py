import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import verificar_licencias as v


def test_nombre_de_requisito():
    assert v._nombre_req("ultralytics>=8.0.0") == "ultralytics"
    assert v._nombre_req("PyMuPDF==1.24 ; python_version>'3.9'") == "pymupdf"
    assert v._nombre_req("rfdetr[onnx]==1.12.1  # Apache-2.0") == "rfdetr"
    assert v._nombre_req("# ultralytics comentado") is None
    assert v._nombre_req("-r requirements.txt") is None


def test_detecta_vetado_en_requirements_y_pyproject(tmp_path, monkeypatch):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "requirements.txt").write_text("numpy\nUltralytics>=8\n", encoding="utf-8")
    (tmp_path / "pkg" / "pyproject.toml").write_text(
        '[project]\nname="x"\ndependencies=["pillow"]\n[project.optional-dependencies]\npdf=["pymupdf"]\n',
        encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "requirements.txt").write_text("ultralytics\n", encoding="utf-8")   # ignorado
    monkeypatch.setattr(v, "RAIZ", tmp_path)
    assert sorted((r, d) for r, d, _ in v.hallazgos()) == [("pkg/pyproject.toml", "pymupdf"),
                                                           ("pkg/requirements.txt", "ultralytics")]


def test_repositorio_actual_limpio():
    assert v.hallazgos() == []
