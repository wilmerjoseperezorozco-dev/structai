"""Edificio de pórticos de concreto en 3D (#275, F4): análisis 3D → diseño de vigas y columnas → cantidades, costo y CO₂
→ memoria de cálculo (F0, `contrato_motor.memoria_calculo`).

Cadena:
  1. Modelo 3D (motor-analisis.portico3d) con diafragma rígido por nivel, inercias fisuradas 0,70·Ig (columnas) y 0,35·Ig (vigas).
  2. Cargas D y L de la losa repartidas a las vigas por líneas a 45° (resultante igual, uniforme equivalente) + peso propio.
  3. Periodo modal por dirección (modal3d), T = mín(T_modelo, Cu·Ta) (A.4.2.1); FHE (A.4.3) con Sa e I (A.2.6, A.2.5).
  4. Derivas con Fs y torsión accidental con Ax (sismo3d.analizar_fhe, A.6, A.3.6.7).
  5. E = Fs/R (B.2.4.2.1, A.3.3), casos ±e; efectos ortogonales 100 % + 30 % (A.3.6.3); combinaciones B.2.4.2.
  6. Vigas por nivel y columnas por piso diseñadas con motor-concreto (C.21: DES, DMO o DMI); columnas de arriba hacia
     abajo para la columna fuerte–viga débil con la sección real del piso superior; flexión biaxial por contorno lineal.
  7. Cantidades (motor-concreto.cantidades_costo) y memoria de cálculo.
Las secciones son ENTRADAS (este módulo verifica y arma el refuerzo; no optimiza secciones: eso es F1/F2 de #275).
"""
from __future__ import annotations

import dataclasses
import importlib
import itertools
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from .cargador import cargar_motor, modulo_cortante_basal

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)
from contrato_motor import memoria_calculo as mc  # noqa: E402

cargar_motor("motor-analisis", "motor_analisis")
_p3 = importlib.import_module("motor_analisis.portico3d")
_s3 = importlib.import_module("motor_analisis.sismo3d")
_m3 = importlib.import_module("motor_analisis.modal3d")
cargar_motor("motor-concreto", "motor_concreto")
_dv = importlib.import_module("motor_concreto.diseno_viga")
_col = importlib.import_module("motor_concreto.columna")
_cc = importlib.import_module("motor_concreto.cantidades_costo")
_vg = importlib.import_module("motor_concreto.viga")
_gp = modulo_cortante_basal()

MOTOR = "orquestador.diseno_edificio_3d/0.1"
FI_COL, FI_VIGA = 0.70, 0.35          # C.10.10.4.1 (inercias fisuradas)
GAMMA_CONCRETO = 24.0                 # kN/m³ (B.3, concreto reforzado)
Q_MAX = 1.0 / 3.0                     # δs ≤ 1,5 (C.10.10.7)
ORTOGONAL = 0.30                      # A.3.6.3
CASOS = ("D", "L", "Ex+e", "Ex-e", "Ey+e", "Ey-e")
N_CASOS_BASE = len(CASOS)
# Deflexiones (C.9.5; números verificados en el corpus nsr10_chunks, 2026-11-20)
FR_COEF = 0.62                        # fr = 0,62·λ·√f'c (C.9-10), concreto de peso normal
XI_LARGO_PLAZO = 2.0                  # ξ para 5 años o más (C.9.5.2.5)
ES_MPA = 200_000.0
PSI_SOSTENIDA = 0.25                  # HIPÓTESIS: fracción de L que actúa de forma sostenida (vivienda/oficinas)
LIM_L_ENTREPISO, LIM_L_CUBIERTA = 360.0, 180.0          # Tabla C.9.5(b): inmediata por L
LIM_FRAGIL, LIM_NO_FRAGIL = 480.0, 240.0                # Tabla C.9.5(b): después de unir elementos no estructurales
H_MIN_AMBOS_CONT, H_MIN_UN_EXTREMO = 21.0, 18.5          # Tabla C.9.5(a), vigas (informativa: no aplica con divisiones frágiles)

NO_VERIFICA = (
    "Nudos viga-columna (C.21.7): cortante en el nudo y anclaje de barras.",
    "Losas, escaleras, cimentación, muros y elementos no estructurales.",
    "Viento (Título B.6), empuje de tierras, cargas de construcción y cargas verticales sísmicas (A.3.6.13).",
    "Carga viva alternada combinada con sismo: los patrones de C.8.11.2 se aplican solo en 1.2D+1.6L.",
    "Efectos P-Δ explícitos: solo se evalúa Qi (A.6.2.3) y la magnificación δs de C.10.10.7.",
    "Empalmes, longitudes de desarrollo y despiece real (las cantidades subestiman el acero entre 5 y 15 %).",
    "Deflexiones con aleta de losa, contraflecha o secuencia constructiva: se usa la sección rectangular (conservador).",
    "Irregularidades en planta y altura (A.3.3) más allá de la torsional: se usa φa = φp = φr = 1,0.",
    "Flexión biaxial con superficie de interacción exacta: se usa el contorno lineal (conservador).",
)


@dataclass(frozen=True)
class ProyectoEdificio3D:
    luces_x_m: tuple[float, ...]
    luces_y_m: tuple[float, ...]
    alturas_piso_m: tuple[float, ...]                  # de abajo hacia arriba
    columnas_mm: tuple[float, ...]                     # lado de la columna cuadrada de cada piso
    vigas_mm: tuple[tuple[float, float], ...]          # (b, h) de las vigas de cada nivel (techo de cada piso)
    carga_muerta_kpa: float                            # losa + acabados + muros divisorios (sin vigas ni columnas)
    carga_viva_kpa: float
    aa: float
    av: float
    perfil_suelo: str
    grupo_uso: str = "I"
    capacidad: str = "DES"
    fc_mpa: float = 28.0
    fy_mpa: float = 420.0
    recubrimiento_mm: float = 40.0
    nombre: str = "Edificio de pórticos"
    uso: str = "residencial"
    divipola: Optional[str] = None                     # código de municipio; nunca coordenadas
    divisiones_fragiles: bool = True                   # mampostería ligada a las vigas → límite ℓ/480 (Tabla C.9.5(b))

    def __post_init__(self):
        n = len(self.alturas_piso_m)
        if n < 1 or len(self.columnas_mm) != n or len(self.vigas_mm) != n:
            raise ValueError("Debe haber una columna y una viga por piso (alturas, columnas_mm y vigas_mm de igual longitud)")
        if not self.luces_x_m or not self.luces_y_m or min(self.luces_x_m + self.luces_y_m) <= 0:
            raise ValueError("Se necesita al menos un vano positivo en cada dirección")
        if min(self.alturas_piso_m) <= 0 or self.carga_muerta_kpa < 0 or self.carga_viva_kpa < 0:
            raise ValueError("Alturas positivas y cargas no negativas")
        for (b, h), c in zip(self.vigas_mm, self.columnas_mm):
            if min(b, h, c) <= 0:
                raise ValueError("Secciones positivas")
        if self.capacidad not in ("DES", "DMO", "DMI"):
            raise ValueError("capacidad: DES, DMO o DMI")


