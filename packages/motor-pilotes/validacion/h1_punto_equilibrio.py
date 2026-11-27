"""H1 (#273): punto de equilibrio entre el diseño conservador de pilotes y una prueba de carga (NSR-10 H.4.7.3).

Prerregistro: validacion/PRERREGISTRO_H1_PUNTO_EQUILIBRIO.md (fijado antes de correr el análisis completo).

Qué compara, por escenario (perfil de suelo, tipo de pilote, carga por pilote, número de pilotes N):
  Sin prueba: L0 = longitud mínima con Q_adm(L) ≥ Q, factores de seguridad de la NSR-10 (motor de StructAI).
  Con prueba: H.4.7.3 permite (a) calcular la capacidad última a partir de la prueba y (b) reducir los factores de
              seguridad hasta el 80 % de la tabla. Con λ = medido / predicho, la capacidad admisible pasa a
              λ·Q_adm(L)/0,8, y L1(λ) = longitud mínima con λ·Q_adm(L)/0,8 ≥ Q.
  λ se toma de la base CYCU (Chen et al. 2025, CC BY 4.0), la misma de la validación del motor: arcilla para el perfil
  arcilloso, arena para el arenoso y ambas para el mixto. Un λ por proyecto (la prueba representa al sitio).
  Costo = N·L·precio por metro (INVIAS 2026-1) + n_pruebas·precio de la prueba.

Uso:
  python -I validacion/h1_punto_equilibrio.py <cycu.xlsx> --conteo   # λ y L0 (sin pruebas); no calcula ahorros
  python -I validacion/h1_punto_equilibrio.py <cycu.xlsx>            # análisis completo -> h1_resultados.json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

from src.arena_spt import EstratoSPT  # noqa: E402
from src.axial import Estrato, Pilote  # noqa: E402
from src.mixto import capacidad_mixta  # noqa: E402

import cycu_2025 as cy_arcilla  # noqa: E402
import cycu_arena_2025 as cy_arena  # noqa: E402

PRECIOS = json.loads((AQUI / "precios_invias_2026_1.json").read_text(encoding="utf-8"))["items"]
SALIDA = AQUI / "h1_resultados.json"
FACTOR_FS = 0.80              # H.4.7.3: FS ≥ 80 % de la tabla
NF_M = 1.0
L_MIN, L_MAX, PASO = 3.0, 40.0, 0.25
PROF_PERFIL = 50
N_PRINCIPAL, NT_PRINCIPAL, MULT_PRINCIPAL = 30, 1, 1
N_VALORES, NT_VALORES, MULT_VALORES = (10, 30, 100), (1, 2, 3), (1, 3, 10)
UMBRAL_AFIRMACION = 0.18      # límite inferior del 18-30 % afirmado
N_BOOT, SEMILLA = 2000, 1181


# ── perfiles fijos ─────────────────────────────────────────────────────────────────────────────────────────────────

def _arcilla(z):
    return Estrato(espesor_m=1.0, gamma_kn_m3=16.0, gamma_sat_kn_m3=16.5, comportamiento="no_drenado",
                   su_kpa=20.0 + 2.0 * (z + 0.5))


def _arena(z, n0):
    return EstratoSPT(espesor_m=1.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, n60=min(n0 + (z + 0.5), 50.0), suelo="arena")


PERFILES = {
    "arcilla_blanda": [_arcilla(z) for z in range(PROF_PERFIL)],
    "arena": [_arena(z, 8.0) for z in range(PROF_PERFIL)],
    "mixto": [_arcilla(z) for z in range(8)] + [_arena(z - 8, 15.0) for z in range(8, PROF_PERFIL)],
}
PILOTES = {   # nombre: (sección, ancho, tipo, ítem de precio por metro, ítem de prueba estática, cargas kN)
    "in_situ_d050": ("circular", 0.5, "excavado", "pilote_in_situ_d050", "prueba_estatica_in_situ", (300, 600, 1000)),
    "in_situ_d100": ("circular", 1.0, "excavado", "pilote_in_situ_d100", "prueba_estatica_in_situ", (1500, 3000)),
    "prefabricado_d050": ("circular", 0.5, "hincado", "pilote_prefabricado_d050", "prueba_estatica_prefabricado",
                          (300, 600, 1000)),
}
COMBOS = {"arcilla_blanda": ("in_situ_d050", "in_situ_d100", "prefabricado_d050"),
          "arena": ("in_situ_d050", "prefabricado_d050"),
          "mixto": ("in_situ_d050", "in_situ_d100", "prefabricado_d050")}
LAMBDA_DE = {"arcilla_blanda": ("arcilla",), "arena": ("arena",), "mixto": ("arcilla", "arena")}


def curva_qadm(perfil: str, pil: str) -> list[tuple[float, float]]:
    sec, b, tipo = PILOTES[pil][:3]
    out, L = [], L_MIN
    while L <= L_MAX + 1e-9:
        r = capacidad_mixta(PERFILES[perfil], Pilote(seccion=sec, ancho_m=b, longitud_m=L, tipo=tipo),
                            nivel_freatico_m=NF_M, combinacion="cm_cv_normal")
        out.append((L, r["q_adm_kn"]))
        L = round(L + PASO, 4)
    return out


def l_requerida(curva, q_kn: float, factor: float) -> float | None:
    for L, qa in curva:
        if factor * qa >= q_kn:
            return L
    return None   # no factible hasta L_MAX


# ── λ empíricos ────────────────────────────────────────────────────────────────────────────────────────────────────

def lambdas(xlsx: Path) -> dict[str, list[tuple[str, float]]]:
    out = {}
    for nombre, mod in (("arcilla", cy_arcilla), ("arena", cy_arena)):
        filas, excl = mod.leer(xlsx)
        filas = mod.con_capacidad(filas, excl)
        out[nombre] = [(f"{nombre}:{f['referencia']}", f["lam"]) for f in filas]
    return out


# ── costos ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def escenario(perfil, pil, q, lam_sitios, *, n=N_PRINCIPAL, nt=NT_PRINCIPAL, mult=MULT_PRINCIPAL, cuantil="p50",
              curva=None):
    curva = curva or curva_qadm(perfil, pil)
    p_m = PRECIOS[PILOTES[pil][3]][cuantil]
    c_prueba = nt * mult * PRECIOS[PILOTES[pil][4]]["p50"]
    L0 = l_requerida(curva, q, 1.0)
    if L0 is None:
        return None
    c0 = n * L0 * p_m
    Lfs = l_requerida(curva, q, 1.0 / FACTOR_FS)
    f_fs = (c0 - (n * Lfs * p_m + c_prueba)) / c0
    n_eq_fs = (c_prueba / (p_m * (L0 - Lfs))) if L0 > Lfs else math.inf
    L1 = []
    no_fact = 0
    for _, lam in lam_sitios:
        x = l_requerida(curva, q, lam / FACTOR_FS)
        if x is None:
            no_fact += 1
            x = L_MAX   # cota: el diseño con prueba necesitaría rediseño (más pilotes o mayor diámetro)
        L1.append(x)
    eL1 = sum(L1) / len(L1)
    c1 = n * eL1 * p_m + c_prueba
    return {"L0": L0, "L_solo_fs": Lfs, "E_L1": eL1, "ahorro_solo_fs": f_fs, "ahorro_empirico": (c0 - c1) / c0,
            "n_equilibrio_solo_fs": n_eq_fs,
            "n_equilibrio_empirico": (c_prueba / (p_m * (L0 - eL1))) if L0 > eL1 else math.inf,
            "p_prueba_alarga": sum(x > L0 for x in L1) / len(L1), "p_no_factible": no_fact / len(L1),
            "p_lambda_bajo_0_8": sum(lam < FACTOR_FS for _, lam in lam_sitios) / len(lam_sitios),
            "costo_prueba_sobre_c0": c_prueba / c0}


def ahorro_perfil(perfil, lam_sitios, curvas, **kw) -> float:
    vals = [escenario(perfil, pil, q, lam_sitios, curva=curvas[(perfil, pil)], **kw)
            for pil in COMBOS[perfil] for q in PILOTES[pil][5]]
    vals = [v["ahorro_empirico"] for v in vals if v]
    return sum(vals) / len(vals)


def boot_sitios(perfil, lam_sitios, curvas, rng) -> list[float]:
    por_sitio: dict[str, list] = {}
    for s, lam in lam_sitios:
        por_sitio.setdefault(s, []).append((s, lam))
    sitios = list(por_sitio)
    vals = []
    for _ in range(N_BOOT):
        muestra = [x for s in rng.choices(sitios, k=len(sitios)) for x in por_sitio[s]]
        vals.append(ahorro_perfil(perfil, muestra, curvas))
    vals.sort()
    return [vals[int(0.025 * N_BOOT)], vals[int(0.975 * N_BOOT) - 1]]


def veredicto(ic):
    if ic[0] >= UMBRAL_AFIRMACION:
        return "CONFIRMADO"
    if ic[1] < UMBRAL_AFIRMACION:
        return "REFUTADO"
    return "NO CONCLUYENTE"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--conteo", action="store_true")
    a = ap.parse_args()
    lam = lambdas(a.xlsx)
    lam_perfil = {p: [x for k in LAMBDA_DE[p] for x in lam[k]] for p in PERFILES}
    curvas = {(p, pil): curva_qadm(p, pil) for p in PERFILES for pil in COMBOS[p]}
    if a.conteo:
        for k, v in lam.items():
            print(f"λ {k}: n={len(v)}, sitios={len({s for s, _ in v})}")
        for (p, pil), c in curvas.items():
            print(p, pil, {q: l_requerida(c, q, 1.0) for q in PILOTES[pil][5]})
        return
    rng = random.Random(SEMILLA)
    out = {"prerregistro": "validacion/PRERREGISTRO_H1_PUNTO_EQUILIBRIO.md", "factor_fs": FACTOR_FS,
           "lambda_n": {k: len(v) for k, v in lam.items()},
           "lambda_sitios": {k: len({s for s, _ in v}) for k, v in lam.items()}, "principal": {}, "escenarios": [],
           "sensibilidad": {}}
    for p in PERFILES:
        val = ahorro_perfil(p, lam_perfil[p], curvas)
        ic = boot_sitios(p, lam_perfil[p], curvas, rng)
        out["principal"][p] = {"ahorro_empirico_medio": val, "ic95": ic, "veredicto": veredicto(ic)}
        for pil in COMBOS[p]:
            for q in PILOTES[pil][5]:
                e = escenario(p, pil, q, lam_perfil[p], curva=curvas[(p, pil)])
                out["escenarios"].append({"perfil": p, "pilote": pil, "q_kn": q, **(e or {"no_factible_sin_prueba": True})})
        sens = {}
        for n in N_VALORES:
            for nt in NT_VALORES:
                for mult in MULT_VALORES:
                    sens[f"N{n}_pruebas{nt}_precio_x{mult}"] = ahorro_perfil(p, lam_perfil[p], curvas, n=n, nt=nt, mult=mult)
        for cu in ("p10", "p90"):
            sens[f"precio_pilote_{cu}"] = ahorro_perfil(p, lam_perfil[p], curvas, cuantil=cu)
        out["sensibilidad"][p] = sens
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=lambda x: None if x == math.inf else x),
                      encoding="utf-8")
    print(json.dumps(out["principal"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
