"""Cruce 3 con covariables departamentales (PIB y estructura económica, DANE vía datos.gov.co `kgyi-qc7j`).

Pregunta: ¿la asociación entre proporción de camiones pesados (INVIAS 2011) y prórrogas de obra (SECOP II) se mantiene al controlar por escala y
estructura económica del departamento, o la pesadez de la mezcla solo refleja minería, agro o tamaño?

Método en dos etapas (con 21 departamentos la inferencia de efectos aleatorios es frágil):
  Etapa 1: logit de contrato con efectos fijos de departamento + log valor, log duración, obra vial, pyme, modalidad y año de firma.
           Resultado: efecto de prórroga por departamento (log-odds) con su error estándar.
  Etapa 2: regresión ponderada (1/ee²) de esos efectos sobre pesados (+10 pp) y covariables. Inferencia t con G - k grados de libertad.
Covariables: promedio 2016-2023 del PIB a precios constantes de 2015: log PIB total y participaciones de minería, agro, industria y construcción.
Bogotá D.C. se suma a Cundinamarca, igual que en SECOP y la mezcla. Salida: data/transporte/cruces_covariables.json.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402
import cruces_secop_logistica as logi  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
URL_PIB = ("https://www.datos.gov.co/resource/kgyi-qc7j.json?$limit=50000&$where=tipo_de_precios%3D%27PIB%20a%20precios%20constantes%20de%202015%27"
           "%20AND%20a_o%3E%3D%272016%27%20AND%20a_o%3C%3D%272023%27")
SALIDA = base.RAIZ / "data" / "transporte" / "cruces_covariables.json"
DIVIPOLA = {5: "ANTIOQUIA", 8: "ATLANTICO", 11: "CUNDINAMARCA", 13: "BOLIVAR", 15: "BOYACA", 17: "CALDAS", 18: "CAQUETA", 19: "CAUCA", 20: "CESAR", 23: "CORDOBA",
            25: "CUNDINAMARCA", 27: "CHOCO", 41: "HUILA", 44: "GUAJIRA", 47: "MAGDALENA", 50: "META", 52: "NARINO", 54: "NORTE DE SANTANDER", 63: "QUINDIO",
            66: "RISARALDA", 68: "SANTANDER", 70: "SUCRE", 73: "TOLIMA", 76: "VALLE", 85: "CASANARE", 81: "ARAUCA", 86: "PUTUMAYO"}
SECTORES = {"mineria": "Explotación de minas", "agro": "Agricultura", "industria": "Industrias manufactureras", "construccion": "Construcción"}


def cargar_pib() -> dict[str, dict[str, float]]:
    """departamento -> {log_pib, mineria, agro, industria, construccion} (participaciones sobre el PIB total, promedio 2016-2023)."""
    filas = json.loads(base.descargar(URL_PIB, base.CACHE / "pib_dep_2016_2023.json").read_text(encoding="utf-8"))
    acum: dict[str, dict[tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
    for r in filas:
        d = DIVIPOLA.get(int(r["c_digo_departamento_divipola"]))
        if d:
            acum[d][(r["a_o"], r["actividad"])] += float(r["valor_miles_de_millones_de"])
    out = {}
    for d, v in acum.items():
        anios = sorted({a for a, _ in v})
        tot = np.mean([sum(x for (a, _), x in v.items() if a == an) for an in anios])
        part = {k: np.mean([sum(x for (a, act), x in v.items() if a == an and act.startswith(pref)) for an in anios]) / tot for k, pref in SECTORES.items()}
        out[d] = {"log_pib": float(np.log10(tot)), **{k: float(x) for k, x in part.items()}}
    return out


def etapa1(filas: list[dict], resultado: str, ds: list[str]) -> tuple[np.ndarray, np.ndarray]:
    X, nombres = logi.matriz(filas)
    # se reemplaza la constante y el predictor departamental por dummies de departamento
    cuerpo = X[:, 2:]
    dummies = np.array([[float(f["dpto"] == d) for d in ds] for f in filas])
    M = np.hstack([dummies, cuerpo])
    keep = np.ones(M.shape[1], bool)
    keep[len(ds):] = M[:, len(ds):].std(0) > 0
    y = np.array([f[resultado] for f in filas])
    ajuste = sm.GLM(y, M[:, keep], family=sm.families.Binomial()).fit()
    return np.asarray(ajuste.params[: len(ds)]), np.sqrt(np.diag(np.asarray(ajuste.cov_params()))[: len(ds)])


def etapa2(efecto: np.ndarray, ee: np.ndarray, pes: np.ndarray, covs: list[np.ndarray]) -> dict:
    Z = np.column_stack([np.ones_like(pes), 10.0 * pes, *[(c - c.mean()) / c.std() for c in covs]])
    m = sm.WLS(efecto, Z, weights=1.0 / ee**2).fit()
    gl = len(efecto) - Z.shape[1]
    b, se = float(m.params[1]), float(m.bse[1])
    # ee de etapa 1 ignora heterogeneidad residual entre departamentos: se usa el ee escalado por la varianza residual de WLS (ya incluido en m.bse)
    t = stats.t.ppf(0.975, gl)
    return {"k": Z.shape[1], "gl": gl, "OR_por_10pp": float(np.exp(b)), "ic95": (float(np.exp(b - t * se)), float(np.exp(b + t * se))), "p_t": float(2 * stats.t.sf(abs(b / se), gl)),
            "R2": float(m.rsquared)}


if __name__ == "__main__":
    mezcla, obras = base.cargar_mezcla(2011), base.cargar_obras()
    ds = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    pib = cargar_pib()
    faltan = [d for d in ds if d not in pib]
    assert not faltan, f"sin PIB: {faltan}"
    pes = {d: float(np.vstack(mezcla[d])[:, 3:].sum() / np.vstack(mezcla[d]).sum()) for d in ds}
    filas = logi.cargar_contratos(pes)
    ds = sorted({f["dpto"] for f in filas})
    p = np.array([pes[d] for d in ds])
    cov = {k: np.array([pib[d][k] for d in ds]) for k in ("log_pib", "mineria", "agro", "industria", "construccion")}
    print("correlaciones Spearman de pesados con covariables:", {k: round(float(stats.spearmanr(p, v)[0]), 2) for k, v in cov.items()})
    modelos = {"M0 solo pesados": [], "M1 + escala (log PIB)": [cov["log_pib"]], "M2 + escala + minería": [cov["log_pib"], cov["mineria"]],
               "M3 + escala + minería + agro": [cov["log_pib"], cov["mineria"], cov["agro"]],
               "M4 + escala + minería + agro + industria + construcción": [cov["log_pib"], cov["mineria"], cov["agro"], cov["industria"], cov["construccion"]]}
    res = {"correlaciones_pesados_covariables": {k: float(stats.spearmanr(p, v)[0]) for k, v in cov.items()}}
    for out in ("prorroga", "suspension"):
        ef, ee = etapa1(filas, out, ds)
        res[out] = {}
        print(f"\n== {out} (efecto departamental ajustado; rango {ef.min():.2f} a {ef.max():.2f} log-odds)")
        for nombre, cs in modelos.items():
            r = etapa2(ef, ee, p, cs)
            res[out][nombre] = r
            print(f"{nombre:58s} OR/+10pp={r['OR_por_10pp']:.3f} IC95 ({r['ic95'][0]:.3f}-{r['ic95'][1]:.3f}) p_t={r['p_t']:.3f} gl={r['gl']} R2={r['R2']:.2f}")
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
