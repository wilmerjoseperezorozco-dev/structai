"""
Re-ingesta verbatim de las Tablas A.3-5, A.3-6 y A.3-7 y de las Figuras A.3-1 y
A.3-2 del Título A de NSR-10 (mezcla de sistemas en la altura; irregularidades
en planta y en altura con sus coeficientes φp y φa). Fase 4 del plan de cierre
del Título A (2026-11-08).

Fuente: NSR-10-95-105.pdf, páginas PDF 7-11 (A-58 a A-62), leídas visualmente.

Por qué se rehace: las tres tablas estaban cargadas DOS veces (familias
NSR10-A-Tabla_A3-* y NSR10-A-A_3_tabla_3_*), partidas en fragmentos sueltos
(p. ej. un chunk que solo decía «Referencias: A.3.3.6, A.3.4.2…»), la familia
antigua de la A.3-7 omitía «pero superior» en el tipo 5aA, y los criterios
geométricos de las Figuras A.3-1 y A.3-2 (p. ej. 1.4(Δ1+Δ2)/2 ≥ Δ1 >
1.2(Δ1+Δ2)/2; a > 1.30 b) no estaban.

Diseño: un chunk por tipo (descripción + φ + referencias juntos), criterios de
las figuras como chunks propios, notas verbatim. Cada chunk se verifica ≤ 128
tokens reales antes de subir. Los dibujos de las figuras NO se transcriben; sí
sus criterios numéricos/ecuaciones (notación lineal; Δ = deriva).

Uso: python _ingest_titulo_a_tablas_a3_5_a_a3_7_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"
LIMITE_TOKENS_REAL = 128

H5 = "NSR-10 Tabla A.3-5 — Mezcla de sistemas estructurales en la altura"
H6 = "NSR-10 Tabla A.3-6 — Irregularidades en planta"
H7 = "NSR-10 Tabla A.3-7 — Irregularidades en la altura"

CHUNKS = [
    # ---------------- Tabla A.3-5 ----------------
    {"id": "NSR10-A-A3T5-flexible-condiciones", "seccion": "Tabla A.3-5 — Mezcla de sistemas en la altura",
     "titulo": "Tabla A.3-5: estructura flexible apoyada sobre una estructura con mayor rigidez — condiciones (rigidez 10 veces, periodo 1.1 veces).",
     "texto": H5 + "\nEstructura flexible apoyada sobre una estructura con mayor rigidez — Descripción de la combinación:\n"
        "Puede utilizarse los requisitos dados aquí si la estructura cumple las siguientes condiciones: "
        "(a) Ambas partes de la estructura, consideradas separadamente, puedan ser clasificadas como regulares de acuerdo con los requisitos de A.3.3, "
        "(b) El promedio de las rigideces de piso de la parte baja sea por lo menos 10 veces el promedio de las rigideces de piso de la parte alta y "
        "(c) El período de la estructura, considerada como un todo, no sea mayor de 1.1 veces el período de la parte superior, al ser considerada como una estructura independiente empotrada en la base. "
        "Si no se cumplen las condiciones anteriores la estructura se considera irregular y deben seguirse los requisitos de A.3.3."},
    {"id": "NSR10-A-A3T5-flexible-requisitos-1", "seccion": "Tabla A.3-5 — Mezcla de sistemas en la altura",
     "titulo": "Tabla A.3-5: estructura flexible sobre rígida — requisitos: no se considera irregular (φp = φa = 1.0), parte superior analizada como estructura separada.",
     "texto": H5 + "\nEstructura flexible apoyada sobre una estructura con mayor rigidez — Requisitos:\n"
        "Se permite que esta combinación de sistemas estructurales no se considere irregular (φp = φa = 1.0), y el sistema puede diseñarse sísmicamente utilizando el método de la fuerza horizontal equivalente, tal como lo prescribe el Capítulo A.4, de la siguiente manera: "
        "(1) La parte superior flexible puede ser analizada y diseñada como una estructura separada, apoyada para efecto de las fuerzas horizontales por la parte más rígida inferior, usando el valor apropiado de R0 para su sistema estructural."},
    {"id": "NSR10-A-A3T5-flexible-requisitos-2", "seccion": "Tabla A.3-5 — Mezcla de sistemas en la altura",
     "titulo": "Tabla A.3-5: estructura flexible sobre rígida — la parte rígida inferior se diseña aparte y las reacciones de la parte superior se amplifican por la relación R0 superior / R0 inferior.",
     "texto": H5 + "\nEstructura flexible apoyada sobre una estructura con mayor rigidez — Requisitos (continuación):\n"
        "(2) La parte rígida inferior debe ser analizada y diseñada como una estructura separada, usando el valor apropiado de R0 para su sistema estructural, y las reacciones de la parte superior, obtenidas de su análisis, deben ser amplificadas por la relación entre el valor de R0 para la parte superior y el valor de R0 de la parte inferior."},
    {"id": "NSR10-A-A3T5-rigida", "seccion": "Tabla A.3-5 — Mezcla de sistemas en la altura",
     "titulo": "Tabla A.3-5: estructura rígida apoyada sobre una estructura con menor rigidez — no es aceptable como solución estructural.",
     "texto": H5 + "\nEstructura rígida apoyada sobre una estructura con menor rigidez — Descripción de la combinación:\n"
        "Corresponde a edificaciones en las cuales se suspende antes de llegar a la base de la estructura, parcial o totalmente, un sistema estructural más rígido que el que llega a la base de la estructura. Este tipo de combinación de sistemas estructurales en la altura presenta inconvenientes en su comportamiento sísmico. No es aceptable como una solución estructural para el presente Reglamento.\n"
        "Requisitos: (1) No es aceptable como solución estructural para el presente Reglamento."},
]

# ---------------- Tabla A.3-6 (planta) ----------------
T6 = [
    ("1aP", "Irregularidad torsional", "La irregularidad torsional existe cuando en una edificación con diafragma rígido, la máxima deriva de piso de un extremo de la estructura, calculada incluyendo la torsión accidental y medida perpendicularmente a un eje determinado, es más de 1.2 y menor o igual a 1.4 veces la deriva promedio de los dos extremos de la estructura, con respecto al mismo eje de referencia.", "0.9", "A.3.3.6, A.3.4.2, A.3.6.3.1, A.3.6.7.1, A.3.6.8.4, A.5.2.1"),
    ("1bP", "Irregularidad torsional extrema", "La irregularidad torsional extrema existe cuando en una edificación con diafragma rígido, la máxima deriva de piso de un extremo de la estructura, calculada incluyendo la torsión accidental y medida perpendicularmente a un eje determinado, es más de 1.4 veces la deriva promedio de los dos extremos de la estructura, con respecto al mismo eje de referencia.", "0.8", "A.3.3.6, A.3.4.2, A.3.6.3.1, A.3.6.7.1, A.3.6.8.4, A.5.2.1"),
    ("2P", "Retrocesos excesivos en las esquinas", "La configuración de una estructura se considera irregular cuando ésta tiene retrocesos excesivos en sus esquinas. Un retroceso en una esquina se considera excesivo cuando las proyecciones de la estructura, a ambos lados del retroceso, son mayores que el 15 por ciento de la dimensión de la planta de la estructura en la dirección del retroceso.", "0.9", "A.3.4.2, A.3.6.8.4, A.3.6.8.5, A.5.2.1"),
    ("3P", "Discontinuidades en el diafragma", "Cuando el diafragma tiene discontinuidades apreciables o variaciones en su rigidez, incluyendo las causadas por aberturas, entradas, retrocesos o huecos con áreas mayores al 50 por ciento del área bruta del diafragma o existen cambios en la rigidez efectiva del diafragma de más del 50 por ciento, entre niveles consecutivos, la estructura se considera irregular.", "0.9", "A.3.3.7, A.3.4.2, A.3.6.8.4, A.5.2.1"),
    ("4P", "Desplazamientos del plano de acción de elementos verticales", "La estructura se considera irregular cuando existen discontinuidades en las trayectorias de las fuerzas inducidas por los efectos sísmicos, tales como cuando se traslada el plano que contiene a un grupo de elementos verticales del sistema de resistencia sísmica, en una dirección perpendicular a él, generando un nuevo plano. Los altillos o mansardas de un solo piso se eximen de este requisito en la consideración de irregularidad.", "0.8", "A.3.3.7, A.3.4.2, A.3.6.8.4, A.3.6.12, A.5.2.1"),
    ("5P", "Sistemas no paralelos", "Cuando las direcciones de acción horizontal de los elementos verticales del sistema de resistencia sísmica no son paralelas o simétricas con respecto a los ejes ortogonales horizontales principales del sistema de resistencia sísmica, la estructura se considera irregular.", "0.9", "A.3.4.2, A.3.6.3.1, A.5.2.1"),
]
for tipo, nombre, desc, fi, refs in T6:
    CHUNKS.append({
        "id": f"NSR10-A-A3T6-{tipo}", "seccion": "Tabla A.3-6 — Irregularidades en planta",
        "titulo": f"Tabla A.3-6 tipo {tipo} — {nombre}: φp = {fi}",
        "texto": f"{H6}\nTipo {tipo} — {nombre}\n{desc}\nφp = {fi}. Referencias: {refs}.",
        "prefijo": 2,
    })
CHUNKS.append({
    "id": "NSR10-A-A3T6-notas", "seccion": "Tabla A.3-6 — Irregularidades en planta",
    "titulo": "Tabla A.3-6: notas (qué irregularidades en planta se evalúan en zona intermedia grupo I y en zona baja grupos I y II).",
    "texto": H6 + "\nNotas:\n"
        "1. En zonas de amenaza sísmica intermedia para edificaciones pertenecientes al grupo de uso I, la evaluación de irregularidad se puede limitar a las irregularidades de los tipos 1aP, 1bP, 3P y 4P (Véase A.3.3.7).\n"
        "2. En zonas de amenaza sísmica baja para edificaciones pertenecientes a los grupos de uso I y II, la evaluación de irregularidad se puede limitar a las irregularidades tipo 1aP e 1bP (Véase A.3.3.6).",
})
CHUNKS.append({
    "id": "NSR10-A-A3F1-criterios", "seccion": "Figura A.3-1 — Irregularidades en planta",
    "titulo": "Figura A.3-1: criterios geométricos de irregularidad en planta (1aP: 1.2 a 1.4 de la deriva promedio; 1bP: más de 1.4; 2P: A > 0.15B y C > 0.15D; 3P: C×D > 0.5 A×B).",
    "texto": "NSR-10 Figura A.3-1 — Irregularidades en planta (criterios; los dibujos no se transcriben)\n"
        "Tipo 1aP — Irregularidad torsional, φp = 0.9: 1.4 (Δ1+Δ2)/2 ≥ Δ1 > 1.2 (Δ1+Δ2)/2\n"
        "Tipo 1bP — Irregularidad torsional extrema, φp = 0.8: Δ1 > 1.4 (Δ1+Δ2)/2\n"
        "Tipo 2P — Retrocesos en las esquinas, φp = 0.9: A > 0.15B y C > 0.15D\n"
        "Tipo 3P — Irregularidad del diafragma, φp = 0.9: 1) C × D > 0.5 A × B; 2) (C × D + C × E) > 0.5 A × B\n"
        "Tipo 4P — Desplazamiento de los planos de acción, φp = 0.8. Tipo 5P — Sistemas no paralelos, φp = 0.9 (solo ilustración).",
})

# ---------------- Tabla A.3-7 (altura) ----------------
T7 = [
    ("1aA", "Piso flexible (Irregularidad en rigidez)", "Cuando la rigidez ante fuerzas horizontales de un piso es menor del 70 por ciento pero superior o igual al 60 por ciento de la rigidez del piso superior o menor del 80 por ciento pero superior o igual al 70 por ciento del promedio de la rigidez de los tres pisos superiores, la estructura se considera irregular.", "0.9", "A.3.3.5.1, A.3.4.2"),
    ("1bA", "Piso flexible (Irregularidad extrema en rigidez)", "Cuando la rigidez ante fuerzas horizontales de un piso es menor del 60 por ciento de la rigidez del piso superior o menor del 70 por ciento del promedio de la rigidez de los tres pisos superiores, la estructura se considera irregular.", "0.8", "A.3.3.5.1, A.3.4.2"),
    ("2A", "Irregularidad en la distribución de las masas", "Cuando la masa, mi, de cualquier piso es mayor que 1.5 veces la masa de uno de los pisos contiguos, la estructura se considera irregular. Se exceptúa el caso de cubiertas que sean más livianas que el piso de abajo.", "0.9", "A.3.3.5.1, A.3.4.2"),
    ("3A", "Irregularidad geométrica", "Cuando la dimensión horizontal del sistema de resistencia sísmica en cualquier piso es mayor que 1.3 veces la misma dimensión en un piso adyacente, la estructura se considera irregular. Se exceptúa el caso de los altillos de un solo piso.", "0.9", "A.3.4.2"),
    ("4A", "Desplazamientos dentro del plano de acción", "La estructura se considera irregular cuando existen desplazamientos en el alineamiento de elementos verticales del sistema de resistencia sísmica, dentro del mismo plano que los contiene, y estos desplazamientos son mayores que la dimensión horizontal del elemento. Cuando los elementos desplazados solo sostienen la cubierta de la edificación sin otras cargas adicionales de tanques o equipos, se eximen de esta consideración de irregularidad.", "0.8", "A.3.3.7, A.3.4.2, A.3.6.12"),
    ("5aA", "Piso débil — Discontinuidad en la resistencia", "Cuando la resistencia del piso es menor del 80 por ciento de la del piso inmediatamente superior pero superior o igual al 65 por ciento, entendiendo la resistencia del piso como la suma de las resistencias de todos los elementos que comparten el cortante del piso para la dirección considerada, la estructura se considera irregular.", "0.9", "A.3.2.4.1, A.3.3.6, A.3.3.7, A.3.4.2"),
    ("5bA", "Piso débil — Discontinuidad extrema en la resistencia", "Cuando la resistencia del piso es menor del 65 por ciento de la del piso inmediatamente superior, entendiendo la resistencia del piso como la suma de las resistencias de todos los elementos que comparten el cortante del piso para la dirección considerada, la estructura se considera irregular.", "0.8", "A.3.2.4.1, A.3.3.6, A.3.3.7, A.3.4.2"),
]
for tipo, nombre, desc, fi, refs in T7:
    CHUNKS.append({
        "id": f"NSR10-A-A3T7-{tipo}", "seccion": "Tabla A.3-7 — Irregularidades en la altura",
        "titulo": f"Tabla A.3-7 tipo {tipo} — {nombre}: φa = {fi}",
        "texto": f"{H7}\nTipo {tipo} — {nombre}\n{desc}\nφa = {fi}. Referencias: {refs}.",
        "prefijo": 2,
    })
CHUNKS.append({
    "id": "NSR10-A-A3T7-notas", "seccion": "Tabla A.3-7 — Irregularidades en la altura",
    "titulo": "Tabla A.3-7: notas (deriva menor de 1.3 veces; qué irregularidades en altura se evalúan en zona intermedia grupo I y zona baja grupos I y II).",
    "texto": H7 + "\nNotas:\n"
        "1. Cuando la deriva de cualquier piso es menor de 1.3 veces la deriva del piso siguiente hacia arriba, puede considerarse que no existen irregularidades de los tipos 1aA, 1bA, 2A, ó 3A (Véase A.3.3.5.1).\n"
        "2. En zonas de amenaza sísmica intermedia para edificaciones pertenecientes al grupo de uso I, la evaluación de irregularidad se puede limitar a las irregularidades de los tipos 4A, 5aA y 5bA (Véase A.3.3.7).\n"
        "3. En zonas de amenaza sísmica baja para edificaciones pertenecientes a los grupos de usos I y II, la evaluación de irregularidad se puede limitar a la irregularidad tipo 5aA y 5bA (Véase A.3.3.6).",
})
CHUNKS.append({
    "id": "NSR10-A-A3F2-criterios-1", "seccion": "Figura A.3-2 — Irregularidades en la altura",
    "titulo": "Figura A.3-2: criterios de irregularidad en altura por rigidez y masa (1aA: 0.60 KD ≤ KC < 0.70 KD; 1bA: KC < 0.60 KD; 2A: mD > 1.50 mE o mC).",
    "texto": "NSR-10 Figura A.3-2 — Irregularidades en la altura (criterios; los dibujos no se transcriben)\n"
        "Tipo 1aA — Piso flexible, φa = 0.9: 0.60 Rigidez KD ≤ Rigidez KC < 0.70 Rigidez KD, o 0.70 (KD+KE+KF)/3 ≤ Rigidez KC < 0.80 (KD+KE+KF)/3\n"
        "Tipo 1bA — Piso flexible extremo, φa = 0.8: Rigidez KC < 0.60 Rigidez KD, o Rigidez KC < 0.70 (KD+KE+KF)/3\n"
        "Tipo 2A — Distribución masa, φa = 0.9: mD > 1.50 mE, o mD > 1.50 mC",
})
CHUNKS.append({
    "id": "NSR10-A-A3F2-criterios-2", "seccion": "Figura A.3-2 — Irregularidades en la altura",
    "titulo": "Figura A.3-2: criterios de irregularidad en altura geométrica y por resistencia (3A: a > 1.30 b; 4A: b > a; 5aA: 0.65 a 0.80 de la resistencia; 5bA: menos de 0.65).",
    "texto": "NSR-10 Figura A.3-2 — Irregularidades en la altura (criterios, continuación)\n"
        "Tipo 3A — Geométrica, φa = 0.9: a > 1.30 b\n"
        "Tipo 4A — Desplazamiento dentro del plano de acción, φa = 0.8: b > a\n"
        "Tipo 5aA — Piso débil, φa = 0.9: 0.65 Resist. Piso C ≤ Resist. Piso B < 0.80 Resist. Piso C\n"
        "Tipo 5bA — Piso débil extremo, φa = 0.8: Resistencia Piso B < 0.65 Resistencia Piso C",
})

PATRONES_ANTIGUOS = ["NSR10-A-Tabla_A3-5_%", "NSR10-A-Tabla_A3-6_%", "NSR10-A-Tabla_A3-7_%",
                     "NSR10-A-A_3_tabla_3_5_%", "NSR10-A-A_3_tabla_3_6_%", "NSR10-A-A_3_tabla_3_7_%"]


def _partir(c: dict, tok) -> list[dict]:
    """Si el chunk supera el límite, lo parte por líneas repitiendo el prefijo
    (encabezado y, en filas, «Tipo — nombre»). Una línea aún demasiado larga se
    parte en el último punto antes de la mitad."""
    def n_tok(t: str) -> int:
        return len(tok.encode(t, add_special_tokens=True))

    if n_tok(c["texto"]) <= LIMITE_TOKENS_REAL:
        return [c]
    NL = chr(10)
    lineas = c["texto"].split(NL)
    k = c.get("prefijo", 1)
    prefijo, cuerpo = NL.join(lineas[:k]), lineas[k:]
    # partir líneas largas
    pendientes: list[str] = []
    for ln in cuerpo:
        if n_tok(prefijo + NL + ln) <= LIMITE_TOKENS_REAL:
            pendientes.append(ln)
            continue
        resto = ln
        while n_tok(prefijo + NL + resto) > LIMITE_TOKENS_REAL:
            corte = resto.rfind(". ", 0, len(resto) // 2 + 40)
            corte = corte + 1 if corte > 0 else resto.rfind(", ", 0, len(resto) // 2 + 40)
            if corte <= 0:
                raise SystemExit(f"No se puede partir: {c['id']}")
            pendientes.append(resto[:corte].strip())
            resto = resto[corte:].strip()
        pendientes.append(resto)
    partes: list[str] = []
    actual = ""
    for ln in pendientes:
        cand = (actual + NL + ln) if actual else ln
        if actual and n_tok(prefijo + NL + cand) > LIMITE_TOKENS_REAL:
            partes.append(actual)
            actual = ln
        else:
            actual = cand
    if actual:
        partes.append(actual)
    out = []
    for i, cuerpo_p in enumerate(partes, 1):
        out.append({**c, "id": f"{c['id']}_p{i}", "texto": prefijo + NL + cuerpo_p})
    return out


def main() -> None:
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tok = model.tokenizer
    finales: list[dict] = []
    for c in CHUNKS:
        finales.extend(_partir(c, tok))
    excedidas = [(c["id"], n) for c in finales
                 if (n := len(tok.encode(c["texto"], add_special_tokens=True))) > LIMITE_TOKENS_REAL]
    for cid, n in excedidas:
        print(f"  ! sobre {LIMITE_TOKENS_REAL} tokens: {cid} = {n}")
    if excedidas:
        raise SystemExit("Chunks sobre el limite real: acortar/partir antes de subir.")
    print(f"{len(CHUNKS)} chunks logicos -> {len(finales)} chunks finales")
    ids = [c["id"] for c in finales]
    assert len(ids) == len(set(ids)), "ids duplicados"

    vec = model.encode([c["texto"] for c in finales], normalize_embeddings=True, show_progress_bar=False)
    rows = [{"id": c["id"], "capitulo": CAPITULO, "seccion": c["seccion"], "titulo": c["titulo"][:500],
             "texto": c["texto"], "embedding": v.tolist()} for c, v in zip(finales, vec)]
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    borrados = 0
    for pat in PATRONES_ANTIGUOS:
        viejos = sb.table("nsr10_chunks").select("id").like("id", pat).execute().data
        if viejos:
            sb.table("nsr10_chunks").delete().in_("id", [v["id"] for v in viejos]).execute()
            borrados += len(viejos)
    print(f"OK: {len(rows)} chunks cargados, {borrados} chunks antiguos borrados.")


if __name__ == "__main__":
    main()
