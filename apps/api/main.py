"""
══════════════════════════════════════════════════════════════
CONSTRUDATA API — FastAPI Unificado
Sprint 1: Backend que wirea RAG NTC + Motor APU + YOLO Detection
══════════════════════════════════════════════════════════════
Endpoints:
  POST /ask              → RAG multi-norma (NTC + NSR-10 + Seg.Industrial)
  POST /detect           → YOLO detección elementos estructurales (imagen)
  POST /apu/calculate    → Cálculo APU con Monte Carlo
  GET  /apu/list         → Catálogo de APUs disponibles
  GET  /health           → Health check + versión

Wiring:
  packages/construdata/rag_multi_norma.py  → /ask
  packages/motor-apu/src/catalogue.py     → /apu/*
  packages/yolo/model.onnx (entrenar con packages/yolo/train.py) → /detect
    — la inferencia real (_load_onnx_model/_detect_onnx) vive en este mismo
    archivo, no en un módulo separado; corre en modo stub si el .onnx no
    existe todavía (ver packages/yolo/README.md)
"""

# NOTA: sin "from __future__ import annotations" a propósito. Con esa
# importación (PEP 563, anotaciones diferidas como strings), el decorador
# @limiter.limit() de slowapi rompe la resolución de forward-refs de
# Pydantic — el wrapper interno de slowapi no expone los globals de este
# módulo, así que FastAPI no encuentra AskRequest/ConsultarRequest al
# registrar las rutas (NameError). Reproducido y confirmado en un venv
# limpio con las versiones exactas pineadas (fastapi==0.115.5,
# pydantic==2.9.2) antes de quitarla — es la causa raíz real, no una
# corrección especulativa.

import asyncio
import io
import os
import sys
import logging
import time
import zipfile
from pathlib import Path
from typing import Optional

# ── Path setup: permite imports de packages/ desde apps/api ───────────────────
ROOT = Path(__file__).resolve().parents[2]          # monorepo/
sys.path.insert(0, str(ROOT / "packages" / "construdata"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.concurrency import run_in_threadpool

from auth import get_current_user
from cache import TTLCache
from rate_limit import limiter
import apu_excel

from json_logging import setup_logging

setup_logging(level=logging.INFO)
log = logging.getLogger("construdata.api")

# ── Sentry: captura de errores en producción ───────────────────────────────
# Se activa solo si SENTRY_DSN está seteado (no rompe dev local sin cuenta
# configurada). traces_sample_rate bajo (10%) porque el plan free de Sentry
# tiene cuota mensual de eventos — con 100 usuarios piloto no hace falta
# tracear el 100% de requests para detectar errores, solo una muestra
# representativa de performance.
_SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
if _SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
    log.info("✓ Sentry inicializado")
else:
    log.warning("✗ SENTRY_DSN no configurado — errores no se reportan a Sentry")

# ── Registro de uso real ───────────────────────────────────────────────────
# Antes del lanzamiento piloto (2026-08) NO existía captura automática de
# uso: solo quedaba rastro de lo que un usuario guardaba manualmente en
# "Proyectos". Con 100 usuarios de prueba entrando hoy, eso significa cero
# evidencia real de uso salvo que cada quien guarde a mano.
#
# `apu_calculations` y `consultas_history` ya existían en el esquema real
# de Supabase (verificado con list_tables — 0 filas en ambas) con columnas
# que calzan casi 1:1 con APUDesglose y AskResponse: diseñadas para esto
# exactamente, pero nunca conectadas desde el backend. Se usan esas en vez
# de crear una tabla nueva redundante.
#
# Ambas funciones son best-effort y nunca bloquean una respuesta real: si
# el insert falla, se loguea y se sigue — la trazabilidad de uso no puede
# tumbar un cálculo del usuario.
try:
    from supabase import create_client as _create_supabase_client
    _uso_sb = _create_supabase_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
except Exception as e:
    _uso_sb = None
    log.warning(f"✗ registro de uso no disponible: {e}")


def registrar_consulta(
    user_id: str, pregunta: str, respuesta: str,
    normas_citadas: Optional[list] = None, normas_detectadas: Optional[list] = None,
    chunks_usados: int = 0, latencia_ms: int = 0, norma_hint: Optional[str] = None,
) -> None:
    if _uso_sb is None:
        return
    try:
        _uso_sb.table("consultas_history").insert({
            "user_id": user_id, "pregunta": pregunta[:2000], "respuesta": (respuesta or "")[:4000],
            "normas_citadas": normas_citadas or [], "normas_detectadas": normas_detectadas or [],
            "chunks_usados": chunks_usados, "latencia_ms": latencia_ms, "norma_hint": norma_hint,
        }).execute()
    except Exception as e:
        log.warning(f"No se pudo registrar consulta en consultas_history: {e}")


def _construir_registro_apu(
    user_id: str, actividad_id: str, cantidad: float, d: "APUDesglose",
    proyecto_nombre: Optional[str] = None,
) -> dict:
    return {
        "user_id": user_id, "uuid_trazabilidad": d.uuid_trazabilidad, "actividad_id": actividad_id,
        "descripcion": d.descripcion, "unidad": d.unidad, "capitulo": d.capitulo, "cantidad": cantidad,
        "costo_materiales": d.costo_materiales, "costo_mano_obra": d.costo_mano_obra,
        "costo_equipo": d.costo_equipo, "costo_directo": d.costo_directo, "aiu": d.aiu,
        "precio_unitario": d.precio_unitario, "pu_p05": d.pu_p05, "pu_p95": d.pu_p95, "pu_std": d.pu_std,
        "norma_ref": d.norma_ref, "proyecto_nombre": proyecto_nombre,
    }


def registrar_apu_calculo(
    user_id: str, actividad_id: str, cantidad: float, d: "APUDesglose",
    proyecto_nombre: Optional[str] = None,
) -> None:
    if _uso_sb is None:
        return
    try:
        _uso_sb.table("apu_calculations").insert(
            _construir_registro_apu(user_id, actividad_id, cantidad, d, proyecto_nombre)
        ).execute()
    except Exception as e:
        log.warning(f"No se pudo registrar cálculo en apu_calculations: {e}")


def registrar_apu_calculos_lote(registros: list[dict]) -> None:
    """Inserta muchos cálculos de una sola vez (batch de Excel) — una única
    llamada de red a Supabase en vez de una por fila. Con un lote de 200
    filas, insertar una por una era el verdadero cuello de botella (el
    cálculo en sí toma ~1-3ms/fila, medido en vivo; 200 llamadas de red
    secuenciales a Supabase pesan muchísimo más que eso)."""
    if _uso_sb is None or not registros:
        return
    try:
        _uso_sb.table("apu_calculations").insert(registros).execute()
    except Exception as e:
        log.warning(f"No se pudo registrar lote de {len(registros)} cálculos en apu_calculations: {e}")


# ── Límite freemium: proyectos simultáneos ──────────────────────────────────
# Encontrado el 2026-08-02 auditando /proyectos: la página agrupa cálculos
# por apu_calculations.proyecto_nombre, pero ningún endpoint del backend
# escribía ese campo nunca — todo cálculo quedaba con proyecto_nombre=NULL,
# así que "Mis proyectos" nunca podía agrupar nada aunque el usuario
# pensara que estaba usando la función. Igual que el límite de APU/mes,
# "1 proyecto" del plan free (apps/web/src/lib/freemium.ts) estaba en la UI
# pero no se hacía cumplir en ningún lado.
LIMITE_PROYECTOS_FREE = 1


def verificar_limite_proyectos(user_id: str, proyecto_nombre: Optional[str]) -> None:
    """Lanza 402 si un usuario free intenta crear un proyecto NUEVO (nombre
    distinto a los que ya tiene) por encima del límite. Agregar más cálculos
    a un proyecto YA existente (mismo nombre) siempre se permite — el límite
    es sobre proyectos simultáneos, no sobre cálculos dentro de uno.
    Sin nombre de proyecto (cálculo suelto, no asignado) no cuenta contra el
    límite — solo los proyectos nombrados explícitamente se consideran.
    """
    if _uso_sb is None or not proyecto_nombre:
        return
    try:
        perfil = _uso_sb.table("profiles").select("plan").eq("id", user_id).maybe_single().execute()
        plan = (perfil.data or {}).get("plan", "free") if perfil else "free"
        if plan != "free":
            return

        existentes = _uso_sb.table("apu_calculations").select("proyecto_nombre") \
            .eq("user_id", user_id).execute()
        nombres = {r["proyecto_nombre"] for r in (existentes.data or []) if r.get("proyecto_nombre")}
        if proyecto_nombre in nombres:
            return
    except Exception as e:
        log.warning(f"No se pudo verificar límite de proyectos (se deja pasar): {e}")
        return

    if len(nombres) >= LIMITE_PROYECTOS_FREE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"El plan gratis permite {LIMITE_PROYECTOS_FREE} proyecto simultáneo. "
                "Activa Pro en /pricing para proyectos ilimitados."
            ),
        )


# ── Límite freemium: APU/mes ────────────────────────────────────────────────
# Encontrado el 2026-08-01, auditando qué tan "terminado" está el SaaS: el
# límite de "5 APU/mes" del plan gratis está definido en
# apps/web/src/lib/freemium.ts (PLANES.free.apu_por_mes) y se MUESTRA en la
# UI, pero nunca se hace cumplir aquí — cualquiera con el token de un
# usuario free puede llamar /apu/calculate sin límite. Debe mantenerse en
# sync manualmente con ese archivo hasta que exista una fuente única de
# verdad (ej. una tabla de planes en Supabase).
LIMITE_APU_MES_FREE = 5


def _cupo_apu_mes_restante(user_id: str) -> Optional[int]:
    """Cuántos cálculos de APU más puede hacer este usuario este mes.

    None = sin límite (plan pro/pro_anual, o _uso_sb no disponible — mismo
    modo best-effort que el registro de uso: preferible dejar pasar a
    tumbar el piloto por un problema de infraestructura de trazabilidad).
    int >= 0 = cupo real restante del plan free, contando filas reales de
    apu_calculations (no un contador denormalizado — profiles.consultas_mes
    existe pero no tiene lógica de reseteo mensual verificada).

    Extraído como función propia (antes vivía inline en
    verificar_limite_apu_mes) porque /apu/calculate-batch necesita el
    número exacto, no solo un sí/no — un lote de 200 filas debe poder
    calcular las primeras N que sí caben en el cupo y marcar el resto como
    omitidas, en vez de bloquear el archivo completo o dejarlo pasar entero.
    """
    if _uso_sb is None:
        return None
    try:
        perfil = _uso_sb.table("profiles").select("plan").eq("id", user_id).maybe_single().execute()
        plan = (perfil.data or {}).get("plan", "free") if perfil else "free"
        if plan != "free":
            return None

        import datetime
        inicio_mes = datetime.datetime.now(datetime.timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        conteo = _uso_sb.table("apu_calculations").select("id", count="exact") \
            .eq("user_id", user_id).gte("created_at", inicio_mes).execute()
        usados = conteo.count or 0
        return max(0, LIMITE_APU_MES_FREE - usados)
    except Exception as e:
        log.warning(f"No se pudo calcular cupo restante de APU/mes (se deja pasar): {e}")
        return None


def verificar_limite_apu_mes(user_id: str) -> None:
    """Lanza 402 si un usuario del plan free ya agotó su cupo de APU del mes."""
    restante = _cupo_apu_mes_restante(user_id)
    if restante is not None and restante <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Alcanzaste el límite de {LIMITE_APU_MES_FREE} cálculos de APU "
                "del plan gratis este mes. Activa Pro en /pricing para cálculos ilimitados."
            ),
        )

