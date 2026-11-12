"""
Dispersión de recetas y estructura de costos de los APU de los colegas (#199, #113). Sin red, solo el JSONL privado.

Idea: lo que envejece en un APU de hace años es el PRECIO; la RECETA (cantidad de material por unidad y horas
de cuadrilla por unidad) depende del método constructivo y cambia poco. Por eso:
  1. Para actividades con ≥ 3 versiones de distintos colegas se mide la dispersión del rendimiento de la cuadrilla
     (h/unidad, la mayor del grupo de mano de obra = tiempo de la cuadrilla) y de la cantidad del material principal
     (el de mayor valor). Se reporta mediana, coeficiente de variación robusto (MAD/mediana) y desviación del
     logaritmo, que es el parámetro que usaría el Monte Carlo de motor-apu (distribución lognormal).
  2. Estructura de costos por capítulo (% materiales / mano de obra / equipo / transporte), que sirve para
     indexar por componente (salario mínimo para MO, ICOCED para materiales) en vez de un solo IPC.
Salida: docs/presupuesto/RECETAS_DISPERSION.md
"""
from __future__ import annotations

import collections
import json
import math
import re
import statistics
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SALIDA = RAIZ / "docs" / "presupuesto" / "RECETAS_DISPERSION.md"


def norm(x: str) -> str:
    x = unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", x).strip()


def robusto(v: list[float]) -> dict:
    med = statistics.median(v)
    mad = statistics.median(abs(x - med) for x in v)
    logs = [math.log(x) for x in v if x > 0]
    return {"n": len(v), "mediana": med, "cv_robusto": (1.4826 * mad / med) if med else float("nan"),
            "sd_log": statistics.stdev(logs) if len(logs) >= 2 else float("nan"), "min": min(v), "max": max(v)}


def main() -> None:
    apus = [json.loads(l) for l in (AQUI / "_privado" / "apu_colegas.jsonl").read_text(encoding="utf-8").splitlines()]
    apus = [a for a in apus if not a.get("duplicado_de")]
    grupos = collections.defaultdict(list)
    for a in apus:
        grupos[(norm(a["descripcion"])[:30], norm(a["unidad"] or ""))].append(a)

    filas = []
    for (desc, unidad), g in grupos.items():
        if len(g) < 3:
            continue
        rend = [max(m["rendimiento"] for m in a["mano_obra"] if m.get("rendimiento")) for a in g
                if any(m.get("rendimiento") for m in a["mano_obra"])]
        cant = []
        for a in g:
            mats = [m for m in a["materiales"] if m.get("cantidad") and m.get("valor_total")]
            if mats:
                cant.append(max(mats, key=lambda m: m["valor_total"])["cantidad"])
        costo = [a["costo_directo_unitario"] for a in g if a.get("costo_directo_unitario")]
        filas.append((desc, unidad, len(g), robusto(rend) if len(rend) >= 3 else None,
                      robusto(cant) if len(cant) >= 3 else None, robusto(costo) if len(costo) >= 3 else None))
    filas.sort(key=lambda f: -f[2])

    # Mediana de la participación de cada componente POR APU (la suma total la dominan unos pocos APU con errores).
    estructura = collections.defaultdict(lambda: collections.defaultdict(list))
    for a in apus:
        cap = a.get("capitulo_taxonomia")
        tot = sum(v for v in a["subtotales"].values() if v)
        if not cap or not tot:
            continue
        for k in ("materiales", "mano_obra", "equipo", "transporte"):
            estructura[cap][k].append((a["subtotales"].get(k) or 0) / tot)

    def f(x, pct=False):
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return "—"
        return f"{x:.0%}" if pct else (f"{x:,.3g}" if x < 1000 else f"{x:,.0f}")

    l = ["# Recetas de los APU de los colegas: dispersión y estructura de costos", "",
         "Generado por `scripts/presupuesto/dispersion_recetas.py` (agregados; los APU están en `_privado/`).", "",
         "## 1. Dispersión entre colegas (actividades con 3 o más versiones)", "",
         "CV robusto = 1,4826·MAD/mediana. `sd_log` es la desviación del logaritmo: el parámetro de una lognormal "
         "para el Monte Carlo de `motor-apu`.", "",
         "| Actividad | Unidad | Versiones | Rendimiento cuadrilla h/u: mediana (CV; sd_log) | Cantidad del material principal: mediana (CV) | Costo directo: mediana (CV; rango) |",
         "|---|---|---|---|---|---|"]
    for desc, unidad, n, r, c, k in filas:
        l.append(f"| {desc} | {unidad or '—'} | {n} | "
                 + (f"{f(r['mediana'])} ({f(r['cv_robusto'], True)}; {f(r['sd_log'])})" if r else "—") + " | "
                 + (f"{f(c['mediana'])} ({f(c['cv_robusto'], True)})" if c else "—") + " | "
                 + (f"{f(k['mediana'])} ({f(k['cv_robusto'], True)}; {f(k['min'])}–{f(k['max'])})" if k else "—") + " |")
    cvs_r = [r["cv_robusto"] for _, _, _, r, _, _ in filas if r and not math.isnan(r["cv_robusto"])]
    cvs_k = [k["cv_robusto"] for _, _, _, _, _, k in filas if k and not math.isnan(k["cv_robusto"])]
    sdl = [r["sd_log"] for _, _, _, r, _, _ in filas if r and not math.isnan(r["sd_log"])]
    l += ["", f"Mediana del CV robusto: rendimientos **{f(statistics.median(cvs_r), True) if cvs_r else '—'}**, "
          f"costo directo **{f(statistics.median(cvs_k), True) if cvs_k else '—'}**; mediana de `sd_log` del rendimiento "
          f"**{f(statistics.median(sdl)) if sdl else '—'}** (n = {len(filas)} actividades).", "",
          "**Ojo:** un CV de 0 % en los rendimientos indica que los colegas usaron la misma tabla de rendimientos; las "
          "versiones no son mediciones independientes y **no sirven para estimar la dispersión real** del Monte Carlo. "
          "La variación del costo viene sobre todo de los precios elegidos y de errores (cantidades por m³ usadas como "
          "por m², totales del ítem en vez de unitarios).", "",
          "## 2. Estructura de costos por capítulo (mediana de la participación por APU)", "",
          "| Capítulo | APU | Materiales | Mano de obra | Equipo | Transporte |", "|---|---|---|---|---|---|"]
    for cap in sorted(estructura, key=lambda c: [int(x) for x in c.split(".")]):
        e = {k: statistics.median(v) for k, v in estructura[cap].items()}
        l.append(f"| {cap} | {len(estructura[cap]['materiales'])} | {e['materiales']:.0%} | {e['mano_obra']:.0%} | {e['equipo']:.0%} | {e['transporte']:.0%} |")
    SALIDA.write_text("\n".join(l) + "\n", encoding="utf-8")
    print("\n".join(l))


if __name__ == "__main__":
    sys.exit(main())
