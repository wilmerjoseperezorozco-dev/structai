"""
REEMPLAZA el Capítulo IV (Análisis Estructural) de peru_e030_chunks con
el texto vigente de la E.030 modificada por la RM 183-2026-VIVIENDA --
tercer capítulo de la reingesta gradual (issue #13, ver
reemplaza_capitulo2_peligro_sismico.py y
reemplaza_capitulo3_categoria_sistema_regularidad.py para el contexto
completo de la estrategia, no repetido aquí).

ESTRATEGIA DE REEMPLAZO: se ELIMINAN los 50 chunks viejos con prefijo
"E030-CAP4-*" (numeración 2019: Artículos 24-30) y se insertan los
nuevos con prefijo "E030-2026-CAP4-*" (numeración 2026: Artículos
28-49 -- el capítulo creció de 7 a 22 artículos, principalmente por
desagregar cada numeral en su propio artículo).

HALLAZGO IMPORTANTE de este capítulo: es el más denso en fórmulas de
toda la norma, y también el que MÁS contenido tiene CONFIRMADO SIN
CAMBIO real (verificado comparando explícitamente contra los chunks
viejos antes de escribir, no asumido):
- V = Z·U·C·S/R · P (fuerza cortante en la base) -- idéntica.
- C/R ≥ 0,11 -- idéntico.
- CT = 35/45/60 (período fundamental) -- idéntico, mismas categorías.
- Fórmula de Rayleigh para T -- idéntica.
- Excentricidad accidental ei = 0,05 · dimensión -- idéntica.
- Fuerza sísmica vertical = 2/3 · Z·U·S -- idéntica.
- Fuerza cortante mínima: 80% (regular) / 90% (irregular) -- idéntica.
Es decir: el Capítulo IV NO tiene los cambios sustantivos de valores
que sí tuvieron los Capítulos II (suelos) y III (R0 ductilidad
limitada) -- el cambio aquí es de renumeración y de desagregación del
texto, no de contenido técnico. Se documenta así explícitamente para
no sugerir cambios donde no los hay.

BONUS: el viejo chunk `E030-CAP4-ART29_4_5-CORTANTE_MINIMA_EXCENTRICIDAD-01/02`
tenía una nota de transcripción sobre una referencia cruzada interna
del documento 2019 que decía "artículo 25" donde por contexto se
esperaría "artículo 28" (ver memoria del proyecto). En la edición 2026
esa referencia (artículo 44.1) apunta correctamente al artículo 34
(cortante en la base) -- la inconsistencia queda resuelta por la
renumeración, no hace falta seguir arrastrando la nota.

Uso: python scripts/ingesta/peru_e030/reemplazo_2026/reemplaza_capitulo4_analisis_estructural.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 (ed. 2026, RM 183-2026-VIVIENDA) — Capítulo IV: Análisis Estructural"

IDS_VIEJOS_A_ELIMINAR_PREFIJO = "E030-CAP4-"

CHUNKS = [
    {
        "id": "E030-2026-CAP4-ART28-CONSIDERACIONES_GENERALES",
        "seccion": "Artículo 28 (ed. 2026)",
        "titulo": "Análisis con 100%+30% en direcciones ortogonales; direcciones no paralelas si aplica Tabla 12; solicitaciones verticales en voladizos/pretensados; remisión al Anexo I",
        "texto": (
            "E.030 (edición 2026, RM 183-2026-VIVIENDA), Artículo 28 — "
            "Consideraciones generales para el análisis estructural. El "
            "análisis en cada dirección predominante se realiza por "
            "fuerzas estáticas equivalentes o por combinación modal "
            "espectral, con 100% de las solicitaciones en una dirección "
            "y 30% en la dirección perpendicular. Para estructuras con "
            "sistemas no paralelos en planta (Tabla N°12), se considera "
            "además que las acciones sísmicas ocurren en las "
            "direcciones de los ejes no paralelos. La excentricidad "
            "accidental (artículos 37 y 45) solo se aplica en la "
            "dirección perpendicular a aquella donde se aplica el 100% "
            "de la acción sísmica.\n\n"
            "Se consideran las solicitaciones sísmicas verticales en "
            "elementos verticales, elementos horizontales de gran luz, "
            "elementos pre/post tensados, y voladizos — actuando "
            "simultáneamente con las fuerzas horizontales en el sentido "
            "más desfavorable. En tiempo-historia, se considera la "
            "acción simultánea en todas las componentes, sin excepción "
            "de regularidad. Las acciones sísmicas de edificaciones "
            "nuevas se determinan según el procedimiento del Anexo I, u "
            "otro que el proyectista determine cumpliendo esta norma."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART29_30-ESFUERZOS_ADMISIBLES_MODELOS",
        "seccion": "Artículos 29-30 (ed. 2026)",
        "titulo": "Verificación por esfuerzos admisibles: fuerzas ×0,8; modelo de análisis: secciones brutas sin fisurar, diafragma rígido, tabiquería no aislada, interacción de muros H/T/L",
        "texto": (
            "Artículo 29 — Diseño y verificación de esfuerzos "
            "admisibles. Las fuerzas sísmicas obtenidas con esta norma "
            "se multiplican por 0,8 al verificar por esfuerzos "
            "admisibles.\n\n"
            "Artículo 30 — Modelos para el análisis. El modelo debe "
            "representar la distribución espacial de masas y rigideces "
            "significativa del comportamiento dinámico. Concreto armado "
            "y albañilería se analizan con las inercias de secciones "
            "brutas, ignorando fisuración y refuerzo. Si el proyectista "
            "determina diafragmas rígidos, puede usarse un modelo de "
            "masas concentradas con 3 grados de libertad por diafragma "
            "(2 traslaciones horizontales + 1 rotación); si el diafragma "
            "no es rígido, se debe considerar su flexibilidad. El "
            "modelo debe incluir la tabiquería no aislada debidamente, "
            "verificando con y sin tabiquería. En edificios con muros "
            "predominantes, se debe modelar la interacción entre muros "
            "en direcciones perpendiculares (muros en H, T, L). No se "
            "incluye la rigidez de las losas fuera de su plano (pueden "
            "modelarse como alas de vigas T o L, confinadas con "
            "estribos)."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART31-ESTIMACION_PESO",
        "seccion": "Artículo 31 (ed. 2026)",
        "titulo": "Peso P: carga permanente + fracción de carga viva (50% categorías A/B, 25% categoría C, 80% depósitos, 25% azoteas, 100% tanques/silos)",
        "texto": (
            "Artículo 31 — Estimación del peso (P). Se calcula "
            "adicionando a la carga permanente total un porcentaje de "
            "la carga viva:\n"
            "  Edificaciones categorías A y B: 50% de la carga viva.\n"
            "  Edificaciones categoría C: 25% de la carga viva.\n"
            "  Depósitos: 80% del peso total posible a almacenar.\n"
            "  Azoteas y techos en general: 25% de la carga viva.\n"
            "  Tanques, silos y estructuras similares: 100% de la carga "
            "que puedan contener."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART32_33-PROCEDIMIENTOS_ANALISIS_ESTATICO",
        "seccion": "Artículos 32-33 (ed. 2026)",
        "titulo": "2 procedimientos (estático/dinámico modal espectral); estático aplica en zona 1 siempre, en otras zonas solo si regular ≤30m o muros portantes ≤15m",
        "texto": (
            "Artículo 32 — Procedimientos de análisis sísmico: (a) "
            "análisis estático o de fuerzas estáticas equivalentes; (b) "
            "análisis dinámico modal espectral. Ambos usan modelo lineal "
            "elástico con solicitaciones reducidas. El análisis "
            "tiempo-historia (Subcapítulo 3) puede usarse como "
            "verificación, pero NO sustituye a los dos anteriores.\n\n"
            "Artículo 33 — Consideraciones básicas para el análisis "
            "estático. Representa las solicitaciones con fuerzas en el "
            "centro de masas de cada nivel. Puede usarse en TODAS las "
            "estructuras (regulares o irregulares) en zona sísmica 1. "
            "En las demás zonas, solo para estructuras regulares "
            "(artículo 23) de no más de 30 m de altura, y para muros "
            "portantes de concreto armado/albañilería armada o "
            "confinada de no más de 15 m de altura (aunque sean "
            "irregulares). El análisis se hace con 100%+30% en "
            "direcciones ortogonales, sumando valores absolutos."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART34-CORTANTE_BASAL",
        "seccion": "Artículo 34 (ed. 2026)",
        "titulo": "Fuerza cortante en la base V=Z·U·C·S/R·P (⚠️ CONFIRMADO SIN CAMBIO respecto a 2019); C=2,5 si T<TP; límite C/R≥0,11 (también sin cambio)",
        "texto": (
            "Artículo 34 — Fuerza cortante en la base. La fuerza "
            "cortante total en la base, para la dirección considerada, "
            "se determina con: V = (Z·U·C·S/R) · P. Cuando el período "
            "fundamental T sea menor que TP, se usa C=2,5. El valor de "
            "C/R debe cumplir: C/R ≥ 0,11.\n\n"
            "Nota de verificación: esta fórmula y el límite C/R≥0,11 se "
            "compararon explícitamente contra el texto de la edición "
            "2019 (ya cargado en este corpus antes del reemplazo) y "
            "están CONFIRMADOS SIN CAMBIO — el artículo se renumeró de "
            "28.2 (2019) a 34 (2026), pero el contenido técnico es "
            "idéntico."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART35_36-DISTRIBUCION_ALTURA_PERIODO",
        "seccion": "Artículos 35-36 (ed. 2026)",
        "titulo": "Distribución de fuerzas Fi=αi·V (exponente k=1,0 si T≤0,5s, k=0,75+0,5T≤2,0 si T>0,5s); período T=hn/CT (CT=35/45/60, ⚠️ sin cambio) y fórmula de Rayleigh alternativa",
        "texto": (
            "Artículo 35 — Distribución de la fuerza sísmica en altura. "
            "Las fuerzas horizontales en el nivel i se calculan con "
            "Fi = αi · V, donde αi es la fracción del cortante basal V "
            "asignada al nivel i según su peso Pi y altura hi elevada a "
            "la potencia k, ponderada sobre la suma de todos los "
            "niveles. El exponente k depende del período fundamental T: "
            "k=1,0 si T≤0,5 s; k=(0,75+0,5·T)≤2,0 si T>0,5 s.\n\n"
            "Artículo 36 — Período fundamental de vibración. Se estima "
            "con T = hn/CT. Valores de CT (verbatim, ⚠️ CONFIRMADOS SIN "
            "CAMBIO respecto a 2019): CT=35 para pórticos de concreto "
            "armado sin muros de corte, o pórticos dúctiles de acero sin "
            "arriostramiento. CT=45 para pórticos de concreto con muros "
            "en cajas de ascensores/escaleras, o pórticos de acero "
            "arriostrados. CT=60 para albañilería y todos los edificios "
            "de concreto armado duales, de muros estructurales, y muros "
            "de ductilidad limitada.\n\n"
            "Alternativamente, fórmula de Rayleigh: T = 2π√(Σ Pi·di² / "
            "g·Σ fi·di), con fi = fuerza lateral del primer modo, di = "
            "desplazamiento lateral del centro de masa (secciones sin "
            "fisurar). Si el análisis no considera la rigidez de "
            "elementos no estructurales no aislados, T se toma como "
            "0,85 del valor de la fórmula precedente."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART37_38-EXCENTRICIDAD_FUERZA_VERTICAL",
        "seccion": "Artículos 37-38 (ed. 2026)",
        "titulo": "Momento torsor accidental Mti=Fi·ei con ei=0,05·dimensión (⚠️ sin cambio); fuerza sísmica vertical = 2/3·Z·U·S (⚠️ sin cambio), análisis dinámico en luces grandes/volados",
        "texto": (
            "Artículo 37 — Excentricidad accidental. Para diafragmas "
            "rígidos, además de la fuerza Fi en el centro de masas, se "
            "aplica un momento torsor accidental Mti = Fi · ei, donde "
            "ei = 0,05 veces la dimensión del edificio en la dirección "
            "perpendicular al análisis. Las condiciones más "
            "desfavorables se obtienen con el mismo signo en todos los "
            "niveles, considerando solo los incrementos de fuerza "
            "horizontal.\n\n"
            "Artículo 38 — Fuerzas sísmicas verticales. La fuerza "
            "sísmica vertical se considera como una fracción del peso "
            "igual a 2/3 · Z·U·S. En elementos horizontales de grandes "
            "luces (incluidos volados) se requiere análisis dinámico "
            "con los espectros del artículo 41.\n\n"
            "Nota de verificación: ambas fórmulas (ei=0,05 y 2/3·Z·U·S) "
            "confirmadas SIN CAMBIO respecto a la edición 2019."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART39_40-MODAL_ESPECTRAL_MODOS",
        "seccion": "Artículos 39-40 (ed. 2026)",
        "titulo": "Cualquier estructura puede diseñarse por combinación modal espectral; modos con ≥90% de masa efectiva, mínimo 3 modos predominantes por dirección",
        "texto": (
            "Artículo 39 — Consideración general para el análisis "
            "dinámico modal espectral. Cualquier estructura puede "
            "diseñarse con los resultados de este método.\n\n"
            "Artículo 40 — Modos de vibración. Se determinan con un "
            "procedimiento que considere apropiadamente rigidez y "
            "distribución de masas. En cada dirección se consideran los "
            "modos cuya suma de masas efectivas sea al menos 90% de la "
            "masa total, tomando como mínimo los 3 primeros modos "
            "predominantes en esa dirección."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART41_42-ACELERACION_ESPECTRAL_CQC",
        "seccion": "Artículos 41-42 (ed. 2026)",
        "titulo": "Espectro inelástico de pseudo-aceleraciones Sa=ZUCS/Rg (componente vertical = 2/3 del horizontal); combinación modal por CQC (Combinación Cuadrática Completa)",
        "texto": (
            "Artículo 41 — Aceleración espectral. Para cada dirección "
            "horizontal se usa un espectro inelástico de "
            "pseudo-aceleraciones Sa = (Z·U·C·S/R)·g. Para la dirección "
            "vertical puede usarse un espectro con valores iguales a "
            "2/3 del espectro horizontal.\n\n"
            "Artículo 42 — Criterios de combinación. La respuesta "
            "máxima elástica esperada (fuerzas internas, cortante "
            "basal, cortantes de entrepiso, momentos de volteo, "
            "desplazamientos) se obtiene por Combinación Cuadrática "
            "Completa (CQC) de las respuestas modales, usando "
            "coeficientes de correlación entre modos que dependen de la "
            "razón de frecuencias ωi/ωj y del amortiguamiento (β=0,05 "
            "para todos los modos). [La expresión algebraica exacta de "
            "los coeficientes de correlación ρij no se pudo recuperar "
            "con precisión de esta extracción del PDF.] Alternativamente "
            "(42.3), la respuesta máxima puede estimarse como la raíz "
            "cuadrada de la suma de los cuadrados de las respuestas "
            "modales (SRSS)."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART43_44_45-COMBINACION_CORTANTE_MINIMA",
        "seccion": "Artículos 43-45 (ed. 2026)",
        "titulo": "Combinación direccional por SRSS (100%+30% ortogonal); fuerza cortante mínima 80% regulares / 90% irregulares (⚠️ sin cambio); excentricidad dinámica 0,05",
        "texto": (
            "Artículo 43 — Criterios de combinación direccional. La "
            "respuesta máxima esperada por la acción simultánea "
            "(100%+30% en direcciones ortogonales) se obtiene como raíz "
            "cuadrada de la suma de los cuadrados de los efectos de "
            "cada componente de sismo.\n\n"
            "Artículo 44 — Fuerza cortante mínima. La fuerza cortante en "
            "el primer entrepiso NO debe ser menor que 80% del valor "
            "calculado por el artículo 34 (análisis estático) para "
            "estructuras regulares, ni menor que 90% para irregulares. "
            "Si no se cumple, se escala proporcionalmente todo excepto "
            "los desplazamientos. (Nota de verificación: estos umbrales "
            "80%/90% están CONFIRMADOS SIN CAMBIO respecto a la edición "
            "2019 — la referencia cruzada interna del documento 2019 "
            "que apuntaba al 'artículo 25' con una inconsistencia "
            "documentada queda resuelta en 2026: ahora apunta "
            "correctamente al artículo 34.)\n\n"
            "Artículo 45 — Excentricidad accidental (efectos de "
            "torsión) para el análisis dinámico: misma fórmula que el "
            "artículo 37, ei=0,05 veces la dimensión perpendicular, "
            "considerando el signo más desfavorable."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART46_47-TIEMPO_HISTORIA_REGISTROS",
        "seccion": "Artículos 46-47 (ed. 2026)",
        "titulo": "Análisis tiempo-historia complementario (no sustituto); mínimo 7 conjuntos de registros de aceleración con 2 componentes ortogonales; escalamiento SRSS entre 0,2T y 1,5T",
        "texto": (
            "Artículo 46 — Consideraciones generales para el análisis "
            "dinámico tiempo-historia. Es un procedimiento "
            "complementario a los estático/modal espectral (nunca "
            "sustituto). Usa un modelo matemático con comportamiento "
            "histerético directo, integrando las ecuaciones de "
            "equilibrio frente a un conjunto de aceleraciones del "
            "terreno.\n\n"
            "Artículo 47 — Registros de aceleración. Se usan como "
            "mínimo 7 conjuntos de registros, cada uno con 2 componentes "
            "ortogonales, de eventos con magnitud/distancia/mecanismo "
            "consistentes con el máximo sismo considerado (se permiten "
            "registros simulados si no hay suficientes reales). Para "
            "cada par se construye un espectro SRSS con 5% de "
            "amortiguamiento crítico. Al escalar, se usa el mismo factor "
            "para ambas componentes, de modo que el promedio SRSS entre "
            "0,2T y 1,5T no sea menor que el espectro de diseño "
            "(artículo 41, con R=1). Para registros espectro-compatibles, "
            "el promedio SRSS debe ser al menos 100% del espectro de "
            "diseño en ese rango, y cada registro individual no menor al "
            "90% en la dirección de análisis."
        ),
    },
    {
        "id": "E030-2026-CAP4-ART48_49-MODELO_NOLINEAL_TRATAMIENTO_RESULTADOS",
        "seccion": "Artículos 48-49 (ed. 2026)",
        "titulo": "Modelo no lineal con comportamiento histerético calibrado por ensayos; resultados = promedios; distorsión máxima ×1,25 de la Tabla N°14; resistencia se verifica dividiendo entre R=2",
        "texto": (
            "Artículo 48 — Modelo para el análisis (tiempo-historia). "
            "Representa correctamente la distribución de masas; el "
            "comportamiento de los elementos se modela según ensayos de "
            "laboratorio (fluencia, degradación de resistencia y "
            "rigidez, estrechamiento de lazos histeréticos); resistencia "
            "según valores esperados con endurecimiento y degradación "
            "cíclica; se permite suponer comportamiento lineal donde el "
            "análisis lo demuestre; amortiguamiento viscoso equivalente "
            "máximo 5%; se puede suponer base empotrada o considerar "
            "flexibilidad de cimentación.\n\n"
            "Artículo 49 — Tratamiento de resultados. Las fuerzas de "
            "diseño, deformaciones y distorsiones se evalúan como "
            "promedios de los resultados máximos de los distintos "
            "análisis. Las distorsiones máximas de entrepiso no deben "
            "exceder 1,25 veces los valores de la Tabla N°14. Las "
            "deformaciones en elementos no deben exceder 2/3 de aquellas "
            "que perderían presión admisible para cargas verticales, ni "
            "implicar pérdida de resistencia mayor al 30%. Para "
            "verificar la resistencia de los elementos, los resultados "
            "del análisis se dividen entre R=2, aplicando las Normas "
            "Técnicas del RNE de cada material."
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


def reemplazar(dry_run: bool = False):
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
    print(f"\nChunks VIEJOS a eliminar (prefijo '{IDS_VIEJOS_A_ELIMINAR_PREFIJO}'): se listarán antes de borrar.")

    if dry_run:
        print("[dry-run] No se elimina ni se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)

    viejos = sb.table("peru_e030_chunks").select("id").like("id", f"{IDS_VIEJOS_A_ELIMINAR_PREFIJO}%").execute()
    ids_viejos = [r["id"] for r in viejos.data]
    print(f"Eliminando {len(ids_viejos)} chunks viejos (edición 2019): {ids_viejos}")
    if ids_viejos:
        sb.table("peru_e030_chunks").delete().in_("id", ids_viejos).execute()

    sb.table("peru_e030_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(ids_viejos)} chunks viejos eliminados, {len(rows)} chunks nuevos (ed. 2026) insertados.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    reemplazar(dry_run=dry)