# ── Importaciones lazy para no fallar si falta algún paquete ──────────────────
# `except Exception` (no solo ImportError): rag_multi_norma.py lee credenciales
# con os.environ["..."] a nivel de módulo, que lanza KeyError si falta alguna
# env var — un KeyError sin capturar tumbaría todo el proceso FastAPI, no solo
# el RAG. Con Exception el resto de la API sigue viva y /ask queda en 503.
try:
    from rag_multi_norma import ask as rag_ask, route_query, ask_delegado
    from rag_multi_norma import sb as supabase_client, groq_client
    from rag_multi_norma import RespuestaIAIndisponibleError
    from rag_multi_norma import uso_groq_hoy as _uso_groq_hoy_fn
    from rag_multi_norma import AVISO_RESPONSABILIDAD_PROFESIONAL, aviso_responsabilidad_para_dominio
    RAG_AVAILABLE = True
    log.info("✓ rag_multi_norma cargado")
except Exception as e:
    RAG_AVAILABLE = False
    log.warning(f"✗ rag_multi_norma no disponible: {e}")

try:
    # Independiente de RAG_AVAILABLE: no necesita Supabase ni Groq, solo el
    # servicio geográfico del SGC (con su propio manejo de errores interno,
    # ver sgc_amenaza_sismica.py / sgc_movimientos_masa.py — ninguno lanza).
    import sgc_amenaza_sismica
    import sgc_movimientos_masa
    SGC_AVAILABLE = True
    log.info("✓ sgc_amenaza_sismica + sgc_movimientos_masa cargados")
except Exception as e:
    SGC_AVAILABLE = False
    log.warning(f"✗ sgc_amenaza_sismica/sgc_movimientos_masa no disponible: {e}")

try:
    # Requiere Supabase (RAG_AVAILABLE trae supabase_client) para guardar/leer
    # noticias_relevantes, pero no depende de Groq -- solo Google News RSS.
    import noticias_colombia
    NOTICIAS_AVAILABLE = RAG_AVAILABLE
    if NOTICIAS_AVAILABLE:
        log.info("✓ noticias_colombia cargado")
    else:
        log.warning("✗ noticias_colombia cargado pero RAG_AVAILABLE=False (necesita supabase_client)")
except Exception as e:
    NOTICIAS_AVAILABLE = False
    log.warning(f"✗ noticias_colombia no disponible: {e}")

try:
    # motor-apu usa imports relativos internos (from .models import ...), por
    # eso se carga como paquete real vía importlib en vez de sys.path — mismo
    # patrón que motor-deformacion, evita "attempted relative import with no
    # known parent package".
    import importlib.util as _ilu_apu
    _apu_init = ROOT / "packages" / "motor-apu" / "src" / "__init__.py"
    _spec_apu = _ilu_apu.spec_from_file_location("motor_apu", _apu_init, submodule_search_locations=[str(_apu_init.parent)])
    motor_apu = _ilu_apu.module_from_spec(_spec_apu)
    sys.modules["motor_apu"] = motor_apu
    _spec_apu.loader.exec_module(motor_apu)
    get_apu = motor_apu.get_apu
    listar_actividades = motor_apu.listar_actividades
    CATALOGO_APU = motor_apu.CATALOGO_APU
    from motor_apu.cantidades import (
        Estribos,
        GeometriaElementoConcreto,
        RefuerzoLongitudinal,
        TipoElementoConcreto,
        calcular_apu_dinamico,
    )
    APU_AVAILABLE = True
    log.info(f"✓ motor-apu cargado — {len(CATALOGO_APU)} APUs en catálogo")
except Exception as e:
    APU_AVAILABLE = False
    log.warning(f"✗ motor-apu no disponible: {e}")

try:
    import numpy as np
    # cv2 (opencv-python-headless) + onnxruntime pesan ~200-300MB residentes
    # combinados, y hoy /detect corre en modo stub (no existe un .onnx
    # entrenado real, ver packages/yolo/README.md) — cargarlos igual en una
    # instancia de 2GB es gastar RAM en una función que todavía no entrega
    # valor real. ENABLE_YOLO=true (default false) los prende cuando el
    # modelo esté entrenado o la instancia suba a 4GB+. Mismo patrón que
    # ENABLE_ESTRUCTURAL más abajo.
    if os.getenv("ENABLE_YOLO", "false").lower() == "true":
        import cv2
        import onnxruntime as ort
        YOLO_DEPS = True
    else:
        YOLO_DEPS = False
        log.info("○ YOLO desactivado (ENABLE_YOLO=false) — libera RAM, /detect en modo stub")
except ImportError:
    YOLO_DEPS = False
    log.warning("✗ onnxruntime/cv2 no instalados — /detect en modo stub")

try:
    # motor-deformacion usa imports relativos internos (from .models import ...),
    # por eso se carga como paquete real vía importlib en vez de sys.path — así
    # no colisiona con el nombre genérico "src" de otros packages del monorepo.
    import importlib.util as _ilu
    _md_init = ROOT / "packages" / "motor-deformacion" / "src" / "__init__.py"
    _spec = _ilu.spec_from_file_location("motor_deformacion", _md_init, submodule_search_locations=[str(_md_init.parent)])
    motor_deformacion = _ilu.module_from_spec(_spec)
    sys.modules["motor_deformacion"] = motor_deformacion
    _spec.loader.exec_module(motor_deformacion)
    DEFORM_AVAILABLE = True
    log.info("✓ motor-deformacion cargado")
except Exception as e:
    DEFORM_AVAILABLE = False
    log.warning(f"✗ motor-deformacion no disponible: {e}")

try:
    # routers/aquai.py carga motor-aquai como paquete real vía importlib
    # (mismo patrón que motor-apu/motor-deformacion) y expone un APIRouter
    # ya armado — se monta abajo con app.include_router.
    from routers.aquai import router as aquai_router
    AQUAI_AVAILABLE = True
    log.info("✓ motor-aquai cargado")
except Exception as e:
    AQUAI_AVAILABLE = False
    log.warning(f"✗ motor-aquai no disponible: {e}")

try:
    from routers.geopot import router as geopot_router
    GEOPOT_AVAILABLE = True
    log.info("✓ motor-geopot cargado")
except Exception as e:
    GEOPOT_AVAILABLE = False
    log.warning(f"✗ motor-geopot no disponible: {e}")

try:
    from routers.vias import router as vias_router
    VIAS_AVAILABLE = True
    log.info("✓ motor-vias cargado")
except Exception as e:
    VIAS_AVAILABLE = False
    log.warning(f"✗ motor-vias no disponible: {e}")

try:
    from routers.gerencia import router as gerencia_router
    GERENCIA_AVAILABLE = True
    log.info("✓ motor-gerencia cargado")
except Exception as e:
    GERENCIA_AVAILABLE = False
    log.warning(f"✗ motor-gerencia no disponible: {e}")

# motor-estructural (InfraCortex) carga torch + ifcopenshell + opencv +
# scipy en memoria — solo esas librerías rondan 1-1.5GB. En una instancia
# de 1GB RAM eso deja sin margen al resto de la API (rag_multi_norma con
# el modelo de embeddings, sentence-transformers, etc.), causando que el
# proceso muera/se reinicie en peticiones reales a /ask — confirmado en
# logs de producción. Se apaga por defecto (ENABLE_ESTRUCTURAL=true para
# prenderlo) hasta que la instancia tenga RAM suficiente o el motor se
# reestructure para cargar sus dependencias de forma perezosa (solo al
# primer request a /estructural/*, no al arrancar la API completa).
if os.getenv("ENABLE_ESTRUCTURAL", "false").lower() == "true":
    try:
        from routers.estructural import router as estructural_router
        ESTRUCTURAL_AVAILABLE = True
        log.info("✓ motor-estructural (Infracortex) cargado")
    except Exception as e:
        ESTRUCTURAL_AVAILABLE = False
        log.warning(f"✗ motor-estructural no disponible: {e}")
else:
    ESTRUCTURAL_AVAILABLE = False
    log.info("○ motor-estructural desactivado (ENABLE_ESTRUCTURAL=false) — libera RAM para el resto de la API")


# ════════════════════════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Construdata API",
    version="1.0.0",
    description="Backend unificado: RAG normativo NTC/NSR-10, Motor APU y detección estructural YOLO",
    docs_url="/docs",
    redoc_url="/redoc",
)

# allow_origins=["*"] + allow_credentials=True es una combinación insegura
# real (cualquier sitio puede hacer peticiones autenticadas con las cookies/
# headers del usuario) — encontrado en la auditoría de seguridad 2026-08-01,
# el comentario original ya decía "en producción: dominio específico" pero
# nunca se hizo. CORS_ORIGINS (coma-separado) permite ajustar sin tocar
# código si se agrega un dominio propio más adelante.
#
# Bug real encontrado el 2026-08-03: el default solo traía el dominio largo
# (...-wilmer-perez-s-projects.vercel.app). El proyecto de Vercel expone 3
# dominios (verificado vía API de Vercel: get_project sobre
# prj_BiuMRQKMMo5MJuKxk3jBbvyYGyXg) y el usuario entra por el alias corto
# structai-pi.vercel.app, que no estaba en la lista — cada llamada a la API
# desde ese dominio se rechazaba en el preflight CORS ("Failed to fetch" en
# el navegador, sin ningún log de error en el backend porque la petición
# nunca llega a la ruta).
_CORS_ORIGINS = [
    o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "https://structai-pi.vercel.app,"
        "https://structai-wilmer-perez-s-projects.vercel.app,"
        "https://structai-git-master-wilmer-perez-s-projects.vercel.app,"
        "http://localhost:3000",
    ).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting por IP ──────────────────────────────────────────────────────
