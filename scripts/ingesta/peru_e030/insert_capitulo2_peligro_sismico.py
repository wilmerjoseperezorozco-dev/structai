"""
Inserta el núcleo verbatim real del Capítulo II (Peligro Sísmico, Artículos
10-14) de la norma E.030 "Diseño Sismorresistente" de Perú en
peru_e030_chunks. Segundo bloque del corpus, después del Capítulo I (ver
insert_capitulo1_disposiciones_generales.py -- mismo texto oficial del
MVCS, misma base legal de citación verbatim, Art. 9(b) del Decreto
Legislativo N° 822).

Cubre: zonificación sísmica (4 zonas, factor Z, Tabla N°1), microzonificación
y estudios de sitio, condiciones geotécnicas (5 perfiles de suelo S0-S4,
Tabla N°2), parámetros de sitio S/TP/TL (Tablas N°3 y N°4), y el factor de
amplificación sísmica C. Es el capítulo más denso en tablas y fórmulas de
toda la norma -- equivalente en importancia al Título A de NSR-10.

Nota sobre la Figura N° 1 (mapa de zonas sísmicas del Perú, Artículo 10.1):
es un gráfico, no se reproduce como texto -- el Anexo II de la norma (no
cargado todavía) trae el listado oficial de provincias/distritos por zona,
que es la fuente autoritativa y textual para resolver "¿en qué zona está
tal provincia?", no el mapa en sí.

Uso: python scripts/ingesta/peru_e030/insert_capitulo2_peligro_sismico.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo II — Peligro Sísmico"

CHUNKS = [
    {
        "id": "E030-CAP2-ART10-ZONIFICACION",
        "seccion": "Artículo 10",
        "titulo": "Zonificación (4 zonas sísmicas, factor Z, Tabla N°1)",
        "texto": """Artículo 10.- Zonificación

10.1. El territorio nacional se considera dividido en cuatro zonas, como se muestra en la Figura N° 1. La zonificación propuesta se basa en la distribución espacial de la sismicidad observada, las características generales de los movimientos sísmicos y la atenuación de éstos con la distancia epicentral, así como en la información neotectónica. El Anexo II contiene el listado de las provincias y distritos que corresponden a cada zona.

[Figura N° 1 — Mapa de Zonas Sísmicas: gráfico, no reproducido como texto; el Anexo II trae el listado textual oficial de provincias y distritos por zona.]

10.2. A cada zona se asigna un factor Z según se indica en la Tabla N° 1. Este factor se interpreta como la aceleración máxima horizontal en suelo rígido con una probabilidad de 10% de ser excedida en 50 años. El factor Z se expresa como una fracción de la aceleración de la gravedad.

Tabla N° 1 — Factores de Zona "Z": Zona 4 → Z = 0,45. Zona 3 → Z = 0,35. Zona 2 → Z = 0,25. Zona 1 → Z = 0,10.""",
    },
    {
        "id": "E030-CAP2-ART11-MICROZONIFICACION",
        "seccion": "Artículo 11",
        "titulo": "Microzonificación Sísmica y Estudios de Sitio",
        "texto": """Artículo 11.- Microzonificación Sísmica y Estudios de Sitio

11.1. Microzonificación Sísmica. 11.1.1. Son estudios multidisciplinarios que investigan los efectos de sismos y fenómenos asociados como licuación de suelos, deslizamientos, tsunamis y otros, sobre el área de interés. Los estudios suministran información sobre la posible modificación de las acciones sísmicas por causa de las condiciones locales y otros fenómenos naturales, así como las limitaciones y exigencias que como consecuencia de los estudios se considere para el diseño, construcción de edificaciones y otras obras. 11.1.2. Para los siguientes casos deben ser considerados los resultados de los estudios de microzonificación correspondientes: a) Áreas de expansión de ciudades. b) Reconstrucción de áreas urbanas destruidas por sismos y fenómenos asociados.

11.2. Estudios de Sitio. 11.2.1. Son estudios similares a los de microzonificación, aunque no necesariamente en toda su extensión. Estos estudios están limitados al lugar del proyecto y suministran información sobre la posible modificación de las acciones sísmicas y otros fenómenos naturales por las condiciones locales. Su objetivo principal es determinar los parámetros de diseño. 11.2.2. Los estudios de sitio se realizan, entre otros casos, en grandes complejos industriales, industria de explosivos, productos químicos inflamables y contaminantes. 11.2.3. No deben emplearse parámetros de diseño inferiores a los indicados en esta Norma.""",
    },
    {
        "id": "E030-CAP2-ART12_1-PERFILES_S0_S1_S2",
        "seccion": "Artículo 12.1 (S0 a S2)",
        "titulo": "Condiciones Geotécnicas — Perfiles de Suelo: S0 (Roca Dura), S1 (Roca o Suelos Muy Rígidos), S2 (Suelos Intermedios)",
        "texto": """Artículo 12.- Condiciones Geotécnicas

