"""
Anillos de clientes potenciales desde SECOP II (issue de segmentación de clientes, parte de #209).

  Anillo 1  firmas de interventoría y consultoría de ingeniería   (contratos tipo Interventoría / Consultoría)
  Anillo 2  contratistas de obra pública y licitantes            (contratos tipo Obra)
  (Anillos 3–5 —constructoras de edificación y vivienda, empresas de servicios públicos, curadurías,
   aseguradoras y laboratorios— necesitan la base cataliza-empresas por CIIU y listados oficiales; ver el issue.)

Reglas de datos:
  * Solo PERSONAS JURÍDICAS (NIT de 9 dígitos que empieza por 8 o 9). Las personas naturales ya llegan
    seudonimizadas desde descargar.py y aquí se excluyen: la Ley 1581 protege a las personas naturales, no a las
    empresas, y un contratista persona natural no es un prospecto B2B.
  * Los consorcios y uniones temporales (es_grupo = Si) no suman como contrato directo: su NIT es del grupo. Si
    existe _privado/experiencia_consorcios.csv (consorcios.py, #218) se suma a cada firma integrante su
    experiencia en grupo (contratos y valor ponderado por participación) en columnas aparte.
  * La lista por empresa (NIT + razón social, datos públicos de SECOP) va a _privado/ (gitignored): es una lista
    comercial, no se publica. El informe público solo lleva agregados.
  * Nada aquí califica conductas: el valor y la recurrencia describen tamaño y experiencia, no riesgo.

Uso: python anillos_clientes.py
"""
from __future__ import annotations

import csv
import re
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from procesos_obra_unspsc import etiquetar, norm

AQUI = Path(__file__).parent
RAW = AQUI / "raw"
PRIVADO = AQUI / "_privado"
SALIDA = AQUI / "salida"
RX_NIT_EMPRESA = re.compile(r"^[89]\d{8}")
csv.field_size_limit(10**9)

FUENTES = {
    "anillo_1": RAW / "secop2_contratos_interventoria_consultoria.csv",
    "anillo_2": RAW / "secop2_contratos_obra.csv",
}


def nit(doc: str) -> str | None:
    d = re.sub(r"\D", "", doc or "")
    return d[:9] if RX_NIT_EMPRESA.match(d) else None


def valor(s: str) -> float:
    try:
        return max(float(s or 0), 0.0)
    except ValueError:
        return 0.0


def tamano(v: float) -> str:
    # Rangos en COP de valor contratado acumulado en SECOP II (no son ingresos de la empresa)
    for tope, nombre in ((5e8, "<500M"), (5e9, "500M-5mil M"), (5e10, "5mil-50mil M")):
        if v < tope:
            return nombre
    return ">50mil M"


def construir(anillo: str, ruta: Path):
    emp = defaultdict(lambda: {"razon_social": Counter(), "contratos": 0, "valor": 0.0, "deptos": Counter(),
                               "tipos_obra": Counter(), "subtipo": Counter(), "ultimo": "", "pyme": Counter(),
                               "dias_adicionados": 0, "con_adicion": 0})
    rep = Counter()
    with ruta.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rep["contratos"] += 1
            if r.get("es_grupo") == "Si":
                rep["consorcio_o_union_temporal"] += 1
                continue
            n = nit(r["documento_proveedor"]) if (r["tipodocproveedor"] or "").upper().startswith("NIT") else None
            if not n:
                rep["no_persona_juridica"] += 1
                continue
            rep["persona_juridica"] += 1
            e = emp[n]
            e["razon_social"][(r["proveedor_adjudicado"] or "").strip().upper()] += 1
            e["contratos"] += 1
            e["valor"] += valor(r["valor_del_contrato"])
            e["deptos"][r["departamento"]] += 1
            texto = r["objeto_del_contrato"] or r["descripcion_del_proceso"]
            tipo, *_ = etiquetar(texto, r["codigo_de_categoria_principal"])
            e["tipos_obra"][tipo] += 1
            if anillo == "anillo_1":
                e["subtipo"][r["tipo_de_contrato"]] += 1
            e["ultimo"] = max(e["ultimo"], (r["fecha_de_firma"] or "")[:10])
            e["pyme"][r.get("es_pyme", "")] += 1
            d = valor(r.get("dias_adicionados"))
            e["dias_adicionados"] += d
            e["con_adicion"] += d > 0
    return emp, rep


def sumar_consorcios(anillo: str, emp: dict) -> int:
    """Agrega la experiencia en consorcios/UT (consorcios.py). Devuelve cuántas firmas eran nuevas en el anillo."""
    ruta = PRIVADO / "experiencia_consorcios.csv"
    if not ruta.exists():
        return 0
    nuevas = 0
    with ruta.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["anillo"] != anillo:
                continue
            nuevas += r["nit"] not in emp
            e = emp[r["nit"]]
            if not e["razon_social"]:
                e["razon_social"][r["razon_social"]] += 1
                e["deptos"][r["departamento_principal"]] += 1
            e["grupo_contratos"] = int(r["contratos_en_grupo"])
            e["grupo_valor"] = float(r["valor_ponderado_cop"])
            e["grupo_lider"] = int(r["veces_lider"])
            e["grupo_socios"] = int(r["socios_distintos"])
            e["ultimo"] = max(e["ultimo"], r["ultimo_contrato_en_grupo"])
    return nuevas


