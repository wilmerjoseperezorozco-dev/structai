"""Router /acero-frio (#81): contrato uniforme y 422 con la norma citada (regla 1)."""
import math
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
from routers.acero_frio import router  # noqa: E402

PERFIL = dict(H_mm=229.0, B_mm=63.5, D_mm=19.0, t_mm=1.5, Fy_MPa=345.0, Fu_MPa=450.0)
CAMPOS = ("unidad_si", "ecuacion", "referencia_normativa", "supuestos", "en_borde_dominio",
          "aviso_responsabilidad_profesional")


@pytest.fixture()
def cliente():
    limiter.reset()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/acero-frio/salud").status_code == 200


def test_propiedades_area_a_mano(cliente):
    r = cliente.post("/acero-frio/perfil-c/propiedades", json=PERFIL)
    assert r.status_code == 200
    j = r.json()
    for c in CAMPOS:
        assert c in j
    t = 1.5
    area = t * ((229 - t) + 2 * (63.5 - t) + 2 * (19 - t / 2))       # línea media
    assert j["valor"]["A_mm2"] == pytest.approx(area, rel=1e-12)


def test_flexion_con_los_tres_estados(cliente):
    cuerpo = dict(perfil=PERFIL, Lm_mm=3000.0, KyLy_mm=3000.0, KtLt_mm=3000.0, Cb=1.0,
                  aleta_comprimida_arriostrada=False)
    r = cliente.post("/acero-frio/perfil-c/flexion", json=cuerpo)
    assert r.status_code == 200
    e = r.json()["valor"]["estados_limite"]
    assert set(e) == {"seccion", "lateral_torsional", "distorsional"}
    assert r.json()["valor"]["phi_Mn_kNm"] == pytest.approx(min(x["phi_Mn_kNm"] for x in e.values()))


def test_sin_datos_de_ltb_responde_422_con_la_norma(cliente):
    r = cliente.post("/acero-frio/perfil-c/flexion",
                     json=dict(perfil=PERFIL, Lm_mm=3000.0, aleta_comprimida_arriostrada=False))
    assert r.status_code == 422 and "F.4.3.3.1.2.1" in r.json()["detail"]


def test_sin_lm_en_c_con_pestana_responde_422(cliente):
    r = cliente.post("/acero-frio/perfil-c/compresion",
                     json=dict(perfil=PERFIL, KxLx_mm=3000.0, KyLy_mm=1000.0, KtLt_mm=1000.0))
    assert r.status_code == 422 and "F.4.3.4.2" in r.json()["detail"]


def test_geometria_fuera_de_dominio_responde_422(cliente):
    r = cliente.post("/acero-frio/perfil-c/compresion",
                     json=dict(perfil={**PERFIL, "B_mm": 120.0}, KxLx_mm=3000.0, KyLy_mm=1000.0, KtLt_mm=1000.0,
                               Lm_mm=1000.0))
    assert r.status_code == 422


def test_campos_extra_o_infinitos_responden_422(cliente):
    assert cliente.post("/acero-frio/perfil-c/tension",
                        json=dict(perfil=PERFIL, An_mm2=300.0, zona="x")).status_code == 422
    assert cliente.post("/acero-frio/perfil-c/tension", content='{"perfil":' + str(PERFIL).replace("'", '"')
                        + ',"An_mm2":1e308}', headers={"content-type": "application/json"}).status_code == 422


def test_flexocompresion_y_flexotension(cliente):
    fc = cliente.post("/acero-frio/perfil-c/flexocompresion",
                      json=dict(perfil=PERFIL, Pu_kN=20.0, Mux_kNm=3.0, KxLx_mm=3000.0, KyLy_mm=1500.0,
                                KtLt_mm=1500.0, Cmx=0.85, aleta_comprimida_arriostrada=False, Cb=1.0, Lm_mm=1500.0))
    assert fc.status_code == 200 and math.isfinite(fc.json()["valor"]["razon"])
    ft = cliente.post("/acero-frio/perfil-c/flexotension",
                      json=dict(perfil=PERFIL, Tu_kN=20.0, Mux_kNm=3.0, An_mm2=400.0,
                                aleta_comprimida_arriostrada=True, Lm_mm=1000.0))
    assert ft.status_code == 200


def test_arrugamiento_exige_la_fila_de_la_tabla(cliente):
    coef = dict(C=4.0, CR=0.1, CN=0.3, Ch=0.02, phi_w=0.85, R_t_max=9.0)
    r = cliente.post("/acero-frio/perfil-c/arrugamiento",
                     json=dict(perfil=PERFIL, Pu_kN=5.0, N_mm=75.0, R_mm=3.0, coeficientes=coef))
    assert r.status_code == 422
    ok = cliente.post("/acero-frio/perfil-c/arrugamiento",
                      json=dict(perfil=PERFIL, Pu_kN=5.0, N_mm=75.0, R_mm=3.0,
                                coeficientes={**coef, "fila": "ficticia para prueba"}))
    assert ok.status_code == 200
