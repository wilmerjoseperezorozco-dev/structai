"""Inventario de series anuales de caudal extremo del IDEAM (largo de registro y cobertura por departamento)."""
import csv
import glob
import os
import sys
import collections
import unicodedata

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _datos_caribe as dc  # noqa: E402

sb = dc._sb()
est, ini = {}, 0
while True:
    p = sb.table("ideam_estaciones_caudal").select("codigo,departamento,latitud,longitud").range(ini, ini + 999).execute().data or []
    for e in p:
        est[e["codigo"]] = e
    if len(p) < 1000:
        break
    ini += 1000


def serie(f):
    out = {}
    for r in csv.DictReader(open(f, encoding="utf-8")):
        try:
            out[int(r["fechaObservacion"][:4])] = float(r["valorObservado"])
        except (ValueError, KeyError):
            pass
    return out


norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper()
CARIBE = {"ATLANTICO", "MAGDALENA", "BOLIVAR", "CORDOBA", "SUCRE", "CESAR", "LA GUAJIRA"}
for v in ("Q_MX_A", "Q_MN_A"):
    S = {os.path.basename(f).split("-")[0]: serie(f) for f in glob.glob(os.path.join("_cache", "ideam", v, "*.csv"))}
    n = np.array([len(s) for s in S.values()])
    print(f"{v}: {len(S)} estaciones | anios (mediana) {int(np.median(n))} | >=10: {(n >= 10).sum()}  >=20: {(n >= 20).sum()}  >=30: {(n >= 30).sum()}  >=40: {(n >= 40).sum()}")
    ult = [max(s) for s in S.values() if s]
    print(f"   ultimo anio (mediana) {int(np.median(ult))}; con dato >= 2020: {sum(u >= 2020 for u in ult)}")
    reg = collections.Counter(norm(est[c]["departamento"]) for c, s in S.items() if len(s) >= 20 and c in est)
    print("   >=20 anios por departamento:", reg.most_common(14), "| sin ubicacion:", sum(1 for c, s in S.items() if len(s) >= 20 and c not in est))
    print("   Caribe con >=20 anios:", sum(1 for c, s in S.items() if len(s) >= 20 and c in est and norm(est[c]["departamento"]) in CARIBE))
    print("   valores <= 0:", sum(1 for s in S.values() for x in s.values() if x <= 0))
