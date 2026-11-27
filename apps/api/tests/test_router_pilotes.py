"""Router /pilotes: contrato uniforme y 422 con la norma citada (regla 1)."""
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
from routers.pilotes import router  # noqa: E402

CAMPOS = ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional")
ARCILLA = dict(espesor_m=30.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=19.0, comportamiento="no_drenado", su_kpa=50.0)
CAPACIDAD = dict(estratos=[ARCILLA], nivel_freatico_m=None, seccion="cuadrada", ancho_m=0.4, longitud_m=15.0,
                 tipo="hincado", filas=3, columnas=3, separacion_m=1.2, combinacion="cm_cv_normal",
                 eficiencia_grupo="ninguna", reaccion_vertical_kn=2000.0)
CAPA = dict(z_tope_m=0.0, espesor_m=4.0, sigma0_kpa=150.0, sigma_p_kpa=150.0, cc=0.30, cr=0.05, e0=0.90)
ASENT = dict(carga_permanente_kn=4000.0, seccion="cuadrada", ancho_m=0.4, longitud_m=15.0, ep_mpa=25000.0, filas=3,
             columnas=3, separacion_m=1.2, db_m=10.0, caso_zapata_equivalente="b_friccion_arcilla",
             suelo_bajo_zapata="cohesivo", estratos_compresibles=[CAPA], tipo_cimentacion="aislada")


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/pilotes/salud").status_code == 200


@pytest.mark.parametrize("ruta,cuerpo", [("/pilotes/capacidad", CAPACIDAD), ("/pilotes/asentamiento", ASENT)])
def test_responde_con_el_contrato_uniforme(cliente, ruta, cuerpo):
    r = cliente.post(ruta, json=cuerpo)
    assert r.status_code == 200, r.text
    j = r.json()
    for campo in CAMPOS:
        assert campo in j


def test_asentamiento_valor_a_mano(cliente):
    j = cliente.post("/pilotes/asentamiento", json=ASENT).json()
    assert j["valor"]["asentamiento_total_mm"] == pytest.approx(210.905 + 1.666667, rel=1e-5)


@pytest.mark.parametrize("ruta,cuerpo", [
    ("/pilotes/capacidad", dict(CAPACIDAD, separacion_m=None)),
    ("/pilotes/asentamiento", dict(ASENT, estratos_compresibles=None)),
    ("/pilotes/asentamiento", dict(ASENT, db_m=20.0)),
])
def test_dato_faltante_responde_422(cliente, ruta, cuerpo):
    assert cliente.post(ruta, json=cuerpo).status_code == 422


def test_falla_de_dominio_del_motor_responde_422(cliente):
    capa = dict(CAPA, sigma_p_kpa=100.0)  # σ'p < σ'0: el motor rechaza con la referencia
    r = cliente.post("/pilotes/asentamiento", json=dict(ASENT, estratos_compresibles=[capa]))
    assert r.status_code == 422 and "Terzaghi" in r.json()["detail"]
