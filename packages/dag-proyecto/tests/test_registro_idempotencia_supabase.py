"""RegistroEfectosSupabase con un cliente simulado que respeta la llave primaria (23505), como Postgres."""
import datetime as dt
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "contrato-motor"))

from dag_proyecto import Artefacto, hash_canonico
from dag_proyecto.flujo import ConflictoIdempotencia, Flujo, Paso
from dag_proyecto.supabase_almacen import RegistroEfectosSupabase


class LlaveDuplicada(Exception):
    code = "23505"


class _Q:
    def __init__(self, db, op, payload=None):
        self.db, self.op, self.payload, self.filtros = db, op, payload, []

    def select(self, *_a):
        return self

    def eq(self, c, v):
        self.filtros.append((c, v))
        return self

    def limit(self, _n):
        return self

    def execute(self):
        self.db.ops.append(self.op)
        if self.op == "insert":
            if self.payload["llave"] in self.db.filas:
                raise LlaveDuplicada("duplicate key value violates unique constraint")
            self.db.filas[self.payload["llave"]] = dict(self.payload)
            return type("R", (), {"data": [self.payload]})()
        fs = [f for f in self.db.filas.values() if all(f.get(c) == v for c, v in self.filtros)]
        if self.op == "delete":
            for f in fs:
                del self.db.filas[f["llave"]]
            return type("R", (), {"data": []})()
        return type("R", (), {"data": [dict(f) for f in fs]})()


class FakeSB:
    def __init__(self):
        self.filas, self.ops = {}, []

    def table(self, nombre):
        assert nombre == "idempotencia_efectos"
        db = self

        class T:
            def select(self, *a):
                return _Q(db, "select")

            def insert(self, fila):
                return _Q(db, "insert", fila)

            def delete(self):
                return _Q(db, "delete")
        return T()


def _flujo(registro, escritos):
    def registrar(p, ent):
        escritos.append(p["monto"])
        return {"fila": len(escritos), "monto": 1.10}            # 1.10: jsonb lo devolvería distinto; se guarda como texto
    return Flujo("lote-apu", "1", [Paso("registrar", "1", (), ("monto",), registrar, efecto=True)], "n",
                 registro_efectos=registro)


def test_repeticion_en_otra_instancia_no_repite_el_efecto():
    db, escritos = FakeSB(), []
    r1 = _flujo(RegistroEfectosSupabase(db), escritos).ejecutar({"monto": 5}, idempotency_key="pedido-1")
    r2 = _flujo(RegistroEfectosSupabase(db), escritos).ejecutar({"monto": 5}, idempotency_key="pedido-1")   # otra instancia
    assert escritos == [5] and r2.reutilizados == ["registrar"]
    assert r2.artefactos["registrar"].resultado == r1.artefactos["registrar"].resultado == {"fila": 1, "monto": 1.10}
    fila = next(iter(db.filas.values()))
    assert fila["flujo"] == "lote-apu" and fila["paso"] == "registrar"


def test_misma_llave_otras_entradas_es_conflicto():
    db, escritos = FakeSB(), []
    _flujo(RegistroEfectosSupabase(db), escritos).ejecutar({"monto": 5}, idempotency_key="k")
    with pytest.raises(ConflictoIdempotencia):
        _flujo(RegistroEfectosSupabase(db), escritos).ejecutar({"monto": 9}, idempotency_key="k")
    assert escritos == [5]


def test_carrera_entre_instancias_gana_la_primera():
    db = FakeSB()
    a = Artefacto("id-a", "registrar", "1", "n", "h", hash_canonico({"v": "a"}), (), {"v": "a"})
    b = Artefacto("id-b", "registrar", "1", "n", "h", hash_canonico({"v": "b"}), (), {"v": "b"})
    assert RegistroEfectosSupabase(db).registrar("L", a, flujo="f").resultado == {"v": "a"}
    assert RegistroEfectosSupabase(db).registrar("L", b, flujo="f").resultado == {"v": "a"}     # chocó con la llave


def test_fila_vencida_se_reemplaza_y_resultado_alterado_falla():
    db = FakeSB()
    t0 = dt.datetime(2026, 11, 16, tzinfo=dt.timezone.utc)
    viejo = RegistroEfectosSupabase(db, vigencia_dias=7, ahora=lambda: t0)
    a = Artefacto("id-a", "registrar", "1", "n", "h", hash_canonico({"v": 1}), (), {"v": 1})
    viejo.registrar("L", a, flujo="f")
    despues = RegistroEfectosSupabase(db, ahora=lambda: t0 + dt.timedelta(days=8))
    assert despues.obtener("L") is None
    b = Artefacto("id-b", "registrar", "1", "n", "h", hash_canonico({"v": 2}), (), {"v": 2})
    assert despues.registrar("L", b, flujo="f").resultado == {"v": 2}
    db.filas["L"]["artefacto"]["resultado_texto"] = '{"v":3}'
    with pytest.raises(ValueError, match="alterado"):
        despues.obtener("L")


def test_error_distinto_de_llave_duplicada_se_propaga():
    class Roto(FakeSB):
        def table(self, nombre):
            t = super().table(nombre)

            class T2:
                def select(self, *a):
                    return t.select(*a)

                def insert(self, fila):
                    raise ConnectionError("Supabase caído")
            return T2()
    a = Artefacto("id-a", "registrar", "1", "n", "h", hash_canonico({"v": 1}), (), {"v": 1})
    with pytest.raises(ConnectionError):
        RegistroEfectosSupabase(Roto()).registrar("L", a, flujo="f")
