"""
Inserta el núcleo verbatim real de la Tabla 6 (Categoría de edificio y
coeficiente de importancia I, sección 4.1) y las Tablas 15 y 16
(Coeficiente R para sistemas dúctiles y de ductilidad limitada, sección
6.3.4) de la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks.

Motivado por completar dos celdas que el documento comparativo
Colombia/Perú/Ecuador (2026-08-25) dejó explícitamente como "pendiente"
en vez de inventar un valor plausible. Texto extraído del mismo PDF
digital oficial del MIDUVI/MIT ya usado para la Sección 1.

Nota de alcance: el R0 de Colombia (NSR-10, Tablas A.3-1 a A.3-4) se
buscó en nsr10_chunks y NO está en el corpus todavía -- confirmado con
varias búsquedas (por sección, por patrón "R0=", en todo el Título A),
no es un problema de búsqueda. Queda pendiente para una sesión con el PDF
oficial de NSR-10 a mano; no se inventa aquí.

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_tabla6_categoria_uso_y_tablas15_16_coeficiente_r.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 4/6 — Categoría de Edificio y Coeficiente R"

CHUNKS = [
    {
        "id": "NECSEDS-S4_1-TABLA6-CATEGORIA_IMPORTANCIA",
        "seccion": "4.1",
        "titulo": "Categoría de Edificio y Coeficiente de Importancia I (Tabla 6: esenciales, ocupación especial, otras — I=1,5/1,3/1,0)",
        "texto": """4.1. Categoría de edificio y coeficiente de importancia I

NOTA: al determinar las fuerzas a partir de las curvas de peligro sísmico, dichas fuerzas no requieren ser modificadas por el factor de importancia I.

La estructura a construirse se clasificará en una de las categorías que se establecen en la Tabla 6 y se adoptará el correspondiente factor de importancia I. El propósito del factor I es incrementar la demanda sísmica de diseño para estructuras, que por sus características de utilización o de importancia deben permanecer operativas o sufrir menores daños durante y después de la ocurrencia del sismo de diseño.

Tabla 6 — Tipo de uso, destino e importancia de la estructura:

Categoría "Edificaciones esenciales" (I=1,5): hospitales, clínicas, centros de salud o de emergencia sanitaria; instalaciones militares, de policía, bomberos, defensa civil; garajes o estacionamientos para vehículos y aviones que atienden emergencias; torres de control aéreo; estructuras de centros de telecomunicaciones u otros centros de atención de emergencias; estructuras que albergan equipos de generación y distribución eléctrica; tanques u otras estructuras utilizadas para depósito de agua u otras sustancias anti-incendio; estructuras que albergan depósitos tóxicos, explosivos, químicos u otras sustancias peligrosas.

Categoría "Estructuras de ocupación especial" (I=1,3): museos, iglesias, escuelas y centros de educación o deportivos que albergan más de trescientas personas; todas las estructuras que albergan más de cinco mil personas; edificios públicos que requieren operar continuamente.

Categoría "Otras estructuras" (I=1,0): todas las estructuras de edificación y otras que no clasifican dentro de las categorías anteriores.

El diseño de las estructuras con factor de importancia 1,0 cumplirá con todos los requisitos establecidos en el presente capítulo de la norma.""",
    },
    {
        "id": "NECSEDS-S6_3_4-CRITERIOS_R",
        "seccion": "6.3.4 (criterios)",
        "titulo": "Ductilidad y Factor de Reducción R — criterios de definición y grupos estructurales",
        "texto": """Los factores de reducción de resistencia R dependen de: tipo de estructura, tipo de suelo, período de vibración considerado, y factores de ductilidad, sobre resistencia, redundancia y amortiguamiento de una estructura en condiciones límite.

Se seleccionará uno de los dos grupos estructurales siguientes: sistemas estructurales dúctiles (Tabla 15) o sistemas estructurales de ductilidad limitada (Tabla 16). Debe tomarse el menor de los valores de R para los casos en los cuales el sistema resistente estructural resulte en una combinación de varios sistemas.

