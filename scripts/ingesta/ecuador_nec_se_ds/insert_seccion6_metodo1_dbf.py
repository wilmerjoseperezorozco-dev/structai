"""
Inserta el núcleo verbatim real de la Sección 6 (Método 1: Diseño Basado en
Fuerzas, DBF) de la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks.

Sección elegida por ser la más extensa de lo que faltaba (18 páginas,
páginas 56-74 del documento, la más pesada del cuerpo restante -- ver
project_structai_replicabilidad_paises.md, "elige lo más pesado y vamos
disminuyendo"). Es el método de cálculo estructural principal de la norma --
equivalente al Capítulo IV de la E.030 peruana ya cargado.

Texto extraído del mismo PDF oficial MIDUVI/MIT ya usado para el resto de
Ecuador (mit.gob.ec/MTOP_NEC-SE-DS.pdf, 139 páginas, extracción limpia
confirmada). Disciplina aplicada tras el hallazgo de _fix_tabla13_*.py:
cada número de tabla se verifica contra el CAPTION que la propia tabla trae
justo debajo de sus datos, nunca contra una referencia cruzada en otro
punto del texto ni contra el índice de tablas (ambos han demostrado tener
desfases reales en este documento).

Nota de alcance: el coeficiente R (Tabla 13, sección 6.3.4) ya se cargó por
separado en los scripts de corrección (_fix_tabla13_r_edificacion_y_tabla15_no_edificacion.py
y _fix_tabla13_ductilidad_limitada_y_referencias_cruzadas.py) -- este script
NO repite esa tabla, cubre el resto de la Sección 6 (6.1, 6.2, 6.3.1-6.3.3,
6.3.5-6.3.10).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion6_metodo1_dbf.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 6 — Método 1: Diseño Basado en Fuerzas (DBF)"

CHUNKS = [
    {
        "id": "NECSEDS-S6_1_1_6_1_2-OBJETIVOS_LIMITES_DBF",
        "seccion": "6.1.1-6.1.2",
        "titulo": "DBF — Objetivos generales y requisitos (RDBF/DDBF); límites del método",
        "texto": (
            "NEC-SE-DS, Sección 6.1.1 — Objetivos generales y requisitos. "
            "Las estructuras deben diseñarse para resistir fuerzas sísmicas "
            "provenientes de las combinaciones de las fuerzas horizontales "
            "actuantes (sección 3.5.1). Se asumirá que las fuerzas sísmicas "
            "de diseño actúan de manera no concurrente en la dirección de "
            "cada eje principal de la estructura.\n\n"
            "Objetivos principales del DBF: tomar en cuenta los niveles de "
            "amenaza sísmica (sección 4.2.2); determinar las fuerzas "
            "sísmicas de diseño (fuerza lateral equivalente); RDBF — "
            "verificar que los efectos del sismo E ≤ Rd (resistencia de "
            "cálculo del elemento, según NEC-SE-HM, NEC-SE-AC, NEC-SE-MP y "
            "NEC-SE-MD, usando modelos elásticos lineales); DDBF — "
            "verificar las deformaciones, en particular las derivas máximas "
            "de la estructura.\n\n"
            "Sección 6.1.2 — Límites del DBF. El DBF presenta limitaciones: "
            "utiliza factores de reducción R constantes por tipología "
            "estructural (asume que la demanda de ductilidad y la "
            "sobre-resistencia son iguales para todos los edificios de una "
            "misma categoría, y que R no cambia con el periodo ni el tipo "
            "de suelo); supone que la rigidez es independiente de la "
            "resistencia. Nota: el DBD (sección 7) resuelve estos problemas "
            "porque la reducción espectral se calcula en función de la "
            "demanda de ductilidad caso por caso, y la rigidez no se asume "
            "al inicio sino que es un producto del diseño."
        ),
    },
    {
        "id": "NECSEDS-S6_1_3_6_1_5-REQUISITOS_APLICACION",
        "seccion": "6.1.3-6.1.5",
        "titulo": "DBF — Requisito RDBF (fuerzas internas), DDBF (derivas), condiciones de aplicación",
        "texto": (
            "NEC-SE-DS, Sección 6.1.3 — Requisito RDBF: fuerzas internas "
            "(solicitaciones mecánicas). Implica el cálculo de las fuerzas "
            "internas en cada elemento estructural (NEC-SE-HM, NEC-SE-AC, "
            "NEC-SE-MP, NEC-SE-MD). Los resultados totales del análisis "
            "deben incluir: deflexiones, derivas, fuerzas en pisos y "
            "elementos, momentos, cortantes de piso, cortante en la base.\n\n"
            "Sección 6.1.4 — Requisito DDBF: derivas de piso. Las "
            "deformaciones generadas por las fuerzas sísmicas se calculan "
            "según el tipo de material y estructura (NEC-SE-HM, NEC-SE-AC, "
            "NEC-SE-MP, NEC-SE-MD).\n\n"
            "Sección 6.1.5 — Condiciones de aplicación: regularidad y "
            "categoría de importancia. Se usará preferencialmente el DBF "
            "para edificios de uso normal, favoreciendo otros métodos para "
            "estructuras esenciales o de ocupación especial. Se permite "
            "recurrir al DBF para estructuras irregulares y todo tipo de "
            "estructura, calculando el corte basal con coeficientes "
            "dedicados a esas configuraciones más desfavorables — el "
            "diseñador deberá justificar el uso del método. También pueden "
            "usarse procedimientos alternativos con adecuado fundamento en "
            "dinámica de estructuras, llevados a cabo por un profesional "
            "especializado."
        ),
    },
    {
        "id": "NECSEDS-S6_1_6_6_1_8-MODELACION_W_AGRIETADAS",
        "seccion": "6.1.6-6.1.8",
        "titulo": "DBF — Modelación estructural, carga sísmica reactiva W, secciones agrietadas (concreto y mampostería)",
        "texto": (
            "NEC-SE-DS, Sección 6.1.6 — Modelación estructural. El modelo "
            "matemático incluirá todos los elementos del sistema resistente "
            "y su distribución espacial de masas y rigideces.\n\n"
            "Sección 6.1.7 — Carga sísmica reactiva W. Caso general: "
            "W = D + 0,25 Li (D = carga muerta total, Li = carga viva del "
            "piso i). Casos especiales, bodegas y almacenaje: W = D + 0,5 Li.\n\n"
            "Sección 6.1.8 — Secciones agrietadas (inercia Ig). Se usan en "
            "particular en los métodos no lineales (6.2.2).\n"
            "a. Estructuras de hormigón armado: en el cálculo de rigidez y "
            "derivas máximas se usan las inercias agrietadas: 0,5 Ig para "
            "vigas (con contribución de losas cuando aplique); 0,8 Ig para "
            "columnas; 0,6 Ig para muros estructurales — en estructuras sin "
            "subsuelos, solo en los dos primeros pisos; con subsuelos, en "
            "los dos primeros pisos y el primer subsuelo; nunca en una "
            "altura menor que la longitud en planta del muro; el resto de "
            "pisos puede considerarse con la inercia no agrietada. En "
            "muros, el valor agrietado se aplica solo donde se espera "
            "rótula plástica por cargas sísmicas severas.\n"
            "b. Estructuras de mampostería: 0,5 Ig para muros con relación "
            "altura total/longitud > 3; no se necesita inercia agrietada "
            "para relación altura/longitud < 1,5; para relación entre 1,5 y "
            "3, el factor se obtiene por interpolación entre 1 y 0,5."
        ),
    },
    {
        "id": "NECSEDS-S6_2-MODELOS_ANALISIS_ESTATICO",
        "seccion": "6.2, 6.2.1",
        "titulo": "DBF — 3 modelos de análisis (estático, dinámico espectral, paso a paso); procedimiento estático",
        "texto": (
            "NEC-SE-DS, Sección 6.2 — Modelos de análisis de las fuerzas "
            "sísmicas usados con el DBF. El DBF presenta la misma "
            "metodología general para 3 métodos de análisis: (1) Estático; "
            "(2) No lineal — análisis dinámico espectral; (3) No lineal — "
            "análisis paso a paso en el tiempo. Se determina el espectro de "
            "diseño en aceleración Sa(T) a partir del PGA (aceleración "
            "sísmica esperada en roca).\n\n"
            "Sección 6.2.1 — Procedimiento estático. Se podrá aplicar para "
            "estructuras de ocupación normal. El factor Z (sección 3.1.1) "
            "se usa para definir el PGA y por ende el espectro Sa(T)."
        ),
    },
    {
        "id": "NECSEDS-S6_2_2ab-NOLINEAL_CONDICIONES_AJUSTE",
        "seccion": "6.2.2 (a-b)",
        "titulo": "DBF — Análisis espectral vs. paso a paso: condiciones de aplicación; ajuste del cortante basal dinámico",
        "texto": (
            "NEC-SE-DS, Sección 6.2.2.a — Procedimientos y condiciones de "
            "aplicación. Análisis espectral: para estructuras de ocupación "
            "especial, esenciales, puentes, obras portuarias y estructuras "
            "diferentes a las de edificación (curvas de peligro de la "
            "sección 3.1.2). Análisis paso a paso en el tiempo: para "
            "estructuras en suelo tipo F. Nota: para poblaciones con más de "
            "100.000 habitantes y suelo tipo F, se hace un espectro "
            "específico al sitio, basado en geología, tectónica, sismología "
            "y suelo local, con amortiguamiento de 5,00% salvo "
            "justificación distinta; para suelo F se desarrollan "
            "acelerogramas representativos de los terremotos reales "
            "esperados (secciones 3.2 y 10.6.4).\n\n"
            "6.2.2.b — Ajuste del corte basal de resultados dinámicos. El "
            "cortante dinámico total en la base, por cualquier método "
            "dinámico, no puede ser: < 80% del cortante estático V "
            "(estructuras regulares); < 90% del cortante estático V "
            "(estructuras irregulares). Ver sección 6.3.2 para la "
            "definición de V."
        ),
    },
    {
        "id": "NECSEDS-S6_2_2cde-CARGA_MODELO_ESPECTRAL",
        "seccion": "6.2.2 (c-e)",
        "titulo": "DBF — Representación de la carga horizontal (sismo de diseño, sin R); modelo matemático; procedimiento de análisis espectral",
        "texto": (
            "NEC-SE-DS, Sección 6.2.2.c — Representación y determinación de "
            "la carga sísmica horizontal. Debe representar como mínimo el "
            "sismo de diseño (periodo de retorno de 475 años), usando la "
            "fórmula general de 6.3.2, SIN aplicar el factor R.\n\n"
            "6.2.2.d — Modelo matemático. Caso general: incluye todos los "
            "elementos del sistema resistente y la distribución espacial de "
            "masas/rigideces, capaz de capturar el comportamiento dinámico "
            "significativo. Casos particulares: estructuras irregulares "
            "usan modelo tridimensional; hormigón armado y mampostería usan "
            "inercias agrietadas (ver 6.3).\n\n"
            "6.2.2.e — Procedimiento 1: análisis espectral. Espectro de "
            "respuesta: el elástico en aceleraciones de la sección 3.3.1, "
            "con las curvas de peligro de 3.1. Número de modos: todos los "
            "que contribuyan significativamente, hasta acumular al menos "
            "90% de la masa total en cada dirección horizontal principal. "
            "Reducción de fuerzas dinámicas: en ningún caso el cortante "
            "basal reducido puede ser menor que el cortante elástico "
            "dividido por R; R se aplica solo si la estructura cumple todos "
            "los requisitos de 4.2 y 6.3.4. También se modifican por I "
            "(sección 4.1) y ØEi/ØPi (sección 5.3). Torsión: se consideran "
            "los efectos torsionales, incluida la torsión accidental de "
            "6.3.7."
        ),
    },
    {
        "id": "NECSEDS-S6_2_2fgh-PASO_A_PASO_TIEMPO",
        "seccion": "6.2.2 (f-h)",
        "titulo": "DBF — Análisis no lineal paso a paso en el tiempo: revisión profesional obligatoria, acelerogramas grabados/artificiales, principios",
        "texto": (
            "NEC-SE-DS, Sección 6.2.2.f — Procedimiento no lineal 2: "
            "análisis paso a paso en el tiempo. Se usa para justificar un "
            "diseño que no pueda justificarse con el método estático o "
            "espectral. Requiere revisión por un profesional independiente "
            "con experiencia en métodos inelásticos, que certifique por "
            "escrito: revisión de criterios del espectro/acelerogramas, del "
            "diseño preliminar y del diseño final.\n\n"
            "Registros de acelerogramas grabados: se usan las 2 componentes "
            "horizontales de al menos 3 eventos sísmicos reales, obtenidos "
            "de la Red Nacional de Acelerógrafos (RNA), consistentes en "
            "magnitud/distancia/mecanismo de falla/efectos de suelo con el "
            "sismo de diseño (sección 10.6.4). Con 3 pares de registros: se "
            "toma la respuesta máxima. Con 7 o más: se usa el promedio.\n\n"
            "Acelerogramas artificiales: si no hay al menos 3 eventos "
            "reales, se simulan artificialmente. Los acelerogramas deben "
            "escalarse para que el promedio de sus espectros (raíz de la "
            "suma de cuadrados) no esté por debajo del espectro amortiguado "
            "al 5% del sismo de diseño entre 0,2T y 1,5T. Ambas componentes "
            "se aplican simultáneamente para considerar efectos "
            "torsionales.\n\n"
            "6.2.2.g-h — Principios de análisis paso a paso: los elásticos "
            "deben cumplir los requisitos de análisis dinámico y pueden "
            "reducirse igual que un análisis dinámico normal; los no "
            "lineales deben modelar capacidades y características de "
            "elementos de forma consistente con datos experimentales, y la "
            "respuesta máxima inelástica NO debe reducirse."
        ),
    },
    {
        "id": "NECSEDS-S6_3_1_6_3_2-PASOS_CORTANTE_BASAL_V",
        "seccion": "6.3.1-6.3.2",
        "titulo": "DBF — Los 5 pasos del método; fórmula del cortante basal de diseño V",
        "texto": (
            "NEC-SE-DS, Sección 6.3.1 — Pasos del método. El DBF asume que "
            "la respuesta estructural se constituye principalmente del "
            "primer modo de vibración (modo fundamental). Pasos: (1) "
            "determinación del espectro de diseño Sa(T) según la geotécnia "
            "del sitio (sección 3.3); (2) cálculo aproximado del periodo "
            "fundamental Ta; (3) determinación del cortante basal V; (4) "
            "distribuciones vertical y horizontal de V; (5) dirección de "
            "aplicación y verificación de que las derivas no sobrepasen el "
            "valor permitido.\n\n"
            "Sección 6.3.2 — Cortante basal de diseño V. El cortante basal "
            "total de diseño V, a nivel de cargas últimas, se determina "
            "mediante: V = [Sa(Ta) · ØP · ØE / (R · I)] · W. Donde: Sa(Ta) = "
            "espectro de diseño en aceleración (sección 3.3.2); ØP y ØE = "
            "coeficientes de configuración en planta y elevación (sección "
            "5.3); I = coeficiente de importancia (sección 4.1); R = factor "
            "de reducción de resistencia sísmica (sección 6.3.4, Tabla 13); "
            "W = carga sísmica reactiva (sección 6.1.7); Ta = periodo de "
            "vibración (sección 6.3.3). El espectro de diseño se determina "
            "según 3.3.1: estructuras de ocupación normal usan el factor Z "
            "(3.1.1); estructuras esenciales/especiales usan las curvas de "
            "3.1.2 en vez del factor Z; suelos tipo F usan acelerogramas y "
            "espectros específicos al sitio (10.6.4)."
        ),
    },
    {
        "id": "NECSEDS-S6_3_3-PERIODO_VIBRACION_TA",
        "seccion": "6.3.3",
        "titulo": "DBF — Periodo de vibración Ta: Método 1 (Ct, α por tipo de estructura) y Método 2 (deflexión elástica)",
        "texto": (
            "NEC-SE-DS, Sección 6.3.3 — Determinación del periodo de "
            "vibración Ta. Se estima con uno de 2 métodos.\n\n"
            "Método 1 (edificación): Ta = Ct · hn^α, donde hn = altura "
            "máxima en metros, Ct y α dependen del tipo de estructura: "
            "acero sin arriostramientos Ct=0,072/α=0,8; acero con "
            "arriostramientos Ct=0,073/α=0,75; pórticos especiales de "
            "hormigón armado sin muros ni diagonales Ct=0,047/α=0,9; con "
            "muros estructurales o diagonales rigidizadoras (y otras "
            "estructuras basadas en muros/mampostería estructural) "
            "Ct=0,049/α=0,75. Alternativamente, para muros estructurales de "
            "hormigón armado o mampostería (con α=1), Ct se calcula con una "
            "fórmula que depende del área en planta AB, del número de "
            "muros nw, y de la altura/área de corte/longitud de cada muro "
            "(hwi, Awi, lwi).\n\n"
            "Método 2: Ta = 2π · √(Σ wi·δi² / Σ fi·δi), donde fi = "
            "distribución aproximada de fuerzas laterales en el piso i, δi "
            "= deflexión elástica del piso i con esas fuerzas, wi = peso "
            "asignado al piso i (fracción de W). El valor de Ta por Método "
            "2 no debe superar en más de 30% el valor por Método 1.\n\n"
            "Interacciones: una vez dimensionada la estructura, los "
            "periodos deben recalcularse por Método 2 o análisis modal, "
            "re-evaluando el cortante basal, hasta que la variación entre "
            "iteraciones consecutivas sea ≤ 10%."
        ),
    },
    {
        "id": "NECSEDS-S6_3_5_6_3_6-DISTRIBUCION_VERTICAL_HORIZONTAL",
        "seccion": "6.3.5-6.3.6",
        "titulo": "DBF — Distribución vertical de fuerzas laterales (fórmula, coeficiente k); distribución horizontal del cortante y excentricidad accidental",
        "texto": (
            "NEC-SE-DS, Sección 6.3.5 — Distribución vertical de fuerzas "
            "sísmicas laterales. Se asemeja a una distribución triangular "
            "dependiente de Ta. Fórmula: Fx = [wx·hx^k / Σ(wi·hi^k)] · V, "
            "donde V = cortante total en la base, wx/wi = peso en el piso "
            "x/i, hx/hi = altura del piso x/i, k = coeficiente según el "
            "periodo T: k=1 si T≤0,5s; k=0,75+0,50T si 0,5<T≤2,5s; k=2 si "
            "T>2,5s.\n\n"
            "Sección 6.3.6 — Distribución horizontal del cortante. El "
            "cortante de piso Vx se distribuye entre los elementos "
            "resistentes en proporción a sus rigideces (considerando "
            "rigidez del piso; en pisos flexibles, se toma en cuenta esa "
            "condición). La masa de cada nivel se considera concentrada en "
            "el centro de masas, desplazada un 5% de la máxima dimensión "
            "del edificio en ese piso (perpendicular a la dirección de "
            "análisis), para tomar en cuenta la torsión accidental — tanto "
            "en estructuras regulares como irregulares."
        ),
    },
    {
        "id": "NECSEDS-S6_3_7_6_3_8-TORSION_PDELTA",
        "seccion": "6.3.7-6.3.8",
        "titulo": "DBF — Torsión accidental y factor de amplificación Ax (máx. 3,0); efectos P-Δ, índice de estabilidad Qi (límite 0,30)",
        "texto": (
            "NEC-SE-DS, Sección 6.3.7 — Momentos torsionales horizontales y "
            "torsión accidental. El momento torsional de diseño se calcula "
            "por las excentricidades entre cargas laterales y elementos "
            "resistentes, más la torsión accidental (centro de masas "
            "desplazado, sección 6.3.6). Con irregularidad torsional, se "
            "incrementa mediante el factor de amplificación torsional "
            "Ax = [δmáx / (1,2·δprom)]², donde δprom = promedio de "
            "desplazamientos en los puntos extremos del nivel x, δmáx = "
            "desplazamiento máximo del nivel x. Ax no debe exceder 3,0. "
            "Para diseño se considera la carga más severa por elemento.\n\n"
            "Sección 6.3.8 — Efectos de segundo orden P-Δ e índice de "
            "estabilidad Qi. Qi = (Pi·Δi) / (Vi·hi), donde Pi = carga "
            "vertical total sin mayorar (muerta + viva) del piso i y "
            "superiores, Δi = deriva del piso i en el centro de masas, "
            "Vi = cortante sísmico del piso i, hi = altura del piso i. Debe "
            "cumplirse Qi ≤ 0,30. Nota: si Qi > 0,30, la estructura es "
            "potencialmente inestable y debe rigidizarse, salvo "
            "demostración más estricta de estabilidad. Los efectos P-Δ no "
            "se consideran si Qi<0,1; entre 0,1 y 0,3 se aplica un factor "
            "de mayoración fP-Δ = 1 / (1 - Qi) a las derivas, fuerzas "
            "internas y momentos."
        ),
    },
    {
        "id": "NECSEDS-S6_3_9-CONTROL_DERIVA_MAXIMA",
        "seccion": "6.3.9",
        "titulo": "DBF — Control de deriva de piso: ΔM = 0,75·R·ΔE, límite según Tabla 14",
        "texto": (
            "NEC-SE-DS, Sección 6.3.9 — Control de la deriva de piso "
            "(derivas inelásticas máximas de piso ΔM). Se calcula la "
            "respuesta máxima inelástica en desplazamientos ΔM causada por "
            "el sismo de diseño, asumiendo secciones agrietadas (6.1.8). "
            "Las derivas de las fuerzas laterales reducidas por el DBF "
            "(estáticas o dinámicas) se calculan por piso mediante análisis "
            "elástico, incluyendo: deflexiones traslacionales y "
            "torsionales (6.3.7) y efectos P-Δ (6.3.8). Nota: en pórticos "
            "metálicos se debe considerar la deformación de las conexiones.\n\n"
            "Límite de la deriva: ΔM = 0,75 · R · ΔE, donde ΔE = "
            "desplazamiento obtenido con las fuerzas laterales de diseño "
            "reducidas. ΔM no puede superar los valores de la Tabla 14 "
            "(Límites de deformación unitaria), que deben satisfacerse en "
            "todas las columnas del edificio, y debe cumplirse "
            "ΔM < Δmáxima (determinada según la sección 5.1)."
        ),
    },
]


MAX_TOKENS_POR_SUBCHUNK = 110


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"][:500],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens: {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("ecuador_nec_se_ds_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en ecuador_nec_se_ds_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
