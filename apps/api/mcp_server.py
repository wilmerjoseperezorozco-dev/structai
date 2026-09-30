"""
Servidor MCP de StructAI -- issue #78.

Expone `/consultar` (normativa NSR-10/NTC/RAS 2000 + precios APU con
trazabilidad, ver rag_multi_norma.ask_delegado()) como herramienta MCP
para clientes de IA (Claude Desktop, Claude Code, cualquier cliente que
hable el protocolo). Reusa el 100% del backend real -- mismo RAG, mismo
motor-apu -- sin duplicar ninguna lógica: fastapi_mcp introspecciona
main.app y envuelve el endpoint HTTP ya existente.

Autenticacion, dos caminos que coexisten:

1. Bearer token directo (siempre disponible): fastapi_mcp reenvia el
   header `authorization` tal cual hacia /consultar, que ya valida el
   JWT de Supabase en auth.get_current_user() -- funciona hoy con
   Claude Code (`claude mcp add --header "Authorization: Bearer <jwt>"`)
   y clientes tipo `mcp-remote`. NO funciona desde el boton "Add custom
   connector" del propio sitio claude.ai -- esa UI (verificado en vivo
   2026-09-30, ver issues reales anthropics/claude-ai-mcp #112 y #715)
   solo expone campos de OAuth Client ID/Secret, sin campo para pegar un
   token estatico.

2. OAuth 2.1 (issue #78, para desbloquear la via anterior): Supabase
   Auth -- que StructAI ya usa para login -- tiene soporte NATIVO de
   servidor OAuth 2.1 con Dynamic Client Registration, pensado
   explicitamente para este caso de uso de MCP (verificado en vivo,
   docs.supabase.com/guides/auth/oauth-server). Se activa con UN TOGGLE
   en el dashboard de Supabase (Authentication > OAuth Server) -- CERO
   cambios de codigo al login existente, las cuentas de usuario actuales
   funcionan automaticamente. Mientras ese toggle siga apagado,
   ENABLE_MCP_OAUTH debe quedar en "false" -- este modulo NO intenta
   activarlo por su cuenta (cambio de superficie de auth de todo el
   proyecto, requiere decision explicita, ver issue #78).

Alcance deliberadamente minimo (decision explicita en el issue): UN
unico tool, solo lectura -- consultar normativa/precios. Nada de
escritura (registrar calculos, modificar datos) todavia. Montado detras
de ENABLE_MCP (default "false"), mismo patron que ENABLE_YOLO/
ENABLE_ESTRUCTURAL -- no cambia nada en produccion sin decision
explicita de habilitarlo.
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi_mcp.types import AuthConfig

log = logging.getLogger("construdata.api")


def _auth_config_oauth() -> AuthConfig | None:
    """Construye la config de OAuth 2.1 apuntando al servidor de
    Supabase -- SOLO si ENABLE_MCP_OAUTH=true (requiere el toggle de
    Supabase ya activado a mano, ver docstring del modulo). issuer +
    authorize_url se derivan de SUPABASE_URL, que ya es una variable de
    entorno obligatoria del proyecto (main.py la exige al arrancar) --
    no se agrega ningun secreto nuevo."""
    if os.environ.get("ENABLE_MCP_OAUTH", "false").lower() != "true":
        return None
    supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
    return AuthConfig(
        issuer=f"{supabase_url}/auth/v1",
        authorize_url=f"{supabase_url}/auth/v1/oauth/authorize",
        # Supabase ya expone metadata OAuth 2.1 spec-compliant con
        # Dynamic Client Registration (RFC 7591) en su propio
        # /.well-known -- no hace falta setup_proxies (eso es para
        # envolver un proveedor NO compatible).
    )


def montar_mcp(app: FastAPI) -> None:
    """Monta el servidor MCP en /mcp. Debe llamarse DESPUES de que todas
    las rutas de main.py ya esten registradas -- FastApiMCP introspecciona
    app.routes en el momento de construccion, no de forma perezosa."""
    auth_config = _auth_config_oauth()
    mcp = FastApiMCP(
        app,
        name="StructAI",
        description=(
            "Normativa colombiana de construccion (NSR-10, NTC, RAS 2000) "
            "y precios reales de construccion con trazabilidad normativa, "
            "usando la cuenta de StructAI del usuario que hace la consulta."
        ),
        include_operations=["consultar"],
        auth_config=auth_config,
    )
    mcp.mount_http()
    if auth_config:
        log.info("MCP server montado en /mcp CON descubrimiento OAuth 2.1 (issue #78, ENABLE_MCP_OAUTH=true)")
    else:
        log.info("MCP server montado en /mcp -- solo bearer token, sin OAuth (issue #78, ENABLE_MCP_OAUTH=false)")
