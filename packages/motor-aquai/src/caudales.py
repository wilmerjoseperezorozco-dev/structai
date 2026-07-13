"""
AquaAI — Módulo dotación y caudales de diseño
Referencia: RAS 2000 Título B, Sección B.2 / Resolución 0330-2017

Caudales calculados:
  Qp   — Caudal promedio diario (L/s)
  Qmd  — Caudal máximo diario   (L/s)  = Qp × fmd
  Qmh  — Caudal máximo horario  (L/s)  = Qmd × fmh
  Qci  — Caudal contra incendio (L/s)  — RAS Título B sección B.7

Ningún valor se pide a un LLM. Toda la lógica es determinística.
"""

from .schemas import CaudalesRequest, CaudalesResponse
from .ras2000_tablas import (
    DOTACION_RAS,
    FACTORES_CONSUMO,
    CAUDAL_INCENDIO,
)

# Conversión: L/hab/día  →  L/s  para N habitantes
# Q [L/s] = (dotacion [L/hab/día] × N [hab]) / 86400 [s/día]
_SEG_POR_DIA = 86_400


def calcular_caudales(req: CaudalesRequest) -> CaudalesResponse:
    nivel = req.nivel_complejidad.value
    clima = req.clima.value

    # 1. Dotación neta (tabla RAS o valor manual)
    if req.dotacion_manual is not None:
        dot_neta = req.dotacion_manual
        norma_ref = "RAS 2000 B.2.1 — Dotación ingresada manualmente por el usuario"
    else:
        _min, _max, _rec = DOTACION_RAS[nivel][clima]
        dot_neta = _rec
        norma_ref = (
            f"RAS 2000 / Res. 0330-2017 Tabla B.2.1 — "
            f"Nivel {nivel} / Clima {clima}: rango {_min}–{_max} L/hab/día, "
            f"valor recomendado {_rec} L/hab/día"
        )

    # 2. Dotación bruta (incluye pérdidas)
    perdidas = req.perdidas_pct / 100.0
    dot_bruta = dot_neta / (1 - perdidas)

    # 3. Caudal promedio diario
    Qp = (dot_bruta * req.poblacion_diseno) / _SEG_POR_DIA

    # 4. Factores y caudales máximos
    f = FACTORES_CONSUMO[nivel]
    fmd = f["fmd"]
    fmh = f["fmh"]
    Qmd = Qp * fmd
    Qmh = Qmd * fmh

    # 5. Caudal contra incendio
    Qci = CAUDAL_INCENDIO[nivel]

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
