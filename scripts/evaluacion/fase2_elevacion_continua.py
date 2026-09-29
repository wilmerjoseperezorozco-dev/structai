"""Fase 2 (issue #61), punto #3 del roadmap de mejora: pendiente CONTINUA
real (no las 7 categorías de letra de IGAC) via SRTM30m (OpenTopoData,
api.opentopodata.org, gratis, sin API key -- limite real documentado:
max 100 ubicaciones/llamada, max 1 llamada/segundo, max 1000 llamadas/dia).

Metodologia: para cada municipio del grupo ALTO (15, mas eventos de
movimiento en masa) y BAJO corregido (217, Fase 1c -- reportan a UNGRD
pero cero movimiento en masa), se obtiene el centroide real via
divipola.resolver_municipio() y se consulta elevacion en 5 puntos (centro
+ ~1km norte/sur/este/oeste) para estimar la magnitud del gradiente de
pendiente (metodo de diferencias finitas centradas, estandar en analisis
de terreno). Se compara con Mann-Whitney U (no chi-cuadrado -- estos son
datos continuos, no categoricos)."""
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
from scipy.stats import mannwhitneyu

TAM_PAGINA = 1000
OPENTOPODATA_URL = "https://api.opentopodata.org/v1/srtm30m"
MAX_LOCATIONS_POR_LLAMADA = 100
OFFSET_GRADOS = 0.009  # ~1km en el ecuador/latitudes bajas de Colombia


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
    """Mismo criterio ya usado y corregido en Fase 1c."""
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

    grupo_bajo_corregido_claves = (
        set(universo) - set(conteo_mm)
    ) & municipios_con_algun_evento
    grupo_bajo = [{"municipio": k, "departamento": universo[k]} for k in grupo_bajo_corregido_claves]

    return grupo_alto, grupo_bajo


def obtener_coordenadas(grupo: list[dict]) -> list[dict]:
    """Resuelve lat/lon real via divipola -- descarta silenciosamente los
    que no resuelven (mismo criterio de 'no inventar' ya usado en todo
    este proyecto), reportando cuántos se pierden."""
    con_coords = []
    sin_resolver = 0
    for m in grupo:
        r = divipola.resolver_municipio(m["municipio"], m["departamento"])
        if r and r.get("latitud") is not None and r.get("longitud") is not None:
            con_coords.append({**m, "lat": r["latitud"], "lon": r["longitud"]})
        else:
            sin_resolver += 1
    print(f"  Resueltos con coordenadas: {len(con_coords)}/{len(grupo)} (sin resolver: {sin_resolver})")
    return con_coords


def consultar_elevaciones_batch(puntos: list[tuple[float, float]]) -> list[float]:
    """Consulta OpenTopoData en lotes de <=100 ubicaciones, respetando
    max 1 llamada/segundo."""
    resultados = []
    for i in range(0, len(puntos), MAX_LOCATIONS_POR_LLAMADA):
        lote = puntos[i:i + MAX_LOCATIONS_POR_LLAMADA]
        locations = "|".join(f"{lat},{lon}" for lat, lon in lote)
        resp = httpx.get(OPENTOPODATA_URL, params={"locations": locations}, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        resultados.extend(r["elevation"] for r in data["results"])
        time.sleep(1.1)  # respeta max 1 llamada/segundo
    return resultados


def calcular_pendientes(grupo_con_coords: list[dict]) -> list[float]:
    """Para cada municipio, arma 5 puntos (centro+N+S+E+O), consulta
    elevacion real, y calcula la magnitud del gradiente de pendiente por
    diferencias finitas centradas: sqrt((dz/dy)^2 + (dz/dx)^2), expresado
    como porcentaje (mismo formato que la convencion IGAC 0-3%..>75%)."""
    puntos = []
    for m in grupo_con_coords:
        lat, lon = m["lat"], m["lon"]
        puntos.append((lat, lon))  # centro (no se usa en el gradiente, solo referencia)
        puntos.append((lat + OFFSET_GRADOS, lon))  # norte
        puntos.append((lat - OFFSET_GRADOS, lon))  # sur
        puntos.append((lat, lon + OFFSET_GRADOS))  # este
        puntos.append((lat, lon - OFFSET_GRADOS))  # oeste

    elevaciones = consultar_elevaciones_batch(puntos)

    distancia_metros = OFFSET_GRADOS * 111320 * 2  # ~1km*2 entre N-S o E-O, aprox en el ecuador
    pendientes = []
    for i in range(len(grupo_con_coords)):
        base = i * 5
        _centro, norte, sur, este, oeste = elevaciones[base:base + 5]
        dz_ns = norte - sur
        dz_eo = este - oeste
        gradiente = math.sqrt(dz_ns**2 + dz_eo**2) / distancia_metros
        pendientes.append(gradiente * 100)  # como porcentaje
    return pendientes


def main() -> None:
    print("=== Reconstruyendo grupos (mismo criterio de Fase 1c) ===")
    grupo_alto_raw, grupo_bajo_raw = reconstruir_grupos()
    print(f"Grupo ALTO: {len(grupo_alto_raw)} municipios")
    print(f"Grupo BAJO corregido: {len(grupo_bajo_raw)} municipios")

    print("\n=== Resolviendo coordenadas reales (divipola) ===")
    print("Grupo ALTO:")
    grupo_alto = obtener_coordenadas(grupo_alto_raw)
    print("Grupo BAJO:")
    grupo_bajo = obtener_coordenadas(grupo_bajo_raw)

    print(f"\n=== Consultando elevación real (SRTM30m, {(len(grupo_alto)+len(grupo_bajo))*5} puntos) ===")
    pendientes_alto = calcular_pendientes(grupo_alto)
    print(f"Grupo ALTO listo ({len(pendientes_alto)} municipios)")
    pendientes_bajo = calcular_pendientes(grupo_bajo)
    print(f"Grupo BAJO listo ({len(pendientes_bajo)} municipios)")

    import statistics
    print("\n=== Resultado: pendiente continua real (%) ===")
    print(f"Grupo ALTO -- media: {statistics.mean(pendientes_alto):.2f}%, mediana: {statistics.median(pendientes_alto):.2f}%")
    print(f"Grupo BAJO -- media: {statistics.mean(pendientes_bajo):.2f}%, mediana: {statistics.median(pendientes_bajo):.2f}%")

    u_stat, p_valor = mannwhitneyu(pendientes_alto, pendientes_bajo, alternative="greater")
    print(f"\nMann-Whitney U = {u_stat:.1f}, p-valor (ALTO > BAJO) = {p_valor:.2e}")
    if p_valor < 0.001:
        print("RESULTADO: el grupo ALTO tiene pendiente real significativamente MAYOR que el grupo BAJO.")
    else:
        print(f"RESULTADO: no hay evidencia suficiente (p={p_valor:.4f}).")

    # Guardar los datos crudos para trazabilidad
    import json
    out = {
        "grupo_alto": [{"municipio": m["municipio"], "pendiente_pct": p} for m, p in zip(grupo_alto, pendientes_alto)],
        "grupo_bajo": [{"municipio": m["municipio"], "pendiente_pct": p} for m, p in zip(grupo_bajo, pendientes_bajo)],
    }
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase2_elevacion_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
