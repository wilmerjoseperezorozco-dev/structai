import dataclasses

from .schemas import (
    DisenoGeometricoRequest, PavimentosRequest, MantenimientoRequest, CierreNivelacionRequest,
    NTC2017Request, NTC4342Request, NTC121Request, NTC1299Request, NTC1362Request,
    NTC3459Request, NTC3493Request,
    NTC3502Request, NTC3760Request, NTC4018Request, NTC4024Request,
    NTC4924AgregadoRequest, NTC4924MamposteriaRequest, NTC5147Request, NTC6008Request,
)
from . import diseno_geometrico as dg
from . import pavimentos as pav
from . import mantenimiento as mant
from . import topografia as topo
from . import ntc_materiales_1 as ntc1
from . import ntc_materiales_2 as ntc2


# ── Diseño geométrico ───────────────────────────────────────────────────────

def validar_diseno_geometrico(req: DisenoGeometricoRequest) -> dict:
    manual = dg.ManualINVIAS2008()
    motor = dg.MotorValidacion(manual)
    params = dg.ParametrosDiseno(
        tipo_via=req.tipo_via, velocidad_diseno=req.velocidad_diseno, topografia=req.topografia,
        volumen_transito=req.volumen_transito, radio_curva=req.radio_curva,
        pendiente_longitudinal=req.pendiente_longitudinal, peralte=req.peralte,
        ancho_carril=req.ancho_carril, bombeo=req.bombeo, tipo_superficie=req.tipo_superficie,
    )
    return dataclasses.asdict(motor.validar(params))


# ── Pavimentos ───────────────────────────────────────────────────────────────

def disenar_pavimento(req: PavimentosRequest) -> dict:
    manual = pav.ManualPavimentos()
    disenador = pav.DisenadorPavimentos(manual)
    params = pav.ParametrosPavimento(
        tipo_pavimento=req.tipo_pavimento, tipo_via=req.tipo_via, tpd=req.tpd,
        esals_millones=req.esals_millones, cbr_subrasante=req.cbr_subrasante,
        modulo_subrasante=req.modulo_subrasante, ip_subrasante=req.ip_subrasante,
        temperatura_media=req.temperatura_media, espesor_subbase=req.espesor_subbase,
        espesor_base=req.espesor_base, modulo_subbase=req.modulo_subbase, modulo_base=req.modulo_base,
    )
    return dataclasses.asdict(disenador.disenar(params))


# ── Mantenimiento ────────────────────────────────────────────────────────────

def diagnosticar_mantenimiento(req: MantenimientoRequest) -> dict:
    manual = mant.ManualMantenimiento()
    diagnosticador = mant.DiagnosticadorMantenimiento(manual)
    params = mant.ParametrosMantenimiento(
        tipo_via=req.tipo_via, tipo_mantenimiento=req.tipo_mantenimiento,
        deterioro_tipo=req.deterioro_tipo, deterioro_gravedad=req.deterioro_gravedad,
        area_afectada=req.area_afectada, profundidad=req.profundidad, longitud=req.longitud,
        ancho=req.ancho, indice_condicion=req.indice_condicion, volumen_transito=req.volumen_transito,
    )
    return dataclasses.asdict(diagnosticador.diagnosticar(params))


# ── Topografía ───────────────────────────────────────────────────────────────

def verificar_cierre_nivelacion(req: CierreNivelacionRequest) -> dict:
    resultado = topo.verificar_cierre_nivelacion(req.error_medido_mm, req.distancia_km, req.estandar)
    return dataclasses.asdict(resultado)


# ── NTC materiales — parte 1 (ya retornan dict) ───────────────────────────────

def verificar_ntc2017(req: NTC2017Request) -> dict:
    adoquin = ntc1.Adoquin(
        nombre=req.nombre, aplicacion=req.aplicacion, tipo=req.tipo,
        largo_mm=req.largo_mm, ancho_mm=req.ancho_mm, espesor_mm=req.espesor_mm,
        resistencia_flexion_mpa=req.resistencia_flexion_mpa, absorcion_porcentaje=req.absorcion_porcentaje,
        fabricante=req.fabricante,
    )
    return adoquin.verificar_ntc2017()


def verificar_ntc4342(req: NTC4342Request) -> dict:
    geotextil = ntc1.Geotextil(
        nombre=req.nombre, tipo=req.tipo, retencion_asfaltica_l_m2=req.retencion_asfaltica_l_m2,
        composicion=req.composicion, porcentaje_poliolefinas=req.porcentaje_poliolefinas,
        fabricante=req.fabricante,
    )
    return geotextil.verificar_ntc4342()


