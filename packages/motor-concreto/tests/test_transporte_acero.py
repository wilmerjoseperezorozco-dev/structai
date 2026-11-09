"""Transporte del acero: casos a mano con vehículos ficticios (los datos de moto/camioneta no tienen fuente, se pasan explícitos)."""
import pytest

from src.figuras_acero import traslapo_traccion_mm
from src.transporte_acero import KG_CO2_GAL, RENDIMIENTO_ANDI_KM_GAL, Vehiculo, planificar

MOTO = Vehiculo("moto (prueba)", 2.0, 40.0, 100.0, KG_CO2_GAL["gasolina_epa"])
CAMION = Vehiculo("camión 2 ejes", 6.0, 4000.0, RENDIMIENTO_ANDI_KM_GAL["camion_2_ejes"]["plano"], KG_CO2_GAL["diesel_fecoc"], "ANDI 2018 / UPME 2020")


def test_185_en_moto_corta_en_tienda_tres_por_varilla():
    p = planificar([1.85] * 30, "4", MOTO, km_ida_vuelta=10)
    assert p.estrategia == "corte en tienda" and p.varillas_compradas == 10 and p.empalmes == 0 and p.viajes >= 1
    assert p.galones == pytest.approx(p.viajes * 10 / 100)
    assert p.co2_transporte_kg == pytest.approx(p.galones * 8.887)


def test_pieza_larga_en_moto_sin_permiso_es_inviable():
    p = planificar([5.6] * 4, "4", MOTO, 10)
    assert p.estrategia == "inviable" and p.varillas_compradas == 0 and p.advertencias


def test_empalmes_usan_el_traslapo_nsr_y_gastan_acero():
    p = planificar([5.6] * 4, "4", MOTO, 10, aceptar_empalmes=True)
    lap = traslapo_traccion_mm("4", 21.0, 420.0) / 1000
    assert p.estrategia == "empalmes para que quepa" and p.empalmes > 0
    assert p.acero_extra_kg == pytest.approx(p.empalmes * lap * 0.9968, rel=0.02) and p.co2_acero_extra_kg > 0
    assert p.acero_kg > 4 * 5.6 * 0.9968


def test_camion_de_6_m_lleva_las_piezas_sin_empalmes():
    p = planificar([5.6] * 4, "4", CAMION, 10)
    assert p.estrategia == "corte en tienda" and p.empalmes == 0 and p.acero_extra_kg == 0


def test_traslapo_mayor_que_el_largo_de_carga_lanza_error():
    corto = Vehiculo("carga muy corta", 0.5, 40.0, 100.0, 8.887)
    with pytest.raises(ValueError):
        planificar([5.6], "4", corto, 10, aceptar_empalmes=True)
