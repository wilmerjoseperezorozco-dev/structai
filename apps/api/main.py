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
  packages/yolo/detector.py               → /detect  (stub ONNX si no hay modelo)
"""

from __future__ import annotations

import io
import os
import sys
import logging
import time
from pathlib import Path
from typing import Optional

# ── Path setup: permite imports de packages/ desde apps/api ───────────────────
ROOT = Path(__file__).resolve().parents[2]          # monorepo/
sys.path.insert(0, str(ROOT / "packages" / "construdata"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("construdata.api")

# ── Importaciones lazy para no fallar si falta algún paquete ──────────────────
# `except Exception` (no solo ImportError): rag_multi_norma.py lee credenciales
# con os.environ["..."] a nivel de módulo, que lanza KeyError si falta alguna
# env var — un KeyError sin capturar tumbaría todo el proceso FastAPI, no solo
# el RAG. Con Exception el resto de la API sigue viva y /ask queda en 503.
try:
    from rag_multi_norma import ask as rag_ask, route_query, ask_delegado
    RAG_AVAILABLE = True
    log.info("✓ rag_multi_norma cargado")
except Exception as e:
    RAG_AVAILABLE = False
    log.warning(f"✗ rag_multi_norma no disponible: {e}")

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
    APU_AVAILABLE = True
    log.info(f"✓ motor-apu cargado — {len(CATALOGO_APU)} APUs en catálogo")
except Exception as e:
    APU_AVAILABLE = False
    log.warning(f"✗ motor-apu no disponible: {e}")

try:
    import numpy as np
    import cv2
    import onnxruntime as ort
    YOLO_DEPS = True
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # en producción: dominio Vercel específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if AQUAI_AVAILABLE:
    app.include_router(aquai_router)
if GEOPOT_AVAILABLE:
    app.include_router(geopot_router)
if VIAS_AVAILABLE:
    app.include_router(vias_router)
if GERENCIA_AVAILABLE:
    app.include_router(gerencia_router)


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

class DeteccionElemento(BaseModel):
    clase: str
    confianza: float
    bbox: list[float]           # [x1, y1, x2, y2] normalizadas
    apu_sugerido_id: Optional[str] = None
    apu_descripcion: Optional[str] = None

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

# Mapa clase → APU sugerido (ajustar cuando el modelo YOLOv8 esté entrenado)
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
    """Inferencia real con YOLOv8 ONNX — output shape [1, num_classes+4, anchors]"""
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

    detecciones: list[DeteccionElemento] = []
    predictions = outputs[0].T                          # [8400, 4+nc]
    conf_threshold = 0.4

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

        clase = STUB_CLASES[class_id] if class_id < len(STUB_CLASES) else f"clase_{class_id}"
        apu_id, apu_desc = CLASE_APU_MAP.get(clase, (None, None))

        detecciones.append(DeteccionElemento(
            clase=clase,
            confianza=round(conf, 3),
            bbox=[round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)],
            apu_sugerido_id=apu_id,
            apu_descripcion=apu_desc,
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
    clases_muestra = ["columna", "viga", "muro_bloque_15"]

    for i in range(n):
        clase = clases_muestra[i % len(clases_muestra)]
        conf = round(rng.uniform(0.62, 0.94), 3)
        x1 = round(rng.uniform(0.05, 0.4), 4)
        y1 = round(rng.uniform(0.05, 0.4), 4)
        x2 = round(min(x1 + rng.uniform(0.1, 0.35), 0.95), 4)
        y2 = round(min(y1 + rng.uniform(0.1, 0.35), 0.95), 4)
        apu_id, apu_desc = CLASE_APU_MAP.get(clase, (None, None))
        detecciones.append(DeteccionElemento(
            clase=clase, confianza=conf,
            bbox=[x1, y1, x2, y2],
            apu_sugerido_id=apu_id,
            apu_descripcion=apu_desc,
        ))

    return sorted(detecciones, key=lambda d: d.confianza, reverse=True), img_w, img_h


# ════════════════════════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    global _onnx_session
    _onnx_session = _load_onnx_model()
    log.info("Construdata API lista ✓")


# ════════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Sistema"])
def health():
    """Health check con estado de cada módulo."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "modulos": {
            "rag_multi_norma":   RAG_AVAILABLE,
            "motor_apu":         APU_AVAILABLE,
            "motor_deformacion": DEFORM_AVAILABLE,
            "motor_aquai":       AQUAI_AVAILABLE,
            "motor_geopot":      GEOPOT_AVAILABLE,
            "motor_vias":        VIAS_AVAILABLE,
            "motor_gerencia":    GERENCIA_AVAILABLE,
            "yolo_onnx":         _onnx_session is not None,
            "yolo_deps":         YOLO_DEPS,
        },
        "apu_count": len(CATALOGO_APU) if APU_AVAILABLE else 0,
    }


# ── /ask — RAG Multi-Norma ───────────────────────────────────────────────────

