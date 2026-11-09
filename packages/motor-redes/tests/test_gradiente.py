"""Solver de redes por el método del gradiente (Todini y Pilati, 1988) con Hazen-Williams, estado permanente.
Referencias independientes: tubería simple a mano, reparto en paralelo en forma cerrada, Hardy-Cross escrito en el test
para una red de dos mallas, y propiedades físicas (continuidad en nudos, cierre de energía en mallas)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.gradiente import resolver_red

N_HW = 1.852


def _r(L, D, C):
    """Resistencia de Hazen-Williams en SI: h = r·Q^1.852."""
    return 10.67 * L / (C ** 1.852 * D ** 4.871)


def _nodo(id, z, demanda=0.0, carga=None):
    return dict(id=id, cota_m=z, demanda_m3s=demanda, carga_fija_m=carga)


def _tramo(id, a, b, L, D, C=130.0):
    return dict(id=id, desde=a, hasta=b, longitud_m=L, diametro_m=D, c_hw=C)


# ── Tubería simple ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tuberia_simple_coincide_con_hazen_williams_a_mano():
    r = resolver_red([_nodo("R", 50.0, carga=100.0), _nodo("N", 40.0, demanda=0.1)], [_tramo("p", "R", "N", 1000.0, 0.3)])
    h = _r(1000.0, 0.3, 130.0) * 0.1 ** N_HW
    assert r["tramos"]["p"]["caudal_m3s"] == pytest.approx(0.1, rel=1e-9)
    assert r["tramos"]["p"]["perdida_m"] == pytest.approx(h, rel=1e-9)
    assert r["nodos"]["N"]["carga_m"] == pytest.approx(100.0 - h, rel=1e-9)
    assert r["nodos"]["N"]["presion_m"] == pytest.approx(100.0 - h - 40.0, rel=1e-9)
    assert r["tramos"]["p"]["velocidad_ms"] == pytest.approx(0.1 / (math.pi * 0.3 ** 2 / 4), rel=1e-9)


def test_el_sentido_del_flujo_sigue_las_cargas_no_el_orden_de_los_nudos():
    # El embalse está en el extremo "hasta": el caudal sale negativo respecto del sentido declarado
    r = resolver_red([_nodo("N", 40.0, demanda=0.1), _nodo("R", 50.0, carga=100.0)], [_tramo("p", "R", "N", 1000.0, 0.3)])
    r2 = resolver_red([_nodo("R", 50.0, carga=100.0), _nodo("N", 40.0, demanda=0.1)], [_tramo("p", "N", "R", 1000.0, 0.3)])
    assert r["tramos"]["p"]["caudal_m3s"] == pytest.approx(0.1, rel=1e-9)
    assert r2["tramos"]["p"]["caudal_m3s"] == pytest.approx(-0.1, rel=1e-9)


# ── Tuberías en paralelo: forma cerrada ─────────────────────────────────────────────────────────────────────────────────
def test_paralelo_reparte_el_caudal_en_proporcion_inversa_a_la_raiz_de_la_resistencia():
    L, d1, d2, q = 800.0, 0.25, 0.35, 0.2
    r1, r2 = _r(L, d1, 130.0), _r(L, d2, 130.0)
    q1 = q / (1.0 + (r1 / r2) ** (1 / N_HW))     # r1 q1^n = r2 q2^n  →  q2 = q1 (r1/r2)^(1/n)
    red = resolver_red([_nodo("R", 30.0, carga=80.0), _nodo("N", 30.0, demanda=q)],
                       [_tramo("a", "R", "N", L, d1), _tramo("b", "R", "N", L, d2)])
    assert red["tramos"]["a"]["caudal_m3s"] == pytest.approx(q1, rel=1e-7)
    assert red["tramos"]["b"]["caudal_m3s"] == pytest.approx(q - q1, rel=1e-7)
    assert red["tramos"]["a"]["perdida_m"] == pytest.approx(red["tramos"]["b"]["perdida_m"], rel=1e-7)


# ── Dos mallas contra Hardy-Cross escrito en el test ────────────────────────────────────────────────────────────────────
def _red_dos_mallas():
    nodos = [_nodo("A", 10.0, carga=60.0), _nodo("B", 10.0), _nodo("C", 10.0), _nodo("D", 10.0, 0.010),
             _nodo("E", 10.0, 0.020), _nodo("F", 10.0, 0.030), _nodo("G", 10.0, 0.020)]
    tramos = [_tramo("AB", "A", "B", 500, 0.30), _tramo("BC", "B", "C", 400, 0.20), _tramo("CD", "C", "D", 300, 0.15),
              _tramo("EF", "E", "F", 400, 0.15), _tramo("FG", "F", "G", 300, 0.15), _tramo("BE", "B", "E", 300, 0.20),
              _tramo("CF", "C", "F", 300, 0.20), _tramo("DG", "D", "G", 400, 0.15)]
    return nodos, tramos


def _hardy_cross(tramos):
    q = {"AB": 0.08, "BC": 0.05, "CD": 0.015, "EF": 0.01, "FG": 0.015, "BE": 0.03, "CF": 0.035, "DG": 0.005}   # factible a mano
    r = {t["id"]: _r(t["longitud_m"], t["diametro_m"], t["c_hw"]) for t in tramos}
    mallas = [[("BC", 1), ("CF", 1), ("EF", -1), ("BE", -1)], [("CD", 1), ("DG", 1), ("FG", -1), ("CF", -1)]]
    for _ in range(500):
        for malla in mallas:
            num = sum(s * r[i] * abs(q[i]) ** (N_HW - 1) * q[i] for i, s in malla)
            den = sum(N_HW * r[i] * abs(q[i]) ** (N_HW - 1) for i, s in malla)
            dq = -num / den
            for i, s in malla:
                q[i] += s * dq
    return q


def test_dos_mallas_coincide_con_hardy_cross_independiente():
    nodos, tramos = _red_dos_mallas()
    q_hc = _hardy_cross(tramos)
    red = resolver_red(nodos, tramos)
    for t in tramos:
        assert red["tramos"][t["id"]]["caudal_m3s"] == pytest.approx(q_hc[t["id"]], rel=1e-6, abs=1e-9)


def test_continuidad_en_cada_nudo_y_cierre_de_energia_en_mallas():
    nodos, tramos = _red_dos_mallas()
    red = resolver_red(nodos, tramos)
    for n in nodos:
        if n["carga_fija_m"] is not None:
            continue
        entra = sum(red["tramos"][t["id"]]["caudal_m3s"] for t in tramos if t["hasta"] == n["id"])
        sale = sum(red["tramos"][t["id"]]["caudal_m3s"] for t in tramos if t["desde"] == n["id"])
        assert entra - sale == pytest.approx(n["demanda_m3s"], abs=1e-9)
    p = lambda i: red["tramos"][i]["perdida_m"]
    assert p("BC") + p("CF") - p("EF") - p("BE") == pytest.approx(0.0, abs=1e-7)
    assert p("CD") + p("DG") - p("FG") - p("CF") == pytest.approx(0.0, abs=1e-7)
    assert red["residuo_continuidad_m3s"] < 1e-9 and red["iteraciones"] >= 1


# ── Propiedades ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_la_presion_es_invariante_a_un_desplazamiento_vertical_de_cotas_y_cargas():
    nodos, tramos = _red_dos_mallas()
    base = resolver_red(nodos, tramos)
    desplazados = [{**n, "cota_m": n["cota_m"] + 250.0, "carga_fija_m": None if n["carga_fija_m"] is None else n["carga_fija_m"] + 250.0}
                   for n in nodos]
    alt = resolver_red(desplazados, tramos)
    for n in nodos:
        assert alt["nodos"][n["id"]]["presion_m"] == pytest.approx(base["nodos"][n["id"]]["presion_m"], abs=1e-9)


def test_mas_demanda_baja_la_presion_minima():
    def pmin(escala):
        nodos, tramos = _red_dos_mallas()
        nodos = [{**n, "demanda_m3s": n["demanda_m3s"] * escala} for n in nodos]
        return min(v["presion_m"] for k, v in resolver_red(nodos, tramos)["nodos"].items() if k != "A")
    vals = [pmin(e) for e in (0.5, 1.0, 2.0, 3.0)]
    assert all(b < a for a, b in zip(vals, vals[1:]))


def test_el_caudal_total_que_sale_del_embalse_iguala_la_demanda():
    nodos, tramos = _red_dos_mallas()
    red = resolver_red(nodos, tramos)
    assert red["nodos"]["A"]["caudal_neto_m3s"] == pytest.approx(0.08, rel=1e-9)


def test_un_nudo_con_demanda_nula_aislado_en_la_red_conectada_funciona():
    red = resolver_red([_nodo("R", 0.0, carga=50.0), _nodo("N", 0.0, 0.0)], [_tramo("p", "R", "N", 500.0, 0.2)])
    assert red["nodos"]["N"]["carga_m"] == pytest.approx(50.0, abs=1e-6)


# ── Fallos explícitos ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_red_sin_nudo_de_carga_fija_se_rechaza():
    with pytest.raises(ValueError, match="carga fija"):
        resolver_red([_nodo("A", 0.0, 0.01), _nodo("B", 0.0, 0.01)], [_tramo("p", "A", "B", 100.0, 0.1)])


def test_componente_desconectada_de_todo_embalse_se_rechaza():
    nodos = [_nodo("R", 0.0, carga=50.0), _nodo("N", 0.0, 0.01), _nodo("X", 0.0, 0.01), _nodo("Y", 0.0, 0.01)]
    tramos = [_tramo("p", "R", "N", 100.0, 0.1), _tramo("q", "X", "Y", 100.0, 0.1)]
    with pytest.raises(ValueError, match="conectad"):
        resolver_red(nodos, tramos)


@pytest.mark.parametrize("cambio", [dict(longitud_m=0.0), dict(longitud_m=-5.0), dict(diametro_m=0.0), dict(c_hw=0.0),
                                    dict(diametro_m=float("nan")), dict(c_hw=float("inf")), dict(desde="Z"), dict(hasta="R")])
def test_tramos_invalidos_se_rechazan(cambio):
    t = {**_tramo("p", "R", "N", 100.0, 0.1), **cambio}
    with pytest.raises(ValueError):
        resolver_red([_nodo("R", 0.0, carga=50.0), _nodo("N", 0.0, 0.01)], [t])


@pytest.mark.parametrize("cambio", [dict(demanda_m3s=-0.1), dict(demanda_m3s=float("nan")), dict(cota_m=float("inf")),
                                    dict(carga_fija_m=float("nan"))])
def test_nudos_invalidos_se_rechazan(cambio):
    n = {**_nodo("N", 0.0, 0.01), **cambio}
    with pytest.raises(ValueError):
        resolver_red([_nodo("R", 0.0, carga=50.0), n], [_tramo("p", "R", "N", 100.0, 0.1)])


def test_identificadores_duplicados_y_listas_vacias_se_rechazan():
    with pytest.raises(ValueError, match="duplicad"):
        resolver_red([_nodo("R", 0.0, carga=50.0), _nodo("R", 0.0, 0.01)], [_tramo("p", "R", "R", 100.0, 0.1)])
    with pytest.raises(ValueError):
        resolver_red([], [])
    with pytest.raises(ValueError):
        resolver_red([_nodo("R", 0.0, carga=50.0)], [])


def test_si_no_converge_en_el_maximo_de_iteraciones_falla_con_mensaje_claro():
    nodos, tramos = _red_dos_mallas()
    with pytest.raises(ValueError, match="converge"):
        resolver_red(nodos, tramos, max_iteraciones=1)


# ── Hallazgos de la revisión adversarial ────────────────────────────────────────────────────────────────────────────────
def test_nudo_de_carga_fija_con_demanda_se_rechaza_en_vez_de_descartarla():
    nodos = [_nodo("R", 0, carga=100.0), _nodo("S", 0, 5.0, carga=90.0), _nodo("a", 0, 0.01)]
    with pytest.raises(ValueError, match="carga fija.*demanda|demanda.*carga fija"):
        resolver_red(nodos, [_tramo("t", "R", "a", 100, 0.2), _tramo("u", "a", "S", 100, 0.2)])


@pytest.mark.parametrize("L,D", [(1.0, 5.0), (10.0, 1.0), (100.0, 0.3), (100.0, 0.2)])
def test_dos_embalses_a_igual_carga_no_inventan_caudal(L, D):
    nodos = [_nodo("R", 0, carga=10.0), _nodo("S", 0, carga=10.0), _nodo("a", 0)]
    red = resolver_red(nodos, [_tramo("t", "R", "a", L, D), _tramo("u", "a", "S", L, D)])
    # Resolución numérica: una pérdida menor que ~1e-12 m queda bajo el redondeo de una carga de 10 m (eps·H ≈ 2e-15 m);
    # por eso se exige que la pérdida sea indistinguible de cero, no que el caudal lo sea (con L=1 m y D=5 m, 1e-5 m³/s pierde 1e-15 m).
    assert abs(red["tramos"]["t"]["perdida_m"]) < 1e-12
    assert abs(red["tramos"]["t"]["caudal_m3s"]) < 1e-4


def test_demanda_minuscula_se_resuelve_con_su_caudal():
    red = resolver_red([_nodo("R", 0, carga=50.0), _nodo("N", 0, 1e-11)], [_tramo("p", "R", "N", 100, 0.2)])
    assert red["tramos"]["p"]["caudal_m3s"] == pytest.approx(1e-11, rel=1e-3)


def test_red_inviable_por_demanda_excesiva_dice_que_es_inviable():
    with pytest.raises(ValueError, match="inviable|converge"):
        resolver_red([_nodo("R", 0, carga=100.0), _nodo("a", 0, 2.0)], [_tramo("t", "R", "a", 1000, 0.1)])


@pytest.mark.parametrize("nodos,tramos", [
    ([dict(id=1, cota_m=0, demanda_m3s=0, carga_fija_m=50), _nodo("b", 0, 0.01)], [_tramo("p", 1, "b", 10, 0.1)]),
    ([_nodo("R", 0, carga=50.0), _nodo("b", 0, 0.01)], [{k: v for k, v in _tramo("p", "R", "b", 10, 0.1).items() if k != "c_hw"}]),
    ([{k: v for k, v in _nodo("R", 0, carga=50.0).items() if k != "cota_m"}, _nodo("b", 0, 0.01)], [_tramo("p", "R", "b", 10, 0.1)]),
])
def test_entradas_mal_formadas_dan_valueerror_no_typeerror_ni_keyerror(nodos, tramos):
    with pytest.raises(ValueError):
        resolver_red(nodos, tramos)
