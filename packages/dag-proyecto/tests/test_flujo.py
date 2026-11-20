"""Flujo atómico (#221, fase 2): caché por contenido, idempotencia de efectos, atomicidad y paralelismo."""
import sys
import threading
import time
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "contrato-motor"))

from dag_proyecto import Artefacto, hash_canonico
from dag_proyecto.flujo import AlmacenAcotado, ConflictoIdempotencia, Flujo, Paso


def _flujo(contador, escritos, *, norma="NSR-10 v1", falla_en=None, almacen=None, max_hilos=4):
    """a(x) y b(y) independientes → c(a, b) → registrar(c) [efecto]."""
    def paso(nombre, f):
        def fn(p, ent):
            contador[nombre] = contador.get(nombre, 0) + 1
            if falla_en == nombre:
                raise RuntimeError(f"falla en {nombre}")
            return f(p, ent)
        return fn

    def registrar(p, ent):
        contador["registrar"] = contador.get("registrar", 0) + 1
        escritos.append(ent["c"].resultado["v"])               # el efecto: una fila nueva
        return {"fila": len(escritos)}

    pasos = [
        Paso("a", "1", (), ("x",), paso("a", lambda p, e: {"v": p["x"] * 2})),
        Paso("b", "1", (), ("y",), paso("b", lambda p, e: {"v": p["y"] + 1})),
        Paso("c", "1", ("a", "b"), (), paso("c", lambda p, e: {"v": e["a"].resultado["v"] + e["b"].resultado["v"]})),
        Paso("registrar", "1", ("c",), (), registrar, efecto=True),
    ]
    return Flujo("prueba", "1", pasos, norma, almacen=almacen, max_hilos=max_hilos)


def test_repeticion_identica_reutiliza_todo_y_no_repite_el_efecto():
    n, escritos = {}, []
    f = _flujo(n, escritos)
    r1 = f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    assert r1.artefactos["c"].resultado == {"v": 11} and escritos == [11]
    r2 = f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    assert r2.reutilizados == ["a", "b", "c", "registrar"] and r2.ejecutados == []
    assert n == {"a": 1, "b": 1, "c": 1, "registrar": 1} and escritos == [11]
    assert r2.artefactos["registrar"].resultado == r1.artefactos["registrar"].resultado


def test_otra_llave_con_las_mismas_entradas_es_otro_efecto_pero_reutiliza_el_calculo():
    n, escritos = {}, []
    f = _flujo(n, escritos)
    f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    r = f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-2")
    assert r.reutilizados == ["a", "b", "c"] and r.ejecutados == ["registrar"]
    assert escritos == [11, 11] and n["c"] == 1


def test_misma_llave_con_otras_entradas_es_un_conflicto_y_no_escribe():
    n, escritos = {}, []
    f = _flujo(n, escritos)
    f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    with pytest.raises(ConflictoIdempotencia):
        f.ejecutar({"x": 9, "y": 4}, idempotency_key="pedido-1")
    assert escritos == [11]


def test_con_efectos_exige_llave():
    with pytest.raises(ValueError, match="idempotency_key"):
        _flujo({}, []).ejecutar({"x": 1, "y": 1})


def test_cambio_de_norma_o_de_version_cambia_la_llave():
    alm = AlmacenAcotado()
    n1, n2 = {}, {}
    a1 = _flujo(n1, [], almacen=alm).ejecutar({"x": 3, "y": 4}, idempotency_key="k").artefactos["c"]
    a2 = _flujo(n2, [], almacen=alm, norma="NSR-10 v2").ejecutar({"x": 3, "y": 4}, idempotency_key="k").artefactos["c"]
    assert a1.id != a2.id and n2["c"] == 1                  # mismo almacén, otra norma: se recalcula


