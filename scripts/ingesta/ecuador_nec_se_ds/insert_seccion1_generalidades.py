"""
Inserta el núcleo verbatim real de la Sección 1 (Generalidades: 1.1
Introducción y 1.2 Definiciones) de la norma NEC-SE-DS "Peligro Sísmico,
Diseño Sismo Resistente" de Ecuador (Norma Ecuatoriana de la
Construcción) en ecuador_nec_se_ds_chunks.

Primer corpus de Ecuador en el programa de replicabilidad internacional
de StructAI, después de Perú (E.030, ver scripts/ingesta/peru_e030/).
Texto extraído directamente del PDF oficial del MIDUVI/MIT
(www.mit.gob.ec) -- a diferencia del PDF de Perú (escaneado, requirió
lectura visual página por página), este es un PDF digital real con texto
extraíble, verificado con pypdf antes de transcribir (141 páginas,
extracción limpia).

Base legal para citar verbatim sin riesgo de derechos de autor: el
Código Orgánico de la Economía Social del Conocimiento, la Creatividad y
la Innovación (COESC+i / "Código Ingenios", 2016) excluye del derecho de
autor los textos oficiales de orden legislativo, administrativo o
judicial. La NEC-SE-DS se aprobó por Acuerdo Ministerial Nro. 0028 del
MIDUVI (19-ago-2014), publicado en el Registro Oficial Año II N° 319
(26-ago-2014) -- misma categoría legal que NSR-10 (Colombia) y E.030
(Perú). Verificado 2026-08-25 con dos fuentes independientes, no asumido
por analogía con Perú (la Decisión 351 de la Comunidad Andina, marco
regional compartido, NO trae esta exclusión en sí misma).

Alcance de hoy: 1.1 Introducción + 1.2 Definiciones completo (~44
términos del glosario técnico). La sección 1.3 (Unidades y Simbología --
una tabla extensa de símbolos matemáticos con subíndices) y 1.4 (Contexto
normativo) quedan para una siguiente ronda, mismo patrón incremental
usado con Perú.

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion1_generalidades.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 1 — Generalidades"

CHUNKS = [
    {
        "id": "NECSEDS-S1-1_1-INTRODUCCION",
        "seccion": "1.1",
        "titulo": "Introducción",
        "texto": """1. Generalidades

1.1. Introducción

En este capítulo de las Normas Ecuatorianas de Construcción, se presentan los requerimientos y metodologías que deben ser aplicados al diseño sismo resistente de edificios principalmente, y en segundo lugar, a otras estructuras; complementadas con normas extranjeras reconocidas.

Este capítulo pone a disposición de los calculistas, diseñadores y profesionales del sector de la construcción, las herramientas de cálculo, basándose en conceptos de Ingeniería Sísmica y que les permiten conocer las hipótesis de cálculo que están adoptando para la toma de decisiones en la etapa de diseño.

Los lineamientos y directrices para la elaboración de la memoria de cálculo se encuentran definidos en la sección 2.3.

Este capítulo se constituirá como un documento de permanente actualización, necesario para el cálculo y diseño sismo resistente de estructuras, considerando el potencial sísmico del Ecuador.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-NOTAS",
        "seccion": "1.2",
        "titulo": "Definiciones — notas de aplicación",
        "texto": """1.2. Definiciones

NOTA 1: Las definiciones incluidas en este capítulo deben ser utilizadas literalmente durante todo el proceso de cálculo y diseño sismo resistente, incluyendo la etapa de elaboración de la memoria de cálculo y de los planos estructurales.

NOTA 2: Otras definiciones de elementos o de conceptos de cálculo y diseño sismo resistente que se utilicen y que no estén incluidas en este capítulo, deben corresponder a conceptos técnicos reconocidos en el campo del diseño sísmico por organismos nacionales o internacionales de normalización, institutos o centros de investigación igualmente reconocidos.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-A_D",
        "seccion": "1.2 (A-D)",
        "titulo": "Definiciones: Altura de piso, Acelerogramas, Base de la estructura, Coeficiente de importancia, Cortante basal de diseño, Cortante de piso, Deriva de piso, Ductilidad global/local",
        "texto": """ALTURA DE PISO — Es la distancia vertical medida entre el terminado de la losa de piso o de nivel de terreno y el terminado de la losa del nivel inmediatamente superior. En el caso que el nivel inmediatamente superior corresponda a la cubierta de la edificación esta medida se llevará hasta el nivel de enrace de la cubierta cuando esta sea inclinada o hasta al nivel de la impermeabilización o elemento de protección contra la intemperie cuando la cubierta sea plana. En los casos en los cuales la altura de piso medida como se indica anteriormente exceda 6 m, se considerará para efectos de calcular el número de pisos como dos pisos. Se permite que para el primer piso aéreo la altura del piso se mida desde la corona del muro de contención de la edificación nueva contra el paramento que está en la colindancia, cuando éste exista.

