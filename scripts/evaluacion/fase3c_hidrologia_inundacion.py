"""Fase 3c (issue #64): densidad de estaciones IDEAM vs eventos reales de
inundacion/creciente subita/avenida torrencial (UNGRD).

Deliberadamente NO repite el error de Fase 1b (#61): en vez de agregar
precipitacion cruda (lecturas incrementales sin validar, con huecos
reales de cobertura), usa CONTEO de estaciones IDEAM activas por
municipio como proxy de exposicion/monitoreo hidrologico -- un dato
categorico simple (cuantas estaciones existen), no requiere agregacion
temporal ni sufre el problema de completitud que bloqueo la precipitacion."""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rag_multi_norma as rm
import ideam_client
from _utils_zona_muda import construir_universos, grupo_alto_top_n
from scipy.stats import mannwhitneyu
import statistics

TAM_PAGINA = 1000
EVENTOS_INUNDACION = {"INUNDACION", "INUNDACIÓN", "INUNDACIoN", "CRECIENTE SUBITA", "Creciente Subita", "AVENIDA TORRENCIAL"}


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


def rank_biserial(x, y, alternative="two-sided"):
    u, p = mannwhitneyu(x, y, alternative=alternative)
    r = 1 - (2 * u) / (len(x) * len(y))
    return u, p, r


def main() -> None:
    print("=== Cargando eventos reales UNGRD (para inundación + filtro zona muda) ===")
    todos_eventos = _paginar("ungrd_emergencias", "municipio,departamento,evento")
    print(f"Total eventos: {len(todos_eventos)}")

    municipios_con_algun_evento, grupo_bajo_claves, conteo_inundacion = construir_universos(
        todos_eventos, EVENTOS_INUNDACION
    )
    print(f"Total eventos de inundación/creciente/avenida: {sum(conteo_inundacion.values())}")
    print(f"Municipios distintos con al menos 1 de estos eventos: {len(conteo_inundacion)}")

    top15_inundacion = grupo_alto_top_n(conteo_inundacion, n=15)

    print("\n=== Contando estaciones IDEAM reales por municipio (catálogo completo, paginado) ===")
    estaciones = []
    inicio = 0
    while True:
        pagina = ideam_client._get(
            ideam_client.DATASETS["estaciones"],
            {"$select": "municipio,departamento,categoria", "$limit": TAM_PAGINA, "$offset": inicio},
        )
        estaciones.extend(pagina)
        if len(pagina) < TAM_PAGINA:
            break
        inicio += TAM_PAGINA
    print(f"Total estaciones reales en el catálogo: {len(estaciones)}")

    densidad_por_municipio: Counter = Counter()
    for e in estaciones:
        clave = (e.get("municipio") or "").strip().upper()
        if clave:
            densidad_por_municipio[clave] += 1

    print("\n=== Grupo ALTO (top 15 inundación) vs BAJO (0 inundación, pero reportan otras cosas) ===")
    print(f"Grupo ALTO: {len(top15_inundacion)} municipios")
    print(f"Grupo BAJO (0 inundación, filtro zona muda aplicado): {len(grupo_bajo_claves)} municipios")

    dens_alto = [densidad_por_municipio.get(m, 0) for m in top15_inundacion]
    dens_bajo = [densidad_por_municipio.get(m, 0) for m in grupo_bajo_claves]

    print(f"\nDensidad de estaciones -- ALTO: mediana={statistics.median(dens_alto):.1f}, media={statistics.mean(dens_alto):.2f}")
    print(f"Densidad de estaciones -- BAJO: mediana={statistics.median(dens_bajo):.1f}, media={statistics.mean(dens_bajo):.2f}")

    u, p, r = rank_biserial(dens_alto, dens_bajo, alternative="greater")
    print(f"\nMann-Whitney U (ALTO > BAJO) = {u:.1f}, p = {p:.4f}")
    print(f"r (rank-biserial) = {r:.4f}")
    if p < 0.05:
        print("RESULTADO: los municipios con más inundaciones SÍ tienen más estaciones IDEAM (mayor exposición/monitoreo hidrológico).")
    else:
        print("RESULTADO: no hay evidencia estadística suficiente de esa asociación.")

    print("\n=== Nota honesta sobre interpretación ===")
    print("Densidad de estaciones mide EXPOSICIÓN/MONITOREO hidrológico (cuántos cuerpos de")
    print("agua monitoreados hay cerca), no la magnitud real de precipitación/caudal --")
    print("un municipio con más estaciones también puede simplemente estar mejor monitoreado")
    print("en general (mismo tipo de sesgo de reporte ya visto en UNGRD), no necesariamente")
    print("tener más agua real. Se reporta como lo que es: un proxy de exposición, no de amenaza física directa.")

    import json
    out = {"dens_alto": dens_alto, "dens_bajo": dens_bajo, "top15_inundacion": top15_inundacion}
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase3c_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
