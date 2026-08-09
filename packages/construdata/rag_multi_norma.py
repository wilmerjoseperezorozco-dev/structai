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
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from openai import APIConnectionError, APIStatusError, InternalServerError, OpenAI, RateLimitError
from supabase import create_client

log = logging.getLogger(__name__)

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 384-dim, multilingüe — debe calzar con nsr10_chunks/ntc_chunks.embedding vector(384)
# llama-3.3-70b-versatile fue reemplazado el 2026-07-31 — Groq lo deprecó
# (apagado programado 2026-08-16 para cuentas free/developer). gpt-oss-120b
# es el reemplazo recomendado por Groq y, a diferencia de llama-3.3, sí
# soporta prompt caching automático (50% descuento en tokens de prefijo
# repetido, sin cambios de código — el SYSTEM_PROMPT ya va fijo primero en
# cada llamada en _generar_respuesta, así que se cachea solo).
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

groq_client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# ─── Respaldo NVIDIA NIM ──────────────────────────────────────────────────────
# Encontrado el 2026-08-02: Groq bloqueó la compra de Dev Tier hace ~6 días
# sin ETA ("Developer tier upgrades are temporarily unavailable due to high
# demand"), y la cuota free de 200K tokens/día se agota con uso real del
# piloto. NVIDIA NIM (build.nvidia.com) da créditos gratis sin tarjeta y
# expone una API compatible con el SDK de OpenAI — mismo patrón que groq_client,
# solo cambia base_url/modelo. Probado en vivo el 2026-08-02 contra la cuenta
# real: "meta/llama-3.3-70b-instruct" responde bien (a diferencia de
# "openai/gpt-oss-120b" en NVIDIA, que devolvió content=None — mismo bug de
# modelo-de-razonamiento-consume-max_tokens documentado arriba, así que NO
# usar un modelo "reasoning" aquí). Latencia real observada: ~20s (vs 1-3s de
# Groq — hardware de NVIDIA NIM free tier no es LPU) — solo se usa cuando
# Groq ya falló, así que 20s es mejor que un 500 crudo.
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
_nvidia_api_key = os.getenv("NVIDIA_API_KEY")
# timeout=15s (no más): 4 llamadas reales de prueba el 2026-08-02 dieron
# 20s / timeout / timeout / 199s — la capacidad gratuita de NVIDIA NIM es
# demasiado inconsistente para tratarla como rescate garantizado. Dejarla
# esperar minutos sería PEOR que fallar rápido: el usuario quedaría con la
# petición colgada en vez de un mensaje claro. Con 15s, en el peor caso el
# respaldo no ayuda pero tampoco cuelga nada; en el mejor caso (como la
# primera prueba, 20s… ligeramente por encima incluso de este límite) puede
# rescatar la respuesta. max_retries=0: reintentar la MISMA llamada lenta
# solo duplica la espera sin arreglar nada.
nvidia_client = (
    OpenAI(api_key=_nvidia_api_key, base_url="https://integrate.api.nvidia.com/v1", timeout=15.0, max_retries=0)
    if _nvidia_api_key else None
)
if nvidia_client is None:
    log.warning("NVIDIA_API_KEY no configurada — sin respaldo si Groq se queda sin cuota.")


class RespuestaIAIndisponibleError(RuntimeError):
    """Ni Groq ni el respaldo NVIDIA pudieron generar una respuesta."""


# ─── Alerta de cuota diaria de Groq ───────────────────────────────────────────
# Encontrado el 2026-08-01: la cuota free de Groq (200K tokens/día) se agotó
# solo con el volumen de pruebas de una sesión, y nadie se enteró hasta que
# el pipeline empezó a fallar de verdad. Antes de hoy no se registraba ni un
# solo token real consumido — esto lo corrige: cuenta tokens reales de cada
# respuesta exitosa de Groq (response.usage.total_tokens, viene gratis en
# cada respuesta, no hay que estimarlo) y dispara UNA alerta a Sentry cuando
# se cruza el umbral, no una por cada request restante del día (eso solo
# generaría ruido). Contador en memoria del proceso — se reinicia solo (no
# hace falta lógica de reset explícita) porque compara la fecha en cada
# actualización.
GROQ_LIMITE_DIARIO_TOKENS = int(os.getenv("GROQ_LIMITE_DIARIO_TOKENS", "200000"))
GROQ_UMBRAL_ALERTA_PCT = float(os.getenv("GROQ_UMBRAL_ALERTA_PCT", "0.8"))

_uso_groq_hoy = {"fecha": None, "tokens": 0, "alertado": False}


