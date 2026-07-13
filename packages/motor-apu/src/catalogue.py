"""
══════════════════════════════════════════════════════════════
CATÁLOGO APU — Construdata 2026 · Barranquilla (factor 1.12)
Fuente: APU_Master_2026_Colombia.xlsx
NSR-10: f'c≥21 MPa · fy=420 MPa G-60 · Zona Intermedia Aa=0.15g
24 actividades — Cap. 1 Preliminares · 2 Excavación · 3 Concreto
4 Acero · 5 Mampostería · 6 Redes Hid. · 7 Eléctricas · 8 Cubiertas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fuentes:
  • Construdata Edición 187 (Jun-Ago 2018) columna B/QUILLA
    Factor ICCV 2018→2026 aplicado: ×1.82
  • Contrato CANGREJERA TRIPLE-A Barranquilla 2025-2026
    (precios directos, ya en COP 2026)
  • Salarios mínimos sector construcción 2026 (Min. Trabajo)
══════════════════════════════════════════════════════════════
"""
from .models import MaterialItem, ManoObraItem, EquipoItem, UnidadMedida, CategoriaObrero, AIU
from .engine import MotorAPU

engine = MotorAPU(aiu=AIU(administracion=0.10, imprevistos=0.05, utilidad=0.08))

# ─── PRECIOS UNITARIOS BARRANQUILLA 2026 ──────────────────────
P = {
    # Conglomerantes
    "CEM_50KG":       39_000,   # Cemento Portland 50 kg (bulto)
    "CEM_KG":            780,   # Cemento Portland (kg)
    # Áridos — B/QUILLA (Arena Juan de Acosta / Puerto Colombia)
    "ARENA_RIO":      90_000,   # Arena de río lavada (m³)
    "ARENA_PEGA":     95_000,   # Arena de pega fina (m³)
    "GRAVA_12":      105_000,   # Grava ½" triturada (m³)
    "RECEBO":         65_000,   # Recebo común (m³)
    "BASE_GRAN":      95_000,   # Base granular compactada (m³)
    # Acero
    "ACE_G60_KG":      5_100,   # Acero corrugado G-60 fy=420 MPa (kg)
    "ALM_18_KG":       8_500,   # Alambre negro #18 (kg)
    "BARR_38_6M":     19_500,   # Barra corrugada G-60 3/8"×6m (un) Ed.187×1.82
    "ACE_FIG_KG":      4_765,   # Acero figurado 60000 PSI (kg) Ed.187 $2,618×1.82
    # Concreto premezclado en planta (puesto en obra)
    "CTO_2000":      430_000,   # 2000 PSI (m³)
    "CTO_2500":      465_000,   # 2500 PSI (m³)
    "CTO_3000":      504_700,   # 3000 PSI (m³)  Ed.187 $277,317×1.82
    "CTO_4000":      560_000,   # 4000 PSI (m³)
    # Morteros y aditivos
    "MOR_1_4":        35_000,   # Mortero premezclado 1:4 (m³)
    "MOR_1_5":        32_000,   # Mortero premezclado 1:5 (m³)
    "AGUA_M3":         5_200,   # Agua potable (m³)
    "SIKAMENT_LT":    11_300,   # Aditivo plastificante (lt)
    "SIKA2_KG":        7_600,   # Sika-2 impermeabilizante (kg)
    # Mampostería
    "BLQ_10":          3_600,   # Bloque concreto 10×20×40 cm (un)
    "BLQ_15":          4_200,   # Bloque concreto 15×20×40 cm (un)
    "BLQ_20":          5_800,   # Bloque concreto 20×20×40 cm (un)
    "LAD_TOLETE":      1_800,   # Ladrillo tolete recocido (un)
    # Formaleta y apuntalamiento
    "FORM_M2":        14_200,   # Formaleta m² con accesorios (día) Ed.187×1.82
    "PARAL_3M":        4_400,   # Paral metálico hasta 3.30 m (ms)
    "DESENC_LT":      16_000,   # Desencofrante emulsionado 16 kg (un)
    # Distanciadores
    "DIST_58":           260,   # Distanciador CM-20 6.5mm-5/8" (un)
    "DIST_14":           340,   # Distanciador CP-30 clip pinza 1/4" (un)
    # Madera y tablas
    "TABLA_CHAPA":    41_650,   # Tabla chapa ordinaria 30×2cm×2.9m (un) Ed.187×1.82
    "REPISA_4CM":      6_250,   # Repisa 8×4cm×2.9m ordinario (un)
    "DURMIENTE_4CM":  10_430,   # Durmiente 4×4cm×2.9m ordinario (un)
    "PUNTILLA_2":      2_100,   # Puntilla con cabeza 2" (lb)
    # Curado
    "MEM_CURA_KG":     9_240,   # Membrana curadora blanco 20 kg (kg)
    # Malla electrosoldada
    "MALLA_XX159":    23_500,   # Malla electrosoldada XX-159 6×2.35m (un)
    # Equipo
    "VIB_DIA":        51_500,   # Vibrador de concreto a gasolina (día)
    "MEZ_HR":         34_000,   # Mezcladora 1 saco 5HP (hr)
    "AND_DIA":        15_000,   # Andamio tubular sección (día)
    # Seguridad Industrial
    "MAL_CERR_ML":    42_000,   # Malla cerramiento galvanizada H=2m (ml)
    "TUB_GAL_1":      55_000,   # Tubo galvanizado 1" poste (un)
    "SEN_KIT":       215_000,   # Kit 5 señales ICONTEC Res.1409 (kit)
    "CONO_REF":       72_000,   # Cono reflectivo vial (un) CANGREJERA 2026
    "VALLA_MOV":     450_000,   # Valla móvil tipo 1 plegable (un) CANGREJERA 2026
    # Excavaciones y rellenos — CANGREJERA 2026 (precios directos)
    "EXC_MAN_M3":     28_631,   # Excavación a mano material común m³
    "EXC_MAQ_M3":     35_752,   # Excavación a máquina m³
    "EXC_ROCA_M3":   122_410,   # Excavación roca con retromartillo m³
    "VOL_VIAJE":      38_000,   # Volqueta m³ (viaje) CANGREJERA 2026
    # Demoliciones — CANGREJERA 2026
    "DEMOL_MUR_M2":   10_748,   # Demolición muros 0.15m m²
    "DEMOL_CTO_M3":  160_551,   # Demolición concreto reforzado m³
}

