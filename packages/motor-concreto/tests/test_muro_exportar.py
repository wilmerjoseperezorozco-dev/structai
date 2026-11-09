import json

import ezdxf
import pytest

from src.muro_contencion import GeometriaMuro, Relleno, SueloApoyo, _poligono
from src.muro_exportar import cantidades_json, contorno, exportar_dxf, exportar_json, memoria
from src.muro_optimizador import CasoMuro, optimizar

C = CasoMuro(3.0, Relleno(18.0, 30.0, 5.0, 10.0), SueloApoyo(30.0, 200.0), a_max_g=0.15)


def test_el_contorno_tiene_el_area_de_concreto_del_verificador():
    for tip in ("estandar", "dentellon", "bandeja"):
        s = optimizar(C, tip)
        area = _poligono(contorno(s.geometria))[0]
        assert area == pytest.approx(s.diseno.concreto_m3_m, rel=2e-3), tip


def test_json_y_dxf_se_generan_y_se_leen(tmp_path):
    s = optimizar(C, "dentellon")
    j = exportar_json(C, s.geometria, s.diseno, tmp_path / "m.json")
    datos = json.loads(j.read_text(encoding="utf-8"))
    assert datos["cantidades"]["partidas"][0]["unidad"] == "m3" and datos["memoria"]["cumple"] is True
    assert any(v["estado"] == "HIPÓTESIS" for v in datos["memoria"]["verificaciones"]) and datos["memoria"]["no_verificado"]
    dxf = exportar_dxf(s.geometria, tmp_path / "m.dxf")
    pol = list(ezdxf.readfile(dxf).modelspace().query("LWPOLYLINE"))
    assert len(pol) == 1 and pol[0].closed


def test_memoria_incluye_sismo_solo_si_hay_a_max():
    s = optimizar(C, "estandar")
    assert any("seudoestático" in v["item"] for v in memoria(C, s.geometria, s.diseno)["verificaciones"])
