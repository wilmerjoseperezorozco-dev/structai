"""#236: PTAP, PTAR y sistema lagunar bajo las reglas de docs/REGLAS_MOTORES_DE_CALCULO.md.

Las respuestas esperadas se calculan aquí con aritmética propia a partir de las fórmulas citadas (Mara 2003,
Marais 1974) y de los números de la Res. 0330 y la Res. 0631, sin llamar a las funciones del motor (regla 4).
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import vertimientos  # noqa: E402
from src.contrato_saneamiento import lagunas_contrato, ptap_contrato, ptar_contrato  # noqa: E402
from src.lagunas import SolicitudLagunas  # noqa: E402
from src.schemas_saneamiento import (  # noqa: E402
    CoagulanteType, PTAPRequest, PTARRequest, TecnologiaPTAR, TipoCuerpoReceptor,
)


def _lagunas(**cambios):
    base = dict(caudal_medio_m3_dia=1000.0, poblacion_equivalente=5000, dbo5_afluente_mg_l=300.0,
                coliformes_afluente_nmp_100ml=1e7, coliformes_objetivo_nmp_100ml=1000.0, temperatura_agua_c=25.0,
                incluir_anaerobia=True, profundidad_anaerobia_m=3.0, profundidad_facultativa_m=1.5,
                profundidad_maduracion_m=1.0, borde_libre_m=0.4, alta_turbulencia_atmosferica=False,
                tasa_acumulacion_lodos_m3_hab_ano=0.04, area_disponible_m2=None, cuerpo_receptor="rio")
    base.update(cambios)
    return SolicitudLagunas(**base)


def _ptar(**cambios):
    base = dict(poblacion_diseno=5000, caudal_acueducto_ls=50.0, factor_retorno=0.8, dbo5_cruda_mg_l=250.0,
                tecnologia=TecnologiaPTAR.UASB, tipo_cuerpo_receptor=TipoCuerpoReceptor.RIO, temperatura_agua_c=24.0)
    base.update(cambios)
    return PTARRequest(**base)


# ─── Sistema lagunar: caso resuelto a mano a 25 °C ──────────────────────────

def test_lagunas_caso_a_mano_25c():
    """Q = 1000 m³/d, Li = 300 mg/L, N0 = 1e7, objetivo 1000, T = 25 °C (cálculo independiente)."""
    q, li, t = 1000.0, 300.0, 25.0
    lam_v = 10 * t + 100                          # 350 g/m³·d
    theta_a = max(li / lam_v, 1.0)                # 0,857 → 1 d (mínimo del art. 196)
    lf = li * (1 - (2 * t + 20) / 100)            # 70 % → 90 mg/L
    lam_s = 350 * (1.107 - 0.002 * t) ** (t - 25)  # 350 kg/ha·d
    theta_f = max(10 * lf * q / lam_s * 1.5 / q, 5.0)  # 3,86 → 5 d (mínimo del art. 197)
    af = q * theta_f / 1.5
    le = lf / (1 + 0.3 * 1.05 ** (t - 20) * theta_f)
    kt = 2.6 * 1.19 ** (t - 20)
    n_fac = 1e7 / ((1 + kt * theta_a) * (1 + kt * theta_f))
    # n = 1 exige θ = 6,8 d (6825 m²); n = 2 queda en el mínimo de 3 d (6000 m²); n = 3 da 9000 m².
    assert (n_fac / 1000 - 1) / kt * q > 2 * 3.0 * q
    n_final = n_fac / (1 + kt * 3.0) ** 2

    r = lagunas_contrato(_lagunas())
    v = r.valor
    ana, fac, mad = v["lagunas"]
    assert ana["trh_d"] == pytest.approx(theta_a) and ana["area_m2"] == pytest.approx(q * theta_a / 3.0, rel=1e-4)
    assert fac["area_m2"] == pytest.approx(af, rel=1e-4) and fac["trh_d"] == pytest.approx(5.0)
    assert v["dbo5_efluente_mg_l"] == pytest.approx(le, rel=1e-4)
    assert v["n_lagunas_maduracion"] == 2 and mad["trh_d"] == pytest.approx(3.0)
    assert v["coliformes_efluente_nmp_100ml"] == pytest.approx(n_final, rel=1e-9)
    assert v["area_espejo_total_m2"] == pytest.approx(q / 3.0 + af + 6000.0, rel=1e-4)
    assert v["lodos"]["periodo_remocion_anos"] == pytest.approx(0.5 * q * theta_a / (5000 * 0.04), rel=1e-4)
    assert v["limites_res0631_mg_l"]["DBO5"] == 90.0 and v["cumple_res0631_dbo5"] is True
    assert r.en_borde_dominio is True             # los TRH tocaron los mínimos normativos
    assert r.aviso_responsabilidad_profesional


def test_maduracion_una_laguna_coincide_con_mezcla_completa_cerrada():
    """Sin anaerobia y con objetivo laxo, N = N0 / [(1 + k·θf)(1 + k·θm)] (solución cerrada de mezcla completa)."""
    t = 20.0
    r = lagunas_contrato(_lagunas(temperatura_agua_c=t, incluir_anaerobia=False, profundidad_anaerobia_m=None,
                                  dbo5_afluente_mg_l=200.0, coliformes_objetivo_nmp_100ml=5e4))
    fac = r.valor["lagunas"][0]
    k = 2.6
    lam_s = 350 * (1.107 - 0.002 * t) ** (t - 25)
    theta_f = 10 * 200 * 1000 / lam_s * 1.5 / 1000
    assert fac["trh_d"] == pytest.approx(theta_f, rel=1e-4)
    n_fac = 1e7 / (1 + k * theta_f)
    theta_m = max(3.0, (n_fac / 5e4 - 1) / k)
    assert r.valor["n_lagunas_maduracion"] == 1
    assert r.valor["coliformes_efluente_nmp_100ml"] == pytest.approx(n_fac / (1 + k * theta_m), rel=1e-9)


def test_res0631_art8_tramos_y_suelo():
    assert vertimientos.limites_art8(600, "rio")["DBO5"] == 90.0
    assert vertimientos.limites_art8(3000, "lago")["SST"] == 90.0
    assert vertimientos.limites_art8(3001, "quebrada") == {"DBO5": 70.0, "SST": 70.0, "DQO": 150.0}
    with pytest.raises(ValueError, match="no aplica a vertimientos al suelo"):
        vertimientos.limites_art8(100, "suelo")


# ─── Regla 1: fallo explícito ───────────────────────────────────────────────

@pytest.mark.parametrize("cambio, articulo", [
    (dict(profundidad_anaerobia_m=2.0), "art. 196"),
    (dict(profundidad_facultativa_m=3.0), "art. 197"),
    (dict(profundidad_maduracion_m=1.5), "art. 198"),
    (dict(borde_libre_m=0.6), "art. 199"),
    (dict(profundidad_anaerobia_m=None), "art. 196"),
])
def test_lagunas_fuera_de_rango_cita_la_norma(cambio, articulo):
    with pytest.raises(ValueError, match=articulo):
        lagunas_contrato(_lagunas(**cambio))


def test_lagunas_area_insuficiente_falla():
    with pytest.raises(ValueError, match="disponibles"):
        lagunas_contrato(_lagunas(area_disponible_m2=5000.0))


def test_ptar_suelo_ya_no_inventa_limite():
    """Rojo antes de #236: 'suelo' devolvía un límite de 300 mg/L que no existe en la Res. 0631."""
    with pytest.raises(ValueError, match="suelo"):
        ptar_contrato(_ptar(tipo_cuerpo_receptor=TipoCuerpoReceptor.SUELO))


