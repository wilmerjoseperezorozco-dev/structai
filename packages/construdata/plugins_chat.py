"""Plugins determinísticos del chat de StructAI (primer lote, issue #104).

CONTRATO de cada plugin: (1) `activar_*(pregunta)` puro y barato, sin red; (2) `ejecutar_*` que consulta datos, calcula con funciones determinísticas (el modelo de
lenguaje NUNCA calcula ni inventa estas cifras) y devuelve un ResultadoPlugin con su fuente, la fecha de los datos y sus límites; (3) nunca lanza: si algo falla,
el chat sigue exactamente igual que antes. `aplicar()` añade al final de la respuesta una sección con los resultados y suma las fuentes; es idempotente y no
muta el diccionario recibido.

Plugins: ENSO por región, vigencia de normas, revisión de un precio unitario, insumos de una actividad INVIAS (y sugerencia por vecinos si se listan insumos).
"""
from __future__ import annotations

import importlib.util
import json
import logging
import math
import re
import sys
import time
import unicodedata
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger("plugins_chat")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
URL_ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
TTL_ONI, TTL_REGISTRO, TIMEOUT_ONI = 6 * 3600, 3600, 3


@dataclass(frozen=True)
class ResultadoPlugin:
    nombre: str
    markdown: str
    fuente: str
    seccion: str
    fecha_datos: Optional[str] = None


def _norm(s: str) -> str:
    t = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9$]+", " ", t).strip()


# ───────────────────────────── 1. ENSO por región ─────────────────────────────
_RE_ENSO = re.compile(r"\bnino\b|\bnina\b|\benso\b|\boni\b")
_REGIONES_TXT = (("caribe", "Caribe"), ("andina", "Andina"), ("pacifico", "Pacifica"), ("orinoquia", "Orinoquia"), ("amazonia", "Amazonia"))
_cache_oni: dict = {"t": 0.0, "v": None}
_cache_enso: dict = {}


def activar_enso(pregunta: str) -> bool:
    return bool(_RE_ENSO.search(_norm(pregunta)))


def _datos_enso() -> dict:
    if not _cache_enso:
        _cache_enso.update(json.loads((AQUI / "data" / "enso_regiones.json").read_text(encoding="utf-8")))
    return _cache_enso


def _descargar(url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "structai-chat/1.0"}), timeout=TIMEOUT_ONI) as r:
        return r.read().decode("utf-8", "replace")


def oni_actual(descargar: Callable[[str], str] = _descargar, ahora: Callable[[], float] = time.time) -> Optional[dict]:
    """Última temporada trimestral del ONI (NOAA CPC); None si no se pudo consultar. Caché de 6 h."""
    if _cache_oni["v"] is not None and ahora() - _cache_oni["t"] < TTL_ONI:
        return _cache_oni["v"]
    try:
        filas = [ln.split() for ln in descargar(URL_ONI).splitlines()[1:] if len(ln.split()) == 4]
        seas, yr, _, anom = filas[-1]
        v = float(anom)
        res = {"temporada": f"{seas} {yr}", "oni": v, "fase": "El Niño" if v >= 0.5 else "La Niña" if v <= -0.5 else "neutral"}
    except Exception as e:  # noqa: BLE001 -- el plugin nunca debe romper el chat
        logger.warning("ONI no disponible: %s", e)
        return _cache_oni["v"]
    _cache_oni.update({"t": ahora(), "v": res})
    return res


def _region(pregunta: str, datos: dict, detectar_municipio: Optional[Callable[[str], Optional[dict]]]) -> tuple[Optional[str], Optional[str]]:
    t = _norm(pregunta)
    for clave, nombre in _REGIONES_TXT:
        if re.search(rf"\b{clave}\b", t):
            return nombre, None
    for dep in sorted(datos["departamentos"], key=len, reverse=True):
        if re.search(rf"\b{re.escape(_norm(dep))}\b", t):
            return datos["departamentos"][dep], dep.title()
    if detectar_municipio:
        try:
            reg = detectar_municipio(pregunta)
        except Exception:  # noqa: BLE001
            reg = None
        if reg:
            dep = _norm(reg.get("departamento", ""))
            for k, v in datos["departamentos"].items():
                if _norm(k) == dep:
                    return v, f"{reg.get('municipio', '')} ({k.title()})"
    return None, None


