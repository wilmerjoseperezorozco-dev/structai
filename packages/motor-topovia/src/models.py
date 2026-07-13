"""
══════════════════════════════════════════════════════════════
MOTOR TOPOVÍA — MODELOS DE DATOS
Topografía + Diseño Vial — Colombia (MAGNA-SIRGAS / INVÍAS)
══════════════════════════════════════════════════════════════
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math


# ─── Enums ───────────────────────────────────────────────────

class OrigenGaussKruger(str, Enum):
    BOGOTA = "Bogotá"
    ESTE = "Este"
    ESTE_ESTE = "Este-Este"
    OESTE = "Oeste"
    OESTE_OESTE = "Oeste-Oeste"


class OrdenPoligonal(str, Enum):
    PRIMER_ORDEN = "1er orden"
    SEGUNDO_ORDEN = "2do orden"
    TERCER_ORDEN = "3er orden"
    TOPOGRAFICO = "Topográfico"
    PRELIMINAR = "Preliminar"


class MetodoCompensacion(str, Enum):
    BOWDITCH = "Bowditch"
    TRANSITO = "Tránsito"


class TipoTerreno(str, Enum):
    PLANO = "Plano"
    ONDULADO = "Ondulado"
    MONTANOSO = "Montañoso"
    ESCARPADO = "Escarpado"


class CategoriaVia(str, Enum):
    AUTOPISTA = "Autopista"
    MULTICARRIL = "Multicarril"
    DOS_CARRILES = "Dos carriles"
    TERCIARIA = "Terciaria"


# ─── Constantes IGAC / INVÍAS ────────────────────────────────

TOLERANCIA_ANGULAR: dict[OrdenPoligonal, float] = {
    OrdenPoligonal.PRIMER_ORDEN: 1.5,
    OrdenPoligonal.SEGUNDO_ORDEN: 3.0,
    OrdenPoligonal.TERCER_ORDEN: 8.0,
    OrdenPoligonal.TOPOGRAFICO: 15.0,
    OrdenPoligonal.PRELIMINAR: 30.0,
}

PRECISION_LINEAL: dict[OrdenPoligonal, float] = {
    OrdenPoligonal.PRIMER_ORDEN: 1 / 100_000,
    OrdenPoligonal.SEGUNDO_ORDEN: 1 / 50_000,
    OrdenPoligonal.TERCER_ORDEN: 1 / 10_000,
    OrdenPoligonal.TOPOGRAFICO: 1 / 5_000,
    OrdenPoligonal.PRELIMINAR: 1 / 3_000,
}

MERIDIANOS_CENTRALES: dict[OrigenGaussKruger, float] = {
    OrigenGaussKruger.BOGOTA: -74.077508,
    OrigenGaussKruger.ESTE: -71.077508,
    OrigenGaussKruger.ESTE_ESTE: -68.080917,
    OrigenGaussKruger.OESTE: -77.077508,
    OrigenGaussKruger.OESTE_OESTE: -80.077508,
}

VELOCIDADES_DISENO: dict[CategoriaVia, dict[TipoTerreno, int]] = {
    CategoriaVia.AUTOPISTA: {
        TipoTerreno.PLANO: 110, TipoTerreno.ONDULADO: 100,
        TipoTerreno.MONTANOSO: 80, TipoTerreno.ESCARPADO: 60,
    },
    CategoriaVia.MULTICARRIL: {
        TipoTerreno.PLANO: 100, TipoTerreno.ONDULADO: 80,
        TipoTerreno.MONTANOSO: 60, TipoTerreno.ESCARPADO: 50,
    },
    CategoriaVia.DOS_CARRILES: {
        TipoTerreno.PLANO: 80, TipoTerreno.ONDULADO: 60,
        TipoTerreno.MONTANOSO: 40, TipoTerreno.ESCARPADO: 30,
    },
    CategoriaVia.TERCIARIA: {
        TipoTerreno.PLANO: 40, TipoTerreno.ONDULADO: 30,
        TipoTerreno.MONTANOSO: 20, TipoTerreno.ESCARPADO: 20,
    },
}


# ─── Dataclasses ─────────────────────────────────────────────

@dataclass(frozen=True)
class Punto:
    """Punto topográfico con coordenadas planas MAGNA-SIRGAS"""
    id: str
    norte: float
    este: float
    cota: float = 0.0
    descripcion: str = ""


@dataclass(frozen=True)
class Vertice:
    """Vértice de poligonal con observaciones de campo"""
    id: str
    angulo_horizontal: float  # grados decimales (ángulo interior)
    distancia_al_siguiente: float  # metros (distancia horizontal)
    norte: float = 0.0
    este: float = 0.0
    cota: float = 0.0


@dataclass(frozen=True)
class LadoPoligonal:
    """Lado calculado de la poligonal"""
    desde: str
    hasta: str
    azimut: float  # grados decimales
    distancia: float  # metros
    delta_norte: float
    delta_este: float
    delta_norte_corregido: float = 0.0
    delta_este_corregido: float = 0.0


@dataclass(frozen=True)
class ResultadoPoligonal:
    """Resultado completo del cálculo de poligonal cerrada"""
    vertices: list[Vertice]
    lados: list[LadoPoligonal]
    coordenadas_finales: list[Punto]
    # Cierre
    suma_angulos_observados: float
    suma_angulos_teorica: float
    error_angular: float  # segundos
    tolerancia_angular: float  # segundos
    cumple_angular: bool
    error_norte: float
    error_este: float
    error_lineal: float
    perimetro: float
    precision: float  # 1:X
    precision_requerida: float  # 1:X
    cumple_lineal: bool
    metodo_compensacion: MetodoCompensacion
    orden: OrdenPoligonal


@dataclass(frozen=True)
class SeccionTransversal:
    """Sección transversal del terreno"""
    abscisa: float  # K+xxx
    puntos: list[tuple[float, float]]  # (distancia al eje, cota relativa)
    cota_eje_terreno: float
    cota_eje_rasante: float = 0.0

    @property
    def es_corte(self) -> bool:
        return self.cota_eje_rasante > self.cota_eje_terreno

    @property
    def altura_corte_relleno(self) -> float:
        return self.cota_eje_rasante - self.cota_eje_terreno


@dataclass(frozen=True)
class ResultadoVolumen:
    """Resultado de cálculo de volúmenes entre secciones"""
    abscisa_inicio: float
    abscisa_fin: float
    area_corte_1: float
    area_corte_2: float
    area_relleno_1: float
    area_relleno_2: float
    volumen_corte: float  # m³
    volumen_relleno: float  # m³
    distancia: float


@dataclass(frozen=True)
class DiagramaMasas:
    """Punto del diagrama de masas (Bruckner)"""
    abscisa: float
    ordenada: float  # Σ(corte - relleno) acumulado
    volumen_corte_acumulado: float
    volumen_relleno_acumulado: float


@dataclass(frozen=True)
class CurvaHorizontal:
    """Elementos de curva circular simple"""
    pi_norte: float
    pi_este: float
    radio: float
    deflexion: float  # grados (ángulo central Δ)
    # Calculados
    tangente: float = 0.0
    longitud: float = 0.0
    externa: float = 0.0
    ordenada_media: float = 0.0
    cuerda_larga: float = 0.0
    pc_abscisa: float = 0.0
    pt_abscisa: float = 0.0


@dataclass(frozen=True)
class ResultadoPavimento:
    """Resultado del diseño de pavimento AASHTO 93"""
    sn_requerido: float
    espesor_carpeta_cm: float
    espesor_base_cm: float
    espesor_subbase_cm: float
    sn_proporcionado: float
    cbr_subrasante: float
    mr_psi: float
    w18: float
    confiabilidad: float
    cumple: bool
