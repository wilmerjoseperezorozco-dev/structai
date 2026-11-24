"""Validación prerregistrada de la v3 (#241): Ejemplo de diseño 1 (talud de corte) de FHWA-SA-96-069 (Byrne et al.,
1996; ROSA P. dot/42092, sha256 0e90485d…3c57), §5.1.1.1, Figuras 5.1 a 5.3. Es independiente de los dos apéndices de GEC 7
que ya se usaron.

Datos (págs. 147–156):
  H = 9,5 m; paramento con batería de 10° respecto de la vertical; talud de 20° en la corona en 6,0 m horizontales y
  luego horizontal. Suelo homogéneo: γ = 18 kN/m³, φ = 34°, c = 5 kPa, sin agua y sin sobrecarga.
  6 filas a 1,0 / 2,5 / 4,0 / 5,5 / 7,0 / 8,5 m bajo la corona, de 7,7 / 7,7 / 7,7 / 6,8 / 5,2 / 3,5 m, a 15°; SH = SV = 1,5 m.
  Cargas admisibles (SLD, Grupo I): arrancamiento 30,0 kN/m, tendón 118 kN, cabeza 90 kN. El FS se aplica solo al suelo:
  es el Método A.
  FS de la solución computarizada con superficies circulares:
    final (6 filas): 1,35;
    construcción (Fig. 5.3), excavación de 2,0 + 1,5·k m con k filas:
      k = 0: 1,16 (control sin clavos); k = 1: 2,38; k = 2: 2,20; k = 3: 1,85; k = 4: 1,53; k = 5: 1,25.
  Comprobación a mano del libro (Fig. 5.2): cuña bilineal dada con interfaz horizontal (β = 0), F = 1,39.

Criterio prerregistrado (comentario en #241 antes de correr), sobre el FS que gobierna en la v3 (el menor entre círculos
de Bishop y dos cuñas):
  PASA si (1) |FS/1,35 − 1| ≤ 0,10 en el caso final y (2) al menos 4 de las 5 etapas con clavos quedan dentro de ±10 %.
  Se reportan sin cambiar el veredicto: el control sin clavos, los FS por superficie y la cuña a mano del libro.

Uso:  python validacion/fhwa_sa96069_ejemplo1.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import cunas as CUNAS  # noqa: E402
from src.suelo_cosido import EST, Capacidades, FilaClavos, analizar, perfil_muro, refuerzos  # noqa: E402

H, BATERIA, TALUD, ANCHO = 9.5, 10.0, 20.0, 6.0
PROF = (1.0, 2.5, 4.0, 5.5, 7.0, 8.5)
LONG = (7.7, 7.7, 7.7, 6.8, 5.2, 3.5)
CAP = Capacidades(tension_kn=118.0, adherencia_kn_m=30.0, paramento_kn=90.0)
SUELO = dict(gamma_kn_m3=18.0, c_kpa=5.0, phi_deg=34.0)
FS_FINAL = 1.35
FS_ETAPAS = {1: 2.38, 2: 2.20, 3: 1.85, 4: 1.53, 5: 1.25}
FS_CONTROL = 1.16
TOL = 0.10


def correr(altura: float, n_filas: int) -> dict:
    filas = [FilaClavos(d, L) for d, L in zip(PROF[:n_filas], LONG[:n_filas])]
    return analizar(altura_m=altura, filas=filas, inclinacion_deg=15.0, sh_m=1.5, cap=CAP, **SUELO,
                    bateria_deg=BATERIA, talud_corona_deg=TALUD, ancho_talud_corona_m=ANCHO, superficie="ambas")


def control_sin_clavos(altura: float) -> dict:
    p = perfil_muro(altura, BATERIA, TALUD, ANCHO)
    suelo = EST.SueloExc(18.0, 5.0, 34.0)
    circ = EST.factor_seguridad_talud(p, suelo, grieta_traccion=False, paramento_continuo=True).fs
    cun = CUNAS.buscar(EST, p, EST._capas(suelo, ())).fs
    return {"fs": min(circ, cun), "fs_circulo": circ, "fs_cuna": cun}


def cuna_del_libro() -> float:
    p = perfil_muro(H, BATERIA, TALUD, ANCHO)
    xb, yb = 7.72 * math.cos(math.radians(29.75)), 7.72 * math.sin(math.radians(29.75))
    xe = xb + 9.00 * math.cos(math.radians(60.96))
    refs = refuerzos(H, [FilaClavos(d, L) for d, L in zip(PROF, LONG)], 15.0, 1.5, CAP, bateria_deg=BATERIA)
    return CUNAS.fs_cunas(EST, p, EST._capas(EST.SueloExc(18.0, 5.0, 34.0), ()), xb, yb, xe, refuerzos=refs,
                          interfaz="horizontal")


def _fila(r: dict, ref: float) -> dict:
    return {"fs_v3": round(r["fs"], 3), "fs_libro": ref, "desvio_rel": round(r["fs"] / ref - 1, 4),
            "dentro": abs(r["fs"] / ref - 1) <= TOL, "gobierna": r.get("superficie"),
            "fs_circulo": round(r.get("fs_circulo", float("nan")), 3), "fs_cuna": round(r.get("fs_cuna", float("nan")), 3)}


def main() -> None:
    salida = {"final": _fila(correr(H, 6), FS_FINAL)}
    for k, ref in FS_ETAPAS.items():
        salida[f"etapa_{k}_filas"] = _fila(correr(2.0 + 1.5 * k, k), ref)
    c = control_sin_clavos(2.0)
    salida["control_sin_clavos"] = {"fs_v3": round(c["fs"], 3), "fs_libro": FS_CONTROL,
                                    "desvio_rel": round(c["fs"] / FS_CONTROL - 1, 4),
                                    "fs_circulo": round(c["fs_circulo"], 3), "fs_cuna": round(c["fs_cuna"], 3)}
    fl = cuna_del_libro()
    salida["cuna_del_libro_beta0"] = {"fs_motor": round(fl, 3), "fs_libro": 1.39, "desvio_rel": round(fl / 1.39 - 1, 4)}
    etapas_ok = sum(salida[f"etapa_{k}_filas"]["dentro"] for k in FS_ETAPAS)
    salida["etapas_dentro"] = etapas_ok
    salida["veredicto"] = "PASA" if salida["final"]["dentro"] and etapas_ok >= 4 else "NO PASA"
    print(json.dumps(salida, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
