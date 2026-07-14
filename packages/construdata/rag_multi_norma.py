"""
══════════════════════════════════════════════════════════════════
RAG MULTI-NORMA — NTC + NSR-10 + Seguridad Industrial
Búsqueda híbrida RRF (semántica + BM25) sobre knowledge_graph
Embeddings: sentence-transformers local (sin costo, sin llamadas externas).
Síntesis de respuesta: Groq (API compatible con OpenAI, respuestas en 1-3s —
Ollama local queda descartado para producción: en CPU sin GPU tarda 4-5 min
por respuesta, inviable para un SaaS con usuarios reales).
Uso: from rag_multi_norma import ask, route_query
══════════════════════════════════════════════════════════════════
"""
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from openai import OpenAI
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 384-dim, multilingüe — debe calzar con nsr10_chunks/ntc_chunks.embedding vector(384)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

groq_client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")


@lru_cache(maxsize=1)
def _embedding_model():
    # Fuerza modo offline: el modelo ya está en caché local (~/.cache/huggingface).
    # Sin esto, sentence-transformers intenta primero contactar HF Hub para
    # revisar actualizaciones y, sin token, puede colgarse por rate-limit.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@dataclass
class ChunkResult:
    chunk_id: str
    norma: str
    seccion: str
    contenido: str
    score: float
    estado_vigencia: Optional[str] = None
    derogada_por: Optional[str] = None
    alcance_derogacion: Optional[str] = None

    @property
    def vigente(self) -> bool:
        # None (norma_id sin vincular todavía) se trata como vigente por
        # defecto — no todos los chunks están linkeados a normas_registro
        # aún, y no hay evidencia de que estén derogados.
        return self.estado_vigencia in (None, "vigente")

# ─── ROUTER INTELIGENTE ───────────────────────────────────────────────────────
KEYWORD_MAP = {
    "NTC 673":  ["resistencia compresion","cilindro","f'c","ensayo compresion","probeta"],
    "NTC 396":  ["asentamiento","slump","consistencia","cono abrams"],
    "NTC 174":  ["agregado","grava","arena","granulometria","modulo finura"],
    "NTC 121":  ["cemento portland","fraguado","clinker","tipo cemento"],
    "NTC 30":   ["tipo cemento","portland tipo","clasificacion cemento"],
    "NTC 4026": ["bloque estructural","mamposteria","muro portante","Clase A","Clase B"],
    "NTC 4076": ["bloque no estructural","tabiqueria","divisorio"],
    "NTC 3459": ["agua concreto","sulfatos agua","cloruros agua","pH agua"],
    "NTC 1299": ["aditivo","plastificante","retardante","acelerante","superplastificante"],
    "NTC 1032": ["contenido aire","metodo presion","aire atrapado"],
    "NTC 504":  ["refrentado","cilindro refrentado","yeso alta resistencia"],
    "NTC 454":  ["muestra concreto","toma de muestra","muestra compuesta"],
    "NTC 2289": ["acero refuerzo","barra corrugada","fy","ASTM A706","Grado 60"],
    "NTC 1500": ["instalacion hidraulica","fontaneria","desague","sanitaria"],
    "NSR-10":   ["sismorresistente","sismo","zona sismica","espectro","NSR-10"],
    "Resolución 1409 de 2012": ["trabajo alturas","caida","arnés","linea vida","andamio"],
    "Decreto 1072 de 2015":    ["SGSST","seguridad salud trabajo","SG-SST","PHVA","politica sst","copasst","vigia sst","investigacion de accidentes","indicadores sst","matriz ipvr"],
    "Resolución 0312 de 2019": ["estandares minimos","autoevaluacion sst","plan de mejoramiento","semaforo sst","calificacion sg-sst"],
    "Ley 1562 de 2012":        ["riesgos laborales","accidente de trabajo","enfermedad laboral","arl","cotizacion riesgos laborales","nivel de riesgo empresa","pension de invalidez"],
    "Resolución 5018 de 2019": ["riesgo electrico","sector electrico","alta tension","reglas oro"],
    "Resolución 3232 de 2024": ["licencia urbanistica","curador","tramite","licencia construccion"],
}

def route_query(query: str) -> list[str]:
    """Devuelve las normas más relevantes para la consulta (máx 3)."""
    q = query.lower()
    scores: dict[str, int] = {}
    for norma, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in q:
                scores[norma] = scores.get(norma, 0) + (2 if len(kw) > 8 else 1)
    if not scores:
        return []
    max_s = max(scores.values())
    return [n for n, s in sorted(scores.items(), key=lambda x: -x[1]) if s >= max_s * 0.5][:3]


