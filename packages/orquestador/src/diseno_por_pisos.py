"""Secciones distintas por piso: asignación óptima vigas+columnas por MILP con verificación exacta.

Problema: elegir para cada piso j una sección (columna cuadrada c, viga b×h) de una biblioteca, minimizando el costo APU total,
sujeto a deriva (A.6.4), estabilidad (Q), diseño completo de vigas y columnas por piso, columna fuerte–viga débil entre pisos
y reglas constructivas (la columna no crece hacia arriba; máximo de secciones distintas de columna y de viga).

Por qué no es un MILP "puro": la rigidez de un piso depende de los vecinos, así que la deriva no es separable. Se resuelve así:
  1. Biblioteca: cada sección candidata se analiza y diseña como pórtico UNIFORME (ruta escalar de referencia, `Portico.resolver`),
     lo que da, por piso, su costo, su deriva y su razón deriva/cortante de piso (rigidez efectiva).
  2. MILP (scipy/HiGHS): x[j,s] binaria; un candidato por piso; deriva por piso con la razón de la biblioteca y el cortante del
     paso anterior; columna no creciente; tope de secciones distintas; cortes que excluyen asignaciones ya evaluadas.
  3. Verificación EXACTA de la asignación (análisis matricial del pórtico real con secciones por piso, diseño por piso de arriba
     hacia abajo con la columna fuerte–viga débil contra la columna superior real). Si falla o mejora, se actualiza la razón
     deriva/cortante con lo medido, se añade un corte y se vuelve a resolver.
  El resultado es la mejor asignación VERIFICADA entre las exploradas; no se afirma optimalidad global (la rigidez del MILP es
  un sustituto del tipo edificio de cortante). El ahorro se mide contra el mejor pórtico uniforme de la MISMA biblioteca.

Supuestos adicionales: ancho de nudo para la cara de la viga = menor de las dos columnas adyacentes (conservador en momento);
ΣMnb de los vigas del piso j contra la columna j y la columna j+1; el nudo de la base (cimentación) no se verifica.
"""
from __future__ import annotations

import dataclasses
import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.optimize import LinearConstraint, Bounds, milp
from scipy.sparse import coo_matrix

from . import diseno_integral as _di
from . import diseno_portico as _dp
from . import grilla_vectorizada as _gv
from . import sismo_portico as _sp
from .diseno_inverso import FC_MPA_POR_CALIDAD

_col, _dv, _viga, _cant, _cb, _pt = _di._col, _di._dv, _di._viga, _di._cant, _di._cb, _di._pt

COLUMNAS_MM = (400, 500, 600, 700)
BASES_MM = (250.0, 300.0, 350.0)
ALTURAS_MM = (500.0, 600.0, 700.0, 800.0)
Q_MAX = _di.Q_MAX
MAX_ITER = 400
LIMITE_TIEMPO_S = 60.0          # tope de la búsqueda MILP+verificación; si se agota se devuelve el mejor verificado y se avisa
PISO_TOLERANCIA = 0.03          # tolerancia mínima de la cota aun con costos calibrados
TOLERANCIA_COTA = 0.05          # el costo del MILP viene de pórticos uniformes: puede sobreestimar el real hasta ~esta fracción

SUPUESTOS = (
    "Cada piso tiene su propia sección de columna cuadrada y de viga; dentro del piso todas iguales.",
    "El MILP usa la razón deriva/cortante de piso medida en pórticos uniformes (sustituto de cortante) y la corrige con lo medido en cada verificación; el resultado es la mejor asignación verificada, no un óptimo global demostrado.",
    "Verificación exacta con análisis matricial del pórtico real; diseño por piso de arriba hacia abajo, la columna fuerte–viga débil se verifica contra la columna superior ya diseñada. El nudo de la base no se verifica.",
    "Cara de la viga: ancho de nudo = menor de las dos columnas adyacentes (conservador en momento).",
) + _di.SUPUESTOS[2:]


@dataclass(frozen=True)
class Seccion:
    c: float
    b: float
    h: float


