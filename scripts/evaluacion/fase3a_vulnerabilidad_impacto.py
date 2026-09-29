"""Fase 3a (issue #62): vulnerabilidad de vivienda (Sisben IV) -> impacto
real NORMALIZADO POR EVENTO (UNGRD) -- primera pregunta que prueba el
componente de VULNERABILIDAD del marco (amenaza+exposicion+vulnerabilidad+
impacto), no solo amenaza fisica.

Por que normalizado por evento: un municipio con mas eventos tiene mas
dano acumulado sin que la vulnerabilidad de vivienda importe -- dividir
por n_eventos aisla si la vulnerabilidad hace que CADA evento sea peor,
que es la pregunta real.

Aplica el mismo filtro de "zona muda" ya validado en el issue #61 --
municipios sin ningun reporte a UNGRD se descartan del grupo de
comparacion, no se cuentan como "impacto cero real"."""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import rag_multi_norma as rm
from scipy.stats import mannwhitneyu
import statistics

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


def rank_biserial(x, y, alternative="two-sided"):
    u, p = mannwhitneyu(x, y, alternative=alternative)
    r = 1 - (2 * u) / (len(x) * len(y))
    return u, p, r


def main() -> None:
    print("=== Cargando Sisbén (vulnerabilidad de vivienda) ===")
    sisben = _paginar(
        "sisben_vulnerabilidad_vivienda_municipio",
        "municipio,departamento,pct_material_vulnerable,n_viviendas_muestra",
    )
    print(f"Municipios con dato Sisbén: {len(sisben)}")

    print("\n=== Cargando eventos reales UNGRD (todos los tipos, para impacto y filtro de zona muda) ===")
    eventos = _paginar(
        "ungrd_emergencias",
        "municipio,departamento,fallecidos,viviendas_destruidas,viviendas_averiadas",
    )
    print(f"Total eventos UNGRD: {len(eventos)}")

    impacto_por_municipio: dict[str, dict] = {}
    for e in eventos:
        clave = (e["municipio"] or "").strip().upper()
        if not clave:
            continue
        d = impacto_por_municipio.setdefault(clave, {"n_eventos": 0, "fallecidos": 0, "viv_destruidas": 0})
        d["n_eventos"] += 1
        d["fallecidos"] += e.get("fallecidos") or 0
        d["viv_destruidas"] += e.get("viviendas_destruidas") or 0

    print(f"Municipios con al menos 1 reporte (no son 'zona muda'): {len(impacto_por_municipio)}")

    print("\n=== Cruzando Sisbén con impacto normalizado (solo municipios que SÍ reportan) ===")
    filas_cruce = []
    for s in sisben:
        clave = (s["municipio"] or "").strip().upper()
        impacto = impacto_por_municipio.get(clave)
        if not impacto or impacto["n_eventos"] == 0:
            continue  # zona muda -- descartado, mismo criterio de #61
        impacto_normalizado = (impacto["fallecidos"] + impacto["viv_destruidas"]) / impacto["n_eventos"]
        filas_cruce.append({
            "municipio": s["municipio"],
            "pct_vulnerable": s["pct_material_vulnerable"],
            "n_eventos": impacto["n_eventos"],
            "impacto_normalizado": impacto_normalizado,
        })
    print(f"Municipios con dato Sisbén Y al menos 1 reporte real: {len(filas_cruce)}")

    pcts = sorted(f["pct_vulnerable"] for f in filas_cruce)
    n = len(pcts)
    q1 = pcts[n // 4]
    q3 = pcts[3 * n // 4]
    print(f"\nDistribución real de % vulnerable: min={pcts[0]:.1f} Q1={q1:.1f} mediana={pcts[n//2]:.1f} Q3={q3:.1f} max={pcts[-1]:.1f}")

    grupo_alta_vulnerabilidad = [f["impacto_normalizado"] for f in filas_cruce if f["pct_vulnerable"] >= q3]
    grupo_baja_vulnerabilidad = [f["impacto_normalizado"] for f in filas_cruce if f["pct_vulnerable"] <= q1]
    print(f"\nGrupo ALTA vulnerabilidad (>=Q3={q3:.1f}%): n={len(grupo_alta_vulnerabilidad)}")
    print(f"Grupo BAJA vulnerabilidad (<=Q1={q1:.1f}%): n={len(grupo_baja_vulnerabilidad)}")

    print(f"\nImpacto normalizado -- ALTA vulnerabilidad: mediana={statistics.median(grupo_alta_vulnerabilidad):.3f}, media={statistics.mean(grupo_alta_vulnerabilidad):.3f}")
    print(f"Impacto normalizado -- BAJA vulnerabilidad: mediana={statistics.median(grupo_baja_vulnerabilidad):.3f}, media={statistics.mean(grupo_baja_vulnerabilidad):.3f}")

    u, p, r = rank_biserial(grupo_alta_vulnerabilidad, grupo_baja_vulnerabilidad, alternative="greater")
    print(f"\nMann-Whitney U (ALTA > BAJA) = {u:.1f}, p = {p:.4f}")
    print(f"r (rank-biserial, tamaño del efecto) = {r:.4f}")
    if p < 0.05:
        print("RESULTADO: la vulnerabilidad de vivienda SÍ se asocia con mayor impacto por evento.")
    else:
        print("RESULTADO: no hay evidencia estadística suficiente a este nivel.")

    import json
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase3a_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filas_cruce, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
