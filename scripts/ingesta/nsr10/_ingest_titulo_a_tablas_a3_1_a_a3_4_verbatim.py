"""
Re-ingesta verbatim de las Tablas A.3-1 a A.3-4 del Título A de NSR-10
(Capítulo A.3, coeficientes R0 y Ω0 por sistema estructural y límites de altura
por zona de amenaza sísmica). Fase 4 del plan de cierre del Título A
(2026-11-08).

Por qué se rehace: al comparar los chunks existentes (familias
NSR10-A3-A_3_{1..4}-* y NSR10-A-A_3_3_1_R0_acero_r*) contra el PDF
(NSR-10-95-105.pdf, páginas PDF 1-6 = A-52 a A-57, leídas visualmente) se
encontraron: un valor erróneo en la Tabla A.3-2 fila 2.a (zonas permitidas), un
«20 m» atribuido a las cerchas no dúctiles de la A.3-3 (el PDF dice 12 m), una
frase añadida («el valor más alto de esta tabla»), una nota con un 25 % que no
está en la nota 1 de la A.3-2, y filas completas ausentes (A.3-2: diagonales
excéntricas, placa de acero y 6 de concéntricas; A.3-3: mixtos, cerchas dúctiles,
lámina doblada, celosías; A.3-4: varios muros y pórticos de acero) y las notas
2-6.

Diseño: UNA FILA POR CHUNK (la fila nunca se separa de su valor al partir en
128 tokens; mismo defecto ya visto en la Tabla A-1.3-1) y encabezado corto (para
que las filas repetidas no desplacen otros chunks del top-k). Cada fila se
verifica ≤ 128 tokens reales antes de subir.

Uso: python _ingest_titulo_a_tablas_a3_1_a_a3_4_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"
LIMITE_TOKENS_REAL = 128

SL = "sin límite"

# --- Tabla A.3-1 ------------------------------------------------------------
G31 = {
    "1": "1. Paneles de cortante de madera",
    "2": "2. Muros estructurales",
    "3": "3. Pórticos con diagonales (las diagonales llevan fuerza vertical)",
}
T31 = [
    # grupo, letra, horizontales, verticales, R0, Ω0, alta, intermedia, baja
    ("1", "", "Paneles de cortante de madera", "muros ligeros de madera laminada", "3.0", "2.5", "6 m", "9 m", "12 m"),
    ("2", "a", "Muros de concreto con capacidad especial de disipación de energía (DES)", "el mismo", "5.0", "2.5", "50 m", SL, SL),
    ("2", "b", "Muros de concreto con capacidad moderada de disipación de energía (DMO)", "el mismo", "4.0", "2.5", "no", "50 m", SL),
    ("2", "c", "Muros de concreto con capacidad mínima de disipación de energía (DMI)", "el mismo", "2.5", "2.5", "no", "no", "50 m"),
    ("2", "d", "Muros de mampostería reforzada de bloque de perforación vertical (DES) con todas las celdas rellenas", "el mismo", "3.5", "2.5", "50 m", SL, SL),
    ("2", "e", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", "el mismo", "2.5", "2.5", "30 m", "50 m", SL),
    ("2", "f", "Muros de mampostería parcialmente reforzada de bloque de perforación vertical", "el mismo", "2.0", "2.5", "Grupo I, 2 pisos", "12 m", "18 m"),
    ("2", "g", "Muros de mampostería confinada", "el mismo", "2.0", "2.5", "Grupo I, 2 pisos", "Grupo I, 12 m", "Grupo I, 18 m"),
    ("2", "h", "Muros de mampostería de cavidad reforzada", "el mismo", "4.0", "2.5", "45 m", "60 m", SL),
    ("2", "i", "Muros de mampostería no reforzada (no tiene capacidad de disipación de energía)", "el mismo", "1.0", "2.5", "no", "no", "Grupo I, 2 pisos (Nota 3)"),
    ("3", "a", "Pórticos de acero estructural con diagonales concéntricas (DES)", "el mismo", "5.0", "2.5", "24 m", "30 m", SL),
    ("3", "b", "Pórticos con diagonales de concreto con capacidad moderada de disipación de energía (DMO)", "el mismo", "3.5", "2.5", "no", "30 m", "30 m"),
    ("3", "c", "Pórticos de madera con diagonales", "el mismo", "2.0", "2.5", "12 m", "15 m", "18 m"),
]
N31 = (
    "Notas de la Tabla A.3-1:\n"
    "1. El sistema de muros de carga es un sistema estructural que no dispone de un pórtico esencialmente completo, en el cual las cargas verticales son resistidas por los muros de carga y las fuerzas horizontales son resistidas por muros estructurales o pórticos con diagonales.\n"
    "2. Para edificaciones clasificadas como irregulares el valor de R0 debe multiplicarse por φa, φp y φr para obtener R = φa φp φr R0 (Véase A.3.3.3).\n"
    "3. La mampostería no reforzada sólo se permite en las regiones de las zonas de amenaza sísmica baja donde Aa sea menor o igual a 0.05 cuando se trate de edificaciones del grupo de uso I, de uno y dos pisos.\n"
    "4. El valor de Ω0 puede reducirse restándole 0.5 en estructuras con diafragma flexible, pero no debe ser menos de 2.0 para cualquier estructura."
)

# --- Tabla A.3-2 ------------------------------------------------------------
G32 = {
    "1": "1. Pórticos de acero con diagonales excéntricas",
    "2": "2. Muros estructurales",
    "3": "3. Pórticos con diagonales concéntricas",
}
PAC = "pórticos de acero resistentes a momentos con capacidad mínima de disipación de energía (DMI)"
T32 = [
    ("1", "a", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo son resistentes a momento", PAC, "7.0", "2.0", "45 m", "60 m", SL),
    ("1", "b", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo no son resistentes a momento", PAC, "6.0", "2.0", "45 m", "60 m", SL),
    ("1", "c", "Pórticos de acero con diagonales excéntricas si el vínculo no se conecta a la columna", "pórticos de acero no resistentes a momentos", "6.0", "2.0", "30 m", "45 m", SL),
    ("1", "d", "Pórticos de acero con diagonales excéntricas si el vínculo tiene conexión resistente a momento con la columna", PAC, "5.0", "2.0", "30 m", "45 m", SL),
    ("2", "a", "Muros de concreto con capacidad especial de disipación de energía (DES)", "pórticos de concreto con capacidad especial de disipación de energía (DES)", "7.0", "2.5", "72 m", SL, SL),
    ("2", "b", "Muros de concreto con capacidad moderada de disipación de energía (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "5.0", "2.5", "no", "72 m", SL),
    ("2", "c", "Muros de concreto con capacidad moderada de disipación de energía (DMO)", "pórticos losa-columna (Nota 3) con capacidad moderada de disipación de energía (DMO)", "3.5", "2.5", "no", "18 m", "27 m"),
    ("2", "d", "Muros de concreto con capacidad mínima de disipación de energía (DMI)", "pórticos de concreto con capacidad mínima de disipación de energía (DMI)", "2.5", "2.5", "no", "no", "72 m"),
    ("2", "e", "Muros de concreto con capacidad mínima de disipación de energía (DMI)", "pórticos losa-columna (Nota 3) con capacidad mínima de disipación de energía (DMI)", "2.0", "2.5", "no", "no", "18 m"),
    ("2", "f", "Muros de mampostería reforzada de bloque de perforación vertical (DES) con todas las celdas rellenas", "pórticos de concreto con capacidad especial de disipación de energía (DES)", "4.5", "2.5", "30 m", "45 m", "45 m"),
    ("2", "g", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", "pórticos de concreto con capacidad especial de disipación de energía (DES)", "3.5", "2.5", "30 m", "45 m", "45 m"),
    ("2", "h", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "2.5", "2.5", "no", "30 m", "45 m"),
    ("2", "i", "Muros de mampostería confinada (DMO — capacidad moderada de disipación de energía)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "2.0", "2.5", "no", "Grupo I, 18 m", "Grupo I, 21 m"),
    ("2", "j", "Muros de mampostería confinada (DMO — capacidad moderada de disipación de energía)", "pórticos de concreto con capacidad mínima de disipación de energía (DMI)", "2.0", "2.5", "no", "no", "Grupo I, 18 m"),
    ("2", "k", "Muros de mampostería de cavidad reforzada (DES — capacidad especial de disipación de energía)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "4.0", "2.5", "no", "30 m", "45 m"),
    ("2", "l", "Muros de mampostería de cavidad reforzada (DES — capacidad especial de disipación de energía)", "pórticos de concreto con capacidad mínima de disipación de energía (DMI)", "2.0", "2.5", "no", "no", "45 m"),
    ("2", "m", "Muros de cortante con placa de acero (DES)", "pórticos de acero resistente o no a momentos", "7.0", "2.0", "50 m", SL, SL),
    ("2", "n", "Muros de cortante compuestos con placa de acero y concreto", "pórticos de acero resistente o no a momentos", "6.5", "2.5", "50 m", SL, SL),
    ("2", "o", "Muros de concreto reforzado (DES) mixtos con elementos de acero", "pórticos de acero resistente o no a momentos", "6.0", "2.5", "50 m", SL, SL),
    ("2", "p", "Muros de concreto reforzado (DMO) mixtos con elementos de acero", "pórticos de acero resistente o no a momentos", "5.5", "2.5", "no", "no", SL),
    ("2", "q", "Muros de concreto reforzado (DMI) mixtos con elementos de acero", "pórticos de acero resistentes o no a momentos", "5.0", "2.5", "no", "no", "45 m"),
    ("3", "a", "Pórticos de acero con diagonales concéntricas (DES)", "pórticos de acero no resistentes a momentos", "5.0", "2.5", "30 m", "45 m", "60 m"),
    ("3", "b", "Pórticos de acero con diagonales concéntricas (DMI)", "pórticos de acero no resistentes a momentos", "4.0", "2.5", "no", "10 m", "60 m"),
    ("3", "c", "Pórticos mixtos con diagonales concéntricas (DES)", "pórticos de acero resistentes o no a momentos", "5.0", "2.0", "50 m", SL, SL),
    ("3", "d", "Pórticos mixtos con diagonales concéntricas (DMI)", "pórticos de acero resistentes o no a momentos", "3.0", "2.0", "no (nota 5)", "no (nota 5)", SL),
    ("3", "e", "Pórticos de acero con diagonales concéntricas restringidas a pandeo, con conexiones viga-columna resistentes a momento", "pórticos de acero no resistentes a momentos", "7.0", "2.5", "30 m", "45 m", SL),
    ("3", "f", "Pórticos de acero con diagonales concéntricas restringidas a pandeo, con conexiones viga-columna no resistentes a momento", "pórticos de acero no resistentes a momentos", "6.0", "2.5", "30 m", "45 m", SL),
    ("3", "g", "Pórticos de concreto con diagonales concéntricas con capacidad moderada de disipación de energía (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "3.5", "2.5", "no", "24 m", "30 m"),
]
N32 = (
    "Notas de la Tabla A.3-2:\n"
    "1. El sistema combinado es un sistema estructural en el cual: (a) las cargas verticales son resistidas por un pórtico no resistente a momentos, esencialmente completo, y las fuerzas horizontales son resistidas por muros estructurales o pórticos con diagonales, o (b) las cargas verticales y horizontales son resistidas por un pórtico resistente a momentos, esencialmente completo, combinado con muros estructurales o pórticos con diagonales, que no cumple los requisitos de un sistema dual.\n"
    "2. Para edificaciones clasificadas como irregulares el valor de R0 debe multiplicarse por φa, φp y φr, para obtener R = φa φp φr R0 (Véase A.3.3.3).\n"
    "3. Los pórticos losa-columna incluyen el reticular celulado.\n"
    "4. El valor de Ω0 puede reducirse restándole 0.5 en estructuras con diafragma flexible, pero no debe ser menos de 2.0 para cualquier estructura.\n"
    "5. Se permite una altura de 20m en edificios de un piso (naves industriales o similares) que no sean del grupo de uso IV."
)

# --- Tabla A.3-3 ------------------------------------------------------------
G33 = {
    "1": "1. Pórticos resistentes a momentos con capacidad especial de disipación de energía (DES)",
    "2": "2. Pórticos resistentes a momentos con capacidad moderada de disipación de energía (DMO)",
    "3": "3. Pórticos resistentes a momentos con capacidad mínima de disipación de energía (DMI)",
    "4": "4. Pórticos losa-columna (incluye reticular celulado)",
    "5": "5. Estructuras de péndulo invertido",
}
PAM = "Pórticos de acero o mixtos resistentes o no a momentos"
T33 = [
    ("1", "a", "Pórticos de concreto (DES)", "el mismo", "7.0", "3.0", SL, SL, SL),
    ("1", "b", "Pórticos de acero (DES)", "el mismo", "7.0 (Nota 3)", "3.0", SL, SL, SL),
    ("1", "c", "Pórticos mixtos", PAM, "7.0", "3.0", SL, SL, SL),
    ("1", "d", "Pórticos de acero con cerchas dúctiles (DES)", PAM, "6.0", "3.0", "30 m", "45 m", SL),
    ("2", "a", "Pórticos de concreto (DMO)", "el mismo", "5.0", "3.0", "no", SL, SL),
    ("2", "b", "Pórticos de acero (DMO)", "el mismo", "5.0 (Nota 3)", "3.0", "no", SL, SL),
    ("2", "c", "Pórticos mixtos con conexiones rígidas (DMO)", PAM, "5.0", "3.0", "no", SL, SL),
    ("3", "a", "Pórticos de concreto (DMI)", "el mismo", "2.5", "3.0", "no", "no", SL),
    ("3", "b", "Pórticos de acero (DMI)", "el mismo", "3.0", "2.5", "no", "no", SL),
    ("3", "c", "Pórticos mixtos con conexiones totalmente restringidas a momento (DMI)", PAM, "3.0", "3.0", "no", "no", SL),
    ("3", "d", "Pórticos mixtos con conexiones parcialmente restringidas a momento", PAM, "6.0", "3.0", "no", "30 m", "50 m"),
    ("3", "e", "Pórticos de acero con cerchas no dúctiles", "el mismo", "1.5", "1.5", "no (nota 5)", "no (nota 5)", "12 m"),
    ("3", "f", "Pórticos de acero con perfiles de lámina doblada en frío y perfiles tubulares estructurales PTE que no cumplen los requisitos de F.2.2.4 para perfiles no esbeltos (nota 6)", "el mismo", "1.5", "1.5", "no (nota 5)", "no (nota 5)", SL),
    ("4", "a", "Pórticos losa-columna de concreto con capacidad moderada de disipación de energía (DMO)", "el mismo", "2.5", "3.0", "no", "15 m", "21 m"),
    ("4", "b", "Pórticos losa-columna de concreto con capacidad mínima de disipación de energía (DMI)", "el mismo", "1.5", "3.0", "no", "no", "15 m"),
    ("5", "a", "Pórticos de acero resistentes a momento con capacidad especial de disipación de energía (DES)", "el mismo", "2.5 (Nota 3)", "2.0", SL, SL, SL),
    ("5", "b", "Pórticos de concreto con capacidad especial de disipación de energía (DES)", "el mismo", "2.5", "2.0", SL, SL, SL),
    ("5", "c", "Pórticos de acero resistentes a momento con capacidad moderada de disipación de energía (DMO)", "el mismo", "1.5 (Nota 3)", "2.0", "no", SL, SL),
]
# Fila especial sin R0/Ω0 (texto verbatim del PDF)
FILA_33_3G = (
    "3", "g", "Otras estructuras de celosía tales como vigas y cerchas",
    "No se pueden usar como parte del sistema de resistencia sísmica, a no ser que tengan conexiones rígidas a columnas, en cuyo caso serán tratadas como pórticos de celosía.",
)
N33 = (
    "Notas de la Tabla A.3-3:\n"
    "1. El sistema de pórtico es un sistema estructural compuesto por un pórtico espacial, resistente a momentos, esencialmente completo, sin diagonales, que resiste todas las cargas verticales y las fuerzas horizontales.\n"
    "2. Para edificaciones clasificadas como irregulares el valor de R0 debe multiplicarse por φa, φp y φr, para obtener R = φa φp φr R0 (Véase A.3.3.3).\n"
    "3. Cuando se trate de estructuras de acero donde las uniones del sistema de resistencia sísmica son soldadas en obra, el valor de R0 debe multiplicarse por 0.90.\n"
    "4. El valor de Ω0 puede reducirse restándole 0.5 en estructuras con diafragma flexible, pero no debe ser menos de 2.0 para cualquier estructura.\n"
    "5. Se permite hasta una altura de 12m en edificios de un piso (naves industriales o similares) que no sean del grupo de Uso IV.\n"
    "6. Los perfiles de lámina doblada y los perfiles tubulares estructurales que cumplen con los requisitos de F.2.2.4 para miembros no esbeltos que se diseñen con conexiones dúctiles calificadas de acuerdo a F.3.1.8 se podrán diseñar como pórticos resistentes a momentos convencionales."
)

# --- Tabla A.3-4 ------------------------------------------------------------
G34 = {
    "1": "1. Muros estructurales",
    "2": "2. Pórticos de acero con diagonales excéntricas",
    "3": "3. Pórticos con diagonales concéntricas",
}
PCD = "pórticos de concreto con capacidad especial de disipación de energía (DES)"
PAD = "pórticos de acero resistentes a momentos con capacidad especial de disipación de energía (DES)"
PAM_ = "pórticos de acero resistentes a momentos con capacidad moderada de disipación de energía (DMO)"
PAL = "pórticos de acero con alma llena, con conexiones rígidas"
T34 = [
    ("1", "a", "Muros de concreto con capacidad especial de disipación de energía (DES)", PCD, "8.0", "2.5", SL, SL, SL),
    ("1", "b", "Muros de concreto con capacidad especial de disipación de energía (DES)", PAD, "8.0", "2.5", SL, SL, SL),
    ("1", "c", "Muros de concreto con capacidad moderada de disipación de energía (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "6.0", "2.5", "no", SL, SL),
    ("1", "d", "Muros de concreto con capacidad moderada de disipación de energía (DMO)", PAM_, "6.0", "2.5", "no", SL, SL),
    ("1", "e", "Muros de mampostería reforzada de bloque de perforación vertical (DES) con todas las celdas rellenas", PCD, "5.5", "3.0", "45 m", "45 m", "45 m"),
    ("1", "f", "Muros de mampostería reforzada de bloque de perforación vertical (DES) con todas las celdas rellenas", PAD, "5.5", "3.0", "45 m", "45 m", "45 m"),
    ("1", "g", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", PCD, "4.5", "2.5", "35 m", "35 m", "35 m"),
    ("1", "h", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", PAD, "4.5", "2.5", "35 m", "35 m", "35 m"),
    ("1", "i", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", PAM_, "3.5", "2.5", "no", "30 m", "30 m"),
    ("1", "j", "Muros de mampostería reforzada de bloque de perforación vertical (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "3.5", "2.5", "no", "30 m", "30 m"),
    ("1", "k", "Muros de cortante con placa de acero (DES)", PAL + " (DES)", "7.0", "2.5", SL, SL, SL),
    ("1", "m", "Muros de cortante mixtos con placa de acero", PAL + " (DES)", "6.5", "2.5", SL, SL, SL),
    ("1", "n", "Muros de concreto reforzado (DES) mixtos con elementos de acero", PAL + " (DES)", "6.0", "2.5", SL, SL, SL),
    ("1", "o", "Muros de concreto reforzado (DMI) mixtos con elementos de acero", PAL + " (DES)", "5.0", "2.5", "no", "no", SL),
    ("1", "p", "Muros de concreto reforzado (DMI) mixtos con elementos de acero", PAL + " (DMO)", "4.0", "3.0", "no", "no", SL),
    ("2", "a", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo son resistentes a momento", PAD, "8.0", "2.5", SL, SL, SL),
    ("2", "b", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo no son resistentes a momento", PAD, "7.0", "2.5", SL, SL, SL),
    ("2", "c", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo son resistentes a momento", PAM_, "6.0", "2.5", SL, SL, SL),
    ("2", "d", "Pórticos de acero con diagonales excéntricas si las conexiones con las columnas por fuera del vínculo no son resistentes a momento", PAM_, "5.0", "2.5", SL, SL, SL),
    ("3", "a", "Pórticos de acero con diagonales concéntricas con capacidad especial de disipación de energía (DES)", PAD, "6.0", "2.5", SL, SL, SL),
    ("3", "b", "Pórticos de acero con diagonales concéntricas con capacidad mínima de disipación de energía (DMI)", PAM_, "3.0", "2.5", "no", "60 m", SL),
    ("3", "c", "Pórticos de concreto con diagonales concéntricas con capacidad moderada de disipación de energía (DMO)", "pórticos de concreto con capacidad moderada de disipación de energía (DMO)", "4.0", "2.5", "no", "24 m", "30 m"),
    ("3", "d", "Pórticos mixtos con diagonales concéntricas (DES)", PAL + " (DES)", "6.0", "2.5", SL, SL, SL),
    ("3", "e", "Pórticos de acero con diagonales concéntricas restringidas al pandeo", PAL + " (DES)", "7.0", "2.5", SL, SL, SL),
    ("3", "f", "Pórticos de acero con diagonales concéntricas (DES)", PAL + " (DMO)", "6.0", "2.5", "no", "10 m", SL),
    ("3", "g", "Pórticos mixtos con diagonales concéntricas (DES)", PAL + " (DMO)", "5.5", "2.5", "50 m", "30 m", SL),
    ("3", "h", "Pórticos con diagonales concéntricas que resistan solo a tensión", "el mismo", "3.0", "2.5", "no (nota 4)", "no (nota 4)", "no (nota 4)"),
]
N34 = (
    "Notas de la Tabla A.3-4:\n"
    "1. El sistema dual es un sistema estructural que tiene un pórtico espacial resistente a momentos y sin diagonales, combinado con muros estructurales o pórticos con diagonales. Para que el sistema estructural se pueda clasificar como sistema dual se deben cumplir los siguientes requisitos: (a) El pórtico espacial resistente a momentos, sin diagonales, esencialmente completo, debe ser capaz de soportar las cargas verticales. (b) Las fuerzas horizontales son resistidas por la combinación de muros estructurales o pórticos con diagonales, con el pórtico resistente a momentos, el cual puede ser un pórtico de capacidad especial de disipación de energía (DES), cuando se trata de concreto reforzado o acero estructural, un pórtico con capacidad moderada de disipación de energía de concreto reforzado, y un pórtico con capacidad mínima de disipación de energía de acero estructural. El pórtico resistente a momentos, actuando independientemente, debe diseñarse para que sea capaz de resistir como mínimo el 25 por ciento del cortante sísmico en la base. (c) Los dos sistemas deben diseñarse de tal manera que en conjunto sean capaces de resistir la totalidad del cortante sísmico en la base, en proporción a sus rigideces relativas, considerando la interacción del sistema dual en todos los niveles de la edificación, pero en ningún caso la responsabilidad de los muros estructurales o los pórticos con diagonales puede ser menor del 75 por ciento del cortante sísmico en la base.\n"
    "2. Para edificaciones clasificadas como irregulares el valor de R0 debe multiplicarse por φa, φp y φr, para obtener R = φa φp φr R0 (Véase A.3.3.3).\n"
    "3. El valor de Ω0 puede reducirse restándole 0.5 en estructuras con diafragma flexible, pero no debe ser menos de 2.0 para cualquier estructura.\n"
    "4. Se permite hasta una altura de 12m en edificios de un piso (naves industriales o similares) que no sean del grupo de uso IV."
)

TABLAS = [
    ("1", "Sistema estructural de muros de carga", G31, T31, N31),
    ("2", "Sistema estructural combinado", G32, T32, N32),
    ("3", "Sistema estructural de pórtico resistente a momentos", G33, T33, N33),
    ("4", "Sistema estructural dual", G34, T34, N34),
]


def _zona(valor: str) -> str:
    if valor == "no":
        return "no se permite"
    if valor.startswith("no ("):
        return "no se permite " + valor[3:]
    if valor == SL:
        return "sin límite de altura"
    if valor.startswith("Grupo I"):
        return "solo Grupo de uso I, " + valor.split(", ", 1)[1]
    return f"hasta {valor}"


_TAG_SISTEMA = {"1": "muros de carga", "2": "sistema combinado", "3": "pórtico resistente a momentos", "4": "sistema dual"}


def _fila(n: str, titulo_tabla: str, grupos: dict, f: tuple) -> dict:
    g, letra, hor, ver, r0, om, alta, inter, baja = f
    etiqueta = f"{g}.{letra}" if letra else g
    cuerpo = (
        f"Horizontales: {hor}\n"
        f"Verticales: {ver}\n"
        f"R0 = {r0}; Ω0 = {om}\n"
        f"Alta: {_zona(alta)}; intermedia: {_zona(inter)}; baja: {_zona(baja)}."
    )
    texto = f"NSR-10 Tabla A.3-{n}, fila {etiqueta} — {grupos[g]}\n" + cuerpo
    texto_corto = f"NSR-10 Tabla A.3-{n}, fila {etiqueta}\n" + cuerpo
    return {
        "id": f"NSR10-A-A3T{n}-{g}{letra or '0'}",
        "seccion": f"A.3.3.1 (Tabla A.3-{n}) — {titulo_tabla}",
        "titulo": f"Tabla A.3-{n} fila {etiqueta}: {hor[:120]} — R0 = {r0}",
        "texto": texto,
        "texto_corto": texto_corto,
        "es_fila": True,
    }


def construir() -> list[dict]:
    chunks: list[dict] = []
    for n, titulo_tabla, grupos, filas, notas in TABLAS:
        for f in filas:
            chunks.append(_fila(n, titulo_tabla, grupos, f))
        if n == "3":
            g, letra, hor, txt = FILA_33_3G
            chunks.append({
                "id": "NSR10-A-A3T3-3g",
                "seccion": f"A.3.3.1 (Tabla A.3-3) — {titulo_tabla}",
                "titulo": "Tabla A.3-3 fila 3.g: otras estructuras de celosía (vigas y cerchas)",
                "texto": (
                    f"NSR-10 Tabla A.3-3 ({titulo_tabla}), fila 3.g — {grupos[g]}\n"
                    f"{hor}: {txt}"
                ),
                "es_fila": True,
            })
        chunks.append({
            "id": f"NSR10-A-A3T{n}-notas",
            "seccion": f"A.3.3.1 (Tabla A.3-{n}) — notas",
            "titulo": f"Tabla A.3-{n}: notas ({titulo_tabla})",
            "texto": f"NSR-10 Tabla A.3-{n} ({titulo_tabla})\n\n" + notas,
            "es_fila": False,
        })
    return chunks


PATRONES_ANTIGUOS = [
    "NSR10-A3-A_3_1-%", "NSR10-A3-A_3_2-%", "NSR10-A3-A_3_3-%", "NSR10-A3-A_3_4-%",
    "NSR10-A-A_3_3_1_R0_acero_r%",
]


def main() -> None:
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _resplit_titulo_f_f42_por_limite_tokens import split_texto
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tok = model.tokenizer

    finales: list[dict] = []
    excedidas: list[tuple[str, int]] = []
    for c in construir():
        if c["es_fila"]:
            n = len(tok.encode(c["texto"], add_special_tokens=True))
            if n > LIMITE_TOKENS_REAL and c.get("texto_corto"):
                c = {**c, "texto": c["texto_corto"]}
                n = len(tok.encode(c["texto"], add_special_tokens=True))
            if n > LIMITE_TOKENS_REAL:
                excedidas.append((c["id"], n))
            finales.append(c)
        else:
            piezas = []
            for p in split_texto(c["texto"]):
                piezas.extend(_sub_particionar_por_tokens_reales(p, tok))
            for i, p in enumerate(piezas, 1):
                finales.append({**c, "id": f"{c['id']}_p{i}", "texto": p})
    if excedidas:
        for cid, n in excedidas:
            print(f"  ! fila sobre {LIMITE_TOKENS_REAL} tokens: {cid} = {n}")
        raise SystemExit("Filas sobre el limite real: acortar antes de subir.")

    ids = [c["id"] for c in finales]
    assert len(ids) == len(set(ids)), "ids duplicados"
    print(f"{len(finales)} chunks nuevos ({sum(1 for c in finales if c['es_fila'])} filas)")

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    vec = model.encode([c["texto"] for c in finales], normalize_embeddings=True, show_progress_bar=False)
    rows = [{
        "id": c["id"], "capitulo": CAPITULO, "seccion": c["seccion"],
        "titulo": c["titulo"][:500], "texto": c["texto"], "embedding": v.tolist(),
    } for c, v in zip(finales, vec)]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("Subidos. Borrando familias antiguas...")

    borrados = 0
    for pat in PATRONES_ANTIGUOS:
        viejos = sb.table("nsr10_chunks").select("id").like("id", pat).execute().data
        if viejos:
            sb.table("nsr10_chunks").delete().in_("id", [v["id"] for v in viejos]).execute()
            borrados += len(viejos)
    print(f"OK: {len(rows)} chunks cargados, {borrados} chunks antiguos borrados.")


if __name__ == "__main__":
    main()
