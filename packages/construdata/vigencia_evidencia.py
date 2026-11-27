"""Parámetros de evidencia para afirmar la vigencia de una norma (#261). Una sola regla para el contexto del RAG
(rag_multi_norma.aviso_vigencia) y para el plugin determinista de vigencia (plugins_chat.ejecutar_vigencia).

Decir que una norma vigente está derogada es un error legal grave para el usuario. Por eso el estado del registro
(normas_registro.estado_vigencia) solo se publica tal cual si trae su respaldo:

  Respaldo = texto de al menos 8 caracteres que lleva un número (identifica el acto o los artículos).
  derogada_total   → la norma que la reemplaza (derogada_por) o el alcance citado (alcance_derogacion).
  derogada_parcial → el alcance (qué artículos o capítulos); sin él no se sabe qué parte perdió vigencia.
  modificada       → no es derogación: se publica, y se aclara que sigue vigente en lo no modificado.
  vigente / None   → sin aviso.

Sin respaldo, o con un estado que no se reconoce, se publica "no confirmado", que no afirma nada.
"""
from __future__ import annotations

from typing import Optional

MIN_CARACTERES_RESPALDO = 8     # un alcance más corto ("sí", "parcial") no identifica el acto ni los artículos
# Un respaldo debe identificar un acto o un artículo, así que lleva al menos un número ("Resolución 0330 de 2017",
# "Capítulo 2", "art. 249"). "Derogada." o "superada por ediciones posteriores" no son respaldo.
ESTADOS = ("vigente", "derogada_total", "derogada_parcial", "modificada", "desconocido")


def con_respaldo(texto: Optional[str]) -> bool:
    t = str(texto or "").strip()
    return len(t) >= MIN_CARACTERES_RESPALDO and any(ch.isdigit() for ch in t)


def estado_publicable(estado: Optional[str], derogada_por: Optional[str] = None,
                      alcance: Optional[str] = None) -> Optional[str]:
    """Estado que se puede afirmar ante el usuario: None (vigente), 'derogada_total', 'derogada_parcial', 'modificada'
    o 'desconocido' (no confirmado)."""
    if estado in (None, "vigente"):
        return None
    if estado == "derogada_total" and (con_respaldo(derogada_por) or con_respaldo(alcance)):
        return "derogada_total"
    if estado == "derogada_parcial" and con_respaldo(alcance):
        return "derogada_parcial"
    if estado == "modificada":
        return "modificada"
    return "desconocido"
