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
        # Radios mínimos (m) en función de la velocidad de diseño (km/h)
        # y el peralte máximo (%). Tabla 3.2 del Capítulo 3.
        self.radios_minimos = {
            30: {6: 25, 8: 20, 10: 15},
            40: {6: 45, 8: 35, 10: 25},
            50: {6: 70, 8: 55, 10: 40},
            60: {6: 105, 8: 80, 10: 60},
            70: {6: 150, 8: 115, 10: 90},
            80: {6: 205, 8: 160, 10: 125},
            90: {6: 270, 8: 210, 10: 165},
            100: {6: 345, 8: 270, 10: 215},
            110: {6: 430, 8: 340, 10: 270},
            120: {6: 530, 8: 420, 10: 335},
        }

        # Distancia de visibilidad de parada (m). Tabla 3.4 INVIAS.
        self.distancia_visibilidad_parada = {
            30: 35, 40: 55, 50: 75, 60: 100,
            70: 130, 80: 160, 90: 195, 100: 235,
            110: 280, 120: 330,
        }

        # Distancia de visibilidad de adelantamiento (m). Tabla 3.5 INVIAS.
        self.distancia_visibilidad_adelantamiento = {
            30: 140, 40: 200, 50: 280, 60: 360,
            70: 460, 80: 570, 90: 690, 100: 820,
            110: 970, 120: 1130,
        }

        # Pendiente longitudinal máxima (%) por tipo de vía y topografía.
        # Tabla 4.1 del Capítulo 4.
        self.pendientes_maximas = {
            TipoVia.PRIMARIA: {
                Topografia.PLANO: 4,
                Topografia.ONDULADO: 5,
                Topografia.MONTANOSO: 7,
                Topografia.ESCARPADO: 9,
            },
            TipoVia.SECUNDARIA: {
                Topografia.PLANO: 5,
                Topografia.ONDULADO: 6,
                Topografia.MONTANOSO: 8,
                Topografia.ESCARPADO: 10,
            },
            TipoVia.TERCIARIA: {
                Topografia.PLANO: 6,
                Topografia.ONDULADO: 8,
                Topografia.MONTANOSO: 10,
                Topografia.ESCARPADO: 12,
            },
        }

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
        """Valida el radio mínimo de curva horizontal según tabla INVIAS."""
        v = params.velocidad_diseno
        peralte_efectivo = params.peralte if params.peralte else 6.0

        if v in self.manual.radios_minimos:
            peraltes_disponibles = sorted(self.manual.radios_minimos[v].keys())
            peralte_usado = min(peraltes_disponibles, key=lambda x: abs(x - peralte_efectivo))
            radio_minimo = self.manual.radios_minimos[v][peralte_usado]
        else:
            radio_minimo = self._interpolar_radio(v, peralte_efectivo)

        cumple = params.radio_curva >= radio_minimo
        if not cumple:
            self._errores.append(
                f"Radio de curva {params.radio_curva:.2f} m es menor que el mínimo "
                f"({radio_minimo:.2f} m) para V={v} km/h y peralte={peralte_efectivo:.1f}%"
            )

        restricciones.append({
            "nombre": "Radio mínimo de curva",
            "valor": params.radio_curva,
            "minimo": radio_minimo,
            "cumple": cumple,
            "referencia": "Capítulo 3 - Tabla 3.2",
        })

    def _interpolar_radio(self, velocidad: float, peralte: float) -> float:
        """Interpola linealmente el radio mínimo para velocidades no estándar."""
        velocidades = sorted(self.manual.radios_minimos.keys())

        def _radio_para(v: int) -> float:
            peraltes = self.manual.radios_minimos[v].keys()
            peralte_cercano = min(peraltes, key=lambda x: abs(x - peralte))
            return self.manual.radios_minimos[v][peralte_cercano]

        if velocidad <= velocidades[0]:
            return _radio_para(velocidades[0])
        if velocidad >= velocidades[-1]:
            return _radio_para(velocidades[-1])

        for i in range(len(velocidades) - 1):
            v1, v2 = velocidades[i], velocidades[i + 1]
            if v1 <= velocidad <= v2:
                r1, r2 = _radio_para(v1), _radio_para(v2)
                return r1 + (r2 - r1) * (velocidad - v1) / (v2 - v1)

        return 0.0

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
        """Valida que la pendiente longitudinal no exceda el máximo según tipo de vía y topografía."""
        pendiente_max = self.manual.pendientes_maximas.get(params.tipo_via, {}).get(params.topografia, 8)
        cumple = abs(params.pendiente_longitudinal) <= pendiente_max

        if not cumple:
            self._errores.append(
                f"Pendiente {params.pendiente_longitudinal:.1f}% excede el máximo "
                f"{pendiente_max}% para vía {params.tipo_via.value} en topografía {params.topografia.value}"
            )

        restricciones.append({
            "nombre": "Pendiente longitudinal máxima",
            "valor": params.pendiente_longitudinal,
            "maximo": pendiente_max,
            "cumple": cumple,
            "referencia": "Capítulo 4 - Tabla 4.1",
        })

    def _validar_ancho_carril(self, params: ParametrosDiseno, restricciones: List[Dict[str, Any]]):
        """Valida el ancho mínimo de carril según tipo de vía."""
        ancho_min = self.manual.ancho_carril_minimo.get(params.tipo_via, 3.0)
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
            v = params.velocidad_diseno
            if v in self.manual.radios_minimos:
                radio_recomendado = max(self.manual.radios_minimos[v].values()) * 1.5
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
