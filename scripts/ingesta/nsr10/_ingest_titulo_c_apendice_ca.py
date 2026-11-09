"""Apéndice C-A (Modelos puntal-tensor) del Título C de la NSR-10, verbatim del Reglamento (sin Comentario).

Fuente: `raw/NSR-10-525-528.pdf` (4 páginas, capa de texto; numeradas C-223 a C-226 en ese archivo), leído el 2026-11-08. Las ecuaciones (C-A-4) y
(C-A-6) se contrastaron contra la imagen de las páginas porque el texto plano las desordena. Ecuaciones en notación lineal; subíndices con guion bajo.
La norma contiene erratas de rotulación que se conservan tal cual y se señalan entre corchetes como nota del transcriptor: la ecuación (A-7) es la
(C-A-7); "C.A.1" en C-A.2.1 es C-A.1; "C.3.2.2(a)" en C-A.3.3 es C-A.3.2.2(a).
Convención de id: NSR10-C-C_A_<numeral con guion bajo>. Solo agrega filas (upsert por id).
Uso: python _ingest_titulo_c_apendice_ca.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
CAPITULO = "C"
P = "NSR-10 Título C, Apéndice C-A (Modelos puntal-tensor) "


def _c(num: str, titulo: str, texto: str) -> dict:
    return {"id": "NSR10-C-C_A_" + num.replace("C-A.", "").replace(".", "_"), "seccion": num, "titulo": titulo, "texto": P + f"{num} ({titulo}) — " + texto}


CHUNKS = [
    _c("C-A.1", "Definiciones del apéndice C-A",
       "Definiciones. Discontinuidad (Discontinuity): cambio abrupto en la geometría o en la carga. "
       "Modelo puntal-tensor (Strut-and-tie model): un modelo de cercha de un elemento estructural, o de una región-D de ese elemento, hecho con puntales y tensores "
       "conectados en los nodos, capaces de transferir las cargas mayoradas a los apoyos o hacia las regiones-B adyacentes. "
       "Nodo (Node): en un modelo puntal-tensor, donde se intersectan los ejes de los puntales, tensores y fuerzas concentradas que actúan en el nodo. "
       "Puntal (Strut): un elemento a compresión en el modelo puntal-tensor. Un puntal representa la resultante de un campo de compresión paralelo o en forma de abanico. "
       "Puntal en forma de botella (Bottle-shaped strut): un puntal que es más ancho en el centro que en sus extremos. "
       "Región-B (B-region): parte de un elemento en la que pueden aplicarse las suposiciones de secciones planas, mencionadas de la teoría de flexión en C.10.2.2. "
       "Región-D (D-region): la parte de un elemento dentro de una distancia h de una discontinuidad de fuerza o geométrica. "
       "Tensor (Tie): un elemento a tracción en el modelo puntal-tensor. "
       "Viga alta (Deep beam): véanse C.10.7.1 y C.11.7.1. "
       "Zona nodal (Nodal zone): el volumen de concreto alrededor de un nodo que se supone transfiere las fuerzas de los puntales y tensores a través del nodo."),
    _c("C-A.2.1", "Procedimiento de diseño: modelo de cercha idealizada",
       "Procedimiento de diseño del modelo puntal-tensor. Se permite diseñar elementos de concreto estructural, o regiones-D en estos elementos, modelando el elemento o región "
       "como una cercha idealizada. El modelo de cercha debe contener puntales, tensores y nodos, como se define en C.A.1 [nota del transcriptor: la norma dice \"C.A.1\"; se refiere a C-A.1]. "
       "El modelo de cercha debe ser capaz de transferir todas las cargas mayoradas hacia los apoyos o regiones-B adyacentes."),
    _c("C-A.2.2", "Equilibrio del modelo puntal-tensor",
       "El modelo puntal-tensor debe estar en equilibrio con las cargas aplicadas y las reacciones."),
    _c("C-A.2.3", "Geometría de la cercha: dimensiones de puntales, tensores y zonas nodales",
       "Para determinar la geometría de la cercha, se deben considerar las dimensiones de los puntales, tensores y zonas nodales."),
    _c("C-A.2.4", "Cruce de tensores y puntales",
       "Se permite que los tensores atraviesen los puntales. Los puntales deben cruzarse o superponerse sólo en los nodos."),
    _c("C-A.2.5", "Ángulo mínimo entre puntal y tensor: 25 grados",
       "El ángulo, θ, entre los ejes de cualquier puntal y de cualquier tensor entrando en un solo nodo no debe ser menor de 25°."),
    _c("C-A.2.6", "Criterio de diseño φFn ≥ Fu (ecuación C-A-1)",
       "El diseño de los puntales, tensores y zonas nodales debe basarse en: φFn ≥ Fu (C-A-1), donde Fu es la fuerza mayorada que actúa en un puntal o en un tensor, "
       "o en una cara de una zona nodal; Fn es la resistencia nominal del puntal, tensor o zona nodal; φ está especificado en C.9.3.2.6."),
    _c("C-A.3.1", "Resistencia nominal a la compresión de un puntal sin refuerzo longitudinal (C-A-2)",
       "Resistencia de los puntales. La resistencia nominal a la compresión de un puntal sin refuerzo longitudinal, Fns, debe tomarse como el menor valor de "
       "Fns = fce·Acs (C-A-2) en los dos extremos del puntal, donde Acs es el área de la sección transversal en un extremo del puntal, y fce es el menor valor entre "
       "(a) la resistencia efectiva a la compresión del concreto en el puntal dado en C-A.3.2, (b) la resistencia efectiva a la compresión en el concreto en la zona nodal dada en C-A.5.2."),
    _c("C-A.3.2", "Resistencia efectiva del concreto en el puntal: fce = 0.85·βs·f'c y valores de βs",
       "La resistencia efectiva a la compresión del concreto, fce, en un puntal debe ser tomada como fce = 0.85·βs·f'c (C-A-3). "
       "C-A.3.2.1 — Para un puntal de sección transversal uniforme a lo largo de su longitud: βs = 1.0. "
       "C-A.3.2.2 — Para los puntales ubicados de tal manera que el ancho de la sección media del puntal es mayor que el ancho en los nodos (puntales en forma de botella): "
       "(a) con refuerzo que cumpla con C-A.3.3: βs = 0.75; (b) sin refuerzo que cumpla con C-A.3.3: βs = 0.60λ, donde λ está definido en C.8.6.1. "
       "C-A.3.2.3 — Para los puntales en elementos sometidos a tracción, o alas en tracción de los elementos: βs = 0.40. "
       "C-A.3.2.4 — Para todos los demás casos: βs = 0.60λ."),
    _c("C-A.3.3", "Refuerzo transversal que cruza el puntal en botella; ecuación C-A-4 y disposición",
       "Si se emplea el valor de βs especificado en C.3.2.2(a) [nota del transcriptor: se refiere a C-A.3.2.2(a)], el eje del puntal debe ser cruzado por el refuerzo diseñado "
       "para resistir la fuerza de tracción transversal resultante de la expansión de la fuerza de compresión en el puntal. Se permite suponer que la fuerza de compresión se expande "
       "en los puntales con una pendiente de 2 longitudinal a 1 transversal al eje del puntal. "
       "C-A.3.3.1 — Para un f'c no mayor a 40 MPa, se admite que las disposiciones de C-A.3.3 se satisfacen cuando el eje del puntal es cruzado por filas de refuerzo que cumplen "
       "la ecuación (C-A-4): Σ (Asi / (bs·si)) · sen αi ≥ 0.003, donde Asi es el área total del refuerzo de superficie con un espaciamiento si en la capa i de refuerzo con barras a un "
       "ángulo αi con respecto al eje del puntal. "
       "C-A.3.3.2 — El refuerzo exigido en C-A.3.3 debe colocarse en alguna de las siguientes formas: en direcciones ortogonales en ángulos α1 y α2 con respecto al eje del puntal, "
       "o en una dirección en un ángulo α con respecto al eje del puntal. Si el refuerzo se coloca en una sola dirección, α no debe ser menor de 40°."),
    _c("C-A.3.4", "Resistencia incrementada del puntal por confinamiento",
       "Si se encuentra documentado mediante ensayos y análisis, se permite usar una resistencia efectiva a la compresión incrementada del puntal debido al refuerzo de confinamiento."),
    _c("C-A.3.5", "Puntal con refuerzo de compresión longitudinal (C-A-5)",
       "Se permite el uso de refuerzo de compresión para aumentar la resistencia de un puntal. El refuerzo de compresión debe colocarse dentro de él, paralelo al eje del puntal, "
       "anclarse adecuadamente, y rodearse por estribos o espirales que cumplan con C.7.10. En estos casos, la resistencia nominal de un puntal reforzado longitudinalmente es: "
       "Fns = fce·Acs + A's·f's (C-A-5)."),
    _c("C-A.4.1", "Resistencia nominal de un tensor Fnt (C-A-6)",
       "Resistencia de los tensores. La resistencia nominal de un tensor, Fnt, debe calcularse como Fnt = Ats·fy + Atp·(fse + Δfp) (C-A-6), donde (fse + Δfp) no debe exceder fpy, "
       "y Atp es igual a cero para los elementos no preesforzados. En la ecuación (C-A-6), se permite tomar Δfp igual a 420 MPa para el refuerzo preesforzado adherido, "
       "o 70 MPa para el refuerzo preesforzado no adherido. Se permiten otros valores de Δfp cuando se justifiquen por medio de análisis."),
    _c("C-A.4.2", "Eje del refuerzo del tensor",
       "El eje del refuerzo en un tensor debe coincidir con el eje del tensor en el modelo puntal-tensor."),
    _c("C-A.4.3", "Anclaje del refuerzo del tensor en la zona nodal",
       "El refuerzo del tensor debe anclarse mediante dispositivos mecánicos, dispositivos de anclaje postensados, ganchos estándar o mediante el desarrollo de barra rectas, "
       "como lo exigen C-A.4.3.1 a C-A.4.3.4. "
       "C-A.4.3.1 — Las zonas nodales deben desarrollar la diferencia entre la fuerza en el tensor en un lado del nodo y la fuerza en el tensor en el otro lado del nodo. "
       "C-A.4.3.2 — En las zonas nodales que anclan un solo tensor, la fuerza en el tensor debe desarrollarse en el punto donde el centroide del refuerzo del tensor sale de la zona nodal "
       "extendida y entra en la luz del elemento. "
       "C-A.4.3.3 — En las zonas nodales que anclan dos o más tensores, la fuerza del tensor en cada dirección debe desarrollarse en el punto donde el centroide del refuerzo del tensor "
       "sale de la zona nodal extendida. "
       "C-A.4.3.4 — El refuerzo transversal requerido por C-A.3.3 debe anclarse de acuerdo con C.12.13."),
    _c("C-A.5.1", "Resistencia nominal a la compresión de una zona nodal Fnn (C-A-7)",
       "Resistencia de las zonas nodales. La resistencia nominal a la compresión de una zona nodal, Fnn, debe ser Fnn = fce·Anz (A-7) [nota del transcriptor: la norma rotula esta "
       "ecuación (A-7); corresponde a C-A-7], donde fce es la resistencia efectiva a la compresión del concreto en una zona nodal, como se da en C-A.5.2 y Anz es la menor de "
       "(a) el área de la cara de una zona nodal en donde actúa Fu, tomada en forma perpendicular a la línea de acción de Fu, o "
       "(b) el área de una sección a través de la zona nodal, tomada en forma perpendicular a la línea de acción de la fuerza resultante en la sección."),
    _c("C-A.5.2", "Resistencia efectiva en la zona nodal fce = 0.85·βn·f'c y valores de βn (nodos CCC, CCT, CTT)",
       "A menos que se coloque refuerzo de confinamiento dentro de la zona nodal y que sus efectos sean respaldados por ensayos y análisis, los esfuerzos de compresión efectivos, fce, "
       "calculados en una cara de una zona nodal debidos a las fuerzas del modelo puntal-tensor, no deben exceder el valor dado por: fce = 0.85·βn·f'c (C-A-8), "
       "donde el valor de βn está dado en C-A.5.2.1 a C-A.5.2.3. "
       "C-A.5.2.1 — En zonas nodales limitadas por puntales o áreas de apoyo, o ambas: βn = 1.0. "
       "C-A.5.2.2 — En zonas nodales que anclan un tensor: βn = 0.80. "
       "C-A.5.2.3 — En zonas nodales que anclan dos o más tensores: βn = 0.60."),
    _c("C-A.5.3", "Modelo puntal-tensor tridimensional: caras de zonas nodales",
       "En un modelo puntal-tensor tridimensional, el área de cada cara de una zona nodal no debe ser menor a la dada en C-A.5.1, y la forma de cada cara de las zonas nodales debe ser "
       "similar a la forma de la proyección del extremo de los puntales sobre las caras correspondientes de las zonas nodales."),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ids = [c["id"] for c in CHUNKS]
    assert len(ids) == len(set(ids)), "ids duplicados"
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
            # las partes posteriores a la primera pierden el encabezado: se les repite el numeral y su título para que el embedding conserve el tema
            if k > 0:
                p = f"{P}{c['seccion']} ({c['titulo']}), continuación — " + p
            filas.append({"capitulo": CAPITULO, **c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p,
                          "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
