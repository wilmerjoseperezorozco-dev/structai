"""Auditoría de unión SINPAD - polígonos (OCHA COD-AB, IGN) - población proyectada (INEI), issue #110.

Uso: python -I peru_auditoria_union.py <sinpad.csv> <per_admin_boundaries.xlsx> <inei_pob_proy.xlsx>
Solo lectura; no calcula ninguna asociación. Es parte de la compuerta de datos del protocolo V1-Perú.
"""
from __future__ import annotations

import sys

import pandas as pd

AÑOS = [str(y) for y in range(2019, 2025)]


def main(sinpad: str, limites: str, poblacion: str) -> None:
    pol = pd.read_excel(limites, sheet_name="per_admin3")
    poly = set(pol["adm3_pcode"].astype(str).str.replace("PE", "", regex=False).str.zfill(6))
    p = pd.read_excel(poblacion, header=None, skiprows=5).rename(columns={0: "ubigeo"})
    p["ubigeo"] = p["ubigeo"].astype(str).str.strip()
    dist = p[p.ubigeo.str.fullmatch(r"\d{6}") & ~p.ubigeo.str.endswith("00")]
    ine = set(dist.ubigeo)
    s = pd.read_csv(sinpad, encoding="latin-1", sep=";", dtype=str)
    s.columns = [c.strip() for c in s.columns]
    s = s.rename(columns={s.columns[2]: "ANO"})
    v = s[s.ANO.isin(AÑOS)]
    sd = set(v["COD. DISTRITO"])
    sin = v[~v["COD. DISTRITO"].isin(poly)]
    print(f"polígonos: {len(poly)} | INEI distritos: {len(ine)} | SINPAD 2019-2024: {len(sd)}")
    print(f"SINPAD en polígonos: {len(sd & poly)} | en INEI: {len(sd & ine)} | en ambos: {len(sd & poly & ine)}")
    print(f"registros en distritos sin polígono: {len(sin)} de {len(v)} ({len(sin)/len(v):.2%}); distritos: {sin['COD. DISTRITO'].nunique()}")
    print(f"polígonos sin población INEI: {len(poly - ine)} | INEI sin polígono: {len(ine - poly)}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
