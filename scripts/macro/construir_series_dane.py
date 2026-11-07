"""Convierte los tres anexos del DANE (descargados con permiso del usuario el 2026-11-06) en series
ordenadas y verifica su coherencia interna. No modela nada.

Fuentes (dane.gov.co, archivos locales en scripts/macro/_cache/dane/, ignorados por git):
- anex-IPC-Indices-sep2026.xlsx: indice TOTAL del IPC, mensual, serie de empalme 2003-2026.
  (No trae desglose por grupo de gasto: la inflacion de alimentos requiere otro archivo.)
- anex-ProduccionConstantes-IItrim2026.xlsx: PIB trimestral por produccion, volumen encadenado base 2015,
  12 agrupaciones CIIU: Cuadro 1 (datos originales) y Cuadro 4 (ajustados por estacionalidad y calendario).
- anex-ECG-sep2026.xlsx: cemento gris. A1 = produccion y despachos nacionales (abr-2009 a sep-2026);
  A6 = despachos por departamento de destino (abr-2009 a ago-2026).

Salidas (scripts/macro/): ipc_mensual.csv, pib_trimestral_12.csv, cemento_nacional_mensual.csv,
cemento_departamento_mensual.csv. Cifras recientes del DANE son provisionales o preliminares.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
DANE = AQUI / "_cache" / "dane"
MES_ES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
          "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
MES_ABR = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}
OK = True


def verificar(cond: bool, msg: str) -> None:
    global OK
    print(("  OK   " if cond else "  FALLA ") + msg)
    OK = OK and cond


def ipc() -> pd.DataFrame:
    d = pd.read_excel(DANE / "anex-IPC-Indices-sep2026.xlsx", header=None)
    fila_anios = d.index[d[0].astype(str).str.strip() == "Mes"][0]
    anios = [int(x) for x in d.iloc[fila_anios, 1:].dropna()]
    filas = []
    for i in range(fila_anios + 1, fila_anios + 13):
        mes = MES_ES[str(d.iloc[i, 0]).strip().lower()]
        for j, a in enumerate(anios, start=1):
            v = d.iloc[i, j]
            if pd.notna(v):
                filas.append((pd.Timestamp(year=a, month=mes, day=1), float(v)))
    s = pd.DataFrame(filas, columns=["fecha", "indice"]).sort_values("fecha").reset_index(drop=True)
    s["var_mensual_pct"] = 100 * s["indice"].pct_change()
    s["var_anual_pct"] = 100 * s["indice"].pct_change(12)
    return s


def pib(hoja: str, etiqueta: str) -> pd.DataFrame:
    d = pd.read_excel(DANE / "anex-ProduccionConstantes-IItrim2026.xlsx", sheet_name=hoja, header=None)
    f_anio = d.index[d[2].astype(str).str.strip() == "Concepto"][0]
    anios, col_anio = {}, None
    for j in range(3, d.shape[1]):
        v = d.iloc[f_anio, j]
        if pd.notna(v):
            col_anio = int(str(v)[:4])
        anios[j] = col_anio
    trim = {j: {"I": 1, "II": 2, "III": 3, "IV": 4}[str(d.iloc[f_anio + 1, j]).strip()] for j in range(3, d.shape[1])}
    filas = []
    for i in range(f_anio + 3, f_anio + 3 + 15):
        nombre = str(d.iloc[i, 2]) if pd.notna(d.iloc[i, 2]) else str(d.iloc[i, 0])
        codigo = str(d.iloc[i, 1]) if pd.notna(d.iloc[i, 1]) else ""
        if nombre in ("nan", "") and codigo in ("nan", ""):
            continue
        for j in range(3, d.shape[1]):
            v = d.iloc[i, j]
            if pd.notna(v):
                filas.append((etiqueta, codigo, nombre[:60], anios[j], trim[j], float(v)))
    return pd.DataFrame(filas, columns=["serie", "codigo", "concepto", "anio", "trimestre", "valor_miles_millones_2015"])


def cemento_nacional() -> pd.DataFrame:
    d = pd.read_excel(DANE / "anex-ECG-sep2026.xlsx", sheet_name="Anexo 1 ", header=None)
    filas, anio = [], None
    for i in range(8, d.shape[0]):
        if pd.notna(d.iloc[i, 0]) and str(d.iloc[i, 0]).strip().isdigit():
            anio = int(str(d.iloc[i, 0]).strip())
        mes = str(d.iloc[i, 2]).strip().lower()[:3]
        if mes in MES_ABR and anio and pd.notna(d.iloc[i, 3]) and pd.notna(d.iloc[i, 4]):
            try:
                filas.append((pd.Timestamp(year=anio, month=MES_ABR[mes], day=1), float(d.iloc[i, 3]), float(d.iloc[i, 4])))
            except ValueError:
                pass
    return pd.DataFrame(filas, columns=["fecha", "produccion_t", "despachos_nacionales_t"]).drop_duplicates("fecha").sort_values("fecha")


def cemento_departamento() -> pd.DataFrame:
    d = pd.read_excel(DANE / "anex-ECG-sep2026.xlsx", sheet_name="Anexo 6", header=None)
    filas, anio, mes = [], None, None
    for i in range(8, d.shape[0]):
        if pd.notna(d.iloc[i, 0]) and str(d.iloc[i, 0]).strip().isdigit():
            anio = int(str(d.iloc[i, 0]).strip())
        if pd.notna(d.iloc[i, 1]) and str(d.iloc[i, 1]).strip().lower()[:3] in MES_ABR:
            mes = MES_ABR[str(d.iloc[i, 1]).strip().lower()[:3]]
        dep = d.iloc[i, 2]
        if anio and mes and pd.notna(dep) and pd.notna(d.iloc[i, 5]):
            try:
                filas.append((pd.Timestamp(year=anio, month=mes, day=1), str(dep).strip(), float(d.iloc[i, 3]) if pd.notna(d.iloc[i, 3]) else np.nan,
                              float(d.iloc[i, 4]) if pd.notna(d.iloc[i, 4]) else np.nan, float(d.iloc[i, 5])))
            except ValueError:
                pass
    return pd.DataFrame(filas, columns=["fecha", "departamento", "granel_t", "empacado_t", "total_t"])


def main() -> None:
    print("== IPC (indice total, mensual)")
    s = ipc()
    s.to_csv(AQUI / "ipc_mensual.csv", index=False)
    print(f"  {len(s)} meses, {s.fecha.min():%Y-%m} a {s.fecha.max():%Y-%m}; ultimo indice {s.indice.iloc[-1]:.2f}, inflacion anual {s.var_anual_pct.iloc[-1]:.2f} %")
    meses = s.fecha.dt.year * 12 + s.fecha.dt.month
    verificar(bool((np.diff(meses) == 1).all()), "meses consecutivos sin huecos")
    verificar(bool((s.indice > 0).all()), "indices positivos")
    verificar(s.var_mensual_pct.abs().max() < 5, f"variacion mensual maxima razonable ({s.var_mensual_pct.abs().max():.2f} %)")

    print("\n== PIB trimestral, 12 agrupaciones (volumen encadenado base 2015)")
    p = pd.concat([pib("Cuadro 1", "original"), pib("Cuadro 4", "ajustado")])
    p.to_csv(AQUI / "pib_trimestral_12.csv", index=False)
    for ser in ("original", "ajustado"):
        q = p[p.serie == ser]
        print(f"  {ser}: {q.concepto.nunique()} conceptos, {q.anio.min()}-{q.anio.max()}, {len(q)} valores; ultimo trimestre {q.anio.max()} T{q[q.anio == q.anio.max()].trimestre.max()}")
    q = p[p.serie == "original"]
    tot = q[q.concepto.str.contains("Producto Interno Bruto")].sort_values(["anio", "trimestre"])
    verificar(len(tot) > 80, f"serie del PIB total con {len(tot)} trimestres")
    verificar(bool((tot.valor_miles_millones_2015 > 0).all()), "PIB positivo")
    anual = tot.groupby("anio").valor_miles_millones_2015.sum()
    print(f"  PIB anual (suma de trimestres, miles de millones de 2015): 2019 {anual.get(2019, np.nan):,.0f} | 2020 {anual.get(2020, np.nan):,.0f} | 2023 {anual.get(2023, np.nan):,.0f}")
    verificar(anual.get(2020, 0) < anual.get(2019, 1), "2020 (pandemia) cae frente a 2019: coherente con lo conocido")

    print("\n== Cemento gris")
    cn = cemento_nacional()
    cn.to_csv(AQUI / "cemento_nacional_mensual.csv", index=False)
    cd = cemento_departamento()
    cd.to_csv(AQUI / "cemento_departamento_mensual.csv", index=False)
    print(f"  nacional: {len(cn)} meses, {cn.fecha.min():%Y-%m} a {cn.fecha.max():%Y-%m}")
    print(f"  por departamento: {len(cd)} filas, {cd.departamento.nunique()} departamentos, {cd.fecha.min():%Y-%m} a {cd.fecha.max():%Y-%m}")
    s_dep = cd.groupby("fecha").total_t.sum()
    comun = cn.set_index("fecha").despachos_nacionales_t.reindex(s_dep.index).dropna()
    rel = (s_dep.reindex(comun.index) / comun)
    verificar(bool(rel.between(0.97, 1.03).mean() > 0.95), f"suma de despachos por departamento vs total nacional: razon mediana {rel.median():.3f}; "
              f"{100 * rel.between(0.97, 1.03).mean():.0f} % de los meses dentro de ±3 %")
    print(f"  Despachos nacionales 2022: {cn[cn.fecha.dt.year == 2022].despachos_nacionales_t.sum() / 1e6:.2f} Mt; 2024: {cn[cn.fecha.dt.year == 2024].despachos_nacionales_t.sum() / 1e6:.2f} Mt")
    print("\nRESULTADO:", "todas las verificaciones pasaron" if OK else "HAY VERIFICACIONES FALLIDAS: no usar las series sin revisar")


if __name__ == "__main__":
    main()
