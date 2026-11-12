"""
Normaliza los APU en Excel de los colegas de Wilmer (permiso de uso confirmado el 2026-11-12) a un JSONL.

Entrada: carpeta con los .xlsx (descomprimidos FUERA del repo; son datos de terceros sin confianza: solo se leen).
Salida:  scripts/presupuesto/_privado/apu_colegas.jsonl   (gitignored: no se publica el trabajo de los colegas)
         docs/presupuesto/APU_COLEGAS_RESUMEN.md            (solo agregados, sin nombres ni archivos)

Qué hace:
- Una hoja = un APU (ITEM, UNIDAD, DESCRIPCIÓN; I. MATERIALES, II. MANO DE OBRA, III. EQUIPO, IV. TRANSPORTE).
  Las columnas se leen por su ENCABEZADO dentro de cada sección (hay hojas con y sin columna DESPERDICIO).
- No guarda nombres de autores ni rutas: el grupo (para validación cruzada por archivo) es un hash.
- Asigna etapa y capítulo de `taxonomia_etapas_presupuesto.json` desde el capítulo original (1–21 del ejercicio),
  con reglas por palabra clave en los capítulos mixtos (9, 10, 15, 19).
- Marca problemas de calidad: total que no cuadra con la suma de subtotales, precio unitario atípico frente a
  las demás versiones de la misma actividad (MAD robusto), rendimiento ausente, unidad ausente.

Uso: python scripts/presupuesto/normalizar_apu_colegas.py <carpeta_xlsx>
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parents[2]
PRIVADO = Path(__file__).resolve().parent / "_privado"
SALIDA = PRIVADO / "apu_colegas.jsonl"
RESUMEN = RAIZ / "docs" / "presupuesto" / "APU_COLEGAS_RESUMEN.md"

# Capítulos del ejercicio (vivienda campestre con piscina) → capítulo de la taxonomía.
CAPITULO_A_TAXONOMIA = {
    1: "1.1", 2: "1.2", 3: "1.3", 4: "1.4", 5: "1.6", 6: "3.1", 7: "2.1", 8: "2.4", 9: "2.6", 10: "1.5",
    11: "3.3", 12: "3.2", 13: "3.2", 14: "1.7", 15: "1.7", 16: "3.1", 17: "3.3", 18: "3.5", 19: "4.1", 20: "3.3",
    21: "3.6",
}
# Reglas para capítulos mixtos: (capítulo original, regex sobre la descripción, capítulo destino)
REGLAS_MIXTOS = [
    (9, r"\bgas\b", "2.3"), (10, r"puerta|rejilla|reja", "3.3"), (15, r"cielo ?raso|drywall|dry wall", "3.4"),
    (19, r"cerramiento|malla|porter", "4.4"), (19, r"parqueadero|pavimento|tope de llanta|acceso de veh", "4.2"),
    (1, r"limpieza|aseo", "3.6"),
]
NOMBRES_CAPITULO_EJERCICIO = {
    1: "Preliminares", 2: "Excavaciones y rellenos", 3: "Cimentación", 4: "Estructura en concreto (tanques, piscina)",
    5: "Mampostería", 6: "Pañetes", 7: "Instalaciones hidrosanitarias", 8: "Instalaciones eléctricas",
    9: "Instalaciones especiales (gas, calentador, piscina)", 10: "Estructura metálica", 11: "Carpintería metálica y ventanería",
    12: "Pisos", 13: "Enchapes", 14: "Impermeabilizaciones", 15: "Cielorrasos y cubiertas", 16: "Estuco y pintura",
    17: "Carpintería de madera", 18: "Aparatos sanitarios", 19: "Obras exteriores", 20: "Cerrajería", 21: "Aseo y entrega",
}
SECCIONES = [("materiales", r"^I\.? ?MATERIAL"), ("mano_obra", r"^II\.? ?MANO"), ("equipo", r"^III\.? ?EQUIPO"),
             ("transporte", r"^IV\.? ?TRANSPORTE")]
CAMPOS = {"DESCRIPCION": "descripcion", "UNIDAD": "unidad", "CANTIDAD": "cantidad", "DESPERDICIO": "desperdicio",
          "V. UNITARIO": "valor_unitario", "VALOR UNITARIO": "valor_unitario", "V. TOTAL": "valor_total",
          "VALOR TOTAL": "valor_total", "BASICO": "basico", "RENDIMIENTO": "rendimiento", "TARIFA": "valor_unitario",
          "DISTANCIA": "distancia", "PRECIO": "valor_unitario"}


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip()
    return re.sub(r"\s+", " ", s)


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def capitulo_original(item, hoja: str, archivo: str):
    for texto in (item, hoja):
        m = re.match(r"^\s*(\d{1,2})(?:[.,]|\s|$)", str(texto or ""))
        if m and 1 <= int(m.group(1)) <= 21:
            return int(m.group(1)), "item" if texto is item else "hoja"
    # Hojas con varios APU lado a lado ponen el nombre del capítulo ("ENCHAPES") en vez del número.
    nombre = norm(f"{item or ''} {hoja}")
    for rx, cap in ((r"ENCHAPE", 13), (r"ESTUCO|PINTURA", 16), (r"LIMPIEZA|ASEO", 21), (r"PANETE", 6),
                    (r"CARPINTERIA METALICA|ALUMINIO|VENTAN", 11), (r"CERRAJ", 20), (r"IMPERMEAB", 14),
                    (r"APARATOS", 18), (r"HIDRAUL|SANITAR", 7), (r"ELECTRIC", 8), (r"CIELO", 15), (r"PISO", 12)):
        if re.search(rx, nombre):
            return cap, "nombre_hoja"
    caps = [int(x) for x in re.findall(r"\b(\d{1,2})\b", Path(archivo).stem) if 1 <= int(x) <= 21]
    if len(caps) == 1:
        return caps[0], "archivo"
    return None, None


def a_taxonomia(cap: int | None, descripcion: str) -> str | None:
    if cap is None:
        return None
    for c, rx, destino in REGLAS_MIXTOS:
        if c == cap and re.search(rx, descripcion, re.I):
            return destino
    return CAPITULO_A_TAXONOMIA.get(cap)


def bloques(ws) -> list[list[list]]:
    """Algunas hojas ponen varios APU lado a lado: se parte la hoja en bloques de columnas, uno por cada celda
    'ITEM' de las primeras filas. Si hay un solo 'ITEM', el bloque es la hoja completa."""
    filas = [list(r) for r in ws.iter_rows(values_only=True)]
    inicios = []
    for r in filas[:4]:
        for j, c in enumerate(r):
            if c is not None and norm(c) == "ITEM" and j not in inicios:
                inicios.append(j)
    inicios.sort()
    if len(inicios) <= 1:
        return [filas]
    cortes = inicios + [max(len(r) for r in filas)]
    return [[r[a:b] for r in filas] for a, b in zip(cortes, cortes[1:])]


def leer_hoja(filas_hoja) -> dict:
    apu = {"item": None, "unidad": None, "descripcion": None, "materiales": [], "mano_obra": [], "equipo": [],
           "transporte": [], "subtotales": {}, "total": None, "factor_prestacional": None}
    seccion, cols = None, {}
    for fila in filas_hoja:
        celdas = list(fila)
        no_vacias = [(i, c) for i, c in enumerate(celdas) if c not in (None, "")]
        if not no_vacias:
            continue
        i0, v0 = no_vacias[0]
        t0 = norm(v0)
        textos = [norm(c) for _, c in no_vacias]
        if t0 == "ITEM" and len(no_vacias) >= 2 and seccion is None:
            apu["item"] = str(no_vacias[1][1]).strip()
            if "UNIDAD" in textos:
                k = textos.index("UNIDAD")
                if k + 1 < len(no_vacias):
                    apu["unidad"] = str(no_vacias[k + 1][1]).strip()
            continue
        if t0.startswith("DESCRIPCI") and seccion is None and len(no_vacias) == 2:
            apu["descripcion"] = str(no_vacias[1][1]).strip()
            continue
        nueva = next((nom for nom, rx in SECCIONES if re.match(rx, t0)), None)
        if nueva:
            seccion, cols = nueva, {}
            continue
        if seccion and t0.startswith("DESCRIPCI"):
            cols = {}
            for i, c in no_vacias:
                clave = next((v for k, v in CAMPOS.items() if norm(c).startswith(k)), None)
                if clave and clave not in cols.values():
                    cols[i] = clave
            continue
        if "SUBTOTAL" in textos:
            k = textos.index("SUBTOTAL")
            val = next((num(c) for _, c in no_vacias[k + 1:] if num(c) is not None), None)
            if seccion:
                apu["subtotales"][seccion] = val
            if t0.startswith("FACTOR PRESTACIONAL") and len(no_vacias) > 1:
                apu["factor_prestacional"] = num(no_vacias[1][1])
            continue
        if any(x.startswith(("TOTAL", "COSTO DIRECTO", "VALOR TOTAL", "PRECIO UNITARIO", "VALOR UNITARIO")) for x in textos[:2]) \
                and not (seccion and cols and t0 not in ("TOTAL", "COSTO DIRECTO", "VALOR TOTAL APU")):
            val = next((num(c) for _, c in reversed(no_vacias) if num(c) is not None), None)
            if val:
                apu["total"] = apu["total"] or val
            continue
        if seccion and cols and isinstance(v0, str) and num(v0) is None:
            reg = {campo: celdas[i] if i < len(celdas) else None for i, campo in cols.items()}
            reg = {k: (num(v) if k not in ("descripcion", "unidad") else (str(v).strip() if v is not None else None))
                   for k, v in reg.items()}
            if reg.get("descripcion"):
                apu[seccion].append(reg)
    return apu


def mad_atipico(valores: list[float], v: float, k: float = 3.5) -> bool:
    if len(valores) < 3 or v is None:
        return False
    med = statistics.median(valores)
    mad = statistics.median(abs(x - med) for x in valores) or 1e-9
    return abs(v - med) / (1.4826 * mad) > k


def main() -> None:
    entrada = Path(sys.argv[1])
    PRIVADO.mkdir(parents=True, exist_ok=True)
    apus = []
    for f in sorted(entrada.rglob("*.xlsx")):
        grupo = hashlib.sha1(f.name.encode()).hexdigest()[:10]
        wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
        for ws in wb.worksheets:
          for nb, bloque in enumerate(bloques(ws)):
              a = leer_hoja(bloque)
              if not (a["materiales"] or a["mano_obra"]) or not a["descripcion"]:
                  continue
              cap, origen = capitulo_original(a["item"], ws.title, f.name)
              a.update(grupo=grupo, capitulo_ejercicio=cap, capitulo_origen=origen,
                       capitulo_taxonomia=a_taxonomia(cap, a["descripcion"]))
              a["id"] = hashlib.sha1(f"{grupo}|{ws.title}|{nb}|{a['descripcion']}".encode()).hexdigest()[:12]
              suma = sum(v for v in a["subtotales"].values() if v)
              # El "total" de la hoja a veces es el valor del ítem (PU × cantidad de obra); el costo directo
              # unitario confiable es la suma de los subtotales por unidad.
              a["costo_directo_unitario"] = round(suma, 2) if suma else None
              a["calidad"] = {
                  "sin_unidad": not a["unidad"],
                  "sin_rendimiento_mo": not any(m.get("rendimiento") for m in a["mano_obra"]),
                  "total_no_cuadra": bool(a["total"] and suma and abs(a["total"] - suma) / max(a["total"], 1) > 0.02),
              }
              apus.append(a)
    # Copias exactas (p. ej. un archivo "- Copia"): misma descripción, unidad y subtotales → se marcan y se
    # excluyen de los conteos y del entrenamiento, porque inflan los datos y filtran entre pliegues de validación.
    vistos = {}
    for a in apus:
        firma = (norm(a["descripcion"]), norm(a["unidad"] or ""), tuple(sorted((k, round(v or 0)) for k, v in a["subtotales"].items())))
        a["duplicado_de"] = vistos.get(firma)
        vistos.setdefault(firma, a["id"])
    duplicados = sum(1 for a in apus if a["duplicado_de"])
    apus_todos, apus = apus, [a for a in apus if not a["duplicado_de"]]
    # Atipicidad del costo unitario entre versiones de la misma actividad (misma descripción normalizada y unidad)
    por_act = collections.defaultdict(list)
    for a in apus:
        por_act[(norm(a["descripcion"])[:40], norm(a["unidad"] or ""))].append(a)
    for grupo in por_act.values():
        cdu = [a["costo_directo_unitario"] for a in grupo if a["costo_directo_unitario"]]
        mat = [a["subtotales"].get("materiales") for a in grupo if a["subtotales"].get("materiales")]
        for a in grupo:
            a["calidad"]["costo_atipico_entre_versiones"] = mad_atipico(cdu, a["costo_directo_unitario"])
            a["calidad"]["materiales_atipicos_entre_versiones"] = mad_atipico(mat, a["subtotales"].get("materiales"))
            a["n_versiones"] = len(grupo)
    with SALIDA.open("w", encoding="utf-8") as fh:
        for a in apus_todos:
            fh.write(json.dumps(a, ensure_ascii=False, default=str) + "\n")

    # Resumen agregado (sin nombres, sin rutas)
    c_ej = collections.Counter(a["capitulo_ejercicio"] for a in apus)
    c_tax = collections.Counter(a["capitulo_taxonomia"] for a in apus)
    cal = collections.Counter(k for a in apus for k, v in a["calidad"].items() if v)
    fp = collections.Counter(a["factor_prestacional"] for a in apus)
    basicos = collections.Counter(int(m["basico"]) for a in apus for m in a["mano_obra"] if m.get("basico"))
    l = ["# APU de los colegas: resumen agregado", "",
         "Generado por `scripts/presupuesto/normalizar_apu_colegas.py`. Los APU normalizados están en "
         "`scripts/presupuesto/_privado/` (gitignored); aquí solo hay agregados, sin autores ni archivos.", "",
         f"- APU leídos: **{len(apus)}** de **{len(set(a['grupo'] for a in apus))}** archivos; "
         f"descripciones distintas: **{len(por_act)}**.",
         f"- Con materiales y mano de obra: **{sum(1 for a in apus if a['materiales'] and a['mano_obra'])}**; "
         f"con rendimiento de MO: **{sum(1 for a in apus if not a['calidad']['sin_rendimiento_mo'])}**; "
         f"con equipo: **{sum(1 for a in apus if a['equipo'])}**.",
         f"- Sin capítulo identificable: **{c_ej.get(None, 0)}**. Copias exactas excluidas: **{duplicados}**.",
         f"- Actividades con 3 o más versiones (de distintos colegas): **{sum(1 for g in por_act.values() if len(g) >= 3)}**; "
         f"son las que permiten estimar la dispersión de rendimientos y costos.", "",
         "| Capítulo del ejercicio | APU | Capítulo de la taxonomía (mayoritario) |", "|---|---|---|"]
    for cap in sorted(k for k in c_ej if k):
        destinos = collections.Counter(a["capitulo_taxonomia"] for a in apus if a["capitulo_ejercicio"] == cap)
        l.append(f"| {cap}. {NOMBRES_CAPITULO_EJERCICIO[cap]} | {c_ej[cap]} | "
                 f"{', '.join(f'{d} ({n})' for d, n in destinos.most_common(3))} |")
    l += ["", "Por capítulo de la taxonomía: " + ", ".join(f"{k} {v}" for k, v in sorted(c_tax.items(), key=lambda x: str(x[0]))),
          "", "Problemas de calidad: " + ", ".join(f"{k} {v}" for k, v in cal.most_common()),
          "", "Factor prestacional usado: " + ", ".join(f"{k} ({v})" for k, v in fp.most_common(6)),
          "", "Salarios básicos mensuales más usados en mano de obra: " + ", ".join(f"{k:,} ({v})" for k, v in basicos.most_common(8))]
    RESUMEN.write_text("\n".join(l) + "\n", encoding="utf-8")
    print("\n".join(l))


if __name__ == "__main__":
    main()
