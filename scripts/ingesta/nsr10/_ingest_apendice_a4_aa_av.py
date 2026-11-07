"""Apéndice A-4 de la NSR-10 (Aa, Av, Ae, Ad y zona de amenaza sísmica de TODOS los municipios) desde el PDF fuente.

Fuente: NSR-10-191-218.pdf (páginas 7-28 del archivo = páginas A-153 a A-174 del reglamento), carpeta `raw/` (ignorada por git).
Qué hace:
  1. Extrae las filas "Municipio CÓDIGO Aa Av Zona Ae Ad" y corrige los artefactos de la extracción (p. ej. "0. 05", "In termedia").
  2. Valida: cantidad de filas, códigos únicos, rangos de valores y coherencia interna de la zona.
  3. Compara contra la tabla `sgc_amenaza_sismica_municipios` (valores servidos por el SGC) y reporta diferencias.
  4. Con --cargar escribe `nsr10_apendice_a4_municipios` (migración 20261107120000).
Uso: python _ingest_apendice_a4_aa_av.py [--cargar]
"""
from __future__ import annotations

import io
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
PDF = AQUI / "raw" / "NSR-10-191-218.pdf"
PAGINAS = range(6, 28)                      # 0-indexadas: páginas A-153 a A-174
NUM = r"0\.\s?\d{1,2}"
FILA = re.compile(rf"^(?P<mun>.+?)\s+(?P<cod>\d{{5}}|\d{{4}}\s\d|\d{{3}}\s\d{{2}}|\d{{2}}\s\d{{3}}|\d\s\d{{4}})\s+(?P<aa>{NUM})\s+(?P<av>{NUM})\s+(?P<zona>[A-Za-zá-úÁ-Ú ]+?)\s+(?P<ae>{NUM})\s+(?P<ad>{NUM})\s*$")
DEPTO = re.compile(r"^Departamento de (?P<d>.+?)\s*$|^(?P<d2>Bogot[áa],? D\.?C\.?|Distrito Capital.*)$")
DEPTOS_DANE = {"05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar", "15": "Boyacá", "17": "Caldas", "18": "Caquetá",
               "19": "Cauca", "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó", "41": "Huila", "44": "La Guajira",
               "47": "Magdalena", "50": "Meta", "52": "Nariño", "54": "Norte de Santander", "63": "Quindío", "66": "Risaralda",
               "68": "Santander", "70": "Sucre", "73": "Tolima", "76": "Valle del Cauca", "81": "Arauca", "85": "Casanare", "86": "Putumayo",
               "88": "San Andrés y Providencia", "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés", "99": "Vichada"}
ZONAS = {"baja": "Baja", "intermedia": "Intermedia", "alta": "Alta"}


def sin_acentos(s: str) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper().strip()


def numero(s: str) -> float:
    return float(s.replace(" ", ""))


def extraer() -> tuple[list[dict], list[str]]:
    r = PdfReader(str(PDF))
    filas, sospechosas, depto = [], [], None
    for i in PAGINAS:
        for linea in (r.pages[i].extract_text() or "").splitlines():
            linea = linea.strip()
            m = DEPTO.match(linea)
            if m:
                depto = (m.group("d") or m.group("d2")).strip()
                continue
            f = FILA.match(linea)
            if f:
                zona = ZONAS.get(re.sub(r"\s+", "", f.group("zona")).lower())
                if zona is None:
                    sospechosas.append(f"zona no reconocida: {linea}")
                    continue
                filas.append({"codigo": f.group("cod").replace(" ", ""), "municipio": re.sub(r"\s+", " ", f.group("mun")).strip(), "departamento": DEPTOS_DANE.get(f.group("cod").replace(" ", "")[:2], depto),
                              "aa": numero(f.group("aa")), "av": numero(f.group("av")), "zona": zona,
                              "ae": numero(f.group("ae")), "ad": numero(f.group("ad")), "pagina": 153 + (i - 6)})
            elif re.search(r"\b\d{5}\b", linea) and "Apéndice" not in linea:
                sospechosas.append(f"fila no reconocida (pág. {153 + (i - 6)}): {linea}")
    return filas, sospechosas


