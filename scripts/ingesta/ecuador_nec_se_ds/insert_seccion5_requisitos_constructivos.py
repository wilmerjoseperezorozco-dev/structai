"""
Inserta el núcleo verbatim real de la Sección 5 (Requisitos
constructivos) de la norma NEC-SE-DS de Ecuador en
ecuador_nec_se_ds_chunks. Cuarta sección más pesada de lo que faltaba
(8 páginas, 48-56 del documento).

Cubre: 5.1 (límites de deriva de piso, Tabla 8), 5.2 (separación entre
estructuras, dentro de la misma estructura y entre estructuras
adyacentes/adosadas), 5.3 (regularidad/configuración estructural:
configuraciones recomendadas y no recomendadas -- Tablas 9 y 10 --,
coeficientes de irregularidad en planta y elevación -- Tablas 11 y 12
-- con sus 4+3 tipos de irregularidad, y las fórmulas de ØP/ØE).

Hallazgo de desfase de numeración (mismo patrón ya documentado y
corregido en la Sección 6, Tabla 13): el propio cuerpo del texto llama
"Tabla 8" a las configuraciones recomendadas (5.3.1) y "Tabla 10 y
Tabla 11" a los coeficientes de irregularidad (5.3.3) -- pero por el
título que cada tabla lleva JUNTO a sus propios datos, Tabla 8 son los
límites de deriva (5.1), Tabla 9/10 son las configuraciones
recomendadas/no recomendadas, y Tabla 11/12 son los coeficientes de
irregularidad en planta/elevación. Se etiqueta cada tabla según su
título propio, no según la referencia cruzada del texto -- mismo
criterio ya aplicado en el resto de Ecuador.

Fórmulas no recuperables: las expresiones algebraicas de separación
mínima entre estructuras (5.2.2) salen vacías/ilegibles en la
extracción del PDF (solo "E =" sin el lado derecho) -- se transcribe la
lógica y el glosario de variables, marcando explícitamente que la
fórmula exacta no se pudo recuperar.

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion5_requisitos_constructivos.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 5 — Requisitos Constructivos"

CHUNKS = [
    {
        "id": "NECSEDS-S5_1-TABLA8-DERIVAS_MAXIMAS",
        "seccion": "5.1 (Tabla 8)",
        "titulo": "Deriva máxima de piso ΔM: 0,02 en hormigón armado/acero/madera, 0,01 en mampostería (Tabla 8, título propio)",
        "texto": (
            "NEC-SE-DS, Sección 5.1 — Límites permisibles de las derivas "
            "de los pisos. La deriva máxima para cualquier piso no debe "
            "exceder los límites de la tabla siguiente, expresada como "
            "porcentaje de la altura de piso.\n\n"
            "Tabla 8 — Valores de ΔM máximos, expresados como fracción de "
            "la altura de piso (verbatim, título propio de la tabla):\n"
            "  Estructuras de hormigón armado, estructuras metálicas y de "
            "madera: ΔM máxima = 0,02.\n"
            "  Estructuras de mampostería: ΔM máxima = 0,01."
        ),
    },
    {
        "id": "NECSEDS-S5_2_1-SEPARACION_MISMA_ESTRUCTURA",
        "seccion": "5.2.1",
        "titulo": "Separación entre partes de una misma estructura intencionalmente separadas (criterio de coincidencia de cotas de entrepiso)",
        "texto": (
            "NEC-SE-DS, Sección 5.2.1 — Separación dentro de la misma "
            "estructura. Todos los elementos de la estructura deben "
            "diseñarse y construirse para actuar como un solo sistema "
            "estructural frente al sismo de diseño, a menos que se "
            "separen intencionalmente una distancia suficiente para "
            "evitar problemas de colisión (golpeteo).\n\n"
            "Para determinar la distancia mínima de separación entre "
            "elementos estructurales, se verifica si los sistemas de "
            "entrepiso de cada parte intencionalmente separada coinciden "
            "a la misma cota en altura:\n"
            "  Si NO coinciden: la distancia mínima de separación es el "
            "promedio de los valores absolutos de los desplazamientos "
            "máximos horizontales inelásticos ΔM de cada una de las "
            "partes.\n"
            "  Si SÍ coinciden: la separación mínima es la mitad del "
            "valor absoluto del desplazamiento máximo horizontal "
            "inelástico ΔM de la parte más desfavorable.\n\n"
            "Los valores deben medirse en la dirección perpendicular a la "
            "junta que las separa, salvo que se tomen medidas para evitar "
            "daños con una distancia menor. La junta debe quedar libre de "
            "todo material."
        ),
    },
    {
        "id": "NECSEDS-S5_2_2-SEPARACION_ESTRUCTURAS_ADYACENTES",
        "seccion": "5.2.2",
        "titulo": "Separación entre estructuras adyacentes/colindantes (con y sin separación previa; estructuras adosadas)",
        "texto": (
            "NEC-SE-DS, Sección 5.2.2 — Separación entre estructuras "
            "adyacentes. La normatividad urbana de cada ciudad debería "
            "establecer la separación mínima entre estructuras "
            "colindantes que no forman parte de la misma unidad "
            "estructural. En ausencia de esa reglamentación, se dan "
            "recomendaciones para 2 escenarios:\n\n"
            "a) Cuando ya existe una estructura colindante con separación "
            "previa respecto al lindero del terreno: se distinguen 2 "
            "casos según si las cotas de entrepiso de ambas estructuras "
            "coinciden o no. [Las expresiones algebraicas exactas de la "
            "separación E para ambos casos no se pudieron recuperar con "
            "precisión de la extracción del PDF — el texto trae solo "
            "'E =' sin el lado derecho de la ecuación. Variables "
            "involucradas, sí legibles: desplazamiento del último piso, "
            "altura de la estructura vecina, separación previamente "
            "existente entre la estructura vecina y la nueva.]\n\n"
            "b) Cuando ya existe una estructura colindante SIN separación "
            "respecto al lindero: si no se conocen sus desplazamientos "
            "máximos, se dan reglas según coincidan o no las cotas de "
            "entrepiso. [Misma limitación: las fórmulas exactas no se "
            "pudieron recuperar con precisión del PDF; las variables "
            "nombradas son fuerzas laterales de diseño reducidas, "
            "desplazamiento del último piso, y altura de la estructura "
            "vecina.]\n\n"
            "Estructuras adosadas: cuando el terreno colindante aún no "
            "está construido y la reglamentación urbana permite "
            "adosamiento, en los pisos donde se requiera adosamiento la "
            "estructura debe separarse del lindero una distancia "
            "calculada con la misma familia de variables (fuerzas "
            "laterales de diseño reducidas, desplazamiento del último "
            "piso) — fórmula exacta tampoco recuperable con precisión de "
            "la extracción."
        ),
    },
    {
        "id": "NECSEDS-S5_2_3-SEPARACIONES_MAXIMAS",
        "seccion": "5.2.3",
        "titulo": "Establecimiento de separaciones máximas entre estructuras (evitar golpeteo, considerando descoincidencia de cotas de entrepiso)",
        "texto": (
            "NEC-SE-DS, Sección 5.2.3 — Establecimiento de separaciones "
            "máximas entre estructuras. El establecimiento de "
            "separaciones máximas debe evitar el golpeteo entre "
            "estructuras adyacentes, o entre partes de una misma "
            "estructura intencionalmente separadas, debido a las "
            "deformaciones laterales durante el sismo. Se considera el "
            "efecto desfavorable de que los sistemas de entrepiso de cada "
            "parte separada (o de estructuras adyacentes) no coincidan a "
            "la misma cota de altura. Para los casos de coincidencia y de "
            "no coincidencia se establece la cuantificación de la "
            "separación máxima correspondiente (mismos criterios de las "
            "secciones 5.2.1 y 5.2.2)."
        ),
    },
    {
        "id": "NECSEDS-S5_3_1-CONFIGURACION_ESTRUCTURAL",
        "seccion": "5.3.1 (Tablas 9 y 10)",
        "titulo": "Configuraciones estructurales recomendadas (Tabla 9) y no recomendadas (Tabla 10); DBF solo permitido si ØP=ØE=1 (regularidad total)",
        "texto": (
            "NEC-SE-DS, Sección 5.3.1 — Configuración estructural. Los "
            "diseñadores arquitectónicos y estructurales deben procurar "
            "que la configuración de la estructura sea simple y regular "
            "para lograr un adecuado desempeño sísmico.\n\n"
            "Tabla 9 — Configuraciones estructurales recomendadas "
            "(título propio de la tabla; el texto narrativo la refiere "
            "por error como 'Tabla 8' en un punto — se etiqueta aquí por "
            "su título real, mismo criterio anti-desfase ya aplicado en "
            "el resto de Ecuador): incluye altura de entrepiso y "
            "configuración vertical de sistemas aporticados constante en "
            "todos los niveles (φEi=1); Centro de Rigidez semejante al "
            "Centro de Masa en planta (φPi=1); dimensión del muro "
            "constante en altura o variando de forma proporcional "
            "(φEi=1).\n\n"
            "Tabla 10 — Configuraciones estructurales no recomendadas: "
            "cambios abruptos de rigidez y resistencia deben evitarse "
            "para impedir acumulación de daño y pérdida de ductilidad "
            "global. Si se usa una configuración no recomendada, el "
            "diseñador debe demostrar el adecuado desempeño sísmico "
            "siguiendo los lineamientos de la NEC-SE-RE.\n\n"
            "El procedimiento DBF (Diseño Basado en Fuerzas, Sección 6) "
            "solo se permite cuando la estructura presenta regularidad "
            "total en planta y en elevación (ØP = ØE = 1). En los demás "
            "casos, se requiere cálculo dinámico para incorporar efectos "
            "torsionales y de modos de vibración distintos al "
            "fundamental."
        ),
    },
    {
        "id": "NECSEDS-S5_3_1B-IRREGULARIDADES_CUALITATIVAS",
        "seccion": "5.3.1 / 5.3.2 (figura)",
        "titulo": "4 tipos de irregularidad no recomendada descritos gráficamente: ejes verticales discontinuos, desplazamiento del plano de acción, piso débil (<70% del piso superior), columna corta",
        "texto": (
            "NEC-SE-DS, Sección 5.3.1-5.3.2 — Descripción gráfica de "
            "configuraciones no recomendadas (complementaria a los tipos "
            "formales con coeficiente de las Tablas 11/12, sección "
            "siguiente):\n\n"
            "Ejes verticales discontinuos o muros soportados por "
            "columnas: la estructura se considera irregular no "
            "recomendada cuando existen desplazamientos en el "
            "alineamiento de elementos verticales del sistema resistente, "
            "dentro de un mismo plano, mayores que la dimensión "
            "horizontal del elemento.\n\n"
            "Desplazamiento de los planos de acción de elementos "
            "verticales: irregular no recomendada cuando existen "
            "discontinuidades en los ejes verticales, como "
            "desplazamientos del plano de acción de elementos verticales "
            "del sistema resistente.\n\n"
            "Piso débil — discontinuidad en la resistencia: irregular no "
            "recomendada cuando la resistencia de un piso es menor que el "
            "70% de la resistencia del piso inmediatamente superior "
            "(resistencia de piso = suma de resistencias de todos los "
            "elementos que comparten el cortante del piso, en la "
            "dirección considerada).\n\n"
            "Columna corta: debe evitarse la presencia de columnas "
            "cortas, tanto en el diseño como en la construcción."
        ),
    },
    {
        "id": "NECSEDS-S5_3_3-TABLA11-COEFICIENTES_IRREGULARIDAD_PLANTA",
        "seccion": "5.3.3 (Tabla 11)",
        "titulo": "4 tipos de irregularidad en planta con coeficiente φPi=0,9 (torsional, retrocesos en esquinas >15%, discontinuidad de piso >50%, ejes no paralelos)",
        "texto": (
            "NEC-SE-DS, Sección 5.3.3 — Irregularidades y coeficientes de "
            "configuración estructural. En estructuras irregulares (en "
            "planta y/o elevación) se usan coeficientes de configuración "
            "que 'penalizan' el diseño incrementando el cortante de "
            "diseño, sin evitar el posible comportamiento sísmico "
            "deficiente — por tanto se recomienda evitar al máximo estas "
            "irregularidades. En estructuras irregulares se debería "
            "privilegiar el DBD (Diseño Basado en Desplazamientos, "
            "Sección 7).\n\n"
            "Tabla 11 — Coeficientes de irregularidad en planta (título "
            "propio de la tabla; el texto narrativo la refiere por error "
            "como 'Tabla 10' en un punto — se etiqueta por su título "
            "real), 4 tipos, todos con φPi = 0,9:\n"
            "  Tipo 1 — Irregularidad torsional: la deriva máxima de un "
            "extremo (incluyendo torsión accidental, sección 6.4.2) es "
            "mayor a 1,2 veces la deriva promedio de ambos extremos "
            "respecto al mismo eje.\n"
            "  Tipo 2 — Retrocesos excesivos en las esquinas: un entrante "
            "es excesivo cuando las proyecciones a ambos lados superan el "
            "15% de la dimensión de la planta en esa dirección (A>0,15B "
            "y C>0,15D).\n"
            "  Tipo 3 — Discontinuidades en el sistema de piso: "
            "aberturas/entrantes/huecos con área mayor al 50% del área "
            "total del piso, o cambios de rigidez en el plano del piso "
            "mayores al 50% entre niveles consecutivos.\n"
            "  Tipo 4 — Ejes estructurales no paralelos: los ejes "
            "estructurales no son paralelos ni simétricos respecto a los "
            "ejes ortogonales principales de la estructura."
        ),
    },
    {
        "id": "NECSEDS-S5_3_3-TABLA12-COEFICIENTES_IRREGULARIDAD_ELEVACION",
        "seccion": "5.3.3 (Tabla 12)",
        "titulo": "3 tipos de irregularidad en elevación con coeficiente φEi=0,9 (piso flexible, distribución de masa >1,5x, geometría >1,3x); fórmulas ØP y ØE",
        "texto": (
            "Tabla 12 — Coeficientes de irregularidad en elevación "
            "(título propio de la tabla; el texto narrativo la refiere "
            "por error como 'Tabla 11' en un punto), 3 tipos, todos con "
            "φEi = 0,9:\n"
            "  Tipo 1 — Piso flexible: la rigidez lateral de un piso es "
            "menor al 70% de la rigidez lateral del piso superior, o "
            "menor al 80% del promedio de la rigidez lateral de los 3 "
            "pisos superiores (Kc < 0,70·KD).\n"
            "  Tipo 2 — Distribución de masa: la masa de cualquier piso "
            "es mayor a 1,5 veces la masa de un piso adyacente (mD > "
            "1,50·mE ó mD > 1,50·mC), excepto el piso de cubierta si es "
            "más liviano que el piso inferior.\n"
            "  Tipo 3 — Irregularidad geométrica: la dimensión en planta "
            "del sistema resistente en un piso es mayor a 1,3 veces la "
            "misma dimensión en un piso adyacente (a > 1,3·b), excepto "
            "altillos de un solo piso.\n\n"
            "Coeficiente de regularidad en planta: ØP = ØPA × ØPB, donde "
            "ØPA = mínimo valor ØPi de cada piso para irregularidades "
            "tipo 1, 2 y/o 3, y ØPB = mínimo valor ØPi para irregularidad "
            "tipo 4. Si la estructura no presenta ninguna irregularidad "
            "de la Tabla 11 en ningún piso, ØP = 1 (regular en planta).\n\n"
            "Coeficiente de regularidad en elevación: ØE = ØEA × ØEB, "
            "donde ØEA = mínimo valor ØEi para irregularidad tipo 1, y "
            "ØEB = mínimo valor ØEi para irregularidad tipo 2 y/o 3. Si "
            "la estructura no presenta ninguna irregularidad de la Tabla "
            "12 en ningún nivel, ØE = 1 (regular en elevación).\n\n"
            "Casos particulares: si ΔMi < 1,30·ΔMi+1 (deriva máxima de "
            "cualquier piso menor a 1,30 veces la deriva máxima del piso "
            "superior), se toma ØP = ØE = 1. Adicionalmente, para "
            "estructuras tipo pórtico especial sismo resistente con "
            "muros estructurales (sistemas duales, sección 1.2), se "
            "considera ØE = 1."
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