def ejecutar_enso(pregunta: str, detectar_municipio=None, descargar=_descargar) -> Optional[ResultadoPlugin]:
    datos = _datos_enso(); oni = oni_actual(descargar)
    region, lugar = _region(pregunta, datos, detectar_municipio)
    lin = []
    if oni:
        lin.append(f"- **Estado actual del Pacífico (NOAA CPC):** ONI de la temporada {oni['temporada']} = {oni['oni']:+.1f} °C → condiciones de **{oni['fase']}** "
                   "(es un indicador del océano, no un pronóstico de lluvias).")
    else:
        lin.append("- No pude consultar el ONI actual en este momento; abajo va solo el historial.")
    regs = [region] if region else list(datos["regiones"])
    for r in regs:
        x = datos["regiones"][r]; a, b = x["altas_nina"], x["bajas_nino_exploratorio"]
        sig = "estadísticamente significativo" if a["p_holm"] < 0.05 and a["dif_pp"] > 0 else "no significativo o de signo contrario"
        et = f"{x['nombre']}" + (f" (consulta sobre {lugar})" if lugar and r == region else "")
        lin.append(f"- **{et}** ({x['estaciones']} estaciones IDEAM, 1934-2026): durante La Niña el {a['nina_pct']} % de las estaciones tuvo caudal anómalamente alto cada mes, "
                   f"frente a {a['neutral_pct']} % en meses neutrales ({a['dif_pp']:+.1f} puntos, IC95 % {a['ic_pp'][0]:+.1f} a {a['ic_pp'][1]:+.1f}; {sig}). "
                   f"Durante El Niño, anomalías bajas: {b['nino_pct']} % frente a {b['neutral_pct']} % (exploratorio, sin ajuste).")
    lin.append("- **Límites:** son señales estadísticas del pasado, no una alerta oficial ni un pronóstico. En validación fuera de muestra, añadir ENSO **no mejoró** la predicción "
               "de crecientes ni del precio de la energía; úselo como contexto. Para alertas oficiales consulte al IDEAM.")
    if not region:
        lin.insert(1, "- No identifiqué su región; se muestran las cinco.")
    return ResultadoPlugin("enso_region", "\n".join(lin), "NOAA CPC (ONI) + análisis propio StructAI (research/coherencia-anomalias)", region or "Todas las regiones",
                           oni["temporada"] if oni else None)


# ───────────────────────────── 2. Vigencia de normas ─────────────────────────────
_RE_VIG = re.compile(r"\bvigen|\bderog|\bmodific|\bactualiz|\breemplaz|\bsustitu|\bsigue siendo")
_cache_reg: dict = {"t": 0.0, "rows": [], "mods": []}
_VERIF = {"texto_verificado": "texto leído y verificado", "solo_citado_por_otro_decreto": "solo citado por otro decreto",
          "resumen_web_sin_verificar": "solo resumen web, sin verificar"}


def activar_vigencia(pregunta: str) -> bool:
    return bool(_RE_VIG.search(_norm(pregunta)))


def _patron_codigo(codigo: str) -> Optional[re.Pattern]:
    c = codigo.lower()
    if "derogada-anterior" in c:
        return None
    if c.startswith("nsr10"):
        return re.compile(r"\bnsr 10\b|\bnsr10\b")
    partes = re.split(r"[-_]", c)
    for i, p in enumerate(partes):
        if p.isdigit() and i > 0:
            pref = {"res": "resolucion", "dec": "decreto"}.get(" ".join(partes[:i]), " ".join(partes[:i]))
            if pref in ("ley", "resolucion", "decreto", "ntc", "iso", "aci", "ais", "ccp", "ntc iso", "inv"):
                return re.compile(rf"\b{re.escape(pref)} 0*{p.lstrip('0') or '0'}\b")
            return None
    return None


def _patron_norma_mod(norma: str) -> re.Pattern:
    t = _norm(norma).split()
    clave = " ".join(t[:2]) if len(t) > 1 else t[0]
    return re.compile(rf"\b{re.escape(clave)}\b")


def _cargar_registro(sb) -> tuple[list, list]:
    if time.time() - _cache_reg["t"] < TTL_REGISTRO and _cache_reg["rows"]:
        return _cache_reg["rows"], _cache_reg["mods"]
    rows = sb.table("normas_registro").select("codigo,nombre_completo,estado_vigencia,alcance_derogacion,notas_vigencia,fecha_expedicion").execute().data or []
    mods = sb.table("normas_modificaciones").select("norma,decreto,fecha,objeto,estado_verificacion").order("fecha").execute().data or []
    _cache_reg.update({"t": time.time(), "rows": rows, "mods": mods})
    return rows, mods


