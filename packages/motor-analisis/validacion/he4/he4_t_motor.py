"""HE4 (#274): T_motor de un pórtico paramétrico equivalente, para compararlo con periodos medidos.

Prerregistro: validacion/he4/PRERREGISTRO_HE4.md. Equivalente fijado:
- planta de 3×3 vanos de L = 6 m, N = máx(1, round(h/3)) pisos de h/N m;
- columnas c0 por carga axial (igual que HE6) y vigas h = máx(L/12; 0,30), b = máx(0,25; h/2);
- inercias BRUTAS (Ig) para igualar la amplitud mínima de la vibración ambiental (sin fisuración);
- masa D = 7,0 kN/m² (igual que HE6).
Uso:
  python -I validacion/he4/he4_t_motor.py --tabla              # T_motor y Ta para N = 1..20, sin datos medidos
  python -I validacion/he4/he4_t_motor.py --csv datos.csv      # razones T_medido/T_motor (solo pórticos)
"""
from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
sys.path.insert(0, str(AQUI.parents[2] / "contrato-motor"))
sys.path.insert(0, str(AQUI.parent))

from src.contrato_3d import _geopot  # noqa: E402
from src.modal3d import modos  # noqa: E402
from src.portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D  # noqa: E402
from he6_qi_deriva import D_KPA, EC, GC, L_KPA, FC_MPA, C_MIN, _redondear, rect  # noqa: E402

VANOS, LUZ = 3, 6.0
UMBRAL = 0.8
N_MIN = 10
B_BOOT = 10_000


def t_motor(h_total: float) -> tuple[float, int]:
    N = max(1, round(h_total / 3.0))
    hp = h_total / N
    pu = N * (1.2 * D_KPA + 1.6 * L_KPA) * LUZ**2
    c = max(C_MIN, _redondear(math.sqrt(pu / (0.40 * FC_MPA * 1000.0))))
    hv = max(_redondear(LUZ / 12), 0.30)
    bv = max(0.25, _redondear(hv / 2))
    Av, Ivf, Ivd, Jv = rect(bv, hv)
    Ac, Ic, _, Jc = rect(c, c)
    xs = [LUZ * i for i in range(VANOS + 1)]
    nodos, els, apoyos, dia, prev = [], [], {}, [], None
    for nv in range(N + 1):
        fila = {}
        for x in xs:
            for y in xs:
                fila[(x, y)] = len(nodos)
                nodos.append(Nodo3D(x, y, nv * hp))
        if nv == 0:
            apoyos.update({k: (True,) * 6 for k in fila.values()})
        else:
            for p, k in fila.items():
                els.append(Elemento3D(prev[p], k, EC, GC, Ac, Ic, Ic, Jc))
            for a, b in zip(xs, xs[1:]):
                for y in xs:
                    els.append(Elemento3D(fila[(a, y)], fila[(b, y)], EC, GC, Av, Ivd, Ivf, Jv))
                    els.append(Elemento3D(fila[(y, a)], fila[(y, b)], EC, GC, Av, Ivd, Ivf, Jv))
            dia.append(Diafragma(f"P{nv}", tuple(fila.values()), xs[-1] / 2, xs[-1] / 2))
        prev = fila
    lado = xs[-1]
    m = D_KPA * lado**2 / 9.80665
    md = modos(Portico3D(nodos, els, apoyos, dia), [(m, m * 2 * lado**2 / 12)] * N)
    return float(md.periodos.max()), N


def bootstrap_mediana(v, b=B_BOOT, semilla=274):
    import random
    rng = random.Random(semilla)
    meds = sorted(statistics.median(rng.choices(v, k=len(v))) for _ in range(b))
    return [meds[int(0.025 * b)], meds[int(0.975 * b) - 1]]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gp = _geopot()
    if "--tabla" in sys.argv:
        print("N  h(m)  T_motor_Ig(s)  Ta_porticos(s)  T_motor/Ta")
        for N in range(1, 21):
            T, _ = t_motor(3.0 * N)
            ta = gp.periodo_aproximado(3.0 * N, "porticos_concreto")
            print(f"{N:2d} {3*N:5.1f} {T:10.3f} {ta:12.3f} {T/ta:10.2f}")
        return
    ruta = Path(sys.argv[sys.argv.index("--csv") + 1])
    filas = [f for f in csv.DictReader(ruta.open(encoding="utf-8")) if f["sistema"].startswith("porticos")]
    razones = []
    for f in filas:
        e, s = float(f["T_efdd_s"]), float(f["T_ssi_s"] or f["T_efdd_s"])
        if abs(e - s) / min(e, s) > 0.10:
            continue
        T, _ = t_motor(float(f["altura_m"]))
        razones.append((e + s) / 2 / T)
    n = len(razones)
    if n < N_MIN:
        print(f"n = {n} pórticos válidos < {N_MIN}: HE4 principal NO se corre (prerregistro).")
        return
    med = statistics.median(razones)
    ic = bootstrap_mediana(razones)
    ver = "CONFIRMADA" if ic[1] < UMBRAL else ("REFUTADA" if ic[0] >= UMBRAL else "NO CONCLUYENTE")
    print({"n": n, "mediana": med, "ic95": ic, "veredicto": ver})


if __name__ == "__main__":
    main()
