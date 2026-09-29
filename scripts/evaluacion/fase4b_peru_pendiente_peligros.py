"""Fase 4b (issue #20/#23): primera prueba real de replicabilidad del
hallazgo mas fuerte de #61 (pendiente vs. movimiento en masa) en Peru,
usando SOLO fuentes verificadas EN VIVO el 2026-09-29 -- no se asume que
Peru tenga lo mismo que Colombia, se prueba cada endpoint antes de usarlo.

Fuentes reales verificadas hoy:
1. INGEMMET GeoCatMin (geocatmin.ingemmet.gob.pe/arcgis/rest/services) --
   directorio ArcGIS REST publico y funcional, mismo patron que
   sgc_movimientos_masa.py. Capa real usada aqui:
   SERV_PELIGROS_GEOLOGICOS/MapServer/0 ("Peligros Geologicos", PUNTOS,
   28.915 eventos reales consultables, actualizado a inicios de 2012,
   incluye deslizamientos/derrumbes/huaycos por el campo TIP_PELIGRO) --
   el equivalente real mas cercano a SIMMA que tiene Peru.
2. SERV_SUSCEPTIBLE_MOV_MASA_REGIONAL/MapServer/0 ("Regiones", POLIGONOS,
   limites departamentales con el campo NOM_DPTO) -- usado SOLO para
   obtener un punto representativo (centroide) por departamento, no como
   fuente de amenaza en si.
3. OpenTopoData (SRTM30m, ya usado en fase2_elevacion_continua.py) --
   funciona igual de bien fuera de Colombia, es un dataset global.

LIMITACION METODOLOGICA IMPORTANTE, declarada desde el diseno del script
(no despues de ver el resultado): a diferencia de Colombia (1.121
municipios, unidad administrativa pequena y razonablemente homogenea),
aqui se trabaja a nivel de DEPARTAMENTO (25 unidades, extensiones enormes
y geograficamente muy heterogeneas -- ej. Ancash tiene costa Y alta
cordillera). Un solo centroide y un radio de busqueda fijo son una
aproximacion mucho mas gruesa que el analisis municipal de #61 -- este
script es una PRIMERA PRUEBA DE REPLICABILIDAD TECNICA, no un reemplazo
del rigor de la Fase 0-2 original.

ESTADO REAL (2026-09-29): el diseno y las 3 fuentes estan verificados en
vivo (via navegador -- consulta espacial real probada contra
SERV_PELIGROS_GEOLOGICOS con el mismo patron de parametros que
sgc_movimientos_masa.py, y conteo real confirmado: 28.915 eventos totales,
docenas dentro de un radio de 15km real cerca de Cusco). Pero ejecutar
este script con httpx desde Python falla con
CERTIFICATE_VERIFY_FAILED -- geocatmin.ingemmet.gob.pe sirve una cadena
de certificado incompleta (falta el intermedio) que el navegador tolera
por un mecanismo de validacion mas permisivo, pero que Python/httpx con
certifi rechaza correctamente. Desactivar la verificacion TLS fue
bloqueado por el clasificador de seguridad del entorno (correctamente) --
no se debilito la verificacion para evitar este bloqueo. Pendiente real:
o bien conseguir/instalar el certificado intermedio correcto, o pedir
permiso explicito y acotado para este host publico especifico, o
recolectar los mismos datos vía el navegador (mas lento, ~25+ llamadas
manuales) en vez de este script."""
import io
import json
import math
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import httpx
from scipy.stats import mannwhitneyu
from shapely.geometry import shape

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_INGEMMET_REGIONES = (
    "https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/"
    "SERV_SUSCEPTIBLE_MOV_MASA_REGIONAL/MapServer/0/query"
)
_INGEMMET_PELIGROS = (
    "https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/"
    "SERV_PELIGROS_GEOLOGICOS/MapServer/0/query"
)
_OPENTOPODATA = "https://api.opentopodata.org/v1/srtm30m"
_RADIO_METROS = 60000  # 60km -- mucho mas grande que los 15km de Colombia,
# a proposito: la unidad aqui es departamento, no municipio.
_TIMEOUT = 20.0


