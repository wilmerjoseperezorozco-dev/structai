"""
══════════════════════════════════════════════════════════════
MOTOR TOPOVÍA — ENGINE DE CÁLCULO
Poligonales, volúmenes, curvas, pavimentos — Colombia
══════════════════════════════════════════════════════════════
"""
import math
from typing import Optional
from .models import (
    Punto, Vertice, LadoPoligonal, ResultadoPoligonal,
    SeccionTransversal, ResultadoVolumen, DiagramaMasas,
    CurvaHorizontal, ResultadoPavimento,
    OrdenPoligonal, MetodoCompensacion, CategoriaVia, TipoTerreno,
    TOLERANCIA_ANGULAR, PRECISION_LINEAL, VELOCIDADES_DISENO,
)


# ═══════════════════════════════════════════════════════════════
# 1. MOTOR DE POLIGONALES
# ═══════════════════════════════════════════════════════════════

def calcular_poligonal_cerrada(
    vertices: list[Vertice],
    azimut_inicial: float,
    norte_inicial: float,
    este_inicial: float,
    orden: OrdenPoligonal = OrdenPoligonal.TOPOGRAFICO,
    metodo: MetodoCompensacion = MetodoCompensacion.BOWDITCH,
) -> ResultadoPoligonal:
    """
    Calcula poligonal cerrada completa.

    Args:
        vertices: lista de vértices con ángulo horizontal y distancia
        azimut_inicial: azimut del primer lado (grados decimales)
        norte_inicial: coordenada norte del primer vértice
        este_inicial: coordenada este del primer vértice
        orden: orden de precisión requerido (IGAC)
        metodo: método de compensación (Bowditch o Tránsito)

    Returns:
        ResultadoPoligonal con coordenadas compensadas y diagnóstico
    """
    n = len(vertices)

    # ── Cierre angular ──
    suma_teorica = (n - 2) * 180.0
    suma_observada = sum(v.angulo_horizontal for v in vertices)
    error_angular_grados = suma_observada - suma_teorica
    error_angular_seg = error_angular_grados * 3600.0

    tol_factor = TOLERANCIA_ANGULAR[orden]
    tolerancia_seg = tol_factor * math.sqrt(n)
    cumple_angular = abs(error_angular_seg) <= tolerancia_seg

    # ── Corrección angular (distribuir equitativamente) ──
    correccion_por_vertice = -error_angular_grados / n
    angulos_corregidos = [
        v.angulo_horizontal + correccion_por_vertice for v in vertices
    ]

    # ── Calcular azimuts ──
    azimuts: list[float] = [azimut_inicial]
    for i in range(1, n):
        az = azimuts[i - 1] + 180.0 + angulos_corregidos[i]
        az = az % 360.0
        azimuts.append(az)

    # ── Calcular proyecciones ──
    distancias = [v.distancia_al_siguiente for v in vertices]
    delta_nortes = [
        d * math.cos(math.radians(az))
        for d, az in zip(distancias, azimuts)
    ]
    delta_estes = [
        d * math.sin(math.radians(az))
        for d, az in zip(distancias, azimuts)
    ]

    # ── Error lineal ──
    error_norte = sum(delta_nortes)
    error_este = sum(delta_estes)
    error_lineal = math.sqrt(error_norte**2 + error_este**2)
    perimetro = sum(distancias)
    precision = error_lineal / perimetro if perimetro > 0 else float("inf")
    precision_requerida = PRECISION_LINEAL[orden]
    cumple_lineal = precision <= precision_requerida

    # ── Compensación ──
    dn_corregidos: list[float] = []
    de_corregidos: list[float] = []

    if metodo == MetodoCompensacion.BOWDITCH:
        for i in range(n):
            corr_n = -(error_norte * distancias[i]) / perimetro
            corr_e = -(error_este * distancias[i]) / perimetro
            dn_corregidos.append(delta_nortes[i] + corr_n)
            de_corregidos.append(delta_estes[i] + corr_e)
    else:  # Tránsito
        sum_abs_dn = sum(abs(dn) for dn in delta_nortes) or 1.0
        sum_abs_de = sum(abs(de) for de in delta_estes) or 1.0
        for i in range(n):
            corr_n = -(error_norte * abs(delta_nortes[i])) / sum_abs_dn
            corr_e = -(error_este * abs(delta_estes[i])) / sum_abs_de
            dn_corregidos.append(delta_nortes[i] + corr_n)
            de_corregidos.append(delta_estes[i] + corr_e)

    # ── Coordenadas finales ──
    lados: list[LadoPoligonal] = []
    coordenadas: list[Punto] = []
    norte_actual = norte_inicial
    este_actual = este_inicial

    coordenadas.append(Punto(
        id=vertices[0].id,
        norte=norte_actual,
        este=este_actual,
        cota=vertices[0].cota,
    ))

    for i in range(n):
        j = (i + 1) % n
        lado = LadoPoligonal(
            desde=vertices[i].id,
            hasta=vertices[j].id,
            azimut=azimuts[i],
            distancia=distancias[i],
            delta_norte=delta_nortes[i],
            delta_este=delta_estes[i],
            delta_norte_corregido=dn_corregidos[i],
            delta_este_corregido=de_corregidos[i],
        )
        lados.append(lado)

        norte_actual += dn_corregidos[i]
        este_actual += de_corregidos[i]

        if j != 0:
            coordenadas.append(Punto(
                id=vertices[j].id,
                norte=norte_actual,
                este=este_actual,
                cota=vertices[j].cota,
            ))

    return ResultadoPoligonal(
        vertices=vertices,
        lados=lados,
        coordenadas_finales=coordenadas,
        suma_angulos_observados=suma_observada,
        suma_angulos_teorica=suma_teorica,
        error_angular=error_angular_seg,
        tolerancia_angular=tolerancia_seg,
        cumple_angular=cumple_angular,
        error_norte=error_norte,
        error_este=error_este,
        error_lineal=error_lineal,
        perimetro=perimetro,
        precision=1 / precision if precision > 0 else float("inf"),
        precision_requerida=1 / precision_requerida,
        cumple_lineal=cumple_lineal,
        metodo_compensacion=metodo,
        orden=orden,
    )


