"""Indexación ICOCED: factores con esperados a mano sobre una serie sintética y coherencia con el archivo real."""
import json
from dataclasses import replace

import pytest

from src.economia_concreto import Economia
from src.indices_icoced import DOMINIO_POR_DEFECTO, factor, periodos_disponibles

SERIE = {"series": {"Barranquilla AM": {
    "Acero corrugado": {"2025-07": 100.0, "2026-07": 109.0},
    "Concreto común": {"2025-07": 200.0, "2026-07": 198.0},
    "Formaleta y accesorios": {"2025-07": 50.0, "2026-07": 55.0},
    "Servicios de preliminares y cimentación": {"2025-07": 80.0, "2026-07": 84.0},
    "Elementos metálicos": {"2025-07": 120.0, "2026-07": 126.0}}}}


@pytest.fixture
def ruta(tmp_path):
    r = tmp_path / "icoced.json"
    r.write_text(json.dumps(SERIE), encoding="utf-8")
    return r


def test_factor_es_el_cociente_de_indices(ruta):
    assert factor("Acero corrugado", "2025-07", "2026-07", ruta=ruta) == pytest.approx(1.09)
    assert factor("Concreto común", "2025-07", "2026-07", ruta=ruta) == pytest.approx(0.99)


def test_factor_identidad_e_inverso(ruta):
    assert factor("Acero corrugado", "2025-07", "2025-07", ruta=ruta) == 1.0
    assert factor("Acero corrugado", "2026-07", "2025-07", ruta=ruta) == pytest.approx(1 / 1.09)


def test_periodo_o_serie_inexistente_lanza_error(ruta):
    with pytest.raises(ValueError, match="no tiene el periodo"):
        factor("Acero corrugado", "2025-07", "2030-01", ruta=ruta)
    with pytest.raises(ValueError, match="sin serie"):
        factor("Acero corrugado", "2025-07", "2026-07", dominio="Atlantida", ruta=ruta)


def test_economia_indexar_a_aplica_cada_factor(ruta):
    e = Economia(fecha_precios="2025-07")
    n = e.indexar_a("2026-07", ruta=ruta)
    assert n.p_acero == pytest.approx(e.p_acero * 1.09) and n.mult_concreto == pytest.approx(e.mult_concreto * 0.99)
    assert n.p_encofrado == pytest.approx(e.p_encofrado * 1.10) and n.p_perforacion_m == pytest.approx(e.p_perforacion_m * 1.05)
    assert n.p_cabeza_anclaje == pytest.approx(e.p_cabeza_anclaje * 1.05)
    assert n.p_ceniza == e.p_ceniza and n.fe_cemento == e.fe_cemento and n.fecha_precios == "2026-07"


def test_economia_sin_fecha_no_se_puede_indexar(ruta):
    with pytest.raises(ValueError, match="fecha_precios"):
        Economia().indexar_a("2026-07", ruta=ruta)


def test_indexar_ida_y_vuelta_recupera_los_precios(ruta):
    e = Economia(fecha_precios="2025-07")
    r = e.indexar_a("2026-07", ruta=ruta).indexar_a("2025-07", ruta=ruta)
    assert r.p_acero == pytest.approx(e.p_acero) and r.p_perforacion_m == pytest.approx(e.p_perforacion_m) and r.fecha_precios == "2025-07"


def test_archivo_real_barranquilla_cubre_2022_a_2026():
    desde, hasta = periodos_disponibles(DOMINIO_POR_DEFECTO, "Acero corrugado")
    assert desde == "2022-01" and hasta >= "2026-09"
    e = replace(Economia(), fecha_precios="2025-07").indexar_a("2026-09")
    assert e.p_acero > 0 and e.fecha_precios == "2026-09"
