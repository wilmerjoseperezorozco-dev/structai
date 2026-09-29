"""Exporta pares (pregunta, contexto recuperado, respuesta verificada) desde
las corridas RAGAS reales ya guardadas en scripts/evaluacion/*_scorecard.csv,
en formato listo para fine-tuning QLoRA (chat messages: system/user/assistant).

Por qué existe este script (2026-09-29, ver [[project_structai_caza_bugs_2026-09-28]]
y la conversación sobre evolucionar StructAI con fine-tuning propio):
StructAI ya acumuló 8 corridas RAGAS reales entre 2026-08-27 y 2026-09-13,
con puntajes reales por pregunta (faithfulness/answer_relevancy/
context_precision/context_recall). Eso es exactamente el material que un
paper reciente sobre LLMs de construcción tuvo que fabricar a mano (715
pares QA generados por el propio LLM desde un grafo) -- nosotros ya lo
tenemos, verificado contra retrieval real, no generado sintéticamente.

Metodología (documentada aquí a propósito -- si esto termina en un paper,
esta es la sección de "Data Curation"):

1. DEDUP por pregunta: cuando la misma pregunta aparece en más de una
   corrida (ej. una pregunta de "52preguntas" del 2026-08-27 reaparece en
   "278preguntas" del 2026-09-09), se queda SOLO la fila de la corrida más
   reciente -- el sistema cambió entre medio (fixes de retrieval, nuevos
   chunks), así que una respuesta vieja puede reflejar un bug ya corregido.
   Encontrado en este export: 198 de 333 preguntas únicas estaban
   duplicadas entre corridas.

2. FILTRO DE CALIDAD (no se incluye una fila solo porque existe):
   - faithfulness >= UMBRAL_FAITHFULNESS Y context_recall >= UMBRAL_RECALL
     -> va a train/heldout como ejemplo "verificado bueno".
   - faithfulness es NaN (RAGAS no pudo puntuarlo -- típico en preguntas
     adversariales donde la respuesta correcta es "esto no existe/no lo
     sé", sin una afirmación factual que verificar) -> va a un archivo
     APARTE (revisar_manual.jsonl) para confirmación humana antes de
     usarse. Nunca se asume "bueno" automáticamente solo por ser NaN.
   - cualquier otra fila (puntaje bajo real) -> se excluye y se reporta,
     no se descarta en silencio.

3. SPLIT train/heldout: 85/15, semilla fija (reproducible), el heldout se
   guarda aparte explícitamente -- nunca se debe reusar como parte del
   "antes/después" de una futura comparación (para eso hace falta un set
   nuevo, no visto ni en RAGAS ni en este fine-tune).

4. Formato de salida: JSONL con {"messages": [system, user, assistant]},
   compatible directo con Unsloth/Axolotl/OpenAI fine-tuning format. El
   mensaje "system" es el SYSTEM_PROMPT real de producción (importado del
   módulo, no copiado a mano, para que nunca quede desactualizado). El
   mensaje "user" reconstruye el contexto EXACTO como lo arma ask() (mismo
   separador "\n\n---\n\n" entre fragmentos). El "assistant" es el
   `response` real (la respuesta que de verdad generó el sistema y que
   RAGAS verificó como bien fundamentada) -- no el `reference` (que es un
   resumen corto de verificación, no una respuesta en el tono de la app).
"""
import ast
import csv
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
from rag_multi_norma import SYSTEM_PROMPT  # noqa: E402  (real, no copiado)

csv.field_size_limit(sys.maxsize)

# Umbrales de calidad -- documentados, ajustables. faithfulness mide "¿la
# respuesta está fundamentada en el contexto recuperado?" (mapea directo a
# "sin derecho a alucinar"); context_recall mide "¿el retrieval SÍ trajo lo
# necesario?" (para no entrenar sobre una respuesta que acertó por suerte
# con mal contexto).
UMBRAL_FAITHFULNESS = 0.9
UMBRAL_CONTEXT_RECALL = 0.85

SEED_SPLIT = 42
FRACCION_HELDOUT = 0.15

EVAL_DIR = PROJECT_ROOT / "scripts" / "evaluacion"
OUT_DIR = EVAL_DIR / "qlora_export"

# (archivo, fecha) -- la fecha ordena qué corrida es "más reciente" para el
# dedup. Se excluyen a propósito los 3 archivos de ablación del 2026-08-27
# (query-decomposition/reranking-combinado/scorecard) porque son subsets de
# 12 preguntas ya cubiertas por corridas posteriores más grandes -- no
# aportan preguntas nuevas, solo medían el efecto de un cambio puntual.
ARCHIVOS_SCORECARD = [
    ("baseline_2026-08-27_52preguntas_scorecard.csv", "2026-08-27"),
    ("baseline_2026-09-07_143preguntas_scorecard.csv", "2026-09-07"),
    ("baseline_2026-09-07_precios_scorecard.csv", "2026-09-07"),
    ("baseline_2026-09-09_278preguntas_scorecard.csv", "2026-09-09"),
    ("baseline_2026-09-13-post-fix_precios_scorecard.csv", "2026-09-13"),
]


@dataclass
class Ejemplo:
    pregunta: str
    contextos: list[str]
    respuesta: str
    reference: str
    faithfulness: float | None
    context_recall: float | None
    fuente_archivo: str
    fuente_fecha: str


def _parsear_float(valor: str) -> float | None:
    valor = valor.strip()
    if not valor or valor.lower() == "nan":
        return None
    try:
        return float(valor)
    except ValueError:
        return None


