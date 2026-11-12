"""
Transcribe el held-out K6 que Wilmer escribió y etiquetó a mano (#171) a dataset_heldout_k6.jsonl.

Regla del protocolo: NO se cambia ni una palabra de las preguntas ni el sentido de una etiqueta. Solo se
normaliza la escritura de la etiqueta al identificador del enrutador. Cada fila conserva la etiqueta original.

Particularidades del archivo recibido (2026-11-12): Excel lo guardó doblemente entrecomillado (cada fila es un
texto que contiene otro CSV). Wilmer cambió algunas preguntas y puso al final las que faltaban (43, 44, 45).

Decisiones de Wilmer (2026-11-12, en la conversación):
  - tipo C = compuesta (como define la plantilla); N = negación.
  - aceptable "base de datos" → normativa_general.
  - "laboratorio(s)" → geopot (regla 5 de GUIA_ETIQUETADO_DOMINIO.md); "topovia" → vias.
El resto son variantes de escritura de un mismo dominio (tildes, guiones, espacios, errores de tipeo) o normas que
la guía asigna a un dominio (SG-SST → normativa_general; AIS 2004 → vulnerabilidad_vivienda; NSR10 →
normativa_general; INVIAS → vias).

Uso: python transcribir_heldout_k6.py <ruta_del_csv_de_wilmer>
Salida: dataset_heldout_k6.jsonl y TRANSCRIPCION_HELDOUT_K6.md (para que Wilmer revise antes de evaluar).
"""
from __future__ import annotations

import csv
import io
import json
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MAPEO = {
    "geopot": "geopot", "laboratorio": "geopot", "laboratorios": "geopot",
    "normativa general": "normativa_general", "normativageneral": "normativa_general", "nsr10": "normativa_general",
    "base de datos": "normativa_general", "sgsst": "normativa_general",
    "gerencia": "gerencia",
    "apu precios": "apu_precios", "apu-precios": "apu_precios",
    "vias": "vias", "invias": "vias", "topovia": "vias",
    "aquai": "aquai",
    "vulnerabilidad": "vulnerabilidad_vivienda", "vunerabilidad": "vulnerabilidad_vivienda",
    "ais2004": "vulnerabilidad_vivienda", "ais 2004": "vulnerabilidad_vivienda",
    "peru": "peru_e030", "peru_030": "peru_e030",
    "ecuador": "ecuador_nec_se_ds", "ecuador_nec_sd_ds": "ecuador_nec_se_ds",
}
TIPO = {"C": "compuesta", "N": "negacion"}


def clave(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().strip()
    return " ".join(s.split())


def leer(ruta: Path) -> list[dict]:
    filas = []
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines()[1:]:
        s = linea.strip()
        if not s:
            continue
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        f = next(csv.reader(io.StringIO(s.replace('""', '"'))))
        numero, resto = f[0].strip(), f[1:]
        pregunta = ",".join(resto[:-4]).strip()
        etiqueta, aceptables, tipo, nota = (x.strip() for x in resto[-4:])
        filas.append({"numero": numero, "pregunta": pregunta, "etiqueta_original": etiqueta,
                      "aceptables_original": aceptables, "tipo_original": tipo, "nota_original": nota})
    return filas


def main() -> None:
    ruta = Path(sys.argv[1])
    filas = leer(ruta)
    sin_mapeo = sorted({x for f in filas for x in (f["etiqueta_original"], f["aceptables_original"])
                        if x and clave(x) not in MAPEO})
    if sin_mapeo:
        sys.exit(f"Etiquetas sin mapeo (no se adivina): {sin_mapeo}")
    salida, md = [], ["# Transcripción del held-out K6 (#171) para revisión de Wilmer", "",
                      "Texto de las preguntas **sin cambios**. Etiqueta original → identificador del enrutador. "
                      "Revisa que el sentido sea el que quisiste antes de leer los resultados.", "",
                      "| # | Pregunta | Etiqueta (tuya → id) | Aceptables (tuya → id) | Tipo |", "|---|---|---|---|---|"]
    for f in filas:
        esperado = MAPEO[clave(f["etiqueta_original"])]
        acept = [esperado]
        if f["aceptables_original"]:
            a = MAPEO[clave(f["aceptables_original"])]
            if a not in acept:
                acept.append(a)
        tipo = TIPO.get(f["tipo_original"].upper(), "simple")
        salida.append({"pregunta": f["pregunta"], "esperado": esperado, "aceptables": acept,
                       "estrato": f"H_{tipo}", "cluster": f"H-{f['numero']}", "nota": f["nota_original"],
                       "id": f"K6H-{int(f['numero']):03d}", "split": "heldout", "numero_wilmer": int(f["numero"]),
                       "etiqueta_original": f["etiqueta_original"], "aceptables_original": f["aceptables_original"],
                       "tipo_original": f["tipo_original"]})
        md.append(f"| {f['numero']} | {f['pregunta'].replace('|', '/')} | {f['etiqueta_original']} → `{esperado}` | "
                  f"{f['aceptables_original'] or '—'} → {', '.join(f'`{x}`' for x in acept)} | {f['tipo_original']} ({tipo}) |")
    (AQUI / "dataset_heldout_k6.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in salida) + "\n", encoding="utf-8")
    (AQUI / "TRANSCRIPCION_HELDOUT_K6.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    from collections import Counter
    print(len(salida), "preguntas |", dict(Counter(x["esperado"] for x in salida)), "|", dict(Counter(x["estrato"] for x in salida)))


if __name__ == "__main__":
    main()
