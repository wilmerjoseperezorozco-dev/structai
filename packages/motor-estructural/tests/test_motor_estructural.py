"""Tests motor-estructural (InfraCortex) — IFC → PINN → NSR-10 Títulos A/B/C.

Mismo patrón que el resto de motores: cada aserción verifica contra el
valor real observado al correr el motor, no un número supuesto. Los
valores esperados se verificaron antes corriendo el pipeline completo
end-to-end vía TestClient contra /estructural/analizar-nudo e
/estructural/inspeccion-estribos.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ifcopenshell
import ifcopenshell.api
import numpy as np
import pytest

from src.infracortex_core import InfracortexEngine
from src.load_engine import calcular_demanda_cortante_nudo, chequeo_nsr10_nudo, ZONA_SISMICA_ATLANTICO, CARGAS_GRAVEDAD_DEFAULT, _espectro, _sa, _eta_amortiguamiento
from src.vision_engine import InfracortexVisionSensor, DeteccionEstribo, ResultadoEspaciado

PROPS_CONCRETO = {"fc": 28.0, "fy": 420.0, "b": 300.0, "h": 300.0, "d": 265.0, "Av": 56.5, "s": 75.0}


@pytest.fixture
def nudo_ifc_path(tmp_path):
    """Columna en el origen P(0,0,0), viga a 3 m de altura en Z."""
    model = ifcopenshell.api.run("project.create_file")
    ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Infracortex_Test")
    ifcopenshell.api.run("unit.assign_unit", model)

    columna = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcColumn", name="Col")
    viga = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBeam", name="Viga")

    ifcopenshell.api.run("geometry.edit_object_placement", model, product=columna, matrix=np.eye(4))
    matriz_viga = np.eye(4)
    matriz_viga[2, 3] = 3.0
    ifcopenshell.api.run("geometry.edit_object_placement", model, product=viga, matrix=matriz_viga)

    ruta = tmp_path / "nudo_test.ifc"
    model.write(str(ruta))
    return str(ruta), columna.GlobalId, viga.GlobalId


# ── InfracortexEngine — topología del nudo ──────────────────────────────────

def test_extraer_topologia_nudo_retorna_tupla_de_tres(nudo_ifc_path):
    """BUG CORREGIDO: la versión original descartaba la rotación de la
    columna (get_local_placement calculado sin asignar) y retornaba solo
    2 valores — una función que por nombre extrae la topología del NUDO
    (viga + columna) en realidad ignoraba la columna por completo."""
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)

    resultado = motor.extraer_topologia_nudo(guid_viga, guid_col)

    assert len(resultado) == 3
    rotacion_viga, rotacion_columna, posicion_nudo = resultado
    assert rotacion_viga.shape == (3, 3)
    assert rotacion_columna.shape == (3, 3)
    assert np.allclose(rotacion_viga, np.eye(3))
    assert np.allclose(rotacion_columna, np.eye(3))
    assert np.allclose(posicion_nudo, [0.0, 0.0, 3000.0])


def test_ensamblar_rigidez_local_produce_matriz_12x12_por_miembro(nudo_ifc_path):
    ruta, guid_col, guid_viga = nudo_ifc_path
    motor = InfracortexEngine(ruta)
    rot_viga, rot_columna, _ = motor.extraer_topologia_nudo(guid_viga, guid_col)

    T12_viga = motor.ensamblar_rigidez_local(rot_viga)
    T12_columna = motor.ensamblar_rigidez_local(rot_columna)

    assert T12_viga.shape == (12, 12)
    assert T12_columna.shape == (12, 12)


# ── load_engine — demanda sísmica/gravedad + chequeo NSR-10 ─────────────────

def test_calcular_demanda_cortante_nudo_valores_reales():
    """Valores verificados end-to-end (TestClient /estructural/analizar-nudo)."""
    resultado = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD_DEFAULT, ZONA_SISMICA_ATLANTICO, altura_piso_mm=3000.0
    )

    assert resultado["T_seg"] == pytest.approx(0.3396, abs=1e-3)
    assert resultado["Sa"] == pytest.approx(0.45, abs=1e-3)
    assert resultado["Vs_basal_N"] / 1000 == pytest.approx(8.96, abs=0.01)
    assert resultado["Vu_gravedad_N"] / 1000 == pytest.approx(43.04, abs=0.01)
    assert resultado["Vu_sismo_N"] / 1000 == pytest.approx(47.20, abs=0.01)
    assert resultado["combinacion_governa"] == "1.2D+1.0E+1.0L"
    # El caso sísmico gobierna sobre el de solo gravedad — Vu_diseno debe ser el máximo
    assert resultado["Vu_diseno_N"] == max(resultado["Vu_gravedad_N"], resultado["Vu_sismo_N"])


def test_chequeo_nsr10_nudo_valores_reales():
    """Vu=47.20kN < phi*Vn=116.52kN → cumple, margen 59.5%."""
    resultado = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD_DEFAULT, ZONA_SISMICA_ATLANTICO, altura_piso_mm=3000.0
    )
    chequeo = chequeo_nsr10_nudo(PROPS_CONCRETO, resultado["Vu_diseno_N"])

    assert chequeo["Vc_kN"] == pytest.approx(71.51, abs=0.01)
    assert chequeo["Vs_kN"] == pytest.approx(83.85, abs=0.01)
    assert chequeo["Vn_max_kN"] == pytest.approx(809.6, abs=0.1)
    assert chequeo["phi_Vn_kN"] == pytest.approx(116.52, abs=0.01)
    assert chequeo["margen_pct"] == pytest.approx(59.5, abs=0.1)
    assert chequeo["cumple"] is True


def test_chequeo_nsr10_nudo_falla_cuando_demanda_supera_capacidad():
    """Comportamiento inverso: una demanda mayor que phi*Vn debe marcar cumple=False."""
    chequeo = chequeo_nsr10_nudo(PROPS_CONCRETO, Vu_N=200_000.0)  # 200 kN >> 116.52 kN disponibles
    assert chequeo["cumple"] is False
    assert chequeo["margen_pct"] < 0


def test_espectro_nsr10_A_2_6_valores_oficiales():
    """Regresión (2026-09-30): la version anterior de _espectro()/_sa()
    usaba la convencion ASCE7/IBC (Ts=SD1/SDS con SD1=Av*Fv*I) en vez de
    las ecuaciones oficiales NSR-10 A.2.6 -- daba TC=0.40*Av*Fv/(Aa*Fa)
    en vez del 0.48 real (A.2.6-2) y omitia el factor 1.2 de la ecuacion
    A.2.6-1, subestimando Sa hasta ~17% para T>TC. El caso de 3 pisos ya
    cubierto en test_calcular_demanda_cortante_nudo_valores_reales cae
    en la meseta (T=0.3396 < TC=0.96) y NUNCA ejercito el bug -- por eso
    quedo invisible. Este test cubre las 3 ramas reales con la zona
    sismica del Atlantico ya usada en el resto del archivo."""
    esp = _espectro(ZONA_SISMICA_ATLANTICO)

    assert esp["SDS"] == pytest.approx(0.45, abs=1e-4)
    assert esp["SD1"] == pytest.approx(0.432, abs=1e-4)   # 1.2*Av*Fv*I -- antes 0.36 (sin el 1.2)
    assert esp["Ts"] == pytest.approx(0.96, abs=1e-4)     # TC real -- antes 0.80
    assert esp["TL"] == pytest.approx(4.32, abs=1e-4)     # ausente antes

    # Meseta (T <= TC)
    assert _sa(0.3396, esp) == pytest.approx(0.45, abs=1e-4)
    assert _sa(0.96, esp) == pytest.approx(0.45, abs=1e-4)
    # Rama descendente 1.2*Av*Fv*I/T (TC < T <= TL) -- la que tenia el bug del 20%
    assert _sa(2.0, esp) == pytest.approx(0.216, abs=1e-4)
    # Rama de periodo largo 1.2*Av*Fv*I*TL/T^2 (T > TL) -- antes inexistente
    assert _sa(5.0, esp) == pytest.approx(0.07465, abs=1e-4)


def test_eta_amortiguamiento_default_5pct_es_exactamente_1() -> None:
    """Issue #75 -- con xi_pct=5.0 (NSR-10 estándar, sin aislamiento) el
    factor de Eurocódigo 8 debe dar EXACTAMENTE 1.0, no solo aproximado
    -- si diera 0.9999999 por ruido de punto flotante, cada cálculo
    default (99% de los usuarios, que nunca tocan este parámetro)
    quedaría contaminado por un factor que no debería existir."""
    assert _eta_amortiguamiento(5.0) == 1.0


def test_eta_amortiguamiento_valores_publicados() -> None:
    """eta = max(sqrt(10/(5+xi)), 0.55), EN 1998-1 §3.2.2.2. xi=20% es el
    valor de referencia citado en la literatura de aislamiento sísmico
    (amortiguamiento efectivo típico de un sistema de aislamiento de
    base) -- eta=0.632 calculado a mano: sqrt(10/25)=sqrt(0.4)=0.6325.
    xi=30% ejercita el piso de 0.55 (sqrt(10/35)=0.5345 < 0.55, se
    clampa) -- caso real de disipadores de alto amortiguamiento."""
    assert _eta_amortiguamiento(20.0) == pytest.approx(0.6325, abs=1e-4)
    assert _eta_amortiguamiento(30.0) == pytest.approx(0.55, abs=1e-4)  # clamp del piso


def test_sa_con_xi_pct_distinto_de_5_escala_las_3_ramas() -> None:
    """Issue #75 -- extensión NO normativa: con xi_pct=20 cada rama del
    espectro debe escalarse por el mismo eta=0.6325 verificado arriba,
    sobre los valores oficiales ya cubiertos en
    test_espectro_nsr10_A_2_6_valores_oficiales."""
    esp = _espectro(ZONA_SISMICA_ATLANTICO)
    eta = _eta_amortiguamiento(20.0)

    assert _sa(0.3396, esp, xi_pct=20.0) == pytest.approx(eta * 0.45, abs=1e-4)
    assert _sa(2.0, esp, xi_pct=20.0) == pytest.approx(eta * 0.216, abs=1e-4)
    assert _sa(5.0, esp, xi_pct=20.0) == pytest.approx(eta * 0.07465, abs=1e-4)
    # Default sin pasar xi_pct sigue siendo el comportamiento NSR-10 puro
    assert _sa(0.3396, esp) == pytest.approx(0.45, abs=1e-4)


def test_calcular_demanda_cortante_nudo_xi_pct_default_no_cambia_resultado() -> None:
    """Regresión de cero-cambio: llamar sin xi_pct debe dar exactamente
    los mismos valores que antes de que existiera el parámetro (mismos
    números que test_calcular_demanda_cortante_nudo_valores_reales)."""
    resultado = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD_DEFAULT, ZONA_SISMICA_ATLANTICO, altura_piso_mm=3000.0
    )
    assert resultado["xi_pct"] == 5.0
    assert resultado["eta_amortiguamiento"] == 1.0
    assert resultado["Sa"] == pytest.approx(0.45, abs=1e-3)


# ── vision_engine — inspección de estribos ───────────────────────────────────

def test_inspeccion_estribos_detecta_seis_y_marca_dos_fallas():
    """Mismo layout verificado end-to-end: separaciones 70/70/80/110/70mm,
    s_max=75mm → 2 fallas (80 y 110), 3 OK."""
    imagen = np.full((500, 600, 3), 45, dtype=np.uint8)
    posiciones_px = [60, 130, 200, 280, 390, 460]

    sensor = InfracortexVisionSensor(s_max_diseno_mm=75.0, escala_mm_por_px=1.0)
    detecciones, separaciones = sensor.analizar(imagen, posiciones_px)

    assert len(detecciones) == 6
    assert len(separaciones) == 5
    obtenidas = [s.separacion_mm for s in separaciones]
    assert obtenidas == pytest.approx([70.0, 70.0, 80.0, 110.0, 70.0])

    fallos = [s for s in separaciones if not s.cumple_nsr10]
    assert len(fallos) == 2
    assert {round(f.separacion_mm) for f in fallos} == {80, 110}


def test_calcular_separaciones_ordena_por_y_no_por_orden_de_llegada():
    sensor = InfracortexVisionSensor(s_max_diseno_mm=75.0, escala_mm_por_px=1.0)
    detecciones_desordenadas = [
        DeteccionEstribo(id=0, y_centro_px=200.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=1, y_centro_px=60.0, x1_px=0, x2_px=100, confianza=0.9),
        DeteccionEstribo(id=2, y_centro_px=130.0, x1_px=0, x2_px=100, confianza=0.9),
    ]

    resultados = sensor.calcular_separaciones(detecciones_desordenadas)

    assert [r.separacion_mm for r in resultados] == pytest.approx([70.0, 70.0])
