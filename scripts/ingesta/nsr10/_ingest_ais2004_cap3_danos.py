"""
AIS 2004 -- Capitulo III: Evaluacion del nivel de dano en viviendas de uno y
dos pisos de mamposteria afectadas por sismos. Clasificacion de danos por
mecanismo de falla (Leves/Moderados/Severos) con umbrales cuantitativos de
ancho de grieta, para mamposteria no reforzada (MNR), confinada (MC) y
reforzada (MR). Directamente relevante para evaluacion post-sismo real
(terremoto de Cali, agosto 2026).

Fuente: mismo documento AIS 2004 ya registrado (ver AIS-2004 en
normas_registro), paginas internas 3-1 a 3-33 (Capitulo III). Resumen
tecnico en palabras propias con atribucion, no reproduccion literal
extensa; no se distribuye el PDF a traves de la app.

Uso: python _ingest_ais2004_cap3_danos.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo Resistente de Viviendas de Mampostería (base histórica de AIS 410-23, financiado por el FOREC tras el terremoto del Eje Cafetero 1999)"

CHUNKS = [
    {
        "id": "AIS2004-cap3-clasificacion_danos",
        "seccion": "Capítulo III — Evaluación del nivel de daño post-sismo",
        "titulo": (
            "Clasificacion de danos post-sismo por mecanismo de falla en vivienda de "
            "mamposteria (no reforzada MNR, confinada MC, reforzada MR): 3 niveles "
            "Leves/Moderados/Severos con umbrales CUANTITATIVOS de ancho de grieta en mm "
            "por cada mecanismo (rotacion, deslizamiento de juntas, tension diagonal, "
            "flexion, cortante). Logica de agregacion tipo 'gobierna el peor caso', "
            "distinta del promedio ponderado del Capitulo II. Util para inspeccion real "
            "post-terremoto."
        ),
        "texto": (
            "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo "
            "Resistente de Viviendas de Mampostería. Capítulo III — Evaluación del nivel "
            "de daño en viviendas de uno y dos pisos de mampostería afectadas por "
            "sismos.\n\n"
            "ALCANCE: el documento se refiere ÚNICAMENTE a daños causados por terremotos "
            "(no por deslizamientos, asentamientos, cauces cercanos, vientos fuertes o "
            "deterioro natural — aunque el método puede adaptarse a esos casos con "
            "participación de un ingeniero). Antes de reparar, es indispensable "
            "identificar la causa real del daño para que la intervención lo resuelva de "
            "fondo y no se repita.\n\n"
            "ELEMENTOS SUSCEPTIBLES A DAÑO, por sistema constructivo:\n"
            "  Mampostería No Reforzada (MNR): muros cortos o pilastras (pilas entre "
            "aberturas de puertas/ventanas, concentran la deformación horizontal), "
            "vigas/dinteles/antepechos (más débiles que las pilas adyacentes, acumulan "
            "daño), muros fuertes (longitud apreciable, sin aberturas, comportamiento de "
            "voladizo empotrado en cimentación).\n"
            "  Mampostería Confinada (MC): paneles (mampostería contenida entre marcos de "
            "concreto reforzado — puede agrietarse en diagonal o fallar fuera del plano), "
            "elementos de confinamiento — vigas y columnas — (pueden fallar por corte, "
            "tensión, compresión, o combinación, generalmente como consecuencia del "
            "agrietamiento del panel interior).\n"
            "  Mampostería Reforzada (MR): muros fuertes (voladizo empotrado en la base, "
            "falla controlada en la base por flexión y/o cortante), muros débiles (más "
            "débiles que las vigas que los conectan, falla por cortante — grietas "
            "diagonales), vigas/dinteles/antepechos (susceptibles por desplazamientos "
            "horizontales del sistema principal).\n\n"
            "SISTEMA DE CLASIFICACIÓN — 3 niveles con umbrales cuantitativos de ancho de "
            "grieta (ejemplos representativos por mecanismo; el documento define criterios "
            "específicos para cada combinación elemento×mecanismo):\n\n"
            "  Muros cortos/pilastras MNR, ROTACIÓN: Leve = pequeñas grietas y mortero "
            "fisurado en juntas horizontales de los extremos; Moderado = grietas "
            "moderadas, posibles grietas en juntas de pega dentro de la pila pero sin "
            "abrirse las juntas horizontales; Severo = posible movimiento en/fuera del "
            "plano, unidades rotas y fisuradas en las esquinas.\n"
            "  Muros cortos/pilastras MNR, DESLIZAMIENTO DE JUNTAS: Leve = mortero "
            "agrietado sin desplazamiento horizontal; Moderado = aberturas en las juntas "
            "de 6 mm, 5% de hiladas con grietas en las unidades; Severo = aberturas de "
            "~12 mm, más del 10% de hiladas agrietadas.\n"
            "  Muros cortos/pilastras MNR, TENSIÓN DIAGONAL: Leve = grietas diagonales "
            "pequeñas en menos del 5% de las hiladas; Moderado = grietas diagonales "
            "menores a 6 mm de ancho que alcanzan las esquinas, sin roturas en ellas; "
            "Severo = grietas mayores a 6 mm, roturas y fisuras secundarias en esquinas, "
            "desprendimiento de mampostería.\n"
            "  Muros fuertes MR, FLEXIÓN/CORTANTE/INESTABILIDAD FUERA DEL PLANO: Leve = "
            "grietas ≤3 mm; Moderado = grietas ≤5 mm, refuerzo en estado de fluencia, "
            "desplazamiento permanente no significativo; Severo = refuerzo en fluencia o "
            "rotura, unidades desplazadas lateralmente, mecanismos de colapso "
            "incipientes.\n"
            "  Muros débiles MR, CORTANTE PURO: Leve = grietas diagonales ≤2 mm; "
            "Moderado = similar sin fisuración de unidades; Severo = grieta única "
            "dominante >10 mm con fallamiento localizado en esquinas inferiores.\n"
            "  Vigas débiles MR, FLEXIÓN/CORTANTE: Leve = grietas <3 mm; Moderado = "
            "grietas entre 3 y 6 mm con fisuras secundarias; Severo = refuerzo en "
            "fluencia/rotura, grietas >9 mm, roturas importantes en uniones de pilas y "
            "vigas.\n\n"
            "AGREGACIÓN — LÓGICA DEL PEOR CASO (distinta del promedio ponderado del "
            "Capítulo II de vulnerabilidad): la calificación se codifica Leve=1, "
            "Moderado=2, Severo=3, y se agrega en tres niveles sucesivos, tomando SIEMPRE "
            "EL MAYOR VALOR (no un promedio):\n"
            "  1. Calificación del daño según mecanismo (para cada elemento, el mayor "
            "entre sus posibles mecanismos de falla)\n"
            "  2. Calificación del daño del tipo de elemento = el mayor valor de todos "
            "los mecanismos correspondientes a ese tipo de elemento\n"
            "  3. Calificación GLOBAL del daño de la edificación = el mayor valor entre "
            "todos los tipos de elemento evaluados\n"
            "Esta lógica de 'un solo eslabón débil define el resultado' es "
            "deliberadamente conservadora y apropiada para diagnóstico post-sismo: un "
            "muro con daño severo no se diluye promediándolo con muros sanos — la "
            "edificación completa se clasifica según su peor componente."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in CHUNKS]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks AIS 2004 Cap III cargados con embedding.")


if __name__ == "__main__":
    main()
