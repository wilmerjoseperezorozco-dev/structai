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
from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

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
def endpoint_poblacion(req: motor_aquai.PoblacionRequest):
    try:
        return motor_aquai.proyectar_poblacion(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/caudales", response_model=motor_aquai.CaudalesResponse, summary="Dotación y caudales de diseño (Qmd, Qmh, Qci)")
def endpoint_caudales(req: motor_aquai.CaudalesRequest):
    try:
        return motor_aquai.calcular_caudales(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica", response_model=motor_aquai.HazenWilliamsResponse, summary="Hidráulica de tuberías — Hazen-Williams")
def endpoint_hidraulica(req: motor_aquai.HazenWilliamsRequest):
    try:
        return motor_aquai.calcular_hazen_williams(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidrologia", response_model=motor_aquai.HidrologiaResponse, summary="Hidrología — caudal de diseño (Método Racional)")
def endpoint_hidrologia(req: motor_aquai.HidrologiaRequest):
    try:
        return motor_aquai.calcular_hidrologia(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica/manning", response_model=motor_aquai.ManningResponse, summary="Manning — alcantarillado a gravedad")
def endpoint_manning(req: motor_aquai.ManningRequest):
    try:
        return motor_aquai.calcular_manning(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica/ariete", response_model=motor_aquai.ArieteResponse, summary="Golpe de ariete (Joukowski)")
def endpoint_ariete(req: motor_aquai.ArieteRequest):
    try:
        return motor_aquai.calcular_ariete(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/hidraulica/bombeo", response_model=motor_aquai.BombeoResponse, summary="Estación de bombeo — TDH, potencia y NPSH")
def endpoint_bombeo(req: motor_aquai.BombeoRequest):
    try:
        return motor_aquai.calcular_bombeo(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/saneamiento/ptap", response_model=motor_aquai.PTAPResponse, summary="Dimensionar PTAP")
def endpoint_ptap(req: motor_aquai.PTAPRequest):
    try:
        return motor_aquai.calcular_ptap(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/saneamiento/ptar", response_model=motor_aquai.PTARResponse, summary="Dimensionar PTAR")
def endpoint_ptar(req: motor_aquai.PTARRequest):
    try:
        return motor_aquai.calcular_ptar(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/tarifas/calcular", response_model=motor_aquai.TarifaResponse, summary="Tarifas CRA por estrato")
def endpoint_tarifa(req: motor_aquai.TarifaRequest):
    try:
        return motor_aquai.calcular_tarifa(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/sui/reporte", response_model=motor_aquai.ReporteSUIResponse, summary="Estructura de reporte para el portal SUI")
def endpoint_reporte_sui(req: motor_aquai.ReporteSUIRequest):
    try:
        return motor_aquai.generar_reporte_sui(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/reporte/memoria", summary="Generar memoria de cálculo en PDF")
def endpoint_memoria_pdf(payload: dict):
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


@router.post("/normativa/buscar", summary="Búsqueda semántica sobre normativa AquAI (requiere OPENAI_API_KEY + tabla normas_vigentes)")
async def endpoint_buscar_normas(pregunta: str, threshold: float = 0.70, limite: int = 5, tipo_norma: str | None = None):
    try:
        import importlib
        rag_normativo = sys.modules.get("motor_aquai.rag_normativo") or importlib.import_module("motor_aquai.rag_normativo")
        return await rag_normativo.buscar_normas_rag(pregunta, threshold, limite, tipo_norma)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
