"""
Regresión de packages/construdata/microzonificacion_local.py -- issue #76.

Golpea Supabase real, no mocks -- mismo criterio que el resto de tests de
integración de este proyecto. Verifica el camino completo: nombre de
municipio (forma canónica que devuelve sgc_amenaza_sismica.py) -> aviso de
microzonificación, para las 3 ciudades ingestadas hoy (Bogotá, Cali,
Pereira), y que una ciudad sin dato (ej. Medellín, geografía confirmada
pero tabla de coeficientes aún pendiente) devuelve None en vez de
fabricar un aviso.
"""
from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

PACKAGES_DIR = API_DIR.parents[1] / "packages" / "construdata"
sys.path.insert(0, str(PACKAGES_DIR))

from dotenv import load_dotenv

load_dotenv(API_DIR / ".env")

import microzonificacion_local as mz  # noqa: E402


def test_bogota_cali_pereira_tienen_microzonificacion() -> None:
    casos = {
        "Bogotá, D.C.": ("Bogotá, D.C.", 16),
        "Cali": ("Santiago de Cali", 13),
        "Pereira": ("Pereira", 7),
    }
    for municipio, (ciudad_esperada, n_zonas_esperado) in casos.items():
        r = mz.consultar_microzonificacion(municipio)
        assert r is not None, f"'{municipio}' debería tener microzonificación local ingestada (issue #76)"
        assert r["ciudad"] == ciudad_esperada
        assert r["n_zonas"] == n_zonas_esperado, (
            f"'{municipio}': se esperaban {n_zonas_esperado} zonas, la base real tiene {r['n_zonas']} "
            "-- revisar si se re-ingestó con otro conteo"
        )
        aviso = mz.formatear_aviso(r)
        assert ciudad_esperada in aviso
        assert "A.2.9.1" in aviso


def test_municipio_sin_microzonificacion_devuelve_none() -> None:
    """Medellín tiene geografía de zonas confirmada pero la tabla de
    coeficientes nunca se ingestó (mapeo zona->número no confiable en la
    única fuente encontrada) -- no debe fabricar un aviso."""
    assert mz.consultar_microzonificacion("Medellín") is None
