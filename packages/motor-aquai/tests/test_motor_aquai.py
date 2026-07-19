"""Tests para Motor AquAI — RAS 2000 / Resolución 0330-2017.

Cada aserción recalcula el valor esperado a partir de la fórmula
documentada en el módulo (o de las tablas normativas en ras2000_tablas.py),
no de un número supuesto — así una regresión real en la fórmula rompe
el test, no solo un cambio cosmético.
"""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from pydantic import ValidationError

from src.schemas import (
    PoblacionRequest, MetodoPoblacion, NivelComplejidad, ClimaRegion,
    CaudalesRequest, HazenWilliamsRequest, HidrologiaRequest, MetodoConcentracion,
)
from src.schemas_hidraulica_avanzada import (
    ManningRequest, ArieteRequest, BombeoRequest, MaterialTuberia, TipoFluidoBombeo,
)
from src.schemas_saneamiento import (
    PTAPRequest, CoagulanteType, PTARRequest, TecnologiaPTAR, TipoCuerpoReceptor,
)
from src.schemas_tarifario import (
    TarifaRequest, TipoPrestador, ReporteSUIRequest, ServicioTarifario,
)

from src.poblacion import proyectar_poblacion
from src.caudales import calcular_caudales
from src.hidraulica import calcular_hazen_williams, _velocidad, _hazen_perdida_total
from src.hidrologia import calcular_hidrologia, _tc_kirpich
from src.manning import calcular_manning, _hidraulica_seccion_llena
from src.ariete import calcular_ariete, presion_vapor_pa, presion_atmosferica_pa
from src.bombeo import calcular_bombeo
from src.ptap import calcular_ptap
from src.ptar import calcular_ptar
from src.tarifario import calcular_tarifa
from src.sui_reporte import calcular_indicadores, generar_reporte_sui, categoria_irca, cumple_irca

from src.ras2000_tablas import (
    DOTACION_RAS, FACTORES_CONSUMO, CAUDAL_INCENDIO, PERIODO_DISENO,
    TASA_CRECIMIENTO_DEFAULT, CURVAS_IDF,
)


# ─── poblacion.py ──────────────────────────────────────────────────────────

def test_poblacion_aritmetico():
    req = PoblacionRequest(
        poblacion_censal=10_000, anio_censo=2010, anio_diseno=2020,
        tasa_crecimiento=0.03, nivel_complejidad=NivelComplejidad.MEDIO,
        metodo=MetodoPoblacion.ARITMETICO,
    )
    resp = proyectar_poblacion(req)
    esperado = 10_000 + 0.03 * 10_000 * 10
    assert resp.poblacion_diseno == round(esperado)


def test_poblacion_geometrico():
    req = PoblacionRequest(
        poblacion_censal=10_000, anio_censo=2010, anio_diseno=2020,
        tasa_crecimiento=0.03, nivel_complejidad=NivelComplejidad.MEDIO,
        metodo=MetodoPoblacion.GEOMETRICO,
    )
    resp = proyectar_poblacion(req)
    esperado = 10_000 * (1.03) ** 10
    assert resp.poblacion_diseno == round(esperado)


def test_poblacion_exponencial():
    req = PoblacionRequest(
        poblacion_censal=10_000, anio_censo=2010, anio_diseno=2020,
        tasa_crecimiento=0.03, nivel_complejidad=NivelComplejidad.MEDIO,
        metodo=MetodoPoblacion.EXPONENCIAL,
    )
    resp = proyectar_poblacion(req)
    esperado = 10_000 * math.exp(0.03 * 10)
    assert resp.poblacion_diseno == round(esperado)


def test_poblacion_tasa_y_periodo_por_defecto():
    req = PoblacionRequest(
        poblacion_censal=5_000, anio_censo=2015, anio_diseno=2030,
        nivel_complejidad=NivelComplejidad.BAJO,   # sin tasa_crecimiento explícita
    )
    resp = proyectar_poblacion(req)
    assert resp.tasa_usada == TASA_CRECIMIENTO_DEFAULT["bajo"]
    assert resp.periodo_diseno == PERIODO_DISENO["bajo"]


