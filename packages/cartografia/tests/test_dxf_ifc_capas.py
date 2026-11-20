"""Tests de metadatos DXF/IFC y catálogo de capas (issue #211)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ezdxf
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.template
import pytest

import capas
import dxf_georef as dg
import ifc_georef as ig
from georef import PuntoBase

PB = PuntoBase(4_880_692.0, 2_066_175.0, 2600.0, rotacion_rad=0.05, escala=0.99987, fuente="levantamiento")


def _guardar_y_leer(doc, tmp_path):
    ruta = tmp_path / "plano.dxf"
    doc.saveas(ruta)
    return ezdxf.readfile(ruta)


@pytest.mark.parametrize("geodata", [False, True])
def test_dxf_guarda_y_recupera_punto_base(tmp_path, geodata):
    doc = dg.nuevo_documento()
    dg.escribir_georef(doc, PB, geodata=geodata)
    leido = _guardar_y_leer(doc, tmp_path)
    assert dg.leer_georef(leido) == PB
    assert leido.header["$INSUNITS"] == 6
    if geodata:
        gd = leido.modelspace().get_geodata()
        assert gd is not None and tuple(gd.dxf.reference_point)[:2] == (PB.e0, PB.n0)


def test_dxf_respaldo_por_variables_de_cabecera(tmp_path):
    doc = dg.nuevo_documento()
    dg.escribir_georef(doc, PB)
    doc.rootdict.remove(dg.NOMBRE_XRECORD)            # un programa que borró el XRECORD
    pb = dg.leer_georef(_guardar_y_leer(doc, tmp_path))
    assert (pb.e0, pb.n0, pb.h0, pb.escala) == (PB.e0, PB.n0, PB.h0, PB.escala)
    assert pb.rotacion_rad == pytest.approx(PB.rotacion_rad, abs=1e-15)


def test_dxf_reescribir_no_duplica(tmp_path):
    doc = dg.nuevo_documento()
    dg.escribir_georef(doc, PB)
    otro = PuntoBase(1.0, 2.0)
    dg.escribir_georef(doc, otro)
    leido = _guardar_y_leer(doc, tmp_path)
    assert dg.leer_georef(leido) == otro
    assert sum(1 for t in leido.header.custom_vars if t[0] == "STRUCTAI_E0") == 1


def test_dxf_sin_georef_devuelve_none():
    assert dg.leer_georef(ezdxf.new()) is None


def test_dxf_polilinea_local_vuelve_al_oficial(tmp_path):
    doc = dg.nuevo_documento()
    dg.escribir_georef(doc, PB)
    oficiales = [(4_880_700.123, 2_066_180.456, 2601.5), (4_880_950.0, 2_066_400.0, 2605.0)]
    dg.agregar_polilinea(doc, oficiales, PB, "VIAS-EJE-DISENO")
    leido = _guardar_y_leer(doc, tmp_path)
    pb = dg.leer_georef(leido)
    pl = next(iter(leido.modelspace().query("POLYLINE")))
    vertices = [v.dxf.location for v in pl.vertices]
    assert all(abs(v.x) < 1000 and abs(v.y) < 1000 for v in vertices)
    for v, (e, n, h) in zip(vertices, oficiales):
        e2, n2, h2 = pb.a_oficial(v.x, v.y, v.z)
        assert max(abs(e2 - e), abs(n2 - n), abs(h2 - h)) < 1e-3


def _modelo(schema):
    if schema == "IFC2X3":
        # Como llega un IFC2X3 real (Revit/ArchiCAD): con proyecto, OwnerHistory y un IfcSite.
        f = ifcopenshell.template.create(schema_identifier="IFC2X3")
        f.by_type("IfcOwnerHistory")[0].ChangeAction = "NOCHANGE"   # la plantilla lo deja vacío (inválido en 2X3)
        f.create_entity("IfcSite", GlobalId=ifcopenshell.guid.new(), OwnerHistory=f.by_type("IfcOwnerHistory")[0],
                        Name="Sitio", CompositionType="ELEMENT")
        return f
    f = ifcopenshell.file(schema=schema)
    proyecto = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="Prueba #211")
    ifcopenshell.api.run("unit.assign_unit", f)
    ifcopenshell.api.run("context.add_context", f, context_type="Model")
    sitio = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcSite", name="Sitio")
    ifcopenshell.api.run("aggregate.assign_object", f, relating_object=proyecto, products=[sitio])
    return f


@pytest.mark.parametrize("schema", ["IFC4", "IFC2X3"])
def test_ifc_guarda_y_recupera_punto_base(tmp_path, schema):
    f = _modelo(schema)
    ig.georreferenciar(f, PB)
    ruta = tmp_path / "m.ifc"
    f.write(str(ruta))
    g = ifcopenshell.open(str(ruta))
    pb = ig.leer_georef(g)
    assert pb.epsg == 9377
    assert (pb.e0, pb.n0, pb.h0) == (PB.e0, PB.n0, PB.h0)
    assert pb.escala == pytest.approx(PB.escala) and pb.rotacion_rad == pytest.approx(PB.rotacion_rad, abs=1e-12)
    if schema == "IFC4":
        mc = g.by_type("IfcMapConversion")
        assert len(mc) == 1 and mc[0].TargetCRS.Name == "EPSG:9377"
        assert math.hypot(mc[0].XAxisAbscissa, mc[0].XAxisOrdinate) == pytest.approx(1.0)


def test_ifc4_reemplaza_sin_duplicar():
    f = _modelo("IFC4")
    ig.georreferenciar(f, PB)
    ig.georreferenciar(f, PuntoBase(1.0, 2.0))
    assert len(f.by_type("IfcMapConversion")) == 1 and len(f.by_type("IfcProjectedCRS")) == 1
    assert ig.leer_georef(f).e0 == 1.0


def test_ifc_sin_georef_devuelve_none():
    assert ig.leer_georef(_modelo("IFC4")) is None


# ── Capas ───────────────────────────────────────────────────────────────────────────────────────────────

def test_catalogo_nombres_unicos_y_validos():
    cat = capas.catalogo()
    nombres = [c.nombre for c in cat["capas"]]
    assert len(nombres) == len(set(nombres))
    assert all(capas.nombre_valido(n) for n in nombres), [n for n in nombres if not capas.nombre_valido(n)]
    assert all(1 <= c.color <= 255 for c in cat["capas"])


def test_cada_capa_se_mapea_a_si_misma():
    for c in capas.catalogo()["capas"]:
        assert capas.mapear(c.nombre) == c.nombre


@pytest.mark.parametrize("entrada,esperada", [
    ("Curvas de Nivel", "TOPO-CURVA-MENOR"),
    ("CURVAS_MAESTRAS", "TOPO-CURVA-MAYOR"),
    ("Eje Vía", "VIAS-EJE-DISENO"),
    ("Lindero_Predio", "PREDIO-LINDERO"),
    ("Colector Sanitario", "ALCA-TUBERIA-DISENO"),
    ("Tubería Acueducto Existente", "ACUE-TUBERIA-EXIST"),
    ("Pozos", "ALCA-POZO"),
    ("COLUMNAS", "ESTR-COLUMNA"),
    ("Acero de refuerzo", "ESTR-REFUERZO"),
    ("CONCRETO", "ESTR-CONCRETO"),
    ("Cotas", "TOPO-TEXTO"),
    ("DIMENSIONES", "ANOT-COTA"),
    ("PLANTA", "ANOT-VISTA"),
    ("Corte", "ANOT-VISTA"),
])
def test_mapeo_de_capas_comunes(entrada, esperada):
    assert capas.mapear(entrada) == esperada


def test_capa_desconocida_no_se_inventa():
    assert capas.mapear("XYZ_123") is None


def test_aplicar_y_validar_dxf(tmp_path):
    doc = dg.nuevo_documento()
    hechas = capas.aplicar_catalogo(doc, {"VIAS"})
    assert hechas and all(h.startswith("VIAS-") for h in hechas)
    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 1), dxfattribs={"layer": "VIAS-EJE-DISENO"})
    msp.add_line((0, 0), (1, 1), dxfattribs={"layer": "curvas nivel"})
    msp.add_line((0, 0), (1, 1), dxfattribs={"layer": "capa rara"})
    doc.layers.add("VACIA_SIN_USO")
    rep = capas.validar_dxf(_guardar_y_leer(doc, tmp_path))
    assert "VIAS-EJE-DISENO" in rep["estandar"]
    assert rep["mapeables"]["curvas nivel"] == "TOPO-CURVA-MENOR"
    assert "capa rara" in rep["sin_mapear"] and "VACIA_SIN_USO" in rep["capas_vacias"]
    assert 0 < rep["cobertura"] < 1


def test_grosor_se_ajusta_a_valores_permitidos():
    assert capas._grosor_dxf(0.35) == 35 and capas._grosor_dxf(0.33) == 35 and capas._grosor_dxf(0.5) == 50


@pytest.mark.parametrize("schema", ["IFC4", "IFC2X3"])
def test_ifc_georreferenciado_pasa_validacion_de_esquema(schema):
    import ifcopenshell.validate
    f = _modelo(schema)
    ig.georreferenciar(f, PB)
    registro = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, registro)
    errores = [s for s in registro.statements if s.get("level") == "Error" or "error" in str(s.get("level", "")).lower()]
    assert not errores, errores[:3]
