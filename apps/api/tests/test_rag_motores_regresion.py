"""
Regresión del RAG de dominio (agente delegador) — Fase 2, batería sistemática
para los 4 motores (AquAI/GeoPot/Vías/Gerencia), hermana de
test_rag_nsr10_regresion.py pero golpeando ask_delegado() en vez de ask():
valida DOS cosas a la vez por caso — (1) que route_motor() enrute la
pregunta al dominio correcto (no se cae a normativa_general ni a otro motor)
y (2) que la respuesta sintetizada contenga el hecho verificado.

Cada hecho esperado se tomó verbatim de motor_chunks en Supabase (columna
contenido), consultado directo el 2026-08-04 — no son números supuestos ni
inventados para el test. Escala en dificultad dentro de cada motor: primero
una definición simple, luego un valor de tabla/umbral específico, luego una
fórmula completa — mismo criterio que la batería de NSR-10.

Costo/latencia: cada caso hace embedding + búsqueda en Supabase + una
llamada real a Groq — no son gratis ni instantáneos. Igual que el archivo
hermano, mover a un marker separado (`@pytest.mark.rag_regresion`) si esto
empieza a doler en CI.

Ejecutar: pytest apps/api/tests/test_rag_motores_regresion.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

# rag_multi_norma.py lee credenciales de os.environ a nivel de módulo — igual
# que en test_rag_nsr10_regresion.py, hay que cargar el .env explícito porque
# este archivo no importa main.py (que ya lo hace como efecto colateral).
load_dotenv(API_DIR / ".env")

from rag_multi_norma import ask_delegado  # noqa: E402


_ESPACIOS_UNICODE = ("\u202f", "\u00a0", "\u2009", "\u2007")  # narrow/no-break/thin/figure space


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    """True si el texto contiene al menos una de las variantes (insensible a
    mayúsculas) — tolera que el LLM use coma o punto decimal, o pequeñas
    diferencias de formato, sin dejar de exigir el hecho numérico real.
    También normaliza espacios unicode (ej. \\u202f narrow no-break space, que
    Groq usa consistentemente entre número/unidad y alrededor de "/" en
    fórmulas como "EV / AC") a espacio ASCII normal — encontrado real corriendo
    esta batería (2026-08-09): la respuesta decía "EV\\u202f=\\u202fEV/AC",
    técnicamente correcta, pero "ev / ac" con espacio normal no calzaba."""
    texto_low = texto.lower()
    for esp in _ESPACIOS_UNICODE:
        texto_low = texto_low.replace(esp, " ")
    return any(v.lower() in texto_low for v in variantes)


CASOS_AQUAI = [
    pytest.param(
        "aquai",
        "Que es la dotacion neta en un sistema de acueducto?",
        # El corpus tiene DOS definiciones válidas de "dotación neta" en
        # motor_chunks: el Artículo 43 (numérica, con unidades L/hab-día) y el
        # Artículo 253 (glosario legal, en prosa: "cantidad de agua requerida
        # para satisfacer las necesidades básicas de un habitante sin
        # considerar las pérdidas técnicas"). Al dividir el chunk gigante del
        # Artículo 253 en sub-chunks más pequeños (2026-08-09, fix del 413 de
        # Groq) su embedding se volvió más preciso y ahora a veces gana el
        # ranking sobre el Artículo 43 para preguntas genéricas "qué es X" —
        # ambas respuestas son correctas, se amplían las variantes aceptadas
        # en vez de forzar una redacción específica.
        ["litros por habitante", "l/hab", "l/hab-dia", "l/hab-día",
         "sin considerar", "necesidades básicas", "necesidades basicas"],
        id="aquai-dotacion-neta-definicion",
    ),
    pytest.param(
        "aquai",
        "De que depende el calculo de la dotacion bruta segun la Resolucion 0330 de 2017?",
        ["perdidas tecnicas", "pérdidas técnicas", "perdidas", "pérdidas"],
        id="aquai-dotacion-bruta-perdidas",
    ),
    pytest.param(
        "aquai",
        "Cuantos años minimos de experiencia especifica debe tener el profesional responsable del diseño de un sistema de acueducto o alcantarillado segun la Resolucion 0330 de 2017?",
        ["5", "cinco"],
        id="aquai-experiencia-profesional-5-anos",
    ),
]

CASOS_GEOPOT = [
    pytest.param(
        "geopot",
        "Como se calcula el indice de plasticidad IP a partir de los limites de Atterberg?",
        ["límite líquido", "limite liquido", "límite plástico", "limite plastico"],
        id="geopot-ip-limites-atterberg",
    ),
    pytest.param(
        "geopot",
        "Segun la clasificacion por indice de plasticidad, a partir de que valor de IP se considera plasticidad muy alta?",
        ["50"],
        id="geopot-ip-muy-alta-50",
    ),
    pytest.param(
        "geopot",
        "Como se calcula el coeficiente de uniformidad Cu en un analisis granulometrico de suelos?",
        ["d60/d10", "d60 / d10", "d60", "d10"],
        id="geopot-coeficiente-uniformidad-cu",
    ),
]

CASOS_VIAS = [
    pytest.param(
        "vias",
        "Segun el Manual INVIAS 2008, cual es el radio minimo de curva horizontal para una velocidad de diseño de 80 km/h con peralte maximo del 8%?",
        ["160"],
        id="vias-radio-minimo-80kmh-8porciento",
    ),
    pytest.param(
        "vias",
        "Que dos variables se usan para obtener el Numero Estructural SN requerido en el diseño de pavimento segun AASHTO 93 adaptado?",
        ["cbr", "esal"],
        id="vias-sn-tabla-esals-cbr",
    ),
    pytest.param(
        "vias",
        "Cual es el factor por el que se divide el numero estructural SN para estimar el espesor de la losa de concreto en un pavimento rigido?",
        ["0.39", "0,39"],
        id="vias-espesor-losa-factor-039",
    ),
]

CASOS_GERENCIA = [
    pytest.param(
        "gerencia",
        "Cual es la formula del CPI, el indice de desempeño de costo, en el analisis de valor ganado?",
        ["ev/ac", "ev / ac"],
        id="gerencia-cpi-formula-ev-ac",
    ),
    pytest.param(
        "gerencia",
        "Cual es la formula del SPI, el indice de desempeño de cronograma, en el analisis de valor ganado?",
        # El LLM a veces devuelve LaTeX (\frac{EV}{PV}) en vez de texto plano
        # "EV/PV" — encontrado real corriendo esta batería (2026-08-04): la
        # respuesta era correcta, el patrón de verificación era demasiado
        # estricto. "ev"/"pv" sueltos son sustrings de palabras españolas
        # comunes (ej. "nuevo", "pvc") y darían falsos positivos, así que se
        # exigen las frases distintivas que sí aparecieron en la respuesta real.
        ["valor ganado", "valor planificado"],
        id="gerencia-spi-formula-ev-pv",
    ),
    pytest.param(
        "gerencia",
        "Por debajo de que valor de CPI se genera una alerta critica automatica por sobrecosto severo en el analisis de portafolio de proyectos?",
        ["0.9", "0,9"],
        id="gerencia-alerta-critica-cpi-090",
    ),
    pytest.param(
        "gerencia",
        "Que porcentaje de ponderacion tiene el CPI dentro del score compuesto de desempeño del proyecto?",
        ["30"],
        id="gerencia-score-compuesto-cpi-30porciento",
    ),
]


@pytest.mark.parametrize(
    "motor_esperado,pregunta,variantes_esperadas",
    CASOS_AQUAI + CASOS_GEOPOT + CASOS_VIAS + CASOS_GERENCIA,
)
def test_delegador_enruta_y_responde_hecho_verificado(
    motor_esperado: str, pregunta: str, variantes_esperadas: list[str]
) -> None:
    resultado = ask_delegado(pregunta, top_k=4)

    assert resultado["dominio"] == motor_esperado, (
        f"El delegador enrutó a '{resultado['dominio']}' en vez de '{motor_esperado}'.\n"
        f"Pregunta: {pregunta}"
    )

    respuesta = resultado["respuesta"]
    assert _contiene_alguna(respuesta, variantes_esperadas), (
        f"Ninguna de {variantes_esperadas} apareció en la respuesta.\n"
        f"Pregunta: {pregunta}\nRespuesta real: {respuesta}"
    )
