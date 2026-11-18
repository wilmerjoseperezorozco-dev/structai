"""
Aviso de vigencia sin respaldo en el contexto (hallazgo #261, 2026-11-17). Sin LLM ni red.

La regla 8 del SYSTEM_PROMPT citaba la frase literal "⚠️ NORMA DEROGADA/MODIFICADA". qwen2.5:7b (CI nocturno, sabotaje
del contexto) la copiaba en el 43 % de sus respuestas sobre la NSR-10 (91 de 214), aunque ningún fragmento de la
NSR-10 está marcado como no vigente en normas_registro. Además, esa frase exacta nunca puede salir de
_format_chunk_context(), que escribe "⚠️ NORMA DEROGADA TOTAL", "⚠️ NORMA MODIFICADA", etc.

Se corrigen dos cosas y se prueban aquí:
1. Las reglas ya no contienen la frase literal (un modelo pequeño la imita).
2. Guarda determinista: si ningún fragmento trae aviso de vigencia, se quitan de la respuesta las líneas que anuncian
   una norma derogada o modificada. Si el contexto sí lo trae, la respuesta no se toca.

Ejecutar: pytest apps/api/tests/test_aviso_vigencia_sin_respaldo.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
load_dotenv(API_DIR / ".env")

import rag_multi_norma as r  # noqa: E402
from rag_multi_norma import ChunkResult, _format_chunk_context, _quitar_aviso_vigencia_sin_respaldo  # noqa: E402

VIGENTE = ChunkResult(chunk_id="1", norma="NSR-10", seccion="F.4.3", contenido="φt = 0,75 para rotura en sección neta.",
                      score=1.0, estado_vigencia="vigente")
SIN_VINCULAR = ChunkResult(chunk_id="2", norma="NSR-10", seccion="H.4.2", contenido="Profundidad de raíces 6 m.",
                           score=1.0, estado_vigencia=None)
DEROGADA = ChunkResult(chunk_id="3", norma="Resolución 1096 de 2000", seccion="B.2", contenido="Dotación neta...",
                       score=1.0, estado_vigencia="derogada_total", derogada_por="Resolución 0330 de 2017")

# Respuesta real (recortada) de qwen2.5:7b en el sabotaje del #261.
RESPUESTA_CON_AVISO_INVENTADO = (
    "Según F.4.3, el coeficiente es φt = 0,75.\n\n"
    "⚠️ NORMA DEROGADA/MODIFICADA: Asegúrate de verificar la vigencia de la norma NSR-10, ya que puede haber "
    "actualizaciones o derogaciones que afecten la información proporcionada."
)


def _contexto(*chunks: ChunkResult) -> str:
    return "\n\n---\n\n".join(_format_chunk_context(c) for c in chunks)


def test_quita_aviso_inventado_si_ningun_fragmento_lo_trae():
    salida = _quitar_aviso_vigencia_sin_respaldo(RESPUESTA_CON_AVISO_INVENTADO, _contexto(VIGENTE, SIN_VINCULAR))
    assert salida == "Según F.4.3, el coeficiente es φt = 0,75."


def test_conserva_aviso_si_el_contexto_trae_una_norma_derogada():
    respuesta = "⚠️ NORMA DEROGADA TOTAL — reemplazada por Resolución 0330 de 2017.\n\nLa dotación neta es..."
    assert _quitar_aviso_vigencia_sin_respaldo(respuesta, _contexto(VIGENTE, DEROGADA)) == respuesta


def test_no_toca_respuestas_sin_aviso():
    respuesta = "La deriva máxima es 1,0 % de la altura de piso.\n\nVer A.6.4."
    assert _quitar_aviso_vigencia_sin_respaldo(respuesta, _contexto(VIGENTE)) == respuesta


def test_variantes_de_aviso_inventado():
    for linea in ("⚠️ NORMA MODIFICADA: verifique.", "Nota: norma derogada / modificada, consulte.",
                  "**⚠️ NORMA DEROGADA/MODIFICADA**"):
        assert _quitar_aviso_vigencia_sin_respaldo(f"Valor: 25,5.\n{linea}", _contexto(VIGENTE)) == "Valor: 25,5."


def test_no_quita_menciones_legitimas_de_vigencia_sin_el_formato_de_aviso():
    """La guarda solo quita el aviso con forma de alerta ("NORMA DEROGADA/MODIFICADA"), no cualquier mención: una
    respuesta que explica que la NSR-10 fue modificada por un decreto, si lo dice el contexto, no debe perderse."""
    respuesta = "El Decreto 1711 de 2021 actualizó el Apéndice A-4."
    assert _quitar_aviso_vigencia_sin_respaldo(respuesta, _contexto(VIGENTE)) == respuesta


def test_contexto_formateado_marca_el_aviso_que_reconoce_la_guarda():
    assert r._RX_AVISO_EN_CONTEXTO.search(_contexto(DEROGADA))
    assert not r._RX_AVISO_EN_CONTEXTO.search(_contexto(VIGENTE, SIN_VINCULAR))


def test_las_reglas_no_contienen_la_frase_literal_que_el_modelo_imitaba():
    for nombre in dir(r):
        valor = getattr(r, nombre)
        if isinstance(valor, str) and "INSTRUCCIONES" in valor.upper():
            assert "DEROGADA/MODIFICADA" not in valor, nombre
    for prompt in r.MOTOR_SYSTEM_PROMPT.values():
        assert "DEROGADA/MODIFICADA" not in prompt


def test_generar_respuesta_aplica_la_guarda(monkeypatch):
    monkeypatch.setattr(r, "_llamar_llm_con_respaldo", lambda messages, max_tokens_groq=700: RESPUESTA_CON_AVISO_INVENTADO)
    assert r._generar_respuesta(_contexto(VIGENTE), "¿φt?") == "Según F.4.3, el coeficiente es φt = 0,75."
