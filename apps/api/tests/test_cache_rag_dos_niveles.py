"""Caché de respuestas RAG en dos niveles (2026-11-16): memoria del proceso delante de Supabase.

Sin red: Supabase se reemplaza por un doble que cuenta cada viaje. Verifica lo que el cambio promete:
  * acierto de nivel 1 -> 0 viajes a Supabase;
  * acierto de nivel 2 -> 1 lectura y ninguna escritura (antes: lectura + UPDATE del contador `hits`);
  * nunca se sirve desde memoria algo que en Supabase ya expiró.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
for k, v in {"SUPABASE_URL": "http://localhost:54321", "SUPABASE_SERVICE_KEY": "clave-de-prueba-local",
             "SUPABASE_JWT_SECRET": "secreto-de-prueba-local", "GROQ_API_KEY": "clave-de-prueba-local"}.items():
    os.environ.setdefault(k, v)

import rag_multi_norma as rmn  # noqa: E402


class _Consulta:
    def __init__(self, sb, op, datos=None):
        self.sb, self.op, self.datos, self.id = sb, op, datos, None

    def select(self, *_a):
        return self

    def eq(self, _col, valor):
        self.id = valor
        return self

    def limit(self, _n):
        return self

    def execute(self):
        self.sb.viajes.append(self.op)
        if self.op == "select":
            fila = self.sb.filas.get(self.id)
            return type("R", (), {"data": [fila] if fila else []})()
        if self.op == "upsert":
            self.sb.filas[self.datos["id"]] = {"respuesta": self.datos["respuesta"], "expira_en": self.datos["expira_en"]}
        return type("R", (), {"data": []})()


class _Tabla:
    def __init__(self, sb):
        self.sb = sb

    def select(self, *_a):
        return _Consulta(self.sb, "select")

    def update(self, datos):
        return _Consulta(self.sb, "update", datos)

    def upsert(self, datos, on_conflict=None):
        return _Consulta(self.sb, "upsert", datos)


class _SupabaseFalso:
    def __init__(self):
        self.viajes: list[str] = []
        self.filas: dict = {}

    def table(self, nombre):
        assert nombre == "rag_cache_respuestas"
        return _Tabla(self)


@pytest.fixture()
def sb(monkeypatch):
    falso = _SupabaseFalso()
    monkeypatch.setattr(rmn, "sb", falso)
    monkeypatch.setattr(rmn, "RAG_CACHE_DISABLED", False)
    assert rmn._cache_l1 is not None, "en la API, cache.py debe estar disponible como nivel 1"
    rmn._cache_l1.clear()
    yield falso
    rmn._cache_l1.clear()


def test_guardar_y_repetir_no_vuelve_a_supabase(sb):
    rmn._guardar_en_cache("ask", "¿Qué es Aa?", {"respuesta": "aceleración pico efectiva"})
    assert sb.viajes == ["upsert"]
    r = rmn._buscar_en_cache("ask", "  ¿qué es   AA? ")                     # misma pregunta normalizada
    assert r == {"respuesta": "aceleración pico efectiva", "desde_cache": True}
    assert sb.viajes == ["upsert"]                                          # acierto de nivel 1: 0 viajes


def test_acierto_de_nivel_2_es_una_lectura_sin_escritura_y_sube_a_memoria(sb):
    rmn._guardar_en_cache("ask", "p", {"r": 1})
    rmn._cache_l1.clear()                                                   # otra instancia / reinicio
    sb.viajes.clear()
    assert rmn._buscar_en_cache("ask", "p") == {"r": 1, "desde_cache": True}
    assert sb.viajes == ["select"]                                          # sin UPDATE del contador
    assert rmn._buscar_en_cache("ask", "p") == {"r": 1, "desde_cache": True}
    assert sb.viajes == ["select"]                                          # ya en nivel 1


def test_nunca_sirve_de_memoria_lo_que_ya_expiro(sb):
    pasado = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)
    rmn._cache_l1.set(rmn._hash_cache("ask", "p"), ({"r": "viejo"}, pasado))
    sb.filas[rmn._hash_cache("ask", "p")] = {"respuesta": {"r": "viejo"}, "expira_en": pasado.isoformat()}
    assert rmn._buscar_en_cache("ask", "p") is None


def test_rutas_distintas_no_se_mezclan(sb):
    rmn._guardar_en_cache("ask", "p", {"r": "ask"})
    assert rmn._buscar_en_cache("ask_precios", "p") is None
