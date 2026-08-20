"""
══════════════════════════════════════════════════════════════
AQUAI ROUTER — Motor hidrosanitario RAS 2000
Complementario de StructAI, montado bajo el prefijo /aquai. Diseñado para
ser separable: toda la lógica vive en packages/motor-aquai (paquete propio,
sin imports cruzados a motor-apu/motor-deformacion), cargado aquí vía
importlib con el mismo patrón usado para esos otros dos motores — evita el
error "attempted relative import" que rompía el wiring original de
motor-apu, y no contamina sys.path con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
# NOTA: sin "from __future__ import annotations" a proposito (igual que
# main.py) -- con PEP 563 activo, @limiter.limit() de slowapi rompe la
# resolucion de forward-refs de FastAPI para tipos no builtin (UploadFile,
# los *Request de motor_*). Reproducido en vivo el 2026-08-02 al agregar
# rate limiting a este router: analizar_nudo() (UploadFile) fallaba con
# FastAPIError en el import; los endpoints con tipos custom (motor_X.Y)
# "funcionaban" solo por coincidencia de que Python 3.10+ ya resuelve
# list/dict/X|None nativamente sin necesitar el future import de todos modos.

import sys
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

# apps/api ya está en sys.path para cuando este módulo se importa (main.py lo
# agrega antes de hacer `from routers.aquai import router`).
from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

# packages/construdata ya está en sys.path (main.py lo agrega antes de
# cargar este router, igual que para rag_multi_norma). ideam_client expone
# los datos abiertos hidrometeorológicos del IDEAM (datos.gov.co, API
# pública sin key) — ver packages/construdata/ideam_client.py.
import ideam_client

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

import importlib.util as _ilu
_aquai_init = ROOT / "packages" / "motor-aquai" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_aquai", _aquai_init, submodule_search_locations=[str(_aquai_init.parent)])
motor_aquai = _ilu.module_from_spec(_spec)
sys.modules["motor_aquai"] = motor_aquai
_spec.loader.exec_module(motor_aquai)

router = APIRouter(prefix="/aquai", tags=["AquAI"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "AquAI", "norma_base": "RAS 2000 / Res. 0330-2017"}


@router.post("/poblacion", response_model=motor_aquai.PoblacionResponse, summary="Proyección de población de diseño")
@limiter.limit("30/minute")
def endpoint_poblacion(request: Request, req: motor_aquai.PoblacionRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.proyectar_poblacion(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/caudales", response_model=motor_aquai.CaudalesResponse, summary="Dotación y caudales de diseño (Qmd, Qmh, Qci)")
@limiter.limit("30/minute")
def endpoint_caudales(request: Request, req: motor_aquai.CaudalesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_caudales(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica", response_model=motor_aquai.HazenWilliamsResponse, summary="Hidráulica de tuberías — Hazen-Williams")
@limiter.limit("30/minute")
def endpoint_hidraulica(request: Request, req: motor_aquai.HazenWilliamsRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_hazen_williams(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidrologia", response_model=motor_aquai.HidrologiaResponse, summary="Hidrología — caudal de diseño (Método Racional)")
@limiter.limit("30/minute")
def endpoint_hidrologia(request: Request, req: motor_aquai.HidrologiaRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_hidrologia(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/hidrologia/estaciones-ideam",
    summary="Estaciones IDEAM cercanas al proyecto (dato real de referencia)",
)
@limiter.limit("30/minute")
def endpoint_estaciones_ideam(
    request: Request,
    municipio: str,
    departamento: str | None = None,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Consulta el catálogo nacional de estaciones del IDEAM (datos abiertos,
    datos.gov.co) para el municipio/departamento del proyecto. Es información
    de REFERENCIA para que el ingeniero verifique qué estaciones reales
    existen cerca y qué miden (pluviométrica, climatológica, limnigráfica) —
    NO reemplaza las curvas IDF regionales oficiales que usa /aquai/hidrologia
    para el caudal de diseño (esas son series estadísticas de eventos
    extremos ya validadas, no observaciones crudas puntuales)."""
    try:
        estaciones = ideam_client.buscar_estaciones(
            departamento=departamento, municipio=municipio, limit=15
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"IDEAM (datos.gov.co) no disponible: {e}")
    return {
        "municipio": municipio,
        "departamento": departamento,
        "total_estaciones": len(estaciones),
        "estaciones": estaciones,
        "nota": (
            "Fuente: Catálogo Nacional de Estaciones del IDEAM, datos abiertos "
            "(datos.gov.co). Uso de referencia para el ingeniero — no reemplaza "
            "las curvas IDF regionales oficiales usadas en el cálculo de "
            "caudal de diseño."
        ),
    }


