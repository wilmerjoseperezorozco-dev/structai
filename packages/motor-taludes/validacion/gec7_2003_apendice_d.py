"""Validación prerregistrada de la v2 (#241): estabilidad global del ejemplo del Apéndice D de FHWA GEC 7 de 2003
(FHWA-IF-03-017, Lazarte et al.) contra SNAIL. Es un caso independiente del Apéndice C de 2015, que ya se usó en la v1.

Datos (págs. D-1 a D-21, Figuras D.1, D.2 y D.7, Tablas D.2 y D.3, fe de erratas 11 y 12):
  Muro vertical de H = 10 m. Estrato 1 (0–9 m): γ = 18 kN/m³, φ' = 33°, c' = 0, qu = 100 kPa.
  Estrato 2 (bajo 9 m): γ = 20 kN/m³, φ' = 39°, c' = 0, qu = 150 kPa. Sin agua.
  7 filas en 0,5 / 2,0 / 3,5 / 5,0 / 6,5 / 8,0 / 9,5 m; i = 20° en la fila 1 y 15° en las demás; SH = SV = 1,5 m; DDH = 150 mm.
  SNAIL en modo "Ultimate" (fe de erratas 11): capacidades últimas divididas por el FS global (Método B).
  Diámetro y paramento "artificialmente grandes" para que gobierne el arrancamiento: PS = 500 kN en la Figura D.7.
  Carga viva: 0,6 m de suelo (10,8 kPa) sobre la vía, de 3,0 a 10,3 m detrás del muro (Figura D.1 y bloque de la D.7).
  Caso 2: longitud uniforme L = 7,0 m, D + L, FS = 1,51.
  Caso 4: L = 10, 10, 10, 7, 7, 5, 5 m, D + L, FS = 1,50.
  Caso 5: como el 4, D + EQ (sin carga viva), kh = 0,17, FS = 1,13.
  Control (sin clavos): caso 1, H = 0,7 m, c' = 2,5 kPa, FS = 1,23.

Criterio prerregistrado (comentario en #241 antes de correr): PASA si |FS_motor / FS_SNAIL − 1| ≤ 0,10 en los casos 2 y 4.
La tolerancia es la mayor discrepancia |SLIDE/SNAIL − 1| de la Tabla 10 de FHWA-NHI-17-068 (grupos I a M, 9,9 %): Bishop
con círculos frente a las cuñas bilineales de SNAIL. Caso 5, control y sensibilidades se reportan sin cambiar el veredicto.

Uso:  python validacion/gec7_2003_apendice_d.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.suelo_cosido import EST, Capacidades, EstratoCosido, FilaClavos, analizar  # noqa: E402

H, SH, DDH = 10.0, 1.5, 0.150
PROF = (0.5, 2.0, 3.5, 5.0, 6.5, 8.0, 9.5)
INCL = (20.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0)
L_UNIFORME = (7.0,) * 7
L_NO_UNIFORME = (10.0, 10.0, 10.0, 7.0, 7.0, 5.0, 5.0)
Q_VIVA, VIA = 0.6 * 18.0, (3.0, 10.3)
SNAIL = {"caso_2": 1.51, "caso_4": 1.50, "caso_5": 1.13, "control_caso_1": 1.23}
PRIMARIOS = ("caso_2", "caso_4")
TOLERANCIA_REL = 0.10
TENSION_GRANDE_KN = 1.0e5           # "artificially large values of nail diameter"
PS_KN = 500.0                       # Figura D.7


def _cap() -> Capacidades:
    return Capacidades(tension_kn=TENSION_GRANDE_KN, adherencia_kn_m=math.pi * 100.0 * DDH, paramento_kn=PS_KN)


def _estrato2() -> EstratoCosido:
    return EstratoCosido(prof_techo_m=9.0, gamma_kn_m3=20.0, c_kpa=0.0, phi_deg=39.0, adherencia_kn_m=math.pi * 150.0 * DDH)


def correr(longitudes, *, viva=True, kh=0.0, via=VIA, metodo="B") -> dict:
    filas = [FilaClavos(d, L, i) for d, L, i in zip(PROF, longitudes, INCL)]
    # La sobrecarga de `analizar` arranca en la corona; para la franja de la vía se llama al Bishop directamente.
    return _analizar_con_franja(filas, viva, kh, via, metodo)


def _analizar_con_franja(filas, viva, kh, via, metodo) -> dict:
    from src.suelo_cosido import refuerzos
    refs = refuerzos(H, filas, 15.0, SH, _cap(), [_estrato2()])
    estr = (EST.EstratoExc(H - 9.0, EST.SueloExc(20.0, 0.0, 39.0)),)
    perfil = EST.perfil_talud(H, 90.0)
    r = EST.factor_seguridad_talud(perfil, EST.SueloExc(18.0, 0.0, 33.0), sobrecarga_kpa=Q_VIVA if viva else 0.0,
                                   sobrecarga_x=(perfil.x_cresta + via[0], perfil.x_cresta + via[1]) if viva else None,
                                   kh=kh, grieta_traccion=False, refuerzos=refs, paramento_continuo=True,
                                   estratos=estr, metodo_refuerzo=metodo)
    clavos = []
    for ref in refs:
        t, _, modo = EST.fuerza_refuerzo(ref, r.xc, r.yc, r.radio)
        clavos.append({"t_kn": round(t * SH, 1), "gobierna": modo})
    return {"fs": r.fs, "circulo": {"xc": round(r.xc, 3), "yc": round(r.yc, 3), "radio": round(r.radio, 3)},
            "en_borde_dominio": r.en_borde_dominio, "clavos": clavos}


def control_caso_1() -> float:
    return EST.factor_seguridad_talud(EST.perfil_talud(0.7, 90.0), EST.SueloExc(18.0, 2.5, 33.0),
                                      grieta_traccion=False, paramento_continuo=True).fs


def main() -> None:
    res = {"caso_2": correr(L_UNIFORME), "caso_4": correr(L_NO_UNIFORME),
           "caso_5": correr(L_NO_UNIFORME, viva=False, kh=0.17)}
    salida = {}
    for k, r in res.items():
        salida[k] = {"fs_motor": round(r["fs"], 3), "fs_snail": SNAIL[k], "desvio_rel": round(r["fs"] / SNAIL[k] - 1, 4),
                     "dentro": abs(r["fs"] / SNAIL[k] - 1) <= TOLERANCIA_REL, "circulo": r["circulo"],
                     "en_borde_dominio": r["en_borde_dominio"], "clavos": r["clavos"]}
    fs1 = control_caso_1()
    salida["control_caso_1"] = {"fs_motor": round(fs1, 3), "fs_snail": SNAIL["control_caso_1"],
                                "desvio_rel": round(fs1 / SNAIL["control_caso_1"] - 1, 4)}
    salida["sensibilidades"] = {
        "caso_2_L_7_2": round(correr((7.2,) * 7)["fs"], 3),                  # LTOTAL U = 50,4 m (pág. D-19)
        "caso_2_viva_0_a_5m": round(correr(L_UNIFORME, via=(0.0, 5.0))["fs"], 3),   # texto: H/2 detrás del muro
        "caso_4_viva_0_a_5m": round(correr(L_NO_UNIFORME, via=(0.0, 5.0))["fs"], 3),
    }
    salida["veredicto"] = "PASA" if all(salida[k]["dentro"] for k in PRIMARIOS) else "NO PASA"
    print(json.dumps(salida, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
