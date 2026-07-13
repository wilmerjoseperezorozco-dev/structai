"""
AquaAI — Módulo SUI: armado de reportes para el Sistema Único de Información
Referencia: Resolución SSPD 20101300048765 de 2010 (formatos SUI)
            Decreto 1575/2007 + Resolución 2115/2007 (IRCA)
            Ley 142/1994 Art. 53 (obligación de reporte)

El SUI (Sistema Único de Información de Servicios Públicos) es el portal de la
Superintendencia de Servicios Públicos donde los prestadores reportan mensualmente:
  - Tarifas cobradas por estrato
  - Suscriptores y consumos
  - Indicadores de calidad del agua (IRCA)
  - Indicadores de continuidad del servicio

Este módulo no envía al SUI directamente (el portal no tiene API pública) —
genera la estructura de datos lista para que el operador la ingrese o la
automatización futura la cargue via RPA/web scraping.
"""

from .schemas_tarifario import ReporteSUIRequest, ReporteSUIResponse, IndicadorSUI

# ─── Categorías IRCA (Resolución 2115/2007 + Decreto 1575/2007) ──────────────
def categoria_irca(irca: float) -> str:
    if irca == 0:            return "Sin riesgo"
    if irca <= 5:            return "Sin riesgo"
    if irca <= 14:           return "Riesgo bajo"
    if irca <= 35:           return "Riesgo medio"
    if irca <= 80:           return "Riesgo alto"
    return "Inviable para consumo humano"

def cumple_irca(irca: float) -> bool:
    return irca <= 5   # Solo "sin riesgo" cumple la Resolución 2115/2007

# ─── Indicadores mínimos exigidos por SUI ────────────────────────────────────
def calcular_indicadores(req: ReporteSUIRequest) -> list[IndicadorSUI]:
    indicadores = []

    # 1. IANC — Índice de Agua No Contabilizada
    ianc = ((req.volumen_producido_m3 - req.volumen_facturado_m3)
            / req.volumen_producido_m3 * 100)
    indicadores.append(IndicadorSUI(
        nombre="IANC — Índice de Agua No Contabilizada",
        valor=round(ianc, 2),
        unidad="%",
        rango_aceptable="≤ 25% (Ley 373/1997 + RAS Res. 0330/2017)",
        cumple=ianc <= 25,
    ))

    # 2. Cobertura (asumida del % de suscriptores respecto a la población)
    # En este módulo no tenemos población total — el campo es informativo
    indicadores.append(IndicadorSUI(
        nombre="Suscriptores activos reportados",
        valor=req.suscriptores_totales,
        unidad="suscriptores",
        rango_aceptable="100% de la zona de servicio",
        cumple=None,   # Requiere dato de población para calcular cobertura real
    ))

    # 3. Consumo medio por suscriptor
    consumo_medio = req.volumen_facturado_m3 / req.suscriptores_totales
    indicadores.append(IndicadorSUI(
        nombre="Consumo medio por suscriptor",
        valor=round(consumo_medio, 2),
        unidad="m³/suscriptor/mes",
        rango_aceptable="Varía según clima: frío ≤ 17m³, templado ≤ 20m³, cálido ≤ 24m³",
        cumple=None,
    ))

    # 4. Recaudo por m³ facturado
    recaudo_m3 = req.recaudo_total_cop / req.volumen_facturado_m3
    indicadores.append(IndicadorSUI(
        nombre="Recaudo por m³ facturado",
        valor=round(recaudo_m3, 2),
        unidad="$/m³",
        rango_aceptable="≥ tarifa cargo consumo estrato 3 vigente",
        cumple=recaudo_m3 >= req.tarifa_cargo_consumo_basico_estrato3 * 0.80,
    ))

    # 5. IRCA (si se provee)
    if req.irca_promedio is not None:
        indicadores.append(IndicadorSUI(
            nombre="IRCA — Índice de Riesgo de Calidad del Agua",
            valor=round(req.irca_promedio, 2),
            unidad="puntos (0-100)",
            rango_aceptable="≤ 5 puntos (Resolución 2115/2007)",
            cumple=cumple_irca(req.irca_promedio),
        ))

    # 6. Muestras conformes (si se provee)
    if req.muestras_tomadas and req.muestras_no_conformes is not None:
        pct_conformes = (1 - req.muestras_no_conformes / req.muestras_tomadas) * 100
        indicadores.append(IndicadorSUI(
            nombre="Muestras conformes de calidad de agua",
            valor=round(pct_conformes, 1),
            unidad="%",
            rango_aceptable="≥ 95% (Decreto 1575/2007)",
            cumple=pct_conformes >= 95,
        ))

    return indicadores


