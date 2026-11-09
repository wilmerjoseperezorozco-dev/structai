"""Router /analisis: contrato uniforme y 422 ante modelos inestables."""
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
from routers.analisis import router  # noqa: E402


@pytest.fixture()
def cliente():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


E, A, I = 2.2e7, 0.12, 1.6e-3
VIGA = dict(nodos=[[0, 0], [3, 0], [6, 0]],
            elementos=[dict(i=0, j=1, E=E, A=A, I=I), dict(i=1, j=2, E=E, A=A, I=I)],
            apoyos={"0": [True, True, False], "2": [False, True, False]},
            casos=[dict(nombre="D", uniformes={"0": 20.0, "1": 20.0})])


def test_portico_responde_con_el_contrato(cliente):
    r = cliente.post("/analisis/portico", json=VIGA)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["valor"]["casos"]["D"]["momento_max_knm"] == pytest.approx(20.0 * 36 / 8, rel=1e-6)
    for campo in ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional"):
        assert campo in j and j[campo] not in (None, "")


def test_modelo_inestable_es_422(cliente):
    assert cliente.post("/analisis/portico", json={**VIGA, "apoyos": {"0": [True, True, False]}}).status_code == 422


def test_nodo_inexistente_es_422(cliente):
    malo = {**VIGA, "elementos": [dict(i=0, j=9, E=E, A=A, I=I)]}
    assert cliente.post("/analisis/portico", json=malo).status_code == 422
