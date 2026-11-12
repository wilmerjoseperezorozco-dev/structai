"""
Cobertura del normalizador de unidades (#207) sobre las fuentes reales de StructAI. Solo lectura.

Mide, por fuente, qué % de filas queda con unidad canónica sin ambigüedad, cuántas son presentaciones comerciales
(requieren su contenido) y cuáles quedan para revisión, con las escrituras más frecuentes de cada grupo.
Fuentes: apu_precios_referencia (Supabase), recetas de los APU de colegas (_privado), composición INVIAS (repo) y
cartillas EPC (si ya se extrajeron).
Salida: docs/presupuesto/UNIDADES_COBERTURA.md
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "packages" / "motor-apu"))
from src.unidades import normalizar  # noqa: E402

SALIDA = RAIZ / "docs" / "presupuesto" / "UNIDADES_COBERTURA.md"


def medir(filas):
    """filas: iterable de (texto_unidad, seccion, descripcion)."""
    c = collections.Counter()
    ej = collections.defaultdict(collections.Counter)
    for u, sec, desc in filas:
        r = normalizar(u, seccion=sec, descripcion=desc)
        g = "canónica" if r.unidad else "presentación" if r.presentacion else "revisión"
        c[g] += 1
        ej[g][(u or "∅").strip()] += 1
    return c, ej


def main() -> None:
    fuentes = {}
    # Base de precios
    try:
        from dotenv import load_dotenv
        from supabase import create_client
        load_dotenv(RAIZ / "apps" / "api" / ".env")
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
        filas, d = [], 0
        while True:
            lote = sb.table("apu_precios_referencia").select("actividad,unidad").range(d, d + 999).execute().data
            filas += lote
            d += 1000
            if len(lote) < 1000:
                break
        fuentes["Base de precios (apu_precios_referencia)"] = [(f["unidad"], None, f["actividad"]) for f in filas]
    except Exception as e:  # noqa: BLE001
        print("base no disponible:", e)
    # Recetas de colegas
    p = AQUI / "_privado" / "apu_colegas.jsonl"
    if p.exists():
        rec = []
        for l in p.read_text(encoding="utf-8").splitlines():
            a = json.loads(l)
            if a.get("duplicado_de"):
                continue
            rec.append((a.get("unidad"), None, a.get("descripcion")))
            for sec in ("materiales", "mano_obra", "equipo", "transporte"):
                rec += [(x.get("unidad"), sec, x.get("descripcion")) for x in a[sec]]
        fuentes["Recetas de colegas (ítem + insumos)"] = rec
    # INVIAS
    inv = []

    def walk(o, desc=None):
        if isinstance(o, dict):
            d = o.get("descripcion") or o.get("nombre") or desc
            for k, v in o.items():
                if "unidad" in k.lower() and isinstance(v, str):
                    inv.append((v, None, d))
                walk(v, d)
        elif isinstance(o, list):
            for x in o:
                walk(x, desc)
    walk(json.loads((RAIZ / "packages" / "motor-apu" / "data" / "composicion_invias_2026_1.json").read_text(encoding="utf-8")))
    fuentes["Composición INVIAS 2026-1"] = inv
    # EPC
    epc = RAIZ / "scripts" / "ingesta" / "epc" / "salida" / "epc_precios_largo.csv"
    if epc.exists():
        with epc.open(encoding="utf-8") as fh:
            vistas = {(f["actividad"], f["unidad"]) for f in csv.DictReader(fh)}
        fuentes["Cartillas EPC 2021–2026 (actividades únicas)"] = [(u, None, a) for a, u in vistas]

    L = ["# Cobertura del normalizador de unidades (#207)", "",
         "Generado por `scripts/presupuesto/cobertura_unidades.py`. *Canónica*: unidad fija resuelta sin ambigüedad. "
         "*Presentación*: bulto, cuñete, caja… (convertible solo con su contenido). *Revisión*: no se decide sin una "
         "persona (no se adivina).", "",
         "| Fuente | Filas | Canónica | Presentación | Revisión | Escrituras en revisión más frecuentes |", "|---|---|---|---|---|---|"]
    for nombre, filas in fuentes.items():
        c, ej = medir(filas)
        n = sum(c.values()) or 1
        top = ", ".join(f"`{k}` ({v})" for k, v in ej["revisión"].most_common(6)) or "—"
        L.append(f"| {nombre} | {n:,} | {c['canónica'] / n:.1%} | {c['presentación'] / n:.1%} | {c['revisión'] / n:.1%} | {top} |")
    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