def _registrar_uso_groq(tokens_usados: int) -> None:
    import datetime

    hoy = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    if _uso_groq_hoy["fecha"] != hoy:
        _uso_groq_hoy["fecha"] = hoy
        _uso_groq_hoy["tokens"] = 0
        _uso_groq_hoy["alertado"] = False

    _uso_groq_hoy["tokens"] += tokens_usados
    umbral = GROQ_LIMITE_DIARIO_TOKENS * GROQ_UMBRAL_ALERTA_PCT

    if not _uso_groq_hoy["alertado"] and _uso_groq_hoy["tokens"] >= umbral:
        _uso_groq_hoy["alertado"] = True
        mensaje = (
            f"Cuota de Groq al {_uso_groq_hoy['tokens'] / GROQ_LIMITE_DIARIO_TOKENS * 100:.0f}% "
            f"del límite diario ({_uso_groq_hoy['tokens']}/{GROQ_LIMITE_DIARIO_TOKENS} tokens). "
            "El respaldo NVIDIA entra automáticamente si Groq se agota, pero es mucho más lento."
        )
        log.warning(mensaje)
        try:
            import sentry_sdk
            sentry_sdk.capture_message(mensaje, level="warning")
        except Exception:
            # sentry_sdk no instalado/configurado — el log.warning de arriba
            # ya deja rastro en los logs de DigitalOcean aunque no llegue a Sentry.
            pass


