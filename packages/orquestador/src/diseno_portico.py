"""Diseño inverso de las vigas de un pórtico plano: análisis matricial → envolventes → diseño por nivel de disipación → costo APU.

Cascada completa:
  municipio → A-4 → zona → capacidad (DMI/DMO/DES)                      (motor-geopot)
  geometría + cargas + fuerzas sísmicas → rigidez directa por candidato (motor-analisis)
  casos D, L, E → combinaciones NSR-10 B.2.4 → envolvente de M⁺, M⁻, V   (motor-analisis)
  envolvente + restricciones del nivel → refuerzo superior/inferior y estribos por zona (motor-concreto)
  cantidades → costo directo APU → la sección de menor costo que cumple    (motor-apu)

Supuestos y límites (también se devuelven en el informe):
  - Una sola sección de viga para todo el pórtico, diseñada con la peor demanda de cualquier viga (conservador).
  - Columnas dadas por el usuario, NO diseñadas; sin verificación columna fuerte-viga débil (C.21.6.2) ni de nudos.
  - Rigidez agrietada: viga 0,35·Ig, columna 0,70·Ig (valores del ACI/NSR-10 C.10.10.4.1; la lista no se recuperó del corpus).
  - Ec = 4700·√f'c MPa (C.8.5.1, concreto de densidad normal, verificado). Sin deformación por cortante ni segundo orden.
  - Las fuerzas sísmicas laterales (E, ya reducidas por R) las entrega el usuario o el motor sísmico: aquí NO se calcula
    el cortante basal. Sin ellas el análisis es solo gravitacional, aunque el nivel exija detallado.
  - Costo = costo directo APU de las vigas; el costo de las columnas no entra en la comparación.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import importlib

from .cargador import cargar_motor, modulo_a4, motor_apu_cantidades, motor_concreto_viga
from .diseno_inverso import FC_MPA_POR_CALIDAD, ORDEN_CAPACIDAD

_cant = motor_apu_cantidades()
_viga = motor_concreto_viga()
cargar_motor("motor-concreto", "motor_concreto")
_dv = importlib.import_module("motor_concreto.diseno_viga")
cargar_motor("motor-analisis", "motor_analisis")
_pt = importlib.import_module("motor_analisis.portico")
_cb = importlib.import_module("motor_analisis.combinaciones")
_a4 = modulo_a4()

FACTOR_I_VIGA = 0.35
FACTOR_I_COLUMNA = 0.70
PESO_UNIT_KN_M3 = 24.0
BASES_MM = tuple(range(200, 551, 50))
ALTURAS_MM = tuple(range(300, 901, 50))


@dataclass(frozen=True)
class ProyectoPortico:
    luces_m: tuple[float, ...]                  # vanos de izquierda a derecha, entre ejes
    alturas_piso_m: tuple[float, ...]           # alturas de entrepiso desde la base
    carga_muerta_kn_m: float                    # sobre las vigas, sin peso propio de la viga
    carga_viva_kn_m: float
    columna_mm: tuple[float, float] = (400.0, 400.0)   # (c1 paralela a la viga, c2 perpendicular)
    fuerzas_laterales_kn: Optional[tuple[float, ...]] = None   # E reducida por nivel (sentido +x); None = sin sismo
    calidad_concreto: str = "3000"
    fy_mpa: float = 420.0
    recubrimiento_mm: float = 40.0
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    codigo_dane: Optional[str] = None
    capacidad: Optional[str] = None             # solo puede subir la mínima de la zona; sin municipio es obligatoria


@dataclass(frozen=True)
class CandidatoPortico:
    b: float
    h: float
    diseno: object
    costo_directo: float
    demanda: object


@dataclass(frozen=True)
class InformePortico:
    capacidad: str
    sismo: Optional[dict]
    optimo: Optional[CandidatoPortico]
    ranking: tuple[CandidatoPortico, ...]
    evaluadas: int
    factibles: int
    envolvente_gobernante: Optional[dict]       # x, M_max, M_min, V_max, V_min y combinaciones, de la viga más exigida
    supuestos: tuple[str, ...] = field(default_factory=tuple)


SUPUESTOS = (
    "Una sola sección para todas las vigas, diseñada con la peor demanda de cualquier viga (conservador).",
    "Columnas dadas, no diseñadas; sin columna fuerte-viga débil (C.21.6.2) ni nudos (C.21.7).",
    "Inercias agrietadas viga 0,35·Ig y columna 0,70·Ig (C.10.10.4.1: lista no recuperada del corpus). Ec = 4700√f'c (C.8.5.1).",
    "El cortante basal y la distribución de fuerzas sísmicas NO se calculan aquí: E llega como dato (ya reducida por R).",
    "Refuerzo longitudinal continuo en toda la luz, una capa por cara, mismo diámetro arriba y abajo; sin empalmes ni anclajes.",
    "Cortante por capacidad: DES con Mpr = 1,25·fy y φ = 0,75; DMO con Mn (C.21.3.3 (a)/(b) no recuperado). Ninguno verificado en el corpus.",
    "Costo directo APU de las vigas (Barranquilla 2026); estribos modelados con separación equivalente por conteo.",
    "Herramienta de apoyo: el diseño debe revisarlo y firmarlo un ingeniero (aviso de responsabilidad profesional, issue #18).",
)


def _capacidad(p: ProyectoPortico) -> tuple[str, Optional[dict]]:
    cap, info = None, None
    if p.municipio or p.codigo_dane:
        f = _a4.buscar(municipio=p.municipio, departamento=p.departamento, codigo=p.codigo_dane)
        cap = f["capacidad_minima"]
        info = {k: f[k] for k in ("codigo", "municipio", "departamento", "aa", "av", "zona_calculada", "capacidad_minima",
                                  "modificado_por", "fuente", "vigencia")}
    if p.capacidad:
        if p.capacidad not in ORDEN_CAPACIDAD:
            raise ValueError(f"capacidad '{p.capacidad}' no válida: {sorted(ORDEN_CAPACIDAD)}")
        if cap is not None and ORDEN_CAPACIDAD[p.capacidad] < ORDEN_CAPACIDAD[cap]:
            raise ValueError(f"{p.capacidad} es menor que la capacidad mínima {cap} que exige la zona; no se permite bajarla")
        cap = p.capacidad
    if cap is None:
        raise ValueError("Indique municipio (para derivar la capacidad de la zona) o capacidad explícita")
    if info is not None:
        info = {**info, "capacidad_aplicada": cap}
    return cap, info


def _modelo(p: ProyectoPortico, b: float, h: float):
    """Construye el pórtico; devuelve (portico, vigas_idx, w_muerta_total)."""
    fc = FC_MPA_POR_CALIDAD[p.calidad_concreto]
    Ec = 4700.0 * math.sqrt(fc) * 1000.0            # kN/m²
    nx, ny = len(p.luces_m) + 1, len(p.alturas_piso_m) + 1
    xs = [0.0]
    for L in p.luces_m:
        xs.append(xs[-1] + L)
    ys = [0.0]
    for H in p.alturas_piso_m:
        ys.append(ys[-1] + H)
    nodos = [_pt.Nodo(xs[i], ys[j]) for j in range(ny) for i in range(nx)]
    nid = lambda i, j: j * nx + i
    c1, c2 = p.columna_mm[0] / 1000, p.columna_mm[1] / 1000
    Ac = c1 * c2
    Ic = FACTOR_I_COLUMNA * c2 * c1**3 / 12     # flexión en el plano del pórtico: canto = c1 (paralela a la viga)
    Av, Iv = b * h / 1e6, FACTOR_I_VIGA * (b / 1000) * (h / 1000) ** 3 / 12
    elementos, vigas = [], []
    for j in range(ny - 1):
        for i in range(nx):
            elementos.append(_pt.Elemento(nid(i, j), nid(i, j + 1), Ec, Ac, Ic))
    for j in range(1, ny):
        for i in range(nx - 1):
            vigas.append(len(elementos))
            elementos.append(_pt.Elemento(nid(i, j), nid(i + 1, j), Ec, Av, Iv))
    apoyos = {nid(i, 0): (True, True, True) for i in range(nx)}
    w_pp = PESO_UNIT_KN_M3 * b / 1000 * h / 1000
    return _pt.Portico(nodos, elementos, apoyos), vigas, w_pp, nid, nx, ny


def _analizar(p: ProyectoPortico, b: float, h: float):
    modelo, vigas, w_pp, nid, nx, ny = _modelo(p, b, h)
    casos = {
        "D": _pt.Caso("D", uniformes={k: p.carga_muerta_kn_m + w_pp for k in vigas}),
        "L": _pt.Caso("L", uniformes={k: p.carga_viva_kn_m for k in vigas}),
    }
    if p.fuerzas_laterales_kn:
        if len(p.fuerzas_laterales_kn) != len(p.alturas_piso_m):
            raise ValueError("fuerzas_laterales_kn debe tener un valor por nivel")
        nod = {}
        for j, F in enumerate(p.fuerzas_laterales_kn, start=1):
            for i in range(nx):
                nod[nid(i, j)] = (F / nx, 0.0, 0.0)
        casos["E"] = _pt.Caso("E", nodales=nod)
    res = {k: modelo.resolver(c) for k, c in casos.items()}
    return modelo, vigas, res, w_pp


def _demanda(p: ProyectoPortico, modelo, vigas, res, w_pp, h: float):
    c1 = p.columna_mm[0] / 1000
    m_neg = m_pos_ap = m_pos_vano = v_max = v_grav = v_centro = 0.0
    ln_min, w_grav, gob = math.inf, 0.0, None
    for k in vigas:
        L = modelo.longitud(modelo.elementos[k])
        xi, xf = c1 / 2, L - c1 / 2
        x2h = (c1 / 2 + 2 * h / 1000, L - c1 / 2 - 2 * h / 1000)
        env = _cb.envolvente(modelo, res, k, posiciones_extra=(xi, xf, *x2h))
        ln_min = min(ln_min, L - c1)
        for x in (xi, xf):
            e = env.en(x)
            m_neg = max(m_neg, -e["M_min"])
            m_pos_ap = max(m_pos_ap, e["M_max"])
            v_max = max(v_max, abs(e["V_max"]), abs(e["V_min"]))
        interior = (env.x > xi) & (env.x < xf)
        m_pos_vano = max(m_pos_vano, float(env.M_max[interior].max()))
        for x in x2h:
            e = env.en(x)
            v_centro = max(v_centro, abs(e["V_max"]), abs(e["V_min"]))
        wg = 1.2 * (p.carga_muerta_kn_m + w_pp) + 1.0 * p.carga_viva_kn_m
        w_grav = max(w_grav, wg)
        v_grav = max(v_grav, wg * L / 2)
        if gob is None or m_neg >= gob["m_neg"]:
            gob = {"m_neg": m_neg, "viga": k, "env": env}
    dem = _dv.DemandaViga(luz_libre_m=ln_min, M_neg_apoyo=m_neg, M_pos_apoyo=max(m_pos_ap, 0.0),
                          M_pos_vano=max(m_pos_vano, 0.0), V_max=v_max, V_gravedad=v_grav, w_grav=w_grav, V_centro=v_centro)
    return dem, gob


def _costo_nivel(p: ProyectoPortico, d) -> float:
    """Costo directo APU de las vigas de un nivel: una viga por vano, estribos contados con la luz libre de cada vano."""
    total = 0.0
    c1_mm = p.columna_mm[0]
    for L in p.luces_m:
        ln_mm = L * 1000 - c1_mm
        n_est = max(2, _dv.contar_estribos(ln_mm, d.h, d.s_conf, d.s_centro, d.nivel != "DMI"))
        geo = _cant.GeometriaElementoConcreto(
            tipo=_cant.TipoElementoConcreto.VIGA, base_m=d.b / 1000, altura_m=d.h / 1000, longitud_m=L,
            recubrimiento_m=p.recubrimiento_mm / 1000,
            refuerzo_longitudinal=_cant.RefuerzoLongitudinal(d.n_sup + d.n_inf, d.dia),
            estribos=_cant.Estribos(d.estribo_dia, L / (n_est - 1)))   # separación equivalente: mismo conteo de estribos
        total += _cant.calcular_apu_dinamico(geo, calidad_concreto=p.calidad_concreto, run_montecarlo=False).costo_directo
    return total


def diseno_portico(p: ProyectoPortico, top: int = 5) -> InformePortico:
    if p.calidad_concreto not in FC_MPA_POR_CALIDAD:
        raise ValueError(f"calidad_concreto '{p.calidad_concreto}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")
    cap, info = _capacidad(p)
    mat = _viga.Materiales(fc=FC_MPA_POR_CALIDAD[p.calidad_concreto], fy=p.fy_mpa, fyt=p.fy_mpa)
    candidatos: list[CandidatoPortico] = []
    evaluadas = 0
    gobernante = None
    for b in BASES_MM:
        for h in ALTURAS_MM:
            evaluadas += 1
            modelo, vigas, res, w_pp = _analizar(p, float(b), float(h))
            dem, gob = _demanda(p, modelo, vigas, res, w_pp, float(h))
            disenos = _dv.disenar(float(b), float(h), dem, cap, mat, recubrimiento=p.recubrimiento_mm,
                                  columna_c1=p.columna_mm[0], columna_c2=p.columna_mm[1])
            if not disenos:
                continue
            mejor = min(disenos, key=lambda x: _costo_nivel(p, x))
            costo = _costo_nivel(p, mejor) * len(p.alturas_piso_m)
            c = CandidatoPortico(float(b), float(h), mejor, costo, dem)
            candidatos.append(c)
            if gobernante is None or costo < gobernante[0]:
                e = gob["env"]
                gobernante = (costo, {"x": e.x.tolist(), "M_max": e.M_max.tolist(), "M_min": e.M_min.tolist(),
                                      "V_max": e.V_max.tolist(), "V_min": e.V_min.tolist(),
                                      "combo_M_max": e.combo_M_max, "combo_M_min": e.combo_M_min, "combo_V": e.combo_V})
    candidatos.sort(key=lambda c: c.costo_directo)
    return InformePortico(cap, info, candidatos[0] if candidatos else None, tuple(candidatos[:top]), evaluadas,
                          len(candidatos), gobernante[1] if gobernante else None, SUPUESTOS)


def resumen(i: InformePortico) -> str:
    L: list[str] = []
    if i.sismo:
        z = i.sismo
        L.append(f"Sismo (A-4): {z['municipio']} ({z['departamento']}) Aa={z['aa']}, Av={z['av']} → zona "
                 f"{z['zona_calculada']} → capacidad {i.capacidad}.")
    else:
        L.append(f"Capacidad indicada por el usuario: {i.capacidad}.")
    if i.optimo is None:
        L.append("Ninguna sección de la rejilla cumple: revise cargas, luces, columnas o amplíe la rejilla.")
        return "\n".join(L)
    o, d = i.optimo, i.optimo.diseno
    dm = o.demanda
    L.append(f"Sección más económica que cumple: {o.b:.0f}×{o.h:.0f} mm, {d.n_sup}#{d.dia} arriba + {d.n_inf}#{d.dia} abajo, "
             f"E#{d.estribo_dia} c/{d.s_conf:.0f} mm en 2h y c/{d.s_centro:.0f} mm al centro → ${o.costo_directo:,.0f} (vigas del pórtico).")
    L.append(f"Demanda de diseño: M⁻={dm.M_neg_apoyo:.0f}, M⁺ apoyo={dm.M_pos_apoyo:.0f}, M⁺ vano={dm.M_pos_vano:.0f} kN·m; "
             f"V={dm.V_max:.0f} kN; ln={dm.luz_libre_m:.2f} m.")
    return "\n".join(L)
