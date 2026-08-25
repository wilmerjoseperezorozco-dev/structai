"""
Inserta el núcleo verbatim real de la Sección 4.2-4.3 (Filosofía
tradicional de diseño sismo resistente y métodos de análisis) de la
norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks. Quinta sección
más pesada de lo que faltaba (7 páginas, 42-48 del documento).

4.1 (Tabla 6, coeficiente de importancia) ya estaba cargada de una
sesión anterior (`NECSEDS-S4_1-TABLA6-CATEGORIA_IMPORTANCIA-*`, 6
subchunks) -- confirmado por consulta directa antes de escribir este
script, no se repite.

Cubre: 4.2.1 (sismo de diseño, 475 años), 4.2.2 (Tabla 7, 4 niveles de
amenaza sísmica), 4.2.3 (efectos lineales/no lineales), 4.2.4 (3
niveles de desempeño: servicio/daño/colapso), 4.2.5 (estructuras
esenciales y de ocupación especial, 2500 años), 4.2.6 (los 3 requisitos
del diseño: no colapso E≤Rd, limitación de daños ΔM<ΔM_máxima,
ductilidad), 4.3.1-4.3.3 (los 2 métodos principales DBF/DBD, sistema
elástico equivalente, factor de reducción R=Rμ·RΩ).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion4_2_4_3_filosofia_metodos.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 4.2-4.3 — Filosofía de Diseño y Métodos de Análisis"

CHUNKS = [
    {
        "id": "NECSEDS-S4_2_1-SISMO_DE_DISENO",
        "seccion": "4.2.1",
        "titulo": "Sismo de diseño: 10% de probabilidad de excedencia en 50 años, período de retorno 475 años",
        "texto": (
            "NEC-SE-DS, Sección 4.2.1 — Sismo de diseño. El sismo de "
            "diseño es un evento sísmico con 10% de probabilidad de ser "
            "excedido en 50 años, equivalente a un período de retorno de "
            "475 años. Se determina a partir de un análisis de "
            "peligrosidad sísmica del sitio de emplazamiento, o a partir "
            "de un mapa de peligro sísmico (sección 3.1.1). Sus efectos "
            "dinámicos pueden modelarse mediante un espectro de "
            "respuesta de diseño (sección 3.3.1), o con un grupo de "
            "acelerogramas con propiedades dinámicas representativas de "
            "los ambientes tectónicos, geológicos y geotécnicos del "
            "sitio (sección 3.2)."
        ),
    },
    {
        "id": "NECSEDS-S4_2_2-TABLA7-NIVELES_AMENAZA_SISMICA",
        "seccion": "4.2.2 (Tabla 7)",
        "titulo": "4 niveles de amenaza sísmica: frecuente (72 años), ocasional (225 años), raro=sismo de diseño (475 años), muy raro/extremo (2.500 años)",
        "texto": (
            "NEC-SE-DS, Sección 4.2.2 — Niveles de amenaza sísmica. "
            "Tabla 7 — Niveles de amenaza sísmica (verbatim):\n"
            "  Nivel 1, Frecuente (menor): probabilidad de excedencia en "
            "50 años = 50%, período de retorno Tr = 72 años, tasa de "
            "excedencia 1/Tr = 0,01389.\n"
            "  Nivel 2, Ocasional (moderado): 20%, Tr = 225 años, tasa = "
            "0,00444.\n"
            "  Nivel 3, Raro (severo): 10%, Tr = 475 años, tasa = "
            "0,00211. Este es el sismo de diseño (sección 4.2.1).\n"
            "  Nivel 4, Muy raro (extremo): 2%, Tr = 2.500 años, tasa = "
            "0,0004. Ver sección 4.2.5 (estructuras esenciales/especiales)."
        ),
    },
    {
        "id": "NECSEDS-S4_2_3-EFECTOS_DE_LOS_SISMOS",
        "seccion": "4.2.3",
        "titulo": "Comportamiento lineal (rigidez elástica) vs. no lineal (propiedades inelásticas + historia de desplazamientos) según capacidad resistente",
        "texto": (
            "NEC-SE-DS, Sección 4.2.3 — Efectos de los sismos. La "
            "producción de terremotos incluye fuerzas y desplazamientos. "
            "Según las estructuras, se observan comportamientos "
            "(respuestas) lineales y no lineales: si la estructura tiene "
            "capacidad resistente suficiente, la relación "
            "fuerzas/desplazamientos es lineal, dada por la rigidez "
            "elástica del sistema; en caso contrario, la relación es no "
            "lineal, y depende de la rigidez elástica, de las propiedades "
            "inelásticas, y de la historia de los desplazamientos "
            "impuestos en la estructura."
        ),
    },
    {
        "id": "NECSEDS-S4_2_4-NIVELES_DESEMPENO_SISMICO",
        "seccion": "4.2.4",
        "titulo": "3 niveles de desempeño estructural: servicio (72 años, sin daño), daño (225 años, seguridad de vida), colapso (475 años, prevención de colapso)",
        "texto": (
            "NEC-SE-DS, Sección 4.2.4 — Objetivos y niveles de desempeño "
            "sísmico. La filosofía de diseño tradicional establece 3 "
            "niveles de desempeño estructural, ante 3 sismos de análisis, "
            "para todas las estructuras:\n\n"
            "1) Nivel de servicio (sismo menor, período de retorno 72 "
            "años): objetivo — que no ocurra ningún daño, ni en "
            "elementos estructurales ni no estructurales.\n\n"
            "2) Nivel de daño (sismo moderado, período de retorno 225 "
            "años — nota: el texto original lo etiqueta también con "
            "'72 años' en un punto, discrepancia real del documento, se "
            "transcribe tal cual sin resolverla por invención): "
            "objetivos — seguridad de vida, protección de los ocupantes, "
            "garantía de funcionalidad. Se espera que la estructura "
            "trabaje en el límite de su capacidad resistente elástica: "
            "no hay daño estructural, pero sí en elementos no "
            "estructurales.\n\n"
            "3) Nivel de colapso (sismo severo = sismo de diseño, "
            "período de retorno 475 años; aplica a estructuras "
            "esenciales o de ocupación especial, sección 4.2.5): "
            "objetivo — prevención de colapso. Se esperan incursiones en "
            "el rango inelástico con daño, pero sin llegar al colapso; "
            "cierto grado de daño estructural y daño considerable en "
            "elementos no estructurales.\n\n"
            "Síntesis (tasa anual de excedencia): Servicio — ningún daño "
            "estructural ni no estructural, tasa 0,023. Daño — ningún "
            "daño estructural, daños no estructurales, tasa 0,014. "
            "Colapso — cierto grado de daño estructural, daños "
            "considerables no estructurales, tasa 0,002."
        ),
    },
    {
        "id": "NECSEDS-S4_2_5-OCUPACION_ESPECIAL_ESENCIAL",
        "seccion": "4.2.5",
        "titulo": "Estructuras esenciales y de ocupación especial: fuerzas sísmicas no menores al DBF estático; ocupación especial verifica no-colapso a 2.500 años; esenciales verifican daño (475 años) Y no-colapso (2.500 años)",
        "texto": (
            "NEC-SE-DS, Sección 4.2.5 — Estructuras de ocupación especial "
            "y esencial. Las categorías de uso y sus coeficientes de "
            "importancia I están en la sección 4.1 (Tabla 6). Estas 2 "
            "categorías deben limitar los daños estructurales, elevando "
            "el nivel de protección para mantenerse operacionales aún "
            "después del sismo de diseño. Se diseñan con un nivel de "
            "fuerzas sísmicas no menor que: (a) las estipuladas en el "
            "método estático del DBF (sección 6); ni (b) las que "
            "resulten de la aceleración máxima y las aceleraciones "
            "espectrales máximas esperadas en el sitio, según las curvas "
            "de peligro sísmico (sección 3.1.2) para un período de "
            "retorno de 475 años, sin aplicar el factor de importancia I.\n\n"
            "a) Estructuras de ocupación especial: se verifica un "
            "correcto desempeño sísmico en rango inelástico que impida "
            "el colapso (nivel de prevención de colapso) ante un "
            "terremoto de 2.500 años de período de retorno (probabilidad "
            "anual de excedencia 0,0004).\n\n"
            "b) Estructuras esenciales: se verifica el desempeño sísmico "
            "en rango inelástico para 2 condiciones: limitación de daño "
            "(nivel de seguridad de vida) ante un terremoto de 475 años "
            "(probabilidad anual 0,00211), Y no-colapso (nivel de "
            "prevención de colapso) ante un terremoto de 2.500 años "
            "(probabilidad anual 0,00004). El efecto de sitio ante este "
            "terremoto debe estudiarse localmente para suelos tipo F "
            "(apéndice 10.6.4). La caracterización y verificación de este "
            "nivel de desempeño se describe en la norma NEC-SE-RE "
            "(Rehabilitación Sísmica de Estructuras).\n\n"
            "c) Síntesis: ocupación especial verifica solo Colapso (tasa "
            "0,00004); estructuras esenciales verifican Daño (tasa "
            "0,00211) Y Colapso (tasa 0,00004) — doble verificación."
        ),
    },
    {
        "id": "NECSEDS-S4_2_6-REQUISITOS_DISENO_SISMORRESISTENTE",
        "seccion": "4.2.6",
        "titulo": "3 requisitos del diseño: no colapso (E≤Rd), limitación de daños (ΔM<ΔM_máxima), ductilidad (diseño por capacidad o dispositivos de control sísmico)",
        "texto": (
            "NEC-SE-DS, Sección 4.2.6 — Requisitos del diseño sismo "
            "resistente. La filosofía de diseño se traduce en 3 "
            "requisitos:\n\n"
            "a) No colapso — condición de resistencia: la estructura "
            "(según NEC-SE-HM hormigón armado, NEC-SE-AC acero, "
            "NEC-SE-MP mampostería estructural, NEC-SE-MD madera) y su "
            "cimentación (NEC-SE-GM geotecnia) no deben rebasar ningún "
            "estado límite de falla — no colapso ante un sismo severo. "
            "Una estructura satisface el estado último si todos los "
            "factores de compresión, tracción, cortante, torsión y "
            "flexión están por debajo del factor de resistencia de la "
            "sección. Formulación general: E ≤ Rd, donde E = efectos del "
            "sismo (incluye efectos de segundo orden) y Rd = resistencia "
            "de diseño del elemento (según NEC-SE-HM/AC/MP/MD). Aplica a "
            "niveles de amenaza sísmica 1 a 3 (estructuras normales y de "
            "ocupación especial) y 4 (estructuras esenciales).\n\n"
            "b) Limitación de daños — deformaciones: la estructura debe "
            "presentar derivas de piso inferiores a las admisibles: "
            "ΔM < ΔM máxima, donde ΔM = desplazamiento máximo horizontal "
            "inelástico. Aplica a niveles de sismo 1 y 2 (estructuras "
            "normales y de ocupación especial) y 3 (ocupación especial y "
            "esenciales). Deformaciones relevantes: derivas de piso, "
            "flechas.\n\n"
            "c) Ductilidad: capacidad de disipar energía de deformación "
            "inelástica, mediante técnicas de diseño por capacidad "
            "(verificando deformaciones plásticas) o dispositivos de "
            "control sísmico. Los efectos se determinan en NEC-SE-DS y "
            "NEC-SE-CG; las resistencias y deformaciones se determinan en "
            "NEC-SE-HA, NEC-SE-MP y NEC-SE-AC."
        ),
    },
    {
        "id": "NECSEDS-S4_3_1_4_3_2-METODOS_DE_ANALISIS",
        "seccion": "4.3.1-4.3.2",
        "titulo": "3 métodos de análisis: DBF (estático, estructuras regulares), DBD (elasto-plástico equivalente, se privilegia en irregulares), método de sistemas de aislamiento/control",
        "texto": (
            "NEC-SE-DS, Sección 4.3.1 — Vista general. Se definen: las "
            "categorías de edificio (normal, esencial, especial; "
            "secciones 4.1 y 4.2), y la conformidad/regularidad "
            "estructural (sección 5.3).\n\n"
            "Sección 4.3.2 — Los 2 principales métodos de análisis:\n"
            "  Diseño Basado en Fuerzas (DBF): método estático, usado "
            "según condiciones de regularidad (sección 6).\n"
            "  Diseño Directo Basado en Desplazamientos (DBD): método "
            "lineal equivalente (elasto-plástico) (sección 7). Para "
            "estructuras irregulares, se privilegia el DBD.\n"
            "  Método de cálculo estático de fuerzas sísmicas para "
            "sistemas específicos (sistemas de control y aislamiento a "
            "la base): el diseñador se apoya en los capítulos 13 y 15 "
            "del BSSC 2004 (sección 8).\n\n"
            "El análisis de mecanismos plásticos se hace mediante diseño "
            "por capacidad. Se permite el uso de otros procedimientos "
            "(análisis no lineales estáticos o dinámicos) que requieren "
            "principios avanzados de Dinámica de Estructuras e Ingeniería "
            "Sísmica — la norma NO describe estos métodos; deben ser "
            "aplicados por especialistas que justifiquen la experiencia "
            "necesaria. Para otros tipos de construcciones (puentes, "
            "tanques, etc.) se proponen referencias en la sección 8.4."
        ),
    },
    {
        "id": "NECSEDS-S4_3_3-SISTEMA_ELASTICO_EQUIVALENTE",
        "seccion": "4.3.3",
        "titulo": "Linealización equivalente del comportamiento no lineal real (5% amortiguamiento viscoso); factor de reducción R = reducción por ductilidad Rμ × sobrerresistencia RΩ",
        "texto": (
            "NEC-SE-DS, Sección 4.3.3 — Sistema elástico equivalente. "
            "Tanto en el DBF (sección 6) como en el DBD (sección 7), la "
            "respuesta real no lineal e inelástica de las estructuras se "
            "'linealiza' (Figura 7: (a) amortiguamiento viscoso de 5%, "
            "(b) amortiguamiento viscoso mayor a 5%).\n\n"
            "En el DBF, el sistema real se sustituye por un sistema "
            "elástico con 5% de amortiguamiento viscoso, cuya rigidez K y "
            "período T se estiman asumiendo: en hormigón, una reducción "
            "de inercia por agrietamiento de las secciones (sección "
            "6.1.8); en acero, los espesores de las placas.\n\n"
            "Cuando el sistema elástico se somete a las acciones sísmicas "
            "de diseño, se desarrolla un cortante basal elástico VE que "
            "se reduce al cortante basal de fluencia V (sección 6.3.2) "
            "mediante un factor de reducción R, que incluye: reducciones "
            "de demanda por ductilidad Rμ, y sobrerresistencia RΩ "
            "(también puede incluir reducciones por redundancia)."
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
