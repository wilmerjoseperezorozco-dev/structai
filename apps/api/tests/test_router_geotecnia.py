"""Router /geotecnia: contrato uniforme y 422 con la norma citada (regla 1)."""
import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")  # valores de prueba locales: no se contacta ningún servicio
os.environ.setdefault("SUPABASE_JWT_SECRET", "secreto-de-prueba-local")

from auth import AuthenticatedUser, get_current_user  # noqa: E402
from rate_limit import limiter  # noqa: E402
from routers.geotecnia import router  # noqa: E402

CAMPOS = ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional")
ESTRATO = dict(espesor_m=4.0, z_medio_m=4.0, sigma0_kpa=100.0, sigma_p_kpa=100.0, cc=0.3, cr=0.03, e0=1.0, cv_m2_dia=0.002, hdr_m=2.0)
ASENT = dict(q_kpa=150.0, B_m=2.0, L_m=3.0, estratos=[ESTRATO], metodo="boussinesq", tipo_cimentacion="aislada")
PORT = dict(c_kpa=10.0, phi_deg=25.0, gamma_kn_m3=18.0, B_m=2.0, L_m=2.0, Df_m=1.0, nivel_freatico_m=None,
            factor_seguridad=3.0, q_aplicada_kpa=150.0)


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/geotecnia/salud").status_code == 200


@pytest.mark.parametrize("ruta,cuerpo", [("/geotecnia/asentamiento", ASENT), ("/geotecnia/portante", PORT)])
def test_responde_con_el_contrato_uniforme(cliente, ruta, cuerpo):
    r = cliente.post(ruta, json=cuerpo)
    assert r.status_code == 200, r.text
    j = r.json()
    for campo in CAMPOS:
        assert campo in j and j[campo] not in (None, "")
    assert isinstance(j["en_borde_dominio"], bool)


def test_dato_faltante_es_422(cliente):
    malo = {k: v for k, v in PORT.items() if k != "factor_seguridad"}
    assert cliente.post("/geotecnia/portante", json=malo).status_code == 422


def test_error_de_dominio_es_422_citando_la_norma(cliente):
    estrato = {**ESTRATO, "sigma_p_kpa": 50.0}
    r = cliente.post("/geotecnia/asentamiento", json={**ASENT, "estratos": [estrato]})
    assert r.status_code == 422 and "preconsolidaci" in r.text


def test_agua_sin_peso_saturado_es_422(cliente):
    r = cliente.post("/geotecnia/portante", json={**PORT, "nivel_freatico_m": 1.0})
    assert r.status_code == 422 and "saturado" in r.text


# ── Ampliación del Título H (#136) ──────────────────────────────────────────────────────────────────────────────────
TOTAL = dict(q_kpa=100.0, B_m=2.0, L_m=2.0, es_kpa=10000.0, nu=0.3, metodo="2a1", tipo_cimentacion="aislada",
             estratos=[{**ESTRATO, "c_alfa": 0.01}])
DIF = dict(apoyos=[dict(x_m=0.0, asentamiento_mm=20.0), dict(x_m=6.0, asentamiento_mm=35.0)], tipo_construccion="porticos_concreto")
MULTI = dict(capas=[dict(espesor_m=4.0, cv_m2_dia=0.01, mv_kpa_inv=1e-3, delta_sigma_kpa=100.0)], tiempos_dias=[10.0, 100.0],
             drenaje_superior=True, drenaje_inferior=False)
MC = dict(espesor_m=4.0, sigma0_kpa=60.0, delta_kpa=40.0, sigma_p_kpa=60.0, cr=0.05, cc_mediana=0.3, cc_cv=0.3,
          e0_mediana=1.0, e0_cv=0.1, rho_cc_e0=0.5, n=1000, semilla=1, tipo_cimentacion="aislada")
EXC = dict(c_kpa=10.0, phi_deg=30.0, gamma_kn_m3=18.0, B_m=2.0, L_m=3.0, Df_m=1.0, nivel_freatico_m=None, V_kn=900.0,
           H_kn=60.0, eB_m=0.2, eL_m=0.0, factor_seguridad=3.0, condicion_carga="muerta_viva_normal")


@pytest.mark.parametrize("ruta,cuerpo", [("/geotecnia/asentamiento-total", TOTAL), ("/geotecnia/diferencial", DIF),
                                         ("/geotecnia/multicapa", MULTI), ("/geotecnia/asentamiento-montecarlo", MC),
                                         ("/geotecnia/portante-excentrica", EXC)])
def test_endpoints_nuevos_responden_con_el_contrato(cliente, ruta, cuerpo):
    r = cliente.post(ruta, json=cuerpo)
    assert r.status_code == 200, r.text
    assert all(c in r.json() for c in CAMPOS)


def test_fs_bajo_el_minimo_de_la_tabla_h471_es_422(cliente):
    r = cliente.post("/geotecnia/portante-excentrica", json={**EXC, "factor_seguridad": 2.0})
    assert r.status_code == 422 and "H.4.7-1" in r.json()["detail"]
    r2 = cliente.post("/geotecnia/portante", json={**PORT, "factor_seguridad": 2.0, "condicion_carga": "muerta_viva_maxima"})
    assert r2.status_code == 422 and "H.4.7-1" in r2.json()["detail"]


def test_apoyos_repetidos_y_calpha_ausente_son_422(cliente):
    r = cliente.post("/geotecnia/diferencial", json={**DIF, "apoyos": [dict(x_m=1.0, asentamiento_mm=1.0)] * 2})
    assert r.status_code == 422 and "H.4.9-1" in r.json()["detail"]
    assert cliente.post("/geotecnia/asentamiento-total", json={**TOTAL, "estratos": [ESTRATO]}).status_code == 422
