"""
MÓDULO: Laboratorio de Suelos
Normas: INV E-125/126 (Atterberg), INV E-141/142 (Proctor), INV E-148 (CBR),
        INV E-123 (granulometría), ASTM D2487 (USCS), AASHTO M145
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ─── CLASIFICACIÓN USCS ───────────────────────────────────────────────────────

class ClasificadorUSCS:
    """
    Clasifica suelos por el Sistema Unificado de Clasificación de Suelos
    (ASTM D2487 / USCS), integrando granulometría y límites de Atterberg.
    """

    @staticmethod
    def clasificar(
        pasa_200_pct: float,       # % que pasa tamiz #200
        pasa_4_pct: float,         # % que pasa tamiz #4
        d10: Optional[float],      # mm — diámetro efectivo
        d30: Optional[float],      # mm
        d60: Optional[float],      # mm
        ll: Optional[float],       # Límite Líquido (%)
        ip: Optional[float],       # Índice de Plasticidad (%)
    ) -> dict:

        finos = pasa_200_pct

        # ── SUELOS GRUESOS (< 50% finos) ──────────────────────────────────
        if finos < 50:
            gruesos = 100 - finos
            gravas = 100 - pasa_4_pct
            arenas = pasa_4_pct - finos

            # Coeficientes de forma (si hay datos granulométricos)
            cu, cc = None, None
            if d10 and d30 and d60 and d10 > 0:
                cu = round(d60 / d10, 2)
                cc = round((d30 ** 2) / (d60 * d10), 2)

            if gravas > arenas:
                # GRAVA
                if finos < 5:
                    if cu and cc and cu >= 4 and 1 <= cc <= 3:
                        simbolo, nombre = "GW", "Grava bien gradada"
                    else:
                        simbolo, nombre = "GP", "Grava mal gradada"
                elif finos > 12:
                    if ip is None or ll is None:
                        simbolo, nombre = "GM", "Grava limosa (sin Atterberg)"
                    elif ip < 4 or (ll < 50 and ip < 0.73 * (ll - 20)):
                        simbolo, nombre = "GM", "Grava limosa"
                    else:
                        simbolo, nombre = "GC", "Grava arcillosa"
                else:
                    simbolo, nombre = "GW-GM / GP-GC", "Grava límite (5–12% finos)"
            else:
                # ARENA
                if finos < 5:
                    if cu and cc and cu >= 6 and 1 <= cc <= 3:
                        simbolo, nombre = "SW", "Arena bien gradada"
                    else:
                        simbolo, nombre = "SP", "Arena mal gradada"
                elif finos > 12:
                    if ip is None or ll is None:
                        simbolo, nombre = "SM", "Arena limosa (sin Atterberg)"
                    elif ip < 4 or (ll < 50 and ip < 0.73 * (ll - 20)):
                        simbolo, nombre = "SM", "Arena limosa"
                    else:
                        simbolo, nombre = "SC", "Arena arcillosa"
                else:
                    simbolo, nombre = "SW-SM / SP-SC", "Arena límite (5–12% finos)"

            return {
                "tipo": "SUELO GRUESO",
                "simbolo_uscs": simbolo,
                "nombre": nombre,
                "finos_pct": round(finos, 1),
                "cu": cu,
                "cc": cc,
            }

        # ── SUELOS FINOS (≥ 50% finos) ────────────────────────────────────
        else:
            if ll is None or ip is None:
                return {
                    "tipo": "SUELO FINO",
                    "simbolo_uscs": "?",
                    "nombre": "Indeterminado — faltan Límites de Atterberg",
                    "finos_pct": round(finos, 1),
                }

            # Carta de plasticidad (Casagrande)
            linea_A = 0.73 * (ll - 20)  # IP línea A

            if ll < 50:   # Baja plasticidad
                if ip < linea_A or ip < 4:
                    simbolo, nombre = "ML", "Limo de baja plasticidad"
                else:
                    simbolo, nombre = "CL", "Arcilla de baja plasticidad"
                    if ip < 7:
                        simbolo, nombre = "CL-ML", "Arcilla-limo de baja plasticidad"
            else:          # Alta plasticidad
                if ip < linea_A:
                    simbolo, nombre = "MH", "Limo de alta plasticidad / Limo elástico"
                else:
                    simbolo, nombre = "CH", "Arcilla de alta plasticidad / Arcilla grasa"

            # Orgánicos (heurístico: LL cae > 3pt tras secado en horno — no aplica aquí)
            # Se marca como posible si LL > 50 e IP bajo
            organico = ll > 50 and ip < linea_A * 0.75

            return {
                "tipo": "SUELO FINO",
                "simbolo_uscs": simbolo,
                "nombre": nombre,
                "finos_pct": round(finos, 1),
                "ll": ll,
                "lp": round(ll - ip, 1) if ip else None,
                "ip": ip,
                "posiblemente_organico": organico,
            }

    @staticmethod
    def aashto(ll: float, ip: float, pasa_200_pct: float) -> dict:
        """Clasificación AASHTO M145 complementaria."""
        f = pasa_200_pct
        if f <= 35:
            if ll <= 40 and ip <= 10:
                grupo = "A-2-4" if ip <= 10 else "A-2-6"
            else:
                grupo = "A-2-7"
            if f <= 35 and ll <= 40 and ip <= 10:
                grupo = "A-1" if f <= 50 else "A-3"
        elif ll <= 40:
            grupo = "A-4" if ip <= 10 else "A-6"
        else:
            grupo = "A-5" if ip <= 10 else "A-7"

        ig = max(0, (f - 35) * (0.2 + 0.005 * (ll - 40)) + 0.01 * (f - 15) * (ip - 10))
        aptitud = (
            "EXCELENTE / BUENA" if ig == 0 else
            "BUENA" if ig <= 1 else
            "REGULAR" if ig <= 4 else
            "MALA" if ig <= 8 else
            "MUY MALA"
        )
        return {
            "grupo_aashto": f"{grupo} (IG={round(ig,1)})",
            "aptitud_subrasante": aptitud,
        }


# ─── LÍMITES DE ATTERBERG ─────────────────────────────────────────────────────

@dataclass
class LimitesAtterberg:
    """INV E-125 (Límite Líquido) e INV E-126 (Límite Plástico)."""
    id_muestra:   str
    ll:           float    # Límite Líquido (%)
    lp:           float    # Límite Plástico (%)
    profundidad_m: float = 0.0

    @property
    def ip(self) -> float:
        return round(self.ll - self.lp, 1)

    @property
    def actividad(self) -> str:
        """Índice de actividad (Skempton) — requiere % arcilla."""
        return "Calcular con % fracción arcilla"

    @property
    def clasificacion_ip(self) -> str:
        if self.ip < 7:   return "No plástico / Muy baja plasticidad"
        if self.ip < 15:  return "Baja plasticidad"
        if self.ip < 30:  return "Media plasticidad"
        if self.ip < 50:  return "Alta plasticidad"
        return "Muy alta plasticidad"

    def resumen(self) -> dict:
        return {
            "id": self.id_muestra,
            "prof_m": self.profundidad_m,
            "LL_%": self.ll,
            "LP_%": self.lp,
            "IP_%": self.ip,
            "plasticidad": self.clasificacion_ip,
        }


# ─── PROCTOR ──────────────────────────────────────────────────────────────────

@dataclass
class EnsayoProctor:
    """
    Compactación Proctor Estándar (INV E-141) o Modificado (INV E-142).
    Entrada: lista de puntos (humedad_%, densidad_seca_g/cm³)
    """
    id_muestra:   str
    tipo:         str                          # "ESTANDAR" o "MODIFICADO"
    puntos:       list[tuple[float, float]]    # [(w%, ρd g/cm³), ...]

    @property
    def optimo(self) -> dict:
        """
        Encuentra el punto de densidad máxima seca por interpolación cuadrática.
        """
        if len(self.puntos) < 3:
            return {"error": "Se necesitan al menos 3 puntos para ajuste"}

        ws = [p[0] for p in self.puntos]
        rds = [p[1] for p in self.puntos]

        # Ajuste cuadrático simple
        n = len(ws)
        sx  = sum(ws);       sx2 = sum(x**2 for x in ws)
        sx3 = sum(x**3 for x in ws); sx4 = sum(x**4 for x in ws)
        sy  = sum(rds);      sxy = sum(ws[i]*rds[i] for i in range(n))
        sx2y= sum(ws[i]**2*rds[i] for i in range(n))

        # Sistema Ax = b (mínimos cuadrados)
        try:
            import numpy as np
            coef = np.polyfit(ws, rds, 2)
            a, b, c = (float(v) for v in coef)  # numpy.float64 no es JSON-serializable por FastAPI
            if a >= 0:
                # No hay máximo real — tomar el máximo observado
                idx_max = rds.index(max(rds))
                return {
                    "wopt_%": round(ws[idx_max], 1),
                    "rdmax_gcm3": round(rds[idx_max], 3),
                    "metodo": "Valor observado (sin máximo cuadrático)"
                }
            wopt = -b / (2 * a)
            rdmax = a * wopt**2 + b * wopt + c
            return {
                "wopt_%": round(wopt, 1),
                "rdmax_gcm3": round(rdmax, 3),
                "metodo": "Ajuste cuadrático"
            }
        except ImportError:
            idx_max = rds.index(max(rds))
            return {
                "wopt_%": round(ws[idx_max], 1),
                "rdmax_gcm3": round(rds[idx_max], 3),
                "metodo": "Valor observado (numpy no disponible)"
            }

    def verificar_compactacion(self, densidad_campo_gcm3: float, porcentaje_minimo: float = 95.0) -> dict:
        opt = self.optimo
        if "error" in opt:
            return opt
        rdmax = opt["rdmax_gcm3"]
        pct = round(densidad_campo_gcm3 / rdmax * 100, 1)
        return {
            "densidad_campo_gcm3": densidad_campo_gcm3,
            "densidad_max_gcm3": rdmax,
            "compactacion_pct": pct,
            "minimo_requerido_pct": porcentaje_minimo,
            "cumple": pct >= porcentaje_minimo,
            "veredicto": "CONFORME" if pct >= porcentaje_minimo else f"NO CONFORME — Falta {round(porcentaje_minimo - pct, 1)}% de compactación",
        }

    def resumen(self) -> dict:
        return {
            "id": self.id_muestra,
            "tipo": self.tipo,
            "puntos_ensayo": self.puntos,
            "optimo": self.optimo,
        }


# ─── CBR ──────────────────────────────────────────────────────────────────────

@dataclass
class EnsayoCBR:
    """
    CBR de laboratorio — INV E-148.
    El CBR se lee a penetración 2.54 mm (0.1") como porcentaje de la carga patrón.
    Carga patrón a 2.54 mm: 13.34 kN (3000 lbf)
    Carga patrón a 5.08 mm: 20.01 kN (4500 lbf)
    """
    id_muestra:       str
    carga_254_kN:     float    # Carga a 2.54 mm de penetración
    carga_508_kN:     float    # Carga a 5.08 mm de penetración
    densidad_seca:    float    # g/cm³
    humedad_pct:      float    # %
    condicion:        str = "SATURADO"    # o "SIN SATURAR"

    PATRON_254 = 13.34   # kN
    PATRON_508 = 20.01   # kN

    @property
    def cbr_254(self) -> float:
        return round(self.carga_254_kN / self.PATRON_254 * 100, 1)

    @property
    def cbr_508(self) -> float:
        return round(self.carga_508_kN / self.PATRON_508 * 100, 1)

    @property
    def cbr_diseno(self) -> float:
        """CBR de diseño = max de las dos penetraciones (INVIAS)."""
        return max(self.cbr_254, self.cbr_508)

    @property
    def clasificacion_subrasante(self) -> str:
        cbr = self.cbr_diseno
        if cbr < 3:   return "S0 — SUBRASANTE MUY MALA (reemplazar material)"
        if cbr < 6:   return "S1 — SUBRASANTE MALA"
        if cbr < 10:  return "S2 — SUBRASANTE REGULAR"
        if cbr < 20:  return "S3 — SUBRASANTE BUENA"
        if cbr < 30:  return "S4 — SUBRASANTE MUY BUENA"
        return "S5 — SUBRASANTE EXCELENTE"

    def espesor_pavimento_cm(self, esal_millones: float) -> dict:
        """
        Estimación simplificada de espesores por método AASHTO 93.
        Solo referencial — diseño final requiere análisis completo.
        """
        cbr = self.cbr_diseno
        mr_mpa = round(10.33 * (cbr ** 0.65), 1)   # Correlación Mr = 10.33*CBR^0.65 (AASHTO)

        # Número estructural simplificado
        sn_requerido = 0.38 * (esal_millones ** 0.2) * (1 / (cbr ** 0.2))

        return {
            "cbr_diseno_pct": cbr,
            "Mr_MPa": mr_mpa,
            "SN_estimado": round(sn_requerido, 2),
            "espesor_base_cm_ref": round(sn_requerido * 10, 0),
            "nota": "Diseño referencial — verificar con método AASHTO 93 completo (INVIAS Manual de Diseño Geométrico)",
        }

    def resumen(self) -> dict:
        return {
            "id": self.id_muestra,
            "cbr_2.54mm_%": self.cbr_254,
            "cbr_5.08mm_%": self.cbr_508,
            "cbr_diseno_%": self.cbr_diseno,
            "clasificacion": self.clasificacion_subrasante,
            "densidad_seca": self.densidad_seca,
            "humedad_%": self.humedad_pct,
            "condicion": self.condicion,
        }


# ─── GRANULOMETRÍA ────────────────────────────────────────────────────────────

@dataclass
class GranulometriaAgregado:
    """
    Análisis granulométrico por tamizado — INV E-123 / NTC 77.
    tamices: lista de (abertura_mm, pasa_acumulado_pct)
    """
    id_muestra: str
    tamices:    list[tuple[float, float]]   # [(abertura_mm, % pasa), ...]

    def _interpolar_d(self, objetivo_pct: float) -> Optional[float]:
        """Interpola linealmente el diámetro para un % que pasa dado."""
        tamices_ord = sorted(self.tamices, key=lambda x: x[0])
        for i in range(len(tamices_ord) - 1):
            d0, p0 = tamices_ord[i]
            d1, p1 = tamices_ord[i + 1]
            if p0 <= objetivo_pct <= p1:
                if p1 == p0:
                    return d0
                t = (objetivo_pct - p0) / (p1 - p0)
                return round(d0 + t * (d1 - d0), 4)
        return None

    @property
    def d10(self) -> Optional[float]: return self._interpolar_d(10)
    @property
    def d30(self) -> Optional[float]: return self._interpolar_d(30)
    @property
    def d60(self) -> Optional[float]: return self._interpolar_d(60)

    @property
    def cu(self) -> Optional[float]:
        return round(self.d60 / self.d10, 2) if self.d10 and self.d60 and self.d10 > 0 else None

    @property
    def cc(self) -> Optional[float]:
        if self.d10 and self.d30 and self.d60 and self.d10 > 0 and self.d60 > 0:
            return round((self.d30 ** 2) / (self.d60 * self.d10), 2)
        return None

    @property
    def pasa_200(self) -> Optional[float]:
        for d, p in self.tamices:
            if abs(d - 0.075) < 0.01:
                return p
        return None

    @property
    def modulo_finura(self) -> Optional[float]:
        """
        Módulo de finura (NTC 77) — para arenas.
        Suma de % retenido acumulado en tamices: 9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15 mm
        """
        tamices_mf = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15]
        suma = 0
        conteo = 0
        for t_obj in tamices_mf:
            for d, p in self.tamices:
                if abs(d - t_obj) < 0.1:
                    retenido = 100 - p
                    suma += retenido
                    conteo += 1
                    break
        if conteo < 5:
            return None
        return round(suma / 100, 2)

    def resumen(self) -> dict:
        return {
            "id": self.id_muestra,
            "d10_mm": self.d10,
            "d30_mm": self.d30,
            "d60_mm": self.d60,
            "Cu": self.cu,
            "Cc": self.cc,
            "pasa_200_%": self.pasa_200,
            "modulo_finura": self.modulo_finura,
        }


# ─── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== CLASIFICACIÓN USCS ===")
    r = ClasificadorUSCS.clasificar(
        pasa_200_pct=65, pasa_4_pct=95,
        d10=None, d30=None, d60=None,
        ll=42, ip=18
    )
    print(json.dumps(r, ensure_ascii=False, indent=2))

    print("\n=== AASHTO ===")
    print(json.dumps(ClasificadorUSCS.aashto(ll=42, ip=18, pasa_200_pct=65), ensure_ascii=False, indent=2))

    print("\n=== PROCTOR MODIFICADO ===")
    proctor = EnsayoProctor(
        id_muestra="M-01",
        tipo="MODIFICADO",
        puntos=[(8.0, 1.82), (10.0, 1.93), (12.0, 1.97), (14.0, 1.94), (16.0, 1.88)]
    )
    print(json.dumps(proctor.resumen(), ensure_ascii=False, indent=2))
    print("Verificación campo:", json.dumps(
        proctor.verificar_compactacion(densidad_campo_gcm3=1.88, porcentaje_minimo=95),
        ensure_ascii=False, indent=2
    ))

    print("\n=== CBR ===")
    cbr = EnsayoCBR(
        id_muestra="CBR-01",
        carga_254_kN=5.2,
        carga_508_kN=7.8,
        densidad_seca=1.90,
        humedad_pct=11.5,
    )
    print(json.dumps(cbr.resumen(), ensure_ascii=False, indent=2))
    print("Pavimento:", json.dumps(cbr.espesor_pavimento_cm(esal_millones=5.0), ensure_ascii=False, indent=2))
