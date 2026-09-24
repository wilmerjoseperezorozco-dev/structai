"""
Corrección puntual de Título B, B.6.5.12.3 (ecuación B.6.5-19,
excentricidad para estructuras flexibles) -- NSR-10. Fase 4 del plan
de cierre del Título B (2026-09-23).

El chunk `NSR10-B-B_6_5_12_3_4_r3`, cargado en la sesión de
2026-09-08, describía las variables de la ecuación B.6.5-19 pero no
transcribía la fórmula real -- el propio chunk
`NSR10-B-B_6_5_12_3_4_r15` dejaba una "NOTA DE FIDELIDAD" honesta
advirtiendo que la ecuación llegó fragmentada por el extractor OCR y
debía verificarse contra el documento fuente antes de usarse. Se
verificó hoy leyendo visualmente la página B-35 de
NSR-10-240-301.pdf (página PDF 15) -- la fórmula real:

e = [eQ + 1.7·Īz·√((gQ·Q·eQ)² + (gR·R·eR)²)] / [1 + 1.7·Īz·√((gQ·Q)² + (gR·R)²)]

Se reemplaza r3 con el texto completo (fórmula real + variables) y se
borra r15 (la nota de fidelidad queda resuelta, ya no aplica).

Uso: python _fix_titulo_b_b65_ecuacion_19.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

ID_A_BORRAR = ["NSR10-B-B_6_5_12_3_4_r3", "NSR10-B-B_6_5_12_3_4_r15"]

SECCION = "B.6.5.12.3 — Casos de carga de viento de diseño (excentricidad, ecuación B.6.5-19 verificada)"
TITULO = "NSR-10 Título B — Capítulo B.6 — Fuerzas de viento"

# 302 tokens de un solo golpe > 128 -- partido en 3 piezas reales, cada
# una verificada bajo el limite con el tokenizer real antes de subir.
PIEZAS = [
    {
        "id": "NSR10-B-B_6_5_12_3_4_ecuacion19_p1",
        "texto": (
            "B.6.5.12.3 — excentricidad e para estructuras flexibles "
            "(Ecuación B.6.5-19):\n\n"
            "e = [eQ + 1.7·Īz·√((gQ·Q·eQ)² + (gR·R·eR)²)] / "
            "[1 + 1.7·Īz·√((gQ·Q)² + (gR·R)²)]"
        ),
    },
    {
        "id": "NSR10-B-B_6_5_12_3_4_ecuacion19_p2",
        "texto": (
            "B.6.5.12.3 — Ecuación B.6.5-19, variables: eQ = "
            "excentricidad e para estructuras rígidas según la fig. "
            "B.6.5-6. eR = distancia entre el centro de cortante "
            "elástico y el centro de masa para cada piso. Īz, gQ, Q, "
            "gR y R se definen de acuerdo con la sección B.6.5.8."
        ),
    },
    {
        "id": "NSR10-B-B_6_5_12_3_4_ecuacion19_p3",
        "texto": (
            "B.6.5.12.3 — Casos de carga de viento de diseño "
            "(continuación). La excentricidad e será positiva o "
            "negativa, la que produzca el efecto de carga más "
            "severo.\n\n"
            "EXCEPCIÓN — Los edificios de un piso de altura con h "
            "menor de 9.0 m, edificios de dos pisos o menos con "
            "pórticos de construcción liviana y edificios de dos "
            "pisos o menos diseñados con diafragmas flexibles, se "
            "pueden diseñar solamente con los casos de carga 1 y 3 de "
            "la fig. B.6.5-6."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import create_client, ClientOptions

    # http2=False: durante esta sesion (2026-09-23) el cliente httpx con
    # HTTP/2 fallaba de forma consistente y reproducible en peticiones
    # POST/DELETE contra Supabase (RemoteProtocolError: "Connection
    # Terminated"), mientras que curl y HTTP/1.1 funcionaban sin
    # problema -- ver [[project_structai_titulo_b_fase1]] en memoria.
    # No es un bug de este script; se deja explicito aqui por si el
    # problema reaparece en scripts futuros.
    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    for p in PIEZAS:
        n = len(tokenizer.encode(p["texto"], add_special_tokens=True))
        print(f"  {p['id']}: {n} tokens reales")
        if n > 128:
            raise SystemExit(f"{p['id']} sobre el limite real -- no subir.")

    textos = [p["texto"] for p in PIEZAS]
    vectores = model.encode(textos, normalize_embeddings=True).tolist()

    rows = []
    for p, vec in zip(PIEZAS, vectores):
        rows.append({
            "id": p["id"],
            "capitulo": CAPITULO,
            "seccion": SECCION,
            "titulo": TITULO[:500],
            "texto": p["texto"],
            "embedding": vec,
        })

    print(f"Subiendo {len(rows)} piezas con la ecuación B.6.5-19 real...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"Borrando {ID_A_BORRAR} (version vieja incompleta + nota de fidelidad ya resuelta)...")
    sb.table("nsr10_chunks").delete().in_("id", ID_A_BORRAR).execute()

    print("OK.")


if __name__ == "__main__":
    main()
