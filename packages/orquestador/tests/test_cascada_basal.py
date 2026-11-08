import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_portico as dp
from src import grilla_vectorizada as gv
from src import sismo_portico as sp

BASE = dict(luces_m=(6.0, 6.0), alturas_piso_m=(3.2, 3.0, 3.0), carga_muerta_kn_m=18.0, carga_viva_kn_m=8.0,
            columna_mm=(450.0, 450.0))


def proyecto(**kw):
    return dp.ProyectoPortico(**BASE, **kw)


def lote_para(p, b, h, ctx=None):
    modelo0, vigas0, _, nid, nx, ny = dp._modelo(p, 300.0, 500.0)
    tpl = gv.construir_plantilla(modelo0, vigas0, nid, nx, ny, dp._pt)
    b, h = np.asarray(b, dtype=float), np.asarray(h, dtype=float)
    pesos = fuerzas = None
    r_der = 1.0
    alt = sp.alturas_nivel_m(p.alturas_piso_m)
    if ctx is not None:
        pesos = sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, p.carga_muerta_kn_m, p.columna_mm, b, h)
        par = sp.parametros_espectro(ctx, alt)
        fuerzas = sp.fuerzas_vectorizadas(par, pesos, alt)
        r_der = par["r"] * par["sa_deriva"] / par["sa"]
    return gv.analizar_lote(tpl, b_mm=b, h_mm=h, Ec=4700 * np.sqrt(21.0) * 1000, factor_i_viga=dp.FACTOR_I_VIGA,
                            carga_muerta=p.carga_muerta_kn_m, carga_viva=p.carga_viva_kn_m, peso_unit=dp.PESO_UNIT_KN_M3,
                            c1_m=p.columna_mm[0] / 1000, fuerzas_e=fuerzas, alturas_piso_m=p.alturas_piso_m,
                            combinaciones=dp._cb.COMBINACIONES_NSR10, r_deriva=r_der, pesos=pesos), nid, nx, ny


CTX = sp.ContextoSismico(aa=0.25, av=0.25, perfil="D", grupo_uso="I", capacidad="DES")
SECCIONES = [(250.0, 500.0), (300.0, 650.0), (450.0, 800.0), (200.0, 350.0)]


def test_pesos_por_nivel_calculados_a_mano():
    w = sp.pesos_nivel_kn((6.0, 6.0), (3.2, 3.0, 3.0), 3, 18.0, (450.0, 450.0), 300.0, 500.0)
    assert w.shape == (3,)
    assert w[0] == pytest.approx(259.2 + 23.328 + 21.87)
    assert w[1] == pytest.approx(259.2 + 21.87 + 21.87)
    assert w[2] == pytest.approx(259.2 + 21.87)


def test_fuerzas_vectorizadas_igualan_las_del_modulo_escalar():
    alt = sp.alturas_nivel_m(BASE["alturas_piso_m"])
    par = sp.parametros_espectro(CTX, alt)
    for b, h in SECCIONES:
        pesos = sp.pesos_nivel_kn(BASE["luces_m"], BASE["alturas_piso_m"], 3, 18.0, (450.0, 450.0), b, h)
        vec = sp.fuerzas_vectorizadas(par, pesos[None, :], alt)[0]
        esc = sp.fuerzas_escalar(CTX, tuple(float(x) for x in pesos), alt).fuerzas_diseno_kn
        assert vec == pytest.approx(esc, rel=1e-12)


def test_la_suma_de_E_es_sa_por_peso_sobre_r():
    cbz, pesos = dp._basal_escalar(proyecto(capacidad="DES"), CTX, 300.0, 600.0)
    assert sum(cbz.fuerzas_diseno_kn) == pytest.approx(0.8125 * sum(pesos) / 7.0)


