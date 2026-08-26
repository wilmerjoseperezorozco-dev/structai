"""
REEMPLAZA el Capítulo III (Categoría, Sistema Estructural y Regularidad
de las Edificaciones) de peru_e030_chunks con el texto vigente de la
E.030 modificada por la RM 183-2026-VIVIENDA -- segundo capítulo de la
reingesta gradual, ver issue #13 e insert histórico en
scripts/ingesta/peru_e030/reemplazo_2026/reemplaza_capitulo2_peligro_sismico.py
(mismo criterio y estrategia de reemplazo, no repetir aquí el contexto
completo).

ESTRATEGIA DE REEMPLAZO: se ELIMINAN los 58 chunks viejos con prefijo
"E030-CAP3-*" (numeración 2019: Artículos 15-23, Tablas 5-10) y se
insertan los nuevos con prefijo "E030-2026-CAP3-*" (numeración 2026:
Artículos 19-27, Tablas 7-13).

CAMBIOS REALES CONFIRMADOS (comparado explícitamente contra los chunks
viejos antes de escribir este script, no asumidos por la sola lectura
de los "considerandos" de la resolución):
- Coeficiente R0 de "Muros de ductilidad limitada": bajó de 4,0 (2019)
  a 3,5 (2026) -- todos los demás valores de la Tabla R0 (SMF=8, IMF=5,
  OMF=4, SCBF=7, OCBF=4, EBF=8, Pórticos=8, Dual=7, muros
  estructurales=6, albañilería=3, madera=7) están CONFIRMADOS SIN
  CAMBIO.
- Edificaciones de Muros de Ductilidad Limitada (EMDL): el máximo de
  pisos permitido bajó de 8 (2019) a 5 (2026); la edición 2026 además
  explicita una densidad mínima de muros (>2,5% por piso) y un espesor
  mínimo (10 cm) que la descripción de 2019 no traía en el mismo nivel
  de detalle.
- Restricción de construcciones de tierra: la edición 2019 prohibía en
  S4; la edición 2026 prohíbe en S4 Y S5 (consistente con que S5 es una
  categoría nueva, no existía en 2019).
- Categorías A1/A2/B/C (Tabla 7, antes Tabla 5) y coeficiente U: sin
  cambio de valores (1,5/1,3/1,0), pero la nota de aislamiento sísmico
  obligatorio para A1 en zonas 3-4 tiene redacción más detallada.
- Artículo 27 (aislamiento/disipación): referencia actualizada a
  ASCE/SEI 7-22 (antes probablemente una edición anterior del ASCE 7,
  no confirmado el número exacto en el chunk viejo -- no se afirma el
  cambio de edición del ASCE por no tener el dato viejo a la vista).

Uso: python scripts/ingesta/peru_e030/reemplazo_2026/reemplaza_capitulo3_categoria_sistema_regularidad.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 (ed. 2026, RM 183-2026-VIVIENDA) — Capítulo III: Categoría, Sistema Estructural y Regularidad"

IDS_VIEJOS_A_ELIMINAR_PREFIJO = "E030-CAP3-"

CHUNKS = [
    {
        "id": "E030-2026-CAP3-ART19-TABLA7-CATEGORIA_FACTOR_U",
        "seccion": "Artículo 19, Tabla N°7 (ed. 2026)",
        "titulo": "Categorías de edificación A1/A2 (esenciales, U=1,5), B (importantes, U=1,3), C (comunes, U=1,0); A1 en zonas 3-4 requiere aislamiento sísmico obligatorio (U=1)",
        "texto": (
            "E.030 (edición 2026, RM 183-2026-VIVIENDA), Artículo 19 — "
            "Categoría de las edificaciones y factor de uso (U). Cada "
            "estructura se clasifica según la Tabla N°7, que asigna el "
            "factor U según la categoría.\n\n"
            "Tabla N°7 — Categoría de las edificaciones y factor U "
            "(verbatim, ed. 2026):\n"
            "  Categoría A 'Edificaciones esenciales' (U=1,5): A1 — "
            "establecimientos de salud público/privado de 2° y 3° "
            "nivel; A2 — edificaciones esenciales para manejo de "
            "emergencias/gobierno/refugio post-desastre (otros "
            "establecimientos de salud, puertos/aeropuertos/estaciones "
            "ferroviarias, bomberos/fuerzas armadas/policía, "
            "generación/tratamiento de agua, instituciones educativas y "
            "universidades, edificaciones cuyo colapso sea riesgo "
            "adicional como hornos/fábricas de inflamables, archivos "
            "esenciales del Estado).\n"
            "  Categoría B 'Edificaciones importantes' (U=1,3): cines, "
            "teatros, estadios, coliseos, centros comerciales, "
            "terminales de buses, penitenciarías, museos, bibliotecas, "
            "depósitos de granos importantes.\n"
            "  Categoría C 'Edificaciones comunes' (U=1,0): viviendas, "
            "oficinas, hoteles, restaurantes, depósitos e industrias "
            "cuya falla no genera peligros adicionales.\n\n"
            "Nota importante: las edificaciones NUEVAS de categoría A1 "
            "en zonas sísmicas 4 y 3 deben tener aislamiento sísmico en "
            "la base obligatoriamente (U=1 en ese caso). Para salud de "
            "primer nivel, la entidad responsable decide. En zonas 1 y "
            "2, es opcional — si no se usa aislamiento en zonas 1-2, U "
            "es como mínimo 1,5."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART20-TABLA8-SISTEMAS_CONCRETO",
        "seccion": "Artículo 20, Tabla N°8 (ed. 2026)",
        "titulo": "Sistemas de concreto armado: pórticos (≥80% cortante en columnas), muros estructurales (≥70% en muros), dual (20-70% en muros), EMDL -- ⚠️ máximo bajó de 8 a 5 pisos",
        "texto": (
            "Artículo 20 — Sistemas estructurales, según material "
            "(Tabla N°8):\n\n"
            "Concreto armado (según Norma E.060 Concreto Armado del "
            "RNE):\n"
            "  Pórticos: ≥80% de la fuerza cortante en la base actúa "
            "sobre las columnas; muros estructurales existentes se "
            "diseñan según su rigidez relativa.\n"
            "  Muros estructurales: resistencia dada predominantemente "
            "por muros dúctiles con ≥70% de la fuerza cortante en la "
            "base.\n"
            "  Dual: combinación de pórticos y muros, con los muros "
            "tomando entre 20% y 70% del cortante en la base.\n"
            "  Edificaciones de Muros de Ductilidad Limitada (EMDL): "
            "alta densidad de muros de concreto armado (mayor a 2,5% "
            "por piso), espesores reducidos (mínimo 10 cm), sin "
            "extremos confinados, refuerzo vertical en una sola capa. "
            "⚠️ Con este sistema se puede construir como MÁXIMO 5 PISOS "
            "(la edición 2019 permitía hasta 8 pisos — cambio real "
            "confirmado, más conservador)."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART20-TABLA8-SISTEMAS_ACERO",
        "seccion": "Artículo 20, Tabla N°8 (ed. 2026)",
        "titulo": "Sistemas de acero: SMF/IMF/OMF (pórticos a momento), SCBF/OCBF (arriostrados concéntricos), EBF (arriostrados excéntricos) -- según Norma E.090",
        "texto": (
            "Sistemas estructurales de acero (Tabla N°8, según Norma "
            "E.090 Estructuras Metálicas del RNE):\n"
            "  Pórticos especiales resistentes a momentos (SMF): alta "
            "capacidad de deformación inelástica por fluencia en "
            "flexión de vigas; columnas más resistentes que las vigas.\n"
            "  Pórticos intermedios resistentes a momentos (IMF): "
            "capacidad limitada de deformación inelástica.\n"
            "  Pórticos ordinarios resistentes a momentos (OMF): "
            "capacidad mínima de deformación inelástica.\n"
            "  Pórticos especiales concéntricamente arriostrados "
            "(SCBF): alta capacidad por resistencia post-pandeo en "
            "arriostres a compresión y fluencia en tracción.\n"
            "  Pórticos ordinarios concéntricamente arriostrados "
            "(OCBF): capacidad limitada.\n"
            "  Pórticos excéntricamente arriostrados (EBF): alta "
            "capacidad, principalmente por fluencia en flexión o corte "
            "en la zona entre arriostres."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART20-TABLA8-ALBANILERIA_MADERA_TIERRA",
        "seccion": "Artículo 20, Tabla N°8 (ed. 2026)",
        "titulo": "Albañilería (E.070, sin diferenciar confinada/armada), madera (E.010), tierra (E.080) -- prohibida en suelos S4 y S5 (S5 categoría nueva)",
        "texto": (
            "Sistemas estructurales de albañilería, madera y tierra "
            "(Tabla N°8): albañilería — muros de unidades de arcilla o "
            "concreto, según Norma E.070 (para esta norma, sin "
            "diferenciar albañilería confinada de armada). Madera — "
            "elementos sismorresistentes principalmente de madera, "
            "según Norma E.010. Tierra — muros de unidades de "
            "albañilería de tierra o tierra apisonada in situ, según "
            "Norma E.080. No se permiten construcciones de tierra en "
            "suelos S4 y S5 (artículo 22.4 — la prohibición en S5 es "
            "consistente con que esa categoría de suelo es nueva en la "
            "edición 2026)."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART21-TABLA9-CATEGORIA_SISTEMA_ZONA",
        "seccion": "Artículo 21, Tabla N°9 (ed. 2026)",
        "titulo": "Sistema estructural permitido según categoría y zona: A1 exige aislamiento en zonas 3-4; A2/B restringidas a sistemas dúctiles en zonas altas; C sin restricción",
        "texto": (
            "Artículo 21 — Categoría de las edificaciones y sistemas "
            "estructurales. Según categoría y zona, se proyecta con el "
            "sistema estructural de la Tabla N°9, respetando además las "
            "restricciones de irregularidad de la Tabla N°13.\n\n"
            "Tabla N°9 — Categoría y sistema estructural (verbatim, ed. "
            "2026):\n"
            "  A1: zonas 4 y 3 → aislamiento sísmico con cualquier "
            "sistema; zonas 2 y 1 → acero SCBF/EBF, concreto dual/muros "
            "estructurales, albañilería armada o confinada.\n"
            "  A2: zonas 4, 3 y 2 → acero SCBF/EBF, concreto dual/muros "
            "estructurales, albañilería armada o confinada; zona 1 → "
            "cualquier sistema. (Nota: pequeñas construcciones rurales "
            "como escuelas y postas médicas pueden usar materiales "
            "tradicionales.)\n"
            "  B: zonas 4, 3 y 2 → acero SMF/IMF/SCBF/OCBF/EBF, "
            "concreto pórticos/dual/muros estructurales, albañilería "
            "armada o confinada, madera; zona 1 → cualquier sistema.\n"
            "  C: zonas 4, 3, 2 y 1 → cualquier sistema.\n\n"
            "Para edificaciones con cobertura liviana se permite "
            "cualquier sistema estructural (artículo 21.2)."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART22-TABLA10-COEFICIENTE_R0",
        "seccion": "Artículo 22, Tabla N°10 (ed. 2026)",
        "titulo": "Coeficiente básico de reducción R0 por sistema estructural; ⚠️ muros de ductilidad limitada bajó de R0=4,0 a R0=3,5 -- todos los demás valores SIN cambio",
        "texto": (
            "Artículo 22 — Sistemas estructurales y coeficiente básico "
            "de reducción de las fuerzas sísmicas (R0). Se clasifican "
            "según material y sistema de estructuración en cada "
            "dirección de análisis.\n\n"
            "Tabla N°10 — Sistemas estructurales y R0 (verbatim, ed. "
            "2026; comparado explícitamente contra la edición 2019, "
            "confirmado que SOLO el valor de ductilidad limitada "
            "cambió):\n"
            "  Acero: SMF=8, IMF=5, OMF=4, SCBF=7, OCBF=4, EBF=8 (sin "
            "cambio respecto a 2019).\n"
            "  Concreto armado: Pórticos=8, Dual=7, De muros "
            "estructurales=6 (sin cambio); Muros de ductilidad "
            "limitada=3,5 (⚠️ CAMBIÓ — edición 2019 tenía R0=4,0, la "
            "reducción es real y del lado conservador: menor R0 implica "
            "mayor fuerza de diseño).\n"
            "  Albañilería armada o confinada=3, Madera=7 (para diseño "
            "por esfuerzos admisibles) — ambos sin cambio.\n\n"
            "Estos coeficientes aplican solo a estructuras donde los "
            "elementos verticales y horizontales permiten disipar "
            "energía manteniendo la estabilidad. Si en una dirección "
            "hay más de un sistema, se toma el menor R0 (22.2). Para "
            "estructuras tipo péndulo invertido: R0=2,5 (22.3)."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART23_24-TABLA11-IRREGULARIDAD_ALTURA",
        "seccion": "Artículos 23-24, Tabla N°11 (ed. 2026)",
        "titulo": "Regularidad estructural (Ia/Ip=1,0 si no hay irregularidad); Tabla N°11 en altura: piso blando/débil (0,75), extrema (0,50), masa (0,90), geométrica (0,90), discontinuidad (0,80/0,60)",
        "texto": (
            "Artículo 23 — Regularidad estructural. Las estructuras se "
            "clasifican regulares o irregulares para: cumplir "
            "restricciones (Tabla N°13), definir procedimientos de "
            "análisis, y determinar el coeficiente R. Sin ninguna "
            "irregularidad de las Tablas N°11/N°12, se consideran "
            "regulares con Ia=Ip=1,0.\n\n"
            "Artículo 24 — Factores de irregularidad (Ia, Ip): Ia = "
            "menor valor de la Tabla N°11 (irregularidades en altura) "
            "en las 2 direcciones; Ip = menor valor de la Tabla N°12 "
            "(en planta). Si las 2 direcciones dan valores distintos, se "
            "toma el menor.\n\n"
            "Tabla N°11 — Irregularidades en altura (verbatim, ed. "
            "2026):\n"
            "  Piso blando (rigidez <70% del entrepiso superior o <80% "
            "del promedio de 3 niveles superiores) o piso débil "
            "(resistencia <80% del entrepiso superior): Ia=0,75.\n"
            "  Irregularidad extrema de rigidez (<60%/<70%) o "
            "resistencia (<65%) — remite a Tabla N°13: Ia=0,50.\n"
            "  Irregularidad de masa (peso de un piso >1,5x un piso "
            "adyacente, no aplica en azoteas/sótanos): Ia=0,90.\n"
            "  Irregularidad geométrica vertical (dimensión en planta "
            ">1,3x un piso adyacente): Ia=0,90.\n"
            "  Discontinuidad en sistemas resistentes (desalineamiento "
            "vertical >25% en elemento que resiste >10% del cortante): "
            "Ia=0,80.\n"
            "  Discontinuidad extrema (elementos discontinuos >25% del "
            "cortante total) — remite a Tabla N°13: Ia=0,60."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART24-TABLA12-IRREGULARIDAD_PLANTA",
        "seccion": "Artículo 24, Tabla N°12 (ed. 2026)",
        "titulo": "Tabla N°12 irregularidades en planta: torsional (0,75)/extrema (0,60), esquinas entrantes (0,90), discontinuidad de diafragma (0,85), sistemas no paralelos (0,90)",
        "texto": (
            "Tabla N°12 — Irregularidades en planta (verbatim, ed. "
            "2026):\n"
            "  Irregularidad torsional (desplazamiento relativo máximo "
            "Δmax >1,3x el promedio Δprom, con diafragmas rígidos y "
            "solo si Δmax >50% del desplazamiento permisible de la "
            "Tabla N°14): Ip=0,75.\n"
            "  Irregularidad torsional extrema (Δmax >1,5x Δprom, "
            "mismas condiciones) — remite a Tabla N°13: Ip=0,60.\n"
            "  Esquinas entrantes (dimensiones en ambas direcciones "
            ">20% de la dimensión total en planta): Ip=0,90.\n"
            "  Discontinuidad del diafragma (aberturas >50% del área "
            "bruta, o área neta resistente <50% del área de la sección "
            "transversal): Ip=0,85.\n"
            "  Sistemas no paralelos (elementos resistentes no "
            "paralelos, no aplica si el ángulo es <30° o si resisten "
            "<10% del cortante del piso): Ip=0,90."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART25-TABLA13-RESTRICCIONES_IRREGULARIDAD",
        "seccion": "Artículo 25, Tabla N°13 (ed. 2026)",
        "titulo": "Restricciones de irregularidad por categoría/zona: A1/A2 sin irregularidades en zonas altas; C sin restricción en zona 1; sistemas de transferencia limitados a 25% de carga en zonas 2-4",
        "texto": (
            "Artículo 25 — Restricciones a la irregularidad.\n\n"
            "Tabla N°13 — Categoría y regularidad de las edificaciones "
            "(verbatim, ed. 2026): A1 y A2 → zonas 4,3,2: no se "
            "permiten irregularidades; zona 1: no se permiten "
            "irregularidades extremas. B → zonas 4,3,2: no se permiten "
            "irregularidades extremas; zona 1: sin restricciones. C → "
            "zonas 4 y 3: no se permiten irregularidades extremas; zona "
            "2: no se permiten irregularidades extremas excepto en "
            "edificios de hasta 2 pisos u 8 m de altura total; zona 1: "
            "sin restricciones.\n\n"
            "25.2. En zonas sísmicas 4, 3 y 2 no se permiten sistemas de "
            "transferencia donde más del 25% de las cargas de gravedad "
            "o sísmicas en cualquier nivel sean soportadas por "
            "elementos verticales no continuos hasta la cimentación "
            "(no aplica al último entrepiso)."
        ),
    },
    {
        "id": "E030-2026-CAP3-ART26_27-COEFICIENTE_R_AISLAMIENTO",
        "seccion": "Artículos 26-27 (ed. 2026)",
        "titulo": "R = R0 · Ia · Ip; aislamiento sísmico rige por la Norma E.031; disipación de energía debe cumplir además el Capítulo 18 de ASCE/SEI 7-22 (o equivalente), con supervisión técnica especializada",
        "texto": (
            "Artículo 26 — Coeficiente de reducción de las fuerzas "
            "sísmicas, R. Se determina como el producto: "
            "R = R0 · Ia · Ip (R0 de la Tabla N°10, Ia/Ip de las Tablas "
            "N°11/N°12).\n\n"
            "Artículo 27 — Sistemas de aislamiento sísmico y "
            "disipación de energía. Las edificaciones con aislamiento "
            "sísmico se rigen por la Norma Técnica E.031 Aislamiento "
            "Sísmico del RNE. Se permite disipación de energía si se "
            "cumplen las disposiciones del Capítulo II de esta norma y, "
            "en lo que corresponda, los requisitos técnicos del "
            "'Chapter 18 Seismic design requirements for structures "
            "with damping systems' del documento ASCE/SEI 7-22 "
            "(Minimum Design Loads and Associated Criteria for "
            "Buildings and Other Structures, American Society of Civil "
            "Engineers), u otra norma de nivel de seguridad equivalente "
            "o superior. La instalación de aislamiento sísmico o "
            "disipación de energía requiere supervisión técnica "
            "especializada a cargo de un ingeniero civil."
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


def reemplazar(dry_run: bool = False):
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
    print(f"\nChunks VIEJOS a eliminar (prefijo '{IDS_VIEJOS_A_ELIMINAR_PREFIJO}'): se listarán antes de borrar.")

    if dry_run:
        print("[dry-run] No se elimina ni se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)

    viejos = sb.table("peru_e030_chunks").select("id").like("id", f"{IDS_VIEJOS_A_ELIMINAR_PREFIJO}%").execute()
    ids_viejos = [r["id"] for r in viejos.data]
    print(f"Eliminando {len(ids_viejos)} chunks viejos (edición 2019): {ids_viejos}")
    if ids_viejos:
        sb.table("peru_e030_chunks").delete().in_("id", ids_viejos).execute()

    sb.table("peru_e030_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(ids_viejos)} chunks viejos eliminados, {len(rows)} chunks nuevos (ed. 2026) insertados.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    reemplazar(dry_run=dry)
