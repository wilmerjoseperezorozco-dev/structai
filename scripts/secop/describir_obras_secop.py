"""Descripcion de la realidad de los contratos de OBRA de SECOP II (issue #95/#98), ANTES de
calibrar detectores. Solo columnas no personales; sin identidad de proveedores. Salida: agregados.

Que mide (y que no):
- Calidad: duplicados, fechas imposibles, valores atipicos/absurdos (errores de captura).
- Senales con tasas base e intervalos de Wilson: contratos con dias adicionados, con adicion en
  valor, con suspension, estado "Modificado"; anticipos; amortizacion; avance real vs esperado;
  sanciones.
- NO prueba causas: una prorroga o adicion puede ser legitima.

Uso: python scripts/secop/describir_obras_secop.py  ->  scripts/secop/informe_obras_secop.md
"""
from __future__ import annotations

import io
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "eval-stats" / "src"))
import estadistica as est  # noqa: E402

LIN: list[str] = []
HOY = date.today()
VALOR_ABSURDO = 1e13          # 10 billones de pesos: ningun contrato de obra individual razonable
Y_MIN, Y_MAX = 2012, 2027


def out(t: str = "") -> None:
    print(t)
    LIN.append(t)


def jl(f: str) -> list[dict]:
    p = CACHE / f
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def fnum(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def fecha(x) -> date | None:
    try:
        return datetime.fromisoformat(str(x)[:10]).date()
    except ValueError:
        return None


def tasa(k: int, n: int) -> str:
    if n == 0:
        return "—"
    lo, hi = est.ic_wilson(k, n)
    d = 2 if 100 * k / n < 1 else 1
    return f"{100 * k / n:.{d}f} % [{100 * lo:.{d}f}, {100 * hi:.{d}f}] (n={n})"


def main() -> None:
    cs = jl("contratos_obra.jsonl")
    ad = jl("adiciones.jsonl")
    ej = jl("ejecucion.jsonl")
    mu = jl("multas_ii.jsonl")
    out("# Contratos de obra de SECOP II: descripcion de la realidad (borrador reproducible)\n")
    out(f"Generado: {HOY}. Solo columnas no personales. Fuente: datos.gov.co (SECOP II), sin identidad de proveedores.\n")

    out("## 1. Inventario y calidad")
    ids = Counter(c["id_contrato"] for c in cs)
    dups = sum(n - 1 for n in ids.values() if n > 1)
    out(f"- Contratos de obra: **{len(cs)}**; ids repetidos: **{dups}**.")
    val = np.array([fnum(c.get("valor_del_contrato")) for c in cs])
    ok = ~np.isnan(val)
    out(f"- Valor del contrato faltante: {int((~ok).sum())}; en cero: {int((val[ok] == 0).sum())}; "
        f"**> {VALOR_ABSURDO:.0e} COP (probable error de captura): {int((val[ok] > VALOR_ABSURDO).sum())}**; negativos: {int((val[ok] < 0).sum())}.")
    f_firma = [fecha(c.get("fecha_de_firma")) for c in cs]
    f_ini = [fecha(c.get("fecha_de_inicio_del_contrato")) for c in cs]
    f_fin = [fecha(c.get("fecha_de_fin_del_contrato")) for c in cs]
    fuera = sum(1 for d in f_firma if d and not (Y_MIN <= d.year <= Y_MAX))
    inv = sum(1 for a, b in zip(f_ini, f_fin) if a and b and b < a)
    nul = sum(1 for d in f_firma if d is None)
    out(f"- Fecha de firma nula: {nul}; fuera de {Y_MIN}-{Y_MAX}: {fuera}; fin anterior al inicio: **{inv}**.")
    pag = np.array([fnum(c.get("valor_pagado")) for c in cs])
    out(f"- Pagado mayor que el valor del contrato (pagado > 1,5 x valor, ambos > 0): "
        f"{int(((pag > 1.5 * val) & (val > 0) & ~np.isnan(pag)).sum())}.\n")

    valido = [c for c, v in zip(cs, val) if not math.isnan(v) and 0 < v <= VALOR_ABSURDO]
    v = np.array([fnum(c["valor_del_contrato"]) for c in valido])
    q = np.percentile(v, [5, 25, 50, 75, 95])
    out("### Valor del contrato (COP, sin atipicos absurdos ni ceros)")
    out(f"n = {len(v)}; mediana **{q[2] / 1e6:,.0f} M** [p5 {q[0] / 1e6:,.1f} M, p25 {q[1] / 1e6:,.0f} M, p75 {q[3] / 1e6:,.0f} M, p95 {q[4] / 1e6:,.0f} M]; "
        f"asimetria muy fuerte (media {v.mean() / 1e6:,.0f} M).\n")

    out("## 2. Estado y años")
    out("| estado | contratos | % |\n|---|---|---|")
    ec = Counter(c.get("estado_contrato") for c in cs)
    for e, n in ec.most_common():
        out(f"| {e} | {n} | {100 * n / len(cs):.1f} |")
    out()
    ya = Counter(d.year for d in f_firma if d)
    out("Contratos por año de firma: " + ", ".join(f"{a}: {ya[a]}" for a in sorted(ya) if 2015 <= a <= 2026) + "\n")

    out("## 3. Señales de modificacion (tasas base con intervalo de Wilson)")
    por_c = defaultdict(Counter)
    for a in ad:
        por_c[a["id_contrato"]][a.get("tipo")] += 1
    n = len(cs)
    con_dias = sum(1 for c in cs if fnum(c.get("dias_adicionados")) > 0)
    con_valor = sum(1 for c in cs if por_c[c["id_contrato"]].get("Adicion en el valor", 0) > 0)
    con_susp = sum(1 for c in cs if por_c[c["id_contrato"]].get("Suspensión", 0) > 0)
    con_react = sum(1 for c in cs if por_c[c["id_contrato"]].get("Reactivación", 0) > 0)
    con_mod = sum(1 for c in cs if c.get("estado_contrato") == "Modificado")
    out(f"- Con días adicionados > 0: **{tasa(con_dias, n)}**")
    out(f"- Con al menos una adición en el valor: **{tasa(con_valor, n)}**")
    out(f"- Con suspensión: {tasa(con_susp, n)}; con reactivación: {tasa(con_react, n)}")
    out(f"- En estado 'Modificado': {tasa(con_mod, n)}")
    dias = np.array([fnum(c.get("dias_adicionados")) for c in cs])
    dpos = dias[(dias > 0) & ~np.isnan(dias)]
    out(f"- Entre los que tienen días adicionados (n={len(dpos)}): mediana {np.median(dpos):.0f} días, p90 {np.percentile(dpos, 90):.0f}, max {dpos.max():.0f}.")
    out("\nAdvertencia: la tabla de adiciones **no trae el monto**; 'adición en el valor' es un indicador, no una medida de sobrecosto. "
        "Una adición puede responder a un cambio de alcance legitimo.\n")

    out("## 4. Anticipos y amortizacion")
    con_ant = [c for c in cs if fnum(c.get("valor_de_pago_adelantado")) > 0]
    out(f"- Contratos con pago adelantado > 0: {tasa(len(con_ant), n)}.")
    cerr = [c for c in con_ant if c.get("estado_contrato") in ("terminado", "Cerrado")]
    sin_amort = [c for c in cerr if fnum(c.get("valor_amortizado")) < 0.99 * fnum(c["valor_de_pago_adelantado"])]
    cero_amort = [c for c in cerr if not fnum(c.get("valor_amortizado")) > 0]
    out(f"- Entre los terminados o cerrados con anticipo (n={len(cerr)}): amortizado < 99 % del anticipo: **{tasa(len(sin_amort), len(cerr))}**; "
        f"amortizado = 0: {tasa(len(cero_amort), len(cerr))}.")
    out("Advertencia: 'amortizado = 0' puede ser falta de reporte y no falta de amortizacion; el detector necesita validar contra el avance de ejecucion.\n")

    out("## 5. Avance de ejecucion (esperado vs real)")
    ult = {}
    for r in ej:
        a, b = fnum(r.get("porcentajedeavanceesperado")), fnum(r.get("porcentaje_de_avance_real"))
        fe = fecha(r.get("fechadeentregaesperada"))
        if math.isnan(a) or math.isnan(b) or fe is None or fe > HOY:
            continue
        k = r["identificadorcontrato"]
        if k not in ult or fe > ult[k][0]:
            ult[k] = (fe, a, b)
    out(f"- Contratos con al menos un hito vencido con avance esperado y real: {len(ult)} de {n}.")
    rezago = [(a, b) for (_, a, b) in ult.values() if a > 0]
    bajo = sum(1 for a, b in rezago if b < a)
    gran = sum(1 for a, b in rezago if b < 0.8 * a)
    out(f"- Último hito vencido con avance real < esperado: **{tasa(bajo, len(rezago))}**; con real < 80 % del esperado: {tasa(gran, len(rezago))}.")
    inc = sum(1 for (_, a, b) in ult.values() if a > 100 or b > 100)
    out(f"- Registros con porcentaje fuera de 0-100 (inconsistente): {inc}.\n")

    out("## 6. Sanciones (SECOP II)")
    ids_obra = set(ids)
    mo = [m for m in mu if m.get("id_contrato") in ids_obra]
    ep = Counter(m.get("estado") for m in mo)
    out(f"- Sanciones registradas en contratos de obra: **{len(mo)}** (de {len(mu)} en todo SECOP II).")
    out("- Por estado: " + ", ".join(f"{k}: {v}" for k, v in ep.most_common()) + ".")
    pub = sum(1 for m in mo if m.get("estado") == "Publicado por el administrador de la plataforma")
    out(f"- Solo las publicadas serian etiqueta utilizable: **{pub}** ({tasa(pub, n)} de los contratos de obra). "
        "Es una etiqueta demasiado escasa para entrenar un clasificador de sanciones.\n")

    out("## 7. Por departamento (contratos con dias adicionados)")
    dep = defaultdict(lambda: [0, 0])
    for c in cs:
        d = c.get("departamento") or "No definido"
        dep[d][0] += 1
        dep[d][1] += fnum(c.get("dias_adicionados")) > 0
    out("| departamento | contratos | con dias adicionados |\n|---|---|---|")
    for d, (t, k) in sorted(dep.items(), key=lambda x: -x[1][0])[:10]:
        out(f"| {d} | {t} | {tasa(k, t)} |")
    out("\nLimites: datos autorreportados por las entidades; errores de captura conocidos; los contratos 'En ejecución' aun no tienen resultado final.")
    (AQUI / "informe_obras_secop.md").write_text("\n".join(LIN), encoding="utf-8")


if __name__ == "__main__":
    main()