def test_poblacion_anio_diseno_debe_ser_mayor():
    with pytest.raises(ValidationError):
        PoblacionRequest(
            poblacion_censal=1_000, anio_censo=2020, anio_diseno=2015,
            nivel_complejidad=NivelComplejidad.BAJO,
        )


# ─── caudales.py ───────────────────────────────────────────────────────────

def test_caudales_tabla_ras_dotacion_recomendada():
    req = CaudalesRequest(
        poblacion_diseno=10_000,
        nivel_complejidad=NivelComplejidad.MEDIO,
        clima=ClimaRegion.CALIDO,
    )
    resp = calcular_caudales(req)
    _min, _max, rec = DOTACION_RAS["medio"]["calido"]
    assert resp.dotacion_lhd == rec

    dot_bruta = rec / (1 - 0.25)   # perdidas_pct default = 25.0
    Qp = (dot_bruta * 10_000) / 86_400
    fmd, fmh = FACTORES_CONSUMO["medio"]["fmd"], FACTORES_CONSUMO["medio"]["fmh"]
    assert resp.Qp_ls == pytest.approx(Qp, rel=1e-4)
    assert resp.Qmd_ls == pytest.approx(Qp * fmd, rel=1e-4)
    assert resp.Qmh_ls == pytest.approx(Qp * fmd * fmh, rel=1e-4)
    assert resp.Qci_ls == CAUDAL_INCENDIO["medio"]


def test_caudales_dotacion_manual_omite_tabla():
    req = CaudalesRequest(
        poblacion_diseno=1_000, nivel_complejidad=NivelComplejidad.BAJO,
        clima=ClimaRegion.FRIO, dotacion_manual=100.0, perdidas_pct=20.0,
    )
    resp = calcular_caudales(req)
    assert resp.dotacion_lhd == 100.0
    assert resp.dotacion_bruta_lhd == pytest.approx(100.0 / 0.8, rel=1e-6)


# ─── hidraulica.py — Hazen-Williams ─────────────────────────────────────────

def test_hazen_williams_helpers_formula_directa():
    Q_m3s, D_m, L_m, C = 0.02, 0.16, 500.0, 150
    v = _velocidad(Q_m3s, D_m)
    assert v == pytest.approx(Q_m3s / (math.pi * (D_m / 2) ** 2))

    hf = _hazen_perdida_total(Q_m3s, C, D_m, L_m)
    assert hf == pytest.approx(10.67 * L_m * Q_m3s ** 1.852 / (C ** 1.852 * D_m ** 4.87))


def test_hazen_williams_material_desconocido_advierte_y_usa_c130():
    req = HazenWilliamsRequest(caudal_ls=15, longitud_m=300, diametro_mm=160, material="TITANIO")
    resp = calcular_hazen_williams(req)
    assert resp.coeficiente_C == 130
    assert any("no reconocido" in a for a in resp.advertencias)


def test_hazen_williams_autoseleccion_cumple_velocidad():
    req = HazenWilliamsRequest(caudal_ls=10, longitud_m=200, cota_inicio_m=50.0, material="PVC")
    resp = calcular_hazen_williams(req)
    assert resp.cumple_velocidad is True
    assert 0.45 <= resp.velocidad_ms <= 5.00


# ─── hidrologia.py ───────────────────────────────────────────────────────────

def test_hidrologia_tc_kirpich_formula():
    L_m, S = 800.0, 0.02
    assert _tc_kirpich(L_m, S) == pytest.approx(0.0195 * (L_m ** 0.77) / (S ** 0.385))


def test_hidrologia_curva_idf_caribe_tr25_valores_de_tabla():
    req = HidrologiaRequest(
        area_cuenca_ha=50, longitud_cauce_m=800, pendiente_media=0.02,
        periodo_retorno=25, coeficiente_escorrentia=0.6, region_idf="caribe",
        metodo_tc=MetodoConcentracion.KIRPICH,
    )
    resp = calcular_hidrologia(req)
    coef = CURVAS_IDF["caribe"][25]
    assert resp.parametros_idf["a"] == coef["a"]
    assert resp.parametros_idf["b"] == coef["b"]
    assert resp.parametros_idf["n"] == coef["n"]

    # Autoconsistencia: Q = C·I·A/360
    Q_m3s_esperado = 0.6 * resp.intensidad_mm_h * 50 / 360.0
    assert resp.caudal_diseno_m3s == pytest.approx(Q_m3s_esperado, rel=1e-3)


