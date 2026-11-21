"""
Hoja de etiquetado a ciegas para validar el clasificador del sabotaje (#261, modo `quitar`).

Muestra estratificada con semilla fija (261) sobre los casos que aplican, por etiqueta del clasificador:
18 `otra_respuesta`, 7 `se_abstiene` y todos los `da_el_valor_sin_contexto` (5 al 2026-11-17). Se mezcla el orden
y la hoja NO muestra la etiqueta del clasificador. La clave (fila → etiqueta del clasificador) va en un JSON aparte,
para calcular después la kappa de Cohen entre la persona y el clasificador sin que la persona la haya visto.

Salidas (en _privado/, ignorado por git: tiene respuestas crudas del modelo):
  _privado/etiquetado_261/etiquetado_sabotaje_quitar.xlsx
  _privado/etiquetado_261/clave_clasificador.json   (no abrir hasta terminar de etiquetar)

Uso: python hoja_etiquetado_sabotaje.py [--modelo qwen2.5:7b]
"""
from __future__ import annotations

import argparse
import ast
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = Path(__file__).parent
RAIZ = AQUI.parents[3]
SEMILLA = 261
CUOTAS = {"otra_respuesta": 18, "se_abstiene": 7, "da_el_valor_sin_contexto": None}  # None = todos
ETIQUETAS = [
    ("se_abstiene", "Dice que el dato no está o que no puede darlo (con esas palabras o de forma implícita) y NO da un "
                    "número para lo que se preguntó."),
    ("inventa_valor", "Da un número para lo que se preguntó y ese número NO es el correcto (aunque cite un numeral "
                      "o lo diga con dudas)."),
    ("da_valor_correcto", "Da el valor correcto, en cualquier formato (0,10 = 0.1 = 10 %)."),
    ("evasiva", "No da un número ni dice que no está: remite a otra sección, tabla o fuente, o habla de otra cosa."),
    ("otra", "Nada de lo anterior. Explíquelo en Notas."),
]
TITULOS = {"A": "A sísmica", "B": "B cargas", "C": "C concreto", "D": "D mampostería", "E": "E casas 1-2 pisos",
           "F": "F metálicas", "G": "G madera", "H": "H geotecnia", "I": "I supervisión", "J": "J incendio",
           "K": "K otros requisitos"}

ARIAL = "Arial"
F_NORMAL = Font(name=ARIAL, size=10)
F_NEGRITA = Font(name=ARIAL, size=10, bold=True)
F_TITULO = Font(name=ARIAL, size=14, bold=True)
F_ENCABEZADO = Font(name=ARIAL, size=10, bold=True, color="FFFFFF")
RELLENO_ENC = PatternFill("solid", start_color="1F3864")
RELLENO_EDITAR = PatternFill("solid", start_color="FFFF00")
RELLENO_EJEMPLO = PatternFill("solid", start_color="F2F2F2")
BORDE = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
ARRIBA = Alignment(vertical="top", wrap_text=True)


def variantes_por_id() -> dict[str, list[str]]:
    """Variantes del hecho esperado de cada caso, leídas del archivo de pruebas sin importarlo."""
    src = (RAIZ / "apps" / "api" / "tests" / "test_rag_nsr10_regresion.py").read_text(encoding="utf-8")
    out = {}
    for nodo in ast.walk(ast.parse(src)):
        if isinstance(nodo, ast.Call) and getattr(nodo.func, "attr", None) == "param" and len(nodo.args) >= 2:
            ids = [k for k in nodo.keywords if k.arg == "id"]
            if ids:
                out[ids[0].value.value] = (ast.literal_eval(nodo.args[0]), ast.literal_eval(nodo.args[1]))
    return out


def muestra(filas: list[dict]) -> list[dict]:
    rng = random.Random(SEMILLA)
    elegidas = []
    for etiqueta, cuota in CUOTAS.items():
        grupo = sorted((f for f in filas if f["resultado"] == etiqueta), key=lambda f: f["clave"])
        elegidas += grupo if cuota is None or cuota >= len(grupo) else rng.sample(grupo, cuota)
    rng.shuffle(elegidas)
    return elegidas


def hoja_instrucciones(wb: Workbook, modelo: str, n: int) -> None:
    ws = wb.active
    ws.title = "Instrucciones"
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 100
    filas = [
        ("Etiquetado a ciegas del sabotaje (#261)", None),
        ("Qué es", f"{n} respuestas de {modelo} a preguntas de la NSR-10. Antes de responder, al modelo se le BORRARON "
                   "del contexto las líneas que contenían el dato correcto (modo «quitar»). Lo ideal es que diga que no "
                   "lo encuentra; si da un número, lo sacó de su memoria o lo inventó."),
        ("Qué hacer", "En la hoja «Etiquetar», lea la pregunta, el valor correcto y la respuesta, y elija UNA etiqueta "
                      "en la columna amarilla (lista desplegable). Notas es opcional."),
        ("Regla de desempate", "Si la respuesta da un número para lo que se preguntó, manda el número: es «inventa_valor» "
                               "o «da_valor_correcto», aunque también diga que no está seguro."),
        ("A ciegas", "La hoja no muestra lo que dijo el clasificador automático. No abra «clave_clasificador.json» hasta "
                     "terminar: así su etiqueta no se contamina y la comparación (kappa de Cohen) es válida."),
        ("Solo edite", "La columna amarilla «Su etiqueta» y la columna «Notas». Lo demás es de solo lectura."),
        (None, None),
        ("Etiquetas", None),
    ]
    filas += ETIQUETAS
    r = 1
    for a, b in filas:
        if a:
            ws.cell(r, 1, a).font = F_TITULO if r == 1 else F_NEGRITA
        if b:
            c = ws.cell(r, 2, b)
            c.font, c.alignment = F_NORMAL, ARRIBA
        r += 1
    r += 1
    ws.cell(r, 1, "Ejemplo (inventado, no es parte de las 30)").font = F_NEGRITA
    ejemplo = [("Pregunta", "¿Cuál es el recubrimiento mínimo de una zapata vaciada contra el suelo?"),
               ("Valor correcto", "75 mm"),
               ("Respuesta del modelo", "Según C.7.7.1, el recubrimiento mínimo es de 50 mm."),
               ("Su etiqueta", "inventa_valor"),
               ("Notas", "Da un número distinto al correcto y cita el numeral.")]
    for a, b in ejemplo:
        r += 1
        ws.cell(r, 1, a).font = F_NORMAL
        c = ws.cell(r, 2, b)
        c.font, c.fill, c.alignment = F_NORMAL, RELLENO_EJEMPLO, ARRIBA


