"""
Diseño geométrico de carreteras (Manual de Diseño Geométrico de Carreteras
INVIAS 2008, con actualización de bombeo por tipo de superficie tomada del
Manual INVIAS 2025). Radio mínimo de curva horizontal por velocidad de
diseño y peralte (con interpolación), distancias de visibilidad de parada
y adelantamiento, pendiente longitudinal máxima, ancho mínimo de carril y
bombeo de calzada.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# 1. ENUMS
# ============================================================================

class TipoVia(Enum):
    """Clasificación de vías según INVIAS."""
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"
    TERCIARIA = "terciaria"


class Topografia(Enum):
    """Tipo de terreno según INVIAS."""
    PLANO = "plano"
    ONDULADO = "ondulado"
    MONTANOSO = "montanoso"
    ESCARPADO = "escarpado"


class TipoSuperficie(Enum):
    """Tipo de superficie de rodadura (Manual INVIAS 2025)."""
    ASFALTICA = "asfaltica"
    CONCRETO = "concreto"
    AFIRMADO = "afirmado"


# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================

@dataclass
class ParametrosDiseno:
    """Parámetros de entrada para el diseño geométrico."""
    tipo_via: TipoVia
    velocidad_diseno: float                          # km/h
    topografia: Topografia
    volumen_transito: int                             # TPD
    radio_curva: Optional[float] = None               # metros
    pendiente_longitudinal: Optional[float] = None     # %
    peralte: Optional[float] = None                    # %
    ancho_carril: Optional[float] = None                # metros
    bombeo: Optional[float] = None                       # %
    tipo_superficie: Optional[TipoSuperficie] = None
    calzadas: int = 1                                    # solo importa en vías Primarias (Tabla 4.2)


@dataclass
class Restriccion:
    """Representa una restricción técnica del diseño."""
    nombre: str
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    formula: Optional[str] = None
    referencia: str = ""
    unidad: str = ""


@dataclass
class ResultadoValidacion:
    """Resultado de la validación de un diseño."""
    cumple: bool
    mensaje: str
    restricciones_aplicadas: List[Dict[str, Any]] = field(default_factory=list)
    sugerencias: List[str] = field(default_factory=list)


# ============================================================================
# 3. BASE DE CONOCIMIENTO DEL MANUAL DE DISEÑO GEOMÉTRICO INVIAS
# ============================================================================

class ManualINVIAS2008:
    """
    Base de conocimiento del Manual de Diseño Geométrico de Carreteras
    INVIAS 2008. El bombeo por tipo de superficie incorpora la
    actualización del Manual INVIAS 2025.
    """

    def __init__(self):
        self._cargar_tablas()
        self._cargar_restricciones()
        self._cargar_recomendaciones()

    def _cargar_tablas(self):
        """Tablas del manual INVIAS."""
        # Coeficiente de fricción transversal máxima fTmáx por velocidad
        # específica VCH (km/h). Tabla 3.1 del Capítulo 3 (valores AASHTO),
        # verificada contra el PDF oficial del CD INV-2008 el 2026-11-06.
        self.friccion_transversal_maxima = {
            20: 0.35, 30: 0.28, 40: 0.23, 50: 0.19, 60: 0.17, 70: 0.15,
            80: 0.14, 90: 0.13, 100: 0.12, 110: 0.11, 120: 0.09, 130: 0.08,
        }

        # Radios mínimos REDONDEADOS (m) que publica el manual, por peralte
        # máximo emáx: Tabla 3.2 (emáx 8 %, vías Primarias y Secundarias) y
        # Tabla 3.3 (emáx 6 %, vías Terciarias). Copiados del PDF oficial.
        # Corrigen una tabla anterior de este repo que quedaba 15-44 % por
        # debajo del manual (lado inseguro) e incluía una columna de 10 %
        # que el manual no publica. RCmín = V^2 / (127 (emáx + fTmáx)).
        self.radios_minimos_tabulados = {
            8: {40: 41, 50: 73, 60: 113, 70: 168, 80: 229,
                90: 304, 100: 394, 110: 501, 120: 667, 130: 832},
            6: {20: 15, 30: 21, 40: 43, 50: 79, 60: 123},
        }
        self.peralte_maximo_por_tipo_via = {
            TipoVia.PRIMARIA: 8, TipoVia.SECUNDARIA: 8, TipoVia.TERCIARIA: 6,
        }

        # Distancia de visibilidad de parada en tramos a nivel (m, REDONDEADA).
        # Tabla 2.6 del Capítulo 2, verificada contra el PDF oficial INV-2008
        # (2026-11-06). Reemplaza una tabla anterior que difería hasta 30 %.
        self.distancia_visibilidad_parada = {
            20: 20, 30: 35, 40: 50, 50: 65, 60: 85, 70: 105,
            80: 130, 90: 160, 100: 185, 110: 220, 120: 250, 130: 285,
        }

        # Distancia mínima de visibilidad de adelantamiento, carreteras de dos
        # carriles (m, REDONDEADA). Tabla 2.9 del Capítulo 2, verificada contra el
        # PDF oficial (2026-11-06). El valor de 20 km/h es extrapolado según el
        # propio manual. La tabla anterior de este repo difería hasta 20 %.
        self.distancia_visibilidad_adelantamiento = {
            20: 130, 30: 200, 40: 270, 50: 345, 60: 410, 70: 485,
            80: 540, 90: 615, 100: 670, 110: 730, 120: 775, 130: 815,
        }

        # Pendiente longitudinal máxima (%) por tipo de vía y topografía.
        # Tabla 4.1 del Capítulo 4.
        self.pendientes_maximas_vtv = {
            # Tabla 4.2 del Capítulo 4 (Manual INVIAS 2008), verificada visualmente
            # contra el PDF oficial el 2026-11-06: pendiente máxima (%) de una
            # tangente vertical según su Velocidad Específica VTV (km/h). Un guion
            # del manual significa que esa categoría no se diseña a esa velocidad
            # (aquí: ausente). Reemplaza una tabla anterior por topografía que no
            # está en el manual y en varios casos permitía más que él.
            "primaria_2_calzadas": {70: 6, 80: 6, 90: 6, 100: 5, 110: 5, 120: 4, 130: 4},
            "primaria_1_calzada": {60: 8, 70: 7, 80: 6, 90: 6, 100: 5, 110: 5, 120: 5},
            "secundaria": {40: 10, 50: 9, 60: 8, 70: 7, 80: 6, 90: 6, 100: 6},
            "terciaria": {20: 14, 30: 12, 40: 10, 50: 10, 60: 10},
        }
        # Aumento permitido de 2 puntos cuando una tangente vertical de pendiente
        # máxima va entre dos curvas verticales consecutivas sin tramo recto
        # (texto bajo la Tabla 4.2). No se aplica automáticamente.
        self.aumento_pendiente_curvas_consecutivas = 2

        # Ancho mínimo de carril (m) por tipo de vía. Capítulo 5.
        self.ancho_carril_minimo = {
            TipoVia.PRIMARIA: 3.65,
            TipoVia.SECUNDARIA: 3.30,
            TipoVia.TERCIARIA: 3.00,
        }

        # Bombeo recomendado (%) por tipo de vía.
        self.bombeo_recomendado = {
            TipoVia.PRIMARIA: 2.5,
            TipoVia.SECUNDARIA: 2.5,
            TipoVia.TERCIARIA: 2.0,
        }

        # Bombeo recomendado (%) por tipo de superficie (Manual INVIAS 2025).
        self.bombeo_recomendado_superficie = {
            TipoSuperficie.ASFALTICA: 2.5,
            TipoSuperficie.CONCRETO: 2.0,
            TipoSuperficie.AFIRMADO: 3.0,
        }

    def radio_minimo(self, velocidad: float, tipo_via: "TipoVia") -> tuple[float, str]:
        """Radio mínimo de curva horizontal (m) y su origen.

        El peralte máximo lo fija el tipo de vía (manual 3.1.3.2: 8 % en
        Primarias/Secundarias, 6 % en Terciarias), no el peralte de diseño de
        cada curva. Si el manual publica el valor, se devuelve ese; si no
        (p. ej. emáx 6 % con V > 60), se calcula con la misma ecuación y la
        Tabla 3.1 y se marca como calculado."""
        emax = self.peralte_maximo_por_tipo_via[tipo_via]
        tabulado = self.radios_minimos_tabulados[emax].get(int(velocidad))
        if tabulado is not None and float(velocidad) == int(velocidad):
            return float(tabulado), f"Capítulo 3 - Tabla {'3.2' if emax == 8 else '3.3'}"
        f = self._friccion(velocidad)
        return round(velocidad ** 2 / (127 * (emax / 100 + f)), 1), "ecuación 3.1.3.4 con Tabla 3.1 (no tabulado)"

    def _friccion(self, velocidad: float) -> float:
        """fTmáx de la Tabla 3.1; interpola entre velocidades tabuladas."""
        tabla = self.friccion_transversal_maxima
        vs = sorted(tabla)
        if velocidad <= vs[0]:
            return tabla[vs[0]]
        if velocidad >= vs[-1]:
            return tabla[vs[-1]]
        for a, b in zip(vs, vs[1:]):
            if a <= velocidad <= b:
                return tabla[a] + (tabla[b] - tabla[a]) * (velocidad - a) / (b - a)
        return tabla[vs[-1]]

    def pendiente_maxima(self, tipo_via: "TipoVia", velocidad: float, calzadas: int = 1) -> tuple[Optional[int], str]:
        """Pendiente máxima (%) de la Tabla 4.2 y su origen; None si el manual
        no contempla esa categoría a esa velocidad."""
        if tipo_via == TipoVia.PRIMARIA:
            clave = "primaria_2_calzadas" if calzadas >= 2 else "primaria_1_calzada"
        else:
            clave = tipo_via.value
        valor = self.pendientes_maximas_vtv[clave].get(int(velocidad)) if float(velocidad) == int(velocidad) else None
        return valor, f"Capítulo 4 - Tabla 4.2 ({clave.replace('_', ' ')}, VTV {velocidad:g} km/h)"

    def _cargar_restricciones(self):
        """Define las restricciones técnicas del manual."""
        self.restricciones = {
            "radio_minimo": Restriccion(
                nombre="Radio mínimo de curva horizontal",
                referencia="Capítulo 3 - Tabla 3.2",
                unidad="m",
            ),
            "peralte_maximo": Restriccion(
                nombre="Peralte máximo",
                valor_maximo=8.0,
                referencia="Capítulo 3",
                unidad="%",
            ),
            "distancia_visibilidad_parada": Restriccion(
                nombre="Distancia de visibilidad de parada",
                referencia="Capítulo 3 - Tabla 3.4",
                unidad="m",
            ),
            "pendiente_maxima": Restriccion(
                nombre="Pendiente longitudinal máxima",
                referencia="Capítulo 4 - Tabla 4.1",
                unidad="%",
            ),
            "ancho_carril_minimo": Restriccion(
                nombre="Ancho mínimo de carril",
                referencia="Capítulo 5",
                unidad="m",
            ),
            "bombeo_minimo": Restriccion(
                nombre="Bombeo mínimo de calzada",
                valor_minimo=2.0,
                referencia="Capítulo 5",
                unidad="%",
            ),
        }

    def _cargar_recomendaciones(self):
        """Recomendaciones de buenas prácticas del manual."""
        self.recomendaciones = {
            "velocidad_diseno": "La velocidad de diseño debe ser consistente con la topografía y el tipo de vía.",
            "curvas_verticales": "Para cambios de pendiente > 1%, usar curvas verticales parabólicas.",
            "peralte": "El peralte debe desarrollarse gradualmente en la longitud de transición.",
            "seccion_transversal": "La sección transversal debe considerar drenaje, seguridad y comodidad.",
        }


# ============================================================================
# 4. MOTOR DE VALIDACIÓN Y RESTRICCIONES
# ============================================================================

class MotorValidacion:
    """
    Motor de validación de diseño geométrico basado en las restricciones
    del Manual de Diseño Geométrico de Carreteras INVIAS.
    """

    def __init__(self, manual: ManualINVIAS2008):
        self.manual = manual
        self._errores: List[str] = []

    def validar(self, params: ParametrosDiseno) -> ResultadoValidacion:
        """Valida un conjunto de parámetros de diseño contra las restricciones del manual."""
        self._errores = []
        restricciones_aplicadas: List[Dict[str, Any]] = []

        self._validar_velocidad(params, restricciones_aplicadas)

        if params.radio_curva:
            self._validar_radio_curva(params, restricciones_aplicadas)

        if params.peralte:
            self._validar_peralte(params, restricciones_aplicadas)

        if params.pendiente_longitudinal:
            self._validar_pendiente(params, restricciones_aplicadas)

        if params.ancho_carril:
            self._validar_ancho_carril(params, restricciones_aplicadas)

        if params.bombeo:
            self._validar_bombeo(params, restricciones_aplicadas)

        sugerencias = self._generar_sugerencias(params)

        cumple = len(self._errores) == 0
        mensaje = "Diseño válido" if cumple else f"Se encontraron {len(self._errores)} errores"

        return ResultadoValidacion(
            cumple=cumple,
            mensaje=mensaje,
            restricciones_aplicadas=restricciones_aplicadas,
            sugerencias=sugerencias,
        )

    def _validar_velocidad(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida que la velocidad de diseño esté dentro del rango permitido."""
        if params.velocidad_diseno < 30 or params.velocidad_diseno > 120:
            self._errores.append(
                f"Velocidad de diseño {params.velocidad_diseno} km/h fuera de rango (30-120 km/h)"
            )
            return

        if params.velocidad_diseno % 10 != 0:
            self._errores.append(
                f"Velocidad de diseño {params.velocidad_diseno} km/h no es válida. Usar múltiplos de 10."
            )

        restricciones.append({
            "nombre": "Velocidad de diseño",
            "valor": params.velocidad_diseno,
            "rango": "30-120 km/h",
            "cumple": 30 <= params.velocidad_diseno <= 120,
        })

    def _validar_radio_curva(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida el radio mínimo de curva horizontal según el Capítulo 3 del
        Manual INVIAS 2008 (Tablas 3.1 a 3.3)."""
        v = params.velocidad_diseno
        radio_minimo, origen = self.manual.radio_minimo(v, params.tipo_via)
        emax = self.manual.peralte_maximo_por_tipo_via[params.tipo_via]

        cumple = params.radio_curva >= radio_minimo
        if not cumple:
            self._errores.append(
                f"Radio de curva {params.radio_curva:.2f} m es menor que el mínimo "
                f"({radio_minimo:.2f} m) para V={v} km/h y peralte máximo {emax}%"
            )

        restricciones.append({
            "nombre": "Radio mínimo de curva",
            "valor": params.radio_curva,
            "minimo": radio_minimo,
            "cumple": cumple,
            "referencia": origen,
        })

    def _validar_peralte(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida que el peralte no exceda el máximo permitido."""
        peralte_max = self.manual.restricciones["peralte_maximo"].valor_maximo
        cumple = params.peralte <= peralte_max

        if not cumple:
            self._errores.append(f"Peralte {params.peralte:.1f}% excede el máximo {peralte_max}%")

        restricciones.append({
            "nombre": "Peralte máximo",
            "valor": params.peralte,
            "maximo": peralte_max,
            "cumple": cumple,
            "referencia": "Capítulo 3",
        })

    def _validar_pendiente(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida la pendiente longitudinal contra la Tabla 4.2 del manual, que
        depende de la categoría de la vía y de la velocidad específica de la
        tangente vertical (se usa la velocidad de diseño como VTV)."""
        pendiente_max, origen = self.manual.pendiente_maxima(
            params.tipo_via, params.velocidad_diseno, params.calzadas)

        if pendiente_max is None:
            cumple = False
            self._errores.append(
                f"El manual (Tabla 4.2) no define pendiente máxima para vía {params.tipo_via.value} "
                f"a {params.velocidad_diseno:g} km/h: la categoría no se diseña a esa velocidad"
            )
        else:
            cumple = abs(params.pendiente_longitudinal) <= pendiente_max
            if not cumple:
                self._errores.append(
                    f"Pendiente {params.pendiente_longitudinal:.1f}% excede el máximo "
                    f"{pendiente_max}% para vía {params.tipo_via.value} a {params.velocidad_diseno:g} km/h"
                )

        restricciones.append({
            "nombre": "Pendiente longitudinal máxima",
            "valor": params.pendiente_longitudinal,
            "maximo": pendiente_max,
            "cumple": cumple,
            "referencia": origen,
        })

    def _validar_ancho_carril(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida el ancho mínimo de carril según tipo de vía."""
        if params.tipo_via not in self.manual.ancho_carril_minimo:
            raise ValueError(
                f"Tipo de vía {params.tipo_via} sin ancho mínimo de carril en el Manual de Diseño Geométrico "
                f"INVIAS (Capítulo 5): no se asume un valor por defecto."
            )
        ancho_min = self.manual.ancho_carril_minimo[params.tipo_via]
        cumple = params.ancho_carril >= ancho_min

        if not cumple:
            self._errores.append(
                f"Ancho de carril {params.ancho_carril:.2f} m es menor que el mínimo "
                f"{ancho_min:.2f} m para vía {params.tipo_via.value}"
            )

        restricciones.append({
            "nombre": "Ancho mínimo de carril",
            "valor": params.ancho_carril,
            "minimo": ancho_min,
            "cumple": cumple,
            "referencia": "Capítulo 5",
        })

    def _validar_bombeo(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida el bombeo mínimo de la calzada, y lo compara con el recomendado por
        tipo de superficie cuando esta se especifica."""
        bombeo_min = self.manual.restricciones["bombeo_minimo"].valor_minimo
        cumple = params.bombeo >= bombeo_min

        if not cumple:
            self._errores.append(f"Bombeo {params.bombeo:.1f}% es menor que el mínimo {bombeo_min}%")

        entrada = {
            "nombre": "Bombeo mínimo",
            "valor": params.bombeo,
            "minimo": bombeo_min,
            "cumple": cumple,
            "referencia": "Capítulo 5",
        }

        if params.tipo_superficie:
            entrada["bombeo_recomendado_superficie"] = self.manual.bombeo_recomendado_superficie.get(
                params.tipo_superficie
            )

        restricciones.append(entrada)

    def _generar_sugerencias(self, params: ParametrosDiseno) -> List[str]:
        """Genera sugerencias de mejora basadas en los parámetros de entrada."""
        sugerencias: List[str] = []

        if params.velocidad_diseno < 50:
            sugerencias.append("Considere aumentar la velocidad de diseño si la topografía lo permite.")

        if params.radio_curva:
            radio_min, _ = self.manual.radio_minimo(params.velocidad_diseno, params.tipo_via)
            radio_recomendado = radio_min * 1.5
            if params.radio_curva < radio_recomendado:
                sugerencias.append(
                    f"Para mayor comodidad y seguridad, use un radio de al menos "
                    f"{radio_recomendado:.0f} m (1.5 veces el mínimo)."
                )

        if params.pendiente_longitudinal and params.pendiente_longitudinal > 5:
            sugerencias.append("En pendientes > 5%, considere carriles de ascenso para vehículos pesados.")

        if params.peralte and params.peralte > 6:
            sugerencias.append("Peraltes > 6% pueden ser incómodos para vehículos lentos. Considere reducir.")

        return sugerencias


if __name__ == "__main__":
    manual = ManualINVIAS2008()
    motor = MotorValidacion(manual)

    params = ParametrosDiseno(
        tipo_via=TipoVia.PRIMARIA,
        velocidad_diseno=80,
        topografia=Topografia.MONTANOSO,
        volumen_transito=5000,
        radio_curva=180,
        pendiente_longitudinal=6.5,
        peralte=7.0,
        ancho_carril=3.50,
        bombeo=2.5,
        tipo_superficie=TipoSuperficie.ASFALTICA,
    )

    resultado = motor.validar(params)
    print(resultado.mensaje)
    for r in resultado.restricciones_aplicadas:
        estado = "OK" if r.get("cumple", True) else "FALLA"
        print(f"  [{estado}] {r['nombre']}: {r}")
    for s in resultado.sugerencias:
        print(f"  Sugerencia: {s}")
