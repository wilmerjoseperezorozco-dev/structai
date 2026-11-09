"""Router /concreto: contrato uniforme de salida y 422 con la norma ante datos fuera de dominio."""
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
from routers.concreto import router  # noqa: E402


@pytest.fixture()
def cliente():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


ZAPATA = dict(c1_mm=400, c2_mm=400, P_serv=800.0, P_u=1100.0, q_adm_kpa=200.0, profundidad_desplante_m=1.5,
              peso_unitario_relleno_kn_m3=17.0, asentamiento_max_mm=25.0, ks_kn_m3=None, fc_mpa=21.0, fy_mpa=420.0)
TALUD = dict(altura_m=5.0, angulo_deg=45.0, gamma_kn_m3=18.0, c_kpa=15.0, phi_deg=28.0, prof_freatico_m=None,
             sobrecarga_kpa=0.0, kh=0.0, estado="diseno")


def test_zapata_responde_con_el_contrato(cliente):
    r = cliente.post("/concreto/zapata", json=ZAPATA)
    assert r.status_code == 200, r.text
    j = r.json()
    for campo in ("valor", "unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio",
                  "aviso_responsabilidad_profesional"):
        assert campo in j and j[campo] not in (None, "")


def test_zapata_sin_datos_del_suelo_es_422(cliente):
    malo = {k: v for k, v in ZAPATA.items() if k != "profundidad_desplante_m"}
    assert cliente.post("/concreto/zapata", json=malo).status_code == 422


def test_zapata_sin_solucion_es_422_con_la_norma(cliente):
    r = cliente.post("/concreto/zapata", json={**ZAPATA, "P_serv": 9e5, "P_u": 1.2e6, "q_adm_kpa": 50.0})
    assert r.status_code == 422 and "NSR-10" in r.text


def test_talud_responde_con_el_contrato(cliente):
    r = cliente.post("/concreto/talud", json=TALUD)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["valor"]["fs"] > 0 and "H.2.4" in j["referencia_normativa"]


def test_talud_estado_invalido_es_422(cliente):
    assert cliente.post("/concreto/talud", json={**TALUD, "estado": "otro"}).status_code == 422