ACELEROGRAMAS — Serie temporal o cronológica de valores de aceleración que se han registrado durante un sismo. En el registro se puede notar una aceleración máxima y la duración de la excitación sísmica.

BASE DE LA ESTRUCTURA — Nivel al cual se considera que la acción sísmica actúa sobre la estructura.

COEFICIENTE DE IMPORTANCIA — Coeficiente relativo a las consecuencias de un daño estructural y al tipo de ocupación.

CORTANTE BASAL DE DISEÑO — Fuerza total de diseño por cargas laterales, aplicada en la base de la estructura, resultado de la acción del sismo de diseño con o sin reducción, de acuerdo con las especificaciones de la presente norma.

CORTANTE DE PISO — Sumatoria de las fuerzas laterales de todos los pisos superiores al nivel considerado.

DERIVA DE PISO — Desplazamiento lateral relativo de un piso -en particular por la acción de una fuerza horizontal- con respecto al piso consecutivo, medido en dos puntos ubicados en la misma línea vertical de la estructura. Se calcula restando del desplazamiento del extremo superior el desplazamiento del extremo inferior del piso.

DUCTILIDAD GLOBAL — Capacidad de la estructura para deformarse más allá del rango elástico, sin pérdida sustancial de su resistencia y rigidez, ante cargas laterales estáticas o cíclicas o ante la ocurrencia de una acción sísmica.

DUCTILIDAD LOCAL — Capacidad de una sección transversal o de un elemento estructural, para deformarse más allá del rango elástico, sin pérdida sustancial de su resistencia y rigidez, ante cargas laterales estáticas o cíclicas o ante la ocurrencia de una acción sísmica.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-E_H",
        "seccion": "1.2 (E-H)",
        "titulo": "Definiciones: Efectos P-Δ, Espectro de respuesta, Estructura, Estructura disipativa, Estructuras esenciales, Factor de sobre resistencia, Factor de redundancia, Fuerzas sísmicas de diseño, Histéresis",
        "texto": """EFECTOS SECUNDARIOS P-Δ — Son los efectos de segundo orden en los desplazamientos horizontales y fuerzas internas de la estructura, causados por la acción de las cargas verticales de la edificación al verse desplazadas horizontalmente.

ESPECTRO DE RESPUESTA PARA DISEÑO — El espectro de diseño puede representarse mediante un espectro de respuesta basado en las condiciones geológicas, tectónicas, sismológicas y del tipo de suelo asociadas con el sitio de emplazamiento de la estructura. Es un espectro de tipo elástico para una fracción de amortiguamiento respecto al crítico del 5%, utilizado con fines de diseño para representar los efectos dinámicos del sismo de diseño.

ESTRUCTURA — Conjunto de elementos estructurales ensamblados para resistir cargas verticales, sísmicas y de cualquier otro tipo. Las estructuras pueden clasificarse en estructuras de edificación y otras estructuras distintas a las de edificación (puentes, tanques, etc.).

ESTRUCTURA DISIPATIVA — Estructura capaz de disipar la energía por un comportamiento histerético dúctil y/o por otros mecanismos.

ESTRUCTURAS ESENCIALES — Son las estructuras que deben permanecer operativas luego de un terremoto para atender emergencias.

FACTOR DE SOBRE RESISTENCIA — Se define el factor de sobre resistencia como la relación entre el cortante basal último que es capaz de soportar la estructura con relación al cortante basal de diseño.

FACTOR DE REDUNDANCIA — El factor de redundancia mide la capacidad de incursionar la estructura en el rango no lineal. La capacidad de una estructura en redistribuir las cargas de los elementos con mayor solicitación a los elementos con menor solicitación. Se evalúa como la relación entre el cortante basal máximo con respecto al cortante basal cuando se forma la primera articulación plástica.

FUERZAS SÍSMICAS DE DISEÑO — Fuerzas laterales que resultan de distribuir adecuadamente el cortante basal de diseño en toda la estructura, según las especificaciones de esta norma.

HISTÉRESIS — Fenómeno por medio del cual dos, o más, propiedades físicas se relacionan de una manera que depende de la historia de su comportamiento previo. En general hace referencia al comportamiento de los materiales estructurales cuando se ven sometidos a deformaciones o esfuerzos que están fuera del rango lineal, o elástico, de comportamiento. Una gran parte de la energía que es capaz de disipar el material estructural en el rango inelástico de respuesta se asocia con el área comprendida dentro de los ciclos de histéresis.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-I_P",
        "seccion": "1.2 (I-P)",
        "titulo": "Definiciones: Impedancia, Licuación, Método de diseño por capacidad, Muros estructurales/mampostería, Niveles de seguridad de vida/prevención de colapso, Peligrosidad sísmica, Período de vibración, PGA, Piso blando/débil",
        "texto": """IMPEDANCIA (SISMICA) — Corresponde al producto de la densidad por la velocidad sísmica, que varía entre las diferentes capas de rocas. La diferencia de impedancia entre las capas de rocas afecta el coeficiente de reflexión.