# Hoy la API no valida usuario (no hay verificación de Authorization/JWT de
# Supabase en ningún endpoint — confirmado al auditar main.py y el cliente
# del frontend en apps/web/src/lib/api.ts), así que el único identificador
# disponible para limitar es la IP. Esto protege infraestructura/costo
# (Groq se paga por token, un scraper podría agotar el presupuesto en
# minutos) — NO reemplaza el límite freemium de "5 APU/mes" por usuario,
# que hoy no se aplica en el servidor y requiere primero validar el JWT de
# Supabase en cada request (tarea aparte).
#
# Backend en memoria (default de slowapi): correcto para una sola
# instancia — que es el plan actual (Render/Cloud Run, 1 proceso). Si en
# el futuro se escala a múltiples instancias, cada una llevaría su propio
# contador y el límite real efectivo se multiplicaría por el número de
# instancias — en ese punto hace falta un backend compartido (Redis) vía
# `storage_uri="redis://..."` en el Limiter.
#
# key_func=rate_limit_key (auth.py): agrupa por user_id si el request trae
# un JWT válido de Supabase, y cae a IP (get_remote_address) si no — así el
# límite es real "por usuario" para quien está logueado, no solo por IP.
#
# limiter importado desde rate_limit.py (no creado acá): los routers de los
# motores (aquai/geopot/vias/gerencia/estructural) también necesitan esta
# misma instancia para poder decorar sus propios endpoints con
# @limiter.limit(...) — main.py los importa ANTES de este punto, así que
# crear el Limiter acá y que los routers hicieran `from main import limiter`
# sería un import circular contra un módulo a medio inicializar.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Manejador global de excepciones ────────────────────────────────────────
# Antes de esto: una excepción no prevista en cualquier endpoint devolvía el
# 500 crudo de Starlette (o, en el peor caso, dejaba el traceback sin
# loguear con contexto). Con --workers 1 (ver Dockerfile) un solo proceso
# sirve toda la API, así que un error mal manejado en un endpoint no debería
# nunca tumbar el proceso completo — este handler evita que una excepción
# no capturada escale más allá del request que la disparó, y la deja
# logueada con el path/método para poder diagnosticarla. Sentry (si está
# configurado) ya captura el evento automáticamente vía su integración de
# Starlette; este handler es lo que ve el CLIENTE (JSON limpio, sin
# traceback filtrado) y lo que queda en logs si Sentry no está activo.
@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception):
    log.error(
        f"Excepción no manejada en {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detail": str(exc) if os.getenv("DEBUG") == "true" else None},
    )

# Cada router se monta dos veces: en su ruta original (ej. /aquai/...) y de
# nuevo bajo /v1 (ej. /v1/aquai/...) — mismo objeto router, FastAPI permite
# incluir el mismo router más de una vez con prefijos distintos sin duplicar
# lógica ni romper nada de lo que ya llama a la ruta sin prefijo. Ver nota de
# versionado /v1 arriba de /health.
if AQUAI_AVAILABLE:
    app.include_router(aquai_router)
    app.include_router(aquai_router, prefix="/v1")
if GEOPOT_AVAILABLE:
    app.include_router(geopot_router)
    app.include_router(geopot_router, prefix="/v1")
if VIAS_AVAILABLE:
    app.include_router(vias_router)
    app.include_router(vias_router, prefix="/v1")
if GERENCIA_AVAILABLE:
    app.include_router(gerencia_router)
    app.include_router(gerencia_router, prefix="/v1")
if ESTRUCTURAL_AVAILABLE:
    app.include_router(estructural_router)
    app.include_router(estructural_router, prefix="/v1")


# ════════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

class AskRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta en lenguaje natural del ingeniero civil")
    norma_hint: Optional[str] = Field(None, description="Filtro de norma explícito, ej: 'NTC 673'")
    top_k: int = Field(6, ge=1, le=20, description="Chunks a recuperar por norma")

class FuenteChunk(BaseModel):
    norma: str
    seccion: str
    contenido_preview: str
    score: float

class AskResponse(BaseModel):
    respuesta: str
    normas_citadas: list[str]
    normas_detectadas_router: list[str]
    fuentes: list[FuenteChunk]
    chunks_usados: int
    latencia_ms: int
    # Garantía determinística (issue #18) -- SIEMPRE presente en /ask (todo
    # su corpus es normativa_general), nunca generado por el LLM. Ver
    # rag_multi_norma.AVISO_RESPONSABILIDAD_PROFESIONAL.
    aviso_responsabilidad: Optional[str] = None


class ConsultarRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta en lenguaje natural, de cualquier dominio de ingeniería")
    top_k: int = Field(6, ge=1, le=20, description="Chunks a recuperar")

class ConsultarResponse(BaseModel):
    dominio: str
    dominio_label: str
    respuesta: str
    normas_citadas: list[str]
    fuentes: list[FuenteChunk]
    chunks_usados: int
    latencia_ms: int
    # Garantía determinística (issue #18) -- solo para dominios de diseño
    # (normativa_general/geopot/aquai/vias), None para apu_precios/gerencia.
    # Nunca generado por el LLM. Ver rag_multi_norma.aviso_responsabilidad_para_dominio().
    aviso_responsabilidad: Optional[str] = None


class APUItem(BaseModel):
    id: str
    descripcion: str
    unidad: str
    capitulo: str
    precio_unitario: float
    ic90_inf: float
    ic90_sup: float
    incertidumbre_pct: float
    norma_ref: Optional[str] = None

class APUDesglose(BaseModel):
    actividad_id: str
    descripcion: str
    unidad: str
    capitulo: str
    costo_materiales: float
    costo_mano_obra: float
    costo_equipo: float
    costo_directo: float
    aiu: float
    precio_unitario: float
    pu_p05: float
    pu_p95: float
    pu_std: float
    norma_ref: Optional[str] = None
    uuid_trazabilidad: str
    timestamp: str

class RefuerzoLongitudinalRequest(BaseModel):
    numero_barras: int = Field(..., gt=0, description="Número de barras longitudinales")
    diametro_pulg: str = Field(..., description="Clave del diámetro: 3, 4, 5, 6, 7 u 8 (octavos de pulgada)")

class EstribosRequest(BaseModel):
    diametro_pulg: str = Field(..., description="Clave del diámetro del estribo")
    espaciamiento_m: float = Field(..., gt=0, description="Separación entre estribos (m)")
    gancho_desarrollo_m: float = Field(0.10, ge=0, description="Longitud extra por los 2 ganchos a 135°")

class APUCantidadesRequest(BaseModel):
    tipo: str = Field(..., description="'columna' o 'viga'")
    base_m: float = Field(..., gt=0, description="Base de la sección (m)")
    altura_m: float = Field(..., gt=0, description="Altura de la sección (m)")
    longitud_m: float = Field(..., gt=0, description="Longitud del elemento (m)")
    recubrimiento_m: float = Field(0.04, gt=0, description="Recubrimiento libre NSR-10 C.7.7 (m)")
    calidad_concreto: str = Field("3000", description="2000, 2500, 3000 o 4000 (PSI)")
    refuerzo_longitudinal: Optional[RefuerzoLongitudinalRequest] = None
    estribos: Optional[EstribosRequest] = None
    incluye_cara_superior_formaleta: bool = Field(
        False, description="True si la viga es aislada (se forman las 4 caras)"
    )
    proyecto_nombre: Optional[str] = Field(None, description="Nombre opcional del proyecto para agrupar en /proyectos")

class DeteccionElemento(BaseModel):
    clase: str
    confianza: float
    bbox: list[float]           # [x1, y1, x2, y2] normalizadas
    apu_sugerido_id: Optional[str] = None
    apu_descripcion: Optional[str] = None
    alerta_seguridad: Optional[str] = None
    norma_ref_seguridad: Optional[str] = None

class DetectResponse(BaseModel):
    elementos_detectados: list[DeteccionElemento]
    imagen_ancho: int
    imagen_alto: int
    modelo_version: str
    latencia_ms: int
    modo: str                   # "onnx" | "stub"


class CargaInput(BaseModel):
    tipo: str = Field(..., description="'puntual' o 'distribuida_uniforme'")
    magnitud: float = Field(..., gt=0, description="N (puntual) o N/m (distribuida)")
    posicion: Optional[float] = Field(None, ge=0, le=1, description="Fracción 0..1 de la luz (solo puntual)")
    cov_carga: float = Field(0.15, ge=0, le=1, description="Coeficiente de variación de la carga")
    descripcion: str = ""


class DeformRequest(BaseModel):
    clase: str = Field(..., description="Clase detectada por /detect: columna, viga, placa_aligerada, muro_bloque_15, muro_bloque_10, muro_concreto")
    cargas: list[CargaInput] = Field(..., min_length=1)
    longitud: Optional[float] = Field(None, gt=0, description="Luz/altura libre en metros (si no se envía, usa el valor típico de catálogo)")
    run_montecarlo: bool = True


class DeformResponse(BaseModel):
    elemento_id: str
    tipo_analisis: str
    deflexion_max_mm: float
    deflexion_admisible_mm: float
    cumple_deflexion: bool
    momento_max_Nm: float
    cortante_max_N: float
    esfuerzo_flexion_max_MPa: float
    esfuerzo_cortante_max_MPa: float
    factor_seguridad: float
    cumple_esfuerzo: bool
    carga_critica_pandeo_kN: Optional[float] = None
    esfuerzo_p05_MPa: float
    esfuerzo_p95_MPa: float
    indice_confiabilidad: float
    probabilidad_falla: float
    notas: list[str]


# ════════════════════════════════════════════════════════════════════════════════
# YOLO DETECTOR (ONNX o stub)
# ════════════════════════════════════════════════════════════════════════════════

# Mapa clase → APU sugerido. Solo columna/viga/acero_refuerzo tienen match
# 1:1 con el modelo real (packages/yolo/, ver abajo) — el resto son clases
# de un catálogo más amplio que no tiene todavía elemento entrenado
# correspondiente (placa_aligerada/zapata/excavación) o son deliberadamente
# ambiguas desde una foto sola (muro_bloque_15 vs muro_concreto: el material
# exacto no se puede inferir de una imagen, ver CLASES_MODELO/"muro").
CLASE_APU_MAP: dict[str, tuple[str, str]] = {
    "columna":          ("C.COL.40X30",  "Columna estructural 40×30 cm"),
    "viga":             ("C.VIG.30X40",  "Viga estructural 30×40 cm"),
    "placa_aligerada":  ("C.PLA.ALIG",   "Placa aligerada h=20 cm"),
    "muro_bloque_15":   ("D.MUR.BLQ15",  "Muro bloque concreto e=15 cm"),
    "muro_bloque_10":   ("D.MUR.BLQ10",  "Muro bloque concreto e=10 cm"),
    "muro_concreto":    ("C.MUR.10",     "Muro concreto 10 cm"),
    "zapata":           ("C.ZAP.120",    "Zapata aislada 120×120×45 cm"),
    "acero_refuerzo":   ("C.ACE.G60",    "Acero corrugado G-60"),
    "excavacion":       ("H.EXC.MAN",    "Excavación manual"),
}

# Modelo de elementos estructurales (packages/yolo/) — 7 clases, dataset real
# de obra (18/59 fotos etiquetadas al momento de escribir esto, ver
# packages/yolo/README.md para el estado exacto y cómo completar el resto).
# El orden de CLASES_MODELO DEBE coincidir exactamente con el orden de
# clases de packages/yolo/dataset/data.yaml (índices 0-6) — un desajuste de
# orden hace que el modelo "acierte" internamente pero el backend etiquete
# mal la clase. Verificar contra el data.yaml real antes de activar el
# modelo entrenado.
CLASES_MODELO = [
    "acero_refuerzo",
    "viga",
    "columna",
    "muro",
    "formaleta",
    "tuberia",
    "trabajador",
]

# Descripción legible para clases sin match de costo en CLASE_APU_MAP
# (material/uso ambiguo desde una sola foto — no se fuerza un id de APU).
CLASE_DESCRIPCION_SIN_APU: dict[str, str] = {
    "muro":     "Muro (verificar material y espesor en sitio)",
    "formaleta": "Formaleta / encofrado",
    "tuberia":  "Tubería (verificar diámetro y uso en sitio)",
}