@dataclass(frozen=True)
class ResultadoPiso:
    piso: int
    seccion: Seccion
    viga: object
    columna: object
    costo_viga: float
    costo_columna: float
    deriva: float
    cortante_diseno_kn: float
    q: float
    razon_scwb: float
    motivo: str = ""

    @property
    def costo(self) -> float:
        return self.costo_viga + self.costo_columna

    @property
    def factible(self) -> bool:
        return not self.motivo


@dataclass(frozen=True)
class Evaluacion:
    pisos: tuple[ResultadoPiso, ...]
    deriva_ok: bool
    basal: Optional[dict] = None

    @property
    def factible(self) -> bool:
        return self.deriva_ok and all(x.factible for x in self.pisos)

    @property
    def costo(self) -> float:
        return sum(x.costo for x in self.pisos)

    @property
    def asignacion(self) -> tuple[Seccion, ...]:
        return tuple(x.seccion for x in self.pisos)


@dataclass(frozen=True)
class InformePisos:
    capacidad: str
    sismo: Optional[dict]
    optimo: Optional[Evaluacion]
    uniforme: Optional[Evaluacion]
    ahorro_pct: Optional[float]
    biblioteca: int
    iteraciones: tuple[dict, ...]
    diagnostico: dict
    supuestos: tuple[str, ...] = field(default_factory=lambda: SUPUESTOS)


# --------------------------------------------------------------------- modelo por pisos
def _pesos(p: _dp.ProyectoPortico, asign: tuple[Seccion, ...], nx: int) -> tuple[float, ...]:
    n = len(asign)
    vigas = [(p.carga_muerta_kn_m + _dp.PESO_UNIT_KN_M3 * s.b / 1000 * s.h / 1000) * sum(p.luces_m) for s in asign]
    col = [_dp.PESO_UNIT_KN_M3 * (s.c / 1000) ** 2 * p.alturas_piso_m[j] * nx for j, s in enumerate(asign)]
    return tuple(vigas[i] + 0.5 * col[i] + (0.5 * col[i + 1] if i + 1 < n else 0.0) for i in range(n))


def _modelo_pisos(p: _dp.ProyectoPortico, asign: tuple[Seccion, ...]):
    Ec = 4700.0 * math.sqrt(FC_MPA_POR_CALIDAD[p.calidad_concreto]) * 1000.0
    nx, ny = len(p.luces_m) + 1, len(p.alturas_piso_m) + 1
    xs = [0.0]
    for L in p.luces_m:
        xs.append(xs[-1] + L)
    ys = [0.0]
    for H in p.alturas_piso_m:
        ys.append(ys[-1] + H)
    nodos = [_pt.Nodo(xs[i], ys[j]) for j in range(ny) for i in range(nx)]
    nid = lambda i, j: j * nx + i
    elementos, vigas_p = [], []
    for j in range(ny - 1):
        c = asign[j].c / 1000
        for i in range(nx):
            elementos.append(_pt.Elemento(nid(i, j), nid(i, j + 1), Ec, c * c, _dp.FACTOR_I_COLUMNA * c**4 / 12))
    for j in range(1, ny):
        s = asign[j - 1]
        lista = []
        for i in range(nx - 1):
            lista.append(len(elementos))
            elementos.append(_pt.Elemento(nid(i, j), nid(i + 1, j), Ec, s.b * s.h / 1e6,
                                          _dp.FACTOR_I_VIGA * (s.b / 1000) * (s.h / 1000) ** 3 / 12))
        vigas_p.append(lista)
    apoyos = {nid(i, 0): (True, True, True) for i in range(nx)}
    w_pp = [_dp.PESO_UNIT_KN_M3 * s.b / 1000 * s.h / 1000 for s in asign]
    return _pt.Portico(nodos, elementos, apoyos), vigas_p, w_pp, nid, nx, ny