# ═══════════════════════════════════════════════════════════════
# 2. MOTOR DE VOLÚMENES
# ═══════════════════════════════════════════════════════════════

def area_seccion(puntos: list[tuple[float, float]], ancho_corona: float) -> tuple[float, float]:
    """
    Calcula área de corte y relleno de una sección transversal.

    Args:
        puntos: lista de (distancia_al_eje, cota_relativa_a_rasante)
                cota positiva = corte, negativa = relleno
        ancho_corona: ancho total de la corona (m)

    Returns:
        (area_corte, area_relleno) en m²
    """
    if len(puntos) < 2:
        return 0.0, 0.0

    sorted_pts = sorted(puntos, key=lambda p: p[0])
    area_corte = 0.0
    area_relleno = 0.0

    for i in range(len(sorted_pts) - 1):
        x1, y1 = sorted_pts[i]
        x2, y2 = sorted_pts[i + 1]
        dx = x2 - x1
        area_trap = dx * (y1 + y2) / 2.0

        if area_trap > 0:
            area_corte += area_trap
        else:
            area_relleno += abs(area_trap)

    return area_corte, area_relleno


def calcular_volumenes(
    secciones: list[SeccionTransversal],
    ancho_corona: float = 7.3,
    factor_abundamiento: float = 1.25,
    factor_compactacion: float = 0.90,
) -> tuple[list[ResultadoVolumen], list[DiagramaMasas]]:
    """
    Calcula volúmenes de corte y relleno entre secciones por áreas medias
    y genera el diagrama de masas (Bruckner).

    Args:
        secciones: lista de secciones transversales ordenadas por abscisa
        ancho_corona: ancho de corona de la vía (m)
        factor_abundamiento: factor de expansión del material (INVÍAS)
        factor_compactacion: factor de contracción al compactar

    Returns:
        (lista de volúmenes, diagrama de masas)
    """
    secciones_ord = sorted(secciones, key=lambda s: s.abscisa)
    resultados: list[ResultadoVolumen] = []
    diagrama: list[DiagramaMasas] = []

    vol_corte_acum = 0.0
    vol_relleno_acum = 0.0
    masa_acum = 0.0

    diagrama.append(DiagramaMasas(
        abscisa=secciones_ord[0].abscisa,
        ordenada=0.0,
        volumen_corte_acumulado=0.0,
        volumen_relleno_acumulado=0.0,
    ))

    for i in range(len(secciones_ord) - 1):
        s1 = secciones_ord[i]
        s2 = secciones_ord[i + 1]
        dist = s2.abscisa - s1.abscisa

        # Convertir puntos a cotas relativas a rasante
        puntos_1 = [
            (d, s1.cota_eje_terreno + c - s1.cota_eje_rasante)
            for d, c in s1.puntos
        ] if s1.cota_eje_rasante > 0 else s1.puntos

        puntos_2 = [
            (d, s2.cota_eje_terreno + c - s2.cota_eje_rasante)
            for d, c in s2.puntos
        ] if s2.cota_eje_rasante > 0 else s2.puntos

        ac1, ar1 = area_seccion(puntos_1, ancho_corona)
        ac2, ar2 = area_seccion(puntos_2, ancho_corona)

        vol_corte = dist * (ac1 + ac2) / 2.0
        vol_relleno = dist * (ar1 + ar2) / 2.0

        resultados.append(ResultadoVolumen(
            abscisa_inicio=s1.abscisa,
            abscisa_fin=s2.abscisa,
            area_corte_1=ac1,
            area_corte_2=ac2,
            area_relleno_1=ar1,
            area_relleno_2=ar2,
            volumen_corte=vol_corte,
            volumen_relleno=vol_relleno,
            distancia=dist,
        ))

        vol_corte_acum += vol_corte
        vol_relleno_acum += vol_relleno
        masa_acum += vol_corte * factor_compactacion - vol_relleno * factor_abundamiento

        diagrama.append(DiagramaMasas(
            abscisa=s2.abscisa,
            ordenada=masa_acum,
            volumen_corte_acumulado=vol_corte_acum,
            volumen_relleno_acumulado=vol_relleno_acum,
        ))

    return resultados, diagrama