# ─── AGENTE DELEGADOR — routing por dominio de ingeniería ────────────────────
# Cada motor tiene su propio corpus de chunks en motor_chunks (columna `motor`).
# Solo se registra aquí un dominio cuando YA tiene chunks reales ingestados
# (ver scripts/ingest_motor_chunks.py) — si no, el routing lo dejaría cayendo
# a una búsqueda vacía en vez de al RAG normativo general, que sí tiene contenido.
MOTOR_KEYWORD_MAP = {
    "aquai": [
        "acueducto", "alcantarillado", "dotacion", "dotación", "caudal de diseño",
        "poblacion de diseño", "población de diseño", "hazen-williams", "hazen williams",
        "golpe de ariete", "ariete hidraulico", "manning", "estacion de bombeo",
        "estación de bombeo", "ptap", "potabilizacion", "potabilización", "ptar",
        "aguas residuales", "vertimiento", "lodos activados", "uasb", "laguna facultativa",
        "tarifa de acueducto", "cra ", "curva idf", "red de acueducto", "red de alcantarillado",
        "sui", "npsh", "coagulante", "floculacion", "floculación", "sedimentador",
        "caudal contra incendio", "hidrante", "dotacion neta", "dotación neta",
        "planta de tratamiento de agua potable", "reactor uasb",
    ],
    "geopot": [
        "uscs", "clasificacion de suelos", "clasificación de suelos", "limites de atterberg",
        "límites de atterberg", "limite liquido", "límite líquido", "limite plastico",
        "límite plástico", "indice de plasticidad", "índice de plasticidad", "proctor",
        "cbr", "subrasante", "granulometria", "granulometría", "modulo de finura",
        "módulo de finura", "cilindro de concreto", "resistencia a compresion",
        "resistencia a compresión", "asentamiento", "slump", "cono de abrams",
        "conformidad del concreto", "agregado grueso", "agregado fino", "desgaste los angeles",
        "desgaste los ángeles", "diseño de mezcla", "aci 211", "zona sismica", "zona sísmica",
        "aa av fa fv", "microzonificacion", "microzonificación", "laboratorio de suelos",
        "pot", "plan de ordenamiento territorial", "ordenamiento territorial",
        "estudios basicos de amenaza", "estudios básicos de amenaza", "amenaza por movimientos en masa",
        "movimientos en masa", "amenaza por inundacion", "amenaza por inundación",
        "avenidas torrenciales", "expediente municipal", "determinantes ambientales",
        "gestion del riesgo", "gestión del riesgo", "vulnerabilidad ambiental",
        "estabilidad de taludes", "capacidad portante",
    ],
    "vias": [
        "radio minimo", "radio mínimo", "curva horizontal", "peralte", "distancia de visibilidad",
        "pendiente longitudinal", "ancho de carril", "bombeo de calzada", "diseño geometrico",
        "diseño geométrico", "esal", "numero estructural", "número estructural", " sn ",
        "pavimento asfaltico", "pavimento asfáltico", "pavimento rigido", "pavimento rígido",
        "espesor de rodadura", "manual invias", "bache", "grieta", "ahuellamiento", "craquelado",
        "losa fragmentada", "mantenimiento vial", "pci", "indice de condicion", "índice de condición",
        "nivelacion diferencial", "nivelación diferencial", "error de cierre", "adoquin", "adoquín",
        "geotextil", "cemento hidraulico", "cemento hidráulico", "aditivo para concreto",
        "aire incorporado", "agua para concreto", "ceniza volante", "puzolana", "escoria de alto horno",
        "prefabricados de concreto", "agregado liviano",
    ],
    "gerencia": [
        "cpi", "spi", "qpi", "ppi", "earned value", "valor ganado", "variacion de costo",
        "variación de costo", "variacion de cronograma", "variación de cronograma", "tcpi",
        "eac", "estimacion al completar", "estimación al completar", "bac", "score de riesgo",
        "riesgo de proyecto", "curva s", "indice de desempeño", "índice de desempeño",
        "trazabilidad de portafolio", "portafolio de proyectos", "prediccion de fecha",
        "predicción de fecha", "regresion lineal", "regresión lineal", "deteccion de anomalias",
        "detección de anomalías", "correlacion de pearson", "correlación de pearson",
        "forecast de kpi",
    ],
}


