"""Superficies limitadoras de obstáculos (RAC 14 Ed. 01 Rev. 05, Tablas D-1 y D-2) para una pista recta.

Solo numpy. Trabaja en coordenadas planas en metros (este, norte) de una proyección conforme local; quien llama
proyecta (por ejemplo con la cuadrícula urbana de Barranquilla, EPSG:6246).

Techo en un punto = la superficie MÁS BAJA que lo cubre, en m sobre el nivel del mar. Donde ninguna superficie cubre
el punto, el techo es +inf: no hay limitación aeronáutica de RAC 14 (sí puede haberla por PANS-OPS o radioayudas,
que aquí no se modelan).

Preregistro: docs/PREREGISTRO_TECHO_AERONAUTICO_BAQ_332.md (#332). La capa orienta y no autoriza: no reemplaza el
permiso de la Aerocivil (Código de Comercio, arts. 1823 a 1826).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Pista:
    """Pista recta entre dos umbrales (sin umbrales desplazados), en coordenadas planas."""
    umbral_a: tuple[float, float]       # (este, norte) del umbral del extremo A (p. ej. RWY 05)
    umbral_b: tuple[float, float]       # umbral del extremo B (p. ej. RWY 23)
    elev_a: float                       # m s. n. m. del umbral A
    elev_b: float
    elev_referencia: float              # elevación de referencia para la horizontal interna (m s. n. m.)
    franja_semiancho: float = 150.0     # franja de 300 m
    franja_extension: float = 60.0      # la franja sobresale 60 m de cada extremo


def _columna(tabla: dict, columna: str):
    return tabla.get(columna)


def cargar_tablas(ruta: Path = AQUI / "rac14_superficies.json") -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def _aproximacion(d, tab, col):
    """Altura sobre el umbral de la superficie de aproximación a distancia d (m) del borde interior. NaN fuera."""
    ap = tab["aterrizaje"]["aproximacion"]
    l1 = ap["primera_seccion"]["longitud"][col]
    p1 = ap["primera_seccion"]["pendiente"][col]
    total = (ap["longitud_total"].get(col) or l1)
    h = np.where(d <= l1, p1 * d, np.nan)
    seg = ap["segunda_seccion"]["longitud"].get(col)
    if seg:
        p2 = ap["segunda_seccion"]["pendiente"][col]
        h = np.where((d > l1) & (d <= l1 + seg), p1 * l1 + p2 * (d - l1), h)
        if ap["seccion_horizontal"]["longitud"].get(col):
            h = np.where((d > l1 + seg) & (d <= total), p1 * l1 + p2 * seg, h)
    return np.where((d >= 0) & (d <= total), h, np.nan)


def techo(este, norte, pista: Pista, aprox_a: str | None, aprox_b: str | None, despegue: str | None,
          forma_horizontal: str = "estadio", arp: tuple[float, float] | None = None,
          tablas: dict | None = None, detalle: bool = False):
    """Techo (m s. n. m.) en los puntos (este, norte).

    aprox_a / aprox_b: columna de la Tabla D-1 para el aterrizaje hacia el umbral A / B (p. ej. "precision_cat1_3_4",
    "no_precision_4"), o None si ese extremo no tiene aproximación. despegue: columna de la Tabla D-2 ("clave_3_4"), y
    se aplica en los dos sentidos. forma_horizontal: "estadio" (radio desde los extremos de la pista) o "circulo"
    (radio desde el ARP).
    detalle=True devuelve además un dict {superficie: altura} para auditar cuál limita.
    """
    tab = tablas or cargar_tablas()
    e = np.asarray(este, dtype=float)
    n = np.asarray(norte, dtype=float)
    ax, ay = pista.umbral_a
    bx, by = pista.umbral_b
    largo = float(np.hypot(bx - ax, by - ay))
    ux, uy = (bx - ax) / largo, (by - ay) / largo
    s = (e - ax) * ux + (n - ay) * uy            # a lo largo del eje, 0 en el umbral A y creciente hacia B
    t = -(e - ax) * uy + (n - ay) * ux           # lateral
    at = np.abs(t)

    def elev_eje(sv):
        return pista.elev_a + (pista.elev_b - pista.elev_a) * np.clip(sv, 0, largo) / largo

    sup: dict[str, np.ndarray] = {}
    inf = np.full(e.shape, np.inf)

    # Columna que define la horizontal interna y la cónica: la más exigente de las aproximaciones presentes.
    cols = [c for c in (aprox_a, aprox_b) if c]
    hi = tab["aterrizaje"]["horizontal_interna"]
    co = tab["aterrizaje"]["conica"]
    radio = max(hi["radio"][c] for c in cols)
    h_hi = pista.elev_referencia + hi["altura"][cols[0]]
    h_cono = max(co["altura"][c] for c in cols)
    p_cono = co["pendiente"][cols[0]]

    # Horizontal interna y cónica
    if forma_horizontal == "estadio":
        dist = np.where(s < 0, np.hypot(s, t), np.where(s > largo, np.hypot(s - largo, t), at))
    elif forma_horizontal == "circulo":
        cx, cy = arp if arp else ((ax + bx) / 2, (ay + by) / 2)
        dist = np.hypot(e - cx, n - cy)
    else:
        raise ValueError(forma_horizontal)
    sup["horizontal_interna"] = np.where(dist <= radio, h_hi, inf)
    lim_cono = radio + h_cono / p_cono
    sup["conica"] = np.where((dist > radio) & (dist <= lim_cono), h_hi + p_cono * (dist - radio), inf)

    # Aproximación y transición a lo largo de sus lados
    base_w = np.full(e.shape, np.nan)            # semiancho de la base de la transición
    base_h = np.full(e.shape, np.nan)            # altura de la base de la transición
    franja = (s >= -pista.franja_extension) & (s <= largo + pista.franja_extension)
    base_w = np.where(franja, pista.franja_semiancho, base_w)
    base_h = np.where(franja, elev_eje(s), base_h)
    ap = tab["aterrizaje"]["aproximacion"]
    for nombre, col, d, elev in (("aproximacion_a", aprox_a, -s - ap["distancia_desde_umbral"].get(aprox_a or "", 0), pista.elev_a),
                                 ("aproximacion_b", aprox_b, s - largo - ap["distancia_desde_umbral"].get(aprox_b or "", 0), pista.elev_b)):
        if not col:
            continue
        hw = ap["longitud_borde_interior"][col] / 2 + d * ap["divergencia_cada_lado"][col]
        h = elev + _aproximacion(d, tab, col)
        dentro = (d >= 0) & (at <= hw) & np.isfinite(h)
        sup[nombre] = np.where(dentro, h, inf)
        lado = (d >= 0) & np.isfinite(h) & (h < h_hi)
        base_w = np.where(lado & np.isnan(base_w), hw, base_w)
        base_h = np.where(lado & np.isnan(base_h), h, base_h)

    # Transición: pendiente medida perpendicular al eje, desde la base hasta la horizontal interna
    p_tr = min(tab["aterrizaje"]["transicion"]["pendiente"][c] for c in cols)
    h_tr = base_h + p_tr * (at - base_w)
    sup["transicion"] = np.where(np.isfinite(h_tr) & (at > base_w) & (h_tr <= h_hi), h_tr, inf)

    # Precisión: transición interna y aterrizaje interrumpido (solo cerca de la pista)
    for col, extremo in ((aprox_a, "a"), (aprox_b, "b")):
        if not col or not col.startswith("precision"):
            continue
        ti = tab["aterrizaje"]["transicion_interna"]["pendiente"][col]
        ai = tab["aterrizaje"]["aproximacion_interna"]
        w_ofz = ai["anchura"][col] / 2
        h_ti = elev_eje(s) + ti * (at - w_ofz)
        en_ofz = franja & (at > w_ofz) & (h_ti <= h_hi)
        sup[f"transicion_interna_{extremo}"] = np.where(en_ofz, h_ti, inf)
        ai_int = tab["aterrizaje"]["aterrizaje_interrumpido"]
        dist_ai = ai_int["distancia_desde_umbral"][col]
        dist_ai = min(dist_ai, largo) if isinstance(dist_ai, (int, float)) else largo + pista.franja_extension
        s0 = dist_ai if extremo == "a" else largo - dist_ai
        d_ai = (s - s0) if extremo == "a" else (s0 - s)
        hw_ai = ai_int["longitud_borde_interior"][col] / 2 + d_ai * ai_int["divergencia_cada_lado"][col]
        h_ai = elev_eje(np.full(e.shape, s0)) + ai_int["pendiente"][col] * d_ai
        sup[f"aterrizaje_interrumpido_{extremo}"] = np.where((d_ai >= 0) & (at <= hw_ai) & (h_ai <= h_hi), h_ai, inf)

    # Ascenso en el despegue, en los dos sentidos (empieza 60 m después del extremo de la pista)
    if despegue:
        dt = tab["despegue"]["ascenso_en_el_despegue"]
        for nombre, d, elev in (("despegue_hacia_b", s - largo - dt["distancia_desde_extremo_pista"][despegue], pista.elev_b),
                                ("despegue_hacia_a", -s - dt["distancia_desde_extremo_pista"][despegue], pista.elev_a)):
            hw = np.minimum(dt["longitud_borde_interior"][despegue] / 2 + d * dt["divergencia_cada_lado"][despegue],
                            dt["anchura_final"][despegue] / 2)
            h = elev + dt["pendiente"][despegue] * d
            sup[nombre] = np.where((d >= 0) & (d <= dt["longitud"][despegue]) & (at <= hw), h, inf)

    pila = np.stack(list(sup.values()))
    resultado = pila.min(axis=0)
    if detalle:
        nombres = np.array(list(sup.keys()))
        limita = np.where(np.isfinite(resultado), nombres[pila.argmin(axis=0)], "")
        return resultado, limita, sup
    return resultado


def pista_skbq(proyectar) -> tuple[Pista, tuple[float, float]]:
    """Pista de SKBQ desde skbq_ad2.json. proyectar(lon, lat) -> (este, norte)."""
    d = json.loads((AQUI / "skbq_ad2.json").read_text(encoding="utf-8"))
    u = d["pista"]["umbrales"]
    a = proyectar(u["05"]["lon"], u["05"]["lat"])
    b = proyectar(u["23"]["lon"], u["23"]["lat"])
    arp = proyectar(d["arp"]["lon"], d["arp"]["lat"])
    return Pista(a, b, u["05"]["elev_m"], u["23"]["elev_m"], d["elevacion_aerodromo_m"]), arp
