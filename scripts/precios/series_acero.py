"""Series mensuales del acero para pronóstico (#262 / #247). Solo lectura de los archivos en _cache/acero_262/.

Arma, sin empalmar por nivel (ver traslape en el #247):
  objetivo   ICOCIV insumo 106 "Acero corrugado" (Anexo 16, sección A16.5), base dic-2020 = 100, 2021-01 → 2026-09.
  auxiliar   ICCP grupo de obra "Aceros y elementos metálicos" (Anexo 10 de anexos_iccp_dic21.xlsx), base dic-2020 = 100,
             2000-01 → 2021-12. Es un grupo de obra (incluye mano de obra, equipo y transporte), no el insumo.
  líderes    TRM promedio mensual ponderado por días de vigencia (datos.gov.co 32sa-8pi3) y BLS PPI WPU1012 (chatarra
             de hierro y acero, dominio público).

traslape() compara ICCP e ICOCIV en 2021: correlación de las variaciones mensuales, diferencia de nivel y elasticidad.
Salida: data/precios_elementos/series_acero_262.csv (periodo, serie, valor). Solo números, con la cita del DANE.
Fuente: DANE, www.dane.gov.co · U.S. Bureau of Labor Statistics · Banco de la República vía datos.gov.co.

Uso: python scripts/precios/series_acero.py [--cache DIR] [--traslape]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics as st
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "data" / "precios_elementos" / "_cache" / "acero_262"
SALIDA = RAIZ / "data" / "precios_elementos" / "series_acero_262.csv"
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")
GRUPO_ICCP = "Aceros y elementos metálicos"
INSUMO_ICOCIV = "Acero corrugado"
TITULO_A165 = "A16.5"


def _filas(ruta: Path, hoja: str) -> list[list]:
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    return [list(r) for r in wb[hoja].iter_rows(values_only=True)]


def bloques_iccp(filas: list[list], etiqueta: str) -> dict[str, float]:
    """Anexo 10 del ICCP: un bloque por año ("Índices AAAA"), con fila "Meses | Enero…" y filas por grupo.
    El orden de los años en el archivo no se supone; se lee de cada encabezado."""
    serie: dict[str, float] = {}
    anio = None
    for r in filas:
        t = str(r[0] or "").strip() if r else ""
        m = re.match(r"Índices\s+(\d{4})", t)
        if m:
            anio = int(m.group(1))
            continue
        if anio and t == etiqueta:
            for k, v in enumerate(r[1:13]):
                if isinstance(v, (int, float)):
                    serie[f"{anio}-{k + 1:02d}"] = float(v)
    return serie


def insumo_icociv(filas: list[list], insumo: str) -> dict[str, float]:
    """Anexo 16, sección A16.5 (grupos de costos e insumos): encabezado de años (el año abre su bloque de meses),
    fila de meses debajo, y filas "Materiales | código | insumo | ponderación | índices…"."""
    ini = next(i for i, r in enumerate(filas) if str(r[0] or "").strip().startswith(TITULO_A165))
    anios, meses = filas[ini + 1], filas[ini + 2]
    periodos: dict[int, str] = {}
    anio = None
    for j, m in enumerate(meses):
        a = anios[j] if j < len(anios) else None
        if a is not None and str(a).strip().isdigit():
            anio = int(str(a).strip())
        if m is not None and str(m).strip().lower() in MESES and anio is not None:
            periodos[j] = f"{anio}-{MESES.index(str(m).strip().lower()) + 1:02d}"
    for r in filas[ini + 4:]:
        if r[0] is not None and str(r[0]).strip().startswith("A16."):
            break                                    # empezó otra sección
        if len(r) > 2 and str(r[2] or "").strip() == insumo:
            return {p: float(r[j]) for j, p in periodos.items() if j < len(r) and isinstance(r[j], (int, float))}
    raise KeyError(f"insumo {insumo!r} no está en {TITULO_A165}")


def trm_mensual(ruta: Path) -> dict[str, float]:
    """Promedio mensual ponderado por días: cada valor rige de vigenciadesde a vigenciahasta (fines de semana).
    Un mes sin todos sus días cubiertos (el mes en curso) se descarta: su promedio no es comparable."""
    suma: dict[str, float] = defaultdict(float)
    dias: dict[str, int] = defaultdict(int)
    with ruta.open(encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            d0, d1 = date.fromisoformat(f["vigenciadesde"][:10]), date.fromisoformat(f["vigenciahasta"][:10])
            v = float(f["valor"])
            d = d0
            while d <= d1:
                p = f"{d.year}-{d.month:02d}"
                suma[p] += v
                dias[p] += 1
                d += timedelta(days=1)
    def dias_mes(p: str) -> int:
        a, m = map(int, p.split("-"))
        return ((date(a + m // 12, m % 12 + 1, 1)) - date(a, m, 1)).days
    return {p: round(suma[p] / dias[p], 4) for p in sorted(suma) if dias[p] == dias_mes(p)}


def bls(rutas: list[Path]) -> dict[str, float]:
    serie: dict[str, float] = {}
    for ruta in rutas:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        for s in datos["Results"]["series"]:
            for d in s["data"]:
                if re.fullmatch(r"M(0[1-9]|1[0-2])", d["period"]):
                    serie[f"{d['year']}-{d['period'][1:]}"] = float(d["value"])
    return dict(sorted(serie.items()))


def variaciones(x: list[float]) -> list[float]:
    return [x[i] / x[i - 1] - 1 for i in range(1, len(x))]


def traslape(a: dict[str, float], b: dict[str, float]) -> dict:
    """a = grupo ICCP, b = insumo ICOCIV. Elasticidad β: pendiente de var(a) sobre var(b)."""
    comunes = sorted(set(a) & set(b))
    if len(comunes) < 3:
        raise ValueError("traslape menor a 3 meses")
    x, y = [a[p] for p in comunes], [b[p] for p in comunes]
    vx, vy = variaciones(x), variaciones(y)
    dif = [abs(p - q) for p, q in zip(x, y)]
    return {"meses": len(comunes), "desde": comunes[0], "hasta": comunes[-1],
            "corr_variacion": round(st.correlation(vx, vy), 3),
            "elasticidad": round(st.linear_regression(vy, vx).slope, 3),
            "dif_nivel_media": round(st.mean(dif), 2), "dif_nivel_max": round(max(dif), 2),
            "var_total_grupo": round(x[-1] / x[0] - 1, 4), "var_total_insumo": round(y[-1] / y[0] - 1, 4)}


def cargar(cache: Path = CACHE) -> dict[str, dict[str, float]]:
    return {
        "icociv_acero_corrugado": insumo_icociv(_filas(cache / "anex-ICOCIV-sep2026.xlsx", "Anexo 16"), INSUMO_ICOCIV),
        "iccp_aceros_elementos_metalicos": bloques_iccp(_filas(cache / "anexos_iccp_dic21.xlsx", "Anexo 10"), GRUPO_ICCP),
        "trm_promedio_mensual": trm_mensual(cache / "trm_datosgov.csv"),
        "bls_wpu1012": bls(sorted(cache.glob("bls_wpu1012_*.json"))),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=CACHE)
    ap.add_argument("--traslape", action="store_true", help="solo imprime la prueba del traslape 2021")
    a = ap.parse_args()
    series = cargar(a.cache)
    for n, s in series.items():
        print(f"{n:34s} {len(s):4d} meses  {min(s)} → {max(s)}")
    print("traslape:", json.dumps(traslape(series["iccp_aceros_elementos_metalicos"], series["icociv_acero_corrugado"])))
    if a.traslape:
        return
    with SALIDA.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["periodo", "serie", "valor"])
        for n, s in series.items():
            for p, v in s.items():
                w.writerow([p, n, v])
    print("escrito", SALIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
