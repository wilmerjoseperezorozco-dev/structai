"""Diseño integral de pórtico plano: vigas + columnas + columna fuerte–viga débil, con costo total APU.

Extiende `diseno_portico` (que diseña solo las vigas con columna dada). Aquí la sección de columna es VARIABLE:

  para cada lado de columna cuadrada c:
    1. análisis vectorizado de TODAS las secciones de viga (rigidez lineal en A, I; casos D, L, E juntos) + fuerzas en
       los extremos de todas las columnas                                              (grilla_vectorizada)
    2. máscara de deriva (A.6.4) y de estabilidad (Q, C.10.10.5.2)
    3. diseño exacto de las vigas sobrevivientes → las K más baratas por sección
    4. ΣMnb real de cada diseño de viga (Mn⁻ + Mn⁺ en nudo interior, el mayor en nudo exterior)
    5. diseño de columna que cumple flexo-compresión (todas las combinaciones, magnificada), columna fuerte–viga débil
       (ΣMnc ≥ 1,2·ΣMnb con la Pu más desfavorable de cada nudo), cortante por capacidad y confinamiento
    6. costo total = vigas + columnas (APU) → mínimo global sobre la rejilla (c, b, h)
  el óptimo se reanaliza con la ruta escalar de referencia y se compara con la vectorizada (vigas Y columnas).

El óptimo es sobre la rejilla declarada, con una sección de columna y una de viga en todo el pórtico. Ver SUPUESTOS.
"""
from __future__ import annotations

import dataclasses
import importlib
import math
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

import numpy as np

from . import diseno_portico as _dp
from . import grilla_vectorizada as _gv
from .cargador import cargar_motor
from .diseno_inverso import FC_MPA_POR_CALIDAD

cargar_motor("motor-concreto", "motor_concreto")
_col = importlib.import_module("motor_concreto.columna")
_dv, _viga, _cant, _cb, _pt = _dp._dv, _dp._viga, _dp._cant, _dp._cb, _dp._pt

COLUMNAS_MM = tuple(range(300, 751, 50))
VIGAS_POR_SECCION = 3                    # diseños de viga más baratos que se prueban contra la columna
Q_MAX = 1.0 / 3.0                        # δs ≤ 1,5 (ACI 318-08 10.10.7.? : por encima se exige análisis de segundo orden)
PARIDAD_MAX = 1e-6

SUPUESTOS = _dp.SUPUESTOS[:1] + (
    "Una sola sección de columna cuadrada y una de viga en todo el pórtico; el óptimo es el mínimo sobre la rejilla declarada, no un óptimo continuo.",
    "Flexión uniaxial en el plano del pórtico, sin torsión ni biaxial. Esfuerzos en el eje del nudo (no se reducen a la cara: conservador).",
    "Columna fuerte–viga débil (C.21.6.2.2, DES): ΣMnb = Mn⁻ + Mn⁺ en nudo interior y el mayor de ambos en nudo exterior, sin aporte de losa (conservador); ΣMnc con la Pu más desfavorable de las combinaciones con E.",
    "Esbeltez: k de Jackson–Moreland (base empotrada ψ=1), magnificación δns (Cm=1) y δs = 1/(1−Q) con Q por entrepiso; rechaza Q > 1/3 y kℓu/r > 100. Fórmulas del ACI 318-08 (C.10.10.5–7 no recuperadas del corpus).",
    "Pn,max 0,75 verificado (C.10.3.6.2, C.10-2). Ash en DES (C.21-7/-8) y Mpr=1,25fy verificados (C.21.6.4.4, notación C.2). so y ℓo en DMO verificados (C.21.3.5.6).",
    "Costo = vigas + columnas, costo directo APU (Barranquilla 2026). No se diseñan nudos (C.21.7), cimentación, losas ni empalmes.",
) + _dp.SUPUESTOS[-1:]


@dataclass(frozen=True)
class CandidatoIntegral:
    c: float
    b: float
    h: float
    viga: object
    columna: object
    costo_vigas: float
    costo_columnas: float
    costo_directo: float
    deriva: float
    q_max: float
    razon_scwb: float                    # menor ΣMnc/(1,2·ΣMnb); NaN si no aplica (DMI/DMO)
    demanda_viga: object = None


@dataclass(frozen=True)
class InformeIntegral:
    capacidad: str
    sismo: Optional[dict]
    optimo: Optional[CandidatoIntegral]
    ranking: tuple[CandidatoIntegral, ...]
    evaluadas: int
    factibles: int
    basal: Optional[dict]
    diagnostico: dict
    supuestos: tuple[str, ...] = field(default_factory=lambda: SUPUESTOS)