@router.get(
    "/hidrologia/precipitacion-ideam",
    summary="Observaciones recientes de precipitación IDEAM (dato real, sin validar)",
)
@limiter.limit("30/minute")
def endpoint_precipitacion_ideam(
    request: Request,
    municipio: str,
    limit: int = 50,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Observaciones crudas de precipitación (mm) del IDEAM para el
    municipio dado — dato en tiempo casi real, SIN validar oficialmente por
    IDEAM (aclaración obligatoria de la propia fuente). Útil para dar
    contexto de campo, no para sustituir la intensidad de diseño I (mm/h)
    de la curva IDF regional que calcula /aquai/hidrologia."""
    limit = max(1, min(limit, 500))
    try:
        obs = ideam_client.precipitacion_por_municipio(municipio, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"IDEAM (datos.gov.co) no disponible: {e}")
    return {
        "municipio": municipio,
        "total_observaciones": len(obs),
        "observaciones": obs,
        "nota": (
            "Fuente: IDEAM, datos abiertos (datos.gov.co), NO validados "
            "oficialmente. Dato de referencia/contexto — el caudal de diseño "
            "de /aquai/hidrologia usa las curvas IDF regionales oficiales de "
            "RAS 2000, no esta observación cruda."
        ),
    }


@router.post("/hidraulica/manning", response_model=motor_aquai.ManningResponse, summary="Manning — alcantarillado a gravedad")
@limiter.limit("30/minute")
def endpoint_manning(request: Request, req: motor_aquai.ManningRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_manning(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica/ariete", response_model=motor_aquai.ArieteResponse, summary="Golpe de ariete (Joukowski)")
@limiter.limit("30/minute")
def endpoint_ariete(request: Request, req: motor_aquai.ArieteRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_ariete(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica/bombeo", response_model=motor_aquai.BombeoResponse, summary="Estación de bombeo — TDH, potencia y NPSH")
@limiter.limit("30/minute")
def endpoint_bombeo(request: Request, req: motor_aquai.BombeoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_bombeo(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/saneamiento/ptap", response_model=motor_aquai.PTAPResponse, summary="Dimensionar PTAP")
@limiter.limit("30/minute")
def endpoint_ptap(request: Request, req: motor_aquai.PTAPRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_ptap(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/saneamiento/ptar", response_model=motor_aquai.PTARResponse, summary="Dimensionar PTAR")
@limiter.limit("30/minute")
def endpoint_ptar(request: Request, req: motor_aquai.PTARRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_ptar(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/tarifas/calcular", response_model=motor_aquai.TarifaResponse, summary="Tarifas CRA por estrato")
@limiter.limit("30/minute")
def endpoint_tarifa(request: Request, req: motor_aquai.TarifaRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.calcular_tarifa(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/sui/reporte", response_model=motor_aquai.ReporteSUIResponse, summary="Estructura de reporte para el portal SUI")
@limiter.limit("30/minute")
def endpoint_reporte_sui(request: Request, req: motor_aquai.ReporteSUIRequest, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return motor_aquai.generar_reporte_sui(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/reporte/memoria", summary="Generar memoria de cálculo en PDF")
@limiter.limit("20/minute")
def endpoint_memoria_pdf(request: Request, payload: dict, user: AuthenticatedUser = Depends(get_current_user)):
    """
    Body: {"meta": {...datos del proyecto...}, "modulos": {...resultados calculados...}, "ingeniero": {...}}
    Ver packages/motor-aquai/src/pdf_memoria.py para el detalle de campos esperados.
    """
    try:
        meta = payload.get("meta", {})
        modulos = payload.get("modulos", {})
        ingeniero = payload.get("ingeniero", {})

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, prefix="aquai_memoria_") as tmp:
            ruta = tmp.name

        motor_aquai_pdf = sys.modules.get("motor_aquai.pdf_memoria")
        if motor_aquai_pdf is None:
            import importlib
            motor_aquai_pdf = importlib.import_module("motor_aquai.pdf_memoria")

        motor_aquai_pdf.generar_memoria_pdf(meta, modulos, ruta, ingeniero)

        nombre_archivo = (
            f"AquAI_Memoria_{meta.get('municipio', 'proyecto').replace(' ', '_')}"
            f"_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        return FileResponse(
            path=ruta, media_type="application/pdf", filename=nombre_archivo,
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(ex)}")
