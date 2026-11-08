import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import a4


def test_snapshot_tiene_1117_municipios_y_29_modificados_por_decreto_092():
    filas = a4._datos()["municipios"]
    assert len(filas) == 1117
    assert sum(1 for f in filas if f["modificado_por"]) == 29


def test_barranquilla_y_tubara_son_zona_baja_con_dmi():
    for nombre in ("Barranquilla", "Tubará"):
        r = a4.buscar(nombre)
        assert (r["aa"], r["av"]) == (0.10, 0.10)
        assert r["zona_calculada"] == "Baja" and r["capacidad_minima"] == "DMI"


def test_bogota_es_intermedia_no_alta_como_decia_la_tabla_departamental():
    r = a4.buscar("Bogotá D. C.")
    assert (r["aa"], r["av"]) == (0.15, 0.20)
    assert r["zona_calculada"] == "Intermedia" and r["capacidad_minima"] == "DMO"


def test_pereira_alta_des():
    assert a4.buscar("Pereira")["capacidad_minima"] == "DES"


@pytest.mark.parametrize("aa,av,zona", [(0.10, 0.10, "Baja"), (0.10, 0.15, "Intermedia"), (0.20, 0.20, "Intermedia"),
                                        (0.15, 0.25, "Alta"), (0.25, 0.10, "Alta")])
def test_zona_por_coeficientes_a_2_3(aa, av, zona):
    assert a4.zona_por_coeficientes(aa, av) == zona


def test_zona_calculada_coincide_con_la_zona_de_la_tabla_en_los_1117_municipios():
    distintos = [f["codigo"] for f in a4._datos()["municipios"]
                 if a4._norm(f["zona"]) != a4._norm(a4.zona_por_coeficientes(f["aa"], f["av"]))]
    assert distintos == []


def test_nombre_ambiguo_exige_departamento_o_codigo():
    with pytest.raises(a4.MunicipioNoEncontrado, match="ambiguo"):
        a4.buscar("Argelia")
    assert a4.buscar("Argelia", departamento="Cauca")["codigo"] == "19050"
    assert a4.buscar(codigo="19050")["departamento"] == "Cauca"


def test_municipio_inexistente():
    with pytest.raises(a4.MunicipioNoEncontrado):
        a4.buscar("Atlantis")
