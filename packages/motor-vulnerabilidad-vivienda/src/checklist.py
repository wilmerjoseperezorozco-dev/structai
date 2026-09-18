"""
Motor de evaluación de vulnerabilidad sísmica de vivienda de mampostería
(1-2 pisos) — Fase 1 (checklist determinístico, sin fotos, sin ML) del
issue #51 de GitHub.

Fuente real, no adaptada: "Manual de Construcción, Evaluación y
Rehabilitación Sismo Resistente de Viviendas de Mampostería" (Asociación
Colombiana de Ingeniería Sísmica -AIS-, con apoyo del Fondo para la
Reconstrucción y Desarrollo Social del Eje Cafetero -FOREC- y la Dirección
para la Prevención y Atención de Emergencias -DPAE- de Bogotá, 2004),
Capítulo II "Evaluación del grado de vulnerabilidad sísmica de viviendas"
(págs. 2-1 a 2-23). Autores: Luis Eduardo Yamín, Omar Darío Cardona,
Shirly Merlano y Carlos Blandón (CEDERI, Universidad de los Andes), con
aportes de la Asociación de Ingenieros Estructurales de Antioquia.

Es un método de evaluación visual rápida (mismo espíritu que FEMA P-154
Rapid Visual Screening) pero calibrado desde el inicio con tipologías
constructivas colombianas reales (mampostería no reforzada/confinada/
reforzada) y con la experiencia real del terremoto del Eje Cafetero de
1999 — NO una traducción de los coeficientes "Basic Score" de FEMA P-154
(esos están calibrados para tipologías de EEUU; ver la investigación
completa en el issue #51 de GitHub sobre por qué se descartó esa ruta).

LÍMITE HONESTO:
- Clasifica en 3 niveles (BAJA / MEDIA / ALTA), no en 5 clases A-E.
- Aplica a vivienda de mampostería (no reforzada, confinada o reforzada)
  de 1-2 pisos — mismo alcance que el Título E de la NSR-10.
- Es una evaluación VISUAL, respondida por quien inspecciona la vivienda
  comparando lo que observa contra las 3 descripciones de cada criterio.
  No sustituye una evaluación estructural formal con cálculo (para eso
  existe el documento más riguroso AIS 410-23, que exige aceleración
  espectral y modelo estructural real — fuera del alcance de este v0).
- El criterio "cantidad de muros en las dos direcciones" referencia una
  fórmula real del manual (Lo = Mo × Ap / t, con Mo tabulado en el
  Capítulo I del mismo manual AIS) para decidir baja/media/alta -- este
  v0 no calcula Lo automáticamente (requeriría portar la tabla Mo del
  Capítulo I, fuera de alcance de esta fase); quien evalúa aplica la
  fórmula a mano o hace el juicio visual comparativo que el propio
  manual permite como alternativa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum


class NivelCriterio(IntEnum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3


@dataclass(frozen=True)
class Criterio:
    id: str
    aspecto: str
    nombre: str
    descripcion_baja: str
    descripcion_media: str
    descripcion_alta: str


CRITERIOS: tuple[Criterio, ...] = (
    Criterio(
        id="irregularidad_planta",
        aspecto="geometricos",
        nombre="Irregularidad en planta de la edificación",
        descripcion_baja="Forma geométrica regular y aproximadamente simétrica; largo menor que 3 veces el ancho; sin entradas y salidas abruptas en planta ni en altura.",
        descripcion_media="Presenta algunas irregularidades en planta o en altura, no muy pronunciadas.",
        descripcion_alta="El largo es mayor que 3 veces el ancho, o la forma es irregular con entradas y salidas abruptas.",
    ),
    Criterio(
        id="cantidad_muros_dos_direcciones",
        aspecto="geometricos",
        nombre="Cantidad de muros en las dos direcciones",
        descripcion_baja="Existen muros estructurales confinados o reforzados en las dos direcciones principales, con longitud total en cada dirección al menos igual a la calculada con Lo = Mo × Ap / t (Mo según tabla del Capítulo I del manual AIS; Ap = área en planta; t = espesor de muros).",
        descripcion_media="La mayoría de los muros se concentran en una sola dirección, aunque existen uno o varios en la otra; la longitud en la dirección de menor cantidad es ligeramente inferior a la calculada con la fórmula.",
        descripcion_alta="Más del 70% de los muros están en una sola dirección, hay muy pocos muros confinados o reforzados, y la longitud total de muros estructurales en cualquier dirección es mucho menor que la calculada.",
    ),
    Criterio(
        id="irregularidad_altura",
        aspecto="geometricos",
        nombre="Irregularidad en altura",
        descripcion_baja="La mayoría de los muros estructurales son continuos desde la cimentación hasta la cubierta.",
        descripcion_media="Algunos muros presentan discontinuidades desde la cimentación hasta la cubierta.",
        descripcion_alta="La mayoría de los muros no son continuos en altura desde la cimentación, con cambios de alineación en el sistema de muros o cambio a columnas en el piso inferior.",
    ),
    Criterio(
        id="calidad_juntas_pega",
        aspecto="constructivos",
        nombre="Calidad de las juntas de pega en mortero",
        descripcion_baja="El espesor de la mayoría de las pegas está entre 0.7 y 1.3 cm; juntas uniformes y continuas, de buena calidad tanto verticales como horizontales; buena adherencia del mortero con la mampostería.",
        descripcion_media="El espesor de la mayoría de las pegas es mayor a 1.3 cm o menor de 0.7 cm; las juntas no son uniformes.",
        descripcion_alta="La pega es muy pobre entre los bloques, casi inexistente; poca regularidad en la alineación de las piezas; no existen juntas verticales y/o horizontales en zonas del muro.",
    ),
    Criterio(
        id="tipo_disposicion_unidades",
        aspecto="constructivos",
        nombre="Tipo y disposición de las unidades de mampostería",
        descripcion_baja="Las unidades de mampostería están trabadas, son de buena calidad (sin agrietamientos importantes ni piezas deterioradas o rotas), colocadas de manera uniforme y continua hilada tras hilada.",
        descripcion_media="Algunas piezas están trabadas y otras no, siendo la mayoría de la primera clase; algunas presentan agrietamiento o deterioro.",
        descripcion_alta="Las unidades de mampostería NO están trabadas (petaca); son de muy mala calidad, con agrietamientos importantes, piezas deterioradas o rotas, y no están colocadas de manera uniforme.",
    ),
    Criterio(
        id="calidad_materiales",
        aspecto="constructivos",
        nombre="Calidad de los materiales",
        descripcion_baja="El mortero no se raya ni desmorona con un clavo o herramienta metálica; el concreto tiene buen aspecto (sin hormigueros, sin acero expuesto); en los elementos de confinamiento hay estribos abundantes y al menos 3-4 barras No. 3 longitudinales; el ladrillo es de buena calidad y resiste caídas de al menos 2 m sin desintegrarse.",
        descripcion_media="Se cumplen varios de los requisitos anteriores, pero no todos.",
        descripcion_alta="No se cumplen más de dos de los requisitos anteriores.",
    ),
    Criterio(
        id="muros_confinados_reforzados",
        aspecto="estructurales",
        nombre="Muros confinados y reforzados",
        descripcion_baja="Todos los muros de mampostería de la vivienda están confinados con vigas y columnas de concreto reforzado alrededor; el espaciamiento máximo entre elementos de confinamiento es del orden de 4 m o la altura entre pisos; todos los elementos de confinamiento tienen refuerzo longitudinal y transversal adecuadamente dispuesto; las culatas y antepechos también están confinados.",
        descripcion_media="Algunos muros de la edificación no cumplen con los requisitos anteriores.",
        descripcion_alta="La mayoría de los muros de mampostería de la vivienda no tienen confinamiento mediante columnas y vigas de concreto reforzado.",
    ),
    Criterio(
        id="detalles_columnas_vigas_confinamiento",
        aspecto="estructurales",
        nombre="Detalles de columnas y vigas de confinamiento",
        descripcion_baja="Las columnas y vigas tienen más de 20 cm de espesor o más de 400 cm² de área transversal; tienen al menos 4 barras No. 3 longitudinales y estribos espaciados a no más de 10-15 cm; existe buen contacto entre el muro de mampostería y los elementos de confinamiento; el refuerzo longitudinal está adecuadamente anclado en sus extremos y a los elementos de la cimentación.",
        descripcion_media="No todas las columnas y vigas cumplen con los requisitos anteriores.",
        descripcion_alta="La mayoría de las columnas y vigas de confinamiento no cumplen con los requisitos establecidos anteriormente.",
    ),
    Criterio(
        id="vigas_amarre_corona",
        aspecto="estructurales",
        nombre="Vigas de amarre o corona",
        descripcion_baja="Existen vigas de amarre o de corona en concreto reforzado en todos los muros, parapetos, fachadas y culatas en mampostería.",
        descripcion_media="No todos los muros o elementos de mampostería disponen de vigas de amarre o de corona.",
        descripcion_alta="La vivienda no dispone de vigas de amarre o corona en los muros o elementos de mampostería.",
    ),
    Criterio(
        id="caracteristicas_aberturas",
        aspecto="estructurales",
        nombre="Características de las aberturas",
        descripcion_baja="Las aberturas en los muros estructurales totalizan menos del 35% del área total del muro; la longitud total de aberturas corresponde a menos de la mitad de la longitud total del muro; existe una distancia desde el borde del muro hasta la abertura adyacente igual a la altura de la misma o 50 cm, la que sea mayor.",
        descripcion_media="No se cumplen algunos de los requisitos anteriores en algunos de los muros de la vivienda.",
        descripcion_alta="Muy pocos o ningún muro estructural de la vivienda cumple con los requisitos anteriores.",
    ),
    Criterio(
        id="entrepiso",
        aspecto="estructurales",
        nombre="Entrepiso",
        descripcion_baja="El entrepiso está conformado por placas de concreto fundidas en el sitio o placas prefabricadas que funcionan de manera monolítica; la placa se apoya de manera adecuada a los muros de soporte y proporciona continuidad y monolitismo; es continua, monolítica y uniforme en relación con los materiales que la componen.",
        descripcion_media="La placa de entrepiso no cumple con alguna de las condiciones anteriores.",
        descripcion_alta="La placa no cumple con varias de las condiciones anteriores; los entrepisos están conformados por madera o combinaciones de materiales (guadua, mortero, madera, concreto) que no proporcionan las características de continuidad y amarre deseados.",
    ),
    Criterio(
        id="amarre_cubiertas",
        aspecto="estructurales",
        nombre="Amarre de cubiertas",
        descripcion_baja="Existen tornillos, alambres o conexiones similares que amarran el techo a los muros; hay arriostramiento de las vigas y la distancia entre ellas no es muy grande; la cubierta es liviana y está debidamente amarrada y apoyada a la estructura.",
        descripcion_media="Algunos de los requisitos anteriores se cumplen.",
        descripcion_alta="La mayoría de los requisitos anteriores no se cumplen; la cubierta es pesada y no está debidamente soportada o arriostrada.",
    ),
    Criterio(
        id="cimentacion",
        aspecto="cimentacion",
        nombre="Cimentación",
        descripcion_baja="La cimentación está conformada por vigas corridas en concreto reforzado bajo los muros estructurales; las vigas de cimentación conforman anillos amarrados/cerrados.",
        descripcion_media="La cimentación no está debidamente amarrada; no se cumplen algunos de los requisitos anteriores.",
        descripcion_alta="La edificación no cuenta con una cimentación adecuada de acuerdo con los requerimientos anteriores.",
    ),
    Criterio(
        id="suelos",
        aspecto="suelos",
        nombre="Suelos",
        descripcion_baja="El suelo de la fundación es duro: no existen hundimientos ni árboles o postes inclinados alrededor, no se siente vibración cuando pasa un vehículo pesado cerca, y las viviendas de la zona no presentan agrietamientos o daños generalizados.",
        descripcion_media="El suelo de la fundación es de mediana resistencia; se pueden presentar algunos hundimientos y vibraciones por el paso de vehículos pesados, con algunos daños generalizados menores o pequeñas manifestaciones de hundimiento.",
        descripcion_alta="El suelo de la fundación es blando o arena suelta; se sabe por hundimiento en zonas vecinas, se siente vibración al paso de vehículos pesados, la vivienda ha presentado asentamientos considerables, y la mayoría de las viviendas de la zona presentan agrietamientos y/o hundimientos.",
    ),
    Criterio(
        id="entorno",
        aspecto="entorno",
        nombre="Entorno (topografía)",
        descripcion_baja="La topografía donde se encuentra la vivienda es plana o muy poco inclinada (ángulo menor a 20° con la horizontal).",
        descripcion_media="La topografía donde se encuentra la vivienda tiene un ángulo entre 20° y 30° de inclinación con la horizontal.",
        descripcion_alta="La vivienda se encuentra localizada en una pendiente con una inclinación mayor de 30° con la horizontal.",
    ),
)

CRITERIOS_POR_ID: dict[str, Criterio] = {c.id: c for c in CRITERIOS}

# Pesos reales tal como los publica el manual AIS (tabla "RESUMEN", pág. 2-22).
ASPECTOS_ORDEN: tuple[str, ...] = (
    "geometricos",
    "constructivos",
    "estructurales",
    "cimentacion",
    "suelos",
    "entorno",
)

PESO_ASPECTO: dict[str, float] = {
    "geometricos": 0.20,
    "constructivos": 0.20,
    "estructurales": 0.30,
    "cimentacion": 0.10,
    "suelos": 0.10,
    "entorno": 0.10,
}

ASPECTO_LABEL: dict[str, str] = {
    "geometricos": "Aspectos geométricos",
    "constructivos": "Aspectos constructivos",
    "estructurales": "Aspectos estructurales",
    "cimentacion": "Cimentación",
    "suelos": "Suelos",
    "entorno": "Entorno",
}


@dataclass(frozen=True)
class ResultadoAspecto:
    aspecto: str
    calificacion_promedio: float
    calificacion: int
    peso: float
    ponderada: float


@dataclass(frozen=True)
class ResultadoVulnerabilidad:
    calificacion_global: float
    clasificacion: str  # "BAJA" | "MEDIA" | "ALTA"
    aspectos: tuple[ResultadoAspecto, ...]
    criterios_evaluados: dict[str, int]


def _redondear_a_nivel(valor: float) -> int:
    """Redondea "mitad hacia arriba" (1.5 -> 2, 2.5 -> 3) al entero más
    cercano dentro de la escala 1-3 -- en vez del round() nativo de
    Python, que redondea al par más cercano (banker's rounding) y daría
    resultados no intuitivos en los casos límite.

    El manual AIS redondea así la calificación promedio de CADA ASPECTO
    a un nivel entero (1/2/3) ANTES de multiplicarla por su peso -- ver
    el ejemplo resuelto del manual (Capítulo II, pág. 2-23): el promedio
    de "aspectos estructurales" es (3+2+3+2+3+3)/6 = 2.67, y el manual
    lo redondea a 3 antes de aplicar el 30% de peso (3×0.3=0.9), no usa
    2.67 directo (2.67×0.3=0.801 no reproduciría el resultado publicado
    de 2.1 en la calificación global). Esta misma función se reusa para
    redondear la calificación global final a BAJA/MEDIA/ALTA.
    """
    nivel = math.floor(valor + 0.5)
    return max(1, min(3, nivel))


def _clasificar(calificacion_global: float) -> str:
    """Mapea la calificación global (ya redondeada a nivel 1/2/3 con
    _redondear_a_nivel) a BAJA/MEDIA/ALTA. Reproduce fielmente el
    ejemplo resuelto del manual AIS (calificación 2.1 -> MEDIA, pág.
    2-23)."""
    nivel = _redondear_a_nivel(calificacion_global)
    return {1: "BAJA", 2: "MEDIA", 3: "ALTA"}[nivel]


def evaluar_vulnerabilidad(respuestas: dict[str, int]) -> ResultadoVulnerabilidad:
    """Calcula la vulnerabilidad sísmica ponderada de una vivienda de
    mampostería de 1-2 pisos a partir de las 15 respuestas del checklist
    AIS (cada una calificada 1=baja, 2=media o 3=alta).

    Lanza ValueError si faltan criterios, sobran criterios no reconocidos,
    o algún valor no está en {1, 2, 3}.
    """
    ids_esperados = set(CRITERIOS_POR_ID)
    ids_recibidos = set(respuestas)

    faltantes = ids_esperados - ids_recibidos
    if faltantes:
        raise ValueError(f"Faltan respuestas para los criterios: {sorted(faltantes)}")

    desconocidos = ids_recibidos - ids_esperados
    if desconocidos:
        raise ValueError(f"Criterios no reconocidos: {sorted(desconocidos)}")

    for criterio_id, nivel in respuestas.items():
        if nivel not in (1, 2, 3):
            raise ValueError(
                f"El criterio '{criterio_id}' debe calificarse 1 (baja), "
                f"2 (media) o 3 (alta); recibido: {nivel!r}"
            )

    aspectos_resultado: list[ResultadoAspecto] = []
    calificacion_global = 0.0

    for aspecto in ASPECTOS_ORDEN:
        ids_del_aspecto = [c.id for c in CRITERIOS if c.aspecto == aspecto]
        valores = [respuestas[cid] for cid in ids_del_aspecto]
        promedio = sum(valores) / len(valores)
        calificacion_redondeada = _redondear_a_nivel(promedio)
        peso = PESO_ASPECTO[aspecto]
        ponderada = calificacion_redondeada * peso
        calificacion_global += ponderada
        aspectos_resultado.append(
            ResultadoAspecto(
                aspecto=aspecto,
                calificacion_promedio=round(promedio, 2),
                calificacion=calificacion_redondeada,
                peso=peso,
                ponderada=round(ponderada, 3),
            )
        )

    return ResultadoVulnerabilidad(
        calificacion_global=round(calificacion_global, 2),
        clasificacion=_clasificar(calificacion_global),
        aspectos=tuple(aspectos_resultado),
        criterios_evaluados=dict(respuestas),
    )


def listar_criterios() -> list[dict]:
    """Devuelve el checklist completo (15 criterios con sus 3 descripciones
    cada uno) para que un frontend/formulario lo renderice sin tener que
    duplicar el texto del manual en otra parte del código."""
    return [
        {
            "id": c.id,
            "aspecto": c.aspecto,
            "aspecto_label": ASPECTO_LABEL[c.aspecto],
            "nombre": c.nombre,
            "descripciones": {
                "baja": c.descripcion_baja,
                "media": c.descripcion_media,
                "alta": c.descripcion_alta,
            },
        }
        for c in CRITERIOS
    ]
