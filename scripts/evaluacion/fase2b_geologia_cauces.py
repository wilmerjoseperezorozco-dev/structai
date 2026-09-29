"""Fase 2b (issue #61): las 2 variables restantes del paper de Medellin
que faltaban -- geologia y distancia a cauces -- via el servicio real del
SGC (srvags.sgc.gov.co, mismo dominio ya usado por sgc_amenaza_sismica.py
y sgc_movimientos_masa.py, encontrado hoy: Mapa_Geologico_Colombia_V2023,
capa 733=Unidades Cronoestratigraficas, capa 728=Drenaje_Sencillo).

Limitacion honesta, documentada a proposito: es un mapa a escala
1:500.000 (nacional) -- solo tiene los rios/cauces PRINCIPALES, no la red
fina de un mapa 1:25.000 como el que probablemente uso el paper de
Medellin para su area metropolitana. La distancia a cauces calculada aqui
es real (viene del servicio oficial del SGC), pero mas gruesa/conservadora
que la del paper original -- confirmado en pruebas: no hay drenaje
mapeado dentro de 5km en varios puntos reales, hace falta expandir el
buffer hasta 10-20km en zonas rurales."""
import io
import math
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import httpx
import rag_multi_norma as rm
import divipola
from scipy.stats import mannwhitneyu, chi2_contingency

BASE_SGC = "https://srvags.sgc.gov.co/arcgis/rest/services/Mapa_Geologico_Colombia/Mapa_Geologico_Colombia_V2023/MapServer"
CAPA_GEOLOGIA = 733
CAPA_DRENAJE = 728
BUFFERS_KM = [2, 5, 10, 20, 40]  # expansion progresiva, nunca asumir un radio fijo
TAM_PAGINA = 1000


def _paginar(tabla: str, columnas: str, filtro=None) -> list[dict]:
    filas = []
    inicio = 0
    while True:
        q = rm.sb.table(tabla).select(columnas).range(inicio, inicio + TAM_PAGINA - 1)
        if filtro is not None:
            q = filtro(q)
        pagina = q.execute().data or []
        filas.extend(pagina)
        if len(pagina) < TAM_PAGINA:
            break
        inicio += TAM_PAGINA
    return filas


def reconstruir_grupos() -> tuple[list[dict], list[dict]]:
    from collections import Counter
    todos_eventos = _paginar("ungrd_emergencias", "municipio,departamento,evento", None)
    municipios_con_algun_evento = {
        (e["municipio"] or "").strip().upper() for e in todos_eventos if e.get("municipio")
    }
    conteo_mm: Counter = Counter()
    depto_de: dict[str, str] = {}
    for e in todos_eventos:
        if e["evento"] == "MOVIMIENTO EN MASA":
            clave = (e["municipio"] or "").strip().upper()
            if clave:
                conteo_mm[clave] += 1
                depto_de[clave] = e.get("departamento") or ""

    todos_municipios = _paginar("sgc_amenaza_sismica_municipios", "municipio,departamento", None)
    universo = {}
    for m in todos_municipios:
        clave = (m["municipio"] or "").strip().upper()
        if clave and clave not in universo:
            universo[clave] = m.get("departamento") or ""

    top15_claves = [m for m, _ in conteo_mm.most_common(15)]
    grupo_alto = [{"municipio": k, "departamento": depto_de.get(k, universo.get(k, ""))} for k in top15_claves]

    grupo_bajo_claves = (set(universo) - set(conteo_mm)) & municipios_con_algun_evento
    grupo_bajo = [{"municipio": k, "departamento": universo[k]} for k in grupo_bajo_claves]
    return grupo_alto, grupo_bajo


def obtener_coordenadas(grupo: list[dict]) -> list[dict]:
    con_coords = []
    for m in grupo:
        r = divipola.resolver_municipio(m["municipio"], m["departamento"])
        if r and r.get("latitud") is not None:
            con_coords.append({**m, "lat": r["latitud"], "lon": r["longitud"]})
    return con_coords


def consultar_geologia(lat: float, lon: float) -> str | None:
    """Devuelve el CodigoUC (unidad cronoestratigrafica) real en ese punto,
    o None si el punto no cae dentro de ningun poligono mapeado (posible
    en el mar/limites de mapa)."""
    try:
        r = httpx.get(f"{BASE_SGC}/{CAPA_GEOLOGIA}/query", params={
            "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
            "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
            "outFields": "CodigoUC,Edad", "f": "json",
        }, timeout=20.0)
        data = r.json()
        feats = data.get("features", [])
        if feats:
            return feats[0]["attributes"].get("CodigoUC")
    except Exception:
        pass
    return None


