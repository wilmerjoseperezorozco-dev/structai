"""Chunks de conocimiento de los motores agregados en nov. 2026: geotecnia (#136), pilotes (#118), acero formado en frío
(#81), protección contra incendio (#336) y viento (#242/#292).

Mismo criterio que ingest_motor_chunks.py: se redactan a mano a partir del código YA verificado en packages/motor-*/src/
(fórmulas, numerales, alcance y lo que el motor NO hace). No se copia texto de la NSR-10, del CCP-14 ni de NFPA: solo
números, ecuaciones y numerales, como en el código. Cada motor tiene un chunk de alcance que dice si está disponible en la
plataforma (endpoint de la API) o si es «próximamente»: no se anuncia lo que no existe.

Al cambiar un motor, actualizar aquí lo que cambie. La llave es `seccion`: única por motor.
"""
from __future__ import annotations

AVISO = ("El resultado es una referencia técnica: no aprueba el diseño ni reemplaza el estudio, el diseño y la firma de "
         "un ingeniero matriculado.")

# ─── Geotecnia — cimentaciones superficiales, NSR-10 Título H ────────────────────────────────────────────────────────
# Fuente: packages/motor-geotecnia/src/{consolidacion,inmediato,esfuerzos,multicapa,montecarlo,portante,contrato_api}.py

