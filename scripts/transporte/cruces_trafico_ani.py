"""Cruce 1 corregido con tráfico ANI por categoría (2016 y 2024) y réplica del hallazgo de prórrogas con una mezcla reciente.

Fuente: datos.gov.co `8yi9-t44c` (tráfico vehicular ANI, mensual por peaje y categoría, con la tarifa aplicada) y `68qj-5xux` (coordenadas, para ubicar
el peaje en un departamento por punto en polígono; la unión es por nombre normalizado, sin ambigüedades; los peajes sin coincidencia se excluyen y se informan).
Tráfico y tarifa tienen la MISMA categoría, por lo que no hace falta el mapeo clase INVIAS -> categoría. Correspondencia con INVIAS 2011 (hipótesis H0, ahora
justificada por el esquema de siete categorías): III y IV = camiones de 2 ejes (C-2P, C-2G), V = 3-4 ejes (C-3-4), VI = 5 ejes (C-5), VII = 6+ ejes (>C-5).
Pesados = (VI + VII) / (III..VII), igual que (C-5 + >C-5) / (todas las clases) en la mezcla INVIAS.
ESQUEMA DE CATEGORÍAS: las concesiones no usan el mismo. 53 de 131 peajes (40 % en 2024) no registran tráfico en VI ni VII y su categoría V concentra 43-53 % de los camiones:
ahí V significa "3 o más ejes" (esquema de cinco categorías) y la proporción de pesados no es comparable. Solo se usan los peajes con tráfico en VI y VII (esquema de siete
categorías), 78 en 2024. Los peajes de otros esquemas se excluyen y se informan.
Pruebas: (P) persistencia 2011 -> 2024 por departamento; (T2') proporción de pesados 2024 frente a forma de tarifa R = V/III; (R) réplica de la prórroga (etapas 1-2 de
cruces_covariables.py) con el predictor ANI 2024, solo en los departamentos con ambos datos. Solo concesiones ANI: no representa los peajes INVIAS.
Salida: data/transporte/cruces_trafico_ani.json.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from shapely.geometry import Point, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_covariables as cov  # noqa: E402
import cruces_peajes_secop as base  # noqa: E402
import cruces_seguridad_institucional as seg  # noqa: E402
import cruces_secop_logistica as logi  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = base.RAIZ / "data" / "transporte" / "cruces_trafico_ani.json"
CAMIONES = ("III", "IV", "V", "VI", "VII")


def nombre(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper().replace("-", " ").split())


def trafico_ani(anio: int) -> dict[tuple[str, str], dict[str, tuple[float, float]]]:
    """(idpeaje, peaje) -> categoría -> (vehículos, ingreso nominal = vehículos x tarifa)."""
    filas = seg.soql("8yi9-t44c", **{"$select": "idpeaje,peaje,categoriatarifa,sum(cantidadtrafico) as t,sum(cantidadtrafico*valortarifa) as ing",
                                    "$where": f"desde>='{anio}-01-01' AND desde<'{anio + 1}-01-01'", "$group": "idpeaje,peaje,categoriatarifa", "$limit": 10000})
    out: dict[tuple[str, str], dict[str, tuple[float, float]]] = defaultdict(dict)
    for r in filas:
        out[(r["idpeaje"], r["peaje"])][r["categoriatarifa"]] = (float(r["t"]), float(r["ing"]))
    return out


def ubicacion_peajes() -> dict[str, str]:
    """nombre normalizado -> departamento (punto en polígono; fuera de polígono, el más cercano). Se descartan nombres repetidos."""
    base.cargar_peajes()  # asegura las descargas en caché
    pol = [(base.norm(f["properties"].get("NOMBRE_DPT") or f["properties"]["DPTO_CNMBR"]), shape(f["geometry"]))
           for f in json.loads((base.CACHE / "dpto_mgn2018.geojson").read_text(encoding="utf-8"))["features"]]
    cuenta: dict[str, int] = defaultdict(int)
    ub: dict[str, str] = {}
    for p in json.loads((base.CACHE / "peajes_68qj-5xux.json").read_text(encoding="utf-8")):
        c = (p.get("point") or {}).get("coordinates")
        if not c:
            continue
        pt = Point(*c)
        dep = next((n for n, g in pol if g.contains(pt)), None) or min(pol, key=lambda t: t[1].distance(pt))[0]
        k = nombre(p["nombre_peaje"])
        cuenta[k] += 1
        ub[k] = dep
    return {k: v for k, v in ub.items() if cuenta[k] == 1}


def esquema_siete(cats: dict[str, tuple[float, float]]) -> bool:
    return cats.get("VI", (0.0, 0.0))[0] > 0 and cats.get("VII", (0.0, 0.0))[0] > 0


def por_departamento(trafico, ub, solo_siete: bool = True) -> tuple[dict[str, dict], list[str], int]:
    dep: dict[str, dict] = defaultdict(lambda: {"cat": defaultdict(float), "ing": defaultdict(float), "peajes": 0})
    sin, usados = [], 0
    for (_, nom), cats in trafico.items():
        d = ub.get(nombre(nom))
        if d is None:
            sin.append(nom)
            continue
        if solo_siete and not esquema_siete(cats):
            continue
        usados += 1
        dep[d]["peajes"] += 1
        for c, (t, ing) in cats.items():
            dep[d]["cat"][c] += t
            dep[d]["ing"][c] += ing
    return dep, sin, usados


def pesados(d: dict) -> float:
    cam = sum(d["cat"].get(c, 0.0) for c in CAMIONES)
    return (d["cat"].get("VI", 0.0) + d["cat"].get("VII", 0.0)) / cam if cam > 0 else float("nan")


def forma_tarifa(d: dict) -> float:
    t = {c: d["ing"][c] / d["cat"][c] for c in ("III", "V") if d["cat"].get(c, 0) > 0}
    return t["V"] / t["III"] if len(t) == 2 and t["III"] > 0 else float("nan")


def rho_ic(x, y, rng) -> dict:
    return base.spearman_boot(np.asarray(x, float), np.asarray(y, float), rng, 3000)


if __name__ == "__main__":
    rng = np.random.default_rng(base.SEMILLA)
    ub = ubicacion_peajes()
    dep24, sin24, n24 = por_departamento(trafico_ani(2024), ub)
    dep16, _, n16 = por_departamento(trafico_ani(2016), ub)
    print(f"ANI 2024: {n24} peajes con esquema de 7 categorías ubicados en {len(dep24)} departamentos; sin coincidencia de nombre: {len(sin24)}  | 2016: {n16} peajes")
    mez11 = base.cargar_mezcla(2011)
    p11 = {d: float(np.vstack(v)[:, 3:].sum() / np.vstack(v).sum()) for d, v in mez11.items()}
    h24 = {d: pesados(v) for d, v in dep24.items() if v["peajes"] >= 1 and not np.isnan(pesados(v))}
    h16 = {d: pesados(v) for d, v in dep16.items() if not np.isnan(pesados(v))}
    res: dict = {"peajes_2024": n24, "sin_coincidencia": len(sin24), "pesados_2024": h24}
    for nombre_p, a, b in (("P1 INVIAS 2011 vs ANI 2016", p11, h16), ("P2 INVIAS 2011 vs ANI 2024", p11, h24), ("P3 ANI 2016 vs ANI 2024", h16, h24)):
        ds = sorted(set(a) & set(b))
        r = rho_ic([a[d] for d in ds], [b[d] for d in ds], rng)
        res[nombre_p] = r
        print(f"{nombre_p:30s} n={r['n']:2d} rho={r['rho']:.2f} IC95 ({r['ic95'][0]:.2f}, {r['ic95'][1]:.2f}) p_perm={r['p_perm']:.3f}")
    ds = sorted(d for d in h24 if not np.isnan(forma_tarifa(dep24[d])) and dep24[d]["peajes"] >= 1)
    t2 = rho_ic([h24[d] for d in ds], [forma_tarifa(dep24[d]) for d in ds], rng)
    res["T2_prima_ANI2024_pesados_vs_forma_tarifa"] = t2
    print(f"T2' (pesados ANI 2024 vs R=V/III, tarifas ANI): n={t2['n']} rho={t2['rho']:.2f} IC95 ({t2['ic95'][0]:.2f}, {t2['ic95'][1]:.2f}) p_perm={t2['p_perm']:.3f}")

    # Réplica de la prórroga
    mezcla, obras = base.cargar_mezcla(2011), base.cargar_obras()
    ds_s = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    filas = logi.cargar_contratos({d: p11[d] for d in ds_s})
    comunes = sorted(set(d for d in ds_s if d in h24) & {f["dpto"] for f in filas})
    filas = [f for f in filas if f["dpto"] in comunes]
    pib = cov.cargar_pib()
    print(f"\nRéplica prórroga: {len(comunes)} departamentos con SECOP + mezcla 2011 + ANI 2024; contratos={len(filas)}")
    ef, ee = cov.etapa1(filas, "prorroga", comunes)
    res["replica_prorroga"] = {}
    for nom, serie in (("predictor INVIAS 2011", p11), ("predictor ANI 2024", h24)):
        p = np.array([serie[d] for d in comunes])
        for mod, cs in (("solo pesados", []), ("+ log PIB", [np.array([pib[d]["log_pib"] for d in comunes])])):
            r = cov.etapa2(ef, ee, p, cs)
            res["replica_prorroga"][f"{nom} | {mod}"] = r
            print(f"{nom:24s} {mod:14s} OR/+10pp={r['OR_por_10pp']:.3f} IC95 ({r['ic95'][0]:.3f}-{r['ic95'][1]:.3f}) p_t={r['p_t']:.3f} gl={r['gl']}")
    res["departamentos_replica"] = comunes
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
