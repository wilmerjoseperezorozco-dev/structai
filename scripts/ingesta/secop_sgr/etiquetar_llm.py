"""
Etiquetado de PLATA con un LLM local (Ollama en WSL) del objeto de contratos de obra de SECOP II. Sin APIs externas.

Qué hace: para una muestra estratificada pide al modelo, en JSON, el tipo de obra, la etapa constructiva principal
y, si el texto la trae, la cantidad con su unidad. Es una etiqueta AUTOMÁTICA (plata): sirve para entrenar un
clasificador rápido y para estimar cuántos contratos traen cantidades, pero su calidad se mide contra una muestra
etiquetada por una persona (regla de #171 y #196). Nunca se mezcla con conjuntos de prueba humanos.

Muestra: 300 contratos que las palabras clave dejaron "sin clasificar" + 100 ya clasificados (para medir el
acuerdo LLM ↔ palabras clave). Semilla fija. Caché por contrato: si se corta, retoma.

Uso: python scripts/ingesta/secop_sgr/etiquetar_llm.py [--modelo qwen2.5:7b] [--n-sin 300] [--n-con 100]
Salida: scripts/ingesta/secop_sgr/salida/llm_<modelo>.jsonl
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
import time
from pathlib import Path

import httpx

AQUI = Path(__file__).resolve().parent
RAW = AQUI / "raw" / "secop2_contratos_obra.csv"
LIMPIO = AQUI / "salida" / "secop2_contratos_obra_limpio.csv"
OLLAMA = "http://127.0.0.1:11434"
TIPOS = ["vía terciaria / placa huella", "pavimentación urbana / vías", "puente", "acueducto / alcantarillado / saneamiento",
         "edificación educativa", "vivienda", "salud", "deportivo / espacio público", "edificación institucional / otra",
         "mantenimiento o reparación de edificación", "obras de mitigación / contención / drenaje", "electrificación / alumbrado",
         "otro"]
ETAPAS = ["obra negra / estructura", "instalaciones (obra gris)", "acabados (obra blanca)", "urbanismo / exteriores / vías",
          "redes externas", "obra completa (varias etapas)", "mantenimiento / reparación", "no aplica"]
SISTEMA = ("Eres un ingeniero civil colombiano. Clasificas el objeto de un contrato de obra pública. Responde SOLO un "
           "JSON con las claves: tipo_obra (una de: " + "; ".join(TIPOS) + "), etapa (una de: " + "; ".join(ETAPAS) +
           "), cantidad (número o null, SOLO si el texto dice explícitamente una cantidad física de obra, p. ej. "
           "'1.200 metros'), unidad (km, ml, m2, m3, un o null). No inventes cantidades.")


def keepalive():
    try:
        return subprocess.Popen(["wsl.exe", "-d", "Ubuntu", "--", "sleep", "infinity"], stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return None


def esperar_ollama(seg=300):
    t = time.time()
    while time.time() - t < seg:
        try:
            if httpx.get(f"{OLLAMA}/api/version", timeout=5).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(5)
    raise SystemExit("Ollama no responde")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    ap.add_argument("--n-sin", type=int, default=300)
    ap.add_argument("--n-con", type=int, default=100)
    a = ap.parse_args()
    with LIMPIO.open(encoding="utf-8") as fh:
        limpio = {r["id_contrato"]: r for r in csv.DictReader(fh)}
    with RAW.open(encoding="utf-8") as fh:
        texto = {r["id_contrato"]: f"{r['objeto_del_contrato']} {r['descripcion_del_proceso']}".strip()
                 for r in csv.DictReader(fh) if r["id_contrato"] in limpio}
    rnd = random.Random(7)
    sin = [i for i, r in limpio.items() if r["tipo_obra"] == "otro / sin clasificar" and len(texto.get(i, "")) > 20]
    con = [i for i, r in limpio.items() if r["tipo_obra"] != "otro / sin clasificar" and len(texto.get(i, "")) > 20]
    muestra = [(i, "sin") for i in rnd.sample(sin, min(a.n_sin, len(sin)))] + \
              [(i, "con") for i in rnd.sample(con, min(a.n_con, len(con)))]
    salida = AQUI / "salida" / f"llm_{a.modelo.replace(':', '_')}.jsonl"
    hechos = {json.loads(l)["id_contrato"] for l in salida.read_text(encoding="utf-8").splitlines()} if salida.exists() else set()
    ka = keepalive()
    esperar_ollama()
    cli = httpx.Client(timeout=600)
    try:
        for k, (i, estrato) in enumerate(muestra, 1):
            if i in hechos:
                continue
            t0 = time.time()
            r = cli.post(f"{OLLAMA}/api/chat", json={
                "model": a.modelo, "stream": False, "format": "json",
                "options": {"temperature": 0, "num_ctx": 2048, "num_predict": 120},
                "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": texto[i][:1200]}]}).json()
            try:
                et = json.loads(r["message"]["content"])
            except (KeyError, json.JSONDecodeError):
                et = {"error": "respuesta no JSON"}
            fila = {"id_contrato": i, "estrato": estrato, "tipo_keywords": limpio[i]["tipo_obra"], "modelo": a.modelo,
                    "llm": et, "segundos": round(time.time() - t0, 1), "valor": limpio[i]["valor"],
                    "cantidad_regex": limpio[i]["cantidad"], "unidad_regex": limpio[i]["unidad_cant"]}
            with salida.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
            print(f"[{k}/{len(muestra)}] {estrato} {fila['segundos']}s -> {et.get('tipo_obra')} | {et.get('cantidad')} {et.get('unidad')}", flush=True)
    finally:
        if ka:
            ka.terminate()


if __name__ == "__main__":
    sys.exit(main())
