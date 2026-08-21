"""
Correccion de retrieval 2026-08-20: NSR10-F-F_3_10_control_calidad y
NSR10-F-F_3_11_ensayos_calificacion (cargados en _ingest_titulo_f_f37_a_f311.py)
mezclaban varios subtemas en un solo chunk cada uno (soldaduras+pernos;
precalificacion+ensayos viga-columna+ensayos BRB) -- mismo patron de dilucion
de embeddings ya identificado antes en la sesion con F.2.10 (soldaduras+
pernos). Verificado empiricamente: similitud coseno real de 0.3-0.46 contra
consultas especificas, perdiendo contra chunks de otros titulos con score
0.5+. Se reemplazan por 5 chunks single-topic.

Uso: python _ingest_titulo_f_f310_f311_split.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS_A_BORRAR = [
    "NSR10-F-F_3_10_control_calidad",
    "NSR10-F-F_3_11_ensayos_calificacion",
]

CHUNKS = [
    {
        "id": "NSR10-F-F_3_10_inspeccion_soldaduras",
        "seccion": "F.3.10.2 (Inspección de soldaduras)",
        "titulo": (
            "Inspeccion de soldaduras del Sistema de Resistencia Sismica de "
            "acero: visual en 3 etapas (antes/durante/despues) segun AWS "
            "D.1.8, y ensayos no destructivos obligatorios (100% ultrasonido "
            "en penetracion completa >=8mm, 25% particulas magneticas en "
            "soldaduras viga-columna, area k)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.10.2, Inspección de "
            "soldaduras del Sistema de Resistencia Sísmica (SRS) de acero, "
            "según AWS D.1.8.\n\n"
            "F.3.10.2.1 Inspección visual — método PRINCIPAL de control, en "
            "3 etapas:\n"
            "  ANTES de soldar: preparación de junta (alineamiento, abertura "
            "de raíz), limpieza de superficies, puntos de soldadura, "
            "acondicionamiento de platinas de respaldo y agujeros de acceso.\n"
            "  DURANTE la soldadura: parámetros del equipo, velocidad de "
            "avance, precalentamiento y temperatura entre pases, posición de "
            "soldadura, calificación del operario, condiciones ambientales "
            "(viento, lluvia, temperatura).\n"
            "  DESPUÉS de soldar: limpieza, identificación del operario, "
            "tamaño/longitud/localización, ausencia de fisuras, fusión "
            "adecuada, tamaño de cráteres, socavación, porosidad; remoción de "
            "platinas de respaldo y extensiones.\n\n"
            "F.3.10.2.2 Ensayos NO destructivos OBLIGATORIOS (más allá de la "
            "inspección visual):\n"
            "  Área 'k' (soldaduras de placas de enchape/continuidad/"
            "atiesadores): partículas magnéticas hasta 75 mm de la soldadura.\n"
            "  Soldaduras acanaladas de penetración completa: ULTRASONIDO al "
            "100% en espesores >=8 mm; RADIOGRÁFICO en espesores <8 mm; "
            "PARTÍCULAS MAGNÉTICAS al 25% de todas las soldaduras "
            "viga-columna acanaladas de penetración completa.\n"
            "  Material base >38 mm con carga perpendicular a la laminación: "
            "ultrasonido para desgarramiento lamelar.\n"
            "  Reparaciones en vigas de sección reducida (RBS): partículas "
            "magnéticas en toda soldadura de reparación.\n"
            "  Reducción de porcentaje de ensayo permitida (a 25% ultrasonido/"
            "radiográfico, o 10% partículas magnéticas) SOLO si el operario "
            "demuestra <5% de rechazos — NUNCA en área 'k', reparaciones, o "
            "remoción de respaldos/extensiones (ahí siempre el porcentaje "
            "completo fijo)."
        ),
    },
    {
        "id": "NSR10-F-F_3_10_inspeccion_pernos",
        "seccion": "F.3.10.3 (Inspección de pernos)",
        "titulo": (
            "Inspeccion de pernos pretensionados del Sistema de Resistencia "
            "Sismica de acero: 3 etapas (antes/durante/despues del "
            "empernado) -- seleccion correcta, verificacion de "
            "pretensionamiento segun F.2.10.3.1, orden de apriete desde el "
            "punto mas rigido."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.10.3, Inspección de pernos "
            "del Sistema de Resistencia Sísmica (SRS) de acero. El principal "
            "método de control es la observación directa de las operaciones "
            "de empernado, en 3 etapas:\n\n"
            "(1) ANTES del empernado: selección correcta de los pernos "
            "especificados para la unión; selección del procedimiento de "
            "empernado adecuado para la junta; correcta fabricación de los "
            "elementos de la conexión, incluido el tipo de preparación de "
            "superficie; ensayos de calificación del procedimiento de "
            "empernado; almacenamiento adecuado de pernos, tuercas y "
            "arandelas.\n\n"
            "(2) DURANTE el empernado: correcta colocación de pernos y "
            "arandelas en todos los agujeros; verificación de apriete "
            "inicial; garantía de que uno de los componentes del perno NO "
            "rote durante el tensionamiento (control con llave de tuercas); "
            "verificación del pretensionamiento según el método de "
            "tensionamiento utilizado, cumpliendo F.2.10.3.1; verificación "
            "de que los pernos se aprieten desde el punto de MAYOR RIGIDEZ "
            "de la junta hacia los bordes libres — este orden evita dejar "
            "tensiones residuales desiguales en la junta.\n\n"
            "(3) DESPUÉS del empernado: documentar las conexiones aceptadas "
            "o rechazadas."
        ),
    },
    {
        "id": "NSR10-F-F_3_11_precalificacion",
        "seccion": "F.3.11.1 (Precalificación de conexiones)",
        "titulo": (
            "Precalificacion de conexiones sismicas viga-columna/"
            "vinculo-columna de acero: dos caminos validos -- usar una "
            "conexion ya precalificada del estandar ANSI/AISC 358 (el mas "
            "comun en la practica, sin necesidad de ensayos adicionales) o "
            "aprobacion directa de la Comision Asesora Permanente. Contenido "
            "obligatorio del registro de precalificacion."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.11.1, Precalificación de "
            "conexiones viga-columna y vínculo-columna.\n\n"
            "Aplica a conexiones resistentes a momento en PRM-DES y PRM-DMO, "
            "y a conexiones vínculo-columna en PAE. Se permite usar "
            "conexiones precalificadas que estén dentro de los límites "
            "aplicados en sus ensayos de precalificación, SIN necesidad de "
            "realizar pruebas cíclicas de calificación adicionales para cada "
            "proyecto — este es el camino más usado en la práctica.\n\n"
            "F.3.11.1.2.2 Autorización de la precalificación — dos caminos "
            "válidos: (1) usar las conexiones precalificadas del estándar "
            "ANSI/AISC 358 'Prequalified Connections for Special and "
            "Intermediate Steel Moment Frames for Seismic Applications', o "
            "versión más reciente; (2) en su defecto, la Comisión Asesora "
            "Permanente para el Régimen de Construcciones Sismo Resistentes "
            "es la responsable de aprobar la precalificación de una conexión "
            "específica y sus límites asociados.\n\n"
            "Variables consideradas en la precalificación (F.3.11.1.4): "
            "parámetros de la viga/vínculo (forma de sección, método de "
            "fabricación, peralte, relación luz/peralte, relación ancho-"
            "espesor, arriostramiento lateral); parámetros de la columna "
            "(análogos, más orientación respecto a la viga); relaciones "
            "viga-columna (resistencia de zona de panel, relación de "
            "momentos); placas de continuidad; soldaduras (localización, "
            "tipo, resistencia y tenacidad del metal de aporte); pernos "
            "(diámetro, grado ASTM A325/A490, tipo de perforación); y "
            "parámetros de fabricación.\n\n"
            "Registro de precalificación OBLIGATORIO (F.3.11.1.6) para una "
            "conexión precalificada: (1) descripción gráfica de la conexión; "
            "(2) comportamiento esperado elástico e inelástico, localización "
            "de la zona inelástica y estados límite que controlan; "
            "(3) sistemas para los que aplica (PRM-DES/DMO o PAE); "
            "(4) límites de todas las variables de calificación; "
            "(5) listado de soldaduras de demanda crítica; (6) definición de "
            "la zona protegida; (7) procedimiento detallado de diseño; "
            "(8) referencias/reportes de ensayo que soportan la "
            "precalificación; (9) resumen de control de calidad requerido. "
            "Cuando los límites de una conexión precalificada contradicen "
            "otros requisitos de F.3, GOBIERNA la conexión precalificada."
        ),
    },
    {
        "id": "NSR10-F-F_3_11_ensayos_viga_columna",
        "seccion": "F.3.11.2 (Ensayos cíclicos de conexión viga-columna/vínculo-columna)",
        "titulo": (
            "Ensayos ciclicos de calificacion de conexiones viga-columna "
            "(PRM-DES/DMO) y vinculo-columna (PAE) cuando NO se usa una "
            "conexion precalificada: requisitos del especimen (peralte "
            ">=90%, peso >=75% del prototipo), secuencia de carga "
            "estandarizada por angulo de deriva (6 ciclos crecientes hasta "
            "fractura), y criterio de aceptacion de 1 ciclo completo sin "
            "perder resistencia."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.11.2, Ensayos Cíclicos de "
            "Calificación de conexiones viga-columna (PRM-DES/DMO) y "
            "vínculo-columna (PAE) — se usan cuando NO se aplica una "
            "conexión precalificada de F.3.11.1.\n\n"
            "Requisitos del espécimen de prueba: mínimo una columna con "
            "vigas o vínculos conectados a uno o ambos lados; puntos de "
            "inflexión que coincidan aproximadamente con los del prototipo "
            "real; la rotación inelástica del espécimen debe desarrollarse "
            "en los MISMOS miembros/elementos que en el prototipo (viga o "
            "vínculo, zona de panel, columna, o elementos de conexión), "
            "dentro de un margen del 25% respecto a la proporción prevista.\n\n"
            "Tamaño de miembros: peralte de viga/vínculo del ensayo >=90% "
            "del prototipo; peso por unidad de longitud >=75%; peralte de "
            "columna de ensayo >=90% del prototipo. Esfuerzo de fluencia: "
            "DEBE determinarse mediante ensayo real de los materiales usados "
            "en el espécimen — los certificados de calidad de acería NUNCA "
            "se aceptan como sustituto. El esfuerzo de fluencia de la viga "
            "no debe estar más del 15% por debajo de Ry*Fy del grado de "
            "acero del prototipo; columnas y elementos de conexión, no más "
            "del 15% por encima ni por debajo.\n\n"
            "SECUENCIA DE CARGA para conexiones viga-columna (control por "
            "ángulo de deriva θ, ciclos crecientes hasta la falla):\n"
            "  6 ciclos a θ=0.00375 rad, 6 a 0.005, 6 a 0.0075, 4 a 0.01, "
            "2 a 0.015, 2 a 0.02, 2 a 0.03, 2 a 0.04 rad — luego continuar "
            "con incrementos de 0.01 rad, 2 ciclos por paso, hasta la "
            "falla.\n\n"
            "SECUENCIA DE CARGA para conexiones vínculo-columna (control por "
            "ángulo de rotación del vínculo γtotal): arranca igual (6 ciclos "
            "a 0.00375-0.01 rad) pero añade más pasos intermedios hasta "
            "γtotal=0.09 rad antes de continuar con incrementos de 0.02 rad — "
            "refleja la mayor capacidad de rotación esperada de un vínculo "
            "corto frente a una rótula de viga normal.\n\n"
            "Criterio de aceptación (F.3.11.2.9): el espécimen debe sostener "
            "el ángulo de deriva o de rotación del vínculo requerido durante "
            "al menos UN ciclo completo de carga, sin caer por debajo de la "
            "resistencia mínima exigida.\n\n"
            "El informe de ensayo obligatorio debe incluir: dibujo del "
            "conjunto y de la conexión, listado de variables esenciales, "
            "historia de carga/desplazamiento, gráfica momento-deriva (o "
            "cortante-rotación para vínculos), rotación inelástica total y "
            "su desglose por componente, observaciones cronológicas "
            "(fluencia, deslizamiento, fractura), y el modo de falla que "
            "controló el ensayo."
        ),
    },
    {
        "id": "NSR10-F-F_3_11_ensayos_BRB",
        "seccion": "F.3.11.3 (Ensayos cíclicos de riostras de pandeo restringido)",
        "titulo": (
            "Ensayos ciclicos de calificacion para riostras de pandeo "
            "restringido (BRB, sistema PAPR): obligatorios siempre (no hay "
            "camino de precalificacion tipo ANSI 358). Requiere minimo 1 "
            "ensayo de conjunto + 1 ensayo de riostra sola, secuencia de "
            "carga por deformacion axial hasta 200 veces la deformacion de "
            "fluencia, criterio de aceptacion: relacion compresion/tension "
            "<=1.3."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — F.3.11.3, Ensayos Cíclicos de "
            "Calificación para riostras de pandeo restringido (BRB, sistema "
            "PAPR de F.3.6.4). A diferencia de las conexiones viga-columna "
            "(F.3.11.1), aquí NO existe un camino de precalificación tipo "
            "ANSI/AISC 358 — el ensayo es SIEMPRE obligatorio, porque el "
            "comportamiento depende del sistema de restricción al pandeo "
            "patentado de cada fabricante, no solo de la sección de acero "
            "del núcleo.\n\n"
            "Se requieren DOS ensayos mínimo: (1) ensayo de CONJUNTO "
            "(assembly test — riostra + conexiones + elementos que "
            "restringen su estabilidad, reproduciendo las demandas "
            "rotacionales del prototipo) — demuestra que el diseño soporta "
            "las demandas reales de deformación y rotación; (2) ensayo de "
            "RIOSTRA sola (uniaxial) — demuestra que el comportamiento "
            "histerético dentro del conjunto es consistente con el de la "
            "riostra aislada.\n\n"
            "Similitud exigida entre espécimen de ensayo y prototipo: misma "
            "sección transversal y orientación del núcleo de acero; "
            "resistencia a fluencia axial del núcleo (Pysc) del espécimen no "
            "debe variar más del 50% respecto al prototipo; mismo material y "
            "método de separación entre núcleo y mecanismo de restricción al "
            "pandeo; esfuerzo de fluencia medido del núcleo del espécimen "
            "debe ser al menos 90% del prototipo (por ensayo real, nunca "
            "certificado de acería).\n\n"
            "SECUENCIA DE CARGA (control por deformación axial Δb, relativa "
            "a Δby=deformación de primera fluencia significativa y "
            "Δbm=deformación correspondiente a la deriva de piso de diseño, "
            "que no puede tomarse menor a 0.01 veces la altura de piso):\n"
            "  2 ciclos a Δb=Δby, 2 a 0.5*Δbm, 2 a Δbm, 2 a 1.5*Δbm, "
            "2 a 2*Δbm — luego ciclos adicionales completos a 1.5*Δbm hasta "
            "que la deformación axial inelástica ACUMULADA alcance al menos "
            "200 VECES la deformación de fluencia (no aplica al espécimen de "
            "conjunto, solo al de riostra sola).\n\n"
            "Criterios de aceptación (F.3.11.3.10): comportamiento "
            "histerético estable y repetitivo con incremento de rigidez; "
            "SIN fractura, inestabilidad de la riostra ni falla de la "
            "conexión en su extremo; la fuerza máxima de tensión y "
            "compresión en cada ciclo NO debe ser menor que la resistencia "
            "nominal del núcleo, para deformaciones mayores que Δby; y — el "
            "límite numérico clave — la RELACIÓN entre la fuerza máxima de "
            "COMPRESIÓN y la fuerza máxima de TENSIÓN (el factor β usado en "
            "el diseño según F.3.6.4.2.1) NO debe exceder 1.3, para "
            "deformaciones mayores que Δby — acota en la práctica qué tan "
            "asimétrico puede ser el comportamiento real de una riostra BRB "
            "frente al ideal simétrico tensión=compresión."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print(f"Borrando {len(CHUNKS_A_BORRAR)} chunks obsoletos (multi-tema)...")
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
    print(f"OK: {len(rows)} chunks single-topic cargados con embedding.")


if __name__ == "__main__":
    main()
