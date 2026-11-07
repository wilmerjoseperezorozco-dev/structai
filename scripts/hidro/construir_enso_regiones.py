"""Construye packages/construdata/data/enso_regiones.json para el plugin de ENSO del chat.
Fuente: scripts/hidro/coherencia_resultados.json (C2, confirmatorio) y las cifras exploratorias de anomalías bajas de RESULTADOS_COHERENCIA.md.
Uso: python construir_enso_regiones.py"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parents[1] / "packages" / "construdata" / "data" / "enso_regiones.json"
# Exploratorio (sin ajuste por múltiples pruebas): El Niño (ONI >= 0,5) frente a neutral, % de estaciones en anomalía baja por mes (RESULTADOS_COHERENCIA.md).
BAJAS = {"Amazonia": (4.2, 4.6), "Andina": (5.3, 3.3), "Caribe": (9.3, 3.5), "Orinoquia": (5.3, 4.5), "Pacifica": (5.8, 3.1)}
DEPTOS = {"ANTIOQUIA": "Andina", "BOYACA": "Andina", "CUNDINAMARCA": "Andina", "SANTANDER": "Andina", "NORTE DE SANTANDER": "Andina", "TOLIMA": "Andina",
          "HUILA": "Andina", "CALDAS": "Andina", "QUINDIO": "Andina", "RISARALDA": "Andina", "BOGOTA D.C.": "Andina", "BOGOTA": "Andina",
          "ATLANTICO": "Caribe", "BOLIVAR": "Caribe", "CESAR": "Caribe", "CORDOBA": "Caribe", "LA GUAJIRA": "Caribe", "MAGDALENA": "Caribe", "SUCRE": "Caribe",
          "CAUCA": "Pacifica", "CHOCO": "Pacifica", "NARINO": "Pacifica", "VALLE DEL CAUCA": "Pacifica",
          "META": "Orinoquia", "ARAUCA": "Orinoquia", "CASANARE": "Orinoquia", "VICHADA": "Orinoquia",
          "CAQUETA": "Amazonia", "PUTUMAYO": "Amazonia", "AMAZONAS": "Amazonia", "GUAINIA": "Amazonia", "GUAVIARE": "Amazonia", "VAUPES": "Amazonia"}
NOMBRES = {"Amazonia": "Amazonía", "Andina": "Andina", "Caribe": "Caribe", "Orinoquia": "Orinoquía", "Pacifica": "Pacífica"}


def main() -> None:
    d = json.loads((AQUI / "coherencia_resultados.json").read_text(encoding="utf-8"))["regiones"]
    reg = {}
    for r, x in d.items():
        b = BAJAS[r]
        reg[r] = {"nombre": NOMBRES[r], "estaciones": x["n_est"],
                  "altas_nina": {"nina_pct": round(100 * x["f_nina"], 1), "neutral_pct": round(100 * x["f_neutral"], 1), "dif_pp": round(100 * x["dif_nina_neutral"], 1),
                                 "ic_pp": [round(100 * x["ic_dif"][0], 1), round(100 * x["ic_dif"][1], 1)], "p_holm": round(x["holm_C2"], 3)},
                  "bajas_nino_exploratorio": {"nino_pct": b[0], "neutral_pct": b[1], "dif_pp": round(b[0] - b[1], 1)}}
    SALIDA.write_text(json.dumps({"fuente": "StructAI, scripts/hidro/coherencia_anomalias.py (610 estaciones IDEAM, 1934-2026); tag research/coherencia-anomalias",
                                  "regiones": reg, "departamentos": DEPTOS}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{SALIDA} ({SALIDA.stat().st_size} bytes); regiones: {list(reg)}")


if __name__ == "__main__":
    main()
