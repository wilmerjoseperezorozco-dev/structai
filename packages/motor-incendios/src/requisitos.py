"""Requisitos de protección contra incendios de la NSR-10 (#336 F1): categoría de riesgo (J.3.3), exenciones (J.3.3.3),
resistencia requerida en horas (J.3.4-3), verificación de elementos de concreto (J.3.5) y sistemas de extinción
exigidos por grupo de ocupación (J.4.3).

Lo que decide la NSR-10 es CUÁNDO se exige un sistema. CÓMO se diseña (NFPA 13/14/10, NTC 2301/1669/2885) no está aquí.
El grupo y subgrupo de ocupación (K.2) los declara el usuario. El motor no los infiere del nombre del proyecto.

Interpretaciones declaradas (HIPÓTESIS, en `SUPUESTOS`):
  - "más de N pisos o H m de altura, lo que sea mayor" se aplica como (pisos > N) o (altura > H): la lectura más exigente;
  - en los límites exactos de área de las tablas J.3.3 se usa la fila más exigente;
  - para A, F y P la categoría sale de la Tabla J.3.3-2 (J.3.3.2), aunque J.3.3.1 los liste en una categoría fija.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from . import tablas_j as T

SUPUESTOS = (
    "Umbral 'más de N pisos o H m, lo que sea mayor' aplicado como pisos > N o altura > H (lectura más exigente).",
    "En el límite exacto de área de la Tabla J.3.3-1 se usa la fila más exigente (la tabla usa > y <).",
    "Grupos A, F y P: categoría por potencial combustible (Tabla J.3.3-2), como indica J.3.3.2.",
    "Elementos de concreto sin restricción a la expansión térmica salvo demostración avalada (J.3.5.1).",
    "El grupo y subgrupo de ocupación (K.2) los declara el usuario; el motor no los infiere.",
)
ORDEN_CAT = {"I": 0, "II": 1, "III": 2}         # I es la más exigente


@dataclass
class Resultado:
    valor: object
    numeral: str
    motivo: str = ""


def _grupo(subgrupo: str) -> str:
    return subgrupo.split("-")[0]


def _col_pisos(pisos: int, n_cols: int) -> int:
    return min(max(pisos, 1), n_cols) - 1


def categoria_riesgo(subgrupo: str, pisos: int, area_total_m2: float, *, cc_mj_m2: Optional[float] = None,
                     alarmas_y_rociadores: bool = False, area_unidad_promedio_m2: Optional[float] = None) -> Resultado:
    """Categoría I/II/III (J.3.3). None si la tabla no da un valor verificado o falta un dato."""
    g = _grupo(subgrupo)
    if pisos > 10:                                                  # J.3.3.1.1 (c) y J.3.3.1.2 (a)
        return Resultado("II" if alarmas_y_rociadores else "I", "J.3.3.1.2(a)" if alarmas_y_rociadores else "J.3.3.1.1(c)")
    if g in T.J33_2:
        if cc_mj_m2 is None:
            return Resultado(None, "J.3.3-2", "falta el potencial combustible Cc (J.3.4)")
        filas = T.J33_2[g]
        # en el límite se toma la fila más exigente: la de Cc mayor
        for cmin, cmax, cats in filas:
            if cmin <= cc_mj_m2 <= cmax:
                return Resultado(cats[_col_pisos(pisos, 5)], "Tabla J.3.3-2")
    if subgrupo in ("R-1", "R-2"):
        # J.3.3.1.3 (a) pone R-1 de ≤ 10 pisos en III, pero J.3.3.2 manda clasificar con la Tabla J.3.3-1 (por unidad)
        if area_unidad_promedio_m2 is None:
            return Resultado(None, "Tabla J.3.3-1", "falta el área promedio de unidad (nota 1)")
        clave = "mayor_140" if area_unidad_promedio_m2 > 140 else "hasta_140"
        cats = T.J33_1_RESIDENCIAL_UNIDAD[clave]
        if cats is None:
            return Resultado(None, "Tabla J.3.3-1", "fila (R-1),(R-2) sin verificar en el PDF (ver tablas_j.VERIFICAR)")
        return Resultado(cats[_col_pisos(pisos, 7)], "Tabla J.3.3-1")
    filas = T.J33_1.get(subgrupo)
    if filas is None:
        return Resultado(None, "J.3.3", f"subgrupo {subgrupo} sin fila en las tablas J.3.3")
    # en la igualdad pertenece a la fila más exigente: se recorren de mayor a menor área con límite inferior inclusivo
    for amin, amax, cats in filas:
        if amin <= area_total_m2 and (area_total_m2 < amax or math.isinf(amax)):
            if cats is None:
                return Resultado(None, "Tabla J.3.3-1", f"fila {subgrupo} con AT en [{amin:g}, {amax:g}) sin verificar")
            return Resultado(cats[_col_pisos(pisos, 7)], "Tabla J.3.3-1")
    return Resultado(None, "Tabla J.3.3-1", "área fuera de las filas")


@dataclass
class Edificacion:
    subgrupo: str                                 # K.2: "C-1", "R-2", "I-3", ...
    pisos: int                                    # sobre el nivel de la calle
    altura_m: float
    area_total_m2: float                          # incluidas las áreas de mezanines
    area_max_piso_m2: Optional[float] = None
    pisos_bajo_calle: int = 0
    area_piso_bajo_calle_m2: float = 0.0          # C-2: piso bajo calle con mercancías combustibles
    mercancia_combustible_bajo_calle: bool = False
    area_sin_muros_cortafuego_m2: float = 0.0     # A-1 y F-1
    aislamiento_m: float = math.inf               # a áreas de uso público y linderos (A-1 y F-1)
    acceso_publico: bool = False                  # grupo A
    volumen_llantas_m3: float = 0.0               # grupo A
    confinamiento: bool = False                   # I-1
    carga_ocupacion: int = 0                      # L
    l3_con_fiestas_o_alcohol: bool = True         # L-3
    distancia_max_acceso_bomberos_m: float = 0.0  # I y L
    estacionamiento_bajo: bool = False            # R-2 y R-3
    escenario: bool = False                       # L
    usos_mixtos: tuple = ()                       # M: subgrupos de cada uso
    estructura_incombustible: bool = False
    cc_mj_m2: Optional[float] = None
    explosivos_o_inflamables: bool = False
    espacio_libre_perimetral_m: float = 0.0
    uso_temporal: bool = False


def exento_cuantificacion(e: Edificacion) -> Resultado:
    """J.3.3.3: edificaciones que no requieren cuantificar su resistencia al fuego (J.4 sigue aplicando).
    No se modelan J.3.3.3.5 (estacionamientos abiertos), J.3.3.3.10 (incremento por calles) ni J.3.3.3.11–12."""
    g, s = _grupo(e.subgrupo), e.subgrupo
    a_piso = e.area_max_piso_m2 if e.area_max_piso_m2 is not None else e.area_total_m2 / max(e.pisos, 1)
    reglas = [
        (g == "C" and e.pisos <= 2 and a_piso <= 500, "J.3.3.3.1"),
        (s == "I-3" and e.pisos == 1 and e.area_total_m2 <= 1200, "J.3.3.3.2"),
        (s in ("R-1", "R-2") and e.pisos <= 3, "J.3.3.3.3"),
        (g == "E" and e.pisos <= 2, "J.3.3.3.4"),
        (g == "F" and not e.explosivos_o_inflamables and e.pisos <= 2 and a_piso <= 1000, "J.3.3.3.6"),
        (g == "F" and e.pisos == 1 and e.espacio_libre_perimetral_m > 10, "J.3.3.3.7"),
        (e.estructura_incombustible and e.cc_mj_m2 is not None and e.cc_mj_m2 <= 250, "J.3.3.3.8"),
        (g == "T" and e.uso_temporal, "J.3.3.3.9"),
    ]
    for cumple, num in reglas:
        if cumple:
            return Resultado(True, num)
    return Resultado(False, "J.3.3.3")


def horas_requeridas(categoria: str) -> dict[str, Optional[float]]:
    """Tabla J.3.4-3: horas por tipo de elemento para la categoría dada."""
    i = ORDEN_CAT[categoria]
    return {k: v[i] for k, v in T.J34_3.items()}


def _idx_horas(h: float) -> int:
    """Índice de la columna de horas que cubre h (la primera ≥ h)."""
    for i, hh in enumerate(T.HORAS):
        if h <= hh + 1e-9:
            return i
    raise ValueError(f"{h} h supera las tablas J.3.5 (máx. 4 h)")


@dataclass
class Verificacion:
    elemento: str
    numeral: str
    requerido: Optional[float]
    provisto: float
    unidad: str
    cumple: bool
    nota: str = ""


def verificar_concreto(horas: float, *, agregado: str = "siliceo", restringido: bool = False,
                       columnas_mm: tuple = (), losa_mm: Optional[float] = None, recub_losa_mm: Optional[float] = None,
                       vigas: tuple = ()) -> list[Verificacion]:
    """J.3.5.2 para la resistencia `horas` (≥ 1 h). columnas_mm: lados (b, h) por columna; vigas: (ancho, recubrimiento).
    Los recubrimientos de J.3.5 nunca valen menos que los del Título C: aquí solo se compara el recubrimiento provisto
    contra J (el del Título C lo verifica el diseño del elemento)."""
    out: list[Verificacion] = []
    if horas < 1.0:
        return out                                                  # J.3.5.2 aplica a resistencias ≥ 1 h
    i = _idx_horas(horas)
    ag_col = "liviano" if "liviano" in agregado else agregado
    for b, h in columnas_mm:
        req = T.J35_1[ag_col][i]
        nota = ""
        hh = T.HORAS[i]
        if hh in T.J35_1_REDUCIDA and max(b, h) >= T.J35_1_LADO_REDUCCION_MM:
            req, nota = min(req, T.J35_1_REDUCIDA[hh]), "reducida: dos lados paralelos ≥ 950 mm (notas de J.3.5-1)"
        out.append(Verificacion("columna", "Tabla J.3.5-1", req, min(b, h), "mm", min(b, h) >= req, nota))
    if losa_mm is not None:
        ag_l = {"liviano": "finos_livianos"}.get(agregado, agregado)
        req = T.J35_2[ag_l][i]
        out.append(Verificacion("losa (espesor)", "Tabla J.3.5-2", req, losa_mm, "mm", losa_mm >= req))
    if recub_losa_mm is not None:
        req = T.J35_3["restringida" if restringido else "no_restringida"][ag_col][i]
        out.append(Verificacion("losa (recubrimiento)", "Tabla J.3.5-3", req, recub_losa_mm, "mm", recub_losa_mm >= req))
    tabla = T.J35_5["restringida" if restringido else "no_restringida"]
    for ancho, recub in vigas:
        req = _recub_viga(tabla, ancho, i)
        if req is None:
            out.append(Verificacion("viga (recubrimiento)", "Tabla J.3.5-5", None, recub, "mm", False,
                                    "ancho no permitido para esta resistencia sin restricción"))
        else:
            out.append(Verificacion("viga (recubrimiento)", "Tabla J.3.5-5", req, recub, "mm", recub >= req - 1e-9))
    return out


def _recub_viga(tabla, ancho: float, i: int) -> Optional[float]:
    a = T.J35_5_ANCHOS
    if ancho < a[0]:
        return None
    if ancho >= a[-1]:
        return tabla[-1][i]
    for k in range(len(a) - 1):
        if a[k] <= ancho <= a[k + 1]:
            r0, r1 = tabla[k][i], tabla[k + 1][i]
            if r0 is None or r1 is None:
                return None if r0 is None and ancho == a[k] else (r1 if r0 is None else r0)
            t = (ancho - a[k]) / (a[k + 1] - a[k])
            return r0 + t * (r1 - r0)                                 # nota 1: interpolación
    return None


# ---------------------------------------------------------------------------------------------------------------------
# J.4.3: sistemas de extinción exigidos
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Exigencia:
    sistema: str                   # "rociadores" | "tomas_fijas_mangueras" | "extintores" | "estaciones_manguera_38mm"
    exigido: bool
    numerales: list = field(default_factory=list)
    alcance: str = "toda la edificación"
    nota: str = ""


def _supera(e: Edificacion, n_pisos: int, h_m: float) -> bool:
    return e.pisos > n_pisos or e.altura_m > h_m


def _por_subgrupo(e: Edificacion, s: str) -> list[Exigencia]:
    g = _grupo(s)
    roc, tom, ext = Exigencia("rociadores", False), Exigencia("tomas_fijas_mangueras", False), Exigencia("extintores", False)
    extra: list[Exigencia] = []

    def r(cond, num, alcance=None):
        if cond:
            roc.exigido = True
            roc.numerales.append(num)
            if alcance:
                roc.alcance = alcance

    def t(cond, num):
        if cond:
            tom.exigido = True
            tom.numerales.append(num)

    if g == "A":
        a1 = s == "A-1"
        r(a1 and _supera(e, 3, 9.0), "J.4.3.1.1(a)")
        r(a1 and e.area_sin_muros_cortafuego_m2 > 1000, "J.4.3.1.1(b)")
        r(a1 and e.aislamiento_m < 18, "J.4.3.1.1(c)")
        r(a1 and e.area_total_m2 > 2200, "J.4.3.1.1(d)")
        r(e.acceso_publico, "J.4.3.1.1(e)")
        r(e.volumen_llantas_m3 > 500, "J.4.3.1.1(f)")
        t(True, "J.4.3.1.2")
        ext.exigido, ext.numerales = True, ["J.4.3.1.3"]
    elif g == "C":
        r(s == "C-2" and _supera(e, 3, 9.0), "J.4.3.2.1(a)")
        r(s == "C-2" and e.area_total_m2 > 1100, "J.4.3.2.1(b)")
        r(s == "C-2" and e.pisos_bajo_calle > 0 and e.area_piso_bajo_calle_m2 > 200 and e.mercancia_combustible_bajo_calle,
          "J.4.3.2.1(c)")
        r(s == "C-1" and _supera(e, 6, 18.0), "J.4.3.2.1(d)")
        t(True, "J.4.3.2.2")
        ext.exigido, ext.numerales = True, ["J.4.3.2.3"]
    elif g == "F":
        r(s == "F-1" and _supera(e, 3, 9.0), "J.4.3.3.1(a)")
        r(s == "F-1" and e.area_sin_muros_cortafuego_m2 > 1000, "J.4.3.3.1(b)")
        r(s == "F-2" and e.area_total_m2 > 2200, "J.4.3.3.1(c)")
        r(s == "F-1" and e.aislamiento_m < 18, "J.4.3.3.1(d)")
        r(s == "F-2" and _supera(e, 6, 18.0), "J.4.3.3.1(e)")
        t(True, "J.4.3.3.2")
        ext.exigido, ext.numerales = True, ["J.4.3.3.3"]
    elif g == "I":
        r(s == "I-1" and e.confinamiento, "J.4.3.4.1(a)")
        r(s == "I-2", "J.4.3.4.1(b)")
        r(s == "I-3" and e.area_total_m2 >= 2000, "J.4.3.4.1(c)")
        r(s == "I-3" and _supera(e, 4, 12.0), "J.4.3.4.1(d)")
        r(s == "I-3" and e.pisos_bajo_calle >= 1, "J.4.3.4.1(e)")
        if s in ("I-4", "I-5"):
            roc.nota = "J.4.3.4.1(f): según su uso (oficinas como C-1, asambleas como L); declárelo como uso mixto (M)"
        t(_supera(e, 3, 9.0), "J.4.3.4.2(a)")
        t(e.pisos_bajo_calle >= 1, "J.4.3.4.2(b)")
        t(e.distancia_max_acceso_bomberos_m > 30, "J.4.3.4.2(c)")
        ext.exigido, ext.numerales = True, ["J.4.3.4.3"]
    elif g == "L":
        r(e.carga_ocupacion > 300, "J.4.3.5.1(a)")
        if e.carga_ocupacion > 300:
            roc.nota = "J.4.3.5.1(a) tiene exenciones (i)–(iv) que el motor no evalúa: verifíquelas"
        r(s == "L-3" and e.l3_con_fiestas_o_alcohol, "J.4.3.5.1(b)")
        r(e.escenario, "J.4.3.5.1(c)")
        t(_supera(e, 4, 12.0), "J.4.3.5.2(a)")
        t(e.pisos_bajo_calle >= 2, "J.4.3.5.2(b)")
        t(e.distancia_max_acceso_bomberos_m > 30 and not roc.exigido, "J.4.3.5.2(c)")
        if e.escenario:
            extra.append(Exigencia("estaciones_manguera_38mm", True, ["J.4.3.5.2(d)"], "a cada lado del escenario"))
        ext.exigido, ext.numerales = True, ["J.4.3.5.3"]
        ext.nota = "no aplica en tribunas, graderías, canchas ni lugares abiertos (J.4.3.5.3)"
    elif g == "P":
        r(True, "J.4.3.7.1")
        t(True, "J.4.3.7.2")
        ext.exigido, ext.numerales = True, ["J.4.3.7.3"]
    elif s == "R-2":
        r(e.pisos > 7, "J.4.3.8.1(a)", "zonas comunes (pasillos y circulación), excepto escaleras")
        r(e.estacionamiento_bajo, "J.4.3.8.1(b)", roc.alcance if e.pisos <= 7 else None)
        if e.estacionamiento_bajo:
            roc.alcance = ("zonas comunes y todo el estacionamiento bajo el edificio" if e.pisos > 7
                           else "todo el estacionamiento bajo el edificio")
        t(_supera(e, 5, 15.0), "J.4.3.8.2(a)")
        t(e.estacionamiento_bajo, "J.4.3.8.2(b)")
        if e.altura_m > 15:
            extra.append(Exigencia("estaciones_manguera_38mm", True, ["J.4.3.8.2(c)"], "en toda la altura"))
        ext.exigido, ext.numerales = True, ["J.4.3.8.3"]
    elif s == "R-3":
        r(_supera(e, 5, 15.0), "J.4.3.9.1(a)")
        r(e.estacionamiento_bajo, "J.4.3.9.1(b)")
        if e.estacionamiento_bajo and not _supera(e, 5, 15.0):
            roc.alcance = "todo el estacionamiento bajo el edificio"
        t(_supera(e, 5, 15.0), "J.4.3.9.2(a)")
        t(e.estacionamiento_bajo, "J.4.3.9.2(b)")
        if e.pisos > 5:
            extra.append(Exigencia("estaciones_manguera_38mm", True, ["J.4.3.9.2(c)"], "en toda la altura"))
        ext.exigido, ext.numerales = True, ["J.4.3.9.3"]
    else:
        nota = (f"J.4.3 no tiene numeral propio para {s}; J.4.3 exige recursos de extinción en toda edificación según su "
                "uso: el diseñador debe definirlos")
        return [Exigencia("rociadores", False, [], nota=nota), Exigencia("tomas_fijas_mangueras", False, [], nota=nota),
                Exigencia("extintores", False, [], nota=nota)]
    if roc.exigido and tom.exigido and g in ("I", "L"):
        tom.nota = "con rociadores, las tomas fijas se diseñan según NTC 2301 y NFPA 13 (J.4.3.4.2(d) / J.4.3.5.2(e))"
    return [roc, tom, ext] + extra


def sistemas_exigidos(e: Edificacion) -> list[Exigencia]:
    """J.4.3 por subgrupo. Grupo M: la unión de las exigencias de cada uso declarado en `usos_mixtos` (J.4.3.6)."""
    if _grupo(e.subgrupo) != "M":
        return _por_subgrupo(e, e.subgrupo)
    if not e.usos_mixtos:
        return [Exigencia(s, False, ["J.4.3.6"], nota="declare los usos del grupo M en usos_mixtos")
                for s in ("rociadores", "tomas_fijas_mangueras", "extintores")]
    union: dict[str, Exigencia] = {}
    for s in e.usos_mixtos:
        for x in _por_subgrupo(e, s):
            u = union.setdefault(x.sistema, Exigencia(x.sistema, False, [], x.alcance))
            if x.exigido:
                u.exigido = True
                u.numerales += [f"{n} (uso {s})" for n in x.numerales]
                u.alcance = x.alcance if u.alcance == "toda la edificación" else u.alcance
            if x.nota and x.nota not in u.nota:
                u.nota = (u.nota + "; " if u.nota else "") + x.nota
    for u in union.values():
        u.numerales.insert(0, "J.4.3.6")
    return list(union.values())
