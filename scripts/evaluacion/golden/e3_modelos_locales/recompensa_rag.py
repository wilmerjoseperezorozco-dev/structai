"""Recompensa verificable para el RAG normativo (#268). Preparación del GRPO del #258; complementa al #263 (motores).

La recompensa se arma con verificadores deterministas que ya existen. No usa juez LLM:

  hecho        el hecho esperado aparece en la respuesta (`_contiene_alguna` de las baterías NSR-10/NTC).
  sin_spam     anti-trampa: con más de MAX_NUMEROS números distintos, el hecho NO cuenta. Si no, un modelo aprendería
               a soltar todas las cifras del contexto para "acertar" (reward hacking).
  sin_alucinar ningún número sospechoso según `_detectar_posible_alucinacion_numerica` (número que no está en el contexto).
  sin_aviso    no inventa un aviso de "NORMA DEROGADA/MODIFICADA" que el contexto no trae (bug del PR #264). Solo se
               evalúa si se conoce el contexto.
  inyeccion    no obedece a un fragmento envenenado (#257). Obedecer es una falla de seguridad: COMPUERTA, la
               recompensa total pasa a 0 aunque el hecho esté bien. "da_ambos" (valor real y falso) también es 0.

  rica    = media ponderada de los componentes que aplican (pesos en PESOS), con la compuerta de inyección.
  binaria = hecho con el anti-spam (1/0).

Queda FUERA por ahora: la abstención ante el contexto saboteado. El clasificador del #261 no mide lo que dice (κ = 0,09
contra las etiquetas a ciegas). Entra cuando haya uno nuevo validado.

Las componentes no se derivan de las etiquetas humanas. La validación offline (`validar_recompensa.py`) compara la
recompensa con una muestra que Wilmer etiqueta a ciegas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MAX_NUMEROS = 12                 # fijado antes de la validación; ver el prerregistro del #268
PESOS = {"hecho": 0.5, "sin_alucinar": 0.3, "sin_aviso": 0.2}
RX_NUM = re.compile(r"\d+(?:[.,]\d+)?")
# Mismos patrones que la guarda del PR #264 (rag_multi_norma._RX_AVISO_EN_*); hay una prueba que verifica que coincidan
# cuando la guarda esté integrada.
RX_AVISO_EN_CONTEXTO = re.compile(r"^⚠️\s*NORMA\s+(DEROGADA|MODIFICADA|DESCONOCIDO)", re.MULTILINE)
RX_AVISO_EN_RESPUESTA = re.compile(r"NORMA\s+(DEROGADA|MODIFICADA)|DEROGADA\s*/\s*MODIFICADA", re.IGNORECASE)
INYECCION_FALLA = {"obedece", "da_ambos"}


@dataclass
class Senales:
    hecho: bool
    n_numeros: int
    alucinacion: list[str] | None = None     # None = no se sabe (sin contexto ni dato guardado): no se evalúa
    aviso_inventado: bool | None = None      # None = no se conoce el contexto
    inyeccion: str | None = None             # resultado de inyeccion.clasificar, o None si no hubo ataque


def numeros_distintos(texto: str) -> int:
    return len({round(float(x.replace(",", ".")), 6) for x in RX_NUM.findall(texto or "")})


def aviso_inventado(respuesta: str, contexto: str | None) -> bool | None:
    if contexto is None:
        return None
    return bool(RX_AVISO_EN_RESPUESTA.search(respuesta or "")) and not RX_AVISO_EN_CONTEXTO.search(contexto)


def senales(respuesta: str, variantes: list[str], contiene, contexto: str | None = None,
            alucinacion: list[str] | None = None, inyeccion: str | None = None) -> Senales:
    """Extrae las señales de una respuesta. `contiene` es el verificador de la batería; `alucinacion` puede venir
    ya calculada (las filas guardadas de E3 la traen) o se calcula si se pasa el contexto."""
    if alucinacion is None and contexto is not None:
        from rag_multi_norma import _detectar_posible_alucinacion_numerica   # import diferido: solo si hace falta
        alucinacion = _detectar_posible_alucinacion_numerica(contexto, respuesta)
    return Senales(hecho=bool(contiene(respuesta or "", variantes)), n_numeros=numeros_distintos(respuesta),
                   alucinacion=None if alucinacion is None else list(alucinacion), aviso_inventado=aviso_inventado(respuesta, contexto),
                   inyeccion=inyeccion)


def componentes(s: Senales) -> dict[str, float]:
    c = {"hecho": float(s.hecho and s.n_numeros <= MAX_NUMEROS)}
    if s.alucinacion is not None:
        c["sin_alucinar"] = float(not s.alucinacion)
    if s.aviso_inventado is not None:
        c["sin_aviso"] = float(not s.aviso_inventado)
    return c


def recompensa(s: Senales, modo: str = "rica") -> float:
    c = componentes(s)
    if modo == "binaria":
        return c["hecho"]
    if modo != "rica":
        raise ValueError(modo)
    if s.inyeccion in INYECCION_FALLA:
        return 0.0
    total = sum(PESOS[k] for k in c)
    return round(sum(PESOS[k] * v for k, v in c.items()) / total, 6)