def _limpiar_nota(texto: Optional[str], limite: int = 320) -> str:
    """Quita detalles internos (fuente real, chunks, rutas de scripts) y corta en límite de frase/palabra."""
    if not texto:
        return ""
    cortes = [texto.find(m) for m in ("Fuente real", "chunk", "scripts/") if m in texto]
    t = (texto[:min(cortes)] if cortes else texto).strip()
    if len(t) > limite:
        t = t[:limite].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return t


def ejecutar_vigencia(pregunta: str, sb) -> Optional[ResultadoPlugin]:
    if sb is None:
        return None
    t = _norm(pregunta); rows, mods = _cargar_registro(sb)
    reg = [r for r in rows if (p := _patron_codigo(r["codigo"])) and p.search(t)]
    normas_mod = sorted({m["norma"] for m in mods if _patron_norma_mod(m["norma"]).search(t)})
    if not reg and not normas_mod:
        return None
    lin = []
    vistos_nsr = False
    for r in reg[:6]:
        if r["codigo"].lower().startswith("nsr10"):
            if vistos_nsr:
                continue
            vistos_nsr = True
            estados = sorted({x["estado_vigencia"] for x in reg if x["codigo"].lower().startswith("nsr10")})
            lin.append(f"- **NSR-10** (registro por títulos): estado {', '.join(estados)}.")
            continue
        extra = " ".join(x for x in (_limpiar_nota(r.get("alcance_derogacion")), _limpiar_nota(r.get("notas_vigencia"))) if x)
        est = {"desconocido": "estado **no confirmado**"}.get(r["estado_vigencia"], f"estado **{r['estado_vigencia'].replace('_', ' ')}**")
        lin.append(f"- **{r['nombre_completo']}**: {est}." + (f" {extra}" if extra else ""))
    for n in normas_mod[:2]:
        cad = [m for m in mods if m["norma"] == n]; ver = sum(m["estado_verificacion"] == "texto_verificado" for m in cad)
        lin.append(f"- **Cadena de modificaciones de {n}:** {len(cad)} normas registradas, {ver} con texto verificado; el resto se conoce por citas en otros decretos o por resúmenes web sin verificar.")
        for m in cad[-6:]:
            lin.append(f"    - {m['decreto']} ({m.get('fecha') or 's. f.'}): {(m.get('objeto') or '')[:130]} — {_VERIF.get(m['estado_verificacion'], m['estado_verificacion'])}.")
    lin.append("- **Límite:** es un registro de seguimiento; no sustituye el texto consolidado oficial ni el Diario Oficial. Verifique la versión vigente antes de aplicar una norma.")
    return ResultadoPlugin("vigencia_normas", "\n".join(lin), "Registro de vigencia de StructAI (normas_registro, normas_modificaciones)", ", ".join(normas_mod or [r["codigo"] for r in reg[:2]]))


# ───────────────────────────── 3. Revisión de un precio ─────────────────────────────
_RE_PESOS = re.compile(r"\$\s*(\d[\d.,]*)(?:\s*(mil millones|millones|millon|mil))?|(\d[\d.,]*)\s*(mil millones|millones|millon|mil)?\s*(?:pesos|cop)\b")
_RE_INTENCION = re.compile(r"razonable|caro|barato|elevad|sobreprecio|justo|correct|cobr|cotiz|ofrec|vend|pagu|pago|cuesta|vale|precio|alto|bajo")
_RELLENO = {"es", "esta", "un", "una", "el", "la", "los", "las", "de", "del", "por", "a", "en", "que", "me", "mi", "razonable", "caro", "barato", "precio", "pagar", "pago",
            "pesos", "cop", "cobran", "cobra", "cotizacion", "cotizan", "cuesta", "vale", "ofrecen", "ofrecieron", "bien", "justo", "correcto", "elevado", "alto", "bajo",
            "sera", "si", "al", "para", "tengo", "puedo", "cuanto", "como", "se", "lo", "le", "son", "hay", "es", "mil", "millones"}
_mod_cache: dict = {}


