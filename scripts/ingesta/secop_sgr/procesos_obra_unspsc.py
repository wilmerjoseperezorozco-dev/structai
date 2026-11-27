"""
SECOP II, procesos de obra por UNSPSC: limpieza, etiquetas prioritarias y control de cordura (issue #212).

Entrada: raw/secop2_procesos_obra.csv (p6dx-8zbt, tipo_de_contrato='Obra', descargado por descargar.py con las
columnas de proveedor ya seudonimizadas). Salida (gitignored):
  salida/secop_procesos_obra_unspsc.csv   tabla limpia lista para la ingesta (migración aparte, sin aplicar)
  salida/SECOP_PROCESOS_UNSPSC.md         perfil y conteos
  salida/muestra_etiquetar_300.csv        muestra estratificada (UNSPSC × modalidad) SIN predicciones, para etiquetar a mano

Licencia de la fuente: CC BY-SA 4.0 (Colombia Compra Eficiente). Las tablas derivadas heredan CC BY-SA 4.0.
Sin datos personales: no se conserva ninguna columna de proveedor; las entidades son públicas.
No se señala a ninguna entidad ni empresa: las etiquetas describen el objeto del proceso, no conductas.

Uso: python procesos_obra_unspsc.py [--segmentos 72 81 95 83] [--verificar-api]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

AQUI = Path(__file__).parent
RAW = AQUI / "raw" / "secop2_procesos_obra.csv"
SALIDA = AQUI / "salida"
VERSION = "reglas-0.1.0"
csv.field_size_limit(10**9)

CAMPOS = ["id_del_proceso", "referencia_del_proceso", "nombre_entidad", "departamento_entidad", "ciudad_entidad",
          "precio_base", "codigo_principal_de_categoria", "urlproceso",
          # además, para métricas (#196, #206, #210)
          "segmento_unspsc", "familia_unspsc", "modalidad_de_contratacion", "fecha_de_publicacion_del",
          "anio", "estado_del_procedimiento", "adjudicado", "valor_total_adjudicacion", "respuestas_al_procedimiento",
          "nombre_del_procedimiento",
          # etiquetas
          "tipo_obra", "tipos_obra", "prioridad_structai", "regla", "version_etiquetas", "alerta_calidad",
          "fecha_carga", "licencia"]

# Tipo de obra: (etiqueta, prioridad para StructAI, regex sobre el nombre normalizado). El ORDEN es la prioridad:
# la primera que coincide es la etiqueta principal; todas las que coinciden van en tipos_obra.
TIPOS = [
    ("interventoria", "media", r"\binterventori"),
    ("estudios_y_disenos", "alta", r"\bestudios?\b.*\bdisen|\bdisen(o|os)\b.*\b(estudio|detalle|fase)|\bconsultori"),
    ("placa_huella_via_terciaria", "alta", r"placa[s]? huella|via[s]? terciari|vias? rural|camino[s]? veredal"),
    ("puentes", "alta", r"\bpuente|\bponton|\bbox ?coulvert|\bbox ?culvert|\bviaducto"),
    ("vias", "alta", r"\bvia[s]?\b|\bvial|pavimenta|\bcarrera\b|\bcalle\b|\bmalla vial|\bcarretera|rehabilitacion de la via|"
                     r"\bandenes|\bbacheo|\bparcheo|\basfalt|\bafirmado|\brecebo|\bcorredor vial"),
    ("acueducto_alcantarillado", "alta", r"acueduct|alcantarill|\bpluvial|\bsanitari[oa]s? |colector|\bptap\b|\bptar\b|"
                                         r"planta de tratamiento|redes? hidr|agua potable|\bsaneamiento|\bpozo[s]? septic|"
                                         r"\bbaterias? sanitari|unidades? sanitari"),
    ("edificacion_educativa", "alta", r"\binstitucion educativa|\bcolegio|\bescuela|\bsede educativa|\baula[s]?\b|"
                                      r"\buniversidad|\bjardin infantil|\bcdi\b|\brestaurante escolar|\bmegacolegio"),
    ("edificacion_salud", "alta", r"\bhospital|\bcentro de salud|\bpuesto de salud|\bese\b|\bips\b|\burgencias"),
    ("vivienda", "alta", r"\bvivienda|\bmejoramiento[s]? de vivienda|\bunidades? habitacional|\bvis\b|\bvip\b"),
    ("espacio_publico_deportivo", "media", r"\bparque|\bespacio publico|\bplaza\b|\bpolideportiv|\bcancha|\bcoliseo|"
                                           r"\bestadio|\bescenario[s]? deportiv|\bmalecon|\bsendero|\bciclo ?ruta|\bgimnasio"),
    ("contencion_estabilizacion", "alta", r"\bmuro[s]? de contencion|\bestabilizacion|\bcontencion|\bgavion|\btalud|"
                                          r"\bremocion en masa|\bdeslizamiento|\bmitigacion"),
    ("electrico_alumbrado", "baja", r"\belectric|\balumbrado|\bfotovoltaic|\bsubestacion|\bredes? de media|\bluminari"),
    ("edificacion_institucional", "media", r"\bedificio|\bsede\b|\balcaldia|\bcasa de la cultura|\bbiblioteca|"
                                           r"\bcentro de (desarrollo|integracion|acopio)|\bplaza de mercado|\bsalon comunal|"
                                           r"\bcarcel|\bbatallon|\bestacion de policia|\bcuartel"),
    ("mantenimiento", "media", r"\bmantenimiento|\breparacion|\badecuacion|\bremodelacion|\bmejoramiento|"
                               r"\brehabilitacion|\brestauracion|\bconservacion|\bpintura"),
]
_RX = [(t, p, re.compile(r)) for t, p, r in TIPOS]

# Respaldo por familia UNSPSC cuando el texto no dice nada (nombres de familia según el clasificador UNSPSC v14
# usado por CCE; verificar en el catálogo de CCE antes de publicarlos).
FAMILIA = {"7211": ("vivienda", "alta"), "7210": ("mantenimiento", "media"), "7214": ("obra_civil_pesada", "media"),
           "7212": ("edificacion_institucional", "media"), "7215": ("obra_especializada", "media"),
           "8110": ("estudios_y_disenos", "alta"), "8310": ("servicios_publicos", "media")}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def numero(s: str) -> float | None:
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def etiquetar(nombre: str, codigo: str) -> tuple[str, list[str], str, str]:
    n = norm(nombre)
    hits = [(t, p) for t, p, rx in _RX if rx.search(n)]
    if hits:
        return hits[0][0], [t for t, _ in hits], hits[0][1], "texto"
    fam = (codigo or "")[3:7]
    if fam in FAMILIA:
        t, p = FAMILIA[fam]
        return t, [t], p, "unspsc"
    return "sin_clasificar", [], "baja", "ninguna"


def segmento(codigo: str) -> str:
    return codigo[3:5] if codigo and codigo.startswith("V1.") and codigo[3:5].isdigit() else "sin_codigo"


def limpiar(segmentos: set[str]) -> tuple[list[dict], dict]:
    vistos: dict[str, dict] = {}
    rep = Counter()
    excluidos_seg = Counter()
    hoy = date.today().isoformat()
    with RAW.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rep["leidas"] += 1
            seg = segmento(r["codigo_principal_de_categoria"])
            if seg != "sin_codigo" and seg not in segmentos:
                excluidos_seg[seg] += 1
                continue
            idp = (r["id_del_proceso"] or "").strip()
            if not idp:
                rep["sin_id"] += 1
                continue
            previo = vistos.get(idp)
            if previo and previo["_ult"] >= (r["fecha_de_ultima_publicaci"] or ""):
                rep["duplicado_id"] += 1
                continue
            if previo:
                rep["duplicado_id"] += 1
            alertas = []
            pb = numero(r["precio_base"])
            if pb is None or pb <= 0:
                alertas.append("precio_base_invalido")
            elif pb < 1e6:
                alertas.append("precio_base_menor_1M")
            elif pb > 1e13:
                alertas.append("precio_base_mayor_10_billones")   # > 10^13 COP: probable error de digitación
            va = numero(r["valor_total_adjudicacion"])
            if va and pb and va > 1.5 * pb:
                alertas.append("adjudicado_mayor_150pct_base")
            url = r["urlproceso"] or ""
            if not url.startswith("https://community.secop.gov.co/"):
                alertas.append("url_no_secop")
            tipo, tipos, prio, regla = etiquetar(r["nombre_del_procedimiento"], r["codigo_principal_de_categoria"])
            f = r["fecha_de_publicacion_del"] or ""
            vistos[idp] = {
                "_ult": r["fecha_de_ultima_publicaci"] or "",
                "id_del_proceso": idp, "referencia_del_proceso": (r["referencia_del_proceso"] or "").strip(),
                "nombre_entidad": (r["entidad"] or "").strip(),
                "departamento_entidad": (r["departamento_entidad"] or "").strip(),
                "ciudad_entidad": (r["ciudad_entidad"] or "").strip(),
                "precio_base": "" if pb is None else f"{pb:.0f}",
                "codigo_principal_de_categoria": r["codigo_principal_de_categoria"],
                "urlproceso": url, "segmento_unspsc": seg,
                "familia_unspsc": (r["codigo_principal_de_categoria"] or "")[3:7] if seg != "sin_codigo" else "",
                "modalidad_de_contratacion": (r["modalidad_de_contratacion"] or "").strip(),
                "fecha_de_publicacion_del": f[:10], "anio": f[:4],
                "estado_del_procedimiento": r["estado_del_procedimiento"], "adjudicado": r["adjudicado"],
                "valor_total_adjudicacion": "" if va is None else f"{va:.0f}",
                "respuestas_al_procedimiento": r["respuestas_al_procedimiento"],
                "nombre_del_procedimiento": re.sub(r"\s+", " ", r["nombre_del_procedimiento"] or "").strip(),
                "tipo_obra": tipo, "tipos_obra": "|".join(tipos), "prioridad_structai": prio, "regla": regla,
                "version_etiquetas": VERSION, "alerta_calidad": "|".join(alertas), "fecha_carga": hoy,
                "licencia": "CC BY-SA 4.0 (Colombia Compra Eficiente, datos.gov.co p6dx-8zbt)",
            }
    filas = list(vistos.values())
    rep["excluidas_por_segmento"] = sum(excluidos_seg.values())
    rep["conservadas"] = len(filas)
    return filas, {"conteo": dict(rep), "excluidos_por_segmento": dict(excluidos_seg.most_common())}


def muestra_estratificada(filas: list[dict], n: int = 300, semilla: int = 212) -> list[dict]:
    """n procesos estratificados por segmento UNSPSC × modalidad (asignación ∝ √tamaño, mínimo 2 por estrato
    con ≥ 2 filas). Sin predicciones: para etiquetar a ciegas."""
    rng = random.Random(semilla)
    estr = defaultdict(list)
    for f in filas:
        estr[(f["segmento_unspsc"], f["modalidad_de_contratacion"])].append(f)
    pesos = {k: len(v) ** 0.5 for k, v in estr.items() if len(v) >= 2}
    total = sum(pesos.values())
    cuota = {k: max(2, round(n * w / total)) for k, w in pesos.items()}
    while sum(cuota.values()) > n:                       # recorta los más grandes hasta llegar a n
        k = max(cuota, key=lambda k: cuota[k])
        cuota[k] -= 1
    salida = []
    for k in sorted(cuota):
        for f in rng.sample(estr[k], min(cuota[k], len(estr[k]))):
            salida.append({"id_del_proceso": f["id_del_proceso"], "segmento_unspsc": k[0], "modalidad": k[1],
                           "nombre_del_procedimiento": f["nombre_del_procedimiento"],
                           "tipo_obra_humano": "", "prioridad_humana": "", "notas": ""})
    rng.shuffle(salida)
    return salida


def contar_api(where: str) -> int | None:
    q = urllib.parse.urlencode({"$select": "count(id_del_proceso) as n", "$where": where})
    try:
        with urllib.request.urlopen(f"https://www.datos.gov.co/resource/p6dx-8zbt.json?{q}", timeout=120) as r:
            return int(json.load(r)[0]["n"])
    except Exception:  # noqa: BLE001
        return None


def control_cordura(local: int, remoto: int | None, minimo_relativo: float = 0.9) -> tuple[bool, str]:
    """La carga incremental se aborta si la API devuelve muchas menos filas que la copia local: pasó el
    2026-11-15, cuando p6dx-8zbt estaba en recarga y contaba 1.000 filas en total (15 de obra)."""
    if remoto is None:
        return False, "API sin respuesta: no se carga nada"
    if remoto < minimo_relativo * local:
        return False, f"API con {remoto:,} filas vs {local:,} locales (< {minimo_relativo:.0%}): fuente en recarga, se aborta"
    return True, f"API {remoto:,} vs local {local:,}: OK"


def informe(filas, rep, api_msg) -> str:
    c = lambda k: Counter(f[k] for f in filas)  # noqa: E731
    L = [f"# SECOP II — procesos de obra por UNSPSC (#212)", "",
         f"Generado por `procesos_obra_unspsc.py` ({VERSION}) el {date.today().isoformat()} desde la copia del 12-nov-2026.",
         "", "## Limpieza", "", "| Paso | Filas |", "|---|---|"]
    L += [f"| {k} | {v:,} |" for k, v in rep["conteo"].items()]
    L += ["", f"Segmentos excluidos: {rep['excluidos_por_segmento']}", "", f"Control de cordura de la API: {api_msg}", ""]
    for campo, titulo in (("segmento_unspsc", "Segmento UNSPSC"), ("tipo_obra", "Tipo de obra (etiqueta principal)"),
                          ("prioridad_structai", "Prioridad StructAI"), ("regla", "Origen de la etiqueta"),
                          ("modalidad_de_contratacion", "Modalidad")):
        L += [f"## {titulo}", "", "| Valor | Procesos | % |", "|---|---|---|"]
        tot = len(filas)
        L += [f"| {k or '(vacío)'} | {v:,} | {v / tot:.1%} |" for k, v in c(campo).most_common(20)]
        L.append("")
    al = Counter(a for f in filas for a in f["alerta_calidad"].split("|") if a)
    L += ["## Alertas de calidad (no se borran, se marcan)", "", "| Alerta | Procesos |", "|---|---|"]
    L += [f"| {k} | {v:,} |" for k, v in al.most_common()]
    L += ["", "Las etiquetas son **reglas de texto + familia UNSPSC**: base para el clasificador TF-IDF (#196) y se miden "
          "contra la muestra humana de 300 (`muestra_etiquetar_300.csv`). Criterio prerregistrado en #212: F1 macro ≥ 0,85.",
          ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segmentos", nargs="+", default=["72", "81", "95", "83"])
    ap.add_argument("--verificar-api", action="store_true")
    a = ap.parse_args()
    SALIDA.mkdir(exist_ok=True)
    filas, rep = limpiar(set(a.segmentos))
    api_msg = "no verificado (usa --verificar-api)"
    if a.verificar_api:
        _, api_msg = control_cordura(rep["conteo"]["leidas"], contar_api("tipo_de_contrato='Obra'"))
    with (SALIDA / "secop_procesos_obra_unspsc.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    muestra = muestra_estratificada(filas)
    with (SALIDA / "muestra_etiquetar_300.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(muestra[0]))
        w.writeheader()
        w.writerows(muestra)
    texto = informe(filas, rep, api_msg)
    (SALIDA / "SECOP_PROCESOS_UNSPSC.md").write_text(texto, encoding="utf-8")
    sha = hashlib.sha256((SALIDA / "secop_procesos_obra_unspsc.csv").read_bytes()).hexdigest()[:16]
    print(texto[:3000])
    print(f"\n{len(filas):,} procesos → salida/secop_procesos_obra_unspsc.csv (sha256 {sha}…); muestra {len(muestra)}")


if __name__ == "__main__":
    main()
