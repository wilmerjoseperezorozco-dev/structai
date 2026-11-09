"""Genera docs/MATRIZ_COHERENCIA.md: qué motores pueden alimentarse unos a otros y cuántas conexiones y cadenas cierran.

Dos motores se conectan cuando una magnitud que produce uno (con su unidad) es una que consume el otro. Las declaraciones viven en
docs/coherencia_motores.json y cada una apunta a su evidencia («ruta::texto»): si el código cambia y la evidencia desaparece, falla.

Qué cuenta y qué no:
  * Una conexión «coherente» dice que las magnitudes coinciden, NO que la cadena esté probada. Solo figuran como probadas las
    cadenas con una prueba que las ejecuta (`cadenas_probadas`).
  * Los motores futuros (planificado, bloqueado) se cuentan aparte y nunca como funcionando.
  * Un motor con declaración «pendiente» aparece en la matriz pero no genera conexiones: no se infiere nada de lo no declarado.

Validación de lo futuro:
    python scripts/inventario/matriz_coherencia.py --verificar               # CI: documento al día, evidencias vigentes, ningún motor nuevo sin declarar
    python scripts/inventario/matriz_coherencia.py --validar-declaracion f.json   # un motor o dato nuevo, antes de añadirlo
    python scripts/inventario/matriz_coherencia.py --validar-valores f.json       # {"magnitud": valor | [valores]}: rango físico y unidad

Uso normal:
    python scripts/inventario/matriz_coherencia.py                           # reescribe docs/MATRIZ_COHERENCIA.md
"""
import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import registro_motores as reg  # noqa: E402

RAIZ = reg.RAIZ
ENTRADA = RAIZ / "docs" / "coherencia_motores.json"
SALIDA = RAIZ / "docs" / "MATRIZ_COHERENCIA.md"
PAQUETES = RAIZ / "packages"
NO_MOTORES = {"contrato-motor", "dag-proyecto", "rag-audit-kit", "eval-stats", "shared-types", "knowledge", "logs", "construdata",
              "bim-intelligence", "ai-gateway", "ve", "yolo"}
DOMINIOS = {"positivo", "no_negativo", "real", "categoria", "compuesto"}
ACCESOS = {"endpoint": 0, "adaptador": 1, "paquete": 2}
ESTADOS = {"implementado", "planificado", "bloqueado"}
TIPOS = {"motor", "dato"}
DECLARACIONES = {"completa", "pendiente"}
LONGITUDES = (2, 3, 4)


# --------------------------------------------------------------------------- validación

def validar_evidencia(evidencia: str, raiz: Path = RAIZ) -> Optional[str]:
    """None si «ruta::texto» existe y el texto está en el archivo; si no, el motivo."""
    ruta, _, ancla = evidencia.partition("::")
    archivo = raiz / ruta
    if not archivo.is_file():
        return f"no existe el archivo {ruta}"
    if ancla and ancla not in archivo.read_text(encoding="utf-8", errors="replace"):
        return f"«{ancla}» no aparece en {ruta}"
    return None


def validar_vocabulario(magnitudes: Dict[str, dict]) -> List[str]:
    problemas = []
    for mid, m in magnitudes.items():
        if not m.get("unidad"):
            problemas.append(f"magnitud {mid}: falta la unidad")
        if m.get("dominio") not in DOMINIOS:
            problemas.append(f"magnitud {mid}: dominio «{m.get('dominio')}» no es uno de {sorted(DOMINIOS)}")
        if "max" in m and not isinstance(m["max"], (int, float)):
            problemas.append(f"magnitud {mid}: max debe ser numérico")
    return problemas


def _validar_lista(nodo: dict, clave: str, magnitudes: Dict[str, dict], raiz: Path) -> List[str]:
    problemas, vistas = [], set()
    for item in nodo.get(clave, []):
        mid = item.get("magnitud")
        if mid not in magnitudes:
            problemas.append(f"{nodo['id']}.{clave}: magnitud «{mid}» fuera del vocabulario (añádala antes con su unidad)")
        if mid in vistas:
            problemas.append(f"{nodo['id']}.{clave}: magnitud «{mid}» repetida")
        vistas.add(mid)
        if item.get("acceso") not in ACCESOS:
            problemas.append(f"{nodo['id']}.{clave}.{mid}: acceso «{item.get('acceso')}» no es uno de {sorted(ACCESOS)}")
        if not item.get("evidencia"):
            problemas.append(f"{nodo['id']}.{clave}.{mid}: falta la evidencia")
        else:
            motivo = validar_evidencia(item["evidencia"], raiz)
            if motivo:
                problemas.append(f"{nodo['id']}.{clave}.{mid}: evidencia inválida, {motivo}")
    return problemas


