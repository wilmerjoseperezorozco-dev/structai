"""HE5 (#274): con losas típicas y relación de aspecto < 3, ¿el diafragma rígido difiere menos del 5 % del
semirrígido en los cortantes de columna?

Prerregistro: validacion/PRERREGISTRO_HE5_DIAFRAGMA.md (fijado antes de correr).
Uso:
  python -I validacion/he5_diafragma.py --conteo   # malla y tiempo de un modelo; no compara cortantes
  python -I validacion/he5_diafragma.py            # -> he5_resultados.json
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))
sys.path.insert(0, str(AQUI))

from src.contrato_3d import _geopot  # noqa: E402
from src.portico3d import Caso3D, Diafragma, Elemento3D, Membrana, Nodo3D, Portico3D  # noqa: E402
from he6_qi_deriva import EC, GC, H, c_inicial, rect, _redondear  # noqa: E402
from he6_qi_deriva import wilson  # noqa: E402

SALIDA = AQUI / "he5_resultados.json"
NX = 3
NY = (3, 4, 5, 6, 7, 8, 9)            # aspecto NY/NX: 1 … 3 (3 = solo descriptivo)
LUCES = (4.0, 6.0, 8.0)
PISOS = (3, 6, 10)
ESPESORES = (0.05, 0.10, 0.15)       # torta de aligerada, maciza delgada, maciza
FACTOR_E = {"principal": 0.5, "sens_025": 0.25, "sens_100": 1.0}
NU = 0.2
UMBRAL = 0.05
AA, PERFIL = 0.25, "D"


def modelo(N, L, ny, t, rigido, fe):
    xs = [L * i for i in range(NX + 1)]
    ys = [L * j for j in range(ny + 1)]
    c = c_inicial(N, L)
    hv = max(_redondear(L / 12), 0.30)
    bv = max(0.25, _redondear(hv / 2))
    Av, Ivf, Ivd, Jv = rect(bv, hv)
    Ac, Ic, _, Jc = rect(c, c)
    nodos, els, apoyos, dia, mem, pisos = [], [], {}, [], [], []
    prev = None
    for nv in range(N + 1):
        fila = {}
        for x in xs:
            for y in ys:
                fila[(x, y)] = len(nodos)
                nodos.append(Nodo3D(x, y, nv * H))
        if nv == 0:
            apoyos.update({k: (True,) * 6 for k in fila.values()})
        else:
            for p, k in fila.items():
                els.append(("col", nv, p, Elemento3D(prev[p], k, EC, GC, Ac, 0.70 * Ic, 0.70 * Ic, Jc)))
            for y in ys:
                for a, b in zip(xs, xs[1:]):
                    els.append(("viga", nv, None, Elemento3D(fila[(a, y)], fila[(b, y)], EC, GC, Av, 0.35 * Ivd, 0.35 * Ivf, Jv)))
            for x in xs:
                for a, b in zip(ys, ys[1:]):
                    els.append(("viga", nv, None, Elemento3D(fila[(x, a)], fila[(x, b)], EC, GC, Av, 0.35 * Ivd, 0.35 * Ivf, Jv)))
            if rigido:
                dia.append(Diafragma(f"P{nv}", tuple(fila.values()), xs[-1] / 2, ys[-1] / 2))
            else:
                for i in range(NX):
                    for j in range(ny):
                        mem.append(Membrana((fila[(xs[i], ys[j])], fila[(xs[i + 1], ys[j])], fila[(xs[i + 1], ys[j + 1])],
                                             fila[(xs[i], ys[j + 1])]), fe * EC, NU, t))
            pisos.append(fila)
        prev = fila
    m = Portico3D(nodos, [e for *_, e in els], apoyos, dia, mem)
    return m, els, pisos, xs, ys


def fuerzas_piso(gp, N):
    alturas = tuple(H * (i + 1) for i in range(N))
    T = gp.cu(AA, gp.coef_fv(AA, PERFIL)) * gp.periodo_aproximado(alturas[-1], "porticos_concreto")
    return list(gp.distribuir_fuerzas(1000.0, tuple(1.0 for _ in range(N)), alturas, T))


def cortantes(m, els, pisos, xs, ys, fs, direccion, rigido):
    d = 0 if direccion == "x" else 1
    if rigido:
        caso = Caso3D(direccion, maestros={f"P{i + 1}": ((F, 0, 0) if d == 0 else (0, F, 0)) for i, F in enumerate(fs)})
    else:
        lx, ly = xs[-1], ys[-1]
        nod = {}
        for i, F in enumerate(fs):
            for (x, y), k in pisos[i].items():
                tx = (0.5 if x in (0, lx) else 1.0) / (len(xs) - 1)
                ty = (0.5 if y in (0, ly) else 1.0) / (len(ys) - 1)
                v = [0.0] * 6
                v[d] = F * tx * ty
                nod[k] = tuple(v)
        caso = Caso3D(direccion, nodales=nod)
    r = m.resolver(caso)
    comp = 1 if d == 0 else 2        # columna: y_local = X global, z_local = Y global
    out = {}
    for idx, (tipo, nv, p, _) in enumerate(els):
        if tipo == "col":
            out[(nv, p)] = float(r.f_extremos[idx][comp])
    return out


def error(vr, vs):
    peor = 0.0
    for nv in {k[0] for k in vr}:
        ks = [k for k in vr if k[0] == nv]
        ref = max(abs(vr[k]) for k in ks)
        peor = max(peor, max(abs(vs[k] - vr[k]) for k in ks) / ref)
    return peor


def evaluar(gp, N, L, ny, t, fe):
    fs = fuerzas_piso(gp, N)
    mr = modelo(N, L, ny, t, True, fe)
    ms = modelo(N, L, ny, t, False, fe)
    e = {d: error(cortantes(*mr, fs, d, True), cortantes(*ms, fs, d, False)) for d in ("x", "y")}
    return {"N": N, "L": L, "ny": ny, "aspecto": ny / NX, "t": t, "error_x": e["x"], "error_y": e["y"],
            "error_max": max(e.values())}


def resumen(filas):
    k = sum(f["error_max"] >= UMBRAL for f in filas)
    ic = wilson(k, len(filas))
    ver = "CONFIRMADA" if ic[1] < 0.10 else ("REFUTADA" if ic[0] > 0.10 else "NO CONCLUYENTE")
    errs = sorted(f["error_max"] for f in filas)
    return {"n": len(filas), "n_error_mayor_igual_5pct": int(k), "proporcion": k / len(filas), "ic95_wilson": ic,
            "veredicto": ver, "error_mediana": errs[len(errs) // 2], "error_max": errs[-1]}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gp = _geopot()
    malla = list(itertools.product(PISOS, LUCES, NY, ESPESORES))
    if "--conteo" in sys.argv:
        t0 = time.time()
        m, *_ = modelo(10, 8.0, 9, 0.05, False, 0.5)
        print("edificios:", len(malla), "| nodos del mayor:", len(m.nodos), "| tiempo de un modelo:", round(time.time() - t0, 1), "s")
        return
    out = {"prerregistro": "validacion/PRERREGISTRO_HE5_DIAFRAGMA.md"}
    for nombre, fe in FACTOR_E.items():
        t0 = time.time()
        filas = [evaluar(gp, *p, fe) for p in malla]
        prin = [f for f in filas if f["aspecto"] < 3]
        out[nombre] = {"factor_E_losa": fe, "resumen_aspecto_menor_3": resumen(prin),
                       "resumen_aspecto_3": resumen([f for f in filas if f["aspecto"] == 3]),
                       "por_espesor": {str(t): resumen([f for f in prin if f["t"] == t]) for t in ESPESORES},
                       "por_aspecto": {f"{a / NX:.2f}": resumen([f for f in filas if f["ny"] == a]) for a in NY},
                       "por_pisos": {str(n): resumen([f for f in prin if f["N"] == n]) for n in PISOS},
                       "edificios": filas}
        print(nombre, round(time.time() - t0), "s", json.dumps(out[nombre]["resumen_aspecto_menor_3"], ensure_ascii=False), flush=True)
        SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
