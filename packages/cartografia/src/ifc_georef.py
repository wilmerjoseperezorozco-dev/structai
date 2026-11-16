"""
Georreferenciación IFC (issue #211).

IFC4 / IFC4X3: IfcMapConversion (del contexto 'Model' a IfcProjectedCRS 'EPSG:9377').
IFC2X3: no tiene IfcMapConversion; se usan los conjuntos ePSet_MapConversion y ePSet_ProjectedCRS en IfcSite
(convención de buildingSMART "User Guide for Geo-referencing in IFC", 2020).
"""
from __future__ import annotations

import math

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.util.element as ue

from georef import EPSG_OFICIAL, PuntoBase

NOMBRE_CRS = f"EPSG:{EPSG_OFICIAL}"
DESCRIPCION_CRS = "MAGNA-SIRGAS 2018 / Origen-Nacional (CTM12, IGAC)"


def _contexto_modelo(model: ifcopenshell.file):
    for c in model.by_type("IfcGeometricRepresentationContext"):
        if not c.is_a("IfcGeometricRepresentationSubContext") and c.ContextType == "Model":
            return c
    raise ValueError("El IFC no tiene un IfcGeometricRepresentationContext 'Model'")


def _metro(model: ifcopenshell.file):
    for u in model.by_type("IfcSIUnit"):
        if u.UnitType == "LENGTHUNIT" and u.Name == "METRE" and not u.Prefix:
            return u
    return model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")


def georreferenciar(model: ifcopenshell.file, pb: PuntoBase) -> None:
    """Agrega (o reemplaza) la georreferenciación del modelo con el punto base."""
    if model.schema == "IFC2X3":
        _georreferenciar_2x3(model, pb)
        return
    contexto = _contexto_modelo(model)
    for op in list(model.by_type("IfcMapConversion")):
        if op.SourceCRS == contexto:
            crs = op.TargetCRS
            model.remove(op)
            if crs is not None and not model.get_inverse(crs):
                model.remove(crs)
    crs = model.create_entity(
        "IfcProjectedCRS", Name=NOMBRE_CRS, Description=DESCRIPCION_CRS, GeodeticDatum="MAGNA-SIRGAS 2018",
        MapProjection="Transverse Mercator", MapZone="Origen-Nacional", MapUnit=_metro(model))
    ax, ay = pb.eje_x
    model.create_entity(
        "IfcMapConversion", SourceCRS=contexto, TargetCRS=crs, Eastings=pb.e0, Northings=pb.n0,
        OrthogonalHeight=pb.h0, XAxisAbscissa=ax, XAxisOrdinate=ay, Scale=pb.escala)


def _georreferenciar_2x3(model: ifcopenshell.file, pb: PuntoBase) -> None:
    sitios = model.by_type("IfcSite")
    if not sitios:
        raise ValueError("El IFC2X3 no tiene IfcSite donde colgar ePSet_MapConversion")
    sitio = sitios[0]
    ax, ay = pb.eje_x
    for nombre, props in (
        ("ePSet_ProjectedCRS", {"Name": NOMBRE_CRS, "Description": DESCRIPCION_CRS,
                                "GeodeticDatum": "MAGNA-SIRGAS 2018", "MapProjection": "Transverse Mercator",
                                "MapZone": "Origen-Nacional"}),
        ("ePSet_MapConversion", {"Eastings": pb.e0, "Northings": pb.n0, "OrthogonalHeight": pb.h0,
                                 "XAxisAbscissa": ax, "XAxisOrdinate": ay, "Scale": pb.escala}),
    ):
        existente = ue.get_pset(sitio, nombre)
        if existente:                                   # reemplazar: se borra el conjunto anterior completo
            viejo = model.by_id(existente["id"])
            for rel in list(model.get_inverse(viejo)):
                model.remove(rel)
            for prop in list(viejo.HasProperties or []):
                model.remove(prop)
            model.remove(viejo)
        _pset_2x3(model, sitio, nombre, props)


def _pset_2x3(model: ifcopenshell.file, producto, nombre: str, props: dict) -> None:
    """Conjunto de propiedades IFC2X3 creado a mano: en 2X3 OwnerHistory es obligatorio y la API de ifcopenshell
    exige configurar un usuario; aquí se reutiliza el OwnerHistory que ya trae el archivo (Revit, ArchiCAD…)."""
    dueno = (model.by_type("IfcOwnerHistory") or [None])[0]
    valores = []
    for k, v in props.items():
        tipo = "IfcLabel" if isinstance(v, str) else "IfcReal"
        valores.append(model.create_entity("IfcPropertySingleValue", Name=k,
                                           NominalValue=model.create_entity(tipo, v)))
    pset = model.create_entity("IfcPropertySet", GlobalId=ifcopenshell.guid.new(), OwnerHistory=dueno,
                               Name=nombre, HasProperties=valores)
    model.create_entity("IfcRelDefinesByProperties", GlobalId=ifcopenshell.guid.new(), OwnerHistory=dueno,
                        RelatedObjects=[producto], RelatingPropertyDefinition=pset)


def leer_georef(model: ifcopenshell.file) -> PuntoBase | None:
    if model.schema == "IFC2X3":

        for sitio in model.by_type("IfcSite"):
            mc = ue.get_pset(sitio, "ePSet_MapConversion")
            crs = ue.get_pset(sitio, "ePSet_ProjectedCRS") or {}
            if mc:
                return _desde_valores(mc, crs.get("Name", NOMBRE_CRS))
        return None
    for op in model.by_type("IfcMapConversion"):
        v = {k: getattr(op, k) for k in ("Eastings", "Northings", "OrthogonalHeight", "XAxisAbscissa",
                                          "XAxisOrdinate", "Scale")}
        return _desde_valores(v, op.TargetCRS.Name if op.TargetCRS else NOMBRE_CRS)
    return None


def _desde_valores(v: dict, nombre_crs: str) -> PuntoBase:

    epsg = int(str(nombre_crs).upper().replace("EPSG:", "")) if str(nombre_crs).upper().startswith("EPSG:") else -1
    ax = v.get("XAxisAbscissa") if v.get("XAxisAbscissa") is not None else 1.0
    ay = v.get("XAxisOrdinate") if v.get("XAxisOrdinate") is not None else 0.0
    return PuntoBase(e0=float(v["Eastings"]), n0=float(v["Northings"]), h0=float(v.get("OrthogonalHeight") or 0.0),
                     rotacion_rad=math.atan2(ay, ax), escala=float(v.get("Scale") or 1.0), epsg=epsg,
                     fuente="ifc", fecha="", version_conversor="")
