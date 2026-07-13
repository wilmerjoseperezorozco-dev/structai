"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — CATÁLOGO DE MATERIALES Y EJEMPLOS
Propiedades elásticas de referencia (NSR-10 / AISC / ASTM). Concreto y
madera se modelan como elástico-lineales isotrópicos — válido para
verificación de deflexión en servicio (ELS) y estimaciones de primer
orden; NO sustituye el diseño por resistencia (ELU) de las Títulos
C (concreto) y G (madera) de la NSR-10 para el diseño final.
══════════════════════════════════════════════════════════════
"""
import math

from .models import (
    CargaAplicada, CondicionApoyo, ElementoEstructural, Material, TipoCarga, TipoElemento,
)
from .geometry import seccion_rectangular, seccion_I
# Importación diferida de MotorDeformacion dentro de cada función de ejemplo
# para evitar import circular (engine → clasificador → catalogue → engine).


def _Ec_concreto_MPa(fc_MPa: float) -> float:
    """Módulo de elasticidad secante del concreto — NSR-10 C.8.5.1 / ACI 318: Ec = 4700·√f'c (MPa)."""
    return 4700.0 * math.sqrt(fc_MPa)


MATERIALES: dict[str, Material] = {
    "ACERO_A36": Material.desde_MPa("Acero ASTM A36", E_MPa=200_000, fy_MPa=250, fu_MPa=400, nu=0.30, cov_fy=0.08),
    "ACERO_A572_50": Material.desde_MPa("Acero ASTM A572 Gr.50", E_MPa=200_000, fy_MPa=345, fu_MPa=450, nu=0.30, cov_fy=0.08),
    "ACERO_G60_REFUERZO": Material.desde_MPa("Acero refuerzo G-60", E_MPa=200_000, fy_MPa=420, fu_MPa=620, nu=0.30, cov_fy=0.06),
    "CONCRETO_21MPA": Material.desde_MPa("Concreto f'c=21 MPa (3000 PSI)", E_MPa=_Ec_concreto_MPa(21), fy_MPa=21, nu=0.20, densidad=2400, cov_E=0.10, cov_fy=0.12),
    "CONCRETO_28MPA": Material.desde_MPa("Concreto f'c=28 MPa (4000 PSI)", E_MPa=_Ec_concreto_MPa(28), fy_MPa=28, nu=0.20, densidad=2400, cov_E=0.10, cov_fy=0.12),
    "MADERA_ES1": Material.desde_MPa("Madera estructural grupo ES1 (NSR-10 Título G)", E_MPa=11_000, fy_MPa=20, nu=0.30, densidad=550, cov_E=0.15, cov_fy=0.18),
    "ALUMINIO_6061T6": Material.desde_MPa("Aluminio 6061-T6", E_MPa=69_000, fy_MPa=276, fu_MPa=310, nu=0.33, densidad=2700, cov_fy=0.06),
}


def ejemplo_viga_acero_simplemente_apoyada():
    """Viga IPE de acero A36, luz 6 m, simplemente apoyada, carga viva puntual + peso propio UDL."""
    from .engine import MotorDeformacion
    elemento = ElementoEstructural(
        id="V-01", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["ACERO_A36"],
        seccion=seccion_I(b_ala=0.15, t_ala=0.012, h_alma=0.30, t_alma=0.008),
        longitud=6.0, condicion_apoyo=CondicionApoyo.SIMPLE,
    )
    cargas = [
        CargaAplicada(tipo=TipoCarga.PUNTUAL, magnitud=25_000, posicion=0.5, cov_carga=0.20, descripcion="Carga viva puntual"),
        CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=3_500, cov_carga=0.08, descripcion="Peso propio + carga muerta"),
    ]
    return MotorDeformacion().analizar_viga(elemento, cargas)


def ejemplo_viga_concreto_cantilever():
    """Voladizo de concreto reforzado 30×50 cm, 2.5 m, carga distribuida uniforme."""
    from .engine import MotorDeformacion
    elemento = ElementoEstructural(
        id="V-CANT-01", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["CONCRETO_21MPA"],
        seccion=seccion_rectangular(b=0.30, h=0.50),
        longitud=2.5, condicion_apoyo=CondicionApoyo.CANTILEVER,
    )
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=12_000, cov_carga=0.15, descripcion="Carga distribuida de losa")]
    return MotorDeformacion().analizar_viga(elemento, cargas)


def ejemplo_columna_acero():
    """Columna tubular de acero A572, altura 3.5 m, apoyos empotrada-empotrada, carga axial de servicio."""
    from .engine import MotorDeformacion
    elemento = ElementoEstructural(
        id="C-01", tipo_elemento=TipoElemento.COLUMNA,
        material=MATERIALES["ACERO_A572_50"],
        seccion=seccion_rectangular(b=0.20, h=0.20),
        longitud=3.5, condicion_apoyo=CondicionApoyo.EMPOTRADA_EMPOTRADA,
    )
    carga_axial = CargaAplicada(tipo=TipoCarga.PUNTUAL, magnitud=450_000, cov_carga=0.18, descripcion="Carga axial de servicio")
    return MotorDeformacion().analizar_columna(elemento, carga_axial, momento_adicional=8_000)
