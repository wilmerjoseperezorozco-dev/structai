"""Apoyo para CHANGELOG.md y releases: borrador desde los commits, notas por versión y verificación previa a publicar.

No inventa el contenido del changelog: el borrador agrupa los asuntos de los commits por tipo (`feat`, `fix`, …) para que una persona
lo redacte como lo hace CHANGELOG.md (periodo, agregado, corregido, limitaciones). Lo que sí verifica de forma mecánica es la
coherencia al publicar: la versión del tag, la sección del CHANGELOG y `API_VERSION` de la API.

Uso:
    python scripts/mantenimiento/changelog.py --borrador [--desde REF]        # imprime un borrador agrupado por tipo
    python scripts/mantenimiento/changelog.py --notas 1.16.0                  # imprime la sección de esa versión
    python scripts/mantenimiento/changelog.py --verificar-release v1.16.0     # falla si tag, CHANGELOG y API_VERSION no coinciden
Sin --desde, el borrador parte del último tag vX.Y.Z.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

RAIZ = Path(__file__).resolve().parents[2]
CHANGELOG = RAIZ / "CHANGELOG.md"
MAIN = RAIZ / "apps" / "api" / "main.py"
_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
_ASUNTO = re.compile(r"^(?P<tipo>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<rompe>!)?:\s*(?P<desc>.+)$")
_TIPOS = {"feat": "Agregado", "fix": "Corregido", "perf": "Cambiado", "refactor": "Cambiado",
          "docs": "Documentación", "test": "Mantenimiento", "chore": "Mantenimiento", "ci": "Mantenimiento"}
_ORDEN = ["Agregado", "Corregido", "Cambiado", "Documentación", "Mantenimiento", "Sin clasificar"]


def clasificar(asunto: str) -> Tuple[str, str]:
    """(sección, descripción) a partir del asunto de un commit convencional; lo demás va a «Sin clasificar»."""
    m = _ASUNTO.match(asunto.strip())
    if not m or m["tipo"] not in _TIPOS:
        return "Sin clasificar", asunto.strip()
    desc = m["desc"].strip()
    if m["scope"]:
        desc = f"`{m['scope']}`: {desc}"
    return _TIPOS[m["tipo"]], desc


def agrupar(commits: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    grupos: Dict[str, List[str]] = {}
    for corto, asunto in commits:
        if asunto.startswith("Merge "):
            continue
        seccion, desc = clasificar(asunto)
        grupos.setdefault(seccion, []).append(f"{desc} ({corto})")
    return {k: grupos[k] for k in _ORDEN if k in grupos}


def renderizar_borrador(grupos: Dict[str, List[str]], desde: str) -> str:
    lineas = [f"## [Sin publicar]", "", f"<!-- Borrador generado desde {desde}: redactar a mano antes de publicar (periodo, limitaciones). -->", ""]
    for seccion, items in grupos.items():
        lineas += [f"### {seccion}"] + [f"- {i}" for i in items] + [""]
    return "\n".join(lineas)


def seccion(texto: str, version: str) -> Optional[Tuple[str, str]]:
    """(título, cuerpo) de la sección «## [version] — título» del changelog, o None si no existe."""
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n", texto, re.M)
    if not m:
        return None
    resto = texto[m.end():]
    fin = re.search(r"^## \[", resto, re.M)
    cuerpo = (resto[:fin.start()] if fin else resto).strip()
    return m.group(0).strip(), cuerpo


def version_api(texto_main: str) -> Optional[str]:
    m = re.search(r'^API_VERSION\s*=\s*"([^"]+)"', texto_main, re.M)
    return m.group(1) if m else None


def verificar_release(tag: str, texto_changelog: str, texto_main: str) -> List[str]:
    """Problemas que impiden publicar; lista vacía si tag, CHANGELOG y API_VERSION coinciden."""
    m = _TAG.match(tag)
    if not m:
        return [f"el tag «{tag}» no tiene la forma vX.Y.Z"]
    version = ".".join(m.groups())
    problemas = []
    sec = seccion(texto_changelog, version)
    if sec is None:
        problemas.append(f"CHANGELOG.md no tiene la sección «## [{version}]»")
    elif len(sec[1]) < 40:
        problemas.append(f"la sección [{version}] del CHANGELOG está vacía o casi vacía")
    api = version_api(texto_main)
    if api != version:
        problemas.append(f"API_VERSION es «{api}» y el tag es {version}: actualizar apps/api/main.py")
    return problemas


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True, encoding="utf-8").stdout


def ultimo_tag() -> str:
    tags = [t for t in _git("tag", "--sort=-v:refname", "--merged", "HEAD").split() if _TAG.match(t)]
    if not tags:
        raise SystemExit("no hay ningún tag vX.Y.Z alcanzable desde HEAD; indique --desde")
    return tags[0]


def commits_desde(ref: str) -> List[Tuple[str, str]]:
    salida = _git("log", f"{ref}..HEAD", "--no-merges", "--format=%h%x1f%s")
    return [tuple(l.split("\x1f", 1)) for l in salida.splitlines() if "\x1f" in l]  # type: ignore[misc]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--borrador", action="store_true")
    g.add_argument("--notas", metavar="X.Y.Z")
    g.add_argument("--verificar-release", metavar="vX.Y.Z")
    ap.add_argument("--desde", help="commit o tag de partida del borrador")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    texto = CHANGELOG.read_text(encoding="utf-8")
    if args.borrador:
        desde = args.desde or ultimo_tag()
        print(renderizar_borrador(agrupar(commits_desde(desde)), desde))
        return 0
    if args.notas:
        sec = seccion(texto, args.notas)
        if sec is None:
            print(f"CHANGELOG.md no tiene la sección [{args.notas}]", file=sys.stderr)
            return 1
        print(sec[1])
        return 0
    problemas = verificar_release(args.verificar_release, texto, MAIN.read_text(encoding="utf-8"))
    for p in problemas:
        print("X " + p, file=sys.stderr)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
