"""Validación de motor-pilotes contra la CYCU pile load test database (#118).

Prerregistro: issue #118 (ver el comentario de prerregistro CYCU, publicado antes de correr el modo completo).
Datos: Chen, Y.-J., Topacio, A., Laveti, S., Jos, M. A., Hsiao, M.-H. (2025). CYCU pile load test database. Mendeley Data,
V1, doi:10.17632/x6c63j8bv8.1. Licencia CC BY 4.0. El Excel no se versiona: vive en _privado/.

Muestra confirmatoria: pruebas a compresión en arcilla (USCS solo de arcillas y limos, sin componente S ni G) con Su > 0,
L y B > 0, en tres hojas: «Drilled Shaft-Compression», «Driven Piles-Round-Compression» y
«Driven Piles-Square-Compression». Cada fila es una prueba con un estrato representativo.

  predicho = q_ult del motor con un estrato homogéneo de Su (fricción α·Su de la NSR-10 H.4.7-3 y punta 9·Su)
  medido   = L2 (Hirany y Kulhawy) en pilas excavadas; Davisson en pilotes hincados
  λ        = medido / predicho

Uso (desde packages/motor-pilotes, con python -I):
  python validacion/cycu_2025.py <cycu.xlsx> --conteo     # solo cuenta la muestra; no lee capacidades
  python validacion/cycu_2025.py <cycu.xlsx>              # análisis completo prerregistrado
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

from src.axial import Estrato, Pilote, capacidad_individual  # noqa: E402

SEMILLA, N_BOOT = 118, 10_000
FILA_INICIO = 6   # las 6 primeras filas son encabezado
# columnas (base 0) verificadas al inspeccionar la estructura del archivo
HOJAS = {
    "Drilled Shaft-Compression": dict(tipo="excavado", seccion="circular", uscs=7, su=25, L=36, B=37, qmax=46,
                                      medido=59, criterio="L2", alterno=61, alterno_nombre="Terzaghi y Peck"),
    "Driven Piles-Round-Compression": dict(tipo="hincado", seccion="circular", uscs=6, su=19, L=31, B=32, qmax=38,
                                           medido=61, criterio="Davisson", alterno=63, alterno_nombre="Terzaghi y Peck"),
    "Driven Piles-Square-Compression": dict(tipo="hincado", seccion="cuadrada", uscs=7, su=24, L=45, B=46, qmax=51,
                                            medido=None, criterio="Davisson", alterno=None, alterno_nombre="Terzaghi y Peck"),
}
GAMMA = 18.0   # no entra en α·Su ni en 9·Su (esfuerzos totales); el motor lo exige


def _num(v):
    return v if isinstance(v, (int, float)) and math.isfinite(v) else None


def es_arcilla(uscs: str | None) -> bool:
    """Todas las componentes de la clasificación (separadas por / o -) son de arcilla o limo: C, M u O; ninguna S ni G."""
    if not uscs:
        return False
    partes = [p.strip() for p in str(uscs).replace("/", "-").split("-") if p.strip()]
    return bool(partes) and all(p[0] in "CMO" for p in partes)


def _columnas_por_nombre(ws, nombre: str) -> list[int]:
    enc = [r for r in ws.iter_rows(min_row=1, max_row=FILA_INICIO, values_only=True)]
    return [j for j in range(ws.max_column) if any(j < len(r) and r[j] and nombre in str(r[j]) for r in enc)]


def leer(ruta: Path) -> tuple[list[dict], Counter]:
    import openpyxl
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    filas, excl = [], Counter()
    for hoja, c in HOJAS.items():
        ws = wb[hoja]
        c = dict(c)
        if c["medido"] is None:      # hoja cuadrada: ubicar Davisson y Terzaghi y Peck por nombre de encabezado
            c["medido"] = _columnas_por_nombre(ws, "Davisson")[0]
            c["alterno"] = [j for j in _columnas_por_nombre(ws, "Terzaghi") if j > 0][0]
        uscs_previo, ref_previa = None, None
        for r in ws.iter_rows(min_row=FILA_INICIO + 1, values_only=True):
            if not r or r[0] in (None, ""):
                continue
            ref = str(r[0]).rsplit("-", 1)[0]
            uscs = r[c["uscs"]]
            if uscs in (None, "") and ref == ref_previa:        # USCS solo en la primera fila del sitio: se arrastra
                uscs = uscs_previo
            uscs_previo, ref_previa = uscs, ref
            base = {"hoja": hoja, "id": str(r[0]), "referencia": ref, "tipo": c["tipo"], "seccion": c["seccion"],
                    "uscs": uscs, "su": _num(r[c["su"]]), "L": _num(r[c["L"]]), "B": _num(r[c["B"]]),
                    "criterio": c["criterio"], "_r": r, "_c": c}
            if not es_arcilla(uscs):
                excl["no es arcilla (USCS)"] += 1
                continue
            if not (base["su"] and base["su"] > 0):
                excl["sin Su"] += 1
                continue
            if not (base["L"] and base["B"] and base["L"] > base["B"] > 0):
                excl["geometría incompleta"] += 1
                continue
            filas.append(base)
    return filas, excl


def con_capacidad(filas: list[dict], excl: Counter) -> list[dict]:
    out = []
    for f in filas:
        r, c = f.pop("_r"), f.pop("_c")
        med, qmax, alt = _num(r[c["medido"]]), _num(r[c["qmax"]]), _num(r[c["alterno"]])
        if not (med and med > 0):
            excl["sin capacidad interpretada"] += 1
            continue
        if qmax and med > qmax * 1.0001:
            excl["capacidad extrapolada (Qm > Qmax)"] += 1
            continue
        pil = Pilote(seccion=f["seccion"], ancho_m=f["B"], longitud_m=f["L"], tipo=f["tipo"])
        est = [Estrato(espesor_m=f["L"] + 10 * f["B"], gamma_kn_m3=GAMMA, comportamiento="no_drenado", su_kpa=f["su"])]
        p = capacidad_individual(est, pil, nivel_freatico_m=None, combinacion="cm_cv_normal")
        f.update(medido_kn=med, alterno_kn=alt if (alt and (not qmax or alt <= qmax * 1.0001)) else None,
                 pred_kn=p["q_ult_kn"], lam=med / p["q_ult_kn"])
        out.append(f)
    return out


def _boot_cluster(filas: list[dict], estad, rng: random.Random) -> tuple[float, float]:
    grupos = defaultdict(list)
    for f in filas:
        grupos[f["referencia"]].append(f)
    claves = list(grupos)
    vals = []
    for _ in range(N_BOOT):
        muestra = [f for k in rng.choices(claves, k=len(claves)) for f in grupos[k]]
        vals.append(estad(muestra))
    vals.sort()
    return vals[int(0.025 * N_BOOT)], vals[int(0.975 * N_BOOT) - 1]


def gm(filas, clave="lam"):
    return math.exp(sum(math.log(f[clave]) for f in filas) / len(filas))


def cov(filas):
    xs = [f["lam"] for f in filas]
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) / m


def veredicto(lo: float, hi: float) -> str:
    if hi < 1.0:
        return "SOBREESTIMA (inseguro): IC95 de λ por debajo de 1"
    if lo > 1.0:
        return "CONSERVADOR: IC95 de λ por encima de 1"
    if lo >= 0.75 and hi <= 1.33:
        return "CALIBRADO: IC95 contiene 1 y queda en [0,75; 1,33]"
    return "NO CONCLUYENTE: IC95 contiene 1 pero es más ancho que [0,75; 1,33]"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--conteo", action="store_true")
    a = ap.parse_args()
    filas, excl = leer(a.xlsx)
    if a.conteo:
        print(f"Candidatas (antes de leer capacidades): {len(filas)}")
        print("  por tipo:", dict(Counter(f["tipo"] for f in filas)))
        print("  por hoja:", dict(Counter(f["hoja"] for f in filas)))
        print("  referencias (sitios) distintas:", len({f['referencia'] for f in filas}))
        print("  exclusiones:", dict(excl))
        return
    filas = con_capacidad(filas, excl)
    rng = random.Random(SEMILLA)
    print(f"n = {len(filas)} pruebas en {len({f['referencia'] for f in filas})} referencias; exclusiones: {dict(excl)}\n")
    print("| Grupo | n | sitios | λ media geométrica | IC95 (bootstrap por sitio) | COV de λ | Veredicto |")
    print("|---|---|---|---|---|---|---|")
    grupos = {"Todas": filas, "Excavadas (L2)": [f for f in filas if f["tipo"] == "excavado"],
              "Hincadas (Davisson)": [f for f in filas if f["tipo"] == "hincado"]}
    for nombre, g in grupos.items():
        if len(g) < 3:
            print(f"| {nombre} | {len(g)} | — | — | — | — | n insuficiente |")
            continue
        lo, hi = _boot_cluster(g, gm, rng)
        print(f"| {nombre} | {len(g)} | {len({f['referencia'] for f in g})} | {gm(g):.3f} | [{lo:.3f}, {hi:.3f}] | "
              f"{cov(g):.2f} | {veredicto(lo, hi)} |")
    exc, hin = grupos["Excavadas (L2)"], grupos["Hincadas (Davisson)"]
    if len(exc) >= 3 and len(hin) >= 3:
        def dif(m):
            e = [f for f in m if f["tipo"] == "excavado"]
            h = [f for f in m if f["tipo"] == "hincado"]
            return math.log(gm(e)) - math.log(gm(h)) if e and h else 0.0
        lo, hi = _boot_cluster(filas, dif, rng)
        print(f"\nH2 (exploratoria): ln λ excavadas − ln λ hincadas = {dif(filas):.3f}, IC95 [{lo:.3f}, {hi:.3f}]")
    alt = [f for f in filas if f["alterno_kn"]]
    if alt:
        print(f"\nSensibilidad al criterio de falla (Terzaghi y Peck, n = {len(alt)}): λ media geométrica "
              f"{math.exp(sum(math.log(f['alterno_kn'] / f['pred_kn']) for f in alt) / len(alt)):.3f}")
    lams = sorted(f["lam"] for f in filas)
    print(f"\nCuantiles de λ (todas): p10 {lams[len(lams) // 10]:.2f}, p50 {lams[len(lams) // 2]:.2f}, "
          f"p90 {lams[9 * len(lams) // 10]:.2f}; fracción con λ < 1 (motor sobreestima): "
          f"{sum(x < 1 for x in lams) / len(lams):.2f}")


if __name__ == "__main__":
    main()
