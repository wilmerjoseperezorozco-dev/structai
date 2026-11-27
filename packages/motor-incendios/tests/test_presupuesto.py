"""Cantidades, presupuesto y costo por m² (#336 F9). Los precios son ILUSTRATIVOS (no son de ninguna base real)."""
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import hidraulica as h  # noqa: E402
from src import presupuesto as pr  # noqa: E402

D = h.Demanda(80.0, 50.0, 0.0, 0.0, fuente="ilustrativo")
T25, T32 = h.Tuberia("1in", 0.0266, 120.0), h.Tuberia("1-1/4in", 0.0351, 120.0)
TR = [((0, 0, 0), (5, 0, 0)), ((5, 0, 0), (5, 3, 0)), ((5, 0, 0), (5, -3, 0))]
RES = h.calcular(TR, (0, 0, 0), [(5, 3, 0), (5, -3, 0)], D,
                 {frozenset(TR[0]): T32, frozenset(TR[1]): T25, frozenset(TR[2]): T25}, {("te_lateral", "1in"): 1.5})


def _p(v, u="und"):
    return pr.PrecioItem(u, v, v, v, fuente="ilustrativo")


PRECIOS = {("tubo", "1in"): _p(30000, "m"), ("tubo", "1-1/4in"): _p(45000, "m"), ("te_lateral", "1in"): _p(20000),
           ("rociador",): _p(50000)}
SIN = {k: (1.0, 1.0, 1.0) for k in ("tubo", "te_lateral", "rociador", "riostra", "colgador", "anclaje", "bomba",
                                     "jockey", "cuarto_m2", "tanque_m3", "gabinete")}


def _dict(cs):
    return {c.clave: c.cantidad for c in cs}


def test_cantidades_desde_la_hidraulica():
    q = _dict(pr.cantidades(RES.tramos, 2))
    assert q == {("tubo", "1-1/4in"): 5.0, ("tubo", "1in"): 6.0, ("te_lateral", "1in"): 2, ("rociador",): 2}


def test_cantidades_de_soportes_bombas_tanque_y_declaradas():
    sop = [SimpleNamespace(n_lateral=1, n_longitudinal=1, n_colgadores=4), SimpleNamespace(n_lateral=0, n_longitudinal=0, n_colgadores=2)]
    cuarto = SimpleNamespace(principal=SimpleNamespace(bomba="B1"), area_m2=21.84)
    tq = SimpleNamespace(volumen_bruto_m3=81.8)
    q = _dict(pr.cantidades(RES.tramos, 2, sop, cuarto, tq, anclajes_por_riostra=2, anclajes_por_colgador=1,
                            declaradas=[pr.Cantidad(("gabinete",), "und", 3, "declarado")]))
    assert (q[("riostra",)], q[("colgador",)], q[("anclaje",)]) == (2, 6, 10)       # 2·2 + 6·1
    assert q[("bomba", "B1")] == 1 and q[("cuarto_m2",)] == 21.84 and q[("tanque_m3",)] == 81.8
    assert q[("gabinete",)] == 3
    with pytest.raises(ValueError, match="anclajes"):
        pr.cantidades(RES.tramos, 2, sop)


def test_presupuesto_determinista_a_mano():
    p = pr.presupuestar(pr.cantidades(RES.tramos, 2), PRECIOS, 100.0, SIN, n=200)
    assert p.total_moda == pytest.approx(5 * 45000 + 6 * 30000 + 2 * 20000 + 2 * 50000)   # 545 000
    assert p.p05 == pytest.approx(545000) and p.p95 == pytest.approx(545000)             # sin dispersión
    assert p.por_m2()["total_moda"] == pytest.approx(5450.0)
    assert not p.parcial and p.cobertura_partidas == 1.0
    assert p.participacion()[0][0] == ("tubo", "1-1/4in")                                # 41 %