# Recordatorios de seguridad — deliberadamente formulados como "verificar",
# no como afirmación de cumplimiento: el modelo detecta la presencia del
# elemento, no si cumple la norma (p.ej. "trabajador" no distingue si trae
# EPP puesto). Ver origen de la funcionalidad: idea inicial de la app era
# documentar precauciones de obra con fotos.
NOTAS_SEGURIDAD: dict[str, tuple[str, str]] = {
    "trabajador": (
        "Trabajador detectado — verificar EPP visible (casco, arnés, chaleco)",
        "Resolución 0312 de 2019 — EPP mínimo obligatorio",
    ),
    "acero_refuerzo": (
        "Acero de refuerzo visible — verificar protección contra empalamiento si hay tránsito de personal cerca",
        "Resolución 0312 de 2019 — riesgos de punción/empalamiento",
    ),
}

# Clases del modelo stub (reemplazar con labels del modelo real)
STUB_CLASES = list(CLASE_APU_MAP.keys())

_onnx_session: Optional["ort.InferenceSession"] = None  # type: ignore[name-defined]

def _load_onnx_model() -> Optional["ort.InferenceSession"]:  # type: ignore[name-defined]
    """Carga el modelo ONNX si existe en packages/yolo/model.onnx"""
    if not YOLO_DEPS:
        return None
    model_path = ROOT / "packages" / "yolo" / "model.onnx"
    if not model_path.exists():
        log.warning(f"Modelo YOLO no encontrado en {model_path} — usando stub")
        return None
    try:
        session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        log.info(f"✓ Modelo YOLO ONNX cargado desde {model_path}")
        return session
    except Exception as e:
        log.error(f"Error cargando modelo ONNX: {e}")
        return None


def _detect_onnx(img_bytes: bytes, session: "ort.InferenceSession") -> list[DeteccionElemento]:  # type: ignore[name-defined]
    """Inferencia real con YOLOv8/v11 ONNX — misma cabeza anchor-free, output shape [1, num_classes+4, anchors]"""
    import numpy as np
    import cv2

    # Decode + resize
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    img_h, img_w = img.shape[:2]

    # Pre-process: BGR→RGB, resize 640×640, normalize
    inp = cv2.resize(img, (640, 640))
    inp = inp[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    inp = np.expand_dims(inp, 0)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: inp})[0]   # [1, 4+nc, 8400]

    predictions = outputs[0].T                          # [8400, 4+nc]
    conf_threshold = 0.4

    candidatos: list[tuple[float, float, float, float, float, int]] = []  # x1,y1,x2,y2,conf,class_id
    for pred in predictions:
        boxes = pred[:4]
        scores = pred[4:]
        class_id = int(np.argmax(scores))
        conf = float(scores[class_id])
        if conf < conf_threshold:
            continue

        cx, cy, w, h = boxes
        x1 = max(0.0, (cx - w / 2) / 640)
        y1 = max(0.0, (cy - h / 2) / 640)
        x2 = min(1.0, (cx + w / 2) / 640)
        y2 = min(1.0, (cy + h / 2) / 640)
        candidatos.append((x1, y1, x2, y2, conf, class_id))

    # Supresión de no-máximos (NMS): sin esto, un mismo objeto real genera
    # varias cajas superpuestas casi idénticas en vez de una sola limpia.
    # Greedy IoU — suficiente para un modelo de 7 clases, no hace falta
    # traer una librería aparte solo para esto.
    def iou(a: tuple, b: tuple) -> float:
        ax1, ay1, ax2, ay2 = a[:4]
        bx1, by1, bx2, by2 = b[:4]
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    candidatos.sort(key=lambda c: c[4], reverse=True)
    conservados: list[tuple] = []
    nms_iou_threshold = 0.5
    for c in candidatos:
        if all(iou(c, k) < nms_iou_threshold or c[5] != k[5] for k in conservados):
            conservados.append(c)

    detecciones: list[DeteccionElemento] = []
    for x1, y1, x2, y2, conf, class_id in conservados:
        clase = (
            CLASES_MODELO[class_id]
            if class_id < len(CLASES_MODELO)
            else f"clase_{class_id}"
        )
        apu_id, apu_desc = CLASE_APU_MAP.get(clase, (None, CLASE_DESCRIPCION_SIN_APU.get(clase)))
        alerta, norma_ref = NOTAS_SEGURIDAD.get(clase, (None, None))

        detecciones.append(DeteccionElemento(
            clase=clase,
            confianza=round(conf, 3),
            bbox=[round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)],
            apu_sugerido_id=apu_id,
            apu_descripcion=apu_desc,
            alerta_seguridad=alerta,
            norma_ref_seguridad=norma_ref,
        ))

    return sorted(detecciones, key=lambda d: d.confianza, reverse=True)


def _detect_stub(img_bytes: bytes) -> tuple[list[DeteccionElemento], int, int]:
    """Stub deterministico para desarrollo sin modelo ONNX."""
    import hashlib
    import struct

    # Dimensiones placeholder
    img_w, img_h = 640, 480

    # Genera detecciones pseudo-aleatorias basadas en hash de la imagen
    h = hashlib.md5(img_bytes).digest()
    seed = struct.unpack("<I", h[:4])[0]

    import random
    rng = random.Random(seed)

    n = rng.randint(1, 3)
    detecciones: list[DeteccionElemento] = []
    clases_muestra = CLASES_MODELO

    for i in range(n):
        clase = clases_muestra[i % len(clases_muestra)]
        conf = round(rng.uniform(0.62, 0.94), 3)
        x1 = round(rng.uniform(0.05, 0.4), 4)
        y1 = round(rng.uniform(0.05, 0.4), 4)
        x2 = round(min(x1 + rng.uniform(0.1, 0.35), 0.95), 4)
        y2 = round(min(y1 + rng.uniform(0.1, 0.35), 0.95), 4)
        apu_id, apu_desc = CLASE_APU_MAP.get(clase, (None, CLASE_DESCRIPCION_SIN_APU.get(clase)))
        alerta, norma_ref = NOTAS_SEGURIDAD.get(clase, (None, None))
        detecciones.append(DeteccionElemento(
            clase=clase, confianza=conf,
            bbox=[x1, y1, x2, y2],
            apu_sugerido_id=apu_id,
            apu_descripcion=apu_desc,
            alerta_seguridad=alerta,
            norma_ref_seguridad=norma_ref,
        ))

    return sorted(detecciones, key=lambda d: d.confianza, reverse=True), img_w, img_h


# ════════════════════════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════════════════════════

def _prewarm_embeddings_blocking() -> None:
    # _embedding_model() es @lru_cache — la primera vez que se llama importa
    # sentence_transformers/torch desde cero, lo cual toma ~17s reales
    # dentro de un proceso que ya cargó FastAPI + Supabase + los 6 motores.
    # Sin precalentar, esa demora caía sobre la PRIMERA consulta real de un
    # usuario a /ask. Función síncrona a propósito: debe invocarse via
    # asyncio.to_thread() para no bloquear el event loop (ver startup()).
    t0 = time.perf_counter()
    try:
        from rag_multi_norma import embed_query
        embed_query("precalentamiento")
        log.info(f"✓ Modelo de embeddings precalentado en {time.perf_counter() - t0:.1f}s")
    except Exception as e:
        log.warning(f"✗ No se pudo precalentar el modelo de embeddings: {e}")


_INTERVALO_NOTICIAS_SEGUNDOS = 3 * 3600  # cada 3 horas -- suficiente para "en vivo"
# real sin golpear Google News RSS con una frecuencia que parezca abuso


async def _ciclo_noticias():
    """Loop en background que actualiza noticias_relevantes cada
    _INTERVALO_NOTICIAS_SEGUNDOS. asyncio.create_task() en vez de un cron
    externo -- no agrega infraestructura nueva (nada de APScheduler ni un
    job separado en DigitalOcean), vive dentro del mismo proceso que ya
    está corriendo 24/7. httpx (síncrono) se corre en un hilo aparte vía
    asyncio.to_thread() para no bloquear el event loop mientras trae los
    9 feeds RSS."""
    while True:
        try:
            resumen = await asyncio.to_thread(noticias_colombia.actualizar_noticias, supabase_client)
            log.info(f"Noticias Colombia actualizadas: {resumen}")
        except Exception as e:
            log.warning(f"Ciclo de noticias falló, se reintenta en el próximo intervalo: {e}")
        await asyncio.sleep(_INTERVALO_NOTICIAS_SEGUNDOS)


@app.on_event("startup")
async def startup():
    global _onnx_session
    _onnx_session = _load_onnx_model()

    if NOTICIAS_AVAILABLE:
        asyncio.create_task(_ciclo_noticias())

    # asyncio.to_thread(), NO awaited: deja el event loop libre para
    # responder /health de inmediato mientras el modelo se carga en
    # paralelo en un hilo aparte. En la instancia anterior de 1GB RAM esto
    # causó un ciclo real de caídas (memoria insuficiente para sostener
    # torch+sentence-transformers junto al resto de la API, confirmado en
    # logs de producción: 3 reinicios consecutivos). Tras subir a
    # apps-s-1vcpu-2gb (2026-07-30), memoria disponible verificada vía
    # /health?deep=true: 1635MB libres (antes 611MB) — margen suficiente.
    if RAG_AVAILABLE:
        asyncio.create_task(asyncio.to_thread(_prewarm_embeddings_blocking))

    log.info("Construdata API lista ✓")


# ════════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

# ── Health ────────────────────────────────────────────────────────────────────
# Distinción liveness/readiness: GET /health (sin parámetros) es barato y
# rápido — solo confirma que el proceso está vivo y qué módulos cargaron al
# arrancar (útil para un liveness probe que se llama cada pocos segundos).
# GET /health?deep=true hace chequeos ACTIVOS contra dependencias externas
# reales (Supabase, Groq, RAM) — más lento y con costo real (una consulta,
# una llamada al LLM), pensado para un readiness probe o un dashboard de
# monitoreo que se consulta con menor frecuencia, no en cada health check.

def _check_supabase_latencia() -> dict:
    """Ping real a Supabase (no solo '¿se importó el cliente?') — mide latencia."""
    if not RAG_AVAILABLE:
        return {"disponible": False, "error": "módulo RAG no cargado (revisar SUPABASE_URL/SUPABASE_SERVICE_KEY)"}
    t0 = time.perf_counter()
    try:
        supabase_client.table("motor_chunks").select("id").limit(1).execute()
        return {"disponible": True, "latencia_ms": round((time.perf_counter() - t0) * 1000, 1)}
    except Exception as e:
        log.error(f"Health check Supabase falló: {e}")
        return {"disponible": False, "error": str(e)}


def _check_llm_provider() -> dict:
    """
    Verifica que Groq responda, sin gastar una llamada de chat completo
    (cara/lenta): lista modelos, que es barato, con timeout corto explícito
    para que un LLM caído no cuelgue el propio health check.
    """
    if not RAG_AVAILABLE:
        return {"disponible": False, "error": "módulo RAG no cargado (revisar GROQ_API_KEY)"}
    t0 = time.perf_counter()
    try:
        groq_client.models.list(timeout=3.0)
        return {"disponible": True, "latencia_ms": round((time.perf_counter() - t0) * 1000, 1)}
    except Exception as e:
        log.error(f"Health check Groq falló: {e}")
        return {"disponible": False, "error": str(e)}


