"""Tests para Motor Vulnerabilidad Vivienda (checklist AIS, Título E NSR-10).

Mismo patrón que motor-geopot: cada aserción recalcula el valor esperado
con la fórmula documentada en el propio módulo (promedio por aspecto ×
peso, suma total), nunca con un número supuesto.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from src.checklist import (
    ASPECTOS_ORDEN,
    CRITERIOS,
    CRITERIOS_POR_ID,
    PESO_ASPECTO,
    evaluar_vulnerabilidad,
    listar_criterios,
)
from src import EvaluacionVulnerabilidadRequest, consultar_checklist, evaluar


# ─── Estructura del checklist ────────────────────────────────────────────

def test_hay_exactamente_15_criterios():
    assert len(CRITERIOS) == 15


def test_pesos_de_aspectos_suman_1():
    assert sum(PESO_ASPECTO.values()) == pytest.approx(1.0)


def test_todos_los_aspectos_referenciados_tienen_peso():
    aspectos_en_criterios = {c.aspecto for c in CRITERIOS}
    assert aspectos_en_criterios == set(ASPECTOS_ORDEN)
    assert aspectos_en_criterios == set(PESO_ASPECTO)


def test_cada_criterio_tiene_las_3_descripciones_no_vacias():
    for c in CRITERIOS:
        assert c.descripcion_baja.strip()
        assert c.descripcion_media.strip()
        assert c.descripcion_alta.strip()


def test_ids_de_criterios_son_unicos():
    ids = [c.id for c in CRITERIOS]
    assert len(ids) == len(set(ids))


# ─── Fórmula real: promedio por aspecto × peso, sumado ──────────────────

def _respuestas_uniformes(nivel: int) -> dict[str, int]:
    return {c.id: nivel for c in CRITERIOS}


def test_todo_baja_da_calificacion_global_1_y_clasificacion_baja():
    resultado = evaluar_vulnerabilidad(_respuestas_uniformes(1))
    assert resultado.calificacion_global == pytest.approx(1.0)
    assert resultado.clasificacion == "BAJA"


def test_todo_media_da_calificacion_global_2_y_clasificacion_media():
    resultado = evaluar_vulnerabilidad(_respuestas_uniformes(2))
    assert resultado.calificacion_global == pytest.approx(2.0)
    assert resultado.clasificacion == "MEDIA"


def test_todo_alta_da_calificacion_global_3_y_clasificacion_alta():
    resultado = evaluar_vulnerabilidad(_respuestas_uniformes(3))
    assert resultado.calificacion_global == pytest.approx(3.0)
    assert resultado.clasificacion == "ALTA"


def test_reproduce_el_ejemplo_resuelto_del_manual_ais_pagina_2_23():
    """Ejemplo real del manual AIS (Capítulo II, pág. 2-23):
    geométricos (2,1,1) -> promedio 1.33; constructivos (2,2,2) -> 2;
    estructurales (3,2,3,2,3,3) -> 2.67; cimentación=2, suelos=2, entorno=2.
    Calificación global = 1.33x0.2 + 2x0.2 + 2.67x0.3 + 2x0.1 + 2x0.1 + 2x0.1
    = 0.2 + 0.4 + 0.9 + 0.2 + 0.2 + 0.2 = 2.1 = MEDIA (redondeando al
    entero más cercano, tal como documenta _clasificar())."""
    respuestas = {
        "irregularidad_planta": 2,
        "cantidad_muros_dos_direcciones": 1,
        "irregularidad_altura": 1,
        "calidad_juntas_pega": 2,
        "tipo_disposicion_unidades": 2,
        "calidad_materiales": 2,
        "muros_confinados_reforzados": 3,
        "detalles_columnas_vigas_confinamiento": 2,
        "vigas_amarre_corona": 3,
        "caracteristicas_aberturas": 2,
        "entrepiso": 3,
        "amarre_cubiertas": 3,
        "cimentacion": 2,
        "suelos": 2,
        "entorno": 2,
    }
    resultado = evaluar_vulnerabilidad(respuestas)
    assert resultado.calificacion_global == pytest.approx(2.1, abs=0.01)
    assert resultado.clasificacion == "MEDIA"


def test_calificacion_ponderada_de_cada_aspecto_redondea_el_promedio_antes_de_ponderar():
    """El manual AIS redondea el promedio de cada aspecto a un nivel
    entero (1/2/3) ANTES de multiplicarlo por el peso -- ver
    _redondear_a_nivel() y el ejemplo resuelto (2.67 -> 3, no 2.67x0.3)."""
    respuestas = _respuestas_uniformes(1)
    # sube 2 de los 6 criterios de "estructurales" a 3: promedio (3+3+1+1+1+1)/6=1.67 -> redondea a 2
    respuestas["muros_confinados_reforzados"] = 3
    respuestas["vigas_amarre_corona"] = 3
    resultado = evaluar_vulnerabilidad(respuestas)

    por_aspecto = {a.aspecto: a for a in resultado.aspectos}
    ids_estructurales = [c.id for c in CRITERIOS if c.aspecto == "estructurales"]
    valores_estructurales = [
        3 if cid in ("muros_confinados_reforzados", "vigas_amarre_corona") else 1
        for cid in ids_estructurales
    ]
    promedio_esperado = sum(valores_estructurales) / len(valores_estructurales)
    assert promedio_esperado == pytest.approx(1.6667, abs=0.001)

    assert por_aspecto["estructurales"].calificacion_promedio == pytest.approx(round(promedio_esperado, 2))
    assert por_aspecto["estructurales"].calificacion == 2  # 1.67 redondea a 2, no a 1
    assert por_aspecto["estructurales"].ponderada == pytest.approx(2 * PESO_ASPECTO["estructurales"])
    # los aspectos no tocados siguen en baja (1) exacto
    assert por_aspecto["geometricos"].calificacion == 1


# ─── Validación de entradas ───────────────────────────────────────────────

def test_falla_si_falta_un_criterio():
    respuestas = _respuestas_uniformes(1)
    del respuestas["entorno"]
    with pytest.raises(ValueError, match="Faltan respuestas"):
        evaluar_vulnerabilidad(respuestas)


def test_falla_si_hay_un_criterio_desconocido():
    respuestas = _respuestas_uniformes(1)
    respuestas["criterio_inventado"] = 1
    with pytest.raises(ValueError, match="no reconocidos"):
        evaluar_vulnerabilidad(respuestas)


def test_falla_si_un_valor_no_es_1_2_o_3():
    respuestas = _respuestas_uniformes(1)
    respuestas["entorno"] = 5
    with pytest.raises(ValueError, match="1 \\(baja\\)"):
        evaluar_vulnerabilidad(respuestas)


# ─── listar_criterios() ───────────────────────────────────────────────────

def test_listar_criterios_devuelve_15_entradas_con_aspecto_label():
    criterios = listar_criterios()
    assert len(criterios) == 15
    for c in criterios:
        assert set(c["descripciones"]) == {"baja", "media", "alta"}
        assert c["aspecto_label"]


# ─── src/__init__.py — capa pública que consume apps/api/routers ─────────
# No reverifica fórmulas (ya cubiertas arriba): solo confirma que cada
# wrapper recibe el Request Pydantic real y delega correctamente.

def test_wrapper_consultar_checklist_coincide_con_listar_criterios():
    assert consultar_checklist() == listar_criterios()


def test_wrapper_evaluar_devuelve_clasificacion_y_metodologia():
    req = EvaluacionVulnerabilidadRequest(
        respuestas=_respuestas_uniformes(1), municipio="Barranquilla"
    )
    r = evaluar(req)
    assert r["clasificacion"] == "BAJA"
    assert r["municipio"] == "Barranquilla"
    assert "AIS" in r["metodologia"]


def test_wrapper_evaluar_propaga_error_como_dict_no_excepcion():
    req = EvaluacionVulnerabilidadRequest(respuestas={"solo_este": 1})
    r = evaluar(req)
    assert "error" in r
