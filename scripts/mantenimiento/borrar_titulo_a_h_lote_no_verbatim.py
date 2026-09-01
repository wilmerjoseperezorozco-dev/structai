"""
Borra 28 chunks de nsr10_chunks (15 en Título A, 13 en Título H) que
NO son verbatim -- son resúmenes parafraseados en estilo "apuntes de
estudio" (ej. "NSR-10 A.1 Alcance: Reglamento obligatorio para todas
las edificaciones nuevas en Colombia...", "Ecuación H.5-1 NSR-10
Capacidad portante última Terzaghi: qult=c*Nc*sc*dc*ic+...") escritos
con la prefijo de id `<Letra>-SEC<N>-*` (heurística de lote sospechoso
ya documentada en CLAUDE.md desde antes de esta sesión).

Encontrado y confirmado real 2026-09-01: no es solo un formato de id
viejo -- comparado con el estilo real de NSR-10 (formal, redacción
exacta del reglamento, confirmado en las decenas de chunks verbatim
reales ingestados hoy mismo en F.4.2-F.4.5), este lote es un resumen
condensado que presenta valores y ecuaciones como si fueran el texto
oficial sin serlo -- riesgo real para una herramienta que vende
"trazabilidad normativa": un ingeniero podría recibir una aproximación
parafraseada creyendo que es la norma exacta.

Decisión del usuario 2026-09-01: borrar ahora (deja un hueco real y
honesto en A.1-A.9 y H.1-H.7 hasta que se reingesten en verbatim real
desde el PDF oficial, en vez de dejar contenido potencialmente
impreciso presentado como autoritativo).

Uso: python borrar_titulo_a_h_lote_no_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")


def main():
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    # Confirmar antes de borrar: traer los ids reales que matchean el patrón.
    existentes = (
        sb.table("nsr10_chunks")
        .select("id")
        .filter("id", "match", "^[A-Z]-SEC[0-9]")
        .execute()
    )
    ids = [row["id"] for row in existentes.data]
    print(f"Chunks encontrados con el patrón <Letra>-SEC<N>-*: {len(ids)}")
    for i in sorted(ids):
        print(f"  {i}")

    if not ids:
        print("Nada que borrar -- ya no hay chunks con ese patrón.")
        return

    print(f"\nBorrando {len(ids)} chunks...")
    sb.table("nsr10_chunks").delete().in_("id", ids).execute()

    print(f"\nOK: {len(ids)} chunks no-verbatim borrados de nsr10_chunks.")


if __name__ == "__main__":
    main()
