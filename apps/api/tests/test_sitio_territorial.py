"""packages/construdata/sitio_territorial.py (#273): ficha territorial y pre-diseño de exploración.

Unitarias con dobles de Supabase y del SGC (sin red): privacidad (redondeo antes de salir), cruces por DIVIPOLA,
agregaciones, estación más cercana, método por zona, recomendaciones y degradación cuando una fuente falla.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages" / "construdata"))

import sitio_territorial as st  # noqa: E402


class _Consulta:
    def __init__(self, filas):
        self.filas, self.filtros, self.rango, self.tope = filas, [], None, None

    def select(self, _cols):
        return self

    def eq(self, campo, valor):
        self.filtros.append(lambda f: str(f.get(campo)) == str(valor))
        return self

    def gte(self, campo, valor):
        self.filtros.append(lambda f: f.get(campo) is not None and f[campo] >= valor)
        return self

    def lte(self, campo, valor):
        self.filtros.append(lambda f: f.get(campo) is not None and f[campo] <= valor)
        return self

    def range(self, a, b):
        self.rango = (a, b)
        return self

    def limit(self, n):
        self.tope = n
        return self

    def execute(self):
        filas = [f for f in self.filas if all(c(f) for c in self.filtros)]
        if self.rango:
            filas = filas[self.rango[0]: self.rango[1] + 1]
        if self.tope:
            filas = filas[: self.tope]
        return type("R", (), {"data": filas})()


class _SB:
    def __init__(self, tablas):
        self.tablas = tablas

    def table(self, nombre):
        if nombre not in self.tablas:
            raise RuntimeError(f"tabla {nombre} caída")
        return _Consulta(self.tablas[nombre])


def _tablas(n_igac=3):
    igac = [{"cod_dane_municipio": "11001", "textura": "Arcillosa", "drenaje": "Pobre", "inund": "Largas", "area_ha": 60},
            {"cod_dane_municipio": "11001", "textura": "Franca", "drenaje": "Bien", "inund": "No hay", "area_ha": 40}]
    igac += [{"cod_dane_municipio": "11001", "textura": "Franca", "drenaje": "Bien", "inund": "No hay", "area_ha": 0.0}
             for _ in range(n_igac)]
    return {
        "nsr10_apendice_a4_municipios": [{"codigo": "11001", "municipio": "Bogotá", "departamento": "Bogotá", "aa": 0.15,
                                          "av": 0.20, "ae": 0.13, "ad": 0.06, "zona": "Intermedia"}],
        "igac_suelos_ufh": igac,
        "ungrd_emergencias": [
            {"codigo_municipio": "11001", "fecha": "2021-05-01", "evento": "CRECIENTE SUBITA", "puentes_vehiculares": 2},
            {"codigo_municipio": "11001", "fecha": "2019-02-01", "evento": "MOVIMIENTO EN MASA", "puentes_vehiculares": 1,
             "viviendas_averiadas": 5},
            {"codigo_municipio": "05001", "fecha": "2020-01-01", "evento": "INUNDACION", "puentes_vehiculares": 9}],
        "sisben_vulnerabilidad_vivienda_municipio": [{"codigo_municipio": "11001", "pct_material_vulnerable": 4.2}],
        "microzonificacion_sismica_local": [
            {"ciudad": "Bogotá, D.C.", "zona": "Lacustre-200", "descripcion_zona": "Arcillas limosas blandas 100-200m"},
            {"ciudad": "Bogotá, D.C.", "zona": "Aluvial-100", "descripcion_zona": "Suelo aluvial, susceptible a licuación"}],
        "ideam_estaciones_caudal": [
            {"codigo": "A", "nombre": "Cerca", "latitud": 4.62, "longitud": -74.07, "estado": "Activa"},
            {"codigo": "B", "nombre": "Lejos", "latitud": 4.95, "longitud": -74.40, "estado": "Activa"}],
    }


class _Resp:
    def __init__(self, datos):
        self.datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self.datos


def _sgc_bogota(llamadas):
    def get(url, params, timeout):
        llamadas.append(params)
        return _Resp({"features": [{"attributes": {"CÓDIGO_MUNICIPIO": "11001", "NOMBRE_MUNICIPIO": "BOGOTÁ, D.C.",
                                                   "NOMBRE_DEPARTAMENTO": "BOGOTÁ", "AA": 0.15, "AV": 0.2,
                                                   "ZONA_AMENAZA_SÍSMICA": "Intermedia"}}]})
    return get


def test_redondeo_y_fuera_de_colombia():
    assert st.redondear(4.609876, -74.081234) == (4.61, -74.08)
    with pytest.raises(ValueError, match="fuera de Colombia"):
        st.redondear(40.4, -3.7)
    with pytest.raises(ValueError):
        st.redondear(float("nan"), -74.0)


def test_ficha_por_coordenada_redondea_antes_de_salir():
    llamadas, simma = [], []
    f = st.ficha_sitio(_SB(_tablas()), lat=4.609876, lon=-74.081234, http_get=_sgc_bogota(llamadas),
                       simma=lambda la, lo: simma.append((la, lo)) or {"total": 3, "radio_km": 15})
    assert llamadas[0]["geometry"] == "-74.08,4.61"          # la coordenada exacta nunca sale
    assert simma == [(4.61, -74.08)]
    assert f["punto"]["lat"] == 4.61 and "4.609876" not in str(f)
    assert f["municipio"]["codigo_municipio"] == "11001"
    assert f["sismo_nsr10"]["aa"] == 0.15
    assert f["suelos_igac"]["fraccion_drenaje_deficiente"] == pytest.approx(0.6)
    assert f["emergencias_ungrd"]["eventos"] == 2                       # no mezcla otro municipio
    assert f["emergencias_ungrd"]["puentes_vehiculares_por_eventos_hidricos"] == 2
    assert f["estacion_ideam_cercana"]["codigo"] == "A"
    assert f["fuentes_no_disponibles"] == []
    temas = [r["tema"] for r in f["recomendaciones"]]
    assert temas == ["sismo", "agua", "socavacion", "ladera", "cimentacion_profunda"]
    metodos = {z["zona"]: z["metodo_cimentacion_orientativo"] for z in f["microzonificacion"]["zonas"]}
    assert metodos["Lacustre-200"].startswith("Arcilla blanda")
    assert metodos["Aluvial-100"].startswith("Perfil aluvial")


def test_paginacion_igac_mas_de_1000_filas():
    f = st.suelos_igac(_SB(_tablas(n_igac=2500)), "11001")
    assert f["unidades"] == 2502


def test_fuente_caida_no_tumba_la_ficha_y_municipio_sin_microzonificacion():
    tablas = _tablas()
    del tablas["ungrd_emergencias"]
    tablas["nsr10_apendice_a4_municipios"].append({"codigo": "05001", "aa": 0.15, "zona": "Intermedia"})
    f = st.ficha_sitio(_SB(tablas), codigo_municipio="5001")
    assert f["municipio"]["codigo_municipio"] == "05001"
    assert "emergencias_ungrd" in f["fuentes_no_disponibles"]
    assert "microzonificacion" not in f["fuentes_no_disponibles"]     # Medellín no tiene estudio cargado: no es falla
    assert "estacion_ideam_cercana" not in f                          # sin coordenada no se busca proximidad


def test_sgc_caido_o_sin_municipio():
    def caido(url, params, timeout):
        raise TimeoutError
    f = st.ficha_sitio(_SB(_tablas()), lat=4.6, lon=-74.08, http_get=caido)
    assert f["municipio"] is None and f["fuentes_no_disponibles"] == ["sgc_municipio"]
    assert st.municipio_por_coordenada(12.0, -70.0, http_get=lambda *a, **k: _Resp({"features": []})) is None


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        st.ficha_sitio(_SB(_tablas()), lat=4.6)
    with pytest.raises(ValueError):
        st.ficha_sitio(_SB(_tablas()))
    with pytest.raises(ValueError, match="DIVIPOLA"):
        st.ficha_sitio(_SB(_tablas()), codigo_municipio="bogota")


def test_metodo_por_zona():
    assert st.metodo_por_zona("Rocas sedimentarias y depósitos de ladera").startswith("Roca")
    assert st.metodo_por_zona("bloques/cantos/gravas en matriz").startswith("Gravas")
    assert st.metodo_por_zona("Arcillas lacustres con intercalaciones aluviales").startswith("Arcilla blanda")
    assert st.metodo_por_zona("Abanico Distal de Cali").startswith("Perfil aluvial")
    assert st.metodo_por_zona("Zona 3 T0=0.17s").startswith("Según exploración")


def test_indicador_hidrico_alto_dispara_recomendacion(monkeypatch):
    monkeypatch.setattr(st, "_INDICE_HIDRICO", {
        "version": "v", "metodo": "m", "validacion": "AUC 0,75", "cobertura": "1000 municipios",
        "municipios": {"11001": {"indice": 0.9, "percentil": 0.95, "puentes_hidricos_2019_2024": 4}}})
    f = st.ficha_sitio(_SB(_tablas()), codigo_municipio="11001")
    assert f["indicador_hidrico"]["nivel"] == "alto"
    assert "sísmico" in f["indicador_hidrico"]["contexto"]
    assert "hidrico" in [r["tema"] for r in f["recomendaciones"]]


def test_indicador_hidrico_fuera_de_cobertura_no_es_falla(monkeypatch):
    monkeypatch.setattr(st, "_INDICE_HIDRICO", {"version": "v", "metodo": "m", "validacion": "v",
                                                "cobertura": "1000 municipios", "municipios": {}})
    f = st.ficha_sitio(_SB(_tablas()), codigo_municipio="11001")
    assert f["indicador_hidrico"]["nivel"] == "sin_dato"
    assert "indicador_hidrico" not in f["fuentes_no_disponibles"]


def test_indice_hidrico_real_bien_formado():
    d = st._indice_hidrico()
    assert len(d["municipios"]) >= 900
    m = next(iter(d["municipios"].values()))
    assert 0 <= m["percentil"] <= 1 and "indice" in m
