"""
MÓDULO: Diagnóstico y Planificación de Mantenimiento Vial
Norma: Manual de Mantenimiento de Carreteras INVIAS (2016), adoptado mediante
       Resolución 04046 de 2018.

Clasifica la gravedad de un deterioro de pavimento, determina la prioridad de
intervención y recomienda el tipo y las actividades de mantenimiento según la
defectología y los umbrales del manual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ─── Enums ──────────────────────────────────────────────────────────────────

class TipoVia(Enum):
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"
    TERCIARIA = "terciaria"


class TipoMantenimiento(Enum):
    RUTINARIO = "rutinario"
    PERIODICO = "periodico"
    EMERGENCIA = "emergencia"


class TipoDeterioro(Enum):
    BACHE = "bache"
    GRIETA = "grieta"
    AHUELLAMIENTO = "ahuellamiento"
    CRAQUELADO = "craquelado"
    HUNDIMIENTO = "hundimiento"
    DESPLAZAMIENTO_BORDE = "desplazamiento_borde"
    LOSA_FRAGMENTADA = "losa_fragmentada"
    FISURA = "fisura"


class GravedadDeterioro(Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class PrioridadIntervencion(Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


# ─── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class ParametrosMantenimiento:
    """Parámetros de entrada para diagnóstico y planificación de mantenimiento."""
    tipo_via: TipoVia
    tipo_mantenimiento: TipoMantenimiento
    deterioro_tipo: TipoDeterioro
    deterioro_gravedad: GravedadDeterioro
    area_afectada: Optional[float] = None          # m²
    profundidad: Optional[float] = None            # cm
    longitud: Optional[float] = None               # m (para grietas)
    ancho: Optional[float] = None                  # mm (para grietas)
    indice_condicion: Optional[float] = None        # PCI (%)
    volumen_transito: Optional[int] = None          # TPD


@dataclass
class ResultadoDiagnostico:
    """Resultado del diagnóstico de mantenimiento."""
    tipo_via: str
    tipo_mantenimiento: str
    deterioro_tipo: str
    gravedad: str
    prioridad: str
    intervencion_recomendada: str
    actividades: List[str]
    urgencia: str
    cumple: bool
    mensaje: str
    restricciones: List[Dict[str, Any]] = field(default_factory=list)
    sugerencias: List[str] = field(default_factory=list)


# ─── Base de conocimiento del manual ───────────────────────────────────────

class ManualMantenimiento:
    """
    Base de conocimiento del Manual de Mantenimiento de Carreteras (2016),
    adoptado mediante Resolución 04046 de 2018: clasificación de tipos de
    mantenimiento, defectología (umbrales de gravedad e intervención por
    tipo de deterioro), actividades de referencia y umbrales de prioridad.
    """

    def __init__(self):
        self._cargar_clasificaciones()
        self._cargar_defectologia()
        self._cargar_actividades()
        self._cargar_umbrales()

    def _cargar_clasificaciones(self):
        """Clasificación de mantenimiento según el manual."""
        self.clasificacion_mantenimiento = {
            TipoMantenimiento.RUTINARIO: {
                "descripcion": "Actividades de conservación continua",
                "actividades_tipicas": [
                    "Rocería y limpieza de calzada",
                    "Limpieza de cunetas y alcantarillas",
                    "Sello de fisuras y grietas",
                    "Parcheo y/o bacheo superficial",
                    "Reparación de señalización vertical y horizontal",
                ],
                "frecuencia": "Diaria o semanal",
                "responsable": "Administrador de Mantenimiento Vial",
            },
            TipoMantenimiento.PERIODICO: {
                "descripcion": "Intervenciones programadas para recuperar condiciones",
                "actividades_tipicas": [
                    "Recarpeteo superficial",
                    "Rehabilitación de capas de rodadura",
                    "Reposición de señalización",
                    "Mantenimiento de obras de arte",
                ],
                "frecuencia": "Anual o bianual",
                "responsable": "Contratista de Obra con Interventoría",
            },
            TipoMantenimiento.EMERGENCIA: {
                "descripcion": "Atención inmediata de sitios críticos",
                "actividades_tipicas": [
                    "Reparación urgente de baches profundos",
                    "Estabilización de taludes",
                    "Reparación de puentes y alcantarillas dañadas",
                    "Restablecimiento de vías afectadas",
                ],
                "frecuencia": "Inmediata (24-48 horas)",
                "responsable": "INVIAS con contratista de emergencia",
            },
        }

    def _cargar_defectologia(self):
        """Catálogo de deterioros y su cuantificación según el manual."""
        self.defectologia = {
            TipoDeterioro.BACHE: {
                "descripcion": "Hueco en la superficie de rodadura",
                "medicion": "Área (m²) y profundidad (cm)",
                "gravedad": {
                    GravedadDeterioro.BAJA: {"profundidad_max": 2.5, "area_max": 0.5},
                    GravedadDeterioro.MEDIA: {"profundidad_max": 5.0, "area_max": 2.0},
                    GravedadDeterioro.ALTA: {"profundidad_max": 10.0, "area_max": 5.0},
                    GravedadDeterioro.CRITICA: {"profundidad_max": float("inf"), "area_max": float("inf")},
                },
                "intervencion": {
                    GravedadDeterioro.BAJA: "Sello superficial",
                    GravedadDeterioro.MEDIA: "Parcheo localizado",
                    GravedadDeterioro.ALTA: "Bacheo profundo",
                    GravedadDeterioro.CRITICA: "Reconstrucción de tramo",
                },
            },
            TipoDeterioro.GRIETA: {
                "descripcion": "Abertura lineal en la superficie",
                "medicion": "Longitud (m) y ancho (mm)",
                "gravedad": {
                    GravedadDeterioro.BAJA: {"ancho_max": 3, "longitud_max": 10},
                    GravedadDeterioro.MEDIA: {"ancho_max": 6, "longitud_max": 30},
                    GravedadDeterioro.ALTA: {"ancho_max": 12, "longitud_max": 50},
                    GravedadDeterioro.CRITICA: {"ancho_max": float("inf"), "longitud_max": float("inf")},
                },
                "intervencion": {
                    GravedadDeterioro.BAJA: "Sello de fisuras",
                    GravedadDeterioro.MEDIA: "Sello con material asfáltico",
                    GravedadDeterioro.ALTA: "Parcheo o recapeo",
                    GravedadDeterioro.CRITICA: "Reconstrucción",
                },
            },
            TipoDeterioro.AHUELLAMIENTO: {
                "descripcion": "Deformación longitudinal en la rodadura",
                "medicion": "Profundidad (cm) y ancho (m)",
                "gravedad": {
                    GravedadDeterioro.BAJA: {"profundidad_max": 1.0},
                    GravedadDeterioro.MEDIA: {"profundidad_max": 2.5},
                    GravedadDeterioro.ALTA: {"profundidad_max": 5.0},
                    GravedadDeterioro.CRITICA: {"profundidad_max": float("inf")},
                },
                "intervencion": {
                    GravedadDeterioro.BAJA: "Monitoreo",
                    GravedadDeterioro.MEDIA: "Fresado superficial",
                    GravedadDeterioro.ALTA: "Fresado y recapeo",
                    GravedadDeterioro.CRITICA: "Reconstrucción de capa",
                },
            },
            TipoDeterioro.CRAQUELADO: {
                "descripcion": "Red de grietas superficiales (mapa de grietas)",
                "medicion": "Área afectada (%)",
                "gravedad": {
                    GravedadDeterioro.BAJA: {"area_max": 10},
                    GravedadDeterioro.MEDIA: {"area_max": 30},
                    GravedadDeterioro.ALTA: {"area_max": 60},
                    GravedadDeterioro.CRITICA: {"area_max": float("inf")},
                },
                "intervencion": {
                    GravedadDeterioro.BAJA: "Sello superficial",
                    GravedadDeterioro.MEDIA: "Tratamiento superficial",
                    GravedadDeterioro.ALTA: "Recapeo",
                    GravedadDeterioro.CRITICA: "Reconstrucción",
                },
            },
            TipoDeterioro.LOSA_FRAGMENTADA: {
                "descripcion": "Losa de concreto dividida en cuatro o más fragmentos",
                "medicion": "Número de fragmentos",
                "gravedad": {
                    GravedadDeterioro.BAJA: {"fragmentos_max": 4},
                    GravedadDeterioro.MEDIA: {"fragmentos_max": 8},
                    GravedadDeterioro.ALTA: {"fragmentos_max": 12},
                    GravedadDeterioro.CRITICA: {"fragmentos_max": float("inf")},
                },
                "intervencion": {
                    GravedadDeterioro.BAJA: "Sello de juntas",
                    GravedadDeterioro.MEDIA: "Reparación parcial",
                    GravedadDeterioro.ALTA: "Reemplazo de losa",
                    GravedadDeterioro.CRITICA: "Reconstrucción de tramo",
                },
            },
        }

    def _cargar_actividades(self):
        """Actividades de mantenimiento según especificaciones."""
        self.actividades_mantenimiento = {
            "sello_fisuras": {
                "descripcion": "Sello de fisuras y grietas con material asfáltico",
                "material": "Asfalto modificado o sello elastomérico",
                "equipo": "Aplicador manual o automático",
                "control_calidad": "Verificar adherencia y sellado completo",
            },
            "parcheo": {
                "descripcion": "Parcheo y/o bacheo de áreas deterioradas",
                "material": "Mezcla asfáltica en caliente o frío",
                "equipo": "Compactador, cortadora, barredora",
                "control_calidad": "Compactación al 95% del Proctor, espesor mínimo 5 cm",
            },
            "recapeo": {
                "descripcion": "Colocación de nueva capa de rodadura",
                "material": "Concreto asfáltico MDC-2",
                "equipo": "Extendedora, rodillos, camiones",
                "control_calidad": "Temperatura 140-160°C, compactación 98%",
            },
            "limpieza_drenaje": {
                "descripcion": "Limpieza de cunetas, alcantarillas y sumideros",
                "frecuencia": "Mensual en temporada seca, semanal en temporada de lluvias",
                "equipo": "Herramientas manuales o retroexcavadora",
            },
            "señalizacion": {
                "descripcion": "Reparación y reposición de señalización vial",
                "referencia": "Manual de Señalización Vial INVIAS 2004",
                "actividades": ["Pintura de rayas", "Reposición de reflectores", "Instalación de señales verticales"],
            },
        }

    def _cargar_umbrales(self):
        """Umbrales de intervención según condiciones."""
        self.umbrales_intervencion = {
            "indice_condicion": {
                "excelente": 85,
                "bueno": 70,
                "regular": 50,
                "pobre": 30,
                "critico": 0,
            },
            "prioridad_por_tpd": {
                "bajo": 500,
                "medio": 2000,
                "alto": 5000,
                "critico": 10000,
            },
            "tiempo_respuesta": {
                PrioridadIntervencion.BAJO: "30 días",
                PrioridadIntervencion.MEDIO: "15 días",
                PrioridadIntervencion.ALTO: "7 días",
                PrioridadIntervencion.CRITICO: "24-48 horas",
            },
        }


# ─── Motor de diagnóstico y planificación ──────────────────────────────────

class DiagnosticadorMantenimiento:
    """
    Motor de diagnóstico de mantenimiento basado en el Manual de Mantenimiento
    de Carreteras INVIAS 2016: determina gravedad, prioridad de intervención,
    tipo de mantenimiento recomendado y actividades específicas.
    """

    def __init__(self, manual: ManualMantenimiento):
        self.manual = manual

    def diagnosticar(self, params: ParametrosMantenimiento) -> ResultadoDiagnostico:
        """Diagnostica el deterioro y recomienda intervención según el manual."""
        restricciones: List[Dict[str, Any]] = []
        sugerencias: List[str] = []
        errores: List[str] = []

        self._validar_parametros(params, errores, sugerencias)

        gravedad = self._determinar_gravedad(params)
        restricciones.append({
            "nombre": "Gravedad del deterioro",
            "valor": gravedad.value,
            "cumple": True,
            "referencia": "Manual de Mantenimiento - Defectología",
        })

        prioridad = self._determinar_prioridad(params, gravedad)
        restricciones.append({
            "nombre": "Prioridad de intervención",
            "valor": prioridad.value,
            "cumple": True,
            "referencia": "Manual de Mantenimiento - Umbrales",
        })

        tipo_mantenimiento = self._determinar_tipo_mantenimiento(params, gravedad, prioridad)
        restricciones.append({
            "nombre": "Tipo de mantenimiento recomendado",
            "valor": tipo_mantenimiento.value,
            "cumple": True,
            "referencia": "Manual de Mantenimiento - Clasificación",
        })

        intervencion = self._obtener_intervencion(params.deterioro_tipo, gravedad)
        restricciones.append({
            "nombre": "Intervención recomendada",
            "valor": intervencion,
            "cumple": True,
            "referencia": f"Defectología - {params.deterioro_tipo.value}",
        })

        actividades = self._obtener_actividades(params, tipo_mantenimiento, intervencion)
        urgencia = self._determinar_urgencia(prioridad)
        self._generar_sugerencias(params, gravedad, prioridad, sugerencias)

        cumple = len(errores) == 0
        mensaje = "Diagnóstico completado exitosamente" if cumple else f"Se encontraron {len(errores)} advertencias"

        return ResultadoDiagnostico(
            tipo_via=params.tipo_via.value,
            tipo_mantenimiento=tipo_mantenimiento.value,
            deterioro_tipo=params.deterioro_tipo.value,
            gravedad=gravedad.value,
            prioridad=prioridad.value,
            intervencion_recomendada=intervencion,
            actividades=actividades,
            urgencia=urgencia,
            cumple=cumple,
            mensaje=mensaje,
            restricciones=restricciones,
            sugerencias=sugerencias,
        )

    def _validar_parametros(self, params: ParametrosMantenimiento, errores: List[str], sugerencias: List[str]):
        """Valida los parámetros de entrada."""
        if params.area_afectada and params.area_afectada <= 0:
            errores.append("El área afectada debe ser mayor que 0")

        if params.profundidad and params.profundidad < 0:
            errores.append("La profundidad no puede ser negativa")

        if params.indice_condicion is not None:
            if params.indice_condicion < 0 or params.indice_condicion > 100:
                errores.append("El índice de condición debe estar entre 0 y 100")
            elif params.indice_condicion < 30:
                sugerencias.append("Índice de condición crítico. Se recomienda intervención inmediata")

        if params.volumen_transito and params.volumen_transito > 5000:
            sugerencias.append("Alto volumen de tránsito. Priorizar mantenimiento para evitar afectación a usuarios")

    def _determinar_gravedad(self, params: ParametrosMantenimiento) -> GravedadDeterioro:
        """Determina la gravedad del deterioro según los parámetros."""
        deterioro = params.deterioro_tipo
        defecto = self.manual.defectologia.get(deterioro)

        if not defecto:
            return GravedadDeterioro.MEDIA

        # Si el usuario ya especificó gravedad, usarla
        if params.deterioro_gravedad:
            return params.deterioro_gravedad

        # Determinar basado en mediciones
        for g in GravedadDeterioro:
            umbrales = defecto["gravedad"].get(g, {})
            cumple = True

            if params.profundidad is not None and "profundidad_max" in umbrales:
                if params.profundidad > umbrales["profundidad_max"]:
                    cumple = False

            if params.area_afectada is not None and "area_max" in umbrales:
                if params.area_afectada > umbrales["area_max"]:
                    cumple = False

            if params.longitud is not None and "longitud_max" in umbrales:
                if params.longitud > umbrales["longitud_max"]:
                    cumple = False

            if params.ancho is not None and "ancho_max" in umbrales:
                if params.ancho > umbrales["ancho_max"]:
                    cumple = False

            if cumple:
                return g

        return GravedadDeterioro.MEDIA

    def _determinar_prioridad(
        self, params: ParametrosMantenimiento, gravedad: GravedadDeterioro
    ) -> PrioridadIntervencion:
        """Determina la prioridad de intervención."""
        prioridad_gravedad = {
            GravedadDeterioro.BAJA: PrioridadIntervencion.BAJO,
            GravedadDeterioro.MEDIA: PrioridadIntervencion.MEDIO,
            GravedadDeterioro.ALTA: PrioridadIntervencion.ALTO,
            GravedadDeterioro.CRITICA: PrioridadIntervencion.CRITICO,
        }

        prioridad = prioridad_gravedad.get(gravedad, PrioridadIntervencion.MEDIO)

        # Ajustar por volumen de tránsito
        if params.volumen_transito:
            umbrales = self.manual.umbrales_intervencion["prioridad_por_tpd"]
            if params.volumen_transito > umbrales["critico"]:
                prioridad = PrioridadIntervencion.CRITICO
            elif params.volumen_transito > umbrales["alto"] and prioridad.value < "alto":
                prioridad = PrioridadIntervencion.ALTO
            elif params.volumen_transito > umbrales["medio"] and prioridad.value < "medio":
                prioridad = PrioridadIntervencion.MEDIO

        # Ajustar por índice de condición
        if params.indice_condicion is not None:
            if params.indice_condicion < 30:
                prioridad = PrioridadIntervencion.CRITICO
            elif params.indice_condicion < 50 and prioridad.value < "alto":
                prioridad = PrioridadIntervencion.ALTO

        return prioridad

    def _determinar_tipo_mantenimiento(
        self,
        params: ParametrosMantenimiento,
        gravedad: GravedadDeterioro,
        prioridad: PrioridadIntervencion,
    ) -> TipoMantenimiento:
        """Determina el tipo de mantenimiento recomendado."""
        if prioridad == PrioridadIntervencion.CRITICO:
            return TipoMantenimiento.EMERGENCIA

        if gravedad in [GravedadDeterioro.ALTA, GravedadDeterioro.CRITICA]:
            return TipoMantenimiento.PERIODICO

        return TipoMantenimiento.RUTINARIO

    def _obtener_intervencion(self, deterioro_tipo: TipoDeterioro, gravedad: GravedadDeterioro) -> str:
        """Obtiene la intervención recomendada específica."""
        defecto = self.manual.defectologia.get(deterioro_tipo)
        if defecto:
            return defecto["intervencion"].get(gravedad, "Evaluación técnica requerida")
        return "Evaluación técnica requerida"

    def _obtener_actividades(
        self,
        params: ParametrosMantenimiento,
        tipo_mantenimiento: TipoMantenimiento,
        intervencion: str,
    ) -> List[str]:
        """Obtiene las actividades específicas de mantenimiento."""
        actividades: List[str] = []

        # Actividades base según tipo de mantenimiento
        if tipo_mantenimiento in self.manual.clasificacion_mantenimiento:
            base = self.manual.clasificacion_mantenimiento[tipo_mantenimiento]
            actividades.extend(base["actividades_tipicas"][:3])

        # Actividades específicas según deterioro
        if params.deterioro_tipo == TipoDeterioro.BACHE:
            actividades.append("Excavación y limpieza del bache")
            actividades.append("Aplicación de material de liga")
            actividades.append("Colocación y compactación de mezcla asfáltica")
        elif params.deterioro_tipo == TipoDeterioro.GRIETA:
            actividades.append("Limpieza y secado de la grieta")
            actividades.append("Aplicación de sello asfáltico")
            actividades.append("Verificación de sellado")
        elif params.deterioro_tipo == TipoDeterioro.AHUELLAMIENTO:
            actividades.append("Fresado de la superficie")
            actividades.append("Colocación de nueva capa")
            actividades.append("Compactación")

        return list(set(actividades))  # Eliminar duplicados

    def _determinar_urgencia(self, prioridad: PrioridadIntervencion) -> str:
        """Determina el nivel de urgencia basado en la prioridad."""
        tiempos = self.manual.umbrales_intervencion["tiempo_respuesta"]
        return tiempos.get(prioridad, "30 días")

    def _generar_sugerencias(
        self,
        params: ParametrosMantenimiento,
        gravedad: GravedadDeterioro,
        prioridad: PrioridadIntervencion,
        sugerencias: List[str],
    ):
        """Genera sugerencias adicionales."""
        if gravedad in [GravedadDeterioro.ALTA, GravedadDeterioro.CRITICA]:
            sugerencias.append("Realizar inspección detallada de la estructura del pavimento")

        if prioridad == PrioridadIntervencion.CRITICO:
            sugerencias.append("Intervención inmediata requerida. Activar protocolo de emergencia")

        if params.tipo_via == TipoVia.PRIMARIA and prioridad.value in ["medio", "bajo"]:
            sugerencias.append("Considerar aumentar prioridad debido a la clasificación de la vía")

        if params.deterioro_tipo == TipoDeterioro.LOSA_FRAGMENTADA:
            sugerencias.append("Verificar el estado de las juntas y barras de transferencia")

        sugerencias.append("Documentar todas las intervenciones según el Manual de Mantenimiento")


# ─── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    manual = ManualMantenimiento()
    diagnosticador = DiagnosticadorMantenimiento(manual)

    print("DIAGNÓSTICO DE MANTENIMIENTO VIAL - Manual INVIAS 2016 (Res. 04046/2018)")
    print("-" * 70)

    params_bache = ParametrosMantenimiento(
        tipo_via=TipoVia.PRIMARIA,
        tipo_mantenimiento=TipoMantenimiento.RUTINARIO,
        deterioro_tipo=TipoDeterioro.BACHE,
        deterioro_gravedad=GravedadDeterioro.MEDIA,
        area_afectada=1.5,
        profundidad=4.0,
        volumen_transito=5000,
    )

    resultado = diagnosticador.diagnosticar(params_bache)
    print(f"\nResultado: {resultado.mensaje}")
    print(f"  Tipo de vía: {resultado.tipo_via}")
    print(f"  Deterioro: {resultado.deterioro_tipo}")
    print(f"  Gravedad: {resultado.gravedad}")
    print(f"  Prioridad: {resultado.prioridad}")
    print(f"  Intervención recomendada: {resultado.intervencion_recomendada}")
    print(f"  Urgencia: {resultado.urgencia}")

    print("\nActividades recomendadas:")
    for act in resultado.actividades:
        print(f"  - {act}")

    if resultado.sugerencias:
        print("\nSugerencias:")
        for s in resultado.sugerencias:
            print(f"  - {s}")
