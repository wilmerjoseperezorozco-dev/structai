"""Fase 4c: fase El Nino/La Nina (indice ONI oficial NOAA) vs anomalia real
de caudal ya detectada por StructAI en produccion (ver
rag_multi_norma._comparar_caudal_historico / _bloque_caudal_con_anomalia).

Por que esta es la pieza mas barata de investigar primero (a diferencia de
Peru/Ecuador, que requieren verificar infraestructura de datos de otro
pais antes de prometer nada): no necesita NINGUN dato nuevo. Cruza dos
cosas que YA existen, verificadas, en este mismo proyecto:
  1. ideam_caudal_historico (352.022 filas reales, carga masiva ya hecha
     el 2026-08-22, ver scripts/ingesta/ideam_caudal/) + las estadisticas
     mensuales por estacion ya calculadas (ideam_caudal_estadisticas_mes,
     11.310 filas, promedio/p10/p90 por estacion x mes).
  2. El indice ONI oficial (Oceanic Nino Index, NOAA Climate Prediction
     Center, ERSSTv6), tabla completa 1950-2026 leida en vivo el
     2026-09-29 de https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/
     -- transcrita completa abajo, no resumida ni estimada.

Metodologia: cada columna de la tabla ONI es una media movil de 3 meses
centrada en un mes especifico (DJF->centro enero, JFM->centro febrero, ...,
NDJ->centro diciembre) -- convencion estandar de NOAA. Se clasifica cada
mes calendario segun el umbral oficial +/-0.5 grados C aplicado MES A MES
(simplificacion honesta: la clasificacion OFICIAL de "episodio" de NOAA
exige 5 temporadas consecutivas sostenidas, lo cual clasifica *periodos*,
no meses individuales -- aqui se usa el umbral mensual simple, mas
permisivo, y se reporta como tal, no como la lista oficial de episodios).

Cruce real: para cada lectura historica de caudal con estadistica
disponible, se calcula si excede el p90 (crecida anomala), esta por
debajo del p10 (sequia anomala) o esta en rango normal de ESE mes
calendario para ESA estacion -- exactamente el mismo criterio que ya usa
_comparar_caudal_historico en produccion, no uno nuevo. Se cruza esa
categoria contra la fase ENSO real de ese mes/anio -- chi-cuadrado +
Cramer's V, mismo estandar estadistico del resto de este proyecto."""
import io
import math
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

