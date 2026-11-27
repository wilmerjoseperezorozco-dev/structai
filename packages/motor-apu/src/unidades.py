"""
Unidades y regla de tres trazable para presupuestos (#207).

Tres capas:
  1. normalizar(texto, seccion, descripcion): la escritura de la fuente ("Mts", "UND", "Gl"...) → unidad canónica.
     Reglas de práctica colombiana (Wilmer, 2026-11-12): "m", "mt", "metro" = metro lineal (ml); "gl" = GLOBAL
     (1 actividad completa) en transporte, mano de obra y equipo, y GALÓN en materiales líquidos o pastas. Lo que no
     se puede decidir se marca como ambiguo: nunca se adivina.
  2. convertir(valor, de, a, **datos):
     A. misma dimensión → factor exacto con fuente (SI/NIST);
     B. cambio de dimensión → SOLO con su dato puente (espesor, ancho, densidad, diámetro, jornada...). Si falta,
        se lanza FaltaDato diciendo qué dato hace falta.
  3. regla_de_tres(a, b, c): X = b·c/a con la fórmula visible y advertencias cuando la relación no es proporcional.

Decisión (Wilmer, 2026-11-12): StructAI responde SIEMPRE en una unidad fija por ítem (taxonomía). Otras unidades
solo entran como dato de la fuente y se convierten a la fija con su geometría, diciéndolo en una línea.
"""
from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field

from .cantidades import peso_barra_kg_m

# ── Unidades canónicas: símbolo de presentación y dimensión ──────────────────────────────────────────────
#    Dimensiones: L longitud, A área, V volumen, M masa, F fuerza, P presión, Q caudal, W potencia,
#    a aceleración, T tiempo, U conteo, G global (1 actividad), % porcentaje de otro costo.
CANONICAS: dict[str, tuple[str, str]] = {
    "mm": ("mm", "L"), "cm": ("cm", "L"), "ml": ("ml", "L"), "km": ("km", "L"), "pulg": ("pulg", "L"), "pie": ("pie", "L"),
    "cm2": ("cm²", "A"), "m2": ("m²", "A"), "ha": ("ha", "A"), "pie2": ("pie²", "A"),
    "cm3": ("cm³", "V"), "L": ("L", "V"), "m3": ("m³", "V"), "gal": ("gal", "V"),
    "g": ("g", "M"), "kg": ("kg", "M"), "t": ("t", "M"), "lb": ("lb", "M"),
    "N": ("N", "F"), "kN": ("kN", "F"), "kgf": ("kgf", "F"), "tf": ("tf", "F"), "lbf": ("lbf", "F"),
    "Pa": ("Pa", "P"), "kPa": ("kPa", "P"), "MPa": ("MPa", "P"), "kgf/cm2": ("kgf/cm²", "P"), "psi": ("psi", "P"),
    "bar": ("bar", "P"), "mca": ("m.c.a.", "P"),
    "m3/s": ("m³/s", "Q"), "L/s": ("L/s", "Q"), "m3/h": ("m³/h", "Q"), "gpm": ("gpm", "Q"),
    "W": ("W", "W"), "kW": ("kW", "W"), "HP": ("HP", "W"), "CV": ("CV", "W"),
    "m/s2": ("m/s²", "a"), "gn": ("g", "a"),
    "min": ("min", "T"), "h": ("h", "T"),
    "dia": ("día", "Tj"), "mes": ("mes", "Tm"), "jornal": ("jornal", "Tj"),
    "un": ("un", "U"), "par": ("par", "U"), "gl": ("gl", "G"), "%": ("%", "%"),
    # Transporte compuesto (INVIAS): cantidad × distancia de acarreo. Solo se convierte con la distancia.
    "m3-km": ("m³-km", "V·km"), "m2-km": ("m²-km", "A·km"), "ml-km": ("ml-km", "L·km"), "t-km": ("t-km", "M·km"),
    "kg-km": ("kg-km", "M·km"), "L-km": ("L-km", "V·km"),
}
_BASE_COMPUESTA = {"m3-km": "m3", "m2-km": "m2", "ml-km": "ml", "t-km": "t", "kg-km": "kg", "L-km": "L"}

