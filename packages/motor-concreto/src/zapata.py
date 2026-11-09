"""Zapata aislada rectangular de concreto reforzado — NSR-10 C.15 (con C.11.11, C.10.14, C.10.5.4, C.7.12.2).

Qué verifica (cada numeral se leyó en `nsr10_chunks` el 2026-11-08):
- Presión de contacto de servicio ≤ q_adm (C.15.2.2; q_adm la entrega el estudio geotécnico, H.4.2.3).
- Altura mínima: d ≥ 150 mm sobre suelo (C.15.7).
- Flexión en la cara de la columna (C.15.4.2a), φ = 0,90 (C.9.3.2.1), refuerzo mínimo ρ = 0,0018 con fy 420 (C.15.10.4/C.10.5.4/C.7.12.2.1),
  separación máxima min(3h, 450 mm) (C.10.5.4), distribución γs = 2/(β+1) en la franja central (C.15.4.4.2, ec. C.15-1).
- Cortante como viga a d de la cara: Vc = 0,17 λ √f'c b d, φ = 0,75 (C.11.1.3.1, C.11.2.1.1, C.15.5.1).
- Punzonamiento: Vc = menor de C.11-31, C.11-32, C.11-33 (C.11.11.2.1), sección crítica a d/2 (C.11.11.1.2).
- Aplastamiento: φ 0,85 f'c A1 √(A2/A1), tope 2 (C.10.14.1), φ = 0,65 (C.9.3.2.4); dovelas ≥ 0,005 Ag (C.15.8.2.1).
- Columna circular → cuadrado de igual área (C.15.3).

NO verificado / fuera del alcance (se devuelve en `supuestos`): longitud de desarrollo (C.15.6 → C.12), recubrimiento contra el suelo (75 mm, C.7.7.1(a), ya verificado en el corpus),
separación libre entre barras (C.7.6), transferencia de momento no balanceado en el punzonamiento (C.11.11.7), zapatas combinadas/medianeras/sobre pilotes,
asentamientos (los calcula el geotecnista; aquí solo se comparan con los límites de H.4.9).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .viga import AREA_MM2, DIAMETRO_MM, PHI_CORTANTE, PHI_FLEXION, Materiales, beta1

PHI_APLASTAMIENTO = 0.65
PESO_CONCRETO_KN_M3 = 24.0
H_MIN_D_MM = 150.0
SEP_MAX_ABS_MM = 450.0
LIMITES_ASENT_TOTAL_MM = {"aislada": 300.0, "medianera": 150.0}          # H.4.9.2 (20 años)
LIMITES_ASENT_DIF = {"acabados_sensibles": 1 / 1000, "muros_carga": 1 / 500, "porticos_concreto": 1 / 300, "acero": 1 / 160}  # Tabla H.4.9-1
LIMITE_GIRO = 1 / 250                                                       # H.4.9.4
FS_CARGA_MUERTA_VIVA = 3.0                                                  # Tabla H.4.7-1, única fila verificada

SUPUESTOS = (
    "q_adm proviene del estudio geotécnico (H.4.2.3); el Título H no da fórmula de capacidad portante.",
    "Longitud de desarrollo (C.15.6/C.12) NO verificada: se informa solo el largo disponible desde la cara de la columna.",
    "Recubrimiento contra el suelo: 75 mm verificado en C.7.7.1(a) (valor por defecto); separación libre de barras (C.7.6) NO verificada en el corpus.",
    "Punzonamiento con momento no balanceado (C.11.11.7) NO modelado: con momento se usa la presión mínima de la zapata (conservador, no normativo).",
    "Zapata concéntrica sobre columna de concreto; sin pedestal; sin cabezal de pilotes.",
    "Requiere revisión y firma de un ingeniero estructural (issue #18).",
)


@dataclass(frozen=True)
class CargasZapata:
    """Fuerzas en la base de la columna. P positivo en compresión [kN]; Mx, My [kN·m] (My causa excentricidad en x).
    Servicio y última se dan por separado porque las combinaciones las define el llamador (B.2)."""
    P_serv: float
    P_u: float
    Mx_serv: float = 0.0
    My_serv: float = 0.0
    Mx_u: float = 0.0
    My_u: float = 0.0


@dataclass(frozen=True)
class Suelo:
    q_adm_kpa: float                    # capacidad admisible BRUTA del informe geotécnico
    profundidad_desplante_m: float = 1.5
    peso_unitario_relleno_kn_m3: float = 17.0
    ks_kn_m3: float = 0.0               # módulo de balasto; 0 = no se verifica asentamiento
    asentamiento_max_mm: float = 25.0   # límite de servicio (valor de referencia SIN fuente en el corpus; parámetro del proyecto)


@dataclass(frozen=True)
class Verif:
    norma: str
    nombre: str
    demanda: float
    capacidad: float
    unidad: str
    cumple: bool


@dataclass(frozen=True)
class DisenoZapata:
    Lx: float
    Ly: float
    h: float
    d: float
    barras_x: str
    barras_y: str
    As_x: float
    As_y: float
    q_max_serv: float
    q_min_serv: float
    volumen_concreto_m3: float
    masa_acero_kg: float
    verificaciones: tuple
    advertencias: tuple
    cumple: bool = field(default=False)


def _lado_equivalente(c1: float, c2: float, circular: bool) -> tuple[float, float]:
    if circular:                                           # c1 = diámetro; C.15.3
        lado = math.sqrt(math.pi * c1**2 / 4)
        return lado, lado
    return c1, c2


def presiones_servicio(c: CargasZapata, s: Suelo, Lx: float, Ly: float, h: float) -> tuple[float, float]:
    """(q_max, q_min) kPa con peso propio y relleno; Lx, Ly, h en m. Linealidad completa (sin despegue)."""
    A = Lx * Ly
    extra = PESO_CONCRETO_KN_M3 * h + s.peso_unitario_relleno_kn_m3 * max(s.profundidad_desplante_m - h, 0.0)
    N = c.P_serv / A + extra
    ex = 6 * c.My_serv / (c.P_serv * Lx) if c.P_serv else 0.0
    ey = 6 * c.Mx_serv / (c.P_serv * Ly) if c.P_serv else 0.0
    p_m = c.P_serv / A
    return N + p_m * (abs(ex) + abs(ey)), N - p_m * (abs(ex) + abs(ey))


def _as_flexion(Mu_knm: float, b: float, d: float, fc: float, fy: float) -> float:
    """Área de acero [mm²] para Mu [kN·m] con bloque rectangular y φ=0,90; b, d en mm. inf si no cabe."""
    Mu = Mu_knm * 1e6 / PHI_FLEXION
    a = d
    As = 0.0
    disc = (0.85 * fc * b * d) ** 2 - 2 * 0.85 * fc * b * Mu
    if disc < 0:
        return math.inf
    a = (0.85 * fc * b * d - math.sqrt(disc)) / (0.85 * fc * b)
    As = 0.85 * fc * b * a / fy
    return As


def _rho_min(fy: float) -> float:
    if fy <= 350:
        return 0.0020
    return max(0.0018 * 420.0 / fy, 0.0014)


def _momento_cara(p_prom_kpa: float, pendiente_kpa_m: float, L: float, B: float, c: float) -> float:
    """Momento [kN·m] en la cara de la columna: ∫ p(x)·B·(x - xc) dx de la cara al borde (el lado más cargado).
    p(x)=p_prom + pendiente·(x-L/2); L,B,c en m. Se toma el voladizo con mayor momento."""
    voladizo = (L - c) / 2
    s = np.linspace(0.0, voladizo, 201)
    mejor = 0.0
    for signo in (1, -1):
        x_rel = c / 2 + s                                    # distancia al eje de la columna
        p = np.maximum(p_prom_kpa + signo * pendiente_kpa_m * x_rel, 0.0)
        mejor = max(mejor, float(np.trapezoid(p * B * s, s)))
    return mejor


def _barras(As_req: float, ancho_mm: float, h: float, fy: float, sep_max: float) -> Optional[tuple[str, float, int]]:
    """Menor área de acero que cumple separación máx y mínima práctica (≥ max(db, 25) + db). Devuelve (texto, As, n)."""
    mejor = None
    for dia in ("4", "5", "6", "7", "8"):
        a1, db = AREA_MM2[dia], DIAMETRO_MM[dia]
        n = max(math.ceil(As_req / a1), math.ceil(ancho_mm / sep_max) + 1)
        sep = (ancho_mm - 150.0) / (n - 1) if n > 1 else ancho_mm
        if sep < max(db, 25.0) + db:
            continue
        cand = (n * a1, f"{n}#{dia} c/{int(sep // 10 * 10)} mm", n)
        if mejor is None or cand[0] < mejor[0]:
            mejor = cand
    return None if mejor is None else (mejor[1], mejor[0], mejor[2])


def verificar(Lx_m: float, Ly_m: float, h_mm: float, c1_mm: float, c2_mm: float, cargas: CargasZapata, suelo: Suelo,
              m: Materiales, *, columna_circular: bool = False, recubrimiento_mm: float = 75.0, lam: float = 1.0) -> DisenoZapata:
    """Diseña el refuerzo mínimo que cumple y verifica todo para una geometría dada."""
    c1, c2 = _lado_equivalente(c1_mm, c2_mm, columna_circular)
    fc, fy = m.fc, m.fy
    adv: list[str] = []
    ver: list[Verif] = []
    qmax, qmin = presiones_servicio(cargas, suelo, Lx_m, Ly_m, h_mm / 1000)
    ver.append(Verif("C.15.2.2", "q máx de servicio ≤ q_adm", qmax, suelo.q_adm_kpa, "kPa", qmax <= suelo.q_adm_kpa))
    ver.append(Verif("H.4 (contacto)", "q mín ≥ 0 (sin despegue)", qmin, 0.0, "kPa", qmin >= 0.0))

    A = Lx_m * Ly_m
    p0 = cargas.P_u / A
    kx = 12 * cargas.My_u / (Lx_m**3 * Ly_m)               # kPa/m de variación lineal en x
    ky = 12 * cargas.Mx_u / (Ly_m**3 * Lx_m)
    Lx, Ly = Lx_m * 1000, Ly_m * 1000
    tiene_mom = abs(cargas.Mx_u) + abs(cargas.My_u) > 0

    # d efectivo con la capa inferior más cercana al suelo; la segunda capa se descuenta 1 diámetro (aprox. #6)
    d_x = h_mm - recubrimiento_mm - 10.0
    d_y = d_x - 19.1
    ver.append(Verif("C.15.7", "d ≥ 150 mm sobre el suelo", min(d_x, d_y), H_MIN_D_MM, "mm", min(d_x, d_y) >= H_MIN_D_MM))

    # --- flexión
    Mx_cara = _momento_cara(p0, kx, Lx_m, Ly_m, c1 / 1000)         # refuerzo paralelo a x, ancho Ly
    My_cara = _momento_cara(p0, ky, Ly_m, Lx_m, c2 / 1000)         # refuerzo paralelo a y, ancho Lx
    rmin = _rho_min(fy)
    sep_max = min(3 * h_mm, SEP_MAX_ABS_MM)
    res = {}
    for eje, M, ancho, d_ef in (("x", Mx_cara, Ly, d_x), ("y", My_cara, Lx, d_y)):
        as_req = _as_flexion(M, ancho, d_ef, fc, fy)
        as_min = rmin * ancho * h_mm
        as_nec = max(as_req, as_min)
        if math.isinf(as_nec):
            res[eje] = None
            continue
        res[eje] = _barras(as_nec, ancho, h_mm, fy, sep_max) or ("sin arreglo", math.inf, 0)
        ver.append(Verif("C.15.4.2/C.9.3.2.1", f"Flexión dir. {eje}: As provisto ≥ requerido", res[eje][1], max(as_req, as_min), "mm²",
                         res[eje][1] >= max(as_req, as_min) * 0.9999))
        ver.append(Verif("C.15.10.4/C.10.5.4", f"As mín dir. {eje}", res[eje][1], as_min, "mm²", res[eje][1] >= as_min * 0.9999))
    if res["x"] is None or res["y"] is None:
        ver.append(Verif("C.9.3.2.1", "Sección a flexión insuficiente (aumentar h)", 1.0, 0.0, "-", False))
        res = {k: v or ("-", math.inf, 0) for k, v in res.items()}
    beta = max(Lx, Ly) / min(Lx, Ly)
    if beta > 1.0 + 1e-9:
        gs = 2.0 / (beta + 1.0)
        adv.append(f"Dirección corta: {gs:.3f} del refuerzo en la franja central de ancho {min(Lx, Ly):.0f} mm (C.15.4.4.2).")

    # --- cortante como viga (sección a d de la cara)
    for eje, L_, B_, c, d_ef, k in (("x", Lx, Ly, c1, d_x, kx), ("y", Ly, Lx, c2, d_y, ky)):
        borde = (L_ - c) / 2 - d_ef
        if borde <= 0:
            ver.append(Verif("C.11.1.3.1", f"Cortante viga dir. {eje}: sección crítica fuera de la zapata", 0.0, 1.0, "kN", True))
            continue
        s = np.linspace(0.0, borde / 1000, 101)
        x_rel = (c + 2 * d_ef) / 2000 + s
        pq = max(np.maximum((p0 + k * x_rel).max(), (p0 - k * x_rel).max()), 0.0)
        Vu = float(pq * (B_ / 1000) * borde / 1000)
        Vc = PHI_CORTANTE * 0.17 * lam * math.sqrt(fc) * B_ * d_ef / 1000
        ver.append(Verif("C.11.2.1.1/C.11.1.3.1", f"Cortante como viga dir. {eje}", Vu, Vc, "kN", Vu <= Vc))

    # --- punzonamiento
    d_p = (d_x + d_y) / 2
    b1, b2 = c1 + d_p, c2 + d_p
    bo = 2 * (b1 + b2)
    q_ref = (p0 - (abs(kx) * Lx_m / 2 + abs(ky) * Ly_m / 2)) if tiene_mom else p0
    Vu_p = cargas.P_u - max(q_ref, 0.0) * (b1 / 1000) * (b2 / 1000)
    betac = max(c1, c2) / min(c1, c2)
    vc = min(0.17 * (1 + 2 / betac), 0.083 * (40 * d_p / bo + 2), 0.33) * lam * math.sqrt(fc)
    Vc_p = PHI_CORTANTE * vc * bo * d_p / 1000
    ver.append(Verif("C.11.11.2.1", "Punzonamiento", Vu_p, Vc_p, "kN", Vu_p <= Vc_p))
    if tiene_mom:
        adv.append("Con momento: punzonamiento usa la presión mínima (conservador); C.11.11.7 no está modelado.")

    # --- aplastamiento columna-zapata y dovelas
    A1 = c1 * c2
    # Conservador: sin el factor √(A2/A1) (C.10.14.1 permite hasta 2 si el soporte es más ancho; la definición de A2 no se leyó en el corpus).
    Pn_ap = PHI_APLASTAMIENTO * 0.85 * fc * A1 / 1000
    exceso = max(cargas.P_u - Pn_ap, 0.0)                    # lo que el aplastamiento no resiste lo transmiten las dovelas (C.15.8.1.2)
    as_dow = max(0.005 * c1 * c2, exceso * 1000 / (0.65 * fy))
    adv.append(f"Aplastamiento φPn = {Pn_ap:.0f} kN (sin bonificación A2/A1); exceso {exceso:.0f} kN a dovelas (C.15.8.1.2, φ 0,65 supuesto).")
    adv.append(f"Dovelas: As mínima a través de la interfaz = {as_dow:.0f} mm² (máx. de 0,005 Ag, C.15.8.2.1, y el exceso por aplastamiento).")
    ldisp = (Lx - c1) / 2 - recubrimiento_mm
    adv.append(f"Largo disponible para desarrollo en x: {ldisp:.0f} mm; ld NO verificada (C.12).")

    vol = Lx_m * Ly_m * h_mm / 1000
    long_x, long_y = Lx - 2 * 75.0, Ly - 2 * 75.0
    masa = 7850e-9 * (res["x"][1] * long_x + res["y"][1] * long_y) if math.isfinite(res["x"][1] + res["y"][1]) else math.inf
    ok = all(v.cumple for v in ver)
    return DisenoZapata(Lx, Ly, h_mm, d_x, res["x"][0], res["y"][0], res["x"][1], res["y"][1], qmax, qmin, vol, masa, tuple(ver), tuple(adv), ok)


def disenar(c1_mm: float, c2_mm: float, cargas: CargasZapata, suelo: Suelo, m: Materiales, *, columna_circular: bool = False,
            relacion_lados: float = 1.0, paso_mm: float = 50.0, h_max_mm: float = 1000.0, recubrimiento_mm: float = 75.0,
            top: int = 5) -> list[DisenoZapata]:
    """Barre lados y espesores y devuelve las `top` zapatas que cumplen, por menor volumen equivalente
    (concreto + masa de acero/7850). Sin precios: el costo con APU se puede conectar después."""
    if cargas.P_serv <= 0 or cargas.P_u <= 0:
        raise ValueError("P_serv y P_u deben ser > 0")
    if suelo.q_adm_kpa <= 0:
        raise ValueError("q_adm debe ser > 0")
    c1, c2 = _lado_equivalente(c1_mm, c2_mm, columna_circular)
    A_min = cargas.P_serv / suelo.q_adm_kpa
    Ly0 = max(math.sqrt(A_min / relacion_lados), c2 / 1000 + 0.2)
    sols: list[DisenoZapata] = []
    for Ly in np.arange(math.ceil(Ly0 * 1000 / paso_mm) * paso_mm, 6000.0 + 1, paso_mm) / 1000:
        Lx = max(round(Ly * relacion_lados * 1000 / paso_mm) * paso_mm / 1000, c1 / 1000 + 0.2)
        if Lx * Ly < A_min:
            continue
        for h in np.arange(300.0, h_max_mm + 1, paso_mm):
            r = verificar(Lx, Ly, float(h), c1_mm, c2_mm, cargas, suelo, m, columna_circular=columna_circular, recubrimiento_mm=recubrimiento_mm)
            if r.cumple:
                sols.append(r)
                break
        if len(sols) >= 40:
            break
    sols.sort(key=lambda r: r.volumen_concreto_m3 + r.masa_acero_kg / 7850.0)
    return sols[:top]


def comprobar_asentamientos(asentamiento_max_mm: float, diferencial_mm: float, luz_entre_apoyos_m: float, tipo: str = "aislada",
                            construccion: str = "porticos_concreto", giro: float = 0.0) -> list[Verif]:
    """Compara asentamientos calculados por el geotecnista con H.4.9.2, Tabla H.4.9-1 y H.4.9.4."""
    if tipo not in LIMITES_ASENT_TOTAL_MM or construccion not in LIMITES_ASENT_DIF:
        raise ValueError("tipo o construccion no reconocidos")
    lim_dif = LIMITES_ASENT_DIF[construccion] * luz_entre_apoyos_m * 1000
    return [
        Verif("H.4.9.2", "Asentamiento total a 20 años", asentamiento_max_mm, LIMITES_ASENT_TOTAL_MM[tipo], "mm", asentamiento_max_mm <= LIMITES_ASENT_TOTAL_MM[tipo]),
        Verif("H.4.9.3", "Asentamiento diferencial", diferencial_mm, lim_dif, "mm", diferencial_mm <= lim_dif),
        Verif("H.4.9.4", "Giro", giro, LIMITE_GIRO, "rad", giro <= LIMITE_GIRO),
    ]


def q_adm_desde_q_ult(q_ult_kpa: float, fs: float = FS_CARGA_MUERTA_VIVA) -> float:
    """q_adm = q_ult / FS. FS=3,0 solo para carga muerta + viva normal (Tabla H.4.7-1); otras filas no leídas."""
    if fs < FS_CARGA_MUERTA_VIVA:
        raise ValueError("FS < 3,0 no está respaldado (Tabla H.4.7-1, fila leída)")
    return q_ult_kpa / fs
