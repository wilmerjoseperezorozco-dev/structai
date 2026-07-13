"""
MÓDULO: Laboratorio de Concreto
Normas: NTC 673 (compresión), NTC 396 (asentamiento), NSR-10
Ensayos: resistencia a compresión, slump, curva de maduración, conformidad.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# ─── Requisitos mínimos por zona sísmica (NSR-10) ────────────────────────────
FC_MIN_NSR10 = {
    "BAJA":        17.5,   # MPa
    "INTERMEDIA":  21.0,
    "ALTA":        21.0,
}

# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class CilindroConcreto:
    """Representa un cilindro de concreto ensayado a compresión (NTC 673)."""
    id_cilindro:   str
    edad_dias:     int          # 3, 7, 14 ó 28 días
    diametro_mm:   float        # mm
    carga_kN:      float        # kN aplicados al fallo
    fecha_colada:  date
    fecha_ensayo:  date
    observaciones: str = ""

    @property
    def area_mm2(self) -> float:
        return math.pi * (self.diametro_mm / 2) ** 2

    @property
    def resistencia_MPa(self) -> float:
        """f'c real = Carga (N) / Área (mm²)"""
        return (self.carga_kN * 1000) / self.area_mm2

    @property
    def resistencia_kgcm2(self) -> float:
        return self.resistencia_MPa * 10.197

    def resumen(self) -> dict:
        return {
            "id": self.id_cilindro,
            "edad_dias": self.edad_dias,
            "diametro_mm": self.diametro_mm,
            "area_mm2": round(self.area_mm2, 2),
            "carga_kN": self.carga_kN,
            "fc_MPa": round(self.resistencia_MPa, 2),
            "fc_kgcm2": round(self.resistencia_kgcm2, 2),
        }


@dataclass
class EnsayoSlump:
    """Asentamiento del cono de Abrams — NTC 396."""
    id_muestra:    str
    slump_mm:      float
    temperatura_C: float
    hora_toma:     str
    observaciones: str = ""

    CLASIFICACION = [
        (0,   25,  "S1 — Seca / Tierra húmeda"),
        (25,  75,  "S2 — Plástica baja"),
        (75,  125, "S3 — Plástica media"),
        (125, 175, "S4 — Fluida"),
        (175, 220, "S5 — Muy fluida"),
    ]

    @property
    def clasificacion(self) -> str:
        for lo, hi, nombre in self.CLASIFICACION:
            if lo <= self.slump_mm < hi:
                return nombre
        return "S5+ — Autocompactante / Verificar relación a/c"

    def resumen(self) -> dict:
        alerta = ""
        if self.slump_mm > 200:
            alerta = "⚠️ Slump excesivo — posible exceso de agua"
        if self.temperatura_C > 32:
            alerta += " ⚠️ Temperatura alta — riesgo de fraguado acelerado"
        return {
            "id": self.id_muestra,
            "slump_mm": self.slump_mm,
            "clasificacion": self.clasificacion,
            "temperatura_C": self.temperatura_C,
            "hora": self.hora_toma,
            "alerta": alerta.strip() or "OK",
        }


# ─── Motor de análisis ────────────────────────────────────────────────────────

