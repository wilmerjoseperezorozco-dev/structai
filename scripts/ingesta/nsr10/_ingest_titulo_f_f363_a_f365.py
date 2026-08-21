"""
NSR-10 Titulo F, F.3.6.3 a F.3.6.5 -- los 3 sistemas sismicos de acero que
faltaban tras PAC (F.3.6.1/F.3.6.2, ya cargado): Porticos Arriostrados
Excentricamente (PAE), Porticos con Arriostramientos de Pandeo Restringido
(PAPR) y Muros de Cortante de Acero (MCA). Cierra F.3.6 completo.

Fuente: NSR-10-901-980.pdf (Drive, id 14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm),
extraido en bruto localmente en F_901_980_raw.txt (paginas internas F-254 a
F-268). Un chunk por sistema (single-topic, patron establecido en la sesion
para mejorar retrieval).

Uso: python _ingest_titulo_f_f363_a_f365.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_3_6_3_PAE",
        "seccion": "F.3.6.3 (Pórticos Arriostrados Excéntricamente)",
        "titulo": (
            "Porticos Arriostrados Excentricamente (PAE): la riostra NO llega "
            "directo al nudo viga-columna, deja un tramo corto de viga (el "
            "'vinculo') que se disena para fluir por cortante ANTES que la "
            "riostra o la columna fallen. Formulas de resistencia a cortante "
            "del vinculo (fluencia por cortante Vp y por flexion Mp), limites "
            "de longitud del vinculo, rigidizadores de alma, y validacion de "
            "conexion vinculo-columna por ensayos ciclicos."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "F.3.6.3 — Pórticos Arriostrados Excéntricamente (PAE).\n\n"
            "F.3.6.3.2 Bases de diseño: un extremo de cada riostra intercepta "
            "la viga con una EXCENTRICIDAD respecto al eje de la riostra "
            "adyacente o la columna, formando un segmento corto de viga — el "
            "'vínculo' (link) — sometido a cortante y flexión. El vínculo es "
            "el elemento diseñado para fluir primero: se espera que el PAE "
            "garantice capacidad de deformación inelástica significativa a "
            "través de la fluencia a CORTANTE de los vínculos — no de las "
            "riostras (a diferencia de PAC) ni de las columnas.\n\n"
            "F.3.6.3.3 Análisis (diseño por capacidad): la carga sísmica "
            "amplificada Emh se calcula suponiendo que las fuerzas en los "
            "extremos del vínculo corresponden a su resistencia a cortante "
            "AJUSTADA — Ry veces la resistencia nominal Vn, multiplicada por "
            "1.25 (vínculos sección I) o 1.4 (sección cajón). Excepción: para "
            "vigas fuera del vínculo y columnas en edificios de 3+ pisos, Emh "
            "puede tomarse como 0.88 veces ese valor.\n\n"
            "F.3.6.3.4.1 Ángulo de rotación del vínculo (ductilidad "
            "controlada por longitud): no debe exceder 0.08 radianes si el "
            "vínculo mide <=1.6*Mp/Vp (vínculo corto, domina cortante — más "
            "dúctil); 0.02 radianes si mide >=2.6*Mp/Vp (vínculo largo, "
            "domina flexión — menos dúctil); interpolación lineal entre "
            "ambos. Esta es la lógica central de PAE: vínculos cortos = más "
            "ductilidad permitida.\n\n"
            "F.3.6.3.5.2 Resistencia a cortante de diseño del vínculo (phi_v="
            "0.9), el MENOR de dos estados límite:\n"
            "  Fluencia por cortante: Vn = Vp, donde Vp = 0.6*Fy*Alw (si "
            "Pu/Py<=0.15) o reducido si hay carga axial alta; Alw=(d-2tf)*tw "
            "para secciones I, o 2*(d-2tf)*tw para cajón.\n"
            "  Fluencia por flexión: Vn = 2*Mp/e, donde Mp=Fy*Z (si "
            "Pu/Py<=0.15) y e = longitud libre del vínculo.\n"
            "Vínculos permitidos: solo secciones I (laminadas/armadas) o "
            "cajón armadas — NUNCA tubería estructural (PTE). Deben cumplir "
            "límites ancho-espesor de ductilidad ALTA (excepción: aletas de "
            "vínculos cortos e<=1.6*Mp/Vp pueden ser ductilidad moderada). "
            "Alma de una sola pieza — prohibidas perforaciones y placas de "
            "enchape en el alma.\n\n"
            "Límite de longitud si Pu/Py>0.15: fórmulas de interpolación "
            "según rho'=(Pu/Vu)/(Py/Vy) — a mayor carga axial, más corto debe "
            "ser el vínculo permitido.\n\n"
            "Rigidizadores de alma (F.3.6.3.5.2-4): obligatorios en ambos "
            "extremos del vínculo (secciones I) con ancho >= bf-2tw y espesor "
            ">= 0.75tw o 10mm (el mayor). Espaciamiento de rigidizadores "
            "intermedios depende de la longitud del vínculo: vínculos cortos "
            "(<=1.6Mp/Vp) necesitan rigidizadores intermedios cada "
            "(30tw-d/5) a 0.08 rad o (52tw-d/5) a 0.02 rad; vínculos largos "
            "(>5Mp/Vp) no requieren rigidizadores intermedios en absoluto.\n\n"
            "F.3.6.3.6.5 Conexiones vínculo-columna (cuando el vínculo se "
            "conecta directo a una columna): deben ser Totalmente Restringidas "
            "(TR) y VALIDARSE mediante conexión precalificada (F.3.11.2) o "
            "mínimo 2 ensayos cíclicos de calificación — la conexión vínculo-"
            "columna es de las más críticas del sistema porque concentra la "
            "rotación inelástica esperada. Excepción sin ensayos: si se "
            "refuerza la conexión viga-columna en el vínculo para excluir la "
            "fluencia de la viga en la zona reforzada, cumpliendo requisitos "
            "específicos de longitud y rigidizadores.\n\n"
            "Empalmes de columna (F.3.6.3.6.4): deben desarrollar al menos "
            "50% de la menor resistencia a flexión de los miembros "
            "conectados; resistencia requerida a cortante = ΣMpc/Hc — mismo "
            "principio de diseño por capacidad usado en PAC-DES."
        ),
    },
    {
        "id": "NSR10-F-F_3_6_4_PAPR",
        "seccion": "F.3.6.4 (Pórticos con Arriostramientos de Pandeo Restringido)",
        "titulo": (
            "Porticos con Arriostramientos de Pandeo Restringido (PAPR, o "
            "BRB en ingles): riostras con nucleo de acero + funda que "
            "restringe el pandeo, permitiendo fluencia dúctil tanto en "
            "TENSION como en COMPRESION (a diferencia de PAC, donde la "
            "riostra en compresion pandea). Factores de ajuste beta (compresion) "
            "y omega (endurecimiento por deformacion) determinados por ensayo, "
            "exige minimo 2 ensayos ciclicos de calificacion obligatorios."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "F.3.6.4 — Pórticos con Arriostramientos de Pandeo Restringido "
            "(PAPR).\n\n"
            "F.3.6.4.2 Bases de diseño: riostras de fabricación especial "
            "compuestas por un NÚCLEO de acero estructural más un SISTEMA QUE "
            "RESTRINGE EL PANDEO del núcleo (una funda/recubrimiento). A "
            "diferencia de PAC (donde la riostra en compresión pandea y solo "
            "disipa energía eficientemente en tensión), en PAPR la riostra "
            "fluye dúctilmente TANTO en tensión como en compresión — el "
            "sistema de restricción impide el pandeo. Deformaciones esperadas "
            "de diseño: correspondientes a una deriva de piso de al menos 2% "
            "de la altura de piso, o dos veces la deriva de diseño (la "
            "mayor), más la deformación por carga gravitacional.\n\n"
            "F.3.6.4.2.1 Resistencia ajustada de la riostra (se establece por "
            "ENSAYO, no por fórmula pura):\n"
            "  Compresión: beta * omega * Ry * Pysc\n"
            "  Tensión: omega * Ry * Pysc\n"
            "donde beta = factor de ajuste de resistencia a compresión "
            "(relación fuerza máxima a compresión / fuerza máxima a tensión "
            "medida en ensayo de calificación — nunca menor que 1), omega = "
            "factor de ajuste por endurecimiento por deformación (relación "
            "fuerza máxima a tensión medida / resistencia a la fluencia "
            "medida Ry*Pysc), Pysc = Fysc*Asc (resistencia axial de fluencia "
            "del núcleo de acero, Asc=área neta del núcleo, phi=0.9). Los "
            "efectos de carga con esta resistencia ajustada NO se amplifican "
            "adicionalmente por Omega0 (el factor de sobrerresistencia ya "
            "está implícito en beta/omega).\n\n"
            "F.3.6.4.3 Análisis: los PAPR NO deben considerarse sistema de "
            "resistencia a cargas gravitacionales (son puramente sísmicos). "
            "Emh se calcula suponiendo todas las riostras en su resistencia "
            "ajustada (tensión o compresión según corresponda, determinado "
            "despreciando cargas gravitacionales).\n\n"
            "F.3.6.4.4.2 Riostras en K: PROHIBIDAS en PAPR (igual que en "
            "PAC-DES).\n"
            "F.3.6.4.4.3 Conexión riostra-viga/columna fuera del plano: debe "
            "resistir una fuerza sísmica igual al 6% de la resistencia a "
            "compresión ajustada de la riostra.\n\n"
            "F.3.6.4.5.1 Vigas y columnas: ductilidad ALTA (F.3.4.1.1) — más "
            "estricto que PAC-DMI.\n\n"
            "F.3.6.4.5.2 Validación OBLIGATORIA por ensayo: el diseño de las "
            "riostras PAPR se basa en resultados de ENSAYOS CÍCLICOS DE "
            "CALIFICACIÓN (F.3.11.3) — mínimo 2 ensayos satisfactorios (uno "
            "de sistema completo con conexión, otro uniaxial o de sistema). "
            "A diferencia de PAC/PRM (donde las fórmulas de capacidad bastan), "
            "en PAPR el comportamiento del núcleo confinado depende tanto del "
            "material como del sistema de restricción, por lo que el código "
            "exige verificación empírica directa, no solo cálculo.\n\n"
            "F.3.6.4.5.3 Zona protegida: incluye el núcleo de acero completo "
            "y los elementos que lo conectan a vigas/columnas.\n\n"
            "F.3.6.4.6.3 Conexiones de riostra: resistencia requerida = 1.1 * "
            "resistencia ajustada a compresión. Diseño de cartelas de unión "
            "debe considerar pandeo local y general, replicando el "
            "arriostramiento lateral usado en los ensayos de calificación.\n\n"
            "Nota de aplicación práctica: PAPR (conocido internacionalmente "
            "como BRB — Buckling-Restrained Brace) es un sistema de "
            "fabricación especializada (patentado por varios fabricantes), "
            "poco común todavía en obra corriente colombiana pero de interés "
            "creciente para retrofit/reforzamiento de edificaciones "
            "existentes por su alta ductilidad simétrica en tensión y "
            "compresión — relevante para la línea de reforzamiento sísmico "
            "de StructAI."
        ),
    },
    {
        "id": "NSR10-F-F_3_6_5_MCA",
        "seccion": "F.3.6.5 (Muros de Cortante de Acero)",
        "titulo": (
            "Muros de Cortante de Acero (MCA-DES): laminas de acero (almas) "
            "conectadas a vigas y columnas que forman un panel a cortante, "
            "disipan energia por fluencia de la placa del alma + rotulas "
            "plasticas en Elementos de Borde Horizontales (EBH). Formula de "
            "resistencia a cortante del panel con angulo de fluencia alpha "
            "(tipicamente 40 grados), y variante con almas perforadas "
            "(reduce resistencia segun diametro/espaciamiento de huecos)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.3 — Provisiones sísmicas para acero. "
            "F.3.6.5 — Muros de Cortante de Acero (MCA).\n\n"
            "F.3.6.5.2 Bases de diseño: estructuras conformadas por LÁMINAS "
            "DE ACERO (almas) conectadas a vigas y columnas — el equivalente "
            "en acero de un muro de cortante de concreto. Disipan energía "
            "inelástica significativa mediante fluencia de la placa del alma "
            "Y formación de rótulas plásticas en los extremos de los "
            "Elementos de Borde Horizontales (EBH — las 'vigas' del sistema, "
            "análogas a las vigas de acople). Los Elementos de Borde "
            "Verticales (EBV) son las 'columnas' del sistema.\n\n"
            "F.3.6.5.3 Análisis (diseño por capacidad): las almas de los MCA "
            "NO deben considerarse resistentes a cargas de gravedad. Emh se "
            "calcula suponiendo que todas las almas resisten su resistencia "
            "esperada a TENSIÓN (Ry*Fy) actuando al ángulo alpha, y los EBH "
            "las acciones resultantes de aplicar en cada extremo momentos de "
            "1.1*Ry*Mp.\n\n"
            "F.3.6.5.4.1 Rigidez de elementos de borde: EBV deben tener "
            "momento de inercia Ic >= 0.0031*tw*h^4/L; EBH deben tener Iv >= "
            "0.0031*L^4/h veces la diferencia de espesores de placa arriba/"
            "abajo — asegura que los elementos de borde no se deformen "
            "excesivamente y permitan que el alma desarrolle su resistencia "
            "completa.\n\n"
            "F.3.6.5.5.1 EBH, EBV y elementos de borde intermedios: "
            "ductilidad ALTA (F.3.4.1.1).\n\n"
            "F.3.6.5.5.2 Resistencia a cortante del panel (phi=0.9):\n"
            "  Vn = 0.42 * Fy * tw * Lcf * sen^2(alpha)\n"
            "donde tw=espesor del alma, Lcf=distancia libre entre aletas de "
            "columna, alpha=ángulo de fluencia del alma respecto a la "
            "vertical (se puede tomar simplificadamente como 40°, o "
            "calcularse con la ecuación F.3.6.5-2 en función de la rigidez "
            "relativa de EBV y EBH).\n\n"
            "F.3.6.5.4.4 Aberturas en el alma: deben enmarcarse en todos sus "
            "lados con elementos de borde intermedios a todo lo ancho/alto "
            "del panel, salvo que se justifique otra distribución por "
            "ensayo/análisis o se use la opción de almas perforadas "
            "(F.3.6.5.7).\n\n"
            "F.3.6.5.7 Almas perforadas (alternativa de diseño arquitectónico "
            "— permite ventanas/aberturas reguladas en el muro de cortante): "
            "patrón regular de perforaciones circulares del mismo diámetro, "
            "alineadas diagonalmente. Resistencia reducida:\n"
            "  Vn = 0.42*Fy*tw*Lcf*(1 - 0.7*D/Sdiag)\n"
            "donde D=diámetro de perforación, Sdiag=distancia mínima centro a "
            "centro entre perforaciones (mínimo 1.67*D). Rigidez calculada "
            "con un espesor efectivo reducido tef (ecuación F.3.6.5-4). "
            "Esfuerzo efectivo de tensión esperado también se reduce por el "
            "mismo factor (1-0.7*D/Sdiag).\n\n"
            "F.3.6.5.6.4 Empalmes de columna: mismo principio de diseño por "
            "capacidad que PAC-DES/PAE/PAPR — desarrollar >=50% de la menor "
            "resistencia a flexión de los miembros conectados, resistencia a "
            "cortante = ΣMpc/Hc.\n\n"
            "Con esta sección se completa F.3.6 (Sistemas Arriostrados y "
            "Muros de Cortante) en su totalidad: PAC-DMI, PAC-DES, PAE, PAPR "
            "y MCA — los 5 sistemas sismo-resistentes de acero reconocidos "
            "por NSR-10 además de PRM (F.3.5)."
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
    print(f"OK: {len(rows)} chunks F.3.6.3-F.3.6.5 cargados con embedding.")


if __name__ == "__main__":
    main()
