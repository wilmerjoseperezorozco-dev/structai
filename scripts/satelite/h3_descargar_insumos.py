"""Paso 1 de H3 (#273): baja de Supabase (solo lectura) y del DIVIPOLA los insumos y los guarda en _cache/h3_insumos.json.
No calcula nada. Se corre con el entorno que tiene supabase (apps/api/.venv), con python -I.
Paso 2: h3_socavacion_puentes.py (entorno con pandas)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "construdata"))
ENV = Path(r"C:\Users\wilme\dev\structai\apps\api\.env")
SALIDA = AQUI / "_cache" / "h3_insumos.json"


def _paginar(sb, tabla: str, cols: str) -> list[dict]:
    filas, ini = [], 0
    while True:
        p = sb.table(tabla).select(cols).range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            return filas
        ini += 1000


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from dotenv import dotenv_values
    from supabase import create_client

    import divipola
    env = dotenv_values(ENV)
    sb = create_client(env["SUPABASE_URL"], env["SUPABASE_SERVICE_KEY"])
    datos = {
        "ungrd": _paginar(sb, "ungrd_emergencias", "fecha,evento,codigo_municipio,puentes_vehiculares,puentes_peatonales"),
        "estaciones": _paginar(sb, "ideam_estaciones_caudal", "codigo,latitud,longitud"),
        "a4": _paginar(sb, "nsr10_apendice_a4_municipios", "codigo,aa"),
        "centroides": [{"codigo": m["codigo_municipio"], "lat": m["latitud"], "lon": m["longitud"]}
                       for m in divipola._cargar_cache()],
    }
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    print({k: len(v) for k, v in datos.items()})


if __name__ == "__main__":
    main()
