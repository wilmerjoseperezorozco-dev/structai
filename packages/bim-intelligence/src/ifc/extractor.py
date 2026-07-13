"""
Extractor IFC con Sistema Nervioso integrado.
Módulo de Gemini adaptado: usa el sensor WPM para capturar fallas exactas
y retorna JSON estructurado que el MCP puede consumir directamente.

Expande parser.py añadiendo manejo de errores por tipo de elemento.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

import ifcopenshell

# Sistema nervioso — sensor de fallas
from ..observabilidad.sensor import inicializar_sensor, veedor

sensor = inicializar_sensor(__name__)

# Tipos IFC y sus extractores
EXTRACTORES: dict[str, Callable] = {}


def extractor(ifc_type: str):
    """Decorador para registrar extractores por tipo IFC."""
    def decorator(fn: Callable) -> Callable:
        EXTRACTORES[ifc_type] = fn
        return fn
    return decorator


# ── Extractores por tipo ──────────────────────────────────────────────────────

@extractor("IfcBeam")
def extraer_vigas(ruta_ifc: str) -> str:
    """
    Extrae vigas del modelo IFC.
    Captura errores exactos con el sensor para diagnóstico posterior.
    """
    try:
        modelo = ifcopenshell.open(ruta_ifc)
        vigas = modelo.by_type("IfcBeam")

        if not vigas:
            raise ValueError(
                f"El modelo {Path(ruta_ifc).name} no contiene elementos tipo IfcBeam."
            )

        datos = []
        for v in vigas:
            datos.append({
                "global_id": str(v.GlobalId),
                "nombre": str(getattr(v, "Name", "")),
                "descripcion": str(getattr(v, "Description", "")),
            })

        veedor.consulta_bim("IfcBeam", len(datos))
        return json.dumps({"estado": "exito", "total": len(datos), "datos": datos}, ensure_ascii=False)

    except Exception as e:
        sensor.error(
            f"Fallo crítico al procesar IfcBeam en: {ruta_ifc}",
            exc_info=True,
        )
        return json.dumps({"estado": "error", "mensaje": "Falla registrada en veedor_fallas.jsonl"})


@extractor("IfcColumn")
def extraer_columnas(ruta_ifc: str) -> str:
    try:
        modelo = ifcopenshell.open(ruta_ifc)
        elementos = modelo.by_type("IfcColumn")

        if not elementos:
            raise ValueError(f"Sin IfcColumn en {Path(ruta_ifc).name}")

        datos = [{"global_id": str(e.GlobalId), "nombre": str(getattr(e, "Name", ""))}
                 for e in elementos]

        veedor.consulta_bim("IfcColumn", len(datos))
        return json.dumps({"estado": "exito", "total": len(datos), "datos": datos}, ensure_ascii=False)

    except Exception as e:
        sensor.error(f"Fallo crítico al procesar IfcColumn en: {ruta_ifc}", exc_info=True)
        return json.dumps({"estado": "error", "mensaje": "Falla registrada en veedor_fallas.jsonl"})


@extractor("IfcSlab")
def extraer_losas(ruta_ifc: str) -> str:
    try:
        modelo = ifcopenshell.open(ruta_ifc)
        elementos = modelo.by_type("IfcSlab")

        if not elementos:
            raise ValueError(f"Sin IfcSlab en {Path(ruta_ifc).name}")

        datos = [{"global_id": str(e.GlobalId), "nombre": str(getattr(e, "Name", ""))}
                 for e in elementos]

        veedor.consulta_bim("IfcSlab", len(datos))
        return json.dumps({"estado": "exito", "total": len(datos), "datos": datos}, ensure_ascii=False)

    except Exception as e:
        sensor.error(f"Fallo crítico al procesar IfcSlab en: {ruta_ifc}", exc_info=True)
        return json.dumps({"estado": "error", "mensaje": "Falla registrada en veedor_fallas.jsonl"})


# ── Extractor genérico ────────────────────────────────────────────────────────

def extraer_elemento(ruta_ifc: str, tipo_ifc: str) -> str:
    """
    Extractor genérico para cualquier tipo IFC.
    Usa extractores especializados si existen, sino extrae campos básicos.
    """
    if tipo_ifc in EXTRACTORES:
        return EXTRACTORES[tipo_ifc](ruta_ifc)

    try:
        modelo = ifcopenshell.open(ruta_ifc)
        elementos = modelo.by_type(tipo_ifc)

        if not elementos:
            raise ValueError(f"Sin {tipo_ifc} en {Path(ruta_ifc).name}")

        datos = [
            {
                "global_id": str(e.GlobalId),
                "nombre": str(getattr(e, "Name", "")),
                "descripcion": str(getattr(e, "Description", "")),
            }
            for e in elementos
        ]

        veedor.consulta_bim(tipo_ifc, len(datos))
        return json.dumps({"estado": "exito", "tipo": tipo_ifc, "total": len(datos), "datos": datos[:50]}, ensure_ascii=False)

    except Exception as e:
        sensor.error(f"Fallo crítico al procesar {tipo_ifc} en: {ruta_ifc}", exc_info=True)
        return json.dumps({"estado": "error", "tipo": tipo_ifc, "mensaje": "Falla registrada en veedor_fallas.jsonl"})


if __name__ == "__main__":
    if len(sys.argv) > 2:
        resultado = extraer_elemento(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        resultado = extraer_elemento(sys.argv[1], "IfcBeam")
    else:
        sensor.error("Ejecución fallida: No se proporcionó ruta de archivo.", exc_info=False)
        resultado = json.dumps({"estado": "error", "mensaje": "Uso: extractor.py <ruta.ifc> [TipoIfc]"})
    print(resultado)