def validar_nodo(nodo: dict, magnitudes: Dict[str, dict], raiz: Path = RAIZ) -> List[str]:
    """Problemas de la declaración de un motor o dato; lista vacía si está bien formada y su evidencia vigente."""
    if not nodo.get("id"):
        return ["nodo sin id"]
    problemas = []
    for campo, validos in (("tipo", TIPOS), ("estado", ESTADOS), ("declaracion", DECLARACIONES)):
        if nodo.get(campo) not in validos:
            problemas.append(f"{nodo['id']}: {campo} «{nodo.get(campo)}» no es uno de {sorted(validos)}")
    if nodo.get("estado") == "bloqueado" and not nodo.get("bloqueo"):
        problemas.append(f"{nodo['id']}: un nodo bloqueado debe decir por qué (campo bloqueo)")
    if nodo.get("declaracion") == "completa":
        if not nodo.get("salidas"):
            problemas.append(f"{nodo['id']}: declaración completa sin salidas")
        if nodo.get("tipo") == "motor" and not nodo.get("entradas"):
            problemas.append(f"{nodo['id']}: declaración completa sin entradas")
        problemas += _validar_lista(nodo, "entradas", magnitudes, raiz) + _validar_lista(nodo, "salidas", magnitudes, raiz)
    elif nodo.get("entradas") or nodo.get("salidas"):
        problemas.append(f"{nodo['id']}: declaración pendiente no puede traer entradas ni salidas; márquela completa")
    return problemas


def paquetes_de_calculo() -> Set[str]:
    """Carpetas packages/motor-* y el orquestador: todo lo que debe figurar en la matriz."""
    nombres = {p.name for p in PAQUETES.iterdir() if p.is_dir() and p.name.startswith("motor-")}
    return (nombres | {"orquestador"}) - NO_MOTORES


def validar_global(datos: dict, raiz: Path = RAIZ) -> List[str]:
    magnitudes, nodos = datos["magnitudes"], datos["nodos"]
    problemas = validar_vocabulario(magnitudes)
    ids = [n.get("id") for n in nodos]
    for dup in {i for i in ids if ids.count(i) > 1}:
        problemas.append(f"nodo repetido: {dup}")
    for n in nodos:
        problemas += validar_nodo(n, magnitudes, raiz)
    por_id = {n["id"]: n for n in nodos if n.get("id")}
    for paquete in sorted(paquetes_de_calculo()):
        if paquete not in por_id:
            problemas.append(f"el paquete {paquete} no figura en la matriz: añádalo (puede ir con declaracion «pendiente»)")
    for m in reg.descubrir():
        nodo = por_id.get(m["paquete"])
        if nodo is None:
            continue
        reales = {f"{e['metodo']} {m['prefijo']}{e['ruta']}" for e in m["endpoints"]}
        if nodo.get("declaracion") != "completa":
            problemas.append(f"{m['paquete']} tiene contrato y endpoints: su declaración no puede quedar pendiente")
        if set(nodo.get("endpoints", [])) != reales:
            problemas.append(f"{m['paquete']}: endpoints declarados {sorted(nodo.get('endpoints', []))} difieren de los del router {sorted(reales)}")
    return problemas + validar_cadenas(datos, por_id, raiz)