@lru_cache(maxsize=4096)
def _costo_col_cache(c: float, n_barras: int, dia: str, est: str, n_est: int, hp_mm: float, calidad: str, rec: float) -> float:
    geo = _cant.GeometriaElementoConcreto(
        tipo=_cant.TipoElementoConcreto.COLUMNA, base_m=c / 1000, altura_m=c / 1000, longitud_m=hp_mm / 1000,
        recubrimiento_m=rec / 1000, refuerzo_longitudinal=_cant.RefuerzoLongitudinal(n_barras, dia),
        estribos=_cant.Estribos(est, hp_mm / 1000 / max(n_est - 1, 1)))
    return _cant.calcular_apu_dinamico(geo, calidad_concreto=calidad, run_montecarlo=False).costo_directo


def costo_columnas(p: _dp.ProyectoPortico, d, nx: int) -> float:
    """Costo directo de todas las columnas: nx por entrepiso, con la altura de cada entrepiso."""
    return sum(nx * _costo_col_cache(d.h, d.n_barras, d.dia, d.estribo, d.n_estribos, hp * 1000, p.calidad_concreto,
                                     p.recubrimiento_mm) for hp in p.alturas_piso_m)


def _mn_viga(d, m) -> tuple[float, float]:
    """(Mn⁻ con el acero superior, Mn⁺ con el inferior) nominales, kN·m."""
    dd = _dv._d(d.h, d.dia, d.estribo_dia, 40.0)
    a = _viga.AREA_MM2[d.dia]
    return (_dv._mn_nominal(d.n_sup * a, d.b, dd, m.fc, m.fy)[0], _dv._mn_nominal(d.n_inf * a, d.b, dd, m.fc, m.fy)[0])


def _ks(p, c: float, b_v: float, h_v: float, nx: int, fc: float):
    ec = 4700.0 * math.sqrt(fc) * 1e6                              # N/m²: solo importan cocientes
    ic = _dp.FACTOR_I_COLUMNA * (c / 1000) ** 4 / 12
    ib = _dp.FACTOR_I_VIGA * (b_v / 1000) * (h_v / 1000) ** 3 / 12
    ny = len(p.alturas_piso_m)
    luces = p.luces_m
    lu_min, lu_max, k_lu = math.inf, 0.0, 0.0
    for j in range(ny):                                           # entrepiso j (de abajo hacia arriba)
        hp = p.alturas_piso_m[j]
        lu = hp - h_v / 1000
        lu_min, lu_max = min(lu_min, lu), max(lu_max, lu)
        for i in range(nx):
            vigas_i = [luces[i - 1]] if i > 0 else []
            vigas_i += [luces[i]] if i < nx - 1 else []
            sb_top = sum(ec * ib / L for L in vigas_i)
            sc_top = ec * ic / hp + (ec * ic / p.alturas_piso_m[j + 1] if j + 1 < ny else 0.0)
            psi_top = sc_top / sb_top if sb_top > 0 else 1e9
            psi_bot = 1.0 if j == 0 else (ec * ic / p.alturas_piso_m[j - 1] + ec * ic / hp) / sb_top
            psi_m = 0.5 * (psi_top + psi_bot)
            k = (20 - psi_m) / 20 * math.sqrt(1 + psi_m) if psi_m < 2 else 0.9 * math.sqrt(1 + psi_m)
            k_lu = max(k_lu, max(k, 1.0) * lu)
    return k_lu, lu_min, lu_max


