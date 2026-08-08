"""
Inserta el núcleo verbatim real del Decreto 1072 de 2015 (Decreto Único
Reglamentario del Sector Trabajo) — Libro 2, Parte 2, Título 4, Capítulo 6:
Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST) — en
nsr10_chunks.

Este decreto sigue VIGENTE (verificado 2026-08-08) — es el decreto marco
del SG-SST en Colombia, continuamente actualizado por decretos posteriores
pero no derogado.

Aclaración importante encontrada al extraer: el Título 4 completo del
decreto se llama "RIESGOS LABORALES" y tiene varios capítulos (1: ARL y
disposiciones generales de riesgos laborales; 5: Consejo Nacional de
Riesgos Laborales; etc.) — el SG-SST específicamente es el CAPÍTULO 6
(Art. 2.2.4.6.1 en adelante), no todo el Título 4. Confirma y corrige la
estructura que traía el archivo sintético "RAG+CAG Decreto1972 2015.pdf"
de Google Drive (que describía el SG-SST como si ocupara los 10 capítulos
completos del Título 4 — no es así en el texto real).

Fuente: texto extraído directo del HTML de
https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173
(Función Pública — Gestor Normativo, actualizado a la fecha de consulta),
NO del archivo "RAG+CAG" de Google Drive (confirmado como resumen
sintético generado, no el texto real — ver
scripts/ingesta/sgsst/sgsst_raw/decreto_1072_2015.txt para el texto
crudo descargado el 2026-08-08).

Núcleo insertado — Capítulo 6, primeros 2 artículos:
- Artículo 2.2.4.6.1 (Objeto y campo de aplicación del SG-SST)
- Artículo 2.2.4.6.2 (Definiciones — 36 términos + Parágrafos 1 y 2)

El resto del Capítulo 6 (política de SST, organización, planificación,
aplicación, auditoría, mejora continua — Art. 2.2.4.6.3 en adelante)
queda para una siguiente ronda.

Uso: python scripts/ingesta/sgsst/insert_decreto1072_2015_nucleo.py [--dry-run]
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
        "id": "DECRETO1072-2015-ART_2_2_4_6_1",
        "capitulo": "Decreto 1072 de 2015 — Libro 2, Parte 2, Título 4, Capítulo 6 (SG-SST)",
        "seccion": "Artículo 2.2.4.6.1",
        "titulo": "Capítulo 6 — Objeto y campo de aplicación del Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST)",
        "texto": """ARTÍCULO 2.2.4.6.1. Objeto y campo de aplicación. El presente capítulo tiene por objeto definir las directrices de obligatorio cumplimiento para implementar el Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST), que deben ser aplicadas por todos los empleadores públicos y privados, los contratantes de personal bajo modalidad de contrato civil, comercial o administrativo, las organizaciones de economía solidaria y del sector cooperativo, las empresas de servicios temporales y tener cobertura sobre los trabajadores dependientes, contratistas, trabajadores cooperados y los trabajadores en misión. (Decreto 1443 de 2014, art. 1)""",
    },
    {
        "id": "DECRETO1072-2015-ART_2_2_4_6_2_def_1",
        "capitulo": "Decreto 1072 de 2015 — Libro 2, Parte 2, Título 4, Capítulo 6 (SG-SST)",
        "seccion": "Artículo 2.2.4.6.2 (parte 1 de 2)",
        "titulo": "Capítulo 6 — Definiciones del SG-SST: acción correctiva/preventiva/de mejora, alta dirección, amenaza, ciclo PHVA, condiciones de trabajo, matriz legal",
        "texto": """ARTÍCULO 2.2.4.6.2. Definiciones. Para los efectos del presente capítulo se aplican las siguientes definiciones:

1. Acción correctiva: Acción tomada para eliminar la causa de una no conformidad detectada u otra situación no deseable.

2. Acción de mejora: Acción de optimización del Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST), para lograr mejoras en el desempeño de la organización en la seguridad y la salud en el trabajo de forma coherente con su política.

3. Acción preventiva: Acción para eliminar o mitigar la(s) causa(s) de una no conformidad potencial u otra situación potencial no deseable.

4. Actividad no rutinaria: Actividad que no forma parte de la operación normal de la organización o actividad que la organización ha determinado como no rutinaria por su baja frecuencia de ejecución.

5. Actividad rutinaria: Actividad que forma parte de la operación normal de la organización, se ha planificado y es estandarizable.

