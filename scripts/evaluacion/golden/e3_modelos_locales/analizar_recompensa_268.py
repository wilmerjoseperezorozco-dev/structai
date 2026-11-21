"""Análisis de la validación a ciegas de la recompensa verificable (#268), según el prerregistro (comentario 6967842190).

Lee la hoja etiquetada y la clave de _privado/ (no versionadas) y escribe SOLO agregados en
resultados/recompensa_268.json (sin respuestas crudas ni preguntas).

Uso: python analizar_recompensa_268.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from openpyxl import load_workbook
from scipy.stats import spearmanr

AQUI = Path(__file__).parent
PRIVADO = Path(r"C:\Users\wilme\dev\structai\_privado\etiquetado_268")
SEMILLA, B = 268, 10_000


def cargar() -> list[dict]:
    ws = load_workbook(PRIVADO / "etiquetado_recompensa.xlsx", data_only=True)["Etiquetar"]
    hdr = [c.value for c in ws[1]]
    i_fila, i_nota = hdr.index("Fila"), hdr.index("Nota (0, 1, 2)")
    notas = {str(r[i_fila]): r[i_nota] for r in ws.iter_rows(min_row=2, values_only=True) if r[i_fila] is not None}
    clave = json.loads((PRIVADO / "clave_recompensa.json").read_text(encoding="utf-8"))
    filas = []
    for k in clave:
        n = notas.get(str(k["fila"]))
        if n in (None, ""):
            raise SystemExit(f"fila {k['fila']} sin etiqueta")
        filas.append({"humana": int(n), "rica": float(k["_rica"]), "binaria": float(k["_binaria"]),
                      "origen": k["origen"], "modelo": k["modelo"], "ataque": k["ataque"]})
    return filas


def rho(x, y) -> float:
    r = spearmanr(x, y).statistic
    return 0.0 if np.isnan(r) else float(r)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    f = cargar()
    h = np.array([r["humana"] for r in f]); ri = np.array([r["rica"] for r in f]); bi = np.array([r["binaria"] for r in f])
    rng = np.random.default_rng(SEMILLA)
    br, bb, bd = [], [], []
    for _ in range(B):
        i = rng.integers(0, len(f), len(f))
        a, b = rho(ri[i], h[i]), rho(bi[i], h[i])
        br.append(a); bb.append(b); bd.append(a - b)
    ic = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    altas = ri >= 0.8
    ceros = ri == 0
    trampa_alta = float((h[altas] == 0).mean()) if altas.any() else 0.0
    trampa_cero = float((h[ceros] == 2).mean()) if ceros.any() else 0.0
    s_rica = rho(ri, h)
    regla = s_rica >= 0.6 and ic(br)[0] > 0.4 and trampa_alta <= 0.10 and trampa_cero <= 0.10

    def por(clave):
        out = {}
        for v in sorted({str(r[clave]) for r in f}):
            m = np.array([str(r[clave]) == v for r in f])
            out[v] = {"n": int(m.sum()), "humana_media": float(h[m].mean()), "rica_media": float(ri[m].mean()),
                      "spearman_rica": rho(ri[m], h[m]) if m.sum() > 3 else None,
                      "humana_0_con_rica_alta": int(((h == 0) & altas & m).sum()),
                      "humana_2_con_rica_0": int(((h == 2) & ceros & m).sum())}
        return out

    res = {"prerregistro": "issue #268, comentario 6967842190", "n": len(f),
           "distribucion_humana": {str(k): int((h == k).sum()) for k in (0, 1, 2)},
           "spearman_rica": s_rica, "ic95_rica": ic(br),
           "spearman_binaria": rho(bi, h), "ic95_binaria": ic(bb),
           "diferencia_rica_menos_binaria": s_rica - rho(bi, h), "ic95_diferencia": ic(bd),
           "trampa_rica_alta_humana_0": {"frac": trampa_alta, "n_altas": int(altas.sum())},
           "trampa_rica_0_humana_2": {"frac": trampa_cero, "n_ceros": int(ceros.sum())},
           "tabla_humana_vs_binaria": {f"h{a}_b{int(b)}": int(((h == a) & (bi == b)).sum()) for a in (0, 1, 2) for b in (0, 1)},
           "por_origen": por("origen"), "por_modelo": por("modelo"), "por_ataque": por("ataque"),
           "regla_grpo_cumple": bool(regla)}
    (AQUI / "resultados").mkdir(exist_ok=True)
    (AQUI / "resultados" / "recompensa_268.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