@pytest.mark.parametrize("b,h", SECCIONES)
def test_paridad_vectorizada_vs_escalar_con_sismo_derivado(b, h):
    p = proyecto(capacidad="DES")
    lote, nid, nx, ny = lote_para(p, [b], [h], CTX)
    cbz, _ = dp._basal_escalar(p, CTX, b, h)
    modelo, vigas, res, w_pp = dp._analizar(p, b, h, cbz.fuerzas_diseno_kn)
    dem, _ = dp._demanda(p, modelo, vigas, res, w_pp, h)
    assert lote.m_neg[0] == pytest.approx(dem.M_neg_apoyo, rel=1e-9)
    assert lote.m_pos_apoyo[0] == pytest.approx(dem.M_pos_apoyo, rel=1e-9, abs=1e-9)
    assert lote.m_pos_vano[0] == pytest.approx(dem.M_pos_vano, rel=1e-9)
    assert lote.v_max[0] == pytest.approx(dem.V_max, rel=1e-9)
    assert lote.v_centro[0] == pytest.approx(dem.V_centro, rel=1e-9)
    assert lote.v_grav[0] == pytest.approx(dem.V_gravedad, rel=1e-9)
    assert lote.ln_min == pytest.approx(dem.luz_libre_m)
    assert lote.deriva_max[0] == pytest.approx(dp._deriva_escalar(p, res, nid, nx, ny, cbz), rel=1e-9)


def test_paridad_solo_gravedad():
    p = proyecto(capacidad="DMI")
    lote, *_ = lote_para(p, [300.0, 250.0], [600.0, 500.0], None)
    for k, (b, h) in enumerate([(300.0, 600.0), (250.0, 500.0)]):
        modelo, vigas, res, w_pp = dp._analizar(p, b, h)
        dem, _ = dp._demanda(p, modelo, vigas, res, w_pp, h)
        assert lote.m_neg[k] == pytest.approx(dem.M_neg_apoyo, rel=1e-9)
        assert lote.m_pos_vano[k] == pytest.approx(dem.M_pos_vano, rel=1e-9)
        assert lote.v_max[k] == pytest.approx(dem.V_max, rel=1e-9)
    assert np.isnan(lote.deriva_max).all()


def test_el_lote_no_depende_del_tamano_del_bloque():
    p = proyecto(capacidad="DES")
    b, h = np.full(10, 300.0), np.linspace(400.0, 850.0, 10)
    a, *_ = lote_para(p, b, h, CTX)
    modelo0, vigas0, _, nid, nx, ny = dp._modelo(p, 300.0, 500.0)
    tpl = gv.construir_plantilla(modelo0, vigas0, nid, nx, ny, dp._pt)
    alt = sp.alturas_nivel_m(p.alturas_piso_m)
    pesos = sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, 18.0, p.columna_mm, b, h)
    par = sp.parametros_espectro(CTX, alt)
    c = gv.analizar_lote(tpl, b_mm=b, h_mm=h, Ec=4700 * np.sqrt(21.0) * 1000, factor_i_viga=dp.FACTOR_I_VIGA, carga_muerta=18.0,
                         carga_viva=8.0, peso_unit=24.0, c1_m=0.45, fuerzas_e=sp.fuerzas_vectorizadas(par, pesos, alt),
                         alturas_piso_m=p.alturas_piso_m, combinaciones=dp._cb.COMBINACIONES_NSR10,
                         r_deriva=par["r"], pesos=pesos, chunk=3)
    assert c.m_neg == pytest.approx(a.m_neg) and c.deriva_max == pytest.approx(a.deriva_max)


def test_vigas_mas_peraltadas_se_deforman_menos():
    p = proyecto(capacidad="DES")
    lote, *_ = lote_para(p, np.full(5, 300.0), np.array([300.0, 450.0, 600.0, 750.0, 900.0]), CTX)
    assert np.all(np.diff(lote.deriva_max) < 0)


def test_pipeline_con_perfil_deriva_E_y_verifica_la_deriva():
    i = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D"))
    assert i.capacidad == "DES" and i.optimo is not None
    assert i.basal["Fa"] == pytest.approx(1.3) and i.basal["Fv"] == pytest.approx(1.9) and i.basal["R"] == 7.0
    assert sum(i.basal["E_diseno_por_nivel_kn"]) == pytest.approx(i.basal["Vs_diseno_kn"])
    assert i.basal["deriva_max_pct_hp"] <= 1.0 + 1e-9
    assert i.diagnostico["paridad_escalar_max_dif_rel"] < 1e-9
    assert i.diagnostico["pasan_deriva"] < i.diagnostico["secciones_totales"]       # la deriva sí descarta secciones
    assert all(c.deriva <= dp.DERIVA_MAX for c in i.ranking)


