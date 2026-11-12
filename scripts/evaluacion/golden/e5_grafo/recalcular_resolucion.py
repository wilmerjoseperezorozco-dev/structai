"""
Fase 0 del plan de huecos (issue #186): recalcula la resolución de las citas de
normas_referencias_cruzadas con el índice por encabezados, SIN escribir en la
base. Compara la resolución guardada (calculada contra `seccion`) con la nueva.

Resolución nueva:
  exacta      el numeral citado tiene su encabezado en algún chunk
  prefijo     no hay encabezado propio, pero sí de algún subnumeral (capítulo)
  sin_destino ni el numeral ni subnumerales aparecen

Uso: python scripts/evaluacion/golden/e5_grafo/recalcular_resolucion.py
Salida: resolucion_recalculada.json (resumen + filas que cambian)
"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

RAIZ = Path(__file__).resolve().parents[4]
load_dotenv(RAIZ / "apps" / "api" / ".env")
AQUI = Path(__file__).parent


def main():
    indice = json.loads((AQUI / "indice_numerales_nsr10.json").read_text(encoding="utf-8"))
    claves = set(indice)
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    filas, off = [], 0
    while True:
        d = sb.table("normas_referencias_cruzadas").select("id,numeral_destino,resolucion,n_chunks_destino").range(off, off + 999).execute().data
        filas += d
        off += 1000
        if len(d) < 1000:
            break

    def nueva(n):
        n = n.strip().upper().rstrip(".-")
        if n in claves:
            return "exacta", len(indice[n])
        hijos = [k for k in claves if k.startswith(n + ".")]
        return ("prefijo", len({c for k in hijos for c in indice[k]})) if hijos else ("sin_destino", 0)

    cambios, transiciones = [], Counter()
    for f in filas:
        r, n = nueva(f["numeral_destino"])
        transiciones[(f["resolucion"], r)] += 1
        if r != f["resolucion"]:
            cambios.append({"id": f["id"], "numeral_destino": f["numeral_destino"], "antes": f["resolucion"], "ahora": r, "n_chunks": n})
    antes = Counter(f["resolucion"] for f in filas)
    ahora = Counter(nueva(f["numeral_destino"])[0] for f in filas)
    salida = {"aristas": len(filas), "antes": dict(antes), "ahora": dict(ahora),
              "transiciones": {f"{a} -> {b}": n for (a, b), n in transiciones.most_common()},
              "cambios": cambios}
    (AQUI / "resolucion_recalculada.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in salida.items() if k != "cambios"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
