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
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from openai import APIConnectionError, APIStatusError, InternalServerError, OpenAI, RateLimitError
from supabase import create_client

import sgc_amenaza_sismica
import sgc_movimientos_masa
import igac_client
import ideam_client
import noticias_colombia

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

# ─── Respaldo NVIDIA NIM — RETIRADO el 2026-08-20 ─────────────────────────────
# Se probó del 2026-08-02 al 2026-08-20 como segundo nivel de respaldo. Se
# retira por decisión explícita del usuario: la latencia real (20s a 199s en
# pruebas reales, hardware free tier no es LPU) hacía que la app se quedara
# "colgada" en vez de responder rápido, y ya existe un respaldo mejor y
# pagado (OpenAI, ver abajo) que no tiene ese problema de inconsistencia.
# Dos niveles (Groq -> OpenAI) son más simples de operar y más predecibles
# que tres. Si se necesita reactivar, el código completo está en el
# historial de git (commit anterior a este cambio).

# ─── Respaldo OpenAI (segundo nivel) ──────────────────────────────────────────
# Agregado 2026-08-20: Groq se agota casi a diario con el volumen real del
# piloto (200K TPD, confirmado agotado múltiples veces en la misma sesión).
# El usuario financia esto con crédito propio de OpenAI ($9, comprado
# explícitamente para este uso). gpt-4o-mini (no gpt-4o): basta para
# síntesis fiel de un contexto RAG ya recuperado -- no requiere razonamiento
# profundo -- y es ~15x más barato que gpt-4o, así que $9 rinde meses de uso
# ocasional como respaldo, no como motor principal.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = (
    OpenAI(api_key=_openai_api_key, timeout=20.0, max_retries=0)
    if _openai_api_key else None
)
if openai_client is None:
    log.warning("OPENAI_API_KEY no configurada — sin tercer respaldo si Groq y NVIDIA fallan.")


def _llamar_llm_con_respaldo(messages: list, max_tokens_groq: int = 700) -> str:
    """Intenta Groq, luego OpenAI, en ese orden -- el respaldo solo se
    prueba si Groq falló por capacidad/red/tamaño (nunca por un bug propio
    como 400/401/403/404/422, que el respaldo fallaría igual o peor,
    enmascarando el error real). Usado por _generar_respuesta() y
    ask_precios() -- unificado aquí para no duplicar la lógica en dos
    sitios. Lanza RespuestaIAIndisponibleError solo si ambos fallan o
    OpenAI no está configurado."""
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL, messages=messages, temperature=0.1,
            max_tokens=max_tokens_groq, extra_body={"reasoning_effort": "low"},
        )
        if response.usage is not None:
            _registrar_uso_groq(response.usage.total_tokens)
        contenido = response.choices[0].message.content
        if contenido:
            return contenido
        log.warning("Groq devolvió respuesta vacía, intentando respaldo OpenAI.")
    except (RateLimitError, APIConnectionError, InternalServerError) as e:
        log.warning(f"Groq no disponible ({type(e).__name__}), intentando respaldo OpenAI: {e}")
    except APIStatusError as e:
        if e.status_code != 413:
            raise
        log.warning(f"Groq rechazó la petición por tamaño de contexto (413), intentando respaldo OpenAI: {e}")

    if openai_client is not None:
        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL, messages=messages, temperature=0.1, max_tokens=500,
            )
            contenido = response.choices[0].message.content
            if contenido:
                log.info(f"Respuesta generada con respaldo OpenAI ({OPENAI_MODEL}) porque Groq no estaba disponible.")
                return contenido
        except Exception as e:
            log.error(f"Respaldo OpenAI también falló: {e}", exc_info=True)

    raise RespuestaIAIndisponibleError(
        "Groq y el respaldo OpenAI no pudieron generar una respuesta. Intenta de nuevo en unos minutos."
    )


class RespuestaIAIndisponibleError(RuntimeError):
    """Ni Groq ni el respaldo OpenAI pudieron generar una respuesta."""


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
            "El respaldo OpenAI entra automáticamente si Groq se agota."
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


def _score_motores(query: str) -> dict[str, int]:
    q = query.lower()
    scores: dict[str, int] = {}
    for motor, keywords in MOTOR_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in q:
                scores[motor] = scores.get(motor, 0) + (2 if len(kw) > 10 else 1)
    return scores


def route_motor(query: str) -> Optional[str]:
    """Detecta si la pregunta pertenece al dominio de un motor específico
    (aquai, geopot, vias, gerencia...) en vez del RAG normativo general."""
    scores = _score_motores(query)
    if not scores:
        return None
    return max(scores.items(), key=lambda x: x[1])[0]


def route_motores_multiples(query: str) -> list[str]:
    """Como route_motor() pero devuelve TODOS los dominios con score > 0,
    ordenados de mayor a menor. Detecta preguntas compuestas — ej. "precio
    del cemento + qué es la dotación neta" — que antes se enrutaban
    completas a un solo dominio (el de mayor score) y perdían la otra mitad
    de la pregunta aunque el dato sí existiera. Bug real encontrado
    2026-08-09 con captura de pantalla del usuario: "dotación neta" (3 pts
    en aquai) le ganaba a "precio de" (1 pt en apu_precios), y la respuesta
    de precio de cemento se perdía por completo pese a estar en la base."""
    scores = _score_motores(query)
    return [m for m, _ in sorted(scores.items(), key=lambda x: -x[1])]


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
    # Granularidad de proveedor individual del mismo catálogo IAD MIPYMES,
    # cargada 2026-08-20 (apu_proveedores_nacional/apu_items_nacional/
    # apu_precios_nacional_detalle) — antes solo existía la mediana de
    # arriba, sin poder decir qué proveedor concreto tenía el mejor precio.
    "catalogo_iad_mipymes_detalle": "Catálogo IAD MIPYMES — Colombia Compra Eficiente (proveedor real con el mejor precio, de 78 proveedores mipyme nacionales)",
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
    categoria_fuente: Optional[str]
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
            categoria_fuente=r.get("categoria_fuente"),
            score=r.get("score") or 0.0,
        )
        for r in result.data
    ]


_INVIAS_UBICACIONES_CACHE: list[dict] | None = None


