"""Promedio mensual por estación de la temperatura máxima y mínima horaria del aire (IDEAM, datos.gov.co) para los departamentos del Caribe, agregado en el servidor
(los conjuntos tienen ~28 millones de registros cada uno). También descarga el índice TNA (temperatura del Atlántico norte tropical, NOAA PSL).
Uso: python extraer_temperatura_caribe.py   Salida: _cache/temperatura_caribe_{max,min}.json y _cache/tna.data"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
DEPTOS = ["ATLANTICO", "ATLÁNTICO", "BOLIVAR", "BOLÍVAR", "CESAR", "CORDOBA", "CÓRDOBA", "LA GUAJIRA", "MAGDALENA", "SUCRE"]
CONJUNTOS = {"max": "ccvq-rp9s", "min": "afdg-3zpb"}
PAGINA = 50000
UA = {"User-Agent": "structai-research/1.0"}


def get(url: str, params: dict | None = None, reintentos: int = 4) -> bytes:
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for k in range(reintentos):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=170).read()
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {k + 1}: {str(e)[:70]}", flush=True)
            time.sleep(10 * (k + 1))
    raise RuntimeError(f"no se pudo descargar {url[:80]}")


def main() -> None:
    CACHE.mkdir(exist_ok=True)
    tna = CACHE / "tna.data"
    if not tna.exists():
        tna.write_bytes(get("https://psl.noaa.gov/data/correlation/tna.data")); print("TNA descargado", flush=True)
    lista = ",".join(f"'{d}'" for d in DEPTOS)
    for clave, ident in CONJUNTOS.items():
        sal = CACHE / f"temperatura_caribe_{clave}.json"
        if sal.exists():
            print(f"{sal.name} ya existe", flush=True); continue
        filas, off = [], 0
        while True:
            p = {"$select": "nombreestacion,departamento,municipio,latitud,longitud,date_trunc_ym(fechaobservacion) as mes,avg(valorobservado) as t,count(*) as n",
                 "$where": f"departamento in({lista}) and valorobservado between -5 and 50",
                 "$group": "nombreestacion,departamento,municipio,latitud,longitud,mes", "$order": "mes,nombreestacion", "$limit": str(PAGINA), "$offset": str(off)}
            lote = json.loads(get(f"https://www.datos.gov.co/resource/{ident}.json", p))
            filas += lote; print(f"  {clave}: {len(filas)} filas estación-mes", flush=True)
            if len(lote) < PAGINA:
                break
            off += PAGINA
        sal.write_text(json.dumps(filas), encoding="utf-8"); print(f"{sal.name}: {len(filas)} filas", flush=True)


if __name__ == "__main__":
    main()
