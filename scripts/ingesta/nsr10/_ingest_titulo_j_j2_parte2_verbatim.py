"""
Título J — re-ingesta verbatim, Capítulo J.2 (parte 2 de 2, CIERRA J.2):
J.2.5.2.5 a J.2.5.4.4, incluida Tabla J.2.5-4 completa.

Fuente: NSR-10-1501-1570.pdf, páginas J-8 a J-9 (páginas reales 37-38).
Extraído visualmente por el mismo bloqueo de codificación del PDF.

Estos numerales nunca tuvieron chunk previo (huecos reales, no reemplazo).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título J — Requisitos de Protección Contra Incendios en Edificaciones"

CHUNKS = [
    {
        "id": "NSR10-J-Tabla_J_2_5_4", "seccion": "J.2.5.2 (Tabla J.2.5-4)",
        "titulo": "Tabla J.2.5-4 — Clasificación requerida de índice de propagación de llama por Grupo de Ocupación y ubicación del acabado",
        "texto": (
            "Tabla J.2.5-4 — Clasificación requerida del índice de propagación de llama para acabados interiores de "
            "acuerdo con el grupo de ocupación de cada edificación. Columnas: Medios de Salida Normales, Corredores, "
            "Espacios con áreas < 170 m², Espacios con áreas > 170 m². "
            "Almacenamiento (A-1): 1, 1, 2, 3. Almacenamiento (A-2): 1, 1, 2, 3. "
            "Comercial (C-1): 1, 1, 3, 3. Comercial (C-2): 1, 1, 2, 3. "
            "Especial (E): 1, 1, 2, 2. "
            "Fabril e industrial (F-1): 1, 2, 2, 2. Fabril e industrial (F-2): 1, 2, 2, 3. "
            "Institucional (I-1): 1, 1, 2, 2. Institucional (I-2): 1, 1, 2, 2. Institucional (I-3): 1, 1, 2, 3. "
            "Institucional (I-4): 1, 2, 2, 3. Institucional (I-5): 1, 2, 3, 3. "
            "Lugares de reunión (L): 1, 2, 2, 2. "
            "Mixto y otros (M): 1, 1, 2, 3. "
            "Alta peligrosidad (P): 1, 1, 2, 2. "
            "Residencial (R-1): 2, 2, 4, 4. Residencial (R-2): 1, 2, 2, 2. Residencial (R-3): 1, 1, 2, 2. "
            "Temporal (T): 1, 2, 3, 3."
        ),
    },
    {
        "id": "NSR10-J-J_2_5_2_5", "seccion": "J.2.5.2.5",
        "titulo": "J.2.5.2.5 — Materiales Clase 3: usables solo en pisos, revestimientos delgados sobre incombustible, o <=20% de paredes/cielo",
        "texto": "J.2.5.2.5 — Los materiales de acabado inscritos en la Clase 3 pueden usarse sólo en alguna de las siguientes condiciones: (a) Para recubrimientos y acabados para pisos. (b) Para recubrimientos de pared con espesores menores que 0.1 cm, cuando se apliquen directamente a un material incombustible. (c) Para recubrimientos de no más del 20% del área total de paredes y cielo raso en espacios que requieran materiales de las clases 1 o 2.",
    },
    {
        "id": "NSR10-J-J_2_5_2_6", "seccion": "J.2.5.2.6",
        "titulo": "J.2.5.2.6 — Con rociadores automáticos, la clase de acabado puede subir a la inmediatamente superior de Tabla J.2.5-3",
        "texto": "J.2.5.2.6 — En espacios donde existan sistemas de rociadores automáticos, la clase respectiva de acabado interior, puede reemplazarse por la clase inmediatamente superior indicada en la tabla J.2.5-3.",
    },
    {
        "id": "NSR10-J-J_2_5_2_7", "seccion": "J.2.5.2.7",
        "titulo": "J.2.5.2.7 — Muros de cerramiento de escaleras/ascensores/buitrones/ductos de basura sin interrupción desde cimiento hasta techo",
        "texto": "J.2.5.2.7 — Los muros de cerramiento de escaleras y ascensores, buitrones, ductos para basuras y corredores de evacuación, deben ser diseñados y construidos sin interrupción desde el cimiento hasta el techo de la estructura. Estos muros deberán cumplir con las especificaciones para muros cortafuegos contenidas en J.2.5.1.1. Las aberturas en los muros a que hace referencia este artículo deberán tener puertas con una resistencia al fuego no inferior a una hora. Estas puertas deberán, en condiciones normales, permanecer cerradas.",
    },
    {
        "id": "NSR10-J-J_2_5_2_8", "seccion": "J.2.5.2.8",
        "titulo": "J.2.5.2.8 — Fachadas construidas con materiales incombustibles (ladrillo, concreto, bloques, yeso, fibrocemento, vidrio, metales)",
        "texto": "J.2.5.2.8 — Las fachadas deben ser construidas con materiales incombustibles como ladrillo, concreto, bloques de concreto, yeso, fibrocemento, vidrio y metales.",
    },
    {
        "id": "NSR10-J-J_2_5_3_1", "seccion": "J.2.5.3.1",
        "titulo": "J.2.5.3.1 — Cielos rasos: soportes, colgantes, rejillas y aditamentos con materiales incombustibles",
        "texto": "J.2.5.3 — CIELOS RASOS — Los cielos rasos utilizados como elementos de acabados, deben cumplir con las siguientes especificaciones: J.2.5.3.1 — Los soportes, colgantes, rejillas y demás aditamentos utilizados para mantener en posición un sistema de cielos rasos, deben construirse con materiales incombustibles.",
    },
    {
        "id": "NSR10-J-J_2_5_3_2", "seccion": "J.2.5.3.2",
        "titulo": "J.2.5.3.2 — Se admite el uso de cielos rasos luminosos construidos con vidrio y metal",
        "texto": "J.2.5.3.2 — En cualquier edificación se admite el uso de cielos rasos luminosos, construidos con vidrio y metal.",
    },
    {
        "id": "NSR10-J-J_2_5_3_3", "seccion": "J.2.5.3.3",
        "titulo": "J.2.5.3.3 — Cielos rasos luminosos incombustibles bajo rociadores: construirse con malla o elemento con aberturas para no impedir el paso del agua",
        "texto": "J.2.5.3.3 — Los cielos rasos luminosos de material incombustible, instalados por debajo de un sistema de rociadores automáticos, deben construirse e instalarse utilizando malla o cualquier otro tipo de elemento con aberturas, en tal forma que no se impida el paso del agua de los rociadores.",
    },
    {
        "id": "NSR10-J-J_2_5_3_4", "seccion": "J.2.5.3.4",
        "titulo": "J.2.5.3.4 — Prohibido cielo raso luminoso de material combustible en salidas/corredores y en I-1/I-2",
        "texto": "J.2.5.3.4 — Se prohíbe el uso de cielos rasos luminosos de material combustible, en: (a) Cualquier salida o corredor. (b) Cualquier habitación de los Subgrupos de Ocupación Institucional de Reclusión (I-1) e Institucional de Salud o Incapacidad (I-2).",
    },
    {
        "id": "NSR10-J-J_2_5_3_5", "seccion": "J.2.5.3.5",
        "titulo": "J.2.5.3.5 — Cielorrasos acústicos/decorativos deben cumplir Tabla J.2.5-4 según el uso del recinto",
        "texto": "J.2.5.3.5 — Los cielorrasos acústicos u otros cielorrasos decorativos deben tener acabados que cumplan con las especificaciones de la tabla J.2.5-4, de acuerdo con el uso del recinto donde se instalará el cielorraso.",
    },
    {
        "id": "NSR10-J-J_2_5_4_1", "seccion": "J.2.5.4.1",
        "titulo": "J.2.5.4.1 — Salas de máquinas/calderas separadas del resto de la edificación mediante muros cortafuego (J.2.5.1.1)",
        "texto": "J.2.5.4 — REQUISITOS PARA SALAS DE MAQUINAS Y CALDERAS — Las salas de máquinas o calderas deben cumplir los requisitos siguientes: J.2.5.4.1 — Todas las salas de máquinas o calderas deben estar separadas del resto de la edificación mediante muros cortafuego que cumplan con las especificaciones consignadas en J.2.5.1.1.",
    },
    {
        "id": "NSR10-J-J_2_5_4_2", "seccion": "J.2.5.4.2",
        "titulo": "J.2.5.4.2 — Superficies combustibles adyacentes a salas de máquinas/calderas: recubrir para no exceder 75°C",
        "texto": "J.2.5.4.2 — Las superficies combustibles adyacentes de salas de máquinas y calderas deben recubrirse adecuadamente con materiales resistentes al fuego, de tal manera que la temperatura sobre una superficie combustible y adyacente no exceda nunca los 75 °C.",
    },
    {
        "id": "NSR10-J-J_2_5_4_3", "seccion": "J.2.5.4.3",
        "titulo": "J.2.5.4.3 — Equipos de calentamiento/combustión: no localizarse cerca de salidas, ascensores u otros equipos si hay riesgo",
        "texto": "J.2.5.4.3 — Los equipos de calentamiento y combustión no deben localizarse cerca de salidas, recintos para ascensores o en la vecindad de otros equipos y materiales, si se teme que esta proximidad contribuya a crear situaciones de riesgo.",
    },
    {
        "id": "NSR10-J-J_2_5_4_4", "seccion": "J.2.5.4.4",
        "titulo": "J.2.5.4.4 — Equipos de calentamiento/combustión deben montarse sobre bases incombustibles",
        "texto": "J.2.5.4.4 — Todos los equipos de calentamiento o combustión que se instalen deben montarse sobre bases incombustibles.",
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas. J.2 queda COMPLETO (55 numerales).")


if __name__ == "__main__":
    main()
