"""Ejemplo de punta a punta del motor contra incendio (#336, F2 → F9) con precios de referencia leídos de un archivo
EXTERNO al repositorio. Uso:

    python -I scripts/incendios/ejemplo_presupuesto.py <precios.json> <salida.json>

El edificio, la demanda y todos los criterios son ILUSTRATIVOS. No salen de NFPA, de un fabricante ni de un proyecto
real. El ejemplo muestra el flujo y la cobertura de precios: no es un diseño. Los diámetros interiores y las masas de
la tubería A795 calibre 10 son datos físicos del catálogo (ASME B36.10); se declaran aquí.
Corre dos escenarios para la unidad dudosa del precio de la tubería: "por m", como dice la fuente, y "por tubo de 6 m".
"""
import json
import os
import sys
from types import SimpleNamespace

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "motor-incendios"))
sys.path.insert(0, RAIZ)

from src import bombas as bo  # noqa: E402
from src import diametros as dm  # noqa: E402
from src import geometria as g  # noqa: E402
from src import hidraulica as h  # noqa: E402
from src import presupuesto as pr  # noqa: E402
from src import rociadores as r  # noqa: E402
from src import soportes as sp  # noqa: E402
from src import trazado as t  # noqa: E402

A795 = {"1-1/4in": (0.0366, 2.69), "1-1/2in": (0.0427, 3.11), "2-1/2in": (0.0669, 5.26), "3in": (0.0828, 6.46),
        "4in": (0.1082, 8.37)}                                   # (d interior m, kg/m), calibre 10