# Factor a la unidad base de su dimensión. Fuentes: SI (BIPM) y NIST SP 811 (anexo B). Exactos por definición salvo
# donde se indica.
FACTOR_BASE: dict[str, float] = {
    # longitud → m
    "mm": 1e-3, "cm": 1e-2, "ml": 1.0, "km": 1e3, "pulg": 0.0254, "pie": 0.3048,
    # área → m²
    "cm2": 1e-4, "m2": 1.0, "ha": 1e4, "pie2": 0.09290304,
    # volumen → m³ (galón US = 231 pulg³ = 3,785411784 L, exacto)
    "cm3": 1e-6, "L": 1e-3, "m3": 1.0, "gal": 3.785411784e-3,
    # masa → kg (libra avoirdupois = 0,45359237 kg, exacto)
    "g": 1e-3, "kg": 1.0, "t": 1e3, "lb": 0.45359237,
    # fuerza → N (gravedad estándar gn = 9,80665 m/s², exacta por convención)
    "N": 1.0, "kN": 1e3, "kgf": 9.80665, "tf": 9806.65, "lbf": 4.4482216152605,
    # presión → Pa (psi = lbf/pulg²; m.c.a. con agua a 4 °C, ρ = 1000 kg/m³ y gn)
    "Pa": 1.0, "kPa": 1e3, "MPa": 1e6, "kgf/cm2": 98066.5, "psi": 6894.757293168, "bar": 1e5, "mca": 9806.65,
    # caudal → m³/s
    "m3/s": 1.0, "L/s": 1e-3, "m3/h": 1 / 3600, "gpm": 3.785411784e-3 / 60,
    # potencia → W (HP mecánico = 550 ft·lbf/s; CV métrico = 75 kgf·m/s)
    "W": 1.0, "kW": 1e3, "HP": 745.69987158227, "CV": 735.49875,
    # aceleración → m/s²
    "m/s2": 1.0, "gn": 9.80665,
    # tiempo de reloj → h
    "min": 1 / 60, "h": 1.0,
    # conteo
    "un": 1.0, "par": 2.0,
}

# Equivalencias de USO (no conversiones exactas): resistencia del concreto. 3000 psi = 20,68 MPa exactos, pero en
# Colombia se dice "21 MPa (3000 psi)". Se devuelven marcadas como nominales.
EQUIVALENCIA_NOMINAL_FC = {17.5: 2500, 21.0: 3000, 24.5: 3500, 28.0: 4000, 31.5: 4500, 35.0: 5000, 42.0: 6000}

# ── Capa 1: normalización ────────────────────────────────────────────────────────────────────────────────
_ALIAS = {
    # metro lineal (regla de práctica: "m", "mt", "metro" = ml)
    "m": "ml", "ml": "ml", "mt": "ml", "mts": "ml", "metro": "ml", "metros": "ml", "metro lineal": "ml",
    "metros lineales": "ml", "m l": "ml", "m.l.": "ml", "ms": "ml",
    "mm": "mm", "cm": "cm", "km": "km", "kms": "km", "pulg": "pulg", "pulgada": "pulg", '"': "pulg", "pie": "pie",
    "m2": "m2", "m^2": "m2", "m²": "m2", "mts2": "m2", "mt2": "m2", "metro cuadrado": "m2", "metros cuadrados": "m2",
    "ha": "ha", "hectarea": "ha", "cm2": "cm2",
    "m3": "m3", "m^3": "m3", "m³": "m3", "mts3": "m3", "mt3": "m3", "metro cubico": "m3", "metros cubicos": "m3",
    "l": "L", "lt": "L", "lts": "L", "litro": "L", "litros": "L", "cm3": "cm3",
    "gal": "gal", "galon": "gal", "galones": "gal",
    "kg": "kg", "kgs": "kg", "kilo": "kg", "kilogramo": "kg", "g": "g", "gr": "g", "gramo": "g",
    "t": "t", "tn": "t", "ton": "t", "tonelada": "t", "lb": "lb", "libra": "lb",
    "h": "h", "hr": "h", "hrs": "h", "hora": "h", "horas": "h", "min": "min",
    "dia": "dia", "dias": "dia", "jornal": "jornal", "mes": "mes",
    "un": "un", "und": "un", "ud": "un", "u": "un", "u n": "un", "unidad": "un", "unidades": "un", "uni": "un",
    "par": "par", "global": "gl", "glb": "gl", "%": "%",
    "h/h": "h", "hh": "h", "hora hombre": "h", "unid": "un", "unds": "un",
    "m3-km": "m3-km", "m3 km": "m3-km", "m3km": "m3-km", "m2-km": "m2-km", "ml-km": "ml-km", "t-km": "t-km",
    "ton-km": "t-km", "kg-km": "kg-km", "l-km": "L-km", "l- km": "L-km",
}
# Presentaciones comerciales: no son unidades de medida; requieren su contenido (dato puente) para convertir.
PRESENTACIONES = {"bulto", "bultos", "cunete", "cte", "caja", "rollo", "rl", "pliego", "lamina", "carton", "juego",
                  "viaje", "placa", "caneca"}
