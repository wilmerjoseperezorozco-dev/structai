"""
Integrantes de consorcios y uniones temporales de SECOP II → experiencia atribuida a cada firma (issue #218).

Hoy los anillos 1 y 2 (anillos_clientes.py) excluyen los contratos firmados por un grupo (es_grupo = Si): 19.610
contratos, 22–35 % del total. Este script los reparte entre sus integrantes:

  1. Descarga de "Grupos de Proveedores - SECOP II" (datos.gov.co, ceth-n4bn, CC BY-SA 4.0) SOLO los grupos que
     aparecen en los contratos ya descargados (enlace: contratos.codigo_proveedor = grupos.codigo_grupo), en lotes
     filtrados, con reanudación. Columnas: grupo, NIT del grupo, tipo, fecha, integrante, NIT, tipo de empresa,
     participación y líder. NO se piden representante legal, teléfonos, correos, direcciones ni sitio web.
  2. Integrantes persona natural (NIT que no empieza por 8 o 9): nombre y documento se reemplazan al escribir por
     el seudónimo HMAC de descargar.py (misma clave, _privado/clave_seudonimo.bin). Nunca entran a la lista.
  3. Atribución: cada contrato del grupo suma 1 "participación en contrato" a cada firma integrante y su valor
     ponderado por el % de participación (si los % no suman 100 se normalizan; si faltan, partes iguales).
  4. Red de alianzas, solo en agregado: tamaño de los grupos, socios por firma, firmas "ancla", regiones.
     Una alianza no es una señal de riesgo y no se califica ninguna conducta.

Salidas:
  raw/secop2_grupos_integrantes.csv          descarga (gitignored)
  _privado/experiencia_consorcios.csv        por firma y anillo: contratos en grupo, valor ponderado, liderazgos
  salida/CONSORCIOS_SECOP.md                 solo agregados

Uso: python consorcios.py [--sin-descarga]   (después: python anillos_clientes.py para integrar la experiencia)
"""
from __future__ import annotations

import argparse
import csv
import io
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import httpx

from descargar import clave, seudonimo

AQUI = Path(__file__).parent
RAW, PRIVADO, SALIDA = AQUI / "raw", AQUI / "_privado", AQUI / "salida"
DESTINO = RAW / "secop2_grupos_integrantes.csv"
MARCA = RAW / "secop2_grupos_integrantes.completo"
API = "https://www.datos.gov.co/resource/ceth-n4bn.csv"
COLUMNAS = ["codigo_grupo", "nombre_grupo", "nit_grupo", "tipo_empresa_grupo", "esta_activo", "fecha_creaci_n_grupo",
            "departamento_grupo", "codigo_participante", "nombre_participante", "nit_participante",
            "tipo_empresa_participante", "participacion", "es_lider_del_grupo"]
CONTRATOS = {"anillo_1": RAW / "secop2_contratos_interventoria_consultoria.csv",
             "anillo_2": RAW / "secop2_contratos_obra.csv"}
LOTE = 150
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def nit9(doc: str) -> str | None:
    d = "".join(ch for ch in (doc or "") if ch.isdigit())
    return d[:9] if len(d) >= 9 and d[0] in "89" else None


def num(s: str) -> float:
    try:
        return max(float(s or 0), 0.0)
    except ValueError:
        return 0.0


def contratos_de_grupo() -> list[dict]:
    filas = []
    for anillo, ruta in CONTRATOS.items():
        with ruta.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("es_grupo") == "Si" and r.get("codigo_proveedor"):
                    filas.append({"anillo": anillo, "codigo": r["codigo_proveedor"].strip(),
                                  "valor": num(r["valor_del_contrato"]), "departamento": r["departamento"],
                                  "fecha": (r["fecha_de_firma"] or "")[:10], "tipo": r["tipo_de_contrato"]})
    return filas


