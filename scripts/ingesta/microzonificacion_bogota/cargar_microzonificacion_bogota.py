"""Carga la microzonificacion sismica LOCAL de Bogota (Decreto Distrital
523 de 2010, "Por el cual se adopta la Microzonificacion Sismica de
Bogota D.C.") -- issue #76.

Fuente PRIMARIA (no secundaria): texto oficial del decreto, descargado
en vivo 2026-09-30 de https://www.scg.org.co/wp-content/uploads/
DECRETO-523-DE-2010-MICROZONIFICACION-BOGOTA.pdf (Sociedad Colombiana
de Geotecnia, republicando el texto oficial). PDF guardado en
raw/decreto_523_2010.pdf (no se commitea, ver .gitignore).

Extraido con pdfplumber (extract_tables), y corregido a mano el ruido de
OCR real del PDF escaneado (confusiones tipograficas: I/J/O por 1/./0,
ej. 'IJ5'->1.35, ']00'->100, 'OJO'->0.30) -- la Tabla 3.1 (diseno) se
cruzo contra una fuente secundaria (nsr-10.com) que coincidio
exactamente en los 16 valores, dando confianza en el metodo de
correccion aplicado igual a las Tablas 4.1 y 5.1.

3 tablas reales del decreto, 16 zonas cada una:
- Tabla 3.1: coeficientes de DISENO (sismo 475 anios, 5% amortiguamiento,
  articulo 4, sustituye A.2.6 para el sismo de diseno normal).
- Tabla 4.1: coeficientes de SEGURIDAD LIMITADA (sismo 225 anios, 5%
  amortiguamiento, sustituye lo que A.10.3 exigiria).
- Tabla 5.1: coeficientes de UMBRAL DE DANIO (sismo 31 anios, 2%
  amortiguamiento, sustituye lo que A.12.3 exigiria) -- unica con 2
  periodos de control (T_Od, T_Cd) en vez de 1.

Parametros nacionales de referencia citados en el decreto (articulo 5,
num. 5.3): Aa=0.15g, Av=0.20g (iguales al Apendice A-4 de NSR-10 para
Bogota). Ae (seguridad limitada)=0.13g. Ad (umbral de dano)=0.06g.

Uso: python cargar_microzonificacion_bogota.py"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CIUDAD = "Bogotá, D.C."
FUENTE = (
    "Decreto Distrital 523 de 2010 (16-dic-2010), 'Por el cual se adopta la "
    "Microzonificacion Sismica de Bogota D.C.' -- texto oficial verificado "
    "en vivo 2026-09-30 (scg.org.co), Tablas 3.1/4.1/5.1. Sustituye "
    "legalmente A.2.4/A.2.6 de NSR-10 para Bogota (A.2.9.1)."
)
FECHA_DECRETO = "2010-12-16"

# Tabla 3.1 -- diseno (475 anios, 5% amortiguamiento)
TABLA_DISENO = {
    "Cerros": (1.35, 1.30, 0.62, 3.0, 0.18),
    "Piedemonte A": (1.65, 2.00, 0.78, 3.0, 0.22),
    "Piedemonte B": (1.95, 1.70, 0.56, 3.0, 0.26),
    "Piedemonte C": (1.80, 1.70, 0.60, 3.0, 0.24),
    "Lacustre-50": (1.40, 2.90, 1.33, 4.0, 0.21),
    "Lacustre-100": (1.30, 3.20, 1.58, 4.0, 0.20),
    "Lacustre-200": (1.20, 3.50, 1.87, 4.0, 0.18),
    "Lacustre-300": (1.05, 2.90, 1.77, 5.0, 0.16),
    "Lacustre-500": (0.95, 2.70, 1.82, 5.0, 0.14),
    "Lacustre Aluvial-200": (1.10, 2.80, 1.63, 4.0, 0.17),
    "Lacustre Aluvial-300": (1.00, 2.50, 1.60, 5.0, 0.15),
    "Aluvial-50": (1.35, 1.80, 0.85, 3.5, 0.20),
    "Aluvial-100": (1.20, 2.10, 1.12, 3.5, 0.18),
    "Aluvial-200": (1.05, 2.10, 1.28, 3.5, 0.16),
    "Aluvial-300": (0.95, 2.10, 1.41, 3.5, 0.14),
    "Depósito Ladera": (1.65, 1.70, 0.66, 3.0, 0.22),
}

# Tabla 4.1 -- seguridad limitada (225 anios, 5% amortiguamiento)
TABLA_SEG_LIMITADA = {
    "Cerros": (1.40, 1.50, 0.51, 3.0, 0.16),
    "Piedemonte A": (1.70, 2.35, 0.66, 3.0, 0.20),
    "Piedemonte B": (2.00, 1.95, 0.47, 3.0, 0.23),
    "Piedemonte C": (1.85, 1.95, 0.51, 3.0, 0.22),
    "Lacustre-50": (1.45, 3.40, 1.13, 4.0, 0.19),
    "Lacustre-100": (1.35, 3.70, 1.32, 4.0, 0.18),
    "Lacustre-200": (1.25, 4.00, 1.54, 4.0, 0.16),
    "Lacustre-300": (1.10, 3.40, 1.48, 5.0, 0.14),
    "Lacustre-500": (1.00, 3.10, 1.49, 5.0, 0.13),
    "Lacustre Aluvial-200": (1.15, 3.20, 1.34, 4.0, 0.15),
    "Lacustre Aluvial-300": (1.05, 2.90, 1.33, 5.0, 0.14),
    "Aluvial-50": (1.40, 2.10, 0.72, 3.5, 0.18),
    "Aluvial-100": (1.25, 2.50, 0.96, 3.5, 0.16),
    "Aluvial-200": (1.10, 2.50, 1.09, 3.5, 0.14),
    "Aluvial-300": (1.00, 2.50, 1.20, 3.5, 0.13),
    "Depósito Ladera": (1.70, 1.95, 0.55, 3.0, 0.20),
}

# Tabla 5.1 -- umbral de dano (31 anios, 2% amortiguamiento)
# (Fa, Fv, T_Od, T_Cd, T_Ld, A_Od)
TABLA_UMBRAL_DANO = {
    "Cerros": (1.50, 1.70, 0.11, 0.57, 3.0, 0.08),
    "Piedemonte A": (1.90, 2.75, 0.14, 0.72, 3.0, 0.10),
    "Piedemonte B": (2.20, 2.25, 0.10, 0.51, 3.0, 0.12),
    "Piedemonte C": (2.05, 2.25, 0.11, 0.55, 3.0, 0.11),
    "Lacustre-50": (1.55, 4.00, 0.26, 1.29, 4.0, 0.09),
    "Lacustre-100": (1.45, 4.40, 0.30, 1.52, 4.0, 0.09),
    "Lacustre-200": (1.35, 4.75, 0.35, 1.76, 4.0, 0.08),
    "Lacustre-300": (1.25, 4.00, 0.32, 1.60, 5.0, 0.08),
    "Lacustre-500": (1.10, 3.75, 0.34, 1.70, 5.0, 0.07),
    "Lacustre Aluvial-200": (1.30, 3.85, 0.30, 1.48, 4.0, 0.08),
    "Lacustre Aluvial-300": (1.20, 3.50, 0.29, 1.46, 5.0, 0.07),
    "Aluvial-50": (1.50, 2.50, 0.17, 0.83, 3.5, 0.09),
    "Aluvial-100": (1.40, 2.90, 0.21, 1.04, 3.5, 0.08),
    "Aluvial-200": (1.20, 2.90, 0.24, 1.21, 3.5, 0.07),
    "Aluvial-300": (1.10, 2.90, 0.26, 1.32, 3.5, 0.07),
    "Depósito Ladera": (1.90, 2.25, 0.12, 0.59, 3.0, 0.10),
}

DESCRIPCIONES = {
    "Cerros": "Rocas sedimentarias y depósitos de ladera con espesores <6m, formaciones de areniscas",
    "Piedemonte A": "Suelo coluvial/aluvial <50m, bloques/cantos/gravas en matriz arcillo-arenosa",
    "Piedemonte B": "Suelo coluvial/aluvial <50m, espesor >12m, bloques/cantos/gravas",
    "Piedemonte C": "Suelo coluvial/aluvial <50m",
    "Lacustre-50": "Arcillas limosas blandas 0-50m de espesor",
    "Lacustre-100": "Arcillas limosas blandas 50-100m de espesor",
    "Lacustre-200": "Arcillas limosas blandas 100-200m de espesor",
    "Lacustre-300": "Arcillas limosas blandas 200-300m de espesor",
    "Lacustre-500": "Arcillas limosas blandas 300-500m de espesor",
    "Lacustre Aluvial-200": "Arcillas lacustres con intercalaciones aluviales, 100-200m",
    "Lacustre Aluvial-300": "Arcillas lacustres con intercalaciones aluviales, 200-300m",
    "Aluvial-50": "Suelo aluvial dúctil, susceptible a licuación, 0-50m",
    "Aluvial-100": "Suelo aluvial dúctil, susceptible a licuación, 50-100m",
    "Aluvial-200": "Suelo aluvial con lentes de arenas limpias, 100-200m",
    "Aluvial-300": "Suelo aluvial con lentes de arenas limpias, 200-300m",
    "Depósito Ladera": "Depósitos de ladera con espesores >6m, composición variable",
}


def main() -> None:
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    filas = []
    for zona in TABLA_DISENO:
        fa_d, fv_d, tc_d, tl_d, a0_d = TABLA_DISENO[zona]
        fa_s, fv_s, tc_s, tl_s, a0_s = TABLA_SEG_LIMITADA[zona]
        fa_u, fv_u, t_od, t_cd, t_ld, a_od = TABLA_UMBRAL_DANO[zona]
        filas.append({
            "ciudad": CIUDAD,
            "zona": zona,
            "descripcion_zona": DESCRIPCIONES[zona],
            "fa_diseno": fa_d, "fv_diseno": fv_d, "tc_diseno_s": tc_d, "tl_diseno_s": tl_d, "a0_diseno_g": a0_d,
            "fa_seg_limitada": fa_s, "fv_seg_limitada": fv_s, "tc_seg_limitada_s": tc_s, "tl_seg_limitada_s": tl_s, "a0_seg_limitada_g": a0_s,
            "fa_umbral_dano": fa_u, "fv_umbral_dano": fv_u, "t_od_s": t_od, "t_cd_s": t_cd, "t_ld_s": t_ld, "a_od_g": a_od,
            "fuente": FUENTE,
            "fecha_decreto": FECHA_DECRETO,
        })

    sb.table("microzonificacion_sismica_local").upsert(filas, on_conflict="ciudad,zona").execute()
    print(f"OK: {len(filas)} zonas de Bogotá cargadas (Decreto 523 de 2010).")


if __name__ == "__main__":
    main()
