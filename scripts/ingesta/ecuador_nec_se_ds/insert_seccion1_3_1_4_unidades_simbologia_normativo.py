"""
Inserta el núcleo verbatim real de la Sección 1.3-1.4 (Unidades y
Simbología; Contexto normativo) de la norma NEC-SE-DS de Ecuador en
ecuador_nec_se_ds_chunks. Con esto se cierra por completo la Sección 1
(Generalidades) -- 1.1/1.2 ya estaban cargadas de una sesión anterior.

Cubre: 1.3.1 (unidades SI usadas en toda la norma), 1.3.2 (glosario
completo de simbología, ~130 símbolos, agrupados temáticamente en 9
bloques para no fragmentar en más de 100 chunks individuales -- mismo
criterio de agrupación ya usado para la Tabla 16 de poblaciones), 1.4.1
(las 8 normas ecuatorianas NEC-SE-* que conforman el marco normativo de
edificación), 1.4.2 (tabla de normas extranjeras de referencia usadas
por la NEC-SE-DS: ASCE7-10, ASTM D2166/D2850/D4318/D5777, ATC-33/40,
FEMA440/450, VISION 2000, NEHRP, NSR-10 de Colombia, AASHTO, PIANC --
con la sección de la norma donde se cita cada una).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion1_3_1_4_unidades_simbologia_normativo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 1.3-1.4 — Unidades, Simbología y Contexto Normativo"

CHUNKS = [
    {
        "id": "NECSEDS-S1_3_1-UNIDADES",
        "seccion": "1.3.1",
        "titulo": "Sistema de unidades usado en toda la norma NEC-SE-DS: SI (m, kN, kg, s, Pa, kPa)",
        "texto": (
            "NEC-SE-DS, Sección 1.3.1 — Unidades usadas en toda la norma "
            "(Sistema Internacional): aceleraciones en m/s²; alturas en "
            "m; áreas en m²; fuerzas y cargas en kN o kN/m²; masas en "
            "kg; períodos en s; peso específico en kg/m³; presión en Pa "
            "o N/m²; resistencias en kPa; velocidad en m/s."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-01_GEOMETRIA_GENERAL",
        "seccion": "1.3.2 (bloque 1/9)",
        "titulo": "Simbología: AB, Así, Ax, α, CPT, Ct, CW, D, DBF, dc, DBD, di, ds",
        "texto": (
            "NEC-SE-DS, Sección 1.3.2 — Simbología (glosario completo de "
            "símbolos usados en toda la norma). Bloque 1/9 — geometría y "
            "conceptos generales:\n"
            "  AB — Área de la edificación en su base.\n"
            "  Así — Área mínima de cortante de la sección de un muro "
            "estructural i, medida en un plano horizontal, en el primer "
            "nivel de la estructura y en la dirección de estudio.\n"
            "  Ax — Factor de amplificación.\n"
            "  α — Impedancia del semiespacio: α = ρsVs / ρ0V0.\n"
            "  CPT — Ensayo penetrómetro de cono.\n"
            "  Ct — Coeficiente que depende del tipo de edificio.\n"
            "  CW — Coeficiente para la formulación alternativa de Ct "
            "(estructuras con muros estructurales de hormigón armado o "
            "mampostería estructural).\n"
            "  D — Carga muerta total de la estructura.\n"
            "  DBF — Diseño Basado en Fuerzas.\n"
            "  dc — Suma de los espesores de estratos de suelos "
            "cohesivos dentro de los 30 m superiores del perfil.\n"
            "  DBD — Diseño Directo Basado en Desplazamientos.\n"
            "  di — Espesor del estrato i, dentro de los 30 m superiores "
            "del perfil.\n"
            "  ds — Suma de los espesores de estratos de suelos no "
            "cohesivos dentro de los 30 m superiores del perfil."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-02_DEFORMACIONES_DERIVAS",
        "seccion": "1.3.2 (bloque 2/9)",
        "titulo": "Simbología: Δvn, δi, dmáx, dprom, Δd, ΔE, ΔEi, Δi, ΔM, ΔMi, ΔMi+1, ΔMup, Δn, Δyi, Δy",
        "texto": (
            "Bloque 2/9 — deformaciones y derivas:\n"
            "  Δvn — Separación previamente existente entre la "
            "estructura vecina y la nueva.\n"
            "  δi — Deflexión elástica del piso i, con las fuerzas "
            "laterales fi.\n"
            "  dmáx — Valor del desplazamiento máximo en el nivel x.\n"
            "  dprom — Promedio de desplazamientos de los puntos "
            "extremos de la estructura en el nivel x.\n"
            "  Δd — Desplazamiento característico usado en el DBD.\n"
            "  ΔE — Fuerzas laterales de diseño reducidas.\n"
            "  ΔEi — Derivas de piso calculada.\n"
            "  Δi — Deriva del piso i calculada en el centro de masas "
            "del piso.\n"
            "  ΔM — Derivas de entrepiso inelásticas máximas "
            "(desplazamientos máximos horizontales inelásticos).\n"
            "  ΔMi — Deriva máxima de cualquier piso.\n"
            "  ΔMi+1 — Deriva máxima del piso superior.\n"
            "  ΔMup — Desplazamiento del último piso.\n"
            "  Δn — Desplazamiento de diseño para un edificio de n "
            "pisos.\n"
            "  Δyi — Desplazamiento de fluencia en el piso i.\n"
            "  Δy — Desplazamiento de fluencia."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-03_FUERZAS_SISMICAS",
        "seccion": "1.3.2 (bloque 3/9)",
        "titulo": "Simbología: E, Eh, Eh1, Eh2, Ex, Ey, η, ξ, εsu, εy",
        "texto": (
            "Bloque 3/9 — fuerzas sísmicas y amortiguamiento:\n"
            "  E — Efectos de las fuerzas sísmicas.\n"
            "  Eh — Componente horizontal del sismo.\n"
            "  Eh1 — Expresión de la combinación 1 de la componente "
            "horizontal del sismo.\n"
            "  Eh2 — Expresión de la combinación 2 de la componente "
            "horizontal del sismo.\n"
            "  Ex — Componente horizontal de dirección perpendicular "
            "según el eje x.\n"
            "  Ey — Componente horizontal de dirección perpendicular "
            "según el eje y.\n"
            "  η — Razón entre la aceleración espectral Sa(T=0,1s) y el "
            "PGA para el período de retorno seleccionado; su valor "
            "depende de la región del Ecuador.\n"
            "  ξ — Nivel de amortiguamiento viscoso equivalente.\n"
            "  εsu — Deformación unitaria última.\n"
            "  εy — Deformación unitaria de fluencia del acero de "
            "refuerzo."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-04_COEFICIENTES_SUELO",
        "seccion": "1.3.2 (bloque 4/9)",
        "titulo": "Simbología: Fa, f'cc, Fd, fi, Fi, fm, fP-D, Fs, Fv, Frev, Fx, fyh",
        "texto": (
            "Bloque 4/9 — coeficientes de amplificación de suelo y "
            "fuerzas de piso:\n"
            "  Fa — Coeficiente de amplificación de suelo en la zona de "
            "período corto; amplifica las ordenadas del espectro "
            "elástico de aceleraciones en roca por efectos de sitio.\n"
            "  f'cc — Resistencia a la compresión del hormigón en el "
            "núcleo confinado.\n"
            "  Fd — Coeficiente de amplificación de suelo; amplifica las "
            "ordenadas del espectro elástico de desplazamientos en roca "
            "por efectos de sitio.\n"
            "  fi — Cualquier distribución aproximada de las fuerzas "
            "laterales en el piso i, u otra distribución racional.\n"
            "  Fi — Vector de fuerzas laterales aplicadas en el piso i.\n"
            "  fm — Curvatura en la sección de la rótula plástica, según "
            "los límites de deformación unitaria.\n"
            "  fP-D — Factor de mayoración de los efectos de segundo "
            "orden.\n"
            "  Fs — Coeficiente de amplificación de suelo; considera el "
            "comportamiento no lineal de los suelos y la degradación del "
            "período del sitio.\n"
            "  Fv — Coeficiente de amplificación de suelo en las zonas "
            "de períodos intermedios.\n"
            "  Frev — Componente vertical del sismo de diseño (fuerza "
            "neta vertical reversible).\n"
            "  Fx — Fuerza lateral aplicada en el piso x.\n"
            "  fyh — Esfuerzo de fluencia."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-05_ALTURAS_RIGIDEZ",
        "seccion": "1.3.2 (bloque 5/9)",
        "titulo": "Simbología: g, H, hb, Heff/He, Hev, hi, Hi, hn, Hn, hwi, hx, I, Ig, IP, K, k, Keff/Ke, L, Lb, Li, lp, lw, lwi, Lr",
        "texto": (
            "Bloque 5/9 — alturas, rigidez, cargas vivas:\n"
            "  g — Aceleración o intensidad de la gravedad.\n"
            "  H — Altura. hb — Peralte de una viga característica de "
            "un pórtico.\n"
            "  Heff o He — Altura efectiva (centroide de fuerzas "
            "inerciales del primer modo de vibración).\n"
            "  Hev — Altura de la estructura vecina. hi — Altura del "
            "piso i. Hi — Para cada nivel de altura.\n"
            "  hn — Altura máxima de la edificación de n pisos, desde la "
            "base. Hn — Altura total del edificio.\n"
            "  hwi — Altura del muro i medida desde la base. hx — Altura "
            "del piso x.\n"
            "  I — Coeficiente de importancia. Ig — Coeficiente aplicado "
            "a la inercia de secciones agrietadas.\n"
            "  IP — Índice de Plasticidad (norma ASTM D 4318).\n"
            "  K — Rigidez de un elemento estructural o de la "
            "estructura. k — Coeficiente relacionado con el período de "
            "vibración T.\n"
            "  Keff o Ke — Rigidez efectiva.\n"
            "  L — Sobrecarga (carga viva). Lb — Longitud de una viga "
            "característica de un pórtico. Li — Carga viva del piso i.\n"
            "  lp — Longitud de la rótula plástica en la base del muro. "
            "lw — Longitud del muro en su base.\n"
            "  lwi — Longitud horizontal de un muro estructural i en el "
            "primer nivel, en la dirección de estudio.\n"
            "  Lr — Sobrecarga cubierta (carga viva)."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-06_MASAS_ENSAYOS_SUELO",
        "seccion": "1.3.2 (bloque 6/9)",
        "titulo": "Simbología: Meff/Me, mi, µ, n, N, N60, Nch, Ni, nw, P-Δ, PGA, Pi",
        "texto": (
            "Bloque 6/9 — masas, ensayos de penetración de suelo, "
            "efectos de segundo orden:\n"
            "  Meff o Me — Masa efectiva del sistema equivalente de un "
            "solo grado de libertad. mi — Masa del piso i.\n"
            "  µ — Demanda por ductilidad. n — Número de pisos de la "
            "estructura.\n"
            "  N — Número medio de golpes del ensayo de penetración "
            "estándar (SPT) en cualquier perfil de suelo.\n"
            "  N60 — Número medio de golpes SPT para el 60% de la "
            "energía teórica, a lo largo de todo el perfil.\n"
            "  Nch — Número medio de golpes SPT para los estratos de "
            "suelos no cohesivos.\n"
            "  Ni — Número de golpes SPT in situ (norma ASTM D 1586), "
            "con corrección por energía N60, del estrato i; no debe "
            "exceder 100.\n"
            "  nw — Número de muros diseñados para resistir las fuerzas "
            "sísmicas en la dirección de estudio.\n"
            "  P-Δ — Efectos de segundo orden.\n"
            "  PGA — Valor de la aceleración sísmica esperada en roca "
            "(Peak Ground Acceleration).\n"
            "  Pi — Suma de la carga vertical total sin mayorar (peso "
            "muerto + sobrecarga por carga viva) del piso i y de todos "
            "los pisos sobre él."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-07_REGULARIDAD_REDUCCION",
        "seccion": "1.3.2 (bloque 7/9)",
        "titulo": "Simbología: ØE, ØEA, ØEB, ØEi, ØP, ØPA, ØPB, ØPi, qc, Qi, r, R, Rd, Rξ, RΩ, ρ0, ρs, ρv",
        "texto": (
            "Bloque 7/9 — coeficientes de regularidad estructural y "
            "factores de reducción sísmica:\n"
            "  ØE — Coeficiente de regularidad en elevación. ØEA/ØEB — "
            "mínimo valor ØEi por tipo de irregularidad (sección 5.3). "
            "ØEi — Coeficiente de configuración en elevación.\n"
            "  ØP — Coeficiente de regularidad en planta. ØPA/ØPB — "
            "mínimo valor ØPi por tipo de irregularidad (sección 5.3). "
            "ØPi — Coeficiente de configuración en planta.\n"
            "  qc — Resistencia de punta de cono del ensayo CPT.\n"
            "  Qi — Índice de estabilidad del piso i (relación entre "
            "momento de segundo orden y momento de primer orden).\n"
            "  r — Factor del espectro de diseño elástico, según la "
            "ubicación geográfica del proyecto.\n"
            "  R — Factor de reducción de resistencia sísmica.\n"
            "  Rd — Resistencia de diseño del elemento considerado.\n"
            "  Rξ — Factor de reducción de demanda sísmica.\n"
            "  RΩ — Factor de sobrerresistencia.\n"
            "  ρ0 — Densidad del geomaterial del semiespacio.\n"
            "  ρs — Densidad promedio del suelo que sobreyace al "
            "semiespacio.\n"
            "  ρv — Cuantía volumétrica."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-08_ESPECTROS_PERIODOS",
        "seccion": "1.3.2 (bloque 8/9)",
        "titulo": "Simbología: Sa, Sd, SD1, SM1, SPT, Su, Sui, T, Tr, Tse, T0, Ta, TC, Teff/Te, TL, θT, θyn, θy",
        "texto": (
            "Bloque 8/9 — espectros de respuesta y períodos:\n"
            "  Sa o Sa(T) — Espectro de respuesta elástico de "
            "aceleraciones (fracción de g), según el período o modo de "
            "vibración.\n"
            "  Sd o Sd(T) — Espectro elástico de diseño de "
            "desplazamientos (5% de amortiguamiento respecto al "
            "crítico), según el período o modo de vibración.\n"
            "  SD1 — Aceleración espectral para T=1s, período de retorno "
            "475 años (estándar ASCE7-10, EE.UU.).\n"
            "  SM1 — Aceleración espectral para T=1s, período de retorno "
            "2.500 años, incluyendo el efecto del suelo de cimentación "
            "(estándar ASCE7-10).\n"
            "  SPT — Ensayo de penetración estándar.\n"
            "  Su — Resistencia al corte no drenado. Sui — Resistencia "
            "al corte no drenado del estrato i (norma ASTM D 2166 o D "
            "2850).\n"
            "  T — Período fundamental de vibración de la estructura.\n"
            "  Tr — Período de retorno de un sismo.\n"
            "  Tse — Período elástico del subsuelo.\n"
            "  T0 — Período límite inferior del espectro sísmico "
            "elástico de aceleraciones (sismo de diseño).\n"
            "  Ta — Período fundamental de vibración aproximado.\n"
            "  TC — Período límite superior del espectro sísmico "
            "elástico de aceleraciones.\n"
            "  Teff o Te — Período efectivo.\n"
            "  TL — Período límite de vibración para el espectro de "
            "respuesta en desplazamientos.\n"
            "  θT — Deriva de diseño (deformación unitaria máxima, "
            "sección 7.2.2). θyn — Deriva de fluencia del último piso. "
            "θy — Deriva de fluencia."
        ),
    },
    {
        "id": "NECSEDS-S1_3_2-SIMBOLOGIA-09_CORTANTES_OTROS",
        "seccion": "1.3.2 (bloque 9/9)",
        "titulo": "Simbología: V, V0, VDBD, VE, Vi, Vs, Vs30, Vsi, Vx, w, W, wi, Wp, Ev, wx, ωθ, Z",
        "texto": (
            "Bloque 9/9 — cortantes, cargas y factor de zona:\n"
            "  V — Cortante total en la base de la estructura para el "
            "DBF.\n"
            "  V0 — Velocidad de la onda cortante del geomaterial en el "
            "semiespacio.\n"
            "  VDBD — Cortante basal utilizado en el DBD (resistencia "
            "requerida al alcanzar el desplazamiento meta).\n"
            "  VE — Cortante basal elástico. Vi — Cortante sísmico del "
            "piso i.\n"
            "  Vs — Velocidad de onda cortante promedio del suelo sobre "
            "el semiespacio. Vs30 — Velocidad media de la onda de "
            "cortante (30 m superiores).\n"
            "  Vsi — Velocidad media de la onda de cortante del estrato "
            "i, medida en campo. Vx — Cortante total en el piso x.\n"
            "  w — Contenido de agua en porcentaje (norma ASTM D 2166).\n"
            "  W — Carga sísmica reactiva.\n"
            "  wi — Peso asignado al piso i, fracción de la carga "
            "reactiva W (incluye fracción de carga viva).\n"
            "  Wp — Peso que actúa en el voladizo.\n"
            "  Ev — Componente vertical del sismo.\n"
            "  wx — Peso asignado al piso x, fracción de W (sección "
            "6.1.7).\n"
            "  ωθ — Factor de amplificación dinámica de derivas.\n"
            "  Z — Aceleración máxima en roca esperada para el sismo de "
            "diseño (fracción de g)."
        ),
    },
    {
        "id": "NECSEDS-S1_4_1-NORMAS_ECUATORIANAS",
        "seccion": "1.4.1",
        "titulo": "Las 8 normas NEC-SE-* que conforman el marco normativo ecuatoriano de edificación (Cargas, Sísmica, Rehabilitación, Geotecnia, Hormigón, Acero, Mampostería, Madera)",
        "texto": (
            "NEC-SE-DS, Sección 1.4.1 — Normas ecuatorianas de la "
            "construcción (marco NEC-SE completo referenciado por esta "
            "norma):\n"
            "  NEC-SE-CG — Cargas (no sísmicas).\n"
            "  NEC-SE-DS — Cargas Sísmicas y Diseño Sismo Resistente "
            "(esta misma norma).\n"
            "  NEC-SE-RE — Rehabilitación Sísmica de Estructuras.\n"
            "  NEC-SE-GM — Geotecnia y Diseño de Cimentaciones.\n"
            "  NEC-SE-HM — Estructuras de Hormigón Armado.\n"
            "  NEC-SE-AC — Estructuras de Acero.\n"
            "  NEC-SE-MP — Estructuras de Mampostería Estructural.\n"
            "  NEC-SE-MD — Estructuras de Madera."
        ),
    },
    {
        "id": "NECSEDS-S1_4_2-NORMAS_EXTRANJERAS",
        "seccion": "1.4.2",
        "titulo": "Normas extranjeras de referencia usadas por la NEC-SE-DS: ASCE7-10, ASTM (4 normas de suelo), ATC-33/40, FEMA 440/450, VISION 2000, NEHRP, NSR-10 de Colombia, AASHTO, PIANC — con la sección donde se citan",
        "texto": (
            "NEC-SE-DS, Sección 1.4.2 — Normas extranjeras usadas para "
            "la NEC-SE-DS (verbatim, abreviación — sección donde se "
            "cita):\n"
            "  ASCE7-10 (Minimum Design Loads for Buildings and other "
            "Structures, ASCE/SEI-7-10, 2010) — sección 10.1.2.\n"
            "  ASTM D 2166 (Unconfined Compressive Strength of Cohesive "
            "Soil) — sección 10.6.2.\n"
            "  ASTM D 2850 (Unconsolidated-Undrained Triaxial "
            "Compression Test on Cohesive Soils) — sección 10.6.2.\n"
            "  ASTM D 4318 (Liquid Limit, Plastic Limit, and Plasticity "
            "Index of Soils) — sección 10.6.2.\n"
            "  ASTM D5777 (Seismic Refraction Method for Subsurface "
            "Investigation) — secciones 10.6.2 y 10.6.4.\n"
            "  Guías ATC-33 / ASCE-SEI 41-06 (Guidelines/Seismic "
            "Rehabilitation of Buildings) — sin sección específica "
            "listada.\n"
            "  Documentos VISION 2000 (SEAOC, 1995) — sin sección "
            "específica listada.\n"
            "  Guía NEHRP (National Earthquake Hazards Reduction "
            "Program) — sección 4.2.2.\n"
            "  Capítulos 13 y 15 del NEHRP/FEMA450 (BSSC 2004, "
            "Recommended Provisions for Seismic Regulations) — secciones "
            "4.3.2 y 8.\n"
            "  ASCE-7-10 / NSR-10 (Reglamento Colombiano de Construcción "
            "Sismo Resistente) — sección 6.3.4.\n"
            "  ATC-40 / FEMA 440 (Seismic Evaluation and Retrofit of "
            "Concrete Buildings; Improvement of nonlinear static seismic "
            "analysis) — sección 7.1.4.\n"
            "  Guías de diseño sísmico para estructuras portuarias del "
            "PIANC — sección 9.2.1.\n"
            "  AASHTO Guide Specifications for LRFD Seismic Bridge "
            "Design — sección 9.2.2.\n"
            "  ASCE 7-10 / NSR-10 (formas espectrales elásticas) — "
            "sección 10.1.2."
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
        # Fallback: dividir por lineas (cada simbolo es una linea) para no
        # partir mitad de una definicion cuando el parrafo entero excede.
        lineas = parrafo.split("\n")
        buffer = ""
        for linea in lineas:
            cand = f"{buffer}\n{linea}".strip() if buffer else linea
            if n_tok(cand) <= max_tokens:
                buffer = cand
            else:
                if buffer:
                    subchunks.append(buffer)
                buffer = linea
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
