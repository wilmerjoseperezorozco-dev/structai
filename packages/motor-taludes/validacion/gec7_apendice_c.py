"""Validación prerregistrada (#241): estabilidad global del ejemplo del Apéndice C de FHWA GEC 7 contra SNAP-2.

Muro vertical de 25 ft, arena limosa (γ = 125 pcf, φ' = 32°, c' = 100 psf, qu = 14,5 psi), 5 filas de clavos #7 grado 75
de 18 ft a 15°, en profundidades 3, 8, 13, 18 y 23 ft, SH = SV = 5 ft, DDH = 6 in; sobrecarga de 150 psf en 25 ft.
SNAP-2 (Tabla C.4): FS = 1,62 sin sobrecarga (etapa 6) y 1,51 con sobrecarga (etapa 7). Tabla C.5: modos por clavo.

Uso:  python validacion/gec7_apendice_c.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.clavos import (FS_GEC7, arrancamiento_por_metro_kn, cono_final, fs_tension, pernos_cabeza_kn,  # noqa: E402
                        flexion_paramento_kn, punzonamiento_kn, tension_tendon_kn)
from src.suelo_cosido import Capacidades, FilaClavos, analizar  # noqa: E402

FT, IN, PSI, KIP, PCF = 0.3048, 0.0254, 6.894757, 4.448222, 0.157087
FC, FY60, FY75 = 4000 * PSI / 1000, 60 * PSI, 75 * PSI
SNAP2 = {"sin_sobrecarga": 1.62, "con_sobrecarga": 1.51}
TOLERANCIA = 0.10
MODOS_C5 = ["arrancamiento", "arrancamiento", "arrancamiento", "arrancamiento", "tension"]
T_C5_KIP = [3.2, 7.2, 12.5, 19.0, 24.7]


def capacidades() -> Capacidades:
    fs = FS_GEC7["estatica"]
    a = 0.20 * IN * IN / FT
    rff = flexion_paramento_kn(espesor_m=8 * IN, fc_mpa=FC, fy_mpa=FY60, a_vn=a, a_vm=a, a_hn=a, a_hm=a,
                               sh_m=5 * FT, sv_m=5 * FT, cf=1.0)
    rfp = punzonamiento_kn(FC, *cono_final(4.125 * IN, 1 * IN, 0.31 * IN, 6 * IN))
    rfh = pernos_cabeza_kn(4, 0.5 * IN, FY60)
    paramento = min(rff / fs["flexion_paramento"], rfp / fs["punzonamiento"], rfh / fs["perno_a307"])
    return Capacidades(tension_kn=tension_tendon_kn(0.60 * IN * IN, FY75) / fs_tension(FY75),
                       adherencia_kn_m=arrancamiento_por_metro_kn(14.5 * PSI, 6 * IN) / fs["arrancamiento"],
                       paramento_kn=paramento)


def correr(sobrecarga: bool) -> dict:
    return analizar(altura_m=25 * FT, filas=[FilaClavos(d * FT, 18 * FT) for d in (3, 8, 13, 18, 23)],
                    inclinacion_deg=15.0, sh_m=5 * FT, cap=capacidades(), gamma_kn_m3=125 * PCF,
                    c_kpa=100 * PSI / 144, phi_deg=32.0, sobrecarga_kpa=150 * PSI / 144 if sobrecarga else 0.0,
                    ancho_sobrecarga_m=25 * FT if sobrecarga else None, grieta_traccion=False)


def main() -> None:
    salida = {}
    for clave, sc in (("sin_sobrecarga", False), ("con_sobrecarga", True)):
        r = correr(sc)
        salida[clave] = {"fs_motor": round(r["fs"], 3), "fs_snap2": SNAP2[clave],
                         "dentro": abs(r["fs"] - SNAP2[clave]) <= TOLERANCIA, "circulo": r["circulo"],
                         "en_borde_dominio": r["en_borde_dominio"],
                         "clavos": [{"t_kip": round(c["t_kn"] / KIP, 2), "gobierna": c["gobierna"],
                                     "l_delante_ft": None if c["l_delante_m"] is None else round(c["l_delante_m"] / FT, 1)}
                                    for c in r["clavos"]]}
    c7 = salida["con_sobrecarga"]["clavos"]
    salida["modos_coinciden_c5"] = sum(c["gobierna"] == m for c, m in zip(c7, MODOS_C5))
    salida["veredicto"] = "PASA" if all(salida[k]["dentro"] for k in SNAP2) else "NO PASA"
    print(json.dumps(salida, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
