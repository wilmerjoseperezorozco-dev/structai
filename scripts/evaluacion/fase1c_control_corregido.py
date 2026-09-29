"""Fase 1c (issue #61): corrige un sesgo real encontrado auditando el
grupo de control de Fase 1 -- 63.4% de los 593 municipios sin eventos de
MOVIMIENTO EN MASA tampoco tienen NINGUN reporte de NINGUN tipo en UNGRD
en 6 años (2019-2024). Eso no es evidencia de bajo riesgo real, es
evidencia de falta de reporte -- confunde "sin amenaza" con "sin
monitoreo/capacidad institucional para reportar", lo cual puede
correlacionar con terreno/acceso de forma independiente del riesgo real.

Grupo de control corregido: municipios que SI reportan algo a UNGRD
(confirmando que tienen capacidad de reporte activa) pero CERO eventos
de movimiento en masa especificamente -- comparacion mas valida que
"todos los municipios sin evento", que mezclaba zonas genuinamente
seguras con zonas mudas."""
import io
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rag_multi_norma as rm
from _utils_zona_muda import construir_universos, grupo_alto_top_n
from scipy.stats import chi2_contingency

TAM_PAGINA = 1000


def _paginar(tabla: str, columnas: str, filtro=None) -> list[dict]:
    filas = []
    inicio = 0
    while True:
        q = rm.sb.table(tabla).select(columnas).range(inicio, inicio + TAM_PAGINA - 1)
        if filtro is not None:
            q = filtro(q)
        pagina = q.execute().data or []
        filas.extend(pagina)
        if len(pagina) < TAM_PAGINA:
            break
        inicio += TAM_PAGINA
    return filas


def perfil_pendiente(municipio: str) -> Counter:
    filas = rm.sb.table("igac_suelos_ufh").select("pendiente").eq(
        "municipio_norm", municipio.upper()
    ).execute().data or []
    return Counter(f["pendiente"] for f in filas)


def main() -> None:
    print("=== Reconstruyendo universos reales ===")
    todos_eventos = _paginar("ungrd_emergencias", "municipio,evento", None)
    municipios_con_algun_evento, grupo_bajo_corregido, conteo_mm = construir_universos(
        todos_eventos, {"MOVIMIENTO EN MASA"}
    )

    # Solo para el print comparativo "antes/despues" -- NO alimenta grupo_bajo_corregido
    # (ese ya sale limpio de construir_universos(), sin cruzar contra esta tabla).
    # Nota real encontrada 2026-09-29 refactorizando este script: cruzar "universo" (con
    # tildes, ej. "ACANDÍ") contra conteo_mm (sin tildes, tal como los trae UNGRD) pierde
    # ~370 municipios reales por desajuste de tildes -- por eso grupo_bajo_corregido ya NO
    # depende de esta tabla, evita ese bug por diseño en vez de normalizar tildes aqui.
    todos_municipios = _paginar("sgc_amenaza_sismica_municipios", "municipio", None)
    universo = {(m["municipio"] or "").strip().upper() for m in todos_municipios}

    top15 = grupo_alto_top_n(conteo_mm, n=15)
    grupo_bajo_viejo = universo - set(conteo_mm)

    print(f"Grupo ALTO: {len(top15)} municipios")
    print(f"Grupo BAJO viejo (Fase 1, sin filtrar por reporte): {len(grupo_bajo_viejo)}")
    print(f"Grupo BAJO CORREGIDO (reportan algo, 0 movimiento en masa): {len(grupo_bajo_corregido)}")
    print(f"Descartados por 'zona muda' (0 reportes de ningún tipo): {len(grupo_bajo_viejo) - len(grupo_bajo_corregido)}")

    print("\n=== Perfil de pendiente: grupo ALTO ===")
    agg_alto = Counter()
    for muni in top15:
        agg_alto.update(perfil_pendiente(muni))

    print("=== Perfil de pendiente: grupo BAJO CORREGIDO (esto tarda un poco) ===")
    agg_bajo = Counter()
    for i, muni in enumerate(sorted(grupo_bajo_corregido)):
        agg_bajo.update(perfil_pendiente(muni))
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(grupo_bajo_corregido)}")

    total_alto = sum(agg_alto.values())
    total_bajo = sum(agg_bajo.values())
    letras = "abcdefg"
    print(f"\nGrupo ALTO: {total_alto} polígonos")
    for letra in letras:
        pct = 100 * agg_alto.get(letra, 0) / total_alto if total_alto else 0
        print(f"  {letra}: {pct:5.1f}%")
    print(f"\nGrupo BAJO corregido: {total_bajo} polígonos")
    for letra in letras:
        pct = 100 * agg_bajo.get(letra, 0) / total_bajo if total_bajo else 0
        print(f"  {letra}: {pct:5.1f}%")

    empinado_alto = 100 * (agg_alto.get("f", 0) + agg_alto.get("g", 0)) / total_alto
    empinado_bajo = 100 * (agg_bajo.get("f", 0) + agg_bajo.get("g", 0)) / total_bajo
    print(f"\nPendiente empinada (f+g): ALTO {empinado_alto:.1f}% vs BAJO corregido {empinado_bajo:.1f}%")
    print(f"Ratio: {empinado_alto/empinado_bajo:.2f}x")

    tabla = [
        [agg_alto.get(l, 0) for l in letras],
        [agg_bajo.get(l, 0) for l in letras],
    ]
    chi2, p, gl, _ = chi2_contingency(tabla)
    import math
    n = total_alto + total_bajo
    v = math.sqrt(chi2 / (n * 1))
    print(f"\nChi-cuadrado = {chi2:.2f}, gl={gl}, p={p:.2e}")
    print(f"Cramér's V = {v:.4f}")


if __name__ == "__main__":
    main()
