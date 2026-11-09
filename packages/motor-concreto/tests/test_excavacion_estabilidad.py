"""Estabilidad de taludes de excavación (Fase 1a). Los valores esperados vienen de cierres teóricos independientes del código:
- talud infinito sin cohesión: FS -> tan(phi)/tan(beta) (límite al que tiende Bishop cuando la superficie crítica es superficial);
- corte vertical en suelo puramente cohesivo (phi=0, sin grieta): para un círculo, Bishop es el equilibrio de momentos exacto; se contrastó con un cálculo independiente por intersección de polígonos (disco ∩ suelo, momento del peso respecto al centro): Ns = gamma*Hc/c = 4,25 en ambos. La altura planar 4c/gamma (Ns 4,0) NO es cota de un mecanismo circular;
- altura crítica de Rankine, 4c/(gamma*sqrt(Ka)): fórmula cerrada;
- Tabla H.2.4-1 de la NSR-10, transcrita del PDF fuente."""
import math

import pytest

from src.excavacion_estabilidad import (SueloExc, altura_critica_bishop, altura_critica_vertical_rankine, angulo_maximo_seguro, factor_seguridad_requerido,
                                        factor_seguridad_talud, perfil_talud)


def test_tabla_h24_valores_transcritos():
    assert factor_seguridad_requerido("diseno", sismo=False, analisis="efectivo") == 1.50
    assert factor_seguridad_requerido("construccion", sismo=False, analisis="efectivo") == 1.25
    assert factor_seguridad_requerido("diseno", sismo=True, analisis="efectivo") == 1.05
    assert factor_seguridad_requerido("construccion", sismo=True, analisis="efectivo") == 1.00
    assert factor_seguridad_requerido("diseno", sismo=False, analisis="no_drenado") == 1.80
    assert factor_seguridad_requerido("construccion", sismo=False, analisis="no_drenado") == 1.40


def test_no_drenado_con_sismo_no_se_permite():
    with pytest.raises(ValueError, match="no se permite"):
        factor_seguridad_requerido("construccion", sismo=True, analisis="no_drenado")


def test_altura_critica_rankine_cerrada():
    # c=20 kPa, gamma=18: phi=0 -> 4c/gamma = 4.444 m; phi=30 -> x tan(60) = 7.698 m
    assert altura_critica_vertical_rankine(SueloExc(gamma=18.0, c_kpa=20.0, phi_deg=0.0)) == pytest.approx(4 * 20 / 18, rel=1e-12)
    assert altura_critica_vertical_rankine(SueloExc(gamma=18.0, c_kpa=20.0, phi_deg=30.0)) == pytest.approx(4 * 20 / 18 * math.tan(math.radians(60.0)), rel=1e-12)


def test_talud_infinito_sin_cohesion_es_cota_inferior_de_bishop():
    suelo = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=35.0)
    fs = factor_seguridad_talud(perfil_talud(altura=5.0, angulo_deg=25.0), suelo).fs
    limite = math.tan(math.radians(35.0)) / math.tan(math.radians(25.0))        # 1.5016
    assert fs >= limite * 0.995          # no puede bajar del talud infinito (salvo tolerancia numérica)
    assert fs <= limite * 1.06           # y la búsqueda debe encontrar superficies casi superficiales


def test_corte_vertical_cohesivo_coincide_con_calculo_independiente_de_momentos():
    suelo = SueloExc(gamma=18.0, c_kpa=30.0, phi_deg=0.0)
    h_b = altura_critica_bishop(suelo, angulo_deg=90.0, grieta_traccion=False)
    ns = suelo.gamma * h_b / suelo.c_kpa
    assert 4.15 <= ns <= 4.35            # 4,25 con intersección de polígonos (shapely) y búsqueda en malla + Nelder-Mead
    # el mecanismo planar (Culmann, Ns=4,0) es más crítico que el mejor círculo: el módulo lo reporta aparte con la altura de Rankine
    assert altura_critica_vertical_rankine(suelo) < h_b


def test_la_grieta_de_traccion_baja_el_fs_del_corte_vertical_cohesivo():
    # phi=0, corte vertical: la grieta seca (z0 = 2c/gamma = 3,33 m) recorta la masa y reduce la altura crítica; se reporta la profundidad de grieta usada
    suelo = SueloExc(gamma=18.0, c_kpa=30.0, phi_deg=0.0)
    p = perfil_talud(altura=6.4, angulo_deg=90.0)
    con = factor_seguridad_talud(p, suelo, grieta_traccion=True)
    sin = factor_seguridad_talud(p, suelo, grieta_traccion=False)
    assert con.profundidad_grieta_m == pytest.approx(2 * 30.0 / 18.0, rel=1e-9)
    assert con.fs < sin.fs


