"""
Ingesta verbatim de NSR-10 Título F.5.4.7 completo (Estructuras de
Aluminio -- Diseño Estático de Miembros: MIEMBROS A COMPRESIÓN, la pieza
más densa de F.5, pendiente desde 2026-09-01) más F.5.4.8.1
(Generalidades de flexión con fuerza axial y flexión biaxial).

Fuente: NSR-10-1083-1182.pdf (páginas internas F-490 a F-501), ya
descargado localmente en scripts/ingesta/nsr10/raw/ (gitignored). Offset
de páginas real confirmado por lectura visual directa: página_F =
página_real - 681 (equivalente a página_interna_del_PDF + 401, donde
página_interna_del_PDF = página_real - 1082).

Texto transcrito verbatim leyendo el PDF nativo página por página (nunca
el texto plano exportado, corrompe subíndices/fórmulas). Sistema de
unidades: kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Nota de fidelidad honesta: la Tabla F.5.4.7-2 (18 casos de perfiles de
aluminio para pandeo torsional) empareja cada fila con un DIBUJO/diagrama
de la sección transversal (ángulos, T, cruciformes, I, canales, etc.).
Las fórmulas de cada caso (λ0, s, X, Y) se transcriben verbatim completas
-- son el contenido técnico realmente utilizable. El dibujo geométrico en
sí NO se reproduce (es un diagrama visual, no texto), siguiendo el mismo
criterio de honestidad ya aplicado a las figuras Cp/GCp de viento del
Título B (ver issue #56) y a los mapas de amenaza sísmica del Título A:
no se inventa una descripción de forma que no se pueda verificar con
certeza a partir de un boceto pequeño. Lo mismo aplica a las Figuras
F.5.4.7-1 y F.5.4.7-2(a)/(b), que son curvas de interpolación gráfica
sin ecuación cerrada -- se documenta su existencia y propósito, no se
inventan valores leídos de la curva.

F.5.4.8 queda PARCIAL a propósito: el PDF fuente descargado corta
literalmente a mitad de un párrafo de F.5.4.8.2 en la página F-501 (la
última del archivo). Solo se ingesta F.5.4.8.1, completo y verbatim. El
resto de F.5.4.8 (desde F.5.4.8.2 en adelante), F.5.4.9, F.5.5-F.5.8 y
los apéndices F.5.A-F.5.F requieren descargar NSR-10-1183-1283.pdf
(pendiente, ver docs/fuentes-normativas.md).

Uso: python _ingest_titulo_f_f547_f548_1_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

TABLA_F_5_4_7_2 = (
    "Tabla F.5.4.7-2 — Parámetros de pandeo torsional para miembros a compresión (18 casos numerados, cada uno "
    "asociado en el documento original a un dibujo de la sección transversal que aquí NO se reproduce — solo las "
    "fórmulas y condiciones de aplicación, verbatim). "
    "Caso 1: condición ρ≤5. λ0 = λ1 = 5B/t - 0.6ρ^1.5 (B/t)^(1/2); s = λu/λ0; X = 0.6. "
    "Caso 2: condición ρ≤5, 1≤w≤2.5. λ0 = λ1 - (w-1){2(w-1)^2 - 1.5ρ}; s = λu/λ0; X = 0.6. "
    "Caso 3 (sección \"Igual\", nota 1): λ0 = 66; s = λu/λ0; X = 0.6. "
    "Caso 4: condición ρ≤5, 0.5≤B/D≤1.0. λ0 = (D/t){4.2 + 0.5(B/D)^2} - 0.6ρ^1.5 (D/t)^(1/2); "
    "s = s4 = {1 + 6(1-B/D)^2}(λu/λ0); X = X4 = 0.6 - 0.4(1-B/D)^2. "
    "Caso 5: condición ρ≤5, 0.5≤B/D≤1.0, 1≤w≤2.5. λ0 = λ4 + 1.5ρ(w-1) - 2(w-1)^3; s = s4; X = X4. "
    "Caso 6 (sección \"Desigual\", nota 1): λ0 = 57; s(1.4(λu/λ0)); X = 0.60. "
    "Caso 7: condición ρ≤3.5. λ0 = 5.1B/t - ρ^1.5 (B/t)^(1/2); X = 1. "
    "Caso 8: condición ρ≤5, 0.5≤B/D≤2.0. λ0 = λ8 = (B/t){4.4 + 1.1(D/B)^2} - 0.7ρ^1.5 (B/t)^(1/2); "
    "s = λy/λ0; X = X8 = 1.1 - 0.3 D/B. "
    "Caso 9: condición ρ≤5, 0.5≤B/D≤2.0, 1≤ϖ≤2.5. λ0 = λ8 + 1.5ρ(ϖ-1) - 2(ϖ-1)^3; s = λy/λ0; X = X8. "
    "Caso 10 (sección \"Igual\", nota 1): λ0 = 70; s = (λy/λ0); X = 0.83. "
    "Caso 11 (sección \"Desigual\", nota 1): λ0 = 60; s = (λy/λ0); X = 0.76. "
    "Caso 12 (sección \"Desigual\", variante, nota 1): λ0 = 63; s = (λy/λ0); X = 0.89. "
    "Caso 13: condición 0.5≤D/B≤2.0, ρ≤3.5. λ0 = (D/t){1.4 + 1.5(B/D) + 1.1(D/B)} - ρ^1.5 (D/t); "
    "s = (λy/λ0); X = 1.3 - 0.8 D/B + 0.2(D/B)^2. "
    "Caso 14: λ0 = 65; s = (λy/λ0); X = 0.78. "
    "Caso 15: condición 1≤D/B≤3, 1≤t2/t1≤2. λ0 = (B/t2){7 + 1.5(D/B)(t2/t1)}; s = (λx/λt); "
    "X = 0.35 D/B - 0.04(D/B)^2; Y = 0.14 - 0.02 D/B - 0.02 t2/t1. "
    "Caso 16: condición 1≤D/B≤3, C/B≤0.4. λ0 = (B/t){7 + 1.5(D/B) + 5(C/B)}; s = (λx/λt); "
    "X = 0.35 D/B - 0.04(D/B)^2 - 0.25 C/B; Y = 0.12 - 0.02 D/B + {0.6(C/B)^2 / (D/B - 0.5)}. "
    "Caso 17: condición 1≤D/B≤3, C/B≤0.4 (misma familia geométrica del caso 16, fórmula Y distinta). "
    "λ0 = (B/t){7 + 1.5(D/B) + 5(C/B)}; s = (λx/λt); X = 0.35 D/B - 0.04(D/B)^2; "
    "Y = 0.12 - 0.02 D/B + {0.05(C/B) / (D/B - 0.5)}. "
    "Caso 18 (sección reforzada, nota 1): λ0 = 126; s = (λx/λt); X = 0.59; Y = 0.104. "
    "NOTA 1: Formas de sección reforzada que cumplan con normas como el BS 1161. "
    "NOTA 2: Las secciones son de espesor uniforme t, excepto los casos 14 y 15. "
    "NOTA 3: λu, λ y λy son los parámetros de esbeltez (l/r) para pandeo por flexión respecto a los ejes u, x o y. "
    "NOTA 4: ρ es un coeficiente que depende de la cantidad de material del filete en la raíz de la sección: "
    "filetes radiados, ρ = R/t; filetes a 45°, ρ = 1.6F/t. "
    "NOTA 5: Los valores dados para λ0, X y Y son válidos únicamente dentro de los límites mostrados. En el caso de "
    "ángulos espalda contra espalda (casos 8 a 12), las expresiones dejan de ser aplicables si la separación entre "
    "los ángulos excede 2t."
)

CHUNKS = [
    {
        "id": "NSR10-F-F_5_4_7_intro", "seccion": "F.5.4.7",
        "titulo": "F.5.4.7 — Miembros a Compresión: 3 verificaciones (columna, pandeo torsional, aplastamiento local)",
        "texto": (
            "F.5.4.7 — MIEMBROS A COMPRESIÓN — Se necesitan generalmente tres verificaciones para miembros cargados "
            "axialmente a compresión (puntales): "
            "(a) Revisión como columna — esto es, revisión a flexión y pandeo (véanse F.5.4.7.2 y F.5.4.7.3) (se "
            "refiere al pandeo general del miembro como un todo). "
            "(b) Revisión por pandeo torsional — (véanse F.5.4.7.2 y F.5.4.7.4) (se refiere al pandeo general del "
            "miembro como un todo). "
            "(c) Revisión por aplastamiento local — (véase F.5.4.7.6) (se refiere a la sección transversal más "
            "débil a lo largo de la longitud). "
            "La revisión (a) siempre debe hacerse, la (b) generalmente se requiere pero puede ser obviada en algunos "
            "casos. La (c) únicamente se necesita para miembros a compresión que tienen bajas relaciones de "
            "esbeltez y que están significativamente debilitados localmente por agujeros o soldadura. "
            "Para tomar en cuenta la interacción entre carga axial y flexión es generalmente necesario referirse a "
            "F.5.4.8. Sin embargo, para puntales con conexiones excéntricas en los extremos, es permitido, en "
            "ciertos casos, usar un procedimiento simplificado (véase F.5.4.7.8) para tener en cuenta los momentos "
            "introducidos. "
            "F.5.4.7.1 — Clasificación de la sección para compresión axial — Antes de hacer cualquiera de las tres "
            "revisiones mencionadas, es necesario clasificar la sección transversal como compacta o esbelta. La "
            "clasificación se basa en el menos favorable de los elementos componentes de acuerdo con F.5.4.3.3."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_2", "seccion": "F.5.4.7.2",
        "titulo": "F.5.4.7.2 — Resistencia al pandeo general: PR = ps·A·φ (ecuación F.5.4.7-1)",
        "texto": (
            "F.5.4.7.2 — Resistencia al pandeo general — Con las dos revisiones, (a) y (b), la fuerza axial P bajo "
            "carga mayorada no debe exceder la resistencia axial de diseño PR basada en pandeo general y dada por la "
            "siguiente expresión: "
            "PR = ps A φ  (F.5.4.7-1). "
            "Donde: A = área bruta, sin reducción por ablandamiento en la zona afectada por el calor, pandeo local o "
            "agujeros. ps = esfuerzo de pandeo en pandeo por flexión o torsional. φ = coeficiente de reducción de "
            "capacidad (véase la tabla F.5.3.3-1). "
            "Para encontrar ps para el pandeo como columna, se debe considerar la falla respecto a ambos ejes "
            "principales y se toma el menor valor. "
            "Para un miembro a compresión de gran esbeltez (λ>130), es necesario consultar el apéndice F.5.I para "
            "encontrar ps."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_3", "seccion": "F.5.4.7.3",
        "titulo": "F.5.4.7.3 — Pandeo como columna: esfuerzo de pandeo (figura F.5.4.5-3), parámetro de esbeltez λ=l/r (ec. F.5.4.7-2), Tabla F.5.4.7-1 coeficiente K",
        "texto": (
            "F.5.4.7.3 — Pandeo como columna. "
            "(a) Esfuerzo de pandeo — El valor de ps para pandeo como columna debe leerse de la curva apropiada en "
            "la figura F.5.4.5-3, seleccionada de acuerdo con F.5.4.7.5. "
            "(b) Parámetro de esbeltez — El parámetro de esbeltez λ para pandeo como columna necesitado para la "
            "figura F.5.4.5-3, se define como sigue: λ = l/r  (F.5.4.7-2). Donde: l = longitud efectiva. "
            "r = radio de giro. Ambos apropiados para la dirección de pandeo en consideración. "
            "Tabla F.5.4.7-1 — Coeficiente de longitud efectiva K para miembros a compresión, según condiciones en "
            "los extremos: "
            "1. Traslación y rotación impedidas en ambos extremos — K=0.7. "
            "2. Traslación impedida en ambos extremos y rotación impedida en uno solo — K=0.85. "
            "3. Traslación impedida y rotación libre en ambos extremos — K=1.0. "
            "4. Traslación impedida en un extremo y rotación impedida en ambos — K=1.25. "
            "5. Traslación y rotación impedidas en un extremo y rotación parcialmente restringida y libertad de "
            "traslación en el otro — K=1.5. "
            "6. Traslación y rotación impedidas en un extremo y traslación y rotación libres en el otro — K=2.0. "
            "La longitud efectiva, l, debe tomarse como KL, donde L es la longitud entre puntos de soporte lateral; "
            "o para un puntal en voladizo, como su longitud. El valor de K, coeficiente de longitud efectiva para "
            "miembros a compresión, debe determinarse a partir del conocimiento de las condiciones en los extremos; "
            "la tabla F.5.4.7-1 sirve de guía. "
            "El valor de r debe basarse en la sección bruta para todos los miembros. "
            "Cuando la sección transversal está total o substancialmente afectada por ablandamiento en la zona "
            "afectada por el calor en un extremo restringido al giro de un miembro, tal restricción debe ignorarse "
            "para encontrar el valor adecuado de K. Así, para el caso 1 en la tabla F.5.4.7-1, K debería tomarse "
            "como 1.0 si la sección está completamente ablandada en cada extremo."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_4", "seccion": "F.5.4.7.4",
        "titulo": "F.5.4.7.4 — Pandeo torsional: excepciones y parámetro de esbeltez λ (ecuaciones F.5.4.7-3 a F.5.4.7-6)",
        "texto": (
            "F.5.4.7.4 — Pandeo torsional. "
            "(a) Excepciones — La posibilidad de pandeo torsional puede ignorarse para los siguientes casos: "
            "secciones huecas cerradas; secciones I doblemente simétricas; secciones enteramente compuestas de "
            "salientes radiantes, esto es, ángulos, secciones T, cruciformes, que se clasifiquen como compactas de "
            "acuerdo con F.5.4.3.3. "
            "(b) Parámetro de esbeltez — El parámetro λ de esbeltez para pandeo torsional puede obtenerse usando las "
            "expresiones F.5.4.7-3 o F.5.4.7-4 dadas enseguida, o siguiendo el apéndice F.5.H. Debe siempre basarse "
            "en el área bruta de la sección. "
            "Fórmula general: λ = π(EA/Pcr)^(1/2)  (F.5.4.7-3). "
            "Donde: A = área de la sección bruta, sin reducción por pandeo local, ablandamiento en la zona afectada "
            "por el calor o agujeros. E = módulo de elasticidad. Pcr = carga crítica elástica para pandeo torsional, "
            "teniendo en cuenta la interacción con el pandeo como columna cuando sea necesario. "
            "Secciones como las dadas en la tabla F.5.4.7-2: λ = k·λt  (F.5.4.7-4). Donde: k = se lee en la figura "
            "F.5.4.7-1. λt = se encuentra de acuerdo con: para ángulos, secciones T, cruciformes: λt = λ0  "
            "(F.5.4.7-5). Para canales, sombreros: λt = λ0 / [1 + (Yλ0²/λx²)]^(1/2)  (F.5.4.7-6). "
            "La tabla F.5.4.7-2 contiene expresiones para λ0 y Y; y también para s y X (necesarios para la figura "
            "F.5.4.7-1). En F.5.4.7-6, la cantidad λx debe tomarse como la esbeltez efectiva para pandeo como "
            "columna alrededor del eje xx (como se define en la tabla F.5.4.7-2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_tabla2", "seccion": "F.5.4.7-2",
        "titulo": "Tabla F.5.4.7-2 — Parámetros de pandeo torsional para miembros a compresión, 18 casos con fórmulas λ0/s/X/Y (dibujos de sección NO reproducidos)",
        "texto": TABLA_F_5_4_7_2,
    },
    {
        "id": "NSR10-F-F_5_4_7_figuras", "seccion": "F.5.4.7-1_y_F.5.4.7-2",
        "titulo": "Figuras F.5.4.7-1 (coeficiente k) y F.5.4.7-2(a)/(b) (esfuerzo de pandeo torsional ps): curvas gráficas de interpolación, no transcritas",
        "texto": (
            "Figura F.5.4.7-1 — Pandeo torsional de miembros a compresión, coeficiente de interacción k: curva de "
            "interpolación gráfica (eje vertical K de 0 a 2.5, eje horizontal S de 0 a 2.5, familia de curvas "
            "paramétricas por valor de X de 0 a 1.0). Es una lectura gráfica sin ecuación cerrada — no se "
            "transcriben valores numéricos de la curva, deben leerse directamente del PDF original (página F-495) "
            "o consultar el apéndice F.5.H mencionado en F.5.4.7.4(b) como alternativa analítica. "
            "Figura F.5.4.7-2(a) — Esfuerzo de pandeo torsional para miembros a compresión ps, para miembro no "
            "soldado (eje vertical ps en kg/mm², eje horizontal λ de 0 a más de 100): familia de curvas, cada una "
            "asociada a uno de los 18 casos de la tabla F.5.4.7-2. Para λ>130 debe usarse la figura F.5.I-1 del "
            "apéndice I en su lugar. "
            "Figura F.5.4.7-2(b) — Misma curva que la (a) pero para miembro soldado. "
            "Ambas figuras son lecturas gráficas de interpolación, sin ecuación cerrada dada en el texto — no se "
            "transcriben valores numéricos, deben leerse directamente del PDF original (página F-496)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_5", "seccion": "F.5.4.7.5",
        "titulo": "F.5.4.7.5 — Selección de la curva de miembros a compresión, Tabla F.5.4.7-3, ecuaciones F.5.4.7-7/8/9",
        "texto": (
            "F.5.4.7.5 — Selección de la curva de miembros a compresión — El esfuerzo de pandeo general ps se debe "
            "leer de la curva de miembros a compresión apropiada de la figura F.5.4.5-3 (para pandeo como columna) "
            "o de la figura F.5.4.7-2 (para pandeo torsional). La selección del diagrama debe estar de acuerdo con "
            "la tabla F.5.4.7-3. En cualquier diagrama dado, la curva apropiada es la que encuentra el eje de "
            "esfuerzos en un esfuerzo p1. "
            "Tabla F.5.4.7-3 — Selección de la curva para miembros a compresión, por tipo de pandeo, miembro no "
            "soldado y miembro soldado: "
            "Pandeo de columna, sección simétrica o ligeramente asimétrica — miembro no soldado: figura F.5.4.5-3 "
            "(a); miembro soldado: figura F.5.4.5-3 (b). "
            "Pandeo de columna, sección severamente asimétrica — miembro no soldado: figura F.5.4.5-3 (b); miembro "
            "soldado: figura F.5.4.5-3 (c). "
            "Pandeo torsional, generalmente — miembro no soldado: figura F.5.4.7-2(a). "
            "Pandeo torsional, sección compuesta por aletas salientes (véase F.5.4.7.5(b)) — miembro no soldado: "
            "figura F.5.4.7-2 (b). "
            "NOTA 1: Un miembro a compresión debe ser generalmente considerado como soldado en esta tabla, si "
            "contiene soldaduras en una longitud mayor que la mayor dimensión de la sección. Esto se hace haya o no "
            "zona afectada por el calor. "
            "NOTA 2: Una sección ligeramente asimétrica es aquella para la cual y1/y2 es menor o igual a 1.5; y1 y "
            "y2 son las distancias desde el eje de pandeo a las fibras extremas más lejana y más cercana, "
            "respectivamente. En otro caso, la sección se debe tratar como severamente asimétrica. "
            "El valor de p1 debe generalmente determinarse como se indica a continuación (para secciones compuestas "
            "por aletas salientes consulte el literal (b) de este numeral). "
            "(1) Sección compacta, sin efectos de zona afectada por el calor: p1 = po  (F.5.4.7-7). "
            "(2) Otras secciones, generalmente: p1 = (Ae/A) po  (F.5.4.7-8). "
            "Donde: A = área bruta de la sección. Ae = área de la sección efectiva (véase el literal (a) de este "
            "numeral). po = esfuerzo límite para el material (véanse las tablas F.5.4.2-1 y F.5.4.2-2). "
            "La selección de la curva sobre esta base es válida siempre que el miembro cumpla las tolerancias de "
            "rectitud y torcedura establecidas para el material extruído. Cuando exista la posibilidad de que un "
            "miembro a compresión fabricado no cumpla estas tolerancias, p1 debe tomarse como s veces el valor dado "
            "por F.5.4.7-7 o F.5.4.7-8, donde: S = 0.6 + 0.5^(-0.02λ) ≤ 1.0  (F.5.4.7-9)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_5a", "seccion": "F.5.4.7.5(a)",
        "titulo": "F.5.4.7.5(a) — Sección efectiva: 3 casos (esbelta libre de ablandamiento, compacta con ablandamiento, esbelta con ablandamiento)",
        "texto": (
            "(a) Sección efectiva — La sección efectiva se aplica a las siguientes secciones de miembros a "
            "compresión: clasificadas como esbeltas; afectadas por ablandamiento en la zona afectada por el calor; "
            "las dos anteriores. "
            "La sección efectiva puede obtenerse tomando el espesor reducido, sin reducción por agujeros, como se "
            "enuncia a continuación. Puede basarse en la sección transversal menos favorable (para miembros "
            "soldados, véase el literal (c) de este mismo numeral). "
            "(1) Sección esbelta libre de ablandamiento en la zona afectada por el calor — El espesor de cualquier "
            "elemento se toma como kL veces su espesor real t, donde kL se encuentra como indica en F.5.4.3.4. En "
            "el caso de elementos reforzados, kL debe aplicarse al área del refuerzo tanto como al espesor básico "
            "de la lámina. "
            "(2) Sección compacta con ablandamiento en la zona afectada por el calor — El espesor de cualquier zona "
            "ablandada debe reducirse de manera que se le dé un área supuesta de kz veces su área real. La "
            "extensión de tal zona debe encontrarse como se indica en F.5.4.4.3 y el valor de kz, como en F.5.4.4.2. "
            "(3) Sección esbelta con ablandamiento en la zona afectada por el calor — Para elementos esbeltos "
            "libres de efectos de zona afectada por el calor, el espesor reducido se determina de acuerdo con (1). "
            "Para regiones afectadas por el calor no localizadas, en elementos esbeltos, se toma de acuerdo con "
            "(2). Si un elemento es esbelto y está afectado por ablandamiento en la zona afectada por el calor, el "
            "espesor reducido se toma como el valor menor entre kL t y kz t en la parte ablandada y como kL t en "
            "las demás zonas de él. "
            "Las secciones compuestas por aletas salientes se tratan especialmente (en el literal siguiente)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_5b", "seccion": "F.5.4.7.5(b)",
        "titulo": "F.5.4.7.5(b) — Secciones compuestas por aletas salientes: aletas no reforzadas (1) vs. reforzadas en la punta (2)",
        "texto": (
            "(b) Secciones compuestas por aletas salientes — Para secciones tales como ángulos, secciones T y "
            "cruciformes, compuestas enteramente por elementos salientes radiantes, los pandeos local y torsional "
            "están estrechamente relacionados. Para tales miembros a compresión, el procedimiento a seguir será: "
            "(1) Sección que contiene sólo aletas salientes no reforzadas: (i) Para considerar el pandeo torsional, "
            "se puede usar la figura F.5.4.7-2 (b) para encontrar ps, en lugar de la figura F.5.4.7-2 (a). (El "
            "diagrama apropiado para pandeo como columna permanece inalterado). (ii) Para determinar p1, que se "
            "necesita para seleccionar la curva apropiada en las figuras F.5.4.5-3 y F.5.4.7-2, el área Ae debe "
            "basarse en la sección efectiva en la cual la reducción normal se hace por zonas afectadas por "
            "ablandamiento causado por el calor pero no hay reducción por pandeo local, esto es, tomar kL=1. De "
            "este modo, para una sección libre de efectos en la zona afectada por el calor: p1 = po. "
            "(2) Sección que contiene aletas salientes con refuerzo en la punta — Si los elementos salientes en "
            "forma de aletas reforzadas son tales que el modo 1 sería crítico en términos de pandeo local (véase el "
            "literal (b) de F.5.4.3.2), se sigue el mismo procedimiento descrito para la sección solo aletas "
            "salientes no reforzadas. Pero si el modo 2 es crítico, se debe emplear la figura F.5.4.7-2 (a) y la "
            "sección efectiva se determina como en el literal (a) de este numeral."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_5c", "seccion": "F.5.4.7.5(c)",
        "titulo": "F.5.4.7.5(c) — Miembros con soldaduras localizadas: caso de restricción al desplazamiento pero no al giro en los extremos",
        "texto": (
            "(c) Miembros a compresión que contienen soldaduras localizadas — La selección de la curva de miembros "
            "a compresión para un miembro afectado por ablandamiento en la zona afectada por el calor debe, por lo "
            "general, basarse en un valor de p1 obtenido para la sección más desfavorable, aún cuando tal "
            "ablandamiento ocurra sólo localmente a lo largo de la longitud. Esto incluye los efectos de zona "
            "afectada por el calor, debidos a la soldadura de accesorios temporales. "
            "Sin embargo, cuando tal ablandamiento causado por el calor tiene una cierta localización específica a "
            "lo largo de la longitud, su presencia puede ser ignorada para considerar el pandeo general siempre y "
            "cuando dicho ablandamiento no se extienda longitudinalmente una distancia mayor que el menor ancho "
            "total del miembro. La localización del ablandamiento causado por el calor, para permitir ésto, es la "
            "posición de curvatura cero o cercana a cero en la forma pandeada del miembro a compresión. Así, para "
            "un miembro a compresión restringido al desplazamiento pero no al giro en sus extremos (véase tabla "
            "F.5.4.7-1, caso 3) se puede suponer que la resistencia a pandeo general no se ve afectada por la "
            "presencia de zonas de ablandamiento localizadas, si están localizadas en sus extremos. (En tal caso, "
            "sería importante hacer la revisión por aplastamiento local)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_6", "seccion": "F.5.4.7.6",
        "titulo": "F.5.4.7.6 — Aplastamiento local: PRS = pa·An·φ (sección compacta) o pa·Ane·φ (otras secciones) — ecuaciones F.5.4.7-10/11",
        "texto": (
            "F.5.4.7.6 — Aplastamiento local — La fuerza axial P bajo carga mayorada no debe exceder la resistencia "
            "de diseño PRS de la sección más desfavorable a lo largo de la longitud del miembro a compresión y "
            "determinada así: "
            "(a) Sección compacta libre de efectos de zona afectada por el calor: PRS = pa An φ  (F.5.4.7-10). "
            "(b) Otras secciones, generalmente: PRS = pa Ane φ  (F.5.4.7-11). "
            "Donde: pa = esfuerzo límite (véanse las tablas F.5.4.2-1 y F.5.4.2-2). An = área de la sección neta, "
            "con reducción por agujeros no rellenos. Ane = área de la sección neta efectiva. φ = coeficiente de "
            "reducción de capacidad (véase la tabla F.5.3.3-1). "
            "El área Ane debe tomarse como Ae menos una reducción por agujeros no rellenos, donde Ae es el área "
            "efectiva usada para considerar el pandeo general (como columna y torsional), véanse los literales (a) "
            "y (b) de F.5.4.7.5. Para agujeros localizados en regiones de espesor reducido, la reducción puede "
            "hacerse con base en el espesor reducido en lugar del espesor total."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_7", "seccion": "F.5.4.7.7",
        "titulo": "F.5.4.7.7 — Secciones híbridas: promedio ponderado de po por áreas brutas (pandeo general) o suma de resistencias (aplastamiento local)",
        "texto": (
            "F.5.4.7.7 — Secciones híbridas — En miembros a compresión que contienen materiales base de diferentes "
            "resistencias, cada elemento debe ser clasificado de acuerdo con su valor particular de po. "
            "La resistencia PR a pandeo general como columna o torsional se puede determinar suponiendo un valor "
            "uniforme de po igual al promedio ponderado de los valores de po para las diferentes partes (ponderado "
            "de acuerdo con las áreas brutas). "
            "La resistencia al aplastamiento local, PRS, puede encontrarse sumando la resistencia de las diferentes "
            "partes."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_8", "seccion": "F.5.4.7.8",
        "titulo": "F.5.4.7.8 — Ciertas clases de miembros a compresión excéntricamente conectados: procedimiento simplificado (a) un solo vano, (b) doble espalda con espalda",
        "texto": (
            "F.5.4.7.8 — Ciertas clases de miembros a compresión excéntricamente conectados. "
            "(a) Miembros a compresión de un solo vano excéntricamente conectados pueden ser tratados usando un "
            "método simple en lugar del procedimiento de interacción dado en F.5.4.8, siempre y cuando la fijación "
            "sea suficiente para prevenir la rotación en el plano del elemento conectado y si no se aplica "
            "deliberadamente flexión: ángulo simple conectado por un lado únicamente; ángulos espalda con espalda "
            "conectados por un lado de una cartela; canal simple conectado por su alma únicamente; T simple "
            "conectada por su aleta únicamente. "
            "Para éstos se permite, para la revisión por pandeo como columna fuera del plano del elemento o "
            "elementos unidos, ignorar la excentricidad de la carga y, en su lugar, tomar una resistencia a "
            "compresión axial reducida igual al 40% del valor que se obtendría para carga centroidal usando el "
            "radio de giro respecto al eje paralelo a la platina de conexión. La resistencia a pandeo torsional se "
            "supone que no se afecta por la excentricidad. "
            "(b) Miembros a compresión conformados por dos componentes espalda con espalda — Tales miembros a "
            "compresión de doble ángulo, canal o T conectados a cada lado de platinas de conexión en los extremos, "
            "se pueden diseñar como miembros monolíticos centroidalmente cargados siempre que lo siguiente ocurra: "
            "los dos componentes estén seguramente conectados en sus extremos, y estén también conectados en los "
            "puntos tercios usando espaciadores de igual espesor que la platina de conexión."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_7_9", "seccion": "F.5.4.7.9",
        "titulo": "F.5.4.7.9 — Miembros a compresión con presillas: 7 condiciones (a-g), ecuaciones F.5.4.7-12/13",
        "texto": (
            "F.5.4.7.9 — Miembros a compresión con presillas — Las reglas generales para miembros a compresión "
            "dadas en F.5.4.7.2 a F.5.4.5.6 no se aplican generalmente a miembros con presillas, éstos deben "
            "someterse a un estudio especial. No obstante, si un miembro a compresión con presillas cumple con "
            "ciertas condiciones, se permite tratarlo como monolítico y obtener su resistencia en la forma normal. "
            "Para ser tratado como un miembro monolítico, un miembro a compresión con presillas debe satisfacer lo "
            "siguiente: "
            "(a) Debe estar cargado axialmente. "
            "(b) Debe consistir de dos componentes principales unidos por presillas igualmente espaciadas. La "
            "sección transversal debe ser simétrica respecto a un eje normal a las presillas. "
            "(c) Las presillas deben ir generalmente en pares. Sin embargo, si los componentes principales son "
            "secciones T o ángulos punta a punta, se permiten presillas simples. "
            "(d) λ2 ≤ 0.8λ1  (F.5.4.7-12). Donde: λ1, λ2 = parámetros de esbeltez para pandeo como columna del "
            "miembro completo respecto a los ejes paralelo y normal a las presillas respectivamente. "
            "(e) λ3 ≤ 0.7λ2  (F.5.4.7-13). Donde: λ3 = parámetro de esbeltez para pandeo como columna del uno de "
            "los componentes principales entre presillas, basado en el pandeo como columna o torsional, el que sea "
            "más crítico. "
            "(f) El sistema de presillas debe diseñarse para resistir una fuerza cortante total V en el plano de "
            "las presillas, tomada como el 2.5% de la fuerza axial en el miembro completo bajo carga mayorada. "
            "(g) La conexión de cada presilla a cada componente principal debe diseñarse para transmitir las "
            "siguientes acciones simultáneas bajo carga mayorada: un cortante longitudinal de Vd/Na; un momento de "
            "Vd/2N actuando en el plano de las presillas. Donde: d = espaciamiento longitudinal entre centros de "
            "presillas. a = espaciamiento de los componentes principales medido hasta los centroides de las "
            "conexiones de cada presilla. N = número de presillas en cada posición (1 ó 2). "
            "Para diseñar las presillas es importante considerar los posibles efectos de debilitamiento por pandeo "
            "local y ablandamiento en la zona afectada por el calor (si es soldado)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_8_1", "seccion": "F.5.4.8.1",
        "titulo": "F.5.4.8 — Flexión con fuerza axial y flexión biaxial. F.5.4.8.1 — Generalidades: casos A/B/C/D de acciones combinadas, dos revisiones",
        "texto": (
            "F.5.4.8 — FLEXIÓN CON FUERZA AXIAL Y FLEXIÓN BIAXIAL. "
            "F.5.4.8.1 — Generalidades — Este numeral da las fórmulas de interacción para revisar miembros sujetos "
            "a los siguientes casos de acción efecto combinados: "
            "(a) Caso A, flexión respecto al eje mayor con fuerza axial (Mx + P). "
            "(b) Caso B, flexión respecto al eje menor con fuerza axial (My + P). "
            "(c) Caso C, flexión biaxial (Mx + My). "
            "(d) Caso D, flexión biaxial con fuerza axial (Mx + My + P). "
            "Donde: P = fuerza axial bajo carga mayorada. Mx, My = momentos uniaxiales respecto de los ejes mayor y "
            "menor respectivamente, bajo carga mayorada. "
            "En general, se necesitan dos revisiones: (a) Revisión de la sección (véase F.5.4.8.3). (b) Revisión "
            "por pandeo general (véase F.5.4.8.4). "
            "La revisión de la sección siempre es necesaria. La revisión por pandeo general puede ser obviada en "
            "las siguientes circunstancias: (1) En el caso A, cuando P es de tensión y también el miembro está "
            "exento de pandeo torsional lateral (véase F.5.4.5.6). (2) En el caso B, cuando P es de tensión. "
            "En la revisión de la sección, los valores tomados para PRS, MRSx y MRSy deben tener en cuenta la "
            "presencia de agujeros y de ablandamiento en la zona afectada por el calor, donde: PRS = resistencia "
            "axial de diseño de la sección transversal, véase F.5.4.6.1 (tensión) o F.5.4.7.6 (compresión). "
            "MRSx, MRSy = resistencias de diseño a momento uniaxial de la sección transversal (véase F.5.4.5.2), "
            "ajustadas para tener en cuenta cortante coincidente si es necesario (véase F.5.4.5.4), respecto al eje "
            "mayor y menor, respectivamente. "
            "Para hacer la revisión por pandeo general, los valores de MRSx y MRSy deben, por lo general, referirse "
            "a la sección más desfavorable en el vano considerado, tomando en cuenta el pandeo local y el "
            "ablandamiento de la zona afectada por el calor pero ignorando los agujeros. El ablandamiento en la "
            "zona afectada por el calor puede ignorarse cuando ocurre en los extremos de la luz, esto quiere decir, "
            "no en voladizo, vano. "
            "Para secciones exentas de pandeo torsional lateral (véase F.5.4.5.6), MRx debe tomarse igual a MRSx, "
            "donde MRx = resistencia de diseño a momento para pandeo torsional lateral (véase el literal (a) de "
            "F.5.4.5.6)."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")


if __name__ == "__main__":
    main()
