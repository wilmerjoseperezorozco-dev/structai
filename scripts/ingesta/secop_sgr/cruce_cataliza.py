"""
Cruce cataliza-empresas (RUES) × SECOP II por NIT: anillos 1–5 de clientes potenciales (issue #216).

Credenciales: las pone Wilmer en `_privado/.env.cataliza` (gitignored), nunca en el código ni en git:
    CATALIZA_SUPABASE_URL=https://peaaudjhbabginkilkcm.supabase.co
    CATALIZA_SUPABASE_SERVICE_KEY=...        (Settings → API → service_role; solo lectura en este script)
El RLS de `empresas` bloquea la llave pública (verificado: 200 con lista vacía), por eso hace falta la de servicio.

Qué se lee: SOLO columnas de la empresa (nit, razón social, organización jurídica, CIIU, ciudad, departamento,
cámara, fechas y estado de matrícula). La tabla `contactos` NO se lee. Las empresas unipersonales se excluyen de
la lista nominal (su razón social suele ser el nombre de una persona natural).

Salidas:
  _privado/prospectos_anillos.csv     una fila por empresa con anillo(s), señales SECOP y puntaje (privado)
  salida/CRUCE_CATALIZA_SECOP.md      solo agregados (publicable)

Uso: python cruce_cataliza.py   (requiere haber corrido anillos_clientes.py)
"""
from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import httpx

AQUI = Path(__file__).parent
PRIVADO = AQUI / "_privado"
SALIDA = AQUI / "salida"
COLUMNAS = ("nit,razon_social,organizacion_juridica,ciiu,ciiu_desc,ciudad,departamento,camara_comercio,fuente,"
            "fecha_matricula,estado_matricula,ultimo_ano_renovado")

ANILLOS_CIIU = [
    ("1_interventoria_consultoria", {"7110", "7490"}, ()),
    ("2_obra_civil", {"4210", "4220", "4290"}, ("43",)),
    ("3_edificacion_vivienda", {"4111", "4112", "6810", "6820"}, ()),
    ("4_servicios_publicos", {"3600", "3700", "3511", "3512", "3513", "3514", "3520", "3811", "3812", "3821",
                              "3822", "3830"}, ()),
    ("5_laboratorio_aseguradora", {"7120", "6511", "6512"}, ()),
    ("proveedor_materiales", {"4663", "2394", "2395", "2392", "2399"}, ()),
]
CONSTRUCCION = {"41", "42", "43", "71"}


def cargar_env() -> dict:
    ruta = PRIVADO / ".env.cataliza"
    if not ruta.exists():
        raise SystemExit(f"Falta {ruta} con CATALIZA_SUPABASE_URL y CATALIZA_SUPABASE_SERVICE_KEY (ver docstring).")
    env = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.lstrip().startswith("#"):
            k, v = linea.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def leer_empresas(env: dict) -> list[dict]:
    url = env["CATALIZA_SUPABASE_URL"].rstrip("/") + "/rest/v1/empresas"
    k = env["CATALIZA_SUPABASE_SERVICE_KEY"]
    cab = {"apikey": k, "Authorization": f"Bearer {k}", "Accept": "application/json"}
    filas, paso = [], 1000
    with httpx.Client(timeout=60) as cli:
        while True:
            r = cli.get(url, params={"select": COLUMNAS, "order": "nit"},
                        headers={**cab, "Range": f"{len(filas)}-{len(filas) + paso - 1}"})
            r.raise_for_status()
            lote = r.json()
            filas += lote
            if len(lote) < paso:
                return filas


def c4(ciiu: str) -> str:
    return re.sub(r"\D", "", ciiu or "")[:4]


def anillo_ciiu(codigo: str) -> str | None:
    for nombre, exactos, prefijos in ANILLOS_CIIU:
        if codigo in exactos or codigo.startswith(prefijos or ("~",)):
            return nombre
    return None


def nit9(s: str) -> str:
    return re.sub(r"\D", "", s or "")[:9]


