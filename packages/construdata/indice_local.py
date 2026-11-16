"""Búsqueda híbrida (vectorial exacta + léxica) en la memoria de la API, sin viajes a Supabase (2026-11-16).

Reproduce en Python las RPC ``search_knowledge`` (6 argumentos), ``search_knowledge_peru_e030`` y
``search_knowledge_ecuador_nec_se_ds`` sobre una instantánea comprimida del corpus que se construye en el despliegue
(``scripts/rag/construir_indice_local.py``) y viaja dentro de la imagen Docker. El arranque en frío de Cloud Run la carga
del disco: no hay egress de Supabase por consulta ni al arrancar.

Diferencia deliberada con producción: la parte semántica es EXACTA. En Postgres, HNSW con ``hnsw.ef_search = 40``
devolvía solo 40 vecinos aunque la función pidiera 300 (ver docs/DESCARGA_SUPABASE.md); aquí se ordenan todos.

La parte léxica emula ``to_tsvector('spanish', ...)`` (analizador ``default`` de Postgres 17 + diccionario Snowball
español con su lista de palabras vacías) y ``ts_rank`` con pesos por defecto, en float32 como en C. La paridad con
Postgres se mide sobre el corpus completo (``scripts/rag/verificar_paridad_tsvector.py``); los empates de
``ROW_NUMBER`` no tienen orden definido ni en Postgres, así que pueden diferir.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import threading
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import snowballstemmer

# ─── Palabras vacías: las que el diccionario spanish_stem de Postgres descarta ────────────────────────────────────────
# Obtenidas de Postgres (ts_lexize('spanish_stem', w) = '{}') sobre todo el vocabulario del corpus más las formas
# verbales y pronombres de la lista Snowball. Nótese que 'cual' es vacía pero 'cuál' no (se compara antes de stemizar).
PALABRAS_VACIAS = frozenset("""
a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el él ella ellas ellos en
entre era erais éramos eran eras eres es esa esas ese eso esos esta está estaba estaban estad estada estadas estado
estados estáis estamos están estando estar estará estarán estaría estarían estas estás este esté estén estés esto estos
estuve estuviera estuvieran estuvieron estuvo fue fuera fueran fueron fuese fui ha habéis había habían habías habida
habido habiendo habrá habrán habré habría han has hasta hay haya hayáis hayamos hayan hayas he hemos hube hubiera
hubieran hubiese hubiesen hubo la las le les lo los más me mi mí mía mío mis mucho muchos muy nada ni no nos nosotros
nuestra nuestras nuestro o os otra otras otro otros para pero poco por porque que qué quien quienes se sea seáis seamos
sean seas sentido sentidos será serán seré sería serían sí siente sin sobre sois somos son soy su sus suya suyo también
tanto te tendrá tendrán tendré tendría tendrían tened tenéis tenemos tenga tengan tengo tenía tenían tenida tenidas
tenido tenidos teniendo ti tiene tienen tienes todo todos tu tú tus tuve tuviera tuvieron tuviese tuvo tuyo un una uno
unos vuestro y ya yo
""".split())

_STEMMER = snowballstemmer.stemmer("spanish")
_LOCK_STEM = threading.Lock()  # el stemmer de snowballstemmer guarda estado: no es seguro entre hilos


def _stem(palabra: str) -> Optional[str]:
    """Diccionario spanish_stem: minúsculas, palabra vacía -> nada, si no la raíz Snowball."""
    p = palabra.lower()
    if p in PALABRAS_VACIAS:
        return None
    with _LOCK_STEM:
        return _STEMMER.stemWord(p)


def _simple(palabra: str) -> str:
    return palabra.lower()


# ─── Analizador: emulación del parser 'default' de Postgres para los tipos que aparecen en el corpus ─────────────────
def _es_letra(c: str) -> bool:
    if c.isascii():
        return c.isalpha()
    cat = unicodedata.category(c)
    # glibc considera letra a los dígitos no ASCII (p. ej. malayalam) y a las marcas combinantes (la barra de v̄)
    return cat[0] in "LM" or cat == "Nd"


def _es_digito(c: str) -> bool:
    return "0" <= c <= "9"


def _es_alnum(c: str) -> bool:
    return _es_digito(c) or _es_letra(c)


# Etiqueta HTML/XML: nombre de letras (admite tildes: <Legislación Anterior>) y atributos ASCII simples o entre comillas.
# Postgres NO la reconoce si un atributo lleva tilde, coma, paréntesis o corchete (<Artículo derogado por el artículo
# 118 ...>, <T≤TL, T>): ahí cada palabra se indexa.
_TAG = re.compile(r"""</?[^\W\d_][^\W_]*(?:\s+[A-Za-z0-9._:\-]+(?:=(?:"[^"]*"|'[^']*'|[A-Za-z0-9._:\-/#%?&+]+))?)*\s*/?>""")
_ENTIDAD = re.compile(r"&(?:#[0-9]+|#[xX][0-9A-Fa-f]+|[A-Za-z]+);")
_PROTOCOLO = re.compile(r"(?:https?|ftp)://", re.IGNORECASE)
_EMAIL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+\-]*@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")
_CIENTIFICO = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?[eE][+-]?[0-9]+")
_NUMERO = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)*")
_PUNTEADO = re.compile(r"[A-Za-z0-9]+(?:\.[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)+")   # 'A-3.2.2' no: es 'a' + '3.2.2'
_CARS_RUTA = re.compile(r"[A-Za-z0-9._\-~/]*")
_RUTA_URL = re.compile(r"/[A-Za-z0-9._\-~/%]*")


