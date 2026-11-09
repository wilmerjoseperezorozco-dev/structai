"""Cadena real orquestador → análisis → zapata sobre el DAG (#150)."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "contrato-motor"))

from dag_proyecto import Orquestador
from dag_proyecto.motores import PARAMETROS_REQUERIDOS, nodos_estructurales

PROYECTO = dict(
    luces_m=[6.0], alturas_piso_m=[3.0], carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0, calidad_concreto="3000",
    fy_mpa=420.0, recubrimiento_mm=40.0, municipio="Pereira", departamento="Risaralda", perfil_suelo="D",
    grupo_uso="I", capacidad="DES", columnas_mm=[400.0, 500.0], b_mm=[300.0, 350.0], h_mm=[500.0, 600.0],
    E_mpa=21000.0, q_adm_kpa=250.0, profundidad_desplante_m=1.5, peso_unitario_relleno_kn_m3=17.0,
    asentamiento_max_mm=25.0, ks_kn_m3=None, fc_mpa=21.0,
)


@pytest.fixture(scope="module")
def corrida():
    o = Orquestador(nodos_estructurales(), norma_version="NSR-10 (Decreto 926/2010)")
    return o, o.ejecutar(PROYECTO)


def test_la_cadena_produce_los_tres_artefactos_con_linaje(corrida):
    _, a = corrida
    assert set(a) == {"orquestador", "analisis", "zapata"}
    assert a["analisis"].entradas == (a["orquestador"].id,)
    assert set(a["zapata"].entradas) == {a["orquestador"].id, a["analisis"].id}


def test_la_zapata_toma_su_carga_de_la_reaccion_del_analisis(corrida):
    _, a = corrida
    rd = a["analisis"].resultado["valor"]["reaccion_base_max_kn"]
    assert a["zapata"].resultado["valor"]["P_serv_kn"] == pytest.approx(rd["D"] + rd["L"])
    assert a["zapata"].resultado["valor"]["P_u_kn"] == pytest.approx(1.2 * rd["D"] + 1.6 * rd["L"])


def test_cada_artefacto_conserva_el_contrato_de_salida(corrida):
    _, a = corrida
    for art in a.values():
        r = art.resultado
        assert isinstance(r["en_borde_dominio"], bool) and r["aviso_responsabilidad_profesional"] and r["supuestos"]


def test_cambiar_solo_el_suelo_recalcula_unicamente_la_zapata(corrida):
    o, a1 = corrida
    a2 = o.ejecutar({**PROYECTO, "q_adm_kpa": 300.0})
    assert a2["orquestador"].id == a1["orquestador"].id and a2["analisis"].id == a1["analisis"].id
    assert a2["zapata"].id != a1["zapata"].id


def test_mas_carga_viva_no_reduce_la_zapata(corrida):
    o, a1 = corrida
    a2 = o.ejecutar({**PROYECTO, "carga_viva_kn_m": 16.0})
    assert a2["zapata"].resultado["valor"]["P_u_kn"] > a1["zapata"].resultado["valor"]["P_u_kn"]


def test_parametro_ausente_falla_citando_la_clave():
    o = Orquestador(nodos_estructurales(), norma_version="x")
    for clave in ("E_mpa", "q_adm_kpa", "perfil_suelo"):
        with pytest.raises(ValueError, match=clave):
            o.ejecutar({k: v for k, v in PROYECTO.items() if k != clave})


def test_los_parametros_declarados_cubren_el_proyecto():
    assert set(PARAMETROS_REQUERIDOS) <= set(PROYECTO)
