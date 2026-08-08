"""
Inserta el núcleo verbatim real de la Resolución 4272 de 2021 (Ministerio
del Trabajo) — Requisitos mínimos de seguridad para el desarrollo de
Trabajo en Alturas (TA) — en nsr10_chunks.

Esta resolución REEMPLAZA a la Resolución 1409 de 2012 (derogada por el
artículo 68 de la Resolución 4272 de 2021, efectiva desde agosto de 2022).
No cargar la 1409 como vigente — StructAI daría una norma derogada.

Fuente: texto extraído directo del HTML de
https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=120880
(Régimen Legal de Bogotá D.C. — SISJUR), NO de los archivos "RAG+CAG"
de Google Drive (confirmados como resúmenes sintéticos generados, no el
texto real de la norma — ver scripts/ingesta/sgsst/sgsst_raw/ para el
HTML/texto crudo descargado el 2026-08-08).

Núcleo insertado — Título I (Disposiciones Generales), Capítulo I completo:
- Artículo 1 (Objeto) + Artículo 2 (Ámbito de aplicación, Parágrafos 1-2)
- Artículo 3 (Definiciones) — las ~60 definiciones completas, en 2 chunks

Títulos II (Requisitos de seguridad: medidas de prevención/protección,
sistemas, permiso de trabajo en alturas), III (Formación y capacitación)
y IV (Disposiciones finales) quedan para una siguiente ronda.

Uso: python scripts/ingesta/sgsst/insert_res4272_2021_nucleo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CHUNKS = [
    {
        "id": "RES4272-2021-ART1_2",
        "capitulo": "Resolución 4272 de 2021 — Requisitos de Seguridad para Trabajo en Alturas",
        "seccion": "Artículo 1 y 2",
        "titulo": "Título I, Capítulo I — Objeto de la resolución y ámbito de aplicación (empleadores, ARL, centros de capacitación), excepciones",
        "texto": """ARTÍCULO 1°. OBJETO. Establecer los requisitos mínimos de seguridad para el desarrollo de Trabajos en Alturas (TA), y lo concerniente con la capacitación y formación de los trabajadores y aprendices en los centros de entrenamiento de Trabajo en Alturas (AT).

ARTÍCULO 2°. ÁMBITO DE APLICACIÓN. La presente resolución aplica a todos los empleadores contratantes, contratistas, aprendices y trabajadores de todas las actividades económicas que desarrollen trabajo en alturas, así mismo a las Administradoras de Riesgos Laborales y centros de capacitación y entrenamiento de Trabajo en Alturas (TA).

PARÁGRAFO 1°. Se exceptúan de la aplicación de la presente resolución, las siguientes actividades: 1. Actividades de atención de emergencias y rescate. 2. Operaciones militares y policiales en acciones propias del servicio. 3. Actividades deportivas, de alta montaña o andinismo. 4. Desarrollo de actos lúdicos o artísticas. 5. Actividades realizadas sobre animales. Para realizar las actividades mencionadas, se debe llevar a cabo un proceso de identificación de peligros, valoración de riesgos e implementación de controles, siguiendo estándares nacionales o internacionales, garantizando siempre la seguridad de las personas que realizan la actividad.

PARÁGRAFO 2°. Si en el análisis de riesgo que realice el coordinador de trabajo en alturas o el responsable del Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST) de la empresa, se identifican condiciones peligrosas que puedan afectar al trabajador en el momento de una caída, tales como áreas con obstáculos, bordes peligrosos, elementos salientes, puntiagudos, sistemas energizados, máquinas en movimiento, entre otros, incluso en alturas inferiores a las establecidas en la presente resolución, se deberán garantizar las medidas de prevención y protección contra caídas necesaria para proteger al trabajador.""",
    },
    {
        "id": "RES4272-2021-ART3_definiciones_1",
        "capitulo": "Resolución 4272 de 2021 — Requisitos de Seguridad para Trabajo en Alturas",
        "seccion": "Artículo 3 (parte 1 de 2)",
        "titulo": "Título I, Capítulo I — Definiciones: absorbedor de energía, anclaje, arnés, capacitación, coordinador de TA, eslingas, gancho, líneas de vida (A-M)",
        "texto": """ARTÍCULO 3°. DEFINICIONES. Para los efectos de la presente resolución, se aplican las siguientes definiciones:

Absorbedor de energía: Equipo que hace parte integral de un sistema de detención de caídas, cuya función es disminuir y limitar las fuerzas de impacto en el cuerpo del trabajador o en los puntos de anclaje en el momento de una caída.

Actividad o tarea no rutinaria: Actividad que no forma parte de la operación normal de la organización o actividad que la organización ha determinado como no rutinaria por su baja frecuencia de ejecución.

Actividad o tarea rutinaria: Actividad que forma parte de la operación normal de la organización, se ha planificado y es estandarizable.