@app.post("/ask", response_model=AskResponse, tags=["Normativa"])
def ask_norma(req: AskRequest):
    """
    Consulta RAG multi-norma.

    Detecta automáticamente qué NTC/NSR-10/Res. aplica a la pregunta,
    busca los chunks relevantes en Supabase (pgvector + BM25 híbrido, embeddings
    locales) y sintetiza la respuesta con Groq (llama-3.3-70b-versatile) citando
    las fuentes — respuestas en 1-3 segundos.

    Ejemplo:
        {"pregunta": "¿Qué resistencia mínima necesito para columnas sísmicas?"}
    """
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo RAG no disponible. Verificar SUPABASE_URL/SUPABASE_SERVICE_KEY y GROQ_API_KEY."
        )

    t0 = time.perf_counter()
    try:
        result = rag_ask(
            question=req.pregunta,
            norma_hint=req.norma_hint,
            top_k=req.top_k,
        )
    except Exception as e:
        log.error(f"Error RAG: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en RAG: {str(e)}")

    latencia = int((time.perf_counter() - t0) * 1000)

    fuentes = [
        FuenteChunk(
            norma=f.get("norma", ""),
            seccion=f.get("seccion", ""),
            contenido_preview=f.get("contenido", "")[:200],
            score=round(float(f.get("score", 0.0)), 4),
        )
        for f in result.get("fuentes", [])
    ]

    return AskResponse(
        respuesta=result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        normas_detectadas_router=result.get("normas_detectadas_router", []),
        fuentes=fuentes,
        chunks_usados=result.get("chunks_usados", 0),
        latencia_ms=latencia,
    )


# ── /consultar — Agente delegador multi-dominio ──────────────────────────────

@app.post("/consultar", response_model=ConsultarResponse, tags=["Normativa"])
def consultar_delegado(req: ConsultarRequest):
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
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo RAG no disponible. Verificar SUPABASE_URL/SUPABASE_SERVICE_KEY y GROQ_API_KEY."
        )

    t0 = time.perf_counter()
    try:
        result = ask_delegado(question=req.pregunta, top_k=req.top_k)
    except Exception as e:
        log.error(f"Error en agente delegador: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en agente delegador: {str(e)}")

    latencia = int((time.perf_counter() - t0) * 1000)

    fuentes = [
        FuenteChunk(
            norma=f.get("norma", ""),
            seccion=f.get("seccion", ""),
            contenido_preview=f.get("contenido", "")[:200],
            score=round(float(f.get("score", 0.0)), 4),
        )
        for f in result.get("fuentes", [])
    ]

    return ConsultarResponse(
        dominio=result.get("dominio", ""),
        dominio_label=result.get("dominio_label", ""),
        respuesta=result.get("respuesta", ""),
        normas_citadas=result.get("normas_citadas", []),
        fuentes=fuentes,
        chunks_usados=result.get("chunks_usados", 0),
        latencia_ms=latencia,
    )


# ── /detect — YOLO Detección Estructural ─────────────────────────────────────

@app.post("/detect", response_model=DetectResponse, tags=["Detección"])
async def detect_structural(
    image: UploadFile = File(..., description="Foto JPG/PNG del elemento estructural"),
):
    """
    Detecta elementos estructurales en la imagen.

    Usa YOLOv8 ONNX cuando el modelo está disponible; retorna stub
    deterministico durante desarrollo. Cada detección incluye la
    clase (columna, viga, muro...) y el APU sugerido correspondiente.

    El campo `modo` indica si la respuesta es real (`onnx`) o stub (`stub`).
    """
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

    if _onnx_session is not None:
        try:
            detecciones = _detect_onnx(img_bytes, _onnx_session)
            import numpy as np, cv2
            arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            img_h, img_w = img.shape[:2]
            modo = "onnx"
        except Exception as e:
            log.error(f"Error inferencia ONNX: {e}", exc_info=True)
            detecciones, img_w, img_h = _detect_stub(img_bytes)
            modo = "stub_fallback"
    else:
        detecciones, img_w, img_h = _detect_stub(img_bytes)
        modo = "stub"

    latencia = int((time.perf_counter() - t0) * 1000)

    return DetectResponse(
        elementos_detectados=detecciones,
        imagen_ancho=img_w,
        imagen_alto=img_h,
        modelo_version="yolov8n-construdata-v1" if modo == "onnx" else "stub-v1",
        latencia_ms=latencia,
        modo=modo,
    )


# ── /deform — Motor Deformación (clasificación → análisis estructural) ────────

@app.post("/deform", response_model=DeformResponse, tags=["Deformación"])
def deform_analyze(req: DeformRequest):
    """
    Cierra el pipeline clasificación→deformación: toma la `clase` que
    devolvió /detect (columna, viga, placa_aligerada, muro_bloque_15,
    muro_bloque_10, muro_concreto) y las cargas indicadas, arma un elemento
    estructural con dimensiones típicas de catálogo y calcula deflexión,
    esfuerzo de flexión/cortante o carga crítica de pandeo (según el tipo),
    con simulación Monte Carlo (N=5000) para acotar el margen de error real
    en vez de reportar un único número "exacto".
    """
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

@app.get("/apu/list", response_model=list[APUItem], tags=["APU"])
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
    try:
        items = listar_actividades()
    except Exception as e:
        log.error(f"Error listando APUs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    return [APUItem(**item) for item in items]


# ── /apu/calculate — Calcular APU específico ─────────────────────────────────

@app.post("/apu/calculate", response_model=APUDesglose, tags=["APU"])
def apu_calculate(
    actividad_id: str = Form(..., description="ID de la actividad APU, ej: C.COL.40X30"),
    cantidad: float = Form(1.0, ge=0.01, description="Cantidad de unidades a calcular"),
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
    if not APU_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Módulo motor-apu no disponible."
        )

    result = get_apu(actividad_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"APU '{actividad_id}' no encontrado. Use GET /apu/list para ver disponibles."
        )

    try:
        import datetime
        return APUDesglose(
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
        log.error(f"Error calculando APU {actividad_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── /ask/route — Debug: ver qué normas detecta el router ──────────────────────

@app.get("/ask/route", tags=["Debug"])
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
