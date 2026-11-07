"""Descarga los anexos mensuales del ICOCIV (DANE) a _cache/icociv/. Reanudable; ritmo moderado (pausa entre archivos).
Solo se bajan los anexos .xlsx/.xls de la página histórica; ~19 MB cada uno. Uso: python bajar_icociv.py"""
from __future__ import annotations

import io
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
DEST = AQUI / "_cache" / "icociv"
PAGINA = "https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-costos-de-la-construccion-de-obras-civiles-icociv/indice-de-costos-de-la-construccion-de-obras-civiles-icociv-informacion-historica"
UA = {"User-Agent": "Mozilla/5.0 structai-research"}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    h = urllib.request.urlopen(urllib.request.Request(PAGINA, headers=UA), timeout=60).read().decode("utf-8", "replace")
    enl = sorted(set(re.findall(r'href="([^"]+anexos?-icociv[^"]+\.xlsx?)"', h, re.I)))
    print(f"Anexos encontrados: {len(enl)}", flush=True)
    for k, e in enumerate(enl):
        nombre = e.rsplit("/", 1)[-1]; f = DEST / nombre
        if f.exists() and f.stat().st_size > 100_000:
            continue
        url = urllib.parse.urljoin("https://www.dane.gov.co", e)
        for intento in range(4):
            try:
                datos = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()
                f.write_bytes(datos)
                print(f"  {k + 1}/{len(enl)} {nombre} ({len(datos) / 1e6:.1f} MB)", flush=True)
                break
            except Exception as ex:
                print(f"  {nombre}: {str(ex)[:60]}; reintento {intento + 1}", flush=True)
                time.sleep(15 * (intento + 1))
        time.sleep(2)
    print("listo", flush=True)


if __name__ == "__main__":
    main()
