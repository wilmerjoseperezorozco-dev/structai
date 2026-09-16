"""Extracción de numerales jerárquicos ("A.3.3.4", "J.4.3.1", "3.2.1") desde
texto plano de un documento fuente.

Esto NO es específico de NSR-10 -- es el mismo patrón usado a mano, sesión
tras sesión, para auditar los 11 títulos (ver docs/fuentes-normativas.md:
"mismo método pypdf + comparación contra nsr10_chunks" repetido para
A/B/C/D/E/G/H/I/J/K), extraído a una función reusable con un patrón
configurable -- una base normativa en otro idioma, o documentación de una
API con secciones "3.2.1", usa el mismo mecanismo pasando su propio patrón.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Default calibrado sobre numerales reales de la NSR-10: letra(s) mayúscula(s)
# (1-3, cubre "A", "I", pero también variantes como "F5" ya vistas en el
# corpus), opcionalmente con 1-2 dígitos pegados (subcapítulos "A2"/"A3"
# encontrados en nsr10_chunks, ver docs/CATALOGO_DATOS.md), seguido de 1 a 7
# grupos "punto+dígitos". Exige al menos un grupo con punto -- una letra
# sola ("A") no cuenta como numeral, evita capturar cada inicial de oración.
PATRON_NUMERAL_DEFAULT = re.compile(
    r"(?<![\w.])([A-Z]{1,3}\d{0,2}(?:\.\d{1,3}){1,7})(?![\d.])"
)


@dataclass(frozen=True)
class Numeral:
    """Un numeral encontrado en el texto fuente, con el contexto real donde
    apareció -- la verificación humana final (que este proyecto siempre
    aplica antes de dar un hueco por confirmado, ver docs/fuentes-normativas.md)
    necesita poder ver la línea real, no solo el numeral suelto."""

    valor: str
    linea_contexto: str


def extraer_numerales(
    texto: str, patron: re.Pattern[str] = PATRON_NUMERAL_DEFAULT
) -> list[Numeral]:
    """Recorre `texto` línea por línea (así `linea_contexto` es siempre útil
    para verificación humana) y devuelve cada numeral encontrado, en orden
    de aparición, SIN deduplicar -- un mismo numeral puede aparecer como
    encabezado real una vez y como referencia cruzada varias veces más;
    quien llama decide qué hacer con los duplicados (dedup_preservando_orden
    de abajo es la opción más común, usada por comparar_cobertura)."""
    encontrados: list[Numeral] = []
    for linea in texto.splitlines():
        for m in patron.finditer(linea):
            encontrados.append(Numeral(valor=m.group(1), linea_contexto=linea.strip()))
    return encontrados


def dedup_preservando_orden(numerales: list[Numeral]) -> list[Numeral]:
    """Se queda con la PRIMERA aparición de cada valor -- normalmente la más
    cercana al encabezado real de la sección, antes de que empiecen las
    referencias cruzadas dispersas en el resto del documento."""
    vistos: set[str] = set()
    resultado: list[Numeral] = []
    for n in numerales:
        if n.valor not in vistos:
            vistos.add(n.valor)
            resultado.append(n)
    return resultado


def capitulo_de(numeral: str, profundidad: int = 2) -> str:
    """"A.3.3.4" con profundidad=2 -> "A.3" -- agrupación para el reporte de
    cobertura por capítulo. profundidad=1 agruparía todo bajo "A" (el
    título completo); el valor por defecto (2) refleja cómo se agrupó a
    mano en docs/fuentes-normativas.md (ej. "B.4.3", "B.4.6" como
    secciones hermanas dentro de B.4)."""
    partes = numeral.split(".")
    return ".".join(partes[: max(profundidad, 1)])
