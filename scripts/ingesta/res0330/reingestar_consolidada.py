"""Re-ingesta de la Res. 0330/2017 consolidada (CRA) en motor_chunks. Por defecto es SIMULACIÓN: no escribe nada.

Pasos (ver README_REINGESTA_0330.md):
  1. python reingestar_consolidada.py             -> simulación: cuenta subchunks y los que exceden 128 tokens
  2. python reingestar_consolidada.py --respaldo  -> exporta las filas actuales a un JSON local (fuera del repo)
  3. python reingestar_consolidada.py --stage     -> inserta las filas nuevas con motor='aquai_stage' (invisibles al filtro motor='aquai')
  4. verificar retrieval sobre las filas stage; luego ejecutar swap_res0330.sql (transacción única)
Nada de esto se ejecuta sin aprobación explícita del usuario."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parents[2]
CHUNKS = AQUI / "res0330_consolidada.json"
NORMA_ID = "f4637666-6f95-4abc-85b8-1d64af5f52bb"      # normas_registro.codigo = 'RES-0330-2017'
NORMA_REF = "Resolución 0330 de 2017"
MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_TOKENS = 110                                       # margen bajo el límite de 128 del modelo (convención del proyecto)


def dividir(texto: str, n_tok, max_tokens: int = MAX_TOKENS) -> list[str]:
    """Empaca oraciones consecutivas hasta el límite de tokens reales; una oración que excede se parte por coma, y luego por palabras."""
    if n_tok(texto) <= max_tokens:
        return [texto]
    piezas, buffer = [], ""
    for oracion in re.split(r"(?<=[.;:])\s+", texto):
        fragmentos = re.split(r"(?<=,)\s+", oracion) if n_tok(oracion) > max_tokens else [oracion]
        for frag in fragmentos:
            if n_tok(frag) > max_tokens:                # último recurso: por palabras
                palabras, parcial = frag.split(), ""
                for w in palabras:
                    cand = f"{parcial} {w}".strip()
                    if n_tok(cand) <= max_tokens:
                        parcial = cand
                    else:
                        if buffer:
                            piezas.append(buffer)
                            buffer = ""
                        piezas.append(parcial)
                        parcial = w
                frag = parcial
            cand = f"{buffer} {frag}".strip() if buffer else frag
            if n_tok(cand) <= max_tokens:
                buffer = cand
            else:
                piezas.append(buffer)
                buffer = frag
    if buffer:
        piezas.append(buffer)
    return piezas


def construir_filas(tokenizer) -> list[dict]:
    n_tok = lambda s: len(tokenizer.encode(s))          # noqa: E731
    filas = []
    for c in json.loads(CHUNKS.read_text(encoding="utf-8"))["chunks"]:
        # El prefijo con el número de artículo se repite en cada subchunk para que ninguno pierda su referencia.
        encabezado = f"ARTÍCULO {c['seccion_origen'].split()[-1]}. {c['titulo']}."
        cuerpo = c["embedding_ready"][len(encabezado):].strip() if c["embedding_ready"].startswith(encabezado) else c["embedding_ready"]
        partes = dividir(cuerpo, lambda s: n_tok(f"{encabezado} {s}"), MAX_TOKENS)
        for i, p in enumerate(partes, 1):
            filas.append({"motor": "aquai_stage", "seccion": c["seccion_origen"] + (f" (parte {i}/{len(partes)})" if len(partes) > 1 else ""),
                          "titulo": c["titulo"], "contenido": f"{encabezado} {p}".strip(), "norma_ref": NORMA_REF, "norma_id": NORMA_ID})
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--respaldo", action="store_true")
    ap.add_argument("--stage", action="store_true")
    a = ap.parse_args()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(f"sentence-transformers/{MODELO}")
    filas = construir_filas(tok)
    excedidos = [f for f in filas if len(tok.encode(f["contenido"])) > 128]
    arts = len({f["seccion"].split(" (")[0] for f in filas})
    print(f"{arts} artículos -> {len(filas)} subchunks; exceden 128 tokens: {len(excedidos)}")
    if not (a.respaldo or a.stage):
        print("[simulación] no se escribió nada")
        return
    from dotenv import load_dotenv
    from supabase import create_client
    load_dotenv(ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    if a.respaldo:
        filas_act, ini = [], 0
        while True:
            r = sb.table("motor_chunks").select("id,motor,seccion,titulo,contenido,norma_ref,norma_id").eq("norma_id", NORMA_ID).range(ini, ini + 999).execute().data
            filas_act += r
            if len(r) < 1000:
                break
            ini += 1000
        destino = Path(os.environ.get("TEMP", ".")) / "respaldo_motor_chunks_res0330.json"
        destino.write_text(json.dumps(filas_act, ensure_ascii=False), encoding="utf-8")
        print(f"respaldo: {len(filas_act)} filas -> {destino}")
    if a.stage:
        from sentence_transformers import SentenceTransformer
        emb = SentenceTransformer(MODELO).encode([f["contenido"] for f in filas], normalize_embeddings=True, batch_size=16).tolist()
        for i in range(0, len(filas), 50):
            sb.table("motor_chunks").insert([{**f, "embedding": e} for f, e in zip(filas[i:i + 50], emb[i:i + 50])]).execute()
        print(f"stage: {len(filas)} filas insertadas con motor='aquai_stage'")


if __name__ == "__main__":
    main()