def _check_memoria() -> dict:
    """
    RAM del proceso, comparada contra el límite real de la instancia.

    Encontrado el 2026-08-01: tanto psutil.virtual_memory() como la lectura
    directa de /sys/fs/cgroup/memory.max reportan memoria del host
    compartido en DigitalOcean App Platform, no del contenedor real (el
    panel oficial de DO mostraba 58% de uso mientras esto marcaba 97%,
    verificado dos veces) — el runtime de contenedores de DO no expone el
    límite real por ninguna de las dos vías estándar. En vez de seguir
    adivinando rutas de cgroup sin poder verificarlas contra el contenedor
    real, se usa proceso_rss_mb (consistente y confiable en todas las
    mediciones) comparado contra RAM_INSTANCIA_MB, que el operador configura
    a mano con el tamaño real del plan (ej. 2048 para una instancia de 2GB,
    visible en el panel de DO). Sin esa env var, no se afirma "critico" —
    mejor no dar una señal que reportar una falsa otra vez.
    """
    try:
        import psutil
        proceso = psutil.Process(os.getpid())
        proceso_rss_mb = round(proceso.memory_info().rss / (1024 * 1024), 1)

        limite_mb = os.getenv("RAM_INSTANCIA_MB")
        if limite_mb:
            limite_mb = float(limite_mb)
            pct_usado = round(proceso_rss_mb / limite_mb * 100, 1)
            critico = pct_usado > 85
        else:
            pct_usado = None
            critico = False

        return {
            "proceso_rss_mb": proceso_rss_mb,
            "ram_instancia_mb": limite_mb,
            "pct_usado": pct_usado,
            "critico": critico,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Versionado /v1 ────────────────────────────────────────────────────────────
# Cada endpoint queda registrado dos veces: en su ruta original (sin prefijo,
# la que ya usa apps/web hoy — nunca se toca, cero riesgo de romper el
# frontend actual) y en /v1/<misma-ruta> (para el día en que haya que romper
# un contrato y necesitemos poder mover clientes nuevos a /v1 mientras /v2
# se estabiliza, sin tumbar a nadie que siga en la ruta vieja). Apilar varios
# decoradores @app.X(...) sobre la misma función es el mismo patrón que ya
# usaba /health con GET+HEAD — FastAPI registra rutas adicionales apuntando
# al mismo handler, no crea una copia ni cambia el comportamiento.
@app.get("/health", tags=["Sistema"])
@app.head("/health", tags=["Sistema"])
@app.get("/v1/health", tags=["Sistema"])
@app.head("/v1/health", tags=["Sistema"])
def health(deep: bool = False):
    """
    Health check con estado de cada módulo.

    - `?deep=true` agrega chequeos activos: latencia real de Supabase,
      disponibilidad del proveedor LLM (Groq) y uso de RAM. Úsalo para
      monitoreo/alertas, no como liveness probe de alta frecuencia — cada
      llamada con deep=true golpea servicios externos de verdad.
    - También responde HEAD (no solo GET): UptimeRobot y la mayoría de
      monitores HTTP usan HEAD por defecto, no GET — encontrado el
      2026-08-01, causaba 405 en cada chequeo y 4 "incidentes" falsos en
      24h (37.8% uptime reportado, sitio real nunca estuvo caído).
    """
    modulos = {
        "rag_multi_norma":   RAG_AVAILABLE,
        "motor_apu":         APU_AVAILABLE,
        "motor_deformacion": DEFORM_AVAILABLE,
        "motor_aquai":       AQUAI_AVAILABLE,
        "motor_geopot":      GEOPOT_AVAILABLE,
        "motor_vias":        VIAS_AVAILABLE,
        "motor_gerencia":    GERENCIA_AVAILABLE,
        "motor_estructural": ESTRUCTURAL_AVAILABLE,
        "yolo_onnx":         _onnx_session is not None,
        "yolo_deps":         YOLO_DEPS,
    }

    resultado = {
        "status": "ok",
        "version": "1.0.0",
        "modulos": modulos,
        "apu_count": len(CATALOGO_APU) if APU_AVAILABLE else 0,
    }

    if not deep:
        return resultado

    supabase_check = _check_supabase_latencia()
    llm_check = _check_llm_provider()
    memoria_check = _check_memoria()
    uso_groq = _uso_groq_hoy_fn() if RAG_AVAILABLE else {"error": "rag_multi_norma no disponible"}

    resultado["dependencias"] = {
        "supabase": supabase_check,
        "llm_groq": llm_check,
        "memoria": memoria_check,
        "uso_groq_hoy": uso_groq,
    }

    # "degraded" si algo activo falló pero el proceso sigue vivo y sirviendo;
    # nunca se retorna 5xx aquí — un monitor necesita poder leer el detalle
    # de QUÉ falló, no solo recibir un error genérico.
    fallas = not supabase_check.get("disponible", True) or not llm_check.get("disponible", True)
    if fallas or memoria_check.get("critico"):
        resultado["status"] = "degraded"

    return resultado


# ── /data-status — escala real de datos, público a propósito ────────────────
# Sin auth (Depends(get_current_user)) DELIBERADAMENTE: es para que cualquiera
# (inversor, socio, institución) pueda verificar la escala real del proyecto
# sin pedir acceso — issue #3 (auditoría externa de visibilidad, 2026-08-20).
# Todos los conteos son consultas en vivo contra Supabase (count="exact"),
# nunca cifras hardcodeadas en el código — si un corpus crece o se corrige,
# esto refleja el cambio de inmediato sin necesitar deploy.

def _contar_filas(tabla: str) -> Optional[int]:
    try:
        r = supabase_client.table(tabla).select("id", count="exact").limit(1).execute()
        return r.count
    except Exception as e:
        log.warning(f"/data-status: no se pudo contar '{tabla}': {e}")
        return None


def _ultima_fila(tabla: str) -> Optional[str]:
    try:
        r = (
            supabase_client.table(tabla)
            .select("created_at")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return r.data[0]["created_at"] if r.data else None
    except Exception as e:
        log.warning(f"/data-status: no se pudo leer última fecha de '{tabla}': {e}")
        return None


@app.get("/data-status", tags=["Sistema"])
@app.get("/v1/data-status", tags=["Sistema"])
def data_status():
    """
    Estado real y verificable de los datos cargados en StructAI — público,
    sin autenticación a propósito, para demostrar escala sin requerir login.

    No reemplaza /health (eso es salud técnica del servicio); esto es
    "cuántos datos normativos/de precios hay realmente cargados y cuándo se
    actualizaron por última vez", pensado para inversores/socios/instituciones.
    """
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo de datos no disponible. Verificar SUPABASE_URL/SUPABASE_SERVICE_KEY.",
        )

    corpus_normativo = {
        "nsr10_chunks": {
            "descripcion": "NSR-10 — Reglamento colombiano de construcción sismo resistente",
            "chunks": _contar_filas("nsr10_chunks"),
            "ultima_actualizacion": _ultima_fila("nsr10_chunks"),
        },
        "ntc_chunks": {
            "descripcion": "NTC (ICONTEC) + SGSST (Decreto 1072, Ley 1562, Res. 0312)",
            "chunks": _contar_filas("ntc_chunks"),
            "ultima_actualizacion": _ultima_fila("ntc_chunks"),
        },
        "motor_chunks": {
            "descripcion": "Corpus propio por motor: AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia",
            "chunks": _contar_filas("motor_chunks"),
            "ultima_actualizacion": _ultima_fila("motor_chunks"),
        },
    }

    base_de_precios = {
        "apu_precios_referencia": {
            "descripcion": "Actividades de construcción con precio de referencia",
            "filas": _contar_filas("apu_precios_referencia"),
        },
        "apu_insumos_referencia": {
            "descripcion": "Insumos (material/mano de obra/equipo) desglosados por actividad",
            "filas": _contar_filas("apu_insumos_referencia"),
        },
        "apu_proveedores_catalogo": {
            "descripcion": "SKU con precio verificado de proveedores locales (Atlántico)",
            "filas": _contar_filas("apu_proveedores_catalogo"),
        },
        "apu_proveedores_nacional": {
            "descripcion": "Proveedores mipyme reales a nivel nacional (IAD MIPYMES, Colombia Compra Eficiente)",
            "filas": _contar_filas("apu_proveedores_nacional"),
        },
        "apu_precios_nacional_detalle": {
            "descripcion": "Precios individuales por proveedor nacional (permite comparar, no solo mediana)",
            "filas": _contar_filas("apu_precios_nacional_detalle"),
        },
    }

    motores_activos = [
        nombre
        for nombre, disponible in {
            "apu": APU_AVAILABLE,
            "deformacion": DEFORM_AVAILABLE,
            "aquai": AQUAI_AVAILABLE,
            "geopot": GEOPOT_AVAILABLE,
            "vias": VIAS_AVAILABLE,
            "gerencia": GERENCIA_AVAILABLE,
            "estructural": ESTRUCTURAL_AVAILABLE,
        }.items()
        if disponible
    ]

    return {
        "fuente": "conteos en vivo contra Supabase — no son cifras fijas en el código",
        "corpus_normativo": corpus_normativo,
        "base_de_precios": base_de_precios,
        "motores_activos": motores_activos,
        "regiones_cubiertas": {
            "detallado": ["Atlántico"],
            "referencia_nacional": ["Colombia (vía IAD MIPYMES / Colombia Compra Eficiente)"],
        },
        "roadmap": "https://github.com/wilmerjoseperezorozco-dev/structai/milestone/1",
    }


# ── /ask — RAG Multi-Norma ───────────────────────────────────────────────────

# Cachea la respuesta COMPLETA de rag_ask() (texto + fuentes + normas
# citadas), no solo el texto — así una pregunta repetida se salta embedding
# + búsqueda híbrida en Supabase + la llamada real a Groq/OpenAI por
# completo, no solo el último paso. TTL de 6h: el contenido normativo que
# respalda la respuesta cambia poco (se actualiza a mano vía scripts de
# ingesta), y esto además reduce consumo real de tokens de Groq — ver
# hallazgo de cuota diaria agotándose con uso real.
_cache_ask = TTLCache(ttl_seconds=6 * 3600, max_size=1000)


def _clave_cache_ask(pregunta: str, norma_hint: Optional[str], top_k: int) -> str:
    return f"{pregunta.strip().lower()}|{(norma_hint or '').strip().lower()}|{top_k}"


@app.post("/ask", response_model=AskResponse, tags=["Normativa"])
@app.post("/v1/ask", response_model=AskResponse, tags=["Normativa"])
@limiter.limit("10/minute")
def ask_norma(request: Request, req: AskRequest):
    """
    Consulta RAG multi-norma.

    Detecta automáticamente qué NTC/NSR-10/Res. aplica a la pregunta,
    busca los chunks relevantes en Supabase (pgvector + BM25 híbrido, embeddings
    locales) y sintetiza la respuesta con Groq (llama-3.3-70b-versatile) citando
    las fuentes — respuestas en 1-3 segundos.

    Ejemplo:
        {"pregunta": "¿Qué resistencia mínima necesito para columnas sísmicas?"}
    """
    user = get_current_user(request)

    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo RAG no disponible. Verificar SUPABASE_URL/SUPABASE_SERVICE_KEY y GROQ_API_KEY."
        )

    clave_cache = _clave_cache_ask(req.pregunta, req.norma_hint, req.top_k)
    result = _cache_ask.get(clave_cache)
    cache_hit = result is not None

    if cache_hit:
        log.info("Consulta /ask (cache hit)", extra={"user_id": user.id, "endpoint": "/ask"})
        latencia = 0
    else:
        log.info("Consulta /ask", extra={"user_id": user.id, "endpoint": "/ask"})
        t0 = time.perf_counter()
        try:
            result = rag_ask(
                question=req.pregunta,
                norma_hint=req.norma_hint,
                top_k=req.top_k,
            )
        except RespuestaIAIndisponibleError as e:
            log.error(f"IA no disponible (Groq + respaldo OpenAI): {e}", extra={"user_id": user.id, "endpoint": "/ask"})
            raise HTTPException(status_code=503, detail="Servicio de IA saturado temporalmente. Intenta de nuevo en unos minutos.")
        except Exception as e:
            log.error(f"Error RAG: {e}", exc_info=True, extra={"user_id": user.id, "endpoint": "/ask"})
            raise HTTPException(status_code=500, detail=f"Error en RAG: {str(e)}")

        latencia = int((time.perf_counter() - t0) * 1000)
        _cache_ask.set(clave_cache, result)

    fuentes = [
        FuenteChunk(
            norma=f.get("norma", ""),
            seccion=f.get("seccion", ""),
            contenido_preview=f.get("contenido", "")[:200],
            score=round(float(f.get("score", 0.0)), 4),
        )
        for f in result.get("fuentes", [])
    ]

    registrar_consulta(
        user.id, req.pregunta, result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        normas_detectadas=result.get("normas_detectadas_router", []),
        chunks_usados=result.get("chunks_usados", 0), latencia_ms=latencia, norma_hint=req.norma_hint,
    )

    return AskResponse(
        respuesta=result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        normas_detectadas_router=result.get("normas_detectadas_router", []),
        fuentes=fuentes,
        chunks_usados=result.get("chunks_usados", 0),
        latencia_ms=latencia,
        # /ask es SIEMPRE normativa_general -- el aviso aplica al 100% de
        # sus respuestas, garantizado aquí, no depende de que el LLM lo
        # mencione (issue #18).
        aviso_responsabilidad=AVISO_RESPONSABILIDAD_PROFESIONAL,
    )


