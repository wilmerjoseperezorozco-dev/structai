"""
NSR-10 Titulo I (Supervision Tecnica) -- cierra el titulo completo, y
corrige un hallazgo serio: 9 chunks con prefijo "I-SEC" estaban cargados
en el corpus atribuidos a secciones I.5, I.7, I.8, I.9 e I.10 -- secciones
que NO EXISTEN. El catalogo maestro verificado pagina por pagina confirma
que Titulo I solo tiene 4 capitulos (I.1 a I.4, paginas I-1 a I-22), y que
I.4 "FINALIZA el capitulo y el Titulo I". Los I-SEC5/7/8/9/10 son contenido
FABRICADO (tablas y formulas inventadas, con cifras que no aparecen en el
texto real -- ej. "Tabla I.3-1" con umbrales de anos de experiencia por
altura de edificio que el I.3 real, de solo ~2 paginas, no contiene). Los
I-SEC1/2/3 (para secciones que si existen) tambien se descartan por venir
del mismo lote no confiable y ya estar cubiertos por chunks verbatim reales
(NSR10-I-I_1-* y NSR10-I-I_2_*, cargados en sesion previa).

Fuente real: NSR-10-1501-1570.pdf (Drive, id 1AXhovLAquw_qFr0I4B7IiTGmuiIl24JP,
Titulo H + Titulo I), paginas internas I-12 a I-22 (I.3 e I.4 completos).

Uso: python _ingest_titulo_i_completo.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título I — Supervisión Técnica"

CHUNKS_A_BORRAR = [
    "I-SEC1-001", "I-SEC2-TAB1", "I-SEC3-TAB1", "I-SEC5-TAB1",
    "I-SEC7-TAB1", "I-SEC8-FORM1", "I-SEC8-TAB1", "I-SEC9-TAB1", "I-SEC10-001",
]

CHUNKS = [
    {
        "id": "NSR10-I-I_3_idoneidad_supervisor",
        "seccion": "I.3 (Idoneidad del supervisor técnico y su personal auxiliar)",
        "titulo": (
            "Idoneidad del supervisor tecnico (Ley 400/1997 Art. 35-38, Ley "
            "1229/2008): debe ser ingeniero civil, arquitecto o constructor "
            "en arquitectura e ingenieria matriculado (o ingeniero mecanico "
            "solo para estructuras metalicas), con mas de 5 anos de "
            "experiencia profesional, e independiente laboralmente del "
            "constructor. NO existe tabla de anos escalonada por altura de "
            "edificio en el texto real -- es un umbral unico de 5 anos."
        ),
        "texto": (
            "NSR-10 Título I — Supervisión Técnica. Capítulo I.3 — Idoneidad "
            "del supervisor técnico y su personal auxiliar.\n\n"
            "I.3.1 General — Las calidades y requisitos del supervisor "
            "técnico están establecidos en los Capítulos 1 y 5 del Título VI "
            "de la Ley 400 de 1997 y en la Ley 1229 de 2008. Según el "
            "Artículo 24 de la Ley 400/1997, la Comisión Asesora Permanente "
            "del Régimen de Construcciones Sismo Resistentes fija los "
            "mecanismos para demostrar experiencia, idoneidad y "
            "conocimientos de quienes ejercen supervisión técnica.\n\n"
            "I.3.2 Del supervisor técnico:\n"
            "  I.3.2.1 PROFESIÓN (Art. 35 Ley 400/1997, Ley 1229/2008): debe "
            "ser ingeniero civil, arquitecto, o constructor en arquitectura "
            "e ingeniería, con matrícula profesional. Excepción: solo para "
            "estructuras METÁLICAS, el supervisor puede ser Ingeniero "
            "Mecánico, igualmente matriculado e inscrito.\n"
            "  I.3.2.2 EXPERIENCIA (Art. 36): debe acreditar ante la "
            "Comisión Asesora Permanente una experiencia MAYOR DE CINCO (5) "
            "AÑOS de ejercicio profesional, contados desde la expedición de "
            "la tarjeta profesional, bajo la dirección de un profesional "
            "facultado, en una o varias de: diseño estructural, "
            "construcción, interventoría, o supervisión técnica. Es un "
            "umbral ÚNICO de 5 años — el Reglamento NO establece una tabla "
            "escalonada de años de experiencia según la altura o el número "
            "de pisos del edificio.\n"
            "  I.3.2.3 INDEPENDENCIA (Art. 37): el supervisor técnico debe "
            "ser laboralmente INDEPENDIENTE del constructor de la estructura "
            "o de los elementos no estructurales cubiertos por el "
            "Reglamento.\n\n"
            "I.3.3 Del personal auxiliar:\n"
            "  I.3.3.1 GENERAL (Art. 38): las calificaciones y experiencia "
            "del personal auxiliar (inspectores, controladores, técnicos) "
            "quedan a JUICIO del supervisor técnico, acordes con las labores "
            "encomendadas y el tamaño/importancia/dificultad de la obra — no "
            "hay una tabla reglamentaria fija de calificaciones por tipo de "
            "personal auxiliar.\n"
            "  I.3.3.2 DIRECCIÓN Y RESPONSABILIDAD (Art. 22): el supervisor "
            "técnico puede delegar labores en personal auxiliar, siempre "
            "bajo su dirección y responsabilidad.\n"
            "  I.3.3.3 RESIDENTES DE SUPERVISIÓN TÉCNICA: deben ser "
            "ingenieros civiles, arquitectos o constructores en arquitectura "
            "e ingeniería matriculados; la experiencia requerida queda a "
            "juicio del supervisor técnico, conmensurable con la obra."
        ),
    },
    {
        "id": "NSR10-I-I_4_1_a_I_4_2_grados_supervision",
        "seccion": "I.4.1 a I.4.2 (Grados de supervisión técnica)",
        "titulo": (
            "Recomendaciones para el ejercicio de la supervision tecnica: 2 "
            "grados -- A (Continua, con residente permanente en obra) y B "
            "(Itinerante, visitas periodicas). Tabla I.4.3-1 determina el "
            "grado recomendado segun area construida, material estructural y "
            "grupo de uso -- edificaciones <3000 m2 estan exentas de "
            "supervision (Art. 18 Ley 400/1997), salvo grupos III/IV."
        ),
        "texto": (
            "NSR-10 Título I — Supervisión Técnica. Capítulo I.4 — "
            "Recomendaciones para el ejercicio de la supervisión técnica. "
            "I.4.1 Generalidades e I.4.2 Alcance recomendado.\n\n"
            "I.4.1.1 Propósito y alcance — estas recomendaciones guían a los "
            "profesionales que realizan supervisión técnica y facilitan el "
            "alcance contractual entre las partes. I.4.1.2 — remite a las "
            "definiciones del Capítulo A.13 y especialmente I.1.1.\n\n"
            "I.4.2.1 Grados de supervisión — se establecen DOS grados: "
            "Grado A (Continua) y Grado B (Itinerante). El grado a usar "
            "depende de las características de la construcción, el grupo de "
            "uso, el sistema estructural y el área de construcción.\n\n"
            "I.4.2.2 GRADO A — Supervisión Técnica CONTINUA: todas las "
            "labores de construcción se supervisan de manera permanente. El "
            "supervisor técnico hace visitas frecuentes y DEBE asignar un "
            "RESIDENTE de supervisión técnica — personal auxiliar profesional "
            "de asistencia permanente en la obra.\n\n"
            "I.4.2.3 GRADO B — Supervisión Técnica ITINERANTE: el supervisor "
            "visita la obra con la frecuencia necesaria para verificar el "
            "avance; para ciertas operaciones debe asistir personalmente él "
            "o su auxiliar profesional. NO es necesario designar personal "
            "auxiliar residente en la obra.\n\n"
            "I.4.2.4 y Tabla I.4.3-1 — Grado recomendado según área "
            "construida, sistema estructural y grupo de uso: \n"
            "  Concreto estructural: <3000 m² con Grupos I-II → Itinerante "
            "(A); Grupos III-IV → Continua (B). Entre 3000-6000 m² con "
            "Grupos I-II → Itinerante; Grupos III-IV → Continua. >6000 m² "
            "(cualquier grupo I-IV) → Continua.\n"
            "  Estructura metálica y madera: misma lógica de umbrales por "
            "área/grupo de uso.\n"
            "  Mampostería: misma lógica; nota adicional recomienda "
            "supervisión Itinerante para mampostería >1000 m².\n\n"
            "Notas clave de la tabla: (1) exentas de Supervisión Técnica "
            "las edificaciones con MENOS de 3000 m² de área construida "
            "(Art. 18 Ley 400/1997) — salvo excepción siguiente; "
            "(2) los Grupos de uso III y IV DEBEN someterse a Supervisión "
            "Técnica INDEPENDIENTEMENTE de su área (Art. 20); "
            "(3) el diseñador estructural o el geotecnista pueden EXIGIR "
            "supervisión técnica sin importar el área, según complejidad; "
            "(4) estructuras diseñadas según Título E (vivienda de baja "
            "altura) están exentas si son menos de 15 unidades de vivienda; "
            "(5) si el proyecto se desarrolla por etapas, el área a "
            "considerar es la de la licencia de construcción vigente."
        ),
    },
    {
        "id": "NSR10-I-I_4_3_procedimientos_control",
        "seccion": "I.4.3.1 a I.4.3.6 (Procedimientos de control)",
        "titulo": (
            "Procedimientos de control del supervisor tecnico: control de "
            "planos (9 aspectos minimos), programa de aseguramiento de "
            "calidad, aprobacion del laboratorio de ensayos (cumplimiento "
            "ICONTEC), ensayos de conformidad con normas y ensayos de "
            "control de calidad remitiendo a las tablas I.2.4-1/I.2.4-2."
        ),
        "texto": (
            "NSR-10 Título I — Supervisión Técnica. I.4.3.1 a I.4.3.6 — "
            "Procedimientos de control (aplican a ambos grados de "
            "supervisión, salvo que se indique lo contrario).\n\n"
            "I.4.3.1 CONTROL DE PLANOS — mínimo debe verificar: grado de "
            "definición (completos/incompletos); definición y consistencia "
            "de dimensiones, cotas y niveles entre plantas/alzados/cortes/"
            "detalles; adecuada definición de calidades de materiales; "
            "cargas de diseño debidamente estipuladas; en casos especiales, "
            "instrucciones de obra falsa, colocación de concreto, "
            "descimbrado, aditivos, tolerancias, niveles de tensionamiento; "
            "coordinación de planos arquitectónicos con los técnicos; "
            "definición del grado de desempeño de elementos no "
            "estructurales; y en general, que existan todas las "
            "indicaciones necesarias para construir adecuadamente.\n\n"
            "I.4.3.3 PROGRAMA DE ASEGURAMIENTO DE CALIDAD — el supervisor "
            "verifica que el constructor disponga de medios adecuados "
            "(dirección, mano de obra, maquinaria, suministro de "
            "materiales) y de un programa de aseguramiento de calidad para: "
            "(a) definir la calidad a alcanzar, (b) obtenerla, "
            "(c) verificar que se alcanzó, y (d) demostrar que fue "
            "definida/obtenida/verificada.\n\n"
            "I.4.3.4 LABORATORIO DE ENSAYO DE MATERIALES — el supervisor "
            "técnico DEBE aprobar el laboratorio de ensayo; es su "
            "responsabilidad asegurar que cumple las disposiciones legales "
            "del ICONTEC y del Ministerio de Ambiente, Vivienda y "
            "Desarrollo Territorial.\n\n"
            "I.4.3.5 ENSAYOS DE CONFORMIDAD CON LAS NORMAS — antes de "
            "iniciar la obra, el supervisor exige al constructor que los "
            "materiales cumplan las especificaciones de calidad de planos y "
            "Reglamento, mediante resultados de ensayos sobre muestras "
            "representativas de lotes recientes del proveedor; solicita "
            "certificados de conformidad cuando el Reglamento lo exija.\n\n"
            "I.4.3.6 ENSAYOS DE CONTROL DE CALIDAD — durante la "
            "construcción se toman muestras periódicas según las "
            "frecuencias prescritas por el Reglamento (remite explícitamente "
            "a las Tablas I.2.4-1 e I.2.4-2, que definen la frecuencia de "
            "ensayo por material — ya cargadas en el corpus como "
            "NSR10-I-I_2_controles_exigidos-*); los ensayos de laboratorio "
            "deben cumplir lo especificado por el Reglamento para cada "
            "material."
        ),
    },
    {
        "id": "NSR10-I-I_4_3_7_tabla_controles_ejecucion",
        "seccion": "I.4.3.7 (Tabla I.4.3-2, controles durante la ejecución)",
        "titulo": (
            "Tabla I.4.3-2: puntos de control obligatorios por el supervisor "
            "tecnico durante la ejecucion de obra, por grado A (continua) o "
            "B (itinerante), organizados por operacion: cimentacion, "
            "formaletas, armaduras, concreto/mortero, prefabricados, "
            "mamposteria, estructuras metalicas (incluyendo galvanizado y "
            "pintura), madera, y elementos no estructurales."
        ),
        "texto": (
            "NSR-10 Título I — Supervisión Técnica. I.4.3.7 — Control de "
            "ejecución. El supervisor técnico inspecciona como mínimo, "
            "directamente o por personal auxiliar según el grado (Tabla "
            "I.4.3-2):\n\n"
            "CIMENTACIÓN: replanteo geométrico, dimensiones de excavaciones, "
            "limpieza de fondo, sistema de drenaje, estratos y niveles de "
            "fundación, protección de excavaciones.\n\n"
            "FORMALETAS Y OBRA FALSA: alineamiento y tolerancias, acabado y "
            "verticalidad de superficies, resistencia/estabilidad ante "
            "asentamientos, aprobación de cálculos de cimbra, "
            "limpieza/impermeabilidad, aberturas de inspección, aprobación "
            "del estudio de descimbrado.\n\n"
            "COLOCACIÓN DE ARMADURAS: grado del acero (fy), diámetro, número "
            "de barras, ganchos y longitud; empalmes (traslapados, "
            "mecánicos o soldados); colocación, recubrimientos, distancia "
            "entre barras, sujeción; limpieza de barras y zona de vaciado.\n\n"
            "MEZCLADO/TRANSPORTE/COLOCACIÓN/CURADO de concretos y morteros: "
            "aprobación de diseños de mezcla, medios y procedimientos de "
            "mezclado/transporte/colocación/compactación, tiempo entre "
            "mezcla y colocación, homogeneidad en estado fresco, "
            "provisiones climáticas, juntas de construcción/dilatación, "
            "sistemas de curado.\n\n"
            "ELEMENTOS PREFABRICADOS (incluye mampostería): características "
            "geométricas, condiciones de almacenaje, curado/protección "
            "contra humedad, transporte e izado, secuencia de colocación.\n\n"
            "MUROS Y MAMPOSTERÍA: alineamiento y plomo, celdas para "
            "inyección y ventanas de inspección, espesor de juntas de pega, "
            "traba adecuada, alturas de inyección, tuberías embebidas, "
            "juntas de control, espigos/anclajes/traslapos, apuntalamientos "
            "provisionales.\n\n"
            "ESTRUCTURAS METÁLICAS: especificación de materiales y fy, "
            "dimensiones y rectitud del conjunto, calificación de "
            "soldadores, biseles e intersticios, procedimientos de "
            "soldadura, cumplimiento de tamaños/longitudes de soldadura, "
            "grado de fusión (porosidad/grietas/socavaciones), marcado de "
            "piezas. GALVANIZADO: limpieza previa, acabado/peso/adherencia/"
            "uniformidad de la capa de zinc, fragilidad por galvanizado. "
            "PINTURA: limpieza, acabado, espesor y adherencia de la capa. "
            "ESTRUCTURA MONTADA: conexión a anclajes, verticalidad y "
            "alineamiento, arriostramientos instalados, torques de pernos "
            "previstos en planos, defectos de soldadura (penetración "
            "insuficiente, poros, socavaciones).\n\n"
            "MADERA: identificación de especies, contenido de humedad, "
            "inmunización y defectos; soportes/platinas/conectores/"
            "adhesivos/anclas/pernos; deflexiones/derivas/plomo; protección "
            "contra deterioro por agua; ventilación de áticos.\n\n"
            "ELEMENTOS NO ESTRUCTURALES: muros de fachada e interiores "
            "(separados o que admitan deformación de la estructura), "
            "enchapes de fachada, áticos/parapetos/antepechos, vidrios, "
            "paneles prefabricados, COLUMNAS CORTAS O CAUTIVAS. Exención: "
            "Grupos de uso I y II en zona de amenaza sísmica BAJA están "
            "exentos de estos requisitos de elementos no estructurales."
        ),
    },
    {
        "id": "NSR10-I-I_4_3_8_informe_final",
        "seccion": "I.4.3.8 (Informe final de supervisión técnica)",
        "titulo": (
            "Informe final de supervision tecnica: contenido minimo del "
            "registro escrito (constructor, supervisor, materiales, "
            "ensayos, NTC empleadas, registro fotografico) y modelo/formato "
            "de la certificacion final que acredita cumplimiento de la "
            "NSR-10, con los 6 controles certificados (planos, "
            "especificaciones, materiales, calidad, ejecucion, elementos no "
            "estructurales)."
        ),
        "texto": (
            "NSR-10 Título I — Supervisión Técnica. I.4.3.8 — Informe "
            "final.\n\n"
            "El registro escrito de las labores realizadas debe incluir una "
            "memoria descriptiva de los controles, con como mínimo: nombre "
            "del constructor y del supervisor técnico, procedencia de los "
            "materiales, planta de producción, listado de Normas Técnicas "
            "(NTC) empleadas para los ensayos, ensayos realizados, "
            "laboratorios utilizados, análisis de resultados, grado de "
            "desempeño de los elementos no estructurales, control de "
            "modificaciones de planos durante la construcción, registro "
            "fotográfico, y constancia del supervisor técnico certificando "
            "que la construcción se realizó de acuerdo con el Reglamento.\n\n"
            "MODELO DE INFORME FINAL DE SUPERVISIÓN TÉCNICA (formato "
            "sugerido por NSR-10): certifica que la obra (nombre, "
            "ubicación, etapa, licencia de construcción) fue sometida "
            "durante la construcción al proceso de supervisión técnica del "
            "Título I, y que se cumplieron 6 controles:\n"
            "  1. Control de planos: existencia de todos los planos "
            "necesarios para cada elemento estructural.\n"
            "  2. Control de especificaciones: cumplimiento de las "
            "especificaciones técnicas de la norma para cada material, más "
            "las particulares de planos y diseñadores.\n"
            "  3. Control de materiales: cumplimiento de requisitos "
            "generales y normas técnicas de calidad de NSR-10, con "
            "monitoreo constante de resultados.\n"
            "  4. Control de Calidad: ensayos a materiales y productos "
            "terminados conforme a planos y NSR-10.\n"
            "  5. Control de la ejecución: verificación de que la obra se "
            "ejecutó según planos, especificaciones y requisitos "
            "constructivos de NSR-10.\n"
            "  6. Elementos no estructurales: grado de desempeño acorde con "
            "el grupo de uso, conservando el criterio del diseñador de "
            "elementos no estructurales.\n"
            "El informe se firma con fecha, ciudad, y número de tarjeta "
            "profesional tanto del Supervisor Técnico como del Director de "
            "Obra."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print(f"Borrando {len(CHUNKS_A_BORRAR)} chunks I-SEC fabricados/no confiables...")
    sb.table("nsr10_chunks").delete().in_("id", CHUNKS_A_BORRAR).execute()

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
    print(f"OK: {len(rows)} chunks reales de Título I cargados. Título I completo (I.1-I.4).")


if __name__ == "__main__":
    main()
