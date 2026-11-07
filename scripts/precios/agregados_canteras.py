"""B1: precio de agregados vs produccion de canteras (protocolo PROTOCOLO_AGREGADOS_CANTERAS.md)."""
from __future__ import annotations

import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import requests
from scipy.stats import rankdata, spearmanr

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "construdata"))
import divipola  # noqa: E402

RNG = np.random.default_rng(20261108)
N_BOOT = 3000
RECURSOS = ["GRAVAS", "ARENAS", "RECEBO", "GRAVAS DE RIO", "ARENA DE RIO", "GRAVA DE CANTERA", "ARENA DE CANTERA", "DIABASA"]
N_PRODUCTORES = 25
MIN_COBERTURA = 0.70
CACHE_ANM = AQUI / "_cache" / "anm_agregados.json"


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def volumenes_anm():
    if CACHE_ANM.exists():
        return json.loads(CACHE_ANM.read_text(encoding="utf-8"))
    lista = ",".join("'" + r + "'" for r in RECURSOS)
    filas, off = [], 0
    while True:
        r = requests.get("https://www.datos.gov.co/resource/r85m-vv6c.json", timeout=120, params={
            "$select": "codigo_dane,volumenes_de_explotacion as v", "$order": ":id",
            "$where": "recurso_natural in(" + lista + ") and a_o_liquidado between '2019' and '2024'",
            "$limit": 5000, "$offset": off})
        r.raise_for_status()
        lote = r.json()
        filas += lote
        if len(lote) < 5000:
            break
        off += 5000
    suma = defaultdict(float)
    for f in filas:
        if f.get("codigo_dane"):
            suma[str(f["codigo_dane"]).zfill(5)] += max(num(f.get("v")), 0.0)
    filas = [{"codigo_dane": k, "v": v} for k, v in suma.items()]
    CACHE_ANM.parent.mkdir(exist_ok=True)
    CACHE_ANM.write_text(json.dumps(filas), encoding="utf-8")
    return filas


def num(s):
    try:
        return float(str(s).replace(",", "").replace(" ", ""))
    except ValueError:
        return 0.0


def pos(cod):
    r = divipola.resolver_por_codigo(cod)
    return (r["latitud"], r["longitud"]) if r and r.get("latitud") else None


def remuestra(bl):
    et = np.unique(bl)
    return np.concatenate([np.where(bl == b)[0] for b in RNG.choice(et, len(et), replace=True)])