# Tabla ONI oficial completa (NOAA CPC, ERSSTv6), columnas = temporadas de
# 3 meses en orden DJF,JFM,FMA,MAM,AMJ,MJJ,JJA,JAS,ASO,SON,OND,NDJ.
# Leida en vivo el 2026-09-29 de
# https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/
ONI_TABLA: dict[int, list[float]] = {
    1950: [-1.3, -1.2, -1.1, -1.1, -1.1, -0.9, -0.6, -0.6, -0.6, -0.6, -0.7, -0.8],
    1951: [-0.7, -0.4, 0.0, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0, 1.0, 1.0, 0.7],
    1952: [0.5, 0.3, 0.3, 0.2, -0.1, -0.4, -0.4, -0.2, 0.0, 0.0, -0.1, 0.1],
    1953: [0.3, 0.5, 0.5, 0.6, 0.8, 0.7, 0.6, 0.7, 0.6, 0.8, 0.5, 0.6],
    1954: [0.4, 0.4, 0.0, -0.3, -0.5, -0.5, -0.7, -0.8, -0.7, -0.5, -0.4, -0.4],
    1955: [-0.5, -0.5, -0.6, -0.8, -0.8, -0.9, -0.7, -0.9, -1.1, -1.4, -1.6, -1.5],
    1956: [-1.2, -0.8, -0.6, -0.5, -0.5, -0.5, -0.5, -0.5, -0.4, -0.4, -0.4, -0.4],
    1957: [-0.3, -0.1, 0.3, 0.6, 0.7, 0.8, 1.0, 1.0, 1.1, 1.2, 1.4, 1.6],
    1958: [1.7, 1.6, 1.2, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.3, 0.4, 0.6],
    1959: [0.6, 0.6, 0.5, 0.4, 0.2, 0.0, -0.2, -0.2, 0.0, 0.1, 0.2, 0.1],
    1960: [0.0, 0.0, 0.1, 0.2, 0.0, 0.0, 0.0, 0.2, 0.2, 0.1, -0.1, -0.1],
    1961: [0.0, 0.0, 0.0, 0.1, 0.2, 0.2, 0.1, -0.2, -0.3, -0.2, -0.1, 0.0],
    1962: [-0.2, -0.2, -0.1, -0.2, -0.2, -0.1, 0.0, -0.1, -0.2, -0.2, -0.2, -0.3],
    1963: [-0.3, -0.2, 0.0, 0.1, 0.1, 0.5, 0.8, 1.1, 1.1, 1.1, 1.2, 1.1],
    1964: [0.9, 0.5, 0.1, -0.3, -0.6, -0.7, -0.7, -0.7, -0.7, -0.8, -0.8, -0.7],
    1965: [-0.5, -0.2, 0.0, 0.2, 0.5, 0.8, 1.1, 1.3, 1.6, 1.7, 1.8, 1.6],
    1966: [1.2, 1.0, 0.8, 0.4, 0.2, 0.2, 0.3, 0.1, -0.1, -0.1, -0.2, -0.3],
    1967: [-0.5, -0.5, -0.5, -0.4, -0.1, 0.1, 0.0, -0.3, -0.4, -0.4, -0.4, -0.4],
    1968: [-0.6, -0.7, -0.6, -0.5, -0.1, 0.2, 0.4, 0.4, 0.3, 0.5, 0.7, 0.9],
    1969: [1.0, 1.0, 0.8, 0.7, 0.6, 0.5, 0.4, 0.4, 0.6, 0.7, 0.8, 0.7],
    1970: [0.5, 0.2, 0.2, 0.3, 0.1, -0.3, -0.5, -0.7, -0.7, -0.7, -0.8, -1.1],
    1971: [-1.3, -1.4, -1.1, -0.8, -0.7, -0.7, -0.7, -0.6, -0.7, -0.8, -0.9, -0.8],
    1972: [-0.6, -0.3, 0.0, 0.3, 0.5, 0.7, 1.0, 1.3, 1.5, 1.7, 1.8, 1.8],
    1973: [1.6, 1.1, 0.6, 0.0, -0.5, -0.8, -1.0, -1.1, -1.3, -1.6, -1.9, -2.0],
    1974: [-1.9, -1.6, -1.2, -1.0, -0.7, -0.6, -0.5, -0.4, -0.5, -0.7, -0.9, -0.7],
    1975: [-0.6, -0.5, -0.6, -0.7, -0.8, -0.9, -1.1, -1.1, -1.3, -1.3, -1.5, -1.6],
    1976: [-1.5, -1.1, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.8, 0.8],
    1977: [0.7, 0.7, 0.3, 0.3, 0.3, 0.5, 0.4, 0.4, 0.5, 0.7, 0.8, 0.8],
    1978: [0.7, 0.5, 0.2, -0.1, -0.3, -0.2, -0.4, -0.4, -0.4, -0.3, -0.1, 0.1],
    1979: [0.2, 0.2, 0.3, 0.3, 0.3, 0.1, 0.1, 0.2, 0.3, 0.5, 0.5, 0.6],
    1980: [0.6, 0.5, 0.4, 0.3, 0.5, 0.4, 0.2, -0.1, -0.2, -0.1, 0.1, 0.0],
    1981: [-0.3, -0.4, -0.4, -0.3, -0.3, -0.3, -0.3, -0.2, -0.1, -0.2, -0.2, -0.1],
    1982: [0.0, 0.0, 0.1, 0.3, 0.7, 0.7, 0.8, 1.0, 1.5, 1.8, 2.0, 2.1],
    1983: [2.1, 1.9, 1.5, 1.2, 1.0, 0.6, 0.3, -0.1, -0.4, -0.8, -1.0, -0.9],
    1984: [-0.6, -0.5, -0.4, -0.5, -0.5, -0.5, -0.4, -0.2, -0.3, -0.6, -0.9, -1.1],
    1985: [-1.0, -0.9, -0.8, -0.8, -0.8, -0.6, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4],
    1986: [-0.4, -0.4, -0.2, -0.2, -0.1, 0.0, 0.2, 0.5, 0.6, 0.9, 1.1, 1.2],
    1987: [1.2, 1.1, 1.0, 0.9, 1.0, 1.1, 1.3, 1.5, 1.5, 1.4, 1.2, 1.0],
    1988: [0.6, 0.4, 0.0, -0.4, -1.0, -1.3, -1.3, -1.1, -1.3, -1.5, -1.8, -1.8],
    1989: [-1.6, -1.4, -1.1, -0.8, -0.6, -0.4, -0.4, -0.4, -0.3, -0.2, -0.1, 0.0],
    1990: [0.2, 0.2, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
    1991: [0.4, 0.3, 0.2, 0.3, 0.5, 0.6, 0.8, 0.7, 0.7, 0.8, 1.2, 1.4],
    1992: [1.5, 1.5, 1.4, 1.3, 1.1, 0.7, 0.4, 0.1, -0.1, -0.2, -0.2, 0.0],
    1993: [0.1, 0.3, 0.5, 0.7, 0.8, 0.6, 0.3, 0.2, 0.2, 0.2, 0.2, 0.2],
    1994: [0.1, 0.0, 0.0, 0.2, 0.3, 0.2, 0.3, 0.3, 0.5, 0.7, 0.9, 1.0],
    1995: [0.9, 0.7, 0.5, 0.2, 0.0, -0.1, -0.3, -0.5, -0.8, -1.0, -1.0, -1.0],
    1996: [-0.9, -0.7, -0.5, -0.4, -0.2, -0.2, -0.2, -0.3, -0.3, -0.3, -0.4, -0.4],
    1997: [-0.4, -0.3, 0.0, 0.3, 0.7, 1.1, 1.5, 1.8, 2.0, 2.2, 2.3, 2.4],
    1998: [2.2, 1.9, 1.4, 1.0, 0.4, -0.1, -0.6, -0.8, -1.0, -1.1, -1.3, -1.5],
    1999: [-1.5, -1.2, -0.9, -0.8, -0.8, -0.8, -0.9, -0.9, -1.0, -1.1, -1.3, -1.5],
    2000: [-1.5, -1.3, -1.0, -0.8, -0.7, -0.6, -0.5, -0.4, -0.4, -0.5, -0.8, -0.8],
    2001: [-0.8, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, -0.1, -0.1, -0.3, -0.3, -0.3],
    2002: [-0.1, 0.1, 0.1, 0.2, 0.3, 0.5, 0.6, 0.6, 0.8, 1.0, 1.2, 1.1],
    2003: [0.9, 0.6, 0.4, 0.0, -0.2, -0.1, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3],
    2004: [0.3, 0.3, 0.2, 0.1, 0.1, 0.2, 0.4, 0.5, 0.6, 0.6, 0.6, 0.7],
    2005: [0.6, 0.6, 0.4, 0.4, 0.3, 0.1, 0.0, -0.1, -0.1, -0.3, -0.6, -0.8],
    2006: [-0.9, -0.8, -0.6, -0.4, -0.2, 0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.9],
    2007: [0.6, 0.2, -0.1, -0.3, -0.3, -0.4, -0.5, -0.8, -1.0, -1.4, -1.6, -1.7],
    2008: [-1.8, -1.6, -1.4, -1.0, -0.8, -0.6, -0.3, -0.2, -0.2, -0.4, -0.6, -0.8],
    2009: [-0.9, -0.8, -0.6, -0.3, 0.0, 0.3, 0.5, 0.6, 0.7, 0.9, 1.3, 1.5],
    2010: [1.5, 1.2, 0.9, 0.4, -0.2, -0.7, -1.0, -1.2, -1.4, -1.5, -1.6, -1.5],
    2011: [-1.3, -1.1, -0.8, -0.7, -0.5, -0.3, -0.4, -0.5, -0.8, -0.9, -1.0, -0.9],
    2012: [-0.7, -0.6, -0.4, -0.3, -0.2, 0.0, 0.3, 0.4, 0.4, 0.3, 0.1, 0.0],
    2013: [-0.2, -0.3, -0.2, -0.2, -0.3, -0.4, -0.4, -0.3, -0.3, -0.1, -0.1, -0.1],
    2014: [-0.2, -0.2, 0.0, 0.3, 0.4, 0.2, 0.1, 0.1, 0.2, 0.5, 0.7, 0.8],
    2015: [0.7, 0.7, 0.7, 0.9, 1.0, 1.2, 1.4, 1.7, 2.0, 2.3, 2.5, 2.6],
    2016: [2.5, 2.2, 1.7, 1.1, 0.6, 0.1, -0.2, -0.3, -0.4, -0.5, -0.5, -0.4],
    2017: [-0.1, 0.1, 0.3, 0.3, 0.4, 0.3, 0.1, -0.1, -0.2, -0.4, -0.6, -0.8],
    2018: [-0.7, -0.7, -0.5, -0.3, -0.1, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.1],
    2019: [1.0, 0.9, 0.9, 0.8, 0.7, 0.6, 0.4, 0.2, 0.3, 0.5, 0.7, 0.8],
    2020: [0.7, 0.7, 0.6, 0.3, 0.0, -0.2, -0.3, -0.4, -0.8, -1.0, -1.1, -1.1],
    2021: [-1.0, -0.9, -0.7, -0.6, -0.4, -0.3, -0.3, -0.5, -0.6, -0.8, -0.9, -0.8],
    2022: [-0.8, -0.7, -0.8, -0.9, -0.8, -0.7, -0.7, -0.8, -0.9, -0.9, -0.8, -0.7],
    2023: [-0.5, -0.3, -0.1, 0.2, 0.5, 0.7, 1.0, 1.3, 1.5, 1.7, 1.9, 2.0],
    2024: [1.8, 1.5, 1.2, 0.8, 0.4, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4],
    2025: [-0.5, -0.2, -0.1, 0.0, 0.0, 0.0, -0.1, -0.3, -0.4, -0.6, -0.6, -0.6],
    2026: [-0.4, -0.2, 0.1, 0.5, 0.9, 1.4, 1.8],  # solo hasta JJA, dato mas reciente
}
UMBRAL_ENSO = 0.5


def oni_por_mes() -> dict[tuple[int, int], float]:
    """Cada columna c (0=DJF..11=NDJ) esta centrada en el mes calendario
    c+1 (DJF centrado en enero, NDJ centrado en diciembre) -- convencion
    estandar NOAA. El anio de la fila es el anio del mes central."""
    resultado: dict[tuple[int, int], float] = {}
    for anio, valores in ONI_TABLA.items():
        for col, valor in enumerate(valores):
            mes_centro = col + 1
            resultado[(anio, mes_centro)] = valor
    return resultado


def fase_enso(valor: float) -> str:
    if valor >= UMBRAL_ENSO:
        return "El Nino"
    if valor <= -UMBRAL_ENSO:
        return "La Nina"
    return "Neutral"


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


def main() -> None:
    print("=== Cargando estadisticas mensuales por estacion (baseline real, ya calculado) ===")
    stats_filas = _paginar(
        "ideam_caudal_estadisticas_mes",
        "codigo_estacion,mes,p10_m3s,p90_m3s,n_observaciones",
    )
    stats: dict[tuple[str, int], dict] = {
        (s["codigo_estacion"], s["mes"]): s
        for s in stats_filas
        if s.get("p10_m3s") is not None and s.get("p90_m3s") is not None
    }
    print(f"Estadisticas usables (con p10/p90 reales): {len(stats)} de {len(stats_filas)}")

    print("\n=== Cargando historico completo de caudal (352.022 filas, esto tarda) ===")
    historico = _paginar("ideam_caudal_historico", "codigo_estacion,fecha,caudal_m3s")
    print(f"Filas historicas cargadas: {len(historico)}")

    print("\n=== Indice ONI oficial NOAA (ERSSTv6) cargado: ===")
    oni_mensual = oni_por_mes()
    print(f"Meses con dato ONI real: {len(oni_mensual)} ({min(oni_mensual)} a {max(oni_mensual)})")

    print("\n=== Cruzando cada lectura real de caudal contra su categoria (alto/normal/bajo) y fase ENSO ===")
    tabla_cruce: Counter = Counter()
    descartadas_sin_stats = 0
    descartadas_sin_oni = 0
    descartadas_caudal_invalido = 0
    usadas = 0

    for fila in historico:
        try:
            caudal = float(fila.get("caudal_m3s"))
        except (TypeError, ValueError):
            descartadas_caudal_invalido += 1
            continue
        fecha = fila.get("fecha") or ""
        if len(fecha) < 7:
            descartadas_caudal_invalido += 1
            continue
        anio, mes = int(fecha[:4]), int(fecha[5:7])

        clave_stats = (fila["codigo_estacion"], mes)
        s = stats.get(clave_stats)
        if not s:
            descartadas_sin_stats += 1
            continue

        oni = oni_mensual.get((anio, mes))
        if oni is None:
            descartadas_sin_oni += 1
            continue

        if caudal > s["p90_m3s"]:
            categoria = "alto (>p90)"
        elif caudal < s["p10_m3s"]:
            categoria = "bajo (<p10)"
        else:
            categoria = "normal"

        tabla_cruce[(fase_enso(oni), categoria)] += 1
        usadas += 1

    print(f"Lecturas usadas en el cruce: {usadas}")
    print(f"Descartadas -- sin estadistica p10/p90 para esa estacion/mes: {descartadas_sin_stats}")
    print(f"Descartadas -- fuera del rango ONI 1950-2026 (JJA): {descartadas_sin_oni}")
    print(f"Descartadas -- caudal/fecha invalidos: {descartadas_caudal_invalido}")

    fases = ["El Nino", "Neutral", "La Nina"]
    categorias = ["alto (>p90)", "normal", "bajo (<p10)"]
    print("\n=== Tabla de contingencia real (conteo de lecturas) ===")
    print(f"{'':12}" + "".join(f"{c:>16}" for c in categorias) + f"{'TOTAL':>10}")
    matriz = []
    for f in fases:
        fila_conteo = [tabla_cruce[(f, c)] for c in categorias]
        matriz.append(fila_conteo)
        total_fila = sum(fila_conteo)
        pcts = [f"{100*v/total_fila:.1f}%" if total_fila else "0%" for v in fila_conteo]
        print(f"{f:12}" + "".join(f"{v:>10} ({p:>5})" for v, p in zip(fila_conteo, pcts)) + f"{total_fila:>10}")

    total_general = sum(sum(row) for row in matriz)
    print(f"\nTotal de lecturas en el cruce: {total_general}")

    chi2, p, gl, _ = chi2_contingency(matriz)
    v = math.sqrt(chi2 / (total_general * min(len(fases) - 1, len(categorias) - 1)))
    print(f"\nChi-cuadrado = {chi2:.2f}, gl={gl}, p={p:.4e}")
    print(f"Cramer's V = {v:.4f}")
    if p < 0.05:
        print("RESULTADO: SI hay asociacion estadistica real entre fase ENSO y categoria de caudal.")
    else:
        print("RESULTADO: no hay evidencia estadistica suficiente de esa asociacion.")

    print("\n=== Nota metodologica honesta ===")
    print("1) Clasificacion ENSO mes-a-mes por umbral simple (+/-0.5 grados C), NO la lista")
    print("   oficial de 'episodios sostenidos' de NOAA (que exige 5 temporadas consecutivas).")
    print("2) Las lecturas NO son independientes entre si -- la misma estacion aporta muchos")
    print("   meses correlacionados entre si (autocorrelacion temporal real), y el chi-cuadrado")
    print("   asume independencia. El resultado indica asociacion real en los datos, pero el")
    print("   p-valor exacto debe leerse con cautela por esta razon (n efectivo probablemente")
    print("   menor al n nominal). Cramer's V es mas robusto a esto que el p-valor solo.")
    print("3) Colombia es un pais grande con multiples regímenes climaticos (Caribe/Pacifico/")
    print("   Andes/Orinoquia/Amazonia) -- este cruce agrega TODAS las estaciones del pais,")
    print("   lo cual puede diluir o mezclar efectos que van en direcciones opuestas por region")
    print("   (ej. El Nino seca el interior pero puede alterar el suroccidente). Desagregar por")
    print("   region es el siguiente paso logico si este resultado agregado es real.")

    import json
    out = {
        "matriz": {f"{f}|{c}": tabla_cruce[(f, c)] for f in fases for c in categorias},
        "chi2": chi2, "p": p, "gl": gl, "cramers_v": v,
        "usadas": usadas, "descartadas_sin_stats": descartadas_sin_stats,
        "descartadas_sin_oni": descartadas_sin_oni,
    }
    out_path = PROJECT_ROOT / "scripts" / "evaluacion" / "fase4c_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nDatos crudos guardados en {out_path}")


if __name__ == "__main__":
    main()
