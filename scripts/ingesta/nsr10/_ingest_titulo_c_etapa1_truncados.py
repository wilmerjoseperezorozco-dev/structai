"""
NSR-10 Título C — Etapa 1 de la ingesta (auditoría 2026-11-08): numerales cuyo chunk en `nsr10_chunks` está
truncado respecto al PDF fuente (ver docs/AUDITORIA_NSR10_PAGINAS_2026-11.md y docs/ANALISIS_MOTORES_Y_ROADMAP_2026-11.md).

Cada numeral se extrae del PDF fuente (scripts/ingesta/nsr10/raw/, gitignored) desde su encabezado hasta el siguiente
encabezado, se limpia (pies de página, líneas de puntos) y se re-trocea por el límite real de tokens. El `id` es el del
chunk existente, así el upsert lo REEMPLAZA (convención del proyecto: on_conflict="id").

Las ecuaciones que pypdf entrega desordenadas NO se transcriben: el chunk dice explícitamente que la ecuación está en la
fuente. Nada se inventa ni se reconstruye de memoria.

Uso:
    python _ingest_titulo_c_etapa1_truncados.py --dry-run     # solo imprime
    python _ingest_titulo_c_etapa1_truncados.py               # upsert
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

CAPITULO = "NSR-10 Título C — Concreto Estructural"
RAW = HERE / "raw"

# numeral -> (PDF fuente, id de chunk existente)
OBJETIVOS = {
    "C.10.10.4.1": "NSR-10-377-387.pdf",
    "C.21.3.3": "NSR-10-477-501.pdf",
    "C.21.3.5.6": "NSR-10-477-501.pdf",
}

HEADING = re.compile(r"^\s*([A-K]\.\d{1,3}(?:\.\d{1,3}){0,6})\s*[—–\-]\s*\S")
PIE = re.compile(r"^\s*(NSR-10\s*[–—-].*|[A-K]-\d{1,4})\s*$")
ECUACION = re.compile(r"\(C\.\d+-\d+\)")


def extraer(numeral: str, pdf: str) -> str:
    import pypdf

    lector = pypdf.PdfReader(str(RAW / pdf))
    lineas = "\n".join((p.extract_text() or "") for p in lector.pages).splitlines()
    ini = next((i for i, l in enumerate(lineas) if (m := HEADING.match(l)) and m.group(1) == numeral), None)
    if ini is None:
        raise SystemExit(f"{numeral}: encabezado no encontrado en {pdf}")
    fin = next((j for j in range(ini + 1, len(lineas)) if HEADING.match(lineas[j])), len(lineas))
    limpias = []
    for l in lineas[ini:fin]:
        if PIE.match(l) or not l.strip():
            continue
        limpias.append(re.sub(r"\.{4,}", " — ", l.strip()))
    texto = re.sub(r"\s+", " ", " ".join(limpias)).strip()
    if ECUACION.search(texto):
        texto += " [Nota de fidelidad: las ecuaciones de este numeral no se transcriben (la extracción de texto las desordena); consultar la fuente.]"
    return texto


# Texto transcrito leyendo la página del PDF (imagen), porque la extracción desordena las ecuaciones.
# Las ecuaciones se escriben en notación lineal; «I» es el momento de inercia (la fuente imprime una «l»).
MANUAL = {
    "C.10.10.4.1": (
        "C.10.10.4.1 — Se permite usar las siguientes propiedades para los elementos en la estructura: "
        "(a) Módulo de elasticidad: Ec de C.8.5.1. "
        "(b) Momentos de inercia, I. Elementos en compresión: Columnas 0.70 Ig; Muros – no agrietados 0.70 Ig; Muros – agrietados 0.35 Ig. "
        "Elementos a flexión: Vigas 0.35 Ig; Placas planas y losas planas 0.25 Ig. "
        "(c) Área: 1.0 Ag. "
        "Como alternativa, se permite que los momentos de inercia de los elementos sometidos a compresión y a flexión, I, se calculen como sigue. "
        "Elementos en compresión: I = (0.80 + 25 Ast/Ag) (1 − Mu/(Pu h) − 0.5 Pu/Po) Ig ≤ 0.875 Ig (C.10-8), "
        "donde Pu y Mu debe provenir de la combinación de carga particular en consideración, o la combinación de Pu y Mu que resulta del menor valor de I. "
        "No hay necesidad de usar un valor de I menor de 0.35 Ig. "
        "Elementos a flexión: I = (0.10 + 25 ρ) (1.2 − 0.2 bw/d) Ig ≤ 0.5 Ig (C.10-9). "
        "Para elementos continuos sometidos a flexión, se permite que I sea el promedio de los valores obtenidos de la ecuación (C.10-9) para secciones críticas de momento positivo y negativo. "
        "No hay necesidad de usar un valor de I menor de 0.25 Ig. "
        "Las dimensiones de la sección transversal de cada elemento usadas en el análisis no deben apartarse más del 10 por ciento de las dimensiones mostradas en los planos de construcción, de lo contrario debe repetirse el análisis."
    ),
}

EXTRA = [
    {
        "id": "NSR10-C-C_9_5_tabla_a_espesores_minimos",
        "seccion": "Tabla C.9.5(a)",
        "titulo": "Alturas o espesores mínimos de vigas no preesforzadas o losas reforzadas en una dirección a menos que se calculen las deflexiones",
        "texto": (
            "NSR-10 Título C, Capítulo C.9 — TABLA C.9.5(a) — Alturas o espesores mínimos de vigas no preesforzadas o losas reforzadas en una dirección "
            "a menos que se calculen las deflexiones. Espesor mínimo, h, para elementos que NO soporten o estén ligados a divisiones u otro tipo de elementos "
            "susceptibles de dañarse debido a deflexiones grandes (A = luz libre del elemento). "
            "Losas macizas en una dirección: simplemente apoyadas A/20; con un extremo continuo A/24; con ambos extremos continuos A/28; en voladizo A/10. "
            "Vigas o losas nervadas en una dirección: simplemente apoyadas A/16; con un extremo continuo A/18.5; con ambos extremos continuos A/21; en voladizo A/8. "
            "NOTAS: Los valores dados en esta tabla se deben usar directamente en elementos de concreto de peso normal y refuerzo grado 420 MPa. "
            "Para otras condiciones, los valores deben modificarse como sigue: "
            "(a) Para concreto liviano estructural con densidad wc dentro del rango de 1 440 a 1 840 kg/m3, los valores de la tabla deben multiplicarse por (1.65 − 0.0003 wc), pero no menos de 1.09. "
            "(b) Para fy distinto de 420 MPa, los valores de esta tabla deben multiplicarse por (0.4 + fy/700)."
        ),
    },
]


def construir() -> list[dict]:
    chunks = []
    for numeral, pdf in OBJETIVOS.items():
        texto = MANUAL.get(numeral) or extraer(numeral, pdf)
        chunks.append({
            "id": f"NSR10-C-{numeral.replace('.', '_')}",
            "capitulo": CAPITULO,
            "seccion": numeral,
            "titulo": texto[:60],
            "texto": f"NSR-10 Título C {texto}",
        })
    chunks += [{"capitulo": CAPITULO, **e} for e in EXTRA]
    return chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    chunks = construir()
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto']}\n")
    if args.dry_run:
        return
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    filas = []
    for c in chunks:
        piezas = _sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)
        for k, p in enumerate(piezas):
            filas.append({**c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p,
                          "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
