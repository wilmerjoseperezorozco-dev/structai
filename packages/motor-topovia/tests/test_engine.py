"""
Tests para Motor TopoVía — Poligonales, Volúmenes, Curvas, Pavimentos
"""
import math
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    Vertice, SeccionTransversal, Punto,
    OrdenPoligonal, MetodoCompensacion,
)
from src.engine import (
    calcular_poligonal_cerrada,
    calcular_curva_horizontal,
    puntos_replanteo_curva,
    radio_minimo_invias,
    calcular_volumenes,
    disenar_pavimento_flexible,
    cbr_a_mr,
    gms_a_decimal,
    decimal_a_gms,
    azimut_a_rumbo,
)


# ═══ POLIGONALES ═══

class TestPoligonalCerrada:
    """Poligonal cerrada de 4 vértices — caso conocido."""

    @pytest.fixture
    def poligonal_4_vertices(self):
        vertices = [
            Vertice(id="A", angulo_horizontal=90.0, distancia_al_siguiente=100.0),
            Vertice(id="B", angulo_horizontal=90.0, distancia_al_siguiente=100.0),
            Vertice(id="C", angulo_horizontal=90.0, distancia_al_siguiente=100.0),
            Vertice(id="D", angulo_horizontal=90.0, distancia_al_siguiente=100.0),
        ]
        return vertices

    def test_cierre_angular_perfecto(self, poligonal_4_vertices):
        resultado = calcular_poligonal_cerrada(
            vertices=poligonal_4_vertices,
            azimut_inicial=0.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
        )
        assert resultado.suma_angulos_teorica == 360.0
        assert resultado.suma_angulos_observados == 360.0
        assert resultado.error_angular == pytest.approx(0.0, abs=0.1)
        assert resultado.cumple_angular is True

    def test_cierre_lineal_perfecto(self, poligonal_4_vertices):
        resultado = calcular_poligonal_cerrada(
            vertices=poligonal_4_vertices,
            azimut_inicial=0.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
        )
        assert resultado.error_lineal == pytest.approx(0.0, abs=0.001)
        assert resultado.cumple_lineal is True

    def test_coordenadas_cuadrado(self, poligonal_4_vertices):
        resultado = calcular_poligonal_cerrada(
            vertices=poligonal_4_vertices,
            azimut_inicial=0.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
        )
        coords = resultado.coordenadas_finales
        assert len(coords) == 4
        # A: (1000000, 1000000)
        assert coords[0].norte == pytest.approx(1000000.0, abs=0.01)
        assert coords[0].este == pytest.approx(1000000.0, abs=0.01)
        # B: (1000100, 1000000) — azimut 0° → norte
        assert coords[1].norte == pytest.approx(1000100.0, abs=0.01)

    def test_perimetro(self, poligonal_4_vertices):
        resultado = calcular_poligonal_cerrada(
            vertices=poligonal_4_vertices,
            azimut_inicial=0.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
        )
        assert resultado.perimetro == pytest.approx(400.0, abs=0.01)

    def test_error_angular_con_desbalance(self):
        vertices = [
            Vertice(id="A", angulo_horizontal=90.01, distancia_al_siguiente=100.0),
            Vertice(id="B", angulo_horizontal=89.99, distancia_al_siguiente=100.0),
            Vertice(id="C", angulo_horizontal=90.02, distancia_al_siguiente=100.0),
            Vertice(id="D", angulo_horizontal=90.01, distancia_al_siguiente=100.0),
        ]
        resultado = calcular_poligonal_cerrada(
            vertices=vertices,
            azimut_inicial=0.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
            orden=OrdenPoligonal.TOPOGRAFICO,
        )
        # Suma = 360.03° → error = 0.03° = 108"
        assert resultado.error_angular == pytest.approx(108.0, abs=1.0)

    def test_metodo_transito(self, poligonal_4_vertices):
        resultado = calcular_poligonal_cerrada(
            vertices=poligonal_4_vertices,
            azimut_inicial=45.0,
            norte_inicial=1000000.0,
            este_inicial=1000000.0,
            metodo=MetodoCompensacion.TRANSITO,
        )
        assert resultado.metodo_compensacion == MetodoCompensacion.TRANSITO
        assert resultado.error_lineal == pytest.approx(0.0, abs=0.01)


