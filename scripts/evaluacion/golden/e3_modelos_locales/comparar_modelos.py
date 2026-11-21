"""
Comparación entre modelos locales sobre los mismos casos (#172). Sin LLM.

Criterio PRERREGISTRADO (fijado el 2026-11-12, antes de las corridas con ventana 16384):
  1. Por modelo: tasa de "pasa" con IC de Wilson e IC bootstrap por título (clúster = prefijo del
     id: A, B, ..., H, motores...), porque los casos de un mismo título no son independientes.
  2. El modelo con mayor tasa es el candidato. Contra cada rival: McNemar exacto sobre los casos
     pareados, p ajustada por Holm (familia = todas las comparaciones contra el candidato).
  3. Gana el candidato solo si TODAS sus comparaciones tienen p_Holm < 0,05.
  4. Si no: los que no se distinguen del candidato quedan EMPATADOS. Entre ellos se elige el más
     barato (menor latencia mediana por caso) SOLO si su tasa está a <= MARGEN_PP puntos del
     candidato; si ninguno más barato cumple, se queda el candidato. Para el CI pesa más acertar
     que ahorrar minutos: un empate estadístico con 4 puntos menos no justifica cambiar de modelo.

Qué filas se usan por modelo: las de resultados/<modelo>_ctx16384.jsonl. Si a un modelo le
faltan casos con 16384, se completan con la corrida de 8192 SOLO si ese caso no estuvo truncado
(el prompt que leyó el modelo fue el mismo). Los casos truncados sin re-corrida se excluyen del
pareo y se informan. Solo entran casos presentes en TODOS los modelos comparados.

Uso: python comparar_modelos.py [--modelos qwen2.5:7b llama3:8b hermes3:latest] [--min-casos 100]
Salida: COMPARACION.md
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
sys.path.insert(0, str(AQUI.parents[3] / "packages" / "eval-stats" / "src"))
import estadistica as st  # noqa: E402

ALFA = 0.05
MARGEN_PP = 0.03


def _leer(p: Path) -> dict:
    if not p.exists():
        return {}
    return {json.loads(l)["id"]: json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def _truncado_8k(f: dict) -> bool:
    # Firma del recorte silencioso de Ollama con num_ctx 8192: exactamente 4.098 tokens leídos.
    return bool(f.get("prompt_truncado")) or f.get("tokens_prompt") == 4098


def filas_modelo(modelo: str) -> tuple[dict, dict]:
    base = modelo.replace(":", "_").replace("/", "_")
    ctx16 = _leer(RES / f"{base}_ctx16384.jsonl")
    ctx8 = _leer(RES / f"{base}.jsonl")
    filas, origen = {}, {"ctx16384": 0, "ctx8192_sin_truncar": 0, "excluidos_truncados_8k": 0}
    for i, f in ctx16.items():
        if "error" not in f:
            filas[i] = f
            origen["ctx16384"] += 1
    for i, f in ctx8.items():
        if i in filas or "error" in f:
            continue
        if _truncado_8k(f):
            origen["excluidos_truncados_8k"] += 1
            continue
        filas[i] = f
        origen["ctx8192_sin_truncar"] += 1
    return filas, origen


def titulo(caso_id: str, bateria: str) -> str:
    return "motores" if bateria == "motores" else caso_id.split("-")[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", default=["qwen2.5:7b", "llama3:8b", "hermes3:latest"])
    ap.add_argument("--min-casos", type=int, default=100,
                    help="mínimo de casos pareados para emitir veredicto (por debajo solo se describe)")
    a = ap.parse_args()

    a.modelos = list(dict.fromkeys(a.modelos))      # sin duplicados (nocturno.sh antepone qwen2.5:7b)
    datos = {m: filas_modelo(m) for m in a.modelos}
    comunes = sorted(set.intersection(*(set(f) for f, _ in datos.values())))
    lineas = ["# Comparación de modelos locales (#172)", "",
              "Criterio prerregistrado: ver el docstring de `comparar_modelos.py`. "
              f"Casos pareados (presentes en todos): **{len(comunes)}**.", "",
              "| Modelo | Pasa | Tasa | Wilson IC95 | Bootstrap por título IC95 | Latencia p50 | Origen de filas |",
              "|---|---|---|---|---|---|---|"]
    tasas, lat = {}, {}
    for m, (filas, origen) in datos.items():
        v = [1.0 if filas[i]["paso"] else 0.0 for i in comunes]
        cl = [titulo(i, filas[i]["bateria"]) for i in comunes]
        k, n = int(sum(v)), len(v)
        wl, wh = st.ic_wilson(k, n) if n else (float("nan"),) * 2
        bc = st.bootstrap_por_cluster(v, cl) if n else {"ic_inf": float("nan"), "ic_sup": float("nan")}
        tasas[m] = k / n if n else 0.0
        lat[m] = statistics.median(filas[i]["segundos_total"] for i in comunes) if n else float("inf")
        lineas.append(f"| {m} | {k}/{n} | {tasas[m]:.1%} | {wl:.1%}–{wh:.1%} | {bc['ic_inf']:.1%}–{bc['ic_sup']:.1%} "
                      f"| {lat[m]:.0f} s | {origen} |")

    if len(comunes) < a.min_casos:
        lineas += ["", f"**Sin veredicto:** {len(comunes)} casos pareados < mínimo {a.min_casos}. Faltan corridas."]
    else:
        cand = max(a.modelos, key=lambda m: (tasas[m], -lat[m]))
        rivales = [m for m in a.modelos if m != cand]
        res = {}
        for r in rivales:
            ca = [1.0 if datos[cand][0][i]["paso"] else 0.0 for i in comunes]
            cb = [1.0 if datos[r][0][i]["paso"] else 0.0 for i in comunes]
            res[r] = st.mcnemar_exacto(cb, ca)    # b = candidato: n01 = solo el candidato acierta
        ph = st.holm([res[r]["p"] for r in rivales])
        lineas += ["", f"Candidato (mayor tasa): **{cand}**", "",
                   "| Rival | Solo candidato acierta | Solo rival acierta | p McNemar | p Holm | ¿Se distingue? |",
                   "|---|---|---|---|---|---|"]
        empatados = [cand]
        for r, p_h in zip(rivales, ph):
            d = res[r]
            distingue = p_h is not None and p_h < ALFA and d["n01_solo_b"] > d["n10_solo_a"]
            if not distingue:
                empatados.append(r)
            lineas.append(f"| {r} | {d['n01_solo_b']} | {d['n10_solo_a']} | {d['p']:.4f} | {p_h:.4f} | "
                          f"{'sí' if distingue else 'no'} |")
        if len(empatados) == 1:
            veredicto = f"**Gana {cand}**: se distingue de todos los rivales (p_Holm < {ALFA})."
        else:
            elegibles = [m for m in empatados if tasas[cand] - tasas[m] <= MARGEN_PP + 1e-12]
            barato = min(elegibles, key=lambda m: lat[m])
            veredicto = (f"**Empate estadístico** entre {', '.join(empatados)}. Regla de desempate: el más barato "
                         f"a <= {MARGEN_PP:.0%} del candidato ({', '.join(elegibles)}) → se elige **{barato}** "
                         f"({tasas[barato]:.1%}, {lat[barato]:.0f} s por caso).")
        lineas += ["", veredicto]
    texto = "\n".join(lineas) + "\n"
    (AQUI / "COMPARACION.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