def test_hidrologia_region_no_reconocida():
    req = HidrologiaRequest(
        area_cuenca_ha=50, longitud_cauce_m=800, pendiente_media=0.02,
        coeficiente_escorrentia=0.5, region_idf="marte",
    )
    with pytest.raises(ValueError):
        calcular_hidrologia(req)


def test_hidrologia_cuenca_grande_advierte():
    req = HidrologiaRequest(
        area_cuenca_ha=1_500, longitud_cauce_m=5_000, pendiente_media=0.01,
        coeficiente_escorrentia=0.5, region_idf="andina_norte",
    )
    resp = calcular_hidrologia(req)
    assert "⚠" in resp.notas_region


# ─── manning.py ──────────────────────────────────────────────────────────────

def test_manning_seccion_llena_formula_directa():
    D_int_m, S, n = 0.20, 0.01, 0.010
    Qf, Vf = _hidraulica_seccion_llena(D_int_m, S, n)
    R = D_int_m / 4.0
    Vf_esperado = (1.0 / n) * R ** (2 / 3) * S ** 0.5
    A = math.pi * D_int_m ** 2 / 4.0
    assert Vf == pytest.approx(Vf_esperado)
    assert Qf == pytest.approx(Vf_esperado * A)


def test_manning_seleccion_diametro_cumple_restricciones():
    req = ManningRequest(caudal_diseno_ls=15, pendiente_m_m=0.01, material=MaterialTuberia.PVC)
    resp = calcular_manning(req)
    # El motor elige el primer diámetro comercial que cumple Q/Qf y tirante —
    # no filtra por el mínimo de 200mm recomendado (RAS D.3.3), solo advierte.
    assert resp.diametro_nominal_mm in [150, 200, 250, 300, 350, 400, 450, 500,
                                         600, 700, 800, 900, 1000, 1100, 1200, 1400, 1600, 1800, 2000]
    if resp.diametro_nominal_mm < 200:
        assert any("200 mm" in a for a in resp.advertencias)
    if resp.cumple_tirante:
        assert resp.relacion_tirante_d_D <= req.relacion_tirante_max


def test_manning_diametro_insuficiente_usa_el_mayor_y_advierte():
    req = ManningRequest(
        caudal_diseno_ls=500, pendiente_m_m=0.001,
        material=MaterialTuberia.PVC, diametro_nominal_mm=150,
    )
    resp = calcular_manning(req)
    assert resp.diametro_nominal_mm == 2000   # DIAMETROS_SANEAMIENTO_MM[-1] — fallback real
    assert any("supera la capacidad" in a for a in resp.advertencias)


# ─── ariete.py — Golpe de ariete ─────────────────────────────────────────────

def test_presion_atmosferica_nivel_del_mar():
    assert presion_atmosferica_pa(0.0) == pytest.approx(101_325.0)


def test_presion_vapor_crece_con_temperatura():
    assert presion_vapor_pa(40.0) > presion_vapor_pa(20.0)


def test_ariete_cierre_rapido_vs_lento():
    base = dict(
        caudal_ls=30, diametro_interno_mm=150, longitud_m=1000,
        material=MaterialTuberia.PVC, espesor_pared_mm=5, presion_estatica_m=40,
    )
    resp_rapido = calcular_ariete(ArieteRequest(**base, velocidad_cierre_s=0.5))
    resp_lento  = calcular_ariete(ArieteRequest(**base, velocidad_cierre_s=60.0))

    assert resp_rapido.cierre_rapido is True
    assert resp_lento.cierre_rapido is False
    # Autoconsistencia Joukowski: H_max = H_estatica + sobrepresion
    assert resp_rapido.presion_maxima_total_m == pytest.approx(
        40 + resp_rapido.sobrepresion_maxima_m, abs=0.05
    )


