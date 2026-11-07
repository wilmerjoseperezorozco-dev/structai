"""Extrae series mensuales de XM (API publica, sin token) para la hipotesis 13 (El Nino y la energia).

Metricas diarias (Entity "Sistema"), una consulta por mes y metrica (maximo 31 dias por consulta):
  PPPrecBolsNaci   precio de bolsa nacional ponderado (COP/kWh)
  AporEner         aportes hidricos de energia (kWh/dia)
  AporEnerMediHist media historica de aportes (kWh/dia)
  PorcVoluUtilDiar volumen util de embalses (fraccion)
Reanudable: cada (metrica, mes) se guarda en scripts/macro/_cache/xm/. Solo extrae y agrega a nivel mensual.
Salida: scripts/macro/xm_energia_mensual.csv
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.request
from calendar import monthrange
from pathlib import Path

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache" / "xm"
URL = "https://servapibi.xm.com.co/daily"
UA = {"User-Agent": "structai-research/0.1", "Content-Type": "application/json"}
METRICAS = ["PPPrecBolsNaci", "AporEner", "AporEnerMediHist", "PorcVoluUtilDiar"]


def consultar(metrica: str, a: int, m: int) -> list[float]:
    f = CACHE / f"{metrica}_{a}-{m:02d}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    ini, fin = f"{a}-{m:02d}-01", f"{a}-{m:02d}-{monthrange(a, m)[1]:02d}"
    body = json.dumps({"MetricId": metrica, "StartDate": ini, "EndDate": fin, "Entity": "Sistema", "Filter": []}).encode()
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, data=body, headers=UA, method="POST"), timeout=120) as r:
                d = json.load(r)
            v = [float(e["Value"]) for it in d.get("Items", []) for e in it.get("DailyEntities", []) if e.get("Value") not in (None, "")]
            f.write_text(json.dumps(v), encoding="utf-8")
            return v
        except Exception as e:
            print(f"  reintento {intento + 1} {metrica} {a}-{m:02d} ({type(e).__name__})", flush=True)
            time.sleep(3 * (intento + 1))
    raise RuntimeError(f"fallo persistente {metrica} {a}-{m:02d}")


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    meses = [(a, m) for a in range(2000, 2027) for m in range(1, 13) if (a, m) <= (2026, 10)]
    filas = []
    t0 = time.time()
    for k, (a, m) in enumerate(meses):
        fila = {"fecha": pd.Timestamp(year=a, month=m, day=1)}
        for met in METRICAS:
            v = consultar(met, a, m)
            fila[met] = sum(v) / len(v) if v else None
            fila[f"{met}_n"] = len(v)
            time.sleep(0.05)
        filas.append(fila)
        if k % 24 == 23:
            print(f"  {a}-{m:02d} listo ({time.time() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(filas)
    df.to_csv(AQUI / "xm_energia_mensual.csv", index=False)
    print(f"\n{len(df)} meses; faltantes por metrica:", {m: int(df[m].isna().sum()) for m in METRICAS}, flush=True)
    print("LISTO", flush=True)


if __name__ == "__main__":
    main()