def test_ptar_lago_usa_el_limite_de_cuerpo_superficial():
    """Rojo antes de #236: 'lago' tenía un límite de 30 mg/L; la Res. 0631 no distingue lagos de ríos."""
    assert ptar_contrato(_ptar(tipo_cuerpo_receptor=TipoCuerpoReceptor.LAGO)).valor["limite_res0631_dbo"] == 90.0


def test_ptar_carga_alta_usa_tramo_de_70():
    r = ptar_contrato(_ptar(caudal_acueducto_ls=200.0, poblacion_diseno=80000))   # 250 mg/L × 13.824 m³/d = 3456 kg/d
    assert r.valor["limite_res0631_dbo"] == 70.0 and r.valor["limite_res0631_sst"] == 70.0


def test_ptar_uasb_sin_temperatura_falla():
    with pytest.raises(ValueError, match="tabla 31"):
        ptar_contrato(_ptar(temperatura_agua_c=None))


def test_ptar_laguna_sin_profundidad_falla():
    """Rojo antes de #236: la laguna facultativa usaba 1,5 m fijos."""
    with pytest.raises(ValueError, match="art. 197"):
        ptar_contrato(_ptar(tecnologia=TecnologiaPTAR.LAGUNA_FACULTATIVA, profundidad_laguna_m=None))


# ─── UASB y filtro percolador dentro de la Res. 0330 ───────────────────────