def verificar_ntc121(req: NTC121Request) -> dict:
    cemento = ntc1.Cemento(
        nombre=req.nombre, tipo=req.tipo, resistencia_compresion_mpa=req.resistencia_compresion_mpa,
        tiempo_fraguado_inicial_min=req.tiempo_fraguado_inicial_min,
        tiempo_fraguado_final_min=req.tiempo_fraguado_final_min,
        expansion_autoclave_porcentaje=req.expansion_autoclave_porcentaje,
        finura_blaine_m2_kg=req.finura_blaine_m2_kg, densidad_g_cm3=req.densidad_g_cm3,
        fabricante=req.fabricante,
    )
    return cemento.verificar_ntc121()


def verificar_ntc1299(req: NTC1299Request) -> dict:
    aditivo = ntc1.Aditivo(
        nombre=req.nombre, tipo=req.tipo, descripcion=req.descripcion, aplicaciones=req.aplicaciones,
        fabricante=req.fabricante, dosificacion_recomendada=req.dosificacion_recomendada,
    )
    return aditivo.verificar_ntc1299()


def verificar_ntc1362(req: NTC1362Request) -> dict:
    cb = ntc1.CementoBlanco(
        nombre=req.nombre, tipo=req.tipo, resistencia_mpa=req.resistencia_mpa,
        tiempo_fraguado_inicial_min=req.tiempo_fraguado_inicial_min,
        tiempo_fraguado_final_min=req.tiempo_fraguado_final_min,
        expansion_autoclave_porcentaje=req.expansion_autoclave_porcentaje,
        finura_blaine_m2_kg=req.finura_blaine_m2_kg, blancura_porcentaje=req.blancura_porcentaje,
        contenido_alcalis_porcentaje=req.contenido_alcalis_porcentaje, fabricante=req.fabricante,
    )
    return cb.verificar_ntc1362()


def verificar_ntc3459(req: NTC3459Request) -> dict:
    analisis = ntc1.AnalisisAgua(**req.analisis.model_dump())
    muestra = ntc1.MuestraAgua(
        nombre=req.nombre, fuente=req.fuente, analisis=analisis,
        fecha_muestreo=req.fecha_muestreo, laboratorio=req.laboratorio,
    )
    return muestra.verificar_ntc3459(req.concreto_preesforzado)


def verificar_ntc3493(req: NTC3493Request) -> dict:
    analisis = ntc1.AnalisisAditivoMineral(**req.analisis.model_dump())
    aditivo = ntc1.AditivoMineral(
        nombre=req.nombre, clase=req.clase, analisis=analisis,
        fabricante=req.fabricante, origen=req.origen,
    )
    return aditivo.verificar_ntc3493(req.tolerancia_loi)


# ── NTC materiales — parte 2 (retornan dataclass Resultado*) ─────────────────

def verificar_ntc3502(req: NTC3502Request) -> dict:
    aditivo = ntc2.AditivoIncorporadorAire(
        nombre=req.nombre, tipo=req.tipo, contenido_aire_porcentaje=req.contenido_aire_porcentaje,
        dosificacion_recomendada=req.dosificacion_recomendada, libre_cloruros=req.libre_cloruros,
        ph=req.ph, densidad_g_cm3=req.densidad_g_cm3, fabricante=req.fabricante,
    )
    resultado = ntc2.MotorVerificacionNTC3502().verificar_aditivo(aditivo)
    return dataclasses.asdict(resultado)


def verificar_ntc3760(req: NTC3760Request) -> dict:
    pigmento = ntc2.PigmentoConcreto(
        nombre=req.nombre, tipo=req.tipo, presentacion=req.presentacion,
        dosificacion_maxima_porcentaje=req.dosificacion_maxima_porcentaje, color=req.color,
        resistencia_alcalina=req.resistencia_alcalina, resistencia_intemperie=req.resistencia_intemperie,
        fabricante=req.fabricante,
    )
    resultado = ntc2.MotorVerificacionNTC3760().verificar_pigmento(pigmento)
    return dataclasses.asdict(resultado)