# ── descarga ─────────────────────────────────────────────────────────────────────────────────────────────────────
def descargar(codigos: list[str]) -> None:
    if MARCA.exists():
        return
    k = clave()
    hechos = set()
    if DESTINO.exists():                                   # reanudación: códigos ya pedidos (con o sin integrantes)
        hechos = set((RAW / "secop2_grupos_pedidos.txt").read_text(encoding="utf-8").split()) \
            if (RAW / "secop2_grupos_pedidos.txt").exists() else set()
    pendientes = [c for c in sorted(set(codigos)) if c not in hechos and c.isdigit()]
    nuevo = not DESTINO.exists()
    with DESTINO.open("a", newline="", encoding="utf-8") as fh, \
            (RAW / "secop2_grupos_pedidos.txt").open("a", encoding="utf-8") as fp, httpx.Client(timeout=120) as cli:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        if nuevo:
            w.writeheader()
        for i in range(0, len(pendientes), LOTE):
            lote = pendientes[i:i + LOTE]
            donde = "codigo_grupo in(" + ",".join(f"'{c}'" for c in lote) + ")"
            offset = 0
            while True:
                r = cli.get(API, params={"$select": ",".join(COLUMNAS), "$where": donde, "$limit": 50000,
                                         "$offset": offset, "$order": "codigo_grupo,codigo_participante"})
                r.raise_for_status()
                filas = list(csv.DictReader(io.StringIO(r.text)))
                for f in filas:
                    if not nit9(f["nit_participante"]):        # persona natural u otro documento → seudónimo
                        s = seudonimo(k, f["nit_participante"] or f["codigo_participante"])
                        f["nit_participante"], f["nombre_participante"] = s, s
                    w.writerow(f)
                if len(filas) < 50000:
                    break
                offset += 50000
            fh.flush()
            fp.write("\n".join(lote) + "\n")
            fp.flush()
            print(f"  lotes {i // LOTE + 1}/{-(-len(pendientes) // LOTE)}", flush=True)
    MARCA.write_text(f"{date.today().isoformat()} {len(set(codigos))} grupos pedidos ceth-n4bn\n", encoding="utf-8")


# ── atribución y red ─────────────────────────────────────────────────────────────────────────────────────────────
def integrantes() -> dict[str, list[dict]]:
    g = defaultdict(dict)
    with DESTINO.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            g[r["codigo_grupo"]][r["nit_participante"]] = r     # un integrante una vez por grupo
    return {k: list(v.values()) for k, v in g.items()}