Adaptador de anclaje: Un componente o subsistema que funciona como interfaz entre el anclaje y un sistema de detención de caídas, restricción, acceso o posicionamiento con el propósito de acoplar el sistema al anclaje.

Anclaje: Punto seguro fijo o móvil al que pueden conectarse adaptadores de anclaje o equipos personales de restricción, posicionamiento, acceso y/o de detención de caídas, capaz de soportar con seguridad las cargas aplicadas por el sistema o subsistema de protección contra caídas. Deben ser diseñados y aprobados por una persona calificada e instalados por una persona competente.

Arnés de cuerpo completo: Equipo de protección personal diseñado para contener el torso y distribuir las fuerzas de la detención de caídas en al menos la parte superior de los muslos, la pelvis, el pecho y los hombros. Es fabricado en correas debidamente cosidas y aseguradas entre sí, e incluye elementos para conectar equipos y asegurarse a un punto de anclaje. Debe ser certificado bajo un estándar nacional o internacionalmente aceptado.

Autocuidado: Se define como actitud y aptitud para realizar de forma voluntaria y sistemática actividades dirigidas a conservar la salud y prevenir accidentes o enfermedades.

Ayudante de seguridad: Trabajador autorizado, debidamente certificado, designado por el empleador para revisar las condiciones de seguridad en el sitio de trabajo y controlar el acceso a las áreas de riesgo de caída de objetos o personas.

Baranda: Barrera que se instala al borde de un lugar para prevenir la posibilidad de caída. Debe garantizar una capacidad de carga y contar con un travesaño de agarre superior, una barrera colocada a nivel del suelo para evitar la caída de objetos y un travesaño intermedio o barrera intermedia que prevenga el paso de personas entre el travesaño superior y la barrera inferior.

Capacitación: Es toda actividad a corto plazo realizada en una empresa o institución autorizada, con el objetivo de preparar el talento humano mediante un proceso en el cual el participante comprende, asimila, incorpora y aplica conocimientos, habilidades, destrezas que lo hacen competente para ejercer sus labores de TA en el puesto de trabajo.

Centro de capacitación y entrenamiento: Espacio destinado y acondicionado, con infraestructura adecuada para desarrollar y fundamentar, el conocimiento y las habilidades necesarias para el desempeño del trabajador y la aplicación de las técnicas relacionadas con el uso de los equipos y la configuración de sistemas de prevención y protección contra caídas para TA.

Coordinador de trabajo en alturas: Trabajador designado por el empleador, capaz de identificar peligros en el sitio en donde se realiza trabajo en alturas, que tiene autorización para aplicar medidas correctivas inmediatas para controlar los riesgos asociados a dichos peligros. La designación del coordinador de TA no significa la creación de un nuevo cargo, ni aumento en la nómina de la empresa, esta función debe ser llevada a cabo por la persona designada por el empleador y puede ser ejecutada por supervisores o coordinadores de procesos, por el coordinador o ejecutor del Sistema de Gestión de Seguridad y Salud en el Trabajo o cualquier otro trabajador que el empleador considere adecuado para cumplir sus funciones.

Delimitación del área: Medida de prevención colectiva que tiene por objeto limitar el área o zona de peligro de caída del trabajador o de objetos y prevenir el acercamiento de este a la zona de caída.

Distancia de desaceleración: Distancia vertical entre el punto donde termina la caída libre y se comienza a activar el absorbedor de energía hasta que este último pare por completo.

Distancia de detención: Distancia vertical total requerida para detener una caída, incluyendo la distancia de desaceleración y la distancia de activación.

Eslinga de detención de caídas: Equipo certificado, que se compone de un sistema de cuerda, reata, cable u otros materiales que cuenta con un absorbedor de energía, que permiten la unión al arnés del trabajador al punto de anclaje. Su función es detener la caída de una persona, absorbiendo la energía de la caída de modo que al trabajador se le limite la carga máxima que recibe. Debe cumplir: a) Todos sus componentes deben ser certificados. b) Resistencia mínima de 5.000 libras (22,2 kilo newtons - 2.272 kg). c) Tener un absorbedor de energía; y d) Tener en sus extremos sistemas de conexión certificados.

Eslinga de posicionamiento o eslinga de restricción: Equipo certificado compuesto de elementos de cuerda, cintas, cable u otros materiales con resistencia mínima de 5.000 libras (22,2 kilo newtons - 2.272 kg) que puede tener en sus extremos ganchos o conectores que permiten la unión de arnés del trabajador y al punto de anclaje. Todas las eslingas y sus componentes deben ser certificados.

Gancho: Equipo metálico con resistencia mínima de 5.000 libras (22.2 kilo newtons - 2.272 kg), que es parte integral de los conectores y permite realizar conexiones entre el arnés, las eslingas y los puntos de anclaje; los ganchos están provistos de una argolla u ojo al que está asegurado el material del equipo conector, y un sistema de apertura y cierre con doble sistema de accionamiento para evitar una apertura accidental.

