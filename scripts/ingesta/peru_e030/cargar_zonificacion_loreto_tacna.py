"""
Carga PRUEBA DE CONCEPTO del Anexo II de la E.030 (Perú) -- listado
oficial de zona sísmica por región/provincia/distrito -- en la tabla
peru_e030_zonificacion_distrital.

A diferencia de los insert_capituloN_*.py (texto narrativo, chunks para
RAG semántico con embeddings), este es un dato de CONSULTA EXACTA: no
tiene sentido "buscar semánticamente" a qué zona pertenece un distrito,
se necesita un lookup directo por nombre. Por eso va a una tabla
relacional propia, sin columna de embedding -- mismo patrón que
sisben_vulnerabilidad_vivienda_municipio en el lado colombiano.

ALCANCE HONESTO de esta carga (decisión explícita del usuario,
2026-08-24, no un recorte silencioso): el Anexo II completo son 40
páginas del PDF oficial del MVCS (~1.874 distritos en las ~24 regiones
del Perú). Transcribir todo a mano en una sola sesión tenía riesgo real
de error de tipeo a esa escala. Se cargan solo las 2 regiones ya
capturadas del PDF como prueba de concepto:

- TACNA: las 4 provincias COMPLETAS (Tarata, Candarave, Jorge Basadre,
  Tacna) -- 27 distritos, confirmado completo porque es la última página
  del documento (con espacio en blanco después, sin continuar).
- LORETO: 5 provincias (Mariscal Ramón Castilla, Maynas, Requena, Loreto,
  Alto Amazonas) -- PARCIAL, Loreto tiene más provincias (Datem del
  Marañón, Putumayo, Ucayali) que no se capturaron todavía porque
  quedaron en páginas siguientes del PDF no leídas.

Las ~22 regiones restantes (~1.850 distritos) quedan pendientes para una
sesión futura -- ver project_structai_replicabilidad_paises.md en la
memoria del proyecto para el detalle completo.

Uso: python scripts/ingesta/peru_e030/cargar_zonificacion_loreto_tacna.py [--dry-run]
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


def _filas(region: str, provincia: str, zona: int, ambito: str, distritos: list[str]) -> list[dict]:
    return [
        {
            "region": region,
            "provincia": provincia,
            "distrito": d,
            "zona_sismica": zona,
            "ambito": ambito,
        }
        for d in distritos
    ]


FILAS: list[dict] = []

# ── LORETO (parcial -- 5 de 8 provincias, ver nota de alcance arriba) ───────
FILAS += _filas("LORETO", "MARISCAL RAMÓN CASTILLA", 1, "TODOS LOS DISTRITOS",
                 ["RAMÓN CASTILLA", "PEBAS", "SAN PABLO", "YAVARÍ"])
FILAS += _filas("LORETO", "MAYNAS", 1, "TODOS LOS DISTRITOS",
                 ["ALTO NANAY", "BELÉN", "FERNANDO LORES", "INDIANA", "IQUITOS",
                  "LAS AMAZONAS", "MAZÁN", "NAPO", "PUNCHANA", "PUTUMAYO",
                  "SAN JUAN BAUTISTA", "TNTE. MANUEL CLAVERO", "TORRES CAUSANA"])
FILAS += _filas("LORETO", "REQUENA", 1, "UN DISTRITO", ["SAQUENA"])
FILAS += _filas("LORETO", "REQUENA", 2, "DIEZ DISTRITOS",
                 ["REQUENA", "CAPELO", "SOPLÍN", "TAPICHE", "JENARO HERRERA",
                  "YAQUERANA", "ALTO TAPICHE", "EMILIO SAN MARTÍN", "MAQUÍA", "PUINAHUA"])
FILAS += _filas("LORETO", "LORETO", 2, "TODOS LOS DISTRITOS",
                 ["NAUTA", "PARINARI", "TIGRE", "TROMPETEROS", "URARINAS"])
FILAS += _filas("LORETO", "ALTO AMAZONAS", 2, "UN DISTRITO", ["LAGUNAS"])
FILAS += _filas("LORETO", "ALTO AMAZONAS", 3, "CINCO DISTRITOS",
                 ["YURIMAGUAS", "BALSAPUERTO", "JEBEROS", "SANTA CRUZ", "TNTE. CÉSAR LÓPEZ ROJAS"])

# ── TACNA (completa -- las 4 provincias, última página del PDF) ────────────
FILAS += _filas("TACNA", "TARATA", 3, "TODOS LOS DISTRITOS",
                 ["CHUCATAMANI", "ESTIQUE", "ESTIQUE-PAMPA", "SITAJARA",
                  "SUSAPAYA", "TARATA", "TARUCACHI", "TICACO"])
FILAS += _filas("TACNA", "CANDARAVE", 3, "TODOS LOS DISTRITOS",
                 ["CAIRANI", "CAMILACA", "CANDARAVE", "CURIBAYA", "HUANUARA", "QUILAHUANI"])
FILAS += _filas("TACNA", "JORGE BASADRE", 4, "TODOS LOS DISTRITOS",
                 ["ILABAYA", "ITE", "LOCUMBA"])
FILAS += _filas("TACNA", "TACNA", 3, "UN DISTRITO", ["PALCA"])
FILAS += _filas("TACNA", "TACNA", 4, "NUEVE DISTRITOS",
                 ["ALTO DE LA ALIANZA", "CALANA", "CIUDAD NUEVA", "INCLÁN", "PACHIA",
                  "POCOLLAY", "SAMA", "TACNA", "LA YARADA LOS PALOS"])


def cargar(dry_run: bool = False):
    print(f"{len(FILAS)} filas a cargar (Loreto parcial + Tacna completa).")
    por_region: dict[str, int] = {}
    for f in FILAS:
        por_region[f["region"]] = por_region.get(f["region"], 0) + 1
    for region, n in por_region.items():
        print(f"  {region}: {n} distritos")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)
    sb.table("peru_e030_zonificacion_distrital").upsert(
        FILAS, on_conflict="region,provincia,distrito"
    ).execute()
    print(f"OK: {len(FILAS)} filas insertadas/actualizadas en peru_e030_zonificacion_distrital.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    cargar(dry_run=dry)