def _k_piso(p, asign, j: int, nx: int, fc: float) -> float:
    """k·ℓu del entrepiso j (m): k de Jackson–Moreland, pórtico desplazable, base empotrada ψ=1, rigideces agrietadas."""
    ec = 4700.0 * math.sqrt(fc) * 1e6
    n = len(asign)
    sc = lambda m: ec * _dp.FACTOR_I_COLUMNA * (asign[m].c / 1000) ** 4 / 12 / p.alturas_piso_m[m]
    sb = lambda m, L: ec * _dp.FACTOR_I_VIGA * (asign[m].b / 1000) * (asign[m].h / 1000) ** 3 / 12 / L
    lu = p.alturas_piso_m[j] - asign[j].h / 1000
    mejor = 0.0
    for i in range(nx):
        adj = ([p.luces_m[i - 1]] if i > 0 else []) + ([p.luces_m[i]] if i < nx - 1 else [])
        sb_top = sum(sb(j, L) for L in adj)
        psi_top = (sc(j) + (sc(j + 1) if j + 1 < n else 0.0)) / sb_top
        psi_bot = 1.0 if j == 0 else (sc(j - 1) + sc(j)) / sum(sb(j - 1, L) for L in adj)
        pm = 0.5 * (psi_top + psi_bot)
        k = (20 - pm) / 20 * math.sqrt(1 + pm) if pm < 2 else 0.9 * math.sqrt(1 + pm)
        mejor = max(mejor, max(k, 1.0) * lu)
    return mejor


def _demanda_columna_piso(p, asign, f, fe, ux, nx, j: int, mat, con_sismo: bool):
    """DemandaColumna del entrepiso j (columnas del piso j y nudos de su cabeza). f: (columnas, 6, casos). → (dem, q) o (None, q)."""
    n = len(asign)
    _nom, C = _gv._combos(_cb.COMBINACIONES_NSR10, con_sismo)
    nc = f.shape[2]
    Cc = C[:, :nc]
    ic = [j * nx + i for i in range(nx)]
    fj = f[ic]
    comb = np.einsum("kc,nac->kna", Cc, fj)
    P = comb[:, :, 0]
    Mns = np.einsum("kc,nac->kna", Cc[:, :2], fj[:, :, :2])[:, :, [2, 5]]
    delta_s, q = 1.0, 0.0
    if con_sismo:
        gravedad = float((1.2 * fj[:, 0, 0] + 1.0 * fj[:, 0, 1]).sum())
        vus = float(sum(fe[j:]))
        ux0 = [0.0] + list(ux)
        dlt = abs(ux0[j + 1] - ux0[j])
        q = gravedad * dlt / (vus * p.alturas_piso_m[j]) if vus > 0 else 0.0
        if q > Q_MAX:
            return None, q
        if q > _col.Q_SIN_AMPLIFICAR:
            delta_s = 1.0 / (1.0 - q)
        Ms = np.einsum("k,na->kna", Cc[:, 2], fj[:, [2, 5], 2])
        Vs = np.einsum("k,n->kn", Cc[:, 2], fj[:, 1, 2])
    else:
        Ms, Vs = np.zeros_like(Mns), np.zeros_like(P)
    V_ns = np.einsum("kc,nc->kn", Cc[:, :2], fj[:, 1, :2])
    es_e = (np.abs(Cc[:, 2]) > 0) if nc == 3 else np.zeros(len(Cc), dtype=bool)
    nudos = []
    if es_e.any():
        P_up = np.einsum("kc,nc->kn", Cc, f[[(j + 1) * nx + i for i in range(nx)], 0, :]) if j + 1 < n else None
        for i in range(nx):
            nudos.append((0 < i < nx - 1, P[es_e, i], P_up[es_e, i] if P_up is not None else None))
    gD, gL = float(np.abs(fj[:, 0, 0]).sum()), float(np.abs(fj[:, 0, 1]).sum())
    beta = 1.2 * gD / (1.2 * gD + 1.6 * gL) if (gD + gL) > 0 else 0.0
    lu = p.alturas_piso_m[j] - asign[j].h / 1000
    dem = _col.DemandaColumna(
        P=P.ravel(), M_ns=Mns.reshape(-1, 2), M_s=Ms.reshape(-1, 2), V=float(np.abs(V_ns + delta_s * Vs).max()),
        V_sismo=float(np.abs(delta_s * Vs).max()), delta_s=delta_s, k_lu_max_m=_k_piso(p, asign, j, nx, mat.fc),
        lu_min_m=lu, lu_max_m=lu, beta_dns=beta, nudos=tuple(nudos), P_sismo=P[es_e].ravel() if es_e.any() else None)
    return dem, q


