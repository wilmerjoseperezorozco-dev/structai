"""Genera packages/motor-geopot/data/nsr10_a4_municipios.json: Aa/Av/Ae/Ad por municipio (Apéndice A-4 NSR-10)
para que los motores lo consulten sin conexión. Mismo contenido que la tabla nsr10_apendice_a4_municipios de Supabase:
texto original 2010 (apendice_a4_extraido.json) + las 29 modificaciones del Decreto 092 de 2011 (a4_en_decretos.json).
Vigencia: posteriores al Decreto 092 de 2011 sin verificar (Supía/Decreto 1711 de 2021 y Guamal sin resolver).

Uso: python generar_snapshot_a4.py
"""
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parents[2] / "packages" / "motor-geopot" / "data" / "nsr10_a4_municipios.json"
CAMPOS = ("aa", "av", "ae", "ad", "zona")
DECRETO = "Decreto 092 de 2011 (anexo técnico, págs. 9-11)"


def main() -> None:
    filas: dict[str, dict] = {}
    for f in json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8")):
        filas[f["codigo"]] = {"codigo": f["codigo"], "municipio": f["municipio"], "departamento": f["departamento"],
                              **{k: f[k] for k in CAMPOS}, "modificado_por": None}
    d092 = json.loads((AQUI / "a4_en_decretos.json").read_text(encoding="utf-8"))["d092_anexo.pdf"]
    for codigo, f in d092.items():
        fila = filas.get(codigo)
        if fila is None or all(fila[k] == f[k] for k in CAMPOS):
            continue
        fila.update({k: f[k] for k in CAMPOS}, modificado_por=DECRETO)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "fuente": "NSR-10 Apéndice A-4 (Decreto 926 de 2010) con modificaciones del Decreto 092 de 2011",
        "vigencia": "Posteriores al Decreto 092 de 2011 sin verificar; Supía (Decreto 1711/2021) y Guamal sin resolver",
        "municipios": sorted(filas.values(), key=lambda x: x["codigo"]),
    }
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=0), encoding="utf-8")
    mod = sum(1 for x in filas.values() if x["modificado_por"])
    print(f"{len(filas)} municipios ({mod} modificados por el Decreto 092/2011) -> {SALIDA}")


if __name__ == "__main__":
    main()