12.1. Perfiles de Suelo. 12.1.1. Para los efectos de esta Norma, los perfiles de suelo se clasifican tomando en cuenta la velocidad promedio de propagación de las ondas de corte (V̄s), alternativamente, para suelos granulares, el promedio ponderado de los N̄60 obtenidos mediante un ensayo de penetración estándar (SPT), o el promedio ponderado de la resistencia al corte en condición no drenada (S̄u) para suelos cohesivos. Estas propiedades se determinan para los 30 m superiores del perfil de suelo medidos desde el nivel del fondo de cimentación, como se indica en el numeral 12.2.

12.1.2. Para los suelos predominantemente granulares, se calcula N̄60 considerando solamente los espesores de cada uno de los estratos granulares. Para los suelos predominantemente cohesivos, la resistencia al corte en condición no drenada S̄u se calcula como el promedio ponderado de los valores correspondientes a cada estrato cohesivo.

12.1.3. Este método también es aplicable si se encuentran suelos heterogéneos (cohesivos y granulares). En tal caso, si a partir de N̄60 para los estratos con suelos granulares y de S̄u para los estratos con suelos cohesivos se obtienen clasificaciones de sitio distintas, se toma la que corresponde al tipo de perfil más desfavorable.

12.1.4. Los tipos de perfiles de suelos son cinco:

a) Perfil Tipo S0: Roca Dura — A este tipo corresponden las rocas sanas con velocidad de propagación de ondas de corte V̄s mayor que 1500 m/s. Las mediciones corresponden al sitio del proyecto o a perfiles de la misma formación con igual o mayor intemperismo o fracturas. Cuando se conoce que la roca dura es continua hasta una profundidad de 30 m, las mediciones de la velocidad de las ondas de corte superficiales pueden ser usadas para estimar el valor de V̄s.

b) Perfil Tipo S1: Roca o Suelos Muy Rígidos — A este tipo corresponden las rocas con diferentes grados de fracturación, de macizos homogéneos y los suelos muy rígidos con velocidades de propagación de onda de corte V̄s, entre 500 m/s y 1500 m/s, incluyéndose los casos en los que se cimienta sobre: b.1) Roca fracturada, con una resistencia a la compresión no confinada qu mayor o igual que 500 kPa (5 kg/cm²). b.2) Arena muy densa o grava arenosa densa, con N̄60 mayor que 50. b.3) Arcilla muy compacta (de espesor menor que 20 m), con una resistencia al corte en condición no drenada S̄u mayor que 100 kPa (1 kg/cm²) y con un incremento gradual de las propiedades mecánicas con la profundidad.

c) Perfil Tipo S2: Suelos Intermedios — A este tipo corresponden los suelos medianamente rígidos, con velocidades de propagación de onda de corte V̄s, entre 180 m/s y 500 m/s, incluyéndose los casos en los que se cimienta sobre: c.1) Arena densa, gruesa a media, o grava arenosa medianamente densa, con valores del SPT N̄60, entre 15 y 50. c.2) Suelo cohesivo compacto, con una resistencia al corte en condiciones no drenada S̄u, entre 50 kPa (0,5 kg/cm²) y 100 kPa (1 kg/cm²) y con un incremento gradual de las propiedades mecánicas con la profundidad.""",
    },
    {
        "id": "E030-CAP2-ART12_1-PERFILES_S3_S4_TABLA2",
        "seccion": "Artículo 12.1 (S3, S4 y Tabla N°2)",
        "titulo": "Condiciones Geotécnicas — Perfiles de Suelo: S3 (Suelos Blandos), S4 (Condiciones Excepcionales) y Tabla N°2 resumen",
        "texto": """d) Perfil Tipo S3: Suelos Blandos — Corresponden a este tipo los suelos flexibles con velocidades de propagación de onda de corte V̄s, menor o igual a 180 m/s, incluyéndose los casos en los que se cimienta sobre: d.1) Arena media a fina, o grava arenosa, con valores del SPT N̄60 menor que 15. d.2) Suelo cohesivo blando, con una resistencia al corte en condición no drenada S̄u, entre 25 kPa (0,25 kg/cm²) y 50 kPa (0,5 kg/cm²) y con un incremento gradual de las propiedades mecánicas con la profundidad. d.3) Cualquier perfil que no corresponda al tipo S4 y que tenga más de 3 m de suelo con las siguientes características: índice de plasticidad Pi mayor que 20, contenido de humedad ω mayor que 40%, resistencia al corte en condición no drenada S̄u menor que 25 kPa.

e) Perfil Tipo S4: Condiciones Excepcionales — A este tipo corresponden los suelos excepcionalmente flexibles y los sitios donde las condiciones geológicas y/o topográficas son particularmente desfavorables, en los cuales se requiere efectuar un estudio específico para el sitio. Sólo es necesario considerar un perfil tipo S4 cuando el Estudio de Mecánica de Suelos (EMS) así lo determine.

La Tabla N° 2 resume valores típicos para los distintos tipos de perfiles de suelo.

