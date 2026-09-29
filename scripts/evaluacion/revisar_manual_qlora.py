"""Segunda pasada sobre revisar_manual.jsonl (los 105 casos donde RAGAS no
pudo calcular faithfulness/context_recall -- ver exportar_dataset_qlora.py).

Hallazgo real tras inspeccionar 8 casos representativos a mano (adversariales,
factuales de Titulo A/H, comparativos): el NaN es casi siempre un artefacto
del PROPIO cálculo de RAGAS (la respuesta es correcta pero la métrica no se
pudo computar), no una señal real de mala calidad. Casos confirmados:
- Preguntas adversariales (Titulo L/M/N inexistentes, NTC 99999, "Marte"):
  el sistema se niega correctamente, RAGAS no puede puntuar faithfulness
  porque no hay ninguna afirmación factual que verificar.
- Preguntas comparativas ("Es mayor X que Y"): cuando uno de los dos valores
  viene DADO en la pregunta misma (ya establecido antes) y solo el otro
  necesita retrieval, context_recall se va a 0.0 aunque la respuesta sea
  perfectamente correcta -- RAGAS penaliza que "no todo salió del contexto",
  pero parte de la comparación viene legítimamente de la pregunta.

Esta pasada NO confía ciegamente en el patrón -- verifica cada caso con la
misma lógica que ya usa _detectar_posible_alucinacion_numerica() en
rag_multi_norma.py: todo número con unidad que aparece en la respuesta debe
poder encontrarse LITERALMENTE en el contexto recuperado O en el texto de
la pregunta (para el caso de comparativas con un valor ya dado). Si un
número de la respuesta no aparece en ninguno de los dos, el caso NO se
promueve automáticamente -- queda para revisión humana real.
"""
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IN_PATH = PROJECT_ROOT / "scripts" / "evaluacion" / "qlora_export" / "revisar_manual.jsonl"
OUT_DIR = PROJECT_ROOT / "scripts" / "evaluacion" / "qlora_export"

FRASES_NEGATIVA = [
    "no encontr", "el contexto disponible no", "no incluye informaci",
    "no encontré información", "no tengo esa informaci", "no está en las normas",
    "no esta en las normas",
]

UNIDADES_RE = (
    r"%|por ciento|porciento|MPa|kPa|kN/m2|kN/m²|kN|mm|m²|m2|"
    r"°|grados|kg|kgf/mm2|kgf/mm²|kgf|L/s|golpes/pie|golpes|años|horas|veces"
)
NUMERO_CON_UNIDAD_RE = re.compile(
    r"\d+[.,]\d+\s?(?:" + UNIDADES_RE + r")?"
    r"|\d{2,}\s?(?:" + UNIDADES_RE + r")"
)
NUMERAL_NORMA_RE = re.compile(r"\b[A-K]\.\d+(?:\.\d+)*(?:-\d+)?\b")


def es_refusal(respuesta: str) -> bool:
    r = respuesta.lower()
    return any(f in r for f in FRASES_NEGATIVA)


def numeros_sin_respaldo(respuesta: str, contexto: str, pregunta: str) -> list[str]:
    """Numeros con unidad en la respuesta que NO aparecen ni en el contexto
    ni en la pregunta (donde a veces viene un valor ya dado, en preguntas
    comparativas)."""
    resp_sin_numerales = NUMERAL_NORMA_RE.sub("", respuesta)
    candidatos = NUMERO_CON_UNIDAD_RE.findall(resp_sin_numerales)
    fuente_disponible = contexto + " " + pregunta
    sospechosos = []
    for c in candidatos:
        c = c.strip()
        variantes = {c, c.replace(",", "."), c.replace(".", ",")}
        solo_num = re.match(r"[\d.,]+", c)
        if solo_num:
            variantes.add(solo_num.group())
        if not any(v in fuente_disponible for v in variantes):
            sospechosos.append(c)
    return sospechosos


def main() -> None:
    filas = []
    with open(IN_PATH, encoding="utf-8") as f:
        for linea in f:
            filas.append(json.loads(linea))

    promovidos, quedan_manual = [], []
    for fila in filas:
        pregunta = fila["_metadata"]["pregunta"]
        contexto = fila["messages"][1]["content"]  # incluye "CONTEXTO NORMATIVO:\n...\n\nPREGUNTA: ..."
        respuesta = fila["messages"][2]["content"]

        if es_refusal(respuesta):
            fila["_metadata"]["motivo_promocion"] = "refusal_correcta"
            promovidos.append(fila)
            continue

        sospechosos = numeros_sin_respaldo(respuesta, contexto, pregunta)
        if not sospechosos:
            fila["_metadata"]["motivo_promocion"] = "todos_los_numeros_respaldados"
            promovidos.append(fila)
        else:
            fila["_metadata"]["numeros_sin_respaldo"] = sospechosos
            quedan_manual.append(fila)

    print(f"Total en revisar_manual.jsonl: {len(filas)}")
    print(f"Promovidos automáticamente (refusal correcta o todos los números respaldados): {len(promovidos)}")
    print(f"Quedan para revisión humana real (números sin respaldo en contexto/pregunta): {len(quedan_manual)}")

    with open(OUT_DIR / "revisar_manual_promovidos.jsonl", "w", encoding="utf-8") as f:
        for fila in promovidos:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    with open(OUT_DIR / "revisar_manual_pendiente.jsonl", "w", encoding="utf-8") as f:
        for fila in quedan_manual:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    if quedan_manual:
        print("\nCasos que SÍ necesitan tus ojos (número no encontrado en contexto ni pregunta):")
        for fila in quedan_manual:
            print(f"  - {fila['_metadata']['pregunta'][:90]}")
            print(f"    números sospechosos: {fila['_metadata']['numeros_sin_respaldo']}")


if __name__ == "__main__":
    main()
