"""Regresion del caso real 2026-11-06: el chat mostro "A.C.P.M. BARRANQUILLA
$3.732 COP/gl, captura 2026-08-08" -- un precio ~3x por debajo del oficial y con
la fecha de CARGA presentada como fecha del precio.

Las pruebas puras no tocan red; la ultima golpea Supabase real (mismo criterio
que el resto de tests de integracion de este proyecto).
"""
from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
PACKAGES_DIR = API_DIR.parents[1] / "packages" / "construdata"
sys.path.insert(0, str(PACKAGES_DIR))

import pytest
from dotenv import load_dotenv

import precio_vigencia as pv

load_dotenv(API_DIR / ".env")


@pytest.mark.parametrize("nombre", ["A.C.P.M. BARRANQUILLA", "A.C.P.M.", "ACPM", "Diesel corriente", "Gasolina corriente"])
def test_combustible_viejo_por_galon_genera_advertencia(nombre: str) -> None:
    assert pv.advertencia_plausibilidad(nombre, "gl", 3731.82) is not None


def test_combustible_con_precio_vigente_no_genera_advertencia() -> None:
    assert pv.advertencia_plausibilidad("A.C.P.M. BARRANQUILLA", "gl", 11291.0) is None


def test_otros_insumos_y_otras_unidades_no_se_tocan() -> None:
    assert pv.advertencia_plausibilidad("Cemento gris", "kg", 400.0) is None
    assert pv.advertencia_plausibilidad("Aceite para formaleta", "gl", 5000.0) is None
    assert pv.advertencia_plausibilidad("A.C.P.M.", "m3", 100.0) is None


@pytest.mark.parametrize("tipo", ["catalogo_construdata", "contrato_real_triple_a_acometidas", None, ""])
def test_fecha_de_archivos_cargados_es_fecha_de_carga(tipo) -> None:
    txt = pv.etiqueta_fecha(tipo, "2026-08-08")
    assert "cargado en StructAI" in txt and "NO esta registrada" in txt
    assert "captura" not in txt.lower()


@pytest.mark.parametrize("tipo", ["invias_regional", "catalogo_iad_mipymes_detalle", "proveedor_homecenter_colombia"])
def test_fuentes_con_fecha_real_conservan_su_fecha(tipo: str) -> None:
    assert pv.etiqueta_fecha(tipo, "2026-01-15") == "fecha: 2026-01-15"


def test_precio_cero_no_es_precio() -> None:
    assert not pv.precio_utilizable(0.0, None)
    assert not pv.precio_utilizable(None, None)
    assert pv.precio_utilizable(3731.82, None)
    assert pv.precio_utilizable(None, 120000.0)   # solo mano de obra si es un dato


def test_contexto_real_acpm_barranquilla_advierte_y_sin_filas_en_cero() -> None:
    import rag_multi_norma as rm

    resultados = rm.buscar_precios_apu("precio del ACPM por galón en Barranquilla", top_k=10)
    acpm = [r for r in resultados if "a.c.p.m" in r.nombre.lower()]
    assert acpm, "la busqueda debe seguir encontrando el insumo (no se esconde, se advierte)"
    assert all(r.precio and r.precio > 0 for r in resultados), "no deben llegar filas con precio 0"
    for r in acpm:
        if r.precio < pv.PISO_COMBUSTIBLE_COP_GL:
            ctx = rm._format_precio_context(r)
            assert "ADVERTENCIA" in ctx
            assert "cargado en StructAI" in ctx
