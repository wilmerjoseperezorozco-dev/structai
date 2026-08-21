"""
NSR-10 Titulo A, Capitulo A.10 -- Evaluacion e Intervencion de Edificaciones
construidas antes de la vigencia del Reglamento. Gap real cerrado
2026-08-20: el chunk obsoleto A-SEC10-TAB1 etiquetaba erroneamente este
codigo (A.10) como "notacion general" -- en realidad es el capitulo de
REFUERZO/REHABILITACION SISMICA de edificaciones existentes, directamente
relevante a la idea del usuario de reforzar vivienda ya construida en
Colombia.

Fuente: NSR-10-140-154.pdf (Drive, id 1-QYd8J2UT0e9J0NQqp--2R4zVkoLhE9G),
paginas internas A-97 a A-111.

Uso: python _ingest_a10_evaluacion_intervencion.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título A — Requisitos generales de diseño y construcción sismo resistente"

CHUNKS = [
    {
        "id": "NSR10-A-A_10_general",
        "seccion": "A.10.1 a A.10.9",
        "titulo": (
            "Evaluacion e intervencion de edificaciones EXISTENTES (construidas antes de "
            "esta version de la NSR-10): alcance, procedimiento de 12 etapas (indice de "
            "sobreesfuerzo + indice de flexibilidad, ambos deben ser <1), tipos de "
            "modificacion (ampliacion adosada/en altura, actualizacion, reforzamiento), "
            "requisitos de rehabilitacion sismica segun edad de construccion, y 3 "
            "metodologias internacionales alternas explicitamente autorizadas: ASCE/SEI "
            "41-06, FEMA 356, ATC-40. CORRIGE el chunk obsoleto A-SEC10-TAB1, que "
            "etiquetaba este codigo A.10 como \"notacion general\" -- en realidad es el "
            "capitulo dedicado a refuerzo/rehabilitacion de vivienda y edificios "
            "existentes."
        ),
        "texto": (
            "NSR-10 Título A, Capítulo A.10 — Evaluación e Intervención de Edificaciones "
            "construidas antes de la vigencia de la presente versión del Reglamento.\n\n"
            "A.10.1.1 Alcance general: establece criterios y procedimientos para EVALUAR LA "
            "VULNERABILIDAD SÍSMICA y adicionar, modificar o remodelar el sistema "
            "estructural de edificaciones existentes diseñadas y construidas ANTES de la "
            "vigencia de esta versión de la NSR-10.\n\n"
            "A.10.1.2 Propósito: una edificación intervenida según este capítulo debe "
            "resistir temblores pequeños sin daño, temblores moderados sin daño "
            "estructural (aunque con algo de daño no estructural), y temblores fuertes SIN "
            "COLAPSO — el mismo estándar de desempeño de una edificación nueva.\n\n"
            "A.10.1.3.1 Reparaciones y cambios menores que NO afecten el sistema de "
            "resistencia sísmica ni la integridad estructural NO requieren los estudios de "
            "este capítulo. A.10.1.3.3 explícitamente permite usar estos criterios para "
            "DIAGNÓSTICO o EVALUACIÓN DE VULNERABILIDAD SÍSMICA (no solo para intervención "
            "física) de edificaciones anteriores a esta versión.\n\n"
            "A.10.1.4 Procedimiento de evaluación e intervención — 12 ETAPAS:\n"
            "  Información preliminar:\n"
            "  1. Verificar que la intervención esté cubierta por el alcance (A.10.1.3)\n"
            "  2. Recopilar información del diseño geotécnico/estructural original y "
            "modificaciones posteriores + exploraciones en campo\n"
            "  3. Calificar el estado del sistema estructural: (a) calidad del diseño/"
            "construcción original, (b) estado de mantenimiento y conservación\n"
            "  Evaluación de la estructura existente:\n"
            "  4. Determinar solicitaciones sísmicas equivalentes (A.10.4.2)\n"
            "  5. Análisis elástico de la estructura y cimentación para esas solicitaciones\n"
            "  6. Determinar la RESISTENCIA EXISTENTE (A.10.4.3.3)\n"
            "  7. Obtener la RESISTENCIA EFECTIVA aplicando 2 coeficientes de reducción "
            "(basados en la calificación de la Etapa 3)\n"
            "  8. Calcular el ÍNDICE DE SOBREESFUERZO = máximo cociente entre fuerza interna "
            "solicitada (Etapa 5) y resistencia efectiva (Etapa 7), para cualquier elemento\n"
            "  9. Obtener las derivas de la estructura del análisis de la Etapa 5\n"
            "  10. Calcular el ÍNDICE DE FLEXIBILIDAD = máximo cociente entre deriva "
            "obtenida y deriva permitida por el Capítulo A.6 (horizontal), más un índice "
            "análogo para deflexiones verticales\n"
            "  Intervención del sistema estructural:\n"
            "  11. Definir el tipo de intervención (A.10.6): ampliación adosada, ampliación "
            "en altura, o actualización al Reglamento\n"
            "  12. Reanalizar el conjunto con la intervención propuesta y diseñar para las "
            "nuevas fuerzas\n\n"
            "REGLA CENTRAL: la edificación intervenida debe quedar con ÍNDICE DE "
            "SOBREESFUERZO < 1 e ÍNDICE DE FLEXIBILIDAD < 1 (ambos comparan la estructura "
            "real contra lo que exigiría una edificación nueva bajo esta NSR-10). El "
            "inverso del índice de sobreesfuerzo general expresa la vulnerabilidad como "
            "fracción de la resistencia de una edificación nueva equivalente (A.10.5.1).\n\n"
            "A.10.1.5-1.7: requiere memoria de cálculo firmada por Ingeniero Civil "
            "matriculado (Arts. 26-27 Ley 400/1997), supervisión técnica obligatoria "
            "(Título I) en TODOS los casos, y responsabilidad profesional plena del "
            "diseñador por el comportamiento futuro de la edificación.\n\n"
            "A.10.6 Tipos de modificación: (a) Ampliación adosada — se amplía área sin "
            "cambiar altura (A.10.7); (b) Ampliación en altura — cambia la altura, las dos "
            "porciones trabajan en conjunto obligatoriamente (A.10.8); (c) Actualización al "
            "Reglamento — sin ampliar área ni altura, el propietario decide voluntariamente "
            "reforzar (A.10.9); (d) Modificaciones menores que no incrementen solicitación "
            "sísmica >10% ni reduzcan capacidad >10% en ningún elemento no requieren "
            "revalidar toda la estructura.\n\n"
            "A.10.9 Rehabilitación sísmica — requisitos SEGÚN LA EDAD de la construcción "
            "(fechas clave: Decreto 1400 de 1984 y Ley 400/NSR-98 de 1997):\n"
            "  - Grupos de uso III/IV (indispensables y atención a comunidad): SIEMPRE "
            "deben llegar a nivel de seguridad de edificación NUEVA, sin importar la edad "
            "(A.10.9.2.1)\n"
            "  - Construidas después del 19-feb-1998 (vigencia NSR-98/Ley 400): nivel de "
            "seguridad de edificación nueva (A.10.9.2.2)\n"
            "  - Construidas entre 1-dic-1984 y 19-feb-1998 (vigencia Decreto 1400 de "
            "1984): se permite un índice de flexibilidad hasta 1.5 (no de sobreesfuerzo) "
            "si se busca seguridad de edificación nueva; O ALTERNATIVAMENTE nivel de "
            "\"seguridad limitada\" (A.10.4.2.2) si el propietario lo acepta por escritura "
            "pública (A.10.9.2.3)\n"
            "  - Construidas ANTES del 1-dic-1984 (sin Decreto 1400 vigente — la mayoría de "
            "la vivienda informal/autoconstruida antigua cae aquí): mínimo nivel de "
            "\"seguridad limitada\" (A.10.4.2.2), también requiere aceptación por "
            "escritura pública del propietario (A.10.9.2.4)\n"
            "  - Patrimonio histórico: se permite nivel de seguridad menor, justificado por "
            "el ingeniero y aceptado por el propietario mediante escritura pública\n\n"
            "A.10.9.4 METODOLOGÍAS ALTERNAS (clave para reforzamiento avanzado): "
            "exclusivamente para EVALUACIÓN DE VULNERABILIDAD (no reemplaza el diseño de "
            "la intervención), la NSR-10 autoriza explícitamente sustituir A.10.4 por las "
            "secciones de rehabilitación de estos 3 documentos internacionales, siempre que "
            "se garanticen los criterios de A.10.9:\n"
            "  (a) \"Seismic Rehabilitation of Existing Buildings\", ASCE/SEI 41-06, "
            "American Society of Civil Engineers, 2006\n"
            "  (b) \"Prestandard and Commentary for the Seismic Rehabilitation of "
            "Buildings\", FEMA 356, 2000\n"
            "  (c) \"Seismic Evaluation and Retrofit of Concrete Buildings\", ATC-40 "
            "(Vol 1 + 2), Applied Technology Council, 1996\n"
            "Estos son los mismos documentos que la ingeniería de rehabilitación sísmica "
            "usa internacionalmente (ASCE 41 es hoy el estándar dominante, sucesor de "
            "FEMA 356; ATC-40 es específico para concreto con el método del espectro de "
            "capacidad)."
        ),
    },
    {
        "id": "NSR10-A-A_10_10_reparacion_post_sismo",
        "seccion": "A.10.10",
        "titulo": (
            "Reparacion de edificaciones DANADAS POR SISMOS: procedimiento tras un sismo "
            "real para decidir tecnicamente si reparar o demoler, y requisitos de la "
            "reparacion segun tipo de dano. Directamente relevante al sismo real de Cali "
            "del 10-ago-2026."
        ),
        "texto": (
            "NSR-10 Título A, Capítulo A.10. A.10.10 — Reparación de edificaciones dañadas "
            "por sismos.\n\n"
            "A.10.10.1 General: tras un sismo, las edificaciones con daños MODERADOS A "
            "SEVEROS (estructurales, no estructurales, o ambos) deben evaluarse con los "
            "estudios de A.10.10.2 para establecer si es técnicamente factible repararlas. "
            "Esto da criterio técnico para la decisión del dueño o autoridad competente de "
            "demoler totalmente, o para apelar una decisión de demolición ya tomada, ANTES "
            "de contar con el estudio.\n\n"
            "A.10.10.1.1 Objeto: una edificación reparada según este capítulo debe cumplir "
            "el propósito de las normas sismo-resistentes (Art. 1 Ley 400/1997, A.1.2.2).\n\n"
            "A.10.10.1.2 Alcance de la reparación: depende del tipo de daño presentado. Las "
            "edificaciones de grupos de uso III/IV (indispensables/atención a la "
            "comunidad) tienen requisito reforzado: deben cumplir A.10.9.2.1 (nivel de "
            "edificación nueva), sin excepción por el hecho de estar reparándose tras un "
            "sismo real."
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
    print(f"OK: {len(rows)} chunks A.10 cargados con embedding.")


if __name__ == "__main__":
    main()
