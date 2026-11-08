"""NSR-10 Apéndice A-4: Aa, Av, Ae, Ad por municipio (datos locales, sin conexión).

Fuente: data/nsr10_a4_municipios.json, generado por scripts/ingesta/nsr10/generar_snapshot_a4.py
(texto original Decreto 926 de 2010 + 29 modificaciones del Decreto 092 de 2011; idéntico a la tabla
nsr10_apendice_a4_municipios de Supabase: 1.117 municipios). Posteriores sin verificar.

Zonas (A.2.3): Baja = Aa y Av ≤ 0,10; Alta = Aa o Av > 0,20; Intermedia = el resto.
Módulo autónomo (solo biblioteca estándar) para poder cargarse desde otros paquetes.
"""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "data" / "nsr10_a4_municipios.json"

# Capacidad mínima de disipación de energía por zona (Título A; verificado para estructuras de acero en F.3.2.1.1,
# mismo esquema A.3 para concreto: C.1.1.9.1). Debe confirmarse con el sistema estructural y grupo de uso reales.
CAPACIDAD_MINIMA = {"Baja": "DMI", "Intermedia": "DMO", "Alta": "DES"}


class MunicipioNoEncontrado(LookupError):
    pass


def _norm(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii").lower().strip()


@lru_cache(maxsize=1)
def _datos() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def zona_por_coeficientes(aa: float, av: float) -> str:
    """A.2.3.1 a A.2.3.3."""
    if aa > 0.20 or av > 0.20:
        return "Alta"
    if aa <= 0.10 and av <= 0.10:
        return "Baja"
    return "Intermedia"


def buscar(municipio: str | None = None, departamento: str | None = None, codigo: str | None = None) -> dict:
    """Devuelve la fila A-4 del municipio. Exige departamento (o código DANE) si el nombre es ambiguo."""
    filas = _datos()["municipios"]
    if codigo:
        for f in filas:
            if f["codigo"] == codigo:
                return _con_meta(f)
        raise MunicipioNoEncontrado(f"Código DANE {codigo} no está en el Apéndice A-4")
    if not municipio:
        raise ValueError("Indique municipio o codigo")
    n = _norm(municipio)
    hallados = [f for f in filas if _norm(f["municipio"]) == n]
    if departamento:
        hallados = [f for f in hallados if _norm(f["departamento"]) == _norm(departamento)]
    if not hallados:
        raise MunicipioNoEncontrado(f"Municipio '{municipio}' no está en el Apéndice A-4 (nombre exacto, sin tildes opcional)")
    if len(hallados) > 1:
        op = ", ".join(f"{f['municipio']} ({f['departamento']}, {f['codigo']})" for f in hallados)
        raise MunicipioNoEncontrado(f"Nombre ambiguo; indique departamento o código: {op}")
    return _con_meta(hallados[0])


def _con_meta(f: dict) -> dict:
    d = _datos()
    zona = zona_por_coeficientes(f["aa"], f["av"])
    return {**f, "zona_calculada": zona, "capacidad_minima": CAPACIDAD_MINIMA[zona], "fuente": d["fuente"], "vigencia": d["vigencia"]}
