"""Resistencias de GEC 7 contra los valores resueltos del Apéndice C (FHWA-NHI-14-007, págs. 310–316), convertidos a SI.

Datos del ejemplo: qu = 14,5 psi, DDH = 6 in, barra #7 grado 75 (At = 0,60 in²), f'c = 4000 psi, malla grado 60
W2.9 (avm = 0,058 in²/ft) + 2 #5 sobre la cabeza (avn = 0,182 in²/ft), hi = 4 in, placa de 9 in, paramento final de 8 in
con #4 c/12 in (0,20 in²/ft), 4 pernos de 1/2 in × 4 1/8 in, tP = 1 in, tSH = 0,31 in, SSH = 6 in, SH = SV = 5 ft.

Resultados del libro: RPO = 51,2 kip (LP = 15,6 ft), RT = 45 kip, To/Tmax ≈ 0,7, RFF inicial = 36 kip, RFF final = 60,8 kip,
RFP inicial = 41,6 kip, RFP final = 36,9 kip, RFH = 47,1 kip.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.clavos import (FS_GEC7, arrancamiento_por_metro_kn, cf_paramento, cono_final, cono_inicial,
                        factor_carga_cabeza, flexion_paramento_kn, fs_tension, pernos_cabeza_kn, punzonamiento_kn,
                        tension_tendon_kn)

KIP = 4.448222
PSI_KPA = 6.894757
IN = 0.0254
FT = 0.3048
IN2_FT = IN * IN / FT          # in²/ft → m²/m
FC = 4000 * PSI_KPA / 1000     # MPa
FY60 = 60 * PSI_KPA            # MPa (ksi × 6,894757)
FY75 = 75 * PSI_KPA


def test_tabla_51_transcrita():
    assert FS_GEC7["estatica"]["global"] == 1.5 and FS_GEC7["estatica"]["arrancamiento"] == 2.0
    assert fs_tension(FY75) == 1.8 and fs_tension(1035.0) == 2.0
    assert FS_GEC7["sismica"]["arrancamiento"] == 1.5 and fs_tension(FY75, "sismica") == 1.35
    assert FS_GEC7["estatica"]["punzonamiento"] == 1.5 and FS_GEC7["estatica"]["flexion_paramento"] == 1.5


def test_arrancamiento_ejemplo():
    rpo = arrancamiento_por_metro_kn(14.5 * PSI_KPA, 6 * IN) * 15.6 * FT
    assert rpo / KIP == pytest.approx(51.2, rel=5e-3)


def test_tension_ejemplo():
    assert tension_tendon_kn(0.60 * IN * IN, FY75) / KIP == pytest.approx(45.0, rel=1e-3)


def test_carga_en_cabeza():
    assert factor_carga_cabeza(5 * FT) == pytest.approx(0.714, rel=1e-6)
    assert factor_carga_cabeza(3 * FT) == pytest.approx(0.6, rel=1e-9)


def test_cf_tabla_65():
    assert cf_paramento(4 * IN, "inicial") == 2.0
    assert cf_paramento(6 * IN, "inicial") == 1.5
    assert cf_paramento(8 * IN, "inicial") == 1.0
    assert cf_paramento(5 * IN, "inicial") == 1.5        # entre filas: el de la fila más gruesa (conservador)
    assert cf_paramento(8 * IN, "final") == 1.0
    with pytest.raises(ValueError):
        cf_paramento(3 * IN, "inicial")


def test_flexion_paramento_inicial_ejemplo():
    a_vm, a_vn = 0.058 * IN2_FT, 0.182 * IN2_FT
    rff = flexion_paramento_kn(espesor_m=4 * IN, fc_mpa=FC, fy_mpa=FY60, a_vn=a_vn, a_vm=a_vm, a_hn=a_vn, a_hm=a_vm,
                               sh_m=5 * FT, sv_m=5 * FT, cf=cf_paramento(4 * IN, "inicial"))
    assert rff / KIP == pytest.approx(36.0, rel=0.02)     # el libro usa la Ec. 6.15 simplificada


def test_flexion_paramento_final_ejemplo():
    a = 0.20 * IN2_FT
    rff = flexion_paramento_kn(espesor_m=8 * IN, fc_mpa=FC, fy_mpa=FY60, a_vn=a, a_vm=a, a_hn=a, a_hm=a,
                               sh_m=5 * FT, sv_m=5 * FT, cf=1.0)
    assert rff / KIP == pytest.approx(60.8, rel=0.02)


def test_punzonamiento_inicial_ejemplo():
    d, h = cono_inicial(9 * IN, 4 * IN)
    assert punzonamiento_kn(FC, d, h) / KIP == pytest.approx(41.6, rel=5e-3)


def test_punzonamiento_final_ejemplo():
    d, h = cono_final(4.125 * IN, 1 * IN, 0.31 * IN, 6 * IN)
    assert h / IN == pytest.approx(4.815) and d / IN == pytest.approx(9.63)
    assert punzonamiento_kn(FC, d, h) / KIP == pytest.approx(36.9, rel=0.015)   # el libro redondea hc a 4,8 in


def test_pernos_ejemplo():
    assert pernos_cabeza_kn(4, 0.5 * IN, FY60) / KIP == pytest.approx(47.1, rel=2e-3)


def test_monotonia_y_rechazos():
    assert punzonamiento_kn(FC, 0.3, 0.1) < punzonamiento_kn(FC, 0.3, 0.12)
    assert arrancamiento_por_metro_kn(100, 0.15) < arrancamiento_por_metro_kn(120, 0.15)
    for f, args in ((arrancamiento_por_metro_kn, (0.0, 0.15)), (tension_tendon_kn, (1e-4, -1.0)),
                    (punzonamiento_kn, (FC, 0.3, 0.1, 1.2)), (pernos_cabeza_kn, (0, 0.01, 400.0))):
        with pytest.raises(ValueError):
            f(*args)
    with pytest.raises(ValueError):       # refuerzo excesivo: brazo negativo
        flexion_paramento_kn(espesor_m=0.1, fc_mpa=20, fy_mpa=420, a_vn=0.01, a_vm=0.01, a_hn=0.01, a_hm=0.01,
                             sh_m=1.5, sv_m=1.5, cf=1.0)
