"""Ingesta incremental del CCP-14 §10.7 (pilotes hincados), §10.8 (pozos perforados) y §10.9 (micropilotes) a
motor_chunks (#118, motor de pilotes). El corpus tenía la Sección 10 solo hasta 10.6.

A diferencia de ingest_ccp14.py, NO borra nada: solo inserta los artículos 10.7–10.9 y sus comentarios, y se niega a
correr si ya hay chunks de esos artículos (idempotencia sin borrado). Reutiliza el partidor de extract_ccp14.py
(mismas etiquetas, incluido "[Comentario]") sin importar ese módulo, que crea carpetas al importarse.

Entrada: el PDF oficial de la Sección 10 (zip de INVIAS). Se lee con PyMuPDF porque pdftotext pierde las letras
griegas de la fuente Symbol (α, β, λ…); aquí se mapean de su código privado (U+F0xx) a Unicode. El texto de la norma no
se versiona: el PDF vive en _privado/.

Dos ajustes al partidor de extract_ccp14.py, solo para esta ingesta:
  * acepta subartículos con letra (10.7.3.8.6b — Método α), que antes quedaban pegados al artículo padre;
  * el separador del encabezado debe ser una raya (— o –) o un guion entre espacios, para no tomar números de
    ecuación como "10.7.3.8.6f-8" por encabezados;
  * el filtro de tabla de contenido queda solo en la regla de "....": la regla de "≥ 3 referencias N-M" botaba
    justo los artículos con ecuaciones y tablas (10.7.3.8.5, 10.7.3.11, 10.7.3.13.1…).

Uso (con python -I):
  python ingest_ccp14_s10_pilotes.py <seccion10.pdf>            # simulación: cuenta chunks, no escribe
  python ingest_ccp14_s10_pilotes.py <seccion10.pdf> --subir    # embeddings locales + inserción en motor_chunks
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
ENV_API = Path(r"C:\Users\wilme\dev\structai\apps\api\.env")
ARTICULOS = ("10.7", "10.8", "10.9")
NORMA_REF = "CCP-14 — Norma Colombiana de Diseño de Puentes (INVIAS / AASHTO LRFD)"
NOMBRE = "Cimentaciones"


def _partidor():
    """clean_raw y split_secciones de extract_ccp14.py, con sus regex, sin ejecutar el resto del módulo."""
    ruta = AQUI / "extract_ccp14.py"
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    nodos = [n for n in arbol.body if isinstance(n, (ast.Import, ast.ImportFrom))
             or (isinstance(n, ast.FunctionDef) and n.name in ("clean_raw", "split_secciones"))
             or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("ARTICULO_RE", "COMENTARIO_RE") for t in n.targets))]
    ns: dict = {}
    exec(compile(ast.Module(nodos, []), str(ruta), "exec"), ns)  # noqa: S102  (código propio del repo)
    ns["ARTICULO_RE"], ns["COMENTARIO_RE"] = ARTICULO_RE, COMENTARIO_RE   # ajustes de esta ingesta (ver docstring)
    fuente = ast.get_source_segment(ruta.read_text(encoding="utf-8"),
                                    next(n for n in nodos if getattr(n, "name", "") == "split_secciones"))
    viejo = r" or len(re.findall(r'\d{1,2}-\d{1,3}\b', body)) >= 3"
    if viejo not in fuente:
        raise RuntimeError("El filtro de índice de extract_ccp14.split_secciones cambió: revisar este ajuste")
    exec(fuente.replace(viejo, ""), ns)  # noqa: S102
    return ns["clean_raw"], ns["split_secciones"]


# Fuente Symbol (Adobe): letra latina → griega, y algunos operadores. Código privado U+F000 + código Symbol.
_SYMBOL = dict(zip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                   "αβχδεφγηιϕκλμνοπθρστυϖωξψζΑΒΧΔΕΦΓΗΙϑΚΛΜΝΟΠΘΡΣΤΥςΩΞΨΖ"))
_SYMBOL_OPS = {0xA3: "≤", 0xB3: "≥", 0xB4: "×", 0xA2: "′", 0xB0: "°", 0xB1: "±", 0xD6: "√", 0xE5: "∑", 0xB6: "∂",
               0xBB: "≈", 0xB9: "≠", 0x2D: "−", 0xD7: "·", 0xAE: "→", 0xA5: "∞", 0xF2: "∫", 0xB8: "÷", 0x20: " "}
TABLA_SYMBOL = {0xF000 + ord(k): v for k, v in _SYMBOL.items()} | {0xF000 + k: v for k, v in _SYMBOL_OPS.items()}
TABLA_SYMBOL |= {0xF000 + c: chr(c) for c in range(0x21, 0x7F) if 0xF000 + c not in TABLA_SYMBOL}

ARTICULO_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){1,4}[a-z]?)\s*(?:-?[—–]|\s-\s)\s*(.+?)$", re.MULTILINE)
COMENTARIO_RE = re.compile(r"^(C\d{1,2}(?:\.\d{1,2}){0,4}[a-z]?)(?:\s*(?:-?[—–]|\s-\s)\s*(.+?))?$", re.MULTILINE)


def texto_pdf(ruta_pdf: Path) -> str:
    import pymupdf
    with pymupdf.open(ruta_pdf) as d:
        return "\n".join(p.get_text() for p in d).translate(TABLA_SYMBOL)


def _articulo(chunk_id: str) -> str | None:
    m = re.match(r"CCP14-S10-C?(10_\d+)", chunk_id)
    return m.group(1).replace("_", ".") if m else None


def chunks_pilotes(ruta_pdf: Path) -> list[dict]:
    clean_raw, split_secciones = _partidor()
    texto = clean_raw(texto_pdf(ruta_pdf), "10")
    return [c for c in split_secciones(texto, "10", NOMBRE) if _articulo(c["chunk_id"]) in ARTICULOS]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--subir", action="store_true")
    a = ap.parse_args()
    chunks = chunks_pilotes(a.pdf)
    from collections import Counter
    por = Counter((_articulo(c["chunk_id"]), "comentario" if "[Comentario]" in c["seccion_origen"] else "articulo")
                  for c in chunks)
    largos = sorted(len(c["embedding_ready"]) for c in chunks)
    print(f"{len(chunks)} chunks de 10.7–10.9: {dict(sorted(por.items()))}")
    if largos:
        print(f"longitud: min {largos[0]}, mediana {largos[len(largos) // 2]}, max {largos[-1]}")
    if not a.subir:
        print("Simulación: no se escribió nada (use --subir).")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")          # antes de importar: huggingface_hub lo lee al importarse
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    load_dotenv(ENV_API)
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    norma = sb.table("normas_registro").select("id").eq("codigo", "CCP-14").execute().data
    if not norma:
        raise RuntimeError("CCP-14 no existe en normas_registro")
    norma_id = norma[0]["id"]
    for art in ARTICULOS:
        ya = (sb.table("motor_chunks").select("id", count="exact").eq("norma_id", norma_id)
              .like("seccion", f"Sección 10 (%) — %{art}%").limit(1).execute())
        if ya.count:
            raise RuntimeError(f"Ya hay {ya.count} chunks de {art}: no se inserta nada (no se borra ni se duplica).")

    rows = [{"seccion": c["seccion_origen"], "titulo": c["titulo"][:500] or c["chunk_id"], "norma_ref": NORMA_REF,
             "contenido": c["embedding_ready"], "norma_id": norma_id, "motor": "vias"} for c in chunks]
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vec = modelo.encode([f"{r['titulo']}. {r['contenido']}" for r in rows], normalize_embeddings=True, batch_size=32)
    for r, v in zip(rows, vec):
        r["embedding"] = v.tolist()
    for i in range(0, len(rows), 50):
        sb.table("motor_chunks").insert(rows[i:i + 50]).execute()
        print(f"  {min(i + 50, len(rows))}/{len(rows)}")
    print(f"OK: {len(rows)} chunks insertados en motor_chunks (motor='vias').")


if __name__ == "__main__":
    main()
