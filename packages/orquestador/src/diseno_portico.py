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
  - Rigidez agrietada: viga 0,35·Ig, columna 0,70·Ig (verificados en C.10.10.4.1).
  - Ec = 4700·√f'c MPa (C.8.5.1, concreto de densidad normal, verificado). Sin deformación por cortante ni segundo orden.
  - Las fuerzas sísmicas laterales (E, ya reducidas por R) las entrega el usuario o el motor sísmico: aquí NO se calcula
    el cortante basal. Sin ellas el análisis es solo gravitacional, aunque el nivel exija detallado.
  - Costo = costo directo APU de las vigas; el costo de las columnas no entra en la comparación.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

import importlib

from .cargador import cargar_motor, modulo_a4, modulo_cortante_basal, motor_apu_cantidades, motor_concreto_viga
from .diseno_inverso import FC_MPA_POR_CALIDAD, ORDEN_CAPACIDAD
from . import grilla_vectorizada as _gv
from . import sismo_portico as _sp

_cant = motor_apu_cantidades()
_viga = motor_concreto_viga()
cargar_motor("motor-concreto", "motor_concreto")
_dv = importlib.import_module("motor_concreto.diseno_viga")
cargar_motor("motor-analisis", "motor_analisis")
_pt = importlib.import_module("motor_analisis.portico")
_cb = importlib.import_module("motor_analisis.combinaciones")
_a4 = modulo_a4()
_sp_cb = modulo_cortante_basal()

FACTOR_I_VIGA = 0.35
FACTOR_I_COLUMNA = 0.70
PESO_UNIT_KN_M3 = 24.0
BASES_MM = tuple(range(200, 551, 50))
ALTURAS_MM = tuple(range(300, 901, 50))
DERIVA_MAX = 0.010                              # Tabla A.6.4-1, concreto reforzado


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
    perfil_suelo: Optional[str] = None          # "A".."E": si se da, E se DERIVA del espectro (A.4.3) y se verifica la deriva (A.6.4)
    grupo_uso: str = "I"                        # I, II, III, IV (Tabla A.2.5-1)
    aa: Optional[float] = None                  # opcionales: reemplazan a los del Apéndice A-4
    av: Optional[float] = None
    factor_deriva_fisurada: float = 1.0         # 0,7 solo si se quiere usar el permiso de A.6.4.1.1 (por defecto conservador)
    preseleccion: Optional[int] = None          # None = diseño exacto de todas; K = recorrer por proxy hasta reunir K diseños factibles


@dataclass(frozen=True)
class CandidatoPortico:
    b: float
    h: float
    diseno: object
    costo_directo: float
    demanda: object
    deriva: float = math.nan               # máx Δ/hp con Fs (I=1); NaN si no se calculó


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
    basal: Optional[dict] = None                # cortante basal y parámetros espectrales de la sección óptima
    diagnostico: dict = field(default_factory=dict)   # embudo, tiempos y paridad escalar-vectorizada


SUPUESTOS = (
    "Una sola sección para todas las vigas, diseñada con la peor demanda de cualquier viga (conservador).",
    "Columnas dadas, no diseñadas; sin columna fuerte-viga débil (C.21.6.2) ni nudos (C.21.7).",
    "Inercias agrietadas viga 0,35·Ig y columna 0,70·Ig (C.10.10.4.1 verificado en el corpus). Ec = 4700√f'c (C.8.5.1).",
    "Con perfil_suelo, E se deriva del espectro NSR-10 (Fa/Fv, Sa, Ta, Vs=Sa·W, Cvx, R=R0 de la Tabla A.3-3 con φ=1): estructura regular y redundante, sin torsión, sin P-Delta, peso sísmico = muerta + peso propio (sin viva), T = Ta. Sin perfil_suelo, E llega como dato (ya reducida por R).",
    "Deriva (A.6.4, 1,0 % hp) con las mismas inercias agrietadas, Fs sin dividir por R (I=1 permitido por A.6.2.1.2), en el centro de masa; sin torsión ni P-Delta. Solo se verifica si E se deriva del espectro.",
    "Refuerzo longitudinal continuo en toda la luz, una capa por cara, mismo diámetro arriba y abajo; sin empalmes ni anclajes.",
    "Cortante por capacidad: φ = 0,75 verificado (C.9.3.2.3); DES con Mpr = 1,25·fy (notación C.2) y DMO con Mn (C.21.3.3 (a)/(b)) verificados en el corpus.",
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


def _analizar(p: ProyectoPortico, b: float, h: float, fuerzas=None):
    modelo, vigas, w_pp, nid, nx, ny = _modelo(p, b, h)
    casos = {
        "D": _pt.Caso("D", uniformes={k: p.carga_muerta_kn_m + w_pp for k in vigas}),
        "L": _pt.Caso("L", uniformes={k: p.carga_viva_kn_m for k in vigas}),
    }
    laterales = fuerzas if fuerzas is not None else p.fuerzas_laterales_kn
    if laterales:
        if len(laterales) != len(p.alturas_piso_m):
            raise ValueError("fuerzas_laterales_kn debe tener un valor por nivel")
        nod = {}
        for j, F in enumerate(laterales, start=1):
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


def _ctx_sismico(p: ProyectoPortico, cap: str, info: Optional[dict]):
    if p.perfil_suelo is None:
        return None
    if p.fuerzas_laterales_kn:
        raise ValueError("Con perfil_suelo las fuerzas sísmicas se derivan del espectro: no entregue fuerzas_laterales_kn")
    aa = p.aa if p.aa is not None else (info or {}).get("aa")
    av = p.av if p.av is not None else (info or {}).get("av")
    return _sp.contexto_desde(aa, av, p.perfil_suelo, p.grupo_uso, cap)


def _basal_escalar(p: ProyectoPortico, ctx, b: float, h: float):
    nx = len(p.luces_m) + 1
    pesos = tuple(float(x) for x in _sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, p.carga_muerta_kn_m, p.columna_mm, b, h))
    return _sp.fuerzas_escalar(ctx, pesos, _sp.alturas_nivel_m(p.alturas_piso_m)), pesos


