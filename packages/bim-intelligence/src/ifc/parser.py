"""
Parser IFC con IfcOpenShell.
Extrae elementos estructurales, propiedades y jerarquía espacial.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import ifcopenshell
import ifcopenshell.util.element as ifc_elem
import ifcopenshell.util.placement as ifc_place
import numpy as np


ELEMENT_TYPES = {
    "structural": [
        "IfcBeam", "IfcColumn", "IfcSlab", "IfcWall",
        "IfcFoundation", "IfcFooting", "IfcPile",
    ],
    "architectural": [
        "IfcDoor", "IfcWindow", "IfcStair", "IfcRoof",
        "IfcCurtainWall", "IfcRamp",
    ],
    "mep": [
        "IfcPipe", "IfcDuct", "IfcCableCarrierSegment",
        "IfcFlowTerminal",
    ],
    "space": ["IfcSpace", "IfcZone", "IfcBuildingStorey"],
}


@dataclass
class BimElement:
    global_id: str
    ifc_type: str
    name: str
    description: str
    storey: str
    material: str
    properties: dict = field(default_factory=dict)
    # Bounding box centroide [x, y, z] en metros
    centroid: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    # Texto plano para embedding
    text_for_embedding: str = ""


def _safe_str(val) -> str:
    return str(val) if val is not None else ""


def _get_storey(element) -> str:
    container = ifcopenshell.util.element.get_container(element)
    if container and hasattr(container, "Name"):
        return _safe_str(container.Name)
    return "Sin nivel"


def _get_material(element) -> str:
    try:
        materials = ifcopenshell.util.element.get_materials(element)
        if materials:
            names = [_safe_str(m.Name) for m in materials if hasattr(m, "Name")]
            return ", ".join(names)
    except Exception:
        pass
    return ""


def _get_properties(element) -> dict:
    props = {}
    try:
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_name, pset_props in psets.items():
            for key, val in pset_props.items():
                props[f"{pset_name}.{key}"] = str(val)
    except Exception:
        pass
    return props


def _get_centroid(element) -> list[float]:
    try:
        placement = ifcopenshell.util.placement.get_local_placement(
            element.ObjectPlacement
        )
        return [float(placement[0][3]), float(placement[1][3]), float(placement[2][3])]
    except Exception:
        return [0.0, 0.0, 0.0]


def _build_text(elem: BimElement) -> str:
    parts = [
        f"Tipo: {elem.ifc_type}",
        f"Nombre: {elem.name}",
        f"Nivel: {elem.storey}",
    ]
    if elem.material:
        parts.append(f"Material: {elem.material}")
    if elem.description:
        parts.append(f"Descripción: {elem.description}")
    for k, v in list(elem.properties.items())[:10]:
        parts.append(f"{k}: {v}")
    return " | ".join(parts)


def parse_ifc(path: str | Path) -> Iterator[BimElement]:
    """Parsea un archivo IFC y emite BimElement por cada elemento relevante."""
    model = ifcopenshell.open(str(path))

    all_types = [t for types in ELEMENT_TYPES.values() for t in types]

    for ifc_type in all_types:
        for el in model.by_type(ifc_type):
            props = _get_properties(el)
            centroid = _get_centroid(el)
            elem = BimElement(
                global_id=_safe_str(el.GlobalId),
                ifc_type=ifc_type,
                name=_safe_str(getattr(el, "Name", "")),
                description=_safe_str(getattr(el, "Description", "")),
                storey=_get_storey(el),
                material=_get_material(el),
                properties=props,
                centroid=centroid,
            )
            elem.text_for_embedding = _build_text(elem)
            yield elem
