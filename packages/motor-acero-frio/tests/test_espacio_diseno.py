"""Espacio de diseño para #311: declaración coherente y enumeración exacta como oráculo."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest

from src.contrato_api import PerfilC, verificar_viga_c
from src.espacio_diseno import ESPACIO_DISENO, enumerar, evaluar, malla, masa_por_metro

FIJOS = dict(Fy_MPa=345.0, Fu_MPa=450.0, Mu_kNm=4.0, Vu_kN=6.0, Lm_mm=2500.0, KyLy_mm=2500.0, KtLt_mm=2500.0,
             Cb=1.0, aleta_comprimida_arriostrada=False)


def test_declaracion_completa():
    for clave in ("variables", "dominio_validez", "restricciones", "objetivos", "costo_por_evaluacion",
                  "metodo_sugerido_311"):
        assert clave in ESPACIO_DISENO
    for v in ESPACIO_DISENO["variables"].values():
        assert v["tipo"] in ("continua", "entera", "catalogo")
        assert ("min" in v and v["min"] < v["max"]) or v.get("valores")


def test_fuera_de_dominio_es_infactible_y_no_rompe():
    e = evaluar(dict(H_mm=400.0, B_mm=50.0, D_mm=15.0, t_mm=0.9), FIJOS)   # h/t > 200
    assert e.factible is False and "fuera de dominio" in e.motivo


def test_enumeracion_es_oraculo_y_el_motor_dispone():
    cand = malla(H=[150.0, 200.0, 250.0], B=[50.0, 65.0], D=[0.0, 15.0, 20.0], t=[1.2, 1.5, 1.9])
    evs = enumerar(cand, FIJOS)
    factibles = [e for e in evs if e.factible]
    assert factibles, "la malla debe contener al menos una C que cumpla"
    mejor = factibles[0]
    # El optimizador propone; el motor dispone: se re-verifica el óptimo con el contrato completo.
    pf = PerfilC(**mejor.perfil, Fy_MPa=345.0, Fu_MPa=450.0)
    r = verificar_viga_c(pf, 4.0, 6.0, Lm_mm=2500.0, KyLy_mm=2500.0, KtLt_mm=2500.0, Cb=1.0,
                         aleta_comprimida_arriostrada=False)
    assert r.valor["cumple"] is True
    assert mejor.margen == pytest.approx(1 - max(r.valor["razones"].values()))
    # Nada más liviano cumple.
    assert all(e.masa_kg_m >= mejor.masa_kg_m - 1e-12 for e in factibles)
    assert len(evs) == len(cand)


def test_masa_por_metro_a_mano():
    pf = PerfilC(H_mm=150.0, B_mm=50.0, D_mm=0.0, t_mm=2.0, Fy_MPa=345.0, Fu_MPa=450.0)
    area = 2.0 * ((150 - 2) + 2 * (50 - 2))                 # línea media de la C sin pestaña
    assert masa_por_metro(pf) == pytest.approx(area * 1e-6 * 7850, rel=1e-12)
