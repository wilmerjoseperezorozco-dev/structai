"""
Regresión del desglose jerárquico actividad->insumo en
rag_multi_norma.ask_precios() (Fase 4 del plan de precios, Paso 3,
2026-09-07) -- verifica que preguntar por el desglose de una actividad
real (material/mano de obra/equipo) devuelva los insumos reales
enlazados vía apu_insumos_referencia.actividad_padre_id, no solo el
precio todo-costo plano que ya se entregaba antes de este cambio.

Cobertura real, no toda la base: solo 927 de 4.566 actividades (20.3%,
verificado con SQL directo) tienen al menos un insumo enlazado por FK
-- este archivo usa 4 actividades reales con desglose_confiable=true y
2+ insumos reales, elegidas con SQL directo antes de escribir el test
(no inventadas).

Golpea el pipeline real (Supabase + Groq/OpenAI), no mocks -- mismo
criterio que test_rag_nsr10_regresion.py y
test_buscar_precios_sinonimos.py.

Ejecutar: pytest apps/api/tests/test_desglose_actividad.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

load_dotenv(API_DIR / ".env")

from rag_multi_norma import ask_precios  # noqa: E402

# Mismo motivo que test_rag_nsr10_regresion.py: el LLM redacta la misma
# respuesta correcta con palabras/formato distinto entre corridas.
pytestmark = pytest.mark.flaky(reruns=1, reruns_delay=3)


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    texto_low = texto.lower()
    return any(v.lower() in texto_low for v in variantes)


CASOS_DESGLOSE = [
    pytest.param(
        "Dame el desglose de materiales, mano de obra y equipo de la gravilla lavada",
        ["mano de obra", "arena", "gravilla"],
        id="gravilla-lavada",
    ),
    pytest.param(
        "Cual es el desglose de insumos del ladrillo estructural Santa Fe?",
        ["ladrillo", "arena", "cemento"],
        id="ladrillo-estructural-santa-fe",
    ),
    pytest.param(
        # Frase corta a propósito -- verificado que una pregunta larga en
        # lenguaje natural ("dame el desglose de materiales, mano de obra y
        # equipo de...") diluye el ranking y ni siquiera trae la actividad
        # real en el top-8 para este ítem (mismo gap de retrieval ya
        # documentado en [[project_structai_ragas_precios_baseline]] para
        # "vereda"/"capataz" -- no es un bug nuevo de esta función).
        "desglose del triturado grueso",
        ["triturado", "mano de obra"],
        id="triturado-grueso",
    ),
    pytest.param(
        "Cual es el desglose real de la demolicion de vigas y columnas?",
        ["volqueta", "mano de obra"],
        id="demolicion-vigas-columnas",
    ),
]


@pytest.mark.parametrize("pregunta,variantes_esperadas", CASOS_DESGLOSE)
def test_desglose_actividad_real(pregunta: str, variantes_esperadas: list[str]) -> None:
    resultado = ask_precios(pregunta, top_k=8)
    respuesta = resultado["respuesta"]
    assert _contiene_alguna(respuesta, variantes_esperadas), (
        f"La respuesta no menciona ninguno de {variantes_esperadas} -- "
        f"¿se perdió el desglose real de insumos? Respuesta real: {respuesta!r}"
    )
    # Al menos uno de los contextos recuperados debe traer la marca real
    # de desglose (agregada por _format_precio_context cuando
    # incluir_desglose=True encuentra insumos vía obtener_desglose_actividad).
    contextos = resultado.get("contextos_recuperados", [])
    assert any("desglose real:" in c["contenido"] for c in contextos), (
        "Ningún contexto recuperado trae la marca 'desglose real:' -- "
        "¿el primer resultado tipo='actividad' dejó de resolver su "
        "actividad_id, o la actividad ya no tiene insumos enlazados?"
    )
