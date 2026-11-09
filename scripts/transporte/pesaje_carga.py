"""Calibración de la flota de carga con registros de pesaje (Supertransporte, datos.gov.co `atkg-vhpp`, 10,9 millones de registros).

Todo se agrega en el servidor (SoQL) y se cachea; no se descargan registros individuales (la placa viene anonimizada y no se usa).
Qué se obtiene:
- Por configuración (C2, C3, 2S2, 2S3, 3S2, 3S3): n, peso bruto medio, peso máximo modal y su razón con el PBV de la Res. 20223040045295/2022, tasa de exceso.
- Histograma del peso bruto (bins de 2 t; para C2 por subclase de peso máximo) para ubicar el modo VACÍO y el modo CARGADO, y estimar la carga útil como su diferencia.
- Calidad de los datos y cobertura temporal; estaciones con mayor tasa de exceso.
Límites: las básculas son puntos de control en corredores, no una muestra aleatoria de la flota (los vehículos cargados pueden estar sobrerrepresentados); no hay tara ni
carga declarada, por eso la carga útil sale de la diferencia entre modos; no hay ubicación de estaciones; el exceso se define como peso registrado > peso máximo del registro.
Salida: data/transporte/pesaje_carga_resumen.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://www.datos.gov.co/resource/atkg-vhpp.json?"
SALIDA = base.RAIZ / "data" / "transporte" / "pesaje_carga_resumen.json"
CONFIGS = ("C2", "C3", "2S2", "2S3", "3S2", "3S3")
PBV_RES_2022 = {"C2": 17_000, "C3": 28_000, "2S2": 32_000, "2S3": 40_500, "3S2": 48_000, "3S3": 52_000}   # = flota_construccion.PBV_KG
SUBCLASES_C2 = (5_500, 10_500, 11_500, 13_500, 17_500)
BIN_KG = 2_000


def consulta(**params) -> list[dict]:
    url = URL + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    destino = base.CACHE / f"pesaje_{hashlib.md5(url.encode()).hexdigest()[:12]}.json"
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=400) as r:  # noqa: S310 - URL fija de datos abiertos
            destino.write_bytes(r.read())
    return json.loads(destino.read_text(encoding="utf-8"))


def resumen_config() -> dict:
    filas = consulta(**{"$select": "categoria_vehiculo,count(*) as n,avg(peso_registrado_en_bascula) as peso,avg(peso_maximo_vehicular) as maximo,"
                                   "sum(case(peso_registrado_en_bascula>peso_maximo_vehicular,1,true,0)) as sobre0,"
                                   "sum(case(peso_registrado_en_bascula>1.05*peso_maximo_vehicular,1,true,0)) as sobre5,"
                                   "sum(case(peso_registrado_en_bascula>2*peso_maximo_vehicular,1,true,0)) as doble",
                         "$where": "peso_registrado_en_bascula>0 AND peso_maximo_vehicular>0", "$group": "categoria_vehiculo", "$order": "n desc", "$limit": "30"})
    return {r["categoria_vehiculo"]: {"n": int(r["n"]), "peso_medio_kg": float(r["peso"]), "maximo_medio_kg": float(r["maximo"]), "exceso_pct": 100 * int(r["sobre0"]) / int(r["n"]),
                                      "exceso_5pct_pct": 100 * int(r["sobre5"]) / int(r["n"]), "mas_del_doble_pct": 100 * int(r["doble"]) / int(r["n"])} for r in filas}


def maximo_modal(config: str) -> tuple[float, int]:
    f = consulta(**{"$select": "peso_maximo_vehicular as m,count(*) as n", "$where": f"categoria_vehiculo='{config}'", "$group": "m", "$order": "n desc", "$limit": "1"})
    return float(f[0]["m"]), int(f[0]["n"])


def histograma(config: str, maximo: int | None = None) -> dict[int, int]:
    cond = f"categoria_vehiculo='{config}' AND peso_registrado_en_bascula>0"
    if maximo is not None:
        cond += f" AND peso_maximo_vehicular={maximo}"
    f = consulta(**{"$select": f"floor(peso_registrado_en_bascula/{BIN_KG}) as b,count(*) as n", "$where": cond, "$group": "b", "$order": "b", "$limit": "200"})
    return {int(r["b"]) * BIN_KG: int(r["n"]) for r in f}


def modos(h: dict[int, int], maximo: float) -> dict:
    """Modo de la mitad inferior (vacío) y de la superior (cargado) respecto del peso máximo; carga útil estimada = diferencia (centros de bin)."""
    inf = {b: n for b, n in h.items() if b + BIN_KG / 2 < 0.5 * maximo}
    sup = {b: n for b, n in h.items() if b + BIN_KG / 2 >= 0.5 * maximo}
    if not inf or not sup:
        return {}
    v, c = max(inf, key=inf.get) + BIN_KG / 2, max(sup, key=sup.get) + BIN_KG / 2
    tot = sum(h.values())
    return {"modo_vacio_kg": v, "modo_cargado_kg": c, "carga_util_modal_kg": c - v, "pct_mitad_inferior": 100 * sum(inf.values()) / tot,
            "pct_en_pico_cargado": 100 * sum(n for b, n in sup.items() if abs(b + BIN_KG / 2 - c) <= BIN_KG) / tot}


def calidad_y_cobertura() -> dict:
    q = consulta(**{"$select": "sum(case(peso_registrado_en_bascula<=0,1,true,0)) as peso0,sum(case(peso_maximo_vehicular<=0,1,true,0)) as max0,count(*) as n,count(distinct estaci_n) as est"})[0]
    dias = consulta(**{"$select": "fecha,count(*) as n", "$group": "fecha", "$limit": "5000"})
    anios: dict[str, int] = defaultdict(int)
    for r in dias:
        f = r["fecha"]
        anios[f[-4:] if len(f) >= 8 and f[-4:].isdigit() else "fecha no interpretable"] += int(r["n"])
    return {"n": int(q["n"]), "peso_cero": int(q["peso0"]), "maximo_cero": int(q["max0"]), "estaciones": int(q["est"]), "registros_por_anio": dict(sorted(anios.items()))}


def estaciones_exceso(min_n: int = 20_000) -> list[dict]:
    f = consulta(**{"$select": "estaci_n,count(*) as n,sum(case(peso_registrado_en_bascula>peso_maximo_vehicular,1,true,0)) as s",
                    "$where": "peso_registrado_en_bascula>0 AND peso_maximo_vehicular>0", "$group": "estaci_n", "$limit": "500"})
    out = [{"estacion": r["estaci_n"], "n": int(r["n"]), "exceso_pct": 100 * int(r["s"]) / int(r["n"])} for r in f if int(r["n"]) >= min_n]
    return sorted(out, key=lambda x: -x["exceso_pct"])


if __name__ == "__main__":
    res: dict = {"calidad": calidad_y_cobertura(), "configuraciones": {}, "c2_subclases": {}}
    print("calidad/cobertura:", {k: v for k, v in res["calidad"].items() if k != "registros_por_anio"}, "\nregistros por año:", res["calidad"]["registros_por_anio"])
    rc = resumen_config()
    print(f"\n{'config':6s}{'n':>10s}{'peso medio':>12s}{'máx modal':>11s}{'/PBV res':>9s}{'exceso':>8s}{'>5 %':>7s}{'vacío':>8s}{'cargado':>9s}{'carga útil':>11s}{'%inf':>6s}")
    for c in CONFIGS:
        m, nm = maximo_modal(c)
        mo = modos(histograma(c), m)
        res["configuraciones"][c] = {**rc[c], "maximo_modal_kg": m, "razon_maximo_modal_pbv": m / PBV_RES_2022[c], "n_modal": nm, **mo}
        print(f"{c:6s}{rc[c]['n']:10d}{rc[c]['peso_medio_kg']:12.0f}{m:11.0f}{m / PBV_RES_2022[c]:9.3f}{rc[c]['exceso_pct']:7.2f}%{rc[c]['exceso_5pct_pct']:6.2f}%"
              f"{mo.get('modo_vacio_kg', float('nan')):8.0f}{mo.get('modo_cargado_kg', float('nan')):9.0f}{mo.get('carga_util_modal_kg', float('nan')):11.0f}{mo.get('pct_mitad_inferior', float('nan')):6.0f}")
    print("\nC2 por subclase de peso máximo:")
    for mx in SUBCLASES_C2:
        h = histograma("C2", mx)
        mo = modos(h, mx)
        n = sum(h.values())
        res["c2_subclases"][str(mx)] = {"n": n, **mo}
        print(f"  máx {mx:6d}: n={n:8d}", {k: round(v) for k, v in mo.items()})
    res["estaciones_mayor_exceso"] = estaciones_exceso()[:10]
    print("\nestaciones con mayor exceso (>= 20 mil registros):", [(e["estacion"], round(e["exceso_pct"], 1)) for e in res["estaciones_mayor_exceso"]])
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
