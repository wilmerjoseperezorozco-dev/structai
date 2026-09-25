"""
Ingesta verbatim de NSR-10 Título F.5.6.10 completo (Uniones Pegadas --
cierra F.5.6 completo, diseño estático de uniones de Estructuras de
Aluminio) y F.5.7.1 completo (Generalidades de Fatiga: influencia en el
diseño, mecanismo de falla, sitios potenciales de grietas, condiciones
de susceptibilidad). Fase 10 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-535 a F-538), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.6.10-1 (ensayo de corte con
capa gruesa de adhesivo) y F.5.6.10-2 (especímenes de ensayo de lámina
delgada) son dibujos de geometría de probetas de ensayo con cotas en mm
-- se documenta su propósito, no se transcriben las cotas dimensionales
completas del dibujo técnico.

Uso: python _ingest_titulo_f_f5610_f571_verbatim.py
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

CHUNKS = [
    {
        "id": "NSR10-F-F_5_6_10_1", "seccion": "F.5.6.10.1",
        "titulo": "F.5.6.10 — Uniones Pegadas: adhesivos requieren aval del Comité Permanente, apropiadas para cortante no tensión, soporte durante curado",
        "texto": (
            "F.5.6.10 — UNIONES PEGADAS. "
            "F.5.6.10.1 — Generalidades — Se pueden lograr uniones estructurales en aluminio utilizando "
            "adhesivos. El procedimiento requiere una técnica experta y debe ser usado con gran cuidado. Siempre "
            "se requerirá contar con el aval del Comité Permanente del Reglamento. "
            "Las uniones pegadas son apropiadas para soportar cargas de cortante pero no deben ser usadas a "
            "tensión o cuando la carga pueda causar descascaramiento u otras fuerzas que traten de abrir la "
            "unión. "
            "Las cargas deben estar soportadas por un área tan grande como sea posible. Incrementando el ancho de "
            "las uniones usualmente se incrementa la tasa pro-resistencia. Incrementar la longitud sólo es "
            "benéfico para traslapos muy cortos. "
            "El comportamiento de uniones pegadas grandes puede mejorarse reduciendo los esfuerzos por "
            "descascaramiento y separación en capas y reduciendo las concentraciones de esfuerzo en el extremo de "
            "los traslapos. Es útil redondear los extremos de los traslapos e introducir piezas de compensación. "
            "Las uniones pegadas deben tener soporte adicional después de ensambladas durante un período "
            "necesario para permitir el desarrollo de la resistencia óptima del adhesivo. Se deben evitar las "
            "bolsas de aire atrapado. "
            "Hay muchos adhesivos disponibles siendo, generalmente, cada uno apropiado para un solo rango "
            "específico de aplicaciones y condiciones de servicio. Las cualidades del adhesivo en todo lo que "
            "respecta a su uso en una estructura particular durante su vida, deben ser demostradas a satisfacción "
            "por el diseñador, quien debe asesorarse de especialistas durante todas las fases del diseño y la "
            "construcción. "
            "La especificación de un sistema de unión debe comprender la preparación de las superficies a "
            "adherir, el adhesivo, los procesos de aplicación y curado y debe ser seguida estrictamente ya que "
            "cualquier variación en cualquier paso puede afectar severamente el comportamiento de la unión."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_10_2", "seccion": "F.5.6.10.2",
        "titulo": "F.5.6.10.2 — Resistencia de diseño: 7 factores (a-g), ensayo a escala natural, resistencia PRG=φ(Rm-2Sd) con φ=0.3 (ec. F.5.6.10-1)",
        "texto": (
            "F.5.6.10.2 — Resistencia de diseño — La resistencia de diseño de una unión pegada está influenciada "
            "por los siguientes factores: "
            "(a) Los procedimientos de preparación de la superficie antes de pegar. "
            "(b) La dirección de los esfuerzos en la unión. "
            "(c) El tamaño y la forma de los componentes a unir. "
            "(d) El espesor de la línea de pegante. "
            "(e) Los procedimientos de ensamblaje y curado. "
            "(f) La temperatura y el ambiente de servicio. "
            "(g) La vida de diseño. "
            "A menos que se disponga de datos de ensayos válidos, la resistencia de la unión debe establecerse "
            "experimentalmente. Generalmente, se deben hacer uniones de muestra a escala natural usando los "
            "mismos procedimientos de fabricación empleados en las uniones reales. La prueba debe realizarse con "
            "una construcción similar de la unión y con una carga como la que soporta la estructura real. Se "
            "deben hacer, como mínimo, cinco ensayos para establecer la media y la desviación estándar de las "
            "cargas de falla. La resistencia de diseño de una unión pegada, PRG, está entonces dada por: "
            "PRG = φ(Rm - 2 Sd)  (F.5.6.10-1). "
            "Donde: Rm = media de las cargas de falla. Sd = desviación estándar de las cargas de falla. "
            "φ = coeficiente de reducción de capacidad para uniones pegadas (véase la tabla F.5.3.3-1), es igual "
            "a 0.3. "
            "El factor φ debe incrementarse con relación a la pérdida de calidad de desempeño del adhesivo en "
            "condiciones extremas de temperatura y ambiente de operación."
        ),
    },
    {
        "id": "NSR10-F-F_5_6_10_3", "seccion": "F.5.6.10.3",
        "titulo": "F.5.6.10.3 — Ensayos: datos del fabricante con probetas de corte de capa gruesa, Sd=0.1Rm si solo se citan resistencias medias (Figuras F.5.6.10-1/2, cierra F.5.6)",
        "texto": (
            "F.5.6.10.3 — Ensayos — Los datos de ensayos del fabricante pueden ser usados como los valores más "
            "optimistas para el diseño inicial. Generalmente, estos datos son dados para probetas de ensayo al "
            "corte unidas con una capa gruesa de adhesivo tal como se muestra en la figura F.5.6.10-1. Cuando "
            "sólo están citadas las resistencias medias, Sd debe tomarse como 0.1 Rm. "
            "Figura F.5.6.10-1 — Ensayo de corte con capa gruesa de adhesivo: probeta rectangular de aluminio "
            "(110 mm de longitud total, sección de ensayo de 25 mm, traslapo de 5 mm) con las fuerzas F aplicadas "
            "en direcciones opuestas. Todas las dimensiones en milímetros. Dibujo técnico con cotas, no se "
            "transcribe la geometría completa. "
            "Los ensayos con láminas delgadas traslapadas (como los descritos en la norma inglesa BS 5350: Parte "
            "C5) pueden usarse con el propósito de hacer comparaciones, estudios de durabilidad, determinar el "
            "tratamiento de la superficie, condiciones de curado, etc. Los valores de la resistencia serán bajos "
            "debido a la tendencia de esta unión a descascararse y serán conservadores si se usan para cálculos "
            "de diseño estructural (véase la figura F.5.6.10-2). "
            "Figura F.5.6.10-2 — Especímenes de ensayo de lámina delgada: (a) unión de traslapo simple, "
            "dimensiones de traslapo 12.5±0.5 mm, espesor 1.5 mm. (a) unión de traslapo doble, espesor 3.0 mm. "
            "(c) posición del agujero del pasador en los especímenes de unión: longitud 100±1.5 mm, un agujero "
            "de diámetro 5.99-6.00 mm, posiciones a 82.53-82.56 mm y separación 25.0±0.25 mm. Todas las "
            "dimensiones en milímetros. Dibujo técnico con cotas, no se transcribe la geometría completa."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_1_1", "seccion": "F.5.7.1",
        "titulo": "F.5.7 — Fatiga. F.5.7.1 — Generalidades: alcance (extrusiones/planchas/láminas), F.5.8 como alternativa de datos. F.5.7.1.1 — Influencia de la fatiga en el diseño (a-c)",
        "texto": (
            "F.5.7 — FATIGA. "
            "F.5.7.1 — GENERALIDADES — Esta sección contiene condiciones específicas para la valoración de la "
            "fatiga. Los datos se aplican a elementos formados con extrusiones, planchas, láminas delgadas y "
            "tiras, no deben usarse para piezas coladas o forjadas en caliente. Los diseñadores que deseen "
            "emplear piezas coladas o forjadas en caliente bajo condiciones de fatiga, deberán consultar con los "
            "fabricantes y seguir un procedimiento apropiado expedido por entidades de reconocida autoridad. "
            "Esta sección da recomendaciones para la evaluación analítica. Como los datos suministrados pueden no "
            "ser adecuados para todas las aplicaciones, en este caso, se pueden obtener datos adicionales "
            "mediante ensayos (véase F.5.8). Los datos obtenidos de acuerdo con F.5.8 pueden usarse sustituyendo "
            "los datos de diseño dados en F.5.7. "
            "F.5.7.1.1 — Influencia de la fatiga en el diseño — Las estructuras sujetas a cargas de servicio "
            "fluctuantes pueden resultar propensas a fallar por fatiga. El grado de cumplimiento con los "
            "criterios de estado límite estático dados en F.5.3 y F.5.4 puede no ser suficiente para controlar "
            "el riesgo de falla por fatiga. "
            "Es necesario establecer, tan pronto como sea posible, el límite para el cual la fatiga controla el "
            "diseño. Para hacer ésto, los siguientes factores son importantes: "
            "(a) Debe existir una predicción exacta de la secuencia de carga de servicio completa a lo largo de "
            "la vida de diseño. "
            "(b) Debe estimarse con exactitud la respuesta elástica de la estructura bajo esas cargas. "
            "(c) El diseño de detalles, los métodos de fabricación y el grado de control de calidad pueden tener "
            "una gran influencia en la resistencia a la fatiga y se deben definir con mayor precisión que como "
            "se requiere para miembros estáticamente controlados. Esto puede tener una influencia significativa "
            "sobre los costos de diseño y construcción."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_1_2", "seccion": "F.5.7.1.2",
        "titulo": "F.5.7.1.2 — Mecanismo de falla: inicio en concentración de esfuerzo, propagación proporcional al rango de esfuerzo³ y raíz de la longitud de grieta",
        "texto": (
            "F.5.7.1.2 — Mecanismo de falla — La falla por fatiga usualmente se inicia en un punto de alta "
            "concentración de esfuerzo, particularmente donde existen discontinuidades repentinas. Las grietas de "
            "fatiga se extienden incrementalmente bajo la acción del cambio cíclico de esfuerzos. Normalmente, "
            "permanecen estables bajo carga constante. La falla última ocurre cuando la sección transversal "
            "restante es insuficiente para soportar la carga pico de tensión aplicada en todas partes. "
            "Las grietas de fatiga se propagan, aproximadamente en ángulos rectos, en la dirección del rango "
            "máximo de esfuerzo principal. La tasa de propagación es proporcional a, por lo menos, la tercera "
            "potencia del producto del rango de esfuerzo y la raíz cuadrada de la longitud total de la grieta. "
            "Por esta razón, el crecimiento de las grietas es lento en las fases tempranas y las grietas por "
            "fatiga tienden a ser poco llamativas durante la mayor parte de su vida. Esto puede generar problemas "
            "para su detección durante el servicio."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_1_3", "seccion": "F.5.7.1.3",
        "titulo": "F.5.7.1.3 — Sitios potenciales para grietas de fatiga: bordes/raíces de soldadura, esquinas maquinadas, superficies de desgaste, raíces de roscas",
        "texto": "F.5.7.1.3 — Sitios potenciales para grietas de fatiga — Los sitios de inicio más comunes para grietas de fatiga son los siguientes: (a) Bordes y raíces de soldaduras de fusión. (b) Esquinas acabadas a máquina y agujeros taladrados. (c) Superficies bajo alta presión de contacto (desgaste). (d) Raíces de roscas de conectores.",
    },
    {
        "id": "NSR10-F-F_5_7_1_4", "seccion": "F.5.7.1.4",
        "titulo": "F.5.7.1.4 — Condiciones de susceptibilidad a la fatiga: relación carga dinámica/estática (a), frecuencia de carga (b), soldadura (c), complejidad de la unión (d), ambiente (e)",
        "texto": (
            "F.5.7.1.4 — Condiciones de susceptibilidad a la fatiga — Las principales condiciones que afectan el "
            "comportamiento ante fatiga son las siguientes: "
            "(a) Relación alta entre carga dinámica y carga estática — Las estructuras móviles o de levante, "
            "tales como vehículos de transporte terrestre o marino, grúas, etc., son más propensas a problemas de "
            "fatiga que las estructuras fijas, a menos que estas últimas soporten predominantemente cargas "
            "móviles, como en el caso de puentes. "
            "(b) Frecuentes aplicaciones de carga — Esto tiene como resultado un alto número de ciclos durante la "
            "vida de diseño. Las estructuras esbeltas y los miembros con bajas frecuencias naturales están "
            "particularmente predispuestos a resonancia y, por consiguiente, a magnificación del esfuerzo "
            "dinámico, aunque los esfuerzos estáticos de diseño son bajos. Las estructuras sometidas "
            "predominantemente a cargas de fluidos tales como el viento y las estructuras que soportan "
            "maquinaria, deben ser revisadas cuidadosamente para efectos de resonancia. "
            "(c) Uso de soldadura — Algunos detalles soldados comúnmente usados tienen baja resistencia a la "
            "fatiga. Esto es aplicable no sólo a uniones entre miembros sino también a cualquier accesorio de un "
            "miembro cargado, sea o no considerada la conexión resultante como estructural. "
            "(d) Complejidad del detalle de la unión — Las uniones complejas frecuentemente conllevan altas "
            "concentraciones de esfuerzos debidas a variaciones locales de rigidez en el camino de la carga. "
            "Mientras que ésto puede tener poco efecto en la capacidad estática última de la unión, puede tener "
            "un efecto severo en la resistencia a la fatiga. Si la fatiga es dominante, la forma de la sección "
            "transversal del miembro debe ser seleccionada para asegurar la uniformidad y simplicidad del diseño "
            "de la unión de modo que los esfuerzos puedan ser calculados y se puedan asegurar las normas "
            "adecuadas de fabricación e inspección. "
            "(e) Ambiente — En ciertos ambientes térmicos y químicos, puede haber reducción de la resistencia a "
            "la fatiga."
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
