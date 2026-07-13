"""
AquaAI — Generador de Memoria de Cálculo (PDF)
Referencia: Resolución 0330/2017 Art. 13 — Requisitos mínimos de documentación técnica

Genera un documento PDF profesional con:
  - Portada con datos del proyecto y prestador
  - Tabla de contenido
  - Una sección por módulo calculado (inputs + fórmulas + resultados + normas)
  - Tabla de advertencias y alertas regulatorias
  - Bloque de firma del ingeniero responsable

Uso:
  from .pdf_memoria import generar_memoria_pdf
  ruta = generar_memoria_pdf(request, resultados, ruta_salida)
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas as rl_canvas

# ─── Paleta AquaAI ───────────────────────────────────────────────────────────
AZUL_OSCURO   = colors.HexColor("#0D2B4E")   # header / títulos
AZUL_MEDIO    = colors.HexColor("#1565C0")   # subtítulos / líneas
AZUL_CLARO    = colors.HexColor("#E3F2FD")   # fondo celdas encabezado
GRIS_TABLA    = colors.HexColor("#F5F5F5")   # filas alternas
VERDE_OK      = colors.HexColor("#1B5E20")
ROJO_ALERTA   = colors.HexColor("#B71C1C")
NARANJA_ADV   = colors.HexColor("#E65100")
BLANCO        = colors.white
GRIS_LINEA    = colors.HexColor("#90A4AE")


# ─── Estilos ─────────────────────────────────────────────────────────────────

def _estilos():
    s = getSampleStyleSheet()
    base = dict(fontName="Helvetica", leading=14, spaceAfter=4)

    estilos = {
        "portada_titulo": ParagraphStyle("portada_titulo",
            fontName="Helvetica-Bold", fontSize=22, leading=28,
            textColor=AZUL_OSCURO, alignment=TA_CENTER, spaceAfter=6),
        "portada_sub": ParagraphStyle("portada_sub",
            fontName="Helvetica", fontSize=13, leading=18,
            textColor=AZUL_MEDIO, alignment=TA_CENTER, spaceAfter=4),
        "portada_dato": ParagraphStyle("portada_dato",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=colors.black, alignment=TA_CENTER, spaceAfter=3),
        "seccion": ParagraphStyle("seccion",
            fontName="Helvetica-Bold", fontSize=13, leading=18,
            textColor=AZUL_OSCURO, spaceBefore=14, spaceAfter=6,
            borderPad=4),
        "subseccion": ParagraphStyle("subseccion",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=AZUL_MEDIO, spaceBefore=8, spaceAfter=4),
        "normal": ParagraphStyle("normal",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=colors.black, spaceAfter=3, alignment=TA_JUSTIFY),
        "formula": ParagraphStyle("formula",
            fontName="Courier", fontSize=9, leading=13,
            textColor=AZUL_OSCURO, leftIndent=18, spaceAfter=3,
            backColor=colors.HexColor("#EEF2F7"), borderPad=4),
        "alerta": ParagraphStyle("alerta",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=ROJO_ALERTA, leftIndent=10, spaceAfter=2),
        "advertencia": ParagraphStyle("advertencia",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=NARANJA_ADV, leftIndent=10, spaceAfter=2),
        "norma": ParagraphStyle("norma",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=colors.HexColor("#455A64"), leftIndent=10, spaceAfter=2),
        "pie": ParagraphStyle("pie",
            fontName="Helvetica", fontSize=7, leading=10,
            textColor=GRIS_LINEA, alignment=TA_CENTER),
    }
    return estilos


# ─── Cabecera y pie de página ─────────────────────────────────────────────────

class _HeaderFooterCanvas(rl_canvas.Canvas):
    """Canvas personalizado que dibuja header/footer en cada página."""

    def __init__(self, *args, proyecto: str = "", prestador: str = "",
                 fecha: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto   = proyecto
        self.prestador  = prestador
        self.fecha      = fecha
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(n_pages)
            super().showPage()
        super().save()

    def _draw_header_footer(self, total_pages: int):
        self.saveState()
        w, h = letter

        # ── Header ────────────────────────────────────────────────────────────
        self.setFillColor(AZUL_OSCURO)
        self.rect(0, h - 1.8*cm, w, 1.8*cm, fill=1, stroke=0)

        self.setFillColor(BLANCO)
        self.setFont("Helvetica-Bold", 11)
        self.drawString(1.5*cm, h - 1.1*cm, "AquaAI")
        self.setFont("Helvetica", 8)
        self.drawString(1.5*cm, h - 1.55*cm, "Motor de Cálculo RAS 2000 / Res. 0330-2017")

        self.setFont("Helvetica", 8)
        self.drawRightString(w - 1.5*cm, h - 1.1*cm, self.prestador[:55])
        self.drawRightString(w - 1.5*cm, h - 1.55*cm, self.proyecto[:55])

        # ── Footer ────────────────────────────────────────────────────────────
        self.setStrokeColor(GRIS_LINEA)
        self.setLineWidth(0.5)
        self.line(1.5*cm, 1.8*cm, w - 1.5*cm, 1.8*cm)

        self.setFillColor(GRIS_LINEA)
        self.setFont("Helvetica", 7)
        self.drawString(1.5*cm, 1.2*cm,
            f"Generado por AquaAI | {self.fecha} | "
            "Este documento es una memoria técnica de apoyo. "
            "Debe ser revisada y firmada por un ingeniero habilitado.")
        pag_txt = f"Pág. {self._pageNumber} de {total_pages}"
        self.drawRightString(w - 1.5*cm, 1.2*cm, pag_txt)

        self.restoreState()


# ─── Helpers de tabla ────────────────────────────────────────────────────────

def _tabla_kv(filas: list[tuple[str, str]], e) -> Table:
    """Tabla clave-valor de dos columnas para parámetros de entrada/salida."""
    datos = [[Paragraph(f"<b>{k}</b>", e["normal"]),
              Paragraph(str(v), e["normal"])] for k, v in filas]
    t = Table(datos, colWidths=[6.5*cm, 11*cm])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), AZUL_CLARO),
        ("BACKGROUND", (1, 0), (1, -1), BLANCO),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANCO, GRIS_TABLA]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ])
    t.setStyle(ts)
    return t


def _tabla_resultados(encabezados: list[str], filas: list[list], e) -> Table:
    """Tabla de resultados con encabezado azul."""
    header = [Paragraph(f"<b>{h}</b>", ParagraphStyle("th",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=BLANCO,
        alignment=TA_CENTER)) for h in encabezados]
    data   = [header] + [[Paragraph(str(c), e["normal"]) for c in row]
                         for row in filas]
    col_w  = [17.5*cm / len(encabezados)] * len(encabezados)
    t = Table(data, colWidths=col_w, repeatRows=1)
    ts = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), AZUL_OSCURO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, GRIS_TABLA]),
        ("GRID",         (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
    ])
    t.setStyle(ts)
    return t


# ─── Secciones por módulo ─────────────────────────────────────────────────────

def _seccion_header(titulo: str, e) -> list:
    return [
        HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO, spaceAfter=2),
        Paragraph(titulo, e["seccion"]),
    ]


def _bloque_poblacion(datos: dict, e) -> list:
    story = _seccion_header("1. Proyección de Población", e)
    story.append(Paragraph(
        "Métodos: Aritmético, Geométrico (recomendado RAS) y Exponencial. "
        "La población de diseño corresponde al valor del método geométrico.",
        e["normal"]))
    story.append(Spacer(1, 6))
    filas = [
        ("Población censal (año base)", f"{datos.get('poblacion_censal', '—')} hab"),
        ("Tasa de crecimiento", f"{datos.get('tasa_crecimiento_pct', '—')} %/año"),
        ("Período de diseño", f"{datos.get('periodo_diseno_anos', '—')} años"),
        ("Año de diseño", str(datos.get('anio_diseno', '—'))),
        ("Población de diseño (geométrico)", f"{datos.get('poblacion_diseno', '—')} hab"),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Fórmula geométrica (RAS 2000 §B.2.2): "
        "Pd = Po × (1 + r)<super>t</super>", e["formula"]))
    normas = datos.get("normas_aplicadas", [])
    for n in normas:
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_caudales(datos: dict, e) -> list:
    story = _seccion_header("2. Dotación y Caudales de Diseño", e)
    story.append(Paragraph(
        "Dotación neta según nivel de complejidad y clima (RAS Tabla B.2.1). "
        "Factores de día máximo (Fmd) y hora máxima (Fmh) aplicados.",
        e["normal"]))
    story.append(Spacer(1, 6))
    filas = [
        ("Nivel de complejidad", datos.get("nivel_complejidad", "—")),
        ("Clima",                datos.get("clima_region", "—")),
        ("Dotación neta",       f"{datos.get('dotacion_neta_lhd', '—')} L/hab·día"),
        ("Pérdidas sistema",    f"{datos.get('perdidas_pct', '—')} %"),
        ("Dotación bruta",      f"{datos.get('dotacion_bruta_lhd', '—')} L/hab·día"),
        ("Caudal promedio Qp",  f"{datos.get('caudal_promedio_ls', '—')} L/s"),
        ("Caudal máx. diario Qmd",   f"{datos.get('caudal_max_diario_ls', '—')} L/s"),
        ("Caudal máx. horario Qmh",  f"{datos.get('caudal_max_horario_ls', '—')} L/s"),
        ("Caudal incendio Qci",      f"{datos.get('caudal_incendio_ls', '—')} L/s"),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Qmd = Qp × Fmd    |    Qmh = Qmd × Fmh", e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_hidraulica(datos: dict, e) -> list:
    story = _seccion_header("3. Hidráulica de Tuberías — Hazen-Williams", e)
    story.append(Paragraph(
        "Selección del diámetro nominal mínimo que satisface las restricciones de "
        "velocidad (0.45–5.0 m/s) y presión del RAS 2000 Título B Sección B.6.",
        e["normal"]))
    story.append(Spacer(1, 6))
    filas = [
        ("Caudal de diseño",    f"{datos.get('caudal_diseno_ls', '—')} L/s"),
        ("Material tubería",    datos.get("material", "—")),
        ("Coef. Hazen-Williams C", str(datos.get("coeficiente_c", "—"))),
        ("Longitud tramo",      f"{datos.get('longitud_m', '—')} m"),
        ("Pendiente hidráulica",f"{datos.get('pendiente_m_m', '—')} m/m"),
        ("Diámetro nominal",    f"{datos.get('diametro_nominal_mm', '—')} mm"),
        ("Velocidad calculada", f"{datos.get('velocidad_ms', '—')} m/s"),
        ("Pérdida de carga hf", f"{datos.get('perdida_carga_m', '—')} m"),
        ("Presión disponible",  f"{datos.get('presion_disponible_m', '—')} m.c.a."),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "hf = 10.67 × L × Q<super>1.852</super> / (C<super>1.852</super> × D<super>4.87</super>)",
        e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_hidrologia(datos: dict, e) -> list:
    story = _seccion_header("4. Hidrología — Caudal de Diseño (Método Racional)", e)
    story.append(Paragraph(
        "Tiempo de concentración por Kirpich/Témez. "
        "Intensidad IDF regional calibrada por zona climática IDEAM.",
        e["normal"]))
    story.append(Spacer(1, 6))
    filas = [
        ("Área de drenaje",         f"{datos.get('area_ha', '—')} ha"),
        ("Coef. escorrentía C",     str(datos.get("coeficiente_c", "—"))),
        ("Período de retorno",      f"{datos.get('periodo_retorno_anos', '—')} años"),
        ("Región IDF",              datos.get("region_idf", "—")),
        ("Tiempo concentración Tc", f"{datos.get('tc_min', '—')} min"),
        ("Intensidad I (IDF)",      f"{datos.get('intensidad_mm_h', '—')} mm/h"),
        ("Caudal de diseño Q",      f"{datos.get('caudal_diseno_m3s', '—')} m³/s"),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Q = C × I × A / 360    [m³/s]    |    I = a / (Tc<super>n</super> + b)    [mm/h]",
        e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_ptap(datos: dict, e) -> list:
    story = _seccion_header("5. Planta de Tratamiento de Agua Potable (PTAP)", e)
    story.append(Paragraph(
        f"Caudal de diseño: {datos.get('caudal_diseno_ls', '—')} L/s. "
        f"Coagulante: {datos.get('coagulante', '—')}. "
        f"Turbidez cruda: {datos.get('turbidez_ntu', '—')} NTU.",
        e["normal"]))
    story.append(Spacer(1, 6))

    unidades = datos.get("unidades", [])
    if unidades:
        encabezados = ["Unidad", "Parámetro clave", "Dimensión", "Norma"]
        filas_t = []
        for u in unidades:
            dims = u.get("dimensiones", {})
            dim_str = " | ".join(f"{k}: {v}" for k, v in list(dims.items())[:2])
            params  = u.get("parametros_diseno", {})
            param_str = " | ".join(f"{k}: {v}" for k, v in list(params.items())[:2])
            filas_t.append([
                u.get("nombre", "")[:35],
                param_str[:50],
                dim_str[:50],
                u.get("norma_ref", "")[:40],
            ])
        story.append(_tabla_resultados(encabezados, filas_t, e))
    story.append(Spacer(1, 5))
    filas = [
        ("Dosis coagulante",    f"{datos.get('dosis_coagulante_mg_l', '—')} mg/L"),
        ("Consumo coagulante",  f"{datos.get('consumo_coagulante_kg_dia', '—')} kg/día"),
        ("CT Giardia 3-log",    f"{datos.get('ct_requerido_mg_min_l', '—')} mg·min/L"),
        ("Dosis cloro",         f"{datos.get('dosis_cloro_mg_l', '—')} mg/L"),
        ("Cloro residual red",  "0.2 – 1.0 mg/L (Res 2115/2007)"),
        ("Cumple Res 2115/2007",str(datos.get("cumple_res2115", "—"))),
    ]
    story.append(_tabla_kv(filas, e))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_ptar(datos: dict, e) -> list:
    story = _seccion_header("6. Planta de Tratamiento de Aguas Residuales (PTAR)", e)
    story.append(Spacer(1, 4))
    filas = [
        ("Caudal AR de diseño",     f"{datos.get('caudal_ar_ls', '—')} L/s  ({datos.get('caudal_ar_m3_dia', '—')} m³/día)"),
        ("DBO₅ cruda",              f"{datos.get('dbo5_cruda_mg_l', '—')} mg/L"),
        ("SST crudo",               f"{datos.get('sst_crudo_mg_l', '—')} mg/L"),
        ("Carga DBO",               f"{datos.get('carga_dbo_kg_dia', '—')} kg/día"),
        ("Tecnología seleccionada", datos.get("tecnologia", "—")),
        ("Eficiencia remoción DBO", f"{datos.get('eficiencia_dbo_pct', '—')} %"),
        ("DBO efluente",            f"{datos.get('dbo_efluente_mg_l', '—')} mg/L"),
        ("Límite Res 0631/2015",    f"{datos.get('limite_res0631_dbo', '—')} mg/L"),
        ("Cumple Res 0631/2015",    str(datos.get("cumple_res0631", "—"))),
        ("Producción de lodos",     f"{datos.get('lodos_kg_dia', '—')} kg SST/día"),
    ]
    story.append(_tabla_kv(filas, e))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_manning(datos: dict, e) -> list:
    story = _seccion_header("7. Alcantarillado a Gravedad — Manning", e)
    story.append(Spacer(1, 4))
    filas = [
        ("Caudal de diseño",      f"{datos.get('caudal_diseno_ls', '—')} L/s"),
        ("Pendiente longitudinal",f"{datos.get('pendiente_mm', '—')} ‰"),
        ("Material",              datos.get("material", "—")),
        ("Coef. Manning n",       str(datos.get("n_manning", "—"))),
        ("Diámetro nominal",      f"{datos.get('diametro_nominal_mm', '—')} mm"),
        ("Q a sección llena Qf",  f"{datos.get('qf_ls', '—')} L/s"),
        ("Relación Q/Qf",         str(datos.get("q_qf", "—"))),
        ("Tirante d/D",           str(datos.get("d_D", "—"))),
        ("Velocidad real",        f"{datos.get('velocidad_ms', '—')} m/s"),
        ("Pendiente mínima",      f"{datos.get('pendiente_min_mm', '—')} ‰"),
        ("Cumple autolimpieza",   str(datos.get("cumple_v_min", "—"))),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "V = (1/n) × R<super>2/3</super> × S<super>1/2</super>    "
        "|    Q = V × A(θ)    |    d/D = (1 − cos(θ/2)) / 2",
        e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_ariete(datos: dict, e) -> list:
    story = _seccion_header("8. Golpe de Ariete — Transitorio Hidráulico", e)
    story.append(Spacer(1, 4))
    filas = [
        ("Caudal",                  f"{datos.get('caudal_ls', '—')} L/s"),
        ("Diámetro interno",        f"{datos.get('diametro_mm', '—')} mm"),
        ("Longitud línea",          f"{datos.get('longitud_m', '—')} m"),
        ("Velocidad flujo",         f"{datos.get('velocidad_ms', '—')} m/s"),
        ("Celeridad onda a",        f"{datos.get('celeridad_ms', '—')} m/s"),
        ("Tiempo crítico Tc",       f"{datos.get('tc_s', '—')} s"),
        ("Tiempo de cierre",        f"{datos.get('t_cierre_s', '—')} s"),
        ("Tipo de cierre",          "RÁPIDO ⚠" if datos.get("cierre_rapido") else "Lento ✓"),
        ("ΔH sobrepresión",         f"{datos.get('delta_h_m', '—')} m.c.a."),
        ("Presión máxima total",    f"{datos.get('h_max_m', '—')} m.c.a."),
        ("Presión mínima",          f"{datos.get('h_min_m', '—')} m.c.a."),
        ("Clase PN recomendada",    datos.get("clase_pn", "—")),
        ("Riesgo de cavitación",    "SÍ ⚠" if datos.get("riesgo_cavitacion") else "No"),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "ΔH = a × ΔV / g    (Joukowski)    |    "
        "a = √(K/ρ) / √(1 + K·D/(E·e))    |    Tc = 2L/a",
        e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_bombeo(datos: dict, e) -> list:
    story = _seccion_header("9. Estación de Bombeo", e)
    story.append(Spacer(1, 4))
    filas = [
        ("Caudal de diseño",          f"{datos.get('caudal_ls', '—')} L/s"),
        ("Altura geométrica Hg",      f"{datos.get('altura_geometrica_m', '—')} m"),
        ("Pérdidas totales hf",       f"{datos.get('perdidas_totales_m', '—')} m"),
        ("TDH total",                 f"{datos.get('tdh_m', '—')} m"),
        ("Potencia hidráulica",       f"{datos.get('p_hidraulica_kw', '—')} kW"),
        ("Potencia al freno",         f"{datos.get('p_freno_kw', '—')} kW"),
        ("Potencia instalada (motor)",f"{datos.get('p_instalada_kw', '—')} kW"),
        ("Consumo estimado",          f"{datos.get('consumo_kwh_mes', '—')} kWh/mes"),
        ("NPSHd disponible",          f"{datos.get('npshd_m', '—')} m"),
        ("Alerta cavitación",         "SÍ ⚠" if datos.get("alerta_cavitacion") else "No"),
        ("Configuración",             datos.get("configuracion", "—")),
    ]
    story.append(_tabla_kv(filas, e))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "TDH = Hg + hf_suc + hf_imp + hf_men    |    "
        "P_hid = ρ·g·Q·TDH    |    P_inst = P_freno / η_motor × 1.15",
        e["formula"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_tarifas(datos: dict, e) -> list:
    story = _seccion_header("10. Estructura Tarifaria CRA", e)
    story.append(Spacer(1, 4))
    filas_enc = [
        ("Tipo de prestador",    datos.get("tipo_prestador", "—")),
        ("Metodología CRA",      datos.get("metodologia_cra", "—")),
        ("Clima (consumo básico)",datos.get("clima", "—")),
        ("CMLP (costo marginal)",f"$ {datos.get('cmlp', '—'):.0f} /m³" if isinstance(datos.get('cmlp'), (int,float)) else "—"),
        ("Cargo fijo",           f"$ {datos.get('cargo_fijo', '—'):.0f} /suscriptor/mes" if isinstance(datos.get('cargo_fijo'), (int,float)) else "—"),
    ]
    story.append(_tabla_kv(filas_enc, e))
    tarifas_estratos = datos.get("tarifas_estratos", [])
    if tarifas_estratos:
        story.append(Spacer(1, 5))
        encabezados = ["Estrato/Uso", "Tipo", "Factor", "CC Básico ($/m³)", "CC Compl. ($/m³)", "CC Sunt. ($/m³)"]
        filas_t = []
        for t in tarifas_estratos:
            filas_t.append([
                t.get("estrato", ""),
                t.get("tipo", ""),
                t.get("factor", ""),
                f"$ {t.get('cc_basico', 0):,.0f}" if isinstance(t.get('cc_basico'), (int,float)) else "—",
                f"$ {t.get('cc_complementario', 0):,.0f}" if isinstance(t.get('cc_complementario'), (int,float)) else "—",
                f"$ {t.get('cc_suntuario', 0):,.0f}" if isinstance(t.get('cc_suntuario'), (int,float)) else "—",
            ])
        story.append(_tabla_resultados(encabezados, filas_t, e))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


def _bloque_sui(datos: dict, e) -> list:
    story = _seccion_header("11. Indicadores SUI — Reporte Regulatorio", e)
    story.append(Spacer(1, 4))
    filas = [
        ("Período",               datos.get("periodo", "—")),
        ("Suscriptores totales",  str(datos.get("suscriptores", "—"))),
        ("Volumen producido",     f"{datos.get('vol_producido_m3', '—')} m³/mes"),
        ("Volumen facturado",     f"{datos.get('vol_facturado_m3', '—')} m³/mes"),
        ("IANC",                  f"{datos.get('ianc_pct', '—')} %  {'⚠ ALERTA' if float(datos.get('ianc_pct', 0) or 0) > 25 else '✓'}"),
        ("IRCA",                  f"{datos.get('irca', '—')}  — {datos.get('irca_categoria', '—')}"),
        ("Muestras conformes",    f"{datos.get('muestras_pct', '—')} %"),
        ("Recaudo $/m³",          f"$ {datos.get('recaudo_m3', '—'):.0f}" if isinstance(datos.get('recaudo_m3'), (int,float)) else "—"),
    ]
    story.append(_tabla_kv(filas, e))
    alertas = datos.get("alertas_regulatorias", [])
    if alertas:
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Alertas regulatorias:</b>", e["subseccion"]))
        for a in alertas:
            story.append(Paragraph(f"⚠ {a}", e["alerta"]))
    for n in datos.get("normas_aplicadas", []):
        story.append(Paragraph(f"▸ {n}", e["norma"]))
    return story


# ─── Sección advertencias globales ───────────────────────────────────────────

def _bloque_advertencias(advertencias: list[str], e) -> list:
    if not advertencias:
        return []
    story = _seccion_header("Advertencias Técnicas y Regulatorias", e)
    story.append(Paragraph(
        "Las siguientes advertencias fueron generadas automáticamente por el motor "
        "AquaAI durante los cálculos. Deben ser evaluadas por el ingeniero responsable.",
        e["normal"]))
    story.append(Spacer(1, 6))
    for adv in advertencias:
        estilo = e["alerta"] if "⚠" in adv else e["advertencia"]
        story.append(Paragraph(f"• {adv}", estilo))
    return story


# ─── Bloque de firma ─────────────────────────────────────────────────────────

def _bloque_firma(ingeniero: dict, e) -> list:
    story = [PageBreak()]
    story += _seccion_header("Firma y Responsabilidad Técnica", e)
    story.append(Paragraph(
        "Esta memoria de cálculo fue elaborada con el apoyo de AquaAI. "
        "El ingeniero firmante certifica haber revisado los resultados, "
        "verificado los datos de entrada y validado el cumplimiento normativo. "
        "La responsabilidad técnica y legal recae exclusivamente en el profesional habilitado.",
        e["normal"]))
    story.append(Spacer(1, 30))

    firma_data = [
        ["", ""],
        [
            Paragraph("_" * 40, e["normal"]),
            Paragraph("_" * 40, e["normal"]),
        ],
        [
            Paragraph(f"<b>{ingeniero.get('nombre', 'Nombre del Ingeniero')}</b>", e["normal"]),
            Paragraph(f"<b>{ingeniero.get('empresa', 'Razón Social del Prestador')}</b>", e["normal"]),
        ],
        [
            Paragraph(f"Matrícula profesional: {ingeniero.get('matricula', '________')}", e["normal"]),
            Paragraph(f"NIT / Código SUI: {ingeniero.get('nit', '________')}", e["normal"]),
        ],
        [
            Paragraph(f"Fecha: {ingeniero.get('fecha', '__ / __ / ____')}", e["normal"]),
            Paragraph("Ciudad y fecha: ______________________", e["normal"]),
        ],
    ]
    t = Table(firma_data, colWidths=[8.5*cm, 9*cm])
    t.setStyle(TableStyle([
        ("VALIGN",  (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Documento generado por AquaAI — Motor de Cálculo RAS 2000 / Resolución 0330/2017. "
        "Versión 2.0. Para soporte técnico: aquaai@aquaai.co",
        e["pie"]))
    return story


# ─── Portada ─────────────────────────────────────────────────────────────────

def _portada(meta: dict, e) -> list:
    story = []
    story.append(Spacer(1, 2.5*cm))

    # Línea decorativa superior
    story.append(HRFlowable(width="100%", thickness=3, color=AZUL_OSCURO))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("MEMORIA DE CÁLCULO", e["portada_titulo"]))
    story.append(Paragraph("Sistema de Agua Potable y Saneamiento Básico", e["portada_sub"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=AZUL_MEDIO))
    story.append(Spacer(1, 1.5*cm))

    # Datos del proyecto
    portada_data = [
        ["PROYECTO",   meta.get("nombre_proyecto", "—")],
        ["PRESTADOR",  meta.get("nombre_prestador", "—")],
        ["MUNICIPIO",  meta.get("municipio", "—")],
        ["DEPARTAMENTO", meta.get("departamento", "—")],
        ["CÓDIGO DANE", meta.get("codigo_dane", "—")],
        ["ELABORÓ",    meta.get("ingeniero_nombre", "—")],
        ["FECHA",      meta.get("fecha_generacion", datetime.today().strftime("%d/%m/%Y"))],
        ["VERSIÓN",    meta.get("version", "1.0")],
    ]

    t = Table(portada_data, colWidths=[5*cm, 12.5*cm])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), AZUL_OSCURO),
        ("TEXTCOLOR",  (0, 0), (0, -1), BLANCO),
        ("BACKGROUND", (1, 0), (1, -1), BLANCO),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [BLANCO, AZUL_CLARO]),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",   (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("GRID",       (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("LEFTPADDING",(0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ])
    t.setStyle(ts)
    story.append(t)

    story.append(Spacer(1, 2*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=AZUL_MEDIO))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Generado con AquaAI — Motor de Cálculo RAS 2000 / Resolución 0330/2017",
        e["portada_dato"]))
    story.append(Paragraph(
        "Este documento es una memoria técnica de apoyo. "
        "Debe ser revisado y firmado por un ingeniero habilitado ante el COPNIA.",
        ParagraphStyle("aviso", fontName="Helvetica-Oblique", fontSize=8,
                       textColor=ROJO_ALERTA, alignment=TA_CENTER, spaceAfter=4)))
    story.append(PageBreak())
    return story


# ─── Función principal ────────────────────────────────────────────────────────

def generar_memoria_pdf(
    meta: dict,
    modulos: dict,
    ruta_salida: str,
    ingeniero: Optional[dict] = None,
) -> str:
    """
    Genera la memoria de cálculo en PDF.

    Parámetros:
        meta: datos del proyecto (nombre_proyecto, nombre_prestador, municipio, etc.)
        modulos: dict con resultados de cada módulo calculado. Claves posibles:
            "poblacion", "caudales", "hidraulica", "hidrologia",
            "ptap", "ptar", "manning", "ariete", "bombeo", "tarifas", "sui"
        ruta_salida: ruta del archivo PDF a generar
        ingeniero: datos del profesional firmante

    Retorna:
        ruta absoluta del PDF generado
    """
    if ingeniero is None:
        ingeniero = {}

    e = _estilos()
    fecha_str = datetime.today().strftime("%d/%m/%Y %H:%M")
    meta.setdefault("fecha_generacion", fecha_str)

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.5*cm,  bottomMargin=2.5*cm,
        title=f"Memoria de Cálculo — {meta.get('nombre_proyecto', 'AquaAI')}",
        author="AquaAI Motor de Cálculo",
        subject="Memoria técnica sistema acueducto y saneamiento — Colombia",
    )

    story = []

    # Portada
    story += _portada(meta, e)

    # Módulos presentes
    BLOQUES = {
        "poblacion":  _bloque_poblacion,
        "caudales":   _bloque_caudales,
        "hidraulica": _bloque_hidraulica,
        "hidrologia": _bloque_hidrologia,
        "ptap":       _bloque_ptap,
        "ptar":       _bloque_ptar,
        "manning":    _bloque_manning,
        "ariete":     _bloque_ariete,
        "bombeo":     _bloque_bombeo,
        "tarifas":    _bloque_tarifas,
        "sui":        _bloque_sui,
    }

    todas_advertencias: list[str] = []
    n_sec = 0
    for clave, fn in BLOQUES.items():
        if clave in modulos and modulos[clave]:
            n_sec += 1
            bloque = fn(modulos[clave], e)
            story += bloque
            story.append(Spacer(1, 8))
            todas_advertencias += modulos[clave].get("advertencias", [])

    # Sección advertencias
    if todas_advertencias:
        story.append(PageBreak())
        story += _bloque_advertencias(todas_advertencias, e)

    # Firma
    story += _bloque_firma(ingeniero, e)

    # Build con canvas personalizado
    def make_canvas(filename, **kw):
        return _HeaderFooterCanvas(
            filename,
            proyecto=meta.get("nombre_proyecto", "AquaAI"),
            prestador=meta.get("nombre_prestador", ""),
            fecha=meta.get("fecha_generacion", ""),
            **kw,
        )

    doc.build(story, canvasmaker=make_canvas)
    return os.path.abspath(ruta_salida)
