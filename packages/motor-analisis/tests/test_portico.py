import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.combinaciones import envolvente
from src.portico import Caso, Elemento, Nodo, Portico

E, A, I = 2.2e7, 0.12, 1.6e-3      # kN/m2, m2, m4  (~300x400)
EI = E * I
L, W = 6.0, 20.0                   # m, kN/m


def viga_simple(n_elem=2):
    xs = np.linspace(0, L, n_elem + 1)
    nodos = [Nodo(float(x), 0.0) for x in xs]
    els = [Elemento(k, k + 1, E, A, I) for k in range(n_elem)]
    return Portico(nodos, els, {0: (True, True, False), n_elem: (False, True, False)})


def test_viga_simple_reacciones_momento_y_flecha():
    p = viga_simple(2)
    r = p.resolver(Caso("D", uniformes={0: W, 1: W}))
    assert r.reacciones[0][1] == pytest.approx(W * L / 2)
    assert r.reacciones[2][1] == pytest.approx(W * L / 2)
    assert r.u[1][1] == pytest.approx(-5 * W * L**4 / (384 * EI), rel=1e-9)
    d = p.diagrama(r, 0, np.array([0.0, L / 2]))
    assert d["M"][1] == pytest.approx(W * L**2 / 8)
    assert d["V"][0] == pytest.approx(W * L / 2)
    assert d["V"][1] == pytest.approx(0.0, abs=1e-9)


def test_viga_biempotrada_momentos_de_empotramiento():
    p = Portico([Nodo(0, 0), Nodo(L, 0)], [Elemento(0, 1, E, A, I)], {0: (True, True, True), 1: (True, True, True)})
    r = p.resolver(Caso("D", uniformes={0: W}))
    d = p.diagrama(r, 0, np.array([0.0, L / 2, L]))
    assert d["M"][0] == pytest.approx(-W * L**2 / 12)
    assert d["M"][1] == pytest.approx(W * L**2 / 24)
    assert d["M"][2] == pytest.approx(-W * L**2 / 12)


def test_viga_continua_dos_vanos_iguales():
    nodos = [Nodo(0, 0), Nodo(L, 0), Nodo(2 * L, 0)]
    p = Portico(nodos, [Elemento(0, 1, E, A, I), Elemento(1, 2, E, A, I)],
                {0: (True, True, False), 1: (False, True, False), 2: (False, True, False)})
    r = p.resolver(Caso("D", uniformes={0: W, 1: W}))
    assert r.reacciones[0][1] == pytest.approx(3 * W * L / 8)
    assert r.reacciones[1][1] == pytest.approx(10 * W * L / 8)
    d = p.diagrama(r, 0, np.array([L]))
    assert d["M"][0] == pytest.approx(-W * L**2 / 8)


def test_voladizo_flecha_y_momento_en_el_empotramiento():
    P = 15.0
    p = Portico([Nodo(0, 0), Nodo(L, 0)], [Elemento(0, 1, E, A, I)], {0: (True, True, True)})
    r = p.resolver(Caso("P", nodales={1: (0.0, -P, 0.0)}))
    assert r.u[1][1] == pytest.approx(-P * L**3 / (3 * EI), rel=1e-9)
    assert p.diagrama(r, 0, np.array([0.0]))["M"][0] == pytest.approx(-P * L)


def test_portico_con_viga_rigida_momento_en_columnas_es_p_h_sobre_4():
    h, P = 3.5, 40.0
    nodos = [Nodo(0, 0), Nodo(0, h), Nodo(L, h), Nodo(L, 0)]
    Ar = A * 1e6   # axialmente rigido: la formula Ph/4 supone columnas sin acortamiento
    cols_beam = [Elemento(0, 1, E, Ar, I), Elemento(1, 2, E, Ar, I * 1e6), Elemento(3, 2, E, Ar, I)]
    p = Portico(nodos, cols_beam, {0: (True, True, True), 3: (True, True, True)})
    r = p.resolver(Caso("E", nodales={1: (P, 0.0, 0.0)}))
    assert r.reacciones[0][0] + r.reacciones[3][0] == pytest.approx(-P)
    assert abs(r.reacciones[0][0]) == pytest.approx(P / 2, rel=1e-4)
    assert abs(r.reacciones[0][2]) == pytest.approx(P * h / 4, rel=1e-4)


def test_equilibrio_global_con_gravedad_y_lateral():
    h = 3.0
    nodos = [Nodo(0, 0), Nodo(0, h), Nodo(L, h), Nodo(L, 0), Nodo(0, 2 * h), Nodo(L, 2 * h)]
    els = [Elemento(0, 1, E, A, I), Elemento(3, 2, E, A, I), Elemento(1, 2, E, A, I),
           Elemento(1, 4, E, A, I), Elemento(2, 5, E, A, I), Elemento(4, 5, E, A, I)]
    p = Portico(nodos, els, {0: (True, True, True), 3: (True, True, True)})
    r = p.resolver(Caso("X", nodales={1: (30.0, 0, 0), 4: (50.0, 0, 0)}, uniformes={2: W, 5: W}))
    assert sum(v[0] for v in r.reacciones.values()) == pytest.approx(-80.0)
    assert sum(v[1] for v in r.reacciones.values()) == pytest.approx(2 * W * L)


def test_modelo_inestable_se_rechaza():
    with pytest.raises(ValueError, match="inestable"):
        Portico([Nodo(0, 0), Nodo(L, 0)], [Elemento(0, 1, E, A, I)], {0: (False, True, False), 1: (False, True, False)})


def test_carga_uniforme_en_columna_se_rechaza():
    p = Portico([Nodo(0, 0), Nodo(0, 3)], [Elemento(0, 1, E, A, I)], {0: (True, True, True)})
    with pytest.raises(ValueError, match="horizontales"):
        p.resolver(Caso("D", uniformes={0: 1.0}))


def test_envolvente_gobierna_1_2d_mas_1_6l_en_viga_simple():
    p = viga_simple(1)
    rd = p.resolver(Caso("D", uniformes={0: 10.0}))
    rl = p.resolver(Caso("L", uniformes={0: 6.0}))
    env = envolvente(p, {"D": rd, "L": rl}, 0)
    wu = 1.2 * 10 + 1.6 * 6
    centro = env.x.size // 2
    assert env.M_max[centro] == pytest.approx(wu * L**2 / 8)
    assert env.combo_M_max[centro] == "1.2D+1.6L"
    assert env.V_max[0] == pytest.approx(wu * L / 2)


def test_envolvente_con_sismo_da_momentos_positivos_y_negativos_en_apoyos():
    h = 3.0
    nodos = [Nodo(0, 0), Nodo(0, h), Nodo(L, h), Nodo(L, 0)]
    els = [Elemento(0, 1, E, A, I), Elemento(1, 2, E, A, I), Elemento(3, 2, E, A, I)]
    p = Portico(nodos, els, {0: (True, True, True), 3: (True, True, True)})
    rd = p.resolver(Caso("D", uniformes={1: 15.0}))
    rl = p.resolver(Caso("L", uniformes={1: 8.0}))
    re = p.resolver(Caso("E", nodales={1: (60.0, 0, 0)}))
    env = envolvente(p, {"D": rd, "L": rl, "E": re}, 1, posiciones_extra=(0.2, L - 0.2))
    ap = env.en(0.2)
    # el sismo invierte el signo del momento en un apoyo: aparece momento positivo (inferior) en el apoyo
    assert ap["M_min"] < 0 < ap["M_max"]
    assert env.en(L / 2)["M_max"] > 0
