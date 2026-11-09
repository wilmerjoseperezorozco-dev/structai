import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import registro_motores as rm


def _motor(**kw):
    base = dict(id="x", prefijo="/x", paquete="motor-x", endpoints=[], pruebas_paquete=1, pruebas_router=1, en_ci=True, condicion_3=True)
    base.update(kw)
    return base


def test_endpoints_detecta_limite_y_422_y_excluye_salud():
    texto = ('@router.get("/salud")\ndef s(): ...\n'
             '@router.post("/a")\n@limiter.limit("10/minute")\ndef a():\n    raise HTTPException(status_code=422)\n'
             '@router.post("/b")\ndef b(): ...\n')
    eps = rm._endpoints(texto)
    assert [e["ruta"] for e in eps] == ["/a", "/b"]
    assert eps[0]["limite"] and eps[0]["falla_422"] and not eps[1]["limite"] and not eps[1]["falla_422"]


def test_un_si_en_condicion_4_exige_revision_y_fecha():
    m = [_motor()]
    assert rm.validar_atestaciones(m, {"x": {"condicion_4": {"valor": True, "evidencia": "llamada"}}})
    assert not rm.validar_atestaciones(m, {"x": {"condicion_4": {"valor": True, "evidencia": "e", "revision": "r", "fecha": "2026-11-10"}}})


def test_un_si_sin_evidencia_se_rechaza_y_un_motor_desconocido_tambien():
    m = [_motor()]
    assert rm.validar_atestaciones(m, {"x": {"condicion_1": {"valor": True}}})
    assert rm.validar_atestaciones(m, {"y": {}})


def test_sin_atestar_es_interrogante_nunca_si():
    assert rm._celda(None, "condicion_1") == "?" and rm._celda({"condicion_1": {"valor": False}}, "condicion_1") == "no"


def test_el_conteo_de_completos_exige_las_cuatro():
    a = {"x": {c: {"valor": True, "evidencia": "e", "revision": "r", "fecha": "f"} for c in rm.CONDICIONES}}
    assert "1 de 10" in rm.renderizar([_motor()], a)
    a["x"]["condicion_2"]["valor"] = False
    assert "0 de 10" in rm.renderizar([_motor()], a)


def test_el_documento_versionado_esta_al_dia():
    assert rm.main(["--verificar"]) == 0
