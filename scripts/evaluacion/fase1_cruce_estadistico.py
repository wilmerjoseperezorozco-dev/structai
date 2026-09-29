"""Fase 1 (issue #61): amplia el grupo de control de 15 a los 620
municipios completos sin eventos de MOVIMIENTO EN MASA registrados, y
corre una prueba estadistica formal (chi-cuadrado) sobre la distribucion
de pendiente entre el grupo ALTO (top-15 con mas eventos) y el grupo
BAJO ahora completo -- en vez de descriptiva nada mas, como en Fase 0.

Precipitacion (IDEAM) queda FUERA de este script a proposito: los datos
crudos de IDEAM son lecturas sub-diarias (varias por dia, ver timestamps
reales) -- promediar valorobservado directamente NO da "precipitacion
media anual" (la variable real que usa el paper de Medellin), da un
numero distinto y potencialmente enganoso. Investigar la semantica real
del sensor (acumulado vs. por evento) antes de construir esa metrica es
un paso aparte, no improvisado en el mismo script que ya tiene resultados
limpios."""
import io
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import rag_multi_norma as rm
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
    print("=== Recalculando grupo ALTO (top 15, mismo que Fase 0) ===")
    eventos = _paginar(
        "ungrd_emergencias", "municipio,departamento,evento",
        lambda q: q.eq("evento", "MOVIMIENTO EN MASA"),
    )
    conteo: Counter = Counter()
    for e in eventos:
        clave = (e["municipio"] or "").strip().upper()
        if clave:
            conteo[clave] += 1
    top15 = [m for m, _ in conteo.most_common(15)]
    print(f"Grupo ALTO: {len(top15)} municipios")

    print("\n=== Grupo BAJO: TODOS los municipios con 0 eventos (no muestra de 15) ===")
    todos_municipios = _paginar("sgc_amenaza_sismica_municipios", "municipio,departamento", None)
    sin_eventos = [
        m["municipio"] for m in todos_municipios
        if (m["municipio"] or "").strip().upper() not in conteo
    ]
    print(f"Grupo BAJO completo: {len(sin_eventos)} municipios (antes: muestra de 15)")

    print("\n=== Perfil de pendiente: grupo ALTO ===")
    agg_alto = Counter()
    sin_dato_alto = 0
    for muni in top15:
        p = perfil_pendiente(muni)
        if not p:
            sin_dato_alto += 1
        agg_alto.update(p)
    print(f"Sin dato IGAC: {sin_dato_alto}/{len(top15)}")

    print("\n=== Perfil de pendiente: grupo BAJO (620 municipios, esto tarda) ===")
    agg_bajo = Counter()
    sin_dato_bajo = 0
    for i, muni in enumerate(sin_eventos):
        p = perfil_pendiente(muni)
        if not p:
            sin_dato_bajo += 1
        agg_bajo.update(p)
        if (i + 1) % 100 == 0:
            print(f"  ... {i+1}/{len(sin_eventos)} procesados")
    print(f"Sin dato IGAC: {sin_dato_bajo}/{len(sin_eventos)}")

    print("\n=== Comparación agregada (grupo BAJO ahora completo, no muestra) ===")
    total_alto = sum(agg_alto.values())
    total_bajo = sum(agg_bajo.values())
    letras = "abcdefg"
    print(f"Grupo ALTO: {total_alto} polígonos totales")
    for letra in letras:
        pct = 100 * agg_alto.get(letra, 0) / total_alto if total_alto else 0
        print(f"  pendiente {letra}: {pct:5.1f}% (n={agg_alto.get(letra, 0)})")
    print(f"\nGrupo BAJO: {total_bajo} polígonos totales")
    for letra in letras:
        pct = 100 * agg_bajo.get(letra, 0) / total_bajo if total_bajo else 0
        print(f"  pendiente {letra}: {pct:5.1f}% (n={agg_bajo.get(letra, 0)})")

    print("\n=== Prueba estadística formal: chi-cuadrado de independencia ===")
    tabla_contingencia = [
        [agg_alto.get(letra, 0) for letra in letras],
        [agg_bajo.get(letra, 0) for letra in letras],
    ]
    chi2, p_valor, gl, esperado = chi2_contingency(tabla_contingencia)
    print(f"Chi-cuadrado = {chi2:.2f}")
    print(f"Grados de libertad = {gl}")
    print(f"p-valor = {p_valor:.2e}")
    if p_valor < 0.001:
        print("\nRESULTADO: la diferencia es estadísticamente significativa (p < 0.001).")
        print("La distribución de pendiente NO es independiente de si el municipio")
        print("tiene o no eventos históricos de movimiento en masa.")
    else:
        print(f"\nRESULTADO: no hay evidencia estadística suficiente (p = {p_valor:.4f}).")


if __name__ == "__main__":
    main()
