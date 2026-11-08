"""Etapa B: seleccion de pluviometros automaticos del IDEAM y totales diarios con control de calidad.
Protocolo: PROTOCOLO_SESGO_CHIRPS.md (fijado antes de descargar). Resumible: cache por estacion en _cache/pluviometros/.
Salida: pluviometros_seleccion.json (estaciones aceptadas por region) y _cache/pluviometros/<codigo>.json (totales diarios).
"""
from __future__ import annotations

import json
import random
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache" / "pluviometros"
CATALOGO = "https://www.datos.gov.co/resource/hp9r-jxuu.json"
DATOS = "https://www.datos.gov.co/resource/s54a-sgyg.json"
F0, F1 = "2022-01-01T00:00:00", "2025-01-01T05:00:00"     # cubre 2022-2024 con margen para la alineacion de +5 h
SEMILLA = 20261108
POR_REGION = 12
MAX_CAND = 120
MIN_DIAS = 300
REGISTROS_DIA, MIN_REG_FRAC, MAX_DIA_MM = 144, 0.90, 600.0
DEPTOS = {
    "Caribe": ["ATLANTICO", "BOLIVAR", "CESAR", "CORDOBA", "LA GUAJIRA", "MAGDALENA", "SUCRE"],
    "Andina": ["ANTIOQUIA", "BOYACA", "CALDAS", "CUNDINAMARCA", "HUILA", "NORTE DE SANTANDER", "QUINDIO", "RISARALDA", "SANTANDER", "TOLIMA"],
    "Pacifica": ["CAUCA", "NARINO", "VALLE DEL CAUCA"],
    "Orinoquia": ["META"],
}
CATEGORIAS = ("Pluviométrica", "Pluviográfica", "Climatológica Principal", "Climatológica Ordinaria")


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").upper().strip()


def candidatas() -> dict[str, list[dict]]:
    r = requests.get(CATALOGO, timeout=120, params={
        "$select": "codigo,nombre,categoria,tecnologia,departamento,municipio,latitud,longitud,altitud",
        "$where": "estado='Activa' and tecnologia like '%Autom%'", "$limit": 20000})
    r.raise_for_status()
    por = {k: [] for k in DEPTOS}
    for e in r.json():
        if e.get("categoria") not in CATEGORIAS or not e.get("latitud"):
            continue
        d = sin_tildes(e.get("departamento", ""))
        for reg, lst in DEPTOS.items():
            if d in lst:
                por[reg].append(e)
    rng = random.Random(SEMILLA)
    for reg in por:
        por[reg].sort(key=lambda e: e["codigo"])
        rng.shuffle(por[reg])
    return por


def bajar(codigo: str) -> pd.DataFrame:
    filas, off = [], 0
    while True:
        for intento in range(5):
            try:
                r = requests.get(DATOS, timeout=180, params={
                    "$select": "fechaobservacion,valorobservado,codigosensor",
                    "$where": f"codigoestacion='{codigo}' and fechaobservacion between '{F0}' and '{F1}'",
                    "$order": ":id", "$limit": 50000, "$offset": off})
                r.raise_for_status()
                break
            except Exception as ex:
                time.sleep(15 * (intento + 1))
        else:
            raise RuntimeError(f"no se pudo descargar {codigo}")
        lote = r.json()
        filas += lote
        if len(lote) < 50000:
            break
        off += 50000
    d = pd.DataFrame(filas)
    if d.empty:
        return d
    d["t"] = pd.to_datetime(d["fechaobservacion"], errors="coerce")
    d["v"] = pd.to_numeric(d["valorobservado"], errors="coerce")
    return d.dropna(subset=["t", "v"])


def totales_diarios(d: pd.DataFrame, desplazamiento_h: int) -> pd.DataFrame:
    sensor = d["codigosensor"].value_counts().idxmax()
    x = d[d["codigosensor"] == sensor].drop_duplicates(subset="t").copy()
    x["dia"] = (x["t"] + pd.Timedelta(hours=desplazamiento_h)).dt.date
    g = x.groupby("dia").agg(n=("v", "size"), suma=("v", "sum"), minimo=("v", "min"))
    g["valido"] = (g["n"] >= REGISTROS_DIA * MIN_REG_FRAC) & (g["minimo"] >= 0) & (g["suma"] <= MAX_DIA_MM)
    g = g[(pd.to_datetime(g.index) >= "2022-01-01") & (pd.to_datetime(g.index) <= "2024-12-31")]
    g["sensor"] = sensor
    return g


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    cand = candidatas()
    sel = {}
    for reg, lista in cand.items():
        sel[reg] = []
        vistas = 0
        print(f"{reg}: {len(lista)} candidatas", flush=True)
        for e in lista[:MAX_CAND]:
            if len(sel[reg]) >= POR_REGION:
                break
            vistas += 1
            f = CACHE / f"{e['codigo']}.json"
            if f.exists():
                res = json.loads(f.read_text(encoding="utf-8"))
            else:
                t0 = time.time()
                d = bajar(e["codigo"])
                if d.empty:
                    res = {"codigo": e["codigo"], "dias_validos": 0, "diario": {}}
                else:
                    por = {h: totales_diarios(d, h) for h in (0, 5)}
                    res = {"codigo": e["codigo"], "dias_validos": int(por[0]["valido"].sum()), "sensor": str(por[0]["sensor"].iloc[0]) if len(por[0]) else None,
                           "diario": {str(h): {str(k): [float(v.suma), int(v.valido)] for k, v in por[h].iterrows()} for h in (0, 5)}}
                f.write_text(json.dumps(res), encoding="utf-8")
                print(f"  {e['codigo']} {e['departamento']:<18} dias validos {res['dias_validos']:>4} ({time.time() - t0:.0f}s)", flush=True)
            if res["dias_validos"] >= MIN_DIAS:
                sel[reg].append({k: e[k] for k in ("codigo", "nombre", "categoria", "departamento", "municipio", "latitud", "longitud", "altitud")} | {"dias_validos": res["dias_validos"]})
        print(f"  {reg}: aceptadas {len(sel[reg])} de {vistas} recorridas", flush=True)
    (AQUI / "pluviometros_seleccion.json").write_text(json.dumps(sel, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in sel.items()})


if __name__ == "__main__":
    main()
