"""
Limpieza y perfil de SECOP II (contratos y procesos de obra) y regalías (SGR), para decidir qué sirve a StructAI.

Entrada: scripts/ingesta/secop_sgr/raw/*.csv (de descargar.py; sin datos personales).
Salida:  scripts/ingesta/secop_sgr/salida/*.csv (tablas limpias) y docs/presupuesto/SECOP_SGR_PERFIL.md (solo agregados).

Principios:
- Se reportan AGREGADOS (por año, departamento, tipo de obra, modalidad). El documento público no nombra entidades
  ni proveedores: una señal de riesgo no es evidencia de una irregularidad.
- Limpieza explícita y reversible: cada regla marca una columna `bandera_*`; nada se borra en silencio.

Uso: python scripts/ingesta/secop_sgr/perfil_secop_sgr.py
"""
from __future__ import annotations

import collections
import math
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
RAW = AQUI / "raw"
SAL = AQUI / "salida"
INFORME = RAIZ / "docs" / "presupuesto" / "SECOP_SGR_PERFIL.md"
TOPE_VALOR = 5e12          # 5 billones COP: por encima, casi seguro error de digitación para un contrato de obra
RX_CANTIDAD = re.compile(
    r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*(km|kms|kil[oó]metros?|m2|m²|mts2|metros cuadrados|ml|"
    r"metros lineales|m3|m³|metros c[uú]bicos)\b", re.I)
RX_BPIN = re.compile(r"\b(20\d{11}|20\d{13})\b")
TIPOS = [("vía terciaria / placa huella", r"placa[- ]?huella|v[ií]as? terciari|v[ií]a rural|veredal"),
         ("pavimentación urbana / vías", r"pavimenta|rehabilitaci[oó]n vial|malla vial|v[ií]as? urban|calle|carrera|carretera|v[ií]a"),
         ("puente", r"\bpuente|box ?culvert|pont[oó]n"),
         ("acueducto / alcantarillado / saneamiento", r"acueducto|alcantarillad|ptar|ptap|saneamiento|agua potable|colector|redes? hidr"),
         ("edificación educativa", r"colegio|instituci[oó]n educativa|escuela|aulas?|sede educativa|universidad"),
         ("vivienda", r"vivienda|mejoramiento de vivienda|unidades habitacionales"),
         ("salud", r"hospital|centro de salud|puesto de salud|ese "),
         ("deportivo / espacio público", r"polideportivo|cancha|parque|coliseo|placa deportiva|espacio p[uú]blico|and[eé]n"),
         ("edificación institucional / otra", r"edificio|sede|casa de la cultura|plaza de mercado|cementerio|biblioteca")]


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def tipo_obra(texto: str) -> str:
    t = norm(texto)
    for nombre, rx in TIPOS:
        if re.search(rx, t):
            return nombre
    return "otro / sin clasificar"


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def fecha(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=True)


def cantidad(texto: str):
    m = RX_CANTIDAD.search(texto or "")
    if not m:
        return None, None
    v = m.group(1)
    v = v.replace(".", "").replace(",", ".") if re.search(r"\d\.\d{3}", v) else v.replace(",", ".")
    try:
        v = float(v)
    except ValueError:
        return None, None
    u = norm(m.group(2))
    u = "km" if u.startswith(("km", "kil")) else "m2" if u in ("m2", "m²", "mts2", "metros cuadrados") else \
        "ml" if u in ("ml", "metros lineales") else "m3"
    return v, u


def pct(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.1%}"


def main() -> None:
    SAL.mkdir(exist_ok=True)
    L = ["# SECOP II y regalías: limpieza, calidad y qué sirve a StructAI", "",
         "Generado por `scripts/ingesta/secop_sgr/perfil_secop_sgr.py` sobre la descarga acotada (≤ 1 GB, sin datos "
         "personales). Solo agregados: **ninguna entidad ni proveedor se nombra**. Una señal de riesgo es una "
         "característica estadística del proceso, **no evidencia de irregularidad**.", ""]

    # ── SECOP II contratos de obra ──────────────────────────────────────────────────────────
    c = pd.read_csv(RAW / "secop2_contratos_obra.csv", dtype=str, keep_default_na=False)
    n0 = len(c)
    c["valor"] = num(c["valor_del_contrato"])
    c["pagado"] = num(c["valor_pagado"])
    c["dias_adic"] = num(c["dias_adicionados"])
    c["firma"] = fecha(c["fecha_de_firma"])
    c["inicio"] = fecha(c["fecha_de_inicio_del_contrato"])
    c["fin"] = fecha(c["fecha_de_fin_del_contrato"])
    c["anio"] = c["firma"].dt.year
    c["texto"] = c["objeto_del_contrato"] + " " + c["descripcion_del_proceso"]
    c["tipo_obra"] = c["texto"].map(tipo_obra)
    q = c["texto"].map(cantidad)
    c["cantidad"] = [x[0] for x in q]
    c["unidad_cant"] = [x[1] for x in q]
    c["bpin_mencionado"] = c["texto"].map(lambda t: (RX_BPIN.search(t) or [None])[0] if RX_BPIN.search(t) else None)
    c["bandera_duplicado"] = c.duplicated("id_contrato", keep="first")
    c["bandera_valor_invalido"] = (c["valor"].isna()) | (c["valor"] <= 0) | (c["valor"] > TOPE_VALOR)
    c["bandera_fechas"] = (c["fin"] < c["inicio"]) | c["firma"].isna()
    c["bandera_sin_ciudad"] = c["ciudad"].str.lower().isin(["", "no definido", "no definida"])
    c["bandera_pagado_mayor"] = c["pagado"] > c["valor"] * 1.0001
    limpio = c[~(c["bandera_duplicado"] | c["bandera_valor_invalido"] | c["bandera_fechas"])].copy()
    L += ["## 1. SECOP II, contratos de obra", "",
          f"Filas descargadas: **{n0:,}**. Después de limpieza (sin duplicados, valor válido entre 0 y 5 billones, "
          f"fechas coherentes): **{len(limpio):,}** ({len(limpio) / n0:.0%}).", "",
          "| Problema de calidad | Contratos | % |", "|---|---|---|"]
    for b, nom in [("bandera_duplicado", "id de contrato duplicado"), ("bandera_valor_invalido", "valor nulo, ≤ 0 o > 5 billones"),
                   ("bandera_fechas", "sin fecha de firma o fin antes del inicio"), ("bandera_sin_ciudad", "ciudad 'No definido'"),
                   ("bandera_pagado_mayor", "valor pagado mayor que el del contrato")]:
        L.append(f"| {nom} | {int(c[b].sum()):,} | {c[b].mean():.1%} |")
    grande = c.loc[c["valor"] > TOPE_VALOR, "valor"]
    L += ["", f"Valores > 5 billones: {len(grande)} (el mayor: {grande.max():.3g} COP), seguramente errores de digitación; "
          "son los que inflaban la suma de 2024.", ""]
    por_anio = limpio.groupby("anio").agg(n=("id_contrato", "size"), valor=("valor", "sum"), mediana=("valor", "median"))
    L += ["| Año de firma | Contratos | Valor total (billones) | Mediana por contrato (millones) |", "|---|---|---|---|"]
    for a, r in por_anio.iterrows():
        if not math.isnan(a):
            L.append(f"| {int(a)} | {int(r.n):,} | {r.valor / 1e12:.2f} | {r.mediana / 1e6:,.0f} |")
    tipos = limpio.groupby("tipo_obra").agg(n=("id_contrato", "size"), valor=("valor", "sum")).sort_values("n", ascending=False)
    L += ["", "Tipo de obra (por palabras clave en el objeto; línea base):", "", "| Tipo | Contratos | Valor (billones) |", "|---|---|---|"]
    for t, r in tipos.iterrows():
        L.append(f"| {t} | {int(r.n):,} | {r.valor / 1e12:.2f} |")

    # Aprovechables para StructAI
    con_cant = limpio[limpio["cantidad"].notna() & (limpio["cantidad"] > 0)].copy()
    con_cant["costo_unitario"] = con_cant["valor"] / con_cant["cantidad"]
    L += ["", "### Qué se puede aprovechar", "",
          f"- **Cantidad en el objeto** (km, m², ml, m³): **{len(con_cant):,}** contratos "
          f"({len(con_cant) / len(limpio):.1%}). Con valor ÷ cantidad sale un **costo paramétrico** por tipo de obra, "
          "región y año, útil para estimar y para revisar presupuestos (#196).",
          f"- **BPIN mencionado en el texto**: **{limpio['bpin_mencionado'].notna().sum():,}** contratos, que se pueden "
          "enlazar con regalías (sección 3).",
          f"- **Fuente de recursos**: {(num(limpio['sistema_general_de_regal_as']) > 0).sum():,} contratos con aporte del SGR.", ""]
    cu = con_cant[(con_cant["unidad_cant"] == "km") & con_cant["tipo_obra"].isin(["vía terciaria / placa huella", "pavimentación urbana / vías"])]
    cu = cu[(cu["costo_unitario"] > 5e7) & (cu["costo_unitario"] < 2e10)]      # 50 M – 20 mil M por km: rango plausible
    if len(cu) >= 20:
        g = cu.groupby("tipo_obra")["costo_unitario"].describe(percentiles=[.25, .5, .75])
        L += ["Ejemplo de costo paramétrico (vías con cantidad en km, filtrado a 50 M–20.000 M COP/km, años mezclados, sin "
              "indexar):", "", "| Tipo | Contratos | P25 (M/km) | Mediana (M/km) | P75 (M/km) |", "|---|---|---|---|---|"]
        for t, r in g.iterrows():
            L.append(f"| {t} | {int(r['count'])} | {r['25%'] / 1e6:,.0f} | {r['50%'] / 1e6:,.0f} | {r['75%'] / 1e6:,.0f} |")
        L.append("")
    limpio[["id_contrato", "proceso_de_compra", "departamento", "ciudad", "anio", "tipo_obra", "modalidad_de_contratacion",
            "valor", "pagado", "dias_adic", "cantidad", "unidad_cant", "bpin_mencionado", "es_pyme", "urlproceso"]] \
        .to_csv(SAL / "secop2_contratos_obra_limpio.csv", index=False)

    # ── SECOP II procesos de obra: competencia y descuento frente al presupuesto oficial ─────
    p = pd.read_csv(RAW / "secop2_procesos_obra.csv", dtype=str, keep_default_na=False)
    p["precio_base"] = num(p["precio_base"])
    p["adjudicado_valor"] = num(p["valor_total_adjudicacion"])
    p["ofertas"] = num(p["respuestas_al_procedimiento"])
    p["oferentes_unicos"] = num(p["proveedores_unicos_con"])
    p["publicacion"] = fecha(p["fecha_de_publicacion_del"])
    p["anio"] = p["publicacion"].dt.year
    p["tipo_obra"] = (p["nombre_del_procedimiento"] + " " + p["descripci_n_del_procedimiento"]).map(tipo_obra)
    adj = p[(p["adjudicado"].str.lower() == "si") & (p["precio_base"] > 0) & (p["adjudicado_valor"] > 0)
            & (p["precio_base"] < TOPE_VALOR) & (p["adjudicado_valor"] < TOPE_VALOR)].copy()
    adj = adj.drop_duplicates("id_del_proceso")
    adj["descuento"] = 1 - adj["adjudicado_valor"] / adj["precio_base"]
    adj = adj[(adj["descuento"] > -0.5) & (adj["descuento"] < 0.9)]
    adj["un_oferente"] = adj["ofertas"] == 1
    L += ["## 2. SECOP II, procesos de obra: competencia y descuento", "",
          f"Procesos descargados: **{len(p):,}**; adjudicados con presupuesto oficial y valor adjudicado válidos: **{len(adj):,}**.", "",
          "| Modalidad | Procesos | Mediana de descuento frente al presupuesto oficial | Un solo oferente |", "|---|---|---|---|"]
    for mod, g in adj.groupby("modalidad_de_contratacion"):
        if len(g) >= 50:
            L.append(f"| {mod} | {len(g):,} | {g['descuento'].median():.1%} | {g['un_oferente'].mean():.0%} |")
    L += ["", "| Tipo de obra | Procesos | Mediana de descuento | Un solo oferente | Mediana de ofertas |", "|---|---|---|---|---|"]
    for t, g in adj.groupby("tipo_obra"):
        L.append(f"| {t} | {len(g):,} | {g['descuento'].median():.1%} | {g['un_oferente'].mean():.0%} | {g['ofertas'].median():.0f} |")
    corr = adj[["ofertas", "descuento"]].dropna()
    if len(corr) > 100:
        from scipy.stats import spearmanr
        rho = spearmanr(corr["ofertas"], corr["descuento"]).statistic
        L += ["", f"**Hipótesis de competencia:** a más ofertas, mayor descuento frente al presupuesto oficial. "
              f"Spearman ρ(ofertas, descuento) = **{rho:.2f}** (n = {len(corr):,}).", ""]
    adj[["id_del_proceso", "id_del_portafolio", "departamento_entidad", "anio", "tipo_obra", "modalidad_de_contratacion",
         "precio_base", "adjudicado_valor", "descuento", "ofertas", "oferentes_unicos", "urlproceso"]] \
        .to_csv(SAL / "secop2_procesos_obra_limpio.csv", index=False)
    union = limpio.merge(adj[["id_del_portafolio", "precio_base", "ofertas", "descuento"]],
                         left_on="proceso_de_compra", right_on="id_del_portafolio", how="inner")
    L += [f"Enlace contrato ↔ proceso (`proceso_de_compra` = `id_del_portafolio`): **{len(union):,}** contratos con su "
          "presupuesto oficial y su número de ofertas.", ""]
    if len(union) > 200:
        union["con_adicion"] = union["dias_adic"] > 0
        g = union.groupby(union["ofertas"] == 1)["con_adicion"].mean()
        L += [f"Contratos con días adicionados: {pct(g.get(True))} con un solo oferente frente a "
              f"{pct(g.get(False))} con dos o más. Es una asociación, no una causa.", ""]

    # ── Regalías ──────────────────────────────────────────────────────────────────────────
    s = pd.read_csv(RAW / "sgr_proyectos.csv", dtype=str, keep_default_na=False)
    s["valor"] = num(s["valortotal"])
    s["fisica"] = num(s["ejecucionfisica"])
    s["financiera"] = num(s["ejecucionfinanciera"])
    s["brecha"] = s["financiera"] - s["fisica"]
    L += ["## 3. Regalías (SGR)", "", f"Proyectos: **{len(s):,}**; BPIN duplicados: {s['codigobpin'].duplicated().sum():,}.", "",
          "| Sector | Proyectos | Valor (billones) | Mediana ejecución física | Mediana ejecución financiera | Financiera > física + 20 pp |",
          "|---|---|---|---|---|---|"]
    for sec, g in s.groupby("sector"):
        if len(g) >= 300:
            L.append(f"| {sec} | {len(g):,} | {g['valor'].sum() / 1e12:.2f} | {g['fisica'].median():.0f} % | "
                     f"{g['financiera'].median():.0f} % | {(g['brecha'] > 20).mean():.0%} |")
    enlaces = limpio["bpin_mencionado"].dropna().isin(set(s["codigobpin"])).sum()
    L += ["", f"Contratos de SECOP II cuyo texto cita un BPIN que existe en el listado del SGR: **{enlaces:,}**.", ""]
    s.to_csv(SAL / "sgr_proyectos_limpio.csv", index=False)
    dnp = RAW / "dnp_proyectos_infraestructura.csv"
    if dnp.exists():
        d = pd.read_csv(dnp, dtype=str, keep_default_na=False)
        L += [f"Proyectos de inversión del DNP (infraestructura): **{len(d):,}**; por sector: " +
              ", ".join(f"{k} {v:,}" for k, v in d["sector"].value_counts().head(6).items()) + ".", ""]

    tam = sum(f.stat().st_size for f in RAW.glob("*.csv")) / 1e6
    L += ["## 4. Tamaño", "", f"Descarga en `raw/`: **{tam:.0f} MB** (tope 1.024 MB).", ""]
    INFORME.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