GEOTECNIA_CHUNKS: list[dict] = [
    {
        "seccion": "StructAI geotecnia — alcance y endpoints",
        "titulo": "Qué calcula el motor de geotecnia de StructAI (cimentaciones superficiales, NSR-10 Título H)",
        "norma_ref": "NSR-10 Título H (H.4.7, H.4.8, H.4.9, H.4.10) · motor-geotecnia StructAI",
        "contenido": (
            "El motor de geotecnia de StructAI calcula, para cimentaciones superficiales: asentamiento por consolidación "
            "primaria y su evolución en el tiempo (POST /geotecnia/asentamiento); asentamiento total a 20 años, suma de "
            "inmediato, consolidación y secundario (POST /geotecnia/asentamiento-total, H.4.8.4 y H.4.9.2); asentamiento "
            "diferencial y giro (POST /geotecnia/diferencial, Tabla H.4.9-1 y H.4.9.4); consolidación multicapa "
            "(POST /geotecnia/multicapa); Monte Carlo del asentamiento con Cc y e0 inciertos "
            "(POST /geotecnia/asentamiento-montecarlo); y capacidad portante de Vesić, centrada "
            "(POST /geotecnia/portante) o con excentricidad e inclinación (POST /geotecnia/portante-excentrica, H.4.10, "
            "factores de seguridad de la Tabla H.4.7-1). Todos los parámetros físicos son obligatorios: el motor no "
            "supone valores del suelo. No calcula estabilidad de taludes, empujes sobre muros ni licuación (esta última "
            "está en el motor de licuación). " + AVISO
        ),
    },
    {
        "seccion": "StructAI geotecnia — consolidación primaria de Terzaghi",
        "titulo": "Asentamiento por consolidación primaria con ramal de recompresión y tiempo de consolidación",
        "norma_ref": "NSR-10 H.4.9 · Terzaghi (1943) · motor-geotecnia StructAI",
        "contenido": (
            "Asentamiento primario de un estrato de arcilla: Sc = Cc·H/(1+e0)·log10(σ'f/σ'0) en arcilla normalmente "
            "consolidada. Si σ'0 está por debajo de la presión de preconsolidación σ'p, el tramo hasta σ'p usa el índice "
            "de recompresión Cr: Sc = Cr·H/(1+e0)·log10(σ'p/σ'0) + Cc·H/(1+e0)·log10(σ'f/σ'p) cuando σ'f supera σ'p. "
            "El grado medio de consolidación U(Tv) es el de Terzaghi para drenaje doble o simple, con Tv = cv·t/Hdr² y "
            "Hdr la trayectoria de drenaje (mitad del espesor con drenaje doble, espesor completo con drenaje simple). "
            "El tiempo para un grado U dado (0 < U < 1) se obtiene resolviendo U(Tv) = U numéricamente. Los límites "
            "admisibles de asentamiento son los del numeral H.4.9 de la NSR-10."
        ),
    },
    {
        "seccion": "StructAI geotecnia — asentamiento total a 20 años",
        "titulo": "Asentamiento total: inmediato elástico + consolidación + compresión secundaria",
        "norma_ref": "NSR-10 H.4.8.4 y H.4.9.2 · motor-geotecnia StructAI",
        "contenido": (
            "StructAI suma tres componentes y compara con el límite de H.4.9.2: S(20 años) = Si + Σ U(20 años)·Sc,i + "
            "Σ Ss,i. El inmediato Si es el de un semiespacio elástico bajo un área rectangular flexible uniformemente "
            "cargada (Timoshenko y Goodier; Harr), en el centro o en la esquina de la zapata B×L. La consolidación de "
            "cada estrato se multiplica por el grado de consolidación alcanzado a los 20 años. La compresión secundaria "
            "es Ss = Cα·H/(1+e0)·log10(t/tp), entre el fin de la primaria tp y el horizonte t. Los incrementos de "
            "esfuerzo bajo la zapata salen de Boussinesq (solución de Newmark para la esquina de un rectángulo y "
            "superposición de cuatro esquinas para el centro) o del método 2:1 (pendiente 2V:1H). El esfuerzo efectivo "
            "geostático usa γ sobre el nivel freático y γ' = γsat − γw bajo él."
        ),
    },
    {
        "seccion": "StructAI geotecnia — asentamiento diferencial y giro",
        "titulo": "Asentamiento diferencial entre apoyos contiguos y giro de cuerpo rígido",
        "norma_ref": "NSR-10 Tabla H.4.9-1 y H.4.9.4 · motor-geotecnia StructAI",
        "contenido": (
            "El motor compara la diferencia de asentamiento Δ entre apoyos contiguos separados una distancia ℓ con el "
            "límite ℓ/divisor de la Tabla H.4.9-1 de la NSR-10, donde el divisor depende del tipo de construcción. "
            "Además compara el giro de cuerpo rígido de la estructura con 1/250 (H.4.9.4)."
        ),
    },
    {
        "seccion": "StructAI geotecnia — consolidación multicapa",
        "titulo": "Consolidación unidimensional en suelos estratificados con integración exacta en el tiempo",
        "norma_ref": "NSR-10 H.4.8.2 y H.4.9 · Terzaghi (1943) · motor-geotecnia StructAI",
        "contenido": (
            "Para perfiles con varias capas de distinto cv y mv, StructAI resuelve mv·∂u/∂t = ∂/∂z(cv·mv·∂u/∂z), con u "
            "el exceso de presión de poros. Discretiza en celdas (volúmenes finitos) y resuelve el sistema C·u' = −K·u "
            "por descomposición espectral: no hay error de paso de tiempo, solo error espacial. La carga es instantánea "
            "(u inicial igual al Δσ de cada capa). Entrega el grado de consolidación y el asentamiento en función del "
            "tiempo. Cada capa requiere espesor, cv (m²/día), mv (1/kPa) y Δσ (kPa)."
        ),
    },
    {
        "seccion": "StructAI geotecnia — Monte Carlo del asentamiento",
        "titulo": "Asentamiento con incertidumbre: Cc y e0 lognormales y probabilidad de superar el límite",
        "norma_ref": "NSR-10 H.4.9.2 · motor-geotecnia StructAI",
        "contenido": (
            "El asentamiento primario puede simularse con Cc y e0 inciertos, cada uno lognormal definido por su mediana "
            "y su coeficiente de variación, con correlación opcional mediante cópula gaussiana. En cada muestra Cr se "
            "acota a Cr ≤ Cc. El resultado trae estadísticos del asentamiento y la probabilidad de que supere el límite "
            "declarado, P(S > límite). La semilla es explícita, así que la simulación es reproducible."
        ),
    },
    {
        "seccion": "StructAI geotecnia — capacidad portante de Vesić",
        "titulo": "Capacidad portante de zapatas con la ecuación general de Vesić",
        "norma_ref": "NSR-10 H.4.2.3 y Tabla H.4.7-1 · Vesić (1973) · motor-geotecnia StructAI",
        "contenido": (
            "q_ult = c·Nc·sc·dc·ic + q·Nq·sq·dq·iq + ½·γ'·B'·Nγ·sγ·iγ, con los factores de capacidad, forma y "
            "profundidad de Vesić (Nc tiende a π+2 cuando φ tiende a 0). Sirve para zapata aislada B×L o corrida (por "
            "metro). El Título H de la NSR-10 no entrega una fórmula de capacidad portante: StructAI usa la teoría "
            "clásica y el resultado no sustituye el estudio geotécnico que exige H.4.2.3. La capacidad admisible se "
            "obtiene con los factores de seguridad de la Tabla H.4.7-1."
        ),
    },
    {
        "seccion": "StructAI geotecnia — portante con excentricidad e inclinación",
        "titulo": "Capacidad portante con carga excéntrica e inclinada: área efectiva de Meyerhof y factores de Vesić",
        "norma_ref": "NSR-10 H.4.10 · Meyerhof · Vesić (1975) · motor-geotecnia StructAI",
        "contenido": (
            "H.4.10 obliga a considerar la excentricidad en la capacidad ante falla. StructAI usa el área efectiva de "
            "Meyerhof, B' = B − 2·eB y L' = L − 2·eL, y para una carga horizontal H en la dirección de B los factores de "
            "inclinación de Vesić (1975): m = (2 + B'/L')/(1 + B'/L'); iq = [1 − H/(V + A'·c·cot φ)]^m; "
            "iγ = [1 − H/(V + A'·c·cot φ)]^(m+1); ic = iq − (1 − iq)/(Nc·tan φ) si φ > 0, o ic = 1 − m·H/(A'·c·Nc) si "
            "φ = 0. Los factores de profundidad usan el B real (Df/B) y los de forma, B'/L'. Devuelve la carga última "
            "en kN (kN/m en zapata corrida)."
        ),
    },
]

# ─── Pilotes — capacidad axial y asentamiento, NSR-10 H.4 y CCP-14 Sección 10 ────────────────────────────────────────
# Fuente: packages/motor-pilotes/src/{axial,arena_spt,mixto,grupo,asentamiento,contrato_api}.py

