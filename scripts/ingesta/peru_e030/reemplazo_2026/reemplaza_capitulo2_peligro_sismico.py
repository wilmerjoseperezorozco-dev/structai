"""
REEMPLAZA el Capítulo II (Peligro Sísmico) de peru_e030_chunks con el
texto vigente de la E.030 modificada por la Resolución Ministerial N.°
183-2026-VIVIENDA (3-may-2026) -- ver issue #13 del repo.

Contexto: el corpus original de Perú (2026-08-24) se construyó con la
RM N.° 043-2019-VIVIENDA, edición ya obsoleta desde mayo 2026. La nueva
resolución NO modifica artículos puntuales -- reemplaza el texto
completo de la norma, renumerado (53->74 artículos, 2->4 anexos). Este
es el primer capítulo reingestado con el texto 2026 (más urgente por
peso Y por ser donde está el cambio ya confirmado en producción:
umbral de suelo S0 bajó de Vs≥1500 a Vs≥800 m/s, categoría S5 nueva).

Fuente: texto oficial de "El Peruano", Separata Especial, domingo
3-may-2026, RM N.° 183-2026-VIVIENDA (verificado con pypdf: encabezado
oficial del diario, firma del Ministro Wilder Alejandro Sifuentes
Quilcate, fecha de la resolución 28-abr-2026). El acceso directo a
busquedas.elperuano.pe/gob.pe devolvió 404/418 con herramientas
automatizadas -- se usó un espejo de terceros (Google Drive, enlazado
desde ccipperu.com), pero el contenido fue verificado auténtico contra
el encabezado oficial antes de usarlo.

ESTRATEGIA DE REEMPLAZO (documentada explícitamente, no silenciosa):
se ELIMINAN los 41 chunks viejos con prefijo "E030-CAP2-*" (numeración
2019: Artículos 10-14) y se insertan los nuevos con prefijo
"E030-2026-CAP2-*" (numeración 2026: Artículos 10-18 -- el capítulo
creció de 5 a 9 artículos). No se mantienen ambas versiones activas a
la vez para el mismo contenido -- causaría que la búsqueda semántica
mezclara datos de 2019 y 2026 en una misma respuesta, exactamente el
riesgo que se está corrigiendo.

Cambios reales confirmados en este capítulo (Tabla 1 SIN cambios --
factor Z idéntico 0,45/0,35/0,25/0,10; Tablas 2/3 CON cambios reales --
ver docstring de cada chunk):
- Art 10-11 (Tabla 1, factor Z): sin cambio de valores, solo renumerado.
- Art 14 (Tabla 2/3, perfiles de suelo): S0 pasó de Vs≥1500 a Vs≥800
  m/s; se agregó S5 (suelos excepcionales); nuevo requisito Ts para
  categorías A/B en zona 4.
- Art 17 (Tabla 4/5, parámetros S/TP/TL): la estructura cambió de
  valores fijos por zona/suelo a RANGOS interpolables según Vs30 real
  dentro de cada perfil S2/S3.
- Art 18 (Tabla 6, factor C): fórmula general no confirmable con
  precisión de esta extracción (ver "no inventar" en el chunk), pero
  el valor C=2,5 para T≤TP sí está legible y coincide con la práctica
  ya conocida.

Uso: python scripts/ingesta/peru_e030/reemplazo_2026/reemplaza_capitulo2_peligro_sismico.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 (ed. 2026, RM 183-2026-VIVIENDA) — Capítulo II: Peligro Sísmico"

IDS_VIEJOS_A_ELIMINAR_PREFIJO = "E030-CAP2-"

CHUNKS = [
    {
        "id": "E030-2026-CAP2-ART10-ZONIFICACION",
        "seccion": "Artículo 10 (ed. 2026)",
        "titulo": "Zonificación sísmica: 4 zonas (Figura N°1); Anexo II contiene el listado de provincias/distritos por zona",
        "texto": (
            "E.030 (edición 2026, RM 183-2026-VIVIENDA), Artículo 10 — "
            "Zonificación. La zonificación resulta de la distribución "
            "espacial de la sismicidad observada, las características "
            "generales de los movimientos sísmicos y su atenuación con "
            "la distancia epicentral, y la información neotectónica. El "
            "territorio nacional se divide en 4 zonas (Figura N°1, "
            "Zonas sísmicas). El Anexo II de la norma contiene el "
            "listado de provincias y distritos que corresponden a cada "
            "zona."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART11-TABLA1-FACTOR_Z",
        "seccion": "Artículo 11, Tabla N°1 (ed. 2026)",
        "titulo": "Factor de zona Z por zona 1-4 (0,10 a 0,45) — SIN CAMBIO respecto a la edición 2019, solo renumerado de Artículo 11 a 11",
        "texto": (
            "Artículo 11 — Factores de zona 'Z'. A cada zona se asigna "
            "un factor Z según la Tabla N°1. Representa la aceleración "
            "máxima horizontal en suelo rígido con 10% de probabilidad "
            "de ser excedida en 50 años, expresada como fracción de la "
            "aceleración de la gravedad.\n\n"
            "Tabla N°1 — Factores de zona Z (verbatim, ed. 2026): "
            "Zona 4 → Z=0,45. Zona 3 → Z=0,35. Zona 2 → Z=0,25. "
            "Zona 1 → Z=0,10.\n\n"
            "Nota: estos valores son IDÉNTICOS a los de la edición 2019 "
            "de la E.030 — la RM 183-2026-VIVIENDA no modificó el "
            "factor Z, solo renumeró el artículo."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART12-MICROZONIFICACION",
        "seccion": "Artículo 12 (ed. 2026)",
        "titulo": "Estudios de microzonificación obligatorios en zonas de expansión urbana y reconstrucción post-desastre; remite al Anexo III (contenido mínimo, nuevo en esta edición)",
        "texto": (
            "Artículo 12 — Microzonificación sísmica. Los estudios de "
            "microzonificación sísmica deben suministrar información "
            "sobre la posible modificación de las acciones sísmicas por "
            "condiciones locales y otros fenómenos naturales, así como "
            "las limitaciones y exigencias que se deriven de esos "
            "estudios para el diseño y construcción. Se deben realizar "
            "estudios de microzonificación en: (a) zonas de expansión "
            "de áreas urbanas; (b) reconstrucción de áreas urbanas con "
            "daños parciales o totales por fenómenos naturales. Se debe "
            "aplicar lo establecido en el Anexo III de la norma "
            "(Contenido Mínimo para la Ejecución de Estudios de "
            "Microzonificación Sísmica — anexo nuevo en la edición "
            "2026, no existía en la edición 2019)."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART13-ESTUDIOS_SITIO",
        "seccion": "Artículo 13 (ed. 2026)",
        "titulo": "Estudios de sitio: determinan parámetros de diseño limitados al lugar del proyecto; nunca inferiores a los de la norma; aplican en complejos industriales/químicos/explosivos",
        "texto": (
            "Artículo 13 — Estudios de sitio. Tienen como objetivo "
            "principal determinar los parámetros de diseño, están "
            "limitados al lugar del proyecto, y suministran información "
            "sobre la posible modificación de las acciones sísmicas y "
            "otros fenómenos naturales por condiciones locales. No deben "
            "emplearse parámetros de diseño inferiores a los indicados "
            "en esta norma. Se realizan, entre otros casos, en grandes "
            "complejos industriales, industria de explosivos, productos "
            "químicos inflamables y contaminantes."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART14-TABLA2-PERFILES_S0_S1_S2",
        "seccion": "Artículo 14.1-14.6, Tabla N°2 (ed. 2026)",
        "titulo": "Perfiles de suelo S0 (roca, Vs≥800 m/s -- CAMBIÓ, antes 1500), S1 (550-800 m/s) y S2 (350-550 m/s); criterio de clasificación por Vs30/N60/Su en los 30 m superiores",
        "texto": (
            "Artículo 14 — Perfiles de suelo. Los perfiles de suelo se "
            "clasifican según la velocidad promedio de propagación de "
            "ondas de corte (Vs30); alternativamente, para suelos "
            "granulares, el promedio ponderado de N60 (ensayo SPT); y "
            "para suelos cohesivos, el promedio ponderado de la "
            "resistencia al corte en condición no drenada (Su). Estas "
            "propiedades se determinan en los 30 m superiores del "
            "perfil, medidos desde el fondo de cimentación (artículo 15). "
            "Para suelos heterogéneos (cohesivos y granulares), se toma "
            "el perfil más desfavorable entre los dos criterios.\n\n"
            "Tabla N°2 — Tipos de perfiles de suelo (verbatim, ed. "
            "2026):\n"
            "  S0 'Roca': rocas con distintos grados de fracturación y "
            "rocas sanas con Vs30 ≥ 800 m/s (⚠️ CAMBIÓ respecto a la "
            "edición 2019, que exigía Vs30 > 1500 m/s — el umbral bajó "
            "significativamente). Si la roca dura es continua hasta 30 "
            "m, se puede usar la velocidad superficial para estimar "
            "Vs30.\n"
            "  S1 'Suelos muy rígidos': Vs30 entre 550 y 800 m/s; o "
            "grava arenosa muy densa con bolonería; o arena muy densa/"
            "grava arenosa densa con N60 > 50; o arcilla muy compacta "
            "(espesor <20 m) con Su > 100 kPa e incremento gradual de "
            "propiedades con la profundidad.\n"
            "  S2 'Suelos rígidos': Vs30 entre 350 y 550 m/s; o arena "
            "densa gruesa a media/grava arenosa medianamente densa con "
            "N60 entre 30 y 50; o arcilla muy compacta (espesor <20 m) "
            "con Su entre 80 y 100 kPa."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART14-TABLA2-PERFILES_S3_S4_S5",
        "seccion": "Artículo 14.6, Tabla N°2 (ed. 2026)",
        "titulo": "Perfiles S3 (200-350 m/s), S4 (<200 m/s), y S5 'suelos excepcionales' -- categoría NUEVA (licuables, colapsables, orgánicos, turba; construcción prohibida salvo estudio específico)",
        "texto": (
            "Tabla N°2 — Tipos de perfiles de suelo (continuación):\n"
            "  S3 'Suelos intermedios': Vs30 entre 200 y 350 m/s; o "
            "arena media a fina con N60 entre 15 y 30; o suelo "
            "cohesivo con Su entre 50 y 80 kPa.\n"
            "  S4 'Suelos blandos': Vs30 < 200 m/s; o arena media a fina "
            "con N60 < 15; o suelo cohesivo blando con Su < 50 kPa; o "
            "cualquier perfil (no S5) con más de 3 m de suelo con "
            "índice de plasticidad IP > 20, contenido de humedad w > "
            "40%, y Su < 25 kPa.\n"
            "  S5 'Suelos excepcionales' (⚠️ CATEGORÍA NUEVA — no "
            "existía en la edición 2019): suelos potencialmente "
            "licuables, excepcionalmente flexibles, susceptibles de "
            "densificación por vibración, colapsables, orgánicos, "
            "turba, suelos finos saturados, sitios con condiciones "
            "geológicas/topográficas particularmente desfavorables, o "
            "con fenómenos de amplificación local. Estos casos NO están "
            "cubiertos por la Tabla N°2 — se PROHÍBEN construcciones "
            "sobre estos perfiles, salvo un estudio específico del "
            "sitio que considere mejoramientos del estrato."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART14-TABLA3-CLASIFICACION_Y_TS",
        "seccion": "Artículo 14.7-14.8, Tabla N°3 (ed. 2026)",
        "titulo": "Tabla N°3 resumen numérico S0-S4 (Vs/N60/Su); verificación obligatoria del período predominante Ts contra 0,65·TP para categorías A/B en zona 4 (Suelos S1-S4) -- requisito NUEVO",
        "texto": (
            "14.7. La Tabla N°3 resume los intervalos numéricos para "
            "clasificar el perfil de suelo:\n\n"
            "Tabla N°3 — Clasificación de los perfiles de suelo "
            "(verbatim, ed. 2026): S0 → Vs30 ≥ 800 m/s. S1 → Vs30 550 a "
            "800 m/s, N60 > 50, Su > 100 kPa. S2 → Vs30 350 a 550 m/s, "
            "N60 30 a 50, Su 80 a 100 kPa. S3 → Vs30 200 a 350 m/s, N60 "
            "15 a 30, Su 50 a 80 kPa. S4 → Vs30 < 200 m/s, N60 < 15, "
            "Su < 50 kPa.\n\n"
            "14.8. Para clasificar un perfil, se usa la Tabla N°3. "
            "ADICIONALMENTE (⚠️ requisito NUEVO en la edición 2026, no "
            "existía en 2019): para edificaciones categorías A y B en "
            "Zona 4 (suelos S1-S4), se debe verificar que el período "
            "predominante del sitio Ts (obtenido por razones espectrales "
            "H/V) sea menor que 0,65·TP (Tabla N°5). Si Ts es mayor que "
            "0,65·TP, se debe tomar el perfil de suelo siguiente más "
            "desfavorable de la Tabla N°2, con el límite superior de "
            "TP, o desarrollar un estudio de sitio específico (artículo "
            "13)."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART15-FORMULAS_VS30_TS_N60_SU",
        "seccion": "Artículo 15 (ed. 2026)",
        "titulo": "Cálculo de Vs30 (promedio ponderado por espesor), Ts (técnica SESAME, mínimo 3 mediciones H/V de 30 min), N60 y Su (promedios ponderados solo sobre estratos granulares/cohesivos respectivamente)",
        "texto": (
            "Artículo 15 — Determinación de los perfiles de suelo. Las "
            "expresiones de este artículo aplican a los 30 m superiores "
            "del perfil, medidos desde el fondo de cimentación.\n\n"
            "15.2. La velocidad promedio de ondas de corte (Vs30) se "
            "calcula como un promedio ponderado por el espesor di de "
            "cada uno de los n estratos, en función de la velocidad Vsi "
            "de cada estrato. [Notación algebraica exacta con sumatorias "
            "no recuperable con precisión de esta extracción del PDF.]\n\n"
            "15.3-15.4. El período predominante Ts del depósito se "
            "estima con mediciones de vibraciones ambientales y la "
            "razón espectral Horizontal/Vertical (H/V) — mínimo 3 "
            "mediciones de al menos 30 minutos cada una, interpretadas "
            "según los criterios del proyecto europeo SESAME (Site "
            "effects assessment using ambient excitations), "
            "seleccionando la interpretación que dé la clasificación "
            "sísmica más conservadora.\n\n"
            "15.5-15.6. N60 (promedio ponderado, solo sobre los m "
            "estratos granulares) y Su (promedio ponderado, solo sobre "
            "los k estratos cohesivos) se calculan con la misma lógica "
            "de ponderación por espesor. [Notación algebraica exacta no "
            "recuperable con precisión de esta extracción.]"
        ),
    },
    {
        "id": "E030-2026-CAP2-ART16-EMS_ITS_PILOTES",
        "seccion": "Artículo 16 (ed. 2026)",
        "titulo": "Todo proyecto requiere EMS o ITS (según E.050); en cimentaciones profundas con pilotes, el perfil de suelo se toma en los 30 m bajo el extremo superior de los pilotes",
        "texto": (
            "Artículo 16 — Consideraciones geotécnicas adicionales. Todo "
            "proyecto de edificación debe contar con Estudio de "
            "Mecánica de Suelos (EMS) o Informe Técnico de Suelos (ITS), "
            "según corresponda, conforme a la Norma Técnica E.050 "
            "Suelos y Cimentaciones del RNE. En estructuras con "
            "cimentaciones profundas a base de pilotes, el perfil de "
            "suelo es el que corresponde a los estratos en los 30 m por "
            "debajo del extremo superior de los pilotes."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART17-TABLA4_5-FACTOR_S_TP_TL",
        "seccion": "Artículo 17, Tablas N°4 y N°5 (ed. 2026)",
        "titulo": "Factor de suelo S y períodos TP/TL por zona y perfil S0-S4; ⚠️ CAMBIO ESTRUCTURAL: ahora son RANGOS interpolables según Vs30 real, no valores fijos como en la edición 2019",
        "texto": (
            "Artículo 17 — Parámetros de sitio (S, TP y TL). Se "
            "selecciona el perfil que mejor describa las condiciones "
            "locales, usando los valores de S, TP y TL de las Tablas "
            "N°4 y N°5.\n\n"
            "Tabla N°4 — Factor de suelo S (verbatim, ed. 2026; ⚠️ "
            "estructura cambiada respecto a 2019 — S2 y S3 ahora son "
            "RANGOS, no valores únicos): Zona 4 → S0=0,80, S1=1,00, "
            "S2=1,00-1,10, S3=1,10-1,20 (S4 requiere análisis de "
            "respuesta de sitio específico). Zona 3 → S0=0,80, S1=1,00, "
            "S2=1,00-1,15, S3=1,15-1,20, S4=1,30. Zona 2 → S0=0,80, "
            "S1=1,00, S2=1,00-1,30, S3=1,30-1,40, S4=1,70. Zona 1 → "
            "S0=0,80, S1=1,00, S2=1,00-1,30, S3=1,30-1,60, S4=2,40.\n\n"
            "Tabla N°5 — Períodos TP y TL (verbatim, ed. 2026, también "
            "en rangos para S2/S3): S0 → TP=0,3s, TL=3,0s. S1 → "
            "TP=0,4s, TL=2,5s. S2 → TP=0,4-0,6s, TL=2,5-2,0s. S3 → "
            "TP=0,6-0,9s, TL=2,0-1,6s. S4 → TP=1,2s, TL=1,6s.\n\n"
            "Nota (*): S, TP y TL se definen interpolando linealmente "
            "entre los extremos del rango según la velocidad de ondas "
            "de corte real (Tabla N°3). Si no se dispone de Vs30, se "
            "toma el mayor valor del rango para S, y TP=0,6s/TL=2,0s "
            "para S2, o TP=0,9s/TL=1,60s para S3."
        ),
    },
    {
        "id": "E030-2026-CAP2-ART18-TABLA6-FACTOR_C",
        "seccion": "Artículo 18, Tabla N°6 (ed. 2026)",
        "titulo": "Factor de amplificación sísmica C, 3 tramos según T/TP/TL; C=2,5 fijo para T≤TP (usado en la fuerza cortante basal del análisis estático, artículo 34)",
        "texto": (
            "Artículo 18 — Factor de amplificación sísmica (C). Se "
            "determina C según la Tabla N°6, en función del período "
            "fundamental de la estructura T comparado con TP y TL (3 "
            "tramos: T≤TP, TP<T≤TL, T>TL). [La expresión algebraica "
            "exacta de los 3 tramos no se pudo recuperar con precisión "
            "de esta extracción del PDF — la forma general reconocible "
            "es la ya usada en ediciones previas de la E.030: C=2,5 "
            "para T≤TP; C decreciente proporcional a TP/T para TP<T≤TL; "
            "C decreciente proporcional a TP·TL/T² para T>TL — no "
            "confirmado carácter por carácter contra este documento, "
            "verificar contra el texto oficial antes de citar la "
            "fórmula completa.]\n\n"
            "C se interpreta como el factor de amplificación de la "
            "aceleración estructural respecto a la aceleración en el "
            "suelo. Para determinar la fuerza cortante basal del "
            "análisis estático (artículo 34), se debe usar C=2,5 en "
            "todo el rango de T≤TP — este valor sí es legible con "
            "precisión en el documento."
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
