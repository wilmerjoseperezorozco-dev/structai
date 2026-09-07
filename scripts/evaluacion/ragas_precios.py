"""
Línea base RAGAS de precios/APU -- 55 preguntas (dataset_baseline_precios.py),
corriendo sobre rag_multi_norma.ask_precios() real (texto completo español +
trigram + expansión de sinónimos regionales, sin mocks).

Esta es la corrida "ANTES" del Paso 3 del plan de Fase 4 (desglose
jerárquico actividad->insumo vía actividad_padre_id) -- se guarda como
baseline real para comparar contra una segunda corrida "DESPUÉS" una vez
implementado ese paso, en vez de asumir que agregar el desglose mejora las
métricas sin medirlo.

Mismos dos parches de entorno que ragas_52preguntas.py, documentados ahí
como confound real (no se ocultan, mismo motivo):

1. Groq forzado a fallar de inmediato -> respaldo OpenAI directo (Groq
   inconsistente/lento hoy, usuario autorizó gastar crédito de OpenAI para
   verificación real en vez de esperar a Groq).
2. Cliente Supabase forzado a HTTP/1.1 (HTTP/2 falla de forma consistente
   desde esta máquina Windows contra los RPC de Supabase).

Ejecutar: C:\\ragas_venv\\Scripts\\python.exe ragas_precios.py
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

from rag_multi_norma import ask_precios
from dataset_baseline_precios import CASOS_BASELINE_PRECIOS

SCRIPT_DIR = Path(__file__).resolve().parent
FECHA = "2026-09-07"


def construir_muestras():
    muestras = []
    for i, caso in enumerate(CASOS_BASELINE_PRECIOS, 1):
        print(f"  [{i:02d}/{len(CASOS_BASELINE_PRECIOS)}] preguntando: {caso['id']} ...", flush=True)
        resultado = ask_precios(caso["pregunta"], top_k=8)
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
    print(f"Construyendo {len(CASOS_BASELINE_PRECIOS)} muestras reales (llamadas a ask_precios(), Groq desactivado -> OpenAI directo)...")
    muestras = construir_muestras()

    out_path = SCRIPT_DIR / f"baseline_{FECHA}_precios_muestras.jsonl"
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
    out_csv = SCRIPT_DIR / f"baseline_{FECHA}_precios_scorecard.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")

    # to_pandas() de RAGAS SOLO conserva user_input/retrieved_contexts/
    # response/reference + las métricas -- descarta cualquier campo custom
    # como "id" que iba en las muestras originales (bug real encontrado en
    # la primera corrida 2026-09-07: df["id"] no existe, KeyError). En vez
    # de la columna "id", se reconstruye el prefijo de categoría por
    # POSICIÓN: EvaluationDataset.from_list() preserva el orden de la
    # lista de entrada, así que la fila i del resultado corresponde a
    # muestras[i].
    df["categoria"] = [m["id"].split("-")[0] + "-" + m["id"].split("-")[1] for m in muestras]

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
    out_resumen = SCRIPT_DIR / f"baseline_{FECHA}_precios_resumen.csv"
    with out_resumen.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=["categoria", "metrica", "media", "std", "min", "max", "n"])
        writer.writeheader()
        writer.writerows(resumen_filas)

    print(f"\n=== SCORECARD (media ± std, n={len(df)} preguntas) ===")
    for fila in resumen_filas:
        if fila["categoria"] == "TODAS":
            print(f"  {fila['metrica']}: {fila['media']:.3f} ± {fila['std']:.3f}  (min={fila['min']:.3f}, max={fila['max']:.3f})")
    print(f"\nDetalle por pregunta: {out_csv}")
    print(f"Resumen media±std (general + por categoría): {out_resumen}")


if __name__ == "__main__":
    main()
