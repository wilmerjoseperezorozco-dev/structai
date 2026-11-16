"""Condición 4 de docs/REGLAS_MOTORES_DE_CALCULO.md: llamada real a la revisión de Cloud Run, comparada con un cálculo a
mano hecho aquí con aritmética independiente (no importa el código del motor).

Uso (lo llama infra/gcp/desplegar.sh): python infra/gcp/llamadas_reales.py URL_REVISION
Lee el JWT de Supabase de la variable TOKEN_PRUEBA (nunca lo imprime). Código de salida 1 si algún motor falla.
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.error
import urllib.request

TOL = 1e-9


def _post(url: str, ruta: str, cuerpo: dict, token: str) -> dict:
    req = urllib.request.Request(url.rstrip("/") + ruta, data=json.dumps(cuerpo).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise AssertionError(f"HTTP {e.code}: {e.read()[:300]!r}") from None


def _cerca(obtenido: float, esperado: float, nombre: str) -> None:
    assert abs(obtenido - esperado) <= TOL * max(1.0, abs(esperado)), f"{nombre}: {obtenido} ≠ {esperado}"


def redes(url: str, token: str) -> str:
    # Un tramo de 1 km, D=0,3 m, C=130, Q=0,1 m³/s desde un embalse a 100 m: pérdida de Hazen-Williams.
    j = _post(url, "/redes/permanente", {
        "nodos": [{"id": "R", "cota_m": 50.0, "carga_fija_m": 100.0}, {"id": "N", "cota_m": 40.0, "demanda_m3s": 0.1}],
        "tramos": [{"id": "p", "desde": "R", "hasta": "N", "longitud_m": 1000.0, "diametro_m": 0.3, "c_hw": 130.0}]}, token)
    h = 10.67 * 1000 / (130 ** 1.852 * 0.3 ** 4.871) * 0.1 ** 1.852
    _cerca(j["valor"]["nodos"]["N"]["carga_m"], 100 - h, "carga en N")
    return f"carga en N = {100 - h:.6f} m (Hazen-Williams)"


def geotecnia(url: str, token: str) -> str:
    # Zapata 2×3 m, q=150 kPa, método 2:1; arcilla normalmente consolidada de 4 m con centro a 4 m.
    estrato = dict(espesor_m=4.0, z_medio_m=4.0, sigma0_kpa=100.0, sigma_p_kpa=100.0, cc=0.3, cr=0.03, e0=1.0,
                   cv_m2_dia=0.002, hdr_m=2.0)
    j = _post(url, "/geotecnia/asentamiento", dict(q_kpa=150.0, B_m=2.0, L_m=3.0, estratos=[estrato], metodo="2a1",
                                                    tipo_cimentacion="aislada"), token)
    delta = 150.0 * 2.0 * 3.0 / ((2.0 + 4.0) * (3.0 + 4.0))
    s_mm = 0.3 * 4.0 / (1.0 + 1.0) * math.log10((100.0 + delta) / 100.0) * 1000.0
    _cerca(j["valor"]["estratos"][0]["delta_sigma_kpa"], delta, "Δσ 2:1")
    _cerca(j["valor"]["asentamiento_total_mm"], s_mm, "asentamiento")
    return f"Δσ = {delta:.4f} kPa, S = {s_mm:.4f} mm (Terzaghi, NC)"


def licuacion(url: str, token: str) -> str:
    # Perfil de 10 m, NF a 2 m, (N1)60=15, FC=3 %, amax=0,3 g, Mw=7,5. Primera subcapa (centro a 2,5 m).
    estrato = dict(z_top_m=0.0, z_base_m=10.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, n1_60=15.0, finos_pct=3.0,
                   no_plastico=True)
    j = _post(url, "/licuacion/spt", dict(amax_g=0.3, mw=7.5, nivel_freatico_m=2.0, estratos=[estrato]), token)
    c = j["valor"]["estratos"][0]["subcapas"][0]
    sv, sve, rd = 46.0, 46.0 - 9.81 * 0.5, 1.0 - 0.00765 * 2.5
    csr = 0.65 * 0.3 * sv / sve * rd                                   # Seed e Idriss
    crr = 1 / 19 + 15 / 135 + 50 / 195 ** 2 - 1 / 200                  # Youd et al. (2001), arena limpia
    fs = crr * (10 ** 2.24 / 7.5 ** 2.56) / csr                         # MSF de Idriss
    for k, v in (("csr", csr), ("crr", crr), ("fs", fs)):
        _cerca(c[k], v, k)
    return f"CSR = {csr:.6f}, CRR = {crr:.6f}, FS = {fs:.6f} (Youd et al. 2001)"


MOTORES = {"redes": redes, "geotecnia": geotecnia, "licuacion": licuacion}


def main() -> int:
    url, token = sys.argv[1], os.environ.get("TOKEN_PRUEBA", "")
    if not token:
        print("  AVISO: sin TOKEN_PRUEBA no se hicieron llamadas reales; la condición 4 NO queda verificada.")
        return 0
    fallos = 0
    for nombre, f in MOTORES.items():
        try:
            print(f"  llamada real {nombre}: correcta contra el cálculo a mano · {f(url, token)}")
        except Exception as e:  # noqa: BLE001
            fallos += 1
            print(f"  X llamada real {nombre}: {e}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
