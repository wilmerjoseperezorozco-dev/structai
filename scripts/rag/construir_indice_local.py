"""Construye la instantánea del corpus RAG para la búsqueda híbrida en memoria (packages/construdata/indice_local.py).

    python scripts/rag/construir_indice_local.py [--si-cambio] [--env apps/api/.env]

* UNA lectura de solo lectura por la API REST de Supabase: los 5 corpus (nsr10_chunks, ntc_chunks, motor_chunks,
  peru_e030_chunks, ecuador_nec_se_ds_chunks) con su embedding, más normas_registro para la vigencia.
* Escribe ``apps/api/datos_indice/indice_rag.npz`` + ``.manifiesto.json`` (sha256). La carpeta está en .gitignore (el
  texto de las normas no va a un repositorio público) pero NO en .gcloudignore/.dockerignore: viaja en la imagen y el
  arranque en frío de Cloud Run la lee del disco, sin egress de Supabase.
* ``--si-cambio``: compara antes la huella barata de cada tabla (conteo + último created_at/updated_at) con la del
  manifiesto y, si nada cambió, no vuelve a descargar. Lo usa infra/gcp/desplegar.sh antes de construir la imagen.
* La clave se lee del .env y nunca se imprime.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
from indice_local import CORPUS, IndiceLocal, construir_archivo  # noqa: E402

DESTINO = RAIZ / "apps" / "api" / "datos_indice" / "indice_rag.npz"

# corpus -> (tabla, columna norma, columna contenido, tiene motor, tiene norma_id)
TABLAS = {
    "nsr10": ("nsr10_chunks", "capitulo", "texto", False, True),
    "ntc": ("ntc_chunks", "norma", "contenido", False, True),
    "motor": ("motor_chunks", "norma_ref", "contenido", True, True),
    "peru": ("peru_e030_chunks", "capitulo", "texto", False, False),
    "ecuador": ("ecuador_nec_se_ds_chunks", "capitulo", "texto", False, False),
}
PAGINA = 500


def _cliente(archivo_env: Path) -> tuple[httpx.Client, str]:
    env = {**dotenv_values(archivo_env), **{k: v for k, v in os.environ.items() if k.startswith("SUPABASE_")}}
    url, clave = env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_KEY")
    if not url or not clave:
        raise SystemExit(f"Faltan SUPABASE_URL / SUPABASE_SERVICE_KEY en {archivo_env}")
    return httpx.Client(headers={"apikey": clave, "Authorization": f"Bearer {clave}"}, timeout=180), url.rstrip("/")


def _conteo(cli, url, tabla) -> int:
    r = cli.get(f"{url}/rest/v1/{tabla}", params={"select": "id", "limit": "1"}, headers={"Prefer": "count=exact"})
    r.raise_for_status()
    return int(r.headers["content-range"].split("/")[-1])


def _ultimo(cli, url, tabla, col) -> str | None:
    r = cli.get(f"{url}/rest/v1/{tabla}", params={"select": col, "order": f"{col}.desc.nullslast", "limit": "1"})
    r.raise_for_status()
    d = r.json()
    return d[0][col] if d else None


def huella(cli, url) -> dict:
    h = {t: {"filas": _conteo(cli, url, t), "ultimo": _ultimo(cli, url, t, "created_at")} for t, *_ in TABLAS.values()}
    h["normas_registro"] = {"filas": _conteo(cli, url, "normas_registro"),
                            "ultimo": _ultimo(cli, url, "normas_registro", "updated_at")}
    return h


def _leer(cli, url, tabla, columnas) -> list[dict]:
    filas, ini = [], 0
    while True:
        r = cli.get(f"{url}/rest/v1/{tabla}", params={"select": columnas, "order": "id.asc", "offset": str(ini),
                                                      "limit": str(PAGINA)})
        r.raise_for_status()
        p = r.json()
        filas += p
        if len(p) < PAGINA:
            return filas
        ini += PAGINA


def construir(archivo_env: Path, destino: Path, si_cambio: bool) -> dict | None:
    cli, url = _cliente(archivo_env)
    h = huella(cli, url)
    man_ruta = destino.with_suffix(".manifiesto.json")
    if si_cambio and destino.exists() and man_ruta.exists():
        if json.loads(man_ruta.read_text(encoding="utf-8")).get("huella_supabase") == h:
            print("Índice local al día: las tablas no cambiaron desde la última instantánea.")
            return None
    filas = []
    for corpus, (tabla, c_norma, c_cont, con_motor, con_nid) in TABLAS.items():
        cols = ["id", c_norma, "seccion", c_cont, "embedding"] + (["motor"] if con_motor else []) + (["norma_id"] if con_nid else [])
        datos = _leer(cli, url, tabla, ",".join(cols))
        if len(datos) != h[tabla]["filas"]:
            raise SystemExit(f"{tabla}: se leyeron {len(datos)} filas y la base tiene {h[tabla]['filas']}")
        for d in datos:
            e = d.get("embedding")
            filas.append({"corpus": corpus, "id": str(d["id"]), "norma": d.get(c_norma), "seccion": d.get("seccion"),
                          "contenido": d.get(c_cont), "motor": d.get("motor"), "norma_id": d.get("norma_id"),
                          "embedding": json.loads(e) if isinstance(e, str) else e})
        print(f"  {tabla}: {len(datos):,} filas", flush=True)
    normas = {n["id"]: {k: n.get(k) for k in ("nombre_completo", "estado_vigencia", "derogada_por", "alcance_derogacion")}
              for n in _leer(cli, url, "normas_registro", "id,nombre_completo,estado_vigencia,derogada_por,alcance_derogacion")}
    man = construir_archivo(filas, normas, destino, {"huella_supabase": h})
    print(json.dumps({k: man[k] for k in ("filas_por_corpus", "lexemas", "bytes", "sha256")}, indent=2, ensure_ascii=False))
    return man


def rehacer_sin_red(destino: Path) -> dict:
    """Recalcula el índice léxico desde la instantánea existente (mismo texto y embeddings), sin tocar Supabase. Sirve
    cuando cambia el analizador de indice_local.py."""
    idx = IndiceLocal.cargar(destino)
    filas = [{"corpus": CORPUS[int(idx.corpus[i])], "id": idx.ids[i], "norma": idx.normas[i], "seccion": idx.secciones[i],
              "contenido": idx.contenidos[i], "motor": idx.motores[i], "norma_id": idx.norma_ids[i],
              "embedding": idx.emb[i] if idx.tiene_emb[i] else None} for i in range(idx.n)]
    man = construir_archivo(filas, idx.normas_registro, destino, {"huella_supabase": idx.manifiesto["huella_supabase"]})
    print(json.dumps({k: man[k] for k in ("filas_por_corpus", "lexemas", "bytes", "sha256")}, indent=2, ensure_ascii=False))
    return man


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", type=Path, default=RAIZ / "apps" / "api" / ".env")
    ap.add_argument("--destino", type=Path, default=DESTINO)
    ap.add_argument("--si-cambio", action="store_true")
    ap.add_argument("--sin-red", action="store_true", help="rehace el índice léxico desde la instantánea existente")
    a = ap.parse_args()
    if a.sin_red:
        rehacer_sin_red(a.destino)
    else:
        construir(a.env, a.destino, a.si_cambio)


if __name__ == "__main__":
    main()