def _costo_col_piso(p, d, c: float, nx: int, j: int) -> float:
    return nx * _di._costo_col_cache(d.h, d.n_barras, d.dia, d.estribo, d.n_estribos, p.alturas_piso_m[j] * 1000,
                                     p.calidad_concreto, p.recubrimiento_mm)


def _analizar_asignacion(p: _dp.ProyectoPortico, asign: tuple[Seccion, ...], ctx):
    """Análisis matricial exacto de una asignación: fuerzas sísmicas, D/L/E, fuerzas de columna y derivas por piso."""
    n = len(p.alturas_piso_m)
    if len(asign) != n:
        raise ValueError("Una sección por piso")
    nx = len(p.luces_m) + 1
    fe, cbz, pesos = None, None, None
    if ctx is not None:
        pesos = _pesos(p, asign, nx)
        cbz = _sp.fuerzas_escalar(ctx, pesos, _sp.alturas_nivel_m(p.alturas_piso_m))
        fe = tuple(cbz.fuerzas_diseno_kn)
    elif p.fuerzas_laterales_kn:
        fe = tuple(p.fuerzas_laterales_kn)
    modelo, vigas_p, w_pp, nid, nx, ny = _modelo_pisos(p, asign)
    casos = {"D": _pt.Caso("D", uniformes={k: p.carga_muerta_kn_m + w_pp[j] for j in range(n) for k in vigas_p[j]}),
             "L": _pt.Caso("L", uniformes={k: p.carga_viva_kn_m for j in range(n) for k in vigas_p[j]})}
    if fe is not None:
        casos["E"] = _pt.Caso("E", nodales={nid(i, j): (fe[j - 1] / nx, 0.0, 0.0) for j in range(1, ny) for i in range(nx)})
    res = {k: modelo.resolver(c) for k, c in casos.items()}
    f = np.zeros((nx * (ny - 1), 6, len(casos)))
    for ic in range(nx * (ny - 1)):
        for ci, k in enumerate(casos):
            f[ic, :, ci] = res[k].f_extremos[ic]
    ux = _dp._ux_niveles(res, nid, nx, ny) if fe is not None else []
    factor = cbz.r * cbz.sa_deriva / cbz.sa if cbz is not None else 1.0
    ux0 = [0.0] + list(ux)
    derivas = [abs(ux0[j + 1] - ux0[j]) * factor / p.alturas_piso_m[j] for j in range(n)] if fe is not None else [math.nan] * n
    return dict(modelo=modelo, vigas_p=vigas_p, w_pp=w_pp, res=res, fe=fe, cbz=cbz, nx=nx, ny=ny, f=f, ux=ux, derivas=derivas)