def _es_host(punteado: str) -> bool:
    ultima = punteado.rsplit(".", 1)[-1]
    return len(ultima) >= 2 and ultima.isascii() and ultima.isalpha()


def _alnum_fin(s: str, i: int) -> int:
    n = len(s)
    while i < n and _es_alnum(s[i]):
        i += 1
    return i


def _recortar_ruta(t: str) -> str:
    return t.rstrip(".-")


def tokens(s: str) -> Iterable[list[tuple[str, str]]]:
    """Grupos de (tipo, token) en orden. Cada grupo es un token del parser y sus partes (palabra compuesta + partes,
    url + host + ruta); cada elemento ocupa una posición, como en to_tsvector."""
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "<":
            m = _TAG.match(s, i)
            i = m.end() if m else i + 1
            continue
        if c == "&":
            m = _ENTIDAD.match(s, i)
            i = m.end() if m else i + 1
            continue
        if c in "+-" and i + 1 < n and _es_digito(s[i + 1]):
            m = _CIENTIFICO.match(s, i)
            if m and not (m.end() < n and _es_alnum(s[m.end()])):
                yield [("sci", m.group())]
                i = m.end()
                continue
            m = _NUMERO.match(s, i)
            if m.group().count(".") >= 2:      # el signo no forma parte de una versión: '-3.2.2' -> '3.2.2'
                i += 1
                continue
            yield [(_tipo_numero(m.group()), m.group())]
            i = m.end()
            continue
        if c == "/" and i + 1 < n and (s[i + 1].isascii() and (s[i + 1].isalnum() or s[i + 1] in "._-~")):
            m = _CARS_RUTA.match(s, i)
            t = _recortar_ruta(m.group())
            if len(t) > 1:
                yield [("file", t)]
                i += len(t)
                continue
            i += 1
            continue
        if not _es_alnum(c):
            i += 1
            continue
        # Correo, URL sin protocolo, host o ruta: solo arrancan con ASCII alfanumérico.
        if c.isascii():
            m = _PROTOCOLO.match(s, i)
            if m:                                   # 'http://' es token 'protocol', que spanish no indexa
                i = m.end()
                continue
            m = _EMAIL.match(s, i)
            if m:
                yield [("email", m.group())]
                i = m.end()
                continue
            if _es_digito(c):
                m = _CIENTIFICO.match(s, i)
                if m and not (m.end() < n and _es_alnum(s[m.end()])):
                    yield [("sci", m.group())]
                    i = m.end()
                    continue
            m = _PUNTEADO.match(s, i)
            if m and not (m.end() < n and _es_alnum(s[m.end()]) and not s[m.end()].isascii()):
                p = m.group()
                if _es_host(p):
                    if m.end() < n and s[m.end()] == "/":
                        r = _RUTA_URL.match(s, m.end())
                        ruta = r.group().rstrip(".,")
                        if len(ruta) > 1:
                            yield [("url", p + ruta), ("host", p), ("url_path", ruta)]
                            i = m.end() + len(ruta)
                            continue
                    yield [("host", p)]
                    i = m.end()
                    continue
                if not _es_digito(c):
                    # Palabra seguida de .número (A.2.3, Fig.3, C.21, a.b): ruta de archivo, que puede seguir con - y /.
                    r = _CARS_RUTA.match(s, i)
                    t = _recortar_ruta(r.group())
                    yield [("file", t)]
                    i += len(t)
                    continue
            j = _alnum_fin(s, i)
            if j < n and s[j] == "/" and s[i:j].isascii() and j + 1 < n and s[j + 1].isascii() and (s[j + 1].isalnum() or s[j + 1] in "._-~"):
                if all(_es_digito(x) for x in s[i:j]) or not _es_digito(c) or any(x.isalpha() for x in s[i:j]):
                    r = _CARS_RUTA.match(s, i)
                    t = _recortar_ruta(r.group())
                    yield [("file", t)]
                    i += len(t)
                    continue
            if _es_digito(c) and all(_es_digito(x) for x in s[i:j]):
                m = _NUMERO.match(s, i)
                yield [(_tipo_numero(m.group()), m.group())]
                i = m.end()
                continue
        j = _alnum_fin(s, i)
        partes = [s[i:j]]
        k = j
        if any(_es_letra(x) for x in partes[0]):
            while k + 1 < n and s[k] == "-" and _es_alnum(s[k + 1]):
                f = _alnum_fin(s, k + 1)
                p = s[k + 1:f]
                if not any(_es_letra(x) for x in p):
                    break
                partes.append(p)
                k = f
        if len(partes) > 1:
            compuesto = "-".join(partes)
            con_digitos = any(_es_digito(x) for x in compuesto)
            grupo = [("numhword" if con_digitos else ("asciihword" if compuesto.isascii() else "hword"), compuesto)]
            for p in partes:
                if any(_es_digito(x) for x in p):
                    grupo.append(("hword_numpart", p))
                else:
                    grupo.append(("hword_asciipart" if p.isascii() else "hword_part", p))
            yield grupo
            i = k
            if i + 1 < n and s[i] == "-" and _es_digito(s[i + 1]):
                i += 1                         # tras un compuesto, '-1' pierde el signo: 'G-A-1' -> 'g-a', 'g', 'a', '1'
            continue
        w = partes[0]
        if any(_es_digito(x) for x in w):
            yield [("numword", w)]
        else:
            yield [("asciiword" if w.isascii() else "word", w)]
        i = j


