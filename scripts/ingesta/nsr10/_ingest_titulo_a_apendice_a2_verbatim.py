"""
Ingesta verbatim del Apéndice A-2 del Título A de NSR-10 (Recomendaciones para
el cálculo de los efectos de interacción dinámica suelo-estructura), páginas
A-141 a A-146. Fase 4 del plan de cierre del Título A (2026-11-08): la
auditoría de texto por página (auditoria_titulo_a_paginas.py) encontró que los
Apéndices A-1, A-2 y A-3 nunca se habían ingestado (cobertura de texto 11 % y
1,5 % en sus PDFs fuente).

Fuente: NSR-10-183-190.pdf, páginas PDF 3 a 8 (A-141 a A-146), leídas
visualmente con Read pages= sobre el PDF nativo.

Fidelidad: las ecuaciones A-2-1 a A-2-15 se transcriben en notación lineal
(el PDF las tiene como imagen/símbolos); la Figura A-2.2-1 (curvas del
coeficiente βo en función de T̄/T) es un gráfico sin ecuación cerrada y NO se
transcribe: solo se documenta su título y de qué variables depende (mismo
criterio ya aplicado a las figuras Cp/GCp de viento, issue #56, y a los mapas de
amenaza sísmica). La barra «‾» sobre un símbolo indica «valor modificado por la
interacción suelo-estructura».

Uso: python _ingest_titulo_a_apendice_a2_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"
PREFIJO = "NSR10-A-APA2"
CAB = "NSR-10 — Apéndice A-2 — Recomendaciones para el cálculo de los efectos de interacción dinámica suelo-estructura\n\n"

CHUNKS = [
    {
        "id": f"{PREFIJO}_A_2_0_nomenclatura_1",
        "seccion": "A-2.0 — Nomenclatura (parte 1)",
        "titulo": "Apéndice A-2, A-2.0: nomenclatura de Aa a M̄1j (aceleración pico efectiva, área e inercia de la cimentación, rigideces Ky y Kθ, altura efectiva h̄, masa participante M̄).",
        "texto": CAB + (
            "APÉNDICE A-2 — RECOMENDACIONES PARA EL CÁLCULO DE LOS EFECTOS DE "
            "INTERACCIÓN DINÁMICA SUELO-ESTRUCTURA\n\n"
            "A-2.0 — NOMENCLATURA\n\n"
            "Aa = coeficiente que representa la aceleración pico efectiva, para diseño, dado en A.2.2.\n"
            "Ao = área de la cimentación.\n"
            "Ds = profundidad del estrato blando. Véase A-2.2.1.2.\n"
            "Go = γ vso² = módulo de cortante promedio para los suelos localizados bajo la cimentación para deformaciones unitarias pequeñas.\n"
            "g = aceleración de la gravedad (9.8 m/s²)\n"
            "hx = altura medida desde la base del nivel en estudio.\n"
            "h̄ = altura efectiva de la edificación, la cual debe tomarse igual a 0.7 veces la altura total, hn. En edificios en los cuales toda la masa M de la edificación está concentrada en un solo piso, debe tomarse igual a la altura del piso, medida desde la base.\n"
            "Io = momento de inercia de la cimentación con respecto a un eje horizontal, perpendicular a la dirección en estudio.\n"
            "k̄ = rigidez de la estructura considerándola como empotrada en la base. Se calcula por medio de la ecuación A-2-4.\n"
            "Ky = rigidez lateral de la cimentación de la edificación, la cual se define como la fuerza estática horizontal aplicada en la cimentación, que produce una deflexión horizontal unitaria. Tanto la fuerza estática como la deflexión horizontal se toman en la dirección en estudio.\n"
            "Kθ = rigidez rotacional, o de balanceo, de la cimentación de la edificación, definida como el momento estático necesario para producir una rotación unitaria, en promedio, de la cimentación con respecto a un eje horizontal perpendicular a la dirección en estudio.\n"
            "Lo = longitud total de la cimentación en la dirección en estudio.\n"
            "Mo = momento de vuelco en la base de la edificación calculado utilizando las fuerzas horizontales de diseño sin incluir la reducción por efectos de interacción suelo-estructura.\n"
            "M1o = momento de vuelco en la base de la edificación calculado utilizando las fuerzas horizontales correspondientes al primer modo sin incluir la reducción por efectos de interacción suelo-estructura.\n"
            "M̄ = masa participante de la edificación, el cual puede tomarse igual a 0.7M, excepto en aquellos casos en los cuales toda la masa M de la edificación está concentrado en un solo piso, caso en el cual debe tomarse igual a M.\n"
            "M̄1j = masa participante de la edificación, para el modo fundamental de la edificación en la dirección j, calculado utilizando la ecuación A.5.4-2."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_0_nomenclatura_2",
        "seccion": "A-2.0 — Nomenclatura (parte 2)",
        "titulo": "Apéndice A-2, A-2.0: nomenclatura de r a Vs′ (longitudes características ra y rm, espectro Sa y S̄a, períodos T, T̄, T1, T̄1, cortante basal Vs, V̄s y V′s = cortante con CuTa).",
        "texto": CAB + (
            "A-2.0 — NOMENCLATURA (continuación)\n\n"
            "r = longitud característica de la cimentación. Se determina por medio de las ecuaciones A-2-7 o A-2-8.\n"
            "ra = longitud característica de la cimentación. Definida por medio de la ecuación A-2-7.\n"
            "rm = longitud característica de la cimentación. Definida por medio de la ecuación A-2-8.\n"
            "Sa = valor del espectro de aceleraciones de diseño, determinado de acuerdo con los requisitos del Capítulo A.2, correspondiente al período fundamental de la estructura, T o Ta, considerada empotrada en su base, calculado de acuerdo con lo prescrito en A.4.2.\n"
            "Sa1 = valor del espectro de aceleraciones de diseño, determinado de acuerdo con los requisitos del Capítulo A.2, correspondiente al período del modo fundamental de la estructura, T1, considerada empotrada en su base.\n"
            "S̄a = valor del espectro de aceleraciones de diseño, determinado de acuerdo con los requisitos del Capítulo A.2, correspondiente al período fundamental de la estructura, T̄, cuando éste se calcula considerando los efectos de la interacción suelo-estructura, tal como se define en A-2.2.1.1.\n"
            "S̄a1 = valor del espectro de aceleraciones de diseño, determinado de acuerdo con los requisitos del Capítulo A.2, correspondiente al período fundamental de la estructura, T̄1, cuando éste se calcula considerando los efectos de la interacción suelo-estructura.\n"
            "T = valor del período fundamental del edificio, calculado de acuerdo con lo prescrito en A.4.2.\n"
            "T1 = valor del período fundamental del edificio, correspondiente al primer modo de vibración.\n"
            "T̄ = valor del período fundamental del edificio tomando en cuenta la interacción suelo-estructura. Se determina de acuerdo con los requisitos de A-2.2.1.1.\n"
            "T̄1 = valor del período fundamental del edificio, correspondiente al primer modo de vibración, tomando en cuenta la interacción suelo-estructura.\n"
            "Vs = cortante sísmico de diseño en la base de la estructura, calculado por el método de la fuerza horizontal equivalente del Capítulo A.4.\n"
            "V′s = cortante sísmico en la base de la estructura, calculado por el método de la fuerza horizontal equivalente del Capítulo A.4, utilizando un período de vibración igual a CuTa."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_0_nomenclatura_3",
        "seccion": "A-2.0 — Nomenclatura (parte 3)",
        "titulo": "Apéndice A-2, A-2.0: nomenclatura de V1j a γ (cortantes modales, ΔVs, vso, α, αθ, β̄, βo, deflexiones δx, δ̄x, masa unitaria γ).",
        "texto": CAB + (
            "A-2.0 — NOMENCLATURA (continuación)\n\n"
            "V1j = cortante sísmico de diseño en la base de la estructura en la dirección j, contribuido por el modo fundamental en esa dirección, calculado de acuerdo con la ecuación A.5.4-3 y sin ser afectado por efectos de interacción suelo-estructura.\n"
            "V̄s = cortante sísmico de diseño en la base de la estructura, calculado tomando en cuenta la interacción suelo-estructura.\n"
            "V̄1j = cortante sísmico de diseño en la base de la estructura en la dirección j, contribuido por el modo fundamental en esa dirección, y afectado por la interacción suelo-estructura.\n"
            "ΔVs = reducción en el cortante sísmico de diseño en la base de la estructura, debido a los efectos de la interacción suelo-estructura. Ecuación A-2-2.\n"
            "ΔV1j = reducción en el cortante sísmico de diseño en la base de la estructura en la dirección j, contribuido por el modo fundamental en esa dirección, debida a los efectos de la interacción suelo-estructura.\n"
            "vso = velocidad promedio de la onda de cortante, de los suelos localizados debajo de la cimentación, para niveles bajos de deformación unitaria, menores de 0.00001 (0.001%).\n"
            "α = parámetro que describe la densidad relativa de la estructura y el suelo bajo ella. Definida en la ecuación A-2-6.\n"
            "αθ = modificador de la rigidez dinámica de la cimentación para tener en cuenta el balanceo.\n"
            "β̄ = coeficiente de amortiguamiento crítico del sistema estructural, considerando interacción suelo-estructura, calculado de acuerdo con lo prescrito en A-2.2-1.\n"
            "βo = coeficiente de amortiguamiento crítico de la cimentación. Se determina por medio de la figura A-2.2-1.\n"
            "δx = deflexión horizontal en el nivel x de la estructura, calculada siguiendo el método de la fuerza horizontal equivalente y utilizando las fuerzas sísmicas de diseño sin ser modificadas por los efectos de la interacción suelo-estructura.\n"
            "δ1x = deflexión horizontal en el nivel x de la estructura, calculada para el primer modo de vibración sin incluir los efectos de la interacción suelo-estructura.\n"
            "δ̄x = deflexión horizontal en el nivel x de la estructura, modificada por los efectos de la interacción suelo-estructura. Ecuación A-2-11.\n"
            "δ̄1x = deflexión horizontal en el nivel x de la estructura, para el primer modo de vibración, modificada por los efectos de la interacción suelo-estructura.\n"
            "γ = masa unitaria promedio del suelo."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_1_general",
        "seccion": "A-2.1 — General",
        "titulo": "Apéndice A-2, A-2.1.1: cuándo usar los requisitos de interacción suelo-estructura (reducen cortante, fuerzas horizontales y momentos de vuelco; aumentan deflexiones y derivas; no usar con base flexible modelada directamente).",
        "texto": CAB + (
            "A-2.1 — GENERAL\n\n"
            "A-2.1.1 — Los requisitos presentados en este Apéndice pueden utilizarse para tener en cuenta los efectos de interacción suelo-estructura en la determinación de las fuerzas sísmicas de diseño y las deformaciones que éstas imponen a la estructura. Su uso se permite dentro de las limitaciones que da el Capítulo A.7 cuando el modelo matemático utilizado para determinar la respuesta de la estructura no incorpora directamente la flexibilidad de la cimentación (uso de modelos empotrados en la base). En general el uso de estos requisitos disminuye los valores de diseño del cortante sísmico en la base, las fuerzas horizontales y los momentos de vuelco, pero aumenta las deflexiones horizontales de la estructura, y por ende las derivas, en sitios particulares de la estructura, además de los desplazamientos y fuerzas secundarias asociadas con los efectos P-Delta. Los requisitos para ser utilizados con el método de la fuerza horizontal equivalente se presentan en A-2.2 y para el método del análisis dinámico modal elástico en A-2.3. Estos requisitos no deben ser usados si se empleó un modelo de base flexible donde la cimentación se modela directamente en el análisis de la estructura, y no un modelo de base empotrada."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_2_1_cortante_base",
        "seccion": "A-2.2.1 — Cortante en la base",
        "titulo": "Apéndice A-2, A-2.2.1: cortante basal con interacción V̄s = Vs − ΔVs (A-2-1), reducción ΔVs (A-2-2), límite V̄s ≥ 0.7 V′s.",
        "texto": CAB + (
            "A-2.2 — MÉTODO DE LA FUERZA HORIZONTAL EQUIVALENTE\n\n"
            "Los requisitos que se presentan a continuación, complementan en lo concerniente a interacción suelo-estructura los dados en el Capítulo A.7.\n\n"
            "A-2.2.1 — CORTANTE EN LA BASE — Para tener en cuenta los efectos de interacción suelo-estructura, el cortante sísmico de diseño en la base, Vs, determinado por medio de la ecuación A.4-5, puede modificarse a:\n\n"
            "V̄s = Vs − ΔVs     (A-2-1)\n\n"
            "y el valor de la reducción en el cortante sísmico en la base, para diseño, debe calcularse por medio de:\n\n"
            "ΔVs = [ Sa − S̄a (0.05/β̄)^0.4 ] g M̄     (A-2-2)\n\n"
            "El valor del cortante sísmico en la base modificado, V̄s, no puede ser menor que 0.7 V′s."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_2_1_1_periodo_efectivo",
        "seccion": "A-2.2.1.1 — Período efectivo de la edificación",
        "titulo": "Apéndice A-2, A-2.2.1.1: período efectivo T̄ = T·√[1 + (k̄/Ky)(1 + Ky h̄²/Kθ)] (A-2-3), k̄ = 4π² M̄/T² (A-2-4), Tabla A-2.1-1 de G/Go y vs/vso según Aa (≤0.10: 0.81/0.90; ≤0.15: 0.64/0.80; ≤0.20: 0.49/0.70; ≥0.30: 0.42/0.65).",
        "texto": CAB + (
            "A-2.2.1.1 — Período efectivo de la edificación — El período efectivo, T̄, debe determinarse por medio de la siguiente ecuación:\n\n"
            "T̄ = T · √[ 1 + (k̄/Ky) · ( 1 + (Ky h̄²)/Kθ ) ]     (A-2-3)\n\n"
            "y\n\n"
            "k̄ = 4π² ( M̄ / T² )     (A-2-4)\n\n"
            "Las rigideces de la cimentación, Ky y Kθ, deben determinarse por medio de principios establecidos de mecánica de suelos, utilizando propiedades del suelo que sean representativas de su comportamiento a niveles de deformación unitaria, conmensurables con los que producen los movimientos sísmicos de diseño. En aquellos casos en los cuales el estudio geotécnico no lo indique, el módulo promedio de cortante, G, para los suelos localizados debajo de la cimentación, en condiciones de deformaciones unitarias apreciables, y la velocidad de la onda de cortante, vs, asociada con estas deformaciones unitarias, pueden determinarse utilizando la tabla A.-2.1-1.\n\n"
            "Tabla A-2.1-1 — Valores de G/Go y vs/vso\n"
            "Valor de Aa ≤ 0.10: G/Go = 0.81; vs/vso = 0.90\n"
            "Valor de Aa ≤ 0.15: G/Go = 0.64; vs/vso = 0.80\n"
            "Valor de Aa ≤ 0.20: G/Go = 0.49; vs/vso = 0.70\n"
            "Valor de Aa ≥ 0.30: G/Go = 0.42; vs/vso = 0.65"
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_2_1_1_periodo_losa_superficial",
        "seccion": "A-2.2.1.1 — Período efectivo, losa de fundación superficial (A-2-5 a A-2-8)",
        "titulo": "Apéndice A-2, A-2.2.1.1: alternativa para losa de fundación superficial — T̄ con α, ra, rm, αθ (A-2-5); α = M̄/(γ Ao h̄) (A-2-6); ra = √(Ao/π) (A-2-7); rm = ⁴√(4Io/π) (A-2-8).",
        "texto": CAB + (
            "Alternativamente, para edificaciones cuya cimentación sea una losa de fundación superficial o aproximadamente superficial, que se construye de una manera tal que se pueda considerar que el contacto entre los muros de contención y el suelo no restringe el libre movimiento de la estructura, el período de vibración efectivo, tomando en cuenta los efectos de la interacción suelo-estructura, se puede determinar por medio de la siguiente ecuación:\n\n"
            "T̄ = T · √[ 1 + (25 α ra h̄)/(vs² T²) · ( 1 + (1.12 ra h̄²)/(αθ rm³) ) ]     (A-2-5)\n\n"
            "en donde:\n\n"
            "α = M̄ / (γ Ao h̄)     (A-2-6)\n\n"
            "ra = √(Ao/π)     (A-2-7)\n\n"
            "y\n\n"
            "rm = ⁴√(4 Io/π)     (A-2-8)"
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_2_1_2_amortiguamiento_efectivo",
        "seccion": "A-2.2.1.2 — Amortiguamiento efectivo",
        "titulo": "Apéndice A-2, A-2.2.1.2: β̄ = βo + 0.05/(T̄/T)³ (A-2-9); r = ra si h̄/Lo ≤ 0.5 y r = rm si h̄/Lo ≥ 1.0; pilotes en punta o estrato blando sobre rígido: β′o = βo(4Ds/(vs T̄))² (A-2-10); β̄ entre 0.05 y 0.20; Figura A-2.2-1 (βo vs T̄/T).",
        "texto": CAB + (
            "A-2.2.1.2 — Amortiguamiento efectivo — El coeficiente de amortiguamiento efectivo del sistema estructura-cimentación, debe calcularse por medio de:\n\n"
            "β̄ = βo + 0.05 / (T̄/T)³     (A-2-9)\n\n"
            "Los valores de βo se obtienen de la figura A-2.2-1. El parámetro r en la figura A-2.2-1 es una longitud característica de la cimentación, la cual se puede determinar así:\n\n"
            "Para h̄/Lo ≤ 0.5, r es igual a ra, de la ecuación A-2-7 y para h̄/Lo ≥ 1.0, r es igual a rm, de la ecuación A-2-8.\n\n"
            "Para valores intermedios se puede interpolar. Lo es la longitud de la cimentación en la dirección en estudio, y en la aplicación de las ecuaciones A-2-7 y A-2-8, Ao e Io se determinan para el área de la cimentación que efectivamente está en contacto con el suelo, pues el transmite el peso de la edificación.\n\n"
            "Para edificios cimentados sobre pilotes que trabajan en punta, y para todos los otros casos en los cuales el suelo de fundación consiste en un estrato de suelos blandos relativamente uniforme, colocado sobre un depósito de suelos más duros, o roca, presentándose un cambio abrupto de rigidez, el coeficiente de amortiguamiento efectivo, βo, que se utiliza en la ecuación A-2-9 puede ser substituido por el valor dado en la siguiente ecuación:\n\n"
            "β′o = βo · ( 4 Ds / (vs T̄) )²     (A-2-10)\n\n"
            "la cual es aplicable sólo en aquellos casos en los cuales la expresión entre paréntesis es menor que la unidad. En esta ecuación Ds es la profundidad total del estrato blando.\n\n"
            "El valor de β̄, calculado de acuerdo con la ecuación A-2-9, con o sin el ajuste representado en la ecuación A-2-10, en ningún caso puede ser menor de 0.05, ni mayor que 0.20.\n\n"
            "Figura A-2.2-1 — Coeficiente de amortiguamiento crítico de la cimentación, βo. (Gráfico de βo, de 0.00 a 0.25, en función de T̄/T, de 1.00 a 2.00, con familias de curvas para h̄/r ≤ 1.0, 1.5, 2.0 y 5.0 y para Aa ≥ 0.20, Aa = 0.15 y Aa ≤ 0.10; no se transcribe el gráfico.)"
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_2_2_y_2_2_3_distribucion_otros_efectos",
        "seccion": "A-2.2.2 y A-2.2.3 — Distribución en la altura y otros efectos",
        "titulo": "Apéndice A-2, A-2.2.2 y A-2.2.3: la distribución en la altura del cortante basal corregido es la de la estructura sin interacción; deflexiones modificadas δ̄x = (V̄s/Vs)(δx + Mo hx/Kθ) (A-2-11).",
        "texto": CAB + (
            "A-2.2.2 — DISTRIBUCIÓN EN LA ALTURA DE LAS FUERZAS SÍSMICAS — La distribución en la altura del cortante en la base corregido por efectos de interacción suelo-estructura se debe tomar igual a la de la de la estructura sin interacción.\n\n"
            "A-2.2.3 — OTROS EFECTOS — Los cortantes de piso, los momentos de vuelco y los efectos torsionales deben determinarse de la misma manera que para edificaciones en las cuales no se ha tomado en cuenta la interacción suelo-estructura, pero utilizando las fuerzas horizontales reducidas por efectos de interacción. Las deflexiones modificadas deben determinarse por medio de la siguiente ecuación:\n\n"
            "δ̄x = (V̄s / Vs) · ( δx + (Mo hx)/Kθ )     (A-2-11)"
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_3_1_cortantes_modales",
        "seccion": "A-2.3.1 — Cortantes modales en la base",
        "titulo": "Apéndice A-2, A-2.3.1: método del análisis modal — V̄1j = V1j − ΔV1j (A-2-12), ΔV1j = [Sa1 − S̄a1 (0.05/β̄)^0.4] g M̄1j (A-2-13), altura efectiva h̄ modal (A-2-14), cortante de diseño no menor que 0.7 V′s.",
        "texto": CAB + (
            "A-2.3 — MÉTODO DEL ANÁLISIS MODAL\n\n"
            "Los siguientes requisitos complementan, en lo concerniente a interacción suelo-estructura, lo presentado en el Capítulo A.5.\n\n"
            "A-2.3.1 — CORTANTES MODALES EN LA BASE — Para tener en cuenta los efectos de interacción suelo-estructura, el cortante sísmico de diseño en la base, correspondiente al modo fundamental, V1j, en la dirección j, determinado por medio de la ecuación A.5.4-3, puede modificarse a:\n\n"
            "V̄1j = V1j − ΔV1j     (A-2-12)\n\n"
            "y el valor de la reducción en el cortante sísmico en la base correspondiente al modo fundamental, debe calcularse utilizando la ecuación A-2-13:\n\n"
            "ΔV1j = [ Sa1 − S̄a1 (0.05/β̄)^0.4 ] g M̄1j     (A-2-13)\n\n"
            "El período T̄1 se calcula utilizando la ecuación A-2-3 o A-2-5, según corresponda, utilizando T1 en vez de T, determinando k̄ por medio de la ecuación A-2-4, utilizando M̄1j en vez de M̄, y calculando h̄ por medio de la siguiente ecuación:\n\n"
            "h̄ = ( Σ(i=1..n) mi φi¹ hi ) / ( Σ(i=1..n) mi φi¹ )     (A-2-14)\n\n"
            "Los valores mencionados T̄1, T1, M̄1j, y h̄ se utilizan para calcular α en la ecuación A-2-6 y el coeficiente βo de la figura A-2.2-1. No debe realizarse ninguna reducción en las contribuciones de los modos de vibración diferentes al fundamental por efectos de interacción suelo-estructura. El cortante en la base de diseño, en ningún caso puede ser menor que 0.7V′s."
        ),
    },
    {
        "id": f"{PREFIJO}_A_2_3_2_y_2_3_3_otros_efectos_valores_diseno",
        "seccion": "A-2.3.2 y A-2.3.3 — Otros efectos modales y valores de diseño",
        "titulo": "Apéndice A-2, A-2.3.2 y A-2.3.3: cortantes de piso y momentos de vuelco según el Capítulo A.5 con V̄1j; deflexiones del primer modo δ̄1x = (V̄1/V1)(δ1x + M1o hx/Kθ) (A-2-15); valores de diseño por A.5 con los efectos modificados del primer modo.",
        "texto": CAB + (
            "A-2.3.2 — OTROS EFECTOS MODALES — Los cortantes de piso, y los momentos de vuelco deben determinarse de la misma manera que para edificaciones en las cuales no se ha tomado en cuenta la interacción suelo-estructura, tal como lo prescribe el Capítulo A.5, pero utilizando el valor de V̄1j en vez de V1j. Las deflexiones modificadas del primer modo deben determinarse por medio de la siguiente ecuación:\n\n"
            "δ̄1x = (V̄1 / V1) · ( δ1x + (M1o hx)/Kθ )     (A-2-15)\n\n"
            "A-2.3.3 — VALORES DE DISEÑO — Se determinan utilizando los procedimientos indicados en el Capítulo A.5, pero utilizando los valores modificados del los efectos del primer modo en cada una de las direcciones principales, en planta, de la edificación."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks-padre del Apéndice A-2...")
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    rows = [{"id": c["id"], "capitulo": CAPITULO, "seccion": c["seccion"], "titulo": c["titulo"][:500],
             "texto": c["texto"], "embedding": v.tolist()} for c, v in zip(CHUNKS, vectores)]
    print(f"Subiendo {len(rows)} chunks-padre a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_apendice_a2_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
