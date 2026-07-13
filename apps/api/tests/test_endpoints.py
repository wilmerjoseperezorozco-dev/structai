"""
Tests de integración end-to-end para la API de Construdata.

Cubre lo que existe de verdad en este backend (no ChromaDB/FAISS ni un
endpoint de carga de PDF en runtime — el corpus normativo se ingesta con
scripts/ingest_*.py, offline; los endpoints de consulta son /ask y
/consultar sobre Supabase pgvector + Groq):

  - Flujo feliz: POST /ask devuelve el shape correcto (respuesta, fuentes,
    normas_citadas, chunks_usados, latencia_ms).
  - Excepciones: módulo RAG no disponible (503), timeout del LLM externo,
    base de datos vectorial (Supabase) sin responder, payload inválido
    (422 automático de Pydantic).
  - /detect con imagen corrupta (el análogo real de "archivo mal formado"
    en este backend, ya que no hay carga de PDF).

Ejecutar: pytest apps/api/tests/ -v
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import ASGITransport, AsyncClient

# Secreto fijo solo para firmar tokens HS256 de prueba (el camino "legacy" que
# Supabase sigue usando en la práctica) — cualquier valor sirve, no es el
# secreto real de producción, mientras lo usen tanto el token de prueba como
# auth.py.
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-solo-para-pytest-no-es-real")

# main.py vive en apps/api/ — se agrega al sys.path para poder importarlo
# como módulo de test sin necesitar el servidor corriendo.
API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

import main as main_module  # noqa: E402  (import después del sys.path.insert es intencional)
import auth as auth_module  # noqa: E402  (después de main: main.py ya corrió load_dotenv())

app = main_module.app

TEST_USER_ID = "00000000-0000-4000-8000-000000000001"

# Supabase soporta dos caminos de firma a la vez (ver auth.py): HS256 con el
# "Legacy JWT secret" (el que de verdad firma los tokens hoy) y ES256 vía
# JWKS (la clave nueva, preparada para cuando el proyecto rote). Los tests
# cubren ambos — el ES256 monkeypatcheando auth._jwks_client para no
# depender de una llamada de red real al JWKS de Supabase en cada corrida.
_TEST_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_OTRA_CLAVE_PRIVADA = ec.generate_private_key(ec.SECP256R1())  # para simular firma ES256 inválida


@pytest.fixture(autouse=True)
def _mock_jwks(monkeypatch):
    """Todos los tests usan la clave pública ES256 de prueba en vez de golpear el JWKS real."""
    fake_key = SimpleNamespace(key=_TEST_PRIVATE_KEY.public_key())
    monkeypatch.setattr(auth_module._jwks_client, "get_signing_key_from_jwt", lambda token: fake_key)


def _bearer_token(user_id: str = TEST_USER_ID, email: str = "ingeniero@test.com", expired: bool = False) -> str:
    """Firma un JWT vía el camino legacy HS256 (el que usa Supabase de verdad hoy)."""
    exp = time.time() - 3600 if expired else time.time() + 3600
    payload = {"sub": user_id, "email": email, "aud": "authenticated", "exp": exp}
    return jwt.encode(payload, os.environ["SUPABASE_JWT_SECRET"], algorithm="HS256")


def _bearer_token_es256(user_id: str = TEST_USER_ID, email: str = "ingeniero@test.com") -> str:
    """Firma un JWT vía el camino ES256/JWKS (la clave nueva, aún no activa en producción)."""
    payload = {"sub": user_id, "email": email, "aud": "authenticated", "exp": time.time() + 3600}
    return jwt.encode(payload, _TEST_PRIVATE_KEY, algorithm="ES256")


@pytest.fixture
async def client():
    """
    Cliente async contra la app en memoria (ASGITransport) — sin levantar uvicorn.

    Trae un JWT válido por default en el header Authorization, porque /ask,
    /consultar, /detect y /apu/calculate ahora requieren autenticación — los
    tests que no son sobre auth no deberían tener que preocuparse por eso.
    Los tests que sí prueban auth pasan su propio header explícito.
    """
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_bearer_token()}"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


# ── Respuesta de RAG simulada (evita golpear Supabase/Groq reales en cada test) ──

RESPUESTA_RAG_MOCK = {
    "respuesta": "El recubrimiento mínimo para vigas expuestas a la intemperie es 40 mm según NSR-10 C.7.7.",
    "normas_citadas": ["NSR-10 C.7.7"],
    "normas_detectadas_router": ["NSR-10"],
    "fuentes": [
        {"norma": "NSR-10", "seccion": "C.7.7", "contenido": "Recubrimiento mínimo...", "score": 0.91}
    ],
    "chunks_usados": 3,
}


# ═══════════════════════════════════════════════════════════════════════════
# FLUJO FELIZ
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_ask_flujo_feliz(client: AsyncClient):
    """POST /ask con una pregunta real -> respuesta con el shape correcto."""
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno — revisar SUPABASE_URL/GROQ_API_KEY")

    with patch("main.rag_ask", return_value=RESPUESTA_RAG_MOCK) as mock_ask:
        res = await client.post(
            "/ask",
            json={"pregunta": "¿Cuál es el recubrimiento mínimo para vigas expuestas?"},
        )

    assert res.status_code == 200
    body = res.json()

    # Claves obligatorias del contrato de respuesta
    for campo in ("respuesta", "normas_citadas", "fuentes", "chunks_usados", "latencia_ms"):
        assert campo in body, f"falta el campo '{campo}' en la respuesta"

    assert body["respuesta"] == RESPUESTA_RAG_MOCK["respuesta"]
    assert body["chunks_usados"] == 3
    assert len(body["fuentes"]) == 1
    assert body["fuentes"][0]["norma"] == "NSR-10"
    assert body["latencia_ms"] >= 0
    mock_ask.assert_called_once()


@pytest.mark.asyncio
async def test_consultar_flujo_feliz(client: AsyncClient):
    """POST /consultar (delegador multi-dominio) -> shape correcto con campo 'dominio'."""
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno")

    mock_delegado = {**RESPUESTA_RAG_MOCK, "dominio": "aquai", "dominio_label": "AquAI"}
    with patch("main.ask_delegado", return_value=mock_delegado):
        res = await client.post(
            "/consultar",
            json={"pregunta": "¿Qué coeficiente C de Hazen-Williams uso para tubería PVC?"},
        )

    assert res.status_code == 200
    body = res.json()
    assert body["dominio"] == "aquai"
    assert body["chunks_usados"] == 3


# ═══════════════════════════════════════════════════════════════════════════
# MANEJO DE EXCEPCIONES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_ask_payload_invalido_422(client: AsyncClient):
    """Sin el campo 'pregunta' -> 422 automático de validación Pydantic, no 500."""
    res = await client.post("/ask", json={})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_ask_modulo_rag_no_disponible_503(client: AsyncClient, monkeypatch):
    """Si RAG_AVAILABLE es False (faltan credenciales/paquete) -> 503, no 500 ni crash."""
    monkeypatch.setattr(main_module, "RAG_AVAILABLE", False)
    res = await client.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code == 503
    assert "RAG no disponible" in res.json()["detail"]


@pytest.mark.asyncio
async def test_ask_timeout_llm_externo(client: AsyncClient):
    """
    Simula que Groq (el LLM externo) excede el timeout. rag_ask() internamente
    llamaría a groq_client.chat.completions.create(), que puede lanzar
    openai.APITimeoutError — se simula genérico con TimeoutError para no
    acoplar el test al SDK de OpenAI. Debe traducirse a un 500 controlado
    con detalle claro, nunca un stack trace crudo al cliente.
    """
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno")

    with patch("main.rag_ask", side_effect=TimeoutError("Groq API timeout tras 30s")):
        res = await client.post("/ask", json={"pregunta": "¿Qué dice la NSR-10 sobre columnas?"})

    assert res.status_code == 500
    assert "Error en RAG" in res.json()["detail"]


@pytest.mark.asyncio
async def test_ask_base_datos_vectorial_caida(client: AsyncClient):
    """
    Simula que Supabase (la base de datos vectorial) no responde —
    ConnectionError en la llamada a search_knowledge(). Igual que el
    timeout: debe devolver 500 controlado, no derribar el proceso.
    """
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno")

    with patch("main.rag_ask", side_effect=ConnectionError("No se pudo conectar a Supabase")):
        res = await client.post("/ask", json={"pregunta": "¿Qué dice la NTC 174?"})

    assert res.status_code == 500
    body = res.json()
    assert "detail" in body


@pytest.mark.asyncio
async def test_detect_imagen_corrupta(client: AsyncClient):
    """
    /detect es el único endpoint real de carga de archivo en este backend
    (imagen, no PDF). Con bytes corruptos, el modo stub debe seguir
    respondiendo 200 con datos deterministas (no depende de decodificar la
    imagen); si hay modelo ONNX real cargado, cv2.imdecode() con bytes
    corruptos retorna None y debe manejarse sin 500 crudo.
    """
    bytes_corruptos = b"esto-no-es-una-imagen-valida" * 10
    res = await client.post(
        "/detect",
        files={"image": ("corrupta.jpg", bytes_corruptos, "image/jpeg")},
    )
    # Aceptamos 200 (stub) o 500 controlado (si el modelo real está cargado
    # y no valida antes de decodificar) — lo que NO es aceptable es un
    # error 5xx sin cuerpo JSON o que el proceso muera.
    assert res.status_code in (200, 500)
    assert res.headers["content-type"].startswith("application/json")


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_health_responde_ok(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] in ("ok", "degraded")
    assert "modulos" in body


# ═══════════════════════════════════════════════════════════════════════════
# AUTENTICACIÓN (JWT de Supabase)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_ask_sin_token_401():
    """Sin header Authorization -> 401, no 422 ni 500 (el cliente `client` sí trae token; este test usa uno propio sin header)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_ask_token_hs256_firma_incorrecta_401():
    """Token HS256 (camino legacy) firmado con un secreto distinto al configurado -> 401."""
    transport = ASGITransport(app=app)
    token_con_otro_secreto = jwt.encode(
        {"sub": TEST_USER_ID, "aud": "authenticated", "exp": time.time() + 3600},
        "otro-secreto-que-no-es-el-configurado",
        algorithm="HS256",
    )
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={"Authorization": f"Bearer {token_con_otro_secreto}"},
    ) as ac:
        res = await ac.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_ask_token_es256_valido_no_da_401():
    """Camino ES256/JWKS (la clave nueva, aún no activa en producción) también debe aceptarse."""
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno")

    transport = ASGITransport(app=app)
    with patch("main.rag_ask", return_value=RESPUESTA_RAG_MOCK):
        async with AsyncClient(
            transport=transport, base_url="http://test",
            headers={"Authorization": f"Bearer {_bearer_token_es256()}"},
        ) as ac:
            res = await ac.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code != 401


