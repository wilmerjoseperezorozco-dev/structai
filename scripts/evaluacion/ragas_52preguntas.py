"""
Línea base RAGAS ampliada -- 52 preguntas (12 originales + 40 nuevas de
D/E/G completos y ampliaciones de A/B/C/F/H/I/J/K/NTC/SGSST), corriendo
sobre el pipeline real con re-ranking combinado + descomposición de
consultas (el estado actual de rag_multi_norma.ask(), no una versión vieja).

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

    out_path = SCRIPT_DIR / "baseline_2026-08-27_52preguntas_muestras.jsonl"
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
    out_csv = SCRIPT_DIR / "baseline_2026-08-27_52preguntas_scorecard.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")

    metricas = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    resumen_filas = []
    for metrica in metricas:
        if metrica in df.columns:
            resumen_filas.append({
                "metrica": metrica,
                "media": round(df[metrica].mean(), 3),
                "std": round(df[metrica].std(ddof=1), 3),
                "min": round(df[metrica].min(), 3),
                "max": round(df[metrica].max(), 3),
                "n": len(df[metrica]),
            })
    import csv as _csv
    out_resumen = SCRIPT_DIR / "baseline_2026-08-27_52preguntas_resumen.csv"
    with out_resumen.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=["metrica", "media", "std", "min", "max", "n"])
        writer.writeheader()
        writer.writerows(resumen_filas)

    print(f"\n=== SCORECARD (media ± std, n={len(df)} preguntas) ===")
    for fila in resumen_filas:
        print(f"  {fila['metrica']}: {fila['media']:.3f} ± {fila['std']:.3f}  (min={fila['min']:.3f}, max={fila['max']:.3f})")
    print(f"\nDetalle por pregunta: {out_csv}")
    print(f"Resumen media±std: {out_resumen}")


if __name__ == "__main__":
    main()
