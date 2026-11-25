"""#328 fase 1: motor-licuacion frente a los 210 casos SPT de Cetin et al. (2018), Data in Brief 20:544–548, CC BY.

Ver docs/memoria_calculo/PRERREGISTRO_328_LICUACION_CETIN2018.md (fijado antes de correr).

Brazos, con las mismas entradas del archivo (profundidad, σv, σ'v, amax, Mw, (N1)60 y FC; psf → kPa):
  M0  motor-licuacion tal cual (Youd et al. 2001 sin Kσ, CRR de Rauch, MSF de Idriss, finos de Idriss y Seed);
  M1  Boulanger e Idriss (2014), determinista: rd(z, M), MSF(N), Kσ, ΔN por finos, CRR7.5,1;
  M1p Boulanger e Idriss (2014), probabilístico: PL = Φ(−(f(N) − 2,67 − ln CSR7.5,1)/0,13);
  M3  regresión logística sobre (N1)60cs y ln CSR7.5,1 de M1, validación dejando un sismo fuera.

El archivo NO se versiona (licencia CC BY, cita en el informe). Uso:
  python -I packages/motor-licuacion/validacion/medir_cetin2018.py <ruta>/mmc2.xls <salida_dir>
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import spt as m0  # noqa: E402

PSF_KPA = 0.0478803
PA_KPA = 101.325
SEMILLA = 3280
N_BOOT = 2000


# ---------------------------------------------------------------------------------------------- Boulanger e Idriss 2014
def bi_rd(z: float, mw: float) -> float:
    a = -1.012 - 1.126 * math.sin(z / 11.73 + 5.133)
    b = 0.106 + 0.118 * math.sin(z / 11.28 + 5.142)
    return math.exp(a + b * mw)


def bi_dn(fc: float) -> float:
    return math.exp(1.63 + 9.7 / (fc + 0.01) - (15.7 / (fc + 0.01)) ** 2)


def bi_f(n: float) -> float:
    return n / 14.1 + (n / 126.0) ** 2 - (n / 23.6) ** 3 + (n / 25.4) ** 4


def bi(c: dict) -> dict:
    n = c["n160"] + bi_dn(c["fc"])
    csr = 0.65 * c["amax"] * c["sv"] / c["sve"] * bi_rd(c["z"], c["mw"])
    msf_max = min(1.09 + (n / 31.5) ** 2, 2.2)
    msf = 1.0 + (msf_max - 1.0) * (8.64 * math.exp(-c["mw"] / 4.0) - 1.325)
    c_s = min(1.0 / (18.9 - 2.55 * math.sqrt(n)), 0.3) if n < (18.9 / 2.55) ** 2 else 0.3
    k_s = min(1.0 - c_s * math.log(c["sve"] / PA_KPA), 1.1)
    csr75 = csr / (msf * k_s)
    crr = math.exp(bi_f(n) - 2.8)
    pl = float(norm.cdf(-(bi_f(n) - 2.67 - math.log(csr75)) / 0.13))
    return {"n160cs_bi": n, "csr75_bi": csr75, "fs_m1": crr / csr75, "pl_m1p": pl}


# ---------------------------------------------------------------------------------------------- datos
def _evento(s: str) -> str:
    """Clave de sismo para agrupar: año + nombre sin magnitud ni signos (une variantes de escritura; declarado)."""
    s = re.sub(r"\s*M[LWSw]?s?\s*=.*$", "", s.strip())
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    return s


def leer(ruta: str) -> list[dict]:
    import xlrd  # solo para leer el .xls; las pruebas no lo necesitan
    hoja = xlrd.open_workbook(ruta).sheet_by_index(0)
    col = {str(c.value).strip(): i for i, c in enumerate(hoja.row(0))}
    casos = []
    for r in range(1, hoja.nrows):
        v = lambda k: hoja.cell_value(r, col[k])  # noqa: E731
        if v("Case Number") in ("", None):
            continue
        casos.append({"id": int(v("Case Number")), "sismo": str(v("Earthquake")).strip(), "evento": _evento(str(v("Earthquake"))),
                      "sitio": str(v("Site")).strip(), "obs": str(v("Liquefied?")).strip(), "clase": str(v("Data Class")).strip(),
                      "z": float(v("Critical Depth (m)")), "sv": float(v("sv (psf)")) * PSF_KPA,
                      "sve": float(v("sv' (psf)")) * PSF_KPA, "amax": float(v("a max (g)")), "mw": float(v("Magnitude for KMw")),
                      "n160": float(v("(N1) 60")), "fc": float(v("FC %"))})
    return casos


# ---------------------------------------------------------------------------------------------- brazos
def evaluar(c: dict) -> dict:
    out = dict(c)
    try:
        n_cs, borde = m0.corregir_finos(n1_60=c["n160"], finos_pct=c["fc"])
        out |= {"n160cs_m0": n_cs, "borde_finos_m0": borde,
                "fs_m0": m0.factor_seguridad_estrato(n1_60cs=n_cs, amax_g=c["amax"], sigma_v_kpa=c["sv"],
                                                     sigma_v_efectivo_kpa=c["sve"], z_m=c["z"], mw=c["mw"]),
                "error_m0": ""}
    except ValueError as e:
        out |= {"fs_m0": math.nan, "error_m0": str(e)[:120]}
    out |= bi(c)
    return out


def logistica(x: np.ndarray, y: np.ndarray, l2: float = 1e-3, it: int = 100) -> np.ndarray:
    X = np.column_stack([np.ones(len(x)), x])
    w = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (p - y) + l2 * w
        H = X.T @ (X * (p * (1 - p))[:, None]) + l2 * np.eye(len(w))
        w -= np.linalg.solve(H, g)
    return w


def m3_loeo(filas: list[dict]) -> None:
    x = np.array([[f["n160cs_bi"], math.log(f["csr75_bi"])] for f in filas])
    y = np.array([f["y"] for f in filas], dtype=float)
    ev = np.array([f["evento"] for f in filas])
    for e in np.unique(ev):
        tr = ev != e
        w = logistica(x[tr], y[tr])
        for i in np.where(~tr)[0]:
            filas[i]["pl_m3"] = float(1 / (1 + math.exp(-(w[0] + w[1:] @ x[i]))))


# ---------------------------------------------------------------------------------------------- métricas
def _met_det(filas, clave):
    ok = [f for f in filas if not math.isnan(f[clave])]
    tp = sum(f["y"] == 1 and f[clave] < 1 for f in ok)
    fn = sum(f["y"] == 1 and f[clave] >= 1 for f in ok)
    tn = sum(f["y"] == 0 and f[clave] >= 1 for f in ok)
    fp = sum(f["y"] == 0 and f[clave] < 1 for f in ok)
    sens = tp / max(1, tp + fn)
    esp = tn / max(1, tn + fp)
    return {"n": len(ok), "tp": tp, "fn": fn, "tn": tn, "fp": fp, "sens": sens, "esp": esp, "bal": (sens + esp) / 2}


def _met_prob(filas, clave):
    p = np.clip(np.array([f[clave] for f in filas]), 1e-6, 1 - 1e-6)
    y = np.array([f["y"] for f in filas])
    return {"logloss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), "brier": float(np.mean((p - y) ** 2)),
            "p_media": float(p.mean()), "y_media": float(y.mean())}


def _boot(filas, fn):
    """IC95 con remuestreo de sismos completos (bootstrap por conglomerado)."""
    rng = np.random.default_rng(SEMILLA)
    por = {}
    for f in filas:
        por.setdefault(f["evento"], []).append(f)
    evs = list(por)
    vals = []
    for _ in range(N_BOOT):
        m = [f for e in rng.choice(evs, len(evs)) for f in por[e]]
        vals.append(fn(m))
    return [float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))]


def calibracion(filas, clave, bordes=(0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001)):
    out = []
    for a, b in zip(bordes[:-1], bordes[1:]):
        s = [f for f in filas if a <= f[clave] < b]
        if s:
            out.append({"bin": [a, min(b, 1.0)], "n": len(s), "p_media": float(np.mean([f[clave] for f in s])),
                        "obs": float(np.mean([f["y"] for f in s]))})
    return out


def estratos(filas):
    def grupo(nombre, pred):
        s = [f for f in filas if pred(f)]
        return {nombre: {"M0": _met_det(s, "fs_m0"), "M1": _met_det(s, "fs_m1"), "n": len(s)}}
    out = {}
    for nombre, pred in (("FC<=5", lambda f: f["fc"] <= 5), ("5<FC<35", lambda f: 5 < f["fc"] < 35), ("FC>=35", lambda f: f["fc"] >= 35),
                         ("N160cs_bi<15", lambda f: f["n160cs_bi"] < 15), ("15<=N160cs_bi<30", lambda f: 15 <= f["n160cs_bi"] < 30),
                         ("N160cs_bi>=30", lambda f: f["n160cs_bi"] >= 30), ("z>12m", lambda f: f["z"] > 12),
                         ("sve>150kPa", lambda f: f["sve"] > 150), ("Mw<7", lambda f: f["mw"] < 7), ("clase A", lambda f: f["clase"] == "A")):
        out |= grupo(nombre, pred)
    return out


def main(ruta_xls: str, salida: str):
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(salida)
    out.mkdir(parents=True, exist_ok=True)
    casos = [evaluar(c) for c in leer(ruta_xls)]
    for c in casos:
        c["y"] = 1 if c["obs"] == "Yes" else (0 if c["obs"] == "No" else None)
    principal = [c for c in casos if c["y"] is not None and c["clase"] in ("A", "B")]
    m3_loeo(principal)
    res = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_328_LICUACION_CETIN2018.md",
           "n_total": len(casos), "n_principal": len(principal), "n_sismos": len({c["evento"] for c in principal}),
           "excluidos": [(c["id"], c["obs"], c["clase"]) for c in casos if c not in principal],
           "errores_m0": [(c["id"], c["error_m0"]) for c in principal if c.get("error_m0")]}
    for k, clave in (("M0", "fs_m0"), ("M1", "fs_m1")):
        m = _met_det(principal, clave)
        m |= {f"ic95_{x}": _boot(principal, lambda s, x=x, clave=clave: _met_det(s, clave)[x]) for x in ("sens", "esp", "bal")}
        res[k] = m
    res["M1_menos_M0"] = {x: res["M1"][x] - res["M0"][x] for x in ("sens", "esp", "bal")} | {
        f"ic95_{x}": _boot(principal, lambda s, x=x: _met_det(s, "fs_m1")[x] - _met_det(s, "fs_m0")[x]) for x in ("sens", "esp", "bal")}
    for k, clave in (("M1p", "pl_m1p"), ("M3", "pl_m3")):
        res[k] = _met_prob(principal, clave) | {"calibracion": calibracion(principal, clave)}
    res["M3_menos_M1p_logloss"] = {"dif": res["M3"]["logloss"] - res["M1p"]["logloss"],
                                   "ic95": _boot(principal, lambda s: _met_prob(s, "pl_m3")["logloss"] - _met_prob(s, "pl_m1p")["logloss"])}
    res["estratos"] = estratos(principal)
    res["sensibilidad_todos_los_casos"] = {k: _met_det([c for c in casos if c["y"] is not None], v)
                                           for k, v in (("M0", "fs_m0"), ("M1", "fs_m1"))}
    (out / "resultados_328_cetin2018.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    campos = ["id", "evento", "sitio", "obs", "clase", "z", "sv", "sve", "amax", "mw", "n160", "fc", "n160cs_m0", "fs_m0", "error_m0",
              "n160cs_bi", "csr75_bi", "fs_m1", "pl_m1p", "pl_m3"]
    with (out / "casos_328.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(casos)
    print(json.dumps({k: res[k] for k in ("n_principal", "n_sismos", "M0", "M1", "M1_menos_M0", "M3_menos_M1p_logloss")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
