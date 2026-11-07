"""Verificacion aguas arriba de la hipotesis fluvial (issue #95). Diseno en
PROTOCOLO_ANALISIS.md seccion 14, fijado antes de correr.

1) Para cada estacion IDEAM utilizable, sigue el flujo D8 rio abajo en el DEM de ~90 m del departamento y
   registra los municipios por los que pasa (conexion hidrologica).
2) Reasigna a cada municipio la estacion CONECTADA mas cercana (<= 100 km) y repite el estadistico fluvial.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from shapely.geometry import Point
from scipy.stats import spearmanr

import fluvial_inundaciones_caribe as fl   # carga estaciones y reutiliza utilidades (configura UTF-8)

if not hasattr(np, "in1d"):          # pysheds 0.5 usa np.in1d, eliminada en NumPy recientes
    np.in1d = np.isin
from pysheds.grid import Grid  # noqa: E402

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402
import cuando_inundaciones_caribe as cu  # noqa: E402

RADIO_SNAP = 3
MAX_PASOS = 40000
KM_MAX = 100
UMBRAL_CAUCE_KM2 = 5.0
DIRS = {64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)}   # dirmap por defecto de pysheds
KM2_CELDA = (3 / 3600 * 111.32) ** 2 * 0.985
RNG = np.random.default_rng(20261106)


def rutas_por_departamento(util: dict, pols: dict) -> dict:
    """codigo_estacion -> {munis: [...], fin: str, acc_km2: float, depto: str}"""
    res = {}
    for d in dc.DEPTOS:
        tif = AQUI / "_cache" / f"dem90_{d}.tif"
        if not tif.exists():
            continue
        grid = Grid.from_raster(str(tif))
        dem = grid.read_raster(str(tif))
        flooded = grid.fill_depressions(grid.fill_pits(dem))
        inflated = grid.resolve_flats(flooded)
        fdir = np.array(grid.flowdir(inflated))
        sin_dato = np.array(dem) == -9999.0
        acc = np.array(grid.accumulation(grid.flowdir(inflated)))
        H, W = fdir.shape
        lab = np.full((H, W), -1, dtype=np.int32)
        codigos = [c for c in pols if c.startswith(d)]
        for i, c in enumerate(codigos):
            mk = features.geometry_mask([pols[c]["geom"].buffer(0).__geo_interface__], out_shape=(H, W), transform=grid.affine, invert=True)
            lab[mk] = i
        inv = ~grid.affine
        for cod, e in util.items():
            col, row = inv * (e["longitud"], e["latitud"])
            r0, c0 = int(row), int(col)
            if not (RADIO_SNAP <= r0 < H - RADIO_SNAP and RADIO_SNAP <= c0 < W - RADIO_SNAP):
                continue
            borde = min(r0, c0, H - 1 - r0, W - 1 - c0)
            if cod in res and res[cod]["borde"] >= borde:
                continue      # la estacion cae en varias cuadriculas: se queda con la mas interior
            ventana = acc[r0 - RADIO_SNAP:r0 + RADIO_SNAP + 1, c0 - RADIO_SNAP:c0 + RADIO_SNAP + 1]
            dr, dc_ = np.unravel_index(np.argmax(ventana), ventana.shape)
            r, c = r0 - RADIO_SNAP + dr, c0 - RADIO_SNAP + dc_
            acc_km2 = float(acc[r, c]) * KM2_CELDA
            munis, fin, vistos = [], "borde", set()
            for _ in range(MAX_PASOS):
                if lab[r, c] >= 0 and codigos[lab[r, c]] not in munis:
                    munis.append(codigos[lab[r, c]])
                v = int(fdir[r, c])
                if v not in DIRS:
                    # Sin direccion de flujo: puede ser el BORDE de la cuadricula, el MAR (celdas sin dato vecinas) o un sumidero interior.
                    if min(r, c, H - 1 - r, W - 1 - c) <= 1:
                        fin = "borde"
                    elif sin_dato[max(r - 1, 0):r + 2, max(c - 1, 0):c + 2].any():
                        fin = "mar/sin dato"
                    else:
                        fin = "sumidero interior"
                    break
                if (r, c) in vistos:
                    fin = "ciclo"
                    break
                vistos.add((r, c))
                r, c = r + DIRS[v][0], c + DIRS[v][1]
                if not (0 <= r < H and 0 <= c < W):
                    fin = "borde"
                    break
            res[cod] = {"munis": munis, "fin": fin, "acc_km2": acc_km2, "depto": d, "borde": borde}
        print(f"  {d} {dc.DEPTOS[d]}: {sum(1 for v in res.values() if v['depto'] == d)} estaciones trazadas", flush=True)
    return res


def main() -> None:
    ch = json.loads((AQUI / "chirps_mensual_caribe.json").read_text(encoding="utf-8"))
    meses = ch["meses"]
    idx = {m: i for i, m in enumerate(meses)}
    cods = list(ch["municipios"])
    pols = dc.poligonos()
    hand = {m["codigo"]: m for m in json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"] if "frac_hand_lt10_5" in m}
    ung = dc.ungrd(cods)
    inund = defaultdict(set)
    for r in ung:
        k = str(r["fecha"])[:7]
        if k in idx and r["evento"] in dc.EVENTOS_INUNDACION:
            inund[r["codigo_municipio"]].add(idx[k])
    est, q = fl.cargar_estaciones_y_caudales(meses)
    util = {e["codigo"]: e for e in est if len(q.get(e["codigo"], {})) >= fl.MIN_MESES_ESTACION}
    print(f"Estaciones utilizables: {len(util)}", flush=True)

    rutas = rutas_por_departamento(util, pols)
    print(f"Estaciones trazadas: {len(rutas)} de {len(util)}")
    sobre_cauce = sum(1 for v in rutas.values() if v["acc_km2"] >= UMBRAL_CAUCE_KM2)
    print(f"  sobre un cauce resuelto (area acumulada >= {UMBRAL_CAUCE_KM2:g} km2): {sobre_cauce} ({100 * sobre_cauce / max(1, len(rutas)):.0f} %)")
    fines = defaultdict(int)
    for v in rutas.values():
        fines[v["fin"]] += 1
    print(f"  fin de la ruta: {dict(fines)}; municipios aguas abajo por estacion (mediana): {np.median([len(v['munis']) for v in rutas.values()]):.0f}")

    def evaluar(cod_mun, cod_est):
        serie = q[cod_est]
        mm = [m for m in meses if m in serie]
        v = np.array([serie[m] for m in mm])
        sd = v.std(ddof=1)
        if sd == 0:
            return None
        zq = {idx[m]: (serie[m] - v.mean()) / sd for m in mm}
        p = np.array(ch["municipios"][cod_mun]["precip_mm"], float)
        zp = (p - p.mean()) / p.std(ddof=1)
        pos = [i for i in inund[cod_mun] if i in zq]
        neg = [i for i in zq if i not in inund[cod_mun]]
        if len(pos) < cu.MIN_POS or len(neg) < cu.MIN_NEG:
            return None
        return cu.auc(np.array([zq[i] for i in pos]), np.array([zq[i] for i in neg])) - cu.auc(zp[pos], zp[neg])

    conectados, no_conect, indeterminados, sin_est = [], [], [], 0
    for c in cods:
        if c not in hand:
            continue
        geom = pols[c]["geom"].buffer(0)
        dist = {k: geom.distance(Point(util[k]["longitud"], util[k]["latitud"])) * fl.KM_POR_GRADO for k in rutas}
        cand = sorted((d, k) for k, d in dist.items() if d <= KM_MAX)
        if not cand:
            sin_est += 1
            continue
        con = [(d, k) for d, k in cand if c in rutas[k]["munis"]]
        if con:
            dd, k = con[0]
            dif = evaluar(c, k)
            if dif is not None:
                conectados.append((c, c[:2], dif, hand[c]["frac_hand_lt10_5"], dd, k, rutas[k]["acc_km2"]))
            continue
        d0, k0 = cand[0]
        if rutas[k0]["fin"] == "borde":
            indeterminados.append(c)
            continue
        dif = evaluar(c, k0)
        if dif is not None:
            no_conect.append((c, c[:2], dif, hand[c]["frac_hand_lt10_5"], d0, k0, rutas[k0]["acc_km2"]))

    def resumen(nombre, filas):
        print(f"\n== {nombre}: {len(filas)} municipios elegibles ==")
        if len(filas) < 15:
            print("   muy pocos para estimar")
            return None
        dif = np.array([f[2] for f in filas]); h = np.array([f[3] for f in filas]); bl = np.array([f[1] for f in filas])
        r0 = spearmanr(h, dif)[0]
        et = np.unique(bl); bs = []
        for _ in range(cu.N_BOOT):
            ix = np.concatenate([np.where(bl == b)[0] for b in RNG.choice(et, len(et), replace=True)])
            if np.ptp(h[ix]) > 0 and np.ptp(dif[ix]) > 0:
                bs.append(spearmanr(h[ix], dif[ix])[0])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        t = np.percentile(h, [33.3, 66.7])
        print(f"   rho(fraccion HAND<10 m, AUC caudal - AUC lluvia) = {r0:+.2f}  IC95% bloques [{lo:+.2f}, {hi:+.2f}] | diferencia media de AUC {dif.mean():+.3f}")
        print(f"   menos llanura: {dif[h <= t[0]].mean():+.3f} (n={int((h <= t[0]).sum())}) | intermedio: {dif[(h > t[0]) & (h <= t[1])].mean():+.3f} | mas llanura: {dif[h > t[1]].mean():+.3f} (n={int((h > t[1]).sum())})")
        print(f"   distancia mediana a la estacion: {np.median([f[4] for f in filas]):.1f} km; estaciones distintas: {len(set(f[5] for f in filas))}; "
              f"estaciones sobre cauce resuelto: {100 * np.mean([f[6] >= UMBRAL_CAUCE_KM2 for f in filas]):.0f} %")
        return r0, lo, hi

    print(f"\nMunicipios sin estacion a <= {KM_MAX} km: {sin_est} | pares indeterminados (la ruta sale de la cuadricula): {len(indeterminados)}")
    rc = resumen("PRINCIPAL: estacion CONECTADA mas cercana (aguas arriba verificada)", conectados)
    rn = resumen("CONTRASTE: municipios cuya estacion mas cercana NO esta conectada", no_conect)
    ref = (0.41, 0.06, 0.57)
    if rc is None or len(conectados) < 30:
        veredicto = "INSUFICIENTE: menos de 30 municipios elegibles con estacion conectada"
    elif rc[1] > 0 and rc[0] >= ref[0]:
        veredicto = "REFORZADA: el IC excluye 0 y el rho es >= al de la seccion 11 (+0,41)"
    else:
        veredicto = "DEBILITADA: el IC incluye 0 o el rho es menor que el de la seccion 11 (+0,41)"
    print(f"\nVEREDICTO (regla fija): {veredicto}")
    print("LIMITES: DEM de superficie a 90 m; el ajuste de la estacion a la red es una eleccion; cuadriculas departamentales (conexion entre "
          "departamentos indeterminada si la ruta sale de la cuadricula); ~68 estaciones; un caudal medido en un tramo no es el que inunda aguas abajo.")
    (AQUI / "aguas_arriba_fluvial.json").write_text(json.dumps({
        "n_conectados": len(conectados), "n_no_conectados": len(no_conect), "n_indeterminados": len(indeterminados),
        "principal": None if rc is None else {"rho": rc[0], "ic": [rc[1], rc[2]]},
        "contraste": None if rn is None else {"rho": rn[0], "ic": [rn[1], rn[2]]}, "veredicto": veredicto}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
