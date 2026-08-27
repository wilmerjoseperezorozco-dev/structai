"""
Descomposición de consultas compuestas (issue #30) — pruebas baratas, sin
llamadas reales a Groq/OpenAI ni a Supabase, en el mismo espíritu que
test_rag_chunk_size_guard.py: cubren la lógica determinística propia
(_fusionar_candidatos) y las guardas de validación de _descomponer_pregunta
(_llamar_llm_con_respaldo se reemplaza con un doble de prueba) — no la
capacidad de juicio del LLM en sí, que ya se verifica de forma real en
test_rag_nsr10_regresion.py::C-factor-phi-traccion-090 (el caso real que
motivó este issue, ver project_structai_ragas_baseline en memoria).

Ejecutar: pytest apps/api/tests/test_query_decomposition.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

# rag_multi_norma.py lee credenciales de os.environ a nivel de módulo (crea el
# cliente de Supabase al importar) -- hace falta cargar el .env antes del
# import aunque estas pruebas no llamen a Supabase de verdad, mismo patrón
# que test_rag_nsr10_regresion.py.
load_dotenv(API_DIR / ".env")

import rag_multi_norma as rmn  # noqa: E402
from rag_multi_norma import ChunkResult, _descomponer_pregunta, _fusionar_candidatos  # noqa: E402


def _chunk(chunk_id: str, score: float) -> ChunkResult:
    return ChunkResult(chunk_id=chunk_id, norma="NSR-10 Título C", seccion="C.1", contenido="texto", score=score)


class TestFusionarCandidatos:
    def test_deduplica_quedandose_con_el_score_mas_alto(self) -> None:
        # Arrange: el mismo chunk aparece en 2 sub-búsquedas con scores distintos
        por_pregunta = [
            [_chunk("A", 0.10), _chunk("B", 0.05)],
            [_chunk("A", 0.30), _chunk("C", 0.02)],
        ]

        # Act
        resultado = _fusionar_candidatos(por_pregunta, limite=40)

        # Assert
        ids_y_scores = {c.chunk_id: c.score for c in resultado}
        assert ids_y_scores == {"A": 0.30, "B": 0.05, "C": 0.02}

    def test_ordena_por_score_descendente(self) -> None:
        por_pregunta = [[_chunk("bajo", 0.01), _chunk("alto", 0.9), _chunk("medio", 0.5)]]

        resultado = _fusionar_candidatos(por_pregunta)

        assert [c.chunk_id for c in resultado] == ["alto", "medio", "bajo"]

    def test_trunca_al_limite_pedido(self) -> None:
        por_pregunta = [[_chunk(str(i), float(i)) for i in range(50)]]

        resultado = _fusionar_candidatos(por_pregunta, limite=10)

        assert len(resultado) == 10
        # Se queda con los de mayor score, no los primeros en orden de inserción
        assert resultado[0].chunk_id == "49"

    def test_una_sola_pregunta_sin_duplicados_no_pierde_candidatos(self) -> None:
        # Caso normal (sin descomposición): una sola lista, debe comportarse
        # como un simple sort + cap, igual que antes de este cambio.
        chunks = [_chunk("x", 0.2), _chunk("y", 0.8)]

        resultado = _fusionar_candidatos([chunks], limite=40)

        assert len(resultado) == 2
        assert resultado[0].chunk_id == "y"


class TestDescomponerPregunta:
    def test_pregunta_simple_no_se_modifica_si_llm_no_sugiere_separar(self, monkeypatch) -> None:
        pregunta = "Cual es la resistencia minima a la compresion f'c que exige la NSR-10?"
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: '{"subpreguntas": []}')

        resultado = _descomponer_pregunta(pregunta)

        assert resultado == [pregunta]

    def test_pregunta_compuesta_se_separa_cuando_el_llm_devuelve_json_valido(self, monkeypatch) -> None:
        respuesta_llm = (
            '{"subpreguntas": ['
            '"Cual es el factor phi de reduccion de resistencia para traccion?", '
            '"Cual es el factor phi de reduccion de resistencia para cortante?"'
            ']}'
        )
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: respuesta_llm)

        resultado = _descomponer_pregunta("factores phi para traccion y cortante")

        assert len(resultado) == 2
        assert "traccion" in resultado[0].lower()
        assert "cortante" in resultado[1].lower()

    def test_json_envuelto_en_markdown_se_extrae_igual(self, monkeypatch) -> None:
        # Los LLMs a veces ignoran "sin texto adicional" y envuelven la
        # respuesta en ```json ... ``` -- _descomponer_pregunta debe tolerarlo.
        respuesta_llm = (
            '```json\n{"subpreguntas": ["Pregunta autocontenida uno", '
            '"Pregunta autocontenida dos"]}\n```'
        )
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: respuesta_llm)

        resultado = _descomponer_pregunta("pregunta compuesta cualquiera")

        assert len(resultado) == 2

    def test_json_malformado_degrada_a_pregunta_original(self, monkeypatch) -> None:
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: "esto no es JSON en absoluto")

        resultado = _descomponer_pregunta("una pregunta cualquiera")

        assert resultado == ["una pregunta cualquiera"]

    def test_demasiadas_subpreguntas_degrada_a_pregunta_original(self, monkeypatch) -> None:
        # Guarda de seguridad: más de _MAX_SUBPREGUNTAS sugiere que el LLM
        # se desvió de la instrucción -- mejor no dividir que dividir mal.
        respuesta_llm = '{"subpreguntas": ["uno bastante largo", "dos bastante largo", "tres bastante largo", "cuatro bastante largo"]}'
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: respuesta_llm)

        resultado = _descomponer_pregunta("pregunta original")

        assert resultado == ["pregunta original"]

    def test_subpregunta_demasiado_corta_degrada_a_pregunta_original(self, monkeypatch) -> None:
        # Guarda de seguridad: una sub-pregunta trivial ("y cortante?") no es
        # autocontenida -- mejor no dividir que perder contexto real.
        respuesta_llm = '{"subpreguntas": ["pregunta completa y larga de verdad", "corta"]}'
        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", lambda *a, **k: respuesta_llm)

        resultado = _descomponer_pregunta("pregunta original")

        assert resultado == ["pregunta original"]

    def test_fallo_de_red_degrada_a_pregunta_original_sin_lanzar(self, monkeypatch) -> None:
        def _falla(*args, **kwargs):
            raise rmn.RespuestaIAIndisponibleError("Groq y OpenAI no disponibles")

        monkeypatch.setattr(rmn, "_llamar_llm_con_respaldo", _falla)

        resultado = _descomponer_pregunta("pregunta original")

        assert resultado == ["pregunta original"]