@pytest.mark.parametrize("variante", ["altura", "agua", "sobrecarga", "sismo"])
def test_monotonia_empeora_con_cada_accion(variante):
    suelo = SueloExc(gamma=18.0, c_kpa=15.0, phi_deg=28.0, gamma_sat=19.5)
    base = factor_seguridad_talud(perfil_talud(altura=5.0, angulo_deg=55.0), suelo).fs
    if variante == "altura":
        peor = factor_seguridad_talud(perfil_talud(altura=7.0, angulo_deg=55.0), suelo).fs
    elif variante == "agua":
        peor = factor_seguridad_talud(perfil_talud(altura=5.0, angulo_deg=55.0), suelo, prof_freatico=1.5).fs
    elif variante == "sobrecarga":
        peor = factor_seguridad_talud(perfil_talud(altura=5.0, angulo_deg=55.0), suelo, sobrecarga_kpa=20.0, sobrecarga_x=(5.0 / math.tan(math.radians(55.0)), 10.0)).fs
    else:
        peor = factor_seguridad_talud(perfil_talud(altura=5.0, angulo_deg=55.0), suelo, kh=0.15).fs
    assert peor < base


def test_mas_cohesion_o_mas_friccion_mejoran_el_fs():
    p = perfil_talud(altura=5.0, angulo_deg=60.0)
    a = factor_seguridad_talud(p, SueloExc(gamma=18.0, c_kpa=10.0, phi_deg=25.0)).fs
    assert factor_seguridad_talud(p, SueloExc(gamma=18.0, c_kpa=20.0, phi_deg=25.0)).fs > a
    assert factor_seguridad_talud(p, SueloExc(gamma=18.0, c_kpa=10.0, phi_deg=32.0)).fs > a


def test_bermas_mejoran_el_fs_a_igual_angulo_de_cara():
    suelo = SueloExc(gamma=18.0, c_kpa=12.0, phi_deg=26.0)
    sin = factor_seguridad_talud(perfil_talud(altura=8.0, angulo_deg=60.0), suelo).fs
    con = factor_seguridad_talud(perfil_talud(altura=8.0, angulo_deg=60.0, bermas=((4.0, 2.0),)), suelo).fs
    assert con > sin


def test_angulo_maximo_seguro_cumple_y_el_siguiente_grado_no():
    suelo = SueloExc(gamma=18.0, c_kpa=8.0, phi_deg=28.0)
    req = factor_seguridad_requerido("construccion", sismo=False, analisis="efectivo")        # 1.25
    a = angulo_maximo_seguro(altura=6.0, suelo=suelo, fs_requerido=req)
    assert 25.0 < a < 90.0
    assert factor_seguridad_talud(perfil_talud(altura=6.0, angulo_deg=a), suelo).fs >= req - 1e-3
    assert factor_seguridad_talud(perfil_talud(altura=6.0, angulo_deg=min(a + 2.0, 90.0)), suelo).fs < req


def test_suelo_muy_resistente_permite_corte_vertical():
    suelo = SueloExc(gamma=18.0, c_kpa=80.0, phi_deg=30.0)
    assert angulo_maximo_seguro(altura=2.0, suelo=suelo, fs_requerido=1.25) == 90.0


def test_suelo_sin_resistencia_suficiente_devuelve_none():
    # arena suelta saturada con phi 20 y H grande: ni siquiera un talud suave cumple FS = 1.5 con nivel freático en la corona
    suelo = SueloExc(gamma=17.0, c_kpa=0.0, phi_deg=20.0, gamma_sat=19.0)
    assert angulo_maximo_seguro(altura=8.0, suelo=suelo, fs_requerido=1.5, prof_freatico=0.0, angulo_min_deg=30.0) is None


def test_validacion_de_entradas():
    with pytest.raises(ValueError):
        SueloExc(gamma=-1.0, c_kpa=0.0, phi_deg=30.0)
    with pytest.raises(ValueError):
        perfil_talud(altura=0.0, angulo_deg=45.0)
    with pytest.raises(ValueError):
        perfil_talud(altura=5.0, angulo_deg=95.0)
    with pytest.raises(ValueError):
        perfil_talud(altura=5.0, angulo_deg=45.0, bermas=((6.0, 1.0),))


def test_selector_talud_si_cabe_y_contencion_si_no():
    suelo = SueloExc(gamma=18.0, c_kpa=8.0, phi_deg=28.0)
    from src.excavacion_estabilidad import decidir_talud_o_contencion
    d = decidir_talud_o_contencion(6.0, suelo, distancia_lindero=50.0)
    assert d.alternativa == "talud" and 25.0 < d.angulo_deg < 90.0
    assert d.retiro_horizontal_m == pytest.approx(6.0 / math.tan(math.radians(d.angulo_deg)))
    assert decidir_talud_o_contencion(6.0, suelo, distancia_lindero=1.0).alternativa == "contencion"
    assert d.fs_requerido == 1.25
