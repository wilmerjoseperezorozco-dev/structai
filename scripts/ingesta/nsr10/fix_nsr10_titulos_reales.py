"""
Corrige un error real de etiquetado encontrado en producción el 2026-07-30:
el usuario preguntó "¿de qué trata el Título F de la NSR-10?" y el sistema
respondió que no tenía información, a pesar de tener contenido técnico real
sobre estructuras metálicas cargado bajo la letra equivocada.

Causa raíz: los PDF fuente en packages/knowledge/nsr10/ ("RAG+CAG Capitulo
X.pdf") ya traían el letrado desplazado desde origen — el archivo nombrado
"Capitulo F.pdf" describe en su propio metadata "titulo_completo":
"Estructuras de Madera", cuando el Título F real de la NSR-10 (verificado
contra fuente oficial) es "Estructuras Metálicas". El contenido semántico
de cada chunk es correcto (referencias reales a AISC 360, AISI S100,
NDS 2005, coeficientes reales); solo la letra del título estaba mal.

Este script:
  1. Reetiqueta el contenido de acero (mal puesto en "E") al Título F real.
  2. Retira la letra falsa del contenido de madera huérfano (no correspondía
     ni al Título F real ni al G, que ya tiene su propio corpus con
     numeración distinta) y del contenido de "elementos no estructurales"
     (tampoco es un título real por sí solo).
  3. Inserta un chunk de "alcance" por cada uno de los 11 títulos reales
     (A-K) de la NSR-10, con la descripción oficial de qué cubre cada uno.
     Esto resuelve el problema de fondo: preguntas tipo "¿de qué trata el
     título X?" son metapreguntas que no se parecen semánticamente a chunks
     técnicos densos en tablas/fórmulas, así que sin un chunk descriptivo
     explícito el buscador semántico no los recupera aunque existan.

Uso: python scripts/ingesta/nsr10/fix_nsr10_titulos_reales.py
Requiere SUPABASE_URL y SUPABASE_SERVICE_KEY en apps/api/.env
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "construdata"))
sys.path.insert(0, str(ROOT / "apps" / "api"))

from dotenv import load_dotenv

load_dotenv(ROOT / "apps" / "api" / ".env")

from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def relabel() -> None:
    r1 = (
        sb.table("nsr10_chunks")
        .update({"capitulo": "NSR-10 Título F — Estructuras Metálicas"})
        .eq("capitulo", "NSR-10 Título E — Estructuras Metálicas")
        .execute()
    )
    print(f"Reetiquetados E->F (acero, contenido correcto): {len(r1.data)}")

    r2 = (
        sb.table("nsr10_chunks")
        .update({"capitulo": "NSR-10 — Estructuras de Madera (contenido técnico complementario)"})
        .eq("capitulo", "NSR-10 Título F — Estructuras de Madera")
        .execute()
    )
    print(f"Reetiquetados F(madera)->sin letra falsa: {len(r2.data)}")

    r3 = (
        sb.table("nsr10_chunks")
        .update({"capitulo": "NSR-10 — Elementos No Estructurales (contenido técnico complementario)"})
        .eq("capitulo", "NSR-10 Título J — Elementos No Estructurales")
        .execute()
    )
    print(f"Reetiquetados J(elementos no estructurales)->sin letra falsa: {len(r3.data)}")

    for capitulo, prefix_old, prefix_new in [
        ("NSR-10 — Estructuras de Madera (contenido técnico complementario)", "F", "MAD"),
        ("NSR-10 — Elementos No Estructurales (contenido técnico complementario)", "J", "ENE"),
    ]:
        rows = sb.table("nsr10_chunks").select("id,seccion,titulo,texto").eq("capitulo", capitulo).execute().data
        for row in rows:
            new_seccion = row["seccion"].replace(prefix_old + ".", prefix_new + ".")
            new_titulo = (
                row["titulo"]
                .replace(f"Capítulo {prefix_old}", "(contenido complementario)")
                .replace(prefix_old + ".", prefix_new + ".")
                .replace("del (contenido complementario)", "(contenido complementario)")
            )
            new_texto = (
                row["texto"]
                .replace(f"Capítulo {prefix_old}", "(contenido complementario)")
                .replace(f"Tabla {prefix_old}.", f"Tabla {prefix_new}.")
                .replace(f"Ecuación {prefix_old}.", f"Ecuación {prefix_new}.")
                .replace(f"Figura {prefix_old}.", f"Figura {prefix_new}.")
                .replace("del (contenido complementario)", "(contenido complementario)")
            )
            sb.table("nsr10_chunks").update(
                {"seccion": new_seccion, "titulo": new_titulo, "texto": new_texto}
            ).eq("id", row["id"]).execute()
        print(f"{capitulo}: {len(rows)} filas de seccion/titulo/texto corregidas")


# Alcance real de los 11 títulos de la NSR-10, verificado contra fuente
# oficial (no supuesto). "cobertura" indica honestamente si el sistema
# tiene chunks técnicos profundos además de este resumen, o solo el resumen.
TITULOS = [
    ("A", "Requisitos Generales de Diseño y Construcción Sismo Resistente",
     "El Título A establece los principios generales y requisitos mínimos de diseño y construcción sismo resistente que aplican a prácticamente todas las edificaciones en Colombia bajo la NSR-10. Define zonas de amenaza sísmica, grupos de uso, y los requisitos generales que se complementan con los demás títulos.",
     "cobertura técnica detallada disponible en el sistema"),
    ("B", "Cargas",
     "El Título B define las cargas que deben considerarse en el diseño estructural: cargas muertas, cargas vivas, carga de granizo, y las combinaciones de carga a utilizar según el método de diseño (LRFD o esfuerzos admisibles).",
     "cobertura técnica detallada disponible en el sistema"),
    ("C", "Concreto Estructural",
     "El Título C regula el diseño y construcción de estructuras de concreto estructural (reforzado, preesforzado), adoptando como base el ACI 318 con los ajustes correspondientes a las condiciones sísmicas colombianas.",
     "cobertura técnica detallada disponible en el sistema"),
    ("D", "Mampostería Estructural",
     "El Título D regula el diseño y construcción de estructuras de mampostería estructural: mampostería confinada, reforzada y no reforzada, incluyendo sus limitaciones según la zona de amenaza sísmica.",
     "cobertura técnica detallada disponible en el sistema"),
    ("E", "Casas de Uno y Dos Pisos",
     "El Título E ofrece una metodología simplificada de diseño y construcción sismo resistente para viviendas de uno y dos pisos, permitiendo prescindir de un diseño estructural detallado por un ingeniero civil cuando se cumplen condiciones específicas de regularidad, área y materiales.",
     "resumen de alcance únicamente — sin detalle técnico profundo en este piloto"),
    ("F", "Estructuras Metálicas",
     "El Título F regula el diseño de estructuras de acero estructural, adoptando como base las especificaciones AISC 360 (perfiles laminados y armados) y AISI S100 (perfiles conformados en frío), con los ajustes sísmicos correspondientes.",
     "cobertura técnica detallada disponible en el sistema"),
    ("G", "Estructuras de Madera y Estructuras de Guadua",
     "El Título G regula el diseño y construcción de estructuras de madera y de guadua (bambú), incluyendo propiedades mecánicas de especies colombianas, factores de reducción de resistencia, uniones, y capacidad sísmica de muros de corte.",
     "cobertura técnica detallada disponible en el sistema"),
    ("H", "Estudios Geotécnicos",
     "El Título H establece los requisitos mínimos que deben cumplir los estudios geotécnicos que sirven de base al diseño estructural y de cimentaciones, incluyendo exploración del subsuelo, ensayos y el contenido mínimo del informe geotécnico.",
     "cobertura técnica detallada disponible en el sistema"),
    ("I", "Supervisión Técnica",
     "El Título I define los requisitos de supervisión técnica durante la construcción de edificaciones, estableciendo cuándo es obligatoria y las responsabilidades del supervisor técnico independientes del constructor y del diseñador.",
     "cobertura técnica detallada disponible en el sistema"),
    ("J", "Protección contra Incendios en Edificaciones",
     "El Título J establece los requisitos de protección contra incendios en edificaciones: resistencia al fuego de elementos estructurales, medios de evacuación, y sistemas de protección activa. Aplica principalmente a edificaciones de uso público, alta ocupación o considerable altura.",
     "resumen de alcance únicamente — sin detalle técnico profundo en este piloto"),
    ("K", "Otros Requisitos Complementarios",
     "El Título K reúne requisitos complementarios que no encajan en los demás títulos: urbanismo y sismo resistencia, vidrios y ventanas, y otros aspectos no estructurales relevantes para la seguridad de la edificación. Aplica principalmente a edificaciones de uso público, alta ocupación o considerable altura.",
     "resumen de alcance únicamente — sin detalle técnico profundo en este piloto"),
]


def seed_alcance() -> None:
    from rag_multi_norma import _embedding_model

    model = _embedding_model()
    for letra, nombre, descripcion, cobertura in TITULOS:
        texto = f"NSR-10 Título {letra} — {nombre}. Alcance: {descripcion} [{cobertura}]"
        emb = model.encode(texto, normalize_embeddings=True).tolist()
        row = {
            "id": f"NSR10-ALCANCE-{letra}",
            "capitulo": f"NSR-10 Título {letra} — {nombre}",
            "seccion": f"{letra}.0",
            "titulo": f"Alcance del Título {letra} — {nombre}",
            "texto": texto,
            "embedding": emb,
        }
        sb.table("nsr10_chunks").upsert(row).execute()
        print(f"Alcance Título {letra}: {nombre}")


if __name__ == "__main__":
    relabel()
    seed_alcance()
    print("\nListo. Verificar con: SELECT capitulo, count(*) FROM nsr10_chunks GROUP BY capitulo;")
