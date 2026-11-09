"""Manejador de errores de validación que nunca falla al serializar.

FastAPI devuelve en cada error el «input» recibido; si el cuerpo trae NaN o Infinity (JSON no estándar que Python sí
acepta), la serialización de la respuesta lanza ValueError y el cliente recibe 500 en lugar de 422. Aquí se descarta
«input» y «ctx» y se conserva ubicación, tipo y mensaje."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def manejar_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    detalle = [{"loc": list(e.get("loc", ())), "type": e.get("type", ""), "msg": e.get("msg", "")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": detalle})
