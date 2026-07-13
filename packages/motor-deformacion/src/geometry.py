"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — GEOMETRÍA ANALÍTICA DE SECCIONES
Propiedades de área por integración (Teorema de Green):

  A    = ∬ dA
  Cx   = (1/A) ∬ x dA        Cy = (1/A) ∬ y dA
  Ix   = ∬ y² dA             Iy = ∬ x² dA        Ixy = ∬ xy dA

Para un polígono cerrado, estas integrales dobles se reducen (Green)
a sumas cerradas sobre los vértices — permite calcular con exactitud
CUALQUIER sección arbitraria (perfiles no estándar, secciones
compuestas, cortes irregulares) sin depender de un catálogo fijo.

Referencia: Bourke, P. "Calculating the area and centroid of a
polygon" — extendido a segundo momento de área vía Teorema de Green.
Validado en tests contra formas cerradas conocidas (rectángulo, círculo).
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
from typing import Optional

from .models import SeccionTransversal


Punto = tuple[float, float]


def _area_con_signo(vertices: list[Punto]) -> float:
    n = len(vertices)
    s = 0.0
    for i in range(n):
        x_i, y_i = vertices[i]
        x_j, y_j = vertices[(i + 1) % n]
        s += x_i * y_j - x_j * y_i
    return s / 2.0


def _asegurar_ccw(vertices: list[Punto]) -> list[Punto]:
    """El desarrollo de Green asume orientación antihoraria (CCW).
    Si el polígono viene en sentido horario, se invierte."""
    return vertices if _area_con_signo(vertices) >= 0 else list(reversed(vertices))


def propiedades_poligono(vertices: list[Punto]) -> dict:
    """
    Calcula área, centroide, momentos de inercia centroidales (Ix, Iy, Ixy)
    y momentos/ejes principales de un polígono simple cerrado arbitrario.

    vertices: lista de (x, y) en metros, sin repetir el primer punto al final.
    """
    if len(vertices) < 3:
        raise ValueError("Se requieren al menos 3 vértices para definir un área")

    v = _asegurar_ccw(vertices)
    n = len(v)

    A = _area_con_signo(v)
    if abs(A) < 1e-15:
        raise ValueError("Área nula o degenerada — verifique los vértices")

    cx = cy = 0.0
    Ix_o = Iy_o = Ixy_o = 0.0   # respecto al origen del sistema de coordenadas dado

    for i in range(n):
        x_i, y_i = v[i]
        x_j, y_j = v[(i + 1) % n]
        cruz = x_i * y_j - x_j * y_i

        cx += (x_i + x_j) * cruz
        cy += (y_i + y_j) * cruz

        Ix_o += (y_i ** 2 + y_i * y_j + y_j ** 2) * cruz
        Iy_o += (x_i ** 2 + x_i * x_j + x_j ** 2) * cruz
        Ixy_o += (x_i * y_j + 2 * x_i * y_i + 2 * x_j * y_j + x_j * y_i) * cruz

    cx /= (6.0 * A)
    cy /= (6.0 * A)
    Ix_o /= 12.0
    Iy_o /= 12.0
    Ixy_o /= 24.0

    # Teorema de ejes paralelos: trasladar del origen al centroide
    Ix = Ix_o - A * cy ** 2
    Iy = Iy_o - A * cx ** 2
    Ixy = Ixy_o - A * cx * cy

    # Momentos principales (diagonalización del tensor de inercia 2x2)
    I_prom = (Ix + Iy) / 2.0
    R = math.sqrt(((Ix - Iy) / 2.0) ** 2 + Ixy ** 2)
    I1 = I_prom + R
    I2 = I_prom - R
    theta_p = 0.5 * math.atan2(-2 * Ixy, Ix - Iy) if (Ix != Iy or Ixy != 0) else 0.0

    y_vals = [p[1] for p in v]
    c_sup = max(y_vals) - cy
    c_inf = cy - min(y_vals)

    return {
        "area": abs(A), "cx": cx, "cy": cy,
        "Ix": abs(Ix), "Iy": abs(Iy), "Ixy": Ixy,
        "I1": abs(I1), "I2": abs(I2), "theta_p_rad": theta_p,
        "c_sup": abs(c_sup), "c_inf": abs(c_inf),
        "vertices_centrados": [(x - cx, y - cy) for x, y in v],
    }


