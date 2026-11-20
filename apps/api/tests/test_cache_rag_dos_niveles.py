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

    def lt(self, _col, valor):
        self.limite = valor
        return self

    def execute(self):
        self.sb.viajes.append(self.op)
        if self.op == "delete":
            self.sb.purgas += 1
            return type("R", (), {"data": []})()
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

    def delete(self):
        return _Consulta(self.sb, "delete")


class _SupabaseFalso:
    def __init__(self):
        self.viajes: list[str] = []
        self.filas: dict = {}
        self.purgas = 0

    def table(self, nombre):
        assert nombre == "rag_cache_respuestas"
        return _Tabla(self)


@pytest.fixture()
def sb(monkeypatch):
    falso = _SupabaseFalso()
    monkeypatch.setattr(rmn, "sb", falso)
    monkeypatch.setattr(rmn, "RAG_CACHE_DISABLED", False)
    monkeypatch.setattr(rmn, "_ultima_purga_cache", {"t": 0.0})          # purga "reciente": no interfiere con los conteos
    monkeypatch.setattr(rmn.time, "monotonic", lambda: 1.0)
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


# --- Estadísticas de caudal IDEAM en RAM: una carga por instancia, cero viajes por comparación ------------------------------

class _SBCaudal:
    def __init__(self, filas, falla=False):
        self.filas, self.falla, self.viajes = filas, falla, 0

    def table(self, nombre):
        assert nombre == "ideam_caudal_estadisticas_mes"
        sb = self

        class Q:
            def __init__(self):
                self.rango, self.filtros = (0, 10**9), {}

            def select(self, *_a):
                return self

            def order(self, *_a):
                return self

            def range(self, a, b):
                self.rango = (a, b)
                return self

            def eq(self, c, v):
                self.filtros[c] = v
                return self

            def execute(self):
                sb.viajes += 1
                if sb.falla and not self.filtros:
                    raise ConnectionError("Supabase caído")
                fs = [f for f in sb.filas if all(f[c] == v for c, v in self.filtros.items())]
                return type("R", (), {"data": fs[self.rango[0]:self.rango[1] + 1]})()
        return Q()


def _filas_caudal(n_est):
    return [{"codigo_estacion": f"E{i:04d}", "mes": m, "promedio_m3s": 10.0 + i, "p90_m3s": 20.0 + i, "n_observaciones": 30}
            for i in range(n_est) for m in range(1, 13)]


def test_caudal_se_carga_una_vez_y_compara_sin_viajes(monkeypatch):
    sb = _SBCaudal(_filas_caudal(100))                            # 1.200 filas: 2 páginas
    monkeypatch.setattr(rmn, "sb", sb)
    monkeypatch.setattr(rmn, "_caudal_mes", {"cargado": 0.0, "datos": None})
    r = rmn._comparar_caudal_historico({"codigo_estacion": "E0005", "fecha": "2026-07-01", "caudal_m3s": 30.0})
    assert r == {"caudal_actual": 30.0, "promedio_historico": 15.0, "pct_diferencia": 100.0, "excede_p90": True, "n_anos_historicos": 30}
    viajes = sb.viajes
    assert viajes == 2
    for i in range(50):
        rmn._comparar_caudal_historico({"codigo_estacion": f"E{i:04d}", "fecha": "2026-03-01", "caudal_m3s": 1.0})
    assert sb.viajes == viajes                                    # 50 comparaciones, 0 viajes
    assert rmn._comparar_caudal_historico({"codigo_estacion": "NO-EXISTE", "fecha": "2026-03-01", "caudal_m3s": 1.0}) is None


def test_caudal_si_falla_la_carga_usa_la_consulta_puntual(monkeypatch):
    sb = _SBCaudal(_filas_caudal(3), falla=True)
    monkeypatch.setattr(rmn, "sb", sb)
    monkeypatch.setattr(rmn, "_caudal_mes", {"cargado": 0.0, "datos": None})
    r = rmn._comparar_caudal_historico({"codigo_estacion": "E0001", "fecha": "2026-02-01", "caudal_m3s": 11.0})
    assert r["promedio_historico"] == 11.0 and r["excede_p90"] is False


def test_no_guarda_contextos_recuperados_y_purga_vencidas_una_vez_por_hora(sb, monkeypatch):
    reloj = {"t": 10_000.0}
    monkeypatch.setattr(rmn.time, "monotonic", lambda: reloj["t"])
    monkeypatch.setattr(rmn, "_ultima_purga_cache", {"t": None})
    rmn._guardar_en_cache("ask", "p", {"respuesta": "r", "contextos_recuperados": [{"contenido": "x" * 5000}]})
    assert "contextos_recuperados" not in next(iter(sb.filas.values()))["respuesta"]
    assert sb.purgas == 1
    rmn._guardar_en_cache("ask", "q", {"respuesta": "r"})
    assert sb.purgas == 1                                                   # dentro de la hora: no vuelve a purgar
    reloj["t"] += rmn.RAG_CACHE_PURGA_S + 1
    rmn._guardar_en_cache("ask", "z", {"respuesta": "r"})
    assert sb.purgas == 2
