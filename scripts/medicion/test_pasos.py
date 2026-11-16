import os
import socket
import sys
import textwrap
import time
import types

import pytest

sys.path.insert(0, os.path.dirname(__file__))

import pasos as ps


@pytest.fixture()
def modulos(tmp_path):
    """Dos módulos reales en disco: `b` importa `f` de `a` con `from a import f` (la referencia que hay que reemplazar)."""
    (tmp_path / "mod_a.py").write_text(textwrap.dedent("""
        import time
        def hoja():
            time.sleep(0.02)
            return 1
        def f():
            time.sleep(0.01)
            return hoja() + 1
        def falla():
            raise ValueError("x")
        class C:
            def m(self):
                return hoja()
        """), encoding="utf-8")
    (tmp_path / "mod_b.py").write_text("from mod_a import f\ndef usar():\n    return f()\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    import mod_a
    import mod_b
    yield tmp_path, mod_a, mod_b
    sys.path.remove(str(tmp_path))
    for m in ("mod_a", "mod_b"):
        sys.modules.pop(m, None)


def test_mide_tambien_las_referencias_importadas_y_separa_el_tiempo_propio(modulos):
    raiz, a, b = modulos
    reg = ps.Registro()
    deshacer, hechos, omitidos = ps.instrumentar(reg, ["mod_a.py::f", "mod_a.py::hoja", "externo.execute", "mod_a.py::no_existe"], raiz)
    assert hechos == ["mod_a.py::f", "mod_a.py::hoja"] and omitidos == ["externo.execute", "mod_a.py::no_existe"]
    with reg.peticion("cadena"):
        assert b.usar() == 2                               # llamada por la referencia `from mod_a import f`
    r = reg.resumen()["cadena"]
    por = {p["paso"]: p for p in r["pasos"]}
    assert por["mod_a.py::f"]["llamadas"] == 1 and por["mod_a.py::hoja"]["llamadas"] == 1
    assert por["mod_a.py::f"]["p50_ms"] >= 30 - 1                       # inclusivo: 10 ms propios + 20 ms de hoja
    assert 8 <= por["mod_a.py::f"]["propio_p50_ms"] < 20               # propio: sin hoja
    deshacer()
    assert b.f is a.f and not hasattr(a.f, "__paso_original__")      # todo vuelve a su lugar


def test_metodo_de_clase_y_errores_se_registran_y_se_relanzan(modulos):
    raiz, a, _b = modulos
    reg = ps.Registro()
    deshacer, hechos, _ = ps.instrumentar(reg, ["mod_a.py::C.m", "mod_a.py::falla"], raiz)
    assert set(hechos) == {"mod_a.py::C.m", "mod_a.py::falla"}
    with reg.peticion("c"):
        assert a.C().m() == 1
    with pytest.raises(ValueError):
        with reg.peticion("c"):
            a.falla()
    r = reg.resumen()["c"]
    assert r["peticiones"]["n"] == 2 and r["peticiones"]["tasa_error"] == 0.5
    assert {p["paso"]: p["tasa_error"] for p in r["pasos"]} == {"mod_a.py::C.m": 0.0, "mod_a.py::falla": 1.0}
    deshacer()


def test_fuera_de_una_peticion_no_se_registra_nada(modulos):
    raiz, a, _b = modulos
    reg = ps.Registro()
    deshacer, _, _ = ps.instrumentar(reg, ["mod_a.py::hoja"], raiz)
    a.hoja()
    assert reg.llamadas == []
    deshacer()


def test_sin_red_externa_bloquea_internet_y_deja_la_maquina_local():
    with ps.sin_red_externa():
        with pytest.raises((ConnectionRefusedError, socket.gaierror)):
            socket.create_connection(("api.groq.com", 443), timeout=1)
        with pytest.raises((ConnectionRefusedError, socket.gaierror)):
            socket.getaddrinfo("example.supabase.co", 443)
        assert socket.getaddrinfo("127.0.0.1", 80)                 # lo local sigue resolviendo
    assert socket.create_connection is not None and socket.getaddrinfo.__module__ == "socket"
