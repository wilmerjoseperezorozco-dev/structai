"""Salida con contrato uniforme de motor-concreto (#130): zapata aislada y talud de excavación."""
import pytest
from pydantic import ValidationError

from src.contrato_api import SolicitudTalud, SolicitudZapata, disenar_zapata_contrato, evaluar_talud_contrato


def _zapata(**kw):
    base = dict(c1_mm=400, c2_mm=400, P_serv=800.0, P_u=1100.0, q_adm_kpa=200.0, profundidad_desplante_m=1.5,
                peso_unitario_relleno_kn_m3=17.0, asentamiento_max_mm=25.0, ks_kn_m3=None, fc_mpa=21.0, fy_mpa=420.0)
    base.update(kw)
    return SolicitudZapata(**base)


def _talud(**kw):
    base = dict(altura_m=5.0, angulo_deg=45.0, gamma_kn_m3=18.0, c_kpa=15.0, phi_deg=28.0, prof_freatico_m=None,
                sobrecarga_kpa=0.0, kh=0.0, estado="diseno")
    base.update(kw)
    return SolicitudTalud(**base)


def test_zapata_devuelve_el_contrato_completo():
    r = disenar_zapata_contrato(_zapata())
    assert r.valor["Lx_m"] > 0 and r.valor["h_mm"] >= 300 and r.valor["cumple"] is True
    assert r.unidad_si and r.ecuacion and "NSR-10" in r.referencia_normativa
    assert isinstance(r.en_borde_dominio, bool) and r.aviso_responsabilidad_profesional
    assert any("q_adm" in s for s in r.supuestos)


def test_zapata_sin_ks_declara_que_no_verifica_asentamiento():
    r = disenar_zapata_contrato(_zapata(ks_kn_m3=None))
    assert any("asentamiento" in s.lower() and "no" in s.lower() for s in r.supuestos)


def test_zapata_exige_datos_del_suelo_sin_defectos():
    with pytest.raises(ValidationError):
        SolicitudZapata(c1_mm=400, c2_mm=400, P_serv=800.0, P_u=1100.0, q_adm_kpa=200.0, fc_mpa=21.0, fy_mpa=420.0)


def test_zapata_sin_solucion_lanza_valueerror():
    with pytest.raises(ValueError, match="NSR-10"):
        disenar_zapata_contrato(_zapata(P_serv=9e5, P_u=1.2e6, q_adm_kpa=50.0))


def test_zapata_mas_carga_no_reduce_el_volumen_de_concreto():
    v = [disenar_zapata_contrato(_zapata(P_serv=p, P_u=1.4 * p)).valor["volumen_concreto_m3"] for p in (400.0, 800.0, 1600.0)]
    assert v[0] <= v[1] <= v[2]


def test_talud_devuelve_contrato_y_fs_coherente_con_la_tabla():
    r = evaluar_talud_contrato(_talud())
    assert r.valor["fs"] > 0 and r.valor["fs_requerido"] == pytest.approx(1.5)
    assert r.valor["cumple"] == (r.valor["fs"] >= r.valor["fs_requerido"])
    assert "H.2.4" in r.referencia_normativa and "Bishop" in r.ecuacion


def test_talud_sin_prof_estrato_firme_declara_la_cota_asumida():
    r = evaluar_talud_contrato(_talud())
    assert any("1,2" in s and "estrato" in s for s in r.supuestos)


def test_talud_sin_nivel_freatico_declara_ausencia_de_agua():
    assert any("agua" in s.lower() for s in evaluar_talud_contrato(_talud()).supuestos)


def test_talud_fs_decrece_con_la_pendiente():
    fs = [evaluar_talud_contrato(_talud(angulo_deg=a)).valor["fs"] for a in (30.0, 40.0, 50.0, 60.0)]
    assert all(a >= b for a, b in zip(fs, fs[1:]))


def test_talud_estado_invalido_lanza_valueerror():
    with pytest.raises(ValueError):
        evaluar_talud_contrato(_talud(estado="otro"))


def test_talud_marca_borde_cuando_el_fs_esta_cerca_del_requerido():
    r = evaluar_talud_contrato(_talud())
    esperado = abs(r.valor["fs"] / r.valor["fs_requerido"] - 1) < 0.05 or r.valor["en_borde_busqueda"]
    assert r.en_borde_dominio is esperado
