"""
Batch 1 de reauditoria Titulo F (NSR-10, Estructuras Metalicas): inserta
chunks verbatim reales para F.2.4 (Diseno de miembros a tension) y F.2.5
(Diseno de miembros a compresion), corrigiendo la estructura equivocada de
los chunks sinteticos obsoletos E-SEC4-FORM1/E-SEC5-* que trataban "F.4" y
"F.5" como capitulos independientes -- en la NSR-10 real, TODO esto vive
anidado dentro del capitulo unico F.2 (F.2.1 a F.2.20+), como numerales
F.2.4 y F.2.5.

Fuente: extraccion via Google Drive de NSR-10-712-742.pdf (paginas internas
F-31 a F-61), carpeta Drive NSR10 (id 1D7-UD-r543j4hUMiegPQ4fDwialfqiEB),
drive_file_id 14t3dnpSmcqmLHvC-Qn5NOsQYmHlV99SB, verificado contra
nsr10_catalogo_maestro.json.

Uso: python _ingest_titulo_f_batch1.py
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
        "id": "NSR10-F-F_2_4",
        "seccion": "F.2.4",
        "titulo": (
            "Diseno de miembros a tension: resistencia de diseno phi_t*Pn (fluencia sobre "
            "area bruta y rotura sobre area neta efectiva), area neta efectiva Ae=An*U con "
            "tabla de factores de rezago de cortante U, miembros armados, miembros conectados "
            "con pasadores, barras de ojo. CORRIGE la numeracion del chunk obsoleto "
            "E-SEC4-FORM1 que trataba esto como capitulo independiente \"F.4\" (en realidad "
            "es el numeral F.2.4 dentro del capitulo unico F.2)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero con perfiles laminados, "
            "armados y tubulares estructurales. F.2.4 — Diseño de miembros a tensión.\n\n"
            "Se aplica a miembros solicitados por tensión axial causada por fuerzas estáticas "
            "que actúan a lo largo del eje centroidal. Incluye: F.2.4.1 Límites de esbeltez, "
            "F.2.4.2 Resistencia de diseño a tensión, F.2.4.3 Área neta efectiva, F.2.4.4 "
            "Miembros armados, F.2.4.5 Miembros conectados con pasadores, F.2.4.6 Barras de "
            "ojo. Para fatiga ver F.2.2.3.10; para tensión+flexión combinadas ver F.2.8; para "
            "barras roscadas ver F.2.10.3; para desgarramiento en bloque ver F.2.10.4.3.\n\n"
            "F.2.4.1 Límites de esbeltez: no hay límite máximo de esbeltez para miembros a "
            "tensión. Se recomienda (no obligatorio) que la relación de esbeltez no exceda "
            "300, salvo varillas o pendolones a tensión.\n\n"
            "F.2.4.2 Resistencia de diseño a tensión: phi_t*Pn es el MENOR entre:\n"
            "  (a) Fluencia por tensión sobre área bruta: Pn = Fy*Ag, phi_t = 0.90 "
            "(ecuación F.2.4.2-1)\n"
            "  (b) Rotura por tensión sobre área neta: Pn = Fu*Ae, phi_t = 0.75 "
            "(ecuación F.2.4.2-2)\n"
            "donde Ae = área neta efectiva, Ag = área bruta, Fy = esfuerzo de fluencia "
            "mínimo especificado, Fu = resistencia a tensión mínima especificada.\n\n"
            "F.2.4.3 Área neta efectiva: Ae = An*U (ecuación F.2.4.3-1), donde U es el factor "
            "de reducción por rezago de cortante (tabla F.2.4.3-1, 8 casos según tipo de "
            "conexión: U=1.0 cuando la carga se transmite a todos los elementos de la sección "
            "por pernos/soldaduras; U=1-x/l cuando se transmite solo a algunos elementos; "
            "valores específicos de 0.60 a 1.0 según número de pernos por línea y geometría "
            "para perfiles W/M/S/HP y ángulos simples). Para secciones abiertas (W, M, S, C, "
            "HP, WT, ST, ángulos), U no necesita ser menor que la relación entre el área bruta "
            "de los elementos conectados y el área bruta total (no aplica a PTE ni platinas). "
            "Para platinas de empalme con perforaciones, An está limitado a 0.85*Ag.\n\n"
            "F.2.4.4 Miembros armados: el espaciamiento longitudinal de conectores entre "
            "elementos en contacto continuo debe cumplir F.2.10.3.5. Presillas sin diagonales "
            "en caras abiertas: longitud >= 2/3 de la distancia entre líneas de conexión, "
            "espesor >= 1/50 de esa distancia, espaciamiento longitudinal de conectores en "
            "presillas <= 150 mm. Esbeltez de cualquier componente entre conectores "
            "preferiblemente <= 300.\n\n"
            "F.2.4.5 Miembros conectados con pasadores: la resistencia de diseño phi_t*Pn es "
            "el menor entre rotura por tensión sobre área neta efectiva (Pn = 2*t*be*Fu, "
            "phi_t=0.75, ecuación F.2.4.5-1), rotura por cortante sobre área efectiva "
            "(Pn = 0.60*Fu*Asf, phi_sf=0.75, ecuación F.2.4.5-2, con Asf = 2t(a+d/2)), "
            "aplastamiento (ver F.2.10.7), y fluencia sobre sección total (ver F.2.4.2a). "
            "Requisitos dimensionales: el ancho de la platina en el agujero del pasador debe "
            "ser >= 2be+d y extenderse una longitud 'a' >= 1.33*be más allá del agujero.\n\n"
            "F.2.4.6 Barras de ojo: la resistencia se determina con F.2.4.2 usando Ag = área "
            "de la sección transversal del cuerpo; el ancho del cuerpo no se toma mayor que "
            "8 veces su espesor. El diámetro del pasador no debe ser menor que 7/8 del ancho "
            "del cuerpo; para Fy > 485 MPa el diámetro del agujero no debe exceder 5 veces el "
            "espesor de la platina."
        ),
    },
    {
        "id": "NSR10-F-F_2_5a",
        "seccion": "F.2.5.1 a F.2.5.3",
        "titulo": (
            "Diseno de miembros a compresion (caso general, pandeo por flexion): resistencia "
            "phi_c*Pn=0.90*Pn, longitud efectiva K, esfuerzo critico Fcr segun KL/r respecto "
            "al limite 4.71*raiz(E/Fy). Es el caso mas usado en la practica (columnas sin "
            "elementos esbeltos). CORRIGE la numeracion de los chunks obsoletos E-SEC5-IMG1/"
            "E-SEC5-FORM1 que trataban esto como capitulo independiente \"F.5\" (en realidad "
            "es el numeral F.2.5 dentro del capitulo unico F.2)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.5 — Diseño de miembros "
            "a compresión (F.2.5.1 a F.2.5.3: provisiones generales, longitud efectiva, pandeo "
            "por flexión — caso estándar sin elementos esbeltos).\n\n"
            "Se aplica a miembros solicitados por compresión axial a través del eje centroidal. "
            "Incluye: F.2.5.1 Provisiones generales, F.2.5.2 Longitud efectiva, F.2.5.3 Pandeo "
            "por flexión (sin elementos esbeltos), F.2.5.4 Pandeo por torsión y flexo-torsión "
            "(sin elementos esbeltos), F.2.5.5 Ángulo sencillo, F.2.5.6 Miembros armados, "
            "F.2.5.7 Elementos esbeltos. Para compresión+flexión combinadas ver F.2.8.1-8.3; "
            "compresión+torsión ver F.2.8.4; secciones compuestas ver F.2.9.2.\n\n"
            "F.2.5.1 Provisiones generales: la resistencia de diseño a compresión es "
            "phi_c*Pn, con phi_c = 0.90. Pn (resistencia nominal) es el MENOR valor entre los "
            "estados límite de pandeo por flexión (PF), pandeo por torsión (PT) y pandeo por "
            "flexo-torsión (PFT). La tabla F.2.5.1-1 guía qué numeral aplicar según el tipo de "
            "sección transversal y si tiene o no elementos esbeltos.\n\n"
            "F.2.5.2 Longitud efectiva: el factor K para la esbeltez de columna KL/r se "
            "determina con F.2.3 o F.2.21. La relación de esbeltez KL/r para miembros a "
            "compresión preferiblemente no debe exceder 200.\n\n"
            "F.2.5.3 Pandeo por flexión de miembros SIN elementos esbeltos (el caso más común "
            "en columnas de perfiles W/HP/tubulares no esbeltos):\n"
            "Pn = Fcr*Ag  (ecuación F.2.5.3-1)\n"
            "El esfuerzo de pandeo por flexión Fcr se calcula:\n"
            "  (a) Cuando KL/r <= 4.71*raiz(E/Fy) [equivalente a Fe >= 0.44*Fy]:\n"
            "      Fcr = [0.658^(Fy/Fe)] * Fy  (ecuación F.2.5.3-2)\n"
            "  (b) Cuando KL/r > 4.71*raiz(E/Fy) [equivalente a Fe < 0.44*Fy]:\n"
            "      Fcr = 0.877*Fe  (ecuación F.2.5.3-3)\n"
            "donde Fe = esfuerzo crítico de pandeo elástico:\n"
            "  Fe = pi^2*E / (KL/r)^2  (ecuación F.2.5.3-4)\n"
            "Ambas fórmulas de límite (basada en KL/r y basada en Fe) producen el mismo "
            "resultado — son formas equivalentes del mismo criterio. Este es el criterio de "
            "diseño a compresión de uso más frecuente en la práctica (columnas típicas de "
            "perfiles laminados no esbeltos, sin simetría simple ni secciones en cruz)."
        ),
    },
    {
        "id": "NSR10-F-F_2_5b",
        "seccion": "F.2.5.4 a F.2.5.7",
        "titulo": (
            "Compresion, casos especiales: pandeo por torsion/flexo-torsion (perfiles en T, "
            "angulos dobles, secciones asimetricas), miembros en angulo sencillo (formulas de "
            "esbeltez efectiva para diagonales de armaduras), miembros armados (esbeltez "
            "modificada KL/r_m), elementos con placas esbeltas (factores de reduccion Qs/Qa)."
        ),
        "texto": (
            "NSR-10 Título F, Capítulo F.2 — Estructuras de acero. F.2.5 — Diseño de miembros "
            "a compresión (F.2.5.4 a F.2.5.7: casos especiales).\n\n"
            "F.2.5.4 Pandeo por torsión y pandeo por flexo-torsión (miembros de simetría "
            "simple, no simétricos, y algunos de simetría doble como perfiles en cruz o "
            "columnas armadas, sin elementos esbeltos; para ángulos sencillos aplica cuando "
            "b/t > 20): Pn = Fcr*Ag (ecuación F.2.5.4-1). Para ángulos dobles en T con "
            "constante de alabeo Cw despreciable y secciones en T, Fcr se calcula con la "
            "ecuación F.2.5.4-2 combinando Fcry (pandeo flexión eje y) y Fcrz (pandeo "
            "torsional puro, ecuación F.2.5.4-3: Fcrz = G*J/(Ag*ro^2)). Para los demás casos, "
            "Fcr se determina con F.2.5.3-2/-3 usando el esfuerzo elástico Fe apropiado: "
            "ecuación F.2.5.4-4 para miembros de simetría doble, F.2.5.4-5 para simetría "
            "simple, y la ecuación cúbica F.2.5.4-6 para miembros no simétricos (la menor "
            "raíz). La tabla F.2.5.4-1 guía qué fórmula aplicar según el tipo de sección. "
            "G (módulo de elasticidad a cortante del acero) = 77200 MPa.\n\n"
            "F.2.5.5 Miembros en ángulo sencillo a compresión: se evalúan con F.2.5.3 o "
            "F.2.5.7 (F.2.5.4 adicional si b/t > 20). Se permite despreciar la excentricidad "
            "de carga (tratar como carga axial) si: (1) la fuerza se aplica por la misma aleta "
            "en ambos extremos, (2) conexión soldada o con al menos 2 pernos por extremo, (3) "
            "sin cargas transversales intermedias — usando una esbeltez efectiva KL/r "
            "calculada según fórmulas específicas (F.2.5.5-1 a -4) que dependen de si el "
            "ángulo es miembro individual/diagonal de armadura plana (L/rx <= 80: "
            "KL/r = 72 + 0.75*L/rx; L/rx > 80: KL/r = 32 + 1.25*L/rx) o diagonal de armadura "
            "en cajón/espacial (L/rx <= 75: KL/r = 60 + 0.8*L/rx; L/rx > 75: "
            "KL/r = 45 + L/rx), con incrementos adicionales para aletas desiguales conectadas "
            "por la aleta menor.\n\n"
            "F.2.5.6 Miembros armados (dos o más perfiles conectados por pernos/soldaduras, "
            "con al menos un lado abierto conectado por cubreplacas perforadas o celosía con "
            "presillas): se calcula igual que F.2.5.3/F.2.5.4/F.2.5.7 pero reemplazando KL/r "
            "por una esbeltez modificada (KL/r)m que depende del tipo de conector (fórmulas "
            "F.2.5.6-1 para pernos de apriete ajustado, F.2.5.6-2 para soldados o pernos "
            "pretensionados, F.2.5.6-3 para ángulos dobles distanciados soldados). Requisitos "
            "dimensionales detallados para espaciamiento de conectores, cubreplacas perforadas "
            "(relación longitud/ancho de agujero <= 2.0, radio mínimo de esquina 38 mm) y "
            "celosía (resistencia a cortante normal >= 2% de la resistencia de diseño a "
            "compresión, inclinación >= 60° en celosía sencilla o >= 45° en doble).\n\n"
            "F.2.5.7 Miembros con elementos esbeltos: Pn = Fcr*Ag (ecuación F.2.5.7-1), con "
            "Fcr calculado igual que F.2.5.3 pero sustituyendo Fy por Q*Fy en los umbrales "
            "(ecuaciones F.2.5.7-2/-3), donde Q = Qs*Qa es el factor de reducción total "
            "(Q=1.0 para secciones no esbeltas). F.2.5.7.1 define Qs (elementos no atiesados "
            "esbeltos: aletas de perfiles laminados o armados, ángulos, almas de T) mediante "
            "fórmulas escalonadas en 3 rangos de b/t respecto a límites en función de "
            "raíz(E/Fy). F.2.5.7.2 define Qa (elementos atiesados esbeltos) como "
            "Qa = Ae/A (ecuación F.2.5.7-16), donde Ae usa anchos efectivos reducidos be "
            "calculados con las ecuaciones F.2.5.7-17/-18/-19 según el tipo de elemento "
            "(general, aletas de secciones cuadradas/rectangulares, o secciones circulares)."
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
    print(f"OK: {len(rows)} chunks F.2.4/F.2.5 cargados con embedding.")


if __name__ == "__main__":
    main()
