"""
StructAI — Carga de la Base Maestra de Precios APU Barranquilla/Atlántico a Supabase.

Fuente: raw/Base_Maestra_Precios_Barranquilla.xlsx — construida por el usuario con
Cowork (investigación de mercado + PDFs de Construdata + archivos reales de proyectos
ejecutados en Triple A/Puerto Colombia + INVIAS regional Atlántico). Ver la hoja
"Resumen" del propio libro para la metodología completa (Rondas 1-5).

Tablas destino (aditivas — no tocan nsr10_chunks/motor_chunks/apu_calculations/catalogue.py):
  - apu_precios_referencia   : precio a nivel de actividad completa
  - apu_insumos_referencia   : desglose insumo por insumo (material/mano de obra/equipo/transporte)
  - apu_proveedores_catalogo : catálogo de ferretería con proveedor/URL/precio verificado

Uso: python cargar_apu_barranquilla.py [--dry-run]
"""
import os
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_XLSX = Path(__file__).resolve().parent / "raw" / "Base_Maestra_Precios_Barranquilla.xlsx"

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

import openpyxl


def _fecha(v):
    """Normaliza fecha (str 'YYYY-MM-DD', date, o datetime) a date ISO string, o None."""
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.date().isoformat() if isinstance(v, datetime) else v.isoformat()
    s = str(v).strip()
    return s or None


