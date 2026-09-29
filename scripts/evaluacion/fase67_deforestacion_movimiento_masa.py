"""Fase (issue #67): deforestacion real del IDEAM/SMByC vs. eventos reales
de movimiento en masa (UNGRD) -- primer cruce estadistico real usando el
cliente `ideam_deforestacion_client.py` (construido y verificado el mismo
dia, ver commit `e15ae86`).

Grupo ALTO/BAJO: mismo criterio ya validado en Fase 1c (#61) -- top-15
municipios por eventos reales de MOVIMIENTO EN MASA vs. municipios que
reportan activamente a UNGRD (cualquier tipo) pero CERO eventos de ese
tipo especifico (filtro de "zona muda", ver _utils_zona_muda.py, issue
#68 -- primer uso real de la utilidad extraida para evitar copiar esta
logica una quinta vez).

LIMITACION METODOLOGICA real, declarada antes de correr el cruce (no
despues de ver el resultado): los eventos UNGRD de movimiento en masa
cubren 2019-2024 (~6 anios), pero la capa "oficializada" mas reciente de
deforestacion del IDEAM/SMByC es el periodo 2020-2021 (un solo anio) --
NO es un cruce temporal perfecto, es una fotografia de cobertura de
bosque de un anio comparada contra 6 anios de eventos. Se declara asi,
no se presenta como si fueran exactamente el mismo periodo."""
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
import ideam_deforestacion_client as idc
from _utils_zona_muda import construir_universos, grupo_alto_top_n
from scipy.stats import chi2_contingency
import math

TAM_PAGINA = 1000
TIPOS_MOVIMIENTO_MASA = {"MOVIMIENTO EN MASA"}


def _paginar(tabla: str, columnas: str) -> list[dict]:
    filas = []
    inicio = 0
    while True:
        pagina = (
            rm.sb.table(tabla).select(columnas).range(inicio, inicio + TAM_PAGINA - 1).execute().data
            or []
        )
        filas.extend(pagina)
        if len(pagina) < TAM_PAGINA:
            break
        inicio += TAM_PAGINA
    return filas


def main() -> None:
    print("=== Cargando eventos reales UNGRD (movimiento en masa + filtro zona muda) ===")
    todos_eventos = _paginar("ungrd_emergencias", "municipio,departamento,evento")
    print(f"Total eventos: {len(todos_eventos)}")

    # departamento por municipio (primera ocurrencia real) -- para resolver
    # coordenadas via divipola sin ambiguedad cuando el nombre se repite
    # entre departamentos (68 casos reales, ver docstring de sgc_amenaza_sismica.py)
    depto_por_municipio: dict[str, str] = {}
    for e in todos_eventos:
        clave = (e.get("municipio") or "").strip().upper()
        if clave and clave not in depto_por_municipio and e.get("departamento"):
            depto_por_municipio[clave] = e["departamento"]

    universo_reportan, grupo_bajo, conteo_mm = construir_universos(todos_eventos, TIPOS_MOVIMIENTO_MASA)
    top15 = grupo_alto_top_n(conteo_mm, n=15)

    print(f"Universo que reporta activamente: {len(universo_reportan)}")
    print(f"Grupo ALTO (top 15 movimiento en masa): {len(top15)} municipios")
    print(f"Grupo BAJO (reportan, 0 movimiento en masa, zona muda descartada): {len(grupo_bajo)} municipios")

    print("\n=== Consultando deforestacion real IDEAM/SMByC por municipio (esto tarda, 1 llamada c/u) ===")
    resultados: list[dict] = []
    grupos = [("ALTO", top15), ("BAJO", sorted(grupo_bajo))]
    for nombre_grupo, municipios in grupos:
        for i, muni in enumerate(municipios, 1):
            depto = depto_por_municipio.get(muni)
            r = idc.consultar_cambio_bosque(muni, depto)
            categoria = r["categoria"] if r else "Sin dato"
            resultados.append({"grupo": nombre_grupo, "municipio": muni, "departamento": depto, "categoria": categoria})
            if i % 50 == 0 or i == len(municipios):
                print(f"  {nombre_grupo}: {i}/{len(municipios)}")

    con_dato = [r for r in resultados if r["categoria"] != "Sin dato"]
    print(f"\nMunicipios con dato real de deforestacion: {len(con_dato)}/{len(resultados)}")

    categorias = sorted({r["categoria"] for r in con_dato})
    print(f"Categorias reales encontradas: {categorias}")

    tabla_cruce: Counter = Counter()
    for r in con_dato:
        tabla_cruce[(r["grupo"], r["categoria"])] += 1

    print("\n=== Tabla de contingencia real (conteo de municipios) ===")
    print(f"{'':8}" + "".join(f"{c:>20}" for c in categorias) + f"{'TOTAL':>10}")
    matriz = []
    for grupo in ("ALTO", "BAJO"):
        fila = [tabla_cruce[(grupo, c)] for c in categorias]
        matriz.append(fila)
        total = sum(fila)
        pcts = [f"{100*v/total:.1f}%" if total else "0%" for v in fila]
        print(f"{grupo:8}" + "".join(f"{v:>14} ({p:>5})" for v, p in zip(fila, pcts)) + f"{total:>10}")

    total_general = sum(sum(f) for f in matriz)
    print(f"\nTotal de municipios en el cruce: {total_general}")

    # chi-cuadrado necesita al menos 2 categorias con datos y ambas filas
    # con total > 0 -- si la deforestacion resulto demasiado rara/ausente
    # en la muestra, se reporta eso honestamente en vez de forzar la prueba.
    filas_no_vacias = [f for f in matriz if sum(f) > 0]
    columnas_con_datos = [j for j in range(len(categorias)) if sum(f[j] for f in matriz) > 0]
    if len(filas_no_vacias) < 2 or len(columnas_con_datos) < 2:
        print("\nRESULTADO: muestra insuficiente para chi-cuadrado (menos de 2 categorias con datos reales en ambos grupos).")
    else:
        chi2, p, gl, _ = chi2_contingency(matriz)
        n_min = min(len(matriz) - 1, len(categorias) - 1) or 1
        v = math.sqrt(chi2 / (total_general * n_min))
        print(f"\nChi-cuadrado = {chi2:.2f}, gl={gl}, p={p:.4e}")
        print(f"Cramer's V = {v:.4f}")
        if p < 0.05:
            print("RESULTADO: SI hay asociacion estadistica real entre deforestacion y movimiento en masa.")
        else:
            print("RESULTADO: no hay evidencia estadistica suficiente de esa asociacion.")

    print("\n=== Nota honesta ===")
    print("1) Desajuste temporal real: deforestacion es una foto de 2020-2021 (unico periodo oficial),")
    print("   movimiento en masa cubre 2019-2024 (6 anios) -- no es el mismo periodo exacto.")
    print("2) Cada consulta de deforestacion es UN punto (centroide del municipio), no un area completa --")
    print("   municipios grandes/heterogeneos pueden no estar bien representados por ese punto.")
    print(f"3) {len(resultados) - len(con_dato)} municipios sin dato real (servicio no disponible o")
    print("   coordenadas no resueltas) -- descartados del cruce, no forzados a una categoria.")

    import json
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase67_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