def pesos(miembros: list[dict]) -> list[float]:
    p = [num(m["participacion"]) for m in miembros]
    s = sum(p)
    return [x / s for x in p] if s > 0 else [1 / len(miembros)] * len(miembros)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-descarga", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    contratos = contratos_de_grupo()
    if not a.sin_descarga:
        descargar([c["codigo"] for c in contratos])
    grupos = integrantes()

    exp = defaultdict(lambda: {"razon": Counter(), "contratos": 0, "valor": 0.0, "lider": 0, "socios": set(),
                               "deptos": Counter(), "ultimo": ""})
    rep = Counter()
    tam = []
    pares = Counter()
    socios_pn = Counter()
    deptos_alianza = Counter()
    suma_part = Counter()
    for c in contratos:
        rep[f"{c['anillo']}_contratos"] += 1
        m = grupos.get(c["codigo"])
        if not m:
            rep[f"{c['anillo']}_sin_integrantes"] += 1
            continue
        rep[f"{c['anillo']}_resueltos"] += 1
        tam.append(len(m))
        s = sum(num(x["participacion"]) for x in m)
        suma_part["100" if abs(s - 100) < 0.5 else "0/sin dato" if s == 0 else "otra"] += 1
        juridicas = [x["nit_participante"] for x in m if nit9(x["nit_participante"])]
        socios_pn["con_persona_natural" if len(juridicas) < len(m) else "solo_juridicas"] += 1
        deptos_alianza[c["departamento"]] += 1
        for x, w in zip(m, pesos(m)):
            n = nit9(x["nit_participante"])
            if not n:
                continue
            k = (c["anillo"], n)
            e = exp[k]
            e["razon"][(x["nombre_participante"] or "").strip().upper()] += 1
            e["contratos"] += 1
            e["valor"] += c["valor"] * w
            e["lider"] += x["es_lider_del_grupo"].lower().startswith("v")
            e["socios"].update(j for j in juridicas if j != n)
            e["deptos"][c["departamento"]] += 1
            e["ultimo"] = max(e["ultimo"], c["fecha"])
        for i, p in enumerate(sorted(juridicas)):
            for q in sorted(juridicas)[i + 1:]:
                pares[(p, q)] += 1

    PRIVADO.mkdir(exist_ok=True)
    with (PRIVADO / "experiencia_consorcios.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["anillo", "nit", "razon_social", "contratos_en_grupo", "valor_ponderado_cop", "veces_lider",
                    "socios_distintos", "departamento_principal", "ultimo_contrato_en_grupo"])
        for (anillo, n), e in sorted(exp.items(), key=lambda kv: (kv[0][0], -kv[1]["valor"])):
            w.writerow([anillo, n, e["razon"].most_common(1)[0][0], e["contratos"], round(e["valor"]), e["lider"],
                        len(e["socios"]), e["deptos"].most_common(1)[0][0], e["ultimo"]])

    # ── agregados publicables ──
    try:
        base = {}
        with (PRIVADO / "prospectos_anillos_1_2.csv").open(encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                base[(r["anillo"], r["nit"])] = r
    except FileNotFoundError:
        base = {}
    L = ["# Consorcios y uniones temporales en SECOP II — agregados (#218)", "",
         f"Generado por `consorcios.py` el {date.today().isoformat()}. Fuente de integrantes: Grupos de Proveedores - "
         "SECOP II (`ceth-n4bn`). Solo agregados; la experiencia por firma está en `_privado/`. Las personas naturales "
         "integrantes están seudonimizadas y no se cuentan como firmas. Una alianza no es una señal de riesgo.", ""]
    for anillo, titulo in (("anillo_1", "Anillo 1 — interventoría y consultoría"), ("anillo_2", "Anillo 2 — obra")):
        firmas = {n for (an, n) in exp if an == anillo}
        nuevas = {n for n in firmas if (anillo, n) not in base}
        tot = rep[f"{anillo}_contratos"]
        L += [f"## {titulo}", "",
              f"- Contratos firmados por un grupo: {tot:,}; con integrantes encontrados: "
              f"**{rep[f'{anillo}_resueltos']:,}** ({rep[f'{anillo}_resueltos'] / max(1, tot):.1%}).",
              f"- Firmas (persona jurídica) con experiencia atribuida: **{len(firmas):,}**, de ellas **{len(nuevas):,} "
              "no aparecían** en el anillo porque solo contratan en grupo.",
              f"- Valor ponderado atribuido: {sum(e['valor'] for (an, _), e in exp.items() if an == anillo) / 1e12:,.2f} "
              "billones de COP.", ""]
    socios = [len(e["socios"]) for e in exp.values()]
    anclas = sum(1 for e in exp.values() if len(e["socios"]) >= 10)
    L += ["## Red de alianzas (agregado)", "",
          f"- Integrantes por grupo: mediana {statistics.median(tam) if tam else 0:.0f}; "
          f"2 integrantes: {sum(t == 2 for t in tam) / max(1, len(tam)):.0%}; 3: {sum(t == 3 for t in tam) / max(1, len(tam)):.0%}; "
          f"4 o más: {sum(t >= 4 for t in tam) / max(1, len(tam)):.0%}.",
          f"- Grupos con al menos una persona natural: {socios_pn['con_persona_natural'] / max(1, sum(socios_pn.values())):.0%}.",
          f"- Participaciones que suman 100 %: {suma_part['100'] / max(1, sum(suma_part.values())):.0%} "
          f"(sin dato: {suma_part['0/sin dato'] / max(1, sum(suma_part.values())):.0%}; en esos casos se reparte en partes iguales).",
          f"- Socios distintos por firma: mediana {statistics.median(socios) if socios else 0:.0f}; firmas \"ancla\" "
          f"(≥ 10 socios distintos): **{anclas:,}**.",
          f"- Pares de firmas que se han asociado: {len(pares):,}; repiten alianza (≥ 2 contratos juntos): "
          f"{sum(v >= 2 for v in pares.values()):,}.", "",
          "| Departamento del contrato | Contratos en grupo |", "|---|---|"]
    L += [f"| {d or '(vacío)'} | {v:,} |" for d, v in deptos_alianza.most_common(10)]
    L += ["", "## Limitaciones", "",
          "- La participación es la registrada en SECOP II al crear el grupo; no refleja cambios posteriores.",
          "- El valor atribuido es valor contratado ponderado, no ingreso ni utilidad de la firma.",
          "- Un mismo contrato cuenta como experiencia para cada integrante (no se divide el número de contratos).", ""]
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "CONSORCIOS_SECOP.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