6. Alta dirección: Persona o grupo de personas que dirigen y controlan una empresa.

7. Amenaza: Peligro latente de que un evento físico de origen natural, o causado, o inducido por la acción humana de manera accidental, se presente con una severidad suficiente para causar pérdida de vidas, lesiones u otros impactos en la salud, así como también daños y pérdidas en los bienes, la infraestructura, los medios de sustento, la prestación de servicios y los recursos ambientales.

8. Autorreporte de condiciones de trabajo y salud: Proceso mediante el cual el trabajador o contratista reporta por escrito al empleador o contratante las condiciones adversas de seguridad y salud que identifica en su lugar de trabajo.

9. Centro de trabajo: Se entiende por Centro de Trabajo a toda edificación o área a cielo abierto destinada a una actividad económica en una empresa determinada.

10. Ciclo PHVA: Procedimiento lógico y por etapas que permite el mejoramiento continuo a través de los siguientes pasos: Planificar (planificar la forma de mejorar la seguridad y salud de los trabajadores, encontrando qué cosas se están haciendo incorrectamente o se pueden mejorar y determinando ideas para solucionar esos problemas), Hacer (implementación de las medidas planificadas), Verificar (revisar que los procedimientos y acciones implementados están consiguiendo los resultados deseados) y Actuar (realizar acciones de mejora para obtener los mayores beneficios en la seguridad y salud de los trabajadores).

11. Condiciones de salud: El conjunto de variables objetivas y de autorreporte de condiciones fisiológicas, psicológicas y socioculturales que determinan el perfil sociodemográfico y de morbilidad de la población trabajadora.

12. Condiciones y medio ambiente de trabajo: Aquellos elementos, agentes o factores que tienen influencia significativa en la generación de riesgos para la seguridad y salud de los trabajadores, entre otros: a) Las características generales de los locales, instalaciones, máquinas, equipos, herramientas, materias primas, productos y demás útiles existentes en el lugar de trabajo; b) Los agentes físicos, químicos y biológicos presentes en el ambiente de trabajo y sus correspondientes intensidades, concentraciones o niveles de presencia; c) Los procedimientos para la utilización de los agentes citados que influyan en la generación de riesgos para los trabajadores; y d) La organización y ordenamiento de las labores, incluidos los factores ergonómicos o biomecánicos y psicosociales.

13. Descripción sociodemográfica: Perfil sociodemográfico de la población trabajadora, que incluye la descripción de las características sociales y demográficas de un grupo de trabajadores, tales como: grado de escolaridad, ingresos, lugar de residencia, composición familiar, estrato socioeconómico, estado civil, raza, ocupación, área de trabajo, edad, sexo y turno de trabajo.

14. Efectividad: Logro de los objetivos del Sistema de Gestión de la Seguridad y Salud en el Trabajo con la máxima eficacia y la máxima eficiencia.

15. Eficacia: Es la capacidad de alcanzar el efecto que espera o se desea tras la realización de una acción.

16. Eficiencia: Relación entre el resultado alcanzado y los recursos utilizados.

17. Emergencia: Es aquella situación de peligro o desastre o la inminencia del mismo, que afecta el funcionamiento normal de la empresa. Requiere de una reacción inmediata y coordinada de los trabajadores, brigadas de emergencias y primeros auxilios y en algunos casos de otros grupos de apoyo dependiendo de su magnitud.

18. Evaluación del riesgo: Proceso para determinar el nivel de riesgo asociado al nivel de probabilidad de que dicho riesgo se concrete y al nivel de severidad de las consecuencias de esa concreción.

19. Evento Catastrófico: Acontecimiento imprevisto y no deseado que altera significativamente el funcionamiento normal de la empresa, implica daños masivos al personal que labora en instalaciones, parálisis total de las actividades de la empresa o una parte de ella y que afecta a la cadena productiva, o genera destrucción parcial o total de una instalación.

20. Identificación del peligro: Proceso para establecer si existe un peligro y definir las características de este.

21. Indicadores de estructura: Medidas verificables de la disponibilidad y acceso a recursos, políticas y organización con que cuenta la empresa para atender las demandas y necesidades en Seguridad y Salud en el Trabajo.

22. Indicadores de proceso: Medidas verificables del grado de desarrollo e implementación del SG-SST.

