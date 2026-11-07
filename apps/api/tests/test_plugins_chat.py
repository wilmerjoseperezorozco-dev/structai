"""Pruebas de los plugins determinísticos del chat (plugins_chat.py). No tocan red: el ONI y Supabase se simulan; los catálogos de motor-apu son archivos locales."""
from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR.parents[1] / "packages" / "construdata"))

import pytest

import plugins_chat as pc

ONI_TXT = " SEAS  YR   TOTAL   ANOM\n  DJF 2026  27.10  -0.20\n  JJA 2026  27.90   0.60\n  ASO 2026  28.50   1.20\n"


class _Resp:
    def __init__(self, data): self.data = data


class _Q:
    def __init__(self, data): self._d = data
    def select(self, *_): return self
    def order(self, *_): return self
    def execute(self): return _Resp(self._d)


class FakeSB:
    def __init__(self, rows, mods): self.t = {"normas_registro": rows, "normas_modificaciones": mods}
    def table(self, n): return _Q(self.t[n])


REGISTRO = [
    {"codigo": "LEY-80-1993", "nombre_completo": "Ley 80 de 1993 — Estatuto General de Contratación", "estado_vigencia": "vigente", "alcance_derogacion": None, "notas_vigencia": None, "fecha_expedicion": "1993-10-28"},
    {"codigo": "RES-0424-2001", "nombre_completo": "Resolución 0424 de 2001", "estado_vigencia": "derogada_total", "alcance_derogacion": "Derogada.", "notas_vigencia": None, "fecha_expedicion": "2001-01-01"},
    {"codigo": "RES-2743-2026", "nombre_completo": "Resolución 2743 de 2026 (INVIAS) — asunto sin confirmar", "estado_vigencia": "desconocido", "alcance_derogacion": None, "notas_vigencia": None, "fecha_expedicion": None},
    {"codigo": "NSR10-TITULO-A", "nombre_completo": "NSR-10 — Título A", "estado_vigencia": "vigente", "alcance_derogacion": None, "notas_vigencia": None, "fecha_expedicion": None},
    {"codigo": "NSR10-TITULO-B", "nombre_completo": "NSR-10 — Título B", "estado_vigencia": "vigente", "alcance_derogacion": None, "notas_vigencia": None, "fecha_expedicion": None},
]
MODS = [
    {"norma": "NSR-10", "decreto": "Decreto 092 de 2011", "fecha": "2011-01-17", "objeto": "Modifica el reglamento.", "estado_verificacion": "texto_verificado"},
    {"norma": "NSR-10", "decreto": "Decreto 1401 de 2023", "fecha": "2023-08-25", "objeto": "Mampostería.", "estado_verificacion": "resumen_web_sin_verificar"},
]


@pytest.fixture(autouse=True)
def _limpiar_cachés():
    pc._cache_oni.update({"t": 0.0, "v": None}); pc._cache_reg.update({"t": 0.0, "rows": [], "mods": []})
    yield


# ---- activación
@pytest.mark.parametrize("q,esperado", [("¿Qué pasa con el Fenómeno de El Niño en el Caribe?", True), ("lluvias por La Niña en Barranquilla", True), ("¿cuál es el ONI actual?", True),
                                        ("resistencia del concreto a 28 días", False), ("niñera", False)])
def test_activar_enso(q, esperado):
    assert pc.activar_enso(q) is esperado


@pytest.mark.parametrize("q,esperado", [("¿Sigue vigente la Ley 80 de 1993?", True), ("¿La NSR-10 fue modificada?", True), ("calcular espesor de losa", False)])
def test_activar_vigencia(q, esperado):
    assert pc.activar_vigencia(q) is esperado


@pytest.mark.parametrize("q,esperado", [("¿Es razonable pagar $35.000 por un saco de cemento?", True), ("me cobran 1.250.000 pesos por el m3 de concreto, ¿es caro?", True),
                                        ("el cemento cuesta 35 mil pesos, ¿es justo?", True), ("¿cuánto cuesta el cemento?", False), ("losa de 20 cm con 4 varillas", False)])
