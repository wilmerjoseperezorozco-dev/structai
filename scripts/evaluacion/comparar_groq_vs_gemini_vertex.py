"""
Medición real: ¿qué % de cobertura da Groq hoy (pipeline de producción, sin
cambios) frente a Gemini vía Vertex AI, sobre la MISMA pregunta y el MISMO
contexto recuperado? Issue #83 -- evaluar Gemini como tercera opción
aditiva en _llamar_llm_con_respaldo(), medir antes de decidir.

Mismo patrón exacto que comparar_groq_vs_ollama_local.py (issue del roadmap
de Groq vs. Ollama local) -- mismo criterio de comparación tolerante, mismo
formato de salida JSON -- solo cambia el segundo modelo.

Metodología (idéntica a la comparación con Ollama):
1. Muestra estratificada (2 por título/norma) de los 125 casos ya
   verificados a mano en apps/api/tests/test_rag_nsr10_regresion.py.
2. Para cada pregunta, ask() UNA vez (pipeline real: retrieval + re-ranking
   + Groq con respaldo automático a OpenAI) -- "Groq, sin cambios".
3. El MISMO contexto recuperado (ask()["contextos_recuperados"]) se le pasa
   a Gemini vía el SDK oficial google-genai en modo Vertex AI -- así la
   comparación mide solo la diferencia de modelo de síntesis, no de
   retrieval.
4. Mismo criterio tolerante de coincidencia que el resto del proyecto.

Autenticación de Vertex AI (a diferencia de Groq/OpenAI, que usan una API
key estática): OAuth2 vía Application Default Credentials -- el SDK
google-genai con vertexai=True refresca el token internamente, no hace
falta manejarlo a mano. Requiere UNA de estas dos cosas antes de correr
este script:
  (a) `gcloud auth application-default login` (interactivo, para correr
      desde una máquina con gcloud -- ej. Cloud Shell), o
  (b) GOOGLE_APPLICATION_CREDENTIALS apuntando a un archivo JSON de cuenta
      de servicio con el rol "Vertex AI User" en el proyecto structai-507113.
Sin ninguna de las dos, el script falla al primer intento con un error de
autenticación real de Google -- no se intenta adivinar ni omitir esto.

Modelo elegido: gemini-3.8-flash (verificado en vivo 2026-09-30 -- tier
"flash" más reciente sin fecha de retiro anunciada; gemini-2.5-flash SÍ
tiene fecha de retiro anunciada, 20-oct-2026, demasiado cerca de cuando se
haría esta evaluación real -- habría que revisar el modelo si este script
se retoma después de esa fecha).

CONFLICTO REAL DE DEPENDENCIAS encontrado y verificado el 2026-09-30 (no
teórico, reproducido con pip en vivo): `google-genai` exige
`httpx>=0.28.1`, pero `apps/api/requirements.txt` fija `httpx==0.27.2` a
propósito para Supabase (ver fix real de HTTP/2, memoria del proyecto:
RemoteProtocolError en POST/DELETE, resuelto forzando http2=False).
Instalar `google-genai` en el mismo entorno que usa el resto de StructAI
sube httpx a 0.28.1 en silencio -- mismo patrón de riesgo ya documentado
para `ragas` arriba en este archivo (conflicto de versión de `openai`).

Por eso este script, igual que ragas, necesita un VENV APARTE (ej.
"C:/gemini_eval_venv"), NO el entorno de apps/api. Pendiente real, no
resuelto todavía: verificar en ese venv aislado que
`rag_multi_norma.ask()` (que usa supabase-py, sensible a httpx) sigue
funcionando bien con httpx>=0.28.1 antes de confiar en los resultados de
esta comparación -- no se asumió que sí, no se probó todavía por falta de
acceso a credenciales de Vertex AI en este entorno.

Ejecutar (en el venv aislado, una vez creado):
  python -m venv C:/gemini_eval_venv
  C:/gemini_eval_venv/Scripts/python.exe -m pip install -r scripts/evaluacion/requirements.txt
  C:/gemini_eval_venv/Scripts/python.exe scripts/evaluacion/comparar_groq_vs_gemini_vertex.py
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

from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

import rag_multi_norma as rmn  # noqa: E402

# Mismo proyecto/región que el resto de la infraestructura de StructAI en
# GCP (ver CLAUDE.md) -- no se inventa un proyecto nuevo para esto.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "structai-507113")
GCP_REGION = os.environ.get("GCP_REGION", "us-east1")
GEMINI_MODEL = "gemini-3.8-flash"

_ESPACIOS_UNICODE = (" ", " ", " ", " ")


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    texto_low = texto.lower()
    for esp in _ESPACIOS_UNICODE:
        texto_low = texto_low.replace(esp, " ")
    return any(v.lower() in texto_low for v in variantes)


def _cargar_casos_verificados(muestra_por_grupo: int = 2) -> list[dict]:
    """Idéntico a comparar_groq_vs_ollama_local.py -- reusa los mismos 125
    casos verificados a mano, sin inventar ningún hecho nuevo."""
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


def _preguntar_gemini_vertex(client: "genai.Client", contexto: str, pregunta: str) -> tuple[str, float]:
    inicio = time.monotonic()
    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"CONTEXTO NORMATIVO:\n{contexto}\n\nPREGUNTA: {pregunta}",
        config=types.GenerateContentConfig(
            system_instruction=rmn.SYSTEM_PROMPT,
            temperature=0.1,
            max_output_tokens=700,
        ),
    )
    duracion = time.monotonic() - inicio
    return (respuesta.text or ""), duracion


def main() -> None:
    gemini_client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=GCP_REGION)

    casos = _cargar_casos_verificados(muestra_por_grupo=2)
    print(f"Muestra: {len(casos)} preguntas (2 por grupo verificado en test_rag_nsr10_regresion.py)")
    print(f"Modelo Gemini: {GEMINI_MODEL} (proyecto {GCP_PROJECT_ID}, región {GCP_REGION})\n")

    resultados = []
    ok_groq = 0
    ok_gemini = 0

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
            respuesta_gemini, duracion_gemini = _preguntar_gemini_vertex(
                gemini_client, contexto, caso["pregunta"]
            )
            paso_gemini = _contiene_alguna(respuesta_gemini, caso["variantes"])
        except Exception as e:  # Vertex sin credenciales/cuota/red -- se registra, no se detiene la corrida
            respuesta_gemini, duracion_gemini, paso_gemini = f"[ERROR: {e}]", None, False
        ok_gemini += paso_gemini

        print(
            f"    Groq   ({duracion_groq:4.1f}s): {'OK ' if paso_groq else 'FAIL'} — {respuesta_groq[:90]!r}"
        )
        print(
            f"    Gemini ({duracion_gemini if duracion_gemini is None else f'{duracion_gemini:4.1f}s'}): "
            f"{'OK ' if paso_gemini else 'FAIL'} — {respuesta_gemini[:90]!r}"
        )

        resultados.append({
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "variantes_esperadas": caso["variantes"],
            "groq": {"respuesta": respuesta_groq, "paso": paso_groq, "segundos": round(duracion_groq, 2)},
            "gemini": {
                "respuesta": respuesta_gemini,
                "paso": paso_gemini,
                "segundos": round(duracion_gemini, 2) if duracion_gemini is not None else None,
            },
        })

    total = len(casos)
    print("\n" + "=" * 60)
    print(f"Groq (pipeline de producción, sin cambios): {ok_groq}/{total} = {ok_groq/total*100:.0f}%")
    print(f"Gemini ({GEMINI_MODEL} vía Vertex):          {ok_gemini}/{total} = {ok_gemini/total*100:.0f}%")

    duraciones_groq = [r["groq"]["segundos"] for r in resultados]
    duraciones_gemini = [r["gemini"]["segundos"] for r in resultados if r["gemini"]["segundos"] is not None]
    if duraciones_groq:
        print(f"Latencia Groq   -- promedio {sum(duraciones_groq)/len(duraciones_groq):.1f}s, máx {max(duraciones_groq):.1f}s")
    if duraciones_gemini:
        print(f"Latencia Gemini -- promedio {sum(duraciones_gemini)/len(duraciones_gemini):.1f}s, máx {max(duraciones_gemini):.1f}s")

    salida = PROJECT_ROOT / "scripts" / "evaluacion" / f"resultado_groq_vs_gemini_vertex_{GEMINI_MODEL.replace('.', '_')}.json"
    salida.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetalle completo por pregunta: {salida}")


if __name__ == "__main__":
    main()
