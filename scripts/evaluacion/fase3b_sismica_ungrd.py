"""Fase 3b (issue #63): amenaza sismica SGC (Aa) vs eventos reales de
SISMO en UNGRD.

Replanteo honesto de la pregunta original: el propio issue #63 advertia
verificar volumen antes de disenar la comparacion. Encontrado: 98 eventos
reales, 82 municipios distintos (volumen razonable para comparar), PERO
el dano acumulado es minimo (1 fallecido, 111 viviendas destruidas en
total en 2019-2024) -- insuficiente para medir "severidad de dano" de
forma confiable (la mayoria de valores serian 0, unos pocos outliers).

Pregunta que SI se puede responder con este volumen: ¿el Aa oficial del
SGC es mas alto en los municipios que SI tuvieron un sismo reportado,
comparado con los que reportan otras cosas pero nunca un sismo? -- valida
si la clasificacion oficial de amenaza coincide con donde realmente se
han reportado sismos, sin prometer nada sobre severidad de dano que el
dato no puede sostener."""
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
from _utils_zona_muda import construir_universos
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
    print("=== Cargando eventos reales UNGRD (todos, para SISMO + filtro zona muda) ===")
    todos_eventos = _paginar("ungrd_emergencias", "municipio,departamento,evento")
    print(f"Total eventos: {len(todos_eventos)}")

    municipios_con_algun_evento, municipios_sin_sismo_pero_reportan, conteo_sismo = construir_universos(
        todos_eventos, {"SISMO"}
    )
    municipios_con_sismo = set(conteo_sismo)
    print(f"Municipios con AL MENOS 1 evento de cualquier tipo: {len(municipios_con_algun_evento)}")
    print(f"Municipios con AL MENOS 1 evento SISMO: {len(municipios_con_sismo)}")

    print("\n=== Cargando amenaza sísmica SGC (Aa) ===")
    sgc = _paginar("sgc_amenaza_sismica_municipios", "municipio,departamento,aa")
    aa_por_municipio: dict[str, float] = {}
    for m in sgc:
        clave = (m["municipio"] or "").strip().upper()
        if clave and m.get("aa") is not None and clave not in aa_por_municipio:
            aa_por_municipio[clave] = float(m["aa"])
    print(f"Municipios con dato Aa: {len(aa_por_municipio)}")

    # Grupo CON sismo real
    aa_con_sismo = [aa_por_municipio[m] for m in municipios_con_sismo if m in aa_por_municipio]
    # Grupo SIN sismo, pero que SI reportan otras cosas (filtro de zona muda -- ver _utils_zona_muda.py)
    aa_sin_sismo = [aa_por_municipio[m] for m in municipios_sin_sismo_pero_reportan if m in aa_por_municipio]

    print(f"\nGrupo CON sismo real: n={len(aa_con_sismo)}")
    print(f"Grupo SIN sismo (pero reportan otras cosas): n={len(aa_sin_sismo)}")

    print(f"\nAa -- grupo CON sismo: mediana={statistics.median(aa_con_sismo):.3f}, media={statistics.mean(aa_con_sismo):.3f}")
    print(f"Aa -- grupo SIN sismo: mediana={statistics.median(aa_sin_sismo):.3f}, media={statistics.mean(aa_sin_sismo):.3f}")

    u, p, r = rank_biserial(aa_con_sismo, aa_sin_sismo, alternative="greater")
    print(f"\nMann-Whitney U (CON sismo > SIN sismo) = {u:.1f}, p = {p:.4f}")
    print(f"r (rank-biserial) = {r:.4f}")
    if p < 0.05:
        print("RESULTADO: el Aa oficial SÍ es más alto donde realmente se han reportado sismos.")
    else:
        print("RESULTADO: no hay evidencia estadística suficiente de esa asociación.")

    print("\n=== Nota honesta sobre severidad de daño (NO se prueba aquí) ===")
    print("98 eventos SISMO en 2019-2024: 1 fallecido total, 111 viviendas destruidas en total.")
    print("Volumen insuficiente para una comparación de severidad confiable -- no se intenta.")

    import json
    out = {
        "municipios_con_sismo": sorted(municipios_con_sismo),
        "aa_con_sismo": aa_con_sismo,
        "aa_sin_sismo": aa_sin_sismo,
    }
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase3b_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
