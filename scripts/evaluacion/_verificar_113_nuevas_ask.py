"""
Verificación real contra ask() de las 113 preguntas agregadas al
dataset el 2026-09-07 SIN verificar en vivo (prefijos H-H9-, H-H10-,
A-A33-, SINT2-, ADV2-, COLOQ2-, COMP2-) -- pendiente documentado en el
propio dataset_baseline_nsr10.py y en memoria privada.

Para cada pregunta: llama a ask() real, extrae candidatos numéricos
del ground_truth (regex), y marca AUTO-PASS si alguno aparece en la
respuesta real, AUTO-FAIL si no. Las adversariales (ADV2-) no tienen
número que buscar -- se marcan NO-AUTO (requieren lectura manual para
juzgar si el sistema inventó contenido o admitió honestamente que no
sabe).

Guarda un JSON completo (pregunta/ground_truth/respuesta/veredicto)
para poder leer cada caso después, sin tener que volver a llamar a
ask() (costoso en tiempo/cuota).

Uso: python _verificar_113_nuevas_ask.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "api"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag_multi_norma import ask  # noqa: E402
from dataset_baseline_nsr10 import CASOS_BASELINE  # noqa: E402

PREFIJOS_NUEVOS = ("H-H9-", "H-H10-", "A-A33-", "SINT2-", "ADV2-", "COLOQ2-", "COMP2-")

NUM_RE = re.compile(
    r"\d+[.,]?\d*\s?(?:%|por ciento|porciento|MPa|kPa|kN/m2|kN/m²|kN|mm|m²|m2|"
    r"°|grados|kg|kgf|kgf/mm2|kgf/mm²|L/s|golpes/pie|golpes|años|horas|veces|"
    r"m(?![a-zA-Z]))"
)


def extraer_candidatos(ground_truth: str) -> list[str]:
    crudos = NUM_RE.findall(ground_truth)
    candidatos = set()
    for c in crudos:
        c = c.strip()
        candidatos.add(c)
        candidatos.add(c.replace(",", "."))
        candidatos.add(c.replace(".", ","))
        # también el número solo, sin unidad, por si la respuesta cambia unidad
        solo_num = re.match(r"[\d.,]+", c)
        if solo_num:
            candidatos.add(solo_num.group())
    return sorted(candidatos)


def main():
    casos = [c for c in CASOS_BASELINE if c["id"].startswith(PREFIJOS_NUEVOS)]
    print(f"Total a verificar: {len(casos)}")

    resultados = []
    for i, caso in enumerate(casos, start=1):
        print(f"[{i}/{len(casos)}] {caso['id']}")
        t0 = time.time()
        try:
            r = ask(caso["pregunta"])
            respuesta = r.get("respuesta", str(r)) if isinstance(r, dict) else str(r)
            error = None
        except Exception as e:  # noqa: BLE001
            respuesta = ""
            error = str(e)
        dt = time.time() - t0

        es_adversarial = caso["id"].startswith("ADV2-")
        if es_adversarial:
            veredicto = "NO-AUTO (adversarial, requiere lectura manual)"
        elif error:
            veredicto = "ERROR"
        else:
            candidatos = extraer_candidatos(caso["ground_truth"])
            encontrado = any(c and c.lower() in respuesta.lower() for c in candidatos)
            veredicto = "AUTO-PASS" if encontrado else "AUTO-FAIL"

        resultados.append({
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "ground_truth": caso["ground_truth"],
            "respuesta": respuesta,
            "error": error,
            "veredicto": veredicto,
            "tiempo_s": round(dt, 1),
        })
        print(f"    -> {veredicto} ({dt:.1f}s)")

        # Guardado incremental -- si algo falla a mitad de camino (rate limit,
        # etc.) no se pierde lo ya corrido.
        out_path = Path(__file__).resolve().parent / "resultados_113_nuevas.json"
        out_path.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    n_pass = sum(1 for r in resultados if r["veredicto"] == "AUTO-PASS")
    n_fail = sum(1 for r in resultados if r["veredicto"] == "AUTO-FAIL")
    n_adv = sum(1 for r in resultados if r["veredicto"].startswith("NO-AUTO"))
    n_err = sum(1 for r in resultados if r["veredicto"] == "ERROR")
    print(f"\nResumen: {n_pass} AUTO-PASS, {n_fail} AUTO-FAIL, {n_adv} adversariales (manual), {n_err} ERROR de {len(resultados)}")


if __name__ == "__main__":
    main()
