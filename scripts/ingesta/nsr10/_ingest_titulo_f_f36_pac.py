"""
F.3.6 (NSR-10, Provisiones sismicas para acero): Sistemas Arriostrados
Concentricamente (PAC-DMI, PAC-DES), el segundo sistema sismico de acero
mas comun en Colombia despues de PRM. Prioridad dado el tamano del
capitulo completo (~80 paginas): PAC-DMI y PAC-DES condensados; PAE
(excentricamente arriostrados) y PAPR (pandeo restringido) quedan
pendientes para un batch futuro.

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
paginas internas F-249 a F-253.

Uso: python _ingest_titulo_f_f36_pac.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-F-F_3_6_PAC",
    "capitulo": "NSR-10 Título F — Estructuras Metálicas",
    "seccion": "F.3.6.1 a F.3.6.2",
    "titulo": (
        "Porticos Arriostrados Concentricamente (PAC) sismo-resistentes de acero, "
        "DMI y DES: segundo sistema sismico de acero mas comun en Colombia despues de "
        "PRM. Prohibicion de arriostramiento en K y de riostras solo-a-tension en DES, "
        "regla de distribucion 30%-70% entre riostras a tension/compresion, diseno por "
        "capacidad usando la resistencia ESPERADA de la riostra Ry*Fy (no la fuerza "
        "sismica de codigo) para columnas/vigas/conexiones."
    ),
    "texto": (
        "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. F.3.6 — "
        "Pórticos Arriostrados Concéntricamente (PAC), dos niveles de capacidad de "
        "disipación de energía.\n\n"
        "F.3.6.1 PAC-DMI (capacidad MÍNIMA): deben soportar deformaciones inelásticas "
        "LIMITADAS. Riostras diseñadas como miembros de ductilidad moderada (F.3.4.1.1). "
        "NO se permiten arriostramientos en K (F.3.6.1.4.2). Para configuraciones en V o "
        "V invertida: KL/r <= 4*raiz(E/Fy), las vigas deben ser continuas entre columnas, "
        "y se diseñan para las fuerzas que resultarían de riostras a tensión en fluencia "
        "esperada (Ry*Fy*Ag) combinadas con riostras a compresión reducidas a 0.3*Pn (ya "
        "pandeadas). Resistencia requerida de conexiones de riostras diagonales: el "
        "efecto de la carga sísmica amplificada, sin exceder la resistencia esperada a "
        "fluencia en tensión (Ry*Fy*Ag) ni la resistencia esperada a compresión (el menor "
        "entre Ry*Fy*Ag y 1.14*Fcre*Ag, con Fcre calculado según F.2.5 usando Ry*Fy en "
        "vez de Fy).\n\n"
        "F.3.6.2 PAC-DES (capacidad ESPECIAL, el más usado en la práctica para edificios "
        "importantes): deben soportar deformaciones inelásticas SIGNIFICATIVAS "
        "principalmente por pandeo de la riostra y fluencia de la riostra en tensión. "
        "Riostras y columnas se diseñan como miembros de ductilidad ALTA (F.3.4.1.1); "
        "vigas como ductilidad moderada.\n\n"
        "Requisito de distribución de fuerzas (F.3.6.2.4.1): a lo largo de cualquier eje "
        "de arriostramiento, para cualquier dirección de la fuerza, AL MENOS 30% pero NO "
        "MÁS de 70% de la fuerza horizontal total debe ser resistida por riostras a "
        "TENSIÓN — a menos que la resistencia nominal de cada riostra a compresión sea "
        "mayor que la resistencia requerida bajo carga sísmica amplificada. Esto evita "
        "que el sistema dependa excesivamente de riostras a tensión únicamente (que se "
        "prohíben del todo para PAC-DES, F.3.6.2.4.4) o de compresión únicamente.\n\n"
        "Arriostramientos en K: NO permitidos para PAC-DES (F.3.6.2.4.3). Riostras en V/V "
        "invertida: las vigas deben ser continuas entre columnas y cumplir requisitos de "
        "ductilidad moderada.\n\n"
        "Diseño por capacidad de columnas/vigas/conexiones (F.3.6.2.3): la carga sísmica "
        "amplificada Emh se toma como el MAYOR resultado entre dos análisis: (1) todas "
        "las riostras actuando a su resistencia ESPERADA (Ry*Fy*Ag en tensión, o el menor "
        "entre Ry*Fy*Ag y 1.14*Fcre*Ag en compresión), y (2) riostras a tensión en "
        "resistencia esperada + riostras a compresión ya pandeadas a su resistencia "
        "post-pandeo esperada (máximo 0.3 veces la resistencia esperada a compresión; "
        "para riostras con esbeltez límite 200, este valor es 15 MPa). Esta lógica de "
        "\"diseñar el resto del pórtico para que las riostras fallen primero, de forma "
        "dúctil\" es el principio central de todo diseño sismo-resistente por capacidad.\n\n"
        "Requisitos de riostras diagonales (F.3.6.2.5.2): esbeltez KL/r <= 200; área neta "
        "efectiva >= área bruta (o reforzar la sección reducida); zona protegida = el "
        "cuarto central de la longitud de la riostra más una distancia igual al peralte "
        "en cada conexión. Empalmes de columna: deben desarrollar al menos el 50% de la "
        "menor resistencia a flexión de los miembros conectados; resistencia requerida a "
        "cortante = ΣMpc/Hc (suma de resistencias plásticas nominales a flexión de "
        "columnas arriba y abajo del empalme, entre la altura libre)."
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