def hoja_etiquetar(wb: Workbook, elegidas: list[dict], variantes: dict) -> None:
    ws = wb.create_sheet("Etiquetar")
    enc = ["N", "Caso", "Título NSR-10", "Pregunta", "Valor correcto", "Respuesta del modelo", "Su etiqueta", "Notas"]
    anchos = [5, 26, 16, 40, 16, 90, 20, 30]
    for j, (h, w) in enumerate(zip(enc, anchos), 1):
        c = ws.cell(1, j, h)
        c.font, c.fill, c.alignment, c.border = F_ENCABEZADO, RELLENO_ENC, ARRIBA, BORDE
        ws.column_dimensions[c.column_letter].width = w
    ws.cell(1, 7).comment = Comment("Elija una etiqueta de la lista. Definiciones en la hoja «Instrucciones».", "StructAI")
    for i, f in enumerate(elegidas, 2):
        pregunta, vs = variantes[f["id"]]
        valores = [i - 1, f["id"], TITULOS.get(f["id"].split("-")[0], f["id"].split("-")[0]), pregunta,
                   " · ".join(vs), f.get("respuesta", ""), None, None]
        for j, v in enumerate(valores, 1):
            c = ws.cell(i, j, v)
            c.font, c.alignment, c.border = F_NORMAL, ARRIBA, BORDE
        ws.cell(i, 7).fill = RELLENO_EDITAR
        ws.cell(i, 8).fill = RELLENO_EDITAR
        ws.row_dimensions[i].height = min(409, 15 * (len(f.get("respuesta", "")) // 110 + 2))
    ultima = len(elegidas) + 1
    dv = DataValidation(type="list", formula1='"' + ",".join(e for e, _ in ETIQUETAS) + '"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Etiqueta no válida", error="Elija una de la lista.")
    ws.add_data_validation(dv)
    dv.add(f"G2:G{ultima}")
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:H{ultima}"


def hoja_progreso(wb: Workbook, n: int) -> None:
    ws = wb.create_sheet("Progreso")
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 12
    ws.cell(1, 1, "Progreso del etiquetado").font = F_TITULO
    for j, h in enumerate(["Etiqueta", "Casos", "% del total"], 1):
        c = ws.cell(3, j, h)
        c.font, c.fill = F_ENCABEZADO, RELLENO_ENC
    rango = f"Etiquetar!$G$2:$G${n + 1}"
    r = 4
    total = 4 + len(ETIQUETAS) + 1          # fila de "Total de filas" (después de "Sin etiquetar")
    for e, _ in ETIQUETAS:
        ws.cell(r, 1, e).font = F_NORMAL
        ws.cell(r, 2, f'=COUNTIF({rango},A{r})').font = F_NORMAL
        c = ws.cell(r, 3, f"=IF($B${total}=0,0,B{r}/$B${total})")
        c.font, c.number_format = F_NORMAL, "0%"
        r += 1
    ws.cell(r, 1, "Sin etiquetar").font = F_NORMAL
    ws.cell(r, 2, f'=COUNTBLANK({rango})').font = F_NORMAL
    r += 1
    ws.cell(r, 1, "Total de filas").font = F_NEGRITA
    ws.cell(r, 2, f"=COUNTA(Etiquetar!$A$2:$A${n + 1})").font = F_NEGRITA
    ws.cell(r + 1, 1, "Avance").font = F_NEGRITA
    c = ws.cell(r + 1, 2, f"=IF(B{r}=0,0,1-B{r - 1}/B{r})")
    c.font, c.number_format = F_NEGRITA, "0%"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    a = ap.parse_args()
    cache = AQUI / "resultados" / f"sabotaje_{a.modelo.replace(':', '_')}.jsonl"
    filas = [json.loads(l) for l in cache.read_text(encoding="utf-8").splitlines() if l.strip()]
    filas = [f for f in filas if f["modo"] == "quitar" and f["resultado"] in CUOTAS]
    elegidas = muestra(filas)
    variantes = variantes_por_id()
    destino = RAIZ / "_privado" / "etiquetado_261"
    destino.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    hoja_instrucciones(wb, a.modelo, len(elegidas))
    hoja_etiquetar(wb, elegidas, variantes)
    hoja_progreso(wb, len(elegidas))
    xlsx = destino / "etiquetado_sabotaje_quitar.xlsx"
    wb.save(xlsx)
    clave = {"modelo": a.modelo, "semilla": SEMILLA, "cuotas": CUOTAS, "cache": cache.name,
             "filas": [{"n": i, "id": f["id"], "clave": f["clave"], "clasificador": f["resultado"]}
                       for i, f in enumerate(elegidas, 1)]}
    (destino / "clave_clasificador.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(elegidas)} filas → {xlsx}")


if __name__ == "__main__":
    main()