def _modulo_apu(archivo: str, nombre: str):
    if nombre not in _mod_cache:
        ruta = RAIZ / "packages" / "motor-apu" / "src" / archivo
        spec = importlib.util.spec_from_file_location(nombre, ruta); m = importlib.util.module_from_spec(spec); sys.modules[nombre] = m; spec.loader.exec_module(m)
        _mod_cache[nombre] = m
    return _mod_cache[nombre]


def _numero(txt: str) -> float:
    s = txt.strip(".,")
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", s):
        return float(re.sub(r"[.,]", "", s))
    if re.fullmatch(r"\d+[.,]\d{1,2}", s):
        return float(s.replace(",", "."))
    return float(re.sub(r"[.,]", "", s))


def _extraer_monto(pregunta: str) -> Optional[tuple[float, str]]:
    t = pregunta.lower()
    for m in _RE_PESOS.finditer(t):
        num, mult = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        try:
            v = _numero(num)
        except ValueError:
            continue
        v *= {"mil": 1e3, "millon": 1e6, "millones": 1e6, "mil millones": 1e9}.get(mult or "", 1)
        return v, (t[:m.start()] + " " + t[m.end():])
    return None


def _normalizar_descripcion_precio(desc: str) -> str:
    """Acerca el lenguaje del usuario al del catálogo: «saco/costal» → «bulto» y «50 kg/kilos» → «50kl» (el catálogo escribe «50Kl»)."""
    d = re.sub(r"\b(saco|sacos|costal|costales)\b", "bulto", desc)
    return re.sub(r"\b(\d+) ?(kg|kilo|kilos|kilogramos|kl)\b", r"\1kl", d)


def activar_precio(pregunta: str) -> bool:
    return _extraer_monto(pregunta) is not None and bool(_RE_INTENCION.search(_norm(pregunta)))


def ejecutar_precio(pregunta: str) -> Optional[ResultadoPlugin]:
    ext = _extraer_monto(pregunta)
    if not ext:
        return None
    precio, resto = ext
    desc = _normalizar_descripcion_precio(" ".join(w for w in _norm(resto).split() if w not in _RELLENO))
    if not desc:
        return None
    pa = _modulo_apu("precios_atipicos.py", "structai_precios_atipicos"); ref = pa.ReferenciaPrecios.desde_json(); v = ref.evaluar(desc, precio)
    if v.veredicto == "sin_referencia":
        txt = (f"- No encontré en el catálogo un ítem suficientemente parecido a «{desc}» (similitud {v.similitud:.2f}); no puedo valorar ese precio. "
               "Pruebe con el nombre más completo del material o la actividad.")
    else:
        lejos = v.veredicto == "consistente" and v.razon is not None and (v.razon > 3 or v.razon < 1 / 3)
        etiqueta = {"consistente": ("**no concluyente**: difiere " + (f"{v.razon:.1f}" if v.razon else "") + "× de la mediana del ítem, pero ese ítem tiene una dispersión tan amplia en el catálogo "
                                    "(posibles unidades mezcladas) que no se marca como atípico") if lejos else "**consistente** con las cotizaciones del catálogo", "alto": "**alto** frente a las cotizaciones del catálogo",
                    "bajo": "**bajo** frente a las cotizaciones del catálogo", "posible_error_de_unidad": "**posible error de unidad** (la diferencia es de un orden de magnitud)"}[v.veredicto]
        txt = (f"- El precio de ${precio:,.0f} COP es {etiqueta}.\n"
               f"    - Ítem de referencia: {v.item} (unidad: {v.unidad}); mediana del catálogo ${v.mediana:,.0f}; su precio es {v.razon:.2f}× esa mediana (puntaje z = {v.z:+.2f}); similitud del emparejamiento {v.similitud:.2f}.\n"
               f"    - **Verifique que la unidad coincida:** el ítem de referencia está en «{v.unidad}». El catálogo trae precios sin IVA.")
    if v.veredicto != "sin_referencia":
        ficha = next((i for i in ref.items if i["nombre"] == v.item), None)
        if ficha and ficha.get("mad_log", 0) >= 0.9:
            txt += ("\n    - **Ojo:** ese ítem tiene una dispersión extrema en el catálogo (rango de cotizaciones de " f"${ficha['q05']:,.0f} a ${ficha['q95']:,.0f}); "
                    "probablemente mezcla unidades o presentaciones. Compare mejor con un ítem de presentación definida.")
    parecidos = [(i, s) for i, s in ref.buscar(desc, 4) if i["nombre"] != (v.item or "") and s >= 0.3][:3]
    if parecidos:
        txt += "\n- **Otros ítems parecidos del catálogo:** " + "; ".join(f"{i['nombre'][:55]} ({i['unidad']}, mediana ${i['mediana']:,.0f})" for i, _ in parecidos) + "."
    txt += ("\n- **Límite:** es un tamizaje estadístico frente a cotizaciones de un catálogo de un solo momento (carga de agosto de 2026), no el precio de mercado ni un dictamen de error; "
            "si la respuesta de arriba usa otra fuente (por ejemplo precios locales por kilo), compare las unidades. En pruebas, ante un error de ×10 detecta el 64 % de los casos.")
    return ResultadoPlugin("revision_precio", txt, "Catálogo IAD MIPYMES (Colombia Compra Eficiente) + revisión StructAI (research/precios-p1-p3)", desc, "2026-08-08")


