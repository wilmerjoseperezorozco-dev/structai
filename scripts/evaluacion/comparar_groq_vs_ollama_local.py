"""
Medición real: ¿qué % de cobertura da Groq hoy (pipeline de producción, sin
cambios) frente a un modelo local vía Ollama, sobre la MISMA pregunta y el
MISMO contexto recuperado? Pedido explícito del usuario al evaluar la idea 2
(cascada Groq -> Ollama local -> OpenAI) del roadmap: "me lo dices Groq sigue
cubriendo XXX% sin cambios, LLM local cubre XXX%".

Metodología:
1. Toma una muestra estratificada (2 por título/norma) de los 125 casos ya
   verificados a mano en apps/api/tests/test_rag_nsr10_regresion.py
   (pregunta + variantes_esperadas + id) -- se reutilizan, no se inventa
   ningún hecho nuevo para esta medición.
2. Para cada pregunta, se llama ask() UNA vez (pipeline real de producción:
   retrieval + re-ranking + Groq con respaldo automático a OpenAI si Groq
   falla) -- esto da la respuesta "Groq, sin cambios" tal como responde hoy
   structai.online.
3. Se reconstruye el contexto recuperado desde
   ask()["contextos_recuperados"] (agregado 2026-08-27 para RAGAS, se
   reutiliza aquí) y se le pasa ESE MISMO contexto a un modelo local vía
   Ollama (http://localhost:11434, API compatible con OpenAI) -- así la
   comparación mide solo la diferencia de modelo de síntesis, no de
   retrieval.
4. Cada respuesta (Groq y local) se compara contra variantes_esperadas con
   el mismo criterio tolerante (normaliza mayúsculas, coma/punto decimal,
   espacios unicode) que ya usan los tests de regresión reales del proyecto.

Nota metodológica honesta: el contexto reconstruido en el paso 3 no incluye
la advertencia de vigencia que _format_chunk_context() antepone a un chunk
derogado -- simplificación aceptable para esta medición exploratoria, no
para producción.

Nota sobre el modelo local: el usuario pidió "Ollama Mistral", pero el único
modelo ya descargado en esta máquina es llama3.1:8b (verificado con
`ollama list` antes de escribir este script) -- se usa ese, no se inventa
que Mistral está disponible. Si se quiere Mistral específicamente, se baja
aparte (~4GB) y se cambia OLLAMA_MODEL_LOCAL abajo.

Ejecutar: python scripts/evaluacion/comparar_groq_vs_ollama_local.py
Requiere: `ollama serve` corriendo en localhost:11434 (ya estaba corriendo
al escribir este script).
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "api"))

from openai import OpenAI  # noqa: E402

import rag_multi_norma as rmn  # noqa: E402

OLLAMA_MODEL_LOCAL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

_ESPACIOS_UNICODE = (" ", " ", " ", " ")


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    texto_low = texto.lower()
    for esp in _ESPACIOS_UNICODE:
        texto_low = texto_low.replace(esp, " ")
    return any(v.lower() in texto_low for v in variantes)


def _cargar_casos_verificados(muestra_por_grupo: int = 2) -> list[dict]:
    """Importa test_rag_nsr10_regresion.py y extrae todas las listas
    CASOS_TITULO_* (pytest.param ya verificados a mano), muestreando
    `muestra_por_grupo` de cada una para tener cobertura across títulos sin
    correr los 125 casos completos (costo/tiempo real de 2 LLMs por caso)."""
    spec = importlib.util.spec_from_file_location(
        "test_rag_nsr10_regresion",
        PROJECT_ROOT / "apps" / "api" / "tests" / "test_rag_nsr10_regresion.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    muestra = []
    for nombre in dir(mod):
        if not nombre.startswith("CASOS_"):
            continue
        grupo = getattr(mod, nombre)
        for param in grupo[:muestra_por_grupo]:
            pregunta, variantes = param.values
            muestra.append({"id": param.id, "pregunta": pregunta, "variantes": variantes})
    return muestra


def _reconstruir_contexto(contextos_recuperados: list[dict]) -> str:
    partes = [
        f"[{c['norma']} {c['seccion']}]\n{c['contenido']}" for c in contextos_recuperados
    ]
    return "\n\n---\n\n".join(partes)


def _preguntar_ollama_local(client: OpenAI, contexto: str, pregunta: str) -> tuple[str, float]:
    inicio = time.monotonic()
    respuesta = client.chat.completions.create(
        model=OLLAMA_MODEL_LOCAL,
        messages=[
            {"role": "system", "content": rmn.SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {pregunta}"},
        ],
        temperature=0.1,
        max_tokens=700,
    )
    duracion = time.monotonic() - inicio
    return (respuesta.choices[0].message.content or ""), duracion


def main() -> None:
    ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    casos = _cargar_casos_verificados(muestra_por_grupo=2)
    print(f"Muestra: {len(casos)} preguntas (2 por grupo verificado en test_rag_nsr10_regresion.py)\n")

    resultados = []
    ok_groq = 0
    ok_local = 0

    for i, caso in enumerate(casos, 1):
        print(f"[{i}/{len(casos)}] {caso['id']}")

        inicio_groq = time.monotonic()
        resultado_ask = rmn.ask(caso["pregunta"])
        duracion_groq = time.monotonic() - inicio_groq
        respuesta_groq = resultado_ask["respuesta"]
        paso_groq = _contiene_alguna(respuesta_groq, caso["variantes"])
        ok_groq += paso_groq

        contexto = _reconstruir_contexto(resultado_ask["contextos_recuperados"])
        try:
            respuesta_local, duracion_local = _preguntar_ollama_local(
                ollama_client, contexto, caso["pregunta"]
            )
            paso_local = _contiene_alguna(respuesta_local, caso["variantes"])
        except Exception as e:  # Ollama caído/timeout -- se registra, no se detiene la corrida
            respuesta_local, duracion_local, paso_local = f"[ERROR: {e}]", None, False
        ok_local += paso_local

        print(
            f"    Groq  ({duracion_groq:4.1f}s): {'OK ' if paso_groq else 'FAIL'} — {respuesta_groq[:90]!r}"
        )
        print(
            f"    Local ({duracion_local if duracion_local is None else f'{duracion_local:4.1f}s'}): "
            f"{'OK ' if paso_local else 'FAIL'} — {respuesta_local[:90]!r}"
        )

        resultados.append({
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "variantes_esperadas": caso["variantes"],
            "groq": {"respuesta": respuesta_groq, "paso": paso_groq, "segundos": round(duracion_groq, 2)},
            "local": {
                "respuesta": respuesta_local,
                "paso": paso_local,
                "segundos": round(duracion_local, 2) if duracion_local is not None else None,
            },
        })

    total = len(casos)
    print("\n" + "=" * 60)
    print(f"Groq (pipeline de producción, sin cambios): {ok_groq}/{total} = {ok_groq/total*100:.0f}%")
    print(f"Local ({OLLAMA_MODEL_LOCAL} vía Ollama):     {ok_local}/{total} = {ok_local/total*100:.0f}%")

    duraciones_groq = [r["groq"]["segundos"] for r in resultados]
    duraciones_local = [r["local"]["segundos"] for r in resultados if r["local"]["segundos"] is not None]
    if duraciones_groq:
        print(f"Latencia Groq  -- promedio {sum(duraciones_groq)/len(duraciones_groq):.1f}s, máx {max(duraciones_groq):.1f}s")
    if duraciones_local:
        print(f"Latencia Local -- promedio {sum(duraciones_local)/len(duraciones_local):.1f}s, máx {max(duraciones_local):.1f}s")

    salida = PROJECT_ROOT / "scripts" / "evaluacion" / f"resultado_groq_vs_ollama_local_{OLLAMA_MODEL_LOCAL.replace(':', '_')}.json"
    salida.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetalle completo por pregunta: {salida}")


if __name__ == "__main__":
    main()
