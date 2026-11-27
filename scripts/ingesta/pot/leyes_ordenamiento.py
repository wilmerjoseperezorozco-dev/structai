"""
Ley 388 de 1997 (ordenamiento territorial) y Ley 1523 de 2012 (gestión del riesgo de desastres) -> motor_chunks
(motor='geopot'), parte de #295 (dominio ordenamiento delgado).

Fuente: textos compilados del Gestor Normativo EVA de la Función Pública (texto oficial con modificaciones y
notas de vigencia incorporadas). NO usar las compilaciones de editoriales con «derechos reservados».

Dos pasos, separados porque los PDF descargados son datos no confiables:
  1) python -I scripts/ingesta/pot/leyes_ordenamiento.py extraer C:/Users/wilme/dev/descargas/normas_pot
     -> packages/construdata/normativa_raw/pot/leyes/<codigo>.json   (solo texto; no abre red ni base)
  2) python scripts/ingesta/pot/leyes_ordenamiento.py cargar [--escribir]
     -> simulación por defecto; con --escribir inserta y SOLO después borra las filas previas de esa norma.

Cada artículo se parte en piezas de <=150 palabras (~200 tokens); cada pieza repite «Ley N de AAAA, Artículo X».
Los artículos cuyo texto dice que fueron derogados no se cargan como contenido vigente.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "pot" / "leyes"
MAX_PALABRAS = 150

LEYES = {
    "LEY-388-1997": {"patron_pdf": r"388", "titulo": "Ley 388 de 1997", "etiqueta": "Ley 388 de 1997 (ordenamiento territorial)"},
    "LEY-1523-2012": {"patron_pdf": r"1523", "titulo": "Ley 1523 de 2012", "etiqueta": "Ley 1523 de 2012 (gestión del riesgo de desastres)"},
}

# «ARTÍCULO 1.-», «ARTÍCULO 12°.», «Artículo 1°.», «ARTÍCULO 15A.» al inicio de línea
_ART = re.compile(r"^\s*ART[ÍI]CULO\s+(\d+[A-Z]?)\s*(?:°|o\.|º)?\s*[.\-–]+", re.I | re.M)
# encabezado/pie de cada página del PDF de Función Pública
_RUIDO = re.compile(r"^\s*(?:Departamento Administrativo de la Función Pública|EVA - Gestor Normativo|"
                    r"Ley \d+ de \d{4}\s*\d*\s*(?:EVA - Gestor Normativo)?)\s*$", re.I | re.M)
_DEROGADO = re.compile(r"^\W*(?:art[íi]culo\s+)?derogad[oa]\b", re.I)


def _partir(texto: str) -> list[str]:
    p = texto.split()
    return [" ".join(p[i:i + MAX_PALABRAS]) for i in range(0, len(p), MAX_PALABRAS)] or [""]


def extraer_ley(texto: str, codigo: str) -> tuple[list[dict], list[str]]:
    meta = LEYES[codigo]
    texto = _RUIDO.sub("", texto)
    ms = list(_ART.finditer(texto))
    chunks, derogados, vistos = [], [], set()
    for i, m in enumerate(ms):
        num = m.group(1).upper()
        if num in vistos:  # una cita «artículo 5.-» dentro de una nota no abre otro artículo
            continue
        vistos.add(num)
        fin = ms[i + 1].start() if i + 1 < len(ms) else len(texto)
        cuerpo = re.sub(r"-\n(?=[a-záéíóúñ])", "", texto[m.end():fin])
        cuerpo = re.sub(r"\s+", " ", cuerpo).strip()
        if len(cuerpo) < 20:
            continue
        if _DEROGADO.match(cuerpo):
            derogados.append(num)
            continue
        partes = _partir(cuerpo)
        for k, parte in enumerate(partes, 1):
            et = f" (parte {k}/{len(partes)})" if len(partes) > 1 else ""
            chunks.append({"seccion": f"Artículo {num}{et}", "titulo": f"{meta['titulo']}, Artículo {num}",
                           "contenido": f"{meta['titulo']}, Artículo {num}{et}. {parte}"})
    return chunks, derogados


def cmd_extraer(origen: Path) -> None:
    import pymupdf
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for codigo, meta in LEYES.items():
        pdfs = [p for p in origen.glob("*.pdf") if re.search(meta["patron_pdf"], p.name)]
        if len(pdfs) != 1:
            raise SystemExit(f"{codigo}: se esperaba 1 PDF en {origen}, hay {len(pdfs)}")
        with pymupdf.open(pdfs[0]) as d:
            texto = "\n".join(p.get_text() for p in d)
        if "Función Pública" not in texto[:600]:
            raise SystemExit(f"{pdfs[0].name}: no es la compilación del Gestor Normativo de la Función Pública")
        chunks, derogados = extraer_ley(texto, codigo)
        arts = len({c["titulo"] for c in chunks})
        (OUT_DIR / f"{codigo}.json").write_text(json.dumps({"codigo": codigo, "fuente": "Gestor Normativo EVA, Función Pública",
                                                             "derogados_omitidos": derogados, "chunks": chunks},
                                                            ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"  {codigo}: {arts} artículos -> {len(chunks)} chunks; derogados omitidos: {derogados or 'ninguno'}")


def cmd_cargar(escribir: bool) -> None:
    import os
    datos = {c: json.loads((OUT_DIR / f"{c}.json").read_text(encoding="utf-8")) for c in LEYES}
    for c, d in datos.items():
        print(f"  {c}: {len(d['chunks'])} chunks")
    if not escribir:
        print("[simulación] no se escribió nada")
        return
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    for codigo, d in datos.items():
        r = sb.table("normas_registro").select("id").eq("codigo", codigo).execute().data
        if not r:
            raise SystemExit(f"{codigo} no está en normas_registro: aplicar la migración primero")
        nid = r[0]["id"]
        previos = [x["id"] for x in sb.table("motor_chunks").select("id").eq("norma_id", nid).execute().data]
        filas = [{"motor": "geopot", "norma_id": nid, "norma_ref": LEYES[codigo]["etiqueta"], **c} for c in d["chunks"]]
        emb = modelo.encode([f["contenido"] for f in filas], normalize_embeddings=True, batch_size=32).tolist()
        for i in range(0, len(filas), 50):
            sb.table("motor_chunks").insert([{**f, "embedding": e} for f, e in zip(filas[i:i + 50], emb[i:i + 50])]).execute()
        for i in range(0, len(previos), 200):
            sb.table("motor_chunks").delete().in_("id", previos[i:i + 200]).execute()
        print(f"  {codigo}: {len(filas)} insertados, {len(previos)} previos borrados")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) >= 3 and sys.argv[1] == "extraer":
        cmd_extraer(Path(sys.argv[2]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "cargar":
        cmd_cargar("--escribir" in sys.argv)
    else:
        raise SystemExit(__doc__)
