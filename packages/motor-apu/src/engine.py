"""
══════════════════════════════════════════════════════════════
MOTOR APU — ENGINE MATEMÁTICO
MotorAPU Engineer | Cálculo Unitario Jerárquico
Incertidumbre via Monte Carlo Simulation
══════════════════════════════════════════════════════════════
"""
import numpy as np
import time
import uuid
from dataclasses import asdict
from typing import Optional
from .models import (
    MaterialItem, ManoObraItem, EquipoItem,
    AIU, APUResult, UnidadMedida
)


class MotorAPU:
    """
    Motor matemático de Análisis de Precios Unitarios.

    Jerarquía de cálculo:
      1. Materiales: Σ(cantidad × (1+desperdicio) × precio_unit)
      2. Mano Obra:  Σ(costo_cuadrilla_dia / rendimiento)
      3. Equipo:     Σ(costo_equipo_hora × cant / rendimiento)
      4. CD = Mat + MO + Equipo
      5. AIU = CD × (A% + I% + U%)
      6. PU = CD + AIU = CD × (1 + AIU%)

    Incertidumbre (Monte Carlo):
      - Rendimientos MO ~ N(μ, σ=μ×var_rend)
      - Rendimientos Equipo ~ N(μ, σ=μ×var_rend)
      - Precios materiales ~ N(μ, σ=μ×var_precio)
      - Cantidades ~ N(μ, σ=μ×var_cant)
      - N=5000 simulaciones → IC 90% = [P5, P95]
    """

    N_SIMULATIONS = 5_000

    def __init__(self, aiu: Optional[AIU] = None):
        self.aiu = aiu or AIU()

    # ── Cálculo determinístico ─────────────────────────────────
    def calcular_materiales(self, materiales: list[MaterialItem]) -> float:
        return sum(m.subtotal for m in materiales)

    def calcular_mano_obra(self, mano_obra: list[ManoObraItem]) -> float:
        return sum(mo.subtotal for mo in mano_obra)

    def calcular_equipo(self, equipo: list[EquipoItem]) -> float:
        return sum(eq.subtotal for eq in equipo)

    def calcular_apu(
        self,
        actividad_id:  str,
        descripcion:   str,
        unidad:        UnidadMedida,
        materiales:    list[MaterialItem],
        mano_obra:     list[ManoObraItem],
        equipo:        list[EquipoItem],
        aiu:           Optional[AIU] = None,
        capitulo:      str = "",
        norma_ref:     str = "",
        run_montecarlo: bool = True
    ) -> APUResult:
        """Calcula APU completo con incertidumbre Monte Carlo."""

        aiu_obj = aiu or self.aiu
        t0 = time.time()

        # ── Costos determinísticos ────────────────────────────
        cd_mat = self.calcular_materiales(materiales)
        cd_mo  = self.calcular_mano_obra(mano_obra)
        cd_eq  = self.calcular_equipo(equipo)
        cd     = cd_mat + cd_mo + cd_eq
        costo_aiu = cd * aiu_obj.total_pct
        pu    = cd * aiu_obj.factor

        # ── Monte Carlo ───────────────────────────────────────
        pu_mean = pu_std = pu_p05 = pu_p95 = 0.0
        if run_montecarlo and cd > 0:
            pu_mean, pu_std, pu_p05, pu_p95 = self._monte_carlo(
                materiales, mano_obra, equipo, aiu_obj
            )

        return APUResult(
            actividad_id     = actividad_id,
            descripcion      = descripcion,
            unidad           = unidad,
            costo_materiales = round(cd_mat, 2),
            costo_mano_obra  = round(cd_mo,  2),
            costo_equipo     = round(cd_eq,  2),
            costo_directo    = round(cd,     2),
            aiu              = aiu_obj,
            costo_aiu        = round(costo_aiu, 2),
            precio_unitario  = round(pu,     2),
            pu_mean          = round(pu_mean, 2),
            pu_std           = round(pu_std,  2),
            pu_p05           = round(pu_p05,  2),
            pu_p95           = round(pu_p95,  2),
            capitulo         = capitulo,
            norma_ref        = norma_ref,
            fecha            = time.strftime("%Y-%m-%d"),
        )

    # ── Monte Carlo ────────────────────────────────────────────
    def _monte_carlo(
        self,
        materiales: list[MaterialItem],
        mano_obra:  list[ManoObraItem],
        equipo:     list[EquipoItem],
        aiu:        AIU
    ) -> tuple[float, float, float, float]:
        rng = np.random.default_rng(42)
        N   = self.N_SIMULATIONS
        pu_samples = np.zeros(N)

        # ── Materiales vectorizados ───────────────────────────
        for mat in materiales:
            precio_sim = rng.normal(
                mat.precio_unit,
                mat.precio_unit * mat.variacion_precio,
                N
            )
            cant_sim = rng.normal(
                mat.cantidad,
                mat.cantidad * mat.variacion_cant,
                N
            )
            desp_sim = rng.uniform(mat.desperdicio * 0.8, mat.desperdicio * 1.2, N)
            pu_samples += np.maximum(cant_sim, 0) * (1 + desp_sim) * np.maximum(precio_sim, 0)

        # ── Mano de Obra vectorizada ──────────────────────────
        for mo in mano_obra:
            rend_sim = rng.normal(
                mo.rendimiento,
                mo.rendimiento * mo.variacion_rend,
                N
            )
            rend_sim = np.maximum(rend_sim, mo.rendimiento * 0.1)  # floor
            costo_cuadrilla = mo.cantidad_cuadrilla * mo.jornal_dia * mo.factor_prestaciones
            pu_samples += costo_cuadrilla / rend_sim

        # ── Equipo vectorizado ────────────────────────────────
        for eq in equipo:
            rend_sim = rng.normal(
                eq.rendimiento,
                eq.rendimiento * eq.variacion_rend,
                N
            )
            rend_sim = np.maximum(rend_sim, eq.rendimiento * 0.1)
            costo_eq_dia = eq.cantidad * eq.valor_hora * eq.horas_dia
            pu_samples += costo_eq_dia / (rend_sim * eq.horas_dia)

        # ── Aplicar AIU ───────────────────────────────────────
        pu_samples *= aiu.factor

        return (
            float(np.mean(pu_samples)),
            float(np.std(pu_samples)),
            float(np.percentile(pu_samples, 5)),
            float(np.percentile(pu_samples, 95))
        )

    # ── APU Jerárquico (Capítulo) ──────────────────────────────
    def calcular_capitulo(
        self,
        capitulo_id:  str,
        descripcion:  str,
        items: list[dict]  # list of {actividad, cantidad_total, apu_result}
    ) -> dict:
        """
        Suma APU × cantidad para obtener costo de capítulo.
        items = [{"actividad": "...", "cantidad": 150.0, "apu": APUResult}]
        """
        subtotal_det  = 0.0
        subtotal_mean = 0.0
        detalle       = []

        for item in items:
            apu: APUResult = item["apu"]
            cant: float    = item["cantidad"]
            det  = round(apu.precio_unitario * cant, 2)
            mean = round(apu.pu_mean * cant, 2) if apu.pu_mean > 0 else det
            subtotal_det  += det
            subtotal_mean += mean
            detalle.append({
                "actividad":       item.get("actividad", apu.descripcion),
                "unidad":          apu.unidad,
                "cantidad":        cant,
                "pu_determinista": apu.precio_unitario,
                "pu_media_mc":     apu.pu_mean,
                "pu_p05":          apu.pu_p05,
                "pu_p95":          apu.pu_p95,
                "subtotal":        det,
                "subtotal_mc":     mean,
                "norma_ref":       apu.norma_ref,
                "incertidumbre_pct": round(
                    (apu.pu_std / apu.pu_mean * 100) if apu.pu_mean > 0 else 0, 1
                ),
            })

        return {
            "capitulo_id":     capitulo_id,
            "descripcion":     descripcion,
            "items":           detalle,
            "subtotal_det":    round(subtotal_det,  2),
            "subtotal_mc_mean":round(subtotal_mean, 2),
            "n_actividades":   len(items),
        }

    def to_dict(self, result: APUResult) -> dict:
        """Serializar APUResult a dict para JSON/Supabase"""
        d = asdict(result)
        d["unidad"] = result.unidad.value
        d["aiu"] = {
            "administracion": result.aiu.administracion,
            "imprevistos":    result.aiu.imprevistos,
            "utilidad":       result.aiu.utilidad,
            "total_pct":      result.aiu.total_pct,
        }
        return d