def route_motor(query: str) -> Optional[str]:
    """Detecta si la pregunta pertenece al dominio de un motor específico
    (aquai, geopot, vias, gerencia...) en vez del RAG normativo general."""
    q = query.lower()
    scores: dict[str, int] = {}
    for motor, keywords in MOTOR_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in q:
                scores[motor] = scores.get(motor, 0) + (2 if len(kw) > 10 else 1)
    if not scores:
        return None
    return max(scores.items(), key=lambda x: x[1])[0]

# ─── BÚSQUEDA HÍBRIDA ────────────────────────────────────────────────────────
def embed_query(text: str) -> list[float]:
    model = _embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()

def search(query: str, norma_filter: Optional[str] = None, top_k: int = 6, motor_filter: Optional[str] = None) -> list[ChunkResult]:
    """Búsqueda híbrida RRF en Supabase. motor_filter restringe a motor_chunks.motor
    (ej. 'aquai') — deja fuera nsr10_chunks/ntc_chunks cuando se usa."""
    embedding = embed_query(query)
    result = sb.rpc("search_knowledge", {
        "query_embedding": embedding,
        "query_text": query,
        "p_norma": norma_filter,
        "match_count": top_k,
        "p_motor": motor_filter,
    }).execute()
    chunks = []
    for r in result.data:
        meta = r.get("metadata") or {}
        chunks.append(ChunkResult(
            chunk_id=r["chunk_id"],
            norma=r["norma"],
            seccion=r["seccion"],
            contenido=r["contenido"],
            score=r["score"],
            estado_vigencia=meta.get("estado_vigencia"),
            derogada_por=meta.get("derogada_por"),
            alcance_derogacion=meta.get("alcance_derogacion"),
        ))
    return chunks

# ─── GENERACIÓN DE RESPUESTA (Groq) ──────────────────────────────────────────
SYSTEM_PROMPT = """Eres un ingeniero civil experto en normatividad colombiana de construcción.
Tu conocimiento abarca: NSR-10, NTC (normas técnicas colombianas),
Código Colombiano de Instalaciones Hidráulicas (NTC 1500),
Reglamentos de Seguridad Industrial (Res. 1409, 5018, Decreto 1072),
Licencias Urbanísticas (Res. 3232) y precios APU Barranquilla 2026.

INSTRUCCIONES:
1. Responde SOLO con base en el contexto normativo proporcionado.
2. SIEMPRE cita el código de la norma y el artículo/sección cuando corresponda.
3. Si hay múltiples normas relevantes, interconéctalas en tu respuesta.
4. Expresa valores técnicos con unidades (MPa, mm, %, m²).
5. Si el contexto no cubre la pregunta, indícalo claramente y sugiere qué norma consultar.
6. Cuando corresponda a APU, indica que la trazabilidad normativa ya está embebida en el motor APU.
7. Si un fragmento de contexto trae una advertencia "⚠️ NORMA DEROGADA/MODIFICADA",
   adviértelo explícitamente al inicio de tu respuesta y menciona cuál es la norma
   vigente que la reemplaza (si se indica). Nunca presentes contenido derogado
   como si fuera la norma vigente hoy — citarlo sin la advertencia induce a error
   normativo real al usuario.
"""


def _format_chunk_context(c: ChunkResult) -> str:
    """Antepone una advertencia visible cuando el chunk viene de una norma
    derogada/modificada (normas_registro.estado_vigencia vía search_knowledge) —
    así el LLM no puede citar texto muerto sin saber que lo es."""
    header = f"[{c.norma} — {c.seccion}]"
    if not c.vigente:
        aviso = f"⚠️ NORMA {(c.estado_vigencia or 'desconocido').upper().replace('_', ' ')}"
        if c.derogada_por:
            aviso += f" — reemplazada por {c.derogada_por}"
        header = f"{header}\n{aviso}"
    return f"{header}\n{c.contenido}"

def _generar_respuesta(contexto: str, question: str) -> str:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {question}"}
        ],
        temperature=0.1,
        max_tokens=1500,
    )
    return response.choices[0].message.content