def parcial(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    A = np.vstack([rz, np.ones_like(rz)]).T
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
    ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def boot(fn, a, bl):
    out = []
    for _ in range(N_BOOT):
        ix = remuestra(bl)
        if np.ptp(a[ix, 1]) > 0 and np.ptp(a[ix, 2]) > 0:
            out.append(fn(ix))
    return np.array(out)


def main():
    divipola._cargar_cache()
    ins = {i["codigo"]: i for i in json.loads((AQUI / "_cache/invias_insumos.json").read_text(encoding="utf-8"))}
    prov = {p["codigo"]: p for p in json.loads((AQUI / "_cache/invias_provincias.json").read_text(encoding="utf-8"))}
    precios = json.loads((AQUI / "_cache/invias_insumos_precios.json").read_text(encoding="utf-8"))
    por_ins = defaultdict(dict)
    for p in precios:
        i = ins.get(p["insumo_codigo"])
        if i and i["categoria"] == "AGREGADOS" and i["unidad"] == "m3" and p["precio"] > 0:
            por_ins[p["insumo_codigo"]][p["provincia_codigo"]] = p["precio"]
    usados = {c: d for c, d in por_ins.items() if len(d) >= MIN_COBERTURA * len(prov)}
    print(f"Insumos de agregados en m3: {len(por_ins)}; con cobertura >= {MIN_COBERTURA:.0%}: {len(usados)}")
    med = {c: np.median(list(d.values())) for c, d in usados.items()}
    idx = {}
    for c in prov:
        v = [math.log(d[c] / med[k]) for k, d in usados.items() if c in d]
        if len(v) >= 3:
            idx[c] = math.exp(np.mean(v))
    vol_mun = {str(f["codigo_dane"]).zfill(5): num(f["v"]) for f in volumenes_anm() if f.get("codigo_dane")}
    vol_dep = defaultdict(float)
    for m, v in vol_mun.items():
        vol_dep[m[:2]] += v
    top = sorted(vol_mun, key=vol_mun.get, reverse=True)[:N_PRODUCTORES]
    top_pos = [p for p in (pos(m) for m in top) if p]
    print(f"Municipios con produccion declarada: {len(vol_mun)}; productores de referencia con coordenadas: {len(top_pos)}")
    bog = pos("11001")
    puertos = [pos(c) for c in ("13001", "08001", "47001", "76109")]
    filas = []
    for c, ind in idx.items():
        dep = f"{prov[c]['codigo_departamento']:0>2}"
        cap = pos(dep + "001")
        if not cap or not bog or not all(puertos) or not top_pos:
            continue
        filas.append((ind, math.log10(1 + vol_dep.get(dep, 0)), min(km(cap, t) for t in top_pos),
                      km(cap, bog), min(km(cap, p) for p in puertos), dep))
    a = np.array([f[:5] for f in filas], float)
    bl = np.array([f[5] for f in filas])
    print(f"Provincias analizadas: {len(filas)} en {len(set(bl))} departamentos\n")
    # columnas de a: 0 indice, 1 log volumen, 2 dist productor, 3 dist Bogota, 4 dist puerto
    pruebas = {"B1a": (1, -1), "B1b": (2, +1)}
    res = {}
    for n, (col, signo) in pruebas.items():
        r0 = spearmanr(a[:, col], a[:, 0])[0]
        bs = boot(lambda ix, col=col: spearmanr(a[ix, col], a[ix, 0])[0], a, bl)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        p = min(1.0, 2 * float(np.mean(bs * signo <= 0)))
        res[n] = (float(r0), float(lo), float(hi), p, signo)
        print(f"{n}: rho = {r0:+.2f}  IC95 por departamentos [{lo:+.2f}, {hi:+.2f}]  p = {p:.4f}")
    ok = {}
    sigue = True
    for i, (n, v) in enumerate(sorted(res.items(), key=lambda kv: kv[1][3])):
        aj = min(1.0, v[3] * (len(res) - i))
        ok[n] = bool(sigue and aj < 0.05 and v[0] * v[4] > 0)
        sigue = ok[n]
        print(f"  Holm {n}: p ajustado = {aj:.4f} -> {'CUMPLE' if ok[n] else 'NO cumple'}")
    for nom, col in (("distancia a Bogota", 3), ("distancia al puerto", 4)):
        r0 = spearmanr(a[:, col], a[:, 0])[0]
        bs = boot(lambda ix, col=col: spearmanr(a[ix, col], a[ix, 0])[0], a, bl)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"Referencia: indice vs {nom}: rho = {r0:+.2f} [{lo:+.2f}, {hi:+.2f}]")
    p0 = parcial(a[:, 2], a[:, 0], a[:, 3])
    bs = boot(lambda ix: parcial(a[ix, 2], a[ix, 0], a[ix, 3]), a, bl)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"B1c (parcial: indice vs distancia a productor | distancia a Bogota): rho = {p0:+.2f} [{lo:+.2f}, {hi:+.2f}]"
          + ("" if ok.get("B1b") else "  (B1b no se cumplio: B1c es solo descriptiva)"))
    (AQUI / "agregados_canteras_resultados.json").write_text(json.dumps(
        {"n_provincias": len(filas), "B1": {k: list(v[:4]) for k, v in res.items()}, "cumple": ok, "B1c": [p0, float(lo), float(hi)]}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
