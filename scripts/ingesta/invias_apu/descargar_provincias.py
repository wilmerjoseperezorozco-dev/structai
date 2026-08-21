"""
Descarga en lote los archivos Excel de APU Regionalizados de INVIAS para un
conjunto de departamentos, usando la API en vivo para resolver los códigos
de provincia reales (nunca adivinar nombres/códigos a mano).

Uso:
  python descargar_provincias.py <carpeta_destino> <codigo_depto_1> [<codigo_depto_2> ...]
  python descargar_provincias.py ./caribe 08 13 20 23 44 47 70 88

Ver invias_apu_client.py para el patrón de la API y
cargar_invias_apu.py para el patrón de nombre de archivo/URL.
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / "packages" / "construdata"))
import invias_apu_client as invias  # noqa: E402

BASE_DESCARGA = "https://hermes2.invias.gov.co/APUs/Provincias"
ANIO = "2026"
PERIODO = "1"


def _slug_sin_tildes(s: str) -> str:
    # La API de INVIAS trae algunos nombres de provincia con espacio final
    # real en el dato (ej. "Sur " en Cesar) -- strip() antes de todo, si no
    # el nombre de archivo queda con doble guion bajo y el 404 correspondiente.
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", s.strip()) if unicodedata.category(c) != "Mn"
    )
    return sin_tildes.upper().strip().replace(" ", "_")


def descargar_departamento(codigo_departamento: str, destino: Path) -> list[str]:
    cobertura = invias.verificar_cobertura_departamento(codigo_departamento)
    if not cobertura["tiene_datos"]:
        print(f"  [AVISO] departamento {codigo_departamento}: sin datos en la API de INVIAS, saltado")
        return []

    descargados = []
    for prov in cobertura["provincias_encontradas"]:
        depto_slug = _slug_sin_tildes(prov["departamento"])
        prov_slug = _slug_sin_tildes(prov["provincia"])
        nombre_archivo = f"APU_{prov['codigo']}_{depto_slug}__{prov_slug}_{ANIO}_{PERIODO}.xlsx"
        url = f"{BASE_DESCARGA}/{ANIO}_{PERIODO}/{nombre_archivo}"
        ruta_destino = destino / nombre_archivo

        resp = httpx.get(url, timeout=60.0)
        if resp.status_code != 200:
            print(f"  [FALLO {resp.status_code}] {nombre_archivo} -- {url}")
            continue

        ruta_destino.write_bytes(resp.content)
        tam_mb = len(resp.content) / (1024 * 1024)
        print(f"  OK  {nombre_archivo}  ({tam_mb:.1f} MB)")
        descargados.append(nombre_archivo)

    return descargados


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    codigos_depto = sys.argv[2:]

    total = 0
    for codigo in codigos_depto:
        print(f"\n=== Departamento {codigo} ===")
        descargados = descargar_departamento(codigo, destino)
        total += len(descargados)

    print(f"\nListo. {total} archivo(s) descargado(s) en {destino}")


if __name__ == "__main__":
    main()
