"""
Anillos 4 y 5 de clientes potenciales con fuentes públicas (issue #216).

  Anillo 4  empresas de servicios públicos: RUPS (Superservicios, 4qkq-csdn) × entidades que CONTRATAN obra,
            interventoría o consultoría en SECOP II (nit_entidad de los contratos ya descargados).
  Anillo 5  aseguradoras (Superfinanciera, sr9n-792w + pólizas SECOP II Garantías, gjp9-cutm), laboratorios
            ambientales acreditados (IDEAM, 2waz-acaa) y curadurías urbanas (SNR, psyr-i7bp).

Habeas data (Ley 1581): se descargan SOLO columnas de la entidad (NIT, razón social, ciudad, tipo, servicio).
Teléfono, correo, dirección, representante legal y contacto NO se piden a la API. En Garantías tampoco se piden
`asegurado` ni `beneficiario` (pueden ser personas naturales). Prestadores con NIT de persona natural (no empieza
por 8 o 9) se excluyen de la lista nominal.

Licencias: CC BY-SA 4.0 en 1–4. Licencias urbanísticas (5) es CC BY-ND 4.0: se usa solo internamente; nada derivado
de ella va a salida/ (la lista de curadurías queda en _privado/).

Salidas:
  raw/anillo45_*.csv                       descargas (gitignored)
  _privado/prospectos_anillos_4_5.csv      lista nominal (privada)
  _privado/curadurias.csv                  curadurías por municipio y volumen de licencias (privada, licencia ND)
  salida/ANILLOS_4_5.md                    solo agregados (publicable)

Uso: python anillos_4_5.py [--sin-descarga]
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import httpx

AQUI = Path(__file__).parent
RAW, PRIVADO, SALIDA = AQUI / "raw", AQUI / "_privado", AQUI / "salida"
API = "https://www.datos.gov.co/resource/{id}.csv"

FUENTES = {
    "rups": ("4qkq-csdn", {"$select": "nit,nombre,servicio,estado,tipo_inscripcion,tipo_prestador,clasificacion,"
                                      "departamento_prestacion,municipio_prestacion,departamento_domicilio,"
                                      "municipio_domicilio"}),
    "sfc": ("sr9n-792w", {"$select": "tipo_entidad,cod_entidad,razon_social,ciudad,numeroidentificacion"}),
    "garantias": ("gjp9-cutm", {"$select": "id_contrato,aseguradora,tipopoliza,subtipopoliza,estado,valor,"
                                           "fechadecreacionpoliza"}),
    "labs_ideam": ("2waz-acaa", {"$select": "nit,nombre_del_laboratorio,ciudad,departamento,"
                                            "estado_de_la_acreditaci_n,matriz,count(*) AS parametros",
                                 "$group": "nit,nombre_del_laboratorio,ciudad,departamento,"
                                           "estado_de_la_acreditaci_n,matriz"}),
    "licencias": ("psyr-i7bp", {"$select": "a_o,departamento,municipio,curaduria,actos_admin_expedidos,"
                                           "urbanizaci_n,parcelaci_n,subdivisi_n,construcci_n,reconocimiento"}),
}
CONTRATOS = ("secop2_contratos_obra.csv", "secop2_contratos_interventoria_consultoria.csv")


# ── utilidades ───────────────────────────────────────────────────────────────────────────────────────────────────
def nit9(s: str) -> str:
    return re.sub(r"\D", "", s or "")[:9]


def es_juridica(n: str) -> bool:
    return len(n) == 9 and n[0] in "89"


def plano(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", s)).strip()


def a_num(s: str) -> float:
    try:
        return float(s or 0)
    except ValueError:
        return 0.0


# Aseguradora es texto libre en SECOP (typos como "SEFUROS DEL ESTADO"). Se agrupa por palabra distintiva.
ASEGURADORAS = [
    ("SEGUROS DEL ESTADO", r"\bESTADO\b"), ("SURA / SURAMERICANA", r"\bSURA"), ("MUNDIAL", r"\bMUNDIAL\b"),
    ("CONFIANZA", r"\bCONFIANZA\b"), ("SOLIDARIA", r"\bSOLIDARIA\b"), ("LIBERTY / HDI", r"\bLIBERTY\b|\bHDI\b"),
    ("PREVISORA", r"\bPREVISORA\b"), ("BOLIVAR", r"\bBOLIVAR\b"), ("ALLIANZ", r"\bALLIANZ\b"),
    ("AXA COLPATRIA", r"\bAXA\b|\bCOLPATRIA\b"), ("NACIONAL DE SEGUROS", r"\bNACIONAL\b"),
    ("CHUBB", r"\bCHUBB\b"), ("ZURICH / QBE", r"\bZURICH\b|\bQBE\b"), ("BERKLEY", r"\bBERKLEY\b"),
    ("MAPFRE", r"\bMAPFRE\b"), ("EQUIDAD", r"\bEQUIDAD\b"), ("CARDIF", r"\bCARDIF\b"), ("SBS", r"\bSBS\b"),
    ("ASEGURADORA SOLIDARIA", r"\bASEGURADORA SOLIDARIA\b"), ("JMALUCELLI", r"MALUCELLI"),
]


# Códigos de tipo de entidad de la Superfinanciera (sr9n-792w), verificados con las razones sociales del archivo.
TIPOS_SFC = {"13": "Compañía de seguros generales", "11": "Corredor de seguros"}


def razon_corta(s: str) -> str:
    """Quita la cola legal ('Sigla: …', ', pudiendo utilizar …', ' en adelante …')."""
    return re.split(r"\s*(?:,|\.)?\s*(?:Sigla|sigla|SIGLA|pudiendo|podr[aá]|en adelante|y adem[aá]s)\b", s or "")[0].strip(" ,.")


def grupo_aseguradora(txt: str) -> str:
    p = plano(txt)
    for nombre, rx in ASEGURADORAS:
        if re.search(rx, p):
            return nombre
    return "otra / sin identificar" if p else "vacío"


# ── descarga ─────────────────────────────────────────────────────────────────────────────────────────────────────
def descargar(nombre: str) -> Path:
    did, params = FUENTES[nombre]
    destino, marca = RAW / f"anillo45_{nombre}.csv", RAW / f"anillo45_{nombre}.completo"
    if marca.exists():
        return destino
    filas, encabezado, paso = [], None, 50000
    with httpx.Client(timeout=120) as cli:
        while True:
            r = cli.get(API.format(id=did), params={**params, "$limit": paso, "$offset": len(filas),
                                                    "$order": params.get("$group", "").split(",")[0] or ":id"})
            r.raise_for_status()
            lector = csv.reader(io.StringIO(r.text))
            cab = next(lector)
            encabezado = encabezado or cab
            lote = list(lector)
            filas += lote
            print(f"  {nombre}: {len(filas):,} filas", flush=True)
            if len(lote) < paso:
                break
    with destino.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(encabezado)
        w.writerows(filas)
    marca.write_text(f"{date.today().isoformat()} {len(filas)} filas {did}\n", encoding="utf-8")
    return destino


def leer(nombre: str) -> list[dict]:
    with (RAW / f"anillo45_{nombre}.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ── cruce ────────────────────────────────────────────────────────────────────────────────────────────────────────
def contratos_por_entidad() -> tuple[dict, dict]:
    """nit_entidad → {contratos, valor, tipos, activa_2024}; id_contrato → tipo (para filtrar garantías)."""
    por_ent, ids = defaultdict(lambda: {"contratos": 0, "valor": 0.0, "tipos": Counter(), "activa_2024": False,
                                        "nombre": ""}), {}
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    for f in CONTRATOS:
        with (RAW / f).open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                e = por_ent[nit9(r["nit_entidad"])]
                e["contratos"] += 1
                e["valor"] += a_num(r["valor_del_contrato"])
                e["tipos"][r["tipo_de_contrato"]] += 1
                e["activa_2024"] |= (r.get("fecha_de_firma") or "")[:4] >= "2024"
                e["nombre"] = e["nombre"] or r["nombre_entidad"]
                ids[r["id_contrato"]] = r["tipo_de_contrato"]
    return por_ent, ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-descarga", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not a.sin_descarga:
        for n in FUENTES:
            descargar(n)

    por_ent, ids_contrato = contratos_por_entidad()
    prospectos, L = [], []

    # Anillo 4 — servicios públicos
    rups = leer("rups")
    prest = defaultdict(lambda: {"servicios": set(), "estados": set(), "municipios": set(), "nombre": "",
                                 "tipo": set(), "clasif": set(), "depto": ""})
    excluidos_pn = set()
    for r in rups:
        n = nit9(r["nit"])
        if not es_juridica(n):
            excluidos_pn.add(n)
            continue
        p = prest[n]
        p["nombre"] = p["nombre"] or r["nombre"]
        p["servicios"].add(plano(r["servicio"]).title())
        p["estados"].add(plano(r["estado"]))
        p["municipios"].add((r["departamento_prestacion"], r["municipio_prestacion"]))
        p["tipo"].add(r["tipo_prestador"])
        p["clasif"].add(r["clasificacion"])
        p["depto"] = p["depto"] or r["departamento_domicilio"]
    a4 = Counter()
    por_servicio = defaultdict(Counter)
    for n, p in prest.items():
        e = por_ent.get(n)
        activo = "OPERATIVA" in p["estados"]
        a4["prestadores"] += 1
        a4["activos"] += activo
        a4["contratan_en_secop"] += bool(e)
        a4["contratan_desde_2024"] += bool(e and e["activa_2024"])
        for s in p["servicios"]:
            por_servicio[s]["prestadores"] += 1
            por_servicio[s]["contratan"] += bool(e)
        puntaje = 20 + (30 if e and e["activa_2024"] else 15 if e else 0) + min(25, (e["contratos"] if e else 0)) \
            + (10 if activo else 0) + min(15, 3 * len(p["municipios"]))
        prospectos.append({"anillo": "4_servicios_publicos", "nit": n, "razon_social": p["nombre"],
                           "detalle": "|".join(sorted(p["servicios"])), "departamento": p["depto"],
                           "municipios_atendidos": len(p["municipios"]),
                           "contratos_secop_como_entidad": e["contratos"] if e else 0,
                           "valor_secop_cop": round(e["valor"]) if e else 0,
                           "activa_secop_2024": bool(e and e["activa_2024"]), "puntaje": min(100, puntaje)})

    # Anillo 5a — aseguradoras
    sfc = leer("sfc")
    tipos_sfc = Counter(r["tipo_entidad"] for r in sfc)
    seguros = [r for r in sfc if r["tipo_entidad"] in TIPOS_SFC]
    gar = leer("garantias")
    g_total = Counter()
    g_por = defaultdict(lambda: {"polizas": 0, "valor": 0.0, "obra": 0, "interv": 0})
    for r in gar:
        g = grupo_aseguradora(r["aseguradora"])
        tipo = ids_contrato.get(r["id_contrato"])
        g_total["polizas"] += 1
        g_total["en_contratos_descargados"] += bool(tipo)
        d = g_por[g]
        d["polizas"] += 1
        d["valor"] += a_num(r["valor"])
        d["obra"] += tipo == "Obra"
        d["interv"] += tipo in ("Interventoría", "Consultoría")
    for r in seguros:
        n = nit9(r["numeroidentificacion"])
        g = grupo_aseguradora(r["razon_social"])
        d = g_por.get(g, {"polizas": 0, "obra": 0, "interv": 0, "valor": 0})
        prospectos.append({"anillo": "5_aseguradora", "nit": n, "razon_social": razon_corta(r["razon_social"]),
                           "detalle": TIPOS_SFC[r["tipo_entidad"]], "departamento": r["ciudad"], "municipios_atendidos": "",
                           "contratos_secop_como_entidad": "", "valor_secop_cop": "",
                           "activa_secop_2024": "",
                           "polizas_secop_obra_interv": d["obra"] + d["interv"],
                           "puntaje": min(100, 30 + min(50, (d["obra"] + d["interv"]) // 20) + (20 if d["polizas"] else 0))})

    # Anillo 5b — laboratorios ambientales acreditados
    labs = defaultdict(lambda: {"nombre": "", "ciudad": "", "depto": "", "matrices": set(), "parametros": 0,
                                "estados": set()})
    for r in leer("labs_ideam"):
        n = nit9(r["nit"])
        if not es_juridica(n):
            continue
        l = labs[n]
        l["nombre"] = l["nombre"] or r["nombre_del_laboratorio"]
        l["ciudad"], l["depto"] = l["ciudad"] or r["ciudad"], l["depto"] or r["departamento"]
        l["matrices"].add(plano(r["matriz"]).title())
        l["parametros"] += int(a_num(r["parametros"]))
        l["estados"].add(plano(r["estado_de_la_acreditaci_n"]))
    for n, l in labs.items():
        suelo = any("SUELO" in m.upper() for m in l["matrices"])
        prospectos.append({"anillo": "5_laboratorio_ambiental", "nit": n, "razon_social": l["nombre"],
                           "detalle": "|".join(sorted(l["matrices"])), "departamento": l["depto"],
                           "municipios_atendidos": "", "contratos_secop_como_entidad": "", "valor_secop_cop": "",
                           "activa_secop_2024": "", "parametros_acreditados": l["parametros"],
                           "puntaje": min(100, 25 + (25 if suelo else 0) + min(30, l["parametros"] // 10)
                                          + (20 if any("VIGENTE" in s or "ACREDITAD" in s for s in l["estados"]) else 0))})

    # Anillo 5c — curadurías (licencia ND: solo privado)
    cur = defaultdict(lambda: {"departamento": "", "municipio": "", "anios": set(), "construccion": 0, "actos": 0})
    for r in leer("licencias"):
        k = plano(r["curaduria"]) + "|" + plano(r["municipio"])
        c = cur[k]
        c["curaduria"], c["departamento"], c["municipio"] = r["curaduria"], r["departamento"], r["municipio"]
        c["anios"].add(r["a_o"])
        c["construccion"] += int(a_num(r["construcci_n"]))
        c["actos"] += int(a_num(r["actos_admin_expedidos"]))
    with (PRIVADO / "curadurias.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["curaduria", "departamento", "municipio", "anios", "licencias_construccion", "actos_expedidos"])
        for c in sorted(cur.values(), key=lambda c: -c["construccion"]):
            w.writerow([c["curaduria"], c["departamento"], c["municipio"], f"{min(c['anios'])}-{max(c['anios'])}",
                        c["construccion"], c["actos"]])

    with (PRIVADO / "aseguradoras_garantias.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["grupo_aseguradora", "polizas", "valor_cop", "polizas_obra", "polizas_interventoria_consultoria"])
        for g, d in sorted(g_por.items(), key=lambda x: -x[1]["polizas"]):
            w.writerow([g, d["polizas"], round(d["valor"]), d["obra"], d["interv"]])

    # Escribir lista privada
    campos = sorted({k for p in prospectos for k in p}, key=lambda k: list(prospectos[0]).index(k)
                    if k in prospectos[0] else 99)
    prospectos.sort(key=lambda p: (p["anillo"], -p["puntaje"]))
    with (PRIVADO / "prospectos_anillos_4_5.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(prospectos)

    # Agregados publicables
    n_cur_mun = len({c["municipio"] for c in cur.values()})
    L = ["# Anillos 4 y 5 de clientes potenciales — agregados (#216)", "",
         f"Generado por `anillos_4_5.py` el {date.today().isoformat()}. Solo agregados; las listas nominales están en "
         "`_privado/`. Sin teléfonos, correos, direcciones, representantes ni personas naturales.", "",
         "## Anillo 4 — empresas de servicios públicos", "",
         f"Fuente: RUPS (Superservicios, `4qkq-csdn`, última actualización 2021: puede estar desactualizado). "
         f"Personas jurídicas: **{a4['prestadores']:,}** ({len(excluidos_pn):,} NIT de persona natural excluidos). "
         f"Activas u operando: {a4['activos']:,}.", "",
         f"- Contratan obra, interventoría o consultoría en SECOP II como entidad: **{a4['contratan_en_secop']:,}** "
         f"({a4['contratan_en_secop'] / max(1, a4['prestadores']):.1%}); desde 2024: {a4['contratan_desde_2024']:,}.", "",
         "| Servicio | Prestadores | Contratan en SECOP II |", "|---|---|---|"]
    for s, c in sorted(por_servicio.items(), key=lambda x: -x[1]["prestadores"]):
        L.append(f"| {s or '(sin dato)'} | {c['prestadores']:,} | {c['contratan']:,} |")
    L += ["", "## Anillo 5 — aseguradoras, laboratorios y curadurías", "",
          f"**Aseguradoras.** Superfinanciera vigila {len(sfc):,} entidades; de ellas "
          f"{tipos_sfc['13']:,} son compañías de seguros generales (las que expiden pólizas de cumplimiento) y "
          f"{tipos_sfc['11']:,} corredores de seguros (colocan esas pólizas). Seguros de vida, bancos y fondos se "
          "excluyen.", "",
          "La tabla por aseguradora queda en `_privado/aseguradoras_garantias.csv`: el nombre en SECOP es texto "
          "libre y la agrupación por palabra clave puede atribuir mal algunas pólizas, así que no se publica por nombre.", "",
          f"**Pólizas en SECOP II Garantías** (`gjp9-cutm`): {g_total['polizas']:,} pólizas; "
          f"{g_total['en_contratos_descargados']:,} corresponden a contratos de obra, interventoría o consultoría ya "
          f"descargados ({g_total['en_contratos_descargados'] / max(1, g_total['polizas']):.1%}). "
          f"La aseguradora es texto libre en SECOP; se agrupó por nombre distintivo en {len(g_por)} grupos "
          f"(concentración: el primer grupo emite el "
          f"{max(d['polizas'] for d in g_por.values()) / max(1, g_total['polizas']):.0%} de las pólizas).", "",
          f"**Laboratorios ambientales acreditados (IDEAM, `2waz-acaa`):** {len(labs):,} personas jurídicas; "
          f"{sum(1 for l in labs.values() if any('SUELO' in m.upper() for m in l['matrices'])):,} con matriz de suelo. "
          "Los laboratorios de materiales y geotecnia (concreto, acero, suelos) los acredita ONAC, cuyo directorio no "
          "está en datos.gov.co: queda pendiente.", "",
          f"**Curadurías urbanas:** {len(cur):,} combinaciones curaduría-municipio en {n_cur_mun:,} municipios. "
          "La fuente (SNR, `psyr-i7bp`) es CC BY-ND 4.0: se usa solo internamente y no se publican derivados.", "",
          "## Limitaciones", "",
          "- El puntaje es una hipótesis inicial sin validar; se calibra con la muestra ciega que etiqueta Wilmer.",
          "- RUPS no se actualiza en datos.gov.co desde 2021.",
          "- Garantías cubre una fracción de los contratos (no todos los procesos publican sus pólizas).", ""]
    (SALIDA / "ANILLOS_4_5.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"lista privada: {len(prospectos):,} filas → _privado/prospectos_anillos_4_5.csv; "
          f"curadurías → _privado/curadurias.csv")


if __name__ == "__main__":
    main()
