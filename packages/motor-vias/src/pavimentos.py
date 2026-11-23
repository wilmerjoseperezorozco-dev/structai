"""
Diseño estructural preliminar de pavimentos con el método AASHTO-93, que es el que adoptan los manuales de INVIAS.

- Flexible: Número Estructural (SN) y espesores de capas. La rodadura mínima depende del tránsito (ver
  `ESPESOR_MINIMO_RODADURA_ASFALTICA`) y la subbase es la capa variable que completa el SN, como en el Manual INVIAS de
  bajos volúmenes.
- Rígido: espesor de losa con la ecuación AASHTO-93 para pavimento rígido (`rigido_aashto93`, issue #106). Reemplaza
  la conversión SN / 0,39, que no tenía fuente.

No reproduce los catálogos de estructuras de INVIAS: sus tablas no están en el corpus. Antes de usarlo como herramienta
de diseño debe validarlo un ingeniero de pavimentos (#106, punto 3).
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from . import rigido_aashto93 as rig

# Los coeficientes estructurales a_i de AASHTO-93 (0,44 / 0,14 / 0,11) están definidos POR PULGADA de espesor y las tablas de SN requerido también
# vienen del método original en pulgadas. Los espesores de este módulo van en cm: hay que convertir (issue #103).
CM_POR_PULGADA = 2.54

# Rodadura asfáltica mínima por tránsito (ESAL de 80 kN en el carril de diseño, millones) → (cm, fuente).
# - Hasta 0,5 millones: Manual INVIAS de diseño de pavimentos asfálticos para vías con bajos volúmenes de tránsito (2007),
#   §5.1: T1 (< 150 000) 50 mm y T2 (150 000 a 500 000) 75 mm. INVIAS redondea los 2,5 in de AASHTO hacia arriba.
# - Más de 0,5 millones: tabla de espesores mínimos de la Guía AASHTO-93, Parte II (3,0 / 3,5 / 4,0 in), que INVIAS cita
#   como base de sus cartas (§8.2.3 del manual de altos volúmenes). Se pasa a cm y se redondea hacia arriba a 0,5 cm.
#   Falta cotejarla con las cartas de diseño de INVIAS, que el corpus no trae.
ESPESOR_MINIMO_RODADURA_ASFALTICA: Tuple[Tuple[float, float, str], ...] = (
    (0.15, 5.0, "INVIAS bajos volúmenes, T1 (< 150 000 ejes): 50 mm"),
    (0.50, 7.5, "INVIAS bajos volúmenes, T2 (150 000 a 500 000 ejes): 75 mm"),
    (2.00, 8.0, "AASHTO-93, 500 001 a 2 000 000 ESAL: 3,0 in (7,62 cm → 8,0 cm)"),
    (7.00, 9.0, "AASHTO-93, 2 000 001 a 7 000 000 ESAL: 3,5 in (8,89 cm → 9,0 cm)"),
    (math.inf, 10.5, "AASHTO-93, más de 7 000 000 ESAL: 4,0 in (10,16 cm → 10,5 cm)"),
)
# Base granular: 150 mm mínimo constructivo (INVIAS bajos volúmenes, §5.1). Cubre los 4 in de AASHTO-93 y equivale en la
# práctica métrica a sus 6 in (15,24 cm) para más de 0,5 millones de ESAL.
ESPESOR_MINIMO_BASE_GRANULAR_CM = 15.0

AVISO_VALIDACION = ("Diseño preliminar con AASHTO-93: no reemplaza el diseño firmado por un ingeniero de pavimentos ni el "
                    "catálogo del Manual INVIAS correspondiente, con el que debe cotejarse (#106).")


def espesor_minimo_rodadura_asfaltica(esals_millones: float) -> Tuple[float, str]:
    """Rodadura asfáltica mínima (cm) y su fuente según el tránsito de diseño."""
    for limite, cm, fuente in ESPESOR_MINIMO_RODADURA_ASFALTICA:
        if esals_millones <= limite:
            return cm, fuente
    raise AssertionError("inalcanzable: la última banda es infinita")


def _techo(valor: float, paso: float) -> float:
    """Redondea hacia arriba a un múltiplo de `paso`. Hacia abajo podía dejar una capa bajo su mínimo."""
    return math.ceil(round(valor / paso, 9)) * paso


# ============================================================================
# 1. ENUMS
# ============================================================================

class TipoPavimento(Enum):
    ASFALTICO = "asfaltico"
    CONCRETO = "concreto"


class TipoVia(Enum):
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"
    TERCIARIA = "terciaria"


class Topografia(Enum):
    PLANO = "plano"
    ONDULADO = "ondulado"
    MONTANOSO = "montanoso"
    ESCARPADO = "escarpado"


class TipoCapa(Enum):
    SUBRASANTE = "subrasante"
    SUBBASE = "subbase"
    BASE = "base"
    RODADURA_ASFALTICA = "rodadura_asfaltica"
    RODADURA_CONCRETO = "rodadura_concreto"


# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================

@dataclass
class ParametrosPavimento:
    """Parámetros de entrada para diseño de pavimentos."""
    tipo_pavimento: TipoPavimento
    tipo_via: TipoVia
    tpd: int                                     # Tránsito Promedio Diario
    esals_millones: float                        # Ejes equivalentes de 8.2 t (millones)
    cbr_subrasante: float                         # CBR de la subrasante (%)
    modulo_subrasante: Optional[float] = None     # Módulo resiliente (MPa)
    ip_subrasante: Optional[float] = None         # Índice de plasticidad
    temperatura_media: Optional[float] = None     # Temperatura media anual (°C)
    espesor_subbase: Optional[float] = None       # Espesor de subbase (cm)
    espesor_base: Optional[float] = None          # Espesor de base (cm)
    modulo_subbase: Optional[float] = None        # Módulo resiliente subbase (MPa)
    modulo_base: Optional[float] = None           # Módulo resiliente base (MPa)
    espesor_rodadura: Optional[float] = None      # Espesor de la capa asfáltica (cm); si no se da, se usa el mínimo por tránsito
    # ── Pavimento rígido (AASHTO-93). k y S'c los exige el método: el motor no los supone. ──
    modulo_reaccion_k: Optional[float] = None     # k efectivo sobre el soporte de la losa (MPa/m), p. ej. ensayo de placa INV E-168
    modulo_rotura_concreto: Optional[float] = None  # S'c, módulo de rotura a 28 días (MPa), INV E-414
    modulo_elastico_concreto: Optional[float] = None  # Ec (MPa); por defecto 27 580 MPa (4·10⁶ psi)
    coeficiente_transferencia_j: float = 3.2      # J: 3,2 con dovelas y berma no ligada; 3,8 sin dovelas; 2,7 con berma de concreto ligada
    coeficiente_drenaje_cd: float = 1.0
    confiabilidad: Optional[float] = None         # R (%); por defecto según el tipo de vía
    serviciabilidad_final: float = 2.5            # pt; p0 = 4,5


@dataclass
class ResultadoDisenoPavimento:
    """Resultado del diseño de pavimento."""
    tipo_pavimento: str
    espesor_total: float                          # cm
    espesor_rodadura: float                       # cm
    espesor_base: float                           # cm
    espesor_subbase: float                         # cm
    numero_estructural: float                      # SN (para asfálticos)
    espesor_equivalente_concreto: float            # cm (para concretos)
    cumple: bool
    mensaje: str
    restricciones: List[Dict[str, Any]] = field(default_factory=list)
    sugerencias: List[str] = field(default_factory=list)


# ============================================================================
# 3. MANUAL DE PAVIMENTOS - TABLAS DE DISEÑO
# ============================================================================

class ManualPavimentos:
    """Base de conocimiento del Manual de Diseño de Pavimentos Asfálticos y
    de Concreto (método mecánico-empírico, ábacos AASHTO 93 adaptados)."""

    def __init__(self):
        self._cargar_tablas()
        self._cargar_restricciones()
        self._cargar_parametros_referencia()

    def _cargar_tablas(self):
        """Tablas de diseño según método mecánico-empírico."""

        # Coeficientes estructurales para capas (a_i), AASHTO-93, por PULGADA de espesor (no por cm; ver CM_POR_PULGADA)
        self.coeficientes_estructurales = {
            "rodadura_asfaltica": {
                "tipo": "asfaltico",
                "a": 0.44,           # Coeficiente estructural (1/pulgada)
                "rango": (0.35, 0.50)
            },
            "base_granular": {
                "tipo": "granular",
                "a": 0.14,
                "rango": (0.10, 0.18)
            },
            "subbase_granular": {
                "tipo": "granular",
                "a": 0.11,
                "rango": (0.08, 0.14)
            }
        }

        # Coeficientes de drenaje (m_i)
        self.coeficientes_drenaje = {
            "excelente": 1.20,
            "bueno": 1.10,
            "regular": 1.00,
            "pobre": 0.90,
            "muy_pobre": 0.80
        }

        # Números estructurales requeridos (SN) según ESALs y CBR
        # Basado en ábacos AASHTO 93 adaptados
        self.sn_requerido = {
            # ESALs (millones) -> {CBR: SN}
            0.1: {3: 2.5, 5: 2.0, 8: 1.5, 12: 1.2},
            0.5: {3: 3.2, 5: 2.6, 8: 2.0, 12: 1.6},
            1.0: {3: 3.8, 5: 3.0, 8: 2.4, 12: 1.9},
            2.0: {3: 4.5, 5: 3.6, 8: 2.9, 12: 2.3},
            5.0: {3: 5.5, 5: 4.4, 8: 3.6, 12: 2.9},
            10.0: {3: 6.2, 5: 5.0, 8: 4.1, 12: 3.3},
            20.0: {3: 7.0, 5: 5.7, 8: 4.7, 12: 3.8},
            50.0: {3: 8.0, 5: 6.6, 8: 5.5, 12: 4.5}
        }

        # Espesores mínimos de capas (cm)
        self.espesores_minimos = {
            TipoPavimento.ASFALTICO: {
                "rodadura": 5.0,
                "base": 15.0,
                "subbase": 15.0
            },
            TipoPavimento.CONCRETO: {
                "rodadura": 15.0,
                "base": 10.0,
                "subbase": 10.0
            }
        }

        # Espesores máximos recomendados
        self.espesores_maximos = {
            TipoPavimento.ASFALTICO: {
                "rodadura": 25.0,
                "base": 40.0,
                "subbase": 60.0
            },
            TipoPavimento.CONCRETO: {
                "rodadura": 40.0,
                "base": 30.0,
                "subbase": 50.0
            }
        }

        # Factor de ajuste por temperatura para asfálticos
        self.factor_temperatura = {
            10: 1.20,   # °C -> factor
            15: 1.10,
            20: 1.00,
            25: 0.90,
            30: 0.80
        }

    def _cargar_restricciones(self):
        """Restricciones técnicas del manual."""
        self.restricciones = {
            "cbr_minimo_subrasante": {
                "valor": 3.0,
                "unidad": "%",
                "descripcion": "CBR mínimo de subrasante para vías con tránsito > 50 veh/día"
            },
            "ip_maximo_subrasante": {
                "valor": 20.0,
                "unidad": "%",
                "descripcion": "Índice de plasticidad máximo para subrasante"
            },
            "espesor_minimo_rodadura_asfaltica": {
                "valor": 5.0,
                "unidad": "cm",
                "descripcion": "Espesor mínimo de capa de rodadura asfáltica"
            },
            "espesor_minimo_rodadura_concreto": {
                "valor": 15.0,
                "unidad": "cm",
                "descripcion": "Espesor mínimo de losa de concreto hidráulico"
            }
        }

    def _cargar_parametros_referencia(self):
        """Parámetros de referencia para estructuración de proyectos."""
        self.parametros_referencia = {
            "confiabilidad": {
                "primaria": 90,
                "secundaria": 85,
                "terciaria": 80
            },
            "desviacion_estandar": {
                "asfaltico": 0.45,
                "concreto": 0.35
            },
            "perdida_serviciabilidad": {
                "asfaltico": 2.0,
                "concreto": 1.8
            }
        }


# ============================================================================
# 4. MOTOR DE DISEÑO MECÁNICO-EMPÍRICO
# ============================================================================

class DisenadorPavimentos:
    """Motor de diseño de pavimentos basado en el método mecánico-empírico
    (AASHTO 93 adaptado)."""

    def __init__(self, manual: ManualPavimentos):
        self.manual = manual

    def disenar(self, params: ParametrosPavimento) -> ResultadoDisenoPavimento:
        """Diseña la estructura de pavimento según el método mecánico-empírico."""
        restricciones: List[Dict[str, Any]] = []
        sugerencias: List[str] = []
        errores: List[str] = []

        # 1. Validar parámetros de entrada
        self._validar_entradas(params, errores, sugerencias)

        # 2. Determinar ESALs de diseño
        esals = self._calcular_esals_diseno(params)
        restricciones.append({
            "nombre": "ESALs de diseño",
            "valor": f"{esals:.2f} millones",
            "cumple": True
        })

        # 3-4. Diseñar según tipo de pavimento (el SN solo aplica al flexible; el rígido usa su propia ecuación)
        if params.tipo_pavimento == TipoPavimento.ASFALTICO:
            sn_requerido = self._calcular_sn(esals, params.cbr_subrasante)
            restricciones.append({
                "nombre": "Número Estructural Requerido (SN)",
                "valor": f"{sn_requerido:.2f}",
                "cumple": True
            })
            resultado = self._disenar_asfaltico(params, sn_requerido, restricciones, sugerencias, errores, esals)
        else:
            resultado = self._disenar_concreto(params, esals, restricciones, sugerencias, errores)

        # 5. Verificar espesores mínimos
        self._verificar_espesores_minimos(resultado, params, errores, esals)

        # 6. Generar sugerencias de optimización
        self._generar_sugerencias_optimizacion(resultado, params, sugerencias)

        cumple = len(errores) == 0
        sugerencias.append(AVISO_VALIDACION)
        mensaje = ("Diseño preliminar AASHTO-93 que cumple las verificaciones del motor (pendiente de validación por un ingeniero de pavimentos)"
                   if cumple else f"Se encontraron {len(errores)} errores: " + "; ".join(errores))

        return ResultadoDisenoPavimento(
            tipo_pavimento=params.tipo_pavimento.value,
            espesor_total=resultado["espesor_total"],
            espesor_rodadura=resultado["espesor_rodadura"],
            espesor_base=resultado["espesor_base"],
            espesor_subbase=resultado["espesor_subbase"],
            numero_estructural=resultado["numero_estructural"],
            espesor_equivalente_concreto=resultado["espesor_concreto"],
            cumple=cumple,
            mensaje=mensaje,
            restricciones=restricciones,
            sugerencias=sugerencias
        )

    def _validar_entradas(self, params: ParametrosPavimento, errores: List, sugerencias: List):
        """Valida los parámetros de entrada."""
        if params.cbr_subrasante < 3:
            errores.append(f"CBR de subrasante {params.cbr_subrasante}% es menor que el mínimo recomendado (3%)")
            sugerencias.append("Considere mejorar la subrasante con material de préstamo o estabilización")

        if params.ip_subrasante and params.ip_subrasante > 20:
            errores.append(f"Índice de plasticidad {params.ip_subrasante}% excede el máximo (20%)")
            sugerencias.append("La subrasante con IP > 20% es expansiva. Considere sustitución o estabilización con cal")

        if params.tpd < 50:
            sugerencias.append("Para tránsito muy bajo (<50 veh/día), considere el Manual de Bajos Volúmenes de Tránsito (2007)")

    def _calcular_esals_diseno(self, params: ParametrosPavimento) -> float:
        """Calcula los ESALs de diseño a partir del TPD y factores de crecimiento."""
        # Si el usuario proporcionó ESALs directamente, usarlos
        if params.esals_millones > 0:
            return params.esals_millones

        # Estimación simplificada: ESALs = TPD * 365 * factor_crecimiento * factor_camiones
        tpd = params.tpd
        if tpd < 100:
            factor_camiones = 0.05
        elif tpd < 1000:
            factor_camiones = 0.10
        elif tpd < 5000:
            factor_camiones = 0.15
        else:
            factor_camiones = 0.20

        # Período de diseño: 20 años
        crecimiento = 1.5  # Factor de crecimiento acumulado (20 años al 2.5%)
        esals = tpd * 365 * crecimiento * factor_camiones / 1_000_000
        return max(esals, 0.01)  # Mínimo 0.01 millones

    def _calcular_sn(self, esals_millones: float, cbr: float) -> float:
        """Calcula el Número Estructural requerido (SN) por tabla (ábacos
        AASHTO 93 adaptados), redondeando ESALs hacia arriba y CBR al más
        cercano disponible."""
        esals_round = min(
            [k for k in self.manual.sn_requerido.keys() if k >= esals_millones],
            default=max(self.manual.sn_requerido.keys())
        )

        cbrs = sorted(self.manual.sn_requerido[esals_round].keys())
        cbr_cercano = min(cbrs, key=lambda x: abs(x - cbr))

        sn = self.manual.sn_requerido[esals_round][cbr_cercano]

        if cbr != cbr_cercano and cbr in self.manual.sn_requerido[esals_round]:
            sn = self.manual.sn_requerido[esals_round][cbr]

        return sn

    def _disenar_asfaltico(self, params: ParametrosPavimento, sn_requerido: float,
                            restricciones: List, sugerencias: List, errores: List, esals: float) -> Dict:
        """Diseño de pavimento asfáltico (estructura flexible)."""
        # Coeficientes estructurales
        a1 = self.manual.coeficientes_estructurales["rodadura_asfaltica"]["a"]
        a2 = self.manual.coeficientes_estructurales["base_granular"]["a"]
        a3 = self.manual.coeficientes_estructurales["subbase_granular"]["a"]

        # Coeficientes de drenaje (asumir bueno)
        m2 = self.manual.coeficientes_drenaje["bueno"]
        m3 = self.manual.coeficientes_drenaje["bueno"]

        # Espesores mínimos: la rodadura depende del tránsito (#106)
        min_rodadura, fuente_rodadura = espesor_minimo_rodadura_asfaltica(esals)
        min_base = max(self.manual.espesores_minimos[TipoPavimento.ASFALTICO]["base"], ESPESOR_MINIMO_BASE_GRANULAR_CM)
        min_subbase = self.manual.espesores_minimos[TipoPavimento.ASFALTICO]["subbase"]
        restricciones.append({
            "nombre": "Rodadura asfáltica mínima por tránsito",
            "valor": f"{min_rodadura} cm",
            "fuente": fuente_rodadura,
            "cumple": True
        })

        # 1. Capa de rodadura: el mínimo por tránsito, o el espesor mayor que fije el ingeniero con `espesor_rodadura`.
        #    Se redondea hacia arriba a 0,5 cm: hacia abajo podía quedar bajo el mínimo.
        d1 = _techo(max(min_rodadura, params.espesor_rodadura or 0.0), 0.5)

        # 2. Capa base (mínimo 15 cm), hacia arriba a 2,5 cm
        d2 = _techo(max(min_base, params.espesor_base or 0.0), 2.5)

        # 3. Calcular SN aportado. Los a_i son por PULGADA: los espesores (cm) se convierten antes de multiplicar (issue #103).
        sn1 = a1 * d1 / CM_POR_PULGADA
        sn2 = a2 * (d2 / CM_POR_PULGADA) * m2

        # 4. Calcular SN restante para subbase
        sn_restante = sn_requerido - sn1 - sn2

        if sn_restante > 0:
            d3 = (sn_restante / (a3 * m3)) * CM_POR_PULGADA      # pulgadas -> cm
            d3 = max(min_subbase, d3)
        else:
            d3 = min_subbase
            # Si sobra SN, se puede reducir base o rodadura
            if sn1 + sn2 > sn_requerido:
                sugerencias.append("El espesor de base puede reducirse para optimizar costos")

        # La subbase (capa variable) se redondea HACIA ARRIBA a 2,5 cm: al más cercano podía dejar el SN real bajo el requerido.
        d3 = _techo(d3, 2.5)

        # Verificar espesores máximos
        max_rodadura = self.manual.espesores_maximos[TipoPavimento.ASFALTICO]["rodadura"]
        max_base = self.manual.espesores_maximos[TipoPavimento.ASFALTICO]["base"]
        max_subbase = self.manual.espesores_maximos[TipoPavimento.ASFALTICO]["subbase"]

        if d1 > max_rodadura:
            errores.append(f"Espesor de rodadura {d1} cm excede el máximo recomendado {max_rodadura} cm")
        if d2 > max_base:
            errores.append(f"Espesor de base {d2} cm excede el máximo recomendado {max_base} cm")
        if d3 > max_subbase:
            errores.append(f"Espesor de subbase {d3} cm excede el máximo recomendado {max_subbase} cm")

        # Calcular SN real (con espesores convertidos a pulgadas)
        sn_real = (a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3) / CM_POR_PULGADA

        # La subbase es la capa variable (como en el Manual INVIAS de bajos volúmenes); rodadura y base van en su mínimo por tránsito
        # salvo que el ingeniero las fije. No se optimiza el costo entre alternativas.
        if esals > 0.5 and not params.espesor_rodadura:
            sugerencias.append(f"Rodadura en su mínimo por tránsito ({fuente_rodadura}); la subbase completa el SN. "
                               "Para optimizar costos compare alternativas fijando `espesor_rodadura` y `espesor_base`.")

        restricciones.append({
            "nombre": "Número Estructural Real (SN)",
            "valor": f"{sn_real:.2f}",
            "requerido": f"{sn_requerido:.2f}",
            "cumple": sn_real >= sn_requerido
        })

        if sn_real < sn_requerido:
            errores.append(f"SN real ({sn_real:.2f}) es menor que el requerido ({sn_requerido:.2f})")

        return {
            "espesor_total": d1 + d2 + d3,
            "espesor_rodadura": d1,
            "espesor_base": d2,
            "espesor_subbase": d3,
            "numero_estructural": sn_real,
            "espesor_concreto": 0
        }

    def _disenar_concreto(self, params: ParametrosPavimento, esals: float,
                           restricciones: List, sugerencias: List, errores: List) -> Dict:
        """Pavimento de concreto simple con juntas (JPCP): espesor de losa con la ecuación AASHTO-93 para rígidos (#106)."""
        min_rodadura = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["rodadura"]
        min_base = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["base"]
        min_subbase = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["subbase"]

        # Base y subbase bajo concreto
        d2 = max(min_base, params.espesor_base or 0.0)
        d3 = max(min_subbase, params.espesor_subbase or 0.0)
        max_base = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["base"]
        max_subbase = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["subbase"]
        if d2 > max_base:
            errores.append(f"Espesor de base {d2} cm excede el máximo recomendado {max_base} cm")
        if d3 > max_subbase:
            errores.append(f"Espesor de subbase {d3} cm excede el máximo recomendado {max_subbase} cm")

        faltan = [n for n, v in (("modulo_reaccion_k (k, MPa/m)", params.modulo_reaccion_k),
                                 ("modulo_rotura_concreto (S'c, MPa)", params.modulo_rotura_concreto)) if v is None]
        if faltan:
            errores.append("La ecuación AASHTO-93 de pavimento rígido exige " + " y ".join(faltan) +
                           ": el motor no los supone. k se obtiene del ensayo de placa (INV E-168) o de una correlación "
                           "justificada por el ingeniero; S'c del ensayo de flexión en vigas (INV E-414).")
            return {"espesor_total": d2 + d3, "espesor_rodadura": 0.0, "espesor_base": d2, "espesor_subbase": d3,
                    "numero_estructural": 0.0, "espesor_concreto": 0.0}

        confiabilidad = params.confiabilidad
        if confiabilidad is None:
            confiabilidad = float(self.manual.parametros_referencia["confiabilidad"][params.tipo_via.value])
        entradas = dict(
            k_MPa_m=params.modulo_reaccion_k, Sc_MPa=params.modulo_rotura_concreto,
            Ec_MPa=params.modulo_elastico_concreto or rig.EC_POR_DEFECTO_MPA,
            J=params.coeficiente_transferencia_j, Cd=params.coeficiente_drenaje_cd, confiabilidad_pct=confiabilidad,
            So=self.manual.parametros_referencia["desviacion_estandar"]["concreto"],
            p0=4.5, pt=params.serviciabilidad_final,
        )
        try:
            losa = rig.espesor_losa(esals, **entradas)
        except ValueError as e:
            errores.append(str(e))
            return {"espesor_total": d2 + d3, "espesor_rodadura": 0.0, "espesor_base": d2, "espesor_subbase": d3,
                    "numero_estructural": 0.0, "espesor_concreto": 0.0}

        # Hacia arriba a 1 cm (el catálogo INVIAS da espesores en cm enteros); nunca por debajo del mínimo
        d_concreto = _techo(max(min_rodadura, losa.D_cm), 1.0)
        w18_adm = rig.w18_admisible_millones(d_concreto, **entradas)

        restricciones.append({
            "nombre": "Espesor de losa (ecuación AASHTO-93 de pavimento rígido)",
            "valor": f"{d_concreto:g} cm",
            "requerido": f"{losa.D_cm:.2f} cm",
            "requerido_minimo": f"{min_rodadura} cm",
            "cumple": d_concreto >= losa.D_cm and d_concreto >= min_rodadura
        })
        restricciones.append({
            "nombre": "ESAL admisibles por la losa (AASHTO-93)",
            "valor": f"{w18_adm:.2f} millones",
            "requerido": f"{esals:.2f} millones",
            "cumple": w18_adm >= esals * (1 - 1e-9)
        })
        sugerencias.extend(losa.supuestos)
        if params.confiabilidad is None:
            sugerencias.append(f"Confiabilidad R = {confiabilidad:g} % tomada por defecto para vía {params.tipo_via.value}; "
                               "fíjela según la importancia de la vía (AASHTO-93, Parte I, cap. 4)")
        if params.esals_millones <= 0:
            sugerencias.append("Los ESAL se estimaron a partir del TPD con factores simplificados: para concreto deben "
                               "calcularse con factores de equivalencia de pavimento rígido")

        max_rodadura = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["rodadura"]
        if d_concreto > max_rodadura:
            errores.append(f"Espesor de losa {d_concreto:g} cm excede el máximo recomendado {max_rodadura} cm")
            sugerencias.append("Revise k, S'c y la transferencia de carga, o considere otra estructura")

        sugerencias.append(f"Para losa de {d_concreto:g} cm: losas de 3,6 a 5,0 m de largo con relación largo/ancho "
                           "entre 1 y 1,3 (Manual INVIAS de concreto §3.5); la transferencia de carga supuesta es J = "
                           f"{params.coeficiente_transferencia_j:g}")

        return {
            "espesor_total": d_concreto + d2 + d3,
            "espesor_rodadura": d_concreto,
            "espesor_base": d2,
            "espesor_subbase": d3,
            "numero_estructural": 0.0,
            "espesor_concreto": d_concreto
        }

    def _verificar_espesores_minimos(self, resultado: Dict, params: ParametrosPavimento, errores: List, esals: float):
        """Verifica que todos los espesores cumplan los mínimos (la rodadura asfáltica, según el tránsito)."""
        min_espesores = dict(self.manual.espesores_minimos[params.tipo_pavimento])
        if params.tipo_pavimento == TipoPavimento.ASFALTICO:
            min_espesores["rodadura"] = espesor_minimo_rodadura_asfaltica(esals)[0]
            min_espesores["base"] = max(min_espesores["base"], ESPESOR_MINIMO_BASE_GRANULAR_CM)
        elif resultado["espesor_concreto"] == 0.0:
            return                     # no se calculó la losa: el error ya está registrado

        for capa, minimo in min_espesores.items():
            clave = f"espesor_{capa}"
            if clave in resultado:
                if resultado[clave] < minimo:
                    errores.append(f"Espesor de {capa} ({resultado[clave]} cm) es menor que el mínimo {minimo} cm")

    def _generar_sugerencias_optimizacion(self, resultado: Dict, params: ParametrosPavimento, sugerencias: List):
        """Genera sugerencias de optimización del diseño."""
        if params.tipo_pavimento == TipoPavimento.ASFALTICO:
            if resultado["espesor_rodadura"] > 15:
                sugerencias.append("Considere reducir el espesor de rodadura si el tránsito no lo requiere")
            if resultado["espesor_base"] > 30:
                sugerencias.append("Para espesores de base > 30 cm, considere usar dos capas de base con diferentes materiales")
        else:
            if resultado["espesor_concreto"] > 30:
                sugerencias.append("Para losas > 30 cm, evalúe el uso de concreto reforzado o losas postensadas")

        # Sugerencia sobre subrasante
        if params.cbr_subrasante < 5:
            sugerencias.append("Subrasante con CBR < 5%. Considere sobrecarga o mejora con material granular")

        # Sugerencia sobre drenaje
        sugerencias.append("Verifique el sistema de drenaje para garantizar la vida útil del pavimento")


if __name__ == "__main__":
    manual = ManualPavimentos()
    disenador = DisenadorPavimentos(manual)

    params_asfaltico = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.ASFALTICO,
        tipo_via=TipoVia.PRIMARIA,
        tpd=5000,
        esals_millones=5.0,
        cbr_subrasante=5,
        ip_subrasante=15,
        temperatura_media=22,
        espesor_base=20,
        espesor_subbase=15
    )
    resultado = disenador.disenar(params_asfaltico)
    print(f"Resultado: {resultado.mensaje}")
    print(f"  Espesor total: {resultado.espesor_total:.1f} cm")
    print(f"  Rodadura: {resultado.espesor_rodadura:.1f} cm | Base: {resultado.espesor_base:.1f} cm | Subbase: {resultado.espesor_subbase:.1f} cm")
    print(f"  SN real: {resultado.numero_estructural:.2f}")

    params_concreto = ParametrosPavimento(
        tipo_pavimento=TipoPavimento.CONCRETO,
        tipo_via=TipoVia.PRIMARIA,
        tpd=8000,
        esals_millones=10.0,
        cbr_subrasante=8,
        ip_subrasante=10,
        espesor_base=15,
        espesor_subbase=15,
        modulo_reaccion_k=60.0,
        modulo_rotura_concreto=4.2,
    )
    resultado_concreto = disenador.disenar(params_concreto)
    print(f"\nResultado: {resultado_concreto.mensaje}")
    print(f"  Losa de concreto: {resultado_concreto.espesor_rodadura:.1f} cm")
    print(f"  Base: {resultado_concreto.espesor_base:.1f} cm | Subbase: {resultado_concreto.espesor_subbase:.1f} cm")
