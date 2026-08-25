"""
Completa las Tablas A.3-1 a A.3-4 del Titulo A de la NSR-10 (coeficientes
R0/Omega0 por sistema estructural) para los materiales que _ingest_a3_r0_acero.py
NO cubrio: concreto, manposteria y madera. El chunk NSR10-A3-A_3_nota_de_cobertura
marcaba estas 4 tablas como "PENDIENTE" (no capturadas verbatim); el script de
acero cerro solo la porcion de acero. Este script cierra el resto.

Fuente: PDF oficial NSR-10 Titulo A, Decreto Final 2010-01-13
(https://www.scg.org.co/Titulo-A-NSR-10-Decreto%20Final-2010-01-13.pdf),
paginas internas A-52 a A-58 (Tablas A.3-1 a A.3-4), extraido y verificado
verbatim contra el PDF real el 2026-08-25 (motivado por el hallazgo del R0
maximo real de Colombia = 8.0, para el documento comparativo Colombia/Peru/
Ecuador -- ver project_structai_replicabilidad_paises.md).

No incluye las Tablas A.3-5 (mezcla de sistemas en altura), A.3-6
(irregularidad en planta) ni A.3-7 (irregularidad en altura) -- esas no son
tablas de R0 y quedan fuera del alcance de este cierre puntual.

Uso: python _ingest_a3_r0_concreto_mamposteria_madera.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NSR-10 Título A — Requisitos generales de diseño sismo resistente"

CHUNKS = [
    {
        "id": "NSR10-A3-A_3_1-R0_TABLA_MUROS_CARGA",
        "seccion": "A.3.3.1 (Tabla A.3-1)",
        "titulo": (
            "Coeficientes R0/Ω0, Tabla A.3-1 — Sistema de Muros de Carga (concreto, "
            "mampostería, madera): R0 desde 1,0 (mampostería no reforzada) hasta 5,0 "
            "(muros de concreto DES)"
        ),
        "texto": (
            "NSR-10 Título A, Tabla A.3-1 — Sistema estructural de muros de carga "
            "(sistema sin pórtico completo: cargas verticales por muros de carga, "
            "fuerzas horizontales por muros estructurales o pórticos con diagonales). "
            "Coeficientes R0 (capacidad de disipación de energía) y Ω0 "
            "(sobre-resistencia) para materiales distintos de acero:\n\n"
            "Paneles de cortante de madera (muros ligeros de madera laminada): "
            "R0 = 3,0, Ω0 = 2,5. Permitido en las 3 zonas de amenaza sísmica "
            "(6 m zona alta, 9 m intermedia, 12 m baja).\n\n"
            "Muros estructurales:\n"
            "  Muros de concreto DES (capacidad especial): R0 = 5,0, Ω0 = 2,5. "
            "Permitido: 50 m zona alta, sin límite intermedia y baja.\n"
            "  Muros de concreto DMO (capacidad moderada): R0 = 4,0, Ω0 = 2,5. "
            "NO permitido en zona alta; 50 m intermedia; sin límite baja.\n"
            "  Muros de concreto DMI (capacidad mínima): R0 = 2,5, Ω0 = 2,5. "
            "NO permitido en zona alta ni intermedia; 50 m en zona baja.\n"
            "  Muros de mampostería reforzada de bloque de perforación vertical "
            "DES, con todas las celdas rellenas: R0 = 3,5, Ω0 = 2,5. Permitido: "
            "50 m zona alta, sin límite intermedia y baja.\n"
            "  Muros de mampostería reforzada DMO: R0 = 2,5, Ω0 = 2,5. Permitido: "
            "30 m zona alta, 50 m intermedia, sin límite baja.\n"
            "  Muros de mampostería parcialmente reforzada de bloque de "
            "perforación vertical: R0 = 2,0, Ω0 = 2,5. Zona alta solo Grupo de "
            "uso I, 2 pisos; 12 m intermedia; 18 m baja.\n"
            "  Muros de mampostería confinada: R0 = 2,0, Ω0 = 2,5. Grupo de uso I "
            "en las 3 zonas: 2 pisos zona alta, 12 m intermedia, 18 m baja.\n"
            "  Muros de mampostería de cavidad reforzada: R0 = 4,0, Ω0 = 2,5. "
            "Permitido: 45 m zona alta, 60 m intermedia, sin límite baja.\n"
            "  Muros de mampostería NO reforzada (sin capacidad de disipación de "
            "energía): R0 = 1,0, Ω0 = 2,5 — el valor MÍNIMO de toda la Tabla A.3-1. "
            "NO permitido en zona alta ni intermedia; en zona baja solo Grupo de "
            "uso I, 2 pisos (Nota 3: solo donde Aa ≤ 0,05).\n\n"
            "Pórticos con diagonales (las diagonales llevan carga vertical):\n"
            "  Pórticos con diagonales de concreto DMO: R0 = 3,5, Ω0 = 2,5. NO "
            "permitido zona alta; 30 m intermedia y baja.\n"
            "  Pórticos de madera con diagonales: R0 = 2,0, Ω0 = 2,5. Permitido: "
            "12 m zona alta, 15 m intermedia, 18 m baja.\n\n"
            "Nota 3: la mampostería no reforzada solo se permite en zonas de "
            "amenaza sísmica baja donde Aa ≤ 0,05, para edificaciones del grupo "
            "de uso I, de uno y dos pisos. Para sistemas de acero de esta misma "
            "tabla (pórticos con diagonales concéntricas DES, R0 = 5,0), ver el "
            "chunk NSR10-A-A_3_3_1_R0_acero."
        ),
    },
    {
        "id": "NSR10-A3-A_3_2-R0_TABLA_SISTEMA_COMBINADO",
        "seccion": "A.3.3.1 (Tabla A.3-2)",
        "titulo": (
            "Coeficientes R0/Ω0, Tabla A.3-2 — Sistema Estructural Combinado "
            "(concreto, mampostería, muros mixtos con acero): R0 desde 2,0 hasta 7,0"
        ),
        "texto": (
            "NSR-10 Título A, Tabla A.3-2 — Sistema estructural combinado: (a) "
            "cargas verticales por pórtico NO resistente a momentos + fuerzas "
            "horizontales por muros o pórticos con diagonales, o (b) cargas "
            "verticales y horizontales por pórtico resistente a momentos combinado "
            "con muros o diagonales, sin cumplir los requisitos de sistema dual.\n\n"
            "Muros estructurales combinados con pórticos de concreto:\n"
            "  Muros de concreto DES + pórticos de concreto DES: R0 = 7,0, "
            "Ω0 = 2,5. NO permitido zona alta; 72 m intermedia; sin límite baja.\n"
            "  Muros de concreto DMO + pórticos de concreto DMO: R0 = 5,0, "
            "Ω0 = 2,5. NO permitido zona alta; 72 m intermedia; sin límite baja.\n"
            "  Muros de concreto DMO + pórticos losa-columna DMO: R0 = 3,5, "
            "Ω0 = 2,5. NO permitido zona alta; 18 m intermedia; 27 m baja.\n"
            "  Muros de concreto DMI + pórticos de concreto DMI: R0 = 2,5, "
            "Ω0 = 2,5. NO permitido zona alta ni intermedia; 72 m baja.\n"
            "  Muros de concreto DMI + pórticos losa-columna DMI: R0 = 2,0, "
            "Ω0 = 2,5. NO permitido zona alta ni intermedia; 18 m baja.\n\n"
            "Muros de mampostería combinados con pórticos de concreto:\n"
            "  Muros de mampostería reforzada DES (celdas rellenas) + pórticos de "
            "concreto DES: R0 = 4,5, Ω0 = 2,5. Permitido: 30 m alta, 45 m "
            "intermedia, 45 m baja.\n"
            "  Muros de mampostería reforzada DMO + pórticos de concreto DES: "
            "R0 = 3,5, Ω0 = 2,5. Permitido: 30/45/45 m.\n"
            "  Muros de mampostería reforzada DMO + pórticos de concreto DMO: "
            "R0 = 2,5, Ω0 = 2,5. NO permitido zona alta; 30 m intermedia, 45 m baja.\n"
            "  Muros de mampostería confinada DMO + pórticos de concreto DMO: "
            "R0 = 2,0, Ω0 = 2,5. NO permitido zona alta; Grupo I 18 m intermedia, "
            "Grupo I 21 m baja.\n"
            "  Muros de mampostería confinada DMO + pórticos de concreto DMI: "
            "R0 = 2,0, Ω0 = 2,5. NO permitido zona alta ni intermedia; Grupo I "
            "18 m baja.\n"
            "  Muros de mampostería de cavidad reforzada DES + pórticos de "
            "concreto DMO: R0 = 4,0, Ω0 = 2,5. NO permitido zona alta; 30 m "
            "intermedia, 45 m baja.\n"
            "  Muros de mampostería de cavidad reforzada DES + pórticos de "
            "concreto DMI: R0 = 2,0, Ω0 = 2,5. NO permitido zona alta ni "
            "intermedia; 45 m baja.\n\n"
            "Muros mixtos (concreto reforzado con elementos de acero) + pórticos "
            "de acero — el valor más alto de esta tabla:\n"
            "  Muros de concreto reforzado DES mixtos con acero + pórticos de "
            "acero (resistentes o no a momentos): R0 = 6,0, Ω0 = 2,5. Permitido: "
            "50 m alta, sin límite intermedia y baja.\n"
            "  Muros de concreto reforzado DMO mixtos con acero + pórticos de "
            "acero: R0 = 5,5, Ω0 = 2,5. NO permitido alta ni intermedia; sin "
            "límite baja.\n"
            "  Muros de concreto reforzado DMI mixtos con acero + pórticos de "
            "acero: R0 = 5,0, Ω0 = 2,5. NO permitido alta ni intermedia; 45 m baja.\n\n"
            "Pórticos con diagonales concéntricas (concreto y mixtos):\n"
            "  Pórticos de concreto con diagonales concéntricas DMO + pórticos de "
            "concreto DMO: R0 = 3,5, Ω0 = 2,5. NO permitido zona alta; 24 m "
            "intermedia, 30 m baja.\n\n"
            "Nota 1: sistema combinado — no cumple los requisitos de sistema dual "
            "(ver Tabla A.3-4) porque el pórtico resistente a momentos no está "
            "diseñado para resistir por sí solo al menos el 25% del cortante "
            "sísmico en la base. Los sistemas de acero puro y muros de cortante "
            "con placa de acero de esta misma tabla están en "
            "NSR10-A-A_3_3_1_R0_acero."
        ),
    },
    {
        "id": "NSR10-A3-A_3_3-R0_TABLA_PORTICO_MOMENTOS",
        "seccion": "A.3.3.1 (Tabla A.3-3)",
        "titulo": (
            "Coeficientes R0/Ω0, Tabla A.3-3 — Sistema de Pórtico Resistente a "
            "Momentos (concreto): R0 desde 1,5 hasta 7,0 (concreto DES)"
        ),
        "texto": (
            "NSR-10 Título A, Tabla A.3-3 — Sistema de pórtico resistente a "
            "momentos: pórtico espacial esencialmente completo, sin diagonales, "
            "que resiste TODAS las cargas verticales y horizontales. Valores para "
            "concreto (el acero de esta tabla está en NSR10-A-A_3_3_1_R0_acero):\n\n"
            "Capacidad especial de disipación (DES):\n"
            "  Pórticos de concreto DES: R0 = 7,0, Ω0 = 3,0. Permitido sin límite "
            "de altura en las 3 zonas de amenaza sísmica.\n\n"
            "Capacidad moderada de disipación (DMO):\n"
            "  Pórticos de concreto DMO: R0 = 5,0, Ω0 = 3,0. NO permitido zona "
            "alta; sin límite intermedia y baja.\n\n"
            "Capacidad mínima de disipación (DMI):\n"
            "  Pórticos de concreto DMI: R0 = 2,5, Ω0 = 3,0. NO permitido zona "
            "alta ni intermedia; sin límite baja.\n\n"
            "Pórticos losa-columna (incluye reticular celulado):\n"
            "  De concreto DMO: R0 = 2,5, Ω0 = 3,0. NO permitido zona alta; "
            "15 m intermedia, 21 m baja.\n"
            "  De concreto DMI: R0 = 1,5, Ω0 = 3,0 — el valor MÍNIMO de toda la "
            "Tabla A.3-3. NO permitido zona alta ni intermedia; 15 m baja.\n\n"
            "Estructuras de péndulo invertido:\n"
            "  Pórticos de concreto DES: R0 = 2,5, Ω0 = 2,0. Permitido sin límite "
            "de altura en las 3 zonas.\n\n"
            "Nota 1: el sistema de pórtico resiste por sí solo el 100% de las "
            "cargas verticales y horizontales, a diferencia del sistema dual "
            "(Tabla A.3-4), donde el pórtico comparte la resistencia horizontal "
            "con muros o diagonales."
        ),
    },
    {
        "id": "NSR10-A3-A_3_4-R0_TABLA_SISTEMA_DUAL",
        "seccion": "A.3.3.1 (Tabla A.3-4)",
        "titulo": (
            "Coeficientes R0/Ω0, Tabla A.3-4 — Sistema Dual (concreto, "
            "mampostería, mixtos): R0 = 8,0, el MÁXIMO de toda la NSR-10, en "
            "muros de concreto DES + pórticos DES"
        ),
        "texto": (
            "NSR-10 Título A, Tabla A.3-4 — Sistema estructural dual: pórtico "
            "espacial resistente a momentos, sin diagonales, capaz de resistir por "
            "sí solo mínimo 25% del cortante sísmico en la base, combinado con "
            "muros estructurales o pórticos con diagonales que en conjunto "
            "resisten el 100% (mínimo 75% a cargo de los muros/diagonales). "
            "Valores para concreto y mampostería (el acero puro de esta tabla — "
            "pórticos con diagonales excéntricas/concéntricas de acero — está en "
            "NSR10-A-A_3_3_1_R0_acero):\n\n"
            "EL VALOR MÁXIMO DE TODA LA NSR-10 — R0 = 8,0:\n"
            "  Muros de concreto DES + pórticos de concreto DES: R0 = 8,0, "
            "Ω0 = 2,5. Permitido sin límite de altura en las 3 zonas.\n\n"
            "Muros de mampostería reforzada combinados con pórticos de concreto:\n"
            "  Muros de mampostería reforzada de bloque de perforación vertical "
            "DES (celdas rellenas) + pórticos de concreto DES: R0 = 5,5, "
            "Ω0 = 3,0. Permitido 45 m en las 3 zonas.\n"
            "  Muros de mampostería reforzada DMO + pórticos de concreto DES: "
            "R0 = 4,5, Ω0 = 2,5. Permitido 35 m en las 3 zonas.\n"
            "  Muros de mampostería reforzada DMO + pórticos de concreto DMO: "
            "R0 = 3,5, Ω0 = 2,5. NO permitido zona alta; 30 m intermedia y baja.\n\n"
            "Muros de concreto reforzado mixtos con acero + pórticos de acero:\n"
            "  Muros de concreto DES mixtos con acero + pórticos de acero con "
            "alma llena DES: R0 = 6,0, Ω0 = 2,5. Sin límite de altura en las 3 "
            "zonas.\n"
            "  Muros de concreto DMI mixtos con acero + pórticos de acero DES: "
            "R0 = 5,0, Ω0 = 2,5. NO permitido zona alta ni intermedia; sin "
            "límite baja.\n"
            "  Muros de concreto DMI mixtos con acero + pórticos de acero DMO: "
            "R0 = 4,0, Ω0 = 3,0. NO permitido zona alta ni intermedia; sin "
            "límite baja.\n\n"
            "Pórticos de concreto con diagonales concéntricas:\n"
            "  De concreto DMO + pórticos de concreto DMO: R0 = 4,0, Ω0 = 2,5. "
            "NO permitido zona alta; 24 m intermedia, 30 m baja.\n\n"
            "Nota 1: para clasificar como sistema dual, el pórtico resistente a "
            "momentos (que puede ser DES en concreto/acero, DMO en concreto, o "
            "DMI en acero) debe diseñarse para resistir como mínimo el 25% del "
            "cortante sísmico en la base, actuando independientemente; los muros "
            "o diagonales deben resistir como mínimo el 75%. Nota 2: para "
            "edificaciones irregulares, R0 se multiplica por φa·φp·φr (A.3.3.3). "
            "Nota 3: Ω0 puede reducirse 0,5 en diafragma flexible, mínimo 2,0."
        ),
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/peru_e030/ y
# ecuador_nec_se_ds/: el tokenizer real (no una aproximación por caracteres)
# es lo único confiable para el límite de 128 tokens del modelo.
MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si solo
    excede el limite se divide por oracion, y si aun asi excede, por coma."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"][:500],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens (se truncarian en la busqueda): {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en nsr10_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