def _cargar_ubicaciones_invias() -> list[dict]:
    """Carga (una sola vez por proceso) el catálogo de provincias/departamentos
    de INVIAS para poder detectar menciones de ubicación en la pregunta.
    Ordenado por longitud de nombre descendente para que un match de
    provincia específica ("Ariari") se intente antes que uno de departamento
    ("Meta") si el texto contuviera ambos por coincidencia."""
    global _INVIAS_UBICACIONES_CACHE
    if _INVIAS_UBICACIONES_CACHE is not None:
        return _INVIAS_UBICACIONES_CACHE

    result = sb.table("invias_provincias").select(
        "codigo,codigo_departamento,departamento,provincia"
    ).execute()
    ubicaciones = []
    for r in result.data:
        ubicaciones.append({"nombre": r["provincia"], "codigo": r["codigo"], "especificidad": 2})
        ubicaciones.append(
            {"nombre": r["departamento"], "codigo": r["codigo_departamento"], "especificidad": 1}
        )
    # Dedup por (nombre, especificidad) -- varios departamentos con múltiples
    # provincias repiten el mismo nombre de departamento varias veces.
    vistos = set()
    unicos = []
    for u in ubicaciones:
        clave = (u["nombre"].strip().lower(), u["especificidad"])
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(u)
    unicos.sort(key=lambda u: (-u["especificidad"], -len(u["nombre"])))
    _INVIAS_UBICACIONES_CACHE = unicos
    return unicos


def _detectar_ubicacion_invias(query: str) -> str | None:
    """Busca en el texto de la pregunta el nombre de una provincia o
    departamento real de INVIAS (sin tildes, insensible a mayúsculas) y
    devuelve su código -- provincia (4 dígitos) tiene prioridad sobre
    departamento (2 dígitos) si ambos aparecen. None si no se menciona
    ninguna ubicación reconocible; en ese caso la búsqueda queda sin filtro
    de ubicación (mismo comportamiento que antes de este fix)."""
    q = _slug_sin_tildes_query(query)
    for ubicacion in _cargar_ubicaciones_invias():
        nombre = _slug_sin_tildes_query(ubicacion["nombre"])
        if nombre and nombre in q:
            return ubicacion["codigo"]
    return None


def _slug_sin_tildes_query(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"
    )


def buscar_precios_invias_vias(query: str, top_k: int = 4) -> list[PrecioResult]:
    """Busca en la base de precios regionalizados de INVIAS (tablas
    invias_actividades/invias_actividad_costos/invias_provincias, cargadas
    por scripts/ingesta/invias_apu/) vía RPC buscar_precios_invias — mismo
    patrón de texto completo español + trigram que buscar_precios_apu(), pero
    esta fuente es normativa vial (numerales de INVIAS), no Barranquilla.

    Fix real 2026-08-21 (encontrado al probar con 43 provincias cargadas):
    la descripción de una actividad es IDÉNTICA en todo el país (mismo
    numeral INVIAS) -- sin detectar la ubicación mencionada en la pregunta,
    el ranking por texto devolvía provincias arbitrarias, no la que el
    usuario pidió. Ahora se detecta el nombre de provincia/departamento en
    la pregunta y se pasa como filtro de prefijo a la RPC.

    Cobertura real hoy: Orinoquía completa + Caribe completo (43 de las 140
    provincias del país). Si la pregunta no tiene match, simplemente
    devuelve lista vacía; no es un error."""
    codigo_ubicacion = _detectar_ubicacion_invias(query)
    params = {"p_query": query, "p_limit": top_k}
    if codigo_ubicacion:
        params["p_provincia_codigo"] = codigo_ubicacion
    result = sb.rpc("buscar_precios_invias", params).execute()
    return [
        PrecioResult(
            tipo="actividad",
            # La descripción real trae una nota entre paréntesis muy larga
            # (alcance técnico del ítem) -- se muestra solo la primera línea
            # como nombre, el resto ya no cabe en un contexto de una línea.
            nombre=r["descripcion"].split("\n")[0].strip()[:200],
            unidad=r.get("unidad"),
            precio=r.get("costo_directo_total"),
            precio_solo_mano_obra=None,
            region=f"{r['provincia']} ({r['departamento']})" if r.get("provincia") else None,
            tipo_fuente="invias_regional",
            fecha_captura=r.get("periodo"),
            item_codigo=r.get("numeral"),
            categoria_fuente=None,
            score=r.get("relevancia") or 0.0,
        )
        for r in result.data
    ]


def _format_precio_context(p: PrecioResult) -> str:
    """Una línea por resultado — solo lo que un profesional necesita:
    nombre, unidad, precio(s), región genérica, fuente y fecha. Nunca nombre
    de obra, dirección ni municipios específicos de un contrato.

    categoria_fuente incluye, para el catálogo IAD MIPYMES, el rango real
    min-max observado entre las cotizaciones de proveedores que promediaron
    ese precio (ej. "Mediana de 60 cotizaciones reales (rango $925–
    $2.513.440 COP)") — variabilidad real de mercado, no simulada. Antes
    quedaba guardada en la base pero la RPC nunca la seleccionaba, así que
    el chat nunca la mencionaba (encontrado 2026-08-09 revisando cómo dar
    una noción de incertidumbre con lo que ya hay, sin inventar una
    distribución que no está respaldada por suficientes datos)."""
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
    if p.categoria_fuente and "rango $" in p.categoria_fuente:
        partes.append(f"variabilidad real de mercado: {p.categoria_fuente}")
    return " | ".join(partes)


