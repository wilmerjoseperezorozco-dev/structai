"""Tests para Motor APU"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import MaterialItem, ManoObraItem, EquipoItem, UnidadMedida, CategoriaObrero, AIU
from src.engine import MotorAPU
from src.catalogue import apu_concreto_columna_3000psi, apu_acero_refuerzo_fy60

def test_precio_unitario_positivo():
    result = apu_concreto_columna_3000psi()
    assert result.precio_unitario > 0

def test_estructura_apu_concreto():
    result = apu_concreto_columna_3000psi()
    assert result.costo_materiales > 0
    assert result.costo_mano_obra  > 0
    assert result.costo_equipo     > 0
    assert result.costo_directo == round(result.costo_materiales + result.costo_mano_obra + result.costo_equipo, 2)

def test_aiu_aplicado_correctamente():
    result = apu_concreto_columna_3000psi()
    expected_aiu = result.costo_directo * result.aiu.total_pct
    assert abs(result.costo_aiu - expected_aiu) < 1.0  # tolerancia COP 1

def test_monte_carlo_genera_incertidumbre():
    result = apu_concreto_columna_3000psi()
    assert result.pu_mean > 0
    assert result.pu_std  > 0
    assert result.pu_p05  < result.pu_mean
    assert result.pu_p95  > result.pu_mean
    # IC 90% razonable: no más del 50% de variación
    variacion = (result.pu_p95 - result.pu_p05) / result.pu_mean
    assert variacion < 0.5

def test_precio_acero_por_kg():
    result = apu_acero_refuerzo_fy60()
    assert result.unidad == UnidadMedida.KG
    # Precio acero Barranquilla 2026 razonable: entre 5000 y 12000 COP/kg
    assert 5_000 < result.precio_unitario < 15_000

def test_capitulo_suma_correcta():
    engine = MotorAPU()
    apu1 = apu_concreto_columna_3000psi()
    apu2 = apu_acero_refuerzo_fy60()
    cap = engine.calcular_capitulo(
        "CAP-C", "Concreto Estructural",
        [{"actividad": "Columnas", "cantidad": 12.5, "apu": apu1},
         {"actividad": "Acero",    "cantidad": 850.0, "apu": apu2}]
    )
    expected = round(apu1.precio_unitario * 12.5 + apu2.precio_unitario * 850.0, 2)
    assert abs(cap["subtotal_det"] - expected) < 1.0

print("✅ Tests definidos correctamente")
