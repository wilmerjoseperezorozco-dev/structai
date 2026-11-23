"""Actualiza SOLO los dos chunks de pavimentos del motor de vías en motor_chunks (#106).

Por qué no se usa `ingest_motor_chunks.py`: su `main()` borra TODOS los chunks con motor='vias' (incluidos los manuales
INVIAS y las INV E 2012) y reinserta solo los escritos a mano. Este script hace un UPDATE puntual por (motor, seccion),
con el texto y el embedding nuevos, y no toca nada más.

Uso:
    python scripts/ingesta/motores/actualizar_chunks_pavimento_106.py            # simulación: muestra qué cambiaría
    python scripts/ingesta/motores/actualizar_chunks_pavimento_106.py --aplicar  # escribe (requiere aprobación previa)

Necesita SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno. Se esperan exactamente 2 filas (hoy ids 42 y 43); si la
consulta devuelve otro número, aborta sin escribir.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_motor_chunks import VIAS_CHUNKS  # noqa: E402

SECCIONES = (
    "AASHTO 93 adaptado — Diseño de pavimento asfáltico (estructura flexible)",
    "AASHTO 93 adaptado — Diseño de pavimento de concreto (estructura rígida)",
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="escribir en Supabase (sin esto, solo simula)")
    args = ap.parse_args()

    nuevos = {c["seccion"]: c for c in VIAS_CHUNKS if c["seccion"] in SECCIONES}
    assert set(nuevos) == set(SECCIONES), "faltan secciones en VIAS_CHUNKS"
    assert all("0.39" not in c["contenido"] for c in nuevos.values()), "el chunk no debe enseñar la conversión retirada"

    from supabase import create_client
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    filas = (sb.table("motor_chunks").select("id, seccion, titulo").eq("motor", "vias")
             .in_("seccion", list(SECCIONES)).execute().data)
    if len(filas) != 2:
        print(f"Se esperaban 2 filas y hay {len(filas)}: no se escribe nada.")
        return 1

    for f in filas:
        print(f"id={f['id']}: «{f['titulo']}» → «{nuevos[f['seccion']]['titulo']}»")
    if not args.aplicar:
        print("Simulación: no se escribió nada. Use --aplicar con aprobación.")
        return 0

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")   # el mismo modelo de ingest_motor_chunks.py
    for f in filas:
        c = nuevos[f["seccion"]]
        emb = model.encode([f"{c['titulo']}. {c['contenido']}"], normalize_embeddings=True)[0].tolist()
        sb.table("motor_chunks").update({"titulo": c["titulo"], "contenido": c["contenido"],
                                         "norma_ref": c["norma_ref"], "embedding": emb}).eq("id", f["id"]).execute()
        print(f"id={f['id']} actualizado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
