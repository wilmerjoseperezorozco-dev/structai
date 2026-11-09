"""Despiece 1D: traslapos, optimalidad en casos con solución conocida y dominancia sobre el primer ajuste."""
import pytest

from src.despiece_proyecto import dividir_con_traslapo, despiece_por_diametro, resolver_ilp

COM = [6.0, 9.0, 12.0]


def test_sin_empalme_si_cabe():
    assert dividir_con_traslapo(5.6, 12.0, 0.8) == [5.6]


def test_un_empalme_suma_un_traslapo():
    p = dividir_con_traslapo(14.0, 12.0, 0.8)
    assert sum(p) == pytest.approx(14.8) and max(p) <= 12.0 + 1e-9 and len(p) == 2


def test_dos_empalmes():
    p = dividir_con_traslapo(30.0, 12.0, 0.8)
    assert len(p) == 3 and sum(p) == pytest.approx(31.6)


def test_traslapo_invalido():
    with pytest.raises(ValueError):
        dividir_con_traslapo(5.0, 0.5, 0.8)


def test_ilp_caso_exacto_sin_desperdicio():
    barras, ok = resolver_ilp([6.0, 6.0, 3.0, 3.0], COM)
    assert ok and sum(l * n for l, n in barras.items()) == pytest.approx(18.0)


def test_ilp_cubre_la_demanda_con_cota_superior():
    # cobertura y cota superior (30 m: 4 piezas de 4 + 2 de 5 caben en 3 barras de 9 + 1 de 6... basta con no pasar de 30)
    piezas = [4.0] * 4 + [5.0] * 2
    barras, ok = resolver_ilp(piezas, COM)
    comprada = sum(l * n for l, n in barras.items())
    assert ok and comprada >= sum(piezas) - 1e-9 and comprada <= 30.0 + 1e-9


def test_ilp_nunca_peor_que_ffd():
    res = despiece_por_diametro([("5", 5.6), ("5", 5.6), ("5", 4.1), ("5", 3.3), ("5", 2.8), ("5", 14.0), ("6", 7.2), ("6", 7.2)], COM)
    for r in res:
        assert r.comprada_ilp_m <= r.comprada_ffd_m + 1e-9
        assert r.comprada_ilp_m >= r.longitud_util_m - 1e-9


def test_la_demanda_queda_cubierta():
    piezas = [2.3, 2.3, 3.7, 3.7, 3.7, 5.1]
    barras, _ = resolver_ilp(piezas, COM)
    assert sum(l * n for l, n in barras.items()) >= sum(piezas) - 1e-9


def test_pieza_mas_larga_que_la_barra():
    with pytest.raises(ValueError):
        resolver_ilp([13.0], COM)
