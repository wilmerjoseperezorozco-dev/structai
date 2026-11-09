"""Exportación paramétrica del muro de contención: JSON de cantidades de obra (APU), memoria de cálculo trazable con etiquetas de hipótesis y contorno DXF.

Cada línea de la memoria lleva su estado: «NSR-10 (leído)» si el numeral se leyó en el corpus el 2026-11-08, «HIPÓTESIS» si es un supuesto de investigación. La
memoria NO reemplaza la revisión de un ingeniero que firme los cálculos (aviso del issue #18).
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .muro_contencion import GeometriaMuro, _perfil_trasero
from .muro_contencion_estructural import DisenoMuro, SUPUESTOS
from .muro_optimizador import CasoMuro

AVISO = "Resultado de una herramienta de investigación: requiere revisión y firma de un ingeniero civil responsable antes de cualquier uso en obra."


def _franja(f) -> dict | None:
    if f is None:
        return None
    return {"mu_knm_m": round(f.mu_knm_m, 2), "vu_kn_m": round(f.vu_kn_m, 2), "h_mm": f.h_mm, "d_mm": round(f.d_mm, 1), "barra": f"#{f.dia} c/{int(f.sep_mm)} mm",
            "as_prov_mm2_m": round(f.as_prov_mm2_m, 1), "as_req_mm2_m": round(f.as_req_mm2_m, 1), "as_min_mm2_m": round(f.as_min_mm2_m, 1), "eps_t": round(f.eps_t, 4),
            "phi_vc_kn_m": round(f.phi_vc_kn_m, 1), "cumple": f.cumple}


def cantidades_json(caso: CasoMuro, d: DisenoMuro) -> dict:
    """Cantidades por metro de muro y partidas APU con los precios usados."""
    e = caso.economia
    return {"aviso": AVISO, "unidad": "por metro lineal de muro",
            "partidas": [{"partida": "Concreto reforzado f'c " + f"{caso.materiales.fc:g} MPa", "unidad": "m3", "cantidad": round(d.concreto_m3_m, 3)},
                         {"partida": "Acero de refuerzo fy " + f"{caso.materiales.fy:g} MPa", "unidad": "kg", "cantidad": round(d.acero_kg_m, 1), "precio_cop_kg": e.p_acero},
                         {"partida": "Encofrado (solo material)", "unidad": "m2", "cantidad": round(d.encofrado_m2_m, 2), "precio_cop_m2": e.p_encofrado}],
            "costo_cop_m": round(d.costo_cop_m), "co2e_kg_m": round(d.co2_kg_m, 1), "mult_concreto": e.mult_concreto,
            "factores_co2": {"cemento": e.fe_cemento, "acero": e.fe_acero}}


def memoria(caso: CasoMuro, g: GeometriaMuro, d: DisenoMuro) -> dict:
    """Memoria trazable: entradas, verificaciones con su numeral y estado, refuerzo y lo no verificado."""
    est, sis = d.estabilidad, d.estabilidad_sismica
    L = lambda item, valor, ref, estado: {"item": item, "valor": valor, "referencia": ref, "estado": estado}
    lineas = [
        L("FS deslizamiento (estático)", round(float(est.fs_deslizamiento), 3), "Tabla H.6.9-1 (≥ 1,60)", "NSR-10 (leído)"),
        L("FS volcamiento (estático)", round(float(est.fs_volcamiento), 3), "Tabla H.6.9-1 (≥ 3,00)", "NSR-10 (leído)"),
        L("Excentricidad e/B", round(float(est.excentricidad_m / g.ancho_base), 3), "Tabla H.6.9-1 (≤ 1/6)", "NSR-10 (leído)"),
        L("Presión máxima de contacto (kPa)", round(float(est.q_max_kpa), 1), "q_adm del estudio geotécnico", "NSR-10 (leído)"),
        L("Coeficiente activo Ka", round(est.ka, 4), "Rankine, plano virtual en el talón", "HIPÓTESIS"),
        L("Fricción en la base μ", round(est.mu_usado, 3), "μ equivalente: tan(2φ/3) + aporte de la punta del dentellón (tan φ sobre su ancho), sin empuje pasivo (H.6.7b)", "HIPÓTESIS"),
        L("Combinaciones de carga", "A: B.2.4-2; S: B.2.4-7 con 1,4E; B: 0,9D+1,6H adicional", "B.2.4.2", "NSR-10 (leído) / HIPÓTESIS en 1,4E y B"),
        L("Recubrimientos", "75 mm contra suelo; 40/50 mm expuestos a suelo", "C.7.7.1", "NSR-10 (leído)"),
        L("Refuerzo mínimo de flexión", "max(0,25√f'c/fy; 1,4/fy)·b·d", "C.10.5.1", "NSR-10 (leído)"),
        L("Cuantías mínimas de la pantalla", "ρv 0,0012 / ρh 0,0020 (≤ #5, fy ≥ 420)", "C.14.3.2-3", "NSR-10 (leído)"),
    ]
    if sis is not None:
        lineas += [L("FS deslizamiento (seudoestático)", round(float(sis.fs_deslizamiento), 3), "Tabla H.6.9-1 (≥ 1,05)", "NSR-10 (leído)"),
                   L("FS volcamiento (seudoestático)", round(float(sis.fs_volcamiento), 3), "Tabla H.6.9-1 (≥ 2,00)", "NSR-10 (leído)"),
                   L("kh = K_ST", round(sis.kh, 3), "H.5.2.5: K_ST/a_max ≥ 0,80 en suelos", "NSR-10 (leído)"),
                   L("Empuje sísmico", "Mononobe-Okabe, incremento a 0,6 h", "H.6.8: «métodos de reconocida aceptación técnica»", "HIPÓTESIS")]
    if d.contrafuerte is not None:
        lineas.append(L("Contrafuertes", f"separación {g.contrafuerte_sep:g} m, espesor {g.contrafuerte_esp:g} m; losas continuas M = wL'²/12; barra principal {d.contrafuerte.n_barras_cf}#{d.contrafuerte.dia_cf}",
                        "método de losas y voladizo de la literatura; el corpus NSR-10 no lo trae", "HIPÓTESIS"))
    if d.anclaje is not None:
        lineas.append(L("Tirantes preesforzados", f"{d.anclaje.fuerza_kn_m:g} kN/m ({d.anclaje.fuerza_ancla_kn:g} kN por tirante, {d.anclaje.n_cordones} cordones, "
                        f"L libre {d.anclaje.l_libre_m:.1f} m + fija {d.anclaje.l_fija_m:.1f} m)", "H.6.7 solo los menciona; adherencia τ supuesta", "HIPÓTESIS"))
    ref_extra = {}
    if d.contrafuerte is not None:
        c = d.contrafuerte
        ref_extra["contrafuerte"] = {"mu_knm": round(c.mu_cf_knm, 1), "vu_kn": round(c.vu_cf_kn, 1), "d_mm": round(c.d_cf_mm), "as_req_mm2": round(c.as_req_cf_mm2),
                                     "barras": f"{c.n_barras_cf}#{c.dia_cf}", "as_prov_mm2": round(c.as_prov_cf_mm2), "estribos_mm2_por_m": round(c.estribos_mm2_m),
                                     "vertical_pantalla": _franja(c.vertical)}
    if d.anclaje is not None:
        a = d.anclaje
        ref_extra["anclaje"] = {"fuerza_kn_m": a.fuerza_kn_m, "fuerza_por_tirante_kn": a.fuerza_ancla_kn, "cordones": a.n_cordones, "l_libre_m": round(a.l_libre_m, 2),
                                "l_fija_m": round(a.l_fija_m, 2), "cumple": a.cumple}
    return {"aviso": AVISO, "entradas": {"H_m": caso.altura, "gamma_kn_m3": caso.relleno.gamma, "phi_deg": caso.relleno.phi_deg, "beta_deg": caso.relleno.beta_deg,
                                         "q_s_kpa": caso.relleno.sobrecarga_kpa, "q_adm_kpa": caso.apoyo.q_adm_kpa, "a_max_g": caso.a_max_g,
                                         "fc_mpa": caso.materiales.fc, "fy_mpa": caso.materiales.fy},
            "geometria": {k: v for k, v in asdict(g).items() if v is not None}, "verificaciones": lineas,
            "refuerzo": {"pantalla": _franja(d.pantalla), "puntera": _franja(d.puntera), "talon": _franja(d.talon), "bandeja": _franja(d.bandeja),
                         "dentellon": _franja(d.dentellon), "horizontal_pantalla": d.acero_horizontal_pantalla, "vertical_frontal_pantalla": d.acero_vertical_frontal_pantalla, **ref_extra},
            "no_verificado": list(SUPUESTOS), "cumple": d.cumple}


def contorno(g: GeometriaMuro) -> list[tuple[float, float]]:
    """Contorno cerrado del concreto (m): zapata + pantalla (perfil trasero) + bandeja + dentellón; x desde la punta, y desde la cara inferior de la zapata."""
    xs, ys = _perfil_trasero(g)
    hz, B = g.h_zapata, g.ancho_base
    pts = [(0.0, 0.0)]
    if g.tiene_dentellon:
        xd = g.dentellon_x_efectivo
        pts += [(xd, 0.0), (xd, -g.dentellon_prof), (xd + g.dentellon_ancho, -g.dentellon_prof), (xd + g.dentellon_ancho, 0.0)]
    pts += [(B, 0.0), (B, hz)]
    y0, y1 = g.bandeja_y, g.bandeja_y + g.bandeja_esp
    insertada = False
    for x, y in zip(xs, ys):
        x, y = float(x), float(y)
        if g.tiene_bandeja and y < y0 - 1e-9:
            pts.append((x, hz + y))
        elif g.tiene_bandeja and y <= y1 + 1e-9:
            if not insertada:
                xa, xb = g.b_puntera + float(g.espesor_pantalla(y0)), g.b_puntera + float(g.espesor_pantalla(y1))
                pts += [(xa, hz + y0), (xa + g.bandeja_vuelo, hz + y0), (xa + g.bandeja_vuelo, hz + y1), (xb, hz + y1)]
                insertada = True
        else:
            pts.append((x, hz + y))
    pts += [(g.b_puntera, hz + g.h_pantalla), (g.b_puntera, hz), (0.0, hz)]
    return pts


def exportar_dxf(g: GeometriaMuro, ruta: str | Path) -> Path:
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.layers.add("CONCRETO", color=7)
    msp = doc.modelspace()
    msp.add_lwpolyline([(x * 1000.0, y * 1000.0) for x, y in contorno(g)], close=True, dxfattribs={"layer": "CONCRETO"})
    ruta = Path(ruta)
    doc.saveas(ruta)
    return ruta


def exportar_json(caso: CasoMuro, g: GeometriaMuro, d: DisenoMuro, ruta: str | Path) -> Path:
    ruta = Path(ruta)
    ruta.write_text(json.dumps({"cantidades": cantidades_json(caso, d), "memoria": memoria(caso, g, d)}, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta
