import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))

from contrato_motor import AVISO_RESPONSABILIDAD, ResultadoMotor, exigir


def _ok(**kw):
    base = dict(valor=3.68, unidad_si="adimensional (pulg. de SN)", ecuacion="log10 W18 = ZR*So + ...",
                referencia_normativa="AASHTO 93; INVIAS Manual de Diseño de Pavimentos", supuestos=["R=0.85"],
                en_borde_dominio=False)
    base.update(kw)
    return ResultadoMotor(**base)


def test_contrato_incluye_aviso_de_responsabilidad_por_defecto():
    assert _ok().aviso_responsabilidad_profesional == AVISO_RESPONSABILIDAD


@pytest.mark.parametrize("campo", ["unidad_si", "ecuacion", "referencia_normativa"])
def test_contrato_rechaza_campos_vacios(campo):
    with pytest.raises(ValidationError):
        _ok(**{campo: "  "})


def test_contrato_rechaza_valor_no_finito():
    for malo in (float("nan"), float("inf")):
        with pytest.raises(ValidationError):
            _ok(valor=malo)


def test_contrato_exige_bandera_de_borde_explicita():
    with pytest.raises(ValidationError):
        ResultadoMotor(valor=1.0, unidad_si="m", ecuacion="x", referencia_normativa="y", supuestos=[])


def test_aviso_no_puede_borrarse():
    with pytest.raises(ValidationError):
        _ok(aviso_responsabilidad_profesional="")


def test_exigir_devuelve_el_valor_tabulado():
    assert exigir("PVC", {"PVC": 150}, "RAS 2000 Título B", "material") == 150


def test_exigir_lanza_valueerror_con_la_norma():
    with pytest.raises(ValueError, match="RAS 2000 Título B"):
        exigir("TITANIO", {"PVC": 150}, "RAS 2000 Título B", "material")