def _ux_niveles(res, nid, nx: int, ny: int) -> list[float]:
    u = res["E"].u
    return [sum(u[nid(i, j)][0] for i in range(nx)) / nx for j in range(1, ny)]


def _deriva_escalar(p: ProyectoPortico, res, nid, nx: int, ny: int, cbz) -> float:
    """máx Δ/hp con las fuerzas elásticas de deriva (I=1): δ(Fs) = R·(Sa_deriva/Sa)·δ(E)."""
    ux = [0.0] + _ux_niveles(res, nid, nx, ny)
    factor = cbz.r * cbz.sa_deriva / cbz.sa
    return max(abs(ux[j] - ux[j - 1]) * factor / p.alturas_piso_m[j - 1] for j in range(1, ny))


def _precios_relativos(p: ProyectoPortico) -> float:
    """Costo relativo acero/concreto (por m² de sección) medido con el propio APU; solo ordena la preselección."""
    L = max(p.luces_m)

    def costo(b, h, n):
        geo = _cant.GeometriaElementoConcreto(
            tipo=_cant.TipoElementoConcreto.VIGA, base_m=b, altura_m=h, longitud_m=L, recubrimiento_m=p.recubrimiento_mm / 1000,
            refuerzo_longitudinal=_cant.RefuerzoLongitudinal(n, "5"), estribos=_cant.Estribos("3", 0.15))
        return _cant.calcular_apu_dinamico(geo, calidad_concreto=p.calidad_concreto, run_montecarlo=False).costo_directo

    base = costo(0.30, 0.50, 4)
    d_conc = (costo(0.30, 0.60, 4) - base) / (0.30 * 0.10)          # costo por m² de sección de concreto
    d_acero = (costo(0.30, 0.50, 6) - base) / (2 * 199e-6)          # costo por m² de acero (2 barras #5)
    return max(d_acero / max(d_conc, 1e-9), 1.0)


def _derivar_basal(p: ProyectoPortico, ctx, o: "CandidatoPortico", res, nid, nx: int, ny: int, cbz, pesos) -> dict:
    der = _deriva_escalar(p, res, nid, nx, ny, cbz)
    t_ray = _sp.periodo_rayleigh(np.array(pesos), np.array(cbz.fuerzas_elasticas_kn), np.array(_ux_niveles(res, nid, nx, ny)) * cbz.r)
    ok = t_ray == t_ray
    t_uso = min(t_ray, cbz.cu_ta) if ok else cbz.T
    sa_ray = _sp_cb.sa_espectro(t_uso, cbz.aa, cbz.av, cbz.fa, cbz.fv, cbz.I)
    cambia = bool(abs(sa_ray - cbz.sa) > 1e-9 or abs(_sp_cb.exponente_k(t_uso) - cbz.k) > 1e-9)
    return {"aa": cbz.aa, "av": cbz.av, "perfil": cbz.perfil, "grupo_uso": cbz.grupo_uso, "Fa": cbz.fa, "Fv": cbz.fv, "I": cbz.I,
            "Ta_s": cbz.T, "Cu_Ta_s": cbz.cu_ta, "Tc_s": cbz.tc, "TL_s": cbz.tl, "Sa": cbz.sa, "k": cbz.k, "R": cbz.r,
            "peso_sismico_kn": cbz.peso_total_kn, "Vs_elastico_kn": cbz.vs_kn, "Vs_diseno_kn": cbz.vs_kn / cbz.r,
            "fuerzas_por_nivel_kn": list(cbz.fuerzas_elasticas_kn), "E_diseno_por_nivel_kn": list(cbz.fuerzas_diseno_kn),
            "deriva_max_pct_hp": 100 * der, "limite_deriva_pct_hp": 100 * DERIVA_MAX, "periodo_rayleigh_s": t_ray,
            "rayleigh_dentro_de_cu_ta": bool(t_ray <= cbz.cu_ta) if ok else None,
            "rayleigh_vs_ta_dif_pct": 100 * (t_ray - cbz.T) / cbz.T if ok else None,
            "rayleigh_cambia_las_fuerzas": cambia if ok else None}