# ═══ CURVAS HORIZONTALES ═══

class TestCurvaHorizontal:

    def test_curva_90_grados(self):
        curva = calcular_curva_horizontal(
            radio=100.0,
            deflexion_grados=90.0,
            pi_abscisa=500.0,
        )
        assert curva.tangente == pytest.approx(100.0, abs=0.1)
        assert curva.longitud == pytest.approx(100 * math.pi / 2, abs=0.1)
        assert curva.pc_abscisa == pytest.approx(400.0, abs=0.1)
        assert curva.cuerda_larga == pytest.approx(100 * math.sqrt(2), abs=0.1)

    def test_radio_minimo_invias_80kmh(self):
        r_min = radio_minimo_invias(80, peralte_max=0.08)
        assert 225 < r_min < 260

    def test_puntos_replanteo(self):
        curva = calcular_curva_horizontal(
            radio=200.0,
            deflexion_grados=60.0,
            pi_abscisa=1000.0,
        )
        puntos = puntos_replanteo_curva(curva, intervalo=20.0)
        assert len(puntos) > 0
        assert puntos[0][1] == pytest.approx(0.0, abs=0.001)
        assert puntos[-1][0] == pytest.approx(curva.pt_abscisa, abs=0.1)


# ═══ VOLÚMENES ═══

class TestVolumenes:

    def test_volumen_corte_uniforme(self):
        s1 = SeccionTransversal(
            abscisa=0.0,
            puntos=[(-5, 2), (0, 2), (5, 2)],
            cota_eje_terreno=100.0,
        )
        s2 = SeccionTransversal(
            abscisa=20.0,
            puntos=[(-5, 2), (0, 2), (5, 2)],
            cota_eje_terreno=100.0,
        )
        vols, diagrama = calcular_volumenes([s1, s2])
        assert len(vols) == 1
        # Área = 10m × 2m = 20 m², Vol = 20m × 20m² = 400 m³
        assert vols[0].volumen_corte == pytest.approx(400.0, rel=0.1)

    def test_diagrama_masas_acumulado(self):
        secciones = [
            SeccionTransversal(abscisa=i * 20.0, puntos=[(-5, 1), (0, 1), (5, 1)], cota_eje_terreno=100.0)
            for i in range(4)
        ]
        _, diagrama = calcular_volumenes(secciones)
        assert len(diagrama) == 4
        assert diagrama[0].ordenada == 0.0
        assert diagrama[-1].volumen_corte_acumulado > 0


# ═══ PAVIMENTOS ═══

class TestPavimentos:

    def test_cbr_a_mr(self):
        mr = cbr_a_mr(5.0)
        assert 6000 < mr < 9000

    def test_diseno_pavimento_bajo_transito(self):
        resultado = disenar_pavimento_flexible(cbr=5.0, w18=100_000)
        assert resultado.cumple is True
        assert resultado.espesor_carpeta_cm >= 5.0
        assert resultado.sn_proporcionado >= resultado.sn_requerido

    def test_diseno_pavimento_alto_transito(self):
        resultado = disenar_pavimento_flexible(
            cbr=3.0, w18=5_000_000, confiabilidad=0.95,
        )
        assert resultado.cumple is True
        assert resultado.espesor_carpeta_cm >= 9.0


# ═══ UTILIDADES ═══

class TestUtilidades:

    def test_gms_a_decimal(self):
        assert gms_a_decimal(45, 30, 0) == pytest.approx(45.5, abs=0.001)

    def test_decimal_a_gms(self):
        g, m, s = decimal_a_gms(45.5)
        assert g == 45
        assert m == 30
        assert s == pytest.approx(0.0, abs=0.1)

    def test_azimut_a_rumbo_ne(self):
        assert "N" in azimut_a_rumbo(45.0)
        assert "E" in azimut_a_rumbo(45.0)

    def test_azimut_a_rumbo_sw(self):
        assert "S" in azimut_a_rumbo(225.0)
        assert "W" in azimut_a_rumbo(225.0)
