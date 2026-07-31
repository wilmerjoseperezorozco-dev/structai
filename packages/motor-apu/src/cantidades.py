"""
══════════════════════════════════════════════════════════════
MOTOR APU — CÓMPUTO DE CANTIDADES PARAMÉTRICO
Columnas y vigas de concreto reforzado: cantidades calculadas desde
dimensiones geométricas reales, no un catálogo de tamaños fijos.
══════════════════════════════════════════════════════════════

Alcance deliberado: este módulo NO diseña el refuerzo de acero (eso es
diseño estructural en concreto reforzado — un módulo separado y más
grande, fuera de este alcance). Toma el refuerzo que el usuario ya
definió (número de barras, diámetro, espaciamiento de estribos) y
calcula las cantidades reales de concreto/acero/formaleta para ESA
geometría específica — a diferencia del catálogo anterior, que tenía
un único valor fijo pensado para un solo tamaño de columna/viga
(ej. "columna 40×30cm" con 0.12 m³/ml hardcodeado).

motor-deformacion (paquete hermano) verifica si una sección con su
acero YA definido cumple deflexión/pandeo — tampoco diseña refuerzo.
Ninguno de los dos motores reemplaza un diseño estructural completo
por un ingeniero; ambos asumen que el refuerzo ya fue definido.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .catalogue import P, S, engine
from .engine import MotorAPU
from .models import (
    AIU,
    APUResult,
    CategoriaObrero,
    EquipoItem,
    ManoObraItem,
    MaterialItem,
    UnidadMedida,
)

DENSIDAD_ACERO_KG_M3 = 7850.0

# Diámetros nominales de barras corrugadas (NTC 2289 / ASTM A706), en
# metros. El peso por metro se DERIVA de la geometría (área × densidad
# del acero) en vez de copiarse de una tabla de memoria — así cualquier
# diámetro que se agregue queda correcto automáticamente y es
# verificable: peso_kg_m = (π/4 × d²) × 7850.
DIAMETRO_BARRA_M: dict[str, float] = {
    "3": 0.00953,   # #3 — 3/8"
    "4": 0.01270,   # #4 — 1/2"
    "5": 0.01588,   # #5 — 5/8"
    "6": 0.01905,   # #6 — 3/4"
    "7": 0.02223,   # #7 — 7/8"
    "8": 0.02540,   # #8 — 1"
}


def peso_barra_kg_m(diametro_pulg: str) -> float:
    """Peso nominal por metro de una barra corrugada (kg/m).

    Derivado de la geometría: peso = área_transversal × densidad_acero.
    No es un valor de tabla memorizado — es reproducible a mano.
    """
    if diametro_pulg not in DIAMETRO_BARRA_M:
        disponibles = ", ".join(sorted(DIAMETRO_BARRA_M))
        raise ValueError(f"Diámetro '{diametro_pulg}' no reconocido. Disponibles: {disponibles}")
    d = DIAMETRO_BARRA_M[diametro_pulg]
    area_m2 = math.pi / 4 * d**2
    return area_m2 * DENSIDAD_ACERO_KG_M3


class TipoElementoConcreto(str, Enum):
    COLUMNA = "columna"
    VIGA = "viga"


@dataclass
class RefuerzoLongitudinal:
    """Acero longitudinal ya definido por el usuario (no se diseña aquí)."""
    numero_barras: int
    diametro_pulg: str  # clave de DIAMETRO_BARRA_M

    def __post_init__(self) -> None:
        if self.numero_barras <= 0:
            raise ValueError("numero_barras debe ser positivo")


@dataclass
class Estribos:
    """Refuerzo transversal (flejes) ya definido por el usuario."""
    diametro_pulg: str
    espaciamiento_m: float
    # Longitud adicional por los 2 ganchos a 135° (desarrollo sísmico
    # NSR-10 C.7.10 / C.21) — aproximación razonable, no un valor exacto
    # de norma; ajustable si el diseño real usa otra longitud de gancho.
    gancho_desarrollo_m: float = 0.10

    def __post_init__(self) -> None:
        if self.espaciamiento_m <= 0:
            raise ValueError("espaciamiento_m debe ser positivo")


@dataclass
class GeometriaElementoConcreto:
    tipo: TipoElementoConcreto
    base_m: float
    altura_m: float
    longitud_m: float
    # Recubrimiento libre — NSR-10 C.7.7 (4 cm típico para elementos
    # interiores no expuestos a intemperie ni contacto con el suelo).
    recubrimiento_m: float = 0.04
    refuerzo_longitudinal: Optional[RefuerzoLongitudinal] = None
    estribos: Optional[Estribos] = None
    # False (defecto) = viga colada monolítica con losa, no se forma la
    # cara superior. True = viga aislada, se forman las 4 caras.
    incluye_cara_superior_formaleta: bool = False

    def __post_init__(self) -> None:
        if self.base_m <= 0 or self.altura_m <= 0 or self.longitud_m <= 0:
            raise ValueError("base_m, altura_m y longitud_m deben ser positivos")
        if self.recubrimiento_m * 2 >= min(self.base_m, self.altura_m):
            raise ValueError("El recubrimiento es demasiado grande para esta sección")


@dataclass
class CantidadesConcreto:
    volumen_concreto_m3: float
    peso_acero_longitudinal_kg: float
    peso_acero_estribos_kg: float
    peso_acero_total_kg: float
    area_formaleta_m2: float
    numero_estribos: int


def calcular_cantidades(geo: GeometriaElementoConcreto) -> CantidadesConcreto:
    """Cómputo de cantidades reales a partir de la geometría del elemento.

    Reemplaza el catálogo estático de tamaños fijos: la misma fórmula
    sirve para cualquier b, h, L — no hace falta un caso hardcodeado
    por cada tamaño de columna o viga.
    """
    volumen = geo.base_m * geo.altura_m * geo.longitud_m

    peso_longitudinal = 0.0
    if geo.refuerzo_longitudinal is not None:
        rl = geo.refuerzo_longitudinal
        peso_longitudinal = rl.numero_barras * geo.longitud_m * peso_barra_kg_m(rl.diametro_pulg)

    peso_estribos = 0.0
    numero_estribos = 0
    if geo.estribos is not None:
        est = geo.estribos
        numero_estribos = math.floor(geo.longitud_m / est.espaciamiento_m) + 1
        perimetro_estribo = 2 * (
            (geo.base_m - 2 * geo.recubrimiento_m) + (geo.altura_m - 2 * geo.recubrimiento_m)
        )
        longitud_por_estribo = perimetro_estribo + est.gancho_desarrollo_m
        peso_estribos = numero_estribos * longitud_por_estribo * peso_barra_kg_m(est.diametro_pulg)

    if geo.tipo == TipoElementoConcreto.COLUMNA:
        # Las 4 caras laterales se forman siempre en una columna.
        area_formaleta = 2 * (geo.base_m + geo.altura_m) * geo.longitud_m
    else:
        # Viga: 2 caras laterales + fondo. La cara superior normalmente
        # no se forma (se funde monolítica con la losa) salvo que el
        # usuario indique lo contrario.
        caras_m = 2 * geo.altura_m + geo.base_m
        if geo.incluye_cara_superior_formaleta:
            caras_m += geo.base_m
        area_formaleta = caras_m * geo.longitud_m

    return CantidadesConcreto(
        volumen_concreto_m3=round(volumen, 4),
        peso_acero_longitudinal_kg=round(peso_longitudinal, 2),
        peso_acero_estribos_kg=round(peso_estribos, 2),
        peso_acero_total_kg=round(peso_longitudinal + peso_estribos, 2),
        area_formaleta_m2=round(area_formaleta, 3),
        numero_estribos=numero_estribos,
    )


# ── Precio de concreto por resistencia (mismas claves del catálogo P) ──
CALIDAD_CONCRETO_A_CLAVE_PRECIO: dict[str, str] = {
    "2000": "CTO_2000",
    "2500": "CTO_2500",
    "3000": "CTO_3000",
    "4000": "CTO_4000",
}

# Rendimientos de referencia (ml de elemento por día-cuadrilla), tomados
# de las mismas cuadrillas/rendimientos que ya usaba el catálogo estático
# para columnas y vigas de concreto — razonables como constantes dentro
# de un rango de tamaño típico, a diferencia de las CANTIDADES de
# materiales (que sí dependen fuertemente del tamaño y por eso se
# calculan arriba en vez de copiarse).
_RENDIMIENTO_ML_DIA = {
    TipoElementoConcreto.COLUMNA: 4.0,
    TipoElementoConcreto.VIGA: 5.0,
}
_VIBRADOR_DIA_POR_ML = 0.08


def calcular_apu_dinamico(
    geo: GeometriaElementoConcreto,
    calidad_concreto: str = "3000",
    aiu: Optional[AIU] = None,
) -> APUResult:
    """Calcula el APU completo (materiales + mano de obra + equipo +
    Monte Carlo) de una columna o viga de concreto reforzado a partir de
    su geometría real, en vez de un tamaño fijo de catálogo.

    Reutiliza el motor matemático existente (MotorAPU.calcular_apu) sin
    modificarlo — solo cambia CÓMO se arman las cantidades de entrada.
    """
    if calidad_concreto not in CALIDAD_CONCRETO_A_CLAVE_PRECIO:
        disponibles = ", ".join(sorted(CALIDAD_CONCRETO_A_CLAVE_PRECIO))
        raise ValueError(f"calidad_concreto '{calidad_concreto}' no reconocida. Disponibles: {disponibles}")

    cant = calcular_cantidades(geo)
    precio_concreto = P[CALIDAD_CONCRETO_A_CLAVE_PRECIO[calidad_concreto]]

    materiales = [
        MaterialItem(
            "CTO", f"Concreto {calidad_concreto} PSI", UnidadMedida.M3,
            cant.volumen_concreto_m3, precio_concreto, desperdicio=0.03,
        ),
    ]
    if cant.peso_acero_total_kg > 0:
        materiales.append(
            MaterialItem(
                "ACE", "Acero corrugado figurado (long. + estribos)", UnidadMedida.KG,
                cant.peso_acero_total_kg, P["ACE_FIG_KG"], desperdicio=0.03,
            )
        )
        materiales.append(
            MaterialItem(
                "ALM", "Alambre negro #18 para amarre", UnidadMedida.KG,
                cant.peso_acero_total_kg * 0.02, P["ALM_18_KG"], desperdicio=0.05,
            )
        )
    materiales.append(
        MaterialItem(
            "FORM", "Formaleta con accesorios", UnidadMedida.M2,
            cant.area_formaleta_m2, P["FORM_M2"], desperdicio=0.10,
        )
    )
    materiales.append(
        MaterialItem(
            "DESENC", "Desencofrante emulsionado", UnidadMedida.UN,
            cant.area_formaleta_m2 * 0.04, P["DESENC_LT"],
        )
    )

    rendimiento_ml_dia = _RENDIMIENTO_ML_DIA[geo.tipo]
    rendimiento_efectivo = rendimiento_ml_dia / geo.longitud_m
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL, 1.0, rendimiento_efectivo, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, rendimiento_efectivo, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem(
            "VIB", "Vibrador de concreto a gasolina", UnidadMedida.DIA,
            _VIBRADOR_DIA_POR_ML * geo.longitud_m, 1.0, P["VIB_DIA"],
        ),
    ]

    tipo_label = "Columna" if geo.tipo == TipoElementoConcreto.COLUMNA else "Viga"
    dims_cm = f"{round(geo.base_m * 100)}×{round(geo.altura_m * 100)}cm"
    return engine.calcular_apu(
        actividad_id=f"C.{geo.tipo.value.upper()[:3]}.DIN",
        descripcion=(
            f"{tipo_label} {dims_cm} × {geo.longitud_m:.2f}m — "
            f"concreto {calidad_concreto} PSI, cantidades calculadas por geometría"
        ),
        unidad=UnidadMedida.UN,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        aiu=aiu,
        capitulo="C — Concreto Estructural",
        norma_ref="NSR-10 C.21 (columnas) / C.11 (vigas) — cantidades calculadas, no de catálogo",
    )
