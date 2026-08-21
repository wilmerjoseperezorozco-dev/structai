"""
F.3.5 (NSR-10, Provisiones sismicas para acero): Porticos Resistentes a
Momento (PRM), los 3 niveles de capacidad de disipacion -- DMI, DMO, DES.
Es el sistema sismico de acero mas comun en Colombia, prioridad sobre
F.3.6-F.3.11 (arriostrados, compuestos, ensayos de conexion) dado el
tamano del capitulo completo (~80 paginas).

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
paginas internas F-234 a F-244 (F.3.5.1 a F.3.5.3, inicio).

Uso: python _ingest_titulo_f_f35_prm.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-F-F_3_5_PRM",
    "capitulo": "NSR-10 Título F — Estructuras Metálicas",
    "seccion": "F.3.5.1 a F.3.5.3",
    "titulo": (
        "Porticos Resistentes a Momento (PRM) sismo-resistentes de acero, los 3 niveles: "
        "DMI (sin requisitos especiales mas alla de F.2), DMO (deriva 0.02 rad, conexion "
        "resiste 0.8Mp), DES (deriva 0.02 rad, conexion resiste 0.8Mp, y la relacion "
        "columna-fuerte/viga-debil SumaM*pc/SumaM*pb > 1 -- la ecuacion sismica de acero "
        "mas citada en la practica). Sistema sismico de acero mas usado en Colombia."
    ),
    "texto": (
        "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.5 — Pórticos "
        "Resistentes a Momento (PRM), tres niveles de capacidad de disipación de energía.\n\n"
        "F.3.5.1 PRM-DMI (capacidad MÍNIMA): diseñados para deformaciones inelásticas "
        "mínimas. Sin requisitos especiales de análisis, sistema, ni relaciones ancho-"
        "espesor/arriostramiento adicionales a los del Capítulo F.2 — es la opción más "
        "simple. No hay zonas protegidas. Conexiones viga-columna pueden ser totalmente "
        "restringidas (TR) o parcialmente restringidas (PR). Para conexiones TR, la "
        "resistencia requerida a flexión es 1.1*Ry*Mp de la viga (ó el máximo momento "
        "transferible por el sistema); la fuerza cortante de diseño usa la carga sísmica "
        "amplificada Emh = 2*(1.1*Ry*Mp)/Lcf (ecuación F.3.5.1-1), donde Ry = relación entre "
        "fluencia esperada y mínima especificada, Mp = Fy*Z, Lcf = longitud libre de la "
        "viga. Para conexiones PR, la resistencia nominal a flexión MnPR no debe ser menor "
        "que 0.5*Mp de la viga conectada (0.5*Mp de la columna en estructuras de un nivel).\n\n"
        "F.3.5.2 PRM-DMO (capacidad MODERADA): deben desarrollar capacidad de deformación "
        "inelástica LIMITADA por fluencia en flexión de vigas/columnas y fluencia por "
        "cortante en la zona de panel. Requisitos clave de la conexión viga-columna "
        "(F.3.5.2.6.2): (1) debe acomodar un ángulo de deriva de piso de AL MENOS "
        "0.02 radianes, (2) la resistencia medida a flexión en la cara de la columna debe "
        "ser AL MENOS 0.8*Mp de la viga conectada a esa deriva. La validación de la "
        "conexión se hace mediante conexiones de ANSI/AISC 358, precalificación (F.3.11.1), "
        "o mínimo 2 ensayos cíclicos de calificación (F.3.11.2). La resistencia requerida a "
        "cortante usa Emh = 2*(1.1*Ry*Mp)/Lh (ecuación F.3.5.2-1), donde Lh = distancia "
        "entre rótulas plásticas. Las zonas de rótula plástica en los extremos de vigas son "
        "zonas protegidas (sin cambios abruptos de sección, sin perforaciones en la aleta). "
        "Empalmes de columna: si son soldados, deben ser acanalados de penetración "
        "completa; si son apernados, resistencia requerida a flexión >= Ry*Fy*Zx de la "
        "columna menor.\n\n"
        "F.3.5.3 PRM-DES (capacidad ESPECIAL): deben desarrollar capacidad de deformación "
        "inelástica SIGNIFICATIVA por fluencia en flexión de vigas y fluencia LIMITADA por "
        "cortante en la zona de panel. Salvo excepción, las columnas deben diseñarse para "
        "ser MÁS FUERTES que las vigas en fluencia completa con endurecimiento por "
        "deformación (se permite fluencia por flexión solo en la base de las columnas). "
        "Requisito central del sistema — relación columna-fuerte/viga-débil "
        "(F.3.5.3.4.1):\n"
        "  Suma(M*pc) / Suma(M*pb) > 1  (ecuación F.3.5.3-1)\n"
        "donde M*pc = suma de las proyecciones al eje de la viga de la resistencia nominal "
        "a flexión de las columnas arriba y abajo de la unión, reducida por la fuerza "
        "axial: M*pc = Suma[Zc*(Fyc - Puc/Ag)] (ecuación F.3.5.3-2), y M*pb es la suma "
        "equivalente para las vigas que llegan al nudo. Esta es la ecuación sísmica de "
        "acero MÁS citada en la práctica de ingeniería colombiana — garantiza que la "
        "estructura desarrolle un mecanismo de colapso dúctil (rótulas en vigas) en vez de "
        "un mecanismo de piso débil-columna (colapso frágil, el patrón de falla más "
        "peligroso en sismos reales). Al igual que en DMO, la conexión viga-columna debe "
        "acomodar 0.02 rad de deriva y resistir 0.8*Mp de la viga; se valida por ANSI/AISC "
        "358, precalificación, o ensayos cíclicos.\n\n"
        "Nota de aplicación: los tres niveles tienen restricciones de uso por zona de "
        "amenaza sísmica y altura definidas en las Tablas A.3-3 del Título A (ver chunk "
        "NSR10-A-A_3_3_1_R0_acero) — DMI solo permitido en zona baja, DMO no permitido en "
        "zona alta, DES sin restricción de altura en ninguna zona."
    ),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vec = model.encode([CHUNK["texto"]], normalize_embeddings=True)[0]

    row = dict(CHUNK)
    row["embedding"] = vec.tolist()
    row["titulo"] = row["titulo"][:500]

    sb.table("nsr10_chunks").upsert(row, on_conflict="id").execute()
    print(f"OK: {CHUNK['id']} cargado con embedding ({len(CHUNK['texto'])} chars).")


if __name__ == "__main__":
    main()
