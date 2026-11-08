"""Prepara (sin tocar producción) la re-ingesta de la Resolución 0330/2017 con el texto consolidado del Gestor Normativo de la CRA.
El texto hoy indexado es una transcripción de IA del PDF escaneado, anterior a las Res. 799 y 908 de 2021.
Uso: python scripts/ingesta/res0330/preparar_reingesta_consolidada.py
Entradas : scripts/ingesta/ras_audit/res0330_2017.txt (CRA)  y  packages/construdata/normativa_raw/res0330/res0330.txt (actual)
Salidas  : scripts/ingesta/res0330/res0330_consolidada.json (chunks listos) y REPORTE_DIFERENCIAS_0330.md"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parents[2]
CRA = ROOT / "scripts" / "ingesta" / "ras_audit" / "res0330_2017.txt"
ACTUAL = ROOT / "packages" / "construdata" / "normativa_raw" / "res0330" / "res0330.txt"
SALIDA_JSON = AQUI / "res0330_consolidada.json"
SALIDA_MD = AQUI / "REPORTE_DIFERENCIAS_0330.md"

ENCABEZADO = re.compile(r"^\s*ARTÍCULO\s+(\d+[A-Z]?)o?\.\s*(.*)$")
ETIQUETAS = re.compile(r"^\s*(Notas de Vigencia|Legislación Anterior|Concordancias|Jurisprudencia Vigencia|Notas del Editor|Doctrina Concordante)\s*$", re.I)
ESTRUCTURA = re.compile(r"^\s*(TÍTULO|CAPÍTULO|SECCIÓN|PARTE)\s+[\dIVXLC]+\b", re.I)
TAG = re.compile(r"<\s*Art[ií]culo\s+(modificado|corregido|adicionado|derogado)[^>]*?(?:por el art[ií]culo\s+(\d+)\s+de la Resoluci[oó]n\s+(\d+)\s+de\s+(\d{4}))?[^>]*>", re.I)
FIN = re.compile(r"^\s*(Comisión de\s*$|Sede principal|Inicio documento|Fin documento|Menú del pie)")


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def similitud(a: str, b: str) -> float:
    """Jaccard sobre trigramas de palabras (rápido; difflib exacto es cuadrático y no termina con artículos largos)."""
    def tri(t: str) -> set:
        w = re.findall(r"\w+", t.lower())
        return {tuple(w[i:i + 3]) for i in range(max(len(w) - 2, 1))}
    x, y = tri(a), tri(b)
    return len(x & y) / len(x | y) if x | y else 1.0


def leer_cra() -> list[dict]:
    lineas = CRA.read_text(encoding="utf-8").splitlines()
    arts, actual = [], None
    for ln in lineas:
        m = ENCABEZADO.match(ln)
        if m:
            actual = {"num": m.group(1), "resto": [m.group(2)]}
            arts.append(actual)
            continue
        if actual is None:
            continue
        if FIN.match(ln):
            actual = None
            continue
        if ETIQUETAS.match(ln) or ESTRUCTURA.match(ln):
            continue
        actual["resto"].append(ln)
    out = []
    for a in arts:
        texto = normalizar(" ".join(a["resto"]))
        texto = re.split(r"\s*Gestor Normativo de la Comisi", texto)[0]   # pie de página de la CRA que sigue al último artículo
        mod = TAG.search(texto)
        nota = None
        if mod:
            nota = normalizar(mod.group(0).strip("<>"))
            nota = re.sub(r"\.?\s*El nuevo texto es el siguiente:?\s*$", "", nota)
            texto = normalizar(texto.replace(mod.group(0), ""))
        m = re.match(r"^([^.]+?)\.\s*(.*)$", texto)
        titulo, cuerpo = (m.group(1).strip(), m.group(2).strip()) if m else (texto[:80], texto)
        out.append({"num": a["num"], "titulo": titulo, "cuerpo": cuerpo, "modificacion": nota})
    return out


def leer_actual() -> dict[str, dict]:
    """El archivo actual no es JSON válido (escapes sueltos): se lee por patrón, línea a línea."""
    s = ACTUAL.read_text(encoding="utf-8")
    patron = re.compile(r'"chunk_id": "RES0330-ART(\d+)",\s*"seccion_origen": "[^"]*",\s*"titulo": "(.*?)",\s*"embedding_ready": "(.*?)"\s*\},?\s*(?=\{|\]|\Z)', re.DOTALL)
    return {m.group(1): {"titulo": m.group(2), "embedding_ready": m.group(3)} for m in patron.finditer(s)}


def main():
    nuevos = leer_cra()
    actuales = leer_actual()
    ids = [a["num"] for a in nuevos]
    duplicados = sorted({i for i in ids if ids.count(i) > 1})
    chunks = [{
        "chunk_id": f"RES0330-ART{a['num']}", "seccion_origen": f"ARTÍCULO {a['num']}", "titulo": a["titulo"][:200],
        "embedding_ready": normalizar(f"ARTÍCULO {a['num']}. {a['titulo']}. " + (f"[{a['modificacion']}] " if a["modificacion"] else "") + a["cuerpo"]),
        "modificacion": a["modificacion"],
    } for a in nuevos]
    SALIDA_JSON.write_text(json.dumps({"fuente": "Gestor Normativo CRA, Resolución 330 de 2017 (texto consolidado con Res. 799 y 908 de 2021)",
                                       "fecha_copia": "2026-08-08", "chunks": chunks}, ensure_ascii=False, indent=1), encoding="utf-8")

    # Comparación por título normalizado (la numeración cambió, no sirve comparar por número)
    ref = {normalizar(c["titulo"]).upper(): (k, c) for k, c in actuales.items()}
    iguales, cambiados, nuevos_art, vistos = [], [], [], set()
    for a in nuevos:
        clave = normalizar(a["titulo"]).upper()
        if clave in ref:
            k, c = ref[clave]
            vistos.add(clave)
            sim = similitud(c["embedding_ready"], f"{a['titulo']}. {a['cuerpo']}")
            (iguales if sim >= 0.97 else cambiados).append((a, k, sim))
        else:
            nuevos_art.append(a)
    solo_actual = [(k, c["titulo"]) for k, c in actuales.items() if normalizar(c["titulo"]).upper() not in vistos]
    desfasados = sum(1 for a, k, _ in iguales + cambiados if a["num"] != k)

    md = ["# Diferencias entre la Res. 0330 indexada y el texto consolidado de la CRA", "",
          "Generado por `preparar_reingesta_consolidada.py` el 2026-11-08. Comparación por título (la numeración cambió).", "",
          f"- Artículos en el texto indexado hoy: **{len(actuales)}**. En el consolidado: **{len(nuevos)}**.",
          f"- Títulos coincidentes con texto casi idéntico (similitud ≥ 0,97): **{len(iguales)}**.",
          f"- Títulos coincidentes con texto distinto: **{len(cambiados)}**.",
          f"- Artículos solo en el consolidado: **{len(nuevos_art)}**. Solo en el indexado: **{len(solo_actual)}**.",
          f"- Artículos coincidentes cuyo **número** difiere: **{desfasados}** (riesgo de cita errónea si no se re-ingesta).",
          f"- Artículos con nota de modificación o corrección en el consolidado: **{sum(1 for a in nuevos if a['modificacion'])}**.",
          f"- Números repetidos en el consolidado: {duplicados or 'ninguno'}.", "",
          "**Cómo leer este reporte.** (1) El texto indexado hoy es una transcripción por IA de un PDF escaneado, así que parte de las diferencias son errores de transcripción y no cambios normativos; con estos datos no se pueden separar. (2) Los títulos repetidos (p. ej. «ALCANCE», «PROCEDIMIENTO GENERAL») se emparejan con una sola fila y generan similitudes cercanas a 0 que son artefactos del emparejamiento por título. (3) La similitud es Jaccard de trigramas de palabras, no una distancia de edición.", "",
          "## Texto distinto (mayor diferencia primero)", "", "| Art. consolidado | Art. indexado | Título | Similitud | Nota |", "|---|---|---|---|---|"]
    for a, k, sim in sorted(cambiados, key=lambda x: x[2])[:60]:
        md.append(f"| {a['num']} | {k} | {a['titulo'][:60]} | {sim:.2f} | {(a['modificacion'] or '')[:60]} |")
    md += ["", "## Solo en el consolidado", ""] + [f"- Art. {a['num']}: {a['titulo'][:90]}" for a in nuevos_art]
    md += ["", "## Solo en el indexado (posibles artículos derogados o con título cambiado)", ""] + [f"- Art. {k}: {t[:90]}" for k, t in solo_actual]
    SALIDA_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"consolidado={len(nuevos)} indexado={len(actuales)} iguales={len(iguales)} cambiados={len(cambiados)} nuevos={len(nuevos_art)} "
          f"solo_indexado={len(solo_actual)} num_distinto={desfasados} duplicados={duplicados}")


if __name__ == "__main__":
    main()
