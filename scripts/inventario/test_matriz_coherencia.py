import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matriz_coherencia as mc  # noqa: E402

VOCAB = {
    "a": {"unidad": "kPa", "dominio": "positivo"},
    "b": {"unidad": "mm", "dominio": "no_negativo", "max": 10},
    "c": {"unidad": "-", "dominio": "real"},
    "d": {"unidad": "-", "dominio": "categoria"},
    "e": {"unidad": "-", "dominio": "compuesto"},
}


def _nodo(i, entradas=(), salidas=(), estado="implementado", tipo="motor", decl="completa", **extra):
    def lista(xs):
        return [{"magnitud": m, "acceso": acc, "evidencia": "x.py"} for m, acc in xs]
    return {"id": i, "tipo": tipo, "estado": estado, "declaracion": decl, "entradas": lista(entradas), "salidas": lista(salidas), **extra}


# ------------------------------------------------------------------ evidencia y nodos

def test_evidencia_exige_archivo_y_texto(tmp_path):
    (tmp_path / "f.py").write_text("def hola(): pass", encoding="utf-8")
    assert mc.validar_evidencia("f.py::def hola", tmp_path) is None
    assert mc.validar_evidencia("f.py", tmp_path) is None
    assert "no existe" in mc.validar_evidencia("g.py", tmp_path)
    assert "no aparece" in mc.validar_evidencia("f.py::def adios", tmp_path)


def test_nodo_valido_pasa(tmp_path):
    (tmp_path / "x.py").write_text("", encoding="utf-8")
    n = _nodo("m", entradas=[("a", "endpoint")], salidas=[("c", "paquete")])
    assert mc.validar_nodo(n, VOCAB, tmp_path) == []


def test_nodo_futuro_con_magnitud_desconocida_o_evidencia_rota(tmp_path):
    n = _nodo("m", entradas=[("zzz", "endpoint")], salidas=[("a", "magia")])
    p = " | ".join(mc.validar_nodo(n, VOCAB, tmp_path))
    assert "fuera del vocabulario" in p and "acceso" in p and "evidencia inválida" in p


def test_pendiente_no_puede_traer_conexiones_ni_bloqueado_sin_motivo(tmp_path):
    assert any("pendiente" in x for x in mc.validar_nodo(_nodo("m", decl="pendiente", salidas=[("a", "endpoint")]), VOCAB, tmp_path))
    assert any("bloqueo" in x for x in mc.validar_nodo(_nodo("m", estado="bloqueado", decl="pendiente"), VOCAB, tmp_path))


def test_vocabulario_exige_unidad_y_dominio():
    p = mc.validar_vocabulario({"x": {"dominio": "positivo"}, "y": {"unidad": "m", "dominio": "raro"}})
    assert any("unidad" in x for x in p) and any("dominio" in x for x in p)


# ------------------------------------------------------------------ grafo

def test_arista_toma_la_via_mas_debil_y_excluye_pendientes():
    a = _nodo("A", salidas=[("a", "endpoint"), ("c", "paquete")])
    b = _nodo("B", entradas=[("a", "adaptador"), ("c", "paquete")])
    pend = _nodo("P", decl="pendiente")
    es = mc.aristas([a, b, pend])
    assert len(es) == 1 and es[0]["via"] == "adaptador" and es[0]["magnitudes"] == ["a", "c"]
    assert mc.aristas([a, a | {"id": "A"}]) == []                   # un nodo no se conecta consigo mismo


def test_caminos_son_simples_y_cuentan_ciclos_una_sola_vez():
    a = _nodo("A", entradas=[("c", "endpoint")], salidas=[("a", "endpoint")])
    b = _nodo("B", entradas=[("a", "endpoint")], salidas=[("c", "endpoint")])
    es = mc.aristas([a, b])
    assert len(mc.caminos(es, 2)) == 2                                  # A->B y B->A
    assert mc.caminos(es, 3) == []                                      # no se puede pasar dos veces por el mismo nodo


def test_futuros_se_cuentan_aparte():
    a = _nodo("A", salidas=[("a", "endpoint")])
    b = _nodo("B", entradas=[("a", "endpoint")], salidas=[("c", "endpoint")])
    f = _nodo("F", entradas=[("c", "endpoint")], estado="planificado")
    r = mc.resumen({"nodos": [a, b, f]})
    assert r["conteos"][2] == {"implementados": 1, "con_futuros": 1}
    assert r["conteos"][3] == {"implementados": 0, "con_futuros": 1}


def test_huecos_de_magnitudes():
    a = _nodo("A", entradas=[("a", "endpoint")], salidas=[("c", "endpoint")])
    r = mc.resumen({"nodos": [a]})
    assert r["sin_productor"] == ["a"] and r["sin_consumidor"] == ["c"]


# ------------------------------------------------------------------ valores futuros

