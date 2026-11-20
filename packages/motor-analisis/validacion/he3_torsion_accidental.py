"""HE3 (#274): omitir la torsión accidental en el análisis dinámico (A.3.6.7 lo permite), ¿subestima en más del 10 %
la deriva de borde en plantas torsionalmente flexibles?

Prerregistro: validacion/PRERREGISTRO_HE1_HE3.md. Familia paramétrica (no es una muestra del inventario):
pórtico de 3×3 vanos de luz L, N pisos de 3 m; las 4 columnas interiores valen k veces las de borde (núcleo
rígido aproximado con columnas) y la losa vuela v metros por todo el perímetro (masa e inercia rotacional sobre la
planta de lado 3L + 2v, sin rigidez nueva). Inercias fisuradas 0,70/0,35. Espectro A.2.6 con Aa = Av y perfil D.
Flexibilidad torsional: Ω = T_traslación / T_torsión de los modos fundamentales (Ω < 1 ⇔ r < ls de EC8 4.2.3.2 en
plantas simétricas).
Uso:
  python -I validacion/he3_torsion_accidental.py --conteo   # solo Ω y tiempos (población); no mide derivas
  python -I validacion/he3_torsion_accidental.py            # -> he3_resultados.json
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))

import he6_qi_deriva as h6  # noqa: E402
from src.modal3d import espectral, modos  # noqa: E402
from src.portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D  # noqa: E402
from src.sismo3d import Piso  # noqa: E402

SALIDA = AQUI / "he3_resultados.json"
PISOS = (3, 6, 9, 12)
LUCES = (4.0, 5.0, 6.0, 7.0, 8.0)
K_NUCLEO = (1.0, 1.5, 2.0, 2.5, 3.0)
VOLADIZO = (0.0, 1.0, 2.0, 3.0)
AA = (0.10, 0.25)
AA_PRINCIPAL = 0.25
PERFIL = "D"
UMBRAL = 0.10
N_MIN = 30
SEMILLA = 274


def edificio(N, L, k, v):
    xs = [L * i for i in range(h6.VANOS + 1)]
    c = h6.c_inicial(N, L)
    hv = max(h6._redondear(L / 12), 0.30)
    bv = max(0.25, h6._redondear(hv / 2))
    Av, Ivf, Ivd, Jv = h6.rect(bv, hv)
    sec = {}
    for x in xs:
        for y in xs:
            interior = 0 < x < xs[-1] and 0 < y < xs[-1]
            cc = h6._redondear(k * c) if interior else c
            sec[(x, y)] = h6.rect(cc, cc)
    nodos, els, apoyos, dia, prev = [], [], {}, [], None
    for nv in range(N + 1):
        fila = {}
        for x in xs:
            for y in xs:
                fila[(x, y)] = len(nodos)
                nodos.append(Nodo3D(x, y, nv * h6.H))
        if nv == 0:
            apoyos.update({q: (True,) * 6 for q in fila.values()})
        else:
            for p, q in fila.items():
                Ac, Ic, _, Jc = sec[p]
                els.append(Elemento3D(prev[p], q, h6.EC, h6.GC, Ac, 0.70 * Ic, 0.70 * Ic, Jc))
            for y in xs:
                for a, b in zip(xs, xs[1:]):
                    els.append(Elemento3D(fila[(a, y)], fila[(b, y)], h6.EC, h6.GC, Av, 0.35 * Ivd, 0.35 * Ivf, Jv))
            for x in xs:
                for a, b in zip(xs, xs[1:]):
                    els.append(Elemento3D(fila[(x, a)], fila[(x, b)], h6.EC, h6.GC, Av, 0.35 * Ivd, 0.35 * Ivf, Jv))
            dia.append(Diafragma(f"P{nv}", tuple(fila.values()), xs[-1] / 2, xs[-1] / 2))
        prev = fila
    lado = xs[-1] + 2 * v
    w = h6.D_KPA * lado**2                              # masa sísmica = carga muerta sobre toda la losa
    pisos = [Piso(f"P{i + 1}", h6.H, lado, lado, w) for i in range(N)]
    return Portico3D(nodos, els, apoyos, dia), pisos


def omega(m, pisos):
    masas = [(p.carga_vertical_kn / 9.8, p.carga_vertical_kn / 9.8 * (p.dim_x_m**2 + p.dim_y_m**2) / 12) for p in pisos]
    md = modos(m, masas)
    J = np.array([j for _, j in masas])
    frac_rz = (J[:, None] * md.phi[2::3] ** 2).sum(axis=0)          # φ normalizada a la masa: Σ = 1 por modo
    orden = np.argsort(-md.periodos)
    t_tor = next(md.periodos[i] for i in orden if frac_rz[i] > 0.5)
    t_tra = next(md.periodos[i] for i in orden if frac_rz[i] <= 0.5)
    return float(t_tra / t_tor), float(t_tra), float(t_tor)


def deriva_borde(r):
    return max(f["deriva_punto_m"] for d in r["direcciones"].values() for f in d["pisos"])


def evaluar(N, L, k, v, aa, gp):
    m, pisos = edificio(N, L, k, v)
    om, t_tra, t_tor = omega(m, pisos)
    fa, fv = gp.coef_fa(aa, PERFIL), gp.coef_fv(aa, PERFIL)
    sa = lambda T: gp.sa_espectro(T, aa, aa, fa, fv, 1.0)  # noqa: E731
    cuta = gp.cu(aa, fv) * gp.periodo_aproximado(N * h6.H, "porticos_concreto")
    vs = sa(min(t_tra, cuta)) * sum(p.carga_vertical_kn for p in pisos)
    sin = espectral(m, pisos, sa, (vs, vs), "regular", "general", True, torsion_accidental=False)
    con = espectral(m, pisos, sa, (vs, vs), "regular", "general", True, torsion_accidental=True)
    d_sin, d_con = deriva_borde(sin), deriva_borde(con)
    return {"N": N, "L": L, "k": k, "v": v, "aa": aa, "omega": om, "T_tras_s": t_tra, "T_tors_s": t_tor,
            "flexible": om < 1.0, "deriva_borde_sin_m": d_sin, "deriva_borde_con_m": d_con,
            "subestimacion": 1.0 - d_sin / d_con, "uso_punto_con": con["uso_max_punto"]}


def bootstrap_mediana(xs, b=10000):
    rng = random.Random(SEMILLA)
    meds = sorted(sorted(rng.choices(xs, k=len(xs)))[len(xs) // 2] for _ in range(b))
    return [meds[int(0.025 * b)], meds[int(0.975 * b)]]


def resumen(filas):
    n = len(filas)
    if n == 0:
        return {"n": 0}
    k = sum(f["subestimacion"] > UMBRAL for f in filas)
    ic = h6.wilson(k, n)
    ver = ("INSUFICIENTE (n < 30)" if n < N_MIN else
           "CONFIRMADA" if ic[0] > 0.5 else "REFUTADA" if ic[1] < 0.5 else "NO CONCLUYENTE")
    sub = [f["subestimacion"] for f in filas]
    return {"n": n, "k_subestima_mas_10pct": int(k), "proporcion": k / n, "ic95_wilson": ic, "veredicto": ver,
            "subestimacion_mediana": sorted(sub)[n // 2], "ic95_mediana_bootstrap": bootstrap_mediana(sub),
            "subestimacion_min": min(sub), "subestimacion_max": max(sub)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gp = h6._geopot()
    malla = list(itertools.product(PISOS, LUCES, K_NUCLEO, VOLADIZO))
    if "--conteo" in sys.argv:
        t = time.time()
        oms = [omega(*edificio(N, L, k, v)) [0] for N, L, k, v in malla]
        print("plantas:", len(malla), "x Aa:", len(AA), "| con Ω < 1:", sum(o < 1 for o in oms), "por Aa",
              "| Ω min/mediana/max:", round(min(oms), 3), round(sorted(oms)[len(oms) // 2], 3), round(max(oms), 3),
              "|", round(time.time() - t, 1), "s")
        return
    t = time.time()
    filas = [evaluar(N, L, k, v, aa, gp) for (N, L, k, v), aa in itertools.product(malla, AA)]
    flex = [f for f in filas if f["flexible"]]
    rig = [f for f in filas if not f["flexible"]]
    out = {"prerregistro": "validacion/PRERREGISTRO_HE1_HE3.md",
           "principal_flexibles": resumen([f for f in flex if f["aa"] == AA_PRINCIPAL]),
           "sensibilidad_flexibles_aa_0_10": resumen([f for f in flex if f["aa"] != AA_PRINCIPAL]),
           "contraste_rigidas": resumen([f for f in rig if f["aa"] == AA_PRINCIPAL]),
           "flexibles_por_k": {str(k): resumen([f for f in flex if f["k"] == k and f["aa"] == AA_PRINCIPAL]) for k in K_NUCLEO},
           "flexibles_por_v": {str(v): resumen([f for f in flex if f["v"] == v and f["aa"] == AA_PRINCIPAL]) for v in VOLADIZO},
           "flexibles_por_pisos": {str(n): resumen([f for f in flex if f["N"] == n]) for n in PISOS},
           "flexibles_por_aa": {str(a): resumen([f for f in flex if f["aa"] == a]) for a in AA},
           "edificios": filas, "segundos": time.time() - t}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("principal_flexibles", "sensibilidad_flexibles_aa_0_10", "contraste_rigidas")}, ensure_ascii=False, indent=1),
          round(out["segundos"]), "s")


if __name__ == "__main__":
    main()