def _primer_momento_max_generico(vertices_centrados: list[Punto], cy_ref: float = 0.0, n_franjas: int = 400) -> float:
    """
    Q_max = ∫ y dA desde el eje neutro hasta la fibra extrema — necesario para
    esfuerzo cortante τ=VQ/(Ib). Para secciones no estándar se integra
    numéricamente (regla del punto medio) sobre franjas horizontales, ya que
    una fórmula cerrada general requiere resolver la intersección del
    polígono con cada franja (caso general de "cortes" de sección).
    """
    ys = [p[1] for p in vertices_centrados]
    y_min, y_max = min(ys), max(ys)
    h = (y_max - y_min) / n_franjas
    q = 0.0
    for k in range(n_franjas // 2, n_franjas):  # desde el eje neutro (y=0) hacia arriba
        y0 = y_min + k * h
        y1 = y0 + h
        y_mid = (y0 + y1) / 2.0
        if y_mid < 0:
            continue
        ancho = _ancho_en_y(vertices_centrados, y_mid)
        q += ancho * h * y_mid
    return abs(q)


def _ancho_en_y(vertices_centrados: list[Punto], y: float) -> float:
    """Ancho del polígono (suma de intersecciones) en la cota y — usado para
    integrar Q(y) y para hallar el ancho del alma en el eje neutro."""
    n = len(vertices_centrados)
    xs_interseccion: list[float] = []
    for i in range(n):
        x1, y1 = vertices_centrados[i]
        x2, y2 = vertices_centrados[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            t = (y - y1) / (y2 - y1)
            xs_interseccion.append(x1 + t * (x2 - x1))
    xs_interseccion.sort()
    ancho = 0.0
    for i in range(0, len(xs_interseccion) - 1, 2):
        ancho += xs_interseccion[i + 1] - xs_interseccion[i]
    return ancho


def seccion_desde_poligono(nombre: str, vertices: list[Punto], cov_dimension: float = 0.02) -> SeccionTransversal:
    """Sección transversal arbitraria — vértices en metros, sentido cualquiera."""
    props = propiedades_poligono(vertices)
    q_max = _primer_momento_max_generico(props["vertices_centrados"])
    ancho_en_neutro = _ancho_en_y(props["vertices_centrados"], 0.0)
    return SeccionTransversal(
        nombre=nombre, area=props["area"], Ix=props["Ix"], Iy=props["Iy"], Ixy=props["Ixy"],
        c_sup=props["c_sup"], c_inf=props["c_inf"],
        ancho_alma=ancho_en_neutro if ancho_en_neutro > 0 else None,
        Q_max=q_max, cov_dimension=cov_dimension,
    )


# ── Formas cerradas de uso frecuente (forma rápida, resultado exacto) ─────────

def seccion_rectangular(b: float, h: float, cov_dimension: float = 0.02) -> SeccionTransversal:
    """b: ancho (m), h: altura (m). Eje x fuerte = flexión sobre h."""
    area = b * h
    return SeccionTransversal(
        nombre=f"Rectangular {b*100:.0f}×{h*100:.0f} cm",
        area=area, Ix=b * h ** 3 / 12.0, Iy=h * b ** 3 / 12.0, Ixy=0.0,
        c_sup=h / 2.0, c_inf=h / 2.0, ancho_alma=b, Q_max=area * h / 8.0,
        cov_dimension=cov_dimension,
    )


def seccion_circular(r: float, cov_dimension: float = 0.02) -> SeccionTransversal:
    """Sección circular sólida, radio r (m)."""
    area = math.pi * r ** 2
    I = math.pi * r ** 4 / 4.0
    return SeccionTransversal(
        nombre=f"Circular ⌀{2*r*100:.0f} cm",
        area=area, Ix=I, Iy=I, Ixy=0.0, c_sup=r, c_inf=r,
        ancho_alma=2 * r, Q_max=(2.0 / 3.0) * r ** 3, cov_dimension=cov_dimension,
    )


def seccion_circular_hueca(r_ext: float, r_int: float, cov_dimension: float = 0.02) -> SeccionTransversal:
    """Tubo circular (r_ext > r_int), ambos en m."""
    area = math.pi * (r_ext ** 2 - r_int ** 2)
    I = math.pi * (r_ext ** 4 - r_int ** 4) / 4.0
    q_max = (2.0 / 3.0) * (r_ext ** 3 - r_int ** 3)
    return SeccionTransversal(
        nombre=f"Tubo ⌀{2*r_ext*100:.0f}/⌀{2*r_int*100:.0f} cm",
        area=area, Ix=I, Iy=I, Ixy=0.0, c_sup=r_ext, c_inf=r_ext,
        ancho_alma=2 * (r_ext - r_int), Q_max=q_max, cov_dimension=cov_dimension,
    )


def seccion_I(b_ala: float, t_ala: float, h_alma: float, t_alma: float, cov_dimension: float = 0.02) -> SeccionTransversal:
    """
    Perfil I/H simétrico compuesto por 3 rectángulos (ala sup, alma, ala inf).
    b_ala: ancho del ala (m) · t_ala: espesor del ala (m)
    h_alma: altura libre del alma entre alas (m) · t_alma: espesor del alma (m)
    Ix se obtiene sumando cada rectángulo trasladado (teorema de ejes paralelos),
    de igual forma que integrar la sección compuesta pieza a pieza.
    """
    h_total = h_alma + 2 * t_ala
    y_centro = h_total / 2.0

    area_ala = b_ala * t_ala
    area_alma = t_alma * h_alma
    area = 2 * area_ala + area_alma

    d_alas = (h_alma + t_ala) / 2.0   # distancia centroide de cada ala al eje neutro
    I_alas = 2 * (b_ala * t_ala ** 3 / 12.0 + area_ala * d_alas ** 2)
    I_alma = t_alma * h_alma ** 3 / 12.0
    Ix = I_alas + I_alma

    Iy_alas = 2 * (t_ala * b_ala ** 3 / 12.0)
    Iy_alma = h_alma * t_alma ** 3 / 12.0
    Iy = Iy_alas + Iy_alma

    q_max = area_ala * d_alas + (t_alma * (h_alma / 2.0) ** 2) / 2.0

    return SeccionTransversal(
        nombre=f"Perfil I {b_ala*100:.0f}×{h_total*100:.0f} cm",
        area=area, Ix=Ix, Iy=Iy, Ixy=0.0,
        c_sup=y_centro, c_inf=y_centro, ancho_alma=t_alma, Q_max=q_max,
        cov_dimension=cov_dimension,
    )