def verificar_ntc4018(req: NTC4018Request) -> dict:
    analisis = ntc2.AnalisisEscoria(**req.analisis.model_dump())
    escoria = ntc2.EscoriaAltoHorno(
        nombre=req.nombre, grado=req.grado, analisis=analisis,
        fabricante=req.fabricante, origen=req.origen,
    )
    resultado = ntc2.MotorVerificacionNTC4018().verificar_escoria(escoria)
    return dataclasses.asdict(resultado)


def verificar_ntc4024(req: NTC4024Request) -> dict:
    dimensiones = ntc2.DimensionesPrefabricado(**req.dimensiones.model_dump())
    resultados = ntc2.ResultadosEnsayo(**req.resultados.model_dump())
    muestra = ntc2.MuestraPrefabricado(
        nombre=req.nombre, tipo=req.tipo, dimensiones=dimensiones, resultados=resultados,
        tamano_lote=req.tamano_lote, numero_especimenes=req.numero_especimenes,
        fabricante=req.fabricante, fecha_muestreo=req.fecha_muestreo,
    )
    resultado = ntc2.MotorVerificacionNTC4024().verificar_muestra(muestra)
    return dataclasses.asdict(resultado)


def verificar_ntc4924_agregado(req: NTC4924AgregadoRequest) -> dict:
    agregado = ntc2.AgregadoLiviano(
        nombre=req.nombre, tipo=req.tipo, densidad_aparente_kg_m3=req.densidad_aparente_kg_m3,
        absorcion_porcentaje=req.absorcion_porcentaje,
        resistencia_compresion_mpa=req.resistencia_compresion_mpa,
        tamano_maximo_mm=req.tamano_maximo_mm, modulo_finura=req.modulo_finura,
        fabricante=req.fabricante,
    )
    resultado = ntc2.MotorVerificacionNTC4924().verificar_agregado(agregado)
    return dataclasses.asdict(resultado)


def verificar_ntc4924_mamposteria(req: NTC4924MamposteriaRequest) -> dict:
    agregado = ntc2.AgregadoLiviano(**req.agregado.model_dump())
    unidad = ntc2.UnidadMamposteria(
        nombre=req.nombre, tipo=req.tipo, agregado=agregado, dimensiones_mm=req.dimensiones_mm,
        resistencia_compresion_mpa=req.resistencia_compresion_mpa,
        densidad_aparente_kg_m3=req.densidad_aparente_kg_m3, absorcion_porcentaje=req.absorcion_porcentaje,
        fabricante=req.fabricante,
    )
    resultado = ntc2.MotorVerificacionNTC4924().verificar_unidad_mamposteria(unidad)
    return dataclasses.asdict(resultado)


def verificar_ntc5147(req: NTC5147Request) -> dict:
    resultados = ntc2.ResultadoAbrasion(**req.resultados.model_dump())
    muestra = ntc2.MuestraAbrasion(
        nombre=req.nombre, tipo=req.tipo, resultados=resultados,
        fecha_ensayo=req.fecha_ensayo, laboratorio=req.laboratorio, fabricante=req.fabricante,
    )
    resultado = ntc2.MotorVerificacionNTC5147().verificar_muestra(muestra)
    return dataclasses.asdict(resultado)


def buscar_termino_ntc6008(req: NTC6008Request) -> dict:
    resultado = ntc2.MotorVerificacionNTC6008().buscar_termino(req.termino_busqueda)
    return dataclasses.asdict(resultado)


__all__ = [
    "DisenoGeometricoRequest", "PavimentosRequest", "MantenimientoRequest", "CierreNivelacionRequest",
    "NTC2017Request", "NTC4342Request", "NTC121Request", "NTC1299Request", "NTC1362Request",
    "NTC3459Request", "NTC3493Request",
    "NTC3502Request", "NTC3760Request", "NTC4018Request", "NTC4024Request",
    "NTC4924AgregadoRequest", "NTC4924MamposteriaRequest", "NTC5147Request", "NTC6008Request",
    "validar_diseno_geometrico", "disenar_pavimento", "diagnosticar_mantenimiento",
    "verificar_cierre_nivelacion",
    "verificar_ntc2017", "verificar_ntc4342", "verificar_ntc121", "verificar_ntc1299", "verificar_ntc1362",
    "verificar_ntc3459", "verificar_ntc3493",
    "verificar_ntc3502", "verificar_ntc3760", "verificar_ntc4018", "verificar_ntc4024",
    "verificar_ntc4924_agregado", "verificar_ntc4924_mamposteria", "verificar_ntc5147",
    "buscar_termino_ntc6008",
]
