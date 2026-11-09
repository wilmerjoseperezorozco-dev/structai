"""Núcleo del DAG de proyecto (#150): hashes canónicos, validación del grafo, caché, invalidación y persistencia."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "contrato-motor"))

from contrato_motor import ResultadoMotor
from dag_proyecto import AlmacenJSON, Nodo, Orquestador, hash_canonico


def _res(v):
    return ResultadoMotor(valor=v, unidad_si="u", ecuacion="e", referencia_normativa="n", supuestos=["s"], en_borde_dominio=False)


def _cadena(contador):
    """a(p.x) → b(a, p.y) → c(b)."""
    def fa(p, ent):
        contador["a"] += 1
        return _res({"v": p["x"] * 2})

    def fb(p, ent):
        contador["b"] += 1
        return _res({"v": ent["a"].resultado["valor"]["v"] + p["y"]})

    def fc(p, ent):
        contador["c"] += 1
        return _res({"v": ent["b"].resultado["valor"]["v"] * 10})

    return Orquestador([Nodo("a", "1.0", (), ("x",), fa), Nodo("b", "1.0", ("a",), ("y",), fb), Nodo("c", "1.0", ("b",), (), fc)],
                       norma_version="NSR-10 (2010)")


def test_hash_canonico_no_depende_del_orden_de_las_claves():
    assert hash_canonico({"a": 1, "b": [1, 2]}) == hash_canonico({"b": [1, 2], "a": 1})
    assert hash_canonico({"a": 1}) != hash_canonico({"a": 2})


def test_ejecucion_en_orden_topologico_y_resultado():
    cnt = dict(a=0, b=0, c=0)
    arts = _cadena(cnt).ejecutar({"x": 3, "y": 4})
    assert arts["c"].resultado["valor"]["v"] == 100
    assert arts["b"].entradas == (arts["a"].id,) and arts["c"].entradas == (arts["b"].id,)


def test_segunda_ejecucion_identica_usa_cache_y_devuelve_los_mismos_hashes():
    cnt = dict(a=0, b=0, c=0)
    o = _cadena(cnt)
    a1 = o.ejecutar({"x": 3, "y": 4})
    a2 = o.ejecutar({"x": 3, "y": 4})
    assert cnt == dict(a=1, b=1, c=1)
    assert {k: v.id for k, v in a1.items()} == {k: v.id for k, v in a2.items()}
    assert {k: v.hash_contenido for k, v in a1.items()} == {k: v.hash_contenido for k, v in a2.items()}


def test_cambio_aguas_abajo_solo_recalcula_los_dependientes():
    cnt = dict(a=0, b=0, c=0)
    o = _cadena(cnt)
    o.ejecutar({"x": 3, "y": 4})
    o.ejecutar({"x": 3, "y": 5})          # y solo entra a b
    assert cnt == dict(a=1, b=2, c=2)


def test_cambio_aguas_arriba_recalcula_toda_la_cadena():
    cnt = dict(a=0, b=0, c=0)
    o = _cadena(cnt)
    o.ejecutar({"x": 3, "y": 4})
    o.ejecutar({"x": 4, "y": 4})
    assert cnt == dict(a=2, b=2, c=2)


def test_artefacto_obsoleto_queda_marcado_al_cambiar_el_proyecto():
    o = _cadena(dict(a=0, b=0, c=0))
    viejos = o.ejecutar({"x": 3, "y": 4})
    o.ejecutar({"x": 4, "y": 4})
    assert o.almacen.obtener(viejos["a"].id).estado == "obsoleto"


def test_parametro_faltante_lanza_valueerror():
    with pytest.raises(ValueError, match="x"):
        _cadena(dict(a=0, b=0, c=0)).ejecutar({"y": 4})


def test_ciclo_lanza_valueerror():
    n = lambda p, e: _res(1)  # noqa: E731
    with pytest.raises(ValueError, match="ciclo"):
        Orquestador([Nodo("a", "1", ("b",), (), n), Nodo("b", "1", ("a",), (), n)], norma_version="x")


def test_entrada_sin_productor_lanza_valueerror():
    with pytest.raises(ValueError, match="productor"):
        Orquestador([Nodo("a", "1", ("fantasma",), (), lambda p, e: _res(1))], norma_version="x")


def test_nombres_de_nodo_duplicados_lanzan_valueerror():
    n = lambda p, e: _res(1)  # noqa: E731
    with pytest.raises(ValueError, match="duplicado"):
        Orquestador([Nodo("a", "1", (), (), n), Nodo("a", "2", (), (), n)], norma_version="x")


def test_cambiar_la_version_del_nodo_o_de_la_norma_cambia_el_id():
    n = lambda p, e: _res(1)  # noqa: E731
    i1 = Orquestador([Nodo("a", "1.0", (), (), n)], norma_version="N1").ejecutar({})["a"].id
    i2 = Orquestador([Nodo("a", "1.1", (), (), n)], norma_version="N1").ejecutar({})["a"].id
    i3 = Orquestador([Nodo("a", "1.0", (), (), n)], norma_version="N2").ejecutar({})["a"].id
    assert len({i1, i2, i3}) == 3


def test_persistencia_json_reproduce_los_artefactos(tmp_path):
    cnt = dict(a=0, b=0, c=0)
    o1 = _cadena(cnt)
    o1.almacen = AlmacenJSON(tmp_path)
    a1 = o1.ejecutar({"x": 3, "y": 4})
    cnt2 = dict(a=0, b=0, c=0)
    o2 = _cadena(cnt2)
    o2.almacen = AlmacenJSON(tmp_path)
    a2 = o2.ejecutar({"x": 3, "y": 4})
    assert cnt2 == dict(a=0, b=0, c=0)                      # todo salió del almacén
    assert {k: v.id for k, v in a1.items()} == {k: v.id for k, v in a2.items()}


def test_un_artefacto_alterado_en_disco_se_detecta(tmp_path):
    o = _cadena(dict(a=0, b=0, c=0))
    o.almacen = AlmacenJSON(tmp_path)
    arts = o.ejecutar({"x": 3, "y": 4})
    ruta = next(tmp_path.glob(f"{arts['a'].id}*.json"))
    ruta.write_text(ruta.read_text(encoding="utf-8").replace('"v":6', '"v":7').replace('"v": 6', '"v": 7'), encoding="utf-8")
    o2 = _cadena(dict(a=0, b=0, c=0))
    o2.almacen = AlmacenJSON(tmp_path)
    with pytest.raises(ValueError, match="hash"):
        o2.ejecutar({"x": 3, "y": 4})


def test_el_aviso_de_responsabilidad_viaja_en_cada_artefacto():
    arts = _cadena(dict(a=0, b=0, c=0)).ejecutar({"x": 3, "y": 4})
    assert all(a.resultado["aviso_responsabilidad_profesional"] for a in arts.values())
