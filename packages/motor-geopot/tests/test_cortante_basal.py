import importlib.util
import math
import sys
from pathlib import Path

import pytest

_RUTA = Path(__file__).resolve().parents[1] / "src" / "cortante_basal.py"
_spec = importlib.util.spec_from_file_location("cortante_basal_test", _RUTA)
cb = importlib.util.module_from_spec(_spec)
sys.modules["cortante_basal_test"] = cb
_spec.loader.exec_module(cb)


def test_fa_fv_valores_de_tabla_y_extremos():
    assert cb.coef_fa(0.1, "D") == 1.6 and cb.coef_fa(0.05, "D") == 1.6      # Aa ≤ 0,1
    assert cb.coef_fa(0.5, "E") == 0.9 and cb.coef_fa(0.8, "E") == 0.9       # Aa ≥ 0,5
    assert cb.coef_fv(0.2, "C") == 1.6 and cb.coef_fv(0.4, "D") == 1.6


def test_interpolacion_lineal_entre_columnas():
    assert cb.coef_fa(0.25, "D") == pytest.approx(1.3)       # entre 1,4 (0,2) y 1,2 (0,3)
    assert cb.coef_fv(0.25, "D") == pytest.approx(1.9)       # entre 2,0 y 1,8
    assert cb.coef_fa(0.15, "C") == pytest.approx(1.2)       # 1,2 y 1,2


def test_perfil_f_y_perfil_invalido_se_rechazan():
    with pytest.raises(ValueError, match="A.2.10"):
        cb.coef_fa(0.2, "F")
    with pytest.raises(ValueError):
        cb.coef_fv(0.2, "Z")


def test_periodos_del_espectro_y_ramas():
    fa, fv = 1.3, 1.9
    tc, tl = cb.periodos_espectro(0.25, 0.25, fa, fv)
    assert tc == pytest.approx(0.48 * 0.25 * 1.9 / (0.25 * 1.3)) and tl == pytest.approx(2.4 * 1.9)
    meseta = 2.5 * 0.25 * fa
    assert cb.sa_espectro(0.0, 0.25, 0.25, fa, fv) == pytest.approx(meseta)
    assert cb.sa_espectro(tc, 0.25, 0.25, fa, fv) == pytest.approx(meseta)
    assert cb.sa_espectro(1.5, 0.25, 0.25, fa, fv) == pytest.approx(1.2 * 0.25 * fv / 1.5)
    assert cb.sa_espectro(0.3, 0.25, 0.25, fa, fv, I=1.25) == pytest.approx(1.25 * meseta)


def test_el_espectro_es_continuo_en_tc():
    fa, fv = 1.3, 1.9
    tc, _ = cb.periodos_espectro(0.25, 0.25, fa, fv)
    antes, despues = cb.sa_espectro(tc - 1e-9, 0.25, 0.25, fa, fv), cb.sa_espectro(tc + 1e-9, 0.25, 0.25, fa, fv)
    assert antes == pytest.approx(despues, rel=1e-6)


def test_periodo_aproximado_y_cu():
    assert cb.periodo_aproximado(9.2) == pytest.approx(0.047 * 9.2 ** 0.9)
    assert cb.periodo_aproximado(9.2, "porticos_acero") == pytest.approx(0.072 * 9.2 ** 0.8)
    assert cb.cu(0.10, 1.6) == pytest.approx(1.75 - 1.2 * 0.10 * 1.6)
    assert cb.cu(0.25, 1.9) == 1.2                      # 1,75 − 0,57 = 1,18 → piso de 1,2
    assert cb.cu(0.5, 2.4) == 1.2


def test_exponente_k_por_tramos():
    assert cb.exponente_k(0.3) == 1.0 and cb.exponente_k(0.5) == 1.0
    assert cb.exponente_k(1.0) == pytest.approx(1.25)
    assert cb.exponente_k(2.5) == pytest.approx(2.0) and cb.exponente_k(3.0) == 2.0


