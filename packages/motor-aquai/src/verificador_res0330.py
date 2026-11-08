"""
AquaAI — Verificador de requisitos de la Resolución 0330/2017
Reglas deterministas; cada una devuelve cumple / no_cumple / requiere_criterio con su fuente.
'requiere_criterio' significa que la norma habilita una excepción que depende del diseñador, no que el diseño cumpla.
"""
from __future__ import annotations

from .marco_normativo import regla
from .schemas import VerificacionNormativa


def _v(id_: str, estado: str, detalle: str) -> VerificacionNormativa:
    r = regla(id_)
    return VerificacionNormativa(regla=id_, fuente=f"Res. 0330/2017, {r.articulo}", estado=estado, detalle=detalle)


def verificar_metodo_racional(area_ha: float) -> VerificacionNormativa:
    lim = regla("racional_area_max").valor
    if area_ha < lim:
        return _v("racional_area_max", "cumple", f"Área {area_ha:g} ha < {lim:g} ha: el método racional está permitido.")
    return _v("racional_area_max", "no_cumple",
              f"Área {area_ha:g} ha ≥ {lim:g} ha: la norma no permite el método racional para colectores y canales de aguas lluvias; "
              "usar un modelo lluvia-escorrentía basado en abstracciones.")


def verificar_velocidad(v_ms: float, pendiente_terreno_m_m: float | None, diametro_mm: float, caudal_ls: float) -> VerificacionNormativa:
    vmax = regla("velocidad_max_colector").valor
    if v_ms <= vmax:
        return _v("velocidad_max_colector", "cumple", f"V = {v_ms:.2f} m/s ≤ {vmax:g} m/s.")
    cond = []
    if pendiente_terreno_m_m is not None and pendiente_terreno_m_m > regla("velocidad_excepcion").valor:
        cond.append(f"pendiente del terreno {pendiente_terreno_m_m * 100:.0f} % > 30 %")
    if diametro_mm >= 600:
        cond.append(f"diámetro {diametro_mm:g} mm ≥ 600 mm")
    if caudal_ls > 500:
        cond.append(f"caudal {caudal_ls:g} L/s > 500 L/s")
    if cond:
        return _v("velocidad_excepcion", "requiere_criterio",
                  f"V = {v_ms:.2f} m/s > {vmax:g} m/s, permitido por excepción ({'; '.join(cond)}). Debe respetar el límite del material y prever protecciones y disipación de energía.")
    return _v("velocidad_max_colector", "no_cumple",
              f"V = {v_ms:.2f} m/s > {vmax:g} m/s sin condición de excepción acreditada"
              + ("" if pendiente_terreno_m_m is not None else " (no se informó la pendiente del terreno; si supera 30 %, informarla)") + ".")


def verificar_caida(desnivel_m: float) -> VerificacionNormativa:
    c, d = regla("camara_caida_desnivel").valor, regla("disipacion_desnivel").valor
    if desnivel_m <= c:
        return _v("camara_caida_desnivel", "cumple", f"Desnivel {desnivel_m:g} m ≤ {c:g} m: no requiere cámara de caída.")
    if desnivel_m <= d:
        return _v("camara_caida_desnivel", "requiere_criterio", f"Desnivel {desnivel_m:g} m > {c:g} m: requiere cámara de caída (Tabla 20 define el diámetro).")
    return _v("disipacion_desnivel", "requiere_criterio", f"Desnivel {desnivel_m:g} m > {d:g} m: requiere cámara de caída y estructuras de disipación de energía.")


def verificar_suds(reduccion_pico_pct: float) -> VerificacionNormativa:
    m = regla("suds_reduccion_pico").valor
    if reduccion_pico_pct >= m:
        return _v("suds_reduccion_pico", "cumple", f"Reducción del pico {reduccion_pico_pct:g} % ≥ {m:g} %.")
    return _v("suds_reduccion_pico", "no_cumple", f"Reducción del pico {reduccion_pico_pct:g} % < {m:g} % exigido en nuevos desarrollos.")
