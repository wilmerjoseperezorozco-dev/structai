"""
Ingesta verbatim de Título B, Capítulo B.2 (Combinaciones de carga) --
NSR-10. Fase 2 del plan de cierre del Título B (2026-09-23), auditoría
real de numerales confirmó B.2 en 5/20 (faltan 15) -- capítulo
fundacional citado por prácticamente todos los demás títulos del
Reglamento (las combinaciones de carga de B.2.3/B.2.4 son la base de
todo diseño estructural).

Fuente: NSR-10-222-226.pdf, páginas PDF 1-5 (B-3 a B-7, capítulo
completo). Leídas visualmente con Read pages= sobre el PDF nativo --
nunca extracción mecánica (pypdf).

Uso: python _ingest_titulo_b_b2_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

CHUNKS = [
    {
        "id": "NSR10-B-B_2_1_1_definiciones_glosario",
        "seccion": "B.2.1.1 — Definiciones (glosario bilingüe de términos del Título B)",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "CAPÍTULO B.2 — COMBINACIONES DE CARGA\n\n"
            "B.2.1 — DEFINICIONES Y LIMITACIONES\n\n"
            "B.2.1.1 — DEFINICIONES — Las definiciones que se dan a "
            "continuación hacen referencia al presente Título B (Se "
            "incluye la traducción al inglés de cada uno de los "
            "términos definidos para efectos de concordancia con los "
            "requisitos de las normas que han servido de base a la "
            "actualización de estos requisitos dentro de la NSR-10):\n\n"
            "Cargas (Loads) — Son fuerzas u otras solicitaciones que "
            "actúan sobre el sistema estructural y provienen del peso "
            "de todos los elementos permanentes en la construcción, "
            "los ocupantes y sus pertenencias, efectos ambientales, "
            "asentamientos diferenciales y restricción de cambios "
            "dimensionales. Las cargas permanentes son cargas que "
            "varían muy poco en el tiempo y cuyas variaciones son "
            "pequeñas en magnitud. Todas las otras cargas son cargas "
            "variables.\n\n"
            "Cargas de servicio (Service loads) — Véase cargas "
            "nominales.\n\n"
            "Carga mayorada (Factored load) — Es una carga que se "
            "obtiene como el producto de una carga nominal por un "
            "coeficiente de carga. Las fuerzas sísmicas dadas en el "
            "Título A de este Reglamento corresponden a fuerzas "
            "mayoradas, pues ya han sido afectadas por el coeficiente "
            "de carga, el cual va incluido en la probabilidad de "
            "ocurrencia del sismo de diseño.\n\n"
            "Cargas nominales (Nominal loads) — Son las magnitudes de "
            "las cargas especificadas en B.3 a B.6 de este Reglamento. "
            "Las cargas muertas, vivas y de viento que se dan en este "
            "Título son cargas nominales o reales, las cuales NO han "
            "sido multiplicadas por el coeficiente de carga.\n\n"
            "Coeficiente de carga (Load factor) — Es un coeficiente "
            "que tiene en cuenta las desviaciones inevitables de las "
            "cargas reales con respecto a las cargas nominales y las "
            "incertidumbres que se tienen en el análisis estructural. "
            "Es sinónimo de \"factor de carga\" para efectos del "
            "Reglamento NSR-10.\n\n"
            "Coeficiente de reducción de resistencia (Strength "
            "reduction factor) — Es un coeficiente que tiene en cuenta "
            "las desviaciones inevitables entre la resistencia real y "
            "la resistencia nominal del elemento y la forma y "
            "consecuencia de su tipo de falla. Es sinónimo de "
            "\"factor de reducción de resistencia\" para efectos del "
            "Reglamento NSR-10.\n\n"
            "Curadurías — Son, de acuerdo con la Ley 388 de 1997, las "
            "entidades encargadas de estudiar, tramitar y expedir las "
            "licencias de construcción en los casos que contempla la "
            "Ley. En aquellos casos en los cuales dentro del presente "
            "Reglamento NSR-10 se menciona la Curaduría, implica "
            "además de ellas la entidad que expide las licencias de "
            "construcción o urbanismo que cumplen sus funciones.\n\n"
            "Durabilidad (Durability) — Capacidad de una estructura o "
            "elementos estructural para garantizar que no se presente "
            "deterioro perjudicial para el desempeño requerido en el "
            "ambiente para el cual se diseñó.\n\n"
            "Edificación (Building) — Es una construcción cuyo uso "
            "principal es la habitación u ocupación por seres humanos.\n\n"
            "Efectos de las cargas (Load effects) — Son las "
            "deformaciones y fuerzas internas que producen las cargas "
            "en los elementos estructurales.\n\n"
            "Estado límite (Limit state) — Es una condición mas allá "
            "de la cual una estructura o uno de sus componentes deja "
            "de cumplir su función (estado límite de servicio) o se "
            "vuelve insegura (estado límite de resistencia).\n\n"
            "Funcionamiento (Serviceability) — Capacidad de la "
            "estructura, o de un elemento estructural, de tener un "
            "comportamiento adecuado en condiciones de servicio.\n\n"
            "Integridad estructural (Structural integrity) — "
            "Capacidad de la estructura para evitar colapso "
            "generalizado cuando ocurre daño localizado.\n\n"
            "Mantenimiento (Maintenance) — Conjunto total de "
            "actividades que se realizan durante la vida de servicio "
            "de diseño de la estructura para que sea capaz de cumplir "
            "con los requisitos de desempeño.\n\n"
            "Método de la resistencia (Strength design method) — Es "
            "un método de diseño para los elementos estructurales tal "
            "que las fuerzas internas calculadas producidas por las "
            "cargas mayoradas no excedan las resistencias de diseño de "
            "los mismos.\n\n"
            "Método de los esfuerzos de trabajo (Allowable stress "
            "design method) — Es un método para diseñar los elementos "
            "estructurales en el cual los esfuerzos calculados "
            "elásticamente, utilizando cargas reales, no deben exceder "
            "un valor límite especificado para cada material.\n\n"
            "Método de los estados límites (Limit state design "
            "method) — Es un método para diseñar estructuras de tal "
            "manera que la probabilidad de falla para ciertos estados "
            "límites considerados importantes esté dentro de valores "
            "aceptables. Por lo general se estudian los estados "
            "límites de servicio y de resistencia. Este último caso se "
            "conoce como método de la resistencia.\n\n"
            "Reparabilidad (Restorability) — Capacidad de la "
            "estructura, o de poder ser reparada física y "
            "económicamente cuando sea dañada por los efectos de las "
            "solicitaciones consideradas.\n\n"
            "Resistencia (Resistance) — Capacidad de un elemento "
            "estructural para soportar las cargas o fuerzas que se le "
            "apliquen\n\n"
            "Resistencia de diseño (Design strength) — Es el producto "
            "de la resistencia nominal por un coeficiente de reducción "
            "de resistencia.\n\n"
            "Resistencia nominal (Nominal strength) — Es la capacidad "
            "de la estructura, o componente de ella, de resistir los "
            "efectos de las cargas, determinada por medio de cálculo "
            "en el cual se utilizan los valores nominales de las "
            "resistencias de los materiales, las dimensiones nominales "
            "del elemento y ecuaciones derivadas de principios "
            "aceptables de mecánica estructural. Estas ecuaciones "
            "provienen de ensayos de campo y ensayos de laboratorio "
            "con modelos a escala, teniendo en cuenta los efectos del "
            "modelaje y las diferencias entre las condiciones en el "
            "terreno y en laboratorio.\n\n"
            "Sistema estructural (Structural system) — Elementos "
            "estructurales interconectados que en conjunto cumplen "
            "una función específica.\n\n"
            "Trayectoria de cargas (Load path) — Sucesión de elementos "
            "estructurales a lo largo de los cuales se transmiten "
            "cargas desde su punto de aplicación hasta la cimentación.\n\n"
            "Vida de servicio de diseño (Design service life) — "
            "Período durante el cual la estructura o el elemento "
            "estructural sean utilizables para el propósito para el "
            "cual se diseñaron con los mantenimientos que se requieran "
            "pero sin que haya necesidad de realizarles reparaciones "
            "importantes."
        ),
    },
    {
        "id": "NSR10-B-B_2_1_2_limitacion",
        "seccion": "B.2.1.2 — Limitación",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.1.2 — LIMITACIÓN — La seguridad de la estructura puede "
            "verificarse utilizando los requisitos de B.2.3 o B.2.4 "
            "dependiendo del método de diseño escogido y del material "
            "estructural. Una vez se ha determinado si se usan unos "
            "requisitos u otros, el diseño debe hacerse en su "
            "totalidad siguiendo los requisitos de ese numeral para "
            "todos los elementos de la estructura."
        ),
    },
    {
        "id": "NSR10-B-B_2_2_nomenclatura",
        "seccion": "B.2.2 — Nomenclatura del Capítulo B.2",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.2 — NOMENCLATURA\n\n"
            "D = carga Muerta consistente en: (a) peso propio del "
            "elemento, (b) peso de todos los materiales de "
            "construcción incorporados a la edificación y que son "
            "permanentemente soportados por el elemento, incluyendo "
            "muros y particiones divisorias de espacios, (c) peso del "
            "equipo permanente.\n"
            "E = fuerzas sísmicas reducidas de diseño (E = Fs/R) que "
            "se emplean para diseñar los miembros estructurales.\n"
            "Ed = fuerza sísmica del umbral de daño.\n"
            "F = cargas debidas al peso y presión de fluidos con "
            "densidades bien definidas y alturas máximas controlables.\n"
            "Fa = carga debida a inundación.\n"
            "Fs = fuerzas sísmicas calculadas de acuerdo con los "
            "requisitos del Título A del Reglamento.\n"
            "G = carga debida al granizo, sin tener en cuenta la "
            "contribución del empozamiento.\n"
            "L = cargas vivas debidas al uso y ocupación de la "
            "edificación, incluyendo cargas debidas a objetos móviles, "
            "particiones que se pueden cambiar de sitio. L incluye "
            "cualquier reducción que se permita. Si se toma en cuenta "
            "la resistencia a cargas de impacto este efecto debe "
            "tenerse en cuenta en la carga viva L.\n"
            "Le = carga de empozamiento de agua.\n"
            "Lr = carga viva sobre la cubierta.\n"
            "L0 = carga viva sin reducir, en kN/m². Véase B.4.5.1.\n"
            "H = cargas debidas al empuje lateral del suelo, de agua "
            "freática o de materiales almacenados con restricción "
            "horizontal.\n"
            "R0 = coeficiente de capacidad de disipación de energía "
            "básico definido para cada sistema estructural y cada "
            "grado de capacidad de disipación de energía del material "
            "estructural. Véase el Capítulo A.3.\n"
            "R = coeficiente de capacidad de disipación de energía "
            "para ser empleado en el diseño, corresponde al "
            "coeficiente de disipación de energía básico multiplicado "
            "por los coeficientes de reducción de capacidad de "
            "disipación de energía por irregularidades en altura y en "
            "planta, y por ausencia de redundancia en el sistema "
            "estructural de resistencia sísmica (R = φa φp φr R0). "
            "Véase el Capítulo A.3.\n"
            "T = fuerzas y efectos causados por efectos acumulados de "
            "variación de temperatura, retracción de fraguado, flujo "
            "plástico, cambios de humedad, asentamiento diferencial o "
            "combinación de varios de estos efectos.\n"
            "W = carga de Viento."
        ),
    },
    {
        "id": "NSR10-B-B_2_3_1_combinaciones_basicas_esfuerzos_trabajo",
        "seccion": "B.2.3.1 — Combinaciones básicas para esfuerzos de trabajo (ecuaciones B.2.3-1 a B.2.3-10)",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.3 — COMBINACIONES DE CARGA PARA SER UTILIZADAS CON EL "
            "MÉTODO DE ESFUERZOS DE TRABAJO O EN LAS VERIFICACIONES DEL "
            "ESTADO LIMITE DE SERVICIO\n\n"
            "B.2.3.1 — COMBINACIONES BÁSICAS — Excepto cuando así se "
            "indique en la parte correspondiente a cada uno de los "
            "materiales que se regulan en este Reglamento, deben "
            "tenerse en cuenta todas las cargas indicadas a "
            "continuación actuando en las combinaciones que se dan. El "
            "diseño debe hacerse para la combinación que produzca el "
            "efecto más desfavorable en la edificación, en su "
            "cimentación, o en el elemento estructural bajo "
            "consideración. El efecto más desfavorable puede ocurrir "
            "cuando una o varias de las cargas no actúen.\n\n"
            "En el presente Reglamento NSR-10, todos los materiales "
            "estructurales, con la excepción de la madera y guadua en "
            "el Título G, se diseñan por el método de la resistencia y "
            "por lo tanto las combinaciones básicas de carga de la "
            "presente sección B.2.3.1 no son aplicables a los "
            "materiales estructurales prescritos en el Reglamento y no "
            "deben utilizarse. Se incluyen para aquellos casos "
            "especiales en los cuales el diseño se realiza por el "
            "método de los esfuerzos admisibles y solo deben emplearse "
            "cuando así lo indique explícitamente el Título o Capítulo "
            "o Sección correspondiente del Reglamento.\n\n"
            "D + F       (B.2.3-1)\n"
            "D + H + F + L + T       (B.2.3-2)\n"
            "D + H + F + (Lr ó G ó Le)       (B.2.3-3)\n"
            "D + H + F + 0.75(L+T) + 0.75(Lr ó G ó Le)       (B.2.3-4)\n"
            "D + H + F + W       (B.2.3-5)\n"
            "D + H + F + 0.7E       (B.2.3-6)\n"
            "D + H + F + 0.75W + 0.75L + 0.75(Lr ó G ó Le)       "
            "(B.2.3-7)\n"
            "D + H + F + 0.75(0.7E) + 0.75L + 0.75(Lr ó G ó Le)       "
            "(B.2.3-8)\n"
            "0.6D + W + H       (B.2.3-9)\n"
            "0.6D + 0.7E + H       (B.2.3-10)\n\n"
            "Deben considerarse los efectos más desfavorables de "
            "viento y de sismo tomándolos independientemente."
        ),
    },
    {
        "id": "NSR10-B-B_2_3_2_fuerzas_sismicas_esfuerzos_trabajo",
        "seccion": "B.2.3.2 — Fuerzas sísmicas para esfuerzos de trabajo (verificación de derivas para sismo de diseño y umbral de daño)",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.3.2 — FUERZAS SÍSMICAS — Las fuerzas sísmicas "
            "reducidas, E, utilizadas en las combinaciones B.2.3-6, "
            "B.2.3-8 y B.2.3-10 corresponden al efecto, expresado en "
            "términos de fuerza, Fs, de los movimientos sísmicos de "
            "diseño prescritos en el Título A, dividido por R (E = "
            "Fs/R). Cuando se trata de diseñar los miembros por el "
            "método de los esfuerzos de trabajo del material, el valor "
            "del coeficiente de carga que afecta las fuerzas sísmicas "
            "E, es 0.7.\n\n"
            "B.2.3.2.1 — Verificación de las derivas por el método de "
            "esfuerzos de trabajo para el sismo de diseño — Para "
            "evaluar las derivas obtenidas de las deflexiones "
            "horizontales causadas por el sismo de diseño, deben "
            "utilizarse los requisitos del capítulo A.6, los cuales "
            "exigen que las derivas se verifiquen para las fuerzas "
            "sísmicas Fs, sin haber sido divididas por R, empleando "
            "1.0E en vez de 0.7E en las ecuaciones que incluyan E en "
            "B.2.3.\n\n"
            "B.2.3.2.2 — Verificación de las derivas por el método de "
            "esfuerzos de trabajo para el sismo de umbral de daño — "
            "Para evaluar las derivas obtenidas de las deflexiones "
            "horizontales causadas por el sismo de umbral de daño en "
            "edificaciones indispensables del grupo de uso IV, deben "
            "utilizarse los requisitos del capítulo A.12, los cuales "
            "exigen que las derivas se verifiquen para las fuerzas "
            "sísmicas Ed."
        ),
    },
    {
        "id": "NSR10-B-B_2_4_1_a_4_2_aplicabilidad_combinaciones_mayoradas",
        "seccion": "B.2.4.1 y B.2.4.2 — Aplicabilidad y combinaciones básicas mayoradas por el método de la resistencia (ecuaciones B.2.4-1 a B.2.4-7)",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.4 — COMBINACIONES DE CARGAS MAYORADAS USANDO EL "
            "MÉTODO DE RESISTENCIA\n\n"
            "B.2.4.1 — APLICABILIDAD — Las combinaciones de carga y "
            "factores de carga dados en la sección B.2.4.2 deben ser "
            "usados en todos los materiales estructurales permitidos "
            "por el Reglamento de diseño del material, con la "
            "excepción de aquellos casos en que el Reglamento indique "
            "explícitamente que deba realizarse el diseño utilizando "
            "el método de los esfuerzos de trabajo, caso en el cual se "
            "deben utilizar las combinaciones de la sección B.2.3.1.\n\n"
            "Nota Importante: Las combinaciones de carga dadas en "
            "B.2.4.2 contienen factores de carga menores que los que "
            "prescribía el Reglamento NSR-98, pero al mismo tiempo "
            "para cada uno de los materiales estructurales en esta "
            "nueva versión del Reglamento (NSR-10) se han prescrito "
            "valores de los coeficientes de reducción de resistencia, "
            "φ, menores que los que contenía el Reglamento NSR-98, "
            "siendo los nuevos valores concordantes con la "
            "probabilidad de falla estructural que limita el "
            "Reglamento. Por lo tanto es incorrecto, e inseguro, "
            "utilizar las nuevas ecuaciones de combinación de carga de "
            "B.2.4.2 con los valores de los coeficientes de reducción "
            "de resistencia, φ, que contenía la NSR-98.\n\n"
            "B.2.4.2 — COMBINACIONES BÁSICAS — El diseño de las "
            "estructuras, sus componentes y cimentaciones debe hacerse "
            "de tal forma que sus resistencias de diseño igualen o "
            "excedan los efectos producidos por las cargas mayoradas "
            "en las siguientes combinaciones:\n\n"
            "1.4(D + F)       (B.2.4-1)\n"
            "1.2(D + F + T) + 1.6(L + H) + 0.5(Lr ó G ó Le)       "
            "(B.2.4-2)\n"
            "1.2D + 1.6(Lr ó G ó Le) + (L ó 0.8W)       (B.2.4-3)\n"
            "1.2D + 1.6W + 1.0L + 0.5(Lr ó G ó Le)       (B.2.4-4)\n"
            "1.2D + 1.0E + 1.0L       (B.2.4-5)\n"
            "0.9D + 1.6W + 1.6H       (B.2.4-6)\n"
            "0.9D + 1.0E + 1.6H       (B.2.4-7)"
        ),
    },
    {
        "id": "NSR10-B-B_2_4_2_1_a_2_7_notas_combinaciones_mayoradas",
        "seccion": "B.2.4.2.1 a B.2.4.2.7 — Notas de las combinaciones mayoradas (fuerzas sísmicas, reducción de L, viento no reducido, H, impacto, deformaciones)",
        "titulo": "NSR-10 Título B — Capítulo B.2 — Combinaciones de carga",
        "texto": (
            "B.2.4.2.1 — Las fuerzas sísmicas reducidas de diseño, E, "
            "utilizadas en las combinaciones B.2.4-5 y B.2.4-7 "
            "corresponden al efecto, expresado en términos de fuerza, "
            "Fs, de los movimientos sísmicos de diseño prescritos en "
            "el Título A, dividido por R (E = Fs/R). Cuando se trata "
            "de diseñar los miembros, el valor del coeficiente de "
            "carga que afecta las fuerzas sísmicas E, es 1.0, dado que "
            "estas están prescritas al nivel de resistencia. Para la "
            "verificación de las derivas obtenidas de las deflexiones "
            "horizontales causadas por el sismo de diseño, deben "
            "utilizarse los requisitos del Capítulo A.6, los cuales "
            "exigen que las derivas se verifiquen para las fuerzas "
            "sísmicas Fs, sin haber sido divididas por R.\n\n"
            "B.2.4.2.2 — Se permite reducir a 0.5 el factor de carga "
            "de carga viva, L, en las combinaciones B.2.4-3, B.2.4-4 y "
            "B.2.4-5, excepto para estacionamientos, áreas ocupadas "
            "como lugares de reunión pública y en todas las áreas "
            "donde L0 sea superior a 4.8 kN/m².\n\n"
            "B.2.4.2.3 — Cuando las cargas de viento prescritas en el "
            "capítulo B.6 del Reglamento NSR-10 no se reducen por el "
            "factor de direccionalidad prescrito allí se permite "
            "utilizar 1.3W en lugar de 1.6W en las combinaciones "
            "B.2.4-4 y B.2.4-6.\n\n"
            "B.2.4.2.4 — El Título A del Reglamento NSR-10 define las "
            "fuerzas por sismo al nivel de resistencia por lo tanto en "
            "las combinaciones B.2.4-5 y B.2.4-7 se debe usar 1.0E. En "
            "las ecuaciones B.2.4-5 y B.2.4-7 se puede usar 1.4E, "
            "cuando los efectos de carga por sismo E se basen en los "
            "niveles de servicio de las fuerzas sísmicas.\n\n"
            "B.2.4.2.5 — El factor de carga para H, cargas debidas al "
            "peso y presión del suelo, agua en el suelo, u otros "
            "materiales, debe fijarse igual a cero en las "
            "combinaciones B.2.4-6 y B.2.4-7 si la acción estructural "
            "debida a H neutraliza las causadas por W o E. Cuando las "
            "presiones laterales ejercidas por el empuje del suelo "
            "proporcionan resistencia a las acciones estructurales "
            "provenientes de otras fuerzas, no deben incluirse en H, "
            "sino deben incluirse en la resistencia de diseño.\n\n"
            "B.2.4.2.6 — Si los efectos del impacto deben ser tenidos "
            "en cuenta en el diseño, estos efectos deben incluirse con "
            "la carga viva L.\n\n"
            "B.2.4.2.7 — Los estimativos de asentamientos "
            "diferenciales, el flujo plástico, la retracción, la "
            "expansión de concretos de retracción compensada o las "
            "variaciones de temperatura deben basarse en una "
            "evaluación realista de tales efectos que puedan ocurrir "
            "durante la vida útil de la estructura."
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
    print(f"Codificando {len(textos)} chunks...")
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print(f"\nSubiendo {len(rows)} chunks a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK.")


if __name__ == "__main__":
    main()
