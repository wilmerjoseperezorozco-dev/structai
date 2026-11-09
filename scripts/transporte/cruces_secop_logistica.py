"""Cruces 3-5: retrasos y ejecución de obras SECOP II, y densidad de peajes, frente a la mezcla de camiones INVIAS 2011.

Cruce 3 (contrato): logit de {prórroga (días adicionados > 0), suspensión, adición de valor} sobre log valor, log duración, obra vial, modalidad,
  pyme, año de firma (efectos fijos: los contratos recientes no han tenido tiempo de acumular prórrogas) y la proporción de pesados del
  departamento (por cada +10 pp). Errores agrupados por departamento con inferencia t de G-1 grados de libertad (G = 21 es pocos grupos).
Cruce 4 (departamento): proporción de registros 'Confirmado' con avance real < esperado, frente a pesados (Spearman parcial por estaciones). La brecha
  mediana es 0 en todos los departamentos (86 % de los registros reportan real = esperado, probable autollenado), por eso se usa la proporción de atraso.
Cruce 5 (departamento): peajes por departamento frente a valor vial contratado y a pesados.
Familia de pruebas primarias corregida por Holm. Todo el efecto es ECOLÓGICO: el predictor es del departamento, no del contrato.
Salida: data/transporte/cruces_secop_logistica.json.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = base.RAIZ
CACHE_SECOP = RAIZ / "scripts" / "secop" / "_cache"
SALIDA = RAIZ / "data" / "transporte" / "cruces_secop_logistica.json"
MODALIDADES = ("Selección Abreviada de Menor Cuantía", "Contratación directa", "Mínima cuantía", "Licitación pública Obra Publica")
MIN_EJEC_DEPTO = 30


def duracion_dias(txt: str) -> float:
    m = re.search(r"(\d+)\s*Mes", txt or "")
    if m:
        return 30.0 * int(m.group(1))
    m = re.search(r"(\d+)\s*D[ií]a", txt or "")
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s*A[ñn]o", txt or "")
    return 365.0 * int(m.group(1)) if m else float("nan")


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def tipos_por_contrato() -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for linea in (CACHE_SECOP / "adiciones.jsonl").open(encoding="utf-8"):
        a = json.loads(linea)
        out[a["id_contrato"]].add(unicodedata.normalize("NFKD", a["tipo"]).encode("ascii", "ignore").decode().lower())
    return out


def cargar_contratos(pesados: dict[str, float]) -> list[dict]:
    tipos, filas = tipos_por_contrato(), []
    for linea in (CACHE_SECOP / "contratos_obra.jsonl").open(encoding="utf-8"):
        c = json.loads(linea)
        d = base.norm(c.get("departamento", ""))
        v, dur = num(c.get("valor_del_contrato")), duracion_dias(c.get("duraci_n_del_contrato", ""))
        firma = c.get("fecha_de_firma") or ""
        if d not in pesados or not (0 < v <= base.VALOR_MAX_COP) or np.isnan(dur) or dur <= 0 or len(firma) < 4:
            continue
        txt = unicodedata.normalize("NFKD", (c.get("objeto_del_contrato") or "").lower()).encode("ascii", "ignore").decode()
        t = tipos.get(c["id_contrato"], set())
        filas.append({"id": c["id_contrato"], "dpto": d, "lv": np.log10(v), "ld": np.log10(dur), "vial": float(bool(base.VIAL.search(txt))),
                      "pyme": float(c.get("es_pyme") == "Si"), "mod": c.get("modalidad_de_contratacion"), "anio": int(firma[:4]),
                      "prorroga": float(num(c.get("dias_adicionados")) > 0), "suspension": float(any("suspension" in x for x in t)),
                      "adicion_valor": float(any("adicion en el valor" in x for x in t)), "pesados": pesados[d]})
    return filas


def matriz(filas: list[dict]) -> tuple[np.ndarray, list[str]]:
    anios = sorted({f["anio"] for f in filas})[1:]
    nombres = ["const", "pesados_10pp", "log_valor", "log_duracion", "vial", "pyme"] + [f"mod:{m[:12]}" for m in MODALIDADES] + [f"anio{a}" for a in anios]
    X = [[1.0, 10.0 * f["pesados"], f["lv"], f["ld"], f["vial"], f["pyme"], *[float(f["mod"] == m) for m in MODALIDADES], *[float(f["anio"] == a) for a in anios]]
         for f in filas]
    return np.array(X), nombres


def logit_agrupado(filas: list[dict], resultado: str) -> dict:
    X, nombres = matriz(filas)
    y = np.array([f[resultado] for f in filas])
    grupos = np.unique([f["dpto"] for f in filas], return_inverse=True)[1]
    g = len(set(grupos))
    ok = X.std(0) > 0
    ok[0] = True
    m = sm.GLM(y, X[:, ok], family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": grupos, "use_correction": True, "df_correction": True})
    i = [n for n, k in zip(nombres, ok) if k].index("pesados_10pp")
    b, se = float(m.params[i]), float(m.bse[i])
    t, tcrit = b / se, stats.t.ppf(0.975, g - 1)
    return {"n": len(y), "G": g, "tasa": float(y.mean()), "OR_por_10pp": float(np.exp(b)), "ic95": (float(np.exp(b - tcrit * se)), float(np.exp(b + tcrit * se))),
            "p_t": float(2 * stats.t.sf(abs(t), g - 1)), "p_normal_ref": float(m.pvalues[i])}


def cruce_ejecucion(pesados: dict[str, float], nest: dict[str, int], rng) -> dict:
    depto = {}
    for linea in (CACHE_SECOP / "contratos_obra.jsonl").open(encoding="utf-8"):
        c = json.loads(linea)
        depto[c["id_contrato"]] = base.norm(c.get("departamento", ""))
    brechas: dict[str, list[float]] = defaultdict(list)
    for linea in (CACHE_SECOP / "ejecucion.jsonl").open(encoding="utf-8"):
        e = json.loads(linea)
        if e.get("estado_del_contrato") != "Confirmado":
            continue
        d, esp, real = depto.get(e["identificadorcontrato"]), num(e.get("porcentajedeavanceesperado")), num(e.get("porcentaje_de_avance_real"))
        if d in pesados and not (np.isnan(esp) or np.isnan(real)):
            brechas[d].append(real - esp)
    ds = sorted(d for d, v in brechas.items() if len(v) >= MIN_EJEC_DEPTO)
    med = np.array([np.mean(np.array(brechas[d]) < 0) for d in ds])
    pes, nes = np.array([pesados[d] for d in ds]), np.array([nest[d] for d in ds], float)
    print(f"\n== Cruce 4: ejecución (avance real - esperado, registros 'Confirmado'), {len(ds)} departamentos con >= {MIN_EJEC_DEPTO} registros")
    todos = np.concatenate([brechas[d] for d in ds])
    print(f"registros con real = esperado: {100 * np.mean(todos == 0):.0f} %; con atraso (real < esperado): {100 * np.mean(todos < 0):.1f} %; rango departamental {100 * med.min():.1f}-{100 * med.max():.1f} %")
    res = base.parcial_boot(pes, med, nes, rng)
    return {"departamentos": ds, "n_registros": int(len(todos)), "prop_real_igual_esperado": float(np.mean(todos == 0)), "prop_atraso_nacional": float(np.mean(todos < 0)),
            "T_ejecucion_parcial": res}


def cruce_peajes_densidad(mezcla: dict, obras: dict, pesados: dict[str, float], rng) -> dict:
    cuenta: dict[str, int] = defaultdict(int)
    for p in base.cargar_peajes():
        cuenta[p["dpto"]] += 1
    ds = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    npj = np.array([cuenta.get(d, 0) for d in ds], float)
    nes = np.array([len(mezcla[d]) for d in ds], float)
    lv = np.log10([obras[d]["valor_vial"] + 1 for d in ds])
    pes = np.array([pesados[d] for d in ds])
    print(f"\n== Cruce 5: densidad de peajes ({len(ds)} departamentos; mediana {np.median(npj):.0f} peajes)")
    return {"T_peajes_vs_valor_vial_parcial": base.parcial_boot(npj, lv, nes, rng), "T_peajes_vs_pesados_parcial": base.parcial_boot(npj, pes, nes, rng),
            "peajes_por_depto": {d: int(c) for d, c in zip(ds, npj)}}


if __name__ == "__main__":
    rng = np.random.default_rng(base.SEMILLA)
    mezcla = base.cargar_mezcla(2011)
    obras = base.cargar_obras()
    ds = sorted(d for d in set(mezcla) & set(obras) if d != "OCANA")
    pesados = {d: float(np.vstack(mezcla[d])[:, 3:].sum() / np.vstack(mezcla[d]).sum()) for d in ds}
    nest = {d: len(mezcla[d]) for d in ds}
    filas = cargar_contratos(pesados)
    print(f"\n== Cruce 3: {len(filas)} contratos en {len({f['dpto'] for f in filas})} departamentos")
    r3 = {}
    for out in ("prorroga", "suspension", "adicion_valor"):
        r3[out] = logit_agrupado(filas, out)
        r = r3[out]
        print(f"{out:14s} tasa={100 * r['tasa']:5.1f}%  OR por +10 pp de pesados = {r['OR_por_10pp']:.3f} IC95 ({r['ic95'][0]:.3f}-{r['ic95'][1]:.3f}) p_t={r['p_t']:.3f}  "
              f"(p normal {r['p_normal_ref']:.3f})")
    r4, r5 = cruce_ejecucion(pesados, nest, rng), cruce_peajes_densidad(mezcla, obras, pesados, rng)
    print("T4", r4["T_ejecucion_parcial"]); print("T5a", r5["T_peajes_vs_valor_vial_parcial"]); print("T5b", r5["T_peajes_vs_pesados_parcial"])
    familia = {f"T3_{k}": v["p_t"] for k, v in r3.items()}
    familia.update({"T4_ejecucion": r4["T_ejecucion_parcial"]["p_perm"], "T5a_peajes_valor_vial": r5["T_peajes_vs_valor_vial_parcial"]["p_perm"],
                    "T5b_peajes_pesados": r5["T_peajes_vs_pesados_parcial"]["p_perm"]})
    ph = base.holm(familia)
    print("\nHolm (6 pruebas):", {k: round(v, 4) for k, v in ph.items()})
    SALIDA.write_text(json.dumps({"cruce3": r3, "cruce4": r4, "cruce5": r5, "p_holm": ph, "semilla": base.SEMILLA}, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
