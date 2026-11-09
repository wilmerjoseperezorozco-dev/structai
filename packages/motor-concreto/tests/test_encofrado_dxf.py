import ezdxf
import pytest

from src import zapata as z
from src import zapata_troncopiramidal as t
from src.encofrado_dxf import exportar_dxf, paneles
from src.viga import Materiales


@pytest.fixture(scope="module")
def diseno():
    cargas = z.CargasZapata(P_serv=1500.0, P_u=2025.0)
    suelo = z.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5)
    r = t.optimizar(400.0, cargas, suelo, Materiales(28.0, 420.0, 420.0))
    assert r is not None
    return r


def test_area_de_paneles_coincide_con_el_motor_mas_el_pedestal(diseno):
    lista = paneles(diseno, 400.0, 500.0)
    zapata = sum(p.area_m2 for p in lista if p.nombre.startswith("Zapata"))
    assert zapata == pytest.approx(diseno.area_encofrado_m2, rel=1e-9)
    assert sum(p.area_m2 for p in lista if p.nombre.startswith("Pedestal")) == pytest.approx(4 * 0.4 * 0.5)


def test_dxf_se_relee_y_tiene_las_capas_y_el_area(tmp_path, diseno):
    r = exportar_dxf(diseno, 400.0, 500.0, tmp_path / "e.dxf")
    doc = ezdxf.readfile(tmp_path / "e.dxf")
    capas = {e.dxf.layer for e in doc.modelspace()}
    assert {"PLANTA", "ELEVACION", "PANELES", "TEXTO"} <= capas
    assert doc.header["$INSUNITS"] == 4
    assert sum(1 for e in doc.modelspace().query("LWPOLYLINE") if e.dxf.layer == "PANELES") == sum(p[1] for p in r["paneles"])
    assert r["area_total_m2"] > diseno.area_encofrado_m2


def test_no_exporta_un_diseno_que_no_cumple(tmp_path, diseno):
    malo = t.ResultadoTroncopiramidal(diseno.L_mm, 300, 300, False, "punzonamiento", 1, float("inf"), 1, 0, 0, "-", "-")
    with pytest.raises(ValueError):
        exportar_dxf(malo, 400.0, 500.0, tmp_path / "x.dxf")