def _tipo_numero(t: str) -> str:
    puntos = t.count(".")
    if puntos == 0:
        return "int" if t[0] in "+-" else "uint"
    return "decimal" if puntos == 1 else "version"


_TIPOS_STEM = {"asciiword", "word", "asciihword", "hword", "hword_asciipart", "hword_part"}
_MAX_POS = 16383   # MAXENTRYPOS - 1
_MAX_NUMPOS = 256  # posiciones guardadas por lexema


def _lexema(tipo: str, tok: str) -> Optional[str]:
    if len(tok.encode("utf-8")) > 2047:
        return None
    return _stem(tok) if tipo in _TIPOS_STEM else _simple(tok)


def grupos_lexemas(texto: str) -> list[list[Optional[str]]]:
    """Por token del parser, la lista de lexemas (None = palabra vacía, que ocupa posición pero no se indexa)."""
    return [[_lexema(t, k) for t, k in g] for g in tokens(texto or "")]


def conteos_tsvector(texto: Optional[str]) -> dict[str, int]:
    """Lo que ts_rank ve de to_tsvector('spanish', texto): número de posiciones por lexema (topes de Postgres)."""
    if texto is None:
        return {}
    pos_por_lex: dict[str, set] = defaultdict(set)
    pos = 0
    for g in grupos_lexemas(texto):
        for lx in g:
            pos += 1
            if lx is not None:
                pos_por_lex[lx].add(min(pos, _MAX_POS))
    return {lx: min(len(p), _MAX_NUMPOS) for lx, p in pos_por_lex.items()}