def main(ruta_precios: str, ruta_salida: str) -> None:
    with open(ruta_precios, encoding="utf-8") as f:
        crudo = json.load(f)["precios"]
    base = {}
    for fam, dn, u, v, fuente in crudo:
        base[(fam, dn) if dn else (fam,)] = (u, v, fuente)

    # F2–F4: un piso de 4 × 3 vanos de 5 m, con rociadores y trazado.
    p = SimpleNamespace(luces_x_m=(5.0,) * 4, luces_y_m=(5.0,) * 3, alturas_piso_m=(3.0,), columnas_mm=(400,),
                        vigas_mm=((300, 500),))
    ed = g.desde_porticos(p, 0.12)
    crit = r.Criterios(4.0, 2.0, 2.0, 0.1, 12.0, 0.10, fuente="ilustrativo")
    dist = r.distribuir(r.panos_entre_vigas(p, 0, 0.12), crit, ed)
    red = t.trazar(ed, (2.5, 2.5, 2.78), dist.puntos, t.ParametrosTrazado(0.08, 0.02))
    alim = red.terminales[0]
    operan = sorted(red.terminales[1:], key=lambda q: -(abs(q[0] - alim[0]) + abs(q[1] - alim[1])))[:12]

    # F5–F6: hidráulica y diámetros. El costo de la tubería sale del precio de referencia (escenario "por m").
    dem = h.Demanda(80.0, 50.0, 0.0, 380.0, fuente="ilustrativo")
    cat = [dm.Opcion(h.Tuberia(dn, d, 120.0), base[("tubo", dn)][1]) for dn, (d, _) in A795.items()]
    le = {(a, dn): v for dn in A795 for a, v in (("codo90", 1.5), ("te_lateral", 3.0))}
    tq = dm.Tanque(60.0, -3.0, None, base[("tanque_m3",)][1], 10.0, fuente="ilustrativo; costo m³ Construdata")
    sol = dm.optimizar(red.tramos(), alim, operan, dem, cat, le, tq,
                       dm.Restricciones(4.0, None, True, fuente="ilustrativo"), iteraciones=1500)
    res = h.calcular(sol.tramos, alim, operan, dem, sol.tuberias(), le)

    # F7: cuarto de bombas y tanque (altitud baja, succión positiva).
    succ = bo.Succion(20.0, 28.0, -3.0, -3.5, h.Tuberia("4in", 0.1082, 120), 8.0, False, fuente="ilustrativo")
    qd, pd = res.q_total_lpm, sol.mejor.p_bomba_kpa
    b1 = bo.Bomba("B-ilustr", round(qd, -2), round(pd * 1.1, -1),
                  ((0, round(pd * 1.1, -1) * 1.3), (round(qd, -2), round(pd * 1.1, -1)), (1.5 * round(qd, -2), round(pd * 1.1, -1) * 0.7)),
                  ((0, 2.0), (1.5 * round(qd, -2), 5.0)), ((100, 0.4), (1.5 * round(qd, -2), 0.65)), 1.8, 0.8, 0.0)
    jk = bo.Bomba("J-ilustr", 40, 2000, ((0, 2200), (40, 2000), (80, 1700)), ((0, 1), (80, 1.5)), ((10, 0.3), (80, 0.5)), 1.0, 0.5, 0.0)
    cb = bo.CriteriosBomba((bo.CriterioCurva(0.0, None, 1.4), bo.CriterioCurva(1.5, 0.65, None)), (0.5, 1.5), (1.0, 1.5),
                           1.0, (7.5, 11, 15, 18.5, 22, 30, 37, 45), 1.15, 40.0, 70.0, fuente="ilustrativo")
    cuarto = bo.disenar(qd, pd, [b1], succ, cb, jk, bo.Holguras(0.9, 1.0, 1.2, 0.6, fuente="ilustrativo"))
    tanque = bo.dimensionar_tanque(qd * 60 / 1000, bo.GeometriaTanque(2.5, 0.3, 0.3, 2.0, fuente="ilustrativo"))

    # F8: soportes en zona baja, grupo II: exento de diseño sísmico (A.9.1.3); quedan los colgadores.
    sis = sp.Sismo(0.10, 1.2, 1.0, 0.30, 3.0, "baja", "II", "DMI")
    cs = sp.CriteriosSoporte(12.0, 24.0, 3.6, 0.065, 45.0, {dn: m for dn, (_, m) in A795.items()}, fuente="ilustrativo")
    cap = sp.CapacidadAnclaje(10.0, 8.0, 6.0, 9.0, "factor_04", fuente="ilustrativo")
    sops = sp.arriostrar(sol.tramos, sol.tuberias(), sis, cs, "expansion", cap, cap)

    # F9: cantidades y presupuesto.
    area = ed.pisos[0].area_m2
    decl = [pr.Cantidad(("gabinete",), "und", 2, "declarado"), pr.Cantidad(("siamesa",), "und", 1, "declarado"),
            pr.Cantidad(("valvula_control_alarma",), "und", 1, "declarado"), pr.Cantidad(("extintor",), "und", 4, "declarado")]
    cants = pr.cantidades(res.tramos, len(dist.puntos), sops, cuarto, tanque, anclajes_por_riostra=2,
                          anclajes_por_colgador=1, declaradas=decl)
    inc = {"tubo": (1.03, 1.05, 1.10), "codo90": (1.0, 1.0, 1.05), "te_lateral": (1.0, 1.0, 1.05), "tanque_m3": (1.0, 1.0, 1.0)}
    salida = {"area_m2": area, "rociadores": len(dist.puntos), "operan": len(operan), "q_total_lpm": qd, "p_bomba_kpa": pd,
              "tanque_m3": tanque.volumen_bruto_m3, "cuarto_m2": cuarto.area_m2, "escenarios": {}}
    for nombre, div in (("tubo_por_m", 1.0), ("tubo_por_6m", 6.0)):
        precios = {}
        for k, (u, v, fuente) in base.items():
            v2 = v / div if k[0] == "tubo" else v
            precios[k] = pr.PrecioItem(u, 0.85 * v2, v2, 1.25 * v2, fuente + " (±: −15 %/+25 % declarado)")
        pres = pr.presupuestar(cants, precios, area, inc, n=5000)
        salida["escenarios"][nombre] = {
            "parcial": pres.parcial, "cobertura_partidas": pres.cobertura_partidas,
            "sin_precio": [list(c.clave) for c in pres.sin_precio], "por_m2": pres.por_m2(),
            "participacion": [[list(k), s] for k, s in pres.participacion()[:5]]}
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    for n, e in salida["escenarios"].items():
        m2 = e["por_m2"]
        print(f"{n}: COP/m² moda {m2['total_moda']:,.0f}  p05–p95 {m2['p05']:,.0f}–{m2['p95']:,.0f}  "
              f"(correlacionado {m2['correlacionado_p05']:,.0f}–{m2['correlacionado_p95']:,.0f})  "
              f"cobertura {e['cobertura_partidas']:.0%}, sin precio: {len(e['sin_precio'])}")
    print(f"área {area:.0f} m², {len(dist.puntos)} rociadores, Q {qd:.0f} L/min, P_bomba {pd:.0f} kPa, "
          f"tanque {tanque.volumen_bruto_m3:.1f} m³")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
