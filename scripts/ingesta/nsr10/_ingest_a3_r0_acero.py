"""
Agrega los coeficientes sismicos R0/Omega0 para sistemas estructurales de
ACERO, extraidos de las Tablas A.3-1 (muros de carga), A.3-3 (portico
resistente a momentos) y A.3-4 (sistema dual) del Titulo A -- NO del Titulo
F como asumian los chunks obsoletos ntc_chunks ids 297/298 ("F.13"). Mismo
patron de error de etiquetado ya corregido para Titulo B (sismo atribuido
por error a B) y Titulo C (numeracion de seccion equivocada).

Fuente: NSR-10-95-105.pdf (Drive, id 1-KdJrOrUi_CTanS9XwJ7F1yDUGR83iuZ),
paginas internas A-52 a A-56 (Tablas A.3-1 a A.3-4), ya leido integramente
en esta sesion al extraer A.3.8/A.3.9 (ver NSR10-A-A_3_8_a_A_3_9).

Uso: python _ingest_a3_r0_acero.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-A-A_3_3_1_R0_acero",
    "capitulo": "NSR-10 Título A — Requisitos generales de diseño y construcción sismo resistente",
    "seccion": "A.3.3.1 (Tablas A.3-1, A.3-3, A.3-4)",
    "titulo": (
        "Coeficientes sismicos R0 y Omega0 para sistemas estructurales de ACERO (portico "
        "resistente a momentos DES/DMO/DMI, portico con diagonales concentricas/excentricas, "
        "sistema dual). CORRIGE el error de atribucion de los chunks obsoletos ntc_chunks "
        "ids 297/298 (\"F.13\"), que asumian que estos coeficientes viven en el Titulo F -- "
        "en realidad son las Tablas A.3-1/A.3-3/A.3-4 del Titulo A (aplican a TODOS los "
        "materiales estructurales, no solo acero, agrupadas por tipo de sistema sismo-"
        "resistente, no por titulo de material)."
    ),
    "texto": (
        "NSR-10 Título A — Requisitos generales de diseño sismo resistente. Capítulo A.3, "
        "Tablas A.3-1/A.3-3/A.3-4 — Coeficientes de capacidad de disipación de energía R0 "
        "y de sobre-resistencia Ω0, valores para sistemas estructurales de ACERO.\n\n"
        "IMPORTANTE: estas tablas están en el Título A (no en el Título F) porque agrupan "
        "los coeficientes sísmicos por TIPO DE SISTEMA resistente (muros de carga, "
        "combinado, pórtico, dual), aplicable a todos los materiales estructurales "
        "(concreto, acero, mampostería, madera) en una sola tabla comparativa — no existe "
        "una tabla R0 exclusiva de acero dentro del Título F. Para edificaciones "
        "irregulares, R0 debe multiplicarse por φa·φp·φr (ver A.3.3.3).\n\n"
        "De la Tabla A.3-1 (Sistema de muros de carga — cargas verticales por muros, "
        "fuerzas horizontales por muros o pórticos con diagonales):\n"
        "  Pórticos de acero estructural con diagonales concéntricas (DES): "
        "R0 = 5.0, Ω0 = 2.5. Uso permitido en las 3 zonas de amenaza sísmica "
        "(altura máx. 24 m zona alta, 30 m intermedia, sin límite zona baja).\n\n"
        "De la Tabla A.3-3 (Sistema de pórtico resistente a momentos — pórtico espacial "
        "sin diagonales que resiste TODAS las cargas verticales y horizontales):\n"
        "  Pórticos resistentes a momentos, capacidad ESPECIAL de disipación (DES), "
        "de acero: R0 = 7.0 (Nota 3: si las uniones del sistema sismo-resistente son "
        "soldadas en obra, R0 se multiplica por 0.90), Ω0 = 3.0. Uso permitido sin "
        "límite de altura en las 3 zonas.\n"
        "  Pórticos resistentes a momentos, capacidad MODERADA (DMO), de acero: "
        "R0 = 5.0 (misma Nota 3), Ω0 = 3.0. NO permitido en zona de amenaza alta; "
        "sin límite de altura en intermedia y baja.\n"
        "  Pórticos resistentes a momentos, capacidad MÍNIMA (DMI), de acero: "
        "R0 = 3.0, Ω0 = 2.5. NO permitido en zona alta ni intermedia; sin límite de "
        "altura solo en zona baja.\n"
        "  Mixtos con conexiones parcialmente restringidas a momento (pórticos de acero o "
        "mixtos, resistentes o no a momentos): R0 = 6.0, Ω0 = 3.0. No permitido en zona "
        "alta; 30 m en intermedia, 50 m en baja.\n"
        "  De acero con cerchas no dúctiles: R0 = 1.5, Ω0 = 1.5. Solo permitido en zona "
        "baja, hasta 12 m (naves industriales de un piso hasta 20 m si no son grupo de "
        "uso IV).\n"
        "  Estructuras de péndulo invertido, pórticos de acero resistentes a momento DES: "
        "R0 = 2.5 (Nota 3), Ω0 = 2.0, sin límite de altura en las 3 zonas.\n"
        "  Estructuras de péndulo invertido, pórticos de acero DMO: R0 = 1.5 (Nota 3), "
        "Ω0 = 2.0, NO permitido en zona alta.\n\n"
        "De la Tabla A.3-4 (Sistema dual — pórtico espacial resistente a momentos sin "
        "diagonales, capaz de resistir por sí solo al menos 25% del cortante sísmico en la "
        "base, combinado con muros estructurales o pórticos con diagonales que resisten en "
        "conjunto el 100%, con mínimo 75% a cargo de los muros/diagonales):\n"
        "  Pórticos de acero con diagonales excéntricas (conexiones resistentes a momento "
        "fuera del vínculo) + pórtico de acero DES: R0 = 8.0, Ω0 = 2.5, sin límite de "
        "altura en las 3 zonas.\n"
        "  Pórticos de acero con diagonales excéntricas (conexiones NO resistentes a "
        "momento fuera del vínculo) + pórtico de acero DES: R0 = 7.0, Ω0 = 2.5, sin "
        "límite de altura en las 3 zonas.\n"
        "  Pórticos de acero con diagonales excéntricas + pórtico de acero DMO: "
        "R0 = 6.0 (conexión resistente a momento) o 5.0 (no resistente), Ω0 = 2.5, sin "
        "límite de altura en las 3 zonas.\n"
        "  Pórticos de acero con diagonales concéntricas DES + pórtico de acero DES: "
        "R0 = 6.0, Ω0 = 2.5, sin límite de altura en las 3 zonas.\n"
        "  Pórticos de acero con diagonales concéntricas DMI + pórtico de acero DMO: "
        "R0 = 3.0, Ω0 = 2.5, NO permitido en zona alta.\n"
        "  Pórticos de acero con diagonales concéntricas restringidas a pandeo + pórtico "
        "de acero con alma llena DES: R0 = 7.0, Ω0 = 2.5, sin límite de altura en las "
        "3 zonas.\n\n"
        "Nomenclatura: DES = capacidad especial de disipación de energía, DMO = moderada, "
        "DMI = mínima. R0 es el coeficiente base de capacidad de disipación de energía "
        "(entre más alto, más ductilidad se asume y menor la fuerza sísmica de diseño); "
        "Ω0 es el coeficiente de sobre-resistencia (usado para elementos que deben "
        "diseñarse por capacidad, no por la fuerza sísmica reducida)."
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
