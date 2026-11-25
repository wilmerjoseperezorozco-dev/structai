"""Cargas de viento NSR-10 Título B.6, Método 2 (procedimiento analítico) para edificios bajos (h ≤ 18 m), v1 (#292, #242).

Solo números y ecuaciones de la norma; el texto de la NSR-10 no se reproduce. Cotejado contra el PDF oficial
(Minvivienda/AIS, 2010), índices de página 239–300.

Alcance v1:
  - presión por velocidad qz = 0,613·Kz·Kzt·Kd·V²·I (N/m², V en m/s), ec. B.6.5-13;
  - Kz por la fórmula de la nota 2 de la Tabla B.6.5-3 con las constantes de la Tabla B.6.5-2;
  - GCpf de edificios bajos (Fig. B.6.5-7), con interpolación lineal en θ (nota 2 de la figura);
  - GCp de componentes y revestimientos de muros y cubiertas a dos aguas (Figs. B.6.5-8A a 8D),
    lineales en log10(A) entre los quiebres dibujados en la figura (1 y 10 m²; 1 y 50 m² en muros);
  - GCpi (Fig. B.6.5-2): cerrado ±0,18, parcialmente cerrado ±0,55, abierto 0;
  - levantamiento neto en la conexión cubierta-muro de una cercha simplemente apoyada (ver `levantamiento_cubierta`).

Fuera de alcance (se declara, no se verifica): Kzt topográfico (entra como dato), factor de ráfaga de estructuras
flexibles, edificios con h > 18 m (B.6.5-3/5 + G), cubiertas abovedadas o a una sola agua, parapetos, cargas torsionales,
casos con viento paralelo a la cumbrera, y la velocidad básica por municipio (el mapa Fig. B.6.4-1 no trae tabla por
municipio: V es un dato declarado).

Convención de signos (B.6.5.12.1.1): positivo hacia la superficie, negativo hacia afuera.
Errata detectada en la NSR-10: en la Fig. B.6.5-8B los GCp del alero se imprimen con signo +; son succiones (−),
como en ASCE 7-05 Fig. 6-11B y en las Figs. 8C/8D de la misma NSR-10.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Tabla B.6.5-2: α, Zg (m)
EXPOSICION = {"B": (7.0, 365.8), "C": (9.5, 274.3), "D": (11.5, 213.4)}
# Fig. B.6.5-2
GCPI = {"cerrado": 0.18, "parcialmente_cerrado": 0.55, "abierto": 0.0}
# Tabla B.6.5-4 (edificios)
KD_EDIFICIOS = 0.85
# Mapa Fig. B.6.4-1: regiones 1 a 5 (m/s); regiones especiales: 28 m/s mientras no haya datos confiables.
V_REGION = {1: 17.0, 2: 22.0, 3: 28.0, 4: 33.0, 5: 36.0}
# Tabla B.6.5-1: factor de importancia (regiones no propensas a huracanes) por grupo de uso
IMPORTANCIA = {"I": 0.87, "II": 1.00, "III": 1.15, "IV": 1.15}


def kz(z_m: float, exposicion: str, caso: int = 1) -> float:
    """Kz (Tabla B.6.5-3, nota 2): 2,01·(Z/Zg)^(2/α) para 4,0 m ≤ Z ≤ Zg; Z < 4,0 m usa Z = 4,0 m.
    En el caso 1 con exposición B, Z no se toma menor que 9,0 m (nota 2)."""
    if exposicion not in EXPOSICION:
        raise ValueError(f"exposición {exposicion!r}: use B, C o D")
    if caso not in (1, 2):
        raise ValueError("caso debe ser 1 o 2")
    if z_m <= 0:
        raise ValueError("z debe ser positiva")
    alfa, zg = EXPOSICION[exposicion]
    zmin = 9.0 if (caso == 1 and exposicion == "B") else 4.0
    z = min(max(z_m, zmin), zg)
    return 2.01 * (z / zg) ** (2.0 / alfa)


def qz(v_m_s: float, kz_: float, kzt: float = 1.0, kd: float = KD_EDIFICIOS, importancia: float = 1.0) -> float:
    """Presión por velocidad en N/m² (ec. B.6.5-13)."""
    if v_m_s <= 0 or kz_ <= 0 or kzt <= 0 or kd <= 0 or importancia <= 0:
        raise ValueError("V, Kz, Kzt, Kd e I deben ser positivos")
    return 0.613 * kz_ * kzt * kd * v_m_s ** 2 * importancia


# ---------------------------------------------------------------- Fig. B.6.5-7 (GCpf, edificios bajos)
_ZONAS_GCPF = ("1", "2", "3", "4", "5", "6", "1E", "2E", "3E", "4E")
_TABLA_GCPF = (  # (θ, valores por zona); 0–5 y 30–45 son mesetas
    (0.0, (0.40, -0.69, -0.37, -0.29, -0.45, -0.45, 0.61, -1.07, -0.53, -0.43)),
    (5.0, (0.40, -0.69, -0.37, -0.29, -0.45, -0.45, 0.61, -1.07, -0.53, -0.43)),
    (20.0, (0.53, -0.69, -0.48, -0.43, -0.45, -0.45, 0.80, -1.07, -0.69, -0.64)),
    (30.0, (0.56, 0.21, -0.43, -0.37, -0.45, -0.45, 0.69, 0.27, -0.53, -0.48)),
    (45.0, (0.56, 0.21, -0.43, -0.37, -0.45, -0.45, 0.69, 0.27, -0.53, -0.48)),
    (90.0, (0.56, 0.56, -0.37, -0.37, -0.45, -0.45, 0.69, 0.69, -0.48, -0.48)),
)


def gcpf(zona: str, theta_deg: float) -> float:
    """GCpf de la Fig. B.6.5-7 (viento perpendicular a la cumbrera), interpolado linealmente en θ."""
    if zona not in _ZONAS_GCPF:
        raise ValueError(f"zona {zona!r}: use una de {_ZONAS_GCPF}")
    if not 0.0 <= theta_deg <= 90.0:
        raise ValueError("θ debe estar entre 0° y 90°")
    k = _ZONAS_GCPF.index(zona)
    for (t0, v0), (t1, v1) in zip(_TABLA_GCPF, _TABLA_GCPF[1:]):
        if t0 <= theta_deg <= t1:
            return v0[k] + (v1[k] - v0[k]) * (theta_deg - t0) / (t1 - t0)
    raise AssertionError("θ fuera de la tabla")  # pragma: no cover


# ---------------------------------------------------------------- Figs. B.6.5-8A a 8D (GCp, componentes)
# Cada curva: puntos (A m², GCp) lineales en log10(A), constantes fuera del primer y último punto.
_CYR = {
    "muro": {  # Fig. B.6.5-8A
        "4-": ((1.0, -1.1), (50.0, -0.8)), "5-": ((1.0, -1.4), (50.0, -0.8)),
        "4+": ((1.0, 1.0), (50.0, 0.7)), "5+": ((1.0, 1.0), (50.0, 0.7)),
    },
    "8B": {  # θ ≤ 7°
        "1-": ((1.0, -1.0), (10.0, -0.9)), "2-": ((1.0, -1.8), (10.0, -1.1)), "3-": ((1.0, -2.8), (10.0, -1.1)),
        "1+": ((1.0, 0.3), (10.0, 0.2)), "2+": ((1.0, 0.3), (10.0, 0.2)), "3+": ((1.0, 0.3), (10.0, 0.2)),
        "alero2-": ((1.0, -1.7), (10.0, -1.6), (100.0, -1.1)), "alero3-": ((1.0, -2.8), (10.0, -0.8)),
    },
    "8C": {  # 7° < θ ≤ 27°
        "1-": ((1.0, -0.9), (10.0, -0.8)), "2-": ((1.0, -1.7), (10.0, -1.2)), "3-": ((1.0, -2.6), (10.0, -2.0)),
        "1+": ((1.0, 0.5), (10.0, 0.3)), "2+": ((1.0, 0.5), (10.0, 0.3)), "3+": ((1.0, 0.5), (10.0, 0.3)),
        "alero2-": ((1.0, -2.2), (10.0, -2.2)), "alero3-": ((1.0, -3.7), (10.0, -2.5)),
    },
    "8D": {  # 27° < θ ≤ 45°
        "1-": ((1.0, -1.0), (10.0, -0.8)), "2-": ((1.0, -1.2), (10.0, -1.0)), "3-": ((1.0, -1.2), (10.0, -1.0)),
        "1+": ((1.0, 0.9), (10.0, 0.8)), "2+": ((1.0, 0.9), (10.0, 0.8)), "3+": ((1.0, 0.9), (10.0, 0.8)),
        "alero2-": ((1.0, -2.0), (10.0, -1.8)), "alero3-": ((1.0, -2.0), (10.0, -1.8)),
    },
}


def _curva(puntos, area):
    if area <= puntos[0][0]:
        return puntos[0][1]
    for (a0, g0), (a1, g1) in zip(puntos, puntos[1:]):
        if area <= a1:
            return g0 + (g1 - g0) * math.log10(area / a0) / math.log10(a1 / a0)
    return puntos[-1][1]


def figura_cubierta(theta_deg: float) -> str:
    if not 0.0 <= theta_deg <= 45.0:
        raise ValueError("cubiertas a dos aguas: θ entre 0° y 45° (Figs. B.6.5-8B a 8D)")
    return "8B" if theta_deg <= 7.0 else ("8C" if theta_deg <= 27.0 else "8D")


def gcp_cubierta(zona: str, area_m2: float, theta_deg: float, signo: str = "-", alero: bool = False) -> float:
    """GCp de componentes de cubierta a dos aguas. zona '1', '2' o '3'; signo '-' (succión) o '+' (presión).
    En el alero, la Fig. da la zona 2 y la 3 (la zona 1 del alero se toma como la 2) y ya incluye las dos caras."""
    if area_m2 <= 0:
        raise ValueError("el área efectiva debe ser positiva")
    if zona not in ("1", "2", "3") or signo not in ("-", "+"):
        raise ValueError("zona 1/2/3 y signo '-' o '+'")
    fig = _CYR[figura_cubierta(theta_deg)]
    if alero:
        if signo == "+":
            raise ValueError("los aleros solo tienen GCp de succión en las Figs. 8B–8D")
        return _curva(fig["alero3-" if zona == "3" else "alero2-"], area_m2)
    return _curva(fig[zona + signo], area_m2)


def gcp_muro(zona: str, area_m2: float, signo: str = "-", theta_deg: float = 20.0) -> float:
    """GCp de muros (Fig. B.6.5-8A), zonas '4' y '5'; se reduce 10 % si θ ≤ 10° (nota 5)."""
    if area_m2 <= 0 or zona not in ("4", "5") or signo not in ("-", "+"):
        raise ValueError("zona 4/5, signo '-' o '+' y área positiva")
    g = _curva(_CYR["muro"][zona + signo], area_m2)
    return 0.9 * g if theta_deg <= 10.0 else g


def presiones_netas(q: float, gcp: float, gcpi: float) -> tuple[float, float]:
    """p = q·(GCp − (±GCpi)) en N/m². Devuelve (la más positiva, la más negativa) de las dos combinaciones."""
    a, b = q * (gcp - gcpi), q * (gcp + gcpi)
    return max(a, b), min(a, b)


# ---------------------------------------------------------------- levantamiento cubierta-muro
@dataclass(frozen=True)
class Levantamiento:
    reaccion_barlovento_n_m: float     # reacción vertical por metro de separación entre cerchas; + = hacia arriba
    reaccion_sotavento_n_m: float
    viento_barlovento_n_m: float       # solo viento (sin factorar)
    muerta_barlovento_n_m: float       # solo muerta (sin factorar, hacia abajo, positivo)


def levantamiento_cubierta(q_h: float, theta_deg: float, luz_m: float, alero_m: float, carga_muerta_pa: float, *,
                           gcpi: float = GCPI["cerrado"], borde: bool = True, factor_d: float = 0.9,
                           factor_w: float = 1.6, cp_inferior_alero: float = 0.8, g_rafaga: float = 0.85,
                           alero_sotavento_inferior: bool = False) -> Levantamiento:
    """Reacción vertical neta en los apoyos de una cercha a dos aguas simplemente apoyada en los muros, con viento
    perpendicular a la cumbrera y la envolvente de edificios bajos (Fig. B.6.5-7).

    Modelo (fijado antes de la validación):
      - luz `luz_m` entre muros, cumbrera centrada, aleros de `alero_m` a cada lado; cargas por metro de separación.
      - Solo se toman las componentes verticales de las presiones normales: p·(dx/cosθ)·cosθ = p·dx sobre la
        proyección horizontal. Las componentes horizontales no se trasladan a las reacciones verticales.
      - Cubierta a barlovento zona 2 (2E si `borde`), a sotavento zona 3 (3E); GCpi con el signo que más levanta (+).
      - Alero a barlovento: cara superior con el GCpf de la zona 2/2E y cara inferior con presión positiva
        G·Cp = g_rafaga·cp_inferior_alero (B.6.5.11.4.1); sin presión interna en el alero.
      - Alero a sotavento: cara superior con la zona 3/3E; la cara inferior se ignora salvo `alero_sotavento_inferior`
        (entonces usa la zona 4/4E del muro a sotavento).
      - Carga muerta uniforme sobre la proyección horizontal de luz + aleros.
      - Reacción factorada = factor_w·(viento) − factor_d·(muerta). Por defecto B.2.4-6 de la NSR-10 (0,9D + 1,6W).
    Devuelve reacciones con + hacia arriba (levantamiento neto si > 0).
    """
    if luz_m <= 0 or alero_m < 0 or q_h <= 0 or carga_muerta_pa < 0:
        raise ValueError("luz y q positivas; alero y carga muerta no negativos")
    e = "E" if borde else ""
    z_bar, z_sot, z_mur = gcpf("2" + e, theta_deg), gcpf("3" + e, theta_deg), gcpf("4" + e, theta_deg)
    gi = abs(gcpi)
    # tramos: (x_ini, x_fin, carga hacia arriba en N/m²) con x = 0 en el muro de barlovento
    tramos = [
        (0.0, luz_m / 2, -q_h * (z_bar - gi)),
        (luz_m / 2, luz_m, -q_h * (z_sot - gi)),
    ]
    if alero_m > 0:
        tramos.append((-alero_m, 0.0, -q_h * z_bar + q_h * g_rafaga * cp_inferior_alero))
        # cara inferior a sotavento: la succión del muro (z_mur < 0) tira hacia abajo, es decir, + q·z_mur hacia arriba
        inferior = q_h * z_mur if alero_sotavento_inferior else 0.0
        tramos.append((luz_m, luz_m + alero_m, -q_h * z_sot + inferior))

    def reaccion_barlovento(t):
        return sum(w * (x1 - x0) * (luz_m - (x0 + x1) / 2) / luz_m for x0, x1, w in t)

    def total(t):
        return sum(w * (x1 - x0) for x0, x1, w in t)

    rw_b = reaccion_barlovento(tramos)
    rw_s = total(tramos) - rw_b
    muerta = [(-alero_m, luz_m + alero_m, carga_muerta_pa)]
    rd_b = reaccion_barlovento(muerta)
    rd_s = total(muerta) - rd_b
    return Levantamiento(factor_w * rw_b - factor_d * rd_b, factor_w * rw_s - factor_d * rd_s, rw_b, rd_b)


# ---------------------------------------------------------------- edificios de cualquier altura (#242)
# Tabla B.6.5-2, constantes para el factor de ráfaga: (b̄, ᾱ, c, ℓ [m], ε̄, z_min [m])
RAFAGA = {"B": (0.45, 1 / 4.0, 0.30, 97.5, 1 / 3.0, 9.0),
          "C": (0.65, 1 / 6.5, 0.20, 152.4, 1 / 5.0, 4.5),
          "D": (0.80, 1 / 9.0, 0.15, 198.1, 1 / 8.0, 2.0)}
G_Q = G_V = 3.4


def cp_muros(L_sobre_B: float) -> tuple[float, float, float]:
    """(barlovento, sotavento, laterales) de la Fig. B.6.5-3; sotavento interpolado en L/B (0–1: −0,5; 2: −0,3; ≥4: −0,2).
    L = dimensión paralela al viento, B = perpendicular."""
    if L_sobre_B <= 0:
        raise ValueError("L/B positiva")
    r = L_sobre_B
    sot = -0.5 if r <= 1 else (-0.5 + 0.2 * (r - 1) if r <= 2 else (-0.3 + 0.05 * (r - 2) if r <= 4 else -0.2))
    return 0.8, sot, -0.7


def _iz_lz(h: float, exposicion: str) -> tuple[float, float, float]:
    _b, _a, c, ell, eps, zmin = RAFAGA[exposicion]
    z = max(0.6 * h, zmin)
    return z, c * (10.0 / z) ** (1 / 6), ell * (z / 10.0) ** eps


def factor_rafaga(h: float, B: float, L: float, exposicion: str, v_m_s: float, n1_hz: float | None = None,
                  amortiguamiento: float = 0.02) -> dict:
    """Factor de efecto ráfaga (B.6.5.8). Rígido (n1 ≥ 1 Hz o sin n1): G de B.6.5-2. Flexible (n1 < 1 Hz): Gf de
    B.6.5-6 con R de B.6.5-8 a B.6.5-11. B y L como en B.6.3 (B perpendicular al viento). Devuelve el detalle."""
    if min(h, B, L, v_m_s) <= 0 or exposicion not in RAFAGA:
        raise ValueError("h, B, L y V positivos; exposición B, C o D")
    z, iz, lz = _iz_lz(h, exposicion)
    q = math.sqrt(1.0 / (1.0 + 0.63 * ((B + h) / lz) ** 0.63))
    out = {"z_m": z, "Iz": iz, "Lz_m": lz, "Q": q}
    g_rig = 0.925 * (1 + 1.7 * G_Q * iz * q) / (1 + 1.7 * G_V * iz)
    if n1_hz is None or n1_hz >= 1.0:
        return out | {"tipo": "rígida", "G": g_rig}
    if not 0 < amortiguamiento < 1:
        raise ValueError("amortiguamiento como fracción del crítico (p. ej. 0,02)")
    bbar, abar = RAFAGA[exposicion][0], RAFAGA[exposicion][1]
    vz = bbar * (z / 10.0) ** abar * v_m_s
    n1 = n1_hz
    N1 = n1 * lz / vz
    rn = 7.47 * N1 / (1 + 10.3 * N1) ** (5 / 3)

    def r_l(eta):
        return 1.0 if eta <= 0 else 1 / eta - (1 - math.exp(-2 * eta)) / (2 * eta * eta)

    rh, rb, rl = r_l(4.6 * n1 * h / vz), r_l(4.6 * n1 * B / vz), r_l(15.4 * n1 * L / vz)
    r = math.sqrt(rn * rh * rb * (0.53 + 0.47 * rl) / amortiguamiento)
    lg = math.log(3600 * n1)
    g_r = math.sqrt(2 * lg) + 0.577 / math.sqrt(2 * lg)
    gf = 0.925 * (1 + 1.7 * iz * math.sqrt(G_Q ** 2 * q ** 2 + g_r ** 2 * r ** 2)) / (1 + 1.7 * G_V * iz)
    return out | {"tipo": "flexible", "G": gf, "G_rigida": g_rig, "Vz_m_s": vz, "N1": n1 * lz / vz, "Rn": rn,
                  "Rh": rh, "RB": rb, "RL": rl, "R": r, "gR": g_r}


def fuerzas_por_nivel(v_m_s: float, exposicion: str, alturas_piso_m, B: float, L: float, *, kzt: float = 1.0,
                      importancia: float = 1.0, n1_hz: float | None = None, amortiguamiento: float = 0.02) -> dict:
    """Fuerza lateral del SPRFV por nivel (kN) con B.6.5-15, edificio cerrado (GCpi se cancela en la resultante):
    barlovento qz·G·0,8 integrado en la altura aferente del nivel (Kz caso 2) + sotavento qh·G·|Cp|. Sin casos
    torsionales ni de carga parcial (Fig. B.6.5-6)."""
    alts = list(alturas_piso_m)
    n = len(alts)
    h = float(sum(alts))
    g = factor_rafaga(h, B, L, exposicion, v_m_s, n1_hz, amortiguamiento)
    cw, cl, _ = cp_muros(L / B)
    qh = qz(v_m_s, kz(h, exposicion, caso=2), kzt, KD_EDIFICIOS, importancia) / 1000.0
    cotas = [0.0] + [sum(alts[:i + 1]) for i in range(n)]
    fuerzas = []
    for nv in range(1, n + 1):
        z0 = (cotas[nv - 1] + cotas[nv]) / 2
        z1 = (cotas[nv] + cotas[nv + 1]) / 2 if nv < n else cotas[nv]
        zs = [z0 + (z1 - z0) * (k + 0.5) / 20 for k in range(20)]
        barl = sum(qz(v_m_s, kz(z, exposicion, caso=2), kzt, KD_EDIFICIOS, importancia) / 1000.0 for z in zs) / 20
        fuerzas.append((barl * g["G"] * cw - qh * g["G"] * cl) * B * (z1 - z0))
    return {"fuerzas_kn": fuerzas, "cortante_basal_kn": sum(fuerzas), "qh_kpa": qh, "G": g["G"], "rafaga": g,
            "Cp": (cw, cl)}
