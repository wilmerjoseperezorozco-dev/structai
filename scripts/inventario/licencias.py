"""Inventario de licencias de las dependencias DIRECTAS (Python y npm) → docs/LICENCIAS_DEPENDENCIAS.md.

La licencia se lee de los metadatos del paquete instalado en este entorno (Python) o de node_modules (npm). Si el paquete
no está instalado, queda «sin verificar»: no se adivina. Es un inventario de dependencias directas; no cubre las transitivas
ni reemplaza una revisión legal. La clasificación es por palabras clave del campo de licencia, pensada para señalar qué
revisar (copyleft), no para dictaminar compatibilidad.

Uso:
    python scripts/inventario/licencias.py             # escribe docs/LICENCIAS_DEPENDENCIAS.md
    python scripts/inventario/licencias.py --stdout    # solo imprime
"""
import argparse
import json
import re
import sys
from importlib import metadata
from pathlib import Path
from typing import Dict, List, Optional

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "docs" / "LICENCIAS_DEPENDENCIAS.md"
_REQ = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def clasificar(licencia: str) -> str:
    t = licencia.upper()
    if not t.strip() or t.strip() == "UNKNOWN" or t.startswith("SIN VERIFICAR"):
        return "sin verificar"
    if "AGPL" in t:
        return "copyleft fuerte (red): revisar"
    if "LGPL" in t or "MPL" in t or "EPL" in t:
        return "copyleft débil: revisar"
    if re.search(r"\bGPL", t) or "GNU GENERAL" in t:
        return "copyleft fuerte: revisar"
    if any(k in t for k in ("MIT", "BSD", "APACHE", "ISC", "PSF", "PYTHON SOFTWARE", "HPND", "UNLICENSE", "0BSD", "CC0", "ZLIB", "BLUEOAK")):
        return "permisiva"
    return "revisar a mano"


def leer_requirements(ruta: Path) -> List[str]:
    nombres = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0]
        m = _REQ.match(linea)
        if m and not linea.strip().startswith("-"):
            nombres.append(m.group(1))
    return nombres


def licencia_python(nombre: str) -> Optional[str]:
    try:
        md = metadata.metadata(nombre)
    except metadata.PackageNotFoundError:
        return None
    expr = md.get("License-Expression")
    if expr:
        return expr
    lic = (md.get("License") or "").strip()
    clasif = [c.split("::")[-1].strip() for c in md.get_all("Classifier") or [] if c.startswith("License ::")]
    if lic and len(lic) < 80 and "\n" not in lic:
        return lic
    return "; ".join(clasif) or (lic.splitlines()[0][:80] if lic else "UNKNOWN")


def licencia_npm(nombre: str) -> Optional[str]:
    for base in (RAIZ / "node_modules", RAIZ / "apps" / "web" / "node_modules"):
        p = base / nombre / "package.json"
        if p.exists():
            lic = json.loads(p.read_text(encoding="utf-8")).get("license")
            if isinstance(lic, dict):
                lic = lic.get("type")
            return str(lic) if lic else "UNKNOWN"
    return None


def recolectar() -> List[Dict[str, str]]:
    filas: List[Dict[str, str]] = []
    vistos = set()
    fuentes = [("apps/api", RAIZ / "apps" / "api" / "requirements.txt")] + \
              [(f"packages/{p.parent.name}", p) for p in sorted((RAIZ / "packages").glob("*/requirements.txt"))]
    for origen, ruta in fuentes:
        for n in leer_requirements(ruta):
            clave = ("py", n.lower().replace("_", "-"))
            if clave in vistos:
                continue
            vistos.add(clave)
            lic = licencia_python(n)
            prueba = n.lower().startswith("pytest") or n.lower() == "locust"
            filas.append({"eco": "Python (pruebas)" if prueba else "Python", "paquete": n, "origen": origen,
                          "licencia": lic or "sin verificar (no instalado)"})
    web = json.loads((RAIZ / "apps" / "web" / "package.json").read_text(encoding="utf-8"))
    for seccion, etiqueta in (("dependencies", "npm"), ("devDependencies", "npm (desarrollo)")):
        for n in sorted(web.get(seccion, {})):
            if n == "shared-types":
                continue                                   # paquete interno del monorepo
            lic = licencia_npm(n)
            filas.append({"eco": etiqueta, "paquete": n, "origen": "apps/web", "licencia": lic or "sin verificar (no instalado)"})
    for f in filas:
        f["clase"] = clasificar(f["licencia"])
    return filas


def renderizar(filas: List[Dict[str, str]]) -> str:
    conteo: Dict[str, int] = {}
    for f in filas:
        conteo[f["clase"]] = conteo.get(f["clase"], 0) + 1
    resumen = " · ".join(f"{k}: {v}" for k, v in sorted(conteo.items()))
    revisar = [f for f in filas if f["clase"] not in ("permisiva",)]
    cuerpo = ["| Ecosistema | Paquete | Dónde se declara | Licencia (metadatos) | Clasificación |", "|---|---|---|---|---|"]
    cuerpo += [f"| {f['eco']} | `{f['paquete']}` | {f['origen']} | {f['licencia']} | {f['clase']} |" for f in sorted(filas, key=lambda x: (x["clase"] == "permisiva", x["eco"], x["paquete"].lower()))]
    return "\n".join([
        "# Licencias de dependencias directas",
        "",
        "Generado por `scripts/inventario/licencias.py`; no editar a mano. Lee la licencia de los metadatos del paquete instalado "
        "(Python) o de `node_modules` (npm). **«Sin verificar» significa que el paquete no estaba instalado al generar el informe, no que "
        "su licencia sea buena o mala.** Solo dependencias directas; las transitivas no se revisan. No es asesoría legal.",
        "",
        f"**Resumen ({len(filas)} dependencias directas):** {resumen}.",
        "",
        f"**Para revisar primero ({len(revisar)}):** " + (", ".join(f"`{f['paquete']}`" for f in revisar) or "ninguna") + ".",
        "",
        "El repositorio es de propiedad del autor y no es de código abierto ([LICENSE](../LICENSE)); un paquete con copyleft "
        "(GPL, LGPL, AGPL, MPL) puede imponer obligaciones al distribuirlo o al ofrecerlo como servicio en red. Verificar cada caso "
        "con la licencia completa antes de afirmar compatibilidad.",
        "",
        *cuerpo,
        "",
    ])


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)
    texto = renderizar(recolectar())
    if args.stdout:
        sys.stdout.buffer.write(texto.encode("utf-8"))
        return 0
    SALIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{SALIDA.relative_to(RAIZ)} escrito")
    return 0


if __name__ == "__main__":
    sys.exit(main())
