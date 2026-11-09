"""Router /licuacion: contrato uniforme y 422 con la norma citada (regla 1)."""
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
from routers.licuacion import router  # noqa: E402

ESTRATO = dict(z_top_m=0.0, z_base_m=10.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, n1_60=15.0, finos_pct=3.0, no_plastico=True)
CUERPO = dict(amax_g=0.3, mw=7.5, nivel_freatico_m=2.0, estratos=[ESTRATO])


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/licuacion/salud").status_code == 200


def test_responde_con_el_contrato_y_el_valor_calculado_a_mano(cliente):
    r = cliente.post("/licuacion/spt", json=CUERPO)
    assert r.status_code == 200
    j = r.json()
    for campo in ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional"):
        assert campo in j
    assert j["valor"]["estratos"][0]["fs"] == pytest.approx(0.56907299259, rel=1e-8)
    assert j["valor"]["clasificacion_lpi"] == "muy alto"


def test_magnitud_fuera_de_rango_responde_422_con_la_norma(cliente):
    r = cliente.post("/licuacion/spt", json={**CUERPO, "mw": 4.0})
    assert r.status_code == 422 and "Youd" in r.json()["detail"]


def test_perfil_no_contiguo_responde_422(cliente):
    r = cliente.post("/licuacion/spt", json={**CUERPO, "estratos": [{**ESTRATO, "z_top_m": 1.0}]})
    assert r.status_code == 422


def test_falta_el_nivel_freatico_responde_422(cliente):
    c = {k: v for k, v in CUERPO.items() if k != "nivel_freatico_m"}
    assert cliente.post("/licuacion/spt", json=c).status_code == 422
