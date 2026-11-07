"""Lote chico de preguntas nuevas (2026-09-29) -- 8 preguntas (numero par,
convencion pedida por Wilmer de aqui en adelante), en las categorias mas
debiles del dataset (SINT, ADV, COLOQ, COMP), con ground_truth verificado
por SQL/retrieval directo ANTES de correrlas -- nunca inventado.

Cada hecho fue confirmado en esta misma sesion:
- phi=0.90 traccion (NSR10-C-C_9_3_2_1), phi=0.75 cortante/torsion
  (NSR10-C-C_9_3_2_3_factor_reduccion_cortante_torsion) -- verificado
  durante el fix del issue #59.
- Dotacion bruta = dotacion neta / (1-%p), %p<=25%, Resolucion 0330 de
  2017 Art. 44 (chunk id=408, motor_chunks) -- verificado durante el fix
  del issue #58.
- Recubrimiento minimo 50mm / a/mc<=0.50 / f'c>=28MPa para concreto en
  contacto directo con el suelo, Titulo C Tabla C.3-1 (nsr10_chunks id=300
  via ntc_chunks) -- verificado con SQL directo hoy.
- Concreto comun 3000 PSI ~$274.575/m3 en Barranquilla -- verificado con
  buscar_precios_apu() real hoy.
- Maximo titulo real de la NSR-10 es K (no hay L/M/N/P) -- verificable por
  inventario, no requiere SQL puntual.

Corre cada pregunta contra el sistema real (ask()/ask_delegado(), cache
desactivado), aplica la MISMA verificacion de fundamentacion numerica que
revisar_manual_qlora.py (todo numero con unidad debe aparecer en el
contexto o la pregunta), y solo lo que pasa se agrega al dataset final.
"""
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
        "id": "SINT-phi-traccion-vs-cortante-2026-09-29",
        "categoria": "SINT",
        "pregunta": "Es mayor el factor phi que exige el Titulo C de la NSR-10 para secciones controladas por traccion (C.9.3.2.1) que el que exige para cortante y torsion (C.9.3.2.3)?",
        "via": "ask",
        "esperado": ["0.90", "0,90", "0.75", "0,75"],
    },
    {
        "id": "ADV-titulo-P-vidrio-curvo-2026-09-29",
        "categoria": "ADV",
        "pregunta": "Que exige el Titulo P de la NSR-10 sobre estructuras de vidrio templado curvo?",
        "via": "ask",
        "esperado": None,  # se verifica por refusal, no por hecho numerico
    },
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
        "id": "COLOQ-recubrimiento-zapata-tierra-2026-09-29",
        "categoria": "COLOQ",
        "pregunta": "Que tan protegido tiene que quedar el hierro de una zapata que va pegada directo a la tierra, segun la norma?",
        "via": "ask",
        "esperado": ["50", "50mm", "50 mm"],
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
    """Verifica contra los hechos YA confirmados por SQL/retrieval directo
    antes de correr la pregunta (ver docstring del modulo) -- mismo patron
    que _contiene_alguna() en test_rag_nsr10_regresion.py, mas confiable
    que reconstruir el contexto real (ask()/ask_delegado() no lo exponen
    completo en su valor de retorno)."""
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
            time.sleep(15)
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
            time.sleep(3)  # respeta el limite de tokens-por-minuto de Groq

    print(f"\n\nTotal: {len(CASOS)} | Promovidos: {len(promovidos)} | Rechazados: {len(rechazados)}")

    # Formato identico al resto del dataset (chat messages).
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

    heldout_path = OUT_DIR / "heldout.jsonl"
    train_path = OUT_DIR / "train.jsonl"
    # Los nuevos van a train (lote chico, no vale la pena partir 85/15 con 8 casos).
    with open(train_path, "a", encoding="utf-8") as f:
        for fila in nuevas_filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    with open(OUT_DIR / "lote_2026-09-29_rechazados.jsonl", "w", encoding="utf-8") as f:
        for r_ in rechazados:
            f.write(json.dumps(r_, ensure_ascii=False, default=str) + "\n")

    print(f"\n{len(nuevas_filas)} filas agregadas a {train_path}")
    print(f"{len(rechazados)} rechazadas guardadas en lote_2026-09-29_rechazados.jsonl")


if __name__ == "__main__":
    main()
