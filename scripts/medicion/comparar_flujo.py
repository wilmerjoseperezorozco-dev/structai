"""Antes/después de la fase 2 de #221 en el pórtico, alternado en la misma corrida (docs/LATENCIA_CADENAS.md, «Cómo leer»).

Cada variante corre en su propio proceso, contra su propio árbol de código, y las variantes se turnan ronda a ronda para que la
carga de la máquina (que cambió hasta ~1,8× en un mismo día) caiga por igual en todas:

  * ``antes``      árbol de referencia (p. ej. un worktree de origin/master): sin vectorizar y sin caché.
  * ``sin_cache``  esta rama, vaciando la caché antes de cada petición: lo que paga una petición nueva.
  * ``con_cache``  esta rama, repitiendo la misma solicitud: aciertos de caché.

Además compara byte a byte la respuesta de las tres variantes (criterio preregistrado: cero diferencias de resultado).

    python scripts/medicion/comparar_flujo.py --antes C:/ruta/worktree-master --rondas 6 --por-ronda 5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))

from medir_cadenas import ENTORNO_PRUEBA, SOL_PORTICO  # noqa: E402

ENDPOINTS = {"portico-integral": SOL_PORTICO}


def _hijo(raiz: Path, variante: str, n: int, endpoint: str) -> dict:
    """Corre dentro del proceso hijo: carga la API del árbol `raiz` y mide n peticiones (más una de calentamiento)."""
    for k, v in ENTORNO_PRUEBA.items():
        os.environ[k] = v
    sys.path.insert(0, str(raiz / "apps" / "api"))
    sys.path.insert(0, str(raiz / "packages" / "construdata"))
    from pasos import sin_red_externa
    with sin_red_externa():
        import main
        if os.environ["SUPABASE_URL"] != ENTORNO_PRUEBA["SUPABASE_URL"]:
            raise RuntimeError("SUPABASE_URL no es la de prueba: se aborta para no tocar producción")
        main.limiter.enabled = False
        from auth import AuthenticatedUser, get_current_user
        from fastapi.testclient import TestClient
        main.app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id="u-medicion-local", email=None)
        api = sys.modules.get("routers.orquestador_api")
        cache = getattr(api, "CACHE_PORTICO", None)
        if variante != "antes" and cache is None:
            raise RuntimeError(f"{raiz} no tiene la caché del flujo: ¿es el árbol de la fase 2?")
        cli = TestClient(main.app)
        cuerpo = ENDPOINTS[endpoint]
        ruta = f"/orquestador/{endpoint}"
        r0 = cli.post(ruta, json=cuerpo)                          # calentamiento (y, con caché, la primera escritura)
        if r0.status_code != 200:
            raise RuntimeError(f"{ruta} respondió {r0.status_code}: {r0.text[:300]}")
        ms = []
        for _ in range(n):
            if variante == "sin_cache":
                cache._datos.clear()
            t = time.perf_counter()
            r = cli.post(ruta, json=cuerpo)
            ms.append((time.perf_counter() - t) * 1000)
            if r.content != r0.content:
                raise RuntimeError("la respuesta cambió entre peticiones idénticas")
    return {"ms": ms, "sha": hashlib.sha256(r0.content).hexdigest()}


def _percentil(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    i = int(k)
    return xs[i] + (xs[min(i + 1, len(xs) - 1)] - xs[i]) * (k - i)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", type=Path, required=True, help="árbol de referencia (worktree de origin/master)")
    ap.add_argument("--rondas", type=int, default=6)
    ap.add_argument("--por-ronda", type=int, default=5)
    ap.add_argument("--endpoint", default="portico-integral", choices=sorted(ENDPOINTS))
    ap.add_argument("--hijo", nargs=3, metavar=("RAIZ", "VARIANTE", "N"), help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.hijo:
        print(json.dumps(_hijo(Path(a.hijo[0]), a.hijo[1], int(a.hijo[2]), a.endpoint)))
        return
    arboles = {"antes": a.antes.resolve(), "sin_cache": RAIZ, "con_cache": RAIZ}
    datos = {v: [] for v in arboles}
    shas = {v: set() for v in arboles}
    for ronda in range(a.rondas):
        orden = list(arboles) if ronda % 2 == 0 else list(reversed(arboles))   # también se alterna quién va primero
        for v in orden:
            out = subprocess.run([sys.executable, __file__, "--endpoint", a.endpoint, "--antes", str(a.antes),
                                  "--hijo", str(arboles[v]), v, str(a.por_ronda)], capture_output=True, text=True, check=False)
            if out.returncode != 0:
                raise SystemExit(f"{v} falló:\n{out.stderr[-2000:]}")
            r = json.loads(out.stdout.strip().splitlines()[-1])
            datos[v] += r["ms"]
            shas[v].add(r["sha"])
        print(f"ronda {ronda + 1}/{a.rondas}", flush=True)
    res = {v: {"n": len(x), "p50_ms": round(_percentil(x, .5), 2), "p95_ms": round(_percentil(x, .95), 2)} for v, x in datos.items()}
    base = res["antes"]["p95_ms"]
    for v in res:
        res[v]["p95_vs_antes"] = round(res[v]["p95_ms"] / base - 1, 4)
    todas = set().union(*shas.values())
    salida = {"endpoint": a.endpoint, "rondas": a.rondas, "por_ronda": a.por_ronda, "variantes": res,
              "respuestas_identicas": len(todas) == 1, "sha_respuesta": sorted(todas)}
    print(json.dumps(salida, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
