import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import licencias as lic


def test_clasificar_copyleft_y_permisivas():
    assert lic.clasificar("AGPL-3.0") == "copyleft fuerte (red): revisar"
    assert lic.clasificar("GNU Lesser General Public License v3 or later (LGPLv3+)") == "copyleft débil: revisar"
    assert lic.clasificar("Mozilla Public License 2.0 (MPL 2.0)") == "copyleft débil: revisar"
    assert lic.clasificar("GPL-3.0-only") == "copyleft fuerte: revisar"
    assert lic.clasificar("Apache-2.0 OR BSD-3-Clause") == "permisiva"


def test_sin_verificar_no_se_confunde_con_permisiva_ni_con_revisar():
    assert lic.clasificar("sin verificar (no instalado)") == "sin verificar"
    assert lic.clasificar("UNKNOWN") == "sin verificar"
    assert lic.clasificar("Licencia propietaria rara") == "revisar a mano"


def test_leer_requirements_ignora_comentarios_y_extras(tmp_path):
    r = tmp_path / "requirements.txt"
    r.write_text("# c\nfastapi==1\nuvicorn[standard]==2  # x\n\n-r otro.txt\nnumpy>=2\n", encoding="utf-8")
    assert lic.leer_requirements(r) == ["fastapi", "uvicorn", "numpy"]
