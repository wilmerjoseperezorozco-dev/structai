"""#292: viento B.6 (Método 2, edificios bajos) en el edificio 3D: casos W, combinaciones y vigas de cubierta."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src import diseno_edificio_3d as de


def proyecto(**kw):
    base = dict(luces_x_m=(5.0, 5.0), luces_y_m=(5.0, 5.0), alturas_piso_m=(3.0, 3.0), columnas_mm=(350, 350),
                vigas_mm=((300, 400), (300, 400)), carga_muerta_kpa=1.0, carga_viva_kpa=0.5, aa=0.05, av=0.05,
                perfil_suelo="D", divipola="08001")
    base.update(kw)
    return de.ProyectoEdificio3D(**base)


VIENTO = de.VientoB6(v_m_s=36.0, exposicion="D")


def test_casos_conservan_la_presion_de_cubierta_y_el_cortante():
    p = proyecto(viento=VIENTO)
    m = de.construir_modelo(p)
    casos, info = de._casos_viento(p, m)
    assert info["evaluado"] and len(casos) == 8 + 16 and info["torsion_bajos"]
    qh = info["qh_kpa"]
    assert qh == pytest.approx(de._b6.qz(36.0, de._b6.kz(6.0, "D"), 1.0, 0.85, 1.0) / 1000)
    nom, caso, ws = casos[0]                                          # W x+, GCpi+
    total_vigas = sum(w * m.portico.longitud(m.portico.elementos[k]) for k, w in ws.items())
    a = info["a_m"]
    lim2 = min(0.5 * 10.0, 2.5 * 6.0)
    esperado = 0.0
    for ii in range(2):
        for jj in range(2):
            xc, yc = 2.5 + 5 * ii, 2.5 + 5 * jj
            z = ("2" if xc <= lim2 else "3") + ("E" if (yc <= 2 * a or yc >= 10 - 2 * a) else "")
            esperado += -qh * (de._b6.gcpf(z, 0.0) - 0.18) * 25.0
    assert total_vigas == pytest.approx(esperado, rel=1e-9)
    # cortante basal = f por metro de altura × altura total; la reacción del modelo lo equilibra
    r = m.portico.resolver(caso)
    fx = sum(v[0] for v in caso.maestros.values())
    assert -sum(v[0] for v in r.reacciones.values()) == pytest.approx(fx, rel=1e-6)
    be = min(4 * a, 10.0)
    f_alt = qh * ((0.61 + 0.43) * be + (0.40 + 0.29) * (10.0 - be))
    assert fx == pytest.approx(f_alt * (6.0 - 1.5), rel=1e-9)     # la mitad inferior del piso 1 va a la cimentación


def test_combinaciones_con_viento():
    nombres, C, es_e = de.combinaciones()
    n2, C2, e2, w2 = de._extender_viento(nombres, C, es_e, ["a", "b"])
    assert C2.shape == (len(C) + 6, C.shape[1] + 2) and w2.sum() == 6 and not e2[w2].any()
    fila = C2[n2.index("0.9D+1.6[b]")]
    assert fila[0] == 0.9 and fila[1] == 0.0 and fila[-1] == 1.6 and fila[-2] == 0.0


@pytest.fixture(scope="module")
def con_y_sin():
    return de.disenar_edificio(proyecto()), de.disenar_edificio(proyecto(viento=VIENTO))


def test_losa_de_concreto_con_viento_de_region_5_no_cambia_la_cubierta(con_y_sin):
    # 1,6·W de succión (≈ 2,5 kN/m) < 0,9·D de losa + peso propio (≈ 3,9 kN/m): gobierna el sismo, como se esperaba en #292
    sin, con = con_y_sin
    assert con.viento["evaluado"] and con.viento["succion_max_vigas_kn_m"] > 0
    assert con.vigas[-1]["demanda"]["M_neg_apoyo"] == pytest.approx(sin.vigas[-1]["demanda"]["M_neg_apoyo"])


def test_levantamiento_extremo_sube_el_momento_negativo_de_la_cubierta(con_y_sin):
    sin, _ = con_y_sin
    fuerte = de.disenar_edificio(proyecto(viento=de.VientoB6(v_m_s=80.0, exposicion="D")))
    assert fuerte.vigas[-1]["demanda"]["M_neg_apoyo"] > sin.vigas[-1]["demanda"]["M_neg_apoyo"]


def test_memoria_declara_el_viento(con_y_sin):
    sin, con = con_y_sin
    txt = " ".join(str(x.concepto) + str(x.valor) for x in con.memoria.cargas)
    assert "qh" in txt and "0.9D+1.6W" in txt
    assert any(s.startswith("Viento: solo Método 2") for s in con.memoria.no_verifica)
    assert any(s.startswith("Viento (Título B.6)") for s in sin.memoria.no_verifica)


def alto(n=4, **kw):
    return proyecto(alturas_piso_m=(3.0,) * n, columnas_mm=(350,) * n, vigas_mm=((300, 400),) * n, viento=VIENTO, **kw)


def test_edificio_alto_usa_el_metodo_general():                       # #242: h = 12 m > 10 m (menor dimensión)
    p = alto()
    m = de.construir_modelo(p)
    casos, info = de._casos_viento(p, m)
    assert info["evaluado"] and info["metodo"] == "general" and len(casos) == 8 + 8 + 4 + 16
    r = de._b6.fuerzas_por_nivel(36.0, "D", (3.0,) * 4, 10.0, 10.0)
    _n, caso, _w = casos[0]
    assert [caso.maestros[f"P{k}"][0] for k in range(1, 5)] == pytest.approx(r["fuerzas_kn"])
    assert info["rafaga"]["x"] == "rígida"                            # sin sis: n1 desconocido → rígido


def test_metodo_general_succion_de_cubierta_a_mano():
    p = alto()
    m = de.construir_modelo(p)
    casos, info = de._casos_viento(p, m)
    _n, _c, ws = casos[0]                                             # W x+, GCpi+
    total = sum(w * m.portico.longitud(m.portico.elementos[k]) for k, w in ws.items())
    qh, g = info["qh_kpa"], info["G"]["x"]
    esperado = sum(-qh * (g * de._b6.cp_cubierta_general(xc, 12.0, 10.0) - 0.18) * 25.0 for xc in (2.5, 7.5) for _ in range(2))
    assert total == pytest.approx(esperado, rel=1e-9)


def test_metodo_general_con_periodo_flexible_sube_g():
    p = alto()
    m = de.construir_modelo(p)
    _c, rig = de._casos_viento(p, m)
    _c, flex = de._casos_viento(p, m, {"x": {"T_modelo_s": 2.0}, "y": {"T_modelo_s": 2.0}})
    assert flex["rafaga"]["x"] == "flexible" and flex["G"]["x"] > rig["G"]["x"]
    assert flex["cortante_basal_kn"]["x"] > rig["cortante_basal_kn"]["x"]


def test_diseno_alto_con_viento_y_memoria():
    inf = de.disenar_edificio(alto())
    assert inf.viento["evaluado"] and inf.viento["metodo"] == "general"
    assert not any("queda para #242" in a for a in inf.advertencias)


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        de.VientoB6(v_m_s=0.0)
    with pytest.raises(ValueError):
        de.VientoB6(v_m_s=28.0, exposicion="A")


# ---------------------------------------------------------------- cubierta liviana
def test_cubierta_liviana_cambia_solo_el_ultimo_nivel():
    base = de.construir_modelo(proyecto())
    liv = de.construir_modelo(proyecto(carga_muerta_cubierta_kpa=0.3, carga_viva_cubierta_kpa=0.5))
    pp = de.GAMMA_CONCRETO * 0.3 * 0.4
    for k, t in enumerate(liv.meta):
        if t[0] in ("vx", "vy"):
            wD, wL = liv.w_viga[k]
            wD0, wL0 = base.w_viga[k]
            if t[1] == 2:
                assert (wD - pp) == pytest.approx((wD0 - pp) * 0.3 / 1.0) and wL == pytest.approx(wL0 * 0.5 / 0.5)
            else:
                assert (wD, wL) == (wD0, wL0)
    assert liv.pesos[0] == pytest.approx(base.pesos[0])
    assert base.pesos[1] - liv.pesos[1] == pytest.approx(0.7 * 100.0)


def test_cubierta_igual_a_entrepiso_no_cambia_el_diseno():
    a = de.disenar_edificio(proyecto())
    b = de.disenar_edificio(proyecto(carga_muerta_cubierta_kpa=1.0, carga_viva_cubierta_kpa=0.5))
    assert [v["demanda"] for v in a.vigas] == [v["demanda"] for v in b.vigas]


def test_cubierta_liviana_con_viento_advierte_y_no_baja_la_demanda():
    p = proyecto(carga_muerta_cubierta_kpa=0.3, carga_viva_cubierta_kpa=0.5)
    sin = de.disenar_edificio(p)
    con = de.disenar_edificio(proyecto(carga_muerta_cubierta_kpa=0.3, carga_viva_cubierta_kpa=0.5, viento=VIENTO))
    assert any("Cubierta liviana" in a for a in con.advertencias)
    assert con.vigas[-1]["demanda"]["M_neg_apoyo"] >= sin.vigas[-1]["demanda"]["M_neg_apoyo"] - 1e-9
    with pytest.raises(ValueError):
        proyecto(carga_muerta_cubierta_kpa=-1.0)


def test_advierte_si_falta_viento_en_edificio_alto_de_zona_baja():     # #321 (c)
    n = 7                                                             # h = 21 m
    p = proyecto(alturas_piso_m=(3.0,) * n, columnas_mm=(400,) * n, vigas_mm=((300, 450),) * n)
    assert de.ADVERTENCIA_VIENTO_ALTO in de.disenar_edificio(p).advertencias
    assert de.ADVERTENCIA_VIENTO_ALTO not in de.disenar_edificio(proyecto()).advertencias


def test_casos_torsionales_fig_b656_a_mano():                         # #322: M_T = 0,75·F·0,15·B por nivel
    p = alto()                                                        # planta 10 × 10 m, 4 niveles
    m = de.construir_modelo(p)
    casos, _info = de._casos_viento(p, m)
    por_nombre = {n: c for n, c, _w in casos}
    f1 = [por_nombre["Wx+,GCpi+"].maestros[f"P{k}"][0] for k in range(1, 5)]
    c2 = por_nombre["W2x+,e+"].maestros
    for k, f in enumerate(f1, 1):
        fx, fy, mz = c2[f"P{k}"]
        assert fx == pytest.approx(0.75 * f) and fy == 0.0 and mz == pytest.approx(0.75 * f * 0.15 * 10.0)
    fy1 = [por_nombre["Wy+,GCpi+"].maestros[f"P{k}"][1] for k in range(1, 5)]
    c4 = por_nombre["W4x+y-,ex+ey-"].maestros["P2"]
    assert c4 == pytest.approx((0.563 * f1[1], -0.563 * fy1[1], 0.563 * (f1[1] * 1.5 - fy1[1] * 1.5)))
    c3 = por_nombre["W3x-y+"].maestros["P4"]
    assert c3 == pytest.approx((-0.75 * f1[3], 0.75 * fy1[3], 0.0))
    assert all(not w for n, _c, w in casos if n.startswith(("W2", "W3", "W4")))   # sin cubierta (HIPÓTESIS)


def test_casos_torsionales_aparecen_en_la_memoria():
    p = alto()
    r = de.disenar_edificio(p)
    txt = " ".join(str(l.concepto) + " " + str(l.valor) for l in r.memoria.cargas)
    assert "Fig. B.6.5-6" in txt and "0,563" in txt and "e_R no se calcula" in txt


def test_sin_casos_parciales_queda_solo_el_caso_1():                  # opción de medición de #322
    from dataclasses import replace
    p = replace(alto(), viento=replace(VIENTO, casos_parciales=False))
    casos, info = de._casos_viento(p, de.construir_modelo(p))
    assert len(casos) == 8 and info["casos_fig_b656"] == (1,)


def test_casos_torsionales_de_edificios_bajos_a_mano():               # #322 parte 2: Fig. B.6.5-7, nota 5
    p = proyecto(viento=VIENTO)                                       # planta 10 × 10 m, 2 niveles de 3 m
    casos, info = de._casos_viento(p, de.construir_modelo(p))
    c = {n: k for n, k, _w in casos}
    qh, a = info["qh_kpa"], info["a_m"]
    fb = de._b6.gcpf("1E", 0.0) - de._b6.gcpf("4E", 0.0)
    fi = de._b6.gcpf("1", 0.0) - de._b6.gcpf("4", 0.0)
    # esquina de referencia en y = 0: 1E−4E en [0, 2a], 1−4 en [2a, 5], 0,25·(1−4) en [5, 10]
    tr = [(0.0, 2 * a, fb), (2 * a, 5.0, fi), (5.0, 10.0, 0.25 * fi)]
    f = qh * sum(k * (u1 - u0) for u0, u1, k in tr)
    yc = qh * sum(k * (u1 - u0) * (u0 + u1) / 2 for u0, u1, k in tr) / f
    ht = 3.0                                                          # nivel 1: 1,5 + 1,5 m
    fx, fy, mz = c["Wx+,T0,GCpi+"].maestros["P1"]
    assert fx == pytest.approx(f * ht) and fy == 0.0 and mz == pytest.approx(-f * ht * (yc - 5.0))
    assert yc < 5.0 and mz > 0                                        # la resultante se corre hacia la esquina de referencia
    assert c["Wx+,T1,GCpi+"].maestros["P1"][2] == pytest.approx(-mz)  # esquina opuesta: torsor opuesto
    # cubierta: el panel lejano (y entre 5 y 10, x entre 0 y 5) lleva 25 % de la presión neta de la zona 2
    _n, _k, ws_t = next(t for t in casos if t[0] == "Wx+,T0,GCpi+")
    assert sum(ws_t.values()) < sum(next(t for t in casos if t[0] == "Wx+,GCpi+")[2].values())


def test_un_nivel_bajo_9_m_no_lleva_casos_torsionales():               # excepción de la nota 5
    p = proyecto(alturas_piso_m=(4.0,), columnas_mm=(300,), vigas_mm=((300, 400),), viento=VIENTO)
    casos, info = de._casos_viento(p, de.construir_modelo(p))
    assert len(casos) == 8 and not info["torsion_bajos"]
