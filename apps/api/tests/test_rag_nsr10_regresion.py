"""
Regresión del RAG NSR-10 — hechos verificados manualmente contra el PDF
oficial durante las rondas de re-extracción verbatim de Títulos A y B
(2026-08-01). Antes de esto, cada verificación vivía en un script
_audit_piloto_*.py que se creaba y se borraba en la sesión — una corrección
de hoy podía romperse en silencio mañana al insertar contenido nuevo, sin
que nadie se enterara hasta que un usuario preguntara mal.

Estos tests golpean el pipeline real (Supabase pgvector + Groq), no mocks —
verifican que el contenido siga existiendo Y siga siendo recuperado en el
top-k, que es exactamente el modo de falla real encontrado varias veces
esta sesión (contenido correcto en la base pero perdido contra un chunk de
otro título en la búsqueda por similitud).

Costo/latencia: cada caso hace una llamada real a Groq — no son gratis ni
instantáneos. Si esto empieza a doler en tiempo de CI, migrar a un marker
separado (`@pytest.mark.rag_regresion`) para correrlos aparte del resto.

Ejecutar: pytest apps/api/tests/test_rag_nsr10_regresion.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

# rag_multi_norma.py lee credenciales de os.environ a nivel de módulo — a
# diferencia de test_endpoints.py, este archivo no importa main.py (que ya
# carga el .env como efecto colateral), así que hay que cargarlo explícito.
# En CI (test-api de ci.yml) estas vienen de GitHub Secrets, no de un .env.
load_dotenv(API_DIR / ".env")

from rag_multi_norma import ask  # noqa: E402

# Cada caso hace una llamada real a Groq -- el LLM a veces redacta la misma
# respuesta correcta con palabras distintas entre corridas (encontrado real
# en CI 2026-08-15: B-biblioteca-estanterias-7kNm2 esperaba "7.0"/"7,0" y la
# respuesta usó otro formato). Reintentar 1 vez filtra ese ruido sin ocultar
# una regresión real de contenido, que fallaría en ambos intentos.
pytestmark = pytest.mark.flaky(reruns=1, reruns_delay=3)


# narrow/no-break/thin/figure space -- encontrado real en CI 2026-08-17: Groq
# respondió "7 kN/m²" (espacio angosto entre el número y la unidad) y
# esta función, a diferencia de su hermana en test_rag_motores_regresion.py,
# nunca normalizaba espacios unicode -- pasaba de largo aunque el rerun de
# pytest-rerunfailures ya se hubiera gastado en otro caso de la misma corrida.
_ESPACIOS_UNICODE = (" ", " ", " ", " ")


def _contiene_alguna(texto: str, variantes: list[str]) -> bool:
    """True si el texto contiene al menos una de las variantes (insensible a
    mayúsculas) — tolera que el LLM use coma o punto decimal, o pequeñas
    diferencias de formato, sin dejar de exigir el hecho numérico real."""
    texto_low = texto.lower()
    for esp in _ESPACIOS_UNICODE:
        texto_low = texto_low.replace(esp, " ")
    return any(v.lower() in texto_low for v in variantes)


CASOS_TITULO_B = [
    pytest.param(
        "El Titulo B trata directamente las fuerzas sismicas de diseño?",
        ["no", "título a", "titulo a"],
        id="B-viento-no-es-sismo",
    ),
    pytest.param(
        "Segun la tabla de carga viva de la NSR-10, cual es la carga viva para estanterias en una biblioteca?",
        # El corpus real dice "7.0 kN/m²" pero Groq a veces redondea a un
        # entero en la redacción ("7 kN/m²", sin decimales) -- mismo hecho
        # numérico, otra forma de escribirlo. Se acepta también "7 kn/m"
        # (tras normalizar espacios unicode) para no depender de que el LLM
        # siempre incluya el ".0"/",0".
        ["7.0", "7,0", "7 kn/m"],
        id="B-biblioteca-estanterias-7kNm2",
    ),
    pytest.param(
        "Cual es la carga minima de diseño por viento en el SPRFV segun la NSR-10?",
        ["0.40", "0,40", "0.4 ", "0,4 "],
        id="B-viento-minimo-040",
    ),
]

CASOS_TITULO_A = [
    pytest.param(
        "Cuales son los 4 sistemas estructurales de resistencia sismica que reconoce la NSR-10?",
        ["muros de carga", "sistema dual"],
        id="A-4-sistemas-estructurales",
    ),
    pytest.param(
        "En el analisis dinamico, el cortante dinamico total en la base no puede ser menor a que porcentaje del cortante de la fuerza horizontal equivalente, para estructuras regulares e irregulares?",
        ["80", "90"],
        id="A-ajuste-dinamico-80-90",
    ),
    pytest.param(
        "Cuales son los valores de Aa y Av para Barranquilla segun la NSR-10?",
        ["0.10", "0,10"],
        id="A-Aa-Av-Barranquilla",
    ),
    pytest.param(
        "Cual es la deriva maxima permitida como porcentaje de la altura de piso para una estructura de concreto reforzado?",
        ["1.0%", "1%", "1,0%", "0.010", "0,010"],
        id="A-deriva-maxima-1-porciento",
    ),
]

CASOS_TITULO_C = [
    pytest.param(
        "Cual es la resistencia minima a la compresion f'c que exige la NSR-10 para el concreto estructural?",
        ["17"],
        id="C-fc-minimo-general-17MPa",
    ),
    pytest.param(
        "Cual es la resistencia minima a la compresion del concreto para estructuras con capacidad de disipacion de energia especial DES o moderada DMO?",
        ["21"],
        id="C-fc-minimo-DMO-DES-21MPa",
    ),
    pytest.param(
        "Cual es el recubrimiento minimo cuando el concreto esta colocado contra el suelo y expuesto permanentemente a el?",
        ["75"],
        id="C-recubrimiento-contacto-suelo-75mm",
    ),
    pytest.param(
        "Cuales son los factores de reduccion de resistencia phi para secciones controladas por traccion y para cortante?",
        ["0.90", "0,90"],
        # Este caso estuvo marcado xfail (2026-08-27) por una causa raíz real:
        # search_knowledge() ataba el pool interno de las ramas semántica y
        # léxica (LIMIT match_count*3) al match_count del LLAMADOR, dando una
        # posición distinta e inestable al mismo chunk según cuánto se pidiera
        # (NSR10-C-C_9_3_2_1: ausente en match_count 30/40, #44 en 50, #45 en
        # 60, #24 en 100 -- verificado en vivo). Fix real aplicado el mismo
        # día en la migración search_knowledge (Supabase): pool interno fijo
        # (300), desacoplado de match_count. Verificado tras el fix: posición
        # #1 estable en match_count 30/40/50/60/100, y este test pasa de
        # verdad (XPASS, sin xfail) contra el pipeline real. Ver
        # [[project_structai_ragas_baseline]] en memoria para el detalle
        # completo de la investigación.
        id="C-factor-phi-traccion-090",
    ),
    pytest.param(
        "Cual es el angulo de doblez de los ganchos sismicos en estribos de confinamiento para estructuras DMO y DES?",
        ["135"],
        id="C-ganchos-sismicos-135grados",
    ),
    pytest.param(
        "Cual es la cuantia maxima de refuerzo a flexion permitida en vigas de porticos resistentes a momento con capacidad especial DES segun el Titulo C?",
        ["0.025", "0,025", "2.5%", "2,5%"],
        id="C-cuantia-maxima-flexion-DES-0025",
    ),
    pytest.param(
        "Cual es el valor maximo de fyt que se puede usar para calcular la cuantia del refuerzo de confinamiento segun el Titulo C?",
        ["700"],
        id="C-fyt-maximo-confinamiento-700MPa",
    ),
    pytest.param(
        "Cual es el espaciamiento maximo del refuerzo en diafragmas estructurales de concreto, excepto losas post-tensadas, segun el Titulo C?",
        ["450"],
        id="C-diafragmas-espaciamiento-max-450mm",
    ),
]

# Ampliación 2026-08-27 (ida de 12 a 50 preguntas) -- mismos hechos ya
# verificados leyendo directamente el PDF oficial verbatim ya cargado en
# nsr10_chunks/ntc_chunks (no se inventa nada nuevo, se extiende la misma
# disciplina a los títulos que ya están verbatim: D, E, G, y a los chunks
# de precisión ya existentes en A/F/J/K). Ver [[project_structai_ragas_baseline]].
CASOS_TITULO_D = [
    pytest.param(
        "A partir de que area construida es obligatoria la supervision tecnica en una estructura de mamposteria segun el Titulo D?",
        ["3000"],
        id="D-supervision-tecnica-3000m2",
    ),
    pytest.param(
        "Cual es el valor minimo absoluto de resistencia a la compresion del mortero de relleno a los 28 dias segun el Titulo D, sin importar la resistencia de la mamposteria?",
        ["12.5", "12,5"],
        id="D-mortero-relleno-minimo-125MPa",
    ),
    pytest.param(
        "Que porcentaje maximo del area de la seccion transversal pueden ocupar las celdas verticales en una unidad de mamposteria de perforacion vertical segun el Titulo D?",
        ["65"],
        id="D-celdas-verticales-max-65porciento",
    ),
    pytest.param(
        "Cual es el diametro minimo de refuerzo permitido en celdas de mamposteria inyectadas con mortero segun el Titulo D?",
        ["3/8", "10m", "10 mm", "n° 3", "n°3", "no. 3"],
        id="D-diametro-minimo-refuerzo-celdas-10mm",
    ),
    pytest.param(
        "Cual es el espesor minimo nominal de un muro de mamposteria NO reforzada segun el Titulo D?",
        ["120"],
        id="D-espesor-minimo-no-reforzada-120mm",
    ),
    pytest.param(
        "En que condicion de amenaza sismica se permite usar mamposteria no reforzada como sistema de resistencia sismica segun el Titulo D?",
        ["0.05", "0,05", "baja"],
        id="D-no-reforzada-zona-baja-Aa-005",
    ),
    pytest.param(
        "En que dimension de probetas se mide la resistencia a la compresion de los morteros de pega tipo H M S o N segun el Titulo D?",
        ["50 mm", "50mm", "75 mm", "75mm"],
        id="D-morteros-probetas-cubos-50mm",
    ),
]

CASOS_TITULO_E = [
    pytest.param(
        "Cual es la resistencia minima a compresion a los 28 dias del mortero de pega en mamposteria confinada segun el Titulo E?",
        ["7.5", "7,5"],
        id="E-mortero-pega-75MPa",
    ),
    pytest.param(
        "Cual es el espesor minimo nominal de un muro estructural en zona sismica alta para una casa de dos pisos, primer nivel, segun el Titulo E?",
        ["110"],
        id="E-espesor-muro-zona-alta-2pisos-110mm",
    ),
    pytest.param(
        "Cual es el area transversal minima de las columnas de confinamiento en mamposteria confinada segun el Titulo E?",
        ["20 000", "20000", "200 cm", "200cm"],
        id="E-columnas-confinamiento-area-20000mm2",
    ),
]

CASOS_TITULO_G = [
    pytest.param(
        "Cuantos pies tablares tiene un metro cubico de madera segun el Titulo G?",
        ["424"],
        id="G-m3-424-pies-tablares",
    ),
    pytest.param(
        "Cual es el contenido de humedad maximo permitido para madera estructural en general, y para madera laminada, segun el Titulo G?",
        ["19", "12"],
        id="G-humedad-madera-estructural-19-12porciento",
    ),
    pytest.param(
        "Se permiten las uniones clavadas en elementos de guadua segun el Titulo G?",
        ["no", "prohib", "grietas"],
        id="G-guadua-uniones-clavadas-prohibidas",
    ),
    pytest.param(
        "Para que contenido de humedad maximo son representativas las cargas admisibles de conexiones de guadua de la tabla G.12.11-2 segun el Titulo G?",
        ["19"],
        id="G-guadua-humedad-cargas-admisibles-19porciento",
    ),
]

CASOS_TITULO_A_EXTRA = [
    pytest.param(
        "Cual es la deriva maxima permitida para mamposteria con falla predominante por cortante segun el Titulo A?",
        ["0.5", "0,5"],
        id="A-deriva-mamposteria-cortante-05porciento",
    ),
]

CASOS_TITULO_F_EXTRA = [
    pytest.param(
        "Cual es la ecuacion basica de diseño DCCR para estructuras de acero segun el Titulo F?",
        ["ru", "rn", "phi"],
        id="F-DCCR-formula-Ru-phiRn",
    ),
    pytest.param(
        "Cuales son los limites de luz entre columnas y peralte total de la cercha en un Portico con Cercha Ductil (PCD) segun el Titulo F?",
        ["20", "1.8", "1,8"],
        id="F-PCD-limites-luz20m-peralte18m",
    ),
]

CASOS_TITULO_J = [
    pytest.param(
        "Cual es el area de servicio y el caudal minimo requerido por hidrante para un hospital segun el Titulo J?",
        ["500", "63"],
        id="J-hidrante-hospital-500m2-63Ls",
    ),
    pytest.param(
        "Cual es la resistencia al fuego minima en horas de un muro cortafuego en una edificacion de categoria de riesgo I segun el Titulo J?",
        ["3"],
        id="J-muro-cortafuego-categoria1-3horas",
    ),
]

CASOS_TITULO_K = [
    pytest.param(
        "Cual es la fuerza maxima requerida para abrir completamente una puerta de salida segun el Titulo K?",
        ["250"],
        id="K-fuerza-apertura-puerta-250N",
    ),
    pytest.param(
        "Por cuanto tiempo minimo debe permanecer en servicio el sistema de iluminacion de emergencia tras una falla del sistema principal segun el Titulo K?",
        ["1.5", "1,5"],
        id="K-iluminacion-emergencia-15horas",
    ),
    pytest.param(
        "Cuantas salidas minimas se requieren para una edificacion con carga de ocupacion entre 501 y 1000 personas segun el Titulo K?",
        ["3", "tres"],
        id="K-numero-salidas-501-1000-3salidas",
    ),
]

CASOS_TITULO_H = [
    pytest.param(
        "Cuantos años minimos de experiencia en diseño geotecnico de cimentaciones debe tener el profesional que dirige un estudio geotecnico segun el Titulo H?",
        ["cinco", "5"],
        id="H-experiencia-geotecnista-5anos",
    ),
    pytest.param(
        "Cual es la profundidad minima y el numero minimo de sondeos para una unidad de construccion de categoria Alta (11 a 20 niveles) segun el Titulo H?",
        ["25", "4"],
        id="H-sondeos-categoria-alta-25m-4sondeos",
    ),
    pytest.param(
        "Entre cuantos niveles y que rango de cargas de servicio define el Titulo H la categoria Media de una unidad de construccion?",
        ["4", "10", "801", "4.000", "4,000", "4000"],
        id="H-categoria-media-4a10niveles",
    ),
]

CASOS_TITULO_I = [
    pytest.param(
        "Cual es la excepcion a la obligatoriedad de supervision tecnica para casas de uno y dos pisos del Titulo E, segun el Titulo I?",
        ["15"],
        id="I-excepcion-titulo-E-15viviendas",
    ),
    pytest.param(
        "Durante cuantos años minimo debe conservar el supervisor tecnico el registro escrito de sus labores segun el Titulo I?",
        ["cinco", "5"],
        id="I-registro-supervisor-5anos",
    ),
    pytest.param(
        "Cuales son los dos grados de supervision tecnica que reconoce el Titulo I?",
        ["continua", "itinerante"],
        id="I-dos-grados-supervision-AB",
    ),
]

CASOS_TITULO_B_EXTRA = [
    pytest.param(
        "Cual es el porcentaje de incremento de carga viva por impacto para los soportes de elevadores o ascensores segun el Titulo B?",
        ["100"],
        id="B-impacto-ascensores-100porciento",
    ),
    pytest.param(
        "Cual es el valor del factor de efecto rafaga G para estructuras rigidas segun el Titulo B?",
        ["0.85", "0,85"],
        id="B-factor-rafaga-G085",
    ),
]

CASOS_NTC_SGSST = [
    pytest.param(
        "Se pueden instalar las instalaciones hidraulicas y sanitarias en la caja del ascensor o el cuarto de maquinas segun la NTC 1500?",
        ["no"],
        id="NTC1500-instalaciones-prohibidas-ascensor",
    ),
    pytest.param(
        "Entre que valores debe estar el modulo de finura del agregado fino para concreto segun la NTC 174?",
        ["2.3", "2,3", "3.1", "3,1"],
        id="NTC174-modulo-finura-23-31",
    ),
    pytest.param(
        "Cual es el tiempo minimo de fraguado inicial del cemento Portland segun la NTC 121?",
        ["45"],
        id="NTC121-fraguado-inicial-45min",
    ),
    pytest.param(
        "Cual es la multa maxima en SMMLV por no reportar un accidente de trabajo grave o mortal segun el Decreto 1072 de 2015?",
        ["1000", "1.000"],
        id="Decreto1072-multa-no-reportar-AT-1000SMMLV",
    ),
    pytest.param(
        "En cuantos meses debe completar la Fase 3 de implementacion del SG-SST una empresa grande de mas de 200 trabajadores segun el Decreto 1072 de 2015?",
        ["6"],
        id="Decreto1072-fase3-empresa-grande-6meses",
    ),
    pytest.param(
        "Cual es el porcentaje maximo de terrones de arcilla y particulas deleznables permitido en el agregado fino para concreto segun la NTC 174?",
        ["3.0", "3,0", "3%"],
        id="NTC174-terrones-arcilla-max-3porciento",
    ),
    pytest.param(
        "Cual es la expansion maxima en autoclave permitida para el cemento Portland segun la NTC 121?",
        ["0.80", "0,80", "0.8%", "0,8%"],
        id="NTC121-expansion-autoclave-08porciento",
    ),
]

# Ampliacion 2026-08-27 (continuacion, K.4.1 -- glosario de vidrios).
CASOS_TITULO_K_K4 = [
    pytest.param(
        "Que le pasa al vidrio templado (fully tempered) cuando se rompe, segun el Titulo K?",
        ["pequeños pedazos", "pequenos pedazos", "fragmenta"],
        id="K-vidrio-templado-fragmenta-pequeños-pedazos",
    ),
    pytest.param(
        "A partir de que angulo respecto a la vertical se considera un vidrio como tragaluz o claraboya segun el Titulo K?",
        ["15"],
        id="K-tragaluz-angulo-15grados",
    ),
    pytest.param(
        "Cual es la diferencia entre vidrio templado y vidrio termoendurecido segun el Titulo K?",
        ["moderada", "alta"],
        id="K-templado-vs-termoendurecido-compresion",
    ),
]

# Ampliacion 2026-08-27 (continuacion, K.4.2 -- requisitos de diseño de vidrios).
CASOS_TITULO_K_K42 = [
    pytest.param(
        "Cual es el factor de seguridad exigido para el diseño de barandas y pasamanos de vidrio segun el Titulo K?",
        ["cuatro", "4"],
        id="K-barandas-vidrio-factor-seguridad-4",
    ),
    pytest.param(
        "Se permite usar vidrios de 2 mm de espesor segun el Titulo K?",
        ["no", "prohib", "flexibilidad"],
        id="K-vidrio-2mm-prohibido",
    ),
    pytest.param(
        "Cual es el limite recomendado de probabilidad de rotura aceptable por esfuerzos termicos en vidrio segun el Titulo K?",
        ["0.8", "0,8"],
        id="K-esfuerzos-termicos-probabilidad-rotura-08porciento",
    ),
    pytest.param(
        "A partir de que inclinacion respecto a la vertical se considera un sistema vidriado como inclinado (no vertical) segun el Titulo K?",
        ["15"],
        id="K-vidrio-inclinado-mas-de-15grados",
    ),
]

# Ampliacion 2026-08-28 -- Titulo F.4.1 (Provisiones Generales de acero
# formado en frio, primera pieza real del hueco mas grande del corpus).
CASOS_TITULO_F_F41 = [
    pytest.param(
        "Cuales son los factores de resistencia phi minimos para miembros y para conexiones en un analisis racional de ingenieria de acero formado en frio segun el Titulo F?",
        ["0.80", "0,80", "0.65", "0,65"],
        id="F-analisis-racional-phi-miembros-080-conexiones-065",
    ),
    pytest.param(
        "Cual es el espesor minimo entregado permitido para acero formado en frio respecto al espesor de diseño segun el Titulo F?",
        ["95"],
        id="F-espesor-minimo-entregado-95porciento",
    ),
    pytest.param(
        "Hasta que espesor de lamina, rollo, tira o barra aplica la especificacion de estructuras de acero con perfiles formados en frio del Titulo F?",
        ["25.4", "25,4", "1 pulgada"],
        id="F-f41-alcance-espesor-maximo-254mm",
    ),
]

# Ampliacion 2026-09-01 -- Titulo F.4.2 (Elementos: anchos efectivos
# rigidizados/no rigidizados, pestana simple, rigidizadores intermedios).
# Reingestado el mismo dia en chunks chicos (~100 tokens) tras encontrar
# que el modelo de embeddings trunca a 128 tokens y los chunks grandes
# originales no retrievaban -- ver commit del re-troceo.
CASOS_TITULO_F_F42 = [
    pytest.param(
        "Cual es la maxima relacion ancho plano-espesor w/t para un elemento a compresion rigidizado con ambos bordes longitudinales conectados a otros elementos rigidizados segun el Titulo F?",
        ["500"],
        id="F-f42-max-wt-elemento-rigidizado-ambos-bordes-500",
    ),
    pytest.param(
        "Cual es la relacion maxima altura-espesor h/t para almas no reforzadas de miembros en flexion de acero formado en frio segun el Titulo F?",
        ["200"],
        id="F-f42-max-ht-almas-no-reforzadas-200",
    ),
    pytest.param(
        "Que coeficiente de pandeo de placa k se usa para elementos NO rigidizados bajo compresion uniforme segun el Titulo F?",
        ["0.43", "0,43"],
        id="F-f42-k-elemento-no-rigidizado-043",
    ),
]


@pytest.mark.parametrize(
    "pregunta,variantes_esperadas",
    CASOS_TITULO_B
    + CASOS_TITULO_A
    + CASOS_TITULO_C
    + CASOS_TITULO_D
    + CASOS_TITULO_E
    + CASOS_TITULO_G
    + CASOS_TITULO_A_EXTRA
    + CASOS_TITULO_F_EXTRA
    + CASOS_TITULO_J
    + CASOS_TITULO_K
    + CASOS_TITULO_H
    + CASOS_TITULO_I
    + CASOS_TITULO_B_EXTRA
    + CASOS_NTC_SGSST
    + CASOS_TITULO_K_K4
    + CASOS_TITULO_K_K42
    + CASOS_TITULO_F_F41
    + CASOS_TITULO_F_F42,
)
def test_respuesta_contiene_hecho_verificado(pregunta: str, variantes_esperadas: list[str]) -> None:
    # top_k=4 (hardcodeado aquí desde antes) quedó por debajo incluso del
    # viejo default de la app (6), y muy por debajo del real actual
    # (TOP_K_DEFAULT_RAG=10, subido 2026-08-26 por el mismo motivo: corpus
    # verbatim mucho más grande y granular tras Título G y C). No pasar
    # top_k usa el default real de ask() -- el test deja de ser más
    # estricto que producción, que era un falso negativo, no una regresión.
    resultado = ask(pregunta)
    respuesta = resultado["respuesta"]
    assert _contiene_alguna(respuesta, variantes_esperadas), (
        f"Ninguna de {variantes_esperadas} apareció en la respuesta.\n"
        f"Pregunta: {pregunta}\nRespuesta real: {respuesta}"
    )