PILOTES_CHUNKS: list[dict] = [
    {
        "seccion": "StructAI pilotes — alcance y endpoints",
        "titulo": "Qué calcula el motor de pilotes de StructAI",
        "norma_ref": "NSR-10 H.4.4 y H.4.7 · CCP-14 Sección 10 · motor-pilotes StructAI",
        "contenido": (
            "El motor de pilotes calcula la capacidad axial a compresión de un pilote individual y de un grupo "
            "(POST /pilotes/capacidad, NSR-10 H.4.4.1 y H.4.7) y el asentamiento de un grupo por el método de la "
            "zapata equivalente (POST /pilotes/asentamiento, H.4.4.2 y H.4.9.2). Admite arcilla (no drenado), suelo "
            "drenado con K y φ', suelo granular con SPT (métodos del CCP-14) y perfiles mixtos con estratos de distinto "
            "tipo. Fricción y punta se evalúan por separado, cada una con su factor de seguridad. Quedan próximamente: "
            "capacidad en roca, el método de Nordlund/Thurman, geomateriales intermedios (N60 > 50) y el bloque en "
            "suelo drenado. No calcula fricción negativa ni capacidad ante carga lateral. " + AVISO
        ),
    },
    {
        "seccion": "StructAI pilotes — capacidad axial NSR-10 H.4.7",
        "titulo": "Capacidad axial de un pilote: fricción drenada y no drenada y punta",
        "norma_ref": "NSR-10 H.4.7-2, H.4.7-3, Tabla H.2.4-1 y Tabla H.4.7-1 · Skempton (1951)",
        "contenido": (
            "Fricción en suelo drenado (H.4.7-2): τF = c' + K·σ'v·tan φ' y la fricción de diseño τL = 2/3·τF. Fricción "
            "en suelo no drenado (H.4.7-3): τL = α·Su con α = 0,2 + 0,8·exp[0,35 − 2·Su/PA] ≤ 1,0, PA la presión "
            "atmosférica. La capacidad admisible por fricción es Σ τL·p·Δz / FS, con el factor de seguridad de la "
            "Tabla H.2.4-1; σ'v se integra de forma continua en todo el perfil. La NSR-10 no da fórmula de resistencia "
            "por punta: en arcilla StructAI usa qp,ult = 9·Su (Skempton, 1951); en suelo drenado la punta debe venir del "
            "estudio geotécnico o, con SPT, del CCP-14. La punta admisible usa el factor de seguridad de la "
            "Tabla H.4.7-1."
        ),
    },
    {
        "seccion": "StructAI pilotes — suelo granular con SPT (CCP-14)",
        "titulo": "Pilotes hincados (Meyerhof) y pilas excavadas (método β) en arena con SPT",
        "norma_ref": "CCP-14 §10.4.6.2.4, §10.7.3.8.6g y §10.8.3.5.2 · motor-pilotes StructAI",
        "contenido": (
            "Corrección por sobrecarga: N1 = CN·N con CN = 0,77·log10(1,92/σ'v[MPa]) ≤ 2,0. Pilote hincado (Meyerhof): "
            "punta qp = 0,038·N1_60·Db/D ≤ qℓ, con qℓ = 0,4·N1_60 MPa en arena y 0,3·N1_60 en limo no plástico; fuste "
            "qs = 0,0019·N̄1_60 MPa en pilotes de desplazamiento. Pila excavada, método β: qs = β·σ'v ≤ 0,19 MPa, con "
            "β = 1,5 − 7,7e-3·√z en arena con N60 ≥ 15 (z en mm), multiplicado por N60/15 si N60 < 15, y "
            "β = 2,0 − 0,00082·z^0,75 en grava, con los límites de β de la norma; punta qp = 0,057·N60 MPa ≤ 3,0 MPa "
            "para N60 ≤ 50. StructAI documenta dos erratas del CCP-14 en estas ecuaciones (el límite de punta en SI y la "
            "punta de pilas excavadas) y usa la forma dimensionalmente correcta de AASHTO LRFD. Como el CCP-14 es LRFD, "
            "la capacidad admisible usa los factores de seguridad de la NSR-10 para mantener un solo criterio."
        ),
    },
    {
        "seccion": "StructAI pilotes — perfiles mixtos",
        "titulo": "Pilote en perfil con capas de arcilla y arena alternadas",
        "norma_ref": "NSR-10 H.4.7 · CCP-14 §10.7.3.8.6g y §10.8.3.5.2 · motor-pilotes StructAI",
        "contenido": (
            "Caso típico de la llanura del Cauca, la Costa Caribe o el aluvial de Bogotá: capas de arcilla y de arena en "
            "el mismo fuste. StructAI evalúa cada estrato con su método y su factor de seguridad: arcilla con α·Su "
            "(H.4.7-3), suelo drenado con 2/3·(c' + K·σ'v·tan φ') (H.4.7-2) y suelo granular con SPT por Meyerhof o β "
            "(CCP-14). La punta depende del estrato de apoyo. En Meyerhof, Db es la penetración dentro del estrato "
            "granular de apoyo: lo que el pilote atraviesa en arcilla no cuenta como empotramiento."
        ),
    },
    {
        "seccion": "StructAI pilotes — grupo de pilotes",
        "titulo": "Capacidad de un grupo de pilotes: suma, bloque y eficiencia",
        "norma_ref": "NSR-10 H.4.4.1 b · Converse-Labarre · Terzaghi y Peck · Skempton (1951)",
        "contenido": (
            "Según H.4.4.1 b, la carga de falla del grupo es la menor entre la suma de las capacidades individuales, la "
            "de un bloque de terreno con la envolvente del grupo y la suma con la posible reducción por eficiencia. "
            "Eficiencia de Converse-Labarre: E = 1 − θ·[(n−1)·m + (m−1)·n]/(90·m·n), θ = atan(D/s) en grados; StructAI "
            "solo la aplica si el ingeniero la pide. Bloque en arcilla: Qb = 2(Bg+Lg)·Σ Su·Δz + Bg·Lg·Nc·Su,punta, con "
            "Nc = 5(1 + 0,2·L/Bg)(1 + 0,2·Bg/Lg) si L/Bg ≤ 2,5 y 7,5(1 + 0,2·Bg/Lg) si no. La NSR-10 no da estas "
            "fórmulas: son las convencionales que pide H.4.4."
        ),
    },
    {
        "seccion": "StructAI pilotes — asentamiento de grupo",
        "titulo": "Asentamiento de un grupo de pilotes por zapata equivalente",
        "norma_ref": "NSR-10 H.4.4.2 · CCP-14 §10.7.2.3 · Meyerhof (1976) · motor-pilotes StructAI",
        "contenido": (
            "La NSR-10 (H.4.4.2) pide estimar el asentamiento con la deformación del pilote y del suelo bajo la punta, "
            "sin fijar fórmulas; StructAI sigue el CCP-14. La zapata equivalente tiene la planta del perímetro exterior "
            "del grupo, a la profundidad (L − Db) + f·Db, con f = 1 para pilotes de punta, 2/3 para fricción en arcilla, "
            "8/9 para fricción en arena sobre arcilla y 2/3 para perfiles por capas. La presión se reparte 2V:1H. En "
            "suelo cohesivo se calcula la consolidación primaria de cada estrato; en suelo granular, "
            "ρ[mm] = 30·q·I·√B/N1_60 (q en MPa, B en mm, I = 1 − 0,125·D'/B ≥ 0,5, D' = 2/3·Db). Se suma el "
            "acortamiento elástico del fuste δe = Q·L/(A·Ep) con la carga completa en toda la longitud, que es una cota "
            "superior."
        ),
    },
]

