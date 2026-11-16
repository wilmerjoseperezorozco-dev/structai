"""
Curaduría de 300–500 fotos para el entrenamiento de visión forense (issue #213).

Tesis a probar: no hacen falta 100.000 fotos. Con un modelo fundacional congelado (DINOv2, Apache-2.0) y una
selección diversa, unos cientos de etiquetas alcanzan lo que da un muestreo al azar mucho mayor.

Pasos:
  1. inventario   adaptadores por dataset → manifiesto (ruta, superficie, clase, fuente, licencia).
                  Solo entran fuentes con licencia que permite uso comercial (ver LICENCIAS).
  2. embeddings   DINOv2-small, token CLS L2-normalizado, en caché .npy (CPU, sin GPU).
  3. duplicados   casi duplicados por coseno ≥ --umbral-dup dentro de cada estrato (superficie × clase).
  4. selección    k-center greedy (cobertura máxima del espacio de embeddings) por estrato, con cuota.
  5. experimento  curva de aprendizaje con sonda lineal: k-center vs. azar, n = 25…800 etiquetas, evaluada en
                  un conjunto de prueba fijo y disjunto; 5 semillas. Mide si la selección diversa ahorra etiquetas.

Uso:
  python curar_subconjunto.py --raiz C:/Users/wilme/dev/datasets/sdnet2018/imagenes --salida salida/ --n 400
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path

import numpy as np

# Fuentes y licencia verificada (2026-11-15). Solo "comercial: True" entra al conjunto de entrenamiento de StructAI.
LICENCIAS = {
    "SDNET2018": {"licencia": "CC BY 4.0", "comercial": True, "doi": "10.15142/T3TD19",
                  "cita": "Dorafshan, Thomas, Maguire (2018), Utah State University"},
    "CODEBRIM": {"licencia": "propia, solo no comercial (cláusula 3 prohíbe uso comercial de modelos derivados)",
                 "comercial": False, "doi": "10.5281/zenodo.2620293"},
    "DeepCrack": {"licencia": "solo investigación no comercial", "comercial": False},
    "Crack500": {"licencia": "sin licencia explícita (pedir permiso)", "comercial": False},
}

SDNET_SUPERFICIE = {"D": "tablero_puente", "W": "muro", "P": "pavimento"}


def inventario_sdnet(raiz: Path) -> list[dict]:
    filas = []
    for sup, nombre in SDNET_SUPERFICIE.items():
        for sub in ("C", "U"):
            carpeta = raiz / sup / f"{sub}{sup}"
            for p in sorted(carpeta.glob("*.jpg")):
                filas.append({"ruta": str(p), "superficie": nombre, "clase": "fisura" if sub == "C" else "sana",
                              "fuente": "SDNET2018", "licencia": LICENCIAS["SDNET2018"]["licencia"]})
    return filas


def submuestra(filas: list[dict], max_por_estrato: int, semilla: int) -> list[dict]:
    """Tope por estrato para que el cómputo en CPU sea razonable (las sanas son 85 % de SDNET)."""
    rng = random.Random(semilla)
    por = {}
    for f in filas:
        por.setdefault((f["superficie"], f["clase"]), []).append(f)
    salida = []
    for k in sorted(por):
        g = por[k]
        salida += g if len(g) <= max_por_estrato else rng.sample(g, max_por_estrato)
    return salida


def embeddings(rutas: list[str], cache: Path, modelo: str = "facebook/dinov2-small", lote: int = 32) -> np.ndarray:
    if cache.exists():
        e = np.load(cache)
        if len(e) == len(rutas):
            return e
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel

    import os
    torch.set_num_threads(int(os.environ.get("STRUCTAI_HILOS", "4")))   # deja CPU para el CI nocturno (Ollama)
    proc = AutoImageProcessor.from_pretrained(modelo)
    red = AutoModel.from_pretrained(modelo).eval()
    salida = []
    t0 = time.time()
    with torch.inference_mode():
        for i in range(0, len(rutas), lote):
            imgs = [Image.open(r).convert("RGB") for r in rutas[i:i + lote]]
            x = proc(images=imgs, return_tensors="pt")
            cls = red(**x).last_hidden_state[:, 0]
            salida.append(torch.nn.functional.normalize(cls, dim=1).numpy().astype(np.float32))
            if (i // lote) % 20 == 0:
                hechas = i + len(imgs)
                print(f"  embeddings {hechas}/{len(rutas)}  {hechas / (time.time() - t0):.1f} img/s", flush=True)
    e = np.concatenate(salida)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, e)
    return e


def quitar_duplicados(emb: np.ndarray, idx: np.ndarray, umbral: float) -> np.ndarray:
    """Greedy: recorre en orden y descarta todo lo que tenga coseno ≥ umbral con algo ya aceptado."""
    aceptados: list[int] = []
    for i in idx:
        if aceptados and float(np.max(emb[aceptados] @ emb[i])) >= umbral:
            continue
        aceptados.append(int(i))
    return np.array(aceptados, dtype=int)


def k_center(emb: np.ndarray, idx: np.ndarray, k: int, semilla: int = 0) -> np.ndarray:
    """k-center greedy (Sener & Savarese 2018, "core-set"): cada nuevo punto es el más lejano de los ya elegidos."""
    if k >= len(idx):
        return idx.copy()
    rng = np.random.default_rng(semilla)
    X = emb[idx]
    elegidos = [int(rng.integers(len(idx)))]
    dmin = 1.0 - X @ X[elegidos[0]]
    for _ in range(k - 1):
        j = int(np.argmax(dmin))
        elegidos.append(j)
        dmin = np.minimum(dmin, 1.0 - X @ X[j])
    return idx[np.array(elegidos)]


def radio_cobertura(emb: np.ndarray, pool: np.ndarray, sel: np.ndarray) -> float:
    """Máxima distancia coseno de un punto del pool a su elegido más cercano (menor = mejor cobertura)."""
    d = 1.0 - emb[pool] @ emb[sel].T
    return float(np.max(np.min(d, axis=1)))


def cuotas(estratos: dict, n: int, frac_fisura: float) -> dict:
    """Reparte n: frac_fisura a las fisuras y el resto a las sanas, igual entre superficies."""
    sup = sorted({s for s, _ in estratos})
    q = {}
    for s in sup:
        q[(s, "fisura")] = round(n * frac_fisura / len(sup))
        q[(s, "sana")] = round(n * (1 - frac_fisura) / len(sup))
    return {k: min(v, len(estratos.get(k, []))) for k, v in q.items()}


def seleccionar(emb, filas, pool, n, frac_fisura, metodo, semilla):
    estratos = {}
    for i in pool:
        estratos.setdefault((filas[i]["superficie"], filas[i]["clase"]), []).append(i)
    estratos = {k: np.array(v) for k, v in estratos.items()}
    rng = np.random.default_rng(semilla)
    sel = []
    for k, q in cuotas(estratos, n, frac_fisura).items():
        g = estratos[k]
        sel.append(k_center(emb, g, q, semilla) if metodo == "kcenter" else rng.choice(g, q, replace=False))
    return np.concatenate(sel)


def experimento(emb, filas, pool, prueba, ns, semillas, frac_fisura):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score

    y = np.array([1 if f["clase"] == "fisura" else 0 for f in filas])
    res = []
    for n in ns:
        for metodo in ("kcenter", "azar"):
            for s in range(semillas):
                sel = seleccionar(emb, filas, pool, n, frac_fisura, metodo, s)
                clf = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced").fit(emb[sel], y[sel])
                pred = clf.predict(emb[prueba])
                res.append({"n": n, "metodo": metodo, "semilla": s,
                            "f1_fisura": round(float(f1_score(y[prueba], pred)), 4),
                            "f1_macro": round(float(f1_score(y[prueba], pred, average="macro")), 4),
                            "radio": round(radio_cobertura(emb, pool, sel), 4)})
        print(f"  n={n}: " + "  ".join(
            f"{m} F1={np.mean([r['f1_fisura'] for r in res if r['n'] == n and r['metodo'] == m]):.3f}"
            for m in ("kcenter", "azar")), flush=True)
    # Techo: todo el pool etiquetado
    clf = LogisticRegression(max_iter=3000, class_weight="balanced").fit(emb[pool], y[pool])
    techo = float(f1_score(y[prueba], clf.predict(emb[prueba])))
    return res, techo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--frac-fisura", type=float, default=0.7)
    ap.add_argument("--max-por-estrato", type=int, default=2600)
    ap.add_argument("--umbral-dup", type=float, default=0.97)
    ap.add_argument("--frac-prueba", type=float, default=0.25)
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--modelo", default="facebook/dinov2-small")
    a = ap.parse_args()
    a.salida.mkdir(parents=True, exist_ok=True)

    filas = submuestra(inventario_sdnet(a.raiz), a.max_por_estrato, 13)
    print(f"inventario: {len(filas)} imágenes (tope {a.max_por_estrato} por estrato)", flush=True)
    emb = embeddings([f["ruta"] for f in filas], a.salida / f"emb_{a.modelo.split('/')[-1]}_{len(filas)}.npy", a.modelo)

    # Prueba fija y disjunta, estratificada, ANTES de seleccionar nada.
    rng = np.random.default_rng(2026)
    todos = np.arange(len(filas))
    prueba = []
    for k in sorted({(f["superficie"], f["clase"]) for f in filas}):
        g = np.array([i for i in todos if (filas[i]["superficie"], filas[i]["clase"]) == k])
        prueba += list(rng.choice(g, int(len(g) * a.frac_prueba), replace=False))
    prueba = np.array(sorted(prueba))
    pool = np.setdiff1d(todos, prueba)

    # Duplicados solo en el pool (la prueba no se toca)
    pool_limpio = []
    for k in sorted({(filas[i]["superficie"], filas[i]["clase"]) for i in pool}):
        g = np.array([i for i in pool if (filas[i]["superficie"], filas[i]["clase"]) == k])
        pool_limpio.append(quitar_duplicados(emb, g, a.umbral_dup))
    pool_limpio = np.concatenate(pool_limpio)
    print(f"pool {len(pool)} → {len(pool_limpio)} tras quitar casi duplicados (coseno ≥ {a.umbral_dup})", flush=True)

    ns = [n for n in (25, 50, 100, 200, 400, 800) if n <= len(pool_limpio)]
    res, techo = experimento(emb, filas, pool_limpio, prueba, ns, a.semillas, a.frac_fisura)

    sel = seleccionar(emb, filas, pool_limpio, a.n, a.frac_fisura, "kcenter", 0)
    with (a.salida / "seleccion_para_etiquetar.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["orden", "ruta", "superficie", "clase", "fuente", "licencia"])
        w.writeheader()
        for o, i in enumerate(sel):
            w.writerow({"orden": o, **filas[i]})
    resumen = {"imagenes": len(filas), "pool": int(len(pool)), "pool_sin_duplicados": int(len(pool_limpio)),
               "prueba": int(len(prueba)), "modelo": a.modelo, "techo_f1_pool_completo": round(techo, 4),
               "seleccion": int(len(sel)), "curva": res, "licencias": LICENCIAS}
    (a.salida / "resultado_curaduria.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"techo (pool completo, {len(pool_limpio)} etiquetas): F1 fisura = {techo:.3f}")
    print(f"selección de {len(sel)} → {a.salida / 'seleccion_para_etiquetar.csv'}")


if __name__ == "__main__":
    main()