@pytest.mark.asyncio
async def test_ask_token_es256_firma_incorrecta_401():
    """Token ES256 firmado con una clave privada distinta a la que expone el JWKS -> 401."""
    transport = ASGITransport(app=app)
    token_con_otra_clave = jwt.encode(
        {"sub": TEST_USER_ID, "aud": "authenticated", "exp": time.time() + 3600},
        _OTRA_CLAVE_PRIVADA,
        algorithm="ES256",
    )
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={"Authorization": f"Bearer {token_con_otra_clave}"},
    ) as ac:
        res = await ac.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_ask_token_expirado_401():
    """Token con firma válida (HS256, camino legacy) pero exp en el pasado -> 401, no 500."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={"Authorization": f"Bearer {_bearer_token(expired=True)}"},
    ) as ac:
        res = await ac.post("/ask", json={"pregunta": "cualquier cosa"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_apu_calculate_requiere_auth(client: AsyncClient):
    """/apu/calculate con token válido (el del fixture `client`) no debe devolver 401."""
    if not main_module.APU_AVAILABLE:
        pytest.skip("APU_AVAILABLE=False en este entorno")
    res = await client.post("/apu/calculate", data={"actividad_id": "C.COL.40X30", "cantidad": "1"})
    assert res.status_code != 401


# ═══════════════════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_rate_limit_ask_bloquea_tras_10_por_minuto(client: AsyncClient):
    """
    /ask está limitado a 10/minute por IP (main.py). Bajo ASGITransport
    todas las peticiones del test comparten la misma IP simulada, así que
    esto reproduce fielmente el comportamiento real: la petición #11 en la
    misma ventana debe devolver 429, no colarse ni tumbar el proceso.
    """
    if not main_module.RAG_AVAILABLE:
        pytest.skip("RAG_AVAILABLE=False en este entorno")

    main_module.limiter.reset()  # aísla este test de cualquier otro que ya haya llamado a /ask

    with patch("main.rag_ask", return_value=RESPUESTA_RAG_MOCK):
        codigos = []
        for _ in range(11):
            res = await client.post("/ask", json={"pregunta": "prueba de límite de tasa"})
            codigos.append(res.status_code)

    assert codigos[:10] == [200] * 10, f"las primeras 10 deberían pasar, se obtuvo: {codigos[:10]}"
    assert codigos[10] == 429, f"la petición #11 debería bloquearse con 429, se obtuvo: {codigos[10]}"

    main_module.limiter.reset()  # no dejar el contador "sucio" para tests que corran después


@pytest.mark.asyncio
async def test_rate_limit_no_afecta_otros_endpoints(client: AsyncClient):
    """Agotar el límite de /ask no debe bloquear /health (endpoints sin límite propio)."""
    main_module.limiter.reset()

    if main_module.RAG_AVAILABLE:
        with patch("main.rag_ask", return_value=RESPUESTA_RAG_MOCK):
            for _ in range(10):
                await client.post("/ask", json={"pregunta": "agotar límite"})

    res = await client.get("/health")
    assert res.status_code == 200

    main_module.limiter.reset()