def _num(v):
    """None-safe float; deja pasar None y castea numéricos."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _rows(ws, start_row=2):
    """Filas no vacías desde start_row (1-indexed), como tuplas de valores."""
    for r in ws.iter_rows(min_row=start_row, values_only=True):
        if any(c is not None for c in r):
            yield r


def cargar_actividades_construdata(ws) -> list[dict]:
    """APU_Actividades_Barranquilla — 1.115 actividades, catálogo Construdata."""
    filas = []
    for r in _rows(ws):
        if r[0] is None or r[3] is None:
            continue
        confiable = bool(r[11]) and str(r[11]).strip().lower().startswith("s")
        filas.append({
            "actividad": str(r[0]).strip(),
            "unidad": r[1],
            "disciplina": r[2],
            "precio_todo_costo": _num(r[3]),
            "costo_materiales": _num(r[4]),
            "costo_mano_obra": _num(r[5]),
            "costo_equipo": _num(r[6]),
            "precio_solo_mano_obra": _num(r[10]),
            "desglose_confiable": confiable,
            "precio_bogota": _num(r[12]),
            "precio_cali": _num(r[13]),
            "precio_medellin": _num(r[14]),
            "categoria_fuente": r[15],
            "region": "Barranquilla",
            "tipo_fuente": "catalogo_construdata",
            "fuente": r[16] or "Construdata (editorial Legis)",
            "fecha_captura": _fecha(r[17]),
        })
    return filas


def cargar_insumos_construdata(ws) -> list[dict]:
    """APU_Insumos_Detalle_BQ — ~7.200 líneas de insumo, catálogo Construdata."""
    filas = []
    for r in _rows(ws):
        if r[3] is None:
            continue
        filas.append({
            "actividad_padre_texto": (str(r[0]).strip() if r[0] else None),
            "disciplina": r[1],
            "tipo_insumo": r[2],
            "insumo": str(r[3]).strip(),
            "unidad": r[4],
            "cantidad": _num(r[5]),
            "valor_unitario": _num(r[6]),
            "valor_unitario_bogota": _num(r[7]),
            "valor_unitario_cali": _num(r[8]),
            "valor_unitario_medellin": _num(r[9]),
            "region": "Barranquilla",
            "tipo_fuente": "catalogo_construdata",
            "fuente": r[11] or "Construdata (editorial Legis)",
            "fecha_captura": _fecha(r[12]),
        })
    return filas


def cargar_infraestructura_aa(ws) -> list[dict]:
    """APU_Infraestructura_AA_BQ — 892 ítems reales, contrato ejecutado acueducto/alcantarillado."""
    filas = []
    for r in _rows(ws):
        if r[4] is None or r[6] is None:
            continue
        filas.append({
            "actividad": str(r[4]).strip(),
            "unidad": r[5],
            "disciplina": r[10],
            "precio_todo_costo": _num(r[6]),
            "desglose_confiable": False,
            "item_codigo": r[1],
            "region": "Barranquilla",
            "categoria_fuente": r[2],
            "tipo_fuente": "contrato_real_infraestructura_aa",
            "fuente": r[7] or "Contrato real acueducto/alcantarillado Barranquilla y Atlántico (Triple A)",
            "fecha_captura": _fecha(r[8]),
        })
    return filas


def cargar_pto_colombia(ws) -> tuple[list[dict], list[dict]]:
    """APU_Reales_PtoColombia — 9 APUs reales (Puerto Colombia), insumo + agregado por actividad."""
    insumos = []
    totales_por_actividad: dict[str, dict] = {}
    for r in _rows(ws):
        if r[0] is None or r[1] is None:
            continue
        item_apu = str(r[0]).strip()
        valor_total = _num(r[5])
        insumos.append({
            "actividad_padre_texto": item_apu,
            "tipo_insumo": "Material" if str(r[1]).strip().upper() not in ("MANO DE OBRA",) else "Mano de Obra",
            "insumo": str(r[1]).strip(),
            "unidad": r[2],
            "cantidad": _num(r[3]),
            "valor_unitario": _num(r[4]),
            "region": "Puerto Colombia",
            "tipo_fuente": "contrato_real_pto_colombia",
            "fuente": r[8] or "Proyecto real Puerto Colombia — Triple A (APU,S PTO COLOMBIA.xlsx)",
            "fecha_captura": date.today().isoformat(),
        })
        if valor_total is not None:
            acc = totales_por_actividad.setdefault(item_apu, {"suma": 0.0, "fuente": r[8]})
            acc["suma"] += valor_total
    actividades = []
    for actividad, acc in totales_por_actividad.items():
        actividades.append({
            "actividad": actividad,
            "unidad": None,
            "disciplina": "Estructuras / Obra civil",
            "precio_todo_costo": round(acc["suma"], 2),
            "desglose_confiable": True,
            "region": "Puerto Colombia",
            "categoria_fuente": "APU real Puerto Colombia",
            "tipo_fuente": "contrato_real_pto_colombia",
            "fuente": (acc["fuente"] or "Proyecto real Puerto Colombia — Triple A") +
                      " — precio_todo_costo = suma de insumos extraídos (puede no incluir todas las líneas de transporte/equipo del APU original)",
            "fecha_captura": date.today().isoformat(),
        })
    return actividades, insumos


def cargar_triple_a_acometidas(ws) -> tuple[list[dict], list[dict]]:
    """APU_Reales_TripleA_Acometidas — 319 líneas, 16 tipos de acometida de acueducto."""
    insumos = []
    totales: dict[str, dict] = {}
    for r in _rows(ws):
        if r[1] is None or r[3] is None:
            continue
        actividad = str(r[1]).strip()
        subtotal = _num(r[7])
        insumos.append({
            "actividad_padre_texto": actividad,
            "tipo_insumo": r[2],
            "insumo": str(r[3]).strip(),
            "unidad": r[4],
            "cantidad": _num(r[6]),
            "valor_unitario": _num(r[5]),
            "region": "Barranquilla",
            "tipo_fuente": "contrato_real_triple_a_acometidas",
            "fuente": r[8] or "Proyecto real acometidas acueducto Triple A (APU 08-11-17.xlsx)",
            "fecha_captura": date.today().isoformat(),
        })
        if subtotal is not None:
            acc = totales.setdefault(actividad, {"suma": 0.0, "fuente": r[8]})
            acc["suma"] += subtotal
    actividades = []
    for actividad, acc in totales.items():
        actividades.append({
            "actividad": actividad,
            "unidad": "Un",
            "disciplina": "Hidráulica y Sanitaria",
            "precio_todo_costo": round(acc["suma"], 2),
            "desglose_confiable": True,
            "region": "Barranquilla",
            "categoria_fuente": "Acometida de acueducto (Triple A)",
            "tipo_fuente": "contrato_real_triple_a_acometidas",
            "fuente": acc["fuente"] or "Proyecto real acometidas acueducto Triple A (APU 08-11-17.xlsx)",
            "fecha_captura": date.today().isoformat(),
        })
    return actividades, insumos


def cargar_mano_obra_atlantico(ws) -> list[dict]:
    """Mano_Obra_Atlantico_2026 — presupuesto real de MO por actividad, sección desde fila 22 (1-indexed)."""
    filas = []
    for r in _rows(ws, start_row=22):
        if r[1] is None or r[7] is None:
            continue
        filas.append({
            "actividad": str(r[1]).strip(),
            "unidad": r[2],
            "disciplina": "Hidráulica y Sanitaria",
            "precio_solo_mano_obra": _num(r[7]),
            "desglose_confiable": True,
            "region": "Atlántico",
            "categoria_fuente": r[0] or "Mano de obra plomería/hidráulica",
            "tipo_fuente": "contrato_real_mano_obra_atlantico",
            "fuente": "Proyecto real Atlántico — presupuesto MO 2026 (PRESUPUESTO_MO_FORMULAS_ATL_2026.xlsx)",
            "fecha_captura": date.today().isoformat(),
        })
    return filas


def cargar_invias(ws, tipo_insumo: str, col_insumo: int, col_valor: int, col_region: int) -> list[dict]:
    """Genérico para las 3 hojas INVIAS_*_Atlantico (materiales/mano de obra/equipo)."""
    filas = []
    for r in _rows(ws):
        if r[col_insumo] is None:
            continue
        filas.append({
            "actividad_padre_texto": None,
            "tipo_insumo": tipo_insumo,
            "insumo": str(r[col_insumo]).strip(),
            "unidad": None,
            "cantidad": None,
            "valor_unitario": _num(r[col_valor]),
            "region": str(r[col_region]).strip().title() if r[col_region] else None,
            "tipo_fuente": "invias_regional",
            "fuente": "INVIAS — Análisis de Precios Unitarios de Referencia Regionalizados 2026-1 (Territorio_APU_2026_1.xlsx)",
            "fecha_captura": date.today().isoformat(),
        })
    return filas


def cargar_referencia_banos(ws) -> list[dict]:
    """Referencia_Nacional_Banos — 53 ítems, referencia NACIONAL (no específica de Barranquilla)."""
    filas = []
    for r in _rows(ws):
        if r[1] is None or r[4] is None:
            continue
        filas.append({
            "actividad": str(r[1]).strip(),
            "unidad": r[3],
            "disciplina": "Hidráulica y Sanitaria / Acabados",
            "precio_todo_costo": _num(r[4]),
            "desglose_confiable": False,
            "region": None,  # explícitamente nacional, no Barranquilla
            "categoria_fuente": r[0],
            "tipo_fuente": "referencia_nacional",
            "fuente": (r[6] or "Construdata") + " — " + (r[8] or "referencia nacional, no desglosada por ciudad"),
            "fecha_captura": _fecha(r[7]),
        })
    return filas


def cargar_proveedores_catalogo(wb, hojas: list[str]) -> list[dict]:
    """Materiales_Construccion, Aceros_Vigas_Perfiles, Electricos_Tornilleria, Plomeria,
    Pinturas_Acabados, Seguridad_EPP_Cerrajeria, Herramientas — 24 SKU reales Homecenter/Samir."""
    filas = []
    for nombre in hojas:
        ws = wb[nombre]
        for r in _rows(ws):
            if r[2] is None:  # Producto / Descripción
                continue
            filas.append({
                "categoria": r[0],
                "subcategoria": r[1],
                "producto": str(r[2]).strip(),
                "marca": r[3],
                "especificaciones": r[4],
                "norma_tecnica": r[5],
                "presentacion_unidad": r[6],
                "precio_cop": _num(r[7]),
                "precio_unitario_normalizado": r[8],
                "proveedor": r[9] or "Sin identificar",
                "ciudad": r[10] or "Barranquilla",
                "url_fuente": r[11],
                "fecha_captura": _fecha(r[12]),
                "estado_verificacion": r[13],
                "notas": r[14],
            })
    return filas


def _batch_insert(sb, tabla: str, filas: list[dict], batch_size: int = 500) -> list[dict]:
    """Inserta en lotes y devuelve las filas insertadas con su id (para vincular padre-hijo)."""
    insertadas = []
    for i in range(0, len(filas), batch_size):
        lote = filas[i:i + batch_size]
        resp = sb.table(tabla).insert(lote).execute()
        insertadas.extend(resp.data)
    return insertadas


def vincular_insumos_a_padre(sb, insumos: list[dict], mapa_actividad_id: dict[str, str]):
    """Rellena actividad_padre_id por coincidencia exacta de texto contra apu_precios_referencia
    ya insertado, y hace update en lote de los insumos que sí calzan."""
    vinculados = 0
    for ins in insumos:
        texto = ins.get("actividad_padre_texto")
        if texto and texto in mapa_actividad_id:
            ins["actividad_padre_id"] = mapa_actividad_id[texto]
            vinculados += 1
    return vinculados


def cargar(dry_run: bool = False):
    if not RAW_XLSX.exists():
        print(f"ERROR: no se encuentra {RAW_XLSX}")
        return

    wb = openpyxl.load_workbook(RAW_XLSX, data_only=True)

    actividades_construdata = cargar_actividades_construdata(wb["APU_Actividades_Barranquilla"])
    insumos_construdata = cargar_insumos_construdata(wb["APU_Insumos_Detalle_BQ"])
    infraestructura = cargar_infraestructura_aa(wb["APU_Infraestructura_AA_BQ"])
    actividades_ptocol, insumos_ptocol = cargar_pto_colombia(wb["APU_Reales_PtoColombia"])
    actividades_tripleA, insumos_tripleA = cargar_triple_a_acometidas(wb["APU_Reales_TripleA_Acometidas"])
    actividades_mo_atl = cargar_mano_obra_atlantico(wb["Mano_Obra_Atlantico_2026"])
    referencia_banos = cargar_referencia_banos(wb["Referencia_Nacional_Banos"])

    insumos_invias = (
        cargar_invias(wb["INVIAS_Materiales_Atlantico"], "Material", 1, 3, 2)
        + cargar_invias(wb["INVIAS_ManoObra_Atlantico"], "Mano de Obra", 1, 2, 3)
        + cargar_invias(wb["INVIAS_Equipo_Atlantico"], "Equipo", 1, 3, 2)
    )

    proveedores = cargar_proveedores_catalogo(wb, [
        "Materiales_Construccion", "Aceros_Vigas_Perfiles", "Electricos_Tornilleria",
        "Plomeria", "Pinturas_Acabados", "Seguridad_EPP_Cerrajeria", "Herramientas",
    ])

    todas_actividades = (
        actividades_construdata + infraestructura + actividades_ptocol
        + actividades_tripleA + actividades_mo_atl + referencia_banos
    )
    todos_insumos = insumos_construdata + insumos_ptocol + insumos_tripleA + insumos_invias

    print("=== Resumen de carga (Base Maestra APU Barranquilla/Atlántico) ===")
    print(f"apu_precios_referencia:")
    print(f"  Construdata (catálogo):            {len(actividades_construdata):5d}")
    print(f"  Infraestructura AA (contrato real): {len(infraestructura):5d}")
    print(f"  Puerto Colombia (contrato real):    {len(actividades_ptocol):5d}")
    print(f"  Triple A acometidas (contrato real):{len(actividades_tripleA):5d}")
    print(f"  Mano de obra Atlántico (contrato):  {len(actividades_mo_atl):5d}")
    print(f"  Referencia nacional (baños):        {len(referencia_banos):5d}")
    print(f"  TOTAL:                              {len(todas_actividades):5d}")
    print(f"apu_insumos_referencia:")
    print(f"  Construdata (catálogo):    {len(insumos_construdata):5d}")
    print(f"  Puerto Colombia:           {len(insumos_ptocol):5d}")
    print(f"  Triple A acometidas:       {len(insumos_tripleA):5d}")
    print(f"  INVIAS regional Atlántico: {len(insumos_invias):5d}")
    print(f"  TOTAL:                     {len(todos_insumos):5d}")
    print(f"apu_proveedores_catalogo: {len(proveedores):5d}")

    if dry_run:
        print("\n[dry-run] No se inserta en Supabase.")
        return

    from supabase import create_client
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return
    sb = create_client(supabase_url, supabase_key)

    print("\nInsertando apu_precios_referencia...")
    insertadas = _batch_insert(sb, "apu_precios_referencia", todas_actividades)
    mapa_actividad_id = {f["actividad"]: f["id"] for f in insertadas if f.get("actividad")}
    print(f"  OK: {len(insertadas)} filas.")

    vinculados = vincular_insumos_a_padre(sb, todos_insumos, mapa_actividad_id)
    print(f"\nVinculando insumos a actividad padre por texto: {vinculados}/{len(todos_insumos)} calzaron.")

    print("Insertando apu_insumos_referencia...")
    ins_insumos = _batch_insert(sb, "apu_insumos_referencia", todos_insumos)
    print(f"  OK: {len(ins_insumos)} filas.")

    print("Insertando apu_proveedores_catalogo...")
    ins_prov = _batch_insert(sb, "apu_proveedores_catalogo", proveedores)
    print(f"  OK: {len(ins_prov)} filas.")

    print("\nListo.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    cargar(dry_run=dry)