def generar_reporte_sui(req: ReporteSUIRequest) -> ReporteSUIResponse:
    ianc = round(
        (req.volumen_producido_m3 - req.volumen_facturado_m3)
        / req.volumen_producido_m3 * 100, 2
    )
    irca_cat = categoria_irca(req.irca_promedio) if req.irca_promedio is not None else "No reportado"
    indicadores = calcular_indicadores(req)
    alertas: list[str] = []

    # Alertas regulatorias
    if ianc > 25:
        alertas.append(
            f"IANC {ianc:.1f}% supera el límite del 25%. "
            "Obligación de presentar Plan de Reducción de Pérdidas ante Superservicios (Ley 373/1997 Art. 4)."
        )
    if req.irca_promedio is not None and req.irca_promedio > 5:
        alertas.append(
            f"IRCA {req.irca_promedio:.1f} — categoría '{irca_cat}'. "
            "Reportar a la Secretaría de Salud departamental y al SIVICAP (Decreto 1575/2007 Art. 11). "
            "Implementar plan de mejora de calidad."
        )
    if req.irca_promedio is not None and req.irca_promedio > 35:
        alertas.append(
            "IRCA > 35: agua INVIABLE o de alto riesgo. "
            "La SSPD puede ordenar intervención o medida de seguridad (Ley 142/1994 Art. 79)."
        )

    # Estructura campos SUI (campos principales del formulario mensual)
    anio, mes = req.periodo.split("-")
    campos_sui = {
        "_instrucciones": "Copiar estos valores en los formularios del portal SUI (sui.superservicios.gov.co)",
        "PERIODO_REPORTE":         req.periodo,
        "NIT_PRESTADOR":           req.nit_prestador,
        "MUNICIPIO":               req.municipio,
        "DEPARTAMENTO":            req.departamento,
        "SERVICIO":                req.servicio.value.upper(),
        "SUSCRIPTORES_TOTALES":    req.suscriptores_totales,
        "SUSCRIPTORES_ESTRATO":    req.suscriptores_por_estrato,
        "VOLUMEN_PRODUCIDO_M3":    req.volumen_producido_m3,
        "VOLUMEN_FACTURADO_M3":    req.volumen_facturado_m3,
        "IANC_PCT":                ianc,
        "RECAUDO_TOTAL_COP":       req.recaudo_total_cop,
        "TARIFA_CF_ESTRATO3":      req.tarifa_cargo_fijo_estrato3,
        "TARIFA_CC_BASICO_ESTRATO3": req.tarifa_cargo_consumo_basico_estrato3,
        "IRCA_PROMEDIO":           req.irca_promedio,
        "IRCA_CATEGORIA":          irca_cat,
        "MUESTRAS_TOMADAS":        req.muestras_tomadas,
        "MUESTRAS_NO_CONFORMES":   req.muestras_no_conformes,
    }

    return ReporteSUIResponse(
        periodo=req.periodo,
        prestador_nit=req.nit_prestador,
        municipio=req.municipio,
        ianc_pct=ianc,
        irca_categoria=irca_cat,
        indicadores=indicadores,
        campos_sui=campos_sui,
        alertas_regulatorias=alertas,
        normas_aplicadas=[
            "Ley 142/1994 Art. 53 — Obligación de reporte al SUI",
            "Decreto 1575/2007 — Sistema para la protección y control calidad del agua",
            "Resolución 2115/2007 — Parámetros de calidad y IRCA",
            "Ley 373/1997 — PUEAA y control de pérdidas (IANC)",
            "Res. CRA 688/2014 o 825/2017 — Metodología tarifaria vigente",
        ],
    )
