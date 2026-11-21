"""Parámetros de evidencia del aviso de vigencia (#261): solo se afirma una derogación con respaldo en el registro."""
import os
import sys
from pathlib import Path

for k, v in {"SUPABASE_URL": "http://localhost:54321", "SUPABASE_SERVICE_KEY": "x", "GROQ_API_KEY": "x",
             "OPENAI_API_KEY": "x"}.items():
    os.environ.setdefault(k, v)
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages" / "construdata"))

import pytest  # noqa: E402

import rag_multi_norma as rmn  # noqa: E402


def chunk(estado, derogada_por=None, alcance=None):
    return rmn.ChunkResult(chunk_id="c", norma="RES-X", seccion="1", contenido="texto", score=1.0,
                           estado_vigencia=estado, derogada_por=derogada_por, alcance_derogacion=alcance)


def test_vigente_y_sin_vincular_no_llevan_aviso():
    assert rmn.aviso_vigencia(chunk("vigente")) is None
    assert rmn.aviso_vigencia(chunk(None)) is None
    assert "⚠️" not in rmn._format_chunk_context(chunk("vigente"))


def test_derogada_total_con_reemplazo_se_avisa():
    a = rmn.aviso_vigencia(chunk("derogada_total", derogada_por="Resolución 0330 de 2017"))
    assert a.startswith("⚠️ NORMA DEROGADA") and "0330 de 2017" in a


def test_derogada_total_con_alcance_sin_reemplazo_se_avisa():
    a = rmn.aviso_vigencia(chunk("derogada_total", alcance="Derogada por la Resolución 0330 de 2017, art. 249"))
    assert a == "⚠️ NORMA DEROGADA"


@pytest.mark.parametrize("estado", ["derogada_total", "derogada_parcial"])
@pytest.mark.parametrize("respaldo", [None, "", "   ", "parcial", "Derogada.", "superada por ediciones posteriores"])
def test_derogacion_sin_respaldo_no_se_afirma(estado, respaldo):
    a = rmn.aviso_vigencia(chunk(estado, derogada_por=respaldo, alcance=respaldo))
    assert "DEROGADA" not in a and "NO CONFIRMADA" in a
    assert not rmn._RX_AVISO_EN_CONTEXTO.search(rmn._format_chunk_context(chunk(estado, alcance=respaldo)))


def test_derogada_parcial_exige_alcance_no_basta_el_reemplazo():
    sin = rmn.aviso_vigencia(chunk("derogada_parcial", derogada_por="Resolución 970 de 2024"))
    assert "DEROGADA" not in sin
    con = rmn.aviso_vigencia(chunk("derogada_parcial", derogada_por="Resolución 970 de 2024",
                                   alcance="Capítulo 2 (supervisión técnica)"))
    assert "PARCIALMENTE" in con and "Capítulo 2" in con and "970 de 2024" in con


def test_modificada_no_es_derogada_y_sigue_vigente():
    a = rmn.aviso_vigencia(chunk("modificada", derogada_por="Resolución 970 de 2024"))
    assert "DEROGADA" not in a and "MODIFICADA por Resolución 970 de 2024" in a and "sigue vigente" in a


def test_estado_raro_no_se_traduce_a_derogada():
    a = rmn.aviso_vigencia(chunk("suspendida_provisionalmente", derogada_por="Consejo de Estado"))
    assert "DEROGADA" not in a and "NO CONFIRMADA" in a


def test_guarda_quita_derogacion_inventada_cuando_el_aviso_se_degrada():
    # el registro dice derogada pero sin respaldo: el contexto ya no lo afirma, y la guarda de #264 quita la frase
    contexto = rmn._format_chunk_context(chunk("derogada_total"))
    resp = "El valor es 1,5 h.\n\nOjo: NORMA DEROGADA, consulte la vigente."
    assert "DEROGADA" not in rmn._quitar_aviso_vigencia_sin_respaldo(resp, contexto)


def test_modificada_con_alcance_muestra_el_acto():
    # caso real tras la migración 20261121150000: Res. 319 de 2022
    a = rmn.aviso_vigencia(chunk("modificada", alcance="Modificada por la Resolución 970 de 2024 (adiciona el "
                                                       "Capítulo 2, supervisión); sigue vigente en lo no modificado"))
    assert a.startswith("⚠️ NORMA MODIFICADA — Modificada por la Resolución 970 de 2024") and "DEROGADA" not in a
