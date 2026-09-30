"""Carga la microzonificacion sismica LOCAL de Santiago de Cali (Decreto
Municipal No. 411.0.20.0158 del 18 de marzo de 2014, "Por el cual se
adopta la Microzonificacion Sismica de Santiago de Cali...") -- issue
#76.

Fuente PRIMARIA: texto oficial del decreto (20 paginas), descargado en
vivo 2026-09-30 de https://www.cali.gov.co/aplicaciones/boletin_publicaciones/
imagenes_documentos/documentoId7429.pdf (Alcaldia de Santiago de Cali,
Boletin de Publicaciones Oficiales). PDF es un ESCANEO SIN capa de texto
(pdfplumber extrae 0 caracteres) -- sin tesseract/pytesseract instalados
en este entorno, se convirtio a imagenes con pdftoppm (Poppler) y se leyo
VISUALMENTE cada tabla (paginas 9/11/12/13 del PDF), no via OCR
automatico. Estudio base: INGEOMINAS & DAGMA, 2005.

10 microzonas reales (Tabla 1 del decreto): 1-Cerros, 2-Flujos y Suelo
Residual, 3-Piedemonte, 4a-Abanico Medio de Cali, 4b-Abanico Distal de
Cali y Menga, 4c-Abanico de Cañaveralejo, 4d-Abanico de Meléndez y Lili,
4e-Abanico de Pance, 5-Transición Abanicos-Llanura, 6-Llanura Aluvial.

Formula del espectro (Tabla 2, identica a NSR-10 A.2.6): Sa=2.5*Aa*Fa*I
(meseta, T<=TC), Sa=1.2*Av*Fv*I/T (TC<T<=TL), Sa=1.2*Av*Fv*TL*I/T^2
(T>TL). Aa=Av=0.25g (diseno), Ae=0.15g (seguridad limitada, Tabla 3),
Ad=0.09g/T0d=0.25s (umbral de daño, Tabla 4, ciudad completa -- NO por
zona en este decreto, a diferencia de Bogota).

HALLAZGO REAL, no simplificado: las microzonas 4b, 4c y 5 tienen una
curva de diseño/seguridad-limitada de DOS TRAMOS (fila "TC" y fila "TL"
con Fa/Fv DISTINTOS cada una en las Tablas 2 y 3) -- no es el espectro
simple de 3 ramas de las demas zonas. Se ingestan como 2 filas
separadas (ej. "4b (tramo TC)" / "4b (tramo TL)") para no perder ni
fabricar un promedio -- documentado en descripcion_zona de cada una.
La Tabla 4 (umbral de daño) SI es de una sola fila por zona incluso
para 4b/4c/5 -- esos valores solo se cargan en la fila "(tramo TC)" de
esa zona para no duplicar, con nota explicita.

Uso: python cargar_microzonificacion_cali.py"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CIUDAD = "Santiago de Cali"
FUENTE = (
    "Decreto Municipal No. 411.0.20.0158 del 18 de marzo de 2014, 'Por el cual "
    "se adopta la Microzonificacion Sismica de Santiago de Cali y se definen sus "
    "respectivas curvas y parametros de diseno estructural sismo resistente' -- "
    "texto oficial verificado en vivo 2026-09-30 (cali.gov.co, boletin de "
    "publicaciones oficiales), Tablas 1/2/3/4. Estudio base: INGEOMINAS & DAGMA, "
    "2005. Sustituye legalmente A.2.4/A.2.6 de NSR-10 para Cali (A.2.9.1)."
)
FECHA_DECRETO = "2014-03-18"

DESCRIPCIONES = {
    "1": "Cerros -- roca ígnea/sedimentaria y material intermedio volcánico/sedimentario",
    "2": "Flujos y Suelo Residual -- suelos fluvio-torrenciales/arcillosos, suelo residual de formación volcánica",
    "3": "Piedemonte -- depósitos de piedemonte 200-500m sobre abanicos aluviales",
    "4a": "Abanico Medio de Cali -- depósito 50-300m",
    "4d": "Abanico de Meléndez y Lili -- depósito 100-400m",
    "4e": "Abanico de Pance -- depósito 100-800m",
    "6": "Llanura Aluvial -- depósito 1000-1700m, llanura aluvial del río Cauca",
}
DESCRIPCIONES_COMPLEJAS = {
    "4b": "Abanico Distal de Cali y Menga -- depósito 300-900m, espectro de 2 tramos (TC y TL con Fa/Fv distintos)",
    "4c": "Abanico de Cañaveralejo -- depósito 400-700m, espectro de 2 tramos (TC y TL con Fa/Fv distintos)",
    "5": "Transición Abanicos-Llanura -- depósito 800-1000m, espectro de 2 tramos (TC y TL con Fa/Fv distintos)",
}

# Tabla 2 -- diseño (Aa=0.25, Av=0.25). Zonas simples: (TC, Fa, TL, Fv)
TABLA2_SIMPLE = {
    "1": (0.55, 0.86, 3.00, 0.99),
    "2": (0.45, 1.20, 3.00, 1.13),
    "3": (1.05, 1.36, 2.00, 2.98),
    "4a": (0.75, 1.20, 2.00, 1.88),
    "4d": (1.20, 0.99, 2.00, 2.48),
    "4e": (0.95, 0.91, 3.00, 1.81),
    "6": (1.15, 1.09, 2.50, 2.61),
}
# Zonas de 2 tramos: {"tramo_TC": (TC,Fa,TL,Fv), "tramo_TL": (TC,Fa,TL,Fv)}
TABLA2_COMPLEJA = {
    "4b": {"TC": (0.70, 1.04, 2.50, 1.52), "TL": (1.60, 0.80, 2.50, 2.67)},
    "4c": {"TC": (0.45, 1.60, 2.00, 1.50), "TL": (1.50, 1.04, 2.10, 3.25)},
    "5":  {"TC": (0.60, 1.12, 2.50, 1.40), "TL": (1.35, 0.83, 2.50, 2.34)},
}

# Tabla 3 -- seguridad limitada (Ae=0.15). Mismo formato que Tabla 2.
TABLA3_SIMPLE = {
    "1": (0.55, 0.86, 3.00, 0.99),
    "2": (0.45, 1.20, 3.00, 1.13),
    "3": (1.05, 1.36, 2.00, 2.98),
    "4a": (0.75, 1.20, 2.00, 1.88),
    "4d": (1.20, 0.99, 2.00, 2.48),
    "4e": (0.95, 0.91, 3.00, 1.81),
    "6": (1.15, 1.09, 2.50, 2.61),
}
TABLA3_COMPLEJA = {
    "4b": {"TC": (0.70, 1.04, 2.50, 1.52), "TL": (1.60, 0.80, 2.50, 2.67)},
    "4c": {"TC": (0.45, 1.60, 2.00, 1.50), "TL": (1.50, 1.04, 2.10, 3.25)},
    "5":  {"TC": (0.60, 1.12, 2.50, 1.40), "TL": (1.35, 0.83, 2.50, 2.34)},
}

# Tabla 4 -- umbral de daño (Ad=0.09 g, T0d=0.25 s, CIUDAD COMPLETA, no por zona).
# (Fv, S_barra, TCd, TLd) -- S_barra es un factor de amplificacion combinado, no Fa.
TABLA4 = {
    "1": (0.99, 1.24, 0.62, 3.00),
    "2": (1.13, 1.41, 0.70, 3.00),
    "3": (2.98, 3.72, 1.86, 2.00),
    "4a": (1.88, 2.35, 1.18, 2.00),
    "4b": (2.67, 3.34, 1.67, 2.50),
    "4c": (3.25, 4.06, 2.03, 2.10),
    "4d": (2.48, 3.10, 1.55, 2.00),
    "4e": (1.81, 2.26, 1.13, 3.00),
    "5": (2.34, 2.93, 1.46, 2.50),
    "6": (2.61, 3.26, 1.63, 2.50),
}


def _fila_base(zona_id: str, sufijo: str, descripcion: str) -> dict:
    return {
        "ciudad": CIUDAD,
        "zona": f"{zona_id} {sufijo}".strip(),
        "descripcion_zona": descripcion,
        "fuente": FUENTE,
        "fecha_decreto": FECHA_DECRETO,
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

    for zona_id, desc in DESCRIPCIONES.items():
        tc_d, fa_d, tl_d, fv_d = TABLA2_SIMPLE[zona_id]
        tc_s, fa_s, tl_s, fv_s = TABLA3_SIMPLE[zona_id]
        fv_u, s_barra, tcd, tld = TABLA4[zona_id]
        fila = _fila_base(zona_id, "", desc)
        fila.update({
            "fa_diseno": fa_d, "fv_diseno": fv_d, "tc_diseno_s": tc_d, "tl_diseno_s": tl_d, "a0_diseno_g": None,
            "fa_seg_limitada": fa_s, "fv_seg_limitada": fv_s, "tc_seg_limitada_s": tc_s, "tl_seg_limitada_s": tl_s, "a0_seg_limitada_g": None,
            "fa_umbral_dano": None, "fv_umbral_dano": fv_u, "t_od_s": None, "t_cd_s": tcd, "t_ld_s": tld, "a_od_g": None,
        })
        filas.append(fila)

    for zona_id, desc in DESCRIPCIONES_COMPLEJAS.items():
        tc2 = TABLA2_COMPLEJA[zona_id]
        tc3 = TABLA3_COMPLEJA[zona_id]
        fv_u, s_barra, tcd, tld = TABLA4[zona_id]
        for tramo in ("TC", "TL"):
            tc_d, fa_d, tl_d, fv_d = tc2[tramo]
            tc_s, fa_s, tl_s, fv_s = tc3[tramo]
            fila = _fila_base(zona_id, f"(tramo {tramo})", desc)
            fila.update({
                "fa_diseno": fa_d, "fv_diseno": fv_d, "tc_diseno_s": tc_d, "tl_diseno_s": tl_d, "a0_diseno_g": None,
                "fa_seg_limitada": fa_s, "fv_seg_limitada": fv_s, "tc_seg_limitada_s": tc_s, "tl_seg_limitada_s": tl_s, "a0_seg_limitada_g": None,
                # Tabla 4 no distingue tramos -- solo se carga en el tramo TC para no duplicar/inventar.
                "fa_umbral_dano": None,
                "fv_umbral_dano": fv_u if tramo == "TC" else None,
                "t_od_s": None,
                "t_cd_s": tcd if tramo == "TC" else None,
                "t_ld_s": tld if tramo == "TC" else None,
                "a_od_g": None,
            })
            filas.append(fila)

    sb.table("microzonificacion_sismica_local").upsert(filas, on_conflict="ciudad,zona").execute()
    print(f"OK: {len(filas)} filas de Cali cargadas (Decreto 411.0.20.0158 de 2014).")
    print("Nota: Aa=Av=0.25g (diseño), Ae=0.15g (seguridad limitada), Ad=0.09g/T0d=0.25s (umbral de daño, ciudad completa) -- no se guardan por fila, son constantes de ciudad citadas en la fuente.")


if __name__ == "__main__":
    main()
