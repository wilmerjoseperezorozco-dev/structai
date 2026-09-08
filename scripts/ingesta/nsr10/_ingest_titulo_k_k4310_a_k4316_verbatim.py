"""
NSR-10 Titulo K, numerales K.4.3.10 a K.4.3.16 -- cierre del capitulo K.4.3
(Seguridad), el ultimo hueco real confirmado en la re-auditoria estricta
2026-09-09 (ver docs/fuentes-normativas.md, fila de Titulo K).

Hallazgo original: K.4.3.1-9 ya estaban en verbatim completo, pero
K.4.3.10 a K.4.3.16 (Vidrio estructural y de piso, Revestimiento con
vidrios, Vidrios en cubierta, y 3 numerales de normas tecnicas
referenciadas -- Colombianas/ASTM/Otras) nunca se ingestaron, pese a que
una fila anterior de docs/fuentes-normativas.md decia "K.4.3 completo"
desde 2026-09-07 -- correccion real ya documentada.

Fuente: NSR-10-1571-1625.pdf (Drive id 1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z,
mismo archivo ya usado para K.2/K.3/K.4.1/K.4.2), paginas internas
K-61 a K-63 (paginas PDF 53-55), leidas visualmente pagina por pagina --
es el final real del capitulo, el PDF no continua despues.

Troceo conservador por numeral (no un solo chunk grande) para respetar
el limite real de 128 tokens del modelo de embeddings desde el primer
intento -- K.4.3.15 (ASTM, ~17 normas) se divide en 2 piezas por ser la
lista mas larga.

Uso: python _ingest_titulo_k_k4310_a_k4316_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título K — Otros Requisitos Complementarios"

CHUNKS = [
    {
        "id": "NSR10-K-K_4_3_10_a_11_demolicion_estructural",
        "seccion": "K.4.3.10 a K.4.3.11 (Demolición y Vidrio Estructural y de Piso)",
        "titulo": "Extracción de vidrios antes de demoliciones y requisitos de dimensiones/perfilado para vidrio estructural y de piso.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.10 — Antes de iniciarse una "
            "demolición, es necesario extraer todos los vidrios que hubiera en la "
            "obra.\n\n"
            "K.4.3.11 — VIDRIO ESTRUCTURAL Y DE PISO — El vidrio estructural y de "
            "piso, deberá tener dimensiones no mayores de 0.30 m de lado y debe "
            "ser capaz de soportar la sobrecarga prevista para la estructura en "
            "donde está ubicado. Los vidrios deberán estar perfilados cuando "
            "vayan dentro de soportes de concreto armado. En caso de que los "
            "vidrios se apoyen en estructura metálica, ésta se ejecutará con "
            "perfiles especiales escogidos al efecto. Las juntas entre paños, "
            "deben sellarse con cemento asfáltico u otro material elástico "
            "similar."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_12_a_13_revestimiento_cubierta",
        "seccion": "K.4.3.12 a K.4.3.13 (Revestimiento con Vidrios y Vidrios en Cubierta)",
        "titulo": "Dimensiones máximas de piezas de vidrio para revestimiento de muros y requisitos para claraboyas, bóvedas/cúpulas y techos transitables de vidrio.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.12 — REVESTIMIENTO CON VIDRIOS "
            "— La colocación de revestimientos con piezas o placas de vidrio, "
            "requiere que se asegure su perfecta adherencia a los muros y se "
            "evite la presencia de aristas cortantes. Las piezas de vidrio que se "
            "usen para revestir deben tener las siguientes dimensiones máximas: "
            "(a) 0.95 m², si se colocan a altura menor de 2.5 m, medida sobre el "
            "solado. (b) 0.50 m², si se colocan arriba de 2.50 m, el lado máximo "
            "de la pieza será de 1.50 m.\n\n"
            "K.4.3.13 — VIDRIOS EN CUBIERTA — Los vidrios de cubierta deben "
            "cumplir los siguientes requisitos: (a) Claraboyas — Toda claraboya "
            "debe construirse con base en marcos y bastidores de metal o "
            "concreto armado, anclados firmemente. (b) Bóvedas y cúpulas — Toda "
            "bóveda o cúpula debe construirse con base en estructura metálica y "
            "vidrios soportados o estructura de concreto armado y vidrios "
            "perfilados inclinados dentro de los soportes. (c) Techos transitables "
            "— Todo techo o azotea de esta clase debe responder a las "
            "especificaciones tal como lo define el numeral K.4.3.11."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_14_ntc_colombianas",
        "seccion": "K.4.3.14 (Normas Técnicas Colombianas)",
        "titulo": "Listado de las 3 normas técnicas colombianas (NTC) declaradas parte del Reglamento para el Capítulo K.4.3 de vidrios.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.14 — NORMAS TÉCNICAS "
            "COLOMBIANAS — NTC 1909 (2008) — Vidrio. Vidrio Plano Flotado. Vidrio "
            "Plano Impreso (grabado). Vidrio Plano Armado (alambrado). Adopción "
            "Modificada de La ASTM C 1036-06. Standard Specification for Flat "
            "Glass. (Especificaciones para Vidrio Plano). NTC 1804 (1990) — "
            "Vidrio. Vidrio plano estirado. NTC 5579 (2007) — Terminología "
            "normalizada de vidrio y productos de vidrio."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_15_astm_1",
        "seccion": "K.4.3.15 — parte 1 (Normas Técnicas Americanas ASTM: vidrio y recubrimientos)",
        "titulo": "Primer bloque de normas ASTM referenciadas para el Capítulo K.4.3: vidrio tratado térmicamente, laminado, curvado, espejos y ensayos de fuga de aire/agua.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.15 — NORMAS TECNICAS "
            "AMERICANAS (ASTM) — ASTM C1048-04 — Standard Specification for "
            "Heat-Treated Flat Glass—Kind HS, Kind FT Coated and Uncoated Glass. "
            "(Vidrio plano tratado con calor, categoría termoendurecido (HS) y "
            "categoría templado (FT) con y sin recubrimiento). ASTM C1172 (2009) "
            "— Standard Specification for Laminated Architectural Flat Glass. "
            "(Vidrio Laminado Plano para Arquitectura). ASTM C1376-03 — Standard "
            "Specification for Pyrolytic and Vacuum Deposition Coatings on Flat "
            "Glass. (Vidrios recubiertos por Deposición al vació y con "
            "recubrimiento Pirolítico). ASTM C1464-06 — Standard Specification "
            "for Bent Glass. (Vidrio Curvado). ASTM C1503-08 — Standard "
            "Specification for Silvered Flat Glass Mirror. (Espejos). ASTM "
            "E283-04 — Standard Test Method for Determining Rate of Air Leakage "
            "Through Exterior Windows, Curtain Walls, and Doors Under Specified "
            "Pressure Differences Across the Specimen. ASTM E330-02 — Test "
            "Method for Structural Performance of Exterior Windows, Doors, "
            "Skylights and Curtain Walls by Uniform Static Air Pressure "
            "Difference. ASTM E331-00(2009) — Standard Test Method for Water "
            "Penetration of Exterior Windows, Skylights, Doors, and Curtain "
            "Walls by Uniform Static Air Pressure Difference. ASTM E547-00(2009) "
            "— Standard Test Method for Water Penetration of Exterior Windows, "
            "Skylights, Doors, and Curtain Walls by Cyclic Static Air Pressure "
            "Difference."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_15_astm_2",
        "seccion": "K.4.3.15 — parte 2 (Normas Técnicas Americanas ASTM: ensayos de campo, impacto y resistencia)",
        "titulo": "Segundo bloque de normas ASTM referenciadas para el Capítulo K.4.3: ensayos de campo de fuga/penetración, barandas, resistencia a carga, impacto y vidrios especiales.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.15 — NORMAS TECNICAS "
            "AMERICANAS (ASTM), continuación — ASTM E783-02 — Standard Test "
            "Method for Field Measurement of Air Leakage through Installed "
            "Exterior Windows and Doors. ASTM E935-00(2006) — Standard Test "
            "Methods for Performance of Permanent Metal Railing Systems and "
            "Rails for Buildings. ASTM E1105-00(2008) — Standard Test Method for "
            "Field Determination of Water Penetration of Installed Exterior "
            "Windows, Skylights, Doors, and Curtain Walls, by Uniform or Cyclic "
            "Static Air Pressure Difference. ASTM E1300-09a — Standard Practice "
            "for Determining Load Resistance of Glass in Buildings. ASTM "
            "E2025-99(2006) — Standard Test Method for Evaluating Fenestration "
            "Components and Assemblies for Resistance to Impact Energies. ASTM "
            "E2353-06 — Standard Test Methods for Performance of Glass in "
            "Permanent Glass Railing Systems, Guards, and Balustrades. ASTM "
            "F1233-06 — Standard Test Method for Security Glazing Materials And "
            "Systems. ASTM F1915-07a — Standard Test Methods for Glazing for "
            "Detention Facilities. ASTM STP 1434 — The Use of Glass in "
            "Buildings. Páginas 105 a 118. ASTM E2190-08 — Standard "
            "Specification for Insulating Glass Unit Performance and "
            "Evaluation. (Unidades de Vidrio Aislante o Doble Vidriado). ASTM "
            "C1349-04 — Standard Specification for Architectural Flat Glass Clad "
            "Polycarbonate. ASTM C1422-99(2005)e1 — Standard Specification for "
            "Chemically Strengthened Flat Glass."
        ),
    },
    {
        "id": "NSR10-K-K_4_3_16_otras_normas",
        "seccion": "K.4.3.16 (Otras Normas Técnicas)",
        "titulo": "Cierra el Capítulo K.4.3 y el Título K completo: normas AAMA, AAMA/WDMA/CSA, ANSI, neozelandesa y UL referenciadas para vidrios.",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.3.16 — OTRAS NORMAS TECNICAS — "
            "AAMA 501.1-05 — Standard test method for metal curtain walls for "
            "water penetration using dynamic pressure. AAMA 501.6-01 — "
            "Recommended Dynamic test method for determining the seismic drift "
            "causing glass fallout from a wall system. AAMA/WDMA/CSA "
            "101/I.S.2/A440-08 — Standard specification for Windows, Doors, and "
            "unit skylights. ANSI Z97.1-2004e — American National Standard for "
            "Safety Glazing Materials Used in Buildings - Safety Performance "
            "Specifications and Methods of Test. (Se puede usar esta versión o "
            "versiones posteriores a esta que estén vigentes en el momento de su "
            "aplicación). NZC 4223:1999 — New Zealand Standards. Estándar de "
            "Nueva Zelanda: Vidrieras para edificios. Parte 3: 1999. UL 410 — "
            "Slip Resistance of Floor Surface Materials."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    print("\nSub-particionando por tokens REALES (limite 128, medido con el tokenizer)...")
    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            n_tok = len(tokenizer.encode(pieza, add_special_tokens=True))
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })
            print(f"  {chunk['id'] + sufijo:60s} {n_tok:3d} tokens")
    print(f"\n{len(CHUNKS)} piezas originales -> {len(piezas_finales)} piezas reales tras troceo.")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for pieza, vec in zip(piezas_finales, vectores):
        rows.append({
            "id": pieza["id"],
            "capitulo": CAPITULO,
            "seccion": pieza["seccion"],
            "titulo": pieza["titulo"][:500],
            "texto": pieza["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de K.4.3.10-16 cargados. Título K completo (K.1-K.4.3).")


if __name__ == "__main__":
    main()
