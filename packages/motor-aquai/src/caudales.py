"""
AquaAI — Módulo dotación y caudales de diseño
Referencia: Resolución 0330 de 2017, Arts. 43-44 (dotación), 47 (factores K1/K2)
            y 70 (caudal contra incendio)

Caudales calculados:
  Qp   — Caudal promedio diario (L/s)
  Qmd  — Caudal máximo diario   (L/s)  = Qp × fmd (K1)
  Qmh  — Caudal máximo horario  (L/s)  = Qmd × fmh (K2)
  Qci  — Caudal mínimo contra incendio (L/s) — Art. 70. No es adicional a Qmh:
         la red debe poder entregarlo durante el período de diseño.

Ningún valor se pide a un LLM. Toda la lógica es determinística.
"""

from .schemas import CaudalesRequest, CaudalesResponse
from .ras2000_tablas import (
    dotacion_neta_maxima,
    factores_consumo_maximos,
    caudal_incendio_minimo,
)

# Conversión: L/hab/día  →  L/s  para N habitantes
# Q [L/s] = (dotacion [L/hab/día] × N [hab]) / 86400 [s/día]
_SEG_POR_DIA = 86_400


def calcular_caudales(req: CaudalesRequest) -> CaudalesResponse:
    # 1. Dotación neta (tope legal por altura, Art. 43 Tabla 1, o valor manual)
    if req.dotacion_manual is not None:
        dot_neta = req.dotacion_manual
        norma_ref = (
            "Res. 0330-2017 Art. 43 — Dotación ingresada manualmente por el "
            "usuario (debe sustentarse en datos históricos reales de consumo)"
        )
    else:
        dot_neta = dotacion_neta_maxima(req.altura_msnm)
        norma_ref = (
            f"Res. 0330-2017 Art. 43, Tabla 1 — Altura {req.altura_msnm:.0f} "
            f"m s.n.m.: dotación neta máxima {dot_neta:.0f} L/hab/día "
            f"(tope legal; use datos históricos reales del SUI o del "
            f"prestador cuando estén disponibles)"
        )

    # 2. Dotación bruta (incluye pérdidas)
    perdidas = req.perdidas_pct / 100.0
    dot_bruta = dot_neta / (1 - perdidas)

    # 3. Caudal promedio diario
    Qp = (dot_bruta * req.poblacion_diseno) / _SEG_POR_DIA

    # 4. Factores de mayoración K1/K2 y caudales máximos (Art. 47, Parágrafo 2)
    fmd, fmh = factores_consumo_maximos(req.poblacion_diseno)
    Qmd = Qp * fmd
    Qmh = Qmd * fmh

    # 5. Caudal mínimo contra incendio (Art. 70)
    Qci = caudal_incendio_minimo(req.poblacion_diseno, req.zona_incendio.value)

    return CaudalesResponse(
        dotacion_lhd=round(dot_neta, 2),
        dotacion_bruta_lhd=round(dot_bruta, 2),
        Qp_ls=round(Qp, 4),
        Qmd_ls=round(Qmd, 4),
        Qmh_ls=round(Qmh, 4),
        Qci_ls=Qci,
        fmd=fmd,
        fmh=fmh,
        norma_ref=norma_ref,
    )
