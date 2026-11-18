"""
Ficha territorial de un sitio de Colombia y pre-diseño de la exploración geotécnica (#273).

Dada una coordenada (por ejemplo, el GPS del celular) o un código DIVIPOLA, encadena datos que StructAI ya tiene:

  1. Coordenada → municipio: consulta de punto en polígono al MapServer del SGC «Municipios_Amenaza_NR10»
     (devuelve código DIVIPOLA, Aa, Av y zona). Verificado en vivo el 2026-11-18 con un punto de Bogotá → 11001.
  2. Cruce por código DIVIPOLA en Supabase (1.088 municipios coinciden en las cuatro tablas):
       nsr10_apendice_a4_municipios   Aa, Av, Ae, Ad oficiales (NSR-10 Apéndice A-4)
       igac_suelos_ufh                textura, drenaje e inundabilidad por área (agronómico: primer metro y medio)
       ungrd_emergencias              eventos 2019–2024 y daños (viviendas, vías, puentes)
       sisben_vulnerabilidad_...      porcentaje de viviendas con material vulnerable
  3. Proximidad: estación IDEAM de caudal más cercana y movimientos en masa del SGC (SIMMA) a 15 km.
  4. Microzonificación (Bogotá, Cali, Pereira): las zonas del municipio con el método de cimentación que aplicaría.
     Ubicar el punto dentro de una zona requiere los polígonos, que aún no están cargados (próximamente).

Salida orientativa: NO reemplaza el estudio geotécnico (NSR-10 Título H). Sin sondeo no hay N ni Su.

Privacidad (Ley 1581): la coordenada se redondea a 0,01° (~1 km) antes de cualquier consulta externa y no se registra
en logs; la ficha solo devuelve la coordenada redondeada.

Ninguna función lanza por fallas de red o de datos: cada fuente que falla queda como `None` y se lista en
`fuentes_no_disponibles`, igual que el contrato de sgc_amenaza_sismica.py.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Callable, Optional

import httpx

log = logging.getLogger(__name__)

SGC_MUNICIPIOS_URL = (
    "http://srvags.sgc.gov.co/arcgis/rest/services/"
    "Zonas_amenaza_Sismica_NR10/Municipios_Amenaza_NR10/MapServer/0/query"
)
DECIMALES_PRIVACIDAD = 2          # 0,01° ≈ 1,1 km
# Caja de Colombia continental e insular (San Andrés ≈ −81,7°; Leticia ≈ −4,2°; Punta Gallinas ≈ 12,5°)
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = -4.3, 13.6, -82.0, -66.8
RADIO_IDEAM_GRADOS = 0.5
_PAGINA = 1000
_MAX_FILAS_IGAC = 10_000

CIUDADES_MICROZONIFICACION = {"11001": "Bogotá, D.C.", "76001": "Santiago de Cali", "66001": "Pereira"}

EVENTOS_HIDRICOS = {"INUNDACION", "CRECIENTE SUBITA", "AVENIDA TORRENCIAL"}
DRENAJE_DEFICIENTE = {"Imperfecto", "Pobre", "Muy pobre"}
INUNDACION_PROLONGADA = {"Largas", "Muy largas"}
DANOS_UNGRD = ("viviendas_destruidas", "viviendas_averiadas", "vias_averiadas", "puentes_vehiculares",
               "puentes_peatonales")


# ── 1. coordenada → municipio ─────────────────────────────────────────────────────────────────────────────────────

def redondear(lat: float, lon: float) -> tuple[float, float]:
    """Valida que la coordenada esté en Colombia y la redondea a 0,01° (privacidad)."""
    for nombre, v in (("lat", lat), ("lon", lon)):
        if not (isinstance(v, (int, float)) and math.isfinite(v)):
            raise ValueError(f"{nombre} debe ser un número finito")
    if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
        raise ValueError("La coordenada está fuera de Colombia")
    return round(lat, DECIMALES_PRIVACIDAD), round(lon, DECIMALES_PRIVACIDAD)


def municipio_por_coordenada(lat: float, lon: float, *, http_get: Callable = httpx.get) -> Optional[dict]:
    """Punto en polígono contra el SGC. Recibe la coordenada ya redondeada. None si no hay municipio o falla el servicio."""
    try:
        r = http_get(SGC_MUNICIPIOS_URL, params={
            "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects", "returnGeometry": "false", "f": "json",
            "outFields": "NOMBRE_MUNICIPIO,NOMBRE_DEPARTAMENTO,CÓDIGO_MUNICIPIO,AA,AV,ZONA_AMENAZA_SÍSMICA,LATITUD,LONGITUD",
        }, timeout=8.0)
        r.raise_for_status()
        datos = r.json()
        feats = datos.get("features") or []
        if "error" in datos or not feats:
            return None
        a = feats[0].get("attributes", {})
        codigo = str(a.get("CÓDIGO_MUNICIPIO") or "").strip().zfill(5)
        if not codigo.strip("0"):
            return None
        return {"codigo_municipio": codigo, "municipio": a.get("NOMBRE_MUNICIPIO"),
                "departamento": a.get("NOMBRE_DEPARTAMENTO"), "aa_sgc": a.get("AA"), "av_sgc": a.get("AV"),
                "zona_amenaza_sgc": a.get("ZONA_AMENAZA_SÍSMICA"),
                "centroide": ({"lat": a["LATITUD"], "lon": a["LONGITUD"]}
                              if a.get("LATITUD") is not None and a.get("LONGITUD") is not None else None)}
    except Exception as e:  # noqa: BLE001 -- contrato: nunca lanza
        log.warning("SGC municipios: servicio no disponible (%s)", type(e).__name__)
        return None


# ── 2. cruces por DIVIPOLA ────────────────────────────────────────────────────────────────────────────────────────

def _filas(sb, tabla: str, columnas: str, campo: str, valor: str, maximo: int = _MAX_FILAS_IGAC) -> list[dict]:
    """Lectura paginada (PostgREST trunca a 1.000 filas sin avisar; ver test_sgc_amenaza_sismica_paginacion.py)."""
    out: list[dict] = []
    while len(out) < maximo:
        lote = (sb.table(tabla).select(columnas).eq(campo, valor)
                .range(len(out), len(out) + _PAGINA - 1).execute().data or [])
        out.extend(lote)
        if len(lote) < _PAGINA:
            break
    return out


def sismo_nsr10(sb, codigo: str) -> Optional[dict]:
    f = _filas(sb, "nsr10_apendice_a4_municipios", "codigo,municipio,departamento,aa,av,ae,ad,zona", "codigo", codigo, 1)
    return f[0] if f else None


def suelos_igac(sb, codigo: str) -> Optional[dict]:
    filas = _filas(sb, "igac_suelos_ufh", "textura,drenaje,inund,area_ha", "cod_dane_municipio", codigo)
    total = sum(float(f.get("area_ha") or 0) for f in filas)
    if not filas or total <= 0:
        return None

    def reparto(campo: str) -> dict[str, float]:
        acc: dict[str, float] = {}
        for f in filas:
            k = f.get(campo) or "Sin dato"
            acc[k] = acc.get(k, 0.0) + float(f.get("area_ha") or 0)
        return {k: round(v / total, 3) for k, v in sorted(acc.items(), key=lambda kv: -kv[1])}

    drenaje, inund = reparto("drenaje"), reparto("inund")
    return {"area_ha": round(total), "unidades": len(filas), "textura": reparto("textura"), "drenaje": drenaje,
            "inundabilidad": inund,
            "fraccion_drenaje_deficiente": round(sum(v for k, v in drenaje.items() if k in DRENAJE_DEFICIENTE), 3),
            "fraccion_inundacion_prolongada": round(sum(v for k, v in inund.items() if k in INUNDACION_PROLONGADA), 3),
            "advertencia": "Levantamiento agronómico (primer metro y medio): no sirve para diseñar cimentaciones."}


def emergencias_ungrd(sb, codigo: str) -> Optional[dict]:
    filas = _filas(sb, "ungrd_emergencias", "fecha,evento," + ",".join(DANOS_UNGRD), "codigo_municipio", codigo)
    if not filas:
        return None
    por_evento: dict[str, int] = {}
    danos = {k: 0 for k in DANOS_UNGRD}
    puentes_hidricos = 0
    for f in filas:
        ev = (f.get("evento") or "SIN CLASIFICAR").strip().upper()
        por_evento[ev] = por_evento.get(ev, 0) + 1
        for k in DANOS_UNGRD:
            danos[k] += int(f.get(k) or 0)
        if ev in EVENTOS_HIDRICOS:
            puentes_hidricos += int(f.get("puentes_vehiculares") or 0)
    fechas = sorted(str(f["fecha"]) for f in filas if f.get("fecha"))
    return {"eventos": len(filas), "periodo": [fechas[0][:10], fechas[-1][:10]] if fechas else None,
            "por_evento": dict(sorted(por_evento.items(), key=lambda kv: -kv[1])), "danos": danos,
            "puentes_vehiculares_por_eventos_hidricos": puentes_hidricos}


def vulnerabilidad_sisben(sb, codigo: str) -> Optional[dict]:
    f = _filas(sb, "sisben_vulnerabilidad_vivienda_municipio",
               "n_viviendas_muestra,n_viviendas_material_vulnerable,pct_material_vulnerable,corte",
               "codigo_municipio", codigo, 1)
    return f[0] if f else None


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def estacion_ideam_cercana(sb, lat: float, lon: float) -> Optional[dict]:
    r = RADIO_IDEAM_GRADOS
    filas = (sb.table("ideam_estaciones_caudal").select("codigo,nombre,corriente,municipio,estado,latitud,longitud")
             .gte("latitud", lat - r).lte("latitud", lat + r).gte("longitud", lon - r).lte("longitud", lon + r)
             .limit(_PAGINA).execute().data or [])
    filas = [f for f in filas if f.get("latitud") is not None and f.get("longitud") is not None]
    if not filas:
        return None
    mejor = min(filas, key=lambda f: distancia_km(lat, lon, f["latitud"], f["longitud"]))
    return {"codigo": mejor["codigo"], "nombre": mejor["nombre"], "corriente": mejor.get("corriente"),
            "estado": mejor.get("estado"), "distancia_km": round(distancia_km(lat, lon, mejor["latitud"],
                                                                                mejor["longitud"]), 1)}


def metodo_por_zona(descripcion: str) -> str:
    """Método de cimentación profunda que aplicaría según la descripción geológica de la zona (orientativo)."""
    d = (descripcion or "").lower()
    if any(k in d for k in ("roca", "cerros")):
        return "Roca o suelo residual somero: cimentación en roca (NSR-10 H.4.7-4), próximamente en motor-pilotes."
    if any(k in d for k in ("piedemonte", "coluvial", "bloques", "cantos", "grava", "torrencial")):
        return ("Gravas con bloques: SPT poco confiable (rechazo); β de grava si N60 ≤ 50, geomaterial intermedio "
                "próximamente. Pedir exploración con perforación rotativa.")
    if "lacustre" in d or ("arcilla" in d and "aluvial" not in d):
        return ("Arcilla blanda: método α de la NSR-10 (validado conservador, λ = 1,48). Pedir ensayos de Su por "
                "estrato y evaluar fricción negativa y asentamientos.")
    if any(k in d for k in ("aluvial", "arena", "abanico", "llanura", "licuación")):
        return ("Perfil aluvial, probablemente mixto arcilla + arena: perfil mixto del motor (SPT del CCP-14 en arena; "
                "λ = 0,96 con 14 % de pruebas bajo la admisible). Pedir SPT con medición de energía y evaluar licuación.")
    return "Según exploración: la descripción de la zona no permite anticipar el método."


def microzonificacion(sb, codigo: str) -> Optional[dict]:
    ciudad = CIUDADES_MICROZONIFICACION.get(codigo)
    if not ciudad:
        return None
    filas = _filas(sb, "microzonificacion_sismica_local", "zona,descripcion_zona,fa_diseno,fv_diseno,fuente",
                   "ciudad", ciudad, 200)
    return {"ciudad": ciudad,
            "nota": "Sin polígonos cargados todavía: se listan todas las zonas; ubicar el punto en una zona está "
                    "próximamente.",
            "zonas": [{"zona": f["zona"], "descripcion": f.get("descripcion_zona"), "fa": f.get("fa_diseno"),
                       "fv": f.get("fv_diseno"), "metodo_cimentacion_orientativo": metodo_por_zona(
                           f.get("descripcion_zona") or "")} for f in filas]}


# ── 3b. indicador hídrico (H3/H5, #273) ───────────────────────────────────────────────────────────────────────────

_INDICE_HIDRICO: Optional[dict] = None
RUTA_INDICE_HIDRICO = Path(__file__).resolve().parent / "data" / "indice_hidrico_h3.json"
PERCENTIL_HIDRICO_ALTO = 0.80


def _indice_hidrico() -> dict:
    global _INDICE_HIDRICO
    if _INDICE_HIDRICO is None:
        _INDICE_HIDRICO = json.loads(RUTA_INDICE_HIDRICO.read_text(encoding="utf-8"))
    return _INDICE_HIDRICO


def indicador_hidrico(codigo: str) -> Optional[dict]:
    """Índice de riesgo hídrico para puentes y vías (H3) del municipio, con su respaldo. None si no está en la cobertura."""
    d = _indice_hidrico()
    m = d["municipios"].get(codigo)
    if m is None:
        return None
    q = m["percentil"]
    nivel = "alto" if q >= PERCENTIL_HIDRICO_ALTO else ("medio" if q >= 0.5 else "bajo")
    return {**m, "nivel": nivel, "version": d["version"], "metodo": d["metodo"], "validacion": d["validacion"],
            "cobertura": d["cobertura"],
            "contexto": "En 2019-2024, el 73 % del daño estructural reportado por la UNGRD (viviendas, vías y puentes) "
                        "fue de origen hídrico y el 0,4 % sísmico (H5, #273). El Aa de la NSR-10 no ordena ese daño una vez "
                        "descontados relieve, población y reporte: el indicador hídrico complementa al sísmico, no lo "
                        "reemplaza.",
            "uso": "Priorizar inspección y estudios hidráulicos; no sirve para diseñar."}


# ── 4. pre-diseño de la exploración ───────────────────────────────────────────────────────────────────────────────

def recomendaciones(ficha: dict) -> list[dict]:
    """Qué pedir en el estudio geotécnico según los datos del sitio. Cada ítem cita el dato que lo dispara."""
    rec: list[dict] = []
    s = ficha.get("sismo_nsr10") or {}
    aa = s.get("aa")
    if isinstance(aa, (int, float)) and aa >= 0.15:
        rec.append({"tema": "sismo", "por_que": f"Aa = {aa} (NSR-10 A-4), amenaza {s.get('zona', '').lower()}",
                    "pedir": "Clasificación del perfil de suelo (NSR-10 A.2.4: Vs30 o N̄) y, si hay arenas bajo el "
                             "nivel freático, evaluación de licuación."})
    g = ficha.get("suelos_igac") or {}
    if g.get("fraccion_drenaje_deficiente", 0) >= 0.25 or g.get("fraccion_inundacion_prolongada", 0) >= 0.10:
        rec.append({"tema": "agua", "por_que": f"IGAC: {g.get('fraccion_drenaje_deficiente', 0):.0%} del área con "
                                               f"drenaje deficiente y {g.get('fraccion_inundacion_prolongada', 0):.0%} "
                                               "con inundaciones largas",
                    "pedir": "Nivel freático medido (piezómetro o lectura estabilizada en sondeo), no supuesto."})
    u = ficha.get("emergencias_ungrd") or {}
    if u.get("puentes_vehiculares_por_eventos_hidricos", 0) > 0:
        rec.append({"tema": "socavacion",
                    "por_que": f"UNGRD: {u['puentes_vehiculares_por_eventos_hidricos']} puentes vehiculares averiados "
                               "por inundación o creciente en el municipio",
                    "pedir": "Si la obra es un puente o está junto a un cauce: estudio hidráulico y de socavación local "
                             "(CCP-14 Sección 2)."})
    h = ficha.get("indicador_hidrico") or {}
    if h.get("nivel") == "alto":
        rec.append({"tema": "hidrico",
                    "por_que": f"Indicador hídrico en el percentil {h['percentil']:.0%} de {h['cobertura']} (H3: AUC 0,75 "
                               "para puentes averiados)",
                    "pedir": "Estudio hidrológico e hidráulico del sitio (crecientes, drenaje, socavación si hay cauce) "
                             "antes de definir cimentación y cota de implantación."})
    m = ficha.get("movimientos_masa") or {}
    if m.get("total", 0) > 0:
        rec.append({"tema": "ladera", "por_que": f"SGC SIMMA: {m['total']} movimientos en masa a {m.get('radio_km')} km",
                    "pedir": "Evaluación de estabilidad de ladera si el sitio tiene pendiente (NSR-10 H.6)."})
    rec.append({"tema": "cimentacion_profunda",
                "por_que": "En la validación de #118, el método SPT en arena dejó el 14 % de las pruebas con capacidad "
                           "medida por debajo de la admisible",
                "pedir": "Si se proyectan pilotes: prueba de carga (ASTM D1143) o PDA. APU INVIAS 2026-1 las cotiza "
                         "entre ≈ $9 y $12,5 M por unidad (valor por verificar)."})
    return rec


# ── ficha completa ────────────────────────────────────────────────────────────────────────────────────────────────

def ficha_sitio(sb, *, lat: Optional[float] = None, lon: Optional[float] = None, codigo_municipio: Optional[str] = None,
                http_get: Callable = httpx.get, simma: Optional[Callable] = None) -> dict:
    """Ficha territorial. Con lat/lon resuelve el municipio en el SGC; con codigo_municipio va directo al cruce."""
    if (lat is None) != (lon is None):
        raise ValueError("Envíe lat y lon juntos")
    if lat is None and not codigo_municipio:
        raise ValueError("Envíe lat/lon o codigo_municipio")
    no_disponibles: list[str] = []
    punto = None
    municipio = None
    if lat is not None:
        lat_r, lon_r = redondear(lat, lon)
        punto = {"lat": lat_r, "lon": lon_r, "precision": "0,01° (~1 km), redondeada por privacidad"}
        municipio = municipio_por_coordenada(lat_r, lon_r, http_get=http_get)
        if municipio is None:
            no_disponibles.append("sgc_municipio")
            if not codigo_municipio:
                return {"punto": punto, "municipio": None, "fuentes_no_disponibles": no_disponibles,
                        "recomendaciones": [], "aviso": _AVISO}
        codigo_municipio = (municipio or {}).get("codigo_municipio") or codigo_municipio
    codigo = str(codigo_municipio).strip().zfill(5)
    if not (codigo.isdigit() and len(codigo) == 5):
        raise ValueError("codigo_municipio debe ser el código DIVIPOLA de 5 dígitos")

    ficha: dict[str, Any] = {"punto": punto, "municipio": municipio or {"codigo_municipio": codigo}}

    def _fuente(nombre: str, fn: Callable, *args):
        try:
            v = fn(*args)
        except Exception as e:  # noqa: BLE001 -- contrato: una fuente caída no tumba la ficha
            log.warning("sitio: fuente %s no disponible (%s)", nombre, type(e).__name__)
            v = None
        if v is None:
            no_disponibles.append(nombre)
        ficha[nombre] = v

    _fuente("sismo_nsr10", sismo_nsr10, sb, codigo)
    if municipio is None and ficha["sismo_nsr10"]:
        ficha["municipio"] = {"codigo_municipio": codigo, "municipio": ficha["sismo_nsr10"].get("municipio"),
                              "departamento": ficha["sismo_nsr10"].get("departamento")}
    _fuente("suelos_igac", suelos_igac, sb, codigo)
    _fuente("emergencias_ungrd", emergencias_ungrd, sb, codigo)
    _fuente("vulnerabilidad_sisben", vulnerabilidad_sisben, sb, codigo)
    _fuente("microzonificacion", microzonificacion, sb, codigo)
    _fuente("indicador_hidrico", indicador_hidrico, codigo)
    if ficha["microzonificacion"] is None and codigo not in CIUDADES_MICROZONIFICACION:
        no_disponibles.remove("microzonificacion")          # no es una falla: el municipio no tiene estudio cargado
    if ficha["indicador_hidrico"] is None and "indicador_hidrico" in no_disponibles and RUTA_INDICE_HIDRICO.exists():
        no_disponibles.remove("indicador_hidrico")          # fuera de la cobertura del panel (21 departamentos)
        ficha["indicador_hidrico"] = {"nivel": "sin_dato", "cobertura": _indice_hidrico()["cobertura"]}
    ref = punto or (municipio or {}).get("centroide")
    if ref:
        _fuente("estacion_ideam_cercana", estacion_ideam_cercana, sb, ref["lat"], ref["lon"])
        if simma is None:
            import sgc_movimientos_masa
            simma = sgc_movimientos_masa.consultar_movimientos_cercanos
        _fuente("movimientos_masa", simma, ref["lat"], ref["lon"])
    ficha["fuentes_no_disponibles"] = no_disponibles
    ficha["recomendaciones"] = recomendaciones(ficha)
    ficha["aviso"] = _AVISO
    return ficha


_AVISO = ("Ficha orientativa a partir de datos públicos (SGC, NSR-10 A-4, IGAC, UNGRD, Sisbén, IDEAM) y del indicador "
          "hídrico de StructAI (#273). No reemplaza el "
          "estudio geotécnico exigido por la NSR-10 Título H; sirve para planear qué exploración pedir.")
