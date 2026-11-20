"""
Metadatos de georreferenciación en DXF (issue #211).

El punto base real se guarda en tres lugares, de más a menos canónico:
  1. XRECORD `STRUCTAI_GEOREF` en el diccionario raíz de objetos: la fuente de verdad que lee StructAI.
  2. Variables de cabecera personalizadas ($CUSTOMPROPERTY): se ven en AutoCAD (DWGPROPS) y en BricsCAD.
  3. GEODATA (opcional): el objeto que usan AutoCAD/Civil 3D para ubicar el dibujo. Su definición de sistema
     de coordenadas es XML propio de Autodesk; aquí va el WKT de EPSG, y falta validarlo en Civil 3D antes de
     activarlo por defecto (criterio de hecho del issue).
Además $INSUNITS = 6 (metros) y $MEASUREMENT = 1 (métrico).
"""
from __future__ import annotations

import json

import ezdxf
from ezdxf.document import Drawing
from pyproj import CRS

from georef import EPSG_OFICIAL, PuntoBase

NOMBRE_XRECORD = "STRUCTAI_GEOREF"
PREFIJO_VAR = "STRUCTAI_"
INSUNITS_METROS = 6


def nuevo_documento(version: str = "R2018") -> Drawing:
    doc = ezdxf.new(version, setup=True)
    doc.units = INSUNITS_METROS
    doc.header["$INSUNITS"] = INSUNITS_METROS
    doc.header["$MEASUREMENT"] = 1
    return doc


def escribir_georef(doc: Drawing, pb: PuntoBase, *, geodata: bool = False) -> None:
    """Graba el punto base en el documento (XRECORD + variables de cabecera [+ GEODATA])."""
    doc.units = INSUNITS_METROS
    doc.header["$INSUNITS"] = INSUNITS_METROS
    doc.header["$MEASUREMENT"] = 1

    raiz = doc.rootdict
    if NOMBRE_XRECORD in raiz:
        raiz.remove(NOMBRE_XRECORD)
    xr = raiz.add_xrecord(NOMBRE_XRECORD)
    # 1 = texto JSON completo (para leer todo de una vez); 40 = reales en orden fijo (para lectores sin JSON).
    xr.extend([
        (1, json.dumps(pb.como_dict(), ensure_ascii=False, sort_keys=True)),
        (70, pb.epsg),
        (40, pb.e0), (40, pb.n0), (40, pb.h0), (40, pb.rotacion_rad), (40, pb.escala),
    ])

    variables = {
        "EPSG": str(pb.epsg), "E0": repr(pb.e0), "N0": repr(pb.n0), "H0": repr(pb.h0),
        "ROTACION_RAD": repr(pb.rotacion_rad), "ESCALA": repr(pb.escala), "FUENTE": pb.fuente,
        "FECHA": pb.fecha, "CONVERSOR": pb.version_conversor,
    }
    cv = doc.header.custom_vars
    for k, v in variables.items():
        etiqueta = PREFIJO_VAR + k
        if cv.has_tag(etiqueta):
            cv.replace(etiqueta, v)
        else:
            cv.append(etiqueta, v)

    if geodata:
        msp = doc.modelspace()
        gd = msp.get_geodata() or msp.new_geodata()
        gd.dxf.coordinate_type = 2                      # 2 = cuadrícula proyectada
        gd.dxf.design_point = (0.0, 0.0, 0.0)           # el origen local del dibujo…
        gd.dxf.reference_point = (pb.e0, pb.n0, pb.h0)  # …corresponde a este punto oficial
        gd.dxf.horizontal_unit_scale = pb.escala
        gd.dxf.horizontal_units = INSUNITS_METROS
        gd.dxf.vertical_unit_scale = 1.0
        gd.dxf.vertical_units = INSUNITS_METROS
        gd.dxf.up_direction = (0.0, 0.0, 1.0)
        c, s = pb.eje_x
        gd.dxf.north_direction = (-s, c)                # Norte de cuadrícula expresado en ejes locales
        gd.coordinate_system_definition = CRS.from_epsg(EPSG_OFICIAL).to_wkt()


def leer_georef(doc: Drawing) -> PuntoBase | None:
    """Recupera el punto base desde el XRECORD; si no está, desde las variables de cabecera. None si no hay."""
    xr = doc.rootdict.get(NOMBRE_XRECORD)
    if xr is not None:
        for codigo, valor in xr.tags:
            if codigo == 1:
                return PuntoBase.desde_dict(json.loads(valor))
    cv = doc.header.custom_vars
    if cv.has_tag(PREFIJO_VAR + "E0"):
        g = lambda k, d=None: cv.get(PREFIJO_VAR + k, d)  # noqa: E731
        return PuntoBase(e0=float(g("E0")), n0=float(g("N0")), h0=float(g("H0", "0")),
                         rotacion_rad=float(g("ROTACION_RAD", "0")), escala=float(g("ESCALA", "1")),
                         epsg=int(g("EPSG", str(EPSG_OFICIAL))), fuente=g("FUENTE", "desconocida"),
                         fecha=g("FECHA", ""), version_conversor=g("CONVERSOR", ""))
    return None


def agregar_polilinea(doc: Drawing, puntos_oficiales, pb: PuntoBase, capa: str, *, cerrada: bool = False):
    """Dibuja una polilínea 3D en coordenadas locales a partir de puntos oficiales (E, N[, H])."""
    filas = [tuple(p) + (0.0,) * (3 - len(p)) for p in puntos_oficiales]
    locales = [pb.a_local(e, n, h) for e, n, h in filas]
    return doc.modelspace().add_polyline3d(locales, close=cerrada, dxfattribs={"layer": capa})
