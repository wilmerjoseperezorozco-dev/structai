import numpy as np
import pytest

from src.recomendador_insumos import RUTA, RecomendadorInsumos

ACTS = [
    {"numeral": "A1", "descripcion": "Concreto 21 MPa", "unidad": "m3", "insumos": ["cem", "arena", "grava", "agua", "mezcladora"]},
    {"numeral": "A2", "descripcion": "Concreto 28 MPa", "unidad": "m3", "insumos": ["cem", "arena", "grava", "agua", "aditivo"]},
    {"numeral": "A3", "descripcion": "Mortero 1:3", "unidad": "m3", "insumos": ["cem", "arena", "agua", "mezcladora"]},
    {"numeral": "B1", "descripcion": "Excavacion", "unidad": "m3", "insumos": ["retro", "operador"]},
]
INS = {c: {"descripcion": c.upper(), "unidad": "u", "tipo": "x"} for c in ["cem", "arena", "grava", "agua", "mezcladora", "aditivo", "retro", "operador"]}


def test_sugiere_insumos_de_actividades_parecidas_y_no_repite_los_visibles():
    r = RecomendadorInsumos(ACTS, INS)
    s = r.sugerir(["cem", "arena", "grava"], k=5)
    codigos = [x["codigo"] for x in s]
    assert "agua" in codigos and "cem" not in codigos and "retro" not in codigos


def test_incluye_actividades_de_apoyo():
    s = RecomendadorInsumos(ACTS, INS).sugerir(["cem", "arena"], k=3)
    assert s and s[0]["actividades_de_apoyo"]


def test_consulta_vacia_o_desconocida_no_sugiere_nada():
    r = RecomendadorInsumos(ACTS, INS)
    assert r.sugerir([]) == [] and r.sugerir(["inexistente"]) == []


def test_actividades_parecidas_ordena_por_similitud():
    p = RecomendadorInsumos(ACTS, INS).actividades_parecidas(["retro", "operador"], k=2)
    assert p[0]["numeral"] == "B1"


@pytest.mark.skipif(not RUTA.exists(), reason="falta el artefacto de composición")
def test_regresion_acierto_ocultando_un_insumo_en_datos_reales():
    """Reproduce, con el módulo, la evaluación de P2a: acierto@10 debe quedar por encima de 0,70 (resultado offline: 0,78 a 0,84)."""
    r = RecomendadorInsumos.desde_json()
    rng = np.random.default_rng(1)
    aciertos, n = 0, 0
    for a in r.actividades:
        if len(a["insumos"]) < 4:
            continue
        oculto = rng.choice(a["insumos"]); visibles = [c for c in a["insumos"] if c != oculto]
        s = r.sugerir(visibles, k=10, excluir_numeral=a["numeral"])
        aciertos += oculto in [x["codigo"] for x in s]; n += 1
    assert n > 200 and aciertos / n > 0.70
