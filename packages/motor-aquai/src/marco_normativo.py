"""
AquaAI — Marco normativo centralizado
Registro de las reglas de la Resolución 0330/2017 que el motor verifica, con fuente, artículo y estado de vigencia.

Todas las reglas listadas se verificaron contra el texto de la resolución indexado en el repositorio
(packages/construdata/normativa_raw/res0330/res0330.txt). Lo que NO esté verificado en texto no entra aquí:
se declara aparte en NO_VERIFICADO para que ningún valor sin fuente se presente como norma.
"""
from __future__ import annotations

from dataclasses import dataclass

FUENTE = "Resolución 0330 de 2017, Ministerio de Vivienda, Ciudad y Territorio"


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
          "Se debe simular con tiempos de concentración mínimos entre 3 y 10 minutos y evaluar la incidencia de adoptar uno u otro valor.", None, "min"),
    Regla("velocidad_max_colector", FUENTE, "Art. 142", "velocidad máxima",
          "La velocidad máxima real en un colector por gravedad no debe sobrepasar 5,0 m/s para el caudal de diseño.", 5.0, "m/s"),
    Regla("velocidad_excepcion", FUENTE, "Art. 142", "excepción por pendiente fuerte",
          "Con topografías de pendiente superior al 30 %, colectores de diámetro igual o superior a 600 mm o caudales superiores a 500 L/s se permiten velocidades mayores a 5 m/s, "
          "sin sobrepasar los límites del material, con protecciones y soluciones de disipación de energía.", 0.30, "m/m"),
    Regla("suds_reduccion_pico", FUENTE, "Art. 151", "drenaje sostenible",
          "En nuevos desarrollos los sistemas urbanos de drenaje sostenible deben reducir como mínimo 25 % el caudal pico del hidrograma de creciente de diseño.", 25.0, "%"),
    Regla("camara_caida_desnivel", FUENTE, "Art. 153", "cámara de caída",
          "El colector que llegue a una estructura de conexión con diferencia de cotas batea mayor a 0,75 m respecto del colector de salida debe entregar mediante cámara de caída.", 0.75, "m"),
    Regla("disipacion_desnivel", FUENTE, "Art. 153", "disipación de energía",
          "Para desniveles mayores a 7,0 m se deben diseñar estructuras de disipación de energía.", 7.0, "m"),
)}

DEROGATORIA = Regla("derogatoria_ras2000", FUENTE, "Art. 255", "vigencia",
                    "Deroga las resoluciones 1096 de 2000 (RAS 2000), 0424 de 2001, 0668 de 2003, 1459 de 2005, 1447 de 2005 y 2320 de 2009.")

# Valores o referencias que el motor menciona pero que NO se verificaron en el texto indexado.
NO_VERIFICADO = (
    "Tabla 16 (períodos de retorno mínimos): solo está en el PDF original; no se verifica el período de retorno hasta transcribirla.",
    "Resoluciones 799 y 908 de 2021 (modificatorias, citadas en ras2000_tablas.py): su texto no está indexado.",
    "Coeficientes a/b/n de las curvas IDF regionales de ras2000_tablas.py: de referencia, sin cita verificable.",
    "Límites de velocidad por material (3,0 m/s PVC/HDPE; 5,0 m/s concreto) en manning.py: el Art. 142 remite a los límites del material sin dar cifras.",
)


def regla(id_: str) -> Regla:
    return REGLAS[id_]


def vigencia_ras2000() -> dict:
    """Estado de vigencia del RAS 2000 (Res. 1096/2000), citado todavía como referencia metodológica en partes del motor."""
    return {"norma": "Resolución 1096 de 2000 (RAS 2000)", "estado": "derogada",
            "derogada_por": f"{FUENTE}, {DEROGATORIA.articulo}", "texto": DEROGATORIA.enunciado,
            "uso_permitido": "referencia metodológica histórica; no sustenta cumplimiento normativo"}
