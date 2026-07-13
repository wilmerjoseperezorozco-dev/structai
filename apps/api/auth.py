"""Verificación de JWT de Supabase — identidad del usuario en el backend.

Supabase soporta dos esquemas de firma a la vez durante la transición a
claves asimétricas: el HS256 con "Legacy JWT secret" (el que usan los
tokens ya emitidos, y el dashboard lo marca literalmente "still used") y
las claves ES256/RS256 nuevas publicadas en el JWKS (preparadas para
cuando el proyecto rote a firma asimétrica). Un token real puede llegar
firmado con cualquiera de los dos según cuándo se emitió, así que este
módulo verifica según el 'alg' que declara el header del propio token:

  - alg=HS256  -> se verifica con SUPABASE_JWT_SECRET (secreto compartido).
  - alg=ES256/RS256 -> se verifica contra la clave pública del JWKS que
    corresponda al 'kid' del token (SUPABASE_URL/auth/v1/.well-known/jwks.json).

Restringir el algoritmo de verificación al que YA declaraba el token
(en vez de aceptar cualquiera de la lista) evita el ataque clásico de
"algorithm confusion" (firmar HS256 usando una clave pública RSA/EC como
si fuera el secreto compartido).

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
SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

_JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
# cache_keys=True: no vuelve a golpear el JWKS en cada request, solo cuando
# aparece un 'kid' que no tiene cacheado (ej. tras una rotación de claves).
_jwks_client = jwt.PyJWKClient(_JWKS_URL, cache_keys=True)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None


def _verify(token: str) -> dict:
    alg = jwt.get_unverified_header(token).get("alg")

    if alg == "HS256":
        return jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")

    if alg in ("ES256", "RS256"):
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=[alg], audience="authenticated")

    raise jwt.InvalidAlgorithmError(f"Algoritmo no soportado: {alg}")


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
