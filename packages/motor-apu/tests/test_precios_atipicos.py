import pytest

from src.precios_atipicos import ReferenciaPrecios, normalizar

ITEMS = [
    {"item_no": 1, "nombre": "Tornillo De Acero Inoxidable De 7/8\" X 5\"", "unidad": "und", "n": 60, "mediana": 6000.0, "mad_log": 0.30, "q05": 3000, "q95": 12000},
    {"item_no": 2, "nombre": "Codo 90° Presion Pvc - 3/4\"", "unidad": "und", "n": 60, "mediana": 1800.0, "mad_log": 0.20, "q05": 900, "q95": 3500},
    {"item_no": 3, "nombre": "Cemento Gris Uso General Bolsa 50 Kg", "unidad": "und", "n": 60, "mediana": 32000.0, "mad_log": 0.05, "q05": 28000, "q95": 36000},
]


@pytest.fixture(scope="module")
def ref():
    return ReferenciaPrecios(ITEMS)


def test_normalizar_quita_acentos_y_conserva_fracciones():
    assert "3/4" in normalizar('Codo 90° Presión PVC - 3/4"')


def test_precio_cercano_a_la_mediana_es_consistente(ref):
    assert ref.evaluar("cemento gris bolsa 50 kg", 33000).veredicto == "consistente"


def test_precio_muy_alto_o_bajo_se_marca(ref):
    assert ref.evaluar("codo pvc 90 presion 3/4", 1800 * 12).veredicto in ("alto", "posible_error_de_unidad")
    assert ref.evaluar("codo pvc 90 presion 3/4", 1800 / 12).veredicto in ("bajo", "posible_error_de_unidad")


def test_factor_diez_se_reporta_como_posible_error_de_unidad(ref):
    assert ref.evaluar("tornillo acero inoxidable 7/8 x 5", 60000).veredicto == "posible_error_de_unidad"


def test_descripcion_sin_parecido_no_tiene_referencia(ref):
    assert ref.evaluar("helicóptero de rescate", 5000).veredicto == "sin_referencia"


def test_precio_invalido_no_tiene_referencia(ref):
    assert ref.evaluar("cemento", -5).veredicto == "sin_referencia"
    assert ref.evaluar("cemento", float("nan")).veredicto == "sin_referencia"


def test_el_aviso_no_afirma_error(ref):
    assert "no establece que el precio sea erróneo" in ref.evaluar("cemento gris bolsa 50 kg", 33000).aviso
