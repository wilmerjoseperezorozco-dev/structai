"""
Línea base RAGAS del pipeline RAG real (packages/construdata/rag_multi_norma.py)
contra las 12 preguntas ya verificadas de NSR-10 Títulos A/B/C (ver
dataset_baseline_nsr10.py -- mismas preguntas de
apps/api/tests/test_rag_nsr10_regresion.py, no inventadas para esto).

Por qué esto existe: antes de gastar en cualquier mejora real (embeddings
de OpenAI, re-ranking, HyDE, GraphRAG...), medir con números objetivos si
el pipeline actual falla y en qué dimensión exacta -- fidelidad
(¿la respuesta inventa algo que el contexto no dice?), relevancia de la
respuesta, precisión y cobertura del contexto recuperado. Sin esta línea
base, cualquier cambio futuro es "se siente mejor", no verificable.

Ejecutar (venv aislado -- ver requirements.txt de esta carpeta):
  C:\\ragas_venv\\Scripts\\python.exe scripts/evaluacion/ragas_baseline_nsr10.py

Costo real: cada pregunta hace 1 llamada real a Groq/OpenAI para generar
la respuesta (ya la hace `ask()` en producción) + varias llamadas más del
LLM-juez de RAGAS por métrica (faithfulness descompone la respuesta en
afirmaciones y verifica cada una contra el contexto). Con 12 preguntas y
4 métricas esto es real pero acotado -- no correr esto en cada push de
CI, es una herramienta de medición puntual, no un test de regresión.
"""
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))
sys.path.insert(0, str(ROOT / "packages" / "construdata"))
sys.path.insert(0, str(SCRIPT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

from dataset_baseline_nsr10 import CASOS_BASELINE
from rag_multi_norma import ask


def construir_muestras():
    """Llama a ask() de verdad para cada pregunta -- mismo pipeline que
    /ask en producción, ninguna llamada simulada. Usa contextos_recuperados
    (agregado a ask() el 2026-08-27 específicamente para esto -- ver el
    comentario en rag_multi_norma.py)."""
    muestras = []
    for caso in CASOS_BASELINE:
        print(f"  preguntando: {caso['id']} ...")
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
    print(f"Construyendo {len(CASOS_BASELINE)} muestras reales (llamadas a ask())...")
    muestras = construir_muestras()

    # Nombres genéricos aquí a propósito (sobrescriben la corrida
    # anterior) -- después de una corrida que valga la pena conservar
    # como referencia, copiar/renombrar a mano a
    # "baseline_<fecha>_muestras.jsonl" / "..._scorecard.csv" (ver
    # baseline_2026-08-27_*.* como ejemplo real, la primera línea base).
    out_path = SCRIPT_DIR / "_muestras.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for m in muestras:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"Muestras guardadas en {out_path} (por si RAGAS falla, no repetir las llamadas reales a Groq/OpenAI)")

    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    # LLM-juez: OpenAI real (gpt-4o-mini, barato) -- separado del
    # Groq/OpenAI que ya usa ask() para generar la respuesta. El usuario
    # ya autorizó gastar cupo real de OpenAI para verificación
    # (ver memoria: feedback_verificacion_sobre_costo).
    juez_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"]))
    juez_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"]))

    dataset = EvaluationDataset.from_list(muestras)

    # Instancias ya construidas de ragas.metrics (verificado con
    # `_required_columns` antes de escribir esto -- faithfulness/
    # answer_relevancy no necesitan "reference"; context_precision/
    # context_recall sí, por eso el dataset trae "reference" en las 12
    # muestras).
    print("Evaluando con RAGAS (faithfulness, answer_relevancy, context_precision, context_recall)...")
    resultado = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=juez_llm,
        embeddings=juez_embeddings,
    )

    df = resultado.to_pandas()
    out_csv = SCRIPT_DIR / "_resultados.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")

    # Media sola no dice si una diferencia entre corridas es real o es
    # varianza entre preguntas -- con n=12/n=50 la desviación estándar entre
    # preguntas de la MISMA corrida suele ser grande (0.15-0.27 en las
    # corridas ya medidas 2026-08-27), a veces mayor que la diferencia entre
    # corridas que se está tratando de atribuir a un cambio de código. Nunca
    # reportar solo el promedio sin esto -- fue exactamente el motivo por el
    # que una caída puntual se leyó primero como regresión real y resultó
    # ser ruido (ver [[project_structai_ragas_baseline]]).
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
    out_resumen = SCRIPT_DIR / "_resumen.csv"
    with out_resumen.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=["metrica", "media", "std", "min", "max", "n"])
        writer.writeheader()
        writer.writerows(resumen_filas)

    print(f"\n=== SCORECARD (media ± desviación estándar, n={len(df)} preguntas) ===")
    for fila in resumen_filas:
        print(f"  {fila['metrica']}: {fila['media']:.3f} ± {fila['std']:.3f}  (min={fila['min']:.3f}, max={fila['max']:.3f})")
    print(f"\nDetalle por pregunta guardado en {out_csv}")
    print(f"Resumen media±std guardado en {out_resumen}")


if __name__ == "__main__":
    main()
