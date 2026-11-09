"""Siniestralidad en sectores críticos (ANSV, `rs3u-8r4q`) normalizada por red vial (INVIAS, `ie7y-asdn`) y población, e integrada a la tabla municipal de 5m.

Lo que SÍ es el conjunto (verificado): 316 sectores críticos de la red nacional (máx. 10 km), con `fallecidos` (3.580 en total) y calificación espacial (gizscore, gipvalue), 133 municipios,
22 departamentos, entidades ANI 141, INVIAS-OTROS 126, DEPTO 48, CIUDAD 1. Actualización de la fuente: abril de 2021. NO trae lesionados ni daños materiales, así que no es posible un índice de
severidad ponderado: lo único medido es mortalidad. Además son los sectores seleccionados como críticos, no todos los siniestros: «0 fallecidos» no significa «seguro».
Red vial `ie7y-asdn`: 715 tramos con geometría pero SIN municipio; los kilómetros por municipio se calculan cortando las líneas con los polígonos DANE MGN 2018 (se omiten vías en desuso).
Población: no hay población total municipal en datos.gov.co; se usa la de 5 a 16 años del MEN (`nudc-7mev`, proyecciones DANE) como PROXY de escala, igual que en 5k.

Variables municipales: tiene_red (km de red nacional > 0), log_km_red = log10(1 + km), fall_x100km = fallecidos de sectores / km de red x 100 (solo con red), fall_log = log10(1 + fall_x100km),
log_pop = log10 de la población de 5-16.

PRUEBA FIJADA ANTES DE CALCULAR. (P) Robustez: al añadir tiene_red, log_km_red, log_pop y fall_log al modelo primario de 5m (prórroga ~ % pesados a <= 50 km, efectos de departamento,
errores agrupados por municipio), el OR de pesados por +10 pp no cambia más de 0,05 en logaritmo respecto de 1,038. (E) Exploratoria: entre los contratos de municipios con red nacional,
mayor fall_log (+1) se asocia con la prórroga; una sola prueba, sin ajuste múltiple, se interpreta solo con el IC.
Salida: data/transporte/siniestralidad_municipal.json.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from shapely.geometry import shape
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_municipal as cm  # noqa: E402
import cruces_peajes_secop as base  # noqa: E402
import cruces_seguridad_institucional as seg  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = base.RAIZ / "data" / "transporte" / "siniestralidad_municipal.json"
URL_MPIO = "https://raw.githubusercontent.com/caticoa3/colombia_mapa/master/co_2018_MGN_MPIO_POLITICO.geojson"
ADMIN_DESUSO = "5"
TOLERANCIA_GRADOS = 5e-5          # ~5 m al simplificar líneas de ~1 m de espaciado
OR_PRIMARIO_5M = 1.038


def km_linea(geom) -> float:
    total = 0.0
    partes = getattr(geom, "geoms", [geom])
    for g in partes:
        if g.geom_type == "LineString" and len(g.coords) > 1:
            c = np.asarray(g.coords)
            total += float(cm.haversine(c[:-1, 1], c[:-1, 0], c[1:, 1], c[1:, 0]).sum())
        elif g.geom_type in ("MultiLineString", "GeometryCollection"):
            total += km_linea(g)
    return total


def red_por_municipio() -> tuple[dict[str, float], float, float]:
    cache = base.CACHE / "km_red_municipio.json"
    if cache.exists():
        c = json.loads(cache.read_text(encoding="utf-8"))
        return c["km"], c["total_geom"], c["total_fuente"]
    km, total_geom, total_fuente = _calcular_red()
    cache.write_text(json.dumps({"km": km, "total_geom": total_geom, "total_fuente": total_fuente}), encoding="utf-8")
    return km, total_geom, total_fuente


def _calcular_red() -> tuple[dict[str, float], float, float]:
    mp = json.loads(base.descargar(URL_MPIO, base.CACHE / "mpio_mgn2018.geojson").read_text(encoding="utf-8"))["features"]
    polis = [shape(f["geometry"]) for f in mp]
    codigos = [f["properties"]["MPIO_CCNCT"] for f in mp]
    arbol = STRtree(polis)
    km: dict[str, float] = defaultdict(float)
    total_geom = total_fuente = 0.0
    for r in seg.soql("ie7y-asdn", **{"$limit": 5000}):
        if r.get("administrador") == ADMIN_DESUSO or not r.get("multiline"):
            continue
        linea = shape(r["multiline"]).simplify(TOLERANCIA_GRADOS)
        total_geom += km_linea(linea)
        total_fuente += float(r.get("shape__length") or 0) / 1000.0
        for i in arbol.query(linea, predicate="intersects"):
            km[codigos[i]] += km_linea(linea.intersection(polis[i]))
    return dict(km), total_geom, total_fuente


def sectores() -> dict[str, dict]:
    out: dict[str, dict] = defaultdict(lambda: {"fallecidos": 0.0, "sectores": 0, "gi_max": float("-inf")})
    for r in seg.soql("rs3u-8r4q", **{"$limit": 2000}):
        d = out[r["divipola"].zfill(5)]
        d["fallecidos"] += float(r["fallecidos"])
        d["sectores"] += 1
        d["gi_max"] = max(d["gi_max"], float(r["gizscore"]))
    return dict(out)


def poblacion_5_16() -> dict[str, float]:
    filas = seg.soql("nudc-7mev", **{"$select": "c_digo_municipio,poblaci_n_5_16", "$where": "a_o='2024'", "$limit": 3000})
    return {r["c_digo_municipio"].zfill(5): float(r["poblaci_n_5_16"]) for r in filas if r.get("poblaci_n_5_16")}


def variables(cod: str, km: dict, sec: dict, pop: dict) -> dict:
    k = km.get(cod, 0.0)
    f = sec.get(cod, {}).get("fallecidos", 0.0)
    x100 = 100 * f / k if k > 0 else 0.0
    return {"tiene_red": float(k > 0), "log_km_red": float(np.log10(1 + k)), "fall_x100km": x100, "fall_log": float(np.log10(1 + x100)),
            "tiene_sec": float(f > 0), "fall_abs_log": float(np.log10(1 + f)),
            "log_pop": float(np.log10(pop[cod])) if cod in pop and pop[cod] > 0 else float("nan")}


if __name__ == "__main__":
    km, tot_geom, tot_fuente = red_por_municipio()
    sec, pop = sectores(), poblacion_5_16()
    print(f"red nacional recortada: {tot_geom:,.0f} km (suma de la fuente shape__length/1000: {tot_fuente:,.0f} km, diferencia {100 * (tot_geom / tot_fuente - 1):+.1f} %); "
          f"municipios con red: {sum(v > 0.05 for v in km.values())} de 1122")
    con_red, con_sec = {c for c, v in km.items() if v > 0.05}, set(sec)
    fall_total = sum(v["fallecidos"] for v in sec.values())
    print(f"municipios con sectores críticos: {len(con_sec)}; con sectores y sin red inventariada: {len(con_sec - con_red)} "
          f"({sum(sec[c]['fallecidos'] for c in con_sec - con_red):.0f} de {fall_total:.0f} fallecidos)")
    top = sorted(sec.items(), key=lambda kv: -kv[1]["fallecidos"])[:10]
    print(f"los 10 municipios con más fallecidos concentran {100 * sum(v['fallecidos'] for _, v in top) / fall_total:.0f} % del total")
    res: dict = {"km_total_recortado": tot_geom, "km_total_fuente": tot_fuente, "municipios_con_red": len(con_red), "municipios_con_sectores": len(con_sec),
                 "sectores_sin_red": len(con_sec - con_red), "fallecidos_total": fall_total}
    comunes = sorted(con_red & con_sec)
    rho = stats.spearmanr([km[c] for c in comunes], [sec[c]["fallecidos"] for c in comunes])
    rho_tasa = stats.spearmanr([km[c] for c in comunes], [100 * sec[c]["fallecidos"] / km[c] for c in comunes])
    print(f"entre los {len(comunes)} municipios con red y sectores: Spearman fallecidos vs km de red = {rho[0]:.2f}; tasa por 100 km vs km de red = {rho_tasa[0]:.2f}")
    res["spearman_fallecidos_km"], res["spearman_tasa_km"] = float(rho[0]), float(rho_tasa[0])

    # Integración con 5m
    muni = cm.municipios()
    codigo = {(cm.dpto(r["dpto"]), cm.clave(r["nom_mpio"])): r["cod_mpio"] for r in seg.soql("gdxc-w37w", **{"$limit": 3000})}
    loc, _ = cm.ubicacion_obras(muni)
    filas, _ = cm.cargar(muni, loc)
    cache: dict[str, dict] = {}
    for f in filas:
        k = tuple(f["muni"].split("|"))
        cod = codigo.get(k) or codigo.get(cm.ALIAS_MUNICIPIO.get(k, k))
        f["cod"] = cod
        if cod not in cache:
            cache[cod] = variables(cod, km, sec, pop) if cod else {}
        f.update(cache[cod] or {x: float("nan") for x in ("tiene_red", "log_km_red", "fall_x100km", "fall_log", "log_pop", "tiene_sec", "fall_abs_log")})
    sin_cod = sum(1 for f in filas if not f["cod"])
    print(f"\ncontratos: {len(filas)} (sin código DANE: {sin_cod}); con red nacional en su municipio: {sum(f['tiene_red'] == 1 for f in filas)}")
    cerca = [f for f in filas if f["n_50"] > 0]
    base_m = cm.ajustar(cerca, "prorroga", "share_50", 10.0)
    cov = ("tiene_red", "log_km_red", "log_pop", "fall_log")
    ext_m = cm.ajustar(cerca, "prorroga", "share_50", 10.0, extras=cov)
    d = float(np.log(ext_m["OR"]) - np.log(base_m["OR"]))
    print(f"(P) OR pesados +10 pp: base {base_m['OR']:.3f} ({base_m['ic95'][0]:.3f}-{base_m['ic95'][1]:.3f}, n={base_m['n']})  |  con covariables {ext_m['OR']:.3f} "
          f"({ext_m['ic95'][0]:.3f}-{ext_m['ic95'][1]:.3f}, n={ext_m['n']})  |  cambio en log OR = {d:+.3f}  -> {'se cumple' if abs(d) <= 0.05 else 'NO se cumple'} (< 0,05)")
    # (E)
    cr = [f for f in filas if f["tiene_red"] == 1]
    exp = cm.ajustar(cr, "prorroga", "fall_log", 1.0, extras=("log_km_red", "log_pop"))
    print(f"(E) prórroga ~ fall_log (+1), municipios con red: OR {exp['OR']:.3f} IC95 ({exp['ic95'][0]:.3f}-{exp['ic95'][1]:.3f}) p={exp['p']:.3f} n={exp['n']} municipios={exp['municipios']}")
    # Sensibilidades de (E), añadidas DESPUÉS de ver el resultado de (E): descriptivas, no confirmatorias
    sens = {"solo fall_log, sin covariables": cm.ajustar(cr, "prorroga", "fall_log", 1.0),
            "tiene sectores críticos (0/1)": cm.ajustar(cr, "prorroga", "tiene_sec", 1.0, extras=("log_km_red", "log_pop")),
            "fallecidos absolutos (log10(1+f))": cm.ajustar(cr, "prorroga", "fall_abs_log", 1.0, extras=("log_km_red", "log_pop")),
            "tasa, sin Bogotá": cm.ajustar([f for f in cr if f["muni"] != "|".join(cm.BOGOTA)], "prorroga", "fall_log", 1.0, extras=("log_km_red", "log_pop")),
            "tasa, sin efectos de departamento": cm.ajustar(cr, "prorroga", "fall_log", 1.0, efectos_depto=False, extras=("log_km_red", "log_pop")),
            "tasa, solo municipios con sectores": cm.ajustar([f for f in cr if f["tiene_sec"] == 1], "prorroga", "fall_log", 1.0, extras=("log_km_red", "log_pop"))}
    for k, v in sens.items():
        print(f"  sensibilidad {k:38s} OR {v['OR']:.3f} IC95 ({v['ic95'][0]:.3f}-{v['ic95'][1]:.3f}) p={v['p']:.3f} n={v['n']} municipios={v['municipios']}")
    res["E_sensibilidades"] = sens
    res["P_base"], res["P_con_covariables"], res["P_delta_log_or"], res["E_exploratoria"] = base_m, ext_m, d, exp
    res["distribucion"] = {"tasa_x100km_p50": float(np.median([100 * sec[c]["fallecidos"] / km[c] for c in comunes])),
                           "tasa_x100km_p90": float(np.percentile([100 * sec[c]["fallecidos"] / km[c] for c in comunes], 90))}
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
