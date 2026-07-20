"""Tests para Motor GeoPot — geotecnia y laboratorio (NSR-10 / INV / NTC / ACI).

Mismo patrón que motor-aquai: cada aserción recalcula el valor esperado
con la fórmula documentada en el propio módulo, no con un número supuesto.
"""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import date

from src.sismica import zona_sismica, listar_zonas, DEPARTAMENTOS, MEDIDAS
from src.lab_suelos import ClasificadorUSCS, LimitesAtterberg, EnsayoProctor, EnsayoCBR, GranulometriaAgregado
from src.lab_concreto import CilindroConcreto, EnsayoSlump, AnalisisConcreto
from src.lab_agregados import AgregadoGrueso, AgregadoFino, DisenoMezclaACI

from src import (
    ZonaSismicaRequest, ConcretoRequest, CilindroInput, SlumpInput,
    USCSRequest, AASHTORequest, ProctorRequest, CBRRequest, GranulometriaRequest,
    AgregadoGruesoRequest, AgregadoFinoRequest, MezclaACIRequest,
    consultar_zona_sismica, resumen_zonas_sismicas, analizar_concreto,
    clasificar_suelo_uscs, clasificar_suelo_aashto, analizar_proctor, analizar_cbr,
    analizar_granulometria, verificar_agregado_grueso, verificar_agregado_fino, disenar_mezcla_aci,
)


# ─── sismica.py ────────────────────────────────────────────────────────────

def test_zona_sismica_atlantico():
    r = zona_sismica("Atlántico")
    assert r["aa"] == 0.15 and r["av"] == 0.2
    assert r["clasificacion"] == "INTERMEDIA"
    assert r["medidas_nsr10"] == MEDIDAS["INTERMEDIA"]


def test_zona_sismica_busca_por_capital():
    r = zona_sismica("Barranquilla")
    assert r["dept"] == "Atlántico"


def test_zona_sismica_sin_tildes_encuentra_igual():
    """Bug real corregido en su momento: 'Atlantico' sin tilde debía encontrar el departamento."""
    r = zona_sismica("Atlantico")
    assert r["dept"] == "Atlántico"


def test_zona_sismica_no_encontrado():
    r = zona_sismica("Marte")
    assert "error" in r


def test_listar_zonas_totales_suman_todos_los_departamentos():
    resumen = listar_zonas()
    assert (resumen["totales"]["alta"] + resumen["totales"]["intermedia"]
            + resumen["totales"]["baja"]) == len(DEPARTAMENTOS)


# ─── lab_suelos.py — ClasificadorUSCS ───────────────────────────────────────

def test_uscs_arcilla_baja_plasticidad_caso_documentado():
    """Caso del propio demo del módulo (__main__): pasa_200=65, ll=42, ip=18 -> CL."""
    r = ClasificadorUSCS.clasificar(pasa_200_pct=65, pasa_4_pct=95, d10=None, d30=None, d60=None, ll=42, ip=18)
    assert r["simbolo_uscs"] == "CL"
    assert r["tipo"] == "SUELO FINO"


def test_uscs_grava_bien_gradada():
    # d10=0.1, d30=0.3, d60=0.5 -> Cu=5.0 (>=4), Cc=1.8 (entre 1 y 3) -> GW
    r = ClasificadorUSCS.clasificar(pasa_200_pct=2, pasa_4_pct=20, d10=0.1, d30=0.3, d60=0.5, ll=None, ip=None)
    assert r["cu"] == pytest.approx(5.0)
    assert r["cc"] == pytest.approx(1.8)
    assert r["simbolo_uscs"] == "GW"


def test_uscs_suelo_fino_indeterminado_sin_atterberg():
    r = ClasificadorUSCS.clasificar(pasa_200_pct=60, pasa_4_pct=90, d10=None, d30=None, d60=None, ll=None, ip=None)
    assert r["simbolo_uscs"] == "?"


def test_aashto_grupo_y_ig():
    r = ClasificadorUSCS.aashto(ll=42, ip=18, pasa_200_pct=65)
    f, ll, ip = 65, 42, 18
    ig_esperado = max(0, (f - 35) * (0.2 + 0.005 * (ll - 40)) + 0.01 * (f - 15) * (ip - 10))
    assert r["grupo_aashto"] == f"A-7 (IG={round(ig_esperado, 1)})"
    assert r["aptitud_subrasante"] == "MUY MALA"


