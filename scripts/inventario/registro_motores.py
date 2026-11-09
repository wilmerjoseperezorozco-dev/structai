"""Genera docs/REGISTRO_MOTORES.md: registro de motores «medidos a producción» (docs/REGLAS_MOTORES_DE_CALCULO.md).

Qué se comprueba solo y qué no:
  * Condición 3 (contrato, 422, límite de tasa) se deduce del código de cada router: es verificable y se recalcula siempre.
  * Condiciones 1, 2 y 4 (referencia independiente, revisión adversaria, despliegue verificado) NO se pueden deducir del
    código. Se leen de docs/registro_motores.json, donde alguien las atestigua con evidencia. Sin atestar = «?», nunca «sí».
  * Un «sí» en la condición 4 exige revisión de Cloud Run, fecha y evidencia; sin ellas el script falla.

Uso:
    python scripts/inventario/registro_motores.py            # reescribe docs/REGISTRO_MOTORES.md
    python scripts/inventario/registro_motores.py --verificar # falla si el documento está desactualizado o es inconsistente
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

RAIZ = Path(__file__).resolve().parents[2]
RUTAS = RAIZ / "apps" / "api" / "routers"
PRUEBAS_API = RAIZ / "apps" / "api" / "tests"
ATESTACIONES = RAIZ / "docs" / "registro_motores.json"
SALIDA = RAIZ / "docs" / "REGISTRO_MOTORES.md"
CI = RAIZ / ".github" / "workflows" / "ci.yml"
UMBRAL_DAG = 10
CONDICIONES = ("condicion_1", "condicion_2", "condicion_4")

_RE_PREFIJO = re.compile(r'APIRouter\(\s*prefix="([^"]+)"')
_RE_ENDPOINT = re.compile(r'@router\.(get|post)\(\s*"([^"]+)"')
_RE_PAQUETE = re.compile(r'"packages"\s*/\s*"([a-z0-9-]+)"')


class ErrorRegistro(ValueError):
    pass


def paquetes_en_matriz() -> Set[str]:
    """Paquetes de la lista `paquete: [...]` del job test-motores de ci.yml (no basta con que el nombre aparezca en el texto)."""
    m = re.search(r"paquete:\s*\[([^\]]+)\]", CI.read_text(encoding="utf-8"))
    return {p.strip() for p in m.group(1).split(",")} if m else set()


def _endpoints(texto: str) -> List[dict]:
    """Cada endpoint con lo que el código demuestra: límite de tasa y respuesta 422 explícita."""
    posiciones = [(m.start(), m.group(1), m.group(2)) for m in _RE_ENDPOINT.finditer(texto)]
    filas = []
    for i, (ini, metodo, ruta) in enumerate(posiciones):
        fin = posiciones[i + 1][0] if i + 1 < len(posiciones) else len(texto)
        bloque = texto[ini:fin]
        filas.append({"metodo": metodo.upper(), "ruta": ruta, "limite": "limiter.limit(" in bloque,
                      "falla_422": "422" in bloque})
    return [f for f in filas if f["ruta"] != "/salud"]


def _contar_pruebas(directorio: Path) -> int:
    if not directorio.is_dir():
        return 0
    return sum(len(re.findall(r"^\s*(?:async\s+)?def test_", p.read_text(encoding="utf-8"), re.M))
               for p in directorio.rglob("test_*.py"))


def descubrir() -> List[dict]:
    en_matriz = paquetes_en_matriz()
    motores = []
    for ruta in sorted(RUTAS.glob("*.py")):
        texto = ruta.read_text(encoding="utf-8")
        if "ResultadoMotor" not in texto and "contrato_" not in texto:
            continue                                    # router sin contrato uniforme: aún no es candidato
        prefijo = _RE_PREFIJO.search(texto)
        paquete = _RE_PAQUETE.search(texto)
        if not prefijo or not paquete:
            continue
        eps = _endpoints(texto)
        carpeta = RAIZ / "packages" / paquete.group(1)
        usa_resultado = any("ResultadoMotor" in p.read_text(encoding="utf-8") for p in (carpeta / "src").glob("*.py")) \
            if (carpeta / "src").is_dir() else False
        motores.append({
            "id": ruta.stem, "prefijo": prefijo.group(1), "paquete": paquete.group(1), "endpoints": eps,
            "pruebas_paquete": _contar_pruebas(carpeta / "tests"),
            "pruebas_router": _contar_pruebas_router(ruta.stem),
            "en_ci": paquete.group(1) in en_matriz,
            "condicion_3": bool(eps) and usa_resultado and all(e["limite"] and e["falla_422"] for e in eps),
        })
    return motores


def _contar_pruebas_router(nombre: str) -> int:
    total = 0
    for candidato in PRUEBAS_API.glob(f"test_router_{nombre.replace('_api', '')}*.py"):
        total += len(re.findall(r"^\s*(?:async\s+)?def test_", candidato.read_text(encoding="utf-8"), re.M))
    return total


def cargar_atestaciones() -> Dict[str, dict]:
    if not ATESTACIONES.exists():
        return {}
    datos = json.loads(ATESTACIONES.read_text(encoding="utf-8"))
    return datos.get("motores", {})


def validar_atestaciones(motores: List[dict], atest: Dict[str, dict]) -> List[str]:
    """Inconsistencias entre lo atestado y lo que el código permite afirmar."""
    problemas = []
    conocidos = {m["id"] for m in motores}
    for mid, a in atest.items():
        if mid not in conocidos:
            problemas.append(f"{mid}: atestado pero no existe un router con contrato con ese nombre")
            continue
        for c in CONDICIONES:
            e = a.get(c)
            if e is None:
                continue
            if e.get("valor") not in (True, False):
                problemas.append(f"{mid}.{c}: «valor» debe ser true o false")
            elif e["valor"] is True and not e.get("evidencia"):
                problemas.append(f"{mid}.{c}: un «sí» exige evidencia (archivo, commit o issue)")
        c4 = a.get("condicion_4")
        if c4 and c4.get("valor") is True and not (c4.get("revision") and c4.get("fecha")):
            problemas.append(f"{mid}.condicion_4: un «sí» exige revisión de Cloud Run y fecha de la llamada real")
    return problemas


def _celda(a: Optional[dict], c: str) -> str:
    e = (a or {}).get(c)
    return "?" if e is None else ("sí" if e["valor"] else "no")


def renderizar(motores: List[dict], atest: Dict[str, dict]) -> str:
    filas, completos = [], []
    for m in motores:
        a = atest.get(m["id"], {})
        c = [_celda(a, "condicion_1"), _celda(a, "condicion_2"), "sí" if m["condicion_3"] else "no", _celda(a, "condicion_4")]
        if all(x == "sí" for x in c):
            completos.append(m["id"])
        eps = ", ".join(f"{e['metodo']} {m['prefijo']}{e['ruta']}" for e in m["endpoints"]) or "—"
        filas.append(f"| `{m['id']}` | `{m['paquete']}` | {c[0]} | {c[1]} | {c[2]} | {c[3]} | "
                     f"{m['pruebas_paquete']} / {m['pruebas_router']} | {'sí' if m['en_ci'] else 'no'} | {eps} |")
    detalle = []
    for m in motores:
        a = atest.get(m["id"], {})
        notas = [f"- {c.replace('_', ' ')}: {a[c].get('evidencia', 'sin evidencia')}"
                 + (f" (revisión {a[c]['revision']}, {a[c]['fecha']})" if a[c].get("revision") else "")
                 for c in CONDICIONES if a.get(c) is not None]
        if m["endpoints"]:
            faltan = [f"{e['metodo']} {m['prefijo']}{e['ruta']}" for e in m["endpoints"] if not (e["limite"] and e["falla_422"])]
            if faltan:
                notas.append("- condición 3: sin límite de tasa o sin 422 explícito en " + ", ".join(faltan))
        if notas:
            detalle.append(f"### `{m['id']}`\n" + "\n".join(notas))
    return "\n".join([
        "# Registro de motores medidos a producción",
        "",
        "Generado por `scripts/inventario/registro_motores.py`; no editar a mano. Criterio: sección «Criterio de motor «medido a "
        "producción»» de [REGLAS_MOTORES_DE_CALCULO.md](REGLAS_MOTORES_DE_CALCULO.md).",
        "",
        "1. Pruebas rojo→verde contra referencia independiente · 2. Revisión adversaria corregida · 3. Contrato, 422 y límite de tasa · "
        "4. Desplegado en Cloud Run y verificado con llamada real.",
        "",
        "**Cómo se llenan las celdas.** La condición 3 se deduce del código de cada router. Las condiciones 1, 2 y 4 no se pueden "
        "deducir: se atestiguan con evidencia en [registro_motores.json](registro_motores.json). «?» significa sin atestar, "
        "**no** que cumpla; «no» significa que se comprobó que no cumple.",
        "",
        f"**Estado: {len(completos)} de {UMBRAL_DAG} motores cumplen las cuatro condiciones** "
        f"({'el DAG de `packages/dag-proyecto` puede conectarse' if len(completos) >= UMBRAL_DAG else 'el DAG sigue sin conectarse'}).",
        "",
        "| Motor (router) | Paquete | 1 | 2 | 3 | 4 | Pruebas paquete / router | CI | Endpoints |",
        "|---|---|---|---|---|---|---|---|---|",
        *filas,
        "",
        "El conteo de pruebas son funciones `test_*`; una prueba parametrizada cuenta una vez.",
        "",
        "## Evidencia atestada",
        "",
        "\n\n".join(detalle) if detalle else "Ninguna condición atestada todavía.",
        "",
    ])


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verificar", action="store_true", help="no escribe; falla si el documento está desactualizado")
    args = ap.parse_args(argv)
    motores, atest = descubrir(), cargar_atestaciones()
    problemas = validar_atestaciones(motores, atest)
    if problemas:
        print("Atestaciones inconsistentes:\n  " + "\n  ".join(problemas), file=sys.stderr)
        return 2
    texto = renderizar(motores, atest)
    if args.verificar:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != texto:
            print("docs/REGISTRO_MOTORES.md está desactualizado: ejecute scripts/inventario/registro_motores.py", file=sys.stderr)
            return 1
        return 0
    SALIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{SALIDA.relative_to(RAIZ)} escrito: {len(motores)} motores con contrato")
    return 0


if __name__ == "__main__":
    sys.exit(main())