def validar_cadenas(datos: dict, por_id: Dict[str, dict], raiz: Path = RAIZ) -> List[str]:
    problemas = []
    pares = {(a["origen"], a["destino"]) for a in aristas(datos["nodos"])}
    for c in datos.get("cadenas_probadas", []):
        ids = c.get("nodos", [])
        for i in ids:
            if i not in por_id:
                problemas.append(f"cadena probada: el nodo {i} no existe")
            elif por_id[i].get("estado") != "implementado":
                problemas.append(f"cadena probada: {i} no está implementado, no puede figurar como probada")
        for a, b in zip(ids, ids[1:]):
            if (a, b) not in pares:
                problemas.append(f"cadena probada {' -> '.join(ids)}: no hay conexión declarada {a} -> {b}")
        motivo = validar_evidencia(c.get("evidencia", ""), raiz) if c.get("evidencia") else "falta la evidencia (la prueba que la ejecuta)"
        if motivo:
            problemas.append(f"cadena probada {' -> '.join(ids)}: {motivo}")
    return problemas


def validar_valor(magnitudes: Dict[str, dict], magnitud: str, valor: Any) -> None:
    """Lanza ValueError si el valor no es físicamente admisible para la magnitud. Pensado para datos que lleguen a futuro."""
    m = magnitudes.get(magnitud)
    if m is None:
        raise ValueError(f"magnitud «{magnitud}» fuera del vocabulario")
    dominio, unidad, nombre = m["dominio"], m["unidad"], f"{magnitud} [{m['unidad']}]"
    if dominio in ("categoria", "compuesto"):
        ok = isinstance(valor, str) and valor.strip() if dominio == "categoria" else isinstance(valor, (dict, list)) and len(valor) > 0
        if not ok:
            raise ValueError(f"{nombre}: se esperaba {'un texto no vacío' if dominio == 'categoria' else 'una estructura no vacía'}")
        return
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise ValueError(f"{nombre}: debe ser un número finito, llegó {valor!r}")
    if dominio == "positivo" and valor <= 0:
        raise ValueError(f"{nombre}: debe ser positivo, llegó {valor}")
    if dominio == "no_negativo" and valor < 0:
        raise ValueError(f"{nombre}: no puede ser negativo, llegó {valor}")
    if "max" in m and valor > m["max"]:
        raise ValueError(f"{nombre}: supera el máximo físico {m['max']}, llegó {valor}")


# --------------------------------------------------------------------------- grafo

def _declarado(n: dict) -> bool:
    return n.get("declaracion") == "completa"


def aristas(nodos: List[dict]) -> List[dict]:
    """Una arista A->B por cada par con al menos una magnitud que A produce y B consume."""
    resultado = []
    for a in nodos:
        for b in nodos:
            if a["id"] == b["id"] or not (_declarado(a) and _declarado(b)):
                continue
            prod = {s["magnitud"]: s["acceso"] for s in a.get("salidas", [])}
            comunes = [(e["magnitud"], max(ACCESOS[prod[e["magnitud"]]], ACCESOS[e["acceso"]]))
                       for e in b.get("entradas", []) if e["magnitud"] in prod]
            if not comunes:
                continue
            via = min(rango for _, rango in comunes)
            futuro = a["estado"] != "implementado" or b["estado"] != "implementado"
            resultado.append({"origen": a["id"], "destino": b["id"], "magnitudes": sorted(m for m, _ in comunes),
                              "via": {v: k for k, v in ACCESOS.items()}[via], "futuro": futuro})
    return resultado


def caminos(es: List[dict], longitud: int) -> List[Tuple[str, ...]]:
    """Caminos simples (sin repetir nodo) de `longitud` nodos."""
    sig: Dict[str, List[str]] = {}
    for a in es:
        sig.setdefault(a["origen"], []).append(a["destino"])
    salida: List[Tuple[str, ...]] = []

    def avanzar(ruta: Tuple[str, ...]) -> None:
        if len(ruta) == longitud:
            salida.append(ruta)
            return
        for s in sig.get(ruta[-1], []):
            if s not in ruta:
                avanzar(ruta + (s,))

    for n in sig:
        avanzar((n,))
    return salida


def resumen(datos: dict) -> dict:
    nodos = datos["nodos"]
    es = aristas(nodos)
    futuros = {n["id"] for n in nodos if n["estado"] != "implementado"}
    conteos = {}
    for k in LONGITUDES:
        todos = caminos(es, k)
        reales = [c for c in todos if not (set(c) & futuros)]
        conteos[k] = {"implementados": len(reales), "con_futuros": len(todos) - len(reales)}
    consumidas = {e["magnitud"] for n in nodos if _declarado(n) for e in n["entradas"]}
    producidas = {s["magnitud"] for n in nodos if _declarado(n) for s in n["salidas"]}
    return {"aristas": es, "conteos": conteos, "sin_productor": sorted(consumidas - producidas),
            "sin_consumidor": sorted(producidas - consumidas)}