# ───────────────────────────── 4. Insumos de una actividad ─────────────────────────────
_RE_INSUMOS = re.compile(r"qu[e] (insumos|materiales|recursos)|cuales son los (insumos|materiales)|composicion (de|del)|insumos (de|del|para|que)|que lleva|que necesita|que incluye")
_ri_cache: dict = {}


def activar_insumos(pregunta: str) -> bool:
    return bool(_RE_INSUMOS.search(_norm(pregunta)))


def _recomendador():
    if "r" not in _ri_cache:
        _ri_cache["r"] = _modulo_apu("recomendador_insumos.py", "structai_recomendador_insumos").RecomendadorInsumos.desde_json()
    return _ri_cache["r"]


def ejecutar_insumos(pregunta: str) -> Optional[ResultadoPlugin]:
    r = _recomendador(); t = _norm(pregunta)
    nombrados = [c for c, i in r.insumos.items() if len(_norm(i["descripcion"])) >= 5 and re.search(rf"\b{re.escape(_norm(i['descripcion']))}\b", t)]
    if len(nombrados) >= 2:
        sug = r.sugerir(nombrados[:8], k=8)
        lin = [f"- Insumos reconocidos en su pregunta: {', '.join(r.insumos[c]['descripcion'] for c in nombrados[:8])}.",
               "- Insumos que suelen acompañarlos en actividades INVIAS parecidas: " + "; ".join(f"{s['descripcion']} ({s['unidad']}, {s['tipo']})" for s in sug) + "."]
        lin.append("- **Límite:** sugiere insumos frecuentes en 324 actividades de obra vial INVIAS 2026-1 (acierto@10 de 0,78 a 0,84 al ocultar un insumo); no verifica que su APU sea correcto ni optimiza costo.")
        return ResultadoPlugin("recomendador_insumos", "\n".join(lin), "Composición de actividades INVIAS 2026-1 + recomendador por vecinos (research/precios-p1-p3)", "sugerencia por vecinos")
    pa = _modulo_apu("precios_atipicos.py", "structai_precios_atipicos")
    q = [w for w in pa.normalizar(pregunta) if w not in _RELLENO and w not in {"insumos", "materiales", "recursos", "lleva", "necesita", "incluye", "composicion", "actividad", "apu", "cuales"}]
    if not q:
        return None
    acts = r.actividades; docs = [set(pa.normalizar(a["descripcion"].split("\n")[0].split("(")[0])) for a in acts]
    # La letra de clase (A/B/C...) es una sola letra y el normalizador la descarta como palabra vacía: se exige aparte, para no devolver «clase B» a quien pidió «clase A».
    clase = re.search(r"\bclase ([a-d])\b", t)
    permitido = [(not clase) or f"clase {clase.group(1)}" in _norm(a["descripcion"].split("\n")[0].split("(")[0]) for a in acts]
    df: dict[str, int] = {}
    for d in docs:
        for w in d:
            df[w] = df.get(w, 0) + 1
    n = len(docs)

    def idf(w: str) -> float:
        return math.log((n + 1) / (df.get(w, 0) + 1)) + 1

    puntajes = []
    for i, d in enumerate(docs):
        inter = [w for w in set(q) if w in d]
        if inter and len(d) and permitido[i]:
            puntajes.append((sum(idf(w) for w in inter) / (sum(idf(w) for w in d) ** 0.5 * sum(idf(w) for w in set(q)) ** 0.5), i))
    puntajes.sort(reverse=True)
    mejores = [(s, i) for s, i in puntajes[:2] if s >= 0.30]
    if not mejores:
        return None
    lin = []
    for s, i in mejores:
        a = acts[i]; ins = [r.insumos[c] for c in a["insumos"] if c in r.insumos][:12]
        lin.append(f"- **INVIAS {a['numeral']} — {a['descripcion'].split(chr(10))[0].strip()[:90]}** (unidad {a['unidad']}; coincidencia {s:.2f}): " + "; ".join(f"{x['descripcion']} ({x['unidad']}, {x['tipo']})" for x in ins) + ".")
    lin.append("- **Límite:** composición de actividades de obra vial del catálogo INVIAS 2026-1 (solo los insumos, sin cantidades ni rendimientos); no es un APU completo ni sustituye el criterio de un presupuestador.")
    return ResultadoPlugin("insumos_actividad", "\n".join(lin), "Composición de actividades INVIAS 2026-1 (invias_actividad_insumos)", ", ".join(acts[i]["numeral"] for _, i in mejores))


