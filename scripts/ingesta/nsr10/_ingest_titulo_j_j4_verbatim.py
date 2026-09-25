"""
Título J — re-ingesta verbatim, Capítulo J.4 completo (Detección y
extinción de incendios): J.4.1 (Alcance), J.4.2 (Sistemas y equipos para
detección y alarma, con la tabla J.4.2-1 por grupo/subgrupo de ocupación)
y J.4.3 (Sistemas y equipos para extinción, con la tabla J.4.3-1 y las
9 subsecciones por grupo de ocupación A/C/F/I/L/M/P/R-2/R-3, cada una con
rociadores automáticos, tomas fijas para bomberos y extintores portátiles).

Fuente: NSR-10-1501-1570.pdf, páginas reales 54-61 (J-25 a J-31, capítulo
J.4 completo hasta la página "Notas" en blanco que precede al Título K).
Mismo offset confirmado en la parte 2 de J.3: página_J = página_real - 29.

Reemplaza los 6 chunks condensados NSR10-J-J_4_* detectados por el mismo
patrón "resumen disfrazado de completo" (minúsculas sin tildes, seccion en
formato de rango) verificado leyendo su texto real antes de borrar.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título J — Requisitos de Protección Contra Incendios en Edificaciones"

IDS_OBSOLETOS = [
    "NSR10-J-J_4_1_a_J_4_2_r1", "NSR10-J-J_4_1_a_J_4_2_r2",
    "NSR10-J-J_4_3_1_a_J_4_3_9_r1", "NSR10-J-J_4_3_1_a_J_4_3_9_r2",
    "NSR10-J-J_4_3_1_a_J_4_3_9_r3", "NSR10-J-J_4_3_1_a_J_4_3_9_r4",
]


CHUNKS = [
    {
        "id": "NSR10-J-J_4_1_1", "seccion": "J.4.1.1",
        "titulo": "J.4.1 — Alcance. J.4.1.1 — Dotaciones de instalaciones de protección contra incendio: detección automática/manual y transmisión de alarma",
        "texto": (
            "CAPITULO J.4 — DETECCIÓN Y EXTINCIÓN DE INCENDIOS. "
            "J.4.1 — ALCANCE. J.4.1.1 — En este Capítulo se establecen las dotaciones de instalaciones de protección "
            "contra incendio con las que deben contar los edificios. La instalación de dispositivos de detección hace "
            "posible la transmisión de una señal, automática mediante detectores o manual mediante pulsadores, desde "
            "el lugar en que se produce el incendio hasta una central, así como la posterior transmisión de la alarma "
            "desde dicha central hasta los ocupantes, pudiendo activarse dicha alarma automática y manualmente."
        ),
    },
    {
        "id": "NSR10-J-J_4_2_1", "seccion": "J.4.2.1",
        "titulo": "J.4.2 — Sistemas y equipos para detección y alarma de incendios. J.4.2.1 — Aire acondicionado: detectores de humo en ductos y tablero de desconexión",
        "texto": (
            "J.4.2 — SISTEMAS Y EQUIPOS PARA DETECCIÓN Y ALARMA DE INCENDIOS. "
            "J.4.2.1 — AIRE ACONDICIONADO — En los edificios que cuenten con sistema central de aire acondicionado, "
            "se deberá disponer de detectores de humo en los ductos principales, que actúen desconectando "
            "automáticamente el sistema. Adicionalmente se dispondrá de un tablero de desconexión del sistema central "
            "de aire acondicionado ubicado adyacente al tablero general eléctrico y para el uso exclusivo del cuerpo "
            "de bomberos."
        ),
    },
    {
        "id": "NSR10-J-J_4_2_2", "seccion": "J.4.2.2",
        "titulo": "J.4.2.2 — Dispositivos para la detección temprana de incendios, según tabla J.4.2-1 por grupo/subgrupo de ocupación",
        "texto": "J.4.2.2 — DISPOSITIVOS PARA LA DETECCIÓN TEMPRANA DE INCENDIOS — Deberán instalarse equipos para la detección y la alarma temprana contra incendios en las edificaciones clasificadas en los grupos y sub-grupos de ocupación que se listan en la tabla J.4.2-1.",
    },
    {
        "id": "NSR10-J-J_4_2_tabla1", "seccion": "J.4.2-1",
        "titulo": "Tabla J.4.2-1 — Instalación de detectores de acuerdo con el grupo de ocupación (R, I, C-I-A, I-L)",
        "texto": (
            "Tabla J.4.2-1 — Instalación de detectores de acuerdo con el grupo de ocupación (Grupo, Subgrupo, "
            "Condición, Tipo de detector, Ubicación). "
            "Grupo R, subgrupo R-2, condición: para edificios con más de 7 pisos. Grupo R, subgrupo R-3, condición: "
            "para edificios con más de 5 pisos. Tipo de detector para R-2/R-3: automáticos de humo y alarma sonora. "
            "Ubicación: pasillos, escaleras y espacios comunes de circulación; espacios residenciales para la cocina; "
            "zonas de almacenamiento cuya superficie total sea mayor de 50 m²; zonas comunes tales como salas de "
            "reunión, de juegos, de deportes etc. "
            "Grupo I, subgrupo I-2, condición: en cualquier caso. Tipo de detector: automáticos de humo y alarma "
            "sonora. Ubicación: se ubicarán pulsadores manuales de alarma de incendio en los pasillos, zonas de "
            "circulación y en las diferentes dependencias del hospital; en las zonas de hospitalización. "
            "Grupos C, I, A (subgrupos C-1, C-2, I-4, I-5, A-1, A-2), condición: zonas de alto riesgo. Tipo de "
            "detector: térmicos y/o de humo y alarma sonora. Ubicación: se ubicarán pulsadores manuales de alarma de "
            "incendios y repartidos adecuadamente. "
            "Grupos I, L (subgrupos I-3, L-1, L-2, L-3, L-4, L-5), condición: si la superficie total construida es "
            "mayor de 5 000 m² o más de tres (3) pisos. Tipo de detector: térmicos y/o de humo y alarma sonora. "
            "Ubicación: se dispondrán pulsadores manuales en el interior de los locales de edificaciones clasificadas "
            "en las categorías de riesgo I y II; no será necesaria la utilización de detectores térmicos o de humo "
            "cuando exista una instalación de rociadores automáticos de agua."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_intro", "seccion": "J.4.3",
        "titulo": "J.4.3 — Sistemas y equipos para extinción de incendios: mantenimiento NFPA 25, otros sistemas según tabla J.4.3-1",
        "texto": (
            "J.4.3 — SISTEMAS Y EQUIPOS PARA EXTINCIÓN DE INCENDIOS. "
            "Toda edificación debe disponer de recursos para la extinción del fuego cuyas características dependen "
            "del grupo de uso en que se clasifique. Los sistemas y equipos deben diseñarse e instalarse de acuerdo con "
            "los requisitos mínimos especificados en el presente Capítulo. Luego de instalados, deben mantenerse "
            "periódicamente para garantizar su adecuada funcionalidad en cualquier momento. Los sistemas hidráulicos "
            "deben tener inspección, prueba y mantenimiento, las cuales se realizan de acuerdo con la norma NFPA 25. "
            "Cuando por características propias de los productos del sistema de almacenamiento o de los equipos, se "
            "requieren otros sistemas de protección contra incendio o sean instalados con la aprobación de la "
            "autoridad competente como una alternativa equivalente, el diseño y la instalación del sistema, deberán "
            "estar de acuerdo con las normas apropiadas indicadas en la tabla J.4.3-1."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_tabla1", "seccion": "J.4.3-1",
        "titulo": "Tabla J.4.3-1 — Otros sistemas de protección contra incendio requerido, con su norma NFPA aplicable",
        "texto": (
            "Tabla J.4.3-1 — Otros sistemas de protección contra incendio requerido, con su norma correspondiente. "
            "Sistema de espuma de baja expansión — NFPA 11. Sistema de espuma de mediana y alta expansión — NFPA 11 A. "
            "Sistema de dióxido de carbono — NFPA 12. Sistema de Halón 1301 — NFPA 12 A. "
            "Rociadores en viviendas uni y bifamiliares y en casas prefabricadas — NFPA 13 D. "
            "Rociadores en ocupaciones residenciales de máximo y que incluyen cuatro pisos de altura — NFPA 13 R. "
            "Sistemas de pulverización de agua — NFPA 15. "
            "Rociadores de agua-espuma por diluvio, sistemas de pulverización de agua-espuma, sistemas de rociadores "
            "de agua-espuma de cabeza cerrada — NFPA 16. "
            "Sistemas de extinción de químico seco — NFPA 17. Sistemas de extinción de químico húmedo — NFPA 17 A. "
            "Sistemas de niebla de agua — NFPA 750. Sistemas de extinción contra incendio de agente limpio — NFPA 2001."
        ),
    },
    # ---- J.4.3.1 — GRUPO A (ALMACENAMIENTO) ----
    {
        "id": "NSR10-J-J_4_3_1_1", "seccion": "J.4.3.1.1",
        "titulo": "J.4.3.1 — Grupo A (Almacenamiento). J.4.3.1.1 — Rociadores Automáticos NTC2301/NFPA 13, 6 condiciones (a-f)",
        "texto": (
            "J.4.3.1 — GRUPO DE OCUPACIÓN A (ALMACENAMIENTO). "
            "J.4.3.1.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación A "
            "(Almacenamiento) debe estar protegida por un sistema aprobado y eléctricamente supervisado, de "
            "rociadores automáticos diseñados de acuerdo con la última versión del Código para suministro y "
            "distribución de agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación "
            "de Sistemas de Rociadores, NFPA 13, así: "
            "(a) En la totalidad de edificios con más de tres pisos o 9 m de altura, lo que sea mayor, clasificados en "
            "el subgrupo de ocupación A-1 (Almacenamiento de riesgo moderado). "
            "(b) En la totalidad de edificios con áreas no separadas por muros cortafuegos y mayores de 1 000 m², "
            "clasificados en el subgrupo de ocupación A-1 (Almacenamiento de riesgo moderado). "
            "(c) Sin importar el número de pisos y en la totalidad de edificios con menos de 18 m de aislamiento con "
            "áreas de uso público y con los linderos de otra propiedad, clasificados en el subgrupo de ocupación A-1 "
            "(Almacenamiento de riesgo moderado). "
            "(d) Sin importar el número de pisos y en la totalidad de edificios con área total de construcción mayor "
            "de 2 200 m², incluidas las áreas de mezanines, clasificados en el subgrupo de ocupación A-1 "
            "(Almacenamiento de riesgo moderado). "
            "(e) Sin importar el subgrupo de clasificación de riesgo, en la totalidad de edificios del grupo A, "
            "independientemente de su área construida, cuando sea de acceso público. "
            "(f) En la totalidad de edificios dedicados al almacenamiento de llantas, con un volumen de almacenamiento "
            "mayor de 500 m³."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_1_2", "seccion": "J.4.3.1.2",
        "titulo": "J.4.3.1.2 — Grupo A: Tomas fijas para bomberos y mangueras (NTC 1669/NFPA 14)",
        "texto": "J.4.3.1.2 — Tomas fijas para bomberos y mangueras para extinción de incendios — Toda edificación clasificada en el grupo de ocupación A (Almacenamiento) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14.",
    },
    {
        "id": "NSR10-J-J_4_3_1_3", "seccion": "J.4.3.1.3",
        "titulo": "J.4.3.1.3 — Grupo A: Extintores portátiles de fuego (NTC 2885/NFPA 10)",
        "texto": "J.4.3.1.3 — Extintores portátiles de fuego — Toda edificación clasificada en el grupo de ocupación A (Almacenamiento) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
    # ---- J.4.3.2 — GRUPO C (COMERCIAL) ----
    {
        "id": "NSR10-J-J_4_3_2_1", "seccion": "J.4.3.2.1",
        "titulo": "J.4.3.2 — Grupo C (Comercial). J.4.3.2.1 — Rociadores Automáticos, 4 condiciones (a-d)",
        "texto": (
            "J.4.3.2 — GRUPO DE OCUPACIÓN C (COMERCIAL). "
            "J.4.3.2.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación C (Comercial) "
            "debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores automáticos "
            "diseñados de acuerdo con la última versión del Código para suministro y distribución de agua para "
            "extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de Rociadores, "
            "NFPA 13, así: "
            "(a) En la totalidad de edificios con más de tres pisos o 9 m de altura, lo que sea mayor, clasificados en "
            "el subgrupo de ocupación de bienes (C-2). "
            "(b) Sin importar el número de pisos y en la totalidad de edificios con área total construida mayor de "
            "1 100 m², incluidas las áreas de mezanines, clasificados en el subgrupo de ocupación de bienes (C-2). "
            "(c) En la totalidad de edificios con pisos bajo nivel de la calle, para áreas de piso mayores de 200 m² "
            "y utilizados para venta, almacenamiento, o manipulación de mercancías combustibles, clasificados en el "
            "subgrupo de ocupación de bienes (C-2). "
            "(d) En la totalidad de edificios con más de seis pisos o 18 m de altura, lo que sea mayor, clasificados "
            "en el subgrupo de ocupación de servicios (C-1)."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_2_2", "seccion": "J.4.3.2.2",
        "titulo": "J.4.3.2.2 — Grupo C: Tomas fijas para bomberos y mangueras",
        "texto": "J.4.3.2.2 — Tomas fijas para bomberos y mangueras para extinción de incendios — Toda edificación clasificada en el grupo de ocupación C (Comercial) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14.",
    },
    {
        "id": "NSR10-J-J_4_3_2_3", "seccion": "J.4.3.2.3",
        "titulo": "J.4.3.2.3 — Grupo C: Extintores de fuego portátiles",
        "texto": "J.4.3.2.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación C (Comercial) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
    # ---- J.4.3.3 — GRUPO F (FABRIL E INDUSTRIAL) ----
    {
        "id": "NSR10-J-J_4_3_3_1", "seccion": "J.4.3.3.1",
        "titulo": "J.4.3.3 — Grupo F (Fabril e Industrial). J.4.3.3.1 — Rociadores Automáticos, 5 condiciones (a-e)",
        "texto": (
            "J.4.3.3 — GRUPO DE OCUPACIÓN F (FABRIL E INDUSTRIAL). "
            "J.4.3.3.1 — Rociadores Automáticos — Toda edificación de ocupación F (Fabril e Industrial) debe estar "
            "protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores automáticos diseñados de "
            "acuerdo con la última versión del Código para suministro y distribución de agua para extinción de "
            "incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de Rociadores, NFPA 13, así: "
            "(a) En la totalidad de edificios con más de tres pisos o 9 m de altura, lo que sea mayor, clasificados en "
            "el subgrupo de ocupación de riesgo moderado (F-1). "
            "(b) En la totalidad de edificios con áreas sin muros cortafuego y mayores de 1 000 m², clasificados en "
            "el subgrupo de ocupación de riesgo moderado (F-1). "
            "(c) Sin importar el número de pisos y en la totalidad de edificios con área total de construcción mayor "
            "de 2 200 m², incluidas las áreas de mezanines, clasificados en el subgrupo de ocupación de riesgo bajo "
            "(F-2). "
            "(d) Sin importar el número de pisos y en la totalidad de edificios con menos de 18 m de aislamiento con "
            "áreas de uso público y con los linderos de otra propiedad, clasificados en el subgrupo de ocupación de "
            "riesgo moderado (F-1). "
            "(e) En la totalidad de edificios con más de seis pisos o 18 m de altura, lo que sea mayor, clasificados "
            "en el subgrupo de ocupación de riesgo bajo (F-2)."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_3_2", "seccion": "J.4.3.3.2",
        "titulo": "J.4.3.3.2 — Grupo F: Tomas fijas para bomberos y mangueras",
        "texto": "J.4.3.3.2 — Tomas fijas para bomberos y mangueras para extinción de incendios — Toda edificación clasificada en el grupo de ocupación F (Fabril e Industrial) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14.",
    },
    {
        "id": "NSR10-J-J_4_3_3_3", "seccion": "J.4.3.3.3",
        "titulo": "J.4.3.3.3 — Grupo F: Extintores de fuego portátiles",
        "texto": "J.4.3.3.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación F (Fabril e Industrial) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
    # ---- J.4.3.4 — GRUPO I (INSTITUCIONAL) ----
    {
        "id": "NSR10-J-J_4_3_4_1", "seccion": "J.4.3.4.1",
        "titulo": "J.4.3.4 — Grupo I (Institucional). J.4.3.4.1 — Rociadores Automáticos, 6 condiciones (a-f)",
        "texto": (
            "J.4.3.4 — GRUPO DE OCUPACIÓN I (INSTITUCIONAL). "
            "J.4.3.4.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación I "
            "(Institucional) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de "
            "rociadores automáticos de acuerdo con la última versión del Código para suministro y distribución de "
            "agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de "
            "Rociadores, NFPA 13, así: "
            "(a) En la totalidad de edificios con confinamiento o restricción de movimiento, clasificados en el "
            "subgrupo de ocupación de reclusión (I-1). "
            "(b) En la totalidad de edificios, clasificados en el subgrupo de ocupación de salud o incapacidad (I-2). "
            "(c) En la totalidad de edificios con área total de construcción de 2 000 m² o mayor, clasificados en el "
            "subgrupo de ocupación de educación (I-3). "
            "(d) En la totalidad de edificios con más de cuatro pisos o 12 m de altura, lo que sea mayor, clasificados "
            "en el subgrupo de ocupación de educación (I-3). "
            "(e) En la totalidad de edificios con uno o más pisos bajo el nivel del suelo, clasificados en el "
            "subgrupo de ocupación de educación (I-3). "
            "(f) En edificios clasificados en los subgrupos de ocupación de seguridad y servicio públicos (I-4 e I-5), "
            "de acuerdo con su uso; por ejemplo, edificios para oficinas se protegerán con las condiciones listadas "
            "para el grupo de ocupación comercial de servicios (C-1) y las áreas para asambleas con las condiciones "
            "del grupo de ocupación de lugares de reunión (L), etc."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_4_2", "seccion": "J.4.3.4.2",
        "titulo": "J.4.3.4.2 — Grupo I: Tomas fijas de agua para bomberos, 4 condiciones (a-d)",
        "texto": (
            "J.4.3.4.2 — Tomas fijas de agua para bomberos — Toda edificación clasificada en el grupo de ocupación I "
            "(Institucional) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para "
            "extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y "
            "distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para "
            "Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, así: "
            "(a) En edificios de más de tres pisos o 9 m de altura, lo que sea mayor, sobre el nivel de la calle. "
            "(b) En edificios con un piso bajo nivel de la calle. "
            "(c) En edificios donde, en uno de sus pisos, la distancia a cualquier punto desde el acceso más cercano "
            "para el Cuerpo de Bomberos es mayor de 30 m. "
            "(d) Cuando el edificio esté protegido con un sistema de rociadores, las tomas fijas para bomberos se "
            "diseñarán teniendo en cuenta lo recomendado por la última versión del Código para suministro y "
            "distribución de agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación "
            "de Sistemas de Rociadores, NFPA 13."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_4_3", "seccion": "J.4.3.4.3",
        "titulo": "J.4.3.4.3 — Grupo I: Extintores de fuego portátiles",
        "texto": "J.4.3.4.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación I (Institucional) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
    # ---- J.4.3.5 — GRUPO L (LUGARES DE REUNIÓN) ----
    {
        "id": "NSR10-J-J_4_3_5_1", "seccion": "J.4.3.5.1",
        "titulo": "J.4.3.5 — Grupo L (Lugares de Reunión). J.4.3.5.1 — Rociadores Automáticos, condición (a) con 4 excepciones i-iv, más (b)-(d)",
        "texto": (
            "J.4.3.5 — GRUPO DE OCUPACIÓN L (LUGARES DE REUNIÓN). "
            "J.4.3.5.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación L (Lugares de "
            "reunión) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores "
            "automáticos de acuerdo con la última versión del Código para suministro y distribución de agua para "
            "extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de Rociadores, "
            "NFPA 13, así: "
            "(a) En la totalidad de edificios con carga de ocupación mayor de 300 personas. El sistema de rociadores "
            "debe cubrir todos los pisos que se encuentren por debajo del piso clasificado como L (Lugar de Reunión). "
            "Si el sitio está bajo el nivel del suelo, el sistema de rociadores debe cubrir todos los pisos superiores "
            "hasta el nivel de salida incluido este nivel. Se eximen del cumplimiento de este requisito: "
            "(i) Salones con un uso único de Lugar de Reunión (L), no utilizado para exhibiciones ni demostraciones, "
            "con área menor de 1 100 m², con separación de resistencia de una hora para fuego de otros espacios o "
            "edificios y con salidas para evacuación independientes y que no dispongan de instalaciones para una "
            "audiencia mayor de 100 personas. "
            "(ii) Lugares de Reunión Deportivos (L-1), dedicados sólo a la práctica del deporte y que no dispongan "
            "de instalaciones para audiencia mayor de 300 personas. "
            "(iii) Los lugares en estadios y arenas ubicados sobre las canchas, escenarios deportivos, zonas de "
            "graderías y asientos, en áreas abiertas sin cerramiento donde un estudio de Ingeniería conceptúe acerca "
            "de la no efectividad de la protección con rociadores como consecuencia de la altura del techo y de la "
            "carga combustible. "
            "(iv) En estadios y arenas abiertos o sin cerramientos con cabinas para prensa menores de 100 m²; con "
            "áreas de almacenamiento, menores de 100 m² y con separación para fuego de por lo manos una hora; áreas "
            "usadas en venta de boletas, baños o concesiones, menores de 30 m², sin materiales inflamables, "
            "construidas con material incombustible. "
            "(b) En la totalidad de edificios, sin importar el área, sin importar el número de personas, clasificados "
            "como grupo de ocupación para Lugares de Reunión Sociales y Recreativos (L-3). Se eximen de este "
            "requisito los lugares de este grupo donde no se realizan fiestas y no se permite el consumo de bebidas "
            "alcohólicas. "
            "(c) Todo el escenario y las áreas anexas como camerinos, vestieres, bodegas, salones de ensayos. Se "
            "exceptúan los que tengan menos 100 m² de área y menos de 15 m de altura y cuyas colgaduras combustibles "
            "no sean verticalmente retractiles y que las colgaduras combustibles se limiten a la cortina principal y "
            "a la cortina del fondo. "
            "(d) Todas las instalaciones interiores en edificios con ocupación para diversión y juegos de niños y "
            "adultos. Se exceptúan estructuras que no excedan de 3.0 m de altura y 15 m² de área de proyección "
            "horizontal."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_5_2", "seccion": "J.4.3.5.2",
        "titulo": "J.4.3.5.2 — Grupo L: Tomas fijas de agua para bomberos, 5 condiciones (a-e)",
        "texto": (
            "J.4.3.5.2 — Tomas fijas de agua para bomberos — Toda edificación clasificada en el grupo de ocupación L "
            "(Lugares de reunión) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para "
            "extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y "
            "distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para "
            "Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, así: "
            "(a) En edificios de más de cuatro pisos o 12 m de altura, lo que sea mayor sobre el nivel de la calle. "
            "(b) En edificios con dos piso bajo nivel de la calle. "
            "(c) En Edificios no protegidos con rociadores donde, en uno de los pisos, la distancia a cualquier punto "
            "desde el acceso mas cercano para el Cuerpo de Bomberos es mayor de 30 m. "
            "(d) A cada lado del escenario se instalará una estación con manguera contra incendios de 38 mm de "
            "diámetro. "
            "(e) Cuando el edificio esté protegido con un sistema de rociadores, las tomas fijas para bomberos se "
            "diseñaran teniendo en cuenta lo recomendado por la última versión del Código para suministro y "
            "distribución de agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación "
            "de Sistemas de Rociadores, NFPA 13."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_5_3", "seccion": "J.4.3.5.3",
        "titulo": "J.4.3.5.3 — Grupo L: Extintores de fuego portátiles, con 4 exenciones/reglas (a-d)",
        "texto": (
            "J.4.3.5.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación L "
            "(Lugares de reunión) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de "
            "acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de "
            "Extintores de fuego Portátiles, NFPA 10, así: "
            "(a) Este requerimiento no aplica a las áreas de tribunas y graderías. "
            "(b) Este requerimiento no aplica a las áreas utilizadas como canchas deportivas, de espectáculos y de "
            "entretenimiento. "
            "(c) Este requerimiento no aplica a los Lugares de Reunión (L) abiertos y a la intemperie. "
            "(d) Los extintores deben localizarse en lugares seguros y accesibles al personal operativo."
        ),
    },
    # ---- J.4.3.6 — GRUPO M (MIXTO Y OTROS) ----
    {
        "id": "NSR10-J-J_4_3_6_1", "seccion": "J.4.3.6.1",
        "titulo": "J.4.3.6 — Grupo M (Mixto y otros). J.4.3.6.1 — Rociadores Automáticos según exigencias de J.4.3.1 a J.4.3.5",
        "texto": "J.4.3.6 — GRUPO DE OCUPACIÓN M (MIXTO Y OTROS). J.4.3.6.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación M (Mixto y otros) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores automáticos de acuerdo con la última versión del Código para suministro y distribución de agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de Rociadores, NFPA 13, de acuerdo con las exigencias de extinción para cada ocupación contenidas en los numerales J.4.3.1 a J.4.3.5.",
    },
    {
        "id": "NSR10-J-J_4_3_6_2", "seccion": "J.4.3.6.2",
        "titulo": "J.4.3.6.2 — Grupo M: Tomas fijas de agua para bomberos, según exigencias de J.4.3.1 a J.4.3.5",
        "texto": "J.4.3.6.2 — Tomas fijas de agua para bomberos — Toda edificación clasificada en el grupo de ocupación M (Mixtos y otros) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, de acuerdo con las exigencias de extinción para cada ocupación contenidas en los numerales J.4.3.1 a J.4.3.5.",
    },
    {
        "id": "NSR10-J-J_4_3_6_3", "seccion": "J.4.3.6.3",
        "titulo": "J.4.3.6.3 — Grupo M: Extintores de fuego portátiles. J.4.3.6.3.1 — Estacionamientos: extintor de polvo químico seco de 5kg cada 10 vehículos",
        "texto": (
            "J.4.3.6.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación M "
            "(Mixtos y otros) debe estar protegida por un sistema de extintores de fuego portátiles, diseñados de "
            "acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de "
            "Extintores de fuego Portátiles, NFPA 10, de acuerdo con las exigencias de extinción para cada ocupación "
            "contenidas en los numerales J.4.3.1 a J.4.3.5. "
            "J.4.3.6.3.1 — En los pisos de toda edificación que se dediquen a estacionamiento y en toda edificación "
            "cuya ocupación sea la de estacionamiento, se dispondrá de un extintor de polvo químico seco de cinco (5) "
            "kg por cada diez (10) vehículos, ubicado en lugares visibles y distanciados entre sí."
        ),
    },
    # ---- J.4.3.7 — GRUPO P (ALTA PELIGROSIDAD) ----
    {
        "id": "NSR10-J-J_4_3_7_1", "seccion": "J.4.3.7.1",
        "titulo": "J.4.3.7 — Grupo P (Alta Peligrosidad). J.4.3.7.1 — Rociadores Automáticos, especificaciones más estrictas entre NTC2301/NFPA13/NFPA5000",
        "texto": "J.4.3.7 — GRUPO DE OCUPACIÓN P (ALTA PELIGROSIDAD). J.4.3.7.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación Alta Peligrosidad (P) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores automáticos diseñados de acuerdo con las especificaciones más estrictas entre las versiones más recientes del Código para suministro y distribución de agua para extinción de incendios en edificios, NTC2301, de la Norma para Instalación de Sistemas de Rociadores, NFPA 13, del Código de Construcción y Seguridad y Código Internacional de construcción, NFPA 5000, así:",
    },
    {
        "id": "NSR10-J-J_4_3_7_2", "seccion": "J.4.3.7.2",
        "titulo": "J.4.3.7.2 — Grupo P: Tomas fijas para bomberos y mangueras, especificaciones más estrictas entre NTC1669/NFPA14/NFPA5000",
        "texto": "J.4.3.7.2 — Tomas fijas de agua para bomberos y mangueras para extinción de incendios — Toda edificación clasificada en el grupo de ocupación Alta Peligrosidad (P) debe estar protegida por un sistema de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con las especificaciones más estrictas entre las versiones más recientes del Código para suministro y distribución de agua para extinción de incendios en edificaciones, NTC 1669, del Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, del Código de Construcción y Seguridad y Código Internacional de construcción, NFPA 5000.",
    },
    {
        "id": "NSR10-J-J_4_3_7_3", "seccion": "J.4.3.7.3",
        "titulo": "J.4.3.7.3 — Grupo P: Extintores de fuego portátiles, especificaciones más estrictas entre NTC2885/NFPA10/NFPA5000",
        "texto": "J.4.3.7.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación Alta Peligrosidad (P) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con las especificaciones más estrictas entre las versiones más recientes de la norma Extintores de fuego portátiles, NTC 2885, de la Norma de Extintores de fuego Portátiles, NFPA 10, del Código de Construcción y Seguridad y Código Internacional de construcción, NFPA 5000.",
    },
    # ---- J.4.3.8 — GRUPO R-2 (RESIDENCIAL MULTIFAMILIAR) ----
    {
        "id": "NSR10-J-J_4_3_8_1", "seccion": "J.4.3.8.1",
        "titulo": "J.4.3.8 — Grupo R-2 (Residencial Multifamiliar). J.4.3.8.1 — Rociadores Automáticos, 2 condiciones (a-b)",
        "texto": (
            "J.4.3.8 — GRUPO DE OCUPACIÓN R-2 (RESIDENCIAL MULTIFAMILIAR). "
            "J.4.3.8.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación Residencial "
            "Multifamiliar (R-2) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de "
            "rociadores automáticos de acuerdo con la última versión del Código para suministro y distribución de "
            "agua para extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de "
            "Rociadores, NFPA 13, así: "
            "(a) En la totalidad de edificaciones clasificadas en el subgrupo de ocupación Residencial Multifamiliar "
            "(R-2), cuya altura exceda 7 pisos, en las zonas comunes (pasillos y áreas de circulación), excepto las "
            "escaleras. "
            "(b) En toda el área de pisos para uso como estacionamiento ubicados bajo edificios clasificados en el "
            "subgrupo de ocupación Residencial Multifamiliar (R-2)."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_8_2", "seccion": "J.4.3.8.2",
        "titulo": "J.4.3.8.2 — Grupo R-2: Tomas fijas para bomberos y mangueras, 3 condiciones (a-c)",
        "texto": (
            "J.4.3.8.2 — Tomas fijas para bomberos y mangueras para extinción de incendios — Toda edificación "
            "clasificada en el grupo de ocupación Residencial Multifamiliar (R-2) debe estar protegida por un sistema "
            "de tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última "
            "versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, "
            "NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, así: "
            "(a) En la totalidad de edificaciones clasificadas en el subgrupo de ocupación Residencial Multifamiliar "
            "(R-2) que tengan más de cinco pisos o 15 m de altura, lo que sea mayor. "
            "(b) En toda el área de pisos para uso como estacionamiento ubicados bajo edificios clasificados en el "
            "subgrupo de ocupación Residencial Multifamiliar (R-2). "
            "(c) En edificios que tengan más de 15 m de altura debe disponerse de un sistema de estaciones de "
            "mangueras de 38 mm de diámetro en toda su altura."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_8_3", "seccion": "J.4.3.8.3",
        "titulo": "J.4.3.8.3 — Grupo R-2: Extintores de fuego portátiles",
        "texto": "J.4.3.8.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación Residencial Multifamiliar (R-2) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
    # ---- J.4.3.9 — GRUPO R-3 (RESIDENCIAL HOTELES) ----
    {
        "id": "NSR10-J-J_4_3_9_1", "seccion": "J.4.3.9.1",
        "titulo": "J.4.3.9 — Grupo R-3 (Residencial Hoteles). J.4.3.9.1 — Rociadores Automáticos, 2 condiciones (a-b)",
        "texto": (
            "J.4.3.9 — GRUPO DE OCUPACIÓN R-3 (RESIDENCIAL HOTELES). "
            "J.4.3.9.1 — Rociadores Automáticos — Toda edificación clasificada en el grupo de ocupación Residencial "
            "Hoteles (R-3) debe estar protegida por un sistema, aprobado y eléctricamente supervisado, de rociadores "
            "automáticos de acuerdo con la última versión del Código para suministro y distribución de agua para "
            "extinción de incendios en edificios, NTC2301 y con la Norma para Instalación de Sistemas de Rociadores, "
            "NFPA 13, así: "
            "(a) En la totalidad de edificaciones clasificadas en el subgrupo de ocupación Residencial Hoteles (R-3) "
            "que tengan más de cinco pisos o 15 m de altura, lo que sea mayor. "
            "(b) En toda el área de pisos para uso como estacionamiento ubicados bajo edificios clasificados en el "
            "subgrupo de ocupación Residencial Hoteles (R-3)."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_9_2", "seccion": "J.4.3.9.2",
        "titulo": "J.4.3.9.2 — Grupo R-3: Tomas fijas para bomberos y mangueras, 3 condiciones (a-c)",
        "texto": (
            "J.4.3.9.2 — Tomas fijas para bomberos y mangueras para extinción de incendios — Toda edificación "
            "clasificada en el grupo de ocupación Residencial Hoteles (R-3) debe estar protegida por un sistema de "
            "tomas fijas para bomberos y mangueras para extinción de incendios diseñados de acuerdo con la última "
            "versión del Código para suministro y distribución de agua para extinción de incendios en edificaciones, "
            "NTC 1669, y con el Código para Instalación de Sistemas de Tuberías Verticales y Mangueras, NFPA 14, así: "
            "(a) En la totalidad de edificaciones clasificadas en el subgrupo de ocupación Residencial Hoteles (R-3) "
            "que tengan más de cinco pisos o 15 m de altura, lo que sea mayor. "
            "(b) En toda el área de pisos para uso como estacionamiento ubicados bajo edificios clasificados en el "
            "subgrupo de ocupación Residencial Hoteles (R-3). "
            "(c) En edificios clasificados en el subgrupo de ocupación Residencial Hoteles (R-3) que tengan más de "
            "cinco pisos debe disponerse de un sistema de estaciones de mangueras de 38 mm de diámetro en toda su "
            "altura."
        ),
    },
    {
        "id": "NSR10-J-J_4_3_9_3", "seccion": "J.4.3.9.3",
        "titulo": "J.4.3.9.3 — Grupo R-3: Extintores de fuego portátiles",
        "texto": "J.4.3.9.3 — Extintores de fuego portátiles — Toda edificación clasificada en el grupo de ocupación Residencial Hoteles (R-3) debe estar protegida por un sistema de extintores portátiles de fuego, diseñados de acuerdo con la última versión de la norma Extintores de fuego portátiles, NTC 2885 y con la Norma de Extintores de fuego Portátiles, NFPA 10.",
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]

    if IDS_OBSOLETOS:
        sb.table("nsr10_chunks").delete().in_("id", IDS_OBSOLETOS).execute()
        print(f"Borrados {len(IDS_OBSOLETOS)} chunks obsoletos: {IDS_OBSOLETOS}")

    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")


if __name__ == "__main__":
    main()
