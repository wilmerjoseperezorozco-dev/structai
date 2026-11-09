"""Cierre de confusores del cruce 3: seguridad, capacidad institucional, amenazas hidrometeorológicas e inversión en transporte (SGR).

Covariables departamentales (todas de datos.gov.co, agregadas con SoQL; se cachean en data/transporte/_cache/):
- homicidios (Policía Nacional, m8fd-ahd9), 2016-2025, tasa por 100 mil personas de 5-16 años. OJO: la población 5-16 (MEN, ji8i-4anb) es solo un PROXY de la escala
  poblacional; no hay población total por departamento cargada. Sirve para comparar tasas entre departamentos solo si 5-16 ~ proporcional a la población total.
- desempeño institucional (MIPG/FURAG de alcaldías, gfs5-jqxi): promedio por departamento del índice de desempeño de las alcaldías.
- amenazas hidrometeorológicas (UNGRD, wwkg-r6te; el recurso cubre solo 2019-2022): emergencias por inundación, deslizamiento, avenida torrencial, creciente,
  vendaval o movimiento en masa por 100 mil personas de 5-16 años.
- inversión SGR en transporte (DNP, mzgh-shtp): log del valor total de proyectos del sector Transporte.
Método: igual que cruces_covariables.py (etapa 1 logit con efectos fijos de departamento, etapa 2 regresión ponderada). Cada covariable se añade sobre M1 (pesados + log PIB)
de a una y luego en un modelo conjunto; con 21 departamentos el modelo conjunto deja pocos grados de libertad y se lee con cautela.
Salida: data/transporte/cruces_seguridad_institucional.json.
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
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_covariables as cov  # noqa: E402
import cruces_peajes_secop as base  # noqa: E402
import cruces_secop_logistica as logi  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
BASE_URL = "https://www.datos.gov.co/resource/{}.json?"
SALIDA = base.RAIZ / "data" / "transporte" / "cruces_seguridad_institucional.json"
EVENTOS_HIDRO = ("INUNDACION", "DESLIZAMIENTO", "AVENIDA TORRENCIAL", "CRECIENTE", "VENDAVAL", "MOVIMIENTO EN MASA")


def soql(recurso: str, **params) -> list[dict]:
    url = BASE_URL.format(recurso) + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    destino = base.CACHE / f"soql_{recurso}_{hashlib.md5(url.encode()).hexdigest()[:10]}.json"
    return json.loads(base.descargar(url, destino).read_text(encoding="utf-8"))


def por_codigo(filas: list[dict], clave_cod: str, clave_val: str) -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for r in filas:
        d = cov.DIVIPOLA.get(int(float(r[clave_cod])))
        if d:
            out[d] += float(r[clave_val])
    return out


def poblacion_proxy() -> dict[str, float]:
    filas = soql("ji8i-4anb", **{"$select": "c_digo_departamento,ano,poblacion_5_16", "$where": "ano>='2016' AND ano<='2022'", "$limit": 5000})
    por: dict[tuple[str, str], float] = defaultdict(float)
    for r in filas:
        d = cov.DIVIPOLA.get(int(float(r["c_digo_departamento"])))
        if d:
            por[(d, r["ano"])] += float(r["poblacion_5_16"])
    acum: dict[str, list[float]] = defaultdict(list)
    for (d, _), v in por.items():
        acum[d].append(v)
    return {d: float(np.mean(v)) for d, v in acum.items()}


def homicidios() -> dict[str, float]:
    filas = soql("m8fd-ahd9", **{"$select": "cod_depto,sum(cantidad) as n", "$where": "fecha_hecho>='2016-01-01' AND fecha_hecho<'2026-01-01'", "$group": "cod_depto", "$limit": 100})
    return por_codigo(filas, "cod_depto", "n")


def desempeno_institucional() -> dict[str, float]:
    filas = soql("gfs5-jqxi", **{"$select": "departamento,municipio,ano,indice_de_desempeno", "$where": "sub_orden='MUNICIPAL'", "$limit": 20000})
    por: dict[str, list[float]] = defaultdict(list)
    for r in filas:
        try:
            por[base.norm(r["departamento"])].append(float(r["indice_de_desempeno"]))
        except (KeyError, ValueError):
            continue
    return {d: float(np.mean(v)) for d, v in por.items()}


def emergencias_hidro() -> dict[str, float]:
    cond = " OR ".join(f"upper(evento) like '%{e}%'" for e in EVENTOS_HIDRO)
    filas = soql("wwkg-r6te", **{"$select": "departamento,count(*) as n", "$where": cond, "$group": "departamento", "$limit": 100})
    out: dict[str, float] = defaultdict(float)
    for r in filas:
        out[base.norm(r["departamento"])] += float(r["n"])
    return out


def inversion_sgr_transporte() -> dict[str, float]:
    filas = soql("mzgh-shtp", **{"$select": "nomocad,sum(valortotal) as v", "$where": "sector='TRANSPORTE'", "$group": "nomocad", "$limit": 5000})
    out: dict[str, float] = defaultdict(float)
    for r in filas:
        out[base.norm(r["nomocad"].split(" - ")[0])] += float(r["v"])
    return out


def construir(ds: list[str]) -> dict[str, np.ndarray]:
    pop, hom, ins, emg, sgr = poblacion_proxy(), homicidios(), desempeno_institucional(), emergencias_hidro(), inversion_sgr_transporte()
    for nombre, fuente in (("población", pop), ("homicidios", hom), ("institucional", ins), ("emergencias", emg), ("SGR", sgr)):
        print(f"{nombre:14s} cubre {sum(d in fuente for d in ds)}/{len(ds)} departamentos; faltan: {[d for d in ds if d not in fuente]}")
    return {"homicidios_x100k": np.array([1e5 * hom[d] / pop[d] / 10 for d in ds]),   # anual promedio sobre 10 años
            "desempeno_inst": np.array([ins[d] for d in ds]),
            "emergencias_hidro_x100k": np.array([1e5 * emg.get(d, 0.0) / pop[d] for d in ds]),
            "log_sgr_transporte": np.log10([sgr.get(d, 0.0) + 1.0 for d in ds])}


if __name__ == "__main__":
    mezcla, obras = base.cargar_mezcla(2011), base.cargar_obras()
    ds0 = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    pes0 = {d: float(np.vstack(mezcla[d])[:, 3:].sum() / np.vstack(mezcla[d]).sum()) for d in ds0}
    filas = logi.cargar_contratos(pes0)
    ds = sorted({f["dpto"] for f in filas})
    p = np.array([pes0[d] for d in ds])
    pib = cov.cargar_pib()
    c = construir(ds)
    c["log_pib"] = np.array([pib[d]["log_pib"] for d in ds])
    rho = {k: float(stats.spearmanr(p, v)[0]) for k, v in c.items()}
    print("\nSpearman con pesados:", {k: round(v, 2) for k, v in rho.items()})
    modelos = {"M1 pesados + log PIB": ["log_pib"], "+ seguridad (homicidios)": ["log_pib", "homicidios_x100k"], "+ institucional (MIPG)": ["log_pib", "desempeno_inst"],
               "+ amenazas hidro (UNGRD)": ["log_pib", "emergencias_hidro_x100k"], "+ inversión SGR transporte": ["log_pib", "log_sgr_transporte"],
               "conjunto: PIB + seguridad + institucional + hidro": ["log_pib", "homicidios_x100k", "desempeno_inst", "emergencias_hidro_x100k"]}
    res = {"rho_pesados": rho}
    for out in ("prorroga", "suspension"):
        ef, ee = cov.etapa1(filas, out, ds)
        res[out] = {"rho_efecto_depto": {k: float(stats.spearmanr(v, ef)[0]) for k, v in c.items()}, "modelos": {}}
        print(f"\n== {out}: Spearman covariable vs efecto departamental:", {k: round(v, 2) for k, v in res[out]["rho_efecto_depto"].items()})
        for nombre, cs in modelos.items():
            r = cov.etapa2(ef, ee, p, [c[k] for k in cs])
            res[out]["modelos"][nombre] = r
            print(f"{nombre:52s} OR/+10pp={r['OR_por_10pp']:.3f} IC95 ({r['ic95'][0]:.3f}-{r['ic95'][1]:.3f}) p_t={r['p_t']:.3f} gl={r['gl']}")
    res["covariables_por_departamento"] = {d: {k: float(v[i]) for k, v in c.items()} for i, d in enumerate(ds)}
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
