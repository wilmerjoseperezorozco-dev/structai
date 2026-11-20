"""
Análisis del sabotaje del contexto (#261): métrica formal con intervalos, por estrato y por tamaño del prompt.

Lee el caché de sabotaje.py (resultados/sabotaje_<modelo>.jsonl) sin llamar a ningún LLM. Se puede correr mientras el
CI nocturno sigue escribiendo: solo lee.

Métricas (definidas en el issue #261 antes de ver los datos del modo falsear):
  quitar  · tasa de memoria   = da_el_valor_sin_contexto / aplica   (responde lo que ya no está en el contexto)
          · tasa de abstención = se_abstiene / aplica                (lo correcto)
  falsear · fidelidad          = fiel_al_contexto_falso / aplica     (repite el número falso del contexto)
          · memoria            = ignora_el_contexto / aplica         (da el valor real pese al contexto)
  «aplica» excluye no_aplica y error. Cada tasa lleva IC de Wilson al 95 %.

Uso: python analizar_sabotaje.py [--modelo qwen2.5:7b] [--muestra-otra N]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parents[3] / "packages" / "eval-stats" / "src"))
from estadistica import ic_wilson  # noqa: E402

TITULOS = {"A": "A sísmica", "B": "B cargas", "C": "C concreto", "D": "D mampostería", "E": "E casas 1-2 pisos",
           "F": "F acero/aluminio", "G": "G madera", "H": "H geotecnia", "I": "I supervisión", "J": "J incendio",
           "K": "K complementarios", "N": "N (otros)"}
METRICAS = {"quitar": ("da_el_valor_sin_contexto", "se_abstiene"), "falsear": ("fiel_al_contexto_falso", "ignora_el_contexto")}
NO_CUENTAN = ("no_aplica", "error")


def pct(k: int, n: int) -> str:
    if not n:
        return "—"
    lo, hi = ic_wilson(k, n)
    return f"{k}/{n} = {k / n:.0%} [{lo:.0%}–{hi:.0%}]"


def cargar(modelo: str) -> list[dict]:
    f = AQUI / "resultados" / f"sabotaje_{modelo.replace(':', '_')}.jsonl"
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    ap.add_argument("--muestra-otra", type=int, default=0, help="imprime N respuestas 'otra_respuesta' al azar para auditarlas")
    a = ap.parse_args()
    filas = cargar(a.modelo)
    print(f"# Sabotaje — {a.modelo}: {len(filas)} filas en caché\n")
    for modo, (m1, m2) in METRICAS.items():
        fs = [f for f in filas if f["modo"] == modo]
        ap_ = [f for f in fs if f["resultado"] not in NO_CUENTAN]
        print(f"## {modo}: {len(fs)} casos, aplica a {len(ap_)}")
        if not ap_:
            print("  (todavía sin casos que apliquen)\n")
            continue
        c = Counter(f["resultado"] for f in ap_)
        for res, v in c.most_common():
            print(f"  {res:28s} {pct(v, len(ap_))}")
        print(f"\n  Por título NSR-10 ({m1} · {m2}):")
        por = defaultdict(list)
        for f in ap_:
            por[f["id"][0]].append(f["resultado"])
        for t in sorted(por):
            rs = por[t]
            print(f"   {TITULOS.get(t, t):20s} n={len(rs):3d}  {m1[:14]}: {pct(rs.count(m1), len(rs)):24s} {m2[:14]}: {pct(rs.count(m2), len(rs))}")
        con_tok = sorted((f for f in ap_ if f.get("tokens_prompt")), key=lambda f: f["tokens_prompt"])
        if len(con_tok) >= 8:
            mitad = len(con_tok) // 2
            print(f"\n  Por tamaño del prompt (mediana {con_tok[mitad]['tokens_prompt']} tokens) — indicio de context rot:")
            for nombre, grupo in (("corto", con_tok[:mitad]), ("largo", con_tok[mitad:])):
                rs = [f["resultado"] for f in grupo]
                print(f"   {nombre:6s} n={len(rs):3d}  {m2[:14]}: {pct(rs.count(m2), len(rs)):24s} otra_respuesta: {pct(rs.count('otra_respuesta'), len(rs))}")
        print()
    if a.muestra_otra:
        otras = [f for f in filas if f["resultado"] == "otra_respuesta"]
        random.Random(261).shuffle(otras)
        print(f"## Muestra de {min(a.muestra_otra, len(otras))} 'otra_respuesta' (semilla 261) para auditar el clasificador\n")
        for f in otras[: a.muestra_otra]:
            print(f"### {f['modo']} · {f['id']}\n{f.get('respuesta', '')[:600]}\n")


if __name__ == "__main__":
    main()