def ask(question: str, norma_hint: Optional[str] = None, top_k: int = 6) -> dict:
    """
    RAG multi-norma completo.
    Retorna: {respuesta, fuentes, normas_citadas, chunks_usados}
    """
    # 1. Routing automático si no hay norma específica
    if norma_hint:
        target_normas = [norma_hint]
        chunks = search(question, norma_filter=norma_hint, top_k=top_k)
    else:
        target_normas = route_query(question)
        # Buscar en todas las normas relevantes en paralelo
        all_chunks: list[ChunkResult] = []
        seen_ids: set[str] = set()
        for norma in (target_normas or [None]):
            results = search(question, norma_filter=norma if target_normas else None, top_k=top_k)
            for c in results:
                if c.chunk_id not in seen_ids:
                    all_chunks.append(c)
                    seen_ids.add(c.chunk_id)
        # Ordenar por score y tomar top 2×top_k
        chunks = sorted(all_chunks, key=lambda x: x.score, reverse=True)[:top_k * 2]

    # 2. Construir contexto (con advertencia de vigencia por chunk cuando aplica)
    contexto = "\n\n---\n\n".join(_format_chunk_context(c) for c in chunks)

    # 3. Síntesis con Ollama local
    respuesta = _generar_respuesta(contexto, question)
    normas_citadas = list({c.norma for c in chunks})

    return {
        "respuesta": respuesta,
        "normas_citadas": normas_citadas,
        "normas_detectadas_router": target_normas,
        "fuentes": [
            {"norma": c.norma, "seccion": c.seccion, "score": round(c.score, 4)}
            for c in chunks
        ],
        "chunks_usados": len(chunks),
        "advertencias_vigencia": [
            {"norma": c.norma, "seccion": c.seccion, "estado_vigencia": c.estado_vigencia, "derogada_por": c.derogada_por}
            for c in chunks if not c.vigente
        ],
    }


# ─── AGENTE DELEGADOR — endpoint /consultar ──────────────────────────────────
MOTOR_LABEL = {
    "aquai": "AquAI (acueducto, alcantarillado y saneamiento — RAS 2000)",
    "geopot": "GeoPot (sísmica NSR-10 y laboratorio de suelos/concreto/agregados)",
    "vias": "motor-vías (diseño geométrico, pavimentos, mantenimiento vial — INVIAS)",
    "gerencia": "motor-gerencia (EVM y predicción de proyectos)",
}


def ask_delegado(question: str, top_k: int = 6) -> dict:
    """
    Punto de entrada único: detecta si la pregunta pertenece al dominio de un
    motor específico (aquai/geopot/vias/gerencia) o al RAG normativo general
    (NSR-10/NTC/seguridad industrial), busca en la fuente correcta y sintetiza
    con Groq. Esto es lo que expone /consultar en la API.
    """
    motor = route_motor(question)

    if motor:
        chunks = search(question, top_k=top_k, motor_filter=motor)
        if not chunks:
            # El dominio se detectó pero aún no tiene chunks cargados —
            # no fabricar respuesta, avisar y devolver dominio vacío en vez
            # de responder con contexto de otro dominio.
            return {
                "dominio": motor,
                "dominio_label": MOTOR_LABEL.get(motor, motor),
                "respuesta": (
                    f"La pregunta parece pertenecer al dominio {MOTOR_LABEL.get(motor, motor)}, "
                    "pero ese corpus todavía no tiene contenido cargado en motor_chunks. "
                    "No se genera una respuesta para evitar inventar información."
                ),
                "normas_citadas": [],
                "fuentes": [],
                "chunks_usados": 0,
            }
    else:
        result = ask(question, top_k=top_k)
        result["dominio"] = "normativa_general"
        result["dominio_label"] = "RAG normativo general (NSR-10 / NTC / seguridad industrial)"
        return result

    contexto = "\n\n---\n\n".join(_format_chunk_context(c) for c in chunks)
    respuesta = _generar_respuesta(contexto, question)

    return {
        "dominio": motor,
        "dominio_label": MOTOR_LABEL.get(motor, motor),
        "respuesta": respuesta,
        "normas_citadas": list({c.norma for c in chunks}),
        "fuentes": [
            {"norma": c.norma, "seccion": c.seccion, "score": round(c.score, 4)}
            for c in chunks
        ],
        "chunks_usados": len(chunks),
        "advertencias_vigencia": [
            {"norma": c.norma, "seccion": c.seccion, "estado_vigencia": c.estado_vigencia, "derogada_por": c.derogada_por}
            for c in chunks if not c.vigente
        ],
    }


# ─── USO DIRECTO ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "¿Qué resistencia mínima a la compresión deben tener los bloques para mampostería estructural?",
        "¿Cuáles son los requisitos del agua para preparar concreto en obra?",
        "¿Qué tipo de acero debo usar en Barranquilla para zona sísmica intermedia?",
        "¿Qué EPP necesito para trabajar en alturas en una obra de construcción?",
        "¿Cuánto debe asentarse el concreto para columnas y vigas?",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"❓ {q}")
        result = ask(q)
        print(f"\n📚 Normas: {', '.join(result['normas_citadas'])}")
        print(f"🔍 Router detectó: {result['normas_detectadas_router']}")
        print(f"\n📝 Respuesta:")
        print(result["respuesta"])
