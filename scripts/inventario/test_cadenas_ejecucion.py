import ast
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import cadenas_ejecucion as ce


def _llamadas(codigo: str):
    v = ce._Llamadas()
    for n in ast.parse(codigo).body[0].body:
        v.visit(n)
    return [t for t, _, _ in v.salida]


def test_cadena_fluida_de_supabase_es_un_solo_paso():
    ll = _llamadas("def f():\n    sb.table('x').select('*').eq('a', 1).execute()\n")
    assert ll == ["sb.table().select().eq().execute"]


def test_sumideros_no_confunden_dict_update_ni_str_encode():
    assert ce.sumidero("sb.table().update().eq().execute") >= {"efecto", "bd"}
    assert "efecto" not in ce.sumidero("resultado.update")
    assert "efecto" not in ce.sumidero("sys.path.insert")
    assert "embeddings" not in ce.sumidero("texto.encode")
    assert "embeddings" not in ce.sumidero("tokenizer.encode")
    assert "embeddings" in ce.sumidero("model.encode")
    assert "llm" in ce.sumidero("groq_client.chat.completions.create")


def test_run_in_threadpool_cuenta_la_funcion_pasada_como_argumento():
    ll = _llamadas("async def f():\n    await run_in_threadpool(_detect_onnx, b, s)\n")
    assert "_detect_onnx" in ll


def test_pasos_dentro_de_except_no_cuentan():
    v = ce._Llamadas()
    for n in ast.parse("def f():\n    try:\n        a()\n    except Exception:\n        b()\n").body[0].body:
        v.visit(n)
    assert [(t, e) for t, _, e in v.salida] == [("a", False), ("b", True)]


def test_etiquetas():
    paso = lambda t, norma=False: {"tipo": t, "tipos": [t], "norma": norma}
    assert ce.etiquetas([paso("bd"), paso("llm"), paso("efecto")])[:2] == ["con_efectos", "con_LLM"]
    assert ce.etiquetas([paso("motor", True)] * 4) == ["dependiente_de_norma"]
    assert ce.etiquetas([paso("cpu")]) == ["pura"]
    assert "dependiente_de_datos" in ce.etiquetas([paso("bd")])


def test_scripts_puntuales():
    assert ce.puntual("scripts/ingesta/nsr10/_fix_titulo_b.py")
    assert ce.puntual("scripts/evaluacion/lote_nuevas_preguntas_2026-09-29.py")
    assert not ce.puntual("scripts/ingesta/ccp14/ingest_ccp14.py")


def test_inventario_real_encuentra_las_cadenas_clave():
    inv = ce.inventario()
    por = {c["entrada"]: c for c in inv["cadenas"]}
    assert por["POST /consultar"]["candidata"] and "con_LLM" in por["POST /consultar"]["etiquetas"]
    assert por["POST /orquestador/portico-integral"]["pasos"] >= ce.UMBRAL
    assert "con_LLM" not in por["POST /orquestador/portico-integral"]["etiquetas"]
    # Las cadenas futuras solo usan nodos declarados y siempre pasan por al menos un motor futuro
    assert inv["futuras"] and all(f["futuros"] and f["pasos"] >= ce.UMBRAL for f in inv["futuras"])