def _lote_vectorizado(p: ProyectoPortico, ctx, b_all: np.ndarray, h_all: np.ndarray, con_columnas: bool = False):
    """Etapa vectorizada: plantilla + fuerzas sísmicas derivadas + análisis de todas las secciones (b_all, h_all)."""
    N, n_lev = b_all.size, len(p.alturas_piso_m)
    modelo0, vigas0, _, nid, nx, ny = _modelo(p, 300.0, 500.0)
    tpl = _gv.construir_plantilla(modelo0, vigas0, nid, nx, ny, _pt)
    Ec = 4700.0 * math.sqrt(FC_MPA_POR_CALIDAD[p.calidad_concreto]) * 1000.0
    alt_niv = _sp.alturas_nivel_m(p.alturas_piso_m)
    pesos = fuerzas = None
    r_deriva = 1.0
    if ctx is not None:
        pesos = _sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, p.carga_muerta_kn_m, p.columna_mm, b_all, h_all)
        par = _sp.parametros_espectro(ctx, alt_niv)
        fuerzas = _sp.fuerzas_vectorizadas(par, pesos, alt_niv)
        r_deriva = par["r"] * par["sa_deriva"] / par["sa"]
    elif p.fuerzas_laterales_kn:
        fuerzas = np.broadcast_to(np.asarray(p.fuerzas_laterales_kn, dtype=float), (N, n_lev)).copy()
    lote = _gv.analizar_lote(tpl, b_mm=b_all, h_mm=h_all, Ec=Ec, factor_i_viga=FACTOR_I_VIGA, carga_muerta=p.carga_muerta_kn_m,
                             carga_viva=p.carga_viva_kn_m, peso_unit=PESO_UNIT_KN_M3, c1_m=p.columna_mm[0] / 1000,
                             fuerzas_e=fuerzas, alturas_piso_m=p.alturas_piso_m, combinaciones=_cb.COMBINACIONES_NSR10,
                             r_deriva=r_deriva, nx=nx, pesos=pesos, con_columnas=con_columnas)
    return lote, tpl, nid, nx, ny, pesos, fuerzas