# ─── lab_suelos.py — Atterberg / Proctor / CBR / Granulometría ─────────────

def test_atterberg_ip_y_clasificacion():
    l = LimitesAtterberg(id_muestra="M1", ll=42.0, lp=24.0)
    assert l.ip == pytest.approx(18.0)
    assert l.clasificacion_ip == "Media plasticidad"   # 15 <= 18 < 30


def test_proctor_optimo_coincide_con_ajuste_numpy_directo():
    puntos = [(8.0, 1.82), (10.0, 1.93), (12.0, 1.97), (14.0, 1.94), (16.0, 1.88)]
    proctor = EnsayoProctor(id_muestra="M-01", tipo="MODIFICADO", puntos=puntos)
    opt = proctor.optimo

    import numpy as np
    ws = [p[0] for p in puntos]; rds = [p[1] for p in puntos]
    a, b, c = np.polyfit(ws, rds, 2)
    wopt_esperado = -b / (2 * a)
    rdmax_esperado = a * wopt_esperado**2 + b * wopt_esperado + c

    assert opt["wopt_%"] == pytest.approx(round(wopt_esperado, 1))
    assert opt["rdmax_gcm3"] == pytest.approx(round(rdmax_esperado, 3))


def test_proctor_verificar_compactacion_conforme_y_no_conforme():
    proctor = EnsayoProctor(
        id_muestra="M-01", tipo="MODIFICADO",
        puntos=[(8.0, 1.82), (10.0, 1.93), (12.0, 1.97), (14.0, 1.94), (16.0, 1.88)],
    )
    rdmax = proctor.optimo["rdmax_gcm3"]
    conforme = proctor.verificar_compactacion(densidad_campo_gcm3=rdmax, porcentaje_minimo=95.0)
    no_conforme = proctor.verificar_compactacion(densidad_campo_gcm3=rdmax * 0.80, porcentaje_minimo=95.0)
    assert conforme["cumple"] is True
    assert no_conforme["cumple"] is False


def test_proctor_menos_de_3_puntos_da_error():
    proctor = EnsayoProctor(id_muestra="M-02", tipo="ESTANDAR", puntos=[(10.0, 1.9), (12.0, 1.95)])
    assert "error" in proctor.optimo


def test_cbr_formula_directa():
    cbr = EnsayoCBR(id_muestra="CBR-01", carga_254_kN=5.2, carga_508_kN=7.8, densidad_seca=1.90, humedad_pct=11.5)
    assert cbr.cbr_254 == pytest.approx(round(5.2 / 13.34 * 100, 1))
    assert cbr.cbr_508 == pytest.approx(round(7.8 / 20.01 * 100, 1))
    assert cbr.cbr_diseno == max(cbr.cbr_254, cbr.cbr_508)


def test_cbr_clasificacion_subrasante_limites():
    def cbr_con(carga_254):
        return EnsayoCBR(id_muestra="X", carga_254_kN=carga_254, carga_508_kN=0, densidad_seca=1.8, humedad_pct=10)

    assert "MUY MALA" in cbr_con(13.34 * 0.02).clasificacion_subrasante     # cbr ~2 < 3
    assert "EXCELENTE" in cbr_con(13.34 * 0.35).clasificacion_subrasante    # cbr ~35 >= 30


def test_cbr_espesor_pavimento_formula():
    cbr = EnsayoCBR(id_muestra="CBR-01", carga_254_kN=5.2, carga_508_kN=7.8, densidad_seca=1.90, humedad_pct=11.5)
    resp = cbr.espesor_pavimento_cm(esal_millones=5.0)
    cbr_val = cbr.cbr_diseno
    mr_esperado = round(10.33 * (cbr_val ** 0.65), 1)
    sn_esperado = 0.38 * (5.0 ** 0.2) * (1 / (cbr_val ** 0.2))
    assert resp["Mr_MPa"] == pytest.approx(mr_esperado)
    assert resp["SN_estimado"] == pytest.approx(round(sn_esperado, 2))


