"""
MÓDULO: Laboratorio de Agregados
Normas: NTC 174 (requisitos), NTC 77 (granulometría), NTC 237 (densidad/absorción),
        NTC 218 (desgaste Los Ángeles), NTC 4205 (índice de aplanamiento y alargamiento)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# ─── Límites granulométricos NTC 174 ─────────────────────────────────────────
GRADACIONES_AGREGADO_GRUESO = {
    "Nº1": {37.5: 100, 25.0: 90, 19.0: 25, 12.5: 0, "nombre": "1\" a ½\""},
    "Nº2": {50.0: 100, 37.5: 90, 25.0: 35, 19.0: 10, 12.5: 0, "nombre": "2\" a ¾\""},
    "Nº3": {37.5: 100, 25.0: 90, 19.0: 40, 9.5: 0, "nombre": "1½\" a ½\""},
    "Nº4": {25.0: 100, 19.0: 90, 9.5: 20, 4.75: 0, "nombre": "¾\" a #4"},
    "Nº5": {19.0: 100, 12.5: 90, 9.5: 40, 4.75: 0, "nombre": "¾\" a #4"},
    "Nº6": {19.0: 100, 12.5: 90, 9.5: 40, 4.75: 15, 2.36: 0, "nombre": "¾\" a #8"},
    "Nº7": {12.5: 100, 9.5: 90, 4.75: 40, 2.36: 0, "nombre": "½\" a #8"},
    "Nº8": {9.5: 100, 4.75: 85, 2.36: 10, 1.18: 0, "nombre": "#4 a #16"},
}

# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class AgregadoGrueso:
    """Propiedades del agregado grueso — NTC 174, 237, 218."""
    id_muestra:          str
    origen:              str              # "Triturado", "Rodado", "Mixto"
    masa_sss_g:          float            # Masa en SSS (superficie saturada seca)
    masa_seca_g:         float            # Masa seca en horno
    masa_sumergida_g:    float            # Masa bajo agua (canastilla)
    perdida_LA_pct:      Optional[float]  # Desgaste Los Ángeles (%)
    particulas_planas_pct: Optional[float] = None
    particulas_alargadas_pct: Optional[float] = None

    @property
    def densidad_sss(self) -> float:
        """Densidad aparente SSS (g/cm³) — NTC 237."""
        vol = self.masa_sss_g - self.masa_sumergida_g
        return round(self.masa_sss_g / vol, 3) if vol > 0 else 0

    @property
    def densidad_aparente(self) -> float:
        """Densidad aparente seca (g/cm³)."""
        vol = self.masa_sss_g - self.masa_sumergida_g
        return round(self.masa_seca_g / vol, 3) if vol > 0 else 0

    @property
    def absorcion_pct(self) -> float:
        """Absorción (%) — NTC 237."""
        if self.masa_seca_g <= 0:
            return 0
        return round((self.masa_sss_g - self.masa_seca_g) / self.masa_seca_g * 100, 2)

    def verificar_ntc174(self, uso: str = "CONCRETO") -> dict:
        """
        Verifica cumplimiento de requisitos NTC 174 según uso.
        uso: "CONCRETO", "ASFALTO", "BASE_GRANULAR"
        """
        limites = {
            "CONCRETO":       {"abs_max": 3.0, "la_max": 40.0, "dens_min": 2.4},
            "ASFALTO":        {"abs_max": 2.0, "la_max": 35.0, "dens_min": 2.5},
            "BASE_GRANULAR":  {"abs_max": 4.0, "la_max": 50.0, "dens_min": 2.3},
        }.get(uso, {"abs_max": 3.0, "la_max": 40.0, "dens_min": 2.4})

        fallas = []
        if self.absorcion_pct > limites["abs_max"]:
            fallas.append(f"Absorción {self.absorcion_pct}% > máx {limites['abs_max']}%")
        if self.perdida_LA_pct and self.perdida_LA_pct > limites["la_max"]:
            fallas.append(f"Desgaste LA {self.perdida_LA_pct}% > máx {limites['la_max']}%")
        if self.densidad_aparente < limites["dens_min"]:
            fallas.append(f"Densidad {self.densidad_aparente} g/cm³ < mín {limites['dens_min']}")
        if self.particulas_planas_pct and self.particulas_planas_pct > 15:
            fallas.append(f"Partículas planas {self.particulas_planas_pct}% > 15%")

        return {
            "id": self.id_muestra,
            "uso": uso,
            "densidad_sss_gcm3": self.densidad_sss,
            "densidad_aparente_gcm3": self.densidad_aparente,
            "absorcion_pct": self.absorcion_pct,
            "perdida_LA_pct": self.perdida_LA_pct,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 174" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }


@dataclass
class AgregadoFino:
    """Propiedades del agregado fino (arena) — NTC 174, NTC 237, NTC 77."""
    id_muestra:       str
    masa_sss_g:       float
    masa_seca_g:      float
    masa_frasco_agua: float    # Masa frasco + agua (sin muestra)
    masa_frasco_agua_muestra: float  # Masa frasco + agua + muestra
    modulo_finura:    float
    impurezas_organicas: str = "CLARO"   # "CLARO", "MÁS CLARO", "OSCURO"

    @property
    def densidad_sss(self) -> float:
        """Picnómetro — ASTM C128 / NTC 237."""
        vol = self.masa_sss_g - (self.masa_frasco_agua_muestra - self.masa_frasco_agua)
        return round(self.masa_sss_g / vol, 3) if vol > 0 else 0

    @property
    def absorcion_pct(self) -> float:
        if self.masa_seca_g <= 0:
            return 0
        return round((self.masa_sss_g - self.masa_seca_g) / self.masa_seca_g * 100, 2)

    def verificar_ntc174(self) -> dict:
        fallas = []
        if not (2.3 <= self.modulo_finura <= 3.1):
            fallas.append(f"MF = {self.modulo_finura} fuera rango 2.3–3.1 NTC 174")
        if self.absorcion_pct > 5.0:
            fallas.append(f"Absorción {self.absorcion_pct}% > 5% máx")
        if self.densidad_sss < 2.3:
            fallas.append(f"Densidad SSS {self.densidad_sss} < 2.3 g/cm³")
        if self.impurezas_organicas == "OSCURO":
            fallas.append("Impurezas orgánicas: Color OSCURO — posible rechazo")

        return {
            "id": self.id_muestra,
            "densidad_sss_gcm3": self.densidad_sss,
            "absorcion_pct": self.absorcion_pct,
            "modulo_finura": self.modulo_finura,
            "impurezas": self.impurezas_organicas,
            "fallas": fallas,
            "veredicto": "CUMPLE NTC 174" if not fallas else f"NO CUMPLE — {len(fallas)} falla(s)",
        }

    def clasificacion_mf(self) -> str:
        mf = self.modulo_finura
        if mf < 2.3:   return "Arena MUY FINA — no recomendada para concreto"
        if mf < 2.6:   return "Arena FINA"
        if mf < 2.9:   return "Arena MEDIA"
        if mf <= 3.1:  return "Arena GRUESA"
        return "Arena MUY GRUESA — verificar NTC 174"


# ─── Diseño de mezcla (ACI 211.1) ─────────────────────────────────────────────

class DisenoMezclaACI:
    """
    Diseño básico de mezcla de concreto por método ACI 211.1.
    Para diseño definitivo se requiere ajuste en laboratorio.
    """

    # Relación a/c vs fc (tabla ACI 211.1 - concreto sin aire incluido)
    TABLA_AC = [
        (17.5, 0.82), (21.0, 0.74), (24.5, 0.68),
        (28.0, 0.62), (31.5, 0.57), (35.0, 0.53), (42.0, 0.44),
    ]

    def __init__(
        self,
        fc_MPa: float,
        tamaño_max_agregado_mm: float = 19.0,
        asentamiento_mm: float = 75.0,
        zona_sismica: str = "ALTA",
    ):
        self.fc = fc_MPa
        self.tma = tamaño_max_agregado_mm
        self.slump = asentamiento_mm
        self.zona_sismica = zona_sismica

    def _relacion_ac(self) -> float:
        """Interpola relación a/c desde tabla ACI."""
        tabla = self.TABLA_AC
        if self.fc <= tabla[0][0]:
            return tabla[0][1]
        if self.fc >= tabla[-1][0]:
            return tabla[-1][1]
        for i in range(len(tabla) - 1):
            fc0, ac0 = tabla[i]
            fc1, ac1 = tabla[i + 1]
            if fc0 <= self.fc <= fc1:
                t = (self.fc - fc0) / (fc1 - fc0)
                return round(ac0 + t * (ac1 - ac0), 3)
        return 0.55

    def calcular(self, densidad_fino: float = 2.65, densidad_grueso: float = 2.70) -> dict:
        """
        Retorna proporciones de mezcla por m³.
        Método simplificado ACI 211.1.
        """
        # FC_MIN_NSR10 referenciado inline

        fc_min = {"BAJA": 17.5, "INTERMEDIA": 21.0, "ALTA": 21.0}.get(self.zona_sismica.upper(), 21.0)
        fc_real = max(self.fc, fc_min)
        if fc_real > self.fc:
            nota_fc = f"⚠️ fc aumentado de {self.fc} a {fc_real} MPa por mínimo NSR-10 zona {self.zona_sismica}"
        else:
            nota_fc = "fc_diseño cumple mínimo NSR-10"

        ac = self._relacion_ac()

        # Contenido de agua (tabla ACI según TMA y slump)
        agua_base = {
            9.5:  {"S1": 207, "S2": 228, "S3": 243},
            12.5: {"S1": 199, "S2": 216, "S3": 228},
            19.0: {"S1": 190, "S2": 205, "S3": 216},
            25.0: {"S1": 179, "S2": 193, "S3": 202},
            37.5: {"S1": 166, "S2": 181, "S3": 190},
        }
        slump_key = "S1" if self.slump < 50 else "S2" if self.slump < 100 else "S3"
        tma_key = min(agua_base.keys(), key=lambda x: abs(x - self.tma))
        agua_kg = agua_base[tma_key][slump_key]

        cemento_kg = round(agua_kg / ac, 1)
        agregado_grueso_kg = round(0.67 * 2700, 1)   # Vol seco varillado × densidad (estimado)
        vol_pasta = (agua_kg / 1000 + cemento_kg / 3150)
        vol_grueso = agregado_grueso_kg / (densidad_grueso * 1000)
        vol_fino = 1.0 - vol_pasta - vol_grueso - 0.01  # 1% aire
        agregado_fino_kg = round(vol_fino * densidad_fino * 1000, 1)

        return {
            "fc_diseno_MPa": fc_real,
            "zona_sismica": self.zona_sismica,
            "nota_nsr10": nota_fc,
            "relacion_a_c": ac,
            "slump_mm": self.slump,
            "tma_mm": self.tma,
            "proporciones_por_m3": {
                "agua_kg":             agua_kg,
                "cemento_kg":          cemento_kg,
                "agregado_fino_kg":    agregado_fino_kg,
                "agregado_grueso_kg":  agregado_grueso_kg,
            },
            "relacion_masa": {
                "cemento": 1.0,
                "fino":    round(agregado_fino_kg / cemento_kg, 2),
                "grueso":  round(agregado_grueso_kg / cemento_kg, 2),
                "agua":    round(agua_kg / cemento_kg, 2),
            },
            "nota_diseno": "Diseño ACI 211.1 simplificado — ajustar con ensayos de laboratorio reales",
        }


# ─── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== AGREGADO GRUESO — NTC 174 ===")
    ag = AgregadoGrueso(
        id_muestra="AG-01", origen="Triturado",
        masa_sss_g=2000.0, masa_seca_g=1958.0, masa_sumergida_g=1222.0,
        perdida_LA_pct=28.5
    )
    print(json.dumps(ag.verificar_ntc174("CONCRETO"), ensure_ascii=False, indent=2))

    print("\n=== AGREGADO FINO — NTC 174 ===")
    af = AgregadoFino(
        id_muestra="AF-01",
        masa_sss_g=500.0, masa_seca_g=487.0,
        masa_frasco_agua=670.0, masa_frasco_agua_muestra=984.0,
        modulo_finura=2.75, impurezas_organicas="CLARO"
    )
    print(json.dumps(af.verificar_ntc174(), ensure_ascii=False, indent=2))
    print(f"Clasificación MF: {af.clasificacion_mf()}")

    print("\n=== DISEÑO DE MEZCLA ACI 211.1 ===")
    diseno = DisenoMezclaACI(fc_MPa=21.0, tamaño_max_agregado_mm=19.0,
                              asentamiento_mm=75, zona_sismica="ALTA")
    print(json.dumps(diseno.calcular(), ensure_ascii=False, indent=2))
