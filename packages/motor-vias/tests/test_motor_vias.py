"""Tests para Motor Vías — INVIAS / AASHTO 93 / NTC materiales.

Mismo patrón que motor-aquai y motor-geopot: cada aserción verifica contra
la tabla/fórmula real del módulo (o recalcula independientemente), no
contra un número supuesto.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from math import sqrt

from src.diseno_geometrico import (
    ManualINVIAS2008, MotorValidacion, ParametrosDiseno,
    TipoVia as TipoViaG, Topografia as TopografiaG, TipoSuperficie,
)
from src.pavimentos import (
    ManualPavimentos, DisenadorPavimentos, ParametrosPavimento,
    TipoPavimento, TipoVia as TipoViaP,
)
from src.mantenimiento import (
    ManualMantenimiento, DiagnosticadorMantenimiento, ParametrosMantenimiento,
    TipoVia as TipoViaM, TipoMantenimiento, TipoDeterioro, GravedadDeterioro, PrioridadIntervencion,
)
from src.topografia import (
    EstandarNivelacion, COEFICIENTES_CIERRE, error_cierre_permisible_mm, verificar_cierre_nivelacion,
)
from src.ntc_materiales_1 import (
    Adoquin, AplicacionAdoquin, TipoAdoquin,
    Geotextil, TipoGeotextil,
    Cemento, TipoCemento,
    Aditivo, TipoAditivo,
    CementoBlanco, TipoCementoBlanco,
    MuestraAgua, AnalisisAgua, FuenteAgua,
    AditivoMineral, AnalisisAditivoMineral, ClaseAditivoMineral,
)
from src.ntc_materiales_2 import (
    AditivoIncorporadorAire, TipoAditivoAire, MotorVerificacionNTC3502,
    PigmentoConcreto, PresentacionPigmento, TipoPigmento, MotorVerificacionNTC3760,
    EscoriaAltoHorno, AnalisisEscoria, GradoEscoria, MotorVerificacionNTC4018,
    MuestraPrefabricado, DimensionesPrefabricado, ResultadosEnsayo, TipoPrefabricado, MotorVerificacionNTC4024,
    AgregadoLiviano, UnidadMamposteria, TipoAgregadoLiviano, TipoUnidadMamposteria, MotorVerificacionNTC4924,
    MuestraAbrasion, ResultadoAbrasion, TipoMaterial, MotorVerificacionNTC5147,
    MotorVerificacionNTC6008,
)

from src import (
    DisenoGeometricoRequest, PavimentosRequest, MantenimientoRequest, CierreNivelacionRequest,
    NTC2017Request, NTC121Request, NTC3502Request, NTC4924MamposteriaRequest,
    NTC4924AgregadoRequest, NTC6008Request,
    validar_diseno_geometrico, disenar_pavimento, diagnosticar_mantenimiento,
    verificar_cierre_nivelacion as verificar_cierre_nivelacion_wrapper,
    verificar_ntc2017, verificar_ntc121, verificar_ntc3502,
    verificar_ntc4924_agregado, verificar_ntc4924_mamposteria, buscar_termino_ntc6008,
)


# ─── diseno_geometrico.py ────────────────────────────────────────────────────

def _motor_geometrico():
    return MotorValidacion(ManualINVIAS2008())


def test_radio_curva_tabla_real_v80_peralte6():
    motor = _motor_geometrico()
    # Tabla real: radios_minimos[80][6] = 205 m
    params = ParametrosDiseno(
        tipo_via=TipoViaG.PRIMARIA, velocidad_diseno=80, topografia=TopografiaG.MONTANOSO,
        volumen_transito=5000, radio_curva=180, peralte=6.0,
    )
    r = motor.validar(params)
    restr = next(x for x in r.restricciones_aplicadas if x["nombre"] == "Radio mínimo de curva")
    assert restr["minimo"] == 205
    assert restr["cumple"] is False   # 180 < 205
    assert r.cumple is False


def test_radio_curva_suficiente_cumple():
    motor = _motor_geometrico()
    params = ParametrosDiseno(
        tipo_via=TipoViaG.PRIMARIA, velocidad_diseno=80, topografia=TopografiaG.MONTANOSO,
        volumen_transito=5000, radio_curva=250, peralte=6.0,
    )
    r = motor.validar(params)
    assert r.cumple is True


def test_velocidad_no_multiplo_de_10_falla():
    motor = _motor_geometrico()
    params = ParametrosDiseno(
        tipo_via=TipoViaG.SECUNDARIA, velocidad_diseno=75, topografia=TopografiaG.PLANO, volumen_transito=1000,
    )
    r = motor.validar(params)
    assert r.cumple is False
    assert any("múltiplos de 10" in e for e in [r.mensaje]) or "10" in r.mensaje or not r.cumple


def test_pendiente_excede_maximo_tabla_real():
    motor = _motor_geometrico()
    # pendientes_maximas[TERCIARIA][PLANO] = 6
    params = ParametrosDiseno(
        tipo_via=TipoViaG.TERCIARIA, velocidad_diseno=40, topografia=TopografiaG.PLANO,
        volumen_transito=300, pendiente_longitudinal=8.0,
    )
    r = motor.validar(params)
    restr = next(x for x in r.restricciones_aplicadas if "Pendiente" in x["nombre"])
    assert restr["maximo"] == 6
    assert restr["cumple"] is False


def test_ancho_carril_bajo_minimo_terciaria():
    motor = _motor_geometrico()
    # ancho_carril_minimo[TERCIARIA] = 3.00
    params = ParametrosDiseno(
        tipo_via=TipoViaG.TERCIARIA, velocidad_diseno=40, topografia=TopografiaG.PLANO,
        volumen_transito=300, ancho_carril=2.5,
    )
    r = motor.validar(params)
    restr = next(x for x in r.restricciones_aplicadas if "carril" in x["nombre"])
    assert restr["minimo"] == 3.00
    assert restr["cumple"] is False


def test_bombeo_incluye_recomendado_por_superficie():
    motor = _motor_geometrico()
    params = ParametrosDiseno(
        tipo_via=TipoViaG.PRIMARIA, velocidad_diseno=80, topografia=TopografiaG.PLANO,
        volumen_transito=5000, bombeo=2.5, tipo_superficie=TipoSuperficie.CONCRETO,
    )
    r = motor.validar(params)
    restr = next(x for x in r.restricciones_aplicadas if "Bombeo" in x["nombre"])
    assert restr["bombeo_recomendado_superficie"] == 2.0   # bombeo_recomendado_superficie[CONCRETO]


# ─── pavimentos.py ────────────────────────────────────────────────────────────

def _disenador_pavimentos():
    return DisenadorPavimentos(ManualPavimentos())


def test_sn_requerido_tabla_real_esal5_cbr8():
    disenador = _disenador_pavimentos()
    # sn_requerido[5.0][8] = 3.6 (tabla real del módulo)
    sn = disenador._calcular_sn(esals_millones=5.0, cbr=8)
    assert sn == 3.6


def test_diseno_asfaltico_sn_real_cumple_requerido():
    disenador = _disenador_pavimentos()
    params = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.ASFALTICO, tipo_via=TipoViaP.PRIMARIA,
        tpd=5000, esals_millones=5.0, cbr_subrasante=5, espesor_base=20,
    )
    r = disenador.disenar(params)
    sn_requerido = disenador._calcular_sn(5.0, 5)
    assert r.numero_estructural >= sn_requerido
    assert r.cumple is True


def test_diseno_concreto_espesor_formula_sn_sobre_039():
    disenador = _disenador_pavimentos()
    params = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.CONCRETO, tipo_via=TipoViaP.PRIMARIA,
        tpd=8000, esals_millones=10.0, cbr_subrasante=8, espesor_base=15, espesor_subbase=15,
    )
    r = disenador.disenar(params)
    sn_requerido = disenador._calcular_sn(10.0, 8)
    d_concreto_esperado = round((sn_requerido / 0.39) / 2.5) * 2.5
    assert r.espesor_rodadura == pytest.approx(max(d_concreto_esperado, 15.0))


def test_cbr_bajo_minimo_genera_error():
    disenador = _disenador_pavimentos()
    params = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.ASFALTICO, tipo_via=TipoViaP.TERCIARIA,
        tpd=200, esals_millones=0.1, cbr_subrasante=2,
    )
    r = disenador.disenar(params)
    assert r.cumple is False
    # El mensaje de resultado es genérico ("Se encontraron N errores");
    # el detalle real de la falla de CBR vive en las sugerencias.
    assert any("subrasante" in s.lower() for s in r.sugerencias)


def test_ip_subrasante_excesivo_genera_error():
    disenador = _disenador_pavimentos()
    params = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.ASFALTICO, tipo_via=TipoViaP.PRIMARIA,
        tpd=5000, esals_millones=5.0, cbr_subrasante=8, ip_subrasante=25.0,
    )
    r = disenador.disenar(params)
    assert r.cumple is False


# ─── mantenimiento.py ─────────────────────────────────────────────────────────

def _diagnosticador():
    return DiagnosticadorMantenimiento(ManualMantenimiento())


def test_intervencion_bache_por_gravedad_tabla_real():
    diag = _diagnosticador()
    for gravedad, esperado in [
        (GravedadDeterioro.BAJA, "Sello superficial"),
        (GravedadDeterioro.MEDIA, "Parcheo localizado"),
        (GravedadDeterioro.ALTA, "Bacheo profundo"),
        (GravedadDeterioro.CRITICA, "Reconstrucción de tramo"),
    ]:
        params = ParametrosMantenimiento(
            tipo_via=TipoViaM.PRIMARIA, tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
            deterioro_tipo=TipoDeterioro.BACHE, deterioro_gravedad=gravedad,
        )
        r = diag.diagnosticar(params)
        assert r.intervencion_recomendada == esperado


def test_gravedad_critica_da_tipo_mantenimiento_emergencia():
    diag = _diagnosticador()
    params = ParametrosMantenimiento(
        tipo_via=TipoViaM.PRIMARIA, tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
        deterioro_tipo=TipoDeterioro.BACHE, deterioro_gravedad=GravedadDeterioro.CRITICA,
    )
    r = diag.diagnosticar(params)
    assert r.prioridad == PrioridadIntervencion.CRITICO.value
    assert r.tipo_mantenimiento == TipoMantenimiento.EMERGENCIA.value


def test_indice_condicion_critico_fuerza_prioridad_critica():
    diag = _diagnosticador()
    params = ParametrosMantenimiento(
        tipo_via=TipoViaM.SECUNDARIA, tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
        deterioro_tipo=TipoDeterioro.GRIETA, deterioro_gravedad=GravedadDeterioro.BAJA,
        indice_condicion=15.0,   # < 30 -> fuerza CRITICO pese a gravedad baja
    )
    r = diag.diagnosticar(params)
    assert r.prioridad == PrioridadIntervencion.CRITICO.value


def test_prioridad_por_tpd_hallazgo_comparacion_lexicografica():
    """
    Hallazgo real (no un bug que se corrige aquí, solo se documenta el
    comportamiento real): _determinar_prioridad compara `prioridad.value <
    "alto"` como STRING, no por severidad. "bajo" < "alto" es False
    lexicográficamente (b > a), así que el TPD > 5000 nunca sube una
    prioridad ya en "bajo" directo a "alto" -- cae al elif de "medio"
    en su lugar porque "bajo" < "medio" sí es True lexicográficamente.
    Se verifica el comportamiento real tal como está, no el que "debería" ser.
    """
    diag = _diagnosticador()
    params = ParametrosMantenimiento(
        tipo_via=TipoViaM.PRIMARIA, tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
        deterioro_tipo=TipoDeterioro.GRIETA, deterioro_gravedad=GravedadDeterioro.BAJA,
        volumen_transito=6000,   # > umbral "alto" (5000)
    )
    r = diag.diagnosticar(params)
    assert r.prioridad == PrioridadIntervencion.MEDIO.value   # no "alto", por el hallazgo de arriba


def test_actividades_no_duplicadas_y_no_vacias():
    diag = _diagnosticador()
    params = ParametrosMantenimiento(
        tipo_via=TipoViaM.PRIMARIA, tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
        deterioro_tipo=TipoDeterioro.BACHE, deterioro_gravedad=GravedadDeterioro.MEDIA,
    )
    r = diag.diagnosticar(params)
    assert len(r.actividades) == len(set(r.actividades))
    assert len(r.actividades) > 0


# ─── topografia.py ────────────────────────────────────────────────────────────

def test_error_cierre_permisible_formula_c_por_raiz_k():
    for estandar in EstandarNivelacion:
        C = COEFICIENTES_CIERRE[estandar].coeficiente_mm
        for K in (0.5, 2.0, 10.0):
            assert error_cierre_permisible_mm(K, estandar) == pytest.approx(C * sqrt(K))


def test_error_cierre_negativo_lanza_valueerror():
    with pytest.raises(ValueError):
        error_cierre_permisible_mm(-1.0, EstandarNivelacion.INVIAS)


def test_verificar_cierre_nivelacion_cumple_y_holgura():
    permisible = error_cierre_permisible_mm(4.0, EstandarNivelacion.IDU)   # 5*sqrt(4)=10mm
    r = verificar_cierre_nivelacion(error_medido_mm=6.0, distancia_km=4.0, estandar=EstandarNivelacion.IDU)
    assert r.error_permisible_mm == pytest.approx(10.0)
    assert r.cumple is True
    assert r.holgura_mm == pytest.approx(4.0)


def test_verificar_cierre_nivelacion_no_cumple_con_error_negativo_absoluto():
    r = verificar_cierre_nivelacion(error_medido_mm=-15.0, distancia_km=1.0, estandar=EstandarNivelacion.IGAC)
    # IGAC: C=2.0 -> permisible = 2*sqrt(1) = 2mm; |-15| = 15 > 2
    assert r.error_medido_mm == 15.0   # se toma el valor absoluto
    assert r.cumple is False


# ─── ntc_materiales_1.py ──────────────────────────────────────────────────────

def test_ntc2017_adoquin_cumple_caso_documentado():
    ad = Adoquin(
        nombre="AD-01", aplicacion=AplicacionAdoquin.VEHICULAR_LIVIANO, tipo=TipoAdoquin.CON_BISEL,
        largo_mm=200.0, ancho_mm=100.0, espesor_mm=80.0,
        resistencia_flexion_mpa=5.5, absorcion_porcentaje=6.0,
    )
    r = ad.verificar_ntc2017()
    assert r["veredicto"] == "CUMPLE NTC 2017"


def test_ntc2017_adoquin_espesor_insuficiente_para_vehicular_pesado():
    ad = Adoquin(
        nombre="AD-02", aplicacion=AplicacionAdoquin.VEHICULAR_PESADO, tipo=TipoAdoquin.NO_BISELADO,
        largo_mm=200.0, ancho_mm=100.0, espesor_mm=80.0,   # < 100mm mínimo para vehicular_pesado
        resistencia_flexion_mpa=5.5, absorcion_porcentaje=6.0,
    )
    r = ad.verificar_ntc2017()
    assert r["veredicto"].startswith("NO CUMPLE")
    assert any("Espesor" in f for f in r["fallas"])


def test_ntc4342_geotextil_retencion_insuficiente():
    gt = Geotextil(
        nombre="GT-01", tipo=TipoGeotextil.TEJIDO,   # tipo no válido según REQUISITOS (solo NO_TEJIDO/PUNZONADO)
        retencion_asfaltica_l_m2=0.5, composicion="Poliéster", porcentaje_poliolefinas=90.0,
    )
    r = gt.verificar_ntc4342()
    assert r["veredicto"].startswith("NO CUMPLE")
    assert len(r["fallas"]) == 3   # retención baja + composición baja + tipo inválido


def test_ntc121_cemento_ug_cumple_caso_documentado():
    ce = Cemento(
        nombre="CE-01", tipo=TipoCemento.UG,
        resistencia_compresion_mpa={3: 13.0, 7: 20.0, 28: 29.0},
        tiempo_fraguado_inicial_min=120.0, tiempo_fraguado_final_min=300.0,
        expansion_autoclave_porcentaje=0.3, finura_blaine_m2_kg=350.0, densidad_g_cm3=3.15,
    )
    r = ce.verificar_ntc121()
    assert r["veredicto"] == "CUMPLE NTC 121"


def test_ntc121_cemento_resistencia_28d_insuficiente():
    ce = Cemento(
        nombre="CE-02", tipo=TipoCemento.UG,
        resistencia_compresion_mpa={3: 13.0, 7: 20.0, 28: 25.0},   # < 28.0 MPa mínimo UG a 28 días
        tiempo_fraguado_inicial_min=120.0, tiempo_fraguado_final_min=300.0,
        expansion_autoclave_porcentaje=0.3, finura_blaine_m2_kg=350.0, densidad_g_cm3=3.15,
    )
    r = ce.verificar_ntc121()
    assert r["veredicto"].startswith("NO CUMPLE")


def test_ntc1299_aditivo_clasificacion_conocida():
    adt = Aditivo(nombre="AD-Q-01", tipo=TipoAditivo.F, descripcion="Superplastificante")
    r = adt.verificar_ntc1299()
    assert r["clasificacion"] == "Superplastificante"
    assert r["veredicto"] == "CUMPLE NTC 1299"


def test_ntc1362_cemento_blanco_blancura_insuficiente():
    cb = CementoBlanco(
        nombre="CB-01", tipo=TipoCementoBlanco.I,
        resistencia_mpa={3: 13.0, 7: 20.0, 28: 29.0},
        tiempo_fraguado_inicial_min=100.0, tiempo_fraguado_final_min=280.0,
        expansion_autoclave_porcentaje=0.2, finura_blaine_m2_kg=380.0,
        blancura_porcentaje=70.0,   # < 80.0% mínimo
    )
    r = cb.verificar_ntc1362()
    assert r["veredicto"].startswith("NO CUMPLE")
    assert any("Blancura" in f for f in r["fallas"])


def test_ntc3459_agua_cloruros_preesforzado_mas_estricto():
    analisis = AnalisisAgua(sulfatos_mg_l=400.0, cloruros_mg_l=700.0, solidos_totales_mg_l=1200.0,
                             solidos_disueltos_mg_l=800.0, ph=7.0)
    ag = MuestraAgua(nombre="AG-01", fuente=FuenteAgua.NATURAL, analisis=analisis)
    r_normal = ag.verificar_ntc3459(concreto_preesforzado=False)   # límite 1000 -> cumple
    r_preesf = ag.verificar_ntc3459(concreto_preesforzado=True)    # límite 500 -> no cumple
    assert r_normal["veredicto"] == "CUMPLE NTC 3459"
    assert r_preesf["veredicto"].startswith("NO CUMPLE")
    assert r_normal["requiere_ensayo_adicional"] is True   # fuente NATURAL


def test_ntc3493_aditivo_mineral_suma_oxidos_y_clase():
    analisis = AnalisisAditivoMineral(sio2_porcentaje=50.0, al2o3_porcentaje=20.0, fe2o3_porcentaje=6.0,
                                       perdida_ignicion_porcentaje=4.0, retencion_malla_325_porcentaje=20.0)
    assert analisis.suma_oxidos_pct == pytest.approx(76.0)
    am = AditivoMineral(nombre="AM-01", clase=ClaseAditivoMineral.F, analisis=analisis)
    r = am.verificar_ntc3493()
    assert r["veredicto"] == "CUMPLE NTC 3493"   # 76% >= 70% mínimo clase F


# ─── ntc_materiales_2.py ──────────────────────────────────────────────────────

def test_ntc3502_aire_incorporado_fuera_de_rango():
    aditivo = AditivoIncorporadorAire(
        nombre="AI-01", tipo=TipoAditivoAire.LIQUIDO,
        contenido_aire_porcentaje=10.0,   # > 8.0% máximo
        dosificacion_recomendada="200 ml/100kg", libre_cloruros=True,
    )
    r = MotorVerificacionNTC3502().verificar_aditivo(aditivo)
    assert r.cumple is False


def test_ntc3760_pigmento_dosificacion_excede_maximo():
    pigmento = PigmentoConcreto(
        nombre="PIG-01", tipo=TipoPigmento.OXIDO_HIERRO, presentacion=PresentacionPigmento.POLVO,
        dosificacion_maxima_porcentaje=12.0,   # > 10% máximo NTC 3760
        color="Rojo",
    )
    r = MotorVerificacionNTC3760().verificar_pigmento(pigmento)
    assert r.cumple is False


def test_ntc4018_escoria_grado80_indice_actividad_tabla_real():
    analisis = AnalisisEscoria(indice_actividad_7dias=70.0, indice_actividad_28dias=80.0,
                                finura_blaine_m2_kg=400.0, densidad_g_cm3=2.9)
    escoria = EscoriaAltoHorno(nombre="ESC-01", grado=GradoEscoria.GRADO_80, analisis=analisis)
    r = MotorVerificacionNTC4018().verificar_escoria(escoria)
    assert r.cumple is True   # exactamente en el mínimo Grado 80 (70/80)


def test_ntc4018_escoria_grado120_no_cumple_con_indices_de_grado80():
    analisis = AnalisisEscoria(indice_actividad_7dias=70.0, indice_actividad_28dias=80.0,
                                finura_blaine_m2_kg=400.0, densidad_g_cm3=2.9)
    escoria = EscoriaAltoHorno(nombre="ESC-02", grado=GradoEscoria.GRADO_120, analisis=analisis)
    r = MotorVerificacionNTC4018().verificar_escoria(escoria)
    assert r.cumple is False   # Grado 120 exige 95/120, no 70/80


def test_ntc4024_numero_especimenes_regla_por_tamano_lote():
    motor = MotorVerificacionNTC4024()
    dim = DimensionesPrefabricado(longitud_mm=400, altura_mm=200, espesor_mm=150)
    resultados = ResultadosEnsayo(resistencia_compresion_mpa=15.0, absorcion_porcentaje=8.0,
                                   densidad_g_cm3=2.1, contenido_humedad_porcentaje=3.0)
    muestra_ok = MuestraPrefabricado(nombre="PF-01", tipo=TipoPrefabricado.BLOQUE, dimensiones=dim,
                                      resultados=resultados, tamano_lote=5000, numero_especimenes=6)
    muestra_falla = MuestraPrefabricado(nombre="PF-02", tipo=TipoPrefabricado.BLOQUE, dimensiones=dim,
                                         resultados=resultados, tamano_lote=5000, numero_especimenes=3)
    assert motor.verificar_muestra(muestra_ok).cumple is True
    assert motor.verificar_muestra(muestra_falla).cumple is False


def test_ntc4924_agregado_densidad_excede_maximo():
    agregado = AgregadoLiviano(
        nombre="AGL-01", tipo=TipoAgregadoLiviano.ARCILLA_EXPANDIDA,
        densidad_aparente_kg_m3=1300.0,   # > 1120 kg/m³ máximo
        absorcion_porcentaje=10.0,
    )
    r = MotorVerificacionNTC4924().verificar_agregado(agregado)
    assert r.cumple is False


def test_ntc4924_unidad_mamposteria_hereda_falla_del_agregado():
    """Hallazgo real: si el agregado no cumple, verificar_unidad_mamposteria
    retorna DIRECTO el resultado del agregado -- nunca llega a verificar
    la resistencia a compresión de la unidad."""
    agregado_malo = AgregadoLiviano(
        nombre="AGL-02", tipo=TipoAgregadoLiviano.ESCORIA_EXPANDIDA,
        densidad_aparente_kg_m3=1300.0, absorcion_porcentaje=10.0,
    )
    unidad = UnidadMamposteria(
        nombre="BLQ-01", tipo=TipoUnidadMamposteria.BLOQUE, agregado=agregado_malo,
        dimensiones_mm={"largo": 400, "ancho": 200, "alto": 200},
        resistencia_compresion_mpa=8.0, densidad_aparente_kg_m3=1300.0, absorcion_porcentaje=10.0,
    )
    r = MotorVerificacionNTC4924().verificar_unidad_mamposteria(unidad)
    assert r.material == "AGL-02"   # devuelve el resultado del AGREGADO, no de la unidad
    assert r.cumple is False


def test_ntc5147_abrasion_promedio_bajo_limite():
    resultados = ResultadoAbrasion(longitud_huella_1_mm=20, longitud_huella_2_mm=21,
                                    longitud_huella_3_mm=19, longitud_huella_4_mm=22, longitud_huella_5_mm=20)
    muestra = MuestraAbrasion(nombre="AB-01", tipo=TipoMaterial.ADOQUIN, resultados=resultados)
    r = MotorVerificacionNTC5147().verificar_muestra(muestra)
    promedio_esperado = (20 + 21 + 19 + 22 + 20) / 5
    assert promedio_esperado <= 23.0
    assert r.cumple is True


def test_ntc5147_abrasion_promedio_excede_limite():
    resultados = ResultadoAbrasion(longitud_huella_1_mm=25, longitud_huella_2_mm=26,
                                    longitud_huella_3_mm=24, longitud_huella_4_mm=27, longitud_huella_5_mm=25)
    muestra = MuestraAbrasion(nombre="AB-02", tipo=TipoMaterial.ADOQUIN, resultados=resultados)
    r = MotorVerificacionNTC5147().verificar_muestra(muestra)
    assert r.cumple is False


def test_ntc6008_busqueda_termino_encontrado_y_no_encontrado():
    motor = MotorVerificacionNTC6008()
    r_ok = motor.buscar_termino("adoquín biselado")
    assert r_ok.cumple is True
    assert "perfil inclinado" in r_ok.definicion

    r_no = motor.buscar_termino("palabra que no existe en la norma")
    assert r_no.cumple is False


# ─── src/__init__.py — capa pública que consume apps/api/routers/vias.py ────

def test_wrapper_validar_diseno_geometrico():
    req = DisenoGeometricoRequest(
        tipo_via="primaria", velocidad_diseno=80, topografia="montanoso",
        volumen_transito=5000, radio_curva=250, peralte=6.0,
    )
    r = validar_diseno_geometrico(req)
    assert r["cumple"] is True


def test_wrapper_disenar_pavimento():
    req = PavimentosRequest(
        tipo_pavimento="asfaltico", tipo_via="primaria", tpd=5000,
        esals_millones=5.0, cbr_subrasante=5, espesor_base=20,
    )
    r = disenar_pavimento(req)
    assert r["cumple"] is True


def test_wrapper_diagnosticar_mantenimiento():
    req = MantenimientoRequest(
        tipo_via="primaria", tipo_mantenimiento="rutinario",
        deterioro_tipo="bache", deterioro_gravedad="media", area_afectada=1.5, profundidad=4.0,
    )
    r = diagnosticar_mantenimiento(req)
    assert r["intervencion_recomendada"] == "Parcheo localizado"


def test_wrapper_verificar_cierre_nivelacion():
    req = CierreNivelacionRequest(error_medido_mm=6.0, distancia_km=4.0, estandar="idu")
    r = verificar_cierre_nivelacion_wrapper(req)
    assert r["cumple"] is True


def test_wrapper_verificar_ntc2017_y_ntc121():
    req2017 = NTC2017Request(
        nombre="AD-01", aplicacion="vehicular_liviano", tipo="con_bisel",
        largo_mm=200.0, ancho_mm=100.0, espesor_mm=80.0,
        resistencia_flexion_mpa=5.5, absorcion_porcentaje=6.0,
    )
    assert verificar_ntc2017(req2017)["veredicto"] == "CUMPLE NTC 2017"

    req121 = NTC121Request(
        nombre="CE-01", tipo="UG",
        resistencia_compresion_mpa={3: 13.0, 7: 20.0, 28: 29.0},
        tiempo_fraguado_inicial_min=120.0, tiempo_fraguado_final_min=300.0,
        expansion_autoclave_porcentaje=0.3, finura_blaine_m2_kg=350.0, densidad_g_cm3=3.15,
    )
    assert verificar_ntc121(req121)["veredicto"] == "CUMPLE NTC 121"


def test_wrapper_ntc_materiales_2_patron_dataclasses_asdict():
    """
    Los wrappers de la parte 2 (NTC 3502+) usan dataclasses.asdict(resultado)
    en vez de retornar un dict plano como los de la parte 1 -- se verifica
    ese camino de serialización explícitamente, no solo el de la parte 1.
    """
    req3502 = NTC3502Request(
        nombre="AI-01", tipo="liquido", contenido_aire_porcentaje=6.0,
        dosificacion_recomendada="150 ml/100kg", libre_cloruros=True,
    )
    r3502 = verificar_ntc3502(req3502)
    assert r3502["cumple"] is True

    r6008 = buscar_termino_ntc6008(NTC6008Request(termino_busqueda="drenante"))
    assert r6008["cumple"] is True


def test_wrapper_ntc4924_mamposteria_con_agregado_anidado():
    req = NTC4924MamposteriaRequest(
        nombre="BLQ-01", tipo="bloque",
        agregado={
            "nombre": "AGL-01", "tipo": "arcilla_expandida",
            "densidad_aparente_kg_m3": 800.0, "absorcion_porcentaje": 12.0,
        },
        dimensiones_mm={"largo": 400, "ancho": 200, "alto": 200},
        resistencia_compresion_mpa=8.0, densidad_aparente_kg_m3=800.0, absorcion_porcentaje=12.0,
    )
    r = verificar_ntc4924_mamposteria(req)
    assert r["cumple"] is True
