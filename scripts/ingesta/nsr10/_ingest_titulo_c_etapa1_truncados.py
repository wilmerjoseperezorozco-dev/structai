"""
NSR-10 Título C — Etapa 1 de la ingesta (auditoría 2026-11-08): numerales cuyo chunk en `nsr10_chunks` está
truncado respecto al PDF fuente (ver docs/AUDITORIA_NSR10_PAGINAS_2026-11.md y docs/ANALISIS_MOTORES_Y_ROADMAP_2026-11.md).

Cada numeral se extrae del PDF fuente (scripts/ingesta/nsr10/raw/, gitignored) desde su encabezado hasta el siguiente
encabezado, se limpia (pies de página, líneas de puntos) y se re-trocea por el límite real de tokens. El `id` es el del
chunk existente, así el upsert lo REEMPLAZA (convención del proyecto: on_conflict="id").

Las ecuaciones que pypdf entrega desordenadas NO se transcriben: el chunk dice explícitamente que la ecuación está en la
fuente. Nada se inventa ni se reconstruye de memoria.

Uso:
    python _ingest_titulo_c_etapa1_truncados.py --dry-run     # solo imprime
    python _ingest_titulo_c_etapa1_truncados.py               # upsert
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

CAPITULO = "NSR-10 Título C — Concreto Estructural"
RAW = HERE / "raw"

# numeral -> (PDF fuente, id de chunk existente)
OBJETIVOS = {
    "C.10.10.4.1": "NSR-10-377-387.pdf",
    "C.21.3.3": "NSR-10-477-501.pdf",
    "C.21.3.5.6": "NSR-10-477-501.pdf",
}

# Lote 2 (2026-11-08): numerales truncados que alimentan los motores de concreto (recubrimiento, deflexiones,
# cortante, losas, zapatas, muros). Los de id con sufijo «-subN» se reemplazan borrando las filas viejas DESPUÉS del upsert.
OBJETIVOS_LOTE2 = {
    "C.7.7.2": "NSR-10-353-362.pdf", "C.7.7.3": "NSR-10-353-362.pdf",
    "C.9.5.2.5": "NSR-10-369-375.pdf", "C.9.5.2.6": "NSR-10-369-375.pdf",
    "C.9.5.3.1": "NSR-10-369-375.pdf", "C.9.5.3.3": "NSR-10-369-375.pdf", "C.9.5.3.4": "NSR-10-369-375.pdf",
    "C.10.10.2": "NSR-10-377-387.pdf",
    "C.11.3.3.1": "NSR-10-389-407.pdf", "C.11.3.4": "NSR-10-389-407.pdf", "C.11.4.6.1": "NSR-10-389-407.pdf",
    "C.11.5.1": "NSR-10-389-407.pdf", "C.11.8.6": "NSR-10-389-407.pdf", "C.11.11.7.2": "NSR-10-389-407.pdf",
    "C.12.16.2": "NSR-10-409-419.pdf", "C.13.6.4.2": "NSR-10-421-434.pdf",
    "C.15.11.4": "NSR-10-443-448.pdf", "C.21.8.4": "NSR-10-477-501.pdf",
}
SUB_VIEJOS = {"C.7.7.2": "NSR10-C-C_7_7_2-sub%", "C.9.5.3.1": "NSR10-C-C_9_5_3_1-sub%"}

HEADING = re.compile(r"^\s*([A-K]\.\d{1,3}(?:\.\d{1,3}){0,6})\s*[—–\-]\s*\S")
PIE = re.compile(r"^\s*(NSR-10\s*[–—-].*|[A-K]-\d{1,4})\s*$")
ECUACION = re.compile(r"\(C\.\d+-\d+\)")


def extraer(numeral: str, pdf: str) -> str:
    import pypdf

    lector = pypdf.PdfReader(str(RAW / pdf))
    lineas = "\n".join((p.extract_text() or "") for p in lector.pages).splitlines()
    ini = next((i for i, l in enumerate(lineas) if (m := HEADING.match(l)) and m.group(1) == numeral), None)
    if ini is None:
        raise SystemExit(f"{numeral}: encabezado no encontrado en {pdf}")
    fin = next((j for j in range(ini + 1, len(lineas)) if HEADING.match(lineas[j])), len(lineas))
    limpias = []
    for l in lineas[ini:fin]:
        if PIE.match(l) or not l.strip():
            continue
        limpias.append(re.sub(r"\.{4,}", " — ", l.strip()))
    texto = re.sub(r"\s+", " ", " ".join(limpias)).strip()
    if numeral.startswith("C.7.7."):  # verificado contra la imagen de la página: «db» (diámetro) sale como «bd», «10» como «.10»
        texto = texto.replace("— bd pero", "— db pero").replace("— .10", "— 10")
    if ECUACION.search(texto):
        texto += " [Nota de fidelidad: las ecuaciones de este numeral no se transcriben (la extracción de texto las desordena); consultar la fuente.]"
    return texto


# Texto transcrito leyendo la página del PDF (imagen), porque la extracción desordena las ecuaciones.
# Las ecuaciones se escriben en notación lineal; «I» es el momento de inercia (la fuente imprime una «l»).
MANUAL = {
    "C.9.5.2.5": (
        "C.9.5.2.5 — A menos que los valores se obtengan mediante un análisis más completo, la deflexión adicional a largo plazo, "
        "resultante del flujo plástico y retracción de elementos en flexión (concreto normal o liviano), debe determinarse multiplicando "
        "la deflexión inmediata causada por la carga permanente por el factor λΔ = ξ / (1 + 50 ρ') (C.9-11), donde ρ' es el valor en la mitad de la luz "
        "para tramos simples y continuos y en el punto de apoyo para voladizos. Puede tomarse ξ, el factor dependiente del tiempo para cargas sostenidas, igual a: "
        "5 años o más 2.0; 12 meses 1.4; 6 meses 1.2; 3 meses 1.0."
    ),
    "C.9.5.3.3": (
        "C.9.5.3.3 — El espesor mínimo h para losas con vigas que se extienden entre los apoyos en todos los lados debe ser: "
        "(a) Para αfm igual o menor que 0.2, se aplican las disposiciones de C.9.5.3.2. "
        "(b) Para αfm mayor que 0.2 pero no mayor que 2.0, h no debe ser menor que h = ℓn (0.8 + fy/1400) / (36 + 5 β (αfm − 0.2)) (C.9-12), pero no menor que 125 mm. "
        "(c) Para αfm mayor que 2.0, h no debe ser menor que h = ℓn (0.8 + fy/1400) / (36 + 9 β) (C.9-13), y no menor que 90 mm. "
        "(d) En bordes discontinuos debe disponerse una viga de borde que tenga una relación de rigidez αf no menor de 0.80, o bien aumentar el espesor mínimo requerido "
        "por las ecuaciones (C.9-12) ó (C.9-13), por lo menos un 10 por ciento en el panel que tenga un borde discontinuo. "
        "TABLA C.9.5(c) — Espesores mínimos de losas sin vigas interiores (ℓn = luz libre en la dirección larga, medida entre caras de los apoyos). "
        "Sin ábacos: panel exterior sin viga de borde / panel exterior con viga de borde / panel interior; con ábacos: panel exterior sin viga de borde / con viga de borde / panel interior. "
        "fy = 280 MPa: ℓn/33, ℓn/36, ℓn/36; ℓn/36, ℓn/40, ℓn/40. "
        "fy = 420 MPa: ℓn/30, ℓn/33, ℓn/33; ℓn/33, ℓn/36, ℓn/36. "
        "fy = 520 MPa: ℓn/28, ℓn/31, ℓn/31; ℓn/31, ℓn/34, ℓn/34. "
        "Notas: para fy entre los valores dados, el espesor mínimo se obtiene por interpolación lineal. Ábaco, como se define en C.13.2.5. "
        "Losas con vigas entre las columnas a lo largo de los bordes exteriores: αf de la viga de borde no menor que 0.8. "
        "ℓn en (b) y (c) es la luz libre en la dirección larga medida cara a cara de las vigas; β es la relación de la luz libre en la dirección larga a la luz libre en la dirección corta de la losa."
    ),
    "C.11.3.3.1": (
        "C.11.3.3.1 — Vci se debe calcular por medio de: Vci = 0.05 λ √f'c bw dp + Vd + Vi Mcre / Mmax (C.11-10), donde dp no debe tomarse menor que 0.80h y "
        "Mcre = (I/yt) (0.5 λ √f'c + fpe − fd) (C.11-11), y los valores de Mmax y Vi se deben calcular con la combinación de carga que causa el máximo momento mayorado en la sección. "
        "No hay necesidad de tomar Vci menor que 0.14 λ √f'c bw d."
    ),
    "C.11.5.1": (
        "C.11.5.1 — Umbral de Torsión. Se permite despreciar los efectos de la torsión si el momento torsional mayorado Tu es menor que: "
        "(a) en elementos no preesforzados: φ 0.083 λ √f'c (Acp² / pcp); "
        "(b) en elementos preesforzados: φ 0.083 λ √f'c (Acp² / pcp) √(1 + fpc / (0.33 λ √f'c)); "
        "(c) para elementos no preesforzados sometidos a tracción axial o fuerzas de compresión: φ 0.083 λ √f'c (Acp² / pcp) √(1 + Nu / (0.33 Ag λ √f'c)). "
        "En elementos construidos monolíticamente con una losa, el ancho sobresaliente del ala usado para calcular Acp y pcp debe cumplir con C.13.2.4. "
        "Para una sección hueca, se debe usar Ag en lugar de Acp en C.11.5.1 y en los límites externos de la sección deben cumplir con C.13.2.4."
    ),
    "C.11.11.7.2": (
        "C.11.11.7.2 — El esfuerzo cortante que resulta de la transferencia de momento por excentricidad de cortante debe suponerse que varía linealmente alrededor del centroide "
        "de las secciones críticas definidas en C.11.11.1.2. El máximo esfuerzo cortante debido a Vu y Mu no debe exceder φvn: "
        "(a) Para elementos sin refuerzo para cortante: φvn = φ Vc / (bo d) (C.11-38), donde Vc se define en C.11.11.2.1 ó C.11.11.2.2. "
        "(b) Para elementos con refuerzo para cortante distinto a cabezas de cortante: φvn = φ (Vc + Vs) / (bo d) (C.11-39), donde Vc y Vs se definen en C.11.11.3.1. "
        "El diseño debe tomar en cuenta la variación del esfuerzo cortante alrededor de la columna. El esfuerzo cortante debido a la fuerza cortante y momento mayorados "
        "no deben exceder de 0.17 φ λ √f'c en la sección crítica ubicada a d/2 fuera de la línea exterior de las ramas del estribo que rodean la columna. "
        "(C.11.11.7.1: γv = 1 − γf (C.11-37); γf Mu se transmite por flexión según C.13.5.3 y γv Mu por excentricidad de cortante.)"
    ),
    "C.13.6.4.2": (
        "C.13.6.4.2 — Las franjas de columnas deben ser diseñadas para resistir las siguientes fracciones, en porcentaje, del momento negativo exterior mayorado. "
        "ℓ2/ℓ1 = 0.5 / 1.0 / 2.0. Con (αf1 ℓ2/ℓ1) = 0: βt = 0: 100 / 100 / 100; βt ≥ 2.5: 75 / 75 / 75. "
        "Con (αf1 ℓ2/ℓ1) ≥ 1.0: βt = 0: 100 / 100 / 100; βt ≥ 2.5: 90 / 75 / 45. "
        "Deben hacerse interpolaciones lineales entre los valores dados, donde βt = Ecb C / (2 Ecs Is) (C.13-5) y C = Σ (1 − 0.63 x/y) x³y/3 (C.13-6). "
        "La constante C para secciones en forma de T o L puede evaluarse dividiendo la sección en sectores rectangulares, como se define en C.13.2.4, y sumando los valores de C de cada porción. "
        "(C.13.6.4.1, momento negativo interior: ℓ2/ℓ1 = 0.5/1.0/2.0; (αf1 ℓ2/ℓ1) = 0: 75/75/75; (αf1 ℓ2/ℓ1) ≥ 1.0: 90/75/45. "
        "C.13.6.4.4, momentos positivos: (αf1 ℓ2/ℓ1) = 0: 60/60/60; ≥ 1.0: 90/75/45; interpolar linealmente.)"
    ),
    "C.10.10.4.1": (
        "C.10.10.4.1 — Se permite usar las siguientes propiedades para los elementos en la estructura: "
        "(a) Módulo de elasticidad: Ec de C.8.5.1. "
        "(b) Momentos de inercia, I. Elementos en compresión: Columnas 0.70 Ig; Muros – no agrietados 0.70 Ig; Muros – agrietados 0.35 Ig. "
        "Elementos a flexión: Vigas 0.35 Ig; Placas planas y losas planas 0.25 Ig. "
        "(c) Área: 1.0 Ag. "
        "Como alternativa, se permite que los momentos de inercia de los elementos sometidos a compresión y a flexión, I, se calculen como sigue. "
        "Elementos en compresión: I = (0.80 + 25 Ast/Ag) (1 − Mu/(Pu h) − 0.5 Pu/Po) Ig ≤ 0.875 Ig (C.10-8), "
        "donde Pu y Mu debe provenir de la combinación de carga particular en consideración, o la combinación de Pu y Mu que resulta del menor valor de I. "
        "No hay necesidad de usar un valor de I menor de 0.35 Ig. "
        "Elementos a flexión: I = (0.10 + 25 ρ) (1.2 − 0.2 bw/d) Ig ≤ 0.5 Ig (C.10-9). "
        "Para elementos continuos sometidos a flexión, se permite que I sea el promedio de los valores obtenidos de la ecuación (C.10-9) para secciones críticas de momento positivo y negativo. "
        "No hay necesidad de usar un valor de I menor de 0.25 Ig. "
        "Las dimensiones de la sección transversal de cada elemento usadas en el análisis no deben apartarse más del 10 por ciento de las dimensiones mostradas en los planos de construcción, de lo contrario debe repetirse el análisis."
    ),
}

EXTRA = [
    {
        "id": "NSR10-C-C_9_5_tabla_a_espesores_minimos",
        "seccion": "Tabla C.9.5(a)",
        "titulo": "Alturas o espesores mínimos de vigas no preesforzadas o losas reforzadas en una dirección a menos que se calculen las deflexiones",
        "texto": (
            "NSR-10 Título C, Capítulo C.9 — TABLA C.9.5(a) — Alturas o espesores mínimos de vigas no preesforzadas o losas reforzadas en una dirección "
            "a menos que se calculen las deflexiones. Espesor mínimo, h, para elementos que NO soporten o estén ligados a divisiones u otro tipo de elementos "
            "susceptibles de dañarse debido a deflexiones grandes (A = luz libre del elemento). "
            "Losas macizas en una dirección: simplemente apoyadas A/20; con un extremo continuo A/24; con ambos extremos continuos A/28; en voladizo A/10. "
            "Vigas o losas nervadas en una dirección: simplemente apoyadas A/16; con un extremo continuo A/18.5; con ambos extremos continuos A/21; en voladizo A/8. "
            "NOTAS: Los valores dados en esta tabla se deben usar directamente en elementos de concreto de peso normal y refuerzo grado 420 MPa. "
            "Para otras condiciones, los valores deben modificarse como sigue: "
            "(a) Para concreto liviano estructural con densidad wc dentro del rango de 1 440 a 1 840 kg/m3, los valores de la tabla deben multiplicarse por (1.65 − 0.0003 wc), pero no menos de 1.09. "
            "(b) Para fy distinto de 420 MPa, los valores de esta tabla deben multiplicarse por (0.4 + fy/700)."
        ),
    },
]

EXTRA2 = [
    {
        "id": "NSR10-C-C_9_5_tabla_b_deflexion_maxima_admisible",
        "seccion": "Tabla C.9.5(b)",
        "titulo": "Deflexión máxima admisible calculada",
        "texto": (
            "NSR-10 Título C, Capítulo C.9 — TABLA C.9.5(b) — Deflexión máxima admisible calculada (ℓ = luz). "
            "Cubiertas planas que no soporten ni estén ligadas a elementos no estructurales susceptibles de sufrir daños debido a deflexiones grandes: "
            "deflexión inmediata debida a la carga viva, L: límite ℓ/180 (este límite no es un resguardo contra el empozamiento de aguas, que se verifica aparte). "
            "Entrepisos que no soporten ni estén ligados a elementos no estructurales susceptibles de sufrir daños debido a deflexiones grandes: "
            "deflexión inmediata debida a la carga viva, L: límite ℓ/360. "
            "Sistema de entrepiso o cubierta que soporte o esté ligado a elementos no estructurales susceptibles de sufrir daños debido a deflexiones grandes: "
            "la parte de la deflexión total que ocurre después de la unión de los elementos no estructurales (la suma de la deflexión a largo plazo debida a todas las cargas permanentes, "
            "y la deflexión inmediata debida a cualquier carga viva adicional): límite ℓ/480 (se puede exceder si se toman medidas para prevenir daños en elementos apoyados o unidos). "
            "Sistema de entrepiso o cubierta que soporte o esté ligado a elementos no estructurales no susceptibles de sufrir daños: misma deflexión: límite ℓ/240 "
            "(pero no mayor que la tolerancia de los elementos no estructurales; se puede exceder con contraflecha). "
            "Las deflexiones a largo plazo se determinan según C.9.5.2.5 ó C.9.5.4.3 y pueden reducirse en la deflexión que ocurra antes de unir los elementos no estructurales."
        ),
    },
]

# Lote 3 (2026-11-08): ecuaciones Ash (C.21-7/-8) que faltaban en el corpus y definición de Mpr, transcritas de la imagen de la página.
EXTRA3 = [
    {
        "id": "NSR10-C-C_21_6_4_4", "seccion": "C.21.6.4.4",
        "titulo": "Refuerzo transversal de columnas DES: ρs y Ash (C.21-6, C.21-7, C.21-8)",
        "texto": (
            "NSR-10 Título C C.21.6.4.4 — Debe proporcionarse refuerzo transversal en las cantidades que se especifican de (a) o (b), a menos que en C.21.6.5 se exija mayor cantidad. "
            "(a) La cuantía volumétrica de refuerzo en espiral o de estribos cerrados de confinamiento circulares, ρs, no debe ser menor que la requerida por la ecuación "
            "ρs = 0.12 f'c / fyt (C.21-6) y no debe ser menor que la requerida por la ecuación (C.10-5). "
            "(b) El área total de la sección transversal del refuerzo de estribos cerrados de confinamiento rectangulares, Ash, no debe ser menor que la requerida por las ecuaciones "
            "Ash = 0.3 (s bc f'c / fyt) [ (Ag / Ach) − 1 ] (C.21-7) y Ash = 0.09 s bc f'c / fyt (C.21-8). "
            "(s = separación del refuerzo transversal; bc = dimensión de la sección del núcleo medida centro a centro del refuerzo de confinamiento; Ach = área del núcleo medida al borde exterior del refuerzo transversal.) "
            "Complemento verificado: C.21.6.4.3 — la separación del refuerzo transversal no debe exceder la menor de (a) un cuarto de la dimensión mínima del elemento, (b) seis veces el diámetro de la barra longitudinal menor, "
            "(c) so = 100 + (350 − hx)/3 (C.21-5), con so no mayor a 150 mm y no menor a 100 mm. "
            "C.21.6.4.1 — ℓo no menor que la mayor de: altura del elemento en la cara del nudo, un sexto de la luz libre, y 450 mm. "
            "C.21.6.4.2 — hx (separación entre ramas o ganchos suplementarios) no debe exceder 350 mm centro a centro. "
            "C.21.6.4.5 — más allá de ℓo, estribos con separación no mayor que seis veces el diámetro de las barras longitudinales de la columna o 150 mm."
        ),
    },
    {
        "id": "NSR10-C-C_21_5_4_1", "seccion": "C.21.5.4.1",
        "titulo": "Cortante de diseño de vigas DES con Mpr y refuerzo transversal",
        "texto": (
            "NSR-10 Título C C.21.5.4 — Requisitos de resistencia a cortante. C.21.5.4.1 — Fuerzas de diseño. La fuerza cortante de diseño, Ve, se debe determinar a partir de las fuerzas estáticas "
            "en la parte del elemento comprendida entre las caras del nudo. Se debe suponer que en las caras de los nudos localizados en los extremos del elemento actúan momentos de signo opuesto "
            "correspondientes a la resistencia probable, Mpr, y que el elemento está además cargado con cargas aferentes gravitacionales mayoradas a lo largo de la luz. "
            "C.21.5.4.2 — Refuerzo transversal. El refuerzo transversal en los lugares identificados en C.21.5.3.1 debe diseñarse para resistir cortante suponiendo Vc = 0 cuando se produzcan simultáneamente "
            "(a) la fuerza cortante inducida por el sismo calculada de acuerdo con C.21.5.4.1 representa la mitad o más de la resistencia máxima a cortante requerida en esas zonas; y "
            "(b) la fuerza axial de compresión mayorada, Pu, incluyendo los efectos sísmicos es menor que Ag f'c / 20."
        ),
    },
    {
        "id": "NSR10-C-C_2_2_Mpr_definicion", "seccion": "C.2.2",
        "titulo": "Notación Mpr: resistencia probable a la flexión",
        "texto": (
            "NSR-10 Título C, Capítulo C.2 (Notación) — Mpr = resistencia probable a la flexión de los elementos, con o sin carga axial, determinada usando las propiedades de los elementos "
            "en las caras de los nudos suponiendo un esfuerzo en tracción para las barras longitudinales de al menos 1.25 fy y un factor de reducción de la resistencia φ de 1.0, N·mm (Capítulo C.21). "
            "Ve = fuerza cortante de diseño correspondiente al desarrollo de la resistencia probable a momento del elemento, N (véanse C.21.5.4.1 y C.21.6.5.1). "
            "C.21.7.2.1 — las fuerzas en el refuerzo longitudinal de vigas en la cara del nudo se determinan suponiendo que el esfuerzo en el refuerzo de tracción por flexión es 1.25 fy."
        ),
    },
]
SUB_VIEJOS_3 = ["NSR10-C-C_21_6_4_4-sub%"]


def construir(lote: int = 1) -> list[dict]:
    chunks = []
    for numeral, pdf in (OBJETIVOS if lote == 1 else OBJETIVOS_LOTE2 if lote == 2 else {}).items():
        texto = MANUAL.get(numeral) or extraer(numeral, pdf)
        chunks.append({
            "id": f"NSR10-C-{numeral.replace('.', '_')}",
            "capitulo": CAPITULO,
            "seccion": numeral,
            "titulo": texto[:60],
            "texto": f"NSR-10 Título C {texto}",
        })
    chunks += [{"capitulo": CAPITULO, **e} for e in {1: EXTRA, 2: EXTRA2, 3: EXTRA3}[lote]]
    return chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--lote", type=int, default=1, choices=(1, 2, 3))
    args = ap.parse_args()
    chunks = construir(args.lote)
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto']}\n")
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
    for c in chunks:
        piezas = _sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)
        for k, p in enumerate(piezas):
            filas.append({**c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p,
                          "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")
    if args.lote == 3:
        for patron in SUB_VIEJOS_3:
            sb.table("nsr10_chunks").delete().like("id", patron).execute()
    if args.lote == 2:  # borrar los trozos viejos «-subN» solo tras el upsert exitoso
        for patron in SUB_VIEJOS.values():
            sb.table("nsr10_chunks").delete().like("id", patron).execute()


if __name__ == "__main__":
    main()
