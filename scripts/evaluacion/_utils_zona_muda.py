"""Utilidad compartida: filtro de "zona muda" (sesgo de subreporte UNGRD),
hallazgo real de la Fase 1c (issue #61, 2026-09-29) -- 63.4% de los
municipios sin eventos de un tipo tampoco tienen NINGÚN reporte de
NINGÚN tipo a UNGRD, lo cual es evidencia de falta de capacidad de
reporte, no de bajo riesgo real. Comparar contra ese grupo infla
artificialmente cualquier diferencia encontrada.

Extraído (issue #68) porque esta misma lógica se copió casi idéntica en
`fase1c_control_corregido.py`, `fase3a_vulnerabilidad_impacto.py`,
`fase3b_sismica_ungrd.py` y `fase3c_hidrologia_inundacion.py` -- riesgo
real de que un análisis futuro contra UNGRD la reescriba mal o la
olvide. Cualquier cruce nuevo contra UNGRD debe usar esto en vez de
reimplementarlo."""
from __future__ import annotations

from collections import Counter


def construir_universos(
    todos_eventos: list[dict], tipos_objetivo: set[str]
) -> tuple[set[str], set[str], Counter]:
    """Dado el conjunto COMPLETO de eventos UNGRD (con al menos las
    claves 'municipio' y 'evento') y el/los tipo(s) de evento que se está
    analizando, devuelve:
      - universo_reportan: municipios con AL MENOS un reporte de
        CUALQUIER tipo (tienen capacidad de reporte activa).
      - grupo_bajo_corregido: universo_reportan MENOS los que tienen el
        tipo objetivo -- el grupo de control real (reportan pero cero
        eventos de ESE tipo), no "todos los que no tienen el tipo"
        (que mezclaría zonas mudas con zonas genuinamente sin el riesgo).
      - conteo_objetivo: Counter de municipio -> cantidad de eventos del
        tipo objetivo, para construir el grupo ALTO (ej. top-N por
        conteo)."""
    universo_reportan: set[str] = set()
    conteo_objetivo: Counter = Counter()
    municipios_con_tipo: set[str] = set()

    for e in todos_eventos:
        clave = (e.get("municipio") or "").strip().upper()
        if not clave:
            continue
        universo_reportan.add(clave)
        if e.get("evento") in tipos_objetivo:
            conteo_objetivo[clave] += 1
            municipios_con_tipo.add(clave)

    grupo_bajo_corregido = universo_reportan - municipios_con_tipo
    return universo_reportan, grupo_bajo_corregido, conteo_objetivo


def grupo_alto_top_n(conteo_objetivo: Counter, n: int = 15) -> list[str]:
    """Los N municipios con más eventos reales del tipo objetivo -- mismo
    criterio de tamaño de grupo ALTO usado en Fase 0/1/1c/3b/3c (15)."""
    return [m for m, _ in conteo_objetivo.most_common(n)]