def fila(anillo, n, e):
    especialidad = [t for t, _ in e["tipos_obra"].most_common(3) if t != "sin_clasificar"]
    total = e["valor"] + e.get("grupo_valor", 0.0)
    return {"anillo": anillo, "nit": n, "razon_social": e["razon_social"].most_common(1)[0][0],
            "contratos": e["contratos"], "valor_cop": round(e["valor"]),
            "contratos_en_grupo": e.get("grupo_contratos", 0), "valor_grupo_ponderado_cop": round(e.get("grupo_valor", 0)),
            "veces_lider": e.get("grupo_lider", 0), "socios_distintos": e.get("grupo_socios", 0),
            "valor_total_cop": round(total), "tamano": tamano(total),
            "departamento_principal": e["deptos"].most_common(1)[0][0], "n_departamentos": len(e["deptos"]),
            "especialidad": "|".join(especialidad), "interventoria_vs_consultoria":
                "|".join(f"{k}:{v}" for k, v in e["subtipo"].most_common()),
            "ultimo_contrato": e["ultimo"], "pyme": (e["pyme"].most_common(1) or [("",)])[0][0],
            "activa_desde_2024": e["ultimo"] >= "2024-01-01"}


def main():
    PRIVADO.mkdir(exist_ok=True)
    SALIDA.mkdir(exist_ok=True)
    todas, informes = [], {}
    nits = {}
    for anillo, ruta in FUENTES.items():
        emp, rep = construir(anillo, ruta)
        rep["firmas_solo_en_grupo"] = sumar_consorcios(anillo, emp)
        filas = [fila(anillo, n, e) for n, e in emp.items()]
        todas += filas
        nits[anillo] = set(emp)
        informes[anillo] = (rep, filas)

    with (PRIVADO / "prospectos_anillos_1_2.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(todas[0]))
        w.writeheader()
        w.writerows(sorted(todas, key=lambda f: (f["anillo"], -f["valor_total_cop"])))

    L = ["# Anillos de clientes potenciales desde SECOP II — agregados", "",
         f"Generado por `anillos_clientes.py` el {date.today().isoformat()}. Solo personas jurídicas; la lista por "
         "empresa está en `_privado/` (no se publica). Incluye la experiencia en consorcios y uniones temporales "
         "atribuida a cada integrante (valor ponderado por participación, ver CONSORCIOS_SECOP.md); el tamaño se "
         "calcula sobre el valor directo más el ponderado.", ""]
    for anillo, (rep, filas) in informes.items():
        titulo = {"anillo_1": "Anillo 1 — interventoría y consultoría", "anillo_2": "Anillo 2 — contratistas de obra"}[anillo]
        act = [f for f in filas if f["activa_desde_2024"]]
        L += [f"## {titulo}", "", f"- Contratos leídos: {rep['contratos']:,}; consorcios/UT: "
              f"{rep['consorcio_o_union_temporal']:,}; personas naturales u otro documento: {rep['no_persona_juridica']:,}.",
              f"- **Empresas (NIT) distintas: {len(filas):,}**, de ellas **{len(act):,} con contrato desde 2024**"
              + (f"; {rep['firmas_solo_en_grupo']:,} solo contratan en consorcio o unión temporal (#218)."
                 if rep["firmas_solo_en_grupo"] else "."),
              f"- Contratos por empresa: mediana {statistics.median([f['contratos'] for f in filas]):.0f}; "
              f"con ≥ 5 contratos: {sum(f['contratos'] >= 5 for f in filas):,}; ≥ 20: {sum(f['contratos'] >= 20 for f in filas):,}.",
              f"- Presencia en ≥ 3 departamentos: {sum(f['n_departamentos'] >= 3 for f in filas):,}.", "",
              "| Tamaño (valor acumulado en SECOP II) | Empresas | Activas desde 2024 |", "|---|---|---|"]
        for t in ("<500M", "500M-5mil M", "5mil-50mil M", ">50mil M"):
            L.append(f"| {t} | {sum(f['tamano'] == t for f in filas):,} | {sum(f['tamano'] == t for f in act):,} |")
        L += ["", "| Especialidad principal | Empresas |", "|---|---|"]
        esp = Counter((f["especialidad"].split("|")[0] or "sin_clasificar") for f in filas)
        L += [f"| {k} | {v:,} |" for k, v in esp.most_common(12)]
        L += ["", "| Departamento principal | Empresas |", "|---|---|"]
        L += [f"| {k or '(vacío)'} | {v:,} |" for k, v in Counter(f["departamento_principal"] for f in filas).most_common(10)]
        L.append("")
    ambos = nits["anillo_1"] & nits["anillo_2"]
    L += ["## Cruce entre anillos", "",
          f"- Empresas que hacen **obra y también interventoría/consultoría**: {len(ambos):,} "
          f"({len(ambos) / len(nits['anillo_1'] | nits['anillo_2']):.1%} del total). Son el perfil de \"firma integral\": "
          "un solo cliente usa motores de diseño, presupuesto y control.", ""]
    texto = "\n".join(L)
    (SALIDA / "ANILLOS_CLIENTES_SECOP.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
