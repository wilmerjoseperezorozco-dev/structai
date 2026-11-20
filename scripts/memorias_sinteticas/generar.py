"""Laboratorio de memorias de cálculo sintéticas (#275, F1): muestreo Sobol del espacio de edificios de pórticos de concreto
→ edificio más barato que cumple (optimizar_edificio_3d) → memoria de cálculo F0 + fila del corpus.

Todos los rangos son SUPUESTOS del espacio de diseño colombiano (ver MANIFIESTO, que se escribe junto al CSV); la malla
no está ponderada por el inventario real. Capacidad de disipación: la mínima que permite la zona de amenaza
(A.2.3: alta si Aa o Av > 0,20; intermedia si > 0,10; Tabla A.3-3: DMO no se permite en zona alta) → DES / DMO / DMI.
Uso:  python scripts/memorias_sinteticas/generar.py --m 11 [--hilos 8] [--hasta 22:40] [--salida data/memorias_sinteticas]
      (n = 2**m casos; reanudable: salta los id ya escritos; un prefijo de 2**k de Sobol sigue siendo un diseño válido)
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 275
DIMS = 12
PERFILES = ("C", "D", "E")
USOS = {"residencial": (1.8, "I"), "oficinas": (2.0, "I"), "educativo": (2.0, "III")}   # L (kN/m², B.4.2.1-1), grupo (A.2.5.1)
FC = (21.0, 28.0, 35.0)
RANGOS = {"N": (3, 12), "vanos_x": (2, 5), "vanos_y": (2, 4), "Lx_m": (4.0, 8.0), "Ly_m": (4.0, 8.0), "hp_m": (2.7, 3.5),
          "Aa": (0.05, 0.40), "Av_sobre_Aa": (0.75, 1.25), "perfil": PERFILES, "uso": tuple(USOS), "D_kpa": (5.0, 8.0), "fc_mpa": FC}


def _r(x, paso):
    return round(round(x / paso) * paso, 6)


def caso(i: int, u) -> dict:
    ent = lambda v, a, b: a + min(int(v * (b - a + 1)), b - a)  # noqa: E731
    lin = lambda v, a, b: a + v * (b - a)                      # noqa: E731
    aa = _r(lin(u[6], *RANGOS["Aa"]), 0.05)
    av = min(0.45, max(0.05, _r(aa * lin(u[7], *RANGOS["Av_sobre_Aa"]), 0.05)))
    uso = tuple(USOS)[min(int(u[9] * 3), 2)]
    zona = "alta" if max(aa, av) > 0.20 else ("intermedia" if max(aa, av) > 0.10 else "baja")
    return {"id": i, "N": ent(u[0], *RANGOS["N"]), "vanos_x": ent(u[1], *RANGOS["vanos_x"]), "vanos_y": ent(u[2], *RANGOS["vanos_y"]),
            "Lx_m": _r(lin(u[3], *RANGOS["Lx_m"]), 0.5), "Ly_m": _r(lin(u[4], *RANGOS["Ly_m"]), 0.5),
            "hp_m": _r(lin(u[5], *RANGOS["hp_m"]), 0.1), "aa": aa, "av": av, "perfil": PERFILES[min(int(u[8] * 3), 2)],
            "uso": uso, "L_kpa": USOS[uso][0], "grupo_uso": USOS[uso][1], "D_kpa": _r(lin(u[10], *RANGOS["D_kpa"]), 0.25),
            "fc_mpa": FC[min(int(u[11] * 3), 2)], "zona": zona, "capacidad": {"alta": "DES", "intermedia": "DMO", "baja": "DMI"}[zona]}


def _iniciar():
    os.environ["OMP_NUM_THREADS"] = "1"


def _trabajo(args):
    c, salida = args
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de, optimizar_edificio_3d as op
    n = c["N"]
    base = de.ProyectoEdificio3D(
        luces_x_m=(c["Lx_m"],) * c["vanos_x"], luces_y_m=(c["Ly_m"],) * c["vanos_y"], alturas_piso_m=(c["hp_m"],) * n,
        columnas_mm=(1.0,) * n, vigas_mm=((1.0, 1.0),) * n, carga_muerta_kpa=c["D_kpa"], carga_viva_kpa=c["L_kpa"],
        aa=c["aa"], av=c["av"], perfil_suelo=c["perfil"], grupo_uso=c["grupo_uso"], capacidad=c["capacidad"],
        fc_mpa=c["fc_mpa"], nombre=f"Sintético {c['id']:05d}", uso=c["uso"])
    try:
        r = op.optimizar(base)
    except Exception as exc:                        # un caso que rompe el motor se registra, no detiene el lote
        return {**c, "estado": "error", "motivo": f"{type(exc).__name__}: {exc}"[:300]}
    fila = {**c, "estado": "ok" if r.mejor else "sin_solucion", "motivo": r.motivo_sin_solucion[:300],
            "evaluaciones_deriva": r.evaluaciones_deriva, "evaluaciones_diseno": r.evaluaciones_diseno, "segundos": round(r.segundos, 2)}
    if r.mejor is not None:
        m = r.mejor
        fila |= {"c_inferior_mm": m.proyecto.columnas_mm[0], "c_superior_mm": m.proyecto.columnas_mm[-1],
                 "b_viga_mm": m.proyecto.vigas_mm[0][0], "h_viga_mm": m.proyecto.vigas_mm[0][1]}
        fila |= {f"y_{k}": v for k, v in m.memoria.caracteristicas.items() if k not in c and k not in ("cumple",)}
        with gzip.open(Path(salida) / "memorias" / f"{c['id']:05d}.json.gz", "wt", encoding="utf-8") as f:
            f.write(m.memoria.a_json())
    return fila


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=9)
    ap.add_argument("--hilos", type=int, default=8)
    ap.add_argument("--hasta", default=None, help="HH:MM: no se reparten casos nuevos después de esta hora")
    ap.add_argument("--salida", default=str(RAIZ / "data" / "memorias_sinteticas"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    from scipy.stats import qmc
    out = Path(a.salida)
    (out / "memorias").mkdir(parents=True, exist_ok=True)
    U = qmc.Sobol(d=DIMS, scramble=True, seed=SEMILLA).random(2 ** a.m)
    ruta = out / "corpus.csv"
    hechos = set()
    if ruta.exists():
        with ruta.open(encoding="utf-8") as f:
            hechos = {int(r["id"]) for r in csv.DictReader(f)}
    pendientes = [(caso(i, U[i]), str(out)) for i in range(len(U)) if i not in hechos]
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    (out / "MANIFIESTO.json").write_text(json.dumps({
        "issue": 275, "fase": "F1", "muestreo": "Sobol scramble", "semilla": SEMILLA, "n_objetivo": 2 ** a.m, "dims": DIMS,
        "rangos_SUPUESTOS": {k: list(v) for k, v in RANGOS.items()}, "usos": USOS,
        "capacidad": "mínima permitida por la zona (A.2.3, Tabla A.3-3)", "optimizador": "orquestador.optimizar_edificio_3d",
        "commit": sha, "actualizado": datetime.now().isoformat(timespec="seconds"),
        "advertencia": "Malla sin ponderación por inventario; diseños óptimos de una rejilla declarada, no diseños de ingenieros."},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(hechos)} hechos, {len(pendientes)} pendientes, {a.hilos} procesos", flush=True)
    limite = None
    if a.hasta:
        hh, mm = map(int, a.hasta.split(":"))
        limite = datetime.now().replace(hour=hh, minute=mm, second=0)
    campos = None
    t0, k = time.time(), 0
    os.environ["OMP_NUM_THREADS"] = "1"
    with Pool(a.hilos, initializer=_iniciar) as pool, \
            ruta.open("a", encoding="utf-8", newline="") as f:
        nuevo = not hechos
        for fila in pool.imap_unordered(_trabajo, pendientes, chunksize=1):
            if campos is None:
                campos = _CAMPOS
                w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
                if nuevo:
                    w.writeheader()
            w.writerow(fila)
            f.flush()
            k += 1
            if k % 25 == 0:
                print(f"{k}/{len(pendientes)} en {time.time() - t0:.0f} s", flush=True)
            if limite and datetime.now() >= limite:
                print("hora límite: se detiene (reanudable)", flush=True)
                pool.terminate()
                break
    print(f"listo: {k} casos en {time.time() - t0:.0f} s", flush=True)


_CAMPOS = ["id", "N", "vanos_x", "vanos_y", "Lx_m", "Ly_m", "hp_m", "aa", "av", "perfil", "uso", "L_kpa", "grupo_uso", "D_kpa", "fc_mpa",
           "zona", "capacidad", "estado", "motivo", "evaluaciones_deriva", "evaluaciones_diseno", "segundos",
           "c_inferior_mm", "c_superior_mm", "b_viga_mm", "h_viga_mm"]
_Y = ["y_T_modelo_x_s", "y_T_x_s", "y_Vs_W", "y_uso_deriva", "y_Qi_max", "y_acero_kg_m2", "y_concreto_m3_m2", "y_costo_cop_m2",
      "y_co2_kg_m2", "y_altura_total_m"]
_CAMPOS += [c for c in _Y if c not in _CAMPOS]

if __name__ == "__main__":
    main()
