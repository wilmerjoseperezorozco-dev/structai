"""
MÓDULO: Materiales viales — verificación de cumplimiento NTC (parte 1)
Normas:
  - NTC 2017  — Adoquines de concreto para pavimentos (INVIAS Art. 510)
  - NTC 4342  — Geotextiles: retención asfáltica en pavimentos asfálticos (INVIAS D6140)
  - NTC 121   — Especificación de desempeño para cemento hidráulico
  - NTC 1299  — Concreto. Aditivos químicos para concreto (IDT ASTM C494)
  - NTC 1362  — Cemento hidráulico blanco (incluida en NSR-10)
  - NTC 3459  — Concretos. Agua para la elaboración de concreto
  - NTC 3493  — Cenizas volantes y puzolanas naturales como aditivos minerales (equiv. ASTM C618)

Cada dataclase de muestra expone un método verificar_ntcXXX() que retorna un dict
de conformidad (cumple/no cumple + detalle de requisitos), siguiendo el patrón de
AgregadoGrueso.verificar_ntc174() en motor-geopot/src/lab_agregados.py.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# NTC 2017 — Adoquines de concreto para pavimentos
# ============================================================================

class AplicacionAdoquin(Enum):
    PEATONAL = "peatonal"
    VEHICULAR_LIVIANO = "vehicular_liviano"
    VEHICULAR_PESADO = "vehicular_pesado"
    PORTUARIO = "portuario"
    INDUSTRIAL = "industrial"


class TipoAdoquin(Enum):
    NO_BISELADO = "no_biselado"
    CON_BISEL = "con_bisel"
    PRISMATICO = "prismatico"


ESPESOR_MINIMO_ADOQUIN_MM = {
    AplicacionAdoquin.PEATONAL: 60,
    AplicacionAdoquin.VEHICULAR_LIVIANO: 80,
    AplicacionAdoquin.VEHICULAR_PESADO: 100,
    AplicacionAdoquin.INDUSTRIAL: 100,
    AplicacionAdoquin.PORTUARIO: 100,  # requiere además BS EN 1338
}

REQUISITOS_ADOQUIN_NTC2017 = {
    "resistencia_flexion_promedio_min_mpa": 5.0,
    "resistencia_flexion_individual_min_mpa": 4.2,
    "absorcion_max_pct": 7.0,
    "absorcion_max_alta_especificacion_pct": 5.0,  # portuario / alta especificación
    "tolerancia_largo_ancho_mm": 2.0,
    "tolerancia_espesor_mm": 3.0,
}


@dataclass
class Adoquin:
    """Adoquín de concreto para pavimentos — NTC 2017 (tercera actualización, 2018)."""
    nombre: str
    aplicacion: AplicacionAdoquin
    tipo: TipoAdoquin
    largo_mm: float
    ancho_mm: float
    espesor_mm: float
    resistencia_flexion_mpa: float
    absorcion_porcentaje: float
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 2017"

    def verificar_ntc2017(self) -> dict:
        """Verifica cumplimiento de espesor, flexotracción, absorción y tolerancias."""
        req = REQUISITOS_ADOQUIN_NTC2017
        fallas = []

        espesor_min = ESPESOR_MINIMO_ADOQUIN_MM.get(self.aplicacion)
        if espesor_min is None:
            fallas.append(f"Aplicación '{self.aplicacion.value}' no reconocida en NTC 2017")
        elif self.espesor_mm < espesor_min:
            fallas.append(f"Espesor {self.espesor_mm} mm < mínimo {espesor_min} mm para {self.aplicacion.value}")

        if self.resistencia_flexion_mpa < req["resistencia_flexion_promedio_min_mpa"]:
            fallas.append(
                f"Resistencia a flexotracción {self.resistencia_flexion_mpa} MPa < "
                f"{req['resistencia_flexion_promedio_min_mpa']} MPa (promedio mínimo)"
            )
        if self.resistencia_flexion_mpa < req["resistencia_flexion_individual_min_mpa"]:
            fallas.append(
                f"Resistencia individual {self.resistencia_flexion_mpa} MPa < "
                f"{req['resistencia_flexion_individual_min_mpa']} MPa (mínimo individual)"
            )

        absorcion_max = (
            req["absorcion_max_alta_especificacion_pct"]
            if self.aplicacion == AplicacionAdoquin.PORTUARIO
            else req["absorcion_max_pct"]
        )
        if self.absorcion_porcentaje > absorcion_max:
            fallas.append(f"Absorción {self.absorcion_porcentaje}% > máx {absorcion_max}%")

        return {
            "id": self.nombre,
            "aplicacion": self.aplicacion.value,
            "espesor_mm": self.espesor_mm,
            "espesor_minimo_mm": espesor_min,
            "resistencia_flexion_mpa": self.resistencia_flexion_mpa,
            "absorcion_pct": self.absorcion_porcentaje,
            "absorcion_max_pct": absorcion_max,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 2017" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 4342 — Geotextiles: retención asfáltica en pavimentos asfálticos
# ============================================================================

class TipoGeotextil(Enum):
    NO_TEJIDO = "no_tejido"
    TEJIDO = "tejido"
    PUNZONADO = "punzonado_por_agujas"


REQUISITOS_GEOTEXTIL_NTC4342 = {
    "retencion_asfaltica_min_l_m2": 0.9,   # INVIAS D6140
    "composicion_min_pct": 95.0,           # poliolefinas o poliéster en masa
    "tipos_validos": (TipoGeotextil.NO_TEJIDO, TipoGeotextil.PUNZONADO),
}


@dataclass
class Geotextil:
    """Geotextil para pavimentos asfálticos — NTC 4342 / INVIAS D6140."""
    nombre: str
    tipo: TipoGeotextil
    retencion_asfaltica_l_m2: float
    composicion: str
    porcentaje_poliolefinas: float
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 4342"

    def verificar_ntc4342(self) -> dict:
        """Verifica retención asfáltica mínima, composición y tipo de geotextil."""
        req = REQUISITOS_GEOTEXTIL_NTC4342
        fallas = []

        if self.retencion_asfaltica_l_m2 < req["retencion_asfaltica_min_l_m2"]:
            fallas.append(
                f"Retención asfáltica {self.retencion_asfaltica_l_m2} l/m² < "
                f"{req['retencion_asfaltica_min_l_m2']} l/m² (INVIAS D6140)"
            )
        if self.porcentaje_poliolefinas < req["composicion_min_pct"]:
            fallas.append(
                f"Composición {self.porcentaje_poliolefinas}% < {req['composicion_min_pct']}% "
                "de poliolefinas/poliéster"
            )
        if self.tipo not in req["tipos_validos"]:
            fallas.append(f"Tipo '{self.tipo.value}' no válido — debe ser no tejido punzonado por agujas")

        return {
            "id": self.nombre,
            "tipo": self.tipo.value,
            "retencion_asfaltica_l_m2": self.retencion_asfaltica_l_m2,
            "composicion_pct": self.porcentaje_poliolefinas,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 4342" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 121 — Especificación de desempeño para cemento hidráulico
# ============================================================================

class TipoCemento(Enum):
    UG = "UG"    # Uso General
    ART = "ART"  # Alta Resistencia Temprana
    RS = "RS"    # Resistente a Sulfatos
    CH = "CH"    # Bajo Calor de Hidratación
    AR = "AR"    # Baja Reactividad Álcali-Sílice (opcional)
    A = "A"      # Con Incorporadores de Aire (opcional)


RESISTENCIAS_MINIMAS_NTC121 = {
    TipoCemento.UG:  {3: 12.0, 7: 19.0, 28: 28.0},
    TipoCemento.ART: {1: 12.0, 3: 24.0, 7: 31.0, 28: 38.0},
    TipoCemento.RS:  {3: 10.0, 7: 17.0, 28: 25.0},
    TipoCemento.CH:  {3: 8.0, 7: 14.0, 28: 21.0},
    TipoCemento.AR:  {3: 10.0, 7: 17.0, 28: 25.0},
    TipoCemento.A:   {3: 10.0, 7: 17.0, 28: 25.0},
}

REQUISITOS_CEMENTO_NTC121 = {
    "fraguado_inicial_min_min": 45.0,   # NTC 118 (Vicat)
    "fraguado_inicial_max_min": 420.0,
    "expansion_autoclave_max_pct": 0.80,  # NTC 107
}


@dataclass
class Cemento:
    """Cemento hidráulico — NTC 121 (especificación de desempeño, 2021)."""
    nombre: str
    tipo: TipoCemento
    resistencia_compresion_mpa: Dict[int, float]  # {edad_dias: resistencia}
    tiempo_fraguado_inicial_min: float
    tiempo_fraguado_final_min: float
    expansion_autoclave_porcentaje: float
    finura_blaine_m2_kg: float
    densidad_g_cm3: float
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 121"

    def verificar_ntc121(self) -> dict:
        """Verifica resistencia por edad según tipo, fraguado inicial y expansión."""
        req = REQUISITOS_CEMENTO_NTC121
        fallas = []

        minimos = RESISTENCIAS_MINIMAS_NTC121.get(self.tipo)
        if minimos is None:
            fallas.append(f"Tipo de cemento '{self.tipo.value}' no reconocido en NTC 121")
            minimos = {}

        resistencias_edad = []
        for edad, minimo in minimos.items():
            valor = self.resistencia_compresion_mpa.get(edad, 0.0)
            cumple_edad = valor >= minimo
            if not cumple_edad:
                fallas.append(f"Resistencia a {edad} días: {valor} MPa < mínimo {minimo} MPa (tipo {self.tipo.value})")
            resistencias_edad.append({"edad_dias": edad, "valor_mpa": valor, "minimo_mpa": minimo, "cumple": cumple_edad})

        if not (req["fraguado_inicial_min_min"] <= self.tiempo_fraguado_inicial_min <= req["fraguado_inicial_max_min"]):
            fallas.append(
                f"Fraguado inicial {self.tiempo_fraguado_inicial_min} min fuera de rango "
                f"({req['fraguado_inicial_min_min']}-{req['fraguado_inicial_max_min']} min, NTC 118)"
            )
        if self.expansion_autoclave_porcentaje > req["expansion_autoclave_max_pct"]:
            fallas.append(
                f"Expansión en autoclave {self.expansion_autoclave_porcentaje}% > "
                f"{req['expansion_autoclave_max_pct']}% (NTC 107)"
            )

        return {
            "id": self.nombre,
            "tipo": self.tipo.value,
            "resistencias_por_edad": resistencias_edad,
            "fraguado_inicial_min": self.tiempo_fraguado_inicial_min,
            "expansion_autoclave_pct": self.expansion_autoclave_porcentaje,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 121" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 1299 — Aditivos químicos para concreto (IDT ASTM C494/C494M-05a)
# ============================================================================

class TipoAditivo(Enum):
    A = "A"  # Plastificante (reductor de agua)
    B = "B"  # Retardante
    C = "C"  # Acelerante
    D = "D"  # Plastificante retardante
    E = "E"  # Plastificante acelerante
    F = "F"  # Superplastificante
    G = "G"  # Superplastificante retardante
    H = "H"  # Superplastificante acelerante


DESCRIPCION_ADITIVO_NTC1299 = {
    TipoAditivo.A: {"nombre": "Plastificante (reductor de agua)", "reduccion_agua": "Moderada", "efecto_fraguado": "Neutro"},
    TipoAditivo.B: {"nombre": "Retardante", "reduccion_agua": "No aplica", "efecto_fraguado": "Retarda"},
    TipoAditivo.C: {"nombre": "Acelerante", "reduccion_agua": "No aplica", "efecto_fraguado": "Acelera"},
    TipoAditivo.D: {"nombre": "Plastificante retardante", "reduccion_agua": "Moderada", "efecto_fraguado": "Retarda"},
    TipoAditivo.E: {"nombre": "Plastificante acelerante", "reduccion_agua": "Moderada", "efecto_fraguado": "Acelera"},
    TipoAditivo.F: {"nombre": "Superplastificante", "reduccion_agua": "> 12%", "efecto_fraguado": "Neutro"},
    TipoAditivo.G: {"nombre": "Superplastificante retardante", "reduccion_agua": "> 12%", "efecto_fraguado": "Retarda"},
    TipoAditivo.H: {"nombre": "Superplastificante acelerante", "reduccion_agua": "> 12%", "efecto_fraguado": "Acelera"},
}


@dataclass
class Aditivo:
    """Aditivo químico para concreto — NTC 1299 (adopción idéntica de ASTM C494)."""
    nombre: str
    tipo: TipoAditivo
    descripcion: str
    aplicaciones: List[str] = field(default_factory=list)
    fabricante: Optional[str] = None
    dosificacion_recomendada: Optional[str] = None
    referencia_normativa: str = "NTC 1299"

    def verificar_ntc1299(self) -> dict:
        """Verifica que el tipo de aditivo esté clasificado en NTC 1299 / ASTM C494."""
        fallas = []
        info = DESCRIPCION_ADITIVO_NTC1299.get(self.tipo)
        if info is None:
            fallas.append(f"Tipo de aditivo '{self.tipo}' no reconocido en NTC 1299")

        return {
            "id": self.nombre,
            "tipo": self.tipo.value,
            "clasificacion": info["nombre"] if info else None,
            "reduccion_agua": info["reduccion_agua"] if info else None,
            "efecto_fraguado": info["efecto_fraguado"] if info else None,
            "equivalencia_astm": "ASTM C494/C494M-05a (adopción idéntica IDT)",
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 1299" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 1362 — Cemento hidráulico blanco (incluida en NSR-10)
# ============================================================================

class TipoCementoBlanco(Enum):
    I = "I"      # Uso General
    II = "II"    # Moderada Resistencia a Sulfatos
    III = "III"  # Alta Resistencia Temprana


RESISTENCIAS_MINIMAS_NTC1362 = {
    TipoCementoBlanco.I:   {3: 12.0, 7: 19.0, 28: 28.0},
    TipoCementoBlanco.II:  {3: 10.0, 7: 17.0, 28: 25.0},
    TipoCementoBlanco.III: {1: 12.0, 3: 24.0, 7: 31.0, 28: 38.0},
}

REQUISITOS_CEMENTO_BLANCO_NTC1362 = {
    "blancura_min_pct": 80.0,           # NTC 6274 (valor referencial)
    "fraguado_inicial_min_min": 45.0,   # NTC 118
    "fraguado_inicial_max_min": 420.0,
    "expansion_autoclave_max_pct": 0.80,  # NTC 107
}


@dataclass
class CementoBlanco:
    """Cemento hidráulico blanco — NTC 1362 (segunda actualización, 2018)."""
    nombre: str
    tipo: TipoCementoBlanco
    resistencia_mpa: Dict[int, float]  # {edad_dias: resistencia}
    tiempo_fraguado_inicial_min: float
    tiempo_fraguado_final_min: float
    expansion_autoclave_porcentaje: float
    finura_blaine_m2_kg: float
    blancura_porcentaje: float
    contenido_alcalis_porcentaje: Optional[float] = None
    fabricante: Optional[str] = None
    referencia_normativa: str = "NTC 1362"

    def verificar_ntc1362(self) -> dict:
        """Verifica resistencia por edad, blancura, fraguado inicial y expansión."""
        req = REQUISITOS_CEMENTO_BLANCO_NTC1362
        fallas = []

        minimos = RESISTENCIAS_MINIMAS_NTC1362.get(self.tipo)
        if minimos is None:
            fallas.append(f"Tipo de cemento blanco '{self.tipo.value}' no reconocido en NTC 1362")
            minimos = {}

        resistencias_edad = []
        for edad, minimo in minimos.items():
            valor = self.resistencia_mpa.get(edad, 0.0)
            cumple_edad = valor >= minimo
            if not cumple_edad:
                fallas.append(f"Resistencia a {edad} días: {valor} MPa < mínimo {minimo} MPa (tipo {self.tipo.value})")
            resistencias_edad.append({"edad_dias": edad, "valor_mpa": valor, "minimo_mpa": minimo, "cumple": cumple_edad})

        if self.blancura_porcentaje < req["blancura_min_pct"]:
            fallas.append(f"Blancura {self.blancura_porcentaje}% < {req['blancura_min_pct']}% (NTC 6274)")
        if not (req["fraguado_inicial_min_min"] <= self.tiempo_fraguado_inicial_min <= req["fraguado_inicial_max_min"]):
            fallas.append(
                f"Fraguado inicial {self.tiempo_fraguado_inicial_min} min fuera de rango "
                f"({req['fraguado_inicial_min_min']}-{req['fraguado_inicial_max_min']} min, NTC 118)"
            )
        if self.expansion_autoclave_porcentaje > req["expansion_autoclave_max_pct"]:
            fallas.append(
                f"Expansión en autoclave {self.expansion_autoclave_porcentaje}% > "
                f"{req['expansion_autoclave_max_pct']}% (NTC 107)"
            )

        return {
            "id": self.nombre,
            "tipo": self.tipo.value,
            "resistencias_por_edad": resistencias_edad,
            "blancura_pct": self.blancura_porcentaje,
            "fraguado_inicial_min": self.tiempo_fraguado_inicial_min,
            "expansion_autoclave_pct": self.expansion_autoclave_porcentaje,
            "incluida_nsr10": True,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 1362" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 3459 — Agua para la elaboración de concreto
# ============================================================================

class FuenteAgua(Enum):
    POTABLE = "potable"
    NATURAL = "natural"
    LLUVIA = "lluvia"
    RECICLADA = "reciclada"
    INDUSTRIAL_TRATADA = "industrial_tratada"


LIMITES_AGUA_NTC3459 = {
    "sulfatos_max_mg_l": 1000.0,
    "cloruros_max_reforzado_mg_l": 1000.0,
    "cloruros_max_preesforzado_mg_l": 500.0,
    "solidos_totales_max_mg_l": 50000.0,
    "solidos_disueltos_max_mg_l": 2000.0,
    "ph_min": 5.0,
    "iones_comunes_max_mg_l": 2000.0,  # Ca2+, Mg2+, Na+, K+, NO3-, CO3 2-
}

FUENTES_AGUA_QUE_REQUIEREN_ENSAYO = (
    FuenteAgua.NATURAL, FuenteAgua.LLUVIA, FuenteAgua.RECICLADA, FuenteAgua.INDUSTRIAL_TRATADA,
)


@dataclass
class AnalisisAgua:
    """Resultados de laboratorio de una muestra de agua — NTC 3459."""
    sulfatos_mg_l: float
    cloruros_mg_l: float
    solidos_totales_mg_l: float
    solidos_disueltos_mg_l: float
    ph: float
    turbiedad: Optional[float] = None
    iones_comunes_mg_l: Optional[float] = None
    observaciones: Optional[str] = None


@dataclass
class MuestraAgua:
    """Muestra de agua para elaboración de concreto — NTC 3459 (ed. 2001)."""
    nombre: str
    fuente: FuenteAgua
    analisis: AnalisisAgua
    fecha_muestreo: Optional[str] = None
    laboratorio: Optional[str] = None
    referencia_normativa: str = "NTC 3459"

    def verificar_ntc3459(self, concreto_preesforzado: bool = False) -> dict:
        """Verifica sulfatos, cloruros, sólidos, pH e iones comunes contra los límites NTC 3459."""
        lim = LIMITES_AGUA_NTC3459
        fallas = []
        a = self.analisis

        if a.sulfatos_mg_l > lim["sulfatos_max_mg_l"]:
            fallas.append(f"Sulfatos {a.sulfatos_mg_l} mg/L > {lim['sulfatos_max_mg_l']} mg/L")

        cloruros_max = lim["cloruros_max_preesforzado_mg_l"] if concreto_preesforzado else lim["cloruros_max_reforzado_mg_l"]
        if a.cloruros_mg_l > cloruros_max:
            tipo = "pre-esforzado" if concreto_preesforzado else "reforzado"
            fallas.append(f"Cloruros {a.cloruros_mg_l} mg/L > {cloruros_max} mg/L (concreto {tipo})")

        if a.solidos_totales_mg_l > lim["solidos_totales_max_mg_l"]:
            fallas.append(f"Sólidos totales {a.solidos_totales_mg_l} mg/L > {lim['solidos_totales_max_mg_l']} mg/L")
        if a.solidos_disueltos_mg_l > lim["solidos_disueltos_max_mg_l"]:
            fallas.append(f"Sólidos disueltos {a.solidos_disueltos_mg_l} mg/L > {lim['solidos_disueltos_max_mg_l']} mg/L")
        if a.ph < lim["ph_min"]:
            fallas.append(f"pH {a.ph} < {lim['ph_min']}")
        if a.iones_comunes_mg_l is not None and a.iones_comunes_mg_l > lim["iones_comunes_max_mg_l"]:
            fallas.append(f"Iones comunes {a.iones_comunes_mg_l} mg/L > {lim['iones_comunes_max_mg_l']} mg/L")

        requiere_ensayo = self.fuente in FUENTES_AGUA_QUE_REQUIEREN_ENSAYO

        return {
            "id": self.nombre,
            "fuente": self.fuente.value,
            "requiere_ensayo_adicional": requiere_ensayo,
            "sulfatos_mg_l": a.sulfatos_mg_l,
            "cloruros_mg_l": a.cloruros_mg_l,
            "ph": a.ph,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 3459" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# NTC 3493 — Cenizas volantes y puzolanas naturales como aditivos minerales
# ============================================================================

class ClaseAditivoMineral(Enum):
    N = "N"  # Puzolana natural
    S = "S"  # Puzolana natural (subclase)
    F = "F"  # Ceniza volante (bajo calcio)
    C = "C"  # Ceniza volante (alto calcio)


SUMA_OXIDOS_MINIMA_NTC3493 = {
    ClaseAditivoMineral.N: 70.0,
    ClaseAditivoMineral.S: 70.0,
    ClaseAditivoMineral.F: 70.0,
    ClaseAditivoMineral.C: 50.0,
}

REQUISITOS_ADITIVO_MINERAL_NTC3493 = {
    "perdida_ignicion_max_pct": 6.0,
    "perdida_ignicion_max_excepcional_pct": 12.0,
    "retencion_malla_325_max_pct": 34.0,
}


@dataclass
class AnalisisAditivoMineral:
    """Análisis químico/físico de un aditivo mineral — NTC 3493."""
    sio2_porcentaje: float
    al2o3_porcentaje: float
    fe2o3_porcentaje: float
    perdida_ignicion_porcentaje: float
    retencion_malla_325_porcentaje: float
    finura_blaine_m2_kg: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    observaciones: Optional[str] = None

    @property
    def suma_oxidos_pct(self) -> float:
        """Suma SiO2 + Al2O3 + Fe2O3 (%)."""
        return round(self.sio2_porcentaje + self.al2o3_porcentaje + self.fe2o3_porcentaje, 2)


@dataclass
class AditivoMineral:
    """Ceniza volante o puzolana natural como aditivo mineral — NTC 3493 (equiv. ASTM C618)."""
    nombre: str
    clase: ClaseAditivoMineral
    analisis: AnalisisAditivoMineral
    fabricante: Optional[str] = None
    origen: Optional[str] = None
    referencia_normativa: str = "NTC 3493"

    def verificar_ntc3493(self, tolerancia_loi: bool = False) -> dict:
        """
        Verifica clase, suma de óxidos, pérdida por ignición y retención en malla 325.
        tolerancia_loi=True permite hasta 12% de pérdida por ignición si el desempeño se valida en laboratorio.
        """
        req = REQUISITOS_ADITIVO_MINERAL_NTC3493
        fallas = []

        minimo_oxidos = SUMA_OXIDOS_MINIMA_NTC3493.get(self.clase)
        if minimo_oxidos is None:
            fallas.append(f"Clase de aditivo mineral '{self.clase}' no reconocida en NTC 3493")
            minimo_oxidos = 0.0
        elif self.analisis.suma_oxidos_pct < minimo_oxidos:
            fallas.append(
                f"Suma de óxidos {self.analisis.suma_oxidos_pct}% < {minimo_oxidos}% "
                f"requerido para Clase {self.clase.value}"
            )

        loi_max = req["perdida_ignicion_max_excepcional_pct"] if tolerancia_loi else req["perdida_ignicion_max_pct"]
        if self.analisis.perdida_ignicion_porcentaje > loi_max:
            fallas.append(f"Pérdida por ignición {self.analisis.perdida_ignicion_porcentaje}% > {loi_max}%")

        if self.analisis.retencion_malla_325_porcentaje > req["retencion_malla_325_max_pct"]:
            fallas.append(
                f"Retención en malla No. 325 = {self.analisis.retencion_malla_325_porcentaje}% > "
                f"{req['retencion_malla_325_max_pct']}%"
            )

        return {
            "id": self.nombre,
            "clase": self.clase.value,
            "suma_oxidos_pct": self.analisis.suma_oxidos_pct,
            "suma_oxidos_minima_pct": minimo_oxidos,
            "perdida_ignicion_pct": self.analisis.perdida_ignicion_porcentaje,
            "tolerancia_loi_aplicada": tolerancia_loi,
            "retencion_malla_325_pct": self.analisis.retencion_malla_325_porcentaje,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 3493" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


# ============================================================================
# Demo
# ============================================================================

if __name__ == "__main__":
    import json

    print("=== ADOQUÍN — NTC 2017 ===")
    ad = Adoquin(
        nombre="AD-01", aplicacion=AplicacionAdoquin.VEHICULAR_LIVIANO, tipo=TipoAdoquin.CON_BISEL,
        largo_mm=200.0, ancho_mm=100.0, espesor_mm=80.0,
        resistencia_flexion_mpa=5.5, absorcion_porcentaje=6.0,
    )
    print(json.dumps(ad.verificar_ntc2017(), ensure_ascii=False, indent=2))

    print("\n=== GEOTEXTIL — NTC 4342 ===")
    gt = Geotextil(
        nombre="GT-01", tipo=TipoGeotextil.NO_TEJIDO,
        retencion_asfaltica_l_m2=1.1, composicion="Poliéster", porcentaje_poliolefinas=96.0,
    )
    print(json.dumps(gt.verificar_ntc4342(), ensure_ascii=False, indent=2))

    print("\n=== CEMENTO — NTC 121 ===")
    ce = Cemento(
        nombre="CE-01", tipo=TipoCemento.UG,
        resistencia_compresion_mpa={3: 13.0, 7: 20.0, 28: 29.0},
        tiempo_fraguado_inicial_min=120.0, tiempo_fraguado_final_min=300.0,
        expansion_autoclave_porcentaje=0.3, finura_blaine_m2_kg=350.0, densidad_g_cm3=3.15,
    )
    print(json.dumps(ce.verificar_ntc121(), ensure_ascii=False, indent=2))

    print("\n=== ADITIVO QUÍMICO — NTC 1299 ===")
    adt = Aditivo(nombre="AD-Q-01", tipo=TipoAditivo.F, descripcion="Superplastificante", aplicaciones=["Concreto autocompactante"])
    print(json.dumps(adt.verificar_ntc1299(), ensure_ascii=False, indent=2))

    print("\n=== CEMENTO BLANCO — NTC 1362 ===")
    cb = CementoBlanco(
        nombre="CB-01", tipo=TipoCementoBlanco.I,
        resistencia_mpa={3: 13.0, 7: 20.0, 28: 29.0},
        tiempo_fraguado_inicial_min=100.0, tiempo_fraguado_final_min=280.0,
        expansion_autoclave_porcentaje=0.2, finura_blaine_m2_kg=380.0, blancura_porcentaje=85.0,
    )
    print(json.dumps(cb.verificar_ntc1362(), ensure_ascii=False, indent=2))

    print("\n=== AGUA PARA CONCRETO — NTC 3459 ===")
    ag = MuestraAgua(
        nombre="AG-01", fuente=FuenteAgua.POTABLE,
        analisis=AnalisisAgua(sulfatos_mg_l=400.0, cloruros_mg_l=300.0, solidos_totales_mg_l=1200.0,
                               solidos_disueltos_mg_l=800.0, ph=7.0),
    )
    print(json.dumps(ag.verificar_ntc3459(), ensure_ascii=False, indent=2))

    print("\n=== ADITIVO MINERAL — NTC 3493 ===")
    am = AditivoMineral(
        nombre="AM-01", clase=ClaseAditivoMineral.F,
        analisis=AnalisisAditivoMineral(sio2_porcentaje=50.0, al2o3_porcentaje=20.0, fe2o3_porcentaje=6.0,
                                         perdida_ignicion_porcentaje=4.0, retencion_malla_325_porcentaje=20.0),
    )
    print(json.dumps(am.verificar_ntc3493(), ensure_ascii=False, indent=2))
