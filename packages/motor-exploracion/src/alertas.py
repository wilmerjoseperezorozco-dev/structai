"""Alertas del sitio y mediciones recomendadas, con la evidencia que las respalda (#273).

Todas las constantes vienen de análisis preregistrados en #273 (scripts/satelite y motor-pilotes/validacion).
Nada se extrapola: fuera de lo validado la salida dice "no aplica" o "sin dato", nunca un valor supuesto.
"""
from __future__ import annotations

# ── nivel freático por relieve (H2, H2b, H2c, H8) ──────────────────────────────────────────────────────────────────
UMBRAL_RELIEVE_M = 6.5          # H2: S = cota − mínima a ≤ 1 km; umbral de Youden en entrenamiento
HAMMOND_FRAC_SUAVE = 0.80       # H2c: Hammond (1964): > 80 % de la vecindad (5 km) con pendiente < 8 %
HAMMOND_RELIEVE_MAX_M = 90.0    #      y relieve local < 90 m
EVID_ALARMA = ("AUC 0,77 [0,67; 0,85] dentro de llanura de Hammond; VPP 0,78; sensibilidad 0,76, "
               "especificidad 0,64 (H2c). Validada fuera de muestra en Casanare (H2b). Solo validada en la Orinoquía.")
EVID_CABECERA = "Con la cabecera municipal la alarma queda por debajo del azar: AUC 0,42 [0,29; 0,56] (H8)."
EVID_FUERA = "Fuera de llanura la alarma solo se activa en el 3 % de los puntos (sensibilidad 0,15, H2c)."

# ── valor de medir el nivel freático (H7) y de la prueba de carga (H1) ──────────────────────────────────────────────
EVID_H7 = ("H7: en pilotes excavados, diseñar suponiendo perfil seco deja el 46 % [42; 50] de los sitios con "
           "capacidad real < 0,9·Q; suponer NF = 0 sobrecuesta en promedio 26 M$ [22; 30] en 30 pilotes, frente a "
           "~9,7 M$ de 10 m de perforación de prueba INVIAS (referencia alta de exploración).")
EVID_H7_HINCADO = ("H7: en pilotes hincados suponer NF = 0 dejó el 7-18 % de los sitios cortos; el nivel además "
                   "importa para licuación e hinca.")
EVID_H1 = {
    "cohesivo": ("evaluar", "H1: en arcilla blanda la prueba estática ahorra en promedio 34 % [24; 42] del costo de "
                 "los pilotes (30 pilotes, INVIAS 2026-1); se paga desde 1-5 pilotes."),
    "mixto": ("no_concluyente", "H1: en perfil mixto el ahorro es 12 % [3; 20]: no concluyente."),
    "granular": ("por_seguridad", "H1: en arena la prueba no ahorra en promedio (−0,5 % [−16; +13]), pero en el 42 % "
                 "de los sitios la capacidad real fue < 0,8 de la predicha: se justifica por seguridad, no por costo."),
    "desconocido": ("sin_dato", "H1: el valor de la prueba depende del suelo (arcilla: ahorra; arena: seguridad). "
                    "Defina el perfil con la exploración."),
}
REF_ALERTAS = "Análisis preregistrados en #273 (H1, H2, H2b, H2c, H7, H8); NSR-10 H.3, H.4.7.3 y H.10.2.1"


def es_llanura(frac_pendiente_suave: float, relieve_5km_m: float) -> bool:
    return frac_pendiente_suave > HAMMOND_FRAC_SUAVE and relieve_5km_m < HAMMOND_RELIEVE_MAX_M


