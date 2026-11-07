"""El "cuando": precipitacion mensual (CHIRPS v3.0) y reportes de inundacion (UNGRD) por
municipio-mes en el Caribe (issue #95). Diseno en PROTOCOLO_ANALISIS.md seccion 10.
Cada municipio se compara consigo mismo (anomalia z propia), lo que neutraliza buena parte del
sesgo de capacidad de reportar entre municipios.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cruzar_relieve_ungrd_caribe as base  # noqa: E402  (configura la salida UTF-8 y trae utilidades)
import _datos_caribe as dc  # noqa: E402

MIN_POS, MIN_NEG = 3, 12
N_BOOT = 5000
RNG = np.random.default_rng(20261106)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def ic_bloques_media(vals: np.ndarray, bloques: np.ndarray) -> tuple[float, float]:
    et = np.unique(bloques)
    bs = []
    for _ in range(N_BOOT):
        idx = np.concatenate([np.where(bloques == b)[0] for b in RNG.choice(et, len(et), replace=True)])
        bs.append(vals[idx].mean())
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main() -> None:
    ch = json.loads((AQUI / "chirps_mensual_caribe.json").read_text(encoding="utf-8"))
    meses = ch["meses"]
    pos_mes = {m: i for i, m in enumerate(meses)}
    cods = list(ch["municipios"])
    hand = {m["codigo"]: m for m in json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"] if "frac_hand_lt10_5" in m}
    ung = dc.ungrd(cods)
    inund = defaultdict(set)
    reportes = defaultdict(set)
    for r in ung:
        k = str(r["fecha"])[:7]
        if k in pos_mes:
            reportes[r["codigo_municipio"]].add(pos_mes[k])
            if r["evento"] in dc.EVENTOS_INUNDACION:
                inund[r["codigo_municipio"]].add(pos_mes[k])

    print(f"Panel: {len(cods)} municipios x {len(meses)} meses = {len(cods) * len(meses)} municipio-mes")
    tot_pos = sum(len(v) for v in inund.values())
    print(f"Municipio-mes con inundacion reportada: {tot_pos} ({100 * tot_pos / (len(cods) * len(meses)):.1f} %)")

    # ---- Regional: lluvia media mensual vs numero de municipios con inundacion ese mes
    P = np.array([ch["municipios"][c]["precip_mm"] for c in cods], float)
    regional = P.mean(0)
    n_mun = np.array([sum(1 for c in cods if i in inund[c]) for i in range(len(meses))], float)
    rho_r, _ = spearmanr(regional, n_mun)
    print(f"\n== Regional (72 meses): rho(lluvia media del Caribe, n municipios con inundacion) = {rho_r:.2f}")
    top = np.argsort(-n_mun)[:5]
    print("   meses con mas municipios con inundacion:", [(meses[i], int(n_mun[i]), f"{regional[i]:.0f} mm") for i in top])

    # ---- Por municipio: AUC de la anomalia de lluvia
    filas = []
    for j, c in enumerate(cods):
        z = (P[j] - P[j].mean()) / P[j].std(ddof=1) if P[j].std(ddof=1) > 0 else np.zeros(len(meses))
        pos = np.array(sorted(inund[c]), int)
        neg = np.array([i for i in range(len(meses)) if i not in inund[c]], int)
        if len(pos) >= MIN_POS and len(neg) >= MIN_NEG:
            filas.append((c, ch["municipios"][c]["depto"], auc(z[pos], z[neg]), len(pos)))
    a = np.array([f[2] for f in filas])
    bl = np.array([f[1] for f in filas])
    lo, hi = ic_bloques_media(a, bl)
    print(f"\n== AUC por municipio de la anomalia de lluvia (n={len(filas)} municipios elegibles de {len(cods)}) ==")
    print(f"   AUC medio {a.mean():.3f}  IC95% bloques [{lo:.3f}, {hi:.3f}] | mediana {np.median(a):.3f} | "
          f"fraccion con AUC > 0.5: {100 * (a > 0.5).mean():.0f} %")
    for d in sorted(set(bl)):
        m = bl == d
        print(f"   {d} {dc.DEPTOS[d]:<11} AUC medio {a[m].mean():.3f}  (n={int(m.sum())})")
    veredicto1 = ("la lluvia discrimina meses con inundacion (IC excluye 0,5)" if lo > 0.5 or hi < 0.5
                  else "el IC del AUC medio incluye 0,5: NO hay evidencia de que la lluvia mensual discrimine")
    print(f"   VEREDICTO (regla fija): {veredicto1}")

    # ---- Moderador HAND
    kk = [(f[2], hand[f[0]]["frac_hand_lt10_5"], f[1]) for f in filas if f[0] in hand]
    av, hv, bv = np.array([k[0] for k in kk]), np.array([k[1] for k in kk]), np.array([k[2] for k in kk])
    rho_m = spearmanr(hv, av)[0]
    et = np.unique(bv)
    bs = []
    for _ in range(N_BOOT):
        idx = np.concatenate([np.where(bv == b)[0] for b in RNG.choice(et, len(et), replace=True)])
        if np.ptp(hv[idx]) > 0 and np.ptp(av[idx]) > 0:
            bs.append(spearmanr(hv[idx], av[idx])[0])
    lom, him = np.percentile(bs, [2.5, 97.5])
    print(f"\n== Moderacion por HAND (n={len(kk)}): rho(fraccion HAND<10 m, AUC municipal) = {rho_m:.2f}  IC95% bloques [{lom:.2f}, {him:.2f}]")
    veredicto2 = ("HAND modera: el IC excluye 0" if lom > 0 or him < 0 else "el IC incluye 0: NO hay evidencia de que HAND module el efecto de la lluvia")
    print(f"   VEREDICTO (regla fija): {veredicto2}")
    tercil = np.percentile(hv, [33.3, 66.7])
    for nombre, m in [("HAND bajo (tercil inferior de la fraccion)", hv <= tercil[0]), ("intermedio", (hv > tercil[0]) & (hv <= tercil[1])),
                      ("HAND alto en fraccion (tercil superior)", hv > tercil[1])]:
        print(f"   {nombre:<44} AUC medio {av[m].mean():.3f} (n={int(m.sum())})")
    print("\nLIMITES: CHIRPS a ~5 km (municipios chicos = 1-3 pixeles); lluvia mensual no capta crecientes de horas; "
          "UNGRD mide reportes; el efecto de la lluvia es casi previsible: lo informativo es su tamano y la moderacion por HAND (exploratoria).")
    (AQUI / "cuando_inundaciones_caribe.json").write_text(json.dumps({
        "n_municipios_elegibles": len(filas), "auc_medio": float(a.mean()), "ic_bloques": [lo, hi], "veredicto_lluvia": veredicto1,
        "moderacion_hand": {"rho": float(rho_m), "ic_bloques": [float(lom), float(him)], "veredicto": veredicto2},
        "regional": {"rho_lluvia_vs_n_municipios": float(rho_r)}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