def _dist_punto_segmento_m(px, py, ax, ay, bx, by) -> float:
    """Distancia real (metros, aproximacion plana valida a esta escala
    cerca del ecuador) de un punto a un segmento de linea."""
    factor_lon = 111320 * math.cos(math.radians(py))
    factor_lat = 111320
    pxm, pym = px * factor_lon, py * factor_lat
    axm, aym = ax * factor_lon, ay * factor_lat
    bxm, bym = bx * factor_lon, by * factor_lat
    dx, dy = bxm - axm, bym - aym
    if dx == 0 and dy == 0:
        return math.hypot(pxm - axm, pym - aym)
    t = max(0, min(1, ((pxm - axm) * dx + (pym - aym) * dy) / (dx * dx + dy * dy)))
    cx, cy = axm + t * dx, aym + t * dy
    return math.hypot(pxm - cx, pym - cy)


def consultar_distancia_cauce_m(lat: float, lon: float) -> float | None:
    """Busca el drenaje mapeado mas cercano expandiendo el buffer de
    busqueda progresivamente (2/5/10/20/40km) -- nunca asume un radio fijo,
    porque el mapa 1:500.000 no tiene drenaje en cada km2. Calcula la
    distancia real punto-a-segmento sobre las geometrias devueltas, no solo
    'esta dentro del buffer si/no'."""
    for buffer_km in BUFFERS_KM:
        try:
            r = httpx.get(f"{BASE_SGC}/{CAPA_DRENAJE}/query", params={
                "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
                "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
                "distance": str(buffer_km * 1000), "units": "esriSRUnit_Meter",
                "outFields": "OBJECTID", "returnGeometry": "true", "f": "json",
            }, timeout=25.0)
            data = r.json()
            feats = data.get("features", [])
            if not feats:
                continue
            min_dist = float("inf")
            for feat in feats:
                paths = feat.get("geometry", {}).get("paths", [])
                for path in paths:
                    for i in range(len(path) - 1):
                        ax, ay = path[i]
                        bx, by = path[i + 1]
                        d = _dist_punto_segmento_m(lon, lat, ax, ay, bx, by)
                        min_dist = min(min_dist, d)
            if min_dist < float("inf"):
                return min_dist
        except Exception:
            continue
    return None


def main() -> None:
    print("=== Reconstruyendo grupos (mismo criterio de Fase 1c) ===")
    grupo_alto_raw, grupo_bajo_raw = reconstruir_grupos()
    grupo_alto = obtener_coordenadas(grupo_alto_raw)
    grupo_bajo = obtener_coordenadas(grupo_bajo_raw)
    print(f"ALTO: {len(grupo_alto)} municipios | BAJO: {len(grupo_bajo)} municipios")

    print("\n=== Geología + distancia a cauces por municipio (esto tarda, ~232 municipios x 2 consultas) ===")
    resultados_alto, resultados_bajo = [], []
    for grupo, resultados, etiqueta in [(grupo_alto, resultados_alto, "ALTO"), (grupo_bajo, resultados_bajo, "BAJO")]:
        for i, m in enumerate(grupo):
            geo = consultar_geologia(m["lat"], m["lon"])
            dist = consultar_distancia_cauce_m(m["lat"], m["lon"])
            resultados.append({"municipio": m["municipio"], "geologia": geo, "distancia_cauce_m": dist})
            if (i + 1) % 25 == 0:
                print(f"  {etiqueta}: {i+1}/{len(grupo)}")
            time.sleep(0.15)

    print("\n=== Resultado: distancia a cauce (m) ===")
    import statistics
    d_alto = [r["distancia_cauce_m"] for r in resultados_alto if r["distancia_cauce_m"] is not None]
    d_bajo = [r["distancia_cauce_m"] for r in resultados_bajo if r["distancia_cauce_m"] is not None]
    print(f"ALTO: n={len(d_alto)}, mediana={statistics.median(d_alto):.0f}m, media={statistics.mean(d_alto):.0f}m")
    print(f"BAJO: n={len(d_bajo)}, mediana={statistics.median(d_bajo):.0f}m, media={statistics.mean(d_bajo):.0f}m")
    if d_alto and d_bajo:
        u, p = mannwhitneyu(d_alto, d_bajo, alternative="less")
        print(f"Mann-Whitney U (ALTO < BAJO, más cerca del cauce) = {u:.1f}, p = {p:.2e}")

    print("\n=== Resultado: geología (unidades distintas por grupo) ===")
    from collections import Counter
    geo_alto = Counter(r["geologia"] for r in resultados_alto if r["geologia"])
    geo_bajo = Counter(r["geologia"] for r in resultados_bajo if r["geologia"])
    print(f"ALTO: {len(geo_alto)} unidades geológicas distintas en {sum(geo_alto.values())} municipios con dato")
    print(f"BAJO: {len(geo_bajo)} unidades geológicas distintas en {sum(geo_bajo.values())} municipios con dato")
    print("Top 5 unidades en ALTO:", geo_alto.most_common(5))
    print("Top 5 unidades en BAJO:", geo_bajo.most_common(5))

    import json
    out = {"grupo_alto": resultados_alto, "grupo_bajo": resultados_bajo}
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase2b_geologia_cauces_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