# ─── CONTEXTO COMPARTIDO: JERGA REGIONAL, ENTIDADES/TRÁMITES, REGISTRO ──────
# Agregado 2026-08-21 a pedido del usuario ("diccionario de sinónimos y
# jergas de obra... clasificación por entidades públicas y trámites POT/
# curaduría... roles y arquetipos"). Se reusa en los 6 prompts (normativa,
# precios, y los 4 motores especializados) en vez de duplicarlo — mismo
# patrón que _REGLAS_ANTIINVENCION_MOTOR.
#
# El glosario regional es vocabulario general del gremio de la construcción
# en español (Colombia + variantes comunes de Sudamérica), NO un glosario
# oficial de ninguna norma — se marca así explícitamente para que el modelo
# nunca lo cite como si fuera normativo. Las entidades/trámites SÍ están
# verificados contra fuentes reales (Decreto 1077 de 2015, Ley 388 de 1997 —
# ver project_structai_roadmap_visibilidad.md para las URLs consultadas).
_CONTEXTO_COLOMBIA_COMPARTIDO = """
JERGA REGIONAL (vocabulario del gremio, NO texto normativo — úsalo solo
para reconocer sinónimos, nunca lo cites como oficial): concreto=hormigón
(Arg/Chile/Perú/Esp); formaleta=encofrado(Esp/Arg/Chile)=cimbra(México);
varilla/cabilla/hierro=acero de refuerzo; placa=losa; friso/pañete=revoque
(Arg)=aplanado(Méx)=enlucido; andén=acera(Esp)=vereda(Arg/Chile/Perú); obra
negra=estructura sin acabados; cercha=cabreada(Chile)=armadura de techo;
recebo=base granular; puntilla=clavo; interventor/supervisor
técnico=fiscalizador(Ecuador); maestro de obra=capataz. Si no reconoces un
término regional con certeza, pregunta — nunca inventes la equivalencia.

ENTIDADES Y TRÁMITES (Colombia, verificado — Decreto 1077/2015, Ley
388/1997): Curaduría Urbana (o Planeación Municipal donde no hay curador)
tramita licencias urbanísticas (construcción/urbanización/reforzamiento/
demolición), plazo legal 45 días hábiles. POT (Plan de Ordenamiento
Territorial, Ley 388/1997) define usos del suelo por municipio; su revisión
inicia 6 meses antes de vencer, y si no se renueva a tiempo sigue vigente
el actual. Supervisión técnica de obra (NSR-10 Título I) es DISTINTA de la
licencia urbanística. CAR = licencias ambientales cuando aplica. COPNIA
(ingenieros, Ley 842/2003) y CPNAA (arquitectos, Ley 435/1998) regulan la
matrícula profesional -- si preguntan cómo verificar que un ingeniero/
supervisor tiene matrícula vigente, remite al Certificado de Vigencia y
Antecedentes Disciplinarios gratuito de COPNIA (copnia.gov.co, trámite
individual con cédula, sin costo) -- NUNCA afirmes tú mismo si una
matrícula específica está vigente o no, no tienes ese dato. No inventes
plazos/decretos que no estén arriba — remite a la entidad competente para
el detalle exacto de un trámite.

REGISTRO: si la pregunta suena a alguien de campo (lenguaje coloquial/
regional), explica con el mismo rigor pero en lenguaje directo, menos
denso en jerga académica; si suena técnica (ingeniero/curador), sé más
denso. El valor técnico nunca cambia según quién pregunte, solo la forma.
"""


APU_PRECIOS_SYSTEM_PROMPT = f"""Eres un asistente de precios de construcción para ingenieros
y maestros de obra profesionales en Colombia.

COBERTURA REAL DE PRECIOS (actualizada 2026-08-21 — dilo con seguridad, no
la subestimes ni la trates como si solo cubrieras Barranquilla):
- Barranquilla/Atlántico: el catálogo más granular y profundo (Construdata,
  contratos reales ejecutados, ferretería, proveedores locales) — insumos y
  actividades específicas de acueducto/alcantarillado, obra civil, acabados.
- Colombia completa (las 5 regiones — Caribe, Andina, Pacífico, Orinoquía,
  Amazonía): Análisis de Precios Unitarios (APU) Regionalizados de
  Referencia que INVIAS publica oficialmente por provincia — 140 de 140
  provincias del país cargadas, sin huecos. Son precios de VÍAS/INFRAESTRUCTURA
  (movimiento de tierra, pavimentos, estructuras de drenaje, etc.), no de
  edificación en general, y varían por región (ej. Chocó/Pacífico cuesta
  más que Atlántico por dificultad de acceso — es una diferencia real, no
  un error).
- Catálogo IAD MIPYMES (Colombia Compra Eficiente): 78 proveedores mipyme
  reales a nivel nacional, con el proveedor específico de mejor precio.

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
8. Cuando un ítem traiga "variabilidad real de mercado" (rango mín-máx entre
   varias cotizaciones reales de proveedores), MENCIÓNALO siempre en tu
   respuesta — es información valiosa para un profesional que va a cotizar:
   le dice qué tanto varía el precio según el proveedor, no solo el número
   mediano. Dilo de forma natural ("el precio mediano es $X, pero entre
   proveedores varía de $Y a $Z"), nunca lo omitas si está en el contexto.
9. Cuando la fuente sea "Catálogo IAD MIPYMES — ... (proveedor real con el
   mejor precio...)", el nombre del ítem ya trae "— mejor precio real: NOMBRE
   DEL PROVEEDOR". Dile al usuario el nombre de ese proveedor específico
   (es una empresa mipyme real registrada a nivel nacional, no un dato
   inventado) y menciona cuántos proveedores se compararon y el rango de
   precios — esto le permite al profesional identificar la opción más barata
   entre proveedores reales de todo el país, no solo ver un promedio.
10. Si la pregunta no menciona ciudad/provincia/departamento y el contexto
    trae precios INVIAS de varias regiones distintas para el mismo numeral,
    dilo ("tengo precios de este ítem en varias provincias — te muestro los
    más relevantes, pero si me dices en qué región es tu proyecto te doy el
    exacto") en vez de mezclar todo como si fuera un solo precio nacional.
    Si el contexto ya viene filtrado a una sola provincia/departamento
    (porque la pregunta la mencionó), no hace falta pedir nada más.
{_CONTEXTO_COLOMBIA_COMPARTIDO}"""


