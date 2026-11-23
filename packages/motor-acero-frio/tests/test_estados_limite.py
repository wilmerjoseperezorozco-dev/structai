"""Pruebas de pandeo distorsional, lateral-torsional y cargas combinadas (#81).

Referencias independientes:
- propiedades de aleta + pestaña simple: formas cerradas del comentario de AISI S100 (Af, Iyf, Ixyf, xo, hx, yo, Jf,
  Cwf = 0) y el Ixf de la línea media derivado a mano, t(4bd³ + d⁴)/(12(b+d));
- Fd de F.4.3.4-21 a -24 y de F.4.3.3-37 a -43 evaluados con esas formas cerradas, sin pasar por propiedades_brutas;
- Cb de una viga simplemente apoyada con carga uniforme = 12,5/11 (valor clásico 1,14);
- Fe del pandeo lateral-torsional evaluado a mano con F.4.3.3-10, -14 y -15;
- interacciones de F.4.3.5 con números redondos.
Más monotonicidad, homogeneidad dimensional, continuidad de las curvas y sabotaje.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest

from src.combinada import coeficiente_cm, flexo_compresion_uniaxial, flexo_tension_uniaxial
from src.contrato_api import (
    PerfilC,
    compresion_perfil_c,
    flexion_perfil_c,
    flexocompresion_perfil_c,
    flexotension_perfil_c,
    verificar_viga_c,
)
from src.distorsional import (
    distorsional_compresion_c,
    distorsional_flexion_c,
    factor_beta,
    propiedades_aleta,
)
from src.flexion import (
    _estado,
    coeficiente_cb,
    modulo_efectivo_a_esfuerzo,
    resistencia_flexion_c,
    resistencia_ltb_c,
)
from src.seccion import GeometriaC

E, MU = 203000.0, 0.3
G = E / (2 * (1 + MU))
G9 = GeometriaC(229.0, 63.5, 19.0, 1.5)          # C con pestaña de proporciones comerciales (≈ 9CS2.5×059)


def _cerradas(g):
    """Formas cerradas de aleta + pestaña simple (AISI S100, comentario de C3.1.4), con la línea media."""
    b, d, t = g.bc, g.dc, g.t
    return dict(Af=(b + d) * t, Jf=(b + d) * t ** 3 / 3, Iyf=t * (b ** 4 + 4 * d * b ** 3) / (12 * (b + d)),
                Ixf=t * (4 * b * d ** 3 + d ** 4) / (12 * (b + d)), Ixyf=t * b * b * d * d / (4 * (b + d)),
                xo=b * b / (2 * (b + d)), hx=-(b * b + 2 * d * b) / (2 * (b + d)), yo=-d * d / (2 * (b + d)), Cwf=0.0)


# ── Propiedades de la aleta ───────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("g", [G9, GeometriaC(150, 50, 15, 1.5), GeometriaC(300, 90, 25, 2.5)])
def test_propiedades_aleta_igual_a_formas_cerradas(g):
    a, c = propiedades_aleta(g), _cerradas(g)
    for k in ("Af", "Jf", "Iyf", "Ixf", "Ixyf", "xo", "hx", "yo"):
        assert getattr(a, k) == pytest.approx(c[k], rel=1e-10), k
    assert abs(a.Cwf) < 1e-9 * c["Iyf"] * g.bc ** 2
    assert a.xo - a.hx == pytest.approx(g.bc, rel=1e-12)       # centro de cortante de la aleta en la esquina


def test_c_sin_pestana_no_tiene_pandeo_distorsional():
    with pytest.raises(ValueError, match="rigidizador de borde"):
        distorsional_flexion_c(GeometriaC(150, 50, 0, 1.5), 340, 1000)


# ── Fd evaluado a mano con las formas cerradas ────────────────────────────────────────────────────────────

def _fd_compresion_a_mano(g, Lm, kphi=0.0):
    c = _cerradas(g)
    t, ho, d = g.t, g.H, c["xo"] - c["hx"]
    T = c["Ixf"] * d * d + c["Cwf"] - c["Ixyf"] ** 2 / c["Iyf"] * d * d
    Lcr = (6 * math.pi ** 4 * ho * (1 - MU ** 2) / t ** 3 * T) ** 0.25
    L = min(Lcr, Lm)
    k = math.pi / L
    kfe = k ** 4 * E * T + k ** 2 * G * c["Jf"]
    kwe = E * t ** 3 / (6 * ho * (1 - MU ** 2))
    r = c["Ixyf"] / c["Iyf"]
    kfg = k ** 2 * (c["Af"] * (d * d * r * r - 2 * c["yo"] * d * r + c["hx"] ** 2 + c["yo"] ** 2) + c["Ixf"] + c["Iyf"])
    kwg = k ** 2 * t * ho ** 3 / 60
    beta = 1.0 if Lm >= Lcr else (Lm / Lcr) ** math.log(Lm / Lcr)
    return beta * (kfe + kwe + kphi) / (kfg + kwg), Lcr


@pytest.mark.parametrize("Lm", [300.0, 700.0, 2000.0])
def test_fd_compresion_a_mano(Lm):
    fd, lcr = _fd_compresion_a_mano(G9, Lm)
    r = distorsional_compresion_c(G9, 345, Lm, E=E, mu=MU)
    assert r.Fd == pytest.approx(fd, rel=1e-10)
    assert r.Lcr == pytest.approx(lcr, rel=1e-10)


def test_fd_flexion_a_mano_seccion_simetrica():
    """Sección simétrica: ξweb = 2 y F.4.3.3-43 se simplifica; Lcr con el término π⁴ho⁴/720 (F.4.3.3-39bis)."""
    g, c = G9, _cerradas(G9)
    t, ho, d = g.t, g.H, c["xo"] - c["hx"]
    T = c["Ixf"] * d * d - c["Ixyf"] ** 2 / c["Iyf"] * d * d
    Lcr = (6 * math.pi ** 4 * ho * (1 - MU ** 2) / t ** 3 * T + math.pi ** 4 * ho ** 4 / 720) ** 0.25
    k, R = math.pi / Lcr, Lcr / ho
    kfe = k ** 4 * E * T + k ** 2 * G * c["Jf"]
    kwe = E * t ** 3 / (12 * (1 - MU ** 2) * ho)
    r = c["Ixyf"] / c["Iyf"]
    kfg = k ** 2 * (c["Af"] * (d * d * r * r - 2 * c["yo"] * d * r + c["hx"] ** 2 + c["yo"] ** 2) + c["Ixf"] + c["Iyf"])
    kwg = ho * t * math.pi ** 2 / 13440 * ((-45360 + 62160) * R ** 2 + 448 * math.pi ** 2 + 50 * math.pi ** 4 / R ** 2) \
        / (math.pi ** 4 + 28 * math.pi ** 2 * R ** 2 + 420 * R ** 4)
    res = distorsional_flexion_c(g, 345, 5000.0, E=E, mu=MU)
    assert res.rigideces["xi_web"] == pytest.approx(2.0, rel=1e-12)
    assert res.Lcr == pytest.approx(Lcr, rel=1e-10)
    assert res.Fd == pytest.approx((kfe + kwe) / (kfg + kwg), rel=1e-10)


def test_kphi_fg_usa_hx_y_no_ho():
    """Errata del corpus en F.4.3.3-42 («ho²»): con hx², K̃φfg no depende de la altura del alma."""
    a1 = distorsional_compresion_c(GeometriaC(150, 63.5, 19, 1.5), 345, 600.0)
    a2 = distorsional_compresion_c(GeometriaC(300, 63.5, 19, 1.5), 345, 600.0)
    assert a1.rigideces["Kphi_fg"] == pytest.approx(a2.rigideces["Kphi_fg"], rel=1e-12)


# ── Propiedades físicas del distorsional ──────────────────────────────────────────────────────────────────

def test_beta_valores():
    assert factor_beta(2000, 1000) == 1.0
    assert factor_beta(500, 1000) == pytest.approx(math.exp(math.log(0.5) ** 2), rel=1e-12)


@pytest.mark.parametrize("fn", [distorsional_flexion_c, distorsional_compresion_c])
def test_distorsional_monotono(fn):
    lms = [200.0, 400.0, 700.0, 1500.0, 4000.0]
    nominales = [fn(G9, 345, lm).nominal for lm in lms]
    assert all(a >= b - 1e-9 for a, b in zip(nominales, nominales[1:]))      # menos restricciones, menos resistencia
    assert fn(G9, 345, 4000.0).nominal == pytest.approx(fn(G9, 345, 9000.0).nominal, rel=1e-12)   # Lm ≥ Lcr
    fds = [fn(G9, 345, 4000.0, kphi=k).Fd for k in (0.0, 50.0, 500.0)]
    assert fds[0] < fds[1] < fds[2]                                           # la restricción rotacional ayuda
    assert all(fn(G9, 345, lm).nominal <= fn(G9, 345, lm).fluencia + 1e-6 for lm in lms)


def test_distorsional_homogeneidad_dimensional():
    g2 = GeometriaC(2 * 229.0, 2 * 63.5, 2 * 19.0, 2 * 1.5)
    f1, f2 = distorsional_flexion_c(G9, 345, 1000.0), distorsional_flexion_c(g2, 345, 2000.0)
    assert f2.Fd == pytest.approx(f1.Fd, rel=1e-10)
    assert f2.nominal == pytest.approx(8 * f1.nominal, rel=1e-10)
    c1, c2 = distorsional_compresion_c(G9, 345, 1000.0), distorsional_compresion_c(g2, 345, 2000.0)
    assert c2.nominal == pytest.approx(4 * c1.nominal, rel=1e-10)


def test_curvas_distorsionales_continuas():
    """F.4.3.3-29 en λd = 0,673 y F.4.3.4-13 en λd = 0,561 devuelven la fluencia (a menos de 0,03 %)."""
    q = 1 / 0.673
    assert (1 - 0.22 * q) * q == pytest.approx(1.0, abs=3e-4)
    q = (1 / 0.561 ** 2) ** 0.6
    assert (1 - 0.25 * q) * q == pytest.approx(1.0, abs=3e-4)


@pytest.mark.parametrize("Lm, kphi", [(0.0, 0.0), (-1.0, 0.0), (1000.0, -5.0), (math.inf, 0.0)])
def test_distorsional_entradas_invalidas(Lm, kphi):
    with pytest.raises(ValueError):
        distorsional_compresion_c(G9, 345, Lm, kphi)


# ── Pandeo lateral-torsional ──────────────────────────────────────────────────────────────────────────────

def test_cb_valores_clasicos():
    assert coeficiente_cb(1.0, 1.0, 1.0, 1.0) == pytest.approx(1.0)
    assert coeficiente_cb(1.0, 0.75, 1.0, 0.75) == pytest.approx(12.5 / 11, rel=1e-12)    # carga uniforme
    with pytest.raises(ValueError):
        coeficiente_cb(1.0, 2.0, 0.5, 0.5)


def test_fe_ltb_a_mano():
    g, L = G9, 3000.0
    p = g.propiedades()
    sey = math.pi ** 2 * E / (L / p.ry) ** 2
    st = (G * p.J + math.pi ** 2 * E * p.Cw / L ** 2) / (p.A * p.ro ** 2)
    Sf = p.Ix / (g.hc + g.t / 2 - p.yc)
    r = resistencia_ltb_c(g, 345, L, L, 1.3)
    assert r.Fe == pytest.approx(1.3 * p.ro * p.A * math.sqrt(sey * st) / Sf, rel=1e-12)


def test_ltb_rangos_y_limites():
    sec = resistencia_flexion_c(G9, 345)
    corta = resistencia_ltb_c(G9, 345, 500, 500, 1.0)
    assert corta.rango == "sin_ltb" and corta.Mn == pytest.approx(sec.Mn, rel=1e-12)
    assert corta.phi_b == sec.phi_b == 0.95      # regresión: sin LTB no se castiga con φb = 0,90
    larga = resistencia_ltb_c(G9, 345, 8000, 8000, 1.0)
    assert larga.rango == "elastico" and larga.Fc == pytest.approx(larga.Fe)
    # Con Fc bajo la sección es totalmente efectiva: Sc es el módulo bruto (referencia independiente del solucionador).
    assert larga.Sc == pytest.approx(larga.Sf, rel=1e-9)
    # F.4.3.3-8 empalma con F.4.3.3-9 en Fe = 0,56·Fy.
    Fy = 345.0
    assert (10 / 9) * Fy * (1 - 10 * Fy / (36 * 0.56 * Fy)) == pytest.approx(0.56 * Fy, rel=1e-3)


def test_ltb_monotono():
    Ls = [800.0, 1500.0, 2200.0, 3000.0, 5000.0]
    mns = [resistencia_ltb_c(G9, 345, L, L, 1.0).Mn for L in Ls]
    assert all(a >= b for a, b in zip(mns, mns[1:]))
    assert resistencia_ltb_c(G9, 345, 3000, 3000, 1.3).Mn > mns[3]
    assert max(mns) <= resistencia_flexion_c(G9, 345).Mn + 1e-6


def test_sc_brentq_igual_a_sustitucion_sucesiva():
    g, fc = G9, 291.7
    sc = modulo_efectivo_a_esfuerzo(g, fc)
    y = g.hc / 2
    for _ in range(2000):
        y_n = _estado(g, y, fc, E, MU, fc)[0]
        if abs(y_n - y) < 1e-11:
            break
        y = y_n
    _, Ix, _, d_comp, *_ = _estado(g, y, fc, E, MU, fc)
    assert sc == pytest.approx(Ix / d_comp, rel=1e-7)


@pytest.mark.parametrize("Cb", [0.9, 5.5, math.nan])
def test_cb_fuera_de_rango_falla(Cb):
    with pytest.raises(ValueError, match="Cb"):
        resistencia_ltb_c(G9, 345, 2000, 2000, Cb)


# ── Contrato: el menor de los estados límite ──────────────────────────────────────────────────────────────

def _perfil9(**kw):
    base = dict(H_mm=229.0, B_mm=63.5, D_mm=19.0, t_mm=1.5, Fy_MPa=345.0, Fu_MPa=450.0)
    base.update(kw)
    return PerfilC(**base)


def test_flexion_gobierna_el_minimo():
    r = flexion_perfil_c(_perfil9(), Lm_mm=3000.0, KyLy_mm=3000.0, KtLt_mm=3000.0, Cb=1.0,
                         aleta_comprimida_arriostrada=False)
    estados = r.valor["estados_limite"]
    assert set(estados) == {"seccion", "lateral_torsional", "distorsional"}
    assert r.valor["phi_Mn_kNm"] == pytest.approx(min(e["phi_Mn_kNm"] for e in estados.values()))
    assert r.valor["gobierna"] == min(estados, key=lambda k: estados[k]["phi_Mn_kNm"])


def test_viga_corta_no_la_gobierna_el_lateral_torsional():
    r = flexion_perfil_c(_perfil9(), Lm_mm=300.0, KyLy_mm=300.0, KtLt_mm=300.0, Cb=1.0,
                         aleta_comprimida_arriostrada=False)
    e = r.valor["estados_limite"]
    assert e["lateral_torsional"]["phi_Mn_kNm"] == pytest.approx(e["seccion"]["phi_Mn_kNm"], rel=1e-12)


def test_flexion_exige_lm_en_c_con_pestana_y_lo_rechaza_sin_pestana():
    with pytest.raises(ValueError, match="Lm"):
        flexion_perfil_c(_perfil9(), aleta_comprimida_arriostrada=True)
    sin = _perfil9(D_mm=0.0)
    assert "distorsional" not in flexion_perfil_c(sin, aleta_comprimida_arriostrada=True).valor["estados_limite"]
    with pytest.raises(ValueError, match="no aplica"):
        flexion_perfil_c(sin, Lm_mm=1000.0, aleta_comprimida_arriostrada=True)


def test_compresion_gobierna_el_minimo():
    r = compresion_perfil_c(_perfil9(), 3000.0, 1000.0, 1000.0, Lm_mm=1000.0)
    e = r.valor["estados_limite"]
    assert r.valor["phi_Pn_kN"] == pytest.approx(min(x["phi_Pn_kN"] for x in e.values()))


def test_interaccion_usa_mnxo_de_la_seccion():
    """F.4.3.3-54 usa Mnxo (resistencia de la sección), no el Mn reducido por pandeo lateral-torsional."""
    pf = _perfil9()
    r = verificar_viga_c(pf, 3.0, 5.0, Lm_mm=3000.0, KyLy_mm=3000.0, KtLt_mm=3000.0, Cb=1.0,
                         aleta_comprimida_arriostrada=False)
    f = flexion_perfil_c(pf, Lm_mm=3000.0, KyLy_mm=3000.0, KtLt_mm=3000.0, Cb=1.0, aleta_comprimida_arriostrada=False)
    pmxo = f.valor["estados_limite"]["seccion"]["phi_Mn_kNm"]
    pv = r.valor["phi_Vn_kN"]
    assert r.valor["razones"]["interaccion"] == pytest.approx(math.hypot(3.0 / pmxo, 5.0 / pv), rel=1e-12)
    assert r.valor["razones"]["flexion"] == pytest.approx(3.0 / f.valor["phi_Mn_kNm"], rel=1e-12)


# ── Cargas combinadas (F.4.3.5) ───────────────────────────────────────────────────────────────────────────

def test_cm_valores():
    assert coeficiente_cm(None, traslacion_nudos=True) == 0.85
    assert coeficiente_cm(0.5, traslacion_nudos=False) == pytest.approx(0.4)
    assert coeficiente_cm(-1.0, traslacion_nudos=False) == pytest.approx(1.0)
    assert coeficiente_cm(None, traslacion_nudos=False, carga_transversal="extremos_libres") == 1.0
    with pytest.raises(ValueError):
        coeficiente_cm(1.5, traslacion_nudos=False)


def test_flexo_compresion_a_mano():
    # P̄/φcPn = 0,4 > 0,15 → F.4.3.5-4 y -5.  αx = 1 − 40/400 = 0,9.
    r = flexo_compresion_uniaxial(40.0, 30.0, 100.0, 120.0, 100.0, 400.0, 0.85)
    assert r.ecuaciones["F.4.3.5-4"] == pytest.approx(0.4 + 0.85 * 0.3 / 0.9, rel=1e-12)
    assert r.ecuaciones["F.4.3.5-5"] == pytest.approx(40 / 120 + 0.3, rel=1e-12)
    assert r.razon == pytest.approx(max(r.ecuaciones.values()))
    # P̄/φcPn = 0,1 ≤ 0,15 → solo F.4.3.5-6.
    r6 = flexo_compresion_uniaxial(10.0, 30.0, 100.0, 120.0, 100.0, 400.0, 0.85)
    assert set(r6.ecuaciones) == {"F.4.3.5-6"} and r6.razon == pytest.approx(0.4)
    with pytest.raises(ValueError, match="Euler"):
        flexo_compresion_uniaxial(500.0, 30.0, 1000.0, 1000.0, 100.0, 400.0, 0.85)


def test_flexo_tension_a_mano():
    r = flexo_tension_uniaxial(30.0, 50.0, 100.0, 100.0, 125.0)
    assert r.ecuaciones["F.4.3.5-1"] == pytest.approx(0.4 + 0.3)
    assert r.ecuaciones["F.4.3.5-2"] == pytest.approx(0.5 - 0.3)


def test_flexocompresion_sin_axial_es_la_flexion():
    pf = _perfil9()
    kw = dict(aleta_comprimida_arriostrada=False, Cb=1.0, Lm_mm=1500.0)
    r = flexocompresion_perfil_c(pf, 0.0, 3.0, 3000.0, 1500.0, 1500.0, 0.85, **kw)
    f = flexion_perfil_c(pf, Lm_mm=1500.0, KyLy_mm=1500.0, KtLt_mm=1500.0, Cb=1.0, aleta_comprimida_arriostrada=False)
    assert r.valor["razon"] == pytest.approx(3.0 / f.valor["phi_Mn_kNm"], rel=1e-12)
    mas = flexocompresion_perfil_c(pf, 30.0, 3.0, 3000.0, 1500.0, 1500.0, 0.85, **kw)
    assert mas.valor["razon"] > r.valor["razon"]


def test_flexotension_incluye_tension_sola():
    pf = _perfil9()
    r = flexotension_perfil_c(pf, 100.0, 0.0, 200.0, aleta_comprimida_arriostrada=True, Lm_mm=1000.0)
    assert r.valor["gobierna"] == "tension_F.4.3.2"          # An pequeña: gobierna la rotura en la sección neta
    assert r.valor["cumple"] is (r.valor["razon"] <= 1.0)


# ── Contraste con un ejemplo publicado ────────────────────────────────────────────────────────────────────

def test_contraste_guia_dsm_aisi_9cs25x059():
    """AISI, Direct Strength Method Design Guide (Schafer), §8.1: 9CS2.5×059, Fy = 55 ksi, My = 126,55 kip·in y
    Mcrd ≈ 0,85·My por franjas finitas (análisis racional, F.4.3.3.1.4(c)).

    - My: el método lineal con esquinas rectas da +3,8 %, porque la guía modela los radios de doblez. Se acepta ±5 %.
    - Distorsional: el método (b) con la kφwe del corpus debe quedar del lado seguro frente al análisis racional."""
    i, ksi = 25.4, 6.894757
    g, Fy = GeometriaC(9 * i, 2.5 * i, 0.773 * i, 0.059 * i), 55 * ksi
    r = distorsional_flexion_c(g, Fy, 1e5)
    my_kip_in = r.fluencia / (4448.222 * 25.4)
    assert my_kip_in == pytest.approx(126.55, rel=0.05)
    assert r.critico / r.fluencia < 0.85