# ───────────────────────────── Orquestación ─────────────────────────────
def ejecutar_plugins(pregunta: str, sb=None, detectar_municipio=None) -> list[ResultadoPlugin]:
    """Ejecuta los plugins que se activan; cada uno aislado (un fallo no afecta a los demás ni al chat)."""
    pasos: list[tuple[str, Callable[[], Optional[ResultadoPlugin]]]] = []
    if activar_enso(pregunta):
        pasos.append(("enso", lambda: ejecutar_enso(pregunta, detectar_municipio)))
    if activar_vigencia(pregunta):
        pasos.append(("vigencia", lambda: ejecutar_vigencia(pregunta, sb)))
    if activar_precio(pregunta):
        pasos.append(("precio", lambda: ejecutar_precio(pregunta)))
    if activar_insumos(pregunta):
        pasos.append(("insumos", lambda: ejecutar_insumos(pregunta)))
    out = []
    for nombre, f in pasos:
        try:
            r = f()
            if r:
                out.append(r)
        except Exception as e:  # noqa: BLE001
            logger.warning("plugin %s falló: %s", nombre, e)
    return out


def aplicar(resultado: dict, pregunta: str, sb=None, detectar_municipio=None) -> dict:
    """Devuelve una COPIA de `resultado` con la sección de plugins añadida a la respuesta y sus fuentes sumadas. Idempotente."""
    if "plugins_usados" in resultado:
        return resultado
    plugins = ejecutar_plugins(pregunta, sb, detectar_municipio)
    if not plugins:
        return resultado
    nuevo = dict(resultado)
    nuevo["respuesta"] = (resultado.get("respuesta") or "") + "\n\n---\n**Datos verificados por StructAI (módulos determinísticos)**\n\n" + "\n\n".join(p.markdown for p in plugins)
    nuevo["fuentes"] = [{"norma": p.fuente, "seccion": p.seccion, "score": 1.0} for p in plugins] + list(resultado.get("fuentes") or [])
    citadas = list(resultado.get("normas_citadas") or [])
    nuevo["normas_citadas"] = [p.fuente for p in plugins if p.fuente not in citadas] + citadas
    nuevo["plugins_usados"] = [p.nombre for p in plugins]
    return nuevo


MENSAJE_DEGRADADO = ("No pude redactar una respuesta completa porque el servicio de IA está saturado en este momento. Esto es lo que StructAI sí pudo verificar "
                     "con sus módulos determinísticos, que no dependen del modelo de lenguaje:")


def respuesta_degradada(pregunta: str, sb=None, detectar_municipio=None) -> Optional[dict]:
    """Respuesta de emergencia cuando el modelo de lenguaje no está disponible: si algún plugin sí tiene respuesta, se devuelve solo ella (marcada `degradado`);
    si ninguno aplica, None y el llamador debe propagar el error original. Evita que una pregunta de vigencia, ENSO o precio falle por completo aunque el dato exista."""
    base = {"respuesta": MENSAJE_DEGRADADO, "normas_citadas": [], "fuentes": [], "chunks_usados": 0, "degradado": True, "dominio": "normativa_general"}
    res = aplicar(base, pregunta, sb, detectar_municipio)
    return res if res is not base else None
