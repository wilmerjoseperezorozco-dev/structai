"""Edificio 3D con diafragmas rígidos y fuerza horizontal equivalente, con contrato uniforme (#274, F1)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D  # noqa: E402
from .sismo3d import Piso, analizar_fhe  # noqa: E402

_COND_BORDE = 1e10
_POS = dict(gt=0, allow_inf_nan=False)


class Elemento3DIn(BaseModel):
    model_config = ConfigDict(strict=True)
    i: int = Field(..., ge=0)
    j: int = Field(..., ge=0)
    E: float = Field(..., le=1e9, description="kN/m²", **_POS)
    G: float = Field(..., le=1e9, description="kN/m²", **_POS)
    A: float = Field(..., le=1e3, description="m²", **_POS)
    Iy: float = Field(..., le=1e4, description="m⁴", **_POS)
    Iz: float = Field(..., le=1e4, description="m⁴", **_POS)
    J: float = Field(..., le=1e4, description="m⁴", **_POS)
    eje_ref: Optional[tuple[float, float, float]] = None


class PisoIn(BaseModel):
    model_config = ConfigDict(strict=True)
    nombre: str = Field(..., min_length=1, max_length=40)
    nodos: list[int] = Field(..., min_length=1)
    x_cm: float = Field(..., allow_inf_nan=False)
    y_cm: float = Field(..., allow_inf_nan=False)
    altura_entrepiso_m: float = Field(..., le=50, **_POS)
    dim_x_m: float = Field(..., le=1000, **_POS)
    dim_y_m: float = Field(..., le=1000, **_POS)
    carga_vertical_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False)
    fs_x_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False, description="Fuerza sísmica del piso Fs (sin dividir por R)")
    fs_y_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False)


class SolicitudEdificio3D(BaseModel):
    model_config = ConfigDict(strict=True)
    nodos: list[tuple[float, float, float]] = Field(..., min_length=2, max_length=20000)
    elementos: list[Elemento3DIn] = Field(..., min_length=1, max_length=40000)
    apoyos: dict[int, tuple[bool, bool, bool, bool, bool, bool]]
    pisos: list[PisoIn] = Field(..., min_length=1, max_length=200, description="De abajo hacia arriba")
    sistema_deriva: Literal["general", "mamposteria_cortante"] = Field(
        ..., description="Tabla A.6.4-1: 'general' = concreto, acero, madera o mampostería que falla por flexión")
    secciones_fisuradas: bool = Field(..., description="A.6.4.1.1: si las inercias ya están fisuradas, deriva × 0,7")


def edificio_3d_fhe_contrato(s: SolicitudEdificio3D) -> ResultadoMotor:
    modelo = Portico3D([Nodo3D(*n) for n in s.nodos],
                       [Elemento3D(e.i, e.j, e.E, e.G, e.A, e.Iy, e.Iz, e.J, e.eje_ref) for e in s.elementos],
                       {k: v for k, v in s.apoyos.items()},
                       [Diafragma(p.nombre, tuple(p.nodos), p.x_cm, p.y_cm) for p in s.pisos])
    pisos = [Piso(p.nombre, p.altura_entrepiso_m, p.dim_x_m, p.dim_y_m, p.carga_vertical_kn) for p in s.pisos]
    r = analizar_fhe(modelo, pisos, [p.fs_x_kn for p in s.pisos], [p.fs_y_kn for p in s.pisos],
                     s.sistema_deriva, s.secciones_fisuradas)
    cond = modelo.numero_condicion()
    adv = []
    if r["irregularidad_torsional"] != "ninguna":
        adv.append(f"Irregularidad torsional {r['irregularidad_torsional']} (Tabla A.3-6): se amplificó la torsión "
                   "accidental con Ax (A.3.6-2) y la deriva se evaluó en los ejes de columna (A.6.3-1). "
                   "Revise si A.3.4.2 exige análisis dinámico (F2, próximamente).")
    if r["Qi_max"] > 0.10:
        adv.append("Qi > 0,10 en algún piso: los efectos P-Δ son obligatorios (A.6.2.3) y aún no se incluyen en los "
                   "desplazamientos (F3, próximamente).")
    if r["sin_limite_un_piso"]:
        adv.append("Edificación de un piso: sin límite de deriva si muros, particiones y cielorrasos la acomodan (A.6.4.1.5).")
    return ResultadoMotor(
        valor=r, unidad_si="desplazamientos y derivas en m; derivas relativas adimensionales (fracción de hpi)",
        ecuacion="K·u = F en 3D con diafragma rígido (ux, uy, rz del centro de masa); Mz = ±0,05·L⊥·Fs; "
                 "δtot = |δcm| + |r·θ|; deriva ≤ límite·hpi (×0,7 si fisuradas)",
        referencia_normativa="NSR-10 A.3.6.7, Tabla A.3-6 (1aP/1bP), A.3.6-2, A.6.2, A.6.3, A.6.4 (Tabla A.6.4-1)",
        supuestos=["Fuerzas por piso Fs de A.4.3 (sin dividir por R), calculadas por el llamador (motor-geopot).",
                   "Diafragmas rígidos en su plano, con el nodo maestro en el centro de masa del piso.",
                   "Elementos prismáticos de Euler-Bernoulli, material lineal, sin P-Δ en los desplazamientos.",
                   "Se evalúan 4 casos: Ex y Ey, cada uno con la masa corrida a ambos lados (±5 %)."],
        en_borde_dominio=bool(cond > _COND_BORDE or r["Qi_max"] > 0.10),
        advertencias=adv + ["Efectos ortogonales (A.3.6.3) y análisis dinámico (A.5): próximamente."])


# ── F2: análisis dinámico elástico espectral (A.5.4) ───────────────────────────────────────────────────────────────

def _geopot():
    """motor-geopot/src/cortante_basal.py es autónomo (solo biblioteca estándar): se carga por ruta."""
    import importlib.util
    nombre = "motor_geopot_cortante_basal"
    if nombre in sys.modules:
        return sys.modules[nombre]
    ruta = Path(__file__).resolve().parents[2] / "motor-geopot" / "src" / "cortante_basal.py"
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod          # las dataclasses del módulo necesitan estar registradas al ejecutarse
    spec.loader.exec_module(mod)
    return mod


class SitioSismico(BaseModel):
    model_config = ConfigDict(strict=True)
    aa: float = Field(..., gt=0, le=0.6, allow_inf_nan=False)
    av: float = Field(..., gt=0, le=0.6, allow_inf_nan=False)
    perfil: Literal["A", "B", "C", "D", "E"]
    grupo_uso: Literal["I", "II", "III", "IV"]
    sistema_periodo: Literal["porticos_concreto", "porticos_acero", "arriostrados_excentricos", "muros"]


class SolicitudEspectral3D(BaseModel):
    model_config = ConfigDict(strict=True)
    edificio: SolicitudEdificio3D = Field(..., description="fs_x_kn/fs_y_kn se ignoran: se recalculan con el periodo del modelo")
    sitio: SitioSismico
    otras_irregularidades: bool = Field(..., description="Irregularidades en altura o en planta distintas de la torsional (Tabla A.3-6/A.3-7)")
    torsion_accidental: bool = Field(..., description="A.3.6.7: opcional en análisis dinámico; se modela corriendo el centro de masa ±5 %")
    deriva_con_I_unitario: bool = Field(..., description="A.6.2.1.2: para grupos II-IV se permite I = 1,0 en las fuerzas de deriva")


def edificio_3d_espectral_contrato(s: SolicitudEspectral3D) -> dict[str, ResultadoMotor]:
    from .modal3d import espectral, masas_piso, modos
    gp = _geopot()
    e, st = s.edificio, s.sitio
    modelo = Portico3D([Nodo3D(*n) for n in e.nodos],
                       [Elemento3D(x.i, x.j, x.E, x.G, x.A, x.Iy, x.Iz, x.J, x.eje_ref) for x in e.elementos],
                       dict(e.apoyos), [Diafragma(p.nombre, tuple(p.nodos), p.x_cm, p.y_cm) for p in e.pisos])
    pisos = [Piso(p.nombre, p.altura_entrepiso_m, p.dim_x_m, p.dim_y_m, p.carga_vertical_kn) for p in e.pisos]
    if any(p.carga_vertical_kn <= 0 for p in pisos):
        raise ValueError("Cada piso necesita carga vertical positiva: es su masa sísmica (A.5.2.2)")
    fa, fv = gp.coef_fa(st.aa, st.perfil), gp.coef_fv(st.av, st.perfil)
    I = 1.0 if s.deriva_con_I_unitario else gp.COEF_IMPORTANCIA[st.grupo_uso]
    sa = lambda T: gp.sa_espectro(T, st.aa, st.av, fa, fv, I)  # noqa: E731
    alturas = list(__import__("itertools").accumulate(p.altura_entrepiso_m for p in pisos))
    ta = gp.periodo_aproximado(alturas[-1], st.sistema_periodo)
    cuta = gp.cu(st.av, fv) * ta
    md = modos(modelo, masas_piso(pisos))
    W = sum(p.carga_vertical_kn for p in pisos)
    T_dir, vs, fs = [], [], []
    for j in (0, 1):
        T_mod = float(md.periodos[int(md.masa_efectiva[:, j].argmax())])
        T = min(T_mod, cuta)                                       # A.4.2.1: T del análisis, sin pasar de Cu·Ta
        T_dir.append({"T_modelo_s": T_mod, "Ta_s": ta, "CuTa_s": cuta, "T_usado_s": T})
        vs.append(sa(T) * W)
        fs.append(list(gp.distribuir_fuerzas(vs[-1], tuple(p.carga_vertical_kn for p in pisos), tuple(alturas), T)))
    fhe = analizar_fhe(modelo, pisos, fs[0], fs[1], e.sistema_deriva, e.secciones_fisuradas)
    regular = fhe["irregularidad_torsional"] == "ninguna" and not s.otras_irregularidades
    din = espectral(modelo, pisos, sa, (vs[0], vs[1]), "regular" if regular else "irregular", e.sistema_deriva,
                    e.secciones_fisuradas, s.torsion_accidental)
    uso = din["uso_max_punto"] if not regular else din["uso_max_cm"]
    sup = ["Masas concentradas en el centro de masa de cada diafragma: m = W/g e inercia de planta rectangular uniforme.",
           "Espectro elástico de A.2.6 (motor-geopot), 5 % de amortiguamiento; combinación CQC.",
           "Vs con T = mín(T del modelo, Cu·Ta) en cada dirección (A.4.2)."]
    adv = []
    if not s.torsion_accidental:
        adv.append("Sin torsión accidental (A.3.6.7 lo deja a opción del diseñador en análisis dinámico).")
    if din["Qi_max"] > 0.10:
        adv.append("Qi > 0,10: los efectos P-Δ son obligatorios (A.6.2.3) y aún no se incluyen (F3, próximamente).")
    r_mod = ResultadoMotor(
        valor={"periodos_s": din["periodos_s"], "masa_participante": din["masa_participante"], "periodo_por_direccion": T_dir},
        unidad_si="s; fracción de la masa total", ecuacion="det(K* − ω²M) = 0 con K* condensada a los maestros; M̄mj = Γ²",
        referencia_normativa="NSR-10 A.5.2.1.1, A.5.4.2 (A.5.4-1, A.5.4-2), A.4.2", supuestos=sup,
        en_borde_dominio=min(din["masa_participante"].values()) < 0.95)
    r_din = ResultadoMotor(
        valor={**{k: din[k] for k in ("direcciones", "torsion_accidental", "limite_deriva", "factor_fisuradas", "Qi_max")},
               "regularidad": "regular" if regular else "irregular", "uso_max_limite": uso, "cumple_deriva": uso <= 1.0,
               "regla_deriva": "A.6.3.1.1 (centro de masa)" if regular else "A.6.3-1 (ejes de columna)"},
        unidad_si="kN; m; derivas relativas adimensionales",
        ecuacion="Vt = CQC(Sam·g·M̄mj); factor = máx(1; 0,80 o 0,90·Vs/Vt); derivas por modo combinadas con CQC",
        referencia_normativa="NSR-10 A.5.4.3, A.5.4.4, A.5.4.5 (A.5.4-4/-5), A.6.3, A.6.4 (Tabla A.6.4-1)", supuestos=sup,
        en_borde_dominio=bool(din["Qi_max"] > 0.10), advertencias=adv + ["Efectos ortogonales (A.3.6.3): próximamente."])
    return {"modal": r_mod, "espectral": r_din, "fhe_referencia": edificio_3d_fhe_contrato(
        e.model_copy(update={"pisos": [p.model_copy(update={"fs_x_kn": fx, "fs_y_kn": fy})
                                       for p, fx, fy in zip(e.pisos, fs[0], fs[1])]}))}
