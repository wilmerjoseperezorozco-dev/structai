import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import vigencia_normas as vn


def test_extrae_decretos_resoluciones_y_rm_con_distintas_grafias():
    t = "DECRETO\xa0926 DE 2010; Decreto  945 de 2017; R.M. N� 183-2026-VIVIENDA; Resolución Ministerial N° 217-2026-VIVIENDA; Resolución 0017 de 2017"
    assert vn.identificadores(t) == {"decreto-926-2010", "decreto-945-2017", "rm-183-2026-vivienda", "rm-217-2026-vivienda", "resolucion-17-2017"}


def test_solo_en_contexto_de_modificacion_ignora_listados_laterales():
    t = "Modificado por el Decreto 945 de 2017. " + "x " * 200 + "Normas recientes: Decreto 1402 de 2010, Decreto 985 de 2010."
    assert vn.identificadores_en_modificacion(t) == {"decreto-945-2017"}


def test_sin_foto_anterior_no_hay_comparacion_ni_alerta():
    assert vn.comparar(None, {"decreto-1-2020"}) == ([], [])


def test_comparar_reporta_nuevos_y_desaparecidos():
    assert vn.comparar(["decreto-1-2020", "decreto-2-2020"], {"decreto-2-2020", "decreto-3-2021"}) == (["decreto-3-2021"], ["decreto-1-2020"])


def test_fuente_ilegible_se_reporta_y_no_se_toma_por_sin_cambios(monkeypatch):
    def falla(url):
        raise OSError("sin red")
    monkeypatch.setattr(vn, "descargar", falla)
    informe, _, alguna_ok, hay_novedad = vn.vigilar({"fuentes": [{"id": "f", "norma": "n", "url": "u"}]}, {})
    assert alguna_ok is False and hay_novedad is False and "no se pudo leer" in informe[0]


def test_pendiente_conocido_siempre_se_reporta(monkeypatch):
    monkeypatch.setattr(vn, "descargar", lambda u: b"<p>Decreto 1 de 2020</p>")
    cfg = {"fuentes": [{"id": "f", "norma": "n", "url": "u"}], "pendientes_conocidos": [{"id": "p", "norma": "n", "nota": "x"}]}
    informe, _, _, hay_novedad = vn.vigilar(cfg, {})
    assert hay_novedad is True and any("PENDIENTE CONOCIDO p" in l for l in informe)
