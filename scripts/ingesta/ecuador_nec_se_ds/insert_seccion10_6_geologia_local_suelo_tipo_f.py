"""
Inserta el núcleo verbatim real de la Sección 10.6 (Procedimientos de
determinación de la geología local) de la norma NEC-SE-DS de Ecuador en
ecuador_nec_se_ds_chunks -- a pedido explícito del usuario ("sigamos
con 10.6, geología local y suelos tipo F").

Verificado antes de escribir: no había NADA de 10.6 en el corpus
todavía (búsqueda por id '%S10_6%'/'%TABLA17%'/'%SUELO_TIPO_F%' vacía).

Cubre: 10.6.1 (procedimiento de clasificación de perfil de suelo en 3
pasos -- verificar suelo tipo F, verificar arcilla blanda → tipo E,
clasificar con Vs/N60/Nch+Su -- y Tabla 17 con los umbrales numéricos
C/D/E), 10.6.2 (perfiles de suelo y ensayos geotécnicos: estabilidad
del depósito, definición de suelos cohesivos/no cohesivos/limosos,
parámetros empleados, velocidad media de onda de cortante Vs30 y los
criterios de definición de perfil A/B/C, otras determinaciones -- Tse,
contraste de impedancia α y el suelo tipo F5 --, N60/Nch/Su/IP/agua),
10.6.3 (necesidad de estudios de microzonificación sísmica en
poblaciones >100.000 habitantes), 10.6.4 (requisitos específicos de
respuesta dinámica y licuefacción para suelos tipo F: investigaciones
geotécnicas requeridas, modelación del perfil de suelo, selección de
registros sísmicos de entrada -- mínimo 7 registros --, análisis de
respuesta de sitio, análisis de licuación de suelos).

Honestidad de fuente: las fórmulas de Vs30, N60, Nch y Su (promedios
ponderados por espesor de estrato) salen con notación matemática
ilegible en la extracción del PDF (símbolos de sumatoria sin su
contenido claro) -- se transcribe el glosario de variables "Dónde:"
(sí legible con precisión) y se describe el concepto general (promedio
ponderado por espesor de cada estrato en los 30 m superiores) sin
afirmar la notación algebraica exacta que aparece impresa en el
documento.

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion10_6_geologia_local_suelo_tipo_f.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 10.6 — Procedimientos de Determinación de la Geología Local"

CHUNKS = [
    {
        "id": "NECSEDS-S10_6_1-PROCEDIMIENTO_CLASIFICACION-01_PASOS_1_2",
        "seccion": "10.6.1",
        "titulo": "Procedimiento de clasificación de perfil de suelo, Paso 1 (verificar suelo tipo F → estudio especial) y Paso 2 (verificar arcilla blanda ≥3m → tipo E)",
        "texto": (
            "NEC-SE-DS, Sección 10.6.1 — Procedimiento de clasificación. "
            "Para utilizar la Tabla 2 (sección 3.2.1) que define el "
            "perfil de suelo a escoger para el diseño, se siguen 3 "
            "pasos:\n\n"
            "Paso 1: verificar si el suelo presenta las características "
            "de perfil tipo F (sección 3.2.1); en ese caso, debe "
            "realizarse un estudio sísmico particular de clasificación "
            "en el sitio, por parte de un ingeniero geotécnico, "
            "conforme a la sección 10.6.4.\n\n"
            "Paso 2: establecer la existencia de estratos de arcilla "
            "blanda. Se define arcilla blanda como aquella con "
            "resistencia al corte no drenado menor de 50 kPa, contenido "
            "de agua w mayor del 40%, e índice de plasticidad IP mayor "
            "de 20. Si existe un espesor total H de 3 m o más de "
            "estratos de arcilla que cumplan estas condiciones, el "
            "perfil de suelo se clasifica como tipo E."
        ),
    },
    {
        "id": "NECSEDS-S10_6_1-PROCEDIMIENTO_CLASIFICACION-02_PASO3_TABLA17",
        "seccion": "10.6.1 (Tabla 17)",
        "titulo": "Paso 3: clasificar con Vs, N60, o Nch+Su (usar el perfil más blando si difieren); Tabla 17 con los umbrales numéricos de C/D/E",
        "texto": (
            "Paso 3: el perfil se clasifica según la Tabla 2, usando uno "
            "de 3 criterios: Vs, N60, o la consideración conjunta de "
            "Nch y Su (sección 3.2.1). Si se obtiene Vs, prevalece esa "
            "clasificación; en caso contrario se usa N60 (todos los "
            "estratos del perfil), estimando el rango de Vs con "
            "correlaciones semi-empíricas de la literatura técnica para "
            "condiciones geotécnicas similares. Alternativamente, puede "
            "usarse Su (fracción cohesiva) junto con Nch (fracción no "
            "cohesiva) — si las dos evaluaciones dan perfiles "
            "diferentes, se usa el perfil de suelo más blando de los "
            "dos (ej. tipo E en vez de tipo D).\n\n"
            "Los 3 criterios se aplican a los 30 m superiores del "
            "perfil: Vs; N; y Nch (estratos no cohesivos, IP<20) o el "
            "promedio ponderado Su (estratos cohesivos, IP>20), tomando "
            "el que indique el perfil más blando.\n\n"
            "Tabla 17 — Criterios para clasificar suelos dentro de los "
            "perfiles tipo C, D o E (verbatim):\n"
            "  Tipo C: Vs entre 360 y 760 m/s; N o Nch mayor que 50; Su "
            "mayor que 100 kPa.\n"
            "  Tipo D: Vs entre 180 y 360 m/s; N o Nch entre 15 y 50; Su "
            "entre 100 y 50 kPa.\n"
            "  Tipo E: Vs menor de 180 m/s; N o Nch menor de 15; Su "
            "menor de 50 kPa."
        ),
    },
    {
        "id": "NECSEDS-S10_6_2-PERFILES_ENSAYOS-01_ESTABILIDAD_DEPOSITO",
        "seccion": "10.6.2 (intro / a)",
        "titulo": "Identificación del perfil desde superficie natural (incluso con sótanos); en depósitos inestables (ladera, licuables, rellenos) no se usan estas definiciones, se requiere investigación geotécnica específica",
        "texto": (
            "NEC-SE-DS, Sección 10.6.2 — Perfiles de suelo y ensayos "
            "geotécnicos. Los efectos locales de la respuesta sísmica de "
            "la edificación deben evaluarse con base en los perfiles de "
            "suelo, sin importar el tipo de cimentación. La "
            "identificación del perfil se hace desde la superficie "
            "natural del terreno, incluso en edificios con sótanos. En "
            "edificios en ladera, el ingeniero geotécnico evalúa la "
            "condición más crítica y desfavorable.\n\n"
            "a) Estabilidad del depósito: los perfiles de suelo se "
            "refieren a depósitos estables. Cuando exista posibilidad de "
            "que el depósito no sea estable (especialmente ante un "
            "sismo — sitios en ladera, suelos potencialmente licuables o "
            "rellenos), NO deben usarse estas definiciones; en su lugar "
            "se requiere una investigación geotécnica que identifique la "
            "estabilidad del depósito y las medidas correctivas "
            "posibles. El estudio geotécnico debe indicar claramente las "
            "medidas correctivas y la demanda sísmica del sitio a usar "
            "en el diseño una vez ejecutadas esas medidas. La "
            "construcción no puede iniciarse sin tomar las medidas "
            "correctivas necesarias."
        ),
    },
    {
        "id": "NECSEDS-S10_6_2-PERFILES_ENSAYOS-02_COHESIVOS_PARAMETROS",
        "seccion": "10.6.2 (b / c)",
        "titulo": "Definición de suelos cohesivos (>30% finos, 15%≤IP≤90%), no cohesivos (<30% finos) y limosos (tratados como cohesivos); parámetros empleados: Vs30, N60, Nch, Su, IP, contenido de agua",
        "texto": (
            "b) Suelos cohesivos: suelos no cohesivos son los que "
            "poseen menos del 30% de finos por peso seco (pasante del "
            "tamiz #200). Suelos cohesivos: más del 30% de finos y 15% ≤ "
            "IP(finos) ≤ 90%. Suelos limosos: más del 30% de finos con "
            "IP(finos) < 15% — se consideran y tratan conservadoramente "
            "como cohesivos para clasificación de sitio en esta norma.\n\n"
            "c) Parámetros empleados para los perfiles de suelo, con "
            "base en los 30 m superiores: la velocidad media de la onda "
            "de cortante Vs30 (m/s); el número medio de golpes del "
            "ensayo SPT al 60% de la energía teórica, N60, a lo largo "
            "del perfil (ensayos cada 1,5 m hasta el estrato estable, "
            "N60≥100 confirmado en al menos 4 m de potencia); cuando se "
            "consideran por separado los estratos no cohesivos y "
            "cohesivos: Nch (no cohesivos) y Su en kPa (cohesivos); "
            "también el Índice de Plasticidad (IP) y el contenido de "
            "agua w (%). Nota: ver la norma NEC-SE-GM para más "
            "información sobre los ensayos geotécnicos usados en "
            "Ecuador."
        ),
    },
    {
        "id": "NECSEDS-S10_6_2-VS30_PERFILES_ABC",
        "seccion": "10.6.2 (d)",
        "titulo": "Vs30: promedio ponderado por espesor de estrato en los 30 m superiores; criterios de definición de perfil tipo A (medición directa), B (medición o estimación), C (siempre medición en sitio)",
        "texto": (
            "d) Velocidad media de la onda de cortante Vs30 (sección "
            "10.6.2): se obtiene como un promedio ponderado por el "
            "espesor de cada estrato di dentro de los 30 m superiores "
            "del perfil, en función de la velocidad de onda de cortante "
            "Vsi de cada estrato. [La notación algebraica exacta con "
            "sumatorias no se pudo recuperar con precisión de la "
            "extracción del PDF — variables: Vsi = velocidad media de "
            "la onda de cortante del estrato i, medida en campo (m/s); "
            "di = espesor del estrato i dentro de los 30 m superiores.]\n\n"
            "Perfil tipo A: la roca competente debe definirse con "
            "mediciones de velocidad de onda de cortante en el sitio, o "
            "en perfiles de la misma formación con meteorización y "
            "fracturación similares. Si se conoce que la roca es "
            "continua hasta al menos 30 m de profundidad, la velocidad "
            "superficial puede usarse para definir Vs.\n\n"
            "Perfil tipo B: la velocidad en roca debe medirse en sitio "
            "o estimarse por el ingeniero geotécnico, para roca "
            "competente con meteorización y fracturación moderada.\n\n"
            "Perfil tipo C: para rocas más blandas o muy meteorizadas o "
            "fracturadas, debe medirse en sitio la velocidad de onda de "
            "cortante, o clasificarse directamente como perfil tipo C. "
            "Los perfiles con más de 3 m de suelo entre la superficie de "
            "la roca y la parte inferior de la fundación NO pueden "
            "clasificarse como tipo A o B."
        ),
    },
    {
        "id": "NECSEDS-S10_6_2-OTRAS_DETERMINACIONES-TSE_IMPEDANCIA_F5",
        "seccion": "10.6.2 (e)",
        "titulo": "Correlaciones semi-empíricas (Su, N60, CPT); período elástico del subsuelo Tse=4H/Vs (técnica de Nakamura H/V); mediciones recomendadas (sísmica de refracción, ReMi, Downhole/Uphole/Crosshole); contraste de impedancia α y el suelo tipo F5",
        "texto": (
            "e) Otras determinaciones de los parámetros del suelo: Vs30 "
            "se puede evaluar en sitio con estimaciones semi-empíricas "
            "que correlacionan velocidades de onda cortante con "
            "parámetros geotécnicos (resistencia al corte no drenado "
            "Su, número de golpes SPT N60, resistencia de punta de cono "
            "CPT qc, u otros según el ingeniero geotécnico "
            "responsable). Si se usan correlaciones, debe considerarse "
            "la incertidumbre mediante rangos esperados. Se puede "
            "calibrar el perfil con mediciones de vibración ambiental "
            "(relación espectral H/V, técnica de Nakamura), estimando "
            "el período elástico del subsuelo: Tse = 4H/Vs.\n\n"
            "Para disminuir incertidumbres, se recomienda medir Vs30 en "
            "campo con métodos geofísicos: sísmica de refracción (ASTM "
            "D5777), Análisis Espectrales de Ondas Superficiales (ReMi), "
            "o ensayos Downhole, Uphole o Crosshole.\n\n"
            "Se consideran siempre los primeros 30 m del perfil, para "
            "velocidades que se incrementan con la profundidad. Si "
            "existe un contraste de impedancia α (relación entre el "
            "producto densidad×velocidad de onda de corte del subsuelo "
            "y del semiespacio) dentro de los 30 m, ese punto se "
            "considera suelo Tipo F5. El semiespacio se define como la "
            "profundidad que no participa en la respuesta dinámica del "
            "sitio, con contraste de impedancia α ≤ 0,5."
        ),
    },
    {
        "id": "NECSEDS-S10_6_2-N60_NCH_SU_IP_AGUA",
        "seccion": "10.6.2 (f-i)",
        "titulo": "N60 (todos los estratos, ponderado por di), Nch (solo estratos no cohesivos), Su (solo estratos cohesivos, máx. 250 kPa por estrato para el promedio), IP (ASTM D4318), contenido de agua (ASTM D2166)",
        "texto": (
            "f) Número medio de golpes SPT: N60 (cualquier perfil, "
            "cohesivo o no) se obtiene como promedio ponderado por el "
            "espesor di de cada estrato en los 30 m superiores. [Notación "
            "algebraica exacta no recuperable con precisión del PDF; "
            "variable Ni = número de golpes SPT in situ, norma ASTM D "
            "1586, con corrección por energía N60, sin exceder 100 por "
            "estrato para el promedio.] Para perfiles con estratos no "
            "cohesivos, se usa Nch aplicando la misma lógica de "
            "ponderación pero solo sobre los m estratos no cohesivos "
            "(ds = suma de sus espesores).\n\n"
            "g) Resistencia media al corte no drenado Su: para estratos "
            "cohesivos en los 30 m superiores, promedio ponderado sobre "
            "los k estratos cohesivos (dc = suma de sus espesores); Sui "
            "(resistencia del estrato i, kPa) no debe exceder 250 kPa "
            "para el promedio ponderado, medida según ASTM D 2166 o "
            "ASTM D 2850.\n\n"
            "h) Índice de plasticidad (IP): se obtiene según norma ASTM "
            "D 4318.\n\n"
            "i) Contenido de agua (w, %): se determina según norma ASTM "
            "D 2166."
        ),
    },
    {
        "id": "NECSEDS-S10_6_3-MICROZONIFICACION_SISMICA",
        "seccion": "10.6.3",
        "titulo": "Poblaciones >100.000 habitantes deberían tener estudios de microzonificación sísmica/geotécnica; sus espectros de diseño locales prevalecen sobre los generales de la norma",
        "texto": (
            "NEC-SE-DS, Sección 10.6.3 — Necesidad (y límites) de "
            "estudios de microzonificación sísmica. Las poblaciones con "
            "más de 100.000 habitantes deberían disponer de estudios de "
            "microzonificación sísmica y geotécnica, describiendo y "
            "analizando: entorno geológico y tectónico local, "
            "sismología regional y fuentes sismogénicas; distribución "
            "espacial de los estratos de suelo; exploración geotécnica "
            "adicional a la requerida para cimentación; espectro de "
            "aceleración de diseño en roca y familias de acelerogramas; "
            "y estudio de amplificación de onda (análisis lineal "
            "equivalente o no lineal) para obtener los movimientos "
            "sísmicos de diseño en superficie (sección 10.6.4). Deben "
            "considerar también posibles efectos topográficos, "
            "inestabilidad sísmica en zonas licuables o de rellenos, y "
            "presencia de taludes inestables.\n\n"
            "Como resultado se dispone de: mapas de zonificación de "
            "suelos, y espectros de diseño sísmico locales o demandas "
            "sísmicas que PREVALECEN sobre los espectros de diseño "
            "generales de esta norma. Mientras se ejecutan estos "
            "estudios en poblaciones que aún no los tienen, pueden "
            "usarse los requisitos mínimos de este capítulo — que no "
            "sustituyen a los estudios detallados de sitio, necesarios "
            "para proyectos de infraestructura importante y otros "
            "distintos a edificación."
        ),
    },
    {
        "id": "NECSEDS-S10_6_4-INTRO_INVESTIGACIONES_SUELO_F",
        "seccion": "10.6.4 (intro)",
        "titulo": "Suelos tipo F requieren investigación geotécnica específica: perforaciones, SPT, CPT, ensayos de columna resonante y triaxiales dinámicos; correlaciones si no hay equipos",
        "texto": (
            "NEC-SE-DS, Sección 10.6.4 — Requisitos específicos: "
            "respuesta dinámica para suelos tipo F. El objetivo es "
            "analizar la respuesta dinámica del sitio y su potencial de "
            "licuefacción. Para perfiles tipo F, se realizan "
            "investigaciones geotécnicas específicas que incluyen: "
            "perforaciones con obtención de muestras, ensayos SPT, "
            "penetrómetro de cono CPT, y otras técnicas que permitan "
            "establecer las características del suelo y el contacto "
            "entre capas de suelo y roca. Alternativa: correlación de "
            "datos de velocidad de onda cortante de suelos similares.\n\n"
            "Se recomienda: (a) velocidades de onda de corte por sísmica "
            "de refracción (ASTM D5777); (b) período elástico del "
            "subsuelo por vibración ambiental (técnica de Nakamura, "
            "1989). Para caracterizar propiedades dinámicas, se deben "
            "hacer ensayos de columna resonante y/o triaxiales dinámicos "
            "de muestras características. Si no se cuenta con esos "
            "equipos, se pueden usar modelos de correlación de curvas de "
            "degradación de rigidez y amortiguamiento según el nivel de "
            "deformación por cortante, para suelos geotécnicamente "
            "similares.\n\n"
            "Las consideraciones siguientes aplican no solo a suelos "
            "tipo F, sino a cualquier estudio de respuesta dinámica, "
            "incluyendo microzonificación sísmica."
        ),
    },
    {
        "id": "NECSEDS-S10_6_4A1-MODELACION_PERFIL_SUELO",
        "seccion": "10.6.4 (a.1)",
        "titulo": "Modelación del perfil de suelo: columna 1D hasta el basamento rocoso o contraste de impedancia <0,5; caracterización por peso volumétrico y perfil de Vs; curvas de reducción de módulo y amortiguamiento; licuación (presión de poro)",
        "texto": (
            "NEC-SE-DS, Sección 10.6.4.a — Análisis de respuesta "
            "dinámica de sitio (3 aspectos: modelación del perfil, "
            "selección de registros de entrada, análisis e "
            "interpretación).\n\n"
            "(1) Modelación del perfil de suelo: comúnmente una columna "
            "unidimensional desde la superficie hasta el basamento "
            "rocoso o donde se desarrolla el primer contraste de "
            "impedancia menor a 0,5. Para proyectos de gran envergadura "
            "(cuencas topográficas, presas, puentes) se consideran "
            "modelos bidimensionales/tridimensionales cuando las "
            "velocidades de onda 2D/3D son significativas. En modelos "
            "1D, las capas se caracterizan por su peso volumétrico total "
            "y el perfil de velocidades de onda cortante, obteniendo el "
            "módulo máximo por cortante a bajas deformaciones y las "
            "relaciones de comportamiento no lineal esfuerzo-deformación "
            "(curvas de reducción de módulo y de amortiguamiento vs. "
            "deformación unitaria por cortante). En modelos 2D/3D "
            "también se requiere la velocidad de onda de compresión o "
            "el módulo de Poisson, con ensayos de columna resonante y "
            "triaxial dinámico (o correlaciones si no hay equipos).\n\n"
            "Para estimar efectos de licuación en la respuesta de sitio, "
            "el modelo no lineal debe incluir el desarrollo de la "
            "presión de poro y sus efectos en la reducción de rigidez y "
            "resistencia del suelo; se pueden usar metodologías "
            "semi-empíricas con resultados de SPT y CPT. La "
            "incertidumbre en las propiedades del suelo (módulo máximo, "
            "reducción de módulos, curvas de amortiguamiento) debe "
            "estimarse."
        ),
    },
    {
        "id": "NECSEDS-S10_6_4A2A3-REGISTROS_ENTRADA_INTERPRETACION",
        "seccion": "10.6.4 (a.2-a.3)",
        "titulo": "Mínimo 7 registros de aceleración en roca tipo B/A escalados al espectro elástico; softwares recomendados para licuefacción (DESRA-2, D-MOD, DEEPSOIL, etc.); espectro de sitio suavizado de la mediana de 7",
        "texto": (
            "(2) Selección de los registros sísmicos de entrada: se "
            "seleccionan registros de aceleración en afloramiento "
            "rocoso (perfil tipo B) representativos de las condiciones "
            "sismológicas del sitio. Salvo un análisis específico de "
            "peligro sísmico del sitio (probabilista o determinista), el "
            "espectro de respuesta en roca se define para perfil tipo B, "
            "tomando como referencia el espectro elástico de "
            "aceleraciones de esta norma. Se deben seleccionar mínimo 7 "
            "registros de aceleraciones sismológicamente compatibles con "
            "magnitud y distancia esperada, escalados de modo que la "
            "mediana se aproxime al espectro elástico en campo libre en "
            "roca tipo B o A, considerando el efecto de la condición de "
            "frontera en la excitación de entrada.\n\n"
            "(3) Análisis de respuesta de sitio e interpretación de "
            "resultados: si la respuesta del suelo es altamente no "
            "lineal (altas aceleraciones, suelos suaves arcillosos), se "
            "recomiendan métodos no lineales; en paralelo se debe hacer "
            "análisis lineal equivalente para comparar. Para "
            "licuefacción, se recomiendan métodos con desarrollo de "
            "presión de poro (esfuerzos efectivos): DESRA-2, SUMDES, "
            "D-MOD, DESRA-MUSC, TESS, DEEPSOIL, AMPLE, entre otros. Se "
            "calculan las relaciones entre espectros de salida y de "
            "entrada (aceleraciones, velocidades, desplazamientos al "
            "5,00% de amortiguamiento crítico, y variación con la "
            "profundidad de deformaciones y esfuerzo cortante máximos). "
            "Se obtiene la mediana de los 7 espectros, ajustada a un "
            "espectro suavizado (leves descensos de picos, ligeros "
            "aumentos de valles). Finalmente se hace análisis de "
            "sensitividad de la incertidumbre de las propiedades del "
            "suelo."
        ),
    },
    {
        "id": "NECSEDS-S10_6_4B-ANALISIS_LICUACION",
        "seccion": "10.6.4 (b)",
        "titulo": "Métodos recomendados para potencial de licuación: Bray y Sancio (2006), Seed et al. (2003), Wu (2003); para arcillas/limos cíclicos: Boulanger e Idriss (2007)",
        "texto": (
            "b) Análisis de licuación de suelos. Para estimar el "
            "potencial de licuación pueden usarse métodos como los de "
            "Bray y Sancio (2006), Seed et al. (2003), Wu, J (2003), "
            "entre otros. Para evaluar específicamente el comportamiento "
            "cíclico de arcillas y limos, se recomiendan los "
            "procedimientos de Boulanger e Idriss (2007)."
        ),
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"][:500],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("ecuador_nec_se_ds_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en ecuador_nec_se_ds_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
