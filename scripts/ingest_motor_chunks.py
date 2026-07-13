"""
Carga chunks de conocimiento específico de dominio (por motor) a Supabase
(motor_chunks), generando embeddings locales — mismo pipeline que
ingest_normativa.py (sentence-transformers, 384-dim).

A diferencia de ingest_normativa.py (que parsea documentos normativos
extraídos de Drive), estos chunks se redactan a mano a partir del código
YA PORTADO en packages/motor-*/src/ — fórmulas, tablas de referencia y
citas normativas que ya existen y están verificadas en el motor de cálculo,
no contenido inventado ni un documento normativo aparte.

Uso: python scripts/ingest_motor_chunks.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


# ─── AquAI — RAS 2000 / Resolución 0330 de 2017 ──────────────────────────────
# Fuente: packages/motor-aquai/src/{poblacion,caudales,hidraulica,ariete,
#         manning,bombeo,ptap,ptar,tarifario,hidrologia,ras2000_tablas}.py

AQUAI_CHUNKS: list[dict] = [
    {
        "seccion": "RAS B.1 — Proyección de población",
        "titulo": "Métodos de proyección poblacional",
        "norma_ref": "RAS 2000 Título B Sección B.1 / Res. 0330-2017 Art. 41",
        "contenido": (
            "La proyección de población para diseño de acueducto usa tres métodos: "
            "Aritmético P(t) = Po + r·Po·t (crecimiento lineal, válido para poblaciones "
            "estabilizadas o en descenso, puede subestimar zonas de expansión); "
            "Geométrico P(t) = Po·(1+r)^t (crecimiento proporcional, recomendado por el RAS "
            "para municipios de nivel de complejidad bajo y medio, más conservador que el "
            "exponencial); Exponencial P(t) = Po·e^(r·t) (crecimiento continuo compuesto, "
            "recomendado para ciudades intermedias y altas en expansión, tiende a ser el más "
            "conservador en horizontes largos). La tasa de crecimiento r se provee o se estima "
            "por nivel de complejidad; el período de diseño según RAS B.1.4 es de 15 años para "
            "nivel bajo, 20 para medio, y 25 años para medio-alto y alto."
        ),
    },
    {
        "seccion": "RAS B.2.1 — Dotación neta",
        "titulo": "Tabla de dotación neta por nivel de complejidad y clima",
        "norma_ref": "RAS 2000 / Res. 0330-2017 Tabla B.2.1",
        "contenido": (
            "La dotación neta (L/habitante/día) depende del nivel de complejidad del sistema "
            "y del clima. Nivel bajo: frío 90-120 (rec. 100), templado 100-130 (rec. 110), "
            "cálido 110-150 (rec. 130). Nivel medio: frío 110-140 (rec. 120), templado "
            "120-155 (rec. 135), cálido 130-170 (rec. 150). Nivel medio-alto: frío 120-160 "
            "(rec. 140), templado 135-175 (rec. 155), cálido 150-200 (rec. 170). Nivel alto: "
            "frío 140-200 (rec. 160), templado 150-225 (rec. 175), cálido 170-250 (rec. 200). "
            "La dotación bruta incluye pérdidas: dotación_bruta = dotación_neta / (1 - %pérdidas)."
        ),
    },
    {
        "seccion": "RAS B.2 — Caudales de diseño",
        "titulo": "Cadena de caudales Qp → Qmd → Qmh y caudal contra incendio",
        "norma_ref": "RAS 2000 Título B Sección B.2 / Res. 0330-2017",
        "contenido": (
            "El caudal promedio diario Qp [L/s] = (dotación_bruta [L/hab/día] × población) / "
            "86400. El caudal máximo diario Qmd = Qp × fmd, y el caudal máximo horario Qmh = "
            "Qmd × fmh. Los factores de variación (RAS B.2.3) según nivel de complejidad son: "
            "bajo fmd=1.30 fmh=2.00; medio fmd=1.25 fmh=1.90; medio-alto fmd=1.20 fmh=1.80; "
            "alto fmd=1.15 fmh=1.60. El caudal contra incendio Qci (RAS B.7) no aplica para "
            "nivel bajo (<1000 hab), es 4.0 L/s mínimo por 2 horas en nivel medio, 8.0 L/s en "
            "medio-alto y 16.0 L/s en nivel alto."
        ),
    },
    {
        "seccion": "RAS B.6 — Hazen-Williams en tuberías a presión",
        "titulo": "Fórmula de Hazen-Williams, coeficientes C y límites de velocidad/presión",
        "norma_ref": "RAS 2000 / Res. 0330-2017 Sección B.6; velocidades B.6.3; presiones B.6.4",
        "contenido": (
            "Velocidad V = 0.8492·C·R^0.63·S^0.54 (m/s); pérdida de carga hf = 10.67·L·Q^1.852 / "
            "(C^1.852·D^4.87) (m), con R el radio hidráulico ≈ D/4 para tubería llena. "
            "Coeficientes C de Hazen-Williams por material: PVC 150, HDPE 150, ACERO 120, "
            "AC (asbesto-cemento, histórico, ya no se instala) 110, CONCRETO 100, HIERRO 100, "
            "GRP 150. El motor calcula el diámetro comercial mínimo (lista nominal 25 a 1000 "
            "mm) que cumpla simultáneamente velocidad mínima 0.45 m/s (evitar sedimentación), "
            "velocidad máxima 5.0 m/s (evitar erosión) y presión mínima de entrega, por defecto "
            "10 m.c.a. mínimo y 60 m.c.a. máximo (RAS B.6.4); presión de salida por encima del "
            "máximo requiere válvula reductora de presión (VRP)."
        ),
    },
    {
        "seccion": "RAS B.7 — Golpe de ariete (transitorio hidráulico)",
        "titulo": "Teoría de Joukowski, celeridad de onda y clasificación del cierre",
        "norma_ref": "RAS 2000 Título B Sección B.7 — Transitorios hidráulicos",
        "contenido": (
            "Sobrepresión por cierre instantáneo (Joukowski): ΔH = a·ΔV/g. Celeridad de onda "
            "a = √(K/ρ) / √(1 + K·D/(E·e)), donde K es el módulo de compresibilidad del agua "
            "(2.07 GPa a 20°C) y E el módulo de elasticidad de la tubería: PVC 2.7 GPa, HDPE "
            "0.8 GPa (más flexible, menor ariete), GRP 35 GPa, gres 70 GPa, concreto 20 GPa, "
            "concreto reforzado 25 GPa, acero 210 GPa. El cierre se clasifica por el tiempo "
            "crítico de reflexión Tc = 2L/a: si el tiempo de cierre real es menor que Tc es "
            "cierre rápido/severo (ΔH = a·V0/g); si es mayor, cierre lento (ΔH = 2L·V0 / "
            "(g·T_cierre)). Presión máxima H_max = H_estática + ΔH, presión mínima H_min = "
            "H_estática − ΔH; hay riesgo de cavitación si H_min < −10 m."
        ),
    },
    {
        "seccion": "RAS Título D — Alcantarillado a gravedad (Manning)",
        "titulo": "Ecuación de Manning, coeficientes n y restricciones de diseño",
        "norma_ref": "RAS 2000 Título D / Resolución 0330/2017 Título D",
        "contenido": (
            "Caudal Q = (1/n)·A·R^(2/3)·S^(1/2); velocidad V = (1/n)·R^(2/3)·S^(1/2). "
            "Coeficientes de rugosidad de Manning n: PVC y HDPE 0.010, GRP 0.011, gres 0.012, "
            "concreto y concreto reforzado 0.013, acero 0.012. Restricciones RAS D.3: tirante "
            "máximo d/D ≤ 0.75, velocidad mínima de autolimpieza 0.45 m/s (RAS D.3.5), "
            "velocidad máxima 3.0 m/s en PVC/HDPE hasta 6.0 m/s en concreto reforzado según "
            "material, diámetro mínimo de colector 200 mm y de ramal domiciliario 150 mm."
        ),
    },
    {
        "seccion": "RAS B.8 — Estación de bombeo",
        "titulo": "Curva del sistema, TDH, potencia y NPSH disponible",
        "norma_ref": "RAS 2000 Título B Sección B.8 — Estaciones de bombeo",
        "contenido": (
            "La altura dinámica total TDH = H_sistema = Hg (altura geométrica) + pérdidas por "
            "fricción en succión y descarga (Hazen-Williams) + pérdidas menores por accesorios "
            "(codos K=0.9, válvula de cheque K=2.5, válvula de compuerta abierta K=0.3, entrada "
            "K=0.5, salida K=1.0). Potencia hidráulica P = ρ·g·Q·TDH; potencia al freno = "
            "P_hidráulica / eficiencia de la bomba; potencia instalada = potencia al freno / "
            "eficiencia del motor. NPSH disponible = (P_atmosférica − P_vapor)/(ρ·g) + "
            "altura de succión − pérdidas de succión; regla práctica del Hydraulic Institute: "
            "NPSHd ≥ NPSHr + 0.5 m de margen. RAS B.8.4 exige siempre bombas de reserva: el "
            "número de bombas instaladas es el número en operación más al menos 1 de reserva "
            "(mínimo 100% de reserva instalada)."
        ),
    },
    {
        "seccion": "Res. 0330/2017 Art. 125-140 — Planta de potabilización (PTAP)",
        "titulo": "Coagulación, floculación, sedimentación y filtración rápida",
        "norma_ref": "Resolución 0330 de 2017 Título C Potabilización, Arts. 125-140",
        "contenido": (
            "Dosificación de coagulante (Art. 125-127): la dosis depende de la turbiedad y "
            "color del agua cruda; si el color crudo supera 50 UC con sulfato de alumbre se "
            "recomienda evaluar sulfato férrico o PAC (Art. 126); pH óptimo de coagulación "
            "6.0-8.0. Floculación (Art. 128-130): mínimo 3 cámaras hidráulicas de flujo "
            "horizontal, gradiente de velocidad G=40 s⁻¹, tiempo de retención T=25 min, número "
            "de Camp GT≈60.000. Sedimentación (Art. 131-134): tasa superficial convencional "
            "20 m³/m²/día, sedimentación laminar (placas inclinadas) 60 m³/m²/día — se usa "
            "laminar si la turbiedad cruda supera 200 NTU; relación largo:ancho recomendada "
            "4:1. Filtración rápida (Art. 135-140): tasa máxima 180 m³/m²/día, mínimo 2 "
            "unidades, máximo 50 m² por filtro, lecho doble capa arena (0.60 m) + antracita "
            "(0.30 m), ciclo de lavado cada 24 h con retrolavado de 15 min."
        ),
    },
    {
        "seccion": "RAS Título E — Tratamiento de aguas residuales (PTAR)",
        "titulo": "UASB, lodos activados, laguna facultativa y cargas per cápita",
        "norma_ref": "RAS 2000 Título E — Tratamiento de aguas residuales (VIGENTE)",
        "contenido": (
            "Cargas per cápita de diseño (RAS Título E Tabla E.4.1): DBO₅ 50 g/hab/día "
            "(rango real 40-60), SST 60 g/hab/día (rango real 50-70). UASB — Reactor "
            "Anaerobio de Flujo Ascendente (RAS Sección E.9, nivel bajo/medio): velocidad "
            "ascensional 0.5-0.8 m/h, tiempo de retención hidráulica 4-8 h, eficiencia típica "
            "70% remoción DBO y 65% remoción SST; requiere postratamiento si el cuerpo "
            "receptor exige DBO < 90 mg/L. Lodos activados — aireación extendida (RAS Sección "
            "E.7, nivel medio-alto/alto): tiempo de retención celular (SRT) 20 días, "
            "coeficiente de producción Y=0.5 kg SSV/kg DBO, decaimiento endógeno Kd=0.05 "
            "1/día, MLSS de diseño 3500 mg/L, DBO efluente objetivo 20 mg/L, eficiencia SST "
            "92%; el RAS recomienda tiempo de retención hidráulica ≥ 18-24 h en aireación "
            "extendida. Laguna facultativa de estabilización (RAS Sección E.10, nivel bajo, "
            "requiere terreno amplio): diseño por carga superficial según temperatura."
        ),
    },
    {
        "seccion": "Res. 0631/2015 MADS — Límites de vertimiento",
        "titulo": "Valores máximos permisibles de DBO5, SST y pH por cuerpo receptor",
        "norma_ref": "Resolución 0631 de 2015 MADS + Decreto 1076/2015 Art. 2.2.3.3",
        "contenido": (
            "Límites de vertimiento de aguas residuales tratadas según el cuerpo receptor "
            "(Res. 0631/2015): a río o quebrada, DBO5 máximo 90 mg/L, SST máximo 90 mg/L, "
            "pH entre 6.0 y 9.0. A lago, límites más estrictos: DBO5 y SST máximo 30 mg/L, "
            "pH entre 6.5 y 8.5. A suelo (infiltración/riego), límites más laxos: DBO5 y SST "
            "hasta 300 mg/L, pH entre 6.0 y 9.0. El permiso de vertimiento se tramita según "
            "el Decreto 1076/2015 Artículo 2.2.3.3."
        ),
    },
    {
        "seccion": "CRA — Metodología tarifaria de acueducto y alcantarillado",
        "titulo": "Costo medio de largo plazo (CMLP), cargo fijo y cargo por consumo",
        "norma_ref": "Res. CRA 688/2014 · Res. CRA 943/2021 · Res. CRA 825/2017 · Res. CRA 750/2016",
        "contenido": (
            "La tarifa se calcula con el Costo Medio de Largo Plazo CMLP = CMI (costo medio de "
            "inversión) + CMO (costo medio de operación) + CMA_unitario (costo medio de "
            "administración distribuido). El Cargo Fijo mensual = CMA por suscriptor; el Cargo "
            "por Consumo = CMI + CMO + CMA distribuido, expresado en $/m³. CMI y CMO se ajustan "
            "por el factor de pérdidas 1/(1−%pérdidas) para llevarlos a $/m³ facturado. Por "
            "tipo de prestador: grandes prestadores bajo Res. CRA 688/2014 + Res. CRA 943/2021 "
            "(período tarifario 2021-2026); pequeños prestadores (≤5.000 suscriptores) bajo "
            "Res. CRA 825/2017; esquemas diferenciales rurales bajo Res. CRA 750/2016."
        ),
    },
    {
        "seccion": "CRA — Rangos de consumo y subsidios/contribuciones por estrato",
        "titulo": "Consumo básico/complementario/suntuario y factores de estrato (Ley 142/1994)",
        "norma_ref": "Ley 142 de 1994 Art. 99 · Decreto 1013 de 2005 · metodología CRA",
        "contenido": (
            "El consumo básico mensual por suscriptor varía por clima: clima frío hasta 11 m³, "
            "templado hasta 13 m³, cálido hasta 16 m³. El rango complementario va del básico "
            "hasta el básico × 1.545 (aprox.); por encima es consumo suntuario, con recargo del "
            "20% sobre la tarifa básica en el rango complementario y 60% en el suntuario. Los "
            "factores de subsidio/contribución por estrato (Ley 142/1994 Art. 99): estrato 1 "
            "subsidio máximo 70%, estrato 2 subsidio 40%, estrato 3 sin subsidio ni "
            "contribución (equilibrio), estrato 4 contribución solidaria 10%, estratos 5 y 6 "
            "contribución 20%, sector comercial contribución 50%, sector industrial "
            "contribución 30%, entidades oficiales en equilibrio."
        ),
    },
    {
        "seccion": "Curvas IDF regionales de Colombia",
        "titulo": "Intensidad-Duración-Frecuencia por región hidrográfica",
        "norma_ref": "RAS 2000 Título D / Resolución 0330-2017 — curvas IDF calibradas IDEAM/UNGRD",
        "contenido": (
            "La intensidad de lluvia de diseño para alcantarillado pluvial se calcula con "
            "I = a / (Tc^n + b), donde Tc es el tiempo de concentración en minutos e I resulta "
            "en mm/h; los coeficientes a, b, n están calibrados por región hidrográfica y "
            "período de retorno (2, 5, 10, 25, 50 y 100 años). La región Pacífico (Chocó "
            "biogeográfico) tiene los coeficientes más altos del país por ser la de mayor "
            "precipitación media del mundo — se recomienda usar sus valores con precaución y "
            "calibrar con estaciones IDEAM locales. La región Caribe tiene régimen bimodal "
            "(abril-junio / septiembre-noviembre) con zona seca en La Guajira que requiere "
            "corrección de +15% en el período de retorno. La Orinoquía tiene régimen unimodal "
            "(mayo-noviembre) sobre grandes llanuras de pendiente muy baja, y la Amazonía "
            "régimen ecuatorial casi uniforme con alta infiltración por cobertura vegetal."
        ),
    },
]

# ─── GeoPot — Laboratorio de suelos, concreto, agregados y sismorresistencia ─
# Fuente: packages/motor-geopot/src/{lab_suelos,lab_concreto,lab_agregados,
#         sismica}.py

GEOPOT_CHUNKS: list[dict] = [
    {
        "seccion": "ASTM D2487 — Clasificación USCS de suelos gruesos",
        "titulo": "Sistema Unificado de Clasificación de Suelos para gravas y arenas",
        "norma_ref": "ASTM D2487 — Sistema Unificado de Clasificación de Suelos (USCS)",
        "contenido": (
            "Un suelo se clasifica como grueso si menos del 50% pasa el tamiz #200 "
            "(finos). Dentro de gruesos, es grava si el % retenido en tamiz #4 supera "
            "al de arena, y viceversa. Con menos de 5% finos se evalúa la gradación "
            "por los coeficientes Cu = D60/D10 y Cc = D30²/(D60·D10): grava bien "
            "gradada (GW) requiere Cu≥4 y 1≤Cc≤3, arena bien gradada (SW) requiere "
            "Cu≥6 y 1≤Cc≤3; si no cumple, se clasifica como mal gradada (GP/SP). Con "
            "más de 12% finos se usa la carta de plasticidad (línea A = 0.73·(LL−20)): "
            "IP<4 o bajo la línea A da limosa (GM/SM), sobre la línea A da arcillosa "
            "(GC/SC). Entre 5% y 12% finos el suelo es de frontera (GW-GM/GP-GC o "
            "SW-SM/SP-SC, doble símbolo)."
        ),
    },
    {
        "seccion": "ASTM D2487 / AASHTO M145 — Suelos finos y clasificación vial",
        "titulo": "Carta de plasticidad de Casagrande y grupo AASHTO con índice de grupo",
        "norma_ref": "ASTM D2487 (USCS) · AASHTO M145",
        "contenido": (
            "Un suelo es fino (≥50% pasa tamiz #200) y se clasifica por la carta de "
            "plasticidad de Casagrande usando la línea A (IP = 0.73·(LL−20)): con "
            "LL<50 (baja plasticidad) IP bajo la línea A o IP<4 da ML (limo), sobre la "
            "línea A da CL (arcilla), y si 4≤IP<7 es CL-ML de frontera; con LL≥50 (alta "
            "plasticidad) bajo la línea A da MH, sobre la línea A da CH. Se marca "
            "posible materia orgánica si LL>50 y IP < 0.75×línea_A. Complementariamente, "
            "AASHTO M145 clasifica para subrasante vial en grupos A-1 a A-7 según LL, "
            "IP y % que pasa tamiz #200, con índice de grupo IG = (F−35)·(0.2+0.005·"
            "(LL−40)) + 0.01·(F−15)·(IP−10) (F = % pasa #200); aptitud de subrasante: "
            "IG=0 excelente/buena, IG≤1 buena, IG≤4 regular, IG≤8 mala, IG>8 muy mala."
        ),
    },
    {
        "seccion": "INV E-125/126 — Límites de Atterberg",
        "titulo": "Límite Líquido, Límite Plástico e Índice de Plasticidad",
        "norma_ref": "INV E-125 (Límite Líquido) / INV E-126 (Límite Plástico)",
        "contenido": (
            "El Índice de Plasticidad IP = LL − LP (%), donde LL es el Límite Líquido "
            "(INV E-125) y LP el Límite Plástico (INV E-126). Clasificación por IP: "
            "IP<7 no plástico o muy baja plasticidad, IP<15 baja plasticidad, IP<30 "
            "media plasticidad, IP<50 alta plasticidad, IP≥50 muy alta plasticidad. "
            "El índice de actividad de Skempton (arcillas expansivas) requiere además "
            "el % de fracción arcilla (<0.002 mm) de la granulometría."
        ),
    },
    {
        "seccion": "INV E-141/142 — Ensayo Proctor de compactación",
        "titulo": "Humedad óptima, densidad máxima seca y verificación de compactación de campo",
        "norma_ref": "INV E-141 (Proctor Estándar) / INV E-142 (Proctor Modificado)",
        "contenido": (
            "El ensayo Proctor (mínimo 3 puntos humedad-densidad) se ajusta por "
            "regresión cuadrática para hallar el punto óptimo: humedad óptima wópt y "
            "densidad seca máxima ρd_max. La verificación de compactación en campo "
            "compara la densidad seca medida contra ρd_max: %compactación = "
            "(densidad_campo / ρd_max) × 100; el criterio de conformidad estándar es "
            "≥95% de la densidad máxima Proctor (ajustable según especificación del "
            "proyecto), reportando el déficit exacto en puntos porcentuales cuando no "
            "se cumple."
        ),
    },
    {
        "seccion": "INV E-148 — Ensayo CBR de laboratorio",
        "titulo": "Relación de Soporte de California, clasificación de subrasante y espesor referencial",
        "norma_ref": "INV E-148 — California Bearing Ratio (CBR)",
        "contenido": (
            "El CBR se calcula como % de la carga patrón a dos penetraciones: a 2.54 mm "
            "la carga patrón es 13.34 kN (3000 lbf), a 5.08 mm es 20.01 kN (4500 lbf); "
            "CBR_diseño = máximo de los dos CBR calculados (criterio INVIAS). "
            "Clasificación de subrasante por CBR de diseño: CBR<3 S0 muy mala (requiere "
            "reemplazo de material), <6 S1 mala, <10 S2 regular, <20 S3 buena, <30 S4 "
            "muy buena, ≥30 S5 excelente. Para un estimado referencial de espesores "
            "AASHTO 93 se usa el módulo resiliente Mr [MPa] = 10.33·CBR^0.65 y el "
            "número estructural SN = 0.38·(ESAL_millones^0.2)·(1/CBR^0.2); este cálculo "
            "es solo orientativo, el diseño definitivo de pavimento requiere el método "
            "AASHTO 93 completo (motor-vías)."
        ),
    },
    {
        "seccion": "INV E-123 / NTC 77 — Granulometría por tamizado",
        "titulo": "Diámetros característicos D10/D30/D60, coeficientes de uniformidad y curvatura, módulo de finura",
        "norma_ref": "INV E-123 (granulometría suelos) / NTC 77 (agregados)",
        "contenido": (
            "Los diámetros D10, D30 y D60 se obtienen por interpolación lineal de la "
            "curva granulométrica (% que pasa vs. abertura del tamiz en mm). El "
            "coeficiente de uniformidad Cu = D60/D10 y el coeficiente de curvatura "
            "Cc = D30²/(D60·D10) determinan si un suelo grueso está bien o mal gradado "
            "(ver USCS). El módulo de finura (NTC 77, para arenas) es la suma de los "
            "% retenidos acumulados en los tamices 9.5, 4.75, 2.36, 1.18, 0.6, 0.3 y "
            "0.15 mm, dividida entre 100; requiere datos en al menos 5 de esos 7 "
            "tamices para calcularse."
        ),
    },
    {
        "seccion": "NTC 673 / NTC 396 — Ensayos de concreto: compresión y asentamiento",
        "titulo": "Resistencia a compresión de cilindros y clasificación del slump",
        "norma_ref": "NTC 673 (compresión de cilindros) / NTC 396 (asentamiento — cono de Abrams)",
        "contenido": (
            "La resistencia a compresión f'c [MPa] = Carga_falla [N] / Área_cilindro "
            "[mm²], con área = π·(diámetro/2)². El asentamiento (slump, NTC 396) se "
            "clasifica: 0-25 mm S1 seca/tierra húmeda, 25-75 mm S2 plástica baja, "
            "75-125 mm S3 plástica media, 125-175 mm S4 fluida, 175-220 mm S5 muy "
            "fluida, >220 mm S5+ autocompactante (verificar relación agua/cemento). "
            "Alertas de campo: slump >200 mm sugiere exceso de agua; temperatura de "
            "colada >32°C indica riesgo de fraguado acelerado."
        ),
    },
    {
        "seccion": "NSR-10 / ACI 318 — Resistencia mínima y conformidad del concreto",
        "titulo": "f'c mínimo por zona sísmica, criterios de conformidad y proyección de resistencia a 28 días",
        "norma_ref": "NSR-10 (Título C) / ACI 318 — Conformidad de resistencia del concreto",
        "contenido": (
            "Resistencia mínima f'c según zona sísmica NSR-10: zona BAJA 17.5 MPa "
            "(2500 PSI), zona INTERMEDIA y ALTA 21.0 MPa (3000 PSI) obligatorio. "
            "Criterio de conformidad ACI 318 (adoptado por NSR-10) sobre cilindros a "
            "28 días: (1) ningún promedio de 2 cilindros consecutivos puede ser menor "
            "que f'c de diseño; (2) ningún cilindro individual puede ser menor que "
            "(f'c diseño − 3.5 MPa). Si no hay cilindros de 28 días aún, se proyecta "
            "la resistencia con factores de madurez ACI 209 (aproximados para cemento "
            "portland): 3 días → factor 0.40, 7 días → 0.65, 14 días → 0.88, 28 días → "
            "1.00; f'c_proyectado = f'c_edad_temprana / factor_madurez. El control de "
            "calidad del lote se evalúa por coeficiente de variación (CV = desviación "
            "estándar / promedio × 100): CV<10% excelente, <15% buena, <20% regular, "
            "≥20% deficiente (revisar proceso)."
        ),
    },
    {
        "seccion": "NTC 174 / NTC 237 / NTC 218 — Requisitos de agregado grueso",
        "titulo": "Densidad, absorción, desgaste Los Ángeles y partículas planas/alargadas por uso",
        "norma_ref": "NTC 174 (requisitos generales) / NTC 237 (densidad y absorción) / NTC 218 (desgaste Los Ángeles)",
        "contenido": (
            "Densidad aparente SSS (superficie saturada seca) [g/cm³] = masa_SSS / "
            "(masa_SSS − masa_sumergida); absorción [%] = (masa_SSS − masa_seca) / "
            "masa_seca × 100. Límites NTC 174 según uso: para CONCRETO absorción "
            "máxima 3.0%, desgaste Los Ángeles máximo 40%, densidad mínima 2.4 g/cm³; "
            "para ASFALTO absorción máxima 2.0%, LA máximo 35%, densidad mínima "
            "2.5 g/cm³; para BASE GRANULAR absorción máxima 4.0%, LA máximo 50%, "
            "densidad mínima 2.3 g/cm³. Adicionalmente, partículas planas y alargadas "
            "no deben superar 15% en ningún uso."
        ),
    },
    {
        "seccion": "NTC 174 / NTC 237 / NTC 77 — Requisitos de agregado fino",
        "titulo": "Módulo de finura, absorción e impurezas orgánicas de la arena",
        "norma_ref": "NTC 174 (requisitos) / NTC 237 (densidad SSS por picnómetro, ASTM C128) / NTC 77 (granulometría)",
        "contenido": (
            "El módulo de finura de la arena (NTC 174) debe estar entre 2.3 y 3.1: "
            "MF<2.3 arena muy fina (no recomendada para concreto), 2.3-2.6 fina, "
            "2.6-2.9 media, 2.9-3.1 gruesa, >3.1 muy gruesa (verificar NTC 174). La "
            "densidad SSS se mide por picnómetro (ASTM C128); absorción máxima "
            "permitida 5.0%, densidad SSS mínima 2.3 g/cm³. Las impurezas orgánicas se "
            "clasifican por color de referencia (CLARO / MÁS CLARO / OSCURO); color "
            "OSCURO es causal de posible rechazo del agregado."
        ),
    },
    {
        "seccion": "ACI 211.1 — Diseño de mezcla de concreto",
        "titulo": "Relación agua/cemento, contenido de agua por TMA/slump y proporciones por m³",
        "norma_ref": "ACI 211.1 — Diseño básico de proporciones de concreto (aplicación simplificada)",
        "contenido": (
            "La relación agua/cemento (a/c) se interpola de la tabla ACI 211.1 según "
            "f'c (concreto sin aire incluido): 17.5 MPa → a/c 0.82, 21.0 → 0.74, "
            "24.5 → 0.68, 28.0 → 0.62, 31.5 → 0.57, 35.0 → 0.53, 42.0 → 0.44. El "
            "contenido de agua de mezcla depende del tamaño máximo del agregado (TMA) "
            "y el nivel de asentamiento (S1<50mm, S2 50-100mm, S3≥100mm): p.ej. para "
            "TMA 19 mm el agua varía entre 190 kg/m³ (S1) y 216 kg/m³ (S3). El cemento "
            "[kg/m³] = agua / (a/c); el volumen de agregado grueso se estima por "
            "volumen seco varillado × densidad, y el agregado fino completa el volumen "
            "unitario descontando pasta, grueso y ~1% de aire atrapado. El f'c de "
            "diseño nunca puede ser menor al mínimo NSR-10 de la zona sísmica del "
            "proyecto; si el usuario ingresa un valor menor, el motor lo ajusta "
            "automáticamente al mínimo normativo y lo reporta."
        ),
    },
    {
        "seccion": "NSR-10 — Zonificación sísmica por departamento",
        "titulo": "Aa, Av, Fa, Fv y medidas constructivas obligatorias según zona de amenaza",
        "norma_ref": "NSR-10 (Título A) — Movimientos sísmicos de diseño, zonificación por municipio/departamento",
        "contenido": (
            "Colombia se zonifica en amenaza sísmica BAJA (Aa<0.15g), INTERMEDIA "
            "(0.15g≤Aa<0.25g) y ALTA (Aa≥0.25g) según los coeficientes Aa (aceleración "
            "pico efectiva) y Av (velocidad) del NSR-10 por municipio. Ejemplos: "
            "Atlántico y Bolívar-Cartagena en zona baja/intermedia (Aa 0.12-0.15g, "
            "riesgo bajo); Bogotá, Antioquia, Valle del Cauca y el Eje Cafetero en "
            "zona ALTA (Aa=0.25g, riesgo medio). Medidas obligatorias por zona: BAJA "
            "requiere f'c mín 17.5 MPa, acero grado 40 permitido, recubrimiento 30 mm, "
            "sin análisis dinámico; INTERMEDIA requiere f'c mín 21 MPa, acero grado 60 "
            "recomendado, recubrimiento 35 mm, análisis estático equivalente mínimo; "
            "ALTA exige f'c mín 21 MPa y acero G-60 (fy=420 MPa) OBLIGATORIOS, "
            "recubrimiento 40 mm (NSR-10 C.7.7), separación máxima de estribos 100 mm "
            "(NSR-10 C.21.4.4.2), supervisión técnica independiente (STI) PERMANENTE "
            "obligatoria (Cap. I), análisis espectral tiempo-historia y estudio "
            "geotécnico profundo con respuesta de sitio y microzonificación."
        ),
    },
]


# ─── motor-vías — Diseño geométrico, pavimentos, mantenimiento, topografía ──
# Fuente: packages/motor-vias/src/{diseno_geometrico,pavimentos,mantenimiento,
#         topografia,ntc_materiales_1,ntc_materiales_2}.py

VIAS_CHUNKS: list[dict] = [
    {
        "seccion": "Manual INVIAS 2008 Cap. 3 Tabla 3.2 — Radio mínimo de curva horizontal",
        "titulo": "Radios mínimos por velocidad de diseño y peralte, con interpolación para velocidades no estándar",
        "norma_ref": "Manual de Diseño Geométrico de Carreteras INVIAS 2008 — Capítulo 3, Tabla 3.2",
        "contenido": (
            "El radio mínimo de curva horizontal [m] depende de la velocidad de diseño "
            "[km/h, múltiplos de 10 entre 30 y 120] y el peralte máximo disponible "
            "[6%, 8% o 10%]: a mayor peralte, menor radio mínimo requerido. Ejemplos de "
            "la tabla: V=60 km/h → radio mínimo 105 m (peralte 6%), 80 m (8%), 60 m "
            "(10%); V=80 km/h → 205/160/125 m; V=100 km/h → 345/270/215 m; V=120 km/h → "
            "530/420/335 m. El peralte máximo absoluto permitido es 8.0%. Para "
            "velocidades no tabuladas se interpola linealmente entre los radios de las "
            "velocidades adyacentes con el peralte más cercano al efectivo."
        ),
    },
    {
        "seccion": "Manual INVIAS 2008 Cap. 3/4/5 — Visibilidad, pendiente, ancho de carril y bombeo",
        "titulo": "Distancias de visibilidad de parada/adelantamiento, pendiente máxima por topografía y bombeo por superficie",
        "norma_ref": "Manual INVIAS 2008 Cap. 3 (Tablas 3.4-3.5), Cap. 4 (Tabla 4.1), Cap. 5 — con bombeo actualizado según Manual INVIAS 2025",
        "contenido": (
            "Distancia de visibilidad de parada [m] por velocidad (Tabla 3.4): 60 km/h → "
            "100 m, 80 km/h → 160 m, 100 km/h → 235 m, 120 km/h → 330 m. Distancia de "
            "visibilidad de adelantamiento (Tabla 3.5): 60 km/h → 360 m, 80 km/h → 570 m, "
            "100 km/h → 820 m, 120 km/h → 1130 m. Pendiente longitudinal máxima [%] según "
            "tipo de vía y topografía (Tabla 4.1): vía PRIMARIA 4% (plano) a 9% "
            "(escarpado); SECUNDARIA 5% a 10%; TERCIARIA 6% a 12%. Ancho mínimo de "
            "carril: primaria 3.65 m, secundaria 3.30 m, terciaria 3.00 m. Bombeo "
            "mínimo de calzada 2.0%; bombeo recomendado por tipo de superficie (Manual "
            "INVIAS 2025): asfáltica 2.5%, concreto 2.0%, afirmado 3.0% (mayor bombeo en "
            "afirmado por su menor capacidad de drenaje superficial)."
        ),
    },
    {
        "seccion": "AASHTO 93 adaptado — ESALs de diseño y Número Estructural requerido",
        "titulo": "Estimación de ejes equivalentes de 8.2 t y número estructural (SN) por CBR y ESALs",
        "norma_ref": "Método mecánico-empírico, ábacos AASHTO 93 adaptados (Manual INVIAS)",
        "contenido": (
            "Si no se dispone de un conteo vehicular detallado, los ESALs de diseño se "
            "estiman como TPD × 365 × factor_crecimiento(1.5, período de diseño 20 años "
            "al 2.5% anual) × factor_camiones / 1.000.000; el factor de camiones crece "
            "con el TPD: 0.05 (TPD<100), 0.10 (TPD<1000), 0.15 (TPD<5000), 0.20 "
            "(TPD≥5000). El Número Estructural requerido (SN) se obtiene de una tabla "
            "ESALs–CBR (ábacos AASHTO 93 adaptados): por ejemplo con 5 millones de "
            "ESALs y CBR=5% el SN requerido es 4.4; con CBR=8% baja a 3.6; con 10 "
            "millones de ESALs y CBR=5% el SN sube a 5.0. A mayor CBR de subrasante o "
            "menor tránsito, menor SN requerido."
        ),
    },
    {
        "seccion": "AASHTO 93 adaptado — Diseño de pavimento asfáltico (estructura flexible)",
        "titulo": "Coeficientes estructurales, coeficientes de drenaje y cálculo de espesores de capas",
        "norma_ref": "Método mecánico-empírico AASHTO 93 adaptado — estructura flexible",
        "contenido": (
            "El SN aportado por cada capa es SNi = ai·di·mi (ai: coeficiente estructural "
            "1/cm, di: espesor cm, mi: coeficiente de drenaje). Coeficientes "
            "estructurales: rodadura asfáltica a1=0.44, base granular a2=0.14, subbase "
            "granular a3=0.11. Coeficientes de drenaje según calidad: excelente 1.20, "
            "bueno 1.10, regular 1.00, pobre 0.90, muy pobre 0.80 (el motor asume "
            "'bueno' por defecto para base y subbase). Espesores mínimos: rodadura "
            "5 cm, base 15 cm, subbase 15 cm; espesores máximos recomendados: rodadura "
            "25 cm, base 40 cm, subbase 60 cm. El diseño fija primero rodadura y base "
            "en sus mínimos, calcula el SN restante para la subbase (SN_restante = "
            "SN_requerido − SN1 − SN2, entonces d3 = SN_restante/(a3·m3)), y redondea "
            "todos los espesores a múltiplos de 2.5 cm."
        ),
    },
    {
        "seccion": "AASHTO 93 adaptado — Diseño de pavimento de concreto (estructura rígida)",
        "titulo": "Espesor de losa por conversión de SN y juntas de contracción",
        "norma_ref": "Método mecánico-empírico AASHTO 93 adaptado — estructura rígida",
        "contenido": (
            "El espesor de la losa de concreto se estima por conversión aproximada del "
            "número estructural: D_concreto [cm] = SN_requerido / 0.39, redondeado a "
            "múltiplos de 2.5 cm y limitado al espesor mínimo de losa (15 cm) y máximo "
            "recomendado (40 cm, por encima de este se sugiere refuerzo continuo o losas "
            "postensadas). Base y subbase bajo la losa son opcionales con mínimos de "
            "10 cm cada una (máximos 30 cm base, 50 cm subbase). Recomendación de "
            "diseño: para toda losa se sugieren juntas de contracción cada 4-5 m con "
            "barras de transferencia de carga."
        ),
    },
    {
        "seccion": "Manual de Mantenimiento INVIAS 2016 (Res. 04046/2018) — Clasificación y defectología de baches y grietas",
        "titulo": "Tipos de mantenimiento (rutinario/periódico/emergencia) y umbrales de gravedad para baches y grietas",
        "norma_ref": "Manual de Mantenimiento de Carreteras INVIAS (2016), adoptado por Resolución 04046 de 2018",
        "contenido": (
            "El mantenimiento se clasifica en RUTINARIO (conservación continua diaria/"
            "semanal: rocería, limpieza de cunetas, sello de fisuras, bacheo "
            "superficial), PERIÓDICO (intervenciones programadas anuales/bianuales: "
            "recarpeteo, rehabilitación de rodadura) y EMERGENCIA (atención inmediata "
            "24-48 h: baches profundos, estabilización de taludes, puentes dañados). "
            "Defectología de BACHE por profundidad/área: BAJA <2.5 cm y <0.5 m² → sello "
            "superficial; MEDIA <5.0 cm y <2.0 m² → parcheo localizado; ALTA <10 cm y "
            "<5.0 m² → bacheo profundo; CRÍTICA → reconstrucción de tramo. Defectología "
            "de GRIETA por ancho/longitud: BAJA <3 mm y <10 m → sello de fisuras; MEDIA "
            "<6 mm y <30 m → sello asfáltico; ALTA <12 mm y <50 m → parcheo o recapeo; "
            "CRÍTICA → reconstrucción."
        ),
    },
    {
        "seccion": "Manual de Mantenimiento INVIAS 2016 — Ahuellamiento, craquelado, losas fragmentadas y prioridad de intervención",
        "titulo": "Umbrales de otros deterioros, índice de condición (PCI) y tiempos de respuesta por prioridad",
        "norma_ref": "Manual de Mantenimiento de Carreteras INVIAS (2016), Resolución 04046 de 2018",
        "contenido": (
            "AHUELLAMIENTO por profundidad: BAJA <1.0 cm (monitoreo), MEDIA <2.5 cm "
            "(fresado superficial), ALTA <5.0 cm (fresado y recapeo), CRÍTICA "
            "(reconstrucción de capa). CRAQUELADO por % de área afectada: BAJA <10% "
            "(sello superficial), MEDIA <30% (tratamiento superficial), ALTA <60% "
            "(recapeo), CRÍTICA (reconstrucción). LOSA FRAGMENTADA por número de "
            "fragmentos: BAJA ≤4 (sello de juntas), MEDIA ≤8 (reparación parcial), ALTA "
            "≤12 (reemplazo de losa), CRÍTICA (reconstrucción de tramo). El índice de "
            "condición (PCI, 0-100%) clasifica el pavimento: ≥85 excelente, ≥70 bueno, "
            "≥50 regular, ≥30 pobre, <30 crítico (intervención inmediata). La prioridad "
            "de intervención se ajusta al alza por volumen de tránsito (TPD>10000 → "
            "crítico) y por PCI bajo (PCI<30 → crítico, PCI<50 → alto); tiempos de "
            "respuesta: bajo 30 días, medio 15 días, alto 7 días, crítico 24-48 horas."
        ),
    },
    {
        "seccion": "Nivelación geométrica — Tolerancia de cierre altimétrico (INVIAS/IDU/IGAC)",
        "titulo": "Fórmula de error de cierre permisible C·√K y coeficientes por entidad",
        "norma_ref": "Guía de estandarización INVIAS 2023 / IDU / IGAC · NTC 6271",
        "contenido": (
            "El error de cierre permisible en nivelación geométrica diferencial es "
            "E_max [mm] = C·√K, donde K es la longitud del circuito o tramo nivelado en "
            "km (ida+vuelta, o perímetro del circuito cerrado) y C es el coeficiente en "
            "mm de la entidad de referencia: INVIAS C=10 (precisión 2.0 cm/km, nivel "
            "automático de precisión), IDU C=5 (precisión 1.0 cm/km, nivel digital o "
            "automático), IGAC C=2 (precisión 0.5 cm/km, nivel geodésico de alta "
            "precisión — el estándar más exigente). El cierre medido en campo (suma "
            "algebraica de diferencias ida/vuelta) se compara contra E_max; la holgura "
            "reportada es E_max menos el error medido absoluto."
        ),
    },
    {
        "seccion": "NTC 2017 — Adoquines de concreto para pavimentos",
        "titulo": "Espesor mínimo por aplicación, resistencia a flexotracción y absorción máxima",
        "norma_ref": "NTC 2017 (tercera actualización, 2018) — INVIAS Art. 510",
        "contenido": (
            "Espesor mínimo del adoquín según aplicación: peatonal 60 mm, vehicular "
            "liviano 80 mm, vehicular pesado 100 mm, industrial 100 mm, portuario "
            "100 mm (requiere además BS EN 1338). Resistencia a flexotracción mínima "
            "5.0 MPa en promedio y 4.2 MPa individual. Absorción máxima 7.0% en general, "
            "reducida a 5.0% para aplicación portuaria o de alta especificación. "
            "Tolerancias dimensionales: largo/ancho ±2.0 mm, espesor ±3.0 mm."
        ),
    },
    {
        "seccion": "NTC 4342 — Geotextiles para retención asfáltica",
        "titulo": "Retención asfáltica mínima, composición y tipo válido de geotextil",
        "norma_ref": "NTC 4342 — Geotextiles en pavimentos asfálticos, equivalente INVIAS D6140",
        "contenido": (
            "Para geotextiles usados en membranas de retención asfáltica dentro de "
            "estructuras de pavimento: retención asfáltica mínima 0.9 L/m² (INVIAS "
            "D6140); composición mínima 95% de poliolefinas o poliéster en masa; el "
            "tipo debe ser no tejido o punzonado por agujas (el tejido no es válido "
            "para esta aplicación)."
        ),
    },
    {
        "seccion": "NTC 121 / NTC 1362 — Cemento hidráulico gris y blanco",
        "titulo": "Resistencias mínimas por tipo y edad, fraguado inicial y expansión en autoclave",
        "norma_ref": "NTC 121 (especificación de desempeño, 2021) / NTC 1362 (cemento blanco, incluida en NSR-10)",
        "contenido": (
            "NTC 121 clasifica el cemento gris en tipos UG (uso general: 12/19/28 MPa a "
            "3/7/28 días), ART (alta resistencia temprana: 12/24/31/38 MPa a 1/3/7/28 "
            "días), RS (resistente a sulfatos: 10/17/25 MPa), CH (bajo calor de "
            "hidratación: 8/14/21 MPa). NTC 1362 clasifica el cemento blanco en tipo I "
            "(12/19/28 MPa), II (moderada resistencia a sulfatos: 10/17/25 MPa), III "
            "(alta resistencia temprana: 12/24/31/38 MPa) y exige blancura mínima 80% "
            "(NTC 6274). Ambos comparten: fraguado inicial entre 45 y 420 minutos (NTC "
            "118, Vicat) y expansión máxima en autoclave 0.80% (NTC 107)."
        ),
    },
    {
        "seccion": "NTC 1299 / NTC 3502 — Aditivos químicos y aire incorporado",
        "titulo": "Tipos A-H de aditivos químicos (ASTM C494) y requisitos de aire incorporado (ASTM C260)",
        "norma_ref": "NTC 1299 (IDT ASTM C494/C494M-05a) / NTC 3502 (equivalente ASTM C260)",
        "contenido": (
            "NTC 1299 clasifica los aditivos químicos para concreto en 8 tipos según "
            "ASTM C494: A plastificante/reductor de agua, B retardante, C acelerante, D "
            "plastificante retardante, E plastificante acelerante, F superplastificante "
            "(reducción de agua >12%), G superplastificante retardante, H "
            "superplastificante acelerante. NTC 3502 rige los aditivos incorporadores "
            "de aire: contenido de aire incorporado debe estar entre 4.0% y 8.0% del "
            "volumen de concreto, el aditivo debe estar libre de cloruros (para evitar "
            "corrosión del refuerzo) y debe ser compatible con otros aditivos químicos; "
            "se usa en concretos expuestos a ciclos hielo-deshielo, pavimentos, puentes "
            "y concretos Tremie."
        ),
    },
    {
        "seccion": "NTC 3459 — Agua para elaboración de concreto",
        "titulo": "Límites de sulfatos, cloruros, sólidos, pH e iones comunes",
        "norma_ref": "NTC 3459 (ed. 2001)",
        "contenido": (
            "Límites de calidad del agua de mezcla: sulfatos máximo 1000 mg/L; "
            "cloruros máximo 1000 mg/L en concreto reforzado, reducido a 500 mg/L en "
            "concreto pre-esforzado (mayor sensibilidad a la corrosión del acero de "
            "presfuerzo); sólidos totales máximo 50.000 mg/L; sólidos disueltos máximo "
            "2.000 mg/L; pH mínimo 5.0; iones comunes (Ca²⁺, Mg²⁺, Na⁺, K⁺, NO₃⁻, CO₃²⁻) "
            "máximo 2.000 mg/L. Las fuentes de agua NATURAL, LLUVIA, RECICLADA e "
            "INDUSTRIAL TRATADA requieren ensayo de laboratorio obligatorio antes de su "
            "uso; el agua POTABLE se asume conforme sin ensayo adicional."
        ),
    },
    {
        "seccion": "NTC 3493 / NTC 4018 — Puzolanas/cenizas volantes y escoria de alto horno",
        "titulo": "Suma de óxidos, pérdida por ignición y grados de índice de actividad",
        "norma_ref": "NTC 3493 (equivalente ASTM C618) / NTC 4018 (primera actualización 2017, equivalente ASTM C989)",
        "contenido": (
            "NTC 3493 exige suma de óxidos (SiO₂+Al₂O₃+Fe₂O₃) mínima 70% para clases N, "
            "S y F (puzolana natural y ceniza volante bajo calcio), reducida a 50% para "
            "clase C (ceniza volante alto calcio); pérdida por ignición máxima 6.0% "
            "(hasta 12.0% con tolerancia excepcional validada en laboratorio); "
            "retención máxima en malla No. 325: 34%. NTC 4018 clasifica la escoria de "
            "alto horno granulada y molida por grado según su índice de actividad con "
            "cemento Portland a 28 días: Grado 80 (índice ≥80%, uso general), Grado 100 "
            "(≥100%, resistencia media/alta) y Grado 120 (≥120%, alta resistencia y "
            "durabilidad excepcional); finura Blaine mínima 350 m²/kg; azufre máximo "
            "2.5%. Ambos materiales sustituyen parcialmente el cemento Portland, "
            "reduciendo la huella de carbono y mejorando la durabilidad frente a "
            "sulfatos."
        ),
    },
    {
        "seccion": "NTC 4024 / NTC 4924 — Prefabricados de concreto y agregados livianos",
        "titulo": "Muestreo por tamaño de lote, ensayos requeridos y límites de agregado liviano",
        "norma_ref": "NTC 4024 (muestreo y ensayo, 2001) / NTC 4924 (equivalente ASTM C331, 2001)",
        "contenido": (
            "NTC 4024 fija el número de especímenes de prefabricados (bloques, "
            "ladrillos, adoquines) según el tamaño del lote: 6 especímenes para lotes "
            "hasta 10.000 unidades, 12 para lotes hasta 100.000, y 6 adicionales por "
            "cada 50.000 unidades por encima de ese umbral; exige los cuatro ensayos de "
            "compresión, absorción, densidad y humedad; el rótulo no puede cubrir más "
            "del 5% del área de la superficie. NTC 4924 limita el agregado liviano para "
            "mampostería (arcilla expandida, esquisto expandido, puzolana expandida, "
            "escoria expandida) a densidad aparente máxima 1120 kg/m³ y absorción "
            "máxima 25%, mejorando el aislamiento térmico/acústico de los muros a "
            "cambio de menor densidad."
        ),
    },
]


# ─── motor-gerencia — Earned Value Management + predicción ML ──────────────
# Fuente: packages/motor-gerencia/src/{evm,ml_engine}.py

GERENCIA_CHUNKS: list[dict] = [
    {
        "seccion": "EVM — Índices de desempeño CPI, SPI, QPI, PPI",
        "titulo": "Fórmulas de los índices de costo, cronograma, calidad y productividad, y sus umbrales de semáforo",
        "norma_ref": "PMI/PMBOK — Earned Value Management (EVM)",
        "contenido": (
            "CPI (Cost Performance Index) = EV/AC (valor ganado sobre costo real); SPI "
            "(Schedule Performance Index) = EV/PV (valor ganado sobre valor "
            "planificado); QPI (Quality Performance Index) = %Calidad/100; PPI "
            "(Productivity Performance Index) = (EV/AC)×(RP/RR), combinando "
            "rendimiento de costo con la relación entre rendimiento real (RP) y "
            "requerido (RR). Para los cuatro índices, valores >1.0 son buen desempeño "
            "(verde 🟢), 0.90-0.999 es alerta (🟡, excepto PPI cuyo umbral de alerta "
            "baja a 0.85), y <0.90 (<0.85 en PPI) es crítico (🔴). Todos son "
            "'higher_better': un valor más alto siempre es mejor desempeño."
        ),
    },
    {
        "seccion": "EVM — Variaciones SV, CV y TCPI",
        "titulo": "Variación de cronograma y costo en unidades monetarias, e índice de desempeño para completar",
        "norma_ref": "PMI/PMBOK — Earned Value Management (EVM)",
        "contenido": (
            "SV (Schedule Variance) = EV − PV [USD]: negativo indica atraso respecto al "
            "plan. CV (Cost Variance) = EV − AC [USD]: negativo indica sobrecosto. Para "
            "ambos, el umbral de alerta es entre −50.000 y −1 USD, y crítico por debajo "
            "de −50.000 USD (umbrales configurables por proyecto). TCPI (To-Complete "
            "Performance Index) = (BAC−EV)/(BAC−AC): a diferencia de los demás índices "
            "es 'lower_better' — mide la eficiencia de costo que se necesita mantener "
            "en el trabajo restante para cumplir el presupuesto (BAC); valores ≤1.05 "
            "son alcanzables (verde), 1.051-1.10 es alerta (la meta se vuelve difícil), "
            ">1.10 es crítico (la meta de eficiencia es prácticamente inalcanzable con "
            "el desempeño actual)."
        ),
    },
    {
        "seccion": "EVM — Score compuesto y estimación del costo final (EAC)",
        "titulo": "Ponderación de los cuatro índices en un semáforo único y tres métodos de proyección EAC",
        "norma_ref": "PMI/PMBOK — Earned Value Management (EVM)",
        "contenido": (
            "El score compuesto 0-100 pondera los índices: CPI 30%, SPI 25%, QPI 25%, "
            "PPI 20%, cada uno normalizado a un techo de 1.2 (valores por encima de 1.2 "
            "no suman más score, evitando que un índice extremo distorsione el "
            "promedio). La Estimación al Completar (EAC) se calcula por tres métodos "
            "según el escenario: método 'cpi' (EAC = BAC/CPI, asume que el CPI actual "
            "se mantiene constante el resto del proyecto — el más usado cuando las "
            "desviaciones de costo son sistémicas); método 'bac' (EAC = AC + (BAC−EV), "
            "asume que el trabajo restante se hará a la tasa presupuestada — solo válido "
            "si la variación de costo actual fue atípica); método 'composite' (EAC = AC "
            "+ (BAC−EV)/(CPI×SPI_aprox), combina desempeño de costo y cronograma)."
        ),
    },
    {
        "seccion": "EVM — Análisis de trazabilidad cruzada de portafolio",
        "titulo": "Rankings entre proyectos, agregados de portafolio y generación automática de alertas",
        "norma_ref": "PMI/PMBOK — Earned Value Management (EVM), extensión de portafolio",
        "contenido": (
            "El análisis cruzado rankea todos los proyectos activos por CPI, SPI, QPI, "
            "PPI y score compuesto (1 = mejor desempeño), y calcula agregados de "
            "portafolio: promedio de cada índice, mejor/peor proyecto por índice, BAC "
            "total, EAC total, CV total y SV total sumados. Genera alertas automáticas: "
            "🔴 CRÍTICO si CPI<0.9 (sobrecoste severo, reporta el EAC estimado) o si "
            "SPI<0.9 (retraso severo de cronograma); 🟡 ALERTA si TCPI>1.1 (meta de "
            "eficiencia difícilmente alcanzable) o si QPI<0.9 (calidad bajo estándar)."
        ),
    },
    {
        "seccion": "ML predictivo — Regresión lineal y detección de anomalías",
        "titulo": "Ajuste de tendencia por mínimos cuadrados y detección de outliers por z-score",
        "norma_ref": "Estadística aplicada a series de tiempo de KPIs de proyecto (sin dependencias externas — regresión y estadística pura)",
        "contenido": (
            "La regresión lineal simple ajusta pendiente e intercepto por mínimos "
            "cuadrados ordinarios (slope = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²)) y reporta "
            "el coeficiente de determinación R² acotado entre 0 y 1. La detección de "
            "anomalías usa z-score: un punto de la serie se marca anómalo si "
            "|valor − media| / desviación_estándar supera el umbral (por defecto 2.0 "
            "desviaciones estándar); requiere al menos 3 observaciones en la serie para "
            "calcular desviación estándar de forma significativa."
        ),
    },
    {
        "seccion": "ML predictivo — Predicción de fecha de término por SPI",
        "titulo": "Duración revisada del proyecto y probabilidad de cumplir el plazo",
        "norma_ref": "Extensión predictiva sobre EVM (PMI/PMBOK) — proyección de cronograma",
        "contenido": (
            "La duración revisada del proyecto se estima como "
            "duración_planeada_meses / SPI_actual (si SPI<1, el proyecto tardará más "
            "de lo planeado; si SPI>1, terminará antes). El atraso proyectado en meses "
            "es el máximo entre 0 y (meses_restantes_revisados − meses_restantes_"
            "originales). La probabilidad de cumplir el plazo a tiempo se aproxima "
            "linealmente como SPI×100, acotada entre 0% y 100% — es una heurística "
            "simple, no un modelo probabilístico riguroso."
        ),
    },
    {
        "seccion": "ML predictivo — Score de riesgo compuesto del proyecto",
        "titulo": "Penalización por índice bajo umbral y por tendencia negativa, con factores explicativos",
        "norma_ref": "Extensión predictiva sobre EVM (PMI/PMBOK) — modelo de riesgo",
        "contenido": (
            "El score de riesgo (0-100, mayor es peor) requiere al menos 3 períodos de "
            "histórico; con menos datos retorna 50 ('Insuficientes datos'). Cada índice "
            "(CPI y SPI con umbral 1.0, QPI con 0.95, PPI con 0.90) aporta una "
            "penalización de 0 a 25 puntos, combinando qué tan por debajo del umbral "
            "está el valor actual más la pendiente de la tendencia reciente (regresión "
            "lineal de la serie); el score total es la suma de las cuatro "
            "penalizaciones (máximo 100). Clasificación: <20 🟢 bajo riesgo, <45 🟡 "
            "riesgo moderado, ≥45 🔴 alto riesgo. Los factores explicativos listan qué "
            "índice específico dispara el riesgo cuando su penalización individual "
            "supera 8-10 puntos."
        ),
    },
    {
        "seccion": "ML predictivo — Proyección de KPIs y correlación entre índices",
        "titulo": "Forecast de los próximos períodos por regresión lineal y matriz de correlación de Pearson",
        "norma_ref": "Extensión predictiva sobre EVM (PMI/PMBOK) — forecasting y análisis de correlación",
        "contenido": (
            "El forecast de KPIs proyecta CPI, SPI, QPI y PPI para los próximos "
            "períodos ajustando una regresión lineal sobre el histórico de cada índice "
            "(mínimo 3 snapshots) y acotando las predicciones entre 0.5 y 1.5 para "
            "evitar extrapolaciones no realistas; incluye el R² de cada ajuste como "
            "medida de confiabilidad de la proyección. La matriz de correlación de "
            "Pearson entre CPI, SPI, QPI y PPI (coeficiente entre -1 y 1) identifica "
            "qué índices se mueven juntos — por ejemplo, una fuerte correlación "
            "positiva entre CPI y PPI sugiere que los problemas de productividad son la "
            "causa raíz de los sobrecostos, más que factores externos de precio."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    todos = [("aquai", AQUAI_CHUNKS), ("geopot", GEOPOT_CHUNKS), ("vias", VIAS_CHUNKS), ("gerencia", GERENCIA_CHUNKS)]

    for motor, chunks in todos:
        if not chunks:
            continue

        borrado = sb.table("motor_chunks").delete().eq("motor", motor).execute()
        print(f"[{motor}] limpiados {len(borrado.data)} chunks previos")

        textos = [f"{c['titulo']}. {c['contenido']}" for c in chunks]
        embeddings = model.encode(textos, normalize_embeddings=True).tolist()

        rows = [
            {
                "motor": motor,
                "seccion": c["seccion"],
                "titulo": c["titulo"],
                "contenido": c["contenido"],
                "norma_ref": c["norma_ref"],
                "embedding": emb,
            }
            for c, emb in zip(chunks, embeddings)
        ]
        sb.table("motor_chunks").insert(rows).execute()
        print(f"[{motor}] insertados {len(rows)} chunks")

    print("Listo.")


if __name__ == "__main__":
    main()