def test_granulometria_interpolacion_y_derivados():
    # Construido para que d10/d30/d60 caigan en puntos exactos de interpolación lineal
    tamices = [
        (0.075, 5), (0.15, 10), (0.3, 20), (0.6, 40), (1.18, 60),
        (2.36, 80), (4.75, 90), (9.5, 100),
    ]
    g = GranulometriaAgregado(id_muestra="G-01", tamices=tamices)
    assert g.pasa_200 == 5
    assert g.d10 is not None and g.d30 is not None and g.d60 is not None
    cu_esperado = round(g.d60 / g.d10, 2)
    assert g.cu == pytest.approx(cu_esperado)
    assert g.modulo_finura is not None   # los 7 tamices de MF están todos presentes


# ─── lab_concreto.py ─────────────────────────────────────────────────────────

def test_cilindro_resistencia_formula():
    c = CilindroConcreto(
        id_cilindro="CIL-01", edad_dias=28, diametro_mm=152.0, carga_kN=260.0,
        fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 29),
    )
    area_esperada = math.pi * (152.0 / 2) ** 2
    fc_esperado = (260.0 * 1000) / area_esperada
    assert c.area_mm2 == pytest.approx(area_esperada)
    assert c.resistencia_MPa == pytest.approx(fc_esperado)
    assert c.resistencia_kgcm2 == pytest.approx(fc_esperado * 10.197)


def test_slump_clasificacion_y_alertas():
    s_media = EnsayoSlump(id_muestra="S-1", slump_mm=95, temperatura_C=28, hora_toma="08:30")
    assert s_media.clasificacion == "S3 — Plástica media"
    assert s_media.resumen()["alerta"] == "OK"

    s_excesivo = EnsayoSlump(id_muestra="S-2", slump_mm=210, temperatura_C=35, hora_toma="09:00")
    r = s_excesivo.resumen()
    assert "Slump excesivo" in r["alerta"]
    assert "Temperatura alta" in r["alerta"]


def test_analisis_concreto_conformidad_cilindros_sobre_diseno():
    """
    Nota: los valores del demo original del módulo (__main__, cargas 260/268/255 kN
    sobre cilindros de 152mm) en realidad dan fc ≈ 14-15 MPa, MUY por debajo de
    fc_diseno=21 MPa -- ese demo no ilustra un caso conforme pese a la carga alta
    en kN (el área de 152mm es grande, ~18146 mm²). Se usan cargas reales más altas
    aquí para construir un caso efectivamente conforme, verificado por cálculo.
    """
    analisis = AnalisisConcreto(fc_diseno_MPa=21.0, zona_sismica="ALTA", proyecto="Test", elemento="Columna")
    for id_, carga in [("CIL-04", 455.0), ("CIL-05", 460.0), ("CIL-06", 450.0)]:
        analisis.agregar_cilindro(CilindroConcreto(
            id_cilindro=id_, edad_dias=28, diametro_mm=152, carga_kN=carga,
            fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 29),
        ))
    # Todas las resistencias individuales quedan bien por encima de fc_diseno=21 MPa
    assert all(c.resistencia_MPa > 21.0 for c in analisis.cilindros)

    conformidad = analisis.verificar_conformidad()
    assert conformidad["criterio_1_ok"] is True
    assert conformidad["criterio_2_ok"] is True
    assert "CONFORME" in conformidad["veredicto"]


def test_analisis_concreto_no_conforme_por_cilindro_bajo():
    analisis = AnalisisConcreto(fc_diseno_MPa=21.0, zona_sismica="ALTA")
    # Cilindro con carga muy baja -> resistencia << fc_diseno - 3.5
    for id_, d, carga in [("A", 152, 260.0), ("B", 152, 50.0)]:
        analisis.agregar_cilindro(CilindroConcreto(
            id_cilindro=id_, edad_dias=28, diametro_mm=d, carga_kN=carga,
            fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 29),
        ))
    conformidad = analisis.verificar_conformidad()
    assert conformidad["criterio_2_ok"] is False
    assert "NO CONFORME" in conformidad["veredicto"]


