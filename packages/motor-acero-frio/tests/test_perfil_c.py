"""Pruebas del perfil C (#81): referencias independientes, propiedades físicas y sabotaje.

Referencias independientes (no llaman al código bajo prueba para obtener el valor esperado):
- canal sin pestaña: centroide, centro de cortante e = 3b²/(h+6b) y Cw = t·b³·h²/12·(3b+2h)/(6b+h) (solución cerrada);
- propiedades brutas por integración numérica de la línea media (otro algoritmo);
- sección efectiva calculada a mano en un caso donde solo se reduce la aleta comprimida;
- cortante, tensión y compresión con las ecuaciones de F.4.3 evaluadas a mano.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import numpy as np
import pytest
from pydantic import ValidationError

from src.ancho_efectivo import E_ACERO_MPA
from src.contrato_api import (
    PerfilC,
    compresion_perfil_c,
    cortante_perfil_c,
    flexion_perfil_c,
    propiedades_perfil_c,
    tension_perfil_c,
    verificar_viga_c,
)
from src.flexion import interaccion_flexion_cortante, resistencia_flexion_c
from src.miembros import (
    coeficiente_kv,
    esfuerzo_nominal_compresion,
    fe_flexo_torsional,
    resistencia_compresion_c,
    resistencia_cortante,
    resistencia_tension,
)
from src.seccion import GeometriaC, propiedades_brutas

E, MU = 203000.0, 0.3
C0 = math.pi ** 2 * E / (12 * (1 - MU ** 2))


def _perfil(**kw):
    base = dict(H_mm=150.0, B_mm=50.0, D_mm=15.0, t_mm=1.5, Fy_MPa=340.0, Fu_MPa=450.0)
    base.update(kw)
    return PerfilC(**base)


# ── Módulo de elasticidad de F.4 ──────────────────────────────────────────────────────────────────────────

def test_modulo_elasticidad_es_el_de_f4():
    """F.4.4.6.1.3 fija E = 203 000 MPa para acero formado en frío (el MVP usaba 200 000)."""
    assert E_ACERO_MPA == 203000.0


# ── Propiedades brutas ────────────────────────────────────────────────────────────────────────────────────

def test_canal_solucion_cerrada():
    h, b, t = 200.0, 80.0, 2.0
    p = propiedades_brutas([(b, 0), (0, 0), (0, h), (b, h)], t)
    assert p.xc == pytest.approx(b * b / (h + 2 * b), rel=1e-12)
    assert p.xs == pytest.approx(-3 * b * b / (h + 6 * b), rel=1e-12)      # al lado opuesto de las aletas
    assert p.Cw == pytest.approx(t * b ** 3 * h ** 2 / 12 * (3 * b + 2 * h) / (6 * b + h), rel=1e-12)
    assert p.J == pytest.approx((2 * b + h) * t ** 3 / 3, rel=1e-12)
    assert p.Ix == pytest.approx(t * h ** 3 / 12 + 2 * b * t * (h / 2) ** 2, rel=1e-12)


def test_propiedades_brutas_contra_integracion_numerica():
    g = GeometriaC(203.2, 63.5, 15.9, 1.52)
    p = g.propiedades()
    nodos = np.array(g.nodos())
    xs, ys, ls = [], [], []
    for (x1, y1), (x2, y2) in zip(nodos[:-1], nodos[1:]):
        n = 4000
        s = (np.arange(n) + 0.5) / n
        xs.append(x1 + s * (x2 - x1)); ys.append(y1 + s * (y2 - y1))
        ls.append(np.full(n, math.hypot(x2 - x1, y2 - y1) / n))
    x, y, dl = np.concatenate(xs), np.concatenate(ys), np.concatenate(ls)
    dA = dl * g.t
    A = dA.sum(); xc = (x * dA).sum() / A; yc = (y * dA).sum() / A
    assert p.A == pytest.approx(A, rel=1e-9)
    assert p.xc == pytest.approx(xc, rel=1e-9)
    assert p.yc == pytest.approx(yc, rel=1e-9)
    assert p.Ix == pytest.approx(((y - yc) ** 2 * dA).sum(), rel=1e-6)
    assert p.Iy == pytest.approx(((x - xc) ** 2 * dA).sum(), rel=1e-6)
    assert p.Ixy == pytest.approx(0.0, abs=1e-6 * p.Ix)                      # simetría


# ── Flexión ───────────────────────────────────────────────────────────────────────────────────────────────

def test_seccion_compacta_totalmente_efectiva_se_igual_sx():
    g = GeometriaC(100, 40, 12, 2.0)
    r = resistencia_flexion_c(g, 340, aleta_comprimida_arriostrada=True)
    assert r.Se == pytest.approx(r.Sx_bruto, rel=1e-9)
    assert r.y_eje_neutro == pytest.approx(g.hc / 2, rel=1e-9)


def test_se_calculado_a_mano_solo_se_reduce_la_aleta():
    """H=100, B=80, D=22, t=1.6, Fy=250. Is ≥ Ia ⇒ R1 = 1; alma y pestaña totalmente efectivas (se verifica)."""
    H, B, D, t, Fy = 100.0, 80.0, 22.0, 1.6, 250.0
    g = GeometriaC(H, B, D, t)
    r = resistencia_flexion_c(g, Fy, aleta_comprimida_arriostrada=True, E=E, mu=MU)
    assert r.anchos["alma"]["totalmente_efectiva"]
    assert r.anchos["pestana_comprimida"]["ds"] == pytest.approx(D - t, rel=1e-12)
    assert r.anchos["aleta_comprimida"]["R1"] == 1.0

    # A mano: F.4.2.4 con f = Fy, w = B − 2t, D/w entre 0,25 y 0,80, R1 = 1
    w = B - 2 * t
    S = 1.28 * math.sqrt(E / Fy)
    assert w / t > 0.328 * S
    k = (4.82 - 5 * D / w) + 0.43
    lam = math.sqrt(Fy / (k * C0 / (w / t) ** 2))
    b = (1 - 0.22 / lam) / lam * w
    hueco = w - b
    hc, bc, dc = H - t, B - t, D - t / 2
    # tramos de línea media: (longitud, y del centroide, inercia propia respecto a su centroide)
    tramos = [(bc, 0.0, 0.0), (dc, dc / 2, dc ** 3 / 12), (hc, hc / 2, hc ** 3 / 12),
              (bc - hueco, hc, 0.0), (dc, hc - dc / 2, dc ** 3 / 12)]
    A = sum(l for l, _, _ in tramos) * t
    ycg = sum(l * y for l, y, _ in tramos) * t / A
    Ix = sum((i + l * (y - ycg) ** 2) * t for l, y, i in tramos)
    Se = Ix / (hc + t / 2 - ycg)
    assert r.fibra_que_fluye == "compresion"
    assert r.y_eje_neutro == pytest.approx(ycg, rel=1e-7)
    assert r.Se == pytest.approx(Se, rel=1e-7)
    assert r.Mn == pytest.approx(Se * Fy, rel=1e-7)


def test_se_sobre_sx_no_crece_con_fy():
    g = GeometriaC(203.2, 63.5, 15.9, 1.52)
    razones = [resistencia_flexion_c(g, fy, aleta_comprimida_arriostrada=True).Se / g.propiedades().Ix for fy in
               (200, 250, 300, 345, 400, 450)]
    assert all(a >= b - 1e-12 for a, b in zip(razones, razones[1:]))


def test_mn_crece_con_el_espesor():
    mns = [resistencia_flexion_c(GeometriaC(150, 50, 15, t), 340, aleta_comprimida_arriostrada=True).Mn
           for t in (1.0, 1.2, 1.5, 1.9, 2.5)]
    assert all(a < b for a, b in zip(mns, mns[1:]))


def test_homogeneidad_dimensional():
    """Escalar todas las longitudes por 2 deja las esbelteces iguales: Se × 8, Pn × 4 (con KL × 2)."""
    g1, g2 = GeometriaC(150, 50, 15, 1.5), GeometriaC(300, 100, 30, 3.0)
    s1 = resistencia_flexion_c(g1, 340, aleta_comprimida_arriostrada=True).Se
    s2 = resistencia_flexion_c(g2, 340, aleta_comprimida_arriostrada=True).Se
    assert s2 == pytest.approx(8 * s1, rel=1e-7)
    p1 = resistencia_compresion_c(g1, 340, 3000, 1000, 1000).Pn
    p2 = resistencia_compresion_c(g2, 340, 6000, 2000, 2000).Pn
    assert p2 == pytest.approx(4 * p1, rel=1e-9)


def test_c_sin_pestana_usa_phi_090_y_aleta_no_rigidizada():
    r = resistencia_flexion_c(GeometriaC(150, 50, 0, 1.5), 340, aleta_comprimida_arriostrada=True)
    assert r.phi_b == 0.90
    assert "b" in r.anchos["aleta_comprimida"]


def test_sin_arriostramiento_falla_explicito():
    with pytest.raises(ValueError, match="lateral-torsional"):
        resistencia_flexion_c(GeometriaC(150, 50, 15, 1.5), 340, aleta_comprimida_arriostrada=False)


def test_interaccion_flexion_cortante_a_mano():
    assert interaccion_flexion_cortante(3.0, 4.0, 5.0, 5.0) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        interaccion_flexion_cortante(1.0, 1.0, 0.0, 5.0)


# ── Cortante ──────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("h, rango", [(40.0, "fluencia"), (110.0, "pandeo_inelastico"), (180.0, "pandeo_elastico")])
def test_cortante_tres_rangos_a_mano(h, rango):
    t, Fy, kv = 1.5, 340.0, 5.34
    esb, lim = h / t, math.sqrt(E * kv / Fy)
    if esb <= lim:
        Fv = 0.6 * Fy
    elif esb <= 1.51 * lim:
        Fv = 0.6 * math.sqrt(E * kv * Fy) / esb
    else:
        Fv = 0.904 * E * kv / esb ** 2                     # forma F.4.3.3-47b
    r = resistencia_cortante(h, t, Fy, kv, E, MU)
    assert r.rango == rango
    assert r.Vn == pytest.approx(h * t * Fv, rel=5e-4)     # 0,904 es el redondeo de π²/(12·0,91) = 0,9038


def test_cortante_en_las_fronteras():
    """Continuo en √(E·kv/Fy). En 1,51·√(E·kv/Fy) la propia norma salta 0,24 %: 0,6/1,51 = 0,3974 frente a
    0,904/1,51² = 0,3965 (en Fy). Se documenta el salto y el contrato lo marca como borde de dominio."""
    t, Fy, kv = 1.0, 340.0, 5.34
    lim = math.sqrt(E * kv / Fy)
    a = resistencia_cortante(lim * (1 - 1e-9), t, Fy, kv, E, MU).Fv
    b = resistencia_cortante(lim * (1 + 1e-9), t, Fy, kv, E, MU).Fv
    assert a == pytest.approx(b, rel=1e-6)
    a = resistencia_cortante(1.51 * lim * (1 - 1e-9), t, Fy, kv, E, MU).Fv
    b = resistencia_cortante(1.51 * lim * (1 + 1e-9), t, Fy, kv, E, MU).Fv
    assert a / Fy == pytest.approx(0.6 / 1.51, rel=1e-6)
    assert b / Fy == pytest.approx(math.pi ** 2 / (12 * (1 - MU ** 2)) / 1.51 ** 2, rel=1e-6)
    h_borde = 1.51 * lim * 1.5
    perfil = _perfil(H_mm=h_borde + 3.0, t_mm=1.5)
    assert cortante_perfil_c(perfil).en_borde_dominio is True


def test_kv_con_rigidizadores():
    assert coeficiente_kv(None) == 5.34
    assert coeficiente_kv(0.5) == pytest.approx(4.00 + 5.34 / 0.25)
    assert coeficiente_kv(2.0) == pytest.approx(5.34 + 4.00 / 4.0)


# ── Tensión ───────────────────────────────────────────────────────────────────────────────────────────────

def test_tension_gobierna_el_menor():
    r = resistencia_tension(Ag=400.0, An=300.0, Fy=340.0, Fu=450.0)
    assert r.phi_Tn == pytest.approx(min(0.9 * 400 * 340, 0.75 * 300 * 450))
    assert r.gobierna == "rotura_seccion_neta"
    with pytest.raises(ValueError):
        resistencia_tension(Ag=400.0, An=500.0, Fy=340.0, Fu=450.0)


# ── Compresión ────────────────────────────────────────────────────────────────────────────────────────────

def test_fn_a_mano_y_continuidad_en_lambda_15():
    Fn, lam = esfuerzo_nominal_compresion(340.0, 340.0)          # λc = 1
    assert lam == 1.0 and Fn == pytest.approx(0.658 * 340.0)
    Fn2, _ = esfuerzo_nominal_compresion(340.0, 340.0 / 4)       # λc = 2
    assert Fn2 == pytest.approx(0.877 / 4 * 340.0)
    a, _ = esfuerzo_nominal_compresion(340.0, 340.0 / 1.5 ** 2 * (1 + 1e-9))
    b, _ = esfuerzo_nominal_compresion(340.0, 340.0 / 1.5 ** 2 * (1 - 1e-9))
    assert a == pytest.approx(b, rel=1e-3)


def test_flexo_torsional_sin_excentricidad_es_el_minimo():
    assert fe_flexo_torsional(500.0, 300.0, 0.0, 50.0) == pytest.approx(300.0)
    assert fe_flexo_torsional(200.0, 300.0, 0.0, 50.0) == pytest.approx(200.0)
    assert fe_flexo_torsional(500.0, 300.0, 30.0, 50.0) < 300.0   # el acople baja Fe


def test_pandeo_eje_debil_a_mano():
    g = GeometriaC(150, 50, 15, 1.5)
    p = g.propiedades()
    r = resistencia_compresion_c(g, 340, 500, 4000, 500)          # eje débil muy esbelto: gobierna flexión
    assert r.modo == "flexion_eje_debil"
    assert r.Fe == pytest.approx(math.pi ** 2 * E / (4000 / p.ry) ** 2, rel=1e-12)
    assert r.Ae <= r.A


# ── Contrato y sabotaje ───────────────────────────────────────────────────────────────────────────────────

def test_contrato_resultado_motor():
    perfil = _perfil()
    for res in (propiedades_perfil_c(perfil), flexion_perfil_c(perfil, aleta_comprimida_arriostrada=True),
                cortante_perfil_c(perfil), tension_perfil_c(perfil, An_mm2=350.0),
                compresion_perfil_c(perfil, 3000, 1000, 1000),
                verificar_viga_c(perfil, 2.0, 5.0, aleta_comprimida_arriostrada=True)):
        assert res.referencia_normativa.startswith("NSR-10")
        assert res.aviso_responsabilidad_profesional
        assert isinstance(res.en_borde_dominio, bool)
    assert any("distorsional" in a for a in flexion_perfil_c(perfil, aleta_comprimida_arriostrada=True).advertencias)


def test_verificar_viga_cumple_y_no_cumple():
    perfil = _perfil()
    ok = verificar_viga_c(perfil, 1.0, 2.0, aleta_comprimida_arriostrada=True)
    assert ok.valor["cumple"] is True
    malo = verificar_viga_c(perfil, 50.0, 2.0, aleta_comprimida_arriostrada=True)
    assert malo.valor["cumple"] is False and malo.valor["gobierna"] in ("flexion", "interaccion")


def test_en_borde_cerca_del_limite_de_aleta():
    perfil = _perfil(B_mm=1.5 * 58 + 3.0)                         # w/t = 58 ≥ 0,95·60
    assert propiedades_perfil_c(perfil).en_borde_dominio is True


@pytest.mark.parametrize("kw, patron", [
    (dict(B_mm=100.0), "w/t"),                                   # w/t > 60
    (dict(D_mm=45.0), "Tabla F.4.2.4-1"),                         # D/w ≥ 0,80
    (dict(H_mm=400.0), "h/t"),                                    # h/t > 200
])
def test_fuera_de_dominio_falla(kw, patron):
    with pytest.raises(ValueError, match=patron):
        flexion_perfil_c(_perfil(**kw), aleta_comprimida_arriostrada=True)


def test_entradas_invalidas():
    with pytest.raises(ValidationError):
        _perfil(Fu_MPa=300.0)                                     # Fu < Fy
    with pytest.raises(ValidationError):
        _perfil(t_mm=-1.0)
    with pytest.raises(ValidationError):
        PerfilC(H_mm=150.0, B_mm=50.0, D_mm=15.0, t_mm=1.5, Fy_MPa=340.0, Fu_MPa=450.0, zona="x")
    with pytest.raises((ValidationError, ValueError)):
        _perfil(D_mm=1.0)                                         # pestaña sin ancho plano


@pytest.mark.parametrize("dims, fy", [((203.2, 63.5, 15.9, 1.52), 345.0), ((250, 65, 20, 1.5), 450.0),
                                      ((300, 75, 20, 1.6), 340.0)])
def test_eje_neutro_brentq_igual_a_sustitucion_sucesiva(dims, fy):
    """Revisión adversaria: el punto fijo de la sección efectiva (con hueco en el alma y R1 < 1) se recalcula con
    otro algoritmo, sustitución sucesiva, y debe coincidir."""
    from src import flexion as fx
    g = GeometriaC(*dims)
    r = resistencia_flexion_c(g, fy, aleta_comprimida_arriostrada=True)
    y = g.hc / 2
    for _ in range(1000):
        y_nuevo = fx._estado(g, y, fy, E_ACERO_MPA, MU)[0]
        if abs(y_nuevo - y) < 1e-11:
            break
        y = y_nuevo
    assert r.y_eje_neutro == pytest.approx(y, abs=1e-6)
    assert r.Se < r.Sx_bruto
