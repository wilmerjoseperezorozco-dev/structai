"""Respaldo exacto de una tabla de Supabase a JSONL comprimido, verificable contra la base, antes de vaciarla.

    python scripts/respaldo/respaldar_tabla.py invias_actividad_insumos --llave id --destino C:/Users/wilme/dev/respaldos/supabase

* Lee por la API REST con paginación por llave (``llave > último``, ordenado por la llave): sin saltos ni duplicados aunque
  la tabla sea grande, y cada página usa el índice de la llave primaria.
* Los ``numeric`` se guardan como TEXTO decimal exacto (se parsean con Decimal, nunca con float): el respaldo reproduce los
  valores bit a bit al recargarlos.
* Escribe ``<tabla>_<fecha>.jsonl.gz`` y ``<tabla>_<fecha>.manifiesto.json`` con conteo, md5 de las llaves en orden (mismo
  cálculo que ``md5(string_agg(id::text, ',' order by id))`` en Postgres), sumas exactas de las columnas numéricas y sha256
  del archivo. Las columnas ``double precision`` (``--float``) se suman redondeadas a 15 cifras significativas, igual que
  ``sum(col::numeric)`` en Postgres; ``--md5-texto a|b|c`` agrega el md5 de esas columnas unidas por ``|`` en orden de la
  llave, como ``md5(string_agg(a || '|' || b::text || '|' || coalesce(c,''), ',' order by id))``. Con ``--verificar-contra`` compara el manifiesto con la huella calculada en la base y falla si algo difiere.
* La clave se lee de ``apps/api/.env`` (``SUPABASE_URL``, ``SUPABASE_SERVICE_KEY``) y nunca se imprime. Solo lectura.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import httpx
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parents[2]


def _cliente(archivo_env: Path) -> tuple[httpx.Client, str]:
    env = {**dotenv_values(archivo_env), **{k: v for k, v in os.environ.items() if k.startswith("SUPABASE_")}}
    url, clave = env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_KEY")
    if not url or not clave:
        raise SystemExit(f"Faltan SUPABASE_URL / SUPABASE_SERVICE_KEY en {archivo_env}")
    return httpx.Client(headers={"apikey": clave, "Authorization": f"Bearer {clave}"}, timeout=120), url.rstrip("/")


def _texto_decimal(x):
    return format(x, "f") if isinstance(x, Decimal) else x


def respaldar(tabla: str, llave: str, destino: Path, archivo_env: Path, pagina: int = 1000,
              columnas_float: tuple[str, ...] = (), md5_texto: tuple[str, ...] = ()) -> dict:
    cli, url = _cliente(archivo_env)
    destino.mkdir(parents=True, exist_ok=True)
    fecha = dt.date.today().isoformat()
    archivo = destino / f"{tabla}_{fecha}.jsonl.gz"
    md5_llaves, md5_txt, n, ultimo = hashlib.md5(), hashlib.md5(), 0, None
    sumas: dict[str, Decimal] = {}
    primera = True
    with gzip.open(archivo, "wt", encoding="utf-8", compresslevel=9) as gz:
        while True:
            params = {"select": "*", "order": f"{llave}.asc", "limit": str(pagina)}
            if ultimo is not None:
                params[llave] = f"gt.{ultimo}"
            r = cli.get(f"{url}/rest/v1/{tabla}", params=params)
            r.raise_for_status()
            filas = json.loads(r.text, parse_float=Decimal)
            if not filas:
                break
            for f in filas:
                for k, v in f.items():
                    if isinstance(v, (Decimal, int)) and not isinstance(v, bool) and k != llave:
                        x = Decimal(format(float(v), ".15g")) if k in columnas_float else Decimal(v)
                        sumas[k] = sumas.get(k, Decimal(0)) + x
                sep = b"" if primera else b","
                md5_llaves.update(sep + str(f[llave]).encode())
                if md5_texto:
                    md5_txt.update(sep + "|".join("" if f[c] is None else str(f[c]) for c in md5_texto).encode("utf-8"))
                primera = False
                gz.write(json.dumps({k: _texto_decimal(v) for k, v in f.items()}, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += len(filas)
            ultimo = filas[-1][llave]
            if n % 50000 < pagina:
                print(f"  {n:,} filas", flush=True)
            if len(filas) < pagina:
                break
    sha = hashlib.sha256(archivo.read_bytes()).hexdigest()
    man = {"tabla": tabla, "fecha": fecha, "llave": llave, "filas": n, "md5_llaves": md5_llaves.hexdigest(),
           "sumas": {k: format(v, "f") for k, v in sorted(sumas.items())}, "archivo": archivo.name,
           "bytes": archivo.stat().st_size, "sha256": sha,
           **({"md5_texto": md5_txt.hexdigest(), "columnas_md5_texto": list(md5_texto)} if md5_texto else {}),
           **({"columnas_float_15g": list(columnas_float)} if columnas_float else {}),
           "formato": "JSONL gzip; una fila por línea; numeric como texto decimal exacto"}
    (destino / f"{tabla}_{fecha}.manifiesto.json").write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    return man


def verificar(man: dict, huella_bd: dict) -> list[str]:
    """Diferencias entre el manifiesto y la huella calculada en Postgres (vacía = respaldo fiel)."""
    errores = []
    if man["filas"] != int(huella_bd["n"]):
        errores.append(f"filas: respaldo {man['filas']} vs base {huella_bd['n']}")
    if man["md5_llaves"] != huella_bd["md5_ids"]:
        errores.append("md5 de las llaves distinto")
    if "md5_texto" in huella_bd and man.get("md5_texto") != huella_bd["md5_texto"]:
        errores.append("md5 de las columnas de texto distinto")
    for col, valor in huella_bd.get("sumas", {}).items():
        if Decimal(man["sumas"].get(col, "0")) != Decimal(valor):
            errores.append(f"suma de {col}: respaldo {man['sumas'].get(col)} vs base {valor}")
    return errores


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tabla")
    ap.add_argument("--llave", default="id")
    ap.add_argument("--destino", type=Path, required=True)
    ap.add_argument("--env", type=Path, default=RAIZ / "apps" / "api" / ".env", help="archivo con SUPABASE_URL y SUPABASE_SERVICE_KEY")
    ap.add_argument("--verificar-contra", type=Path, help="JSON con la huella de la base: {n, md5_ids, sumas: {col: texto}}")
    ap.add_argument("--float", default="", help="columnas double precision, separadas por coma")
    ap.add_argument("--md5-texto", default="", help="columnas a|b|c para el md5 de texto")
    a = ap.parse_args()
    man = respaldar(a.tabla, a.llave, a.destino, a.env, columnas_float=tuple(c for c in a.float.split(",") if c),
                    md5_texto=tuple(c for c in a.md5_texto.split("|") if c))
    print(json.dumps({k: man[k] for k in ("filas", "md5_llaves", "bytes", "sha256")}, indent=2))
    if a.verificar_contra:
        errores = verificar(man, json.loads(a.verificar_contra.read_text(encoding="utf-8")))
        if errores:
            print("RESPALDO NO COINCIDE CON LA BASE:\n  " + "\n  ".join(errores))
            sys.exit(1)
        print("OK: respaldo idéntico a la base (conteo, md5 de llaves y sumas exactas)")


if __name__ == "__main__":
    main()
