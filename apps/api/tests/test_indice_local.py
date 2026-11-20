"""Índice RAG local (packages/construdata/indice_local.py) y su respaldo a la RPC de Supabase (2026-11-16).

Sin red ni Supabase. Los valores esperados de to_tsvector('spanish', ...) y de ts_rank salieron de Postgres 17
(proyecto de producción, consulta de solo lectura sobre textos sintéticos), así que estas pruebas fijan la paridad del
analizador local con Postgres: si alguien cambia una regla del tokenizador o la versión de snowballstemmer, se rompen.
La paridad sobre el corpus real se mide aparte con scripts/rag/verificar_paridad_tsvector.py y paridad_top10.py.
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))
for k, v in {"SUPABASE_URL": "http://localhost:54321", "SUPABASE_SERVICE_KEY": "clave-de-prueba-local",
             "SUPABASE_JWT_SECRET": "secreto-de-prueba-local", "GROQ_API_KEY": "clave-de-prueba-local"}.items():
    os.environ.setdefault(k, v)

import indice_local as il  # noqa: E402


def _tsvector_texto(texto: str) -> str:
    """Representación de to_tsvector como la imprime Postgres: lexemas en orden de bytes con sus posiciones."""
    pos: dict[str, list[int]] = {}
    p = 0
    for grupo in il.grupos_lexemas(texto):
        for lx in grupo:
            p += 1
            if lx is not None:
                pos.setdefault(lx, []).append(p)
    return " ".join(f"'{lx}':{','.join(map(str, pos[lx]))}" for lx in sorted(pos, key=lambda x: x.encode("utf-8")))


# (texto, salida de to_tsvector('spanish', texto)::text en Postgres 17)
CASOS_POSTGRES = [
    ("G-A-1 x", "'1':4 'g':2 'g-a':1 'x':5"),
    ("A-3.2.2 x", "'3.2.2':2 'x':3"),
    ("-3.2.2 x", "'3.2.2':1 'x':2"),
    ("Ver ⚠️ alerta", "'alert':2 'ver':1"),
    ("concreto.. Los", "'..':2 'concret':1"),
    ("concreto... Los", "'concret':1"),
    ("<Legislación Anterior> vigas", "'vig':1"),
    ("<Artículo derogado por el artículo 118> vigas", "'118':6 'articul':1,5 'derog':2 'vig':7"),
    ("v̄s columnas", "'column':2 'v̄s':1"),
    ("www.invias.gov.co/normas/e-100 x",
     "'/normas/e-100':3 'www.invias.gov.co':2 'www.invias.gov.co/normas/e-100':1 'x':4"),
    ("soporte@structai.co x", "'soporte@structai.co':1 'x':2"),
    ("fc = 21 MPa y 2.5e-3", "'2.5e-3':5 '21':2 'fc':1 'mpa':3"),
    ("kN/m2 y 1/2 y /2", "'/2':5 '1/2':3 'kn/m2':1"),
    ("A.2.3 Fig.3 C.21", "'a.2.3':1 'c.21':3 'fig.3':2"),
    ("NTC-5551 losa-aligerada", "'-5551':2 'aliger':5 'los':4 'losa-aliger':3 'ntc':1"),
    ("&amp; &#233; x", "'x':1"),
    ("http://x.com/a b", "'/a':3 'b':4 'x.com':2 'x.com/a':1"),
    ("+5 -10 3.5 1.2.3", "'+5':1 '-10':2 '1.2.3':4 '3.5':3"),
    # reglas añadidas al medir la paridad de motor_chunks (2026-11-16)
    ("mm/mm/ºC x", "'mm/mm':1 'x':3 'ºc':2"),
    ("mm/mm/ x", "'mm/mm':1 'x':2"),
    ("kN/m/. x", "'kn/m':1 'x':2"),
    ("a/b/c/ x", "'a/b/c':1 'x':2"),
    ("a/b/é x", "'a/b':1 'e':2 'x':3"),
    ("a/ x", "'x':2"),
    ("mm/mm/_ x", "'mm/mm/_':1 'x':2"),
    ("Figura 9.8.3.6.3-1.. Los", "'-1':3 '..':4 '9.8.3.6.3':2 'figur':1"),
    ("(\\docs\\LEY\\1993\\L0080_93.pdf)de la", "'1993':3 'docs':1 'l0080_93.pdf':4 'ley':2"),
    ("7 y 8.. En", "'..':4 '7':1 '8':3"),
    ("L0080_93.pdf x", "'l0080_93.pdf':1 'x':2"),
    ("a_b x", "'b':2 'x':3"),
    ("ab_1.txt x", "'ab_1.txt':1 'x':2"),
    ("x -1.. y", "'-1':2 '..':3 'x':1"),
    ("x 3-1.. y", "'-1':3 '..':4 '3':2 'x':1"),
    ("artículo10.6.1.3 x", "'artículo10.6.1.3':1 'x':2"),
    ("artículo.3 x", "'3':2 'articul':1 'x':3"),
    ("Sección.2 x", "'2':2 'seccion':1 'x':3"),
    ("año.txt x", "'año':1 'txt':2 'x':3"),
    ("é.3 x", "'3':2 'e':1 'x':3"),
    ("artículo10/2 x", "'artículo10/2':1 'x':2"),
    ("niño10.5 x", "'niño10.5':1 'x':2"),
    ("ab10.6.1.3 x", "'ab10.6.1.3':1 'x':2"),
    ("más.de x", "'x':3"),
]


@pytest.mark.parametrize("texto,esperado", CASOS_POSTGRES)
def test_tsvector_igual_a_postgres(texto, esperado):
    assert _tsvector_texto(texto) == esperado


def test_snowball_fijado_en_2_2_0():
    """snowballstemmer 3.x stemiza distinto que el Snowball de Postgres 17: con 3.x 'ocupacion' (sin tilde) da 'ocup';
    Postgres deja 'ocupacion'. Valores de to_tsvector('spanish', ...) en Postgres 17."""
    assert il._stem("ocupacion") == "ocupacion"
    assert il._stem("ocupación") == "ocup"
    assert il._stem("vigas") == "vig"


def test_consultas_or():
    # search_knowledge: to_tsquery(string_agg(lexemas de to_tsvector(q), ' | ')) -> vuelve a stemizar cada lexema
    assert il.consulta_or_colombia("viga de concreto reforzado") == [["concret"], ["reforz"], ["vig"]]
    # Perú/Ecuador: plainto_tsquery con ' & ' -> ' | ' (sin volver a stemizar), en el orden del texto
    assert il.consulta_or_pais("viga de concreto reforzado") == [["vig"], ["concret"], ["reforz"]]
    assert il.consulta_or_colombia("") == []
    assert il.consulta_or_colombia("de la y") == []          # solo palabras vacías


DOCS_RANK = [
    "La viga de concreto reforzado soporta la losa de concreto.",
    "Columna de acero estructural con viga metálica.",
    "Concreto, concreto, concreto y más concreto para la cimentación.",
    "Sin términos relevantes aquí.",
]
# (ts_rank(to_tsvector('spanish', doc), q)::float8 * 1e10)::bigint en Postgres, q = 'concret' | 'reforz' | 'vig'
RANK_POSTGRES = [658587739, 202642363, 288483929, 0]


def _fila(corpus, id_, contenido, emb, norma="NSR-10 A.2", motor=None, norma_id=None):
    return {"corpus": corpus, "id": id_, "norma": norma, "seccion": "s", "contenido": contenido, "motor": motor,
            "norma_id": norma_id, "embedding": emb}


@pytest.fixture()
def indice_rank(tmp_path):
    filas = [_fila("nsr10", f"d{i}", t, [1.0, float(i), 0.0]) for i, t in enumerate(DOCS_RANK)]
    ruta = tmp_path / "rank.npz"
    il.construir_archivo(filas, {}, ruta, {})
    return il.IndiceLocal.cargar(ruta)


def test_ts_rank_float32_igual_a_postgres(indice_rank):
    docs, res = indice_rank._puntajes_lexicos(il.consulta_or_colombia("viga de concreto reforzado"),
                                              indice_rank._filtro(il.COLOMBIA, None, None))
    obtenido = {int(d): round(float(np.float32(r)) * 1e10) for d, r in zip(docs, res)}
    assert obtenido == {i: v for i, v in enumerate(RANK_POSTGRES) if v}      # el doc 3 no cumple la consulta
    assert indice_rank._lexica(il.consulta_or_colombia("viga de concreto reforzado"),
                               indice_rank._filtro(il.COLOMBIA, None, None), 300) == [0, 2, 1]


def test_ilike_como_postgres():
    p = il._ilike("%A.%")                    # '%' || p || '%' : subcadena, % y _ siguen siendo comodines
    assert p.search("nsr-10 a.2.4")
    assert not p.search("nsr-10 b2")
    assert il._ilike("A_2").search("xa.2y")  # '_' = un carácter cualquiera
    assert il._ilike("ntc").search("NTC 673".lower())


@pytest.fixture()
def indice_rrf(tmp_path):
    """Ids que chocan entre tablas ('7' en nsr10 y en motor), como en producción: search_knowledge une por id en texto."""
    filas = [
        _fila("nsr10", "7", "viga de concreto", [1.0, 0.0, 0.0], norma="NSR-10 C.21", norma_id="nid-1"),
        _fila("nsr10", "8", "columna de acero", [0.9, 0.1, 0.0], norma="NSR-10 F.2"),
        _fila("motor", "7", "pavimento de concreto", [0.0, 1.0, 0.0], norma="INV E-100", motor="vias"),
        _fila("motor", "9", "talud", [0.0, 0.0, 1.0], norma="Res. 0330", motor="aquai"),
        _fila("peru", "E030-1", "factor de zona sísmica", [1.0, 0.0, 0.0], norma="E.030 Capítulo II"),
        _fila("ecuador", "NEC-1", "espectro elástico", [0.0, 1.0, 0.0], norma="NEC-SE-DS 3"),
    ]
    normas = {"nid-1": {"nombre_completo": "NSR-10", "estado_vigencia": "vigente", "derogada_por": None,
                        "alcance_derogacion": None}}
    ruta = tmp_path / "rrf.npz"
    il.construir_archivo(filas, normas, ruta, {})
    return il.IndiceLocal.cargar(ruta)


def test_rrf_full_join_por_id_texto(indice_rrf):
    r = indice_rrf.search_knowledge([1.0, 0.0, 0.0], "concreto", None, 10, 60)
    # semántica: nsr10/7 (1), nsr10/8 (2), motor/7 (3), motor/9 (4); léxica ('concret'): nsr10/7 y motor/7 (empatan)
    # nsr10/7 semántico se une con AMBOS '7' léxicos (FULL JOIN por texto): dos filas con 1/61 + 1/61 y 1/61 + 1/62
    puntajes = sorted((round(x.score, 12) for x in r), reverse=True)
    esperado = sorted([float(Fraction(1, 61) + Fraction(1, 61)), float(Fraction(1, 61) + Fraction(1, 62)),
                       float(Fraction(1, 62)), float(Fraction(1, 63) + Fraction(1, 61)),
                       float(Fraction(1, 63) + Fraction(1, 62)), float(Fraction(1, 64))], reverse=True)
    assert puntajes == [round(x, 12) for x in esperado]
    assert {x.chunk_id for x in r} == {"7", "8", "9"}
    # la metadata de vigencia sale de normas_registro (COALESCE(s.norma_id, l.norma_id))
    assert r[0].metadata == {"estado_vigencia": "vigente", "derogada_por": None, "alcance_derogacion": None}


def test_filtros_motor_y_norma(indice_rrf):
    solo_vias = indice_rrf.search_knowledge([0.0, 1.0, 0.0], "concreto", None, 10, 60, p_motor="vias")
    assert [x.chunk_id for x in solo_vias] == ["7"] and solo_vias[0].norma == "INV E-100"
    solo_c = indice_rrf.search_knowledge([1.0, 0.0, 0.0], "", "C.21", 10, 60)
    assert [x.norma for x in solo_c] == ["NSR-10 C.21"]
    # los corpus de Perú y Ecuador no entran en search_knowledge
    assert all(x.chunk_id not in ("E030-1", "NEC-1") for x in indice_rrf.search_knowledge([1.0, 0.0, 0.0], "", None, 10))


def test_search_pais(indice_rrf):
    peru = indice_rrf.search_pais("peru", [1.0, 0.0, 0.0], "zona sísmica", None, 8)
    assert [x.chunk_id for x in peru] == ["E030-1"]
    assert peru[0].score == pytest.approx(1 / 61 + 1 / 61)
    assert indice_rrf.search_pais("ecuador", [1.0, 0.0, 0.0], "zona", None, 8)[0].chunk_id == "NEC-1"


def test_sha256_rechaza_archivo_alterado(tmp_path):
    ruta = tmp_path / "x.npz"
    il.construir_archivo([_fila("nsr10", "1", "viga", [1.0, 0.0])], {}, ruta, {})
    datos = bytearray(ruta.read_bytes())
    datos[-1] ^= 0xFF
    ruta.write_bytes(bytes(datos))
    with pytest.raises(ValueError, match="sha256"):
        il.IndiceLocal.cargar(ruta)


# ─── respaldo a la RPC en rag_multi_norma ─────────────────────────────────────────────────────────────────────────────
import rag_multi_norma as rmn  # noqa: E402


class _SbFalso:
    def __init__(self, datos):
        self.datos, self.llamadas = datos, []

    def rpc(self, nombre, params):
        self.llamadas.append((nombre, params))
        datos = self.datos

        class _Resp:
            def execute(self_inner):
                return type("R", (), {"data": datos})()
        return _Resp()


_FILA_RPC = {"chunk_id": "rpc-1", "norma": "NSR-10", "seccion": "A.2", "contenido": "texto", "score": 0.03,
             "metadata": {"estado_vigencia": "vigente"}}
_FILA_RPC_PAIS = {"chunk_id": "rpc-p", "capitulo": "E.030", "seccion": "1", "contenido": "texto", "score": 0.02}


@pytest.fixture()
def rag(monkeypatch):
    monkeypatch.setattr(rmn, "embed_query", lambda q: [1.0, 0.0, 0.0])
    monkeypatch.setattr(rmn, "_indice", {"cargado": False, "valor": None, "error": None})
    monkeypatch.setattr(rmn, "RAG_INDICE_LOCAL", True)
    return monkeypatch


def test_sin_archivo_usa_la_rpc(rag, tmp_path):
    rag.setattr(rmn, "RAG_INDICE_LOCAL_RUTA", tmp_path / "no_existe.npz")
    sb = _SbFalso([_FILA_RPC])
    rag.setattr(rmn, "sb", sb)
    r = rmn.search("viga", top_k=5)
    assert [x.chunk_id for x in r] == ["rpc-1"] and sb.llamadas[0][0] == "search_knowledge"
    assert rmn.estado_indice_local() == {"activo": False, "error": "no existe no_existe.npz"}


def test_archivo_invalido_usa_la_rpc(rag, tmp_path):
    ruta = tmp_path / "malo.npz"
    il.construir_archivo([_fila("nsr10", "1", "viga", [1.0, 0.0, 0.0])], {}, ruta, {})
    ruta.write_bytes(ruta.read_bytes() + b"x")                      # ya no cuadra con el manifiesto
    rag.setattr(rmn, "RAG_INDICE_LOCAL_RUTA", ruta)
    sb = _SbFalso([_FILA_RPC])
    rag.setattr(rmn, "sb", sb)
    assert [x.chunk_id for x in rmn.search("viga")] == ["rpc-1"]
    assert "sha256" in rmn.estado_indice_local()["error"]


def test_indice_que_falla_usa_la_rpc(rag):
    class _Roto:
        def search_knowledge(self, *a, **k):
            raise RuntimeError("se dañó")

        def search_pais(self, *a, **k):
            raise RuntimeError("se dañó")
    rag.setattr(rmn, "_indice", {"cargado": True, "valor": _Roto(), "error": None})
    sb = _SbFalso([_FILA_RPC])
    rag.setattr(rmn, "sb", sb)
    assert [x.chunk_id for x in rmn.search("viga")] == ["rpc-1"]
    sb_pais = _SbFalso([_FILA_RPC_PAIS])
    rag.setattr(rmn, "sb", sb_pais)
    assert [x.chunk_id for x in rmn.search_peru_e030("zona")] == ["rpc-p"]
    assert sb_pais.llamadas[0][0] == "search_knowledge_peru_e030"


def test_apagado_por_variable_usa_la_rpc(rag, tmp_path):
    rag.setattr(rmn, "RAG_INDICE_LOCAL", False)
    sb = _SbFalso([_FILA_RPC])
    rag.setattr(rmn, "sb", sb)
    assert [x.chunk_id for x in rmn.search("viga")] == ["rpc-1"]


def test_indice_valido_no_toca_supabase(rag, tmp_path):
    ruta = tmp_path / "ok.npz"
    il.construir_archivo([_fila("nsr10", "A-1", "viga de concreto", [1.0, 0.0, 0.0], norma_id="n1"),
                          _fila("peru", "P-1", "zona sísmica", [1.0, 0.0, 0.0], norma="E.030")],
                         {"n1": {"nombre_completo": "NSR-10", "estado_vigencia": "vigente", "derogada_por": None,
                                 "alcance_derogacion": None}}, ruta, {})
    rag.setattr(rmn, "RAG_INDICE_LOCAL_RUTA", ruta)

    class _SbProhibido:
        def rpc(self, *a, **k):
            raise AssertionError("con el índice local no debe llamarse a Supabase")
    rag.setattr(rmn, "sb", _SbProhibido())
    r = rmn.search("viga", top_k=3)
    assert [x.chunk_id for x in r] == ["A-1"] and r[0].estado_vigencia == "vigente"
    assert [x.chunk_id for x in rmn.search_peru_e030("zona")] == ["P-1"]
    estado = rmn.estado_indice_local()
    assert estado["activo"] is True and estado["error"] is None


def test_estado_carga_el_indice_sin_consulta_previa(rag, tmp_path):
    """/health?deep=true lo usa el despliegue antes de mover tráfico: debe reflejar el estado real aunque la revisión
    todavía no haya recibido consultas (carga perezosa forzada)."""
    ruta = tmp_path / "ok.npz"
    il.construir_archivo([_fila("nsr10", "A-1", "viga", [1.0, 0.0, 0.0])], {}, ruta, {})
    rag.setattr(rmn, "RAG_INDICE_LOCAL_RUTA", ruta)
    assert rmn._indice["cargado"] is False
    assert rmn.estado_indice_local()["activo"] is True
