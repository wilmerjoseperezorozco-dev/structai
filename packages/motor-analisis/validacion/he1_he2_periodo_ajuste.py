"""HE1 y HE2 (#274) sobre los 500 pórticos diseñados en HE6 (método espectral, ya cumplen la deriva).

HE1: ¿T del modelo de pórtico desnudo > Cu·Ta en la mayoría? (gobierna el tope de A.4.2.1 en la FHE)
HE2: ¿Vt dinámico sin escalar < 0,80·Vs en la mayoría? (gobierna el ajuste A.5.4.5)
Prerregistro: validacion/PRERREGISTRO_HE1_HE3.md (fijado antes de correr este script).
Uso:  python -I validacion/he1_he2_periodo_ajuste.py   -> he1_he2_resultados.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))

import he6_qi_deriva as h6  # noqa: E402
from src.modal3d import espectral, modos  # noqa: E402
from src.sismo3d import Piso  # noqa: E402

SALIDA = AQUI / "he1_he2_resultados.json"
UMBRAL_AJUSTE = 0.80


def veredicto_mayoria(k, n):
    ic = h6.wilson(k, n)
    v = "CONFIRMADA" if ic[0] > 0.5 else ("REFUTADA" if ic[1] < 0.5 else "NO CONCLUYENTE")
    return {"n": n, "k": int(k), "proporcion": k / n if n else None, "ic95_wilson": ic, "veredicto": v}


def mediana(xs):
    xs = sorted(xs)
    n = len(xs)
    return None if n == 0 else (xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2]))


def evaluar(f, gp):
    N, L, aa, perfil = f["N"], f["L"], f["aa"], f["perfil"]
    c, dv = f["c_m"], f["hv_m"] - max(h6._redondear(L / 12), 0.30)
    alturas = tuple(h6.H * (i + 1) for i in range(N))
    fa, fv = gp.coef_fa(aa, perfil), gp.coef_fv(aa, perfil)
    sa = lambda T: gp.sa_espectro(T, aa, aa, fa, fv, 1.0)  # noqa: E731
    cuta = gp.cu(aa, fv) * gp.periodo_aproximado(alturas[-1], "porticos_concreto")
    out = {"N": N, "L": L, "aa": aa, "perfil": perfil, "c_m": c, "hv_m": f["hv_m"], "CuTa_s": cuta}
    for nombre, fcc, fcv in (("fisurada", 0.70, 0.35), ("bruta", 1.0, 1.0)):
        m, pisos, pesos = h6.edificio(N, L, c, dv, fcc, fcv)
        masas = [(w / gp.G, w / gp.G * (p.dim_x_m**2 + p.dim_y_m**2) / 12) for w, p in zip(pesos, pisos)]
        T = float(modos(m, masas).periodos.max())
        out[f"T_{nombre}_s"] = T
        out[f"T_{nombre}_sobre_CuTa"] = T / cuta
        if nombre == "fisurada":
            Tfhe = min(T, cuta)
            vs = sa(Tfhe) * sum(pesos)
            pis_m = [Piso(p.diafragma, h6.H, p.dim_x_m, p.dim_y_m, w) for p, w in zip(pisos, pesos)]
            r = espectral(m, pis_m, sa, (vs, vs), "regular", "general", True, torsion_accidental=False)
            razon = min(d["razon_Vt_Vs"] for d in r["direcciones"].values())
            out.update({"Vs_kn": vs, "Vt_sin_ajuste_kn": min(d["Vt_sin_ajuste_kn"] for d in r["direcciones"].values()),
                        "razon_Vt_Vs": razon, "factor_ajuste": max(1.0, UMBRAL_AJUSTE / razon)})
    return out


def resumen(filas):
    return {
        "HE1_principal_fisurada": {**veredicto_mayoria(sum(f["T_fisurada_sobre_CuTa"] > 1 for f in filas), len(filas)),
                                   "mediana_T_sobre_CuTa": mediana([f["T_fisurada_sobre_CuTa"] for f in filas])},
        "HE1_sensibilidad_bruta": {**veredicto_mayoria(sum(f["T_bruta_sobre_CuTa"] > 1 for f in filas), len(filas)),
                                   "mediana_T_sobre_CuTa": mediana([f["T_bruta_sobre_CuTa"] for f in filas])},
        "HE2": {**veredicto_mayoria(sum(f["razon_Vt_Vs"] < UMBRAL_AJUSTE for f in filas), len(filas)),
                "mediana_Vt_Vs": mediana([f["razon_Vt_Vs"] for f in filas]),
                "mediana_factor_ajuste": mediana([f["factor_ajuste"] for f in filas])},
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    gp = h6._geopot()
    disenos = [f for f in json.loads(h6.SALIDA.read_text(encoding="utf-8"))["espectral"]["edificios"] if f["cumple"]]
    t = time.time()
    filas = [evaluar(f, gp) for f in disenos]
    out = {"prerregistro": "validacion/PRERREGISTRO_HE1_HE3.md", "poblacion": "diseños espectrales de HE6",
           "resumen": resumen(filas),
           "por_pisos": {str(n): resumen([f for f in filas if f["N"] == n]) for n in h6.PISOS},
           "por_aa": {str(a): resumen([f for f in filas if f["aa"] == a]) for a in h6.AA},
           "por_perfil": {p: resumen([f for f in filas if f["perfil"] == p]) for p in h6.PERFILES},
           "edificios": filas, "segundos": time.time() - t}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["resumen"], ensure_ascii=False, indent=1), round(out["segundos"]), "s")


if __name__ == "__main__":
    main()
