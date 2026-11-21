"""
NSR-10 Título B, capítulo B.6 (viento): numerales con encabezado real en el
PDF y sin texto en el corpus (issue #186, Fase 1 de
scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md).

Fuente: raw/NSR-10-240-301.pdf (Drive 1ZLlTm7J__ucSvEt99qizpl3AocB12naL,
3.101.062 bytes, verificado 2026-11-11). Extracción de encabezado a encabezado
con el modo estricto de encabezado (`titulo_f=True`): con el modo normal, la
referencia "B.6.5-2" dentro de la nomenclatura se tomaba como encabezado y
cortaba B.6.3 a mitad de texto.

Vigencia, verificada antes de escribir (regla de CLAUDE.md), para estos numerales:
- Decreto 1711 de 2021: su anexo técnico (leído completo, 39 páginas) solo toca
  del Título B la Figura B.6.4-1. No modifica B.6.1.2, B.6.3 ni B.6.5.6.3.
- Decreto 340 de 2012: su anexo modifica B.4.5-1, la Figura B.6.4-1 y la
  Figura B.6.4-2. No toca estos numerales.
- Decreto 945 de 2017: PENDIENTE de verificar (no se obtuvo una copia legible).
  No ejecutar el upsert hasta cerrarlo o hasta que el dueño del proyecto lo apruebe.

Estado por numeral:
- B.6.1.2 y B.6.5.6.3: extracción limpia; solo se corrigen palabras partidas por el PDF.
- B.6.3 (nomenclatura): extracción completa (~7.000 caracteres), pero los
  subíndices salen desordenados ("fA" por A_f, "oiA" por A_oi, "pC" por C_p;
  21 símbolos). PENDIENTE de transcripción manual contra la imagen de la
  página, como en MANUAL de _ingest_titulo_c_etapa1_truncados.py. No se ingiere
  con los símbolos equivocados.

Uso:  python _ingest_titulo_b_b6_huecos_grafo.py            (dry-run: solo muestra)
      python _ingest_titulo_b_b6_huecos_grafo.py --upsert   (escribe; requiere aprobación)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _ingest_titulo_c_etapa1_truncados as base  # noqa: E402

CAPITULO = "NSR-10 Título B — Cargas"
PDF = "NSR-10-240-301.pdf"
LISTOS = {
    "B.6.1.2": "presiones_caras_opuestas",
    "B.6.5.6.3": "categorias_exposicion",
}
PENDIENTES_MANUAL: dict[str, str] = {}

# B.6.3 transcrita leyendo las páginas B-23 a B-25 del PDF (imagen, 2026-11-11), porque la extracción de texto
# desordena los subíndices ("fA" por A_f). Convenciones: subíndice con guion bajo (A_f = A sub f); barra y gorro
# con caracteres Unicode (b̄, b̂, ᾱ, z̄); «I» (factor de importancia) es una I mayúscula aunque la fuente imprime «l»;
# en h, el símbolo del ángulo es θ. 83 símbolos, mismo orden que el PDF.
MANUAL = {
    "B.6.3": (
        "B.6.3 — NOMENCLATURA — La nomenclatura siguiente comprende las variables utilizadas en el presente capítulo. "
        "A = área efectiva para viento, en m²; "
        "A_f = área de un edificio u otra estructura abierta. Puede referirse al área normal a la dirección de viento o al área proyectada en un plano normal a la dirección del viento, en m²; "
        "A_g = área bruta a la cual hace referencia A_o, en m²; "
        "A_gi = la suma de las áreas brutas de toda la superficie del envolvente (paredes y cubierta) sin incluir A_g, en m²; "
        "A_o = área total de aberturas en una pared que recibe presión positiva externa, en m²; "
        "A_oi = la suma del área de aberturas de toda la superficie del envolvente (paredes y cubierta) sin incluir A_o, en m²; "
        "A_og = área total de aberturas en toda la superficie del cerramiento (paredes y cubierta) del edificio, en m²; "
        "A_g = área bruta de la pared sólida libre o la valla rígida, en m²; "
        "a = ancho de la zona para coeficiente de presión, en m; "
        "B = dimensión horizontal del edificio medido en dirección normal a la dirección del viento, en m; "
        "b̄ = factor de velocidad media de viento horaria en la ec. B.6.5-12 de la tabla B.6.5-2; "
        "b̂ = factor de velocidad de ráfaga de 3 segundos, de la tabla B.6.5-2; "
        "C_f = coeficiente de fuerza a usarse en el cálculo de cargas de viento para estructuras diferentes a edificios; "
        "C_N = coeficiente de presión neta a usarse en el cálculo de cargas de viento para edificios abiertos; "
        "C_p = coeficiente de presión externa a usarse en el cálculo de cargas de viento para edificios; "
        "c = factor de intensidad de turbulencia en la ec. B.6.5-3 de la tabla B.6.5-2; "
        "D = diámetro de estructura o miembro circular, en m; "
        "D′ = profundidad de elementos sobresalientes como nervaduras y cornisas, en m; "
        "F = fuerza de viento de diseño para estructuras diferentes a edificios, en N; "
        "G = factor de efecto ráfaga; "
        "G_f = factor de efecto ráfaga para el SPRFV de edificios flexibles y otras estructuras; "
        "GC_pn = coeficiente de presión combinada para un parapeto; "
        "GC_p = producto del coeficiente de presión externa y el factor de efecto ráfaga a usarse en la determinación de cargas de viento para edificios; "
        "GC_pf = producto del coeficiente equivalente de presión externa y el factor de efecto ráfaga a usarse en la determinación de cargas de viento para el SPRFV de edificios bajos; "
        "GC_pi = producto del coeficiente de presión interna y el factor de efecto ráfaga a usarse en la determinación de cargas de viento para edificios; "
        "g_Q = factor pico para respuesta del entorno en las ecs. B.6.5-2 y B.6.5-6; "
        "g_R = factor pico para respuesta de resonancia en las ec. B.6.5-6; "
        "g_v = factor pico para respuesta de viento en las ecs. B.6.5-2 y B.6.5-6; "
        "H = altura de la colina o escarpe en la fig. B.6.5-1, en m; "
        "h = altura media de un edificio o altura de cualquier otra estructura. Se debe usar la altura a la cornisa si el ángulo de inclinación θ es menor o igual a 10°, en m; "
        "h_e = altura de la cornisa en una determinada pared o altura promedio de cornisa si esta varía a los largo de la estructura; "
        "I = factor de importancia; "
        "I_z̄ = intensidad de turbulencia de la ec. B.6.5-6; "
        "K_1, K_2, K_3 = factores de multiplicación en la fig. B.6.5-1 usados para calcular K_zt; "
        "K_d = factor de direccionalidad de viento, en la tabla B.6.5-4; "
        "K_h = coeficiente de exposición de presión por velocidad evaluado en z = h; "
        "K_z = coeficiente de exposición de presión por velocidad evaluado a la altura z; "
        "K_zt = factor topográfico definido en la sección B.6.5.7; "
        "L = dimensión horizontal del edificio medida en dirección paralela a la dirección del viento, en m; "
        "L_h = distancia viento arriba de la cresta de la colina o escarpe en la fig. B.6.5-1, donde la diferencia en elevación de terreno es la mitad de la altura de la colina o escarpe, en m; "
        "L_z̄ = longitud integral a escala de la turbulencia (para modelos a escala en túnel de viento), en m; "
        "L_r = dimensión horizontal de esquina de retorno para un muro libre o valla maciza de la fig. B.6.5-17, en m; "
        "ℓ = factor de escala de longitud integral de la tabla B.6.5-2, en m; "
        "N_1 = frecuencia reducida de la ec. B.6.5-10; "
        "n_1 = frecuencia natural del edificio, en Hz; "
        "p = presión de diseño a usarse en el cálculo de cargas de viento para edificios; "
        "p_L = presión de viento actuando en la cara a sotavento en la fig. B.6.5-6, en N/m²; "
        "p_net = presión neta de viento de diseño de la ec. B.6.4-2, en N/m²; "
        "p_net10 = presión neta de viento de diseño para la categoría de exposición B a h=10.0 m; "
        "p_s = presión neta de viento de diseño de la ec. B.6.4-1, en N/m²; "
        "p_s10 = presión de viento de diseño simplificada para la categoría de exposición B a h=10.0 m en la Fig. B.6.4-2; "
        "p_w = presión de viento actuando en la cara a barlovento en la fig. B.6.5-6, en N/m²; "
        "Q = factor de respuesta del entorno de la ec. B.6.5-4; "
        "q = presión por velocidad, en N/m²; "
        "q_h = presión por velocidad evaluada a la altura z = h, en N/m²; "
        "q_i = presión por velocidad para la determinación de la presión interna, en N/m²; "
        "q_p = presión por velocidad en la parte superior del parapeto, en N/m²; "
        "q_z = presión por velocidad evaluada a una altura z por encima del terreno, en N/m²; "
        "R = factor de respuesta de resonancia de la ec. B.6.5-8; "
        "R_B, R_h, R_L = valores de la ec. B.6.5-8; "
        "R_i = factor de reducción de la ec. B.6.5-14; "
        "R_n = valor de la ec. B.6.5-9; "
        "s = dimensión vertical de un muro libre o una valla maciza de la fig. B.6.5-17, en m; "
        "V = velocidad básica de viento de la fig. B.6.4-1 en m/s. La velocidad básica de viento corresponde a la velocidad de una ráfaga de 3 segundos a una altura de 10 m por encima del suelo en un terreno de categoría de exposición C; "
        "V_i = volumen interno sin particiones, en m³; "
        "V̄_z̄ = velocidad de viento promedia por hora a una altura z̄, m/s; "
        "W = ancho del edificio en las figs. B.6.5-9 y B.6.5-11A y B; y ancho de la luz en las figs. B.6.5-10 y B.6.5-12, en m; "
        "X = distancia hasta el centro de presión desde el borde a barlovento, en m; "
        "x = distancia tomada desde la cima en la dirección de barlovento o sotavento en la fig. B.6.5-1, en m; "
        "z = altura por encima del terreno, en m; "
        "z̄ = altura equivalente de la estructura, en m; "
        "z_g = altura nominal de la capa atmosférica limite usada en este código. Los valores aparecen en la tabla B.6.5-2; "
        "z_min = altura mínima de exposición de la tabla B.6.5-2; "
        "α = exponente para la ley potencial de la velocidad de ráfaga de 3 seg, de la tabla B.6.5-2; "
        "α̂ = inversa de α de la Tabla B.6.5-2; "
        "ᾱ = exponente para la ley potencial de la velocidad media horaria del viento, ec. B.6.5-12 en la tabla B.6.5-2; "
        "β = coeficiente de amortiguamiento, porcentaje crítico para edificios y otras estructuras; "
        "ε = coeficiente de área sólida vs área bruta para muros libres, vallas macizas, vallas abiertas, torres de celosía y otras estructuras de celosía; "
        "λ = factor de ajuste por altura y exposición del edificio de las figs. B.6.4-2 y B.6.4-3; "
        "ε̄ = exponente para la ley potencial de la escala de longitud integral en la ec. B.6.5-5 obtenido de la tabla B.6.5-2; "
        "η = valor usado en la ec. B.6.5-11A (véase sección B.6.5.8.2); "
        "θ = ángulo de inclinación de la cubierta, en grados; "
        "ν = cociente alto/ancho para vallas macizas."
    ),
}
# Palabras partidas por el PDF (verificadas contra la página).
CORRECCIONES = {"categorí a": "categoría", "determ ine": "determine"}


def construir() -> list[dict]:
    chunks = []
    for numeral, slug in LISTOS.items():
        texto = base.extraer(numeral, PDF, titulo_f=True)
        for mal, bien in CORRECCIONES.items():
            texto = texto.replace(mal, bien)
        chunks.append({"id": f"NSR10-B-B_{numeral[2:].replace('.', '_')}_{slug}", "capitulo": CAPITULO,
                       "seccion": numeral, "titulo": texto.split(" — ")[1][:60] if " — " in texto else texto[:60],
                       "texto": f"NSR-10 Título B {texto}"})
    for numeral, texto in MANUAL.items():
        chunks.append({"id": f"NSR10-B-B_{numeral[2:].replace('.', '_')}_nomenclatura", "capitulo": CAPITULO,
                       "seccion": numeral, "titulo": "NOMENCLATURA (variables del capítulo B.6)",
                       "texto": f"NSR-10 Título B {texto}"})
    return chunks


def verificar_manual() -> None:
    """Control de la transcripción: mismo número de símbolos que la extracción automática del
    PDF, y cada definición transcrita aparece en ese texto (comparando sin símbolos ni espacios)."""
    import re
    import unicodedata

    def plano(s):
        s = "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if c.isalnum())
        return s
    extraido = base.extraer("B.6.3", PDF, titulo_f=True)
    n_pdf = extraido.count(" = ")
    entradas = [e for e in MANUAL["B.6.3"].split(" — ", 2)[2].split("; ") if " = " in e]
    n_manual = sum(e.count(" = ") for e in entradas)
    faltan = [e[:50] for e in entradas if plano(e.split(" = ", 1)[1])[:40] not in plano(extraido)]
    print(f"B.6.3 control: símbolos en el PDF {n_pdf} | transcritos {n_manual} | definiciones no halladas en el PDF: {faltan}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upsert", action="store_true", help="escribe en nsr10_chunks (requiere aprobación)")
    args = ap.parse_args()
    chunks = construir()
    verificar_manual()
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto']}\n")
    for n, motivo in PENDIENTES_MANUAL.items():
        print(f"PENDIENTE (no se ingiere): {n} — {motivo}")
    print(f"{len(chunks)} chunks listos")
    if not args.upsert:
        print("dry-run: no se escribió nada")
        return
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    load_dotenv(base.PROJECT_ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    filas = []
    for c in chunks:
        for k, p in enumerate(_sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)):
            filas.append({**c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p, "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
