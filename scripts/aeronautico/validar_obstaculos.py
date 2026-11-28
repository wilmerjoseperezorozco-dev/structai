"""Paso 5 de #332 fase 2: validación del techo aeronáutico contra obstáculos publicados (preregistro, «Validación»).

Criterio fijado antes de abrir el listado:
- ningún obstáculo debería superar el techo calculado en más de 5 m, salvo que el listado lo marque como aceptado o
  señalizado;
- si más del 5 % lo supera sin esa marca, la construcción de las superficies se considera errónea.

Fuentes:
1. Listado de obstáculos de la Aerocivil, «Obstáculos AMDT 72» (Conjunto de datos AIP, vigente 2026-07-09), hoja
   «All». Para SKBQ trae UNA fila, sin coordenadas: «Postes», 12 m, iluminado, «en área de aproximación y despegue,
   pista 23, 350 m del umbral, rumbo 220°». Se ubica en la prolongación del eje, 350 m antes del umbral 23.
   No dice si 12 m es cota o altura. Se evalúan las dos lecturas: 12 m s. n. m. y 12 m sobre el umbral 23.
2. Fuente secundaria (no preregistrada; se informa aparte): plano de obstáculos de aeródromo OACI tipo A, AD 2 SKBQ-41,
   AIRAC 69/25. Es un plano escaneado. Las distancias y cotas se leyeron a ojo sobre los perfiles, con incertidumbre de
   unos ±20 m en distancia y ±2 m en cota. Las distancias se cuentan desde el extremo de la pista, sobre la
   prolongación del eje (la pista no tiene umbrales desplazados: TORA = 3 000 m en los dos sentidos).

Uso (entorno geo): python -I scripts/aeronautico/validar_obstaculos.py [salida.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from georef_u16 import A_U16  # noqa: E402
from superficies import pista_skbq, techo  # noqa: E402

UMBRAL_EXCESO_M = 5.0
FRACCION_MAX = 0.05

# (fuente, id, extremo de referencia 'a' = umbral 05 (SO) o 'b' = umbral 23 (NE), distancia fuera de la pista [m],
#  cota del tope [m s. n. m.], marcado como señalizado/aceptado, nota)
OBSTACULOS = [
    ("listado_AMDT72", "postes_cota", "b", 350.0, 12.0, True, "12 m leído como cota; iluminado"),
    ("listado_AMDT72", "postes_altura", "b", 350.0, 16.15 + 12.0, True, "12 m leído como altura sobre el umbral 23"),
    ("plano_tipo_A", "1_obstaculo_movil_SO", "a", 740.0, 35.0, False, "lectura visual"),
    ("plano_tipo_A", "2_NE", "b", 170.0, 21.0, False, "lectura visual; barra delgada"),
    ("plano_tipo_A", "3_muro_NE", "b", 350.0, 2.0, False, "lectura visual"),
    ("plano_tipo_A", "4_obstaculo_movil_NE", "b", 600.0, 10.0, False, "lectura visual; meseta de 380 a 620 m"),
]


def punto_en_eje(pista, extremo: str, dist: float):
    a, b = np.array(pista.umbral_a), np.array(pista.umbral_b)
    u = (b - a) / np.linalg.norm(b - a)
    p = a - u * dist if extremo == "a" else b + u * dist
    return p


def main(salida: str | None = None):
    sys.stdout.reconfigure(encoding="utf-8")
    pista, arp = pista_skbq(lambda lo, la: A_U16.transform(lo, la))
    kw = dict(pista=pista, aprox_a="precision_cat1_3_4", aprox_b="no_precision_4", despegue="clave_3_4")
    filas = []
    for fuente, ident, ext, dist, cota, marcado, nota in OBSTACULOS:
        E, N = punto_en_eje(pista, ext, dist)
        h, limita, _ = techo(np.array([E]), np.array([N]), detalle=True, **kw)
        exceso = cota - float(h[0])
        filas.append({"fuente": fuente, "id": ident, "extremo": "umbral 05" if ext == "a" else "umbral 23",
                      "distancia_m": dist, "cota_m": round(cota, 2), "techo_m": round(float(h[0]), 2),
                      "superficie": str(limita[0]), "exceso_m": round(exceso, 2), "marcado": marcado, "nota": nota})
        print(f"{fuente:<15} {ident:<22} {dist:6.0f} m  cota {cota:6.2f}  techo {float(h[0]):6.2f} "
              f"({limita[0]})  exceso {exceso:+6.2f}")

    def evaluar(fuente):
        f = [r for r in filas if r["fuente"] == fuente]
        sin_marca = [r for r in f if not r["marcado"]]
        sobre = [r for r in sin_marca if r["exceso_m"] > UMBRAL_EXCESO_M]
        frac = len(sobre) / len(sin_marca) if sin_marca else None
        return {"n": len(f), "n_sin_marca": len(sin_marca), "n_exceso_mayor_5m_sin_marca": len(sobre),
                "fraccion": frac, "max_exceso_m": max(r["exceso_m"] for r in f),
                "erronea": bool(frac is not None and frac > FRACCION_MAX)}

    res = {"obstaculos": filas, "listado_preregistrado": evaluar("listado_AMDT72"),
           "plano_tipo_A_secundario": evaluar("plano_tipo_A")}
    print(json.dumps({k: v for k, v in res.items() if k != "obstaculos"}, ensure_ascii=False, indent=1))
    if salida:
        Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