# ─── SALARIOS 2026 ─────────────────────────────────────────────
S = {
    "AYUDANTE": 48_000,   # Ayudante albañilería (jornal/día)
    "OFICIAL":  72_000,   # Oficial albañilería (jornal/día)
    "MAESTRO":  95_000,   # Maestro de obra (jornal/día)
}
FACTOR_PREST = 1.6084   # Factor prestaciones sociales Colombia 2026

# ══════════════════════════════════════════════════════════════
# CAPÍTULO C — CONCRETO ESTRUCTURAL (NSR-10 Título C)
# ══════════════════════════════════════════════════════════════

def apu_columna_40x30():
    """Columna 40×30cm — Concreto 3000 PSI armada y vaciada (m)
    Fuente: Construdata Ed.187 B/QUILLA COLUMNA 40×30CM × ICCV 1.82"""
    materiales = [
        MaterialItem("CTO",   "Concreto CTE. Grava Común 3000 PSI",      UnidadMedida.M3, 0.12, P["CTO_3000"], desperdicio=0.03),
        MaterialItem("ACE",   "Acero corrugado Fig. 60000 PSI",           UnidadMedida.KG, 1.0,  P["ACE_FIG_KG"], desperdicio=0.03),
        MaterialItem("ALM",   "Alambre negro #18 recocido",               UnidadMedida.KG, 0.09, P["ALM_18_KG"], desperdicio=0.05),
        MaterialItem("BARR",  "Barra corrugada G-60 3/8\"×6m",            UnidadMedida.UN, 2.46, P["BARR_38_6M"], desperdicio=0.02),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",           UnidadMedida.UN, 0.03, P["DESENC_LT"]),
        MaterialItem("D58",   "Distanciador CM-20 6.5mm-5/8\"",           UnidadMedida.UN, 4.0,  P["DIST_58"]),
        MaterialItem("TABL",  "Tabla chapa 30×2cm×2.9m",                  UnidadMedida.UN, 1.0,  P["TABLA_CHAPA"], desperdicio=0.10),
        MaterialItem("REPR",  "Repisa 8×4cm×2.9m ordinario",              UnidadMedida.UN, 1.0,  P["REPISA_4CM"], desperdicio=0.10),
        MaterialItem("DURN",  "Durmiente 4×4cm×2.9m ordinario",           UnidadMedida.UN, 1.0,  P["DURMIENTE_4CM"], desperdicio=0.10),
        MaterialItem("PUNT",  "Puntilla con cabeza 2\"",                   UnidadMedida.KG, 0.40, P["PUNTILLA_2"], desperdicio=0.05),
        MaterialItem("MELL",  "Malla electrosoldada XX-159",               UnidadMedida.UN, 0.10, P["MALLA_XX159"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,   1.0, 4.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE,  2.0, 4.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB", "Vibrador concreto a gasolina", UnidadMedida.DIA, 0.08, 1.0, P["VIB_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.COL.40X30",
        descripcion="Columna 40×30cm — concreto 3000 PSI armada y vaciada",
        unidad=UnidadMedida.ML,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural",
        norma_ref="NSR-10 C.21 f'c≥21MPa columnas DMO | Construdata Ed.187 B/QUILLA ×1.82"
    )

def apu_concreto_columna_m3():
    """Concreto en columnas f'c=3000 PSI — vaciado en sitio (m³)"""
    materiales = [
        MaterialItem("CTO",  "Concreto CTE. Grava Común 3000 PSI", UnidadMedida.M3, 1.03, P["CTO_3000"], desperdicio=0.02),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",    UnidadMedida.UN, 0.25, P["DESENC_LT"]),
        MaterialItem("PUNT", "Puntilla con cabeza 2\"",             UnidadMedida.KG, 3.33, P["PUNTILLA_2"], desperdicio=0.05),
        MaterialItem("MEM",  "Membrana curadora blanco",            UnidadMedida.KG, 0.50, P["MEM_CURA_KG"]),
        MaterialItem("TABL", "Tabla chapa ordinaria 0.30m",         UnidadMedida.UN, 8.33, P["TABLA_CHAPA"], desperdicio=0.15),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.MAESTRO,   0.25, 2.0, S["MAESTRO"]),
        ManoObraItem(CategoriaObrero.OFICIAL,   1.0,  2.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE,  2.0,  2.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB", "Vibrador de concreto a gasolina", UnidadMedida.DIA, 0.5, 1.0, P["VIB_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.COL.M3",
        descripcion="Concreto en columnas f'c=3000 PSI (21 MPa) vaciado en sitio",
        unidad=UnidadMedida.M3,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural",
        norma_ref="NSR-10 C.3.2 / C.21 — f'c mín 21 MPa columnas DMO"
    )

def apu_viga_30x40():
    """Viga 30×40cm — Concreto 3000 PSI armada y vaciada (m)
    Fuente: Construdata Ed.187 B/QUILLA VIGA 30×40CM × ICCV 1.82"""
    materiales = [
        MaterialItem("CTO",   "Concreto CTE. Grava Común 3000 PSI", UnidadMedida.M3, 0.12, P["CTO_3000"], desperdicio=0.03),
        MaterialItem("ACE",   "Acero figurado 60000 PSI",            UnidadMedida.KG, 1.0,  P["ACE_FIG_KG"], desperdicio=0.03),
        MaterialItem("ALM",   "Alambre negro #18 recocido",          UnidadMedida.KG, 0.09, P["ALM_18_KG"], desperdicio=0.05),
        MaterialItem("BARR",  "Barra corrugada G-60 3/8\"×6m",       UnidadMedida.UN, 2.46, P["BARR_38_6M"], desperdicio=0.02),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",      UnidadMedida.UN, 0.03, P["DESENC_LT"]),
        MaterialItem("D58",   "Distanciador CM-20 6.5mm-5/8\"",      UnidadMedida.UN, 4.0,  P["DIST_58"]),
        MaterialItem("REPR",  "Repisa 8×4cm×2.9m",                   UnidadMedida.UN, 0.60, P["REPISA_4CM"], desperdicio=0.10),
        MaterialItem("TABL",  "Tabla chapa 30×2cm×2.9m",             UnidadMedida.UN, 1.0,  P["TABLA_CHAPA"], desperdicio=0.10),
        MaterialItem("PUNT",  "Puntilla con cabeza 2\"",              UnidadMedida.KG, 0.40, P["PUNTILLA_2"], desperdicio=0.05),
        MaterialItem("MEM",   "Membrana curadora blanco",             UnidadMedida.KG, 0.10, P["MEM_CURA_KG"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,   1.0, 5.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE,  2.0, 5.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB", "Vibrador concreto a gasolina", UnidadMedida.DIA, 0.08, 1.0, P["VIB_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.VIG.30X40",
        descripcion="Viga 30×40cm — concreto 3000 PSI armada y vaciada",
        unidad=UnidadMedida.ML,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural",
        norma_ref="NSR-10 C.11 — Vigas sismorresistentes | Construdata Ed.187 B/QUILLA ×1.82"
    )

def apu_acero_g60():
    """Suministro e instalación acero Grado 60 fy=420 MPa (kg)
    Fuente: Construdata Ed.187 — ACERO CORR. FIG. 60000 PSI $2,618×1.82"""
    materiales = [
        MaterialItem("ACE", "Acero corrugado G-60 A706 (fy=420 MPa)", UnidadMedida.KG, 1.0,   P["ACE_G60_KG"], desperdicio=0.05),
        MaterialItem("ALM", "Alambre negro #18 para amarre",           UnidadMedida.KG, 0.015, P["ALM_18_KG"],  desperdicio=0.10),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 250.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 250.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("DOB", "Dobladora/cortadora acero (hr)", UnidadMedida.HR, 1.0, 31.25, 18_000),
    ]
    return engine.calcular_apu(
        actividad_id="C.ACE.G60",
        descripcion="Acero G-60 fy=420 MPa — suministro, figurado e instalación",
        unidad=UnidadMedida.KG,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural",
        norma_ref="NSR-10 C.3.5 — Acero A706 obligatorio zonas sísmicas Alt. 2 y 3"
    )

def apu_zapata_120x120x45():
    """Zapata aislada 1.20×1.20×0.45m — Cimentación puntual (un)
    Ed.187 B/QUILLA $411,552 × 1.82 = $749,025/un"""
    materiales = [
        MaterialItem("CTO",   "Concreto CTE. Grava Común 3000 PSI",  UnidadMedida.M3, 0.65, P["CTO_3000"], desperdicio=0.02),
        MaterialItem("ACE",   "Acero figurado 60000 PSI",             UnidadMedida.KG, 1.0,  P["ACE_FIG_KG"], desperdicio=0.03),
        MaterialItem("ALM",   "Alambre negro #18 recocido",           UnidadMedida.KG, 0.25, P["ALM_18_KG"], desperdicio=0.05),
        MaterialItem("BARR",  "Barra corrugada G-60 3/8\"×6m",        UnidadMedida.UN, 3.36, P["BARR_38_6M"], desperdicio=0.02),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",       UnidadMedida.UN, 0.04, P["DESENC_LT"]),
        MaterialItem("D58",   "Distanciador CM-20 6.5mm-5/8\"",       UnidadMedida.UN, 4.0,  P["DIST_58"]),
        MaterialItem("D14",   "Distanciador CP-30 clip pinza 1/4\"",  UnidadMedida.UN, 4.0,  P["DIST_14"]),
        MaterialItem("REPR",  "Repisa 8×4cm×2.9m",                    UnidadMedida.UN, 2.0,  P["REPISA_4CM"], desperdicio=0.10),
        MaterialItem("TABL",  "Tabla chapa 30×2cm×2.9m",              UnidadMedida.UN, 1.65, P["TABLA_CHAPA"], desperdicio=0.10),
        MaterialItem("PUNT",  "Puntilla con cabeza 2\"",               UnidadMedida.KG, 0.40, P["PUNTILLA_2"], desperdicio=0.05),
        MaterialItem("MEM",   "Membrana curadora blanco",              UnidadMedida.KG, 0.10, P["MEM_CURA_KG"]),
        MaterialItem("MELL",  "Malla electrosoldada XX-159",           UnidadMedida.UN, 0.10, P["MALLA_XX159"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,   1.0, 2.5, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE,  2.0, 2.5, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB", "Vibrador concreto a gasolina", UnidadMedida.DIA, 0.10, 1.0, P["VIB_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.ZAP.120",
        descripcion="Zapata aislada 1.20×1.20×0.45m — concreto 3000 PSI armada",
        unidad=UnidadMedida.UN,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Cimentaciones",
        norma_ref="NSR-10 C.15 — Cimentaciones superficiales | Ed.187 B/QUILLA ×1.82"
    )

def apu_placa_aligerada():
    """Placa aligerada casetón icopor recuperable — entrepiso (m²)
    Ed.187 B/QUILLA $142,102/m² × 1.82 = $258,626/m²"""
    materiales = [
        MaterialItem("CTO",   "Concreto CTE. Grava Común 3000 PSI", UnidadMedida.M3, 0.20, P["CTO_3000"], desperdicio=0.03),
        MaterialItem("ACE",   "Acero figurado 60000 PSI",            UnidadMedida.KG, 1.0,  P["ACE_FIG_KG"], desperdicio=0.03),
        MaterialItem("ALM",   "Alambre negro #18 recocido",          UnidadMedida.KG, 0.50, P["ALM_18_KG"], desperdicio=0.05),
        MaterialItem("BARR",  "Barra corrugada G-60 3/8\"×6m",       UnidadMedida.UN, 3.36, P["BARR_38_6M"], desperdicio=0.02),
        MaterialItem("CASET", "Casetón icopor recuperable",           UnidadMedida.M3, 0.40, 111_300, desperdicio=0.05),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",      UnidadMedida.UN, 0.03, P["DESENC_LT"]),
        MaterialItem("D14",   "Distanciador CP-30 clip pinza 1/4\"", UnidadMedida.UN, 4.0,  P["DIST_14"]),
        MaterialItem("DURN",  "Durmiente 4×4cm×2.9m",                UnidadMedida.UN, 3.50, P["DURMIENTE_4CM"], desperdicio=0.10),
        MaterialItem("TABL",  "Tabla chapa 30×2cm×2.9m",             UnidadMedida.UN, 0.40, P["TABLA_CHAPA"], desperdicio=0.10),
        MaterialItem("REPR",  "Repisa 8×4cm×2.9m",                   UnidadMedida.UN, 0.20, P["REPISA_4CM"], desperdicio=0.10),
        MaterialItem("MELL",  "Malla electrosoldada XX-159",          UnidadMedida.UN, 0.10, P["MALLA_XX159"]),
        MaterialItem("MEM",   "Membrana curadora blanco",             UnidadMedida.KG, 0.10, P["MEM_CURA_KG"]),
        MaterialItem("PUNT",  "Puntilla con cabeza 2\"",              UnidadMedida.KG, 0.20, P["PUNTILLA_2"], desperdicio=0.05),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 15.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 15.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB",  "Vibrador concreto a gasolina", UnidadMedida.DIA, 0.08, 1.0,  P["VIB_DIA"]),
        EquipoItem("PAR",  "Paral metálico hasta 3.30m",   UnidadMedida.UN,  0.5,  1.0,  P["PARAL_3M"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.PLA.ALIG",
        descripcion="Placa aligerada casetón icopor recuperable — entrepiso",
        unidad=UnidadMedida.M2,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural (Placas)",
        norma_ref="NSR-10 C.13 — Losas de entrepiso | Ed.187 B/QUILLA ×1.82"
    )

def apu_muro_concreto_10cm():
    """Muro en concreto 3000 PSI, espesor 10cm — vaciado en sitio (m²)
    Ed.187 B/QUILLA $126,823/m × 1.82 = $230,819/m²"""
    materiales = [
        MaterialItem("CTO",   "Concreto CTE. Grava Común 3000 PSI", UnidadMedida.M3, 0.11, P["CTO_3000"], desperdicio=0.03),
        MaterialItem("DESENC","Desencofrante emulsionado 16 kg",      UnidadMedida.UN, 0.03, P["DESENC_LT"]),
        MaterialItem("D14",   "Distanciador PPN-100 1/4\"",          UnidadMedida.UN, 4.0,  P["DIST_14"]),
        MaterialItem("FORM",  "Formaleta m² con accesorios (día)",    UnidadMedida.DIA,1.0,  P["FORM_M2"]),
        MaterialItem("MELL",  "Malla electrosoldada XX-159",          UnidadMedida.UN, 0.14, P["MALLA_XX159"]),
        MaterialItem("MEM",   "Membrana curadora blanco",             UnidadMedida.KG, 0.10, P["MEM_CURA_KG"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 8.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 8.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VIB", "Vibrador concreto a gasolina", UnidadMedida.DIA, 0.08, 1.0, P["VIB_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="C.MUR.10",
        descripcion="Muro en concreto 3000 PSI e=10cm — vaciado en sitio",
        unidad=UnidadMedida.M2,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="C — Concreto Estructural (Muros)",
        norma_ref="NSR-10 C.14 — Muros estructurales de concreto | Ed.187 B/QUILLA ×1.82"
    )

# ══════════════════════════════════════════════════════════════
# CAPÍTULO D — MAMPOSTERÍA (NSR-10 Título D)
# ══════════════════════════════════════════════════════════════

def apu_muro_bloque15():
    """Muro mampostería confinada bloque concreto 15 cm (m²)"""
    materiales = [
        MaterialItem("BLQ",  "Bloque concreto 15×20×40 cm", UnidadMedida.UN, 12.5, P["BLQ_15"],  desperdicio=0.03),
        MaterialItem("MOR",  "Mortero premezclado 1:5",      UnidadMedida.M3, 0.04, P["MOR_1_5"], desperdicio=0.05),
        MaterialItem("AGUA", "Agua potable",                  UnidadMedida.M3, 0.04, P["AGUA_M3"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 8.5, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 8.5, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("AND", "Andamio tubular sección (día)", UnidadMedida.DIA, 0.5, 8.5, P["AND_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="D.MUR.BLQ15",
        descripcion="Muro mampostería confinada bloque concreto 15 cm",
        unidad=UnidadMedida.M2,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="D — Mampostería",
        norma_ref="NSR-10 D.4 — Mampostería confinada | confinantes cada 4m"
    )

def apu_muro_bloque10():
    """Muro divisorio bloque concreto 10 cm (m²)"""
    materiales = [
        MaterialItem("BLQ",  "Bloque concreto 10×20×40 cm", UnidadMedida.UN, 12.5, P["BLQ_10"],  desperdicio=0.03),
        MaterialItem("MOR",  "Mortero premezclado 1:5",      UnidadMedida.M3, 0.03, P["MOR_1_5"], desperdicio=0.05),
        MaterialItem("AGUA", "Agua potable",                  UnidadMedida.M3, 0.03, P["AGUA_M3"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 10.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 10.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("AND", "Andamio tubular sección (día)", UnidadMedida.DIA, 0.3, 10.0, P["AND_DIA"]),
    ]
    return engine.calcular_apu(
        actividad_id="D.MUR.BLQ10",
        descripcion="Muro divisorio bloque concreto 10 cm",
        unidad=UnidadMedida.M2,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="D — Mampostería",
        norma_ref="NSR-10 D.10 — Muros no estructurales de mampostería"
    )

# ══════════════════════════════════════════════════════════════
# CAPÍTULO H — MOVIMIENTO DE TIERRA (NSR-10 H)
# Fuente: Contrato CANGREJERA B/QUILLA 2025-2026 (precios directos)
# ══════════════════════════════════════════════════════════════

def apu_excavacion_manual():
    """Excavación a mano en material común — incluye retiro (m³)
    CANGREJERA 2026 ítem 3.3.2.1: $28,631/m³"""
    materiales = []
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 4.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 4.0, S["AYUDANTE"]),
    ]
    equipo = [
        EquipoItem("VOL", "Volqueta m³ (viaje)", UnidadMedida.HR, 1.0, 1.0, P["VOL_VIAJE"]),
    ]
    return engine.calcular_apu(
        actividad_id="H.EXC.MAN",
        descripcion="Excavación a mano en material común — incluye retiro",
        unidad=UnidadMedida.M3,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="H — Geotecnia y Excavaciones",
        norma_ref="NSR-10 H.1 — Trabajos de suelos | CANGREJERA B/QUILLA 2026"
    )

def apu_excavacion_maquina():
    """Excavación a máquina en material común — incluye retiro (m³)
    CANGREJERA 2026 ítem 3.3.2.2: $35,752/m³"""
    materiales = []
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL, 1.0, 80.0, S["OFICIAL"]),
    ]
    equipo = [
        EquipoItem("EXC", "Retroexcavadora (día)",  UnidadMedida.DIA, 1.0, 80.0, 850_000),
        EquipoItem("VOL", "Volqueta m³ (viaje)",    UnidadMedida.HR,  1.0, 4.0,  P["VOL_VIAJE"]),
    ]
    return engine.calcular_apu(
        actividad_id="H.EXC.MAQ",
        descripcion="Excavación a máquina en material común — incluye retiro",
        unidad=UnidadMedida.M3,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="H — Geotecnia y Excavaciones",
        norma_ref="NSR-10 H.1 — Trabajos de suelos | CANGREJERA B/QUILLA 2026"
    )

# ══════════════════════════════════════════════════════════════
# SEGURIDAD INDUSTRIAL (Decreto 1072/2015 — Res. 1409/2012)
# ══════════════════════════════════════════════════════════════

def apu_cerramiento_seguridad():
    """Cerramiento provisional de seguridad industrial (ml)
    Decreto 1072/2015 Art. 2.2.4.6.8 | Res. 1409/2012"""
    materiales = [
        MaterialItem("MAL",  "Malla cerramiento galvanizada H=2m",      UnidadMedida.ML, 1.1,  P["MAL_CERR_ML"], desperdicio=0.05),
        MaterialItem("TUB",  "Tubo galvanizado 1\" poste soporte c/2m", UnidadMedida.UN, 0.5,  P["TUB_GAL_1"]),
        MaterialItem("SEN",  "Kit señalización ICONTEC (5 señales)",    UnidadMedida.UN, 0.05, P["SEN_KIT"]),
        MaterialItem("CONO", "Cono reflectivo vial",                    UnidadMedida.UN, 0.10, P["CONO_REF"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 25.0, S["OFICIAL"]),
        ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 25.0, S["AYUDANTE"]),
    ]
    equipo = []
    return engine.calcular_apu(
        actividad_id="SEG.CER.01",
        descripcion="Cerramiento provisional de seguridad industrial en obra",
        unidad=UnidadMedida.ML,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="Seguridad Industrial (SISO)",
        norma_ref="Decreto 1072/2015 Art. 2.2.4.6.8 | Resolución 1409/2012 Trabajo en Alturas"
    )

def apu_valla_movil_pmt():
    """Valla móvil tipo 1 plegable — señalización PMT (un)
    CANGREJERA 2026 ítem 3.1.1.6.1: $339,864/un → 2026 actual"""
    materiales = [
        MaterialItem("VALL", "Valla móvil tipo 1 plegable (PMT)", UnidadMedida.UN, 1.0, P["VALLA_MOV"]),
    ]
    mano_obra = [
        ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 8.0, S["AYUDANTE"]),
    ]
    equipo = []
    return engine.calcular_apu(
        actividad_id="SEG.VAL.PMT",
        descripcion="Valla móvil tipo 1 plegable — señalización obra en vía pública",
        unidad=UnidadMedida.UN,
        materiales=materiales, mano_obra=mano_obra, equipo=equipo,
        capitulo="Seguridad Industrial (SISO)",
        norma_ref="Resolución 1409/2012 Art. 18 PMT | CANGREJERA B/QUILLA 2026"
    )

# ══════════════════════════════════════════════════════════════
# CAPÍTULO 1 — PRELIMINARES (APU_Master_2026_Colombia.xlsx)
# ══════════════════════════════════════════════════════════════

def apu_prel_limpieza_demolicion():
    """Limpieza y demolición de estructura existente (m²)"""
    return engine.calcular_apu(
        actividad_id="PREL-001",
        descripcion="Limpieza y demolición de estructura existente",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("HERR", "Herramienta menor (5%)", UnidadMedida.GL, 1.0, P["DEMOL_MUR_M2"] * 0.05),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 12.5, S["AYUDANTE"]),
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 12.5, S["OFICIAL"]),
        ],
        equipo=[
            EquipoItem("VOL", "Volqueta transporte escombros", UnidadMedida.VJE, 0.03, 1.0, P["VOL_VIAJE"]),
        ],
        capitulo="Cap. 1 — Preliminares",
        norma_ref="Decreto 1072/2015 — Seguridad Industrial",
    )

def apu_prel_nivelacion_compactacion():
    """Limpieza, nivelación y compactación de terreno (m²)"""
    return engine.calcular_apu(
        actividad_id="PREL-002",
        descripcion="Limpieza, nivelación y compactación de terreno",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("REC",  "Recebo compactación",     UnidadMedida.M3, 0.05, P["RECEBO"]),
            MaterialItem("AGUA", "Agua compactación",       UnidadMedida.M3, 0.008, P["AGUA_M3"]),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 25.0, S["AYUDANTE"]),
            ManoObraItem(CategoriaObrero.OPERARIO, 1.0, 80.0, S["MAESTRO"]),
        ],
        equipo=[
            EquipoItem("COMP", "Compactador vibratorio 5 HP", UnidadMedida.DIA, 0.0125, 1.0, 205_000),
        ],
        capitulo="Cap. 1 — Preliminares",
        norma_ref=None,
    )

def apu_prel_campamento():
    """Campamento provisional, bodegas y oficinas (gl)"""
    return engine.calcular_apu(
        actividad_id="PREL-003",
        descripcion="Campamento provisional, bodegas y oficinas en obra",
        unidad=UnidadMedida.GL,
        materiales=[
            MaterialItem("PAN", "Panel divisorio metálico provisional", UnidadMedida.M2, 80.0, 31_000, desperdicio=0.02),
            MaterialItem("CUB", "Cubierta zinc cal.26",                  UnidadMedida.M2, 60.0, 24_600, desperdicio=0.05),
            MaterialItem("PIS", "Piso entablado provisional",            UnidadMedida.M2, 40.0, 18_000, desperdicio=0.05),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  2.0, 0.0625, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 0.0625, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 1 — Preliminares",
        norma_ref="Decreto 1072/2015 Art. 2.2.4 — Instalaciones provisionales",
    )

def apu_prel_senalizacion():
    """Señalización y vallas de seguridad perimetral (ml)"""
    return engine.calcular_apu(
        actividad_id="PREL-004",
        descripcion="Señalización y vallas de seguridad perimetral",
        unidad=UnidadMedida.ML,
        materiales=[
            MaterialItem("VALLA", "Valla móvil PMT plegable",            UnidadMedida.UN, 0.25, P["VALLA_MOV"]),
            MaterialItem("CINTA", "Cinta señalización reflectiva",        UnidadMedida.ML, 1.0,    950, desperdicio=0.05),
            MaterialItem("KIT",   "Kit señales ICONTEC Res.1409 (5 un)", UnidadMedida.UN, 0.02, P["SEN_KIT"]),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 50.0, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 1 — Preliminares",
        norma_ref="NSR-10 I.1 — Supervisor técnico · Decreto 1072/2015",
    )


# ══════════════════════════════════════════════════════════════
# CAPÍTULO 4 — ACERO ADICIONAL
# ══════════════════════════════════════════════════════════════

def apu_acero_barra_38_instalada():
    """Barra corrugada G-60 3/8\" figurada e instalada (kg)"""
    return engine.calcular_apu(
        actividad_id="ACER-001",
        descripcion='Barra corrugada G-60 3/8" (9.5 mm) figurada e instalada',
        unidad=UnidadMedida.KG,
        materiales=[
            MaterialItem("BARR", 'Barra corrugada G-60 3/8"x6m', UnidadMedida.UN, 0.015, P["BARR_38_6M"], desperdicio=0.03),
            MaterialItem("ALM",  "Alambre negro #18",             UnidadMedida.KG, 0.006, P["ALM_18_KG"],  desperdicio=0.05),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 320.0, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 320.0, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("CIZ", "Cizalla cortadora electrica", UnidadMedida.DIA, 0.003, 1.0, 85_000),
        ],
        capitulo="Cap. 4 — Acero y Refuerzo",
        norma_ref="NSR-10 C.3.5 C.7 — fy=420 MPa G-60",
    )

def apu_malla_6x6_4x4():
    """Malla electrosoldada 6x6 4x4 colocada (m²)"""
    return engine.calcular_apu(
        actividad_id="ACER-002",
        descripcion="Malla electrosoldada 6x6 4x4 colocada",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("MALL", "Malla electrosoldada 6x6 4x4 panel 2.35 m", UnidadMedida.UN, 0.44, P["MALLA_XX159"], desperdicio=0.05),
            MaterialItem("ALM",  "Alambre recocido #18 (fijacion)",            UnidadMedida.KG, 0.02, P["ALM_18_KG"]),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 40.0, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 40.0, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 4 — Acero y Refuerzo",
        norma_ref="NSR-10 C.7 — Mallas de refuerzo",
    )

def apu_perfil_ipe200():
    """Perfil estructural IPE 200 laminado en caliente + soldadura (kg)"""
    return engine.calcular_apu(
        actividad_id="ACER-003",
        descripcion="Perfil estructural IPE 200 laminado en caliente + soldadura",
        unidad=UnidadMedida.KG,
        materiales=[
            MaterialItem("IPE",  "Perfil IPE 200 A36 6 m (aprox 22.4 kg/m)", UnidadMedida.UN, 0.0075, 650_000, desperdicio=0.03),
            MaterialItem("ELE",  "Electrodo E-7018 1/8",                      UnidadMedida.KG, 0.008,   20_700, desperdicio=0.05),
            MaterialItem("ANTI", "Anticorrosivo epoxido primario",             UnidadMedida.LT, 0.005,   31_000),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.SOLDADOR,  1.0, 16.7, S["MAESTRO"] * 1.4),
            ManoObraItem(CategoriaObrero.AYUDANTE,  1.0, 16.7, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("SOLD", "Equipo soldadura SMAW 250A", UnidadMedida.DIA, 0.06, 1.0, 125_000),
        ],
        capitulo="Cap. 4 — Acero y Refuerzo",
        norma_ref="NSR-10 F — Estructuras Metalicas",
    )


# ══════════════════════════════════════════════════════════════
# CAPÍTULO 5 — MAMPOSTERÍA ADICIONAL
# ══════════════════════════════════════════════════════════════

def apu_muro_ladrillo_macizo():
    """Muro ladrillo macizo prensado 24x12x6 cm fachada (m²)"""
    return engine.calcular_apu(
        actividad_id="MAMP-002",
        descripcion="Muro ladrillo macizo prensado 24x12x6 cm fachada",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("LAD", "Ladrillo macizo prensado 24x12x6 cm", UnidadMedida.UN, 68.0, P["LAD_TOLETE"], desperdicio=0.05),
            MaterialItem("MOR", "Mortero 1:3 fachada",                  UnidadMedida.M3, 0.025, P["MOR_1_4"] * 1.12),
            MaterialItem("CEM", "Cemento gris 50 kg (adicional)",       UnidadMedida.BTO, 0.03, P["CEM_50KG"]),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 1.538, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 2.0, 1.538, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("MEZ", "Mezcladora 1 saco 5 HP", UnidadMedida.HR, 0.10, 1.0, P["MEZ_HR"]),
        ],
        capitulo="Cap. 5 — Mamposteria Estructural",
        norma_ref="NSR-10 D.1 — Materiales mamposteria",
    )

def apu_columna_confinamiento():
    """Columna confinamiento 20x12 cm concreto f'c=17.5 MPa + acero (ml)"""
    return engine.calcular_apu(
        actividad_id="MAMP-003",
        descripcion="Columna confinamiento 20x12 cm concreto f'c=17.5 MPa + acero",
        unidad=UnidadMedida.ML,
        materiales=[
            MaterialItem("CTO",  "Concreto 2500 PSI premezclado",        UnidadMedida.M3, 0.0024, P["CTO_2500"], desperdicio=0.04),
            MaterialItem("ACE",  "Acero corrugado G-60 3/8",             UnidadMedida.KG, 1.8,   P["ACE_G60_KG"], desperdicio=0.03),
            MaterialItem("FORM", "Formaleta columna confinamiento",       UnidadMedida.M2, 0.08,  P["FORM_M2"] * 5),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 6.67, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 6.67, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 5 — Mamposteria Estructural",
        norma_ref="NSR-10 D.2.4 — Columnas de confinamiento",
    )


# ══════════════════════════════════════════════════════════════
# CAPÍTULO 6 — REDES HIDRÁULICAS Y SANITARIAS
# ══════════════════════════════════════════════════════════════

def apu_tuberia_pvc_2in():
    """Tuberia PVC 2in agua fria instalada (ml)"""
    return engine.calcular_apu(
        actividad_id="HID-001",
        descripcion='Tuberia PVC PAVCO 2" agua fria instalada',
        unidad=UnidadMedida.ML,
        materiales=[
            MaterialItem("TUB",  "Tuberia PVC PAVCO 2 pulgadas (m)",   UnidadMedida.ML, 1.0,  9_520, desperdicio=0.03),
            MaterialItem("ACC",  "Accesorios codos/tees/uniones 2in",  UnidadMedida.GL, 0.15, 9_520 * 0.15),
            MaterialItem("PEG",  "Pegante PVC 1/4 gal",                UnidadMedida.GL, 0.005,31_360),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.TECNICO,   1.0, 12.5, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE,  1.0, 12.5, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 6 — Redes Hidraulicas y Sanitarias",
        norma_ref="NTC 382 NTC 1339 — Tuberia PVC presion",
    )

def apu_tuberia_sanitaria_4in():
    """Tuberia sanitaria PVC 4in drenaje instalada (ml)"""
    return engine.calcular_apu(
        actividad_id="HID-002",
        descripcion='Tuberia sanitaria PVC 4" drenaje instalada',
        unidad=UnidadMedida.ML,
        materiales=[
            MaterialItem("TUB",  "Tuberia PVC sanitaria 4 pulgadas (m)", UnidadMedida.ML, 1.0,  17_024, desperdicio=0.03),
            MaterialItem("ACC",  "Accesorios sanitarios 4in (12%)",       UnidadMedida.GL, 0.12, 17_024 * 0.12),
            MaterialItem("SIL",  "Silla YEE 4x4 pulgadas",               UnidadMedida.UN, 0.05, 24_640),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.TECNICO,   1.0, 10.0, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE,  1.0, 10.0, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 6 — Redes Hidraulicas y Sanitarias",
        norma_ref="NTC 1087 RAS 2000 — Instalaciones sanitarias",
    )


# ══════════════════════════════════════════════════════════════
# CAPÍTULO 7 — REDES ELÉCTRICAS
# ══════════════════════════════════════════════════════════════

def apu_cable_12awg_canaleta():
    """Cable #12 AWG THWN-2 en canaleta instalado (ml)"""
    return engine.calcular_apu(
        actividad_id="ELEC-001",
        descripcion="Cable #12 AWG THWN-2 en canaleta metalica instalado",
        unidad=UnidadMedida.ML,
        materiales=[
            MaterialItem("CAB",  "Cable #12 AWG THWN-2 (m)",        UnidadMedida.ML, 1.0,    952, desperdicio=0.03),
            MaterialItem("CAN",  "Canaleta metalica 32 mm (m)",      UnidadMedida.ML, 1.0,  5_040, desperdicio=0.02),
            MaterialItem("CONX", "Conectores y abrazaderas (5%)",    UnidadMedida.GL, 0.05, 5_040),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.ELECTRICISTA, 1.0, 20.0, S["OFICIAL"] * 1.2),
            ManoObraItem(CategoriaObrero.AYUDANTE,     1.0, 20.0, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 7 — Redes Electricas",
        norma_ref="RETIE 2013 NTC 2050 — Instalaciones electricas",
    )

def apu_luminaria_led_40w():
    """Luminaria LED 40W downlight 3000K empotrada (un)"""
    return engine.calcular_apu(
        actividad_id="ELEC-002",
        descripcion="Luminaria LED 40W downlight 3000K empotrada IP44",
        unidad=UnidadMedida.UN,
        materiales=[
            MaterialItem("LED",  "Luminaria LED 40W downlight IP44", UnidadMedida.UN, 1.0, 95_200, desperdicio=0.0),
            MaterialItem("CAB",  "Cable #14 AWG THWN-2 (3 m)",       UnidadMedida.ML, 3.0,    694, desperdicio=0.05),
            MaterialItem("CAJA", "Caja octogonal empotrada galvan.",  UnidadMedida.UN, 1.0,  5_040),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.ELECTRICISTA, 1.0, 4.0, S["OFICIAL"] * 1.2),
            ManoObraItem(CategoriaObrero.AYUDANTE,     1.0, 4.0, S["AYUDANTE"]),
        ],
        equipo=[],
        capitulo="Cap. 7 — Redes Electricas",
        norma_ref="RETIE 2013 NTC 2050 — Iluminacion",
    )


# ══════════════════════════════════════════════════════════════
# CAPÍTULO 8 — CUBIERTAS E IMPERMEABILIZACIÓN
# ══════════════════════════════════════════════════════════════

def apu_cubierta_teja_ceramica():
    """Cubierta teja ceramica colonial cocida (m²)"""
    return engine.calcular_apu(
        actividad_id="CUB-001",
        descripcion="Cubierta teja ceramica colonial cocida 26x42 cm",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("TEJ",  "Teja ceramica colonial 26x42 cm",  UnidadMedida.UN, 30.0,  2_016, desperdicio=0.05),
            MaterialItem("MOR",  "Mortero 1:3 fijacion teja (kg)",   UnidadMedida.KG, 25.0,    448, desperdicio=0.05),
            MaterialItem("LIM",  "Limaton PVC blanco (ml)",           UnidadMedida.ML,  0.05, 20_160),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 2.0, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 2.0, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("AND", "Andamio tubular seccion", UnidadMedida.DIA, 0.5, 1.0, P["AND_DIA"]),
        ],
        capitulo="Cap. 8 — Cubiertas e Impermeabilizacion",
        norma_ref=None,
    )

def apu_membrana_asfaltica():
    """Cubierta membrana asfaltica impermeabilizacion (m²)"""
    return engine.calcular_apu(
        actividad_id="CUB-002",
        descripcion="Cubierta membrana asfaltica 4 mm APP torch-on impermeabilizacion",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("MEM",  "Membrana asfaltica 4 mm APP torch-on", UnidadMedida.M2, 1.05, 35_840, desperdicio=0.05),
            MaterialItem("IMP",  "Imprimante asfaltico (lt)",             UnidadMedida.LT,  0.3, 13_440),
            MaterialItem("GEO",  "Geotextil proteccion NT 200 (m2)",      UnidadMedida.M2,  1.0,  9_520),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.OFICIAL,  1.0, 2.86, S["OFICIAL"]),
            ManoObraItem(CategoriaObrero.AYUDANTE, 1.0, 2.86, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("SOP", "Soplete gas propano", UnidadMedida.DIA, 0.35, 1.0, 42_000),
            EquipoItem("AND", "Andamio tubular",     UnidadMedida.DIA, 0.35, 1.0, P["AND_DIA"]),
        ],
        capitulo="Cap. 8 — Cubiertas e Impermeabilizacion",
        norma_ref="NTC 4166 NTC 4167 — Membranas asfalticas",
    )

def apu_estructura_cubierta():
    """Estructura soporte cubierta viguetas + polines metalicos (m²)"""
    return engine.calcular_apu(
        actividad_id="CUB-003",
        descripcion="Estructura soporte cubierta (viguetas perfil C + polines omega)",
        unidad=UnidadMedida.M2,
        materiales=[
            MaterialItem("VIG",  "Vigueta perfil C 150x65x2 mm (kg)",  UnidadMedida.KG,  4.5,  6_496, desperdicio=0.03),
            MaterialItem("POL",  "Polin omega 1.5 pulgadas cal.22 (ml)",UnidadMedida.ML,  1.2, 13_440, desperdicio=0.03),
            MaterialItem("TOR",  "Tornillos autoperforantes techo",     UnidadMedida.UN,  8.0,    392),
            MaterialItem("ANTI", "Anticorrosivo epoxido",               UnidadMedida.LT,  0.02,42_560),
        ],
        mano_obra=[
            ManoObraItem(CategoriaObrero.SOLDADOR,  1.0, 3.33, S["MAESTRO"] * 1.3),
            ManoObraItem(CategoriaObrero.AYUDANTE,  2.0, 3.33, S["AYUDANTE"]),
        ],
        equipo=[
            EquipoItem("SOLD", "Equipo soldadura SMAW basico", UnidadMedida.DIA, 0.30, 1.0, 125_000),
        ],
        capitulo="Cap. 8 — Cubiertas e Impermeabilizacion",
        norma_ref="NSR-10 F — Estructuras Metalicas NTC 2289",
    )


# ══════════════════════════════════════════════════════════════
# CATÁLOGO COMPLETO
# ══════════════════════════════════════════════════════════════
CATALOGO_APU: dict = {
    # Capítulo C — Concreto Estructural
    "C.COL.40X30":  apu_columna_40x30,
    "C.COL.M3":     apu_concreto_columna_m3,
    "C.VIG.30X40":  apu_viga_30x40,
    "C.ACE.G60":    apu_acero_g60,
    "C.ZAP.120":    apu_zapata_120x120x45,
    "C.PLA.ALIG":   apu_placa_aligerada,
    "C.MUR.10":     apu_muro_concreto_10cm,
    # Capítulo D — Mampostería
    "D.MUR.BLQ15":  apu_muro_bloque15,
    "D.MUR.BLQ10":  apu_muro_bloque10,
    # Capítulo H — Excavaciones
    "H.EXC.MAN":    apu_excavacion_manual,
    "H.EXC.MAQ":    apu_excavacion_maquina,
    # Seguridad Industrial
    "SEG.CER.01":   apu_cerramiento_seguridad,
    "SEG.VAL.PMT":  apu_valla_movil_pmt,
    # Cap. 1 — Preliminares (APU_Master_2026)
    "PREL-001":     apu_prel_limpieza_demolicion,
    "PREL-002":     apu_prel_nivelacion_compactacion,
    "PREL-003":     apu_prel_campamento,
    "PREL-004":     apu_prel_senalizacion,
    # Cap. 4 — Acero adicional
    "ACER-001":     apu_acero_barra_38_instalada,
    "ACER-002":     apu_malla_6x6_4x4,
    "ACER-003":     apu_perfil_ipe200,
    # Cap. 5 — Mampostería adicional
    "MAMP-002":     apu_muro_ladrillo_macizo,
    "MAMP-003":     apu_columna_confinamiento,
    # Cap. 6 — Redes Hidráulicas
    "HID-001":      apu_tuberia_pvc_2in,
    "HID-002":      apu_tuberia_sanitaria_4in,
    # Cap. 7 — Redes Eléctricas
    "ELEC-001":     apu_cable_12awg_canaleta,
    "ELEC-002":     apu_luminaria_led_40w,
    # Cap. 8 — Cubiertas
    "CUB-001":      apu_cubierta_teja_ceramica,
    "CUB-002":      apu_membrana_asfaltica,
    "CUB-003":      apu_estructura_cubierta,
}

def get_apu(actividad_id: str):
    fn = CATALOGO_APU.get(actividad_id)
    return fn() if fn else None

def listar_actividades() -> list[dict]:
    results = []
    for aid, fn in CATALOGO_APU.items():
        r = fn()
        results.append({
            "id":               aid,
            "descripcion":      r.descripcion,
            "unidad":           r.unidad.value,
            "capitulo":         r.capitulo,
            "precio_unitario":  r.precio_unitario,
            "ic90_inf":         r.pu_p05,
            "ic90_sup":         r.pu_p95,
            "incertidumbre_pct":round(r.pu_std/r.pu_mean*100, 1) if r.pu_mean > 0 else 0,
            "norma_ref":        r.norma_ref,
        })
    return results

# ─── PRECIOS DE REFERENCIA EXPORTABLES AL SCHEMA SQL ──────────
PRECIOS_MATERIALES_2026 = [
    # (codigo, descripcion, unidad, precio_cop, fuente)
    ("CEM-50KG",  "Cemento Portland tipo I 50 kg",                    "bulto",  P["CEM_50KG"],   "mercado B/QUILLA 2026"),
    ("ARENA-RIO", "Arena de río lavada (Juan de Acosta)",             "m³",     P["ARENA_RIO"],  "Ed.187×1.82 + mercado"),
    ("GRAVA-12",  "Grava ½\" triturada",                             "m³",     P["GRAVA_12"],   "Ed.187×1.82 + mercado"),
    ("ACE-G60",   "Acero corrugado G-60 fy=420 MPa",                 "kg",     P["ACE_G60_KG"], "Ed.187 $2,618×1.82"),
    ("BLQ-15",    "Bloque concreto 15×20×40 cm",                     "un",     P["BLQ_15"],     "mercado B/QUILLA 2026"),
    ("BLQ-10",    "Bloque concreto 10×20×40 cm",                     "un",     P["BLQ_10"],     "mercado B/QUILLA 2026"),
    ("CTO-3000",  "Concreto premezclado 3000 PSI en planta",         "m³",     P["CTO_3000"],   "Ed.187 $277,317×1.82"),
    ("CTO-2500",  "Concreto premezclado 2500 PSI en planta",         "m³",     P["CTO_2500"],   "Ed.187 interpolado×1.82"),
    ("CTO-2000",  "Concreto premezclado 2000 PSI en planta",         "m³",     P["CTO_2000"],   "Ed.187 interpolado×1.82"),
    ("EXC-MAN",   "Excavación a mano material común (APU completo)", "m³",     P["EXC_MAN_M3"], "CANGREJERA 2026"),
    ("EXC-MAQ",   "Excavación a máquina material común",             "m³",     P["EXC_MAQ_M3"], "CANGREJERA 2026"),
]

PRECIOS_MO_2026 = [
    # (codigo, descripcion, jornal_dia, factor_prestaciones)
    ("MO-AYU", "Ayudante albañilería", S["AYUDANTE"], FACTOR_PREST),
    ("MO-OFC", "Oficial albañilería",  S["OFICIAL"],  FACTOR_PREST),
    ("MO-MAE", "Maestro de obra",      S["MAESTRO"],  FACTOR_PREST),
]
