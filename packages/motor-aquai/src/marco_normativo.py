"""
AquaAI — Marco normativo centralizado
Registro de las reglas de la Resolución 0330/2017 que el motor verifica, con fuente, artículo y vigencia.

FUENTE DE LA NUMERACIÓN: texto consolidado del Gestor Normativo de la CRA (259 artículos, con las modificaciones y
correcciones de las Resoluciones 799 y 908 de 2021 marcadas en el propio texto), copia en
scripts/ingesta/ras_audit/res0330_2017.txt (descargada 2026-08-08).
ATENCIÓN: el texto indexado para el RAG (packages/construdata/normativa_raw/res0330/res0330.txt, 255 artículos) es anterior a esas
modificaciones y numera distinto (p. ej. SUDS es el Art. 151 allí y el Art. 153 aquí; derogatoria Art. 255 allí y Art. 258 aquí).
Un valor sin verificar en texto no entra al registro: va en NO_VERIFICADO.
"""
from __future__ import annotations

from dataclasses import dataclass

FUENTE = "Resolución 0330 de 2017 (MVCT), texto consolidado del Gestor Normativo de la CRA"


@dataclass(frozen=True)
class Regla:
    id: str
    fuente: str
    articulo: str
    tema: str
    enunciado: str
    valor: float | None = None
    unidad: str = ""


REGLAS: dict[str, Regla] = {r.id: r for r in (
    Regla("racional_area_max", FUENTE, "Art. 135", "método racional",
          "El método racional puede usarse siempre que el área de drenaje sea inferior a 80 ha (colectores y canales de aguas lluvias).", 80.0, "ha"),
    Regla("tc_minimo_sensibilidad", FUENTE, "Art. 135", "tiempo de concentración",
          "Se debe realizar una simulación para tiempos de concentración mínimos entre 3 y 10 minutos y evaluar la incidencia de adoptar uno u otro valor.", None, "min"),
    Regla("periodo_retorno_minimo", FUENTE, "Art. 135, Tabla 16", "período de retorno",
          "El período de retorno de la lluvia de diseño no puede ser menor que los valores de la Tabla 16."),
    Regla("velocidad_max_colector", FUENTE, "Arts. 142 y 150", "velocidad máxima",
          "La velocidad máxima real en un colector por gravedad no debe sobrepasar 5,0 m/s para el caudal de diseño (Art. 142 sanitarios; Art. 150 pluviales y combinados).", 5.0, "m/s"),
    Regla("velocidad_excepcion", FUENTE, "Arts. 142 y 150, parágrafo", "excepción por pendiente fuerte",
          "Con topografías de pendiente superior al 30 %, colectores de diámetro igual o superior a 600 mm o caudales superiores a 500 L/s se permiten velocidades mayores a 5 m/s, "
          "sin sobrepasar los límites del material ni 10 m/s; las tuberías con más de 5 m/s requieren revestimientos internos especiales contra la abrasión, protecciones y disipación de energía.", 0.30, "m/m"),
    Regla("velocidad_tope_absoluto", FUENTE, "Arts. 142 y 150, parágrafo", "tope absoluto de velocidad",
          "Aun con excepción, la velocidad no debe superar 10 m/s.", 10.0, "m/s"),
    Regla("suds_reduccion_pico", FUENTE, "Art. 153 (modificado por Res. 799/2021, Art. 44)", "drenaje sostenible",
          "En nuevos desarrollos se debe evaluar la viabilidad de SUDS; de ser viable, su diseño debe reducir el pico del hidrograma de la creciente de diseño en no menos de 30 %.", 30.0, "%"),
    Regla("camara_caida_desnivel", FUENTE, "Art. 155", "cámara de caída",
          "El colector que llegue a una estructura de conexión con diferencia de cotas batea mayor a 0,75 m respecto del colector de salida debe entregar mediante cámara de caída.", 0.75, "m"),
    Regla("disipacion_desnivel", FUENTE, "Art. 155", "disipación de energía",
          "Para desniveles mayores a 7,0 m se deben diseñar estructuras de disipación de energía.", 7.0, "m"),
    Regla("descarga_disipacion", FUENTE, "Art. 159", "descarga a cuerpos de agua",
          "Las redes que descargan a canales, cuerpos de agua o a cielo abierto requieren estructura de descarga estable y disipación que lleve el flujo a régimen subcrítico."),
)}

