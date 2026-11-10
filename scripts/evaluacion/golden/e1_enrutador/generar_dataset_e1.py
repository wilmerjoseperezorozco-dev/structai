"""
Genera dataset_e1.jsonl: preguntas etiquetadas con el dominio al que
DEBERÍAN enrutarse (issue #169, experimento E1). Sin LLM, sin red.

Etiquetado:
  esperado   -- dominio estricto (el que da la mejor respuesta hoy: p.ej.
                geopot para Aa/Av de un municipio, porque solo ese dominio
                activa el dato oficial del SGC en vivo).
  aceptables -- dominios que también producirían una respuesta correcta
                (p.ej. normativa_general, que puede citar el Apéndice A-4).
  estrato    -- tipo de dificultad (taxonomía L3/L4/L5 del plan).
  cluster    -- plantilla de redacción; las preguntas de una misma
                plantilla están correlacionadas y se remuestrean juntas.

Limitación declarada: lo etiquetó la misma persona que diseñó las variantes
del enrutador. El plan exige revisión por una segunda persona antes de
tratar estas etiquetas como verdad final (sección 8 del plan).

Uso: python scripts/evaluacion/golden/e1_enrutador/generar_dataset_e1.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

SALIDA = Path(__file__).with_name("dataset_e1.jsonl")
NG = "normativa_general"

casos: list[dict] = []


def add(pregunta, esperado, estrato, cluster, aceptables=None, nota=""):
    casos.append({
        "pregunta": pregunta, "esperado": esperado,
        "aceptables": sorted(set([esperado] + (aceptables or []))),
        "estrato": estrato, "cluster": cluster, "nota": nota,
    })


# ── S1: amenaza sísmica por municipio (el caso de origen) ─────────────────
# 10 redacciones x 3 municipios. Estricto geopot (activa SGC); aceptable NG.
PLANTILLAS_S1 = [
    "¿Cuál es la amenaza sísmica (Aa/Av) de {m}?",
    "Cual es el Aa y Av de {m}",
    "zona de amenaza sísmica de {m}",
    "¿Qué valores de Aa y Av le corresponden a {m} según la NSR-10?",
    "voy a construir en {m}, que tan sismica es la zona",
    "aceleración pico efectiva para {m}",
    "En {m} la amenaza sismica es alta, intermedia o baja?",
    "necesito el coeficiente Aa para un proyecto en {m}",
    "¿Qué tan fuerte tiembla en {m} para efectos de diseño?",
    "parámetros sísmicos de {m} para el espectro de diseño",
]
MUNICIPIOS = ["Sincelejo", "Montería", "Valledupar", "Pasto", "Cúcuta", "Neiva",
              "Quibdó", "Villavicencio", "Armenia", "Riohacha", "Tunja", "Popayán",
              "Ibagué", "Yopal", "Santa Marta", "Florencia", "Manizales", "Tumaco",
              "Bucaramanga", "Mocoa", "Pereira", "Leticia", "Cartagena", "Sogamoso",
              "Buenaventura", "Barrancabermeja", "Girardot", "Apartadó", "Duitama", "Ipiales"]
_m = MUNICIPIOS[:]
random.Random(169).shuffle(_m)
for i, p in enumerate(PLANTILLAS_S1):
    for m in _m[3 * i: 3 * i + 3]:
        add(p.format(m=m), "geopot", "S1_sismica_municipio", f"S1-{i}", [NG])

# ── S2: preguntas directas por dominio (vocabulario literal) ──────────────
S2 = [
    ("¿Cuál es la dotación neta mínima para un municipio de nivel de complejidad medio según la Resolución 0330?", "aquai"),
    ("¿Cómo se diseña un tanque de almacenamiento de agua potable según el RAS?", "aquai"),
    ("velocidad mínima en tuberías de alcantarillado sanitario", "aquai"),
    ("¿Cómo se clasifica un suelo con el sistema USCS?", "geopot"),
    ("¿Qué es el límite líquido en el ensayo de Atterberg?", "geopot"),
    ("¿Cómo se interpreta el ensayo de asentamiento con el cono de Abrams?", "geopot"),
    ("¿Cuál es el peralte máximo para una vía en terreno montañoso según INVIAS?", "vias"),
    ("¿Cómo se calcula el número de ejes equivalentes ESAL para un pavimento?", "vias"),
    ("¿Qué carga viva vehicular exige la CCP-14 para puentes?", "vias"),
    ("¿Cómo se interpreta un SPI menor a 1 en valor ganado?", "gerencia"),
    ("¿Qué significa el EAC en el análisis de valor ganado?", "gerencia"),
    ("¿Cuánto cuesta el metro cúbico de concreto de 3000 psi?", "apu_precios"),
    ("precio del bulto de cemento gris en Bogotá", "apu_precios"),
    ("¿Cuál es el factor de zona Z para Lima según la E.030?", "peru_e030"),
    ("¿Qué valor de Z establece la NEC-SE-DS para Quito?", "ecuador_nec_se_ds"),
    ("¿Cuál es el recubrimiento mínimo del refuerzo en vigas según el Título C de la NSR-10?", NG),
    ("¿Qué exige la Resolución 0312 de 2019 sobre estándares mínimos del SG-SST?", NG),
    ("¿Cuál es la deriva máxima permitida en edificaciones según la NSR-10?", NG),
    ("¿Qué evalúa el checklist de vulnerabilidad sísmica de vivienda de la AIS?", "vulnerabilidad_vivienda"),
    ("¿Cómo evaluar la vulnerabilidad sísmica de mi casa de mampostería confinada?", "vulnerabilidad_vivienda"),
]
for i, (q, d) in enumerate(S2):
    add(q, d, "S2_directa", f"S2-{i}")

# ── S3: coloquial / indirecto (sin la palabra clave literal) ──────────────
S3 = [
    ("¿Cuánta agua debe gastar cada persona al día para diseñar el acueducto de un pueblo?", "aquai"),
    ("se me inunda la calle cada vez que llueve, como dimensiono el tubo de aguas lluvias", "aquai"),
    ("¿la tierra de mi lote aguanta una casa de tres pisos?", "geopot"),
    ("el concreto que me llegó a la obra parece muy aguado, cómo lo verifico", "geopot"),
    ("¿qué tan inclinada puede ser una carretera de montaña?", "vias"),
    ("la carretera de mi vereda está llena de huecos, cómo se clasifica ese daño", "vias"),
    ("voy atrasado y pasado de presupuesto en la obra, cómo lo mido", "gerencia"),
    ("¿cómo sé si mi proyecto va a terminar a tiempo con lo que llevo ejecutado?", "gerencia"),
    ("¿en cuánto me sale pañetar un muro de 20 metros cuadrados?", "apu_precios"),
    ("cuanta plata necesito para fundir una placa de 50 m2", "apu_precios"),
    ("tengo una casa de ladrillo sin columnas, ¿es peligrosa si tiembla?", "vulnerabilidad_vivienda"),
    ("mi casa es de dos pisos y tiene grietas en los muros, ¿resiste un sismo?", "vulnerabilidad_vivienda"),
    ("¿qué tan gruesa debe ser una columna de un edificio de cinco pisos en Colombia?", NG),
    ("¿los obreros tienen que usar arnés para trabajar en el techo?", NG),
    ("estoy diseñando en Cusco, qué norma sísmica aplica", "peru_e030"),
    ("voy a construir en Cuenca, Ecuador, que coeficiente sismico uso", "ecuador_nec_se_ds"),
]
for i, (q, d) in enumerate(S3):
    add(q, d, "S3_coloquial", f"S3-{i}")

# ── S4: sinónimos y menciones indirectas de un concepto técnico ───────────
S4 = [
    ("¿cuál es la PGA de diseño para Barranquilla?", "geopot", [NG], "PGA = aceleración pico"),
    ("coeficiente de aceleración horizontal pico efectiva en Cali", "geopot", [NG], ""),
    ("¿qué coeficientes de sitio Fa y Fv aplican a un suelo tipo D?", "geopot", [NG], ""),
    ("¿cuál es la capacidad de carga admisible de una arcilla blanda?", "geopot", [], "capacidad portante"),
    ("¿cómo se calcula el IRI de una vía?", "vias", [], "rugosidad"),
    ("índice de desempeño del costo de mi obra", "gerencia", [], "CPI sin sigla"),
    ("¿cuánto vale el análisis de precio unitario de un muro en bloque?", "apu_precios", [], "APU sin sigla"),
    ("¿cuál es el consumo per cápita de agua para diseño?", "aquai", [], "dotación"),
    ("¿cuál es el periodo de retorno para diseñar un alcantarillado pluvial?", "aquai", [], ""),
    ("¿cómo se llama la norma colombiana de sismorresistencia y qué cubre?", NG, [], ""),
]
for i, (q, d, a, n) in enumerate(S4):
    add(q, d, "S4_sinonimo", f"S4-{i}", a, n)

# ── S5: negación explícita (L4) ───────────────────────────────────────────
S5 = [
    ("no te pregunto precios, quiero saber qué dice la NSR-10 sobre el recubrimiento del acero", NG, []),
    ("no es sobre mi casa, quiero la zona de amenaza sísmica de Sincelejo", "geopot", [NG]),
    ("no necesito el costo del concreto, sino cómo se verifica su resistencia en laboratorio", "geopot", []),
    ("sin hablar de pavimentos, ¿qué es el valor ganado en gerencia de obra?", "gerencia", []),
    ("no me interesa la norma de Perú, sino la colombiana para diseño sísmico de edificios", NG, ["geopot"]),
    ("no quiero evaluar la vulnerabilidad de la vivienda, solo saber el Aa de Montería", "geopot", [NG]),
]
for i, (q, d, a) in enumerate(S5):
    add(q, d, "S5_negacion", f"S5-{i}", a)

# ── S6: confusores sísmicos (sismo no implica vivienda) ───────────────────
S6 = [
    ("¿qué sistema estructural exige la NSR-10 para zona de amenaza sísmica alta?", NG, ["geopot"]),
    ("¿cómo se calcula el cortante basal sísmico de un edificio?", NG, []),
    ("¿cuál es el coeficiente de capacidad de disipación de energía R0 para pórticos de concreto DES?", NG, []),
    ("¿qué es el espectro elástico de aceleraciones de diseño?", NG, ["geopot"]),
    ("¿cuándo se requiere un estudio de microzonificación sísmica?", "geopot", [NG]),
    ("¿un hospital tiene un coeficiente de importancia mayor en el diseño sísmico?", NG, []),
    ("licuación de suelos durante un sismo, cómo se evalúa", "geopot", [NG]),
    ("¿qué pasó con el sismo de esta semana y qué norma aplica a la reconstrucción?", NG, []),
]
for i, (q, d, a) in enumerate(S6):
    add(q, d, "S6_confusor_sismico", f"S6-{i}", a)

# ── S7: generales / fuera de los motores ──────────────────────────────────
S7 = [
    ("¿qué es la NTC 673?", NG, []),
    ("¿qué requisitos de señalización exige una obra en vía pública?", NG, ["vias"]),
    ("¿qué es un plan de emergencias en una obra?", NG, []),
    ("¿quién debe firmar los planos estructurales en Colombia?", NG, []),
    ("hola, ¿qué puedes hacer?", NG, []),
    ("¿qué norma regula las escaleras de evacuación en edificios?", NG, []),
]
for i, (q, d, a) in enumerate(S7):
    add(q, d, "S7_general", f"S7-{i}", a)

# ── partición dev/test por cluster (ninguna plantilla queda partida) ──────
clusters = sorted({c["cluster"] for c in casos})
random.Random(2026).shuffle(clusters)
DEV = set(clusters[: int(len(clusters) * 0.4)])
for i, c in enumerate(casos):
    c["id"] = f"E1-{i:03d}"
    c["split"] = "dev" if c["cluster"] in DEV else "test"

with SALIDA.open("w", encoding="utf-8") as f:
    for c in casos:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(f"{len(casos)} casos -> {SALIDA.name} | dev={sum(c['split'] == 'dev' for c in casos)} "
      f"test={sum(c['split'] == 'test' for c in casos)}")