def test_fallo_no_deja_el_flujo_a_medias_y_el_reintento_sigue_desde_lo_valido():
    n, escritos = {}, []
    alm = AlmacenAcotado()
    f = _flujo(n, escritos, falla_en="c", almacen=alm)
    with pytest.raises(RuntimeError, match="falla en c"):
        f.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    assert escritos == [] and f.ultima_completa == {}       # el efecto no corrió y no se confirmó nada
    f2 = _flujo(n, escritos, almacen=alm)                   # reintento (el fallo se corrigió)
    r = f2.ejecutar({"x": 3, "y": 4}, idempotency_key="pedido-1")
    assert r.reutilizados == ["a", "b"] and r.ejecutados == ["c", "registrar"]
    assert n["a"] == 1 and n["b"] == 1 and escritos == [11]
    assert set(f2.ultima_completa) == {"a", "b", "c", "registrar"}


def test_paso_puro_no_puede_depender_de_un_efecto():
    pasos = [Paso("e", "1", (), (), lambda p, e: {}, efecto=True), Paso("p", "1", ("e",), (), lambda p, e: {})]
    with pytest.raises(ValueError, match="no puede depender del efecto"):
        Flujo("f", "1", pasos, "n")


def test_falta_un_parametro_no_se_asume_por_defecto():
    with pytest.raises(ValueError, match="Falta el parámetro 'y'"):
        _flujo({}, []).ejecutar({"x": 1}, idempotency_key="k")


def test_pasos_independientes_corren_en_paralelo():
    en_curso, maximo, lock = [0], [0], threading.Lock()

    def lento(p, e):
        with lock:
            en_curso[0] += 1
            maximo[0] = max(maximo[0], en_curso[0])
        time.sleep(0.05)                                    # E/S simulada
        with lock:
            en_curso[0] -= 1
        return {"ok": True}

    pasos = [Paso(f"r{i}", "1", (), (), lento) for i in range(4)]
    t0 = time.perf_counter()
    Flujo("paralelo", "1", pasos, "n", max_hilos=4).ejecutar({})
    assert maximo[0] == 4 and time.perf_counter() - t0 < 0.15
    maximo[0] = 0
    Flujo("serie", "1", pasos, "n", max_hilos=1).ejecutar({})
    assert maximo[0] == 1


def test_almacen_acotado_expulsa_el_menos_usado_y_verifica_el_hash():
    alm = AlmacenAcotado(max_artefactos=2)

    def art(i, res=None):
        res = res if res is not None else {"i": i}
        return Artefacto(f"id{i}", "n", "1", "n", "h", hash_canonico({"i": i}), (), res)

    alm.guardar(art(1))
    alm.guardar(art(2))
    assert alm.obtener("id1") is not None                   # id1 pasa a ser el más reciente
    alm.guardar(art(3))
    assert alm.obtener("id2") is None and alm.obtener("id1") is not None and len(alm) == 2
    alm.guardar(art(4, res={"i": "alterado"}))
    with pytest.raises(ValueError, match="alterado"):
        alm.obtener("id4")


def test_huella_cambia_con_el_contenido_no_con_los_finales_de_linea(tmp_path):
    from dag_proyecto.flujo import huella_de_archivos
    (tmp_path / "m").mkdir()
    (tmp_path / "m" / "a.py").write_bytes(b"x = 1\n")
    (tmp_path / "m" / "tests").mkdir()
    (tmp_path / "m" / "tests" / "t.py").write_bytes(b"assert 1\n")
    h1 = huella_de_archivos(tmp_path / "m")
    (tmp_path / "m" / "a.py").write_bytes(b"x = 1\r\n")
    (tmp_path / "m" / "tests" / "t.py").write_bytes(b"assert 2\n")          # las pruebas no son el motor
    assert huella_de_archivos(tmp_path / "m") == h1
    (tmp_path / "m" / "a.py").write_bytes(b"x = 2\n")
    assert huella_de_archivos(tmp_path / "m") != h1
    with pytest.raises(FileNotFoundError):
        huella_de_archivos(tmp_path / "no_existe")
