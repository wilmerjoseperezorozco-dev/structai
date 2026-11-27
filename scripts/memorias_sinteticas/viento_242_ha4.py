"""#242, hipótesis H-A4: levantamiento neto en la correa de una cubierta liviana (succión B.6 de componentes y
revestimientos). Separado de viento_242.py el 2026-11-26 junto con el módulo cubierta_liviana, que sigue SIN VALIDAR
(FEMA P-55 Ej. 9.1 no pasó por la regla de zona). Los resultados ya medidos están en RESULTADOS_242_VIENTO_ALTURA.md.

Uso:  python -I scripts/memorias_sinteticas/viento_242_ha4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confiabilidad_f3 as f3  # noqa: E402

RAIZ = f3.RAIZ


def cubierta_liviana_tabla() -> dict:
    """H-A4 (determinista): fracción de combinaciones región × exposición × zona con levantamiento neto
    1,6·|p| > 0,9·D en la correa (θ = 5°, h = 6 m, luz 5 m → área efectiva L²/3, GCpi +0,18), por peso D."""
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    b6 = de._b6
    from motor_viento import cubierta_liviana as cl
    out = {}
    for peso in (0.15, 0.30, 0.50):
        filas = []
        for reg, v in b6.V_REGION.items():
            for e in ("B", "C", "D"):
                qh = b6.qz(v, b6.kz(6.0, e), 1.0, b6.KD_EDIFICIOS, 1.0) / 1000
                for z in ("1", "2", "3"):
                    p = cl.succion(qh, z, 25 / 3, 5.0, b6.GCPI["cerrado"])
                    filas.append({"region": reg, "exp": e, "zona": z, "p_kpa": p, "razon_succion_D": abs(p) / peso,
                                  "neto": 1.6 * abs(p) > 0.9 * peso})
        k = sum(f["neto"] for f in filas)
        sin = [f"{f['region']}-{f['exp']}-{f['zona']}" for f in filas if not f["neto"]]
        out[f"D={peso}"] = {"n": len(filas), "k_neto": k, "frac": k / len(filas), "sin_levantamiento": sin,
                            "frac_neto_si_succion>5D": (sum(f["neto"] for f in filas if f["razon_succion_D"] > 5) /
                                                        max(1, sum(f["razon_succion_D"] > 5 for f in filas)))}
    return out


if __name__ == "__main__":
    print(json.dumps(cubierta_liviana_tabla(), ensure_ascii=False, indent=1))
