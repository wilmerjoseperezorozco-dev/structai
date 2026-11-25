import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import v_municipio as m


def test_tabla_completa_y_valores_de_la_figura():
    t = m._tabla()
    assert len(t) == 1122
    assert {v.v_m_s for v in t.values()} <= {17.0, 22.0, 28.0, 33.0, 36.0}
    assert all(v.v_m_s >= v.v_cabecera_m_s for v in t.values())          # nunca por debajo de la cabecera


@pytest.mark.parametrize("cod,v", [("08001", 36.0), ("13001", 36.0), ("88001", 36.0), ("54001", 17.0), ("91001", 28.0)])
def test_puntos_inequivocos_de_la_figura(cod, v):
    # Barranquilla y Cartagena en la región 5; San Andrés por el recuadro; Cúcuta en la franja 1; Leticia en la nota (28)
    assert m.v_basica(cod).v_m_s == v


def test_codigo_con_ceros_y_estado():
    assert m.v_basica("8001").divipola == "08001"
    assert "SIN VALIDAR" in m.ESTADO_VALIDACION
    with pytest.raises(KeyError):
        m.v_basica("99999")
