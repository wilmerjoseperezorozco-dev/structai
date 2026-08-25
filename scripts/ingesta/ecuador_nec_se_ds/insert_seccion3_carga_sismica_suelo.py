"""
Inserta el núcleo verbatim real de la Sección 3 (Carga sísmica y condición
del suelo) de la norma NEC-SE-DS de Ecuador en ecuador_nec_se_ds_chunks.
Tercera sección más pesada de lo que faltaba (14 páginas, 27-40 del
documento). Verificado que no había NADA de la Sección 3 en el corpus
todavía (solo se habían usado sus datos de forma puntual al corregir la
Sección 6, sin ingestarla como chunks propios).

Cubre: 3.1 (zonificación sísmica, factor Z, Tabla 1; curvas de peligro
sísmico), 3.2 (tipos de perfil de suelo A-F, Tabla 2; coeficientes de sitio
Fa/Fd/Fs, Tablas 3-5), 3.3 (espectros elásticos de diseño en aceleraciones
y en desplazamientos), 3.4 (componente vertical del sismo), 3.5
(combinación de fuerzas sísmicas ortogonales y verticales). 3.6 es solo una
figura sin texto propio, no se ingesta.

Fuente: mismo PDF oficial MIDUVI/MIT ya usado para el resto de Ecuador.
A diferencia de la Sección 7 (DBD), esta sección tiene fórmulas más
simples y mejor extraídas -- se transcriben tal cual cuando son legibles
con confianza; los dos únicos casos donde la expresión exacta de T0/TC no
se pudo recuperar con precisión se marcan explícitamente (mismo criterio
de honestidad de fuente ya aplicado en el resto del proyecto).

Uso: python scripts/ingesta/ecuador_nec_se_ds/insert_seccion3_carga_sismica_suelo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NEC-SE-DS Sección 3 — Carga Sísmica y Condición del Suelo"

CHUNKS = [
    {
        "id": "NECSEDS-S3_1_1-TABLA1-ZONIFICACION_FACTOR_Z",
        "seccion": "3.1.1 (Tabla 1)",
        "titulo": "6 zonas sísmicas de Ecuador y factor Z (I=0,15 a VI≥0,50); mapa de peligro sísmico al 10% en 50 años (475 años de retorno)",
        "texto": (
            "NEC-SE-DS, Sección 3.1.1 — Zonificación sísmica y factor de "
            "zona Z. Para edificios de uso normal se usa Z, la aceleración "
            "máxima en roca esperada para el sismo de diseño, como fracción "
            "de la gravedad. El sitio determina una de las 6 zonas "
            "sísmicas del Ecuador (mapa, Figura 1). El mapa proviene del "
            "estudio de peligro sísmico para 10% de excedencia en 50 años "
            "(período de retorno 475 años), con saturación a 0,50 g en el "
            "litoral ecuatoriano (zona VI).\n\n"
            "Tabla 1 — Valores del factor Z por zona sísmica (verbatim):\n"
            "  Zona I: Z = 0,15 (peligro intermedio).\n"
            "  Zona II: Z = 0,25 (peligro alto).\n"
            "  Zona III: Z = 0,30 (peligro alto).\n"
            "  Zona IV: Z = 0,35 (peligro alto).\n"
            "  Zona V: Z = 0,40 (peligro alto).\n"
            "  Zona VI: Z ≥ 0,50 (peligro muy alto).\n\n"
            "Todo el territorio ecuatoriano está catalogado como de "
            "amenaza sísmica alta, con excepción del nororiente (amenaza "
            "intermedia) y el litoral (amenaza muy alta). Para facilitar "
            "la determinación de Z, la Tabla 16 de la sección 10.2 incluye "
            "un listado de poblaciones con su valor correspondiente (ya "
            "cargada en este corpus, 512 registros); si la población no "
            "consta en la lista, se toma el valor de la población más "
            "cercana."
        ),
    },
    {
        "id": "NECSEDS-S3_1_2-CURVAS_PELIGRO_SISMICO",
        "seccion": "3.1.2",
        "titulo": "Curvas de peligro sísmico por capital de provincia (PGA vs. probabilidad anual de excedencia) — para estructuras esenciales/especiales, puentes y obras portuarias",
        "texto": (
            "NEC-SE-DS, Sección 3.1.2 — Curvas de peligro sísmico. Para "
            "estructuras de ocupación especial y/o esencial, puentes, "
            "obras portuarias y otras estructuras diferentes a las de "
            "edificación, se necesitan distintos niveles de peligro "
            "sísmico para verificar distintos niveles de desempeño "
            "(sección 4.2.4). Se proporcionan curvas de peligro sísmico "
            "probabilista para cada capital de provincia, relacionando la "
            "aceleración sísmica esperada en roca (PGA) con la "
            "probabilidad anual de excedencia (Figuras 16 a 38 del "
            "apéndice 10.3). El período de retorno es el inverso de la "
            "probabilidad anual de excedencia. Cada figura incluye también "
            "curvas de aceleraciones máximas espectrales para períodos "
            "estructurales de 0,1, 0,2, 0,5 y 1,0 segundos. Información "
            "complementaria sobre microzonificación sísmica está en el "
            "apéndice 10.6.3."
        ),
    },
    {
        "id": "NECSEDS-S3_2_1-TABLA2-TIPOS_PERFIL_SUELO",
        "seccion": "3.2.1 (Tabla 2)",
        "titulo": "6 tipos de perfil de suelo A-F (por velocidad de onda de cortante Vs, N, Su); tipo F requiere evaluación explícita in situ (6 subclases F1-F6)",
        "texto": (
            "NEC-SE-DS, Sección 3.2.1 — Tipos de perfiles de suelos para "
            "el diseño sísmico. Se definen 6 tipos de perfil (Tabla 2). "
            "Para los tipos A-E, los parámetros corresponden a los 30 m "
            "superiores del perfil; perfiles con estratos diferenciables "
            "se subdividen con subíndice i (1 en superficie, n en el "
            "fondo). El tipo F usa otros criterios (sección 10.6.4), sin "
            "limitarse a los 30 m superiores en perfiles de espesor "
            "significativo.\n\n"
            "Tabla 2 — Clasificación de perfiles de suelo (verbatim):\n"
            "  A — Perfil de roca competente: Vs ≥ 1500 m/s.\n"
            "  B — Perfil de roca de rigidez media: 1500 > Vs ≥ 760 m/s.\n"
            "  C — Suelos muy densos o roca blanda: 760 > Vs ≥ 360 m/s, o "
            "N ≥ 50,0, o Su ≥ 100 kPa.\n"
            "  D — Suelos rígidos: 360 > Vs ≥ 180 m/s, o 50 > N ≥ 15,0, o "
            "100 > Su ≥ 50 kPa.\n"
            "  E — Vs < 180 m/s, o perfil con espesor total H > 3 m de "
            "arcillas blandas (índice de plasticidad IP > 20, contenido de "
            "agua w ≥ 40%, Su < 50 kPa).\n"
            "  F — Requiere evaluación explícita en el sitio por un "
            "ingeniero geotecnista. Subclases: F1 (suelos susceptibles a "
            "falla/colapso sísmico: licuables, arcillas sensitivas, "
            "dispersivos, débilmente cementados); F2 (turba y arcillas "
            "orgánicas, H > 3 m); F3 (arcillas de muy alta plasticidad, "
            "H > 7,5 m con IP > 75); F4 (gran espesor de arcillas de "
            "rigidez media a blanda, H > 30 m); F5 (contrastes de "
            "impedancia en los primeros 30 m, incluyendo contactos "
            "suelo-roca con cambios bruscos de velocidad de onda de "
            "corte); F6 (rellenos colocados sin control ingenieril)."
        ),
    },
    {
        "id": "NECSEDS-S3_2_2-TABLAS345-COEFICIENTES_SITIO",
        "seccion": "3.2.2 (Tablas 3, 4, 5)",
        "titulo": "Coeficientes de sitio Fa (amplificación período corto), Fd (desplazamientos), Fs (comportamiento no lineal) por tipo de suelo A-E y zona I-VI",
        "texto": (
            "NEC-SE-DS, Sección 3.2.2 — Coeficientes de perfil de suelo "
            "Fa, Fd y Fs. Nota: para suelo tipo F no se dan valores — "
            "requieren estudio especial (sección 10.6.4).\n\n"
            "Tabla 3 — Fa (amplifica el espectro de aceleraciones en roca "
            "por efectos de sitio), por tipo de suelo y zona (Z=0,15 a "
            "≥0,5): A=0,9 en todas las zonas; B=1,0 en todas las zonas; "
            "C=1,4/1,3/1,25/1,23/1,2/1,18; D=1,6/1,4/1,3/1,25/1,2/1,12; "
            "E=1,8/1,5/1,39/1,26/1,14/0,97.\n\n"
            "Tabla 4 — Fd (amplifica el espectro de desplazamientos en "
            "roca): A=0,9 en todas las zonas; B=1,0 en todas las zonas; "
            "C=1,6/1,5/1,4/1,35/1,3/1,25; D=1,9/1,7/1,6/1,5/1,4/1,3; "
            "E=2,1/1,75/1,7/1,65/1,6/1,5.\n\n"
            "Tabla 5 — Fs (comportamiento no lineal del suelo, "
            "degradación del período del sitio): A=0,75 en todas las "
            "zonas; B=0,75 en todas las zonas; C=1,0/1,1/1,2/1,25/1,3/1,45; "
            "D=1,2/1,25/1,3/1,4/1,5/1,65; E=1,5/1,6/1,7/1,8/1,9/2,0.\n\n"
            "Nota: para poblaciones con más de 100.000 habitantes y suelo "
            "tipo F, se hace un espectro específico al sitio (geología, "
            "tectónica, sismología, suelo local), con amortiguamiento de "
            "5,00% salvo justificación distinta."
        ),
    },
    {
        "id": "NECSEDS-S3_3_1-ESPECTRO_ACELERACIONES_SA",
        "seccion": "3.3.1",
        "titulo": "Espectro elástico horizontal de aceleraciones Sa = η·Z·Fa (T≤TC) o η·Z·Fa·(TC/T)^r (T>TC); factor r (1,0 ó 1,5); η por región (Costa 1,80 / Sierra 2,48 / Oriente 2,60)",
        "texto": (
            "NEC-SE-DS, Sección 3.3.1 — Espectro elástico horizontal de "
            "diseño en aceleraciones. El espectro Sa (fracción de la "
            "gravedad) depende de: el factor de zona Z, el tipo de suelo, "
            "y los coeficientes Fa/Fd/Fs. Válido para amortiguamiento de "
            "5% respecto al crítico, en 2 rangos de período T:\n\n"
            "Sa = η · Z · Fa   para 0 ≤ T ≤ TC\n"
            "Sa = η · Z · Fa · (TC/T)^r   para T > TC\n\n"
            "Donde: η = razón entre la aceleración espectral Sa(T=0,1s) y "
            "el PGA para el período de retorno seleccionado; r = 1,0 para "
            "suelo tipo A, B o C; r = 1,5 para suelo tipo D o E; T = "
            "período fundamental de vibración; TC = período límite "
            "superior de la meseta del espectro; Z = aceleración máxima en "
            "roca (fracción de g).\n\n"
            "Valores de η según la región (de los espectros de peligro "
            "uniforme normalizados por Z, período de retorno 475 años): "
            "η = 1,80 en provincias de la Costa (excepto Esmeraldas); "
            "η = 2,48 en provincias de la Sierra, Esmeraldas y Galápagos; "
            "η = 2,60 en provincias del Oriente.\n\n"
            "Nota: para suelo tipo D y E, TL (usado en el espectro de "
            "desplazamientos, sección 3.3.2) se limita a un máximo de 4 "
            "segundos. [Las expresiones algebraicas exactas de T0 y TC en "
            "función de Fa/Fd/Fs no se pudieron recuperar con precisión "
            "del texto extraído del PDF — ver documento oficial.] Para "
            "análisis dinámico de modos distintos al fundamental, con T "
            "menor a T0, se usa una expresión distinta de Sa que interpola "
            "linealmente entre 0 y el valor en T0. Si estudios de "
            "microzonificación sísmica (sección 10.6.3) dan valores "
            "distintos de Fa/Fd/Fs/Sa para una región, se pueden usar esos "
            "valores en su lugar."
        ),
    },
    {
        "id": "NECSEDS-S3_3_2-ESPECTRO_DESPLAZAMIENTOS_SD",
        "seccion": "3.3.2",
        "titulo": "Espectro elástico de desplazamientos Sd, definido en 4 tramos según T0/TC/TL — usa los mismos períodos límite que el espectro de aceleraciones",
        "texto": (
            "NEC-SE-DS, Sección 3.3.2 — Espectro elástico de diseño en "
            "desplazamientos. Se define el espectro Sd (en metros), para "
            "amortiguamiento de 5% respecto al crítico (Figura 4), en 4 "
            "tramos según el período T: (1) 0 ≤ T ≤ T0; (2) T0 < T ≤ TC; "
            "(3) TC < T ≤ TL; (4) T > TL. [Las expresiones algebraicas "
            "exactas de cada tramo no se pudieron recuperar con precisión "
            "del texto extraído del PDF — ver documento oficial para la "
            "notación completa.] Los períodos límite T0, TC y TL son los "
            "mismos definidos para el espectro elástico de aceleraciones "
            "(sección 3.3.1). Nota: para suelo tipo D y E, TL se limita a "
            "un máximo de 4 segundos también en el espectro de "
            "desplazamientos."
        ),
    },
    {
        "id": "NECSEDS-S3_4-COMPONENTE_VERTICAL",
        "seccion": "3.4",
        "titulo": "Componente vertical del sismo Ev = (2/3)·Eh; caso especial cerca de falla geológica (0-10 km); voladizos horizontales (fuerza neta vertical reversible)",
        "texto": (
            "NEC-SE-DS, Sección 3.4.1 — Caso general. La componente "
            "vertical Ev puede definirse escalando la componente "
            "horizontal Eh por un factor mínimo de 2/3: Ev = (2/3) · Eh.\n\n"
            "Sección 3.4.2 — Caso particular: estructuras esenciales o "
            "especiales en campo cercano (0-10 km) de una falla "
            "superficial. NO se puede usar la fórmula anterior — se debe "
            "evaluar la componente vertical mediante estudio de respuesta "
            "de sitio.\n\n"
            "Sección 3.4.3 — Elementos que exceden los límites de las "
            "plantas de los pisos (ej. voladizos horizontales). Se "
            "diseñan para una fuerza neta vertical reversible: "
            "Frev = Wp · Z · Fa · I, donde Wp = peso que actúa en el "
            "voladizo, I = coeficiente de importancia (sección 4.1). La "
            "expresión asume que, en campo no cercano, la acción vertical "
            "máxima es 2/3 de la horizontal máxima, con un espectro plano "
            "definido por Z·Fa."
        ),
    },
    {
        "id": "NECSEDS-S3_5-COMBINACION_ORTOGONAL_VERTICAL",
        "seccion": "3.5",
        "titulo": "Combinación de fuerzas sísmicas ortogonales (100%/30%, o SRSS) y con la componente vertical (E = Eh + 0,3·Ev)",
        "texto": (
            "NEC-SE-DS, Sección 3.5.1 — Combinación de las componentes "
            "horizontales. Se considera la concurrencia simultánea de los "
            "efectos ortogonales, tomando la combinación más "
            "desfavorable entre 2 formulaciones:\n\n"
            "Combinación 1 (Eh1) — 100% de las fuerzas en una dirección + "
            "30% en la perpendicular: "
            "Eh1 = máx[(Ex + 0,3·Ey); (0,3·Ex + Ey)].\n\n"
            "Combinación 2 (Eh2) — raíz cuadrada de la suma de cuadrados: "
            "Eh2 = √(Ex² + Ey²).\n\n"
            "Combinación más desfavorable: Eh = máx[Eh1; Eh2].\n\n"
            "Sección 3.5.2 — Combinación de las componentes horizontales y "
            "vertical. Los efectos totales del sismo E se representan "
            "combinando las 3 componentes: E = Eh + 0,3 · Ev, donde Eh = "
            "componente horizontal combinada, Ev = componente vertical "
            "(sección 3.4)."
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
