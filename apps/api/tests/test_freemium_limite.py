"""
Tests de verificar_limite_apu_mes() — el enforcement server-side del límite
freemium de APU/mes (encontrado sin aplicar el 2026-08-01: la UI lo
mostraba pero cualquiera con un token válido podía saltárselo llamando la
API directo). No golpea Supabase real — mockea main._uso_sb con la misma
forma de respuesta que devuelve el cliente real (visto en producción).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

import main as main_module  # noqa: E402


def _mock_uso_sb(plan: str, calculos_este_mes: int) -> MagicMock:
    """Simula main._uso_sb devolviendo un perfil con `plan` y un conteo de
    `calculos_este_mes` filas en apu_calculations — misma forma que la
    respuesta real de supabase-py (.data para maybe_single, .count para
    select con count="exact")."""
    mock = MagicMock()

    perfil_response = MagicMock()
    perfil_response.data = {"plan": plan}

    conteo_response = MagicMock()
    conteo_response.count = calculos_este_mes

    # profiles: .table().select().eq().maybe_single().execute()
    # apu_calculations: .table().select().eq().gte().execute()
    tabla_mock = MagicMock()
    tabla_mock.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = perfil_response
    tabla_mock.select.return_value.eq.return_value.gte.return_value.execute.return_value = conteo_response
    mock.table.return_value = tabla_mock
    return mock


def test_usuario_free_bajo_el_limite_no_bloquea():
    with patch.object(main_module, "_uso_sb", _mock_uso_sb("free", 3)):
        main_module.verificar_limite_apu_mes("user-1")  # no debe lanzar


def test_usuario_free_en_el_limite_bloquea_con_402():
    with patch.object(main_module, "_uso_sb", _mock_uso_sb("free", main_module.LIMITE_APU_MES_FREE)):
        with pytest.raises(HTTPException) as exc_info:
            main_module.verificar_limite_apu_mes("user-2")
        assert exc_info.value.status_code == 402


def test_usuario_pro_nunca_bloquea_aunque_tenga_muchos_calculos():
    with patch.object(main_module, "_uso_sb", _mock_uso_sb("pro", 999)):
        main_module.verificar_limite_apu_mes("user-3")  # no debe lanzar


def test_sin_uso_sb_disponible_no_bloquea_fail_open():
    with patch.object(main_module, "_uso_sb", None):
        main_module.verificar_limite_apu_mes("user-4")  # no debe lanzar
