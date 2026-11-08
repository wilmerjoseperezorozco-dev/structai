"""Núcleo vectorizado: análisis de pórtico plano para N secciones candidatas en una sola operación de NumPy.

Idea: la rigidez de un pórtico cuyas vigas cambian de sección es LINEAL en (A_viga, I_viga):
    K(b, h) = K_columnas + A(b,h)·K_axial_vigas + I(b,h)·K_flexión_vigas
así que las tres matrices se ensamblan una vez y las N rigideces salen por broadcasting (N, gdl, gdl).
Los casos D, L y E se resuelven juntos como columnas de una misma matriz de cargas (N, gdl, 3) — una sola factorización por
sección — y las combinaciones NSR-10 se obtienen por superposición (einsum), no resolviendo cada combinación.

Entrega, por sección, las mismas demandas que la ruta escalar (`diseno_portico._demanda`) y la deriva máxima de piso.
La paridad con la ruta escalar está probada en tests/test_grilla_vectorizada.py.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

COMBINACION_COLUMNAS = ("D", "L", "E")
N_PUNTOS_ENVOLVENTE = 41
CHUNK = 4000                      # secciones por bloque: acota memoria (~ CHUNK·gdl²·8 bytes)


@dataclass(frozen=True)
class Plantilla:
    """Parte del modelo que no depende de la sección de las vigas."""
    ndof: int
    libres: np.ndarray
    K0: np.ndarray
    Ka: np.ndarray
    Ki: np.ndarray
    F_unit: np.ndarray            # carga nodal equivalente por 1 kN/m sobre todas las vigas
    vigas: tuple[tuple[int, int, float], ...]     # (nodo i, nodo j, L)
    niveles: tuple[tuple[int, ...], ...]          # nodos de cada nivel (1..n)
    nodo_nivel_lateral: tuple[tuple[int, ...], ...]
    columnas: tuple = ()          # (entrepiso, eje, gdl, k_local·T) de cada columna
    nx: int = 0


def construir_plantilla(modelo, vigas_idx: list[int], nid, nx: int, ny: int, pt_modulo) -> Plantilla:
    n = len(modelo.nodos)
    ndof = 3 * n
    K0, Ka, Ki = np.zeros((ndof, ndof)), np.zeros((ndof, ndof)), np.zeros((ndof, ndof))
    F_unit = np.zeros(ndof)
    vigas_set = set(vigas_idx)
    info, cols = [], []
    for idx, e in enumerate(modelo.elementos):
        L = modelo.longitud(e)
        T, g = modelo._T(e), modelo._gdl(e)
        if idx in vigas_set:
            ea = pt_modulo.Elemento(e.i, e.j, e.E, 1.0, 0.0)
            ei = pt_modulo.Elemento(e.i, e.j, e.E, 0.0, 1.0)
            Ka[np.ix_(g, g)] += T.T @ modelo._k_local(ea, L) @ T
            Ki[np.ix_(g, g)] += T.T @ modelo._k_local(ei, L) @ T
            F_unit[g] -= T.T @ modelo._f0(-1.0, L)       # 1 kN/m hacia abajo → q local = -1
            info.append((e.i, e.j, L))
        else:
            K0[np.ix_(g, g)] += T.T @ modelo._k_local(e, L) @ T
            cols.append((idx // nx, idx % nx, np.array(g), modelo._k_local(e, L) @ T))
    niveles = tuple(tuple(nid(i, j) for i in range(nx)) for j in range(1, ny))
    return Plantilla(ndof, modelo._libres, K0, Ka, Ki, F_unit, tuple(info), niveles, niveles, tuple(cols), nx)


@dataclass(frozen=True)
class ResultadoLote:
    b: np.ndarray
    h: np.ndarray
    m_neg: np.ndarray
    m_pos_apoyo: np.ndarray
    m_pos_vano: np.ndarray
    v_max: np.ndarray
    v_centro: np.ndarray
    w_grav: np.ndarray
    v_grav: np.ndarray
    ln_min: float
    deriva_max: np.ndarray        # máx Δ/hp de todos los pisos (con Fs, no reducidas), NaN si no hay sismo
    fuerzas_e: Optional[np.ndarray]     # (N, niveles) E de diseño usada
    periodo_rayleigh: Optional[np.ndarray]
    col_f: Optional[np.ndarray] = None    # (N, columnas, 6, casos[D,L,E]) fuerzas de extremo locales (f0 = compresión en i)
    ux_e: Optional[np.ndarray] = None     # (N, niveles) desplazamiento horizontal medio por E


def _combos(combinaciones: dict, con_sismo: bool):
    nombres, filas = [], []
    for nombre, f in combinaciones.items():
        if not con_sismo and "E" in f:
            continue
        nombres.append(nombre)
        filas.append([f.get(c, 0.0) for c in COMBINACION_COLUMNAS])
    return nombres, np.array(filas)


def analizar_lote(tpl: Plantilla, *, b_mm: np.ndarray, h_mm: np.ndarray, Ec: float, factor_i_viga: float,
                  carga_muerta: float, carga_viva: float, peso_unit: float, c1_m: float,
                  fuerzas_e: Optional[np.ndarray], alturas_piso_m: tuple[float, ...], combinaciones: dict,
                  r_deriva: float = 1.0, nx: int = 1, pesos: Optional[np.ndarray] = None,
                  chunk: int = CHUNK, con_columnas: bool = False) -> ResultadoLote:
    """Analiza N secciones. fuerzas_e: (N, n_niveles) fuerzas laterales de diseño (ya divididas por R) o None.

    r_deriva: factor que convierte el desplazamiento por E en el de las fuerzas elásticas con I=1 (R·Sa_deriva/Sa).
    """
    b_mm, h_mm = np.asarray(b_mm, dtype=float), np.asarray(h_mm, dtype=float)
    N = b_mm.size
    con_sismo = fuerzas_e is not None
    nombres, C = _combos(combinaciones, con_sismo)
    salidas = {k: np.zeros(N) for k in ("m_neg", "m_pos_ap", "m_pos_vano", "v_max", "v_centro", "w_grav", "v_grav", "deriva")}
    ln_min = min(L - c1_m for _, _, L in tpl.vigas)
    ray = np.full(N, np.nan) if (con_sismo and pesos is not None) else None
    lib = tpl.libres
    ix = np.ix_(lib, lib)
    K0f, Kaf, Kif = tpl.K0[ix], tpl.Ka[ix], tpl.Ki[ix]
    ncasos = 3 if con_sismo else 2
    col_f = np.zeros((N, len(tpl.columnas), 6, ncasos)) if con_columnas else None
    ux_all = np.zeros((N, len(tpl.niveles))) if (con_columnas and con_sismo) else None
    nlev = len(tpl.niveles)
    for s in range(0, N, chunk):
        sl = slice(s, min(N, s + chunk))
        b, h = b_mm[sl], h_mm[sl]
        n = b.size
        A = b * h / 1e6
        I = factor_i_viga * (b / 1000) * (h / 1000) ** 3 / 12
        Kf = K0f[None] + A[:, None, None] * Kaf[None] + I[:, None, None] * Kif[None]
        w_pp = peso_unit * b / 1000 * h / 1000
        wD, wL = carga_muerta + w_pp, np.full(n, carga_viva)
        F = np.zeros((n, tpl.ndof, ncasos))
        F[:, :, 0] = wD[:, None] * tpl.F_unit[None]
        F[:, :, 1] = wL[:, None] * tpl.F_unit[None]
        if con_sismo:
            fe = fuerzas_e[sl]
            for j, nodos in enumerate(tpl.niveles):
                for nd in nodos:
                    F[:, 3 * nd, 2] = fe[:, j] / len(nodos)
        try:
            uf = np.linalg.solve(Kf, F[:, lib, :])
        except np.linalg.LinAlgError as exc:
            raise ValueError("Modelo inestable en alguna sección del lote") from exc
        U = np.zeros((n, tpl.ndof, ncasos))
        U[:, lib, :] = uf
        # --- fuerzas en los extremos de cada viga y envolventes ------------------
        m_neg = np.zeros(n); m_pos_ap = np.zeros(n); m_pos_vano = np.zeros(n)
        v_max = np.zeros(n); v_centro = np.zeros(n); v_grav = np.zeros(n)
        EI = Ec * I
        w_caso = np.stack([wD, wL] + ([np.zeros(n)] if con_sismo else []), axis=1)       # (n, casos)
        for (i, j, L) in tpl.vigas:
            a, bb, c, d = 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
            uyi, uyj = U[:, 3 * i + 1, :], U[:, 3 * j + 1, :]
            rzi, rzj = U[:, 3 * i + 2, :], U[:, 3 * j + 2, :]
            V1 = a[:, None] * (uyi - uyj) + bb[:, None] * (rzi + rzj) + w_caso * L / 2
            M1 = bb[:, None] * (uyi - uyj) + c[:, None] * rzi + d[:, None] * rzj + w_caso * L**2 / 12
            xi, xf = c1_m / 2, L - c1_m / 2
            x2h = np.stack([c1_m / 2 + 2 * h / 1000, L - c1_m / 2 - 2 * h / 1000], axis=1)
            x_unif = np.broadcast_to(np.linspace(0.0, L, N_PUNTOS_ENVOLVENTE), (n, N_PUNTOS_ENVOLVENTE))
            extra = np.clip(np.concatenate([np.broadcast_to([xi, xf], (n, 2)), x2h], axis=1), 0.0, L)
            xs = np.concatenate([x_unif, extra], axis=1)                          # (n, K)
            Vc = V1[:, :, None] - w_caso[:, :, None] * xs[:, None, :]             # (n, casos, K)
            Mc = -M1[:, :, None] + V1[:, :, None] * xs[:, None, :] - w_caso[:, :, None] * xs[:, None, :] ** 2 / 2
            Cc = C[:, :ncasos]
            M = np.einsum("kc,nct->nkt", Cc, Mc)
            V = np.einsum("kc,nct->nkt", Cc, Vc)
            k0 = N_PUNTOS_ENVOLVENTE
            M_hi, M_lo = M.max(axis=1), M.min(axis=1)                              # (n, K)
            Vabs = np.abs(V).max(axis=1)
            m_neg = np.maximum(m_neg, np.maximum(-M_lo[:, k0], -M_lo[:, k0 + 1]))
            m_pos_ap = np.maximum(m_pos_ap, np.maximum(M_hi[:, k0], M_hi[:, k0 + 1]))
            v_max = np.maximum(v_max, np.maximum(Vabs[:, k0], Vabs[:, k0 + 1]))
            v_centro = np.maximum(v_centro, np.maximum(Vabs[:, k0 + 2], Vabs[:, k0 + 3]))
            interior = (xs > xi) & (xs < xf)
            m_pos_vano = np.maximum(m_pos_vano, np.where(interior, M_hi, -np.inf).max(axis=1))
            wg = 1.2 * wD + 1.0 * wL
            v_grav = np.maximum(v_grav, wg * L / 2)
        if con_columnas:
            for ic, (_, _, g, kT) in enumerate(tpl.columnas):
                col_f[sl, ic] = np.einsum("ab,nbc->nac", kT, U[:, g, :])
        salidas["m_neg"][sl], salidas["m_pos_ap"][sl] = m_neg, m_pos_ap
        salidas["m_pos_vano"][sl] = np.maximum(m_pos_vano, 0.0)
        salidas["v_max"][sl], salidas["v_centro"][sl], salidas["v_grav"][sl] = v_max, v_centro, v_grav
        salidas["w_grav"][sl] = 1.2 * wD + 1.0 * wL
        if con_sismo:
            ux = np.stack([U[:, [3 * nd for nd in nodos], 2].mean(axis=1) for nodos in tpl.niveles], axis=1)   # (n, niveles)
            if ux_all is not None:
                ux_all[sl] = ux
            ux0 = np.concatenate([np.zeros((n, 1)), ux], axis=1)
            hp = np.asarray(alturas_piso_m, dtype=float)
            salidas["deriva"][sl] = (np.abs(np.diff(ux0, axis=1)) * r_deriva / hp).max(axis=1)
            if ray is not None:
                fs = fuerzas_e[sl]
                d_el = ux
                m = pesos[sl] / 9.8
                den = (fs * d_el).sum(axis=1)
                with np.errstate(invalid="ignore", divide="ignore"):
                    ray[sl] = np.where(den > 0, 2 * math.pi * np.sqrt((m * d_el**2).sum(axis=1) / den), np.nan)
    deriva = salidas["deriva"] if con_sismo else np.full(N, np.nan)
    return ResultadoLote(b_mm, h_mm, salidas["m_neg"], salidas["m_pos_ap"], salidas["m_pos_vano"], salidas["v_max"],
                         salidas["v_centro"], salidas["w_grav"], salidas["v_grav"], ln_min, deriva,
                         fuerzas_e if con_sismo else None, ray, col_f, ux_all)
