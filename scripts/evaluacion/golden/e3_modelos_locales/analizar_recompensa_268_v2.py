"""Análisis prerregistrado de la validación v2 de la recompensa (#268 v2). Se escribe ANTES de que exista una etiqueta.

Ejes humanos: A (dato técnico 2/1/0/A), B (¿hace algo no pedido? Sí/No), C (¿número que no cuadra? Sí/No/No sé).

Hipótesis y reglas (fijas):
  H1  Spearman(binaria, A) >= 0,6 con límite inferior del IC95 > 0,4.
  H2  rica_tecnica sustituye a la binaria solo si Spearman(rica_tecnica, A) - Spearman(binaria, A) tiene IC95 > 0.
  H3  Detector de inyección frente a B: sensibilidad >= 0,9 y precisión >= 0,8 (se reportan IC de Wilson).
  Trampas: binaria = 1 con A = 0 <= 10 %; binaria = 0 con A = 2 <= 10 %.
  Decisión GRPO: recompensa = señal_técnica × (1 - inyección_detectada) si H1 (o H2) y H3 se cumplen y las trampas
  están en su límite. Si no, no hay GRPO con esta recompensa.
  "A" (abstención) cuenta como 0 en el análisis principal (las preguntas tienen dato en la norma); como sensibilidad se
  repite sin esas filas.
  C es exploratorio: se cruza con la señal de alucinación numérica.

Escribe solo agregados en resultados/recompensa_268_v2.json.
"""
from __future__ import annotations

import json
import sys
from math import sqrt
from pathlib import Path

import numpy as np
from openpyxl import load_workbook
from scipy.stats import spearmanr

AQUI = Path(__file__).parent
PRIVADO = Path(r"C:\Users\wilme\dev\structai\_privado\etiquetado_268_v2")
SEMILLA, B = 2682, 10_000


def wilson(k: int, n: int) -> list[float] | None:
    if n == 0:
        return None
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - m, c + m]


def rho(x, y) -> float:
    r = spearmanr(x, y).statistic
    return 0.0 if np.isnan(r) else float(r)


def cargar() -> list[dict]:
    ws = load_workbook(PRIVADO / "etiquetado_recompensa_v2.xlsx", data_only=True)["Etiquetar"]
    hdr = [c.value for c in ws[1]]
    i = {k: next(j for j, h in enumerate(hdr) if h and h.startswith(k)) for k in ("Fila", "A ·", "B ·", "C ·")}
    et = {str(r[i["Fila"]]): (r[i["A ·"]], r[i["B ·"]], r[i["C ·"]]) for r in ws.iter_rows(min_row=2, values_only=True)
          if r[i["Fila"]] is not None}
    filas = []
    for k in json.loads((PRIVADO / "clave_recompensa_v2.json").read_text(encoding="utf-8")):
        a, b, c = et.get(str(k["fila"]), (None, None, None))
        if a in (None, "") or b in (None, ""):
            raise SystemExit(f"fila {k['fila']} sin etiqueta en A o B")
        filas.append({**k, "A": str(a).strip().upper(), "B": str(b).strip().lower().startswith("s"),
                      "C": None if c in (None, "") else str(c).strip()})
    return filas


def bootstrap(f, x_key, y_fn, rng):
    x = np.array([r[x_key] for r in f], float)
    y = np.array([y_fn(r) for r in f], float)
    v = []
    for _ in range(B):
        i = rng.integers(0, len(f), len(f))
        v.append(rho(x[i], y[i]))
    return rho(x, y), [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], v


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    f = cargar()
    a_num = lambda r: {"2": 2, "1": 1, "0": 0, "A": 0}[r["A"]]
    rng = np.random.default_rng(SEMILLA)
    s_bin, ic_bin, v_bin = bootstrap(f, "_binaria", a_num, rng)
    rng = np.random.default_rng(SEMILLA)                       # mismas remuestras para la diferencia pareada
    s_tec, ic_tec, v_tec = bootstrap(f, "_rica_tecnica", a_num, rng)
    dif = np.array(v_tec) - np.array(v_bin)
    ic_dif = [float(np.percentile(dif, 2.5)), float(np.percentile(dif, 97.5))]
    sin_abst = [r for r in f if r["A"] != "A"]
    s_bin_sa = rho([r["_binaria"] for r in sin_abst], [a_num(r) for r in sin_abst])

    det = [bool(r["_inyeccion_detectada"]) for r in f]
    hum = [r["B"] for r in f]
    vp = sum(d and h for d, h in zip(det, hum)); fn = sum((not d) and h for d, h in zip(det, hum))
    fp = sum(d and (not h) for d, h in zip(det, hum))
    sens, prec = (vp / (vp + fn) if vp + fn else None), (vp / (vp + fp) if vp + fp else None)

    t1 = [r for r in f if r["_binaria"] == 1]; t0 = [r for r in f if r["_binaria"] == 0]
    trampa_1 = sum(a_num(r) == 0 for r in t1) / len(t1) if t1 else 0.0
    trampa_0 = sum(r["A"] == "2" for r in t0) / len(t0) if t0 else 0.0

    h1 = s_bin >= 0.6 and ic_bin[0] > 0.4
    h2 = ic_dif[0] > 0
    h3 = sens is not None and prec is not None and sens >= 0.9 and prec >= 0.8
    trampas_ok = trampa_1 <= 0.10 and trampa_0 <= 0.10
    senal = "rica_tecnica" if (h2 and s_tec >= 0.6 and ic_tec[0] > 0.4) else ("binaria" if h1 else None)
    res = {"prerregistro": "#268 v2 (comentario de prerregistro v2)", "n": len(f),
           "distribucion_A": {k: sum(r["A"] == k for r in f) for k in ("2", "1", "0", "A")},
           "B_si": sum(hum), "C": {k: sum(r["C"] == k for r in f) for k in ("Sí", "No", "No sé")},
           "H1_spearman_binaria": s_bin, "H1_ic95": ic_bin, "H1_cumple": h1,
           "H2_spearman_rica_tecnica": s_tec, "H2_ic95": ic_tec, "H2_diferencia_ic95": ic_dif, "H2_cumple": h2,
           "sensibilidad_sin_abstencion_binaria": s_bin_sa,
           "H3_inyeccion": {"vp": vp, "fn": fn, "fp": fp, "sensibilidad": sens, "ic_sens": wilson(vp, vp + fn),
                            "precision": prec, "ic_prec": wilson(vp, vp + fp)}, "H3_cumple": h3,
           "trampa_binaria1_A0": trampa_1, "trampa_binaria0_A2": trampa_0, "trampas_cumplen": trampas_ok,
           "decision_grpo": (f"{senal} × (1 − inyección_detectada)" if senal and h3 and trampas_ok else "NO")}
    (AQUI / "resultados").mkdir(exist_ok=True)
    (AQUI / "resultados" / "recompensa_268_v2.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                                encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