def demanda_columnas(p: _dp.ProyectoPortico, tpl, lote, q: int, c: float, b_v: float, h_v: float, mat, cap_sismo: bool):
    """Arma DemandaColumna de la sección q desde las fuerzas vectorizadas; devuelve (dem, q_max)."""
    f = lote.col_f[q]                                              # (ncol, 6, casos)
    nx, ny = tpl.nx, len(p.alturas_piso_m) + 1
    nombres, C = _gv._combos(_cb.COMBINACIONES_NSR10, cap_sismo)
    ncasos = f.shape[2]
    Cc = C[:, :ncasos]
    comb = np.einsum("kc,nac->kna", Cc, f)                         # (K, ncol, 6)
    P = comb[:, :, 0]
    Mns = np.einsum("kc,nac->kna", Cc[:, :2], f[:, :, :2])[:, :, [2, 5]]
    delta_s, q_max = 1.0, 0.0
    if cap_sismo:
        fe = lote.fuerzas_e[q]
        ux = np.concatenate([[0.0], lote.ux_e[q]])
        gravedad = 1.2 * f[:, 0, 0] + 1.0 * f[:, 0, 1]             # P bajo 1,2D+1,0L por columna
        for j in range(ny - 1):
            en_piso = [ic for ic, (st, *_r) in enumerate(tpl.columnas) if st == j]
            sum_p = float(gravedad[en_piso].sum())
            vus = float(fe[j:].sum())
            dlt = abs(ux[j + 1] - ux[j])
            q_j = sum_p * dlt / (vus * p.alturas_piso_m[j]) if vus > 0 else 0.0
            q_max = max(q_max, q_j)
        if q_max > Q_MAX:
            return None, q_max
        if q_max > _col.Q_SIN_AMPLIFICAR:
            delta_s = 1.0 / (1.0 - q_max)
        Ms = np.einsum("k,na->kna", Cc[:, 2], f[:, [2, 5], 2])
        Vs = np.einsum("k,n->kn", Cc[:, 2], f[:, 1, 2])
    else:
        Ms = np.zeros_like(Mns)
        Vs = np.zeros_like(P)
    V_ns = np.einsum("kc,nc->kn", Cc[:, :2], f[:, 1, :2])
    V = np.abs(V_ns + delta_s * Vs).max()
    V_sismo = float(np.abs(delta_s * Vs).max())
    es_e = np.abs(Cc[:, 2]) > 0 if ncasos == 3 else np.zeros(len(Cc), dtype=bool)
    nudos = []
    if es_e.any():
        for j in range(1, ny):
            for i in range(nx):
                p_inf = P[es_e, (j - 1) * nx + i]
                p_sup = P[es_e, j * nx + i] if j < ny - 1 else None
                nudos.append((0 < i < nx - 1, p_inf, p_sup))
    gD = float(np.abs(f[:, 0, 0]).sum())
    gL = float(np.abs(f[:, 0, 1]).sum())
    beta = 1.2 * gD / (1.2 * gD + 1.6 * gL) if (gD + gL) > 0 else 0.0
    k_lu, lu_min, lu_max = _ks(p, c, b_v, h_v, nx, mat.fc)
    dem = _col.DemandaColumna(P=P.ravel(), M_ns=Mns.reshape(-1, 2), M_s=Ms.reshape(-1, 2), V=float(V), V_sismo=V_sismo,
                              delta_s=delta_s, k_lu_max_m=k_lu, lu_min_m=lu_min, lu_max_m=lu_max, beta_dns=beta,
                              nudos=tuple(nudos), P_sismo=P[es_e].ravel() if es_e.any() else None)
    return dem, q_max


def _tabla_secciones(grilla):
    bases, alturas = grilla if grilla is not None else (_dp.BASES_MM, _dp.ALTURAS_MM)
    bb, hh = np.meshgrid(np.asarray(bases, dtype=float), np.asarray(alturas, dtype=float), indexing="ij")
    return bb.ravel(), hh.ravel()


