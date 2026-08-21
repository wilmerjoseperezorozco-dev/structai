"""
AIS 410-23: Evaluacion y Reduccion de la Vulnerabilidad Sismica en Viviendas
de Mamposteria (Asociacion Colombiana de Ingenieria Sismica, junio 2023,
encargado por el Ministerio de Vivienda, Ciudad y Territorio).

Documento publicado abiertamente por Minvivienda para consulta publica
(https://www.minvivienda.gov.co/system/files/consultasp/ais-410-23-uso-mvct-junio-2023.pdf).
Tratamiento: resumen tecnico en palabras propias (no reproduccion literal de
bloques extensos del documento fuente), citando AIS 410-23 como fuente en
cada chunk. No se distribuye el PDF original a traves de la aplicacion.

Complementa directamente al Capitulo A.10 de la NSR-10 (ver
NSR10-A-A_10_general): A.10 asume documentacion de diseno original, que no
existe en la vivienda de origen informal (~60% del parque de vivienda
colombiano segun las cifras citadas mas abajo). AIS 410-23 fue encargado
por el propio Ministerio de Vivienda para llenar exactamente ese vacio.

Uso: python _ingest_ais410_vulnerabilidad_informal.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "AIS 410-23 — Evaluación y Reducción de la Vulnerabilidad Sísmica en Viviendas de Mampostería (complementario a NSR-10 A.10, vivienda de origen informal)"

CHUNKS = [
    {
        "id": "AIS410-23-alcance_cifras",
        "seccion": "Cap. 1 — Alcance y contexto",
        "titulo": (
            "AIS 410-23: por que existe, a que vivienda aplica, y la magnitud real del "
            "problema de vivienda informal en Colombia (cifras oficiales citadas por el "
            "documento). Encargado por Minvivienda porque el Capitulo A.10 de la NSR-10 "
            "es de dificil cumplimiento para vivienda sin documentacion de diseno "
            "original -- el caso tipico de la autoconstruccion."
        ),
        "texto": (
            "AIS 410-23 — Evaluación y Reducción de la Vulnerabilidad Sísmica en Viviendas "
            "de Mampostería. Asociación Colombiana de Ingeniería Sísmica (AIS), Comité "
            "AIS 400 / Subcomité Vulnerabilidad Sísmica de Vivienda Informal, junio 2023. "
            "Encargado y publicado por el Ministerio de Vivienda, Ciudad y Territorio "
            "(Minvivienda) para consulta pública.\n\n"
            "POR QUÉ EXISTE: el Capítulo A.10 de la NSR-10 (evaluación e intervención de "
            "edificaciones existentes) resulta de difícil cumplimiento para vivienda "
            "existente de origen informal, porque su metodología parte de que exista "
            "información técnica mínima del diseño y construcción originales — algo que "
            "la autoconstrucción, por definición, no tiene. Ante esa limitación explícita "
            "de la norma principal, Minvivienda encargó a AIS una metodología de "
            "evaluación alterna diseñada específicamente para este vacío.\n\n"
            "MAGNITUD DEL PROBLEMA (cifras citadas textualmente por el documento, con sus "
            "fuentes): de cada 5 unidades de vivienda que aparecen en el mercado "
            "colombiano, 3 son de origen informal, edificadas sin licencia de "
            "construcción (Centro de Estudios de la Construcción y el Desarrollo Urbano y "
            "Regional, CENAC). Los modelos de exposición de la Fundación Global "
            "Earthquake Model (GEM) reportan cifras cercanas al 70% y 60% de vivienda "
            "informal no reforzada en Medellín y Cali, respectivamente. Un estudio "
            "conjunto entre el Área Metropolitana del Valle de Aburrá (AMVA) y la "
            "Universidad de los Andes (2018) encontró que el 79% de las viviendas del "
            "Valle de Aburrá son de mampostería no reforzada o parcialmente confinada. El "
            "Instituto Distrital de Gestión del Riesgo y Cambio Climático (IDIGER, 2018) "
            "reportó una cifra similar, 75%, para Bogotá.\n\n"
            "LINAJE TÉCNICO del documento: se desarrolla a partir del \"Manual de "
            "Evaluación y Reforzamiento Sísmico para Reducción de Vulnerabilidad en "
            "Viviendas\" producido por Build Change (ONG sin ánimo de lucro especializada "
            "en vivienda resiliente en países en desarrollo), aprobado en 2015 como "
            "régimen de excepción por la Comisión Asesora Permanente para el Régimen de "
            "Construcciones Sismo Resistentes (CASACRS — la misma comisión que redacta la "
            "NSR-10). Ese manual de Build Change se basa a su vez en ASCE-31 (Seismic "
            "Evaluation of Existing Buildings) y ASCE-41 (Seismic Rehabilitation of "
            "Existing Buildings) — los mismos estándares internacionales que la propia "
            "NSR-10 cita en su Capítulo A.10.9.4 para edificaciones formales. AIS 410-23 "
            "además integra investigación experimental sobre sistemas estructurales "
            "típicos de la vivienda informal colombiana, desarrollada por EAFIT "
            "(Medellín), la Escuela Colombiana de Ingeniería Julio Garavito (ECI, "
            "Bogotá) y la Universidad Militar Nueva Granada (UMNG), en colaboración con "
            "Build Change; y retoma principios del \"Manual de construcción, evaluación y "
            "rehabilitación sismo resistente de viviendas de mampostería\" publicado por "
            "AIS en 2004.\n\n"
            "OBJETIVO explícito del documento (citado): \"reducir la vulnerabilidad en "
            "estructuras existentes antes de un evento sísmico [...] reducir al mínimo el "
            "riesgo de pérdida de vidas humanas, y defender en lo posible el patrimonio "
            "del Estado y de los ciudadanos\" — texto que remite directamente al Artículo "
            "1 de la Ley 400 de 1997.\n\n"
            "ALCANCE Y LÍMITES DE APLICABILIDAD (Tabla 1.2.2-1 del documento): aplica a "
            "vivienda de origen informal en todo el territorio nacional, con sistema "
            "estructural fundamentalmente en mampostería, de hasta 3 niveles, uso Grupo I "
            "(residencial, con excepciones para comercio en primer piso). Distingue dos "
            "sistemas: (a) muros de mampostería NO REFORZADA (MNR), con coeficiente de "
            "capacidad de disipación R=1, permitido hasta 2 pisos en zona de amenaza alta "
            "e intermedia y hasta 2 pisos en zona baja; (b) muros de mampostería "
            "CONFINADA (MC), R=2, permitido hasta 2 pisos en zona alta e intermedia y "
            "hasta 3 pisos en zona baja. Se excluyen expresamente las construcciones "
            "cubiertas por A.1.2.4 de la NSR-10, viviendas no informales, viviendas "
            "nuevas (este documento es solo para intervención de lo YA EXISTENTE), y "
            "edificaciones de los grupos de uso II, III o IV.\n\n"
            "CRITERIO DE DESEMPEÑO esperado tras la intervención (no es cero-daño): frente "
            "al sismo de diseño de la NSR-10 (Capítulo A.2), la vivienda debe quedar con "
            "algún margen antes de un colapso parcial o total, y el riesgo general de "
            "lesiones fatales debe ser bajo — aunque puedan producirse lesiones y daño no "
            "estructural. El documento reconoce explícitamente que, cuando no hay recursos "
            "para una intervención completa, se puede aplicar un enfoque de REDUCCIÓN "
            "PROGRESIVA de la vulnerabilidad, priorizando actividades por categoría "
            "(condición estructural, configuración, transferencia de carga, resistencia y "
            "ductilidad) sin generar nuevas deficiencias — filosofía explícitamente "
            "orientada a la realidad económica de este segmento de vivienda, no al ideal "
            "de una intervención completa de una sola vez."
        ),
    },
    {
        "id": "AIS410-23-procedimiento_general",
        "seccion": "Cap. 1.4 — Procedimiento general de evaluación e intervención",
        "titulo": (
            "AIS 410-23: procedimiento general (informacion preliminar, evaluacion de la "
            "vivienda existente, intervencion del sistema estructural), con el flujo de "
            "decision explicito de cuando la metodologia alterna de AIS 410 aplica o no."
        ),
        "texto": (
            "AIS 410-23 — Evaluación y Reducción de la Vulnerabilidad Sísmica en Viviendas "
            "de Mampostería. Sección 1.4 — Procedimiento general de evaluación e "
            "intervención (flujo descrito en la Figura 1.4-1 del documento).\n\n"
            "ETAPA 1 — INFORMACIÓN PRELIMINAR: identificar la vivienda y verificar que "
            "está dentro del alcance del documento (sección 1.2.2); ubicarla en el "
            "territorio; recopilar y analizar datos de zonas de riesgo/amenaza y de zonas "
            "protegidas, de exclusión o de desarrollo urbanístico según el Plan de "
            "Ordenamiento Territorial (POT) vigente; visitar el sitio y explorar el "
            "entorno. En TODOS los casos debe verificarse primero que la vivienda no esté "
            "en zona de amenaza alta por remoción en masa ni en zona de exclusión — si "
            "existen condiciones patológicas de ese tipo (congénitas o adquiridas), deben "
            "resolverse antes de continuar con la reducción de vulnerabilidad sísmica "
            "propiamente dicha.\n\n"
            "ETAPA 2 — EVALUAR LA ESTRUCTURA EXISTENTE: se completa un formato de "
            "levantamiento de vulnerabilidad (LVD, Apéndice A-1 del documento) que "
            "recorre sitio, configuración, elementos estructurales (cimientos, muros "
            "perimetrales e internos, viga de amarre, voladizos, columnas de "
            "confinamiento, aberturas en muros y en losas, sistemas de losa y de "
            "cubierta), elementos no estructurales (parapetos, muros cortos) y calidad de "
            "los materiales (unidades de mampostería, mortero de pega, revoque). De este "
            "levantamiento surge la pregunta central: ¿hay deficiencias?\n\n"
            "PUNTO DE DECISIÓN CLAVE: si hay deficiencias, se evalúa si pueden mitigarse "
            "usando la metodología alterna de AIS 410. Si SÍ se pueden mitigar con esta "
            "metodología, se pasa a diseñar la intervención. Si NO se pueden mitigar con "
            "esta metodología simplificada (p. ej. deficiencias que requieren análisis "
            "estructural más riguroso, o la vivienda excede el alcance de la Tabla "
            "1.2.2-1), el documento indica terminar el reporte y presentarlo — es decir, "
            "AIS 410 tiene un límite explícito de aplicabilidad y no pretende cubrir todos "
            "los casos de vivienda informal, solo el subconjunto que cumple su alcance "
            "declarado.\n\n"
            "ETAPA 3 — INTERVENCIÓN DEL SISTEMA ESTRUCTURAL: si la vulnerabilidad SÍ es "
            "mitigable con AIS 410, se diseña la propuesta de intervención siguiendo los "
            "lineamientos del documento para mitigar TODAS las deficiencias identificadas "
            "(o, bajo el enfoque de reducción progresiva, las priorizadas), se tramitan "
            "los permisos y autorizaciones correspondientes, y se ejecuta la fase de "
            "construcción — con lo cual se considera mitigada la vulnerabilidad de la "
            "vivienda según la metodología del documento.\n\n"
            "Nota de aplicación para StructAI: este flujo es estructuralmente análogo al "
            "de A.10 de la NSR-10 (evaluar → calcular índices → intervenir), pero "
            "simplificado y calibrado para operar SIN planos ni memorias de cálculo "
            "originales — el insumo de entrada es un levantamiento de campo (LVD), no un "
            "expediente técnico preexistente."
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
    print(f"OK: {len(rows)} chunks AIS 410-23 cargados con embedding.")


if __name__ == "__main__":
    main()