def test_activar_precio(q, esperado):
    assert pc.activar_precio(q) is esperado


@pytest.mark.parametrize("texto,valor", [("cuesta $35.000", 35000), ("35 mil pesos", 35000), ("1.250.000 pesos", 1250000), ("$3.5 millones", 3_500_000), ("$ 19000", 19000)])
def test_extraer_monto(texto, valor):
    assert pc._extraer_monto(texto)[0] == pytest.approx(valor)


@pytest.mark.parametrize("q,esperado", [("¿Qué insumos lleva la sub-base granular clase A?", True), ("composición de la actividad de afirmado", True), ("¿qué es un afirmado?", False)])
def test_activar_insumos(q, esperado):
    assert pc.activar_insumos(q) is esperado


# ---- ENSO
def test_oni_fase_y_cache():
    llamadas = []
    def desc(_u): llamadas.append(1); return ONI_TXT
    v = pc.oni_actual(desc); assert v["temporada"] == "ASO 2026" and v["oni"] == pytest.approx(1.2) and v["fase"] == "El Niño"
    pc.oni_actual(desc); assert len(llamadas) == 1  # caché


def test_oni_falla_no_lanza():
    def mal(_u): raise TimeoutError("sin red")
    assert pc.oni_actual(mal) is None


def test_enso_region_por_departamento_y_texto_sin_ruido():
    r = pc.ejecutar_enso("¿Cómo afecta El Niño al Atlántico?", descargar=lambda _u: ONI_TXT)
    assert "Caribe" in r.markdown and "El Niño" in r.markdown and "no mejoró" in r.markdown and r.seccion == "Caribe"


def test_enso_region_por_municipio():
    r = pc.ejecutar_enso("¿Y La Niña en Montería?", detectar_municipio=lambda _q: {"municipio": "MONTERIA", "departamento": "CÓRDOBA"}, descargar=lambda _u: ONI_TXT)
    assert r.seccion == "Caribe"


def test_enso_sin_region_muestra_las_cinco_y_sin_oni_lo_dice():
    def mal(_u): raise TimeoutError()
    r = pc.ejecutar_enso("háblame del fenómeno de La Niña", descargar=mal)
    assert "No pude consultar el ONI" in r.markdown and "Amazonía" in r.markdown and "Andina" in r.markdown and "no identifiqué su región" in r.markdown.lower()


# ---- vigencia
def test_vigencia_ley_y_estado():
    r = pc.ejecutar_vigencia("¿Sigue vigente la Ley 80 de 1993?", FakeSB(REGISTRO, MODS))
    assert r and "vigente" in r.markdown and "Estatuto General" in r.markdown


def test_vigencia_derogada_y_desconocida():
    assert "derogada total" in pc.ejecutar_vigencia("¿está vigente la resolución 424 de 2001?", FakeSB(REGISTRO, MODS)).markdown
    assert "no confirmado" in pc.ejecutar_vigencia("¿rige la resolución 2743 de 2026?", FakeSB(REGISTRO, MODS)).markdown


def test_vigencia_nsr10_cadena_con_verificacion():
    md = pc.ejecutar_vigencia("¿la NSR-10 fue modificada?", FakeSB(REGISTRO, MODS)).markdown
    assert "1 con texto verificado" in md and "Decreto 092 de 2011" in md and "resumen web, sin verificar" in md and "no sustituye" in md
    assert md.count("**NSR-10** (registro por títulos)") == 1  # los títulos se colapsan


def test_vigencia_norma_desconocida_devuelve_none_y_sin_sb_tambien():
    assert pc.ejecutar_vigencia("¿está vigente el decreto 9999 de 2030?", FakeSB(REGISTRO, MODS)) is None
    assert pc.ejecutar_vigencia("¿vigente la ley 80?", None) is None