def test_ariete_riesgo_cavitacion_con_presion_estatica_baja():
    req = ArieteRequest(
        caudal_ls=50, diametro_interno_mm=100, longitud_m=2000,
        velocidad_cierre_s=0.2, material=MaterialTuberia.ACERO,
        espesor_pared_mm=4, presion_estatica_m=5,
    )
    resp = calcular_ariete(req)
    assert resp.presion_minima_m < 5   # H_min = H_estatica - ΔH, siempre por debajo
    if resp.presion_minima_m < -10.0:
        assert resp.riesgo_cavitacion is True


# ─── bombeo.py ────────────────────────────────────────────────────────────────

def test_bombeo_tdh_es_geometrica_mas_perdidas():
    req = BombeoRequest(
        caudal_diseno_ls=20, altura_geometrica_m=30,
        longitud_descarga_m=500, diametro_succion_mm=150, diametro_descarga_mm=100,
    )
    resp = calcular_bombeo(req)
    assert resp.tdh_m == pytest.approx(
        30 + resp.perdidas_friccion_succion_m + resp.perdidas_friccion_descarga_m + resp.perdidas_menores_m,
        abs=0.01,
    )
    assert resp.n_bombas_reserva == 1   # RAS B.8.4: siempre 1 de reserva


def test_bombeo_altitud_alta_reduce_npsh_y_advierte():
    base = dict(
        caudal_diseno_ls=20, altura_geometrica_m=15,
        longitud_descarga_m=300, diametro_succion_mm=150, diametro_descarga_mm=100,
    )
    resp_bajo = calcular_bombeo(BombeoRequest(**base, altitud_msnm=0))
    resp_alto = calcular_bombeo(BombeoRequest(**base, altitud_msnm=3000))
    assert resp_alto.npsh_disponible_m < resp_bajo.npsh_disponible_m
    assert any("Altitud" in a for a in resp_alto.advertencias)


# ─── ptap.py ──────────────────────────────────────────────────────────────────

def test_ptap_dosis_coagulante_tabla_alumbre():
    req = PTAPRequest(caudal_diseno_ls=50, turbidez_cruda_ntu=30, coagulante=CoagulanteType.ALUMBRE)
    resp = calcular_ptap(req)
    assert resp.dosis_coagulante_mg_l == 28.0   # tabla DOSIS_ALUMBRE, tramo (10,50], factor alumbre=1.0
    assert len(resp.unidades) == 5              # coagulación, floculación, sedimentación, filtración, desinfección
    assert resp.cumple_res2115 is True


def test_ptap_ph_fuera_de_rango_advierte():
    req = PTAPRequest(caudal_diseno_ls=50, turbidez_cruda_ntu=30, ph_crudo=5.0)
    resp = calcular_ptap(req)
    assert any("pH crudo" in a for a in resp.advertencias)


# ─── ptar.py ──────────────────────────────────────────────────────────────────

def test_ptar_caudal_es_acueducto_por_factor_retorno():
    req = PTARRequest(
        poblacion_diseno=5_000, caudal_acueducto_ls=50, factor_retorno=0.8,
        dbo5_cruda_mg_l=250, tecnologia=TecnologiaPTAR.UASB,
        tipo_cuerpo_receptor=TipoCuerpoReceptor.RIO,
    )
    resp = calcular_ptar(req)
    assert resp.caudal_ar_ls == pytest.approx(50 * 0.8)
    # UASB: eficiencia DBO fija en 70% -> efluente = cruda * 0.30
    assert resp.dbo_efluente_mg_l == pytest.approx(250 * 0.30, rel=1e-6)
    assert resp.limite_res0631_dbo == 90.0   # LIMITES_RES0631["rio"]["DBO5"]


def test_ptar_estima_dbo_per_capita_si_no_se_provee():
    req = PTARRequest(
        poblacion_diseno=5_000, caudal_acueducto_ls=50, factor_retorno=0.8,
        tecnologia=TecnologiaPTAR.UASB,
    )
    resp = calcular_ptar(req)
    assert resp.dbo5_cruda_mg_l > 0
    assert any("DBO₅ estimada per cápita" in a for a in resp.advertencias)


# ─── tarifario.py ─────────────────────────────────────────────────────────────

