"""
Cobertura de los precios de StructAI frente a la taxonomía de presupuesto por etapas. SOLO LECTURA.

Lee `apu_precios_referencia` (Supabase) y clasifica cada actividad en un capítulo de
`packages/motor-apu/data/taxonomia_etapas_presupuesto.json` con las claves (regex) de la taxonomía.
Desempate: gana el capítulo cuya clave aparece MÁS AL INICIO de la descripción, porque en los
presupuestos colombianos la actividad principal va primero ("Excavación manual para tubería" es
excavación, no tubería). Es una línea base para medir huecos; el clasificador real (con umbral y
aprendizaje activo, como el enrutador de #169) queda en el issue de la taxonomía.

Los productos de ferretería del catálogo IAD (tipo_fuente = catalogo_iad_mipymes) son INSUMOS sueltos,
no actividades con APU: se cuentan aparte.

Uso:  python scripts/presupuesto/cobertura_etapas.py            (escribe docs/presupuesto/COBERTURA_PRECIOS_ETAPAS.md)
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TAXONOMIA = RAIZ / "packages" / "motor-apu" / "data" / "taxonomia_etapas_presupuesto.json"
SALIDA_MD = RAIZ / "docs" / "presupuesto" / "COBERTURA_PRECIOS_ETAPAS.md"
SALIDA_JSON = RAIZ / "docs" / "presupuesto" / "cobertura_precios_etapas.json"
INSUMOS_SUELTOS = {"catalogo_iad_mipymes"}


def cargar_taxonomia() -> list[dict]:
    t = json.loads(TAXONOMIA.read_text(encoding="utf-8"))
    caps = []
    for e in t["etapas"]:
        for c in e["capitulos"]:
            caps.append({"etapa": f"{e['id']}. {e['nombre']}", "id": c["id"], "nombre": c["nombre"],
                         "rx": [re.compile(k, re.I) for k in c["claves"]], "normas": c["normas"],
                         "motores": c["motores"], "issues": c.get("issues", [])})
    return caps


def clasificar(texto: str, caps: list[dict]) -> tuple[dict | None, int]:
    """(capítulo, n de capítulos que coincidieron). Gana la coincidencia más temprana en el texto."""
    mejor, pos_mejor, n = None, 10 ** 9, 0
    for c in caps:
        pos = min((m.start() for r in c["rx"] if (m := r.search(texto))), default=None)
        if pos is None:
            continue
        n += 1
        if pos < pos_mejor:
            mejor, pos_mejor = c, pos
    return mejor, n


def leer_precios() -> list[dict]:
    from dotenv import load_dotenv
    from supabase import create_client
    load_dotenv(RAIZ / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    cols = "actividad,unidad,region,tipo_fuente,disciplina,desglose_confiable,costo_materiales,costo_mano_obra,precio_todo_costo"
    filas, desde = [], 0
    while True:
        lote = sb.table("apu_precios_referencia").select(cols).range(desde, desde + 999).execute().data
        filas += lote
        if len(lote) < 1000:
            return filas
        desde += 1000


def main() -> None:
    caps = cargar_taxonomia()
    filas = leer_precios()
    actividades = [f for f in filas if f["tipo_fuente"] not in INSUMOS_SUELTOS]
    insumos = len(filas) - len(actividades)
    por_cap = collections.defaultdict(list)
    ambiguas, sin = 0, []
    for f in actividades:
        c, n = clasificar(f["actividad"] or "", caps)
        if c is None:
            sin.append(f)
            continue
        ambiguas += n > 1
        por_cap[c["id"]].append(f)

    def desglosada(f):
        return bool(f["costo_materiales"] and f["costo_mano_obra"])

    resumen = []
    for c in caps:
        fs = por_cap.get(c["id"], [])
        regiones = collections.Counter(f["region"] or "—" for f in fs)
        faltan = [n for n, est in c["normas"] if est == "falta"]
        resumen.append({"etapa": c["etapa"], "id": c["id"], "capitulo": c["nombre"], "actividades": len(fs),
                        "con_desglose": sum(desglosada(f) for f in fs),
                        "regiones": dict(regiones.most_common(3)), "motores": c["motores"],
                        "normas_faltantes": faltan, "issues": c["issues"]})
    palabras = collections.Counter(w for f in sin for w in re.findall(r"[a-záéíóúñ]{5,}", (f["actividad"] or "").lower()))

    lineas = ["# Cobertura de precios de StructAI por etapa y capítulo", "",
              "Generado por `scripts/presupuesto/cobertura_etapas.py` (solo lectura) contra `apu_precios_referencia`, "
              "con la taxonomía `packages/motor-apu/data/taxonomia_etapas_presupuesto.json`. Clasificación por palabras "
              "clave (línea base): sirve para ver huecos, no como etiqueta definitiva.", "",
              f"- Filas totales: **{len(filas)}**. Insumos sueltos de ferretería (IAD): **{insumos}**, fuera del conteo.",
              f"- Actividades con APU o precio de obra: **{len(actividades)}**; clasificadas: **{len(actividades) - len(sin)}** "
              f"({(len(actividades) - len(sin)) / max(len(actividades), 1):.0%}); sin clasificar: **{len(sin)}**; "
              f"con más de un capítulo posible: **{ambiguas}**.", "",
              "| Etapa | Capítulo | Actividades | Con desglose MO/materiales | Regiones (top 3) | Motores | Normas que faltan | Issues |",
              "|---|---|---|---|---|---|---|---|"]
    for r in resumen:
        reg = ", ".join(f"{k} {v}" for k, v in r["regiones"].items()) or "—"
        lineas.append(f"| {r['etapa']} | {r['id']} {r['capitulo']} | {r['actividades']} | {r['con_desglose']} | {reg} | "
                      f"{', '.join(r['motores']) or '**ninguno**'} | {'; '.join(r['normas_faltantes']) or '—'} | "
                      f"{', '.join(r['issues']) or '—'} |")
    lineas += ["", "Palabras más frecuentes en las actividades sin clasificar (para ampliar las claves):", "",
               ", ".join(f"{w} ({n})" for w, n in palabras.most_common(40))]
    SALIDA_MD.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_MD.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    SALIDA_JSON.write_text(json.dumps({"total": len(filas), "insumos_sueltos": insumos, "actividades": len(actividades),
                                       "sin_clasificar": len(sin), "ambiguas": ambiguas, "capitulos": resumen},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    sys.exit(main())