def huella_tsvector(texto: Optional[str]) -> str:
    """md5 de 'lexema:n' ordenados por bytes y unidos por espacio; en Postgres:
    md5(string_agg(lexeme || ':' || array_length(positions, 1), ' ' order by lexeme collate "C"))
      from unnest(to_tsvector('spanish', texto))."""
    c = conteos_tsvector(texto)
    s = " ".join(f"{lx}:{c[lx]}" for lx in sorted(c, key=lambda x: x.encode("utf-8")))
    return hashlib.md5(s.encode("utf-8")).hexdigest() if c else ""


# ─── Consultas léxicas ───────────────────────────────────────────────────────────────────────────────────────────────
def consulta_or_colombia(texto: str) -> list[list[str]]:
    """q_or de search_knowledge: to_tsquery('spanish', string_agg(lexeme, ' | ')) sobre unnest(to_tsvector(texto)).

    to_tsquery vuelve a pasar cada lexema por el analizador y el stemmer; si un lexema da varios (compuestos con
    guion, URL), Postgres los une con <-> y aquí se exige que estén todos. Devuelve los grupos (OR entre grupos)."""
    lexemas = sorted(conteos_tsvector(texto), key=lambda x: x.encode("utf-8"))
    grupos = []
    for lx in lexemas:
        re_lex = [x for g in grupos_lexemas(lx) for x in g if x is not None]
        if re_lex:
            grupos.append(re_lex)
    return grupos


def consulta_or_pais(texto: str) -> list[list[str]]:
    """v_tsquery de Perú/Ecuador: plainto_tsquery con ' & ' cambiado por ' | ' (sin volver a stemizar)."""
    grupos = []
    for g in grupos_lexemas(texto):
        lx = [x for x in g if x is not None]
        if lx:
            grupos.append(lx)
    return grupos


_W_D = np.float32(0.1)   # peso por defecto de las posiciones sin peso (D)
_PI2_6 = 1.64493406685


def _aporte_por_conteo() -> np.ndarray:
    """(wjm + resj - wjm/(jm+1)^2) de calc_rank_or para n posiciones, en float32 como en C."""
    out = np.zeros(_MAX_NUMPOS + 1, dtype=np.float32)
    resj = np.float32(0.0)
    for j in range(_MAX_NUMPOS):
        resj = np.float32(resj + np.float32(_W_D / np.float32((j + 1) * (j + 1))))
        out[j + 1] = np.float32(np.float32(_W_D + resj) - np.float32(_W_D / np.float32(1)))
    return out


_APORTE = _aporte_por_conteo()


# ─── Índice ──────────────────────────────────────────────────────────────────────────────────────────────────────────
CORPUS = ("nsr10", "ntc", "motor", "peru", "ecuador")
COLOMBIA = (0, 1, 2)     # search_knowledge une nsr10_chunks, ntc_chunks y motor_chunks