Hueco: Para efecto de esta norma es el espacio vacío o brecha en una superficie o pared, a través del cual se puede producir una caída de 2,00 metros o más de personas u objetos.

Línea de advertencia: Es una medida de prevención de caídas que demarca un área en la que se puede trabajar sin un sistema de protección. Consiste en una línea de acero, cuerda, cadena u otros materiales, sostenida mediante soportes que la mantengan a una altura entre 0,85 metros y 1 metro sobre la superficie de trabajo.

Líneas de vida horizontales: Equipos certificados de cables de acero, cuerdas, rieles u otros materiales que debidamente anclados a la estructura donde se realizará el trabajo en alturas, permiten la conexión de los equipos personales de protección contra caídas y el desplazamiento horizontal del trabajador sobre una determinada superficie. La estructura de anclaje debe ser evaluada con métodos de ingeniería.

Líneas de vida horizontales fijas: Son aquellas debidamente ancladas a una determinada estructura, fabricadas en cable de acero o rieles metálicos y según su longitud, se soportan por puntos de anclaje intermedios; deben ser diseñadas e instaladas por una persona calificada.

Líneas de vida horizontales portátiles: Son equipos certificados y preensamblados, elaborados en cuerda o cable de acero, con sistemas absorbentes de choque, conectores en sus extremos, un sistema tensionador y dispositivos adaptadores de anclaje; se instalan por trabajadores autorizados entre dos puntos de comprobada resistencia y se verifica su instalación por el coordinador de trabajo en alturas o una persona calificada.

Líneas de vida verticales: Equipos certificados de cables de acero, cuerdas, rieles u otros materiales que debidamente ancladas en un punto superior a la zona de labor, protegen al trabajador en su desplazamiento vertical. Serán diseñadas e instaladas por una persona calificada o por una persona avalada por el fabricante.

Máxima Fuerza de Detención (MFD): La máxima fuerza que puede soportar el trabajador sin sufrir una lesión, es 1.800 libras (8 kilo newtons - 816 kg).

Medidas activas de protección contra caídas: Son las que involucran la participación del trabajador. Incluyen: punto de anclaje, mecanismos de anclaje, conectores, arnés de cuerpo completo y plan de rescate.

Medidas colectivas de prevención: Todas aquellas actividades dirigidas a informar o demarcar la zona de peligro y evitar una caída de alturas o ser lesionado por objetos que caigan. Sirven como barreras informativas y corresponden a medidas de control en el medio.

Medidas de prevención contra caídas: Conjunto de acciones individuales o colectivas que se implementan para advertir o evitar la caída de personas y objetos cuando se realizan trabajos en alturas. Incluyen la capacitación, los procedimientos, el entrenamiento, la aptitud psicofísica, la vigilancia en salud laboral, los sistemas de ingeniería para prevención de caídas, medidas colectivas de prevención, permiso de trabajo en alturas, listas de chequeo, y los análisis de peligros.

Medidas de protección contra caídas: Conjunto de acciones individuales o colectivas que se implementan para detener la caída de personas y objetos una vez ocurra o para mitigar sus consecuencias.

Medidas pasivas de protección contra caídas: Están diseñadas para detener o capturar al trabajador en el trayecto de su caída, sin permitir impacto contra estructuras o elementos, requieren poca o ninguna intervención del trabajador.

Mosquetón: Equipo certificado, metálico en forma de argolla que permite realizar conexiones directas del arnés a los puntos de anclaje, o servir de conexión entre equipos de protección contra caídas o rescate a su punto de anclaje. Deben tener una resistencia mínima certificada de 5.000 libras (22,2 kilo newtons - 2.272 kg).""",
    },
    {
        "id": "RES4272-2021-ART3_definiciones_2",
        "capitulo": "Resolución 4272 de 2021 — Requisitos de Seguridad para Trabajo en Alturas",
        "seccion": "Artículo 3 (parte 2 de 2)",
        "titulo": "Título I, Capítulo I — Definiciones: permiso de trabajo en alturas, persona calificada, sistemas de posicionamiento/restricción, trabajador autorizado, trabajo en alturas (N-U)",
        "texto": """Permiso de trabajo en alturas: Mecanismo administrativo que, mediante la verificación y control previo de todos los aspectos relacionados en la presente resolución, tiene como objeto fomentar la prevención durante la realización de trabajos en alturas.

Persona calificada: Según las disposiciones establecidas en la Ley 400 de 1997 relacionado con los profesionales a cargo o la norma que la modifique o sustituya.

Persona en proceso de capacitación y entrenamiento: Aprendiz objeto de acciones de capacitación y entrenamiento.

