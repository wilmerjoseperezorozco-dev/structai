"""
══════════════════════════════════════════════════════════════
ESTRUCTURAL ROUTER — Motor INFRACORTEX (StructAI)
Empresa física: Infracortex | App: StructAI
──────────────────────────────────────────────────────────────
Endpoints:
  GET  /estructural/salud              → Health check del motor
  POST /estructural/analizar-nudo      → IFC → PINN → NSR-10 (upload .ifc)
  POST /estructural/inspeccion-estribos → Imagen → YOLO → NSR-10 C.21.4.4

Patrón: carga motor-estructural vía importlib (mismo estilo motor-aquai).
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

# ── Carga motor-estructural como paquete real (evita error de import relativo) ─
import importlib.util as _ilu

_me_init = ROOT / "packages" / "motor-estructural" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location(
    "motor_estructural",
    _me_init,
    submodule_search_locations=[str(_me_init.parent)],
)
motor_estructural = _ilu.module_from_spec(_spec)
sys.modules["motor_estructural"] = motor_estructural
_spec.loader.exec_module(motor_estructural)

# ── Re-exportaciones para legibilidad ─────────────────────────────────────────
InfracortexEngine            = motor_estructural.InfracortexEngine
calcular_demanda_cortante    = motor_estructural.calcular_demanda_cortante_nudo
ZONA_SISMICA                 = motor_estructural.ZONA_SISMICA_ATLANTICO
CARGAS_DEFAULT               = motor_estructural.CARGAS_GRAVEDAD_DEFAULT
InfracortexVisionSensor      = motor_estructural.InfracortexVisionSensor
AnalisisNudoRequest          = motor_estructural.AnalisisNudoRequest
AnalisisNudoResponse         = motor_estructural.AnalisisNudoResponse
InspeccionEstribosResponse   = motor_estructural.InspeccionEstribosResponse
ResultadoEstriboItem         = motor_estructural.ResultadoEstriboItem

# Importar chequeo NSR-10 directamente
import importlib as _imp
_le = _imp.import_module("motor_estructural.load_engine")
chequeo_nsr10_nudo = _le.chequeo_nsr10_nudo

# auth
_api_path = Path(__file__).resolve().parents[1]
if str(_api_path) not in sys.path:
    sys.path.insert(0, str(_api_path))
from auth import get_current_user  # noqa: E402

router = APIRouter(prefix="/estructural", tags=["Estructural – Infracortex"])


# ─────────────────────────────────────────────────────────────────────────────
# GET /estructural/salud
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/salud")
def salud():
    return {
        "estado":          "ok",
        "motor":           "motor-estructural",
        "empresa":         "Infracortex",
        "app":             "StructAI",
        "norma_base":      "NSR-10 Títulos A, B y C",
        "zona_sismica":    "Departamento del Atlántico",
        "capas_activas":   ["IFC→Tensores", "SciPy 12GDL", "PINN float64", "Cargas NSR-10", "YOLO Estribos"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /estructural/analizar-nudo
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/analizar-nudo",
    response_model=AnalisisNudoResponse,
    summary="Análisis completo BIM → PINN → NSR-10 de un nudo estructural",
)
async def analizar_nudo(
    ifc_file:     UploadFile = File(...,  description="Archivo .ifc del modelo BIM"),
    guid_viga:    str        = Form(...,  description="GlobalId IFC de la viga"),
    guid_columna: str        = Form(...,  description="GlobalId IFC de la columna"),
    fc:           float      = Form(28.0, description="f'c [MPa]"),
    fy:           float      = Form(420.0,description="fy acero [MPa]"),
    b:            float      = Form(300.0,description="Ancho sección [mm]"),
    h:            float      = Form(300.0,description="Altura sección [mm]"),
    d:            float      = Form(265.0,description="Peralte efectivo [mm]"),
    Av:           float      = Form(56.5, description="Área estribos [mm²]"),
    s:            float      = Form(75.0, description="Separación estribos [mm]"),
    num_pisos:    int        = Form(3,    description="Pisos que convergen al nudo"),
):
    """
    Pipeline completo:
    1. Lee el IFC → extrae topología del nudo (Capa 1)
    2. Ensambla matriz 12×12 con SciPy (Capa 2)
    3. Calcula demanda sísmica NSR-10 Atlántico (Capa 4)
    4. Evalúa capacidad del nudo por cortante (NSR-10 C.21.7.4.1)

    Retorna el veredicto estructural (PASA / FALLA) con todos los valores.
    """
    # Guardar IFC en archivo temporal
    contenido = await ifc_file.read()
    with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
        tmp.write(contenido)
        ruta_ifc = tmp.name

    try:
        motor = InfracortexEngine(ruta_ifc)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error abriendo IFC: {e}")

    try:
        rotacion_viga, rotacion_columna, posicion_mm = motor.extraer_topologia_nudo(guid_viga, guid_columna)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"GUIDs no encontrados en el IFC: {e}")

    T12_viga = motor.ensamblar_rigidez_local(rotacion_viga)
    T12_columna = motor.ensamblar_rigidez_local(rotacion_columna)

    # Cargas y demanda sísmica
    cargas = {**CARGAS_DEFAULT, "numero_pisos": num_pisos}
    resultado = calcular_demanda_cortante(cargas, ZONA_SISMICA, altura_piso_mm=float(posicion_mm[2]))

    # Chequeo NSR-10
    props = {"fc": fc, "fy": fy, "b": b, "h": h, "d": d, "Av": Av, "s": s}
    chequeo = chequeo_nsr10_nudo(props, resultado["Vu_diseno_N"])

    esp = resultado["espectro"]
    veredicto = "PASA" if chequeo["cumple"] else "FALLA"

    return AnalisisNudoResponse(
        posicion_nudo_mm=[float(x) for x in posicion_mm],
        matriz_T12_shape=list(T12_viga.shape),
        matriz_T12_columna_shape=list(T12_columna.shape),
        periodo_T_seg=round(resultado["T_seg"], 4),
        Sa_g=round(resultado["Sa"], 4),
        espectro={
            "SDS": round(esp["SDS"], 4),
            "SD1": round(esp["SD1"], 4),
            "T0":  round(esp["T0"],  4),
            "Ts":  round(esp["Ts"],  4),
        },
        Vs_basal_kN=round(resultado["Vs_basal_N"] / 1000, 2),
        Vu_sismo_kN=round(resultado["Vu_sismo_N"] / 1000, 2),
        Vu_gravedad_kN=round(resultado["Vu_gravedad_N"] / 1000, 2),
        chequeo_nsr10={**chequeo, "combinacion_governa": resultado["combinacion_governa"]},
        veredicto=veredicto,
        norma_referencia="NSR-10 Títulos A (A.2.6, A.4.1, A.4.3) y C (C.11.3, C.11.4, C.21.7)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /estructural/inspeccion-estribos
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/inspeccion-estribos",
    response_model=InspeccionEstribosResponse,
    summary="Inspección visual de estribos: imagen → separación real → NSR-10 C.21.4.4",
)
async def inspeccion_estribos(
    imagen:             UploadFile = File(...,   description="Foto JPG/PNG de la armadura"),
    posiciones_y_csv:   str        = Form(...,   description="Posiciones Y de estribos en px, separadas por coma: '60,130,200'"),
    s_max_diseno_mm:    float      = Form(75.0,  description="Separación máxima de diseño [mm] (del modelo IFC)"),
    escala_mm_por_px:   float      = Form(1.0,   description="Calibración: mm por pixel de la imagen"),
):
    """
    Valida que la separación real de estribos en obra cumpla con la
    separación de diseño del modelo BIM (NSR-10 C.21.4.4 zona de confinamiento).

    `posiciones_y_csv`: coordenadas verticales (px) de cada estribo detectado
    por YOLO (o anotadas manualmente). Ejemplo: "60,130,200,280".
    """
    # Leer imagen
    img_bytes = await imagen.read()
    arr = np.frombuffer(img_bytes, np.uint8)
    img = None
    try:
        import cv2 as _cv2
        img = _cv2.imdecode(arr, _cv2.IMREAD_COLOR)
    except Exception:
        pass

    if img is None:
        img = np.zeros((400, 600, 3), dtype=np.uint8)

    # Parsear posiciones
    try:
        posiciones = [float(v.strip()) for v in posiciones_y_csv.split(",") if v.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="posiciones_y_csv debe ser números separados por coma")

    if len(posiciones) < 2:
        raise HTTPException(status_code=422, detail="Se necesitan al menos 2 posiciones de estribos para calcular separación")

    sensor = InfracortexVisionSensor(
        s_max_diseno_mm=s_max_diseno_mm,
        escala_mm_por_px=escala_mm_por_px,
    )
    detecciones, separaciones = sensor.analizar(img, posiciones)

    fallos   = sum(1 for s in separaciones if not s.cumple_nsr10)
    veredicto = "CUMPLE" if fallos == 0 else "INCUMPLE"
    accion    = (
        f"Reposicionar {fallos} estribo(s) para que la separación sea ≤{s_max_diseno_mm:.0f} mm"
        if fallos > 0 else None
    )

    return InspeccionEstribosResponse(
        estribos_detectados=len(detecciones),
        s_max_diseno_mm=s_max_diseno_mm,
        resultados=[
            ResultadoEstriboItem(
                par=s.par,
                separacion_mm=s.separacion_mm,
                cumple_nsr10=s.cumple_nsr10,
                s_max_mm=s.s_max_mm,
            )
            for s in separaciones
        ],
        fallos=fallos,
        veredicto=veredicto,
        accion_requerida=accion,
        norma_referencia="NSR-10 Título C · Artículo C.21.4.4",
    )