23. Indicadores de resultado: Medidas verificables de los cambios alcanzados en el periodo definido, teniendo como base la programación hecha y la aplicación de recursos propios del programa o del sistema de gestión.

24. Matriz legal: Es la compilación de los requisitos normativos exigibles a la empresa acorde con las actividades propias e inherentes de su actividad productiva, los cuales dan los lineamientos normativos y técnicos para desarrollar el Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST), el cual deberá actualizarse en la medida que sean emitidas nuevas disposiciones aplicables.""",
    },
    {
        "id": "DECRETO1072-2015-ART_2_2_4_6_2_def_2",
        "capitulo": "Decreto 1072 de 2015 — Libro 2, Parte 2, Título 4, Capítulo 6 (SG-SST)",
        "seccion": "Artículo 2.2.4.6.2 (parte 2 de 2)",
        "titulo": "Capítulo 6 — Definiciones del SG-SST: mejora continua, no conformidad, peligro, política de SST, riesgo, vigilancia epidemiológica; Parágrafos 1-2 (equivalencia salud ocupacional / SST)",
        "texto": """25. Mejora continua: Proceso recurrente de optimización del Sistema de Gestión de la Seguridad y Salud en el Trabajo, para lograr mejoras en el desempeño en este campo, de forma coherente con la política de Seguridad y Salud en el Trabajo (SST) de la organización.

26. No conformidad: No cumplimiento de un requisito. Puede ser una desviación de estándares, prácticas, procedimientos de trabajo, requisitos normativos aplicables, entre otros.

27. Peligro: Fuente, situación o acto con potencial de causar daño en la salud de los trabajadores, en los equipos o en las instalaciones.

28. Política de seguridad y salud en el trabajo: Es el compromiso de la alta dirección de una organización con la seguridad y la salud en el trabajo, expresadas formalmente, que define su alcance y compromete a toda la organización.

29. Registro: Documento que presenta resultados obtenidos o proporciona evidencia de las actividades desempeñadas.

30. Rendición de cuentas: Mecanismo por medio del cual las personas e instituciones informan sobre su desempeño.

31. Revisión proactiva: Es el compromiso del empleador o contratante que implica la iniciativa y capacidad de anticipación para el desarrollo de acciones preventivas y correctivas, así como la toma de decisiones para generar mejoras en el SG-SST.

32. Revisión reactiva: Acciones para el seguimiento de enfermedades laborales, incidentes, accidentes de trabajo y ausentismo laboral por enfermedad.

33. Requisito Normativo: Requisito de seguridad y salud en el trabajo impuesto por una norma vigente y que aplica a las actividades de la organización.

34. Riesgo: Combinación de la probabilidad de que ocurra una o más exposiciones o eventos peligrosos y la severidad del daño que puede ser causada por estos.

35. Valoración del riesgo: Consiste en emitir un juicio sobre la tolerancia o no del riesgo estimado.

36. Vigilancia de la salud en el trabajo o vigilancia epidemiológica de la salud en el trabajo: Comprende la recopilación, el análisis, la interpretación y la difusión continuada y sistemática de datos a efectos de la prevención. Es indispensable para la planificación, ejecución y evaluación de los programas de seguridad y salud en el trabajo, el control de los trastornos y lesiones relacionadas con el trabajo y el ausentismo laboral por enfermedad, así como para la protección y promoción de la salud de los trabajadores. Dicha vigilancia comprende tanto la vigilancia de la salud de los trabajadores como la del medio ambiente de trabajo.

PARÁGRAFO 1. En aplicación de lo establecido en el artículo 10 de la Ley 1562 de 2012, para todos los efectos se entenderá como seguridad y salud en el trabajo todo lo que antes de la entrada en vigencia de dicha ley hacía referencia al término salud ocupacional.

PARÁGRAFO 2. Conforme al parágrafo anterior se entenderá el Comité Paritario de Salud Ocupacional como Comité Paritario en Seguridad y Salud en el Trabajo y el Vigía en Salud Ocupacional como Vigía en Seguridad y Salud en el Trabajo, quienes tendrán las funciones establecidas en la normatividad vigente. (Decreto 1443 de 2014, art. 2)""",
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Mismo chunker validado en insert_titulo_d_nucleo.py / insert_res4272_2021_nucleo.py:
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

    print(f"{len(CHUNKS)} bloques originales (Decreto 1072/2015 Cap. 6) -> {len(rows)} subchunks reales:")
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
