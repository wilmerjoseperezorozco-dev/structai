"""Cruces estadísticos: (1) tarifas de peajes × mezcla de camiones INVIAS y (2) contratos de obra SECOP × mezcla de camiones.

Entradas
- data/transporte/composicion_camiones_invias.csv  (mezcla de camiones por estación y año, de composicion_camiones_invias.py)
- datos.gov.co recurso 68qj-5xux ("Peajes": coordenadas y tarifas por categoría I-VII; se descarga a data/transporte/_cache/)
- límites departamentales DANE MGN 2018 en GeoJSON (se descarga a la caché; asignación peaje→departamento por punto en polígono)
- scripts/secop/_cache/contratos_obra.jsonl  (contratos de obra de SECOP II, sin columnas de identidad)

Salida: data/transporte/cruces_resultados.json y un resumen en pantalla.

Decisiones de diseño (todas son hipótesis declaradas, no hechos verificados):
- Clase INVIAS → categoría de peaje: H0 (por ejes) C-2P→III, C-2G→IV, C-3-4→V, C-5→VI, >C-5→VII. Se contrastan H1 y H2 como sensibilidad.
  Lo único comprobado en los datos es que las tarifas III<=IV<=V son monótonas en los 166 peajes con categoría III.
- Se excluyen los peajes sin categoría III (13) y el de tarifa plana en las 7 categorías (La Parada, $2.700): no representan un cuadro tarifario.
- Si una categoría pesada vale 0 en un peaje se arrastra la última categoría no nula (hay 87 peajes con VI>0 de 179).
- El costo esperado por paso de camión crece POR CONSTRUCCIÓN con la proporción de pesados; no se correlaciona con ella (sería circular).
  El contraste inferencial usa la forma de la tarifa R = tarifa V / tarifa III, que no depende de la mezcla.
- La mezcla es de 2011 (fin de la serie INVIAS disponible) y los contratos de 2016-2026: desfase temporal, falacia ecológica, n pequeño.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from shapely.geometry import Point, shape

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "data" / "transporte" / "_cache"
MEZCLA = RAIZ / "data" / "transporte" / "composicion_camiones_invias.csv"
OBRAS = RAIZ / "scripts" / "secop" / "_cache" / "contratos_obra.jsonl"
SALIDA = RAIZ / "data" / "transporte" / "cruces_resultados.json"
URL_PEAJES = "https://www.datos.gov.co/resource/68qj-5xux.json?$limit=500"
URL_DPTO = "https://raw.githubusercontent.com/caticoa3/colombia_mapa/master/co_2018_MGN_DPTO_POLITICO.geojson"
CLASES = ("C-2P", "C-2G", "C-3-4", "C-5", ">C-5")
CATS = ("i", "ii", "iii", "iv", "v", "vi", "vii")
MAPEOS = {  # clase -> índice en CATS
    "H0": (2, 3, 4, 5, 6),
    "H1": (2, 3, 4, 4, 5),
    "H2": (2, 2, 4, 5, 6),
}
SEMILLA, REPS = 20261109, 5000
VALOR_MAX_COP = 1e12            # un contrato de obra municipal de más de un billón se trata como error de digitación
ALIAS_DPTO = {"VALLE DEL CAUCA": "VALLE", "LA GUAJIRA": "GUAJIRA", "SANTAFE DE BOGOTA D.C": "CUNDINAMARCA", "DISTRITO CAPITAL DE BOGOTA": "CUNDINAMARCA",
              "BOGOTA D.C.": "CUNDINAMARCA", "BOGOTA": "CUNDINAMARCA"}
VIAL = re.compile(r"\b(via|vias|vial|viales|pavimento|pavimentacion|placa huella|carretera|carreteable|puente|rehabilitacion de la via|mantenimiento vial)\b")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper().strip()
    return ALIAS_DPTO.get(s, s)


def descargar(url: str, destino: Path) -> Path:
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=90) as r:  # noqa: S310 - URLs fijas de datos abiertos
            destino.write_bytes(r.read())
    return destino


def cargar_peajes() -> list[dict]:
    """Peajes con departamento asignado por punto en polígono (los que caen fuera, al departamento más cercano) y tarifas arrastradas."""
    pol = [(norm(f["properties"]["NOMBRE_DPT"] if "NOMBRE_DPT" in f["properties"] else f["properties"]["DPTO_CNMBR"]), shape(f["geometry"]))
           for f in json.loads(descargar(URL_DPTO, CACHE / "dpto_mgn2018.geojson").read_text(encoding="utf-8"))["features"]]
    out, fuera = [], []
    for r in json.loads(descargar(URL_PEAJES, CACHE / "peajes_68qj-5xux.json").read_text(encoding="utf-8")):
        c = (r.get("point") or {}).get("coordinates")
        if not c:
            continue
        p = Point(*c)
        dep = next((n for n, g in pol if g.contains(p)), None)
        if dep is None:
            dep = min(pol, key=lambda t: t[1].distance(p))[0]
            fuera.append(r["nombre_peaje"])
        tar = [float(r.get(f"categoria_{k}") or 0) for k in CATS]
        if tar[2] <= 0:
            continue                      # sin categoría III no hay referencia de camión liviano
        for j in range(3, 7):             # arrastre de la última categoría no nula
            if tar[j] <= 0:
                tar[j] = tar[j - 1]
        if len(set(tar)) == 1:
            continue                      # tarifa plana en las 7 categorías (La Parada, $2.700): no es un cuadro tarifario
        out.append({"peaje": r["nombre_peaje"], "dpto": dep, "tar": tar})
    print(f"peajes usados {len(out)}; asignados por cercanía (fuera de polígono): {fuera}")
    return out


def cargar_mezcla(anio: int) -> dict[str, list[np.ndarray]]:
    """territorial normalizada -> lista de vectores de 5 conteos (uno por estación) del año dado."""
    out: dict[str, list[np.ndarray]] = defaultdict(list)
    for f in csv.DictReader(MEZCLA.open(encoding="utf-8")):
        if int(f["anio"]) == anio:
            out[norm(f["territorial"])].append(np.array([float(f[c]) for c in CLASES]))
    return out


def ic(x: np.ndarray, nivel: float = 0.95) -> tuple[float, float]:
    a = (1 - nivel) / 2
    return float(np.quantile(x, a)), float(np.quantile(x, 1 - a))


def costo_esperado_boot(est: list[np.ndarray], tar: np.ndarray, mapeo: tuple[int, ...], rng, reps: int = REPS) -> tuple[float, tuple[float, float]]:
    """E[tarifa por paso de camión] = suma_c p_c * tarifa_cat(c). Bootstrap conjunto sobre estaciones (mezcla) y peajes (tarifa)."""
    est_m, idx = np.vstack(est), list(mapeo)
    punto = float((est_m.sum(0) / est_m.sum()) @ tar[:, idx].mean(0))
    n_e, n_t = len(est_m), len(tar)
    sims = np.empty(reps)
    for b in range(reps):
        p = est_m[rng.integers(0, n_e, n_e)].sum(0)
        t = tar[rng.integers(0, n_t, n_t)][:, idx].mean(0)
        sims[b] = (p / p.sum()) @ t
    return punto, ic(sims)


def spearman_boot(x: np.ndarray, y: np.ndarray, rng, reps: int = REPS) -> dict:
    rho, _ = stats.spearmanr(x, y)
    n = len(x)
    boots = []
    for _ in range(reps):
        i = rng.integers(0, n, n)
        if len(set(x[i])) > 1 and len(set(y[i])) > 1:
            boots.append(stats.spearmanr(x[i], y[i])[0])
    perm = stats.permutation_test((x,), lambda a: stats.spearmanr(a, y)[0], permutation_type="pairings", n_resamples=9999, random_state=int(rng.integers(1 << 31)),
                                  alternative="two-sided")
    return {"n": n, "rho": float(rho), "ic95": ic(np.array(boots)), "p_perm": float(perm.pvalue)}


def parcial_boot(x: np.ndarray, y: np.ndarray, z: np.ndarray, rng, reps: int = REPS) -> dict:
    """Spearman parcial de x e y controlando z: residuos de las regresiones de rangos."""
    def par(a, b, c):
        ra, rb, rc = (stats.rankdata(v) for v in (a, b, c))
        X = np.column_stack([np.ones_like(rc), rc])
        res = lambda r: r - X @ np.linalg.lstsq(X, r, rcond=None)[0]  # noqa: E731
        return float(np.corrcoef(res(ra), res(rb))[0, 1])
    n = len(x)
    boots = [par(x[i], y[i], z[i]) for i in (rng.integers(0, n, n) for _ in range(reps)) if len(set(x[i])) > 1 and len(set(y[i])) > 1 and len(set(z[i])) > 1]
    obs = par(x, y, z)
    cnt = sum(abs(par(x, rng.permutation(y), z)) >= abs(obs) for _ in range(4999))
    return {"n": n, "rho_parcial": obs, "ic95": ic(np.array(boots)), "p_perm": (cnt + 1) / 5000}


def holm(p: dict[str, float]) -> dict[str, float]:
    orden = sorted(p, key=p.get)
    m, ajust, previo = len(p), {}, 0.0
    for k, nombre in enumerate(orden):
        previo = max(previo, min(1.0, (m - k) * p[nombre]))
        ajust[nombre] = previo
    return ajust


def kruskal_epsilon(grupos: list[np.ndarray]) -> dict:
    h, p = stats.kruskal(*grupos)
    n = sum(len(g) for g in grupos)
    return {"k": len(grupos), "n": n, "H": float(h), "p": float(p), "epsilon2": float((h - len(grupos) + 1) / (n - len(grupos)))}


def cruce_peajes(peajes: list[dict], mezcla: dict[str, list[np.ndarray]], rng) -> dict:
    por_dpto: dict[str, np.ndarray] = {}
    for d in {p["dpto"] for p in peajes}:
        por_dpto[d] = np.array([p["tar"] for p in peajes if p["dpto"] == d])
    comunes = sorted(set(por_dpto) & set(mezcla))
    print(f"\n== Cruce 1: departamentos con peajes y mezcla 2011: {len(comunes)}")
    filas = {}
    for d in comunes:
        est_m = np.vstack(mezcla[d])
        pes = float(est_m[:, 3:].sum() / est_m.sum())
        r = float(np.mean(por_dpto[d][:, 4] / por_dpto[d][:, 2]))
        costos = {h: costo_esperado_boot(mezcla[d], por_dpto[d], m, rng, 2000) for h, m in MAPEOS.items()}
        filas[d] = {"n_estaciones": len(mezcla[d]), "n_peajes": len(por_dpto[d]), "pesados_C5_mas": pes, "R_V_sobre_III": r,
                    "costo_esperado_COP": {h: {"punto": v[0], "ic95": v[1]} for h, v in costos.items()}}
        print(f"{d:20s} est={len(mezcla[d]):3d} peajes={len(por_dpto[d]):3d} pesados={100 * pes:5.1f}%  R={r:4.2f}  E[H0]={costos['H0'][0]:8.0f} "
              f"[{costos['H0'][1][0]:.0f}-{costos['H0'][1][1]:.0f}]")
    pes = np.array([filas[d]["pesados_C5_mas"] for d in comunes])
    rr = np.array([filas[d]["R_V_sobre_III"] for d in comunes])
    t2 = spearman_boot(pes, rr, rng)
    t1 = kruskal_epsilon([por_dpto[d][:, 4] for d in comunes if len(por_dpto[d]) >= 2])
    rob = {h: float(stats.spearmanr(pes, [filas[d]["costo_esperado_COP"][h]["punto"] for d in comunes])[0]) for h in MAPEOS}
    return {"por_departamento": filas, "T1_kruskal_tarifa_cat_V": t1, "T2_spearman_pesados_vs_R": t2, "rho_descriptivo_pesados_vs_costo_por_mapeo": rob}


def cargar_obras() -> dict[str, dict]:
    ag: dict[str, dict] = defaultdict(lambda: {"n": 0, "valor": 0.0, "n_vial": 0, "valor_vial": 0.0})
    descartados = 0
    for linea in OBRAS.open(encoding="utf-8"):
        c = json.loads(linea)
        try:
            v = float(c.get("valor_del_contrato") or 0)
        except ValueError:
            continue
        if v <= 0 or v > VALOR_MAX_COP:
            descartados += v > VALOR_MAX_COP
            continue
        d = norm(c.get("departamento", ""))
        a = ag[d]
        a["n"] += 1
        a["valor"] += v
        txt = unicodedata.normalize("NFKD", (c.get("objeto_del_contrato") or "").lower()).encode("ascii", "ignore").decode()
        if VIAL.search(txt):
            a["n_vial"] += 1
            a["valor_vial"] += v
    print(f"contratos de obra agregados; descartados por valor > {VALOR_MAX_COP:.0e}: {descartados}")
    return ag


def cruce_secop(mezcla: dict[str, list[np.ndarray]], obras: dict[str, dict], rng) -> dict:
    comunes = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    print(f"\n== Cruce 2: departamentos con contratos de obra y mezcla 2011: {len(comunes)} (Ocaña excluida: no se pudo verificar su equivalencia)")
    pes = np.array([np.vstack(mezcla[d])[:, 3:].sum() / np.vstack(mezcla[d]).sum() for d in comunes])
    nest = np.array([len(mezcla[d]) for d in comunes], float)
    lv = np.log10([obras[d]["valor_vial"] + 1 for d in comunes])
    ln = np.log10([obras[d]["n_vial"] + 1 for d in comunes])
    cuota = np.array([obras[d]["valor_vial"] / obras[d]["valor"] for d in comunes])
    t3 = parcial_boot(lv, pes, nest, rng)
    crudo = spearman_boot(lv, pes, rng)
    cuota_t = spearman_boot(cuota, pes, rng)
    print(f"pesados vs log valor vial: crudo rho={crudo['rho']:.2f}; parcial|n_estaciones rho={t3['rho_parcial']:.2f} IC95={t3['ic95']}; cuota vial rho={cuota_t['rho']:.2f}")
    return {"departamentos": comunes, "T3_parcial_pesados_vs_valor_vial": t3, "crudo_pesados_vs_valor_vial": crudo, "T4_pesados_vs_cuota_vial": cuota_t,
            "log_n_vial_vs_pesados_rho": float(stats.spearmanr(ln, pes)[0])}


def efecto_mezcla(peajes: list[dict], rng) -> dict:
    """Cambio de mezcla 2006->2011 con tarifas fijas, en las estaciones comunes (pareadas), por departamento y total."""
    def por_est(anio):
        out = {}
        for f in csv.DictReader(MEZCLA.open(encoding="utf-8")):
            if int(f["anio"]) == anio:
                out[(norm(f["territorial"]), f["estacion"])] = np.array([float(f[c]) for c in CLASES])
        return out
    a, b = por_est(2006), por_est(2011)
    tar_nac = np.array([p["tar"] for p in peajes])
    res = {}
    for d in ("ATLANTICO", "ANTIOQUIA", "BOLIVAR", "CUNDINAMARCA", "TODOS"):
        claves = [k for k in a if k in b and (d == "TODOS" or k[0] == d)]
        if len(claves) < 5:
            continue
        tar = tar_nac if d == "TODOS" else np.array([p["tar"] for p in peajes if p["dpto"] == d] or tar_nac)
        t = tar[:, list(MAPEOS["H0"])].mean(0)
        va = np.array([a[k] for k in claves]); vb = np.array([b[k] for k in claves])
        def delta(i):
            pa, pb = va[i].sum(0), vb[i].sum(0)
            return float((pb / pb.sum()) @ t - (pa / pa.sum()) @ t), float(pb[3:].sum() / pb.sum() - pa[3:].sum() / pa.sum())
        n = len(claves)
        base = delta(np.arange(n))
        boots = np.array([delta(rng.integers(0, n, n)) for _ in range(REPS)])
        res[d] = {"n_estaciones_comunes": n, "delta_costo_COP": base[0], "ic95_costo": ic(boots[:, 0]), "delta_pesados": base[1], "ic95_pesados": ic(boots[:, 1])}
        print(f"{d:12s} n={n:3d}  Δ pesados={100 * base[1]:+5.1f} pp IC95=({100 * res[d]['ic95_pesados'][0]:+.1f},{100 * res[d]['ic95_pesados'][1]:+.1f})  "
              f"Δ costo/paso={base[0]:+8.0f} COP IC95=({res[d]['ic95_costo'][0]:+.0f},{res[d]['ic95_costo'][1]:+.0f})")
    return res


if __name__ == "__main__":
    rng = np.random.default_rng(SEMILLA)
    peajes, mezcla11 = cargar_peajes(), cargar_mezcla(2011)
    r1 = cruce_peajes(peajes, mezcla11, rng)
    r2 = cruce_secop(mezcla11, cargar_obras(), rng)
    print("\n== Efecto de la mezcla 2006->2011 (tarifas fijas H0, estaciones comunes, bootstrap pareado)")
    r3 = efecto_mezcla(peajes, rng)
    p_holm = holm({"T1": r1["T1_kruskal_tarifa_cat_V"]["p"], "T2": r1["T2_spearman_pesados_vs_R"]["p_perm"], "T3": r2["T3_parcial_pesados_vs_valor_vial"]["p_perm"],
                   "T4": r2["T4_pesados_vs_cuota_vial"]["p_perm"]})
    print("\nHolm (4 pruebas):", {k: round(v, 4) for k, v in p_holm.items()})
    print("T1", r1["T1_kruskal_tarifa_cat_V"]); print("T2", r1["T2_spearman_pesados_vs_R"]); print("T3", r2["T3_parcial_pesados_vs_valor_vial"]); print("T4", r2["T4_pesados_vs_cuota_vial"])
    print("rho descriptivo pesados vs costo esperado (circular):", r1["rho_descriptivo_pesados_vs_costo_por_mapeo"])
    SALIDA.write_text(json.dumps({"cruce_peajes": r1, "cruce_secop": r2, "efecto_mezcla_2006_2011": r3, "p_holm": p_holm, "semilla": SEMILLA, "reps": REPS},
                                 ensure_ascii=False, indent=1, default=float), encoding="utf-8")
