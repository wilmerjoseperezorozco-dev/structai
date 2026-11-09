import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from contrato_motor.propiedades import verificar_homogeneidad, verificar_monotonia


def test_monotonia_acepta_funcion_creciente():
    verificar_monotonia(lambda x: x ** 2, [0, 1, 2, 3])


def test_monotonia_detecta_violacion():
    with pytest.raises(AssertionError):
        verificar_monotonia(lambda x: -(x - 2) ** 2, [0, 1, 2, 3, 4])


def test_monotonia_decreciente_y_estricta():
    verificar_monotonia(lambda x: 1 / x, [1, 2, 4], creciente=False, estricta=True)
    with pytest.raises(AssertionError):
        verificar_monotonia(lambda x: 1.0, [1, 2, 3], estricta=True)


def test_homogeneidad_de_una_ley_de_potencia():
    verificar_homogeneidad(lambda q, d: q ** 1.852 / d ** 4.87, dict(q=2.0, d=0.2), "q", 1.852)
    verificar_homogeneidad(lambda q, d: q ** 1.852 / d ** 4.87, dict(q=2.0, d=0.2), "d", -4.87)


def test_homogeneidad_detecta_exponente_equivocado():
    with pytest.raises(AssertionError):
        verificar_homogeneidad(lambda q, d: q ** 1.852 / d ** 4.87, dict(q=2.0, d=0.2), "q", 2.0)
