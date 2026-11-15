"""
Sabotaje controlado del contexto (#169, fase F del plan): ¿el modelo responde con lo recuperado o con su memoria?

Sobre los 125 casos NSR-10 (los mismos de la batería), se altera SOLO el texto que recibe el LLM; recuperación,
enrutamiento y prompts quedan idénticos a producción. Dos modos, fijados antes de correr:

  quitar   se eliminan del contexto las líneas que contienen el hecho esperado (variantes del test).
           Correcto: abstenerse o decir que no está. Si responde el valor real → lo sacó de su memoria
           (respuesta no fundamentada, aunque sea "correcta").
  falsear  el número del hecho se reemplaza en el contexto por uno falso (×1,37, mismo formato).
           Fiel al contexto: repite el falso. Si da el valor real → ignoró el contexto (memoria por encima del
           documento). Ni uno ni otro → otra cosa (abstención o error).

Los casos donde el hecho no aparece en el contexto, o no es numérico (en falsear), se marcan "no_aplica".
Harness: el de correr_bateria.py (ventana 16384, keepalive propio de WSL, reintentos, nunca graba con Ollama caído).
Caché: resultados/sabotaje_<modelo>.jsonl (retoma si se corta).

Uso: python sabotaje.py --modelo qwen2.5:7b [--modos quitar falsear] [--resumen]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import correr_bateria as cb      # fija RAG_CACHE_DISABLED y NUM_CTX antes de importar rag_multi_norma

r = cb.r
AQUI = Path(__file__).parent
RX_ABSTENCION = re.compile(r"no (se )?(encontr|dispon|tengo|cuento|aparece|est[aá] (en|disponible|especificad|indicad))|"
                           r"no (hay|existe) (informaci|un valor|dato)|no (se )?(menciona|especifica|indica|precisa)|"
                           r"no puedo (confirmar|determinar|dar|precisar)|fuera del contexto|sin informaci", re.I)
RX_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def falso(v: str) -> str | None:
    """Mismo texto con su número multiplicado por 1,37 y el mismo separador decimal. None si no es numérico."""
    m = RX_NUM.search(v)
    if not m:
        return None
    txt = m.group(0)
    sep = "," if "," in txt else "."
    dec = len(txt.split(sep)[1]) if sep in txt else 0
    x = float(txt.replace(",", "."))
    y = round(x * 1.37, max(dec, 1 if x * 1.37 % 1 else 0))
    nuevo = f"{y:.{max(dec, 1 if y % 1 else 0)}f}".replace(".", sep)
    if nuevo == txt:
        return None
    return v[:m.start()] + nuevo + v[m.end():]


def sabotear(texto: str, variantes: list[str], modo: str, contiene) -> tuple[str, int, dict]:
    """Devuelve (texto alterado, nº de cambios, mapa variante→falso)."""
    if modo == "quitar":
        lineas = texto.split("\n")
        quedan = [l for l in lineas if not contiene(l, variantes)]
        return "\n".join(quedan), len(lineas) - len(quedan), {}
    cambios, mapa = 0, {}
    for v in sorted(variantes, key=len, reverse=True):
        f = falso(v)
        if not f:
            continue
        patron = re.compile(r"(?<![\d.,])" + re.escape(v) + r"(?![\d])", re.I)
        texto, n = patron.subn(f, texto)
        if n:
            cambios += n
            mapa[v] = f
    return texto, cambios, mapa


def generador_saboteado(modelo: str, modo: str, variantes: list[str], contiene, estado: dict):
    base = cb.generador_local(modelo)

    def llamar(messages: list, max_tokens_groq: int = 700) -> str:
        nuevos = []
        for m in messages:
            if m["role"] == "system":
                nuevos.append(m)
                continue
            c, n, mapa = sabotear(m["content"], variantes, modo, contiene)
            estado["cambios"] += n
            estado["mapa"].update(mapa)
            nuevos.append({**m, "content": c})
        return base(nuevos, max_tokens_groq)
    return llamar


def clasificar(modo: str, resp: str, variantes: list[str], mapa: dict, contiene) -> str:
    real = contiene(resp, variantes)
    if modo == "quitar":
        if real:
            return "da_el_valor_sin_contexto"
        return "se_abstiene" if RX_ABSTENCION.search(resp) else "otra_respuesta"
    fals = any(f.lower() in resp.lower() for f in mapa.values())
    if fals and not real:
        return "fiel_al_contexto_falso"
    if real and not fals:
        return "ignora_el_contexto"
    if real and fals:
        return "da_ambos"
    return "se_abstiene" if RX_ABSTENCION.search(resp) else "otra_respuesta"


def correr(modelo: str, modos: list[str], maximo: int | None = None, salida_nombre: str | None = None) -> None:
    salida = AQUI / "resultados" / (salida_nombre or f"sabotaje_{modelo.replace(':', '_')}.jsonl")
    hechos = {json.loads(l)["clave"] for l in salida.read_text(encoding="utf-8").splitlines()} if salida.exists() else set()
    casos = cb.cargar_casos("nsr10")[:maximo] if maximo else cb.cargar_casos("nsr10")
    total = len(casos) * len(modos)
    k = 0
    for modo in modos:
        for c in casos:
            k += 1
            clave = hashlib.sha1(f"{modo}|{c['id']}|{c['pregunta']}".encode()).hexdigest()[:16]
            if clave in hechos:
                continue
            if not any(RX_NUM.search(v) for v in c["variantes"]):
                # Hecho no numérico (p. ej. "no", "nivel máximo"): quitar borraría líneas con palabras genéricas y
                # falsear no tiene qué cambiar. Se registra sin llamar al LLM.
                with salida.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"clave": clave, "id": c["id"], "modo": modo, "modelo": modelo,
                                         "resultado": "no_aplica", "motivo": "hecho no numérico"}, ensure_ascii=False) + "\n")
                continue
            for intento in range(cb.REINTENTOS_CASO + 1):
                cb.esperar_ollama()
                estado = {"cambios": 0, "mapa": {}}
                r._llamar_llm_con_respaldo = generador_saboteado(modelo, modo, c["variantes"], c["contiene"], estado)
                cb._ultima.clear()
                t = time.time()
                fila = {"clave": clave, "id": c["id"], "modo": modo, "modelo": modelo, "num_ctx": cb.NUM_CTX}
                try:
                    resp = r.ask(c["pregunta"]).get("respuesta", "")
                    fila["respuesta"] = resp
                except Exception as e:  # noqa: BLE001
                    resp = ""
                    fila["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                if not cb._ultima.get("fallo_conexion"):
                    break
            else:
                raise cb.OllamaCaido(f"{c['id']}: conexión inestable")
            fila["cambios_en_contexto"] = estado["cambios"]
            fila["falsos"] = estado["mapa"]
            if estado["cambios"] == 0:
                fila["resultado"] = "no_aplica"
            elif "error" in fila:
                fila["resultado"] = "error"
            else:
                fila["resultado"] = clasificar(modo, resp, c["variantes"], estado["mapa"], c["contiene"])
            fila["segundos_total"] = round(time.time() - t, 1)
            fila["tokens_prompt"] = cb._ultima.get("tokens_prompt")
            fila["prompt_truncado"] = cb._ultima.get("prompt_truncado")
            with salida.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
            print(f"[{k}/{total}] {modo:8s} {c['id'][:42]:42s} {fila['resultado']:26s} {fila['segundos_total']:6.1f}s", flush=True)


def resumen(modelo: str, nombre: str | None = None) -> str:
    salida = AQUI / "resultados" / (nombre or f"sabotaje_{modelo.replace(':', '_')}.jsonl")
    if not salida.exists():
        return f"(sin resultados todavía en {salida.name})"
    filas = [json.loads(l) for l in salida.read_text(encoding="utf-8").splitlines()]
    L = [f"# Sabotaje controlado del contexto — {modelo} (#169)", "",
         "Generado por `sabotaje.py`. Ver el docstring para la definición de cada modo y resultado.", ""]
    for modo in ("quitar", "falsear"):
        fs = [f for f in filas if f["modo"] == modo]
        if not fs:
            continue
        c = Counter(f["resultado"] for f in fs)
        aplica = sum(v for k, v in c.items() if k not in ("no_aplica", "error"))
        L += [f"## Modo {modo} ({len(fs)} casos; aplica a {aplica})", "", "| Resultado | Casos | % de los que aplica |", "|---|---|---|"]
        for res, v in c.most_common():
            L.append(f"| {res} | {v} | {v / aplica:.0%} |" if res not in ("no_aplica", "error") and aplica else f"| {res} | {v} | — |")
        L.append("")
    texto = "\n".join(L) + "\n"
    (AQUI / f"SABOTAJE_{modelo.replace(':', '_')}.md").write_text(texto, encoding="utf-8")
    return texto


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    ap.add_argument("--modos", nargs="+", default=["quitar", "falsear"])
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--max", type=int, help="solo los primeros N casos (prueba rápida; escribe a un archivo aparte)")
    a = ap.parse_args()
    if not a.resumen:
        try:
            if a.max:
                nombre = f"sabotaje_prueba_{a.modelo.replace(':', '_')}.jsonl"
                correr(a.modelo, a.modos, a.max, nombre)
                print(resumen(a.modelo, nombre))
                return
            correr(a.modelo, a.modos)
        except cb.OllamaCaido as e:
            print(f"CORTADO: {e}. Relanzar retoma.", flush=True)
            print(resumen(a.modelo))
            sys.exit(4)
    print(resumen(a.modelo))


if __name__ == "__main__":
    main()
