"""
Unit tests de _detectar_posible_alucinacion_numerica (issue #31, primer
paso de auto-evaluación barata post-generación) — completamente offline,
sin llamadas a Groq/OpenAI ni a Supabase, para poder correr en cada CI
sin costo ni latencia, a diferencia de test_rag_nsr10_regresion.py.

Contexto real que motivó esta función (2026-09-08, verificación de las
113 preguntas nuevas del dataset RAGAS contra ask() real): 2 alucinaciones
confirmadas donde el LLM citó un número/cifra que NO estaba en el
contexto recuperado — ver project_structai_nsr10_inventario_titulos.md
en memoria privada del usuario para el detalle completo de cada caso.
Estos tests reproducen esos 2 patrones reales (con datos sintéticos, no
llamando a producción) más los casos límite que ya se descubrieron al
construir el heurístico (numerales de norma tipo "A.3.3-1" no deben
contarse como número inventado).

Ejecutar: pytest apps/api/tests/test_rag_deteccion_alucinacion_numerica.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

# rag_multi_norma.py lee credenciales de os.environ a nivel de módulo (mismo
# motivo documentado en test_rag_nsr10_regresion.py) -- hay que cargar el
# .env ANTES de importar, aunque este archivo no haga ninguna llamada real
# a Supabase/Groq (los tests de abajo son 100% offline).
load_dotenv(API_DIR / ".env")

from rag_multi_norma import _detectar_posible_alucinacion_numerica  # noqa: E402


def test_numero_presente_en_contexto_no_se_marca():
    contexto = "[H — H.9.3.4] Deformación potencial de hidrocolapso > 0.20 se clasifica como muy severa."
    respuesta = "Según el Título H, un suelo se clasifica como muy severo cuando épsilon_w supera 0.20."
    assert _detectar_posible_alucinacion_numerica(contexto, respuesta) == []


def test_numero_fabricado_no_presente_en_contexto_se_marca():
    # Reproduce el patrón real de COLOQ2-fyt-confinamiento-700MPa: el LLM
    # citó "0.0018 x 200,000 = 360 MPa" y un artículo (C.10.13.8.7) que no
    # tenían relación con el valor real (fyt <= 700 MPa) del contexto.
    contexto = "[C — C.21.6.4.4] El valor de fyt usado para calcular la cuantía del refuerzo de confinamiento no debe exceder 700 MPa."
    respuesta = "La resistencia a la fluencia correspondiente es de 360 MPa (0.0018 x 200,000)."
    sospechosos = _detectar_posible_alucinacion_numerica(contexto, respuesta)
    assert "360 MPa" in sospechosos
    assert "200,000" in sospechosos or "200.000" in sospechosos


def test_numeral_de_norma_no_se_confunde_con_numero_inventado():
    # "A.3.3-1" es una referencia a la ecuación, no un número fabricado --
    # no debe aparecer en la lista de sospechosos aunque el contexto no
    # repita el numeral literalmente en ese formato.
    contexto = "[A — A.3.3] R = phi_a * phi_p * phi_r * R0"
    respuesta = "Según la ecuación A.3.3-1 del Título A, R = phi_a * phi_p * phi_r * R0."
    assert _detectar_posible_alucinacion_numerica(contexto, respuesta) == []


def test_numero_con_formato_distinto_coma_vs_punto_no_se_marca():
    # El mismo valor con separador decimal distinto (coma vs. punto) no debe
    # marcarse como sospechoso -- es un problema de formato, no de contenido.
    contexto = "[D — D.2.5] La resistencia mínima del mortero de relleno es 12,5 MPa."
    respuesta = "Según el Título D, la resistencia mínima del mortero de relleno es 12.5 MPa."
    assert _detectar_posible_alucinacion_numerica(contexto, respuesta) == []


def test_respuesta_sin_numeros_no_marca_nada():
    contexto = "[G — G.12.11.1.1] No se permiten uniones clavadas en guadua."
    respuesta = "No, las uniones clavadas están prohibidas en guadua porque los clavos inducen grietas longitudinales."
    assert _detectar_posible_alucinacion_numerica(contexto, respuesta) == []


def test_multiples_numeros_fabricados_se_marcan_todos():
    contexto = "[H — H.9.1] Los minerales activos son montmorilonita, vermiculita y haloisita."
    respuesta = "El 45.5% de las arcillas del país contienen estos minerales, según un estudio de 1998."
    sospechosos = _detectar_posible_alucinacion_numerica(contexto, respuesta)
    assert "45.5%" in sospechosos