LICUACIÓN — Fenómeno mediante el cual un depósito de suelo, sea ésta grava, arena, limo o arcillas de baja plasticidad saturadas, pierde gran parte de su resistencia al esfuerzo cortante debido al incremento de presión de poros bajo condiciones de carga no-drenada, sean monotónicas o cíclicas.

MÉTODO DE DISEÑO POR CAPACIDAD — Método de diseño eligiendo ciertos elementos del sistema estructural, diseñados y estudiados en detalle de manera apropiada para asegurar la disipación energética bajo el efecto de deformaciones importantes, mientras todos los otros elementos estructurales resisten suficientemente para que las disposiciones elegidas para disipar las energía estén aseguradas.

MURO ESTRUCTURAL (DIAFRAGMA VERTICAL) — Pared construida a todo lo alto de la estructura, diseñada para resistir fuerzas sísmicas en su propio plano, cuyo diseño proporcionará un comportamiento dúctil ante cargas sísmicas.

MURO DE MAMPOSTERÍA CONFINADA — Mampostería construida rígidamente rodeada en sus cuatro lados por columnas y vigas de hormigón armado o de mampostería armada no proyectados para que trabajen como pórticos resistentes a flexión.

MURO DE MAMPOSTERÍA REFORZADA — Muro de cortante de mampostería, reforzado con varillas de acero, que forma parte del sistema estructural y que no necesita de elementos de borde para su confinamiento.

NIVEL DE SEGURIDAD DE VIDA (sismo de diseño) — Proteger la vida de sus ocupantes ante un terremoto de 475 años de período de retorno (de probabilidad anual de excedencia 0.002 en las curvas de peligro sísmico). Véase también "sismo de diseño".

NIVEL DE PREVENCIÓN DE COLAPSO (sismo extremo) — Impedir el colapso de la estructura ante un terremoto de 2500 años de período de retorno (sismo severo, probabilidad anual de excedencia 0.0004 en las curvas de peligro sísmico).

PELIGROSIDAD SÍSMICA (PELIGRO SÍSMICO) — Probabilidad de excedencia, dentro de un período específico de tiempo y dentro de una región determinada, de movimientos del suelo cuyos parámetros aceleración, velocidad, desplazamiento, magnitud o intensidad son cuantificados.

PERÍODO DE VIBRACIÓN — Es el tiempo que transcurre dentro de un movimiento armónico ondulatorio, o vibratorio, para que el sistema vibratorio vuelva a su posición original considerada luego de un ciclo de oscilación.

PERÍODO DE VIBRACIÓN FUNDAMENTAL — Es el mayor período de vibración de la estructura en la dirección horizontal de interés.

PGA (Peak Ground Acceleration) — Aceleración sísmica máxima en el terreno.

PISO BLANDO — Piso en el cual su rigidez lateral es menor que el 70% de la rigidez lateral del piso inmediato superior.

