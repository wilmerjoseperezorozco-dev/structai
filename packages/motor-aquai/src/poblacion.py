"""
AquaAI — Módulo de proyección de población
Referencia: Resolución 0330 de 2017, Art. 40 (período de diseño) y Art. 41
            (métodos de proyección)

Métodos implementados:
  - Aritmético   : P(t) = Po + r·t
  - Geométrico   : P(t) = Po·(1 + r)^t          ← recomendado para municipios pequeños
  - Exponencial  : P(t) = Po·e^(r·t)             ← recomendado para ciudades en crecimiento

La tasa r se puede proveer explícitamente o se estima por nivel de complejidad
(TASA_CRECIMIENTO_DEFAULT — tabla aún pendiente de revisión, ver auditoría
2026-08-08). El período de diseño, en cambio, ya NO depende del nivel de
complejidad: el Art. 40 de la Res. 0330/2017 fija 25 años para todos los
componentes de acueducto, alcantarillado y aseo.
"""

import math
from .schemas import PoblacionRequest, PoblacionResponse, MetodoPoblacion
from .ras2000_tablas import TASA_CRECIMIENTO_DEFAULT, PERIODO_DISENO_ANIOS


def proyectar_poblacion(req: PoblacionRequest) -> PoblacionResponse:
    Po = req.poblacion_censal
    t  = req.anio_diseno - req.anio_censo

    # Tasa: usar la provista o el default por nivel de complejidad
    r = req.tasa_crecimiento if req.tasa_crecimiento is not None \
        else TASA_CRECIMIENTO_DEFAULT[req.nivel_complejidad.value]

    # Período de diseño: uniforme por ley (Res. 0330/2017 Art. 40), no depende
    # del nivel de complejidad.
    periodo_diseno = PERIODO_DISENO_ANIOS

    if req.metodo == MetodoPoblacion.ARITMETICO:
        Pd = Po + r * Po * t          # r como fracción decimal anual
        formula = f"P = {Po} + {r:.4f}·{Po}·{t} = {int(round(Pd))} hab"
        notas = (
            "Método aritmético: supone crecimiento lineal constante. "
            "Válido para poblaciones estabilizadas o en descenso. "
            "Puede subestimar en zonas de expansión."
        )

    elif req.metodo == MetodoPoblacion.GEOMETRICO:
        Pd = Po * (1 + r) ** t
        formula = f"P = {Po} × (1 + {r:.4f})^{t} = {int(round(Pd))} hab"
        notas = (
            "Método geométrico: supone crecimiento proporcional. "
            "Recomendado por RAS para municipios de nivel bajo y medio. "
            "Más conservador que el exponencial."
        )

    elif req.metodo == MetodoPoblacion.EXPONENCIAL:
        Pd = Po * math.exp(r * t)
        formula = f"P = {Po} × e^({r:.4f}·{t}) = {int(round(Pd))} hab"
        notas = (
            "Método exponencial: crecimiento continuo compuesto. "
            "Recomendado para ciudades intermedias y altas en expansión. "
            "Tiende a ser el más conservador en horizontes largos."
        )

    else:
        raise ValueError(f"Método no reconocido: {req.metodo}")

    return PoblacionResponse(
        poblacion_diseno=int(round(Pd)),
        periodo_diseno=periodo_diseno,
        tasa_usada=r,
        metodo=req.metodo.value,
        formula=formula,
        notas=notas,
    )