Plan de mejora: Documento elaborado por el proveedor inscrito de capacitación y entrenamiento en trabajo en alturas, presentado para su aprobación ante la Dirección de Movilidad y Capacitación para el Trabajo del Ministerio del Trabajo, para subsanar hallazgos de incumplimiento de condiciones técnicas, operativas y jurídicas.

Programa de prevención y protección contra caídas en alturas: Es la planeación, organización, ejecución y evaluación de las actividades identificadas por el empleador como necesarias de implementar en los sitios de trabajo en forma integral e interdisciplinaria, para prevenir la ocurrencia de accidentes y enfermedades laborales por trabajo en alturas y, llegado el caso, las medidas de protección implementadas para detener la caída una vez ocurra o mitigar sus consecuencias.

Proveedor de capacitación y entrenamiento: Organización o persona inscrita en el registro de la Dirección de Movilidad y Capacitación para el Trabajo del Ministerio del Trabajo, que oferta el servicio de capacitación y entrenamiento en trabajo en alturas.

Requerimiento de claridad o espacio libre de caída: Distancia vertical requerida por un trabajador en caso de una caída, para evitar que este impacte contra el suelo o contra un obstáculo. Dependerá principalmente de la configuración del sistema de detención de caídas utilizado.

Rodapié: Elemento horizontal construido en material rígido, que se instala en el perímetro de una plataforma, en la parte inferior de la baranda de seguridad de protección, para evitar la caída al vacío de herramientas de mano o elementos de trabajo.

Señalización del área: Es una medida de prevención que incluye avisos informativos que indican con letras o símbolos gráficos el peligro de caída de personas y objetos.

Sistema de acceso por cuerdas: Es un sistema con equipos certificados, configurado para que, a través de cuerdas y equipos, un trabajador autorizado pueda acceder, ascender, descender o realizar una progresión a un lugar específico.

Sistema de posicionamiento: Sistema con equipos certificados, configurado para ubicar al trabajador en un sitio de trabajo de modo que permanezca parcial o totalmente suspendido de sus equipos, limitando la distancia de caída del trabajador a máximo 60 cm, de modo que pueda utilizar las dos manos para su labor.

Sistema de restricción: Sistema con un conjunto de equipos certificados de diferentes longitudes fijas o graduables que también puede permitir la conexión de sistemas de bloqueo o freno. Su función es limitar los desplazamientos del trabajador para que no llegue a un sitio del que pueda caer por un borde o lado desprotegido, huecos o aberturas. No debe ser usado en superficies con una inclinación superior de 18,4 grados.

Sistemas de ingeniería para prevención de caídas: Son aquellos sistemas relacionados con cambios o modificación en el diseño, montaje, construcción, instalación, puesta en funcionamiento, para eliminar, sustituir o mitigar el riesgo de caída — desde evitar el trabajo en alturas hasta implementar mecanismos que permitan menor tiempo de exposición.

Sistemas de protección de caídas: Sistema con un conjunto de elementos, anclajes y/o equipos certificados, que el empleador dispone para que el trabajador autorizado use para su protección ante una caída, y que garantiza que reduce las fuerzas sobre el cuerpo al máximo permitido y aprobado por una persona calificada.

Trabajador autorizado: Trabajador que ha sido designado por la organización para realizar trabajos en alturas, cuya salud fue evaluada y se le consideró apto para trabajo en alturas y que posee la constancia de capacitación y entrenamiento de trabajo en alturas o el certificado de competencia laboral para trabajo en alturas.

Trabajo en alturas: Toda actividad que realiza un trabajador que ocasione la suspensión y/o desplazamiento, en el que se vea expuesto a un riesgo de caída, mayor a 2,0 metros, con relación del plano de los pies del trabajador al plano horizontal inferior más cercano a él.

Trabajos en suspensión: Tareas en las que el trabajador debe "suspenderse" o colgarse y mantenerse en esa posición, mientras realiza su tarea o mientras es subido o bajado.

Unidades Vocacionales de Aprendizaje en Empresas (Uvae): Son mecanismos dentro de las empresas que buscan desarrollar conocimiento en la organización mediante procesos de autoformación, con el fin de preparar, entrenar, reentrenar, complementar y certificar la capacidad del recurso humano para realizar labores seguras en trabajo en alturas dentro de la empresa.""",
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Mismo chunker validado en insert_titulo_d_nucleo.py / insert_titulo_h_i_nucleo.py:
    divide por parrafo -> oracion -> coma hasta respetar el limite real de
    tokens del tokenizer (no una aproximacion por caracteres)."""
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
                "capitulo": chunk["capitulo"],
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
        rows.append({**f, "embedding": emb})

    print(f"{len(CHUNKS)} bloques originales (Res. 4272/2021 Título I) -> {len(rows)} subchunks reales:")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en nsr10_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
