"""Etapa 1 (Título C): tablas del Capítulo C.4 (durabilidad) que el corpus solo citaba por nombre.
Transcritas de la imagen de las páginas C-35 a C-38 (`NSR-10-337-340.pdf`, leídas el 2026-11-08), en notación lineal. Solo agrega filas.
Uso: python _ingest_titulo_c4_tablas_durabilidad.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
CAPITULO = "C"
P = "NSR-10 Título C "
CHUNKS = [
    {"id": "NSR10-C-C_4_2_1_tabla", "seccion": "C.4.2.1", "titulo": "Tabla C.4.2.1 — Categorías y clases de exposición",
     "texto": P + "Tabla C.4.2.1 — Categorías y clases de exposición. Categoría F (congelamiento y deshielo): F0 no aplicable, concreto no expuesto a ciclos de congelamiento y deshielo; "
     "F1 moderada, expuesto a ciclos de congelamiento y deshielo y exposición ocasional a la humedad; F2 severa, en contacto continuo con la humedad; "
     "F3 muy severa, en contacto continuo con la humedad y expuesto a productos químicos descongelantes. "
     "Categoría S (sulfato), sulfatos solubles en agua (SO4) en el suelo, % en peso / sulfato (SO4) disuelto en agua, ppm: S0 no aplicable SO4 < 0.10 / SO4 < 150; "
     "S1 moderada 0.10 ≤ SO4 < 0.20 / 150 ≤ SO4 < 1500, o agua marina; S2 severa 0.20 ≤ SO4 ≤ 2.00 / 1500 ≤ SO4 ≤ 10000; S3 muy severa SO4 > 2.00 / SO4 > 10000. "
     "Categoría P (requiere baja permeabilidad): P0 no aplicable, en contacto con el agua donde no se requiere baja permeabilidad; P1 requerida, en contacto con el agua donde se requiera baja permeabilidad. "
     "Categoría C (protección del refuerzo contra la corrosión): C0 no aplicable, concreto seco o protegido contra la humedad; C1 moderada, expuesto a la humedad pero no a una fuente externa de cloruros; "
     "C2 severa, expuesto a la humedad y a una fuente externa de cloruros provenientes de productos químicos descongelantes, sal, agua salobre, agua de mar o salpicaduras del mismo origen."},
    {"id": "NSR10-C-C_4_3_1_tabla", "seccion": "C.4.3.1", "titulo": "Tabla C.4.3.1 — Requisitos para el concreto según la clase de exposición",
     "texto": P + "Tabla C.4.3.1 — Requisitos para el concreto según la clase de exposición (relación a/mc máxima; f'c mínimo en MPa). "
     "F0: a/mc N/A, f'c 17. F1: 0.45, 31, contenido de aire según tabla C.4.4.1. F2: 0.45, 31, aire según tabla C.4.4.1. F3: 0.45, 31, aire según tabla C.4.4.1 y límites en los cementantes según tabla C.4.4.2. "
     "S0: N/A, 17, sin restricción en el tipo de cemento (ASTM C150, C595, C1157), cloruro de calcio sin restricción. "
     "S1: 0.50, 28, ASTM C150 tipo II, ASTM C595 IP(MS) o IS(<70)(MS), ASTM C1157 MS, cloruro de calcio sin restricción. "
     "S2: 0.45, 31, ASTM C150 tipo V, ASTM C595 IP(HS) o IS(<70)(HS), ASTM C1157 HS, cloruro de calcio no se permite. "
     "S3: 0.45, 31, ASTM C150 tipo V más puzolanas o escoria, ASTM C595 IP(HS) y puzolanas o escoria, o IS(<70)(HS) y puzolanas o escoria, ASTM C1157 HS y puzolanas o escoria, cloruro de calcio no se permite. "
     "P0: N/A, 17, ninguna. P1: 0.50, 28, ninguna. "
     "Contenido máximo de iones de cloruro (Cl-) soluble en agua en el concreto, porcentaje por peso de cemento (concreto reforzado / preesforzado): C0: a/mc N/A, f'c 17, 1.00 / 0.06. C1: 0.50, 17, 0.30 / 0.06. C2: 0.40, 35, 0.15 / 0.06, requisitos relacionados C.7.7.6 y C.18.16. "
     "Notas: se pueden permitir combinaciones alternativas de materiales cementantes siempre que sean ensayadas para comprobar la resistencia a los sulfatos y cumplan los criterios de C.4.5.1; "
     "para exposición al agua marina se permiten otros tipos de cemento pórtland con contenidos de hasta 10 por ciento de aluminato tricálcico (C3A) si la relación a/mc no excede 0.40; "
     "se permiten otros tipos de cemento como el tipo III o tipo I en exposiciones clase S1 o S2 si el contenido de C3A es menor al 8 ó 5 por ciento, respectivamente; "
     "la cantidad de la fuente específica de puzolana o escoria que se debe usar no debe ser inferior a la cantidad que haya sido determinada por experiencia en mejorar la resistencia a sulfatos cuando se usa en concretos que contienen cemento tipo V, "
     "o de manera alternativa no debe ser menor a la cantidad ensayada según la NTC 3330 (ASTM C1012) y cumplir con los requisitos de C.4.5.1; "
     "el contenido de iones cloruro solubles en agua se determina según NTC 4049 (ASTM C1218M) a edades de 28 a 42 días; para concreto liviano véase C.4.1.2."},
    {"id": "NSR10-C-C_4_4_1_tabla", "seccion": "C.4.4.1", "titulo": "Tabla C.4.4.1 — Contenido total de aire para concreto expuesto a congelamiento y deshielo",
     "texto": P + "Tabla C.4.4.1 — Contenido total de aire (porcentaje) para concreto expuesto a ciclos de congelamiento y deshielo, por tamaño máximo nominal del agregado (mm): exposición clase F1 / clases F2 y F3. "
     "9.5: 6 / 7.5. 12.5: 5.5 / 7. 19.0: 5 / 6. 25.0: 4.5 / 6. 37.5: 4.5 / 5.5. 50: 4 / 5. 75: 3.5 / 4.5. Tolerancia ±1.5 por ciento; para f'c mayor de 35 MPa se puede reducir el aire en 1 por ciento (C.4.4.1)."},
    {"id": "NSR10-C-C_4_4_2_tabla", "seccion": "C.4.4.2", "titulo": "Tabla C.4.4.2 — Requisitos para concreto sometido a clase de exposición F3",
     "texto": P + "Tabla C.4.4.2 — Requisitos para concreto sometido a clase de exposición F3, porcentaje máximo sobre el total de materiales cementantes en peso: "
     "cenizas volantes u otras puzolanas que cumplan NTC 3493 (ASTM C618): 25; escoria que cumple NTC 4018 (ASTM C989): 50; humo de sílice que cumple NTC 4637 (ASTM C1240): 10; "
     "total de cenizas volantes u otras puzolanas, escoria y humo de sílice: 50; total de cenizas volantes u otras puzolanas y humo de sílice: 35. "
     "El total de materiales cementantes incluye cementos ASTM C150, C595, NTC 4578 (ASTM C845) y ASTM C1157, y los porcentajes incluyen las puzolanas presentes en cementos adicionados tipo IP, la escoria de cementos tipo IS y el humo de sílice de cementos adicionados. "
     "Las cenizas volantes u otras puzolanas y el humo de sílice no deben constituir más del 25 y 10 por ciento, respectivamente, del peso total de materiales cementantes. Este límite aplica solo a la clase F3 (congelamiento y deshielo)."},
    {"id": "NSR10-C-C_4_5_1_tabla", "seccion": "C.4.5.1", "titulo": "Tabla C.4.5.1 — Conveniencia de combinaciones de materiales cementantes expuestos a sulfatos",
     "texto": P + "Tabla C.4.5.1 — Requisitos para establecer la conveniencia de las combinaciones de materiales cementantes expuestos a sulfatos solubles en agua. "
     "Expansión máxima al ser ensayada usando NTC 3330 (ASTM C1012): clase S1: 0.10 por ciento a 6 meses; clase S2: 0.05 por ciento a 6 meses o 0.10 por ciento a 12 meses (el límite a 12 meses solo se aplica cuando el límite a 6 meses no es alcanzado); clase S3: 0.10 por ciento a 18 meses."},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for c in CHUNKS:
        print(f"--- {c['id']} ({len(c['texto'])} car.)")
    if args.dry_run:
        return
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    filas = []
    for c in CHUNKS:
        for k, p in enumerate(_sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)):
            filas.append({"capitulo": CAPITULO, **c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p,
                          "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
