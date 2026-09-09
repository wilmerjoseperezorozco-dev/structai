"""
Línea base RAGAS de NSR-10/normas -- 143 preguntas (dataset_baseline_nsr10.py,
crecido de 12 -> 52 -> 103 -> 143 en sesiones sucesivas sin correr RAGAS
completo, por la decisión explícita de diferir la corrida hasta +300
preguntas -- ver [[project_structai_ragas_baseline]] en memoria). Esta
corrida (2026-09-07) se adelanta sobre esa decisión a pedido explícito del
usuario, específicamente para medir las 40 preguntas complejas nuevas
(síntesis cruzada entre títulos, adversariales, compuestas precio+norma,
coloquiales) que no existían en ninguna corrida anterior. Corre sobre el
pipeline real con re-ranking combinado + descomposición de consultas (el
estado actual de rag_multi_norma.ask(), no una versión vieja).

Dos parches de entorno aplicados SOLO para esta corrida, documentados
explícitamente como confound real (no se ocultan):

1. Groq forzado a fallar de inmediato -> respaldo OpenAI directo. Groq
   viene inconsistente/lento hoy (mismo patrón de agotamiento de cuota ya
   documentado); el usuario autorizó explícitamente usar OpenAI (crédito
   real disponible) en vez de esperar a que Groq falle o cuelgue.
2. Cliente Supabase forzado a HTTP/1.1 -- HTTP/2 falla de forma
   consistente y reproducible (httpcore.RemoteProtocolError:
   ConnectionTerminated, 5/5 en pruebas aisladas) contra el RPC
   search_knowledge desde esta máquina Windows. HTTP/1.1 funciona sin
   fallos. No se toca production (Google Cloud Run desde 2026-09-01,
   antes DigitalOcean -- en ambos casos Linux, ruta de red distinta) --
   esto puede ser específico de esta máquina/ISP.

Ejecutar: C:\\ragas_venv\\Scripts\\python.exe ragas_52preguntas.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\HP\Desktop\optimizacion para negocios en el atlantico\tubara\construdata")
sys.path.insert(0, str(ROOT / "apps" / "api"))
sys.path.insert(0, str(ROOT / "packages" / "construdata"))
sys.path.insert(0, str(ROOT / "scripts" / "evaluacion"))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

import httpx
from supabase import create_client, ClientOptions

import rag_multi_norma
from openai import APIConnectionError as GroqAPIConnectionError

def _groq_falla_de_inmediato(*args, **kwargs):
    raise GroqAPIConnectionError(request=None)

rag_multi_norma.groq_client.chat.completions.create = _groq_falla_de_inmediato

_http1_client = httpx.Client(http2=False, timeout=60)
rag_multi_norma.sb = create_client(
    os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"],
    options=ClientOptions(httpx_client=_http1_client),
)

from rag_multi_norma import ask
from dataset_baseline_nsr10 import CASOS_BASELINE

SCRIPT_DIR = Path(__file__).resolve().parent
# Antes hardcodeado a "baseline_2026-08-27_52preguntas_*" -- bug real
# encontrado 2026-09-07: el dataset ya creció a 143 preguntas (52 -> 103
# -> 143 en sesiones sucesivas sin correr RAGAS completo, por la decisión
# de diferir hasta +300), y ese nombre fijo habría SOBREESCRITO el
# baseline histórico de 52 preguntas del 2026-08-27 con datos de una
# corrida distinta bajo el mismo nombre. Corregido a nombre derivado del
# n real + fecha real de la corrida, para que cada baseline quede
# identificado por lo que realmente mide (mismo principio que ya usa
# ragas_precios.py con su constante FECHA).
FECHA = "2026-09-09"
N_PREGUNTAS = len(CASOS_BASELINE)


def construir_muestras():
    muestras = []
    for i, caso in enumerate(CASOS_BASELINE, 1):
        print(f"  [{i:02d}/{len(CASOS_BASELINE)}] preguntando: {caso['id']} ...", flush=True)
        resultado = ask(caso["pregunta"], top_k=10)
        contextos = [c["contenido"] for c in resultado.get("contextos_recuperados", [])]
        muestras.append({
            "id": caso["id"],
            "user_input": caso["pregunta"],
            "response": resultado["respuesta"],
            "retrieved_contexts": contextos,
            "reference": caso["ground_truth"],
        })
    return muestras


def main():
    print(f"Construyendo {len(CASOS_BASELINE)} muestras reales (llamadas a ask(), Groq desactivado -> OpenAI directo)...")
    muestras = construir_muestras()

    out_path = SCRIPT_DIR / f"baseline_{FECHA}_{N_PREGUNTAS}preguntas_muestras.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for m in muestras:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"Muestras guardadas en {out_path}")

    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    juez_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"]))
    juez_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"]))

    dataset = EvaluationDataset.from_list(muestras)

    print(f"Evaluando con RAGAS (n={len(muestras)}): faithfulness, answer_relevancy, context_precision, context_recall...")
    resultado = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=juez_llm,
        embeddings=juez_embeddings,
    )

    df = resultado.to_pandas()
    out_csv = SCRIPT_DIR / f"baseline_{FECHA}_{N_PREGUNTAS}preguntas_scorecard.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")

    # to_pandas() de RAGAS no conserva campos custom como "id" (mismo bug
    # real encontrado en ragas_precios.py 2026-09-07) -- se reconstruye la
    # categoría por POSICIÓN, no por columna. Prefijo nuevo (SINT-/ADV-/
    # COMP-/COLOQ-) vs. cualquier otro id = pregunta "original" (de las 103
    # ya existentes antes de esta ampliación).
    PREFIJOS_NUEVOS = ("SINT-", "ADV-", "COMP-", "COLOQ-")
    def _categoria(id_: str) -> str:
        for p in PREFIJOS_NUEVOS:
            if id_.startswith(p):
                return p.rstrip("-")
        return "original"
    df["categoria"] = [_categoria(m["id"]) for m in muestras]

    metricas = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    resumen_filas = []
    for metrica in metricas:
        if metrica in df.columns:
            resumen_filas.append({
                "categoria": "TODAS",
                "metrica": metrica,
                "media": round(df[metrica].mean(), 3),
                "std": round(df[metrica].std(ddof=1), 3),
                "min": round(df[metrica].min(), 3),
                "max": round(df[metrica].max(), 3),
                "n": len(df[metrica]),
            })
    for categoria, grupo in df.groupby("categoria"):
        for metrica in metricas:
            if metrica in grupo.columns:
                resumen_filas.append({
                    "categoria": categoria,
                    "metrica": metrica,
                    "media": round(grupo[metrica].mean(), 3),
                    "std": round(grupo[metrica].std(ddof=1), 3) if len(grupo) > 1 else 0.0,
                    "min": round(grupo[metrica].min(), 3),
                    "max": round(grupo[metrica].max(), 3),
                    "n": len(grupo[metrica]),
                })

    import csv as _csv
    out_resumen = SCRIPT_DIR / f"baseline_{FECHA}_{N_PREGUNTAS}preguntas_resumen.csv"
    with out_resumen.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=["categoria", "metrica", "media", "std", "min", "max", "n"])
        writer.writeheader()
        writer.writerows(resumen_filas)

    print(f"\n=== SCORECARD (media ± std, n={len(df)} preguntas) ===")
    for fila in resumen_filas:
        if fila["categoria"] == "TODAS":
            print(f"  {fila['metrica']}: {fila['media']:.3f} ± {fila['std']:.3f}  (min={fila['min']:.3f}, max={fila['max']:.3f})")
    print(f"\n=== Por categoría ===")
    for fila in resumen_filas:
        if fila["categoria"] != "TODAS":
            print(f"  {fila['categoria']:10s} {fila['metrica']:18s}: {fila['media']:.3f} (n={fila['n']})")
    print(f"\nDetalle por pregunta: {out_csv}")
    print(f"Resumen media±std (general + por categoría): {out_resumen}")


if __name__ == "__main__":
    main()