def test_r_por_capacidad_y_reducciones():
    assert cb.r_reducido("DES") == 7.0 and cb.r_reducido("DMO") == 5.0 and cb.r_reducido("DMI") == 2.5
    assert cb.r_reducido("DES", phi_r=0.75, phi_p=0.9) == pytest.approx(7.0 * 0.75 * 0.9)
    with pytest.raises(ValueError):
        cb.r_reducido("DXX")
    with pytest.raises(ValueError):
        cb.r_reducido("DES", phi_a=1.2)


def test_distribucion_suma_vs_y_crece_con_la_altura():
    f = cb.distribuir_fuerzas(600.0, (1000.0, 1000.0, 1000.0), (3.2, 6.2, 9.2), T=0.35)
    assert sum(f) == pytest.approx(600.0) and f[0] < f[1] < f[2]
    # k=1: proporcional a m·h
    assert f[0] / f[2] == pytest.approx(3.2 / 9.2)


def test_distribucion_con_periodo_largo_usa_k_mayor():
    corta = cb.distribuir_fuerzas(100.0, (1.0, 1.0), (3.0, 6.0), T=0.3)
    larga = cb.distribuir_fuerzas(100.0, (1.0, 1.0), (3.0, 6.0), T=2.0)       # k = 1,75
    assert larga[1] > corta[1]


def test_cortante_basal_ejemplo_calculado_a_mano():
    pesos = (1500.0, 1500.0, 1400.0)
    cbz = cb.cortante_basal(aa=0.25, av=0.25, perfil="D", capacidad="DES", pesos_nivel_kn=pesos,
                            alturas_nivel_m=(3.2, 6.2, 9.2))
    assert cbz.fa == pytest.approx(1.3) and cbz.fv == pytest.approx(1.9)
    assert cbz.T == pytest.approx(0.047 * 9.2 ** 0.9)
    assert cbz.sa == pytest.approx(2.5 * 0.25 * 1.3)                         # T=0,346 < Tc=0,70 → meseta
    assert cbz.vs_kn == pytest.approx(0.8125 * 4400.0)
    assert sum(cbz.fuerzas_elasticas_kn) == pytest.approx(cbz.vs_kn)
    assert sum(cbz.fuerzas_diseno_kn) == pytest.approx(cbz.vs_kn / 7.0)
    assert cbz.r == 7.0 and cbz.k == 1.0


def test_importancia_amplifica_y_deriva_usa_i_uno():
    base = cb.cortante_basal(aa=0.25, av=0.25, perfil="D", capacidad="DES", pesos_nivel_kn=(1000.0,), alturas_nivel_m=(3.0,))
    iv = cb.cortante_basal(aa=0.25, av=0.25, perfil="D", capacidad="DES", pesos_nivel_kn=(1000.0,), alturas_nivel_m=(3.0,),
                           grupo_uso="IV")
    assert iv.vs_kn == pytest.approx(1.5 * base.vs_kn)
    assert iv.sa_deriva == pytest.approx(base.sa)                           # A.6.2.1.2


def test_zona_baja_con_dmi_da_fuerza_de_diseno_pequena_pero_positiva():
    z = cb.cortante_basal(aa=0.10, av=0.10, perfil="C", capacidad="DMI", pesos_nivel_kn=(800.0, 800.0),
                          alturas_nivel_m=(3.0, 6.0))
    assert 0 < sum(z.fuerzas_diseno_kn) < sum(z.fuerzas_elasticas_kn)


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        cb.cortante_basal(aa=0.2, av=0.2, perfil="D", capacidad="DES", pesos_nivel_kn=(0.0,), alturas_nivel_m=(3.0,))
    with pytest.raises(ValueError):
        cb.cortante_basal(aa=0.2, av=0.2, perfil="D", capacidad="DES", pesos_nivel_kn=(1.0,), alturas_nivel_m=(3.0,),
                          grupo_uso="V")
    with pytest.raises(ValueError):
        cb.distribuir_fuerzas(10.0, (1.0, 1.0), (3.0,), 0.3)
