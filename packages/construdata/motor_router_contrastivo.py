"""
Enrutador contrastivo de dominio -- alternativa matemática a _score_motores()
(coincidencia de subcadena contra ~200 palabras clave por dominio, con un
peso arbitrario por longitud de palabra). Misma idea de fondo que CLM-8B
(Stanford/NVIDIA, publicado 2026-09-23): codificar la pregunta y comparar
por similitud en un espacio de embeddings contra representaciones
pre-calculadas de cada "acción" disponible (aquí, cada dominio), en vez de
generar texto o hacer coincidencia léxica para decidir.

Diferencia deliberada con CLM-8B: no se adopta el modelo completo (backbone
Qwen3-8B congelado, ~16GB de VRAM) porque el problema real de StructAI es
una clasificación de 9 categorías, no un espacio de acciones agéntico
abierto -- sería GPU nueva para resolver un problema mucho más pequeño.
Se reutiliza el modelo de embeddings YA cargado en producción
(paraphrase-multilingual-MiniLM-L12-v2, vía _embedding_model() de
rag_multi_norma.py), sin costo de infraestructura adicional.

Método: por cada dominio se define un pequeño conjunto de preguntas de
ejemplo reales y representativas (EJEMPLOS_POR_DOMINIO). Se codifican una
sola vez y se cachea el centroide (promedio normalizado) por dominio --
el equivalente al "caching de acciones reutilizables" de CLM. En
inferencia, se codifica la pregunta entrante y se compara por similitud
coseno (producto punto, porque embed_query() ya normaliza) contra cada
centroide.

Los ejemplos de este archivo están escritos deliberadamente con frases
DISTINTAS a las de apps/api/tests/test_rag_motores_regresion.py, para que
ese archivo sirva como conjunto de prueba honesto (sin fuga de datos) al
comparar este enrutador contra _score_motores() -- ver
scripts/evaluacion/comparar_enrutador_keyword_vs_contrastivo.py.

Uso:
    from motor_router_contrastivo import route_motores_contrastivo
    route_motores_contrastivo("cuanto cuesta el saco de cemento en Barranquilla?")
    # -> [("apu_precios", 0.71), ("geopot", 0.42), ...]
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from rag_multi_norma import embed_query

# Igual que MOTOR_KEYWORD_MAP en rag_multi_norma.py, más el dominio implícito
# "normativa_general" (NSR-10/NTC/SGSST) que allí nunca se declara -- es el
# resultado de que _score_motores() no encuentre ninguna palabra clave. Aquí
# SÍ necesita ejemplos propios porque el clasificador contrastivo siempre
# elige el dominio más cercano, nunca "ninguno".
EJEMPLOS_POR_DOMINIO: dict[str, list[str]] = {
    "aquai": [
        "cual es el diametro minimo de una tuberia de alcantarillado sanitario",
        "como se calcula el caudal de diseño para una red de acueducto",
        "que velocidad minima debe tener el flujo en un colector de aguas residuales",
        "cual es el periodo de diseño recomendado para una planta de tratamiento de agua potable",
        "que formula se usa para el golpe de ariete en tuberias a presion",
        "cuales son los parametros de calidad del agua potable segun la resolucion 0330",
        "como se dimensiona un tanque de almacenamiento de agua para una poblacion",
        "que es la dotacion bruta y como se calcula",
        "cual es la profundidad minima de instalacion de una tuberia de acueducto",
        "que criterios exige la CRA para la prestacion del servicio de alcantarillado",
    ],
    "geopot": [
        "como se clasifica un suelo segun el sistema unificado de clasificacion de suelos",
        "que ensayo de laboratorio se usa para determinar el limite liquido de un suelo",
        "cual es la resistencia minima a la compresion de un cilindro de concreto a los 28 dias",
        "como se calcula la capacidad portante admisible de una cimentacion superficial",
        "que es el ensayo proctor modificado y para que sirve",
        "cual es el valor tipico de CBR para una subrasante buena",
        "como se determina la microzonificacion sismica de una ciudad",
        "que factores intervienen en el analisis de estabilidad de un talud",
        "cual es la granulometria requerida para un agregado grueso de concreto",
        "que estudios basicos de amenaza exige el ordenamiento territorial",
    ],
    "vulnerabilidad_vivienda": [
        "mi casa de un piso en mamposteria es segura ante un sismo fuerte",
        "como se hace una evaluacion visual rapida de vulnerabilidad sismica",
        "que columnas de confinamiento necesita una vivienda de dos pisos",
        "cual es el checklist para evaluar si una casa antigua resiste un terremoto",
        "que diferencia hay entre mamposteria confinada y mamposteria no reforzada",
        "como se evalua la vulnerabilidad sismica de una vivienda autoconstruida",
        "que dice el titulo E de la NSR-10 sobre viviendas de uno y dos pisos",
        "cuales son las señales de que una casa de mamposteria puede colapsar en un sismo",
    ],
    "vias": [
        "cual es el radio minimo de curvatura para una via terciaria",
        "como se calcula el numero estructural de un pavimento flexible",
        "que espesor de losa se requiere para un pavimento rigido de concreto",
        "cuales son los tipos de falla mas comunes en un pavimento asfaltico",
        "que pendiente longitudinal maxima permite el manual de diseño geometrico de INVIAS",
        "como se determina el transito de diseño para dimensionar un pavimento",
        "que es el indice de condicion del pavimento y como se mide",
        "cual es el procedimiento de diseño de un tunel vial segun el macizo rocoso",
        "que normas de ensayo INVIAS se usan para caracterizar un agregado",
        "como se calcula el peralte de una curva horizontal en una carretera",
    ],
    "apu_precios": [
        "cuanto cuesta un metro cubico de concreto en Barranquilla",
        "cual es el precio actual del hierro de refuerzo por kilogramo",
        "donde consigo un proveedor de cemento con buen precio en el Atlantico",
        "cual es el valor de la mano de obra para pañete en una obra",
        "necesito el analisis de precios unitarios para una excavacion manual",
        "cuanto vale la varilla de 1/2 pulgada hoy en dia",
        "cual es el costo por metro cuadrado de instalar piso ceramico",
        "que proveedores de ferreteria tienen el mejor precio de bloque de concreto",
    ],
    "gerencia": [
        "como se calcula el indice de desempeño de costo en un proyecto de construccion",
        "que significa que el CPI de un proyecto sea menor a uno",
        "cual es la formula del valor planificado en la gestion de valor ganado",
        "como se hace una licitacion publica bajo la ley 80 de contratacion estatal",
        "que funciones tiene el interventor de un contrato de obra publica",
        "cuales son las causales de caducidad de un contrato estatal",
        "como se proyecta la fecha de terminacion de un proyecto usando regresion lineal",
        "que es el pliego de condiciones en un proceso de seleccion abreviada",
        "cual es la diferencia entre supervision e interventoria de un contrato",
        "como se interpreta una curva S de avance de obra",
    ],
    "peru_e030": [
        "que factor de zona sismica aplica en Lima segun la norma E.030",
        "cuales son los requisitos sismorresistentes para edificaciones en Peru",
        "que dice el reglamento nacional de edificaciones del Peru sobre el diseño sismico",
        "cual es la categoria de uso de un hospital segun la norma peruana E.030",
        "que exige el MVCS peruano para la clasificacion de suelos sismicos",
    ],
    "ecuador_nec_se_ds": [
        "cual es el coeficiente de zona sismica para Quito segun la NEC-SE-DS",
        "que requisitos sismorresistentes exige la norma ecuatoriana de la construccion",
        "que dice el MIDUVI sobre el diseño sismico de edificaciones en Ecuador",
        "cual es la categoria de importancia de un colegio segun la norma ecuatoriana",
        "que establece el codigo ingenios para estructuras en zona sismica del Ecuador",
    ],
    "normativa_general": [
        "cual es la deriva maxima permitida para una estructura de concreto segun la NSR-10",
        "que espaciamiento de estribos exige el titulo C para vigas sismorresistentes",
        "cuales son los requisitos de refuerzo minimo en un muro de mamposteria estructural",
        "que dice el titulo A de la NSR-10 sobre las zonas de amenaza sismica en Colombia",
        "cual es el recubrimiento minimo del concreto reforzado expuesto al suelo",
        "que elementos deben tener resistencia al fuego segun el titulo J de la NSR-10",
        "cuales son las obligaciones del empleador segun el decreto 1072 de 2015",
        "que exige la NTC sobre la instalacion de extintores en una edificacion",
        "cual es el procedimiento de supervision tecnica obligatoria segun el titulo I",
        "que capitulo de la NSR-10 regula el diseño de cimentaciones",
        "que dice la ley 1562 de 2012 sobre el sistema de riesgos laborales",
        "cuales son los requisitos minimos de un estudio geotecnico segun el titulo H",
    ],
}


@lru_cache(maxsize=1)
def _centroides() -> dict[str, np.ndarray]:
    """Codifica todos los ejemplos una sola vez y cachea el centroide
    (promedio de embeddings, re-normalizado) por dominio -- el "caching de
    acciones reutilizables" de CLM, aplicado a los 9 dominios de StructAI."""
    centroides: dict[str, np.ndarray] = {}
    for dominio, ejemplos in EJEMPLOS_POR_DOMINIO.items():
        vectores = np.array([embed_query(ej) for ej in ejemplos])
        centroide = vectores.mean(axis=0)
        norma = np.linalg.norm(centroide)
        centroides[dominio] = centroide / norma if norma > 0 else centroide
    return centroides


def route_motores_contrastivo(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    """Devuelve hasta top_k dominios ordenados por similitud coseno
    descendente, como [(dominio, score), ...]. embed_query() ya normaliza,
    así que la similitud coseno es simplemente el producto punto."""
    vector_query = np.array(embed_query(query))
    centroides = _centroides()
    similitudes = [(dominio, float(np.dot(vector_query, c))) for dominio, c in centroides.items()]
    similitudes.sort(key=lambda x: -x[1])
    return similitudes[:top_k]


def route_motor_contrastivo(query: str) -> str:
    """Solo el dominio más probable -- equivalente contrastivo de route_motor()."""
    return route_motores_contrastivo(query, top_k=1)[0][0]
