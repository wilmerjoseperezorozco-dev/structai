"""Descarga a _cache/ las cotizaciones nacionales (apu_precios_nacional_detalle), los ítems y los proveedores. Reanudable por archivo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "satelite"))
import _datos_caribe as dc  # noqa: E402

CACHE = Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)


def bajar(tabla: str, cols: str, orden: str) -> list[dict]:
    f = CACHE / f"{tabla}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table(tabla).select(cols).order(orden).range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    f.write_text(json.dumps(filas, ensure_ascii=False, default=str), encoding="utf-8")
    return filas


if __name__ == "__main__":
    for t, c, o in (("apu_items_nacional", "*", "item_no"), ("apu_proveedores_nacional", "*", "id"),
                    ("apu_precios_nacional_detalle", "item_no,proveedor_id,precio_sin_iva,precio_valido,precio_sospechoso,fuente", "id")):
        print(t, len(bajar(t, c, o)))
