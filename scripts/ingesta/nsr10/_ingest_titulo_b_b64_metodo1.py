"""
NSR-10 Titulo B (Cargas), B.6.4 -- Metodo 1: Procedimiento Simplificado de
viento. Cierra un hueco real: el chunk existente NSR10-B-B_6_2_a_B_6_4 solo
resume el marco general (B.6.2 definiciones, B.6.3 nomenclatura, mencion de
que existe un Metodo 1), sin las condiciones de aplicabilidad, las ecuaciones
de diseno (B.6.4-1, B.6.4-2) ni las presiones minimas. Nota importante: los
valores numericos de Ps10/Pnet10 (presion base a h=10m, Exposicion B) NO
existen como tabla de texto en la fuente -- se leen de las figuras B.6.4-2 y
B.6.4-3 (graficos), por lo que no son extraibles como texto; se documenta esto
explicitamente para no generar falsa expectativa de una tabla faltante.

Fuente: NSR-10 archivo Titulo B paginas B-21 a B-82 (Drive, id
1ZLlTm7J__ucSvEt99qizpl3AocB12naL), paginas internas B-25 a B-27.

Uso: python _ingest_titulo_b_b64_metodo1.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-B-B_6_4_metodo1_simplificado",
    "capitulo": "NSR-10 Título B — Cargas",
    "seccion": "B.6.4.1 a B.6.4.3",
    "titulo": (
        "Metodo 1 (Procedimiento Simplificado) de cargas de viento: "
        "condiciones de aplicabilidad para SPRFV y para componentes/"
        "revestimientos, ecuaciones de diseno Ps=lambda*Kzt*I*Ps10 y "
        "Pnet=lambda*Kzt*I*Pnet10, presiones minimas 0.40 kN/m2. Los valores "
        "Ps10/Pnet10 se leen de figuras graficas (B.6.4-2/B.6.4-3), no de "
        "una tabla de texto."
    ),
    "texto": (
        "NSR-10 Título B, Capítulo B.6 — Fuerzas de viento. B.6.4 — Método 1: "
        "Procedimiento Simplificado.\n\n"
        "B.6.4.1 Alcance — Para usar el Método Simplificado, el edificio debe "
        "cumplir las condiciones de B.6.4.1.1 (si se va a diseñar el SPRFV "
        "con este método) o B.6.4.1.2 (si solo se van a diseñar componentes y "
        "revestimientos). Si solo cumple B.6.4.1.2, el SPRFV debe diseñarse "
        "obligatoriamente con el Método 2 (Analítico) o el Método 3 (Túnel "
        "de viento) — el Método 1 no es válido para el SPRFV en ese caso.\n\n"
        "B.6.4.1.1 Condiciones para el SPRFV (las 8 deben cumplirse todas): "
        "(a) edificio de diafragma simple (sin separaciones estructurales); "
        "(b) edificio BAJO según B.6.2 (altura media de cubierta h <= 18 m Y "
        "h no excede la menor dimensión horizontal); (c) edificio cerrado, "
        "cumpliendo provisiones de zonas propensas a huracanes (B.6.5.9.3); "
        "(d) forma regular (sin geometría irregular); (e) NO clasificado "
        "como flexible (frecuencia fundamental >= 1 Hz); (f) sin riesgo de "
        "cargas transversales al viento, generación de vórtices, golpeteo/"
        "aleteo, ni efectos de canalización o sacudimiento por estela de "
        "obstrucciones a barlovento; (g) sección transversal aproximadamente "
        "simétrica en cada dirección, cubierta plana o a dos/cuatro aguas "
        "con ángulo de inclinación theta <= 45°; (h) exento de los casos de "
        "carga torsional de la Nota 5 de la fig. B.6.5-7, o esos casos no "
        "controlan el diseño de ningún elemento del SPRFV.\n\n"
        "B.6.4.1.2 Condiciones para componentes y revestimientos (más laxas "
        "que para el SPRFV, las 4 deben cumplirse): (a) altura promedio h <= "
        "18.0 m; (b) edificio cerrado cumpliendo zonas propensas a "
        "huracanes; (c) forma regular; (d) cubierta plana, a dos aguas con "
        "theta <= 45°, o a cuatro aguas con theta <= 27°.\n\n"
        "B.6.4.2 Procedimiento de diseño — Pasos: (a) velocidad básica de "
        "viento V según B.6.5.4 (viento de cualquier dirección horizontal); "
        "(b) factor de importancia I según B.6.5.5; (c) categoría de "
        "exposición según B.6.5.6; (d) coeficiente de ajuste por altura y "
        "exposición, lambda, de la fig. B.6.4-2.\n\n"
        "B.6.4.2.1 SPRFV — presión de diseño simplificada (ecuación B.6.4-1):\n"
        "  Ps = lambda * Kzt * I * Ps10\n"
        "donde lambda = factor de ajuste por altura/exposición (fig. "
        "B.6.4-2), Kzt = factor topográfico (B.6.5.7, evaluado a la altura "
        "media de cubierta h, ecuación B.6.5-1), I = factor de importancia "
        "(B.6.5.5), Ps10 = presión de viento de diseño simplificada para "
        "Exposición B con h=10 m, leída de la fig. B.6.4-2 — Ps10 es un "
        "valor GRÁFICO (tabla de figura, no texto tabulado) que varía por "
        "zona de presión (A, B, C, D) y por velocidad básica de viento V.\n\n"
        "B.6.4.2.1.1 Presiones mínimas (SPRFV) — no menores al caso mínimo "
        "de B.6.1.3.1: Ps = +0.40 kN/m2 para zonas A, B, C y D; 0 kN/m2 para "
        "zonas E, F, G y H.\n\n"
        "B.6.4.2.2 Componentes y revestimientos — presión neta de diseño "
        "(ecuación B.6.4-2):\n"
        "  Pnet = lambda * Kzt * I * Pnet10\n"
        "donde Pnet10 = presión neta de viento de diseño para Exposición B a "
        "h=10.0 m, de la fig. B.6.4-3 (también gráfica, no tabulada como "
        "texto).\n\n"
        "B.6.4.2.2.1 Presiones mínimas (componentes/revestimientos): Pnet no "
        "menor a +0.4 kN/m2 (positiva) ni a -0.4 kN/m2 (negativa).\n\n"
        "B.6.4.3 Revestimiento permeable — se usan las cargas de la fig. "
        "B.6.4-3 para todo revestimiento permeable, salvo que datos "
        "experimentales aprobados u otra literatura reconocida demuestren "
        "cargas menores para el tipo específico de revestimiento.\n\n"
        "NOTA METODOLÓGICA: los valores numéricos base Ps10 y Pnet10 (y el "
        "factor lambda) se presentan en NSR-10 como FIGURAS/GRÁFICOS (fig. "
        "B.6.4-2 y B.6.4-3), no como tablas de texto — por eso no existe una "
        "'Tabla B.6.4-1' de valores extraíble como texto plano; cualquier "
        "cálculo real con el Método 1 requiere leer esas figuras o "
        "digitalizar sus curvas. El Método 2 (Analítico, B.6.5) sí usa "
        "tablas de texto explícitas (B.6.5-1 Factor de Importancia, B.6.5-2 "
        "Constante de Exposición, B.6.5-3 Kh/Kz, B.6.5-4 Kd) y es el método "
        "más apto para implementar como cálculo estructurado en StructAI."
    ),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vec = model.encode([CHUNK["texto"]], normalize_embeddings=True)[0]

    row = dict(CHUNK)
    row["embedding"] = vec.tolist()
    row["titulo"] = row["titulo"][:500]

    sb.table("nsr10_chunks").upsert(row, on_conflict="id").execute()
    print(f"OK: {CHUNK['id']} cargado con embedding ({len(CHUNK['texto'])} chars).")


if __name__ == "__main__":
    main()
