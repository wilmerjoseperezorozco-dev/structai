"""Mide la cobertura de líneas de cada paquete y guarda docs/cobertura_medida.json.

Corre las pruebas de cada paquete de la matriz de CI con pytest-cov (tarda ~10 min; motor-concreto ~3 min). Es una medición de
LÍNEAS ejecutadas por las pruebas, no de corrección: un 100 % no demuestra que el cálculo sea correcto. Sin umbral ni compuerta.

Uso:
    python scripts/inventario/cobertura.py                  # mide todos los paquetes de la matriz de CI
    python scripts/inventario/cobertura.py motor-redes      # solo los indicados
"""
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro_motores as reg  # noqa: E402

RAIZ = reg.RAIZ
SALIDA = RAIZ / "docs" / "cobertura_medida.json"
RC = RAIZ / ".coveragerc"


def objetivo(carpeta: Path) -> str:
    if (carpeta / "src").is_dir():
        return "src"
    for hijo in sorted(carpeta.iterdir()):
        if hijo.is_dir() and hijo.name not in ("tests", "__pycache__", "node_modules") and not hijo.name.startswith("."):
            return hijo.name
    raise ValueError(f"{carpeta.name}: no se encontró el código a medir")


def medir(paquete: str) -> Dict[str, object]:
    carpeta = RAIZ / "packages" / paquete
    with tempfile.TemporaryDirectory() as t:
        salida = Path(t) / "cov.json"
        r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", f"--cov={objetivo(carpeta)}",
                            f"--cov-config={RC}", f"--cov-report=json:{salida}"], cwd=carpeta, capture_output=True, text=True)
        if not salida.exists():
            return {"error": "sin reporte de cobertura", "pruebas_pasan": False}
        tot = json.loads(salida.read_text(encoding="utf-8"))["totals"]
    return {"porcentaje": round(tot["percent_covered"], 1), "lineas_cubiertas": tot["covered_lines"],
            "lineas_totales": tot["num_statements"], "pruebas_pasan": r.returncode == 0}


def main(argv: List[str]) -> int:
    previo = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {"paquetes": {}}
    elegidos = argv or sorted(reg.paquetes_en_matriz())
    paquetes = dict(previo["paquetes"])
    for p in elegidos:
        paquetes[p] = medir(p)
        print(p, paquetes[p])
    datos = {"_nota": "Cobertura de líneas medida con scripts/inventario/cobertura.py. Mide qué líneas ejecutan las pruebas, no si el cálculo es correcto.",
             "medido_el": date.today().isoformat(), "paquetes": dict(sorted(paquetes.items()))}
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
