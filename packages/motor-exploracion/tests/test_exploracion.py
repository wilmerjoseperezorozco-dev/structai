"""Pruebas de motor-exploracion: valores de oro (tablas NSR-10 H.3), cálculo independiente de Boussinesq,
reglas de alerta preregistradas en #273 y sabotaje (entradas inválidas deben fallar, nunca asumir valores)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from src import alertas, categoria, sondeos
from src.contrato_api import SolicitudExploracion, TerrenoLote, pre_disenar_exploracion


def _terreno(**kw):
    base = dict(ubicacion="lote", relieve_local_1km_m=3.0, fraccion_pendiente_suave_5km=0.95, relieve_5km_m=30.0)
    base.update(kw)
    return TerrenoLote(**base)


def _sol(**kw):
    base = dict(niveles=5, carga_max_servicio_kn=2500.0, planta_ancho_m=15.0, planta_largo_m=25.0,
                profundidad_excavacion_m=0.0, cimentacion="zapatas", suelo="desconocido", amenaza_sismica="baja",
                terreno=_terreno())
    base.update(kw)
    return SolicitudExploracion(**base)


# ── oro: Tabla H.3.1-1 y Tabla H.3.2-1 ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("niveles,cat", [(1, "baja"), (3, "baja"), (4, "media"), (10, "media"), (11, "alta"),
                                         (20, "alta"), (21, "especial")])
def test_categoria_por_niveles(niveles, cat):
    assert categoria.por_niveles(niveles) == cat


@pytest.mark.parametrize("q,cat", [(100.0, "baja"), (800.0, "baja"), (801.0, "media"), (4000.0, "media"),
                                   (4001.0, "alta"), (8000.0, "alta"), (8001.0, "especial")])
def test_categoria_por_carga(q, cat):
    assert categoria.por_carga(q) == cat


def test_se_asigna_la_categoria_mas_desfavorable():
    c = categoria.categoria(2, 5000.0)
    assert (c["por_niveles"], c["por_carga"], c["categoria"]) == ("baja", "alta", "alta")


def test_borde_de_carga_marcado():
    assert categoria.categoria(5, 3900.0)["en_borde"] is True
    assert categoria.categoria(6, 2500.0)["en_borde"] is False


@pytest.mark.parametrize("cat,n,z", [("baja", 3, 6.0), ("media", 4, 15.0), ("alta", 4, 25.0), ("especial", 5, 30.0)])
def test_tabla_sondeos(cat, n, z):
    e = sondeos.exploracion_minima(cat, None, None, False, 0.0)
    assert e["n_sondeos_min"] == n and e["profundidad_bajo_excavacion_m"] == z
    assert e["n_sondeos_a_profundidad_min"] == math.ceil(n / 2)


# ── Boussinesq: comparación con integración numérica independiente de cargas puntuales ──────────────────────────────

def _boussinesq_numerico(B, L, z, k=400):
    s, dA = 0.0, (B / k) * (L / k)
    for i in range(k):
        x = -B / 2 + (i + 0.5) * B / k
        for j in range(k):
            y = -L / 2 + (j + 0.5) * L / k
            R = math.sqrt(x * x + y * y + z * z)
            s += 3 * z ** 3 / (2 * math.pi * R ** 5) * dA
    return s


@pytest.mark.parametrize("B,L", [(10.0, 10.0), (10.0, 40.0)])
def test_profundidad_10pct_coincide_con_integracion_numerica(B, L):
    z = sondeos.profundidad_10pct(B, L)
    assert _boussinesq_numerico(B, L, z) == pytest.approx(0.10, abs=2e-4)


def test_profundidad_10pct_valores_de_texto():
    # bulbo de 0,1·q: ≈ 2B bajo una planta cuadrada y ≈ 6B bajo una franja larga (gráficas clásicas de isobaras)
    assert sondeos.profundidad_10pct(10.0, 10.0) / 10.0 == pytest.approx(2.09, abs=0.02)
    assert sondeos.profundidad_10pct(10.0, 1000.0) / 10.0 == pytest.approx(6.3, abs=0.2)


def test_gobierna_el_criterio_mayor_y_se_suma_la_excavacion():
    r = pre_disenar_exploracion(_sol(profundidad_excavacion_m=3.0))["exploracion_minima"].valor
    assert r["gobierna"] == "incremento_10pct"            # media: 15 m de tabla < ~33 m del bulbo de 15×25 m
    assert r["profundidad_desde_terreno_m"] == pytest.approx(r["profundidad_bajo_excavacion_m"] + 3.0)


def test_losa_considera_1_5_B():
    r = sondeos.exploracion_minima("baja", 4.0, 4.0, True, 0.0)
    assert r["criterios_m"]["1.5_ancho_losa"] == pytest.approx(6.0)


# ── alertas de nivel freático (H2c, H8) ─────────────────────────────────────────────────────────────────────────────

def _nf(**kw):
    return pre_disenar_exploracion(_sol(terreno=_terreno(**kw)))["nivel_freatico"].valor


def test_llanura_con_relieve_bajo_da_alarma():
    assert _nf(relieve_local_1km_m=6.5)["estado"] == "alarma"


def test_llanura_sin_alarma_nunca_dice_nivel_hondo_como_conclusion():
    v = _nf(relieve_local_1km_m=12.0)
    assert v["estado"] == "sin_alarma" and "no significa" in v["mensaje"]


@pytest.mark.parametrize("frac,rel", [(0.80, 30.0), (0.95, 90.0), (0.5, 300.0)])
def test_fuera_de_llanura_no_aplica(frac, rel):
    assert _nf(fraccion_pendiente_suave_5km=frac, relieve_5km_m=rel)["estado"] == "no_aplica_terreno"


def test_solo_municipio_no_evalua_la_alarma():
    t = TerrenoLote(ubicacion="municipio")
    assert pre_disenar_exploracion(_sol(terreno=t))["nivel_freatico"].valor["estado"] == "sin_dato_lote"


def test_nivel_medido_prevalece_y_quita_el_piezometro():
    r = pre_disenar_exploracion(_sol(terreno=_terreno(nivel_freatico_medido_m=4.0)))
    assert r["nivel_freatico"].valor["estado"] == "medido"
    assert all(x["medicion"] != "piezometro" for x in r["recomendaciones"].valor)


def test_falta_metrica_dem():
    assert _nf(relieve_5km_m=None)["estado"] == "sin_dato_dem"


# ── recomendaciones (H1, H7) ────────────────────────────────────────────────────────────────────────────────────────

def _rec(**kw):
    return {x["medicion"]: x for x in pre_disenar_exploracion(_sol(**kw))["recomendaciones"].valor}


def test_pilote_excavado_sin_nivel_pide_piezometro_alta():
    r = _rec(cimentacion="pilote_excavado", suelo="granular", terreno=_terreno(relieve_local_1km_m=20.0))
    assert r["piezometro"]["prioridad"] == "alta" and "46 %" in r["piezometro"]["evidencia"]


@pytest.mark.parametrize("suelo,veredicto", [("cohesivo", "evaluar"), ("granular", "por_seguridad"),
                                             ("mixto", "no_concluyente"), ("desconocido", "sin_dato")])
def test_prueba_de_carga_segun_suelo(suelo, veredicto):
    assert _rec(cimentacion="pilote_hincado", suelo=suelo)["prueba_de_carga_estatica"]["veredicto"] == veredicto


def test_zapatas_no_piden_prueba_de_carga():
    assert "prueba_de_carga_estatica" not in _rec(cimentacion="zapatas")


def test_licuacion_solo_con_suelo_granular_y_amenaza_intermedia_o_alta():
    assert "evaluacion_licuacion" in _rec(suelo="granular", amenaza_sismica="alta")
    assert "evaluacion_licuacion" not in _rec(suelo="granular", amenaza_sismica="baja")
    assert "evaluacion_licuacion" not in _rec(suelo="cohesivo", amenaza_sismica="alta")


def test_remocion_en_masa_como_contexto():
    assert "estabilidad_de_taludes" in _rec(terreno=_terreno(eventos_remocion_5km=3))
    assert "estabilidad_de_taludes" not in _rec(terreno=_terreno(eventos_remocion_5km=0))


# ── contrato y sabotaje ─────────────────────────────────────────────────────────────────────────────────────────────

def test_contrato_completo_y_serializable():
    r = pre_disenar_exploracion(_sol(cimentacion="pilote_excavado"))
    assert set(r) == {"categoria", "exploracion_minima", "nivel_freatico", "recomendaciones"}
    for v in r.values():
        assert v.aviso_responsabilidad_profesional and v.supuestos and v.referencia_normativa
        v.model_dump_json()
    assert any("punta" in a for a in r["exploracion_minima"].advertencias)


@pytest.mark.parametrize("campo,valor", [("niveles", 0), ("niveles", 5.0), ("carga_max_servicio_kn", -1.0),
                                         ("carga_max_servicio_kn", float("nan")), ("cimentacion", "caisson"),
                                         ("suelo", "arcilla"), ("amenaza_sismica", "moderada"),
                                         ("profundidad_excavacion_m", -0.5)])
def test_entradas_invalidas_fallan(campo, valor):
    with pytest.raises(ValidationError):
        _sol(**{campo: valor})


def test_planta_incompleta_falla():
    with pytest.raises(ValidationError):
        _sol(planta_largo_m=None)


def test_losa_sin_planta_falla():
    with pytest.raises(ValidationError):
        _sol(cimentacion="losa", planta_ancho_m=None, planta_largo_m=None)


def test_municipio_con_metricas_de_lote_falla():
    with pytest.raises(ValidationError):
        TerrenoLote(ubicacion="municipio", relieve_local_1km_m=3.0)


def test_categoria_desconocida_falla():
    with pytest.raises(ValueError):
        sondeos.exploracion_minima("muy_alta", None, None, False, 0.0)


def test_constantes_preregistradas_no_cambian():
    assert (alertas.UMBRAL_RELIEVE_M, alertas.HAMMOND_FRAC_SUAVE, alertas.HAMMOND_RELIEVE_MAX_M) == (6.5, 0.80, 90.0)