def diseno_portico(p: ProyectoPortico, top: int = 5, *, grilla: Optional[tuple] = None,
                   verificar_escalar: bool = True) -> InformePortico:
    """Embudo: (1) análisis vectorizado de TODAS las secciones → demandas y deriva; (2) máscara de deriva (A.6.4);
    (3) diseño exacto por nivel de las sobrevivientes (o de una preselección); (4) costo APU; (5) el óptimo se reanaliza con la
    ruta escalar de referencia y se compara con la vectorizada."""
    t0 = time.perf_counter()
    if p.calidad_concreto not in FC_MPA_POR_CALIDAD:
        raise ValueError(f"calidad_concreto '{p.calidad_concreto}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")
    cap, info = _capacidad(p)
    ctx = _ctx_sismico(p, cap, info)
    mat = _viga.Materiales(fc=FC_MPA_POR_CALIDAD[p.calidad_concreto], fy=p.fy_mpa, fyt=p.fy_mpa)
    bases, alturas = grilla if grilla is not None else (BASES_MM, ALTURAS_MM)
    bb, hh = np.meshgrid(np.asarray(bases, dtype=float), np.asarray(alturas, dtype=float), indexing="ij")
    b_all, h_all = bb.ravel(), hh.ravel()
    N, n_lev = b_all.size, len(p.alturas_piso_m)
    if p.fuerzas_laterales_kn and len(p.fuerzas_laterales_kn) != n_lev:
        raise ValueError("fuerzas_laterales_kn debe tener un valor por nivel")

    # --- (1) análisis vectorizado ------------------------------------------------------
    lote, tpl, nid, nx, ny, pesos, fuerzas = _lote_vectorizado(p, ctx, b_all, h_all)
    t1 = time.perf_counter()

    # --- (2) máscara de deriva ---------------------------------------------------------
    ok = np.ones(N, dtype=bool)
    if ctx is not None:
        ok &= lote.deriva_max * p.factor_deriva_fisurada <= DERIVA_MAX
    n_deriva = int(ok.sum())
    idx = np.flatnonzero(ok)

    # --- (3) preselección opcional por proxy -------------------------------------------
    if p.preseleccion is not None and idx.size > p.preseleccion:
        k_rel = _precios_relativos(p)
        d = h_all[idx] - p.recubrimiento_mm - 10.0 - 16.0
        as_req = (lote.m_neg[idx] + lote.m_pos_vano[idx]) * 1e6 / (0.9 * p.fy_mpa * 0.9 * d)       # mm², aproximado
        proxy = b_all[idx] * h_all[idx] / 1e6 + k_rel * as_req / 1e6
        idx = idx[np.argsort(proxy)]                  # de menor a mayor proxy; se recorre hasta reunir K factibles

    candidatos: list[CandidatoPortico] = []
    n_exactas = 0
    for q in idx:
        if p.preseleccion is not None and len(candidatos) >= p.preseleccion:
            break
        n_exactas += 1
        b, h = float(b_all[q]), float(h_all[q])
        dem = _dv.DemandaViga(luz_libre_m=lote.ln_min, M_neg_apoyo=float(lote.m_neg[q]), M_pos_apoyo=float(lote.m_pos_apoyo[q]),
                              M_pos_vano=float(lote.m_pos_vano[q]), V_max=float(lote.v_max[q]), V_gravedad=float(lote.v_grav[q]),
                              w_grav=float(lote.w_grav[q]), V_centro=float(lote.v_centro[q]))
        disenos = _dv.disenar(b, h, dem, cap, mat, recubrimiento=p.recubrimiento_mm,
                              columna_c1=p.columna_mm[0], columna_c2=p.columna_mm[1])
        if not disenos:
            continue
        c_min, mejor = min(((_costo_nivel(p, x), x) for x in disenos), key=lambda t: t[0])
        candidatos.append(CandidatoPortico(b, h, mejor, c_min * n_lev, dem, float(lote.deriva_max[q])))
    candidatos.sort(key=lambda c: c.costo_directo)
    t2 = time.perf_counter()

    # --- (4) reanálisis escalar del óptimo y paridad ------------------------------------
    gobernante = basal = paridad = None
    if candidatos:
        o = candidatos[0]
        cbz = pesos_o = None
        fuerzas_o = p.fuerzas_laterales_kn
        if ctx is not None:
            cbz, pesos_o = _basal_escalar(p, ctx, o.b, o.h)
            fuerzas_o = cbz.fuerzas_diseno_kn
        modelo, vigas, res, w_pp = _analizar(p, o.b, o.h, fuerzas_o)
        dem_s, gob = _demanda(p, modelo, vigas, res, w_pp, o.h)
        e = gob["env"]
        gobernante = {"x": e.x.tolist(), "M_max": e.M_max.tolist(), "M_min": e.M_min.tolist(), "V_max": e.V_max.tolist(),
                      "V_min": e.V_min.tolist(), "combo_M_max": e.combo_M_max, "combo_M_min": e.combo_M_min, "combo_V": e.combo_V}
        paridad = max(abs(getattr(dem_s, k) - getattr(o.demanda, k)) / max(1.0, abs(getattr(dem_s, k)))
                      for k in ("M_neg_apoyo", "M_pos_apoyo", "M_pos_vano", "V_max", "V_centro", "V_gravedad", "w_grav"))
        if verificar_escalar and paridad > 1e-6:
            raise RuntimeError(f"La ruta vectorizada difiere de la escalar de referencia ({paridad:.2e}); no se entrega el resultado")
        if cbz is not None:
            basal = _derivar_basal(p, ctx, o, res, nid, nx, ny, cbz, pesos_o)
    diag = {"secciones_totales": N, "pasan_deriva": n_deriva, "diseno_exacto_sobre": n_exactas, "factibles": len(candidatos),
            "t_vectorizado_s": round(t1 - t0, 4), "t_diseno_costo_s": round(t2 - t1, 4),
            "paridad_escalar_max_dif_rel": paridad, "preseleccion": p.preseleccion}
    return InformePortico(cap, info, candidatos[0] if candidatos else None, tuple(candidatos[:top]), N, len(candidatos),
                          gobernante, SUPUESTOS, basal, diag)


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
