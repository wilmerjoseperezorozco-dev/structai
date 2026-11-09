"""Router /redes: contrato uniforme y 422 ante entrada inválida o red sin solución (regla 1)."""
import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")  # valores de prueba locales: no se contacta ningún servicio
os.environ.setdefault("SUPABASE_JWT_SECRET", "secreto-de-prueba-local")

from auth import AuthenticatedUser, get_current_user  # noqa: E402
from rate_limit import limiter  # noqa: E402
from routers.redes import router  # noqa: E402
from validacion_handler import manejar_validacion  # noqa: E402

CUERPO = dict(
    nodos=[dict(id="R", cota_m=50.0, carga_fija_m=100.0), dict(id="N", cota_m=40.0, demanda_m3s=0.1)],
    tramos=[dict(id="p", desde="R", hasta="N", longitud_m=1000.0, diametro_m=0.3, c_hw=130.0)],
)


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(RequestValidationError, manejar_validacion)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/redes/salud").status_code == 200


def test_responde_con_el_contrato_y_el_valor_de_hazen_williams_a_mano(cliente):
    r = cliente.post("/redes/permanente", json=CUERPO)
    assert r.status_code == 200
    j = r.json()
    for campo in ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio", "aviso_responsabilidad_profesional"):
        assert campo in j
    h = 10.67 * 1000.0 / (130.0 ** 1.852 * 0.3 ** 4.871) * 0.1 ** 1.852
    assert j["valor"]["nodos"]["N"]["carga_m"] == pytest.approx(100.0 - h, rel=1e-9)


def test_red_sin_embalse_responde_422(cliente):
    cuerpo = dict(CUERPO, nodos=[dict(id="R", cota_m=1.0), dict(id="N", cota_m=1.0, demanda_m3s=0.1)])
    r = cliente.post("/redes/permanente", json=cuerpo)
    assert r.status_code == 422 and "carga fija" in str(r.json())


def test_nudo_inexistente_en_un_tramo_responde_422(cliente):
    cuerpo = dict(CUERPO, tramos=[dict(id="p", desde="R", hasta="Z", longitud_m=10.0, diametro_m=0.3, c_hw=130.0)])
    assert cliente.post("/redes/permanente", json=cuerpo).status_code == 422


def test_nan_en_el_cuerpo_se_rechaza(cliente):
    r = cliente.post("/redes/permanente", content='{"nodos": [], "tramos": [{"longitud_m": NaN}]}',
                     headers={"content-type": "application/json"})
    assert r.status_code == 422


def test_bomba_por_el_endpoint_y_422_si_no_vence(cliente):
    cuerpo = dict(
        nodos=[dict(id="R", cota_m=10.0, carga_fija_m=10.0), dict(id="B", cota_m=10.0), dict(id="N", cota_m=30.0, demanda_m3s=0.03)],
        tramos=[dict(id="t", desde="B", hasta="N", longitud_m=800.0, diametro_m=0.25, c_hw=120.0)],
        bombas=[dict(id="bomba", desde="R", hasta="B", h0_m=60.0, a_s2m5=2000.0)])
    r = cliente.post("/redes/permanente", json=cuerpo)
    assert r.status_code == 200 and abs(r.json()["valor"]["bombas"]["bomba"]["caudal_m3s"] - 0.03) < 1e-8
    cuerpo["bombas"][0]["h0_m"] = 5.0
    cuerpo["nodos"][2]["demanda_m3s"] = 0.0
    r = cliente.post("/redes/permanente", json=cuerpo)
    assert r.status_code == 422 and "no vence" in str(r.json())
