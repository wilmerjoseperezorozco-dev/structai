"""
Contrato motor -> numeral (issue #186, Fase 0 del plan de huecos).

Todo numeral de la NSR-10 que un motor determinista cita en su código debe
tener su texto en el corpus, para que el usuario pueda verificar el cálculo
contra la norma dentro de StructAI ("honestidad de fuente siempre verificable",
CLAUDE.md).

Se valida contra el índice numeral -> chunks construido a partir de los
encabezados del texto (scripts/evaluacion/golden/e5_grafo/indice_numerales.py),
no contra la columna `seccion`: un chunk contiene varios numerales como
encabezados, y comparar solo contra `seccion` hizo creer que faltaban numerales
que sí estaban (2026-11-11). No consulta Supabase: corre en el CI de GitHub.
Si se ingiere contenido nuevo, regenerar el índice.

Un numeral se considera resuelto si:
  - tiene encabezado propio en el índice (exacta), o
  - es un capítulo o sección cuyos subnumerales están en el índice, o
  - un ancestro de al menos tres niveles (p. ej. C.11.2) tiene encabezado.

Ejecutar: pytest apps/api/tests/test_contrato_motor_numerales.py -v
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
INDICE = RAIZ / "scripts" / "evaluacion" / "golden" / "e5_grafo" / "indice_numerales_nsr10.json"
RE_NUMERAL = re.compile(r"\b([A-K])\.(\d+(?:\.\d+)*)\b")

# Motores cuyos numerales son de OTRA norma (las letras se repiten entre normas).
MOTORES_OTRA_NORMA = {
    "motor-aquai": "RAS 2000 / Res. 0330 (B.7, D.3.5... no son numerales de la NSR-10)",
}
# Referencias puntuales a otras normas dentro de motores NSR-10, con su justificación.
EXCEPCIONES = {
    ("motor-estructural", "E.031"): "NTE E.031 de Perú (aislamiento sísmico, Tabla N.5), no el Título E de la NSR-10",
}


def _motores():
    for d in sorted((RAIZ / "packages").glob("motor-*")):
        if d.name not in MOTORES_OTRA_NORMA and (d / "src").exists():
            yield d


def _numerales(motor_dir: Path) -> set[str]:
    return {f"{m.group(1)}.{m.group(2)}"
            for f in (motor_dir / "src").rglob("*.py")
            for m in RE_NUMERAL.finditer(f.read_text(encoding="utf-8", errors="ignore"))}


@pytest.fixture(scope="module")
def indice() -> set[str]:
    if not INDICE.exists():
        pytest.skip(f"Falta el índice {INDICE.name}; regenerarlo con indice_numerales.py")
    return set(json.loads(INDICE.read_text(encoding="utf-8")))


def _resuelto(n: str, indice: set[str]) -> bool:
    if n in indice or any(k.startswith(n + ".") for k in indice):
        return True
    partes = n.split(".")
    return any(".".join(partes[:i]) in indice for i in range(len(partes) - 1, 2, -1))


@pytest.mark.parametrize("motor_dir", list(_motores()), ids=lambda d: d.name)
def test_numerales_citados_por_el_motor_estan_en_el_corpus(motor_dir, indice):
    faltantes = sorted(n for n in _numerales(motor_dir)
                       if (motor_dir.name, n) not in EXCEPCIONES and not _resuelto(n, indice))
    assert not faltantes, (
        f"{motor_dir.name} cita numerales NSR-10 sin texto en el corpus: {faltantes}. "
        "Ingerirlos (ver scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md) o, si son de otra norma, "
        "agregarlos a EXCEPCIONES con su justificación."
    )


def test_excepciones_siguen_vigentes():
    """Una excepción que ya no aparece en el código es basura: se borra."""
    for (motor, numeral), motivo in EXCEPCIONES.items():
        assert numeral in _numerales(RAIZ / "packages" / motor), f"Excepción obsoleta: {motor} ya no cita {numeral} ({motivo})"