def test_partida_sin_precio_no_se_inventa():
    precios = {k: v for k, v in PRECIOS.items() if k != ("rociador",)}
    p = pr.presupuestar(pr.cantidades(RES.tramos, 2), precios, 100.0, SIN, n=100)
    assert p.parcial and [c.clave for c in p.sin_precio] == [("rociador",)]
    assert p.total_moda == pytest.approx(445000) and p.cobertura_partidas == pytest.approx(0.75)


def test_unidades_e_incertidumbre_obligatorias():
    mal = {**PRECIOS, ("tubo", "1in"): _p(30000, "und")}
    with pytest.raises(ValueError, match="unidad"):
        pr.presupuestar(pr.cantidades(RES.tramos, 2), mal, 100.0, SIN)
    with pytest.raises(ValueError, match="incertidumbre"):
        pr.presupuestar(pr.cantidades(RES.tramos, 2), PRECIOS, 100.0, {"tubo": (1, 1, 1)})


def test_monte_carlo_y_cota_correlacionada():
    precios = {k: pr.PrecioItem(v.unidad, 0.8 * v.moda, v.moda, 1.3 * v.moda, "ilustrativo") for k, v in PRECIOS.items()}
    inc = dict(SIN, tubo=(1.02, 1.05, 1.10))
    p = pr.presupuestar(pr.cantidades(RES.tramos, 2), precios, 100.0, inc, n=20000)
    assert p.p05 < p.p50 < p.p95
    assert p.correlacionado_p05 <= p.p05 and p.correlacionado_p95 >= p.p95             # la independencia estrecha el rango
    pr2 = pr.presupuestar(pr.cantidades(RES.tramos, 2), precios, 100.0, inc, n=20000)
    assert pr2.p50 == p.p50                                                             # semilla fija: reproducible


def test_percentil_triangular():
    assert pr._tri_ppf(0.5, 0.0, 1.0, 2.0) == pytest.approx(1.0)
    assert pr._tri_ppf(0.0, 0.0, 1.0, 2.0) == pytest.approx(0.0) and pr._tri_ppf(1.0, 0.0, 1.0, 2.0) == pytest.approx(2.0)


def _muestras(n=9):
    verdad = {"a0": 80e6, "a1_QH": 40.0, "c1_area": 35000.0, "c2_pisos": 6e6, "c3_gabinetes": 4e6}
    out = []
    for k in range(n):
        d = {"area_m2": 2000 + 900 * k, "pisos": 3 + (k * 2) % 9, "gabinetes": 2 + (k * 5) % 7, "q_lpm": 1500 + 150 * (k % 4),
             "p_kpa": 400 + 60 * ((k * 3) % 5)}
        d["costo"] = (verdad["a0"] + verdad["a1_QH"] * d["q_lpm"] * d["p_kpa"] + verdad["c1_area"] * d["area_m2"]
                      + verdad["c2_pisos"] * d["pisos"] + verdad["c3_gabinetes"] * d["gabinetes"])
        out.append(d)
    return verdad, out


def test_modelo_fijo_mas_variable_recupera_coeficientes_conocidos():
    verdad, ms = _muestras()
    m = pr.ajustar_modelo(ms)
    for k, v in verdad.items():
        assert m.coef[k] == pytest.approx(v, rel=1e-6)
    assert m.r2 == pytest.approx(1.0) and m.error_loo_rel < 1e-6
    assert m.predecir(5000, 6, 4, 1800, 500) == pytest.approx(80e6 + 40 * 1800 * 500 + 35000 * 5000 + 6e6 * 6 + 4e6 * 4)


def test_modelo_exige_datos_suficientes_y_variados():
    _, ms = _muestras()
    with pytest.raises(ValueError, match="al menos"):
        pr.ajustar_modelo(ms[:6])
    iguales = [dict(d, pisos=5) for d in ms]
    with pytest.raises(ValueError, match="rango"):
        pr.ajustar_modelo(iguales)