def test_vigencia_ley_80_no_confunde_ley_800():
    assert pc.ejecutar_vigencia("¿sigue vigente la ley 800?", FakeSB(REGISTRO, MODS)) is None


# ---- precio (usa el catálogo local de motor-apu)
def test_precio_con_referencia_muestra_unidad_y_limites():
    r = pc.ejecutar_precio("¿Es razonable pagar $19.000 por cemento gris?")
    assert r and "Cemento Gris" in r.markdown and "unidad" in r.markdown.lower() and "tamizaje" in r.markdown.lower() and r.fecha_datos == "2026-08-08"


def test_precio_sin_referencia_no_inventa():
    r = pc.ejecutar_precio("¿Es razonable pagar $5.000 por bulldozer renta por hora?")
    assert r and "no encontré" in r.markdown.lower()


# ---- insumos
def test_insumos_por_descripcion():
    r = pc.ejecutar_insumos("¿Qué insumos lleva la sub-base granular clase A?")
    assert r and "320" in r.markdown and "sin cantidades" in r.markdown


def test_insumos_sugerencia_por_vecinos_si_se_nombran_insumos():
    r = pc.ejecutar_insumos("tengo en mi APU soldador, oficial y equipo de oxicorte, ¿qué insumos suelen acompañarlos?")
    assert r is None or r.nombre in {"recomendador_insumos", "insumos_actividad"}


# ---- orquestación
def test_aplicar_no_cambia_si_nada_se_activa_y_es_idempotente_e_inmutable():
    base = {"respuesta": "texto", "fuentes": [{"norma": "NSR-10", "seccion": "A.1", "score": 0.9}], "normas_citadas": ["NSR-10"]}
    assert pc.aplicar(base, "espesor de una losa", FakeSB(REGISTRO, MODS)) is base
    out = pc.aplicar(base, "¿Sigue vigente la Ley 80 de 1993?", FakeSB(REGISTRO, MODS))
    assert out is not base and base["respuesta"] == "texto" and "Datos verificados por StructAI" in out["respuesta"]
    assert out["plugins_usados"] == ["vigencia_normas"] and out["fuentes"][0]["norma"].startswith("Registro de vigencia") and out["fuentes"][-1]["norma"] == "NSR-10"
    assert pc.aplicar(out, "¿Sigue vigente la Ley 80 de 1993?", FakeSB(REGISTRO, MODS)) is out


def test_un_plugin_que_falla_no_rompe_a_los_demas(monkeypatch):
    def bomba(*_a, **_k): raise RuntimeError("falla simulada")
    monkeypatch.setattr(pc, "ejecutar_enso", bomba)
    out = pc.ejecutar_plugins("¿La Niña y la vigencia de la ley 80?", FakeSB(REGISTRO, MODS))
    assert [p.nombre for p in out] == ["vigencia_normas"]


# ---- regresiones de los defectos encontrados al probar con datos reales (2026-11-08)
def test_insumos_respeta_la_clase_a_no_devuelve_b():
    r = pc.ejecutar_insumos("¿Qué insumos lleva la sub-base granular clase A?")
    assert r and "CLASE A" in r.markdown.upper() and "CLASE B" not in r.markdown.upper()


def test_insumos_clase_inexistente_no_inventa():
    assert pc.ejecutar_insumos("¿Qué insumos lleva la sub-base granular clase D?") is None


def test_precio_muy_lejos_de_la_mediana_no_se_llama_consistente():
    r = pc.ejecutar_precio("Me cobran $38.000 por un saco de cemento gris, ¿es razonable?")
    assert r and "no concluyente" in r.markdown and "**consistente**" not in r.markdown


def test_nota_de_vigencia_no_filtra_detalles_internos():
    nota = "Vigente pero modificada por la Ley 1150 de 2007. Fuente real: Gestor Normativo. 142 chunks reales extraidos por scripts/extract_leyes_gerencia.py"
    limpia = pc._limpiar_nota(nota)
    assert "scripts/" not in limpia and "chunks" not in limpia and limpia.startswith("Vigente pero modificada")