# --------------------------------------------------------------------------- documento

def _tabla_nodos(nodos: List[dict], probados: Set[str]) -> List[str]:
    filas = ["| Nodo | Tipo | Estado | Declaración | Entradas | Salidas | En cadena probada |", "|---|---|---|---|---|---|---|"]
    for n in sorted(nodos, key=lambda x: (x["estado"] != "implementado", x["id"])):
        decl = "completa" if _declarado(n) else "**?** pendiente"
        estado = n["estado"] + (" (bloqueado: " + n["bloqueo"] + ")" if n["estado"] == "bloqueado" else "")
        filas.append(f"| `{n['id']}` | {n['tipo']} | {estado} | {decl} | {len(n.get('entradas', []))} | {len(n.get('salidas', []))} | "
                     f"{'sí' if n['id'] in probados else 'no'} |")
    return filas


def renderizar(datos: dict) -> str:
    nodos, magnitudes = datos["nodos"], datos["magnitudes"]
    r = resumen(datos)
    probados = {i for c in datos.get("cadenas_probadas", []) for i in c["nodos"]}
    impl = [n for n in nodos if n["estado"] == "implementado" and n["tipo"] == "motor"]
    pend = [n["id"] for n in impl if not _declarado(n)]
    futuros = [n for n in nodos if n["estado"] != "implementado"]
    reales = [a for a in r["aristas"] if not a["futuro"]]
    potenciales = [a for a in r["aristas"] if a["futuro"]]
    lineas = [
        "# Matriz de coherencia entre motores y datos",
        "",
        "Generado por `scripts/inventario/matriz_coherencia.py` desde [coherencia_motores.json](coherencia_motores.json); no editar a mano. "
        "Dos nodos se conectan cuando una magnitud que produce uno (con su unidad) es una que consume el otro. "
        "**Coherente no significa probado**: solo las cadenas de la sección «Cadenas probadas» tienen una prueba que las ejecuta.",
        "",
        f"- Motores implementados: {len(impl)}; con declaración completa: {len(impl) - len(pend)}; **pendientes de declarar: {len(pend)}** "
        f"({', '.join('`' + p + '`' for p in pend) or 'ninguno'}). Lo no declarado no genera conexiones: no se infiere nada.",
        f"- Motores futuros (planificados o bloqueados): {len(futuros)}. Nunca se cuentan como funcionando.",
        f"- Magnitudes del vocabulario: {len(magnitudes)}, cada una con unidad y dominio físico.",
        "",
        "## Cuántas conexiones y cadenas cierran",
        "",
        "Camino simple = sin repetir nodo. «Solo implementados» no incluye ningún motor futuro; «con futuros» son los adicionales que "
        "aparecerían al construirlos.",
        "",
        "| Nodos en la cadena | Solo implementados | Adicionales con motores futuros |", "|---|---|---|",
        *[f"| {k} ({'pares' if k == 2 else 'cadenas'}) | {c['implementados']} | {c['con_futuros']} |" for k, c in r["conteos"].items()],
        "",
        f"Probadas de extremo a extremo: **{len(datos.get('cadenas_probadas', []))}**.",
        "",
        "## Cadenas probadas",
        "",
        *([f"- `{' -> '.join(c['nodos'])}` — prueba: `{c['evidencia']}`" for c in datos.get("cadenas_probadas", [])]
          or ["Ninguna."]),
        "",
        "## Conexiones entre nodos implementados",
        "",
        "Vía: **endpoint** = ambos lados son campos del contrato HTTP; **adaptador** = exige una transformación escrita aparte "
        "(combinar cargas, armar la malla); **paquete** = solo desde Python.",
        "",
        "| Origen | Destino | Magnitudes | Vía |", "|---|---|---|---|",
        *[f"| `{a['origen']}` | `{a['destino']}` | {', '.join(a['magnitudes'])} | {a['via']} |" for a in reales],
        "",
        "## Conexiones que abrirían los motores futuros",
        "",
        "| Origen | Destino | Magnitudes |", "|---|---|---|",
        *[f"| `{a['origen']}` | `{a['destino']}` | {', '.join(a['magnitudes'])} |" for a in potenciales],
        "",
        "## Huecos",
        "",
        "**Magnitudes que algún nodo consume y ninguno produce** (las aporta el usuario o un estudio externo): "
        + (", ".join(f"`{m}`" for m in r["sin_productor"]) or "ninguna") + ".",
        "",
        "**Magnitudes que algún nodo produce y ninguno consume** (hoy salen de la cadena sin uso): "
        + (", ".join(f"`{m}`" for m in r["sin_consumidor"]) or "ninguna") + ".",
        "",
        "## Nodos",
        "",
        *_tabla_nodos(nodos, probados),
        "",
        "## Qué se valida hacia el futuro",
        "",
        "- `--verificar` (en CI) falla si el documento está desactualizado, si una evidencia («ruta::texto») ya no existe en el código, "
        "si aparece un paquete `motor-*` sin figurar aquí, si un motor con contrato queda «pendiente» o sus endpoints difieren de los del router, "
        "o si una cadena probada pierde su prueba.",
        "- `--validar-declaracion` revisa la declaración de un motor o dato nuevo antes de añadirlo: magnitudes del vocabulario, accesos y evidencia vigente.",
        "- `--validar-valores` (y la función `validar_valor`) rechaza datos fuera del dominio físico de su magnitud: negativos donde no cabe, "
        "no finitos, por encima del máximo (p. ej. aceleración pico > 2 g, ángulo de fricción > 90°).",
        "",
        "## Límites",
        "",
        "- La coincidencia de magnitudes es condición necesaria, no suficiente: una conexión puede exigir un adaptador (columna «vía») "
        "o supuestos que el contrato de cada motor declara.",
        "- La matriz no mide si una cadena es correcta; eso lo hacen las condiciones 1 y 2 del [registro de motores](REGISTRO_MOTORES.md).",
        "",
    ]
    return "\n".join(lineas)