# ═══════════════════════════════════════════════════════════════
# 3. MOTOR DE CURVAS HORIZONTALES
# ═══════════════════════════════════════════════════════════════

def calcular_curva_horizontal(
    radio: float,
    deflexion_grados: float,
    pi_abscisa: float,
    pi_norte: float = 0.0,
    pi_este: float = 0.0,
) -> CurvaHorizontal:
    """
    Calcula elementos de curva circular simple.

    Args:
        radio: radio de la curva (m)
        deflexion_grados: ángulo de deflexión Δ (grados decimales)
        pi_abscisa: abscisa del PI
        pi_norte: coordenada norte del PI
        pi_este: coordenada este del PI

    Returns:
        CurvaHorizontal con todos los elementos calculados
    """
    d_rad = math.radians(deflexion_grados)

    tangente = radio * math.tan(d_rad / 2)
    longitud = radio * d_rad
    externa = radio * (1 / math.cos(d_rad / 2) - 1)
    ordenada_media = radio * (1 - math.cos(d_rad / 2))
    cuerda_larga = 2 * radio * math.sin(d_rad / 2)

    pc_abscisa = pi_abscisa - tangente
    pt_abscisa = pc_abscisa + longitud

    return CurvaHorizontal(
        pi_norte=pi_norte,
        pi_este=pi_este,
        radio=radio,
        deflexion=deflexion_grados,
        tangente=tangente,
        longitud=longitud,
        externa=externa,
        ordenada_media=ordenada_media,
        cuerda_larga=cuerda_larga,
        pc_abscisa=pc_abscisa,
        pt_abscisa=pt_abscisa,
    )


def puntos_replanteo_curva(
    curva: CurvaHorizontal,
    intervalo: float = 10.0,
) -> list[tuple[float, float, float]]:
    """
    Genera puntos de replanteo por deflexiones.

    Args:
        curva: curva horizontal calculada
        intervalo: intervalo de estaqueo (m)

    Returns:
        lista de (abscisa, deflexión_acumulada_grados, cuerda_m)
    """
    puntos: list[tuple[float, float, float]] = []
    l_actual = 0.0

    while l_actual <= curva.longitud + 0.001:
        defl_rad = l_actual / (2 * curva.radio)
        defl_grados = math.degrees(defl_rad)
        cuerda = 2 * curva.radio * math.sin(defl_rad)
        abscisa = curva.pc_abscisa + l_actual

        puntos.append((abscisa, defl_grados, cuerda))

        if l_actual == curva.longitud:
            break
        l_actual = min(l_actual + intervalo, curva.longitud)

    return puntos


def radio_minimo_invias(
    velocidad_kmh: int,
    peralte_max: float = 0.08,
) -> float:
    """
    Radio mínimo según INVÍAS.
    R_min = V² / (127 × (e_max + f_max))
    """
    friccion = {
        20: 0.18, 30: 0.17, 40: 0.17, 50: 0.16,
        60: 0.15, 70: 0.15, 80: 0.14, 90: 0.13,
        100: 0.12, 110: 0.10,
    }
    f = friccion.get(velocidad_kmh, 0.14)
    return velocidad_kmh**2 / (127 * (peralte_max + f))


# ═══════════════════════════════════════════════════════════════
# 4. MOTOR DE PAVIMENTOS AASHTO 93
# ═══════════════════════════════════════════════════════════════

def cbr_a_mr(cbr: float) -> float:
    """CBR → Módulo resiliente (psi). Correlación INVÍAS: M_R = 2555 × CBR^0.64"""
    return 2555.0 * cbr**0.64


