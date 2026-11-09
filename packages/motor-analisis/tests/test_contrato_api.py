"""Salida con contrato uniforme de motor-analisis (#130). Valores esperados por fórmulas cerradas de la viga simple."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from contrato_motor.propiedades import verificar_homogeneidad
from src.contrato_api import SolicitudPortico, resolver_portico_contrato

E, A, I, L = 2.2e7, 0.12, 1.6e-3, 6.0


def _viga(w=20.0, n_elem=2, apoyos=None, **kw):
    xs = [L * k / n_elem for k in range(n_elem + 1)]
    base = dict(
        nodos=[(x, 0.0) for x in xs],
        elementos=[dict(i=k, j=k + 1, E=E, A=A, I=I) for k in range(n_elem)],
        apoyos={0: (True, True, False), n_elem: (False, True, False)} if apoyos is None else apoyos,
        casos=[dict(nombre="D", nodales={}, uniformes={k: w for k in range(n_elem)})],
    )
    base.update(kw)
    return SolicitudPortico(**base)


def test_contrato_completo_y_resultados_de_viga_simple():
    r = resolver_portico_contrato(_viga())
    d = r.valor["casos"]["D"]
    assert d["reacciones"]["0"][1] == pytest.approx(20.0 * L / 2)
    assert d["flecha_max_m"] == pytest.approx(5 * 20.0 * L**4 / (384 * E * I), rel=1e-9)
    assert d["momento_max_knm"] == pytest.approx(20.0 * L**2 / 8, rel=1e-6)
    assert r.unidad_si and "rigidez" in r.ecuacion.lower() and r.referencia_normativa
    assert r.supuestos and r.aviso_responsabilidad_profesional and isinstance(r.en_borde_dominio, bool)


def test_equilibrio_global_es_invariante_y_se_reporta():
    d = resolver_portico_contrato(_viga()).valor["casos"]["D"]
    assert abs(d["residuo_equilibrio_vertical_kn"]) < 1e-6


def test_linealidad_duplicar_la_carga_duplica_momento_y_flecha():
    a = resolver_portico_contrato(_viga(w=10.0)).valor["casos"]["D"]
    b = resolver_portico_contrato(_viga(w=20.0)).valor["casos"]["D"]
    assert b["momento_max_knm"] == pytest.approx(2 * a["momento_max_knm"], rel=1e-9)
    assert b["flecha_max_m"] == pytest.approx(2 * a["flecha_max_m"], rel=1e-9)


def test_homogeneidad_flecha_crece_con_la_cuarta_potencia_de_la_luz():
    def flecha(luz):
        xs = [0.0, luz / 2, luz]
        s = SolicitudPortico(nodos=[(x, 0.0) for x in xs], elementos=[dict(i=0, j=1, E=E, A=A, I=I), dict(i=1, j=2, E=E, A=A, I=I)],
                             apoyos={0: (True, True, False), 2: (False, True, False)},
                             casos=[dict(nombre="D", nodales={}, uniformes={0: 20.0, 1: 20.0})])
        return resolver_portico_contrato(s).valor["casos"]["D"]["flecha_max_m"]
    verificar_homogeneidad(lambda luz: flecha(luz), dict(luz=6.0), "luz", 4.0, rel=1e-9)


def test_modelo_sin_apoyos_lanza_valueerror():
    with pytest.raises(ValueError):
        resolver_portico_contrato(_viga(apoyos={}))


def test_modelo_inestable_lanza_valueerror_con_mensaje():
    with pytest.raises(ValueError, match="inestable|singular"):
        resolver_portico_contrato(_viga(apoyos={0: (True, True, False)}))


def test_sin_casos_es_error_de_validacion():
    with pytest.raises(ValidationError):
        _viga(casos=[])


def test_modelo_mal_condicionado_marca_borde():
    # rigidez muy dispar entre elementos: número de condición ~1e12 (entre el borde 1e10 y el rechazo 1e14)
    s = _viga(elementos=[dict(i=0, j=1, E=E, A=A, I=I), dict(i=1, j=2, E=E * 1e-5, A=A * 1e-5, I=I * 1e-5)])
    assert resolver_portico_contrato(s).en_borde_dominio is True