DEROGATORIA = Regla("derogatoria_ras2000", FUENTE, "Art. 258", "vigencia",
                    "Deroga las resoluciones 1096 de 2000 (RAS 2000), 0424 de 2001, 0668 de 2003, 1459 de 2005, 1447 de 2005 y 2320 de 2009.")

# Tabla 16 (Art. 135): tipo de tramo -> período de retorno mínimo (años). Transcrita del texto consolidado.
TABLA_16: dict[str, tuple[str, int]] = {
    "residencial_inicial_menor_2ha": ("Tramos iniciales en zonas residenciales con áreas tributarias menores de 2 hectáreas", 3),
    "comercial_industrial_inicial_menor_2ha": ("Tramos iniciales en zonas comerciales o industriales, con áreas tributarias menores de 2 hectáreas", 5),
    "alcantarillado_2_a_10ha": ("Tramos de alcantarillado con áreas tributarias entre 2 y 10 hectáreas", 5),
    "alcantarillado_mayor_10ha": ("Tramos de alcantarillado con áreas tributarias mayores de 10 hectáreas", 10),
    "canal_menor_1000ha": ("Canales abiertos que drenan áreas menores a 1000 hectáreas", 50),
    "canal_plano_mayor_1000ha": ("Canales abiertos en zonas planas y que drenan áreas mayores a 1000 hectáreas", 100),
    "canal_montanoso_mayor_1000ha": ("Canales abiertos en zonas montañosas (alta velocidad) o a media ladera, que drenan áreas mayores a 1000 hectáreas", 100),
}

# Tabla 20 (Art. 155): diámetro interno real de la tubería de entrada (hasta, mm) -> diámetro interno real mínimo de la tubería de la cámara (mm).
TABLA_20: tuple[tuple[float, float], ...] = ((300.0, 170.0), (450.0, 280.0), (900.0, 360.0))

# Cadena de vigencia verificada el 2026-11-08 en la página del Ministerio de Vivienda (Reglamento Técnico RAS).
HISTORIAL = (
    ("Res. 0330 de 2017 (8-jun-2017)", "adopta el RAS; deroga las Res. 1096/2000, 0424/2001, 0668/2003, 1459/2005 y 2320/2009"),
    ("Res. 0650 de 2017 (2-oct-2017)", "adiciona un artículo transitorio a la 0330"),
    ("Res. 0799 de 2021 (9-dic-2021)", "modifica la 0330; vigente desde el 21-dic-2021"),
    ("Res. 0908 de 2021 (17-dic-2021)", "corrige errores formales de la 0799"),
    ("Res. 0548 de 2022 (26-jul-2022)", "adiciona un artículo transitorio a la 0799"),
)

# Valores o referencias que el motor menciona pero que NO se verificaron en el texto.
NO_VERIFICADO = (
    "Modificaciones posteriores a julio de 2022: la página oficial del Ministerio de Vivienda (consultada 2026-11-08) no lista ningún instrumento posterior a la Res. 0548 de 2022; no se hizo una búsqueda exhaustiva en el Diario Oficial, así que la ausencia no está demostrada.",
    "Régimen de transición: la Res. 0548 de 2022 (art. transitorio de la Res. 799 de 2021) permite reformular, sin las disposiciones modificatorias de la 799, proyectos en preinversión diseñados bajo la 0330 original; el verificador no distingue ese caso y aplica el texto modificado.",
    "Coeficientes a/b/n de las curvas IDF regionales de ras2000_tablas.py: de referencia, sin cita verificable.",
    "Límites de velocidad por material (3,0 m/s PVC/HDPE; 5,0 m/s concreto) en manning.py: los Arts. 142 y 150 remiten a los límites recomendados del material sin dar cifras.",
)


def regla(id_: str) -> Regla:
    return REGLAS[id_]


def vigencia_ras2000() -> dict:
    """Estado de vigencia del RAS 2000 (Res. 1096/2000), citado todavía como referencia metodológica en partes del motor."""
    return {"norma": "Resolución 1096 de 2000 (RAS 2000)", "estado": "derogada",
            "derogada_por": f"Resolución 0330 de 2017, {DEROGATORIA.articulo}", "texto": DEROGATORIA.enunciado, "cadena_0330": [list(h) for h in HISTORIAL],
            "uso_permitido": "referencia metodológica histórica; no sustenta cumplimiento normativo"}
