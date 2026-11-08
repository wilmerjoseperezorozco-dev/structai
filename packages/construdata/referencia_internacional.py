"""Reglas para usar fuentes de otros países como referencia comparada (issue #110).

Convención de `norma_ref` para un fragmento extranjero:  ``INT/<PAIS>/<AÑO> — <nombre>``
(ejemplo: ``INT/US/1980 — USBM RI 8507``). El prefijo ``INT/`` marca el fragmento como
«referencia internacional»: el RAG lo etiqueta en el contexto y obliga al modelo a no
presentarlo como exigencia colombiana. Hoy no hay fragmentos con este prefijo en la base:
el módulo prepara la regla antes de ingestar.
"""
from __future__ import annotations

import re

PREFIJO = "INT/"
_PATRON = re.compile(r"^INT/(?P<pais>[A-Z]{2})/(?P<anio>\d{4}) — (?P<nombre>\S.*)$")

AVISO_CONTEXTO = "🌐 REFERENCIA INTERNACIONAL — no es norma colombiana ni es obligatoria en Colombia"

REGLA_PROMPT = """
REFERENCIAS INTERNACIONALES: algunos fragmentos del contexto llevan la marca
"🌐 REFERENCIA INTERNACIONAL". Para ellos:
a) Primero responde con lo que diga la norma colombiana vigente del contexto. Si Colombia no
   fija un valor o un método, dilo de forma explícita ("la norma colombiana consultada no
   fija…") ANTES de citar cualquier referencia extranjera.
b) Presenta el valor extranjero siempre con su país y año, y di que NO es exigencia en
   Colombia; es un criterio comparado que el diseñador debe justificar para su proyecto.
c) Indica el límite de aplicabilidad que el propio fragmento declare (tipo de estructura,
   rango de frecuencias, geología, clima). Si el fragmento no declara ninguno, dilo.
d) NUNCA mezcles un valor extranjero con una cita colombiana como si vinieran de la misma
   norma, ni lo uses para completar un hueco de una norma colombiana sin avisarlo.
"""


def construir_norma_ref(pais: str, anio: int, nombre: str) -> str:
    """Devuelve el `norma_ref` canónico; falla si los datos no cumplen la convención."""
    if not re.fullmatch(r"[A-Z]{2}", pais or ""):
        raise ValueError(f"pais debe ser código ISO de 2 letras en mayúscula, recibido {pais!r}")
    if not 1900 <= int(anio) <= 2100:
        raise ValueError(f"anio fuera de rango: {anio!r}")
    if not (nombre or "").strip():
        raise ValueError("nombre vacío")
    return f"{PREFIJO}{pais}/{int(anio)} — {nombre.strip()}"


def es_referencia_internacional(norma_ref: str | None) -> bool:
    return bool(norma_ref) and _PATRON.match(norma_ref) is not None


def analizar_norma_ref(norma_ref: str) -> dict[str, str] | None:
    m = _PATRON.match(norma_ref or "")
    return m.groupdict() if m else None


def contexto_tiene_referencia_internacional(contexto: str) -> bool:
    return "REFERENCIA INTERNACIONAL" in (contexto or "")