def cargar_scorecard(nombre_archivo: str, fecha: str) -> list[Ejemplo]:
    ruta = EVAL_DIR / nombre_archivo
    ejemplos = []
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            # retrieved_contexts se guardó como str(list_de_python) -- no es
            # JSON válido (comillas simples), hace falta ast.literal_eval.
            try:
                contextos = ast.literal_eval(fila["retrieved_contexts"])
            except (ValueError, SyntaxError):
                contextos = [fila["retrieved_contexts"]]
            ejemplos.append(
                Ejemplo(
                    pregunta=fila["user_input"].strip(),
                    contextos=contextos,
                    respuesta=fila["response"].strip(),
                    reference=fila["reference"].strip(),
                    faithfulness=_parsear_float(fila["faithfulness"]),
                    context_recall=_parsear_float(fila["context_recall"]),
                    fuente_archivo=nombre_archivo,
                    fuente_fecha=fecha,
                )
            )
    return ejemplos


def deduplicar_por_pregunta(ejemplos: list[Ejemplo]) -> tuple[list[Ejemplo], int]:
    """Se queda con la fila de la corrida MÁS RECIENTE cuando la misma
    pregunta aparece en 2+ archivos. Devuelve (únicos, cuántos duplicados
    se descartaron)."""
    mejores: dict[str, Ejemplo] = {}
    descartados = 0
    for ej in ejemplos:
        actual = mejores.get(ej.pregunta)
        if actual is None:
            mejores[ej.pregunta] = ej
        elif ej.fuente_fecha > actual.fuente_fecha:
            mejores[ej.pregunta] = ej
            descartados += 1
        else:
            descartados += 1
    return list(mejores.values()), descartados


def clasificar(ejemplos: list[Ejemplo]) -> tuple[list[Ejemplo], list[Ejemplo], list[Ejemplo]]:
    """Devuelve (verificados_buenos, revisar_manual, excluidos_bajo_puntaje)."""
    buenos, revisar, excluidos = [], [], []
    for ej in ejemplos:
        if ej.faithfulness is None or ej.context_recall is None:
            revisar.append(ej)
        elif ej.faithfulness >= UMBRAL_FAITHFULNESS and ej.context_recall >= UMBRAL_CONTEXT_RECALL:
            buenos.append(ej)
        else:
            excluidos.append(ej)
    return buenos, revisar, excluidos


def formatear_mensaje_usuario(ej: Ejemplo) -> str:
    """Reconstruye el contexto EXACTO como lo arma ask() antes de pasarlo
    al LLM -- mismo separador, para que el fine-tune vea el mismo formato
    de entrada que producción."""
    contexto = "\n\n---\n\n".join(ej.contextos)
    return f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {ej.pregunta}"


def a_formato_chat(ej: Ejemplo) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatear_mensaje_usuario(ej)},
            {"role": "assistant", "content": ej.respuesta},
        ],
        "_metadata": {
            "pregunta": ej.pregunta,
            "reference": ej.reference,
            "fuente": ej.fuente_archivo,
            "faithfulness": ej.faithfulness,
            "context_recall": ej.context_recall,
        },
    }


def escribir_jsonl(ruta: Path, ejemplos: list[Ejemplo]) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        for ej in ejemplos:
            f.write(json.dumps(a_formato_chat(ej), ensure_ascii=False) + "\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    todos: list[Ejemplo] = []
    for nombre, fecha in ARCHIVOS_SCORECARD:
        cargados = cargar_scorecard(nombre, fecha)
        print(f"  {nombre}: {len(cargados)} filas")
        todos.extend(cargados)

    unicos, n_duplicados = deduplicar_por_pregunta(todos)
    print(f"\nTotal filas crudas: {len(todos)}")
    print(f"Preguntas únicas tras dedup (se queda la corrida más reciente): {len(unicos)}")
    print(f"Duplicados descartados: {n_duplicados}")

    buenos, revisar, excluidos = clasificar(unicos)
    print(f"\nVerificados buenos (faithfulness>={UMBRAL_FAITHFULNESS}, context_recall>={UMBRAL_CONTEXT_RECALL}): {len(buenos)}")
    print(f"Para revisar a mano (score no calculable, ej. adversariales): {len(revisar)}")
    print(f"Excluidos por puntaje bajo: {len(excluidos)}")

    random.seed(SEED_SPLIT)
    buenos_shuffled = buenos[:]
    random.shuffle(buenos_shuffled)
    n_heldout = max(1, round(len(buenos_shuffled) * FRACCION_HELDOUT))
    heldout = buenos_shuffled[:n_heldout]
    train = buenos_shuffled[n_heldout:]

    escribir_jsonl(OUT_DIR / "train.jsonl", train)
    escribir_jsonl(OUT_DIR / "heldout.jsonl", heldout)
    escribir_jsonl(OUT_DIR / "revisar_manual.jsonl", revisar)
    escribir_jsonl(OUT_DIR / "excluidos_bajo_puntaje.jsonl", excluidos)

    print(f"\nSplit final: {len(train)} train / {len(heldout)} heldout (semilla {SEED_SPLIT})")
    print(f"\nEscrito en {OUT_DIR}:")
    print("  train.jsonl, heldout.jsonl, revisar_manual.jsonl, excluidos_bajo_puntaje.jsonl")

    if excluidos:
        print("\nPreguntas excluidas por puntaje bajo (para que las veas, no quedan ocultas):")
        for ej in excluidos:
            print(f"  - [{ej.fuente_archivo}] faithfulness={ej.faithfulness} recall={ej.context_recall}: {ej.pregunta[:80]}")


if __name__ == "__main__":
    main()
