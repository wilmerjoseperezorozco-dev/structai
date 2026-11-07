"""Ubicacion de EJECUCION de los contratos de obra (SECOP II, gra4-pcp2). Mejora el limite de
"ciudad de la entidad != sitio de obra" de la hipotesis 1.

PRIVACIDAD: solo se piden id_contrato y localizaci_n. El conjunto trae tambien documento y nombre
del proveedor; NO se descargan. Datos crudos en scripts/secop/_cache/ (ignorado por git).
Reanudable. Usa la logica por lotes de extraer_obras_secop.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import extraer_obras_secop as ex  # noqa: E402


def main() -> None:
    ex.CACHE.mkdir(exist_ok=True)
    ids = [c["id_contrato"] for c in ex.contratos() if c.get("id_contrato")]
    print(f"Contratos de obra: {len(ids)}", flush=True)
    ex.por_lotes("ubicaciones", "gra4-pcp2", "id_contrato", ids, "id_contrato,localizaci_n")
    print("LISTO", flush=True)


if __name__ == "__main__":
    main()