def test_uasb_cumple_profundidad_y_velocidad_del_art_189():
    """Rojo antes de #236: v = 0,6 m/h y TRH = 6 h daban 3,6 m de altura, bajo el mínimo de 4,5 m."""
    d = ptar_contrato(_ptar()).valor["dimensionamiento"]
    assert 4.5 - 1e-9 <= d["altura_util_m"] <= 6.0
    assert 0.5 <= d["velocidad_ascensional_m_h"] <= 0.7
    assert d["trh_h"] == pytest.approx(4.5 / 0.7, rel=1e-3)        # TRH mínimo que alcanza 4,5 m con 0,7 m/h


def test_uasb_factor_pico_limita_la_velocidad():
    d = ptar_contrato(_ptar(factor_pico=2.0)).valor["dimensionamiento"]
    assert d["velocidad_ascensional_m_h"] * 2.0 <= 1.1 + 1e-9


def test_filtro_percolador_cumple_tabla_38():
    """Rojo antes de #236: reportaba 4 m³/m²·d con una carga real de 8 y carga orgánica ~1 kg/m³·d."""
    d = ptar_contrato(_ptar(tecnologia=TecnologiaPTAR.FILTRO_PERCOLADOR)).valor["dimensionamiento"]
    assert 0.24 <= d["carga_organica_kg_dbo_m3_dia"] <= 0.48 + 1e-9
    assert 4.0 - 1e-9 <= d["carga_hidraulica_m3_m2_dia"] <= 10.0 + 1e-9
    assert 1.8 <= d["profundidad_m"] <= 2.4
    q = 50 * 0.8 * 86.4
    assert d["carga_hidraulica_m3_m2_dia"] == pytest.approx(q * (1 + d["relacion_recirculacion"]) / d["area_m2"], rel=1e-3)


def test_eficiencia_requerida_se_usa():
    """Rojo antes de #236: el campo se aceptaba y se ignoraba."""
    r = ptar_contrato(_ptar(tecnologia=TecnologiaPTAR.LODOS_ACTIVADOS, eficiencia_requerida_dbo_pct=95.0))
    assert r.valor["eficiencia_requerida_dbo_pct"] == 95.0 and r.valor["cumple_res0631"] is False


# ─── PTAP ───────────────────────────────────────────────────────────────────

def test_ptap_contrato_no_afirma_cumplimiento_y_respeta_art_114_y_121():
    r = ptap_contrato(PTAPRequest(caudal_diseno_ls=50, turbidez_cruda_ntu=30, color_crudo_uc=15, ph_crudo=7.0,
                                  temperatura_c=20, coagulante=CoagulanteType.ALUMBRE))
    v = r.valor
    assert v["cumple_res2115"] is None
    filtros = next(u for u in v["unidades"] if u["nombre"].startswith("Filtros"))
    assert filtros["dimensiones"]["n_filtros"] >= 4
    desinf = next(u for u in v["unidades"] if "desinfección" in u["nombre"])
    assert desinf["dimensiones"]["t_contacto_min"] >= 20.0
    assert "121" in r.referencia_normativa and r.supuestos


# ─── Regla 7: monotonicidad y homogeneidad ─────────────────────────────────

def test_lagunas_mas_coliformes_no_reduce_area():
    a = [lagunas_contrato(_lagunas(coliformes_afluente_nmp_100ml=n)).valor["area_espejo_total_m2"]
         for n in (1e5, 1e6, 1e7, 1e8)]
    assert a == sorted(a)


def test_lagunas_escala_lineal_con_el_caudal():
    """Con la misma concentración, doblar el caudal dobla cada área y conserva los TRH (homogeneidad)."""
    r1 = lagunas_contrato(_lagunas()).valor
    r2 = lagunas_contrato(_lagunas(caudal_medio_m3_dia=2000.0, poblacion_equivalente=10000)).valor
    assert r2["area_espejo_total_m2"] == pytest.approx(2 * r1["area_espejo_total_m2"], rel=1e-6)
    for l1, l2 in zip(r1["lagunas"], r2["lagunas"]):
        assert l2["trh_d"] == pytest.approx(l1["trh_d"])
    assert r2["lodos"]["periodo_remocion_anos"] == pytest.approx(r1["lodos"]["periodo_remocion_anos"])


def test_lagunas_mas_calor_no_aumenta_area():
    a = [lagunas_contrato(_lagunas(temperatura_agua_c=t)).valor["area_espejo_total_m2"] for t in (15, 20, 25, 30)]
    assert all(x >= y - 1e-6 for x, y in zip(a, a[1:]))
