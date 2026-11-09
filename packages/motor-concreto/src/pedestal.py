"""Pedestal de concreto reforzado de sección cuadrada bajo carga axial concéntrica (NSR-10 Título C).

Se diseña como elemento a compresión con estribos. Verificaciones, todas con numerales leídos del corpus el 2026-11-08:
- C.10.9.1: 0.01·Ag ≤ Ast ≤ 0.04·Ag.
- C.10.3.6.2 / C.10-2: φPn,max = φ·0.75·[0.85 f'c (Ag − Ast) + fy Ast], φ = 0.65 (C.9.3.2.2(b), estribos).
- C.10.14.1 / C.9.3.2.4: aplastamiento φ·0.85·f'c·A1 con φ = 0.65, SIN el factor √(A2/A1) (conservador).
- C.10.10.1.2 y C.10-6: r = 0.3·c y k·ℓu/r ≤ 22 (k = 1: el pedestal se trata como no arriostrado por prudencia).
- C.7.6.3: separación libre entre barras ≥ max(1.5·db, 40 mm).
- C.12.3.2: ℓdc = max(0.24·fy·db/√f'c, 0.043·fy·db) para los pasadores en compresión dentro de la zapata (sin reducciones por exceso de refuerzo; el
  mínimo de 200 mm de C.12.3.1 se aplica por la práctica de ACI, no se re-verificó en el corpus). Disponible: h_zapata − 75 mm.
- C.7.10.5.1/.2: estribo mínimo No. 3; separación ≤ min(16 db_long, 48 db_estribo, menor dimensión).
- Base del pedestal con momentos y cortante (C.15.8.1.4 -> C.11.6), numerales leídos del corpus el 2026-11-09:
  interacción P–M por la curva de columna (columna.curva, φ de C.9.3.2) y flexión biaxial con la suma lineal Mux/φMnx + Muy/φMny <= 1 (conservadora; la
  NSR-10 no fija el método); cortante por fricción Avf = Vu/(φ·fy·μ) (C.11-25) con φ = 0.75 (C.9.3.2.3), fy <= 420 (C.11.6.6), μ = 0.6λ si la junta no es
  intencionalmente rugosa y 1.0λ si lo es a ~6 mm (C.11.6.4.3, C.11.6.9), Vn <= min(0.2f'c Ac, 5.5 Ac) o, junta rugosa, min(0.2f'c Ac, (3.3 + 0.08f'c) Ac, 11 Ac) (C.11.6.5).
  No se acredita la compresión permanente (C.11.6.7 lo permite); la tracción neta se suma al área requerida: Ast >= Avf + T/(0.9 fy), T = (Mux+Muy)/z - Pu/2.
NO verifica: gancho de los pasadores, la alternativa de pedestal de concreto simple (C.22.8), ni cortante propio del pedestal como columna (C.11.2) en su altura libre.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .columna import curva, phi_mn_a
from .viga import AREA_MM2, DIAMETRO_MM

PHI_COMPRESION = 0.65
PHI_APLASTAMIENTO = 0.65
FACTOR_PN_MAX = 0.75
ESBELTEZ_MAX = 22.0
RHO_MIN, RHO_MAX = 0.01, 0.04
LD_MINIMO_MM = 200.0
RECUBRIMIENTO_ZAPATA_ABAJO_MM = 75.0
PHI_CORTANTE_FRICCION = 0.75
DIA_ESTRIBO = "3"
DIAS_LONGITUDINAL = ("5", "6", "7", "8")
N_CARA = (2, 3, 4, 5)


@dataclass(frozen=True)
class ResultadoPedestal:
    cumple: bool
    motivo_fallo: str
    c_mm: float
    h_mm: float
    barras: str
    As_mm2: float
    rho: float
    phi_Pn_max_kN: float
    phi_aplastamiento_kN: float
    esbeltez: float
    ld_compresion_mm: float
    estribos: str
    masa_acero_kg: float
    volumen_m3: float
    area_encofrado_m2: float
    Avf_mm2: float = 0.0
    utilizacion_flexion: float = 0.0
    mu_friccion: float = 0.0


def _falla(c, h, motivo, esb=0.0):
    return ResultadoPedestal(False, motivo, c, h, "-", 0.0, 0.0, 0.0, 0.0, esb, 0.0, "-", math.inf, c * c * h / 1e9, 4 * c * h / 1e6)


def disenar_pedestal(c_mm: float, h_mm: float, Pu_kN: float, fc: float, fy: float, h_zapata_mm: float, *, recubrimiento_mm: float = 50.0,
                     Mux_kNm: float = 0.0, Muy_kNm: float = 0.0, Vux_kN: float = 0.0, Vuy_kN: float = 0.0, junta_rugosa: bool = False) -> ResultadoPedestal:
    """Menor área de acero longitudinal que cumple todas las verificaciones. h_mm = altura libre del pedestal sobre la zapata.
    Mu*, Vu* son las solicitaciones en la BASE del pedestal (junta con la zapata)."""
    if c_mm <= 0 or h_mm < 0 or Pu_kN <= 0:
        raise ValueError("c_mm > 0, h_mm >= 0 y Pu_kN > 0")
    Ag = c_mm * c_mm
    esb = h_mm / (0.3 * c_mm)
    if esb > ESBELTEZ_MAX:
        return _falla(c_mm, h_mm, f"esbeltez {esb:.1f} > 22 (C.10-6): requiere magnificación de momentos", esb)
    aplast = PHI_APLASTAMIENTO * 0.85 * fc * Ag / 1000
    if Pu_kN > aplast:
        return _falla(c_mm, h_mm, f"aplastamiento {aplast:.0f} kN < Pu (C.10.14.1)", esb)
    fy_f = min(fy, 420.0)                                                     # C.11.6.6
    mu = 1.0 if junta_rugosa else 0.6
    V = math.hypot(Vux_kN, Vuy_kN)
    vn_lim = min(0.2 * fc, 3.3 + 0.08 * fc, 11.0) if junta_rugosa else min(0.2 * fc, 5.5)
    vn_max = PHI_CORTANTE_FRICCION * vn_lim * Ag / 1000
    if V > vn_max:
        return _falla(c_mm, h_mm, f"cortante por fricción {V:.0f} kN > φVn,max {vn_max:.0f} kN (C.11.6.5)", esb)
    avf = V * 1000 / (PHI_CORTANTE_FRICCION * fy_f * mu)
    d_est = DIAMETRO_MM[DIA_ESTRIBO]
    mejor = None
    motivos: set[str] = set()
    for dia in DIAS_LONGITUDINAL:
        db, a1 = DIAMETRO_MM[dia], AREA_MM2[dia]
        ld = max(0.24 * fy * db / math.sqrt(fc), 0.043 * fy * db, LD_MINIMO_MM)
        for n_cara in N_CARA:
            n = 4 * (n_cara - 1)
            Ast = n * a1
            if not RHO_MIN * Ag <= Ast <= RHO_MAX * Ag:
                motivos.add("cuantía fuera de 1–4 % (C.10.9.1)")
                continue
            sep_libre = (c_mm - 2 * (recubrimiento_mm + d_est + db / 2)) / (n_cara - 1) - db
            if sep_libre < max(1.5 * db, 40.0):
                motivos.add("separación libre < max(1.5db, 40) (C.7.6.3)")
                continue
            phi_pn = PHI_COMPRESION * FACTOR_PN_MAX * (0.85 * fc * (Ag - Ast) + fy * Ast) / 1000
            if phi_pn < Pu_kN:
                motivos.add("φPn,max < Pu con ρ≤4 % (C.10-2)")
                continue
            if ld > h_zapata_mm - RECUBRIMIENTO_ZAPATA_ABAJO_MM:
                motivos.add(f"ℓdc {ld:.0f} mm no cabe en la zapata (C.12.3.2)")
                continue
            util = 0.0
            m_tot = abs(Mux_kNm) + abs(Muy_kNm)
            if m_tot > 0:
                phi_mn = phi_mn_a(curva(c_mm, c_mm, n_cara, dia, DIA_ESTRIBO, recubrimiento_mm, fc, fy), Pu_kN)
                if not phi_mn > 0:
                    motivos.add("Pu fuera de la curva de interacción")
                    continue
                util = m_tot / phi_mn
                if util > 1.0:
                    motivos.add("interacción P–M biaxial > 1")
                    continue
            z_brazo = (c_mm - 2 * (recubrimiento_mm + d_est + db / 2)) / 1000
            tens = max(m_tot / z_brazo - Pu_kN / 2, 0.0)
            if Ast < avf + tens * 1000 / (0.9 * fy):
                motivos.add("As < Avf + tracción (C.11.6.4/C.11.6.7)")
                continue
            if mejor is None or Ast < mejor[0]:
                mejor = (Ast, n, dia, db, a1, phi_pn, ld, util)
    if mejor is None:
        return _falla(c_mm, h_mm, "; ".join(sorted(motivos)) or "sin solución", esb)
    Ast, n, dia, db, a1, phi_pn, ld, util = mejor
    s = math.floor(min(16 * db, 48 * d_est, c_mm) / 10) * 10
    n_est = math.ceil(h_mm / s) + 1 if h_mm > 0 else 0
    largo_est = 4 * (c_mm - 2 * recubrimiento_mm) + 2 * max(6 * d_est, 75.0)
    masa = 7850e-9 * (Ast * (h_mm + ld) + n_est * largo_est * AREA_MM2[DIA_ESTRIBO])
    return ResultadoPedestal(True, "", c_mm, h_mm, f"{n}#{dia}", Ast, Ast / Ag, phi_pn, PHI_APLASTAMIENTO * 0.85 * fc * Ag / 1000, esb, ld,
                             f"#{DIA_ESTRIBO} c/{s} mm", masa, Ag * h_mm / 1e9, 4 * c_mm * h_mm / 1e6, avf, util, mu)
