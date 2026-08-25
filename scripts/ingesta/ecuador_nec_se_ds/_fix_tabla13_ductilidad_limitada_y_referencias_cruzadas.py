"""
SEGUNDA parte de la correccion del coeficiente R de Ecuador (ver
_fix_tabla13_r_edificacion_y_tabla15_no_edificacion.py para la primera).

Al releer el cuerpo completo de la Tabla 13 (paginas 67-69), se confirmo que
la porcion "Sistemas Estructurales de Ductilidad Limitada" NO es una tabla
aparte -- es la SEGUNDA MITAD de la misma Tabla 13 (la propia tabla, en su
caption real de pagina 69, dice simplemente "Tabla 13: Coeficiente de
reduccion de respuesta estructural R", sin distincion de "otra tabla" para
la parte de ductilidad limitada).

El chunk NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA-* (cargado en sesion anterior,
junto con el ya corregido de sistemas ductiles) tenia el MISMO tipo de error,
mas grave en este caso -- no solo el numero de tabla mal (16 en vez de 13):

  - "luces de hasta 5 metros" -- el documento real dice "4 metros"
  - Una fila completa INVENTADA: "Hormigon armado con secciones de dimension
    menor con armadura electrosoldada de alta resistencia -> R=2,5" -- esta
    fila NO existe en el texto real de la Tabla 13 (verificado leyendo el
    cuerpo completo, paginas 67-69, no solo el fragmento con la tabla)
  - "acero conformado en frio, aluminio, madera... R=2,5" -- el valor real
    es R=3, no R=2,5
  - Remite a "NEC-SE-HM" y "NEC-SE-VIVIENDA" -- el documento real dice
    "NEC-SE-HA" y "NEC-DR-VIVIENDA"

Tambien se corrigen las referencias cruzadas a "Tabla 15"/"Tablas 15 y 16"
en NECSEDS-S6_3_4-CRITERIOS_R-02 y -04, que deberian decir "Tabla 13" (la
misma tabla unica, ya que dúctiles + ductilidad limitada son dos secciones
de la Tabla 13, no dos tablas distintas).

Verificado 2026-08-25 releyendo el cuerpo real del PDF oficial NEC-SE-DS,
paginas 67-69, lineas ~2522-2533 del texto extraido.

Uso: python _fix_tabla13_ductilidad_limitada_y_referencias_cruzadas.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 6.3.4 — Coeficiente de Reducción R"

IDS_A_ELIMINAR = [
    "NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA-01",
    "NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA-02",
    "NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA-03",
    "NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA-04",
]

CHUNKS_NUEVOS = [
    {
        "id": "NECSEDS-S6_3_4-TABLA13-R_DUCTILIDAD_LIMITADA",
        "seccion": "6.3.4 (Tabla 13, ductilidad limitada)",
        "titulo": (
            "Coeficiente R para sistemas estructurales de ductilidad "
            "limitada -- segunda mitad de la Tabla 13, NO una tabla aparte "
            "(corrige el chunk anterior mal etiquetado 'Tabla 16' con una "
            "fila inventada y remisiones normativas equivocadas)"
        ),
        "texto": (
            "NEC-SE-DS, Tabla 13 (continuación) — Coeficiente de reducción "
            "de respuesta estructural R, Sistemas Estructurales de "
            "Ductilidad Limitada (verbatim, página 69 — es la segunda mitad "
            "de la misma Tabla 13, no una tabla numerada aparte):\n\n"
            "Pórticos resistentes a momento:\n"
            "  Hormigón armado con secciones de dimensión menor a la "
            "especificada en la NEC-SE-HA, limitados a viviendas de hasta "
            "2 pisos con luces de hasta 4 metros: R = 3.\n"
            "  Estructuras de acero conformado en frío, aluminio, madera, "
            "limitados a 2 pisos: R = 3.\n\n"
            "Muros estructurales portantes:\n"
            "  Mampostería no reforzada, limitada a un piso: R = 1.\n"
            "  Mampostería reforzada, limitada a 2 pisos: R = 3.\n"
            "  Mampostería confinada, limitada a 2 pisos: R = 3.\n"
            "  Muros de hormigón armado, limitados a 4 pisos: R = 3.\n\n"
            "El valor de R de la Tabla 13 podrá utilizarse para viviendas y "
            "edificios de baja altura diseñados con sistemas estructurales "
            "de ductilidad limitada, siempre que la estructura se diseñe de "
            "conformidad con los requerimientos de la NEC-DR-VIVIENDA. No "
            "deben utilizarse sistemas de ductilidad limitada para un "
            "número de pisos que rebase los límites de esta tabla, ni si "
            "el factor de importancia I es mayor que 1."
        ),
    },
]

# Correcciones puntuales de texto (no requieren volver a trocear porque el
# cambio es corto y no cambia el conteo de tokens de forma relevante -- se
# revalida igual contra el limite de 128 antes de subir).
CORRECCIONES_TEXTO = {
    "NECSEDS-S6_3_4-CRITERIOS_R-02": (
        "Se seleccionará uno de los dos grupos estructurales siguientes: "
        "sistemas estructurales dúctiles o sistemas estructurales de "
        "ductilidad limitada, ambos descritos en la Tabla 13 (no son dos "
        "tablas distintas, son las dos mitades de la misma tabla). Debe "
        "tomarse el menor de los valores de R para los casos en los "
        "cuales el sistema resistente estructural resulte en una "
        "combinación de varios sistemas."
    ),
    "NECSEDS-S6_3_4-CRITERIOS_R-04": (
        "No deben utilizarse sistemas estructurales de ductilidad "
        "limitada para: un número de pisos que rebasen los límites "
        "establecidos en la Tabla 13, o si el factor de importancia I es "
        "mayor que 1."
    ),
}


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

    # Chunks nuevos
    filas_planas = []
    for chunk in CHUNKS_NUEVOS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"][:500],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    # Correcciones de texto puntuales (mismo id, texto nuevo)
    for cid, texto_nuevo in CORRECCIONES_TEXTO.items():
        filas_planas.append({
            "id": cid,
            "titulo": None,  # se preserva el titulo existente, no se toca
            "seccion": None,
            "texto": texto_nuevo,
        })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    for f in filas_planas:
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
            print(f"ADVERTENCIA: {f['id']} excede 128 tokens ({n_tokens})")

    print(f"IDs a ELIMINAR (Tabla 16 vieja, con fila inventada): {len(IDS_A_ELIMINAR)}")
    for i in IDS_A_ELIMINAR:
        print(f"  DELETE {i}")
    print(f"\nChunks nuevos: {len(CHUNKS_NUEVOS)} -> {len(filas_planas) - len(CORRECCIONES_TEXTO)} subchunks")
    print(f"Correcciones de texto puntuales: {len(CORRECCIONES_TEXTO)}")
    for cid in CORRECCIONES_TEXTO:
        print(f"  UPDATE texto {cid}")

    if dry_run:
        print("[dry-run] No se modifica Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay contenido que excede el limite de tokens.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("ecuador_nec_se_ds_chunks").delete().in_("id", IDS_A_ELIMINAR).execute()
    print(f"OK: {len(IDS_A_ELIMINAR)} chunks viejos eliminados.")

    for f, emb in zip(filas_planas, embeddings):
        if f["id"] in CORRECCIONES_TEXTO:
            sb.table("ecuador_nec_se_ds_chunks").update({
                "texto": f["texto"],
                "embedding": emb,
            }).eq("id", f["id"]).execute()
        else:
            sb.table("ecuador_nec_se_ds_chunks").upsert({
                "id": f["id"],
                "capitulo": CAPITULO_LABEL,
                "titulo": f["titulo"],
                "seccion": f["seccion"],
                "texto": f["texto"],
                "embedding": emb,
            }, on_conflict="id").execute()
    print(f"OK: {len(filas_planas)} filas insertadas/actualizadas.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    ejecutar(dry_run=dry)
