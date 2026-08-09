"""
StructAI — Re-trocheo de chunks sobredimensionados en el RAG.

Contexto (2026-08-09): al arreglar 4 fallas de test_rag_motores_regresion.py
se encontró que un chunk de 57.650 caracteres (aquai, Artículo 253 —
Definiciones) causaba un 413 de Groq (límite 8.000 TPM) cuando se recuperaba
junto a otros 3 chunks. Se dividió manualmente. Al re-correr el suite completo
aparecieron OTRAS 4 fallas por el mismo motivo en geopot/vías/gerencia — y una
auditoría reveló ~96 chunks >5.000 caracteres repartidos en motor_chunks
(geopot/gerencia/vías) y nsr10_chunks/ntc_chunks (normativa general, incluye
el chunk de 38.301 caracteres del Título G ya documentado como pendiente en
project_construdata_limite_tokens_embeddings.md). Este script generaliza el
fix manual aplicado al chunk 617: divide cada chunk sobredimensionado en
piezas de ~2.500 caracteres cortando en el último ". " antes del límite (no
corta definiciones a la mitad salvo casos raros), calcula embedding nuevo por
pieza, inserta las piezas y borra el original — solo si la inserción fue
completa.

Uso:
  python rechunk_chunks_sobredimensionados.py --dry-run [--tabla motor_chunks|nsr10_chunks|ntc_chunks] [--umbral 5000]
  python rechunk_chunks_sobredimensionados.py [--tabla ...] [--umbral 5000]
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

sys.path.insert(0, str(ROOT / "packages" / "construdata"))

TARGET = 2500
MIN_VENTANA = 300  # no cortar si el ". " mas cercano queda a menos de esto del inicio


def dividir(contenido: str) -> list[str]:
    """Divide en piezas de ~TARGET chars, cortando en el ultimo '. ' antes del
    limite para no partir definiciones/oraciones a la mitad."""
    partes = []
    i, n = 0, len(contenido)
    while i < n:
        fin = min(i + TARGET, n)
        if fin < n:
            corte = contenido.rfind(". ", i, fin)
            corte = fin if (corte == -1 or corte < i + MIN_VENTANA) else corte + 2
        else:
            corte = fin
        partes.append(contenido[i:corte].strip())
        i = corte
    return [p for p in partes if p]


# Config por tabla: columna de contenido, columnas extra a copiar tal cual,
# y si el id es autoincremental (se omite en el insert) o hay que generarlo.
TABLAS = {
    "motor_chunks": {
        "content_col": "contenido",
        "select_cols": "id,motor,seccion,titulo,norma_ref,norma_id,contenido",
        "copy_cols": ["motor", "seccion", "titulo", "norma_ref", "norma_id"],
        "seccion_col": "seccion",
        "id_autoincrement": True,
    },
    "nsr10_chunks": {
        "content_col": "texto",
        "select_cols": "id,capitulo,seccion,titulo,norma_id,texto",
        "copy_cols": ["capitulo", "seccion", "titulo", "norma_id"],
        "seccion_col": "seccion",
        "id_autoincrement": False,  # id es text, hay que generarlo
    },
    "ntc_chunks": {
        "content_col": "contenido",
        "select_cols": "id,norma,seccion,titulo,norma_id,contenido",
        "copy_cols": ["norma", "seccion", "titulo", "norma_id"],
        "seccion_col": "seccion",
        "id_autoincrement": True,
    },
}


def _fetch_todas(sb, tabla: str, select_cols: str) -> list[dict]:
    """Supabase REST limita a 1000 filas por default -- motor_chunks tiene
    3.697, hay que paginar o se pierden filas silenciosamente."""
    filas = []
    PAGE = 1000
    inicio = 0
    while True:
        r = sb.table(tabla).select(select_cols).range(inicio, inicio + PAGE - 1).execute()
        filas.extend(r.data)
        if len(r.data) < PAGE:
            break
        inicio += PAGE
    return filas


def procesar_tabla(sb, embed_query, tabla: str, umbral: int, dry_run: bool) -> dict:
    cfg = TABLAS[tabla]
    content_col = cfg["content_col"]
    todas = _fetch_todas(sb, tabla, cfg["select_cols"])
    oversized = [row for row in todas if len(row[content_col] or "") > umbral]
    oversized.sort(key=lambda row: -len(row[content_col]))

    resumen = {"tabla": tabla, "candidatos": len(oversized), "procesados": 0, "sub_chunks_creados": 0, "detalle": []}

    for row in oversized:
        contenido = row[content_col]
        partes = dividir(contenido)
        resumen["detalle"].append((row["id"], len(contenido), len(partes)))

        if dry_run:
            continue

        nuevas_filas = []
        for idx, texto in enumerate(partes):
            emb = embed_query(texto)
            nueva = {c: row[c] for c in cfg["copy_cols"]}
            nueva[cfg["seccion_col"]] = f"{row[cfg['seccion_col']]} (parte {idx+1}/{len(partes)})"
            nueva[content_col] = texto
            nueva["embedding"] = emb
            if not cfg["id_autoincrement"]:
                nueva["id"] = f"{row['id']}-P{idx+1}"
            nuevas_filas.append(nueva)

        resp = sb.table(tabla).insert(nuevas_filas).execute()
        if len(resp.data) == len(partes):
            sb.table(tabla).delete().eq("id", row["id"]).execute()
            resumen["procesados"] += 1
            resumen["sub_chunks_creados"] += len(partes)
        else:
            print(f"  ADVERTENCIA: {tabla} id={row['id']} — insercion incompleta "
                  f"({len(resp.data)}/{len(partes)}), NO se borra el original.")

    return resumen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tabla", choices=list(TABLAS.keys()), default=None)
    ap.add_argument("--umbral", type=int, default=5000)
    args = ap.parse_args()

    from supabase import create_client
    from rag_multi_norma import embed_query

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    tablas = [args.tabla] if args.tabla else list(TABLAS.keys())

    print(f"=== Re-trocheo de chunks > {args.umbral} caracteres ({'DRY RUN' if args.dry_run else 'EJECUCION REAL'}) ===\n")
    total_procesados = 0
    total_sub_chunks = 0
    for tabla in tablas:
        print(f"--- {tabla} ---")
        resumen = procesar_tabla(sb, embed_query, tabla, args.umbral, args.dry_run)
        for chunk_id, largo, n_partes in resumen["detalle"]:
            print(f"  id={chunk_id} | {largo:6d} chars -> {n_partes} sub-chunks")
        if args.dry_run:
            print(f"  Candidatos: {resumen['candidatos']}")
        else:
            print(f"  Procesados: {resumen['procesados']}/{resumen['candidatos']}, sub-chunks creados: {resumen['sub_chunks_creados']}")
        total_procesados += resumen["procesados"]
        total_sub_chunks += resumen["sub_chunks_creados"]
        print()

    if not args.dry_run:
        print(f"TOTAL: {total_procesados} chunks originales reemplazados por {total_sub_chunks} sub-chunks.")


if __name__ == "__main__":
    main()
