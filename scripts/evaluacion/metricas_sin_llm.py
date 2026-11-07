"""Métricas de evaluación SIN LLM (protocolo: PROTOCOLO_METRICAS_SIN_LLM.md, definido antes de correr).

Usa solo lo ya guardado: baseline_2026-09-09_278preguntas_{muestras.jsonl,scorecard.csv} y la tabla consultas_history.
Uso: python scripts/evaluacion/metricas_sin_llm.py
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
EVAL = RAIZ / "scripts" / "evaluacion"
RNG = np.random.default_rng(20261107)
N_BOOT = 2000
UMBRAL_REL, MIN_CLAVES, K_LISTA = 0.5, 3, (1, 3, 5, 10)
TIPOS_ESPECIALES = ("ADV", "COLOQ", "COMP", "SINT")
PALABRAS_VACIAS = set("""porque cuando donde segun deben debe entre sobre puede pueden parte tanto mismo misma cada otros otras otro otra
tambien siempre ademas aunque desde hasta cuales cuanto cuanta cuantos cuantas minimo maxima maximo minima norma normas reglamento
titulo capitulo articulo seccion requisitos requisito indica indican establece establecen aplica aplican respecto mediante conforme
debera deberan existe existen general generales segun cualquier ninguna ninguno respuesta pregunta valor valores caso casos""".split())
RE_CODIGO = re.compile(r"\b[A-K]\.\d+(?:\.\d+)*(?:\.\d+)*", re.I)
RE_TABLA = re.compile(r"\b(?:tabla|figura)\s+[A-K]?\.?\d+(?:\.\d+)*(?:-\d+)?", re.I)
RE_NUM = re.compile(r"\d+(?:[.,]\d+)?")
ABSTENCION = ("no tengo", "no se encuentra", "no cuento con", "no puedo confirmar", "no esta en", "no hay informacion", "no dispongo",
              "no existe informacion", "no encontre", "no figura", "no esta disponible", "no tengo informacion")


ABSTENCION_AMPLIADA = ABSTENCION + ("no incluye", "no menciona", "no existe", "no contempla", "no especifica", "no aborda", "no hay un", "no se hace referencia")


def sin_acentos(s: str) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()


def numeros(texto: str) -> set[str]:
    out = set()
    for m in RE_NUM.findall(sin_acentos(texto)):
        m = m.replace(",", ".")
        if "." in m or len(m) >= 2:
            out.add(m)
    return out


def codigos(texto: str) -> set[str]:
    t = sin_acentos(texto)
    return {re.sub(r"\s+", "", c.lower()) for c in RE_CODIGO.findall(t)} | {re.sub(r"\s+", "", c.lower()) for c in RE_TABLA.findall(t)}


def claves(referencia: str) -> set[str]:
    t = sin_acentos(referencia)
    palabras = {w for w in re.findall(r"[a-z]{6,}", t) if w not in PALABRAS_VACIAS}
    return {"n:" + n for n in numeros(referencia)} | {"c:" + c for c in codigos(referencia)} | {"w:" + w for w in palabras}


def tokens_contexto(ctx: str) -> set[str]:
    t = sin_acentos(ctx)
    return ({"n:" + n for n in numeros(ctx)} | {"c:" + c for c in codigos(ctx)} |
            {"w:" + w for w in re.findall(r"[a-z]{6,}", t) if w not in PALABRAS_VACIAS})


def cobertura(k: set[str], ctx: str) -> float:
    return len(k & tokens_contexto(ctx)) / len(k) if k else 0.0


def wilson(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def boot_cluster(valores: np.ndarray, cluster: np.ndarray, fun=np.mean) -> tuple[float, float]:
    u = np.unique(cluster); idx = {c: np.where(cluster == c)[0] for c in u}
    out = []
    for _ in range(N_BOOT):
        sel = np.concatenate([idx[c] for c in RNG.choice(u, len(u), replace=True)])
        out.append(fun(valores[sel]))
    return tuple(np.percentile(out, [2.5, 97.5]))


def cargar() -> pd.DataFrame:
    filas = [json.loads(l) for l in open(EVAL / "baseline_2026-09-09_278preguntas_muestras.jsonl", encoding="utf-8")]
    df = pd.DataFrame(filas)
    pref = df["id"].str.split("-").str[0]
    base = pref.str.rstrip("0123456789")
    df["tipo"] = np.where(base.isin(TIPOS_ESPECIALES), base, "hecho")
    df["cluster"] = np.where(df.tipo == "hecho", pref, df.tipo)
    sc = pd.read_csv(EVAL / "baseline_2026-09-09_278preguntas_scorecard.csv")[["user_input", "context_recall", "context_precision", "faithfulness"]]
    return df.merge(sc.drop_duplicates("user_input"), on="user_input", how="left")


def metricas_recuperacion(df: pd.DataFrame) -> dict:
    sub = df[df.tipo != "ADV"].copy()
    sub["claves"] = sub["reference"].map(claves)
    sub = sub[sub["claves"].map(len) >= MIN_CLAVES].copy()
    sub["cov"] = [[cobertura(k, c) for c in cs] for k, cs in zip(sub["claves"], sub["retrieved_contexts"])]
    sub["covmax"] = sub["cov"].map(lambda v: max(v) if v else 0.0)
    ok = sub.dropna(subset=["context_recall"])
    rho = spearmanr(ok["covmax"], ok["context_recall"])[0] if len(ok) > 10 else np.nan
    lo, hi = boot_cluster(np.c_[ok["covmax"], ok["context_recall"]], ok["cluster"].to_numpy(),
                          lambda m: spearmanr(m[:, 0], m[:, 1])[0]) if len(ok) > 10 else (np.nan, np.nan)
    valido = bool(rho > 0.30 and lo > 0)
    print(f"\n== M1 validación del proxy: n={len(ok)} ρ(cobertura máx., context_recall RAGAS) = {rho:+.2f} IC95% [{lo:+.2f}, {hi:+.2f}] -> "
          f"{'VÁLIDO' if valido else 'NO VÁLIDO: M2 no se publica como medida de recuperación'}")
    res = {"M1": {"n": int(len(ok)), "rho": float(rho), "ic": [float(lo), float(hi)], "valido": valido, "por_tipo": {}}, "M2": {}}
    for t, g in ok.groupby("tipo"):
        if len(g) >= 10:
            r_t = float(spearmanr(g["covmax"], g["context_recall"])[0]); res["M1"]["por_tipo"][t] = {"n": int(len(g)), "rho": r_t}
            print(f"   (descriptivo) validez por tipo {t}: n={len(g)} ρ = {r_t:+.2f}")

    def rr(v):
        for i, c in enumerate(v):
            if c >= UMBRAL_REL:
                return 1 / (i + 1)
        return 0.0

    def ndcg(v):
        v = v[:10]
        dcg = sum(c / np.log2(i + 2) for i, c in enumerate(v))
        ideal = sum(c / np.log2(i + 2) for i, c in enumerate(sorted(v, reverse=True)))
        return dcg / ideal if ideal > 0 else 0.0

    def fila(g: pd.DataFrame, por_pregunta: bool = False):
        # Los grupos de un solo tipo especial no tienen estructura de clúster (todos compartirían el mismo): IC por pregunta.
        cl = np.arange(len(g)) if por_pregunta else g["cluster"].to_numpy()
        out = {"n": int(len(g))}
        for K in K_LISTA:
            x = np.array([any(c >= UMBRAL_REL for c in v[:K]) for v in g["cov"]], float)
            out[f"recall@{K}"] = (float(x.mean()),) + tuple(map(float, boot_cluster(x, cl)))
        for nombre, f in (("MRR", rr), ("NDCG@10", ndcg)):
            x = np.array([f(v) for v in g["cov"]], float)
            out[nombre] = (float(x.mean()),) + tuple(map(float, boot_cluster(x, cl)))
        return out
    print("\n== M2 recuperación (proxy léxico; excluye ADV y referencias con < 3 claves) ==")
    for nombre, g in [("GLOBAL", sub)] + [(t, sub[sub.tipo == t]) for t in sorted(sub.tipo.unique())]:
        if len(g) < 5:
            continue
        r = fila(g, por_pregunta=nombre not in ("GLOBAL", "hecho")); res["M2"][nombre] = r
        print(f"  {nombre:<7} n={r['n']:<3} " + " | ".join(f"{k} {r[k][0]:.2f} [{r[k][1]:.2f},{r[k][2]:.2f}]" for k in ("recall@1", "recall@3", "recall@5", "recall@10", "MRR", "NDCG@10")))
    return res


def metricas_citas_numeros(df: pd.DataFrame) -> dict:
    res = {"M3": {}, "M4": {}}
    sup = tot = 0
    por_resp, hall = [], []
    for _, r in df.iterrows():
        ctx = sin_acentos(" ".join(r["retrieved_contexts"]))
        ctx_compacto = re.sub(r"\s+", "", ctx)
        cits = codigos(r["response"])
        if cits:
            s = sum(1 for c in cits if c in ctx_compacto)
            sup += s; tot += len(cits); por_resp.append(s / len(cits))
        nums = numeros(r["response"]) - numeros(r["user_input"])
        hall.append((r["tipo"], r["cluster"], int(any(n not in ctx for n in nums)) if nums else np.nan))
    print("\n== M3 corrección de citas ==")
    print(f"  citas totales {tot}; con soporte en el contexto {sup} ({100 * sup / max(tot, 1):.1f} %); respuestas con ≥1 cita {len(por_resp)}; "
          f"tasa media por respuesta {np.mean(por_resp):.2f}")
    res["M3"] = {"citas": tot, "con_soporte": sup, "tasa": sup / max(tot, 1), "respuestas_con_cita": len(por_resp)}
    h = pd.DataFrame(hall, columns=["tipo", "cluster", "flag"]).dropna()
    print("\n== M4 posible alucinación numérica (respuesta con ≥1 cifra ausente del contexto) ==")
    for nombre, g in [("GLOBAL", h)] + [(t, h[h.tipo == t]) for t in sorted(h.tipo.unique())]:
        x, n = int(g.flag.sum()), len(g)
        lo, hi = wilson(x, n)
        res["M4"][nombre] = {"x": x, "n": n, "tasa": x / max(n, 1), "ic": [float(lo), float(hi)]}
        print(f"  {nombre:<7} {x}/{n} = {100 * x / max(n, 1):.1f} % [{100 * lo:.1f}, {100 * hi:.1f}]")
    return res


def abstencion(df: pd.DataFrame) -> dict:
    res = {}
    df = df.assign(abst=[any(f in sin_acentos(r) for f in ABSTENCION) for r in df["response"]],
                   abst_amp=[any(f in sin_acentos(r) for f in ABSTENCION_AMPLIADA) for r in df["response"]])
    print("\n== M5 abstención. (a) léxico fijado ANTES de correr; (b) léxico AMPLIADO post hoc tras revisar a mano las 12 adversariales sin coincidencia ==")
    for nombre, g in [("GLOBAL", df)] + [(t, df[df.tipo == t]) for t in sorted(df.tipo.unique())]:
        res[nombre] = {}
        partes = []
        for clave, col in (("a_priori", "abst"), ("ampliado_post_hoc", "abst_amp")):
            x, n = int(g[col].sum()), len(g); lo, hi = wilson(x, n)
            res[nombre][clave] = {"x": x, "n": n, "tasa": x / max(n, 1), "ic": [float(lo), float(hi)]}
            partes.append(f"{clave}: {x}/{n} = {100 * x / max(n, 1):.1f} % [{100 * lo:.1f}, {100 * hi:.1f}]")
        etiqueta = "esperada ALTA" if nombre == "ADV" else ("falsa abstención, esperada BAJA" if nombre != "GLOBAL" else "global")
        print(f"  {nombre:<7} " + " | ".join(partes) + f"  ({etiqueta})")
    return res


def produccion() -> dict:
    sys.path.insert(0, str(RAIZ / "scripts" / "satelite"))
    import _datos_caribe as dc
    filas, ini, sb = [], 0, dc._sb()
    while True:
        p = sb.table("consultas_history").select("latencia_ms,feedback_util,created_at,dominio_enrutado").range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    d = pd.DataFrame(filas)
    lat = pd.to_numeric(d["latencia_ms"], errors="coerce").dropna()
    lat = lat[lat > 0]
    res = {"n_consultas": int(len(d)), "n_con_latencia": int(len(lat))}
    print(f"\n== M6 producción: {len(d)} consultas en consultas_history ({len(lat)} con latencia) ==")
    if len(lat) >= 5:
        for q in (50, 95, 99):
            v = np.percentile(lat, q); lo, hi = boot_cluster(lat.to_numpy(), np.arange(len(lat)), lambda x, q=q: np.percentile(x, q))
            res[f"p{q}_ms"] = [float(v), float(lo), float(hi)]
            print(f"  latencia p{q} = {v:,.0f} ms  IC95% [{lo:,.0f}, {hi:,.0f}]")
    d["mes"] = pd.to_datetime(d["created_at"]).dt.strftime("%Y-%m")
    d["lat"] = pd.to_numeric(d["latencia_ms"], errors="coerce")
    res["por_mes"] = {}
    print("  (descriptivo, post hoc) latencia por mes:")
    for m, g in d[d.lat > 0].groupby("mes"):
        res["por_mes"][m] = {"n": int(len(g)), "p50": float(g.lat.median()), "max": float(g.lat.max())}
        print(f"    {m}: n={len(g):>2}  mediana {g.lat.median():>8,.0f} ms  máximo {g.lat.max():>8,.0f} ms")
    fb = d["feedback_util"].dropna()
    fb = fb[fb.astype(str).isin(["True", "False", "true", "false"])]
    if len(fb):
        pos = int(fb.astype(str).str.lower().eq("true").sum()); lo, hi = wilson(pos, len(fb))
        res["feedback"] = {"n": int(len(fb)), "positivos": pos, "tasa": pos / len(fb), "ic": [float(lo), float(hi)]}
        print(f"  feedback: {pos}/{len(fb)} positivos = {100 * pos / len(fb):.0f} % [{100 * lo:.0f}, {100 * hi:.0f}] (n muy pequeño)")
    else:
        print("  feedback: ninguna consulta con 👍/👎 registrado")
        res["feedback"] = {"n": 0}
    return res


def main() -> None:
    df = cargar()
    print(f"Dataset: {len(df)} preguntas; por tipo: {df.tipo.value_counts().to_dict()}")
    out = {}
    out.update(metricas_recuperacion(df))
    out.update(metricas_citas_numeros(df))
    out["M5"] = abstencion(df)
    out["M6"] = produccion()
    (EVAL / "metricas_sin_llm_resultados.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
