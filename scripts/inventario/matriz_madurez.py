"""Genera docs/MATRIZ_MADUREZ.md: matriz de evidencia por subsistema (TRL + calidad + operación + licencias).

No hay una «puntuación de madurez» única a propósito: cada columna se sustenta en una fuente distinta y se lee por separado.
  * Calidad (pruebas, CI, contrato/422/límite de tasa): se deduce del repositorio (scripts/inventario/registro_motores.py).
  * Licencias: se lee de los metadatos de las dependencias directas (scripts/inventario/licencias.py).
  * TRL y operación: NO se pueden deducir; se atestiguan en docs/matriz_madurez.json con evidencia y límite. Sin atestar = «?».
    Los motores con contrato toman la operación del registro de motores (condición 4).

Uso:
    python scripts/inventario/matriz_madurez.py             # escribe docs/MATRIZ_MADUREZ.md
    python scripts/inventario/matriz_madurez.py --verificar # falla si el documento está desactualizado
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import licencias as lic  # noqa: E402
import registro_motores as reg  # noqa: E402

RAIZ = reg.RAIZ
ENTRADA = RAIZ / "docs" / "matriz_madurez.json"
SALIDA = RAIZ / "docs" / "MATRIZ_MADUREZ.md"
_ORDEN = ["copyleft fuerte (red): revisar", "copyleft fuerte: revisar", "copyleft débil: revisar", "revisar a mano", "sin verificar", "permisiva"]


def _peor_licencia(origenes: List[str], deps: List[Dict[str, str]]) -> str:
    propias = [d for d in deps if d["origen"] in origenes and "pruebas" not in d["eco"] and "desarrollo" not in d["eco"]]
    if not propias:
        return "sin dependencias directas declaradas"
    clases = {d["clase"] for d in propias}
    peor = next(c for c in _ORDEN if c in clases)
    marcadas = [d["paquete"] for d in propias if d["clase"] == peor] if peor != "permisiva" else []
    return peor if not marcadas else f"{peor} ({', '.join(marcadas[:3])})"


def filas(motores: List[dict], atest_reg: Dict[str, dict], datos: dict, deps: List[Dict[str, str]]) -> List[Dict[str, str]]:
    por_id = {m["id"]: m for m in motores}
    resultado = []
    ids_atestados = set()
    for s in datos["subsistemas"]:
        trl = s.get("trl")
        m = por_id.get(s.get("motor", ""))
        paquetes = s.get("paquetes") or ([m["paquete"]] if m else [])
        pruebas = sum(reg._contar_pruebas(RAIZ / "packages" / p / "tests") for p in paquetes)
        en_ci = all(p in EN_MATRIZ for p in paquetes) if paquetes else False
        if m:
            ids_atestados.add(m["id"])
            c4 = (atest_reg.get(m["id"], {}).get("condicion_4") or {}).get("valor")
            operacion = "en producción verificado" if c4 is True else ("no desplegado" if c4 is False else "?")
            calidad = f"{pruebas} pruebas · CI {'sí' if en_ci else 'no'} · contrato/422/límite {'sí' if m['condicion_3'] else 'no'}"
        else:
            op = s.get("operacion")
            operacion = op["estado"] if op else "?"
            calidad = f"{pruebas} pruebas · CI {'sí' if en_ci else 'no'}" + (f" · {s['ci_extra']}" if s.get("ci_extra") else "")
        resultado.append({
            "nombre": s["nombre"], "trl": f"TRL {trl['valor']}" if trl else "?",
            "calidad": calidad, "operacion": operacion,
            "licencias": _peor_licencia([f"packages/{p}" for p in paquetes] + (["apps/api"] if s["id"] == "corpus-rag" else []), deps),
            "evidencia": (trl["evidencia"] + " **Límite:** " + trl["limite"]) if trl else "Sin atestar.",
        })
    for mid in datos.get("motores_sin_atestar", []):
        m = por_id.get(mid)
        if not m:
            continue
        pruebas = sum(reg._contar_pruebas(RAIZ / "packages" / m["paquete"] / "tests") for _ in [0])
        resultado.append({
            "nombre": f"Motor `{mid}`", "trl": "?",
            "calidad": f"{pruebas} pruebas · CI {'sí' if m['paquete'] in EN_MATRIZ else 'no'} · contrato/422/límite {'sí' if m['condicion_3'] else 'no'}",
            "operacion": "?", "licencias": _peor_licencia([f"packages/{m['paquete']}"], deps), "evidencia": "Sin atestar.",
        })
    return resultado


EN_MATRIZ = reg.paquetes_en_matriz()


def renderizar() -> str:
    datos = json.loads(ENTRADA.read_text(encoding="utf-8"))
    motores, atest_reg, deps = reg.descubrir(), reg.cargar_atestaciones(), lic.recolectar()
    tabla = ["| Subsistema | TRL (autoevaluado) | Calidad de software | Operación | Licencias (dependencias directas) |", "|---|---|---|---|---|"]
    detalle = []
    for f in filas(motores, atest_reg, datos, deps):
        tabla.append(f"| {f['nombre']} | {f['trl']} | {f['calidad']} | {f['operacion']} | {f['licencias']} |")
        if f["evidencia"] != "Sin atestar.":
            detalle.append(f"**{f['nombre']}.** {f['evidencia']}")
    return "\n".join([
        "# Matriz de madurez por subsistema",
        "",
        "Generado por `scripts/inventario/matriz_madurez.py`; no editar a mano. No existe una nota única de «madurez»: cada columna sale de una "
        "fuente distinta y se lee por separado.",
        "",
        "- **TRL**: escala de niveles de madurez tecnológica. Es **autoevaluado**, sin revisión externa; cada valor lleva su evidencia y el límite "
        "que impide subir. «?» = sin atestar (no significa que cumpla).",
        "- **Calidad**: se calcula del repositorio: funciones de prueba, presencia en la matriz de CI y, en motores, contrato `ResultadoMotor`, "
        "fallo explícito 422 y límite de tasa. **No se publica porcentaje de cobertura porque no se mide hoy.**",
        "- **Operación**: «en producción verificado» exige revisión de Cloud Run y llamada real registradas (ver [REGISTRO_MOTORES.md](REGISTRO_MOTORES.md)).",
        "- **Licencias**: la peor clasificación entre las dependencias directas del subsistema ([LICENCIAS_DEPENDENCIAS.md](LICENCIAS_DEPENDENCIAS.md)).",
        "",
        *tabla,
        "",
        "## Evidencia y límites de los TRL atestados",
        "",
        "\n\n".join(detalle) if detalle else "Ninguno atestado.",
        "",
        "## Qué no se publica, y por qué",
        "",
        "- **Un único badge de madurez o de TRL**: comprime evidencias de naturaleza distinta y no se puede verificar en vivo.",
        "- **Porcentaje de cobertura de pruebas**: no hay medición; un número sin medir sería una afirmación sin sustento.",
        "- **«Seguridad» o «calidad» como sello**: lo comprobable es el estado de alertas de dependencias, la auditoría de CI y las revisiones adversarias documentadas, no un sello.",
        "- **TRL 7 o superior**: exige operación por terceros medida y revisión técnica independiente; hoy no existen.",
        "",
    ])


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verificar", action="store_true")
    args = ap.parse_args(argv)
    texto = renderizar()
    if args.verificar:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != texto:
            print("docs/MATRIZ_MADUREZ.md está desactualizado: ejecute scripts/inventario/matriz_madurez.py", file=sys.stderr)
            return 1
        return 0
    SALIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{SALIDA.relative_to(RAIZ)} escrito")
    return 0


if __name__ == "__main__":
    sys.exit(main())
