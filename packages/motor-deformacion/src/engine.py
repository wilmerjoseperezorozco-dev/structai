"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — ENGINE
Orquesta geometría (geometry) + teoría de vigas (beam_theory) + teoría de
columnas (column_theory) + incertidumbre (uncertainty) sobre un
ElementoEstructural arbitrario. Diseñado para secciones/cargas que cambian
de un caso a otro (no depende de un catálogo fijo de perfiles).
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Optional

from . import beam_theory, column_theory, uncertainty
from .clasificador import elemento_desde_deteccion
from .models import (
    CargaAplicada, CondicionApoyo, ElementoEstructural, ResultadoDeformacion, TipoCarga, TipoElemento,
)


class MotorDeformacion:
    """Motor de análisis de deformación y esfuerzo para elementos estructurales."""

    def _resolver_caso(self, elemento: ElementoEstructural, carga: CargaAplicada) -> beam_theory.ResultadoViga:
        EI = elemento.material.E * elemento.seccion.Ix
        L = elemento.longitud
        cond = elemento.condicion_apoyo

        usa_formula_cerrada = cond in (
            CondicionApoyo.CANTILEVER, CondicionApoyo.SIMPLE, CondicionApoyo.EMPOTRADA_EMPOTRADA,
        ) and carga.tipo in (TipoCarga.PUNTUAL, TipoCarga.DISTRIBUIDA_UNIFORME)

        if usa_formula_cerrada:
            a = (carga.posicion if carga.posicion is not None else 0.5) * L
            if cond == CondicionApoyo.CANTILEVER:
                if carga.tipo == TipoCarga.PUNTUAL:
                    return beam_theory.cantilever_puntual(carga.magnitud, a, L, EI)
                return beam_theory.cantilever_udl(carga.magnitud, L, EI)
            if cond == CondicionApoyo.SIMPLE:
                if carga.tipo == TipoCarga.PUNTUAL:
                    a = min(max(a, 1e-9), L - 1e-9)
                    return beam_theory.simple_puntual(carga.magnitud, a, L, EI)
                return beam_theory.simple_udl(carga.magnitud, L, EI)
            if carga.tipo == TipoCarga.PUNTUAL:
                # Fórmula cerrada empotrada-empotrada disponible solo para carga centrada;
                # otras posiciones se resuelven con el solver general.
                if carga.posicion is None or abs(carga.posicion - 0.5) < 1e-6:
                    return beam_theory.empotrada_empotrada_puntual(carga.magnitud, L, EI)
            else:
                return beam_theory.empotrada_empotrada_udl(carga.magnitud, L, EI)

        # Caso general: EMPOTRADA_APOYADA, carga distribuida arbitraria, o
        # carga puntual fuera de las posiciones con fórmula cerrada.
        if carga.tipo == TipoCarga.DISTRIBUIDA_GENERAL and carga.funcion is not None:
            w_func = carga.funcion
        elif carga.tipo == TipoCarga.PUNTUAL:
            a = (carga.posicion if carga.posicion is not None else 0.5) * L
            ancho = max(L / 400.0, 1e-4)

            def w_func(x: float, _a=a, _P=carga.magnitud, _ancho=ancho) -> float:
                return _P / _ancho if abs(x - _a) <= _ancho / 2 else 0.0
        else:
            def w_func(x: float, _w=carga.magnitud) -> float:
                return _w

        return beam_theory.resolver_general(w_func, L, EI, cond)

    def analizar_viga(
        self, elemento: ElementoEstructural, cargas: list[CargaAplicada], run_montecarlo: bool = True,
    ) -> ResultadoDeformacion:
        """Análisis de flexión: deflexión, esfuerzo de flexión, esfuerzo cortante."""
        if not cargas:
            raise ValueError("Se requiere al menos una carga para analizar la viga")

        resultados = [(self._resolver_caso(elemento, c), c) for c in cargas]
        superpuesto = beam_theory.superponer([r for r, _ in resultados], elemento.longitud)
        x_star = superpuesto.x_deflexion_max

        # El punto de momento máximo NO coincide en general con el de deflexión
        # máxima (p.ej. en un voladizo: M_max está en el empotramiento, v_max en
        # la punta) — se ubica por separado escaneando el dominio.
        xs_scan = [elemento.longitud * i / 2000.0 for i in range(2001)]
        m_vals = [superpuesto.M(x) for x in xs_scan]
        idx_m = max(range(len(m_vals)), key=lambda i: abs(m_vals[i]))
        x_m_star = xs_scan[idx_m]

        seccion = elemento.seccion
        material = elemento.material
        S_det = min(seccion.modulo_seccion_sup, seccion.modulo_seccion_inf) if seccion.c_inf > 0 else seccion.modulo_seccion_sup

        M_det = superpuesto.momento_max
        V_det = superpuesto.cortante_max
        esfuerzo_flexion = M_det / S_det if S_det > 0 else float("inf")
        esfuerzo_cortante = 0.0
        if seccion.Q_max and seccion.ancho_alma:
            esfuerzo_cortante = V_det * seccion.Q_max / (seccion.Ix * seccion.ancho_alma)

        fs = material.fy / esfuerzo_flexion if esfuerzo_flexion > 0 else float("inf")
        deflexion_admisible = elemento.deflexion_admisible

        notas = [
            f"Punto crítico de deflexión x*={x_star:.3f} m · punto crítico de momento x_M*={x_m_star:.3f} m (de {elemento.longitud:.3f} m)",
            "M(x), V(x) no dependen de E ni I en vigas prismáticas con EI constante — "
            "solo la deflexión depende del material y la sección.",
        ]

        resultado = ResultadoDeformacion(
            elemento_id=elemento.id, tipo_analisis="flexion",
            deflexion_max=superpuesto.deflexion_max, momento_max=M_det, cortante_max=V_det,
            esfuerzo_flexion_max=esfuerzo_flexion, esfuerzo_cortante_max=esfuerzo_cortante,
            factor_seguridad=fs, deflexion_admisible=deflexion_admisible,
            cumple_deflexion=superpuesto.deflexion_max <= deflexion_admisible,
            cumple_esfuerzo=fs >= 1.0, notas=notas,
        )

        if run_montecarlo:
            contribuciones = [
                uncertainty.ContribucionCarga(
                    v_det=r.v(x_star), M_det=r.M(x_m_star), carga_mean=c.magnitud, cov_carga=c.cov_carga,
                )
                for r, c in resultados
            ]
            inc = uncertainty.propagar_flexion(
                contribuciones, S_det,
                material.E, material.cov_E, material.fy, material.cov_fy,
                deflexion_admisible, cov_dimension=seccion.cov_dimension,
            )
            resultado.deflexion_mean = inc.deflexion.mean
            resultado.deflexion_std = inc.deflexion.std
            resultado.deflexion_p05 = inc.deflexion.p05
            resultado.deflexion_p95 = inc.deflexion.p95
            resultado.esfuerzo_mean = inc.esfuerzo.mean
            resultado.esfuerzo_std = inc.esfuerzo.std
            resultado.esfuerzo_p05 = inc.esfuerzo.p05
            resultado.esfuerzo_p95 = inc.esfuerzo.p95
            resultado.indice_confiabilidad = inc.indice_confiabilidad_esfuerzo
            resultado.probabilidad_falla = inc.probabilidad_falla_esfuerzo
            resultado.notas.append(
                f"IC90% esfuerzo flexión: [{inc.esfuerzo.p05/1e6:.1f}, {inc.esfuerzo.p95/1e6:.1f}] MPa "
                f"· β={inc.indice_confiabilidad_esfuerzo:.2f} · Pf≈{inc.probabilidad_falla_esfuerzo:.2e}"
            )

        return resultado

    def analizar_columna(
        self, elemento: ElementoEstructural, carga_axial: CargaAplicada,
        momento_adicional: float = 0.0, run_montecarlo: bool = True,
    ) -> ResultadoDeformacion:
        """Análisis de pandeo (Euler/Johnson) + esfuerzo combinado axial+flexión."""
        material = elemento.material
        seccion = elemento.seccion
        L = elemento.longitud
        K = elemento.K

        pandeo = column_theory.analizar_columna(
            carga_axial.magnitud, material.E, seccion.Ix, seccion.area, material.fy, K, L,
        )

        S_det = min(seccion.modulo_seccion_sup, seccion.modulo_seccion_inf) if seccion.c_inf > 0 else seccion.modulo_seccion_sup
        esfuerzo_comb, factor_amp = column_theory.esfuerzo_combinado_viga_columna(
            carga_axial.magnitud, seccion.area, momento_adicional, S_det, pandeo.carga_critica,
        )

        notas = [
            f"Régimen de pandeo: {pandeo.regimen} · esbeltez λ={pandeo.esbeltez:.1f} "
            f"(transición λc={pandeo.esbeltez_transicion:.1f})",
            f"Factor de amplificación P-Δ: {factor_amp:.3f}" if factor_amp != float("inf") else "P ≥ Pcr — columna inestable",
        ]

        resultado = ResultadoDeformacion(
            elemento_id=elemento.id, tipo_analisis="pandeo",
            esfuerzo_flexion_max=esfuerzo_comb, carga_critica_pandeo=pandeo.carga_critica,
            factor_seguridad=pandeo.factor_seguridad,
            deflexion_admisible=elemento.deflexion_admisible,
            cumple_esfuerzo=(esfuerzo_comb < material.fy) if esfuerzo_comb != float("inf") else False,
            cumple_deflexion=True, notas=notas,
        )

        if run_montecarlo:
            inc = uncertainty.propagar_pandeo(
                pandeo.carga_critica, pandeo.esbeltez, pandeo.regimen,
                material.E, material.cov_E, material.fy, material.cov_fy,
                seccion.area, seccion.cov_dimension,
                carga_axial.magnitud, carga_axial.cov_carga,
            )
            resultado.deflexion_mean = inc.carga_critica.mean
            resultado.deflexion_std = inc.carga_critica.std
            resultado.deflexion_p05 = inc.carga_critica.p05
            resultado.deflexion_p95 = inc.carga_critica.p95
            resultado.indice_confiabilidad = inc.indice_confiabilidad
            resultado.probabilidad_falla = inc.probabilidad_falla
            resultado.notas.append(
                f"IC90% carga crítica pandeo: [{inc.carga_critica.p05/1e3:.1f}, {inc.carga_critica.p95/1e3:.1f}] kN "
                f"· β={inc.indice_confiabilidad:.2f} · Pf≈{inc.probabilidad_falla:.2e}"
            )

        return resultado

    def analizar_elemento(
        self, elemento: ElementoEstructural, cargas: list[CargaAplicada], run_montecarlo: bool = True,
    ) -> ResultadoDeformacion:
        """Punto de entrada único: despacha a flexión o pandeo según tipo_elemento."""
        if elemento.tipo_elemento == TipoElemento.COLUMNA:
            carga_axial = next((c for c in cargas if c.tipo == TipoCarga.PUNTUAL), cargas[0])
            momento = sum(c.magnitud for c in cargas if c.descripcion == "momento")
            return self.analizar_columna(elemento, carga_axial, momento, run_montecarlo)
        return self.analizar_viga(elemento, cargas, run_montecarlo)

    def analizar_desde_deteccion(
        self, clase_detectada: str, cargas: list[CargaAplicada],
        longitud: Optional[float] = None, run_montecarlo: bool = True,
    ) -> Optional[ResultadoDeformacion]:
        """
        Pipeline clasificación → deformación: toma la clase que devolvió el
        detector de visión (/detect) y arma un ElementoEstructural de partida
        con dimensiones típicas del catálogo Construdata para analizarlo de
        inmediato. Retorna None si la clase no es analizable estructuralmente.
        """
        elemento = elemento_desde_deteccion(clase_detectada, longitud=longitud)
        if elemento is None:
            return None
        return self.analizar_elemento(elemento, cargas, run_montecarlo)
