from .schemas import (
    ZonaSismicaRequest,
    CilindroInput, SlumpInput, ConcretoRequest,
    USCSRequest, AASHTORequest, ProctorRequest, CBRRequest, GranulometriaRequest,
    AgregadoGruesoRequest, AgregadoFinoRequest, MezclaACIRequest,
)
from .sismica import zona_sismica, listar_zonas
from .lab_concreto import CilindroConcreto, EnsayoSlump, AnalisisConcreto
from .lab_suelos import ClasificadorUSCS, LimitesAtterberg, EnsayoProctor, EnsayoCBR, GranulometriaAgregado
from .lab_agregados import AgregadoGrueso, AgregadoFino, DisenoMezclaACI


def consultar_zona_sismica(req: ZonaSismicaRequest) -> dict:
    return zona_sismica(req.departamento)


def resumen_zonas_sismicas() -> dict:
    return listar_zonas()


def analizar_concreto(req: ConcretoRequest) -> dict:
    analisis = AnalisisConcreto(
        fc_diseno_MPa=req.fc_diseno_MPa,
        zona_sismica=req.zona_sismica,
        proyecto=req.proyecto,
        elemento=req.elemento,
    )
    for c in req.cilindros:
        analisis.agregar_cilindro(CilindroConcreto(**c.model_dump()))
    for s in req.slumps:
        analisis.agregar_slump(EnsayoSlump(**s.model_dump()))
    return analisis.informe_completo()


def clasificar_suelo_uscs(req: USCSRequest) -> dict:
    return ClasificadorUSCS.clasificar(
        pasa_200_pct=req.pasa_200_pct, pasa_4_pct=req.pasa_4_pct,
        d10=req.d10, d30=req.d30, d60=req.d60, ll=req.ll, ip=req.ip,
    )


def clasificar_suelo_aashto(req: AASHTORequest) -> dict:
    return ClasificadorUSCS.aashto(ll=req.ll, ip=req.ip, pasa_200_pct=req.pasa_200_pct)


def analizar_proctor(req: ProctorRequest) -> dict:
    proctor = EnsayoProctor(id_muestra=req.id_muestra, tipo=req.tipo, puntos=req.puntos)
    resultado = proctor.resumen()
    if req.densidad_campo_gcm3 is not None:
        resultado["verificacion_campo"] = proctor.verificar_compactacion(
            req.densidad_campo_gcm3, req.porcentaje_minimo
        )
    return resultado


def analizar_cbr(req: CBRRequest) -> dict:
    cbr = EnsayoCBR(
        id_muestra=req.id_muestra, carga_254_kN=req.carga_254_kN, carga_508_kN=req.carga_508_kN,
        densidad_seca=req.densidad_seca, humedad_pct=req.humedad_pct, condicion=req.condicion,
    )
    resultado = cbr.resumen()
    if req.esal_millones is not None:
        resultado["pavimento"] = cbr.espesor_pavimento_cm(req.esal_millones)
    return resultado


def analizar_granulometria(req: GranulometriaRequest) -> dict:
    return GranulometriaAgregado(id_muestra=req.id_muestra, tamices=req.tamices).resumen()


def verificar_agregado_grueso(req: AgregadoGruesoRequest) -> dict:
    agregado = AgregadoGrueso(
        id_muestra=req.id_muestra, origen=req.origen,
        masa_sss_g=req.masa_sss_g, masa_seca_g=req.masa_seca_g, masa_sumergida_g=req.masa_sumergida_g,
        perdida_LA_pct=req.perdida_LA_pct,
        particulas_planas_pct=req.particulas_planas_pct, particulas_alargadas_pct=req.particulas_alargadas_pct,
    )
    return agregado.verificar_ntc174(req.uso)


def verificar_agregado_fino(req: AgregadoFinoRequest) -> dict:
    agregado = AgregadoFino(
        id_muestra=req.id_muestra, masa_sss_g=req.masa_sss_g, masa_seca_g=req.masa_seca_g,
        masa_frasco_agua=req.masa_frasco_agua, masa_frasco_agua_muestra=req.masa_frasco_agua_muestra,
        modulo_finura=req.modulo_finura, impurezas_organicas=req.impurezas_organicas,
    )
    resultado = agregado.verificar_ntc174()
    resultado["clasificacion_mf"] = agregado.clasificacion_mf()
    return resultado


def disenar_mezcla_aci(req: MezclaACIRequest) -> dict:
    diseno = DisenoMezclaACI(
        fc_MPa=req.fc_MPa, tamaño_max_agregado_mm=req.tamaño_max_agregado_mm,
        asentamiento_mm=req.asentamiento_mm, zona_sismica=req.zona_sismica,
    )
    return diseno.calcular(densidad_fino=req.densidad_fino, densidad_grueso=req.densidad_grueso)


__all__ = [
    "ZonaSismicaRequest", "CilindroInput", "SlumpInput", "ConcretoRequest",
    "USCSRequest", "AASHTORequest", "ProctorRequest", "CBRRequest", "GranulometriaRequest",
    "AgregadoGruesoRequest", "AgregadoFinoRequest", "MezclaACIRequest",
    "consultar_zona_sismica", "resumen_zonas_sismicas", "analizar_concreto",
    "clasificar_suelo_uscs", "clasificar_suelo_aashto", "analizar_proctor", "analizar_cbr",
    "analizar_granulometria", "verificar_agregado_grueso", "verificar_agregado_fino", "disenar_mezcla_aci",
]
