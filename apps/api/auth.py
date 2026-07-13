"""Verificación de JWT de Supabase — identidad del usuario en el backend.

Este proyecto de Supabase firma los tokens con una clave asimétrica ES256
(no el HS256 con secreto compartido de proyectos viejos) — confirmado por
la clave pública real expuesta en el JWKS del proyecto. Eso significa que
no hace falta ningún secreto propio: PyJWT descarga y cachea las claves
públicas desde SUPABASE_URL/auth/v1/.well-known/jwks.json (ya expuesto por
Supabase) y verifica la firma contra la clave pública que corresponda al
'kid' del token. Como son claves públicas, no hay nada sensible que
guardar — y si Supabase rota las claves, PyJWKClient las vuelve a pedir
solas la próxima vez que no encuentra el 'kid'.

NOTA: get_current_user() se llama explícitamente dentro del cuerpo de cada
endpoint (no como Depends() de FastAPI) a propósito — slowapi ya rompió una
vez la resolución de forward-refs de Pydantic al inspeccionar la firma de
una ruta decorada (ver comentario en main.py sobre PEP 563). Evitar tocar
la firma de las rutas decoradas con @limiter.limit() reduce ese riesgo.
"""

import os
from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status
from slowapi.util import get_remote_address

SUPABASE_URL = os.environ["SUPABASE_URL"]
_JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# cache_keys=True: no vuelve a golpear el JWKS en cada request, solo cuando
# aparece un 'kid' que no tiene cacheado (ej. tras una rotación de claves).
_jwks_client = jwt.PyJWKClient(_JWKS_URL, cache_keys=True)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None


def _verify(token: str) -> dict:
    signing_key = _jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256"],
        audience="authenticated",
    )


def get_current_user(request: Request) -> AuthenticatedUser:
    """Extrae y valida el JWT de Supabase del header Authorization.

    Lanza 401 si falta el header, el token es inválido, expiró, o no trae
    el claim 'sub' (id de usuario) que Supabase Auth siempre incluye.
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el header Authorization: Bearer <token>",
        )
    token = auth_header[7:]

    try:
        payload = _verify(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin claim 'sub'")

    return AuthenticatedUser(id=user_id, email=payload.get("email"))


def rate_limit_key(request: Request) -> str:
    """Clave de rate limiting: user_id si hay un JWT válido, IP en caso contrario.

    Se usa como key_func del Limiter — corre ANTES de que el endpoint llame
    a get_current_user(), así que un token inválido cae a IP en vez de
    lanzar 401 aquí (el 401 real lo produce el endpoint, no el limiter).
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        try:
            payload = _verify(auth_header[7:])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except (jwt.InvalidTokenError, jwt.PyJWKClientError):
            pass
    return get_remote_address(request)
