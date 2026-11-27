"""
Carga chunks de conocimiento específico de dominio (por motor) a Supabase
(motor_chunks), generando embeddings locales — mismo pipeline que
ingest_normativa.py (sentence-transformers, 384-dim).

A diferencia de ingest_normativa.py (que parsea documentos normativos
extraídos de Drive), estos chunks se redactan a mano a partir del código
YA PORTADO en packages/motor-*/src/ — fórmulas, tablas de referencia y
citas normativas que ya existen y están verificadas en el motor de cálculo,
no contenido inventado ni un documento normativo aparte.

Carga GeoPot, Vías y Gerencia, y los motores de chunks_motores_nuevos.py (geotecnia, pilotes,
acero frío, incendios). AquAI usa scripts/ingesta/ras2000/ingest_ras2000.py, que
extrae texto oficial real (Resolución 1096 de 2000) en vez de chunks
redactados a mano.

Uso:
  python scripts/ingesta/motores/ingest_motor_chunks.py            # simula (solo lee)
  python scripts/ingesta/motores/ingest_motor_chunks.py --aplicar  # escribe
  python scripts/ingesta/motores/ingest_motor_chunks.py --motor vias --aplicar

Reemplaza únicamente las filas de `motor_chunks` cuya `seccion` coincide con un
chunk de este archivo. Antes borraba todo `motor = X`, lo que en 'vias' se
llevaba los Manuales de Pavimentos INVIAS y las secciones INV E 2012 cargadas
por otros scripts.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]          # raíz del repo (scripts/ingesta/motores/este_archivo)

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


# AquAI ya no se carga desde este archivo: scripts/ingesta/ras2000/ingest_ras2000.py reemplazó
# estos 13 chunks redactados a mano por 303 chunks reales extraídos artículo
# por artículo del texto oficial de la Resolución 1096 de 2000 (RAS 2000
# Títulos A-H), con la misma trazabilidad que NSR-10/NTC/SGSST. Ver ese
# script para volver a cargar o actualizar el corpus de AquAI.


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
            "por pulgada de espesor, di: espesor en pulgadas = cm/2.54, mi: coeficiente "
            "de drenaje). Coeficientes estructurales: rodadura asfáltica a1=0.44, base "
            "granular a2=0.14, subbase granular a3=0.11. Coeficientes de drenaje según "
            "calidad: excelente 1.20, bueno 1.10, regular 1.00, pobre 0.90, muy pobre "
            "0.80 (el motor asume 'bueno' por defecto para base y subbase). La rodadura "
            "asfáltica mínima depende del tránsito en el carril de diseño: 5 cm hasta "
            "150 000 ejes y 7.5 cm hasta 500 000 (Manual INVIAS de bajos volúmenes); "
            "8 cm hasta 2 millones, 9 cm hasta 7 millones y 10.5 cm por encima "
            "(tabla de espesores mínimos de AASHTO-93: 3.0, 3.5 y 4.0 pulgadas). La "
            "base granular mínima es 15 cm y la subbase mínima 15 cm; máximos "
            "recomendados: rodadura 25 cm, base 40 cm, subbase 60 cm. La subbase es la "
            "capa variable que completa el SN y se redondea hacia arriba a 2.5 cm. Es "
            "un diseño preliminar que debe validar un ingeniero de pavimentos."
        ),
    },
    {
        "seccion": "AASHTO 93 adaptado — Diseño de pavimento de concreto (estructura rígida)",
        "titulo": "Espesor de losa con la ecuación AASHTO-93 de pavimento rígido y juntas",
        "norma_ref": "Guía AASHTO 1993 — ecuación de diseño de pavimento rígido",
        "contenido": (
            "El espesor de la losa de concreto D se despeja de la ecuación de diseño de "
            "pavimento rígido de la Guía AASHTO 1993: log10(W18) = ZR·So + "
            "7.35·log10(D+1) − 0.06 + log10(ΔPSI/3.0)/(1 + 1.624·10^7/(D+1)^8.46) + "
            "(4.22 − 0.32·pt)·log10[S'c·Cd·(D^0.75 − 1.132)/(215.63·J·(D^0.75 − "
            "18.42/(Ec/k)^0.25))], con D en pulgadas, S'c y Ec en psi y k en pci. "
            "Entradas obligatorias: k (módulo de reacción efectivo, MPa/m, por ejemplo "
            "con el ensayo de placa INV E-168) y S'c (módulo de rotura a 28 días, MPa, "
            "INV E-414); el motor no los supone. Por defecto: Ec = 27 580 MPa, J = 3.2 "
            "(dovelas), Cd = 1.0, So = 0.35, p0 = 4.5, pt = 2.5 y confiabilidad según "
            "el tipo de vía. La losa se redondea hacia arriba a 1 cm con mínimo de "
            "15 cm. El método reemplazó una conversión aproximada desde el SN que no "
            "tenía fuente (issue #106). Losas de 3.6 a 5.0 m de largo con relación largo/ancho entre "
            "1 y 1.3 (Manual INVIAS de pavimentos de concreto). Es un diseño "
            "preliminar: debe cotejarse con el catálogo del Manual INVIAS y validarlo "
            "un ingeniero de pavimentos."
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


TABLA = "motor_chunks"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from chunks_motores_nuevos import MOTORES_NUEVOS  # noqa: E402  (geotecnia, pilotes, acero frío, incendios, viento)

MOTORES = {"geopot": GEOPOT_CHUNKS, "vias": VIAS_CHUNKS, "gerencia": GERENCIA_CHUNKS, **MOTORES_NUEVOS}
_PAGINA = 1000
_LOTE_BORRADO = 200


def secciones_del_script(chunks: list[dict]) -> set[str]:
    """Secciones que este script escribe para un motor. Deben ser únicas: son
    la llave con la que se reconoce qué filas son "nuestras" al reemplazar."""
    secciones = [c["seccion"] for c in chunks]
    repetidas = sorted({s for s in secciones if secciones.count(s) > 1})
    if repetidas:
        raise ValueError(f"secciones repetidas en el script: {repetidas}")
    return set(secciones)


def filas_del_motor(sb, motor: str) -> list[dict]:
    """Todas las filas (id, seccion) del motor, paginadas. Solo lectura.

    El filtro por sección se hace aquí en Python y no con `.in_()` en
    PostgREST: las secciones llevan comas, puntos y paréntesis, que rompen el
    filtro `in.(...)` si no se escapan."""
    filas: list[dict] = []
    ini = 0
    while True:
        r = (sb.table(TABLA).select("id,seccion").eq("motor", motor)
             .order("id").range(ini, ini + _PAGINA - 1).execute().data)
        filas += r
        ini += _PAGINA
        if len(r) < _PAGINA:
            return filas


def planificar(sb, motor: str, chunks: list[dict]) -> dict:
    """Qué haría el script con un motor, sin escribir nada.

    Solo se reemplazan las filas cuya `seccion` está en la lista de chunks de
    este archivo. El resto del motor (Manuales de Pavimentos INVIAS, secciones
    INV E 2012 del PR #298, lo que otro script haya cargado) se conserva."""
    propias = secciones_del_script(chunks)
    filas = filas_del_motor(sb, motor)
    ids_a_borrar = [f["id"] for f in filas if f["seccion"] in propias]
    return {
        "motor": motor,
        "filas_motor": len(filas),
        "ids_a_borrar": ids_a_borrar,
        "conservadas": len(filas) - len(ids_a_borrar),
        "a_insertar": len(chunks),
    }


def imprimir_plan(plan: dict) -> None:
    print(
        f"[{plan['motor']}] filas actuales del motor: {plan['filas_motor']} | "
        f"se borrarían {len(plan['ids_a_borrar'])} (secciones de este script) | "
        f"se conservan {plan['conservadas']} (cargadas por otros scripts) | "
        f"se insertarían {plan['a_insertar']}"
    )


def aplicar(sb, model, plan: dict, chunks: list[dict]) -> None:
    """Inserta primero y borra después, solo por id: si la inserción falla,
    los chunks previos siguen en la tabla. Nunca borra por `motor` a secas."""
    motor = plan["motor"]
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
    sb.table(TABLA).insert(rows).execute()
    print(f"[{motor}] insertados {len(rows)} chunks")

    ids = plan["ids_a_borrar"]
    for i in range(0, len(ids), _LOTE_BORRADO):
        sb.table(TABLA).delete().in_("id", ids[i:i + _LOTE_BORRADO]).execute()
    print(f"[{motor}] borrados {len(ids)} chunks previos de este script; "
          f"{plan['conservadas']} de otros scripts intactos")


def _argumentos(argv: list[str] | None):
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe en Supabase; sin este flag solo simula (lectura)")
    ap.add_argument("--motor", choices=sorted(MOTORES), action="append",
                    help="limita a uno o más motores (por defecto, todos)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None, sb=None, model=None):
    args = _argumentos(argv)
    motores = args.motor or list(MOTORES)

    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    # AquAI se carga aparte con scripts/ingesta/ras2000/ingest_ras2000.py (corpus real RAS 2000)
    planes = [(planificar(sb, m, MOTORES[m]), MOTORES[m]) for m in motores if MOTORES[m]]
    for plan, _ in planes:
        imprimir_plan(plan)

    if not args.aplicar:
        print("Simulación: no se escribió nada. Repetir con --aplicar para ejecutar.")
        return planes

    if model is None:
        from sentence_transformers import SentenceTransformer
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        print("Cargando modelo de embeddings local...")
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    for plan, chunks in planes:
        aplicar(sb, model, plan, chunks)
    print("Listo.")
    return planes


if __name__ == "__main__":
    main()
