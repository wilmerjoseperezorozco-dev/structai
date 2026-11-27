"""Prueba de realidad de motor-pilotes con 5 pilotes de El Dorado, Bogotá (#118).

Prerregistro: https://github.com/wilmerjoseperezorozco-dev/structai/issues/118#issuecomment-6975779859
Fuente: Rodríguez, J. A., «Optimización de cimentaciones», 5.º Encuentro de Suelos y Estructuras, Escuela Colombiana de
Ingeniería. Ensayos PDA/CAPWAP de GRL Engineers y Jeoprobe, 2008. Solo se transcriben números.

Uso: python validacion/eldorado_2008.py   (desde packages/motor-pilotes)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

from src.axial import Estrato, Pilote, capacidad_individual  # noqa: E402

T_A_KN = 9.81
GAMMA = 12.8          # 1,3 t/m³ del artículo; no entra en α·Su ni en 9·Su (esfuerzos totales)
ESCENARIOS = {"bajo": (10.0, 20.0), "central": (15.0, 30.0), "alto": (20.0, 40.0)}   # Su (kPa) en 0–10 m y > 10 m
PILOTES = [  # nombre, sección, ancho (m), L efectiva (m), tipo, medido total / fricción / punta (t)
    ("Preexcavado 1", "circular", 0.60, 32.0, "excavado", 192, 180, 12),
    ("Preexcavado 2 este", "circular", 0.60, 32.0, "excavado", 212, 184, 28),
    ("Preexcavado 3", "circular", 0.60, 38.0, "excavado", 308, 264, 44),
    ("Hincado 1", "cuadrada", 0.30, 39.0, "hincado", 132, 126, 6),
    ("Hincado 2", "cuadrada", 0.30, 39.0, "hincado", 128, 119, 9),
]


def perfil(su_sup: float, su_inf: float) -> list[Estrato]:
    return [Estrato(espesor_m=10.0, gamma_kn_m3=GAMMA, comportamiento="no_drenado", su_kpa=su_sup),
            Estrato(espesor_m=60.0, gamma_kn_m3=GAMMA, comportamiento="no_drenado", su_kpa=su_inf)]


def evaluar() -> list[dict]:
    filas = []
    for nombre, sec, b, L, tipo, tot, fric, punta in PILOTES:
        pil = Pilote(seccion=sec, ancho_m=b, longitud_m=L, tipo=tipo)
        pred = {k: capacidad_individual(perfil(*su), pil, nivel_freatico_m=None, combinacion="cm_cv_normal")
                for k, su in ESCENARIOS.items()}
        med = tot * T_A_KN
        filas.append({"pilote": nombre, "tipo": tipo, "medido_kn": med, "medido_friccion_kn": fric * T_A_KN,
                      "medido_punta_kn": punta * T_A_KN,
                      **{f"pred_{k}_kn": r["q_ult_kn"] for k, r in pred.items()},
                      "pred_central_friccion_kn": pred["central"]["qs_ult_kn"],
                      "pred_central_punta_kn": pred["central"]["qp_ult_kn"],
                      "lambda_total": med / pred["central"]["q_ult_kn"],
                      "lambda_friccion": fric * T_A_KN / pred["central"]["qs_ult_kn"],
                      "en_banda": pred["bajo"]["q_ult_kn"] <= med <= pred["alto"]["q_ult_kn"]})
    return filas


def main() -> None:
    filas = evaluar()
    print("| Pilote | Medido (kN) | Banda motor bajo–alto (kN) | Central (kN) | λ total | λ fricción | ¿En banda? |")
    print("|---|---|---|---|---|---|---|")
    for f in filas:
        print(f"| {f['pilote']} | {f['medido_kn']:.0f} | {f['pred_bajo_kn']:.0f}–{f['pred_alto_kn']:.0f} | "
              f"{f['pred_central_kn']:.0f} | {f['lambda_total']:.2f} | {f['lambda_friccion']:.2f} | "
              f"{'sí' if f['en_banda'] else 'no'} |")
    n_banda = sum(f["en_banda"] for f in filas)
    gm = math.exp(sum(math.log(f["lambda_total"]) for f in filas) / len(filas))
    print(f"\nEn banda: {n_banda}/5 → {'PASA' if n_banda >= 4 else 'NO PASA'} (criterio ≥ 4/5)")
    print(f"Media geométrica λ total (central): {gm:.3f}")
    for tipo in ("excavado", "hincado"):
        sub = [f["lambda_total"] for f in filas if f["tipo"] == tipo]
        print(f"  {tipo}: λ total = {', '.join(f'{x:.2f}' for x in sub)}")


if __name__ == "__main__":
    main()
