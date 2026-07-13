"""Verificación de JWT de Supabase — identidad del usuario en el backend.

Los tokens los emite Supabase Auth (HS256, firmados con SUPABASE_JWT_SECRET,
visible en el dashboard de Supabase en Settings > API > JWT Secret). La
verificación es local con PyJWT — no se llama a Supabase por cada request,
así que no agrega latencia de red.

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

SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None


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
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError as e:
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
            payload = jwt.decode(
                auth_header[7:],
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except jwt.InvalidTokenError:
            pass
    return get_remote_address(request)