def test_analisis_concreto_proyeccion_28d_desde_7d():
    analisis = AnalisisConcreto(fc_diseno_MPa=21.0, zona_sismica="ALTA")
    analisis.agregar_cilindro(CilindroConcreto(
        id_cilindro="C7", edad_dias=7, diametro_mm=152, carga_kN=185.0,
        fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 8),
    ))
    fc7 = analisis.cilindros[0].resistencia_MPa
    proyeccion = analisis.proyectar_28_dias(7)
    assert proyeccion == pytest.approx(round(fc7 / 0.65, 2))   # FACTORES_MADUREZ[7] = 0.65


# ─── lab_agregados.py ────────────────────────────────────────────────────────

def test_agregado_grueso_densidad_y_absorcion():
    ag = AgregadoGrueso(
        id_muestra="AG-01", origen="Triturado",
        masa_sss_g=2000.0, masa_seca_g=1958.0, masa_sumergida_g=1222.0, perdida_LA_pct=28.5,
    )
    vol = 2000.0 - 1222.0
    assert ag.densidad_sss == pytest.approx(round(2000.0 / vol, 3))
    assert ag.densidad_aparente == pytest.approx(round(1958.0 / vol, 3))
    assert ag.absorcion_pct == pytest.approx(round((2000.0 - 1958.0) / 1958.0 * 100, 2))


def test_agregado_grueso_verificar_ntc174_cumple_caso_documentado():
    ag = AgregadoGrueso(
        id_muestra="AG-01", origen="Triturado",
        masa_sss_g=2000.0, masa_seca_g=1958.0, masa_sumergida_g=1222.0, perdida_LA_pct=28.5,
    )
    r = ag.verificar_ntc174("CONCRETO")
    assert r["veredicto"] == "CUMPLE NTC 174"
    assert r["fallas"] == []


def test_agregado_grueso_falla_por_absorcion_alta():
    ag = AgregadoGrueso(
        id_muestra="AG-02", origen="Rodado",
        masa_sss_g=2100.0, masa_seca_g=1900.0, masa_sumergida_g=1222.0, perdida_LA_pct=20.0,
    )
    r = ag.verificar_ntc174("CONCRETO")   # absorción ~10.5% > 3.0% máx
    assert r["veredicto"].startswith("NO CUMPLE")
    assert any("Absorción" in f for f in r["fallas"])


def test_agregado_fino_densidad_y_clasificacion_mf():
    af = AgregadoFino(
        id_muestra="AF-01", masa_sss_g=500.0, masa_seca_g=487.0,
        masa_frasco_agua=670.0, masa_frasco_agua_muestra=984.0,
        modulo_finura=2.75, impurezas_organicas="CLARO",
    )
    vol = 500.0 - (984.0 - 670.0)
    assert af.densidad_sss == pytest.approx(round(500.0 / vol, 3))
    assert af.clasificacion_mf() == "Arena MEDIA"   # 2.6 <= 2.75 < 2.9


def test_agregado_fino_falla_por_impurezas_oscuras():
    af = AgregadoFino(
        id_muestra="AF-02", masa_sss_g=500.0, masa_seca_g=487.0,
        masa_frasco_agua=670.0, masa_frasco_agua_muestra=984.0,
        modulo_finura=2.75, impurezas_organicas="OSCURO",
    )
    r = af.verificar_ntc174()
    assert r["veredicto"].startswith("NO CUMPLE")
    assert any("OSCURO" in f for f in r["fallas"])


def test_diseno_mezcla_relacion_ac_interpolada():
    d = DisenoMezclaACI(fc_MPa=21.0, tamaño_max_agregado_mm=19.0, asentamiento_mm=75.0, zona_sismica="ALTA")
    # fc=21.0 cae exactamente en la tabla ACI -> a/c = 0.74
    assert d._relacion_ac() == pytest.approx(0.74)


def test_diseno_mezcla_fc_bajo_minimo_nsr10_se_ajusta():
    d = DisenoMezclaACI(fc_MPa=15.0, zona_sismica="ALTA")   # < 21 MPa mínimo NSR-10 zona ALTA
    resultado = d.calcular()
    assert resultado["fc_diseno_MPa"] == 21.0
    assert "aumentado" in resultado["nota_nsr10"]


