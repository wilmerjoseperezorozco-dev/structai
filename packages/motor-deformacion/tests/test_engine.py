"""Tests de integración del MotorDeformacion (engine.py) — geometría + teoría
de vigas/columnas + incertidumbre combinadas en un ElementoEstructural."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import MotorDeformacion
from src.models import CargaAplicada, CondicionApoyo, ElementoEstructural, TipoCarga, TipoElemento
from src.geometry import seccion_rectangular
from src.catalogue import (
    MATERIALES, ejemplo_viga_acero_simplemente_apoyada,
    ejemplo_viga_concreto_cantilever, ejemplo_columna_acero,
)
from src.clasificador import elemento_desde_deteccion, estimar_longitud_desde_bbox


def test_cantilever_concreto_esfuerzo_flexion_correcto():
    """Regresión: el motor evaluaba antes el momento en el punto de deflexión
    máxima (la punta libre, M=0) en vez del punto de momento máximo (el
    empotramiento) — daba esfuerzo=0 para cualquier voladizo."""
    r = ejemplo_viga_concreto_cantilever()
    # M_max = wL^2/2 = 12000*2.5^2/2 = 37500 N·m ; S = b*h^2/6 = 0.3*0.5^2/6 = 0.0125 m^3
    # esfuerzo = 37500/0.0125 = 3.0e6 Pa
    assert abs(r.esfuerzo_flexion_max - 3.0e6) / 3.0e6 < 1e-6


def test_viga_acero_cumple_deflexion_y_esfuerzo():
    r = ejemplo_viga_acero_simplemente_apoyada()
    assert r.cumple_deflexion
    assert r.cumple_esfuerzo
    assert r.factor_seguridad > 1.0
    assert r.deflexion_max > 0
    assert r.esfuerzo_flexion_max > 0


def test_monte_carlo_produce_intervalo_creciente_p05_mean_p95():
    r = ejemplo_viga_acero_simplemente_apoyada()
    assert r.esfuerzo_p05 < r.esfuerzo_mean < r.esfuerzo_p95
    assert r.deflexion_p05 < r.deflexion_mean < r.deflexion_p95
    assert r.deflexion_std > 0
    assert r.esfuerzo_std > 0


def test_indice_confiabilidad_es_finito_y_positivo_para_diseno_seguro():
    r = ejemplo_viga_acero_simplemente_apoyada()
    assert r.indice_confiabilidad > 0
    assert 0 <= r.probabilidad_falla <= 1


def test_columna_acero_analisis_completo():
    r = ejemplo_columna_acero()
    assert r.tipo_analisis == "pandeo"
    assert r.carga_critica_pandeo is not None
    assert r.carga_critica_pandeo > 450_000  # debe soportar la carga aplicada
    assert r.factor_seguridad > 1.0
    assert r.cumple_esfuerzo


def test_deflexion_no_cumple_cuando_excede_limite():
    """Viga muy esbelta con carga alta -> debe fallar el chequeo de servicio L/360."""
    elemento = ElementoEstructural(
        id="V-FALLA", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["ACERO_A36"],
        seccion=seccion_rectangular(b=0.05, h=0.08),
        longitud=8.0, condicion_apoyo=CondicionApoyo.SIMPLE,
    )
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=6_000)]
    r = MotorDeformacion().analizar_viga(elemento, cargas, run_montecarlo=False)
    assert not r.cumple_deflexion


def test_superposicion_multiples_cargas_en_analizar_viga():
    elemento = ElementoEstructural(
        id="V-MULTI", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["ACERO_A36"],
        seccion=seccion_rectangular(b=0.15, h=0.30),
        longitud=5.0, condicion_apoyo=CondicionApoyo.SIMPLE,
    )
    carga_unica = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=4_000)]
    cargas_combinadas = carga_unica + [
        CargaAplicada(tipo=TipoCarga.PUNTUAL, magnitud=8_000, posicion=0.5)
    ]
    motor = MotorDeformacion()
    r_unica = motor.analizar_viga(elemento, carga_unica, run_montecarlo=False)
    r_combo = motor.analizar_viga(elemento, cargas_combinadas, run_montecarlo=False)
    assert r_combo.deflexion_max > r_unica.deflexion_max
    assert r_combo.momento_max > r_unica.momento_max


def test_viga_empotrada_apoyada_usa_solver_general():
    """Condición EMPOTRADA_APOYADA no tiene fórmula cerrada en este motor —
    debe resolverse vía el solver BVP general sin lanzar excepción."""
    elemento = ElementoEstructural(
        id="V-PROPPED", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["ACERO_A36"],
        seccion=seccion_rectangular(b=0.2, h=0.35),
        longitud=6.0, condicion_apoyo=CondicionApoyo.EMPOTRADA_APOYADA,
    )
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=5_000)]
    r = MotorDeformacion().analizar_viga(elemento, cargas, run_montecarlo=False)
    assert r.deflexion_max > 0
    assert r.momento_max > 0


def test_pipeline_clasificacion_a_deformacion():
    """clase detectada por /detect (YOLO) -> ElementoEstructural -> análisis."""
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=10_000, cov_carga=0.15)]
    r = MotorDeformacion().analizar_desde_deteccion("viga", cargas, longitud=5.0, run_montecarlo=False)
    assert r is not None
    assert r.deflexion_max > 0


def test_pipeline_clasificacion_clase_no_analizable_retorna_none():
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=1_000)]
    r = MotorDeformacion().analizar_desde_deteccion("excavacion", cargas)
    assert r is None


def test_elemento_desde_deteccion_columna_usa_condicion_correcta():
    el = elemento_desde_deteccion("columna")
    assert el is not None
    assert el.tipo_elemento == TipoElemento.COLUMNA
    assert el.condicion_apoyo == CondicionApoyo.EMPOTRADA_EMPOTRADA


def test_estimar_longitud_desde_bbox():
    # bbox ocupa el 50% de la altura de una imagen de referencia de 3.0 m de alto
    longitud = estimar_longitud_desde_bbox([0.1, 0.25, 0.4, 0.75], alto_imagen_m=3.0, alto_imagen_px=1000)
    assert abs(longitud - 1.5) < 1e-6


def test_resultado_usa_tipos_nativos_python_no_numpy():
    """Regresión: numpy.float64/numpy.bool_ sin convertir rompían la
    serialización JSON en el endpoint FastAPI /deform (json.dumps no sabe
    serializar numpy.bool_). Todo campo expuesto debe ser tipo nativo."""
    import json
    for r in (ejemplo_viga_acero_simplemente_apoyada(), ejemplo_viga_concreto_cantilever(), ejemplo_columna_acero()):
        assert type(r.deflexion_max) is float
        assert type(r.momento_max) is float
        assert type(r.cortante_max) is float
        assert type(r.cumple_deflexion) is bool
        assert type(r.cumple_esfuerzo) is bool
        json.dumps({
            "deflexion_max": r.deflexion_max, "cumple_deflexion": r.cumple_deflexion,
            "cumple_esfuerzo": r.cumple_esfuerzo, "momento_max": r.momento_max,
        })


def test_viga_empotrada_apoyada_tipos_nativos():
    """La condición EMPOTRADA_APOYADA usa el solver BVP (resolver_general) —
    ruta de código separada de las fórmulas cerradas, se verifica aparte."""
    elemento = ElementoEstructural(
        id="V-PROPPED-TIPOS", tipo_elemento=TipoElemento.VIGA,
        material=MATERIALES["ACERO_A36"],
        seccion=seccion_rectangular(b=0.2, h=0.35),
        longitud=6.0, condicion_apoyo=CondicionApoyo.EMPOTRADA_APOYADA,
    )
    cargas = [CargaAplicada(tipo=TipoCarga.DISTRIBUIDA_UNIFORME, magnitud=5_000)]
    r = MotorDeformacion().analizar_viga(elemento, cargas, run_montecarlo=False)
    assert type(r.deflexion_max) is float
    assert type(r.momento_max) is float
    assert type(r.cumple_deflexion) is bool
