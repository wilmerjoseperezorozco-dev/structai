"""
AquaAI — Verificador de requisitos de la Resolución 0330/2017
Reglas deterministas; cada una devuelve cumple / no_cumple / requiere_criterio con su fuente.
'requiere_criterio' significa que la norma habilita una excepción o una obra que depende del diseñador, no que el diseño cumpla.
"""
from __future__ import annotations

from .marco_normativo import TABLA_16, TABLA_20, regla
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


def verificar_periodo_retorno(tr_anios: float, tipo_tramo: str) -> VerificacionNormativa:
    if tipo_tramo not in TABLA_16:
        raise ValueError(f"Tipo de tramo '{tipo_tramo}' no reconocido. Opciones: {sorted(TABLA_16)}")
    descripcion, minimo = TABLA_16[tipo_tramo]
    if tr_anios >= minimo:
        return _v("periodo_retorno_minimo", "cumple", f"TR = {tr_anios:g} años ≥ {minimo} años exigidos ({descripcion}).")
    return _v("periodo_retorno_minimo", "no_cumple", f"TR = {tr_anios:g} años < {minimo} años mínimos de la Tabla 16 ({descripcion}).")


def verificar_velocidad(v_ms: float, pendiente_terreno_m_m: float | None, diametro_mm: float, caudal_ls: float) -> VerificacionNormativa:
    vmax, tope = regla("velocidad_max_colector").valor, regla("velocidad_tope_absoluto").valor
    if v_ms <= vmax:
        return _v("velocidad_max_colector", "cumple", f"V = {v_ms:.2f} m/s ≤ {vmax:g} m/s.")
    if v_ms > tope:
        return _v("velocidad_tope_absoluto", "no_cumple", f"V = {v_ms:.2f} m/s > {tope:g} m/s: ni la excepción por pendiente, diámetro o caudal permite superar {tope:g} m/s.")
    cond = []
    if pendiente_terreno_m_m is not None and pendiente_terreno_m_m > regla("velocidad_excepcion").valor:
        cond.append(f"pendiente del terreno {pendiente_terreno_m_m * 100:.0f} % > 30 %")
    if diametro_mm >= 600:
        cond.append(f"diámetro {diametro_mm:g} mm ≥ 600 mm")
    if caudal_ls > 500:
        cond.append(f"caudal {caudal_ls:g} L/s > 500 L/s")
    if cond:
        return _v("velocidad_excepcion", "requiere_criterio",
                  f"V = {v_ms:.2f} m/s > {vmax:g} m/s, permitido por excepción ({'; '.join(cond)}). Debe respetar el límite del material y {tope:g} m/s, "
                  "usar revestimiento interno especial contra la abrasión y prever protecciones y disipación de energía.")
    return _v("velocidad_max_colector", "no_cumple",
              f"V = {v_ms:.2f} m/s > {vmax:g} m/s sin condición de excepción acreditada"
              + ("" if pendiente_terreno_m_m is not None else " (no se informó la pendiente del terreno; si supera 30 %, informarla)") + ".")


def diametro_camara_minimo(diametro_entrada_mm: float) -> float | None:
    """Diámetro interno real mínimo de la tubería de la cámara de caída (Tabla 20). None si la entrada supera 900 mm (exige transición)."""
    for hasta, minimo in TABLA_20:
        if diametro_entrada_mm <= hasta:
            return minimo
    return None


def verificar_caida(desnivel_m: float, diametro_entrada_mm: float | None = None) -> VerificacionNormativa:
    c, d = regla("camara_caida_desnivel").valor, regla("disipacion_desnivel").valor
    if desnivel_m <= c:
        return _v("camara_caida_desnivel", "cumple", f"Desnivel {desnivel_m:g} m ≤ {c:g} m: no requiere cámara de caída.")
    extra = ""
    if diametro_entrada_mm is not None:
        minimo = diametro_camara_minimo(diametro_entrada_mm)
        extra = (f" Diámetro interno real mínimo de la tubería de la cámara: {minimo:g} mm (Tabla 20)." if minimo is not None
                 else " Con entrada mayor a 900 mm debe diseñarse una transición entre el colector y la estructura de conexión que garantice la reducción de energía.")
    if desnivel_m <= d:
        return _v("camara_caida_desnivel", "requiere_criterio", f"Desnivel {desnivel_m:g} m > {c:g} m: requiere cámara de caída.{extra}")
    return _v("disipacion_desnivel", "requiere_criterio", f"Desnivel {desnivel_m:g} m > {d:g} m: requiere cámara de caída y estructuras de disipación de energía.{extra}")


def verificar_res0330(desnivel_caida_m=None, diametro_entrada_mm=None, reduccion_pico_suds_pct=None, suds_viable=None) -> dict:
    """Evalúa solo los requisitos para los que se informó dato; devuelve también la vigencia y lo no verificado."""
    from .marco_normativo import NO_VERIFICADO, vigencia_ras2000
    out = []
    if desnivel_caida_m is not None:
        out.append(verificar_caida(desnivel_caida_m, diametro_entrada_mm))
    if reduccion_pico_suds_pct is not None or suds_viable is False:
        out.append(verificar_suds(reduccion_pico_suds_pct or 0.0, suds_viable))
    return {"verificaciones_normativas": out, "vigencia": vigencia_ras2000(), "no_verificado": list(NO_VERIFICADO)}


def verificar_suds(reduccion_pico_pct: float, viable: bool | None = None) -> VerificacionNormativa:
    """Art. 153 (mod. Res. 799/2021): se evalúa la viabilidad; si es viable, la reducción del pico no debe ser menor a 30 %.
    viable=False significa que la evaluación de viabilidad concluyó que no lo es (debe estar documentada); None = no informado, se exige el porcentaje."""
    m = regla("suds_reduccion_pico").valor
    if viable is False:
        return _v("suds_reduccion_pico", "cumple", "Se informó que la evaluación de viabilidad de SUDS concluyó que no es viable; debe estar documentada con los seis aspectos del Art. 153.")
    if reduccion_pico_pct >= m:
        return _v("suds_reduccion_pico", "cumple", f"Reducción del pico {reduccion_pico_pct:g} % ≥ {m:g} %.")
    return _v("suds_reduccion_pico", "no_cumple", f"Reducción del pico {reduccion_pico_pct:g} % < {m:g} % exigido si los SUDS son viables.")