def test_diseno_mezcla_relacion_masa_coherente_con_proporciones():
    d = DisenoMezclaACI(fc_MPa=28.0, tamaño_max_agregado_mm=19.0, asentamiento_mm=75.0, zona_sismica="ALTA")
    r = d.calcular()
    prop = r["proporciones_por_m3"]
    rel = r["relacion_masa"]
    assert rel["agua"] == pytest.approx(round(prop["agua_kg"] / prop["cemento_kg"], 2))
    assert rel["grueso"] == pytest.approx(round(prop["agregado_grueso_kg"] / prop["cemento_kg"], 2))


# ─── src/__init__.py — capa pública que consume apps/api/routers/geopot.py ──
# No reverifica fórmulas (ya cubiertas arriba): solo confirma que cada wrapper
# recibe el Request Pydantic real y delega correctamente sin romperse.

def test_wrapper_consultar_zona_sismica():
    r = consultar_zona_sismica(ZonaSismicaRequest(departamento="Atlántico"))
    assert r["clasificacion"] == "INTERMEDIA"


def test_wrapper_resumen_zonas_sismicas():
    r = resumen_zonas_sismicas()
    assert "totales" in r


def test_wrapper_analizar_concreto_con_cilindros_y_slumps():
    req = ConcretoRequest(
        fc_diseno_MPa=21.0, zona_sismica="ALTA", proyecto="P1", elemento="E1",
        cilindros=[CilindroInput(
            id_cilindro="C1", edad_dias=28, diametro_mm=152, carga_kN=455.0,
            fecha_colada="2026-06-01", fecha_ensayo="2026-06-29",
        )],
        slumps=[SlumpInput(id_muestra="S1", slump_mm=95, temperatura_C=28, hora_toma="08:30")],
    )
    r = analizar_concreto(req)
    assert r["conformidad"]["fc_diseno_MPa"] == 21.0
    assert len(r["cilindros"]) == 1
    assert len(r["slumps"]) == 1


def test_wrapper_clasificar_suelo_uscs_y_aashto():
    req_u = USCSRequest(pasa_200_pct=65, pasa_4_pct=95, ll=42, ip=18)
    assert clasificar_suelo_uscs(req_u)["simbolo_uscs"] == "CL"

    req_a = AASHTORequest(ll=42, ip=18, pasa_200_pct=65)
    assert clasificar_suelo_aashto(req_a)["aptitud_subrasante"] == "MUY MALA"


def test_wrapper_analizar_proctor_con_verificacion_campo():
    req = ProctorRequest(
        id_muestra="M-01", tipo="MODIFICADO",
        puntos=[(8.0, 1.82), (10.0, 1.93), (12.0, 1.97), (14.0, 1.94), (16.0, 1.88)],
        densidad_campo_gcm3=1.95, porcentaje_minimo=95.0,
    )
    r = analizar_proctor(req)
    assert "verificacion_campo" in r
    assert "cumple" in r["verificacion_campo"]


def test_wrapper_analizar_cbr_con_pavimento():
    req = CBRRequest(
        id_muestra="CBR-01", carga_254_kN=5.2, carga_508_kN=7.8,
        densidad_seca=1.90, humedad_pct=11.5, esal_millones=5.0,
    )
    r = analizar_cbr(req)
    assert "pavimento" in r


def test_wrapper_analizar_granulometria():
    req = GranulometriaRequest(id_muestra="G-01", tamices=[(0.075, 5), (2.36, 80), (9.5, 100)])
    r = analizar_granulometria(req)
    assert r["id"] == "G-01"


def test_wrapper_verificar_agregados():
    req_g = AgregadoGruesoRequest(
        id_muestra="AG-01", masa_sss_g=2000.0, masa_seca_g=1958.0, masa_sumergida_g=1222.0,
    )
    assert verificar_agregado_grueso(req_g)["veredicto"] == "CUMPLE NTC 174"

    req_f = AgregadoFinoRequest(
        id_muestra="AF-01", masa_sss_g=500.0, masa_seca_g=487.0,
        masa_frasco_agua=670.0, masa_frasco_agua_muestra=984.0, modulo_finura=2.75,
    )
    r_f = verificar_agregado_fino(req_f)
    assert "clasificacion_mf" in r_f


def test_wrapper_disenar_mezcla_aci():
    req = MezclaACIRequest(fc_MPa=21.0, zona_sismica="ALTA")
    r = disenar_mezcla_aci(req)
    assert r["fc_diseno_MPa"] == 21.0
