"""Análisis de la fase 2 fijado en docs/evaluacion/PREREGISTRO_INDICE_LOCAL.md (índice local vs RPC).

Solo lee los resultados ya generados; no llama a Groq ni a Supabase. Uso:

    python -I scripts/evaluacion/indice_local/analizar_fase2.py

Qué calcula, tal como lo dice el preregistro:
- Prueba principal: McNemar exacto sobre los pares discordantes (local ✓/RPC ✗ frente a local ✗/RPC ✓), α = 0,05.
- Tamaño del efecto: diferencia apareada de proporciones (local − RPC), con IC95 por bootstrap de pares
  (10.000 réplicas, semilla 20261116).
- Además:
  - el total de la batería: las preguntas "sin efecto" (prompt idéntico) cuentan con diferencia 0;
  - resultados por batería;
  - aprobación absoluta de cada modo con IC de Wilson;
  - todo con y sin las generaciones 413 (enmienda del 2026-11-18).
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "packages" / "eval-stats" / "src"))
from estadistica import ic_wilson, mcnemar_exacto  # noqa: E402

RES = Path(__file__).resolve().parent / "resultados"
SEMILLA, N_BOOT, ALFA = 20261116, 10_000, 0.05


def cargar() -> tuple[dict, list[dict]]:
    pares: dict[str, dict] = {}
    for linea in (RES / "fase2_respuestas.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(linea)
        pares.setdefault(r["id"], {"bateria": r["bateria"]})[r["modo"]] = r
    filtro = json.loads((RES / "filtro_contexto.json").read_text(encoding="utf-8"))
    return pares, filtro["filas"]


def ic_bootstrap_dif(d: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(SEMILLA)
    medias = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    return float(np.quantile(medias, 0.025)), float(np.quantile(medias, 0.975))


def efecto_minimo_detectable(n: int, p_disc: float, potencia: float = 0.80) -> float:
    """Aproximación normal para McNemar: δ ≈ (z_{1−α/2} + z_{potencia})·√(p_disc / n)."""
    if n == 0 or p_disc == 0:
        return math.nan
    return (stats.norm.ppf(1 - ALFA / 2) + stats.norm.ppf(potencia)) * math.sqrt(p_disc / n)


def analizar(nombre: str, local: np.ndarray, rpc: np.ndarray, n_sin_efecto: int = 0) -> dict:
    mc = mcnemar_exacto(rpc, local)                      # a = RPC, b = local: diff_prop = local − RPC
    d = np.concatenate([local.astype(float) - rpc.astype(float), np.zeros(n_sin_efecto)])
    lo, hi = ic_bootstrap_dif(d)
    n = len(local)
    kl, kr = int(local.sum()), int(rpc.sum())
    disc = mc["n01_solo_b"] + mc["n10_solo_a"]
    out = {
        "grupo": nombre, "n_generadas": n, "n_sin_efecto": n_sin_efecto,
        "local_ok": kl, "rpc_ok": kr,
        "aprob_local": kl / n, "aprob_local_wilson": ic_wilson(kl, n),
        "aprob_rpc": kr / n, "aprob_rpc_wilson": ic_wilson(kr, n),
        "solo_local": mc["n01_solo_b"], "solo_rpc": mc["n10_solo_a"], "p_mcnemar": mc["p"],
        "dif": float(d.mean()), "dif_ic95": (lo, hi),
        "efecto_minimo_detectable_80": efecto_minimo_detectable(len(d), disc / len(d)),
    }
    out["decision"] = ("el índice local MEJORA" if lo > 0 else "REGRESIÓN" if hi < 0
                       else "no se detecta diferencia con este n")
    return out


def mde(x: float) -> str:
    return "— (sin pares discordantes)" if math.isnan(x) else f"±{100 * x:.1f} pts"


def fmt(r: dict) -> str:
    pc = lambda x: f"{100 * x:.1f} %"                    # noqa: E731
    wl, wr = r["aprob_local_wilson"], r["aprob_rpc_wilson"]
    lo, hi = r["dif_ic95"]
    return (f"| {r['grupo']} | {r['n_generadas']} (+{r['n_sin_efecto']} sin efecto) | "
            f"{r['local_ok']} = {pc(r['aprob_local'])} [{pc(wl[0])}–{pc(wl[1])}] | "
            f"{r['rpc_ok']} = {pc(r['aprob_rpc'])} [{pc(wr[0])}–{pc(wr[1])}] | {r['solo_local']} / {r['solo_rpc']} | "
            f"{r['p_mcnemar']:.3f} | {100 * r['dif']:+.1f} pts [{100 * lo:+.1f}, {100 * hi:+.1f}] | "
            f"{mde(r['efecto_minimo_detectable_80'])} | {r['decision']} |")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pares, filas = cargar()
    sin_efecto = Counter(f["bateria"] for f in filas if f["identico"])
    ids = sorted(pares)
    incompletos = [i for i in ids if not {"local", "rpc"} <= pares[i].keys()]
    if incompletos:
        print(f"faltan modos en {len(incompletos)} preguntas: {incompletos[:5]}")
        return 1
    err = Counter((pares[i][m].get("error"), m) for i in ids for m in ("local", "rpc") if pares[i][m].get("error"))
    tablas = []
    for etiqueta, excluir_413 in (("con 413 como no aprobada (principal)", False), ("sin los pares con 413", True)):
        sel = [i for i in ids if not (excluir_413 and any(pares[i][m].get("error") == "413" for m in ("local", "rpc")))]
        filas_md = []
        for grupo in ("todas", "nsr10", "motores"):
            s = [i for i in sel if grupo == "todas" or pares[i]["bateria"] == grupo]
            loc = np.array([bool(pares[i]["local"]["aprueba"]) for i in s])
            rpc = np.array([bool(pares[i]["rpc"]["aprueba"]) for i in s])
            filas_md.append(fmt(analizar(f"{grupo} (generadas)", loc, rpc)))
            nse = sum(sin_efecto.values()) if grupo == "todas" else sin_efecto.get(grupo, 0)
            filas_md.append(fmt(analizar(f"{grupo} (batería total)", loc, rpc, nse)))
        tablas.append((etiqueta, filas_md))

    cab = ("| Grupo | n | Local ✓ [Wilson] | RPC ✓ [Wilson] | solo local / solo RPC | p McNemar | Local − RPC [IC95 boot] "
           "| Efecto mín. detectable (80 %) | Decisión |\n|---|---|---|---|---|---|---|---|---|")
    md = ["# Resultados de la fase 2: índice local vs RPC", "",
          "Generado por `analizar_fase2.py` según `docs/evaluacion/PREREGISTRO_INDICE_LOCAL.md`. "
          f"Bootstrap de pares: {N_BOOT} réplicas, semilla {SEMILLA}. Población: {len(filas)} preguntas, "
          f"{sum(sin_efecto.values())} sin efecto (prompt idéntico), {len(ids)} generadas en los dos modos.", "",
          "Generaciones rechazadas con 413 (cuentan como no aprobadas en la tabla principal): "
          + (", ".join(f"{n} en modo {m}" for (_, m), n in sorted(err.items())) or "ninguna") + ".", ""]
    for etiqueta, filas_md in tablas:
        md += [f"## {etiqueta}", "", cab, *filas_md, ""]
    md += ["La regla de decisión se aplica a la fila **todas (batería total)** de la tabla principal: IC95 entero > 0 → "
           "mejora; cruza 0 → no se detecta diferencia (no se afirma equivalencia); entero < 0 → regresión y se "
           "revierte con `RAG_INDICE_LOCAL=false`.", ""]
    salida = RES / "RESULTADOS_FASE2.md"
    salida.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
