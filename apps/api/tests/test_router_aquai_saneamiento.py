"""Router /aquai/saneamiento (#236): contrato uniforme y 422 con la norma citada (regla 1)."""
import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages" / "construdata"))
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")  # valores de prueba locales: no se contacta ningún servicio
os.environ.setdefault("SUPABASE_JWT_SECRET", "secreto-de-prueba-local")

from auth import AuthenticatedUser, get_current_user  # noqa: E402
from rate_limit import limiter  # noqa: E402
from routers.aquai import router  # noqa: E402

LAGUNAS = dict(caudal_medio_m3_dia=1000.0, poblacion_equivalente=5000, dbo5_afluente_mg_l=300.0,
               coliformes_afluente_nmp_100ml=1e7, coliformes_objetivo_nmp_100ml=1000.0, temperatura_agua_c=25.0,
               incluir_anaerobia=True, profundidad_anaerobia_m=3.0, profundidad_facultativa_m=1.5,
               profundidad_maduracion_m=1.0, borde_libre_m=0.4, alta_turbulencia_atmosferica=False,
               tasa_acumulacion_lodos_m3_hab_ano=0.04, area_disponible_m2=None, cuerpo_receptor="rio")
PTAR = dict(poblacion_diseno=5000, caudal_acueducto_ls=50.0, factor_retorno=0.8, dbo5_cruda_mg_l=250.0,
            tecnologia="uasb", tipo_cuerpo_receptor="rio", temperatura_agua_c=24.0)
CONTRATO = ("valor", "unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio",
            "aviso_responsabilidad_profesional")


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_lagunas_contrato_y_valor_a_mano(cliente):
    r = cliente.post("/aquai/saneamiento/lagunas", json=LAGUNAS)
    assert r.status_code == 200
    j = r.json()
    assert all(c in j for c in CONTRATO)
    # anaerobia 333,3 + facultativa 3333,3 + 2 de maduración de 3000 m² (cálculo a mano en test_saneamiento_236)
    assert j["valor"]["area_espejo_total_m2"] == pytest.approx(1000 / 3 + 1000 * 5 / 1.5 + 6000, rel=1e-4)


def test_lagunas_profundidad_fuera_de_rango_422_cita_art_196(cliente):
    r = cliente.post("/aquai/saneamiento/lagunas", json={**LAGUNAS, "profundidad_anaerobia_m": 6.0})
    assert r.status_code == 422 and "art. 196" in r.json()["detail"]


def test_ptar_contrato(cliente):
    r = cliente.post("/aquai/saneamiento/ptar", json=PTAR)
    assert r.status_code == 200 and all(c in r.json() for c in CONTRATO)
    assert r.json()["valor"]["limite_res0631_dbo"] == 90.0


def test_ptar_suelo_422(cliente):
    r = cliente.post("/aquai/saneamiento/ptar", json={**PTAR, "tipo_cuerpo_receptor": "suelo"})
    assert r.status_code == 422 and "0631" in r.json()["detail"]


def test_ptap_contrato(cliente):
    r = cliente.post("/aquai/saneamiento/ptap", json=dict(caudal_diseno_ls=32.5, turbidez_cruda_ntu=80, color_crudo_uc=15,
                                                          ph_crudo=7.0, temperatura_c=27, coagulante="alumbre",
                                                          nivel_complejidad="medio_alto"))
    assert r.status_code == 200 and r.json()["valor"]["cumple_res2115"] is None
