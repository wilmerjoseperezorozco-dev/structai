"""Pruebas sin red de ingest_motor_chunks.py: el cliente de Supabase y el
modelo de embeddings son dobles en memoria. Ninguna prueba toca Supabase.

Correr: python -m pytest scripts/ingesta/motores/test_ingest_motor_chunks.py
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ingest_motor_chunks as imc  # noqa: E402


class _Resp:
    def __init__(self, data):
        self.data = data


class _Consulta:
    """Imita la cadena de PostgREST (select/eq/order/range/insert/delete/in_)."""

    def __init__(self, cliente, tabla):
        self.c, self.tabla = cliente, tabla
        self.op, self.filtros, self.rango, self.payload = None, [], None, None

    def select(self, _cols):
        self.op = "select"
        return self

    def insert(self, rows):
        self.op, self.payload = "insert", rows
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, col, val):
        self.filtros.append(("eq", col, val))
        return self

    def in_(self, col, vals):
        self.filtros.append(("in", col, list(vals)))
        return self

    def order(self, _col):
        return self

    def range(self, ini, fin):
        self.rango = (ini, fin)
        return self

    def _coincide(self, fila):
        for tipo, col, val in self.filtros:
            if tipo == "eq" and fila[col] != val:
                return False
            if tipo == "in" and fila[col] not in val:
                return False
        return True

    def execute(self):
        self.c.llamadas.append((self.op, self.tabla, list(self.filtros)))
        if self.op == "select":
            filas = [f for f in self.c.filas if self._coincide(f)]
            ini, fin = self.rango or (0, len(filas))
            return _Resp([{"id": f["id"], "seccion": f["seccion"]} for f in filas[ini:fin + 1]])
        if self.op == "insert":
            for r in self.payload:
                self.c.siguiente_id += 1
                self.c.filas.append({**r, "id": self.c.siguiente_id})
            return _Resp(self.payload)
        if self.op == "delete":
            if not any(t == "in" and col == "id" for t, col, _ in self.filtros):
                raise AssertionError(f"borrado sin lista de ids: {self.filtros}")
            borradas = [f for f in self.c.filas if self._coincide(f)]
            self.c.filas = [f for f in self.c.filas if not self._coincide(f)]
            return _Resp(borradas)
        raise AssertionError(self.op)


class ClienteFalso:
    def __init__(self, filas):
        self.filas = [dict(f) for f in filas]
        self.siguiente_id = max((f["id"] for f in self.filas), default=0)
        self.llamadas = []

    def table(self, nombre):
        return _Consulta(self, nombre)

    def escrituras(self):
        return [ll for ll in self.llamadas if ll[0] in ("insert", "delete")]


class ModeloFalso:
    def encode(self, textos, normalize_embeddings=True):
        class _Arr(list):
            def tolist(self):
                return list(self)
        return _Arr([[0.0] * 384 for _ in textos])


def _tabla_inicial():
    """'vias' con 2 chunks de este script + 1.500 de otros scripts (fuerza la
    paginación de 1.000), más filas de 'geopot' y de otro motor."""
    filas, i = [], 0
    for c in imc.VIAS_CHUNKS[:2]:
        i += 1
        filas.append({"id": i, "motor": "vias", "seccion": c["seccion"]})
    for k in range(1500):
        i += 1
        filas.append({"id": i, "motor": "vias", "seccion": f"INV E-{k:03d}-13 — Sección {k}"})
    i += 1
    filas.append({"id": i, "motor": "geopot", "seccion": imc.GEOPOT_CHUNKS[0]["seccion"]})
    i += 1
    filas.append({"id": i, "motor": "aquai", "seccion": "RAS B.2.1 — Dotación neta"})
    return filas


def test_sin_aplicar_solo_lee_y_reporta_conteos(capsys):
    sb = ClienteFalso(_tabla_inicial())
    planes = imc.main(["--motor", "vias"], sb=sb, model=ModeloFalso())

    assert sb.escrituras() == []
    plan = planes[0][0]
    assert plan["filas_motor"] == 1502
    assert sorted(plan["ids_a_borrar"]) == [1, 2]
    assert plan["conservadas"] == 1500
    assert plan["a_insertar"] == len(imc.VIAS_CHUNKS)
    salida = capsys.readouterr().out
    assert "se borrarían 2" in salida and "se conservan 1500" in salida
    assert "Simulación" in salida


def test_aplicar_conserva_los_chunks_de_otros_scripts():
    sb = ClienteFalso(_tabla_inicial())
    imc.main(["--motor", "vias", "--aplicar"], sb=sb, model=ModeloFalso())

    vias = [f for f in sb.filas if f["motor"] == "vias"]
    ajenas = [f for f in vias if f["seccion"].startswith("INV E-")]
    assert len(ajenas) == 1500
    assert {f["id"] for f in vias if f["id"] in (1, 2)} == set()
    propias = [f for f in vias if not f["seccion"].startswith("INV E-")]
    assert sorted(f["seccion"] for f in propias) == sorted(c["seccion"] for c in imc.VIAS_CHUNKS)
    # los otros motores no se tocan
    assert any(f["motor"] == "aquai" for f in sb.filas)
    assert any(f["motor"] == "geopot" and f["id"] == 1503 for f in sb.filas)


def test_nunca_borra_por_motor_a_secas_e_inserta_antes_de_borrar():
    sb = ClienteFalso(_tabla_inicial())
    imc.main(["--aplicar"], sb=sb, model=ModeloFalso())

    ops = [op for op, _, _ in sb.escrituras()]
    for op, _, filtros in sb.escrituras():
        if op == "delete":
            assert [(t, col) for t, col, _ in filtros] == [("in", "id")]
    # por motor: insert y luego delete
    assert ops.index("insert") < ops.index("delete")


def test_secciones_repetidas_abortan_antes_de_escribir():
    sb = ClienteFalso(_tabla_inicial())
    chunk = imc.VIAS_CHUNKS[0]
    with pytest.raises(ValueError, match="repetidas"):
        imc.planificar(sb, "vias", [chunk, chunk])
    assert sb.escrituras() == []


def test_secciones_del_script_son_unicas_en_cada_motor():
    for chunks in imc.MOTORES.values():
        imc.secciones_del_script(chunks)


def test_motores_nuevos_registrados_con_secciones_unicas_y_campos_completos():
    from chunks_motores_nuevos import MOTORES_NUEVOS, VIENTO_CHUNKS
    assert {"geotecnia", "pilotes", "acero_frio", "incendios"} <= set(imc.MOTORES)
    assert "viento" not in imc.MOTORES                       # se registra cuando el PR #331 esté en master
    for motor, chunks in {**MOTORES_NUEVOS, "viento": VIENTO_CHUNKS}.items():
        imc.secciones_del_script(chunks)                     # falla si hay secciones repetidas
        assert any("alcance" in c["seccion"] for c in chunks), motor
        for c in chunks:
            assert set(c) == {"seccion", "titulo", "norma_ref", "contenido"}, (motor, c["seccion"])
            assert all(c[k].strip() for k in c), (motor, c["seccion"])
            assert len(c["contenido"]) < 2000, (motor, c["seccion"])


def test_raiz_del_repo_apunta_al_env_de_la_api():
    assert (imc.ROOT / "apps" / "api").is_dir()
