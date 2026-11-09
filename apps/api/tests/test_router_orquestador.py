"""Router /orquestador junto a /concreto (ambos cargan motor-concreto): contrato uniforme y 422."""
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
from routers.concreto import router as router_concreto  # noqa: E402
from routers.orquestador_api import router  # noqa: E402


@pytest.fixture()
def cliente():
    app = FastAPI()
    app.include_router(router_concreto)
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


SOL = dict(luces_m=[6.0, 6.0], alturas_piso_m=[3.2, 3.0], carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0, calidad_concreto="3000",
           fy_mpa=420.0, recubrimiento_mm=40.0, municipio="Pereira", departamento="Risaralda", perfil_suelo="D", grupo_uso="I",
           capacidad="DES", columnas_mm=[400.0, 500.0, 600.0], b_mm=[250.0, 300.0, 350.0], h_mm=[500.0, 600.0, 700.0, 800.0])


def test_portico_integral_responde_con_el_contrato(cliente):
    r = cliente.post("/orquestador/portico-integral", json=SOL)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["valor"]["costo_directo_cop"] > 0
    for campo in ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional"):
        assert campo in j and j[campo] not in (None, "")


def test_ambos_routers_conviven_en_la_misma_app(cliente):
    assert cliente.get("/concreto/salud").status_code == 200 and cliente.get("/orquestador/salud").status_code == 200


def test_sin_perfil_de_suelo_es_422(cliente):
    malo = {k: v for k, v in SOL.items() if k != "perfil_suelo"}
    assert cliente.post("/orquestador/portico-integral", json=malo).status_code == 422


def test_sin_solucion_es_422_con_la_norma(cliente):
    r = cliente.post("/orquestador/portico-integral", json={**SOL, "carga_muerta_kn_m": 400.0, "carga_viva_kn_m": 200.0,
                                                          "b_mm": [250.0], "h_mm": [500.0], "columnas_mm": [300.0]})
    assert r.status_code == 422 and "NSR-10" in r.text
