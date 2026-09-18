"""
Idea 6 del roadmap: CI de ingesta continua.

No re-extrae numerales del PDF fuente -- esos son gitignored, no viajan
con el checkout de CI (ver CLAUDE.md: "el documento fuente nunca se
versiona"). En su lugar compara la LISTA DE NUMERALES ya congelada en cada
baseline (scripts/ingesta/*/cobertura_baseline/*.json, generados a mano
con generar_baseline_cobertura.py cuando SÍ se tiene el PDF a mano) contra
el estado EN VIVO del corpus en Supabase. Si la cobertura de un título con
baseline BAJA respecto a cuando se generó ese archivo, algo rompió
cobertura que ya existía -- una migración, un borrado accidental, un
script con un bug -- y eso es justo lo que debe bloquear un merge.

Esto NO exige que todo el corpus esté al 100% (no lo está, ver
docs/fuentes-normativas.md: A/B/J siguen con huecos reales conocidos) --
exige que no siga bajando desde donde ya estaba. Títulos sin baseline
todavía simplemente no se verifican (opt-in progresivo, no retroactivo).

Ejecutar: python scripts/ingesta/verificar_cobertura_baseline.py
Sale con código 1 (falla el job de CI) si detecta una regresión real.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "rag-audit-kit"))

from dotenv import load_dotenv  # noqa: E402

from src import Numeral, comparar_cobertura  # noqa: E402

# Margen por redondeo/variación menor entre corridas (el mismo baseline
# recalculado dos veces con exactamente los mismos datos ya puede variar
# +/-0.1 por redondeo de porcentaje) -- NO es licencia para tolerar una
# regresión real, solo para no fallar por ruido de punto flotante.
TOLERANCIA_PCT = 0.5


def main() -> int:
    load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

    patron = str(PROJECT_ROOT / "scripts" / "ingesta" / "*" / "cobertura_baseline" / "*.json")
    archivos_baseline = sorted(glob.glob(patron))

    if not archivos_baseline:
        print("Sin baselines de cobertura todavía -- nada que verificar (opt-in progresivo).")
        return 0

    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    hubo_regresion = False
    for ruta in archivos_baseline:
        data = json.loads(Path(ruta).read_text(encoding="utf-8"))
        numerales = [Numeral(v, "") for v in data["numerales"]]

        res = (
            sb.table(data["tabla"])
            .select(data["columna_seccion"])
            .ilike(data["columna_seccion"], f"{data['prefijo_seccion']}%")
            .execute()
        )
        cubiertos = [r[data["columna_seccion"]] for r in res.data if r.get(data["columna_seccion"])]

        reporte = comparar_cobertura(numerales, cubiertos)
        baseline_pct = data["pct_cobertura_al_generar"]
        delta = round(reporte.pct_cobertura - baseline_pct, 1)

        estado = "OK"
        if reporte.pct_cobertura < baseline_pct - TOLERANCIA_PCT:
            estado = "REGRESION"
            hubo_regresion = True

        print(
            f"[{estado}] {data['titulo']}: baseline {baseline_pct}% -> actual "
            f"{reporte.pct_cobertura}% (delta {delta:+.1f}) -- {os.path.basename(ruta)}"
        )
        if estado == "REGRESION":
            print(f"  Faltantes nuevos respecto al baseline: {[n.valor for n in reporte.faltantes]}")

    if hubo_regresion:
        print(
            "\nCobertura real retrocedió respecto a un baseline ya guardado -- "
            "bloqueando. Si el retroceso es intencional (ej. se reemplazó un "
            "chunk resumen por otro verbatim con distinta sección), regenerar "
            "el baseline con generar_baseline_cobertura.py y commitearlo junto "
            "con el cambio."
        )
        return 1

    print("\nSin regresiones de cobertura detectadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
