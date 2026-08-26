"""
REEMPLAZA la tabla `peru_e030_zonificacion_distrital` (Anexo II —
Zonificación Sísmica por distrito) con el dataset 2026, verificado de
forma REAL y COMPLETA -- no una muestra -- contra el texto oficial de
la RM 183-2026-VIVIENDA ("El Peruano", Separata Especial, 3-may-2026).

METODOLOGÍA (documentada en detalle porque este fue el trabajo más
grande de toda la reingesta gradual de Perú -- ver issue #13 y
[[project_structai_replicabilidad_paises]] en la memoria del proyecto):

1. El Anexo II 2026 cambió de formato respecto a 2019: en vez de una
   lista plana distrito-por-distrito, agrupa por PROVINCIA con
   "TODOS LOS DISTRITOS" (uniforme) o excepciones nombradas -- mucho
   más compacto, pero con artefactos de extracción de PDF genuinamente
   complejos (el marcador de zona aparece pegado al PRIMER distrito de
   su grupo en la extracción lineal, no al final; nombres de provincia
   y distrito a veces partidos en 2-3 líneas; departamentos y
   provincias que comparten nombre con su propia capital homónima
   causan colisiones reales).

2. Se construyó un parser en Python (`scripts/ingesta/peru_e030/
   reemplazo_2026/` en el scratchpad de la sesión, no versionado --
   herramienta de una sola vez, no parte del pipeline de ingesta
   permanente) usando el paquete `ubigeos-peru` (datos oficiales INEI)
   como ancla para desambiguar departamento/provincia/distrito. Tras
   7 rondas de depuración de bugs reales (alias sin normalizar,
   encabezado especial de Callao como "Provincia Constitucional",
   departamento+provincia homónimos glued en una línea, marcador de
   zona partido en 3 líneas, filtro de números de página demasiado
   agresivo que borraba dígitos de zona sueltos, fusión de nombres de
   distrito largos partidos en 2 líneas, y auto-colisión de
   departamento con su propia provincia capital), el parser validó
   automáticamente contra INEI ~170 de las 196 provincias.

3. Las ~33 provincias restantes (con fallas de parseo genuinas por
   colisiones de nombres -- ej. "Bolognesi" es nombre de una provincia
   de Áncash Y TAMBIÉN de un distrito dentro de la provincia Pallasca)
   se transcribieron a mano leyendo directamente las páginas reales del
   PDF oficial (páginas 31-66), verificando cada conteo declarado
   ("TODOS LOS DISTRITOS", o un número exacto como "DIECINUEVE
   DISTRITOS") contra los nombres realmente listados.

4. Resultado: dataset de 1.884 filas, cubriendo las 196 provincias
   oficiales de Perú (25 departamentos/regiones + Callao), sin huecos,
   sin duplicados.

5. Comparado explícitamente contra los 1.851 registros de la edición
   2019 ya cargada (normalizando mayúsculas/tildes/puntuación para la
   comparación): de 1.732 distritos con clave coincidente entre ambas
   ediciones, solo 3 tienen un cambio REAL de zona sísmica -- los 3
   en la provincia de Aija (Áncash): La Merced, Huacllán y Succha
   bajaron de zona 4 a zona 3. Confirmado visualmente contra la página
   35 del PDF oficial (la provincia Aija completa es zona 3, "TODOS
   LOS DISTRITOS"). El resto de discrepancias de nombres encontradas
   en la comparación (ej. "TNTE. CESAR LOPEZ ROJAS" vs "TENIENTE CESAR
   LOPEZ ROJAS", "CARLOS F. FITZCARRALD" vs "CARLOS FERMIN
   FITZCARRALD") son variantes de escritura/abreviación, no cambios de
   zona -- verificado explícitamente, no asumido.

ESTRATEGIA DE REEMPLAZO: TRUNCATE + INSERT completo (no upsert
incremental) -- la tabla es una tabla de consulta exacta (lookup), no
un log histórico, y el dataset nuevo es una reconstrucción completa
verificada, no un parche parcial.

Nota de formato: los nombres se guardan en mayúscula/minúscula normal
con tildes (ej. "Chachapoyas", no "CHACHAPOYAS") -- mejora respecto a
la convención todo-mayúsculas de la carga 2019, porque estos campos se
interpolan directamente en las respuestas del LLM
(`pais_zonificacion.formatear_dato_peru()`) y se leen mejor en una
oración en español. La búsqueda exacta por distrito sigue funcionando
igual porque `_normalizar()` en pais_zonificacion.py ya quita
tildes/mayúsculas al indexar, independientemente de cómo se guarde el
dato.

Uso: python scripts/ingesta/peru_e030/reemplazo_2026/reemplaza_anexo2_zonificacion_distrital.py [--dry-run]
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

# Dataset final ensamblado en el scratchpad de la sesión (parser +
# transcripción manual verificada). Se copia aquí como JSON embebido
# para que este script sea reproducible sin depender de archivos
# temporales fuera del repo.
DATASET_PATH = Path(__file__).resolve().parent / "anexo2_2026_dataset.json"


def reemplazar(dry_run: bool = False):
    with open(DATASET_PATH, encoding="utf-8") as f:
        filas_crudas = json.load(f)

    rows = [
        {"region": dep, "provincia": prov, "distrito": dist, "zona_sismica": zona}
        for dep, prov, dist, zona in filas_crudas
    ]

    print(f"Filas a insertar: {len(rows)}")
    provincias = {(r["region"], r["provincia"]) for r in rows}
    print(f"Provincias distintas: {len(provincias)}")

    # Validaciones basicas antes de tocar produccion
    zonas_invalidas = [r for r in rows if r["zona_sismica"] not in (1, 2, 3, 4)]
    if zonas_invalidas:
        print(f"ABORTADO: {len(zonas_invalidas)} filas con zona_sismica invalida.")
        return
    vacios = [r for r in rows if not r["region"] or not r["provincia"] or not r["distrito"]]
    if vacios:
        print(f"ABORTADO: {len(vacios)} filas con campo vacio.")
        return

    if dry_run:
        print("[dry-run] No se modifica Supabase.")
        return

    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    sb = create_client(supabase_url, supabase_key)

    antes = sb.table("peru_e030_zonificacion_distrital").select("id", count="exact").execute()
    print(f"Filas actuales en la tabla (edicion 2019): {antes.count}")

    # TRUNCATE real: borrar todo por id != 0 (no hay id=0 valido, borra todo)
    sb.table("peru_e030_zonificacion_distrital").delete().neq("id", 0).execute()

    # Insertar en lotes de 500 (limite practico del cliente supabase-py)
    LOTE = 500
    for i in range(0, len(rows), LOTE):
        lote = rows[i:i + LOTE]
        sb.table("peru_e030_zonificacion_distrital").insert(lote).execute()
        print(f"  insertadas {min(i + LOTE, len(rows))}/{len(rows)}")

    despues = sb.table("peru_e030_zonificacion_distrital").select("id", count="exact").execute()
    print(f"OK: tabla reemplazada. Filas nuevas (edicion 2026): {despues.count}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    reemplazar(dry_run=dry)