def nivel_freatico(ubicacion: str, relieve_1km_m, frac_suave_5km, relieve_5km_m, nivel_medido_m) -> dict:
    if nivel_medido_m is not None:
        return {"estado": "medido", "nivel_m": nivel_medido_m,
                "mensaje": f"Nivel freático medido: {nivel_medido_m:g} m. Use el medido y confirme su variación "
                           "estacional (H.10.2.1)."}
    if ubicacion == "municipio":
        return {"estado": "sin_dato_lote",
                "mensaje": "Sin el punto del lote no se evalúa la alarma de relieve: mida el nivel freático.",
                "evidencia": EVID_CABECERA}
    if None in (relieve_1km_m, frac_suave_5km, relieve_5km_m):
        return {"estado": "sin_dato_dem",
                "mensaje": "Faltan métricas del modelo de elevación del lote: mida el nivel freático."}
    if not es_llanura(frac_suave_5km, relieve_5km_m):
        return {"estado": "no_aplica_terreno", "llanura": False,
                "mensaje": "La alarma de relieve no aplica en este terreno (no es llanura): mida el nivel freático.",
                "evidencia": EVID_FUERA}
    if relieve_1km_m <= UMBRAL_RELIEVE_M:
        return {"estado": "alarma", "llanura": True,
                "mensaje": "Alarma: el relieve del lote indica que es probable un nivel freático somero (≤ 2 m). "
                           "Mídalo antes de diseñar.",
                "evidencia": EVID_ALARMA}
    return {"estado": "sin_alarma", "llanura": True,
            "mensaje": "El relieve no indica nivel freático somero. Esto no significa que el nivel sea hondo: mídalo.",
            "evidencia": EVID_ALARMA}


def recomendaciones(cimentacion: str, suelo: str, amenaza_sismica: str, nf: dict,
                    n_eventos_remocion_5km: int | None) -> list[dict]:
    rec = []
    if nf["estado"] != "medido":
        if cimentacion == "pilote_excavado":
            rec.append({"medicion": "piezometro", "prioridad": "alta",
                        "motivo": "Pilotes excavados: el nivel freático cambia la longitud requerida.",
                        "evidencia": EVID_H7})
        else:
            ev = EVID_H7_HINCADO if cimentacion == "pilote_hincado" else \
                "NSR-10 H.10.2.1: debe determinarse el nivel freático y sus fluctuaciones estacionales."
            rec.append({"medicion": "piezometro", "prioridad": "alta" if nf["estado"] == "alarma" else "media",
                        "motivo": "Registre el nivel estabilizado en los sondeos o con piezómetro.", "evidencia": ev})
    if cimentacion in ("pilote_excavado", "pilote_hincado"):
        veredicto, ev = EVID_H1[suelo]
        rec.append({"medicion": "prueba_de_carga_estatica", "veredicto": veredicto,
                    "prioridad": "alta" if veredicto in ("evaluar", "por_seguridad") else "media",
                    "motivo": "NSR-10 H.4.7.3 permite reducir el factor de seguridad con pruebas de carga.",
                    "evidencia": ev})
    if suelo in ("granular", "mixto", "desconocido") and amenaza_sismica in ("intermedia", "alta"):
        rec.append({"medicion": "evaluacion_licuacion",
                    "prioridad": "alta" if nf["estado"] in ("alarma", "medido") else "media",
                    "motivo": "Suelo posiblemente granular en amenaza sísmica intermedia o alta: evalúe licuación "
                              "(SPT con finos y nivel freático; motor-licuacion). Un suelo licuable es perfil tipo F "
                              "(NSR-10 A.2.4).",
                    "evidencia": "Criterio normativo; no es un hallazgo de #273."})
    if n_eventos_remocion_5km:
        rec.append({"medicion": "estabilidad_de_taludes", "prioridad": "media",
                    "motivo": f"Hay {n_eventos_remocion_5km} eventos de remoción en masa (SIMMA) a ≤ 5 km del lote: "
                              "incluya la evaluación de estabilidad en el alcance del estudio.",
                    "evidencia": "H4: el inventario por cabecera subestima; el conteo a 5 km del lote es contexto, "
                                 "no una amenaza calculada."})
    return rec