# ---- modo degradado cuando el modelo de lenguaje no está disponible
def test_respuesta_degradada_devuelve_solo_plugins_y_marca_degradado():
    r = pc.respuesta_degradada("¿Sigue vigente la Ley 80 de 1993?", FakeSB(REGISTRO, MODS))
    assert r and r["degradado"] is True and pc.MENSAJE_DEGRADADO in r["respuesta"] and "Ley 80" in r["respuesta"] and r["plugins_usados"] == ["vigencia_normas"]


def test_respuesta_degradada_none_si_ningun_plugin_aplica():
    assert pc.respuesta_degradada("espesor de una losa de 5 m de luz", FakeSB(REGISTRO, MODS)) is None


# ---- regresión (2026-11-08): el saco de 50 kg debe emparejar con «Cemento Gris 50Kl», no con el ítem «Cemento Gris» en kg de unidades mezcladas
def test_precio_saco_de_50_kg_empareja_el_item_correcto():
    r = pc.ejecutar_precio("¿Es razonable pagar $38.000 por un saco de cemento gris de 50 kg?")
    assert r and "50Kl" in r.markdown and "**consistente**" in r.markdown and "no concluyente" not in r.markdown


def test_precio_ambiguo_advierte_dispersion_y_muestra_alternativas():
    md = pc.ejecutar_precio("¿Es razonable pagar $38.000 por un saco de cemento gris?").markdown
    assert "dispersión extrema" in md and "Otros ítems parecidos" in md


def test_normalizar_descripcion_precio():
    assert pc._normalizar_descripcion_precio("saco cemento gris 50 kg") == "bulto cemento gris 50kl"


# ---- susceptibilidad a movimientos en masa e informe de sitio (datos sintéticos; no leen el artefacto real ni la red)
import time as _time

SUSC = {"min_fondo": 20, "auc_region": {"Caribe": 0.74, "Andina": 0.88}, "rho_sgc_region": {"Caribe": {"rho": 0.12, "n": 40}, "Andina": {"rho": 0.55, "n": 200}},
        "municipios": {
            "08001": {"municipio": "Barranquilla", "departamento": "Atlántico", "categoria_sgc": "B", "sgc_pct": {"baja": 97.0, "media": 3.0, "alta": 0.0, "muy_alta": 0.0}, "n_fondo": 25, "n_eventos": 0, "indice_pct": 10.0},
            "05001": {"municipio": "Medellín", "departamento": "Antioquia", "categoria_sgc": "A", "sgc_pct": {"baja": 10.0, "media": 40.0, "alta": 45.0, "muy_alta": 5.0}, "n_fondo": 80, "n_eventos": 30, "indice_pct": 88.0},
            "08999": {"municipio": "Pueblito", "departamento": "Atlántico", "categoria_sgc": "M", "sgc_pct": {"baja": 50.0, "media": 50.0, "alta": 0.0, "muy_alta": 0.0}, "n_fondo": 3, "n_eventos": 0, "indice_pct": None},
        }}
BQ = {"municipio": "Barranquilla", "departamento": "Atlántico", "latitud": 10.96, "longitud": -74.8}
MED = {"municipio": "Medellín", "departamento": "Antioquia"}


@pytest.fixture
def susc_falso():
    pc._cache_susc.clear(); pc._cache_susc.update(SUSC)
    pc._cache_oni.update({"t": _time.time(), "v": {"temporada": "ASO 2026", "oni": 1.2, "fase": "El Niño"}})
    yield
    pc._cache_susc.clear()


@pytest.mark.parametrize("q,esperado", [("¿Hay riesgo de deslizamientos en Medellín?", True), ("susceptibilidad a movimientos en masa", True), ("resistencia del concreto", False)])
def test_activar_susceptibilidad(q, esperado):
    assert pc.activar_susceptibilidad(q) is esperado


