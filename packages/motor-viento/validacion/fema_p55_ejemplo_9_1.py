"""Validación prerregistrada de `cubierta_liviana.separacion_maxima` contra FEMA P-55 (2011), Vol. II, Cap. 9,
Ejemplo 9.1 (separación de clavos del entablado de cubierta por succión), cap. 9 de UNT, sha256 44c00c55…b68b38.

Datos (enunciado): V = 150 mph (ASCE 7-10), exposición D; entablado OSB 7/16 in; clavo 8d con capacidad a extracción de
66 lb por clavo (NDS, ASD); separación de viguetas 16 in y 24 in; zona de borde perimetral. Altura media de 33 ft
(la de las Tablas 8-6 a 8-9 que el ejemplo usa).

Supuestos fijados ANTES de leer la solución:
  - "perimeter edge zone" = zona 2 (en ASCE, la 3 es la esquina);
  - A = 10 ft² (meseta) y GCp de la figura de θ ≤ 7° (la envolvente que usa la Tabla 8-8), GCpi = +0,18;
  - ASD: 0,6·W sin carga muerta (el enunciado no da el peso del entablado);
  - Kz de exposición D a 33 ft con la fórmula de la NSR-10 (Tabla B.6.5-3, nota 2).
Independencia limitada: comparte qh y GCp con el Ejemplo 8.7, ya usado. Lo nuevo es la conversión a separación.

Criterio (prerregistrado en #292): para cada separación de viguetas, si el libro reporta la separación sin redondear,
|s_motor/s_libro − 1| ≤ 5 %; si solo reporta la separación adoptada (redondeada), s_libro ≤ s_motor < 1,5·s_libro.
PASA si se cumple en los dos casos.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import b6  # noqa: E402
from src.cubierta_liviana import separacion_maxima, succion  # noqa: E402

FT, IN, MPH, LB = 0.3048, 0.0254, 0.44704, 4.4482216e-3   # m, m, m/s, kN
LIBRO_SIN_REDONDEO: dict = {}   # {16: in, 24: in}, se llena después del prerregistro
LIBRO_ADOPTADA: dict = {16: 4.0, 24: 3.0}   # Ej. 9.1: "specify 4-in." y "3-in." (zona 3 de alero, no zona 2)


def motor() -> dict:
    kz = b6.kz(33 * FT, "D")
    qh = b6.qz(150 * MPH, kz, 1.0, 0.85) / 1000.0                        # kN/m², sin factor (ASCE 7-10: sin I)
    p = succion(qh, "2", 10 * FT ** 2, 5.0, 0.18)
    out = {"Kz_D": kz, "qh_asd_psf": 0.6 * qh * 1000 / 47.880259, "p_asd_psf": 0.6 * p * 1000 / 47.880259}
    for s in (16, 24):
        out[s] = separacion_maxima(p, s * IN, 66 * LB, 0.0, factor_w=0.6, factor_d=0.0) / IN
    return out


def main() -> None:
    m = motor()
    sal = {"Kz_D": round(m["Kz_D"], 4), "qh_asd_psf": round(m["qh_asd_psf"], 2), "p_asd_psf": round(m["p_asd_psf"], 2)}
    ok = []
    for s in (16, 24):
        f = {"s_motor_in": round(m[s], 2)}
        if s in LIBRO_SIN_REDONDEO:
            d = m[s] / LIBRO_SIN_REDONDEO[s] - 1
            f |= {"s_libro_in": LIBRO_SIN_REDONDEO[s], "desvio": round(d, 4), "dentro": abs(d) <= 0.05}
        elif s in LIBRO_ADOPTADA:
            f |= {"s_adoptada_libro_in": LIBRO_ADOPTADA[s], "dentro": LIBRO_ADOPTADA[s] <= m[s] < 1.5 * LIBRO_ADOPTADA[s]}
        if "dentro" in f:
            ok.append(f["dentro"])
        sal[f"viguetas_{s}in"] = f
    sal["veredicto"] = "SIN DATOS DEL LIBRO" if len(ok) < 2 else ("PASA" if all(ok) else "NO PASA")
    print(json.dumps(sal, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
