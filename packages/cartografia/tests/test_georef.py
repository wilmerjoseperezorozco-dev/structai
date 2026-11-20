"""Tests de cartografia/src/georef.py (issue #211).

Referencia independiente: la serie de Krüger para Transversa de Mercator (Karney 2011, ec. 35–36, orden n^6),
escrita aquí a mano a partir de los parámetros publicados de EPSG:9377, sin llamar a pyproj. Su error es de
micrómetros dentro de Colombia, así que una diferencia > 1 mm frente a pyproj indicaría un error de configuración."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest

import georef as g

# Parámetros de EPSG:9377 (Res. IGAC 471/2020) y GRS80
A, F = 6378137.0, 1 / 298.257222101
LAT0, LON0, K0, X0, Y0 = 4.0, -73.0, 0.9992, 5_000_000.0, 2_000_000.0


def _kruger(lon, lat):
    n = F / (2 - F)
    a_rect = A / (1 + n) * (1 + n**2 / 4 + n**4 / 64 + n**6 / 256)
    alfa = [
        n / 2 - 2 * n**2 / 3 + 5 * n**3 / 16 + 41 * n**4 / 180 - 127 * n**5 / 288 + 7891 * n**6 / 37800,
        13 * n**2 / 48 - 3 * n**3 / 5 + 557 * n**4 / 1440 + 281 * n**5 / 630 - 1983433 * n**6 / 1935360,
        61 * n**3 / 240 - 103 * n**4 / 140 + 15061 * n**5 / 26880 + 167603 * n**6 / 181440,
        49561 * n**4 / 161280 - 179 * n**5 / 168 + 6601661 * n**6 / 7257600,
        34729 * n**5 / 80640 - 3418889 * n**6 / 1995840,
        212378941 * n**6 / 319334400,
    ]
    e = math.sqrt(F * (2 - F))

    def xi_eta(lon_, lat_):
        phi, lam = math.radians(lat_), math.radians(lon_ - LON0)
        t = math.sinh(math.atanh(math.sin(phi)) - e * math.atanh(e * math.sin(phi)))
        xi_p = math.atan2(t, math.cos(lam))
        eta_p = math.asinh(math.sin(lam) / math.sqrt(t * t + math.cos(lam) ** 2))
        xi = xi_p + sum(a * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p) for j, a in enumerate(alfa, 1))
        eta = eta_p + sum(a * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p) for j, a in enumerate(alfa, 1))
        return xi, eta

    xi, eta = xi_eta(lon, lat)
    xi0, _ = xi_eta(LON0, LAT0)
    return X0 + K0 * a_rect * eta, Y0 + K0 * a_rect * (xi - xi0)


PUNTOS = {  # lon, lat (WGS84 ≈ MAGNA-SIRGAS al nivel de cm; aquí se compara la proyección, no el datum)
    "bogota": (-74.0758, 4.5981),
    "barranquilla": (-74.7813, 10.9639),
    "leticia": (-69.9406, -4.2153),
    "san_andres": (-81.7006, 12.5847),
    "puerto_carreno": (-67.4859, 6.1890),
    "pasto": (-77.2811, 1.2136),
}


def test_origen_de_la_proyeccion_es_exacto():
    e, n = g.a_ctm12(LON0, LAT0, "MAGNA-SIRGAS-2018")
    assert e == pytest.approx(X0, abs=1e-6) and n == pytest.approx(Y0, abs=1e-6)


@pytest.mark.parametrize("ciudad", sorted(PUNTOS))
def test_pyproj_coincide_con_kruger_independiente(ciudad):
    lon, lat = PUNTOS[ciudad]
    e, n = g.a_ctm12(lon, lat, "MAGNA-SIRGAS-2018")   # geográfico del mismo datum: sin cambio de datum
    er, nr = _kruger(lon, lat)
    assert abs(e - er) < 1e-3 and abs(n - nr) < 1e-3, (e - er, n - nr)


def test_ida_y_vuelta_geografica_submilimetrica():
    lon, lat = np.array([p[0] for p in PUNTOS.values()]), np.array([p[1] for p in PUNTOS.values()])
    e, n = g.a_ctm12(lon, lat)
    lon2, lat2 = g.de_ctm12(e, n)
    e2, n2 = g.a_ctm12(lon2, lat2)
    assert np.max(np.abs(np.asarray(e2) - e)) < 1e-3 and np.max(np.abs(np.asarray(n2) - n)) < 1e-3


def test_zona_antigua_bogota_3116_llega_al_mismo_punto():
    lon, lat = PUNTOS["bogota"]
    x, y = g.transformador("MAGNA-SIRGAS", 3116).transform(lon, lat)
    e1, n1 = g.a_ctm12(x, y, "MAGNA-BOGOTA")
    e2, n2 = g.a_ctm12(lon, lat, "MAGNA-SIRGAS")
    assert abs(e1 - e2) < 0.01 and abs(n1 - n2) < 0.01


def test_origen_desconocido_falla_claro():
    with pytest.raises(ValueError, match="Origen desconocido"):
        g.a_ctm12(0, 0, "ZONA-INVENTADA")


def test_area_de_uso():
    assert g.dentro_de_colombia(*PUNTOS["leticia"]) and g.dentro_de_colombia(*PUNTOS["san_andres"])
    assert not g.dentro_de_colombia(-3.70, 40.42)    # Madrid


# ── Punto base y precisión ──────────────────────────────────────────────────────────────────────────────

def test_paso_float32_cerca_de_5_millones_es_medio_metro():
    assert g.paso_float32(4_880_692.0) == 0.5
    assert g.paso_float32(250.0) < 3.1e-5


def test_float32_pierde_decimetros_en_oficial_y_no_en_local():
    rng = np.random.default_rng(7)
    e = 4_880_692.0 + rng.uniform(-300, 300, 500)
    n = 2_066_175.0 + rng.uniform(-300, 300, 500)
    oficial = np.column_stack([e, n])
    pb = g.punto_base_desde(e, n)
    x, y, _ = pb.a_local(e, n)
    assert g.error_float32(oficial) > 0.05            # hasta 0,25 m de error en float32
    assert g.error_float32(np.column_stack([x, y])) < 3e-5   # < 0,03 mm en local


def test_punto_base_centro_del_envolvente_redondeado():
    pb = g.punto_base_desde([100.4, 200.6, 300.2], [10.0, 20.0, 1000.0], [5.7, 3.2, 9.9])
    assert (pb.e0, pb.n0, pb.h0) == (200.0, 505.0, 3.0)


@pytest.mark.parametrize("rot", [0.0, 0.3, -1.2, math.pi])
@pytest.mark.parametrize("escala", [1.0, 0.99987])
def test_ida_y_vuelta_local_menor_a_un_milimetro(rot, escala):
    rng = np.random.default_rng(1)
    e = 4_803_779.03 + rng.uniform(-5000, 5000, 200)
    n = 2_770_137.57 + rng.uniform(-5000, 5000, 200)
    h = rng.uniform(0, 80, 200)
    pb = g.PuntoBase(4_803_779.0, 2_770_138.0, 0.0, rotacion_rad=rot, escala=escala)
    e2, n2, h2 = pb.a_oficial(*pb.a_local(e, n, h))
    assert max(np.max(np.abs(e2 - e)), np.max(np.abs(n2 - n)), np.max(np.abs(h2 - h))) < 1e-3


def test_rotacion_convencion_ifc():
    # Eje x local girado 90°: un punto en x=+10 local está 10 m al Norte del punto base.
    pb = g.PuntoBase(1000.0, 2000.0, rotacion_rad=math.pi / 2)
    e, n, _ = pb.a_oficial(10.0, 0.0)
    assert e == pytest.approx(1000.0, abs=1e-9) and n == pytest.approx(2010.0, abs=1e-9)
    assert pb.eje_x == pytest.approx((0.0, 1.0), abs=1e-12)


def test_punto_base_rechaza_otro_epsg_y_escala_invalida():
    with pytest.raises(ValueError):
        g.PuntoBase(0, 0, epsg=3116)
    with pytest.raises(ValueError):
        g.PuntoBase(0, 0, escala=0)
    with pytest.raises(ValueError):
        g.PuntoBase(float("nan"), 0)


def test_dict_ida_y_vuelta():
    pb = g.PuntoBase(4_880_692.0, 2_066_175.0, 2600.0, 0.01, 1.0, fuente="levantamiento")
    assert g.PuntoBase.desde_dict(pb.como_dict()) == pb


def test_proyectar_a_local_desde_wgs84():
    pts = [(-74.0758, 4.5981, 2600.0), (-74.0740, 4.6000, 2610.0)]
    loc, pb = g.proyectar_a_local(pts)
    assert np.all(np.abs(loc[:, :2]) < 300) and np.all(loc[:, 2] >= 0)
    assert pb.h0 == 2600.0


def test_proyectar_lat_lon_invertidos_falla():
    with pytest.raises(ValueError, match="invertidas"):
        g.proyectar_a_local([(4.5981, -74.0758)])   # lat como lon: fuera del dominio de la proyección
