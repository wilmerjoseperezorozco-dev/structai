"""Balance de tierras: casos con solución calculable a mano y propiedades (conservación, optimalidad frente a heurística)."""
import numpy as np
import pytest

from src.excavacion_balance import Problema, combustible_gal_por_m3_km, resolver_balance


def _p(**kw):
    base = dict(cortes_m3=(1000.0,), aprovechable=(1.0,), demandas_m3=(600.0,), d_corte_relleno_km=((1.0,),), botaderos_cap_m3=(1e9,), d_corte_botadero_km=((10.0,),),
                tarifa_botadero_cop_m3=(5000.0,), prestamos_cap_m3=(1e9,), d_prestamo_relleno_km=((5.0,),), precio_prestamo_cop_m3=(30000.0,), costo_cop_m3_km=1000.0)
    base.update(kw)
    return Problema(**base)


def test_reutiliza_lo_necesario_y_bota_el_resto():
    plan = resolver_balance(_p())
    assert plan.x[0, 0] == pytest.approx(600.0) and plan.y[0, 0] == pytest.approx(400.0) and plan.z.sum() == pytest.approx(0.0)
    assert plan.reutilizacion_pct == pytest.approx(60.0)
    assert plan.costo_cop == pytest.approx(600 * 1000 * 1.0 + 400 * (1000 * 10 + 5000))


def test_prestamo_cercano_barato_vence_al_corte_lejano():
    # corte a 40 km del relleno (40.000/m³) frente a préstamo a 1 km con precio 8.000 (+1.000 de transporte): conviene el préstamo
    plan = resolver_balance(_p(d_corte_relleno_km=((40.0,),), d_prestamo_relleno_km=((1.0,),), precio_prestamo_cop_m3=(8000.0,)))
    assert plan.z[0, 0] == pytest.approx(600.0) and plan.x.sum() == pytest.approx(0.0)


def test_fraccion_aprovechable_limita_la_reutilizacion():
    plan = resolver_balance(_p(aprovechable=(0.3,)))
    assert plan.x.sum() == pytest.approx(300.0) and plan.z.sum() == pytest.approx(300.0)


def test_objetivo_reutilizacion_no_menos_que_costo_y_no_menos_barato():
    p = _p(d_corte_relleno_km=((40.0,),), d_prestamo_relleno_km=((1.0,),), precio_prestamo_cop_m3=(8000.0,))
    c, r = resolver_balance(p, "costo"), resolver_balance(p, "reutilizacion")
    assert r.reutilizacion_pct >= c.reutilizacion_pct - 1e-9 and r.costo_cop >= c.costo_cop - 1e-6
    assert r.reutilizacion_pct == pytest.approx(60.0)


def test_conservacion_y_optimalidad_en_instancias_aleatorias():
    rng = np.random.default_rng(7)
    for _ in range(25):
        ni, nj, nl, nk = (int(v) for v in rng.integers(1, 4, 4))
        cortes = rng.uniform(100, 1000, ni)
        p = Problema(tuple(cortes), tuple(rng.uniform(0, 1, ni)), tuple(rng.uniform(100, 800, nj)), tuple(map(tuple, rng.uniform(0.5, 20, (ni, nj)))),
                     tuple([1e9] * nl), tuple(map(tuple, rng.uniform(0.5, 20, (ni, nl)))), tuple(rng.uniform(0, 8000, nl)),
                     tuple([1e9] * nk), tuple(map(tuple, rng.uniform(0.5, 20, (nk, nj)))), tuple(rng.uniform(5000, 40000, nk)), 1200.0)
        plan = resolver_balance(p)
        assert np.allclose(plan.x.sum(1) + plan.y.sum(1), cortes, atol=1e-6)
        assert np.allclose(plan.x.sum(0) + plan.z.sum(0), p.demandas_m3, atol=1e-6)
        assert (plan.x.sum(1) <= np.array(p.aprovechable) * cortes + 1e-6).all()
        k = p.costo_cop_m3_km
        heur = sum(cortes[i] * min(k * p.d_corte_botadero_km[i][ll] + p.tarifa_botadero_cop_m3[ll] for ll in range(nl)) for i in range(ni)) + \
            sum(p.demandas_m3[j] * min(k * p.d_prestamo_relleno_km[kk][j] + p.precio_prestamo_cop_m3[kk] for kk in range(nk)) for j in range(nj))
        assert plan.costo_cop <= heur + 1e-3


def test_infactible_y_validaciones():
    with pytest.raises(ValueError):
        resolver_balance(_p(botaderos_cap_m3=(100.0,), aprovechable=(0.0,)))     # 1000 m³ sin dónde ir y sin reutilizar
    with pytest.raises(ValueError):
        resolver_balance(_p(aprovechable=(1.5,)))
    with pytest.raises(ValueError):
        resolver_balance(_p(botaderos_cap_m3=(float("inf"),)))
    assert combustible_gal_por_m3_km(6.0, 10.0, 0.25) == pytest.approx(2 * 1.25 / 60.0)