PISO DÉBIL — Piso en el cual su resistencia lateral es menor que el 80% de la resistencia del piso inmediato superior.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-PORTICOS",
        "seccion": "1.2 (Pórticos especiales)",
        "titulo": "Definiciones: Pórtico Especial Sismo Resistente (simple, con diagonales rigidizadoras, con muros estructurales/sistemas duales, con vigas banda)",
        "texto": """PÓRTICO ESPECIAL SISMO RESISTENTE — Estructura formada por columnas y vigas descolgadas del sistema de piso, que resiste cargas verticales y de origen sísmico, en la cual tanto el pórtico como la conexión viga-columna son capaces de resistir tales fuerzas y está especialmente diseñado y detallado para presentar un comportamiento estructural dúctil.

PÓRTICO ESPECIAL SISMO RESISTENTE CON DIAGONALES RIGIDIZADORAS — Sistema resistente de una estructura compuesta tanto por pórticos especiales sismo resistentes como por diagonales estructurales, concéntricas o no, adecuadamente dispuestas espacialmente, diseñados todos ellos para resistir fuerzas sísmicas. Se entiende como una adecuada disposición el ubicar las diagonales lo más simétricamente posible, hacia la periferia y en todo lo alto de la estructura. Para que la estructura se considere pórtico con diagonales se requiere que el sistema de diagonales absorba al menos el 75% del cortante basal en cada dirección.

PÓRTICO ESPECIAL SISMO RESISTENTE CON MUROS ESTRUCTURALES (SISTEMAS DUALES) — Sistema resistente de una estructura compuesta tanto por pórticos especiales sismo resistentes como por muros estructurales adecuadamente dispuestos espacialmente, diseñados todos ellos para resistir fuerzas sísmicas. Se entiende como una adecuada disposición ubicar los muros estructurales lo más simétricamente posible, hacia la periferia y que mantienen su longitud en planta en todo lo alto de la estructura. Para que la estructura se considere como un sistema dual se requiere que los muros absorban al menos el 75% del corte basal en cada dirección.

PÓRTICO ESPECIAL SISMO RESISTENTE CON VIGAS BANDA — Estructura compuesta por columnas y losas con vigas bandas (del mismo espesor de la losa) que resisten cargas verticales y de origen sísmico, en la cual tanto el pórtico como la conexión losa-columna son capaces de resistir tales fuerzas y está especialmente diseñada y detallada para presentar un comportamiento estructural dúctil. Para ser aceptable la utilización de la viga banda, ésta debe tener un peralte no menor a 0.25 m.""",
    },
    {
        "id": "NECSEDS-S1-1_2-DEFINICIONES-R_Z",
        "seccion": "1.2 (R-Z)",
        "titulo": "Definiciones: Resistencia/Rigidez lateral de piso, Respuesta elástica, Semi espacio, Sismo de diseño, Sistemas de control de respuesta sísmica, Sobre resistencia, factor Z, Zonas disipativas/sísmicas",
        "texto": """RESISTENCIA LATERAL DEL PISO — Sumatoria de la capacidad a corte de los elementos estructurales verticales del piso.

RESPUESTA ELÁSTICA — Parámetros relacionados con fuerzas y deformaciones determinadas a partir de un análisis elástico, utilizando la representación del sismo de diseño sin reducción, de acuerdo con las especificaciones de la presente norma.

RIGIDEZ LATERAL DE PISO — Sumatoria de las rigideces a corte de los elementos verticales estructurales del piso.

RIGIDEZ EFECTIVA — Proviene de una relación entre período, masa y rigidez para sistemas de un grado de libertad.

SEMI ESPACIO — Se define como aquella profundidad que no ejerce participación en la respuesta dinámica del sitio, cuyo contraste de impedancia es menor o igual que 0.5 (α ≤ 0.5).

SISMO DE DISEÑO — Evento sísmico que tiene una probabilidad del 10% de ser excedido en 50 años (período de retorno de 475 años), determinado a partir de un análisis de la peligrosidad sísmica del sitio de emplazamiento de la estructura o a partir de un mapa de peligro sísmico. Para caracterizar este evento, puede utilizarse un grupo de acelerogramas con propiedades dinámicas representativas de los ambientes tectónicos, geológicos y geotécnicos del sitio, conforme lo establece esta norma. Los efectos dinámicos del sismo de diseño pueden modelarse mediante un espectro de respuesta para diseño, como el proporcionado en esta norma.

SISTEMAS DE CONTROL DE RESPUESTA SÍSMICA — Son sistemas y dispositivos adaptados a las estructuras que, al modificar las características dinámicas de las mismas, controlan y disipan parte de la energía de entrada de un sismo y permiten reducir la respuesta sísmica global de la estructura y mitigar su daño ante sismos severos. Pueden clasificarse en 3 grupos: sistemas de aislamiento sísmico, sistemas de disipación pasiva de energía y sistemas de control activo.

SOBRE RESISTENCIA — La sobre resistencia desarrollada en las rótulas plásticas indica valores de resistencia, por encima de los nominales especificados. Los factores de sobre resistencia tienen en cuenta principalmente las variaciones entre la tensión de fluencia especificada y la real, el endurecimiento por deformación del acero y el aumento de resistencia por confinamiento del hormigón.

Z (factor) — El valor de Z de cada zona sísmica representa la aceleración máxima en roca esperada para el sismo de diseño, expresada como fracción de la aceleración de la gravedad.

ZONAS DISIPATIVAS — Partes predefinidas de una estructura disipativa donde se localiza principalmente la aptitud estructural a disipar energía (también llamadas zonas críticas).

ZONAS SÍSMICAS — El Ecuador se divide en seis zonas sísmicas, caracterizada por el valor del factor de zona Z. Todo el territorio ecuatoriano está catalogado como de amenaza sísmica alta, con excepción del nororiente que presenta una amenaza sísmica intermedia y del litoral ecuatoriano que presenta una amenaza sísmica muy alta.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ y
# scripts/ingesta/peru_e030/: el tokenizer real (no una aproximación por
# caracteres) es lo único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n, cada uno un termino del
    glosario ya completo), empacando parrafos consecutivos hasta el
    limite de tokens reales. Un parrafo que por si solo excede el limite
    se divide por oracion, y si aun asi excede, por coma."""
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
                "titulo": chunk["titulo"],
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
    print(f"\nSubchunks que exceden 128 tokens (se truncarian en la busqueda): {excedidos}/{len(rows)}")

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