def ask_precios(question: str, top_k: int = 8) -> dict:
    """RAG de precios APU — mismo contrato de salida que ask()/ask_delegado()."""
    resultados = buscar_precios_apu(question, top_k=top_k)
    # Suma también los precios regionalizados de INVIAS (numerales de
    # carretera/vías, cobertura hoy: Orinoquía) -- son una fuente distinta a
    # apu_precios_referencia (Barranquilla/Atlántico), así que se agregan en
    # vez de reemplazar, y se reordenan juntos por relevancia. No depende de
    # que el motor detectado haya sido "vias": cualquier pregunta de precio
    # puede coincidir con un numeral INVIAS aunque no use vocabulario vial.
    resultados_invias = buscar_precios_invias_vias(question, top_k=top_k)
    if resultados_invias:
        resultados = sorted(resultados + resultados_invias, key=lambda p: -p.score)[:top_k]
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
    respuesta = _llamar_llm_con_respaldo(messages, max_tokens_groq=700)

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
SYSTEM_PROMPT = f"""Eres un ingeniero civil experto en normatividad colombiana de construcción.
Tu conocimiento abarca: NSR-10 completa (los 11 títulos, A a K, verbatim),
NTC (normas técnicas colombianas), Código Colombiano de Instalaciones
Hidráulicas (NTC 1500), Reglamentos de Seguridad Industrial (Res. 1409,
5018, Decreto 1072), Licencias Urbanísticas (Res. 3232), precios de
construcción de Barranquilla/Atlántico y de las 140 provincias de Colombia
(INVIAS, ver bloque "SOBRE STRUCTAI" abajo).

SOBRE STRUCTAI (usa esto SOLO cuando la pregunta es sobre la herramienta
misma — qué hace, para qué sirve, si cubre tal cosa —, nunca lo mezcles
como si fuera contenido normativo citable con norma/artículo):
StructAI es la app de ingeniería civil donde estás respondiendo. Tiene,
verificado y en producción (no en desarrollo):
- NSR-10 completa (Títulos A-K) y catálogo NTC, texto verbatim citable
  artículo por artículo — no resúmenes genéricos de IA.
- Amenaza sísmica (Aa/Av/zona) en vivo para los 1.123 municipios de
  Colombia, vía servicio geográfico oficial del Servicio Geológico
  Colombiano (SGC) — no solo un puñado de ciudades cargadas a mano.
- Precios de construcción: catálogo profundo de Barranquilla/Atlántico
  (contratos reales) + Análisis de Precios Unitarios Regionalizados de
  INVIAS para las 140 provincias del país (cobertura nacional completa,
  las 5 regiones), + catálogo de 78 proveedores mipyme nacionales
  (Colombia Compra Eficiente).
- Datos hidrometeorológicos IDEAM en vivo (estaciones, precipitación,
  temperatura) por departamento/municipio.
- Motor APU con cálculo de incertidumbre (Monte Carlo, IC90) y motores
  especializados: AquAI (acueducto/alcantarillado, RAS 2000), GeoPot
  (sísmica y laboratorio de suelos), motor-vías (diseño geométrico y
  pavimentos, INVIAS), motor-gerencia (EVM, predicción de proyectos).
Cuando te pregunten si StructAI "sirve para" algo concreto (ej. gestión
de riesgo sísmico, un proyecto en una región específica, calcular
precios de reconstrucción), responde con estos hechos reales de forma
concreta y segura — di explícitamente qué parte de esto aplica a su
caso — en vez de una respuesta genérica de "un software debería
cumplir con..." que no diga qué SÍ tiene esta herramienta. Si te
preguntan algo que StructAI todavía no tiene, dilo con la misma
honestidad, sin inventar una capacidad que no está en esta lista.

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
10. Cuando la pregunta sea amplia/genérica (cubre un tema completo, no un
    dato puntual) y tenga sentido, cierra con UNA sugerencia breve y
    concreta de hacia dónde profundizar (ej. "si me dices la zona de
    amenaza sísmica de tu proyecto te doy el valor exacto de Aa/Av", "¿es
    para una vivienda de 1-2 pisos? Ahí aplica el Título E, más simple que
    el general"). No lo hagas en cada respuesta ni lo fuerces en preguntas
    puntuales que ya quedaron completamente resueltas — es una guía
    ocasional, no una muletilla de cierre.
{_CONTEXTO_COLOMBIA_COMPARTIDO}"""


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

