"""
Carga ficha técnica curada de ACI 318-05 (Cap. 11 — Cortante y Torsión,
Cap. 21 — Disposiciones especiales para diseño sísmico) a ntc_chunks.

Por qué ficha técnica y no texto verbatim completo: el PDF fuente (495
páginas, packages/construdata/normativa_raw/aci/aci_318_05.pdf, extraído
2026-08-19 desde Drive id=1cjSTClWoCledyeZAnIdEIZuJUKD_lehe) tiene layout
a dos columnas con ecuaciones subindicadas -- pypdf revuelve el orden de
lectura en fórmulas complejas (confirmado real: "φVn ≥ Vu (11-1)" se
extrajo como "φ ≥nuVV (11-1)"). Insertar eso tal cual habría metido
fórmulas incorrectas en un producto de ingeniería real. En vez de eso,
cada ecuación aquí se redactó a mano y se incluye solo si se pudo
verificar con alta confianza (son ecuaciones estándar de pregrado/
práctica profesional, no coeficientes oscuros de una tabla específica).

El texto crudo completo queda guardado en
packages/construdata/normativa_raw/aci/aci_318_05_full.txt (1.6M
caracteres, 495 páginas) para una futura pasada con verificación visual
página por página (Read con `pages`) si se decide ampliar la cobertura
-- especialmente el Capítulo 12 (Longitudes de desarrollo), que quedó
fuera de este lote porque su ecuación básica (12-1) tiene varios
coeficientes (ψt, ψe, ψs, (cb+Ktr)/db) que sí requieren esa verificación.

Uso: python scripts/ingesta/aci_318/ingest_aci_318_cap11_21.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


FICHA_CAP11 = [
    {
        "seccion": "Cap. 11.1 — Resistencia al cortante, requisito general",
        "titulo": "Ecuación general de resistencia al cortante",
        "contenido": (
            "ACI 318-05 Cap. 11 exige que el diseño de secciones sometidas a cortante "
            "cumpla φVn ≥ Vu (Ec. 11-1), donde Vu es la fuerza cortante mayorada en la "
            "sección y Vn es la resistencia nominal al cortante. La resistencia nominal "
            "se calcula como Vn = Vc + Vs (Ec. 11-2): Vc es la resistencia que aporta el "
            "concreto y Vs la que aporta el refuerzo de cortante (estribos). El factor "
            "de reducción de resistencia para cortante es φ = 0.75."
        ),
    },
    {
        "seccion": "Cap. 11.3 — Resistencia al cortante proporcionada por el concreto",
        "titulo": "Vc para elementos no preesforzados sometidos solo a cortante y flexión",
        "contenido": (
            "Para elementos no preesforzados sometidos únicamente a cortante y flexión, "
            "el valor simplificado de Vc (en unidades SI, f'c y resultado en N) es "
            "Vc = 0.17·λ·√f'c·bw·d, donde bw es el ancho del alma, d el peralte efectivo "
            "y λ el factor de concreto liviano (λ = 1.0 para concreto de peso normal, "
            "menor para liviano). ACI 318 también permite una expresión más detallada "
            "que incluye el efecto de la cuantía de refuerzo longitudinal y la relación "
            "momento/cortante (Vu·d/Mu), normalmente reservada para diseño más refinado."
        ),
    },
    {
        "seccion": "Cap. 11.5 — Resistencia al cortante proporcionada por el refuerzo",
        "titulo": "Vs con estribos perpendiculares al eje del elemento",
        "contenido": (
            "Cuando el refuerzo de cortante es perpendicular al eje del elemento, "
            "Vs = Av·fy·d/s, donde Av es el área del refuerzo de cortante dentro de un "
            "espaciamiento s, fy su esfuerzo de fluencia y d el peralte efectivo. ACI 318 "
            "limita fy usado en este cálculo a un máximo de 420 MPa (salvo refuerzo "
            "electrosoldado de alambre, que puede llegar a 550 MPa)."
        ),
    },
    {
        "seccion": "Cap. 11.5.4-11.5.5 — Espaciamiento máximo del refuerzo de cortante",
        "titulo": "Límites de separación de estribos",
        "contenido": (
            "El espaciamiento máximo del refuerzo de cortante perpendicular al eje del "
            "elemento es d/2 (sin exceder 600 mm). Si Vs excede 0.33·√f'c·bw·d, ese "
            "espaciamiento máximo se reduce a la mitad: d/4 (sin exceder 300 mm) -- regla "
            "pensada para asegurar que cada grieta diagonal potencial sea interceptada por "
            "al menos un estribo."
        ),
    },
    {
        "seccion": "Cap. 11.4.6.3 — Refuerzo mínimo de cortante",
        "titulo": "Cuándo se exige refuerzo mínimo de cortante",
        "contenido": (
            "ACI 318 exige refuerzo mínimo de cortante en casi todo elemento de concreto "
            "reforzado sometido a flexión donde Vu exceda la mitad de φVc (con excepciones "
            "puntuales: losas, zapatas, algunas vigas de poco peralte). El área mínima "
            "típica es Av,min = 0.062·√f'c·(bw·s/fy), sin ser menor que 0.35·(bw·s/fy) -- "
            "evita una falla frágil súbita al agrietarse el concreto sin refuerzo que "
            "redistribuya el esfuerzo."
        ),
    },
    {
        "seccion": "Cap. 11.6 — Cortante por fricción",
        "titulo": "Concepto de cortante por fricción (shear-friction)",
        "contenido": (
            "El cortante por fricción (11.6, referenciado también en 11.7) modela la "
            "transferencia de cortante a través de un plano de posible agrietamiento o "
            "junta (interfaz concreto-concreto colocado en momentos distintos, o "
            "concreto-acero) mediante fricción generada por refuerzo perpendicular al "
            "plano que actúa como abrazadera. Es el concepto clave para diseñar "
            "conexiones en elementos prefabricados y ménsulas cortas."
        ),
    },
    {
        "seccion": "Cap. 11.6.5 — Ménsulas y cartelas (corbels)",
        "titulo": "Aplicabilidad de disposiciones para ménsulas",
        "contenido": (
            "Las disposiciones de ménsulas y cartelas (11.6, antes 11.9 en ediciones "
            "previas) aplican a elementos en voladizo corto (relación luz de cortante a "
            "peralte a/d ≤ 1) que transmiten cargas principalmente por acción de puntal-"
            "tensor, no por flexión clásica -- requieren refuerzo horizontal cerrado "
            "(estribos) además del refuerzo principal de tracción por el efecto de "
            "cortante por fricción dominante."
        ),
    },
    {
        "seccion": "Cap. 11.5.1 — Torsión, criterio general",
        "titulo": "Ecuación general de resistencia a la torsión",
        "contenido": (
            "Análogo al cortante, el diseño por torsión exige φTn ≥ Tu, donde Tu es el "
            "momento torsor mayorado y Tn la resistencia nominal a torsión. ACI 318 "
            "permite despreciar la torsión (Tu por debajo de un umbral, típicamente "
            "φ·0.083·λ·√f'c·(Acp²/pcp) para secciones sólidas no preesforzadas) cuando el "
            "efecto es de compatibilidad y no de equilibrio -- es decir, cuando la "
            "estructura puede redistribuir el momento torsor sin comprometer el "
            "equilibrio global."
        ),
    },
    {
        "seccion": "Cap. 11.5.3 — Modelo de torsión en tubo de pared delgada",
        "titulo": "Analogía del tubo de pared delgada / armadura espacial",
        "contenido": (
            "Para el diseño de refuerzo por torsión, ACI 318 usa el modelo de tubo de "
            "pared delgada con analogía de armadura espacial (thin-walled tube / space "
            "truss analogy): la sección se idealiza como un tubo hueco con un área "
            "encerrada Aoh, y la resistencia se calcula en términos de esa área cerrada "
            "por el eje del refuerzo transversal cerrado, no el área bruta de la "
            "sección."
        ),
    },
]

FICHA_CAP21 = [
    {
        "seccion": "Cap. 21.1 — Alcance del diseño sísmico especial",
        "titulo": "Aplicabilidad según nivel de diseño sismorresistente",
        "contenido": (
            "El Capítulo 21 de ACI 318 aplica disposiciones especiales de detallado "
            "según el nivel de diseño sismorresistente exigido: ordinario (sin requisitos "
            "adicionales significativos), intermedio (DMO -- pórticos y muros con "
            "ductilidad moderada) y especial (DES -- pórticos y muros especiales, con los "
            "requisitos de detallado más estrictos). NSR-10 mapea sus propios niveles de "
            "capacidad de disipación de energía (DMI/DMO/DES) directamente sobre esta "
            "clasificación de ACI 318."
        ),
    },
    {
        "seccion": "Cap. 21.2 — Requisitos generales de materiales",
        "titulo": "f'c mínimo y acero de refuerzo en zonas sísmicas",
        "contenido": (
            "Para elementos que resisten fuerzas sísmicas con capacidad de disipación de "
            "energía moderada o especial, ACI 318 exige f'c ≥ 21 MPa (concreto liviano "
            "≥ 21 MPa también, con verificación adicional). El refuerzo longitudinal debe "
            "cumplir requisitos de ductilidad del acero (relación fu/fy real mínima y "
            "elongación mínima), no basta con cumplir solo el fy nominal -- se exige acero "
            "grado 420 (ASTM A706 preferido, o A615 con ensayos adicionales de "
            "conformidad)."
        ),
    },
    {
        "seccion": "Cap. 21.5 — Pórticos especiales resistentes a momento (vigas)",
        "titulo": "Requisitos de vigas en pórticos especiales (DES)",
        "contenido": (
            "En vigas de pórticos especiales resistentes a momento: la cuantía de acero "
            "longitudinal no debe exceder 0.025, debe haber refuerzo continuo superior e "
            "inferior con al menos 2 barras y una cuantía mínima ρmin = 0.25·√f'c/fy (sin "
            "ser menor que 1.4/fy), y la resistencia a momento positivo en la cara del "
            "nudo no debe ser menor que la mitad de la resistencia a momento negativo en "
            "esa misma cara -- busca asegurar ductilidad y evitar una falla fràgil por "
            "sobre-refuerzo."
        ),
    },
    {
        "seccion": "Cap. 21.6 — Pórticos especiales resistentes a momento (columnas)",
        "titulo": "Criterio de columna fuerte-viga débil (strong column-weak beam)",
        "contenido": (
            "ACI 318 exige el principio de columna fuerte-viga débil: la suma de las "
            "resistencias nominales a flexión de las columnas que llegan a un nudo debe "
            "ser al menos 1.2 veces la suma de las resistencias nominales a flexión de "
            "las vigas que llegan a ese mismo nudo (ΣMnc ≥ 1.2·ΣMnb). El objetivo es "
            "forzar que las rótulas plásticas se formen en las vigas, no en las columnas "
            "-- un mecanismo de columna débil puede colapsar el piso completo, mientras "
            "que rótulas en vigas son más controlables y menos catastróficas."
        ),
    },
    {
        "seccion": "Cap. 21.6.4 — Refuerzo transversal de confinamiento en columnas",
        "titulo": "Zona de confinamiento en los extremos de columna (lo)",
        "contenido": (
            "En los extremos de columnas de pórticos especiales, dentro de una longitud "
            "lo (la mayor entre: el peralte de la columna, 1/6 de la luz libre, o 450 mm) "
            "se exige refuerzo transversal de confinamiento (estribos cerrados de "
            "confinamiento o espirales) con espaciamiento reducido -- típicamente el "
            "menor entre 1/4 de la dimensión mínima de la columna, 6 veces el diámetro de "
            "la barra longitudinal, o un valor calculado por una fórmula de "
            "espaciamiento máximo (so). Esta zona confinada es donde se espera la "
            "formación de rótulas plásticas y donde el concreto necesita más ductilidad "
            "para no desmoronarse ante ciclos de carga sísmica."
        ),
    },
    {
        "seccion": "Cap. 21.9 — Muros estructurales especiales",
        "titulo": "Elementos de borde especiales (special boundary elements)",
        "contenido": (
            "Los muros estructurales especiales requieren evaluar si necesitan elementos "
            "de borde especiales (zonas de confinamiento reforzado en los extremos del "
            "muro) mediante uno de dos métodos: (a) el método basado en desplazamientos "
            "(displacement-based, evalúa la profundidad del eje neutro bajo la deriva de "
            "diseño) o (b) el método basado en esfuerzos (stress-based, evalúa si el "
            "esfuerzo de compresión en la fibra extrema excede 0.2·f'c). Si se requieren, "
            "estos elementos de borde llevan el mismo tipo de confinamiento transversal "
            "exigido en columnas especiales."
        ),
    },
    {
        "seccion": "Cap. 21.7 — Nudos viga-columna en pórticos especiales",
        "titulo": "Resistencia al cortante del nudo",
        "contenido": (
            "El nudo (la zona donde se cruzan vigas y columnas) de un pórtico especial "
            "se diseña por cortante con una resistencia nominal Vn que depende de si el "
            "nudo está confinado en las 4 caras por vigas, en 3 caras, o en menos -- ACI "
            "318 da 3 expresiones distintas (γ·√f'c·Aj, con γ = 1.7, 1.25 o 1.0 según el "
            "grado de confinamiento) donde Aj es el área efectiva de la sección "
            "transversal del nudo. También exige refuerzo transversal mínimo dentro del "
            "nudo, salvo que las 4 caras estén confinadas por vigas de ancho suficiente."
        ),
    },
    {
        "seccion": "Cap. 21.3 — Pórticos con capacidad de disipación moderada (DMO)",
        "titulo": "Diferencia entre pórticos DMO y pórticos especiales (DES)",
        "contenido": (
            "Los pórticos con capacidad de disipación de energía moderada (DMO, sección "
            "21.3 en ediciones ACI 318 posteriores a esta reorganización) tienen "
            "requisitos de detallado menos estrictos que los pórticos especiales: exigen "
            "refuerzo transversal en los extremos de vigas y columnas pero con criterios "
            "de espaciamiento y confinamiento menos exigentes, y no aplican el criterio "
            "estricto de columna fuerte-viga débil de 21.6. Se usan en zonas de amenaza "
            "sísmica intermedia, no en las de mayor amenaza."
        ),
    },
]


def _rows(ficha: list[dict], norma_label: str, norma_id: str) -> list[dict]:
    return [{
        "seccion": f["seccion"],
        "titulo": f["titulo"],
        "norma": norma_label,
        "contenido": f["contenido"],
        "norma_id": norma_id,
    } for f in ficha]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "ACI-318-05").execute()
    if not norma_row.data:
        raise RuntimeError("ACI-318-05 no existe en normas_registro -- registrarlo primero")
    norma_id = norma_row.data[0]["id"]

    norma_label = "ACI 318-05 (ficha técnica curada -- Cap. 11 y 21, no es el texto completo verbatim)"
    rows = _rows(FICHA_CAP11, norma_label, norma_id) + _rows(FICHA_CAP21, norma_label, norma_id)
    print(f"Total chunks: {len(rows)} (Cap. 11: {len(FICHA_CAP11)}, Cap. 21: {len(FICHA_CAP21)})")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando ficha técnica previa de ACI-318-05 (idempotente, por norma_id)...")
    borrado = sb.table("ntc_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a ntc_chunks...")
    sb.table("ntc_chunks").insert(rows).execute()
    print(f"OK: {len(rows)} chunks de ficha técnica ACI 318-05 cargados (norma_id={norma_id})")


if __name__ == "__main__":
    main()