@dataclass
class Fila:
    chunk_id: str
    norma: Optional[str]
    seccion: Optional[str]
    contenido: Optional[str]
    score: float
    metadata: dict


class IndiceLocal:
    def __init__(self, corpus: np.ndarray, ids: list[str], normas: list[Optional[str]], secciones: list[Optional[str]],
                 contenidos: list[Optional[str]], motores: list[Optional[str]], norma_ids: list[Optional[str]],
                 embeddings: np.ndarray, tiene_emb: np.ndarray, vocab: list[str], post_ptr: np.ndarray,
                 post_doc: np.ndarray, post_n: np.ndarray, normas_registro: dict, manifiesto: dict):
        self.corpus, self.ids, self.normas, self.secciones = corpus, ids, normas, secciones
        self.contenidos, self.motores, self.norma_ids = contenidos, motores, norma_ids
        self.emb, self.tiene_emb = embeddings, tiene_emb
        self.normas_min = [None if x is None else x.lower() for x in normas]
        self.motores_arr = np.array([m if m is not None else "" for m in motores], dtype=object)
        self.vocab = {lx: k for k, lx in enumerate(vocab)}
        self.post_ptr, self.post_doc, self.post_n = post_ptr, post_doc, post_n
        self.normas_registro = normas_registro
        self.manifiesto = manifiesto
        self.n = len(ids)

    # -- carga ---------------------------------------------------------------------------------------------------------
    @classmethod
    def cargar(cls, ruta: Path) -> "IndiceLocal":
        man = json.loads(ruta.with_suffix(".manifiesto.json").read_text(encoding="utf-8"))
        datos = ruta.read_bytes()
        if hashlib.sha256(datos).hexdigest() != man["sha256"]:
            raise ValueError(f"{ruta.name} no coincide con su manifiesto (sha256)")
        import io
        z = np.load(io.BytesIO(datos), allow_pickle=False)
        textos = json.loads(gzip.decompress(z["textos_json_gz"].tobytes()).decode("utf-8"))
        return cls(corpus=z["corpus"], ids=textos["ids"], normas=textos["normas"], secciones=textos["secciones"],
                   contenidos=textos["contenidos"], motores=textos["motores"], norma_ids=textos["norma_ids"],
                   embeddings=z["embeddings"], tiene_emb=z["tiene_emb"], vocab=textos["vocab"],
                   post_ptr=z["post_ptr"], post_doc=z["post_doc"], post_n=z["post_n"],
                   normas_registro=textos["normas_registro"], manifiesto=man)

    # -- piezas --------------------------------------------------------------------------------------------------------
    def _filtro(self, corpus: tuple[int, ...], p_norma: Optional[str], p_motor: Optional[str]) -> np.ndarray:
        m = np.isin(self.corpus, corpus)
        if p_norma is not None:
            patron = _ilike(p_norma)
            m &= np.array([x is not None and bool(patron.search(x)) for x in self.normas_min])
        if p_motor is not None:
            m &= np.array([mo == p_motor for mo in self.motores], dtype=bool)
        return m

    def _semantica(self, q: np.ndarray, mascara: np.ndarray, limite: int) -> list[int]:
        cand = np.flatnonzero(mascara & self.tiene_emb)
        if cand.size == 0:
            return []
        e = self.emb[cand]
        qn = q / (np.linalg.norm(q) or 1.0)
        # distancia coseno de pgvector: 1 - a·b / (|a||b|)
        dist = 1.0 - (e @ qn) / np.maximum(np.linalg.norm(e, axis=1), 1e-30)
        orden = np.argsort(dist, kind="stable")[:limite]
        return cand[orden].tolist()

    def _lexica(self, grupos: list[list[str]], mascara: np.ndarray, limite: int) -> list[int]:
        if not grupos:
            return []
        # documentos que cumplen algún grupo (OR de grupos; dentro de un grupo, todos sus lexemas)
        cumple = np.zeros(self.n, dtype=bool)
        conteo: dict[str, np.ndarray] = {}
        for lx in {x for g in grupos for x in g}:
            k = self.vocab.get(lx)
            arr = np.zeros(self.n, dtype=np.int32)
            if k is not None:
                a, b = self.post_ptr[k], self.post_ptr[k + 1]
                arr[self.post_doc[a:b]] = self.post_n[a:b]
            conteo[lx] = arr
        for g in grupos:
            cg = np.ones(self.n, dtype=bool)
            for lx in g:
                cg &= conteo[lx] > 0
            cumple |= cg
        cumple &= mascara
        docs = np.flatnonzero(cumple)
        if docs.size == 0:
            return []
        # ts_rank (calc_rank_or): suma por término único, en el orden de bytes de los términos, float32 como en C
        items = sorted({x for g in grupos for x in g}, key=lambda x: x.encode("utf-8"))
        res = np.zeros(docs.size, dtype=np.float32)
        for lx in items:
            n = conteo[lx][docs]
            aporte = _APORTE[n].astype(np.float64) / _PI2_6
            res = np.where(n > 0, (res.astype(np.float64) + aporte).astype(np.float32), res)
        res = (res / np.float32(len(items))).astype(np.float32)
        orden = np.argsort(-res, kind="stable")[:limite]
        return docs[orden].tolist()

    def _metadata(self, i: int) -> dict:
        nid = self.norma_ids[i]
        nr = self.normas_registro.get(nid) if nid else None
        if nr is None:
            return {}
        der = self.normas_registro.get(nr.get("derogada_por")) if nr.get("derogada_por") else None
        return {"estado_vigencia": nr.get("estado_vigencia"),
                "derogada_por": der.get("nombre_completo") if der else None,
                "alcance_derogacion": nr.get("alcance_derogacion")}

    def _rrf(self, sem: list[int], lex: list[int], rrf_k: int, limite: int, con_metadata: bool) -> list[Fila]:
        """FULL OUTER JOIN por id en texto (como en SQL: ids de tablas distintas pueden coincidir) y suma RRF."""
        por_id_lex: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for r, i in enumerate(lex, 1):
            por_id_lex[self.ids[i]].append((r, i))
        filas, usados = [], set()
        for rs, i in enumerate(sem, 1):
            pares = por_id_lex.get(self.ids[i])
            if pares:
                usados.add(self.ids[i])
                for rl, il in pares:
                    filas.append((Fraction(1, rrf_k + rs) + Fraction(1, rrf_k + rl), i, il))
            else:
                filas.append((Fraction(1, rrf_k + rs), i, None))
        for r, i in enumerate(lex, 1):
            if self.ids[i] not in usados:
                filas.append((Fraction(1, rrf_k + r), i, None))
        filas.sort(key=lambda t: t[0], reverse=True)
        out = []
        for score, i, il in filas[:limite]:
            nid_doc = i if self.norma_ids[i] is not None or il is None else il   # COALESCE(s.norma_id, l.norma_id)
            out.append(Fila(chunk_id=self.ids[i], norma=self.normas[i], seccion=self.secciones[i],
                            contenido=self.contenidos[i], score=float(score),
                            metadata=self._metadata(nid_doc) if con_metadata else {}))
        return out

    # -- RPC equivalentes ----------------------------------------------------------------------------------------------
    def search_knowledge(self, query_embedding, query_text: str, p_norma: Optional[str] = None, match_count: int = 8,
                         rrf_k: int = 60, p_motor: Optional[str] = None) -> list[Fila]:
        mascara = self._filtro(COLOMBIA, p_norma, p_motor)
        q = np.asarray(query_embedding, dtype=np.float32)
        sem = self._semantica(q, mascara, 300)
        lex = self._lexica(consulta_or_colombia(query_text or ""), mascara, 300)
        return self._rrf(sem, lex, rrf_k, match_count, con_metadata=True)

    def search_pais(self, pais: str, query_embedding, query_text: str, p_capitulo: Optional[str] = None,
                    match_count: int = 8, rrf_k: int = 60) -> list[Fila]:
        mascara = self._filtro((CORPUS.index(pais),), p_capitulo, None)
        q = np.asarray(query_embedding, dtype=np.float32)
        sem = self._semantica(q, mascara, match_count * 3)
        lex = self._lexica(consulta_or_pais(query_text or ""), mascara, match_count * 3)
        return self._rrf(sem, lex, rrf_k, match_count, con_metadata=False)

    def resumen(self) -> dict:
        return {k: self.manifiesto.get(k) for k in ("construido_en", "filas_por_corpus", "sha256", "bytes")}


