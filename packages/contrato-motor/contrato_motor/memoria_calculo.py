"""Memoria de cálculo legible por máquina (#275, F0). Esquema versionado común a todos los motores.

La memoria es a la vez evidencia técnica (cada línea dice de dónde sale) y una fila del corpus de entrenamiento
(`caracteristicas`: entradas y salidas planas para modelos subrogados). Secciones:
  datos_entrada → cargas → modelacion (análisis) → diseno (elementos y verificaciones) → cantidades → no_verifica.
Estados de cada línea:
  "ENTRADA"         dato del usuario o del proyecto;
  "NSR-10 (leído)"  numeral leído en el corpus nsr10_chunks;
  "CALCULADO"       resultado del motor con una ecuación declarada;
  "HIPÓTESIS"       supuesto de modelación o método que la norma no fija (o que no se leyó en el corpus).
La memoria NO reemplaza la firma de un ingeniero responsable (#18; Ley 400 de 1997).
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from . import AVISO_RESPONSABILIDAD

VERSION_ESQUEMA = "structai.memoria_calculo/0.1"
Estado = Literal["ENTRADA", "NSR-10 (leído)", "CALCULADO", "HIPÓTESIS"]


class Linea(BaseModel):
    concepto: str
    valor: Any
    unidad: str = ""
    referencia: str = ""
    estado: Estado
    ecuacion: str = ""


class Verificacion(BaseModel):
    nombre: str
    demanda: float
    capacidad: float
    unidad: str
    cumple: bool
    referencia: str
    nota: str = ""

    @property
    def razon(self) -> float:
        return self.demanda / self.capacidad if self.capacidad else float("inf")


class ElementoDisenado(BaseModel):
    grupo: str                         # p. ej. "Vigas nivel 3", "Columnas piso 1"
    tipo: Literal["viga", "columna", "zapata", "muro", "losa", "otro"]
    cantidad: int = Field(ge=1)
    seccion: str                       # "300×500 mm"
    refuerzo: dict[str, Any]
    verificaciones: list[Verificacion]
    demandas: dict[str, float] = Field(default_factory=dict)

    @property
    def cumple(self) -> bool:
        return all(v.cumple for v in self.verificaciones)


class Cantidades(BaseModel):
    concreto_m3: float
    acero_kg: float
    encofrado_m2: float
    costo_cop: float
    co2_kg: float
    area_construida_m2: float
    fuente_precios: str
    fecha_precios: Optional[str] = None

    @property
    def por_m2(self) -> dict[str, float]:
        a = self.area_construida_m2
        return {"concreto_m3_m2": self.concreto_m3 / a, "acero_kg_m2": self.acero_kg / a,
                "costo_cop_m2": self.costo_cop / a, "co2_kg_m2": self.co2_kg / a}


class MemoriaCalculo(BaseModel):
    esquema: str = VERSION_ESQUEMA
    generado: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    motor: str
    aviso: str = AVISO_RESPONSABILIDAD
    proyecto: dict[str, Any]           # nombre, tipología, uso, DIVIPOLA (nunca coordenadas exactas), sistema
    datos_entrada: list[Linea]
    cargas: list[Linea]
    modelacion: list[Linea]
    resultados_analisis: dict[str, Any]
    diseno: list[ElementoDisenado]
    cantidades: Optional[Cantidades] = None
    no_verifica: list[str]
    advertencias: list[str] = Field(default_factory=list)
    caracteristicas: dict[str, float | int | str | bool | None] = Field(default_factory=dict)

    @field_validator("no_verifica")
    @classmethod
    def _declarar_limites(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Toda memoria debe declarar lo que el motor NO verifica")
        return v

    @property
    def cumple(self) -> bool:
        return all(e.cumple for e in self.diseno) and bool(self.resultados_analisis.get("cumple_deriva", True))

    def a_json(self) -> str:
        d = self.model_dump()
        d["cumple"] = self.cumple
        if self.cantidades is not None:
            d["cantidades"]["por_m2"] = self.cantidades.por_m2
        return json.dumps(d, ensure_ascii=False, indent=1)

    def a_html(self) -> str:
        """Vista legible para imprimir. Todo el texto se escapa (los nombres vienen del usuario)."""
        e = html.escape

        def tabla_lineas(titulo, lineas):
            filas = "".join(f"<tr><td>{e(l.concepto)}</td><td>{e(_fmt(l.valor))} {e(l.unidad)}</td><td>{e(l.ecuacion)}</td>"
                            f"<td>{e(l.referencia)}</td><td class='est'>{e(l.estado)}</td></tr>" for l in lineas)
            return (f"<h2>{e(titulo)}</h2><table><tr><th>Concepto</th><th>Valor</th><th>Ecuación</th><th>Referencia</th>"
                    f"<th>Estado</th></tr>{filas}</table>")

        partes = [f"<h1>Memoria de cálculo: {e(str(self.proyecto.get('nombre', '')))}</h1>",
                  f"<p class='aviso'>{e(self.aviso)}</p>",
                  f"<p>Esquema {e(self.esquema)} · motor {e(self.motor)} · {e(self.generado)} · "
                  f"<b>{'CUMPLE' if self.cumple else 'NO CUMPLE'}</b></p>",
                  tabla_lineas("1. Datos de entrada", self.datos_entrada),
                  tabla_lineas("2. Cargas", self.cargas),
                  tabla_lineas("3. Modelación y análisis", self.modelacion)]
        partes.append("<h2>4. Diseño de elementos</h2>")
        for el in self.diseno:
            filas = "".join(f"<tr><td>{e(v.nombre)}</td><td>{v.demanda:.4g}</td><td>{v.capacidad:.4g}</td><td>{e(v.unidad)}</td>"
                            f"<td>{'sí' if v.cumple else '<b>NO</b>'}</td><td>{e(v.referencia)}</td><td>{e(v.nota)}</td></tr>"
                            for v in el.verificaciones)
            partes.append(f"<h3>{e(el.grupo)} ({el.cantidad} × {e(el.seccion)})</h3><p>Refuerzo: {e(_fmt(el.refuerzo))}</p>"
                          f"<table><tr><th>Verificación</th><th>Demanda</th><th>Capacidad</th><th>Unidad</th><th>Cumple</th>"
                          f"<th>Numeral</th><th>Nota</th></tr>{filas}</table>")
        if self.cantidades is not None:
            c, pm = self.cantidades, self.cantidades.por_m2
            partes.append(f"<h2>5. Cantidades y costo</h2><p>Concreto {c.concreto_m3:.1f} m³ · acero {c.acero_kg:,.0f} kg · "
                          f"encofrado {c.encofrado_m2:,.0f} m² · costo directo {c.costo_cop:,.0f} COP · {c.co2_kg:,.0f} kg CO₂e</p>"
                          f"<p>Por m² construido ({c.area_construida_m2:,.0f} m²): {pm['concreto_m3_m2']:.3f} m³ · "
                          f"{pm['acero_kg_m2']:.1f} kg · {pm['costo_cop_m2']:,.0f} COP · {pm['co2_kg_m2']:.1f} kg CO₂e. "
                          f"Precios: {e(c.fuente_precios)}</p>")
        partes.append("<h2>6. Lo que este cálculo NO verifica</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in self.no_verifica) + "</ul>")
        if self.advertencias:
            partes.append("<h2>Advertencias</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in self.advertencias) + "</ul>")
        estilo = ("body{font-family:system-ui,sans-serif;max-width:1100px;margin:auto;padding:16px;color:#1a1a1a}"
                  "table{border-collapse:collapse;width:100%;font-size:13px;margin-bottom:12px}"
                  "td,th{border:1px solid #ccc;padding:4px 6px;text-align:left;vertical-align:top}"
                  ".aviso{background:#fff4d6;padding:8px;border-left:4px solid #c90}.est{white-space:nowrap}")
        return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Memoria de cálculo</title>"
                f"<style>{estilo}</style></head><body>{''.join(partes)}</body></html>")


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    if isinstance(v, (dict, list, tuple)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)
