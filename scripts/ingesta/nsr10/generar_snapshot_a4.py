"""Genera packages/motor-geopot/data/nsr10_a4_municipios.json: Aa/Av/Ae/Ad por municipio (Apéndice A-4 NSR-10)
para que los motores lo consulten sin conexión. Mismo contenido que la tabla nsr10_apendice_a4_municipios de Supabase:
texto original 2010 (apendice_a4_extraido.json) + las 29 modificaciones del Decreto 092 de 2011 (a4_en_decretos.json)
+ Supía por el Decreto 1711 de 2021 (#189; anexo técnico verificado en el PDF oficial, el mismo valor que ya tiene la tabla).
Vigencia: Guamal sigue sin resolver; los demás decretos con anexo (340/2012, 945/2017, 1401/2023) no cambian el A-4 según
a4_en_decretos.json, pero la auditoría completa del anexo contra el corpus sigue pendiente en #189.

Uso: python generar_snapshot_a4.py
"""
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parents[2] / "packages" / "motor-geopot" / "data" / "nsr10_a4_municipios.json"
CAMPOS = ("aa", "av", "ae", "ad", "zona")
DECRETO = "Decreto 092 de 2011 (anexo técnico, págs. 9-11)"
# Decreto 1711 de 2021, anexo técnico, pág. 4 del PDF oficial de MinVivienda (verificado el 2026-11-11, issue #189).
# Mismo valor y texto que aplicó scripts/ingesta/nsr10/_actualizar_a4_con_decreto_1711.py en la tabla de Supabase.
DECRETO_1711 = "Decreto 1711 de 2021 (anexo técnico, pág. 4 del PDF oficial de MinVivienda)"
MODIFICACIONES_1711 = {"17777": {"aa": 0.25, "av": 0.30, "ae": 0.20, "ad": 0.10, "zona": "Alta"}}


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
    for codigo, f in MODIFICACIONES_1711.items():                    # posterior al 092: prevalece
        if codigo not in filas:
            raise ValueError(f"El Decreto 1711 de 2021 modifica {codigo}, que no está en el Apéndice A-4 extraído")
        filas[codigo].update(f, modificado_por=DECRETO_1711)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "fuente": "NSR-10 Apéndice A-4 (Decreto 926 de 2010) con modificaciones de los Decretos 092 de 2011 y 1711 de 2021",
        "vigencia": "Decretos 092/2011 y 1711/2021 aplicados; Guamal sin resolver; auditoría completa de anexos pendiente (#189)",
        "municipios": sorted(filas.values(), key=lambda x: x["codigo"]),
    }
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=0), encoding="utf-8")
    mod = sum(1 for x in filas.values() if x["modificado_por"])
    print(f"{len(filas)} municipios ({mod} modificados por decretos posteriores a 2010) -> {SALIDA}")


if __name__ == "__main__":
    main()