@pytest.mark.parametrize("mag,valor", [("a", 5), ("a", 0.1), ("b", 0), ("b", 10), ("c", -3.5), ("d", "DES"), ("e", {"k": 1}), ("e", [1])])
def test_valores_validos(mag, valor):
    mc.validar_valor(VOCAB, mag, valor)


@pytest.mark.parametrize("mag,valor", [("a", 0), ("a", -1), ("b", -0.1), ("b", 10.5), ("c", float("nan")), ("c", float("inf")),
                                       ("a", True), ("a", "5"), ("d", ""), ("d", 3), ("e", {}), ("e", 3)])
def test_valores_invalidos(mag, valor):
    with pytest.raises(ValueError):
        mc.validar_valor(VOCAB, mag, valor)


def test_magnitud_desconocida_se_rechaza():
    with pytest.raises(ValueError, match="fuera del vocabulario"):
        mc.validar_valor(VOCAB, "nueva", 1.0)


# ------------------------------------------------------------------ repositorio real

@pytest.fixture(scope="module")
def datos():
    return mc._cargar()


def test_las_declaraciones_reales_son_validas(datos):
    assert mc.validar_global(datos) == []


def test_el_documento_esta_al_dia(datos):
    assert mc.SALIDA.read_text(encoding="utf-8") == mc.renderizar(datos)


def test_un_paquete_nuevo_sin_declarar_hace_fallar(datos, monkeypatch):
    actuales = mc.paquetes_de_calculo()
    monkeypatch.setattr(mc, "paquetes_de_calculo", lambda: actuales | {"motor-nuevo"})
    assert any("motor-nuevo" in p for p in mc.validar_global(datos))


def test_cadena_probada_rota_o_con_futuro_hace_fallar(datos):
    d = copy.deepcopy(datos)
    d["cadenas_probadas"] = [{"nodos": ["motor-geotecnia", "motor-licuacion"], "evidencia": "scripts/inventario/matriz_coherencia.py"},
                             {"nodos": ["motor-analisis", "futuro-columna-circular"], "evidencia": "scripts/inventario/matriz_coherencia.py"},
                             {"nodos": ["motor-analisis", "motor-concreto"], "evidencia": "no/existe.py"}]
    p = " | ".join(mc.validar_global(d))
    assert "no hay conexión declarada motor-geotecnia -> motor-licuacion" in p
    assert "no está implementado" in p and "no existe el archivo no/existe.py" in p


def test_un_motor_con_contrato_no_puede_quedar_pendiente(datos):
    d = copy.deepcopy(datos)
    for n in d["nodos"]:
        if n["id"] == "motor-redes":
            n.update(declaracion="pendiente", entradas=[], salidas=[])
    assert any("motor-redes" in p and "pendiente" in p for p in mc.validar_global(d))


def test_endpoints_declarados_deben_coincidir_con_el_router(datos):
    d = copy.deepcopy(datos)
    next(n for n in d["nodos"] if n["id"] == "motor-redes")["endpoints"] = ["POST /redes/permanente"]
    assert any("motor-redes" in p and "endpoints" in p for p in mc.validar_global(d))


def test_evidencia_vencida_hace_fallar(datos):
    d = copy.deepcopy(datos)
    next(n for n in d["nodos"] if n["id"] == "motor-geotecnia")["salidas"][0]["evidencia"] = "packages/motor-geotecnia/src/contrato_api.py::campo_que_ya_no_existe"
    assert any("campo_que_ya_no_existe" in p for p in mc.validar_global(d))


# ------------------------------------------------------------------ CLI

def test_cli_validar_valores(tmp_path, capsys):
    bueno, malo = tmp_path / "b.json", tmp_path / "m.json"
    bueno.write_text(json.dumps({"q_adm_kpa": [150, 200.5], "aceleracion_pico_g": 0.3}), encoding="utf-8")
    malo.write_text(json.dumps({"q_adm_kpa": [150, -2], "aceleracion_pico_g": 3.0}), encoding="utf-8")
    assert mc.main(["--validar-valores", str(bueno)]) == 0
    assert mc.main(["--validar-valores", str(malo)]) == 1


def test_cli_validar_declaracion(tmp_path):
    nuevo = _nodo("motor-pilotes-real", entradas=[("perfil_spt", "endpoint")], salidas=[("capacidad_pilote_kn", "endpoint")])
    for item in nuevo["entradas"] + nuevo["salidas"]:
        item["evidencia"] = "docs/coherencia_motores.json"
    f = tmp_path / "n.json"
    f.write_text(json.dumps(nuevo), encoding="utf-8")
    assert mc.main(["--validar-declaracion", str(f)]) == 0
    nuevo["salidas"][0]["magnitud"] = "magnitud_inventada"
    f.write_text(json.dumps(nuevo), encoding="utf-8")
    assert mc.main(["--validar-declaracion", str(f)]) == 1