_LIQUIDOS = re.compile(r"pintura|thinner|tiner|vinilo|esmalte|laca|barniz|sellador|imprima|anticorrosiv|antioxidante|"
                       r"impermeabilizante|aceite|acpm|gasolina|combustible|disolvente|varsol|pegante|aditivo|"
                       r"acronal|epox|curador|desmoldante|estuco|masilla|inmunizante|liquido|pegacor|silicona")
_ACTIVIDAD = re.compile(r"transporte|acarreo|movilizaci|desmonte|descapote|limpieza|aseo|poda|tala|senaliz|campamento|"
                        r"herramienta|equipo|mano de obra|retiro|cerramiento|valla|provisional|prueba|ensayo|tramite|"
                        r"permiso|reembolso|acometida|punto|conexion|tablero|instalacion")


def _n(s: str | None) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", s.replace("²", "2").replace("³", "3")).strip(" .")


@dataclass
class Normalizada:
    unidad: str | None             # clave canónica (p. ej. "m2") o None si ambigua o desconocida
    texto_original: str
    razon: str
    ambigua: bool = False
    presentacion: str | None = None   # "bulto", "cunete"... si la fuente usa una presentación comercial

    @property
    def simbolo(self) -> str | None:
        return CANONICAS[self.unidad][0] if self.unidad else None


def normalizar(texto: str | None, seccion: str | None = None, descripcion: str | None = None) -> Normalizada:
    """Escritura de la fuente → unidad canónica. `seccion`: materiales, mano_obra, equipo o transporte (si se conoce)."""
    t = _n(texto)
    if not t:
        return Normalizada(None, texto or "", "unidad vacía", ambigua=True)
    if t in ("gl", "g l"):
        d = _n(descripcion)
        if seccion in ("transporte", "mano_obra", "equipo"):
            return Normalizada("gl", texto, f"'gl' en {seccion} = global (1 actividad)")
        if d and _ACTIVIDAD.search(d) and not _LIQUIDOS.search(d):
            return Normalizada("gl", texto, "'gl' con descripción de actividad = global")
        if d and _LIQUIDOS.search(d):
            return Normalizada("gal", texto, "'gl' con líquido o pasta = galón")
        if seccion == "materiales":
            return Normalizada("gal", texto, "'gl' en materiales = galón (presentación) por defecto")
        return Normalizada(None, texto, "'gl' sin contexto: ¿global o galón?", ambigua=True)
    if t in _ALIAS:
        return Normalizada(_ALIAS[t], texto, "alias conocido")
    if t in PRESENTACIONES:
        return Normalizada(None, texto, "presentación comercial: requiere su contenido para convertir",
                           presentacion=t)
    return Normalizada(None, texto, "escritura no reconocida", ambigua=True)


# ── Capa 2: conversión ───────────────────────────────────────────────────────────────────────────────────
class FaltaDato(ValueError):
    """La conversión cambia de dimensión y le falta su dato puente. `dato` dice cuál."""

    def __init__(self, dato: str, explicacion: str):
        self.dato = dato
        super().__init__(f"Falta el dato '{dato}': {explicacion}")