def evaluar_asignacion(p: _dp.ProyectoPortico, asign: tuple[Seccion, ...], cap: str, ctx, mat,
                       vigas_por_seccion: int = _di.VIGAS_POR_SECCION, descartar_por_deriva: bool = False) -> Evaluacion:
    """Análisis matricial exacto + diseño por piso (arriba→abajo) de una asignación de secciones por piso.

    descartar_por_deriva: si la deriva ya incumple, no se diseña (el análisis cuesta ms; el diseño, decenas de ms)."""
    n = len(p.alturas_piso_m)
    con_sismo = ctx is not None or bool(p.fuerzas_laterales_kn)
    a = _analizar_asignacion(p, asign, ctx)
    modelo, vigas_p, w_pp, res, fe, cbz = a["modelo"], a["vigas_p"], a["w_pp"], a["res"], a["fe"], a["cbz"]
    nx, f, ux, derivas = a["nx"], a["f"], a["ux"], a["derivas"]
    deriva_ok = True
    if ctx is not None:
        deriva_ok = max(derivas) * p.factor_deriva_fisurada <= _dp.DERIVA_MAX
    if descartar_por_deriva and not deriva_ok:
        vac = [ResultadoPiso(piso=j, seccion=asign[j], viga=None, columna=None, costo_viga=math.nan, costo_columna=math.nan,
                             deriva=derivas[j], cortante_diseno_kn=float(sum(fe[j:])), q=0.0, razon_scwb=math.nan,
                             motivo="deriva") for j in range(n)]
        return Evaluacion(tuple(vac), False, None)
    resultados: dict[int, ResultadoPiso] = {}
    cv_sup, c_sup = None, None
    for j in range(n - 1, -1, -1):
        s = asign[j]
        v_dis = float(sum(fe[j:])) if fe is not None else math.nan
        base = dict(piso=j, seccion=s, viga=None, columna=None, costo_viga=math.nan, costo_columna=math.nan,
                    deriva=derivas[j], cortante_diseno_kn=v_dis, q=0.0, razon_scwb=math.nan)
        c_eff = min(s.c, asign[j + 1].c) if j + 1 < n else s.c
        pj = dataclasses.replace(p, columna_mm=(c_eff, c_eff))
        dem_v, _gob = _dp._demanda(pj, modelo, vigas_p[j], res, w_pp[j], s.h)
        disenos = _dv.disenar(s.b, s.h, dem_v, cap, mat, recubrimiento=p.recubrimiento_mm, columna_c1=c_eff, columna_c2=c_eff)
        if not disenos:
            resultados[j] = ResultadoPiso(**base, motivo="sin diseño de viga")
            cv_sup = None
            continue
        baratos = sorted(((_dp._costo_nivel(pj, x), x) for x in disenos), key=lambda t: t[0])[:vigas_por_seccion]
        dem_c, q = _demanda_columna_piso(p, asign, f, fe, ux, nx, j, mat, con_sismo)
        base["q"] = q
        if dem_c is None:
            resultados[j] = ResultadoPiso(**base, motivo="Q > 1/3 (requiere segundo orden)")
            cv_sup = None
            continue
        mejor = None
        for c_viga, dv in baratos:
            mneg, mpos = _di._mn_viga(dv, mat)
            cols = _col.disenar_columna(s.c, s.c, dem_c, cap, mat, recubrimiento=p.recubrimiento_mm,
                                        mnb_int=mneg + mpos, mnb_ext=max(mneg, mpos), cv_sup=cv_sup)
            if not cols:
                continue
            c_col, dc = min(((_costo_col_piso(p, x, s.c, nx, j), x) for x in cols), key=lambda t: t[0])
            if mejor is None or c_viga + c_col < mejor[0]:
                mejor = (c_viga + c_col, c_viga, c_col, dv, dc)
        if mejor is None:
            resultados[j] = ResultadoPiso(**base, motivo="sin diseño de columna (o columna fuerte–viga débil)")
            cv_sup = None
            continue
        _t, c_viga, c_col, dv, dc = mejor
        razon = next((v.capacidad for v in dc.verificaciones if v.norma == "C.21.6.2.2"), math.nan)
        base.update(viga=dv, columna=dc, costo_viga=c_viga, costo_columna=c_col, razon_scwb=razon)
        resultados[j] = ResultadoPiso(**base)
        cv_sup = _col.curva(s.c, s.c, dc.n_cara, dc.dia, dc.estribo, p.recubrimiento_mm, mat.fc, mat.fy)
    basal = None
    if cbz is not None:
        _fz = tuple(float(x) for x in cbz.fuerzas_elasticas_kn)
        basal = {"Vs_elastico_kn": cbz.vs_kn, "Vs_diseno_kn": cbz.vs_kn / cbz.r, "R": cbz.r, "T_s": cbz.T,
                 "peso_sismico_kn": cbz.peso_total_kn, "deriva_max_pct_hp": 100 * max(derivas)}
    return Evaluacion(tuple(resultados[j] for j in range(n)), deriva_ok, basal)


