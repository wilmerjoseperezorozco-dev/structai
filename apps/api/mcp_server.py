"""
Servidor MCP de StructAI -- issue #78.

Expone `/consultar` (normativa NSR-10/NTC/RAS 2000 + precios APU con
trazabilidad, ver rag_multi_norma.ask_delegado()) como herramienta MCP
para clientes de IA (Claude Desktop, Claude Code, cualquier cliente que
hable el protocolo). Reusa el 100% del backend real -- mismo RAG, mismo
motor-apu -- sin duplicar ninguna lógica: fastapi_mcp introspecciona
main.app y envuelve el endpoint HTTP ya existente.

Autenticacion: fastapi_mcp reenvia el header `authorization` tal cual
(comportamiento por defecto, ver `headers` en FastApiMCP.__init__) hacia
la llamada real a /consultar, que ya valida el JWT de Supabase en
auth.get_current_user() -- el mismo token de sesion que el chat web usa
hoy autentica tambien al cliente MCP. No se crea ningun sistema de login
nuevo.

Alcance deliberadamente minimo (decision explicita en el issue): UN
unico tool, solo lectura -- consultar normativa/precios. Nada de
escritura (registrar calculos, modificar datos) todavia. Montado detras
de ENABLE_MCP (default "false"), mismo patron que ENABLE_YOLO/
ENABLE_ESTRUCTURAL -- no cambia nada en produccion sin decision
explicita de habilitarlo.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

log = logging.getLogger("construdata.api")


def montar_mcp(app: FastAPI) -> None:
    """Monta el servidor MCP en /mcp. Debe llamarse DESPUES de que todas
    las rutas de main.py ya esten registradas -- FastApiMCP introspecciona
    app.routes en el momento de construccion, no de forma perezosa."""
    mcp = FastApiMCP(
        app,
        name="StructAI",
        description=(
            "Normativa colombiana de construccion (NSR-10, NTC, RAS 2000) "
            "y precios reales de construccion con trazabilidad normativa, "
            "usando la cuenta de StructAI del usuario que hace la consulta."
        ),
        include_operations=["consultar"],
    )
    mcp.mount_http()
    log.info("MCP server montado en /mcp (issue #78, unico tool: 'consultar')")
