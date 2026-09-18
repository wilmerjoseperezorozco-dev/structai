"""Heurística de confianza: ¿el chunk ya ingestado es verbatim real, o es un
resumen condensado disfrazado de completo?

Patrón encontrado A MANO, repetidas veces, en distintos títulos de la
NSR-10 (A.3.3, B.3.4, K.2, K.3, F.3, y el Título J completo -- ver
docs/fuentes-normativas.md) antes de que existiera esta heurística: un
chunk de 150-400 caracteres cubriendo una sección fuente que en el PDF
real ocupa varios párrafos o una tabla completa. Esto NO reemplaza la
verificación humana -- es exactamente lo que ya se hacía a ojo, formalizado
en una función, para no tener que releer manualmente cada chunk existente
título por título. Un ratio bajo es una SEÑAL para revisar, no una prueba.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfianzaChunk:
    numeral: str
    longitud_chunk: int
    longitud_fuente: int
    ratio: float
    sospechoso: bool
    motivo: str


def evaluar_confianza(
    numeral: str,
    texto_chunk: str,
    texto_fuente_seccion: str,
    umbral_ratio: float = 0.35,
    longitud_fuente_minima: int = 200,
) -> ConfianzaChunk:
    """`texto_fuente_seccion`: el texto de ESA sección específica tal como
    aparece en el documento fuente (quien llama ya lo aisló -- este paquete
    no sabe cortar secciones de un PDF, eso es responsabilidad del script
    de ingesta que ya lee el documento). Secciones fuente muy cortas
    (< longitud_fuente_minima, default 200 caracteres -- una definición de
    una línea, por ejemplo) no entran en la comparación de ratio: un chunk
    igual de corto ahí es correcto, no sospechoso, y el ratio por sí solo
    daría falsos positivos en secciones genuinamente breves."""
    len_chunk = len(texto_chunk)
    len_fuente = len(texto_fuente_seccion)

    if len_fuente < longitud_fuente_minima:
        return ConfianzaChunk(
            numeral=numeral, longitud_chunk=len_chunk, longitud_fuente=len_fuente,
            ratio=1.0, sospechoso=False,
            motivo="Sección fuente breve (< longitud_fuente_minima) -- ratio no aplica.",
        )

    ratio = round(len_chunk / len_fuente, 3) if len_fuente else 1.0
    sospechoso = ratio < umbral_ratio
    motivo = (
        f"Chunk cubre solo {ratio:.0%} de la longitud de la sección fuente "
        f"({len_chunk} de {len_fuente} caracteres) -- mismo patrón de "
        "'resumen disfrazado de completo' ya visto en A.3.3/B.3.4/K.2/K.3/"
        "F.3/Título J. Revisar contra el documento original antes de "
        "confiar en este chunk para una decisión de diseño real."
        if sospechoso
        else f"Chunk cubre {ratio:.0%} de la longitud de la sección fuente -- dentro de rango esperado."
    )
    return ConfianzaChunk(
        numeral=numeral, longitud_chunk=len_chunk, longitud_fuente=len_fuente,
        ratio=ratio, sospechoso=sospechoso, motivo=motivo,
    )
