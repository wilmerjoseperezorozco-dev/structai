"""
Regresión del RAG NSR-10 — hechos verificados manualmente contra el PDF
oficial durante las rondas de re-extracción verbatim de Títulos A y B
(2026-08-01). Antes de esto, cada verificación vivía en un script
_audit_piloto_*.py que se creaba y se borraba en la sesión — una corrección
de hoy podía romperse en silencio mañana al insertar contenido nuevo, sin
que nadie se enterara hasta que un usuario preguntara mal.

Estos tests golpean el pipeline real (Supabase pgvector + Groq), no mocks —
verifican que el contenido siga existiendo Y siga siendo recuperado en el
top-k, que es exactamente el modo de falla real encontrado varias veces
esta sesión (contenido correcto en la base pero perdido contra un chunk de
otro título en la búsqueda por similitud).

Costo/latencia: cada caso hace una llamada real a Groq — no son gratis ni
instantáneos. Si esto empieza a doler en tiempo de CI, migrar a un marker
separado (`@pytest.mark.rag_regresion`) para correrlos aparte del resto.

Ejecutar: pytest apps/api/tests/test_rag_nsr10_regresion.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

# rag_multi_norma.py lee credenciales de os.environ a nivel de módulo — a
# diferencia de test_endpoints.py, este archivo no importa main.py (que ya
# carga el .env como efecto colateral), así que hay que cargarlo explícito.
# En CI (test-api de ci.yml) estas vienen de GitHub Secrets, no de un .env.
load_dotenv(API_DIR / ".env")

from rag_multi_norma import ask  # noqa: E402


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    """True si el texto contiene al menos una de las variantes (insensible a
    mayúsculas) — tolera que el LLM use coma o punto decimal, o pequeñas
    diferencias de formato, sin dejar de exigir el hecho numérico real."""
    texto_low = texto.lower()
    return any(v.lower() in texto_low for v in variantes)


CASOS_TITULO_B = [
    pytest.param(
        "El Titulo B trata directamente las fuerzas sismicas de diseño?",
        ["no", "título a", "titulo a"],
        id="B-viento-no-es-sismo",
    ),
    pytest.param(
        "Segun la tabla de carga viva de la NSR-10, cual es la carga viva para estanterias en una biblioteca?",
        ["7.0", "7,0"],
        id="B-biblioteca-estanterias-7kNm2",
    ),
    pytest.param(
        "Cual es la carga minima de diseño por viento en el SPRFV segun la NSR-10?",
        ["0.40", "0,40", "0.4 ", "0,4 "],
        id="B-viento-minimo-040",
    ),
]

CASOS_TITULO_A = [
    pytest.param(
        "Cuales son los 4 sistemas estructurales de resistencia sismica que reconoce la NSR-10?",
        ["muros de carga", "sistema dual"],
        id="A-4-sistemas-estructurales",
    ),
    pytest.param(
        "En el analisis dinamico, el cortante dinamico total en la base no puede ser menor a que porcentaje del cortante de la fuerza horizontal equivalente, para estructuras regulares e irregulares?",
        ["80", "90"],
        id="A-ajuste-dinamico-80-90",
    ),
    pytest.param(
        "Cuales son los valores de Aa y Av para Barranquilla segun la NSR-10?",
        ["0.10", "0,10"],
        id="A-Aa-Av-Barranquilla",
    ),
    pytest.param(
        "Cual es la deriva maxima permitida como porcentaje de la altura de piso para una estructura de concreto reforzado?",
        ["1.0%", "1%", "1,0%", "0.010", "0,010"],
        id="A-deriva-maxima-1-porciento",
    ),
]


@pytest.mark.parametrize("pregunta,variantes_esperadas", CASOS_TITULO_B + CASOS_TITULO_A)
def test_respuesta_contiene_hecho_verificado(pregunta: str, variantes_esperadas: list[str]) -> None:
    resultado = ask(pregunta, top_k=4)
    respuesta = resultado["respuesta"]
    assert _contiene_alguna(respuesta, variantes_esperadas), (
        f"Ninguna de {variantes_esperadas} apareció en la respuesta.\n"
        f"Pregunta: {pregunta}\nRespuesta real: {respuesta}"
    )