def _generar_respuesta(contexto: str, question: str, system_prompt: Optional[str] = None) -> str:
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
    #
    # El fallback de 2 niveles (Groq -> OpenAI) vive en
    # _llamar_llm_con_respaldo(), compartido con ask_precios().
    #
    # system_prompt: por defecto SYSTEM_PROMPT (RAG normativo general), pero
    # ask_delegado()/_ask_delegado_compuesto() pasan el prompt especializado
    # del motor detectado (MOTOR_SYSTEM_PROMPT) cuando la pregunta es de
    # aquai/geopot/vias/gerencia -- antes todos los motores compartían el
    # mismo tono/jerga de "ingeniero civil general", sin la voz ni los
    # términos propios de cada especialidad (un hidráulico no habla igual
    # que un gerente de proyecto). Ver MOTOR_SYSTEM_PROMPT más abajo.
    messages = [
        {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {question}"}
    ]
    return _llamar_llm_con_respaldo(messages, max_tokens_groq=700)

# Palabras que indican que la pregunta busca algo vigente AHORA, no un
# hecho normativo permanente -- evita meter noticias en cada pregunta de
# cálculo (sería ruido puro), solo cuando de verdad hay intención temporal.
_PALABRAS_ACTUALIDAD = (
    "noticia", "noticias", "reciente", "recientes", "ultima hora", "última hora",
    "hoy", "esta semana", "actualidad", "que esta pasando", "qué está pasando",
    "novedad", "novedades", "actualizacion", "actualización",
)


def _quiere_actualidad(pregunta: str) -> bool:
    q = pregunta.lower()
    return any(p in q for p in _PALABRAS_ACTUALIDAD)


def _bloque_contexto_noticias() -> Optional[str]:
    """Si hay noticias guardadas (ver noticias_colombia.py, alimentado por
    el scheduler de apps/api), arma un bloque de contexto con las más
    recientes de cada categoría. None si no hay datos o Supabase no
    responde -- nunca lanza."""
    try:
        desastres = noticias_colombia.noticias_recientes(sb, categoria="desastre", limite=3)
        regulatorias = noticias_colombia.noticias_recientes(sb, categoria="regulatoria", limite=2)
    except Exception:
        return None
    items = desastres + regulatorias
    if not items:
        return None
    lineas = [
        f"- [{it['categoria']}] {it['titulo']} ({it['fuente']}, {it.get('fecha_publicacion') or 'fecha desconocida'})"
        for it in items
    ]
    return (
        "NOTICIAS RECIENTES DE COLOMBIA (vía Google News, no verificadas por StructAI "
        "más allá del titular -- citar la fuente y la fecha, no afirmar como hecho propio):\n"
        + "\n".join(lineas)
    )


def _comparar_caudal_historico(registro: dict) -> Optional[dict]:
    """Compara un registro de caudal ACTUAL (de
    ideam_client.caudal_por_municipio(), siempre en vivo) contra las
    estadísticas históricas de ESE MISMO mes calendario para esa estación
    (tabla ideam_caudal_estadisticas_mes, calculada una vez a partir del
    histórico real cargado por scripts/ingesta/ideam_caudal/, ver
    infra/supabase/migrations/20260822123425_...). Devuelve None si esa
    estación todavía no tiene estadística cargada (carga masiva en curso o
    estación nueva sin historia suficiente) o si el caudal actual no es
    numérico -- nunca inventa una comparación sin datos reales de ambos
    lados."""
    try:
        caudal_actual = float(registro.get("caudal_m3s"))
        mes = int((registro.get("fecha") or "")[5:7])
    except (TypeError, ValueError):
        return None
    if not (1 <= mes <= 12):
        return None
    resultado = (
        sb.table("ideam_caudal_estadisticas_mes")
        .select("promedio_m3s, p90_m3s, n_observaciones")
        .eq("codigo_estacion", registro["codigo_estacion"])
        .eq("mes", mes)
        .execute()
    )
    if not resultado.data:
        return None
    stats = resultado.data[0]
    promedio = stats.get("promedio_m3s")
    if not promedio:
        return None
    return {
        "caudal_actual": caudal_actual,
        "promedio_historico": promedio,
        "pct_diferencia": (caudal_actual - promedio) / promedio * 100,
        "excede_p90": stats.get("p90_m3s") is not None and caudal_actual > stats["p90_m3s"],
        "n_anos_historicos": stats.get("n_observaciones"),
    }


def _bloque_caudal_con_anomalia(registros: list[dict]) -> str:
    """Igual que ideam_client.formatear_caudal(), pero suma la comparación
    contra el histórico real cuando está disponible (ver
    _comparar_caudal_historico) -- esto es lo que convierte "el caudal es
    177 m³/s" en "el caudal es 177 m³/s, un 14% por debajo de lo normal
    para julio según 42 años de registro". Si una estación no tiene
    estadística cargada todavía, cae de forma segura al formato simple sin
    comparación -- nunca bloquea ni inventa."""
    if not registros:
        return ""
    por_estacion: dict[str, list[dict]] = {}
    for r in registros:
        por_estacion.setdefault(r["codigo_estacion"], []).append(r)

    lineas = ["Caudal medio mensual reciente (IDEAM, estaciones hidrológicas en vivo):"]
    hay_anomalia_alta = False
    for codigo, filas in por_estacion.items():
        ultimo = sorted(filas, key=lambda f: f["fecha"] or "")[-1]
        rio = ultimo.get("corriente") or "río sin identificar"
        nombre_est = ultimo.get("nombre_estacion") or codigo
        fecha = (ultimo.get("fecha") or "")[:7]
        estado = ultimo.get("estado_aprobacion") or "sin estado"
        comparacion = _comparar_caudal_historico(ultimo)
        if comparacion:
            caudal_txt = f"{comparacion['caudal_actual']:.1f}"
            pct = comparacion["pct_diferencia"]
            signo = "por encima del" if pct >= 0 else "por debajo del"
            anomalia = " ⚠️ (supera el percentil 90 histórico)" if comparacion["excede_p90"] else ""
            if comparacion["excede_p90"]:
                hay_anomalia_alta = True
            lineas.append(
                f"- Río {rio} (estación {nombre_est}, {ultimo.get('municipio')}): "
                f"{caudal_txt} m³/s en {fecha} [{estado}] — {abs(pct):.0f}% {signo} "
                f"promedio histórico de ese mes ({comparacion['promedio_historico']:.0f} m³/s, "
                f"{comparacion['n_anos_historicos']} años de registro){anomalia}"
            )
        else:
            try:
                caudal_txt = f"{float(ultimo.get('caudal_m3s')):.1f}"
            except (TypeError, ValueError):
                caudal_txt = ultimo.get("caudal_m3s")
            lineas.append(
                f"- Río {rio} (estación {nombre_est}, {ultimo.get('municipio')}): "
                f"{caudal_txt} m³/s en {fecha} [{estado}] — sin comparación histórica todavía"
            )
    if hay_anomalia_alta:
        lineas.append(
            "Uno o más ríos están por encima de su percentil 90 histórico para este mes -- "
            "señal ESTADÍSTICA de caudal anómalo, NO una alerta oficial de inundación. "
            "Para alertas oficiales consulta directamente al IDEAM/UNGRD."
        )
    else:
        lineas.append(
            "Un caudal muy por encima de lo típico para ese mes/río es indicio de crecida "
            "-- esto NO es una alerta oficial de inundación, para eso consulta directamente "
            "al IDEAM/UNGRD."
        )
    return "\n".join(lineas)


def _bloque_contexto_sgc(sgc_registro: dict) -> str:
    """Arma el bloque de contexto en vivo del SGC/IGAC/IDEAM a partir de un
    registro de sgc_amenaza_sismica.detectar_municipio_en_texto(): siempre
    incluye la amenaza sísmica; si el registro trae coordenadas (lo trae
    desde 2026-08-20) suma el inventario de movimientos en masa cercano
    (SIMMA, sgc_movimientos_masa.py); desde 2026-08-21 suma también las
    unidades físicas homogéneas de suelo del IGAC/UPRA (taxonomía, drenaje,
    inundabilidad, profundidad -- ver igac_client.py, dataset nacional
    fy2r-gwsd); y desde 2026-08-22 suma el caudal reciente de ríos del IDEAM
    (contexto de riesgo de inundación -- ver ideam_client.caudal_por_municipio(),
    bucket S3 público del IDEAM). Cada pieza es independiente -- si una
    fuente no responde o no tiene datos para ese municipio, las demás se
    siguen mostrando igual."""
    partes = [sgc_amenaza_sismica.formatear_respuesta(sgc_registro)]
    lat, lon = sgc_registro.get("latitud"), sgc_registro.get("longitud")
    if lat is not None and lon is not None:
        movimientos = sgc_movimientos_masa.consultar_movimientos_cercanos(lat, lon)
        if movimientos:
            partes.append(sgc_movimientos_masa.formatear_respuesta(movimientos, sgc_registro["municipio"]))
    unidades_suelo = igac_client.consultar_suelos_municipio(
        sgc_registro["municipio"], sgc_registro.get("departamento")
    )
    if unidades_suelo:
        bloque_suelo = igac_client.formatear_respuesta(unidades_suelo, sgc_registro["municipio"])
        if bloque_suelo:
            partes.append(bloque_suelo)
    caudales = ideam_client.caudal_por_municipio(sgc_registro["municipio"], sgc_registro.get("departamento"))
    if caudales:
        bloque_caudal = _bloque_caudal_con_anomalia(caudales)
        if bloque_caudal:
            partes.append(bloque_caudal)
    return "\n\n".join(partes)


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

    # Enriquecimiento con dato oficial en vivo del SGC (ver sgc_amenaza_sismica.py):
    # muchas preguntas de "zona sísmica de <municipio>" caen en este camino general
    # (NSR-10 Título A) en vez del motor geopot -- se aplica aquí también, no solo
    # en ask_delegado(), para cubrir ambos caminos. Nunca reemplaza la búsqueda
    # semántica normal, solo la complementa; si el servicio del SGC no responde o
    # no hay match de municipio, sigue exactamente igual que antes.
    sgc_registro = sgc_amenaza_sismica.detectar_municipio_en_texto(question)
    if sgc_registro:
        contexto = f"DATO OFICIAL EN VIVO (SGC):\n{_bloque_contexto_sgc(sgc_registro)}\n\n---\n\n{contexto}"

    # Enriquecimiento con noticias recientes (ver noticias_colombia.py): solo
    # cuando la pregunta tiene intención temporal explícita ("noticias",
    # "hoy", "última hora"...) -- meter esto en TODA pregunta sería ruido
    # puro para cálculos normativos normales, que son atemporales por
    # naturaleza.
    if _quiere_actualidad(question):
        bloque_noticias = _bloque_contexto_noticias()
        if bloque_noticias:
            contexto = f"{bloque_noticias}\n\n---\n\n{contexto}"

    # 3. Síntesis con Ollama local
    respuesta = _generar_respuesta(contexto, question)
    normas_citadas = list({c.norma for c in chunks})
    fuentes = [
        {"norma": c.norma, "seccion": c.seccion, "score": round(c.score, 4)}
        for c in chunks
    ]
    if sgc_registro:
        fuente_sgc = "SGC — Servicio Geológico Colombiano (amenaza sísmica en vivo)"
        normas_citadas = [fuente_sgc] + normas_citadas
        fuentes = [{"norma": fuente_sgc, "seccion": sgc_registro["municipio"], "score": 1.0}] + fuentes

    return {
        "respuesta": respuesta,
        "normas_citadas": normas_citadas,
        "normas_detectadas_router": target_normas,
        "fuentes": fuentes,
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
    "apu_precios": "Precios de construcción (Barranquilla/Atlántico + INVIAS nacional, 140 provincias)",
}


# ─── PROMPTS ESPECIALIZADOS POR MOTOR ────────────────────────────────────────
# Hasta 2026-08-21, aquai/geopot/vias/gerencia compartían el mismo
# SYSTEM_PROMPT genérico de "ingeniero civil experto en normatividad" -- útil
# para el RAG normativo general, pero un hidráulico, un geotecnista, un
# diseñador vial y un gerente de proyectos NO hablan igual ni usan la misma
# jerga en Colombia. Cada motor tiene su propia voz + su propio vocabulario
# técnico real (verificado contra el código fuente de cada motor en
# packages/motor-*, no inventado), reusando las mismas reglas anti-invención
# que ya probó SYSTEM_PROMPT/APU_PRECIOS_SYSTEM_PROMPT.
_REGLAS_ANTIINVENCION_MOTOR = f"""
INSTRUCCIONES (aplican siempre, sin excepción):
1. Responde SOLO con base en el contexto proporcionado. Nunca inventes un
   valor, norma, artículo, fórmula o coeficiente que no esté en el contexto.
2. Cita el código de la norma y el artículo/sección SOLO si aparece
   LITERALMENTE en el contexto (header "[norma — sección]" de cada
   fragmento). Si no tienes el número exacto, di "la sección
   correspondiente de [Norma]" — nunca inventes un número de cita.
3. Si el contexto no cubre la pregunta, dilo con naturalidad y sugiere qué
   consultar — sin inventar valores ni fórmulas de esa norma.
4. Menciona "⚠️ NORMA DEROGADA/MODIFICADA" únicamente si esa frase exacta
   aparece en el contexto — nunca como forma genérica de expresar duda.
5. Cuando la pregunta sea amplia y tenga sentido, cierra con UNA sugerencia
   breve de hacia dónde profundizar (nunca en cada respuesta, solo cuando
   agregue valor real).
{_CONTEXTO_COLOMBIA_COMPARTIDO}"""

AQUAI_SYSTEM_PROMPT = f"""Eres un ingeniero hidráulico y sanitario colombiano, especialista en
acueducto, alcantarillado y saneamiento básico (RAS 2000 y su actualización,
Resolución 0330 de 2017).

VOZ Y TONO: hablas como el ingeniero hidrosanitario que revisa el diseño de
una red antes de radicarlo — directo, con la jerga real del gremio: caudal
de diseño, dotación neta, coeficientes K1/K2 (máximo diario/horario),
caudal contra incendio, coeficiente de rugosidad de Hazen-Williams, golpe
de ariete (celeridad, cierre rápido/lento), TDH de una estación de bombeo,
PTAP/PTAR, colector, cámara de inspección, pendiente hidráulica. Nunca
suenas a manual traducido — suenas a alguien que calcula esto todos los
días en Colombia.
{_REGLAS_ANTIINVENCION_MOTOR}"""

GEOPOT_SYSTEM_PROMPT = f"""Eres un ingeniero geotecnista y de laboratorio de materiales
colombiano, especialista en amenaza sísmica NSR-10 y ensayos de suelos,
concreto y agregados.

VOZ Y TONO: hablas como el geotecnista que firma un estudio de suelos —
preciso, con la jerga real: capacidad portante, perfil estratigráfico,
límites de Atterberg, ensayo Proctor (compactación), CBR, clasificación
USCS, licuación, sondeo, SPT, granulometría, desgaste Los Ángeles,
asentamiento (slump), curva de maduración del concreto, zona de amenaza
sísmica (Aa/Av). Si citas un libro de referencia general de ingeniería
geológica (ej. González de Vallejo), acláralo como lectura recomendada,
NUNCA como si fuera texto verbatim de una norma colombiana — solo cita
verbatim lo que esté literalmente en el contexto.
{_REGLAS_ANTIINVENCION_MOTOR}"""

VIAS_SYSTEM_PROMPT = f"""Eres un ingeniero vial colombiano, especialista en diseño geométrico
de carreteras, pavimentos y mantenimiento vial (Manual de Diseño Geométrico
INVIAS, Manual de Mantenimiento INVIAS, normas de ensayo INV E-).

VOZ Y TONO: hablas como el ingeniero de vías que revisa un diseño en campo
— directo, con la jerga real: subrasante, CBR de diseño, número
estructural, radio mínimo de curva horizontal, peralte, distancia de
visibilidad de parada/adelantamiento, pendiente longitudinal máxima,
bombeo de calzada, TPD (tránsito promedio diario), capa de rodadura,
deterioro de pavimento (piel de cocodrilo, ahuellamiento, etc.).
{_REGLAS_ANTIINVENCION_MOTOR}"""

GERENCIA_SYSTEM_PROMPT = f"""Eres un gerente de proyectos de construcción colombiano,
especialista en control de costos y cronograma con Earned Value Management
(EVM) y predicción de tendencias de obra.

VOZ Y TONO: hablas como el gerente que presenta el informe de avance del
mes — claro, con la jerga real: valor ganado (EV), valor planeado (PV),
costo actual (AC), CPI/SPI (índices de desempeño de costo/cronograma),
EAC (estimado a la conclusión), curva S, línea base, EDT/WBS, hito,
sobrecosto, desviación de cronograma. Explica qué significa el número para
la toma de decisión (¿vamos bien o mal?), no solo la fórmula.
{_REGLAS_ANTIINVENCION_MOTOR}"""

MOTOR_SYSTEM_PROMPT: dict[str, str] = {
    "aquai": AQUAI_SYSTEM_PROMPT,
    "geopot": GEOPOT_SYSTEM_PROMPT,
    "vias": VIAS_SYSTEM_PROMPT,
    "gerencia": GERENCIA_SYSTEM_PROMPT,
}


def _ask_delegado_compuesto(question: str, motores: list[str], top_k: int) -> dict:
    """Pregunta compuesta detectada (ej. 'precio del cemento + definición de
    dotación neta'): apu_precios y al menos otro dominio puntúan ambos por
    encima de 0. En vez de forzar todo al dominio ganador (perdiendo la otra
    mitad de la pregunta pese a que el dato sí existe), se consulta AMBAS
    fuentes y se sintetiza una sola respuesta con trazabilidad de norma +
    precio. Ver route_motores_multiples() para el detalle del bug original."""
    otro_motor = next((m for m in motores if m != "apu_precios"), None)
    mitad = max(3, top_k // 2)

    precios = buscar_precios_apu(question, top_k=mitad)
    # Cuando el otro dominio es "vias", la pregunta de precio probablemente
    # se refiere a un ítem de carretera/INVIAS (ej. "relleno granular",
    # "señalización", numerales 6xx/7xx/8xx) -- se suma la base regionalizada
    # de INVIAS a la de Barranquilla/Atlántico en vez de reemplazarla, ya que
    # cubren cosas distintas (Orinoquía por provincia vs. Atlántico general).
    if otro_motor == "vias":
        precios = precios + buscar_precios_invias_vias(question, top_k=mitad)
    chunks = search(question, top_k=mitad, motor_filter=otro_motor) if otro_motor else []

    partes = []
    if chunks:
        partes.append(
            "CONTEXTO NORMATIVO:\n" + "\n\n---\n\n".join(_format_chunk_context(c) for c in chunks)
        )
    if precios:
        partes.append(
            "PRECIOS DISPONIBLES:\n" + "\n".join(_format_precio_context(p) for p in precios)
        )

    if not partes:
        dominio_label = " + ".join(MOTOR_LABEL.get(m, m) for m in motores)
        return {
            "dominio": "+".join(motores),
            "dominio_label": dominio_label,
            "respuesta": (
                f"La pregunta parece cubrir {dominio_label}, pero no encontré "
                "contenido cargado para ninguna de las dos partes todavía. "
                "No genero una respuesta para evitar inventar información."
            ),
            "normas_citadas": [],
            "fuentes": [],
            "chunks_usados": 0,
        }

    contexto = "\n\n===\n\n".join(partes)
    # otro_motor puede ser None (pregunta compuesta detectó solo apu_precios
    # más ruido) -- MOTOR_SYSTEM_PROMPT.get(None) da None y _generar_respuesta
    # cae a SYSTEM_PROMPT genérico, comportamiento seguro por defecto.
    respuesta = _generar_respuesta(contexto, question, system_prompt=MOTOR_SYSTEM_PROMPT.get(otro_motor))

    fuentes = [
        {
            "norma": c.norma,
            "seccion": c.seccion,
            "contenido": c.contenido[:400],
            "score": round(c.score, 4),
        }
        for c in chunks
    ] + [
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
        for p in precios
    ]
    normas_citadas = list(dict.fromkeys(
        [c.norma for c in chunks] + [p.fuente_display for p in precios]
    ))[:6]

    return {
        "dominio": "+".join(motores),
        "dominio_label": " + ".join(MOTOR_LABEL.get(m, m) for m in motores),
        "respuesta": respuesta,
        "normas_citadas": normas_citadas,
        "fuentes": fuentes,
        "chunks_usados": len(chunks) + len(precios),
    }


def ask_delegado(question: str, top_k: int = 6) -> dict:
    """
    Punto de entrada único: detecta si la pregunta pertenece al dominio de un
    motor específico (aquai/geopot/vias/gerencia) o al RAG normativo general
    (NSR-10/NTC/seguridad industrial), busca en la fuente correcta y sintetiza
    con Groq. Esto es lo que expone /consultar en la API.

    Si la pregunta es compuesta (ej. mezcla precio + normativa) y apu_precios
    puntúa junto a otro dominio, delega a _ask_delegado_compuesto() para no
    perder ninguna de las dos mitades — ver route_motores_multiples().
    """
    motores = route_motores_multiples(question)
    if "apu_precios" in motores and len(motores) > 1:
        return _ask_delegado_compuesto(question, motores, top_k)

    motor = motores[0] if motores else None

    if motor == "apu_precios":
        # No usa motor_chunks/embeddings — tablas y RPC propios (ver arriba).
        result = ask_precios(question, top_k=top_k)
        result["dominio"] = motor
        result["dominio_label"] = MOTOR_LABEL.get(motor, motor)
        return result

    if motor:
        chunks = search(question, top_k=top_k, motor_filter=motor)
        # Para vias, un precio INVIAS encontrado también cuenta como "sí hay
        # contenido" -- calculado aquí (antes del early-return de abajo) para
        # no descartar la pregunta solo porque motor_chunks no tuvo match,
        # cuando la base de precios regionalizados sí lo tiene.
        precios_invias_disponibilidad = (
            motor == "vias" and _score_motores(question).get("apu_precios", 0) > 0
        )
        if not chunks and not precios_invias_disponibilidad:
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

    # Enriquecimiento con dato oficial en vivo del SGC/IGAC/IDEAM: si la
    # pregunta de geopot O aquai menciona un municipio de Colombia, se
    # consulta el servicio geográfico real del SGC (Aa/Av/zona de amenaza
    # sísmica NSR-10) y se antepone al contexto -- cobertura de los 1.122
    # municipios del país, no solo las ciudades ya troceadas a mano en
    # motor_chunks/nsr10_chunks. aquai se agregó 2026-08-22: el mismo
    # bloque ahora también trae caudal de ríos IDEAM (ver
    # _bloque_contexto_sgc), directamente relevante para preguntas
    # hidráulicas/de riesgo de inundación, no solo para geopot. Nunca
    # reemplaza la búsqueda semántica normal, solo la complementa; si el
    # servicio falla o no hay match, sigue exactamente el mismo camino de
    # siempre. Ver sgc_amenaza_sismica.py para el detalle.
    sgc_registro = (
        sgc_amenaza_sismica.detectar_municipio_en_texto(question)
        if motor in ("geopot", "aquai")
        else None
    )

    # Enriquecimiento con precios regionalizados de INVIAS: mismo espíritu que
    # el enriquecimiento SGC de arriba -- nunca reemplaza la búsqueda semántica
    # normal de motor_chunks (contenido normativo/técnico de vías), solo la
    # complementa cuando la pregunta también tiene intención de precio (se
    # reusa el mismo scoring de apu_precios ya probado en route_motores_multiples,
    # no una heurística nueva). Cobertura real hoy: solo Orinoquía (9 de 140
    # provincias) -- si no hay match, la lista simplemente viene vacía.
    precios_invias = (
        buscar_precios_invias_vias(question, top_k=4)
        if motor == "vias" and _score_motores(question).get("apu_precios", 0) > 0
        else []
    )
    if not chunks and not precios_invias:
        # precios_invias_disponibilidad predijo que había precio (evitó el
        # early-return de arriba), pero la RPC no encontró match real -- caer
        # al mismo mensaje honesto de "no hay contenido" en vez de llamar al
        # LLM con un contexto vacío.
        return {
            "dominio": motor,
            "dominio_label": MOTOR_LABEL.get(motor, motor),
            "respuesta": (
                f"La pregunta parece pertenecer al dominio {MOTOR_LABEL.get(motor, motor)}, "
                "pero no encontré contenido normativo ni precios de INVIAS que coincidan. "
                "No se genera una respuesta para evitar inventar información."
            ),
            "normas_citadas": [],
            "fuentes": [],
            "chunks_usados": 0,
        }

    contexto = "\n\n---\n\n".join(_format_chunk_context(c) for c in chunks)
    if sgc_registro:
        contexto = f"DATO OFICIAL EN VIVO (SGC):\n{_bloque_contexto_sgc(sgc_registro)}\n\n---\n\n{contexto}"
    if precios_invias:
        bloque_precios = "PRECIOS INVIAS REGIONALIZADOS (vías/carreteras):\n" + "\n".join(
            _format_precio_context(p) for p in precios_invias
        )
        contexto = f"{bloque_precios}\n\n---\n\n{contexto}" if contexto else bloque_precios

    # Mismo enriquecimiento de noticias que ask() -- faltaba aquí (bug real
    # encontrado 2026-08-20 con Groq en vivo: una pregunta de geopot con
    # intención temporal nunca traía noticias porque solo estaba conectado
    # en ask(), no en este branch).
    if _quiere_actualidad(question):
        bloque_noticias = _bloque_contexto_noticias()
        if bloque_noticias:
            contexto = f"{bloque_noticias}\n\n---\n\n{contexto}"

    respuesta = _generar_respuesta(contexto, question, system_prompt=MOTOR_SYSTEM_PROMPT.get(motor))

    normas_citadas = list({c.norma for c in chunks})
    fuentes = [
        {"norma": c.norma, "seccion": c.seccion, "score": round(c.score, 4)}
        for c in chunks
    ]
    if sgc_registro:
        fuente_sgc = "SGC — Servicio Geológico Colombiano (amenaza sísmica en vivo)"
        normas_citadas = [fuente_sgc] + normas_citadas
        fuentes = [{"norma": fuente_sgc, "seccion": sgc_registro["municipio"], "score": 1.0}] + fuentes
    if precios_invias:
        normas_citadas = [p.fuente_display for p in precios_invias] + normas_citadas
        fuentes = [
            {
                "norma": p.fuente_display,
                "seccion": f"{p.nombre} — ${p.precio:,.0f} COP/{p.unidad or 'un'} ({p.region})" if p.precio is not None else p.nombre,
                "score": p.score,
            }
            for p in precios_invias
        ] + fuentes

    return {
        "dominio": motor,
        "dominio_label": MOTOR_LABEL.get(motor, motor),
        "respuesta": respuesta,
        "normas_citadas": normas_citadas,
        "fuentes": fuentes,
        "chunks_usados": len(chunks) + len(precios_invias),
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
