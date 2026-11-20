"""HE6 (#274): si un pórtico de concreto cumple la deriva del 1 % (A.6.4), ¿es raro que Qi > 0,10 (A.6.2.3)?

Prerregistro: validacion/PRERREGISTRO_HE6_QI_DERIVA.md (fijado antes de calcular Qi).
Edificios paramétricos (no es una muestra del inventario real): pórticos de concreto de 3×3 vanos cuadrados,
N pisos de 3 m, luz L, sitio (Aa = Av, perfil). Prediseño: vigas h0 = máx(L/12; 0,30), b = máx(0,25; h/2);
columnas cuadradas iguales en todo el edificio, c0 por carga axial. Si no cumple la deriva, en cada paso crecen
a la vez la columna y la altura de viga 0,05 m (tope 1,20 m cada una). Inercias fisuradas C.10.10.4.1 (columnas 0,70·Ig, vigas 0,35·Ig) → deriva × 0,7 (A.6.4.1.1).
Uso:
  python -I validacion/he6_qi_deriva.py --conteo   # malla y tiempos; no calcula Qi
  python -I validacion/he6_qi_deriva.py            # análisis -> he6_resultados.json
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

from src.contrato_3d import _geopot  # noqa: E402
from src.modal3d import espectral, masas_piso, modos  # noqa: E402
from src.portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D  # noqa: E402
from src.sismo3d import Piso, analizar_fhe  # noqa: E402

SALIDA = AQUI / "he6_resultados.json"
PISOS = range(3, 13)
LUCES = (4.0, 5.0, 6.0, 7.0, 8.0)
AA = (0.10, 0.15, 0.20, 0.25, 0.30)
PERFILES = ("C", "D")
VANOS, H = 3, 3.0
FC_MPA = 28.0
EC = 4700 * math.sqrt(FC_MPA) * 1000.0          # kN/m², C.8.5.1
GC = EC / (2 * (1 + 0.2))
D_KPA, L_KPA = 7.0, 1.8                         # carga muerta total (losa, acabados, muros, pórtico) y viva residencial
C_MIN, C_MAX, PASO = 0.30, 1.20, 0.05
Q_UMBRAL = 0.10


def _redondear(x):
    return math.ceil(x / PASO - 1e-9) * PASO


def rect(b, h):
    a, c = max(b, h), min(b, h)
    J = a * c**3 * (1 / 3 - 0.21 * c / a * (1 - c**4 / (12 * a**4)))
    return b * h, b * h**3 / 12, h * b**3 / 12, J


def edificio(N, L, c, dv=0.0, fc_col=0.70, fc_vig=0.35):
    xs = [L * i for i in range(VANOS + 1)]
    hv = max(_redondear(L / 12), 0.30) + dv
    bv = max(0.25, _redondear(hv / 2))
    Av, Iv_fuerte, Iv_debil, Jv = rect(bv, hv)
    Ac, Ic, _, Jc = rect(c, c)
    nodos, els, apoyos, dia, prev = [], [], {}, [], None
    for nv in range(N + 1):
        fila = {}
        for x in xs:
            for y in xs:
                fila[(x, y)] = len(nodos)
                nodos.append(Nodo3D(x, y, nv * H))
        if nv == 0:
            apoyos.update({k: (True,) * 6 for k in fila.values()})
        else:
            for p, k in fila.items():
                els.append(Elemento3D(prev[p], k, EC, GC, Ac, fc_col * Ic, fc_col * Ic, Jc))
            for y in xs:
                for a, b in zip(xs, xs[1:]):
                    els.append(Elemento3D(fila[(a, y)], fila[(b, y)], EC, GC, Av, fc_vig * Iv_debil, fc_vig * Iv_fuerte, Jv))
            for x in xs:
                for a, b in zip(xs, xs[1:]):
                    els.append(Elemento3D(fila[(x, a)], fila[(x, b)], EC, GC, Av, fc_vig * Iv_debil, fc_vig * Iv_fuerte, Jv))
            dia.append(Diafragma(f"P{nv}", tuple(fila.values()), xs[-1] / 2, xs[-1] / 2))
        prev = fila
    lado = xs[-1]
    area = lado**2
    pisos = [Piso(f"P{i + 1}", H, lado, lado, (D_KPA + L_KPA) * area) for i in range(N)]
    pesos = tuple(D_KPA * area for _ in range(N))
    return Portico3D(nodos, els, apoyos, dia), pisos, pesos


def c_inicial(N, L):
    pu = N * (1.2 * D_KPA + 1.6 * L_KPA) * L**2          # columna interior, kN
    return max(C_MIN, _redondear(math.sqrt(pu / (0.40 * FC_MPA * 1000.0))))


def evaluar(N, L, aa, perfil, gp, metodo):
    fa, fv = gp.coef_fa(aa, perfil), gp.coef_fv(aa, perfil)
    sa = lambda T: gp.sa_espectro(T, aa, aa, fa, fv, 1.0)  # noqa: E731
    c, dv, pasos = c_inicial(N, L), 0.0, 0
    hv0 = max(_redondear(L / 12), 0.30)
    while c <= C_MAX + 1e-9 and hv0 + dv <= C_MAX + 1e-9:
        m, pisos, pesos = edificio(N, L, c, dv)
        md = modos(m, [(w / gp.G, w / gp.G * (p.dim_x_m**2 + p.dim_y_m**2) / 12) for w, p in zip(pesos, pisos)])
        alturas = tuple(H * (i + 1) for i in range(N))
        cuta = gp.cu(aa, fv) * gp.periodo_aproximado(alturas[-1], "porticos_concreto")
        T = min(float(md.periodos.max()), cuta)
        vs = sa(T) * sum(pesos)
        if metodo == "espectral":
            # masas sísmicas = D; carga vertical para Pi = D + L: se pasa la masa por la carga de los pisos
            pis_m = [Piso(p.diafragma, H, p.dim_x_m, p.dim_y_m, w) for p, w in zip(pisos, pesos)]
            r = espectral(m, pis_m, sa, (vs, vs), "regular", "general", True, torsion_accidental=True)
            uso = r["uso_max_cm"]
            Pfac = (D_KPA + L_KPA) / D_KPA                 # Qi con P = D + L (A.6.0) y Δ, V de la masa D
            qi = Pfac * r["Qi_max"]
        else:
            fs = gp.distribuir_fuerzas(vs, pesos, alturas, T)
            r = analizar_fhe(m, pisos, list(fs), list(fs), "general", True)
            uso, qi = r["uso_max_limite"], r["Qi_max"]
        if uso <= 1.0:
            return {"N": N, "L": L, "aa": aa, "perfil": perfil, "metodo": metodo, "c_m": round(c, 2),
                    "hv_m": round(hv0 + dv, 2), "pasos": pasos, "T_modelo_s":
                    float(md.periodos.max()), "CuTa_s": cuta, "uso_deriva": uso, "Qi_max": qi, "cumple": True}
        c += PASO
        dv += PASO
        pasos += 1
    return {"N": N, "L": L, "aa": aa, "perfil": perfil, "metodo": metodo, "c_m": None, "cumple": False}


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan")] * 2
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return [c - h, c + h]


def resumen(filas):
    ok = [f for f in filas if f["cumple"]]
    k = sum(f["Qi_max"] > Q_UMBRAL for f in ok)
    ic = wilson(k, len(ok))
    ver = "CONFIRMADA" if ic[1] < Q_UMBRAL else ("REFUTADA" if ic[0] > Q_UMBRAL else "NO CONCLUYENTE")
    return {"n_edificios": len(filas), "n_cumplen": len(ok), "n_sin_diseno": len(filas) - len(ok),
            "n_qi_mayor_0_10": int(k), "proporcion": k / len(ok) if ok else None, "ic95_wilson": ic, "veredicto": ver,
            "qi_max_mediana": sorted(f["Qi_max"] for f in ok)[len(ok) // 2] if ok else None}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gp = _geopot()
    malla = list(itertools.product(PISOS, LUCES, AA, PERFILES))
    if "--conteo" in sys.argv:
        t = time.time()
        m, pisos, _ = edificio(12, 8.0, 0.6)
        print("edificios:", len(malla), "| nodos del mayor:", len(m.nodos), "| elementos:", len(m.elementos),
              "| tiempo de un modelo de 12 pisos:", round(time.time() - t, 2), "s")
        print("columna inicial (N=3, L=4):", c_inicial(3, 4.0), "| (N=12, L=8):", c_inicial(12, 8.0))
        return
    out = {"prerregistro": "validacion/PRERREGISTRO_HE6_QI_DERIVA.md"}
    for metodo in ("espectral", "fhe"):
        filas = [evaluar(N, L, aa, pf, gp, metodo) for N, L, aa, pf in malla]
        out[metodo] = {"resumen": resumen(filas),
                       "por_aa": {str(a): resumen([f for f in filas if f["aa"] == a]) for a in AA},
                       "por_pisos": {str(n): resumen([f for f in filas if f["N"] == n]) for n in PISOS},
                       "edificios": filas}
        print(metodo, json.dumps(out[metodo]["resumen"], ensure_ascii=False))
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