def test_tarifa_cmlp_formula():
    req = TarifaRequest(
        tipo_prestador=TipoPrestador.GRANDE, clima="calido",
        costo_medio_inversion_cmi=1000, costo_medio_operacion_cmo=800,
        costo_medio_administracion_cma=15000, consumo_medio_facturado_m3=15,
        factor_perdidas=0.25,
    )
    resp = calcular_tarifa(req)
    factor = 1 / (1 - 0.25)
    cmlp_esperado = 1000 * factor + 800 * factor + (15000 / 15)
    assert resp.cmlp_m3 == pytest.approx(cmlp_esperado, rel=1e-4)
    assert resp.tarifa_base.consumo_basico_limite_m3 == 16.0   # CONSUMO_BASICO["calido"]
    assert len(resp.tarifas_por_estrato) == 9                  # 9 entradas en FACTORES_ESTRATO


def test_tarifa_estrato1_subsidiado_y_estrato4_contribuye():
    req = TarifaRequest(
        tipo_prestador=TipoPrestador.PEQUENO, clima="templado",
        costo_medio_inversion_cmi=500, costo_medio_operacion_cmo=400,
        costo_medio_administracion_cma=10000,
    )
    resp = calcular_tarifa(req)
    por_estrato = {t.estrato: t for t in resp.tarifas_por_estrato}
    assert por_estrato["1"].tipo == "subsidio"
    assert por_estrato["1"].cargo_consumo_basico_aplicado < resp.tarifa_base.cargo_consumo_basico_m3
    assert por_estrato["4"].tipo == "contribucion"
    assert por_estrato["4"].cargo_consumo_basico_aplicado > resp.tarifa_base.cargo_consumo_basico_m3


def test_tarifa_clima_invalido():
    req = TarifaRequest(
        tipo_prestador=TipoPrestador.GRANDE, clima="tropical_invalido",
        costo_medio_inversion_cmi=500, costo_medio_operacion_cmo=400,
        costo_medio_administracion_cma=10000,
    )
    with pytest.raises(ValueError):
        calcular_tarifa(req)


# ─── sui_reporte.py ────────────────────────────────────────────────────────────

def test_categoria_irca_limites():
    assert categoria_irca(0) == "Sin riesgo"
    assert categoria_irca(5) == "Sin riesgo"
    assert categoria_irca(14) == "Riesgo bajo"
    assert categoria_irca(35) == "Riesgo medio"
    assert categoria_irca(80) == "Riesgo alto"
    assert categoria_irca(81) == "Inviable para consumo humano"


def test_cumple_irca_solo_sin_riesgo():
    assert cumple_irca(5.0) is True
    assert cumple_irca(5.01) is False


def _sui_request(**overrides):
    base = dict(
        municipio="Barranquilla", departamento="Atlántico", nit_prestador="900123456",
        periodo="2026-06", servicio=ServicioTarifario.ACUEDUCTO,
        suscriptores_totales=1_000, suscriptores_por_estrato={"1": 400, "2": 400, "3": 200},
        volumen_producido_m3=50_000, volumen_facturado_m3=40_000,
        recaudo_total_cop=80_000_000,
        tarifa_cargo_fijo_estrato3=15_000, tarifa_cargo_consumo_basico_estrato3=3_000,
    )
    base.update(overrides)
    return ReporteSUIRequest(**base)


def test_sui_ianc_formula():
    req = _sui_request()
    resp = generar_reporte_sui(req)
    ianc_esperado = (50_000 - 40_000) / 50_000 * 100
    assert resp.ianc_pct == pytest.approx(ianc_esperado)
    assert resp.ianc_pct <= 25   # no debería disparar la alerta de IANC


def test_sui_ianc_alto_genera_alerta():
    req = _sui_request(volumen_producido_m3=100_000, volumen_facturado_m3=60_000)  # IANC=40%
    resp = generar_reporte_sui(req)
    assert resp.ianc_pct == pytest.approx(40.0)
    assert any("IANC" in a for a in resp.alertas_regulatorias)


def test_sui_irca_alto_genera_alerta_de_reporte():
    req = _sui_request(irca_promedio=45.0)
    resp = generar_reporte_sui(req)
    assert resp.irca_categoria == "Riesgo alto"
    assert any("IRCA" in a for a in resp.alertas_regulatorias)
