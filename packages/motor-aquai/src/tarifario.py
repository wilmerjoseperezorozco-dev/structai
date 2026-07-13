"""
AquaAI — Motor tarifario CRA
Referencia: CRA 688/2014, CRA 825/2017, CRA 943/2021, CRA 750/2016, Ley 142/1994

Metodología general:
  CMLP = CMI + CMO + CMA_unitario

  Cargo Fijo (CF)        = CMA  [$/suscriptor/mes]
  Cargo por Consumo (CC) = CMI + CMO + CMA_distribuido  [$/m³]

  La tarifa que paga cada suscriptor varía por estrato según los
  factores de subsidio y contribución de la Ley 142/1994.

Estructura de consumo (CRA por clima):
  ┌─────────────┬────────────┬────────────────┬──────────────┐
  │   Clima     │  Básico    │ Complementario │  Suntuario   │
  ├─────────────┼────────────┼────────────────┼──────────────┤
  │  Frío       │  ≤ 11 m³  │  11 – 17 m³   │  > 17 m³    │
  │  Templado   │  ≤ 13 m³  │  13 – 20 m³   │  > 20 m³    │
  │  Cálido     │  ≤ 16 m³  │  16 – 24 m³   │  > 24 m³    │
  └─────────────┴────────────┴────────────────┴──────────────┘
"""

from .schemas_tarifario import (
    TarifaRequest, TarifaResponse, TipoPrestador,
    ComponenteTarifa, TarifaEstrato,
)

# ─── Tablas normativas fijas ──────────────────────────────────────────────────

# Límites de consumo básico y complementario por clima (m³/suscriptor/mes)
CONSUMO_BASICO: dict[str, float] = {
    "frio":     11.0,
    "templado": 13.0,
    "calido":   16.0,
}
CONSUMO_COMPLEMENTARIO_FACTOR = 1.545  # complementario = básico × 1.545 (aprox. CRA)

# Factores de subsidio y contribución sobre el cargo por consumo básico
# Fuente: Ley 142/1994 Art. 99, Decreto 1013/2005, actualizados por jurisprudencia CRA
# Positivo = subsidio (descuento al suscriptor)
# Negativo = contribución (recargo al suscriptor, financia subsidios)
FACTORES_ESTRATO: dict[str, dict] = {
    "1":          {"factor": 0.70,   "tipo": "subsidio",      "descripcion": "Subsidio máximo 70% sobre consumo básico"},
    "2":          {"factor": 0.40,   "tipo": "subsidio",      "descripcion": "Subsidio 40% sobre consumo básico"},
    "3":          {"factor": 0.00,   "tipo": "equilibrio",    "descripcion": "Sin subsidio ni contribución"},
    "4":          {"factor": -0.10,  "tipo": "contribucion",  "descripcion": "Contribución solidaria 10%"},
    "5":          {"factor": -0.20,  "tipo": "contribucion",  "descripcion": "Contribución solidaria 20%"},
    "6":          {"factor": -0.20,  "tipo": "contribucion",  "descripcion": "Contribución solidaria 20%"},
    "comercial":  {"factor": -0.50,  "tipo": "contribucion",  "descripcion": "Contribución sector comercial 50%"},
    "industrial": {"factor": -0.30,  "tipo": "contribucion",  "descripcion": "Contribución sector industrial 30%"},
    "oficial":    {"factor": 0.00,   "tipo": "equilibrio",    "descripcion": "Entidades oficiales: sin subsidio ni contribución"},
}

# Incremento por consumo complementario y suntuario (porcentaje sobre CC básico)
INCREMENTO_COMPLEMENTARIO = 0.20   # +20% sobre tarifa base — CRA
INCREMENTO_SUNTUARIO      = 0.60   # +60% sobre tarifa base — CRA

# Norma de referencia por tipo de prestador
NORMA_REF: dict[str, str] = {
    "grande":  "Res. CRA 688/2014 + Res. CRA 943/2021 (período tarifario 2021-2026)",
    "pequeno": "Res. CRA 825/2017 — Pequeños prestadores (≤ 5.000 suscriptores)",
    "rural":   "Res. CRA 750/2016 — Esquemas diferenciales zonas rurales",
}


# ─── Motor de cálculo ─────────────────────────────────────────────────────────

