"""Hipotesis fluvial (issue #95): ¿en municipios con mucho terreno bajo respecto al cauce (HAND)
los reportes de inundacion siguen el CAUDAL de un rio cercano mejor que la lluvia local?
Diseno en PROTOCOLO_ANALISIS.md seccion 11, fijado antes de correr.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from dotenv import dotenv_values
from scipy.stats import spearmanr
from shapely.geometry import Point
from supabase import create_client

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cruzar_relieve_ungrd_caribe as base  # noqa: E402,F401  (configura la salida UTF-8)
import _datos_caribe as dc  # noqa: E402
import cuando_inundaciones_caribe as cu  # noqa: E402  (auc, MIN_POS, MIN_NEG, N_BOOT)

BBOX = (-77.6, 7.7, -70.9, 12.7)
RADIOS_KM = (25, 50)
MIN_MESES_ESTACION = 48
KM_POR_GRADO = 111.32
RNG = np.random.default_rng(20261106)


def cargar_estaciones_y_caudales(meses: list[str]):
    env = dotenv_values(dc.RAIZ / "apps/api/.env")
    sb = create_client(env["SUPABASE_URL"], env.get("SUPABASE_SERVICE_KEY") or env["SUPABASE_KEY"])
    est, ini = [], 0
    while True:
        pag = (sb.table("ideam_estaciones_caudal").select("codigo,nombre,corriente,latitud,longitud")
               .gte("latitud", BBOX[1]).lte("latitud", BBOX[3]).gte("longitud", BBOX[0]).lte("longitud", BBOX[2])
               .range(ini, ini + 999).execute().data or [])
        est += pag
        if len(pag) < 1000:
            break
        ini += 1000
    cods = [e["codigo"] for e in est]
    q = defaultdict(dict)
    for k in range(0, len(cods), 80):
        ini = 0
        while True:
            pag = (sb.table("ideam_caudal_historico").select("codigo_estacion,fecha,caudal_m3s")
                   .in_("codigo_estacion", cods[k:k + 80]).gte("fecha", "2019-01-01").lte("fecha", "2024-12-31")
                   .range(ini, ini + 999).execute().data or [])
            for r in pag:
                m = str(r["fecha"])[:7]
                if m in meses and r["caudal_m3s"] is not None:
                    q[r["codigo_estacion"]][m] = float(r["caudal_m3s"])
            if len(pag) < 1000:
                break
            ini += 1000
    return est, q


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

    est, q = cargar_estaciones_y_caudales(meses)
    util = {e["codigo"]: e for e in est if len(q.get(e["codigo"], {})) >= MIN_MESES_ESTACION}
    print(f"Estaciones IDEAM en el bbox del Caribe: {len(est)}; con >= {MIN_MESES_ESTACION} meses de caudal en 2019-2024: {len(util)}")

    resultados = {}
    for R in RADIOS_KM:
        filas = []
        for j, c in enumerate(cods):
            if c not in hand:
                continue
            geom = pols[c]["geom"].buffer(0)
            dist = {k: geom.distance(Point(e["longitud"], e["latitud"])) * KM_POR_GRADO for k, e in util.items()}
            if not dist:
                continue
            k, d = min(dist.items(), key=lambda x: x[1])
            if d > R:
                continue
            serie = q[k]
            mm = [m for m in meses if m in serie]
            v = np.array([serie[m] for m in mm])
            sd = v.std(ddof=1)
            if sd == 0:
                continue
            zq = {idx[m]: (serie[m] - v.mean()) / sd for m in mm}
            p = np.array(ch["municipios"][c]["precip_mm"], float)
            zp_all = (p - p.mean()) / p.std(ddof=1)
            pos = [i for i in inund[c] if i in zq]
            neg = [i for i in zq if i not in inund[c]]
            if len(pos) < cu.MIN_POS or len(neg) < cu.MIN_NEG:
                continue
            a_q = cu.auc(np.array([zq[i] for i in pos]), np.array([zq[i] for i in neg]))
            a_p = cu.auc(zp_all[pos], zp_all[neg])
            filas.append({"c": c, "depto": c[:2], "est": k, "km": d, "auc_q": a_q, "auc_p": a_p, "hand": hand[c]["frac_hand_lt10_5"],
                          "corriente": util[k].get("corriente")})
        resultados[R] = filas

    for R, filas in resultados.items():
        print(f"\n===== Radio {R} km: {len(filas)} municipios elegibles =====")
        if len(filas) < 15:
            print("   muy pocos municipios elegibles para concluir")
            continue
        aq = np.array([f["auc_q"] for f in filas]); ap = np.array([f["auc_p"] for f in filas])
        dif = aq - ap
        h = np.array([f["hand"] for f in filas]); bl = np.array([f["depto"] for f in filas])
        lo, hi = cu.ic_bloques_media(aq, bl)
        print(f"   AUC medio del CAUDAL: {aq.mean():.3f} [{lo:.3f}, {hi:.3f}] | AUC medio de la LLUVIA (mismos municipios y meses): {ap.mean():.3f}")
        dlo, dhi = cu.ic_bloques_media(dif, bl)
        print(f"   diferencia media (caudal - lluvia): {dif.mean():+.3f}  IC95% bloques [{dlo:+.3f}, {dhi:+.3f}]")
        rho = spearmanr(h, dif)[0]
        et = np.unique(bl); bs = []
        for _ in range(cu.N_BOOT):
            ix = np.concatenate([np.where(bl == b)[0] for b in RNG.choice(et, len(et), replace=True)])
            if np.ptp(h[ix]) > 0 and np.ptp(dif[ix]) > 0:
                bs.append(spearmanr(h[ix], dif[ix])[0])
        l2, h2 = np.percentile(bs, [2.5, 97.5])
        print(f"   PRUEBA PRINCIPAL: rho(fraccion HAND<10 m, caudal - lluvia) = {rho:+.2f}  IC95% bloques [{l2:+.2f}, {h2:+.2f}]")
        t = np.percentile(h, [33.3, 66.7])
        for nombre, m in [("MENOS llanura (tercil inferior de la fraccion HAND<10 m)", h <= t[0]), ("intermedio", (h > t[0]) & (h <= t[1])), ("MAS llanura (tercil superior)", h > t[1])]:
            print(f"   {nombre:<56} caudal {aq[m].mean():.3f} | lluvia {ap[m].mean():.3f} | dif {dif[m].mean():+.3f} (n={int(m.sum())})")
        if l2 > 0:
            v_ = "HIPOTESIS FLUVIAL APOYADA (IC positivo y excluye 0)"
        elif h2 < 0:
            v_ = "NO apoyada: el IC es NEGATIVO (el caudal cercano predice relativamente peor donde hay mas terreno bajo)"
        else:
            v_ = "NO apoyada: el IC incluye 0"
        print(f"   VEREDICTO (regla fija): {v_}")
        print(f"   mediana de distancia a la estacion: {np.median([f['km'] for f in filas]):.1f} km; estaciones distintas: {len(set(f['est'] for f in filas))}")
    print("\nLIMITES: cercania != conexion hidrologica (no se verifica 'aguas arriba'); series mensuales; la mayoria de estaciones "
          "esta en cauces medianos y pequenos; cobertura decreciente 2019-2024; 7 bloques = IC poco fiable.")
    out = {str(R): [{k: v for k, v in f.items()} for f in fs] for R, fs in resultados.items()}
    (AQUI / "fluvial_inundaciones_caribe.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
