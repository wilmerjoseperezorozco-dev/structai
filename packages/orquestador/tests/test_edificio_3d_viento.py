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
    assert info["evaluado"] and len(casos) == 8
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
    assert info["evaluado"] and info["metodo"] == "general" and len(casos) == 8
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