def calcular_tarifa(req: TarifaRequest) -> TarifaResponse:
    clima   = req.clima.lower()
    perdidas = req.factor_perdidas
    advertencias: list[str] = []

    if clima not in CONSUMO_BASICO:
        raise ValueError(f"Clima '{clima}' no reconocido. Use: frio | templado | calido")

    # ── 1. Consumos de referencia ───────────────────────────────────────────
    cb  = CONSUMO_BASICO[clima]
    cc_lim = round(cb * CONSUMO_COMPLEMENTARIO_FACTOR, 1)

    # ── 2. CMLP y componentes ──────────────────────────────────────────────
    # CMI y CMO se expresan en $/m³ de agua producida
    # Se ajustan por pérdidas para llevarlos a $/m³ facturado
    factor_perdidas = 1 / (1 - perdidas)

    cmi_ajustado = req.costo_medio_inversion_cmi * factor_perdidas
    cmo_ajustado = req.costo_medio_operacion_cmo * factor_perdidas

    # CMA en $/suscriptor/mes → se distribuye por consumo medio para obtener $/m³
    cma_unitario = req.costo_medio_administracion_cma / req.consumo_medio_facturado_m3

    cmlp = cmi_ajustado + cmo_ajustado + cma_unitario

    # ── 3. Cargos base ─────────────────────────────────────────────────────
    cargo_fijo = req.costo_medio_administracion_cma          # $/suscriptor/mes
    cc_basico  = cmi_ajustado + cmo_ajustado + cma_unitario  # $/m³ (igual al CMLP)
    cc_compl   = round(cc_basico * (1 + INCREMENTO_COMPLEMENTARIO), 2)
    cc_suntuario = round(cc_basico * (1 + INCREMENTO_SUNTUARIO), 2)

    tarifa_base = ComponenteTarifa(
        cargo_fijo_mes=round(cargo_fijo, 2),
        cargo_consumo_basico_m3=round(cc_basico, 2),
        cargo_consumo_compl_m3=cc_compl,
        cargo_consumo_suntuario_m3=cc_suntuario,
        consumo_basico_limite_m3=cb,
        consumo_complementario_limite_m3=cc_lim,
    )

    # ── 4. Tarifas por estrato ─────────────────────────────────────────────
    norma = NORMA_REF[req.tipo_prestador.value]
    tarifas_estrato: list[TarifaEstrato] = []

    for estrato, datos in FACTORES_ESTRATO.items():
        f = datos["factor"]
        if datos["tipo"] == "subsidio":
            cf_aplicado  = round(cargo_fijo * (1 - f), 2)
            cc_aplicado  = round(cc_basico  * (1 - f), 2)
        else:
            # Contribución: el suscriptor paga la tarifa + el recargo
            cf_aplicado  = round(cargo_fijo * (1 + abs(f)), 2)
            cc_aplicado  = round(cc_basico  * (1 + abs(f)), 2)

        tarifas_estrato.append(TarifaEstrato(
            estrato=estrato,
            cargo_fijo_aplicado=cf_aplicado,
            cargo_consumo_basico_aplicado=cc_aplicado,
            factor_subsidio_contribucion=f,
            tipo=datos["tipo"],
            norma_ref=norma,
        ))

    # ── 5. Advertencias ────────────────────────────────────────────────────
    if perdidas > 0.30:
        advertencias.append(
            f"IANC {perdidas*100:.0f}% supera el 30% — Superservicios puede iniciar investigación. "
            "Implementar PUEAA (Ley 373/1997) de inmediato."
        )
    if req.tipo_prestador == TipoPrestador.PEQUENO and cmlp > 8000:
        advertencias.append(
            "CMLP > $8.000/m³ es alto para un pequeño prestador. "
            "Verificar si los costos de inversión están correctamente amortizados (Res. CRA 825/2017 Art. 12)."
        )
    if req.tipo_prestador == TipoPrestador.RURAL:
        advertencias.append(
            "Prestador en zona rural: aplicar Res. CRA 750/2016. "
            "Los municipios pueden aportar subsidios directos adicionales vía transferencias del SGP."
        )

    # ── 6. Ejemplo de factura (estrato 3, consumo medio) ──────────────────
    consumo_ej = req.consumo_medio_facturado_m3
    if consumo_ej <= cb:
        valor_consumo = consumo_ej * cc_basico
    elif consumo_ej <= cc_lim:
        valor_consumo = cb * cc_basico + (consumo_ej - cb) * cc_compl
    else:
        valor_consumo = (cb * cc_basico
                         + (cc_lim - cb) * cc_compl
                         + (consumo_ej - cc_lim) * cc_suntuario)

    ejemplo = {
        "estrato":          3,
        "consumo_m3":       consumo_ej,
        "cargo_fijo_cop":   round(cargo_fijo, 0),
        "cargo_consumo_cop": round(valor_consumo, 0),
        "total_factura_cop": round(cargo_fijo + valor_consumo, 0),
        "nota": f"Consumo ejemplo: {consumo_ej} m³ en clima {clima}. Estrato 3 sin subsidio ni contribución.",
    }

    return TarifaResponse(
        tarifa_base=tarifa_base,
        tarifas_por_estrato=tarifas_estrato,
        cmlp_m3=round(cmlp, 2),
        metodologia_aplicada=norma,
        norma_ref=norma,
        advertencias=advertencias,
        ejemplo_factura=ejemplo,
    )