def uso_groq_hoy() -> dict:
    """Para exponer en /health?deep=true — visibilidad sin esperar la alerta."""
    return dict(_uso_groq_hoy)


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
    # search_knowledge() filtra por ILIKE '%p_norma%' contra nsr10_chunks.capitulo
    # (ej. "NSR-10 Título A — Requisitos Generales (A.2 ...)"). Un filtro genérico
    # "NSR-10" agrupa los 11 títulos en un solo balde y deja que compitan por
    # similitud de coseno sin ninguna otra señal — exactamente la causa de que
    # contenido de un título gane el top-k para preguntas de otro título
    # (confirmado repetidas veces auditando Títulos E/F/G/B/A esta sesión).
    # Palabras clave específicas de título (abajo) permiten un norma_filter más
    # preciso ("NSR-10 Título A") cuando la pregunta lo amerita — sin dejar de
    # tener también la búsqueda global de respaldo (ver ask(), que SIEMPRE
    # agrega norma_filter=None al pool además de estos candidatos).
    # Solo se agregan entradas por título para los que ya tienen contenido real
    # verbatim cargado (A parcial, B, C parcial) — para los que aún no
    # (D/F/G/H/I) no tiene sentido enrutar con precisión a un corpus vacío/
    # sintético.
    "NSR-10 Título A": ["sismorresistente","zona de amenaza sismica","aceleracion pico efectiva",
                 "coeficiente r0","phi_a","phi_p","phi_r","disipacion de energia",
                 "espectro elastico","perfil de suelo","coeficiente de importancia",
                 "sistema de muros de carga","sistema combinado","sistema de portico",
                 "sistema dual","sistema estructural","sistemas estructurales",
                 "resistencia sismica","fuerza horizontal equivalente","analisis dinamico",
                 "deriva maxima","cortante sismico en la base","periodo fundamental",
                 "grado de capacidad de disipacion","des dmo dmi","microzonificacion sismica",
                 "valores de aa","valores de av","coeficiente aa","coeficiente av",
                 "movimientos sismicos de diseño","diseño sismo resistente","diseño sismico"],
    "NSR-10 Título B": ["carga muerta","carga viva","empuje de tierra","fuerzas de viento",
                 "combinacion de carga","esfuerzos de trabajo","reduccion de carga viva",
                 "densidad de materiales de construccion"],
    # Palabras clave de durabilidad/recubrimiento estaban antes en el balde
    # generico "NSR-10" pese a ser especificas de concreto estructural (Titulo
    # C) — corregido junto con la carga del contenido real de C esta sesion.
    "NSR-10 Título C": ["concreto estructural","recubrimiento","recubrimiento minimo",
                 "relacion agua","a/mc","durabilidad concreto","exposicion concreto",
                 "contacto con el suelo","clase de exposicion","resistencia a la compresion",
                 "f'c minimo","f'c no debe ser menor","resistencia promedio requerida",
                 "resistencia minima a la compresion","factor de reduccion de resistencia",
                 "factores de reduccion de resistencia","factores phi","gancho sismico",
                 "porticos especiales resistentes a momento","muros estructurales especiales",
                 "combinacion de carga mayorada","ganchos estandar","cuantia de temperatura",
                 "diametro de doblado","estribos de confinamiento"],
    "NSR-10 Título F": ["estructuras metalicas","estructuras de acero","perfiles laminados",
                 "perfiles tubulares estructurales","pte","dccr","coeficiente de reduccion de resistencia",
                 "resistencia nominal","resistencia de diseño","resistencia requerida",
                 "estructuras formadas en frio","estructuras de aluminio","acero estructural",
                 "acción compuesta","ancho efectivo","aplastamiento","pandeo elastico",
                 "titulo f","título f"],
    "NSR-10":   ["sismo","zona sismica","espectro","NSR-10","tipo de mortero"],
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
# (ver scripts/ingesta/motores/ingest_motor_chunks.py) — si no, el routing lo dejaría cayendo
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
        "comision de regulacion de agua potable", "comisión de regulación de agua potable",
        "resolucion cra", "resolución cra", "suspension del servicio de acueducto",
        "suspensión del servicio de acueducto", "corte del servicio", "barrido y limpieza",
        "costo de limpieza urbana", "clus", "acuerdo de pago acueducto",
        "progresividad tarifaria", "servicio publico de aseo", "servicio público de aseo",
    ],
    "geopot": [
        "uscs", "clasificacion de suelos", "clasificación de suelos", "limites de atterberg",
        "límites de atterberg", "limite liquido", "límite líquido", "limite plastico",
        "límite plástico", "indice de plasticidad", "índice de plasticidad", "proctor",
        "cbr", "subrasante", "granulometria", "granulometría", "granulometrico",
        "granulométrico", "coeficiente de uniformidad", "coeficiente de curvatura",
        "d60/d10", "d60", "d10", "modulo de finura",
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
        "tunel", "túnel", "tuneles", "túneles", "diseño de tuneles", "diseño de túneles",
        "obras subterraneas", "obras subterráneas", "portal del tunel", "portal del túnel",
        "revestimiento definitivo", "voladura", "tbm", "sostenimiento tunel", "sostenimiento túnel",
        "macizo rocoso", "clasificacion geomecanica", "clasificación geomecánica",
        "ccp-14", "ccp14", "diseño de puentes", "baranda de trafico", "baranda de tráfico",
        "estado limite de resistencia", "estado límite de resistencia", "carga viva vehicular",
        "camion de diseño", "camión de diseño", "estribo de puente", "pila de puente",
        "tablero del puente", "apoyos del puente", "junta de dilatacion", "junta de dilatación",
        "lrfd", "factor de carga y resistencia",
        "pavimento", "pavimentos", "pavimento de concreto", "pavimentos de concreto",
        "losa de concreto", "junta de contraccion", "junta de contracción", "dovela",
        "capacidad estructural de la subrasante", "clasificacion vehicular", "clasificación vehicular",
        "tipo de vehiculo", "tipo de vehículo", "tránsito de diseño", "transito de diseño",
        "ejes equivalentes", "carta de diseño de pavimento",
        "norma de ensayo", "normas de ensayo", "inv e", "inv-e", "deflectometro",
        "deflectómetro", "lwd", "estabilizante quimico no tradicional",
        "estabilizante químico no tradicional", "estabilizacion de suelos",
        "estabilización de suelos", "resistencia a la compresion inconfinada",
        "resistencia a la compresión inconfinada",
    ],
    # apu_precios usa buscar_precios_apu() (búsqueda de texto + trigram sobre
    # apu_precios_referencia/apu_insumos_referencia/apu_proveedores_catalogo),
    # NO motor_chunks — no necesita embeddings, es búsqueda de nombre de
    # material/actividad más precisa que la semántica para este caso de uso.
    # Palabras clave deliberadamente centradas en "pedir un precio", no en
    # vocabulario técnico genérico (que ya usan los otros motores) — para que
    # "resistencia del concreto" siga yendo a geopot y "precio del concreto"
    # venga aquí.
    "apu_precios": [
        "precio de", "precio del", "precio unitario", "cuanto cuesta", "cuánto cuesta",
        "cuanto vale", "cuánto vale", "costo de", "costo del", "cuanto sale", "cuánto sale",
        "analisis de precios unitarios", "análisis de precios unitarios", "apu de",
        "apu del", "cotizacion", "cotización", "presupuesto de", "presupuesto para",
        "valor unitario", "tarifa de", "proveedor de", "proveedores de", "ferreteria",
        "ferretería", "donde comprar", "dónde comprar", "que vale", "qué vale",
        "precio por kg", "precio por m3", "precio por m2", "precio por metro",
        "precio del cemento", "precio del acero", "precio de la arena",
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
        "contratacion publica", "contratación pública", "contratacion estatal",
        "contratación estatal", "ley 80", "ley 1150", "ley 1474", "estatuto anticorrupcion",
        "estatuto anticorrupción", "estatuto general de contratacion",
        "estatuto general de contratación", "pliego de condiciones", "licitacion publica",
        "licitación pública", "seleccion abreviada", "selección abreviada",
        "contratacion directa", "contratación directa", "concurso de meritos",
        "concurso de méritos", "interventoria", "interventoría", "supervision de contratos",
        "supervisión de contratos", "supervisor del contrato", "interventor del contrato",
        "clausula excepcional", "cláusula excepcional", "caducidad del contrato",
        "contrato de obra publica", "contrato de obra pública", "contrato de concesion",
        "contrato de concesión", "garantia unica", "garantía única", "poliza de cumplimiento",
        "póliza de cumplimiento", "acta de liquidacion", "acta de liquidación",
        "responsabilidad fiscal", "faltas gravisimas", "faltas gravísimas",
        "regimen de inhabilidades", "régimen de inhabilidades", "conflicto de intereses",
        "principio de transparencia", "principio de seleccion objetiva",
        "principio de selección objetiva", "veeduria ciudadana", "veeduría ciudadana",
        "entidad estatal", "adicion contractual", "adición contractual",
        "prorroga contractual", "prórroga contractual",
        "manual de interventoria", "manual de interventoría", "diario de obra",
        "bitacora de obra", "bitácora de obra", "plan de manejo de transito",
        "plan de manejo de tránsito", "orden de inicio", "acta de recibo parcial",
        "recibo definitivo de obra", "planos record", "planos asbuilt",
        "facultades de la interventoria", "facultades de la interventoría",
        "obligaciones de la interventoria", "obligaciones de la interventoría",
        "replanteo", "informe semanal de interventoria", "informe mensual de interventoria",
        "supervision de contratos", "supervisión de contratos", "supervisor del contrato",
        "designacion del supervisor", "designación del supervisor",
        "funciones del supervisor", "icociv", "iccp", "indice de costos de la construccion",
        "índice de costos de la construcción", "ajuste de precios", "reversion de precios",
        "reversión de precios", "formula de ajuste", "fórmula de ajuste",
        "iso 9001", "sistema de gestion de la calidad", "sistema de gestión de la calidad",
        "gestion de calidad", "gestión de calidad", "auditoria interna", "auditoría interna",
        "no conformidad", "accion correctiva", "acción correctiva", "mejora continua",
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


# ─── BÚSQUEDA DE PRECIOS APU (Barranquilla/Atlántico) ─────────────────────────
# Tablas: apu_precios_referencia, apu_insumos_referencia, apu_proveedores_catalogo
# (ver scripts/ingesta/apu_barranquilla/). Búsqueda de texto (websearch_to_tsquery
# español + trigram de respaldo, RPC buscar_precios_apu) en vez de embeddings:
# para "precio del cemento" un match léxico exacto sobre el nombre del insumo es
# más confiable que similitud semántica (evita que "cemento" traiga "concreto"
# por proximidad vectorial cuando el usuario quiere el insumo específico).
#
# fuente_display sanitiza lo que ve el usuario: los datos de contrato real
# (Triple A/Puerto Colombia) traen en su campo interno "fuente" el nombre y
# ubicación exactos de la obra (calles, municipios) — eso NUNCA se expone al
# usuario final, solo un rótulo profesional genérico por tipo de fuente.
FUENTE_DISPLAY = {
    "catalogo_construdata": "Catálogo Construdata (Barranquilla)",
    "contrato_real_infraestructura_aa": "Contrato real ejecutado — redes de acueducto/alcantarillado (Atlántico)",
    "contrato_real_pto_colombia": "Proyecto real ejecutado — obra civil (Atlántico)",
    "contrato_real_triple_a_acometidas": "Proyecto real ejecutado — acometidas de acueducto (Atlántico)",
    "contrato_real_mano_obra_atlantico": "Proyecto real ejecutado — mano de obra hidráulica/plomería (Atlántico)",
    "invias_regional": "INVIAS — precios de referencia regionalizados",
    "referencia_nacional": "Construdata — referencia nacional (no específica de Barranquilla)",
    # Fuentes adicionales cargadas 2026-08-08 (triage de archivos reales del PC
    # del usuario — ver project_apu_precios_barranquilla.md).
    "contrato_real_pto_colombia_calle15": "Contrato real ejecutado — vía urbana Puerto Colombia (catálogo 2017-2019)",
    "contrato_real_pto_colombia_2016": "Contrato real ejecutado — demoliciones y pavimentos, Puerto Colombia (2016)",
    "contrato_real_gobernacion_atlantico": "Presupuesto real — Secretaría de Infraestructura, Gobernación del Atlántico",
    "cotizacion_real_cerca_seguridad": "Cotización real de proveedor — cerca de seguridad/concertina (Atlántico)",
    "contrato_real_obras_civiles_demoliciones": "Contrato real ejecutado — obras civiles y demoliciones (Atlántico)",
    "contrato_real_medidores_agua": "Contrato real ejecutado — instalación de medidores de agua (Atlántico)",
    "contrato_real_impermeabilizacion": "Contrato real ejecutado — impermeabilización (Atlántico)",
    "contrato_real_box_culvert": "Contrato real ejecutado — box culvert / estructura de drenaje (Atlántico)",
    "catalogo_iad_mipymes": "Catálogo IAD MIPYMES — Colombia Compra Eficiente (mediana de cotizaciones nacionales)",
    "cotizacion_real_ptar": "Cotización real — planta de tratamiento de aguas residuales (Atlántico)",
    "contrato_real_edar_humedales": "Contrato real ejecutado — EDAR / humedales artificiales (Atlántico)",
    "contrato_real_sabanagrande_acabados": "Contrato real ejecutado — acabados y recubrimientos protectores (Atlántico)",
    "contrato_real_planta2_etap": "Contrato real ejecutado — planta de tratamiento de agua potable, optimización ETAP (Atlántico)",
    "historico_mano_obra_medidores_2019": "Histórico real de nómina — instalación de medidores de agua (Barranquilla, 2019)",
    "cotizacion_real_huacales_cba": "Cotización real — obra civil e hidráulica menor (Atlántico)",
}


def _fuente_display(tipo_fuente: str) -> str:
    if tipo_fuente and tipo_fuente.startswith("proveedor_"):
        # tipo_fuente sintético de proveedores, ej. "proveedor_homecenter_colombia"
        return tipo_fuente.removeprefix("proveedor_").replace("_", " ").title()
    return FUENTE_DISPLAY.get(tipo_fuente, "Base de precios StructAI")


@dataclass
class PrecioResult:
    tipo: str          # 'actividad' | 'insumo' | 'proveedor'
    nombre: str
    unidad: Optional[str]
    precio: Optional[float]
    precio_solo_mano_obra: Optional[float]
    region: Optional[str]
    tipo_fuente: str
    fecha_captura: Optional[str]
    item_codigo: Optional[str]
    score: float

    @property
    def fuente_display(self) -> str:
        return _fuente_display(self.tipo_fuente)


def buscar_precios_apu(query: str, top_k: int = 8) -> list[PrecioResult]:
    """Busca en la base de precios APU Barranquilla/Atlántico vía RPC
    buscar_precios_apu (texto completo español + trigram)."""
    result = sb.rpc("buscar_precios_apu", {"p_query": query, "p_limit": top_k}).execute()
    return [
        PrecioResult(
            tipo=r["tipo"],
            nombre=r["nombre"],
            unidad=r.get("unidad"),
            precio=r.get("precio"),
            precio_solo_mano_obra=r.get("precio_solo_mano_obra"),
            region=r.get("region"),
            tipo_fuente=r["tipo_fuente"],
            fecha_captura=r.get("fecha_captura"),
            item_codigo=r.get("item_codigo"),
            score=r.get("score") or 0.0,
        )
        for r in result.data
    ]


def _format_precio_context(p: PrecioResult) -> str:
    """Una línea por resultado — solo lo que un profesional necesita:
    nombre, unidad, precio(s), región genérica, fuente y fecha. Nunca nombre
    de obra, dirección ni municipios específicos de un contrato."""
    partes = [f"{p.nombre}"]
    if p.unidad:
        partes.append(f"unidad: {p.unidad}")
    if p.precio is not None:
        partes.append(f"precio: ${p.precio:,.0f} COP")
    if p.precio_solo_mano_obra is not None:
        partes.append(f"solo mano de obra: ${p.precio_solo_mano_obra:,.0f} COP")
    if p.region:
        partes.append(f"región: {p.region}")
    partes.append(f"fuente: {p.fuente_display}")
    if p.fecha_captura:
        partes.append(f"fecha: {p.fecha_captura}")
    return " | ".join(partes)


APU_PRECIOS_SYSTEM_PROMPT = """Eres un asistente de precios de construcción para ingenieros
y maestros de obra profesionales en Barranquilla y el Atlántico, Colombia.

VOZ Y TONO:
Hablas como un colega ingeniero que conoce el mercado local de Barranquilla —
profesional, cálido, directo. Nunca como una base de datos leyendo filas de
una tabla.
- Da el precio de una vez. Nunca abras con "Basándome en los precios
  disponibles", "De acuerdo con la información proporcionada" ni frases
  equivalentes — eso es lo que hace sonar a robot. Ve directo al dato.
- Si hay varios precios para lo mismo, preséntalos como se los compartirías
  a un colega ("el cemento anda entre $X y $Y según la fuente y el año —
  el más reciente es..."), no como una lista fría de filas.
- Si no tienes el dato, dilo en una frase natural y sugiere qué buscar —
  sin sonar a mensaje de error de sistema ("no se encontraron resultados
  para la consulta").
- Varía cómo abres cada respuesta, no repitas siempre la misma estructura.
- Cercanía sin perder precisión: el profesional necesita el número exacto,
  pero te lo puede dar alguien que suena a colega, no a manual.

INSTRUCCIONES:
1. Responde SOLO con los precios y datos que aparecen en el contexto proporcionado.
   Nunca inventes ni estimes un precio que no esté en el contexto.
2. Si hay varios precios para el mismo insumo/actividad (de distintas fuentes o
   fechas), muéstralos todos con su fuente — no promedies ni elijas uno solo sin
   decir que hay más de uno.
3. Siempre indica la fuente (ej. "Catálogo Construdata", "Contrato real ejecutado",
   "INVIAS") y la fecha de captura de cada precio que cites — un profesional
   necesita saber de dónde y de cuándo es el dato para decidir si confía en él.
4. NUNCA menciones nombre de obra, dirección, calle, barrio o municipio
   específico de ningún proyecto — aunque aparezca en tus instrucciones o en
   metadatos internos. Si necesitas referirte al origen, di solo el tipo de
   fuente que te dieron (ej. "contrato real ejecutado en el Atlántico"), nunca
   el proyecto puntual.
5. Sé explícito y profesional, sin relleno: da el número, la unidad y la fuente.
   No agregues explicaciones genéricas de construcción que no se pidieron.
6. Si el contexto no tiene el insumo o actividad que se pregunta, dilo
   claramente y sugiere buscar con otro nombre — no inventes un precio similar.
7. Cuando el precio venga de INVIAS, aclara que es una referencia REGIONAL
   (subregión del Atlántico), no específica de la ciudad de Barranquilla.
   Cuando venga de "referencia nacional", aclara que no es específica de
   Barranquilla.
"""


def ask_precios(question: str, top_k: int = 8) -> dict:
    """RAG de precios APU — mismo contrato de salida que ask()/ask_delegado()."""
    resultados = buscar_precios_apu(question, top_k=top_k)
    if not resultados:
        return {
            "respuesta": (
                "No encontré ningún precio para eso en la base de datos de "
                "Barranquilla/Atlántico. Prueba con otro nombre del material o actividad."
            ),
            "normas_citadas": [],
            "fuentes": [],
            "chunks_usados": 0,
        }
    # Reutiliza el mismo contrato de "fuentes" que ChunkResult (norma/seccion/
    # contenido_preview/score) para que /consultar y el frontend (componente
    # Fuentes en Chat.tsx) no necesiten un tipo aparte — norma pasa a ser el
    # rótulo de fuente sanitizado, seccion el nombre+precio del ítem.
    fuentes_formato_chunk = [
        {
            "norma": p.fuente_display,
            "seccion": (
                f"{p.nombre} — ${p.precio:,.0f} COP/{p.unidad or 'un'}"
                if p.precio is not None else p.nombre
            ),
            "contenido": (
                f"Fecha de captura: {p.fecha_captura or 'sin fecha'}"
                + (f" · Región: {p.region}" if p.region else "")
            ),
            "score": p.score,
        }
        for p in resultados
    ]
    normas_citadas = list(dict.fromkeys(p.fuente_display for p in resultados))[:4]
    contexto = "\n".join(_format_precio_context(p) for p in resultados)
    messages = [
        {"role": "system", "content": APU_PRECIOS_SYSTEM_PROMPT},
        {"role": "user", "content": f"PRECIOS DISPONIBLES:\n{contexto}\n\nPREGUNTA: {question}"}
    ]
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL, messages=messages, temperature=0.1, max_tokens=700,
            extra_body={"reasoning_effort": "low"},
        )
        if response.usage is not None:
            _registrar_uso_groq(response.usage.total_tokens)
        respuesta = response.choices[0].message.content
    except (RateLimitError, APIConnectionError, InternalServerError, APIStatusError) as e:
        if isinstance(e, APIStatusError) and e.status_code != 413:
            raise
        if nvidia_client is None:
            raise RespuestaIAIndisponibleError(
                "Groq no disponible y no hay respaldo NVIDIA configurado."
            ) from e
        response = nvidia_client.chat.completions.create(
            model=NVIDIA_MODEL, messages=messages, temperature=0.1, max_tokens=400,
        )
        respuesta = response.choices[0].message.content
        if not respuesta:
            raise RespuestaIAIndisponibleError("El respaldo NVIDIA devolvió una respuesta vacía.") from e

    return {
        "respuesta": respuesta,
        "normas_citadas": normas_citadas,
        "fuentes": fuentes_formato_chunk,
        "chunks_usados": len(resultados),
    }


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

