from src.muro_contencion import Relleno, SueloApoyo
from src.muro_optimizador import CasoMuro
from src.muro_pareto import elegir, frontera

C = CasoMuro(4.0, Relleno(18.0, 30.0, 5.0, 10.0), SueloApoyo(30.0, 200.0), a_max_g=0.15)


def test_frontera_es_no_dominada_y_ordenada():
    pts = frontera(C, lambdas=(0.0, 400.0, 6000.0))
    assert pts
    for a, b in zip(pts[:-1], pts[1:]):
        assert a.costo_cop_m <= b.costo_cop_m and a.co2_kg_m >= b.co2_kg_m


def test_elegir_devuelve_extremos_coherentes():
    pts = frontera(C, lambdas=(0.0, 150.0, 1000.0, 15000.0))
    e = elegir(pts)
    assert e["minimo_costo"].costo_cop_m <= e["equilibrio"].costo_cop_m <= e["minima_huella"].costo_cop_m
    assert e["minima_huella"].co2_kg_m <= e["minimo_costo"].co2_kg_m
