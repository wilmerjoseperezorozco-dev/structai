"""
NSR-10 Titulo C, numerales hoja reales confirmados sin chunk propio en
la re-auditoria estricta 2026-09-09 (ver docs/fuentes-normativas.md,
fila de Titulo C, ~41 de 1.814 numerales, ~2,3%).

De los 41 candidatos del diff crudo, 26 se confirmaron con spot-check
leyendo el PDF real (encabezado + contenido verbatim localizado). Los
15 restantes se descartaron tras verificacion adicional:
- C.9.2.5, C.9.2.6, C.9.2.7: el capitulo C.9.2 real salta de C.9.2.4
  directo a C.9.3 -- no existen como numerales propios.
- C.8.5.4, C.8.5.5, C.8.5.12: citados desde el Apendice C-G
  (nomenclatura y alcance del metodo alterno de diseno) como remision a
  Ec/Es/una excepcion, pero el C.8.5 real del cuerpo principal solo
  tiene 3 sub-numerales (C.8.5.1=Ec, C.8.5.2=Es, C.8.5.3=Ep) -- las
  citas del apendice usan una numeracion que no corresponde a este
  Titulo C (posible inconsistencia del documento fuente, no un hueco
  de ingesta: el contenido de Ec/Es ya esta cubierto bajo C.8.5.1/
  C.8.5.2).
- C.11.6.6.2, C.11.7.4.3, C.11.12.3, C.12.3.2.5, C.13.2.6, C.21.2.1.6,
  C.21.2.6, C.21.7.6.2, C.21.7.6.3: solo aparecen como remision cruzada
  desde otro numeral, nunca localizados como encabezado propio en
  ninguno de los 29 PDF fuente -- mismo tratamiento honesto que
  E.7.26.2/C.10.17 en auditorias anteriores, no se ingesta contenido
  sin poder verificarlo.

Hallazgo mas valioso: el capitulo C.18.5 (Esfuerzos admisibles en el
acero de preesforzado) tiene contenido real completo sin ningun chunk
en produccion.

Fuente: PDFs de la auditoria original de Titulo C (29 archivos,
scripts/ingesta/nsr10/raw/, gitignored), paginas confirmadas leyendo
visualmente cada una.

Uso: python _ingest_titulo_c_26_numerales_faltantes.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título C — Concreto Estructural"

CHUNKS = [
    {
        "id": "NSR10-C-C_3_6_1_aditivos",
        "seccion": "C.3.6.1 (Aditivos para Reducción de Agua y Modificación de Fraguado)",
        "titulo": "Normas técnicas (NTC 1299/ASTM C494M, NTC 4023/ASTM C1017M) exigidas para aditivos reductores de agua y de fraguado o concreto fluido.",
        "texto": (
            "NSR-10 Título C, Capítulo C.3 — C.3.6.1 — Los aditivos para "
            "reducción de agua y modificación del tiempo de fraguado deben "
            "cumplir con la norma NTC 1299 (ASTM C494M). Los aditivos para "
            "producir concreto fluido deben cumplir la norma NTC 4023 (ASTM "
            "C1017M)."
        ),
    },
    {
        "id": "NSR10-C-C_6_3_6_1_ductos_no_corrosion",
        "seccion": "C.6.3.6.1 (Ductos/Tuberías Embebidas Sustituyendo Concreto — Requisito de No Corrosión)",
        "titulo": "Condición para que ductos y tuberías embebidas sustituyan estructuralmente al concreto desplazado: no exposición a corrosión.",
        "texto": (
            "NSR-10 Título C, Capítulo C.6 — C.6.3.6.1 — No estén expuestas a "
            "la corrosión o a otra causa de deterioro."
        ),
    },
    {
        "id": "NSR10-C-C_7_10_4_6_espirales_extension",
        "seccion": "C.7.10.4.6 (Extensión de Espirales desde la Zapata)",
        "titulo": "Requisito de extender las espirales desde la parte superior de la zapata hasta la altura del refuerzo horizontal más bajo del elemento soportado.",
        "texto": (
            "NSR-10 Título C, Capítulo C.7 — C.7.10.4.6 — Las espirales deben "
            "extenderse desde la parte superior de la zapata o losa en "
            "cualquier nivel, hasta la altura del refuerzo horizontal más bajo "
            "del elemento soportado."
        ),
    },
    {
        "id": "NSR10-C-C_7_12_3_2_espaciamiento_tendones",
        "seccion": "C.7.12.3.2 (Espaciamiento Máximo entre Tendones de Retracción y Temperatura)",
        "titulo": "Límite de 1.8 m para el espaciamiento entre tendones de acero de preesforzado usados como refuerzo de retracción y temperatura.",
        "texto": (
            "NSR-10 Título C, Capítulo C.7 — C.7.12.3.2 — El espaciamiento "
            "entre los tendones no debe exceder 1.8 m."
        ),
    },
    {
        "id": "NSR10-C-C_8_10_1_diseno_columnas",
        "seccion": "C.8.10.1 (Diseño de Columnas para Fuerzas Axiales y Momentos Mayorados)",
        "titulo": "Requisito de diseñar columnas para las fuerzas axiales mayoradas de todos los pisos y considerar la condición de máxima relación momento/carga axial.",
        "texto": (
            "NSR-10 Título C, Capítulo C.8 — C.8.10.1 — Las columnas se deben "
            "diseñar para resistir las fuerzas axiales que provienen de las "
            "cargas mayoradas de todos los pisos o cubierta, y el momento "
            "máximo debido a las cargas mayoradas en un solo vano adyacente "
            "del entrepiso o cubierta bajo consideración. También debe "
            "considerarse la condición de carga que produzca la máxima "
            "relación entre momento y carga axial."
        ),
    },
    {
        "id": "NSR10-C-C_9_3_2_3_factor_reduccion_cortante_torsion",
        "seccion": "C.9.3.2.3 (Factor de Reducción de Resistencia φ para Cortante y Torsión)",
        "titulo": "Valor φ = 0.75 para el factor de reducción de resistencia en cortante y torsión, dentro de la tabla C.9.3.2.1-C.9.3.2.7.",
        "texto": (
            "NSR-10 Título C, Capítulo C.9 — C.9.3.2 — El factor de reducción "
            "de resistencia, φ, debe ser el dado en C.9.3.2.1 a C.9.3.2.7: "
            "C.9.3.2.3 — Cortante y torsión ... φ = 0.75."
        ),
    },
    {
        "id": "NSR10-C-C_11_3_2_cortante_preesforzados",
        "seccion": "C.11.3.2 (Resistencia al Cortante Vc en Elementos Preesforzados)",
        "titulo": "Ecuación C.11-9 para Vc en elementos con fuerza efectiva de preesforzado ≥40% de la resistencia a tracción del refuerzo de flexión.",
        "texto": (
            "NSR-10 Título C, Capítulo C.11 — C.11.3.2 — Para elementos que "
            "tengan una fuerza efectiva de preesforzado no menor al 40 por "
            "ciento de la resistencia a la tracción del refuerzo de flexión, a "
            "menos que se efectúe un cálculo más detallado de acuerdo con "
            "C.11.3.3, Vc = (0.05λ√f'c + 4.8·Vu·dp/Mu)·bw·d (C.11-9), pero no "
            "es necesario considerar a Vc menor que 0.17λ√f'c·bw·d. Vc no debe "
            "tomarse mayor que 0.42λ√f'c·bw·d ni que el valor dado en C.11.3.4 "
            "u C.11.3.5. Vu·dp/Mu no se debe tomar mayor que 1.0, donde Mu "
            "ocurre simultáneamente con Vu."
        ),
    },
    {
        "id": "NSR10-C-C_11_7_6_refuerzo_alternativo_vigas_altas",
        "seccion": "C.11.7.6 (Refuerzo Mínimo Alternativo en Vigas Altas)",
        "titulo": "Permiso de diseñar el refuerzo horizontal/vertical mínimo de vigas altas cumpliendo el Apéndice C-A.3.3 en vez de C.11.7.4/C.11.7.5.",
        "texto": (
            "NSR-10 Título C, Capítulo C.11 — C.11.7.6 — Se permite diseñar el "
            "refuerzo cumpliendo con las disposiciones de C-A.3.3 en lugar del "
            "refuerzo horizontal y vertical mínimo especificado en C.11.7.4 y "
            "C.11.7.5."
        ),
    },
    {
        "id": "NSR10-C-C_12_14_3_2_empalme_mecanico_completo",
        "seccion": "C.12.14.3.2 (Desarrollo Mínimo de un Empalme Mecánico Completo)",
        "titulo": "Requisito de desarrollar al menos 1.25fy de la barra, en tracción o compresión, para un empalme mecánico completo.",
        "texto": (
            "NSR-10 Título C, Capítulo C.12 — C.12.14.3.2 — Un empalme "
            "mecánico completo debe desarrollar en tracción o compresión, "
            "según sea requerido, al menos 1.25fy de la barra."
        ),
    },
    {
        "id": "NSR10-C-C_13_5_3_3_incremento_gamma_f",
        "seccion": "C.13.5.3.3 (Incremento del Factor γf para Momentos No Balanceados en Columnas de Borde)",
        "titulo": "Condiciones (a)/(b) para aumentar γf hasta 1.25 veces en columnas de borde e interiores, con límite de deformación unitaria y remisión a C.11.11.2.1.",
        "texto": (
            "NSR-10 Título C, Capítulo C.13 — C.13.5.3.3 — Para losas no "
            "preesforzadas con momentos no balanceados transferidos entre la "
            "losa y las columnas, se permite aumentar el valor de γf dado en "
            "la ecuación (C.13-1) de acuerdo a lo siguiente: (a) Para columnas "
            "de borde con momentos no balanceados alrededor de un eje paralelo "
            "al borde, γf = 1.0 siempre que Vu en el borde de apoyo no exceda "
            "0.75φVc, o en una esquina de apoyo no exceda 0.5φVc. (b) Para "
            "momentos no balanceados en apoyos interiores, y para columnas de "
            "borde con momentos no balanceados alrededor de un eje "
            "perpendicular al borde, se permite que γf sea incrementado hasta "
            "en 1.25 veces el valor dado en la ecuación (C.13-1), pero no más "
            "de γf = 1.0, siempre que el Vu en el apoyo no exceda 0.4φVc. La "
            "deformación unitaria neta a tracción εt calculada para el ancho "
            "efectivo de losa, definido en C.13.5.3.2, no debe ser menor de "
            "0.010. El valor de Vc en las letras (a) y (b) deben calcularse de "
            "acuerdo con C.11.11.2.1."
        ),
    },
    {
        "id": "NSR10-C-C_13_7_2_1_portico_equivalente_definicion",
        "seccion": "C.13.7.2.1 (Definición del Pórtico Equivalente)",
        "titulo": "Definición del pórtico equivalente como estructura constituida por pórticos a lo largo de los ejes de columnas longitudinales y transversales.",
        "texto": (
            "NSR-10 Título C, Capítulo C.13 — C.13.7.2 — Pórtico equivalente — "
            "C.13.7.2.1 — Debe considerarse que la estructura está constituida "
            "por pórticos equivalentes a lo largo de los ejes de columnas "
            "longitudinales y transversales a lo largo de toda la estructura."
        ),
    },
    {
        "id": "NSR10-C-C_13_9_1_2_minimo_nervaduras",
        "seccion": "C.13.9.1.2 (Número Mínimo de Nervaduras en Losas Nervadas Apoyadas en Muros/Vigas Rígidas)",
        "titulo": "Requisito de al menos cinco nervaduras por dirección para aplicar el método de losas en dos direcciones apoyadas sobre muros o vigas rígidas.",
        "texto": (
            "NSR-10 Título C, Capítulo C.13 — C.13.9.1.2 — Cuando se trate de "
            "losas nervadas, el mínimo número de nervaduras en cada dirección "
            "debe ser mayor o igual a cinco, para poder aplicar el método de "
            "esta sección."
        ),
    },
    {
        "id": "NSR10-C-C_13_9_5_2_seccion_critica_momento_positivo",
        "seccion": "C.13.9.5.2 (Sección Crítica para Momento Positivo)",
        "titulo": "Ubicación de la sección crítica de momento positivo: el centro de los paneles.",
        "texto": (
            "NSR-10 Título C, Capítulo C.13 — C.13.9.5 — Las secciones "
            "críticas para momento, en cualquiera de las dos direcciones, son "
            "las siguientes: C.13.9.5.1 — Para momentos negativos los bordes "
            "de los paneles en las caras de los apoyos. C.13.9.5.2 — Para "
            "momento positivo los centros de los paneles."
        ),
    },
    {
        "id": "NSR10-C-C_13_9_8_distribucion_momento_negativo_desbalanceado",
        "seccion": "C.13.9.8 (Distribución del Momento Negativo Desbalanceado entre Paneles Adyacentes)",
        "titulo": "Regla de distribución proporcional a la rigidez a flexión cuando el momento negativo de un lado del apoyo es menos del 80% del otro lado.",
        "texto": (
            "NSR-10 Título C, Capítulo C.13 — C.13.9.8 — Cuando el momento "
            "negativo en un lado del apoyo sea menos del 80% del "
            "correspondiente al otro lado del apoyo, la diferencia debe "
            "distribuirse en proporción a la rigidez a flexión relativa de las "
            "losas."
        ),
    },
    {
        "id": "NSR10-C-C_14_8_2_3_muro_controlado_traccion",
        "seccion": "C.14.8.2.3 (Requisito de Control por Tracción en Muros Esbeltos)",
        "titulo": "Condición de que el muro esté controlado por tracción, dentro del diseño alternativo para muros esbeltos (C.14.8.2.1 a C.14.8.2.6).",
        "texto": (
            "NSR-10 Título C, Capítulo C.14 — C.14.8.2 — Los muros diseñados "
            "de acuerdo con las disposiciones de C.14.8 deben cumplir C.14.8.2.1 "
            "a C.14.8.2.6 ... C.14.8.2.3 — El muro debe estar controlado por "
            "tracción."
        ),
    },
    {
        "id": "NSR10-C-C_15_5_3_cabezal_pilotes_distancia",
        "seccion": "C.15.5.3 (Cabezal de Pilotes según Distancia Eje-Columna)",
        "titulo": "Requisitos diferenciados de cortante para cabezales de pilotes según la distancia entre el eje del pilote y el eje de la columna, con remisión al Apéndice C-A.",
        "texto": (
            "NSR-10 Título C, Capítulo C.15 — C.15.5.3 — Cuando la distancia "
            "entre el eje de cualquier pilote y el eje de la columna es mayor "
            "a dos veces la distancia entre la parte superior del cabezal de "
            "los pilotes y la parte superior del pilote, el cabezal de los "
            "pilotes debe cumplir con C.11.11 y C.15.5.4. Otros cabezales de "
            "pilotes deben cumplir ya sea con el Apéndice C-A, o ambos, "
            "C.11.11 y C.15.5.4. Si se usa el Apéndice C-A, la resistencia a "
            "la compresión efectiva del concreto de los puntales, fce, debe "
            "determinarse usando C-A.3.2.2(b)."
        ),
    },
    {
        "id": "NSR10-C-C_18_3_2_2_secciones_fisuradas",
        "seccion": "C.18.3.2.2 (Suposición de Diseño: el Concreto No Resiste Tracción en Secciones Fisuradas)",
        "titulo": "Suposición de teoría elástica para el estudio de esfuerzos en transferencia del preesfuerzo: en secciones fisuradas el concreto no resiste tracción.",
        "texto": (
            "NSR-10 Título C, Capítulo C.18 — C.18.3.2 — Para el estudio de "
            "los esfuerzos en transferencia del preesforzado, bajo cargas de "
            "servicio y en el estado correspondiente a cargas de fisuración, "
            "se debe emplear la teoría elástica con las suposiciones de "
            "C.18.3.2.1 y C.18.3.2.2. C.18.3.2.1 — Las deformaciones unitarias "
            "varían linealmente con la altura en todas las etapas de carga. "
            "C.18.3.2.2 — En las secciones fisuradas el concreto no resiste "
            "tracción."
        ),
    },
    {
        "id": "NSR10-C-C_18_5_esfuerzos_admisibles_preesforzado",
        "seccion": "C.18.5 y C.18.5.1 (Esfuerzos Admisibles en el Acero de Preesforzado)",
        "titulo": "Capítulo completo: límites de esfuerzo de tracción admisible en el acero de preesforzado según la etapa de carga (gato, transferencia, tendones postensados).",
        "texto": (
            "NSR-10 Título C, Capítulo C.18 — C.18.5 — ESFUERZOS ADMISIBLES EN "
            "EL ACERO DE PREESFORZADO — C.18.5.1 — Los esfuerzos de tracción "
            "en el acero de preesforzado no deben exceder: (a) Debido a la "
            "fuerza del gato de preesforzado ... 0.94fpy pero no mayor que el "
            "mínimo entre 0.80fpu y el máximo valor recomendado por el "
            "fabricante del acero de preesforzado o de los dispositivos de "
            "anclaje. (b) Inmediatamente después de la transferencia del "
            "preesfuerzo ... 0.82fpy pero no mayor que 0.74fpu. (c) Tendones "
            "de postensado, en anclajes y acoples, inmediatamente después de "
            "transferencia ... 0.70fpu."
        ),
    },
    {
        "id": "NSR10-C-C_18_18_2_2_agua_mortero_inyeccion",
        "seccion": "C.18.18.2.2 (Requisitos del Agua para Mortero de Inyección de Tendones Adheridos)",
        "titulo": "Remisión del agua usada en el mortero de inyección de tendones adheridos a los requisitos de C.3.4.",
        "texto": (
            "NSR-10 Título C, Capítulo C.18 — C.18.18.2 — Los materiales para "
            "el mortero de inyección deben cumplir con lo especificado en "
            "C.18.18.2.1 a C.18.18.2.4 ... C.18.18.2.2 — El agua debe cumplir "
            "con los requisitos de C.3.4."
        ),
    },
    {
        "id": "NSR10-C-C_21_4_4_4_seccion_21_9_9_no_aplica_muros",
        "seccion": "C.21.4.4.4 (Exención de la Sección C.21.9.9 para Muros con DMO)",
        "titulo": "Exención de cumplir la sección C.21.9.9 para muros con capacidad moderada de disipación de energía (DMO).",
        "texto": (
            "NSR-10 Título C, Capítulo C.21 — C.21.4.4.4 — La sección C.21.9.9 "
            "no hay necesidad de cumplirla."
        ),
    },
    {
        "id": "NSR10-C-C_21_7_2_1_fuerza_refuerzo_nudo",
        "seccion": "C.21.7.2.1 (Fuerza de Diseño en el Refuerzo Longitudinal de Vigas en la Cara del Nudo)",
        "titulo": "Requisito de determinar las fuerzas en el refuerzo longitudinal de vigas en la cara del nudo suponiendo una resistencia de 1.25fy en tracción por flexión.",
        "texto": (
            "NSR-10 Título C, Capítulo C.21 — C.21.7.2 — Requisitos generales "
            "— C.21.7.2.1 — Las fuerzas en el refuerzo longitudinal de vigas "
            "en la cara del nudo deben determinarse suponiendo que la "
            "resistencia en el refuerzo de tracción por flexión es 1.25fy."
        ),
    },
    {
        "id": "NSR10-C-C_21_11_1_alcance_diafragmas",
        "seccion": "C.21.11.1 (Alcance de Diafragmas y Cerchas Estructurales DES)",
        "titulo": "Alcance del capítulo de diafragmas: losas de piso y cubierta que transmiten fuerzas sísmicas en estructuras DES, y su aplicación a elementos colectores y cerchas.",
        "texto": (
            "NSR-10 Título C, Capítulo C.21 — C.21.11 — Diafragmas y cerchas "
            "estructurales asignadas a la capacidad especial de disipación de "
            "energía (DES) — C.21.11.1 — Alcance — Las losas de piso y "
            "cubierta que actúen como diafragmas estructurales para trasmitir "
            "fuerzas inducidas por los movimientos sísmicos en estructuras "
            "asignadas a la capacidad de disipación de energía especial "
            "(DES), deben diseñarse de acuerdo con lo indicado en esta "
            "sección. Esta sección también se aplica a elementos colectores y "
            "cerchas que sirven como parte del sistema de resistencia ante "
            "fuerzas sísmicas."
        ),
    },
    {
        "id": "NSR10-C-C_21_12_3_4_losas_terreno_diafragma",
        "seccion": "C.21.12.3.4 (Losas sobre el Terreno como Diafragma Estructural)",
        "titulo": "Requisito de diseñar como diafragmas estructurales las losas sobre el terreno que resisten fuerzas sísmicas de muros o columnas.",
        "texto": (
            "NSR-10 Título C, Capítulo C.21 — C.21.12.3.4 — Las losas sobre el "
            "terreno que resisten fuerzas sísmicas provenientes de los muros o "
            "columnas que son parte del sistema de resistencia ante fuerzas "
            "sísmicas deben diseñarse como diafragmas estructurales de acuerdo "
            "con lo indicado en C.21.11. Los planos de diseño deben "
            "especificar claramente que la losa sobre el terreno es un "
            "diafragma estructural y es parte del sistema de resistencia ante "
            "fuerzas sísmicas."
        ),
    },
    {
        "id": "NSR10-C-C_21_13_3_1_estribos_espaciamiento_axial_baja",
        "seccion": "C.21.13.3.1 (Espaciamiento de Estribos para Elementos con Baja Carga Axial Gravitacional)",
        "titulo": "Requisito de espaciamiento de estribos (< d/2) para elementos que no contribuyen a la resistencia lateral con fuerza axial mayorada menor que Agf'c/10.",
        "texto": (
            "NSR-10 Título C, Capítulo C.21 — C.21.13.3.1 — Elementos "
            "sometidos a una fuerza axial gravitacional mayorada que no exceda "
            "Agf'c/10 deben satisfacer C.21.5.2.1. El espaciamiento de los "
            "estribos debe ser menor que d/2 a lo largo del elemento."
        ),
    },
    {
        "id": "NSR10-C-C_22_7_3_no_concreto_simple_zapatas_pilotes",
        "seccion": "C.22.7.3 (Prohibición de Concreto Simple para Zapatas sobre Pilotes)",
        "titulo": "Prohibición explícita de usar concreto estructural simple en zapatas apoyadas sobre pilotes.",
        "texto": (
            "NSR-10 Título C, Capítulo C.22 — C.22.7.3 — No debe usarse "
            "concreto simple para zapatas sobre pilotes."
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
    tokenizer = model.tokenizer

    print("\nSub-particionando por tokens REALES (limite 128, medido con el tokenizer)...")
    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            n_tok = len(tokenizer.encode(pieza, add_special_tokens=True))
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })
            print(f"  {chunk['id'] + sufijo:60s} {n_tok:3d} tokens")
    print(f"\n{len(CHUNKS)} piezas originales -> {len(piezas_finales)} piezas reales tras troceo.")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for pieza, vec in zip(piezas_finales, vectores):
        rows.append({
            "id": pieza["id"],
            "capitulo": CAPITULO,
            "seccion": pieza["seccion"],
            "titulo": pieza["titulo"][:500],
            "texto": pieza["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de los 25 grupos (26 numerales) de Título C cargados.")


if __name__ == "__main__":
    main()
