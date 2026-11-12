"""
NSR-10 Título B, capítulo B.6 (viento): numerales con encabezado real en el
PDF y sin texto en el corpus (issue #186, Fase 1 de
scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md).

Fuente: raw/NSR-10-240-301.pdf (Drive 1ZLlTm7J__ucSvEt99qizpl3AocB12naL,
3.101.062 bytes, verificado 2026-11-11). Extracción de encabezado a encabezado
con el modo estricto de encabezado (`titulo_f=True`): con el modo normal, la
referencia "B.6.5-2" dentro de la nomenclatura se tomaba como encabezado y
cortaba B.6.3 a mitad de texto.

Vigencia, verificada antes de escribir (regla de CLAUDE.md), para estos numerales:
- Decreto 1711 de 2021: su anexo técnico (leído completo, 39 páginas) solo toca
  del Título B la Figura B.6.4-1. No modifica B.6.1.2, B.6.3 ni B.6.5.6.3.
- Decreto 340 de 2012: su anexo modifica B.4.5-1, la Figura B.6.4-1 y la
  Figura B.6.4-2. No toca estos numerales.
- Decreto 945 de 2017: PENDIENTE de verificar (no se obtuvo una copia legible).
  No ejecutar el upsert hasta cerrarlo o hasta que el dueño del proyecto lo apruebe.

Estado por numeral:
- B.6.1.2 y B.6.5.6.3: extracción limpia; solo se corrigen palabras partidas por el PDF.
- B.6.3 (nomenclatura): extracción completa (~7.000 caracteres), pero los
  subíndices salen desordenados ("fA" por A_f, "oiA" por A_oi, "pC" por C_p;
  21 símbolos). PENDIENTE de transcripción manual contra la imagen de la
  página, como en MANUAL de _ingest_titulo_c_etapa1_truncados.py. No se ingiere
  con los símbolos equivocados.

Uso:  python _ingest_titulo_b_b6_huecos_grafo.py            (dry-run: solo muestra)
      python _ingest_titulo_b_b6_huecos_grafo.py --upsert   (escribe; requiere aprobación)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _ingest_titulo_c_etapa1_truncados as base  # noqa: E402

CAPITULO = "NSR-10 Título B — Cargas"
PDF = "NSR-10-240-301.pdf"
LISTOS = {
    "B.6.1.2": "presiones_caras_opuestas",
    "B.6.5.6.3": "categorias_exposicion",
}
PENDIENTES_MANUAL = {"B.6.3": "nomenclatura: subíndices desordenados por la extracción"}
# Palabras partidas por el PDF (verificadas contra la página).
CORRECCIONES = {"categorí a": "categoría", "determ ine": "determine"}


def construir() -> list[dict]:
    chunks = []
    for numeral, slug in LISTOS.items():
        texto = base.extraer(numeral, PDF, titulo_f=True)
        for mal, bien in CORRECCIONES.items():
            texto = texto.replace(mal, bien)
        chunks.append({"id": f"NSR10-B-B_{numeral[2:].replace('.', '_')}_{slug}", "capitulo": CAPITULO,
                       "seccion": numeral, "titulo": texto.split(" — ")[1][:60] if " — " in texto else texto[:60],
                       "texto": f"NSR-10 Título B {texto}"})
    return chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upsert", action="store_true", help="escribe en nsr10_chunks (requiere aprobación)")
    args = ap.parse_args()
    chunks = construir()
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto']}\n")
    for n, motivo in PENDIENTES_MANUAL.items():
        print(f"PENDIENTE (no se ingiere): {n} — {motivo}")
    print(f"{len(chunks)} chunks listos")
    if not args.upsert:
        print("dry-run: no se escribió nada")
        return
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    load_dotenv(base.PROJECT_ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    filas = []
    for c in chunks:
        for k, p in enumerate(_sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)):
            filas.append({**c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p, "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
