"""Compara los numerales reales de un documento fuente contra lo que ya
tiene chunk en el corpus RAG, y arma el mismo tipo de reporte por capítulo
que docs/fuentes-normativas.md viene documentando a mano título por título.

Reglas de coincidencia (calibradas sobre nsr10_chunks.seccion, ver
docs/CATALOGO_DATOS.md -- ampliadas 2026-09-16 tras una validación real
contra Título I que encontró un caso real no cubierto por la regla
original, ver abajo):

1. Match exacto.
2. El valor cubierto EMPIEZA con el numeral seguido de un límite no
   numérico -- la columna `seccion` real trae a veces texto extra pegado
   ("J.3.3.2 (Tabla J.3.3-1)").
3. El valor cubierto es un RANGO explícito en texto libre ("I.2.1 a
   I.2.3", mismo convenio real usado en varios chunks de Título I) --
   cubre cualquier numeral hermano dentro de ese rango numérico, siempre
   que compartan el mismo prefijo padre.

LÍMITE HONESTO conocido, no resuelto automáticamente a propósito: un
`seccion` que es solo el capítulo padre en texto libre ("I.1", sin rango
ni numeral hijo) -- visto en Título I cubriendo 11 chunks reales que sí
tienen el contenido de I.1.1 a I.1.5.1 completo, verificado a mano leyendo
`texto`, pero sin decirlo en `seccion` -- NO se cuenta automáticamente
como cobertura de sus numerales hijos acá. Asumir que un padre bare cubre
todo lo de abajo sería adivinar, no verificar (podría ser solo la intro),
y este paquete prefiere sub-reportar cobertura (falso "candidato a hueco"
que una revisión humana descarta rápido) antes que sobre-reportarla
(hueco real escondido detrás de una cobertura que en realidad no existía).
Si `pct_cobertura` sale bajo pese a que el título tiene volumen real de
chunks, revisar `texto` de los chunks del capítulo antes de confiar en el
número -- exactamente lo que ya hacía este proyecto a mano.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .numerales import Numeral, capitulo_de, dedup_preservando_orden

_PATRON_RANGO = re.compile(
    r"^([A-Z]{1,3}\d{0,2}(?:\.\d{1,3})*)\s+a\s+([A-Z]{1,3}\d{0,2}(?:\.\d{1,3})*)\b"
)


def _en_rango(numeral: str, inicio: str, fin: str) -> bool:
    """True si `numeral` cae dentro de [inicio, fin] -- solo cuando los tres
    comparten el mismo prefijo padre (todo menos el último componente) y el
    último componente es numérico en los tres. "I.2.2" cae en
    "I.2.1 a I.2.3"; "I.2.2.1" (un nieto, no un hermano) no."""
    partes_num, partes_ini, partes_fin = numeral.split("."), inicio.split("."), fin.split(".")
    if not (len(partes_num) == len(partes_ini) == len(partes_fin)):
        return False
    if not (partes_num[:-1] == partes_ini[:-1] == partes_fin[:-1]):
        return False
    try:
        n, i, f = int(partes_num[-1]), int(partes_ini[-1]), int(partes_fin[-1])
    except ValueError:
        return False
    return i <= n <= f


def _cubierto(numeral: str, valores_cubiertos: list[str]) -> bool:
    for v in valores_cubiertos:
        if v == numeral:
            return True
        if v.startswith(numeral):
            siguiente = v[len(numeral) : len(numeral) + 1]
            if not siguiente.isdigit():
                return True
        rango = _PATRON_RANGO.match(v)
        if rango and _en_rango(numeral, rango.group(1), rango.group(2)):
            return True
    return False


@dataclass(frozen=True)
class CoberturaCapitulo:
    capitulo: str
    total: int
    cubiertos: int
    faltantes: list[str]

    @property
    def pct(self) -> float:
        return round(100 * self.cubiertos / self.total, 1) if self.total else 100.0


@dataclass(frozen=True)
class ReporteCobertura:
    total_fuente: int
    total_cubiertos: int
    faltantes: list[Numeral]
    por_capitulo: dict[str, CoberturaCapitulo] = field(default_factory=dict)

    @property
    def pct_cobertura(self) -> float:
        return round(100 * self.total_cubiertos / self.total_fuente, 1) if self.total_fuente else 100.0


def comparar_cobertura(
    numerales_fuente: list[Numeral],
    valores_cubiertos: list[str],
    profundidad_capitulo: int = 2,
) -> ReporteCobertura:
    """`numerales_fuente`: salida de extraer_numerales() sobre el texto del
    documento oficial. `valores_cubiertos`: valores reales ya en el corpus
    (ej. SELECT DISTINCT seccion FROM nsr10_chunks WHERE seccion LIKE 'A.%') --
    deliberadamente recibe una lista simple, no un cliente de Supabase, para
    no acoplar este paquete a ningún backend concreto (idea 1 del roadmap:
    "mismo método, distinto dominio" -- otra base de conocimiento trae sus
    propios valores cubiertos de donde sea que los tenga)."""
    unicos = dedup_preservando_orden(numerales_fuente)

    faltantes = [n for n in unicos if not _cubierto(n.valor, valores_cubiertos)]
    total_cubiertos = len(unicos) - len(faltantes)

    por_capitulo: dict[str, list[Numeral]] = {}
    for n in unicos:
        por_capitulo.setdefault(capitulo_de(n.valor, profundidad_capitulo), []).append(n)

    reporte_capitulos = {
        cap: CoberturaCapitulo(
            capitulo=cap,
            total=len(ns),
            cubiertos=sum(1 for n in ns if _cubierto(n.valor, valores_cubiertos)),
            faltantes=[n.valor for n in ns if not _cubierto(n.valor, valores_cubiertos)],
        )
        for cap, ns in por_capitulo.items()
    }

    return ReporteCobertura(
        total_fuente=len(unicos),
        total_cubiertos=total_cubiertos,
        faltantes=faltantes,
        por_capitulo=reporte_capitulos,
    )
