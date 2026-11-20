"""Genera docs/CADENAS_EJECUCION.md + docs/cadenas_ejecucion.json: inventario de cadenas de ejecución (issue #221, fase 1).

Qué es una cadena: la secuencia de PASOS que ejecuta un punto de entrada, en orden de código. Un paso es una llamada
a una función del repositorio (o a un cliente externo) que, directa o transitivamente, hace algo con costo propio:

  llm          llamada a un modelo (Groq/OpenAI/Anthropic/Ollama)
  bd           lectura en Supabase/Postgres/Qdrant
  efecto       escritura en BD (insert/upsert/update/delete), correo, archivo de salida
  red          HTTP externo (httpx/requests/urlopen)
  embeddings   codificación de texto a vector
  motor        cálculo de un motor (packages/motor-*, orquestador, dag-proyecto, cartografía)
  cache        lectura/escritura de una caché existente (TTLCache, lru_cache)
  cpu          resto de pasos internos con subpasos (orquestación)

Puntos de entrada:
  * endpoints de FastAPI (apps/api/main.py y apps/api/routers/*.py) y la herramienta MCP;
  * pipelines fuera de línea: funciones main() de scripts/ (ingesta, evaluación, inventario) y los flujos de
    packages/dag-proyecto y packages/orquestador;
  * cadenas FUTURAS: caminos entre motores declarados en docs/coherencia_motores.json que pasan por un motor
    planificado o bloqueado (inventario estricto: solo nodos y magnitudes declarados con evidencia; no se inventan
    motores). Se calculan con las mismas funciones que docs/MATRIZ_COHERENCIA.md.

Etiquetas (#221): con_efectos (necesita llave de idempotencia, no caché) > con_LLM (cacheable por hash de
prompt+modelo+contexto) > dependiente_de_norma (cacheable con la versión de la norma en la llave) > pura (cacheable).
Una cadena con ≥ 4 pasos secuenciales es CANDIDATA a flujo atómico. El orden de trabajo lo da latencia × frecuencia
MEDIDAS (fase 1, paso 2), no este conteo.

Límites del análisis estático (se declaran, no se esconden):
  * La resolución de llamadas es por imports y nombres; las que no se resuelven no cuentan como paso. Cada paso
    dice cómo se resolvió (import, local, metodo, por_nombre).
  * Las ramas (if/try) se cuentan como secuencia del peor caso; los pasos dentro de `except` no se cuentan.
  * Los motores cargados con importlib se resuelven por nombre de función cuando el nombre es único en el repo.

Uso:
    python scripts/inventario/cadenas_ejecucion.py            # reescribe docs/CADENAS_EJECUCION.md y el JSON
    python scripts/inventario/cadenas_ejecucion.py --verificar # falla si el documento está desactualizado
                                                              # (en el CI es informativo: depende de todo el código)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import matriz_coherencia as mc  # noqa: E402

RAIZ = mc.RAIZ
SALIDA_MD = RAIZ / "docs" / "CADENAS_EJECUCION.md"
SALIDA_JSON = RAIZ / "docs" / "cadenas_ejecucion.json"
UMBRAL = 4
PROFUNDIDAD = 3
RAICES_CODIGO = ("apps/api", "packages", "scripts")
EXCLUIR = {"tests", "test", "node_modules", ".venv", ".venv-motores", "venv", "__pycache__", "terceros", "raw",
           "_privado", "salida", "resultados", "dataset", "dataset_coco"}
ES_MOTOR_HOJA = re.compile(r"^packages/(motor-[a-z0-9-]+|cartografia|yolo)/")    # no se expanden: un cálculo = un paso
PAQUETES_MOTOR = re.compile(r"^packages/(motor-[a-z0-9-]+|orquestador|dag-proyecto|cartografia|yolo)/")
TIPOS = ("llm", "bd", "efecto", "red", "embeddings", "motor", "cache", "cpu")

# Sumideros: patrones sobre el texto de la llamada (p. ej. "self.client.chat.completions.create").
SUMIDEROS = [
    ("llm", re.compile(r"chat\.completions\.create|messages\.create|generate_content|\bollama\b|_llamar_llm|"
                       r"llamar_llm|\bgroq\b", re.I)),
    # Escritura en BD solo si la cadena pasa por una tabla/colección (dict.update o sys.path.insert NO son efectos)
    ("efecto", re.compile(r"(\.table\(\)|\.from_\(\)|collection\w*\(\)|qdrant\w*)\S*\.(insert|upsert|update|delete)\b|"
                          r"\.upsert$|smtplib|send_mail|sendmail|enviar_correo|\.write_text$|\.write_bytes$|\.to_csv$|"
                          r"\.writerows?$|\.savefig$|\.to_parquet$|\.dump$")),
    ("bd", re.compile(r"\.table\(\)|\.table$|\.rpc\(\)|\.rpc$|\.from_\(\)|create_client|qdrant|psycopg|"
                      r"\.query_points$")),
    ("red", re.compile(r"^(httpx|requests|urllib\.request)\.|\.urlopen$|^(cli|client|session|http)\.(get|post)$|"
                       r"hf_hub_download")),
    # Embeddings: el modelo de vectores, no str.encode ni tokenizer.encode (eso es tokenizar, CPU)
    ("embeddings", re.compile(r"^(self\.)?_?(model|modelo|embedder|encoder|st_model|emb\w*)\.encode$|"
                              r"SentenceTransformer\(\)\.encode|embed_(query|documents?|textos?|consulta)|"
                              r"_?embedding_model\(\)\.encode|\.embed$", re.I)),
    ("cache", re.compile(r"(_?cache\w*)\.(get|set)$|lru_cache", re.I)),
    ("motor", re.compile(r"(session|sesion)\.run$|InferenceSession$")),
]
PAQUETES_DATOS = re.compile(r"^packages/(motor-apu|motor-gerencia)/")   # precios/gestión: dependen de datos, no de norma
NORMA = re.compile(r"nsr10_chunks|ntc_chunks|motor_chunks|norma_ref|rag_multi_norma|_recuperar_fuentes|"
                   r"buscar_chunks|match_\w*chunks", re.I)
CORTOS = {"get", "set", "run", "main", "load", "save", "post", "update", "read", "write", "close", "open", "format",
          "append", "items", "keys", "values", "copy", "parse", "join", "split", "strip", "lower", "upper", "info",
          "error", "warning", "debug", "exception", "validate", "dict", "model_dump", "json", "encode", "decode",
          "calcular", "resolver", "procesar", "ejecutar", "construir", "crear", "cargar", "leer", "guardar"}


# ── índice del código ────────────────────────────────────────────────────────────────────────────────────────────
@dataclass
class Funcion:
    id: str                       # ruta/relativa.py::Clase.funcion
    modulo: str                   # ruta relativa
    nombre: str
    clase: Optional[str]
    nodo: ast.AST
    llamadas: List[Tuple[str, int, bool]] = field(default_factory=list)   # (texto, línea, en_except)
    directos: Set[str] = field(default_factory=set)
    norma: bool = False


@dataclass
class Modulo:
    ruta: str
    importados: Dict[str, Tuple[str, Optional[str]]] = field(default_factory=dict)  # alias -> (módulo, nombre|None)
    funciones: Dict[str, Funcion] = field(default_factory=dict)                      # "f" o "Clase.f"


def _texto(n: ast.AST) -> str:
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return f"{_texto(n.value)}.{n.attr}"
    if isinstance(n, ast.Call):
        return _texto(n.func) + "()"
    if isinstance(n, ast.Subscript):
        return _texto(n.value) + "[]"
    return "?"


class _Llamadas(ast.NodeVisitor):
    def __init__(self):
        self.salida: List[Tuple[str, int, bool]] = []
        self._except = 0
        self._rama = 0

    def visit_If(self, n):
        self.visit(n.test)
        self._rama += 1
        for h in n.body + n.orelse:
            self.visit(h)
        self._rama -= 1

    def visit_ExceptHandler(self, n):
        self._except += 1
        self.generic_visit(n)
        self._except -= 1

    def visit_FunctionDef(self, n):        # no entra a funciones anidadas: son otra unidad
        pass

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, n):
        # Argumentos primero (se ejecutan antes que la llamada). En una cadena fluida
        # (sb.table("x").select("*").eq(...).execute()) solo se registra la llamada más externa: es UN paso.
        eslabon = n
        while True:
            for a in list(eslabon.args) + [k.value for k in eslabon.keywords]:
                self.visit(a)
            f = eslabon.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call):
                eslabon = f.value
                continue
            if isinstance(f, ast.Attribute):
                self.visit(f.value)
            break
        texto = _texto(n.func)
        # Llamadas diferidas: la función va como argumento. `_por_flujo` es el flujo atómico de la API (#221, fase 2).
        if re.search(r"(run_in_threadpool|to_thread|\.submit|run_in_executor|_por_flujo)$", texto) and n.args:
            destino = n.args[1] if texto.endswith("run_in_executor") and len(n.args) > 1 else n.args[0]
            if isinstance(destino, (ast.Name, ast.Attribute)):
                self.salida.append((_texto(destino), n.lineno, self._except > 0))
        self.salida.append((texto, n.lineno, self._except > 0))


def archivos() -> List[Path]:
    salida = []
    for raiz in RAICES_CODIGO:
        for p in sorted((RAIZ / raiz).rglob("*.py")):
            rel = p.relative_to(RAIZ).parts
            if any(x in EXCLUIR for x in rel) or p.name.startswith("test_") or p.name == "conftest.py":
                continue
            salida.append(p)
    return salida


def _alias_de_modulo(arbol: ast.Module, m: "Modulo") -> None:
    """Alias que el análisis de `import` no ve y que esconden el paso más caro de una cadena (medido en #221: el diseño de
    columna era el 82 % del pórtico): `_col = importlib.import_module("motor_concreto.columna")` y
    `_dv, _viga = _dp._dv, _dp._viga` (alias reexportado por otro módulo; se resuelve en el Resolutor con «@»)."""
    def uno(destino: ast.expr, valor: ast.expr) -> None:
        if not isinstance(destino, ast.Name):
            return
        if isinstance(valor, ast.Call) and _texto(valor.func).endswith("import_module") and valor.args \
                and isinstance(valor.args[0], ast.Constant) and isinstance(valor.args[0].value, str):
            m.importados[destino.id] = (valor.args[0].value, None)
        elif isinstance(valor, ast.Attribute) and isinstance(valor.value, ast.Name) and valor.value.id in m.importados:
            m.importados[destino.id] = (f"@{valor.value.id}.{valor.attr}", None)

    for n in arbol.body:
        if not isinstance(n, ast.Assign) or len(n.targets) != 1:
            continue
        t, v = n.targets[0], n.value
        if isinstance(t, ast.Tuple) and isinstance(v, ast.Tuple) and len(t.elts) == len(v.elts):
            for a, b in zip(t.elts, v.elts):
                uno(a, b)
        else:
            uno(t, v)


def indexar() -> Dict[str, Modulo]:
    mods: Dict[str, Modulo] = {}
    for p in archivos():
        rel = p.relative_to(RAIZ).as_posix()
        try:
            arbol = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        m = Modulo(rel)
        for n in ast.walk(arbol):
            if isinstance(n, ast.Import):
                for a in n.names:
                    m.importados[(a.asname or a.name).split(".")[0]] = (a.name, None)
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    m.importados[a.asname or a.name] = (n.module, a.name)
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    m.importados[a.asname or a.name] = (a.name, None)
        _alias_de_modulo(arbol, m)
        fuente = p.read_text(encoding="utf-8")

        def registrar(fn, clase=None):
            nombre = f"{clase}.{fn.name}" if clase else fn.name
            f = Funcion(f"{rel}::{nombre}", rel, fn.name, clase, fn)
            v = _Llamadas()
            for hijo in fn.body:
                v.visit(hijo)
            f.llamadas = v.salida
            segmento = ast.get_source_segment(fuente, fn) or ""
            f.norma = bool(NORMA.search(segmento))
            if any(_texto(d.func if isinstance(d, ast.Call) else d).endswith("lru_cache") for d in fn.decorator_list):
                f.directos.add("cache")
            m.funciones[nombre] = f

        for n in arbol.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                registrar(n)
            elif isinstance(n, ast.ClassDef):
                for h in n.body:
                    if isinstance(h, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        registrar(h, n.name)
            elif isinstance(n, ast.If):                 # funciones definidas bajo `if X_AVAILABLE:` etc.
                for h in ast.walk(n):
                    if isinstance(h, (ast.FunctionDef, ast.AsyncFunctionDef)) and h.name not in m.funciones:
                        registrar(h)
        mods[rel] = m
    return mods


class Resolutor:
    def __init__(self, mods: Dict[str, Modulo]):
        self.mods = mods
        self.por_nombre: Dict[str, List[Funcion]] = defaultdict(list)
        self.por_base: Dict[str, List[str]] = defaultdict(list)
        for m in mods.values():
            base = Path(m.ruta).stem if Path(m.ruta).stem != "__init__" else Path(m.ruta).parent.name
            self.por_base[base].append(m.ruta)
            for f in m.funciones.values():
                if not f.clase:
                    self.por_nombre[f.nombre].append(f)
        self.todas = {f.id: f for m in mods.values() for f in m.funciones.values()}

    def modulo_de(self, dotted: str, desde: str) -> Optional[str]:
        partes = dotted.replace("-", "_").split(".")
        candidatos = self.por_base.get(partes[-1], [])
        if not candidatos:
            return None
        if len(candidatos) == 1:
            return candidatos[0]
        cola = "/".join(partes)
        for c in candidatos:                                   # coincidencia por sufijo de ruta (con o sin «src/»)
            norm = c.replace("-", "_").removesuffix(".py")
            if norm.endswith(cola) or norm.replace("/src/", "/").endswith(cola):
                return c
        mismo = [c for c in candidatos if c.split("/")[:2] == desde.split("/")[:2]]
        return mismo[0] if len(mismo) == 1 else None

    def _importado(self, m: "Modulo", nombre: str, saltos: int = 0) -> Optional[Tuple[str, Optional[str]]]:
        """(módulo, nombre) de un alias, persiguiendo los reexportados «@base.attr» (máximo 3 saltos)."""
        par = m.importados.get(nombre)
        if not par or not par[0].startswith("@"):
            return par
        if saltos >= 3:
            return None
        base, _, attr = par[0][1:].partition(".")
        bm = m.importados.get(base)
        ruta = self.modulo_de(bm[0] if bm[1] is None else f"{bm[0]}.{bm[1]}", m.ruta) if bm and not bm[0].startswith("@") else None
        if ruta is None and bm:
            ruta = self.modulo_de(bm[0], m.ruta)
        return self._importado(self.mods[ruta], attr, saltos + 1) if ruta else None

    def resolver(self, texto: str, f: Funcion) -> Tuple[Optional[Funcion], str]:
        m = self.mods[f.modulo]
        partes = texto.split(".")
        if len(partes) == 1:
            n = partes[0]
            if n in m.funciones:
                return m.funciones[n], "local"
            if n in m.importados:
                mod, nom = m.importados[n]
                ruta = self.modulo_de(mod, f.modulo)
                if ruta and nom and nom in self.mods[ruta].funciones:
                    return self.mods[ruta].funciones[nom], "import"
            return self._por_nombre(n)
        cabeza, ultimo = partes[0], partes[-1]
        if cabeza == "self" and f.clase and len(partes) == 2:
            g = m.funciones.get(f"{f.clase}.{ultimo}")
            if g:
                return g, "metodo"
        if cabeza in m.importados and len(partes) == 2 and self._importado(m, cabeza):
            mod, nom = self._importado(m, cabeza)
            ruta = self.modulo_de(f"{mod}.{nom}" if nom else mod, f.modulo) or self.modulo_de(mod, f.modulo)
            if ruta and ultimo in self.mods[ruta].funciones:
                return self.mods[ruta].funciones[ultimo], "import"
        if len(partes) == 2 and (cabeza.endswith("()") or
                                 (not cabeza.startswith(("_", "self")) and cabeza not in m.importados)):
            return self._por_nombre(ultimo)          # módulo cargado con importlib (p. ej. _motor_apu.calcular)
        return None, ""

    def _por_nombre(self, n: str) -> Tuple[Optional[Funcion], str]:
        c = self.por_nombre.get(n, [])
        if len(c) == 1 and len(n) >= 6 and n not in CORTOS:
            return c[0], "por_nombre"
        return None, ""


# ── clasificación ────────────────────────────────────────────────────────────────────────────────────────────────
def sumidero(texto: str) -> Set[str]:
    return {t for t, rx in SUMIDEROS if rx.search(texto)}


class Analisis:
    def __init__(self, mods: Dict[str, Modulo]):
        self.r = Resolutor(mods)
        self._tipos: Dict[str, Set[str]] = {}
        self._norma: Dict[str, bool] = {}
        for f in self.r.todas.values():
            for texto, _, _ in f.llamadas:
                f.directos |= sumidero(texto)
            if PAQUETES_MOTOR.match(f.modulo) or PAQUETES_DATOS.match(f.modulo):
                f.directos.add("motor")
            if PAQUETES_MOTOR.match(f.modulo) and not PAQUETES_DATOS.match(f.modulo):
                f.norma = True

    def tipos(self, f: Funcion, pila: Tuple[str, ...] = ()) -> Set[str]:
        """Tipos transitivos de una función (con corte de ciclos)."""
        if f.id in self._tipos:
            return self._tipos[f.id]
        if f.id in pila or len(pila) > 12:
            return set(f.directos)
        t = set(f.directos)
        n = f.norma
        for texto, _, _ in f.llamadas:
            g, _ = self.r.resolver(texto, f)
            if g:
                t |= self.tipos(g, pila + (f.id,))
                n = n or self._norma.get(g.id, g.norma)
        self._tipos[f.id] = t
        self._norma[f.id] = n
        return t

    def norma(self, f: Funcion) -> bool:
        self.tipos(f)
        return self._norma.get(f.id, f.norma)

    def pasos(self, f: Funcion, prof: int = 0, pila: Tuple[str, ...] = ()) -> List[dict]:
        salida: List[dict] = []
        for texto, linea, en_except in f.llamadas:
            if en_except:
                continue
            directos = sumidero(texto)
            g, via = self.r.resolver(texto, f)
            if g and g.id not in pila and g.id != f.id:
                t = self.tipos(g)
                if not t:
                    continue
                sub = self.pasos(g, prof + 1, pila + (f.id,)) if prof < PROFUNDIDAD else []
                if len(sub) >= 2 and not ES_MOTOR_HOJA.match(g.modulo):
                    salida += sub                              # función orquestadora: se expande
                else:
                    salida.append({"paso": g.id, "tipo": _principal(t), "tipos": sorted(t), "via": via,
                                   "linea": f"{f.modulo}:{linea}", "norma": self.norma(g)})
            elif g:
                continue
            elif directos:
                salida.append({"paso": texto, "tipo": _principal(directos), "tipos": sorted(directos),
                               "via": "externo", "linea": f"{f.modulo}:{linea}", "norma": bool(NORMA.search(texto))})
        return _sin_repetidos(salida)


def _principal(t: Set[str]) -> str:
    for k in ("llm", "efecto", "bd", "red", "embeddings", "motor", "cache"):
        if k in t:
            return k
    return "cpu"


def _sin_repetidos(p: List[dict]) -> List[dict]:
    salida = []
    for x in p:
        if salida and salida[-1]["paso"] == x["paso"]:
            continue
        salida.append(x)
    return salida


def etiquetas(pasos: List[dict]) -> List[str]:
    t = {x["tipo"] for x in pasos} | {k for x in pasos for k in x["tipos"]}
    e = []
    if "efecto" in t:
        e.append("con_efectos")
    if "llm" in t:
        e.append("con_LLM")
    if any(x["norma"] for x in pasos):
        e.append("dependiente_de_norma")
    if {"bd", "red"} & t or ("motor" in t and not any(x["norma"] for x in pasos)):
        e.append("dependiente_de_datos")
    if not ({"efecto", "llm", "bd", "red"} & t) and "dependiente_de_norma" not in e:
        e.append("pura")
    return e or ["sin_clasificar"]


# ── puntos de entrada ────────────────────────────────────────────────────────────────────────────────────────────
_RX_RUTA = re.compile(r"^(app|router)\.(get|post|put|delete|patch)$")


def endpoints(mods: Dict[str, Modulo]) -> List[Tuple[str, Funcion]]:
    salida = []
    for ruta in sorted(mods):
        if not (ruta == "apps/api/main.py" or ruta.startswith("apps/api/routers/") or ruta == "apps/api/mcp_server.py"):
            continue
        prefijo = ""
        fuente = (RAIZ / ruta).read_text(encoding="utf-8")
        mp = re.search(r'APIRouter\(\s*prefix="([^"]+)"', fuente)
        if mp:
            prefijo = mp.group(1)
        for f in mods[ruta].funciones.values():
            rutas = []
            for d in getattr(f.nodo, "decorator_list", []):
                if isinstance(d, ast.Call) and _RX_RUTA.match(_texto(d.func)) and d.args and \
                        isinstance(d.args[0], ast.Constant) and not str(d.args[0].value).startswith("/v1"):
                    rutas.append(f"{_texto(d.func).split('.')[1].upper()} {prefijo}{d.args[0].value}")
                elif isinstance(d, ast.Call) and _texto(d.func).endswith(".tool"):
                    rutas.append(f"MCP {f.nombre}")
            for r in rutas:
                salida.append((r, f))
    return salida


def pipelines(mods: Dict[str, Modulo]) -> List[Tuple[str, Funcion]]:
    salida = []
    for ruta in sorted(mods):
        m = mods[ruta]
        if ruta.startswith("scripts/") and "main" in m.funciones:
            salida.append((ruta, m.funciones["main"]))
        elif ruta.startswith("scripts/") and ruta.endswith(".sh"):
            continue
        elif re.match(r"^packages/(dag-proyecto|orquestador)/", ruta):
            for nombre, f in m.funciones.items():
                if not nombre.startswith("_") and "." not in nombre and nombre in {
                        "ejecutar", "ejecutar_dag", "correr", "orquestar", "portico_integral", "materializar"}:
                    salida.append((f"{ruta}::{nombre}", f))
    return salida


RX_PUNTUAL = re.compile(r"/_[^/]+\.py$|20\d\d-\d\d-\d\d|_(fix|parche|retroch\w*|reintentar|verificar_\d+)\b|/(fix|parche)_")


def puntual(entrada: str) -> bool:
    """Script de una sola vez (prefijo _, fecha en el nombre, fix/parche/reintento): no es un pipeline recurrente."""
    return bool(RX_PUNTUAL.search(entrada))


def familia(entrada: str) -> str:
    e = entrada.lower()
    if e.startswith("scripts/"):
        return "scripts/" + e.split("/")[1]
    for clave, nombre in (("/ask", "rag"), ("/consultar", "rag"), ("mcp", "rag"), ("/detect", "vision"),
                          ("/apu", "precios"), ("/orquestador", "orquestador"), ("/proyecto", "orquestador"),
                          ("scripts/ingesta", "ingesta"), ("scripts/evaluacion", "evaluacion"),
                          ("scripts/inventario", "inventario"), ("dag-proyecto", "orquestador"),
                          ("packages/orquestador", "orquestador"), ("health", "sistema"), ("status", "sistema")):
        if clave in e:
            return nombre
    return "motor" if e.split(" ")[0] in {"get", "post", "put", "delete", "patch"} else "otro"


# ── cadenas futuras (estricto) ───────────────────────────────────────────────────────────────────────────────────
def cadenas_futuras() -> List[dict]:
    datos = json.loads(mc.ENTRADA.read_text(encoding="utf-8"))
    nodos = {n["id"]: n for n in datos["nodos"]}
    es = mc.aristas(datos["nodos"])
    por_par = {(a["origen"], a["destino"]): a["magnitudes"] for a in es}
    futuros = {i for i, n in nodos.items() if n["estado"] != "implementado"}
    salida = []
    for k in range(UMBRAL, 7):
        for c in mc.caminos(es, k):
            if not set(c) & futuros:
                continue
            salida.append({"nodos": list(c), "pasos": len(c),
                           "futuros": [i for i in c if i in futuros],
                           "estados": [nodos[i]["estado"] for i in c],
                           "magnitudes": [por_par[(a, b)] for a, b in zip(c, c[1:])],
                           "etiquetas": ["dependiente_de_norma", "pura"] if all(nodos[i]["tipo"] in ("motor", "dato")
                                                                                 for i in c) else ["sin_clasificar"]})
    salida.sort(key=lambda x: (-x["pasos"], x["nodos"]))
    return salida


# ── informe ──────────────────────────────────────────────────────────────────────────────────────────────────────
def inventario() -> dict:
    mods = indexar()
    a = Analisis(mods)
    cadenas = []
    for clase, entradas in (("endpoint", endpoints(mods)), ("pipeline", pipelines(mods))):
        for nombre, f in entradas:
            p = a.pasos(f)
            es_puntual = clase == "pipeline" and puntual(nombre)
            cadenas.append({"entrada": nombre, "clase": clase, "familia": familia(nombre), "funcion": f.id,
                            "pasos": len(p), "puntual": es_puntual,
                            "candidata": len(p) >= UMBRAL and not es_puntual, "etiquetas": etiquetas(p),
                            "cache_existente": any(x["tipo"] == "cache" for x in p),
                            "secuencia": p})
    cadenas.sort(key=lambda c: (c["clase"], -c["pasos"], c["entrada"]))
    resueltas = Counter(x["via"] for c in cadenas for x in c["secuencia"])
    return {"umbral": UMBRAL, "profundidad": PROFUNDIDAD, "modulos": len(mods),
            "funciones": sum(len(m.funciones) for m in mods.values()), "resolucion": dict(sorted(resueltas.items())),
            "cadenas": cadenas, "futuras": cadenas_futuras()}


def _resumen_secuencia(p: List[dict], n: int = 9) -> str:
    def corto(x):
        nombre = x["paso"].split("::")[-1]
        return f"{nombre}[{x['tipo']}]"
    s = " → ".join(corto(x) for x in p[:n])
    return s + (f" → … (+{len(p) - n})" if len(p) > n else "")


def renderizar(inv: dict) -> str:
    cad = inv["cadenas"]
    cand = [c for c in cad if c["candidata"]]
    L = ["# Inventario de cadenas de ejecución (#221, fase 1)", "",
         "Generado por `scripts/inventario/cadenas_ejecucion.py`; no editar a mano. Análisis **estático** (AST + imports): "
         "dice qué pasos hay y de qué tipo, **no cuánto tardan**. El orden de trabajo lo da latencia × frecuencia medidas "
         "(fase 1, paso 2), nunca este conteo solo. Ver el docstring para la definición de paso, tipo y etiqueta.", "",
         f"- Código analizado: {inv['modulos']:,} módulos, {inv['funciones']:,} funciones (sin pruebas).",
         f"- Puntos de entrada: {sum(c['clase'] == 'endpoint' for c in cad)} endpoints y "
         f"{sum(c['clase'] == 'pipeline' for c in cad)} pipelines fuera de línea.",
         f"- **Candidatas a flujo atómico (≥ {inv['umbral']} pasos secuenciales): {len(cand)}** "
         f"({sum(c['clase'] == 'endpoint' for c in cand)} endpoints, {sum(c['clase'] == 'pipeline' for c in cand)} pipelines).",
         f"- Cadenas futuras con ≥ {inv['umbral']} motores que pasan por un motor planificado o bloqueado: "
         f"**{len(inv['futuras'])}** (solo nodos declarados en `docs/coherencia_motores.json`).",
         "- Resolución de los pasos: " + ", ".join(f"{k} {v}" for k, v in inv["resolucion"].items()) +
         " (`por_nombre` = función única en el repo con ese nombre; revisar si un paso parece fuera de lugar).", "",
         "## Etiquetas de las candidatas", "",
         "| Etiqueta | Candidatas | Qué permite |", "|---|---|---|"]
    que = {"con_efectos": "llave de idempotencia (no caché)", "con_LLM": "caché por hash de prompt + modelo + contexto, con aviso",
           "dependiente_de_norma": "caché con la versión de la norma en la llave (#193)",
           "dependiente_de_datos": "caché con la versión/fecha del dato (catálogo, tabla) en la llave",
           "pura": "caché directa",
           "sin_clasificar": "revisar a mano"}
    cuenta = Counter(e for c in cand for e in c["etiquetas"])
    L += [f"| `{e}` | {cuenta.get(e, 0)} | {q} |" for e, q in que.items()]
    L += ["", f"Con caché ya existente en la secuencia: {sum(c['cache_existente'] for c in cand)} de {len(cand)}.", "",
          "## Por familia", "", "| Familia | Cadenas | Candidatas | Con LLM | Con efectos |", "|---|---|---|---|---|"]
    fam = defaultdict(list)
    for c in cad:
        fam[c["familia"]].append(c)
    for k in sorted(fam, key=lambda k: -len(fam[k])):
        cs = fam[k]
        L.append(f"| {k} | {len(cs)} | {sum(c['candidata'] for c in cs)} | "
                 f"{sum('con_LLM' in c['etiquetas'] for c in cs)} | {sum('con_efectos' in c['etiquetas'] for c in cs)} |")
    L += ["", "## Endpoints candidatos (los que ve el usuario)", "",
          "| Entrada | Pasos | Etiquetas | Caché | Secuencia |", "|---|---|---|---|---|"]
    for c in [c for c in cand if c["clase"] == "endpoint"]:
        L.append(f"| `{c['entrada']}` | {c['pasos']} | {', '.join(c['etiquetas'])} | "
                 f"{'sí' if c['cache_existente'] else 'no'} | {_resumen_secuencia(c['secuencia'], 12)} |")
    pip = [c for c in cand if c["clase"] == "pipeline"]
    L += ["", "## Pipelines recurrentes candidatos (fuera de línea)", "",
          f"{len(pip)} pipelines recurrentes llegan al umbral; {sum(c['puntual'] for c in cad)} scripts puntuales "
          "(prefijo `_`, fecha en el nombre, fix/parche/reintento) no cuentan como candidatos. Los 25 más largos:", "",
          "| Entrada | Pasos | Etiquetas | Secuencia |", "|---|---|---|---|"]
    for c in pip[:25]:
        L.append(f"| `{c['entrada']}` | {c['pasos']} | {', '.join(c['etiquetas'])} | {_resumen_secuencia(c['secuencia'], 7)} |")
    L += ["", "| Carpeta | Pipelines candidatos | Con efectos | Con LLM |", "|---|---|---|---|"]
    por = defaultdict(list)
    for c in pip:
        por[c["familia"]].append(c)
    for k in sorted(por, key=lambda k: -len(por[k])):
        L.append(f"| `{k}` | {len(por[k])} | {sum('con_efectos' in c['etiquetas'] for c in por[k])} | "
                 f"{sum('con_LLM' in c['etiquetas'] for c in por[k])} |")
    L += ["", "## Cadenas futuras (motores planificados o bloqueados)", "",
          "Inventario estricto: caminos simples entre nodos **declarados** (con evidencia) en `docs/coherencia_motores.json`, "
          "enlazados por magnitudes que uno produce y otro consume. Ningún motor futuro se cuenta como funcionando. "
          "Todas son cálculo de motores: al implementarse nacen como flujo atómico `dependiente_de_norma` con artefactos "
          "direccionados por contenido (#150).", "",
          "| Motor futuro | Estado | Cadenas futuras en las que aparece | Máximo de nodos |", "|---|---|---|---|"]
    estado = {i: e for f in inv["futuras"] for i, e in zip(f["nodos"], f["estados"])}
    aparece = Counter(i for f in inv["futuras"] for i in f["futuros"])
    largo = defaultdict(int)
    for f in inv["futuras"]:
        for i in f["futuros"]:
            largo[i] = max(largo[i], f["pasos"])
    L += [f"| `{i}` | {estado[i]} | {v} | {largo[i]} |" for i, v in aparece.most_common()]
    L += ["", "Un motor futuro que aparece en muchas cadenas desbloquea más flujos al implementarse; es una señal de "
          "prioridad, no la única (falta el costo de construirlo y la demanda medida).", "",
          "| Nodos | Cadena | Motores futuros | Magnitudes que pasan |", "|---|---|---|---|"]
    for f in inv["futuras"][:40]:
        L.append(f"| {f['pasos']} | {' → '.join(f['nodos'])} | {', '.join(f['futuros'])} | "
                 f"{' / '.join(','.join(m) for m in f['magnitudes'])} |")
    if len(inv["futuras"]) > 40:
        L.append(f"| … | {len(inv['futuras']) - 40} más en `docs/cadenas_ejecucion.json` | | |")
    L += ["", "## Cadenas cortas (< 4 pasos)", "",
          f"{sum(not c['candidata'] for c in cad)} cadenas no llegan al umbral. No se descartan: una de 3 pasos con un LLM "
          "puede pesar más que una de 6 en CPU. Están completas en el JSON.", ""]
    return "\n".join(L)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    inv = inventario()
    md = renderizar(inv)
    js = json.dumps(inv, ensure_ascii=False, indent=1) + "\n"
    if a.verificar:
        # Solo el Markdown (sin números de línea): el JSON trae líneas que cambian con cualquier edición.
        ok = SALIDA_MD.exists() and SALIDA_MD.read_text(encoding="utf-8") == md
        if not ok:
            print(f"{SALIDA_MD.relative_to(RAIZ)} está desactualizado: ejecute scripts/inventario/cadenas_ejecucion.py")
            return 1
        print("✓ inventario de cadenas al día")
        return 0
    SALIDA_MD.write_text(md, encoding="utf-8")
    SALIDA_JSON.write_text(js, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
