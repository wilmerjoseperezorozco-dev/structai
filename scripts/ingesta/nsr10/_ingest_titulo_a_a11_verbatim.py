"""
Ingesta verbatim de Título A, Capítulo A.11 (Instrumentación sísmica) --
NSR-10. Fase 1 del plan de cierre del Título A (2026-09-22), auditoría
real de numerales confirmó A.11 en 0% de cobertura (13 numerales reales,
ninguno con chunk).

Fuente: NSR-10-156-158.pdf, páginas PDF 1-3 (A-113 a A-115, capítulo
completo, PDF completo), leídas visualmente con Read pages= sobre el PDF
nativo.

Uso: python _ingest_titulo_a_a11_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"

CHUNKS = [
    {
        "id": "NSR10-A-A_11_1_1_a_A_11_1_2_instrumentacion_acelerografos",
        "seccion": "A.11.1.1 a A.11.1.2 — Instrumentación y acelerógrafos",
        "titulo": "Título A, A.11.1.1 (alcance del capítulo) y A.11.1.2 (acelerógrafos digitales de movimiento fuerte): objetivos de la instrumentación (a) y aprobación del tipo de instrumento por INGEOMINAS/Red Nacional de Acelerógrafos (b).",
        "texto": (
            "CAPÍTULO A.11 — INSTRUMENTACIÓN SÍSMICA\n\n"
            "A.11.1 — GENERAL\n\n"
            "A.11.1.1 — INSTRUMENTACIÓN — En el presente Capítulo se indica cuándo "
            "deben colocarse instrumentos sísmicos en las edificaciones, en dónde "
            "deben localizarse y quién corre con los costos de los instrumentos, "
            "del espacio que éstos ocupen y del mantenimiento y vigilancia de los "
            "mismos.\n\n"
            "A.11.1.2 — ACELERÓGRAFOS — En la instrumentación sísmica de "
            "edificaciones deben emplearse acelerógrafos digitales de movimiento "
            "fuerte.\n\n"
            "(a) Objetivos de la instrumentación — Dentro de los objetivos de este "
            "tipo de instrumentación se encuentra la recolección de registros que "
            "permitan, entre otros: la medición de los períodos de vibración de la "
            "edificación al verse sometida a movimientos sísmicos, la "
            "determinación del nivel de daño que ocurrió a la edificación debido a "
            "la ocurrencia de un sismo que la afecte, la identificación de efectos "
            "de sitio causados por la amplificación de las ondas sísmicas debida a "
            "los estratos de suelo subyacentes, el grado de atenuación que sufren "
            "las ondas sísmicas al viajar desde el lugar donde ocurre la "
            "liberación de energía hasta el sitio donde se encuentre localizada la "
            "edificación, y en general el mejoramiento sobre el conocimiento que "
            "se tiene a nivel nacional de los fenómenos sísmicos y sus efectos "
            "sobre las construcciones y los materiales de construcción "
            "nacionales. La valiosa información que se recolecta por medio de la "
            "instrumentación permitirá realizar ajustes a los requisitos del "
            "presente Reglamento en sus ediciones futuras; llevando, a una "
            "reducción de la vulnerabilidad sísmica de las edificaciones "
            "colombianas, y, muy seguramente, a una reducción de los costos de "
            "proveer seguridad sísmica a ellas.\n\n"
            "(b) Aprobación del tipo de instrumento — INGEOMINAS es la entidad "
            "gubernamental que opera la Red Nacional de Acelerógrafos y es la "
            "encargada de aprobar los tipos de instrumentos que se coloquen en las "
            "edificaciones que los requieran de acuerdo con los requisitos del "
            "presente Capítulo. El INGEOMINAS mantendrá una lista de los tipos de "
            "instrumentos posibles de ser utilizados y las especificaciones "
            "mínimas de los mismos para ser colocados en edificaciones, tal como "
            "requiere el presente Capítulo. La Red Nacional de Acelerógrafos del "
            "INGEOMINAS y quien designe la autoridad municipal o distrital donde "
            "esté ubicada la edificación, deben recibir, sin costo alguno y por lo "
            "menos una vez al año, copia de los registros obtenidos, "
            "independientemente de quien sea el propietario del instrumento. "
            "Cuando el municipio o distrito donde se encuentra localizada la "
            "edificación haya, de acuerdo con A.2.9.3.7(d), desarrollado un plan "
            "de instalación, operación y mantenimiento de una red de acelerógrafos "
            "de movimientos fuertes, la entidad municipal o distrital que "
            "administre esta red podrá, si así lo desea, asumir las funciones que "
            "en esta misma sección se asignan al INGEOMINAS, a quien deberá "
            "informar sobre esta decisión."
        ),
    },
    {
        "id": "NSR10-A-A_11_1_3_localizacion",
        "seccion": "A.11.1.3 — Localización",
        "titulo": "Título A, A.11.1.3: 4 tipos de localización de instrumentos sísmicos (a) instrumentación en la altura, (b) instrumento único, (c) instrumento de campo abierto, (d) arreglo de instrumentos), A.11.1.3.1 (estudio geotécnico obligatorio) y A.11.1.3.2 (curadurías no expiden licencia sin el espacio dispuesto).",
        "texto": (
            "A.11.1.3 — LOCALIZACIÓN — La definición de la localización de los "
            "instrumentos sísmicos acelerográficos dentro de las edificaciones es "
            "responsabilidad del Ingeniero que realice el diseño estructural del "
            "proyecto, atendiendo las recomendaciones dadas en la presente sección "
            "y en A.11.1.4. La localización de los instrumentos debe estar "
            "comprendida dentro de uno de los siguientes tipos:\n\n"
            "(a) Instrumentación en la altura — Se dispone un mínimo de tres "
            "instrumentos en la altura de la edificación, de tal manera que "
            "exista al menos uno en su base, uno aproximadamente a media altura "
            "de la edificación y uno en el nivel superior. En este caso el "
            "instrumento colocado en la base debe tener tres sensores triaxiales "
            "con dos componentes horizontales ortogonales y una componente "
            "vertical, y los otros dos instrumentos pueden tener solo dos "
            "sensores horizontales ortogonales.\n\n"
            "(b) Instrumento único en la edificación — Cuando se coloca un solo "
            "instrumento en la edificación, éste debe localizarse en la base de "
            "la misma.\n\n"
            "(c) Instrumento de campo abierto — Se coloca un instrumento sobre el "
            "terreno, alejado de las edificaciones, por lo menos una distancia "
            "igual a su altura.\n\n"
            "(d) Arreglo de instrumentos — Se dispone un conjunto de instrumentos "
            "que cubren las localizaciones anteriores. En este caso los "
            "instrumentos deben tener un dispositivo que inicie el registro de "
            "aceleraciones en todos ellos simultáneamente.\n\n"
            "A.11.1.3.1 — En todas las edificaciones donde se coloquen "
            "instrumentos sísmicos, se debe realizar un estudio geotécnico cuyo "
            "alcance permita definir las propiedades dinámicas del suelo en el "
            "sitio.\n\n"
            "A.11.1.3.2 — Las Curadurías o las entidades encargadas de expedir las "
            "licencias de construcción de acuerdo con lo requerido en la Ley 388 "
            "de 1997 y sus decretos reglamentarios se abstendrán de expedir la "
            "correspondiente licencia de construcción, incluyendo las de "
            "remodelaciones y reforzamientos futuros, cuando en los casos que se "
            "requiera instrumentación sísmica según el presente Reglamento no se "
            "hayan dispuesto en el proyecto arquitectónico los espacios a que hace "
            "referencia este Capítulo y no se haya consignado en el reglamento de "
            "propiedad horizontal de la edificación, cuando se trate de "
            "copropiedades, las obligaciones de la copropiedad respecto a la "
            "ubicación, suministro, mantenimiento y vigilancia del instrumento. La "
            "autoridad competente se abstendrá de expedir el certificado de "
            "permiso de ocupación al que se refiere el Artículo 46 del Decreto 564 "
            "de 2006 cuando no se haya instalado el instrumento o instrumentos que "
            "se requieren de acuerdo con lo dispuesto en el presente Capítulo del "
            "Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_11_1_4_caracteristicas_espacio",
        "seccion": "A.11.1.4 — Características del espacio donde se coloca el instrumento",
        "titulo": "Título A, A.11.1.4: requisitos físicos del espacio para el instrumento (2 m² mínimo, 2 m de altura libre, alejado de vibraciones, toma eléctrica doble con breaker de 15 amperios, piso de concreto mínimo 15 cm, tubo PVC de 1 pulgada entre espacios de un arreglo).",
        "texto": (
            "A.11.1.4 — CARACTERÍSTICAS DEL ESPACIO DONDE SE COLOCA EL INSTRUMENTO "
            "— El espacio físico donde se coloca el instrumento debe tener al "
            "menos un área de dos metros cuadrados con una dimensión mínima en "
            "planta de un metro y una altura libre mínima de dos metros, debe "
            "estar alejado de las zonas alta circulación, de maquinarias y "
            "equipos que induzcan vibraciones. El espacio debe ser cerrado, pero "
            "con ventilación adecuada, y ser de un material adecuado para "
            "garantizar la seguridad del instrumento. Además se debe colocar "
            "dentro de él una toma eléctrica doble, un breaker de 15 amperios y "
            "una salida de iluminación eléctrica con interruptor. El piso debe "
            "ser de concreto y de un espesor suficiente para permitir el anclaje "
            "del instrumento (mínimo 15 cm). El espacio no puede ser utilizado "
            "para ningún otro fin diferente al de albergar el instrumento. Cuando "
            "se utilice un arreglo de instrumentos, los espacios que alberguen "
            "los diferentes instrumentos, deben disponer de una conexión entre "
            "ellos por medio de un tubo de PVC de diámetro mínimo de una pulgada "
            "(1\") para poder realizar las conexiones eléctricas entre "
            "instrumentos."
        ),
    },
    {
        "id": "NSR10-A-A_11_1_5_costos",
        "seccion": "A.11.1.5 — Costos",
        "titulo": "Título A, A.11.1.5: distribución de costos de instrumentación sísmica — (a) costo de los instrumentos (propietario del proyecto), (b) costo del espacio (propietarios de la edificación), (c) costo de mantenimiento, (d) costo de vigilancia/póliza de seguros.",
        "texto": (
            "A.11.1.5 — COSTOS — Los diferentes costos en que se incurre en la "
            "instrumentación de una edificación se distribuyen de la siguiente "
            "manera:\n\n"
            "(a) Costo de los instrumentos — Los instrumentos serán adquiridos por "
            "la persona, natural o jurídica, a cuyo nombre se expida la licencia "
            "de construcción de la edificación, quien además debe costear su "
            "instalación. El INGEOMINAS se reserva el derecho de colocar "
            "instrumentos adicionales, a su costo, dentro de los espacios que se "
            "destinen para la instrumentación sísmica. La propiedad de los "
            "instrumentos será de quienes los adquieran. Independientemente de "
            "quien sea el propietario del instrumento, la Red Sismológica "
            "Nacional y quien designe la autoridad municipal o distrital donde "
            "esté ubicada la edificación, deben recibir copia, sin costo alguno, "
            "de los registros obtenidos por medio de los instrumentos.\n\n"
            "(b) Costo de los espacios donde se colocan los instrumentos — El "
            "costo del espacio o espacios donde se colocan los instrumentos será "
            "de cargo de los propietarios de la edificación. El propietario, o "
            "propietarios, de la edificación darán libre acceso a estos espacios "
            "a los funcionarios del INGEOMINAS, o a quienes ellos deleguen, para "
            "efectos de instalación, mantenimiento y retiro de los registros del "
            "instrumento. Cuando se trate de una copropiedad, en el reglamento de "
            "copropiedad deben incluirse cláusulas al respecto.\n\n"
            "(c) Costo del mantenimiento de los instrumentos — El costo de "
            "mantenimiento de los instrumentos correrá por cuenta del propietario "
            "o propietarios de la edificación. Esta obligación debe quedar "
            "incluida en el reglamento de copropiedad. Quien preste el "
            "mantenimiento debe ser aprobado por el INGEOMINAS. El mantenimiento "
            "debe realizarse con la frecuencia que requiera el fabricante del "
            "instrumento; no obstante, ésta debe realizarse con una periodicidad "
            "no mayor de un año.\n\n"
            "(d) Costo de la vigilancia del instrumento — Los costos de vigilancia "
            "de los instrumentos correrán por cuenta de los propietarios de la "
            "edificación donde se encuentren localizados, sean éstos de su "
            "propiedad o no. Los propietarios son responsables del instrumento "
            "para efectos de su seguridad, y deben adquirir y mantener una "
            "póliza de seguros, la cual debe cubrir el costo de reposición del "
            "instrumento en caso de hurto, substracción u otra eventualidad."
        ),
    },
    {
        "id": "NSR10-A-A_11_2_colocacion_instrumentos",
        "seccion": "A.11.2 — Colocación de instrumentos sísmicos",
        "titulo": "Título A, A.11.2: cuándo colocar instrumentos según zona de amenaza sísmica — A.11.2.1 zona alta (umbral 20.000 m², 3-10 pisos), A.11.2.2 zona intermedia (umbral 30.000 m², 5-15 pisos), A.11.2.3 zona baja (sin obligación).",
        "texto": (
            "A.11.2 — COLOCACIÓN DE INSTRUMENTOS SÍSMICOS\n\n"
            "Dentro de las construcciones que se adelanten en el territorio "
            "nacional, cubiertas por el alcance del presente Reglamento, deben "
            "colocarse instrumentos sísmicos en los siguientes casos:\n\n"
            "A.11.2.1 — ZONAS DE AMENAZA SÍSMICA ALTA — En las siguientes "
            "edificaciones, localizadas en zonas de amenaza sísmica alta deben "
            "colocarse instrumentos sísmicos:\n\n"
            "(a) En toda edificación con un área construida de más de 20 000 m² y "
            "que tenga entre 3 y 10 pisos debe colocarse un instrumento sísmico "
            "como mínimo. El espacio para su colocación será colindante con el "
            "sistema estructural y debe localizarse en el nivel inferior de la "
            "edificación.\n"
            "(b) En toda edificación con un área construida de más de 20 000 m² "
            "que tenga entre 11 y 20 pisos, deben colocarse al menos 2 "
            "instrumentos sísmicos, en espacios colindantes, localizados, uno en "
            "el nivel inferior y otro cerca de la cubierta. En este caso el "
            "instrumento localizado cerca de la cubierta puede tener solo dos "
            "sensores horizontales ortogonales.\n"
            "(c) En toda edificación de 21 o más pisos, independientemente del "
            "área construida, deben colocarse 3 instrumentos, en espacios "
            "colindantes con el sistema estructural. Uno en el nivel inferior, "
            "uno aproximadamente a mitad de la altura y otro en inmediaciones de "
            "la cubierta. Los instrumentos deben conformar un arreglo. "
            "Alternativamente al arreglo de tres instrumentos, se puede realizar "
            "la instalación de tres sensores de aceleración, uno triaxial y dos "
            "biaxiales como indica A.11.1.3(a), conectados a un sistema central "
            "de captura de datos.\n"
            "(d) En todo conjunto habitacional que tenga más de 200 unidades de "
            "vivienda, que no sean de interés social, se debe colocar un "
            "instrumento de campo abierto.\n\n"
            "A.11.2.2 — ZONAS DE AMENAZA SÍSMICA INTERMEDIA — En las siguientes "
            "edificaciones, localizadas en zonas de amenaza sísmica intermedia "
            "deben colocarse instrumentos sísmicos:\n\n"
            "(a) En toda edificación con un área construida de más de 30 000 m² y "
            "que tenga entre 5 y 15 pisos debe colocarse un instrumento como "
            "mínimo. El espacio donde se coloque el instrumento será colindante "
            "con el sistema estructural y debe localizarse en el nivel inferior "
            "de la edificación.\n"
            "(b) En toda edificación con un área construida de más de 30 000 m² "
            "que tenga entre 16 y 25 pisos, deben colocarse al menos 2 "
            "instrumentos sísmicos, en espacios colindantes con el sistema "
            "estructural, localizados, uno en el nivel inferior y otro cerca a "
            "la cubierta.\n"
            "(c) En toda edificación de más de 25 pisos, independientemente del "
            "área construida, deben colocarse 3 instrumentos sísmicos, en "
            "espacios colindantes con el sistema estructural. Uno en el nivel "
            "inferior, uno aproximadamente a mitad de la altura y otro en "
            "inmediaciones de la cubierta. Los instrumentos deben conformar un "
            "arreglo. Alternativamente al arreglo de tres instrumentos, se puede "
            "realizar la instalación de tres sensores triaxiales de aceleración, "
            "conectados a un sistema central de captura de datos.\n"
            "(d) Todo conjunto habitacional que tenga más de 300 unidades de "
            "vivienda, que no sean de interés social, debe colocarse un "
            "instrumento sísmico de campo abierto.\n\n"
            "A.11.2.3 — ZONAS DE AMENAZA SÍSMICA BAJA — En las edificaciones "
            "localizadas en zonas de amenaza sísmica baja no hay obligación de "
            "colocar instrumentos sísmicos."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks-padre de A.11...")
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

    print(f"Subiendo {len(rows)} chunks-padre de A.11 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_a11_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
