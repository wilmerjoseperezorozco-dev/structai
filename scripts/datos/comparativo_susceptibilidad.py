"""Comparación 1 de PROTOCOLO_COMPARATIVO.md: modelos de susceptibilidad no medidos (logística L1, logística con splines, bosque aleatorio, árboles extremadamente
aleatorios, perceptrón multicapa) frente a gradient boosting, con la validación cruzada del banco C (5 grupos de departamentos, 3 réplicas).
Uso: python comparativo_susceptibilidad.py"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import p1_susceptibilidad as S  # noqa: E402  (cargar, oof, TODAS, K_FOLDS, REPS)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CONT = ["elev", "pend", "curv", "dist_falla_km", "lluvia_anual_mm"]
CAT = ["edad", "cobertura"]
N_BOOT = 150


def prep(spline: bool):
    num = make_pipeline(SplineTransformer(n_knots=5, degree=3), StandardScaler()) if spline else StandardScaler()
    return ColumnTransformer([("n", num, CONT), ("c", OneHotEncoder(handle_unknown="ignore"), CAT)])


MODELOS = {
    "LR (L1)": lambda: make_pipeline(prep(False), LogisticRegression(penalty="l1", solver="liblinear", C=1.0, max_iter=300)),
    "LR + splines": lambda: make_pipeline(prep(True), LogisticRegression(C=1.0, max_iter=500)),
    "Bosque aleatorio": lambda: make_pipeline(prep(False), RandomForestClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=3, random_state=0)),
    "Árboles extremadamente aleatorios": lambda: make_pipeline(prep(False), ExtraTreesClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=3, random_state=0)),
    "Perceptrón 64-32": lambda: make_pipeline(prep(False), MLPClassifier(hidden_layer_sizes=(64, 32), early_stopping=True, max_iter=100, random_state=0)),
}


def oof_modelo(d, fabrica, rep):
    rng = np.random.default_rng(1000 + rep); deps = np.unique(d.dep); rng.shuffle(deps)
    fd = d.dep.map({x: i % S.K_FOLDS for i, x in enumerate(deps)}).to_numpy(); p = np.zeros(len(d))
    for k in range(S.K_FOLDS):
        tr, te = np.where(fd != k)[0], np.where(fd == k)[0]
        m = fabrica().fit(d.loc[tr, CONT + CAT], d.loc[tr, "presencia"]); p[te] = m.predict_proba(d.loc[te, CONT + CAT])[:, 1]
    return p


def main() -> None:
    d = S.cargar(); y = d.presencia.to_numpy(); dep = d.dep.to_numpy(); u = np.unique(dep); ix = {x: np.where(dep == x)[0] for x in u}
    ref = [S.oof(d, S.TODAS, r) for r in range(S.REPS)]
    pred = {"HGB (referencia)": ref}
    for nombre, fab in MODELOS.items():
        pred[nombre] = [oof_modelo(d, fab, r) for r in range(S.REPS)]; print(f"   ajustado: {nombre}", flush=True)
    rng = np.random.default_rng(20261109)
    boots = [np.concatenate([ix[x] for x in rng.choice(u, len(u))]) for _ in range(N_BOOT)]
    print("\nAUC espacial (promedio de 3 réplicas), Brier y diferencia frente a HGB (IC95 % por departamento):")
    res, pv = {}, {}
    for nombre, ps in pred.items():
        auc = np.mean([roc_auc_score(y, p) for p in ps]); br = np.mean([brier_score_loss(y, p) for p in ps])
        if nombre.startswith("HGB"):
            print(f"   {nombre:<34} AUC {auc:.4f}  Brier {br:.4f}"); res[nombre] = {"auc": float(auc), "brier": float(br)}; continue
        base = np.mean([roc_auc_score(y, a) - roc_auc_score(y, b) for a, b in zip(ps, ref)])
        bd = np.array([np.mean([roc_auc_score(y[s], a[s]) - roc_auc_score(y[s], b[s]) for a, b in zip(ps, ref)]) for s in boots if len(np.unique(y[s])) == 2])
        lo, hi = np.percentile(bd, [2.5, 97.5]); pv[nombre] = (np.sum(bd <= 0) + 1) / (len(bd) + 1)
        res[nombre] = {"auc": float(auc), "brier": float(br), "dif": float(base), "lo": float(lo), "hi": float(hi)}
        print(f"   {nombre:<34} AUC {auc:.4f}  Brier {br:.4f}  Δ vs HGB = {base:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    orden = sorted(pv, key=pv.get); prev = 0.0
    print("\nSuperioridad frente a HGB (Holm sobre 5):")
    for i, k in enumerate(orden):
        prev = max(prev, min(1.0, pv[k] * (len(orden) - i))); res[k]["holm"] = float(prev)
        print(f"   {k:<34} p ajustado {prev:.3f} -> {'SUPERA' if prev < 0.05 and res[k]['dif'] > 0 else 'no supera'}")
    for k in ("LR (L1)", "LR + splines"):
        print(f"No inferioridad de {k} frente a HGB (margen −0,02): límite inferior {res[k]['lo']:+.4f} -> {'no inferior' if res[k]['lo'] > -0.02 else 'no se puede afirmar'}")
    nombres = list(pred); M = np.array([[spearmanr(pred[a][0], pred[b][0])[0] for b in nombres] for a in nombres])
    print("\nAcuerdo espacial entre modelos (correlación de rangos de las predicciones, réplica 1):")
    for a, fila in zip(nombres, M):
        print(f"   {a:<34} " + " ".join(f"{v:5.2f}" for v in fila))
    (AQUI / "comparativo_susceptibilidad_resultados.json").write_text(json.dumps({"modelos": res, "acuerdo": M.tolist(), "orden": nombres}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