# ─── Acero formado en frío — perfil C, NSR-10 Capítulo F.4 ───────────────────────────────────────────────────────────
# Fuente: packages/motor-acero-frio/src/{ancho_efectivo,elementos,flexion,distorsional,miembros,combinada,arrugamiento,
#         seccion,contrato_api}.py

ACERO_FRIO_CHUNKS: list[dict] = [
    {
        "seccion": "StructAI acero formado en frío — alcance y endpoints",
        "titulo": "Qué calcula el motor de acero formado en frío de StructAI (perfil C, NSR-10 F.4)",
        "norma_ref": "NSR-10 Capítulo F.4 · motor-acero-frio StructAI",
        "contenido": (
            "El motor verifica perfiles C formados en frío, con o sin pestaña, según NSR-10 F.4: propiedades brutas y "
            "sectoriales (POST /acero-frio/perfil-c/propiedades); flexión con los tres estados límite, sección, pandeo "
            "lateral-torsional y distorsional (/perfil-c/flexion); viga con flexión, cortante e interacción "
            "(/perfil-c/viga); compresión (/perfil-c/compresion); tensión (/perfil-c/tension); flexocompresión y "
            "flexotensión alrededor del eje fuerte (/perfil-c/flexocompresion, /perfil-c/flexotension) y arrugamiento "
            "del alma (/perfil-c/arrugamiento). Supuestos: método lineal de línea media, esquinas rectas (radio interior "
            "0) y elementos en tensión totalmente efectivos. No calcula todavía secciones Z, ángulos ni la flexión "
            "alrededor del eje débil, ni conexiones (F.4.5). E = 203 000 MPa (F.4.4.6.1.3) y μ = 0,3 son los únicos "
            "valores por defecto, porque los fija la norma. " + AVISO
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — ancho efectivo de Winter",
        "titulo": "Ancho efectivo de elementos en compresión (método de Winter)",
        "norma_ref": "NSR-10 F.4.2.2 y F.4.2.3.1 · motor-acero-frio StructAI",
        "contenido": (
            "Para un elemento plano de ancho w y espesor t con esfuerzo de compresión f: Fcr = k·π²·E/[12·(1 − μ²)·(w/t)²] "
            "(F.4.2.2-5) y λ = √(f/Fcr) (F.4.2.2-4). Si λ ≤ 0,673 el elemento es totalmente efectivo, b = w (F.4.2.2-1); "
            "si λ > 0,673, b = ρ·w (F.4.2.2-2) con ρ = (1 − 0,22/λ)/λ (F.4.2.2-3). k = 4 en elementos rigidizados (el "
            "alma de una C) y k = 0,43 en no rigidizados (el ala de una C sin pestaña). Con E se usa 203 000 MPa, el "
            "valor que fija el propio F.4, no 200 000 MPa. El cálculo de diseño es iterativo, porque f depende de la "
            "sección efectiva: StructAI resuelve ese punto fijo con un método de raíces, no con pasos fijos."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — anchos efectivos bajo gradiente y aleta con pestaña",
        "titulo": "Alma con gradiente de esfuerzos, elementos no rigidizados y aleta con pestaña",
        "norma_ref": "NSR-10 F.4.2.2.3, F.4.2.3.2 y F.4.2.4 · motor-acero-frio StructAI",
        "contenido": (
            "El alma bajo gradiente de esfuerzos se trata con F.4.2.2.3(a), con f1 en el borde más comprimido y f2 con "
            "signo (negativo en tensión). Los elementos no rigidizados con gradiente usan F.4.2.3.2: con ambos bordes "
            "comprimidos k = 0,578/(ψ + 0,34) (F.4.2.3-2). La aleta con pestaña a 90° se trata con F.4.2.4(a). StructAI "
            "documenta dos lecturas de transcripción: en F.4.2.2-19 la variable despejada es b2, y en F.4.2.3-1 se usa "
            "ψ = |f2/f1| entre 0 y 1, porque la otra lectura daría un k menor que el de compresión uniforme, lo cual es "
            "físicamente imposible."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — flexión: sección y pandeo lateral-torsional",
        "titulo": "Resistencia a flexión de un perfil C: sección efectiva y pandeo lateral-torsional",
        "norma_ref": "NSR-10 F.4.3.3.1.1 y F.4.3.3.1.2.1 · motor-acero-frio StructAI",
        "contenido": (
            "Resistencia de la sección (Procedimiento 1): Mn = Se·Fy (F.4.3.3-1), flexión alrededor del eje fuerte con "
            "la aleta superior comprimida. Se sale de la sección efectiva, cuyo eje neutro depende de los anchos "
            "efectivos; StructAI lo resuelve como un punto fijo. Pandeo lateral-torsional: Mn = Sc·Fc (F.4.3.3-7), con "
            "Fe = Cb·ro·A·√(σey·σt)/Sf (F.4.3.3-10) y G = E/(2(1+μ)). Cb = 12,5·Mmax/(2,5·Mmax + 3MA + 4MB + 3MC) "
            "(F.4.3.3-12); puede tomarse 1, y en voladizos con el extremo libre sin arriostrar debe ser 1. La resistencia "
            "de diseño es la menor entre sección, lateral-torsional y distorsional."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — pandeo distorsional",
        "titulo": "Pandeo distorsional de perfiles C con pestaña (método general)",
        "norma_ref": "NSR-10 F.4.3.3.1.4(b) y F.4.3.4.2(b) · AISI S100-07 · motor-acero-frio StructAI",
        "contenido": (
            "StructAI usa el método general (b) y no el simplificado (a), porque (a) excluye la pestaña a 90°. En "
            "flexión, Mn distorsional sale de F.4.3.3-28/-29 con My = Sfy·Fy y Mcrd = Sf·Fd; en compresión, Pn sale de "
            "F.4.3.4-12/-13 con Py = Ag·Fy y Fd sin el factor β. El factor de gradiente de momento en flexión es "
            "1,0 ≤ 1 + 0,4·(L/Lm)^0,7·(1 + M1/M2)^0,7 ≤ 1,3 (F.4.3.3-38) y puede tomarse 1,0. kφ = 0 cuando la aleta "
            "comprimida no tiene restricción rotacional. Al cotejar con la NSR-10 impresa se encontraron cuatro "
            "diferencias con la transcripción del corpus (en F.4.3.3-38, -39, -41 y F.4.3.4-21) y una errata de "
            "traducción en las definiciones de xo y hx; el motor sigue la impresa y las definiciones de AISI S100-07."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — tensión, cortante y compresión",
        "titulo": "Resistencia a tensión, cortante y compresión de miembros formados en frío",
        "norma_ref": "NSR-10 F.4.3.2, F.4.3.3.2.1 y F.4.3.4.1 · motor-acero-frio StructAI",
        "contenido": (
            "Tensión: fluencia Tn = Ag·Fy con φ = 0,90 (F.4.3.2-1) y rotura Tn = An·Fu con φ = 0,75 (F.4.3.2-2); el área "
            "neta An es obligatoria, no se supone igual a Ag, y la rotura en la conexión (F.4.5) no se verifica. "
            "Cortante: Vn = Aw·Fv (F.4.3.3-44) con Aw = h·t, kv = 5,34 sin rigidizadores. Compresión: Pn = Ae·Fn "
            "(F.4.3.4-1), Fn por F.4.3.4-2 si λc ≤ 1,5 o F.4.3.4-3 si λc > 1,5, con λc = √(Fy/Fe); Fe es el menor entre "
            "pandeo flector alrededor del eje débil (F.4.3.4-5) y flexo-torsional (F.4.3.4-6, β = 1 − (xo/ro)²). El "
            "pandeo distorsional en compresión se verifica aparte."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — carga axial y momento combinados",
        "titulo": "Flexocompresión, flexotensión e interacción flexión-cortante",
        "norma_ref": "NSR-10 F.4.3.5 y F.4.3.3-54 · motor-acero-frio StructAI",
        "contenido": (
            "Flexocompresión con F.4.3.5-4 y -5 (o -6 si P̄/φcPn ≤ 0,15), con αx = 1 − P̄/PEX > 0 (F.4.3.5-7); cada razón "
            "individual tampoco puede pasar de 1. Cm: 0,85 en pórticos con traslación; 0,6 − 0,4·M1/M2 en arriostrados "
            "sin carga transversal (F.4.3.5-11); con carga transversal, 0,85 o 1,0 según los extremos. Flexotensión con "
            "F.4.3.5-1 y -2, φt = 0,95. Viga: √[(Mu/φbMnxo)² + (Vu/φvVn)²] ≤ 1,0 (F.4.3.3-54) en almas no reforzadas. "
            "Hoy solo se considera la flexión alrededor del eje fuerte: el término del eje débil se toma nulo y así se "
            "declara."
        ),
    },
    {
        "seccion": "StructAI acero formado en frío — arrugamiento del alma",
        "titulo": "Arrugamiento del alma bajo cargas concentradas y su interacción con la flexión",
        "norma_ref": "NSR-10 F.4.3.3.4.1, F.4.3.3.5.1(a) y Tabla F.4.3.3-2 · motor-acero-frio StructAI",
        "contenido": (
            "Pn = C·t²·Fy·sen θ·(1 − CR·√(R/t))·(1 + CN·√(N/t))·(1 − Ch·√(h/t)) (F.4.3.3-56), con h la porción plana "
            "del alma, R el radio interior de doblez y N la longitud de apoyo. Los coeficientes C, CR, CN, Ch y φw salen "
            "de la Tabla F.4.3.3-2 según el apoyo (sujeto o no), la aleta (rigidizada o no), la carga (una o dos aletas) "
            "y la posición (extremo o interior); la condición de la aleta se deduce de la geometría. Interacción con la "
            "flexión en almas sencillas no reforzadas: 0,91·(P̄/Pn) + M̄/Mnxo ≤ 1,33·φ con φ = 0,90 (F.4.3.3-61)."
        ),
    },
]

# ─── Protección contra incendio — #336 (código listo, plataforma: próximamente) ──────────────────────────────────────
# Fuente: packages/motor-incendios/src/{requisitos,rociadores,trazado,hidraulica,diametros,bombas,soportes,presupuesto}.py

INCENDIOS_CHUNKS: list[dict] = [
    {
        "seccion": "StructAI protección contra incendio — alcance y disponibilidad",
        "titulo": "Qué hace el motor de protección contra incendio de StructAI y qué no",
        "norma_ref": "NSR-10 Título J y A.9 · motor-incendios StructAI (próximamente en la plataforma)",
        "contenido": (
            "El motor de protección contra incendio de StructAI está implementado y probado, pero todavía no está "
            "disponible en la plataforma: próximamente. Cubre: requisitos de la NSR-10 (categoría de riesgo, horas de "
            "resistencia al fuego y sistemas exigidos), ubicación de rociadores, trazado de la tubería esquivando vigas "
            "y ductos, cálculo hidráulico, optimización de diámetros con el tanque, cuarto de bombas, soportes "
            "sismorresistentes y presupuesto. La NSR-10 decide cuándo se exige un sistema; cómo se diseña (NFPA 13, 14, "
            "20, NTC 2301 y otras) entra como criterios del proyecto que el diseñador declara con su fuente: el motor no "
            "trae valores de esas normas. No aprueba el diseño: la firma es del ingeniero responsable y la revisión, de "
            "los bomberos (Ley 1575 de 2012). " + AVISO
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — requisitos NSR-10 Título J",
        "titulo": "Categoría de riesgo, resistencia al fuego y sistemas exigidos según el Título J",
        "norma_ref": "NSR-10 J.3.3, J.3.3.3, J.3.4-3, J.3.5 y J.4.3",
        "contenido": (
            "Con el grupo y subgrupo de ocupación que declara el usuario (Título K), el motor determina la categoría de "
            "riesgo I, II o III (J.3.3), las exenciones de cuantificar la resistencia al fuego (J.3.3.3), las horas de "
            "resistencia por tipo de elemento (Tabla J.3.4-3), la verificación de dimensiones y recubrimientos de "
            "elementos de concreto (J.3.5) y los sistemas de extinción exigidos (J.4.3; en ocupación mixta, la unión de "
            "las exigencias de cada uso). Las filas de las tablas cuya lectura del PDF es ambigua quedan sin valor hasta "
            "verificarlas, y con ellas el motor no clasifica. Las interpretaciones se declaran: por ejemplo, «más de N "
            "pisos o H m de altura» se aplica con la lectura más exigente."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — ubicación de rociadores y trazado",
        "titulo": "Malla de rociadores por paño y trazado de tubería que esquiva obstáculos",
        "norma_ref": "motor-incendios StructAI · criterios del proyecto (NFPA 13 / NTC 2301 declarados por el diseñador)",
        "contenido": (
            "Rociadores: en cada paño de techo entre vigas se busca la malla uniforme con el menor número de rociadores "
            "que cumple los criterios declarados (separación máxima y mínima, distancia a muros, área máxima por "
            "rociador, deflector). Se informa también la cota inferior ceil(área/área máxima). Los rociadores con un "
            "obstáculo debajo quedan señalados para revisión: la versión actual no aplica las reglas de obstrucción. "
            "Trazado: árbol de Steiner rectilíneo en 3D sobre una rejilla de Hanan extendida, con la heurística del "
            "camino más corto (Takahashi y Matsuyama, costo ≤ 2·(1 − 1/T) veces el óptimo en la rejilla), repetida desde "
            "varias raíces. Cada tramo se revisa contra vigas, columnas y ductos con la holgura declarada, y la tubería "
            "solo cruza losas por los pases declarados."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — cálculo hidráulico",
        "titulo": "Cálculo hidráulico de la red de rociadores con Hazen-Williams",
        "norma_ref": "motor-incendios StructAI · Hazen-Williams · Q = K·√P",
        "contenido": (
            "Pérdidas por Hazen-Williams en SI: hf[m] = 10,67·L·Q^1,852/(C^1,852·d^4,8704), Q en m³/s y d interior en m; "
            "presión estática ΔP = γ·Δz; descarga del rociador Q = K·√P (K en L/(min·√bar)). Como la red es un árbol, "
            "el caudal de cada tramo es exacto. Las presiones de los rociadores que operan se resuelven por Newton con "
            "jacobiano analítico; el rociador más exigido fija su presión mínima y, si otro queda por debajo, pasa a "
            "gobernar. Los accesorios (codos y tees laterales) suman su longitud equivalente declarada. Una revisión "
            "independiente comprueba presión en cada rociador, balance de caudal en cada nodo, energía tramo a tramo y "
            "velocidad máxima. K, presión y caudal mínimos, C y el área de diseño son datos del proyecto."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — diámetros y tanque subterráneo",
        "titulo": "Optimización de diámetros comerciales teniendo en cuenta el tanque y la bomba",
        "norma_ref": "motor-incendios StructAI",
        "contenido": (
            "Minimiza costo = Σ L·c(d) + costo_m³·V con velocidad máxima en cada tramo, presión mínima en cada rociador, "
            "volumen requerido (caudal de rociadores más mangueras por la duración) ≤ volumen útil del tanque si ya "
            "existe, y presión de bomba P = P_alim + γ·(z_alim − z_agua_mín) + pérdidas de succión ≤ máximo si se "
            "declara. Los diámetros importan para el tanque: una red estrecha desbalancea más, los rociadores cercanos "
            "descargan de más y sube el volumen. Método: solución voraz y luego recocido simulado con semilla fija; "
            "ninguno garantiza el óptimo global, por eso las pruebas lo comparan con búsqueda exhaustiva en redes "
            "pequeñas. Catálogo, costos, velocidad máxima y duración son datos del proyecto."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — cuarto de bombas y NPSH",
        "titulo": "Bomba principal, bomba jockey y NPSH disponible desde un tanque subterráneo",
        "norma_ref": "motor-incendios StructAI · atmósfera estándar · ecuación de Antoine",
        "contenido": (
            "Presión atmosférica por altitud: P = 101,325·(1 − 2,25577e-5·h)^5,25588 kPa. Presión de vapor del agua "
            "(Antoine): log10 P[mmHg] = 8,07131 − 1730,63/(233,426 + T). NPSH disponible = (P_atm − P_vapor)/γ + "
            "(z_agua_mín − z_eje) − pérdidas de succión. El motor elige la bomba más barata del catálogo declarado que "
            "cumple las verificaciones de curva y de NPSH que el proyecto toma de la norma aplicable, dimensiona la "
            "jockey, el tanque (menor huella con la altura útil máxima) y el cuarto. Si la norma del proyecto no admite "
            "succión negativa, una bomba horizontal sobre tanque subterráneo se rechaza y se informa la alternativa "
            "(bomba vertical tipo turbina o bajar el cuarto), que decide el diseñador."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — soportes sismorresistentes",
        "titulo": "Riostras, colgadores y anclajes de la red contra incendio según NSR-10 A.9",
        "norma_ref": "NSR-10 A.9.4-1, A.9.4-2, A.9.4.4, A.9.4.8, A.9.4.9, Tablas A.9.2-1 y A.9.6-1, B.2.4, Apéndice C-D",
        "contenido": (
            "Fuerza sísmica sobre la tubería: Fp = (ax·ap/Rp)·g·Mp ≥ (Aa·I/2)·g·Mp (A.9.4-1), con ax según la altura del "
            "soporte (A.9.4-2, heq ≈ 0,75·hn) y ax = Aa·I en la base (A.9.4.8). Para tubería contra incendio ap = 2,5 "
            "(Tabla A.9.6-1); Rp = 6 con anclaje dúctil, 1,5 no dúctil (expansión) y 0,5 húmedo (A.9.4.9). El grado de "
            "desempeño mínimo es superior en grupos IV y III, bueno en II y bajo en I (Tabla A.9.2-1); el grado "
            "superior exige anclaje dúctil. Se suma la vertical ±W/3 (A.9.4.4). En DMO y DES los anclajes al concreto "
            "siguen C-D.3.3 y la interacción C-D.7. Los edificios de grupos I y II en amenaza baja están exentos "
            "(A.9.1.3) y conservan solo los colgadores por gravedad con 1,4D. Separaciones y capacidades de los anclajes "
            "son datos del proyecto."
        ),
    },
    {
        "seccion": "StructAI protección contra incendio — presupuesto",
        "titulo": "Cantidades, presupuesto con incertidumbre y costo por m² de la red contra incendio",
        "norma_ref": "motor-incendios StructAI",
        "contenido": (
            "Las cantidades salen del diseño: tubería por diámetro, accesorios contados por la topología de la red "
            "(tees, codos, reducciones, salidas de rociador y un acople por extremo), tubos comerciales con sus acoples "
            "intermedios y dos extremos ranurados o roscados por tubo, rociadores, riostras, colgadores, anclajes, "
            "bombas, tanque y cuarto. Gabinetes, siamesa y válvulas entran como cantidades declaradas. Una partida sin "
            "precio nunca se estima: el total se declara parcial y se informa la cobertura. El total se simula por "
            "Monte Carlo con distribuciones triangulares (p05, p50 y p95) y se informa también la cota con todas las "
            "partidas correlacionadas, porque los precios suelen moverse juntos. Un modelo de costo fijo + variable "
            "sirve para prefactibilidad, no reemplaza una cotización."
        ),
    },
]

# ─── Viento — NSR-10 Título B.6 (#242, #292, #322, #323), en master desde el PR #331 ──────────────────────
# Fuente: packages/motor-viento/src/b6.py y packages/orquestador/src/diseno_edificio_3d.py

VIENTO_CHUNKS: list[dict] = [
    {
        "seccion": "StructAI viento — alcance y disponibilidad",
        "titulo": "Qué calcula el motor de viento de StructAI (NSR-10 B.6) y qué no",
        "norma_ref": "NSR-10 Título B.6 · motor-viento StructAI (próximamente en la plataforma)",
        "contenido": (
            "El motor de viento de StructAI aplica el procedimiento analítico de la NSR-10 B.6 al edificio de pórticos "
            "3D: método de edificios bajos (h ≤ 18 m y h no mayor que la menor dimensión en planta), método general "
            "para cualquier altura con factor de ráfaga de estructura rígida o flexible, y casos torsionales. Está "
            "implementado y probado, pero todavía no está disponible en la plataforma: próximamente. La velocidad "
            "básica V, la exposición y Kzt son datos del sitio; la tabla de V por municipio está sin validar y no se usa "
            "por defecto. No verifica componentes ni revestimientos de cubiertas livianas ni sus anclajes. " + AVISO
        ),
    },
    {
        "seccion": "StructAI viento — presión por velocidad y Kz",
        "titulo": "Presión por velocidad qz y coeficiente de exposición Kz",
        "norma_ref": "NSR-10 ec. B.6.5-13, Tablas B.6.5-2 y B.6.5-3",
        "contenido": (
            "qz = 0,613·Kz·Kzt·Kd·V²·I en N/m² con V en m/s (B.6.5-13). Kz = 2,01·(Z/Zg)^(2/α) para 4,0 m ≤ Z ≤ Zg, con "
            "α y Zg de la Tabla B.6.5-2 según la exposición; por debajo de 4,0 m se usa Z = 4,0 m, y en el caso 1 con "
            "exposición B, Z no se toma menor que 9,0 m (nota 2 de la Tabla B.6.5-3). Coeficientes de presión interna "
            "GCpi: edificio cerrado ±0,18, parcialmente cerrado ±0,55, abierto 0. Convención de signos: positivo hacia "
            "la superficie, negativo hacia afuera."
        ),
    },
    {
        "seccion": "StructAI viento — edificios bajos y casos torsionales",
        "titulo": "Método de edificios bajos: GCpf por zonas, succión de cubierta y casos torsionales",
        "norma_ref": "NSR-10 Fig. B.6.5-7 y Figs. B.6.5-8A a 8D",
        "contenido": (
            "Para edificios bajos, StructAI aplica los GCpf de la Fig. B.6.5-7 por zonas (1 a 4 y de borde 1E a 4E, con "
            "el ancho de borde 2a) en las cuatro direcciones de viento, cada una con GCpi positivo y negativo, y reparte "
            "la succión de la cubierta a las vigas del último nivel. Con la nota 5 genera también los casos torsionales "
            "(zonas al 25 % en la mitad lejana), salvo en edificios de un nivel con h ≤ 9 m. Para componentes y "
            "revestimientos usa los GCp de las Figs. B.6.5-8A a 8D, lineales en log10 del área efectiva. Se documenta "
            "una errata de la NSR-10: en la Fig. B.6.5-8B los GCp del alero se imprimen con signo positivo y son "
            "succiones."
        ),
    },
    {
        "seccion": "StructAI viento — método general y factor de ráfaga",
        "titulo": "Método general para edificios altos: Cp de muros y factor de ráfaga rígido o flexible",
        "norma_ref": "NSR-10 B.6.5.8, Fig. B.6.5-3, ecs. B.6.5-2, B.6.5-6, B.6.5-8 a B.6.5-11 y B.6.5-15",
        "contenido": (
            "Para h > 18 m o h mayor que la menor dimensión en planta, la fuerza lateral por nivel combina barlovento "
            "qz·G·0,8 (Kz a la altura de cada nivel) y sotavento qh·G·|Cp|, con Cp de sotavento interpolado en L/B "
            "(Fig. B.6.5-3). Factor de ráfaga: estructura rígida (n1 ≥ 1 Hz) con G de B.6.5-2; flexible (n1 < 1 Hz) con "
            "Gf de B.6.5-6 y la respuesta resonante de B.6.5-8 a B.6.5-11. Gf depende del amortiguamiento β, que la "
            "NSR-10 no fija: StructAI lo trata como hipótesis declarada. En mediciones propias con 272 pórticos de zona "
            "baja, V = 36 m/s y exposición D, pasar de β = 0,02 a 0,01 subió la relación viento/sismo 4,9 % en la "
            "mediana y cambió el refuerzo del 10,7 % de los edificios."
        ),
    },
    {
        "seccion": "StructAI viento — cuándo gobierna el viento en zona sísmica baja",
        "titulo": "Mediciones de StructAI: cuándo el viento cambia el diseño de pórticos en zona de amenaza sísmica baja",
        "norma_ref": "NSR-10 B.6 y A.2.3 · mediciones prerregistradas de StructAI (#292-W y #242)",
        "contenido": (
            "En experimentos prerregistrados de StructAI sobre pórticos de concreto con losa en zona de amenaza sísmica "
            "baja: en edificios bajos el viento de B.6 no cambió el diseño de ninguno de los 86 casos evaluados. En "
            "edificios más altos, con V = 36 m/s y exposición D, el viento cambió el refuerzo de 24 de 272 edificios "
            "(9 %) y algunos dejaron de cumplir. La competencia entre sismo y viento la gobierna la altura: la relación "
            "1,6W/E crece aproximadamente con H^0,9. Por eso, en un edificio de más de 20 m en zona baja sin viento "
            "evaluado, StructAI advierte que conviene declarar la V del sitio. Son resultados de un corpus sintético con "
            "supuestos declarados, no reemplazan el análisis de cada proyecto."
        ),
    },
]

MOTORES_NUEVOS = {
    "geotecnia": GEOTECNIA_CHUNKS,
    "pilotes": PILOTES_CHUNKS,
    "acero_frio": ACERO_FRIO_CHUNKS,
    "incendios": INCENDIOS_CHUNKS,
    "viento": VIENTO_CHUNKS,
}
