"""
Ingesta verbatim de NSR-10 Título F.5.6.4.4 a F.5.6.6 (Diseño Estático de
Uniones -- Estructuras de Aluminio): aplastamiento (.4.4), cortante y
tensión combinados (.4.5), pernos de alta resistencia que trabajan por
fricción (F.5.6.5, completa) y uniones con pasadores (F.5.6.6, completa).
Fase 7 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-524 a F-526), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Uso: python _ingest_titulo_f_f5644_a_f566_verbatim.py
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

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_6_4_4", "seccion": "F.5.6.4.4",
        "titulo": "F.5.6.4.4 — Aplastamiento: menor entre BRF de sujetador (ec. F.5.6.4-3) y BRP de la capa conectada (ec. F.5.6.4-4/5), coeficiente c según df/t",
        "texto": (
            "F.5.6.4.4 — Aplastamiento — La resistencia efectiva de diseño al aplastamiento para un único remache "
            "o perno es igual al menor valor entre la resistencia de diseño al aplastamiento de un solo sujetador "
            "BRF y la capacidad por aplastamiento de la capa conectada BRP. "
            "La resistencia de diseño al aplastamiento, BRF, para un sujetador único se toma como: "
            "BRF = φ df t 2 pf  (F.5.6.4-3). Donde: df = diámetro nominal del sujetador. t = espesor de la capa "
            "conectada. pf = se define en F.5.6.4.1 para sujetadores de acero y aluminio. φ = coeficiente de "
            "reducción de capacidad (véase la tabla F.5.3.3-1). "
            "La capacidad por aplastamiento de la capa conectada está dada por el menor valor de los siguientes: "
            "BRP = φ c df t pa  (F.5.6.4-4). BRP = φ e t pa  (F.5.6.4-5). "
            "Donde: e = distancia desde el centro de un agujero hasta el borde adyacente en la dirección del "
            "aplastamiento del sujetador. c = 2 cuando df/t < 10; c = 20t/df cuando 10 < df/t < 13; c = 1.5 cuando "
            "df/t > 13. pa = el menor valor entre 0.5(f0.2 + fu) y 1.2 f0.2 para el material de la capa conectada "
            "(véanse las tablas F.5.4.2-1 y F.5.4.2-2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_4_5", "seccion": "F.5.6.4.5",
        "titulo": "F.5.6.4.5 — Cortante y tensión combinados: (P/PRT)² + (V/VRS)² ≤ 1 (ecuación F.5.6.4-6)",
        "texto": (
            "F.5.6.4.5 — Cortante y tensión combinados — Cuando los pernos o remaches (excepto remaches de "
            "aluminio, véase F.5.6.4.3) están sujetos a cortante y tensión, se debe satisfacer la siguiente "
            "condición (adicionalmente a F.5.6.4.2 y F.5.6.4.3): "
            "(P/PRT)² + (V/VRS)² ≤ 1  (F.5.6.4-6). "
            "Donde: P = carga axial de tensión generada bajo carga mayorada. V = carga cortante generada bajo "
            "carga mayorada. PRT = resistencia de diseño a tensión axial. VRS = resistencia de diseño a cortante."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_5_intro", "seccion": "F.5.6.5",
        "titulo": "F.5.6.5 — Pernos de alta resistencia que trabajan por fricción: solo grado general precargado, umbral 23 kgf/mm², efectos de relajamiento térmico en aluminio",
        "texto": (
            "F.5.6.5 — PERNOS DE ALTA RESISTENCIA QUE TRABAJAN POR FRICCION — En estructuras de aluminio, sólo "
            "deben usarse pernos de alta resistencia a fricción de grado general precargados. El diseño puede "
            "hacerse con base en cálculos para uniones cuando la resistencia de prueba del material de las partes "
            "conectadas exceda 23 kgf/mm². Si la resistencia de prueba de las partes conectadas es menor de 23 "
            "kgf/mm², la resistencia de las uniones usando pernos de alta resistencia a fricción de grado general "
            "debe ser determinada mediante ensayos. En estructuras de aluminio, el relajamiento de la precarga del "
            "perno debido a la tensión en el material unido no puede ignorarse. "
            "La expansión térmica del aluminio excede la del acero y, por lo tanto, la variación en la tensión del "
            "perno debida al cambio de temperatura no puede ignorarse. Una temperatura reducida, reduce la "
            "capacidad por fricción y una temperatura incrementada, incrementa el esfuerzo a tensión en el perno y "
            "el esfuerzo de aplastamiento debajo de las arandelas. Estos efectos son significativos únicamente "
            "para cambios extremos de temperatura y longitudes grandes de agarre."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_5_1_a_2", "seccion": "F.5.6.5.1",
        "titulo": "F.5.6.5.1 — Estado límite último (menor entre cortante y aplastamiento). F.5.6.5.2 — Estado límite de servicio (γs=1.2)",
        "texto": (
            "F.5.6.5.1 — Estado límite último (resistencia estática) — Para pernos de alta resistencia a fricción "
            "en agujeros de holgura normal, la capacidad última es la menor entre la capacidad por cortante como se "
            "determina en F.5.6.4.2 y la capacidad por aplastamiento como se determina en F.5.6.4.4. "
            "F.5.6.5.2 — Estado límite de servicio (deformación) — El estado límite de servicio para una conexión "
            "hecha con pernos de alta resistencia a fricción se alcanza cuando la carga cortante aplicada a "
            "cualquier perno iguala su capacidad por fricción determinada en F.5.6.5.3. Para la revisión del "
            "estado límite de servicio, γs = 1.2."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_5_3_4", "seccion": "F.5.6.5.3",
        "titulo": "F.5.6.5.3 — Capacidad por fricción: Fc=Pp·μs·NF/γs (ec. F.5.6.5-1). F.5.6.5.4 — Preesfuerzo: Pp=Po-0.9Stb (ec. F.5.6.5-2)",
        "texto": (
            "F.5.6.5.3 — Capacidad por fricción — La resistencia de diseño al cortante depende de la capacidad por "
            "fricción del perno de alta resistencia, dicha capacidad por fricción (Fc) está dada por lo siguiente: "
            "Fc = Pp μs NF / γs  (F.5.6.5-1). "
            "Donde: Pp = carga de preesfuerzo (véase F.5.6.5.4). μs = coeficiente de deslizamiento (véase "
            "F.5.6.5.5). γs = 1.33 si el valor de μs se toma como 0.33; γs = 1.1 si el valor de μs se encuentra en "
            "ensayos. NF = número de interfaces de fricción. "
            "F.5.6.5.4 — Preesfuerzo — La carga de preesfuerzo para un perno de alta resistencia a fricción se "
            "debe tomar como se indica enseguida: Pp = Po - 0.9 Stb  (F.5.6.5-2). Donde: Po = carga de prueba del "
            "perno. Stb = carga de tensión externa aplicada en la dirección axial del perno (si la hay)."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_5_5", "seccion": "F.5.6.5.5",
        "titulo": "F.5.6.5.5 — Coeficiente de deslizamiento: μs=0.33 para interfaces tratadas con chorro de arena de óxido de aluminio G38, condiciones de aplicabilidad",
        "texto": (
            "F.5.6.5.5 — Coeficiente de deslizamiento — Cuando todas las partes conectadas son de aleación de "
            "aluminio y las interfaces de fricción han sido tratadas para asegurar propiedades de fricción "
            "consistentes por medio de chorro de arena de óxido de aluminio G38, se puede suponer un valor μs=0.33 "
            "siempre y cuando el espesor total de las partes conectadas exceda el diámetro del perno y el esfuerzo "
            "en el área bruta de las partes no exceda 0.6 f0.2 (donde f0.2 es la resistencia de prueba a tensión "
            "del 2% para el material de la lámina). "
            "Si una o más de las condiciones anteriores no se obedece, μs debe determinarse a partir de ensayos. "
            "El número de pernos necesario para obtener la capacidad por fricción que satisfaga F.5.6.5.2, cuando "
            "se toma μs=0.33, puede ser mayor que el número requerido para satisfacer el estado límite último "
            "(véase F.5.6.5.1). En tales casos, puede ser ventajoso desarrollar un tratamiento de superficie para "
            "las interfaces que incremente el factor de deslizamiento."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_6_intro_1", "seccion": "F.5.6.6",
        "titulo": "F.5.6.6 — Uniones con pasadores: definición, dispositivo de sujeción 10% cortante. F.5.6.6.1 — Pasadores sólidos: luz efectiva, esfuerzos límite (ec. F.5.6.6-1/2)",
        "texto": (
            "F.5.6.6 — UNIONES CON PASADORES — En una unión con pasador, las partes están conectadas por un solo "
            "pasador que permite la rotación. No hay carga axial en el pasador y, por lo tanto, no hay acción de "
            "mordaza sobre las partes conectadas. Los pasadores pueden no estar sometidos a cortante simple, así "
            "uno de los miembros a ser unidos debe tener un extremo en horquilla o abrazadera. El sistema de "
            "sujeción del pasador, por ejemplo una presilla de resorte, debe diseñarse para soportar una carga "
            "lateral igual al 10% de la fuerza cortante total en el pasador. "
            "F.5.6.6.1 — Pasadores sólidos — Se deben considerar los esfuerzos de flexión en los pasadores y para "
            "ésto se toma una luz efectiva igual a la distancia entre centros de apoyos. Sin embargo, si las "
            "platinas de apoyo tienen un espesor mayor que la mitad del diámetro del pasador, se puede considerar "
            "la variación de la presión de aplastamiento a través del espesor de la platina al determinar la luz "
            "efectiva. "
            "Si el pasador debe ser removido para desmantelar la estructura y reinsertado para reensamblarla, la "
            "sección transversal del pasador debe revisarse para un límite de servicio asociado con el límite de "
            "comportamiento elástico. Los siguientes esfuerzos no deben ser excedidos bajo carga mayorada: "
            "(a) Esfuerzo cortante promedio en el pasador: φ 0.6 pa  (F.5.6.6-1). "
            "(b) Esfuerzo de flexión en el pasador: φ 1.2 pa  (F.5.6.6-2). "
            "Donde: pa = definido para pasadores de acero y de aluminio en F.5.6.4.1. φ = coeficiente de reducción "
            "de capacidad (véase la tabla F.5.3.3-1). "
            "Si el pasador estará instalado permanentemente, se puede suponer una distribución plástica completa "
            "del esfuerzo de flexión bajo la carga mayorada de diseño."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_6_2", "seccion": "F.5.6.6.2",
        "titulo": "F.5.6.6.2 — Miembros conectados por pasadores: área neta mínima 1.33Pφ/pa, espesor mínimo, área neta a 45°, ancho neto de platina de apoyo, tolerancia de diámetro 5%",
        "texto": (
            "F.5.6.6.2 — Miembros conectados por pasadores — Las siguientes reglas no deben ser usadas cuando la "
            "línea de acción de la carga está en otra dirección diferente a la del flujo del grano en las partes "
            "conectadas. "
            "El área neta a través del agujero del pasador, normal al eje de un miembro a tensión conectado por un "
            "pasador, debe ser al menos 1.33 Pφ/pa y el espesor del miembro conectado debe ser por lo menos "
            "Pφ/(1.6 pa df) para instalaciones permanentes o Pφ/(1.4 pa df) para instalaciones desmontables. "
            "Donde: P = carga axial mayorada. pa = definido en F.5.4.2 para el material del miembro conectado. "
            "df = diámetro del pasador. φ = coeficiente de reducción de capacidad (véase la tabla F.5.3.3-1). "
            "El área neta de cualquier sección a cada lado del eje del miembro, medida a un ángulo de 45° o menos "
            "con el eje del miembro, debe ser por lo menos 0.9 P γm / pa. "
            "El ancho neto de la platina de apoyo en el agujero del pasador, medido normal al eje del miembro, no "
            "debe exceder ocho veces el espesor de la platina de apoyo. "
            "El diámetro del agujero del pasador no debe exceder el diámetro del pasador en más del 5%. "
            "Las platinas de los pasadores, y cualquier conexión entre ellas y el miembro, deben diseñarse para "
            "soportar una parte de la carga axial total proporcional a la parte correspondiente a la platina del "
            "área total de apoyo del pasador."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
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
    print(f"Upsert OK: {len(rows)} filas nuevas.")


if __name__ == "__main__":
    main()
