"""
Vigencia del Apéndice A-4 frente al servicio del SGC (issue #189). Sin LLM.

El servicio del SGC refleja el A-4 de 2010. Supía (Caldas) cambió de Aa 0,15 a
0,25 por el anexo técnico del Decreto 1711 de 2021; la tabla
nsr10_apendice_a4_municipios ya tiene el valor vigente
(scripts/ingesta/nsr10/_actualizar_a4_con_decreto_1711.py). El chat debe
advertir la diferencia y dar el valor vigente, sin editar el espejo del SGC.

Ejecutar: pytest apps/api/tests/test_vigencia_a4.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
load_dotenv(API_DIR / ".env")

import rag_multi_norma as r  # noqa: E402


def test_supia_tiene_el_valor_del_decreto_1711():
    fila = r.sb.table("nsr10_apendice_a4_municipios").select("aa,modificado_por,valores_originales_2010").eq("codigo", "17777").single().execute().data
    assert fila["aa"] == 0.25
    assert "1711" in (fila["modificado_por"] or "")
    assert fila["valores_originales_2010"]["aa"] == 0.15


def test_el_chat_advierte_cuando_el_sgc_muestra_el_valor_de_2010():
    reg = {"municipio": "Supía", "departamento": "Caldas", "aa": 0.15, "av": 0.3, "ae": 0.2, "ad": 0.1}
    aviso = r._advertencia_a4_modificado(reg)
    assert "Aa = 0.25" in aviso and "1711" in aviso and "Aa = 0.15" in aviso


def test_sin_aviso_si_el_sgc_coincide_con_el_a4_vigente():
    reg = {"municipio": "Supía", "departamento": "Caldas", "aa": 0.25, "av": 0.3, "ae": 0.2, "ad": 0.1}
    assert r._advertencia_a4_modificado(reg) == ""


def test_sin_aviso_para_municipio_no_modificado():
    reg = {"municipio": "Sincelejo", "departamento": "Sucre", "aa": 0.1, "av": 0.15, "ae": 0.07, "ad": 0.04}
    assert r._advertencia_a4_modificado(reg) == ""