def validar(filas: list[dict]) -> list[str]:
    msgs = []
    cods = Counter(f["codigo"] for f in filas)
    dup = {c: n for c, n in cods.items() if n > 1}
    msgs.append(f"filas {len(filas)}; códigos únicos {len(cods)}; duplicados {dup or 'ninguno'}")
    for campo, lo, hi in (("aa", 0.0, 0.5), ("av", 0.0, 0.5), ("ae", 0.0, 0.5), ("ad", 0.0, 0.3)):
        malos = [f for f in filas if not lo < f[campo] <= hi]
        if malos:
            msgs.append(f"{campo} fuera de ({lo}, {hi}]: {[(m['municipio'], m[campo]) for m in malos[:6]]}")
    por_zona = {}
    for f in filas:
        por_zona.setdefault(f["zona"], []).append(max(f["aa"], f["av"]))
    for z, v in por_zona.items():
        msgs.append(f"zona {z}: n={len(v)}, max(Aa, Av) entre {min(v):.2f} y {max(v):.2f}")
    return msgs


def comparar_con_sgc(filas: list[dict]) -> list[str]:
    sys.path.insert(0, str(RAIZ / "scripts" / "satelite"))
    import _datos_caribe as dc
    sb, sgc, ini = dc._sb(), {}, 0
    while True:
        pg = sb.table("sgc_amenaza_sismica_municipios").select("municipio_normalizado,departamento_normalizado,aa,av,ae,ad,zona").range(ini, ini + 999).execute().data or []
        for x in pg:
            sgc[(x["municipio_normalizado"], x["departamento_normalizado"])] = x
        if len(pg) < 1000:
            break
        ini += 1000
    msgs, emparejadas, difs, sin_par = [], 0, [], []
    for f in filas:
        k = (sin_acentos(f["municipio"]), sin_acentos(f["departamento"] or ""))
        s = sgc.get(k)
        if s is None:
            sin_par.append(f"{f['municipio']} ({f['departamento']}, {f['codigo']})")
            continue
        emparejadas += 1
        d = {c: (f[c], s[c]) for c in ("aa", "av", "ae", "ad") if s[c] is None or abs(f[c] - s[c]) > 1e-9}
        if sin_acentos(s["zona"] or "") != sin_acentos(f["zona"]):
            d["zona"] = (f["zona"], s["zona"])
        if d:
            difs.append((f["municipio"], f["departamento"], d))
    msgs.append(f"PDF {len(filas)} filas; SGC {len(sgc)} filas; emparejadas por nombre+departamento: {emparejadas}")
    msgs.append(f"con diferencias de valor: {len(difs)}")
    for m, d, x in difs[:25]:
        msgs.append(f"   {m} ({d}): {x}")
    msgs.append(f"filas del PDF sin pareja en SGC: {len(sin_par)} -> {sin_par[:15]}")
    return msgs


def main() -> None:
    filas, sosp = extraer()
    print("== EXTRACCIÓN ==")
    for m in validar(filas):
        print("  ", m)
    print(f"  filas sospechosas: {len(sosp)}")
    for s in sosp[:15]:
        print("    ", s)
    print("\n== COMPARACIÓN CON sgc_amenaza_sismica_municipios ==")
    for m in comparar_con_sgc(filas):
        print("  ", m)
    (AQUI / "apendice_a4_extraido.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    if "--cargar" in sys.argv:
        sys.path.insert(0, str(RAIZ / "scripts" / "satelite"))
        import _datos_caribe as dc
        sb = dc._sb()
        unicas = {f["codigo"]: f for f in filas}             # Bogotá aparece dos veces (págs. A-163 y A-165) con valores idénticos
        filas_db = [{k: v for k, v in f.items() if k != "pagina"} | {"pagina_reglamento": f["pagina"]} for f in unicas.values()]
        for k in range(0, len(filas_db), 200):
            sb.table("nsr10_apendice_a4_municipios").upsert(filas_db[k:k + 200], on_conflict="codigo").execute()
        print(f"\nCargadas {len(filas_db)} filas en nsr10_apendice_a4_municipios")


if __name__ == "__main__":
    main()