def diseno_integral(p: _dp.ProyectoPortico, top: int = 5, *, columnas_mm=COLUMNAS_MM, grilla: Optional[tuple] = None,
                    vigas_por_seccion: int = VIGAS_POR_SECCION, verificar_escalar: bool = True) -> InformeIntegral:
    """Mínimo costo total (vigas + columnas) sobre la rejilla (lado de columna) × (b, h de viga). Exige perfil_suelo o fuerzas dadas."""
    t0 = time.perf_counter()
    if p.calidad_concreto not in FC_MPA_POR_CALIDAD:
        raise ValueError(f"calidad_concreto '{p.calidad_concreto}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")
    cap, info = _dp._capacidad(p)
    ctx = _dp._ctx_sismico(p, cap, info)
    con_sismo = ctx is not None or bool(p.fuerzas_laterales_kn)
    fc = FC_MPA_POR_CALIDAD[p.calidad_concreto]
    mat = _viga.Materiales(fc=fc, fy=p.fy_mpa, fyt=p.fy_mpa)
    b_all, h_all = _tabla_secciones(grilla)
    n_lev = len(p.alturas_piso_m)
    cands: list[CandidatoIntegral] = []
    evaluadas = pasan_deriva = vigas_ok = 0
    t_vec = 0.0
    for c in columnas_mm:
        pc = dataclasses.replace(p, columna_mm=(float(c), float(c)))
        t1 = time.perf_counter()
        lote, tpl, nid, nx, ny, pesos, fuerzas = _dp._lote_vectorizado(pc, ctx, b_all, h_all, con_columnas=True)
        t_vec += time.perf_counter() - t1
        evaluadas += b_all.size
        ok = np.ones(b_all.size, dtype=bool)
        if ctx is not None:
            ok &= lote.deriva_max * p.factor_deriva_fisurada <= _dp.DERIVA_MAX
        pasan_deriva += int(ok.sum())
        for q in np.flatnonzero(ok):
            b, h = float(b_all[q]), float(h_all[q])
            dem_v = _dv.DemandaViga(luz_libre_m=lote.ln_min, M_neg_apoyo=float(lote.m_neg[q]), M_pos_apoyo=float(lote.m_pos_apoyo[q]),
                                    M_pos_vano=float(lote.m_pos_vano[q]), V_max=float(lote.v_max[q]), V_gravedad=float(lote.v_grav[q]),
                                    w_grav=float(lote.w_grav[q]), V_centro=float(lote.v_centro[q]))
            disenos = _dv.disenar(b, h, dem_v, cap, mat, recubrimiento=p.recubrimiento_mm, columna_c1=c, columna_c2=c)
            if not disenos:
                continue
            vigas_ok += 1
            baratos = sorted(((_dp._costo_nivel(pc, x), x) for x in disenos), key=lambda t: t[0])[:vigas_por_seccion]
            dem_c, q_max = demanda_columnas(pc, tpl, lote, int(q), float(c), b, h, mat, con_sismo)
            if dem_c is None:
                continue
            mejor = None
            for c_viga, dv in baratos:
                mneg, mpos = _mn_viga(dv, mat)
                cols = _col.disenar_columna(float(c), float(c), dem_c, cap, mat, recubrimiento=p.recubrimiento_mm,
                                            mnb_int=mneg + mpos, mnb_ext=max(mneg, mpos))
                if not cols:
                    continue
                c_col, dc = min(((costo_columnas(pc, x, nx), x) for x in cols), key=lambda t: t[0])
                total = c_viga * n_lev + c_col
                if mejor is None or total < mejor.costo_directo:
                    razon = next((v.capacidad for v in dc.verificaciones if v.norma == "C.21.6.2.2"), math.nan)
                    mejor = CandidatoIntegral(float(c), b, h, dv, dc, c_viga * n_lev, c_col, total, float(lote.deriva_max[q]),
                                              q_max, razon, dem_v)
            if mejor is not None:
                cands.append(mejor)
    cands.sort(key=lambda x: x.costo_directo)
    t2 = time.perf_counter()
    basal = paridad = None
    if cands:
        o = cands[0]
        po = dataclasses.replace(p, columna_mm=(o.c, o.c))
        paridad, basal = _verificar_optimo(po, ctx, o, verificar_escalar)
    diag = {"secciones_por_columna": int(b_all.size), "lados_de_columna": len(tuple(columnas_mm)), "combinaciones_evaluadas": evaluadas,
            "pasan_deriva": pasan_deriva, "con_viga_factible": vigas_ok, "factibles_vigas_y_columnas": len(cands),
            "t_vectorizado_s": round(t_vec, 3), "t_total_s": round(t2 - t0, 3), "paridad_escalar_max_dif_rel": paridad}
    return InformeIntegral(cap, info, cands[0] if cands else None, tuple(cands[:top]), evaluadas, len(cands), basal, diag)


def _verificar_optimo(po, ctx, o: CandidatoIntegral, verificar: bool):
    """Reanálisis con la ruta escalar (Portico.resolver): compara demandas de viga y fuerzas de columna con las vectorizadas."""
    cbz = pesos_o = None
    fuerzas_o = po.fuerzas_laterales_kn
    if ctx is not None:
        cbz, pesos_o = _dp._basal_escalar(po, ctx, o.b, o.h)
        fuerzas_o = cbz.fuerzas_diseno_kn
    modelo, vigas, res, w_pp = _dp._analizar(po, o.b, o.h, fuerzas_o)
    dem_s, _gob = _dp._demanda(po, modelo, vigas, res, w_pp, o.h)
    paridad = max(abs(getattr(dem_s, k) - getattr(o.demanda_viga, k)) / max(1.0, abs(getattr(dem_s, k)))
                  for k in ("M_neg_apoyo", "M_pos_apoyo", "M_pos_vano", "V_max", "V_centro", "V_gravedad", "w_grav"))
    lote1, tpl1, *_r = _dp._lote_vectorizado(po, ctx, np.array([o.b]), np.array([o.h]), con_columnas=True)
    casos = [k for k in ("D", "L", "E") if k in res]
    nx = tpl1.nx
    for ic, (st, i, _g, _kt) in enumerate(tpl1.columnas):
        for ci, caso in enumerate(casos):
            ref = res[caso].f_extremos[st * nx + i]
            dif = float(np.max(np.abs(ref - lote1.col_f[0, ic, :, ci]))) / max(1.0, float(np.max(np.abs(ref))))
            paridad = max(paridad, dif)
    if verificar and paridad > PARIDAD_MAX:
        raise RuntimeError(f"La ruta vectorizada difiere de la escalar de referencia ({paridad:.2e}); no se entrega el resultado")
    basal = None
    if cbz is not None:
        ny = len(po.alturas_piso_m) + 1
        basal = _dp._derivar_basal(po, ctx, o, res, (lambda i, j: j * nx + i), nx, ny, cbz, pesos_o)
    return paridad, basal
