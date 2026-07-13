"""
Diseño estructural de pavimentos (AASHTO 93, adaptado - Manual INVIAS, método
mecánico-empírico). ESALs de diseño, Número Estructural (SN) y espesores de
capas para pavimentos asfálticos (flexibles) y de concreto (rígidos).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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

        # Coeficientes estructurales para capas (a_i)
        self.coeficientes_estructurales = {
            "rodadura_asfaltica": {
                "tipo": "asfaltico",
                "a": 0.44,           # Coeficiente estructural (1/cm)
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

        # 3. Calcular número estructural requerido (SN)
        sn_requerido = self._calcular_sn(esals, params.cbr_subrasante)
        restricciones.append({
            "nombre": "Número Estructural Requerido (SN)",
            "valor": f"{sn_requerido:.2f}",
            "cumple": True
        })

        # 4. Diseñar según tipo de pavimento
        if params.tipo_pavimento == TipoPavimento.ASFALTICO:
            resultado = self._disenar_asfaltico(params, sn_requerido, restricciones, sugerencias, errores)
        else:
            resultado = self._disenar_concreto(params, sn_requerido, restricciones, sugerencias, errores)

        # 5. Verificar espesores mínimos
        self._verificar_espesores_minimos(resultado, params, errores)

        # 6. Generar sugerencias de optimización
        self._generar_sugerencias_optimizacion(resultado, params, sugerencias)

        cumple = len(errores) == 0
        mensaje = "Diseño válido según el Manual de Pavimentos INVIAS" if cumple else f"Se encontraron {len(errores)} errores"

        return ResultadoDisenoPavimento(
            tipo_pavimento=params.tipo_pavimento.value,
            espesor_total=resultado.get("espesor_total", 0),
            espesor_rodadura=resultado.get("espesor_rodadura", 0),
            espesor_base=resultado.get("espesor_base", 0),
            espesor_subbase=resultado.get("espesor_subbase", 0),
            numero_estructural=resultado.get("numero_estructural", sn_requerido),
            espesor_equivalente_concreto=resultado.get("espesor_concreto", 0),
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
                            restricciones: List, sugerencias: List, errores: List) -> Dict:
        """Diseño de pavimento asfáltico (estructura flexible)."""
        # Coeficientes estructurales
        a1 = self.manual.coeficientes_estructurales["rodadura_asfaltica"]["a"]
        a2 = self.manual.coeficientes_estructurales["base_granular"]["a"]
        a3 = self.manual.coeficientes_estructurales["subbase_granular"]["a"]

        # Coeficientes de drenaje (asumir bueno)
        m2 = self.manual.coeficientes_drenaje["bueno"]
        m3 = self.manual.coeficientes_drenaje["bueno"]

        # Espesores mínimos
        min_rodadura = self.manual.espesores_minimos[TipoPavimento.ASFALTICO]["rodadura"]
        min_base = self.manual.espesores_minimos[TipoPavimento.ASFALTICO]["base"]
        min_subbase = self.manual.espesores_minimos[TipoPavimento.ASFALTICO]["subbase"]

        # 1. Capa de rodadura (mínimo 5 cm)
        d1 = max(min_rodadura, 5.0)

        # 2. Capa base (mínimo 15 cm)
        d2 = max(min_base, params.espesor_base if params.espesor_base else 15.0)

        # 3. Calcular SN aportado
        sn1 = a1 * d1
        sn2 = a2 * d2 * m2

        # 4. Calcular SN restante para subbase
        sn_restante = sn_requerido - sn1 - sn2

        if sn_restante > 0:
            d3 = sn_restante / (a3 * m3)
            d3 = max(min_subbase, d3)
        else:
            d3 = min_subbase
            # Si sobra SN, se puede reducir base o rodadura
            if sn1 + sn2 > sn_requerido:
                sugerencias.append("El espesor de base puede reducirse para optimizar costos")

        # Redondear a múltiplos de 2.5 cm (práctica común)
        d1 = round(d1 / 2.5) * 2.5
        d2 = round(d2 / 2.5) * 2.5
        d3 = round(d3 / 2.5) * 2.5

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

        # Calcular SN real
        sn_real = a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3

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

    def _disenar_concreto(self, params: ParametrosPavimento, sn_requerido: float,
                           restricciones: List, sugerencias: List, errores: List) -> Dict:
        """Diseño de pavimento de concreto (estructura rígida)."""
        # Espesor mínimo de losa de concreto
        min_rodadura = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["rodadura"]
        min_base = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["base"]
        min_subbase = self.manual.espesores_minimos[TipoPavimento.CONCRETO]["subbase"]

        # Factor de conversión SN -> espesor de concreto (aproximado)
        # D_concreto = SN / 0.39
        d_concreto = sn_requerido / 0.39
        d_concreto = max(min_rodadura, d_concreto)

        # Redondear a múltiplos de 2.5 cm
        d_concreto = round(d_concreto / 2.5) * 2.5

        # Verificar espesor máximo
        max_rodadura = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["rodadura"]
        if d_concreto > max_rodadura:
            errores.append(f"Espesor de losa {d_concreto} cm excede el máximo recomendado {max_rodadura} cm")
            sugerencias.append("Considere losa con refuerzo continuo o diseño de espesor variable")

        # Base y subbase bajo concreto (opcionales)
        d2 = params.espesor_base if params.espesor_base else min_base
        d2 = max(min_base, d2)
        d3 = params.espesor_subbase if params.espesor_subbase else min_subbase
        d3 = max(min_subbase, d3)

        # Verificar máximos
        max_base = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["base"]
        max_subbase = self.manual.espesores_maximos[TipoPavimento.CONCRETO]["subbase"]
        if d2 > max_base:
            errores.append(f"Espesor de base {d2} cm excede el máximo recomendado {max_base} cm")
        if d3 > max_subbase:
            errores.append(f"Espesor de subbase {d3} cm excede el máximo recomendado {max_subbase} cm")

        restricciones.append({
            "nombre": "Espesor de losa de concreto",
            "valor": f"{d_concreto} cm",
            "requerido_minimo": f"{min_rodadura} cm",
            "cumple": d_concreto >= min_rodadura
        })

        # Sugerencia sobre juntas
        sugerencias.append(f"Para losa de {d_concreto} cm, considerar juntas cada 4-5 m y barras de transferencia")

        return {
            "espesor_total": d_concreto + d2 + d3,
            "espesor_rodadura": d_concreto,
            "espesor_base": d2,
            "espesor_subbase": d3,
            "numero_estructural": sn_requerido,
            "espesor_concreto": d_concreto
        }

    def _verificar_espesores_minimos(self, resultado: Dict, params: ParametrosPavimento, errores: List):
        """Verifica que todos los espesores cumplan los mínimos del manual."""
        min_espesores = self.manual.espesores_minimos[params.tipo_pavimento]

        for capa, minimo in min_espesores.items():
            clave = f"espesor_{capa}"
            if clave in resultado:
                if resultado[clave] < minimo:
                    errores.append(f"Espesor de {capa} ({resultado[clave]} cm) es menor que el mínimo {minimo} cm")

    def _generar_sugerencias_optimizacion(self, resultado: Dict, params: ParametrosPavimento, sugerencias: List):
        """Genera sugerencias de optimización del diseño."""
        if params.tipo_pavimento == TipoPavimento.ASFALTICO:
            if resultado.get("espesor_rodadura", 0) > 15:
                sugerencias.append("Considere reducir el espesor de rodadura si el tránsito no lo requiere")
            if resultado.get("espesor_base", 0) > 30:
                sugerencias.append("Para espesores de base > 30 cm, considere usar dos capas de base con diferentes materiales")
        else:
            if resultado.get("espesor_concreto", 0) > 30:
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
        espesor_subbase=15
    )
    resultado_concreto = disenador.disenar(params_concreto)
    print(f"\nResultado: {resultado_concreto.mensaje}")
    print(f"  Losa de concreto: {resultado_concreto.espesor_rodadura:.1f} cm")
    print(f"  Base: {resultado_concreto.espesor_base:.1f} cm | Subbase: {resultado_concreto.espesor_subbase:.1f} cm")