Nota 1: a pesar de ser constante en el DBF (Diseño Basado en Fuerzas), el factor R permite disminuir sustancialmente la ordenada elástica espectral, siempre que se disponga de un adecuado comportamiento inelástico durante el sismo de diseño.

Nota 2: los valores del factor R consideran la definición de las cargas sísmicas a nivel de resistencia, no a nivel de servicio (a diferencia de la versión previa de esta norma).

No deben utilizarse sistemas estructurales de ductilidad limitada para: un número de pisos que rebasen los límites establecidos en las Tablas 15 y 16, o si el factor de importancia I es mayor que 1.""",
    },
    {
        "id": "NECSEDS-TABLA15-R_SISTEMAS_DUCTILES",
        "seccion": "Tabla 15",
        "titulo": "Coeficiente R para Sistemas Estructurales Dúctiles (Sistemas Duales R=8, Pórticos Resistentes a Momentos R=8, Otros R=5)",
        "texto": """Tabla 15 — Coeficiente R para sistemas estructurales dúctiles:

Sistemas Duales: pórticos especiales sismo resistentes de hormigón armado con vigas descolgadas y con muros estructurales de hormigón armado o con diagonales rigidizadoras → R=8. Pórticos especiales sismo resistentes de acero laminado en caliente, con diagonales rigidizadoras (excéntricas o concéntricas) o con muros estructurales de hormigón armado → R=8. Pórticos con columnas de hormigón armado y vigas de acero laminado en caliente con diagonales rigidizadoras → R=8. Pórticos especiales sismo resistentes de hormigón armado con vigas banda, con muros estructurales de hormigón armado o con diagonales rigidizadoras → R=7.

Pórticos resistentes a momentos: pórticos especiales sismo resistentes de hormigón armado con vigas descolgadas → R=8. Pórticos especiales sismo resistentes de acero laminado en caliente o con elementos armados de placas → R=8. Pórticos con columnas de hormigón armado y vigas de acero laminado en caliente → R=8.

Otros sistemas estructurales para edificaciones: sistemas de muros estructurales dúctiles de hormigón armado → R=5. Pórticos especiales sismo resistentes de hormigón armado con vigas banda → R=5.""",
    },
    {
        "id": "NECSEDS-TABLA16-R_DUCTILIDAD_LIMITADA",
        "seccion": "Tabla 16",
        "titulo": "Coeficiente R para Sistemas Estructurales de Ductilidad Limitada (viviendas ≤2 pisos: R=1 a 3)",
        "texto": """Tabla 16 — Coeficiente R para sistemas estructurales de ductilidad limitada:

Pórticos resistentes a momento: hormigón armado con secciones de dimensión menor a la especificada en la NEC-SE-HM, limitados a viviendas de hasta 2 pisos con luces de hasta 5 metros → R=3. Hormigón armado con secciones de dimensión menor con armadura electrosoldada de alta resistencia → R=2,5. Estructuras de acero conformado en frío, aluminio, madera, limitados a 2 pisos → R=2,5.

Muros estructurales portantes: mampostería no reforzada, limitada a un piso → R=1. Mampostería reforzada, limitada a 2 pisos → R=3. Mampostería confinada, limitada a 2 pisos → R=3. Muros de hormigón armado, limitados a 4 pisos → R=3.

El valor de R de la Tabla 16 podrá utilizarse para viviendas y edificios de baja altura diseñados con sistemas estructurales de ductilidad limitada, siempre y cuando la estructura sea diseñada de conformidad con los requerimientos de la NEC-SE-VIVIENDA.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/,
# peru_e030/ y ecuador_nec_se_ds/: el tokenizer real (no una aproximación
# por caracteres) es lo único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite se divide por oracion, y si aun asi excede, por
    coma."""
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
