"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — MODELOS DE DATOS
Análisis estructural: deformación, esfuerzo y pandeo
Unidades internas SI estrictas: metros (m), Newton (N), Pascal (Pa)
══════════════════════════════════════════════════════════════
"""
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
import math


class TipoElemento(str, Enum):
    VIGA = "Viga"
    COLUMNA = "Columna"
    MURO = "Muro"
    LOSA = "Losa"


class CondicionApoyo(str, Enum):
    CANTILEVER = "Cantilever (empotrada-libre)"
    SIMPLE = "Simplemente apoyada"
    EMPOTRADA_EMPOTRADA = "Empotrada-empotrada"
    EMPOTRADA_APOYADA = "Empotrada-apoyada (propped)"


# Factor de longitud efectiva K por condición de apoyo (pandeo de columnas, AISC)
K_PANDEO: dict[CondicionApoyo, float] = {
    CondicionApoyo.CANTILEVER: 2.0,
    CondicionApoyo.SIMPLE: 1.0,
    CondicionApoyo.EMPOTRADA_EMPOTRADA: 0.5,
    CondicionApoyo.EMPOTRADA_APOYADA: 0.7,
}


class TipoCarga(str, Enum):
    PUNTUAL = "Puntual"
    DISTRIBUIDA_UNIFORME = "Distribuida uniforme"
    DISTRIBUIDA_GENERAL = "Distribuida general"


@dataclass
class Material:
    """
    Material elástico lineal (Ley de Hooke, régimen isotrópico).
    E, G, fy, fu en Pascales (Pa) — usar `desde_MPa()` para capturar en MPa.
    """
    nombre: str
    E: float                    # Módulo de elasticidad (Pa)
    nu: float = 0.3              # Coeficiente de Poisson
    fy: float = 0.0              # Esfuerzo de fluencia (Pa)
    fu: Optional[float] = None   # Esfuerzo último (Pa)
    densidad: float = 7850.0     # kg/m3
    # Incertidumbre (coeficiente de variación σ/μ) — mismo criterio que Motor APU
    cov_E: float = 0.05
    cov_fy: float = 0.10

    @property
    def G(self) -> float:
        """Módulo de cortante derivado de teoría de elasticidad isotrópica: G = E / (2(1+ν))"""
        return self.E / (2 * (1 + self.nu))

    @classmethod
    def desde_MPa(
        cls, nombre: str, E_MPa: float, fy_MPa: float,
        nu: float = 0.3, fu_MPa: Optional[float] = None,
        densidad: float = 7850.0, cov_E: float = 0.05, cov_fy: float = 0.10,
    ) -> "Material":
        return cls(
            nombre=nombre, E=E_MPa * 1e6, nu=nu, fy=fy_MPa * 1e6,
            fu=(fu_MPa * 1e6) if fu_MPa is not None else None,
            densidad=densidad, cov_E=cov_E, cov_fy=cov_fy,
        )


@dataclass
class SeccionTransversal:
    """
    Propiedades geométricas de la sección transversal, referidas al eje
    centroidal. Calculadas por integración analítica (formas cerradas) o
    por integración numérica sobre polígono (`geometry.propiedades_poligono`).
    """
    nombre: str
    area: float          # m²
    Ix: float             # Momento de inercia respecto al eje centroidal x (m⁴) — flexión eje fuerte
    Iy: float             # Momento de inercia respecto al eje centroidal y (m⁴)
    Ixy: float = 0.0       # Producto de inercia (m⁴)
    c_sup: float = 0.0     # Distancia fibra extrema superior al eje centroidal x (m)
    c_inf: float = 0.0     # Distancia fibra extrema inferior al eje centroidal x (m)
    ancho_alma: Optional[float] = None  # Ancho en el eje neutro, para cortante τ=VQ/(Ib) (m)
    Q_max: Optional[float] = None       # Primer momento de área máximo (m³), sección rectangular: A*h/8... se calcula en geometry
    # Incertidumbre dimensional (afecta Ix, Iy vía propagación ~ dimensión^n)
    cov_dimension: float = 0.02

    @property
    def radio_giro_x(self) -> float:
        return math.sqrt(self.Ix / self.area) if self.area > 0 else 0.0

    @property
    def radio_giro_y(self) -> float:
        return math.sqrt(self.Iy / self.area) if self.area > 0 else 0.0

    @property
    def modulo_seccion_sup(self) -> float:
        """S = I/c (m³) — módulo resistente elástico, fibra superior."""
        return self.Ix / self.c_sup if self.c_sup > 0 else 0.0

    @property
    def modulo_seccion_inf(self) -> float:
        return self.Ix / self.c_inf if self.c_inf > 0 else 0.0

    @property
    def c_max(self) -> float:
        return max(self.c_sup, self.c_inf)


@dataclass
class CargaAplicada:
    """
    Carga sobre el elemento.
    - PUNTUAL:               magnitud en N, `posicion` = fracción de L (0..1) donde actúa
    - DISTRIBUIDA_UNIFORME:  magnitud en N/m, actúa en todo el vano
    - DISTRIBUIDA_GENERAL:   `funcion` (N/m) recibe x en metros, 0<=x<=L
    Convención: magnitud positiva = actúa hacia abajo / en compresión (columnas).
    """
    tipo: TipoCarga
    magnitud: float = 0.0
    posicion: Optional[float] = None          # fracción 0..1 (solo PUNTUAL)
    funcion: Optional[Callable[[float], float]] = None   # solo DISTRIBUIDA_GENERAL
    descripcion: str = ""
    # Incertidumbre — cargas variables/vivas tienen mayor variación que las permanentes
    cov_carga: float = 0.15


@dataclass
class ElementoEstructural:
    """Elemento físico a analizar: viga, columna, muro o losa."""
    id: str
    tipo_elemento: TipoElemento
    material: Material
    seccion: SeccionTransversal
    longitud: float                            # m (luz libre / altura libre)
    condicion_apoyo: CondicionApoyo = CondicionApoyo.SIMPLE
    k_pandeo: Optional[float] = None            # si None, se toma de K_PANDEO[condicion_apoyo]
    deflexion_limite_razon: float = 360.0        # límite servicio L/360 (NSR-10 C.9 / ACI 318 típico)

    @property
    def K(self) -> float:
        return self.k_pandeo if self.k_pandeo is not None else K_PANDEO[self.condicion_apoyo]

    @property
    def deflexion_admisible(self) -> float:
        return self.longitud / self.deflexion_limite_razon


@dataclass
class ResultadoDeformacion:
    """
    Resultado de análisis. Incluye valor determinístico (referencia) y
    caracterización probabilística (Monte Carlo) porque el objetivo no es
    fingir un número exacto sino acotar honestamente el margen de error.
    """
    elemento_id: str
    tipo_analisis: str                  # "flexion" | "pandeo" | "combinado"
    # Determinístico
    deflexion_max: float = 0.0           # m
    momento_max: float = 0.0             # N·m
    cortante_max: float = 0.0            # N
    esfuerzo_flexion_max: float = 0.0     # Pa
    esfuerzo_cortante_max: float = 0.0    # Pa
    carga_critica_pandeo: Optional[float] = None   # N (Pcr Euler/Johnson)
    factor_seguridad: float = 0.0
    deflexion_admisible: float = 0.0
    cumple_deflexion: bool = False
    cumple_esfuerzo: bool = False
    # Incertidumbre (Monte Carlo, N=5000)
    deflexion_mean: float = 0.0
    deflexion_std: float = 0.0
    deflexion_p05: float = 0.0
    deflexion_p95: float = 0.0
    esfuerzo_mean: float = 0.0
    esfuerzo_std: float = 0.0
    esfuerzo_p05: float = 0.0
    esfuerzo_p95: float = 0.0
    indice_confiabilidad: float = 0.0     # β (FOSM) — mayor es más seguro
    probabilidad_falla: float = 0.0       # P[esfuerzo > fy] aprox. Φ(-β)
    # Metadata
    notas: list[str] = field(default_factory=list)