# --------------------------------------------------------------------- MILP
def _resolver_milp(costos, permitido, secciones, n, tope_col, tope_viga, no_crecer, cortes):
    """costos[j][s] (nan = no disponible), permitido[j][s] bool. → lista de índices por piso o None."""
    var = {}
    for j in range(n):
        for s in range(len(secciones)):
            if permitido[j][s] and not math.isnan(costos[j][s]):
                var[(j, s)] = len(var)
    nv = len(var)
    if nv == 0:
        return None, None
    col_keys = sorted({secciones[s].c for (_j, s) in var})
    viga_keys = sorted({(secciones[s].b, secciones[s].h) for (_j, s) in var})
    ny_c = len(col_keys) if tope_col else 0
    ny_v = len(viga_keys) if tope_viga else 0
    N = nv + ny_c + ny_v
    obj = np.zeros(N)
    for (j, s), k in var.items():
        obj[k] = costos[j][s]
    filas, lb, ub = [], [], []

    def nueva(coefs, lo, hi):
        filas.append(coefs)
        lb.append(lo)
        ub.append(hi)

    for j in range(n):
        nueva({k: 1.0 for (jj, s), k in var.items() if jj == j}, 1.0, 1.0)
    if no_crecer:
        # c_j ≥ c_{j+1}  ⇔  para todo umbral v:  Σ_{c_t ≥ v} x[j+1,t]  ≤  Σ_{c_s ≥ v} x[j,s]
        for j in range(n - 1):
            for v in col_keys:
                coefs = {}
                for (jj, s), k in var.items():
                    if secciones[s].c >= v:
                        if jj == j + 1:
                            coefs[k] = coefs.get(k, 0.0) + 1.0
                        elif jj == j:
                            coefs[k] = coefs.get(k, 0.0) - 1.0
                if coefs:
                    nueva(coefs, -np.inf, 0.0)
    if tope_col:
        for (j, s), k in var.items():
            nueva({k: 1.0, nv + col_keys.index(secciones[s].c): -1.0}, -np.inf, 0.0)
        nueva({nv + i: 1.0 for i in range(ny_c)}, 0.0, float(tope_col))
    if tope_viga:
        for (j, s), k in var.items():
            nueva({k: 1.0, nv + ny_c + viga_keys.index((secciones[s].b, secciones[s].h)): -1.0}, -np.inf, 0.0)
        nueva({nv + ny_c + i: 1.0 for i in range(ny_v)}, 0.0, float(tope_viga))
    for corte in cortes:
        if corte and corte[0] == "dom":
            # corte de dominancia: la sección del piso j fallaba la deriva con todos los demás pisos iguales o MÁS blandos
            # (c, b, h menores o iguales) → cualquier asignación en esa situación también falla
            _t, j0, asig = corte
            coefs = {}
            for (j, s), k in var.items():
                a = secciones[asig[j]]
                t = secciones[s]
                if j == j0:
                    if s == asig[j]:
                        coefs[k] = 1.0
                elif t.c <= a.c and t.b <= a.b and t.h <= a.h:
                    coefs[k] = 1.0
            if (j0, asig[j0]) in var:
                nueva(coefs, -np.inf, float(n - 1))
            continue
        coefs = {var[(j, s)]: 1.0 for j, s in enumerate(corte) if (j, s) in var}
        if len(coefs) == len(corte):
            nueva(coefs, -np.inf, float(n - 1))
    rows, cols, vals = [], [], []
    for r_, coefs in enumerate(filas):
        for k, v in coefs.items():
            rows.append(r_)
            cols.append(k)
            vals.append(v)
    A = coo_matrix((vals, (rows, cols)), shape=(len(filas), N)).tocsr()
    integ = np.ones(N)
    r = milp(obj, constraints=LinearConstraint(A, lb, ub), integrality=integ, bounds=Bounds(0, 1))
    if not r.success:
        return None, None
    elegido = [None] * n
    for (j, s), k in var.items():
        if r.x[k] > 0.5:
            elegido[j] = s
    return elegido, float(r.fun)