@pytest.mark.parametrize("q,esperado", [("Necesito un informe de sitio para Barranquilla", True), ("ficha técnica del terreno en Medellín", True), ("¿qué debo saber del terreno en Cali para construir?", True),
                                        ("¿qué es un informe de ensayo?", False), ("zona sísmica de Cali", False)])
def test_activar_informe_sitio(q, esperado):
    assert pc.activar_informe_sitio(q) is esperado


def test_susceptibilidad_omite_el_indice_si_no_concuerda_con_el_mapa_del_sgc_en_la_region(susc_falso):
    r = pc.ejecutar_susceptibilidad("¿Hay deslizamientos en Barranquilla?", lambda _q: BQ)      # en los datos sintéticos el Caribe tiene ρ = 0,12 < 0,30
    assert "97.0 % del área en amenaza baja" in r.markdown and "categoría" not in r.markdown
    assert "Índice de StructAI omitido" in r.markdown and "percentil" not in r.markdown and "ρ = 0.12" in r.markdown


def test_susceptibilidad_region_confiable_no_lleva_la_advertencia_de_baja(susc_falso):
    md = pc.ejecutar_susceptibilidad("deslizamientos en Medellín", lambda _q: MED).markdown
    assert "percentil 88" in md and "región Andina" in md and "omitido" not in md and "Moderada" not in md


def test_susceptibilidad_municipio_con_pocos_puntos_no_inventa_indice(susc_falso):
    pc._cache_susc["rho_sgc_region"]["Caribe"]["rho"] = 0.63      # región con concordancia suficiente, para aislar el caso «pocos puntos»
    md = pc.ejecutar_susceptibilidad("deslizamientos en Pueblito", lambda _q: {"municipio": "Pueblito", "departamento": "Atlántico"}).markdown
    assert "No hay suficientes puntos" in md and "percentil" not in md


def test_susceptibilidad_sin_municipio_o_desconocido_devuelve_none(susc_falso):
    assert pc.ejecutar_susceptibilidad("deslizamientos", lambda _q: None) is None
    assert pc.ejecutar_susceptibilidad("deslizamientos", lambda _q: {"municipio": "Inexistente", "departamento": "X"}) is None
    assert pc.ejecutar_susceptibilidad("deslizamientos", None) is None


def test_informe_de_sitio_tiene_todas_las_secciones_y_cabecera(susc_falso):
    r = pc.ejecutar_informe_sitio("informe de sitio para Barranquilla", lambda _q: BQ, lambda reg: "Amenaza sísmica en Barranquilla: Aa 0,10.\n\nSuelos del IGAC: unidades de drenaje moderado.")
    md = r.markdown
    assert md.startswith("### Informe de sitio — Barranquilla (Atlántico)")
    for s in ("Datos oficiales del sitio", "Amenaza sísmica en Barranquilla", "Suelos del IGAC", "Movimientos en masa", "Contexto climático (ENSO)", "Qué normas consultar antes de diseñar", "Título H"):
        assert s in md
    assert "no reemplaza el estudio de suelos" in md and r.nombre == "informe_sitio"


def test_informe_de_sitio_sobrevive_si_el_bloque_de_datos_falla(susc_falso):
    def bomba(_reg): raise RuntimeError("falla simulada")
    md = pc.ejecutar_informe_sitio("informe de sitio para Barranquilla", lambda _q: BQ, bomba).markdown
    assert "Datos oficiales del sitio" not in md and "Qué normas consultar" in md and "Movimientos en masa" in md


def test_informe_de_sitio_sin_municipio_devuelve_none(susc_falso):
    assert pc.ejecutar_informe_sitio("informe de sitio", lambda _q: None) is None


def test_orquestacion_informe_no_repite_enso_ni_susceptibilidad(susc_falso):
    out = pc.ejecutar_plugins("informe de sitio para Barranquilla: deslizamientos y El Niño", None, lambda _q: BQ, lambda reg: "Dato del sitio.")
    assert [p.nombre for p in out] == ["informe_sitio"]


