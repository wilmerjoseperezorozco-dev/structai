"""Reintenta los casos del lote 2026-09-29 que fallaron por el limite de
tokens-por-minuto de Groq, con pausa mas larga (25s, seguro para 8000 TPM
con llamadas de ~5000 tokens cada una)."""
import io
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.environ["RAG_CACHE_DISABLED"] = "true"
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import rag_multi_norma as rm

OUT_DIR = PROJECT_ROOT / "scripts" / "evaluacion" / "qlora_export"

CASOS = [
    {
        "id": "ADV-dotacion-antartida-2026-09-29",
        "categoria": "ADV",
        "pregunta": "Cual es la dotacion bruta que exige la Resolucion 0330 de 2017 para un proyecto en la Antartida?",
        "via": "ask_delegado",
        "esperado": None,
    },
    {
        "id": "ADV-concreto-arena-lunar-titulo-C-2026-09-29",
        "categoria": "ADV",
        "pregunta": "Que numeral del Titulo C regula el concreto fabricado con arena lunar?",
        "via": "ask",
        "esperado": None,
    },
    {
        "id": "COLOQ-phi-traccion-estiron-2026-09-29",
        "categoria": "COLOQ",
        "pregunta": "Que tanto hay que rebajarle a la resistencia del concreto cuando la seccion se raja por estiron, o sea por traccion, segun el Titulo C?",
        "via": "ask",
        "esperado": ["0.90", "0,90"],
    },
    {
        "id": "COLOQ-dotacion-agua-bruta-2026-09-29",
        "categoria": "COLOQ",
        "pregunta": "De que depende cuanta agua bruta hay que calcularle a un acueducto, segun la norma del 2017?",
        "via": "ask_delegado",
        "esperado": ["25", "dotaci"],
    },
    {
        "id": "COMP-recubrimiento-y-precio-concreto-2026-09-29",
        "categoria": "COMP",
        "pregunta": "Cual es el recubrimiento minimo que exige el Titulo C para concreto en contacto directo con el suelo, y cuanto cuesta el concreto en Barranquilla?",
        "via": "ask",
        "esperado": ["50"],
    },
]

FRASES_NEGATIVA = [
    "no encontr", "el contexto disponible no", "no incluye informaci",
    "no encontré información", "no tengo esa informaci", "no está en las normas",
    "no esta en las normas", "no existe", "no aplica", "no aparece",
    "ningún numeral", "ningun numeral", "ninguna referencia",
]


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def es_refusal(respuesta: str) -> bool:
    r = respuesta.lower()
    return any(f in r for f in FRASES_NEGATIVA)


def contiene_esperado(respuesta: str, esperado: list[str]) -> bool:
    r = _sin_tildes(respuesta.lower())
    return any(_sin_tildes(e.lower()) in r for e in esperado)


def main() -> None:
    promovidos, rechazados = [], []
    for i, caso in enumerate(CASOS):
        print(f"\n=== {caso['id']} ({caso['categoria']}) ===")
        print("Pregunta:", caso["pregunta"])
        try:
            if caso["via"] == "ask":
                r = rm.ask(caso["pregunta"])
            else:
                r = rm.ask_delegado(caso["pregunta"])
        except rm.RespuestaIAIndisponibleError as e:
            print(f"  -> ERROR (cuota), se omite: {e}")
            rechazados.append({**caso, "respuesta": None, "motivo": "error_cuota"})
            if i < len(CASOS) - 1:
                time.sleep(40)
            continue
        respuesta = r["respuesta"]
        print("Respuesta:", respuesta[:300])

        if caso["categoria"] == "ADV":
            if es_refusal(respuesta):
                print("  -> promovido (refusal correcta)")
                promovidos.append({**caso, "respuesta": respuesta, "motivo": "refusal_correcta"})
            else:
                print("  -> RECHAZADO (se esperaba una negativa honesta, no llego)")
                rechazados.append({**caso, "respuesta": respuesta, "motivo": "refusal_esperada_no_llego"})
        elif caso["esperado"] and contiene_esperado(respuesta, caso["esperado"]):
            print("  -> promovido (contiene el hecho verificado)")
            promovidos.append({**caso, "respuesta": respuesta, "motivo": "hecho_verificado_presente"})
        else:
            print(f"  -> RECHAZADO, no contiene ninguno de: {caso['esperado']}")
            rechazados.append({**caso, "respuesta": respuesta, "motivo": "hecho_verificado_ausente"})

        if i < len(CASOS) - 1:
            time.sleep(25)

    print(f"\n\nTotal: {len(CASOS)} | Promovidos: {len(promovidos)} | Rechazados: {len(rechazados)}")

    nuevas_filas = []
    for p in promovidos:
        nuevas_filas.append({
            "messages": [
                {"role": "system", "content": rm.SYSTEM_PROMPT},
                {"role": "user", "content": f"PREGUNTA: {p['pregunta']}"},
                {"role": "assistant", "content": p["respuesta"]},
            ],
            "_metadata": {
                "pregunta": p["pregunta"],
                "categoria": p["categoria"],
                "fuente": "lote_2026-09-29",
                "motivo_promocion": p["motivo"],
            },
        })

    train_path = OUT_DIR / "train.jsonl"
    with open(train_path, "a", encoding="utf-8") as f:
        for fila in nuevas_filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    with open(OUT_DIR / "lote_2026-09-29_reintento_rechazados.jsonl", "w", encoding="utf-8") as f:
        for r_ in rechazados:
            f.write(json.dumps(r_, ensure_ascii=False, default=str) + "\n")

    print(f"\n{len(nuevas_filas)} filas agregadas a {train_path}")


if __name__ == "__main__":
    main()