def calcular_sn_flexible(
    w18: float,
    mr_psi: float,
    confiabilidad: float = 0.85,
    so: float = 0.45,
    po: float = 4.2,
    pt: float = 2.0,
) -> float:
    """
    Calcula SN requerido con AASHTO 93 (pavimento flexible).
    Resuelve iterativamente la ecuación fundamental.
    """
    zr_table = {
        0.60: -0.253, 0.75: -0.674, 0.85: -1.037,
        0.90: -1.282, 0.95: -1.645, 0.99: -2.327, 0.999: -3.090,
    }
    zr = zr_table.get(confiabilidad, -1.037)
    delta_psi = po - pt
    log_w18 = math.log10(w18)

    sn = 1.0
    for _ in range(200):
        term1 = zr * so
        term2 = 9.36 * math.log10(sn + 1) - 0.20
        term3 = math.log10(delta_psi / (4.2 - 1.5)) / (
            0.40 + 1094.0 / (sn + 1) ** 5.19
        )
        term4 = 2.32 * math.log10(mr_psi) - 8.07
        w18_calc = term1 + term2 + term3 + term4

        if abs(w18_calc - log_w18) < 0.001:
            break

        if w18_calc < log_w18:
            sn += 0.05
        else:
            sn -= 0.01
            if sn < 0.5:
                sn = 0.5

    return round(sn, 2)


def disenar_pavimento_flexible(
    cbr: float,
    w18: float,
    confiabilidad: float = 0.85,
    a1: float = 0.44,
    a2: float = 0.14,
    a3: float = 0.11,
    m2: float = 1.0,
    m3: float = 1.0,
) -> ResultadoPavimento:
    """
    Diseño completo de pavimento flexible AASHTO 93.

    Args:
        cbr: CBR de subrasante (%)
        w18: ejes equivalentes de 8.2 ton
        confiabilidad: nivel de confiabilidad (0-1)
        a1-a3: coeficientes estructurales (MDC, base, subbase)
        m2-m3: coeficientes de drenaje

    Returns:
        ResultadoPavimento con espesores y validación
    """
    mr = cbr_a_mr(cbr)
    sn_req = calcular_sn_flexible(w18, mr, confiabilidad)

    # Espesores mínimos según tránsito (INVÍAS)
    if w18 < 50_000:
        d1_min, d2_min, d3_min = 0.0, 10.0, 10.0
    elif w18 < 150_000:
        d1_min, d2_min, d3_min = 5.0, 10.0, 10.0
    elif w18 < 500_000:
        d1_min, d2_min, d3_min = 6.5, 10.0, 10.0
    elif w18 < 2_000_000:
        d1_min, d2_min, d3_min = 7.5, 15.0, 15.0
    elif w18 < 7_000_000:
        d1_min, d2_min, d3_min = 9.0, 15.0, 15.0
    else:
        d1_min, d2_min, d3_min = 10.0, 15.0, 15.0

    # cm → pulgadas para SN
    d1_in = d1_min / 2.54
    d2_in = d2_min / 2.54
    d3_in = d3_min / 2.54

    sn_prov = a1 * d1_in + a2 * m2 * d2_in + a3 * m3 * d3_in

    # Ajustar subbase si SN insuficiente
    while sn_prov < sn_req:
        d3_min += 5.0
        d3_in = d3_min / 2.54
        sn_prov = a1 * d1_in + a2 * m2 * d2_in + a3 * m3 * d3_in

    return ResultadoPavimento(
        sn_requerido=sn_req,
        espesor_carpeta_cm=d1_min,
        espesor_base_cm=d2_min,
        espesor_subbase_cm=d3_min,
        sn_proporcionado=round(sn_prov, 2),
        cbr_subrasante=cbr,
        mr_psi=round(mr, 0),
        w18=w18,
        confiabilidad=confiabilidad,
        cumple=sn_prov >= sn_req,
    )


# ═══════════════════════════════════════════════════════════════
# 5. UTILIDADES
# ═══════════════════════════════════════════════════════════════

def gms_a_decimal(grados: int, minutos: int, segundos: float) -> float:
    """Convierte grados-minutos-segundos a grados decimales."""
    return grados + minutos / 60.0 + segundos / 3600.0


def decimal_a_gms(decimal: float) -> tuple[int, int, float]:
    """Convierte grados decimales a (grados, minutos, segundos)."""
    g = int(decimal)
    resto = (decimal - g) * 60
    m = int(resto)
    s = (resto - m) * 60
    return g, m, round(s, 2)


def azimut_a_rumbo(azimut: float) -> str:
    """Convierte azimut (0-360) a rumbo (N45°30'E)."""
    az = azimut % 360
    if az <= 90:
        g, m, s = decimal_a_gms(az)
        return f"N {g}°{m:02d}'{s:05.2f}\" E"
    elif az <= 180:
        g, m, s = decimal_a_gms(180 - az)
        return f"S {g}°{m:02d}'{s:05.2f}\" E"
    elif az <= 270:
        g, m, s = decimal_a_gms(az - 180)
        return f"S {g}°{m:02d}'{s:05.2f}\" W"
    else:
        g, m, s = decimal_a_gms(360 - az)
        return f"N {g}°{m:02d}'{s:05.2f}\" W"
