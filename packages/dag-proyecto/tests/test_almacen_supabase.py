"""AlmacenSupabase con un cliente simulado: aislamiento por usuario, integridad por hash y fallo explícito."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "contrato-motor"))

from contrato_motor import ResultadoMotor
from dag_proyecto import Nodo, Orquestador
from dag_proyecto.supabase_almacen import AlmacenSupabase


class _Resp:
    def __init__(self, data):
        self.data = data


class _Q:
    def __init__(self, filas, op, payload=None):
        self.filas, self.op, self.payload, self.filtros = filas, op, payload, []

    def select(self, *_a, **_k):
        return self

    def eq(self, col, val):
        self.filtros.append((col, val))
        return self

    def limit(self, *_a):
        return self

    def _coinciden(self):
        return [f for f in self.filas if all(f.get(c) == v for c, v in self.filtros)]

    def execute(self):
        if self.op == "select":
            return _Resp([dict(f) for f in self._coinciden()])
        if self.op == "upsert":
            clave = (self.payload["user_id"], self.payload["id"])
            self.filas[:] = [f for f in self.filas if (f["user_id"], f["id"]) != clave] + [dict(self.payload)]
            return _Resp([self.payload])
        for f in self._coinciden():
            f.update(self.payload)
        return _Resp([])


class FakeSB:
    def __init__(self):
        self.filas = []

    def table(self, _nombre):
        outer = self

        class T:
            def select(self, *a, **k):
                return _Q(outer.filas, "select").select(*a, **k)

            def upsert(self, row, **_k):
                return _Q(outer.filas, "upsert", row)

            def update(self, row):
                return _Q(outer.filas, "update", row)
        return T()


def _res(v):
    return ResultadoMotor(valor=v, unidad_si="u", ecuacion="e", referencia_normativa="n", supuestos=["s"], en_borde_dominio=False)


def _orq(almacen, cnt):
    def fa(p, ent):
        cnt["a"] += 1
        return _res({"v": p["x"] * 2, "grande": 1e22, "chico": 1e-5})
    return Orquestador([Nodo("a", "1", (), ("x",), fa)], norma_version="N", almacen=almacen)


def test_roundtrip_conserva_el_hash_incluso_con_numeros_extremos():
    sb, cnt = FakeSB(), dict(a=0)
    a1 = _orq(AlmacenSupabase(sb, "u1"), cnt).ejecutar({"x": 3})["a"]
    a2 = _orq(AlmacenSupabase(sb, "u1"), cnt).ejecutar({"x": 3})["a"]
    assert cnt["a"] == 1 and a1.id == a2.id and a1.hash_contenido == a2.hash_contenido


def test_otro_usuario_no_reutiliza_ni_ve_artefactos_ajenos():
    sb, cnt = FakeSB(), dict(a=0)
    _orq(AlmacenSupabase(sb, "u1"), cnt).ejecutar({"x": 3})
    _orq(AlmacenSupabase(sb, "u2"), cnt).ejecutar({"x": 3})
    assert cnt["a"] == 2 and {f["user_id"] for f in sb.filas} == {"u1", "u2"}


def test_fila_alterada_se_detecta_por_hash():
    sb, cnt = FakeSB(), dict(a=0)
    _orq(AlmacenSupabase(sb, "u1"), cnt).ejecutar({"x": 3})
    sb.filas[0]["resultado_texto"] = sb.filas[0]["resultado_texto"].replace("\"v\":6", "\"v\":7")
    with pytest.raises(ValueError, match="hash"):
        _orq(AlmacenSupabase(sb, "u1"), cnt).ejecutar({"x": 3})


def test_obsoleto_se_persiste():
    sb, cnt = FakeSB(), dict(a=0)
    o = _orq(AlmacenSupabase(sb, "u1"), cnt)
    viejo = o.ejecutar({"x": 3})["a"]
    o.ejecutar({"x": 4})
    assert next(f for f in sb.filas if f["id"] == viejo.id)["estado"] == "obsoleto"


def test_usuario_vacio_lanza_valueerror():
    with pytest.raises(ValueError, match="usuario"):
        AlmacenSupabase(FakeSB(), "")