def test_orquestacion_sin_informe_activa_susceptibilidad_y_enso_por_separado(susc_falso):
    out = pc.ejecutar_plugins("deslizamientos y El Niño en Medellín", None, lambda _q: MED)
    assert {p.nombre for p in out} == {"susceptibilidad_mm", "enso_region"}


def test_respuesta_degradada_incluye_el_informe_de_sitio(susc_falso):
    r = pc.respuesta_degradada("informe de sitio para Barranquilla", None, lambda _q: BQ, lambda reg: "Dato del sitio.")
    assert r and r["degradado"] is True and r["plugins_usados"] == ["informe_sitio"] and "Dato del sitio." in r["respuesta"]


def test_susceptibilidad_confiabilidad_moderada_si_concuerda_con_el_sgc_pero_el_auc_es_bajo(susc_falso):
    pc._cache_susc["rho_sgc_region"]["Caribe"]["rho"] = 0.63      # como en el artefacto real: el Caribe concuerda con el SGC (ρ = 0,63) pero su AUC es 0,77
    md = pc.ejecutar_susceptibilidad("deslizamientos en Barranquilla", lambda _q: BQ).markdown
    assert "Moderada" in md and "omitido" not in md and "percentil 10" in md and "no es una probabilidad" in md


# ---- regresión del enrutamiento a corpus extranjeros (2026-11-08) y del informe directo
def test_un_municipio_colombiano_descarta_el_corpus_peruano_si_no_se_nombra_a_peru():
    q = "Necesito un informe de sitio para un terreno en Quibdó"
    assert pc.depurar_motores_extranjeros(q, ["peru_e030"], lambda _q: {"municipio": "Quibdó"}) == ["normativa_general"]
    assert pc.depurar_motores_extranjeros(q, ["peru_e030", "geopot"], lambda _q: {"municipio": "Quibdó"}) == ["geopot"]
    assert pc.depurar_motores_extranjeros(q, ["ecuador_nec_se_ds"], lambda _q: {"municipio": "Quibdó"}) == ["normativa_general"]


def test_si_se_nombra_a_peru_o_ecuador_se_conserva_el_corpus_extranjero():
    det = lambda _q: {"municipio": "Lima"}   # incluso si un municipio colombiano coincide con el texto
    assert pc.depurar_motores_extranjeros("¿Qué dice la E.030 de Perú sobre el factor Z en Lima?", ["peru_e030"], det) == ["peru_e030"]
    assert pc.depurar_motores_extranjeros("zonas sísmicas en Ecuador según la NEC-SE", ["ecuador_nec_se_ds"], det) == ["ecuador_nec_se_ds"]


def test_sin_municipio_colombiano_no_se_toca_el_enrutamiento():
    assert pc.depurar_motores_extranjeros("¿Qué dice la E.030?", ["peru_e030"], lambda _q: None) == ["peru_e030"]
    assert pc.depurar_motores_extranjeros("pregunta", ["geopot"], lambda _q: {"municipio": "X"}) == ["geopot"]
    assert pc.depurar_motores_extranjeros("pregunta", ["peru_e030"], None) == ["peru_e030"]


def test_informe_directo_no_depende_del_modelo_y_marca_informe_directo(susc_falso):
    r = pc.respuesta_informe_directa("Necesito un informe de sitio para Barranquilla", None, lambda _q: BQ, lambda reg: "Dato del sitio.")
    assert r and r["informe_directo"] is True and pc.NOTA_INFORME in r["respuesta"] and "Informe de sitio — Barranquilla" in r["respuesta"] and r["plugins_usados"] == ["informe_sitio"]


def test_informe_directo_none_si_la_pregunta_no_pide_informe_o_no_hay_municipio(susc_falso):
    assert pc.respuesta_informe_directa("zona sísmica de Cali", None, lambda _q: BQ, None) is None
    assert pc.respuesta_informe_directa("informe de sitio", None, lambda _q: None, None) is None