class AnalisisConcreto:
    """
    Analiza un lote de cilindros, verifica conformidad NSR-10
    y proyecta la resistencia a 28 días.
    """

    # Factores de maduración ACI 209 (aproximado, suelo tipo cemento portland)
    FACTORES_MADUREZ = {3: 0.40, 7: 0.65, 14: 0.88, 28: 1.00}

    def __init__(
        self,
        fc_diseno_MPa: float,
        zona_sismica: str = "ALTA",
        proyecto: str = "",
        elemento: str = "",
    ):
        self.fc_diseno = fc_diseno_MPa
        self.zona_sismica = zona_sismica.upper()
        self.proyecto = proyecto
        self.elemento = elemento
        self.cilindros: list[CilindroConcreto] = []
        self.slumps: list[EnsayoSlump] = []

    def agregar_cilindro(self, cilindro: CilindroConcreto):
        self.cilindros.append(cilindro)

    def agregar_slump(self, slump: EnsayoSlump):
        self.slumps.append(slump)

    # ── Estadísticas ──────────────────────────────────────────────────────────

    def _cilindros_edad(self, edad: int) -> list[CilindroConcreto]:
        return [c for c in self.cilindros if c.edad_dias == edad]

    def estadisticas_edad(self, edad: int) -> dict:
        cils = self._cilindros_edad(edad)
        if not cils:
            return {"edad_dias": edad, "n": 0}
        resistencias = [c.resistencia_MPa for c in cils]
        n = len(resistencias)
        prom = sum(resistencias) / n
        desv = math.sqrt(sum((r - prom) ** 2 for r in resistencias) / max(n - 1, 1))
        cv = (desv / prom * 100) if prom > 0 else 0
        return {
            "edad_dias": edad,
            "n": n,
            "fc_promedio_MPa": round(prom, 2),
            "fc_min_MPa": round(min(resistencias), 2),
            "fc_max_MPa": round(max(resistencias), 2),
            "desv_std_MPa": round(desv, 2),
            "cv_pct": round(cv, 1),
            "calidad_control": self._calidad_cv(cv),
        }

    @staticmethod
    def _calidad_cv(cv: float) -> str:
        if cv < 10: return "EXCELENTE"
        if cv < 15: return "BUENA"
        if cv < 20: return "REGULAR"
        return "DEFICIENTE — Revisar proceso"

    # ── Proyección a 28 días ──────────────────────────────────────────────────

    def proyectar_28_dias(self, edad: int) -> Optional[float]:
        """Proyecta fc@28d desde fc a edad temprana usando factores ACI 209."""
        cils = self._cilindros_edad(edad)
        if not cils:
            return None
        factor = self.FACTORES_MADUREZ.get(edad)
        if not factor:
            return None
        fc_edad = sum(c.resistencia_MPa for c in cils) / len(cils)
        return round(fc_edad / factor, 2)

    # ── Conformidad NSR-10 / ACI 318 ─────────────────────────────────────────

    def verificar_conformidad(self) -> dict:
        """
        Criterio ACI 318 (adoptado NSR-10):
        Conforme si:
          1) Ningún promedio de 2 cilindros consecutivos < fc_diseño
          2) Ningún cilindro individual < (fc_diseño - 3.5 MPa)
        """
        cils_28 = self._cilindros_edad(28)
        fc_min_nsr = FC_MIN_NSR10.get(self.zona_sismica, 21.0)

        resultado = {
            "fc_diseno_MPa": self.fc_diseno,
            "fc_min_nsr10_MPa": fc_min_nsr,
            "zona_sismica": self.zona_sismica,
            "cilindros_28d": len(cils_28),
            "criterio_1_ok": True,
            "criterio_2_ok": True,
            "fallas": [],
            "proyeccion_28d": {},
            "veredicto": "CONFORME",
        }

        if not cils_28:
            # Proyectar desde edades tempranas
            for edad in [7, 14, 3]:
                proy = self.proyectar_28_dias(edad)
                if proy:
                    resultado["proyeccion_28d"] = {
                        "desde_edad": edad,
                        "fc_proyectado_MPa": proy,
                        "cumple_diseno": proy >= self.fc_diseno,
                        "cumple_nsr10": proy >= fc_min_nsr,
                    }
                    if proy < self.fc_diseno:
                        resultado["veredicto"] = "PROYECCION BAJO fc_DISENO — Monitorear"
                    break
            return resultado

        resistencias = [c.resistencia_MPa for c in cils_28]

        # Criterio 1: promedios consecutivos
        for i in range(len(resistencias) - 1):
            prom = (resistencias[i] + resistencias[i + 1]) / 2
            if prom < self.fc_diseno:
                resultado["criterio_1_ok"] = False
                resultado["fallas"].append(
                    f"Crit.1: Promedio cils {i+1}-{i+2} = {prom:.2f} MPa < {self.fc_diseno} MPa"
                )

        # Criterio 2: ningún cilindro < (fc - 3.5 MPa)
        limite_ind = self.fc_diseno - 3.5
        for c in cils_28:
            if c.resistencia_MPa < limite_ind:
                resultado["criterio_2_ok"] = False
                resultado["fallas"].append(
                    f"Crit.2: {c.id_cilindro} = {c.resistencia_MPa:.2f} MPa < {limite_ind:.1f} MPa"
                )

        # Verificar mínimo NSR-10
        if self.fc_diseno < fc_min_nsr:
            resultado["fallas"].append(
                f"NSR-10: fc_diseño {self.fc_diseno} MPa < mínimo zona {self.zona_sismica} ({fc_min_nsr} MPa)"
            )

        if resultado["fallas"]:
            resultado["veredicto"] = "NO CONFORME — Requiere acción correctiva"
        else:
            fc_prom = sum(resistencias) / len(resistencias)
            resultado["veredicto"] = f"CONFORME — fc_prom28d = {fc_prom:.2f} MPa"

        return resultado

    def informe_completo(self) -> dict:
        """Genera el informe completo del lote de concreto."""
        return {
            "proyecto": self.proyecto,
            "elemento": self.elemento,
            "fc_diseno_MPa": self.fc_diseno,
            "zona_sismica": self.zona_sismica,
            "fecha_informe": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estadisticas": {
                edad: self.estadisticas_edad(edad)
                for edad in [3, 7, 14, 28]
                if self._cilindros_edad(edad)
            },
            "cilindros": [c.resumen() for c in self.cilindros],
            "slumps": [s.resumen() for s in self.slumps],
            "conformidad": self.verificar_conformidad(),
        }


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== ENSAYO DE CONCRETO — NTC 673 ===\n")

    analisis = AnalisisConcreto(
        fc_diseno_MPa=21.0,
        zona_sismica="ALTA",
        proyecto="Edificio Res. Los Pinos",
        elemento="Columna C-1 Piso 3",
    )

    # Slump en obra
    analisis.agregar_slump(EnsayoSlump("S-01", slump_mm=95, temperatura_C=28, hora_toma="08:30"))

    # Cilindros de 7 días
    datos_7d = [("CIL-01", 152, 185.0), ("CIL-02", 152, 192.0), ("CIL-03", 152, 179.0)]
    for id_, d, carga in datos_7d:
        analisis.agregar_cilindro(CilindroConcreto(
            id_cilindro=id_, edad_dias=7, diametro_mm=d, carga_kN=carga,
            fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 8)
        ))

    # Cilindros de 28 días
    datos_28d = [("CIL-04", 152, 260.0), ("CIL-05", 152, 268.0), ("CIL-06", 152, 255.0)]
    for id_, d, carga in datos_28d:
        analisis.agregar_cilindro(CilindroConcreto(
            id_cilindro=id_, edad_dias=28, diametro_mm=d, carga_kN=carga,
            fecha_colada=date(2026, 6, 1), fecha_ensayo=date(2026, 6, 29)
        ))

    informe = analisis.informe_completo()
    print(json.dumps(informe, ensure_ascii=False, indent=2))
