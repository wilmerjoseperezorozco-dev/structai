"""Descarga de series anuales de caudal maximo (Q_MX_A) y minimo (Q_MN_A) del almacen abierto del IDEAM
(datos.ideam.gov.co/s3-estacionesideam, observaciones/historicos/csv/). Un CSV por estacion, reanudable.
Uso: python bajar_ideam_extremos.py [Q_MX_A Q_MN_A ...]"""
from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

B = "https://datos.ideam.gov.co/s3-estacionesideam"
DEST = Path(__file__).resolve().parent / "_cache" / "ideam"


def listar(prefijo: str) -> list[str]:
    claves, tok = [], None
    while True:
        q = {"list-type": 2, "prefix": prefijo, "max-keys": 1000}
        if tok:
            q["continuation-token"] = tok
        x = urllib.request.urlopen(f"{B}?{urllib.parse.urlencode(q)}", timeout=90).read().decode()
        claves += re.findall(r"<Key>([^<]+\.csv)</Key>", x)
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", x)
        if "<IsTruncated>true" not in x or not m:
            return claves
        tok = m.group(1)


def bajar(clave: str) -> bool:
    f = DEST / clave.split("/")[-2] / clave.split("/")[-1]
    if f.exists():
        return True
    for i in range(5):
        try:
            datos = urllib.request.urlopen(f"{B}/{clave}", timeout=60).read()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(datos)
            return True
        except Exception:
            time.sleep(2 ** i)
    return False


def main() -> None:
    for v in (sys.argv[1:] or ["Q_MX_A", "Q_MN_A"]):
        claves = listar(f"observaciones/historicos/csv/{v}/")
        print(f"{v}: {len(claves)} estaciones", flush=True)
        with ThreadPoolExecutor(4) as ex:
            ok = sum(ex.map(bajar, claves))
        print(f"{v}: descargadas {ok}/{len(claves)}", flush=True)


if __name__ == "__main__":
    main()
