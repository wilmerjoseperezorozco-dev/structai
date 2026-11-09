import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import changelog as c  # noqa: E402

CHANGELOG = """# Historial

## [Sin publicar]

- algo pendiente

## [1.16.0] — Nombre

Periodo: 7-8 de noviembre.

### Agregado
- Una novedad con texto suficiente para no ser vacía.

## [1.15.0] — Anterior

### Agregado
- viejo
"""
MAIN = 'import x\nAPI_VERSION = "1.16.0"\n'


def test_clasificar_tipos_y_scope():
    assert c.clasificar("feat(redes): bombas") == ("Agregado", "`redes`: bombas")
    assert c.clasificar("fix: error") == ("Corregido", "error")
    assert c.clasificar("ci: matriz") == ("Mantenimiento", "matriz")
    assert c.clasificar("Actualizar cosas") == ("Sin clasificar", "Actualizar cosas")
    assert c.clasificar("wip: x")[0] == "Sin clasificar"


def test_agrupar_omite_merges_y_ordena():
    g = c.agrupar([("a1", "docs: guía"), ("b2", "feat: nuevo"), ("c3", "Merge branch x"), ("d4", "fix: bug")])
    assert list(g) == ["Agregado", "Corregido", "Documentación"]
    assert g["Agregado"] == ["nuevo (b2)"]


def test_seccion_delimita_por_siguiente_encabezado():
    titulo, cuerpo = c.seccion(CHANGELOG, "1.16.0")
    assert titulo.startswith("## [1.16.0]")
    assert "Una novedad" in cuerpo and "viejo" not in cuerpo
    assert c.seccion(CHANGELOG, "9.9.9") is None


def test_version_api():
    assert c.version_api(MAIN) == "1.16.0"
    assert c.version_api("nada") is None


def test_verificar_release_ok():
    assert c.verificar_release("v1.16.0", CHANGELOG, MAIN) == []


def test_verificar_release_detecta_problemas():
    assert any("vX.Y.Z" in p for p in c.verificar_release("1.16", CHANGELOG, MAIN))
    p = c.verificar_release("v1.17.0", CHANGELOG, MAIN)
    assert any("sección" in x for x in p) and any("API_VERSION" in x for x in p)
    vacio = "## [1.16.0] — X\n\n## [1.15.0]\n"
    assert any("vacía" in x for x in c.verificar_release("v1.16.0", vacio, MAIN))