def _ilike(patron: str) -> re.Pattern:
    """ILIKE '%' || p || '%': subcadena sin distinguir mayúsculas; % y _ dentro de p siguen siendo comodines."""
    partes = []
    for ch in patron.lower():
        partes.append(".*" if ch == "%" else "." if ch == "_" else re.escape(ch))
    return re.compile("".join(partes), re.DOTALL)


# ─── Construcción de la instantánea (lo usa scripts/rag/construir_indice_local.py) ─────────────────────────────────────
def construir_archivo(filas: list[dict], normas_registro: dict, ruta: Path, extra_manifiesto: dict) -> dict:
    """filas: dicts con corpus (nombre), id, norma, seccion, contenido, motor, norma_id, embedding (lista o None)."""
    import datetime as dt
    import io

    n = len(filas)
    dim = next((len(f["embedding"]) for f in filas if f["embedding"] is not None), 384)
    emb = np.zeros((n, dim), dtype=np.float32)
    tiene = np.zeros(n, dtype=bool)
    for i, f in enumerate(filas):
        if f["embedding"] is not None:
            emb[i] = np.asarray(f["embedding"], dtype=np.float32)
            tiene[i] = True
    postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for i, f in enumerate(filas):
        for lx, c in conteos_tsvector(f["contenido"]).items():
            postings[lx].append((i, c))
    vocab = sorted(postings, key=lambda x: x.encode("utf-8"))
    ptr = np.zeros(len(vocab) + 1, dtype=np.int64)
    docs, ns = [], []
    for k, lx in enumerate(vocab):
        for i, c in postings[lx]:
            docs.append(i)
            ns.append(c)
        ptr[k + 1] = len(docs)
    textos = {"ids": [str(f["id"]) for f in filas], "normas": [f["norma"] for f in filas],
              "secciones": [f["seccion"] for f in filas], "contenidos": [f["contenido"] for f in filas],
              "motores": [f["motor"] for f in filas], "norma_ids": [f["norma_id"] for f in filas],
              "vocab": vocab, "normas_registro": normas_registro}
    buf = io.BytesIO()
    np.savez_compressed(
        buf, corpus=np.array([CORPUS.index(f["corpus"]) for f in filas], dtype=np.int8), embeddings=emb,
        tiene_emb=tiene, post_ptr=ptr, post_doc=np.array(docs, dtype=np.int32), post_n=np.array(ns, dtype=np.int16),
        textos_json_gz=np.frombuffer(gzip.compress(json.dumps(textos, ensure_ascii=False).encode("utf-8"), 9), dtype=np.uint8))
    datos = buf.getvalue()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(datos)
    man = {"construido_en": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "filas_por_corpus": dict(Counter(f["corpus"] for f in filas)), "dim": dim, "lexemas": len(vocab),
           "postings": len(docs), "bytes": len(datos), "sha256": hashlib.sha256(datos).hexdigest(),
           "snowballstemmer": getattr(snowballstemmer, "__version__", "?"), **extra_manifiesto}
    ruta.with_suffix(".manifiesto.json").write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    return man
