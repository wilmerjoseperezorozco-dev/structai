"""Cargador compartido de los datos del Caribe (issue #95, Frente C).

Reune, por municipio: relieve (DEM, poligonos), reportes UNGRD, clasificacion de
suelos IGAC y tamano de la muestra Sisben (proxy de poblacion registrada).
No calcula estadistica: solo ensambla y conserva la procedencia.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from dotenv import dotenv_values
from shapely.geometry import shape
from supabase import create_client

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CACHE = AQUI / "_cache"
DEPTOS = {"08": "Atlántico", "47": "Magdalena", "13": "Bolívar", "23": "Córdoba",
          "70": "Sucre", "20": "Cesar", "44": "La Guajira"}
EVENTOS_INUNDACION = ["INUNDACION", "INUNDACIÓN", "INUNDACIoN", "CRECIENTE SUBITA", "Creciente Subita", "AVENIDA TORRENCIAL"]
M_POR_GRADO = 111_320.0


def _sb():
    env = dotenv_values(RAIZ / "apps/api/.env")
    return create_client(env["SUPABASE_URL"], env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_KEY"])


def _paginar(tabla: str, cols: str, codigos: list[str], col_codigo: str) -> list[dict]:
    sb, filas, ini = _sb(), [], 0
    while True:
        pag = sb.table(tabla).select(cols).in_(col_codigo, codigos).range(ini, ini + 999).execute().data or []
        filas.extend(pag)
        if len(pag) < 1000:
            return filas
        ini += 1000


def dem() -> list[dict]:
    return json.loads((AQUI / "dem_poligonos_caribe.json").read_text(encoding="utf-8"))["municipios"]


def poligonos() -> dict[str, dict]:
    """codigo -> {geom (shapely), centroide (lon, lat), area_km2 aprox}. El area usa
    una correccion por latitud, suficiente para densidades (no es area geodesica)."""
    out = {}
    for d in DEPTOS:
        f = CACHE / f"poligonos_{d}.geojson"
        for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
            g = shape(ft["geometry"])
            c = g.centroid
            km2 = g.area * (M_POR_GRADO / 1000) ** 2 * math.cos(math.radians(c.y))
            out[ft["properties"]["CODIGO"]] = {"geom": g, "centroide": (c.x, c.y), "area_km2": km2,
                                               "nombre": ft["properties"]["NOMBRE_ENT"]}
    return out


def ungrd(codigos: list[str]) -> list[dict]:
    return _paginar("ungrd_emergencias",
                    "id,fecha,evento,codigo_municipio,personas,familias,viviendas_destruidas,viviendas_averiadas,hectareas,fuente,creado_en",
                    codigos, "codigo_municipio")


def igac(codigos: list[str]) -> dict[str, dict]:
    """Por municipio: fraccion de area con inundacion (Cortas/Largas/Muy largas sobre el
    area clasificada, sin 'No aplica') y clase dominante (por area) de textura y drenaje."""
    filas = _paginar("igac_suelos_ufh", "cod_dane_municipio,inund,textura,drenaje,area_ha", codigos, "cod_dane_municipio")
    inund, tot = defaultdict(float), defaultdict(float)
    tex, dre = defaultdict(Counter), defaultdict(Counter)
    for r in filas:
        a = float(r["area_ha"] or 0)
        c = r["cod_dane_municipio"]
        if a <= 0:
            continue
        if r["inund"] not in (None, "No aplica"):
            tot[c] += a
            if r["inund"] in ("Cortas", "Largas", "Muy largas"):
                inund[c] += a
        if r["textura"] not in (None, "No aplica"):
            tex[c][r["textura"]] += a
        if r["drenaje"] not in (None, "No aplica"):
            dre[c][r["drenaje"]] += a
    return {c: {"frac_inundable": inund[c] / tot[c],
                "textura_dom": tex[c].most_common(1)[0][0] if tex[c] else None,
                "drenaje_dom": dre[c].most_common(1)[0][0] if dre[c] else None}
            for c in tot if tot[c] > 0}


def poblacion_dane(codigos: list[str], anio: int = 2020) -> dict[str, dict]:
    """Poblacion municipal proyectada por el DANE (CNPV 2018, serie 2018-2042, actualizada
    2025-08-08), total y % en cabecera. Archivo local descargado de dane.gov.co
    (PPED-AreaMun-2018-2042_VP.xlsx). En ese archivo las columnas MPIO y DPMP vienen con las
    etiquetas cruzadas: MPIO trae el codigo y DPMP el nombre."""
    import pandas as pd
    f = CACHE / "dane_poblacion" / "PPED-AreaMun-2018-2042_VP.xlsx"
    df = pd.read_excel(f, sheet_name=2, header=7).dropna(subset=["MPIO"])
    df["codigo"] = df["MPIO"].astype(int).astype(str).str.zfill(5)
    df = df[(df["AÑO"] == anio) & df["codigo"].isin(codigos)]
    p = df.pivot_table(index="codigo", columns="ÁREA GEOGRÁFICA", values="TOTAL")
    return {c: {"poblacion": float(r["Total"]), "pct_cabecera": float(r["Cabecera Municipal"] / r["Total"])}
            for c, r in p.iterrows()}


def sisben(codigos: list[str]) -> dict[str, dict]:
    filas = _paginar("sisben_vulnerabilidad_vivienda_municipio",
                     "codigo_municipio,n_viviendas_muestra,pct_material_vulnerable", codigos, "codigo_municipio")
    return {r["codigo_municipio"]: r for r in filas}
