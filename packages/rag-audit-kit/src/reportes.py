"""Formatea un ReporteCobertura como markdown -- mismo tipo de tabla que ya
se escribe a mano en docs/fuentes-normativas.md, generada acá en vez de
transcrita numeral por numeral."""
from __future__ import annotations

from .cobertura import ReporteCobertura


def reporte_markdown(reporte: ReporteCobertura, titulo: str = "Cobertura") -> str:
    lineas = [
        f"# {titulo}",
        "",
        f"**{reporte.total_cubiertos} de {reporte.total_fuente} numerales cubiertos "
        f"({reporte.pct_cobertura}%).**",
        "",
        "| Capítulo | Cubiertos | Total | % | Faltantes |",
        "|---|---:|---:|---:|---|",
    ]
    for cap in sorted(reporte.por_capitulo):
        c = reporte.por_capitulo[cap]
        faltantes_str = ", ".join(c.faltantes[:8]) + (" …" if len(c.faltantes) > 8 else "")
        lineas.append(f"| {cap} | {c.cubiertos} | {c.total} | {c.pct}% | {faltantes_str or '—'} |")

    if reporte.faltantes:
        lineas += ["", "## Candidatos a hueco real (verificar contra el documento fuente antes de actuar)", ""]
        for n in reporte.faltantes:
            lineas.append(f"- `{n.valor}` — _{n.linea_contexto[:140]}_")

    return "\n".join(lineas)