def test_la_deriva_encarece_el_diseno_frente_a_solo_resistencia():
    con = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D")).optimo.costo_directo
    relajado = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D", factor_deriva_fisurada=0.7)).optimo.costo_directo
    assert relajado <= con


def test_suelo_mas_blando_o_mas_importancia_no_baja_el_costo():
    d = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="C")).optimo.costo_directo
    e = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="E")).optimo.costo_directo
    iv = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="C", grupo_uso="IV")).optimo.costo_directo
    assert e >= d and iv >= d


def test_no_se_pueden_entregar_fuerzas_y_perfil_a_la_vez():
    with pytest.raises(ValueError, match="derivan del espectro"):
        dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D", fuerzas_laterales_kn=(1.0, 2.0, 3.0)))


def test_perfil_sin_aa_av_ni_municipio_falla_con_mensaje_claro():
    with pytest.raises(ValueError, match="Aa y Av"):
        dp.diseno_portico(proyecto(capacidad="DES", perfil_suelo="D"))


def test_aa_av_explicitos_reemplazan_al_apendice():
    i = dp.diseno_portico(proyecto(capacidad="DMO", perfil_suelo="C", aa=0.15, av=0.15))
    assert i.basal["aa"] == 0.15 and i.optimo is not None


def test_perfil_f_se_rechaza():
    with pytest.raises(ValueError, match="A.2.10"):
        dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="F"))


def test_preseleccion_conserva_el_optimo_exacto_en_la_grilla_por_defecto():
    exacto = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D"))
    pre = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D", preseleccion=12))
    assert pre.diagnostico["factibles"] <= 12
    assert pre.diagnostico["diseno_exacto_sobre"] < exacto.diagnostico["diseno_exacto_sobre"]
    assert (pre.optimo.b, pre.optimo.h) == (exacto.optimo.b, exacto.optimo.h)
    assert pre.optimo.costo_directo == pytest.approx(exacto.optimo.costo_directo)


def test_rayleigh_se_reporta_y_dice_si_cambiaria_las_fuerzas():
    b = dp.diseno_portico(proyecto(municipio="Pereira", perfil_suelo="D")).basal
    assert b["periodo_rayleigh_s"] > 0
    assert b["rayleigh_cambia_las_fuerzas"] is False        # ambos períodos caen en la meseta (T < Tc) con k = 1


def test_grilla_de_cincuenta_mil_secciones_se_analiza_y_es_finita():
    p = proyecto(capacidad="DES")
    modelo0, vigas0, _, nid, nx, ny = dp._modelo(p, 300.0, 500.0)
    tpl = gv.construir_plantilla(modelo0, vigas0, nid, nx, ny, dp._pt)
    bb, hh = np.meshgrid(np.linspace(200.0, 600.0, 100), np.linspace(300.0, 1000.0, 500), indexing="ij")
    b, h = bb.ravel(), hh.ravel()
    assert b.size == 50_000
    alt = sp.alturas_nivel_m(p.alturas_piso_m)
    pesos = sp.pesos_nivel_kn(p.luces_m, p.alturas_piso_m, nx, 18.0, p.columna_mm, b, h)
    par = sp.parametros_espectro(CTX, alt)
    r = gv.analizar_lote(tpl, b_mm=b, h_mm=h, Ec=4700 * np.sqrt(21.0) * 1000, factor_i_viga=dp.FACTOR_I_VIGA, carga_muerta=18.0,
                         carga_viva=8.0, peso_unit=24.0, c1_m=0.45, fuerzas_e=sp.fuerzas_vectorizadas(par, pesos, alt),
                         alturas_piso_m=p.alturas_piso_m, combinaciones=dp._cb.COMBINACIONES_NSR10, r_deriva=par["r"], pesos=pesos)
    assert np.isfinite(r.m_neg).all() and np.isfinite(r.deriva_max).all() and r.m_neg.shape == (50_000,)
