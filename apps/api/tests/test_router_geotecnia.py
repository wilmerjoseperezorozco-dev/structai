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