def main():
    env = cargar_env()
    empresas = leer_empresas(env)
    secop = {}
    with (PRIVADO / "prospectos_anillos_1_2.csv").open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            secop.setdefault(r["nit"], []).append(r)

    filas, agg = [], defaultdict(Counter)
    for e in empresas:
        n = nit9(e["nit"])
        cod = c4(e["ciiu"])
        a_ciiu = anillo_ciiu(cod)
        s = secop.get(n, [])
        anillos_secop = sorted({x["anillo"] for x in s})
        contratos = sum(int(x["contratos"]) for x in s)
        valor = sum(int(x["valor_cop"]) for x in s)
        activa_secop = any(x["activa_desde_2024"] == "True" for x in s)
        grupo = a_ciiu or ("ganan_obra_sin_ciiu_construccion" if s and cod[:2] not in CONSTRUCCION else
                           ("solo_secop" if s else "otro"))
        a = agg[grupo]
        a["empresas"] += 1
        a["en_secop"] += bool(s)
        a["secop_activa_2024"] += activa_secop
        a["unipersonal"] += "UNIPERSONAL" in (e["organizacion_juridica"] or "").upper()
        if grupo == "otro":
            continue
        # Puntaje de prioridad (0–100), hipótesis inicial a validar con la muestra etiquetada por Wilmer:
        prio = {"1_interventoria_consultoria": 35, "2_obra_civil": 30, "3_edificacion_vivienda": 30,
                "4_servicios_publicos": 20, "5_laboratorio_aseguradora": 20, "proveedor_materiales": 10}.get(a_ciiu, 15)
        puntaje = prio + (25 if activa_secop else 10 if s else 0) + min(20, contratos * 2) \
            + (10 if len(anillos_secop) == 2 else 0) + (10 if (e.get("estado_matricula") or "").upper() == "ACTIVA" else 0)
        if "UNIPERSONAL" in (e["organizacion_juridica"] or "").upper():
            continue                       # posible persona natural: fuera de la lista nominal
        filas.append({"nit": n, "razon_social": e["razon_social"], "anillo_ciiu": a_ciiu or "", "ciiu": cod,
                      "ciiu_desc": e["ciiu_desc"], "ciudad": e["ciudad"], "departamento": e["departamento"],
                      "camara": e["camara_comercio"], "anillos_secop": "|".join(anillos_secop),
                      "contratos_secop": contratos, "valor_secop_cop": valor, "activa_secop_2024": activa_secop,
                      "estado_matricula": e["estado_matricula"], "fecha_matricula": e["fecha_matricula"],
                      "puntaje": min(100, puntaje)})

    filas.sort(key=lambda f: -f["puntaje"])
    with (PRIVADO / "prospectos_anillos.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    L = ["# Cruce cataliza-empresas (RUES) × SECOP II — agregados (#216)", "",
         f"Generado por `cruce_cataliza.py` el {date.today().isoformat()}. {len(empresas):,} empresas de cataliza; "
         f"{len(secop):,} empresas (NIT) en SECOP II obra/interventoría/consultoría. Sin contactos ni personas naturales.",
         "", "| Grupo | Empresas | En SECOP II | Activas en SECOP desde 2024 |", "|---|---|---|---|"]
    for g in sorted(agg):
        a = agg[g]
        L.append(f"| {g} | {a['empresas']:,} | {a['en_secop']:,} ({a['en_secop'] / a['empresas']:.1%}) | {a['secop_activa_2024']:,} |")
    L += ["", "`ganan_obra_sin_ciiu_construccion`: empresas cuyo CIIU no es de construcción (41/42/43/71) y aparecen "
          "como contratistas de obra o interventoría. Se reporta **solo el total**: un CIIU desactualizado es la "
          "explicación más común, no una irregularidad.", ""]
    (SALIDA / "CRUCE_CATALIZA_SECOP.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"lista privada: {len(filas):,} empresas → _privado/prospectos_anillos.csv")


if __name__ == "__main__":
    main()
