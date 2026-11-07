"""Consolida los resultados de la corrida final y aplica la corrección de Holm (α = 0,05) a la familia de contrastes de §23.

Familia: H1, H2, H3, H4a, H4b (p-valores bootstrap bilaterales, bloques por departamento). H5 se evalúa por su regla (sin p-valor).
Imprime también el estado de cada insumo (qué terminó y qué no) para que un resultado faltante no se confunda con un resultado nulo.
"""
from __future__ import annotations

import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def leer(nombre):
    ruta = os.path.join(AQUI, nombre)
    if not os.path.exists(ruta):
        return None
    return json.load(open(ruta, encoding="utf-8"))


def main() -> None:
    h12, h3, h45 = leer("hipotesis_h1_h2.json"), leer("hipotesis_h3.json"), leer("hipotesis_h4_h5.json")
    familia = {}
    mejora = {}   # dirección del efecto: True si la candidata es MEJOR que su referencia (los p-valores son bilaterales: «significativo» también incluye ser significativamente PEOR)
    if h12:
        familia["H1 (umbral normalizado)"] = h12["H1"]["p"]; familia["H2 (umbral con covariables)"] = h12["H2"]["p"]
        mejora["H1 (umbral normalizado)"] = h12["H1"]["dif"] > 0; mejora["H2 (umbral con covariables)"] = h12["H2"]["dif"] > 0
    if h3 and "p" in h3:
        familia["H3 (susceptibilidad en log)"] = h3["p"]; mejora["H3 (susceptibilidad en log)"] = h3["dif"] > 0
    if h45:
        familia["H4a (GEV con ONI, campo)"] = h45["resumen"]["H4a"]["p"]; familia["H4b (GEV con ONI, predictiva)"] = h45["resumen"]["H4b"]["p"]
        mejora["H4a (GEV con ONI, campo)"] = h45["resumen"]["H4a"]["estadistico"] > 0.05      # fracción de estaciones con efecto frente al azar (0,05)
        mejora["H4b (GEV con ONI, predictiva)"] = h45["resumen"]["H4b"]["estadistico"] > 0.5  # fracción de estaciones donde la candidata gana frente al azar (0,5)
    print("== Estado de los insumos ==")
    for nombre, d in (("H1/H2 (umbrales)", h12), ("H3 (susceptibilidad)", h3), ("H4/H5 (crecientes)", h45)):
        print(f"  {nombre}: {'disponible' if d else 'NO disponible (no terminó o falló: ver su registro)'}")
    print("\n== Holm sobre la familia (α = 0,05) ==")
    orden = sorted(familia.items(), key=lambda kv: kv[1]); m = len(orden); sigue = True
    for i, (nombre, p) in enumerate(orden):
        aj = min(1.0, p * (m - i))
        rechaza = sigue and aj < 0.05
        sigue = rechaza
        if not rechaza:
            veredicto = "NO significativo tras Holm"
        elif mejora.get(nombre, True):
            veredicto = "significativo y la candidata MEJORA: hipótesis confirmada"
        else:
            veredicto = "significativo pero la candidata es PEOR: hipótesis NO confirmada"
        print(f"  {nombre:<36} p = {p:.4f}  p ajustado (Holm) = {aj:.4f}  -> {veredicto}")
    if not familia:
        print("  (sin p-valores disponibles)")
    if h45 and any(r.get("h5") for r in h45["estaciones"]):
        import numpy as np
        h5 = [r["h5"] for r in h45["estaciones"] if r.get("h5") and r["h5"].get("razon_ancho") is not None]
        if h5:
            dll = np.median([x["dll"] for x in h5]); rz = np.median([x["razon_ancho"] for x in h5])
            print(f"\n== H5 (regla, sin p-valor) ==  mediana Δloglik = {dll:+.2f}; mediana razón de ancho = {rz:.2f} -> {'mejora' if dll >= -0.5 and rz < 1 else 'NO mejora'}")
    print("\nNota: la corrección de Holm cubre solo estos cinco contrastes; los demás protocolos (§§15-22) se reportaron cada uno con su regla fija y deben leerse como una familia más amplia.")


if __name__ == "__main__":
    main()
