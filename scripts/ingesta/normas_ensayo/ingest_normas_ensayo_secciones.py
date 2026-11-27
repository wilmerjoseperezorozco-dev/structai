"""
Carga las Secciones de Normas de Ensayo (INVIAS 2012, adoptadas por Res. 1375 de 2014) a
motor_chunks (motor='vias'), generando embeddings locales.

Uso:
  python scripts/ingesta/normas_ensayo/ingest_normas_ensayo_secciones.py                 # simulación: cuenta chunks
  python ... --escribir                                                                   # secciones nuevas de #295
  python ... --escribir --secciones seccion_200 seccion_300                               # recargar otras

Orden seguro: inserta las filas nuevas y SOLO después borra las previas de esa norma (por id),
para no dejar un hueco de normativa si algo falla a mitad de camino.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
VIAS_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "vias"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "normativa_general"))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

SECCIONES = {
    "seccion_200": ("SECCION-200-ENSAYO-2012", "Normas de Ensayo — Sección 200 (Agregados Pétreos)"),
    "seccion_300": ("SECCION-300-ENSAYO-2012", "Normas de Ensayo — Sección 300 (Cemento)"),
    "seccion_100": ("SECCION-100-ENSAYO-2012", "Normas de Ensayo — Sección 100 (Suelos)"),
    "seccion_400": ("SECCION-400-ENSAYO-2012", "Normas de Ensayo — Sección 400 (Concreto hidráulico)"),
    "seccion_600": ("SECCION-600-ENSAYO-2012", "Normas de Ensayo — Sección 600 (Estabilización de suelos)"),
    "seccion_700_800_a": ("SECCION-700-800-ENSAYO-2012", "Normas de Ensayo — Secciones 700 y 800 (Mezclas asfálticas y pavimentos)"),
    "seccion_700_800_b": ("SECCION-700-800-ENSAYO-2012", "Normas de Ensayo — Secciones 700 y 800 (Mezclas asfálticas y pavimentos)"),
}


NUEVAS_295 = ["seccion_100", "seccion_400", "seccion_600", "seccion_700_800_a", "seccion_700_800_b"]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--escribir", action="store_true")
    ap.add_argument("--secciones", nargs="+", default=NUEVAS_295, choices=list(SECCIONES))
    a = ap.parse_args()
    elegidas = {k: SECCIONES[k] for k in a.secciones}

    if not a.escribir:
        for doc_code in elegidas:
            path = VIAS_DIR / f"{doc_code}.txt"
            n = len(extract_chunks(_clean(path.read_text(encoding="utf-8")))) if path.exists() else None
            print(f"  {doc_code}: {n if n is not None else 'FALTA ' + path.name} chunks")
        print("[simulación] no se escribió nada")
        return

    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_ids = {}
    for doc_code, (codigo, _) in elegidas.items():
        row = sb.table("normas_registro").select("id").eq("codigo", codigo).execute()
        if not row.data:
            raise RuntimeError(f"{codigo} no existe en normas_registro — registrarlo primero")
        norma_ids[doc_code] = row.data[0]["id"]

    all_rows = []
    for doc_code, (codigo, norma_label) in elegidas.items():
        path = VIAS_DIR / f"{doc_code}.txt"
        if not path.exists():
            print(f"  ADVERTENCIA: {path.name} no existe, se omite")
            continue
        cleaned = _clean(path.read_text(encoding="utf-8"))
        chunks = extract_chunks(cleaned)
        print(f"  {doc_code}.txt: {len(chunks)} chunks")
        for c in chunks:
            all_rows.append({
                "seccion": c["seccion_origen"] or c["chunk_id"],
                "titulo": c["titulo"][:500] or c["chunk_id"],
                "norma_ref": norma_label,
                "contenido": c["embedding_ready"],
                "norma_id": norma_ids[doc_code],
                "motor": "vias",
            })

    print(f"\nTotal chunks Secciones de Normas de Ensayo: {len(all_rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row_, vec in zip(all_rows, vectores):
        row_["embedding"] = vec.tolist()

    if not all_rows:
        raise SystemExit("no hay chunks que subir; no se toca nada")
    previos = []
    for norma_id in set(norma_ids.values()):
        ini = 0
        while True:
            r = sb.table("motor_chunks").select("id").eq("norma_id", norma_id).range(ini, ini + 999).execute().data
            previos += [x["id"] for x in r]
            ini += 1000
            if len(r) < 1000:
                break

    print("Subiendo a motor_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")

    print(f"Borrando {len(previos)} chunks previos de esas normas (ya reemplazados)...")
    for i in range(0, len(previos), 200):
        sb.table("motor_chunks").delete().in_("id", previos[i:i + 200]).execute()
    print(f"OK: {len(all_rows)} chunks de Secciones de Normas de Ensayo cargados en motor_chunks (motor='vias')")


if __name__ == "__main__":
    main()