def _linealizar(p, ctx, secciones, ref: tuple[Seccion, ...]) -> list[list[float]]:
    """Razón deriva/cortante del piso j al cambiar SOLO ese piso de la asignación de referencia a cada sección de la biblioteca
    (exacta para un cambio; aproximación local para varios)."""
    n = len(ref)
    out = [[math.nan] * len(secciones) for _ in range(n)]
    for j in range(n):
        for s_, sec in enumerate(secciones):
            a = _analizar_asignacion(p, tuple(sec if jj == j else ref[jj] for jj in range(n)), ctx)
            v = float(sum(a["fe"][j:]))
            out[j][s_] = a["derivas"][j] / v if v > 0 else math.nan
    return out


def diseno_por_pisos(p: _dp.ProyectoPortico, *, columnas_mm=COLUMNAS_MM, bases_mm=BASES_MM, alturas_mm=ALTURAS_MM,
                     max_columnas_distintas: Optional[int] = None, max_vigas_distintas: Optional[int] = None,
                     columna_no_crece: bool = True, max_iter: int = MAX_ITER,
                     tolerancia_cota: float = TOLERANCIA_COTA, limite_tiempo_s: float = LIMITE_TIEMPO_S) -> InformePisos:
    t0 = time.perf_counter()
    if p.calidad_concreto not in FC_MPA_POR_CALIDAD:
        raise ValueError(f"calidad_concreto '{p.calidad_concreto}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")
    cap, info = _dp._capacidad(p)
    ctx = _dp._ctx_sismico(p, cap, info)
    fc = FC_MPA_POR_CALIDAD[p.calidad_concreto]
    mat = _viga.Materiales(fc=fc, fy=p.fy_mpa, fyt=p.fy_mpa)
    n = len(p.alturas_piso_m)
    secciones = [Seccion(float(c), float(b), float(h)) for c in columnas_mm for b in bases_mm for h in alturas_mm]
    S = len(secciones)
    # 1. biblioteca (pórticos uniformes)
    costo = [[math.nan] * S for _ in range(n)]
    razon = [[math.nan] * S for _ in range(n)]
    deriva_u = [[math.nan] * S for _ in range(n)]
    uniformes: list[tuple[int, Evaluacion]] = []
    for s, sec in enumerate(secciones):
        ev = evaluar_asignacion(p, (sec,) * n, cap, ctx, mat)
        for j, pj in enumerate(ev.pisos):
            deriva_u[j][s] = pj.deriva
            if pj.factible:
                costo[j][s] = pj.costo
            if ctx is not None and pj.cortante_diseno_kn > 0:
                razon[j][s] = pj.deriva / pj.cortante_diseno_kn
        if ev.factible:
            uniformes.append((s, ev))
    uniforme = min((e for _s, e in uniformes), key=lambda e: e.costo, default=None)
    if ctx is not None:        # razón deriva/cortante OPTIMISTA: el piso j con la sección s y los demás con la más rígida de la biblioteca
        rig = Seccion(max(x.c for x in secciones), max(x.b for x in secciones), max(x.h for x in secciones))
        for j in range(n):
            for s, sec in enumerate(secciones):
                a = _analizar_asignacion(p, tuple(sec if jj == j else rig for jj in range(n)), ctx)
                v = float(sum(a["fe"][j:]))
                razon[j][s] = a["derivas"][j] / v if v > 0 else math.nan
    t_bib = time.perf_counter() - t0
    # 2-3. MILP + verificación
    limite = _dp.DERIVA_MAX / max(p.factor_deriva_fisurada, 1e-9)
    v_star = ([pj.cortante_diseno_kn for pj in uniforme.pisos] if uniforme is not None
              else [0.0] * n)
    if ctx is not None and uniforme is not None:       # re-linealiza la deriva alrededor del mejor verificado (incumbente)
        razon = _linealizar(p, ctx, secciones, uniforme.asignacion)
    cortes: list[tuple[int, ...]] = []
    mejor: Optional[Evaluacion] = uniforme        # el mejor pórtico uniforme ya está verificado: es la cota de partida
    log: list[dict] = []
    completa = True
    sobreestima = 0.0          # mayor sobreestimación observada del costo del MILP frente al exacto (cota calibrada)
    observado = False
    for it in range(max_iter):
        if time.perf_counter() - t0 > limite_tiempo_s:
            log.append({"iteracion": it, "estado": "tiempo agotado"})
            completa = False
            break
        permitido = [[True] * S for _ in range(n)]
        if ctx is not None:
            for j in range(n):
                for s in range(S):
                    r = razon[j][s]
                    permitido[j][s] = (not math.isnan(r)) and r * v_star[j] <= limite * (1 + 1e-9)
        sel, obj = _resolver_milp(costo, permitido, secciones, n, max_columnas_distintas, max_vigas_distintas,
                                  columna_no_crece, cortes)
        if sel is None:
            log.append({"iteracion": it, "estado": "MILP infactible: no quedan asignaciones"})
            break
        tol = max(PISO_TOLERANCIA, 1.5 * sobreestima) if observado else tolerancia_cota
        if mejor is not None and obj * (1 - tol) >= mejor.costo:
            log.append({"iteracion": it, "estado": "cota del MILP (con tolerancia) ya no puede mejorar el mejor verificado", "cota": obj})
            break
        asign = tuple(secciones[s] for s in sel)
        ev = evaluar_asignacion(p, asign, cap, ctx, mat, descartar_por_deriva=True)
        cortes.append(tuple(sel))
        entrada = {"iteracion": it, "asignacion": [(a.c, a.b, a.h) for a in asign], "costo_milp": obj,
                   "factible": ev.factible, "costo_exacto": ev.costo if ev.factible else None}
        if ev.factible:
            observado = True
            sobreestima = max(sobreestima, (obj - ev.costo) / obj)
            if mejor is None or ev.costo < mejor.costo:
                mejor = ev
                if ctx is not None:
                    v_star = [pj.cortante_diseno_kn for pj in ev.pisos]
                    razon = _linealizar(p, ctx, secciones, ev.asignacion)
        else:
            entrada["motivos"] = [pj.motivo for pj in ev.pisos if pj.motivo] + ([] if ev.deriva_ok else ["deriva"])
            if ctx is not None:
                for j, pj in enumerate(ev.pisos):
                    if pj.deriva * p.factor_deriva_fisurada > _dp.DERIVA_MAX:
                        cortes.append(("dom", j, tuple(sel)))
            for j, pj in enumerate(ev.pisos):
                if ctx is not None and pj.cortante_diseno_kn > 0 and not math.isnan(pj.deriva):
                    razon[j][sel[j]] = max(razon[j][sel[j]], pj.deriva / pj.cortante_diseno_kn)
        for j, pj in enumerate(ev.pisos):               # costo exacto en contexto: se adopta el menor (estimación optimista)
            if pj.factible and not (costo[j][sel[j]] <= pj.costo):
                costo[j][sel[j]] = pj.costo
        log.append(entrada)
    ahorro = None
    if mejor is not None and uniforme is not None:
        ahorro = 100.0 * (uniforme.costo - mejor.costo) / uniforme.costo
    diag = {"biblioteca": S, "uniformes_factibles": len(uniformes), "t_biblioteca_s": round(t_bib, 2),
            "t_total_s": round(time.perf_counter() - t0, 2), "iteraciones": len(log), "busqueda_completa": completa and len(log) < max_iter}
    return InformePisos(cap, info, mejor, uniforme, ahorro, S, tuple(log), diag)
