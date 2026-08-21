"""
Manual de Evaluacion y Reforzamiento Sismico para Reduccion de Vulnerabilidad
en Viviendas (Build Change + Swisscontact Colombia, 2015, aprobado por la
CASACRS mediante Acta 124 del 4 de marzo de 2015 como regimen de excepcion
al NSR-10). Es la fuente directa que AIS 410-23 (2023) actualizo y formalizo.

Fuente: https://get.buildchange.org/wp-content/uploads/2016/04/15-11-05-BC_Manual-de-Evaluacion-y-Reforzamiento.pdf
(sitio oficial de la ONG Build Change, publicacion abierta). Resumen tecnico
en palabras propias con atribucion, no reproduccion literal extensa; no se
distribuye el PDF a traves de la app.

Uso: python _ingest_buildchange_pam.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "Manual Build Change/Swisscontact 2015 — Evaluación y Reforzamiento Sísmico de Vivienda (aprobado CASACRS Acta 124/2015, régimen de excepción NSR-10, base de AIS 410-23)"

CHUNKS = [
    {
        "id": "BUILDCHANGE-2015-metodo_PAM",
        "seccion": "Método PAM (Porcentaje de Área de Muros)",
        "titulo": (
            "Metodologia cuantitativa PAM para evaluar si una vivienda de mamposteria "
            "necesita refuerzo sismico: PAM_requerido = bPAM_requerido x CB x CQ x CR x "
            "CP x CW x 1/R (minimo 8% para no reforzada, 4% para confinada), comparado "
            "contra PAM_efectiva de la vivienda real. Con todos los factores C definidos "
            "cuantitativamente -- calidad del bloque, calidad de obra, vulnerabilidad, "
            "piso, peso sismico. Es el motor de calculo detras de AIS 410-23."
        ),
        "texto": (
            "Manual de Evaluación y Reforzamiento Sísmico (Build Change/Swisscontact, "
            "2015). Método del Porcentaje de Área de Muros (PAM) — el criterio central "
            "para decidir si una vivienda de mampostería necesita refuerzo sísmico.\n\n"
            "LÓGICA: un problema común observado en colapsos reales de vivienda de "
            "mampostería es la insuficiencia del área de muros cortantes en dirección "
            "horizontal — los muros existentes fallan por esfuerzos laterales excesivos, "
            "generando colapso parcial o total de ese nivel. El método evalúa, en cada "
            "nivel y en cada dirección por separado, si el área de muros disponible es "
            "suficiente para el tipo de construcción (mampostería no reforzada o "
            "confinada). Si la densidad de muros es MENOR a la requerida, la edificación "
            "necesita reforzarse.\n\n"
            "FÓRMULA DEL PAM REQUERIDO:\n"
            "  PAM_requerido = bPAM_requerido × CB × CQ × CR × CP × CW × (1/R)\n"
            "  ≥ 8% para Mampostería No Reforzada (MNR)\n"
            "  ≥ 4% para Mampostería Confinada (MC)\n\n"
            "donde cada factor C ajusta el requerimiento base según las condiciones "
            "reales de la vivienda:\n\n"
            "CB — Factor de Resistencia del Bloque (rango 0.40 a 1.13): ante ausencia de "
            "pruebas de laboratorio, se puede asumir conservadoramente f'cu = 2.0 MPa "
            "para bloque 4/5 (CB=1.0 para esa resistencia). Para bloque de mayor "
            "resistencia, CB baja (ej. CB=0.40 para f'cu > 15 MPa) — bloques más "
            "resistentes permiten menos área de muro relativa. Fórmulas: para bloque "
            "4/5, CB = 1.05/√(0.195+0.45·f'cu); para tolete (ladrillo sólido), "
            "CB = 1.05/√(0.62+0.35·f'cu).\n\n"
            "CQ — Factor de Calidad de Obra (rango 1.0 a 1.70): CQ=1.0 para calidad "
            "común; CQ=1.35 para mala calidad (juntas con relleno incompleto, hiladas "
            "superiores sin contacto con la losa); CQ=1.70 si la MAYORÍA de las juntas "
            "verticales no tienen mortero (indicio grave de mano de obra deficiente, muy "
            "común en autoconstrucción sin supervisión técnica). Se pueden usar valores "
            "intermedios según la severidad observada.\n\n"
            "CR — Factor de Vulnerabilidad para el Análisis: 0.75 al evaluar la "
            "vulnerabilidad existente (nivel de seguridad limitada, análogo al "
            "coeficiente A.10.3-2 de la NSR-10 para rehabilitación), 1.00 al validar un "
            "esquema de reforzamiento propuesto (debe cumplir el mismo estándar que una "
            "edificación nueva).\n\n"
            "CP — Factor de Piso (rango 0.39 a 1.00): diferencia la demanda sísmica por "
            "nivel — el primer piso de un edificio de 3 niveles con cubierta pesada tiene "
            "CP=0.79, mientras el nivel 3 (más alto) tiene CP=0.39; con cubierta liviana "
            "los valores son aún menores (0.61 y 0.14 respectivamente) porque hay menos "
            "masa sísmica que resistir en los niveles superiores.\n\n"
            "CW — Factor de Peso Sísmico (rango 1.00 a 2.03): ajusta por el peso adicional "
            "que añaden los revoques y recubrimientos de refuerzo — desde 1.00 (sin "
            "revoque) hasta 2.03 (recubrimiento de concreto reforzado en más del 50% de "
            "los muros, en tolete).\n\n"
            "R — Factor de Reducción de la fuerza sísmica (1.0 a 2.0): 1 para "
            "mampostería no reforzada, 2 para mampostería confinada — la confinación "
            "duplica la capacidad de disipación de energía reconocida por el método.\n\n"
            "FÓRMULA DEL ÁREA EFECTIVA DE MUROS DESPUÉS DE REFORZAR:\n"
            "  PAM_efectiva = PAM_actual + PAM_reforzado\n"
            "  PAM_actual = A_muros_existentes / A_b\n"
            "  PAM_reforzado = 0.095 × (ΣKm·Lm + ΣKp·Lp + ΣKc·Lc) / A_b\n"
            "donde A_b es el área en planta del nivel, y Km/Kp/Kc son los factores de "
            "equivalencia de las técnicas de refuerzo aplicadas (ver chunk de técnicas de "
            "reforzamiento). Se calcula el PAM_efectivo en cada dirección primaria y se "
            "compara contra el PAM_requerido — si PAM_efectiva ≥ PAM_requerido en ambas "
            "direcciones, la vivienda queda adecuadamente reforzada."
        ),
    },
    {
        "id": "BUILDCHANGE-2015-tecnicas_reforzamiento",
        "seccion": "Técnicas de reforzamiento y factores K",
        "titulo": (
            "Catalogo de tecnicas de refuerzo con factores de equivalencia cuantitativos: "
            "muros nuevos (Km hasta 6.0 segun resistencia relativa), pañete reforzado "
            "(Kp=1.0-2.0, 1.5-3.0cm), recubrimiento de concreto reforzado (Kc=4, 6cm de "
            "espesor). Cada tecnica se traduce a 'cuanto muro existente equivale' para "
            "sumar directamente en la formula de PAM efectivo. Incluye tambien la "
            "confirmacion explicita de aplicabilidad nacional del metodo (Anexo D)."
        ),
        "texto": (
            "Manual de Evaluación y Reforzamiento Sísmico (Build Change/Swisscontact, "
            "2015). Técnicas de reforzamiento y sus factores de equivalencia K.\n\n"
            "OPCIONES GENERALES para incrementar el Porcentaje de Área de Muros (PAM): "
            "(1) reconvertir mampostería no reforzada a confinada agregando los detalles "
            "de confinamiento requeridos; (2) agregar nuevos muros de mampostería; "
            "(3) redoblar el espesor de muros existentes; (4) rellenar vanos de puertas y "
            "ventanas; (5) agregar un recubrimiento de pañete de concreto (3.0 cm total, "
            "1.5 cm por lado o 1.5 cm por una sola cara); (6) agregar un recubrimiento "
            "nuevo de concreto reforzado de 6.0 cm de espesor. Técnicas que en cambio "
            "REDUCEN el porcentaje necesario: introducir elementos confinantes de "
            "concreto reforzado (más ductilidad), mejorar la calidad de la mampostería, "
            "suprimir un piso superior, o convertir una cubierta pesada de concreto en "
            "una cubierta liviana.\n\n"
            "FACTOR Km — Muros nuevos de mampostería: el bloque nuevo suele ser más "
            "resistente que el existente, así que se le da un incremento en su "
            "contribución. Ejemplos tabulados (bloque nuevo vs. resistencia del bloque "
            "existente en MPa): con bloque portante nuevo (>15 MPa) sobre mampostería "
            "existente débil (f'cu=1.5 MPa), Km=6.0 — es decir, 1 metro de muro nuevo "
            "equivale a 6 metros de muro existente. El factor baja a medida que el bloque "
            "existente ya es de buena calidad (Km=2.0 cuando el existente ya tiene "
            "f'cu=15 MPa). Para relleno de vanos con el MISMO material que el existente, "
            "Km=1.0 siempre (no hay ganancia relativa).\n\n"
            "FACTOR Kp — Pañete nuevo (revoque estructural): Kp=1.0 con 1.5 cm de "
            "revoque a un solo lado del muro; Kp=2.0 con 1.5 cm a cada lado (3.0 cm "
            "total). Agregar pañete con Kp=1 equivale a agregar 1 vez la longitud del "
            "muro existente (duplica su longitud efectiva); con Kp=2, la longitud "
            "efectiva se TRIPLICA (3L = L + 2×L). IMPORTANTE: estos factores NO aplican "
            "si el bloque existente ya supera f'cu = 3.0 MPa — agregar pañete a un muro "
            "ya resistente no mejora significativamente su capacidad lateral.\n\n"
            "FACTOR Kc — Recubrimiento de concreto reforzado nuevo: Kc=4 al agregar 6.0 "
            "cm de recubrimiento de concreto reforzado a una sola cara de un muro de 9 "
            "cm — la longitud efectiva del muro se QUINTUPLICA (5L = L + 4×L). Es la "
            "técnica de mayor ganancia de resistencia por unidad de longitud "
            "intervenida, pero también la más costosa. Misma limitación que Kp: no "
            "aplica sobre bloque existente con f'cu > 3.0 MPa.\n\n"
            "PRIORIZACIÓN Y COSTO (nota práctica del manual, relevante para vivienda de "
            "bajos recursos): rellenar una puerta o ventana, o demoler un piso superior, "
            "tienden a ser las soluciones más económicas aunque menos atractivas "
            "estéticamente para el propietario; agregar muros nuevos o elementos "
            "confinantes es más atractivo pero más caro. El manual explícitamente "
            "recomienda discutir estas opciones con el propietario — el reforzamiento "
            "estructural de vivienda de bajos recursos es, en la práctica, una decisión "
            "que combina ingeniería con la realidad económica de cada familia, no solo un "
            "cálculo técnico.\n\n"
            "APLICABILIDAD NACIONAL (Anexo D del manual, \"Uso del manual en Colombia, "
            "fuera de Bogotá\", citado casi textualmente por ser la respuesta directa a "
            "si este método sirve para todo el país): \"el enfoque y la metodología son "
            "aplicables a Colombia en general\". Para usarlo fuera de Bogotá el "
            "ingeniero debe: (1) verificar que la estructura esté dentro de los "
            "parámetros de aplicabilidad (vivienda informal, mampostería, hasta 3 "
            "pisos); (2) usar el sistema de identificación catastral aplicable "
            "localmente (CHIP es específico de Bogotá — en otros municipios se usa otro "
            "identificador); (3) verificar con las autoridades locales los requisitos de "
            "planos para radicar la licencia; (4) para licuefacción, referirse a la "
            "cartografía y normativa local disponible en cada municipio; (5) para "
            "aceleraciones de diseño Sa, usar el Capítulo A.2 de la NSR-10 (nacional) o "
            "la microzonificación sísmica local vigente donde exista (Bogotá, Medellín y "
            "otras ciudades grandes tienen la suya propia) — el manual da una tabla "
            "general de Sa por Aa y tipo de perfil de suelo (A a F) basada directamente "
            "en el Capítulo A.2 de la NSR-10, utilizable en cualquier municipio del país "
            "sin necesidad de microzonificación local."
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
    print(f"OK: {len(rows)} chunks Build Change 2015 cargados con embedding.")


if __name__ == "__main__":
    main()