# ── /consultar — Agente delegador multi-dominio ──────────────────────────────

_cache_consultar = TTLCache(ttl_seconds=6 * 3600, max_size=1000)


@app.post("/consultar", response_model=ConsultarResponse, tags=["Normativa"])
@app.post("/v1/consultar", response_model=ConsultarResponse, tags=["Normativa"])
@limiter.limit("10/minute")
def consultar_delegado(request: Request, req: ConsultarRequest):
    """
    Punto de entrada único para preguntas de cualquier dominio de ingeniería.

    Detecta si la pregunta pertenece al corpus de un motor específico
    (por ahora: AquAI — acueducto/alcantarillado RAS 2000) y busca ahí;
    si no, cae al RAG normativo general (NSR-10/NTC/seguridad industrial),
    el mismo que usa /ask. GeoPot, motor-vías y motor-gerencia se suman a
    este delegador a medida que se ingesta su corpus de chunks reales.

    Ejemplo:
        {"pregunta": "¿Qué coeficiente C de Hazen-Williams uso para tubería PVC?"}
    """
    user = get_current_user(request)

    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo RAG no disponible. Verificar SUPABASE_URL/SUPABASE_SERVICE_KEY y GROQ_API_KEY."
        )

    clave_cache = f"{req.pregunta.strip().lower()}|{req.top_k}"
    result = _cache_consultar.get(clave_cache)
    cache_hit = result is not None

    if cache_hit:
        log.info("Consulta /consultar (cache hit)", extra={"user_id": user.id, "endpoint": "/consultar"})
        latencia = 0
    else:
        log.info("Consulta /consultar", extra={"user_id": user.id, "endpoint": "/consultar"})
        t0 = time.perf_counter()
        try:
            result = ask_delegado(question=req.pregunta, top_k=req.top_k)
        except RespuestaIAIndisponibleError as e:
            log.error(f"IA no disponible (Groq + respaldo OpenAI): {e}", extra={"user_id": user.id, "endpoint": "/consultar"})
            raise HTTPException(status_code=503, detail="Servicio de IA saturado temporalmente. Intenta de nuevo en unos minutos.")
        except Exception as e:
            log.error(f"Error en agente delegador: {e}", exc_info=True, extra={"user_id": user.id, "endpoint": "/consultar"})
            raise HTTPException(status_code=500, detail=f"Error en agente delegador: {str(e)}")

        latencia = int((time.perf_counter() - t0) * 1000)
        _cache_consultar.set(clave_cache, result)

    fuentes = [
        FuenteChunk(
            norma=f.get("norma", ""),
            seccion=f.get("seccion", ""),
            contenido_preview=f.get("contenido", "")[:200],
            score=round(float(f.get("score", 0.0)), 4),
        )
        for f in result.get("fuentes", [])
    ]

    registrar_consulta(
        user.id, req.pregunta, result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        chunks_usados=result.get("chunks_usados", 0), latencia_ms=latencia,
    )

    return ConsultarResponse(
        dominio=result.get("dominio", ""),
        dominio_label=result.get("dominio_label", ""),
        respuesta=result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        fuentes=fuentes,
        chunks_usados=result.get("chunks_usados", 0),
        latencia_ms=latencia,
        # Determinístico por dominio (issue #18) -- None para apu_precios/
        # gerencia, el aviso fijo para normativa_general/geopot/aquai/vias.
        aviso_responsabilidad=aviso_responsabilidad_para_dominio(result.get("dominio", "")),
    )


# ── /detect — YOLO Detección Estructural ─────────────────────────────────────

