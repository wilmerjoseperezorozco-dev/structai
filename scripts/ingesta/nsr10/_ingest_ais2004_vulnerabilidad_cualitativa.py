"""
Manual de Construccion, Evaluacion y Rehabilitacion Sismo Resistente de
Viviendas de Mamposteria (AIS, financiado por el FOREC tras el terremoto
del Eje Cafetero de 1999, con apoyo de DPAE Bogota y CEDERI-Uniandes).
El mas antiguo de la cadena AIS 2004 -> Build Change 2015 -> AIS 410-23
2023. Este chunk cubre el Capitulo II (evaluacion cualitativa rapida de
vulnerabilidad por checklist ponderado) -- un metodo mas simple que el PAM
cuantitativo de Build Change, util como primer filtro de campo antes de un
analisis mas detallado.

Fuente: publicado abiertamente (bdd.pseau.org / academia.edu / civilgeeks.com,
multiples espejos). Resumen tecnico en palabras propias con atribucion, no
reproduccion literal extensa; no se distribuye el PDF a traves de la app.

Uso: python _ingest_ais2004_vulnerabilidad_cualitativa.py
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
        "id": "AIS2004-cap2-vulnerabilidad_cualitativa",
        "seccion": "Capítulo II — Evaluación cualitativa de vulnerabilidad",
        "titulo": (
            "Metodo cualitativo rapido de evaluacion de vulnerabilidad sismica para "
            "vivienda de 1-2 pisos: checklist ponderado con 3 niveles (Baja/Media/Alta = "
            "1/2/3) en 6 categorias (geometria, calidad constructiva, aspectos "
            "estructurales, cimentacion, suelo, entorno), con formula de calificacion "
            "global ponderada. Mas simple que el metodo PAM cuantitativo de Build Change "
            "-- sirve como primer filtro de campo antes de un analisis detallado."
        ),
        "texto": (
            "AIS 2004 — Manual de Construcción, Evaluación y Rehabilitación Sismo "
            "Resistente de Viviendas de Mampostería. Capítulo II — Evaluación del grado "
            "de vulnerabilidad sísmica de viviendas de uno y dos pisos ya construidas "
            "(basado en las disposiciones del Título E de la NSR-98, disposiciones "
            "simplificadas para vivienda de 1-2 pisos hasta 15 unidades o 3000 m²).\n\n"
            "MÉTODO: un checklist cualitativo, más simple y rápido que el método "
            "cuantitativo PAM (ver chunks BUILDCHANGE-2015-*), útil para una primera "
            "inspección de campo. Cada aspecto se califica en 3 niveles — Vulnerabilidad "
            "Baja (=1), Media (=2), Alta (=3) — y se agrupan en 6 categorías con pesos "
            "relativos fijos:\n"
            "  - Aspectos geométricos (peso 20%): irregularidad en planta, cantidad de "
            "muros en las dos direcciones, irregularidad en altura\n"
            "  - Aspectos constructivos (peso 20%): calidad de las juntas de pega en "
            "mortero, tipo y disposición de las unidades de mampostería, calidad de los "
            "materiales\n"
            "  - Aspectos estructurales (peso 30%, el más pesado): muros confinados y "
            "reforzados, detalles de columnas/vigas de confinamiento, vigas de amarre o "
            "corona, características de las aberturas, entrepiso, amarre de cubiertas\n"
            "  - Cimentación (peso 10%)\n"
            "  - Suelos (peso 10%)\n"
            "  - Entorno / pendiente del terreno (peso 10%)\n\n"
            "CRITERIOS CONCRETOS DE CADA NIVEL (ejemplos citados, útiles para una "
            "checklist automatizada):\n"
            "  - Cantidad de muros: vulnerabilidad baja si hay longitud de muros en cada "
            "dirección principal ≥ Lo = (Mo × Ap) / t, donde Ap = área en planta (×0.67 "
            "si la cubierta es liviana), t = espesor de muros, Mo = coeficiente tabulado.\n"
            "  - Calidad de juntas de mortero: baja vulnerabilidad si el espesor de la "
            "mayoría de las pegas está entre 0.7 y 1.3 cm, juntas uniformes y continuas; "
            "alta vulnerabilidad si la pega es \"muy pobre entre los bloques, casi "
            "inexistente\".\n"
            "  - Calidad de materiales: baja vulnerabilidad si el mortero no se deja "
            "rayar con un clavo o herramienta metálica, el concreto no tiene hormigueros "
            "ni acero expuesto, hay al menos 3-4 barras No.3 longitudinales en elementos "
            "de confinamiento, y el ladrillo resiste caídas de al menos 2 metros sin "
            "desintegrarse.\n"
            "  - Confinamiento: baja vulnerabilidad si TODOS los muros están confinados "
            "con vigas y columnas de concreto reforzado, espaciados no más de 4 m o la "
            "altura entre pisos, con refuerzo longitudinal Y transversal en las columnas "
            "(mínimo 4 barras No.3, estribos cada 10-15 cm).\n"
            "  - Aberturas: baja vulnerabilidad si las aberturas en muros estructurales "
            "totalizan menos del 35% del área total del muro, con longitud de aberturas "
            "menor a la mitad de la longitud total del muro.\n"
            "  - Suelo: baja vulnerabilidad si no hay hundimientos, árboles o postes "
            "inclinados alrededor, ni vibración perceptible al paso de vehículos "
            "pesados; alta vulnerabilidad si el suelo es blando o arena suelta, con "
            "asentamientos visibles en la zona.\n"
            "  - Entorno (pendiente del terreno): baja vulnerabilidad si la topografía "
            "es plana o con inclinación <20°; alta vulnerabilidad si la pendiente supera "
            "30° respecto a la horizontal.\n\n"
            "CALIFICACIÓN GLOBAL: para cada categoría, la calificación de vulnerabilidad "
            "es el PROMEDIO de las calificaciones de sus componentes individuales; luego "
            "cada categoría se multiplica por su peso relativo y se suman todos los "
            "productos para obtener la calificación global de la vivienda. Ejemplo "
            "trabajado en el manual: una vivienda con aspectos geométricos=1.33, "
            "constructivos=2, estructurales=2.67, cimentación=2, suelos=2, entorno=2, "
            "da una calificación global de 2.1 → clasificada como VULNERABILIDAD MEDIA "
            "(el rango 1.0-1.5 sería Baja, 1.5-2.5 Media, 2.5-3.0 Alta, aproximadamente, "
            "aunque el documento no tabula explícitamente los rangos de corte — se infiere "
            "de la escala 1/2/3 subyacente).\n\n"
            "USO RECOMENDADO PARA STRUCTAI: este método, por su simplicidad (checklist "
            "cualitativo, sin fórmulas de resistencia de materiales), es ideal como una "
            "primera herramienta de auto-diagnóstico accesible para propietarios o "
            "personal no experto — complementario, no sustituto, del método cuantitativo "
            "PAM (Build Change/AIS 410-23) que sí requiere criterio de un ingeniero "
            "calificado para la fase de diseño de la intervención."
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
    print(f"OK: {len(rows)} chunks AIS 2004 cargados con embedding.")


if __name__ == "__main__":
    main()
