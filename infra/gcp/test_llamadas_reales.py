"""Las llamadas reales del despliegue deben cuadrar con los motores (se prueban aquí en proceso, sin red)."""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "apps" / "api"))
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_JWT_SECRET", "secreto-de-prueba-local")

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import llamadas_reales as lr  # noqa: E402
from auth import AuthenticatedUser, get_current_user  # noqa: E402
from rate_limit import limiter  # noqa: E402
from routers import aquai, geotecnia, licuacion, redes  # noqa: E402


@pytest.fixture()
def en_proceso(monkeypatch):
    limiter.reset()
    app = FastAPI()
    for r in (redes, geotecnia, licuacion, aquai):
        app.include_router(r.router)
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-prueba", email=None)
    c = TestClient(app)

    def _post(url, ruta, cuerpo, token):
        r = c.post(ruta, json=cuerpo)
        assert r.status_code == 200, r.text
        return r.json()
    monkeypatch.setattr(lr, "_post", _post)


@pytest.mark.parametrize("motor", sorted(lr.MOTORES))
def test_calculo_a_mano_coincide_con_el_motor(en_proceso, motor):
    assert lr.MOTORES[motor]("", "x")


def test_sin_token_no_falla_pero_avisa(monkeypatch, capsys):
    monkeypatch.delenv("TOKEN_PRUEBA", raising=False)
    monkeypatch.setattr(sys, "argv", ["x", "https://ejemplo"])
    assert lr.main() == 0 and "NO queda verificada" in capsys.readouterr().out
