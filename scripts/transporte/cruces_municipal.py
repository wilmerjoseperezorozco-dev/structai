"""Réplica a escala municipal: ¿las obras cerca de corredores con más tráfico pesado tienen más prórrogas?

HIPÓTESIS PRIMARIA, fijada ANTES de ver resultados (las líneas 5h-5l exploraron muchas especificaciones sin una corrección global):
  H1. Entre contratos de obra ejecutados dentro de los 50 km de al menos un peaje ANI de esquema de siete categorías, un mayor porcentaje de camiones pesados
      (VI + VII sobre III..VII, ponderado por el tráfico de camiones de los peajes a <= 50 km, ANI 2024) se asocia con mayor odds de prórroga
      (dias_adicionados > 0), CON efectos fijos de departamento de ejecución y de año de firma, y errores agrupados por municipio. Una sola prueba, dos colas.
  Secundarias (familia con Holm): volumen de pesados a <= 50 km (log10), distancia al peaje más cercano (cada +50 km), y los resultados suspensión y adición de valor.
  Sensibilidad (no se contrastan): radios de 30 y 100 km; sin efectos fijos de departamento.
Diseño: la unidad de análisis es el contrato; la ubicación es el MUNICIPIO DE EJECUCIÓN (SECOP II `gra4-pcp2`, campo localizaci_n), no el de la entidad. Con efectos fijos de
departamento el contraste usa solo la variación dentro del departamento, que elimina los confusores departamentales de 5i a 5k.
Datos: contratos de obra y ubicaciones (caché SECOP), coordenadas de municipios (DIVIPOLA, `gdxc-w37w`), tráfico ANI por categoría 2024 y coordenadas de peajes
(`8yi9-t44c`, `68qj-5xux`). Solo concesiones ANI con esquema de siete categorías (ver 5l). Contratos con más de una ubicación distinta se excluyen (ambiguos).
Salida: data/transporte/cruces_municipal.json.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402
import cruces_secop_logistica as logi  # noqa: E402
import cruces_seguridad_institucional as seg  # noqa: E402
import cruces_trafico_ani as ani  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = base.RAIZ / "data" / "transporte" / "cruces_municipal.json"
UBICACIONES = base.RAIZ / "scripts" / "secop" / "_cache" / "ubicaciones.jsonl"
RADIO_PRIMARIO_KM, RADIOS_SENSIBILIDAD = 50.0, (30.0, 100.0)
R_TIERRA_KM = 6371.0
# Diferencias de nombre entre SECOP (localizaci_n) y DIVIPOLA, detectadas por el reporte de filas sin coincidencia (independiente de los resultados).
ALIAS_MUNICIPIO = {("VALLE", "CALI"): ("VALLE", "SANTIAGO DE CALI"), ("NORTE DE SANTANDER", "CUCUTA"): ("NORTE DE SANTANDER", "SAN JOSE DE CUCUTA"),
                   ("BOLIVAR", "CARTAGENA"): ("BOLIVAR", "CARTAGENA DE INDIAS"), ("TOLIMA", "MARIQUITA"): ("TOLIMA", "SAN SEBASTIAN DE MARIQUITA"),
                   ("PUTUMAYO", "LEGUIZAMO"): ("PUTUMAYO", "PUERTO LEGUIZAMO"), ("NARINO", "TUMACO"): ("NARINO", "SAN ANDRES DE TUMACO"),
                   ("ANTIOQUIA", "SANTAFE DE ANTIOQUIA"): ("ANTIOQUIA", "SANTA FE DE ANTIOQUIA"), ("ANTIOQUIA", "DON MATIAS"): ("ANTIOQUIA", "DONMATIAS"),
                   ("BOLIVAR", "MOMPOS"): ("BOLIVAR", "SANTA CRUZ DE MOMPOX"), ("CAUCA", "PIENDAMO"): ("CAUCA", "PIENDAMO TUNIA"),
                   ("CUNDINAMARCA", "DISTRITO CAPITAL"): ("CUNDINAMARCA", "BOGOTA")}
BOGOTA = ("CUNDINAMARCA", "BOGOTA")


def clave(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    s = " ".join(re.sub(r"[^A-Z0-9 ]", " ", s).split())
    return re.sub(r" D C$", "", s)


def haversine(lat, lon, lats, lons) -> np.ndarray:
    p1, p2 = np.radians(lat), np.radians(lats)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lons - lon) / 2) ** 2
    return 2 * R_TIERRA_KM * np.arcsin(np.sqrt(a))


def dpto(s: str) -> str:
    d = base.norm(s.replace("DEPARTAMENTO DEL ", "").replace("DEPARTAMENTO DE ", ""))
    return "CUNDINAMARCA" if d.startswith("BOGOTA") else d


def municipios() -> dict[tuple[str, str], tuple[float, float]]:
    out: dict[tuple[str, str], tuple[float, float]] = {}
    for r in seg.soql("gdxc-w37w", **{"$limit": 3000}):
        try:
            out[(dpto(r["dpto"]), clave(r["nom_mpio"]))] = (float(r["latitud"].replace(",", ".")), float(r["longitud"].replace(",", ".")))
        except (KeyError, ValueError):
            continue
    return out


def ubicacion_obras(muni: dict) -> tuple[dict[str, tuple[str, str]], dict[str, int]]:
    por: dict[str, set[tuple[str, str]]] = defaultdict(set)
    cnt = defaultdict(int)
    for linea in UBICACIONES.open(encoding="utf-8"):
        r = json.loads(linea)
        partes = [p.strip() for p in r["localizaci_n"].split(";")]
        if len(partes) < 3:
            cnt["sin_municipio"] += 1
            continue
        k = (dpto(partes[1].upper()), clave(partes[2]))
        k = ALIAS_MUNICIPIO.get(k, k)
        if k in muni:
            por[r["id_contrato"]].add(k)
        else:
            cnt["sin_coincidencia"] += 1
    unicos = {i: next(iter(v)) for i, v in por.items() if len(v) == 1}
    cnt["contratos_ubicados"], cnt["contratos_ambiguos"] = len(unicos), len(por) - len(unicos)
    return unicos, dict(cnt)


def peajes_siete_categorias() -> list[dict]:
    """Peajes ANI 2024 con esquema de siete categorías: coordenadas, camiones y pesados."""
    import json as _j
    ub = ani.ubicacion_peajes()
    coords = {}
    for p in _j.loads((base.CACHE / "peajes_68qj-5xux.json").read_text(encoding="utf-8")):
        c = (p.get("point") or {}).get("coordinates")
        if c:
            coords[ani.nombre(p["nombre_peaje"])] = (c[1], c[0])
    out = []
    for (_, nom), cats in ani.trafico_ani(2024).items():
        k = ani.nombre(nom)
        cam = sum(cats.get(c, (0.0, 0.0))[0] for c in ani.CAMIONES)
        if k in coords and k in ub and ani.esquema_siete(cats) and cam > 0:
            pes = cats["VI"][0] + cats["VII"][0]
            out.append({"peaje": nom, "lat": coords[k][0], "lon": coords[k][1], "camiones": cam, "pesados": pes})
    return out


def exposicion(lat: float, lon: float, p: dict[str, np.ndarray]) -> dict:
    d = haversine(lat, lon, p["lat"], p["lon"])
    e = {"dist_min_km": float(d.min()), "share_cercano": float(p["pes"][d.argmin()] / p["cam"][d.argmin()])}
    for r in (RADIO_PRIMARIO_KM, *RADIOS_SENSIBILIDAD):
        m = d <= r
        cam, pes = p["cam"][m].sum(), p["pes"][m].sum()
        e[f"share_{int(r)}"] = float(pes / cam) if m.any() else float("nan")
        e[f"logvol_{int(r)}"] = float(np.log10(pes + 1.0)) if m.any() else float("nan")
        e[f"n_{int(r)}"] = int(m.sum())
    return e


def cargar(muni, loc) -> tuple[list[dict], list[dict]]:
    pj = peajes_siete_categorias()
    p = {k: np.array([x[k2] for x in pj], float) for k, k2 in (("lat", "lat"), ("lon", "lon"), ("cam", "camiones"), ("pes", "pesados"))}
    print(f"peajes ANI de siete categorías con coordenadas: {len(pj)}")
    deptos = {d for d, _ in muni}
    contratos = logi.cargar_contratos({d: 0.0 for d in deptos})
    cache: dict[tuple[str, str], dict] = {}
    filas = []
    for c in contratos:
        k = loc.get(c["id"])
        if k is None:
            continue
        if k not in cache:
            cache[k] = exposicion(*muni[k], p)
        filas.append({**c, "dep_ejec": k[0], "muni": f"{k[0]}|{k[1]}", **cache[k]})
    return filas, pj


def ajustar(filas: list[dict], resultado: str, variable: str, escala: float = 1.0, efectos_depto: bool = True, extras: tuple[str, ...] = ()) -> dict:
    """`extras`: nombres de campos numéricos de cada fila que se añaden como covariables municipales (por defecto ninguna: el modelo no cambia)."""
    sub = [f for f in filas if not np.isnan(f[variable]) and not any(np.isnan(f[e]) for e in extras)]
    X0, nombres = logi.matriz(sub)
    cuerpo = X0[:, 2:]
    deps = sorted({f["dep_ejec"] for f in sub})
    dum = np.array([[float(f["dep_ejec"] == d) for d in deps] for f in sub])
    extra_m = np.array([[f[e] for e in extras] for f in sub], float).reshape(len(sub), len(extras))
    M = np.hstack([np.column_stack([np.ones(len(sub)), np.array([f[variable] * escala for f in sub])]), cuerpo, extra_m, dum[:, 1:] if efectos_depto else np.zeros((len(sub), 0))])
    ok = M.std(0) > 0
    ok[0] = True
    y = np.array([f[resultado] for f in sub])
    g = np.unique([f["muni"] for f in sub], return_inverse=True)[1]
    m = sm.GLM(y, M[:, ok], family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": g, "use_correction": True, "df_correction": True})
    b, se = float(m.params[1]), float(m.bse[1])
    G = len(set(g))
    t = stats.t.ppf(0.975, G - 1)
    return {"n": len(sub), "municipios": G, "departamentos": len(deps), "tasa": float(y.mean()), "OR": float(np.exp(b)), "ic95": (float(np.exp(b - t * se)), float(np.exp(b + t * se))),
            "p": float(2 * stats.t.sf(abs(b / se), G - 1))}


if __name__ == "__main__":
    muni = municipios()
    loc, cnt = ubicacion_obras(muni)
    print(f"municipios DIVIPOLA con coordenadas: {len(muni)}; ubicaciones: {cnt}")
    filas, pj = cargar(muni, loc)
    print(f"contratos con ubicación de ejecución y controles completos: {len(filas)}; municipios: {len({f['muni'] for f in filas})}")
    cerca = [f for f in filas if f["n_50"] > 0]
    print(f"contratos a <= 50 km de algún peaje de siete categorías: {len(cerca)} en {len({f['muni'] for f in cerca})} municipios, {len({f['dep_ejec'] for f in cerca})} departamentos")
    res: dict = {"conteos": cnt, "n_peajes": len(pj), "n_contratos": len(filas), "n_cerca_50": len(cerca)}
    h1 = ajustar(cerca, "prorroga", "share_50", 10.0)
    res["H1_primaria_prorroga_share_50_por_10pp"] = h1
    print(f"\nH1 (primaria) prórroga ~ pesados a <=50 km, OR por +10 pp = {h1['OR']:.3f} IC95 ({h1['ic95'][0]:.3f}-{h1['ic95'][1]:.3f}) p={h1['p']:.4f} "
          f"n={h1['n']} municipios={h1['municipios']} deptos={h1['departamentos']} tasa={100 * h1['tasa']:.1f}%")
    sec = {"logvolumen_50_por_1": ajustar(cerca, "prorroga", "logvol_50", 1.0), "distancia_por_50km_todos": ajustar(filas, "prorroga", "dist_min_km", 1 / 50),
           "suspension_share_50": ajustar(cerca, "suspension", "share_50", 10.0), "adicion_valor_share_50": ajustar(cerca, "adicion_valor", "share_50", 10.0)}
    ph = base.holm({k: v["p"] for k, v in sec.items()})
    for k, v in sec.items():
        v["p_holm"] = ph[k]
        print(f"secundaria {k:28s} OR={v['OR']:.3f} IC95 ({v['ic95'][0]:.3f}-{v['ic95'][1]:.3f}) p={v['p']:.4f} Holm={ph[k]:.4f} n={v['n']}")
    res["secundarias"] = sec
    sens = {}
    for r in RADIOS_SENSIBILIDAD:
        sub = [f for f in filas if f[f"n_{int(r)}"] > 0]
        sens[f"radio_{int(r)}km"] = ajustar(sub, "prorroga", f"share_{int(r)}", 10.0)
    sens["sin_Bogota_50km"] = ajustar([f for f in cerca if f["muni"] != "|".join(BOGOTA)], "prorroga", "share_50", 10.0)
    sens["sin_ciudades_sin_alias_(primera_corrida)"] = ajustar([f for f in cerca if f["muni"].split("|")[1] not in {k[1] for k in ALIAS_MUNICIPIO.values()} | {"BOGOTA"}],
                                                              "prorroga", "share_50", 10.0)
    sens["sin_efectos_depto_50km"] = ajustar(cerca, "prorroga", "share_50", 10.0, efectos_depto=False)
    for k, v in sens.items():
        print(f"sensibilidad {k:26s} OR={v['OR']:.3f} IC95 ({v['ic95'][0]:.3f}-{v['ic95'][1]:.3f}) p={v['p']:.4f} n={v['n']}")
    res["sensibilidad"] = sens
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
