"""
AquaAI — Módulo de proyección de población
Referencia: RAS 2000 Título B, Sección B.1 / Resolución 0330-2017 Art. 41

Métodos implementados:
  - Aritmético   : P(t) = Po + r·t
  - Geométrico   : P(t) = Po·(1 + r)^t          ← recomendado RAS para municipios pequeños
  - Exponencial  : P(t) = Po·e^(r·t)             ← recomendado RAS para ciudades en crecimiento

La tasa r se puede proveer explícitamente o se estima por nivel de complejidad.
"""

import math
from .schemas import PoblacionRequest, PoblacionResponse, MetodoPoblacion
from .ras2000_tablas import TASA_CRECIMIENTO_DEFAULT, PERIODO_DISENO


def proyectar_poblacion(req: PoblacionRequest) -> PoblacionResponse:
    Po = req.poblacion_censal
    t  = req.anio_diseno - req.anio_censo

    # Tasa: usar la provista o el default por nivel de complejidad
    r = req.tasa_crecimiento if req.tasa_crecimiento is not None \
        else TASA_CRECIMIENTO_DEFAULT[req.nivel_complejidad.value]

    periodo_diseno = PERIODO_DISENO[req.nivel_complejidad.value]

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