def obtener_regiones() -> list[dict]:
    """Descarga los 25 departamentos reales con su geometria (INEI 2011,
    via INGEMMET) y calcula un centroide real por poligono (shapely) --
    no se inventa ninguna coordenada."""
    resp = httpx.get(
        _INGEMMET_REGIONES,
        params={
            "where": "1=1",
            "outFields": "NOM_DPTO,CAPITAL",
            "returnGeometry": "true",
            "geometryPrecision": 4,
            "outSR": 4326,
            "f": "json",
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    regiones = []
    for f in data.get("features", []):
        rings = f["geometry"]["rings"]
        # geometria esriPolygon -> geojson-like para shapely (mismo anillo
        # exterior mas grande si hay islas/multi-parte, criterio simple y
        # razonable para un centroide aproximado)
        anillo_mayor = max(rings, key=lambda r: len(r))
        poligono = shape({"type": "Polygon", "coordinates": [anillo_mayor]})
        centroide = poligono.centroid
        regiones.append({
            "departamento": f["attributes"]["NOM_DPTO"],
            "capital": f["attributes"]["CAPITAL"],
            "lon": centroide.x,
            "lat": centroide.y,
        })
    return regiones


def contar_peligros_cercanos(lat: float, lon: float) -> int:
    resp = httpx.get(
        _INGEMMET_PELIGROS,
        params={
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "distance": _RADIO_METROS,
            "units": "esriSRUnit_Meter",
            "returnCountOnly": "true",
            "f": "json",
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("count", 0)


def consultar_elevaciones_batch(puntos: list[tuple[float, float]]) -> list[float | None]:
    """Mismo patron de fase2_elevacion_continua.py -- respeta el limite
    real de 100 ubicaciones/llamada y 1 llamada/segundo de OpenTopoData."""
    elevaciones: list[float | None] = []
    for i in range(0, len(puntos), 100):
        lote = puntos[i:i + 100]
        locs = "|".join(f"{lat},{lon}" for lat, lon in lote)
        resp = httpx.get(_OPENTOPODATA, params={"locations": locs}, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for r in data.get("results", []):
            elevaciones.append(r.get("elevation"))
        if i + 100 < len(puntos):
            time.sleep(1.1)
    return elevaciones


def calcular_pendiente_pct(lat: float, lon: float, elevs: dict) -> float | None:
    """Gradiente por diferencias finitas, identico a Fase 2: centro + N/S/E/O
    a ~0.009 grados (~1km)."""
    centro = elevs.get((round(lat, 5), round(lon, 5)))
    norte = elevs.get((round(lat + 0.009, 5), round(lon, 5)))
    sur = elevs.get((round(lat - 0.009, 5), round(lon, 5)))
    este = elevs.get((round(lat, 5), round(lon + 0.009, 5)))
    oeste = elevs.get((round(lat, 5), round(lon - 0.009, 5)))
    if None in (centro, norte, sur, este, oeste):
        return None
    dist_m = 0.009 * 111320  # ~1km real a esta latitud aprox.
    dz_ns = (norte - sur) / 2
    dz_eo = (este - oeste) / 2
    return math.hypot(dz_ns, dz_eo) / dist_m * 100


def rank_biserial(x, y, alternative="two-sided"):
    u, p = mannwhitneyu(x, y, alternative=alternative)
    r = 1 - (2 * u) / (len(x) * len(y))
    return u, p, r


def main() -> None:
    print("=== Descargando los 25 departamentos reales de Peru (INGEMMET/INEI 2011) ===")
    regiones = obtener_regiones()
    print(f"Departamentos obtenidos: {len(regiones)}")
    for r in regiones:
        print(f"  {r['departamento']:20} centroide=({r['lat']:.3f},{r['lon']:.3f})")

    print(f"\n=== Contando eventos reales de 'Peligros Geologicos' (INGEMMET, radio {_RADIO_METROS/1000:.0f}km) por departamento ===")
    for r in regiones:
        r["n_peligros"] = contar_peligros_cercanos(r["lat"], r["lon"])
        print(f"  {r['departamento']:20} {r['n_peligros']} eventos")

    print("\n=== Consultando elevacion real (SRTM30m, OpenTopoData) -- 5 puntos x 25 departamentos ===")
    puntos = []
    for r in regiones:
        lat, lon = r["lat"], r["lon"]
        puntos.extend([
            (round(lat, 5), round(lon, 5)),
            (round(lat + 0.009, 5), round(lon, 5)),
            (round(lat - 0.009, 5), round(lon, 5)),
            (round(lat, 5), round(lon + 0.009, 5)),
            (round(lat, 5), round(lon - 0.009, 5)),
        ])
    elevaciones_lista = consultar_elevaciones_batch(puntos)
    elevs = {p: e for p, e in zip(puntos, elevaciones_lista)}

    for r in regiones:
        r["pendiente_pct"] = calcular_pendiente_pct(r["lat"], r["lon"], elevs)
        print(f"  {r['departamento']:20} pendiente={r['pendiente_pct']}")

    validos = [r for r in regiones if r["pendiente_pct"] is not None]
    print(f"\nDepartamentos con pendiente calculable: {len(validos)}/{len(regiones)}")

    conteos = sorted(v["n_peligros"] for v in validos)
    mediana_conteo = conteos[len(conteos) // 2]
    alto = [v for v in validos if v["n_peligros"] > mediana_conteo]
    bajo = [v for v in validos if v["n_peligros"] <= mediana_conteo]
    print(f"\nGrupo ALTO (> mediana de {mediana_conteo} eventos): {len(alto)} departamentos -> {[a['departamento'] for a in alto]}")
    print(f"Grupo BAJO (<= mediana): {len(bajo)} departamentos -> {[b['departamento'] for b in bajo]}")

    pend_alto = [a["pendiente_pct"] for a in alto]
    pend_bajo = [b["pendiente_pct"] for b in bajo]
    import statistics
    print(f"\nPendiente -- ALTO: mediana={statistics.median(pend_alto):.2f}%, media={statistics.mean(pend_alto):.2f}%")
    print(f"Pendiente -- BAJO: mediana={statistics.median(pend_bajo):.2f}%, media={statistics.mean(pend_bajo):.2f}%")

    if len(pend_alto) >= 2 and len(pend_bajo) >= 2:
        u, p, r = rank_biserial(pend_alto, pend_bajo, alternative="greater")
        print(f"\nMann-Whitney U (ALTO > BAJO) = {u:.1f}, p = {p:.4f}")
        print(f"r (rank-biserial) = {r:.4f}")
        if p < 0.05:
            print("RESULTADO: SI hay mas pendiente en los departamentos con mas eventos -- mismo patron que Colombia (#61).")
        else:
            print("RESULTADO: no hay evidencia estadistica suficiente a este nivel (n=25 departamentos, muestra chica).")
    else:
        print("\nMuestra insuficiente para prueba estadistica formal.")

    print("\n=== Nota honesta ===")
    print("n=25 (departamentos, no 1.121 municipios como en Colombia) -- cualquier resultado aqui es")
    print("una senal exploratoria de PRIMERA REPLICABILIDAD TECNICA, no una confirmacion al nivel de")
    print("rigor de #61. El centroide departamental es una aproximacion muy gruesa en departamentos")
    print("geograficamente heterogeneos (costa+sierra en el mismo departamento, ej. Ancash/Arequipa).")

    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase4b_peru_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(regiones, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
