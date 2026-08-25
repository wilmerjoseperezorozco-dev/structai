"""
Inserta el núcleo verbatim real de la Sección 7 (Método 2: Diseño Basado en
Desplazamientos, DBD) de la norma NEC-SE-DS de Ecuador en
ecuador_nec_se_ds_chunks. Segunda sección más pesada de lo que faltaba
(11 páginas, 74-85 del documento).

Nota de honestidad sobre fórmulas: la Sección 7 tiene varias ecuaciones con
sumatorias, subíndices y símbolos griegos (Δ, ξ, µ, ω, θ) que la extracción
de texto del PDF distorsiona -- no se pueden recuperar con la certeza
suficiente como para transcribir la notación algebraica exacta sin
arriesgar inventar un símbolo que no está realmente ahí. Para esos casos
(marcados explícitamente en el texto de cada chunk), se transcribe el
concepto y el glosario de variables tal como aparecen verbatim en el "Dónde:"
de cada fórmula (esa parte SÍ es legible con precisión), pero se indica
que la expresión algebraica exacta requiere el documento oficial -- mismo
criterio que "no inventar" ya aplicado en el resto del proyecto. Las
fórmulas que sí quedaron legibles con confianza (ej. VDBD = Keff · Δd) se
transcriben tal cual.

Fuente: mismo PDF oficial MIDUVI/MIT ya usado para el resto de Ecuador.

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion7_metodo2_dbd.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 7 — Método 2: Diseño Basado en Desplazamientos (DBD)"

CHUNKS = [
    {
        "id": "NECSEDS-S7_1_1_7_1_2-PRINCIPIOS_CONDICIONES_DBD",
        "seccion": "7.1.1-7.1.2",
        "titulo": "DBD — Principios (desplazamiento objetivo), diseño por capacidad; condiciones de aplicación (esenciales, irregulares, aporticados/muros)",
        "texto": (
            "NEC-SE-DS, Sección 7.1.1 — Principios y objetivos del DBD. El "
            "Diseño Basado en Desplazamientos (DBD) parte de un "
            "desplazamiento objetivo (desplazamiento de diseño), función "
            "del desempeño o nivel de daño deseado, y proporciona la "
            "resistencia lateral requerida para alcanzar ese desempeño. Se "
            "debe respetar la metodología tradicional de diseño sismo "
            "resistente de la sección 4.2. Para asegurar su eficiencia, se "
            "usan en paralelo los principios del Diseño por Capacidad en el "
            "detallamiento, para que el mecanismo dúctil seleccionado (y "
            "solo ese) se desarrolle durante un evento sísmico severo.\n\n"
            "Sección 7.1.2 — Condiciones de aplicación. Se privilegia el "
            "DBD para estructuras esenciales y de ocupación especial, y en "
            "lo posible para estructuras irregulares en planta y "
            "elevación. Puede usarse para edificios aporticados de "
            "hormigón armado o acero, y para edificios con muros "
            "estructurales. Los criterios para otros tipos de estructura "
            "pueden obtenerse en Priestley, Calvi y Kowalsky (2007)."
        ),
    },
    {
        "id": "NECSEDS-S7_1_3_7_1_6-SISTEMA_EQUIVALENTE_LOGICA",
        "seccion": "7.1.3-7.1.6",
        "titulo": "DBD — Espectro de desplazamientos; sistema elástico equivalente de 1 grado de libertad (rigidez secante); puntos clave; lógica del proceso",
        "texto": (
            "NEC-SE-DS, Sección 7.1.3 — Representación del sismo de diseño "
            "DBD. Las estructuras se diseñan para la amenaza sísmica "
            "representada por el espectro de desplazamientos de la sección "
            "3.3.2.\n\n"
            "Sección 7.1.4 — Sistema elástico equivalente de un grado de "
            "libertad. El DBD utiliza una estructura equivalente de un "
            "grado de libertad, basado en que el primer modo de vibración "
            "genera las mayores demandas y desarrolla las rótulas "
            "plásticas; la demanda de otros modos se considera mediante "
            "factores de amplificación dinámica en secciones/elementos "
            "protegidos (donde no deben formarse rótulas). Se fundamenta en "
            "linearización equivalente: la estructura inelástica en su "
            "desplazamiento máximo se reemplaza por un sistema elástico de "
            "1 grado de libertad, usando la rigidez secante en el punto de "
            "respuesta máxima y aplicando amortiguamiento viscoso e "
            "histerético equivalente. Este sistema representa la respuesta "
            "pico de desplazamiento, no las características elásticas "
            "iniciales de la estructura.\n\n"
            "Sección 7.1.5 — Puntos clave del DBD: caracteriza la "
            "estructura por la rigidez secante Ke, definida para un "
            "desplazamiento característico Δ y un amortiguamiento viscoso "
            "equivalente ξ (combina amortiguamiento elástico + energía "
            "histerética). El ingeniero diseña para un desplazamiento "
            "prefijado (no verifica un límite a posteriori); el resultado "
            "final son los esfuerzos y la rigidez de los elementos.\n\n"
            "Sección 7.1.6 — Lógica del proceso: (1) determinar la "
            "Estructura Equivalente (7.1.4); (2) determinar el "
            "desplazamiento de diseño ΔD (7.2.3); (3) desarrollar el "
            "espectro de desplazamientos de diseño (3.3.2); (4) distribuir "
            "el cortante basal V para las masas discretizadas y analizar la "
            "estructura bajo esa distribución (7.2.4)."
        ),
    },
    {
        "id": "NECSEDS-S7_2_1-REQUISITOS_DESEMPENO",
        "seccion": "7.2.1",
        "titulo": "DBD — Requisitos generales (rótulas predeterminadas, amplificación por modos altos, P-Δ); nivel de desempeño 'seguridad de vida'",
        "texto": (
            "NEC-SE-DS, Sección 7.2.1 — Requisitos generales para la "
            "aplicación del DBD. Se verifican las deformaciones "
            "inelásticas: rótulas plásticas solo en sitios "
            "predeterminados, aplicando diseño por capacidad; las fuerzas "
            "de diseño de secciones que deben permanecer elásticas se "
            "amplifican para incluir efectos de modos de vibración altos; "
            "se verifica que los efectos de segundo orden (P-Δ) no causen "
            "inestabilidad. La estructura debe cumplir los requisitos de "
            "configuración estructural (sección 5.3) para asegurar un "
            "mecanismo satisfactorio de deformación inelástica.\n\n"
            "Nivel de desempeño estructural: se usa el nivel \"seguridad de "
            "vida\" (sección 4.2.4). En el DBD, el daño se correlaciona con "
            "los desplazamientos generados durante un sismo severo, no con "
            "la resistencia lateral desarrollada."
        ),
    },
    {
        "id": "NECSEDS-S7_2_2-TABLA14-DEFORMACION_UNITARIA_MAXIMA",
        "seccion": "7.2.2 (Tabla 14)",
        "titulo": "DBD — Criterio de desempeño: deformación unitaria máxima (Tabla 14: hormigón <0,02, acero refuerzo 0,06, acero estructural 0,025)",
        "texto": (
            "NEC-SE-DS, Sección 7.2.2 — Criterio de desempeño: deformación "
            "unitaria máxima. El desplazamiento meta lo gobierna "
            "generalmente el límite de deriva de piso en pórticos "
            "resistentes a momentos (flexibilidad inherente), o los "
            "límites de deformación unitaria en edificios con muros "
            "estructurales. Se verifican límites de deformación por "
            "compresión y por flexión o flexo-compresión. Para el estado "
            "límite \"seguridad de vida\", se aplican los límites de la "
            "Tabla 14 a las fibras extremas de las secciones donde se "
            "espera rótula plástica; los límites de deriva admisibles "
            "están en la sección 5.2.\n\n"
            "Tabla 14 — Límites de deformación unitaria máxima (verbatim):\n"
            "  Hormigón en compresión: εcu < 0,02 (según fórmula de Mander "
            "con la cuantía volumétrica de confinamiento ρv, el esfuerzo de "
            "fluencia fyh, la deformación unitaria última del refuerzo de "
            "confinamiento εsu, y la resistencia del hormigón confinado "
            "f'cc — la expresión algebraica exacta de esta fórmula no se "
            "pudo recuperar con precisión del PDF, ver documento oficial).\n"
            "  Acero de refuerzo en tensión: 0,06.\n"
            "  Acero estructural: 0,025.\n\n"
            "Estos valores definen el nivel de daño más allá del cual los "
            "costos de reparación pueden superar los de reposición. Nota: "
            "cuando no sea posible un confinamiento adecuado, o el modelo "
            "de Mander u otro método racional no pueda aplicarse, el "
            "límite de deformación unitaria del hormigón se fija en 0,004. "
            "El límite del acero de refuerzo (0,06) es conservador, para "
            "evitar mecanismos de falla por fatiga y pandeo de barras "
            "longitudinales no considerados por el método."
        ),
    },
    {
        "id": "NECSEDS-S7_2_3abc-DESPLAZAMIENTO_ALTURA_MASA_EFECTIVA",
        "seccion": "7.2.3 (a-c)",
        "titulo": "DBD — Desplazamiento característico Δd (reducido por irregularidad), altura efectiva Heff, masa efectiva Meff — conceptos y variables (fórmulas con sumatorias no recuperables con precisión del PDF)",
        "texto": (
            "NEC-SE-DS, Sección 7.2.3 — Determinación de los parámetros "
            "usados en el DBD.\n\n"
            "a. Desplazamiento característico Δd: se reduce aplicando los "
            "factores de irregularidad en planta y elevación (ØP, ØE, "
            "sección 5.3), para contrarrestar la amplificación de "
            "desplazamientos/deformaciones/derivas por esas "
            "irregularidades. Es una relación ponderada por masa (mi) y "
            "desplazamiento de diseño por piso (Δi), multiplicada por "
            "ØP·ØE. [La expresión algebraica exacta con las sumatorias no "
            "se pudo recuperar con precisión del texto extraído del PDF — "
            "ver el documento oficial para la fórmula completa.]\n\n"
            "b. Altura efectiva Heff: define el centroide de las fuerzas "
            "inerciales generadas por el primer modo de vibración, como "
            "relación ponderada de la altura de cada nivel Hi por el "
            "producto masa×desplazamiento (mi·Δi) de cada piso. [Sumatoria "
            "exacta no recuperable con precisión del PDF.]\n\n"
            "c. Masa efectiva Meff: del sistema equivalente de un grado de "
            "libertad, como relación entre la sumatoria de mi·Δi de todos "
            "los pisos y el desplazamiento característico Δd. [Sumatoria "
            "exacta no recuperable con precisión del PDF.]\n\n"
            "Variables comunes: mi = masa del piso i (estructural + no "
            "estructural + 25% de la carga viva); Δi = desplazamiento de "
            "diseño del piso i (sección 7.3); ØP, ØE = factores de "
            "irregularidad en planta/elevación (sección 5.3)."
        ),
    },
    {
        "id": "NECSEDS-S7_2_3de-DESPLAZAMIENTO_FLUENCIA_DUCTILIDAD",
        "seccion": "7.2.3 (d-e)",
        "titulo": "DBD — Desplazamiento de fluencia Δy (pórticos de hormigón/acero, muros estructurales); demanda de ductilidad µ = ΔD/Δy",
        "texto": (
            "NEC-SE-DS, Sección 7.2.3.d — Desplazamiento de fluencia Δy. Se "
            "estima con análisis estructural racional, o mediante "
            "ecuaciones específicas para estructuras aporticadas o con "
            "muros estructurales — basadas en que la curvatura de fluencia "
            "por flexión depende de la geometría y la deformación unitaria "
            "de fluencia de los materiales, no de la resistencia de la "
            "sección.\n\n"
            "Para edificios con pórticos: Δy es función de la deriva de "
            "fluencia θy y la altura efectiva Heff. La deriva de fluencia "
            "θy se estima, para pórticos de hormigón armado, en función de "
            "la deformación unitaria de fluencia del acero εy y de la luz "
            "de la viga característica; para pórticos de acero estructural, "
            "en función de εy y de la longitud/peralte de la viga "
            "característica (Lb, hb). [Las expresiones algebraicas exactas "
            "no se pudieron recuperar con precisión del PDF — ver "
            "documento oficial.]\n\n"
            "Para edificios con muros estructurales: Δy depende de la "
            "longitud del muro en su base lw, la altura efectiva Heff y la "
            "altura total del edificio Hn, además de εy. [Fórmula exacta "
            "no recuperable con precisión del PDF.]\n\n"
            "7.2.3.e — Demanda de ductilidad. µ = ΔD / Δy, donde ΔD = "
            "desplazamiento característico usado en el DBD, Δy = "
            "desplazamiento de fluencia."
        ),
    },
    {
        "id": "NECSEDS-S7_2_3fgh-RXI_PERIODO_RIGIDEZ_EFECTIVOS",
        "seccion": "7.2.3 (f-h)",
        "titulo": "DBD — Factor de reducción de demanda sísmica Rξ (Figura 12, no confundir con R de 6.3.4); período efectivo Teff; rigidez efectiva Keff = 4π²·Meff/Teff²",
        "texto": (
            "NEC-SE-DS, Sección 7.2.3.f — Factor de reducción de demanda "
            "sísmica Rξ. Se obtiene de la Figura 12 en función de la "
            "demanda de ductilidad µ. Advertencia explícita de la norma: "
            "Rξ NO debe confundirse ni compararse con el factor R usado en "
            "la sección 6.3.4 (el coeficiente R del DBF) — son conceptos "
            "distintos con nombres parecidos.\n\n"
            "7.2.3.g — Período efectivo Teff. Se obtiene del espectro de "
            "desplazamientos de la sección 3.3.2, con expresiones "
            "distintas según si el desplazamiento característico Δd es "
            "menor o mayor que el desplazamiento correspondiente al "
            "período TL (ver Figura 7) — en función de Δd, Rξ, el factor "
            "de zona Z y el factor de sitio Fd (sección 3.2.2). El período "
            "efectivo es más largo que el período elástico, porque al "
            "entrar en el rango inelástico la estructura degrada su "
            "rigidez y alarga su período. [Las dos expresiones exactas — "
            "identificadas en el documento como (2-44) y (2-45) — no se "
            "pudieron recuperar con precisión algebraica del PDF, ver "
            "documento oficial.]\n\n"
            "7.2.3.h — Rigidez efectiva Keff. De la relación estándar entre "
            "período, masa y rigidez para sistemas de un grado de "
            "libertad: Keff = 4π² · Meff / Teff², donde Meff = masa "
            "efectiva, Teff = período efectivo."
        ),
    },
    {
        "id": "NECSEDS-S7_2_4-CORTANTE_BASAL_VDBD",
        "seccion": "7.2.4",
        "titulo": "DBD — Cortante basal VDBD = Keff · Δd (resistencia requerida al desplazamiento meta, no de fluencia; puede superar el V del DBF por sobre-resistencia)",
        "texto": (
            "NEC-SE-DS, Sección 7.2.4 — Cortante basal de diseño para el "
            "DBD. El cortante VDBD no es de fluencia: es la resistencia "
            "requerida por la estructura cuando alcanza el desplazamiento "
            "meta. Se calcula para las dos direcciones principales, a "
            "partir del desplazamiento de diseño y la rigidez efectiva:\n\n"
            "VDBD = Keff · Δd\n\n"
            "Donde: Keff = rigidez efectiva; Δd = desplazamiento "
            "característico. Si un edificio se diseña para derivas menores "
            "a las especificadas en 7.2.1, el DBD indicará que requiere "
            "mayor resistencia lateral y, por tanto, mayor rigidez.\n\n"
            "NOTA explícita de la norma: el cortante basal del DBD (7.2.4) "
            "podría ser MAYOR que el cortante V obtenido mediante el DBF "
            "(sección 6.3.2) — esto se debe a que VDBD incluye la "
            "sobre-resistencia de la estructura."
        ),
    },
    {
        "id": "NECSEDS-S7_2_5-VECTOR_FUERZAS_LATERALES_DBD",
        "seccion": "7.2.5",
        "titulo": "DBD — Distribución del cortante VDBD por piso (coeficiente K=0,9 aporticados / 1,0 otros); análisis de capacidad de rótulas plásticas (no se verifican derivas, ya fueron impuestas)",
        "texto": (
            "NEC-SE-DS, Sección 7.2.5 — Vector de fuerzas laterales. El "
            "cortante basal VDBD se distribuye en el centro de masa de "
            "cada piso: una relación para los pisos 1 a n-1 (ponderada por "
            "masa mi y deriva Δi de cada piso, con un coeficiente K = 0,9 "
            "para edificaciones aporticadas y K = 1,0 para todas las demás "
            "estructuras) y una relación distinta para el piso de techo "
            "(piso n), en función del desplazamiento de diseño Δn y la "
            "masa mn del piso n. [Las expresiones algebraicas exactas no "
            "se pudieron recuperar con precisión del PDF — ver documento "
            "oficial.]\n\n"
            "Análisis de la capacidad de rótulas plásticas: el análisis "
            "estructural posterior al cálculo del cortante basal tiene "
            "como objeto distribuir la resistencia en todos los elementos. "
            "En el DBD NO es necesario comprobar derivas de piso en el "
            "análisis estructural, porque las derivas ya fueron impuestas "
            "al inicio, en el perfil de desplazamiento objetivo. La "
            "estructura se analiza bajo el vector de fuerza lateral de "
            "diseño para determinar la capacidad de momento requerida en "
            "las rótulas plásticas, con el análisis basado en la rigidez "
            "efectiva de los miembros (compatible con el perfil de "
            "desplazamiento objetivo) — o cualquier otro método que "
            "satisfaga equilibrio estático. Las acciones de diseño a "
            "cortante en vigas, y de columnas/muros fuera de las rótulas "
            "plásticas, se establecen según NEC-SE-HM, NEC-SE-AC, "
            "NEC-SE-MP y NEC-SE-MD."
        ),
    },
    {
        "id": "NECSEDS-S7_3_1-PERFIL_DESPLAZAMIENTO_APORTICADOS",
        "seccion": "7.3.1",
        "titulo": "DBD — Perfil de desplazamiento en edificios aporticados: lineal si n≤4 pisos, no lineal (deriva máxima en primer piso) si n>4",
        "texto": (
            "NEC-SE-DS, Sección 7.3.1 — Perfil de desplazamiento de diseño "
            "en edificaciones aporticadas. Para un edificio de n pisos, el "
            "perfil se determina para cada altura de nivel Hi, en base a "
            "la deriva de diseño θD (sección 7.2.2), la altura total Hn, y "
            "un factor de amplificación dinámica de derivas ωθ (definido "
            "en función de Hn). [La expresión exacta de ωθ y de la deriva "
            "máxima por número de pisos no se pudo recuperar con precisión "
            "algebraica del PDF — ver documento oficial.]\n\n"
            "Para edificios de 4 pisos o menos: se asume un perfil de "
            "desplazamiento LINEAL.\n"
            "Para edificios de más de 4 pisos: el perfil es NO LINEAL y la "
            "deriva máxima ocurre en el PRIMER piso. Las expresiones para "
            "el caso n≤4 y n>4 usan la altura total del edificio Hn, la "
            "deriva de diseño θD, la altura de cada nivel Hi, y el factor "
            "ωθ."
        ),
    },
    {
        "id": "NECSEDS-S7_3_2-PERFIL_DESPLAZAMIENTO_MUROS",
        "seccion": "7.3.2",
        "titulo": "DBD — Perfil de desplazamiento en edificios con muros estructurales: el menor entre 2 ecuaciones (límite de deformación unitaria en rótula plástica de base, o deriva máxima en el último piso)",
        "texto": (
            "NEC-SE-DS, Sección 7.3.2 — Perfil de desplazamiento de diseño "
            "en edificaciones con muros estructurales. Se define con "
            "análisis racional, o se toma el MENOR valor calculado con 2 "
            "ecuaciones:\n\n"
            "(1) Perfil controlado por límites de deformación unitaria en "
            "la rótula plástica de la base del muro — en función del "
            "desplazamiento de fluencia por piso, la deformación unitaria "
            "de fluencia del acero εy, la longitud del muro en su base lw, "
            "la longitud de la rótula plástica Lp, la altura de cada nivel "
            "Hi, la altura total Hn, y la curvatura φm correspondiente a "
            "los límites de deformación unitaria de la sección 7.2.2.\n\n"
            "(2) Perfil controlado por la deriva máxima que ocurre en el "
            "ÚLTIMO piso — en función de variables similares (desplazamiento "
            "y deriva de fluencia por piso, altura de nivel, altura total, "
            "εy, lw).\n\n"
            "[Las expresiones algebraicas exactas de ambas ecuaciones no se "
            "pudieron recuperar con precisión del texto extraído del PDF "
            "(fórmulas con múltiples subíndices y fracciones) — ver el "
            "documento oficial para la notación completa.] La segunda "
            "ecuación produce un perfil de desplazamiento controlado "
            "específicamente por la deriva máxima del último piso."
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
