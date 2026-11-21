"""#292: deflexiones de servicio (C.9.5) y disposición de la carga viva (C.8.11.2) en el edificio 3D."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_edificio_3d as de


def proyecto(**kw):
    base = dict(luces_x_m=(6.0, 6.0, 6.0), luces_y_m=(5.0, 5.0), alturas_piso_m=(3.0,) * 3, columnas_mm=(500,) * 3,
                vigas_mm=((350, 500),) * 3, carga_muerta_kpa=6.0, carga_viva_kpa=1.8, aa=0.10, av=0.10, perfil_suelo="D",
                capacidad="DMI")
    base.update(kw)
    return de.ProyectoEdificio3D(**base)


def test_flecha_biapoyada_carga_uniforme():
    L, w, EI = 6.0, 20.0, 5e4
    xs = np.linspace(0, L, 41)
    assert de._flecha_rel(w * xs * (L - xs) / 2, xs, L, EI) == pytest.approx(5 * w * L**4 / (384 * EI), rel=2e-3)


def test_flecha_doble_empotrada_es_un_quinto():
    L, w, EI = 6.0, 20.0, 5e4
    xs = np.linspace(0, L, 41)
    M = w * xs * (L - xs) / 2 - w * L**2 / 12
    assert de._flecha_rel(M, xs, L, EI) == pytest.approx(w * L**4 / (384 * EI), rel=5e-3)


def test_icr_simplemente_reforzada_coincide_con_la_formula_cerrada():
    b, d, As, n = 0.3, 0.45, 1.5e-3, 8.0
    rho = As / (b * d)
    k = math.sqrt(2 * rho * n + (rho * n) ** 2) - rho * n
    esperado = b * (k * d) ** 3 / 3 + n * As * (d - k * d) ** 2
    assert de._icr(b, d, 0.05, As, 0.0, n) == pytest.approx(esperado, rel=1e-9)


def test_ie_entre_icr_e_ig():
    assert de._ie(10.0, 1.0, 0.3, 20.0) == 1.0
    ie = de._ie(40.0, 1.0, 0.3, 20.0)
    assert 0.3 < ie < 1.0
    assert ie == pytest.approx(0.125 + 0.875 * 0.3)


def test_patrones_alternados_son_complementarios_y_alternan_por_nivel():
    m = de.construir_modelo(proyecto())
    pats = dict(de._patrones_viva(m))
    a, b = pats["alternados 0"], pats["alternados 1"]
    vigas = {k for k, t in enumerate(m.meta) if t[0] in ("vx", "vy")}
    assert a | b == vigas and not a & b
    vx = {(t[1], t[2], t[3]): k for k, t in enumerate(m.meta) if t[0] == "vx"}
    assert (vx[(1, 0, 0)] in a) != (vx[(1, 1, 0)] in a)            # vanos vecinos alternan
    assert (vx[(1, 0, 0)] in a) != (vx[(2, 0, 0)] in a)            # y alternan por nivel
    assert len(pats) >= 4                                           # + pares de vanos adyacentes


def test_patron_alternado_aumenta_el_momento_positivo_de_gravedad():
    p = proyecto()
    m = de.construir_modelo(p)
    sis = de.analisis_sismico(p, m)
    der = de._s3.analizar_fhe(m.portico, m.pisos, sis["x"]["Fs_deriva_kn"], sis["y"]["Fs_deriva_kn"], "general", True)
    F, _ = de._resolver_casos(p, m, sis, der["Ax"])
    pats = de._patrones_viva(m)
    Fx = np.concatenate([F, de._resolver_patrones(m, pats)])
    solo_grav = np.array([[1.2, 1.6, 0, 0, 0, 0]])
    _, Cx, _ = de._extender_combinaciones(["g"], solo_grav, np.array([False]), pats)
    d0, _ = de._demanda_vigas(p, m, F, solo_grav, 1)
    d1, _ = de._demanda_vigas(p, m, Fx, Cx, 1, pats)
    assert d1.M_pos_vano > d0.M_pos_vano * 1.01
    assert d1.M_neg_apoyo >= d0.M_neg_apoyo * 0.999


def test_diseno_incluye_deflexiones_y_la_memoria_lo_declara():
    inf = de.disenar_edificio(proyecto())
    assert inf.cumple, inf.fallas
    for fv in inf.vigas:
        nombres = [v.nombre for v in fv["diseno"].verificaciones]
        assert any(n.startswith("Deflexión inmediata") for n in nombres)
        assert any(n.startswith("Deflexión después") for n in nombres)
    cub = inf.vigas[-1]["diseno"].verificaciones
    assert any("ℓ/180 (cubierta)" in v.nombre for v in cub)
    assert not any("Deflexiones de vigas por cargas de servicio" in s for s in de.NO_VERIFICA)
    conceptos = [ln.concepto for ln in inf.memoria.cargas]
    assert "Disposición de la carga viva" in conceptos and "Deflexiones de servicio" in conceptos


def test_viga_esbelta_no_cumple_por_deflexion():
    p = proyecto(luces_x_m=(9.0, 9.0), luces_y_m=(9.0,), vigas_mm=((300, 400),) * 3, carga_muerta_kpa=8.0,
                 carga_viva_kpa=5.0)
    inf = de.disenar_edificio(p)
    assert any("deflexión" in f and "C.9.5" in f for f in inf.fallas) or any(
        "ningún refuerzo" in f for f in inf.fallas)


def test_divisiones_no_fragiles_relajan_el_limite():
    p = proyecto()
    fr = de.disenar_edificio(p).vigas[0]["diseno"].verificaciones
    nf = de.disenar_edificio(proyecto(divisiones_fragiles=False)).vigas[0]["diseno"].verificaciones
    cap = lambda vs: next(v.capacidad for v in vs if v.nombre.startswith("Deflexión después"))  # noqa: E731
    assert cap(nf) == pytest.approx(2 * cap(fr))


def test_margen_de_gravedad_escala_solo_la_demanda_de_gravedad():
    base = de.disenar_edificio(proyecto())
    con = de.disenar_edificio(proyecto(u_max_gravedad=0.9))
    assert base.cumple and con.cumple
    # la envolvente sube, pero nunca más que 1/0,9 (las combinaciones con sismo no se escalan)
    m0, m1 = base.vigas[-1]["demanda"]["M_pos_vano"], con.vigas[-1]["demanda"]["M_pos_vano"]
    assert m0 < m1 <= m0 / 0.9 + 1e-9
    v0, v1 = base.vigas[-1]["demanda"]["V_gravedad"], con.vigas[-1]["demanda"]["V_gravedad"]
    assert v1 == pytest.approx(v0)                                  # Ve por capacidad usa la gravedad sin mayorar
    assert con.cantidades["costo_cop"] >= base.cantidades["costo_cop"]
    assert any("u_máx = 0.9" in str(ln.valor) for ln in con.memoria.cargas)


def test_u_max_recomendado_solo_en_zona_baja():
    assert de.u_max_recomendado(proyecto()) == de.U_MAX_ZONA_BAJA
    assert de.u_max_recomendado(proyecto(aa=0.25, av=0.25)) == 1.0
    with pytest.raises(ValueError):
        proyecto(u_max_gravedad=1.2)