Tabla N° 2 — Clasificación de los Perfiles de Suelo: Perfil S0 → V̄s > 1500 m/s. Perfil S1 → V̄s 500 a 1500 m/s, N̄60 > 50, S̄u > 100 kPa. Perfil S2 → V̄s 180 a 500 m/s, N̄60 15 a 50, S̄u 50 a 100 kPa. Perfil S3 → V̄s < 180 m/s, N̄60 < 15, S̄u 25 a 50 kPa. Perfil S4 → Clasificación basada en el EMS (Estudio de Mecánica de Suelos).""",
    },
    {
        "id": "E030-CAP2-ART12_2_3-FORMULAS_CONSIDERACIONES",
        "seccion": "Artículo 12.2 y 12.3",
        "titulo": "Definición de los Perfiles de Suelo (fórmulas Vs, N60, Su promedio ponderado) y Consideraciones Adicionales",
        "texto": """12.2. Definición de los Perfiles de Suelo. Las expresiones de este numeral se aplican a los 30 m superiores del perfil de suelo, medidos desde el nivel del fondo de cimentación. El subíndice i se refiere a uno cualquiera de los n estratos con distintas características, m se refiere al número de estratos con suelos granulares y k al número de estratos con suelos cohesivos.

a) Velocidad Promedio de las Ondas de Corte, V̄s — Se determina con: V̄s = (suma de di, i=1 a n) / (suma de di/Vsi, i=1 a n), donde di es el espesor de cada uno de los n estratos y Vsi es la correspondiente velocidad de ondas de corte (m/s).

b) Promedio Ponderado del Ensayo Estándar de Penetración, N̄60 — Se calcula considerando solamente los estratos con suelos granulares en los 30 m superiores del perfil: N̄60 = (suma de di, i=1 a m) / (suma de di/N60i, i=1 a m), donde di es el espesor de cada uno de los m estratos con suelo granular y N60i es el correspondiente valor corregido del SPT.

c) Promedio Ponderado de la Resistencia al Corte en Condición no Drenada, S̄u — Se calcula considerando solamente los estratos con suelos cohesivos en los 30 m superiores del perfil: S̄u = (suma de di, i=1 a k) / (suma de di/Sui, i=1 a k), donde di es el espesor de cada uno de los k estratos con suelo cohesivo y Sui es la correspondiente resistencia al corte en condición no drenada (kPa).

12.3. Consideraciones Adicionales. 12.3.1. En los casos en los que no sea obligatorio realizar un Estudio de Mecánica de Suelos (EMS) o cuando no se disponga de las propiedades del suelo hasta la profundidad de 30 m, se permite que el profesional responsable estime valores adecuados sobre la base de las condiciones geotécnicas conocidas. 12.3.2. En el caso de estructuras con cimentaciones profundas a base de pilotes, el perfil de suelo es el que corresponda a los estratos en los 30 m por debajo del extremo superior de los pilotes.""",
    },
    {
        "id": "E030-CAP2-ART13-PARAMETROS_SITIO",
        "seccion": "Artículo 13",
        "titulo": "Parámetros de Sitio S, TP y TL (Tablas N°3 y N°4)",
        "texto": """Artículo 13.- Parámetros de Sitio (S, TP y TL)

Se considera el tipo de perfil que mejor describa las condiciones locales, utilizándose los correspondientes valores del factor de amplificación del suelo S y de los períodos TP y TL dados en las Tablas N° 3 y N° 4.

Tabla N° 3 — Factor de Suelo "S" (por Zona y Perfil): Zona 4 → S0=0,80, S1=1,00, S2=1,05, S3=1,10. Zona 3 → S0=0,80, S1=1,00, S2=1,15, S3=1,20. Zona 2 → S0=0,80, S1=1,00, S2=1,20, S3=1,40. Zona 1 → S0=0,80, S1=1,00, S2=1,60, S3=2,00.

Tabla N° 4 — Períodos "TP" y "TL" (por Perfil de suelo): Perfil S0 → TP=0,3 s, TL=3,0 s. Perfil S1 → TP=0,4 s, TL=2,5 s. Perfil S2 → TP=0,6 s, TL=2,0 s. Perfil S3 → TP=1,0 s, TL=1,6 s.""",
    },
    {
        "id": "E030-CAP2-ART14-FACTOR_C",
        "seccion": "Artículo 14",
        "titulo": "Factor de Amplificación Sísmica (C)",
        "texto": """Artículo 14.- Factor de Amplificación Sísmica (C)

De acuerdo a las características de sitio, se define el factor de amplificación sísmica (C) por las siguientes expresiones: si T < TP entonces C = 2,5. Si TP < T < TL entonces C = 2,5 · (TP/T). Si T > TL entonces C = 2,5 · (TP·TL/T²).

T es el período de acuerdo al numeral 28.4, concordado con el numeral 29.1.

Este coeficiente se interpreta como el factor de amplificación de la aceleración estructural respecto de la aceleración en el suelo.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite (ej. el bloque de un perfil de suelo completo con
    sub-criterios) se divide por oracion, y si aun asi excede, por coma."""
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
    sb.table("peru_e030_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en peru_e030_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