@app.post("/detect", response_model=DetectResponse, tags=["Detección"])
@app.post("/v1/detect", response_model=DetectResponse, tags=["Detección"])
@limiter.limit("10/minute")
async def detect_structural(
    request: Request,
    image: UploadFile = File(..., description="Foto JPG/PNG del elemento estructural"),
):
    """
    Detecta elementos estructurales en obra a partir de una foto: acero de
    refuerzo, viga, columna, muro, formaleta, tubería, trabajador (7 clases,
    ver CLASES_MODELO). Cuando aplica, sugiere el APU de costo correspondiente
    (`apu_sugerido_id`) y/o un recordatorio de seguridad con referencia
    normativa (`alerta_seguridad`, `norma_ref_seguridad`) — el recordatorio
    es una verificación sugerida, no una afirmación de cumplimiento (el
    modelo detecta presencia del elemento, no si cumple la norma).

    Usa YOLOv11 ONNX (packages/yolo/model.onnx) cuando el modelo está
    disponible; retorna stub determinístico si aún no se ha entrenado (ver
    packages/yolo/README.md).

    El campo `modo` indica si la respuesta es real (`onnx`) o stub (`stub`)
    — nunca se presenta un stub como si fuera una detección real.
    """
    user = get_current_user(request)
    log.info("Consulta /detect", extra={"user_id": user.id, "endpoint": "/detect"})

    # Validar tipo
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Se esperaba imagen (image/*), recibido: {content_type}"
        )

    img_bytes = await image.read()
    if len(img_bytes) > 20 * 1024 * 1024:  # 20 MB límite
        raise HTTPException(status_code=413, detail="Imagen demasiado grande (máx 20 MB)")

    t0 = time.perf_counter()

    # run_in_threadpool: la inferencia ONNX (y el stub, aunque es liviano) es
    # trabajo CPU-bound síncrono. Este endpoint es `async def` (necesario
    # para `await image.read()`), así que sin esto el event loop entero
    # queda bloqueado mientras procesa la imagen — no solo esta petición,
    # TODAS las peticiones concurrentes a la API (RAG, APU, health...).
    if _onnx_session is not None:
        try:
            detecciones = await run_in_threadpool(_detect_onnx, img_bytes, _onnx_session)
            import numpy as np, cv2
            arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            img_h, img_w = img.shape[:2]
            modo = "onnx"
        except Exception as e:
            log.error(f"Error inferencia ONNX: {e}", exc_info=True)
            detecciones, img_w, img_h = await run_in_threadpool(_detect_stub, img_bytes)
            modo = "stub_fallback"
    else:
        detecciones, img_w, img_h = await run_in_threadpool(_detect_stub, img_bytes)
        modo = "stub"

    latencia = int((time.perf_counter() - t0) * 1000)

    return DetectResponse(
        elementos_detectados=detecciones,
        imagen_ancho=img_w,
        imagen_alto=img_h,
        modelo_version="yolo11n-construdata-v1" if modo == "onnx" else "stub-v1",
        latencia_ms=latencia,
        modo=modo,
    )


# ── /deform — Motor Deformación (clasificación → análisis estructural) ────────

@app.post("/deform", response_model=DeformResponse, tags=["Deformación"])
@app.post("/v1/deform", response_model=DeformResponse, tags=["Deformación"])
@limiter.limit("20/minute")
def deform_analyze(request: Request, req: DeformRequest):
    """
    Cierra el pipeline clasificación→deformación: toma la `clase` que
    devolvió /detect (columna, viga, placa_aligerada, muro_bloque_15,
    muro_bloque_10, muro_concreto) y las cargas indicadas, arma un elemento
    estructural con dimensiones típicas de catálogo y calcula deflexión,
    esfuerzo de flexión/cortante o carga crítica de pandeo (según el tipo),
    con simulación Monte Carlo (N=5000) para acotar el margen de error real
    en vez de reportar un único número "exacto".
    """
    user = get_current_user(request)
    log.info("Consulta /deform", extra={"user_id": user.id, "endpoint": "/deform"})

    if not DEFORM_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo motor-deformacion no disponible."
        )

    TipoCarga = motor_deformacion.TipoCarga
    CargaAplicada = motor_deformacion.CargaAplicada

    try:
        cargas = [
            CargaAplicada(
                tipo=TipoCarga.PUNTUAL if c.tipo == "puntual" else TipoCarga.DISTRIBUIDA_UNIFORME,
                magnitud=c.magnitud, posicion=c.posicion, cov_carga=c.cov_carga, descripcion=c.descripcion,
            )
            for c in req.cargas
        ]
        resultado = motor_deformacion.MotorDeformacion().analizar_desde_deteccion(
            req.clase, cargas, longitud=req.longitud, run_montecarlo=req.run_montecarlo,
        )
    except Exception as e:
        log.error(f"Error en análisis de deformación ({req.clase}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La clase '{req.clase}' no corresponde a un elemento analizable por deformación. "
                   f"Válidas: columna, viga, placa_aligerada, muro_bloque_15, muro_bloque_10, muro_concreto"
        )

    return DeformResponse(
        elemento_id=resultado.elemento_id,
        tipo_analisis=resultado.tipo_analisis,
        deflexion_max_mm=round(resultado.deflexion_max * 1000, 3),
        deflexion_admisible_mm=round(resultado.deflexion_admisible * 1000, 3),
        cumple_deflexion=resultado.cumple_deflexion,
        momento_max_Nm=round(resultado.momento_max, 1),
        cortante_max_N=round(resultado.cortante_max, 1),
        esfuerzo_flexion_max_MPa=round(resultado.esfuerzo_flexion_max / 1e6, 3),
        esfuerzo_cortante_max_MPa=round(resultado.esfuerzo_cortante_max / 1e6, 3),
        factor_seguridad=round(resultado.factor_seguridad, 3) if resultado.factor_seguridad != float("inf") else -1,
        cumple_esfuerzo=resultado.cumple_esfuerzo,
        carga_critica_pandeo_kN=round(resultado.carga_critica_pandeo / 1e3, 2) if resultado.carga_critica_pandeo else None,
        esfuerzo_p05_MPa=round(resultado.esfuerzo_p05 / 1e6, 3),
        esfuerzo_p95_MPa=round(resultado.esfuerzo_p95 / 1e6, 3),
        indice_confiabilidad=round(resultado.indice_confiabilidad, 3) if resultado.indice_confiabilidad not in (float("inf"), float("-inf")) else -1,
        probabilidad_falla=resultado.probabilidad_falla,
        notas=resultado.notas,
    )


# ── /apu/list — Catálogo APU ──────────────────────────────────────────────────

# listar_actividades() recorre el catálogo completo (29 ítems) y recalcula
# cada uno (incluye Monte Carlo para el IC90) en cada llamada — el catálogo
# es un dict estático en Python, no cambia entre deploys, así que cachearlo
# 1h evita recomputar lo mismo en cada carga del panel de APU sin arriesgar
# servir datos desactualizados por mucho tiempo si algún día sí cambia.
_cache_apu_list = TTLCache(ttl_seconds=3600, max_size=1)


@app.get("/apu/list", response_model=list[APUItem], tags=["APU"])
@app.get("/v1/apu/list", response_model=list[APUItem], tags=["APU"])
def apu_list():
    """
    Lista todos los APUs disponibles en el catálogo Construdata 2026 Barranquilla.

    Incluye precio unitario, IC90 Monte Carlo e incertidumbre porcentual.
    """
    if not APU_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo motor-apu no disponible."
        )

    cacheado = _cache_apu_list.get("catalogo")
    if cacheado is not None:
        return cacheado

    try:
        items = listar_actividades()
    except Exception as e:
        log.error(f"Error listando APUs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    resultado = [APUItem(**item) for item in items]
    _cache_apu_list.set("catalogo", resultado)
    return resultado


# ── /apu/calculate — Calcular APU específico ─────────────────────────────────

@app.post("/apu/calculate", response_model=APUDesglose, tags=["APU"])
@app.post("/v1/apu/calculate", response_model=APUDesglose, tags=["APU"])
@limiter.limit("20/minute")
def apu_calculate(
    request: Request,
    actividad_id: str = Form(..., description="ID de la actividad APU, ej: C.COL.40X30"),
    cantidad: float = Form(1.0, ge=0.01, description="Cantidad de unidades a calcular"),
    proyecto_nombre: Optional[str] = Form(None, description="Nombre opcional del proyecto para agrupar en /proyectos"),
):
    """
    Calcula el APU completo con desglose Mat + MO + Equipo + AIU.

    Incluye simulación Monte Carlo (N=5000) para IC90 de incertidumbre.
    El campo `uuid_trazabilidad` permite rastrear este cálculo específico
    en el reporte PDF final.

    IDs disponibles: C.COL.40X30, C.COL.M3, C.VIG.30X40, C.ACE.G60,
    C.ZAP.120, C.PLA.ALIG, C.MUR.10, D.MUR.BLQ15, D.MUR.BLQ10,
    H.EXC.MAN, H.EXC.MAQ, SEG.CER.01, SEG.VAL.PMT
    """
    user = get_current_user(request)
    verificar_limite_apu_mes(user.id)
    verificar_limite_proyectos(user.id, proyecto_nombre)

    if not APU_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo motor-apu no disponible."
        )

    log.info("Consulta /apu/calculate", extra={"user_id": user.id, "endpoint": "/apu/calculate", "actividad_id": actividad_id})
    result = get_apu(actividad_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"APU '{actividad_id}' no encontrado. Use GET /apu/list para ver disponibles."
        )

    try:
        import datetime
        desglose = APUDesglose(
            actividad_id=actividad_id,
            descripcion=result.descripcion,
            unidad=result.unidad.value,
            capitulo=result.capitulo,
            costo_materiales=round(result.costo_materiales * cantidad, 2),
            costo_mano_obra=round(result.costo_mano_obra * cantidad, 2),
            costo_equipo=round(result.costo_equipo * cantidad, 2),
            costo_directo=round(result.costo_directo * cantidad, 2),
            aiu=round(result.aiu_total * cantidad, 2),
            precio_unitario=round(result.precio_unitario, 2),
            pu_p05=round(result.pu_p05, 2),
            pu_p95=round(result.pu_p95, 2),
            pu_std=round(result.pu_std, 2),
            norma_ref=result.norma_ref,
            uuid_trazabilidad=result.uuid_trazabilidad,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        log.error(f"Error calculando APU {actividad_id}: {e}", exc_info=True, extra={"user_id": user.id, "endpoint": "/apu/calculate"})
        raise HTTPException(status_code=500, detail=str(e))

    registrar_apu_calculo(user.id, actividad_id, cantidad, desglose, proyecto_nombre)
    return desglose


# ── /apu/calculate-dinamico — Cantidades desde geometría real (no catálogo) ──

@app.post("/apu/calculate-dinamico", response_model=APUDesglose, tags=["APU"])
@app.post("/v1/apu/calculate-dinamico", response_model=APUDesglose, tags=["APU"])
@limiter.limit("20/minute")
def apu_calculate_dinamico(request: Request, body: APUCantidadesRequest):
    """
    Calcula el APU de una columna o viga de concreto reforzado a partir de
    su geometría real (base, altura, longitud, refuerzo) en vez de un
    tamaño fijo de catálogo — las cantidades de concreto, acero y
    formaleta se calculan con fórmulas geométricas para ESTA sección
    específica.

    No diseña el refuerzo: el número de barras y el espaciamiento de
    estribos ya deben venir definidos (de un diseño estructural propio
    o de /deform). Si se omiten, el cálculo solo incluye concreto y
    formaleta.
    """
    user = get_current_user(request)
    verificar_limite_apu_mes(user.id)
    verificar_limite_proyectos(user.id, body.proyecto_nombre)

    if not APU_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo motor-apu no disponible."
        )

    log.info("Consulta /apu/calculate-dinamico", extra={"user_id": user.id, "endpoint": "/apu/calculate-dinamico"})

    try:
        tipo = TipoElementoConcreto(body.tipo)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"tipo debe ser 'columna' o 'viga', recibido: '{body.tipo}'"
        )

    refuerzo = None
    if body.refuerzo_longitudinal is not None:
        refuerzo = RefuerzoLongitudinal(
            numero_barras=body.refuerzo_longitudinal.numero_barras,
            diametro_pulg=body.refuerzo_longitudinal.diametro_pulg,
        )
    estribos = None
    if body.estribos is not None:
        estribos = Estribos(
            diametro_pulg=body.estribos.diametro_pulg,
            espaciamiento_m=body.estribos.espaciamiento_m,
            gancho_desarrollo_m=body.estribos.gancho_desarrollo_m,
        )

    try:
        geo = GeometriaElementoConcreto(
            tipo=tipo,
            base_m=body.base_m,
            altura_m=body.altura_m,
            longitud_m=body.longitud_m,
            recubrimiento_m=body.recubrimiento_m,
            refuerzo_longitudinal=refuerzo,
            estribos=estribos,
            incluye_cara_superior_formaleta=body.incluye_cara_superior_formaleta,
        )
        result = calcular_apu_dinamico(geo, calidad_concreto=body.calidad_concreto)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        log.error(
            f"Error calculando APU dinámico: {e}", exc_info=True,
            extra={"user_id": user.id, "endpoint": "/apu/calculate-dinamico"}
        )
        raise HTTPException(status_code=500, detail=str(e))

    import datetime
    desglose = APUDesglose(
        actividad_id=result.actividad_id,
        descripcion=result.descripcion,
        unidad=result.unidad.value,
        capitulo=result.capitulo,
        costo_materiales=result.costo_materiales,
        costo_mano_obra=result.costo_mano_obra,
        costo_equipo=result.costo_equipo,
        costo_directo=result.costo_directo,
        aiu=result.costo_aiu,
        precio_unitario=result.precio_unitario,
        pu_p05=result.pu_p05,
        pu_p95=result.pu_p95,
        pu_std=result.pu_std,
        norma_ref=result.norma_ref,
        uuid_trazabilidad=result.uuid_trazabilidad,
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
    )
    registrar_apu_calculo(user.id, result.actividad_id, 1.0, desglose, body.proyecto_nombre)
    return desglose


# ── /apu/plantilla y /apu/calculate-batch — APU por lote (Excel) ─────────────
# Reusan get_apu()/calcular_apu_dinamico() exactamente igual que los
# endpoints de arriba — no se tocó /apu/calculate ni /apu/calculate-dinamico,
# esto solo agrega una capa de Excel encima (ver apu_excel.py).

def _calcular_fila_apu(fila: dict) -> tuple[dict, Optional["APUDesglose"]]:
    """Calcula una fila de la plantilla. Nunca lanza — captura cualquier
    error y lo devuelve como resultado 'ERROR' para no tumbar el lote
    completo por una fila mal llenada."""
    import datetime as _dt

    resultado: dict = {k: None for k in apu_excel.COLUMNAS_SALIDA}
    try:
        if fila["modo"] == "catalogo":
            actividad_id = fila["actividad_id"]
            cantidad = fila["cantidad"]
            result = get_apu(actividad_id)
            if result is None:
                raise ValueError(f"actividad_id '{actividad_id}' no existe en el catálogo (ver hoja Catalogo_APU)")
            desglose = APUDesglose(
                actividad_id=actividad_id,
                descripcion=result.descripcion,
                unidad=result.unidad.value,
                capitulo=result.capitulo,
                costo_materiales=round(result.costo_materiales * cantidad, 2),
                costo_mano_obra=round(result.costo_mano_obra * cantidad, 2),
                costo_equipo=round(result.costo_equipo * cantidad, 2),
                costo_directo=round(result.costo_directo * cantidad, 2),
                aiu=round(result.aiu_total * cantidad, 2),
                precio_unitario=round(result.precio_unitario, 2),
                pu_p05=round(result.pu_p05, 2),
                pu_p95=round(result.pu_p95, 2),
                pu_std=round(result.pu_std, 2),
                norma_ref=result.norma_ref,
                uuid_trazabilidad=result.uuid_trazabilidad,
                timestamp=_dt.datetime.utcnow().isoformat() + "Z",
            )
            costo_total_fila = round(desglose.precio_unitario * cantidad, 2)
        else:
            tipo = TipoElementoConcreto(fila["tipo"])
            refuerzo = (
                RefuerzoLongitudinal(numero_barras=fila["refuerzo"]["numero_barras"], diametro_pulg=fila["refuerzo"]["diametro_pulg"])
                if fila.get("refuerzo") else None
            )
            estribos = (
                Estribos(
                    diametro_pulg=fila["estribos"]["diametro_pulg"],
                    espaciamiento_m=fila["estribos"]["espaciamiento_m"],
                    gancho_desarrollo_m=fila["estribos"]["gancho_desarrollo_m"],
                )
                if fila.get("estribos") else None
            )
            geo = GeometriaElementoConcreto(
                tipo=tipo,
                base_m=fila["base_m"],
                altura_m=fila["altura_m"],
                longitud_m=fila["longitud_m"],
                recubrimiento_m=fila["recubrimiento_m"],
                refuerzo_longitudinal=refuerzo,
                estribos=estribos,
                incluye_cara_superior_formaleta=fila["incluye_cara_superior_formaleta"],
            )
            result = calcular_apu_dinamico(geo, calidad_concreto=fila["calidad_concreto"])
            desglose = APUDesglose(
                actividad_id=result.actividad_id,
                descripcion=result.descripcion,
                unidad=result.unidad.value,
                capitulo=result.capitulo,
                costo_materiales=result.costo_materiales,
                costo_mano_obra=result.costo_mano_obra,
                costo_equipo=result.costo_equipo,
                costo_directo=result.costo_directo,
                aiu=result.costo_aiu,
                precio_unitario=result.precio_unitario,
                pu_p05=result.pu_p05,
                pu_p95=result.pu_p95,
                pu_std=result.pu_std,
                norma_ref=result.norma_ref,
                uuid_trazabilidad=result.uuid_trazabilidad,
                timestamp=_dt.datetime.utcnow().isoformat() + "Z",
            )
            costo_total_fila = round(desglose.precio_unitario * fila["cantidad"], 2)

        resultado.update({
            "estado": "OK",
            "descripcion": desglose.descripcion,
            "unidad": desglose.unidad,
            "capitulo": desglose.capitulo,
            "costo_materiales": desglose.costo_materiales,
            "costo_mano_obra": desglose.costo_mano_obra,
            "costo_equipo": desglose.costo_equipo,
            "costo_directo": desglose.costo_directo,
            "aiu": desglose.aiu,
            "precio_unitario": desglose.precio_unitario,
            "costo_total_fila": costo_total_fila,
            "pu_p05": desglose.pu_p05,
            "pu_p95": desglose.pu_p95,
            "pu_std": desglose.pu_std,
            "norma_ref": desglose.norma_ref,
            "uuid_trazabilidad": desglose.uuid_trazabilidad,
        })
        return resultado, desglose
    except (ValueError, KeyError, TypeError) as e:
        resultado["estado"] = "ERROR"
        resultado["error_detalle"] = str(e)
        return resultado, None
    except Exception as e:
        log.error(f"Error inesperado calculando fila de lote APU: {e}", exc_info=True)
        resultado["estado"] = "ERROR"
        resultado["error_detalle"] = f"Error interno: {e}"
        return resultado, None


@app.get("/apu/plantilla", tags=["APU"])
@app.get("/v1/apu/plantilla", tags=["APU"])
@limiter.limit("10/minute")
def apu_plantilla(request: Request):
    """Descarga la plantilla .xlsx para calcular APU en lote (catálogo y/o geometría dinámica)."""
    user = get_current_user(request)
    if not APU_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Módulo motor-apu no disponible.")
    log.info("Descarga /apu/plantilla", extra={"user_id": user.id, "endpoint": "/apu/plantilla"})
    catalogo = listar_actividades()
    xlsx_bytes = apu_excel.generar_plantilla(catalogo)
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_apu_construdata.xlsx"},
    )


@app.post("/apu/calculate-batch", tags=["APU"])
@app.post("/v1/apu/calculate-batch", tags=["APU"])
@limiter.limit("5/minute")
def apu_calculate_batch(
    request: Request,
    archivo: UploadFile = File(..., description="Plantilla .xlsx llenada (ver GET /apu/plantilla)"),
):
    """
    Calcula APU para todas las filas de una plantilla Excel subida (hasta
    200 filas, catálogo y/o geometría dinámica mezclados) y devuelve un
    .xlsx con el presupuesto completo: costos, AIU, IC90, trazabilidad
    normativa por fila, y una fila de total al final.

    Una fila con error (actividad_id inválido, geometría inconsistente)
    no tumba el lote — queda marcada en rojo con el detalle del error, el
    resto de filas se calculan igual. Si el plan gratis se queda sin cupo
    mensual a mitad del archivo, las filas restantes quedan marcadas
    "OMITIDO" (no se calculan ni se cobran) en vez de bloquear el archivo
    completo — el usuario recibe igual su Excel con lo que sí alcanzó a
    calcular y ve exactamente cuántas filas quedaron pendientes.
    """
    user = get_current_user(request)
    if not APU_AVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Módulo motor-apu no disponible.")

    filename = archivo.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=422, detail="Se esperaba un archivo .xlsx")

    file_bytes = archivo.file.read()
    if len(file_bytes) > 5 * 1024 * 1024:  # 5 MB — una plantilla de 200 filas pesa unos KB
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (máx 5 MB)")

    log.info("Consulta /apu/calculate-batch", extra={"user_id": user.id, "endpoint": "/apu/calculate-batch"})

    try:
        filas = apu_excel.leer_filas(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except zipfile.BadZipFile:
        # load_workbook() lanza esto (no ValueError) cuando el archivo no es
        # un .xlsx real -- ej. un usuario sube un .csv renombrado, un archivo
        # corrupto, o un .doc. Encontrado sin manejar el 2026-08-04 (crash
        # real reportado por Sentry): un archivo no-xlsx tumbaba el endpoint
        # con 500 en vez de un 422 claro.
        raise HTTPException(
            status_code=422,
            detail="El archivo no es un .xlsx válido — descargue la plantilla desde 'Descargar plantilla' y no cambie su formato al guardarlo.",
        )

    # None = plan pro (sin límite). int = cupo real restante del plan free
    # este mes — hallazgo de la auditoría de seguridad 2026-08-02: antes se
    # chequeaba el límite UNA vez antes del lote completo, así que subir 200
    # filas de un tirón daba 200 cálculos reales sin importar el plan.
    cupo_restante = _cupo_apu_mes_restante(user.id)

    # Cálculo síncrono CPU-bound (Monte Carlo N=5000 por fila) — este
    # endpoint no es async, FastAPI ya lo corre en threadpool automáticamente
    # (a diferencia de /detect, que es async def y necesita run_in_threadpool
    # explícito porque await bloquearía el loop entero). Medido en vivo:
    # ~1-3ms/fila, 200 filas es <1s de cómputo — el cuello de botella real
    # era escribir a Supabase fila por fila (ver registrar_apu_calculos_lote).
    resultados: list[dict] = []
    registros_para_insertar: list[dict] = []
    calculadas = 0
    for fila in filas:
        if cupo_restante is not None and calculadas >= cupo_restante:
            resultado = {k: None for k in apu_excel.COLUMNAS_SALIDA}
            resultado["estado"] = "OMITIDO"
            resultado["error_detalle"] = (
                f"Límite de {LIMITE_APU_MES_FREE} cálculos/mes del plan gratis alcanzado "
                f"({calculadas} calculados en este archivo). Activa Pro en /pricing para "
                "procesar el resto de este archivo sin límite."
            )
            resultados.append(resultado)
            continue

        resultado, desglose = _calcular_fila_apu(fila)
        resultados.append(resultado)
        if desglose is not None:
            cantidad_registrada = fila.get("cantidad", 1.0)
            registros_para_insertar.append(
                _construir_registro_apu(user.id, desglose.actividad_id, cantidad_registrada, desglose)
            )
            calculadas += 1

    registrar_apu_calculos_lote(registros_para_insertar)

    out_bytes = apu_excel.generar_resultado(filas, resultados)
    log.info(
        f"/apu/calculate-batch: {len(filas)} filas, "
        f"{sum(1 for r in resultados if r['estado'] == 'OK')} OK, "
        f"{sum(1 for r in resultados if r['estado'] == 'ERROR')} con error, "
        f"{sum(1 for r in resultados if r['estado'] == 'OMITIDO')} omitidas por límite del plan",
        extra={"user_id": user.id, "endpoint": "/apu/calculate-batch"},
    )
    return Response(
        content=out_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=presupuesto_apu_construdata.xlsx"},
    )


# ── /amenaza-sismica — dato en vivo del SGC por municipio ─────────────────────
# Endpoint público (sin auth, sin Groq) para el diagnóstico de vulnerabilidad
# y cualquier otro uso que necesite Aa/Av/zona de un municipio sin pasar por
# el chat completo. Ver packages/construdata/sgc_amenaza_sismica.py.

@app.get("/amenaza-sismica", tags=["GeoPot"])
@app.get("/v1/amenaza-sismica", tags=["GeoPot"])
@limiter.limit("30/minute")
def amenaza_sismica_municipio(request: Request, municipio: str):
    """Busca el municipio mencionado en `municipio` (texto libre, ej. 'Sincelejo'
    o 'Tuchín, Córdoba') contra el servicio geográfico del SGC y devuelve
    Aa/Av/Ae/Ad/zona de amenaza sísmica NSR-10, más (si hay coordenadas)
    el inventario de movimientos en masa cercano (SIMMA, radio 15 km) en
    `movimientos_masa`. 404 si no hay match de municipio o el servicio del
    SGC no respondió -- nunca 500, ninguno de los dos módulos lanza."""
    if not SGC_AVAILABLE:
        raise HTTPException(status_code=503, detail="Servicio de amenaza sísmica no disponible")
    registro = sgc_amenaza_sismica.detectar_municipio_en_texto(municipio)
    if not registro:
        raise HTTPException(status_code=404, detail=f"No se encontró un municipio de Colombia en '{municipio}'")

    resultado = dict(registro)
    lat, lon = registro.get("latitud"), registro.get("longitud")
    if lat is not None and lon is not None:
        resultado["movimientos_masa"] = sgc_movimientos_masa.consultar_movimientos_cercanos(lat, lon)
    return resultado


# ── /noticias — noticias recientes de Colombia (desastres/regulatorio) ────────

@app.get("/noticias", tags=["Noticias"])
@app.get("/v1/noticias", tags=["Noticias"])
@limiter.limit("30/minute")
def noticias(request: Request, categoria: Optional[str] = None, limite: int = 10):
    """Lee las noticias ya guardadas en noticias_relevantes (actualizadas
    cada 3h por el ciclo en background, ver _ciclo_noticias()) -- esto NO
    consulta Google News en vivo por request, solo lee lo último guardado.
    `categoria` opcional: 'desastre' o 'regulatoria'. Sin filtro, trae
    ambas mezcladas por fecha."""
    if not NOTICIAS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Servicio de noticias no disponible")
    if categoria not in (None, "desastre", "regulatoria"):
        raise HTTPException(status_code=422, detail="categoria debe ser 'desastre' o 'regulatoria'")
    return noticias_colombia.noticias_recientes(supabase_client, categoria=categoria, limite=min(limite, 50))


# ── /ask/route — Debug: ver qué normas detecta el router ──────────────────────

@app.get("/ask/route", tags=["Debug"])
@app.get("/v1/ask/route", tags=["Debug"])
def debug_route(q: str):
    """
    Muestra qué normas detectaría el router para una query dada.
    Útil para calibrar el KEYWORD_MAP.
    """
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG no disponible")
    normas = route_query(q)
    return {"query": q, "normas_detectadas": normas, "total": len(normas)}


# ════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "production") == "development",
        log_level="info",
    )
