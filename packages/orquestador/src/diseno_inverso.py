"""Diseño inverso de una viga: la sección que cumple NSR-10 Título C al menor costo APU.

Cascada: el usuario entrega UNA vez los datos del proyecto (luz, cargas, calidad del concreto). Desde ahí
  motor-concreto (verificación normativa)  →  motor-apu (costo)  →  comparación con el diseño base.
El peso propio se recalcula para cada sección candidata (la carga depende de la dimensión).

Honestidad del resultado:
  - El porcentaje de ahorro SOLO se calcula contra un diseño base que cumple. Si el base no cumple, se reporta
    el costo mínimo para cumplir y, aparte, la corrección mínima que conserva b y h.
  - El costo es APU costo directo determinista (sin Monte Carlo), precios del catálogo de motor-apu.
  - El óptimo es global sobre la rejilla de búsqueda declarada, no sobre todos los diseños posibles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from .cargador import modulo_a4, motor_apu_cantidades, motor_concreto_sismo, motor_concreto_viga

_cant = motor_apu_cantidades()
_viga = motor_concreto_viga()
_sismo = motor_concreto_sismo()
_a4 = modulo_a4()

# Calidad del catálogo APU (psi) → f'c en MPa
FC_MPA_POR_CALIDAD = {"2000": 14.0, "2500": 17.5, "3000": 21.0, "4000": 28.0}

BASES_MM = tuple(range(250, 501, 50))
ALTURAS_MM = tuple(range(300, 801, 50))
BARRAS_DIA = ("4", "5", "6", "7", "8")
BARRAS_N = tuple(range(2, 9))
ESTRIBO_DIA = "3"
ESTRIBO_S_MM = tuple(range(300, 49, -25))   # de mayor a menor: el primero que cumple es el más económico


@dataclass(frozen=True)
class ProyectoViga:
    """Datos que el usuario ingresa una sola vez."""
    luz_m: float
    carga_muerta_kn_m: float      # sin peso propio
    carga_viva_kn_m: float
    calidad_concreto: str = "3000"
    fy_mpa: float = 420.0
    recubrimiento_mm: float = 40.0
    base: Optional[object] = None  # motor_concreto.viga.Seccion del diseño actual, si existe
    # Cascada geoespacial → sísmica: basta el municipio; Aa/Av salen del Apéndice A-4 y de ahí la capacidad mínima.
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    codigo_dane: Optional[str] = None
    capacidad: Optional[str] = None             # "DMI" | "DMO" | "DES": solo puede subir la mínima de la zona
    ancho_apoyo_m: float = 0.40                 # luz libre ln = luz - ancho
    momento_apoyo_kn_m: Optional[float] = None  # envolvente del análisis del pórtico en la cara del nudo


@dataclass(frozen=True)
class Candidato:
    seccion: object
    resultado: object
    costo_directo: float
    precio_unitario: float
    uuid_apu: str
    calidad_concreto: str

    @property
    def descripcion(self) -> str:
        s = self.seccion
        return (f"{s.b:.0f}x{s.h:.0f} mm, {s.barras_n}#{s.barras_dia}, "
                f"E#{s.estribo_dia} c/{s.estribo_s:.0f} mm, f'c={FC_MPA_POR_CALIDAD[self.calidad_concreto]:g} MPa")


@dataclass(frozen=True)
class Informe:
    optimo_global: Optional[Candidato]
    minima_intervencion: Optional[Candidato]    # conserva b y h del diseño base
    base_verificacion: Optional[object]
    base_costo: Optional[float]
    base_cumple: Optional[bool]
    ahorro_pct: Optional[float]                 # solo si el base cumple
    candidatos_evaluados: int
    candidatos_cumplen: int
    supuestos: tuple[str, ...] = field(default_factory=tuple)
    sismo: Optional[dict] = None                # fila A-4, zona y capacidad aplicada (None si no se dio municipio)


SUPUESTOS = (
    "Viga simplemente apoyada, carga uniforme gravitacional, sección rectangular, una capa de barras.",
    "Sin detallado sísmico del Capítulo C.21, sin torsión; deflexión solo por altura mínima l/16.",
    "l/16 de la Tabla C.9.5(a) verificado en el corpus; φ de cortante 0,75 sigue sin verificar contra el corpus.",
    "Costo = costo directo APU determinista del catálogo motor-apu (Barranquilla 2026), por elemento.",
    "Óptimo sobre la rejilla: b 250-500 mm, h 300-800 mm (pasos de 50), barras #4-#8, 2-8 barras, estribos #3.",
    "Modo sísmico (DMO/DES): requisitos de C.21.5 como cota conservadora, refuerzo simétrico, estribos de confinamiento en toda la luz; la demanda sísmica de flexión debe venir del análisis del pórtico.",
    "Herramienta de apoyo: el diseño debe revisarlo y firmarlo un ingeniero (ver aviso de responsabilidad profesional).",
)


def _costo(s, calidad: str, longitud_m: float) -> tuple[float, float, str]:
    geo = _cant.GeometriaElementoConcreto(
        tipo=_cant.TipoElementoConcreto.VIGA,
        base_m=s.b / 1000, altura_m=s.h / 1000, longitud_m=longitud_m,
        recubrimiento_m=s.recubrimiento / 1000,
        refuerzo_longitudinal=_cant.RefuerzoLongitudinal(s.barras_n + s.barras_sup_n, s.barras_dia),
        estribos=_cant.Estribos(s.estribo_dia, s.estribo_s / 1000),
    )
    r = _cant.calcular_apu_dinamico(geo, calidad_concreto=calidad, run_montecarlo=False)
    return r.costo_directo, r.precio_unitario, r.uuid_trazabilidad



ORDEN_CAPACIDAD = {"DMI": 0, "DMO": 1, "DES": 2}


def capacidad_aplicada(p: ProyectoViga) -> tuple[Optional[str], Optional[dict]]:
    """Cascada geoespacial → sísmica: municipio → Aa/Av (A-4) → zona (A.2.3) → capacidad mínima.

    `p.capacidad` solo puede subir la mínima de la zona, nunca bajarla. Sin municipio ni capacidad: modo gravitacional.
    """
    info = None
    cap = None
    if p.municipio or p.codigo_dane:
        fila = _a4.buscar(municipio=p.municipio, departamento=p.departamento, codigo=p.codigo_dane)
        cap = fila["capacidad_minima"]
        info = {k: fila[k] for k in ("codigo", "municipio", "departamento", "aa", "av", "zona_calculada",
                                     "capacidad_minima", "modificado_por", "fuente", "vigencia")}
    if p.capacidad:
        if p.capacidad not in ORDEN_CAPACIDAD:
            raise ValueError(f"capacidad '{p.capacidad}' no válida: {sorted(ORDEN_CAPACIDAD)}")
        if cap is None or ORDEN_CAPACIDAD[p.capacidad] >= ORDEN_CAPACIDAD[cap]:
            cap = p.capacidad
        else:
            raise ValueError(f"{p.capacidad} es menor que la capacidad mínima {cap} que exige la zona; no se permite bajarla")
    if info is not None:
        info = {**info, "capacidad_aplicada": cap}
    return cap, info


def evaluar(sec, mat, cargas, p: ProyectoViga, cap: Optional[str]):
    """Verificación gravitacional + (si DMO/DES) requisitos sísmicos de vigas. Devuelve motor_concreto Resultado."""
    r = _viga.verificar(sec, mat, cargas)
    if cap in ("DMO", "DES"):
        dem = _sismo.DemandaSismica(luz_libre_m=p.luz_m - p.ancho_apoyo_m, momento_apoyo_kn_m=p.momento_apoyo_kn_m)
        extra = tuple(_sismo.verificar_sismico(sec, mat, cargas, dem))
        v = r.verificaciones + extra
        return _viga.Resultado(all(x.cumple for x in v), r.wu, r.Mu, r.Vu, v)
    return r


def _mejor_estribo(b: float, h: float, n: int, dia: str, p: ProyectoViga, mat, cargas, cap):
    """Mayor separación de estribos que cumple todo (None si ninguna)."""
    for s_mm in ESTRIBO_S_MM:
        sec = _viga.Seccion(b=b, h=h, barras_n=n, barras_dia=dia, estribo_dia=ESTRIBO_DIA,
                            estribo_s=float(s_mm), recubrimiento=p.recubrimiento_mm,
                            barras_sup_n=n if cap in ("DMO", "DES") else 0)
        r = evaluar(sec, mat, cargas, p, cap)
        if r.cumple:
            return sec, r
    return None


def _enumerar(p: ProyectoViga, calidades: Iterable[str], bases: Iterable[float], alturas: Iterable[float]):
    cargas = _viga.Cargas(p.carga_muerta_kn_m, p.carga_viva_kn_m, p.luz_m)
    cap, _ = capacidad_aplicada(p)
    for cal in calidades:
        mat = _viga.Materiales(fc=FC_MPA_POR_CALIDAD[cal], fy=p.fy_mpa, fyt=p.fy_mpa)
        for b in bases:
            for h in alturas:
                for dia in BARRAS_DIA:
                    for n in BARRAS_N:
                        hallado = _mejor_estribo(float(b), float(h), n, dia, p, mat, cargas, cap)
                        if hallado:
                            yield cal, hallado[0], hallado[1]


def _mas_barato(p: ProyectoViga, calidades, bases, alturas) -> tuple[Optional[Candidato], int, int]:
    mejor: Optional[Candidato] = None
    cumplen = 0
    calidades, bases, alturas = tuple(calidades), tuple(bases), tuple(alturas)
    evaluados = len(calidades) * len(bases) * len(alturas) * len(BARRAS_DIA) * len(BARRAS_N)
    for cal, sec, res in _enumerar(p, calidades, bases, alturas):
        cumplen += 1
        costo, pu, uid = _costo(sec, cal, p.luz_m)
        if mejor is None or costo < mejor.costo_directo:
            mejor = Candidato(sec, res, costo, pu, uid, cal)
    return mejor, evaluados, cumplen


def diseno_inverso(p: ProyectoViga, calidades: Iterable[str] = ("3000",)) -> Informe:
    """Busca el diseño más económico que cumple; si hay diseño base lo compara con honestidad."""
    calidades = tuple(calidades)
    for c in calidades:
        if c not in FC_MPA_POR_CALIDAD:
            raise ValueError(f"calidad_concreto '{c}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")

    cap, info_sismo = capacidad_aplicada(p)
    optimo, evaluados, cumplen = _mas_barato(p, calidades, BASES_MM, ALTURAS_MM)

    base_ver = base_costo = base_cumple = ahorro = None
    minima = None
    if p.base is not None:
        cargas = _viga.Cargas(p.carga_muerta_kn_m, p.carga_viva_kn_m, p.luz_m)
        mat = _viga.Materiales(fc=FC_MPA_POR_CALIDAD[p.calidad_concreto], fy=p.fy_mpa, fyt=p.fy_mpa)
        base_ver = evaluar(p.base, mat, cargas, p, cap)
        base_cumple = base_ver.cumple
        base_costo = _costo(p.base, p.calidad_concreto, p.luz_m)[0]
        if base_cumple and optimo is not None:
            ahorro = round((base_costo - optimo.costo_directo) / base_costo * 100, 1)
        minima, _, _ = _mas_barato(p, (p.calidad_concreto,), (p.base.b,), (p.base.h,))

    return Informe(optimo, minima, base_ver, base_costo, base_cumple, ahorro, evaluados, cumplen, SUPUESTOS, info_sismo)


def resumen(i: Informe) -> str:
    """Texto para el ingeniero: cumple/no cumple + solución económica, sin prometer lo que no se calculó."""
    L: list[str] = []
    if i.sismo is not None:
        z = i.sismo
        L.append(f"Sismo (NSR-10 A-4): {z['municipio']} ({z['departamento']}) Aa={z['aa']}, Av={z['av']} → zona "
                 f"{z['zona_calculada']} → capacidad {z['capacidad_aplicada']}.")
    if i.base_verificacion is not None:
        if i.base_cumple:
            L.append(f"El diseño base CUMPLE NSR-10 (costo directo ${i.base_costo:,.0f}).")
        else:
            fallas = "; ".join(f"{f.nombre} ({f.norma}) razón {f.razon:.2f}" for f in i.base_verificacion.fallas())
            L.append(f"El diseño base NO CUMPLE: {fallas}.")
    if i.optimo_global is None:
        L.append("Ningún diseño de la rejilla cumple: aumentar luz de apoyo, reducir cargas o ampliar la rejilla.")
        return "\n".join(L)
    o = i.optimo_global
    L.append(f"Solución más económica que cumple: {o.descripcion} → costo directo ${o.costo_directo:,.0f}.")
    if i.ahorro_pct is not None:
        L.append(f"Reducción de costo frente al diseño base que ya cumplía: {i.ahorro_pct:.1f} %.")
    elif i.base_cumple is False and i.minima_intervencion is not None:
        m = i.minima_intervencion
        L.append(f"Corrección mínima conservando {i.minima_intervencion.seccion.b:.0f}x"
                 f"{i.minima_intervencion.seccion.h:.0f}: {m.descripcion} → ${m.costo_directo:,.0f} "
                 f"(el diseño base no cumplía, no se reporta % de ahorro).")
    return "\n".join(L)