# --------------------------------------------------------------------------- CLI

def _cargar() -> dict:
    return json.loads(ENTRADA.read_text(encoding="utf-8"))


def _imprimir(problemas: List[str]) -> None:
    for p in problemas:
        print("X " + p.encode("ascii", "replace").decode("ascii"), file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--verificar", action="store_true")
    g.add_argument("--validar-declaracion", metavar="ARCHIVO.json")
    g.add_argument("--validar-valores", metavar="ARCHIVO.json")
    args = ap.parse_args(argv)
    datos = _cargar()
    if args.validar_declaracion:
        nodo = json.loads(Path(args.validar_declaracion).read_text(encoding="utf-8"))
        problemas = validar_nodo(nodo, datos["magnitudes"])
        _imprimir(problemas)
        print("declaracion valida" if not problemas else f"{len(problemas)} problema(s)")
        return 1 if problemas else 0
    if args.validar_valores:
        valores = json.loads(Path(args.validar_valores).read_text(encoding="utf-8"))
        problemas = []
        for mag, v in valores.items():
            for x in (v if isinstance(v, list) and datos["magnitudes"].get(mag, {}).get("dominio") not in ("compuesto",) else [v]):
                try:
                    validar_valor(datos["magnitudes"], mag, x)
                except ValueError as e:
                    problemas.append(str(e))
        _imprimir(problemas)
        print("valores validos" if not problemas else f"{len(problemas)} valor(es) invalido(s)")
        return 1 if problemas else 0
    problemas = validar_global(datos)
    if problemas:
        _imprimir(problemas)
        return 1
    texto = renderizar(datos)
    if args.verificar:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != texto:
            print("docs/MATRIZ_COHERENCIA.md esta desactualizado: ejecute scripts/inventario/matriz_coherencia.py", file=sys.stderr)
            return 1
        return 0
    SALIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{SALIDA.relative_to(RAIZ)} escrito")
    return 0


if __name__ == "__main__":
    sys.exit(main())
