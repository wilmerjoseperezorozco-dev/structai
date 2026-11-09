"""Barrido de regresión (regla 1): ningún motor puede sustituir en silencio un dato físico con `.get(clave, número)`.

Las excepciones permitidas son usos que no sustituyen un dato de ingeniería (ausencia legítima de carga, texto de
presentación en PDF). Cada una está justificada. Una aparición nueva hace fallar la prueba.
"""
import re
from pathlib import Path

PAQUETES = Path(__file__).resolve().parents[2]
PATRON = re.compile(r"\.get\([^()]*,\s*-?[0-9]+(\.[0-9]+)?\)")

PERMITIDOS = {
    ("motor-analisis/src/portico.py", 'q_local.get(idx, 0.0)'): "un elemento sin carga distribuida tiene carga 0",
    ("motor-concreto/src/excavacion_estabilidad.py", 'kw.get("kh", 0.0)'): "sin kh explícito el cálculo es estático; el selector exige kh coherente con el sismo",
}
PREFIJO_PERMITIDO = {
    "motor-aquai/src/pdf_memoria.py": "texto de presentación del informe PDF, no un dato de cálculo",
}


def _apariciones():
    for f in sorted(PAQUETES.glob("motor-*/src/*.py")):
        rel = f.relative_to(PAQUETES).as_posix()
        for n, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if linea.lstrip().startswith("#"):
                continue
            m = PATRON.search(linea)
            if m:
                yield rel, n, linea.strip()


def test_no_hay_get_con_valor_numerico_por_defecto_fuera_de_la_lista_permitida():
    nuevas = []
    for rel, n, linea in _apariciones():
        if rel in PREFIJO_PERMITIDO:
            continue
        if any(rel == r and frag in linea for (r, frag) in PERMITIDOS):
            continue
        nuevas.append(f"{rel}:{n}: {linea}")
    assert not nuevas, "Fallback numérico silencioso (regla 1 de REGLAS_MOTORES_DE_CALCULO.md):\n" + "\n".join(nuevas)
