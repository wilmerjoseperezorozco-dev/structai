"""
Georreferenciación oficial IGAC con origen local (issue #211).

Sistema oficial: MAGNA-SIRGAS 2018 / Origen-Nacional, EPSG:9377 ("CTM12"; Res. IGAC 471 y 529 de 2020, Res. 370 de 2021)
    +proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +units=m

Por qué un punto base: cerca de E = 5.000.000 m el paso entre dos float32 consecutivos es 0,5 m, así que un visor
CAD/IFC/WebGL que guarda vértices en float32 "salta" medio metro. Se dibuja en coordenadas locales
(E - E0, N - N0, H - H0) y se guarda el punto base real (E0, N0, H0) en el archivo para volver al oficial sin pérdida.

Convención de rotación y escala: la de IfcMapConversion (IFC4), para que DXF, IFC y Supabase cuenten lo mismo:
    E = E0 + s·(x·cosθ − y·sinθ)
    N = N0 + s·(x·sinθ + y·cosθ)
    H = H0 + z
θ es el ángulo del eje X local medido desde el Este hacia el Norte (antihorario), y s la escala.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Iterable, Sequence

import numpy as np
from pyproj import CRS, Transformer

EPSG_OFICIAL = 9377
NOMBRE_OFICIAL = "MAGNA-SIRGAS 2018 / Origen-Nacional"
VERSION_CONVERSOR = "cartografia-0.1.0"

# Orígenes de entrada aceptados. MAGNA-SIRGAS geográfico (4686) y las zonas Gauss-Krüger anteriores
# (3114–3118, "origen Bogotá" = 3116) siguen apareciendo en planos y catastros viejos.
ORIGENES = {
    "WGS84": 4326,
    "MAGNA-SIRGAS": 4686,
    "MAGNA-SIRGAS-2018": 20046,
    "MAGNA-OESTE-OESTE": 3114,
    "MAGNA-OESTE": 3115,
    "MAGNA-BOGOTA": 3116,
    "MAGNA-ESTE": 3117,
    "MAGNA-ESTE-ESTE": 3118,
    "CTM12": EPSG_OFICIAL,
}

_TRANSFORMADORES: dict[tuple[int, int], Transformer] = {}


def _epsg(origen: int | str) -> int:
    if isinstance(origen, int):
        return origen
    clave = origen.upper().replace("EPSG:", "")
    if clave.isdigit():
        return int(clave)
    if clave not in ORIGENES:
        raise ValueError(f"Origen desconocido: {origen!r}. Usa un código EPSG o uno de {sorted(ORIGENES)}")
    return ORIGENES[clave]


def transformador(origen: int | str, destino: int | str = EPSG_OFICIAL) -> Transformer:
    """Transformer de pyproj con orden (x=lon/Este, y=lat/Norte), cacheado."""
    k = (_epsg(origen), _epsg(destino))
    if k not in _TRANSFORMADORES:
        _TRANSFORMADORES[k] = Transformer.from_crs(CRS.from_epsg(k[0]), CRS.from_epsg(k[1]), always_xy=True)
    return _TRANSFORMADORES[k]


def a_ctm12(x, y, origen: int | str = "WGS84"):
    """De un sistema de origen a EPSG:9377. Para geográficos, x = longitud y y = latitud (en grados)."""
    return transformador(origen).transform(x, y)


def de_ctm12(e, n, destino: int | str = "WGS84"):
    return transformador(EPSG_OFICIAL, destino).transform(e, n)


def dentro_de_colombia(lon: float, lat: float) -> bool:
    """¿Está dentro del área de uso que EPSG declara para 9377? (Colombia continental, insular y marítima)."""
    a = CRS.from_epsg(EPSG_OFICIAL).area_of_use
    return a.west <= lon <= a.east and a.south <= lat <= a.north


def paso_float32(valor: float) -> float:
    """Distancia al siguiente float32 representable: la resolución que tiene un visor en float32 en ese valor."""
    v = np.float32(valor)
    return float(np.spacing(v))


def error_float32(puntos: np.ndarray) -> float:
    """Máximo error (m) al guardar estas coordenadas en float32 y volverlas a leer."""
    p = np.asarray(puntos, dtype=np.float64)
    return float(np.max(np.abs(p.astype(np.float32).astype(np.float64) - p))) if p.size else 0.0


@dataclass(frozen=True)
class PuntoBase:
    """Punto base (E0, N0, H0) en EPSG:9377 + rotación/escala de la convención IfcMapConversion."""
    e0: float
    n0: float
    h0: float = 0.0
    rotacion_rad: float = 0.0
    escala: float = 1.0
    epsg: int = EPSG_OFICIAL
    fuente: str = "centroide"                # centroide | levantamiento | usuario | catastro
    fecha: str = field(default_factory=lambda: date.today().isoformat())
    version_conversor: str = VERSION_CONVERSOR

    def __post_init__(self):
        if self.epsg != EPSG_OFICIAL:
            raise ValueError(f"El punto base debe estar en EPSG:{EPSG_OFICIAL}; llegó EPSG:{self.epsg}")
        if not (self.escala > 0 and math.isfinite(self.escala)):
            raise ValueError("La escala debe ser un número positivo")
        for nombre in ("e0", "n0", "h0", "rotacion_rad"):
            if not math.isfinite(getattr(self, nombre)):
                raise ValueError(f"{nombre} no es finito")

    @property
    def eje_x(self) -> tuple[float, float]:
        """(XAxisAbscissa, XAxisOrdinate) de IfcMapConversion."""
        return math.cos(self.rotacion_rad), math.sin(self.rotacion_rad)

    def a_local(self, e, n, h=0.0):
        """Oficial (EPSG:9377) → local. Acepta escalares o arreglos."""
        c, s = self.eje_x
        de = (np.asarray(e, dtype=np.float64) - self.e0) / self.escala
        dn = (np.asarray(n, dtype=np.float64) - self.n0) / self.escala
        x = c * de + s * dn
        y = -s * de + c * dn
        z = np.asarray(h, dtype=np.float64) - self.h0
        return _escalar(x), _escalar(y), _escalar(z)

    def a_oficial(self, x, y, z=0.0):
        """Local → oficial (EPSG:9377)."""
        c, s = self.eje_x
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        e = self.e0 + self.escala * (c * x - s * y)
        n = self.n0 + self.escala * (s * x + c * y)
        h = self.h0 + np.asarray(z, dtype=np.float64)
        return _escalar(e), _escalar(n), _escalar(h)

    def como_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def desde_dict(cls, d: dict) -> "PuntoBase":
        campos = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        for k in ("e0", "n0", "h0", "rotacion_rad", "escala"):
            if k in campos:
                campos[k] = float(campos[k])
        if "epsg" in campos:
            campos["epsg"] = int(campos["epsg"])
        return cls(**campos)


def _escalar(a: np.ndarray):
    return float(a) if np.ndim(a) == 0 else a


def punto_base_desde(e: Sequence[float], n: Sequence[float], h: Sequence[float] | None = None, *,
                     redondeo: float = 1.0, fuente: str = "centroide", rotacion_rad: float = 0.0) -> PuntoBase:
    """Punto base = centro del rectángulo envolvente, redondeado a `redondeo` metros (legible y estable).

    Se usa el centro del envolvente y no la media: no lo mueve un levantamiento con muchos puntos en un solo sector.
    La cota base es la mínima redondeada hacia abajo, para que las z locales queden ≥ 0."""
    e = np.asarray(e, dtype=np.float64)
    n = np.asarray(n, dtype=np.float64)
    if e.size == 0 or e.shape != n.shape:
        raise ValueError("Se necesitan coordenadas E y N del mismo tamaño")
    r = float(redondeo)
    e0 = round((e.min() + e.max()) / 2 / r) * r
    n0 = round((n.min() + n.max()) / 2 / r) * r
    h0 = 0.0
    if h is not None and len(h):
        h0 = math.floor(float(np.min(h)) / r) * r
    return PuntoBase(e0=e0, n0=n0, h0=h0, fuente=fuente, rotacion_rad=rotacion_rad)


def proyectar_a_local(puntos: Iterable[Sequence[float]], origen: int | str = "WGS84",
                      punto_base: PuntoBase | None = None, *, redondeo: float = 1.0):
    """Lista de (x, y[, z]) en el sistema de origen → (arreglo N×3 local, PuntoBase).

    Si no se da punto base, se calcula con `punto_base_desde`. Las coordenadas geográficas van (lon, lat[, h])."""
    p = np.asarray(list(puntos), dtype=np.float64)
    if p.ndim != 2 or p.shape[1] not in (2, 3):
        raise ValueError("Cada punto debe ser (x, y) o (x, y, z)")
    z = p[:, 2] if p.shape[1] == 3 else np.zeros(len(p))
    if CRS.from_epsg(_epsg(origen)).is_geographic:
        fuera = [i for i, (lo, la) in enumerate(p[:, :2]) if not dentro_de_colombia(lo, la)]
        if fuera:
            raise ValueError(f"{len(fuera)} punto(s) fuera del área de uso de EPSG:{EPSG_OFICIAL} (primero: índice "
                             f"{fuera[0]}). ¿Longitud y latitud invertidas? El orden es (lon, lat).")
    e, n = a_ctm12(p[:, 0], p[:, 1], origen)
    e, n = np.asarray(e), np.asarray(n)
    if not np.all(np.isfinite(e)) or not np.all(np.isfinite(n)):
        raise ValueError("La proyección produjo valores no finitos: ¿lon/lat invertidos o sistema de origen errado?")
    pb = punto_base or punto_base_desde(e, n, z, redondeo=redondeo)
    x, y, zl = pb.a_local(e, n, z)
    return np.column_stack([x, y, zl]), pb