@dataclass
class Resultado:
    valor: float
    unidad: str
    formula: str
    datos: dict = field(default_factory=dict)
    exacta: bool = True
    advertencias: list[str] = field(default_factory=list)

    @property
    def texto(self) -> str:
        return f"{formatear(self.valor)} {CANONICAS[self.unidad][0]}"


def dimension(u: str) -> str:
    if u not in CANONICAS:
        raise ValueError(f"Unidad '{u}' no canónica; usar normalizar() primero")
    return CANONICAS[u][1]


def _misma(valor: float, de: str, a: str) -> Resultado:
    f = FACTOR_BASE[de] / FACTOR_BASE[a]
    return Resultado(valor * f, a, f"{formatear(valor)} {CANONICAS[de][0]} × {f:.10g} = {formatear(valor * f)} {CANONICAS[a][0]}")


def convertir(valor: float, de: str, a: str, **datos) -> Resultado:
    """Convierte `valor` de la unidad `de` a la unidad `a` (claves canónicas).

    Datos puente aceptados (en unidades SI salvo que se indique):
      espesor_m (m³↔m²), ancho_m (m²↔ml), densidad_t_m3 (m³↔t), diametro_barra (ml↔kg de acero, p. ej. "4"),
      contenido_L (gal real del envase), jornada_h (h↔día/jornal), piezas_por_m2 (m²→un), longitud_pieza_m (ml→un),
      factor_expansion (m³ banco→m³ suelto, con estado="banco_a_suelto").
    """
    if de == a:
        return Resultado(valor, a, "misma unidad")
    dde, da = dimension(de), dimension(a)
    # galón con contenido real declarado por el envase
    if "gal" in (de, a) and "contenido_L" in datos and dde == da == "V":
        litros = float(datos["contenido_L"])
        fac = litros * 1e-3
        if de == "gal":
            r = convertir(valor * fac, "m3", a)
        else:
            r = convertir(valor, de, "m3")
            r = Resultado(r.valor / fac, "gal", r.formula, exacta=True)
        r.formula = f"galón del envase = {formatear(litros)} L (dato declarado); " + r.formula
        r.datos["contenido_L"] = litros
        return r
    if dde == da and dde in "LAVMFPQWaTU" and de in FACTOR_BASE and a in FACTOR_BASE:
        return _misma(valor, de, a)
    # transporte compuesto ↔ su base, con la distancia de acarreo
    if dde.endswith("·km") or da.endswith("·km"):
        comp, otra = (de, a) if dde.endswith("·km") else (a, de)
        base = _BASE_COMPUESTA[comp]
        if dimension(otra) != dimension(base):
            raise FaltaDato("regla", f"{CANONICAS[comp][0]} solo se relaciona con {CANONICAS[base][0]} y su dimensión")
        if "distancia_km" not in datos or datos["distancia_km"] in (None, ""):
            raise FaltaDato("distancia_km", f"de {CANONICAS[comp][0]} a {CANONICAS[base][0]} hace falta la distancia de acarreo")
        dist = float(datos["distancia_km"])
        if dde.endswith("·km"):       # 50 m³-km con 10 km = 5 m³ transportados
            r = convertir(valor / dist, base, a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} ÷ {formatear(dist)} km = {r.texto}"
        else:
            r = Resultado(convertir(valor, de, base).valor * dist, a, "")
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} × {formatear(dist)} km = {r.texto}"
        r.datos["distancia_km"] = dist
        return r
    if "G" in (dde, da) or "%" in (dde, da):
        raise ValueError("'gl' (global) y '%' no se convierten: global es 1 actividad completa y % es una regla "
                         "sobre otro costo. Solo se prorratean con una base explícita.")

    def req(nombre, expl):
        if nombre not in datos or datos[nombre] in (None, ""):
            raise FaltaDato(nombre, expl)
        return datos[nombre]

    # volumen ↔ área con el espesor
    if {dde, da} == {"V", "A"}:
        e = float(req("espesor_m", "de volumen a área (o al revés) hace falta el espesor"))
        v_m3 = convertir(valor, de, "m3").valor if dde == "V" else None
        if dde == "V":
            r = convertir(v_m3 / e, "m2", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} ÷ espesor {formatear(e)} m = {r.texto}"
        else:
            a_m2 = convertir(valor, de, "m2").valor
            r = convertir(a_m2 * e, "m3", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} × espesor {formatear(e)} m = {r.texto}"
        r.datos["espesor_m"] = e
        return r
    # área ↔ longitud con el ancho (o alto)
    if {dde, da} == {"A", "L"}:
        w = float(req("ancho_m", "de área a metro lineal (o al revés) hace falta el ancho o alto del elemento"))
        if dde == "A":
            r = convertir(convertir(valor, de, "m2").valor / w, "ml", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} ÷ ancho {formatear(w)} m = {r.texto}"
        else:
            r = convertir(convertir(valor, de, "ml").valor * w, "m2", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} × ancho {formatear(w)} m = {r.texto}"
        r.datos["ancho_m"] = w
        return r
    # volumen ↔ masa con la densidad
    if {dde, da} == {"V", "M"}:
        rho = float(req("densidad_t_m3", "de volumen a masa hace falta la densidad del material (t/m³)"))
        if dde == "V":
            r = convertir(convertir(valor, de, "m3").valor * rho, "t", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} × densidad {formatear(rho)} t/m³ = {r.texto}"
        else:
            r = convertir(convertir(valor, de, "t").valor / rho, "m3", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} ÷ densidad {formatear(rho)} t/m³ = {r.texto}"
        r.datos["densidad_t_m3"] = rho
        return r
    # longitud de barra ↔ masa de acero con el diámetro
    if {dde, da} == {"L", "M"}:
        d = str(req("diametro_barra", "de metros de barra a kilos hace falta el diámetro (p. ej. '4' = 1/2\")"))
        w = peso_barra_kg_m(d)
        if dde == "L":
            r = convertir(convertir(valor, de, "ml").valor * w, "kg", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} × {formatear(w)} kg/m (barra #{d}) = {r.texto}"
        else:
            r = convertir(convertir(valor, de, "kg").valor / w, "ml", a)
            r.formula = f"{formatear(valor)} {CANONICAS[de][0]} ÷ {formatear(w)} kg/m (barra #{d}) = {r.texto}"
        r.datos["diametro_barra"] = d
        r.advertencias.append("peso nominal por geometría (NTC 2289); no incluye traslapos ni desperdicio")
        return r
    # tiempo de reloj ↔ días de jornada
    if {dde, da} <= {"T", "Tj"} and dde != da:
        j = float(req("jornada_h", "de horas a días o jornales hace falta la jornada vigente (horas por día), "
                                   "que cambió por ley entre 2023 y 2026"))
        if dde == "T":
            r = Resultado(convertir(valor, de, "h").valor / j, a, f"{formatear(valor)} h ÷ {formatear(j)} h/día")
        else:
            r = Resultado(convertir(valor * j, "h", a).valor, a, f"{formatear(valor)} día × {formatear(j)} h/día")
        r.datos["jornada_h"] = j
        return r
    # área o longitud → piezas (con redondeo hacia arriba: unidades indivisibles)
    if da == "U" and dde in ("A", "L"):
        if dde == "A":
            ppm = float(req("piezas_por_m2", "de m² a piezas hacen falta las piezas por m² del formato"))
            exacto = convertir(valor, de, "m2").valor * ppm
            formula = f"{formatear(valor)} m² × {formatear(ppm)} piezas/m²"
        else:
            lp = float(req("longitud_pieza_m", "de metros a piezas hace falta la longitud de cada pieza (tubo de 6 m)"))
            exacto = convertir(valor, de, "ml").valor / lp
            formula = f"{formatear(valor)} ml ÷ {formatear(lp)} m/pieza"
        n = math.ceil(exacto - 1e-9)
        return Resultado(n, "un", f"{formula} = {formatear(exacto)} → {n} (se redondea hacia arriba)",
                         datos=dict(datos), exacta=False,
                         advertencias=["unidades indivisibles: se compran piezas enteras"])
    raise FaltaDato("regla", f"no hay regla para convertir {CANONICAS[de][0]} ({dde}) a {CANONICAS[a][0]} ({da})")


def expansion_suelo(volumen_banco_m3: float, factor_expansion: float) -> Resultado:
    """m³ en banco → m³ suelto (el material excavado ocupa más). El factor depende del suelo: es un dato con fuente."""
    v = volumen_banco_m3 * factor_expansion
    return Resultado(v, "m3", f"{formatear(volumen_banco_m3)} m³ en banco × factor {formatear(factor_expansion)} = "
                              f"{formatear(v)} m³ sueltos", datos={"factor_expansion": factor_expansion},
                     exacta=False, advertencias=["el factor de expansión depende del tipo de suelo"])


def convertir_precio(precio: float, de: str, a: str, **datos) -> Resultado:
    """Precio por unidad `de` → precio por unidad `a`. Si 1 `de` = k `a`, entonces precio/`a` = precio/`de` ÷ k.
    No admite conversiones con redondeo (piezas enteras): el precio unitario no se redondea."""
    k = convertir(1.0, de, a, **datos)
    if not k.exacta:
        raise ValueError("conversión con redondeo (piezas enteras): no aplica a precios unitarios")
    p = precio / k.valor
    return Resultado(p, a, f"$ {formatear(precio)} / {CANONICAS[de][0]} ÷ ({k.formula.split(' = ')[-1]} por "
                           f"{CANONICAS[de][0]}) = $ {formatear(p)} / {CANONICAS[a][0]}",
                     datos=k.datos, advertencias=k.advertencias)


def equivalencia_fc(mpa: float) -> dict:
    """Resistencia del concreto: conversión exacta MPa→psi y la equivalencia NOMINAL de uso si existe."""
    exacto = mpa * 1e6 / FACTOR_BASE["psi"]
    return {"mpa": mpa, "psi_exacto": round(exacto, 1), "psi_nominal": EQUIVALENCIA_NOMINAL_FC.get(mpa),
            "nota": "la nominal es de uso (p. ej. 21 MPa ≈ 3000 psi); la exacta es la conversión de unidades"}


# ── Capa 3: regla de tres ────────────────────────────────────────────────────────────────────────────────
def regla_de_tres(a: float, b: float, c: float, *, costo_fijo: float | None = None, indivisible: bool = False,
                  anios_distintos: bool = False, no_lineal: bool = False, unidad_x: str = "") -> Resultado:
    """Si `a` → `b`, entonces `c` → X = b·c/a. Advierte cuando la proporcionalidad no se cumple."""
    if a == 0:
        raise ZeroDivisionError("a no puede ser 0")
    adv = []
    x = b * c / a
    formula = f"X = {formatear(b)} × {formatear(c)} ÷ {formatear(a)} = {formatear(x)} {unidad_x}".strip()
    if costo_fijo:
        variable = (b - costo_fijo) * c / a + costo_fijo
        adv.append(f"hay un costo fijo de {formatear(costo_fijo)}: no escala con la cantidad; X corregido = "
                   f"{formatear(variable)}")
        x = variable
    if indivisible:
        adv.append("unidades indivisibles (bultos, tubos): redondear hacia arriba al comprar")
    if anios_distintos:
        adv.append("precios de años distintos: indexar (ICOCED, IPC o salario mínimo), no aplicar regla de tres")
    if no_lineal:
        adv.append("relación no lineal (p. ej. peso de barra ∝ d², pendiente ∝ tan θ): la regla de tres no aplica")
    return Resultado(x, "un", formula, exacta=not (adv and (no_lineal or anios_distintos)), advertencias=adv)


# ── Presentación ─────────────────────────────────────────────────────────────────────────────────────────
def formatear(x: float, decimales: int | None = None) -> str:
    """Formato colombiano: punto de miles y coma decimal (12.500,5). Hasta 4 decimales significativos."""
    if decimales is None:
        decimales = 0 if abs(x) >= 1000 or float(x).is_integer() else (2 if abs(x) >= 1 else 4)
    s = f"{x:,.{decimales}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def formatear_precio(precio: float, unidad: str) -> str:
    return f"$ {formatear(round(precio))} / {CANONICAS[unidad][0]}"
