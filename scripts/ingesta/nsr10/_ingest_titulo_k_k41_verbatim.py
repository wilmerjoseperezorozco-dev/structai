"""
NSR-10 Titulo K, Capitulo K.4.1 completo -- Alcance y las ~40 definiciones
del Capitulo K.4 (Requisitos especiales para vidrios), en verbatim real.

Continuacion del cierre de Titulo K (K.1-K.3 ya completos, commit
53ba201). K.4 (vidrios) es grande -- K.4.1 (3 paginas), K.4.2 (13
paginas, requisitos de diseno con tablas densas de espesor/area por tipo
de vidrio), K.4.3 (16+ paginas, seguridad -- sigue mas alla del PDF ya
descargado, no cerrable hoy). Se cierra K.4.1 completo como pedazo
autocontenido; K.4.2/K.4.3 quedan para una sesion futura.

Reemplaza el chunk viejo NSR10-K-K_4_1_alcance_definiciones (2132 chars,
condensado -- el glosario real tiene ~40 terminos definidos, mucho mas
extenso) por 2 chunks verbatim (alcance+glosario A-M, glosario N-V).

Fuente: NSR-10-1571-1625.pdf (Drive id 1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z),
paginas internas K-33 a K-35 (paginas PDF 25-27), leido visualmente
pagina por pagina. Sin formulas matematicas -- solo definiciones tecnicas.

Uso: python _ingest_titulo_k_k41_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título K — Otros Requisitos Complementarios"

CHUNKS = [
    {
        "id": "NSR10-K-K_4_1_alcance_glosario_a_m",
        "seccion": "K.4.1 (Alcance y Definiciones, A-M)",
        "titulo": "Alcance del Capítulo K.4 y definiciones de A (Abertura de perfil) a M (Muro Cortina/Pisavidrio).",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — REQUISITOS ESPECIALES PARA VIDRIOS, "
            "PRODUCTOS DE VIDRIO Y SISTEMAS VIDRIADOS. K.4.1 — GENERAL. K.4.1.1 — "
            "ALCANCE — Las estipulaciones de este Capítulo se refieren a requisitos "
            "generales de diseño, seguridad y constructivos, que deben aplicarse a: "
            "(a) Vidrios, vidrieras, ventanales y productos de vidrio para uso en "
            "edificaciones. (b) Láminas de vidrio verticales e inclinadas para uso en "
            "sistemas vidriados en fachadas. (c) Láminas de vidrio para pisos y "
            "elementos estructurales de vidrio. (d) Elementos complementarios en "
            "sistemas de vidriado.\n\n"
            "K.4.1.2 — DEFINICIONES — Para la correcta interpretación del Reglamento "
            "contenido en este Capítulo, se adoptan las definiciones siguientes:\n\n"
            "Abertura de perfil o galce (Rabbet) — Una sección \"L\" que puede estar "
            "revestida con vidrio o puede recibir un sello perimetral o pisavidrio "
            "removible para retener la lámina de vidrio en su lugar.\n"
            "Choque térmico (Thermal shock) — Cambio abrupto de temperatura impuesto "
            "sobre un elemento de vidrio.\n"
            "Cuñas o calzos de apoyo (Setting blocks) — Extrusiones de neopreno, "
            "EPDM (caucho sintético etileno propileno dieno tipo M ASTM), silicona, "
            "caucho u otro material aceptable como equivalente a los anteriores, "
            "generalmente rectangulares, sobre las cuales se coloca el borde inferior "
            "del producto de vidrio para soportar efectivamente el peso.\n"
            "Cinta celular (Cellular strip) — Cintas hechas de caucho sintético "
            "autoadhesivo.\n"
            "Compuesto bicomponente elástico (Two-part rubberizing compound) — "
            "Compuesto flexible para vidriado, aplicado a mano o con pistola, que "
            "cuando se mezcla cura para formar un material elástico.\n"
            "Doble vidriado (Double glazing) — Vidriado aislante que incorpora dos "
            "láminas de vidrio separadas por una cámara de aire.\n"
            "Grado de Desempeño – GD (Performance Grade – PG) — Indicador numérico "
            "que define el comportamiento del producto de vidriado para tragaluces o "
            "claraboyas, designado de acuerdo con los resultados de la realización "
            "exitosa de los ensayos aplicables citados en el Capítulo 5 de la norma "
            "AAMA/WDMA/CSA 101/I.S.2/A440-08.\n"
            "Sello perimetral o Junquillo (Bead) — Sellante aplicado en una junta sin "
            "importar el método de aplicación.\n"
            "Lámina (Lite) — Término arquitectónico para lámina u hoja de vidrio. "
            "Lámina u hoja que compone un vidrio laminado.\n"
            "Material de vidriado (Glazing material) — Elementos de vidrio, "
            "incluyendo vidrio recocido, vidrio templado, vidrio laminado, vidrio "
            "armado, o combinaciones donde estos son usados.\n"
            "Materiales para vidriado de seguridad (Safety glazing materials) — "
            "Estos son productos orgánicos o inorgánicos, construidos o tratados de "
            "tal manera que reduzcan la posibilidad de lesión a las personas como "
            "resultado de contacto con ellos, sea o no que se rompan. El vidrio "
            "monolítico recocido de cualquier espesor no es considerado como "
            "material para vidriado de seguridad. Los materiales para vidriado de "
            "seguridad deben cumplir los requisitos de la especificación ANSI "
            "Z97.1-2004e. Ver Vidrio de Seguridad.\n"
            "Material plástico de vidriado (Plastic glazing material) — Una hoja "
            "sencilla de material plástico sintético, una combinación de dos o más "
            "de tales hojas laminadas entre sí, o una combinación de material "
            "plástico y material de refuerzo en forma de fibras o escamas. Este "
            "material contiene como ingrediente esencial una sustancia orgánica de "
            "gran peso molecular, que es sólido en su estado terminado y al cual, en "
            "alguna etapa de su fabricación o procesamiento para llegar a ser un "
            "artículo acabado, se le puede dar forma por flujo.\n"
            "Muro Cortina o Fachada Flotante (Curtain Wall) — Es el sistema que "
            "proporciona aislamientos relacionados con la luz, calor, ruido y "
            "viento, agregando carga a la estructura sin hacer parte del sistema de "
            "resistencia sísmica de la edificación."
        ),
    },
    {
        "id": "NSR10-K-K_4_1_glosario_n_v",
        "seccion": "K.4.1 (Definiciones, N-V)",
        "titulo": "Definiciones de N (Pisavidrio) a V (Vidrio Tratado Térmicamente): tipos de vidrio (templado, laminado, armado, flotado, recocido, spandrel, etc.).",
        "texto": (
            "NSR-10 Título K, Capítulo K.4 — K.4.1.2 — DEFINICIONES (continuación):\n\n"
            "Pisavidrio (Bead) — Pieza de pequeña sección que sirve para la fijación "
            "de los vidrios y paneles al marco.\n"
            "Sistema de Baranda (Guard System) — Un sistema de protección a lo largo "
            "de los bordes de lugares accesibles como de terrazas, balcones, techos, "
            "plataformas, rampas, escaleras o descansos, que es diseñado para "
            "minimizar la probabilidad de una caída accidental desde la superficie "
            "de tránsito peatonal.\n"
            "Tragaluz, Vidrio Inclinado o Claraboya (Skylight) — Vidrio plano que se "
            "instala en un ángulo mayor a 15° de la vertical en el exterior de un "
            "edificio.\n"
            "Unidad de doble vidriado (Double glazing unit) — Dos láminas de vidrio "
            "separadas por una cavidad sellada permanentemente y que cumple los "
            "requisitos de la especificación ASTM E2190-08.\n"
            "Ventana de observación (Sight glass) — Ventana de vidrio para un "
            "puerto de visualización, por lo general para un sistema presurizado "
            "por ejemplo en piscinas.\n"
            "Ventanal o ventanaje (Fenestration) — Panel de vidrio, unidad de "
            "ventana, tragaluz, puerta o muro cortina o fachada flotante en el "
            "exterior de una edificación.\n"
            "Vidrio Endurecido químicamente (Chemically strengthened) — Vidrio al "
            "que se ha realizado intercambio de iones para producir una capa "
            "sometida a esfuerzos de compresión en la superficie tratada.\n"
            "Vidriado (Glazing) — 1) Término genérico usado para describir un "
            "material que cubre un vano como vidrio, láminas, etc. 2) El proceso de "
            "instalar un material que cubre un vano en una abertura preparada para "
            "ventanas, puertas, paneles, particiones, etc.\n"
            "Vidriado seco (Dry glazing) — Es la designación común para sistemas que "
            "utilizan empaques de caucho extruídos como uno o los dos sellos del "
            "vidriado. El desempeño no es afectado de la misma manera que los "
            "sistemas de vidriado húmedo, por factores como la instalación, "
            "intemperie, mano de obra y compatibilidad. También se conocen como "
            "sistemas vidriados de compresión del empaque.\n"
            "Vidrio (Glass) — Producto inorgánico de fusión, constituido "
            "principalmente por compuestos de silicio, calcio y sodio, que se han "
            "enfriado hasta adquirir un estado rígido sin cristalización.\n"
            "Vidrio Armado (Wired glass) — Vidrio plano con una capa de malla de "
            "alambre totalmente incluida en el vidrio y que cumple los requisitos de "
            "la especificación NTC 1909 (2009).\n"
            "Vidrio con recubrimiento orgánico (Organic-coated glass) — Ensamble que "
            "consiste de una lámina de vidrio con una o ambas superficies cubiertas "
            "con 1) Una película o lámina orgánica adhesiva o; 2) Un recubrimiento "
            "aplicado. Cuando un vidrio con recubrimiento orgánico se quiebra "
            "numerosas grietas aparecen, pero los fragmentos de vidrio tienden a "
            "adherirse al material orgánico aplicado. Vidrio que cumple los "
            "requisitos de la especificación ASTM C1048-04.\n"
            "Vidrio curvado (Bent Glass) — Vidrio Plano al cual se le ha dado forma "
            "curva a través de un elemento curvo cuando ha estado caliente y que "
            "cumple con los requisitos de la especificación ASTM C1464-06.\n"
            "Vidrio Decorativo (Decorative glass) — Vidrio tallado, cubierto con "
            "plomo o Vidrio Dalle, o material para vidriado cuyo propósito es "
            "decorativo o artístico, y no funcional. En este vidrio el color, "
            "textura u otras cualidades o componentes del diseño no pueden ser "
            "removidos sin destruir el material para vidriado, y su superficie, o el "
            "ensamble dentro del que se incorporará, se divide en segmentos.\n"
            "Vidrio de Seguridad (Safety glass) — Vidrio plano (incluso curvado) de "
            "tal forma fabricado, tratado, procesado o combinado con otros "
            "materiales que al romperse por contacto humano, la probabilidad y/o "
            "gravedad del corte y las heridas por esquirlas producidas por tal "
            "contacto es reducida. Ver Materiales para Vidriado de Seguridad. Vidrio "
            "que cumple los requisitos de la especificación ANSI Z97.1-2004e.\n"
            "Vidrio Estirado (Drawn Glass) — Vidrio plano elaborado mediante "
            "estirado contínuo y que cumple los requisitos de la especificación "
            "NTC1804 (1990).\n"
            "Vidrio fabricado con rodillos de laminación (Rolled glass) — Vidrio "
            "plano formado mediante un proceso con rodillos.\n"
            "Vidrio Flotado (Float glass) — Vidrio plano que ha sido formado sobre "
            "un metal fundido, por lo general estaño y que cumple los requisitos de "
            "la especificación NTC 1909 (2008).\n"
            "Vidrio Impreso o Grabado (Patterned Glass) — Vidrio plano que tiene un "
            "patrón en una o ambas superficies y que cumple los requisitos de la "
            "especificación NTC 1909 (2008).\n"
            "Vidrio Laminado (Laminated Glass) — Un ensamble que consiste de al "
            "menos una lámina de vidrio adherida a al menos otra lámina de vidrio o "
            "material plástico de vidriado, con una entrecapa orgánica. NOTA: Cuando "
            "el Vidrio laminado se rompe aparecen numerosas grietas pero los "
            "fragmentos de vidrio tienden a adherirse a la entrecapa. Vidrio que "
            "cumple los requisitos de la especificación ASTM C1172:09.\n"
            "Vidrio Plano (Flat Glass) — Término general que comprende vidrio "
            "estirado, vidrio cilindrado, vidrio flotado y diversas formas de vidrio "
            "fabricado con rodillos de laminación y que cumple los requisitos de las "
            "especificaciones de las normas NTC 1909 (2008) o NTC 1804 (1990).\n"
            "Vidrio-plástico para vidriado de seguridad — El término incluye "
            "laminados con una o más capas de vidrio y una o más capas de plástico.\n"
            "Vidrio Recocido (Annealed glass) — Es una lámina de vidrio plano, "
            "monolítico, de espesor uniforme en el cual los esfuerzos superficiales "
            "residuales son cercanos a cero.\n"
            "Vidrio Spandrel (Spandrel glass) — Vidrio arquitectónico que se "
            "utiliza en las áreas donde no hay visibilidad o como material de "
            "fachada para edificios y que cumple los requisitos aplicables de la "
            "especificación ASTM C1048-04.\n"
            "Vidrio Templado (Fully tempered glass) — Vidrio plano que ha sido "
            "tratado térmicamente hasta obtener una compresión alta en la "
            "superficie o el borde y que cumple los requisitos de la especificación "
            "ASTM C1048-04. Cuando se rompe en cualquier punto, la pieza entera se "
            "fragmenta en pequeños pedazos que tienen bordes relativamente romos en "
            "comparación con los bordes de las piezas rotas de vidrio recocido.\n"
            "Vidrio Termoendurecido (Heat-strengthened glass) — Vidrio plano que ha "
            "sido tratado térmicamente hasta lograr una compresión moderada en la "
            "superficie o en el borde, y que cumple los requisitos de la "
            "especificación ASTM C1048-04.\n"
            "Vidrio Transparente (Transparent glass) — Vidrio que transmite la luz "
            "y permite una visión clara a través del mismo y que cumple los "
            "requisitos de la especificación NTC 1909 (2008) o de la NTC 1804(1990) "
            "según sea vidrio flotado o vidrio estirado respectivamente.\n"
            "Vidrio Traslúcido (Translucent glass) — Vidrio que transmite la luz "
            "con grados variables de difusión de forma que la visión no es nítida. "
            "Nota: La difusión de la luz se puede producir mediante la impresión de "
            "un patrón en la superficie del vidrio en el proceso de fabricación, o "
            "mediante un tratamiento superficial después de la fabricación, por "
            "ejemplo grabado con chorro de arena o grabado químico.\n"
            "Vidrio Tratado Térmicamente (Heat Treaterd Glass) — Término general "
            "para el vidrio que se ha sometido a un tratamiento térmico "
            "caracterizado por un enfriamiento rápido para producir una capa "
            "superficial sometida a esfuerzo de compresión."
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
    textos = [c["texto"] for c in CHUNKS]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print("\nBorrando el chunk viejo condensado (NSR10-K-K_4_1_alcance_definiciones)...")
    sb.table("nsr10_chunks").delete().eq("id", "NSR10-K-K_4_1_alcance_definiciones").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de K.4.1 cargados. Numeral K.4.1 completo (glosario A-V).")


if __name__ == "__main__":
    main()
