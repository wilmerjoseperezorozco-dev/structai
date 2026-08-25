"""
CORRIGE un error real ya en produccion: los chunks NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-*
(cargados en una sesion anterior) etiquetaban como "Tabla 15" una tabla que en
realidad es la TABLA 13 del documento (verbatim, confirmado leyendo el cuerpo
real del PDF -- no el indice, que tiene su propio desfase de numeracion), y
ademas tenian los VALORES DE R MAL (R=8 en varias filas donde el documento
real dice R=7 o R=6). Ya estaba wireado al chat real (motor ecuador_nec_se_ds,
ver rag_multi_norma.py) -- una pregunta real sobre el coeficiente R de un
sistema dual en Ecuador hubiera recibido R=8 en vez de R=7, un error de
diseno sismico real y peligroso (R mas alto = fuerza de diseno mas baja =
menos conservador).

Verificado 2026-08-25 releyendo el cuerpo del PDF oficial NEC-SE-DS
(mit.gob.ec/MTOP_NEC-SE-DS.pdf, 139 paginas, mismo archivo ya usado --
confirmado mismo tamano de archivo en ambas descargas) en la seccion 6.3.4
(Ductilidad y factor de reduccion de resistencia sismica R), paginas 66-69
del documento, lineas ~2450-2560 del texto extraido. La tabla real:

  Tabla 13 -- Coeficiente de reduccion de respuesta estructural R
  (para estructuras de EDIFICACION, sistemas ductiles):
    Sistemas Duales: R=7 (3 combinaciones) y R=6 (vigas banda)
    Portico resistente a momentos: R=6 (las 3 combinaciones)
    Otros sistemas: R=5 (ya estaba correcto en el chunk viejo, es la unica
    fila que no tenia error)
    Ductilidad limitada: R=1 a 3 (mamposteria/acero conformado, ya cargado
    aparte en NECSEDS-TABLA16... espera, NO -- ver nota abajo)

Ademas se encontro que SI existe una Tabla 15 real, pero es una tabla
DISTINTA: "Factor de reduccion de respuesta R para estructuras diferentes a
las de edificacion" (seccion 9.3.7, pagina 90) -- reservorios, chimeneas,
torres, letreros, etc, R entre 2 y 3.5. Nunca se habia cargado. Se agrega
aqui tambien, como contenido nuevo (no como correccion).

NOTA sobre Tabla 16 (ductilidad limitada, R=1 a 3, viviendas <=2 pisos):
esa es una tabla DISTINTA otra vez -- confirmado en el indice real
(Tabla 16 en el indice de tablas es justamente "Poblaciones ecuatorianas...",
pero el chunk ya cargado NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA es sobre R de
ductilidad limitada, un tercer uso del numero "16" -- el documento reusa
numeros de tabla de forma inconsistente entre el cuerpo principal y los
apendices). Se revisa por separado en un chequeo futuro si hace falta --
fuera del alcance de esta correccion puntual (el foco aqui es el R de
edificacion normal, el mas usado, y el hallazgo de Tabla 15 real).

Uso: python _fix_tabla13_r_edificacion_y_tabla15_no_edificacion.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 6/9 — Coeficiente de Reducción R"

# IDs viejos a eliminar (mal etiquetados Y con valores incorrectos)
IDS_A_ELIMINAR = [
    "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-01",
    "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-02",
    "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-03",
    "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-04",
    "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES-05",
]

CHUNKS = [
    {
        "id": "NECSEDS-S6_3_4-TABLA13-R_EDIFICACION",
        "seccion": "6.3.4 (Tabla 13)",
        "titulo": (
            "Coeficiente R para sistemas estructurales dúctiles de edificación "
            "(Tabla 13, CORRIGE el chunk anterior mal etiquetado 'Tabla 15' con "
            "R=8 -- el valor real es R=7 para sistemas duales, R=6 para pórtico "
            "resistente a momentos)"
        ),
        "texto": (
            "NEC-SE-DS, Sección 6.3.4 — Ductilidad y factor de reducción de "
            "resistencia sísmica R. Tabla 13: Coeficiente de reducción de "
            "respuesta estructural R, para sistemas estructurales dúctiles de "
            "edificación (verbatim, verificado contra el cuerpo del PDF "
            "oficial, páginas 67-68):\n\n"
            "Sistemas Duales:\n"
            "  Pórticos especiales sismo resistentes de hormigón armado con "
            "vigas descolgadas, con muros estructurales de hormigón armado o "
            "con diagonales rigidizadoras (de hormigón o acero laminado en "
            "caliente): R = 7.\n"
            "  Pórticos de acero laminado en caliente con diagonales "
            "rigidizadoras (excéntricas o concéntricas) o con muros "
            "estructurales de hormigón armado: R = 7.\n"
            "  Pórticos con columnas de hormigón armado y vigas de acero "
            "laminado en caliente con diagonales rigidizadoras (excéntricas o "
            "concéntricas): R = 7.\n"
            "  Pórticos especiales sismo resistentes de hormigón armado con "
            "vigas banda, con muros estructurales de hormigón armado o con "
            "diagonales rigidizadoras: R = 6.\n\n"
            "Pórticos resistentes a momentos:\n"
            "  Pórticos especiales sismo resistentes de hormigón armado con "
            "vigas descolgadas: R = 6.\n"
            "  Pórticos especiales sismo resistentes de acero laminado en "
            "caliente o con elementos armados de placas: R = 6.\n"
            "  Pórticos con columnas de hormigón armado y vigas de acero "
            "laminado en caliente: R = 6.\n\n"
            "Otros sistemas estructurales para edificaciones:\n"
            "  Sistemas de muros estructurales dúctiles de hormigón armado: "
            "R = 5.\n"
            "  Pórticos especiales sismo resistentes de hormigón armado con "
            "vigas banda: R = 5.\n\n"
            "Debe tomarse el MENOR de los valores de R cuando el sistema "
            "resistente resulte de la combinación de varios sistemas de esta "
            "tabla. Para estructuras diferentes a las de edificación (torres, "
            "chimeneas, tanques, etc.), NO aplica esta tabla — ver Tabla 15 "
            "(Sección 9.3.7)."
        ),
    },
    {
        "id": "NECSEDS-S9_3_7-TABLA15-R_NO_EDIFICACION",
        "seccion": "9.3.7 (Tabla 15)",
        "titulo": (
            "Coeficiente R para estructuras diferentes a la edificación "
            "(Tabla 15 real: reservorios, chimeneas, torres, silos, letreros — "
            "R entre 2,0 y 3,5, nunca antes cargado)"
        ),
        "texto": (
            "NEC-SE-DS, Sección 9.3.7 — Factor de reducción de respuesta para "
            "estructuras diferentes a las de edificación. Se permite una "
            "reducción de fuerzas sísmicas de diseño mediante el factor R "
            "cuando el diseño de este tipo de estructuras provee suficiente "
            "resistencia y ductilidad, de manera consistente con la filosofía "
            "de diseño de la norma.\n\n"
            "Tabla 15 — Factor de reducción de respuesta R para estructuras "
            "diferentes a las de edificación (verbatim, página 90):\n"
            "  Reservorios y depósitos, incluidos tanques y esferas "
            "presurizadas, soportados mediante columnas o soportes "
            "arriostrados o no arriostrados: R = 2,0.\n"
            "  Silos de hormigón fundido en sitio y chimeneas que poseen "
            "paredes continuas desde la cimentación: R = 3,5.\n"
            "  Estructuras tipo cantiléver tales como chimeneas, silos y "
            "depósitos apoyados en sus bordes: R = 3,0.\n"
            "  Naves industriales con perfiles de acero: R = 3,0.\n"
            "  Torres en armadura (auto-portantes o atirantadas): R = 3,0.\n"
            "  Estructuras en forma de péndulo invertido: R = 2,0.\n"
            "  Torres de enfriamiento: R = 3,5.\n"
            "  Depósitos elevados soportados por una pila o por apoyos no "
            "arriostrados: R = 3,0.\n"
            "  Letreros y carteleras: R = 3,5.\n"
            "  Estructuras para vallas publicitarias y monumentos: R = 2,0.\n"
            "  Otras estructuras no descritas en este documento: R = 2,0."
        ),
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
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


def ejecutar(dry_run: bool = False):
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

    print(f"IDs a ELIMINAR (mal etiquetados, valores incorrectos): {len(IDS_A_ELIMINAR)}")
    for i in IDS_A_ELIMINAR:
        print(f"  DELETE {i}")
    print(f"\n{len(CHUNKS)} bloques nuevos -> {len(rows)} subchunks reales:")
    for r in rows:
        print(f"  UPSERT {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se modifica Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("ecuador_nec_se_ds_chunks").delete().in_("id", IDS_A_ELIMINAR).execute()
    print(f"OK: {len(IDS_A_ELIMINAR)} chunks viejos eliminados.")
    sb.table("ecuador_nec_se_ds_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks nuevos insertados/actualizados.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    ejecutar(dry_run=dry)