@dataclass
class Modelo:
    portico: object
    xs: list[float]
    ys: list[float]
    meta: list[tuple]                 # por elemento: ("col", piso, i, j) | ("vx"/"vy", nivel, i, j)
    pisos: list                       # sismo3d.Piso (carga vertical D + L)
    pesos: list[float]                # peso sísmico por nivel (D + peso propio), kN
    cargas_d: dict[int, tuple]
    cargas_l: dict[int, tuple]
    w_viga: dict[int, tuple[float, float]]    # elemento viga → (wD, wL) kN/m hacia abajo


@dataclass
class InformeEdificio3D:
    proyecto: ProyectoEdificio3D
    sismo: dict
    deriva: dict
    vigas: list[dict] = field(default_factory=list)
    columnas: list[dict] = field(default_factory=list)
    cantidades: Optional[dict] = None
    fallas: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    memoria: Optional[object] = None

    @property
    def cumple(self) -> bool:
        return not self.fallas


# ---------------------------------------------------------------------------------------------------- modelo
def _rect(b, h):
    a, c = max(b, h), min(b, h)
    J = a * c**3 * (1 / 3 - 0.21 * c / a * (1 - c**4 / (12 * a**4)))
    return b * h, b * h**3 / 12, h * b**3 / 12, J


def _area_45(a: float, b: float) -> float:
    """Área de losa que llega al lado de longitud a de un panel a×b con líneas de rotura a 45°."""
    s = min(a, b)
    return s * s / 4 if a <= b else a * b / 2 - b * b / 4


def construir_modelo(p: ProyectoEdificio3D) -> Modelo:
    ec = 4700 * math.sqrt(p.fc_mpa) * 1000.0
    gc = ec / (2 * (1 + 0.2))
    xs = [0.0] + list(itertools.accumulate(p.luces_x_m))
    ys = [0.0] + list(itertools.accumulate(p.luces_y_m))
    nodos, els, meta, apoyos, dia = [], [], [], {}, []
    cd, cl, wv = {}, {}, {}
    prev = None
    for nv in range(len(p.alturas_piso_m) + 1):
        z = sum(p.alturas_piso_m[:nv])
        fila = {}
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                fila[(i, j)] = len(nodos)
                nodos.append(_p3.Nodo3D(x, y, z))
        if nv == 0:
            apoyos.update({k: (True,) * 6 for k in fila.values()})
        else:
            piso = nv - 1
            c = p.columnas_mm[piso] / 1000
            Ac, Ic, _, Jc = _rect(c, c)
            for (i, j), k in fila.items():
                cd[len(els)] = (0.0, 0.0, -GAMMA_CONCRETO * Ac)
                els.append(_p3.Elemento3D(prev[(i, j)], k, ec, gc, Ac, FI_COL * Ic, FI_COL * Ic, Jc))
                meta.append(("col", piso, i, j))
            b, h = (v / 1000 for v in p.vigas_mm[piso])
            Av, Ivf, Ivd, Jv = _rect(b, h)
            pp = GAMMA_CONCRETO * Av
            for j in range(len(ys)):
                for i in range(len(xs) - 1):
                    a = p.luces_x_m[i]
                    area = sum(_area_45(a, p.luces_y_m[jj]) for jj in (j - 1, j) if 0 <= jj < len(p.luces_y_m))
                    wD, wL = p.carga_muerta_kpa * area / a + pp, p.carga_viva_kpa * area / a
                    k = len(els)
                    els.append(_p3.Elemento3D(fila[(i, j)], fila[(i + 1, j)], ec, gc, Av, FI_VIGA * Ivd, FI_VIGA * Ivf, Jv))
                    meta.append(("vx", nv, i, j))
                    cd[k], cl[k], wv[k] = (0.0, 0.0, -wD), (0.0, 0.0, -wL), (wD, wL)
            for i in range(len(xs)):
                for j in range(len(ys) - 1):
                    a = p.luces_y_m[j]
                    area = sum(_area_45(a, p.luces_x_m[ii]) for ii in (i - 1, i) if 0 <= ii < len(p.luces_x_m))
                    wD, wL = p.carga_muerta_kpa * area / a + pp, p.carga_viva_kpa * area / a
                    k = len(els)
                    els.append(_p3.Elemento3D(fila[(i, j)], fila[(i, j + 1)], ec, gc, Av, FI_VIGA * Ivd, FI_VIGA * Ivf, Jv))
                    meta.append(("vy", nv, i, j))
                    cd[k], cl[k], wv[k] = (0.0, 0.0, -wD), (0.0, 0.0, -wL), (wD, wL)
            dia.append(_p3.Diafragma(f"P{nv}", tuple(fila.values()), xs[-1] / 2, ys[-1] / 2))
        prev = fila
    lx, ly = xs[-1], ys[-1]
    area = lx * ly
    n = len(p.alturas_piso_m)
    nnod = len(xs) * len(ys)
    long_vigas = len(ys) * lx + len(xs) * ly
    pesos, pisos = [], []
    for piso in range(n):
        b, h = (v / 1000 for v in p.vigas_mm[piso])
        col = lambda s: GAMMA_CONCRETO * (p.columnas_mm[s] / 1000) ** 2 * p.alturas_piso_m[s] * nnod  # noqa: E731
        w = p.carga_muerta_kpa * area + GAMMA_CONCRETO * b * h * long_vigas + 0.5 * col(piso) + (0.5 * col(piso + 1) if piso + 1 < n else 0.0)
        pesos.append(w)
        pisos.append(_s3.Piso(f"P{piso + 1}", p.alturas_piso_m[piso], lx, ly, w + p.carga_viva_kpa * area))
    mod = _p3.Portico3D(nodos, els, apoyos, dia)
    return Modelo(mod, xs, ys, meta, pisos, pesos, cd, cl, wv)


# ---------------------------------------------------------------------------------------------------- sismo
def _periodos_dir(md) -> tuple[float, float]:
    """Periodo del modo con mayor masa efectiva en X y en Y."""
    return float(md.periodos[np.argmax(md.masa_efectiva[:, 0])]), float(md.periodos[np.argmax(md.masa_efectiva[:, 1])])


def analisis_sismico(p: ProyectoEdificio3D, m: Modelo) -> dict:
    fa, fv = _gp.coef_fa(p.aa, p.perfil_suelo), _gp.coef_fv(p.av, p.perfil_suelo)
    I = _gp.COEF_IMPORTANCIA[p.grupo_uso]
    alturas = tuple(itertools.accumulate(p.alturas_piso_m))
    ta = _gp.periodo_aproximado(alturas[-1], "porticos_concreto")
    cuta = _gp.cu(p.av, fv) * ta
    masas = [(w / _gp.G, w / _gp.G * (q.dim_x_m**2 + q.dim_y_m**2) / 12) for w, q in zip(m.pesos, m.pisos)]
    md = _m3.modos(m.portico, masas)
    tx, ty = _periodos_dir(md)
    r = _gp.r_reducido(p.capacidad)
    out = {"fa": fa, "fv": fv, "I": I, "Ta_s": ta, "CuTa_s": cuta, "R": r, "W_kn": sum(m.pesos),
           "periodos_modales_s": md.periodos[:6].tolist()}
    for d, t in (("x", tx), ("y", ty)):
        T = min(t, cuta)
        sa, sa_d = _gp.sa_espectro(T, p.aa, p.av, fa, fv, I), _gp.sa_espectro(T, p.aa, p.av, fa, fv, 1.0)
        fs = _gp.distribuir_fuerzas(sa * sum(m.pesos), tuple(m.pesos), alturas, T)
        fs_d = _gp.distribuir_fuerzas(sa_d * sum(m.pesos), tuple(m.pesos), alturas, T)
        out[d] = {"T_modelo_s": t, "T_s": T, "gobierna_CuTa": t > cuta, "Sa": sa, "Vs_kn": sa * sum(m.pesos),
                  "Fs_kn": list(fs), "Fs_deriva_kn": list(fs_d), "E_kn": [f / r for f in fs], "k": _gp.exponente_k(T)}
    return out


