"""Tests para el cómputo de cantidades paramétrico (columnas/vigas de concreto)"""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from src.cantidades import (
    DENSIDAD_ACERO_KG_M3,
    DIAMETRO_BARRA_M,
    Estribos,
    GeometriaElementoConcreto,
    RefuerzoLongitudinal,
    TipoElementoConcreto,
    calcular_apu_dinamico,
    calcular_cantidades,
    peso_barra_kg_m,
)
from src.models import UnidadMedida


def test_peso_barra_se_deriva_de_geometria():
    """peso_kg_m = area_transversal x densidad_acero — verificable a mano."""
    d = DIAMETRO_BARRA_M["4"]  # 1/2" = 0.0127 m
    esperado = (math.pi / 4 * d**2) * DENSIDAD_ACERO_KG_M3
    assert peso_barra_kg_m("4") == pytest.approx(esperado)
    # Valor de referencia bien conocido para barra #4 (1/2"): ~0.994 kg/m
    assert peso_barra_kg_m("4") == pytest.approx(0.994, abs=0.01)


def test_diametro_no_reconocido_falla_explicito():
    with pytest.raises(ValueError):
        peso_barra_kg_m("99")


def test_volumen_concreto_coincide_con_catalogo_estatico_40x30():
    """El catálogo estático ya validado tenía 0.12 m³/ml para una
    columna 40x30cm — la fórmula geométrica debe reproducir ese mismo
    valor exacto para L=1m, confirmando que no es un número inventado."""
    geo = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA,
        base_m=0.40, altura_m=0.30, longitud_m=1.0,
    )
    cant = calcular_cantidades(geo)
    assert cant.volumen_concreto_m3 == pytest.approx(0.12, abs=0.001)


def test_volumen_escala_linealmente_con_longitud():
    geo_corta = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.30, altura_m=0.30, longitud_m=2.0,
    )
    geo_larga = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.30, altura_m=0.30, longitud_m=4.0,
    )
    c1 = calcular_cantidades(geo_corta)
    c2 = calcular_cantidades(geo_larga)
    assert c2.volumen_concreto_m3 == pytest.approx(c1.volumen_concreto_m3 * 2, rel=1e-6)


def test_dimensiones_no_positivas_fallan():
    with pytest.raises(ValueError):
        GeometriaElementoConcreto(tipo=TipoElementoConcreto.COLUMNA, base_m=0, altura_m=0.3, longitud_m=1.0)
    with pytest.raises(ValueError):
        GeometriaElementoConcreto(tipo=TipoElementoConcreto.VIGA, base_m=0.3, altura_m=0.3, longitud_m=-1.0)


def test_recubrimiento_excesivo_falla():
    with pytest.raises(ValueError):
        GeometriaElementoConcreto(
            tipo=TipoElementoConcreto.COLUMNA, base_m=0.20, altura_m=0.20,
            longitud_m=3.0, recubrimiento_m=0.15,
        )


def test_refuerzo_longitudinal_escala_con_numero_de_barras():
    base = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.40, altura_m=0.40, longitud_m=3.0,
        refuerzo_longitudinal=RefuerzoLongitudinal(numero_barras=4, diametro_pulg="6"),
    )
    doble = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.40, altura_m=0.40, longitud_m=3.0,
        refuerzo_longitudinal=RefuerzoLongitudinal(numero_barras=8, diametro_pulg="6"),
    )
    c1 = calcular_cantidades(base)
    c2 = calcular_cantidades(doble)
    assert c2.peso_acero_longitudinal_kg == pytest.approx(c1.peso_acero_longitudinal_kg * 2, rel=1e-6)
    assert c1.peso_acero_longitudinal_kg > 0


def test_estribos_mas_espaciamiento_da_menos_estribos():
    apretado = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.40, altura_m=0.40, longitud_m=3.0,
        estribos=Estribos(diametro_pulg="3", espaciamiento_m=0.10),
    )
    holgado = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.40, altura_m=0.40, longitud_m=3.0,
        estribos=Estribos(diametro_pulg="3", espaciamiento_m=0.20),
    )
    c1 = calcular_cantidades(apretado)
    c2 = calcular_cantidades(holgado)
    assert c1.numero_estribos > c2.numero_estribos
    assert c1.peso_acero_estribos_kg > c2.peso_acero_estribos_kg


def test_formaleta_columna_cuatro_caras():
    geo = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.30, altura_m=0.40, longitud_m=2.0,
    )
    cant = calcular_cantidades(geo)
    esperado = 2 * (0.30 + 0.40) * 2.0
    assert cant.area_formaleta_m2 == pytest.approx(esperado, abs=0.001)


def test_formaleta_viga_sin_cara_superior_por_defecto():
    geo = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.VIGA, base_m=0.30, altura_m=0.40, longitud_m=2.0,
    )
    cant_sin = calcular_cantidades(geo)
    geo_con = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.VIGA, base_m=0.30, altura_m=0.40, longitud_m=2.0,
        incluye_cara_superior_formaleta=True,
    )
    cant_con = calcular_cantidades(geo_con)
    assert cant_con.area_formaleta_m2 > cant_sin.area_formaleta_m2


# ── Integración con el motor APU existente ──────────────────────────

def test_calcular_apu_dinamico_produce_resultado_valido():
    geo = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.40, altura_m=0.30, longitud_m=3.0,
        refuerzo_longitudinal=RefuerzoLongitudinal(numero_barras=4, diametro_pulg="6"),
        estribos=Estribos(diametro_pulg="3", espaciamiento_m=0.15),
    )
    result = calcular_apu_dinamico(geo, calidad_concreto="3000")
    assert result.unidad == UnidadMedida.UN
    assert result.precio_unitario > 0
    assert result.costo_materiales > 0
    assert result.costo_mano_obra > 0
    assert result.pu_mean > 0
    assert result.pu_p05 < result.pu_mean < result.pu_p95


def test_calcular_apu_dinamico_escala_con_dimensiones():
    """Dos columnas de distinto tamaño deben dar precios distintos --
    a diferencia del catálogo estático, que daba el mismo costo por ml
    sin importar la seccion real que el usuario necesitaba."""
    pequena = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.25, altura_m=0.25, longitud_m=3.0,
        refuerzo_longitudinal=RefuerzoLongitudinal(numero_barras=4, diametro_pulg="4"),
        estribos=Estribos(diametro_pulg="3", espaciamiento_m=0.15),
    )
    grande = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.COLUMNA, base_m=0.60, altura_m=0.60, longitud_m=3.0,
        refuerzo_longitudinal=RefuerzoLongitudinal(numero_barras=8, diametro_pulg="8"),
        estribos=Estribos(diametro_pulg="3", espaciamiento_m=0.15),
    )
    r1 = calcular_apu_dinamico(pequena)
    r2 = calcular_apu_dinamico(grande)
    assert r2.precio_unitario > r1.precio_unitario * 2


def test_calidad_concreto_invalida_falla_explicito():
    geo = GeometriaElementoConcreto(
        tipo=TipoElementoConcreto.VIGA, base_m=0.30, altura_m=0.40, longitud_m=4.0,
    )
    with pytest.raises(ValueError):
        calcular_apu_dinamico(geo, calidad_concreto="9999")
