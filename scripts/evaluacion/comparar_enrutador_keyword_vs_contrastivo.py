"""
Comparación real, medida, entre el enrutador de dominio actual
(_score_motores(), coincidencia de subcadena contra ~200 palabras clave) y
el nuevo enrutador contrastivo (motor_router_contrastivo.py, centroides de
embeddings + similitud coseno) -- ver ese archivo para el porqué.

Conjunto de prueba (SIN fuga de datos con los ejemplos de referencia del
enrutador contrastivo):
  - Las 13 preguntas reales de apps/api/tests/test_rag_motores_regresion.py
    (aquai/geopot/vias/gerencia), ya verificadas contra producción -- se
    REUTILIZAN tal cual, nunca se copiaron a EJEMPLOS_POR_DOMINIO.
  - +10 preguntas nuevas para los 5 dominios que ese archivo no cubre
    (apu_precios, vulnerabilidad_vivienda, peru_e030, ecuador_nec_se_ds,
    normativa_general), escritas con fraseo/sinónimos DISTINTOS a los
    ejemplos de referencia del enrutador contrastivo, varias a propósito
    sin ninguna palabra clave literal de MOTOR_KEYWORD_MAP -- para medir
    si el enfoque de embeddings generaliza donde el léxico no puede.

Métrica: accuracy top-1 de cada enrutador contra la etiqueta real, por
dominio y total. Se reporta tal cual salga, gane quien gane -- ningún
número se ajusta para que el enfoque nuevo quede mejor.

Uso: python scripts/evaluacion/comparar_enrutador_keyword_vs_contrastivo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))

from motor_router_contrastivo import route_motores_contrastivo  # noqa: E402
from rag_multi_norma import route_motor  # noqa: E402

# Las 13 de test_rag_motores_regresion.py (pregunta, dominio_real) -- copiadas
# de ahí SOLO como texto de la pregunta y su dominio correcto, sin tocar el
# archivo original.
CASOS_REGRESION_EXISTENTE = [
    ("Que es la dotacion neta en un sistema de acueducto?", "aquai"),
    ("De que depende el calculo de la dotacion bruta segun la Resolucion 0330 de 2017?", "aquai"),
    ("Cuantos años minimos de experiencia especifica debe tener el profesional responsable del diseño de un sistema de acueducto o alcantarillado segun la Resolucion 0330 de 2017?", "aquai"),
    ("Como se calcula el indice de plasticidad IP a partir de los limites de Atterberg?", "geopot"),
    ("Segun la clasificacion por indice de plasticidad, a partir de que valor de IP se considera plasticidad muy alta?", "geopot"),
    ("Como se calcula el coeficiente de uniformidad Cu en un analisis granulometrico de suelos?", "geopot"),
    ("Segun el Manual INVIAS 2008, cual es el radio minimo de curva horizontal para una velocidad de diseño de 80 km/h con peralte maximo del 8%?", "vias"),
    ("Que dos variables se usan para obtener el Numero Estructural SN requerido en el diseño de pavimento segun AASHTO 93 adaptado?", "vias"),
    ("Cual es el factor por el que se divide el numero estructural SN para estimar el espesor de la losa de concreto en un pavimento rigido?", "vias"),
    ("Cual es la formula del CPI, el indice de desempeño de costo, en el analisis de valor ganado?", "gerencia"),
    ("Cual es la formula del SPI, el indice de desempeño de cronograma, en el analisis de valor ganado?", "gerencia"),
    ("Por debajo de que valor de CPI se genera una alerta critica automatica por sobrecosto severo en el analisis de portafolio de proyectos?", "gerencia"),
    ("Que porcentaje de ponderacion tiene el CPI dentro del score compuesto de desempeño del proyecto?", "gerencia"),
]

# Nuevas, held-out, para los 5 dominios sin cobertura en el archivo de
# regresión -- varias deliberadamente sin la palabra clave literal, para
# probar generalización real, no solo memorización de vocabulario.
CASOS_NUEVOS = [
    # apu_precios: "quanto me sale" es coloquial, no está en MOTOR_KEYWORD_MAP
    ("Quanto me sale hacer una placa de contrapiso de 100 metros cuadrados?", "apu_precios"),
    ("Necesito saber que tan caro esta el saco de cemento esta semana", "apu_precios"),
    # vulnerabilidad_vivienda: sin usar "vulnerabilidad" ni "checklist"
    ("Tengo una casa vieja de bahareque y ladrillo, se me puede caer si tiembla fuerte?", "vulnerabilidad_vivienda"),
    ("Como se que tan preparada esta mi vivienda de dos pisos para un terremoto?", "vulnerabilidad_vivienda"),
    # peru_e030: mencionando el pais sin decir "E.030" literal
    ("Estoy diseñando un edificio en Arequipa, que norma sismica peruana debo seguir?", "peru_e030"),
    ("Cual es la clasificacion de perfiles de suelo que usa el reglamento de edificaciones del Peru?", "peru_e030"),
    # ecuador_nec_se_ds: mencionando ciudad ecuatoriana, no el código de la norma
    ("Voy a construir en Guayaquil, que exige la normativa ecuatoriana de diseño sismico?", "ecuador_nec_se_ds"),
    ("Que categoria de importancia sismica tiene un hospital en Ecuador?", "ecuador_nec_se_ds"),
    # normativa_general: preguntas de NSR-10/NTC/SGSST sin vocabulario de otros motores
    ("Cual es la altura maxima permitida antes de exigir un sistema de resistencia sismica especial en Colombia?", "normativa_general"),
    ("Que exige la ley colombiana sobre el uso de elementos de proteccion personal en una obra de construccion?", "normativa_general"),
]

TODOS_LOS_CASOS = CASOS_REGRESION_EXISTENTE + CASOS_NUEVOS


def route_combinado(pregunta: str) -> str | None:
    """El diseño real que se conecta a producción: keyword primero (rápido,
    sin costo de embedding); si no encuentra nada, se prueba el contrastivo."""
    dominio_keyword = route_motor(pregunta)
    if dominio_keyword:
        return dominio_keyword
    return route_motores_contrastivo(pregunta, top_k=1)[0][0]


def main() -> None:
    aciertos_keyword = 0
    aciertos_contrastivo = 0
    aciertos_combinado = 0
    fallos_keyword: list[tuple[str, str, str | None]] = []
    fallos_contrastivo: list[tuple[str, str, str]] = []
    fallos_combinado: list[tuple[str, str, str | None]] = []

    for pregunta, dominio_real in TODOS_LOS_CASOS:
        dominio_keyword = route_motor(pregunta)
        dominio_contrastivo = route_motores_contrastivo(pregunta, top_k=1)[0][0]
        dominio_combinado = route_combinado(pregunta)

        if dominio_keyword == dominio_real:
            aciertos_keyword += 1
        else:
            fallos_keyword.append((pregunta, dominio_real, dominio_keyword))

        if dominio_contrastivo == dominio_real:
            aciertos_contrastivo += 1
        else:
            fallos_contrastivo.append((pregunta, dominio_real, dominio_contrastivo))

        if dominio_combinado == dominio_real:
            aciertos_combinado += 1
        else:
            fallos_combinado.append((pregunta, dominio_real, dominio_combinado))

    total = len(TODOS_LOS_CASOS)
    print(f"Total de casos: {total}\n")
    print(f"Enrutador actual (keyword):           {aciertos_keyword}/{total} ({100*aciertos_keyword/total:.1f}%)")
    print(f"Enrutador nuevo (contrastivo):         {aciertos_contrastivo}/{total} ({100*aciertos_contrastivo/total:.1f}%)")
    print(f"Combinado (keyword -> contrastivo):    {aciertos_combinado}/{total} ({100*aciertos_combinado/total:.1f}%)")

    print("\n--- Fallos del enrutador keyword (actual) ---")
    for pregunta, esperado, obtenido in fallos_keyword:
        print(f"  [{esperado} -> {obtenido}] {pregunta}")

    print("\n--- Fallos del enrutador contrastivo (nuevo) ---")
    for pregunta, esperado, obtenido in fallos_contrastivo:
        print(f"  [{esperado} -> {obtenido}] {pregunta}")

    print("\n--- Fallos del combinado (el que se conecta a producción) ---")
    for pregunta, esperado, obtenido in fallos_combinado:
        print(f"  [{esperado} -> {obtenido}] {pregunta}")


if __name__ == "__main__":
    main()
