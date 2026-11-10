"""
Ciclo operativo de aprendizaje activo para el clasificador de dominio
(issue #169, E1e). Prioriza QUÉ consultas reales conviene etiquetar a mano.

E1e mostró que 38 preguntas de la misma distribución que el uso real valen
más que 333 de las baterías de NSR-10 (que incluso empeoran el modelo). Por
eso el pool de este ciclo son las consultas reales de consultas_history (más,
opcionalmente, preguntas escritas por colegas), no las baterías.

Pasos:
  1) seleccionar: entrena con todo lo etiquetado, puntúa el pool por entropía
     y elige N con diversidad (k-medias). Escribe un CSV para etiquetar.
  2) Una persona llena la columna `etiqueta` (y `aceptables` si aplica),
     siguiendo docs/evaluacion/GUIA_ETIQUETADO_DOMINIO.md.
  3) incorporar: valida el CSV y lo agrega al almacén de etiquetas.

Privacidad: las consultas reales pueden contener datos de usuarios. Todo lo
que sale de consultas_history se escribe en _privado/, que está en .gitignore.
Solo lectura en Supabase.

Uso:
  python aprendizaje_activo.py seleccionar [--n 20] [--desde 2026-10-27] [--extra preguntas.txt]
  python aprendizaje_activo.py incorporar _privado/por_etiquetar_AAAA-MM-DD.csv
  python aprendizaje_activo.py estado
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

import e1e_umbral_activo as m

AQUI = Path(__file__).parent
PRIVADO = AQUI / "_privado"
ALMACEN = PRIVADO / "etiquetadas.jsonl"
DOMINIOS = sorted(set(m.e.mrc.EJEMPLOS_POR_DOMINIO))
COLUMNAS = ["id", "pregunta", "predicho", "confianza", "segundo", "enrutado_produccion",
            "etiqueta", "aceptables", "nota"]


def _etiquetado_publico():
    """Semilla de producción + dataset E1 completo (dev y test: en operación
    ya no se reserva test; la evaluación formal se repite con held-out nuevo)."""
    filas = [(q, d) for d, qs in m.e.mrc.EJEMPLOS_POR_DOMINIO.items() for q in qs]
    for l in (AQUI / "dataset_e1.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(l)
        filas.append((c["pregunta"], c["esperado"]))
    return filas


def _etiquetado_privado():
    if not ALMACEN.exists():
        return []
    return [(x["pregunta"], x["etiqueta"]) for x in map(json.loads, ALMACEN.read_text(encoding="utf-8").splitlines())]


def entrenar_todo():
    datos = _etiquetado_publico() + _etiquetado_privado()
    X = m.emb([q for q, _ in datos])
    y = np.array([d for _, d in datos])
    modelo = m.entrenar(X, y)
    return modelo, m.ajustar_tau(X, y), {q for q, _ in datos}


def _pool(desde: str | None, extra: Path | None):
    pool = []
    q = m.e.r.sb.table("consultas_history").select("id,pregunta,dominio_enrutado,created_at").order("created_at")
    if desde:
        q = q.gte("created_at", desde)
    for f in q.execute().data:
        if f.get("pregunta"):
            pool.append({"id": f"hist-{f['id']}", "pregunta": f["pregunta"].strip(),
                         "enrutado_produccion": f.get("dominio_enrutado") or ""})
    if extra:
        for i, linea in enumerate(extra.read_text(encoding="utf-8").splitlines()):
            if linea.strip():
                pool.append({"id": f"extra-{extra.stem}-{i}", "pregunta": linea.strip(), "enrutado_produccion": ""})
    vistos, unicos = set(), []
    for p in pool:
        clave = m.e._norm(p["pregunta"])
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(p)
    return unicos


def seleccionar(n: int, desde: str | None, extra: Path | None):
    modelo, tau, ya = entrenar_todo()
    pool = [p for p in _pool(desde, extra) if p["pregunta"] not in ya]
    if not pool:
        print("Pool vacío: no hay consultas nuevas sin etiquetar.")
        return
    X = m.emb([p["pregunta"] for p in pool])
    P = modelo.predict_proba(X)
    entropia = -(P * np.log(P + 1e-12)).sum(1)
    candidatos = list(np.argsort(-entropia)[: max(n * 4, n)])
    k = min(n, len(candidatos))
    if k < len(candidatos):
        km = KMeans(n_clusters=k, n_init=5, random_state=169).fit(X[candidatos])
        elegidos = [max((c for c, l in zip(candidatos, km.labels_) if l == g), key=lambda c: entropia[c]) for g in range(k)]
    else:
        elegidos = candidatos
    PRIVADO.mkdir(exist_ok=True)
    salida = PRIVADO / f"por_etiquetar_{dt.date.today().isoformat()}.csv"
    with salida.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        for i in sorted(elegidos, key=lambda c: -entropia[c]):
            orden = np.argsort(-P[i])
            w.writerow({"id": pool[i]["id"], "pregunta": pool[i]["pregunta"],
                        "predicho": modelo.classes_[orden[0]] if P[i, orden[0]] >= tau else m.NG,
                        "confianza": f"{P[i, orden[0]]:.2f}", "segundo": modelo.classes_[orden[1]],
                        "enrutado_produccion": pool[i]["enrutado_produccion"], "etiqueta": "", "aceptables": "", "nota": ""})
    print(f"Pool {len(pool)} | elegidas {len(elegidos)} (entropía + diversidad) | tau actual {tau}")
    print(f"CSV para etiquetar: {salida}")
    print(f"Etiquetas válidas: {', '.join(DOMINIOS)}. Guía: docs/evaluacion/GUIA_ETIQUETADO_DOMINIO.md")


def incorporar(archivo: Path):
    nuevas, errores = [], []
    with archivo.open(encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            et = (fila.get("etiqueta") or "").strip()
            if not et:
                continue
            acept = [a.strip() for a in (fila.get("aceptables") or "").split(",") if a.strip()]
            malas = [x for x in [et] + acept if x not in DOMINIOS]
            if malas:
                errores.append(f"{fila['id']}: etiqueta inválida {malas}")
                continue
            nuevas.append({"id": fila["id"], "pregunta": fila["pregunta"], "etiqueta": et,
                           "aceptables": sorted(set([et] + acept)), "nota": fila.get("nota", ""),
                           "fecha": dt.date.today().isoformat()})
    if errores:
        print("No se incorporó nada; corrige estas filas:\n  " + "\n  ".join(errores))
        return
    PRIVADO.mkdir(exist_ok=True)
    existentes = {json.loads(l)["id"] for l in ALMACEN.read_text(encoding="utf-8").splitlines()} if ALMACEN.exists() else set()
    with ALMACEN.open("a", encoding="utf-8") as f:
        for x in nuevas:
            if x["id"] not in existentes:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"Incorporadas {len(nuevas)} etiquetas a {ALMACEN}")


def estado():
    pub, priv = _etiquetado_publico(), _etiquetado_privado()
    from collections import Counter
    print(f"Etiquetas públicas: {len(pub)} | privadas (consultas reales): {len(priv)}")
    print("Por dominio:", dict(Counter(d for _, d in pub + priv).most_common()))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seleccionar")
    s.add_argument("--n", type=int, default=20)
    s.add_argument("--desde")
    s.add_argument("--extra", type=Path)
    i = sub.add_parser("incorporar")
    i.add_argument("archivo", type=Path)
    sub.add_parser("estado")
    a = ap.parse_args()
    if a.cmd == "seleccionar":
        seleccionar(a.n, a.desde, a.extra)
    elif a.cmd == "incorporar":
        incorporar(a.archivo)
    else:
        estado()


if __name__ == "__main__":
    main()
