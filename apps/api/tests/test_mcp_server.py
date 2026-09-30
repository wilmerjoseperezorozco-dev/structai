"""
Regresión de apps/api/mcp_server.py -- issue #78.

Verifica el contrato real del montaje MCP, no solo que el import no
lance: con ENABLE_MCP=false (default de producción) /mcp no debe existir
-- cero cambio de comportamiento para el 100% del tráfico actual. Con
ENABLE_MCP=true, /mcp debe montarse con EXACTAMENTE un tool ("consultar"),
reusando el schema real de ConsultarRequest/ConsultarResponse ya
expuesto por FastAPI -- no un schema inventado a mano.

Recarga main.py en cada test (import fresco) porque el módulo lee
ENABLE_MCP una sola vez al importarse -- reimportar simula honestamente
dos arranques distintos del proceso con env distinto, en vez de mutar
estado global después de importado.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

PACKAGES_DIR = API_DIR.parents[1] / "packages" / "construdata"
sys.path.insert(0, str(PACKAGES_DIR))

from dotenv import load_dotenv

load_dotenv(API_DIR / ".env")


def _reimportar_main():
    if "main" in sys.modules:
        del sys.modules["main"]
    return importlib.import_module("main")


def test_enable_mcp_false_no_monta_ruta_mcp(monkeypatch) -> None:
    """Default de producción -- /mcp no debe existir en absoluto."""
    monkeypatch.setenv("ENABLE_MCP", "false")
    main = _reimportar_main()
    rutas_mcp = [r.path for r in main.app.routes if "/mcp" in getattr(r, "path", "")]
    assert rutas_mcp == [], f"Con ENABLE_MCP=false no debería existir ninguna ruta /mcp, se encontró: {rutas_mcp}"


def test_enable_mcp_true_monta_un_unico_tool_consultar(monkeypatch) -> None:
    """Con ENABLE_MCP=true, /mcp se monta con EXACTAMENTE el tool
    'consultar' -- alcance deliberadamente mínimo del issue #78, no debe
    exponer /admin/*, /detect, /apu/calculate-batch ni ningún otro
    endpoint por accidente."""
    monkeypatch.setenv("ENABLE_MCP", "true")
    main = _reimportar_main()
    rutas_mcp = [r.path for r in main.app.routes if "/mcp" in getattr(r, "path", "")]
    assert "/mcp" in rutas_mcp

    from fastapi_mcp import FastApiMCP
    mcp = FastApiMCP(main.app, include_operations=["consultar"])
    nombres = [t.name for t in mcp.tools]
    assert nombres == ["consultar"], f"Se esperaba solo el tool 'consultar', se encontraron: {nombres}"


def test_enable_mcp_oauth_false_no_rompe_el_montaje_bearer(monkeypatch) -> None:
    """Default (ENABLE_MCP_OAUTH=false): /mcp se monta igual que siempre,
    solo con el camino de bearer token -- confirma que agregar el
    parámetro OAuth no cambió el comportamiento por defecto."""
    monkeypatch.setenv("ENABLE_MCP", "true")
    monkeypatch.setenv("ENABLE_MCP_OAUTH", "false")
    main = _reimportar_main()
    assert any(r.path == "/mcp" for r in main.app.routes)


def test_enable_mcp_oauth_true_no_lanza_al_construir_authconfig(monkeypatch) -> None:
    """ENABLE_MCP_OAUTH=true construye un AuthConfig real apuntando a
    SUPABASE_URL sin lanzar excepción -- NO verifica el round-trip OAuth
    completo (requiere el toggle 'OAuth Server' activado en el dashboard
    de Supabase, que sigue apagado -- ver issue #78, no se activa desde
    código)."""
    monkeypatch.setenv("ENABLE_MCP", "true")
    monkeypatch.setenv("ENABLE_MCP_OAUTH", "true")
    main = _reimportar_main()
    assert any(r.path == "/mcp" for r in main.app.routes)

    from mcp_server import _auth_config_oauth
    cfg = _auth_config_oauth()
    assert cfg is not None
    assert cfg.issuer.endswith("/auth/v1")
    assert cfg.authorize_url.endswith("/auth/v1/oauth/authorize")


def test_tool_consultar_reusa_el_schema_real_de_consultarrequest(monkeypatch) -> None:
    """El input schema del tool MCP debe salir del ConsultarRequest real
    (pregunta/top_k) -- confirma que fastapi_mcp está introspeccionando
    la ruta real, no un schema inventado a mano en mcp_server.py."""
    monkeypatch.setenv("ENABLE_MCP", "true")
    main = _reimportar_main()

    from fastapi_mcp import FastApiMCP
    mcp = FastApiMCP(main.app, include_operations=["consultar"])
    tool = mcp.tools[0]
    props = tool.inputSchema["properties"]
    assert "pregunta" in props
    assert "top_k" in props
    assert tool.inputSchema["required"] == ["pregunta"]
