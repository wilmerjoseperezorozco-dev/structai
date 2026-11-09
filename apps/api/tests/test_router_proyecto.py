"""Router /proyecto: DAG estructural con artefactos versionados; datos faltantes o sin solución → 422."""
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
from routers.proyecto import router  # noqa: E402

SOL = dict(
    luces_m=[6.0], alturas_piso_m=[3.0], carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0, calidad_concreto="3000",
    fy_mpa=420.0, recubrimiento_mm=40.0, municipio="Pereira", departamento="Risaralda", perfil_suelo="D",
    grupo_uso="I", capacidad="DES", columnas_mm=[400.0, 500.0], b_mm=[300.0, 350.0], h_mm=[500.0, 600.0],
    E_mpa=21000.0, q_adm_kpa=250.0, profundidad_desplante_m=1.5, peso_unitario_relleno_kn_m3=17.0,
    asentamiento_max_mm=25.0, ks_kn_m3=None, fc_mpa=21.0,
)


@pytest.fixture()
def cliente():
    limiter.reset()  # el límite de 5/min es por proceso: cada prueba parte de cero
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    return TestClient(app)


def test_salud(cliente):
    assert cliente.get("/proyecto/salud").status_code == 200


def test_proyecto_estructural_devuelve_artefactos_versionados(cliente):
    r = cliente.post("/proyecto/estructural", json=SOL)
    assert r.status_code == 200, r.text
    j = r.json()
    assert set(j["artefactos"]) == {"orquestador", "analisis", "zapata"}
    z = j["artefactos"]["zapata"]
    assert len(z["id"]) == 64 and len(z["hash_contenido"]) == 64 and z["estado"] == "vigente"
    assert z["entradas"] == [j["artefactos"]["orquestador"]["id"], j["artefactos"]["analisis"]["id"]] or set(z["entradas"]) == {
        j["artefactos"]["orquestador"]["id"], j["artefactos"]["analisis"]["id"]}
    assert z["resultado"]["aviso_responsabilidad_profesional"]


def test_misma_solicitud_da_los_mismos_ids(cliente):
    a = cliente.post("/proyecto/estructural", json=SOL).json()["artefactos"]
    b = cliente.post("/proyecto/estructural", json=SOL).json()["artefactos"]
    assert {k: v["id"] for k, v in a.items()} == {k: v["id"] for k, v in b.items()}


def test_dato_faltante_es_422(cliente):
    malo = {k: v for k, v in SOL.items() if k != "q_adm_kpa"}
    assert cliente.post("/proyecto/estructural", json=malo).status_code == 422


def test_sin_solucion_es_422_citando_la_norma(cliente):
    r = cliente.post("/proyecto/estructural", json={**SOL, "carga_muerta_kn_m": 5000.0, "columnas_mm": [300.0], "b_mm": [200.0], "h_mm": [300.0]})
    assert r.status_code == 422 and "NSR-10" in r.text


# ── persistencia en Supabase (cliente simulado) ───────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages" / "dag-proyecto" / "tests"))
from test_almacen_supabase import FakeSB  # noqa: E402


def test_persiste_artefactos_del_usuario_y_reutiliza_en_la_segunda_corrida(cliente, monkeypatch):
    import routers.proyecto as rp
    sb = FakeSB()
    monkeypatch.setattr(rp, "_cliente_supabase", lambda: sb)
    j1 = cliente.post("/proyecto/estructural", json=SOL).json()
    assert j1["persistido"] is True
    assert {f["user_id"] for f in sb.filas} == {"u-prueba"} and len(sb.filas) == 3
    n = len(sb.filas)
    j2 = cliente.post("/proyecto/estructural", json=SOL).json()
    assert len(sb.filas) == n and {k: v["id"] for k, v in j1["artefactos"].items()} == {k: v["id"] for k, v in j2["artefactos"].items()}


def test_sin_cliente_supabase_responde_sin_persistir(cliente, monkeypatch):
    import routers.proyecto as rp
    monkeypatch.setattr(rp, "_cliente_supabase", lambda: None)
    j = cliente.post("/proyecto/estructural", json=SOL).json()
    assert j["persistido"] is False and set(j["artefactos"]) == {"orquestador", "analisis", "zapata"}


def test_si_supabase_falla_se_calcula_igual_y_se_declara(cliente, monkeypatch):
    import routers.proyecto as rp

    class Roto:
        def table(self, *_):
            raise RuntimeError("sin conexión")
    monkeypatch.setattr(rp, "_cliente_supabase", lambda: Roto())
    j = cliente.post("/proyecto/estructural", json=SOL).json()
    assert j["persistido"] is False and j["artefactos"]["zapata"]["resultado"]["valor"]["cumple"] is True