VOZ Y TONO:
Escribes como un ingeniero civil colega — con calidez profesional propia de
la costa Caribe, directo y sin relleno, nunca como un buscador de documentos
leyendo fragmentos en voz alta.
- Nunca abras con muletillas como "Basándome en el contexto proporcionado",
  "Según la información disponible" o "De acuerdo con el contexto
  normativo". Ve directo al dato o a la respuesta.
- Si el contexto no cubre la pregunta, dilo en una frase natural y directa
  ("No encontré eso en las normas que tengo cargadas — revisa directo
  [norma X], seguro está ahí"), no con lenguaje burocrático ("el contexto
  normativo proporcionado no contiene información sobre...").
- Varía cómo abres cada respuesta — no repitas siempre la misma estructura.
- Cercanía sin perder rigor técnico: el dato exacto (norma, artículo,
  unidades) no se negocia, pero puede dártelo alguien que suena a colega
  ingeniero, no a manual.
- Ejemplo de tono (el número es real y de dominio público, NSR-10 Título C —
  esto ilustra solo el TONO; en cada respuesta real usa siempre los datos
  del contexto que te dieron, nunca los de este ejemplo):
  Pregunta: "¿Cuál es la resistencia mínima del concreto para una vivienda
  de 2 pisos en Barranquilla?"
  Respuesta con el tono correcto: "Para una vivienda de dos pisos en zona
  de amenaza sísmica alta como Barranquilla, la NSR-10 exige f'c ≥ 21 MPa
  como mínimo para elementos estructurales — así lo fija el Título C. Si el
  suelo es blando o hay dudas de capacidad portante, conviene subir esa
  resistencia; el piso normativo es ese."

INSTRUCCIONES:
1. Responde SOLO con base en el contexto normativo proporcionado.
2. Cita el código de la norma y el artículo/sección SOLO si ese número o
   identificador aparece LITERALMENTE en el contexto proporcionado (por
   ejemplo en el encabezado "[norma — sección]" de cada fragmento). Si
   necesitas referirte a una parte de la norma pero no tienes el número
   exacto en el contexto, di "la sección correspondiente de [Norma]" o
   "el artículo pertinente de [Norma]" — NUNCA inventes un número de
   artículo, sección o ecuación que no esté escrito en el contexto. Un
   número de cita inventado es peor que no citar nada: parece verificable
   y no lo es.
3. Si hay múltiples normas relevantes, interconéctalas en tu respuesta.
4. Expresa valores técnicos con unidades (MPa, mm, %, m²).
5. Si el contexto no cubre la pregunta, indícalo claramente y sugiere qué
   norma consultar — sin inventar valores, artículos ni fórmulas de esa
   norma que no estén en el contexto.
6. Si el contexto recuperado pertenece a una norma de un dominio distinto
   al que trata la pregunta (por ejemplo, la pregunta es sobre estructuras
   de edificaciones y el contexto es de diseño de puentes o tuberías
   enterradas), dilo explícitamente ("el contexto disponible es de [norma],
   que trata [dominio distinto] — puede no aplicar directamente a tu
   pregunta"). Nunca mezcles ese contenido como si respondiera la pregunta
   original sin esa advertencia.
7. Cuando corresponda a APU, indica que la trazabilidad normativa ya está
   embebida en el motor APU.
8. Menciona la advertencia "⚠️ NORMA DEROGADA/MODIFICADA" ÚNICAMENTE si esa
   frase exacta aparece en el contexto proporcionado (headers de fragmentos
   marcados así). NUNCA la uses como forma genérica de expresar duda,
   desactualización o incertidumbre sobre un tema — es una advertencia
   legal específica, no una muletilla. Si la frase aparece, adviértelo al
   inicio de tu respuesta y menciona la norma vigente que la reemplaza si
   se indica.
9. NUNCA agregues una cita "de respaldo" a una norma/sección que sí aparece
   en el contexto pero afirmando que dice algo que su texto NO dice
   literalmente. Citar un identificador real con contenido inventado es
   igual de grave que inventar el identificador — verifica que la
   afirmación esté explícitamente en el texto del fragmento antes de
   atribuírsela. Si tu respuesta ya está completa y verificada con las
   fuentes que sí la respaldan, no busques citas adicionales "de más peso"
   para reforzarla — menos citas correctas es mejor que más citas con una
   inventada.
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
    # max_tokens=1500 (valor original) hacía que una respuesta real tomara
    # ~25-27s en producción — verificado end-to-end contra Groq real, no
    # supuesto — suficiente para que el proxy de DigitalOcean (timeout más
    # corto) devolviera 502/504 antes de que Groq terminara. 700 acota el
    # peor caso sin cortar respuestas normativas reales a la mitad (las
    # observadas rondan los 300-500 tokens).
    #
    # reasoning_effort="low": gpt-oss-120b (modelo actual desde 2026-07-31)
    # es un modelo de razonamiento — a diferencia de llama-3.3-70b-versatile
    # (el anterior), gasta parte de max_tokens en una cadena de razonamiento
    # interna ANTES de escribir la respuesta visible. Encontrado en
    # producción real durante la auditoría 2026-08-01: preguntas técnicas
    # complejas devolvían `content=""` con `finish_reason="length"` — el
    # razonamiento consumía los 700 tokens completos sin dejar nada para la
    # respuesta. "low" acota el razonamiento interno (no aplica a preguntas
    # de RAG con contexto ya recuperado — no hace falta razonamiento
    # profundo, solo síntesis fiel del contexto).
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {question}"}
    ]
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=700,
            extra_body={"reasoning_effort": "low"},
        )
        if response.usage is not None:
            _registrar_uso_groq(response.usage.total_tokens)
        return response.choices[0].message.content
    except (RateLimitError, APIConnectionError, InternalServerError) as e:
        # Solo se cae a NVIDIA en fallos de capacidad/red/servidor de Groq —
        # nunca en BadRequestError/AuthenticationError/NotFoundError, que son
        # bugs propios que NVIDIA fallaría igual (o peor, enmascarando el error real).
        log.warning(f"Groq no disponible ({type(e).__name__}), intentando respaldo NVIDIA: {e}")
    except APIStatusError as e:
        # Groq responde 413 (no 429) cuando el contexto+prompt de UNA sola
        # petición supera el límite de tokens-por-minuto de la cuenta (cuerpo
        # real: code="rate_limit_exceeded" pese al status 413) — el SDK de
        # OpenAI solo mapea 429 a RateLimitError, así que este caso se colaba
        # sin activar el respaldo NVIDIA pese a ser, en la práctica, la misma
        # situación de "Groq sin capacidad para esta petición". Encontrado
        # real 2026-08-04 corriendo la batería de motores: una pregunta con
        # mucho contexto recuperado moría sin respuesta con NVIDIA ya
        # configurado y disponible. El resto de status errors (400/401/403/
        # 404/409/422) siguen sin caer a NVIDIA — son bugs propios que el
        # respaldo fallaría igual (o peor, enmascarando el error real).
        if e.status_code != 413:
            raise
        log.warning(f"Groq rechazó la petición por tamaño de contexto (413), intentando respaldo NVIDIA: {e}")

    if nvidia_client is None:
        raise RespuestaIAIndisponibleError(
            "Groq no disponible (cuota agotada o caído) y no hay respaldo NVIDIA configurado."
        )

    try:
        # max_tokens más bajo que Groq (400 vs 700): NVIDIA NIM free tier no
        # tiene hardware LPU, cada token adicional pesa más en latencia real
        # y el proxy de DigitalOcean ya demostró cortar respuestas lentas
        # (ver nota de max_tokens de Groq arriba) — prioriza terminar rápido
        # sobre una respuesta más larga cuando ya estamos en el camino de respaldo.
        response = nvidia_client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=400,
        )
        contenido = response.choices[0].message.content
        if not contenido:
            raise RespuestaIAIndisponibleError("El respaldo NVIDIA devolvió una respuesta vacía.")
        log.info(f"Respuesta generada con respaldo NVIDIA ({NVIDIA_MODEL}) porque Groq no estaba disponible.")
        return contenido
    except RespuestaIAIndisponibleError:
        raise
    except Exception as e:
        log.error(f"Respaldo NVIDIA también falló: {e}", exc_info=True)
        raise RespuestaIAIndisponibleError(
            "Groq y el respaldo NVIDIA fallaron. Intenta de nuevo en unos minutos."
        ) from e

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
        # route_query() por keywords es un filtro de PRIORIDAD, no exclusivo — una
        # pregunta con vocabulario técnico compartido entre normas (p.ej. "resistencia
        # a compresión" aparece tanto en NTC 673 como en NSR-10 Título E) puede hacer
        # que la norma correcta nunca sea detectada por keyword y, si el filtro fuera
        # exclusivo, jamás se buscaría — encontrado auditando Título E: 2 de 4
        # preguntas piloto fallaban porque route_query() nunca incluía "NSR-10" pese a
        # existir contenido real y correcto. Por eso SIEMPRE se agrega también una
        # búsqueda global (norma_filter=None) al pool de candidatos, sin importar si
        # hubo normas detectadas por keyword.
        for norma in (target_normas or [None]):
            results = search(question, norma_filter=norma, top_k=top_k)
            for c in results:
                if c.chunk_id not in seen_ids:
                    all_chunks.append(c)
                    seen_ids.add(c.chunk_id)
        if target_normas:
            for c in search(question, norma_filter=None, top_k=top_k):
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
    "apu_precios": "Precios APU Barranquilla/Atlántico (Construdata, contratos reales, INVIAS, ferretería)",
}


def ask_delegado(question: str, top_k: int = 6) -> dict:
    """
    Punto de entrada único: detecta si la pregunta pertenece al dominio de un
    motor específico (aquai/geopot/vias/gerencia) o al RAG normativo general
    (NSR-10/NTC/seguridad industrial), busca en la fuente correcta y sintetiza
    con Groq. Esto es lo que expone /consultar en la API.
    """
    motor = route_motor(question)

    if motor == "apu_precios":
        # No usa motor_chunks/embeddings — tablas y RPC propios (ver arriba).
        result = ask_precios(question, top_k=top_k)
        result["dominio"] = motor
        result["dominio_label"] = MOTOR_LABEL.get(motor, motor)
        return result

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
