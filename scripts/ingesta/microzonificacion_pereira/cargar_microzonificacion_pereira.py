"""Carga la microzonificacion sismica LOCAL de Pereira -- issue #76.

Fuente PRIMARIA: Decreto Municipal No. 932 del 19 DE OCTUBRE DE 2011 (no
2012 -- correccion real a la verificacion inicial del issue #76),
publicado en la Gaceta Metropolitana Ordinaria No. 77 del Area
Metropolitana Centro Occidente. Descargado en vivo 2026-09-30 de
https://curaduria1pereira.com/wp-content/uploads/2025/07/Decreto-932-de-2011.pdf
(Curaduria Urbana 1 de Pereira). PDF es un escaneo SIN capa de texto,
leido VISUALMENTE (paginas 3-4 de 17) via pdftoppm, no OCR automatico.

NOTA HONESTA sobre que es realmente este decreto: su titulo real es "Por
el cual se adopta la REGLAMENTACION DE TRANSICION para la solicitud y
tramite de licencias de construccion de que trata la SECCION A.2.9.5 del
Decreto 926 de 2010 -- NSR-10 para el Municipio de Pereira" -- es decir,
es un decreto de TRANSICION (mientras se completa la armonizacion formal
del estudio con la Comision Asesora Permanente, A.2.9.5), no
necesariamente la adopcion definitiva final. Aun asi, SI contiene y
adopta formalmente la Tabla 1 de coeficientes espectrales (Articulo
Segundo), basada en el estudio real "Exploracion Geotecnica,
Investigacion de Laboratorio y Zonificacion Sismica de Pereira,
Dosquebradas y Santa Rosa de Cabal" (Risaralda, 1999).

7 zonas (sin nombre descriptivo en este decreto, solo "Zona 1" a "Zona
7"). SOLO tabla de DISENO (To, Tc, TL, Aa=Av=0.25g, Fa, Fv) -- a
diferencia de Bogota/Cali, este decreto NO incluye tablas separadas de
seguridad limitada ni umbral de dano (columnas correspondientes quedan
NULL, no se inventan).

Formula identica a NSR-10 A.2.6 (confirmado en el propio decreto,
Ecuaciones 1-4): Sa=2.5*Aa*Fa*I (T0<=T<=TC), Sa=1.2*Av*Fv*I/T
(TC<T<=TL). La ecuacion 1 (T<T0) es, igual que en NSR-10 y Bogota,
exclusiva de modos superiores en analisis dinamico -- no aplica al
periodo fundamental.

Uso: python cargar_microzonificacion_pereira.py"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CIUDAD = "Pereira"
FUENTE = (
    "Decreto Municipal No. 932 del 19 de octubre de 2011, 'Por el cual se adopta "
    "la Reglamentacion de Transicion para la solicitud y tramite de licencias de "
    "construccion de que trata la Seccion A.2.9.5 del Decreto 926 de 2010 -- NSR-10 "
    "para el Municipio de Pereira' (Gaceta Metropolitana Ordinaria No. 77, "
    "octubre de 2011) -- Tabla 1, Articulo Segundo. Basado en el estudio "
    "'Exploracion Geotecnica, Investigacion de Laboratorio y Zonificacion "
    "Sismica de Pereira, Dosquebradas y Santa Rosa de Cabal' (Risaralda, 1999). "
    "NOTA: es un decreto de TRANSICION (A.2.9.5), no la armonizacion final "
    "confirmada por la Comision Asesora Permanente -- verificado en vivo "
    "2026-09-30. Solo trae tabla de diseno, no seguridad limitada ni umbral de dano."
)
FECHA_DECRETO = "2011-10-19"

# Tabla 1: (To, Tc, TL, Fa, Fv) -- Aa=Av=0.25g para las 7 zonas
TABLA1 = {
    "Zona 1": (0.08, 0.40, 3.5, 1.76, 1.47),
    "Zona 2": (0.10, 0.50, 4.0, 1.60, 1.67),
    "Zona 3": (0.17, 0.80, 5.8, 1.44, 2.40),
    "Zona 4": (0.19, 0.90, 5.8, 1.28, 2.40),
    "Zona 5": (0.07, 0.32, 2.8, 1.76, 1.17),
    "Zona 6": (0.17, 0.80, 6.4, 1.60, 2.67),
    "Zona 7": (0.15, 0.70, 6.2, 1.76, 2.57),
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
    for zona, (to, tc, tl, fa, fv) in TABLA1.items():
        filas.append({
            "ciudad": CIUDAD,
            "zona": zona,
            "descripcion_zona": (
                f"Estudio 'Zonificación Sísmica de Pereira, Dosquebradas y Santa Rosa "
                f"de Cabal' (1999). T0={to}s (rama de modos superiores, no usada en "
                f"periodo fundamental)."
            ),
            "fa_diseno": fa, "fv_diseno": fv, "tc_diseno_s": tc, "tl_diseno_s": tl, "a0_diseno_g": None,
            "fa_seg_limitada": None, "fv_seg_limitada": None, "tc_seg_limitada_s": None, "tl_seg_limitada_s": None, "a0_seg_limitada_g": None,
            "fa_umbral_dano": None, "fv_umbral_dano": None, "t_od_s": None, "t_cd_s": None, "t_ld_s": None, "a_od_g": None,
            "fuente": FUENTE,
            "fecha_decreto": FECHA_DECRETO,
        })

    sb.table("microzonificacion_sismica_local").upsert(filas, on_conflict="ciudad,zona").execute()
    print(f"OK: {len(filas)} zonas de Pereira cargadas (Decreto 932 de 2011).")
    print("Nota: Aa=Av=0.25g para las 7 zonas (constante de ciudad, no por fila).")


if __name__ == "__main__":
    main()
