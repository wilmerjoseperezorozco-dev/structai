"""Paso 3 de #332 fase 2: plano U-16 → malla de 30 m con los pisos máximos del POT de Barranquilla.

- Se renderiza el PDF a 3 px/pt (≈ 3,3 m/px) y se reparte en celdas de 30 m de la cuadrícula del U-16, ya
  georreferenciada por georef_u16.py.
- En cada celda se mide qué fracción de los píxeles tiene cada color de la leyenda (tolerancia RGB de 22).
- Las clases rayadas se reconocen por su mezcla:
  - Nivel IA: rayas naranjas sobre blanco;
  - Mejoramiento II: amarillo + rayas verdes;
  - Especial (b): marrón + rayas verdes.
- Cada celda recibe la clase dominante si cubre al menos el 30 % de los píxeles. Si no, queda sin clase (vías,
  textos, bordes, suelo sin norma de altura en este plano).

Uso (entorno geo): python -I scripts/aeronautico/clasificar_u16.py <U16.pdf> <georef_u16.json> <salida.npz>
"""
from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pymupdf

warnings.filterwarnings("ignore")

ZOOM = 3
CELDA = 30.0
TOL = 16
FRAC_MIN = 0.30

# (nombre, color RGB TAL COMO APARECE EN EL MAPA, pisos máximos o None si depende de otro plan).
# El mapa no usa exactamente el RGB de las muestras de la leyenda (leyenda → mapa, p. ej. Nivel III (229,152,0) →
# (231,165,27)). Cada color del mapa se asignó a la muestra de la leyenda más cercana con el histograma de colores del
# área urbana; ver el informe.
CLASES = [
    ("Nivel IB", (255, 237, 183), 5),
    ("Nivel II", (255, 213, 141), 11),
    ("Nivel III", (231, 165, 27), 16),
    ("Especial (a)", (177, 129, 27), None),
    ("Reactivación", (231, 93, 27), 40),
    ("Redesarrollo", (177, 27, 27), 40),
    ("Desarrollo bajo", (237, 195, 255), 8),
    ("Desarrollo medio", (201, 27, 255), 16),
    ("Desarrollo alto", (93, 27, 129), 50),
    ("Mejoramiento I", (231, 231, 27), 5),
    ("Conservación patrimonial", (27, 111, 231), 8),
]
# Nivel IA (2 pisos): rayas del MISMO naranja de Nivel III sobre blanco; se distingue por la densidad.
# Mejoramiento II y Especial (b): rayas verde brillante (~(80,190,8)) sobre el color de fondo.
BLANCO = (255, 255, 255)
NOMBRES = [c[0] for c in CLASES] + ["Nivel IA", "Mejoramiento II", "Especial (b)"]
PISOS = [c[2] for c in CLASES] + [2, 8, None]


def _mascara(img, rgb, tol=TOL):
    d = np.abs(img.astype(np.int16) - np.array(rgb, dtype=np.int16)).max(axis=-1)
    return d <= tol


def main(pdf: str, georef: str, salida: str):
    sys.stdout.reconfigure(encoding="utf-8")
    g = json.loads(open(georef, encoding="utf-8").read())
    a, b, c, d, e, f = g["afin_pdf_a_u16"]
    pg = pymupdf.open(pdf)[0]
    # Marco del mapa: entre las etiquetas de la cuadrícula (se excluye el rótulo inferior)
    marco = pymupdf.Rect(60, 45, 1925, 2555)
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), clip=marco, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
    # Coordenadas U-16 del centro de cada píxel
    xs = marco.x0 + (np.arange(pix.w) + 0.5) / ZOOM
    ys = marco.y0 + (np.arange(pix.h) + 0.5) / ZOOM
    E_min, E_max = sorted([a * marco.x0 + c, a * marco.x1 + c])
    N_min, N_max = sorted([e * marco.y0 + f, e * marco.y1 + f])
    E0 = np.floor(E_min / CELDA) * CELDA
    N1 = np.ceil(N_max / CELDA) * CELDA
    ncol = int(np.ceil((E_max - E0) / CELDA))
    nfil = int(np.ceil((N1 - N_min) / CELDA))
    # Índice de celda de cada píxel (la rotación del afín es despreciable: b, d ~ 0)
    col = ((a * xs[None, :] + b * ys[:, None] + c - E0) // CELDA).astype(np.int32)
    fil = ((N1 - (d * xs[None, :] + e * ys[:, None] + f)) // CELDA).astype(np.int32)
    idx = (fil * ncol + col).ravel()
    tot = np.bincount(idx, minlength=nfil * ncol).astype(np.float32)

    def frac(mask):
        return (np.bincount(idx, weights=mask.ravel(), minlength=nfil * ncol) / np.maximum(tot, 1)).astype(np.float32)

    fr = np.stack([frac(_mascara(img, rgb)) for _, rgb, _ in CLASES])
    i_iii = NOMBRES.index("Nivel III")
    f_nar = fr[i_iii].copy()
    im = img.astype(np.int16)
    f_ver = frac((im[..., 1] > 150) & (im[..., 0] < 140) & (im[..., 2] < 60))
    f_bla = frac(_mascara(img, BLANCO, 6))
    i_mi = NOMBRES.index("Mejoramiento I")
    i_ea = NOMBRES.index("Especial (a)")
    extra = np.zeros((3, fr.shape[1]), dtype=np.float32)
    ia = (f_nar >= 0.06) & (f_nar < 0.45) & (f_bla + f_nar >= 0.6)
    extra[0] = np.where(ia, f_nar + f_bla, 0)                                                           # Nivel IA
    fr[i_iii] = np.where(ia, 0, fr[i_iii])
    extra[1] = np.where((f_ver >= 0.05) & (fr[i_mi] >= 0.2), fr[i_mi] + f_ver, 0)                       # Mejoramiento II
    extra[2] = np.where((f_ver >= 0.05) & (fr[i_ea] >= 0.2), fr[i_ea] + f_ver, 0)                       # Especial (b)
    fr[i_mi] = np.where(extra[1] > 0, 0, fr[i_mi])
    fr[i_ea] = np.where(extra[2] > 0, 0, fr[i_ea])
    todo = np.vstack([fr, extra])
    clase = np.where(todo.max(axis=0) >= FRAC_MIN, todo.argmax(axis=0), -1).astype(np.int16)
    clase = clase.reshape(nfil, ncol)
    pisos = np.full(clase.shape, np.nan, dtype=np.float32)
    for i, p in enumerate(PISOS):
        if p is not None:
            pisos[clase == i] = p
    np.savez_compressed(salida, clase=clase, pisos=pisos, E0=E0, N1=N1, celda=CELDA,
                        nombres=np.array(NOMBRES), pisos_clase=np.array([p if p else -1 for p in PISOS]))
    print(f"malla {nfil} x {ncol} celdas de {CELDA:.0f} m; origen E0={E0:.0f}, N1={N1:.0f}")
    for i, nom in enumerate(NOMBRES):
        n = int((clase == i).sum())
        print(f"  {nom:<26} {PISOS[i] if PISOS[i] else '—':>3} pisos  {n * CELDA * CELDA / 1e4:8.1f} ha")


if __name__ == "__main__":
    main(*sys.argv[1:4])
