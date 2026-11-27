"""Validación prerregistrada del motor de viento B.6 v1 (#292) contra FEMA P-55 (2011), Vol. II, Cap. 8,
Ejemplos 8.5 (levantamiento cubierta-muro, envolvente de edificios bajos) y 8.7 (succión en entablado, C&C).

Fuente: FEMA P-55 Coastal Construction Manual, 4.ª ed., 2011 (obra del gobierno de EE. UU.), capítulo 8 descargado
del archivo web de UNT; sha256 9297384e…8b68b38. Usa ASCE 7-10, cuyos GCpf (Fig. 28.4-1) y GCp (Fig. 30.4-2A/B/C)
coinciden con las Figs. B.6.5-7 y B.6.5-8 de la NSR-10 (cotejado). Se compara con la V y los factores del libro
(ASD, 0,6D + 0,6W); la V de diseño y las combinaciones de la NSR-10 no se validan aquí.

Datos de entrada (enunciados):
  8.5: luz 24 ft, aleros de 2 ft, D = 10 psf (cubierta + cielo raso), V = 150 mph, exposición C, h = 33 ft,
       cerrado, Kz = 1,0, Kzt = 1,0, Kd = 0,85.
  8.7: mismo sitio; q (ASD) = 29,38 psf; GCpi = 0,18; área efectiva 10 ft².

Contaminación declarada (vista al leer los enunciados, antes de implementar): en 8.5 el libro usa 0,6D + 0,6W,
GCpi = 0,18, G·Cp = 0,68 en la cara inferior del alero a barlovento, GCpf de borde y "la mayor fuerza ocurre con 20°".

Criterio (prerregistrado en #292 antes de abrir las soluciones):
  H1 (8.7): cada presión de succión reportada por el libro para cubierta (zonas 1, 2, 3) y muro (4, 5), con la
      figura que el libro use, dentro de ±5 %.
  H2 (8.5): cada levantamiento neto en la conexión cubierta-muro reportado por el libro (cada pendiente), con el
      modelo de `levantamiento_cubierta` fijado en b6.py, dentro de ±10 %.
  PASA si H1 y H2. Se informan sin cambiar el veredicto: el viento solo, la variante con la cara inferior a sotavento.
  Los valores del libro se capturan en LIBRO_* después de publicar el prerregistro, sin tocar la lógica.

Uso:  python validacion/fema_p55_ejemplos_8_5_8_7.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import b6  # noqa: E402

PSF = 47.880259          # Pa por psf
PLF = 14.593903          # N/m por lb/ft
FT = 0.3048
MPH = 0.44704
TOL_H1, TOL_H2 = 0.05, 0.10

# ---- se llenan con los resultados del libro después del prerregistro
LIBRO_8_7: dict = {"cubierta_1": 34.7, "cubierta_2": 58.2, "cubierta_3": 87.5, "muro_4": 37.6, "muro_5": 46.4,
                   "_theta": 5.0, "_theta_muro": 20.0}   # Tabla 8-8, 150 mph; cubierta con Fig. 30.4-2A, muros sin reducción
LIBRO_8_5: dict = {20.0: 424.0}   # Tabla 8-6 y Ej. 8.5: luz 24 ft, 150 mph, θ = 20°


def ejemplo_8_7() -> dict:
    q = 29.38 * PSF
    a = 10 * FT ** 2
    theta = LIBRO_8_7.get("_theta", 20.0)
    out = {}
    for z in ("1", "2", "3"):
        out[f"cubierta_{z}"] = b6.presiones_netas(q, b6.gcp_cubierta(z, a, theta), 0.18)[1] / PSF
    for z in ("4", "5"):
        out[f"muro_{z}"] = b6.presiones_netas(q, b6.gcp_muro(z, a, theta_deg=LIBRO_8_7.get("_theta_muro", theta)), 0.18)[1] / PSF
    return out


def ejemplo_8_5(theta: float, **kw) -> dict:
    q = b6.qz(150 * MPH, 1.0, 1.0, 0.85)          # ASCE 7-10: sin I (la V ya es última)
    r = b6.levantamiento_cubierta(q, theta, 24 * FT, 2 * FT, 10 * PSF, factor_d=0.6, factor_w=0.6, **kw)
    return {"asd_plf": r.reaccion_barlovento_n_m / PLF, "viento_solo_plf": r.viento_barlovento_n_m / PLF,
            "q_psf": q / PSF}


def _cmp(motor, libro, tol):
    d = motor / libro - 1
    return {"motor": round(motor, 2), "libro": libro, "desvio": round(d, 4), "dentro": abs(d) <= tol}


def main() -> None:
    sal = {"8.7": {}, "8.5": {}}
    m87 = ejemplo_8_7()
    for k, v in m87.items():
        if k.startswith("_"):
            continue
        sal["8.7"][k] = _cmp(abs(v), LIBRO_8_7[k], TOL_H1)  # post hoc: el libro tabula la succión en magnitud if k in LIBRO_8_7 else {"motor": round(v, 2)}
    tetas = sorted(set(LIBRO_8_5) | {0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0})
    for t in tetas:
        m = ejemplo_8_5(t)
        fila = _cmp(m["asd_plf"], LIBRO_8_5[t], TOL_H2) if t in LIBRO_8_5 else {"motor": round(m["asd_plf"], 1)}
        fila["viento_solo_plf"] = round(m["viento_solo_plf"], 1)
        fila["con_inferior_sotavento"] = round(ejemplo_8_5(t, alero_sotavento_inferior=True)["asd_plf"], 1)
        sal["8.5"][f"theta_{t:g}"] = fila
    sal["q_8_5_psf"] = round(ejemplo_8_5(20.0)["q_psf"], 2)
    h1 = [v["dentro"] for v in sal["8.7"].values() if "dentro" in v]
    h2 = [v["dentro"] for v in sal["8.5"].values() if "dentro" in v]
    sal["H1"] = f"{sum(h1)}/{len(h1)}"
    sal["H2"] = f"{sum(h2)}/{len(h2)}"
    sal["veredicto"] = ("PASA" if h1 and h2 and all(h1) and all(h2) else
                        "SIN DATOS DEL LIBRO" if not (h1 and h2) else "NO PASA")
    print(json.dumps(sal, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
