"""Georreferencia del plano U-16 del POT de Barranquilla (Decreto 0212 de 2014, versión de octubre de 2019).

El PDF es un plano vectorial con cuadrícula métrica cada 5 km (MAGNA-SIRGAS, Transversa de Mercator, origen
Barranquilla: latitud 10,923183, falso este 917 264,4, falso norte 1 699 839,9, factor de escala 1). El meridiano de
origen no viene impreso; se toma el de la cuadrícula urbana oficial de Barranquilla (EPSG:6246, -74,8343313°), que
comparte origen y falsos con lo impreso.

1. Ajuste afín (mínimos cuadrados) entre los puntos del PDF y las coordenadas de las etiquetas de la cuadrícula métrica.
2. Control INDEPENDIENTE (preregistro #332): 5 etiquetas de la cuadrícula geográfica (grados-minutos), que el plano
   dibuja por separado. Se proyectan con pyproj y se comparan con la posición que predice el ajuste. Criterio fijado:
   todas a < 30 m.

Uso (entorno geo, fuera del venv de la API):
    python -I scripts/aeronautico/georef_u16.py <ruta U16.pdf> [salida.json]
"""
from __future__ import annotations

import json
import re
import sys
import warnings

import numpy as np
import pymupdf
from pyproj import CRS, Transformer

warnings.filterwarnings("ignore")

CRS_U16 = CRS.from_proj4("+proj=tmerc +lat_0=10.9231830833333 +lon_0=-74.8343313333333 +k=1 "
                         "+x_0=917264.406 +y_0=1699839.935 +ellps=GRS80 +units=m +no_defs")
A_U16 = Transformer.from_crs("EPSG:4686", CRS_U16, always_xy=True)
DE_U16 = Transformer.from_crs(CRS_U16, "EPSG:4686", always_xy=True)
UMBRAL_CONTROL_M = 30.0


def _num(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def etiquetas(pdf: str):
    pg = pymupdf.open(pdf)[0]
    este, norte, lon, lat = [], [], [], []
    for x0, y0, x1, y1, s, *_ in pg.get_text("words"):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if re.fullmatch(r"9\d\d\.\d{3}", s):                         # etiqueta de este, sobre el borde sup/inf
            este.append((cx, cy, _num(s)))
        elif re.fullmatch(r"1\.\d{3}\.\d{3}", s):                    # etiqueta de norte, rotada en los bordes
            norte.append((cx, cy, _num(s)))
        else:
            m = re.fullmatch(r"(\d+)\D(\d+)'([NO])", s)
            if m:
                v = int(m.group(1)) + int(m.group(2)) / 60
                (lon if m.group(3) == "O" else lat).append((cx, cy, -v if m.group(3) == "O" else v))
    return pg.rect, este, norte, lon, lat


def ajustar(este, norte):
    """E = a*x + b*y + c ; N = d*x + e*y + f, usando la coordenada que cada etiqueta fija."""
    filas, obs = [], []
    for x, y, v in este:
        filas.append([x, y, 1, 0, 0, 0]); obs.append(v)
    for x, y, v in norte:
        filas.append([0, 0, 0, x, y, 1]); obs.append(v)
    A, b = np.array(filas), np.array(obs)
    coef, *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = A @ coef - b
    return coef, resid


def pdf_a_u16(coef, x, y):
    a, b, c, d, e, f = coef
    return a * x + b * y + c, d * x + e * y + f


def u16_a_pdf(coef, E, N):
    a, b, c, d, e, f = coef
    M = np.array([[a, b], [d, e]])
    return np.linalg.solve(M, np.array([E - c, N - f]))


def controles(coef, lon, lat):
    """Cada etiqueta geográfica marca dónde un meridiano o un paralelo corta el marco. Del ajuste se obtiene la
    coordenada del marco en ese punto; con pyproj, la del meridiano/paralelo; la diferencia es el error."""
    res = []
    for x, y, v in lon:                                  # meridiano: comparar el ESTE en el borde
        E, N = pdf_a_u16(coef, x, y)
        lo, la = DE_U16.transform(E, N)
        E_ver, _ = A_U16.transform(v, la)
        res.append({"etiqueta": f"{-v:.4f}°O", "pdf": [round(x, 1), round(y, 1)], "error_m": round(float(E - E_ver), 1)})
    for x, y, v in lat:                                  # paralelo: comparar el NORTE en el borde
        E, N = pdf_a_u16(coef, x, y)
        lo, la = DE_U16.transform(E, N)
        _, N_ver = A_U16.transform(lo, v)
        res.append({"etiqueta": f"{v:.4f}°N", "pdf": [round(x, 1), round(y, 1)], "error_m": round(float(N - N_ver), 1)})
    return res


def main(pdf: str, salida: str | None = None):
    sys.stdout.reconfigure(encoding="utf-8")
    rect, este, norte, lon, lat = etiquetas(pdf)
    coef, resid = ajustar(este, norte)
    escala = float(np.hypot(coef[0], coef[3]))
    print(f"etiquetas métricas: {len(este)} de este, {len(norte)} de norte; escala {escala:.4f} m/pt "
          f"(1:{escala / 0.000352778:.0f}); residuo máx. {np.abs(resid).max():.1f} m")
    # Los 5 controles preregistrados: los 3 meridianos y 2 paralelos del borde IZQUIERDO/SUPERIOR
    sup = sorted([c for c in lon if c[1] < rect.height / 2], key=lambda c: c[0])[:3]
    izq = sorted([c for c in lat if c[0] < rect.width / 2], key=lambda c: c[1])
    izq = [c for c in izq if abs(c[2] - 11.0) < 1e-6 or abs(c[2] - (10 + 57 / 60)) < 1e-6]
    ctrl = controles(coef, sup, izq)
    for c in ctrl:
        print(f"  control {c['etiqueta']:>10}: error {c['error_m']:+.1f} m")
    otros = controles(coef, [c for c in lon if c not in sup], [c for c in lat if c not in izq])
    pasa = len(ctrl) == 5 and all(abs(c["error_m"]) < UMBRAL_CONTROL_M for c in ctrl)
    print(f"criterio preregistrado (5 controles < {UMBRAL_CONTROL_M:.0f} m): {'PASA' if pasa else 'NO PASA'}; "
          f"resto de etiquetas geográficas: máx. {max(abs(c['error_m']) for c in otros):.1f} m")
    out = {"crs_u16_proj4": CRS_U16.to_proj4(), "afin_pdf_a_u16": [float(v) for v in coef],
           "escala_m_por_pt": escala, "residuo_max_m": float(np.abs(resid).max()),
           "controles_preregistrados": ctrl, "controles_adicionales": otros, "pasa": pasa}
    if salida:
        with open(salida, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