# ---------------------------------------------------------------------------------------------------- fuerzas
def _resolver_casos(p, m: Modelo, sis: dict, ax: dict) -> np.ndarray:
    """F[c, elemento, 12] para los casos D, L, Ex±e, Ey±e (E = Fs/R, momento torsor con Ax)."""
    res = [m.portico.resolver(_p3.Caso3D("D", uniformes=m.cargas_d)),
           m.portico.resolver(_p3.Caso3D("L", uniformes=m.cargas_l))]
    casos = _s3._casos(m.pisos, sis["x"]["E_kn"], sis["y"]["E_kn"], ax)
    orden = {"Ex+e": 0, "Ex-e": 1, "Ey+e": 2, "Ey-e": 3}
    resE = [None] * 4
    for nom, _d, caso in casos:
        resE[orden[nom]] = m.portico.resolver(caso)
    res += resE
    ne = len(m.portico.elementos)
    return np.array([[r.f_extremos[k] for k in range(ne)] for r in res]), res


def _patrones_viva(m: Modelo) -> list[tuple[str, frozenset]]:
    """Disposición de la carga viva de C.8.11.2, por viga (con su carga tributaria) y alternando por nivel (C.8.11.1):
    (b) vanos alternados (2 patrones complementarios) y (a) pares de vanos adyacentes (4 desfases). Devuelve
    (nombre, vigas cargadas)."""
    vigas = [(k, t) for k, t in enumerate(m.meta) if t[0] in ("vx", "vy")]
    pos = lambda t: t[2] if t[0] == "vx" else t[3]  # noqa: E731  posición de la viga a lo largo de su eje
    pats = [(f"alternados {r}", frozenset(k for k, t in vigas if (pos(t) + t[1]) % 2 == r)) for r in (0, 1)]
    pats += [(f"adyacentes {s}", frozenset(k for k, t in vigas if ((pos(t) + s) // 2 + t[1]) % 2 == 0)) for s in range(4)]
    vistos, out = set(), []
    for nom, s in pats:                                              # con pocos vanos algunos patrones coinciden
        if s and s not in vistos:
            vistos.add(s)
            out.append((nom, s))
    return out


def _resolver_patrones(m: Modelo, pats) -> np.ndarray:
    """F[p, elemento, 12] de la carga viva en cada patrón."""
    ne = len(m.portico.elementos)
    out = []
    for nom, s in pats:
        r = m.portico.resolver(_p3.Caso3D(f"L {nom}", uniformes={k: m.cargas_l[k] for k in s}))
        out.append([r.f_extremos[k] for k in range(ne)])
    return np.array(out).reshape(len(pats), ne, 12)


def _extender_combinaciones(nombres, C, es_e, pats):
    """Agrega 1.2D + 1.6·L_patrón por patrón (C.8.11.2) como casos 6.. de la matriz."""
    npat = len(pats)
    Cx = np.hstack([C, np.zeros((len(C), npat))])
    filas = []
    for i, (nom, _s) in enumerate(pats):
        f = np.zeros(N_CASOS_BASE + npat)
        f[0], f[N_CASOS_BASE + i] = 1.2, 1.6
        filas.append(f)
    if filas:
        Cx = np.vstack([Cx, filas])
    return (list(nombres) + [f"1.2D+1.6L[{nom}]" for nom, _ in pats], Cx,
            np.concatenate([es_e, np.zeros(npat, dtype=bool)]))


def combinaciones() -> tuple[list[str], np.ndarray, np.ndarray]:
    """Matriz C (K × 6 casos) de B.2.4.2 con E = E_dir,±e ± 0,3·E_perp,±e (A.3.6.3). Devuelve (nombres, C, es_sismo)."""
    nombres, filas = ["1.4D", "1.2D+1.6L"], [[1.4, 0, 0, 0, 0, 0], [1.2, 1.6, 0, 0, 0, 0]]
    evec = []
    for princ, perp in (((2, 3), (4, 5)), ((4, 5), (2, 3))):
        for a in princ:
            for b in perp:
                for s in (1.0, -1.0):
                    v = [0.0] * 6
                    v[a] += 1.0
                    v[b] += s * ORTOGONAL
                    evec.append((f"{CASOS[a]}{'+' if s > 0 else '-'}0.3{CASOS[b]}", v))
    for nom, v in evec:
        for sg in (1.0, -1.0):
            for base, (cD, cL) in (("1.2D+1.0L", (1.2, 1.0)), ("0.9D", (0.9, 0.0))):
                nombres.append(f"{base}{'+' if sg > 0 else '-'}[{nom}]")
                filas.append([cD, cL] + [sg * x for x in v[2:]])
    C = np.array(filas)
    return nombres, C, np.abs(C[:, 2:]).sum(axis=1) > 0


# ---------------------------------------------------------------------------------------------------- vigas
def _q_casos(k, wD, wL, ncasos, pats) -> np.ndarray:
    """Carga distribuida local y por caso (y local = vertical hacia arriba): D, L, sismo (0) y patrones de L."""
    q = np.zeros(ncasos)
    q[0], q[1] = -wD, -wL
    for i, (_nom, s) in enumerate(pats):
        q[N_CASOS_BASE + i] = -wL if k in s else 0.0
    return q


def _demanda_vigas(p, m: Modelo, F, C, nivel: int, pats=()):
    piso = nivel - 1
    c = p.columnas_mm[piso] / 1000
    h = p.vigas_mm[piso][1] / 1000
    vigas = [k for k, t in enumerate(m.meta) if t[0] in ("vx", "vy") and t[1] == nivel]
    m_neg = m_pos_ap = m_pos_vano = v_max = v_grav = v_centro = w_grav = 0.0
    ln_min = math.inf
    grav = np.zeros(len(F))
    grav[0], grav[1] = 1.2, 1.0
    for k in vigas:
        L = m.portico.longitud(m.portico.elementos[k])
        wD, wL = m.w_viga[k]
        q = _q_casos(k, wD, wL, len(F), pats)
        xf = (c / 2, L - c / 2)
        x2h = (min(c / 2 + 2 * h, L / 2), max(L - c / 2 - 2 * h, L / 2))
        xin = np.linspace(c / 2, L - c / 2, 21)[1:-1]
        xs = np.array([*xf, *x2h, *xin])
        Fi = F[:, k, :]                                              # (6, 12)
        Mc = -Fi[:, 5][:, None] + Fi[:, 1][:, None] * xs[None, :] + q[:, None] * xs[None, :] ** 2 / 2   # (6, npts)
        Vc = Fi[:, 1][:, None] + q[:, None] * xs[None, :]
        M, V = C @ Mc, C @ Vc                                        # (K, npts)
        m_neg = max(m_neg, float(-M[:, :2].min()))
        m_pos_ap = max(m_pos_ap, float(M[:, :2].max()))
        m_pos_vano = max(m_pos_vano, float(M[:, 4:].max()))
        v_max = max(v_max, float(np.abs(V[:, :2]).max()))
        v_centro = max(v_centro, float(np.abs(V[:, 2:4]).max()))
        v_grav = max(v_grav, float(np.abs(grav @ Vc[:, :2]).max()))
        w_grav = max(w_grav, 1.2 * wD + 1.0 * wL)
        ln_min = min(ln_min, L - c)
    dem = _dv.DemandaViga(luz_libre_m=ln_min, M_neg_apoyo=max(m_neg, 0.0), M_pos_apoyo=max(m_pos_ap, 0.0),
                          M_pos_vano=max(m_pos_vano, 0.0), V_max=v_max, V_gravedad=v_grav, w_grav=w_grav, V_centro=v_centro)
    return dem, vigas


def _cantidades_vigas(p, m: Modelo, d, vigas, c_mm: float):
    tot = _cc.Cantidades(0.0, 0.0, 0.0)
    for k in vigas:
        ln = m.portico.longitud(m.portico.elementos[k]) - c_mm / 1000
        n_est = max(2, _dv.contar_estribos(ln * 1000, d.h, d.s_conf, d.s_centro, d.nivel != "DMI"))
        tot = tot + _cc.cantidades_viga(dataclasses.replace(d, n_estribos=n_est), ln, p.recubrimiento_mm)
    return tot


def _mn_viga(d, mat, rec) -> tuple[float, float]:
    dd = _dv._d(d.h, d.dia, d.estribo_dia, rec)
    a = _vg.AREA_MM2[d.dia]
    return _dv._mn_nominal(d.n_sup * a, d.b, dd, mat.fc, mat.fy)[0], _dv._mn_nominal(d.n_inf * a, d.b, dd, mat.fc, mat.fy)[0]


# ---------------------------------------------------------------------------------------------------- columnas
def _ie(Ma, Ig, Icr, Mcr) -> float:
    """Inercia efectiva (C.9-8), ≤ Ig."""
    if Ma <= Mcr:
        return Ig
    r = (Mcr / Ma) ** 3
    return min(Ig, r * Ig + (1 - r) * Icr)


def _icr(b, d, dp, As, Asp, n) -> float:
    """Inercia fisurada transformada de sección rectangular doblemente reforzada (m⁴; entradas en m y m²)."""
    a2, a1, a0 = b / 2, (n - 1) * Asp + n * As, -((n - 1) * Asp * dp + n * As * d)
    c = (-a1 + math.sqrt(a1 * a1 - 4 * a2 * a0)) / (2 * a2)
    return b * c**3 / 3 + (n - 1) * Asp * (c - dp) ** 2 + n * As * (d - c) ** 2


def _flecha_rel(Mx, xs, L, EI) -> float:
    """Flecha en el centro relativa a la cuerda: δ = ∫ M·m̄ / EI, m̄ = momento por carga unitaria en L/2 (biapoyada).
    M positivo = flexión que tracciona abajo; δ positiva hacia abajo."""
    mb = np.where(xs <= L / 2, xs / 2, (L - xs) / 2)
    y = Mx * mb
    return float(np.sum((y[1:] + y[:-1]) * np.diff(xs)) / 2 / EI)    # trapecios (numpy 1.x y 2.x)


def _deflexiones(p, m: Modelo, F, vigas, d, nivel: int, pats, mat):
    """Deflexiones de servicio de las vigas del nivel con el refuerzo d (C.9.5.2): Ie de C.9-8 en el centro de la luz
    (C.9.5.2.4), largo plazo con λΔ = ξ/(1+50ρ') (C.9.5.2.5) y límites de la Tabla C.9.5(b). Devuelve las
    verificaciones de la viga que gobierna."""
    rec = p.recubrimiento_mm
    dd = _dv._d(d.h, d.dia, d.estribo_dia, rec) / 1000
    a = _vg.AREA_MM2[d.dia] / 1e6
    b, h = d.b / 1000, d.h / 1000
    As, Asp, dp = d.n_inf * a, d.n_sup * a, h - dd
    ec = 4700 * math.sqrt(mat.fc) * 1000.0                            # kN/m²
    n = ES_MPA / (4700 * math.sqrt(mat.fc))
    Ig, Icr = b * h**3 / 12, _icr(b, dd, dp, As, Asp, n)
    Mcr = FR_COEF * math.sqrt(mat.fc) * 1000.0 * Ig / (h / 2)
    rho_p = Asp / (b * dd)
    lam = XI_LARGO_PLAZO / (1 + 50 * rho_p)
    cubierta = nivel == len(p.alturas_piso_m)
    lim_L = LIM_L_CUBIERTA if cubierta else LIM_L_ENTREPISO
    lim_t = LIM_FRAGIL if p.divisiones_fragiles else LIM_NO_FRAGIL
    peor = None
    for k in vigas:
        L = m.portico.longitud(m.portico.elementos[k])
        wD, wL = m.w_viga[k]
        xs = np.linspace(0.0, L, 41)
        q = _q_casos(k, wD, wL, len(F), pats)
        Mc = -F[:, k, 5][:, None] + F[:, k, 1][:, None] * xs[None, :] + q[:, None] * xs[None, :] ** 2 / 2
        MD = Mc[0]
        MLs = [Mc[1]] + [Mc[N_CASOS_BASE + i] for i in range(len(pats)) if k in pats[i][1]]
        ML = max(MLs, key=lambda x: float(x[len(xs) // 2]))              # disposición con mayor momento en el centro
        mid = len(xs) // 2
        Ma_D, Ma_DL = max(float(MD[mid]), 0.0), max(float(MD[mid] + ML[mid]), 0.0)
        dD = _flecha_rel(MD, xs, L, ec * _ie(Ma_D, Ig, Icr, Mcr))
        dDL = _flecha_rel(MD + ML, xs, L, ec * _ie(Ma_DL, Ig, Icr, Mcr))
        dL = max(dDL - dD, 0.0)
        d_t = lam * (dD + PSI_SOSTENIDA * dL) + dL
        r = max(dL / (L / lim_L), d_t / (L / lim_t))
        if peor is None or r > peor[0]:
            peor = (r, L, dL, d_t)
    if peor is None:
        return []
    _, L, dL, d_t = peor
    ln = L - p.columnas_mm[nivel - 1] / 1000
    nota_a = (f"h = {d.h:g} mm; Tabla C.9.5(a) daría ℓ/{H_MIN_AMBOS_CONT:g} = {1000 * ln / H_MIN_AMBOS_CONT:.0f} mm (ambos extremos "
              f"continuos), pero no aplica con divisiones frágiles (C.9.5.2.1): se calcula la deflexión")
    hip = (f"Ie en el centro (C.9.5.2.4), sección rectangular sin aleta; λΔ = {lam:.2f} con ρ' de {d.n_sup} barras superiores; "
           f"carga sostenida D + {PSI_SOSTENIDA:g}·L (HIPÓTESIS); disposición de L de C.8.11.2 con mayor momento en el centro; ℓ = {L:.2f} m entre ejes")
    return [
        _vg.Verificacion(f"Deflexión inmediata por L ≤ ℓ/{lim_L:g} ({'cubierta' if cubierta else 'entrepiso'})", 1000 * dL,
                         1000 * L / lim_L, "mm", dL <= L / lim_L, "C.9.5.2.2, Tabla C.9.5(b)", nota_a),
        _vg.Verificacion(f"Deflexión después de unir elementos no estructurales ≤ ℓ/{lim_t:g} "
                         f"({'frágiles' if p.divisiones_fragiles else 'no frágiles'})", 1000 * d_t, 1000 * L / lim_t, "mm",
                         d_t <= L / lim_t, "C.9.5.2.5, Tabla C.9.5(b)", hip),
    ]


def _k_jackson_moreland(psi_a: float, psi_b: float) -> float:
    psi_m = 0.5 * (psi_a + psi_b)
    k = (20 - psi_m) / 20 * math.sqrt(1 + psi_m) if psi_m < 2 else 0.9 * math.sqrt(1 + psi_m)
    return max(k, 1.0)


def _klu(p, m: Modelo, piso: int) -> float:
    ec = 1.0                                                        # solo cocientes
    n = len(p.alturas_piso_m)
    ic = lambda s: FI_COL * (p.columnas_mm[s] / 1000) ** 4 / 12      # noqa: E731
    ib = lambda nv: FI_VIGA * (p.vigas_mm[nv - 1][0] / 1000) * (p.vigas_mm[nv - 1][1] / 1000) ** 3 / 12  # noqa: E731
    lu = p.alturas_piso_m[piso] - p.vigas_mm[piso][1] / 1000
    peor = 0.0
    for luces, nlin in ((p.luces_x_m, len(m.xs)), (p.luces_y_m, len(m.ys))):
        for i in range(nlin):
            vanos = [luces[i - 1]] if i > 0 else []
            vanos += [luces[i]] if i < len(luces) else []

            def psi(nv):                                            # nudo del nivel nv (1..n)
                sc = ec * ic(nv - 1) / p.alturas_piso_m[nv - 1] + (ec * ic(nv) / p.alturas_piso_m[nv] if nv < n else 0.0)
                sb = sum(ec * ib(nv) / L for L in vanos)
                return sc / sb if sb > 0 else 1e9
            psi_top = psi(piso + 1)
            psi_bot = 1.0 if piso == 0 else psi(piso)
            peor = max(peor, _k_jackson_moreland(psi_top, psi_bot) * lu)
    return peor


def _demanda_columnas(p, m: Modelo, F, C, es_e, res, piso: int, mat, sis: dict):
    """DemandaColumna del piso (ambos ejes concatenados) y las demandas por eje para la flexión biaxial."""
    cols = [k for k, t in enumerate(m.meta) if t[0] == "col" and t[1] == piso]
    sup = {(t[2], t[3]): k for k, t in enumerate(m.meta) if t[0] == "col" and t[1] == piso + 1}
    Fc = F[:, cols, :]                                               # (6, nc, 12)
    P = np.einsum("kc,cn->kn", C, Fc[:, :, 0])                       # (K, nc), compresión +
    Cg, Ce = C.copy(), C.copy()
    Cg[:, 2:N_CASOS_BASE] = 0.0                                     # gravedad: D, L y patrones de L
    Ce[:, :2], Ce[:, N_CASOS_BASE:] = 0.0, 0.0                       # sismo
    # Qi del entrepiso con los casos de diseño (C.10.10.7): Q = ΣPu·Δo / (Vus·lc)
    grav = 1.2 * Fc[0, :, 0].sum() + 1.0 * Fc[1, :, 0].sum()
    q = 0.0
    for c_idx, j in ((0, 0), (2, 1)):                                # Ex+e → ux, Ey+e → uy
        r = res[2 + c_idx]
        u_sup = r.maestros[f"P{piso + 1}"][j]
        u_inf = r.maestros[f"P{piso}"][j] if piso > 0 else 0.0
        e_kn = sis["x" if j == 0 else "y"]["E_kn"]
        vus = sum(e_kn[piso:])
        if vus > 0:
            q = max(q, grav * abs(u_sup - u_inf) / (vus * p.alturas_piso_m[piso]))
    if q > Q_MAX:
        return None, None, q
    ds = 1.0 / (1.0 - q) if q > _col.Q_SIN_AMPLIFICAR else 1.0
    ejes = {"x": ((5, 11), 1), "y": ((4, 10), 2)}                    # Mz (flexión por sismo en X), My (en Y); cortantes Vy, Vz
    dems, P_all, Mns_all, Ms_all = {}, [], [], []
    V = V_s = 0.0
    for eje, ((a, b), iv) in ejes.items():
        Mns = np.stack([np.einsum("kc,cn->kn", Cg, Fc[:, :, a]), np.einsum("kc,cn->kn", Cg, Fc[:, :, b])], axis=-1)
        Ms = np.stack([np.einsum("kc,cn->kn", Ce, Fc[:, :, a]), np.einsum("kc,cn->kn", Ce, Fc[:, :, b])], axis=-1)
        Vns, Vs = np.einsum("kc,cn->kn", Cg, Fc[:, :, iv]), np.einsum("kc,cn->kn", Ce, Fc[:, :, iv])
        V = max(V, float(np.abs(Vns + ds * Vs).max()))
        V_s = max(V_s, float(np.abs(ds * Vs).max()))
        P_all.append(P.ravel())
        Mns_all.append(Mns.reshape(-1, 2))
        Ms_all.append(Ms.reshape(-1, 2))
        dems[eje] = (P.ravel(), Mns.reshape(-1, 2), Ms.reshape(-1, 2))
    nudos = []
    Pe = P[es_e]
    for ic_, k in enumerate(cols):
        _, _, i, j = m.meta[k]
        arriba = sup.get((i, j))
        p_sup = None
        if arriba is not None:
            p_sup = np.einsum("kc,c->k", C[es_e], F[:, arriba, 0])
        nudos.append((0 < i < len(m.xs) - 1, Pe[:, ic_], p_sup))
        nudos.append((0 < j < len(m.ys) - 1, Pe[:, ic_], p_sup))
    gD, gL = float(np.abs(Fc[0, :, 0]).sum()), float(np.abs(Fc[1, :, 0]).sum())
    beta = 1.2 * gD / (1.2 * gD + 1.6 * gL) if gD + gL > 0 else 0.0
    lu = p.alturas_piso_m[piso] - p.vigas_mm[piso][1] / 1000
    base = dict(V=V, V_sismo=V_s, delta_s=ds, k_lu_max_m=_klu(p, m, piso), lu_min_m=lu, lu_max_m=lu, beta_dns=beta)
    dem = _col.DemandaColumna(P=np.concatenate(P_all), M_ns=np.concatenate(Mns_all), M_s=np.concatenate(Ms_all),
                              nudos=tuple(nudos), P_sismo=np.tile(Pe.ravel(), 2) if es_e.any() else None, **base)
    por_eje = {e: _col.DemandaColumna(P=v[0], M_ns=v[1], M_s=v[2], nudos=(), **base) for e, v in dems.items()}
    return dem, por_eje, q


def _biaxial(d, por_eje, mat, rec) -> float:
    """Máx de Mux/φMn(Pu) + Muy/φMn(Pu) (contorno lineal, sección simétrica) sobre combinaciones y columnas."""
    cv = _col.curva(d.h, d.b, d.n_cara, d.dia, d.estribo, rec, mat.fc, mat.fy)
    mx = _col.momentos_diseno(d.h, d.b, por_eje["x"], mat)
    my = _col.momentos_diseno(d.h, d.b, por_eje["y"], mat)
    if mx is None or my is None:
        return math.inf
    phi = _col.phi_mn_arr(cv, por_eje["x"].P)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (mx[0] + my[0]) / phi
    return float(np.nanmax(np.where(np.isnan(phi), np.inf, r)))


# ---------------------------------------------------------------------------------------------------- cadena
def disenar_edificio(p: ProyectoEdificio3D) -> InformeEdificio3D:
    m = construir_modelo(p)
    sis = analisis_sismico(p, m)
    der = _s3.analizar_fhe(m.portico, m.pisos, sis["x"]["Fs_deriva_kn"], sis["y"]["Fs_deriva_kn"], "general", True)
    inf = InformeEdificio3D(p, sis, {"uso_max": der["uso_max_limite"], "Qi_max": der["Qi_max"],
                                     "irregularidad_torsional": der["irregularidad_torsional"],
                                     "razon_torsional": der["razon_torsional_max"], "Ax": der["Ax"],
                                     "cumple": der["cumple_deriva"], "por_piso": _derivas_piso(der, m)})
    if not der["cumple_deriva"]:
        inf.fallas.append(f"Deriva: usa el {100 * der['uso_max_limite']:.0f} % del límite (A.6.4); aumente secciones")
    if der["Qi_max"] > _s3.Q_PDELTA:
        inf.advertencias.append(f"Qi máx = {der['Qi_max']:.3f} > 0,10: A.6.2.3 exige considerar P-Δ (HE6: ocurre en edificios altos con Aa ≤ 0,15)")
    F, res = _resolver_casos(p, m, sis, der["Ax"])
    nombres, C, es_e = combinaciones()
    pats = _patrones_viva(m)                                         # C.8.11.2
    F = np.concatenate([F, _resolver_patrones(m, pats)]) if pats else F
    nombres, C, es_e = _extender_combinaciones(nombres, C, es_e, pats)
    mat = _vg.Materiales(fc=p.fc_mpa, fy=p.fy_mpa, fyt=p.fy_mpa)
    rec = p.recubrimiento_mm
    n = len(p.alturas_piso_m)
    total = _cc.Cantidades(0.0, 0.0, 0.0)
    disenos_viga = {}
    for nivel in range(1, n + 1):
        b, h = p.vigas_mm[nivel - 1]
        c = p.columnas_mm[nivel - 1]
        dem, vigas = _demanda_vigas(p, m, F, C, nivel, pats)
        cand0 = _dv.disenar(b, h, dem, p.capacidad, mat, recubrimiento=rec, columna_c1=c, columna_c2=c)
        cand = []
        for d in cand0:                                              # C.9.5: el refuerzo cambia Icr, se filtra por candidato
            vd = _deflexiones(p, m, F, vigas, d, nivel, pats, mat)
            if all(v.cumple for v in vd):
                cand.append(dataclasses.replace(d, verificaciones=tuple(d.verificaciones) + tuple(vd)))
        fila = {"nivel": nivel, "b": b, "h": h, "n": len(vigas), "demanda": dataclasses.asdict(dem), "diseno": None}
        if not cand0:
            inf.fallas.append(f"Vigas del nivel {nivel} ({b:g}×{h:g} mm): ningún refuerzo cumple C.21 / C.10 / C.11")
        elif not cand:
            vd = _deflexiones(p, m, F, vigas, cand0[0], nivel, pats, mat)
            peor = max(vd, key=lambda v: v.demanda / v.capacidad)
            inf.fallas.append(f"Vigas del nivel {nivel} ({b:g}×{h:g} mm): deflexión {peor.demanda:.1f} mm > "
                              f"{peor.capacidad:.1f} mm (C.9.5); aumente la altura de la viga")
        else:
            qs = [(_cc.costo_co2(_cantidades_vigas(p, m, d, vigas, c), p.fc_mpa)[0], i) for i, d in enumerate(cand)]
            d = cand[min(qs)[1]]
            q = _cantidades_vigas(p, m, d, vigas, c)
            total = total + q
            disenos_viga[nivel] = d
            fila.update(diseno=d, cantidades=q)
        inf.vigas.append(fila)
    sup_curva = None
    for piso in range(n - 1, -1, -1):
        c = p.columnas_mm[piso]
        fila = {"piso": piso + 1, "c": c, "n": len(m.xs) * len(m.ys), "diseno": None}
        dem, por_eje, q = _demanda_columnas(p, m, F, C, es_e, res, piso, mat, sis)
        fila["Q"] = q
        if dem is None:
            inf.fallas.append(f"Columnas del piso {piso + 1}: Q = {q:.2f} > 1/3 (C.10.10.7): requiere análisis de segundo orden")
            inf.columnas.insert(0, fila)
            sup_curva = None
            continue
        dvg = disenos_viga.get(piso + 1)
        mnn, mnp = _mn_viga(dvg, mat, rec) if dvg else (0.0, 0.0)
        cand = _col.disenar_columna(c, c, dem, p.capacidad, mat, recubrimiento=rec, mnb_int=mnn + mnp,
                                    mnb_ext=max(mnn, mnp), cv_sup=sup_curva)
        ok = []
        for d in cand:
            rb = _biaxial(d, por_eje, mat, rec)
            if rb <= 1.0:
                qd = _cc.cantidades_columna(d, p.alturas_piso_m[piso], rec)
                ok.append((_cc.costo_co2(qd, p.fc_mpa)[0], rb, d))
        fila.update(demanda={"P_max_kn": float(dem.P.max()), "V_kn": dem.V, "delta_s": dem.delta_s,
                             "k_lu_m": dem.k_lu_max_m, "mnb_int": mnn + mnp, "mnb_ext": max(mnn, mnp)})
        if not ok:
            inf.fallas.append(f"Columnas del piso {piso + 1} ({c:g} mm): ningún refuerzo cumple flexo-compresión biaxial, "
                              f"columna fuerte–viga débil y C.21 ({len(cand)} cumplen uniaxial)")
            sup_curva = None
        else:
            _, rb, d = min(ok, key=lambda t: t[0])
            qd = _cc.cantidades_columna(d, p.alturas_piso_m[piso], rec)
            nq = fila["n"]
            total = total + _cc.Cantidades(qd.volumen_m3 * nq, qd.acero_kg * nq, qd.encofrado_m2 * nq)
            fila.update(diseno=d, biaxial=rb, cantidades=qd)
            sup_curva = _col.curva(d.h, d.b, d.n_cara, d.dia, d.estribo, rec, mat.fc, mat.fy)
        inf.columnas.insert(0, fila)
    cop, co2 = _cc.costo_co2(total, p.fc_mpa)
    area = m.xs[-1] * m.ys[-1] * n
    inf.cantidades = {"concreto_m3": total.volumen_m3, "acero_kg": total.acero_kg, "encofrado_m2": total.encofrado_m2,
                      "costo_cop": cop, "co2_kg": co2, "area_construida_m2": area}
    if sis["x"]["gobierna_CuTa"] or sis["y"]["gobierna_CuTa"]:
        inf.advertencias.append("El periodo del modelo supera Cu·Ta: la FHE usa el tope Cu·Ta (A.4.2.1; HE1 de #274: 97 % de los pórticos).")
    inf.memoria = memoria(inf, m, nombres)
    return inf


def _derivas_piso(der, m: Modelo) -> list[dict]:
    out = []
    for q in m.pisos:
        filas = [f for f in der["derivas"] if f["piso"] == q.diafragma]
        out.append({"piso": q.diafragma, "uso": max(f["uso_limite"] for f in filas), "Qi": max(f["Qi"] for f in filas),
                    "deriva_relativa": max(f["deriva_relativa"] for f in filas)})
    return out


# ---------------------------------------------------------------------------------------------------- memoria F0
def _verifs(vs) -> list:
    out = []
    for v in vs:
        dem, cap = float(v.demanda), float(v.capacidad)
        out.append(mc.Verificacion(nombre=v.nombre, demanda=dem if math.isfinite(dem) else 1e30,
                                   capacidad=cap if math.isfinite(cap) else 1e30, unidad=v.unidad, cumple=bool(v.cumple),
                                   referencia=v.norma, nota=v.nota))
    return out


def memoria(inf: InformeEdificio3D, m: Modelo, nombres_comb: list[str]):
    p, s, d = inf.proyecto, inf.sismo, inf.deriva
    L = mc.Linea
    n = len(p.alturas_piso_m)
    entrada = [
        L(concepto="Uso de la edificación / grupo de uso", valor=f"{p.uso} / {p.grupo_uso}", referencia="A.2.5.1", estado="ENTRADA"),
        L(concepto="Municipio (DIVIPOLA)", valor=p.divipola or "no declarado", estado="ENTRADA"),
        L(concepto="Aa / Av", valor=f"{p.aa:g} / {p.av:g}", referencia="A.2.3, Apéndice A-4", estado="ENTRADA"),
        L(concepto="Perfil de suelo", valor=p.perfil_suelo, referencia="A.2.4 (del estudio geotécnico)", estado="ENTRADA"),
        L(concepto="Fa / Fv", valor=f"{s['fa']:.3g} / {s['fv']:.3g}", referencia="Tablas A.2.4-3 y A.2.4-4", estado="NSR-10 (leído)"),
        L(concepto="Coeficiente de importancia I", valor=s["I"], referencia="Tabla A.2.5-1", estado="NSR-10 (leído)"),
        L(concepto="Sistema estructural / capacidad de disipación", valor=f"pórticos de concreto {p.capacidad}", referencia="Tabla A.3-3", estado="ENTRADA"),
        L(concepto="f'c / fy", valor=f"{p.fc_mpa:g} / {p.fy_mpa:g}", unidad="MPa", estado="ENTRADA"),
        L(concepto="Ec", valor=4700 * math.sqrt(p.fc_mpa), unidad="MPa", ecuacion="Ec = 4700·√f'c", referencia="C.8.5.1", estado="NSR-10 (leído)"),
        L(concepto="Planta", valor=f"luces X {list(p.luces_x_m)} m; luces Y {list(p.luces_y_m)} m", estado="ENTRADA"),
        L(concepto="Alturas de piso", valor=list(p.alturas_piso_m), unidad="m", estado="ENTRADA"),
        L(concepto="Columnas por piso (cuadradas)", valor=list(p.columnas_mm), unidad="mm", estado="ENTRADA"),
        L(concepto="Vigas por nivel (b×h)", valor=[f"{b:g}×{h:g}" for b, h in p.vigas_mm], unidad="mm", estado="ENTRADA"),
        L(concepto="Recubrimiento libre", valor=p.recubrimiento_mm, unidad="mm", referencia="C.7.7.1", estado="ENTRADA"),
    ]
    cargas = [
        L(concepto="Carga muerta sobre la losa (losa + acabados + muros)", valor=p.carga_muerta_kpa, unidad="kN/m²", referencia="B.3", estado="ENTRADA"),
        L(concepto="Carga viva", valor=p.carga_viva_kpa, unidad="kN/m²", referencia="Tabla B.4.2.1-1", estado="ENTRADA"),
        L(concepto="Peso propio de vigas y columnas", valor=GAMMA_CONCRETO, unidad="kN/m³", referencia="B.3", estado="HIPÓTESIS"),
        L(concepto="Reparto de la losa a las vigas", valor="líneas de rotura a 45°, uniforme equivalente con la misma resultante", estado="HIPÓTESIS"),
        L(concepto="Peso sísmico total W (D + peso propio)", valor=s["W_kn"], unidad="kN", referencia="A.4.2", estado="CALCULADO"),
        L(concepto="Combinaciones", valor=f"{len(nombres_comb)}: 1.4D; 1.2D+1.6L; 1.2D+1.0L±E; 0.9D±E", referencia="B.2.4.2", estado="NSR-10 (leído)"),
        L(concepto="Disposición de la carga viva",
          valor=f"{sum('[' in c and c.startswith('1.2D+1.6L[') for c in nombres_comb)} patrones (vanos alternados y adyacentes, "
                "por viga, alternando por nivel) en 1.2D+1.6L", referencia="C.8.11.1, C.8.11.2", estado="NSR-10 (leído)"),
        L(concepto="Deflexiones de servicio",
          valor=f"Ie (C.9-8), λΔ = ξ/(1+50ρ') con ξ = {XI_LARGO_PLAZO:g}; L sostenida = {PSI_SOSTENIDA:g}·L; "
                f"divisiones {'frágiles (ℓ/480)' if p.divisiones_fragiles else 'no frágiles (ℓ/240)'}",
          referencia="C.9.5.2, Tabla C.9.5(b)", estado="HIPÓTESIS"),
        L(concepto="Efectos ortogonales", valor="E = 100 % en una dirección + 30 % en la perpendicular", referencia="A.3.6.3", estado="NSR-10 (leído)"),
        L(concepto="Torsión accidental", valor="±5 % de la dimensión perpendicular, amplificada por Ax", referencia="A.3.6.7.1, A.3.6-2", estado="NSR-10 (leído)"),
    ]
    model = [
        L(concepto="Modelo", valor=f"pórtico 3D, {len(m.portico.nodos)} nodos, {len(m.portico.elementos)} elementos, diafragma rígido por nivel",
          referencia="A.3.6.7.2, A.5.2.1.1", estado="HIPÓTESIS"),
        L(concepto="Inercias fisuradas", valor="columnas 0,70·Ig; vigas 0,35·Ig", referencia="C.10.10.4.1", estado="NSR-10 (leído)"),
        L(concepto="Ta", valor=s["Ta_s"], unidad="s", ecuacion="Ta = Ct·h^α", referencia="A.4.2-3", estado="NSR-10 (leído)"),
        L(concepto="Cu·Ta", valor=s["CuTa_s"], unidad="s", ecuacion="Cu = 1,75 − 1,2·Av·Fv ≥ 1,2", referencia="A.4.2-2", estado="NSR-10 (leído)"),
    ]
    for dd in ("x", "y"):
        q = s[dd]
        model += [
            L(concepto=f"T modal dirección {dd.upper()}", valor=q["T_modelo_s"], unidad="s", referencia="A.4.2.1 (modal3d)", estado="CALCULADO"),
            L(concepto=f"T usado en {dd.upper()}", valor=q["T_s"], unidad="s", ecuacion="T = mín(T_modelo, Cu·Ta)", referencia="A.4.2.1", estado="NSR-10 (leído)"),
            L(concepto=f"Sa en {dd.upper()}", valor=q["Sa"], unidad="g", referencia="A.2.6-1", estado="NSR-10 (leído)"),
            L(concepto=f"Vs en {dd.upper()}", valor=q["Vs_kn"], unidad="kN", ecuacion="Vs = Sa·g·M", referencia="A.4.3-1", estado="CALCULADO"),
        ]
    model += [
        L(concepto="R", valor=s["R"], ecuacion="R = φa·φp·φr·R0 (φ = 1,0)", referencia="A.3.3-1, Tabla A.3-3", estado="NSR-10 (leído)"),
        L(concepto="Deriva máxima / límite", valor=d["uso_max"], ecuacion="0,7·Δ/hpi ≤ 1,0 %", referencia="A.6.4.1, A.6.4.1.1", estado="CALCULADO"),
        L(concepto="Irregularidad torsional", valor=f"{d['irregularidad_torsional']} (δmax/δprom = {d['razon_torsional']:.3f})", referencia="Tabla A.3-6", estado="CALCULADO"),
        L(concepto="Qi máximo", valor=d["Qi_max"], ecuacion="Qi = Pi·Δcm/(Vi·hpi)", referencia="A.6.2-2", estado="CALCULADO"),
    ]
    diseno = []
    for v in inf.vigas:
        if v["diseno"] is None:
            continue
        dv = v["diseno"]
        diseno.append(mc.ElementoDisenado(
            grupo=f"Vigas del nivel {v['nivel']}", tipo="viga", cantidad=v["n"], seccion=f"{v['b']:g}×{v['h']:g} mm",
            refuerzo={"superior": f"{dv.n_sup}#{dv.dia}", "inferior": f"{dv.n_inf}#{dv.dia}",
                      "estribos": f"#{dv.estribo_dia} c/{dv.s_conf:g} mm (confinamiento) y c/{dv.s_centro:g} mm (centro)"},
            verificaciones=_verifs(dv.verificaciones), demandas={k: float(x) for k, x in v["demanda"].items()}))
    for c in inf.columnas:
        if c["diseno"] is None:
            continue
        dc = c["diseno"]
        vs = _verifs(dc.verificaciones) + [mc.Verificacion(
            nombre="Flexión biaxial: Mux/φMn + Muy/φMn ≤ 1 (contorno lineal)", demanda=c["biaxial"], capacidad=1.0, unidad="-",
            cumple=c["biaxial"] <= 1.0, referencia="HIPÓTESIS (contorno de carga con α = 1, conservador)")]
        diseno.append(mc.ElementoDisenado(
            grupo=f"Columnas del piso {c['piso']}", tipo="columna", cantidad=c["n"], seccion=f"{c['c']:g}×{c['c']:g} mm",
            refuerzo={"longitudinal": f"{dc.n_barras}#{dc.dia} ({dc.n_cara} por cara)",
                      "estribos": f"#{dc.estribo} c/{dc.s_conf:g} mm en ℓo = {dc.lo_mm:g} mm y c/{dc.s_fuera:g} mm fuera"},
            verificaciones=vs, demandas={k: float(x) for k, x in c["demanda"].items()} | {"Q": float(c["Q"])}))
    q = inf.cantidades
    cant = mc.Cantidades(concreto_m3=q["concreto_m3"], acero_kg=q["acero_kg"], encofrado_m2=q["encofrado_m2"],
                         costo_cop=q["costo_cop"], co2_kg=q["co2_kg"], area_construida_m2=q["area_construida_m2"],
                         fuente_precios="motor-concreto.Economia (línea base 2026-11; solo vigas y columnas, costo directo)")
    resultados = {"cumple_deriva": bool(d["cumple"]), "deriva_por_piso": d["por_piso"],
                  "periodos_modales_s": s["periodos_modales_s"], "Vs_kn": {"x": s["x"]["Vs_kn"], "y": s["y"]["Vs_kn"]},
                  "fallas": list(inf.fallas)}
    caract = {"n_pisos": n, "n_vanos_x": len(p.luces_x_m), "n_vanos_y": len(p.luces_y_m),
              "luz_x_media_m": float(np.mean(p.luces_x_m)), "luz_y_media_m": float(np.mean(p.luces_y_m)),
              "altura_total_m": float(sum(p.alturas_piso_m)), "aa": p.aa, "av": p.av, "perfil": p.perfil_suelo,
              "grupo_uso": p.grupo_uso, "capacidad": p.capacidad, "fc_mpa": p.fc_mpa, "D_kpa": p.carga_muerta_kpa,
              "L_kpa": p.carga_viva_kpa, "columna_base_mm": p.columnas_mm[0], "viga_h_base_mm": p.vigas_mm[0][1],
              "T_modelo_x_s": s["x"]["T_modelo_s"], "T_x_s": s["x"]["T_s"], "Vs_W": s["x"]["Vs_kn"] / s["W_kn"],
              "uso_deriva": d["uso_max"], "Qi_max": d["Qi_max"], "cumple": inf.cumple}
    if q["area_construida_m2"] > 0:
        caract |= {"acero_kg_m2": q["acero_kg"] / q["area_construida_m2"], "concreto_m3_m2": q["concreto_m3"] / q["area_construida_m2"],
                   "costo_cop_m2": q["costo_cop"] / q["area_construida_m2"], "co2_kg_m2": q["co2_kg"] / q["area_construida_m2"]}
    return mc.MemoriaCalculo(
        motor=MOTOR, proyecto={"nombre": p.nombre, "tipologia": "porticos_concreto_3d", "uso": p.uso, "divipola": p.divipola,
                               "sistema": f"pórticos de concreto resistentes a momentos {p.capacidad}"},
        datos_entrada=entrada, cargas=cargas, modelacion=model, resultados_analisis=resultados, diseno=diseno, cantidades=cant,
        no_verifica=list(NO_VERIFICA), advertencias=list(inf.advertencias) + [f"NO CUMPLE: {f}" for f in inf.fallas],
        caracteristicas=caract)
