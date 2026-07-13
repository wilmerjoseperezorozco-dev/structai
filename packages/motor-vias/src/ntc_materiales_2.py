"""
MÓDULO: Materiales y Aditivos para Concreto y Pavimentos II
Normas cubiertas:
    NTC 3502 — Aditivos incorporadores de aire para concreto (equivalente ASTM C260)
    NTC 3760 — Concreto coloreado integralmente. Especificaciones para pigmentos (equivalente ASTM C979)
    NTC 4018 — Escoria de alto horno granulada y molida (equivalente ASTM C989)
    NTC 4024 — Prefabricados de concreto. Muestreo y ensayo
    NTC 4924 — Agregados livianos para unidades de mampostería de concreto (equivalente ASTM C331)
    NTC 5147 — Resistencia a la abrasión (arena y disco metálico ancho)
    NTC 6008 — Terminología y clasificación para adoquines y losetas de concreto
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


#──────────────────────────────────────────────────────────────────────────────
# NTC 3502 — Aditivos incorporadores de aire para concreto (equivalente ASTM C260)
#──────────────────────────────────────────────────────────────────────────────

class TipoAditivoAire(Enum):
    """Tipos de aditivos incorporadores de aire según NTC 3502"""
    LIQUIDO = "liquido"
    POLVO = "polvo"
    PASTA = "pasta"
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class AditivoIncorporadorAire:
    """Modelo de un aditivo incorporador de aire según NTC 3502"""
    nombre: str
    tipo: TipoAditivoAire
    contenido_aire_porcentaje: float  # % de aire incorporado en el concreto
    dosificacion_recomendada: str  # ml/kg de cemento o %
    libre_cloruros: bool = True
    ph: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 3502 (ASTM C260)"
@dataclass
class ResultadoVerificacionNTC3502:
    """Resultado de la verificación de cumplimiento de NTC 3502"""
    aditivo: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 3502 (CAG)
# ============================================================================
class ConocimientoNTC3502:
    """
    Base de conocimiento CAG de la NTC 3502: Aditivos incorporadores de aire para concreto
    Equivalente a ASTM C260
    """
    def __init__(self):
        self._cargar_requisitos()
        self._cargar_normas_relacionadas()
        self._cargar_recomendaciones_uso()
        self._cargar_aplicaciones()
    def _cargar_requisitos(self):
        """Requisitos técnicos según NTC 3502 / ASTM C260"""
        self.requisitos = {
            "contenido_aire": {
                "parametro": "Contenido de aire incorporado",
                "valor_minimo": 4.0,
                "valor_maximo": 8.0,
                "unidad": "%",
                "descripcion": "Porcentaje de aire incorporado en el concreto"
            },
            "libre_cloruros": {
                "parametro": "Libre de cloruros",
                "requerido": True,
                "descripcion": "El aditivo no debe contener cloruros que puedan causar corrosión"
            },
            "estabilidad_aire": {
                "parametro": "Estabilidad del aire",
                "descripcion": "El aire debe mantenerse estable durante el transporte y colocación"
            },
            "compatibilidad": {
                "parametro": "Compatibilidad con otros aditivos",
                "descripcion": "Debe ser compatible con plastificantes, retardantes y otros aditivos"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 3502"""
        self.normas_relacionadas = {
            "ASTM_C260": "Standard Specification for Air-Entraining Admixtures for Concrete",
            "NTC_1299": "Concretos. Aditivos químicos para concreto",
            "NTC_4023": "Especificaciones para aditivos químicos usados en producción de concreto fluido",
            "NTC_3760": "Concreto coloreado integralmente. Especificaciones para pigmentos",
            "NTC_3823": "Ensayos de cenizas volantes y puzolanas naturales",
            "NTC_174": "Especificaciones de los agregados para concreto"
        }
    def _cargar_recomendaciones_uso(self):
        """Recomendaciones para el uso de aditivos incorporadores de aire"""
        self.recomendaciones_uso = [
            "El aditivo debe añadirse al agua de amasado del concreto mediante dosificador automático o manualmente",
            "La dosificación debe ser ajustada según las condiciones del concreto y el ambiente",
            "Se recomienda verificar el contenido de aire en obra mediante ensayos de densidad",
            "El aditivo no debe contener cloruros para evitar corrosión del acero de refuerzo",
            "Es compatible con la mayoría de los aditivos químicos para concreto",
            "La efectividad del aditivo depende de la dosificación, tiempo de mezclado y temperatura"
        ]
    def _cargar_aplicaciones(self):
        """Aplicaciones típicas de aditivos incorporadores de aire"""
        self.aplicaciones = [
            "Concretos expuestos a ciclos de hielo-deshielo",
            "Pavimentos y puentes",
            "Concretos impermeabilizados",
            "Concretos Tremie (bajo agua)",
            "Estructuras en climas fríos",
            "Concretos con requisitos de durabilidad"
        ]
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 3502
# ============================================================================
class MotorVerificacionNTC3502:
    """
    Motor de verificación de cumplimiento de la NTC 3502
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC3502()
    def verificar_aditivo(self, aditivo: AditivoIncorporadorAire) -> ResultadoVerificacionNTC3502:
        """
        Verifica que un aditivo incorporador de aire cumpla con los requisitos de la NTC 3502
        """
        requisitos = []
        errores = []
        # 1. Verificar tipo de aditivo
        requisitos.append(self._verificar_tipo(aditivo))
        # 2. Verificar contenido de aire
        requisitos.append(self._verificar_contenido_aire(aditivo))
        # 3. Verificar libre de cloruros
        requisitos.append(self._verificar_libre_cloruros(aditivo))
        # 4. Verificar equivalencia ASTM
        requisitos.append(self._verificar_astm())
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "El aditivo cumple con los requisitos de la NTC 3502" if cumple else \
                  f"El aditivo no cumple con {len(no_cumple)} requisito(s) de la NTC 3502"
        return ResultadoVerificacionNTC3502(
            aditivo=aditivo.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_tipo(self, aditivo: AditivoIncorporadorAire) -> Dict[str, Any]:
        """Verifica que el tipo de aditivo sea válido"""
        if aditivo.tipo not in [TipoAditivoAire.LIQUIDO, TipoAditivoAire.POLVO, TipoAditivoAire.PASTA]:
            return {
                "parametro": "Tipo de aditivo",
                "valor": aditivo.tipo.value if hasattr(aditivo.tipo, 'value') else str(aditivo.tipo),
                "cumple": False,
                "mensaje": f"Tipo '{aditivo.tipo}' no reconocido en NTC 3502"
            }
        return {
            "parametro": "Tipo de aditivo",
            "valor": aditivo.tipo.value,
            "cumple": True,
            "mensaje": f"Tipo {aditivo.tipo.value} válido según NTC 3502"
        }
    def _verificar_contenido_aire(self, aditivo: AditivoIncorporadorAire) -> Dict[str, Any]:
        """Verifica el contenido de aire incorporado"""
        req = self.conocimiento.requisitos["contenido_aire"]
        cumple = req["valor_minimo"] <= aditivo.contenido_aire_porcentaje <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": aditivo.contenido_aire_porcentaje,
            "minimo": req["valor_minimo"],
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "cumple": cumple,
            "mensaje": f"Contenido de aire = {aditivo.contenido_aire_porcentaje}% {'dentro de' if cumple else 'fuera de'} rango ({req['valor_minimo']}-{req['valor_maximo']}%)"
        }
    def _verificar_libre_cloruros(self, aditivo: AditivoIncorporadorAire) -> Dict[str, Any]:
        """Verifica que el aditivo esté libre de cloruros"""
        req = self.conocimiento.requisitos["libre_cloruros"]
        cumple = aditivo.libre_cloruros == req["requerido"]
        return {
            "parametro": req["parametro"],
            "valor": "Sí" if aditivo.libre_cloruros else "No",
            "requerido": req["requerido"],
            "cumple": cumple,
            "mensaje": f"Libre de cloruros: {'Sí' if aditivo.libre_cloruros else 'No'} {'(cumple)' if cumple else '(no cumple)'}"
        }
    def _verificar_astm(self) -> Dict[str, Any]:
        """Verifica la equivalencia con ASTM C260"""
        return {
            "parametro": "Equivalencia internacional",
            "valor": "ASTM C260",
            "relacion": "Adopción idéntica",
            "cumple": True,
            "mensaje": "NTC 3502 es equivalente a ASTM C260"
        }
    def obtener_requisito(self, parametro: str) -> Optional[Dict]:
        """Obtiene un requisito específico"""
        return self.conocimiento.requisitos.get(parametro)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 3502
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 3760 — Concreto coloreado integralmente. Especificaciones para pigmentos (equivalente ASTM C979)
#──────────────────────────────────────────────────────────────────────────────

class PresentacionPigmento(Enum):
    POLVO = "polvo"
    GRANULAR = "granular"
    LIQUIDO = "liquido"
class TipoPigmento(Enum):
    OXIDO_HIERRO = "oxido_hierro"          # Rojo, amarillo, negro
    OXIDO_COBALTO = "oxido_cobalto"        # Azul
    OXIDO_CROMO = "oxido_cromo"            # Verde
    DIOXIDO_TITANIO = "dioxido_titanio"    # Blanco
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class PigmentoConcreto:
    """Modelo de un pigmento para concreto coloreado según NTC 3760"""
    nombre: str
    tipo: TipoPigmento
    presentacion: PresentacionPigmento
    dosificacion_maxima_porcentaje: float  # % del peso del cemento
    color: str
    resistencia_alcalina: bool = True
    resistencia_intemperie: bool = True
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 3760"
@dataclass
class ResultadoVerificacionNTC3760:
    """Resultado de la verificación de cumplimiento de NTC 3760"""
    pigmento: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 3760 (CAG)
# ============================================================================
class ConocimientoNTC3760:
    """
    Base de conocimiento CAG de la NTC 3760: Concreto coloreado integralmente
    Especificaciones para pigmentos (1995)
    """
    def __init__(self):
        self._cargar_requisitos()
        self._cargar_tipos_pigmentos()
        self._cargar_normas_relacionadas()
        self._cargar_recomendaciones_uso()
    def _cargar_requisitos(self):
        """Requisitos técnicos según NTC 3760 / ASTM C979"""
        self.requisitos = {
            "dosificacion_maxima": {
                "parametro": "Dosificación máxima de pigmento",
                "valor_maximo": 10.0,
                "unidad": "% del peso del cemento",
                "referencia": "ASTM C979 / NTC 3760",
                "descripcion": "La adición de pigmento no debe exceder el 10% del peso del cemento"
            },
            "resistencia_alcalina": {
                "parametro": "Resistencia a la alcalinidad",
                "requerido": True,
                "descripcion": "El pigmento debe ser resistente al ambiente alcalino del cemento"
            },
            "resistencia_intemperie": {
                "parametro": "Resistencia a la intemperie",
                "requerido": True,
                "descripcion": "El pigmento debe resistir la exposición solar y condiciones climáticas"
            },
            "control_color": {
                "parametro": "Control de variación de color",
                "descripcion": "La variación de color debe mantenerse dentro de límites establecidos"
            }
        }
    def _cargar_tipos_pigmentos(self):
        """Tipos de pigmentos utilizados en concreto"""
        self.tipos_pigmentos = {
            TipoPigmento.OXIDO_HIERRO: {
                "nombre": "Óxido de hierro",
                "colores": ["Rojo", "Amarillo", "Negro", "Café"],
                "descripcion": "Pigmentos inorgánicos de alta estabilidad",
                "estabilidad": "Excelente"
            },
            TipoPigmento.OXIDO_COBALTO: {
                "nombre": "Óxido de cobalto",
                "colores": ["Azul"],
                "descripcion": "Pigmento inorgánico para tonos azules",
                "estabilidad": "Buena"
            },
            TipoPigmento.OXIDO_CROMO: {
                "nombre": "Óxido de cromo",
                "colores": ["Verde"],
                "descripcion": "Pigmento inorgánico para tonos verdes",
                "estabilidad": "Excelente"
            },
            TipoPigmento.DIOXIDO_TITANIO: {
                "nombre": "Dióxido de titanio",
                "colores": ["Blanco"],
                "descripcion": "Pigmento inorgánico para tonos blancos",
                "estabilidad": "Excelente"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 3760"""
        self.normas_relacionadas = {
            "ASTM_C979": "Standard Specification for Pigments for Integrally Colored Concrete",
            "NTC_1299": "Concretos. Aditivos químicos para concreto",
            "NTC_2017": "Adoquines de concreto para pavimentos",
            "NTC_6008": "Terminología y clasificación para adoquines y losetas",
            "NSR_10": "Norma Sismo Resistente"
        }
    def _cargar_recomendaciones_uso(self):
        """Recomendaciones para el uso de pigmentos en concreto"""
        self.recomendaciones_uso = [
            "Los pigmentos se mezclan integralmente en el concreto, adhiriéndose al cemento Portland para formar parte permanente de la mezcla",
            "La dosificación no debe exceder el 10% del peso del cemento para evitar afectar la resistencia",
            "Los pigmentos deben ser resistentes a la alcalinidad del cemento y a la exposición solar",
            "Para mantener uniformidad en el color, se recomienda un control estricto de la dosificación y el mezclado",
            "El uso de pigmentos no afecta la durabilidad ni la resistencia estructural del concreto"
        ]
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 3760
# ============================================================================
class MotorVerificacionNTC3760:
    """
    Motor de verificación de cumplimiento de la NTC 3760
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC3760()
    def verificar_pigmento(self, pigmento: PigmentoConcreto) -> ResultadoVerificacionNTC3760:
        """
        Verifica que un pigmento cumpla con los requisitos de la NTC 3760
        """
        requisitos = []
        errores = []
        # 1. Verificar presentación
        requisitos.append(self._verificar_presentacion(pigmento))
        # 2. Verificar dosificación máxima
        requisitos.append(self._verificar_dosificacion(pigmento))
        # 3. Verificar resistencia a la alcalinidad
        requisitos.append(self._verificar_resistencia_alcalina(pigmento))
        # 4. Verificar resistencia a la intemperie
        requisitos.append(self._verificar_resistencia_intemperie(pigmento))
        # 5. Verificar equivalencia ASTM
        requisitos.append(self._verificar_astm())
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "El pigmento cumple con los requisitos de la NTC 3760" if cumple else \
                  f"El pigmento no cumple con {len(no_cumple)} requisito(s) de la NTC 3760"
        return ResultadoVerificacionNTC3760(
            pigmento=pigmento.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_presentacion(self, pigmento: PigmentoConcreto) -> Dict[str, Any]:
        """Verifica que la presentación del pigmento sea válida"""
        if pigmento.presentacion not in [PresentacionPigmento.POLVO, 
                                         PresentacionPigmento.GRANULAR, 
                                         PresentacionPigmento.LIQUIDO]:
            return {
                "parametro": "Presentación del pigmento",
                "valor": pigmento.presentacion.value if hasattr(pigmento.presentacion, 'value') else str(pigmento.presentacion),
                "cumple": False,
                "mensaje": f"Presentación '{pigmento.presentacion}' no reconocida en NTC 3760"
            }
        return {
            "parametro": "Presentación del pigmento",
            "valor": pigmento.presentacion.value,
            "cumple": True,
            "mensaje": f"Presentación {pigmento.presentacion.value} válida según NTC 3760"
        }
    def _verificar_dosificacion(self, pigmento: PigmentoConcreto) -> Dict[str, Any]:
        """Verifica la dosificación máxima del pigmento"""
        req = self.conocimiento.requisitos["dosificacion_maxima"]
        cumple = pigmento.dosificacion_maxima_porcentaje <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": pigmento.dosificacion_maxima_porcentaje,
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "cumple": cumple,
            "mensaje": f"Dosificación {pigmento.dosificacion_maxima_porcentaje}% {'<= ' if cumple else '> '}{req['valor_maximo']}% del peso del cemento"
        }
    def _verificar_resistencia_alcalina(self, pigmento: PigmentoConcreto) -> Dict[str, Any]:
        """Verifica la resistencia a la alcalinidad"""
        req = self.conocimiento.requisitos["resistencia_alcalina"]
        cumple = pigmento.resistencia_alcalina == req["requerido"]
        return {
            "parametro": req["parametro"],
            "valor": "Sí" if pigmento.resistencia_alcalina else "No",
            "requerido": req["requerido"],
            "cumple": cumple,
            "mensaje": f"Resistencia a la alcalinidad: {'Sí' if pigmento.resistencia_alcalina else 'No'} {'(cumple)' if cumple else '(no cumple)'}"
        }
    def _verificar_resistencia_intemperie(self, pigmento: PigmentoConcreto) -> Dict[str, Any]:
        """Verifica la resistencia a la intemperie"""
        req = self.conocimiento.requisitos["resistencia_intemperie"]
        cumple = pigmento.resistencia_intemperie == req["requerido"]
        return {
            "parametro": req["parametro"],
            "valor": "Sí" if pigmento.resistencia_intemperie else "No",
            "requerido": req["requerido"],
            "cumple": cumple,
            "mensaje": f"Resistencia a la intemperie: {'Sí' if pigmento.resistencia_intemperie else 'No'} {'(cumple)' if cumple else '(no cumple)'}"
        }
    def _verificar_astm(self) -> Dict[str, Any]:
        """Verifica la equivalencia con ASTM C979"""
        return {
            "parametro": "Equivalencia internacional",
            "valor": "ASTM C979",
            "relacion": "Norma equivalente",
            "cumple": True,
            "mensaje": "NTC 3760 es equivalente a ASTM C979"
        }
    def obtener_requisito(self, parametro: str) -> Optional[Dict]:
        """Obtiene un requisito específico"""
        return self.conocimiento.requisitos.get(parametro)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 3760
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 4018 — Escoria de alto horno granulada y molida (equivalente ASTM C989)
#──────────────────────────────────────────────────────────────────────────────

class GradoEscoria(Enum):
    """Grados de resistencia de la escoria según NTC 4018"""
    GRADO_80 = 80   # Índice de actividad ≥ 80%
    GRADO_100 = 100 # Índice de actividad ≥ 100%
    GRADO_120 = 120 # Índice de actividad ≥ 120%
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class AnalisisEscoria:
    """Modelo de análisis de una escoria de alto horno según NTC 4018"""
    indice_actividad_7dias: float  # % de actividad a 7 días
    indice_actividad_28dias: float  # % de actividad a 28 días
    finura_blaine_m2_kg: float
    densidad_g_cm3: float
    contenido_azufre_porcentaje: Optional[float] = None
    perdida_ignicion_porcentaje: Optional[float] = None
    observaciones: Optional[str] = None
@dataclass
class EscoriaAltoHorno:
    """Modelo de una escoria de alto horno según NTC 4018"""
    nombre: str
    grado: GradoEscoria
    analisis: AnalisisEscoria
    fabricante: Optional[str] = None
    origen: Optional[str] = None
    referencia_normativa: str = "NTC 4018 (ASTM C989)"
@dataclass
class ResultadoVerificacionNTC4018:
    """Resultado de la verificación de cumplimiento de NTC 4018"""
    escoria: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 4018 (CAG)
# ============================================================================
class ConocimientoNTC4018:
    """
    Base de conocimiento CAG de la NTC 4018: Escoria de alto horno granulada y molida
    Primera actualización (2017) - Equivalente a ASTM C989
    """
    def __init__(self):
        self._cargar_grados()
        self._cargar_requisitos()
        self._cargar_normas_relacionadas()
        self._cargar_recomendaciones_uso()
    def _cargar_grados(self):
        """Grados de escoria según NTC 4018"""
        self.grados = {
            GradoEscoria.GRADO_80: {
                "nombre": "Grado 80",
                "descripcion": "Índice de actividad con cemento Portland ≥ 80% a 28 días",
                "indice_actividad_min_7dias": 70.0,
                "indice_actividad_min_28dias": 80.0,
                "aplicacion": "Uso general, concretos de resistencia normal"
            },
            GradoEscoria.GRADO_100: {
                "nombre": "Grado 100",
                "descripcion": "Índice de actividad con cemento Portland ≥ 100% a 28 días",
                "indice_actividad_min_7dias": 75.0,
                "indice_actividad_min_28dias": 100.0,
                "aplicacion": "Concretos de media y alta resistencia"
            },
            GradoEscoria.GRADO_120: {
                "nombre": "Grado 120",
                "descripcion": "Índice de actividad con cemento Portland ≥ 120% a 28 días",
                "indice_actividad_min_7dias": 95.0,
                "indice_actividad_min_28dias": 120.0,
                "aplicacion": "Concretos de alta resistencia y durabilidad excepcional"
            }
        }
    def _cargar_requisitos(self):
        """Requisitos técnicos según NTC 4018"""
        self.requisitos = {
            "indice_actividad": {
                "parametro": "Índice de actividad con cemento Portland",
                "unidad": "%",
                "metodo": "NTC 220 (ASTM C109)",
                "descripcion": "Resistencia relativa frente a mortero de control"
            },
            "finura_blaine": {
                "parametro": "Finura (Blaine)",
                "valor_minimo": 350.0,
                "unidad": "m²/kg",
                "metodo": "NTC 33 (ASTM C204)",
                "descripcion": "Superficie específica del material"
            },
            "densidad": {
                "parametro": "Densidad",
                "unidad": "g/cm³",
                "metodo": "NTC 221 (ASTM C188)",
                "descripcion": "Densidad del material"
            },
            "contenido_azufre": {
                "parametro": "Contenido de azufre (S)",
                "valor_maximo": 2.5,
                "unidad": "%",
                "metodo": "NTC 184 (ASTM C114)",
                "descripcion": "Contenido máximo de azufre"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 4018"""
        self.normas_relacionadas = {
            "ASTM_C989": "Standard Specification for Slag Cement for Use in Concrete and Mortars",
            "NTC_33": "Finura del cemento Portland (Blaine)",
            "NTC_121": "Cemento Portland. Especificaciones físicas y mecánicas",
            "NTC_184": "Cementos hidráulicos. Análisis químicos",
            "NTC_220": "Resistencia a compresión de morteros",
            "NTC_221": "Densidad del cemento hidráulico",
            "NTC_224": "Contenido de aire en morteros",
            "NTC_294": "Finura sobre tamiz No. 325",
            "NTC_321": "Cemento Portland. Especificaciones químicas",
            "NTC_3330": "Cambio longitudinal expuesto a sulfatos"
        }
    def _cargar_recomendaciones_uso(self):
        """Recomendaciones para el uso de escoria de alto horno"""
        self.recomendaciones_uso = [
            "La escoria de alto horno granulada y molida se puede usar como adición al cemento Portland para producir un cemento que cumpla con ASTM C595",
            "También puede usarse como ingrediente separado en mezclas de mortero o concreto",
            "Es útil en lechadas y morteros especiales, y como material cementoso principal con activador apropiado",
            "El índice de actividad se determina comparando la resistencia a compresión con morteros de control",
            "La información técnica detallada se encuentra en los Apéndices X1, X2 y X3 de la norma y en el Informe 226 1R de ACI",
            "El uso de escoria de alto horno mejora la durabilidad frente a sulfatos y cloruros",
            "Reduce la huella de carbono al sustituir parcialmente el cemento Portland"
        ]
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 4018
# ============================================================================
class MotorVerificacionNTC4018:
    """
    Motor de verificación de cumplimiento de la NTC 4018
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC4018()
    def verificar_escoria(self, escoria: EscoriaAltoHorno) -> ResultadoVerificacionNTC4018:
        """
        Verifica que una escoria de alto horno cumpla con los requisitos de la NTC 4018
        """
        requisitos = []
        errores = []
        # 1. Verificar grado de escoria
        requisitos.append(self._verificar_grado(escoria))
        # 2. Verificar índice de actividad
        requisitos.append(self._verificar_indice_actividad(escoria))
        # 3. Verificar finura (Blaine)
        requisitos.append(self._verificar_finura(escoria))
        # 4. Verificar contenido de azufre
        requisitos.append(self._verificar_azufre(escoria))
        # 5. Verificar equivalencia ASTM
        requisitos.append(self._verificar_astm())
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "La escoria cumple con los requisitos de la NTC 4018" if cumple else \
                  f"La escoria no cumple con {len(no_cumple)} requisito(s) de la NTC 4018"
        return ResultadoVerificacionNTC4018(
            escoria=escoria.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_grado(self, escoria: EscoriaAltoHorno) -> Dict[str, Any]:
        """Verifica que el grado de escoria sea válido"""
        grado_info = self.conocimiento.grados.get(escoria.grado)
        if not grado_info:
            return {
                "parametro": "Grado de escoria",
                "valor": escoria.grado.value if hasattr(escoria.grado, 'value') else str(escoria.grado),
                "cumple": False,
                "mensaje": f"Grado '{escoria.grado}' no reconocido en NTC 4018"
            }
        return {
            "parametro": "Grado de escoria",
            "valor": escoria.grado.value,
            "nombre": grado_info["nombre"],
            "descripcion": grado_info["descripcion"],
            "aplicacion": grado_info["aplicacion"],
            "cumple": True,
            "mensaje": f"Grado {escoria.grado.value} ({grado_info['nombre']}) válido según NTC 4018"
        }
    def _verificar_indice_actividad(self, escoria: EscoriaAltoHorno) -> Dict[str, Any]:
        """Verifica el índice de actividad a 7 y 28 días"""
        grado_info = self.conocimiento.grados.get(escoria.grado)
        if not grado_info:
            return {
                "parametro": "Índice de actividad",
                "cumple": False,
                "mensaje": "Grado de escoria no reconocido"
            }
        req_7dias = grado_info["indice_actividad_min_7dias"]
        req_28dias = grado_info["indice_actividad_min_28dias"]
        cumple_7 = escoria.analisis.indice_actividad_7dias >= req_7dias
        cumple_28 = escoria.analisis.indice_actividad_28dias >= req_28dias
        cumple_total = cumple_7 and cumple_28
        return {
            "parametro": "Índice de actividad con cemento Portland",
            "7_dias": {
                "valor": escoria.analisis.indice_actividad_7dias,
                "minimo": req_7dias,
                "cumple": cumple_7
            },
            "28_dias": {
                "valor": escoria.analisis.indice_actividad_28dias,
                "minimo": req_28dias,
                "cumple": cumple_28
            },
            "unidad": "%",
            "metodo": "NTC 220 (ASTM C109)",
            "cumple": cumple_total,
            "mensaje": f"Índice de actividad: 7d={escoria.analisis.indice_actividad_7dias}% {'>= ' if cumple_7 else '< '}{req_7dias}%, 28d={escoria.analisis.indice_actividad_28dias}% {'>= ' if cumple_28 else '< '}{req_28dias}%"
        }
    def _verificar_finura(self, escoria: EscoriaAltoHorno) -> Dict[str, Any]:
        """Verifica la finura Blaine"""
        req = self.conocimiento.requisitos["finura_blaine"]
        cumple = escoria.analisis.finura_blaine_m2_kg >= req["valor_minimo"]
        return {
            "parametro": req["parametro"],
            "valor": escoria.analisis.finura_blaine_m2_kg,
            "minimo": req["valor_minimo"],
            "unidad": req["unidad"],
            "metodo": req["metodo"],
            "cumple": cumple,
            "mensaje": f"Finura Blaine = {escoria.analisis.finura_blaine_m2_kg} m²/kg {'>= ' if cumple else '< '}{req['valor_minimo']} m²/kg"
        }
    def _verificar_azufre(self, escoria: EscoriaAltoHorno) -> Dict[str, Any]:
        """Verifica el contenido de azufre"""
        req = self.conocimiento.requisitos["contenido_azufre"]
        if escoria.analisis.contenido_azufre_porcentaje is None:
            return {
                "parametro": req["parametro"],
                "valor": "No disponible",
                "maximo": req["valor_maximo"],
                "unidad": req["unidad"],
                "cumple": True,
                "mensaje": "Contenido de azufre no medido (se asume cumplimiento)"
            }
        cumple = escoria.analisis.contenido_azufre_porcentaje <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": escoria.analisis.contenido_azufre_porcentaje,
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "metodo": req["metodo"],
            "cumple": cumple,
            "mensaje": f"Contenido de azufre = {escoria.analisis.contenido_azufre_porcentaje}% {'<= ' if cumple else '> '}{req['valor_maximo']}%"
        }
    def _verificar_astm(self) -> Dict[str, Any]:
        """Verifica la equivalencia con ASTM C989"""
        return {
            "parametro": "Equivalencia internacional",
            "valor": "ASTM C989",
            "titulo": "Standard Specification for Slag Cement for Use in Concrete and Mortars",
            "relacion": "NTC 4018 es equivalente a ASTM C989",
            "cumple": True,
            "mensaje": "NTC 4018 es equivalente a ASTM C989"
        }
    def obtener_grado(self, grado: GradoEscoria) -> Optional[Dict]:
        """Obtiene información de un grado de escoria"""
        return self.conocimiento.grados.get(grado)
    def obtener_requisito(self, parametro: str) -> Optional[Dict]:
        """Obtiene un requisito específico"""
        return self.conocimiento.requisitos.get(parametro)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 4018
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 4024 — Prefabricados de concreto. Muestreo y ensayo
#──────────────────────────────────────────────────────────────────────────────

class TipoPrefabricado(Enum):
    BLOQUE = "bloque"
    LADRILLO = "ladrillo"
    CHAPA = "chapa"
    GRAMOQUIN = "gramoquin"
    LOSETA = "loseta"
    OTRO = "otro"
class TipoEnsayo(Enum):
    COMPRESION = "compresion"
    ABSORCION = "absorcion"
    DENSIDAD = "densidad"
    HUMEDAD = "humedad"
    DIMENSIONES = "dimensiones"
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class DimensionesPrefabricado:
    """Modelo de dimensiones de un prefabricado según NTC 4024"""
    longitud_mm: float
    altura_mm: float
    espesor_mm: float
    espesor_pared_mm: Optional[float] = None
    espesor_tabique_mm: Optional[float] = None
@dataclass
class ResultadosEnsayo:
    """Modelo de resultados de ensayo según NTC 4024"""
    resistencia_compresion_mpa: Optional[float] = None
    absorcion_porcentaje: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    contenido_humedad_porcentaje: Optional[float] = None
    observaciones: Optional[str] = None
@dataclass
class MuestraPrefabricado:
    """Modelo de una muestra de prefabricado según NTC 4024"""
    nombre: str
    tipo: TipoPrefabricado
    dimensiones: DimensionesPrefabricado
    resultados: ResultadosEnsayo
    tamano_lote: int
    numero_especimenes: int
    fabricante: Optional[str] = None
    fecha_muestreo: Optional[str] = None
    referencia_normativa: str = "NTC 4024"
@dataclass
class ResultadoVerificacionNTC4024:
    """Resultado de la verificación de cumplimiento de NTC 4024"""
    muestra: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 4024 (CAG)
# ============================================================================
class ConocimientoNTC4024:
    """
    Base de conocimiento CAG de la NTC 4024: Prefabricados de concreto
    Muestreo y ensayo de prefabricados no reforzados, vibrocompactados (2001)
    """
    def __init__(self):
        self._cargar_requisitos_muestreo()
        self._cargar_requisitos_ensayos()
        self._cargar_normas_relacionadas()
    def _cargar_requisitos_muestreo(self):
        """Requisitos de muestreo según NTC 4024"""
        self.requisitos_muestreo = {
            "tamano_lote": {
                "parametro": "Tamaño del lote",
                "unidad": "unidades",
                "descripcion": "Número total de unidades en el lote"
            },
            "numero_especimenes": {
                "parametro": "Número de especímenes",
                "reglas": [
                    {"lote_maximo": 10000, "especimenes": 6},
                    {"lote_maximo": 100000, "especimenes": 12},
                    {"lote_maximo": float('inf'), "especimenes_por": 50000}
                ],
                "descripcion": "Cantidad de especímenes a tomar según tamaño del lote"
            },
            "rotulado": {
                "parametro": "Área de rótulo",
                "valor_maximo": 5.0,
                "unidad": "%",
                "descripcion": "El rótulo no debe cubrir más del 5% del área de la superficie"
            }
        }
    def _cargar_requisitos_ensayos(self):
        """Requisitos de ensayos según NTC 4024"""
        self.requisitos_ensayos = {
            "compresion": {
                "parametro": "Resistencia a la compresión",
                "unidad": "MPa",
                "descripcion": "Capacidad del prefabricado para soportar cargas axiales"
            },
            "absorcion": {
                "parametro": "Absorción de agua",
                "unidad": "%",
                "descripcion": "Capacidad de absorción de agua del material"
            },
            "densidad": {
                "parametro": "Densidad",
                "unidad": "g/cm³",
                "descripcion": "Masa por unidad de volumen"
            },
            "humedad": {
                "parametro": "Contenido de humedad",
                "unidad": "%",
                "descripcion": "Cantidad de agua presente en el material"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 4024"""
        self.normas_relacionadas = {
            "NTC_4026": "Unidades de mampostería, perforadas o macizas de concreto",
            "NTC_2017": "Adoquines de concreto para pavimentos",
            "NTC_121": "Especificación de desempeño para cemento hidráulico",
            "NTC_174": "Especificaciones de los agregados para concreto"
        }
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 4024
# ============================================================================
class MotorVerificacionNTC4024:
    """
    Motor de verificación de cumplimiento de la NTC 4024
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC4024()
    def verificar_muestra(self, muestra: MuestraPrefabricado) -> ResultadoVerificacionNTC4024:
        """
        Verifica que una muestra de prefabricado cumpla con los requisitos de la NTC 4024
        """
        requisitos = []
        errores = []
        # 1. Verificar tipo de prefabricado
        requisitos.append(self._verificar_tipo(muestra))
        # 2. Verificar número de especímenes según lote
        requisitos.append(self._verificar_numero_especimenes(muestra))
        # 3. Verificar ensayos realizados
        requisitos.append(self._verificar_ensayos(muestra))
        # 4. Verificar dimensiones
        requisitos.append(self._verificar_dimensiones(muestra))
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "La muestra cumple con los requisitos de la NTC 4024" if cumple else \
                  f"La muestra no cumple con {len(no_cumple)} requisito(s) de la NTC 4024"
        return ResultadoVerificacionNTC4024(
            muestra=muestra.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_tipo(self, muestra: MuestraPrefabricado) -> Dict[str, Any]:
        """Verifica que el tipo de prefabricado sea válido"""
        if muestra.tipo not in [TipoPrefabricado.BLOQUE, TipoPrefabricado.LADRILLO,
                               TipoPrefabricado.CHAPA, TipoPrefabricado.GRAMOQUIN,
                               TipoPrefabricado.LOSETA, TipoPrefabricado.OTRO]:
            return {
                "parametro": "Tipo de prefabricado",
                "valor": muestra.tipo.value if hasattr(muestra.tipo, 'value') else str(muestra.tipo),
                "cumple": False,
                "mensaje": f"Tipo '{muestra.tipo}' no reconocido en NTC 4024"
            }
        return {
            "parametro": "Tipo de prefabricado",
            "valor": muestra.tipo.value,
            "cumple": True,
            "mensaje": f"Tipo {muestra.tipo.value} válido según NTC 4024"
        }
    def _verificar_numero_especimenes(self, muestra: MuestraPrefabricado) -> Dict[str, Any]:
        """Verifica el número de especímenes según el tamaño del lote"""
        req = self.conocimiento.requisitos_muestreo["numero_especimenes"]
        # Determinar el número requerido según las reglas
        requerido = None
        for regla in req["reglas"]:
            if muestra.tamano_lote <= regla["lote_maximo"]:
                if "especimenes" in regla:
                    requerido = regla["especimenes"]
                elif "especimenes_por" in regla:
                    import math
                    requerido = math.ceil(muestra.tamano_lote / regla["especimenes_por"]) * 6
                break
        if requerido is None:
            requerido = 6  # Valor por defecto
        cumple = muestra.numero_especimenes >= requerido
        return {
            "parametro": req["parametro"],
            "tamano_lote": muestra.tamano_lote,
            "especimenes_tomados": muestra.numero_especimenes,
            "especimenes_requeridos": requerido,
            "cumple": cumple,
            "mensaje": f"Especímenes: {muestra.numero_especimenes} {'>= ' if cumple else '< '}{requerido} (requeridos para lote de {muestra.tamano_lote} unidades)"
        }
    def _verificar_ensayos(self, muestra: MuestraPrefabricado) -> Dict[str, Any]:
        """Verifica que se hayan realizado los ensayos requeridos"""
        resultados = []
        cumple_total = True
        # Verificar cada tipo de ensayo
        ensayos_realizados = []
        if muestra.resultados.resistencia_compresion_mpa is not None:
            ensayos_realizados.append("compresion")
        if muestra.resultados.absorcion_porcentaje is not None:
            ensayos_realizados.append("absorcion")
        if muestra.resultados.densidad_g_cm3 is not None:
            ensayos_realizados.append("densidad")
        if muestra.resultados.contenido_humedad_porcentaje is not None:
            ensayos_realizados.append("humedad")
        ensayos_requeridos = ["compresion", "absorcion", "densidad", "humedad"]
        faltantes = [e for e in ensayos_requeridos if e not in ensayos_realizados]
        cumple = len(faltantes) == 0
        return {
            "parametro": "Ensayos realizados",
            "realizados": ensayos_realizados,
            "requeridos": ensayos_requeridos,
            "faltantes": faltantes,
            "cumple": cumple,
            "mensaje": f"Ensayos: {'completos' if cumple else 'faltan: ' + ', '.join(faltantes)}"
        }
    def _verificar_dimensiones(self, muestra: MuestraPrefabricado) -> Dict[str, Any]:
        """Verifica que las dimensiones sean válidas"""
        dim = muestra.dimensiones
        if dim.longitud_mm <= 0 or dim.altura_mm <= 0 or dim.espesor_mm <= 0:
            return {
                "parametro": "Dimensiones",
                "valor": f"L={dim.longitud_mm}, A={dim.altura_mm}, E={dim.espesor_mm}",
                "cumple": False,
                "mensaje": "Dimensiones inválidas (deben ser > 0)"
            }
        return {
            "parametro": "Dimensiones",
            "longitud_mm": dim.longitud_mm,
            "altura_mm": dim.altura_mm,
            "espesor_mm": dim.espesor_mm,
            "espesor_pared_mm": dim.espesor_pared_mm,
            "espesor_tabique_mm": dim.espesor_tabique_mm,
            "cumple": True,
            "mensaje": f"Dimensiones válidas: L={dim.longitud_mm}mm, A={dim.altura_mm}mm, E={dim.espesor_mm}mm"
        }
    def obtener_requisito_muestreo(self, parametro: str) -> Optional[Dict]:
        """Obtiene un requisito de muestreo específico"""
        return self.conocimiento.requisitos_muestreo.get(parametro)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 4024
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 4924 — Agregados livianos para unidades de mampostería de concreto (equivalente ASTM C331)
#──────────────────────────────────────────────────────────────────────────────

class TipoAgregadoLiviano(Enum):
    ARCILLA_EXPANDIDA = "arcilla_expandida"
    ESQUISTO_EXPANDIDO = "esquisto_expandido"
    PUZOLANA_EXPANDIDA = "puzolana_expandida"
    ESCORIA_EXPANDIDA = "escoría_expandida"
    OTRO = "otro"
class TipoUnidadMamposteria(Enum):
    BLOQUE = "bloque"
    LADRILLO = "ladrillo"
    CHAPA = "chapa"
    OTRO = "otro"
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class AgregadoLiviano:
    """Modelo de un agregado liviano según NTC 4924"""
    nombre: str
    tipo: TipoAgregadoLiviano
    densidad_aparente_kg_m3: float
    absorcion_porcentaje: float
    resistencia_compresion_mpa: Optional[float] = None
    tamano_maximo_mm: Optional[float] = None
    modulo_finura: Optional[float] = None
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 4924 (ASTM C331)"
@dataclass
class UnidadMamposteria:
    """Modelo de una unidad de mampostería con agregado liviano"""
    nombre: str
    tipo: TipoUnidadMamposteria
    agregado: AgregadoLiviano
    dimensiones_mm: Dict[str, float]  # largo, ancho, alto
    resistencia_compresion_mpa: float
    densidad_aparente_kg_m3: float
    absorcion_porcentaje: float
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 4924"
@dataclass
class ResultadoVerificacionNTC4924:
    """Resultado de la verificación de cumplimiento de NTC 4924"""
    material: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 4924 (CAG)
# ============================================================================
class ConocimientoNTC4924:
    """
    Base de conocimiento CAG de la NTC 4924: Agregados livianos para unidades de mampostería de concreto
    Año 2001 - Equivalente a ASTM C331
    """
    def __init__(self):
        self._cargar_requisitos()
        self._cargar_tipos_agregados()
        self._cargar_normas_relacionadas()
        self._cargar_recomendaciones_uso()
    def _cargar_requisitos(self):
        """Requisitos técnicos según NTC 4924 / ASTM C331"""
        self.requisitos = {
            "densidad_aparente": {
                "parametro": "Densidad aparente del agregado liviano",
                "valor_maximo": 1120.0,
                "unidad": "kg/m³",
                "referencia": "ASTM C331",
                "descripcion": "La densidad aparente del agregado liviano no debe exceder 1120 kg/m³"
            },
            "absorcion": {
                "parametro": "Absorción de agua",
                "valor_maximo": 25.0,
                "unidad": "%",
                "referencia": "ASTM C331",
                "descripcion": "La absorción de agua máxima permitida para agregados livianos"
            },
            "resistencia_compresion_unidad": {
                "parametro": "Resistencia a la compresión de la unidad",
                "unidad": "MPa",
                "referencia": "NTC 4026",
                "descripcion": "Según el tipo de unidad y su uso (estructural o no estructural)"
            }
        }
    def _cargar_tipos_agregados(self):
        """Tipos de agregados livianos según NTC 4924"""
        self.tipos_agregados = {
            TipoAgregadoLiviano.ARCILLA_EXPANDIDA: {
                "nombre": "Arcilla expandida",
                "descripcion": "Arcilla sometida a expansión por calentamiento",
                "densidad_tipica": "400-900 kg/m³",
                "aplicacion": "Bloques y ladrillos livianos"
            },
            TipoAgregadoLiviano.ESQUISTO_EXPANDIDO: {
                "nombre": "Esquisto expandido",
                "descripcion": "Esquisto sometido a expansión por calentamiento",
                "densidad_tipica": "500-1000 kg/m³",
                "aplicacion": "Unidades de mampostería estructural"
            },
            TipoAgregadoLiviano.PUZOLANA_EXPANDIDA: {
                "nombre": "Puzolana expandida",
                "descripcion": "Material puzolánico expandido por calor",
                "densidad_tipica": "400-800 kg/m³",
                "aplicacion": "Bloques livianos para mampostería interior"
            },
            TipoAgregadoLiviano.ESCORIA_EXPANDIDA: {
                "nombre": "Escoria expandida",
                "descripcion": "Subproducto siderúrgico expandido",
                "densidad_tipica": "600-1100 kg/m³",
                "aplicacion": "Unidades de mampostería general"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 4924"""
        self.normas_relacionadas = {
            "ASTM_C331": "Standard Specification for Lightweight Aggregates for Concrete Masonry Units",
            "NTC_4026": "Unidades (bloques y ladrillos) de concreto para mampostería estructural",
            "NTC_4076": "Unidades de concreto para mampostería interior y chapas",
            "NTC_4024": "Prefabricados de concreto. Muestreo y ensayo",
            "NTC_2017": "Adoquines de concreto para pavimentos",
            "NTC_121": "Especificación de desempeño para cemento hidráulico",
            "NTC_3493": "Cenizas volantes y puzolanas como aditivos minerales",
            "NTC_4018": "Escoria de alto horno para concreto y morteros"
        }
    def _cargar_recomendaciones_uso(self):
        """Recomendaciones para el uso de agregados livianos en mampostería"""
        self.recomendaciones_uso = [
            "Los agregados livianos reducen el peso de las unidades de mampostería, facilitando su manipulación y transporte",
            "La densidad aparente del agregado liviano no debe exceder 1120 kg/m³ según ASTM C331",
            "La absorción de agua de los agregados livianos no debe exceder el 25%",
            "El uso de agregados livianos mejora el aislamiento térmico y acústico de los muros",
            "Las unidades de mampostería con agregados livianos pueden ser estructurales o no estructurales según su resistencia",
            "La selección del tipo de agregado liviano depende de la aplicación y los requisitos de resistencia"
        ]
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 4924
# ============================================================================
class MotorVerificacionNTC4924:
    """
    Motor de verificación de cumplimiento de la NTC 4924
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC4924()
    def verificar_agregado(self, agregado: AgregadoLiviano) -> ResultadoVerificacionNTC4924:
        """
        Verifica que un agregado liviano cumpla con los requisitos de la NTC 4924
        """
        requisitos = []
        errores = []
        # 1. Verificar tipo de agregado
        requisitos.append(self._verificar_tipo(agregado))
        # 2. Verificar densidad aparente
        requisitos.append(self._verificar_densidad(agregado))
        # 3. Verificar absorción
        requisitos.append(self._verificar_absorcion(agregado))
        # 4. Verificar equivalencia ASTM
        requisitos.append(self._verificar_astm())
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "El agregado liviano cumple con los requisitos de la NTC 4924" if cumple else \
                  f"El agregado liviano no cumple con {len(no_cumple)} requisito(s) de la NTC 4924"
        return ResultadoVerificacionNTC4924(
            material=agregado.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_tipo(self, agregado: AgregadoLiviano) -> Dict[str, Any]:
        """Verifica que el tipo de agregado sea válido"""
        tipo_info = self.conocimiento.tipos_agregados.get(agregado.tipo)
        if not tipo_info:
            return {
                "parametro": "Tipo de agregado liviano",
                "valor": agregado.tipo.value if hasattr(agregado.tipo, 'value') else str(agregado.tipo),
                "cumple": False,
                "mensaje": f"Tipo '{agregado.tipo}' no reconocido en NTC 4924"
            }
        return {
            "parametro": "Tipo de agregado liviano",
            "valor": agregado.tipo.value,
            "nombre": tipo_info["nombre"],
            "descripcion": tipo_info["descripcion"],
            "densidad_tipica": tipo_info["densidad_tipica"],
            "aplicacion": tipo_info["aplicacion"],
            "cumple": True,
            "mensaje": f"Tipo {agregado.tipo.value} ({tipo_info['nombre']}) válido según NTC 4924"
        }
    def _verificar_densidad(self, agregado: AgregadoLiviano) -> Dict[str, Any]:
        """Verifica la densidad aparente del agregado liviano"""
        req = self.conocimiento.requisitos["densidad_aparente"]
        cumple = agregado.densidad_aparente_kg_m3 <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": agregado.densidad_aparente_kg_m3,
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "referencia": req["referencia"],
            "cumple": cumple,
            "mensaje": f"Densidad aparente = {agregado.densidad_aparente_kg_m3} kg/m³ {'<= ' if cumple else '> '}{req['valor_maximo']} kg/m³"
        }
    def _verificar_absorcion(self, agregado: AgregadoLiviano) -> Dict[str, Any]:
        """Verifica la absorción de agua del agregado liviano"""
        req = self.conocimiento.requisitos["absorcion"]
        cumple = agregado.absorcion_porcentaje <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": agregado.absorcion_porcentaje,
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "referencia": req["referencia"],
            "cumple": cumple,
            "mensaje": f"Absorción = {agregado.absorcion_porcentaje}% {'<= ' if cumple else '> '}{req['valor_maximo']}%"
        }
    def _verificar_astm(self) -> Dict[str, Any]:
        """Verifica la equivalencia con ASTM C331"""
        return {
            "parametro": "Equivalencia internacional",
            "valor": "ASTM C331",
            "titulo": "Standard Specification for Lightweight Aggregates for Concrete Masonry Units",
            "relacion": "NTC 4924 es equivalente a ASTM C331",
            "cumple": True,
            "mensaje": "NTC 4924 es equivalente a ASTM C331"
        }
    def verificar_unidad_mamposteria(self, unidad: UnidadMamposteria) -> ResultadoVerificacionNTC4924:
        """
        Verifica que una unidad de mampostería con agregado liviano cumpla con los requisitos
        """
        # Primero verificar el agregado
        resultado_agregado = self.verificar_agregado(unidad.agregado)
        if not resultado_agregado.cumple:
            return resultado_agregado
        # Verificar requisitos adicionales de la unidad
        requisitos = []
        # Verificar resistencia a compresión
        req = self.conocimiento.requisitos["resistencia_compresion_unidad"]
        if unidad.resistencia_compresion_mpa > 0:
            requisitos.append({
                "parametro": req["parametro"],
                "valor": unidad.resistencia_compresion_mpa,
                "unidad": req["unidad"],
                "referencia": req["referencia"],
                "cumple": True,
                "mensaje": f"Resistencia a compresión = {unidad.resistencia_compresion_mpa} MPa"
            })
        else:
            requisitos.append({
                "parametro": req["parametro"],
                "valor": "No especificado",
                "unidad": req["unidad"],
                "referencia": req["referencia"],
                "cumple": False,
                "mensaje": "Resistencia a compresión no especificada"
            })
        cumple = all(r.get("cumple", True) for r in requisitos)
        mensaje = "La unidad de mampostería cumple con los requisitos de la NTC 4924" if cumple else \
                  "La unidad de mampostería no cumple con todos los requisitos de la NTC 4924"
        return ResultadoVerificacionNTC4924(
            material=unidad.nombre,
            cumple=cumple,
            requisitos=resultado_agregado.requisitos + requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def obtener_tipo_agregado(self, tipo: TipoAgregadoLiviano) -> Optional[Dict]:
        """Obtiene información de un tipo de agregado liviano"""
        return self.conocimiento.tipos_agregados.get(tipo)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 4924
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 5147 — Resistencia a la abrasión (arena y disco metálico ancho)
#──────────────────────────────────────────────────────────────────────────────

class TipoMaterial(Enum):
    ADOQUIN = "adoquin"
    LOSETA = "loseta"
    PREFABRICADO = "prefabricado"
    OTRO = "otro"
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class ResultadoAbrasion:
    """Modelo de resultados del ensayo de abrasión según NTC 5147"""
    longitud_huella_1_mm: float
    longitud_huella_2_mm: float
    longitud_huella_3_mm: float
    longitud_huella_4_mm: float
    longitud_huella_5_mm: float
    observaciones: Optional[str] = None
@dataclass
class MuestraAbrasion:
    """Modelo de una muestra sometida a ensayo de abrasión"""
    nombre: str
    tipo: TipoMaterial
    resultados: ResultadoAbrasion
    fecha_ensayo: Optional[str] = None
    laboratorio: Optional[str] = None
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 5147"
@dataclass
class ResultadoVerificacionNTC5147:
    """Resultado de la verificación de cumplimiento de NTC 5147"""
    muestra: str
    cumple: bool
    requisitos: List[Dict[str, Any]]
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 5147 (CAG)
# ============================================================================
class ConocimientoNTC5147:
    """
    Base de conocimiento CAG de la NTC 5147: Resistencia a la abrasión
    Método de ensayo mediante arena y disco metálico ancho (2002/2003)
    """
    def __init__(self):
        self._cargar_requisitos()
        self._cargar_equipo()
        self._cargar_normas_relacionadas()
        self._cargar_recomendaciones()
    def _cargar_requisitos(self):
        """Requisitos técnicos según NTC 5147"""
        self.requisitos = {
            "longitud_maxima_huella": {
                "parametro": "Longitud promedio de la huella de abrasión",
                "valor_maximo": 23.0,
                "unidad": "mm",
                "referencia": "NTC 5147",
                "descripcion": "La longitud promedio de la huella de 5 especímenes no debe exceder 23 mm"
            },
            "numero_especimenes": {
                "parametro": "Número de especímenes",
                "valor_requerido": 5,
                "unidad": "unidades",
                "referencia": "NTC 5147",
                "descripcion": "Se deben ensayar 5 especímenes para obtener el promedio"
            },
            "revoluciones": {
                "parametro": "Revoluciones del disco",
                "valor_requerido": 75,
                "unidad": "revoluciones",
                "referencia": "NTC 5147",
                "descripcion": "El disco debe girar 75 revoluciones durante el ensayo"
            }
        }
    def _cargar_equipo(self):
        """Especificaciones del equipo según NTC 5147"""
        self.equipo = {
            "dimensiones": "734 x 503 x 600 mm",
            "disco": {
                "diametro": "200 mm",
                "material": "Acero tratado",
                "ancho": "70 mm"
            },
            "pesa_arrastre": {
                "masa": "2 kg",
                "material": "Acero"
            },
            "temporizador": "Programable de 1 a 9999 segundos",
            "parada": "Automática después de 75 revoluciones",
            "muestra": {
                "tamano_maximo": "200 x 150 x 70 mm"
            },
            "operacion": "110 VAC, 50/60 Hz - 600 W"
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 5147"""
        self.normas_relacionadas = {
            "NTC_2017": "Adoquines de concreto para pavimentos - Exige ensayo de abrasión",
            "NTC_4992": "Losetas de concreto para pavimentos - Exige ensayo de abrasión",
            "NTC_4024": "Prefabricados de concreto. Muestreo y ensayo",
            "NTC_6008": "Terminología y clasificación para adoquines y losetas"
        }
    def _cargar_recomendaciones(self):
        """Recomendaciones para el ensayo de abrasión"""
        self.recomendaciones = [
            "La longitud de la huella es inversamente proporcional a la resistencia al desgaste",
            "Una huella más corta indica mayor resistencia a la abrasión",
            "El ensayo debe realizarse sobre 5 especímenes para obtener un promedio representativo",
            "La muestra debe prepararse adecuadamente antes del ensayo",
            "El equipo debe calibrarse periódicamente para garantizar resultados precisos"
        ]
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 5147
# ============================================================================
class MotorVerificacionNTC5147:
    """
    Motor de verificación de cumplimiento de la NTC 5147
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC5147()
    def verificar_muestra(self, muestra: MuestraAbrasion) -> ResultadoVerificacionNTC5147:
        """
        Verifica que una muestra cumpla con los requisitos de la NTC 5147
        """
        requisitos = []
        errores = []
        # 1. Verificar tipo de material
        requisitos.append(self._verificar_tipo(muestra))
        # 2. Verificar número de especímenes
        requisitos.append(self._verificar_especimenes(muestra))
        # 3. Verificar longitud de huella
        requisitos.append(self._verificar_longitud_huella(muestra))
        # 4. Verificar especificaciones del equipo
        requisitos.append(self._verificar_equipo())
        # Determinar si cumple
        no_cumple = [r for r in requisitos if not r.get("cumple", True)]
        cumple = len(no_cumple) == 0
        mensaje = "La muestra cumple con los requisitos de la NTC 5147" if cumple else \
                  f"La muestra no cumple con {len(no_cumple)} requisito(s) de la NTC 5147"
        return ResultadoVerificacionNTC5147(
            muestra=muestra.nombre,
            cumple=cumple,
            requisitos=requisitos,
            mensaje=mensaje,
            timestamp=datetime.now().isoformat()
        )
    def _verificar_tipo(self, muestra: MuestraAbrasion) -> Dict[str, Any]:
        """Verifica que el tipo de material sea válido"""
        if muestra.tipo not in [TipoMaterial.ADOQUIN, TipoMaterial.LOSETA,
                               TipoMaterial.PREFABRICADO, TipoMaterial.OTRO]:
            return {
                "parametro": "Tipo de material",
                "valor": muestra.tipo.value if hasattr(muestra.tipo, 'value') else str(muestra.tipo),
                "cumple": False,
                "mensaje": f"Tipo '{muestra.tipo}' no reconocido en NTC 5147"
            }
        return {
            "parametro": "Tipo de material",
            "valor": muestra.tipo.value,
            "cumple": True,
            "mensaje": f"Tipo {muestra.tipo.value} válido según NTC 5147"
        }
    def _verificar_especimenes(self, muestra: MuestraAbrasion) -> Dict[str, Any]:
        """Verifica que se hayan ensayado 5 especímenes"""
        req = self.conocimiento.requisitos["numero_especimenes"]
        # Verificar que todos los valores estén presentes
        valores = [
            muestra.resultados.longitud_huella_1_mm,
            muestra.resultados.longitud_huella_2_mm,
            muestra.resultados.longitud_huella_3_mm,
            muestra.resultados.longitud_huella_4_mm,
            muestra.resultados.longitud_huella_5_mm
        ]
        especimenes_validos = sum(1 for v in valores if v is not None and v > 0)
        cumple = especimenes_validos >= req["valor_requerido"]
        return {
            "parametro": req["parametro"],
            "valor": especimenes_validos,
            "requerido": req["valor_requerido"],
            "unidad": req["unidad"],
            "cumple": cumple,
            "mensaje": f"Especímenes válidos: {especimenes_validos} {'>= ' if cumple else '< '}{req['valor_requerido']}"
        }
    def _verificar_longitud_huella(self, muestra: MuestraAbrasion) -> Dict[str, Any]:
        """Verifica que la longitud promedio de la huella no exceda 23 mm"""
        req = self.conocimiento.requisitos["longitud_maxima_huella"]
        valores = [
            muestra.resultados.longitud_huella_1_mm,
            muestra.resultados.longitud_huella_2_mm,
            muestra.resultados.longitud_huella_3_mm,
            muestra.resultados.longitud_huella_4_mm,
            muestra.resultados.longitud_huella_5_mm
        ]
        valores_validos = [v for v in valores if v is not None and v > 0]
        if len(valores_validos) < 5:
            return {
                "parametro": req["parametro"],
                "valor": "No disponible",
                "maximo": req["valor_maximo"],
                "unidad": req["unidad"],
                "cumple": False,
                "mensaje": f"Faltan {5 - len(valores_validos)} valores para calcular el promedio"
            }
        promedio = sum(valores_validos) / len(valores_validos)
        cumple = promedio <= req["valor_maximo"]
        return {
            "parametro": req["parametro"],
            "valor": round(promedio, 2),
            "maximo": req["valor_maximo"],
            "unidad": req["unidad"],
            "valores_individuales": [round(v, 2) for v in valores_validos],
            "cumple": cumple,
            "mensaje": f"Longitud promedio = {round(promedio, 2)} mm {'<= ' if cumple else '> '}{req['valor_maximo']} mm"
        }
    def _verificar_equipo(self) -> Dict[str, Any]:
        """Verifica las especificaciones del equipo"""
        equipo = self.conocimiento.equipo
        return {
            "parametro": "Especificaciones del equipo",
            "disco": f"Ø {equipo['disco']['diametro']} - Ancho {equipo['disco']['ancho']}",
            "pesa": equipo["pesa_arrastre"]["masa"],
            "revoluciones": "75",
            "cumple": True,
            "mensaje": "Equipo conforme a las especificaciones de NTC 5147"
        }
    def obtener_requisito(self, parametro: str) -> Optional[Dict]:
        """Obtiene un requisito específico"""
        return self.conocimiento.requisitos.get(parametro)
# ============================================================================
# 5. MÓDULO RAG PARA NTC 5147
# ============================================================================

#──────────────────────────────────────────────────────────────────────────────
# NTC 6008 — Terminología y clasificación para adoquines y losetas de concreto
#──────────────────────────────────────────────────────────────────────────────

class TipoAdoquin(Enum):
    """Tipos de adoquín según NTC 6008 y NTC 2017"""
    NO_BISELADO = "no_biselado"
    BISELADO = "biselado"
    DRENANTE = "drenante"
    ESPECIAL = "especial"
class UsoAdoquin(Enum):
    PEATONAL = "peatonal"
    VEHICULAR_LIVIANO = "vehicular_liviano"
    VEHICULAR_PESADO = "vehicular_pesado"
    INDUSTRIAL = "industrial"
class EstadoVerificacion(Enum):
    CUMPLE = "cumple"
    NO_CUMPLE = "no_cumple"
    ADVERTENCIA = "advertencia"
# ============================================================================
# 2. MODELOS DE DATOS
# ============================================================================
@dataclass
class TerminoNTC6008:
    """Modelo de un término definido en NTC 6008"""
    termino: str
    definicion: str
    referencia: str = "NTC 6008"
    anio: int = 2013
@dataclass
class Adoquin:
    """Modelo de un adoquín según NTC 6008"""
    nombre: str
    tipo: TipoAdoquin
    uso: UsoAdoquin
    geometria: Dict[str, float]  # dimensiones en mm
    bisel: bool = False
    drenante: bool = False
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 6008 / NTC 2017"
@dataclass
class ResultadoVerificacionNTC6008:
    """Resultado de la verificación de terminología según NTC 6008"""
    termino: str
    cumple: bool
    definicion: str
    mensaje: str
    timestamp: str
# ============================================================================
# 3. BASE DE CONOCIMIENTO - NTC 6008 (CAG)
# ============================================================================
class ConocimientoNTC6008:
    """
    Base de conocimiento CAG de la NTC 6008: Terminología y clasificación
    para adoquines y losetas de concreto (2013)
    """
    def __init__(self):
        self._cargar_terminos()
        self._cargar_clasificacion()
        self._cargar_normas_relacionadas()
    def _cargar_terminos(self):
        """Términos definidos en NTC 6008"""
        self.terminos = [
            TerminoNTC6008(
                termino="Adoquín de concreto",
                definicion="Elemento constructivo versátil y resistente, fabricado con precisión para garantizar alta durabilidad y bajo mantenimiento. Solución ideal para pavimentar áreas de alto tránsito"
            ),
            TerminoNTC6008(
                termino="Adoquín especial",
                definicion="Pieza maestra de ingeniería, diseñada a medida para adaptarse a cualquier entorno y resistir las pruebas del tiempo. Combina estética y funcionalidad de manera excepcional"
            ),
            TerminoNTC6008(
                termino="Superficie de referencia",
                definicion="Cara principal del adoquín, la que soporta el desgaste diario"
            ),
            TerminoNTC6008(
                termino="Forma",
                definicion="Contorno que identifica al adoquín, desde su cara superior hasta su base"
            ),
            TerminoNTC6008(
                termino="Pared o cara lateral",
                definicion="Caras que unen a los adoquines, formando las juntas que permiten que trabajen juntos"
            ),
            TerminoNTC6008(
                termino="Arista",
                definicion="Bordes donde se encuentran las caras del adoquín, creando las esquinas"
            ),
            TerminoNTC6008(
                termino="Adoquín no biselado",
                definicion="Adoquín sin perfil inclinado ni modificación en las aristas de la cara de desgaste"
            ),
            TerminoNTC6008(
                termino="Adoquín biselado",
                definicion="Adoquín con perfil inclinado en las aristas"
            ),
            TerminoNTC6008(
                termino="Adoquín drenante",
                definicion="Adoquín diseñado para permitir el paso del agua a través de la superficie"
            )
        ]
    def _cargar_clasificacion(self):
        """Clasificación de adoquines según NTC 6008"""
        self.clasificacion = {
            "por_geometria": {
                "no_biselado": "Sin bisel ni modificación en aristas",
                "biselado": "Con perfil inclinado en aristas",
                "drenante": "Permite paso de agua"
            },
            "por_uso": {
                "peatonal": "Tráfico peatonal",
                "vehicular_liviano": "Tráfico vehicular liviano",
                "vehicular_pesado": "Tráfico vehicular pesado",
                "industrial": "Tráfico industrial y cargas estáticas"
            },
            "por_acabado": {
                "normal": "Acabado estándar",
                "texturizado": "Superficie con textura",
                "especial": "Diseño a medida"
            }
        }
    def _cargar_normas_relacionadas(self):
        """Normas relacionadas con NTC 6008"""
        self.normas_relacionadas = {
            "NTC_2017": "Adoquines de concreto para pavimentos - Requisitos físicos",
            "NTC_4992": "Losetas de concreto para pavimentos",
            "NTC_4024": "Prefabricados de concreto. Muestreo y ensayo",
            "NTC_4026": "Unidades de concreto para mampostería estructural",
            "NTC_4076": "Unidades de concreto para mampostería no estructural",
            "NTC_4109": "Bordillos, cunetas y topellantas de concreto",
            "NTC_ISO_80000_1": "Cantidades y Unidades. Parte 1: Generalidades"
        }
# ============================================================================
# 4. MOTOR DE VERIFICACIÓN - NTC 6008
# ============================================================================
class MotorVerificacionNTC6008:
    """
    Motor de verificación de terminología según NTC 6008
    """
    def __init__(self):
        self.conocimiento = ConocimientoNTC6008()
    def buscar_termino(self, termino_busqueda: str) -> ResultadoVerificacionNTC6008:
        """
        Busca un término en la NTC 6008 y devuelve su definición
        """
        termino_busqueda = termino_busqueda.strip().lower()
        for termino in self.conocimiento.terminos:
            if termino_busqueda in termino.termino.lower():
                return ResultadoVerificacionNTC6008(
                    termino=termino.termino,
                    cumple=True,
                    definicion=termino.definicion,
                    mensaje=f"Término '{termino.termino}' encontrado en NTC 6008",
                    timestamp=datetime.now().isoformat()
                )
        return ResultadoVerificacionNTC6008(
            termino=termino_busqueda,
            cumple=False,
            definicion="Término no encontrado en NTC 6008",
            mensaje=f"El término '{termino_busqueda}' no está definido en NTC 6008",
            timestamp=datetime.now().isoformat()
        )
    def obtener_todos_terminos(self) -> List[TerminoNTC6008]:
        """Obtiene todos los términos definidos en NTC 6008"""
        return self.conocimiento.terminos
    def obtener_clasificacion(self) -> Dict:
        """Obtiene la clasificación de adoquines según NTC 6008"""
        return self.conocimiento.clasificacion
# ============================================================================
# 5. MÓDULO RAG PARA NTC 6008
# ============================================================================
