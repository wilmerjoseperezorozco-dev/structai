"""
NSR-10 Titulo A, Capitulo A.9 -- Elementos no estructurales. Gap corregido
2026-08-20: los 10 chunks obsoletos con prefijo "J-SEC" (ids J-SEC1-001,
J-SEC2-TAB1, J-SEC4-FORM1, J-SEC4-TAB1/2, J-SEC5-TAB1, J-SEC7-TAB1,
J-SEC8-TAB1, J-SEC9-TAB1, J-SEC12-TAB1/FORM1) usaban seccion "ENE.x"
(Elementos No Estructurales) y su propio capitulo ya reconocia "probablemente
Titulo A.9, sin confirmar contra indice oficial" -- confirmado contra el
catalogo maestro verificado pagina por pagina: es A.9 real (A-87 a A-95),
no Titulo J (que es Proteccion contra Incendios).

Fuente: NSR-10-130-138.pdf (Drive, id 1-aUdCX_gFVIuooVNKrxu3xYB0WUlwo4p),
capitulo completo A-87 a A-95, sin recortes.

Uso: python _ingest_a9_elementos_no_estructurales.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título A — Requisitos generales de diseño y construcción sismo resistente"

CHUNKS = [
    {
        "id": "NSR10-A-A_9_general_fuerzas",
        "seccion": "A.9.1 a A.9.4",
        "titulo": (
            "Elementos no estructurales: 3 grados de desempeno (Superior/Bueno/Bajo) "
            "minimos por grupo de uso, formula de fuerza sismica de diseno "
            "Fp=(ax*ap/Rp)*g*Mp, y los 4 tipos de anclaje segun Rp permitido (Especiales "
            "Rp=6, Dúctiles Rp=6, No dúctiles Rp=1.5, Húmedos Rp=0.5 -- estos ultimos sin "
            "anclaje mecanico resistente a traccion, NO permitidos para elementos "
            "criticos)."
        ),
        "texto": (
            "NSR-10 Título A, Capítulo A.9 — Elementos no estructurales. A.9.1 a A.9.4 — "
            "Alcance, grados de desempeño, responsabilidades y criterio de diseño.\n\n"
            "A.9.1.2 Alcance: cubre acabados/elementos arquitectónicos y decorativos, "
            "instalaciones hidráulicas/sanitarias/eléctricas/de gas, equipos mecánicos, "
            "estanterías, e instalaciones especiales — y sus anclajes a la estructura. "
            "EXENTAS: edificaciones de grupos de uso I y II en zona de amenaza sísmica "
            "BAJA (A.9.1.3).\n\n"
            "A.9.2 Grados de desempeño de elementos no estructurales ante el sismo de "
            "diseño: Superior (daño mínimo, no interfiere la operación), Bueno (daño "
            "totalmente reparable, puede haber interferencia temporal), Bajo (daños "
            "graves, incluso no reparables, pero SIN desprendimiento ni colapso). "
            "Mínimo requerido por grupo de uso (Tabla A.9.2-1): Grupo IV → Superior; "
            "Grupo III → Superior; Grupo II → Bueno; Grupo I → Bajo. El propietario puede "
            "exigir voluntariamente un grado mejor, comunicándolo por escrito.\n\n"
            "A.9.3 Responsabilidades: el diseñador responsable de cada sistema (no "
            "necesariamente el ingeniero estructural) firma el diseño sísmico de sus "
            "elementos no estructurales; el supervisor técnico verifica cumplimiento; el "
            "profesional que figura como diseñador arquitectónico en la licencia coordina "
            "entre los diferentes diseños para que no se afecten entre sí.\n\n"
            "A.9.4.1 Dos estrategias de diseño: (a) SEPARAR el elemento de la estructura "
            "(deja holgura suficiente para que la deformación sísmica no lo afecte; el "
            "elemento resiste sus propias fuerzas inerciales); (b) DISPONER elementos que "
            "admitan las deformaciones de la estructura (deben ser flexibles y tolerar la "
            "deriva sin daño mayor al grado de desempeño fijado).\n\n"
            "A.9.4.2 Fuerza sísmica horizontal reducida de diseño (ecuación A.9.4-1):\n"
            "  Fp = (ax*ap/Rp) * g * Mp  >=  0.2*Aa*I*g*Mp\n"
            "donde ax = aceleración horizontal en el punto de soporte del elemento "
            "(calculada según A.9.4.2.2, o simplificada con heq = 0.75*hn), ap = "
            "coeficiente de amplificación dinámica del elemento (1.0 a 2.5, según Tablas "
            "A.9.5-1/A.9.6-1 — elementos rígidos con período <=0.06s amplifican menos), "
            "Rp = coeficiente de capacidad de disipación de energía del elemento y su "
            "sistema de anclaje (0.5 a 6.0), Mp = masa del elemento, g = 9.8 m/s².\n\n"
            "A.9.4.9 Tipos de anclaje según el Rp permitido: \n"
            "  Rp=6, Especiales — anclajes diseñados según Título F para acero DES.\n"
            "  Rp=6, Dúctiles — anclajes profundos con epóxico o vaciados en sitio "
            "(relación embebido/diámetro > 8); cumplen C.21. NO se permiten pernos de "
            "expansión ni anclajes por explosivo (tiros).\n"
            "  Rp=1.5, No dúctiles — pernos de expansión, anclajes superficiales "
            "(relación embebido/diámetro < 8), incluyendo barras con gancho embebidas en "
            "mortero de mampostería. Se permiten en elementos no dúctiles; si se usan en "
            "elementos dúctiles, deben diseñarse igual con Rp=1.5.\n"
            "  Rp=0.5, Húmedos — mortero o adhesivos pegados directamente sin ningún "
            "anclaje mecánico resistente a tracción — el nivel más débil, apto solo "
            "cuando la tabla lo permite explícitamente (p.ej. muros divisorios).\n\n"
            "A.9.4.10 Elementos de conexión en fachadas: la conexión debe diseñarse para "
            "1.33*Fp; todos los pernos/tornillos/soldaduras del sistema de conexión, para "
            "3.0*Fp — un factor de seguridad adicional explícito sobre la fuerza base."
        ),
    },
    {
        "id": "NSR10-A-A_9_5_a_9_6_tablas",
        "seccion": "A.9.5 a A.9.6 (Tablas A.9.5-1 y A.9.6-1)",
        "titulo": (
            "Elementos arquitectonicos criticos que requieren cuidado especial (fachadas, "
            "cielos rasos, parapetos, columnas cortas/cautivas, vidrios) y valores ap/Rp "
            "tabulados por elemento: fachadas prefabricadas ap=1.0, parapetos/aticos "
            "ap=2.5, estanterias >2.5m ap=2.5, calderas/tuberias de gas/incendio ap=2.5, "
            "equipos electricos/HVAC ap=1.0."
        ),
        "texto": (
            "NSR-10 Título A, Capítulo A.9. A.9.5 — Acabados y elementos arquitectónicos; "
            "A.9.6 — Instalaciones hidráulicas, sanitarias, mecánicas y eléctricas.\n\n"
            "A.9.5.2 Elementos que requieren especial cuidado (peligro grave para la vida "
            "o riesgo de dañar elementos estructurales críticos):\n"
            "  Muros de fachada: no deben disgregarse, deben amarrarse para que no caigan "
            "sobre transeúntes.\n"
            "  Cielos rasos y enchapes de fachada: su desprendimiento es peligro directo.\n"
            "  Áticos/parapetos/antepechos: mismo peligro que fachadas; si la cubierta es "
            "de tejas/material frágil, considerar que el parapeto falle HACIA ADENTRO "
            "sobre la cubierta.\n"
            "  Vidrios: holgura suficiente en el montaje para evitar rotura peligrosa; "
            "alternativas: películas protectoras, vidrio templado o tripliado.\n"
            "  COLUMNAS CORTAS O CAUTIVAS: cuando un muro no estructural restringe "
            "lateralmente una columna sin llegar hasta la losa superior — debe evitarse "
            "SIEMPRE (separar el muro de la columna, o llevarlo hasta la losa). Es una de "
            "las causas de falla frágil de columnas más documentadas en sismos reales.\n\n"
            "Tabla A.9.5-1 — valores representativos de ap y tipo de anclaje mínimo "
            "(Superior/Bueno/Bajo):\n"
            "  Fachadas prefabricadas (paneles o vidrio, apoyadas arriba y abajo): "
            "ap=1.0; Dúctiles/No dúctiles/No dúctiles\n"
            "  Fachadas de mampostería reforzada, apoyadas solo abajo: ap=2.5\n"
            "  Mampostería NO reforzada de fachada, apoyada solo abajo: NO se permite "
            "para desempeño Superior/Bueno; solo Bajo con anclaje No dúctil\n"
            "  Muros divisorios de altura parcial: ap=2.5, Húmedos permitido en Bajo\n"
            "  Áticos, parapetos y chimeneas (voladizo vertical): ap=2.5\n"
            "  Estanterías/anaqueles/bibliotecas >2.50 m de altura (incluido contenido): "
            "ap=2.5; si se diseñan según Título F, Especiales/Dúctiles; si no, "
            "Dúctiles/No dúctiles\n"
            "  Cielos rasos: ap=1.0, No dúctiles en ambos grados exigibles\n\n"
            "Tabla A.9.6-1 — instalaciones (ap y anclaje mínimo):\n"
            "  Sistemas de protección contra el fuego: ap=2.5, Dúctiles/No dúctiles\n"
            "  Tuberías de gases y combustibles, tuberías de sistema contra incendio: "
            "ap=2.5, Dúctiles\n"
            "  Equipo eléctrico/mecánico general (calderas, transformadores, bombas, "
            "tanques), sistemas de aire acondicionado/ventilación: ap=1.0, Dúctiles\n"
            "  Luminarias tipo péndulo: ap=1.5 específicamente, soporte vertical con "
            "factor de seguridad 4.0\n"
            "  Exenciones sin soporte sísmico requerido: ductos/tuberías colgados de "
            "soportes individuales de <=300 mm de longitud, tuberías <65 mm de diámetro "
            "interior fuera de cuartos de máquinas, ductos HVAC con sección <0.60 m².\n\n"
            "A.9.6.5 Interruptores automáticos: obligatorios en empates de electricidad/"
            "gas de edificaciones Grupo de uso IV en zona sísmica intermedia y alta, "
            "activados con aceleración horizontal del terreno > 0.5*Aa.\n\n"
            "A.9.6.6 Ascensores en Grupo de uso IV en zona sísmica alta: deben cumplir "
            "ANSI/ASME A17.1 (incluyendo Apéndice F)."
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
    print(f"OK: {len(rows)} chunks A.9 cargados con embedding.")


if __name__ == "__main__":
    main()
